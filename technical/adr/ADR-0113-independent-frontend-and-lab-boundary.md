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

- **Status:** ACCEPTED — Biopeia TARGET responsibility allocation.
- **Work class:** `CONSTITUTIONAL`.
- **Operational risk:** `HIGH` because the proposal changes an accepted cross-domain responsibility allocation.
- **Decision authority:** Biopeia Architecture Owner.
- **Decision date:** 2026-10-13.
- **Decision evidence:** [Docs #166 owner decision](https://github.com/biopeia/docs/issues/166#issuecomment-6144222674).
- **Implementation authorization:** Authorized prospectively but deferred. No implementation starts now. A separate Owner start instruction and completion of the readiness gates in the approved readiness plan are required; this ADR does not authorize API/schema/transport choices, experiments, runtime control or deployment.

## Context

[ADR-0102 — Lab](ADR-0102-lab.md) is accepted and says Lab may present through Workbench/UI. [Docs #164](https://github.com/biopeia/docs/issues/164) and [PR #165](https://github.com/biopeia/docs/pull/165) propose a complete human-facing presentation application independent from Lab. At the time this ADR was proposed, the accepted ADR and proposed design had a material responsibility conflict. The Architecture Owner has now resolved the TARGET responsibility allocation through the decision recorded below; Lab #63 reconciliation remains outstanding.

The approved application is a read-only presentation consumer of authorized Observation publications. It is not a domain authority, causal runtime, scientific apparatus, evidence custodian or operator-control mechanism. This boundary is consistent with [ADR-0078 — Observation is causally passive](ADR-0078-observation-is-causally-passive.md), [ADR-0100 — Observation capability and evidence custody](ADR-0100-observation-capability-and-evidence-custody.md), and [ADR-0101 — Operator Control](ADR-0101-operator-control.md).

## Accepted decision

Establish a standalone Biopeia frontend application/repository, provisionally named `biopeia/frontend`, for human-facing presentation of authorized Observation publications. It has independent application and release lifecycle, but acquires no semantic or causal authority.

This decision **partially supersedes ADR-0102 for Biopeia TARGET only**, and only for allocation of the general human-facing visualization application:

1. Lab does not own or host the canonical standalone Biopeia frontend or its general-purpose visualization UI.
2. Lab retains its scientific apparatus responsibilities, including studies, protocols, experiment/run orchestration within its authority, evidence admission and custody, scientific analysis, and any Lab-specific scientific tooling that is not the canonical general-purpose frontend.
3. Presentation of a publication does not admit it as scientific evidence. Lab remains the scientific/evidence custodian under its applicable contracts.
4. Observation remains a passive publication/read boundary. The frontend consumes only approved Observation paths and cannot publish, mutate domain state, or establish causal truth.
5. Runtime controls, experiment interventions, run creation/launch and evidence admission are outside this frontend decision. Any future control surface requires its own competent authorization and contract under ADR-0101; it may not be inferred from visualization needs.
6. World and domain owners retain their existing authority over causal state, domain state, identity, meaning and publication. The frontend must preserve the source authority and provenance required by the applicable Observation family.
7. This decision does not select or approve a wire schema, API, transport, authentication model, deployment topology, data-retention policy or supported Observation family. Those require evidence-backed, separately reviewed contracts and decisions.

### Lab-specific tooling boundary

Classify a human-facing capability by the work it performs, not by its visual form, technology, repository path or data source:

- **Lab-specific scientific tooling** is integral to carrying out or evaluating a Lab-owned scientific operation. It may configure or execute an authorized protocol/run, operate scientific apparatus, validate protocol-specific measurements, admit/custody evidence, or analyze study-scoped results. Lab may own such tooling, including embedded plots or 3D views, when those views are part of that bounded scientific workflow.
- **General-purpose frontend presentation** displays authorized Observation publications for human inspection across ordinary runtime or multiple scientific contexts. It does not itself execute a protocol, operate apparatus, admit evidence, or perform study-specific analysis. The proposed independent frontend owns this presentation application and its shared UI; it does not acquire the domain or scientific authority of the displayed data.
- A capability that combines both responsibilities must be split at the operation boundary: Lab owns the scientific operation and any apparatus-specific interface necessary to perform it; the frontend owns reusable presentation of authorized publications. A shared appearance, shared charting component, or common data source does not transfer ownership.

If a future capability cannot be classified by these criteria, its owner must be resolved explicitly before implementation; repository placement or visual similarity is not a default ownership rule.

The historical text and provenance of ADR-0102 remain unchanged. Its remaining accepted responsibilities continue to apply. The ADR index and design register record the accepted partial supersession and approved design lifecycle.

## Alternatives considered

- **Retain the canonical Workbench/UI within Lab:** preserves ADR-0102 without amendment and minimizes repository count, but conflicts with the owner's stated product direction for an independent complete frontend. If selected, Docs #164 and PR #165 must be revised to remove the independent application allocation.
- **Establish an independent read-only frontend:** separates general presentation lifecycle from scientific apparatus while preserving Observation and Lab authority boundaries. Adds a repository and requires separately resolved access, contract and operations work. This is the accepted resolution.
- **Place the UI in Observation:** rejected because passive publication and human-facing presentation are distinct responsibilities; it would blur the boundary recorded by ADR-0100.
- **Place the UI in the workspace:** rejected because workspace tooling/orchestration is not a durable product application or semantic authority.
- **Make the frontend a Lab subsystem with a separate repository:** rejected as the proposed boundary because repository separation alone would not resolve Lab's ownership of the general presentation application.

## Consequences

- ADR-0102 is marked `PARTIALLY SUPERSEDED` only for the TARGET presentation allocation stated above; no historical text is rewritten.
- Docs #164 / PR #165 are reconciled to the accepted responsibility boundary. The design lifecycle remains governed by `registry/designs.yaml`; constitutional acceptance alone does not mark every companion specification approved.
- Lab #63 remains to be reconciled: general frontend presentation work is removed from Lab's implementation scope, while any distinct Lab scientific apparatus requirement is retained as a Lab-owned task. Existing work and evidence must be reviewed before re-scope; none is discarded by this ADR.
- A separate implementation-readiness plan identifies repository-owned issues and gates. Implementation is prospectively authorized but must not start until each required gate has its own evidence and competent approval and the Architecture Owner issues a separate start instruction.
- The frontend must not be represented as ready merely because this responsibility decision is accepted. Observation consumer contracts, security/access, UX approval, and release/operations ownership remain separate readiness conditions.

## Unselected alternative disposition

The Architecture Owner did not select the alternative of retaining the canonical Workbench/UI within Lab. The decision is recorded above; this paragraph preserves the alternative considered, not a pending choice.

## Decision record

- **Outcome:** ACCEPTED.
- **Authority:** Biopeia Architecture Owner.
- **Date:** 2026-10-13.
- **Decision evidence:** [Docs #166](https://github.com/biopeia/docs/issues/166)
- **Implementation authorization:** prospectively authorized but deferred; implementation must not start until the remaining readiness gates are satisfied and a separate Owner start instruction is given.

## References

- [ADR-0078 — Observation is causally passive](ADR-0078-observation-is-causally-passive.md)
- [ADR-0100 — Observation capability and evidence custody](ADR-0100-observation-capability-and-evidence-custody.md)
- [ADR-0101 — Operator Control](ADR-0101-operator-control.md)
- [ADR-0102 — Lab](ADR-0102-lab.md)
- [Docs #164 — Human-facing visualization design](https://github.com/biopeia/docs/issues/164)
- [Docs #166 — Constitutional decision](https://github.com/biopeia/docs/issues/166)
- [Docs PR #165 — Frontend proposal](https://github.com/biopeia/docs/pull/165)
- [Lab #63 — Render committed World projections](https://github.com/biopeia/lab/issues/63)
