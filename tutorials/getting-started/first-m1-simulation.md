---
diataxis_kind: tutorial
document_id: TUT-WLD-FIRST-M1-SIMULATION
domain: world
source_of_truth: world:src/world/m1_process.py
review_basis: world@1f35e92611ed76f1863136916601f07fc2fd78c1
---

# Your First M1 Autonomous Simulation

Welcome to Biopeia. In this guided tutorial, you will run an autonomous, 10-cycle sensorimotor simulation using the canonical M1 bootstrap process, inspect the resulting causal journal, and verify the committed checkpoints across participating domain owners.

Reviewed against `world` at commit `1f35e92611ed76f1863136916601f07fc2fd78c1`.

## What you will learn

By the end of this tutorial, you will:

- Understand how an operator profile initializes the simulation.
- Execute a bounded 10-cycle simulation run.
- Examine how World commits cuts at each tick.
- Locate and inspect the content-addressed checkpoint blobs created by Organism, Embodiment, and Environment.

## Requirements

Ensure you are working inside the activated Biopeia environment:

```bash
python3 -c "import world; import mujoco; print('Ready:', mujoco.__version__)"
```

*(Should output `Ready: 3.15.0`).*

## Step 1: Inspect the exemplary operator profile

Biopeia provides an exemplary profile configured with a MuJoCo 3.15 physical arena and an articulated body:

```bash
head -n 25 profiles/m1/scalar-sensorimotor-mujoco-3.15-v1.json
```

Notice the top-level declaration:

- `schema_name`: `"biopeia.world.m1.scalar-sensorimotor-profile"`
- `physics.solver_version`: `"3.15.0"`
- `embodiment`: Defines joint masses and sensor placements.
- `environment`: Defines the static terrain and scalar chemical field.

## Step 2: Launch the 10-cycle simulation

Create a clean temporary directory for your simulation run:

```bash
TARGET_RUN="/tmp/biopeia-tutorial-run"
rm -rf "$TARGET_RUN"

world-m1 --profile profiles/m1/scalar-sensorimotor-mujoco-3.15-v1.json \
         --state-root "$TARGET_RUN" \
         --cycles 10
```

### What happens as it runs

1. **Preflight validation:** `world-m1` verifies git status and exact dependency hashes.
2. **Genesis commit:** At tick 0, genesis checkpoints for Organism, Embodiment, and Environment are written.
3. **Loopback bridge:** A local HTTP observation bridge is bound to `127.0.0.1`.
4. **Execution cycles:** 10 discrete causal cycles execute in sequence, advancing the tick counter from 1 to 10.

Upon completion, you will see output concluding with exit code `0`.

## Step 3: Inspect the durable causal manifest

The manifest tracks the authoritative state of the World:

```bash
python3 -m json.tool "$TARGET_RUN/manifest/world-manifest-v2.json"
```

Look for the `committed_cut` section:

```json
{
  "status": "committed",
  "committed_cut": {
    "tick": 10,
    "cut_id": "...",
    "participants": ["organism", "embodiment", "environment"]
  }
}
```

This confirms that tick 10 was reached, all three owners participated, and their state updates were committed deterministically.

## Step 4: Trace the append-only causal journal

Now open the journal to see the step-by-step history:

```bash
head -n 3 "$TARGET_RUN/journal/world-causal-journal-v3.jsonl"
```

Each line records an immutable causal cut with:

- The tick index (`0`, `1`, `2`, ...).
- The hash references of the owner checkpoints at that exact moment.
- The physics step outcome.

## Step 5: Verify the content-addressed checkpoint store

Inspect the binary state blobs stored under `checkpoints/`:

```bash
find "$TARGET_RUN/checkpoints" -type f
```

Each file is stored using a content-addressed two-level hash directory structure (`checkpoints/ab/abcdef...blob`). This ensures that identical states share storage and that no checkpoint can be corrupted silently.

## Congratulations

You have completed your first autonomous Biopeia simulation! You have seen firsthand how:

- The operator profile sets the starting parameters without dictating the causal outcome.
- World acts as the authoritative coordinator and commit boundary.
- Every state transition is recorded durably and verified against content hashes.

To explore further, see:

- [The M1 Bounded Process Bootstrap (Explanation)](../../explanation/world/m1-process-bootstrap.md)
- [How to Execute an M1 Bounded Simulation Process (How-To)](../../how-to/operator/m1-process-execution.md)
- [M1 Operator Profile Specification (Reference)](../../reference/parameters/m1-profile-specification.md)
