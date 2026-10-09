# ADR-0088 — Lifecycle event ontology

## Provenance

- **Original decision:** AD-0014
- **Source:** sealed Biopeia Architecture v1 audit dossier of `alessbarb/symbiont-lab`,
  the `AD-0014` row of `.audit/registers/decisions.md` (SHA-256 `0c03a0d438ff4a38337c683ecd4649ce3862cf600b6f3e2f2baf1ab421e5d43d`)
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

TARGET lifecycle ontology keeps `BODY_DEATH`, `ORGANISM_DORMANCY`, `WORLD_PRESENCE_TERMINATION`, `ORGANISM_DEATH`, `REEMBODIMENT`, `OFFSPRING_DEATH`, and `LINEAGE_TERMINATION` distinct. Body nonviability belongs primarily to EMBODIMENT and ends the active body/EmbodimentEpisode, not automatically the longitudinal Organism. The same Organism may persist dormant without active embodiment and later re-embody in a new episode, preserving identity and contract-relevant longitudinal state; this is not offspring creation or an automatic reset, and not every body-death event is necessarily recoverable. World may coordinate/commit World-presence and shared lifecycle consequences but cannot infer final Organism death from body death, runtime shutdown, checkpoint absence, or administrative removal. Organism death is a distinct terminal identity transition resolved under an explicit lifecycle contract involving continuity state, body viability, recoverability and authorized rules; a dead identity cannot later resume as the same Organism. Offspring death is not lineage termination. Scientific survival/mortality/selection/fitness/lifespan measures must name the event ontology. Roles: EMBODIMENT determines body viability; ORGANISM owns longitudinal identity/continuity; WORLD coordinates presence and commits resolved shared events; LAB observes or explicitly intervenes experimentally.

## Ratification and evidence

Ratification authority: Architecture Owner. EV-0302/0303/0322/0333/0339/0340/0341; ADR-0013/0035; AD-0007. TARGET ontology resolved. CURRENT source routes remain distinct and are not retroactively presumed compliant; no finding is created without demonstrated contract applicability and mismatch. No code or dynamic changes.

## Register scope

The decisions register opens with a statement that applies to every
ratification in it, reproduced verbatim.

> Architecture Owner ratifications in this register are normative for TARGET. They do not assert CURRENT compliance. See EV-0249 and EV-0252 for ratification records and constitutional-text reconciliation.

## References

- AD-0007 is [ADR-0081 — The canonical Organism is longitudinal](ADR-0081-the-canonical-organism-is-longitudinal.md)
