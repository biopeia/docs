# The journal snapshot store

Reviewed against `world` at commit `07a4db8f2fe6a0dde1a01a63ab27c158e71cf3f5`
(main on 2026-10-16); first written against `95f5064c`. Statements are marked
by what supports them: the code, the tests, or an accepted decision.

> Revision delta, 2026-10-17. The review revision moved from `d66ac61` to `07a4db8`. Between the two, World changed `src/world/durable_runtime.py` once (`5d4abca`, #186: journal initialisation may be retried), `src/world/causal_cycle.py` (#179, #180, #182) and `src/world/m1_process.py` (#190), and added tests (#185, #186, #188). The first-write change is described under "The first write"; nothing else in this document changed.

## What it is

The [causal journal](causal-journal.md) lives in memory. The
[causal manifest](causal-manifest.md) is durable, but holds only a position
and a digest of the journal, not the journal records themselves. Something
has to put the records on disk in a form the manifest can point to. The journal
snapshot store does that, and nothing else.

From World's point of view, the journal participates in every causal cut: it
has an explicit checkpoint reference in the manifest under the reserved owner
name `world-journal`.

## What it writes: The v3 append-only journal

In schema `event-journal-v3`
(`world:src/world/durable_runtime.py::DurableJournalSnapshotStore`), World does
not rewrite full snapshot files on every tick. Instead, it maintains a single
append-only file named `world-causal-journal-v3.jsonl` within the store
directory.

Each committed cut appends only the delta records belonging to that tick,
formatted as single-line JSON with an explicit newline (`\n`) terminator.
Writes are serialized using POSIX advisory file locking (`fcntl.flock`).

### The first write

The first write creates the file through a temporary file and a hard link, so
a competing initialiser fails with "World journal was concurrently
initialized". Since `5d4abca` (#186), an existing journal found at
initialisation is reused only if its bytes equal the genesis bytes being
proposed. That case arises when a process stopped after the first journal and
before the tick-zero manifest. Any other existing file still raises "World
journal already exists without its committed reference"
(`test_initial_journal_rejects_existing_bytes_that_are_not_the_exact_candidate`).

A journal checkpoint reference carries:

- `owner`: `"world-journal"`
- `owner_identity`: The World ID string
- `checkpoint_id`: `journal-cut-{tick}-sequence-{sequence}-offset-{offset}`
- `schema_version`: `"event-journal-v3"`
- `locator`: Path to `world-causal-journal-v3.jsonl`
- `sha256`: The cumulative SHA-256 digest of the file prefix up to `offset`

To maintain bounded tick latency as history grows, `DurableJournalSnapshotStore`
caches the verified prefix signature (`_previous_prefix_is_cached`).
Consecutive ticks append deltas in $O(\Delta)$ time without rescanning prior
records.

## Two different fingerprints

A committed manifest carries two hashes concerning the journal:

- the **file hash** in the journal's checkpoint reference, computed over the
  exact bytes of the `world-causal-journal-v3.jsonl` file prefix up to
  `offset`;
- the **prefix digest** in the manifest's journal boundary, computed by the
  journal itself by hashing each record onto the previous record's digest.

The first establishes byte-level storage integrity on disk. The second
establishes the causal hash chain of the event stream. Both are verified
when a cut is restored.

## Reading, verifying and tail recovery

Verifying a reference checks that it names the journal as owner, carries
schema `event-journal-v3`, and that the file prefix up to `offset` hashes to
the recorded SHA-256 digest. Reading then parses the line-delimited JSON
records and rebuilds the `EventJournal`, re-verifying causal digests.

If a tick is interrupted before commit, `_discard_uncommitted_tail` truncates
any trailing uncommitted bytes beyond the committed offset under the manifest
writer lock, preventing partial or corrupt records from remaining in the
journal file during recovery.

## What supports this description

| Claim | Support |
|---|---|
| Single JSONL append-only architecture, offset locators, schema `event-journal-v3` | Code in `world:src/world/durable_runtime.py:235-645` |
| Prefix signature caching and bounded delta append | Code in `world:src/world/durable_runtime.py:250-420` |
| POSIX flock locking and tail discard during recovery | Code in `world:src/world/durable_runtime.py:540-560` and tests in `world:tests/test_durable_runtime.py` |
| Role of the journal as causal and evidentiary history | Accepted decision ADR-0107 |
