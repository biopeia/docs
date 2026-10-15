# The executive outcome ledger

Reviewed against `organism` at commit `ba0011797a6a3b4d48c7731651e50560c4043f18`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run, or neither.

## What it is

When the Organism package admits an affordance (see
[from an affordance to a motor command](action-path.md)), one of the inputs
is optional: a history of how earlier attempts at the same thing ended. The
executive outcome ledger is the structure meant to hold that history and to
turn it into a number.

It is a bounded table. Each row is keyed by a pair, a competence and the
effect expected from it, and holds the last sixteen recorded outcomes for
that pair. Asked about a pair, the ledger returns a factor between 0.5 and
1.5 that admission multiplies into relevance, or a flag that the pair is
suppressed and should not be admitted at all.

The module is called "Executive Outcome Learning" in its own header. What it
does is count: it stores classified outcomes and computes a ratio from the
counts. The module is explicit about what it leaves alone: "nothing here
writes causal evidence, controllability, agency or competence evidence, and
nothing here is a reward".

`ActionDomain` accepts an optional `ExecutiveOutcomeLedger`. On an explicit
terminal `close()`, it validates a supplied non-neutral outcome against the
intent, records it under the intent's competence and anticipated effect, then
closes the commitment and intent. Unit tests exercise successful recording
and rejection cases (`organism:tests/source_unit/actuation/test_domain.py`).
This is a source-level composition contract, not evidence that a production
runtime supplies the ledger or calls `close()` from an observed world cycle.

## What an outcome is

The ledger does not observe anything. It is told. A caller hands it a sample:
a tick, a class, a reason string and three optional numbers (effect
similarity, prediction mismatch, progress before failure). The three numbers
are stored and, except for an average of the mismatch that nothing consumes,
not used.

The class is one of four that count, and a fifth that is refused:

| Class | Meaning given by the classifier |
|---|---|
| positive | status `satisfied` with reason `anticipated_effect_observed` |
| contradicting | status `failed` with one of three reasons, among them `stagnation` |
| terminal | status `failed` with a controller or commitment failure, when the binding was valid at the start |
| suppress | status `invalidated` with one of four reasons, among them `embodiment_changed` |
| neutral | everything else; never stored |

A function in the module maps a status and a reason to a class
(`organism:src/organism/agency/executive_outcome.py::classify_outcome`,
covered by `test_outcome_classes_follow_the_failure_reason`). The statuses are
those of an intent. The reasons are literal strings, and the code notes of
them: "Reason strings mirror core.domains.intention (agency never imports
core)." No such module exists in the Organism repository, so at this revision
nothing produces those strings. A reason the classifier does not list is
neutral.

Neutral outcomes are refused on the way in
(`test_neutral_outcomes_are_never_evidence`). An interruption, a rejection,
or a completion that was not verified leaves no trace.

## From counts to a factor

For one pair, let *s*, *c* and *t* be the numbers of positive, contradicting
and terminal samples among the last sixteen. The module computes

```text
confidence = (1 + s) / (2 + s + c + 2t)
factor     = confidence / 0.5, limited to the range 0.5 to 1.5
```

A pair never seen gets a factor of exactly 1, and so does a pair with equal
positives and contradictions. A terminal failure weighs twice a contradicting
one. The weights and limits are attributes of a small policy object and the
computation happens at each lookup, not when a sample is stored; the code
gives the reason: "Evidence stores facts (samples); the modulation policy is
computed at lookup so it can change without reinterpreting checkpoints."
Covered by `test_confidence_formula_and_bounded_factor`,
`test_window_keeps_the_last_sixteen_real_outcomes` and
`test_modulation_is_per_key`.

Values obtained by running the module, to make the scale concrete:

| History of one pair | Factor |
|---|---|
| none | 1.0 |
| one positive | 1.33 |
| sixteen positives | 1.5 |
| one contradicting | 0.67 |
| one terminal | 0.5 |
| sixteen terminal | 0.5 |

The factor reaches its floor after a single terminal failure and its ceiling
only after several successes. In admission the factor multiplies a relevance
that must reach 0.2 by default, so the floor halves relevance and does not by
itself exclude anything.

## Suppression

A sample of the suppress class does something different. It must arrive with
a description of the state it was judged against: a binding fingerprint,
whether the competence was executable, and two revision numbers
(`test_suppression_requires_the_state_it_is_judged_against`). The ledger
stores that description, and from then on reports the pair as suppressed.

Suppression is lifted when a lookup supplies a description that differs from
the stored one in any of the four fields. A lookup that supplies none, or the
same one, leaves the pair suppressed
(`test_suppression_lifts_only_on_relevant_revision`).

Three properties of this, read from the code and confirmed by running it:

- **Lifting is permanent and happens during a lookup.** Once a differing
  description has been presented, the stored one is deleted. A later lookup
  with the original description found the pair no longer suppressed. The
  ledger does not remember that the pair was ever suppressed, apart from the
  sample in its window.
- **A suppress sample occupies one of the sixteen places** and counts toward
  none of *s*, *c* and *t*. After lifting, a pair with that single sample has
  a factor of 1.
- **Asking is not free of effect.** Besides lifting, every lookup increments
  counters that are part of the ledger's exported state.

## Bounds

The table holds at most 256 pairs by default. Recording an outcome for a pair
moves it to the most recent end; when the table is over capacity the pair
least recently *recorded* is dropped, together with its suppression if it had
one (`test_ledger_is_bounded_and_reports_saturation`). Looking a pair up does
not refresh it: in a run with a capacity of two, a pair that had just been
looked up was the next one dropped.

Ticks are stored as given. A sample with an earlier tick than its predecessor
was accepted, and the tick reported for the last outcome was then the earlier one.

## Across a restart

The ledger exports its whole content to plain data, with a schema version,
and can be rebuilt from it. The round trip was exact for content and counters
(`test_ledger_checkpoint_round_trip_is_exact`), and a payload of the earlier
schema is refused (`test_v1_context_keys_are_rejected`).

Two things do not survive, confirmed by running the module: the capacity,
which is not exported, so a ledger built with a capacity of two was restored
with 256; and a non-default policy object, for the same reason.

More important is what the export is not part of. No checkpoint in the
repository includes it. The composed cognitive payload described under
[identity and the checkpoint envelope](identity-and-checkpoint.md) does not,
and nothing else assembles Organism state. Whether this history would survive
a restart of an Organism is therefore not something the code decides yet.

## At each lifecycle boundary

| Boundary | What happens | Support |
|---|---|---|
| Birth | A new ledger is empty | Code |
| Checkpoint | Content and counters can be exported; capacity and policy are not | Code, test and ad hoc run |
| Restart | An exported ledger can be rebuilt; no checkpoint carries it | Code and test; search of the repository |
| Re-embodiment | Nothing in the ledger reacts. Rows are keyed by competence and effect, not by body. A caller could record a suppress sample with reason `embodiment_changed` | Code; no operation performs a re-embodiment |
| Reproduction | No operation exists and nothing refers to the ledger from the genetics code | Search of the repository |

## Whose state this is

[ADR-0092](../../technical/adr/ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md)
and
[ADR-0095](../../technical/adr/ADR-0095-surviving-semantic-authorities.md)
place agency and competence state under the Organism's authority and call it
longitudinal. The ledger lives in the Organism package and imports nothing
from another domain, which is consistent with that. Whether it is in fact
kept across the life of an Organism depends on a composition that does not
exist at this revision; the decisions state an intent and the code does not
yet contradict or fulfil it.

## What supports this description

| Claim | Support |
|---|---|
| Classification of outcomes, the confidence formula and its limits, the window of sixteen, refusal of neutral outcomes, per-pair modulation, suppression and its lifting, the bound and eviction, exact round trip, refusal of the earlier schema | Code and tests in `organism:tests/source_unit/agency/test_executive_outcome.py` |
| The table of factors; lifting is permanent; a suppress sample fills a place; lookups change counters; lookups do not refresh a pair; ticks are not ordered; capacity is not restored | Code, and one ad hoc run of the module at that revision; no test is kept for these |
| How the factor is used by admission | Code of `organism:src/organism/agency/prospective.py` and the same ad hoc run, with a hand-written callback |
| `ActionDomain.close()` records an explicitly supplied non-neutral outcome; no reviewed organism checkpoint includes the ledger | Code and `test_domain.py`; source search |
| That this state is the Organism's and longitudinal | Accepted decisions ADR-0092 and ADR-0095; statements of intent |

No recorded outcome from a run of an Organism was examined, because none can
exist at this revision. That the ledger changes behaviour for the better, or
at all, is not supported by anything reviewed here.

## Open questions

- Which runtime component supplies factual outcomes and invokes the explicit
  close operation; the domain validates but does not infer those facts.
- Whether a lookup is meant to change the ledger, given that admission may
  look up candidates it then does not admit.
- Whether the ledger belongs in the Organism's portable checkpoint.
