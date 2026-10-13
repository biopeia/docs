---
id: design.cross-domain.biopeia-frontend-approval-and-development-readiness-v1
title: "Biopeia Frontend v1 — Approval and Development Readiness Plan"
document_type: design
owner: biopeia-project-owner
created: 2026-10-13
language: en
document_version: 1
---

# Biopeia Frontend v1 — Approval and Development Readiness Plan

**Lifecycle:** Proposed; not ratified. `registry/designs.yaml` is authoritative.
**Purpose:** Define the evidence and competent-authority gates for formal design approval and later implementation.
**Implementation authorization:** Not granted.

## 1. Purpose and boundary

This plan completes the review package for the proposed independent Biopeia frontend. It makes explicit what can be approved now as a design, what requires a constitutional decision, and what must be established before code or deployment work begins.

The plan does not itself ratify the independent frontend, amend ADR-0102, establish an Observation API/schema/transport, authorize experiments or runtime control, create a repository, or approve deployment. Its statuses are readiness tracking, not authority.

## 2. Approval package

The formal review package consists of:

1. [Independent visualization application design](biopeia-frontend-v1.md) — architecture, boundaries, phases and explicit exclusions.
2. [Functional, interaction and UX specification](biopeia-frontend-ux-spec-v1.md) — seven peer-level screens, interactions, states and source-backed readiness snapshot.
3. [Visual design specification](biopeia-frontend-visual-design-v1.md) — visual language and clearly identified synthetic concepts.
4. [Proposed ADR-0113](../../adr/ADR-0113-independent-frontend-and-lab-boundary.md) — adoption-ready constitutional text for the unresolved ADR-0102 presentation allocation.
5. This readiness plan — separates design approval from implementation authorization and assigns subsequent evidence to competent owners.

All documents remain proposed until their designated lifecycle authority records otherwise. No PR merge, CI result, review count or Project field substitutes for constitutional acceptance.

## 3. Formal design approval gates

| Gate | Required evidence | Competent authority | Current status |
|---|---|---|---|
| A. Responsibility allocation | Explicit accept/reject disposition of proposed ADR-0113; partial ADR-0102 scope stated; Lab responsibilities preserved | Architecture Owner; tracked by [Docs #166](https://github.com/biopeia/docs/issues/166) | OPEN — human constitutional decision |
| B. Design consistency | Independent review of architecture, UX, visual design and exact candidate revision; findings resolved or bounded | Docs design owner and reviewer under BAW-004; constitutional authority remains separate | BOUNDED — independent adversarial review of PR #165 candidate `3c4f20ff4f98d0b61bfdc77e6e81b68d9e559a02`; no material contradiction within Proposed-design scope. |
| C. Observation feasibility | Re-inspected, exact-revision inventory of actual family, publication, query/delivery, replay, identity, access and World-cut verification contracts; unsupported paths explicitly excluded | Observation owner for its contracts; World/domain owners for their publication/adoption claims | OPEN — snapshot is not an approved client contract |
| D. Lab scope reconciliation | Lab #63 separated into any Lab-owned scientific-apparatus requirement and any frontend-owned presentation requirement; no work/evidence lost | Lab owner; tracked by [Lab #63](https://github.com/biopeia/lab/issues/63) | OPEN — depends on Gate A |

The package can reach **Design Review Complete** only when Gates A and B are resolved and the remaining C/D questions are either bounded as explicit blockers to implementation or assigned to a competent owner with a linked issue and closure trigger. Design Review Complete does not imply implementation readiness.

The [independent review record](https://github.com/biopeia/docs/pull/165#issuecomment-6142822054) documents the bounded outcome. It is not a formal GitHub approval, constitutional acceptance, or implementation authorization.

## 4. Source-backed Observation baseline

The UX specification records a discovery snapshot from `biopeia/observation` at `1456df093e4ac28032d956e4df30957f0bf87cec` (2026-10-13). That snapshot found a semantic claim model and bounded in-process plane; partial readiness for finite scalar-field and BodyPose mappings; no established World-verified committed-cut consumer publication path; no established full Environment-to-receptor-to-Modality-to-Organism family; and no supported browser/network/auth/query or cross-restart replay path.

These are inspection results at a pinned revision, not permanent claims about current `main` and not approval of a frontend contract. Before implementation, the Observation owner must refresh the inventory against exact current source revisions and explicitly approve the client-consumable contracts and access boundary. A frontend issue may consume only capabilities established by that review. Missing capability means exclude/disable the function truthfully, not create a mock or an undocumented adapter that supplies missing semantics.

## 5. Implementation authorization gates

No application implementation begins until all applicable gates below have evidence and competent approval:

### 5.1 Constitutional and repository gate

- ADR-0113 is explicitly accepted or an alternative decision is recorded.
- The design register records the decision and lifecycle; ADR-0102 is indexed with its precise disposition without rewriting history.
- Lab #63 and Docs #164/PR #165 are reconciled to the accepted boundary.
- Classify Lab-specific scientific tooling versus general frontend presentation using ADR-0113's operation-based criteria; split mixed capabilities by operation and account for existing Lab work/evidence before re-scope.
- Architecture Owner authorizes implementation planning for the approved target boundary.
- Repository owner, release owner and security/operations responsibility for `biopeia/frontend` are named before repository creation or external deployment.

### 5.2 Observation and domain-contract gate

- Exact source revisions and owner-approved contracts are identified for each first-release feature.
- Contracts preserve the ratified Observation Semantic Model: authority, typed subject, epistemic basis, domain time/revision, provenance, availability, family revision, units/frame where applicable, coherence and delivery guarantees.
- World-side evidence is required before presenting a cut as World-committed or coherent.
- No frontend UI join is treated as domain identity linkage or causal evidence.
- For any unsupported feature, its issue either removes the feature from the release scope or blocks it until the owner publishes the needed contract.

### 5.3 Security and deployment gate

- A threat model distinguishes local development from any shared or production deployment.
- Authentication/authorization principal, read scopes, data classification, secrets handling, CORS/origin policy, cache behavior, logging/retention, export and operational owner are specified for the target environment.
- Access denial, stale credentials, partial scope, disconnect, oversized/untrusted content and unsafe links have defined safe behavior.
- A server-side proxy/BFF, gateway, database, public exposure or credential persistence is not introduced without its own design, owner and security review.

### 5.4 UX, accessibility and performance gate

- Seven peer-level screens, context absence, loading, empty, partial, stale, unsupported, gap, conflict, access-denied and error states are covered.
- Visual concepts are explicitly marked synthetic; visual detail does not imply real source capability.
- Keyboard, screen reader, reduced motion, non-3D equivalent information and both themes have testable acceptance criteria.
- Performance targets are labeled provisional until benchmark hardware, datasets, measurement method and thresholds are approved.

### 5.5 Integration and release gate

- Implementation issues name owning repository, exact dependencies, acceptance evidence, risk/class, review authority and rollback or exclusion behavior.
- The production integration path uses approved Observation publication; no workspace/test fixture substitutes for missing production composition.
- End-to-end acceptance records exact repository revisions, configuration, command, identity/cut/publication evidence, negative cases and limitations.
- Independent review is obtained where BAW-004 requires it; scientific or constitutional authority remains with its designated owner.
- Deployment and operational readiness are reviewed separately from local development success.

## 6. Proposed issue decomposition

The entries below are work packages to create or reconcile in the owning repositories after the relevant parent issues are reviewed. They are not claims that these issues already exist, and this table does not create implementation authorization. Reuse [Docs #164](https://github.com/biopeia/docs/issues/164), [Docs #166](https://github.com/biopeia/docs/issues/166) and [Lab #63](https://github.com/biopeia/lab/issues/63) rather than creating duplicates.

| Package | Owning repository | Dependency | Completion evidence |
|---|---|---|---|
| Constitutional application boundary and ADR disposition | `docs` | Architecture Owner decision | Accepted/rejected ADR record; ADR-0102 and design-register status reconciled |
| Lab #63 responsibility reconciliation | `lab` | Constitutional disposition | Lab-only scientific apparatus scope preserved; presentation scope linked to frontend work; existing evidence accounted for |
| Approved Observation consumer contract inventory | `observation` with affected domain owners | Current source inspection; no schema assumption | Exact revisions, supported families/publication/read path/access semantics, World verification and exclusions approved by competent owners |
| Frontend security/access and deployment design | `docs` plus named operations/security owner | Target deployment context identified | Threat model and explicit local/shared/production access decisions approved |
| Frontend repository bootstrap and shell | `frontend` once created | Gates 5.1–5.4; explicit implementation authorization | Governed repository, CI, locked toolchain, read-only shell, empty/denied states; no fabricated production records |
| First supported read-only feature slice | `frontend` + `observation` | Approved contract for that feature | Exact-source end-to-end rendering, provenance inspection and negative-state tests |
| Spatial visualization | `frontend` + relevant domain owners | Approved spatial family, frames and geometry/pose linkage | Claim-to-renderer-to-inspector trace; non-3D parity; unsupported cases fail truthfully |
| Release and production deployment | `frontend` and named operations owner | Security, accessibility, performance and integration acceptance | Operational runbook, access verification, release review and known-limitations report |

Any child issue must state the exact missing evidence/decision, accountable owner, repository, dependency, acceptance criteria, applicable independent review and closure trigger. Do not create a child for a capability that is explicitly excluded from v1.

## 7. Decision and status transitions

1. **Proposed design:** current state. Documentation and review may continue; no implementation authority follows.
2. **Constitutional decision accepted:** the application responsibility boundary is settled. This does not automatically approve the design or authorize code.
3. **Design Review Complete:** architecture/UX/visual proposal has exact-revision review and bounded feasibility/security questions. This authorizes issue planning only, unless a separate explicit decision says otherwise.
4. **Implementation authorized:** competent owner approves the scoped implementation plan after required contracts and security decisions exist.
5. **Implementation accepted:** each implemented feature passes its own technical and integration acceptance. Release/deployment remains separate.

Lifecycle updates belong in the canonical design register and decision records. Project #1 is coordination only.

## 8. Out of scope

This plan does not approve the frontend architecture, freeze React/TypeScript/Vite/Three.js as required technology, approve the visual identity, choose API/schema/transport/authentication/deployment, create or modify a frontend repository, authorize runtime controls, authorize experimental execution, accept evidence, claim browser access exists, or establish causal replay. No legacy Symbiont code or backward compatibility is permitted or required.

## References

- [Biopeia Frontend v1 architecture design](biopeia-frontend-v1.md)
- [Biopeia Frontend v1 UX specification](biopeia-frontend-ux-spec-v1.md)
- [Biopeia Frontend v1 visual design](biopeia-frontend-visual-design-v1.md)
- [Proposed ADR-0113 — Independent Frontend and Lab Presentation Boundary](../../adr/ADR-0113-independent-frontend-and-lab-boundary.md)
- [ADR-0078 — Observation is causally passive](../../adr/ADR-0078-observation-is-causally-passive.md)
- [ADR-0100 — Observation capability and evidence custody](../../adr/ADR-0100-observation-capability-and-evidence-custody.md)
- [ADR-0101 — Operator Control](../../adr/ADR-0101-operator-control.md)
- [ADR-0102 — Lab](../../adr/ADR-0102-lab.md)
- [Docs #164](https://github.com/biopeia/docs/issues/164), [Docs #166](https://github.com/biopeia/docs/issues/166), [Lab #63](https://github.com/biopeia/lab/issues/63), [Docs PR #165](https://github.com/biopeia/docs/pull/165)
