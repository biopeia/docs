# Migration End-to-End Acceptance Report

**Status:** CANDIDATE — not a migration-closure report  
**Evidence date:** 2026-10-12  
**Scope:** bounded two-run TARGET sensorimotor causal cycle  
**Tracking:** [world#86](https://github.com/biopeia/world/issues/86), [.github-private#42](https://github.com/biopeia/.github-private/issues/42)

## Decision and scope

This report records a reproducible candidate run of the production World-owned composition for a bounded scalar-sensing and articulated-body scenario. An independent adversarial review of the prior report revision `77c51bef7ff2818e4cc2432557ad3f4a28cd948a` and its run evidence returned **CONFIRMED**, limited to the candidate-evidence claims (see the review record on [docs#137](https://github.com/biopeia/docs/pull/137#issuecomment-6118303207)). This revision records that outcome; this updated report revision still requires exact-revision review. This is not final migration acceptance: the exact World and supporting-domain revisions used by the run remain on open pull requests. Re-run the acceptance test against integrated revisions and update this report before treating it as integrated acceptance evidence.

The run exercises actual Biopeia TARGET owner APIs and World production composition. The test launches and inspects the run; it does not supply the missing causal composition. No Symbiont runtime, compatibility bridge, workspace-owned semantic behavior, environmental labels, reward, goal, or physiology model is used.

## Repository revisions and review state

| Repository | Revision used | Publication state at evidence date |
|---|---|---|
| `biopeia/world` | `349bfa63557c4e00e478ea7b2d32b944f1897331` | PR [#114](https://github.com/biopeia/world/pull/114), OPEN |
| `biopeia/organism` | `b2e00f06a0862613a8ce29c844606eb37407f751` | PR [#130](https://github.com/biopeia/organism/pull/130), OPEN |
| `biopeia/embodiment` | `bff1bf16c2b812822364a94146ec9349292753ac` | PR [#61](https://github.com/biopeia/embodiment/pull/61), OPEN |
| `biopeia/environment` | `b71d5566c3a73774a088a41a7b99a03954e43a53` | pinned candidate revision |
| `biopeia/modality` | `79b779152d4bff2ab4191dc6601c8f1640e4cae3` | pinned candidate revision |
| `biopeia/observation` | `ef6321d2bab43b883238cdcf0ce33c08321d595c` | pinned candidate revision |

The World integration and runtime dependency extras explicitly pin these commits. PR merge state is a separate fact from this candidate-run evidence; no merge or integrated-main claim is made here.

## Reproduction

From the `biopeia/world` candidate checkout, with the pinned integration dependencies available:

```bash
uv run --extra integration pytest -q tests/integration/test_end_to_end_causal_cycle_acceptance.py
```

Result on 2026-10-12:

```text
1 passed in 0.45s
```

The acceptance test executes `_run` twice from the same declared initial state into separate persistence roots, compares causal identities, command values, adopted joint state, and Observation claims, then performs a same-process restore and second committed step in both runs. The test is non-skipping and fails if the TARGET integration imports or composition are unavailable.

## Scenario configuration

- World: `world.acceptance.sensorimotor-v1`; initial committed causal tick `0`.
- Presence: `presence.acceptance.sensorimotor-v1`.
- Organism: `12345678-1234-5678-1234-567812345678`.
- Body / episode / morphology: `body.acceptance.sensorimotor-v1` / `episode.acceptance.sensorimotor-v1` / `morphology.acceptance.sensorimotor-r1`.
- Environment and revision: `environment.acceptance.sensorimotor-v1` / `environment.acceptance.r1`; scalar field revision `field.acceptance.r1`.
- Resource and receptor: `resource.acceptance.scalar-field-v1` / `receptor.acceptance.scalar-v1`; opaque channel `channel.opaque.scalar-v1`.
- Frame: `acceptance.world-frame`, right-handed, Z-up, axes declared in the test.
- Initial field: resource position `(1, 0, 0)`, field radius `2`, resource radius `0.1`, remaining amount `10`, transfer-per-tick `1`; sample at the receptor origin yields `0.25` dimensionless.
- Modality: explicit revisioned `DimensionlessScalarFieldIdentityV1`; input/output are both dimensionless scalar values in `[0, 1]`.
- Body: fixed-base articulated root and one stable `joint.hinge`; actuator channels are identity-addressed (`actuator.hinge.positive`, `actuator.hinge.negative`).
- Solver: MuJoCo `3.14.0`; revision `mujoco-3.14.0-acceptance-r1`; timestep `0.01 s`, iterations `50`, tolerance `1e-10`; solver parameters and contact policy are explicit in the test.
- Randomness: no runtime random source is used by this fixture; both runs use identical explicit initial state and configuration.

## Evidence for the ten required segments

| # | Required segment | Candidate evidence | Scope limit |
|---|---|---|---|
| 1 | Environment owns external state | The run uses `StaticEnvironmentOwner` plus `IdentifiedFiniteScalarField`, each with stable identity, declared revision, frame and owner checkpoint. | The scalar field is static for this fixture; this does not establish a general Environment dynamics model. |
| 2 | Modality performs real transduction | The Environment field is sampled at an Embodiment-owned `EmbodimentReceptor` and passed through `DimensionlessScalarFieldIdentityV1`; the produced input is `0.25` on `channel.opaque.scalar-v1`. | Identity transduction is only justified for the same dimensionless quantity/range; it proves no richer sensory model. |
| 3 | Organism receives and processes input | World invokes `advance_organism_from_scalar_field_for_physical_step`, which reaches the public Organism transition path; `organism_step` advances and the run records the correlated World step separately. | One bounded transition is not evidence of learning, cognition quality, or adaptation. |
| 4 | Organism produces action intent | `OrganismExplorationComposer.prepare` runs behind the Organism action port after the accepted transition and returns a proposal and command. | This does not show the action was selected because the scalar value changed or that it is scientifically effective. |
| 5 | Production path constructs a complete motor command | The production composition uses stable actuator IDs and Embodiment-owned differential binding; both channels are present. No final command is injected by the test. | This fixture tests a bounded one-joint actuator surface, not arbitrary morphologies. |
| 6 | World performs physical step | `run_scalar_sensorimotor_cycle_and_publish` creates `PhysicalStepContext` from World tick and invokes the configured articulated MuJoCo adapter. | Solver configuration is small and deterministic; no performance or production-scale claim. |
| 7 | Owners validate/adopt their state | Embodiment adopts the candidate body state; Environment validates its accepted physical-step correlation; owner checkpoint payloads are written and validated before World commit. | The body root is fixed at the receptor origin. The post-step sample therefore uses a stable source receptor location; moving-root sampling is not established. |
| 8 | World commits coherent causal cut | The two-run test commits ticks `1` and `2`, with explicit World ID, commit IDs, step IDs, owner references and causal correlations. | Tick `2` follows same-process restore; not a fresh-process/bootstrap recovery test. |
| 9 | Observation receives actual post-commit publication | The World composition publishes owner-backed `body_pose` and `finite_scalar_field` claims after commit. Delivery sequences and committed-cut references are asserted; claim lineage refers to owner checkpoint hashes. | The test uses an in-process Observation plane; it does not test network transport, durable delivery, replay or UI rendering. |
| 10 | One run is traceable end to end | The acceptance test retains results for sensory input, action proposal/command, physical outcome, committed cuts, checkpoint references and Observation messages; repeated runs compare these values. | No external scientific evidence admission is implied. |

### Repeated-run observations

The test asserts the same first-cut identity, tick, sensory value, command, adopted joint state (within the declared numeric comparison), and Observation claims across the two independent run directories. It also asserts matching resumed tick-2 command, joint state and Observation claims.

During the separately captured two-run execution, the initial sensory value was `0.25`. Tick-1 motor channels were `0.1762655831525182` and `0.09808329665800182`; the adopted hinge position/velocity were `-0.0003580868083723772 rad` and `-0.03580868083723772 rad/s`. After the same-process restore, tick-2 hinge position/velocity were `-0.0013156820046243461 rad` and `-0.09575951962519688 rad/s`. These are fixture-specific outputs, not calibrated physical or biological claims.

The two delivered claims per committed cut are a body-pose projection and a finite-scalar-field projection. Their Observation delivery sequences and lineage references are checked against the associated committed cut and owner checkpoint hashes. The test intentionally creates a fresh Observation plane for each independent run, so sequence identity is compared within each run rather than claimed globally.

## Independent review and limitations

An independent review of the bounded World composition was **BOUNDED**: it confirmed that a concrete Organism-owned exploration composer is invoked through the production World composition, while explicitly not confirming action-conditioning, learning, or scientific effectiveness. A separate exact-report/run review under BAW-004 was **CONFIRMED** for the prior report revision `77c51bef7ff2818e4cc2432557ad3f4a28cd948a` and candidate evidence: the reviewer inspected World#114 at `349bfa63557c4e00e478ea7b2d32b944f1897331`, reproduced the acceptance test in a clean temporary clone (`1 passed`), and matched the recorded tick-1/tick-2 numeric outputs. No material discrepancy was found. This updated report revision requires its own exact-revision check; neither review promotes open candidate commits to integrated revisions or establishes migration closure. The final integrated run and its exact report revision also require review.

This run does not prove:

- that the Organism learned a causal relationship or that its action was conditioned on the sensed value;
- resource semantics, goals, rewards, locomotion, or behavioral success;
- physiological validity or scientific calibration;
- moving-root receptor projection correctness;
- fresh-process restart, full bootstrap recovery, universal crash/power-loss resistance, or arbitrary replay;
- production-scale solver performance, network Observation transport, or visualization completeness;
- migration closure.

## Required follow-up before acceptance

1. Integrate the exact reviewed dependencies and World composition through the repository merge process.
2. Re-run this non-skipping acceptance test against the resulting integrated revisions and update all SHAs and output evidence.
3. Obtain and record an independent adversarial review of the exact report revision and its evidence.
4. Continue to satisfy the separate checkpoint/continuation and migration-closure criteria; this causal-cycle report does not close them.
