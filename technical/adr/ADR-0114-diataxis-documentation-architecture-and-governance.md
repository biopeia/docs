---
id: ADR-0114
title: "Diátaxis Documentation Architecture and Governance"
document_type: adr
owner: biopeia-architecture-owner
created: 2026-10-16
language: en
document_version: 1
---

# ADR-0114 — Diátaxis Documentation Architecture and Governance

## Status and authority

- **Status:** ACCEPTED — adopted by the Biopeia Architecture Owner on 2026-10-16.
- **Work class:** `CONSTITUTIONAL` (defines repository corpus architecture, document authority classification, and publication boundaries).
- **Operational risk:** `MEDIUM` (structural reorganization of canonical docs without altering domain runtime contracts or approved decisions).
- **Decision authority:** Biopeia Architecture Owner.
- **Decision date:** 2026-10-16.
- **Decision evidence:** Comprehensive documentation audit of 2026-10-16 ([diataxis-documentation-audit-2026-10-16.md](../inventory/diataxis-documentation-audit-2026-10-16.md)).
- **Implementation authorization:** Phased execution authorized under governance phases P0 through P5. Phase P0 ratified herein.

## Context

The audit of working publications (Biopeia Master, 237 pages across 57 chapters; Technical Reference, 88 pages across 3 narrative chapters and 11 generated sections) at revision `docs@7642ebe` identified structural mixing of communication purposes:

1. Explanatory prose, formal technical references, and code implementation audits are blended inside single chapters (DOC-01, DOC-05).
2. The current publishing model (`tools/publication/model.py`) restricts chapter roots strictly to `("explanation/", "reference/")`, leaving no structured home for executable tutorials or operational how-to guides (DOC-03, DOC-06).
3. Redundancy exists across current volumes (e.g., `explanation/cross-domain/observation-presentation-boundary.md` appearing in both Master and Reference) (DOC-02).
4. Concrete implementation audits tied to transient git revisions are presented as permanent architectural truths rather than timestamped evidence (DOC-05).

Biopeia requires a strict separation of purposes—distinguishing what has been decided, what has been implemented, what has been empirically observed, and what remains an open scientific hypothesis—while preserving `biopeia/docs` as the single canonical source of truth.

## Accepted decision

Adopt the Diátaxis documentation framework as the canonical information architecture and governance standard for `biopeia/docs`, organized into four distinct communicative quadrants and a transversal traceability layer:

1. **Four Diátaxis Quadrants:**
   - **Tutorials (`tutorials/`):** Learning-oriented, step-by-step executable experiences starting from verified baselines (e.g., M1 simulation run, domain identification).
   - **How-to Guides (`how-to/`):** Task-oriented, problem-solving procedures for operators, developers, and researchers, derived strictly from implemented and verifiable interfaces.
   - **Reference (`reference/`):** Information-oriented technical specifications, canonical component catalogs, cross-domain contracts, parameters, state structures, and schemas.
   - **Explanation (`explanation/`):** Understanding-oriented conceptual architecture, scientific foundations, domain boundaries, constitutional rationale, and candidate hypotheses.

2. **Transversal Governance Layer:**
   - Registers (`registry/`), Architecture Decision Records (`technical/adr/`), Design Notes (`technical/design/`), and versioned Implementation Audits (`audits/` or `technical/inventory/`) constitute a transversal governance and evidence layer.
   - They feed all four quadrants without constituting an informal fifth Diátaxis quadrant.

3. **Three Non-Negotiable Guarantees:**
   - **No change of decision authority:** Restructuring or moving text shall not modify, supersede, or dilute any accepted ADR or ratified design.
   - **No inflation of evidence:** Relocating an implementation test, metric, or code sample to a reference or tutorial shall not elevate its epistemic standing into a validated scientific claim.
   - **Strict provenance preservation:** Every published artifact and document must retain its lineage to the exact source commit, unit, test, or registry entry.

4. **Publication Strategy:**
   - Evolve publications from monographic mixed editions into four dedicated volumes aligned with the Diátaxis quadrants:
     - Volume I: Foundations and Architecture (*Explanation*)
     - Volume II: Technical Reference (*Reference*)
     - Volume III: Operations and Development Guide (*How-to*)
     - Volume IV: Guided Learning (*Tutorials*)
   - Eliminate cross-volume chapter duplication by replacing repeated narrative chapters with generated technical summary cards in reference volumes.

## Execution plan

Phased transition roadmap:

- **P0 — Architectural Ratification (this record):** Formalize the Diátaxis architecture, boundaries, and governance constraints.
- **P1 — Exhaustive Inventory and Classification Matrix:** Map all 57 existing chapters and mixed sections to target quadrants without moving physical files prematurely.
- **P2 — Publishing Model and Validation Expansion:** Update `tools/publication/model.py`, `registry/schema.yaml`, `tools/render_indexes.py`, and CI test suites to validate all four quadrants.
- **P3 — Corpus Refactoring:** Incrementally split and migrate mixed chapters (prioritizing Organism, World, and cross-domain boundaries) with strict content fidelity.
- **P4 — How-to and Tutorial Construction:** Author verified procedural and tutorial tracks backed by automated integration tests.
- **P5 — Four-Volume Publication and Sunset:** Validate deterministic PDF generation of all four volumes and decommission legacy composite manifests.

## Consequences

- The canonical repository `biopeia/docs` remains the single source of truth; no fragmentation into auxiliary doc repositories.
- `CHAPTER_ROOTS` and validation tools will require progressive updates during Phase P2 to recognize `tutorials/` and `how-to/`.
- Authors and automated agents must adhere to strict quadrant-specific style guidelines and mandatory Diátaxis metadata tags upon full rollout.
- Existing publication pipelines remain operational during the transition until Phase P5 validation is complete.

## References

- Comprehensive Documentation Audit of 2026-10-16: [`technical/inventory/diataxis-documentation-audit-2026-10-16.md`](../inventory/diataxis-documentation-audit-2026-10-16.md)
- Diátaxis Framework: [diataxis.fr](https://diataxis.fr/)
- [ADR-0111 — Design-First Work and Governance Procedure](ADR-0111-design-first-work-and-governance-procedure.md)
- [ADR-0113 — Independent Frontend and Lab Presentation Boundary](ADR-0113-independent-frontend-and-lab-boundary.md)
