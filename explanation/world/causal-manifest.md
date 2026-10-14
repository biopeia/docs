# The World causal manifest

Reviewed against `world` at commit `e2be58700c870419a309ef3e2460b30b95c256be` (main on
2026-10-14); first written against `95f5064c`. Everything below describes the
later revision. Statements are marked by what supports them: the code, the
tests, or an accepted decision.

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
- exactly one registered owner link for each active presence, with stable
  owner identity;
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

## Presence-to-owner association

Schema v4 persists committed and pending presence-owner links alongside the
presence and owner rosters. The committed link set is validated against active
presences and registered owner identities; a pending transition carries its
proposed link set. Consequently this association is included in the cut and
is available to restoration/recovery. This proves persistence of the mapping,
not discovery of an authority omitted from the accepted genesis input or
reconstruction of every external owner state.

## What a manifest must satisfy to exist

A manifest that breaks any of these cannot be constructed. They are read from
the code; the tests named cover some of them.

- The journal boundary is inclusive: an empty journal has no last position and
  an empty digest; a non-empty one has a position and a SHA-256
  (`test_manifest_requires_inclusive_durable_journal_boundary`). This is the
  meaning fixed by
  [ADR-0086](../../technical/adr/ADR-0086-capture-manifest-last-sequence-semantics.md).
  The empty case can still be constructed, but the durable runtime no longer
  produces it: it writes a record into the journal at genesis, so every
  manifest it publishes has a position and a digest (see
  [the durable runtime document](durable-runtime.md)).
- No two references name the same owner and identity
  (`test_manifest_rejects_duplicate_owner_identity_reference`), and no
  presence appears twice
  (`test_manifest_rejects_duplicate_active_presence_ids`).
- Every active presence has exactly one link to a registered owner; committed
  and pending link sets are validated during manifest construction and
  lifecycle transition.
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

Before doing so it writes a receipt: a small immutable file under the schema
name `world-recovery-receipt-v2`, naming the World, the transition, the tick
that was pending, the tick restored, a hash of the proposed transition and a
hash of the manifest being restored. The hash of the proposed transition is
taken over the pending manifest without its status and without the failure
text, so the same proposal hashes the same however it failed. The file is
named after a hash of the World, the transition identifier and the pending
tick together. The receipt is written first so that, if the process stops
between the two writes, a retry can find it and finish.

The receipt is read back in one more place. When a transition is opened, the
store looks for a receipt under the same World, identifier and tick. If one
exists and the proposal now offered hashes differently, the transition is
refused and the manifest stays committed; an unreadable receipt, or one whose
identity fields do not match, is refused as well. So the identifier of a
transition that was recovered cannot be reused, at that tick, for a different
proposal (`test_recovered_transition_identity_cannot_be_reused_for_different_proposal`).
Two recovered transitions keep two receipts
(`test_recovery_receipts_keep_distinct_transition_identities`), and the same
identifier at a later tick gets its own
(`test_same_transition_id_on_later_tick_gets_a_distinct_recovery_receipt`).
These three tests are in `world:tests/test_durable_runtime.py`. That the same
identifier with the same proposal is accepted again is read from the code; no
test was found for it.

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
- **The lock protects individual state changes, not the whole transition.** A
  thread-based test shows a second concurrent transition-open attempt is
  refused while a transition is pending
  (`test_only_one_cross_process_transition_can_prepare_at_a_time`). The
  implementation uses POSIX advisory file locking intended to serialize
  processes on a compliant local filesystem, but this test does not exercise
  separate processes. The lock is not held across the owner callback and does
  not constitute a distributed coordinator. The broader single-logical-writer requirement remains as stated in
  [ADR-0084](../../technical/adr/ADR-0084-single-writer-or-explicit-coordination-for-shared-persistent-state.md).
- **The lock is advisory and local.** It relies on POSIX file locking and says
  nothing about other hosts or about filesystems that do not honour it.
- **It is not a security boundary.** The code says so of its own mutation
  methods: they are internal to the durable runtime and do not stop trusted
  code in the same process, or anything with access to the files.
- **Power-loss behavior remains unverified.** The process-termination tests
  establish only the boundaries they stop at. One of them stops a writer
  while the manifest's temporary file is partly written and finds the
  previous cut intact
  (`test_process_termination_during_partial_manifest_write_keeps_previous_cut`
  in `world:tests/test_durable_runtime.py`). None establishes what survives
  power loss.

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
| Manifest v4 persists committed/pending presence-owner links; pending state retains the previous cut; recovery writes a receipt before republishing; a thread-level test excludes concurrent transition preparation | Code and tests in `world:tests/test_manifest.py`, including `test_only_one_cross_process_transition_can_prepare_at_a_time`, at World `95f5064c6b06bd66bb58a72110b066afe4ca70b0` |
| Content and naming of the receipt; refusal to reuse a recovered transition identifier for another proposal | Code and the three tests named above, at World `95f5064c6b06bd66bb58a72110b066afe4ca70b0`; the receipt's fields were also read from a file written in an ad hoc run at that revision |
| A refused verifier leaves the manifest preparing until the next activity check | Code and `test_unverified_checkpoint_dependency_leaves_durable_recovery_required` |
| Retrying recovery publication after receipt creation reuses and syncs the existing receipt directory | `test_retry_after_recovery_publication_interruption_fsyncs_existing_receipt_directory` in `world:tests/test_durable_runtime.py` at World `95f5064c6b06bd66bb58a72110b066afe4ca70b0` |
| What the manifest is for, and what recovery must mean | Accepted decisions ADR-0106, ADR-0093, ADR-0084; statements of intent, not test results |

The durable runtime and its tests were reviewed at the pinned revision. No
persisted manifest from a real run or experiment was examined; targeted process
termination tests are not power-loss evidence.

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
- Receipts are immutable. They are read back when a recovery publication is
  retried and when a transition identifier is offered again at the same
  tick. Nothing lists them or removes them, and whether they are meant as a
  record for anyone else is not stated.
