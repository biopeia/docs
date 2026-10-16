---
diataxis_kind: how-to
document_id: HOWTO-OBSERVATION-V2-LOCAL-ARCHIVE
domain: observation
source_of_truth: observation:src/observation/archive_capture.py
review_basis: observation@572c86f8fce66a73cc3899a4a929448416f1e6bf
---

# How to Capture and Read a Local Observation V2 Archive

This procedure demonstrates the bounded, opt-in local SQLite capture and read-only query path available in Observation `572c86f8fce66a73cc3899a4a929448416f1e6bf`. It is not the default `make run` workflow, a supported remote service, a complete producer history, or acceptance of Observation V2.

## Scope and prerequisites

- Run from the Biopeia workspace root with the existing `repos/world/.venv` runtime environment and the six source checkouts under `repos/`.
- The capture harness runs a fresh bounded World runtime and subscribes to publications emitted after the capture watermark. It does not backfill prior/current publications.
- The output directory must not already exist. The SQLite archive is operational local data; this procedure does not define production retention, backup, access-control, or scientific evidence-custody policy.
- Keep the archive on a local filesystem and do not expose it through HTTP or copy it into Lab evidence custody.
- The tested run uses 10 cycles. The harness accepts a bounded count from 1 through 100; this limit is a harness constraint, not a World simulation limit.

The two executable scripts used below are `observation-v2-capture.py` and `observation-v2-reopen.py` in this guide's directory. After this procedure is integrated into the canonical `repos/docs` checkout, the default `DOCS_ROOT` below points to them. To exercise a candidate before integration, set `DOCS_ROOT` to the documentation worktree containing this guide. `PYTHONPATH` is explicit so imports resolve to the checked-out source trees rather than an installed package selected by the environment.

## Capture a bounded run

Choose a new output path and run the capture harness:

```sh
OUT="$PWD/.local/observation-v2-local-$(date +%Y%m%d-%H%M%S)"
DOCS_ROOT="${DOCS_ROOT:-$PWD/repos/docs}"
test ! -e "$OUT" || { echo "Output path already exists: $OUT" >&2; exit 1; }
PYTHONPATH="$PWD/repos/observation/src:$PWD/repos/world/src:$PWD/repos/organism/src:$PWD/repos/embodiment/src:$PWD/repos/environment/src:$PWD/repos/modality/src" \
  repos/world/.venv/bin/python "$DOCS_ROOT/how-to/operator/observation-v2-capture.py" \
  --workspace "$PWD" --output "$OUT" --cycles 10
```

The harness starts the local archive capture, executes the bounded runtime, stops the capture in a `finally` path, closes the Observation bridge, and writes `runtime-capture.json` plus `archive-dir/observations.sqlite`. A failed process, missing report, nonzero exit, capture error, or non-verified coverage is a failed/ambiguous capture; do not treat it as complete. SQLite's `integrity_check=ok` alone is not a completeness claim.

## Reopen in a separate read-only process

After the capture process exits, run:

```sh
DOCS_ROOT="${DOCS_ROOT:-$PWD/repos/docs}"
PYTHONPATH="$PWD/repos/observation/src" repos/world/.venv/bin/python \
  "$DOCS_ROOT/how-to/operator/observation-v2-reopen.py" \
  --output "$OUT" --page-size 4
```

The read-only process writes `read-only-reopen.json`. It exercises local-receipt-sequence pagination, exact filters supported by stored metadata, family/catalog counts, coverage status, payload digest validation, and the explicit `unsupported_filter` result for `run_id`. It compares the SQLite file hash before and after reading to detect mutation.

Only filter fields actually present in the stored record may be queried. Missing identity and unverified coverage remain explicit; no values are synthesized. Local receipt order is not causal World order. A closed capture verifies only its declared local interval, not that every possible producer publication was emitted or observed. The reader does not prove World-cut membership and does not join publications from different owners.

## Bounded acceptance run recorded for this procedure

The commands above were exercised using the candidate scripts from the `docs/observation-38-local-acceptance-20261017` worktree. Machine-readable evidence is retained locally at `.local/observation-v2-acceptance-20261018T233958Z/`; it is not committed into the documentation repository. The folder timestamp is a local artifact name, not a declared capture timestamp.

- World run `observation-v2-41e9cda4-2081-431a-8976-075d2de9422c` completed 10 cycles through causal tick 10. Profile: `m1.scalar-sensorimotor.operator-r3`, SHA-256 `1b16404ff02b000f458f8f0718d27356681efcb5a5c7bcd9140b651c50e03bbb`.
- Capture `5c45d6a1-c49f-40e6-83a7-af6eaf592ce1` closed `closed_verified` for its declared local interval: 32 persisted receipts, no recorded received-not-persisted publications, gaps, or unverifiable intervals. This does not establish producer-wide completeness.
- A separate process reopened the file; SQLite integrity was `ok`, payload digests validated, and all 32 records were paginated in eight pages of four. Exact stored-metadata filters for owner, family, subject, revision, and domain time returned results. `run_id` returned `unsupported_filter`.
- Archive SHA-256 was `c5bd84410e286f8548e4dbe87c32a574096199b535ce3493511a01f7353687ab` before and after the read-only query.
- Source revisions and imported module paths are recorded in `runtime-capture.json`. Observation and Organism had pre-existing untracked nested worktree paths; those checkouts were not modified by this run.

This is a bounded local execution, not a `make run` integration, browser/history acceptance, indefinite-runtime result, physical disk-loss test, World-cut query, shared/remote access approval, or evidence-custody decision. Observation #38 remains open.
