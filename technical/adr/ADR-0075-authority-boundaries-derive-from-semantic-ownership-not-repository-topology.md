# ADR-0075 — Authority boundaries derive from semantic ownership, not repository topology

> **Provenance.** Transcription of `AD-0001` from the sealed architecture audit
> dossier of `alessbarb/symbiont-lab` (archive `.audit.zip`, SHA-256
> `ff258afcb1c80b9feefacc28575d1e5ccd5f15c062dd36499498747df4d57df2`): the `AD-0001` row of `.audit/registers/decisions.md` (SHA-256 `0c03a0d438ff4a38337c683ecd4649ce3862cf600b6f3e2f2baf1ab421e5d43d`).
> The decision, status and ratification texts below are verbatim. The source row has no title; the title above was written for this record.
> Section headings were added. Identifiers of the form `AD-NNNN` inside the
> text are the source identifiers; see References for the corresponding
> records here. Identifiers of the form `ADR-NNNN` up to `ADR-0072` name the
> historical decision records of `symbiont-lab`, which were not copied.

## Status

- **Status:** ACCEPTED
- **Type:** CONSTITUTIONAL NORMATIVE
- **Source identifier:** AD-0001

## Decision

Derive authority boundaries first from semantic ownership, causality, state, interfaces, lifecycle and failure boundaries; do not infer authorities from historical package/repository topology. TARGET strategy: ORGANISM, EMBODIMENT, MODALITY, ENVIRONMENT, WORLD, OBSERVATION and LAB should evolve as independently versionable repositories only when those authorities survive architectural falsification. Multi-repo topology is a consequence of ratified authorities, never evidence that the authorities exist.

## Ratification and evidence

Ratification authority: Architecture Owner. EV-0033/0249/0252. The seven authority boundaries and target decomposition remain subject to Pass 15 falsification; no repository extraction is authorized.

## Register scope

The decisions register opens with a statement that applies to every
ratification in it, reproduced verbatim.

> Architecture Owner ratifications in this register are normative for TARGET. They do not assert CURRENT compliance. See EV-0249 and EV-0252 for ratification records and constitutional-text reconciliation.
