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

Under [ADR-0093](../../technical/adr/ADR-0093-material-failure-before-commit-requires-explicit-recovery.md), any failure during a causal transition locks the runtime in a durable `RECOVERY_REQUIRED` status. Ordinary ticks and normal runtime initialization are blocked until an explicit recovery procedure is performed.

Recovery always rolls back to the previous confirmed cut; it **never** attempts to guess or complete an interrupted tick.

## Read-only diagnosis and programmatic integration contract

The diagnostic inspection in Step 1 can be performed with the installed World package. **Steps 2–4 are integration guidance, not a self-contained runnable recovery recipe.** They require a host with real owner checkpoint verifier, domain owner contracts and restoration callbacks. Do not execute the illustrative snippets against a real state root without those implementations and tested authorization. A successful return from a placeholder is not evidence that owner state was restored.

## Programmatic recovery procedure

### Step 1: Diagnose the recovery requirement

Inspect the causal manifest (`manifest.json`) in the affected state root:

```python
from pathlib import Path
from world.manifest import ManifestStatus, WorldCausalManifestStore

state_root = Path("./runs/m1-session-interrupted")
manifest_store = WorldCausalManifestStore(state_root / "manifest.json")
manifest = manifest_store.read()

print("Status:", manifest.status.value)
print("Pending transition ID:", manifest.pending_transition_id)
print("Committed cut tick:", manifest.causal_tick)

if manifest.status is ManifestStatus.RECOVERY_REQUIRED:
    print("Explicit recovery required before runtime can resume.")
```

If `manifest.status is ManifestStatus.RECOVERY_REQUIRED`, proceed to Step 2.

### Step 2: Initialize stores and identifiers

Instantiate the manifest and journal stores associated with the state root:

```python
from world.durable_runtime import DurableJournalSnapshotStore
from world.runtime import WorldId

world_id = WorldId(manifest.world_id)
presence_id = manifest.presence_ids[0] if manifest.presence_ids else None
journal_store = DurableJournalSnapshotStore(state_root / "journal", world_id)
```

### Step 3: Execute `DurableWorldRuntime.recover_previous_cut`

Recovery is executed through the classmethod `DurableWorldRuntime.recover_previous_cut`, passing the stores, owner verification contracts, and an `owner_checkpoint_restorer` callback:

**Pseudocode only — do not copy and execute as an operational recovery command.** The example below illustrates the integration contract. Note that `restore_organism_checkpoint`, `restore_embodiment_checkpoint`, and `restore_environment_checkpoint` are **illustrative integration handlers** that the runtime host or orchestrator provides to reload checkpoint state into running domain subsystems. The exact failure and journal-tail behavior must be checked against the pinned World implementation and its tests. An unsuccessful owner restoration must not be reported as a successful recovery.

```python
from pathlib import Path
from world.durable_runtime import DurableWorldRuntime
from world.manifest import CheckpointReference

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


def owner_checkpoint_restorer(references: tuple[CheckpointReference, ...]) -> None:
    """Restores authoritative owner state from verified committed checkpoint references."""
    for ref in references:
        locator_path = Path(ref.locator)
        if not locator_path.is_file():
            raise FileNotFoundError(f"Missing required checkpoint payload: {locator_path}")

        # Dispatch checkpoint payload to the owning domain's restore interface:
        if ref.owner == "organism":
            restore_organism_checkpoint(locator_path)
        elif ref.owner == "embodiment":
            restore_embodiment_checkpoint(locator_path)
        elif ref.owner == "environment":
            restore_environment_checkpoint(locator_path)
        else:
            raise ValueError(f"Unrecognized owner in checkpoint reference: {ref.owner}")


# Execute atomic rollback via classmethod; returns a recovered DurableWorldRuntime:
recovered_runtime = DurableWorldRuntime.recover_previous_cut(
    world_id,
    presence_id,
    manifest_store,
    journal_store,
    owner_checkpoint_verifier=owner_checkpoint_verifier,
    owner_checkpoint_contracts=owner_checkpoint_contracts,
    owner_checkpoint_restorer=owner_checkpoint_restorer,
)
```

### Step 4: Verification of restored state

Verify that:

1. The uncommitted journal bytes were discarded and rolled back to the prior committed cut offset via `DurableJournalSnapshotStore._discard_uncommitted_tail`.
2. The manifest records the cut as committed with no pending transitions:

   ```python
   assert recovered_runtime.status is ManifestStatus.COMMITTED
   assert recovered_runtime.causal_tick == manifest.causal_tick
   ```

3. An immutable recovery receipt is persisted under `state_root / "recoveries" / f"{receipt_sha256}.json"`.

Only after a real owner restorer has successfully completed, the returned state and durable receipt have been independently verified, and the host has checked all owner contracts may the World be considered restored. This document by itself does not establish an operator-supported recovery path.

## What supports this procedure

| Claim | Support |
|---|---|
| Mandatory explicit recovery contract | [ADR-0093](../../technical/adr/ADR-0093-material-failure-before-commit-requires-explicit-recovery.md) |
| Rollback classmethod `recover_previous_cut` | `world:src/world/durable_runtime.py::DurableWorldRuntime.recover_previous_cut` |
| Uncommitted journal truncation | `world:src/world/durable_runtime.py::DurableJournalSnapshotStore._discard_uncommitted_tail` |
| Owner checkpoint restoration pattern | `world:tests/test_durable_runtime.py::test_explicit_recovery_restores_prior_cut_through_owner_and_records_receipt` |
