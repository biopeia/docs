# Post-commit observation publication and outcome classification

Reviewed against `world` at commit `d66ac6197c8ea8489dc4f2689641ff0a88b6482a`
(main on 2026-10-16). Statements are marked by what supports them: the code,
the tests, or an accepted decision.

## What it is

Once a World causal cut has been committed to durable storage, observation
projections produced by domain owners may be published to an observation plane.
World coordinates this post-commit join through
`world:src/world/physical_step_publication.py::run_physical_step_and_publish`
and `world:src/world/observation_publication.py::publish_committed_owner_observations`.

World does not invent or alter semantic observations. Each observation must be
constructed by its domain owner's approved adapter from an exact committed owner
checkpoint. World's role is strictly the verification of causal cut identity,
owner checkpoint provenance, and correlation context before delivery to the
observation sink.

## The four caller-visible outcomes

An attempted physical step and publication returns a
`PhysicalStepPublicationResult` (`world:src/world/physical_step_publication.py:31`)
classified into one of four mutually exclusive outcomes
(`PhysicalStepOutcome`, lines 48-54):

1. **`NOT_COMMITTED`**: The transition failed before commit. The source cut
   remains active and committed in the manifest store. If failure occurred after
   owner preparation began, `recovery_required` is set to true.
2. **`COMMITTED_AND_PUBLISHED`**: The causal transition committed durably, the
   committed-cut receipt was verified, and all owner observations were accepted
   by the observation sink.
3. **`COMMITTED_PUBLICATION_INCOMPLETE`**: The causal cut committed durably and
   is authoritative, but observation delivery was partial or failed. Crucially,
   the committed cut is preserved; World never rolls back, retries, or
   re-executes a committed cut due to downstream publication failures.
4. **`COMMIT_UNKNOWN`**: The commit state could not be disambiguated from
   available store evidence (for example, if the manifest is in `PREPARING` or
   store I/O failed). Callers must halt execution and require explicit recovery.

## The publication guard and concurrency

Step execution and publication are serialized by
`world.committed_cut_publication_guard()`
(`world:src/world/durable_runtime.py:964`).

The guard enforces strict single-tick latching:

- If concurrent threads attempt a tick or publication, `TickInProgressError` is
  raised.
- Reentrancy within the same thread is permitted for receipt lookup, but a
  second nested tick is rejected.
- On step failure or exceptions, `world.inspect_transition_commit` inspects
  manifest evidence without mutating state or triggering recovery, enabling
  safe caller classification.

## Pre-publication validation of owner observations

Before any observation is passed to the sink,
`_validate_owner_observation` (`world:src/world/observation_publication.py:141-190`)
validates every item against the verified `CommittedWorldCut`:

- **Reference membership:** The observation's declared owner checkpoint digest
  must match an entry in the cut's `owner_checkpoint_references`.
- **Authority alignment:** The observation's declared authority must match the
  checkpoint reference owner.
- **Lineage integrity:** The observation's parent hash must equal the
  checkpoint SHA-256 digest.
- **Temporal correlation:** The observation's `target_causal_tick` and
  `world_id` must match the committed cut coordinates.

If any observation fails validation, publication fails closed before any items
are written to the observation plane.

## Passive observation non-interference

Observation is causally passive
([ADR-0078](../../technical/adr/ADR-0078-observation-is-causally-passive.md)).
Integration tests in
`world:tests/integration/observation/test_world_post_commit_owner_publication.py`
prove this non-interference:

- **Bit-identical execution:** Running a physical causal step with active
  observation publication produces byte-for-byte identical outcomes (causal
  tick, journal records, body pose, linear velocity, and owner checkpoint
  digests) compared to running the step without observation publishing
  (`test_passive_observation_publication_does_not_change_adopted_world_result`).
- **Subscriber overflow resilience:** When downstream observation subscribers
  overflow their buffer and force a ring-buffer rebase (`PlaneRebaseRequired`
  with `reason="consumer_overflow"`), World commit and owner adoption proceed
  without interruption or corruption
  (`test_observation_subscriber_overflow_does_not_change_world_causal_result`).

## Spatial projection and render observations

Following physical step execution, World handles two distinct classes of spatial
render observations:

1. **Cut-bound dynamic render link poses:**
   When an articulated solver produces a transient render pose candidate, World
   binds it to the committed cut via `associate_render_pose_candidate`
   (`world:src/world/spatial_projection.py`). World verifies that the candidate's
   source/target ticks and body identifier match the verified
   `CommittedWorldCut`, and that its parent reference names the cut's exact
   Embodiment checkpoint. It wraps the resulting `CommittedRenderPoseProjection`
   into an `OwnerObservation` with `embodiment_render_link_pose_observation` and
   delivers it through `publish_committed_owner_observations`. The digest
   covers only the candidate bytes; it is not added to the World journal or
   checkpoint.
2. **Static owner scene and morphology projections:**
   At initial cycle startup (`publish_static_spatial=True` in
   `world:src/world/causal_cycle.py`), static render projections
   (`environment_render_scene_observation` and
   `embodiment_render_morphology_observation`) are published directly to the
   `ObservationPlane` passively after the cut-bound claims. Static owner
   projections are not checkpoint snapshots and must not be laundered through
   World's committed-state association.

## Integration with the local observation read bridge

In end-to-end integration and operator processes
(`world:tests/integration/observation/test_world_post_commit_owner_publication.py`,
`world:src/world/m1_process.py`), the sink is an in-memory `ObservationPlane`
paired with a `LocalObservationReadBridge`
(`observation:src/observation/http_bridge.py`).

Following each durable World commit:

- World delivers the verified `embodiment.body_pose` and
  `environment.finite_scalar_field` claims to the plane, along with dynamic
  `embodiment.render_link_pose` projections and static spatial scene/morphology
  claims when configured.
- The read bridge exposes `GET /v1/current` on a loopback port
  (`127.0.0.1:<port>`), allowlisting requests from `http://127.0.0.1:4173`.
- Downstream observers read passive, detached snapshots over HTTP with
  `Cache-Control: no-store` without participating in the simulation thread.

## What supports this description

| Claim | Support |
|---|---|
| Four outcome states, classification logic, non-retry on publication failure | Code in `world:src/world/physical_step_publication.py` and tests in `world:tests/test_observation_publication.py` |
| Publication guard latching, inspection without mutation | Code in `world:src/world/durable_runtime.py:964-1100` |
| Owner observation structural and digest validation against committed cut | Code in `world:src/world/observation_publication.py` |
| Spatial projection cut association and verification | Code in `world:src/world/spatial_projection.py` and integration tests in `world:tests/integration/physical_step/test_articulated_production_join.py` |
| Bit-identical non-interference and subscriber overflow resilience | Integration tests in `world:tests/integration/observation/test_world_post_commit_owner_publication.py` |
| Architectural passivity of observation | Accepted decision ADR-0078 |
