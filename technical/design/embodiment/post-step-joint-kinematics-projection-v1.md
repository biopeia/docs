# Embodiment — Post-step Joint Kinematics Projection v1

## Purpose and decision

This document records the bounded owner disposition for [Embodiment #75](https://github.com/biopeia/embodiment/issues/75).

**Owner disposition (2026-10-16):** adopted post-step joint kinematics are an intended Embodiment-owned projection candidate. The source is the complete `ArticulatedEmbodimentPhysicalState` returned by `adopt_candidate`, not `BodyPhysicalInput` and not an untrusted solver candidate. This does not authorize a new public API, Observation mapping, storage format, runtime implementation, scientific claim, or historical compatibility behavior. Any passive Observation mapping requires a separate bounded issue after the remaining coordinate-semantics checks below.

The disposition is bounded by the exact code revisions recorded here and the limitations below. It is not a claim that the current code emits joint observations or that any such projection has been used at runtime.

## Evidence basis

Inspected current repository `origin/main` revisions on 2026-10-16:

| Repository | Revision | Relevant source |
|---|---|---|
| Embodiment | `957af224e4400fc30a9d8d78d987cec16a8e959e` | `src/embodiment/physics3d/articulated_state.py`; `src/embodiment/physics3d/physical_transition.py`; `src/embodiment/physics3d/physical_projection.py`; `src/embodiment/physics3d/mechanics.py` |
| Observation | `0e11ab728b4debb30e2d851ef3aa4149cc32dcb0` | `src/observation/semantic.py`; `src/observation/embodiment.py` |
| World | `1e42240beb82f0647d89e796d4a325a240d1b147` | `src/world/adapters/articulated_mujoco.py`; `tests/integration/physical_step/test_first_biopeia_physical_causal_step.py` |
| Lab | `4234ff0f5a182e587b5fc4eb66f837dcdab9912a` | `MIGRATION.md` row for `lab/src/lab/observation/joint_kinematics.py` |

Embodiment's `ArticulatedEmbodimentPhysicalState` owns the adopted root state, active morphology and joint values. Construction checks exact joint identity coverage and morphology limits. Its root state records a causal tick and the correlated preceding physical step. `adopt_candidate` accepts the candidate only against a `WorldPhysicalStepContext`, then returns a new owner state. The value's checkpoint digest describes encoded state; `durably_referenceable` is false, so digest presence alone is not proof of persistence.

`BodyPhysicalInput` contains joint identifiers and rad/rad/s values but its source documentation explicitly defines it as solver input. It is not the source of a post-step observation. Observation currently has generic semantic values and other Embodiment mappings; the inspected source does not establish a joint-kinematics family mapping. Lab's migration inventory records the historical adapter as dropped and defers any target projection to #75.

## Bounded owner-side projection semantics

If a future implementation is separately authorized, it must derive data from one already-adopted `ArticulatedEmbodimentPhysicalState` and preserve at least:

- `world_id`, `causal_tick`, `body_id`, `embodiment_episode_id`, and `morphology_revision` from that same owner state;
- `morphology_sha256` from its active morphology and the stable `joint_id` for each value;
- position in `rad` and velocity in `rad/s`, as checked against the active morphology's ranges;
- lineage to the exact source-state checkpoint digest and, when present, its `PhysicalStepCorrelation` (`physical_step_id`, source causal tick, environment revision and solver configuration revision).

The sample denotes the adopted state at its World causal tick, not a wall-clock timestamp and not the source tick of the solver request. World remains the authority that establishes whether that state belongs to a committed causal cut. Embodiment's projection does not itself authenticate a World commit or authorize Observation publication.

World's current articulated MuJoCo adapter reads `qpos` and `qvel` by each Embodiment joint's native address, creates the solver candidate, and passes that candidate to `body_state.adopt_candidate(..., world_context=context)` before checkpoint writing. The integration fixture exercises a one-hinge path. This establishes the current adapter path, not a solver-independent semantic contract. The owner representation has stable joint identity and an axis in each `JointSpec`, but the inspected contract and fixture do not fully specify a solver-independent sign/zero convention or frame semantics for generalized coordinates. **That semantic detail is not inferred here.** Before an Observation family contract is proposed, Embodiment must verify and specify it from the actual solver/adoption path and tests. Until then, consumers must not infer comparability across morphology revisions or solver configurations.

## Boundary and non-goals

- No reuse of the historical `JointKinematicsSample` or `simulated_apparatus_sample` claim shape.
- No claim of physical measurement, calibration, scientific validity, equivalence, or evidence admission.
- No direct projection from solver input, solver candidate, caller-built values, or morphology descriptor alone.
- No extension of the existing Body Pose Observation contract and no new Observation adapter, API, persistence, transport, or Lab consumer in this decision.
- No change to causal commit ownership: World decides causal ordering and committed-cut inclusion; Observation may only map an owner-authorized projection after a separately approved contract.
- No change to Lab evidence custody or experiment protocols.

## Follow-up and closure gates

1. Independently review this exact design candidate under BAW-004, including the authority and coordinate-semantics claims.
2. Embodiment owner verifies the solver-to-adopted-state coordinate sign/zero/frame convention against source and tests, or explicitly narrows any eventual projection to the convention the evidence establishes.
3. Reconcile Lab #237's migration row with this owner disposition and link the source/target revisions; do not reclassify the historical adapter as retained code.
4. If a passive Observation mapping is still warranted, open a separate Observation implementation issue with its own owner-approved semantic family and tests. Otherwise record the reason and leave only the Embodiment-owned state available.

This is a design/owner disposition only. It does not authorize implementation or close any linked work automatically.
