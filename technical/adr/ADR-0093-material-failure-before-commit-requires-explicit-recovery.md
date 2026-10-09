# ADR-0093 — Material failure before commit requires explicit recovery

## Provenance

- **Original decision:** AD-0019
- **Source:** sealed Biopeia Architecture v1 audit dossier of `alessbarb/symbiont-lab`,
  the `AD-0019` row of `.audit/registers/decisions.md` (SHA-256 `0c03a0d438ff4a38337c683ecd4649ce3862cf600b6f3e2f2baf1ab421e5d43d`)
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

A material failure between causal-transition start and completion of COMMIT, including causal journal publication, places the runtime in durable `RECOVERY_REQUIRED`, attributed to the failed transition and visible to readers. Ordinary execution cannot resume implicitly on a later tick. Before continuation, an explicit verifiable recovery transition must establish coherent, identifiable, recoverable state (e.g. successful rollback, coherent checkpoint restore, validated reconstruction or equivalent). Restart alone is not recovery. Full rollback is not mandated. Organism-private recovery semantics remain Organism-defined under AD-0018. Whether failure of one Organism requires the entire multi-organism World or only that subject to enter recovery is reserved to Pass 15. Observation/presentation/telemetry failure alone is not material; persistence failure after COMMIT remains for Pass 15.

## Ratification and evidence

Ratification authority: Architecture Owner. EV-0344; AD-0009/0018 and DYN-OP0020 evidence. This defines TARGET, not CURRENT conformance. No code/fault injection or runtime modification authorized.

## Register scope

The decisions register opens with a statement that applies to every
ratification in it, reproduced verbatim.

> Architecture Owner ratifications in this register are normative for TARGET. They do not assert CURRENT compliance. See EV-0249 and EV-0252 for ratification records and constitutional-text reconciliation.

## References

- AD-0009 is [ADR-0083 — Causal cycles have explicit commit semantics](ADR-0083-causal-cycles-have-explicit-commit-semantics.md)
- AD-0018 is [ADR-0092 — Organism owns the meaning of its private longitudinal state](ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md)
