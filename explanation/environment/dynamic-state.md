# A piece of the environment that changes

Reviewed against `environment` at commit
`0a9f4fbb1922cc6ca9e7b2489cf891606ef9ee41` (main on 2026-10-10). Everything below describes that
revision. Statements are marked by what supports them: the code, the tests,
or neither.

## What it is

The [static scene](static-scene.md) takes part in a physical step by
accepting that nothing changed. This component is the first place where
Environment accepts that something did: one object, with one position, that
may be somewhere else after a step.

It is deliberately small, and says so. The module calls itself a "dynamic
state fixture" that "demonstrates a bounded state transition contract" and
"does not define environmental laws, solve physics, or claim that a candidate
was physically calibrated". What it establishes is the shape of adoption for
state that moves, not any rule about how things move.

## What it holds

An owner
(`environment:src/environment/dynamic_state.py::DynamicEnvironmentOwner`)
holds one object's identifier, the frame it is expressed in, and its position
in metres. The owner is bound, when created, to one World, one environment
identifier and one revision.

## How the position changes

Only by adoption. The owner is handed a candidate (a correlation and a
proposed state of the object) together with the correlation it should
expect, and adopts only when:

- the expected correlation names the World the owner is bound to;
- the candidate carries exactly that correlation;
- the correlation names this environment and this revision;
- its tick is the one immediately after the last adopted;
- the proposed state is for the same object, in the same frame;
- and the proposed position is three finite numbers.

Then the object's position becomes the proposed one and the correlation is
recorded. A refusal changes nothing
(`test_environment_owner_adopts_only_world_correlated_same_object_transition`,
`test_rejects_wrong_world_step_environment_or_revision_without_mutation`,
`test_bound_world_rejects_matching_candidate_and_expected_from_another_world`,
`test_rejects_stale_tick_unknown_object_and_frame_without_mutation`).

## What adoption does not judge

The owner checks who the candidate is for and when. It does not check what
the candidate says, beyond its being finite. A run of the module confirmed
that a position of five million kilometres, below the ground, is adopted
like any other. Deciding whether a proposed position is physically or
ecologically admissible would be an environmental law, and the module states
that it defines none.

This is the difference from the static scene. There, the owner could refuse
any change because any change was wrong. Here a change is expected, and
nothing yet says which changes are right.

## Recovery

The checkpoint is canonical JSON with the owner's World, environment,
revision, frame, object state and last accepted correlation. Restoring
accepts exactly that shape, keeps the binding to the World even before any
step, refuses a recorded correlation from another World, and continues from
the next tick
(`test_checkpoint_restore_preserves_state_identity_and_next_step_continuity`,
`test_initial_checkpoint_preserves_world_attachment_before_first_step`,
`test_checkpoint_is_closed_and_requires_exact_schema`,
`test_checkpoint_rejects_last_correlation_from_another_world`).

The owner answers the first of the two questions World asks of an owner in a
causal cut, whether checkpoint bytes are valid for an identity and schema
(`test_checkpoint_schema_and_checkpoint_reference_validation_are_explicit`).
It does not provide the second, the confirmation after a restoration, which
the durable World runtime calls during restore and recovery; see
[the durable World runtime](../world/durable-runtime.md). Confirmed by
inspecting the class at that revision.

## Who uses it

Nobody yet. A search of the source and test trees of the other six
repositories at their main branches on 2026-10-10 found no use of this
module. It is exercised only by its own tests.

## What supports this description

| Claim | Support |
|---|---|
| Adoption rules, refusal without change, checkpoint strictness and continuity, World binding | Code and tests in `environment:tests/test_dynamic_state.py` |
| Any finite position is adopted; the restoration confirmation is absent | Code, and one ad hoc run of the module at that revision |
| No consumer | A search of the other repositories on 2026-10-10 |
| That it defines no environmental law | The module's own documentation |
