# Evidence that an actuator does something

Reviewed against `organism` at commit `3cc0f319f4ac00a631685aae0999134b6d64007f`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run, or an accepted decision.

## What it is

An Organism is given a set of channels it may command and is told nothing
about what any of them does. Before it can rely on a channel it needs some
sign that using it has a consequence. This component keeps that sign: for
each channel, a running summary of how its activation has gone together with
changes in what the Organism perceives.

It is deliberately passive. The class says of itself that it "never proposes
or authorizes an action. It only summarizes evidence about opaque channels
already present on the current actuator surface". It records; something else
decides what to try.

The words in the code are stronger than what the code does, and this
document uses the weaker ones. What is kept is a correlation between two
series of numbers. It shows that a channel's activation and a percept moved
together in what was recorded. It does not show cause, and nothing here
shows that the Organism knows, controls or intends anything.

It complements the pieces described in
[how an Organism acts](action-path.md) and
[competence development](competence-development.md), which it does not call
and which do not call it.

## What is kept for each channel

One record per actuator of the surface
(`organism:src/organism/actuation/candidate.py::ActuatorCandidateState`),
and never for an actuator the surface does not have. It holds:

- how many times the channel was observed active;
- for each percept it has been paired with, a bounded statistical summary of
  the pairs of activation and change in that percept;
- the same kind of summary partitioned by exact physical context;
- a state, dormant or active;
- the tick it was last seen, and the number of samples that was required when
  it became active, plus the context fingerprint that justified promotion.

The model keeps two layers of bounded aggregate, not a log: no history of
activations or percepts is kept. A longitudinal aggregate tracks up to 256
percepts per channel and evicts the weakest when full. Separately, evidence is
partitioned by an exact context consisting of body, embodiment episode,
morphology revision and surface fingerprint. Up to 128 contexts are retained;
reaching that limit refuses a new context rather than discarding history.
Each context can track up to 256 percept relations, and reaching that limit
also refuses new evidence.

The longitudinal aggregate exposes an **effect strength**: the largest
absolute correlation between activation and change, over percepts with at
least three pairs. Promotion is separate and uses the analogous strength
and sample count from the current exact context. A channel whose activation
tracks a change scores high in that summary and one paired with noise scores low
(`test_effect_strength_is_high_for_causal_relation_and_low_for_noise`); the
test's name says causal, and what it checks is correlation.

## What the numbers depend on

Each observation is a pair: an activation, and the change in a percept that
followed it. The record cannot check where the pair came from. Its
documentation states the obligation on the caller: the change must be the
percept one tick after the activation minus the percept at the activation,
and the method "does not and cannot verify that contract itself; it only
accumulates whatever pair it is handed". A test shows what goes wrong when
the pairing is shifted
(`test_observe_effect_pairing_contract_correct_vs_wrong_time_shift`).

So everything downstream is only as good as the pairing done by a caller.
The code records the pair in both the longitudinal aggregate and the exact
current context; promotion uses the context-specific evidence, not the pooled
aggregate.

## Becoming active

All channels start dormant
(`test_new_proposer_has_all_actuators_dormant`). A channel becomes active
when asked to be considered and two conditions hold: its best-supported
percept has at least a minimum number of pairs, twelve unless the caller says
otherwise and never fewer than three, and its effect strength reaches a
threshold, one half unless configured
(`test_natural_evidence_can_promote_actuator_from_endogenous_activity`,
`test_natural_evidence_does_not_promote_before_minimum_samples`).

A run of the module confirmed both sides: twelve pairs in which the percept
changed in proportion to the activation made a channel active, and twelve
pairs with a constant change did not.

Nothing makes a channel dormant again. The set of active channels is called
the active repertoire.

The class notes that this is the only route: evidence that arose in ordinary
activity, with no scheduled probing. It says the probing apparatus moved to a
Lab module, `lab.studies.common.actuator_probing_calendar`, for studies run
by Lab. No source module of that name exists in the `lab` repository at its
main branch on 2026-10-10; the name appears there only in migration records.

## Saving and restoring

The whole state can be exported and restored
(`organism:src/organism/actuation/checkpoint.py`). Export holds every
record in full, including summaries with a single pair
(`test_to_payload_exports_relations_unconditionally_including_single_sample`).

Restoring is strict in several ways, each tested:

- the payload must hold exactly one record per actuator of the surface it is
  restored onto, no more and no fewer
  (`test_restore_raises_when_candidate_set_does_not_match_constitution`);
- each record must be stored under its own identifier
  (`test_restore_raises_when_candidate_key_does_not_match_its_own_actuator_id_field`);
- fields are neither defaulted nor coerced
  (`test_from_payload_raises_on_missing_field_instead_of_defaulting`,
  `test_from_payload_raises_on_invalid_field_value_instead_of_coercing`);
- a record that claims to be active must carry evidence that it could have
  become so
  (`test_restore_raises_when_active_candidate_evidence_does_not_satisfy_promotion`),
  judged against the number of samples recorded at the time and not against
  today's strength, which may have fallen since
  (`test_restore_accepts_naturally_promoted_candidate_after_effect_strength_decays`).

The threshold is not saved. The code calls it configuration and expects the
caller to supply it again.

## Across bodies

The checkpoint records and validates the owning Organism identity and source
context. Restoring it for a different Organism is rejected. Restoring it for
the same Organism under a different body, episode, morphology revision or
surface retains the prior evidence but demotes active applicability; new
context-specific evidence is required before promotion. Tests cover rejection
of a foreign Organism, re-embodiment retention/demotion, and invalidation on
each physical-context change. The surface constitution must still match the
checkpoint's actuator set.

Two decisions bear on this.
[ADR-0094](../../technical/adr/ADR-0094-somatic-state-ownership-body-holds-organism-regulates-and-feels.md)
says "Body-bound motor competence and sensory/interoceptive calibration are
not transferred and must be reacquired", and
[ADR-0104](../../technical/adr/ADR-0104-body-schema-and-competence.md) says
re-embodiment "may invalidate active commitments/calibration but must not
silently erase longitudinal learning". The code neither invalidates nor
erases: what it has learned about a channel follows the channel's name to
whatever body carries that name. Whether evidence about a channel is
body-bound competence or longitudinal learning, and so which sentence
applies, is not settled here.

## Small types in the same package

`organism:src/organism/actuation/types.py` defines the value types used at
the edge of actuation: a motor intent with an activation required to be a
finite number in the unit interval and not a boolean
(`test_motor_intent_requires_activation_in_unit_range`,
`test_motor_intent_rejects_non_finite_and_bool_activation`), and an
actuation record that carries no interpreted health or cost
(`test_actuation_contains_no_interpreted_health_or_cost`).

`organism:src/organism/actuation/state.py` defines a snapshot of counters
(effects, evidence, competences, intents and others) for reporting. It is a
plain record of numbers and is constructed nowhere in the source or tests of
the repository at this revision.

## Time and randomness

Ticks are supplied by the caller and only stored. No clock and no random
source is read.

## Who uses it

Nobody outside the package. The model is constructed only by its own restore
function and by tests; a search of the source of the other repositories on
2026-10-10 found no use of the model, its export or its restore. No Organism
checkpoint carries this state.

## What supports this description

| Claim | Support |
|---|---|
| What is kept, the bound on percepts, effect strength, promotion rules, export and strict restore | Code and tests in `organism:tests/source_unit/actuation/test_candidate.py`, `test_proposer.py`, `test_checkpoint_gate.py` and `test_types.py` |
| Promotion is context-specific; foreign-Organism restore rejects; physical-context change retains prior evidence but clears active applicability | Code and tests in `organism:tests/source_unit/actuation/test_checkpoint_gate.py` and `test_candidate.py` |
| The pairing obligation on the caller | The code's own documentation, and one test |
| No user outside the package; the Lab module named does not exist | Searches of the repositories at their main branches on 2026-10-10 |
| What re-embodiment should do to motor learning | Accepted decisions ADR-0094 and ADR-0104; statements of intent |
