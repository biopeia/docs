# ADR-0083 — Causal cycles have explicit commit semantics

> **Provenance.** Transcription of `AD-0009` from the sealed architecture audit
> dossier of `alessbarb/symbiont-lab` (archive `.audit.zip`, SHA-256
> `ff258afcb1c80b9feefacc28575d1e5ccd5f15c062dd36499498747df4d57df2`): the `AD-0009` row of `.audit/registers/decisions.md` (SHA-256 `0c03a0d438ff4a38337c683ecd4649ce3862cf600b6f3e2f2baf1ab421e5d43d`).
> The decision, status and ratification texts below are verbatim. The source row has no title; the title above was written for this record.
> Section headings were added. Identifiers of the form `AD-NNNN` inside the
> text are the source identifiers; see References for the corresponding
> records here. Identifiers of the form `ADR-NNNN` up to `ADR-0072` name the
> historical decision records of `symbiont-lab`, which were not copied.

## Status

- **Status:** ACCEPTED
- **Type:** CONSTITUTIONAL NORMATIVE
- **Source identifier:** AD-0009

## Decision

Each material causal cycle has explicit working transition → causal resolution → COMMIT semantics. Pre-commit failure must not publish a complete causal transition; post-failure state is coherent, identifiable and recoverable under the runtime contract. Full transactional rollback is not required; equivalent staging, COW, rollback, transactional state, checkpoint/replay, commit log or mechanism is acceptable if invariant holds.

## Ratification and evidence

Ratification authority: Architecture Owner. EV-0037/0202/0203/0249; OP-0009 split to OP-0020. CURRENT guarantee remains empirical.

## Register scope

The decisions register opens with a statement that applies to every
ratification in it, reproduced verbatim.

> Architecture Owner ratifications in this register are normative for TARGET. They do not assert CURRENT compliance. See EV-0249 and EV-0252 for ratification records and constitutional-text reconciliation.
