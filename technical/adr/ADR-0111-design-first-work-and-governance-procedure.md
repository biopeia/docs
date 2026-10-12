---
id: ADR-0111
title: "Design-First Work and Governance Procedure"
document_type: adr
owner: biopeia-project-owner
created: 2026-10-12
language: en
document_version: 1
---

# ADR-0111 — Design-First Work and Governance Procedure

## Status

- **Status:** PROPOSED — awaiting explicit Architecture/Repository Owner decision.
- **Work class:** `ORDINARY` (proposed; see rationale below).
- **Operational risk:** `MEDIUM` (proposed; governance-enforcement impact requires independent review where applicable).
- **Decision authority:** Architecture/Repository Owner for the shared operational workflow. A constitutional approval gate applies only if the decision is changed to alter a protected constitutional invariant or authority boundary.
- **Decision requested:** Accept, revise or reject this ADR and its linked design. This proposal is not a decision, ratification, implementation authorization or experiment authorization.

## Context

Biopeia already has a ratified execution contract, risk-proportional review policy, repository ownership rules and Project #1 operating procedure. The Topic-first proposal in [`.github-private#41`](https://github.com/biopeia/.github-private/issues/41) and the Design-first design in [Docs design PR #131](https://github.com/biopeia/docs/pull/131) identified complementary concerns but risked reading as two competing procedures.

The design was revised in [Docs PR #132](https://github.com/biopeia/docs/pull/132), merged as `c79be2dc42eeb1e85fa197634fc2c992a89cb918`. The revision makes topic intake and design-first execution stages of one lifecycle, and clarifies that cross-domain scope alone does not establish a constitutional classification. The design remains proposed in the Docs registry.

Current normative sources distinguish class from operational risk; reserve constitutional decisions to the Architecture Owner; and require competent-authority decisions to be explicit rather than inferred from review, labels, CI or Project state. This ADR proposes to adopt a shared procedure without changing those authorities or domain semantics.

## Decision proposed

Adopt the [Design-First Work and Governance Procedure v1](../design/governance/design-first-work-and-governance-procedure-v1.md) as Biopeia's shared operational procedure, subject to the limits in this ADR.

The procedure establishes that:

1. Every new concern has a traceable owning Issue recording purpose, scope, owner, affected repository/domain and next decision or evidence needed. Lightweight work may include its specification in that Issue; a separate design document is not universally required.
2. Triage selects the applicable existing governance class and operational risk from actual impact. It does not introduce a competing work taxonomy or permit an executor to downgrade controls.
3. Research and protocol preparation may precede design acceptance within their existing authorization limits. Neither activity authorizes experiment execution, protected changes or implementation beyond scope. Existing category authorizations remain bounded by their own policy.
4. A standalone Issue is sufficient for a self-contained task. A coordinating parent with related subissues is used when independent deliverables, dependencies or cross-repository integration require it. Parent closure requires its own integration acceptance.
5. Designs describe proposals and impacts; ADRs record durable decisions; DNs record material local/reversible decisions; Issues define and coordinate work; PRs carry repository-scoped changes and evidence; scientific records retain evidence and scientific disposition.
6. Technical, integration and scientific acceptance remain distinct. CI, review, merge, Project status and closure do not imply a scientific conclusion or acceptance of a larger deliverable.
7. Project #1 remains an operational coordination view. Its workflow, status, closure and archive behavior must be assessed against existing live settings before any changes; this ADR changes no live setting.
8. Markdown artifacts created for this procedure use the proposed common frontmatter defined in the linked design and eventual templates. Their lifecycle authorities remain in their designated canonical sources.
9. Emergencies may use the bounded response and follow-up path in the design; they do not waive constitutional restrictions, scientific authorization, repository protections or review/merge gates.

## Classification and authority rationale

### Proposed work class: `ORDINARY`

The proposed procedure governs work coordination and evidence/decision traceability within existing authority boundaries. It does not change domain ownership, scientific interpretation, protected `FROZEN` evidence, experiment authorization, or constitutional invariants. Under the existing Agent Work Contract, those effects would require a stronger class and their designated authority. Cross-domain scope, by itself, is not sufficient to classify this proposal as `CONSTITUTIONAL`.

If the owner determines that the adopted text changes a protected invariant or authority boundary, the affected decision must be reclassified and the constitutional approval gate applied; this ADR cannot override that requirement.

### Proposed operational risk: `MEDIUM`

A shared procedure can materially affect governance enforcement once adopted and implemented. The ratified risk policy therefore calls for independent review when a candidate materially affects governance enforcement. This ADR changes no enforcement setting or code; implementation candidates must be assessed against their exact diffs and reviewed under that policy before merge when its threshold is met. Risk does not change the work class or transfer decision authority.

### Proposed decision authority

The existing shared Agent Work Contract is ratified by the Architecture/Repository Owner, and the Topic-first proposal requires approval by the responsible human. Accordingly, this proposal requests an explicit Architecture/Repository Owner decision on adoption of the shared operational procedure. That request does not claim authority to change any domain-owned contract or scientific policy; any such change requires its own competent authority.

## Alternatives considered

- **Require a parent Issue for every concern:** rejected as the default because it duplicates a lightweight task's own scope and acceptance contract without adding coordination value. A parent remains required when multiple deliverables, dependencies or repositories need integration.
- **Require a separate design document for every task:** rejected as disproportionate. Lightweight work may be specified in its Issue while retaining traceability and applicable controls.
- **Treat cross-domain scope as automatically `CONSTITUTIONAL`:** rejected because existing classification is based on protected impact, and cross-domain scope alone does not demonstrate an invariant or authority-boundary change.
- **Merge Topic-first and Design-first into one undifferentiated artifact:** rejected. Their functions remain distinct: an Issue is the universal intake/execution record; a design is a separate proposal when scope, alternatives or impact warrant one.
- **Implement automation or change Project #1 before ratification:** rejected. Automation and live settings require separate, scoped Issues, verification and authorization after a decision.

## Consequences if accepted

- The linked design's document status may be updated to `approved` only with a reference to this accepted ADR; implementation status and architecture scope remain separate registry fields.
- Implementation work must be derived from the design impact map into owning-repository Issues and added to Project #1. Use a parent only where integration needs it; split independently verifiable parts into linked subissues.
- The initial implementation should prioritize templates, frontmatter/relation validation and clearly documented state semantics. Project automation should be changed only after live settings and representative cases are tested.
- A pilot should include lightweight, cross-domain and scientific work without blocking work already underway. A seven-day review Issue should be created at adoption to measure overhead, decision latency, traceability gaps, automation errors and review delays.
- This ADR does not itself create those Issues, modify Project #1, authorize experiments, or authorize code or policy enforcement changes.

## Decision record

No decision has been recorded yet. The Architecture/Repository Owner must record one of `ACCEPTED`, `REVISE` or `REJECTED`, its rationale and date here through a reviewed update. Until then, this ADR and the linked design remain proposals, and implementation remains unauthorized.

## References

- Governance decision Issue: [biopeia/.github-private#43](https://github.com/biopeia/.github-private/issues/43)
- Parent Topic-first proposal: [biopeia/.github-private#41](https://github.com/biopeia/.github-private/issues/41)
- Design document: [Design-First Work and Governance Procedure v1](../design/governance/design-first-work-and-governance-procedure-v1.md)
- Initial design proposal: [biopeia/docs#131](https://github.com/biopeia/docs/pull/131)
- Topic/design reconciliation: [biopeia/docs#132](https://github.com/biopeia/docs/pull/132)
- Canonical execution contract: `biopeia/.github-private/workflow/agent-work-contract-v1.md`
- Risk policy: `biopeia/.github-private/workflow/review-policy.md`
- Project #1 governance: `biopeia/.github-private/workflow/project-1-governance.md`
