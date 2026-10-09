# ADR-0110 — Repository consequence and dependency direction

## Provenance

- **Original decision:** AD-0036
- **Source:** sealed Biopeia Architecture v1 audit dossier of `alessbarb/symbiont-lab`,
  `.audit/ARCHITECTURE_OWNER_TANDA2_RATIFICATION.md` (SHA-256 `bb70560e0eedffab619199da9b804de15f7b9b4d30c6dc4757b703d5312939c9`), section `AD-0036`, and its row in `.audit/registers/decisions.md` (SHA-256 `0c03a0d438ff4a38337c683ecd4649ce3862cf600b6f3e2f2baf1ab421e5d43d`)
- **Source integrity:** archive `.audit.zip`, SHA-256 `ff258afcb1c80b9feefacc28575d1e5ccd5f15c062dd36499498747df4d57df2`,
  recorded in the source repository as `BIOPEIA_ARCHITECTURE_V1_AUDIT_BASELINE`
- **Original authority:** Architecture Owner
- **Original acceptance date:** 2026-10-09
- **Transformation:** DOCUMENTARY NORMALIZATION ONLY
- **Semantic changes:** NONE

The decision, status and ratification texts below are verbatim from the source.
The record number, the section headings, this provenance section and the
References list were added. Identifiers of the form `AD-NNNN` inside the text
are the source identifiers. Identifiers of the form `ADR-NNNN` up to `ADR-0072`
name the historical decision records of `symbiont-lab`, which were not copied.

## Status

- **Status:** ACCEPTED
- **Type:** CONSTITUTIONAL NORMATIVE

## Decision

Semantic authority and repository count are not identical. Migration planning uses this TARGET classification:

| Area | Semantic classification | Independent repository candidate |
| --- | --- | --- |
| Organism | Authority | Yes |
| Embodiment | Authority | Yes |
| Environment | Authority | Yes |
| World | Authority | Yes |
| Modality | Contract/library | Yes, if independently versioned/reused |
| Observation | Passive contract/capability | Yes, if needed to prevent World↔Lab coupling |
| Lab | Apparatus/application | Yes |

A seven-repository topology remains valid and likely, but is not “seven repositories = seven authorities”; it is four authority repositories, two reusable contract/capability candidates and one scientific apparatus/application candidate. Final extraction rehearsal must validate Modality/Observation repo merit. No repositories are created or code moved by this decision.

As a design constraint, use neutral contracts/data structures to avoid concrete peer import cycles. Organism, Embodiment and Environment expose explicit projections/contracts to World; Modality supplies transduction without interpretation ownership; Observation consumes passive projections/events without writeback; Lab composes authorities and issues explicit interventions. This is not an exact import graph or final API.

### Summary in the decisions register

Migration planning distinguishes four semantic-authority repositories (Organism, Embodiment, Environment, World), two reusable contract/capability repository candidates (Modality, Observation), and one apparatus/application candidate (Lab). Seven repositories remain valid/likely but are not seven authorities; final extraction rehearsal validates Modality/Observation repo merit. Dependency direction uses neutral contracts to avoid peer cycles. No migration is authorized.

## Ratification and evidence

Ratification authority: Architecture Owner. EV-0436; Pass 15 bounded evidence EV-0434/0435; related prior ADs noted in `.audit/ARCHITECTURE_OWNER_TANDA2_RATIFICATION.md`. Defines TARGET only; no CURRENT compliance, final APIs/storage format, repository migration, gate closure or Pass 16B authorization.

## Ratification record

The source ratification covers AD-0021 to AD-0036 together. Its opening and
closing statements apply to this decision and are reproduced verbatim.

> Audit baseline: `cef998a55aae32ed8b2f7373079c11667b01e915`  
> Ratification date: 2026-10-09  
> Decision type: `CONSTITUTIONAL NORMATIVE`  
> Status: `ACCEPTED`  
> Ratification authority: `Architecture Owner`
>
> This ratification defines TARGET semantics/contracts after Pass 15 and independent review REV-0026…REV-0030. It does not assert CURRENT compliance.
>
> It does **not** authorize repository migration, destructive cut-over, final API/storage formats, Gate A/B/C closure, or Pass 16B. It does not modify the pinned Constitution or CURRENT code. Historical document reconciliation and implementation/conformance work remain separate.

> Pass 15 is complete as bounded falsification. The accepted decisions above replace recommendation-only status in the Tanda 2 packet. Preserve immutable REV-0026…REV-0030 and their prior `PARTIALLY_ACCEPTED` resolutions; this ratification does not rewrite reviewer claims. The bounded results informing this decision are EV-0434/0435; this record is EV-0436. REV-0026's solver coupling is addressed by AD-0024; REV-0027 by AD-0032; REV-0028 by AD-0034; REV-0029 by AD-0025; REV-0030 by AD-0022. No review is silently erased or promoted to authority.
>
> Current code compliance remains separate. FND-0022 and OP-0019 retain the bounded current reproduction evidence; other conformance work remains in existing findings/OPs. No finding is closed by target ratification alone. Gate A/B/C remain open. Pass 16B, migration, destructive cut-over and functional code changes remain unauthorized.

## References

- AD-0021 is [ADR-0095 — Surviving semantic authorities](ADR-0095-surviving-semantic-authorities.md)
- AD-0022 is [ADR-0096 — World participation, including singleton](ADR-0096-world-participation-including-singleton.md)
- AD-0024 is [ADR-0098 — Physical substrate and causal integration](ADR-0098-physical-substrate-and-causal-integration.md)
- AD-0025 is [ADR-0099 — Modality contract/library](ADR-0099-modality-contract-library.md)
- AD-0032 is [ADR-0106 — Hybrid multi-owner persistence](ADR-0106-hybrid-multi-owner-persistence.md)
- AD-0034 is [ADR-0108 — Reproduction and causal entropy](ADR-0108-reproduction-and-causal-entropy.md)
