# The M1 bounded process bootstrap and operator profile

Reviewed against `world` at commit `07a4db8f2fe6a0dde1a01a63ab27c158e71cf3f5`
(main on 2026-10-17). Statements are marked by what supports them: the code,
the tests, or an accepted decision. A decision states intent; it is not a
result.

> Review note, 2026-10-17. This document was rewritten against `07a4db8`. The
> previous version, reviewed at `d66ac61`, described the preflight, the profile
> schema and the state-directory layout incorrectly even at that revision:
>
> - it described the preflight as refusing a dirty tree and checking pinned
>   dependency revisions;
> - it described a profile schema version 2;
> - it listed `manifest/`, `journal/` and `checkpoints/` directories.
>
> Code references now name functions and tests rather than line ranges.

## What it is

The M1 bounded process bootstrap is the production entry point for
multi-cycle sensorimotor simulation runs. It is a command-line executable,
`world-m1 = "world.m1_process:main"` in `world:pyproject.toml`:

```text
world-m1 --profile <operator-profile.json> --state-root <new-directory> [--cycles <1-10000>]
         [--organism-checkpoint {v4,v5}] [--archive-observations] [--archive-max-payload-bytes N]
```

Without `--cycles`, the process runs until it is signalled or the domain ends
it (`world:M1_PROCESS_CONTRACT.md`, "Candidate command").

The process contract (`world:M1_PROCESS_CONTRACT.md`) separates operator
configuration inputs, durable simulation state and downstream observability.
Its rule is that a run either starts cleanly or fails before changing anything.

## Preflight

Before it creates anything on disk, `main` (`world:src/world/m1_process.py`)
runs a block that the code marks as read-only:

1. **The operator profile.** It is loaded and validated by
   `load_operator_profile`.
2. **Provenance of the source.** `verified_revisions()` records revisions
   "as provenance, not admission pins":
   - the World checkout's full `HEAD` commit; preflight fails if it cannot be
     read;
   - the installed World distribution's version, which must equal the version
     in `pyproject.toml`, or preflight fails;
   - the working tree state, `clean` or `dirty`. A dirty tree is **recorded**,
     with a `world_worktree_sha256` digest of the diff and untracked files,
     **not refused**;
   - each runtime dependency's VCS commit, read from its `direct_url.json` and
     recorded as found, or as `"unavailable"`. It is not compared with a pin;
   - MuJoCo, which must be exactly `3.15.0`, or preflight fails.
3. **The state root.** The path must not exist and must not be a symlink. Its
   parent must resolve without symlinks.

If any of this fails, the process prints one JSONL record to **standard
output**, with `event: "failed"` and `outcome: "preflight_failed"`, and exits
with code `2`. The target path is left unchanged. Tests:
`test_preflight_failure_does_not_create_or_mutate_state_root`,
`test_existing_state_target_is_byte_for_byte_unchanged_on_preflight_failure`,
`test_incompatible_installed_world_version_fails_preflight_without_mutation` and
`test_invalid_organism_checkpoint_fails_preflight`, all in
`world:tests/integration/test_m1_process.py`.

**Contract and code differ.** `M1_PROCESS_CONTRACT.md` asks to "fail
preflight if required revisions cannot be verified". At `07a4db8`, an
unverifiable dependency revision is recorded as `"unavailable"` and preflight
continues. This document describes the code.

## The operator profile

A profile is a configuration input: *"Operator profiles are configuration
inputs, not physical ground truth or simulation results"*
(`M1_PROCESS_CONTRACT.md`). Its schema is
`biopeia.world.m1.scalar-sensorimotor-profile`, version `1`, the only accepted
version (`PROFILE_SCHEMA_VERSION = 1` in `world:src/world/m1_profile.py`).

The repository ships two profiles, both schema version 1. Both load at this
revision, and both include `geometry_revision` in their Embodiment definition.

| File | `profile_id` | Solver revision |
|---|---|---|
| `profiles/m1/scalar-sensorimotor-mujoco-3.15-v1.json` | `m1.scalar-sensorimotor.operator-r2` | `mujoco-3.15.0-m1-operator-r2` |
| `profiles/m1/scalar-sensorimotor-mujoco-3.15-v2.json` | `m1.scalar-sensorimotor.operator-r3` | `mujoco-3.15.0-m1-operator-r3-grid-v2` |

The `-v1` and `-v2` suffixes are profile revisions, not schema versions; the
two files differ only in these two fields. Each profile holds sections for the
World, Embodiment, Environment, Modality, Organism, the solver, the
Observation bridge and provenance. Profile parameters set initial conditions;
they do not dictate causal outcomes.

The scenario derives from historical acceptance benchmarks in the
documentation repository
(`docs:technical/migration/MIGRATION_END_TO_END_ACCEPTANCE_REPORT.md:48-61`, at
commit `586dcbb8376c2800fc7ea8e04ba0b486db3e87db`), updated for MuJoCo 3.15.0.
The contract treats that report as provenance for scenario intent, not as
validation of this executable.

## Command-line options

- `--organism-checkpoint {v4,v5}`, default `v4`. It selects self-contained v4
  exploration checkpoints, or compact v5 checkpoints with World-verified
  action-history dependencies (`test_fresh_world_process_runs_with_organism_checkpoint_v5`).
- `--archive-observations`, off by default, added by World #190. It attaches
  Observation's `LocalObservationArchiveCapture` to the runtime's
  `ObservationPlane`, writing `observations.sqlite` in the state root. The
  terminal record then carries an `observation_archive` summary, whose
  sequence kind is `observation_plane_delivery_not_world_causal_tick`.
  Archive teardown errors are reported but never turn a committed outcome into
  a failure. If the capture cannot start, the run is reported as `failed` with
  `outcome: "recovery_required"`, the label the general exception path uses,
  even though no tick ran.
  Tests: `test_opt_in_observation_archive_captures_only_deliveries_during_run`
  and `test_archive_capacity_gap_does_not_fail_world_or_uncommit_cycles`.
  The archive is passive local capture, not Lab evidence custody.
- `--archive-max-payload-bytes N`, between 1 and 64 MiB; the default is
  64 MiB.

## Genesis and runtime construction

After the `starting` and `initializing` records, `construct_fresh_runtime`
(`world:src/world/m1_profile.py`) builds the runtime:

1. It creates the owner checkpoint store `FileOwnerCheckpointStore(state_root / "owners")`
   and calls `write_genesis()` (`world:src/world/owner_checkpoint_store.py`).
   That writes the initial Organism, Embodiment and Environment checkpoints as
   content-addressed blobs at `owners/<digest[:2]>/<digest>.blob`, with
   checkpoint IDs `genesis:<digest[:24]>`.
2. It opens `manifest.json` (`WorldCausalManifestStore`) and the `journal/`
   directory (`DurableJournalSnapshotStore`), and initialises the durable World
   at tick 0 with the verified genesis references.
3. It creates an in-memory `ObservationPlane` and a
   `LocalObservationReadBridge`. The bridge's host comes from the profile's
   `observation_bridge` section; the shipped profiles use `127.0.0.1`, with
   allowed origin `http://127.0.0.1:4173`. The port is ephemeral, since
   `main` passes `observation_port=0`.

When the bridge has started, the process prints a `ready` record carrying the
bridge URL (`observation_bridge`).

## Signals and teardown

The session loop is `run_scalar_sensorimotor_session`. `SIGINT` and `SIGTERM`
set a stop flag, checked only between completed cycles, so a cycle in progress
is not interrupted (`test_sigterm_stops_after_a_verified_cycle_boundary`).

On exit, the observation bridge is closed inside an inner `try`/`finally`
before the original signal handlers are restored. A second signal during the
close therefore does not interrupt it
(`test_signal_during_observation_bridge_teardown_does_not_interrupt_close`).
A runtime failure prints a terminal `failed` record with the last verified
committed cut and exits non-zero
(`test_runtime_failure_reports_last_committed_cut_and_nonzero_exit`).

## What supports this description

| Claim | Support |
|---|---|
| Entry point and options | `world:pyproject.toml` (`[project.scripts]`); `world:src/world/m1_process.py::main` |
| Process contract and its rules | `world:M1_PROCESS_CONTRACT.md` |
| Preflight checks, provenance recording, and no residue on failure | Code: `m1_process.py::verified_revisions` and `main`. The four preflight tests named above |
| Profile schema version 1 and the two shipped profiles | `world:src/world/m1_profile.py` (`PROFILE_SCHEMA`, `PROFILE_SCHEMA_VERSION`, `load_operator_profile`). Both files loaded with `load_operator_profile` at `07a4db8` |
| Genesis blobs, store layout and bridge construction | `m1_profile.py::construct_fresh_runtime`; `owner_checkpoint_store.py::write_genesis`, `_blob_path` |
| Observation archive option | `m1_process.py::main`; the two archive tests named above; World #190 |
| Real cycles and post-commit observations | `test_fresh_world_process_runs_real_cycles_and_serves_postcommit_observations` |
| Signals and teardown | The two signal tests named above |
