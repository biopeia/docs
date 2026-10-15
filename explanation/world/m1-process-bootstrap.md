# The M1 bounded process bootstrap and operator profile

Reviewed against `world` at commit `76680345941fb627764ad831deded267dc11777c`
(main on 2026-10-15). Statements are marked by what supports them: the code,
the tests, or an accepted decision. A decision states intent; it is not a
result.

## What it is

The M1 bounded process bootstrap is the production operating entry point for
autonomous, multi-cycle sensorimotor simulation runs.

It is implemented as a standalone command-line executable:
`world-m1 --profile <operator-profile.json> --state-root <new-directory> [--cycles <1-10000>]`
(`world:pyproject.toml:12-13`, `world:src/world/m1_process.py::main`).
An explicit `--cycles` bounds execution to a finite cycle count (1–10,000);
omitting `--cycles` selects continuous mode, which streams cycle results
without unbounded memory growth until an orderly stop signal or domain
termination is received.

The executable is governed by an explicit process contract
(`world:M1_PROCESS_CONTRACT.md`). It establishes clean separation between
operator configuration inputs, durable simulation state, and downstream
observability, ensuring that execution starts cleanly or fails closed without
partial side effects.

## Fail-closed preflight validation

Before allocating runtime resources or creating disk directories, `world-m1`
enforces strict preflight validation (`world:src/world/m1_process.py:20-68, 117-133`):

1. **Clean repository status:** The `world` repository must have a clean git
   working tree with no unstaged, staged, or untracked changes.
2. **Version matching:** Installed package metadata must match the version in
   `pyproject.toml`.
3. **Exact runtime dependency pins:** Inspects `direct_url.json` for installed
   dependencies, verifying exact 40-character commit hashes for:
   - `embodiment` (`a925c2f...`)
   - `environment` (`b71d556...`)
   - `modality` (`79b7791...`)
   - `observation` (`a0d3f61...`)
   - `organism` (`9c9339a...`)
4. **Physics solver version:** Strictly asserts `mujoco.__version__ == "3.15.0"`.
5. **Fresh state directory:** The target `state_root` path must not exist, must
   not be a symlink, and its parent directory must exist and resolve cleanly.

If any check fails, `world-m1` writes a single JSONL lifecycle event to
standard error with status `"failed"` and `outcome: "preflight_failed"`, and
exits immediately with code `2`. Crucially, the filesystem is left completely
unmodified (`world:tests/integration/test_m1_process.py:75-88, 165-181`).

## The operator profile

The configuration of a run is defined by an operator profile schema:
`biopeia.world.m1.scalar-sensorimotor-profile` version 1
(`world:src/world/m1_profile.py::load_operator_profile`).

The repository ships reference profiles:
- `world:profiles/m1/scalar-sensorimotor-mujoco-3.15-v1.json`: derived directly
  from historical acceptance benchmarks in the documentation repository
  (`docs:technical/migration/MIGRATION_END_TO_END_ACCEPTANCE_REPORT.md:48-61`) at
  commit `586dcbb8376c2800fc7ea8e04ba0b486db3e87db`, updated for MuJoCo 3.15.0.
- `world:profiles/m1/scalar-sensorimotor-mujoco-3.15-v2.json`: enables solver
  profile revision `operator-r3` (`m1-fixed-single-hinge-grid-v1`). World evaluates
  a deterministic bounded set of applied torques from a fresh MuJoCo state and
  commits only candidate transitions whose joint velocity respects Embodiment's
  maximum angular velocity cap without clipping `qvel`. Failure to find a
  compliant candidate fails the cycle. Each `cycle_committed` JSONL event emits
  `velocity_regulation` evidence (torque, effort limit, velocity cap, candidate
  velocity) as process telemetry.

The profile defines:
- World identifier and source revisions.
- Embodiment morphology, mass, damping, actuator mappings, and receptor offsets.
- Environment static arena boundaries, geometry, and scalar field parameters.
- Organism cognitive initial state, action parameters, and foundation conventions.

The process contract emphasizes: *"Operator profiles are configuration inputs,
not physical ground truth or simulation results."* Profile parameters specify
initialization conditions; they do not dictate causal simulation outcomes.

## Genesis persistence and runtime construction

Once preflight checks succeed, `construct_fresh_runtime`
(`world:src/world/m1_profile.py:596-666`) builds the production runtime:

1. Creates the state root directory structure: `manifest/`, `journal/`, and
   `checkpoints/`.
2. Instantiates `FileOwnerCheckpointStore` and invokes `write_genesis()`
   (`world:src/world/owner_checkpoint_store.py:81-100`). This persists the
   initial state blobs of Organism, Embodiment, and Environment using the
   canonical content-addressed format `checkpoints / digest[:2] / f"{digest}.blob"`
   and ID `f"genesis:{digest[:24]}"`.
3. Initializes `DurableWorldRuntime` with an initial cut at tick 0 containing
   verified genesis checkpoint references across all participating owners.
4. Starts an in-memory `ObservationPlane` and attaches a
   `LocalObservationReadBridge` (`observation:src/observation/http_bridge.py`)
   bound to ephemeral loopback port `127.0.0.1:0` with allowed origin
   `http://127.0.0.1:4173`.
5. Emits a JSONL `"ready"` event on standard output containing the bridge URL,
   run ID, and genesis cut receipt.

## Cooperative signals and teardown protection

Execution runs through `run_scalar_sensorimotor_session` (`world:src/world/causal_cycle.py:613-755`).
In finite mode, execution stops after the specified cycle count; in continuous
mode, it streams results without unbounded result retention (`retain_cycle_results=False`)
until interrupted or stopped by a domain stop predicate.

Process shutdown is governed by strict signal coordination:
- Traps `SIGINT` and `SIGTERM` signals (`world:src/world/m1_process.py:139-142`),
  setting an internal stop flag.
- The stop flag is checked strictly between completed cycles. An in-flight
  cycle is never interrupted mid-step, ensuring that physical stepping, durable
  commit, and owner adoption complete cleanly before halting.
- **Teardown signal protection (#154):** In commit `1f35e92`, the shutdown
  procedure encloses `runtime.observation_bridge.close()` in an inner
  `try...finally` block before restoring the caller's original signal handlers.
  This prevents a secondary signal received during HTTP bridge closure from
  raising an unhandled `KeyboardInterrupt` exception, ensuring clean,
  uninterrupted resource release
  (`world:tests/integration/test_m1_process.py:122-163`).

## What supports this description

| Claim | Support |
|---|---|
| Executable CLI entry point `world-m1` (bounded & continuous modes) | Code in `world:pyproject.toml:12-13` and `world:src/world/m1_process.py:main` |
| Process contract, lifecycle protocol, and preflight rules | Documented in `world:M1_PROCESS_CONTRACT.md` |
| Fail-closed preflight checks and zero disk residue on failure | Code in `world:src/world/m1_process.py:20-68` and tests in `world:tests/integration/test_m1_process.py:75-88` |
| Operator profile schema v1 and runtime builder | Code in `world:src/world/m1_profile.py` and tests in `world:tests/test_m1_profile.py` |
| Operator profile v2 and single-hinge velocity regulation | Config `world:profiles/m1/scalar-sensorimotor-mujoco-3.15-v2.json`, solver code in `world:src/world/adapters/articulated_mujoco.py`, and tests in `world:tests/integration/physical_step/test_velocity_regulation.py` |
| Genesis blob persistence at tick 0 | Code in `world:src/world/owner_checkpoint_store.py:81-100` and tests in `world:tests/test_owner_checkpoint_store.py` |
| Loopback observation bridge integration and ready event emission | Code in `world:src/world/m1_process.py:148-154` and integration tests |
| Cooperative signal trapping, safe teardown protection, and streaming continuous loop | Code in `world:src/world/m1_process.py:139-234` and tests in `world:tests/integration/test_m1_process.py:90-163` |

