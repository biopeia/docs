---
diataxis_kind: how-to
document_id: HOWTO-WLD-RECOVERY
domain: world
source_of_truth: world:src/world/durable_runtime.py
review_basis: world@e2be58700c870419a309ef3e2460b30b95c256be
---

# How to Recover a World Runtime from a Failed Causal Cut

This procedure guides operators and maintainers through recovering a durable World runtime when an in-flight tick was interrupted before completion.

Reviewed against `world` at commit `e2be58700c870419a309ef3e2460b30b95c256be`.

## Context and operational conditions

Under [ADR-0093](../../technical/adr/ADR-0093-material-failure-before-commit-requires-explicit-recovery.md), any failure during a causal transition locks the runtime in a durable `recovery_required` state. Ordinary ticks and normal runtime restoration are blocked until an explicit recovery procedure is performed.

Recovery always rolls back to the previous confirmed cut; it **never** attempts to guess or complete an interrupted tick.

## Procedure

### Step 1: Diagnose the recovery requirement

Inspect the causal manifest (`manifest/world-manifest-v2.json`) in the affected state root:

```python
import json
from pathlib import Path

state_root = Path("./runs/m1-session-interrupted")
manifest_data = json.loads((state_root / "manifest" / "world-manifest-v2.json").read_text())

print("Status:", manifest_data.get("status"))
print("Failed transition ID:", manifest_data.get("pending_transition", {}).get("transition_id"))
print("Committed cut tick:", manifest_data.get("committed_cut", {}).get("tick"))
```

If `status == "recovery_required"`, proceed to Step 2.

### Step 2: Instantiate the durable runtime in recovery mode

Load the durable runtime pointing to the state directory. The runtime will detect the recovery requirement:

```python
from world.durable_runtime import DurableWorldRuntime
from world.owner_checkpoint_store import FileOwnerCheckpointStore

checkpoint_store = FileOwnerCheckpointStore(state_root / "checkpoints")
runtime = DurableWorldRuntime(state_root=state_root, checkpoint_store=checkpoint_store)

assert runtime.is_recovery_required(), "World runtime is not in recovery-required state"
```

### Step 3: Execute `recover_previous_cut`

Invoke recovery passing the competent owner state restorer callback:

```python
def owner_restorer(owner_name: str, checkpoint_ref: dict) -> bool:
    """Restores the authoritative owner state for the specified cut."""
    # Delegate to the owner's restore interface (Organism, Embodiment, Environment)
    return True

receipt = runtime.recover_previous_cut(restorer=owner_restorer)
print("Recovery completed successfully. Receipt ID:", receipt["receipt_id"])
```

### Step 4: Verification of restored state

Verify that:

1. The uncommitted journal bytes were discarded and rolled back to the last committed cut offset.
2. The manifest records the cut as committed with no pending transitions:

   ```python
   assert not runtime.is_recovery_required()
   assert runtime.current_tick == manifest_data["committed_cut"]["tick"]
   ```

3. An immutable recovery receipt is persisted under `manifest/receipts/`.

The World is now restored to a clean, consistent state and may be safely resumed.

## What supports this procedure

| Claim | Support |
|---|---|
| Mandatory explicit recovery contract | [ADR-0093](../../technical/adr/ADR-0093-material-failure-before-commit-requires-explicit-recovery.md) |
| Rollback method `recover_previous_cut` | `world:src/world/durable_runtime.py::DurableWorldRuntime.recover_previous_cut` |
| Uncommitted journal truncation | `world:src/world/durable_runtime.py::_discard_uncommitted_tail` |
| Receipt generation and verified recovery tests | `world:tests/test_durable_runtime.py::test_explicit_recovery_restores_prior_cut_through_owner_and_records_receipt` |
