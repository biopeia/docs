# The World causal journal

Reviewed against `world` at commit `a8d07fd791da76365aa74080eef1e82b11a599fd`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, or neither.

## What it is

When a World commits a causal tick, something has to remember that it
happened, in which order, and in a form that can later be compared with what
was persisted. The causal journal is that memory. It is an append-only list of
records, each describing one World-scoped causal event, together with a
running digest that changes whenever any earlier record changes.

It is deliberately narrow. The journal orders and fingerprints records. It
does not know what a record means, does not store anything on disk, and does
not decide whether a tick may commit. Those belong to other parts of World and
to the authorities that define each event.

This matters for how the journal may be read. It is evidence of what World
committed, in order. It is not the state of the Organism, the body or the
environment, and it is not, on its own, a recovery mechanism. The accepted
decision on its role says the same: the journal is causal and evidentiary
history that may take part in recovery, and is not the sole authority for
state ([ADR-0107](../../technical/adr/ADR-0107-journal-role.md)).

## What a record carries

A record (`world:src/world/journal.py::CausalRecord`) is an immutable envelope
with:

- an identifier, the identifier of the World it belongs to, and the causal
  tick at which it was committed;
- a record type, which the journal treats as an opaque string;
- optionally, the identifier of the actor;
- a payload restricted to JSON-compatible values;
- two separate lists of other record identifiers: causal parents and
  contributing records.

Creating a record fails if the record identifier, the World identifier or the
record type is empty, or if the tick is negative. The payload is copied and
frozen on creation: later changes to the object it was built from do not reach
the record, and the record's payload cannot be modified. Both behaviours are
covered by tests (`test_record_requires_identity_type_and_nonnegative_tick`,
`test_payload_is_deeply_read_only_and_json_compatible`).

The journal does not interpret the type, the payload, or the two lists of
related identifiers. In particular, the code does not check that a parent or
contributing identifier names a record that exists.

## How a record enters the journal

There are two ways in, and both follow the same rule: a record is encoded
before anything visible changes.

**Direct append.** `EventJournal.append` first serialises the record to a
canonical byte form (JSON with sorted keys, no insignificant whitespace, and
non-finite numbers rejected). Only if that succeeds are the record, its
indexes and its digest added. A payload holding a value such as NaN can
therefore be placed in a record but cannot be appended, and a failed append
leaves the journal exactly as it was. This is covered by
`test_encoding_failure_does_not_publish_record_or_partial_staged_batch`.

**Staged batch.** `EventJournal.stage` puts records in a holding list that is
not part of the journal. `commit_staged` encodes the whole batch first and
publishes its members only if every one encodes; `abort_staged` discards the
batch. The tests show that a batch whose second member fails to encode
publishes none of its members.

Two properties of staging follow from the code and are not exercised by any
test:

- after a failed `commit_staged`, the staged records remain staged; nothing
  clears them until a later commit or an explicit abort;
- staging lives in memory only. The module's own description calls it "an
  in-memory transaction aid, not a durable commit protocol".

At this revision neither World runtime uses staging. The durable runtime
appends the committed tick record and may append zero or more opaque
`world.owner_record.committed` records supplied by participating owners. The
in-memory runtime appends only its tick record.

## The running digest

After each append the journal stores one digest for the prefix that ends at
that record. It is the SHA-256 of the previous prefix digest (as text),
a zero byte, and the canonical bytes of the new record. The digest of the
empty journal is the empty string.

Because each digest folds in the one before it, the digest at position *n*
depends on every record up to *n* and on their order. The tests confirm two
consequences: rebuilding a journal from its snapshot reproduces every prefix
digest, and changing a field of the first record changes the digest of the
first prefix (`test_prefix_digests_survive_snapshot_restore_and_detect_changes`).

The digest lets a consumer check that two journals hold the same records in
the same order. It is a fingerprint, not a signature: nothing in it identifies
who produced the journal.

## What can be read from it

Reading never changes the journal. It offers the full sequence in commit
order, the records of one tick, the last *k* records, a record by position,
pages that continue after a given record identifier, and a plain-data snapshot
of all or part of the sequence. A snapshot can be turned back into a journal
with `EventJournal.from_snapshot`, which re-creates every record through the
same validation and recomputes the digests. The read paths are covered by
`test_indexed_queries_match_append_order` and
`test_pagination_and_unknown_cursor`.

There is no operation that removes or replaces a record; a test asserts that
the class has no `remove` or `update`.

## What the journal does not enforce

These are properties one might assume and that the journal, by itself, does
not guarantee at this revision. Each is read from the code; none has a test
asserting the absence of a check.

- **Unique record identifiers.** A second record with an existing identifier
  is appended. The identifier index keeps the position of the first one, so
  paging "after" that identifier resumes after the first occurrence.
- **One World per journal.** Records with different World identifiers can be
  appended to the same journal.
- **Tick order.** Ticks are not required to be increasing or contiguous.
- **Existence of related records.** As noted above.

In the durable runtime, two of these are checked elsewhere, when a persisted
cut is validated: every record must belong to the manifest's World, and the
ticks must be exactly 1 to the committed tick
(`world:src/world/durable_runtime.py::DurableWorldRuntime._validate_cut`).
Record identifiers are unique in practice because both runtimes derive them
from the World identifier and the tick. That is a property of the callers,
not of the journal.

## How World uses it

Both runtimes write a `world.causal_tick.committed` record per committed tick,
identified as `<world id>:tick:<n>`, with the active presence as actor. The
durable runtime additionally accepts zero or more opaque owner-authored
records (`world.owner_record.committed`) in that committed journal cut. Each
owner record is bound to its tick, owner identity and stable record ID; World
validates structural uniqueness and JSON shape but does not interpret the
payload. Tests cover records surviving later ticks and restore.

- The in-memory coordinator (`world:src/world/runtime.py::WorldRuntime.tick`)
  runs the transition, then appends the record. If either step raises, the
  runtime enters `RECOVERY_REQUIRED` and the tick counter does not advance.
- The durable coordinator (`world:src/world/durable_runtime.py`) builds a
  candidate copy of the journal, appends the record to the copy, writes the
  whole candidate as an immutable snapshot file, and records in the World
  manifest both the position of the last record and the prefix digest. The
  candidate replaces the live journal only after the manifest commit
  succeeds.

The position recorded in the manifest is the index of the last persisted
record, and is absent for an empty journal. That is the inclusive meaning
fixed by [ADR-0086](../../technical/adr/ADR-0086-capture-manifest-last-sequence-semantics.md).

The snapshot store and the manifest are separate components and are not
documented here.

## Time

The only clock in the journal is the causal tick carried by each record. The
journal reads no host clock and generates no random values; given the same
records in the same order it produces the same digests. This is read from the
code, which imports neither a clock nor a random source.

## What persists

Nothing, as far as the journal itself is concerned. It holds its records in
memory and loses them when the process ends. Continuity across a restart
exists only where a caller has saved a snapshot and rebuilds the journal from
it, as the durable coordinator does.

## What supports this description

| Claim | Support |
|---|---|
| Record validation, payload immutability, append order, batch behaviour, read paths, digest reproduction and sensitivity | Code and tests in `world:tests/test_journal.py` |
| Staged records survive a failed commit; duplicate identifiers, mixed Worlds and unordered ticks are accepted | Code, and one ad hoc run of the module at that revision; no test is kept for them |
| Neither runtime uses staging; durable runtime writes the tick record plus zero or more opaque owner records | Code and tests in `world:tests/test_durable_runtime.py` at World `a8d07fd791da76365aa74080eef1e82b11a599fd` |
| The journal's role as history and not sole state authority | Accepted decision ADR-0107; it is a statement of intent, not a test result |

No runtime trace, persisted journal or experiment was examined. Nothing here
says how the journal behaves under process failure, concurrent writers or
large record counts.

## Open questions

- Staging is implemented and tested but has no caller in this repository.
  Whether it is intended for a later multi-record tick or is a leftover of the
  source it was reconstructed from is not recorded.
- The durable coordinator copies and re-encodes the whole journal on every
  tick. A bounded synthetic direct-store characterization confirms quadratic
  retained-byte growth at World `cb6bfb7c9bccd16c2f85f0f24deba1a12bfc80c8`;
  workload-level cost remains unknown. See the [journal snapshot-store
  characterization](journal-snapshot-store.md#follow-up-size-and-write-characterization).
- Whether uniqueness of record identifiers should be a property of the
  journal rather than of its callers is undecided.
