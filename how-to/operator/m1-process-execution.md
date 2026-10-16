---
diataxis_kind: how-to
document_id: HOWTO-WLD-M1-EXECUTION
domain: world
source_of_truth: world:src/world/m1_process.py
review_basis: world@1f35e92611ed76f1863136916601f07fc2fd78c1
---

# How to Execute an M1 Bounded Simulation Process

This guide provides the exact operational procedure for running an autonomous, multi-cycle M1 simulation run using the `world-m1` command-line executable.

Reviewed against `world` at commit `1f35e92611ed76f1863136916601f07fc2fd78c1`.

## Prerequisites and preflight checks

Before launching an execution run, ensure your execution environment meets the strict preflight requirements:

1. **Verify repository cleanliness:**
   The working tree must have no untracked, staged, or unstaged modifications:

   ```bash
   git status --porcelain
   ```

   *(Must return empty output).*

2. **Verify MuJoCo version:**
   Confirm that MuJoCo version 3.15.0 is installed:

   ```bash
   python3 -c "import mujoco; assert mujoco.__version__ == '3.15.0', f'Expected 3.15.0, got {mujoco.__version__}'"
   ```

3. **Verify profile configuration:**
   Ensure your profile is a valid JSON document conforming to schema `biopeia.world.m1.scalar-sensorimotor-profile` v1. You can inspect the reference profile at:
   `profiles/m1/scalar-sensorimotor-mujoco-3.15-v1.json`

## Procedure

### Step 1: Select an unallocated state root path

`world-m1` enforces a fail-closed check requiring that the target `--state-root` path **does not exist**:

```bash
RUN_DIR="./runs/m1-session-$(date +%Y%m%d-%H%M%S)"
# Verify that RUN_DIR does not exist yet:
test ! -e "$RUN_DIR" || { echo "Directory already exists: $RUN_DIR" >&2; exit 1; }
```

### Step 2: Execute `world-m1`

Invoke the executable with the profile, state root, and requested cycle count (between 1 and 10000):

```bash
world-m1 --profile profiles/m1/scalar-sensorimotor-mujoco-3.15-v1.json \
         --state-root "$RUN_DIR" \
         --cycles 100
```

### Step 3: Monitor runtime startup

During initialization, `world-m1` emits lifecycle events on stdout:

- A JSONL `ready` event is emitted upon genesis commit at tick 0:

  ```json
  {"event": "ready", "run_id": "...", "bridge_url": "http://127.0.0.1:...", "tick": 0}
  ```

- The local loopback observation bridge is active and reachable by visualization clients during execution.

### Step 4: Verify post-run artifacts

Upon clean completion with exit code `0`, inspect the generated state root:

```bash
ls -la "$RUN_DIR"
```

The directory structure must contain:

- `manifest/`: The durable causal manifest (`world-manifest-v2.json`) recording the final committed cut.
- `journal/`: The append-only event journal (`world-causal-journal-v3.jsonl`).
- `checkpoints/`: Content-addressed binary state blobs for Organism, Embodiment, and Environment.

## Diagnostic and error recovery

| Symptom | Cause | Resolution |
|---|---|---|
| Exit code `2` with `outcome: "preflight_failed"` | Dirty git working tree or unmet dependency pin. | Run `git status` and stash/commit all changes; verify dependencies in `.venv`. |
| Exit code `2` with `state_root_exists` | The path specified in `--state-root` already exists. | Specify a new, non-existent target path. |
| Process halted via `SIGINT` | Operator interrupted run. | `world-m1` finishes the current in-flight cycle cleanly before terminating. The state root remains at a consistent, committed cut. |

## What supports this procedure

| Claim | Support |
|---|---|
| CLI arguments and cycle range | `world:src/world/m1_process.py::parse_args` |
| Preflight assertions and exit code 2 | `world:src/world/m1_process.py:20-68` and `world:tests/integration/test_m1_process.py:75-88` |
| Lifecycle events (`ready`, `failed`) | `world:src/world/m1_process.py:148-154` |
| Signal safety between completed cycles | `world:tests/integration/test_m1_process.py:90-163` |
