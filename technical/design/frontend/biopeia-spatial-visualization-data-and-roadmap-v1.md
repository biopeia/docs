---
id: design.cross-domain.biopeia-spatial-visualization-data-and-roadmap-v1
title: "Biopeia Spatial Visualization — Owner-Authorized Data Readiness and Roadmap"
document_type: design
owner: biopeia-project-owner
created: 2026-10-15
language: en
document_version: 1
---

# Biopeia Spatial Visualization — Owner-Authorized Data Readiness and Roadmap

## Objective

Define a reviewable, source-grounded path from the current bounded Observation
view to a future Frontend spatial renderer. The design is intentionally
independent of the M1.1 operational fixes and of M2's durable Observation
history. [Docs #164](https://github.com/biopeia/docs/issues/164) remains the
authority for accepted screen-level UX and render/fallback behavior. This
proposal adds only the spatial-specific owner decision map, the static-versus-
dynamic data decomposition question, cross-owner revision/cut readiness, and
the sequence of readiness gates needed before those UX requirements could be
implemented. If this proposal conflicts with #164, #164 remains in force until
the competent authority approves a formal update.

This document proposes readiness requirements and decisions for competent
owners. It does **not** approve or create any domain publication family,
schema, API, transport, asset store, or implementation task. The state of this
design is recorded only in `registry/designs.yaml`.

## Scope and exclusions

Affected repositories and authority boundaries:

| Concern | Semantic authority / responsibility | What this design does not transfer |
|---|---|---|
| Body morphology, body-local frames, articulation and dynamic somatic state | Embodiment | No renderer-owned body identity, morphology or joint semantics |
| Static and dynamic environmental geometry/resources | Environment | No World- or Frontend-authored terrain, object identity or resource truth |
| Causal ordering, committed-cut identity and cross-owner cut membership | World | No UI join or delivery timestamp treated as a causal commit |
| Passive carriage of approved owner claims | Observation | No schema, storage, interpretation or semantic authority |
| Scene assembly and visual fallback | Frontend | Presentation only; never a semantic authority |
| Explanatory record and dependency roadmap | Docs | Documentation does not accept the proposed contracts |

This design excludes runtime controls, interventions, scientific evidence
admission, inferred sensorimotor links, organism cognition/identity not
published by its owner, durable history/replay (M2), and implementation of
new publication contracts. Existing solver input/output, checkpoints, fixture
geometry and renderer-private scene objects are not UI contracts by virtue of
their existence.

In the registry, `participating_domains` names semantic owner domains whose
contracts may be affected. Frontend and Docs are application and documentation
roles respectively; listing them there would not make either a semantic owner.

## Current state and evidence

The source snapshot used for this proposal is:

| Repository | Revision | Relevant implementation inspected | What it demonstrates / does not demonstrate |
|---|---|---|---|
| `embodiment` | `5a23e1fbeaa31109647aec4d4dc36eddbe0a6321` | `src/embodiment/physics3d/articulated_spec.py`, `articulated_state.py`, `physical_projection.py`; `src/embodiment/observation.py` | Embodiment has owner-bound articulated morphology, joint topology/state and a BodyPose projection. This does not establish a browser-facing morphology/mesh/joint publication contract. |
| `environment` | `d09e45c40633c9b2bf927c7aec3f6326318c2ea8` | `src/environment/static_scene.py`, `physical.py`, `identified_resource.py` | Environment has explicit fixture-oriented static scene/frame/primitive values and resource projections. They are not a stable general scene or asset-delivery contract. |
| `world` | `76680345941fb627764ad831deded267dc11777c` | `src/world/causal_cycle.py`, `durable_runtime.py`, `observation_publication.py` | World owns causal coordination and committed cuts, and can correlate post-commit projections. This does not prove arbitrary owner geometry is included in a verified cut. |
| `observation` | `2f4751f53678f2210930770605844cac766b1da4` | `src/observation/semantic.py`, `embodiment.py`, `environment.py`, `http_bridge.py` | Current local/browser path is bounded to BodyPose and finite scalar-field projections. No approved geometry family or durable historical scene query was found. |
| `frontend` | `496c05dcd062eb0833abdfb1030cfb87f6f80aa7` | Current M1 UI/read adapter | The browser displays the two supported claims and explicitly reports no authorized scene geometry. It does not reconstruct meshes from claims. |
| `docs` | `16d951c` | Accepted Frontend UX/readiness designs | Docs #164 defines spatial rendering truthfulness and screen acceptance; its contract-readiness and implementation gates remain applicable. |

These are code/document inspections at the listed revisions, not owner approval
of a new spatial contract. In particular, the existence of frame descriptors,
joint topology, URDF generation, static primitives, physical-step state or
BodyPose does not establish compatible identity, asset lifetime, display
geometry or cross-owner coherence for a browser scene.

### Phase 0 current-source refresh and capability matrix

Reviewed against the following exact `origin/main` revisions on 2026-10-15.
The labels describe capability for the Spatial V1 browser objective, not the
general health or completeness of each repository. `PARTIAL` means relevant
owner data or a bounded neighboring mechanism exists but does not satisfy the
browser-rendering contract. `REQUIRES APPROVAL` marks a proposed new exposure
or cross-owner relation; it is not an implementation authorization.

| Repository and revision | Capability / classification | Source evidence | Boundary and remaining gap |
|---|---|---|---|
| Embodiment `d73315d87bbb3f2eea14e8c33812b37b59a5d72f` | `PARTIAL`; browser publication `REQUIRES APPROVAL` | [`articulated_spec.py`](https://github.com/biopeia/embodiment/blob/d73315d87bbb3f2eea14e8c33812b37b59a5d72f/src/embodiment/physics3d/articulated_spec.py), [`physical_projection.py`](https://github.com/biopeia/embodiment/blob/d73315d87bbb3f2eea14e8c33812b37b59a5d72f/src/embodiment/physics3d/physical_projection.py), [`observation.py`](https://github.com/biopeia/embodiment/blob/d73315d87bbb3f2eea14e8c33812b37b59a5d72f/src/embodiment/observation.py) | Owner-side articulated topology, morphology and physical state exist. Current approved `BodyPose` exposes root position/orientation only; it is not a segment geometry or per-link transform publication. No mesh/shape exposure follows from solver morphology. |
| Environment `d09e45c40633c9b2bf927c7aec3f6326318c2ea8` | `PARTIAL`; render projection `REQUIRES APPROVAL` | [`static_scene.py`](https://github.com/biopeia/environment/blob/d09e45c40633c9b2bf927c7aec3f6326318c2ea8/src/environment/static_scene.py), [`identified_resource.py`](https://github.com/biopeia/environment/blob/d09e45c40633c9b2bf927c7aec3f6326318c2ea8/src/environment/identified_resource.py) | Environment has owner-side ground-plane/sphere descriptors and identified resource projections, alongside the approved finite-scalar field. No browser geometry family or approval to expose solver/genesis parameters was found. |
| World `a7c8099cf6ede9cfdb8f6cf7eaefb2eab8dc9bad` | `PARTIAL`; cross-owner scene join `REQUIRES APPROVAL` | [`observation_publication.py`](https://github.com/biopeia/world/blob/a7c8099cf6ede9cfdb8f6cf7eaefb2eab8dc9bad/src/world/observation_publication.py), [`durable_runtime.py`](https://github.com/biopeia/world/blob/a7c8099cf6ede9cfdb8f6cf7eaefb2eab8dc9bad/src/world/durable_runtime.py) | World verifies each owner publication against a World-issued committed cut, owner checkpoint reference, World identity and causal tick. This generic per-claim mechanism does not itself define a complete cross-owner spatial snapshot or compatibility among geometry and dynamic claims. |
| Observation `a8b43af65b79ca4e2455bfc1ff1b55faf3d4d353` | `PARTIAL`; added family carriage `REQUIRES APPROVAL` | [`http_bridge.py`](https://github.com/biopeia/observation/blob/a8b43af65b79ca4e2455bfc1ff1b55faf3d4d353/src/observation/http_bridge.py), [`embodiment.py`](https://github.com/biopeia/observation/blob/a8b43af65b79ca4e2455bfc1ff1b55faf3d4d353/src/observation/embodiment.py), [`environment.py`](https://github.com/biopeia/observation/blob/a8b43af65b79ca4e2455bfc1ff1b55faf3d4d353/src/observation/environment.py) | The local read bridge allowlist is exactly `embodiment.body_pose` and `environment.finite_scalar_field`, with a bounded current-view response. No geometry family, durable history, or composite-scene semantics are authorized by the transport. |
| Frontend `326613b74e388d3108cbafd3bab9128a35bd2246` | `PARTIAL`; 3D renderer `ABSENT` | [`views.js`](https://github.com/biopeia/frontend/blob/326613b74e388d3108cbafd3bab9128a35bd2246/src/views.js), [`package.json`](https://github.com/biopeia/frontend/blob/326613b74e388d3108cbafd3bab9128a35bd2246/package.json), `tests/views.test.js` | Spatial Explorer displays the two allowed source claims and an explicit no-authorized-geometry fallback. No canvas/mesh renderer or Three.js/WebGL dependency exists in the current package. Existing passive acquisition/store/presentation separation remains reusable. |
| Modality `62af4aba07146d5dfdc978af07bb72111112d873` | Spatial geometry `ABSENT` | [`scalar_field.py`](https://github.com/biopeia/modality/blob/62af4aba07146d5dfdc978af07bb72111112d873/src/modality/scalar_field.py) | The inspected module is stateless, fixture-specific scalar transduction and explicitly assigns no environmental or sensory semantics. It supplies no spatial geometry or transform authority. |
| Organism `d8ed534d48188fb2f629faaa8dd85b95063a0c2d` | Spatial publication `ABSENT` in inspected contracts | [`actuation/command.py`](https://github.com/biopeia/organism/blob/d8ed534d48188fb2f629faaa8dd85b95063a0c2d/src/organism/actuation/command.py), [`actuation/evidence.py`](https://github.com/biopeia/organism/blob/d8ed534d48188fb2f629faaa8dd85b95063a0c2d/src/organism/actuation/evidence.py) | Organism has internal actuation/evidence state, including passive bodily-change evidence, but no authorized spatial-visualization publication was found in the inspected contracts. This work does not expose private cognition or equate commands with physical state. |
| Lab `c688abb60308eba4fb9ac2301599efa67a9b0200` | Reusable renderer `ABSENT` in current source tree | [`observation_consumer.py`](https://github.com/biopeia/lab/blob/c688abb60308eba4fb9ac2301599efa67a9b0200/src/lab/observation_consumer.py) and current `src/` inventory | Lab has a passive Observation consumer and separate experiment/evidence responsibilities. The current source inventory contains no renderer/viewer implementation to reuse; historical physics3d migration/disposition tests are not a renderer or authority transfer. |
| Docs `4988eee30b2ee2cd152066e138fb5fd1e325359e` | UX/design references `EXISTING`; spatial roadmap is a proposal | [Accepted Frontend UX design](https://github.com/biopeia/docs/blob/4988eee30b2ee2cd152066e138fb5fd1e325359e/technical/design/frontend/biopeia-frontend-ux-spec-v1.md), this design, `registry/designs.yaml` | Docs #164 supplies accepted screen truthfulness/fallback requirements; this spatial roadmap remains a proposed readiness design. Neither creates an owner publication contract. |
| Workspace `6e8d83cf353d2bef7addcdb293508784c0bede6c` | Local `make run` / `make view` orchestration `EXISTING`; spatial renderer acceptance `ABSENT` | [`Makefile`](https://github.com/biopeia/workspace/blob/6e8d83cf353d2bef7addcdb293508784c0bede6c/Makefile), `tools/m1_operator.py` | Workspace composes local World and Frontend processes but owns neither domain semantics nor spatial rendering. The previously reported `world-m1` import failure must be tested in the operator path; a `world-m1 --help` check alone is not integrated runtime acceptance. |

This is a source capability audit, not a new owner decision. It makes no new
claim about repository-wide test status; passing tests would not establish
publication permission or real-browser spatial rendering. The independent
clean-current-main production/browser run recorded in [World #156's evidence
log](https://github.com/biopeia/world/issues/156#issuecomment-6195150220)
showed 1,224 valid physical commits within unchanged morphology bounds, then
stopped because Organism produced no motor command. The Owner's [bounded
acceptance](https://github.com/biopeia/world/issues/156#issuecomment-6195474291)
accepts grid-v2 for physical candidate safety only; it assigns no semantics to
that terminal event and does not establish continuous operation.

**Phase 0 conclusion:** the first identified implementation gaps are owner-
authorized Embodiment geometry/per-link state and Environment geometry
publication, an Observation carriage decision for exact bounded families, and
a World-backed cross-owner compatibility/cut relation if a joined scene is to
be labeled coherent. These are `REQUIRES APPROVAL`, not yet approved contracts.
Frontend implementation of a 3D renderer remains deferred until those gates
are resolved; static isolated claims must not be visually assembled as one
scene without explicit identity, revision, frame and cut compatibility.

The actual M1.1 browser reproduction is recorded in [Workspace #50 comment
6187298340](https://github.com/biopeia/workspace/issues/50#issuecomment-6187298340):
World committed 271 continuous ticks; the browser observed real changing
BodyPose/finite-scalar publications and displayed “No authorized scene
geometry.” This is bounded M1 evidence, not 3D-rendering or humanoid evidence.

## Proposal: readiness requirements, not a contract

### 1. Keep static description distinct from dynamic state

For future owner review, consider two separately versioned publication
classes:

1. **Spatial description** — stable owner-identified geometry/primitive or
   approved asset references; morphology/topology where owned; object/link
   identity; local frames and transforms; units/scale; descriptor revision;
   permitted rendering representation and resource bounds.
2. **Dynamic state** — owner-authored pose/joint/resource/environment state at
   an explicitly identified source revision and domain time. Where a causal
   relation is claimed, World must supply a verifiable committed-cut
   relationship; presentation must not infer one from arrival order.

This split is a design question, not a mandate. Each owner may propose a
different decomposition if it preserves their authority and permits a
reviewable compatibility relation. The design does not select data formats,
compression, cache policy, URL model, asset hosting, delivery cadence, or
transport.

### 2. Require explicit compatibility before scene assembly

A future renderer may assemble an object only when owner-approved data
explicitly establishes all required links:

- source owner and stable scoped subject/object identity;
- descriptor, morphology or environment revision compatible with the dynamic
  state;
- declared frame identities, transform path, handedness, units and scale;
- exact selected World committed cut and the owner state/projection's relation
  to that cut, if the view labels it committed or coherent;
- source availability/completeness and asset resolution status;
- provenance and source reference retained through a scene-object inspector.

No heuristic matching by labels, array position, proximity, similar IDs,
arrival time or renderer object key is permitted. If one relation is missing,
contradictory or incompatible, omit the affected rendering and identify the
missing/unsupported relation in the accessible table and inspector.

This is a cross-contract readiness test, not a second screen specification.
The accepted #164 S03 requirements govern detailed renderer interaction,
visual status, semantic fallback, provenance inspection and accessibility.

### 3. Separate decision owners

| Decision | Decision owner | Required review question |
|---|---|---|
| Body geometry representation, morphology revision, link/joint frames and dynamic kinematics | Embodiment owner | Which body facts are authorized for external projection, at what scope, and how does state bind to the active morphology? |
| Environmental/scene geometry, static/dynamic resources, frames and assets | Environment owner | Which environment facts are renderable, how are immutable descriptors revised, and what remains private or non-spatial? |
| Cross-owner causal cut references and committed status | World owner | What proof is sufficient to relate every displayed owner projection to one exact committed cut? |
| Claim carriage, consumer access, availability, size/rate limits and compatibility | Observation owner, with source owners | Can the accepted passive channel carry the approved family revisions without interpreting them? |
| Renderer validation, safe asset resolution, non-3D equivalence and provenance UX | Frontend owner, after readiness gates | Can the application render only compatible authorized inputs and preserve the epistemic metadata? |
| Cross-domain architecture and readiness reconciliation | Architecture Owner | Are owner proposals compatible with accepted ADRs and does the implementation-start gate pass? |

Docs #167 remains the separate security/deployment design gate. The
Observation consumer-contract inventory remains tracked by [Observation
#37](https://github.com/biopeia/observation/issues/37). This Issue does not
replace or close either dependency.

## Cross-contract readiness examples

The following examples make the proposed owner-data prerequisites concrete;
they do not replace or amend the #164 S03 render rules, UI states, fallback or
acceptance criteria.

| Available evidence | Permitted Frontend behavior | Prohibited inference |
|---|---|---|
| BodyPose only | Show the source claim in a semantic table; label its frame and source metadata | Invent a body mesh, anatomy, joint pose or animation |
| Geometry descriptor only | Inspect authorized descriptor metadata if a consumer contract permits it | Show current position or imply dynamic state |
| Geometry plus pose, but no approved identity/revision/frame compatibility | Display separate source claims with an explicit compatibility gap | Attach geometry to a body based on names, order or proximity |
| Compatible static descriptor and dynamic owner state, but no verified World cut | Render only as owner projections with separate source-time/status; do not call the composite committed/coherent | Treat matching timestamps or arrival order as a causal commit |
| Compatible static and dynamic publications explicitly related to a verified committed cut | Render that selected cut with per-source provenance and completeness; preserve text-equivalent access | Interpolate by default, imply continuity between cuts, or turn omitted objects into absence |
| Missing, inaccessible, oversized, unsupported, stale or conflicting asset/state | Omit affected geometry; report the precise condition and retain accessible published metadata where available | Substitute stock geometry, fetch arbitrary URLs, or silently drop provenance |

Interpolation, if ever considered, needs a separate owner decision and
explicit presentation-only labeling of its endpoints and operation. It is
outside this design's proposed first spatial milestone.

## Phased roadmap and gates

| Phase | Work | Entry evidence | Exit evidence |
|---|---|---|---|
| 0. Contract inventory | Recheck exact owner source revisions and map current geometry, pose, frames, identities, dynamic state, Observation families and World-cut references | Docs #164 accepted; bounded M1 publication evidence | Current-source matrix; explicit gaps; no inferred UI contract |
| 1. Owner proposals | Embodiment and Environment independently propose or reject their static/dynamic representations; World specifies/rejects cut relationship; Observation specifies carriage/access feasibility | Phase 0 evidence and owner Issues scoped in their repositories | Each affected owner records an explicit decision; rejected/unsupported data removed from roadmap |
| 2. Cross-domain design review | Reconcile representation compatibility, frames, revisions, partial states, assets/resources, security, provenance and failure behavior | Owner decisions/proposals; Docs #167 and Observation #37 findings | Approved architecture/contract decisions, exact dependencies and implementation-start gate; unresolved authority is a blocker |
| 3. Minimal authorized renderer | Implement only one source-backed fixture slice using accepted contracts; geometry transfer static/revisioned and dynamic claims reference exact revisions/cut when required | Separate explicit Owner start instruction plus all applicable readiness gates | Tests prove valid render, mismatched revision/frame rejection, missing-asset behavior, provenance round-trip and accessible non-3D equivalent |
| 4. Real-browser acceptance | Run a continuous World and browser over owner-approved live publications | Phase 3 implementation and exact release candidates | Browser shows real source-driven changes; cut/availability/disconnect semantics truthful; no unsupported geometry; complete reproducible evidence and independent review |
| 5. Broader scene capability | Add further geometry families, resource types or multiple bodies only through owner-scoped proposals | Prior phase accepted and new capability owners identified | Each added family independently reviewed and covered by compatibility, security, performance and fallback evidence |

Phase 4 must not claim persistent history: durable Observation history, query,
missed-cut reconstruction and longitudinal continuity belong to M2. Current
World journal/checkpoints do not substitute for an Observation archive.

## Acceptance criteria for this design

- The current supported browser evidence and its limits are revision-pinned.
- Domain authority, passive Observation, World causal ownership and Frontend
  presentation boundaries are explicit.
- Static descriptors are separated from dynamic state as a proposal, with
  compatibility/cut requirements and open owner decisions visible.
- The render/no-render matrix prevents guessing and specifies accessible
  fallback behavior.
- The roadmap has falsifiable gates, repository dependencies and an explicit
  prohibition on starting implementation without applicable contract
  decisions and a separate Owner start instruction.
- The proposed design has independent review; any unresolved material finding
  remains a blocker rather than being silently accepted.

## Risks and unresolved decisions

- **Representation risk:** physics geometry and render geometry may not have
  the same purpose or appropriate disclosure. Each owner decides what, if
  anything, may be published for visualization.
- **Coherence risk:** independent owner states can be individually valid yet
  not belong to one World cut. World alone determines causal commitment;
  Frontend cannot repair missing membership.
- **Resource/security risk:** arbitrary meshes and remote asset references
  create parsing, memory, decompression, path, and request risks. Any asset
  mechanism requires the separate security/deployment review and bounded
  owner-approved resolution.
- **Temporal risk:** display interpolation can imply motion or continuity that
  the publication path does not establish. It is excluded unless separately
  authorized and labeled.
- **Availability risk:** missing delivery does not imply source absence;
  unavailable and unsupported data must remain distinct when the source
  contract permits that distinction.

The design deliberately leaves unresolved whether owners will publish
geometry, which assets/primitive families are appropriate, how static data is
referenced/cached, whether dynamic joint state is suitable for external
presentation, and which consumer access contract will be approved. No owner
decision is inferred from a merge, CI, existing fixture, or this proposal.

## Related records

- [Docs #164 — accepted human-facing visualization design](https://github.com/biopeia/docs/issues/164)
- [Docs #167 — frontend read-access security and deployment boundary](https://github.com/biopeia/docs/issues/167)
- [Observation #37 — consumer contract inventory](https://github.com/biopeia/observation/issues/37)
- [Workspace #50 — M1.1 operational/browser evidence and M1.1/M2 boundary](https://github.com/biopeia/workspace/issues/50)
- [ADR-0075 — authority follows semantic ownership](../../adr/ADR-0075-authority-boundaries-derive-from-semantic-ownership-not-repository-topology.md)
- [ADR-0078 — Observation is causally passive](../../adr/ADR-0078-observation-is-causally-passive.md)

## Current-source revalidation (2026-10-15)

This section supplements, rather than overwrites, the older pinned snapshot
above. It records a read-only reinspection against the following local remote
tracking refs. It does not change this document's `proposed` status, approve a
contract, or authorize implementation. The Lab primary checkout was six
commits behind its recorded `origin/main`; only files read explicitly with
`git show origin/main:<path>` count as current Lab evidence in this audit.

| Repository | Revalidated revision | Source evidence inspected | Current finding and limit |
|---|---|---|---|
| Embodiment | `d73315d87bbb3f2eea14e8c33812b37b59a5d72f` | `physics3d/articulated_spec.py`, `articulated_state.py`, `physical_projection.py`, `observation_contract.py`; tests `test_articulated_spec.py`, `test_articulated_state.py`, `test_physical_projection.py`, `test_body_pose_observation_projection.py`, `test_physics3d_observation_contract.py` | Owner-bound morphology contains segments, dimensions/materials, joint topology, frames and stable morphology content identity. Owner state validates root pose and joint values. The BodyPose projection is root pose only; no browser-facing segment-geometry or per-link world-transform publication contract was identified. The listed tests were inspected as existing test locations, not run as part of this revalidation. |
| Environment | `d09e45c40633c9b2bf927c7aec3f6326318c2ea8` | `static_scene.py`, `physical.py`, `procedural_genesis.py`, `identified_resource.py`; tests `test_static_scene.py`, `test_physical_projection.py`, `test_environment_physical_projection.py` | Environment owns explicit static scene/frame/primitive and resource geometry values; the procedural sphere layout is narrow and deterministic. These values and solver/checkpoint uses do not by themselves establish an external visual publication contract, general scene/asset format or correlation with Embodiment. Tests were not run in this revalidation. |
| World | `a7c8099cf6ede9cfdb8f6cf7eaefb2eab8dc9bad` | `observation_publication.py`, `durable_runtime.py`; tests `test_observation_publication.py`, `test_world_post_commit_owner_publication.py` | World verifies that each published owner observation references a checkpoint in a World-verified committed cut, has matching source lineage and names the same World and causal tick. This generic gate does not create geometry, assert scene completeness, interpret owner values, or make an arbitrary UI join acceptable. Tests were not run in this revalidation. |
| Observation | `a8b43af65b79ca4e2455bfc1ff1b55faf3d4d353` | `README.md`, `http_bridge.py`, `semantic.py`; tests `test_http_bridge.py`, `test_plane.py`, `test_observational_boundary_adversarial.py` | The documented browser bridge remains bounded to BodyPose v1 and finite scalar-field current projections. The in-memory plane's global delivery sequence is not domain/causal time and it is not durable history. No general geometry publication family or durable scene query was found. Tests were not run in this revalidation. |
| Frontend | `326613b74e388d3108cbafd3bab9128a35bd2246` | `README.md`, `package.json`, `src/model.js`, `src/views.js`, `src/observation-client.js`; tests include `model.test.js`, `observation-client.test.js`, `observation-store.test.js` | The supported model remains the two bounded M1 claims; README explicitly denies inference of scene geometry, shared World snapshot, causal relation and organism activity. `package.json` has no 3D renderer dependency. No authorized geometry data is currently available to render; absence in the current client is not proof that a domain source cannot provide it. Tests were not run in this revalidation. |
| Modality | `62af4aba07146d5dfdc978af07bb72111112d873` | `README.md` and `src/` search for geometry/spatial claims | Modality describes narrow, non-authoritative scalar transduction and does not own body/environment geometry. No spatial output contract was identified; this does not imply Modality is absent from all future sensory presentation. |
| Organism | `d8ed534d48188fb2f629faaa8dd85b95063a0c2d` | `README.md` and source search for geometry/spatial publication | Organism owns longitudinal identity/private state and lifecycle, not physical body state. No spatial geometry publication was identified. This design excludes private cognition and does not infer organism activity from geometry. |
| Lab | `90d0229655771d134236c0f2e59cb893c0dbe7c6` (`origin/main`; local `HEAD` behind) | Current remote `README.md`; remote inspection confirmed the historical `src/lab/physics3d/engine.py` path is not present in current TARGET main. Lab #63 is a Workbench consumer integration. | No current TARGET physics renderer was established as reusable. Lab #63 does not make Lab the Frontend owner or authorize use of historical engine code. |
| Docs / Workspace | Docs `eb93c8d75bf5e3778081b63f723d61363473f875`; Workspace working tree clean | Docs #176 registry entry and design; Docs #164 accepted UX design; Workspace #50 / Project history | Docs #176 remains `document_status: proposed`, `implementation_status: not_evaluated`, `architecture_scope: UNRESOLVED`. Docs #164 governs UX/fallback. Workspace M1.1 browser evidence is not a spatial contract. |

The audit found existing owner geometry sources and a generic World committed-
cut publication gate, but no complete path that publishes compatible
Embodiment geometry, Environment geometry and required dynamic state through
an approved browser-readable Observation contract. A displayable scene cannot
be reconstructed safely from BodyPose plus a scalar field. This is a finding
about the inspected source path, not a claim that the source domains lack all
physical geometry.

### Issue and dependency disposition

- [Frontend #22](https://github.com/biopeia/frontend/issues/22) is the P0
  coordinator for revalidation and staged delivery. It operationalizes this
  design; it is not a competing design record.
- [Embodiment #77](https://github.com/biopeia/embodiment/issues/77) asks the
  owner to distinguish publishable articulated geometry/state from internal
  solver/morphology data. It is research/design only.
- [Environment #73](https://github.com/biopeia/environment/issues/73) asks the
  owner to disposition existing static/resource geometry for external visual
  use. It is research/design only and does not duplicate the completed
  genesis/checkpoint/solver-input work.
- [Observation #37](https://github.com/biopeia/observation/issues/37) remains
  the open consumer-read boundary inventory; no replacement issue was opened.
- [Docs #167](https://github.com/biopeia/docs/issues/167) remains the open
  security/deployment design gate; no deployment was attempted.
- [Frontend #4](https://github.com/biopeia/frontend/issues/4) remains design-
  only browser-adapter readiness, explicitly dependent on Observation #37 and
  Docs #167.
- World already has generic committed-cut membership/provenance verification
  in the inspected source. No World child issue was opened: revisit only if
  the Embodiment/Environment proposals show that their future owner claims
  cannot be related to an exact committed cut by the current World contract.
- Modality and Organism currently have no demonstrated spatial publication
  role. Lab #63 is a separate Workbench consumer; historical Lab physics code
  is not a current TARGET renderer. Neither is a justified spatial child task
  on the current evidence.

The child Issues request owner dispositions; they do not approve a new
publication family, identity link, transport, inter-owner synchronization,
asset delivery, or exposure of protected state. Docs #176's proposed readiness
gates and the applicable security/read-boundary decisions remain controlling.

### Evidence claim ledger for this revalidation

| Claim | Evidence | Type | Limits |
|---|---|---|---|
| Environment source code has bounded static and resource geometry values | Environment `static_scene.py`, `physical.py`, `procedural_genesis.py` at `d09e45c...` | Implemented (source observed) | Not a general visual contract or browser delivery path |
| Embodiment source code has articulated morphology and owner-validated joint/root state | Embodiment `articulated_spec.py`, `articulated_state.py` at `d73315d...` | Implemented (source observed) | No identified UI geometry publication contract; source presence is not authorization |
| Current Frontend documents only two M1 claim families and no inferred scene | Frontend `README.md` and `src/model.js` at `326613b...` | Documented / implemented boundary | No real-browser test was run for a 3D renderer because no geometry contract is currently exposed |
| World has a generic post-commit owner-publication verification path | World `observation_publication.py` at `a7c8099...` | Implemented (source observed) | Does not establish complete scene membership or browser support |
| New domain owner review is needed before proposing owner geometry publication | No external geometry publication family found in inspected Observation adapter; current design #176 leaves owner decisions open | Inference from inspected evidence | Requires Embodiment, Environment, Observation and competent cross-domain Owner disposition; not an approved contract |
