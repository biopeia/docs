# The sensorimotor causal cycle

Reviewed against `world` at commit `e2be58700c870419a309ef3e2460b30b95c256be`
(main on 2026-10-14). Statements are marked by what supports them: the code,
the tests, or an accepted decision.

## What it is

The sensorimotor causal cycle is the end-to-end operational loop that
integrates an Organism, an articulated Embodiment, an Environment holding a
finite resource field, and the durable World runtime into a single, repeatable
causal transition.

The coordinator is implemented in
`world:src/world/causal_cycle.py::run_scalar_sensorimotor_cycle_and_publish`.
It replaces test-only simulation fixtures with a production coordination
path, proving that the multi-owner architecture executes and continues across
restarts without losing causal integrity
(`world:tests/integration/test_end_to_end_causal_cycle_acceptance.py`).

## The operational sequence

Each tick of the cycle advances through seven explicit stages:

1. **Receptor sample projection:** Embodiment projects the receptor sample
   point in the world reference frame at the source cut
   (`project_receptor_sample_point`).
2. **Environment field sampling:** Environment evaluates the scalar field at
   the receptor coordinates from a restored checkpoint, emitting a correlated
   `FiniteScalarFieldSample`.
3. **Cognitive perception and proposal:** The scalar sample is transduced via
   Modality (`DimensionlessScalarFieldIdentityV1`) and ingested by Organism
   (`advance_organism_from_scalar_field_for_physical_step`). Organism's
   action composer proposes a bounded motor exploration command and prepares
   its candidate checkpoint.
4. **Articulated physics advancement:** MuJoCo executes the physical step
   (`advance_articulated_mujoco_step_from_motor_command`), composing motor
   activations into joint torques, stepping the solver, and emitting
   articulated body pose and static scene candidates.
5. **Opaque checkpoint persistence:** The serialized checkpoint bytes of
   Organism, Embodiment, and Environment are written atomically to disk by
   `FileOwnerCheckpointStore` (`world:src/world/owner_checkpoint_store.py`).
6. **Durable World commit:** World commits the transition to the append-only
   manifest and journal (`world.tick()`), generating a tamper-resistant
   `CommittedWorldCut` receipt.
7. **Post-commit adoption and observation:** Owners adopt the candidate state
   against the verified receipt (`adopt_after_world_commit`), and World
   publishes verified owner observations to the observation plane.

## The owner checkpoint store

World stores owner checkpoints without inspecting or decoding their internal
contents.

The storage abstraction is implemented by `FileOwnerCheckpointStore`
(`world:src/world/owner_checkpoint_store.py:50`):
- It accepts opaque `OwnerCheckpointPayload` bytes, storing them in
  content-addressed files (`.checkpoint`) named by their lowercase SHA-256
  digest.
- Writes are performed atomically using a temporary file, `os.fsync`, and
  an atomic rename.
- Reading returns the verified raw bytes, confirming that the content matches
  its content-addressed locator.

## Restoration and live continuation

The cycle proves full crash-recovery continuation through
`restore_scalar_sensorimotor_runtime` (`world:src/world/causal_cycle.py:148`).

Given a durable World runtime and the latest committed cut:
1. World verifies the committed cut and reads the corresponding checkpoint
   bytes from the owner checkpoint store.
2. Organism, Embodiment, and Environment are restored from their exact
   committed checkpoint bytes.
3. Actuator applicability and surface fingerprints are validated.
4. Subsequent ticks executed on the restored runtime produce bit-identical
   causal journal records, body poses, and checkpoint digests when compared to
   uninterrupted live execution
   (`test_restored_causal_cycle_matches_live_continuation`).

## What supports this description

| Claim | Support |
|---|---|
| Complete cycle coordination and 7-stage sequence | Code in `world:src/world/causal_cycle.py` |
| Articulated MuJoCo execution from motor commands | Code in `world:src/world/adapters/articulated_mujoco.py` |
| Atomic, content-addressed owner checkpoint persistence | Code in `world:src/world/owner_checkpoint_store.py` and tests in `world:tests/test_owner_checkpoint_store.py` |
| Full state restoration and continuation matching live execution | Acceptance tests in `world:tests/integration/test_end_to_end_causal_cycle_acceptance.py` |
| Preserved domain ownership and passivity of observation | Accepted decisions ADR-0073, ADR-0078, ADR-0095 |
