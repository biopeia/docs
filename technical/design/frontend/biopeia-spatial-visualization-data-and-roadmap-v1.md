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
| `embodiment` | `d73315d87bbb3f2eea14e8c33812b37b59a5d72f` | `src/embodiment/physics3d/articulated_spec.py`, `articulated_state.py`, `physical_projection.py`; `src/embodiment/observation.py` | Embodiment has owner-bound articulated morphology, joint topology/state and a BodyPose projection. This does not establish a browser-facing morphology/mesh/joint publication contract. Since the prior inspected revision, only migration metadata and lockfile changed. |
| `environment` | `d09e45c40633c9b2bf927c7aec3f6326318c2ea8` | `src/environment/static_scene.py`, `physical.py`, `identified_resource.py` | Environment has explicit fixture-oriented static scene/frame/primitive values and resource projections. They are not a stable general scene or asset-delivery contract. |
| `world` | `a7c8099cf6ede9cfdb8f6cf7eaefb2eab8dc9bad` | `src/world/causal_cycle.py`, `durable_runtime.py`, `observation_publication.py`, `adapters/articulated_mujoco.py` | World owns causal coordination and committed cuts, and can correlate post-commit projections. The intervening changes add/strengthen grid-v2 physical candidate selection and journal behavior; they do not authorize arbitrary owner geometry or a browser scene contract. |
| `observation` | `a8b43af65b79ca4e2455bfc1ff1b55faf3d4d353` | `src/observation/semantic.py`, `embodiment.py`, `environment.py`, `http_bridge.py` | Current local/browser path is bounded to BodyPose and finite scalar-field projections. The intervening change only updates dependency lock entries. No approved geometry family or durable historical scene query was found. |
| `frontend` | `326613b74e388d3108cbafd3bab9128a35bd2246` | `src/main.js`, `observation-client.js`, `observation-store.js`, `presentation-scheduler.js`, `views.js`; browser acceptance scripts | The browser displays the two supported claims and explicitly reports no authorized scene geometry. Store subscriptions and presentation updates are selective; no renderer is present and claims are not reconstructed into meshes. |
| `docs` | `16d951c` | Accepted Frontend UX/readiness designs | Docs #164 defines spatial rendering truthfulness and screen acceptance; its contract-readiness and implementation gates remain applicable. |

These are code/document inspections at the listed revisions, not owner approval
of a new spatial contract. In particular, the existence of frame descriptors,
joint topology, URDF generation, static primitives, physical-step state or
BodyPose does not establish compatible identity, asset lifetime, display
geometry or cross-owner coherence for a browser scene.

### World #156 disposition update (2026-10-15)

The current-source capability matrix and issue/dependency inventory are
recorded in the preceding **Current-source revalidation** section. This update
adds only the subsequent World #156 owner disposition, rather than duplicating
that matrix. A clean-current-main production/browser run is recorded in [World
#156's evidence log](https://github.com/biopeia/world/issues/156#issuecomment-6195150220):
it reached 1,224 confirmed commits within unchanged Embodiment position and
velocity bounds, then stopped before the next commit because Organism produced
no motor command. The Owner's [bounded engineering acceptance](https://github.com/biopeia/world/issues/156#issuecomment-6195474291)
accepts grid-v2 for physical candidate safety, pre-commit rejection of
infeasible candidates, and preservation of the last valid cut. It makes no
claim of scientific efficacy, general solver validity or indefinite
stability, and assigns no semantics to the later no-command termination.

This update does not resolve the spatial publication gaps identified in the
matrix. Geometry/per-link state, Environment render geometry and Observation
carriage remain separate owner decisions. World already has a generic
committed-cut membership/provenance gate, but neither that mechanism nor the
grid-v2 acceptance authorizes a spatial family or a cross-owner scene claim.

The actual M1.1 browser reproduction is recorded in [Workspace #50 comment
6187298340](https://github.com/biopeia/workspace/issues/50#issuecomment-6187298340):
World committed 271 continuous ticks; the browser observed real changing
BodyPose/finite-scalar publications and displayed “No authorized scene
geometry.” This is bounded M1 evidence, not 3D-rendering or humanoid evidence.

### Frontend current-main presentation evidence (2026-10-15)

At Frontend `326613b74e388d3108cbafd3bab9128a35bd2246`, `npm test` passed
43/43 and `npm run build` succeeded. The tests cover selective store
subscriptions, rejection of obsolete request completions, stale retention on
disconnect, latest-view coalescing, and view rendering without fabricated
geometry or cross-owner joins. The build emits the existing static read-only
shell; no rendering dependency or 3D implementation is present.

The live-browser acceptance harness in
`scripts/acceptance-live-browser.mjs` expects the authorized M1 bridge and
requires two distinct committed World ticks with source-lineage digests; it is
not a spatial renderer acceptance. The available integrated browser evidence
is the bounded M1.1 run linked above: it demonstrated real changing claim data
and separately measured stable shell/focus/scroll behavior, but no authorized
scene geometry. Thus these checks support current passive presentation
readiness only; they do not satisfy Spatial Visualization V1's final browser
criterion.

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

### 3. Renderer technology evaluation (recommendation only)

For the bounded first renderer, prefer Three.js over handwritten WebGL. The
target needs a scene graph for owner-supplied local transforms, primitive
geometry, a separate camera, orbit/zoom/pan controls and selective updates to
existing scene objects. Three.js already provides a WebGL 2 renderer, an
object/transform scene graph and an `OrbitControls` addon. Raw WebGL would avoid
the library dependency, but would require Biopeia to implement and maintain
the scene graph, transform/matrix handling, camera controls, buffer lifecycle
and rendering diagnostics itself. That is more application code without
improving the authority boundary.

The recommendation is deliberately small: evaluate only the `three` package
and its `OrbitControls` addon, hosted by the existing Frontend build. Do not
add React Three Fiber, asset loaders, remote asset URLs, post-processing,
WebGPU, or another rendering service for the first slice. Keep the renderer
isolated behind Spatial Explorer's presentation boundary; create static
geometry once per descriptor revision and update only transforms when
validated source state changes. Render in response to data/control changes
rather than inventing animation or increasing Observation acquisition
frequency. A hidden or unsupported WebGL 2 context must fall back to the
accepted accessible non-3D view.

This is a technology recommendation, not an implementation start decision or
approval of any geometry/state publication contract. The browser must receive
only owner-approved, schema-validated data before this renderer is added.
Three.js documents its [WebGL 2 renderer](https://threejs.org/docs/pages/WebGLRenderer),
[hierarchical scene graph](https://threejs.org/manual/pages/scenegraph.html),
and [OrbitControls camera interaction](https://threejs.org/docs/pages/OrbitControls.html).

### 4. Separate decision owners

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
| Lab | `e6a084f1abae751a8248b373901150754a403bbc` (`origin/main`; local `HEAD` behind) | Current remote `README.md`; remote inspection confirmed the historical `src/lab/physics3d/engine.py` path is not present in current TARGET main. Lab #63 is a Workbench consumer integration. The intervening revision changes migration inventory/tests, not the current renderer inventory. | No current TARGET physics renderer was established as reusable. Lab #63 does not make Lab the Frontend owner or authorize use of historical engine code. |
| Docs / Workspace | Docs `4988eee30b2ee2cd152066e138fb5fd1e325359e`; Workspace working tree clean | Docs #176 registry entry and design; Docs #164 accepted UX design; Workspace #50 / Project history | Docs #176 remains `document_status: proposed`, `implementation_status: not_evaluated`, `architecture_scope: UNRESOLVED`. Docs #164 governs UX/fallback. Workspace M1.1 browser evidence is not a spatial contract. |

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
