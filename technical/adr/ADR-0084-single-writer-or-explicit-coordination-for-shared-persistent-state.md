# ADR-0084 — Single writer or explicit coordination for shared persistent state

> **Provenance.** Transcription of `AD-0010` from the sealed architecture audit
> dossier of `alessbarb/symbiont-lab` (archive `.audit.zip`, SHA-256
> `ff258afcb1c80b9feefacc28575d1e5ccd5f15c062dd36499498747df4d57df2`): the `AD-0010` row of `.audit/registers/decisions.md` (SHA-256 `0c03a0d438ff4a38337c683ecd4649ce3862cf600b6f3e2f2baf1ab421e5d43d`).
> The decision, status and ratification texts below are verbatim. The source row has no title; the title above was written for this record.
> Section headings were added. Identifiers of the form `AD-NNNN` inside the
> text are the source identifiers; see References for the corresponding
> records here. Identifiers of the form `ADR-NNNN` up to `ADR-0072` name the
> historical decision records of `symbiont-lab`, which were not copied.

## Status

- **Status:** ACCEPTED
- **Type:** CONSTITUTIONAL NORMATIVE
- **Source identifier:** AD-0010

## Decision

Shared authoritative persistent state has either SINGLE WRITER OWNERSHIP or EXPLICIT CONCURRENT WRITE COORDINATION. Atomic file replacement alone is not mutual exclusion/conflict resolution. Scope excludes derived caches, temporary artifacts, immutable archives and independent per-process state. Architecture Owner clarifies that running two independent `observed_resident` processes against the same `--state-file` is NOT a supported deployment absent explicit coordination; this does not assert that CURRENT code prevents such invocation.

## Ratification and evidence

Ratification authority: Architecture Owner. EV-0219/0222/0249/0256; OP-0013 supported-contract question resolved by Owner clarification; current enforcement/applicability remains empirical under OP-0021.
