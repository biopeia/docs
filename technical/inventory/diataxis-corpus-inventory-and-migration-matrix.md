# Biopeia Corpus Inventory and Diátaxis Migration Matrix

**Document Status:** CANONICAL INVENTORY & TRACEABILITY MATRIX  
**Governance Baseline:** [ADR-0114 — Diátaxis Documentation Architecture and Governance](../adr/ADR-0114-diataxis-documentation-architecture-and-governance.md)  
**Audit Reference:** [diataxis-documentation-audit-2026-10-16.md](diataxis-documentation-audit-2026-10-16.md)  
**Total Documents Analyzed:** 59 (57 explanatory chapters + 2 canonical reference documents)  

---

## 1. Executive Summary and Quadrant Allocation

The 57 existing explanatory chapters in `explanation/` and 2 reference documents in `reference/` represent the entire canonical knowledge base of Biopeia. Under ADR-0114, no physical file is moved until its content has been mapped and preserved without loss of evidence or meaning.

| Domain | Total Chapters | Primary Diátaxis | Extracted Reference Targets | Extracted How-To Targets | Extracted Tutorial Targets | Versioned Audits |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `biopeia` | 4 | Explanation / Reference | 5 | 0 | 1 | 0 |
| `cross-domain` | 1 | Explanation / Reference | 1 | 0 | 0 | 1 |
| `embodiment` | 5 | Explanation / Reference | 10 | 0 | 0 | 5 |
| `environment` | 5 | Explanation / Reference | 8 | 0 | 0 | 5 |
| `global` | 2 | Explanation / Reference | 0 | 0 | 0 | 0 |
| `lab` | 4 | Explanation / Reference | 5 | 1 | 0 | 4 |
| `modality` | 1 | Explanation / Reference | 2 | 0 | 0 | 1 |
| `observation` | 3 | Explanation / Reference | 5 | 0 | 0 | 3 |
| `organism` | 22 | Explanation / Reference | 39 | 0 | 0 | 22 |
| `world` | 12 | Explanation / Reference | 14 | 2 | 1 | 12 |

---

## 2. Complete Inventory and Migration Classification

| ID | Current Path | Document Title | Domain | Review Basis | Target Quadrant | Planned Extractions |
|---|---|---|---|---|---|---|
| DOC-001 | [`explanation/biopeia/capability-maturity.md`](../../explanation/biopeia/capability-maturity.md) | Capability maturity: what the documented evidence supports | `biopeia` | — | **Explanation** | **Ref:** `capability-maturity-schema.md` |
| DOC-002 | [`explanation/biopeia/one-step-across-the-domains.md`](../../explanation/biopeia/one-step-across-the-domains.md) | One step across the domains | `biopeia` | — | **Explanation** | **Tut:** `tracing-one-causal-step.md` |
| DOC-003 | [`explanation/biopeia/research-hypotheses.md`](../../explanation/biopeia/research-hypotheses.md) | What Biopeia sets out to find out: candidate hypotheses | `biopeia` | — | **Explanation** | **Ref:** `research-hypotheses-parameters.md`, `research-hypotheses-schema.md` |
| DOC-004 | [`explanation/biopeia/what-biopeia-is.md`](../../explanation/biopeia/what-biopeia-is.md) | What Biopeia is | `biopeia` | — | **Explanation** | **Ref:** `what-biopeia-is-parameters.md`, `what-biopeia-is-schema.md` |
| DOC-005 | [`explanation/cross-domain/observation-presentation-boundary.md`](../../explanation/cross-domain/observation-presentation-boundary.md) | The human-facing presentation boundary | `cross-domain` | — | **Explanation** | **Ref:** `observation-presentation-boundary-contract.md`<br>**Audit:** `observation-presentation-boundary-review.md` |
| DOC-006 | [`explanation/embodiment/actuation-projection.md`](../../explanation/embodiment/actuation-projection.md) | From a motor command to effector channels | `embodiment` | — | **Explanation** | **Ref:** `actuation-projection-parameters.md`, `actuation-projection-schema.md`<br>**Audit:** `actuation-projection-review.md` |
| DOC-007 | [`explanation/embodiment/articulated-body.md`](../../explanation/embodiment/articulated-body.md) | The articulated body: what it is made of and where its joints are | `embodiment` | — | **Explanation** | **Ref:** `articulated-body-parameters.md`, `articulated-body-schema.md`<br>**Audit:** `articulated-body-review.md` |
| DOC-008 | [`explanation/embodiment/physical-projection.md`](../../explanation/embodiment/physical-projection.md) | What Embodiment hands to a solver: the physical projection, the body pose and its conventions | `embodiment` | — | **Explanation** | **Ref:** `physical-projection-parameters.md`, `physical-projection-schema.md`<br>**Audit:** `physical-projection-review.md` |
| DOC-009 | [`explanation/embodiment/physical-state.md`](../../explanation/embodiment/physical-state.md) | The body's physical state and the adoption of a solver candidate | `embodiment` | — | **Explanation** | **Ref:** `physical-state-parameters.md`, `physical-state-schema.md`<br>**Audit:** `physical-state-review.md` |
| DOC-010 | [`explanation/embodiment/somatic-state.md`](../../explanation/embodiment/somatic-state.md) | Somatic state: what a body holds | `embodiment` | — | **Explanation** | **Ref:** `somatic-state-parameters.md`, `somatic-state-schema.md`<br>**Audit:** `somatic-state-review.md` |
| DOC-011 | [`explanation/environment/dynamic-state.md`](../../explanation/environment/dynamic-state.md) | A piece of the environment that changes | `environment` | — | **Explanation** | **Ref:** `dynamic-state-parameters.md`, `dynamic-state-schema.md`<br>**Audit:** `dynamic-state-review.md` |
| DOC-012 | [`explanation/environment/finite-resource.md`](../../explanation/environment/finite-resource.md) | The finite resource | `environment` | — | **Explanation** | **Ref:** `finite-resource-parameters.md`, `finite-resource-schema.md`<br>**Audit:** `finite-resource-review.md` |
| DOC-013 | [`explanation/environment/procedural-genesis.md`](../../explanation/environment/procedural-genesis.md) | Procedural genesis of a scene | `environment` | — | **Explanation** | **Audit:** `procedural-genesis-review.md` |
| DOC-014 | [`explanation/environment/resource-geometry.md`](../../explanation/environment/resource-geometry.md) | Giving a resource a physical shape | `environment` | — | **Explanation** | **Ref:** `resource-geometry-parameters.md`, `resource-geometry-schema.md`<br>**Audit:** `resource-geometry-review.md` |
| DOC-015 | [`explanation/environment/static-scene.md`](../../explanation/environment/static-scene.md) | The static scene and its owner | `environment` | — | **Explanation** | **Ref:** `static-scene-parameters.md`, `static-scene-schema.md`<br>**Audit:** `static-scene-review.md` |
| DOC-016 | [`explanation/lab/body-interoception-transducer.md`](../../explanation/lab/body-interoception-transducer.md) | The body interoception transducer | `lab` | — | **Explanation** | **Ref:** `body-interoception-transducer-parameters.md`, `body-interoception-transducer-schema.md`<br>**Audit:** `body-interoception-transducer-review.md` |
| DOC-017 | [`explanation/lab/observation-consumer.md`](../../explanation/lab/observation-consumer.md) | The Lab observation consumer | `lab` | — | **Explanation** | **Audit:** `observation-consumer-review.md` |
| DOC-018 | [`explanation/lab/operator-material-transfer.md`](../../explanation/lab/operator-material-transfer.md) | The operator material transfer | `lab` | — | **Explanation** | **Ref:** `operator-material-transfer-contract.md`<br>**HowTo:** `material-transfer-intervention.md`<br>**Audit:** `operator-material-transfer-review.md` |
| DOC-019 | [`explanation/lab/study-utilities.md`](../../explanation/lab/study-utilities.md) | The study utilities | `lab` | — | **Explanation** | **Ref:** `study-utilities-parameters.md`, `study-utilities-schema.md`<br>**Audit:** `study-utilities-review.md` |
| DOC-020 | [`explanation/modality/current-state.md`](../../explanation/modality/current-state.md) | Modality: a narrow transduction contract, not a sensory system | `modality` | — | **Explanation** | **Ref:** `current-state-parameters.md`, `current-state-schema.md`<br>**Audit:** `current-state-review.md` |
| DOC-021 | [`explanation/observation/inherited-projection.md`](../../explanation/observation/inherited-projection.md) | The inherited projection | `observation` | — | **Explanation** | **Ref:** `inherited-projection-parameters.md`, `inherited-projection-schema.md`<br>**Audit:** `inherited-projection-review.md` |
| DOC-022 | [`explanation/observation/observation-plane.md`](../../explanation/observation/observation-plane.md) | The observation plane | `observation` | — | **Explanation** | **Ref:** `observation-plane-parameters.md`, `observation-plane-schema.md`<br>**Audit:** `observation-plane-review.md` |
| DOC-023 | [`explanation/observation/semantic-claim-model.md`](../../explanation/observation/semantic-claim-model.md) | The semantic claim model | `observation` | — | **Explanation** | **Ref:** `semantic-claim-model-schema.md`<br>**Audit:** `semantic-claim-model-review.md` |
| DOC-024 | [`explanation/organism/action-path.md`](../../explanation/organism/action-path.md) | From an affordance to a motor command | `organism` | — | **Explanation** | **Ref:** `action-path-parameters.md`, `action-path-schema.md`<br>**Audit:** `action-path-review.md` |
| DOC-025 | [`explanation/organism/actuator-evidence.md`](../../explanation/organism/actuator-evidence.md) | Evidence that an actuator does something | `organism` | — | **Explanation** | **Ref:** `actuator-evidence-parameters.md`, `actuator-evidence-schema.md`<br>**Audit:** `actuator-evidence-review.md` |
| DOC-026 | [`explanation/organism/attention-allocation.md`](../../explanation/organism/attention-allocation.md) | Allocating a bounded budget of attention | `organism` | — | **Explanation** | **Audit:** `attention-allocation-review.md` |
| DOC-027 | [`explanation/organism/capacity-pressure-and-pair-statistics.md`](../../explanation/organism/capacity-pressure-and-pair-statistics.md) | Capacity pressure and pair statistics | `organism` | — | **Explanation** | **Ref:** `capacity-pressure-and-pair-statistics-parameters.md`, `capacity-pressure-and-pair-statistics-schema.md`<br>**Audit:** `capacity-pressure-and-pair-statistics-review.md` |
| DOC-028 | [`explanation/organism/causal-evidence-and-controllability.md`](../../explanation/organism/causal-evidence-and-controllability.md) | Effects, causal evidence and controllability | `organism` | — | **Explanation** | **Ref:** `causal-evidence-and-controllability-parameters.md`, `causal-evidence-and-controllability-schema.md`<br>**Audit:** `causal-evidence-and-controllability-review.md` |
| DOC-029 | [`explanation/organism/causal-provenance-log.md`](../../explanation/organism/causal-provenance-log.md) | The causal provenance log | `organism` | — | **Explanation** | **Ref:** `causal-provenance-log-parameters.md`, `causal-provenance-log-schema.md`<br>**Audit:** `causal-provenance-log-review.md` |
| DOC-030 | [`explanation/organism/cognitive-checkpoint.md`](../../explanation/organism/cognitive-checkpoint.md) | What a cognitive checkpoint carries | `organism` | — | **Explanation** | **Ref:** `cognitive-checkpoint-parameters.md`, `cognitive-checkpoint-schema.md`<br>**Audit:** `cognitive-checkpoint-review.md` |
| DOC-031 | [`explanation/organism/cognitive-graph.md`](../../explanation/organism/cognitive-graph.md) | The cognitive graph and its explicit-tick transition | `organism` | — | **Explanation** | **Ref:** `cognitive-graph-invariants.md`<br>**Audit:** `organism-cognitive-graph-audit.md`, `cognitive-graph-review.md` |
| DOC-032 | [`explanation/organism/competence-development.md`](../../explanation/organism/competence-development.md) | How a repeated motor pattern becomes a competence | `organism` | — | **Explanation** | **Ref:** `competence-development-parameters.md`, `competence-development-schema.md`<br>**Audit:** `competence-development-review.md` |
| DOC-033 | [`explanation/organism/continuation-closure-and-reembodiment.md`](../../explanation/organism/continuation-closure-and-reembodiment.md) | Organism continuation closure and re-embodiment | `organism` | — | **Explanation** | **Ref:** `continuation-closure-and-reembodiment-parameters.md`, `continuation-closure-and-reembodiment-schema.md`<br>**Audit:** `continuation-closure-and-reembodiment-review.md` |
| DOC-034 | [`explanation/organism/execution-binding-and-affordances.md`](../../explanation/organism/execution-binding-and-affordances.md) | Execution bindings, availability and the affordance resolver | `organism` | — | **Explanation** | **Ref:** `execution-binding-and-affordances-schema.md`<br>**Audit:** `execution-binding-and-affordances-review.md` |
| DOC-035 | [`explanation/organism/executive-outcome-ledger.md`](../../explanation/organism/executive-outcome-ledger.md) | The executive outcome ledger | `organism` | — | **Explanation** | **Ref:** `executive-outcome-ledger-parameters.md`, `executive-outcome-ledger-schema.md`<br>**Audit:** `executive-outcome-ledger-review.md` |
| DOC-036 | [`explanation/organism/experience-record-and-ledger.md`](../../explanation/organism/experience-record-and-ledger.md) | The experience record and its ledger | `organism` | — | **Explanation** | **Ref:** `experience-record-and-ledger-parameters.md`, `experience-record-and-ledger-schema.md`<br>**Audit:** `experience-record-and-ledger-review.md` |
| DOC-037 | [`explanation/organism/foundation-conventions.md`](../../explanation/organism/foundation-conventions.md) | Foundation conventions: thresholds, an evidence count and limits | `organism` | — | **Explanation** | **Ref:** `foundation-conventions-parameters.md`, `foundation-conventions-schema.md`<br>**Audit:** `foundation-conventions-review.md` |
| DOC-038 | [`explanation/organism/generative-resident.md`](../../explanation/organism/generative-resident.md) | The generative resident and what a "private model" is in code | `organism` | — | **Explanation** | **Ref:** `generative-resident-parameters.md`, `generative-resident-schema.md`<br>**Audit:** `generative-resident-review.md` |
| DOC-039 | [`explanation/organism/genome-and-inheritance.md`](../../explanation/organism/genome-and-inheritance.md) | The genome, its expression and the germline record | `organism` | — | **Explanation** | **Ref:** `genome-and-inheritance-parameters.md`, `genome-and-inheritance-schema.md`<br>**Audit:** `genome-and-inheritance-review.md` |
| DOC-040 | [`explanation/organism/graph-plasticity.md`](../../explanation/organism/graph-plasticity.md) | How the cognitive graph is changed | `organism` | — | **Explanation** | **Ref:** `graph-plasticity-parameters.md`, `graph-plasticity-schema.md`<br>**Audit:** `graph-plasticity-review.md` |
| DOC-041 | [`explanation/organism/identity-and-checkpoint.md`](../../explanation/organism/identity-and-checkpoint.md) | Organism identity and the checkpoint envelope | `organism` | — | **Explanation** | **Ref:** `identity-and-checkpoint-parameters.md`, `identity-and-checkpoint-schema.md`<br>**Audit:** `identity-and-checkpoint-review.md` |
| DOC-042 | [`explanation/organism/life-of-an-organism.md`](../../explanation/organism/life-of-an-organism.md) | The life of an Organism, as the code has it | `organism` | — | **Explanation** | **Ref:** `life-of-an-organism-parameters.md`, `life-of-an-organism-schema.md` |
| DOC-043 | [`explanation/organism/prospective-deliberation.md`](../../explanation/organism/prospective-deliberation.md) | Prospective deliberation and the outcome-value ledger | `organism` | — | **Explanation** | **Ref:** `prospective-deliberation-parameters.md`, `prospective-deliberation-schema.md`<br>**Audit:** `prospective-deliberation-review.md` |
| DOC-044 | [`explanation/organism/sense-to-checkpoint-transition.md`](../../explanation/organism/sense-to-checkpoint-transition.md) | From an opaque sense signal to an accepted step | `organism` | — | **Explanation** | **Ref:** `sense-to-checkpoint-transition-parameters.md`, `sense-to-checkpoint-transition-schema.md`<br>**Audit:** `sense-to-checkpoint-transition-review.md` |
| DOC-045 | [`explanation/organism/transition-and-continuation.md`](../../explanation/organism/transition-and-continuation.md) | The Organism transition boundary and the continuation registry | `organism` | — | **Explanation** | **Ref:** `transition-and-continuation-schema.md`<br>**Audit:** `transition-and-continuation-review.md` |
| DOC-046 | [`explanation/world/causal-cycle.md`](../../explanation/world/causal-cycle.md) | The sensorimotor causal cycle | `world` | — | **Explanation** | **Ref:** `causal-cycle-schema.md`<br>**Audit:** `causal-cycle-review.md` |
| DOC-047 | [`explanation/world/causal-journal.md`](../../explanation/world/causal-journal.md) | The World causal journal | `world` | — | **Explanation** | **Ref:** `causal-journal-parameters.md`, `causal-journal-schema.md`<br>**Audit:** `causal-journal-review.md` |
| DOC-048 | [`explanation/world/causal-manifest.md`](../../explanation/world/causal-manifest.md) | The World causal manifest | `world` | — | **Explanation** | **Ref:** `causal-manifest-schema.md`<br>**Audit:** `causal-manifest-review.md` |
| DOC-049 | [`explanation/world/durable-runtime.md`](../../explanation/world/durable-runtime.md) | The durable World runtime | `world` | — | **Explanation** | **Ref:** `durable-runtime-parameters.md`, `durable-runtime-schema.md`<br>**Audit:** `durable-runtime-review.md` |
| DOC-050 | [`explanation/world/genesis-and-rosters.md`](../../explanation/world/genesis-and-rosters.md) | World genesis, rosters and participant closure | `world` | — | **Explanation** | **Ref:** `genesis-and-rosters-schema.md`<br>**Audit:** `genesis-and-rosters-review.md` |
| DOC-051 | [`explanation/world/in-memory-runtime.md`](../../explanation/world/in-memory-runtime.md) | The in-memory World runtime | `world` | — | **Explanation** | **Ref:** `in-memory-runtime-schema.md`<br>**Audit:** `in-memory-runtime-review.md` |
| DOC-052 | [`explanation/world/journal-snapshot-store.md`](../../explanation/world/journal-snapshot-store.md) | The journal snapshot store | `world` | — | **Explanation** | **Ref:** `journal-snapshot-store-schema.md`<br>**Audit:** `journal-snapshot-store-review.md` |
| DOC-053 | [`explanation/world/m1-process-bootstrap.md`](../../explanation/world/m1-process-bootstrap.md) | The M1 bounded process bootstrap and operator profile | `world` | — | **Explanation** | **Ref:** `m1-profile-schema.md`<br>**HowTo:** `m1-process-execution.md`<br>**Tut:** `first-m1-simulation.md`<br>**Audit:** `m1-process-bootstrap-review.md` |
| DOC-054 | [`explanation/world/mujoco-step-executor.md`](../../explanation/world/mujoco-step-executor.md) | The MuJoCo step executor | `world` | — | **Explanation** | **Ref:** `mujoco-step-executor-schema.md`<br>**Audit:** `mujoco-step-executor-review.md` |
| DOC-055 | [`explanation/world/observation-publication.md`](../../explanation/world/observation-publication.md) | Post-commit observation publication and outcome classification | `world` | — | **Explanation** | **Audit:** `observation-publication-review.md` |
| DOC-056 | [`explanation/world/physical-step.md`](../../explanation/world/physical-step.md) | The physical causal step, as it exists today | `world` | — | **Explanation** | **Ref:** `physical-step-parameters.md`, `physical-step-schema.md`<br>**Audit:** `physical-step-review.md` |
| DOC-057 | [`explanation/world/recovery.md`](../../explanation/world/recovery.md) | World recovery | `world` | — | **Explanation** | **Ref:** `world-recovery-contract.md`<br>**HowTo:** `recover-previous-cut.md`<br>**Audit:** `recovery-review.md` |
| DOC-058 | [`reference/evidence-status.md`](../../reference/evidence-status.md) | Evidence status and review status | `global` | — | **Reference** | — |
| DOC-059 | [`reference/units.md`](../../reference/units.md) | Units | `global` | — | **Reference** | — |

---

## 3. Domain Decomposition and Fidelity Rules

### 3.1. Organism (22 Chapters)

- **Core Principle:** Organism owns private longitudinal state, cognitive graph topology, and adaptive competence. Labels like `predictor` or `concept` denote node types and algorithmic mechanisms, NOT verified human-level cognitive faculties.
- **Fidelity Rule:** Algorithmic invariants and limits (e.g. `foundation-conventions.md`, `cognitive-graph.md`, `attention-allocation.md`) are extracted into `reference/parameters/` while retaining conceptual rationale in `explanation/organism/`.
- **Audit Traceability:** Evidence tables (`| Claim | Support |`) remain tied to their commit baseline in `audits/implementation/`.

### 3.2. World (12 Chapters)

- **Core Principle:** World is the authoritative single writer of causal history, cut sequences, and post-commit publication.
- **Operational Decomposition:**
  - `explanation/world/m1-process-bootstrap.md` decomposes into: Explanation (bootstrap lifecycle), Reference (`reference/schemas/m1-profile-schema.md`), and How-To (`how-to/operator/m1-process-execution.md`).
  - `explanation/world/recovery.md` yields operational procedure `how-to/operator/recover-previous-cut.md` strictly verified against `src/world/recovery.py`.

### 3.3. Embodiment and Environment (10 Chapters)

- **Fidelity Rule:** Somatic state representations, actuator projections, and MuJoCo coordinate frame conventions form strict reference contracts (`reference/contracts/`). Descriptive physics remain in Explanation.

### 3.4. Modality and Observation (4 Chapters)

- **Resolution of DOC-04:** Modality (sensory transduction library) and Observation (passive publication plane) maintain separated publication volumes and chapters to reflect independent authority.
- **Resolution of DOC-02:** `explanation/cross-domain/observation-presentation-boundary.md` remains in Explanation; its concrete HTTP bridge and observation client contract is projected into `reference/contracts/`.

### 3.5. Lab (4 Chapters)

- **Separation:** Study protocol utilities, observation consumers, and operator material transfer are divided into operational run procedures (`how-to/operator/`) and scientific apparatus explanation (`explanation/lab/`).

---

## 4. Phase P1 Verification Gate

- All 57 explanation chapters accounted for: **100% COVERAGE**.
- All 2 canonical reference files accounted for: **100% COVERAGE**.
- Zero orphaned documents.
- Ready for Phase P2 (tooling and model expansion).
