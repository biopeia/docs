# ADR-0084 — Single writer or explicit coordination for shared persistent state

## Provenance

- **Original decision:** AD-0010
- **Source:** sealed Biopeia Architecture v1 audit dossier of `alessbarb/symbiont-lab`,
  the `AD-0010` row of `.audit/registers/decisions.md` (SHA-256 `0c03a0d438ff4a38337c683ecd4649ce3862cf600b6f3e2f2baf1ab421e5d43d`)
- **Source integrity:** archive `.audit.zip`, SHA-256 `ff258afcb1c80b9feefacc28575d1e5ccd5f15c062dd36499498747df4d57df2`,
  recorded in the source repository as `BIOPEIA_ARCHITECTURE_V1_AUDIT_BASELINE`
- **Original authority:** Architecture Owner
- **Original acceptance date:** NOT RECORDED IN SOURCE
- **Transformation:** DOCUMENTARY NORMALIZATION ONLY
- **Semantic changes:** NONE
- **Editorial title:** added during documentary normalization; non-normative

The decision, status and ratification texts below are verbatim from the source.
The record number, the section headings, this provenance section and the
References list were added. Identifiers of the form `AD-NNNN` inside the text
are the source identifiers. Identifiers of the form `ADR-NNNN` up to `ADR-0072`
name the historical decision records of `symbiont-lab`, which were not copied.

## Status

- **Status:** ACCEPTED
- **Type:** CONSTITUTIONAL NORMATIVE

## Decision

Shared authoritative persistent state has either SINGLE WRITER OWNERSHIP or EXPLICIT CONCURRENT WRITE COORDINATION. Atomic file replacement alone is not mutual exclusion/conflict resolution. Scope excludes derived caches, temporary artifacts, immutable archives and independent per-process state. Architecture Owner clarifies that running two independent `observed_resident` processes against the same `--state-file` is NOT a supported deployment absent explicit coordination; this does not assert that CURRENT code prevents such invocation.

## Ratification and evidence

Ratification authority: Architecture Owner. EV-0219/0222/0249/0256; OP-0013 supported-contract question resolved by Owner clarification; current enforcement/applicability remains empirical under OP-0021.

## Register scope

The decisions register opens with a statement that applies to every
ratification in it, reproduced verbatim.

> Architecture Owner ratifications in this register are normative for TARGET. They do not assert CURRENT compliance. See EV-0249 and EV-0252 for ratification records and constitutional-text reconciliation.
