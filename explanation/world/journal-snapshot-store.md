# The journal snapshot store

Reviewed against `world` at commit `95f5064c6b06bd66bb58a72110b066afe4ca70b0`.
Everything below describes that revision, except the size characterization,
which names its own. Statements are marked by what supports them: the code,
the tests, an ad hoc run made at that revision on 2026-10-11, or neither.

## What it is

The [causal journal](causal-journal.md) lives in memory. The
[causal manifest](causal-manifest.md) is durable, but holds only a position
and a digest of the journal, not the journal. Something has to put the
records themselves on disk, in a form the manifest can point to. The journal
snapshot store does that, and nothing else.

Each time it is asked, it writes the whole journal as it stands to one new
file and hands back a checkpoint reference to that file. From World's point of
view the journal thereby becomes one more participant in a causal cut: it has
a reference in the manifest like any owner's checkpoint, under the reserved
owner name `world-journal`.

## What it writes

A snapshot is the complete sequence of records, from the first to the
current last, as plain data in canonical JSON. It is a *prefix* snapshot, not
an increment: the file written at tick *n* contains every record up to *n*.
The first snapshot, written when the World is initialised, is not empty: it
holds the causal-cut record of tick zero (see
[the durable runtime document](durable-runtime.md)).

The file is named after the tick and the SHA-256 of its own bytes, and it is
never modified. Writing goes through a temporary file that is flushed to disk
and then linked into place in a way that cannot replace an existing file; the
directory is flushed afterwards. If a file of that name is already there, the
store accepts it only if its bytes are identical, and otherwise refuses.

The reference returned
(`world:src/world/durable_runtime.py::DurableJournalSnapshotStore.write`)
names the journal as owner, the World as the identity, the tick in the
checkpoint identifier, a schema version, the path of the file as locator, and
the SHA-256 of the file. The schema version is the name `event-journal-v2`.

## Two different fingerprints

A committed manifest ends up carrying two hashes that concern the journal,
and they are not the same thing:

- the **file hash** in the journal's checkpoint reference, computed over the
  bytes of the snapshot file;
- the **prefix digest** in the manifest's journal boundary, computed by the
  journal itself by chaining each record onto the previous digest.

The first establishes that the file has not changed. The second establishes
which records there are and in what order. An ad hoc run confirms they differ for the same
journal. Reading a snapshot back checks the first; the durable runtime checks
the second when it validates a cut.

## Reading and verifying

Verifying a reference checks three things: that it names the journal as owner,
that it carries the journal schema, and that the file at its locator exists
and hashes to the recorded value. A reference carrying the earlier schema
name, `event-journal-v1`, therefore does not verify. Read from the code; no
test covers it and the repository provides no conversion. Reading verifies first, then rebuilds a
journal from the file, which passes every record through the journal's own
validation and recomputes its digests.

## What it does not do

Each of these is read from the code and was confirmed by an ad hoc run at
that revision; none has a test of its own.

- **It does not check which World a snapshot belongs to.** Verification does
  not look at the identity in the reference, and a store created for one World
  reads a snapshot written for another. The check that a cut references the
  journal of its own World is made by the durable runtime when it restores,
  and the check that every record belongs to the manifest's World is made when
  a cut is validated.
- **It keeps every snapshot.** Nothing in the store removes a file. Because
  each file is a full prefix, the size of the newest file grows with the
  number of records, and the total kept grows faster than that. In the run,
  a World with one owner left six files after five ticks, of 636, 1472, 2308,
  3144, 3980 and 4816 bytes. Each tick now adds two records, the tick record
  and the causal-cut record, and the second carries the owner's reference
  with its locator, so these sizes depend on the length of the path the
  checkpoints were written under and on the number of participants.
- **Its locator is a filesystem path as given.** A reference stops resolving
  if the directory is moved, and means nothing on another host.
- **It decides nothing about commit.** Writing a snapshot does not commit a
  tick. A snapshot written for a transition that later fails stays on disk,
  referenced by no committed manifest.

## Time, identity and persistence

The store carries the causal tick in file names and identifiers and reads no
host clock. What it writes survives the process; that is its purpose.
Durability under power loss was not examined. The code flushes files and
directories. Tests stop the writing process at four points of a snapshot's
publication and find the previous cut still committed; after the file has
been linked into place the candidate is visible on the filesystem the test
ran on, which the repository notes "is not evidence that its directory entry
survives power loss".

## Follow-up size and write characterization

The description above is pinned to World `95f5064c6b06bd66bb58a72110b066afe4ca70b0`.
An earlier bounded local characterization was run against World
`cb6bfb7c9bccd16c2f85f0f24deba1a12bfc80c8`, before the journal carried a
causal-cut record per tick, using `EventJournal` and
`DurableJournalSnapshotStore.write` directly. It appended one synthetic record
per tick with a 32-character payload string and wrote each full prefix once to
a temporary local directory. The production store path (including file and
directory `fsync`) was used; the temporary files were removed after each run.

| Records/ticks | Newest prefix | Prefix files retained | Total retained bytes | Elapsed |
|---:|---:|---:|---:|---:|
| 10 | 2,145 B | 10 | 11,793 B | 0.202 s |
| 50 | 10,825 B | 50 | 275,533 B | 1.033 s |
| 100 | 21,678 B | 100 | 1,093,461 B | 1.976 s |
| 200 | 43,678 B | 200 | 4,372,261 B | 6.772 s |

This confirms the implementation-level quadratic retained-byte growth for
fixed-size records: each saved prefix contains earlier records, and no older
prefix is removed. The elapsed values are one local run, not a stable
performance estimate. The benchmark is synthetic and does not include the
full `DurableWorldRuntime`, representative record sizes or production
storage. It was not repeated at the revision reviewed here, where each tick
written through the durable runtime adds a second, larger record; the bytes
per tick in the table understate what that runtime now writes. No intended tick rate, run duration, retention horizon, filesystem,
or storage budget was supplied, so the measurements do not establish whether
the cost is unacceptable for Biopeia's intended workloads. The bounded method
and results are recorded in [World issue #32](https://github.com/biopeia/world/issues/32#issuecomment-6094690365).

This characterization does not authorize deleting prefixes. Any future
retention, compaction or incremental-storage design must preserve the committed
cut's recovery requirements and the journal's causal/evidentiary role in
[ADR-0107](../../technical/adr/ADR-0107-journal-role.md).

## What supports this description

| Claim | Support |
|---|---|
| Snapshot content, naming, immutable publication, the shape of the reference, verification and reading | Code |
| A committed tick publishes a journal snapshot before the manifest is complete; owner causal records survive later ticks and restore as part of the prefix | Code and `test_durable_tick_publishes_journal_and_owner_checkpoint_before_complete_manifest`, `test_owner_causal_record_survives_later_tick_and_restore` in `world:tests/test_durable_runtime.py` at World `95f5064c6b06bd66bb58a72110b066afe4ca70b0` |
| A candidate journal file interrupted while partly written, before it is flushed, before it is linked, or after it is linked, does not replace the previous cut | `test_process_termination_during_partial_journal_write_requires_recovery`, `test_process_termination_during_journal_publication_keeps_previous_cut` and `test_journal_directory_fsync_failure_requires_recovery_to_previous_cut` in the same file; process terminations and one injected exception on the filesystem the tests ran on |
| File hash and prefix digest differ; a store for another World reads the snapshot; all snapshots are kept and grow | Code and one ad hoc run at the reviewed revision; earlier fixed-size-prefix growth characterization at World `cb6bfb7c9bccd16c2f85f0f24deba1a12bfc80c8` |

No test in the repository calls the store alone; it is exercised through
the durable runtime's tests, which now include the interruptions of its
write path listed above.

## Open questions

- Whether old snapshots are meant to be retained as history or may be removed
  once a later cut is committed. The decision on the journal's role
  ([ADR-0107](../../technical/adr/ADR-0107-journal-role.md)) treats the
  journal as causal and evidentiary history, which bears on the answer.
- Whether the World check belongs in the store's own verification.
- The cost has only been measured with a synthetic direct-store benchmark.
  Whether it is operationally material for intended workloads remains open.
