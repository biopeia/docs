# The durable World runtime

Reviewed against `world` at commit `d66ac6197c8ea8489dc4f2689641ff0a88b6482a` (main on
2026-10-16); first written against `95f5064c`. Everything below describes the
later revision. Statements are marked by what supports them: the code, the
tests, or an accepted decision.

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

Initialisation appends one record to the journal, of type
`world.causal_cut.committed`, naming the genesis commit, the participants and
their checkpoint references. It writes that journal as a snapshot, verifies
every reference, and publishes the manifest of tick zero in a way that cannot
overwrite an existing World. The journal of a new World is therefore not
empty: in an ad hoc run the manifest of tick zero placed the journal boundary
at position 0, with that one record.

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
   owners and presences and name participants of this step only. A change to
   the presence roster must come with a presence lifecycle transition
   (`world:src/world/durable_runtime.py::PresenceLifecycleTransition`): a
   declaration that one named presence is being registered or terminated,
   with a non-empty account of what triggered it. A tick changes at most that
   one presence. Inconsistent requests are rejected here, before anything is
   written, and leave the runtime usable.
4. **Open the transition durably.** The manifest is rewritten as preparing,
   still describing the previous cut, with the proposed rosters attached.
5. **Ask the owners to save.** A callback supplied by the caller persists the
   owners' new state and returns one reference per participant. It may also
   return owner-authored opaque causal records associated with the transition.
6. **Check what came back.** The references must name exactly the proposed
   participants. For each, World reads the bytes at the locator itself,
   compares their hash with the reference, and asks that owner's contract
   whether the checkpoint is valid. If an owner declares dependencies on other
   owner checkpoints, World verifies that every declared dependency reference
   exists in the committed cut or its ancestors and that dependencies are
   verified before dependents (`tests/test_checkpoint_dependencies.py`). Owner
   causal records must be structurally valid, uniquely identified and bound to
   participating owners.
7. **Extend the journal with delta records.** Under schema `event-journal-v3`,
   World appends only the new delta records to `world-causal-journal-v3.jsonl`
   in this order: the tick record; a causal-cut record naming the commit, the
   participants and every owner checkpoint reference of this cut; when the
   tick changes the presence roster, a presence lifecycle record; and any
   owner causal records. Writes are serialized using `fcntl.flock` and prefix
   verification is cached.
8. **Publish the cut.** The manifest of the new cut is committed through the
   manifest store, which re-verifies the references. Only then do the
   runtime's in-memory journal and manifest advance. Once committed, callers may
   obtain a verified `CommittedWorldCut` receipt via `world.committed_cut_for()`.

If anything from step 5 onward fails, the runtime latches, tries to mark the
durable manifest as requiring recovery with a description of the failure, and
re-raises. The tick counter does not advance.

Covered by tests: the order of publication
(`test_durable_tick_publishes_journal_and_owner_checkpoint_before_complete_manifest`),
roster changes only through an explicit tick
(`test_world_owner_registry_changes_only_through_explicit_lifecycle_tick`,
`test_lifecycle_registration_and_step_participants_are_explicit_and_exact`,
`test_presence_roster_is_published_only_through_world_lifecycle_tick`), a
presence change refused without a lifecycle transition
(`test_rejected_or_failed_presence_lifecycle_does_not_publish_next_tick`), a new
owner needing a contract
(`test_new_owner_cannot_register_without_owner_checkpoint_contract`), and a
failed registration keeping the previous cut
(`test_failed_registration_keeps_prior_cut_and_pending_roster_for_recovery`).

## What the journal keeps for each cut

The manifest names only the current cut. Since the journal schema named
`event-journal-v2`, the journal also keeps, for every committed tick from
zero, one causal-cut record with the commit identifier, the participants and
the descriptor of each owner checkpoint reference: owner, identity,
checkpoint identifier, schema version, locator and hash. World copies these
descriptors without opening the checkpoints.

When a cut is validated, at restore and at recovery, the journal must hold
exactly one such record per tick, each well formed, and the latest must agree
with the manifest in commit identifier, participants and references. Read
from `world:src/world/durable_runtime.py::DurableWorldRuntime._validate_cut`;
that the references of an earlier cut remain readable from the journal after
later ticks was seen in an ad hoc run with a step-only participant.

Two consequences follow:

- A snapshot written under the earlier schema name is not accepted: the
  store's verification compares the schema name of the reference. Read from
  the code; no test covers it and the repository provides no conversion.
- The journal's prefix digest now depends on where the owners' checkpoints
  are stored, because the locator is part of each descriptor. The same World
  driven with the same inputs under two different directories gave equal
  owner checkpoint hashes and different prefix digests (ad hoc run). World's own
  integration fixtures say so and compare committed cuts without the digest.

## A World with no presence

A lifecycle transition may terminate the presence the runtime is acting as.
The tick record of a tick that carries a lifecycle transition, of either
type, is attributed to World, not to the presence,
and a `world.presence.lifecycle.committed` record keeps the transition, the
affected presence and owner, the trigger as declared, the participants and
the affected owner's checkpoint reference. After the last presence is
terminated the World is still committed, with an empty presence roster, and
the runtime acts as no presence.

Such a World refuses an ordinary tick. It accepts a lifecycle transition that
registers a presence, and can be restored without naming one. A lifecycle
transition identifier already committed in the journal cannot be used again.
Covered by
`test_last_presence_can_terminate_world_remains_active_and_later_registers`.
The repository states the limit: "This implementation does not support
ordinary causal cuts with no owner participants".

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
  to save, and may have advanced them, before the failure. In an ad hoc
  run, a tick that failed its roster check after the callback left the
  owner's new checkpoint file on disk, referenced by nothing, and wrote no
  journal snapshot; the file was still there after recovery.

Recovery (`DurableWorldRuntime.recover_previous_cut`) is explicit and is
delegated: World verifies the previous cut's references, calls a restorer
supplied by the caller to put the owners back, asks each owner's contract to
confirm the restoration, verifies the references again, and only then has the
manifest store write an immutable rollback-operation receipt and republish
the previous cut. This receipt records a schema name, the World, the
transition, the tick that was pending, the tick restored, a hash of the
proposed transition and a hash of the recovered manifest; it is distinct from
checkpoint validation and is not an owner attestation. Its use when a
transition identifier is offered again is described in
[the causal manifest document](causal-manifest.md). If the restoration
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
  evidence. A second test does use a separate process: it reads the
  preparing manifest while the writer is paused inside its owner callback,
  and the writer then commits
  (`test_second_process_can_observe_preparing_manifest_while_writer_callback_is_open`).
  That shows a reader sees the open transition; it exercises no second
  writer. This is not distributed consensus, multi-writer coordination
  across arbitrary stores, or a general recovery protocol.
  [ADR-0084](../../technical/adr/ADR-0084-single-writer-or-explicit-coordination-for-shared-persistent-state.md)
  still defines the broader architectural requirement.
- **Crash consistency is not generally demonstrated.** Subprocess tests stop
  a writer at chosen points and check that the prior cut stays the committed
  one and that the open transition needs explicit recovery: after PREPARING
  is published
  (`test_process_termination_after_preparing_reopens_prior_cut_as_recovery_required`);
  while the owner callback has written part of a checkpoint
  (`test_process_termination_during_partial_owner_checkpoint_write_requires_recovery`);
  while the manifest's temporary file is partly written
  (`test_process_termination_during_partial_manifest_write_keeps_previous_cut`);
  and, since world `9f65707` made the journal an append-only file of
  fixed-size records, after a candidate record has been appended and flushed
  but before the manifest references it
  (`test_process_termination_after_uncommitted_journal_append_recovers_prior_prefix`).
  One more test injects a flush error on the journal append
  (`test_journal_append_fsync_failure_keeps_previous_committed_prefix`). In
  both, the committed prefix still replays to the previous records, the manifest
  requires recovery, and `recover_previous_cut` returns the runtime to the
  previous committed tick; the flush-error test also checks that the journal
  file is truncated back to its committed size.
  (This list of journal cases was updated on 2026-10-16 against `world`
  `d66ac6197c8ea8489dc4f2689641ff0a88b6482a`, which is now also this unit's
  recorded basis; both tests already existed at the earlier basis `1f35e92`. The three temporary-file publication tests
  this document described earlier were removed by `9f65707`.)
  These are process terminations on the filesystem the tests ran on. The
  repository says this evidence "is not power-loss fault injection or a
  general crash-consistency proof" (`world:MIGRATION.md`), and it is not an
  exhaustive crash-point analysis, a test of a real flush error, or a
  multi-process recovery proof.
- **Completeness of the roster rests on the genesis declaration.**
- **Presence ownership is explicit and durable.** Each active presence has
  exactly one registered owner link, persisted in the manifest and changed
  only through explicit lifecycle transitions. One owner may support multiple
  presences. This is not authority discovery; completeness is relative to the
  accepted genesis and explicit lifecycle inputs. One runtime object acts as
  at most one presence, or as none when the World has none; do not mistake
  that for a one-owner/one-presence restriction.

## Time and identity

The runtime advances one clock, the causal tick, by exactly one per committed
transition. It reads no host time. Record and commit identifiers are derived
from the World identifier, the tick and the transition identifier supplied by
the caller.

## What supports this description

| Claim | Support |
|---|---|
| Genesis owner-link closure; order of publication; roster and presence changes, including termination of the last presence and re-entry; contract required for new owners; validation of owner bytes before acceptance; restore and explicit recovery; refusal when restoration cannot be confirmed | Code and tests in `world:tests/test_durable_runtime.py` at Biopeia World `95f5064c6b06bd66bb58a72110b066afe4ca70b0`. In an ad hoc run of the repository's default suite at that revision, started from outside the checkout, 88 of 91 cases passed, among them every test of this file; the three that failed are the checks of the CI workflow file in `world:tests/test_integration_workflow_gate.py`, which passed when run from the root of the checkout |
| One causal-cut record per tick, checked against the manifest when a cut is validated | Code. The record's presence in the journal is asserted by `test_durable_tick_publishes_journal_and_owner_checkpoint_before_complete_manifest`; no test was found that offers a journal lacking one, or holding a malformed one, and checks the refusal |
| The journal of tick zero holds one record; earlier cuts' references stay in the journal; the prefix digest differs between storage directories | Ad hoc runs at Biopeia World `95f5064c6b06bd66bb58a72110b066afe4ca70b0` |
| An end-to-end tick with real owners from the other repositories | `world:tests/integration`, run by that repository's integration job in CI at pinned revisions |
| A roster error before the transition opens leaves the runtime usable; a failure after the callback can leave an unreferenced owner checkpoint | Code and tests in `world:tests/test_durable_runtime.py` at Biopeia World `95f5064c6b06bd66bb58a72110b066afe4ca70b0`, and an ad hoc run at that revision; this does not imply automatic cleanup |
| The limits listed above | Code and its documentation; they are statements of what is not provided, not results |

The test suite includes process termination at the points listed above, a read of the open transition from a second process, recovery-publication retry, and thread-level exclusion of concurrent preparation. The implementation's advisory file lock is intended for process-level serialization on supported local filesystems, but no test exercises two writing processes. These tests do not prove power-loss durability, exhaustive crash consistency, or general distributed coordination.

## Open questions

- What should enforce the single logical writer, if anything in World should.
- Whether unreferenced owner checkpoints and journal snapshots left by failed
  transitions are to be cleaned, and by whom.
- What would count as evidence of crash consistency for this protocol.
