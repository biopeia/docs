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
| `observation` | `a8b43af65b79ca4e2455bfc1ff1b55faf3d4d353` | `src/observation/semantic.py`, `embodiment.py`, `environment.py`, `http_bridge.py` | Current local/browser path is bounded to BodyPose and finite scalar-field projections. Neither currently allowlisted M1 family exposes a World commit ID/cut receipt in its consumer payload; the bridge explicitly offers per-message, not cross-owner snapshot, coherence. No approved geometry family or durable historical scene query was found. |
| `frontend` | `326613b74e388d3108cbafd3bab9128a35bd2246` | `src/main.js`, `observation-client.js`, `observation-store.js`, `presentation-scheduler.js`, `views.js`; browser acceptance scripts | The browser displays the two supported claims and explicitly reports no authorized scene geometry. Store subscriptions and presentation updates are selective; no renderer is present and claims are not reconstructed into meshes. |
| `docs` | `16d951c` | Accepted Frontend UX/readiness designs | Docs #164 defines spatial rendering truthfulness and screen acceptance; its contract-readiness and implementation gates remain applicable. |

These are code/document inspections at the listed revisions, not owner approval
of a new spatial contract. In particular, the existence of frame descriptors,
joint topology, URDF generation, static primitives, physical-step state or
BodyPose does not establish compatible identity, asset lifetime, display
geometry or cross-owner coherence for a browser scene.

### Earlier bounded owner candidate-field dispositions (2026-10-15)

The Domain Owner accepted the candidate field subsets recorded in [Embodiment
#77](https://github.com/biopeia/embodiment/issues/77#issuecomment-6197195602),
[Environment #73](https://github.com/biopeia/environment/issues/73#issuecomment-6197196000),
and [Observation #37](https://github.com/biopeia/observation/issues/37#issuecomment-6197196506).
These earlier dispositions bounded candidate fields; they were not completed
wire schemas or permission to add fields outside the candidates:

- Embodiment may author a static render-only segment/joint descriptor and a
  dynamic per-link transform projection, bound to body, episode, morphology,
  geometry revision, named source cut, explicit frames and units. Internal
  checkpoint/URDF, mass, material/contact/receptor/effector and cognitive data
  remain excluded. If Embodiment cannot produce its own transforms, the body
  is omitted rather than derived by Frontend.
- Environment may author a static descriptor limited to the already modeled
  ground-plane/sphere primitives, object/frame identifiers and Environment
  identity/revisions in declared SI units. Solver values, genesis/checkpoint
  data, arbitrary asset references and unmodeled/dynamic objects remain
  excluded.
- Observation may pass separately versioned immutable spatial descriptors
  and dynamic state only after the exact source-owned schemas are established.
  Its existing local-only GET/read limits, response cap, strict validation and
  no-history/no-cache/no-cross-owner-join boundary remain in force.

### Earlier owner direction for design work only (2026-10-15)

The Owner has authorized the next bounded design and contract-definition work,
but has **not** approved implementation, publication, or a completed wire
contract. The direction is recorded in the Owner's disposition on [Frontend
#22](https://github.com/biopeia/frontend/issues/22#issuecomment-6199059732),
with affected-domain records on [Embodiment
#77](https://github.com/biopeia/embodiment/issues/77#issuecomment-6199062525),
[Environment #73](https://github.com/biopeia/environment/issues/73#issuecomment-6199062981),
[World #162](https://github.com/biopeia/world/issues/162#issuecomment-6199063376),
and [Observation
#37](https://github.com/biopeia/observation/issues/37#issuecomment-6199063932).
These dispositions unblock design only; owners still need to review the exact
proposed contract before implementation.

The current design direction is deliberately narrow:

- Environment may define a read-only publication for static, owner-authored
  render geometry, identifiers, units, coordinate frame and revision.
- Embodiment may define distinct static articulated geometry/topology and
  dynamic kinematics publications, with body/episode/morphology identity,
  source revision, units and frames. Frontend must not derive missing physical
  properties.
- Observation may carry approved source-owned claims without changing their
  meaning or correlating them on its own.
- A composite scene may be described as causally coherent only when an
  explicit World-owned and consumer-verifiable relationship identifies the
  same confirmed committed cut and verifies each source-state/revision
  relationship. Equal tick numbers alone are insufficient. The design must
  define verification and behavior for missing, conflicting, or late claims;
  unresolved claims remain separate and cannot be called one coherent scene.

This recorded the earlier proposal direction, not a choice of schema, envelope,
transport, asset model, or implementation. The later design-base dispositions
below supersede its open question about whether this design direction may
advance, but not its restrictions on final schemas, implementation, publication,
UX, security/read access or M2/M3 scope.

No disposition authorizes a new shared cross-owner spatial transform. The
current source audit does, however, identify a narrower M1 configuration: the
articulated MuJoCo adapter rejects inputs unless the Embodiment body's
`reference_frame` equals the Environment scene's `frame.frame_id`; the M1
profile creates that Environment frame using the Embodiment profile's
`frame_id` and declares its parent as `world`, with an identity basis/origin.
This is a profile-configured same-frame-ID compatibility check. The adapter
checks identifier equality only; it does not independently validate axes,
handedness, units, origin, an actual transform, or semantic compatibility.
This is not a consumer-visible spatial publication or a general cross-profile
frame contract.

The distinction matters: the previously accepted candidate field subsets and current generic
post-commit publication join do not carry the M1 profile's frame-ID linkage
and equality-check evidence, static descriptor revision, and dynamic per-link
transforms together to Observation. A renderer must not claim that relation for arbitrary profiles or
independently delivered claims. For the M1 profile, the existing solver gate
may be relevant evidence for a bounded rendering relation after the exact
owner-authored projections and their cut/revision binding are specified and
the frame linkage is preserved or revalidated in the authorized publication
path. World causal co-membership still does not itself establish spatial frame
compatibility.

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

### Explicit no-actuation result: design gate, not an interpretation of `None`

The Owner's decision on [Frontend
#22](https://github.com/biopeia/frontend/issues/22#issuecomment-6199059732)
distinguishes a valid, explicit no-actuation result from a missing, malformed,
incomplete or failed Organism result. World may advance physical evolution
without an actuation request only for the valid explicit outcome. It must not
manufacture a neutral command, replay the prior command or mutate physical
state to simulate rest. An invalid result must fail the transition in a
controlled way and preserve the last confirmed cut. Vital/lifecycle
termination must be explicit from its competent domain and cannot be inferred
from no-actuation.

This is a semantic decision, not evidence that current code already implements
that result contract. At Organism
`d8ed534d48188fb2f629faaa8dd85b95063a0c2d`,
`ExplorationActionCandidate.motor_command` is typed `MotorCommand | None`.
`OrganismExplorationComposer.prepare` initializes its local command to `None`
and sets a command only when the prepared `intents` collection is non-empty.
Thus this path produces an internal candidate with no command when no intent
was prepared, but the candidate carries no separate discriminator declaring
that condition a valid no-actuation result. Errors raised before candidate
creation are separate failure paths; they are not valid abstention. At World
`a7c8099cf6ede9cfdb8f6cf7eaefb2eab8dc9bad`,
`causal_cycle.py` raises when that field is `None`, and the articulated
MuJoCo adapter accepts a required `MotorCommand`. Therefore the current
candidate `None` is not yet a demonstrated valid no-actuation result, and
the current caller treats it as a failed transition. This observation does
not determine the broader contract meaning of every no-command path.

The design-only follow-ups are [Organism
#176](https://github.com/biopeia/organism/issues/176) and [World
#165](https://github.com/biopeia/world/issues/165). They must inspect the exact
result path, validity checks, physical no-actuation integration and cut
preservation. No change to the present `None` treatment or to actuator/
termination semantics is authorized until those designs and owner reviews
establish the required contract. This investigation does not alter World
#156's bounded grid-v2 acceptance.

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

### Current implementation gaps after the owner dispositions

At the exact source snapshot above:

1. Embodiment's `ArticulatedBodySpec` contains candidate segment dimensions,
   origins and joint topology, but its complete checkpoint representation
   also contains fields explicitly excluded from visualization. The proposed
   render subset needs a new owner-authored projection; the checkpoint must
   not be serialized or filtered by Frontend. `ArticulatedEmbodimentPhysicalState`
   contains root pose and joint position/velocity, not per-link transforms.
   Embodiment must author the accepted transform projection; the browser must
   not derive it.
2. Environment's `StaticPhysicalScene` combines renderable plane/sphere
   geometry with gravity, friction and optional genesis provenance. A safe
   descriptor must be separately projected and must omit these excluded
   fields.
3. World verifies generic owner checkpoint lineage, authority, World identity
   and causal tick for post-commit claims. Separately, the articulated
   physical-step adapter checks equality of the body and scene frame IDs only;
   the M1 profile uses the Embodiment profile frame ID for the Environment
   frame ID and sets parent `world` with identity basis/origin. The M1 profile
   configures this same-ID compatibility, but the adapter does not validate
   frame semantics (axes, handedness, units, origin or transform). The profile
   also constructs the physical scene with `objects=()`, so this path supplies
   no renderable Environment primitive geometry. This is not a consumer-visible
   spatial publication. The current production
   publication join contains no spatial descriptor or per-link family and
   does not expose this frame-linkage proof to Observation.
4. Observation's HTTP allowlist currently contains exactly
   `embodiment.body_pose` and `environment.finite_scalar_field`; no accepted
   geometry or per-link family is carried. The candidate carriage approval
   does not change that allowlist until exact schemas/limits are implemented
   and reviewed.

These are source gaps, not requests to enlarge a domain's authority. Static
owner descriptors and dynamic owner state must remain distinct. Any future
renderer must show separate owner claims rather than assemble them into one
scene until the frame relationship and relevant cut binding are proven.

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
| 1. Exact owner schemas | Specify bounded Embodiment and Environment projections and Observation's closed read schemas; keep World verification generic unless evidence shows a missing cut check | Bounded scope decisions in Embodiment #77, Environment #73 and Observation #37; exact current-source revisions above | Exact schemas, exclusions, units, limits and lineage tests recorded in owner repositories; no out-of-scope fields |
| 2. Spatial-frame relationship | Determine whether and how the M1 profile-configured same-frame-ID compatibility can be preserved for a bounded consumer view; do not generalize it to arbitrary profiles. World cut membership alone is insufficient | M1 profile uses the Embodiment profile frame ID for its Environment frame; World adapter checks ID equality only, without validating frame semantics; no spatial family or frame proof in post-commit Observation publication | Owner-reviewed exact frame binding and its propagation/verification for the selected profile, or a documented decision to render separate projections only; no heuristic join |
| 3. Cross-domain design review | Reconcile exact schemas, frame mapping, revisions, partial states, security, provenance and failure behavior | Owner schema proposals, spatial-frame disposition, Docs #167 and Observation #37 gates | Approved architecture/contract decisions, exact dependencies and implementation-start gate; unresolved authority is a blocker |
| 4. Minimal authorized renderer | Implement only one source-backed slice using accepted contracts; geometry transfer static/revisioned and dynamic claims reference exact revisions/cut when required | Exact approved schemas, resolved frame relationship for any combined view, security/readiness gates | Tests prove valid render, mismatched revision/frame rejection, missing-data behavior, provenance round-trip and accessible non-3D equivalent |
| 5. Real-browser acceptance | Run a continuous World and browser over owner-approved live publications | Phase 4 implementation and exact release candidates | Browser shows real source-driven changes; cut/availability/disconnect semantics truthful; no unsupported geometry; reproducible evidence and independent review |
| 6. Broader scene capability | Add further geometry families, resource types or multiple bodies only through owner-scoped proposals | Prior phase accepted and new capability owners identified | Each added family independently reviewed and covered by compatibility, security, performance and fallback evidence |

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

The bounded primitive/per-link candidate scopes and Observation carriage
approach are authorized for design and owner review, not accepted wire
contracts. Exact schemas, consumer-visible propagation and validation of the
M1 solver's existing frame relation, static-data refresh/lifetime, and the cut
relationship for dynamic state remain unresolved. The design direction does
not authorize arbitrary assets or broader geometry families. No decision is
inferred from a merge, CI, existing fixture, or this proposal.

## Related records

- [Docs #164 — accepted human-facing visualization design](https://github.com/biopeia/docs/issues/164)
- [Docs #167 — frontend read-access security and deployment boundary](https://github.com/biopeia/docs/issues/167)
- [Observation #37 — consumer contract inventory](https://github.com/biopeia/observation/issues/37)
- [World #162 — consumer-visible committed-cut association decision](https://github.com/biopeia/world/issues/162)
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
| World | `a7c8099cf6ede9cfdb8f6cf7eaefb2eab8dc9bad` | `observation_publication.py`, `durable_runtime.py`, `adapters/articulated_mujoco.py`, `m1_profile.py`, M1 profile JSON; tests `test_observation_publication.py`, `test_world_post_commit_owner_publication.py`, `test_articulated_production_join.py`; [World #162](https://github.com/biopeia/world/issues/162) | World validates owner publications against an internal `CommittedWorldCut` (world identity, causal tick, commit ID and owner checkpoint references). That server-side validation does not itself expose a consumer-verifiable receipt in the current M1 Observation payloads. Separately, the M1 profile uses the Embodiment profile frame ID for the Environment scene frame (parent `world`, identity basis/origin); the adapter checks ID equality only, not frame semantics, and `m1_profile.py` constructs the scene with `objects=()`. World #162 asks its owner to decide the sufficient consumer-visible cut-association contract; no sufficiency rule is assumed here. Tests were inspected, not run in this revalidation. |
| Observation | `a8b43af65b79ca4e2455bfc1ff1b55faf3d4d353` | `README.md`, `http_bridge.py`, `semantic.py`; tests `test_http_bridge.py`, `test_plane.py`, `test_observational_boundary_adversarial.py` | The documented browser bridge remains bounded to BodyPose v1 and finite scalar-field current projections. The in-memory plane's global delivery sequence is not domain/causal time and it is not durable history. No general geometry publication family or durable scene query was found. Tests were not run in this revalidation. |
| Frontend | `3b158cc73e57a8175265e1d25a66eb09346679f9` | `README.md`, `package.json`, `src/model.js`, `src/views.js`, `src/observation-client.js`, `src/style.css`; [PR #24](https://github.com/biopeia/frontend/pull/24) adds `tests/views.test.js` coverage | Frontend still consumes the same two bounded M1 claim families and has no 3D renderer dependency. PR #24 adds separate SVG coordinate markers for supported finite coordinates, with independent display scaling, owner identity, frame and provenance labels; it expressly does not compose claims into a scene. This is coordinate evidence presentation, not authorized physical geometry or a coherent shared World snapshot. Current-source tests/build were not rerun in this documentation revalidation. |
| Modality | `62af4aba07146d5dfdc978af07bb72111112d873` | `README.md` and `src/` search for geometry/spatial claims | Modality describes narrow, non-authoritative scalar transduction and does not own body/environment geometry. No spatial output contract was identified; this does not imply Modality is absent from all future sensory presentation. |
| Organism | `d8ed534d48188fb2f629faaa8dd85b95063a0c2d` | `README.md` and source search for geometry/spatial publication | Organism owns longitudinal identity/private state and lifecycle, not physical body state. No spatial geometry publication was identified. This design excludes private cognition and does not infer organism activity from geometry. |
| Lab | `e6a084f1abae751a8248b373901150754a403bbc` (`origin/main`; local `HEAD` behind) | Current remote `README.md`; remote inspection confirmed the historical `src/lab/physics3d/engine.py` path is not present in current TARGET main. Lab #63 is a Workbench consumer integration. The intervening revision changes migration inventory/tests, not the current renderer inventory. | No current TARGET physics renderer was established as reusable. Lab #63 does not make Lab the Frontend owner or authorize use of historical engine code. |
| Docs / Workspace | Docs `eec6ed35af985b5a7935cded2049201b22dfe612`; Workspace `6e8d83cf353d2bef7addcdb293508784c0bede6c` | Docs #176 registry entry and design; Docs #164 accepted UX design; Workspace #50 / Project history | Docs #176 remains `document_status: proposed`, `implementation_status: not_evaluated`, `architecture_scope: UNRESOLVED`. Docs #164 governs UX/fallback. Workspace M1.1 browser evidence is not a spatial contract. |

### Capability status matrix

Status is per capability, not per repository. `EXISTING` means an owner-side
capability is present in the cited source; it does not imply external
publication. `PARTIAL` means only a bounded part of the requested path exists.
`ABSENT` means the inspected current source did not establish the capability.
`REQUIRES APPROVAL` identifies a new boundary or authority decision, not a
work item that may be implemented by inference. The source snapshot above is
source-inspection evidence only; tests listed above were not run in this
revalidation.

| Capability | Status | Owner | Source / evidence | Tests | Limitation and linked decision |
|---|---|---|---|---|---|
| Internal articulated morphology and validated joint state | `EXISTING` | Embodiment | `d73315d…`; `physics3d/articulated_spec.py`, `articulated_state.py` | Source and test locations inspected; not run | Internal owner representation only. Embodiment #77 accepts design direction; exact geometry conventions, digest and transform production remain to be settled. |
| Root body pose projection | `PARTIAL` | Embodiment | `d73315d…`; `physical_projection.py`, `observation_contract.py` | Projection tests inspected; not run | Root pose is not per-segment geometry or link transforms. No second kinematics engine is authorized. |
| Browser-readable articulated geometry and segment transforms | `ABSENT` | Embodiment | Same source snapshot; no external geometry family identified | No conformance test exists in the inspected current source | Publication requires exact owner-approved contract. See Embodiment #77. |
| Internal Environment scene/resource geometry | `EXISTING` | Environment | `d09e45c…`; `static_scene.py`, `physical.py`, `identified_resource.py` | Source and test locations inspected; not run | Existing owner geometry is not a visual publication contract. Environment #73 accepts design direction; primitive/frame scope and review remain open. |
| Renderable active M1 Environment scene | `ABSENT` | Environment | `d09e45c…`; M1 profile has `objects=()` | Profile/source inspected; no rendered-scene test | Do not invent a floor, objects, terrain or resources. Environment #73. |
| Confirmed World cut and owner-checkpoint validation | `EXISTING` | World | `a7c8099…`; `observation_publication.py`, `durable_runtime.py` | Test locations inspected; not run | Internal validation exists; browser-verifiable proof is not present in current M1 claims. World #162. |
| Consumer-verifiable proof that dynamic projections share one confirmed cut | `ABSENT` | World | Same snapshot; current claims lack exposed commit identity/proof | No consumer conformance test identified | Equal tick/frame labels alone are insufficient. Candidate should reuse existing commit/checkpoint evidence; no new history store. World #162 accepts direction only. |
| Current bounded Observation reads for BodyPose and finite scalar field | `PARTIAL` | Observation | `a8b43af…`; `README.md`, `http_bridge.py`, `semantic.py` | Bridge/boundary test locations inspected; not run | Existing current-view transport, not spatial geometry, durable history or shared-cut composition. Observation #37. |
| Passive transport of approved spatial descriptions with provenance | `REQUIRES APPROVAL` | Observation plus publishing owners | `a8b43af…`; current allowlist/read boundary | No spatial-family conformance test identified | Exact family, bounds and provenance must be approved; no semantic joins. Observation #37. |
| Independent 2D markers for supported M1 coordinate claims | `PARTIAL` | Frontend | `3b158cc…`; `src/views.js`, `src/style.css` | PR #24 added view tests; not rerun in this audit | Presentation markers are not a physical scene and do not establish shared coordinates. |
| Authorized spatial 3D renderer for real owner geometry | `ABSENT` | Frontend | `3b158cc…`; `package.json`, `src/` inspection | No real-browser 3D acceptance evidence | Renderer stays blocked until owner contracts, read boundary and cut proof are approved. Frontend #22. |
| Spatial geometry publication role | `ABSENT` | Modality | `62af4ab…`; README/source search | No relevant contract test identified | No spatial authority inferred for Modality. |
| Spatial geometry publication role | `ABSENT` | Organism | `d8ed534…`; README/source search | No relevant contract test identified | Organism identity/private state and lifecycle remain outside physical geometry. |
| Reusable current-target Lab renderer | `ABSENT` | Lab | `e6a084f…` (`origin/main`); current README/path check | No current-target renderer test established | Historical engine path is not present in current target main; Lab #63 is a separate consumer. |
| Canonical design/readiness record | `EXISTING` | Docs | `0373d063…`; Docs #176 registry, Docs #164 UX | Registry validation is tracked separately from this source inspection | Keep `proposed / not_evaluated / UNRESOLVED`; design-base acceptance does not change registry readiness. |
| Workspace runtime/browser coordination evidence | `EXISTING` | Workspace | `4e34c97…`; Workspace #50 and M1.1 artifacts | Evidence is bounded to recorded M1.1 checks | Operational evidence is not a geometry/cut contract and does not establish Spatial V1 acceptance. |

The matrix records capability, not readiness or acceptance. In particular,
`REQUIRES APPROVAL` must not be read as implementation authorization, while
`EXISTING` owner-side geometry must not be synthesized into a browser scene
without an approved publication and verified cut relationship.

The audit found existing owner geometry sources and an M1 profile-configured
same-frame-ID compatibility check, but no complete path that publishes compatible
Embodiment geometry, Environment geometry and required dynamic state through
an approved browser-readable Observation contract. The World gate applies to
the physical solver inputs; the current generic post-commit publication path
does not carry a spatial family or expose that frame-linkage proof. A
displayable scene cannot be reconstructed safely from BodyPose plus a scalar
field. This is a finding about the inspected source path, not a claim that the
source domains lack all physical geometry.

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
- World #162 records the newly verified consumer-visible cut-association gap.
  World validates each owner publication against a `CommittedWorldCut`, but
  the current M1 allowlisted claims do not expose that commit identity to the
  browser, and Observation promises no cross-owner snapshot. #162 is a
  design/disposition gate, not authorization to change World or Observation
  contracts. It is distinct from World #103's generic post-commit publication
  join and #144's local bridge integration test.
- Modality and Organism currently have no demonstrated spatial publication
  role. Lab #63 is a separate Workbench consumer; historical Lab physics code
  is not a current TARGET renderer. Neither is a justified spatial child task
  on the current evidence.

The child Issues have recorded design-base Owner dispositions, now linked in
the candidate-conformance section below. Those dispositions do not approve a
new publication family, identity link, transport, inter-owner synchronization,
asset delivery, or exposure of protected state. Exact schemas and publication
remain subject to owner review; Docs #176 readiness gates and applicable
security/read-boundary decisions remain controlling. World #162's disposition
accepts the direction of a consumer-verifiable shared-cut proof but not its
exact verification mechanism or implementation.

### Frontend coordinate-marker delta (2026-10-15)

Frontend PR #24 merged as `3b158cc73e57a8175265e1d25a66eb09346679f9` and
changes only `src/views.js`, `src/style.css` and `tests/views.test.js`. The
Spatial route now renders one independent two-dimensional SVG coordinate
marker per supported M1 claim when that claim has a finite coordinate triplet
and a nonempty frame label. Each marker is centered and scaled independently
for presentation; it retains owner claim identity, context time, source
lineage, frame and stale labeling. The view continues to say that the markers
are not a physical scene and does not join the Environment and Embodiment
claims. This merged code and its tests establish an implemented presentation
change, not an independently verified real-browser rendering result.

Accordingly, the prior current-source finding remains: the browser has no
authorized Environment/Embodiment scene geometry, no articulated link
transforms, no approved consumer-visible common-cut proof and no 3D renderer.
The coordinate markers do not satisfy Spatial Visualization V1 and are not
evidence of a shared physical coordinate system.

### Owner dispositions and candidate conformance sketches (2026-10-15)

The Owner accepted the architectural direction in Embodiment #77, Environment
#73, World #162 and Observation #37 as design base. The recorded dispositions
are [Embodiment #77](https://github.com/biopeia/embodiment/issues/77#issuecomment-6200248780),
[Environment #73](https://github.com/biopeia/environment/issues/73#issuecomment-6200249144),
[World #162](https://github.com/biopeia/world/issues/162#issuecomment-6200249455),
and [Observation #37](https://github.com/biopeia/observation/issues/37#issuecomment-6200249767).
This acceptance permits preparation and review of candidate schemas and
conformance vectors. It is not approval of exact fields, wire formats,
implementation, publication, or the Frontend renderer. The following are
illustrative review material, not normative contracts. Existing security/read
limits and owner authority remain in force.

The candidate-gap review used these local `main` revisions as its source
snapshot (not as runtime pins): Workspace
`4e34c97569aaa1ba5611eda3dab3923cd33dfd83`, Docs
`0373d063ada83b08fc4343f6a8c6dc382a155283`, Frontend
`3b158cc73e57a8175265e1d25a66eb09346679f9`, World
`51cea9f8975fbdea603592fa5e9c56b073a2f4d4`, Observation
`a8b43af65b79ca4e2455bfc1ff1b55faf3d4d353`, Embodiment
`d73315d87bbb3f2eea14e8c33812b37b59a5d72f`, and Environment
`d09e45c40633c9b2bf927c7aec3f6326318c2ea8`. This is a documented
source-inspection snapshot; no new integrated runtime or browser execution was
performed for these candidate sketches.

#### Candidate separation of static description, dynamic state and cut proof

The candidate model has four separately owned parts. Names and encodings below
are provisional; each owner must settle its own exact schema.

| Candidate part | Owner | Minimum review content | Explicit non-goal |
|---|---|---|---|
| Static environment description | Environment | Environment identity/revision; declared frame and units; only source-supported primitive variants; an empty collection is valid | No generated floor, props, terrain or objects. The inspected M1 profile has `objects=()` |
| Static articulated description | Embodiment | Morphology/body identity and revision; stable segment IDs; parent/attachment topology; explicitly defined visual primitive and local visual origin; digest over precisely the render-description fields | Do not reuse a broader physical morphology digest without proving that its inputs and stability semantics match this purpose |
| Dynamic articulated state | Embodiment | Complete owner-produced pose set keyed by the static segment IDs; explicit reference frame, units, time/cut reference and finite translation/rotation representation | No Frontend forward kinematics and no second kinematics engine. The owner must identify and validate the producer from authorized state |
| Cut-association evidence | World | Existing exact committed-cut identity and a verifiable association for dynamic owner state; whether a versioned static descriptor is pinned as a valid input at that cut rather than republished per cut remains an explicit design question | Do not assume a separate session ID exists. No equal-tick-only join, new persistence/history, or claim that evidence attests to semantic correctness or frame compatibility |

An illustrative Environment value may contain `items: []`; that means no
Environment primitives were published, not an empty plane or a default floor.
If a ground plane is explicitly published, its normal, offset, frame, unit and
orientation convention must be fully specified. The inspected source expresses
the plane using `normal · position_m = offset_m`; the candidate contract must
retain or deliberately replace that exact convention through Environment
review. Sphere or box support must likewise be limited to forms actually
owned and produced by Environment or Embodiment. Do not infer support for
meshes, textures, materials, lights or arbitrary assets.

Embodiment must settle whether a visual primitive is body-local, segment-local
or attached through another explicit frame, and define handedness, axis
convention, quaternion component order, normalization tolerance and digest
canonicalization. Any dynamic pose list must be complete and unambiguous for
the referenced static description. Existing root pose and joint scalars do
not, on their own, prove that per-link browser poses are currently published.
The owner must identify a source that already calculates the authorized
transforms at the same physical state; duplicating kinematics in Frontend is
out of scope.

World's candidate proof must bind dynamic publication references to the *same
exact confirmed cut*, rather than infer association from equal `causal_tick`.
It should reuse existing cut/commit identity and evidence, not introduce a new
session identifier unless one is already part of an approved source contract.
Static geometry/morphology may be immutable or versioned across multiple cuts;
the competent owners and World must decide how the selected revision is pinned
and shown to be valid for the cut without requiring per-tick republishing.
Whether an opaque reference, publication/checkpoint identity, schema revision
or digest is exposed to a consumer is unresolved and requires owner and
security/read-boundary review. Internal filesystem locators must not be
exposed. The design still needs to identify who authenticates World-issued
evidence, how a consumer distinguishes confirmed from uncertain state, and how
restore/fork/recovery affect the binding. A digest alone must not be treated as
proof of authenticity. Any eventual proof establishes only the exact membership
it specifies; it does not prove geometry validity, coordinate compatibility,
scene completeness, or scientific meaning.

Observation's candidate role is bounded transport of separately identified,
owner-approved publications with their original provenance and World evidence
unchanged. The response remains subject to the existing configured size and
read boundary. The current total response cap is not a per-family budget; the
owners must derive safe per-message/count limits and demonstrate the combined
response bound. Observation must not create a cross-owner semantic join, turn
delivery order into causal order, repair missing data, or call the result a
coherent scene. Frontend may assemble a joint visual presentation only after
the approved evidence and exact frame-compatibility rules permit it.

#### Candidate positive and negative conformance vectors

These vectors are proposed test cases, not tests already implemented or
executed. Owners should turn the applicable cases into executable tests in
their repositories before exact contract approval.

| Case | Candidate expectation | Responsible review |
|---|---|---|
| Environment explicitly publishes no primitives (`items: []`) | Valid empty publication; renderer shows no invented geometry | Environment, Frontend |
| A supported, finite primitive has unique identity, declared dimensions, frame and unit | Accept only if that primitive and convention are included in the final Environment contract | Environment |
| Unknown primitive kind, duplicate identity, non-finite coordinate, non-positive size, malformed frame, undeclared unit or digest mismatch | Reject; do not silently substitute geometry or defaults | Owning geometry domain |
| Static Embodiment topology has duplicate/missing segment IDs or invalid parent links | Candidate rejection; exact invariants belong in the Embodiment schema | Embodiment |
| Dynamic pose is missing/duplicated for a required segment, has non-finite translation, invalid quaternion, mismatched body/morphology/digest or incompatible reference frame | Candidate rejection; pose completeness/freshness rules and numeric tolerances require Embodiment decision. Do not calculate missing transforms in Frontend | Embodiment; Frontend verifies contract only |
| Two projections have the same tick but different World/commit identity | Reject the proposed common-cut association | World |
| Owner publication identity/revision/digest is absent, ambiguous, mismatched or not a member of the claimed cut | Reject association; preserve claims separately if existing Observation policy allows | World, Observation |
| A required dynamic owner publication is missing, late or unavailable | Do not present a complete/coherent dynamic scene; expose available claims with separate status. Static revision lifetime/pinning must be resolved separately and is not automatically a late per-tick publication | World, Observation, Frontend |
| Carried response exceeds approved total/count/size limits | Apply the exact owner-approved bound/error policy; the policy must prevent a truncated payload from appearing valid. Numeric limits and error behavior remain undecided | Observation |
| Observation receives valid distinct owner claims and cut evidence | Preserve each claim and provenance independently; do not join or reinterpret them | Observation |

#### Executable-test ownership and gates

| Repository | Candidate test responsibility | Gate before implementation |
|---|---|---|
| Environment | Primitive allowlist, identity uniqueness, finite values, frame/units, empty-set semantics, deterministic digest and bounded size | Environment approves exact static schema and visual/ground convention |
| Embodiment | Topology validity, visual-local-frame convention, canonical render digest, pose completeness/validity and evidence for the transform producer | Embodiment approves exact static and dynamic schemas and source responsibility; no duplicate kinematics |
| World | Exact-cut association, committed identity and publication-reference membership; negative same-tick/different-commit cases; rejection for missing/ambiguous references | World approves the exact consumer verification mechanism, reusing existing causal evidence |
| Observation | Strict allowlist, passive byte-preserving or equivalently lossless carriage, provenance preservation, total/count bounds, invalid payload rejection and no cross-owner join | Observation and affected owners approve exact carried schema/bounds; existing security limits unchanged |
| Frontend | Consume only the approved shape; no fabricated defaults, forward kinematics, implicit joins, stale-source mixing or unverified common-scene label | Contract gates pass; renderer implementation is separately authorized |

These are test plans only. No new test currently proves these candidate
contracts, no new data family has been published, and no renderer implementation
is authorized by the design-base disposition. The exact schemas, static
revision lifetime, frame compatibility rules (including why matching frame
labels alone would or would not suffice), digest canonicalization, numerical
tolerances, size/count limits, error behavior, verifier trust path and
restore/fork semantics remain open decisions in the existing issues. These
vectors are candidate review criteria, not normative acceptance tests. The
equality of frame identifiers or axis labels alone must not be taken as proof
of spatial compatibility. The
registry state for this document therefore remains `proposed` /
`not_evaluated` / `UNRESOLVED`.

### Evidence claim ledger for this revalidation

| Claim | Evidence | Type | Limits |
|---|---|---|---|
| Environment source code has bounded static and resource geometry values | Environment `static_scene.py`, `physical.py`, `procedural_genesis.py` at `d09e45c...` | Implemented (source observed) | Not a general visual contract or browser delivery path |
| Embodiment source code has articulated morphology and owner-validated joint/root state | Embodiment `articulated_spec.py`, `articulated_state.py` at `d73315d...` | Implemented (source observed) | No identified UI geometry publication contract; source presence is not authorization |
| Current Frontend consumes the two bounded M1 claim families and presents their supported coordinates as separate 2D markers, without inferring a scene | Frontend `README.md`, `package.json`, `src/model.js`, `src/views.js` and `src/style.css` at `3b158cc73e57a8175265e1d25a66eb09346679f9`; [PR #24](https://github.com/biopeia/frontend/pull/24) tests | Implemented presentation boundary | No real-browser rendering of authorized 3D geometry was run; no geometry contract or 3D renderer is currently exposed |
| World has a generic post-commit owner-publication verification path | World `observation_publication.py` at `a7c8099...` | Implemented (source observed) | Does not establish complete scene membership or browser support |
| M1 physical-step inputs use a profile-configured same frame ID | World `m1_profile.py`, M1 profile JSON and `adapters/articulated_mujoco.py` at `a7c8099...` | Implemented (source observed) | Adapter checks identifier equality only; it does not validate frame semantics. The M1 profile scene has `objects=()`, and no corresponding spatial Observation publication or browser contract is exposed |
| World validates owner publications against a committed cut, but the browser lacks a shared-cut proof in the current M1 subset | World `observation_publication.py` at `a7c8099...`; Observation `http_bridge.py` and family serializers at `a8b43af...`; design-base disposition [World #162](https://github.com/biopeia/world/issues/162#issuecomment-6200249455) | Implemented + independently reviewed gap; design direction accepted | Limited to the two currently allowlisted M1 families. Equal ticks are insufficient. Exact verifier, consumer trust path and affected-owner contract review remain open |
| Domain owners accepted the spatial publication direction as design base, permitting candidate schema/vector preparation only | [Embodiment #77](https://github.com/biopeia/embodiment/issues/77#issuecomment-6200248780), [Environment #73](https://github.com/biopeia/environment/issues/73#issuecomment-6200249144), [Observation #37](https://github.com/biopeia/observation/issues/37#issuecomment-6200249767) | Owner disposition recorded | Exact owner schemas, field bounds, publication families and implementation authorization remain open |
