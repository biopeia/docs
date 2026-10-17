# DOC-018 — Web Publication Evaluation v1

Reviewed against: docs@cc3f4ee53b7e1d73af0a3071cdc391e7ba6b90d5
Review date: 2026-10-17
Scope: evaluate options for navigable, searchable Diátaxis documentation with commit-level provenance
Status: proposed design; no hosting, deployment, access, or implementation decision

## Decision question

What is the lowest-risk publication path that improves navigation across Diátaxis quadrants, domains, contracts, and evidence while preserving Docs as the canonical corpus and respecting private repository access?

This note evaluates the DOC-018 alternatives. It is not an ADR, a deployment plan, an authorization to publish private content, or evidence that a web site exists.

## Current state (verified)

| Capability | Current evidence | Limit |
|---|---|---|
| Canonical corpus and ordered publications | `publication/publications/*.yaml` and `tools/publication/model.py` compose canonical documents and generated sections. | Composition produces document editions, not a web information architecture. |
| Generated navigation | `tools/render_indexes.py` generates local Markdown indexes from manifests and registry data. | The index is not a deployed site or full-text search service. |
| Commit/source references | `tools/publication/references.py` resolves code, tests, issues, and source references to repository revisions and validates available local checkouts. | A link is only useful to a reader authorized for the referenced private repository; build-time resolution is not proof of reader access. |
| Build and delivery | `.github/workflows/publication.yml` builds publication artifacts. | The inspected workflow has no Pages/site deployment step. The build artifact is not a supported public or authenticated web service. |
| Documentation architecture | ADR-0114 accepts the Diátaxis corpus architecture and phased transition. | ADR-0114 does not specify web hosting, audience access, retention, or a search implementation. |

## Requirements and constraints

1. The canonical content remains in `biopeia/docs`; generated output is a projection, never a second authority.
2. Navigation should make the four quadrants, domain, contract, and evidence/provenance discoverable without implying a claim is accepted merely because it is published.
3. Source and issue links must retain exact revision context and clearly disclose private-access requirements.
4. A search index must be derived only from content intended for its audience. It must not expose private code, issue text, artifacts, credentials, or non-published registry material.
5. Deployment audience, authentication, hosting ownership, retention, and operations are unresolved. No public exposure may be inferred from the word “web”.
6. DOC-018 depends on migration/publication reconciliation: Docs #78 conditions the broader publication split on accepted migration closure, and the current critical-path tracker `.github-private#42` remains open. This note does not waive that gate.

## Alternatives

| Option | Benefits | Costs / risks | Assessment |
|---|---|---|---|
| A. Keep document artifacts and improve generated Markdown indexes | Lowest change; preserves current publication pipeline and exact links; no new hosting surface. | Navigation and search remain dependent on repository access and reader tooling; does not meet a browser-native web experience. | Safe fallback; does not fully satisfy DOC-018's web UX objective. |
| B. Generate a self-contained static HTML edition as a build artifact, initially without deployment | Browser-native navigation/search can be evaluated offline; no server or new runtime authority; artifact can be generated from the existing canonical manifests. | Requires a new renderer, security/content review, accessibility and link validation, artifact-lifecycle decision, and reader testing. Build-artifact access/retention properties must be verified before relying on them. | Best bounded prototype candidate, but implementation requires a separate owner start/approval after dependency reconciliation. |
| C. Host an authenticated internal documentation site | Convenient shared browsing/search and central updates. | Adds hosting, identity/access integration, operational owner, content synchronization, retention, incident/security responsibilities, and private-link behavior. No hosting topology or owner is established by inspected ADRs/workflows. | Do not select until access model, operations owner, cost, and migration gate are decided. |
| D. Publish a public site | Broadest reach and simplest reader access. | Repository and evidence references are private; a public build risks exposing content or falsely implying private links are public. No public-disclosure approval exists in this evidence. | Not recommended; no public publication is authorized. |

Cost comparison is qualitative only. No hosting estimate, artifact retention guarantee, or identity-provider capability was verified; those remain inputs to any later implementation decision.

## Proposed bounded path (not yet approved)

1. Preserve A as the current supported state.
2. After the migration dependency and owner start gate are reconciled, evaluate B as an isolated, non-deployed prototype using only the manifests' explicitly included documents.
3. Before any shared or hosted deployment, require a separate owner decision covering audience, authentication, hosting/operations owner, retention, security review, accessible navigation/search, and private-link behavior.
4. Treat public hosting as out of scope unless a competent owner explicitly authorizes a disclosure policy and audits the exact output.

The prototype, if later authorized, should demonstrate navigation from quadrant → domain → document → cited contract/evidence, search over the published corpus only, explicit source revision display, and graceful unavailable/private-link states. Those are proposed evaluation criteria, not implemented requirements.

## Authority and evidence limits

| Claim | Evidence | Type | Limits |
|---|---|---|---|
| Diátaxis is the accepted Docs information architecture and transition is phased. | `technical/adr/ADR-0114-diataxis-documentation-architecture-and-governance.md` | ACCEPTED | Does not select site technology, access model, or deployment. |
| Current manifests and renderer compose canonical documents and indexes. | `publication/publications/*.yaml`, `tools/publication/model.py`, `tools/render_indexes.py` | IMPLEMENTED (source inspection) | This note did not execute a new publication build. |
| The current Publication workflow has no site deployment step. | `.github/workflows/publication.yml` | IMPLEMENTED (source inspection) | Does not prove no external deployment exists; none was evidenced in the inspected repository. |
| A browser-native static artifact could support local navigation and search. | Option analysis in this note | INFERENCE | Requires prototype and user/accessibility testing; not observed or implemented. |
| Public hosting is not authorized by the inspected records. | ADR-0114; ADR-0113 deployment non-selection; private repository/link model | EVIDENCE-BOUNDED | A future competent owner may authorize it after disclosure/access review. |

## References

- [ADR-0114 — Diátaxis Documentation Architecture and Governance](../../adr/ADR-0114-diataxis-documentation-architecture-and-governance.md)
- [ADR-0113 — Independent Frontend and Lab Presentation Boundary](../../adr/ADR-0113-independent-frontend-and-lab-boundary.md) (separate runtime frontend; not the Docs publication system)
- `publication/README.md`
- `publication/publications/`
- `tools/render_indexes.py`
- `tools/publication/references.py`
- `.github/workflows/publication.yml`
- [Docs #278 — DOC-018](https://github.com/biopeia/docs/issues/278)
- [Docs #78 — two publications dependency](https://github.com/biopeia/docs/issues/78)
- [Internal #42 — migration critical path](https://github.com/biopeia/.github-private/issues/42)
