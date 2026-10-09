# ADR-0088 — Lifecycle event ontology

> **Provenance.** Transcription of `AD-0014` from the sealed architecture audit
> dossier of `alessbarb/symbiont-lab` (archive `.audit.zip`, SHA-256
> `ff258afcb1c80b9feefacc28575d1e5ccd5f15c062dd36499498747df4d57df2`): the `AD-0014` row of `.audit/registers/decisions.md` (SHA-256 `0c03a0d438ff4a38337c683ecd4649ce3862cf600b6f3e2f2baf1ab421e5d43d`).
> The decision, status and ratification texts below are verbatim. The source row has no title; the title above was written for this record.
> Section headings were added. Identifiers of the form `AD-NNNN` inside the
> text are the source identifiers; see References for the corresponding
> records here. Identifiers of the form `ADR-NNNN` up to `ADR-0072` name the
> historical decision records of `symbiont-lab`, which were not copied.

## Status

- **Status:** ACCEPTED
- **Type:** CONSTITUTIONAL NORMATIVE
- **Source identifier:** AD-0014

## Decision

TARGET lifecycle ontology keeps `BODY_DEATH`, `ORGANISM_DORMANCY`, `WORLD_PRESENCE_TERMINATION`, `ORGANISM_DEATH`, `REEMBODIMENT`, `OFFSPRING_DEATH`, and `LINEAGE_TERMINATION` distinct. Body nonviability belongs primarily to EMBODIMENT and ends the active body/EmbodimentEpisode, not automatically the longitudinal Organism. The same Organism may persist dormant without active embodiment and later re-embody in a new episode, preserving identity and contract-relevant longitudinal state; this is not offspring creation or an automatic reset, and not every body-death event is necessarily recoverable. World may coordinate/commit World-presence and shared lifecycle consequences but cannot infer final Organism death from body death, runtime shutdown, checkpoint absence, or administrative removal. Organism death is a distinct terminal identity transition resolved under an explicit lifecycle contract involving continuity state, body viability, recoverability and authorized rules; a dead identity cannot later resume as the same Organism. Offspring death is not lineage termination. Scientific survival/mortality/selection/fitness/lifespan measures must name the event ontology. Roles: EMBODIMENT determines body viability; ORGANISM owns longitudinal identity/continuity; WORLD coordinates presence and commits resolved shared events; LAB observes or explicitly intervenes experimentally.

## Ratification and evidence

Ratification authority: Architecture Owner. EV-0302/0303/0322/0333/0339/0340/0341; ADR-0013/0035; AD-0007. TARGET ontology resolved. CURRENT source routes remain distinct and are not retroactively presumed compliant; no finding is created without demonstrated contract applicability and mismatch. No code or dynamic changes.

## References

- AD-0007 is [ADR-0081 — The canonical Organism is longitudinal](ADR-0081-the-canonical-organism-is-longitudinal.md)
