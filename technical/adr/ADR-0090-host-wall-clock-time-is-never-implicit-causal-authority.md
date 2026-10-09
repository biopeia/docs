# ADR-0090 — Host wall-clock time is never implicit causal authority

> **Provenance.** Transcription of `AD-0016` from the sealed architecture audit
> dossier of `alessbarb/symbiont-lab` (archive `.audit.zip`, SHA-256
> `ff258afcb1c80b9feefacc28575d1e5ccd5f15c062dd36499498747df4d57df2`): the `AD-0016` row of `.audit/registers/decisions.md` (SHA-256 `0c03a0d438ff4a38337c683ecd4649ce3862cf600b6f3e2f2baf1ab421e5d43d`).
> The decision, status and ratification texts below are verbatim. The source row has no title; the title above was written for this record.
> Section headings were added. Identifiers of the form `AD-NNNN` inside the
> text are the source identifiers; see References for the corresponding
> records here. Identifiers of the form `ADR-NNNN` up to `ADR-0072` name the
> historical decision records of `symbiont-lab`, which were not copied.

## Status

- **Status:** ACCEPTED
- **Type:** CONSTITUTIONAL NORMATIVE
- **Source identifier:** AD-0016

## Decision

Host wall-clock time is never implicit causal authority. ADR-0042's listed exceptions are not inherited; each requires individual classification against this rule. Causal times (as applicable `T_world`, `T_physics`, `T_organism`, `T_embodiment`, `T_body`, generation) must be explicit and distinct; which authority advances or orders them is reserved to Pass 15. Host time remains permitted for performance, infrastructure scheduling, timeouts and operator telemetry, but not implicit biological causation. If an Organism can perceive host time/load/its own tick latency, it enters only as an external phenomenon through Modality transduction as an opaque Organism signal. Host-executed asynchronous work (including private-model training/adoption/activation) may enter causal state only on a causally determined tick or as such an external phenomenon.

## Ratification and evidence

Ratification authority: Architecture Owner. EV-0344. Verify CURRENT wall-clock paths and each ADR-0042 exception independently; do not infer non-conformance. This does not select time ownership/ordering or runtime topology.

## Register scope

The decisions register opens with a statement that applies to every
ratification in it, reproduced verbatim.

> Architecture Owner ratifications in this register are normative for TARGET. They do not assert CURRENT compliance. See EV-0249 and EV-0252 for ratification records and constitutional-text reconciliation.
