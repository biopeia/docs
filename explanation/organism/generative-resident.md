# The generative resident and what a "private model" is in code

Reviewed against `organism` at commit `6543188ff302a5f2dc8002c0086252d6061e5310`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run, or an accepted decision.

## What it is

Beside [the cognitive graph](cognitive-graph.md) the package contains a
second, larger body of code under the name "Generative Cognition v1". Its own
one-line description is "bounded, non-factual internal cognition".

Stripped of its vocabulary, it is a bookkeeping system around a question it
cannot answer itself. Given a list of things marked as unresolved, it picks
one, asks whatever answer-producing objects have been plugged in for a guess,
files the guess as a record, and later, if told what actually happened, marks
the record as agreeing or disagreeing. Everything it stores is labelled as not
being an observation.

The answer-producing objects are what the code calls models, and in some
places private models. **There is no model in this repository.** There are no
weights, no training and no inference. There is an interface a model would
have to satisfy and four adapters that wrap a function supplied by the caller.
This document describes the bookkeeping and that interface.

The words used throughout the code (hypothesis, imagined, counterfactual,
replay, epistemic value, calibration) name records and counters. The
repository's migration notes say of the slice that carries this state that it
does not establish "that cognition is scientifically effective". Each term is
reduced below to the operation performed.

## The parts

| Name in the code | What it is |
|---|---|
| Resident (`organism:src/organism/cognition/generative/resident.py::ResidentGenerativeCognition`) | The object that owns the others and exposes one step |
| Agenda | A table of at most 64 targets: an identifier, one of seven source labels, some reference strings, and counters |
| Scheduler | A count of how many times each mode ran at each tick, against a quota |
| Registry | A dictionary from model identifier to model object |
| Workspace | The states and transitions produced in one step, under five limits |
| Hypothesis | A record: identifier, source identifiers, a number called uncertainty, one of five statuses, two lists of evidence references |
| Calibration | Per model, operation, depth band and uncertainty band: a count of guesses and a list of 0-or-1 errors |
| Use tracker | Per token: how often it appeared in generated states, in which episodes, with which source references |

A **state** is a tuple of features (a token string, an optional scalar, a
number called confidence) with an origin label, a parent, a depth and two
numbers in [0, 1] called uncertainty and coherence. A test pins the absence of
anything else: `test_state_requires_provenance_and_has_no_physical_fields`.
The origin label is one of seven words: observed, remembered, inferred,
replayed, imagined, counterfactual, abstract. Only inferred, replayed,
imagined and counterfactual are ever assigned by the code.

## One step

Read from `ResidentGenerativeCognition.step` and confirmed by running it.

The caller supplies a tick, a mode (online, idle or offline), optionally an
object called `cognition`, a tuple of candidate identifiers, and a tuple of
intent outcomes.

1. **Demand is recorded.** Three inputs create or refresh agenda targets:
   - each entry in `cognition.prediction_errors` becomes a target whose
     uncertainty is the entry's loss clipped to [0, 1];
   - each candidate identifier becomes a target `gc.prospective.<id>` with
     uncertainty 0.5;
   - each intent outcome whose status is `failed` or `invalidated` refreshes
     that target with uncertainty 1.0.

   A target beyond the agenda's capacity is dropped and counted
   (`test_demand_beyond_capacity_is_dropped_not_fatal`).
2. **A root state is made.** Its features are the sixteen largest entries, by
   magnitude, of `cognition.activations`; its uncertainty is the mean of the
   clipped losses, or 0.5 if there are none.
3. **One target is selected.** The agenda ranks eligible targets by a fixed
   weighted sum of their numbers; the code comments on the sum: "Technical
   scheduling score only; it is not a reward or world truth." In online mode
   only targets that came from candidate identifiers are eligible
   (`test_prediction_error_enters_endogenous_agenda_but_waits_for_compatible_model`,
   `test_idle_mode_routes_prediction_error_to_a_compatible_model`).
4. **The scheduler allows or refuses.** It refuses if there is no target, the
   workspace is closed, the model-query limit is spent, or this mode's quota
   for this tick is used
   (`test_scheduler_is_separate_from_target_selection_and_enforces_mode_quota`).
5. **Models are asked.** The target's reference strings are passed as the
   query. Depending on the target's source label and on how many registered
   models accept a branch query, one of three routines runs:
   - **rollout**: ask once per depth step, take the proposal of the model
     whose identifier sorts first, append a child state; depth is 1 online,
     up to 2 idle, up to 4 offline
     (`test_rollout_composes_multiple_steps_and_preserves_uncertainty`);
   - **branch**: ask once, append one sibling state per proposal, skipping any
     whose features duplicate an existing state
     (`test_branch_creates_deterministic_siblings_within_bound`,
     `test_branch_prunes_equivalent_generated_states`);
   - **counterfactual**: the rollout routine with a different operation label
     and origin label, and nothing else
     (`test_counterfactual_is_generated_and_never_executes_an_intervention`).

   A child's uncertainty is the larger of its parent's and the proposal's, so
   it never falls along a chain; coherence is the smaller.
6. **Records are filed.** For each transition a hypothesis is created, or an
   existing active one for the same target and model reused, with status
   "predicted" and a copy of the proposal's outcome tokens. Each guess is
   counted in the calibration table and each feature token in the use
   tracker.
7. **Progress is noted.** If the routine produced nothing, the target's
   no-progress count rises; at three it is suppressed for eight ticks
   (`test_no_progress_suppresses_repeated_target_and_later_reactivates_it`).

If no registered model answers, the step ends with no hypothesis
(`test_resident_loop_abstains_when_no_model_can_answer_prospective_target`).
The step returns a snapshot of counts and identifiers.

Two entry points bypass models. `materialize_replay` copies caller-supplied
tokens into a single state labelled replayed
(`test_materialized_replay_preserves_factual_source_without_creating_observation`).
`materialize_recombination` concatenates the features of two caller-supplied
fragments into a single state labelled imagined, provided the fragments share
at least one string in a field called compatibility keys
(`test_recombination_materializes_two_compatible_sources_as_imagined`,
`test_recombination_rejects_incompatible_fragments_without_workspace`). The
compatibility test is set intersection of strings the caller wrote.

## What a "private model" is in code

A model is anything with a `model_id`, a method `supports(operation, state)`
and a method `generate(state, operation, context)` returning proposals
(`organism:src/organism/cognition/generative/model.py::GenerativeModel`, a
structural protocol). A proposal is features, outcome tokens, two numbers and
some reference strings. The registry holds models by identifier and asks every
one that says it supports the operation
(`test_registry_routes_only_capable_models_in_stable_order`).

Four adapters are provided. Their module says: "Adapters only translate an
existing query result into ``GeneratedProposal``. They do not copy model
state, train models, record evidence, or execute actions."

| Adapter | What it wraps | What it returns |
|---|---|---|
| `PrivateSLMGenerativeAdapter` | a function of (first query token, remaining tokens) returning an object with a `predicted_token` and a `confidence_class` from 0 to 7 | one feature; confidence is the class divided by 7 |
| `CompetenceEffectGenerativeAdapter` | a function of (first token, second token) returning an `effect_id` and a `confidence`, or nothing | one feature named by the effect |
| `SensorimotorDynamicsGenerativeAdapter` | a function of the query returning a mapping of numbers | one feature per key, confidence fixed at 0.5 |
| `EpisodicReplayAdapter` | a function of the query returning features | those features, uncertainty and coherence fixed at 0.75 |

The first of these is the only place the phrase is tied to something concrete,
and what it ties it to is a callable. Whether that callable is a trained
language model, a lookup table or a constant is invisible to this package. In
the tests it is a lambda. The test
`test_resident_loop_uses_learned_competence_effect_adapter` registers an
adapter around a lambda that returns the string `effect.` followed by its
argument with confidence 0.75; nothing in it was learned.

An adapter treats the first query token as a competence identifier whatever
the target was. In a run, a target created from a prediction error between
nodes `p` and `s` was put to a competence adapter, which answered about a
"competence" named `p`. The query tokens are opaque strings and nothing checks
that a model is being asked a question of the kind it answers.

What the repository does not contain, checked by listing `organism:src` on
2026-10-09: any module that defines model weights, a tokenizer, a training
procedure or an inference gateway. The migration notes list the historical
modules for those and mark them as split to other owners or deferred. Model
objects are also not part of saved state; see
[the cognitive checkpoint](cognitive-checkpoint.md).

[ADR-0103](../../technical/adr/ADR-0103-portable-organism-state.md) says
"Private learned state belongs to Organism longitudinal continuity, including
private-model weights". At this revision there are no such weights in the
Organism repository for that sentence to apply to. The decision and the code
are set side by side; conformance is not ruled on.

## From "predicted" to "supported" or "contradicted"

A hypothesis changes status in one place:
`ResidentGenerativeCognition.note_factual_outcome`. The caller names an
action, the outcome tokens that occurred and one or more evidence references.

- Every reference is first passed to a resolver, a function the runtime is
  expected to install. If no resolver is installed, or it returns false for
  any reference, nothing changes and the call returns 0
  (`test_resident_rejects_unresolved_factual_evidence_without_mutation`).
- Otherwise each active hypothesis for `gc.prospective.<action>` is compared:
  if its stored outcome tokens share at least one string with the supplied
  tokens it becomes "supported", else "contradicted"
  (`test_resident_marks_matching_action_hypothesis_contradicted_by_factual_outcome`,
  `test_resident_contradicts_hypothesis_only_with_resolved_observed_fact`).
- The calibration table records an error of 0 or 1 for that guess, and the
  target is marked resolved.

So "supported" means: a string a callback returned earlier also appears in a
tuple the caller passed later, and a callback said the reference was
acceptable. The resident has no access to what happened. Its module says the
same of itself: "The resident does not own or cache factual records".

## The separation from fact, and what enforces it

The package's central claim about itself is that generated content never
becomes evidence or action. The class says: "It cannot execute actions or
write factual evidence." How far the code makes that true is worth separating
into what is structural and what is declarative.

**Structural.** The package imports nothing that could act or record a fact.
The resident has no reference to an actuator, a body, an experience ledger or
a World. Its outputs are snapshots and the values of three read-only methods.
This is a property of what the code can reach.

**Declarative.** Three things present themselves as guards and are not on any
path (search of `organism:src` for each name, 2026-10-09):

- `EpistemicFirewall` has three methods, each of which raises an error for
  any argument (`test_firewall_rejects_all_factual_and_executive_sinks`).
  Nothing calls them. They check nothing because there is nothing to check:
  calling one is how a caller would declare that an operation is forbidden.
- `GenerativeAgenda.reject_external_target` increments a counter and raises
  (`test_external_target_is_release_blocking_contamination`). Nothing calls
  it. The method that actually adds a target accepts any well-formed one; in a
  run, a target named `lab.task.1` with a reference `lab-label` was added.
  The agenda cannot tell where a string came from.
- `factual_contamination_count` is saved, restored and reported. No statement
  increments it.

**By convention.** The resolver decides what counts as evidence. With a
resolver that accepts everything, the identifier of a generated state was
passed as the evidence reference and the hypothesis was marked contradicted
on its strength (ad hoc run). The guarantee that generated output is not
evidence therefore rests on the resolver, which is outside this repository.

Recorded as finding F-0075.

## What other code is offered

Three read-only methods are the resident's output to the rest of an Organism.

- `anticipated_effects` lists outcome tokens beginning with `effect.` from
  active hypotheses, with the hypotheses that hold them.
- `epistemic_value_for` returns, for one candidate, three numbers in [0, 1]
  derived from its agenda target and hypotheses, and their mean. The code
  calls the mean "a bounded comparison signal, not a reward or action command"
  (`test_epistemic_value_is_comparison_signal_not_action_authority`).
- `consolidation_signals` reports the use tracker's counts per token. A
  separate object can turn a count into a request for a structural change to
  the graph and hand it to a function supplied by the caller
  (`test_mature_signal_projects_only_to_external_structural_contention`); the
  receiving component is not in this repository.

The admission stage of the [action path](action-path.md) has parameters
shaped for the first two: a collection of "generative" affordances and a
function from identifier to epistemic value. Neither side imports the other,
and no code connects them (search of `organism:src` for `anticipated_effects`
and `epistemic_value_for`, 2026-10-09: each appears only at its definition).

## Bounded, and where it is not

Most stores are capped: 64 targets, 128 hypotheses, 256 tracked tokens, and
per-step limits of 64 states, 64 transitions, depth 8, 8 branches and 128
model queries (`test_workspace_is_bounded_and_rejects_reserved_operations`).
When hypotheses are full, a finished one is discarded to make room, and if all
are active no new one is created.

Two stores have no cap, confirmed by a run of 2000 steps, each followed by a
reconciliation:

| Steps | Scheduler entries | Calibration errors | Saved state, bytes |
|---|---|---|---|
| 10 | 10 | 10 | 8 343 |
| 100 | 100 | 100 | 55 135 |
| 1000 | 1000 | 1000 | 113 239 |
| 2000 | 2000 | 2000 | 164 455 |

The scheduler keeps one entry per tick and mode it has ever allowed and never
removes one, although only the current tick's entry can affect a decision. The
calibration table appends one number per comparison. Both are written into
every saved state. Recorded as finding F-0074.

## Time

The step takes its tick from the caller and reads no clock. It does not
require the tick to increase: after a step at tick 10, a step at tick 2 was
accepted and produced an episode named for tick 2 (ad hoc run). That differs
from the graph's transition, which refuses a tick that does not advance. The
resident keeps its own counter, `generative_tick`, which counts depth steps
and is unrelated to the caller's tick.

The caller's tick is stored under the field names `started_symbiont_tick` and
`last_symbiont_tick`, a name from the code's origin that is now part of the
saved format.

## At each lifecycle boundary

| Boundary | What happens | Support |
|---|---|---|
| Birth | All tables empty; no model registered; no resolver | Code |
| Checkpoint | Agenda, scheduler, last workspace, hypotheses, calibration, use tracker and three counters are exported; models, the resolver, the budget and one counter are not | Code, tests and a run; see [the cognitive checkpoint](cognitive-checkpoint.md) |
| Restart | Restoring returns a resident with no models unless a registry is passed, and no resolver, so reconciliation is inert until one is installed | Code, `test_portable_checkpoint_restore_uses_explicit_external_model_registry`, and a run |
| Re-embodiment | No operation. The nearest is that a step may be given the identifiers that still exist, and targets for others are retired | Code and `test_prospective_targets_of_vanished_sources_are_retired` |
| Reproduction | No operation exists | Absence in the code (search of `organism:src/organism/cognition/generative` for `inherit`, `offspring` and `parent_id`, 2026-10-09) |

## What supports this description

| Claim | Support |
|---|---|
| The step, selection, scheduling, the three routines | Code and tests in `organism:tests/source_unit/cognition/test_generative_resident.py`, `test_generative_agenda.py`, `test_generative_scheduler.py`, `test_generative_rollout.py`, `test_generative_branch.py`, `test_generative_counterfactual.py`, `test_generative_execution.py` |
| The model interface, registry and adapters | Code and tests in `test_generative_model.py`, `test_generative_adapters.py` |
| No model, weights or training exist in the repository | Listing of `organism:src`, and `organism:MIGRATION.md` |
| Status changes by token overlap behind a resolver | Code and tests in `test_generative_resident.py`, `test_generative_hypothesis.py` |
| The guards have no caller; the contamination counter never changes; any well-formed target is accepted; a permissive resolver admits a generated identifier | Searches named in the text, and one ad hoc run at that revision |
| Outputs offered to agency are not connected | Search named in the text |
| Growth of the scheduler and calibration stores; a decreasing tick is accepted; an adapter answers a prediction-error target as a competence | The same ad hoc run |
| That the Organism owns this state and that no efficacy is claimed | ADR-0092, ADR-0105 and `organism:MIGRATION.md`; statements of intent and scope |

No run with a real model was examined; none can be made from this repository.

## Open questions

- Which repository will hold the model objects, and how a saved resident is to
  be reunited with the same models.
- Which component installs the resolver, and what it must refuse.
- Whether the three guards are meant to be called by something, or are
  statements of intent in code form.
- Whether a step should refuse a tick that does not advance.
- What should bound the scheduler's and the calibration table's history.
