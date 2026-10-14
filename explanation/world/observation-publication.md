# Post-commit observation publication and outcome classification

Reviewed against `world` at commit `e2be58700c870419a309ef3e2460b30b95c256be`
(main on 2026-10-14). Statements are marked by what supports them: the code,
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

## What supports this description

| Claim | Support |
|---|---|
| Four outcome states, classification logic, non-retry on publication failure | Code in `world:src/world/physical_step_publication.py` and tests in `world:tests/test_observation_publication.py` |
| Publication guard latching, inspection without mutation | Code in `world:src/world/durable_runtime.py:964-1100` |
| Owner observation structural and digest validation against committed cut | Code in `world:src/world/observation_publication.py` |
| Bit-identical non-interference and subscriber overflow resilience | Integration tests in `world:tests/integration/observation/test_world_post_commit_owner_publication.py` |
| Architectural passivity of observation | Accepted decision ADR-0078 |
