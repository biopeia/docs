# Incremental validators and their differential tests (V-06, v1)

**Scope:** a read-only investigation for V-06 of
[the verification strategy](verification-strategy-v1.md). It looks at places
where an incremental or cached computation replaces a full one, and at
whether a test compares the two over generated sequences. Implementation
belongs to Organism and World. Read at `organism` `779c097d2123` and `world` `8266b8968b4d`.

| Incremental path | Full counterpart | Differential evidence | Gap |
|---|---|---|---|
| Organism compact v5 action history: warm index and incremental validation (`actuation/action_history.py`) | Full-history `ActionDomain` round-tripped through its own checkpoint | `test_seeded_differential_matches_full_history`: 12 seeds × 120 generated operations, same verdict, message and state at every step. Also `test_regression_matches_full_history` (warm and cold) and `test_incremental_and_cold_agree_on_forged_segments` | None of substance. Seeds and length are fixed; a Hypothesis stateful machine would explore beyond them |
| World cached journal prefix verification, `DurableJournalSnapshotStore.verify_cached` (world `9b2011f`) | `DurableJournalSnapshotStore.verify` | One example: `test_changed_backing_file_invalidates_cached_prefix_and_rejects_tampering` (append, corrupt the backing file, expect rejection) | **No generated sequence** checks that `verify_cached(ref) == verify(ref)` after every operation. Operations would be: append, truncate, replace or corrupt the backing file, change its size or mtime, and reopen |

## Proposal (for World)

A seeded differential, or a `RuleBasedStateMachine`, over the journal store
alone. Apply random appends and random tampering with the backing file, and
assert after each step that the cached and full verifiers agree. The cache
must never accept what the full verifier rejects. This targets the one
optimization on the commit path whose divergence would let a tampered prefix
pass. It overlaps the crash-point harness of V-03 only in the store it
exercises.

## Limits

Only incremental paths named in commit messages and test names were
searched; other caches may exist.
