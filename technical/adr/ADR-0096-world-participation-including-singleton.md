# ADR-0096 — World participation, including singleton

## Provenance

- **Original decision:** AD-0022
- **Source:** sealed Biopeia Architecture v1 audit dossier of `alessbarb/symbiont-lab`,
  `.audit/ARCHITECTURE_OWNER_TANDA2_RATIFICATION.md` (SHA-256 `bb70560e0eedffab619199da9b804de15f7b9b4d30c6dc4757b703d5312939c9`), section `AD-0022`, and its row in `.audit/registers/decisions.md` (SHA-256 `0c03a0d438ff4a38337c683ecd4649ce3862cf600b6f3e2f2baf1ab421e5d43d`)
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

Every causally active embodied Organism participates in a World causal context, including at `N=1`. A singleton World may be thin, but includes World identity, causal time/order, causal commit, presence and a recovery boundary. This does not require a heavyweight population runtime or reuse of CURRENT `WorldRuntimeState`.

### Summary in the decisions register

Every causally active embodied Organism participates in a World causal context, including N=1. A singleton context may be thin but has identity, causal order/time, commit, presence and recovery boundary; CURRENT need not reuse WorldRuntimeState.

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
- AD-0024 is [ADR-0098 — Physical substrate and causal integration](ADR-0098-physical-substrate-and-causal-integration.md)
- AD-0025 is [ADR-0099 — Modality contract/library](ADR-0099-modality-contract-library.md)
- AD-0032 is [ADR-0106 — Hybrid multi-owner persistence](ADR-0106-hybrid-multi-owner-persistence.md)
- AD-0034 is [ADR-0108 — Reproduction and causal entropy](ADR-0108-reproduction-and-causal-entropy.md)
- AD-0036 is [ADR-0110 — Repository consequence and dependency direction](ADR-0110-repository-consequence-and-dependency-direction.md)
