# The durable World runtime

Reviewed against `world` at commit `cb4bd6b0506b554bf4187b36c23095a7521c4504`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, or neither.

## What it is

The [journal](causal-journal.md), the [manifest](causal-manifest.md) and the
[snapshot store](journal-snapshot-store.md) are structures. None of them
decides when a tick has happened. The durable runtime is where that decision
is made: it is the component that takes a World from one committed causal cut
to the next, and the only place in this repository where a tick is published only after the
state it refers to has been made durable.

It is a coordinator. It never holds, reads or interprets the state of an
Organism, a body or an environment. It asks the owners to save their own
state, receives opaque references to what they saved, checks what it is able
to check, and publishes the cut. This division is the one ratified in
[ADR-0106](../../technical/adr/ADR-0106-hybrid-multi-owner-persistence.md).

## How a World starts

A durable World begins from a genesis specification
(`world:src/world/durable_runtime.py::WorldGenesisSpec`): the World's
identity, its initial presences, the owners registered with it, one initial
checkpoint reference per owner, and, per owner, a contract able to validate
that owner's checkpoints.

The specification is a declaration by whoever creates the World. The code
says so: it is "not a discovery mechanism for authorities external to the
accepted specification". World checks the declaration for internal
consistency (every registered owner has a reference and a contract, and no
reference lacks an owner); it cannot know whether an authority that should
have been declared was left out. Tests:
`test_genesis_spec_is_authoritative_input_for_tick_zero_roster`,
`test_complete_cut_requires_nonempty_stable_owner_identity_closure`.

Initialisation writes an empty journal snapshot, verifies every reference,
and publishes the manifest of tick zero in a way that cannot overwrite an
existing World.

## What happens in one tick

The order is the substance. Read from
`world:src/world/durable_runtime.py::DurableWorldRuntime.tick`:

1. **Refuse if busy or latched.** Only one tick may run in this runtime; a
   second call fails at once. If an earlier tick failed, every later call is
   refused.
2. **Check the durable state is the one this runtime last saw.** The manifest
   is read back. If a transition is found open it is marked as interrupted. If
   the manifest differs from the runtime's own copy, the runtime latches and
   refuses.
3. **Work out the proposed rosters.** The caller may register or unregister
   owners and presences and name participants of this step only. Inconsistent
   requests are rejected here, before anything is written, and leave the
   runtime usable.
4. **Open the transition durably.** The manifest is rewritten as preparing,
   still describing the previous cut, with the proposed rosters attached.
5. **Ask the owners to save.** A callback supplied by the caller persists the
   owners' new state and returns one reference per participant.
6. **Check what came back.** The references must name exactly the proposed
   participants. For each, World reads the bytes at the locator itself,
   compares their hash with the reference, and asks that owner's contract
   whether the checkpoint is valid.
7. **Extend the journal on a copy.** One record for the tick is appended to a
   copy of the journal, and the copy is written as a snapshot.
8. **Publish the cut.** The manifest of the new cut is committed through the
   manifest store, which re-verifies the references. Only then do the
   runtime's in-memory journal and manifest advance.

If anything from step 5 onward fails, the runtime latches, tries to mark the
durable manifest as requiring recovery with a description of the failure, and
re-raises. The tick counter does not advance.

Covered by tests: the order of publication
(`test_durable_tick_publishes_journal_and_owner_checkpoint_before_complete_manifest`),
roster changes only through an explicit tick
(`test_world_owner_registry_changes_only_through_explicit_lifecycle_tick`,
`test_lifecycle_registration_and_step_participants_are_explicit_and_exact`,
`test_presence_roster_is_published_only_through_world_lifecycle_tick`), a new
owner needing a contract
(`test_new_owner_cannot_register_without_owner_checkpoint_contract`), and a
failed registration keeping the previous cut
(`test_failed_registration_keeps_prior_cut_and_pending_roster_for_recovery`).

## What World checks, and what it trusts

For a causal cut, World verifies the journal snapshot, passes the non-World
checkpoint references to the configured reference verifier, and then checks
each owner reference itself: it reads the bytes at the locator, compares their
SHA-256 with the reference, and asks the registered owner contract to validate
those bytes for the recorded owner identity and schema version. The owner
contract and verifier are supplied by the caller; World does not parse or own
the checkpoint's private schema. There is no per-owner
`OwnerRecoveryReceipt` created by this validation path. The contract check is
covered by `test_world_rejects_owner_checkpoint_unless_contract_returns_true`
in `world:tests/test_durable_runtime.py`.

Everything else is trust. The contract is code supplied by the owner and
runs in the same process; World cannot tell whether it is honest or whether
the checkpoint is semantically complete. The repository's own documentation
states that the owner component is trusted code. These checks are not a
cryptographic attestation by the owner and do not demonstrate resistance to a
malicious or defective adapter.

## After a failure

A failed tick leaves the World in a state that needs explicit recovery, which
is what
[ADR-0093](../../technical/adr/ADR-0093-material-failure-before-commit-requires-explicit-recovery.md)
requires. Two things are true at that point and should not be confused:

- The **record** is coherent. The manifest still describes the previous cut.
- The **owners' state** may not be. The callback has already asked the owners
  to save, and may have advanced them, before the failure. In a run of the
  module, a tick that failed its roster check after the callback left the
  owner's new checkpoint file on disk, referenced by nothing.

Recovery (`DurableWorldRuntime.recover_previous_cut`) is explicit and is
delegated: World verifies the previous cut's references, calls a restorer
supplied by the caller to put the owners back, asks each owner's contract to
confirm the restoration, verifies the references again, and only then has the
manifest store write an immutable rollback-operation receipt and republish
the previous cut. This receipt records the World, transition, restored tick,
and hashes of the pending and recovered manifests; it is distinct from
checkpoint validation and is not an owner attestation. If the restoration
cannot be confirmed the World stays in recovery
(`test_explicit_recovery_restores_prior_cut_through_owner_and_records_receipt`,
`test_failed_owner_recovery_keeps_recovery_required_manifest`). The code
requires the restorer to be safe to retry.

Restarting a World from a committed cut (`DurableWorldRuntime.restore`)
follows the same pattern and refuses to produce a runtime if the references
no longer verify after the owners have restored
(`test_restore_validates_world_cut_then_delegates_owner_restore`,
`test_restore_refuses_runtime_if_owner_restore_changes_checkpoint_dependency`).

## What it does not guarantee

The component is explicit about its limits, in its own documentation and in
the repository's. Stated here so they are not lost:

- **It is not a transaction across owners.** There is no rollback. Coherence
  after a failure depends on the owners' restorers.
- **One logical writer is a precondition, not an enforced property.** Within
  one runtime a second tick is refused. Across runtimes or processes nothing
  holds a transition open exclusively: a second actor that checks the
  manifest while a tick is in progress marks it interrupted, and the first
  tick then fails at commit. A runtime notices that another actor changed the
  manifest only when it begins its next tick.
  [ADR-0084](../../technical/adr/ADR-0084-single-writer-or-explicit-coordination-for-shared-persistent-state.md)
  requires either a single writer or explicit coordination; this
  implementation relies on the first.
- **Crash consistency is not demonstrated.** The recovery path is described
  in the code as "not crash-consistency proof or a multi-process recovery
  protocol".
- **Completeness of the roster rests on the genesis declaration.**
- **One presence acts.** A runtime is bound to one presence, which cannot
  unregister itself in its own tick. The association between a presence and
  an owner is checked at genesis only and is not kept in the manifest.

## Time and identity

The runtime advances one clock, the causal tick, by exactly one per committed
transition. It reads no host time. Record and commit identifiers are derived
from the World identifier, the tick and the transition identifier supplied by
the caller.

## What supports this description

| Claim | Support |
|---|---|
| Genesis as authoritative input; order of publication; roster and presence changes; contract required for new owners; validation of owner bytes before acceptance; restore and explicit recovery; refusal when restoration cannot be confirmed | Code and tests in `world:tests/test_durable_runtime.py` at Biopeia World `9da5ecce209e66d955627cff1b57c58080683fa9` |
| An end-to-end tick with real owners from the other repositories | `world:tests/integration`, run by that repository's integration job in CI at pinned revisions |
| A roster error before the transition opens leaves the runtime usable; a failure after the callback can leave an unreferenced owner checkpoint | Code and tests in `world:tests/test_durable_runtime.py` at Biopeia World `9da5ecce209e66d955627cff1b57c58080683fa9`; this does not imply automatic cleanup |
| The limits listed above | Code and its documentation; they are statements of what is not provided, not results |

No crash, power-loss or concurrent-process test was examined, and none
appears to exist in the repository.

## Open questions

- What should enforce the single logical writer, if anything in World should.
- Whether unreferenced owner checkpoints and journal snapshots left by failed
  transitions are to be cleaned, and by whom.
- What would count as evidence of crash consistency for this protocol.
