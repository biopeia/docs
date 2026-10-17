# World commit and recovery: filesystem effects and crash-test coverage (v1)

**Scope:** an investigation for V-03 of
[the verification strategy](verification-strategy-v1.md). It maps each
filesystem effect on World's commit and recovery path to the process-termination
tests that cover it, and it lists the effects no test covers. It changes no
code and orders no work. Whether to build the harness in §4, and how, is
World's decision; the formal model in §5 also needs Architecture Owner review
(ADR-0083, ADR-0093).

Read at `world` `d66ac6197c8ea8489dc4f2689641ff0a88b6482a` (main on
2026-10-16): `src/world/durable_runtime.py`, `src/world/manifest.py`,
`src/world/owner_checkpoint_store.py` and `tests/test_durable_runtime.py`.
Line numbers refer to that revision.

The failure model is **process termination**: the process stops at an
arbitrary instruction, and the filesystem keeps every completed system call.
That is the model the existing tests use, and the repository states its limit:
the evidence "is not power-loss fault injection or a general crash-consistency
proof" (`world:MIGRATION.md`). Directory `fsync` only matters under power loss,
so under this model it is a point where termination can occur, not a point
where data can be lost.

## 1. The sequence of one tick

`DurableWorldRuntime.tick` (`durable_runtime.py:1342`) runs these steps in
order:

1. `_begin_transition` publishes a **PREPARING** manifest (`manifest.py`
   `_write`, around line 491). It writes a temporary file, flushes it, calls
   `os.replace` on the manifest, then flushes the directory.
2. The owner callback writes owner checkpoints (`owner_checkpoint_store.py`
   around line 185). Each one is written to a temporary file, flushed,
   hard-linked to its content address, followed by a directory flush and
   removal of the temporary file.
3. Owner causal records are collected, and declared dependencies are
   verified (`_verify_dependency_declarations`).
4. The journal is written (`durable_runtime.py` around line 470). The first
   write uses a temporary file, a flush, a hard link and a directory flush.
   Later writes open the journal, `truncate` it to the committed offset, write
   the delta, and flush.
5. `_commit_transition` publishes the **COMMITTED** manifest through the same
   `_write`.
6. If any step raises, the runtime latches and `_record_failure` writes a
   **RECOVERY_REQUIRED** manifest.

`recover_previous_cut` discards the uncommitted journal tail (`truncate` and
`fsync`, around line 586), lets the owners restore, and then completes. It
writes an immutable recovery receipt with temporary file, flush, link and
directory flush, then a COMMITTED manifest.

## 2. Coverage by the existing tests

| Termination point | Test | Covered |
|---|---|---|
| After PREPARING is published, before owner writes | `test_process_termination_after_preparing_reopens_prior_cut_as_recovery_required` | Yes |
| During a partial PREPARING manifest temporary write | `test_process_termination_during_partial_manifest_write_keeps_previous_cut` | Yes |
| During a partial owner checkpoint write | `test_process_termination_during_partial_owner_checkpoint_write_requires_recovery` | Yes |
| After the journal delta is appended and flushed, before COMMITTED | `test_process_termination_after_uncommitted_journal_append_recovers_prior_prefix` | Yes |
| A flush error on the journal append (exception, not termination) | `test_journal_append_fsync_failure_keeps_previous_committed_prefix` | Yes |
| Recovery publication interrupted, then retried | `test_retry_after_recovery_publication_interruption_fsyncs_existing_receipt_directory` (interrupts `_write`; the process is not terminated) | Partly |

## 3. Points no test covers

Coverage was checked by mechanism as well as by name. `git grep` over all of
`tests/` at this revision found process termination (`os._exit`) only in the
five `test_durable_runtime.py` tests above. Injected `os.fsync` failures
appear only in the journal-append test. `_fsync_directory`, `_record_failure`
and `_discard_uncommitted_tail` are called directly in the tests named in the
table. `tests/test_owner_checkpoint_store.py` has no retry or crash test, and
`tests/test_journal.py` exercises the in-memory journal, not the journal file.

None of these is known to fail. Each is a point the guarantee claims and no
test exercises.

| # | Point | Expected under the code's design | Why it matters |
|---|---|---|---|
| G1 | Termination during a partial **COMMITTED** manifest temporary write | `os.replace` has not run, so the PREPARING manifest remains and reopening requires recovery | Only the PREPARING write is tested; the COMMITTED write is the one that decides the cut |
| G2 | Termination after the COMMITTED `os.replace`, before the directory flush | The new cut is committed | It is the commit point itself; no test terminates there |
| G3 | Termination after the journal `truncate` to the committed offset, before the delta write | Same state as before the append | It is the only step that shortens a file during a tick |
| G4 | Termination during `_record_failure` (the RECOVERY_REQUIRED write) | PREPARING remains, so reopening requires recovery, as in the first test | The write itself is exercised directly (`test_manifest.py::test_failure_detail_is_durable_and_does_not_clear_recovery_state`), but not under termination |
| G5 | Termination inside `recover_previous_cut`: after the tail is discarded, after owners restore, or between receipt and manifest | Retry completes the same recovery; receipts are identity-stable (finding F-0011) | Recovery is tested for an exception, not for termination at each step |
| G6 | Termination between an owner checkpoint hard link and its directory flush, or before the temporary file is removed | A content-addressed retry is idempotent; the code comments on this case (around line 180) | Leftover temporary files and retry idempotence have no termination test |
| G7 | Termination during the first journal write (temporary file, link) as opposed to the append path | The genesis or first cut stays recoverable | Only the append path is tested since `9f65707` |

## 4. Systematic enumeration (engineering)

The points above are the full list of filesystem effects on the path:
temporary-file write, file flush, `os.replace`, `os.link`, `truncate`,
directory flush, and `unlink`. A harness can wrap these calls in a child
process, terminate the child at the *n*-th effect for every *n* of one tick,
and after each termination reopen and assert one invariant:

> After reopening, either the manifest is COMMITTED at the previous tick with
> its journal prefix and owner references verifying, or it requires recovery
> and recovery restores exactly that cut. It is never COMMITTED at the new tick
> unless every reference of the new cut verifies.

The count of *n* is small: by reading the code, one tick crosses an estimated few dozen effects (not measured). So the
enumeration is exhaustive for one tick under this failure model, where the
current tests are a sample. Running the same harness over
`recover_previous_cut` covers G5. A new effect site added to the path is
enumerated automatically, so coverage cannot silently fall behind the code.

## 5. Formal model (for review)

The state the invariant speaks about is small: manifest status (COMMITTED,
PREPARING, RECOVERY_REQUIRED), committed tick, committed and candidate
journal offsets, and the set of owner references. Writing it as a transition
system, with one step per filesystem effect plus *terminate* and *reopen*,
lets the invariant above be model-checked (TLA+) or proved (Lean 4) for every
interleaving, recovery included. The model verifies the protocol, not the
Python. The harness in §4 ties them together: each enumerated trace from the
code must be a path in the model's transition relation.

> **Architecture review, 2026-10-17.** The owner relayed a delegated
> technical review of this section: **favourable, with conditions**. Modelling
> commit and recovery as a transition system, checked against an interruption
> harness, is an adequate way to investigate the protocol. The model must
> represent the manifest status, the journal offsets, the checkpoint
> references, and the commit and recovery transitions. Three conditions:
>
> 1. **Explicit invariants:** no uncommitted cut is recovered; references
>    from different cuts are never mixed; resuming duplicates no effect.
> 2. **Model–implementation correspondence:** each formal transition names
>    the World operation it stands for.
> 3. **Model limits:** process termination is kept distinct from power loss,
>    corruption and concurrent writers.
>
> This section is still a proposed model, not an executable formal
> specification. The approach is approved for World to prepare the harness
> and the model; the protocol is **not** verified. Architectural approval
> remains with the Biopeia owner; implementation belongs to World.

## 6. Limits

The effect sites were read from source, not traced at run time. Termination
is the only failure model considered; power loss, filesystem bugs and
concurrent writers are out of scope (ADR-0084 covers coordination). No claim
is made that any uncovered point fails.

## 7. Current-main revalidation (2026-10-17)

The source/test inventory was rechecked against World `main` at
`873c8a96b9c94d8f745404d5a009b3b8bf00734c` (with Docs `main` at
`60b0f49678b1e9871b337ee2514e53278b3a4536`). The seven recorded termination
points G1–G7 remain without corresponding process-termination tests in
`tests/test_durable_runtime.py`. That file still has five termination tests:
PREPARING publication, partial owner-checkpoint write, partial manifest temp
write, uncommitted journal append, and one recovery/transition path. This
revalidation confirms the previously identified **coverage gap only**; it
neither demonstrates a failure at G1–G7 nor establishes power-loss safety.

No test suite was run for this revalidation. No source code was changed. The
harness and formal-model proposals above remain proposals, not accepted World
work or verified guarantees. World retains authority to select or reject the
next engineering step.

## 8. Coverage after World #185 and #186 (2026-10-17)

> Section note, 2026-10-17. Checked against `world` `5d4abca26b4cd88232b9c69feae42b38760c5f6b`.
> The tests below were run there with World's virtual environment:
> `pytest tests/test_durable_runtime.py tests/test_owner_checkpoint_store.py -k "process_termination or initial_journal_rejects"`,
> 13 passed. §7 above describes the earlier revision `873c8a9` and is kept as it was.

World added process-termination tests in #185 (`c5f055cef325e919ceb9ddc8a67c22c95c4c2a78`)
and #186 (`5d4abca26b4cd88232b9c69feae42b38760c5f6b`):

| Point | Test now covering it | Status |
|---|---|---|
| G1 partial COMMITTED manifest write | `test_process_termination_during_partial_manifest_write_keeps_previous_cut`, parametrised `PREPARING` and `COMMITTED` | covered |
| G2 after the COMMITTED `os.replace`, before the directory flush | `test_process_termination_after_committed_manifest_replace_keeps_new_cut` | covered |
| G3 after the journal `truncate`, before the delta write | `test_process_termination_after_journal_truncate_before_delta_keeps_prior_cut` | covered |
| G4 during `_record_failure` (the RECOVERY_REQUIRED write) | none; the partial-manifest test is parametrised only for `PREPARING` and `COMMITTED` | **not covered** |
| G5 inside `recover_previous_cut` | `test_process_termination_during_owner_restoration_keeps_recovery_retryable` | **partly**: termination during owner restoration. Termination after the tail is discarded, or between the receipt and the manifest, has no dedicated test |
| G6 owner checkpoint link and directory flush | `test_process_termination_after_owner_blob_link_is_retryable`, parametrised `after-link` and `after-directory-fsync` | covered |
| G7 first journal write | `test_process_termination_during_first_journal_publication_allows_genesis_retry`, with `test_initial_journal_rejects_existing_bytes_that_are_not_the_exact_candidate` | covered, **with a source change** (below) |

**G7 changed the code, not only the tests.** At `5d4abca`,
`DurableJournalSnapshotStore` no longer rejects an existing journal file at
initialisation outright. It accepts the file only when its bytes equal the
exact genesis bytes being proposed, which is the case after a termination
between publishing the first journal and publishing its manifest. Any other
content still raises `ManifestError`.

This change is why most World units with review basis `d66ac61` are now
reported stale. For `world-durable-runtime`, `world-causal-transition`,
`world-genesis-and-rosters`, `world-recovery` and `physical-causal-step`,
`durable_runtime.py` is the only file listed. Two units list more files:

- `world-journal-snapshot-store` also lists Organism `bounded_action.py`;
- `lab-operator-material-transfer` also lists World `causal_cycle.py` and
  Organism `competence.py`.

Reviewing these units and moving their bases waits for the World
documentation work in preparation (owner disposition of 2026-10-17).

> Section note, 2026-10-17, later the same day. World #188 merged as
> `20653e845867d1e0bbc4745e354b9a6d81cdd8b8`. The text below replaces the
> earlier line that called it open.

World #188 adds `tests/test_systematic_fault_injection.py`. It terminates the
process at each intercepted filesystem effect (`replace`, `link`, `unlink`,
`fsync`) along the normal path of `tick()` and of `recover_previous_cut()`.
It does not intercept `truncate` or `write`, and I did not map each G5
sub-point to an effect index. G4 is on the failure path (`_record_failure`),
which the harness does not trace, so **G4 is still not covered**.

World #188 also adds a TLA+ model, `specs/WorldCommitRecovery.tla`. A `formal-tlc`
CI job runs TLC on it with a pinned JAR digest; on the merge commit it
reported "No error has been found", with 142 distinct states. Invariant `I3`
now requires the committed journal length to equal the committed tick plus
one on a COMMITTED manifest, which is the "no duplicated effect on resume"
condition of the architecture review. The model checks a single owner
identity, with `MaxTick = 2`.

The pinned TLC release, `v1.8.0`, is a GitHub prerelease that upstream
republishes. When it does, the digest check will fail closed.
