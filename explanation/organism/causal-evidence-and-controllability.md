# Effects, causal evidence and controllability

Reviewed against `organism` at commit `ba0011797a6a3b4d48c7731651e50560c4043f18`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run, or an accepted decision.

## What it is

After a command has been issued, something in the body's signals may change.
The Organism package contains a set of structures for keeping a record of
that: what changed, after which command, and how often the same change
followed the same kind of command compared with how often it happened
otherwise. From those counts it computes numbers it calls controllability and
agency.

The words are the code's. Causal evidence is a row in a bounded list.
Controllability is a difference between two observed rates, scaled by how
many rows there are. Agency is a weighted sum of three such numbers. Nothing
here intervenes, randomises or tests a hypothesis; the structures count what a
caller reports to them.

The evidence ledger and inference models are implemented as composable
Organism mechanisms and have source-unit coverage. The reviewed source does
not itself assemble them into a live runtime: they are instantiated in tests,
not by a production Organism/world orchestrator, and no complete observed
causal cycle was examined. The findings below describe those mechanisms and
their tested contracts, not demonstrated causal learning.

## The parts

```text
change in signals ──▶ effect space ──▶ effect identifier
                                            │
issued command ─▶ intervention signature    │
                         │                  ▼
                         └──────────▶ evidence ledger ◀── passive windows
                                            │ counts
              ┌─────────────────────────────┼──────────────────────┐
              ▼                             ▼                      ▼
     forward model               controllability model        agency model
  (most frequent effect)        (rate above alternatives)   (weighted sum)
```

A caller is expected to do the wiring: nothing in the package passes the
output of one part to the next.

## What an effect is

An effect (`organism:src/organism/actuation/effects.py::EffectSpace`) is an
identifier for a pattern of change. The registry receives a mapping from
feature name to a signed change and does three things.

1. It drops every feature whose name does not begin with one of six prefixes
   (`signal.`, `latent.`, `part.`, `channel.`, `internal.`, `effect.`). The
   module's stated reason: "No body, world, lab or evaluator semantic label is
   accepted here." The check is on the prefix only.
2. It multiplies each change by seven, rounds, and limits the result to the
   range from minus seven to seven. Changes that round to zero are dropped.
3. It hashes what remains. That hash is the effect identifier.

So two changes are the same effect when they round to the same integers on
the same features. In an ad hoc run, changes of 0.50 and 0.55 on one feature
gave one identifier, a change of 0.07 gave nothing, and a mapping with only
foreign prefixes gave nothing. Each identifier keeps a count of how often it
was seen and a confidence equal to that count over eight, at most one. The
registry holds 512 identifiers and drops the least seen.

A second, finer unit exists beside it. An atom is one feature, one direction
and one of three coarse magnitudes
(`test_magnitude_class_is_a_fixed_function_of_the_bucket`,
`test_v4_signature_decomposes_exactly_one_atom_per_entry`,
`test_atom_identity_is_pure_and_distinguishes_direction_and_magnitude`). A
change is cut into at most sixteen atoms, largest first
(`test_transition_atoms_are_bounded_keeping_the_largest_changes`,
`test_non_organism_features_and_negligible_changes_make_no_atom`).

Comparing two effects goes through one class, which at this revision returns
one for the same identifier and zero otherwise.

## What a row of evidence is

The ledger (`organism:src/organism/actuation/evidence.py::CausalEvidenceLedger`,
which describes itself as the "Single bounded factual source for all
sensorimotor inference views.") holds two lists.

- **Intervention rows.** One per reported transition: a command reference, the
  commitment it was issued under, an attempt identifier, an intervention
  signature, optionally a competence, a context reference, two ticks, and the
  effect identifier and atoms observed afterwards, if any. A transition
  without an attempt and a signature is refused, and so is an effect whose
  identifier does not begin with `effect.`.
- **Passive rows.** One per reported window in which no command was issued,
  with the effect observed in it, if any.

The two lists are bounded separately, 4096 and 1024 rows by default, oldest
dropped first, so that idle time cannot push out interventions. Counts are
kept incrementally per competence, signature, commitment and attempt, with and
without context. Confirmed by running the ledger: with a capacity of four, six
interventions left the last four and the counts followed; a round trip through
its export gave equal rows and equal counts.

The ledger takes what it is given. Rows with ticks out of order were accepted.
Two passive windows with the same ticks, context and prior state reference but
different outcomes received the same identifier.

## The question the counts answer

Every model asks the ledger one question about a source and an effect, and
gets four integers back:

```text
action_n     rows of this source
action_hits  of those, rows with this effect
other_n      all other rows, in the same context
other_hits   of those, rows with this effect
```

A source is a competence, an intervention signature, or a group of signatures.
What matters is the third number. **Other means every other retained row:
passive windows and also the rows of every other source.** The comparison is
therefore not between acting and not acting, but between this source and
everything else on record.

## Controllability as computed here

The function
(`organism:src/organism/actuation/model.py::controllability_confidence`,
"Intervention reliability beyond the alternative rate, times support.") is:

```text
if action_n == 0 or action_hits == 0:  0
if other_n  == 0:  min(0.25, action_n / 32)
otherwise:         (action_hits / action_n  -  other_hits / other_n)  *  min(1, min(action_n, other_n) / 8)
                   limited to the range 0 to 1
```

The model class that stores the results says of itself: "Infer control only
when intervention evidence beats alternatives." Values obtained by running the
function and the ledger:

| Rows on record | Result for source A |
|---|---|
| A eight times, effect each time; nothing else | 0.25 |
| A eight times, effect never; nothing else | 0.0 |
| A eight of eight; eight passive windows without the effect | 1.0 |
| A eight of eight; eight passive windows without; B eight of eight with the same effect | 0.5 |
| A eight of eight; B eight of eight with the same effect; no passive windows | 0.0 |

The zero-hit guard prevents a positive controllability estimate when no
action-linked observation of the effect exists. With observed hits but no
comparison rows, the estimate remains capped at 0.25; it is a bounded score,
not a demonstrated causal result. The last row shows that two sources that
each produce an effect every time cancel one another when no passive windows
exist. These edge cases are recorded in finding F-0103.

The model stores one estimate per source, effect and context, at most 8192,
most recently updated kept. It can be rebuilt from the ledger and exports its
estimates as a list, which restored to equal estimates in the ad hoc run.

The package uses the word controllability for two other numbers: the effect
size times consistency kept for a motor primitive (see
[competence development](competence-development.md)), and a field of an
execution binding that stores whatever the caller supplied, limited to the
unit interval (see
[execution bindings](execution-binding-and-affordances.md)). The three are
not converted into one another by any code.

## Agency as computed here

```text
temporal    = action_hits / action_n
specificity = temporal - other_hits / other_n, limited to 0..1
predictive  = prediction match supplied by the caller, or 0.5 if none
result      = min(action_n, other_n) / 8, at most 1,
              times (0.45 * temporal + 0.35 * specificity + 0.20 * predictive);
              zero if temporal or specificity is zero
```

With eight rows that always showed the effect and eight passive windows that
never did, the result was 0.9 without a prediction match and 1.0 with a match
of one. With no other rows at all it was zero. A rebuild from the ledger
always uses the default of 0.5, because the ledger holds no prediction match.
The number is a contingency score. That it measures ownership of a
consequence, as the class's description puts it, is an interpretation the code
does not test.

## The forward model

The third view
(`organism:src/organism/actuation/model.py::CompetenceEffectModel`) counts,
per competence and context, which effect followed. Asked for a prediction it
returns the most frequent effect with a confidence equal to its share; for an
unseen context it pools all contexts of that competence. It can be rebuilt
from the ledger and has no export of its own.

## Naming what was done: signatures and dimensions

A row of evidence names an intervention signature. The module that produces
one (`organism:src/organism/actuation/intervention.py::InterventionSignatureRegistry`)
derives it from a command alone: the set of channels driven and, for each,
whether it was driven at more or less than half the strongest. Absolute
intensity is left out of the identity and kept as a four-bin histogram.
Confirmed by running it: one channel at 0.2 and at 0.9 gave one signature;
two channels at 0.9 and 0.2 and the same two at 0.9 and 0.9 gave two.

A further module
(`organism:src/organism/actuation/dimension.py::ActionDimensionRegistry`)
groups signatures that drive the same channel set and admits the group as an
action dimension when its dominant effect is frequent enough and more frequent
than elsewhere. The thresholds are described in the code as "Experimental
gate parameters; deliberately not frozen scientific values." A dimension
records the surfaces on which its evidence was gathered. In an ad hoc run a
dimension learned on one surface was reported available and bound there;
on a second surface offering the same channel references it was available and
not bound; on a surface without them it was neither, and remained in the
registry.

Both modules, and the attempt record
(`organism:src/organism/actuation/attempt.py::ActionAttempt`), have no test
and no caller. The identifier namespaces now use Biopeia names: intervention signatures
use `biopeia-intervention-signature-v2`, and action dimensions use
`biopeia-action-dimension-v3`. Both registry schema versions were incremented
so checkpoints carrying the previous identifier namespaces fail closed instead
of silently retaining those identities. This is a compatibility boundary, not
evidence that either registry is integrated into an Organism checkpoint.

## Footprints

One consumer of evidence rows is tested:
`organism:src/organism/actuation/footprint.py::FootprintRegistry`. It answers
a narrower question than the models: of the atoms seen after pulses on one
channel set, which occur more often than a quiet period of the same length
would explain.

A pulse is one commitment with at least three rows that all drive the same
channel set (`test_pulses_are_commitments_on_one_channel_set`). An atom
becomes a member of the set's footprint when the lower 95 % Wilson bound of
its hit rate over pulses exceeds the rate expected from passive windows of the
same length by a margin, with at least four pulses; it leaves only when the
bound falls to a lower margin
(`test_length_matched_baseline_rejects_drift_that_pulses_merely_last_longer_for`,
`test_weak_real_effects_enter_the_footprint`, `test_too_few_pulses_never_enter`,
`test_wilson_bound`). Every entry and exit is logged with the estimate that
caused it, and a content that something refers to can be pinned so that it
keeps resolving while membership changes
(`test_every_membership_change_is_a_traced_transition_with_its_rule`,
`test_pinned_content_keeps_resolving_as_a_distinct_snapshot`). Its export
restores exactly (`test_restored_registry_continues_the_same_causal_history`).
The module states: "Nothing here writes evidence."

Here the baseline is passive windows only, unlike the models above. The tests
build their evidence rows by hand; no test passes rows from a ledger. The
optional membership rules behind switches (false discovery rate, block
replication) are covered by `test_bh_membership_keeps_real_effects_and_rejects_rest_level_drift`
and `test_block_replicated_membership_needs_two_independent_blocks` and were
not examined further.

## Across a restart and a change of body

| Part | Export | Restore |
|---|---|---|
| Effect space | counts per pattern, footprint effects, pressure counters | exact in the ad hoc run |
| Evidence ledger | every row of both lists and both capacities | exact in the ad hoc run; a row in the wrong list is refused |
| Controllability and agency models | list of estimates | exact in the ad hoc run for controllability |
| Forward model | none | rebuilt from the ledger by a caller |
| Signature registry | signatures and counts; not the recent command index | exact for signatures |
| Dimension registry | dimensions, channels and verified surfaces | availability is false until a surface is bound again |
| Footprint registry | members, versions, pins and the transition log | `test_pinned_snapshot_survives_restore_and_later_versions_exactly` |

No checkpoint in the repository includes any of these exports (search of
`organism:src/organism/checkpoint.py` and
`organism:src/organism/cognition/portable_checkpoint.py`, 2026-10-09; part of
finding F-0102).

Nothing in the ledger, the effect space or the models is keyed by a body. A
row carries a context reference and no surface or embodiment. If rows from two
bodies were reported to one ledger, the counts would pool them. Only the
dimension registry distinguishes surfaces.

| Boundary | What happens | Support |
|---|---|---|
| Birth | Every part starts empty | Code |
| Checkpoint | Each part but the forward model can be exported | Code and ad hoc run; tests for footprints only |
| Restart | Exports restore; no checkpoint carries them | Ad hoc run; search of the repository |
| Re-embodiment | Nothing reacts. Rows are not keyed by body. Dimensions keep their knowledge and lose availability and binding | Code and ad hoc run; no operation performs a re-embodiment |
| Reproduction | No operation exists | Search of the genetics code, 2026-10-10 |

[ADR-0092](../../technical/adr/ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md)
and [ADR-0095](../../technical/adr/ADR-0095-surviving-semantic-authorities.md)
place learning, agency and competence under the Organism's authority. These
modules live in the Organism package and import nothing from another domain,
which is consistent with that; whether the state is kept over the life of an
Organism depends on a composition that does not exist.
[ADR-0104](../../technical/adr/ADR-0104-body-schema-and-competence.md)
distinguishes learned knowledge about bodies and prior embodiments from its
current applicability; of the parts here, only the dimension registry makes
that distinction. These are statements of intent and this document does not
rule on conformance.

## Time

No part reads a clock; the search is described under
[competence development](competence-development.md#time-and-determinism).
Ticks are arguments, are stored as given, and are not required to increase.
A transition must end no earlier than it starts and a passive window must end
after it starts; nothing else relates one row's ticks to another's.

## What supports this description

| Claim | Support |
|---|---|
| How a change becomes an effect identifier; the count and confidence; the bound | Code and one ad hoc run of the module at that revision; tests cover only the static rounding function |
| Atoms | Code and tests in `organism:tests/source_unit/actuation/test_effect_atoms.py` |
| What a row holds, the two bounds, incremental counts and round trip | Code and tests in `organism:tests/source_unit/actuation/test_causal_evidence_checkpoint.py` |
| That the other rows include other sources | Code and the ad hoc run |
| The controllability formula and zero-hit guard | Code and tests in `organism:tests/source_unit/actuation/test_controllability_model.py` |
| The agency formula and values | Code and tests in `organism:tests/source_unit/actuation/test_controllability_model.py` |
| The forward model | Code and the ad hoc run; no test |
| Signatures and dimensions | Code and the ad hoc run; no test |
| Footprint membership, logging, pinning and restore | Code and tests in `organism:tests/source_unit/actuation/test_causal_footprints.py`; not run separately beyond the test suite |
| These mechanisms are not assembled by a production Organism/world runtime; test fixtures construct and exercise selected compositions | Source search at the reviewed repository heads; unit-test suite |
| Whose state this is | Accepted decisions ADR-0092, ADR-0095 and ADR-0104; statements of intent |

The source-unit coverage includes these mechanisms, including strict checkpoint
validation. No evidence from a production Organism run was examined; the code
and tests do not establish such a run. That these numbers track what an Organism can in fact control
is not supported by anything reviewed here.

## Open questions

- Which component reports transitions and passive windows to the ledger, and
  from what: the ledger expects references to states, commands and attempts
  that no code produces.
- Whether the comparison for controllability is meant to include the rows of
  other sources, and what the result should be when there is nothing to
  compare with.
- Whether evidence gathered with one body is meant to count for another.
- How the three numbers called controllability relate.
