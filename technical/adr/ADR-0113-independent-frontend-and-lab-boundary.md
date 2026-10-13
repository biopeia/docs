---
id: ADR-0113
title: "Independent Frontend and Lab Presentation Boundary"
document_type: adr
owner: biopeia-architecture-owner
created: 2026-10-13
language: en
document_version: 1
---

# ADR-0113 — Independent Frontend and Lab Presentation Boundary

## Status and authority

- **Status:** PROPOSED — no constitutional effect until explicitly accepted by the Architecture Owner.
- **Work class:** `CONSTITUTIONAL`.
- **Operational risk:** `HIGH` because the proposal changes an accepted cross-domain responsibility allocation.
- **Decision authority:** Biopeia Architecture Owner.
- **Decision requested:** Accept or reject the proposed resolution below. Review, CI, merge, Issue state or Project state is not acceptance.
- **Implementation authorization:** Not granted. Acceptance of this ADR would settle the responsibility boundary only; it would not authorize repository creation, API/schema/transport choices, experiments, runtime control or deployment.

## Context

[ADR-0102 — Lab](ADR-0102-lab.md) is accepted and says Lab may present through Workbench/UI. [Docs #164](https://github.com/biopeia/docs/issues/164) and [PR #165](https://github.com/biopeia/docs/pull/165) propose a complete human-facing presentation application independent from Lab. The owner has directed that the frontend be independent, while [Lab #63](https://github.com/biopeia/lab/issues/63) still describes a Lab Workbench visualization target. The accepted ADR and proposed design therefore have a material responsibility conflict that cannot be resolved by a design document or PR merge.

The proposed application is a read-only presentation consumer of authorized Observation publications. It is not a domain authority, causal runtime, scientific apparatus, evidence custodian or operator-control mechanism. This boundary is consistent with [ADR-0078 — Observation is causally passive](ADR-0078-observation-is-causally-passive.md), [ADR-0100 — Observation capability and evidence custody](ADR-0100-observation-capability-and-evidence-custody.md), and [ADR-0101 — Operator Control](ADR-0101-operator-control.md).

## Proposed decision

If accepted, establish a standalone Biopeia frontend application/repository, provisionally named `biopeia/frontend`, for human-facing presentation of authorized Observation publications. It has independent application and release lifecycle, but acquires no semantic or causal authority.

This decision would **partially supersede ADR-0102 for Biopeia TARGET only**, and only for allocation of the general human-facing visualization application:

1. Lab does not own or host the canonical standalone Biopeia frontend or its general-purpose visualization UI.
2. Lab retains its scientific apparatus responsibilities, including studies, protocols, experiment/run orchestration within its authority, evidence admission and custody, scientific analysis, and any Lab-specific scientific tooling that is not the canonical general-purpose frontend.
3. Presentation of a publication does not admit it as scientific evidence. Lab remains the scientific/evidence custodian under its applicable contracts.
4. Observation remains a passive publication/read boundary. The frontend consumes only approved Observation paths and cannot publish, mutate domain state, or establish causal truth.
5. Runtime controls, experiment interventions, run creation/launch and evidence admission are outside this frontend decision. Any future control surface requires its own competent authorization and contract under ADR-0101; it may not be inferred from visualization needs.
6. World and domain owners retain their existing authority over causal state, domain state, identity, meaning and publication. The frontend must preserve the source authority and provenance required by the applicable Observation family.
7. This decision does not select or approve a wire schema, API, transport, authentication model, deployment topology, data-retention policy or supported Observation family. Those require evidence-backed, separately reviewed contracts and decisions.

The historical text and provenance of ADR-0102 remain unchanged. Its remaining accepted responsibilities continue to apply. The ADR index and design register should record the partial supersession only after explicit acceptance.

## Alternatives considered

- **Retain the canonical Workbench/UI within Lab:** preserves ADR-0102 without amendment and minimizes repository count, but conflicts with the owner's stated product direction for an independent complete frontend. If selected, Docs #164 and PR #165 must be revised to remove the independent application allocation.
- **Establish an independent read-only frontend as proposed:** separates general presentation lifecycle from scientific apparatus while preserving Observation and Lab authority boundaries. Adds a repository and requires separately resolved access, contract and operations work. This is the proposed resolution.
- **Place the UI in Observation:** rejected because passive publication and human-facing presentation are distinct responsibilities; it would blur the boundary recorded by ADR-0100.
- **Place the UI in the workspace:** rejected because workspace tooling/orchestration is not a durable product application or semantic authority.
- **Make the frontend a Lab subsystem with a separate repository:** rejected as the proposed boundary because repository separation alone would not resolve Lab's ownership of the general presentation application.

## Consequences if accepted

- ADR-0102 is marked `PARTIALLY SUPERSEDED` only for the TARGET presentation allocation stated above; no historical text is rewritten.
- Docs #164 / PR #165 are reconciled to the accepted responsibility boundary. The design lifecycle remains governed by `registry/designs.yaml`; constitutional acceptance alone does not mark every companion specification approved.
- Lab #63 is reconciled: general frontend presentation work is removed from Lab's implementation scope, while any distinct Lab scientific apparatus requirement is retained as a Lab-owned task. Existing work and evidence must be reviewed before re-scope; none is discarded by this ADR.
- A separate implementation-readiness plan identifies repository-owned issues and gates. No implementation begins until each required gate has its own evidence and authorization.
- The frontend must not be represented as ready merely because this responsibility decision is accepted. Observation consumer contracts, security/access, UX approval, and release/operations ownership remain separate readiness conditions.

## Rejection or alternative disposition

If the Architecture Owner rejects this proposal or chooses Lab-hosted Workbench/UI instead, this ADR must be recorded as rejected/superseded by the explicit disposition, and Docs #164 / PR #165 must be revised before design ratification. No implementation follows from a rejected proposal.

## Decision record

Complete this section only after an explicit competent-authority decision:

- **Outcome:** pending
- **Authority:** pending
- **Date:** pending
- **Decision evidence:** [Docs #166](https://github.com/biopeia/docs/issues/166)
- **Implementation authorization:** not granted by this ADR

## References

- [ADR-0078 — Observation is causally passive](ADR-0078-observation-is-causally-passive.md)
- [ADR-0100 — Observation capability and evidence custody](ADR-0100-observation-capability-and-evidence-custody.md)
- [ADR-0101 — Operator Control](ADR-0101-operator-control.md)
- [ADR-0102 — Lab](ADR-0102-lab.md)
- [Docs #164 — Human-facing visualization design](https://github.com/biopeia/docs/issues/164)
- [Docs #166 — Constitutional decision](https://github.com/biopeia/docs/issues/166)
- [Docs PR #165 — Frontend proposal](https://github.com/biopeia/docs/pull/165)
- [Lab #63 — Render committed World projections](https://github.com/biopeia/lab/issues/63)
