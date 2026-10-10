# Prospective deliberation and the outcome-value ledger

Reviewed against `organism` at commit `6543188ff302a5f2dc8002c0086252d6061e5310`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run, or an accepted decision.

## What it is

The Organism package has two ways of picking one thing to do from several.
The first, admission of an affordance, is described under
[the action path](action-path.md). This document describes the second. It
takes a list of candidate actions, asks a caller-supplied function what
outcome each would lead to, looks up how past occurrences of that outcome were
valued, multiplies a few numbers and returns the candidate with the highest
product, or none.

The code calls this prospective agency and deliberation. What runs is a lookup
and an arithmetic comparison. The prediction is made elsewhere and handed in;
the value is a running mean of numbers a caller recorded. Nothing reviewed
here supports saying that an Organism foresees or weighs anything in a wider
sense.

**The result goes nowhere.** No code calls the deliberation outside its tests,
no code records a value in the ledger outside its tests, and no code turns the
returned record into an intent, a proposal or anything else on the action path
(search of the seven repositories at `origin/main`, 2026-10-09). The class
describes its own limits as "Never executes motors. Never records experience.
Never imports lab."

## The outcome-value ledger

The only state is a ledger
(`organism:src/organism/agency/value.py::OutcomeValueLedger`). It maps an
outcome, an opaque string, to running statistics of the numbers recorded for
it: count, mean, variance, counts of positive and negative values and the tick
of the last one. The module says where the numbers are meant to come from,
"derived exclusively from homeostatic deviation changes", but the ledger
cannot tell: it records whatever finite number it is given, limited to the
range from minus one to one. A value of 5.0 was stored as 1.0; a value that is
not finite is ignored without error
(`test_clamping_to_minus_one_plus_one`, `test_nan_observation_silently_ignored`,
`test_welford_mean_converges`).

Each record updates two tables. One is keyed by the outcome alone, at most
256 entries. The other is keyed by the outcome and a context key, at most 1024
entries. The context key is a digest of an ordered list of tokens; the ledger
never sees the tokens (`test_context_key_is_stable_and_order_sensitive`,
`test_same_outcome_can_have_opposite_value_in_two_private_contexts`). When a
table is full, the entry with the fewest samples, then the oldest, is dropped
(`test_capacity_enforced_at_256`, `test_eviction_removes_lowest_evidence_entry`).

An estimate carries a confidence equal to the number of samples over sixteen,
at most one (`test_confidence_saturates_at_16_samples`).

### Which table answers

Asked for an outcome in a context, the ledger returns the contextual entry if
one exists and otherwise the entry for the outcome alone
(`test_unknown_context_falls_back_to_global_value`). The class describes this
as: "Prospective lookup
prefers the contextual estimate and falls back to global evidence while a
new context is still evidence-poor."

The code falls back only when the context has no sample at all. Confirmed by
running the ledger: an outcome recorded sixteen times at +1 without a context
and then once at -1 in a context gave, for that context, a mean of -1 with a
confidence of one sixteenth. The seventeen samples of the other table were not
used. Since the policy below ignores estimates under a confidence of one
quarter, a context with one to three samples makes its outcome unselectable
there, whatever the wider evidence says. This is recorded in finding F-0104.

## One deliberation

`organism:src/organism/agency/prospective.py::ProspectiveAgency` holds a
ledger, a policy and a query budget. One call receives a tick, the candidates,
the context tokens, a number called homeostatic deviation between zero and
one, the prediction function, and optionally a function giving an epistemic
value per candidate. It proceeds in order:

1. If the caller says the organism is not alive, or has no active model, it
   returns at once with that reason.
2. If there are no candidates, no context tokens, or the ledger is empty, it
   returns with a reason (see the table below).
3. It keeps the first candidates up to the budget, eight by default, in the
   order given (`test_query_budget_limits_candidates_queried`).
4. For each it calls the prediction function. A call that raises, or returns
   something that is not a prediction record, drops the candidate silently
   (`test_predictor_exception_treated_as_no_candidate`).
5. It looks up the value of the predicted outcome in the current context.
6. It hands the evaluated candidates to the policy.

A prediction is an outcome string and a confidence class from 0 to 7. The
module describing the records is explicit that it is not an observation: "it
describes what the model predicts *would*
happen if the action were taken. It is never recorded as observed
experience."

## The policy

`organism:src/organism/agency/policy.py::ProspectivePolicy` drops candidates
without a value estimate, with a confidence class under four of seven (a
minimum of 0.5 by default), or with a value confidence under one quarter (four
samples by default). For the rest:

```text
utility = mean value * value confidence * (confidence class / 7) * homeostatic deviation
```

The candidate with the highest utility is returned if that utility is positive
and exceeds the second highest by a margin, 0.02 by default. The module states
the rule: "A non-positive pragmatic utility is never selected prospectively."
(`test_best_utility_candidate_wins`,
`test_only_non_positive_value_abstains_from_pragmatic_prospection`,
`test_decision_margin_blocks_close_candidates`,
`test_homeostatic_need_scales_expected_value`,
`test_zero_homeostatic_need_abstains_from_pragmatic_prospection`).

Three consequences of the arithmetic, confirmed by running the policy:

- **With a deviation of zero nothing is ever selected.** The deviation
  multiplies every utility. The module says exploration is left to the other
  route, admission.
- **Candidates that predict the same outcome cannot be told apart.** Three
  candidates whose predictions named one outcome with one confidence class had
  equal utility, and none was selected.
- **The epistemic value almost never matters.** It orders candidates of
  exactly equal utility
  (`test_epistemic_value_breaks_only_exact_pragmatic_ties`,
  `test_epistemic_value_never_overrides_higher_pragmatic_utility`), but an
  exact tie has a margin of zero, which is under the default margin. Two tied
  candidates with epistemic values of 0 and 1 gave no selection. The tests
  that show the tie-break build the policy with a margin of zero.

A further tie-break exists below that: a digest of the organism identifier,
the tick and the action identifier (`test_tiebreaking_is_deterministic`,
`test_tiebreaking_varies_by_tick`). It is deterministic and reads no clock;
see [competence development](competence-development.md#time-and-determinism).

## The record returned and its reasons

The result (`organism:src/organism/agency/types.py::DeliberationOutcome`)
carries the tick, the selected candidate or none, the predicted outcome, the
utility under the name expected value, two confidences, the margin and a
reason from a closed list of eight strings. Obtained by running the class:

| Situation | Reason returned |
|---|---|
| a candidate selected | `selected` |
| organism not alive | `physiology_dead` |
| no active model | `no_active_model` |
| no context tokens | `no_active_model` |
| no candidates, or every prediction call failed | `no_candidates` |
| ledger empty, or no predicted outcome has a value | `no_value_evidence` |
| model or value confidence too low | `insufficient_confidence` |
| two candidates too close | `insufficient_margin` |
| best utility zero or negative, including a deviation of zero | `insufficient_margin` |

Two of the reasons therefore cover situations their names do not describe.
The eighth string, `budget_exhausted`, is never returned. A selection with a
single eligible candidate has no margin and reports none.

The readiness check the class calls
(`organism:src/organism/agency/readiness.py::check_readiness`) lists six
conditions; two of them are fed the same fact, whether the candidate list is
empty. It has no test of its own.

## Where candidates come from

The package offers one source:
`organism:src/organism/agency/candidates.py`, which lists established
competences as candidates of the family `competence`; see
[competence development](competence-development.md). Nothing connects it to
the deliberation except that both use the same candidate record. The
prediction function has no implementation in these two packages.

Nor is this route connected to the other. Admission produces a decision record
with a field for a counterfactual prediction reference, which would let a
deliberation be cited; no code fills it from one.

## Across a restart

The class exports the ledger and a schema version, and restores from it
(`test_checkpoint_roundtrip_preserves_ledger`,
`test_restore_fails_closed_on_wrong_schema`). The ledger's own restore is
strict: an unknown version, a malformed entry, a duplicate or a table over
capacity is refused whole, and a version-one export without contexts is
accepted (`test_checkpoint_roundtrip_preserves_statistics_and_context`,
`test_restore_accepts_v1_global_checkpoint`,
`test_restore_rejects_corrupted_entry_instead_of_returning_partial_ledger`,
`test_restore_rejects_global_checkpoint_over_capacity_without_truncation`).

The policy, the budget and the organism identifier are not exported; the
caller supplies them again. A module
(`organism:src/organism/agency/checkpoint.py`) lists what is and is not
persisted and defines a schema version constant that the class does not use;
the class writes the number 1 itself.

No checkpoint in the repository includes the export (search of
`organism:src/organism/checkpoint.py` and
`organism:src/organism/cognition/portable_checkpoint.py`, 2026-10-09; part of
finding F-0102).

## At each lifecycle boundary

| Boundary | What happens | Support |
|---|---|---|
| Birth | A new ledger is empty, and with an empty ledger nothing is selected | Code and ad hoc run |
| Checkpoint | The ledger can be exported; nothing else is state | Code and tests |
| Restart | An export can be restored; no checkpoint carries it | Code and tests; search of the repository |
| Re-embodiment | Nothing reacts. Values are keyed by outcome and context digest, not by body | Code; no operation performs a re-embodiment |
| Reproduction | No operation exists | Search of the genetics code, 2026-10-09 |

## Beside the decisions

[ADR-0092](../../technical/adr/ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md)
and [ADR-0095](../../technical/adr/ADR-0095-surviving-semantic-authorities.md)
place agency and learning under the Organism's authority. The ledger lives in
the Organism package, imports nothing from another domain and refuses nothing
on the grounds of where a value came from.

[ADR-0105](../../technical/adr/ADR-0105-cognition-structure.md) describes
cognition as "DEVELOPMENTALLY PROGRESSIVE AND SUSPENDIBLE WITH STATE
PRESERVED" and makes no claim of efficacy. The deliberation returns without
selecting while there is no model, no context or no recorded value, and the
ledger is untouched by those returns; that is as far as the code goes toward
it. Whether an Organism is in any of those conditions is told to the class by
its caller. These are statements of intent and this document does not rule on
conformance.

## What supports this description

| Claim | Support |
|---|---|
| What the ledger stores, the limit to minus one and one, the two tables and their bounds, eviction, confidence | Code and tests in `organism:tests/source_unit/agency/test_value.py` |
| A context with one sample displaces the wider estimate | Code and one ad hoc run of the module at that revision; the test covers only a context with no sample |
| The order of a deliberation, the budget, dropped predictions | Code and tests in `organism:tests/source_unit/agency/test_prospective.py` |
| The utility formula, thresholds and margin | Code and tests in `organism:tests/source_unit/agency/test_policy.py` |
| Equal predictions give no selection; a tie on utility is not broken under the default margin | Code and the ad hoc run |
| The table of reasons | The ad hoc run, and tests for some rows |
| Export and strict restore | Code and tests |
| The schema constant is unused; the policy and budget are not exported | Code and the ad hoc run |
| Nothing calls the deliberation, records a value or consumes the result | Search of the seven repositories at `origin/main`, 2026-10-09 |
| Whose state this is, and that cognition may be undeveloped or suspended | Accepted decisions ADR-0092, ADR-0095 and ADR-0105; statements of intent |

No value recorded during a run of an Organism was examined, because none can
exist at this revision. That selection by this rule serves an Organism is not
supported by anything reviewed here.

## Open questions

- Which component records values, from which signal, and at which tick
  relative to the action that preceded the outcome.
- Which component supplies predictions, and what an outcome string denotes.
- How a selection is meant to enter the action path, and how it relates to
  admission when both return something.
- Whether a contextual estimate with few samples is meant to displace the
  estimate for the outcome alone.
