# Organism continuation closure and re-embodiment

Reviewed against `organism` at commit `637bc21a7e2a1aa9e0870f55f134e839657687f4`
(main on 2026-10-16); first written against `de16558faeba`. Statements are marked by what supports them: the code,
the tests, or an accepted specification.

## What it is

An organism's life extends beyond the lifespan of any single physical body.
When an embodiment undergoes death, degradation, or experimental transfer,
the organism's cognitive identity and acquired knowledge may continue in a
new body.

The rules governing what persists across re-embodiment, what is suspended,
and what is discarded are established by the Organism Continuation Closure
Specification v1 (`organism:docs/continuation/organism-continuation-closure-specification-v1.md`),
Owner-State Inventory v1 (`organism:docs/continuation/organism-owner-state-inventory-v1.md`),
and the fail-closed longitudinal checkpoint aggregate (`OrganismLongitudinalCheckpoint`).

## The four-tier state taxonomy

Organism state is strictly classified into four operational tiers:

1. **`REQUIRED_PORTABLE` (Core Cognitive Identity):**
   State that must survive across any transition and any embodiment. This
   includes the transition identity (`OrganismIdentity`), cognitive graph
   topology and synaptic plasticity, historical experience ledger, germline
   genome, and safety counters. In `OrganismLongitudinalCheckpoint`, exactly ten
   named subsystems (`REQUIRED_LONGITUDINAL_COMPONENTS`) must be present. If any
   required portable field cannot be restored or validated, restoration fails closed.
2. **`SUSPENDED_REVALIDABLE` (Surface-Bound Sensorimotor State):**
   State that was acquired on a specific physical body and cannot be executed
   safely on an arbitrary new body without verification. This includes
   competence execution bindings (`CompetenceExecutionBinding`), actuator
   calibrations, and motor control parameters.
   When an organism is re-embodied or restored, these bindings are not
   deleted; instead, `mark_stale_for_surface` transitions them to `STALE`
   with `StalenessReason.SURFACE_NOT_CURRENT`. They remain preserved as
   historical hypotheses (`PredictionScope.HISTORICAL`), preventing
   destructive cross-body actuator commands.
3. **`RESOLVABLE_EXTERNAL` (External Dependency Closures):**
   Content-addressed external artifacts referenced by digest. The standalone
   cognitive checkpoint payload enforces an empty manifest (`dependency_closure: []`);
   however, the M3 compact action history (`biopeia-organism-exploration-checkpoint-v5`)
   and the aggregate `OrganismLongitudinalCheckpoint` explicitly support external
   dependencies (`CheckpointDependency(locator, sha256)`). Restoration requires a
   caller-supplied reader and verifies every declared digest before decoding subsystems.
4. **`DISPOSABLE_EPHEMERAL` (Transient Scratchpad):**
   Single-tick proposal scratchpads, transient attention allocation masks,
   and uncommitted proposal buffers. These are discarded at every cut boundary
   and are never written to durable checkpoints.

## Actuator applicability validation at restore

When an organism runtime is restored from a committed checkpoint, restoration
enforces strict actuator applicability validation
(`organism:src/organism/actuation/bounded_action.py:521-591`):

- The caller must supply paired `expected_actuator_context` and
  `expected_surface`.
- The restored composer validates that the surface fingerprint matches the
  current embodiment's active morphology.
- Stable actuator identities and channel counts are verified.
- Any mismatch raises an applicability error before the action composer can
  issue commands to the physics engine (`test_production_composer_stages_identity_bound_exploration_without_evidence_claims`).

## Preserving knowledge without somatic confusion

The continuation closure enforces a fundamental architectural invariant:
**longitudinal knowledge is preserved, but somatic execution is strictly
surface-verified**.

An organism transferred to a different morphology does not forget its causal
history or world experiences; however, its motor controllers refuse to fire
unverified commands until new motor affordances are confirmed against the
new body's active physical surface.

## What supports this description

| Claim | Support |
|---|---|
| Four-tier state classification and continuation closure rules | Specification in `organism:docs/continuation/organism-continuation-closure-specification-v1.md` |
| Longitudinal checkpoint aggregate enforces 10-subsystem closure | Code in `organism:src/organism/checkpoint.py` and tests in `organism:tests/source_unit/test_longitudinal_checkpoint.py` |
| Surface staleness marking and historical hypothesis preservation | Code in `organism:src/organism/actuation/binding.py:343-367` and `organism:src/organism/agency/availability.py:87-119` |
| Fail-closed actuator applicability validation on checkpoint restore | Code in `organism:src/organism/actuation/bounded_action.py:521-591` and tests in `world:tests/integration/test_end_to_end_causal_cycle_acceptance.py` |
| Cognitive checkpoint empty dependency closure enforcement | Code in `organism:src/organism/cognition/portable_checkpoint.py:180-186` |
| Separation of longitudinal cognition from embodiment life | Accepted decisions ADR-0041, ADR-0095 |
