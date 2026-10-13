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

**Lifecycle:** Approved by the Architecture Owner on 2026-10-13. `registry/designs.yaml` is authoritative.
**Purpose:** Record the accepted design decision and define the remaining evidence and competent-authority gates before implementation may start.
**Implementation authorization:** Prospectively authorized but deferred. Development must not start now; a separate Owner start instruction and completion of the readiness gates below are required.

## 1. Purpose and boundary

This plan records the approved independent Biopeia frontend design and makes explicit the remaining requirements before any code or deployment work begins. The Architecture Owner accepted ADR-0113 and approved the design on 2026-10-13, while prospectively authorizing implementation but deferring its start.

The plan records the Architecture Owner's acceptance of ADR-0113 and approval of the design package. It does not establish an Observation API/schema/transport, authorize experiments or runtime control, create a repository, approve deployment, or waive the remaining readiness gates. Its readiness statuses do not replace the authority of the owners named below.

## 2. Approval package

The formal review package consists of:

1. [Independent visualization application design](biopeia-frontend-v1.md) — architecture, boundaries, phases and explicit exclusions.
2. [Functional, interaction and UX specification](biopeia-frontend-ux-spec-v1.md) — seven peer-level screens, interactions, states and source-backed readiness snapshot.
3. [Visual design specification](biopeia-frontend-visual-design-v1.md) — visual language and clearly identified synthetic concepts.
4. [Accepted ADR-0113](../../adr/ADR-0113-independent-frontend-and-lab-boundary.md) — constitutional decision partially superseding ADR-0102 for the general-purpose Biopeia TARGET frontend allocation.
5. This readiness plan — separates design approval from implementation authorization and assigns subsequent evidence to competent owners.

The architecture, UX, visual-design and readiness documents are approved in `registry/designs.yaml`; ADR-0113 is accepted. The package remains subject to the implementation-start gates below. PR merge, CI results, review count or Project fields do not replace the named authorities' approval of their respective contracts.

## 3. Formal design approval gates

| Gate | Required evidence | Competent authority | Current status |
|---|---|---|---|
| A. Responsibility allocation | Explicit accept/reject disposition of proposed ADR-0113; partial ADR-0102 scope stated; Lab responsibilities preserved | Architecture Owner; tracked by [Docs #166](https://github.com/biopeia/docs/issues/166) | **RESOLVED — ACCEPTED** by the Architecture Owner on 2026-10-13; see [decision record](https://github.com/biopeia/docs/issues/166#issuecomment-6144222674) and accepted ADR-0113. |
| B. Design consistency | Independent review of architecture, UX, visual design and exact candidate revision; findings resolved or bounded | Docs design owner and reviewer under BAW-004; constitutional authority remains separate | BOUNDED — independent adversarial review of the design claims at PR #165 candidate `b34c39b77af7be7387fba8f3e54a9b56e6c2cb19`; the later delta to `e641b90b4c1c9c5ccd710e9aee925ad2c67efcbc` was confirmed non-material in [the exact-head update](https://github.com/biopeia/docs/pull/165#issuecomment-6143396043). The review record is not itself a GitHub approval or authority decision. |
| C. Observation feasibility | Re-inspected, exact-revision inventory of actual family, publication, query/delivery, replay, identity, access and World-cut verification contracts; unsupported paths explicitly excluded | Observation owner for its contracts; World/domain owners for their publication/adoption claims | OPEN — tracked by [Observation #37](https://github.com/biopeia/observation/issues/37); the pinned snapshot is not an approved client contract |
| D. Lab scope reconciliation | Lab #63 disposition reconciled against the accepted frontend boundary; preserve Lab scientific-apparatus scope and account for existing work/evidence | Lab owner; tracked by [Lab #63](https://github.com/biopeia/lab/issues/63) | **RESOLVED — NOT PLANNED** for the superseded general-presentation work; Lab #63 is closed with its disposition recorded. No scientific work or evidence was transferred or discarded by that closure. |
| E. Security and deployment design | Threat model and explicit local/shared/production boundaries, access assumptions, security/operations ownership, exclusions and follow-up gates | Docs design owner and competent security/operations authority; tracked by [Docs #167](https://github.com/biopeia/docs/issues/167) | OPEN — proposal drafted and independently reviewed on PR #168; no competent security/operations authority has been named and no target profile is accepted. Implementation start and deployment remain unauthorized. |

The Architecture Owner approved the design package on 2026-10-13 after the bounded independent review. Gate A is resolved. Gate D is resolved as stated above. Gates C and E remain implementation-start blockers and must be closed or explicitly bounded by their competent owners. The Architecture Owner has authorized implementation prospectively but explicitly deferred its start; this plan does not grant permission to begin development now. A separate explicit Owner start instruction is still required after the remaining readiness gates are satisfied.

Earlier independent reviews of candidates `3c4f20ff4f98d0b61bfdc77e6e81b68d9e559a02` and `ae1784f1b15c9a9208587f0788259f031aba3343` remain historical records. The bounded review is recorded against `b34c39b77af7be7387fba8f3e54a9b56e6c2cb19` in [PR comment #6143323876](https://github.com/biopeia/docs/pull/165#issuecomment-6143323876), and the later exact-head delta is recorded in [PR comment #6143396043](https://github.com/biopeia/docs/pull/165#issuecomment-6143396043). The review is separate from the Architecture Owner's acceptance and prospective implementation authorization recorded in [Docs #166](https://github.com/biopeia/docs/issues/166#issuecomment-6144222674).

## 4. Source-backed Observation baseline

The UX specification records a discovery snapshot from `biopeia/observation` at `1456df093e4ac28032d956e4df30957f0bf87cec` (2026-10-13). That snapshot found a semantic claim model and bounded in-process plane, and partial readiness for finite scalar-field and BodyPose mappings. Subsequent merged work completed the bounded producer-side path for owner-authorized post-commit publication and World committed-cut verification (Observation #26/#28 and World #105/#106; see the completion evidence in Observation #26). This does not establish a browser-readable consumer/access contract: browser/network access, authentication, query, and cross-restart replay remain unsupported or unapproved. No full Environment-to-receptor-to-Modality-to-Organism family is established. Observation #37 owns the exact-current-source inventory and owner disposition; the historical snapshot must not be presented as current-source approval.

These are inspection results at a pinned revision, not permanent claims about current `main` and not approval of a frontend contract. Before implementation, the Observation owner must refresh the inventory against exact current source revisions and explicitly approve the client-consumable contracts and access boundary. A frontend issue may consume only capabilities established by that review. Missing capability means exclude/disable the function truthfully, not create a mock or an undocumented adapter that supplies missing semantics.

## 5. Implementation authorization gates

The Architecture Owner prospectively authorized implementation but explicitly deferred its start. No application implementation begins until all applicable gates below have evidence and competent approval **and** the Owner gives a separate start instruction:

### 5.1 Constitutional and repository gate

- ADR-0113 is explicitly accepted or an alternative decision is recorded.
- The design register records the decision and lifecycle; ADR-0102 is indexed with its precise disposition without rewriting history.
- Docs #164/PR #165 and Lab #63 are reconciled to the accepted boundary: the general-purpose presentation application belongs to the independent Frontend design, while Lab retains scientific apparatus and evidence responsibilities. Lab #63 is closed as not planned; see its disposition comment.
- Classify Lab-specific scientific tooling versus general frontend presentation using ADR-0113's operation-based criteria; split mixed capabilities by operation and account for existing Lab work/evidence before re-scope.
- Architecture Owner has authorized the target boundary for future implementation; start remains deferred and requires a separate explicit instruction.
- Repository owner, release owner and security/operations responsibility for `biopeia/frontend` are named before repository creation or external deployment; these roles are not assigned by this plan.

### 5.2 Observation and domain-contract gate

- Exact source revisions and owner-approved contracts are identified for each first-release feature.
- Contracts preserve the ratified Observation Semantic Model: authority, typed subject, epistemic basis, domain time/revision, provenance, availability, family revision, units/frame where applicable, coherence and delivery guarantees.
- World-side evidence is required before presenting a cut as World-committed or coherent.
- No frontend UI join is treated as domain identity linkage or causal evidence.
- For any unsupported feature, its issue either removes the feature from the release scope or blocks it until the owner publishes the needed contract.

### 5.3 Security and deployment gate

- Complete and review the proposed threat model / deployment-boundary design in [Docs #167](https://github.com/biopeia/docs/issues/167); a documentary proposal and independent review do not themselves constitute competent security/operations acceptance, authorize implementation start or authorize deployment.
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

The entries below are work packages to track or reconcile in the owning repositories after the relevant parent issues are reviewed. Linked issues are coordination records, not implementation authorization. Reuse [Docs #164](https://github.com/biopeia/docs/issues/164), [Docs #166](https://github.com/biopeia/docs/issues/166), [Observation #37](https://github.com/biopeia/observation/issues/37), [Docs #167](https://github.com/biopeia/docs/issues/167) and [Lab #63](https://github.com/biopeia/lab/issues/63) rather than creating duplicates.

| Package | Owning repository | Dependency | Completion evidence |
|---|---|---|---|
| Constitutional application boundary and ADR disposition | `docs` | Architecture Owner decision | Accepted/rejected ADR record; ADR-0102 and design-register status reconciled |
| Lab #63 responsibility reconciliation | `lab` | Constitutional disposition | **Resolved:** Lab #63 closed as not planned for superseded general-presentation work; Lab scientific apparatus and evidence custody remain in scope under their existing contracts. |
| Approved Observation consumer contract inventory — [Observation #37](https://github.com/biopeia/observation/issues/37) | `observation` with affected domain owners | Current source inspection; no schema assumption | Exact revisions, supported families/publication/read path/access semantics, World verification and exclusions approved by competent owners |
| Frontend security/access and deployment design — [Docs #167](https://github.com/biopeia/docs/issues/167) | `docs` plus named operations/security owner | Target deployment context identified | Threat model and explicit local/shared/production access decisions approved |
| Frontend repository bootstrap and shell | `frontend` once created | Remaining applicable readiness gates 5.1–5.4; separate explicit Owner start instruction | Governed repository, CI, locked toolchain, read-only shell, empty/denied states; no fabricated production records |
| First supported read-only feature slice | `frontend` + `observation` | Approved contract for that feature | Exact-source end-to-end rendering, provenance inspection and negative-state tests |
| Spatial visualization | `frontend` + relevant domain owners | Approved spatial family, frames and geometry/pose linkage | Claim-to-renderer-to-inspector trace; non-3D parity; unsupported cases fail truthfully |
| Release and production deployment | `frontend` and named operations owner | Security, accessibility, performance and integration acceptance | Operational runbook, access verification, release review and known-limitations report |

Any child issue must state the exact missing evidence/decision, accountable owner, repository, dependency, acceptance criteria, applicable independent review and closure trigger. Do not create a child for a capability that is explicitly excluded from v1.

## 7. Decision and status transitions

1. **Design proposed:** superseded for this package by the Owner's design approval recorded 2026-10-13.
2. **Constitutional decision accepted:** ADR-0113 is accepted; its partial supersession of ADR-0102 is limited to the general-purpose Biopeia TARGET frontend allocation.
3. **Design approved:** the Architecture Owner approved the design package after bounded independent adversarial review. This does not imply that consumer contracts or the security/deployment target are ready.
4. **Implementation prospectively authorized, start deferred:** authorization exists, but no work may begin until Gates C and E and the applicable provisions in 5.1–5.5 are evidenced/approved and a separate explicit Owner start instruction is issued. Gate D is resolved as a migration/reconciliation item; its closure does not authorize implementation or transfer Lab responsibilities.
5. **Implementation accepted:** each implemented feature passes its own technical and integration acceptance. Release/deployment remains separate and requires its own authorization.

Lifecycle updates belong in the canonical design register and decision records. Project #1 is coordination only.

## 8. Out of scope

This plan does not select an Observation API/schema/transport/authentication/deployment, create or modify a frontend repository, authorize runtime controls, authorize experimental execution, accept evidence, claim browser access exists, or establish causal replay. The approved design's technology and visual details remain recommendations where explicitly labeled as such; they are not substitutes for the contracts and operational decisions in the readiness gates. No legacy Symbiont code or backward compatibility is permitted or required.

## References

- [Biopeia Frontend v1 architecture design](biopeia-frontend-v1.md)
- [Biopeia Frontend v1 UX specification](biopeia-frontend-ux-spec-v1.md)
- [Biopeia Frontend v1 visual design](biopeia-frontend-visual-design-v1.md)
- [Accepted ADR-0113 — Independent Frontend and Lab Presentation Boundary](../../adr/ADR-0113-independent-frontend-and-lab-boundary.md)
- [ADR-0078 — Observation is causally passive](../../adr/ADR-0078-observation-is-causally-passive.md)
- [ADR-0100 — Observation capability and evidence custody](../../adr/ADR-0100-observation-capability-and-evidence-custody.md)
- [ADR-0101 — Operator Control](../../adr/ADR-0101-operator-control.md)
- [ADR-0102 — Lab](../../adr/ADR-0102-lab.md)
- [Docs #164](https://github.com/biopeia/docs/issues/164), [Docs #166](https://github.com/biopeia/docs/issues/166), [Observation #37](https://github.com/biopeia/observation/issues/37), [Docs #167](https://github.com/biopeia/docs/issues/167), [Lab #63](https://github.com/biopeia/lab/issues/63), [merged Docs PR #165](https://github.com/biopeia/docs/pull/165)
