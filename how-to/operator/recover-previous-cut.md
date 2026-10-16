---
diataxis_kind: how-to
document_id: HOWTO-WLD-RECOVERY
domain: world
source_of_truth: world:src/world/durable_runtime.py
review_basis: world@e2be58700c870419a309ef3e2460b30b95c256be
---

# How to Recover a World Runtime from a Failed Causal Cut (Programmatic Contract)

This procedure describes how a durable World runtime recovers after an in-flight causal tick was interrupted before commit.

Reviewed against `world` at commit `e2be58700c870419a309ef3e2460b30b95c256be`.

> [!IMPORTANT]
> **Operational availability notice:** An automated operator CLI command (such as `world-m1 recover`) is **not yet implemented**. In the current release, recovery is an internal programmatic operation on `DurableWorldRuntime`.
>
> Operators and integrators must **not** employ stub restorers that return success unconditionally (`return True`). Causal recovery under ADR-0093 requires passing each `CheckpointReference` to its competent domain owner (Organism, Embodiment, Environment) to restore verified persistent state from disk.

## Context and operational conditions

Under [ADR-0093](../../technical/adr/ADR-0093-material-failure-before-commit-requires-explicit-recovery.md), any failure during a causal transition locks the runtime in a durable `recovery_required` state. Ordinary ticks and normal runtime restoration are blocked until an explicit recovery procedure is performed.

Recovery always rolls back to the previous confirmed cut; it **never** attempts to guess or complete an interrupted tick.

## Programmatic recovery procedure

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

Load the durable runtime pointing to the state directory. The runtime detects the recovery requirement:

```python
from world.durable_runtime import DurableWorldRuntime
from world.owner_checkpoint_store import FileOwnerCheckpointStore

checkpoint_store = FileOwnerCheckpointStore(state_root / "checkpoints")
runtime = DurableWorldRuntime(state_root=state_root, checkpoint_store=checkpoint_store)

assert runtime.is_recovery_required(), "World runtime is not in recovery-required state"
```

### Step 3: Execute `recover_previous_cut` with domain owner restoration

Recovery requires passing a callable `restorer(references: tuple[CheckpointReference, ...])` to `recover_previous_cut`. The runtime passes the tuple of `CheckpointReference` objects recorded at the last committed cut, and the caller must ensure each participating domain owner (Organism, Embodiment, Environment) restores its live state from the payload at `ref.locator` before returning.

The example below illustrates the integration contract. Note that `restore_organism_checkpoint`, `restore_embodiment_checkpoint`, and `restore_environment_checkpoint` are **illustrative integration handlers** that the runtime host or orchestrator provides to reload checkpoint state into the running domain subsystems. If any domain restoration fails or raises an exception, the World runtime does not commit the recovery receipt, and the uncommitted journal tail remains untouched.

```python
from pathlib import Path
from world.checkpoint_reference import CheckpointReference

# Illustrative integration handlers: integrators implement these to route checkpoint
# payloads to their running subsystem instances or continuation engines.
def restore_organism_checkpoint(locator: Path) -> None:
    """Illustrative: dispatch to Organism continuation / cognitive memory loader."""
    ...


def restore_embodiment_checkpoint(locator: Path) -> None:
    """Illustrative: dispatch to Embodiment somatic / joint state loader."""
    ...


def restore_environment_checkpoint(locator: Path) -> None:
    """Illustrative: dispatch to Environment static scene / entity state loader."""
    ...


def owner_restorer(references: tuple[CheckpointReference, ...]) -> None:
    """Restores authoritative owner state from verified committed checkpoint references."""
    for ref in references:
        locator_path = Path(ref.locator)
        if not locator_path.is_file():
            raise FileNotFoundError(f"Missing required checkpoint payload: {locator_path}")

        # Dispatch checkpoint payload to the owning domain's restore interface:
        if ref.owner == "organism":
            # Organism restores private longitudinal cognitive state
            restore_organism_checkpoint(locator_path)
        elif ref.owner == "embodiment":
            # Embodiment restores physical somatic and joint configuration
            restore_embodiment_checkpoint(locator_path)
        elif ref.owner == "environment":
            # Environment restores static scene and dynamic resource entities
            restore_environment_checkpoint(locator_path)
        else:
            raise ValueError(f"Unrecognized owner in checkpoint reference: {ref.owner}")


# Execute atomic rollback:
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
| Owner checkpoint restoration pattern | `world:tests/test_durable_runtime.py::test_explicit_recovery_restores_prior_cut_through_owner_and_records_receipt` |
