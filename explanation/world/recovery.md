# World recovery

Reviewed against `world` at commit `cb4bd6b0506b554bf4187b36c23095a7521c4504`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, or neither.

## What this is about

A causal tick can fail part-way: after World has said it is starting, and
before it has said it is done. This document follows what happens from that
moment until the World is allowed to run again. The mechanism spans the
[durable runtime](durable-runtime.md), the
[causal manifest](causal-manifest.md) and the owners; no single component
contains it.

The governing decision is
[ADR-0093](../../technical/adr/ADR-0093-material-failure-before-commit-requires-explicit-recovery.md):
a failure between the start of a transition and its commit puts the runtime
in a durable recovery-required state; ordinary execution does not resume by
itself on a later tick; an explicit, verifiable recovery must come first; and
a restart alone is not recovery.

## Three ways a World comes to need recovery

1. **A tick fails after it opened.** The runtime latches in memory and tries
   to write the failure into the manifest. Covered by
   `test_failed_registration_keeps_prior_cut_and_pending_roster_for_recovery`
   and `test_unverifiable_owner_checkpoint_keeps_durable_manifest_pending`.
2. **A transition is found open.** Any check for ordinary activity that finds
   the manifest still preparing treats the transition as interrupted and
   marks it. This is what turns a process that died mid-tick into a World
   that requires recovery when it is next started. Covered at the level of
   the store by `test_durable_pending_transition_blocks_ordinary_execution`.
3. **The manifest changed behind the runtime's back.** At the start of each
   tick the runtime compares the durable manifest with its own copy and
   latches if they differ. Read from the code; no test was found for it.

In the first two cases the need is durable: it is written in the manifest and
survives the process. In the third it is a latch in one runtime's memory.

## What is refused while recovery is required

Every further tick, and restoring a runtime from the stored cut. Covered by
the tests named above. The manifest keeps describing the last committed cut
throughout, together with the identifier and tick of the transition that
failed, the roster it proposed, and a description of the failure
(`test_failure_detail_is_durable_and_does_not_clear_recovery_state` in
`world:tests/test_manifest.py`).

## The recovery itself

Recovery is a deliberate call
(`world:src/world/durable_runtime.py::DurableWorldRuntime.recover_previous_cut`).
It goes back; it never goes forward. The failed transition is not retried or
completed. In order:

1. Confirm the World is in fact waiting for recovery, and that the caller is
   asking about the right World and a presence that belongs to it.
2. Read the journal snapshot of the previous cut and check that it agrees
   with the manifest.
3. Verify the previous cut's references: the files are there, their hashes
   match, and each owner's contract accepts its checkpoint.
4. Call the **restorer**, supplied by the caller, with the owners'
   references. This is the only step in which any owner's state changes, and
   World does not perform it.
5. Ask each owner's contract to confirm the restoration, and verify the
   references once more.
6. Have the manifest store write an immutable receipt and republish the
   previous cut as committed.

If step 4 fails, or step 5 cannot confirm it, the World stays waiting for
recovery (`test_failed_owner_recovery_keeps_recovery_required_manifest`). A
successful recovery is covered by
`test_explicit_recovery_restores_prior_cut_through_owner_and_records_receipt`,
and a retry after an interruption between the receipt and the manifest by
`test_retry_after_recovery_publication_interruption_fsyncs_existing_receipt_directory`.

## Starting again from a committed cut

Restarting a World that was not in the middle of anything
(`DurableWorldRuntime.restore`) is the same pattern without the receipt:
verify, let the owners restore, confirm, verify again. A cut that references
no owner state is refused
(`test_restore_and_recovery_reject_publicly_published_cuts_without_owner_state`).

## What is left behind

Recovery restores the record and asks the owners to restore themselves. It
removes nothing. After a failed tick and its recovery, the following may
remain, none of it referenced by any committed cut:

- owner checkpoints written by the callback for the tick that failed;
- the journal snapshot written for that tick, if the failure came later;
- the receipt of the recovery, which is kept deliberately.

The first was observed in an ad hoc run recorded in
[the durable runtime document](durable-runtime.md). Nothing in `world`
removes such files.

## What recovery does not establish

- **That the owners are back where they were.** World checks that the
  previous checkpoints are intact and that each owner's contract answers yes.
  It cannot see the owners' live state.
- **Crash consistency.** The code calls this path "not crash-consistency
  proof or a multi-process recovery protocol". No test stops a process in the
  middle of a write.
- **Safety of a partial restoration.** The code requires the restorer to be
  "safe to retry"; that is an obligation on the caller, not something
  checked.
- **Anything for the in-memory coordinator.** The simpler
  [in-memory runtime](in-memory-runtime.md) also latches on failure, but has
  no recovery call at all; its own documentation says it "does not by itself
  satisfy the TARGET post-failure contract".

## A question the decision left open

ADR-0093 reserves whether the failure of one participant requires the whole
World, or only that participant, to enter recovery. In this implementation
the question does not arise in that form: a World runtime acts as one
presence, and any failure in a tick puts the whole World in recovery.

## What supports this description

| Claim | Support |
|---|---|
| Failure and interruption lead to a durable recovery-required state; ticks and restore are refused; explicit recovery restores the previous cut and writes a receipt; a failed restoration keeps the state | Code and tests in `world:tests/test_durable_runtime.py` and `world:tests/test_manifest.py` |
| A manifest changed outside the runtime latches it at the next tick | Code only |
| Residue left by a failed tick | Code, and one ad hoc run |
| What recovery must mean | Accepted decision ADR-0093; a statement of intent |
