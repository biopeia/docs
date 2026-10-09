# ADR-0086 — Capture manifest last-sequence semantics

> **Provenance.** Transcription of `AD-0012` from the sealed architecture audit
> dossier of `alessbarb/symbiont-lab` (archive `.audit.zip`, SHA-256
> `ff258afcb1c80b9feefacc28575d1e5ccd5f15c062dd36499498747df4d57df2`): the `AD-0012` row of `.audit/registers/decisions.md` (SHA-256 `0c03a0d438ff4a38337c683ecd4649ce3862cf600b6f3e2f2baf1ab421e5d43d`).
> The decision, status and ratification texts below are verbatim. The source row has no title; the title above was written for this record.
> Section headings were added. Identifiers of the form `AD-NNNN` inside the
> text are the source identifiers; see References for the corresponding
> records here. Identifiers of the form `ADR-NNNN` up to `ADR-0072` name the
> historical decision records of `symbiont-lab`, which were not copied.

## Status

- **Status:** ACCEPTED
- **Type:** TARGET CONTRACT / CONSTITUTIONAL NORMATIVE
- **Source identifier:** AD-0012

## Decision

`CaptureManifest.last_sequence` is the inclusive, durable, record-oriented highest journal sequence successfully persisted as part of the capture; empty journal uses `null`, records `0..N` use `N`. It is not the next ordinal. Reservation without successful persistence does not make an ordinal the manifest's last sequence. A next ordinal uses a distinct `next_sequence` concept or explicit derivation.

## Ratification and evidence

Ratification authority: Architecture Owner. EV-0278. CURRENT comparison is separate: FND-0021 records the static semantic mismatch in the pinned resident path, without automatically labeling it corruption/off-by-one. No fault injection or durability test performed.
