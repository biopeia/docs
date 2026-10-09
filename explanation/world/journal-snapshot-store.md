# The journal snapshot store

Reviewed against `world` at commit `cb4bd6b0506b554bf4187b36c23095a7521c4504`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, or neither.

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

The file is named after the tick and the SHA-256 of its own bytes, and it is
never modified. Writing goes through a temporary file that is flushed to disk
and then linked into place in a way that cannot replace an existing file; the
directory is flushed afterwards. If a file of that name is already there, the
store accepts it only if its bytes are identical, and otherwise refuses.

The reference returned
(`world:src/world/durable_runtime.py::DurableJournalSnapshotStore.write`)
names the journal as owner, the World as the identity, the tick in the
checkpoint identifier, a schema version, the path of the file as locator, and
the SHA-256 of the file.

## Two different fingerprints

A committed manifest ends up carrying two hashes that concern the journal,
and they are not the same thing:

- the **file hash** in the journal's checkpoint reference, computed over the
  bytes of the snapshot file;
- the **prefix digest** in the manifest's journal boundary, computed by the
  journal itself by chaining each record onto the previous digest.

The first establishes that the file has not changed. The second establishes
which records there are and in what order. A run of the module confirms they differ for the same
journal. Reading a snapshot back checks the first; the durable runtime checks
the second when it validates a cut.

## Reading and verifying

Verifying a reference checks three things: that it names the journal as owner,
that it carries the journal schema, and that the file at its locator exists
and hashes to the recorded value. Reading verifies first, then rebuilds a
journal from the file, which passes every record through the journal's own
validation and recomputes its digests.

## What it does not do

Each of these is read from the code and was confirmed by running the module
at that revision; none has a test of its own.

- **It does not check which World a snapshot belongs to.** Verification does
  not look at the identity in the reference, and a store created for one World
  reads a snapshot written for another. The check that a cut references the
  journal of its own World is made by the durable runtime when it restores,
  and the check that every record belongs to the manifest's World is made when
  a cut is validated.
- **It keeps every snapshot.** Nothing in the store removes a file. Because
  each file is a full prefix, the size of the newest file grows with the
  number of records, and the total kept grows faster than that. In the run,
  five ticks left six files of 3, 199, 396, 593, 790 and 987 bytes.
- **Its locator is a filesystem path as given.** A reference stops resolving
  if the directory is moved, and means nothing on another host.
- **It decides nothing about commit.** Writing a snapshot does not commit a
  tick. A snapshot written for a transition that later fails stays on disk,
  referenced by no committed manifest.

## Time, identity and persistence

The store carries the causal tick in file names and identifiers and reads no
host clock. What it writes survives the process; that is its purpose.
Durability under power loss was not examined: the code flushes files and
directories, and no test or run here checks what survives a crash.

## What supports this description

| Claim | Support |
|---|---|
| Snapshot content, naming, immutable publication, the shape of the reference, verification and reading | Code |
| A committed tick publishes a journal snapshot before the manifest is complete | Code and `test_durable_tick_publishes_journal_and_owner_checkpoint_before_complete_manifest` in `world:tests/test_durable_runtime.py` |
| File hash and prefix digest differ; a store for another World reads the snapshot; all snapshots are kept and grow | Code, and one ad hoc run of the module at that revision |

No test in the repository addresses the store alone; it is exercised through
the durable runtime's tests.

## Open questions

- Whether old snapshots are meant to be retained as history or may be removed
  once a later cut is committed. The decision on the journal's role
  ([ADR-0107](../../technical/adr/ADR-0107-journal-role.md)) treats the
  journal as causal and evidentiary history, which bears on the answer.
- Whether the World check belongs in the store's own verification.
- The cost of writing the full prefix on every tick as the journal grows has
  not been measured.
