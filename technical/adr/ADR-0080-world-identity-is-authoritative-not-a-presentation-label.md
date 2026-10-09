# ADR-0080 — World identity is authoritative, not a presentation label

> **Provenance.** Transcription of `AD-0006` from the sealed architecture audit
> dossier of `alessbarb/symbiont-lab` (archive `.audit.zip`, SHA-256
> `ff258afcb1c80b9feefacc28575d1e5ccd5f15c062dd36499498747df4d57df2`): the `AD-0006` row of `.audit/registers/decisions.md` (SHA-256 `0c03a0d438ff4a38337c683ecd4649ce3862cf600b6f3e2f2baf1ab421e5d43d`).
> The decision, status and ratification texts below are verbatim. The source row has no title; the title above was written for this record.
> Section headings were added. Identifiers of the form `AD-NNNN` inside the
> text are the source identifiers; see References for the corresponding
> records here. Identifiers of the form `ADR-NNNN` up to `ADR-0072` name the
> historical decision records of `symbiont-lab`, which were not copied.

## Status

- **Status:** ACCEPTED
- **Type:** CONSTITUTIONAL NORMATIVE
- **Source identifier:** AD-0006

## Decision

World identity is an authoritative `world_id` or explicitly defined canonical equivalent. Display names, CLI labels and UI titles are presentation, not identity. Persistent namespaces must explicitly relate to authoritative identity or deliberate configuration, never accidentally to a presentation label.

## Ratification and evidence

Ratification authority: Architecture Owner. EV-0224/0249; OP-0014 split to OP-0022. CURRENT compliance remains empirical.
