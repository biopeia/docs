# ADR-0089 — Standing of historical ADRs for the target architecture

> **Provenance.** Transcription of `AD-0015` from the sealed architecture audit
> dossier of `alessbarb/symbiont-lab` (archive `.audit.zip`, SHA-256
> `ff258afcb1c80b9feefacc28575d1e5ccd5f15c062dd36499498747df4d57df2`): the `AD-0015` row of `.audit/registers/decisions.md` (SHA-256 `0c03a0d438ff4a38337c683ecd4649ce3862cf600b6f3e2f2baf1ab421e5d43d`).
> The decision, status and ratification texts below are verbatim. The source row has no title; the title above was written for this record.
> Section headings were added. Identifiers of the form `AD-NNNN` inside the
> text are the source identifiers; see References for the corresponding
> records here. Identifiers of the form `ADR-NNNN` up to `ADR-0072` name the
> historical decision records of `symbiont-lab`, which were not copied.

## Status

- **Status:** ACCEPTED
- **Type:** CONSTITUTIONAL NORMATIVE
- **Source identifier:** AD-0015

## Decision

Historical ADR `Accepted` status does not by itself make an ADR binding for TARGET. Explicit contradictions are resolved in favor of accepted audit constitutional ADs while preserving historical provenance. A non-explicit tension that constrains or prejudges an accepted or Pass-15-reserved decision is `CONFLICT_REQUIRING_OWNER`, not silently reconciled by Codex. Per-ADR Codex classification `TARGET_CONSTRAINT` is only a proposal until Architecture Owner confirmation. ADR-0060's denial of a possible common World causal authority and its assignment of ordinary population/life orchestration to Lab are `SUPERSEDED` for TARGET. Its claims that Physics3D is only Body apparatus, that Body/surroundings simulation belongs to Lab, or that it fixes ownership of the body-medium integration step are `SUSPENDED` pending Pass 15, neither active constraints nor superseded conclusions. Its remaining vocabulary and Organism-package placement rules require specific reconciliation.

## Ratification and evidence

Ratification authority: Architecture Owner. EV-0344. Preserve ADR source/status; register all 72 separately. ADR-0041 and ADR-0023 are explicitly `CONFLICT_REQUIRING_OWNER` pending exact scope reconciliation. ADR-0060 is component-scoped as described; no Pass-15 authority or implementation shape selected.

## Later note in the decisions register: ADR source-reconciliation addendum (2026-10-08)

The Owner's dispositions recorded at EV-0345 apply to ADR-0023 and ADR-0041 as scoped there; they do not add a new target architecture. ADR-0023 retains the causal coherence/recovery invariant but its whole-world deep rollback of Organism-private state is superseded; Organism defines private recovery semantics. ADR-0041's population cap is an apparatus bound, not TARGET ecological law. See `.audit/registers/adr_conflicts_for_owner.md` for exact pinned-text crosswalks and the six residual constitutional conflicts. No Pass-15-reserved Tanda 2 decision is ratified by these dispositions.

## Later note in the decisions register: EV-0408 append-only status correction — AD-0015 / ADR-0023 / ADR-0041

The AD-0015 row above preserves its original EV-0344-era routing as history. Its sentence stating that ADR-0023 and ADR-0041 are `CONFLICT_REQUIRING_OWNER` is **superseded as current status** by EV-0345 and EV-0378: ADR-0023 is `PARTIALLY SUPERSEDED / SCOPED TARGET CONSTRAINT` (recovery invariant retained; whole-world ownership of arbitrary private Organism rollback superseded), and ADR-0041 is `APPARATUS BOUND, NOT TARGET ECOLOGICAL LAW`. Neither remains an unresolved Owner decision. EV-0342/EV-0385 bound current cap mechanism only within their recorded scope; OP-0002 historical-run/harness applicability remains open. This notice does not alter AD-0015 or the historical source ADRs.
