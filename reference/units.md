# Units

Generated from `registry/` by `tools/render_units.py`. Do not edit: change the
registry and render again. The registry is the only source; this page
restates it so that the answers about one unit can be read in one place.

34 units, 9 cross-domain contracts, 82 findings.

## World

### World causal journal

`component.world-causal-journal` · component · CURRENT

| | |
|---|---|
| Identifier | `WLD-JRN` |
| Responsible for | the in-memory append order, read-only record envelopes and prefix digests of committed World causal records |
| Must not | interpret record types, payloads or the related-record identifiers it carries; claim durable storage, atomic publication or recovery; decide whether a causal tick commits |
| Owned by | world |
| Explained in | [explanation/world/causal-journal.md](../explanation/world/causal-journal.md) |
| Implemented in | `world:src/world/journal.py` |
| State | owner world, family causal_history; durable: no; in a causal cut: yes; a failed transition can leave: staged records remain staged after a failed batch commit; nothing durable. Its records are named by a cut through the journal boundary only when a durable runtime drives it |
| Governed by | [technical/adr/ADR-0107-journal-role.md](../technical/adr/ADR-0107-journal-role.md), [technical/adr/ADR-0086-capture-manifest-last-sequence-semantics.md](../technical/adr/ADR-0086-capture-manifest-last-sequence-semantics.md) |
| Tests | `world:tests/test_journal.py` |
| Reviewed at | world@9da5ecce209e (RECORDED) |
| Known findings | F-0005 performance concern ([issue](https://github.com/biopeia/world/issues/32)); F-0008 implementation finding (open); F-0009 implementation finding (open) |

### World causal manifest

`component.world-causal-manifest` · component · CURRENT

| | |
|---|---|
| Identifier | `WLD-MAN` |
| Responsible for | the durable record of a World causal cut: its tick, rosters, opaque owner checkpoint references, journal boundary and commit or recovery status |
| Must not | decode, write or judge the owner state its references point to; restore owner state during recovery; claim to be a transaction across owners, a multi-writer protocol or a security boundary |
| Owned by | world |
| Explained in | [explanation/world/causal-manifest.md](../explanation/world/causal-manifest.md) |
| Implemented in | `world:src/world/manifest.py` |
| State | owner world, family causal_history; durable: yes; in a causal cut: yes; a failed transition can leave: a preparing or recovery-required record naming the failed transition, its proposed rosters and the failure; after recovery, an immutable receipt |
| Depends on | `component.world-causal-journal` |
| Governed by | [technical/adr/ADR-0106-hybrid-multi-owner-persistence.md](../technical/adr/ADR-0106-hybrid-multi-owner-persistence.md), [technical/adr/ADR-0093-material-failure-before-commit-requires-explicit-recovery.md](../technical/adr/ADR-0093-material-failure-before-commit-requires-explicit-recovery.md), [technical/adr/ADR-0084-single-writer-or-explicit-coordination-for-shared-persistent-state.md](../technical/adr/ADR-0084-single-writer-or-explicit-coordination-for-shared-persistent-state.md), [technical/adr/ADR-0086-capture-manifest-last-sequence-semantics.md](../technical/adr/ADR-0086-capture-manifest-last-sequence-semantics.md) |
| Tests | `world:tests/test_manifest.py` |
| Reviewed at | world@9da5ecce209e (RECORDED) |
| Known findings | F-0006 evidence gap ([issue](https://github.com/biopeia/world/issues/33)); F-0007 recovery durability gap (accepted); F-0011 implementation finding (open) |

### World journal snapshot store

`component.world-journal-snapshot-store` · component · CURRENT

| | |
|---|---|
| Identifier | `WLD-SNP` |
| Responsible for | the immutable on-disk snapshots of the World causal journal and the checkpoint references to them |
| Must not | decide whether a causal tick commits; interpret the records it stores; remove or rewrite a snapshot |
| Owned by | world |
| Explained in | [explanation/world/journal-snapshot-store.md](../explanation/world/journal-snapshot-store.md) |
| Implemented in | `world:src/world/durable_runtime.py` |
| State | owner world, family causal_history; durable: yes; in a causal cut: yes; a failed transition can leave: a snapshot file for the failed tick, referenced by no committed cut |
| Depends on | `component.world-causal-journal` |
| Governed by | [technical/adr/ADR-0107-journal-role.md](../technical/adr/ADR-0107-journal-role.md), [technical/adr/ADR-0106-hybrid-multi-owner-persistence.md](../technical/adr/ADR-0106-hybrid-multi-owner-persistence.md) |
| Tests | `world:tests/test_durable_runtime.py` |
| Reviewed at | world@9da5ecce209e (RECORDED) |
| Known findings | F-0003 recovery durability gap ([issue](https://github.com/biopeia/world/issues/30)); F-0005 performance concern ([issue](https://github.com/biopeia/world/issues/32)); F-0010 implementation finding (open) |

### Durable World runtime

`component.world-durable-runtime` · component · CURRENT

| | |
|---|---|
| Identifier | `WLD-DRT` |
| Responsible for | the coordination of a World causal transition from one committed cut to the next, and the in-process refusal to continue after a failure |
| Must not | hold, read or interpret the state of an Organism, an Embodiment or an Environment; restore owner state itself during recovery; claim crash consistency, rollback across owners or a multi-writer protocol |
| Owned by | world |
| Explained in | [explanation/world/durable-runtime.md](../explanation/world/durable-runtime.md) |
| Implemented in | `world:src/world/durable_runtime.py` |
| State | owner world, family ephemeral; durable: no; in a causal cut: no; a failed transition can leave: an in-memory latch that refuses further ticks; owner checkpoints written by the callback, referenced by no committed cut |
| Cross-domain contracts | Owner checkpoint validation (structural); Operator material transfer (shared_type) |
| Depends on | `component.world-causal-journal`, `component.world-causal-manifest`, `component.world-journal-snapshot-store` |
| Governed by | [technical/adr/ADR-0106-hybrid-multi-owner-persistence.md](../technical/adr/ADR-0106-hybrid-multi-owner-persistence.md), [technical/adr/ADR-0093-material-failure-before-commit-requires-explicit-recovery.md](../technical/adr/ADR-0093-material-failure-before-commit-requires-explicit-recovery.md), [technical/adr/ADR-0084-single-writer-or-explicit-coordination-for-shared-persistent-state.md](../technical/adr/ADR-0084-single-writer-or-explicit-coordination-for-shared-persistent-state.md), [technical/adr/ADR-0083-causal-cycles-have-explicit-commit-semantics.md](../technical/adr/ADR-0083-causal-cycles-have-explicit-commit-semantics.md), [technical/design/runtime/biopeia-physical-step-integration-v1.md](../technical/design/runtime/biopeia-physical-step-integration-v1.md) |
| Tests | `world:tests/test_durable_runtime.py`, `world:tests/integration/test_durable_checkpoint_restore_slice.py`, `world:tests/integration/physical_step/test_first_biopeia_physical_causal_step.py` |
| Reviewed at | world@9da5ecce209e (RECORDED) |
| Known findings | F-0003 recovery durability gap ([issue](https://github.com/biopeia/world/issues/30)); F-0004 implementation finding ([issue](https://github.com/biopeia/world/issues/31)); F-0005 performance concern ([issue](https://github.com/biopeia/world/issues/32)); F-0006 evidence gap ([issue](https://github.com/biopeia/world/issues/33)); F-0007 recovery durability gap (accepted) |

### In-memory World runtime

`component.world-in-memory-runtime` · component · CURRENT

| | |
|---|---|
| Identifier | `WLD-RTM` |
| Responsible for | an in-memory World identity, one presence, a tick counter and its causal journal, and the in-process refusal to continue after a failed transition |
| Must not | interpret the transition it runs or roll back what it changed; claim durable state or recovery |
| Owned by | world |
| Explained in | [explanation/world/in-memory-runtime.md](../explanation/world/in-memory-runtime.md) |
| Implemented in | `world:src/world/runtime.py` |
| State | owner world, family ephemeral; durable: no; in a causal cut: no; a failed transition can leave: an in-memory latch that refuses further ticks; whatever the opaque transition changed before failing is not rolled back |
| Depends on | `component.world-causal-journal` |
| Governed by | [technical/adr/ADR-0080-world-identity-is-authoritative-not-a-presentation-label.md](../technical/adr/ADR-0080-world-identity-is-authoritative-not-a-presentation-label.md), [technical/adr/ADR-0083-causal-cycles-have-explicit-commit-semantics.md](../technical/adr/ADR-0083-causal-cycles-have-explicit-commit-semantics.md), [technical/adr/ADR-0096-world-participation-including-singleton.md](../technical/adr/ADR-0096-world-participation-including-singleton.md) |
| Tests | `world:tests/test_runtime.py`, `world:tests/integration/test_first_biopeia_causal_tick.py` |
| Reviewed at | world@9da5ecce209e (RECORDED) |
| Known findings | F-0012 recovery durability gap (accepted) |

### World causal transition

`mechanism.world-causal-transition` · mechanism · CURRENT

| | |
|---|---|
| Owned by | world |
| Explained in | [explanation/world/durable-runtime.md](../explanation/world/durable-runtime.md), [explanation/world/causal-manifest.md](../explanation/world/causal-manifest.md) |
| Implemented in | `world:src/world/durable_runtime.py`, `world:src/world/manifest.py` |
| Depends on | `component.world-durable-runtime`, `component.world-causal-manifest`, `component.world-journal-snapshot-store` |
| Governed by | [technical/adr/ADR-0083-causal-cycles-have-explicit-commit-semantics.md](../technical/adr/ADR-0083-causal-cycles-have-explicit-commit-semantics.md), [technical/adr/ADR-0106-hybrid-multi-owner-persistence.md](../technical/adr/ADR-0106-hybrid-multi-owner-persistence.md) |
| Tests | `world:tests/test_durable_runtime.py`, `world:tests/test_manifest.py` |
| Reviewed at | world@9da5ecce209e (RECORDED) |

### World genesis, rosters and participant closure

`mechanism.world-genesis-and-rosters` · mechanism · CURRENT

| | |
|---|---|
| Owned by | world |
| Explained in | [explanation/world/genesis-and-rosters.md](../explanation/world/genesis-and-rosters.md) |
| Implemented in | `world:src/world/durable_runtime.py`, `world:src/world/manifest.py` |
| Depends on | `component.world-durable-runtime`, `component.world-causal-manifest` |
| Governed by | [technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md](../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md), [technical/adr/ADR-0095-surviving-semantic-authorities.md](../technical/adr/ADR-0095-surviving-semantic-authorities.md), [technical/adr/ADR-0096-world-participation-including-singleton.md](../technical/adr/ADR-0096-world-participation-including-singleton.md) |
| Tests | `world:tests/test_durable_runtime.py` |
| Reviewed at | world@9da5ecce209e (RECORDED) |
| Known findings | F-0001 contract gap ([issue](https://github.com/biopeia/world/issues/28)) |

### World recovery

`mechanism.world-recovery` · mechanism · CURRENT

| | |
|---|---|
| Owned by | world |
| Explained in | [explanation/world/recovery.md](../explanation/world/recovery.md) |
| Implemented in | `world:src/world/durable_runtime.py`, `world:src/world/manifest.py` |
| Depends on | `mechanism.world-causal-transition` |
| Governed by | [technical/adr/ADR-0093-material-failure-before-commit-requires-explicit-recovery.md](../technical/adr/ADR-0093-material-failure-before-commit-requires-explicit-recovery.md), [technical/adr/ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md](../technical/adr/ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md) |
| Tests | `world:tests/test_durable_runtime.py`, `world:tests/test_manifest.py` |
| Reviewed at | world@9da5ecce209e (RECORDED) |
| Known findings | F-0003 recovery durability gap ([issue](https://github.com/biopeia/world/issues/30)); F-0006 evidence gap ([issue](https://github.com/biopeia/world/issues/33)); F-0011 implementation finding (open) |

### Physical causal step

`mechanism.physical-causal-step` · mechanism · EXPERIMENTAL

| | |
|---|---|
| Owned by | world; also involves organism, embodiment, environment, observation |
| Explained in | [explanation/world/physical-step.md](../explanation/world/physical-step.md) |
| Implemented in | `world:src/world/physical_step.py`, `world:tests/integration/physical_step/test_first_biopeia_physical_causal_step.py`, `world:tests/integration/physical_step/test_procedural_sphere_world_step.py`, `world:src/world/durable_runtime.py` |
| Cross-domain contracts | Correlation of a physical step (fixture_only); Observation of a committed cut (fixture_only); Body physical input to a solver (fixture_only) |
| Depends on | `mechanism.world-causal-transition`, `mechanism.world-genesis-and-rosters` |
| Governed by | [technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md](../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md), [technical/adr/ADR-0098-physical-substrate-and-causal-integration.md](../technical/adr/ADR-0098-physical-substrate-and-causal-integration.md), [technical/design/runtime/biopeia-physical-step-integration-v1.md](../technical/design/runtime/biopeia-physical-step-integration-v1.md) |
| Tests | `world:tests/unit/test_physical_step.py`, `world:tests/integration/physical_step/test_first_biopeia_physical_causal_step.py`, `world:tests/integration/physical_step/test_procedural_sphere_world_step.py` |
| Reviewed at | world@9da5ecce209e (RECORDED) |
| Known findings | F-0002 implementation finding ([issue](https://github.com/biopeia/world/issues/29)); F-0013 contract gap ([issue](https://github.com/biopeia/environment/issues/37)); F-0020 contract gap ([issue](https://github.com/biopeia/embodiment/issues/25)); F-0115 contract gap ([issue](https://github.com/biopeia/embodiment/issues/32)) |

### One step across the domains

`concept.biopeia-one-step-across-the-domains` · concept · CURRENT

| | |
|---|---|
| Owned by | world; also involves environment, modality, organism, embodiment, observation, lab |
| Explained in | [explanation/biopeia/one-step-across-the-domains.md](../explanation/biopeia/one-step-across-the-domains.md) |
| Depends on | `component.world-causal-manifest`, `component.world-durable-runtime`, `mechanism.world-recovery`, `mechanism.physical-causal-step`, `component.environment-finite-resource`, `component.environment-static-scene`, `concept.modality-current-state`, `component.embodiment-physical-state`, `mechanism.embodiment-actuation-projection`, `component.lab-operator-material-transfer`, `component.observation-semantic-claim-model`, `component.observation-plane`, `mechanism.organism-action-path`, `component.organism-identity-checkpoint` |
| Governed by | [technical/adr/ADR-0095-surviving-semantic-authorities.md](../technical/adr/ADR-0095-surviving-semantic-authorities.md), [technical/adr/ADR-0110-repository-consequence-and-dependency-direction.md](../technical/adr/ADR-0110-repository-consequence-and-dependency-direction.md), [technical/adr/ADR-0098-physical-substrate-and-causal-integration.md](../technical/adr/ADR-0098-physical-substrate-and-causal-integration.md) |

## Environment

### Finite resource

`component.environment-finite-resource` · component · CURRENT

| | |
|---|---|
| Identifier | `ENV-RES` |
| Responsible for | the objective quantity remaining of one finite environmental resource, its place, its scalar field and its stable identity |
| Must not | determine contact, cause an organism action or assign meaning to the resource; regenerate; claim physical equivalence to an endogenous mechanism |
| Owned by | environment; also involves world, lab |
| Explained in | [explanation/environment/finite-resource.md](../explanation/environment/finite-resource.md) |
| Implemented in | `environment:src/environment/resource.py`, `environment:src/environment/identified_resource.py` |
| State | owner environment, family environmental_state |
| Cross-domain contracts | Owner checkpoint validation (structural); Operator material transfer (shared_type) |
| Governed by | [technical/adr/ADR-0095-surviving-semantic-authorities.md](../technical/adr/ADR-0095-surviving-semantic-authorities.md), [technical/adr/ADR-0074-biopeia-world-environment-authority-split.md](../technical/adr/ADR-0074-biopeia-world-environment-authority-split.md), [technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md](../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md) |
| Tests | `environment:tests/unit/test_resource.py`, `environment:tests/test_identified_resource.py` |
| Reviewed at | environment@f97ec22272b6 (RECORDED) |
| Known findings | F-0014 implementation finding (open); F-0015 contract gap (open); F-0016 implementation finding (open) |

### Static scene and its owner

`component.environment-static-scene` · component · CURRENT

| | |
|---|---|
| Identifier | `ENV-SCN` |
| Responsible for | an immutable static physical scene (frame, gravity, ground planes, spheres) and the record of the last physical step Environment accepted for it |
| Must not | depend on a solver or let a solver own the scene; adopt a changed scene; mint the authority of a physical step |
| Owned by | environment; also involves world |
| Explained in | [explanation/environment/static-scene.md](../explanation/environment/static-scene.md) |
| Implemented in | `environment:src/environment/static_scene.py` |
| State | owner environment, family environmental_state |
| Cross-domain contracts | Owner checkpoint validation (structural); Correlation of a physical step (fixture_only); Frame and unit conventions between body and scene (by_convention) |
| Governed by | [technical/adr/ADR-0098-physical-substrate-and-causal-integration.md](../technical/adr/ADR-0098-physical-substrate-and-causal-integration.md), [technical/adr/ADR-0074-biopeia-world-environment-authority-split.md](../technical/adr/ADR-0074-biopeia-world-environment-authority-split.md), [technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md](../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md), [technical/design/runtime/biopeia-physical-step-integration-v1.md](../technical/design/runtime/biopeia-physical-step-integration-v1.md) |
| Tests | `environment:tests/test_static_scene.py` |
| Reviewed at | environment@0a9f4fbb1922 (RECORDED) |
| Known findings | F-0013 contract gap ([issue](https://github.com/biopeia/environment/issues/37)) |

### Procedural genesis of a scene

`component.environment-procedural-genesis` · component · CURRENT

| | |
|---|---|
| Identifier | `ENV-GEN` |
| Responsible for | one identified, versioned generator that turns a seed and an explicit configuration into a static scene with recorded provenance |
| Must not | read host time, process state or a global random source; guarantee non-overlap, terrain quality, ecological meaning or scientific suitability; attach labels or meaning to what it generates |
| Owned by | environment |
| Explained in | [explanation/environment/procedural-genesis.md](../explanation/environment/procedural-genesis.md) |
| Implemented in | `environment:src/environment/procedural_genesis.py` |
| State | owner implementation-local, family ephemeral |
| Depends on | `component.environment-static-scene` |
| Governed by | [technical/adr/ADR-0074-biopeia-world-environment-authority-split.md](../technical/adr/ADR-0074-biopeia-world-environment-authority-split.md), [technical/adr/ADR-0090-host-wall-clock-time-is-never-implicit-causal-authority.md](../technical/adr/ADR-0090-host-wall-clock-time-is-never-implicit-causal-authority.md) |
| Tests | `environment:tests/test_genesis.py` |
| Reviewed at | environment@f97ec22272b6 (RECORDED) |
| Known findings | F-0017 implementation finding (accepted); F-0019 evidence gap (open) |

### Physical projection of resource geometry

`component.environment-resource-geometry` · component · CURRENT

| | |
|---|---|
| Identifier | `ENV-GEO` |
| Responsible for | the realisation of a resource's relative centre and radius as a sphere in metres, in a frame and at a scale the caller declares |
| Must not | infer calibration or supply a default frame or scale; transform coordinates to another frame; treat the scalar field, the quantity or the transfer bound as collider data; change the resource |
| Owned by | environment |
| Explained in | [explanation/environment/resource-geometry.md](../explanation/environment/resource-geometry.md) |
| Implemented in | `environment:src/environment/physical.py` |
| State | owner implementation-local, family ephemeral |
| Depends on | `component.environment-finite-resource`, `component.environment-static-scene` |
| Governed by | [technical/adr/ADR-0098-physical-substrate-and-causal-integration.md](../technical/adr/ADR-0098-physical-substrate-and-causal-integration.md), [technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md](../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md) |
| Tests | `environment:tests/unit/test_physical_projection.py`, `environment:tests/test_boundary.py` |
| Reviewed at | environment@f97ec22272b6 (RECORDED) |
| Known findings | F-0015 contract gap (open); F-0018 implementation finding (open) |

### Dynamic object state and its owner

`component.environment-dynamic-state` · component · CURRENT

| | |
|---|---|
| Identifier | `ENV-DYN` |
| Responsible for | the position of one identified object in the environment, and the record of the last physical step Environment accepted for it |
| Must not | define environmental laws or judge whether a proposed position is physically admissible; solve physics or claim a candidate was calibrated; mint the authority of a physical step |
| Owned by | environment; also involves world |
| Explained in | [explanation/environment/dynamic-state.md](../explanation/environment/dynamic-state.md) |
| Implemented in | `environment:src/environment/dynamic_state.py` |
| State | owner environment, family environmental_state |
| Cross-domain contracts | Correlation of a physical step (fixture_only) |
| Depends on | `component.environment-static-scene` |
| Governed by | [technical/adr/ADR-0098-physical-substrate-and-causal-integration.md](../technical/adr/ADR-0098-physical-substrate-and-causal-integration.md), [technical/adr/ADR-0074-biopeia-world-environment-authority-split.md](../technical/adr/ADR-0074-biopeia-world-environment-authority-split.md), [technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md](../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md), [technical/design/runtime/biopeia-physical-step-integration-v1.md](../technical/design/runtime/biopeia-physical-step-integration-v1.md) |
| Tests | `environment:tests/test_dynamic_state.py` |
| Reviewed at | environment@0a9f4fbb1922 (RECORDED) |
| Known findings | F-0013 contract gap ([issue](https://github.com/biopeia/environment/issues/37)); F-0125 contract gap (open); F-0126 implementation finding (accepted); F-0127 implementation finding (open) |

## Embodiment

### Body physical state and adoption of a solver candidate

`component.embodiment-physical-state` · component · CURRENT

| | |
|---|---|
| Identifier | `EMB-PHY` |
| Responsible for | the free-root pose and velocities of one body in one embodiment episode at one World causal tick, and the correlation of the last physical step accepted for it |
| Must not | execute a solver or let a solver change the state; commit a World cut or claim a durable checkpoint reference; mint the authority of a physical step |
| Owned by | embodiment; also involves world |
| Explained in | [explanation/embodiment/physical-state.md](../explanation/embodiment/physical-state.md) |
| Implemented in | `embodiment:src/embodiment/physics3d/physical_transition.py`, `embodiment:src/embodiment/observation.py` |
| State | owner embodiment, family embodiment_local; birth: initialize, checkpoint: preserve, restart: preserve, reembodiment: reset, reproduction: not_inherited |
| Cross-domain contracts | Owner checkpoint validation (structural); Correlation of a physical step (fixture_only) |
| Governed by | [technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md](../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md), [technical/adr/ADR-0098-physical-substrate-and-causal-integration.md](../technical/adr/ADR-0098-physical-substrate-and-causal-integration.md), [technical/adr/ADR-0095-surviving-semantic-authorities.md](../technical/adr/ADR-0095-surviving-semantic-authorities.md), [technical/adr/ADR-0094-somatic-state-ownership-body-holds-organism-regulates-and-feels.md](../technical/adr/ADR-0094-somatic-state-ownership-body-holds-organism-regulates-and-feels.md), [technical/design/runtime/biopeia-physical-step-integration-v1.md](../technical/design/runtime/biopeia-physical-step-integration-v1.md) |
| Tests | `embodiment:tests/test_physical_transition.py`, `embodiment:tests/test_body_pose_sample.py` |
| Reviewed at | embodiment@a5129f03aa4b, world@c162b67e698d (RECORDED) |
| Known findings | F-0020 contract gap ([issue](https://github.com/biopeia/embodiment/issues/25)); F-0021 contract gap (open); F-0120 contract gap (open) |

### Actuation projection by stable effector identity

`mechanism.embodiment-actuation-projection` · mechanism · CURRENT

| | |
|---|---|
| Owned by | embodiment; also involves organism |
| Explained in | [explanation/embodiment/actuation-projection.md](../explanation/embodiment/actuation-projection.md) |
| Implemented in | `embodiment:src/embodiment/physics3d/actuation_projection.py` |
| Cross-domain contracts | Motor command from Organism to Embodiment (structural) |
| Governed by | [technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md](../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md), [technical/design/runtime/biopeia-physical-step-integration-v1.md](../technical/design/runtime/biopeia-physical-step-integration-v1.md) |
| Tests | `embodiment:tests/test_actuation_projection.py` |
| Reviewed at | embodiment@a5129f03aa4b (RECORDED) |
| Known findings | F-0022 implementation finding (open); F-0023 contract gap (open) |

### Somatic state, metabolic ledger and body checkpoint

`component.embodiment-somatic-state` · component · CURRENT

| | |
|---|---|
| Identifier | `EMB-SOM` |
| Responsible for | one body's energy reserve and maximum, structural integrity and per-structure records, vital state, age, stored temperature, fatigue, growth and senescence values, and the per-kind metabolic accounts |
| Must not | leave the dead state; create physical energy by refilling accounting channels; assign Organism identity or World commit authority to Embodiment; obtain or authorise a material transfer |
| Owned by | embodiment; also involves lab, world |
| Explained in | [explanation/embodiment/somatic-state.md](../explanation/embodiment/somatic-state.md) |
| Implemented in | `embodiment:src/embodiment/physiology.py`, `embodiment:src/embodiment/metabolism.py`, `embodiment:src/embodiment/physiology_config.py`, `embodiment:src/embodiment/intake.py`, `embodiment:src/embodiment/checkpoint.py` |
| State | owner embodiment, family embodiment_local; birth: initialize, checkpoint: preserve, restart: preserve, reembodiment: reset, reproduction: not_inherited |
| Cross-domain contracts | Operator material transfer (shared_type); Body interoception (shared_type) |
| Governed by | [technical/adr/ADR-0094-somatic-state-ownership-body-holds-organism-regulates-and-feels.md](../technical/adr/ADR-0094-somatic-state-ownership-body-holds-organism-regulates-and-feels.md), [technical/adr/ADR-0095-surviving-semantic-authorities.md](../technical/adr/ADR-0095-surviving-semantic-authorities.md) |
| Tests | `embodiment:tests/test_somatic_state.py`, `embodiment:tests/test_intake.py`, `embodiment:tests/test_checkpoint.py` |
| Reviewed at | embodiment@a5129f03aa4b (RECORDED) |
| Known findings | F-0021 contract gap (open); F-0024 implementation finding ([issue](https://github.com/biopeia/embodiment/issues/26)); F-0025 recovery durability gap ([issue](https://github.com/biopeia/embodiment/issues/27)); F-0026 documentation inconsistency (open); F-0027 implementation finding ([issue](https://github.com/biopeia/embodiment/issues/20)) |

### Articulated body specification, active morphology and joint state

`component.embodiment-articulated-body` · component · CURRENT

| | |
|---|---|
| Identifier | `EMB-ART` |
| Responsible for | the description of one body's segments, hinge joints and topology, its binding to a body, an embodiment episode and a morphology revision, and the position and velocity of every joint of that body at one World causal tick |
| Must not | execute a solver or let a solver change the state; coordinate or commit a World causal cut; treat the position of a joint in a collection as its identity; authenticate the origin of a morphology descriptor |
| Owned by | embodiment; also involves world |
| Explained in | [explanation/embodiment/articulated-body.md](../explanation/embodiment/articulated-body.md) |
| Implemented in | `embodiment:src/embodiment/physics3d/articulated_spec.py`, `embodiment:src/embodiment/physics3d/mechanics.py`, `embodiment:src/embodiment/physics3d/articulated_state.py` |
| State | owner embodiment, family embodiment_local; birth: initialize, checkpoint: preserve, restart: preserve, reembodiment: reset, reproduction: not_inherited |
| Cross-domain contracts | Owner checkpoint validation (structural); Correlation of a physical step (fixture_only) |
| Depends on | `component.embodiment-physical-state` |
| Governed by | [technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md](../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md), [technical/adr/ADR-0098-physical-substrate-and-causal-integration.md](../technical/adr/ADR-0098-physical-substrate-and-causal-integration.md), [technical/adr/ADR-0104-body-schema-and-competence.md](../technical/adr/ADR-0104-body-schema-and-competence.md), [technical/adr/ADR-0094-somatic-state-ownership-body-holds-organism-regulates-and-feels.md](../technical/adr/ADR-0094-somatic-state-ownership-body-holds-organism-regulates-and-feels.md), [technical/adr/ADR-0095-surviving-semantic-authorities.md](../technical/adr/ADR-0095-surviving-semantic-authorities.md), [technical/design/runtime/biopeia-physical-step-integration-v1.md](../technical/design/runtime/biopeia-physical-step-integration-v1.md) |
| Tests | `embodiment:tests/test_articulated_spec.py`, `embodiment:tests/test_physics3d_mechanics.py`, `embodiment:tests/test_articulated_state.py`, `world:tests/integration/physical_step/test_first_biopeia_physical_causal_step.py` |
| Reviewed at | embodiment@a5129f03aa4b, world@c162b67e698d (RECORDED) |
| Known findings | F-0115 contract gap ([issue](https://github.com/biopeia/embodiment/issues/32)); F-0116 recovery durability gap ([issue](https://github.com/biopeia/embodiment/issues/33)); F-0117 implementation finding (open); F-0118 implementation finding (open); F-0121 implementation finding (open) |

### Physical projection for a solver, body pose sample, declared conventions and physical duration

`mechanism.embodiment-physical-projection` · mechanism · CURRENT

| | |
|---|---|
| Owned by | embodiment; also involves world, environment |
| Explained in | [explanation/embodiment/physical-projection.md](../explanation/embodiment/physical-projection.md) |
| Implemented in | `embodiment:src/embodiment/physics3d/physical_projection.py`, `embodiment:src/embodiment/observation.py`, `embodiment:src/embodiment/physics3d/observation_contract.py`, `embodiment:src/embodiment/duration.py` |
| Cross-domain contracts | Body physical input to a solver (fixture_only); Frame and unit conventions between body and scene (by_convention) |
| Depends on | `component.embodiment-articulated-body`, `component.embodiment-physical-state` |
| Governed by | [technical/adr/ADR-0098-physical-substrate-and-causal-integration.md](../technical/adr/ADR-0098-physical-substrate-and-causal-integration.md), [technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md](../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md), [technical/adr/ADR-0090-host-wall-clock-time-is-never-implicit-causal-authority.md](../technical/adr/ADR-0090-host-wall-clock-time-is-never-implicit-causal-authority.md), [technical/design/runtime/biopeia-physical-step-integration-v1.md](../technical/design/runtime/biopeia-physical-step-integration-v1.md) |
| Tests | `embodiment:tests/test_physical_projection.py`, `embodiment:tests/test_body_pose_sample.py`, `embodiment:tests/test_physics3d_observation_contract.py`, `embodiment:tests/test_duration.py`, `world:tests/integration/physical_step/test_first_biopeia_physical_causal_step.py`, `world:tests/integration/physical_step/test_procedural_sphere_world_step.py` |
| Reviewed at | embodiment@a5129f03aa4b, world@c162b67e698d (RECORDED) |
| Known findings | F-0115 contract gap ([issue](https://github.com/biopeia/embodiment/issues/32)); F-0119 contract gap (open); F-0120 contract gap (open) |

## Organism

### From an affordance to a motor command

`mechanism.organism-action-path` · mechanism · CURRENT

| | |
|---|---|
| Owned by | organism; also involves world, embodiment |
| Explained in | [explanation/organism/action-path.md](../explanation/organism/action-path.md) |
| Implemented in | `organism:src/organism/agency/affordance.py`, `organism:src/organism/agency/prospective.py`, `organism:src/organism/agency/intention.py`, `organism:src/organism/actuation/action.py`, `organism:src/organism/actuation/arbitration.py`, `organism:src/organism/actuation/commitment.py`, `organism:src/organism/actuation/controller.py`, `organism:src/organism/actuation/command.py`, `organism:src/organism/actuation/surface.py`, `organism:src/organism/actuation/system.py`, `world:tests/integration/physical_step/test_first_biopeia_physical_causal_step.py` |
| Cross-domain contracts | Motor command from Organism to Embodiment (structural) |
| Depends on | `mechanism.physical-causal-step` |
| Governed by | [technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md](../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md), [technical/adr/ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md](../technical/adr/ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md), [technical/adr/ADR-0095-surviving-semantic-authorities.md](../technical/adr/ADR-0095-surviving-semantic-authorities.md) |
| Tests | `organism:tests/source_unit/agency/test_executive_admission.py`, `organism:tests/source_unit/actuation/test_command_binding.py`, `organism:tests/source_unit/actuation/test_surface.py`, `organism:tests/source_unit/actuation/test_system.py` |
| Reviewed at | organism@6543188ff302, world@f496422a5cfb (RECORDED) |
| Known findings | F-0030 contract gap ([issue](https://github.com/biopeia/organism/issues/30)); F-0032 contract gap ([issue](https://github.com/biopeia/organism/issues/32)); F-0035 implementation finding (open); F-0037 evidence gap (open); F-0038 documentation inconsistency (open) |

### Organism identity and the checkpoint envelope

`component.organism-identity-checkpoint` · component · CURRENT

| | |
|---|---|
| Identifier | `ORG-IDC` |
| Responsible for | the value that identifies one Organism and the envelope that carries its opaque private state with the references needed to restore it |
| Must not | interpret, assemble or restore the private state it carries; generate an identity from host entropy; claim to record continuations, branches or which checkpoint of an identity is canonical; claim that the declared dependencies are all the private state requires |
| Owned by | organism; also involves world |
| Explained in | [explanation/organism/identity-and-checkpoint.md](../explanation/organism/identity-and-checkpoint.md) |
| Implemented in | `organism:src/organism/identity.py`, `organism:src/organism/checkpoint.py`, `organism:src/organism/cognition/portable_checkpoint.py` |
| State | owner organism, family identity_longitudinal; birth: initialize, checkpoint: preserve, restart: preserve, reembodiment: preserve, reproduction: not_inherited |
| Governed by | [technical/adr/ADR-0081-the-canonical-organism-is-longitudinal.md](../technical/adr/ADR-0081-the-canonical-organism-is-longitudinal.md), [technical/adr/ADR-0091-one-non-terminated-continuation-per-organism-identity.md](../technical/adr/ADR-0091-one-non-terminated-continuation-per-organism-identity.md), [technical/adr/ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md](../technical/adr/ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md), [technical/adr/ADR-0103-portable-organism-state.md](../technical/adr/ADR-0103-portable-organism-state.md) |
| Tests | `organism:tests/test_identity.py`, `organism:tests/test_checkpoint.py`, `organism:tests/source_unit/cognition/test_portable_checkpoint.py` |
| Reviewed at | organism@6543188ff302 (RECORDED) |
| Known findings | F-0031 contract gap ([issue](https://github.com/biopeia/organism/issues/31)); F-0033 contract gap ([issue](https://github.com/biopeia/organism/issues/33)); F-0034 implementation finding (open) |

### Executive outcome ledger

`component.organism-executive-outcome-ledger` · component · CURRENT

| | |
|---|---|
| Identifier | `ORG-EOL` |
| Responsible for | a bounded table of the last classified outcomes recorded for each pair of competence and anticipated effect, and any suppression recorded for the pair |
| Must not | observe outcomes itself or classify anything it is not told; write causal evidence, controllability, agency or competence evidence; act as a reward or select an action |
| Owned by | organism |
| Explained in | [explanation/organism/executive-outcome-ledger.md](../explanation/organism/executive-outcome-ledger.md) |
| Implemented in | `organism:src/organism/agency/executive_outcome.py`, `organism:src/organism/agency/prospective.py` |
| State | owner organism, family adaptive_longitudinal; birth: empty, checkpoint: preserve, restart: preserve, reembodiment: preserve, reproduction: not_inherited |
| Depends on | `mechanism.organism-action-path` |
| Governed by | [technical/adr/ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md](../technical/adr/ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md), [technical/adr/ADR-0095-surviving-semantic-authorities.md](../technical/adr/ADR-0095-surviving-semantic-authorities.md) |
| Tests | `organism:tests/source_unit/agency/test_executive_outcome.py` |
| Reviewed at | organism@6543188ff302 (RECORDED) |
| Known findings | F-0036 implementation finding (open); F-0037 evidence gap (open); F-0038 documentation inconsistency (open) |

### Competence development engine

`component.organism-competence-development` · component · CURRENT

| | |
|---|---|
| Identifier | `ORG-ACD` |
| Responsible for | the statistics of four-step activation sequences observed for one body, the motor primitives derived from them, and the position of its deterministic exploration |
| Must not | issue a commitment or a motor command; interpret the names of body signals or actuator channels; start a replay that no caller requested; claim to produce the competence records that bindings and affordances require |
| Owned by | organism |
| Explained in | [explanation/organism/competence-development.md](../explanation/organism/competence-development.md) |
| Implemented in | `organism:src/organism/actuation/sensorimotor.py`, `organism:src/organism/actuation/competence.py`, `organism:src/organism/actuation/composition.py`, `organism:src/organism/actuation/exploration.py`, `organism:src/organism/agency/candidates.py` |
| State | owner organism, family adaptive_longitudinal; birth: empty, checkpoint: preserve, restart: preserve, reembodiment: reset, reproduction: not_inherited |
| Depends on | `mechanism.organism-action-path` |
| Governed by | [technical/adr/ADR-0090-host-wall-clock-time-is-never-implicit-causal-authority.md](../technical/adr/ADR-0090-host-wall-clock-time-is-never-implicit-causal-authority.md), [technical/adr/ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md](../technical/adr/ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md), [technical/adr/ADR-0104-body-schema-and-competence.md](../technical/adr/ADR-0104-body-schema-and-competence.md) |
| Tests | `organism:tests/source_unit/actuation/test_sensorimotor.py`, `organism:tests/source_unit/actuation/test_causal_probing.py`, `organism:tests/source_unit/actuation/test_genome_motor_genes.py`, `organism:tests/source_unit/agency/test_candidates.py` |
| Reviewed at | organism@6543188ff302 (RECORDED) |
| Known findings | F-0100 contract gap ([issue](https://github.com/biopeia/organism/issues/39)); F-0101 contract gap ([issue](https://github.com/biopeia/organism/issues/40)); F-0102 recovery durability gap ([issue](https://github.com/biopeia/organism/issues/41)); F-0103 implementation finding ([issue](https://github.com/biopeia/organism/issues/42)); F-0105 evidence gap (open); F-0106 implementation finding (open); F-0107 documentation inconsistency (open) |

### Effects, causal evidence and controllability

`component.organism-causal-evidence` · component · CURRENT

| | |
|---|---|
| Identifier | `ORG-ACE` |
| Responsible for | a bounded list of reported transitions and passive windows with the effect observed in each, the registry of effect identifiers, and the estimates computed from their counts |
| Must not | observe a body or issue a command; write a competence, a binding or an affordance; claim that a difference of observed rates establishes a cause |
| Owned by | organism |
| Explained in | [explanation/organism/causal-evidence-and-controllability.md](../explanation/organism/causal-evidence-and-controllability.md) |
| Implemented in | `organism:src/organism/actuation/effects.py`, `organism:src/organism/actuation/evidence.py`, `organism:src/organism/actuation/model.py`, `organism:src/organism/actuation/intervention.py`, `organism:src/organism/actuation/dimension.py`, `organism:src/organism/actuation/attempt.py`, `organism:src/organism/actuation/footprint.py` |
| State | owner organism, family adaptive_longitudinal; birth: empty, checkpoint: preserve, restart: preserve, reembodiment: preserve, reproduction: not_inherited |
| Depends on | `mechanism.organism-action-path` |
| Governed by | [technical/adr/ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md](../technical/adr/ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md), [technical/adr/ADR-0095-surviving-semantic-authorities.md](../technical/adr/ADR-0095-surviving-semantic-authorities.md), [technical/adr/ADR-0104-body-schema-and-competence.md](../technical/adr/ADR-0104-body-schema-and-competence.md) |
| Tests | `organism:tests/source_unit/actuation/test_effect_atoms.py`, `organism:tests/source_unit/actuation/test_causal_footprints.py` |
| Reviewed at | organism@6543188ff302 (RECORDED) |
| Known findings | F-0100 contract gap ([issue](https://github.com/biopeia/organism/issues/39)); F-0102 recovery durability gap ([issue](https://github.com/biopeia/organism/issues/41)); F-0103 implementation finding ([issue](https://github.com/biopeia/organism/issues/42)); F-0105 evidence gap (open); F-0106 implementation finding (open); F-0107 documentation inconsistency (open) |

### Execution bindings, availability and the affordance resolver

`component.organism-execution-binding` · component · CURRENT

| | |
|---|---|
| Identifier | `ORG-AEB` |
| Responsible for | one row per competence recording the surface it was last confirmed on, the evidence references, a status and its revision |
| Must not | change a binding's status without a caller; issue a commitment or a motor command; determine which surface or embodiment is current; claim to prevent an action: nothing on the action path consults it |
| Owned by | organism |
| Explained in | [explanation/organism/execution-binding-and-affordances.md](../explanation/organism/execution-binding-and-affordances.md) |
| Implemented in | `organism:src/organism/actuation/binding.py`, `organism:src/organism/agency/availability.py`, `organism:src/organism/agency/affordances.py` |
| State | owner organism, family embodiment_local; birth: empty, checkpoint: preserve, restart: preserve, reembodiment: invalidate_authority, reproduction: not_inherited |
| Depends on | `mechanism.organism-action-path`, `component.organism-competence-development`, `component.organism-causal-evidence`, `component.organism-executive-outcome-ledger` |
| Governed by | [technical/adr/ADR-0095-surviving-semantic-authorities.md](../technical/adr/ADR-0095-surviving-semantic-authorities.md), [technical/adr/ADR-0104-body-schema-and-competence.md](../technical/adr/ADR-0104-body-schema-and-competence.md) |
| Tests | `organism:tests/source_unit/agency/test_competence_availability.py` |
| Reviewed at | organism@6543188ff302 (RECORDED) |
| Known findings | F-0100 contract gap ([issue](https://github.com/biopeia/organism/issues/39)); F-0101 contract gap ([issue](https://github.com/biopeia/organism/issues/40)); F-0102 recovery durability gap ([issue](https://github.com/biopeia/organism/issues/41)); F-0103 implementation finding ([issue](https://github.com/biopeia/organism/issues/42)); F-0105 evidence gap (open); F-0106 implementation finding (open); F-0107 documentation inconsistency (open) |

### Prospective deliberation and the outcome-value ledger

`component.organism-prospective-deliberation` · component · CURRENT

| | |
|---|---|
| Identifier | `ORG-APD` |
| Responsible for | running statistics of the values recorded for each outcome string, alone and per context digest |
| Must not | predict an outcome itself; record a value it was not given; execute, commit or admit an action |
| Owned by | organism |
| Explained in | [explanation/organism/prospective-deliberation.md](../explanation/organism/prospective-deliberation.md) |
| Implemented in | `organism:src/organism/agency/prospective.py`, `organism:src/organism/agency/policy.py`, `organism:src/organism/agency/value.py`, `organism:src/organism/agency/readiness.py`, `organism:src/organism/agency/types.py`, `organism:src/organism/agency/checkpoint.py` |
| State | owner organism, family adaptive_longitudinal; birth: empty, checkpoint: preserve, restart: preserve, reembodiment: preserve, reproduction: not_inherited |
| Depends on | `mechanism.organism-action-path`, `component.organism-competence-development` |
| Governed by | [technical/adr/ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md](../technical/adr/ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md), [technical/adr/ADR-0095-surviving-semantic-authorities.md](../technical/adr/ADR-0095-surviving-semantic-authorities.md), [technical/adr/ADR-0105-cognition-structure.md](../technical/adr/ADR-0105-cognition-structure.md) |
| Tests | `organism:tests/source_unit/agency/test_prospective.py`, `organism:tests/source_unit/agency/test_policy.py`, `organism:tests/source_unit/agency/test_value.py` |
| Reviewed at | organism@6543188ff302 (RECORDED) |
| Known findings | F-0100 contract gap ([issue](https://github.com/biopeia/organism/issues/39)); F-0102 recovery durability gap ([issue](https://github.com/biopeia/organism/issues/41)); F-0104 implementation finding (open); F-0105 evidence gap (open) |

## Modality

### Modality: decided role and current state of the repository

`concept.modality-current-state` · concept · TARGET

| | |
|---|---|
| Owned by | modality; also involves world, organism |
| Explained in | [explanation/modality/current-state.md](../explanation/modality/current-state.md) |
| Implemented in | `modality:src/modality/__init__.py` |
| Cross-domain contracts | Body interoception (shared_type) |
| Governed by | [technical/adr/ADR-0099-modality-contract-library.md](../technical/adr/ADR-0099-modality-contract-library.md), [technical/adr/ADR-0095-surviving-semantic-authorities.md](../technical/adr/ADR-0095-surviving-semantic-authorities.md), [technical/adr/ADR-0110-repository-consequence-and-dependency-direction.md](../technical/adr/ADR-0110-repository-consequence-and-dependency-direction.md), [technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md](../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md), [technical/design/runtime/biopeia-physical-step-integration-v1.md](../technical/design/runtime/biopeia-physical-step-integration-v1.md) |
| Tests | `modality:tests/test_unratified_surface.py`, `world:tests/integration/test_first_biopeia_causal_tick.py` |
| Reviewed at | modality@9bd1b77c9eab, world@c162b67e698d (RECORDED) |
| Known findings | F-0050 implementation finding (accepted); F-0051 documentation inconsistency ([issue](https://github.com/biopeia/modality/issues/11)); F-0052 documentation inconsistency ([issue](https://github.com/biopeia/modality/issues/12)); F-0053 documentation inconsistency (open); F-0054 documentation inconsistency (open); F-0055 evidence gap ([issue](https://github.com/biopeia/modality/issues/13)); F-0056 contract gap (open); F-0057 contract gap (open); F-0058 documentation inconsistency (open) |

## Observation

### Semantic claim model

`component.observation-semantic-claim-model` · component · CURRENT

| | |
|---|---|
| Identifier | `OBS-SEM` |
| Responsible for | the shape of a semantic claim and of an observation of it, and the few cross-field rules checked when one is built; no state and no meaning |
| Must not | be the authority for any claim it describes; define a semantic family, a contract, units, a wire format or a transport; be imported by the source packages of the authorities |
| Owned by | observation |
| Explained in | [explanation/observation/semantic-claim-model.md](../explanation/observation/semantic-claim-model.md) |
| Implemented in | `observation:src/observation/semantic.py` |
| State | owner implementation-local, family ephemeral |
| Cross-domain contracts | Observation of a committed cut (fixture_only) |
| Governed by | [technical/adr/ADR-0100-observation-capability-and-evidence-custody.md](../technical/adr/ADR-0100-observation-capability-and-evidence-custody.md), [technical/adr/ADR-0095-surviving-semantic-authorities.md](../technical/adr/ADR-0095-surviving-semantic-authorities.md), [technical/adr/ADR-0099-modality-contract-library.md](../technical/adr/ADR-0099-modality-contract-library.md), [technical/design/observability/observation-semantic-model-v1.md](../technical/design/observability/observation-semantic-model-v1.md), [technical/design/observation/observation-architecture-biopeia-v1.md](../technical/design/observation/observation-architecture-biopeia-v1.md) |
| Tests | `observation:tests/test_semantic_model.py` |
| Reviewed at | observation@397c0b4691b5, world@c162b67e698d (RECORDED) |
| Known findings | F-0041 implementation finding ([issue](https://github.com/biopeia/observation/issues/14)); F-0044 implementation finding (accepted); F-0046 contract gap (open) |

### Observation plane

`component.observation-plane` · component · CURRENT

| | |
|---|---|
| Identifier | `OBS-PLN` |
| Responsible for | an in-memory delivery sequence, a bounded replay history, a bounded last-published view per key, and the queues of its open streams |
| Must not | alter, validate or interpret an observation, or decide what it means; present the delivery sequence as domain or causal time; call back into a producer or carry a command; claim durability, resumption across restarts or custody of evidence |
| Owned by | observation |
| Explained in | [explanation/observation/observation-plane.md](../explanation/observation/observation-plane.md) |
| Implemented in | `observation:src/observation/plane.py` |
| State | owner implementation-local, family ephemeral |
| Cross-domain contracts | Observation of a committed cut (fixture_only) |
| Depends on | `component.observation-semantic-claim-model` |
| Governed by | [technical/adr/ADR-0078-observation-is-causally-passive.md](../technical/adr/ADR-0078-observation-is-causally-passive.md), [technical/adr/ADR-0100-observation-capability-and-evidence-custody.md](../technical/adr/ADR-0100-observation-capability-and-evidence-custody.md), [technical/adr/ADR-0101-operator-control.md](../technical/adr/ADR-0101-operator-control.md), [technical/design/observation/observation-architecture-biopeia-v1.md](../technical/design/observation/observation-architecture-biopeia-v1.md), [technical/design/observability/observation-semantic-model-v1.md](../technical/design/observability/observation-semantic-model-v1.md) |
| Tests | `observation:tests/test_plane.py` |
| Reviewed at | observation@397c0b4691b5 (RECORDED) |
| Known findings | F-0040 implementation finding ([issue](https://github.com/biopeia/observation/issues/13)); F-0041 implementation finding ([issue](https://github.com/biopeia/observation/issues/14)); F-0043 evidence gap ([issue](https://github.com/biopeia/observation/issues/16)); F-0044 implementation finding (accepted); F-0045 implementation finding (open); F-0047 contract gap (accepted); F-0049 performance concern (open) |

### Inherited projection

`component.observation-inherited-projection` · component · CURRENT

| | |
|---|---|
| Identifier | `OBS-PRJ` |
| Responsible for | a fixed list of copied key names, the grouping of them into three records, and a frame record with constant provenance labels; no state |
| Must not | read a domain, hold state or deliver anything; be taken as a compatibility promise, a ratified contract or the meaning of the keys it copies; emit either metabolic reserve key |
| Owned by | observation; also involves lab, world |
| Explained in | [explanation/observation/inherited-projection.md](../explanation/observation/inherited-projection.md) |
| Implemented in | `observation:src/observation/projection.py`, `observation:src/observation/contracts.py` |
| State | owner implementation-local, family ephemeral |
| Cross-domain contracts | Telemetry through the inherited projection (shared_type) |
| Governed by | [technical/adr/ADR-0078-observation-is-causally-passive.md](../technical/adr/ADR-0078-observation-is-causally-passive.md), [technical/adr/ADR-0100-observation-capability-and-evidence-custody.md](../technical/adr/ADR-0100-observation-capability-and-evidence-custody.md), [technical/adr/ADR-0085-project-identity-is-biopeia-and-the-individual-is-organism.md](../technical/adr/ADR-0085-project-identity-is-biopeia-and-the-individual-is-organism.md), [technical/design/observation/observation-architecture-biopeia-v1.md](../technical/design/observation/observation-architecture-biopeia-v1.md) |
| Tests | `observation:tests/test_projection.py` |
| Reviewed at | observation@397c0b4691b5, world@c162b67e698d, lab@4d5ff706b832 (RECORDED) |
| Known findings | F-0042 contract gap ([issue](https://github.com/biopeia/observation/issues/15)); F-0048 implementation finding (open) |

## Lab

### Operator material transfer

`component.lab-operator-material-transfer` · component · CURRENT

| | |
|---|---|
| Identifier | `LAB-OMT` |
| Responsible for | the intervention request as declared by the caller, the order in which Environment, Embodiment and World are asked, and the intervention evidence checkpoint with the files of its store |
| Must not | decide how much the resource offers or is debited, or how much the body accepts; change the owners' objects in place or adopt a state World has not committed; treat the operator identifier as authentication or authorisation; claim equivalence to an endogenous physical mechanism, or present a transfer as a scientific result |
| Owned by | lab; also involves environment, embodiment, world, observation |
| Explained in | [explanation/lab/operator-material-transfer.md](../explanation/lab/operator-material-transfer.md) |
| Implemented in | `lab:src/lab/interventions/material_transfer.py`, `embodiment:src/embodiment/intake.py`, `environment:src/environment/identified_resource.py`, `observation:src/observation/projection.py`, `world:src/world/durable_runtime.py` |
| State | owner lab, family evidence_record |
| Cross-domain contracts | Owner checkpoint validation (structural); Operator material transfer (shared_type); Telemetry through the inherited projection (shared_type) |
| Depends on | `component.environment-finite-resource`, `component.world-durable-runtime` |
| Governed by | [technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md](../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md), [technical/adr/ADR-0100-observation-capability-and-evidence-custody.md](../technical/adr/ADR-0100-observation-capability-and-evidence-custody.md), [technical/adr/ADR-0101-operator-control.md](../technical/adr/ADR-0101-operator-control.md), [technical/adr/ADR-0102-lab.md](../technical/adr/ADR-0102-lab.md) |
| Tests | `lab:tests/integration/test_material_transfer_intervention.py`, `lab:tests/integration/test_operator_material_transfer.py` |
| Reviewed at | lab@4d5ff706b832, embodiment@a5129f03aa4b, environment@f97ec22272b6, observation@397c0b4691b5, world@9da5ecce209e (RECORDED) |
| Known findings | F-0060 recovery durability gap ([issue](https://github.com/biopeia/lab/issues/31)); F-0061 contract gap ([issue](https://github.com/biopeia/lab/issues/32)); F-0062 implementation finding ([issue](https://github.com/biopeia/lab/issues/33)); F-0063 contract gap (open); F-0065 evidence gap (accepted); F-0068 documentation inconsistency (open) |

### Study utilities

`component.lab-study-utilities` · component · CURRENT

| | |
|---|---|
| Identifier | `LAB-STU` |
| Responsible for | nothing persistent; pure computations over seed lists, lists of scalar measurements, an event stream of one historical shape and a configuration dictionary |
| Must not | run experiments, own simulated life or carry scientific artifacts; be read as a test of significance or as evidence of an effect; be taken for a digest of a Biopeia World |
| Owned by | lab |
| Explained in | [explanation/lab/study-utilities.md](../explanation/lab/study-utilities.md) |
| Implemented in | `lab:src/lab/studies/common/pairing.py`, `lab:src/lab/studies/common/statistics.py`, `lab:src/lab/studies/common/digests.py` |
| State | owner implementation-local, family ephemeral |
| Tests | `lab:tests/unit/test_pairing.py`, `lab:tests/unit/test_statistics.py`, `lab:tests/unit/test_digests.py` |
| Reviewed at | lab@c73f5b4321bf (RECORDED) |
| Known findings | F-0064 implementation finding ([issue](https://github.com/biopeia/lab/issues/34)); F-0066 implementation finding (open) |

### Body interoception transducer

`component.lab-body-interoception-transducer` · component · CURRENT

| | |
|---|---|
| Identifier | `LAB-INT` |
| Responsible for | the permutation that assigns four body-state sources to four caller-named slots |
| Must not | assign labels, valence or action meaning to the values; change the body state it reads or own any physiology; claim scientific validity |
| Owned by | lab; also involves embodiment |
| Explained in | [explanation/lab/body-interoception-transducer.md](../explanation/lab/body-interoception-transducer.md) |
| Implemented in | `lab:src/lab/apparatus/interoception.py` |
| State | owner lab, family infrastructure |
| Cross-domain contracts | Body interoception (shared_type) |
| Governed by | [technical/adr/ADR-0094-somatic-state-ownership-body-holds-organism-regulates-and-feels.md](../technical/adr/ADR-0094-somatic-state-ownership-body-holds-organism-regulates-and-feels.md), [technical/adr/ADR-0099-modality-contract-library.md](../technical/adr/ADR-0099-modality-contract-library.md) |
| Tests | `lab:tests/unit/test_interoception.py` |
| Reviewed at | lab@4d5ff706b832 (RECORDED) |
| Known findings | F-0067 contract gap (open); F-0068 documentation inconsistency (open) |
