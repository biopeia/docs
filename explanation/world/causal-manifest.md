# The World causal manifest

Reviewed against `world` at commit `cb4bd6b0506b554bf4187b36c23095a7521c4504`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, or neither.

## What it is

The [causal journal](causal-journal.md) remembers *that* ticks were committed
and in what order. It says nothing about the state the participants were in
when a tick committed. The causal manifest is the piece that ties the two
together: one small durable record, owned by World, that names a causal cut.

A cut is the answer to "what, exactly, was true of this World at tick *n*?".
The manifest does not contain that state. It contains *references* to it: for
each participating owner, an opaque pointer to that owner's checkpoint with
its hash, plus the point the journal had reached. World can therefore say
which states belong together without being able to read any of them.

That separation is the design intent recorded in
[ADR-0106](../../technical/adr/ADR-0106-hybrid-multi-owner-persistence.md):
each semantic owner defines its own checkpoint, and World owns the coherent
cut across them. The manifest is where the cut is written down.

## What the manifest records

One manifest (`world:src/world/manifest.py::WorldCausalManifest`) describes
either a committed cut or a committed cut with a transition pending on top of
it. It carries:

- the World identifier and the causal tick of the cut;
- the active presences at that cut;
- one checkpoint reference per participant, each naming an owner, the
  identity of the owner's subject, a checkpoint identifier, a schema version,
  a locator and a SHA-256;
- the journal boundary: the position of the last persisted record and the
  journal's prefix digest at that position;
- the identifier of the commit;
- two rosters of participants, as pairs of owner and identity: owners
  registered with the World, and participants of this step only;
- a status, and, when a transition is pending, its identifier, its tick, the
  rosters proposed for it and, after a failure, a description of the failure.

The reference to the journal itself is recognisable by its owner name and is
not counted as a participant.

## What a manifest must satisfy to exist

A manifest that breaks any of these cannot be constructed. They are read from
the code; the tests named cover some of them.

- The journal boundary is inclusive: an empty journal has no last position and
  an empty digest; a non-empty one has a position and a SHA-256
  (`test_manifest_requires_inclusive_durable_journal_boundary`). This is the
  meaning fixed by
  [ADR-0086](../../technical/adr/ADR-0086-capture-manifest-last-sequence-semantics.md).
- No two references name the same owner and identity
  (`test_manifest_rejects_duplicate_owner_identity_reference`), and no
  presence appears twice
  (`test_manifest_rejects_duplicate_active_presence_ids`).
- The set of non-journal references is exactly the union of the two rosters.
  A participant without a reference, or a reference without a participant, is
  rejected.
- A participant cannot be both a registered owner and a step-only
  participant.
- A committed manifest identifies its commit and carries no pending details.
  A pending one names a transition for exactly the next tick.

## The three states

The status is the centre of the mechanism. It is persisted with the manifest,
so it survives the process.

```text
COMMITTED ──begin──▶ PREPARING ──commit──▶ COMMITTED (next tick)
                         │
                 failure │ or found at start-up
                         ▼
                 RECOVERY_REQUIRED ──recovery──▶ COMMITTED (same tick as before)
```

**Committed.** The cut is complete. Ordinary execution may begin the next
transition.

**Preparing.** A transition for the next tick has been opened. While it is
open the manifest still describes the *previous* cut, with its tick and its
references unchanged, and additionally records what is being attempted. No
second transition can be opened: beginning one requires the status to be
committed (`test_only_one_cross_process_transition_can_prepare_at_a_time`).

**Recovery required.** Something went wrong between opening a transition and
committing it. Ordinary execution is refused until an explicit recovery
(`test_durable_pending_transition_blocks_ordinary_execution`). This is the
behaviour required by
[ADR-0093](../../technical/adr/ADR-0093-material-failure-before-commit-requires-explicit-recovery.md):
a restart alone is not recovery, and execution does not resume on a later
tick by itself.

## What commits a cut

Committing replaces the pending manifest with the manifest of the next cut.
The store accepts it only if all of the following hold, and otherwise leaves
the file as it was:

- a transition is actually pending;
- the new manifest is for the same World and for exactly the pending tick;
- its commit identifier is the identifier of the pending transition;
- it references the state of at least one owner besides the journal
  (`test_manifest_store_rejects_journal_only_initial_cut_and_commit`);
- its rosters and its presences are the ones proposed when the transition was
  opened (`test_manifest_store_rejects_owner_membership_change_on_commit`);
- a verifier supplied by the caller, given the references, answers that the
  checkpoints they point to are verified
  (`test_successful_causal_cut_publication_verifies_dependency_closure`).

The last condition is where the separation of authority shows. The manifest
store cannot judge a checkpoint; it asks. What makes a checkpoint acceptable
is decided outside this component.

When the verifier refuses, the store raises and the manifest stays in the
preparing state. Moving it to recovery required is a separate step: the
caller records the failure, or the next check for ordinary activity finds the
open transition and converts it
(`test_unverified_checkpoint_dependency_leaves_durable_recovery_required`).

## What recovery does, and does not do

Completing a recovery writes back the manifest of the cut that was committed
before the failed transition, with the same tick and the same references, and
clears the pending details.

Before doing so it writes a receipt: a small immutable file naming the World,
the transition, the tick restored, and the hashes of the pending manifest and
of the manifest being restored. The receipt is written first so that, if the
process stops between the two writes, a retry can find it and finish.

Recovery in this component restores the *record*, not the state. The code's
own description says the runtime calls it only after every owner has restored
its checkpoint through its own recovery contract. Whether the owners were in
fact restored is not something the manifest store checks.

## How it is stored

The manifest is one JSON file in canonical form. Each change writes a
temporary file, flushes it to disk, replaces the manifest file in one step and
flushes the directory. The very first manifest is published in a way that
refuses to overwrite an existing one
(`test_initialize_is_atomic_no_overwrite_for_competing_initializers`).
Changes take an advisory lock on a companion file. Reading takes no lock.

## What it does not guarantee

- **It is not a transaction over the owners' states.** The manifest names
  checkpoints; it does not write them, and it cannot make several owners'
  writes succeed or fail together.
- **The lock protects each change, not a whole transition.** The lock is
  released between opening a transition and committing it. A second process
  that checks for ordinary activity in that interval finds the open
  transition, treats it as interrupted, and marks recovery required; the
  first process's commit then fails. One logical writer is assumed, as
  [ADR-0084](../../technical/adr/ADR-0084-single-writer-or-explicit-coordination-for-shared-persistent-state.md)
  requires of shared persistent state, and is not enforced here.
- **The lock is advisory and local.** It relies on POSIX file locking and says
  nothing about other hosts or about filesystems that do not honour it.
- **It is not a security boundary.** The code says so of its own mutation
  methods: they are internal to the durable runtime and do not stop trusted
  code in the same process, or anything with access to the files.
- **Durability under power loss was not examined.** The code flushes files and
  directories; no test or run here checks what survives a crash.

## Time and identity

The manifest carries the causal tick and no host time. Its commit identifier
is the identifier of the transition that produced the cut. The World
identifier is carried explicitly in the manifest and in every receipt, in
line with
[ADR-0080](../../technical/adr/ADR-0080-world-identity-is-authoritative-not-a-presentation-label.md).

## What supports this description

| Claim | Support |
|---|---|
| Journal boundary, uniqueness of references and presences, single open transition, refusal of ordinary execution while pending, commit conditions on owner state, roster and verifier, durable failure detail, no-overwrite initialisation | Code and tests in `world:tests/test_manifest.py` |
| Roster must equal the set of references; pending manifest keeps the previous cut; recovery writes a receipt and restores the previous tick | Code, and one ad hoc run of the module at that revision |
| A refused verifier leaves the manifest preparing until the next activity check | Code and `test_unverified_checkpoint_dependency_leaves_durable_recovery_required` |
| An activity check by a second actor during an open transition marks recovery required and makes the original commit fail | Code, and the same ad hoc run; no test is kept for it |
| What the manifest is for, and what recovery must mean | Accepted decisions ADR-0106, ADR-0093, ADR-0084; statements of intent, not test results |

The durable runtime that drives this store, and its own tests, were not
reviewed for this document. No persisted manifest from a real run, no crash
test and no experiment was examined.

## Correspondence with the decision on persistence

ADR-0106 lists what a World causal manifest identifies: World identity,
causal time, the identities of the participating authorities, exact
checkpoint references, the journal boundary, dependency hashes, and commit or
recovery status. Each of those has a field in this manifest. That is a
correspondence of content. It is not a finding that the implementation
conforms to the decision: the conditions under which a cut may be called
complete depend on the durable runtime and on the owners, which lie outside
this component.

## Open questions

- Whether the single-writer assumption should be enforced by the store, for
  instance by holding ownership of a transition, or stays an obligation of the
  caller.
- What should happen to a transition left preparing by a refused verifier if
  the caller does not record the failure.
- The receipts accumulate in a directory and nothing reads them back in this
  component; their intended consumer is not recorded.
