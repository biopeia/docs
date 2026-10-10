# The durable World runtime

Reviewed against `world` at commit `a8d07fd791da76365aa74080eef1e82b11a599fd`.
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

The specification is a declaration by whoever creates the World. It requires
exactly one registered owner link for every initial active presence, as well
as a reference and contract for every registered owner. The code says genesis
is "not a discovery mechanism for authorities external to the accepted
specification": World guarantees roster completeness relative to the accepted
genesis, not completeness against undeclared external authorities. Tests:
`test_genesis_spec_is_authoritative_input_for_tick_zero_roster`,
`test_genesis_requires_explicit_unique_links_to_registered_owners` and
`test_genesis_requires_presence_owner_and_durable_checkpoint_closure`.

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
   owners' new state and returns one reference per participant. It may also
   return owner-authored opaque causal records associated with the transition.
6. **Check what came back.** The references must name exactly the proposed
   participants. For each, World reads the bytes at the locator itself,
   compares their hash with the reference, and asks that owner's contract
   whether the checkpoint is valid. Owner causal records must be structurally
   valid, uniquely identified and bound to participating owners.
7. **Extend the journal on a copy.** World appends the tick record and any
   owner causal records to a copy of the journal, then writes the copy as a
   snapshot.
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
- **Writer coordination evidence is bounded.** A thread-based test excludes
  a second concurrent transition from preparing
  (`test_only_one_cross_process_transition_can_prepare_at_a_time`). The
  implementation uses POSIX advisory `flock`, intended to serialize processes
  on a compliant local filesystem, but this test is not multi-process
  evidence. This is not distributed consensus, multi-writer coordination
  across arbitrary stores, or a general recovery protocol.
  [ADR-0084](../../technical/adr/ADR-0084-single-writer-or-explicit-coordination-for-shared-persistent-state.md)
  still defines the broader architectural requirement.
- **Crash consistency is not generally demonstrated.** A process-termination
  test shows that a process stopped after PREPARING reopens with the prior cut
  and `RECOVERY_REQUIRED` (`test_process_termination_after_preparing_reopens_prior_cut_as_recovery_required`). This targeted result is not a power-loss guarantee, exhaustive crash-point analysis, or general multi-process recovery proof.
- **Completeness of the roster rests on the genesis declaration.**
- **Presence ownership is explicit and durable.** Each active presence has
  exactly one registered owner link, persisted in the manifest and changed
  only through explicit lifecycle transitions. One owner may support multiple
  presences. This is not authority discovery; completeness is relative to the
  accepted genesis and explicit lifecycle inputs. The runtime still exposes an
  `active_presence_id` for its single-actor convenience path; do not mistake
  that for a one-owner/one-presence restriction.

## Time and identity

The runtime advances one clock, the causal tick, by exactly one per committed
transition. It reads no host time. Record and commit identifiers are derived
from the World identifier, the tick and the transition identifier supplied by
the caller.

## What supports this description

| Claim | Support |
|---|---|
| Genesis owner-link closure; order of publication; roster and presence changes; contract required for new owners; validation of owner bytes before acceptance; restore and explicit recovery; refusal when restoration cannot be confirmed | Code and tests in `world:tests/test_durable_runtime.py` at Biopeia World `a8d07fd791da76365aa74080eef1e82b11a599fd` |
| An end-to-end tick with real owners from the other repositories | `world:tests/integration`, run by that repository's integration job in CI at pinned revisions |
| A roster error before the transition opens leaves the runtime usable; a failure after the callback can leave an unreferenced owner checkpoint | Code and tests in `world:tests/test_durable_runtime.py` at Biopeia World `a8d07fd791da76365aa74080eef1e82b11a599fd`; this does not imply automatic cleanup |
| The limits listed above | Code and its documentation; they are statements of what is not provided, not results |

The test suite includes process termination after PREPARING, recovery-publication retry, and thread-level exclusion of concurrent preparation. The implementation's advisory file lock is intended for process-level serialization on supported local filesystems, but the cited concurrency test does not exercise separate processes. These tests do not prove power-loss durability, exhaustive crash consistency, or general distributed coordination.

## Open questions

- What should enforce the single logical writer, if anything in World should.
- Whether unreferenced owner checkpoints and journal snapshots left by failed
  transitions are to be cleaned, and by whom.
- What would count as evidence of crash consistency for this protocol.
