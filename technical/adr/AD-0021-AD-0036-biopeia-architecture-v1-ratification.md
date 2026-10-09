# Architecture Owner — Pass 15 Tanda 2 Ratification

> **Provenance.** Copied from the sealed architecture audit dossier of
> `alessbarb/symbiont-lab`: archive `.audit.zip`, SHA-256
> `ff258afcb1c80b9feefacc28575d1e5ccd5f15c062dd36499498747df4d57df2`
> (recorded there as `BIOPEIA_ARCHITECTURE_V1_AUDIT_BASELINE`), member
> `.audit/ARCHITECTURE_OWNER_TANDA2_RATIFICATION.md`, member SHA-256
> `bb70560e0eedffab619199da9b804de15f7b9b4d30c6dc4757b703d5312939c9`. The text
> is unchanged. The original is retained in the source repository. The
> decisions, reviews, evidence records, findings and open points it cites by
> identifier (for example AD-0004, AD-0013, AD-0016, AD-0019, REV-0026…REV-0030,
> EV-0434…EV-0436, FND-0022, OP-0019) remain in that dossier and were not copied.

Audit baseline: `cef998a55aae32ed8b2f7373079c11667b01e915`  
Ratification date: 2026-10-09  
Decision type: `CONSTITUTIONAL NORMATIVE`  
Status: `ACCEPTED`  
Ratification authority: `Architecture Owner`

This ratification defines TARGET semantics/contracts after Pass 15 and independent review REV-0026…REV-0030. It does not assert CURRENT compliance.

It does **not** authorize repository migration, destructive cut-over, final API/storage formats, Gate A/B/C closure, or Pass 16B. It does not modify the pinned Constitution or CURRENT code. Historical document reconciliation and implementation/conformance work remain separate.

## AD-0021 — Surviving semantic authorities

Ratified primary semantic authorities: `ORGANISM`, `EMBODIMENT`, `ENVIRONMENT`, `WORLD`. They are distinct and must not be collapsed solely to reduce repository count.

- **Organism** owns longitudinal identity, private cognition, memory, learning, private models, agency, competence, homeostatic regulation, reproductive origination and portable longitudinal state. Other authorities may not semantically inspect or rewrite private state except through an explicit Organism-owned contract.
- **Embodiment** owns concrete body/episode physical and somatic truth as applicable: morphology, energy, temperature, fatigue, damage, structural integrity, viability, body-local calibration and embodiment-episode identity. It does not own Organism identity or shared physical-world resolution merely because bodies participate in it.
- **Environment** owns objective environmental/ecological state and rules as applicable: resources, terrain, hazards, medium properties, ecological conditions/dynamics and spatial environmental state. It is semantically distinct from World; it does not define Organism goals/rewards/meaning.
- **World** owns world identity, active presence, causal ordering, shared interaction resolution, cross-entity coordination, commit, population registry where applicable, lifecycle choreography and global recovery coordination. It does not own Organism-private semantics, Embodiment somatic truth or Environment ecological truth.

## AD-0022 — World participation, including singleton

Every causally active embodied Organism participates in a World causal context, including at `N=1`. A singleton World may be thin, but includes World identity, causal time/order, causal commit, presence and a recovery boundary. This does not require a heavyweight population runtime or reuse of CURRENT `WorldRuntimeState`.

## AD-0023 — Hybrid World

TARGET World is a **Hybrid World**: neither a trivial message router nor owner of every domain's state. It owns shared causal coordination and commit; domain authorities retain semantic state. World coordinates through explicit contracts and projections/tokens. Co-deployment does not merge semantic ownership.

## AD-0024 — Physical substrate and causal integration

Physics3D is a `PHYSICAL SUBSTRATE / ENGINE`, not a semantic authority. Embodiment owns body/somatic state; Environment owns environmental physical conditions; World owns causal integration protocol and decides whether a resolved physical transition becomes committed World state; the physical substrate executes numerical coupled resolution over owner projections. Thus numerical integration executor is distinct from causal transition authority. Do not create a semantic authority solely for the solver.

## AD-0025 — Modality contract/library

Modality is a `CONTRACT / LIBRARY / IMPLEMENTATION CAPABILITY`, not an independent semantic authority on current evidence. It defines transduction between physical/environmental phenomena and opaque signals/effectors, not Organism interpretation. It need not be stateless; state is assigned explicitly: body-local calibration and episode transducer state to Embodiment/episode, learned perceptual adaptation to Organism, medium parameters to Environment, and pure scratch state to non-authoritative implementation. Reconsider authority only if future evidence identifies persistent semantic state without an existing owner.

## AD-0026 — Observation capability and evidence custody

Observation is a `PASSIVE CAPABILITY / BOUNDARY`, not a semantic state authority. Separate runtime projection of authoritative state; transport/presentation as application/infrastructure; and durable scientific evidence/provenance custody as scientific apparatus/governance. Observation can emit facts; Lab/scientific apparatus records durable evidence. AD-0004 remains controlling: Observation is not Operator Control.

## AD-0027 — Operator Control

Operator Control is a `PRIVILEGED INTERVENTION CAPABILITY`, not an independent semantic authority. It may be hosted by Lab/applications. Pause/step/resume/speed/inject commands are explicit attributable requests to the relevant causal authority; World validates/commits requests that change World causality. They must not mutate hidden state through Observation.

## AD-0028 — Lab

Lab is a `SCIENTIFIC APPARATUS / APPLICATION UMBRELLA`, not authority over autonomous life. It may compose experiment definitions, studies, launch/supervision, controls, evidence capture, analysis and Workbench/UI, and construct/attach authorities for experiments. It does not own Organism, World, Environment, Embodiment, ordinary reproduction or ordinary cognition. Lab application shutdown is not World death absent an explicit lifecycle request/contract.

## AD-0029 — Portable Organism state

Private learned state belongs to Organism longitudinal continuity, including private-model weights, memory, learned representations, competence, agency and cognitive development where present. A portable Organism checkpoint carries the dependency closure required to restore it, as embedded data or verified content-addressed durable references. A checkpoint referencing missing private-model content is not a complete portable continuation.

## AD-0030 — Body schema and competence

Distinguish actual physical body truth (Embodiment), current episode calibration (Embodiment/episode), learned knowledge about bodies and prior embodiments (Organism), and active applicability of learned motor/sensor competence (validated against current Embodiment). Re-embodiment may invalidate active commitments/calibration but must not silently erase longitudinal learning. Competence may require reacclimation or become temporarily unusable while remaining learned Organism state.

## AD-0031 — Cognition structure

Cognition is structurally `DEVELOPMENTALLY PROGRESSIVE AND SUSPENDIBLE WITH STATE PRESERVED`, within Organism authority. Architecture may permit undeveloped capability, temporary inactivity, suspended computation and progressive activation while preserving Organism-owned state. This establishes no scientific efficacy, necessity, dispensability or viability claim. Activation/adoption affecting causal behavior enters on explicit causal time under AD-0016.

## AD-0032 — Hybrid multi-owner persistence

Semantic owners define authoritative checkpoint state: Organism checkpoint, Embodiment body/episode checkpoint, Environment state/checkpoint, and World causal coordination state. World owns the coherent causal cut across participating authorities. TARGET provides an equivalent World causal manifest identifying world identity, causal time/tick, participating authority identities, exact checkpoint/version references, journal/evidence boundary, dependency hashes and commit/recovery status. Physical layout remains open (embedded, content-addressed, manifest references, bundle or multi-file publication).

A World causal cut is not published as complete until all authority state required for that cut is durably identifiable and recoverable. Publication failure invokes `RECOVERY_REQUIRED` as governed by AD-0019. REV-0027 establishes the need for this outcome, not a mandate for 2PC or WAL; no specific storage/transaction mechanism is selected.

## AD-0033 — Journal role

EventJournal is causal/evidentiary history and may participate in recovery, but is not ratified as sole state authority. Recovery may combine checkpoint, manifest and journal. Exact replay authority is an implementation decision for later validation.

## AD-0034 — Reproduction and causal entropy

AD-0013 remains unchanged: Organism originates ordinary reproductive readiness/transition; Environment and Embodiment provide conditions; World coordinates, validates, materializes and commits; Lab only intervenes explicitly. REV-0028 demonstrates a CURRENT/TARGET gap in the inspected Resident path, not grounds to weaken TARGET. The CURRENT host-triggered Resident reproduction path must not be promoted unchanged. OS entropy contributing to causal identity/state must be removed, explicitly injected or placed under controlled causal RNG before conformance. This is a TARGET constraint, not an assertion of replay failure or authorization to edit code now.

## AD-0035 — Population capacity

ADR-0041's cap remains a `CURRENT APPARATUS CONSTRAINT`, not ecological TARGET law. Hidden technical ceilings must not masquerade as carrying capacity, selection or reproductive fitness. Infrastructure limits are externally attributable. Any apparatus limit that prevents a potential birth is observable and scientifically attributable; a study may use a population limit only as an explicit recorded experimental intervention/condition. No ecological carrying-capacity law is selected here.

## AD-0036 — Repository consequence and dependency direction

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

## Pass 15 and review reconciliation

Pass 15 is complete as bounded falsification. The accepted decisions above replace recommendation-only status in the Tanda 2 packet. Preserve immutable REV-0026…REV-0030 and their prior `PARTIALLY_ACCEPTED` resolutions; this ratification does not rewrite reviewer claims. The bounded results informing this decision are EV-0434/0435; this record is EV-0436. REV-0026's solver coupling is addressed by AD-0024; REV-0027 by AD-0032; REV-0028 by AD-0034; REV-0029 by AD-0025; REV-0030 by AD-0022. No review is silently erased or promoted to authority.

Current code compliance remains separate. FND-0022 and OP-0019 retain the bounded current reproduction evidence; other conformance work remains in existing findings/OPs. No finding is closed by target ratification alone. Gate A/B/C remain open. Pass 16B, migration, destructive cut-over and functional code changes remain unauthorized.
