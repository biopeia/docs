# Cross-Domain Source Disposition Reconciliation

Pinned historical source: [`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`](https://github.com/alessbarb/symbiont-lab/tree/80d372a186513035f85a769db886e505cabba52d).  
Target coordination authority: `biopeia/docs` under issue [biopeia/docs#63](https://github.com/biopeia/docs/issues/63).  
Governing ADRs and Ratifications: [ADR-0074](../adr/ADR-0074-biopeia-world-environment-authority-split.md), [ADR-0075](../adr/ADR-0075-authority-boundaries-derive-from-semantic-ownership-not-repository-topology.md), [ADR-0094](../adr/ADR-0094-somatic-state-ownership-body-holds-organism-regulates-and-feels.md), [ADR-0095](../adr/ADR-0095-surviving-semantic-authorities.md), [ADR-0099](../adr/ADR-0099-modality-contract-library.md), [ADR-0102](../adr/ADR-0102-lab.md), and [ADR-0110](../adr/ADR-0110-repository-consequence-and-dependency-direction.md).

---

## 1. Context and Objective

The migration audit (`AUDITORIA_MIGRACION_BIOPEIA_2026-10-10.md`, SHA-256 `78f69a8b2fee...`) identified two major classes of cross-ledger discrepancies across child repositories:

1. **Audit Section 6 (Mislabeled extraction rows):** 32 ledger rows in `biopeia/organism` marked `SPLIT` pointing to whole byte-identical copies of source modules.
2. **Audit Section 7 (Cross-ledger contradictory dispositions):** 56 source paths receiving differing final dispositions depending on the individual repository ledger consulted (e.g. `core/embodiment/**` claiming `REWRITE`/`SPLIT` in Organism vs `DEFER`/`DROP` in Embodiment; `environment/**` claiming `DROP` in Environment vs `SPLIT` in World; `core/orchestration/runtime.py` claiming `SPLIT+REWRITE` in Lab, `DEFER` in Modality, and `DROP` in Organism).

This coordination document records the **single authoritative cross-domain adjudication** for these items. Individual child repository implementation and local ledger maintenance remain with each domain owner (specifically tracked under [biopeia/organism#59](https://github.com/biopeia/organism/issues/59) for Organism).

---

## 2. Audit Section 6 Reconciliation: Source-Identical Organism Extractions

Under User Constraint [`UC-0001`](../adr/README.md#uc-0001) and ADR-0075, a direct whole-file extraction with package-import retargeting is classified as **`MOVE (copy-first with package retargeting)`** rather than `SPLIT`. Calling byte-identical files `SPLIT` incorrectly suggests an architectural decomposition that did not occur during initial extraction.

The 30 affected source files (corresponding to 32 historical `SPLIT` rows in `organism/MIGRATION.md`) are listed below with their immutable source blobs at `80d372a`:

| Source path at pinned revision | Pinned Blob SHA-1 | Authoritative Disposition | Target path in `biopeia/organism` | Notes and Tracking |
|---|---|---|---|---|
| `symbiont/src/symbiont/actuation/action.py` | `e2ebd9f5d62643e2c5922be9f7decd4c7fb72420` | `MOVE (copy-first)` | `src/organism/actuation/action.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/actuation/arbitration.py` | `ca000816df835cb430f2576361f607c1394e5188` | `MOVE (copy-first)` | `src/organism/actuation/arbitration.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/actuation/attempt.py` | `7881ec6720a2b26c5317e577b042516a047e76fa` | `MOVE (copy-first)` | `src/organism/actuation/attempt.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/actuation/competence.py` | `fa4febc9849392f2f707311df8629e979e4e07a2` | `MOVE (copy-first)` | `src/organism/actuation/competence.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/actuation/evidence.py` | `b5a57b2e9841b3a45fd48d6a9c11d9c92a59f67d` | `MOVE (copy-first)` | `src/organism/actuation/evidence.py` | Full copy (662 lines); tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/actuation/exploration.py` | `29c8e1ca7c1a2a9459fcce535c049479a62d565b` | `MOVE (copy-first)` | `src/organism/actuation/exploration.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/actuation/footprint.py` | `75e86d26c51bda210765304b23dacd4e2bb7ad98` | `MOVE (copy-first)` | `src/organism/actuation/footprint.py` | Full copy (896 lines); tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/actuation/types.py` | `1acae3f80eadc1976bd0a05a4bbde806343c3709` | `MOVE (copy-first)` | `src/organism/actuation/types.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/agency/__init__.py` | `24d4a203707ca6f108616e5befc08a9954742875` | `MOVE (copy-first)` | `src/organism/agency/__init__.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/agency/affordance.py` | `93809f36ff12a4907d1b763b640d9d48a21f23b8` | `MOVE (copy-first)` | `src/organism/agency/affordance.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/agency/affordances.py` | `771728686a71060d06a162ce71697bf31eb30cad` | `MOVE (copy-first)` | `src/organism/agency/affordances.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/agency/availability.py` | `c64ac9cd7fcd96e889b6b65f6c020ae3dc9e41d6` | `MOVE (copy-first)` | `src/organism/agency/availability.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/agency/executive_outcome.py` | `71ddc5570264dfcaf97085719d4fb6463e221f9e` | `MOVE (copy-first)` | `src/organism/agency/executive_outcome.py` | Full copy (415 lines); tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/agency/invariants.py` | `5eef9115f013d33076bf2fa69ebf40aa9d3e8e50` | `MOVE (copy-first)` | `src/organism/agency/invariants.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/agency/operational.py` | `2467d0cf0c53d4ebaa2bcfce3178c5208f2fcaee` | `MOVE (copy-first)` | `src/organism/agency/operational.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/agency/policy.py` | `fb786e6616641b69c4f1c1071221f4cb84e2dd75` | `MOVE (copy-first)` | `src/organism/agency/policy.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/agency/priorities.py` | `eaef68700ef26d40398f6dffdd59bb5a1135beea` | `MOVE (copy-first)` | `src/organism/agency/priorities.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/agency/repertoire.py` | `2495d4d3c3336d31ba2ddcce89fa78832a8a815a` | `MOVE (copy-first)` | `src/organism/agency/repertoire.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/agency/telemetry.py` | `bc653063f2597ffc6fc27027376e18471c2ae913` | `MOVE (copy-first)` | `src/organism/agency/telemetry.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/capacity.py` | `3715b93dca6094553ea1fc5efda6d0cf032c5240` | `MOVE (copy-first)` | `src/organism/capacity.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/cognition/attention.py` | `07f5e718d0932ce7ec651f893693fb13a0da9b6a` | `MOVE (copy-first)` | `src/organism/cognition/attention.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/cognition/deliberation.py` | `482a5c48b2ebda41c5949d288924b1ff5fa4b46c` | `MOVE (copy-first)` | `src/organism/cognition/deliberation.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/cognition/hypotheses.py` | `ad631f496150fe1f391a82da3a3a416ea6186981` | `MOVE (copy-first)` | `src/organism/cognition/hypotheses.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/cognition/memory.py` | `9b3eb186358cfa53b3b3a62d0577df0db64e1017` | `MOVE (copy-first)` | `src/organism/cognition/memory.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/cognition/salience.py` | `561ce5d8cff381c828ca1a719941a33758b292e1` | `MOVE (copy-first)` | `src/organism/cognition/salience.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/foundation/epistemic.py` | `f3ca67c5cf7a421b8c2d1b827361eeaa863c3d52` | `MOVE (copy-first)` | `src/organism/foundation/epistemic.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/foundation/limits.py` | `82f9ef05eb4b967a57a169b1ae3104c2ae7e7811` | `MOVE (copy-first)` | `src/organism/foundation/limits.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/genetics/genome.py` | `e98bc05bf60ca3ce6fa89c09930fca68e6475fc2` | `MOVE (copy-first)` | `src/organism/genetics/genome.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/genetics/germline.py` | `888cf3e271705e45a2dc8122ffae08e6ca6fbf28` | `MOVE (copy-first)` | `src/organism/genetics/germline.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |
| `symbiont/src/symbiont/provenance.py` | `1c7d23a4b752496a7d7ef11efbce376b539cceb3` | `MOVE (copy-first)` | `src/organism/provenance.py` | Full copy; tracked in owner repo via [Organism #59](https://github.com/biopeia/organism/issues/59). |

---

## 3. Audit Section 7 Reconciliation: Cross-Ledger Contradictions

Under [ADR-0075](../adr/ADR-0075-authority-boundaries-derive-from-semantic-ownership-not-repository-topology.md), authority boundaries derive from semantic domain ownership, not repository topology or historical mono-ledger convenience. Dispositions are adjudicated according to the ratified domain owners.

### 3.1 `symbiont/src/symbiont/core/embodiment/**` (Embodiment vs Organism)

- **Authoritative Semantic Owner:** **Embodiment** (`biopeia/embodiment`) per [ADR-0094](../adr/ADR-0094-somatic-state-ownership-body-holds-organism-regulates-and-feels.md) and [ADR-0095](../adr/ADR-0095-surviving-semantic-authorities.md).
- **Adjudication Principle:** Embodiment holds concrete somatic state, morphology, energetics, and kinematic viability. Organism owns longitudinal identity, cognition, and behavioral regulation. Where Organism's historical ledger claimed `SPLIT` or `REWRITE` on somatic files, Embodiment's granular inventory in `embodiment/MIGRATION.md` is the authoritative baseline.

| Source path | Pinned Blob SHA-1 | Authoritative Disposition | Authoritative Owner | Adjudication & Target Notes |
|---|---|---|---|---|
| `core/embodiment/__init__.py` | `ea0df2cffb5b594b8df40b4b905589cac40b51f4` | `REWRITE` | Embodiment | Minimal standalone package export; no Organism or host coupling. |
| `core/embodiment/adaptation.py` | `85edb6a3713777d32b6a7cbe4f26757042504d22` | `DROP` | Embodiment | Legacy somatic adaptation heuristics replaced by domain-owned rates; excluded from target. |
| `core/embodiment/agency.py` | `8e452d866061d7bef83e1bfe6631be25f489d15b` | `SPLIT` | Embodiment / Organism | Sensorimotor capability constraints stay in Embodiment; cognitive agency delegated to Organism. |
| `core/embodiment/assimilation.py` | `28c9824474f2ad50b347c928772b361cefbbb9e5` | `SPLIT` | Embodiment / Organism | Somatic intake in Embodiment (`src/embodiment/intake.py`); experiential learning in Organism. |
| `core/embodiment/body.py` | `84d57d7a820070699314f3e21d0349da18751398` | `SPLIT` | Embodiment | Somatic intake/energy in `intake.py`; `tick_physics()` is `DROP` (no legacy monolithic physics tick). |
| `core/embodiment/body_schema.py` | `909c67c8988e95186aab3053210a847c1761a7ba` | `SPLIT` | Embodiment / Organism | Physical morphology schema in Embodiment; cognitive self-model representation in Organism. |
| `core/embodiment/contract.py` | `85076bceaff300ff4a593f4bdc81ae78de1751b4` | `REWRITE` | Embodiment | Target-owned typed contracts (`src/embodiment/contracts.py`). |
| `core/embodiment/degradation.py` | `cfc40aebf5afa228108ca00f29b439fe83ff0c06` | `DROP` | Embodiment | Monolithic wear formulas dropped; replaced by target-specific viability rules. |
| `core/embodiment/development.py` | `a727788628fbf86b311c66c4403387ac6e56ab00` | `SPLIT` | Embodiment / Organism | Somatic growth/scaling in Embodiment; developmental cognitive milestones in Organism. |
| `core/embodiment/duration.py` | `965fd3bb62f08c2c582e5b785233955d796297ee` | `MOVE (copy-first)` | Embodiment | `PhysicalDuration` copied directly to `src/embodiment/duration.py`. |
| `core/embodiment/dynamics.py` | `579620bc4167bbcdc9e442dfc42149373c94ed91` | `DROP` | Embodiment | Legacy kinematic equations dropped; articulated physics delegated to MuJoCo / modern engine. |
| `core/embodiment/episode.py` | `e085f4edc4603200cd0a9ad3591a596e3d75b54f` | `SPLIT` | Embodiment | Episode identity and physical bounds extracted; historical container dropped. |
| `core/embodiment/history.py` | `a5d20ad2fcf1cd5156ebaa6ba690d78eddc891d7` | `DROP` | Embodiment | Monolithic trajectory history dropped; Lab owns experiment custody; World owns causal journal. |
| `core/embodiment/homeostasis.py` | `4dd604719b1d568490bc0fff29bbcd8b4a1c0e7c` | `SPLIT` | Embodiment / Organism | Physical vital reserves in Embodiment; regulatory homeostatic control in Organism. |
| `core/embodiment/lifecycle.py` | `1dd3367acaf457be5b6f4837b2440c5a750221d2` | `SPLIT` | Embodiment / World | Somatic life state (alive/dead/viable) in Embodiment; lifecycle events coordinated by World. |
| `core/embodiment/longitudinal.py` | `f4c7529be153f54199e1480a6216bdead1c4ea57` | `SPLIT` | Embodiment / Organism | Physical strain accumulation in Embodiment; longitudinal identity in Organism. |
| `core/embodiment/memory.py` | `9fe68589710a3f5f6a7514123b73ccaba602c3b7` | `DROP` | Embodiment | Somatic memory buffer dropped; Organism owns private cognitive memory. |
| `core/embodiment/metabolism.py` | `4ba6b77486d32fac7a2a98d4f32ce3707f59f1bb` | `SPLIT` | Embodiment | Somatic metabolic accounting extracted to `src/embodiment/metabolism.py`. |
| `core/embodiment/ontogeny.py` | `3f7ec7453c277d7fb905fd152628243194c73a12` | `DROP` | Embodiment | Legacy ontogenetic stage heuristics dropped. |
| `core/embodiment/physiology.py` | `be27d6590f28436c3ed02683aa0dd9173b14b355` | `SPLIT` | Embodiment | Somatic physiological state extracted to `src/embodiment/physiology.py`. |
| `core/embodiment/physiology_config.py` | `7f3c23364f4093d62ff25ac2af2373183c5cb1f7` | `SPLIT` | Embodiment | Somatic config in `src/embodiment/physiology_config.py`; `prospective_*` deferred to Organism; `somatic_reference_duration_s` is `DROP`. |
| `core/embodiment/reachability.py` | `aa20bf98182c518a8df3fdf5a3bab166122af027` | `SPLIT` | Embodiment / Organism | Kinematic reach limits in Embodiment; affordance evaluation in Organism. |
| `core/embodiment/reembodiment.py` | `e5ede03a28c335c062f222b1d11346d1741025f9` | `SPLIT` | Embodiment / Organism | Fresh morphology attachment in Embodiment; continuous identity persistence in Organism. |
| `core/embodiment/session.py` | `dfe7dfe42b4d3b6a15d839afb6d895fbe1a167b3` | `DROP` | Embodiment | Monolithic runtime session container dropped; replaced by World causal step and Lab protocol. |
| `core/embodiment/transition.py` | `4c6f47478223e67fe6234c984c832aaec4aeae18` | `DROP` | Embodiment | Legacy in-memory transition runner dropped; World durable runtime coordinates causal transitions. |

### 3.2 `environment/src/environment/**` (Environment vs World)

- **Authoritative Semantic Owners:**
  - Environmental state, fields, resources, terrain laws $\rightarrow$ **Environment** (`biopeia/environment`) per [ADR-0074](../adr/ADR-0074-biopeia-world-environment-authority-split.md).
  - Causal transactions, ordering, journals, active presence $\rightarrow$ **World** (`biopeia/world`) per [ADR-0074](../adr/ADR-0074-biopeia-world-environment-authority-split.md).
- **Adjudication Principle:** Where `environment/MIGRATION.md` recorded `DEFER`/`DROP` for causal transaction and event coordination files, it was reflecting the absence of those responsibilities in the Environment domain. The authoritative disposition across the 12 contested modules:

| Source path | Pinned Blob SHA-1 | Authoritative Disposition | Authoritative Owner | Adjudication & Target Notes |
|---|---|---|---|---|
| `environment/src/environment/checkpoint.py` | `3d586a6df303bf5dfdff49860bbde19b8fd1e556` | `SPLIT` / `REWRITE` | World | Causal manifest and checkpoint coordination belong to World (`src/world/manifest.py`); dropped from Environment. |
| `environment/src/environment/constitution.py` | `288733dbd05c697f6f538b39d99c5a9399c7dacf` | `REWRITE` | World | World manifest topology and invariant verification belong to World; dropped from Environment. |
| `environment/src/environment/contracts.py` | `72122f3da2f6683449b1cf248eba3cd147c6f6dd` | `SPLIT` | Environment / World | Environmental state contracts in Environment; presence/step participant contracts in World. |
| `environment/src/environment/deferred.py` | `afc63f1ccd1bb72ec4204689b1ede61f1267b982` | `DROP` | World / Environment | Legacy deferred transaction mechanics dropped; replaced by World two-phase prepare/commit manifest. |
| `environment/src/environment/events.py` | `0d53017ade217269d1f602dfd9710b60e27e0254` | `SPLIT` | World | Causal event journal mechanics extracted to World (`src/world/journal.py`); `WorldEvent` taxonomy is `DROP`. |
| `environment/src/environment/genesis.py` | `34d90b1b33c1434d6b21164c9ceced08603d2271` | `SPLIT` | Environment | Environmental fields and initial resource distribution extracted to Environment (`src/environment/genesis.py`). |
| `environment/src/environment/laws.py` | `5b2c1133fe7a93a42da59c72eb9d94899cf02329` | `MOVE` | Environment | Environmental laws copied to Environment (`src/environment/laws.py`). |
| `environment/src/environment/movement.py` | `12c88ad1b925478851743e4554fae26e15ca4bfb` | `SPLIT` | World / Embodiment | Spatial position and movement interaction belong to World/Embodiment integration; dropped from Environment. |
| `environment/src/environment/observation.py` | `86c19ea60ba17f58d5a44408d19bd5208730878b` | `REWRITE` | Observation | Passive perceptual projections belong to Observation domain; dropped from Environment. |
| `environment/src/environment/physics3d/resource.py` | `30a6c6eb0d5fa957863bf10731f822a9ee2b20fb` | `SPLIT` | Environment | Finite resource state extracted to Environment (`src/environment/physics3d/resource.py`). |
| `environment/src/environment/state.py` | `0fc5120235da9264486513c493963c9b88fe47bc` | `SPLIT` | Environment / World | Objective environment state in Environment; causal state cut tracking in World. |
| `environment/src/environment/topology.py` | `2bdd5eb8e99b48fb70611c78cc46cdc51a3a2415` | `SPLIT` | Environment / World | `HexCoord` coordinate primitive extracted to Environment (`src/environment/spatial.py`); occupancy grid belongs to World. |

### 3.3 `symbiont/src/symbiont/core/orchestration/runtime.py` (Lab vs Modality vs Organism)

- **Authoritative Semantic Decomposition:** **`SPLIT`** across Organism, Lab, World, and `DROP`.
  - Pinned Blob SHA-1: `c436087ec1d1f4bfab6bfa7c4e4d801514c69708`.
  - Governing Invariant: No monolithic runtime loop or combined controller survives the migration.
  - Adjudication of constituent responsibilities:
    1. **Longitudinal Identity:** Extracted and rewritten under **Organism** (`src/organism/identity.py`). Organism owns self-identity verification.
    2. **Operator Intervention Application:** Extracted and rewritten under **Lab** (`src/lab/interventions/material_transfer.py::apply_material_transfer`). Lab owns experimental intervention execution and evidence recording.
    3. **Causal Step Coordination:** Reconstructed under **World** (`src/world/durable_runtime.py`, `src/world/physical_step.py`). World coordinates step progression and causal cuts.
    4. **Modality:** Owns **no runtime authority**. Per [ADR-0099](../adr/ADR-0099-modality-contract-library.md), Modality is a contract/transducer library with zero persistent state or runtime orchestration authority. Modality's historical `DEFER` row is formally closed.
    5. **Monolithic Tick Loop & Engine:** Classified as **`DROP as TARGET runtime`**. The historical monolithic loop (`RuntimeTickResult`, tick state hashes, global thread loop) is rejected.

---

## 4. Verification and Non-Regression

- Pinned historical source revision: `80d372a186513035f85a769db886e505cabba52d` (read-only; untouched).
- All 30 Section 6 source modules and 56 Section 7 source modules have been verified against exact Git blob SHA-1s in the pinned tree.
- Cross-ledger contradictions are adjudicated definitively under ratified Architecture decisions [ADR-0074](../adr/ADR-0074-biopeia-world-environment-authority-split.md), [ADR-0075](../adr/ADR-0075-authority-boundaries-derive-from-semantic-ownership-not-repository-topology.md), [ADR-0094](../adr/ADR-0094-somatic-state-ownership-body-holds-organism-regulates-and-feels.md), [ADR-0095](../adr/ADR-0095-surviving-semantic-authorities.md), [ADR-0099](../adr/ADR-0099-modality-contract-library.md), and [ADR-0102](../adr/ADR-0102-lab.md).
