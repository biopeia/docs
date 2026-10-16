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
| `embodiment` | `4b542455a9c95bcc105a9885eaac395c0d99b921` | `src/embodiment/physics3d/articulated_spec.py`, `articulated_state.py`, `physical_projection.py`; candidate `docs/spatial-render-projection-contract-candidate-v1.md` | Owner-bound morphology and root/joint state remain internal; BodyPose remains root-only. PR #78 adds a non-normative candidate, not a browser-facing publication, final schema, or per-link transform producer. |
| `environment` | `d59770c05366b24a604b220fc9f7b551b27877f7` | `src/environment/static_scene.py`, `spatial_render.py`; `tests/test_spatial_render.py` | Adds a bounded deterministic, detached local projection of existing planes/spheres, frame and Environment identity/revision, metres and render-subset digest. It is not a transport/publication path, general asset format, dynamic state, or cross-domain frame/cut proof. |
| `world` | `51cea9f8975fbdea603592fa5e9c56b073a2f4d4` | `src/world/causal_cycle.py`, `durable_runtime.py`, `observation_publication.py`, `adapters/articulated_mujoco.py`, `m1_profile.py` | World owns causal coordination and committed cuts and validates post-commit owner projections. The current M1 consumer payload still does not expose a verifiable spatial cut association or geometry composition contract. |
| `observation` | `a8b43af65b79ca4e2455bfc1ff1b55faf3d4d353` | `src/observation/semantic.py`, `embodiment.py`, `environment.py`, `http_bridge.py` | Current local/browser path is bounded to BodyPose and finite scalar-field projections. Neither currently allowlisted M1 family exposes a World commit ID/cut receipt in its consumer payload; the bridge explicitly offers per-message, not cross-owner snapshot, coherence. No approved geometry family or durable historical scene query was found. |
| `frontend` | `3b158cc73e57a8175265e1d25a66eb09346679f9` | `src/main.js`, `observation-client.js`, `observation-store.js`, `presentation-scheduler.js`, `views.js`; browser acceptance scripts | The browser displays the two supported claims and independent 2D coordinate markers; it explicitly does not present them as a physical scene. No authorized 3D renderer is present and claims are not reconstructed into meshes. |
| `docs` | `951a4ac610c3bcf64638b4433e99683f5bf5b943` | Accepted Frontend UX/readiness designs; current registry and roadmap | Docs #164 defines spatial rendering truthfulness and screen acceptance; Docs #183 is the current proposal update. Contract-readiness and implementation gates remain applicable. |

These are code/document inspections at the listed revisions, not owner approval
of a new spatial contract. In particular, the existence of frame descriptors,
joint topology, URDF generation, static primitives, physical-step state or
BodyPose does not establish compatible identity, asset lifetime, display
geometry or cross-owner coherence for a browser scene.

### Earlier bounded owner candidate-field dispositions (2026-10-15)

The Domain Owner accepted the candidate field subsets recorded in
[Embodiment #77](https://github.com/biopeia/embodiment/issues/77#issuecomment-6197195602),
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
contract. The direction is recorded in the Owner's disposition on
[Frontend #22](https://github.com/biopeia/frontend/issues/22#issuecomment-6199059732),
with affected-domain records on
[Embodiment #77](https://github.com/biopeia/embodiment/issues/77#issuecomment-6199062525),
[Environment #73](https://github.com/biopeia/environment/issues/73#issuecomment-6199062981),
[World #162](https://github.com/biopeia/world/issues/162#issuecomment-6199063376),
and [Observation #37](https://github.com/biopeia/observation/issues/37#issuecomment-6199063932).
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
that matrix. A clean-current-main production/browser run is recorded in
[World #156's evidence log](https://github.com/biopeia/world/issues/156#issuecomment-6195150220):
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

The Owner's decision on
[Frontend #22](https://github.com/biopeia/frontend/issues/22#issuecomment-6199059732)
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

The design-only follow-ups are
[Organism #176](https://github.com/biopeia/organism/issues/176) and
[World #165](https://github.com/biopeia/world/issues/165). They must inspect the exact
result path, validity checks, physical no-actuation integration and cut
preservation. No change to the present `None` treatment or to actuator/
termination semantics is authorized until those designs and owner reviews
establish the required contract. This investigation does not alter World
\#156's bounded grid-v2 acceptance.

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
2. Environment's `project_spatial_render_scene` now returns a detached,
   canonicalizable descriptor over modeled planes/spheres and the declared
   frame, Environment identity/revision, metre units and a render-only SHA-256
   digest. Source bounds are 128 items, 128 UTF-8 bytes per text value and
   65,536 canonical descriptor bytes. It excludes gravity, friction, genesis,
   checkpoints and dynamic state. This projection is implemented and tested
   at Environment `d59770c05366b24a604b220fc9f7b551b27877f7`; it does not
   itself publish or transport the descriptor, bind it to Embodiment, or prove
   World cut membership. The current M1 profile still has an empty scene.
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
Observation consumer-contract inventory remains tracked by
[Observation #37](https://github.com/biopeia/observation/issues/37). This Issue does not
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
| Embodiment | `4b542455a9c95bcc105a9885eaac395c0d99b921` | `physics3d/articulated_spec.py`, `articulated_state.py`, `physical_projection.py`; candidate `docs/spatial-render-projection-contract-candidate-v1.md` | Internal morphology, root pose and joint state remain as previously described. PR #78 adds a design candidate; the current source still does not establish an external geometry family or per-link transform producer. Exact candidate implementation conformance was not tested in this revalidation. |
| Environment | `d59770c05366b24a604b220fc9f7b551b27877f7` | `spatial_render.py`, `static_scene.py`; `tests/test_spatial_render.py` | `project_spatial_render_scene` implements bounded static projection; focused test command `uv run --with pytest pytest -q tests/test_spatial_render.py` passed (6 tests). This proves the Environment projection contract in this checkout, not external transport, browser delivery, cross-owner compatibility or causal cut association. |
| World | `51cea9f8975fbdea603592fa5e9c56b073a2f4d4` | `observation_publication.py`, `durable_runtime.py`, `adapters/articulated_mujoco.py`, `m1_profile.py`, M1 profile JSON; tests `test_observation_publication.py`, `test_world_post_commit_owner_publication.py`, `test_articulated_production_join.py`; [World #162](https://github.com/biopeia/world/issues/162) | World validates owner publications against an internal `CommittedWorldCut` (world identity, causal tick, commit ID and owner checkpoint references). That server-side validation does not itself expose a consumer-verifiable receipt in the current M1 Observation payloads. Separately, the M1 profile uses the Embodiment profile frame ID for the Environment scene frame (parent `world`, identity basis/origin); the adapter checks ID equality only, not frame semantics, and `m1_profile.py` constructs the scene with `objects=()`. The only commit after the prior source-inspection revision `a7c8099…` changes `uv.lock`; the inspected source files are unchanged. World #162 asks its owner to decide the sufficient consumer-visible cut-association contract; no sufficiency rule is assumed here. Tests were inspected, not run in this revalidation. |
| Observation | `a8b43af65b79ca4e2455bfc1ff1b55faf3d4d353` | `README.md`, `http_bridge.py`, `semantic.py`; tests `test_http_bridge.py`, `test_plane.py`, `test_observational_boundary_adversarial.py` | The documented browser bridge remains bounded to BodyPose v1 and finite scalar-field current projections. The in-memory plane's global delivery sequence is not domain/causal time and it is not durable history. No general geometry publication family or durable scene query was found. Tests were not run in this revalidation. |
| Frontend | `3b158cc73e57a8175265e1d25a66eb09346679f9` | `README.md`, `package.json`, `src/model.js`, `src/views.js`, `src/observation-client.js`, `src/style.css`; [PR #24](https://github.com/biopeia/frontend/pull/24) adds `tests/views.test.js` coverage | Frontend still consumes the same two bounded M1 claim families and has no 3D renderer dependency. PR #24 adds separate SVG coordinate markers for supported finite coordinates, with independent display scaling, owner identity, frame and provenance labels; it expressly does not compose claims into a scene. This is coordinate evidence presentation, not authorized physical geometry or a coherent shared World snapshot. Current-source tests/build were not rerun in this documentation revalidation. |
| Modality | `62af4aba07146d5dfdc978af07bb72111112d873` | `README.md` and `src/` search for geometry/spatial claims | Modality describes narrow, non-authoritative scalar transduction and does not own body/environment geometry. No spatial output contract was identified; this does not imply Modality is absent from all future sensory presentation. |
| Organism | `d8ed534d48188fb2f629faaa8dd85b95063a0c2d` | `README.md` and source search for geometry/spatial publication | Organism owns longitudinal identity/private state and lifecycle, not physical body state. No spatial geometry publication was identified. This design excludes private cognition and does not infer organism activity from geometry. |
| Lab | `e6a084f1abae751a8248b373901150754a403bbc` (`origin/main`; local `HEAD` behind) | Current remote `README.md`; remote inspection confirmed the historical `src/lab/physics3d/engine.py` path is not present in current TARGET main. Lab #63 is closed as not planned/superseded; ADR-0113 and Docs #165 assign the general frontend consumer role to Frontend. | No current TARGET physics renderer was established as reusable. Lab #63 does not make Lab the Frontend owner or authorize use of historical engine code. |
| Docs / Workspace | Docs `76d26cb240625f740c12f52aaaf706cc0ae4515f`; Workspace `4e34c97569aaa1ba5611eda3dab3923cd33dfd83` | Docs #176 registry entry and design; Docs #164 accepted UX design; Docs #183; Workspace #50 / Project history | Docs #176 remains `document_status: proposed`, `implementation_status: not_evaluated`, `architecture_scope: UNRESOLVED`. Docs #164 governs UX/fallback. Workspace M1.1 browser evidence is not a spatial contract. |

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
| Internal articulated morphology and validated joint state | `EXISTING` | Embodiment | `4b54245…`; `physics3d/articulated_spec.py`, `articulated_state.py` | Source inspected; previous focused tests are not evidence for a new render family | Internal owner representation only. Embodiment #77 accepts a design base; exact geometry conventions, digest and transform production remain to be settled. |
| Root body pose projection | `PARTIAL` | Embodiment | `4b54245…`; `physical_projection.py`, `observation_contract.py` | Existing projection test locations inspected; not rerun here | Root pose is not per-segment geometry or link transforms. No second kinematics engine is authorized. |
| Browser-readable articulated geometry and segment transforms | `ABSENT` | Embodiment | `4b54245…`; code plus non-normative candidate doc inspected | No conformance test exists in the inspected source for a published geometry/per-link family | Publication requires exact owner-approved contract and an identified transform producer. See Embodiment #77. |
| Bounded static Environment render projection | `EXISTING` | Environment | `d59770c…`; `spatial_render.py` | `tests/test_spatial_render.py`: 6 passed on the cited checkout | Detached local projection only; no Observation transport, cross-domain frame join, or World-cut proof. Environment #73 approved the bounded baseline; exact consumer composition remains separate. |
| Renderable active M1 Environment scene | `ABSENT` | Environment | Environment `d59770c…`; World `51cea9f…` M1 profile sets an empty scene | Profile/source inspected; no rendered-scene test | The projection can truthfully represent an empty scene; do not invent a floor, objects, terrain or resources. Environment #73. |
| Confirmed World cut and owner-checkpoint validation | `EXISTING` | World | `51cea9f…`; `observation_publication.py`, `durable_runtime.py` | Test locations inspected; not run | Internal validation exists; browser-verifiable proof is not present in current M1 claims. World #162. |
| Consumer-verifiable proof that dynamic projections share one confirmed cut | `ABSENT` | World | `51cea9f…`; current claims lack exposed commit identity/proof | No consumer conformance test identified | Equal tick/frame labels alone are insufficient. Candidate should reuse existing commit/checkpoint evidence; no new history store. World #162 accepts direction only. |
| Current bounded Observation reads for BodyPose and finite scalar field | `PARTIAL` | Observation | `a8b43af…`; `README.md`, `http_bridge.py`, `semantic.py` | Bridge/boundary test locations inspected; not run | Existing current-view transport, not spatial geometry, durable history or shared-cut composition. Observation #37. |
| Passive transport of approved spatial descriptions with provenance | `REQUIRES APPROVAL` | Observation plus publishing owners | `a8b43af…`; current allowlist/read boundary | No spatial-family conformance test identified | Exact family, bounds and provenance must be approved; no semantic joins. Observation #37. |
| Independent 2D markers for supported M1 coordinate claims | `PARTIAL` | Frontend | `3b158cc…`; `src/views.js`, `src/style.css` | PR #24 added view tests; not rerun in this audit | Presentation markers are not a physical scene and do not establish shared coordinates. |
| Authorized spatial 3D renderer for real owner geometry | `ABSENT` | Frontend | `3b158cc…`; `package.json`, `src/` inspection | No real-browser 3D acceptance evidence | Renderer stays blocked until owner contracts, read boundary and cut proof are approved. Frontend #22. |
| Spatial geometry publication role | `ABSENT` | Modality | `62af4ab…`; README/source search | No relevant contract test identified | No spatial authority inferred for Modality. |
| Spatial geometry publication role | `ABSENT` | Organism | `d8ed534…`; README/source search | No relevant contract test identified | Organism identity/private state and lifecycle remain outside physical geometry. |
| Reusable current-target Lab renderer | `ABSENT` | Lab | `e6a084f…` (`origin/main`); current README/path check | No current-target renderer test established | Historical engine path is not present in current target main; Lab #63 is closed as not planned/superseded; ADR-0113 and Docs #165 assign general Frontend ownership to Frontend. |
| Canonical design/readiness record | `EXISTING` | Docs | `0373d063…`; Docs #176 registry, Docs #164 UX | Registry validation is tracked separately from this source inspection | Keep `proposed / not_evaluated / UNRESOLVED`; design-base acceptance does not change registry readiness. |
| Workspace runtime/browser coordination evidence | `EXISTING` | Workspace | `4e34c97…`; Workspace #50 and M1.1 artifacts | Evidence is bounded to recorded M1.1 checks | Operational evidence is not a geometry/cut contract and does not establish Spatial V1 acceptance. |

The matrix records capability, not readiness or acceptance. In particular,
`REQUIRES APPROVAL` must not be read as implementation authorization, while
`EXISTING` owner-side geometry must not be synthesized into a browser scene
without an approved publication and verified cut relationship.

### Candidate contract status (2026-10-15)

The owner-design direction and bounded local publication baselines have since
received distinct dispositions. Do not conflate the implemented Environment
projection with a carried Observation family or a coherent scene. Current
owner dispositions and candidate references are:

| Domain | Candidate evidence | Status and scope |
|---|---|---|
| Environment | [Environment #73](https://github.com/biopeia/environment/issues/73), owner disposition at comment `6201000808`, [merged PR #75](https://github.com/biopeia/environment/pull/75), head `982c555df0cc333aeba536a6c66783f37285652e` | Owner approved the bounded read-only static geometry baseline for implementation/local publication. PR #75 implements `project_spatial_render_scene` for modeled ground-plane/sphere primitives, stable IDs, frames, Environment identity/revision and SI lengths; it excludes solver parameters, seeds/checkpoints, arbitrary assets and dynamics without separate owner-authored state/cut binding. The projection is not an Observation transport path or a cross-domain frame/cut join. |
| Embodiment | [Embodiment #77](https://github.com/biopeia/embodiment/issues/77), owner disposition at comment `6201001211`, [merged candidate-documentation PR #78](https://github.com/biopeia/embodiment/pull/78), head `406c08461a66962bef65ac0bd6715a83e32a05ac` | Owner approved the bounded baseline for implementation/local publication: static articulated geometry/topology and separate dynamic kinematics with identity, revision, units and frames. PR #78 adds a non-normative design candidate only; current `main` does not implement that projection or a per-link transform producer. Exact producer, conventions and bounds remain gated; no Frontend-derived kinematics or solver/private fields. |
| World | [World #162](https://github.com/biopeia/world/issues/162), design disposition at comment `6201001585`, [PR #166](https://github.com/biopeia/world/pull/166) at `10a4d9232f4f61c46bb199049420041b2de228f7` | Owner accepted design work for consumer-verifiable association to the same confirmed committed cut, reusing existing World evidence and no new persistence. The design disposition does **not** authorize implementation/publication. PR #166 is a separate implementation candidate; its exact-head CI was reported green but required review remains pending. |
| Observation | [Observation #37](https://github.com/biopeia/observation/issues/37), carriage disposition at comment `6201002076` | Owner accepted the bounded passive-carriage design direction only: separately versioned/bounded owner-approved claims, provenance preserved, existing local GET/security and payload limits, no joins/history/assets. It does not authorize an allowlist entry, schema, code, or transport change. |

These dispositions are not interchangeable: Environment and Embodiment
approved bounded owner publication baselines; Observation accepted a passive
carriage design direction; World accepted a cut-association design direction,
not its implementation. Exact field sets, limits, producer behavior,
cross-domain frame compatibility, the consumer-verification trust path, and
failure handling remain to be resolved by the responsible owners. The
registry state remains `proposed / not_evaluated / UNRESOLVED`.

The Owner separately directed no-actuation semantics in the design decisions
recorded on [Embodiment #77](https://github.com/biopeia/embodiment/issues/77#issuecomment-6201001211),
[Environment #73](https://github.com/biopeia/environment/issues/73#issuecomment-6201000808),
[World #162](https://github.com/biopeia/world/issues/162#issuecomment-6201001585),
and [Observation #37](https://github.com/biopeia/observation/issues/37#issuecomment-6201002076): Organism must explicitly produce a valid no-actuation result; World must not infer that result from silence/error, issue a neutral or repeated command, or mutate state artificially. Invalid/missing output fails the transition and preserves the last confirmed cut; vital termination must be explicit from its competent domain. The current `None` behavior must not change until its exact call path and contract meaning are documented. This is design direction only, not implementation authorization.

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
  role. Lab #63 is closed as not planned/superseded; ADR-0113 and Docs #165
  assign the general Frontend consumer role to Frontend. Historical Lab
  physics code is not a current TARGET renderer. Neither is a justified
  spatial child task on the current evidence.

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

The Owner accepted the architectural direction in Embodiment #77,
Environment #73, World #162 and Observation #37 as design base. The recorded dispositions
are [Embodiment #77](https://github.com/biopeia/embodiment/issues/77#issuecomment-6200248780),
[Environment #73](https://github.com/biopeia/environment/issues/73#issuecomment-6200249144),
[World #162](https://github.com/biopeia/world/issues/162#issuecomment-6200249455),
and [Observation #37](https://github.com/biopeia/observation/issues/37#issuecomment-6200249767).
This acceptance permits preparation and review of candidate schemas and
conformance vectors. It is not approval of exact fields, wire formats,
implementation, publication, or the Frontend renderer. The following are
illustrative review material, not normative contracts. Existing security/read
limits and owner authority remain in force.

The earlier candidate-gap review used these local `main` revisions as its
source snapshot (not as runtime pins): Workspace
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

#### Concrete candidate review examples (non-normative)

These examples are intentionally a review aid, not JSON Schemas or wire
contracts. Every field name and encoding remains subject to owner approval.
The Environment example is empty because that is the truthful state of the
inspected M1 profile; the non-empty example uses source-owned primitive/frame
shapes only and is not a claim that M1 publishes them. Bracketed values such
as `<world-issued-reference>` are placeholders, not valid JSON values.

Environment candidate, valid empty scene:

```json
{
  "schema_version": "candidate-1",
  "environment_id": "<owner-id>",
  "environment_revision": "<owner-revision>",
  "length_unit": "m",
  "frame": {
    "frame_id": "<owner-frame>",
    "parent_frame_id": "<owner-parent-frame>",
    "origin_m": [0, 0, 0],
    "x_axis_in_parent": [1, 0, 0],
    "y_axis_in_parent": [0, 1, 0],
    "z_axis_in_parent": [0, 0, 1],
    "handedness": "RIGHT_HANDED",
    "up_axis": "Z"
  },
  "items": [],
  "render_geometry_sha256": "<digest-over-defined-render-fields>"
}
```

The angle-bracket values above are illustrative placeholder strings, not
valid values under an approved schema. They must be replaced by
owner-produced values before this can be an acceptance vector. A candidate
invalid value would change `items` to a sphere with `radius_m: -1`, duplicate
an `object_id`, or alter the content without recomputing the digest; all must
be rejected, not repaired by Frontend.

Candidate articulated description and dynamic pose set (shape only):

```json
{
  "body_id": "<embodiment-owner-id>",
  "embodiment_episode_id": "<owner-episode-id>",
  "morphology_revision": "<owner-revision>",
  "render_geometry_sha256": "<digest-over-defined-render-fields>",
  "segments": [
    {
      "segment_id": "<stable-owner-segment-id>",
      "parent_segment_id": null,
      "primitive": {"kind": "sphere", "radius_m": "<positive-owner-value>"},
      "primitive_frame": "<explicit-owner-local-frame>"
    }
  ]
}
```

```json
{
  "body_id": "<same-embodiment-owner-id>",
  "embodiment_episode_id": "<same-owner-episode-id>",
  "morphology_revision": "<same-owner-revision>",
  "render_geometry_sha256": "<same-render-digest>",
  "frame_id": "<owner-declared-reference-frame>",
  "length_unit": "m",
  "quaternion_order": "xyzw",
  "physical_step_correlation": "<World-issued-physical-step-correlation>",
  "poses": [
    {"segment_id": "<every-required-stable-segment-id>", "position_m": [0, 0, 0], "orientation": [0, 0, 0, 1]}
  ]
}
```

The numeric pose above is illustrative only and not a captured Biopeia state.
An actual valid vector must be emitted from the authorized physical-step
producer and validated by Embodiment. Candidate invalid variants include a
missing or repeated segment pose, non-finite component, zero-norm quaternion,
digest/revision mismatch, or evidence from a different physical step. No
Frontend kinematics may fill the gap.

Candidate World association and passive Observation carriage:

```json
{
  "world_id": "<existing-world-id>",
  "causal_tick": "<existing-confirmed-tick>",
  "commit_id": "<existing-commit-id>",
  "members": [
    {"owner": "environment", "claim_id": "<claim-id>", "content_sha256": "<digest>", "owner_checkpoint_ref": "<opaque-world-authorized-ref>"},
    {"owner": "embodiment", "claim_id": "<claim-id>", "content_sha256": "<digest>", "owner_checkpoint_ref": "<opaque-world-authorized-ref>"}
  ]
}
```

```json
{
  "claims": [
    {"family": "<approved-source-family>", "claim": "<unchanged owner claim object with original provenance>"},
    {"family": "<approved-source-family>", "claim": "<unchanged owner claim object with original provenance>"}
  ],
  "world_association": {"<opaque-key>": "<unchanged World-authorized association object>"},
  "delivery_metadata": {"<opaque-key>": "<existing Observation delivery metadata object>"}
}
```

The placeholder values are schema-invalid strings used only to show an
object-shaped opaque envelope; they do not specify the actual wire types.
These are separate candidate values, not an Observation-created join. A
consumer-side negative vector changes only one claim's commit/digest/reference
while retaining the same tick: the consumer must refuse a composed scene and
retain individually labeled claims only. Whether `members` is authenticated
by the approved existing World/Observation trust path, which exact opaque
reference is safe to expose, and whether these values fit existing response
limits remain unresolved domain/security decisions; do not implement these
placeholders as a contract.

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

These are test plans for the cross-domain candidate contracts only. Environment
has since added a local static projection (documented above), but no new
Observation data family or composed scene has been published. The design-base
disposition did not authorize a renderer; the later owner dispositions remain
separate and are summarized below. The exact schemas, static
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
| Environment has a bounded local static render projection | Environment `spatial_render.py` at `d59770c05366b24a604b220fc9f7b551b27877f7` | Implemented; focused tests 6 passed | No publication/transport, dynamic state, cross-domain frame join, or World-cut proof |
| Embodiment source code has articulated morphology and owner-validated joint/root state | Embodiment `articulated_spec.py`, `articulated_state.py` at `4b542455a9c95bcc105a9885eaac395c0d99b921` | Implemented (source observed) | No identified UI geometry publication contract or per-link transform producer; source presence is not authorization |
| Current Frontend consumes the two bounded M1 claim families and presents their supported coordinates as separate 2D markers, without inferring a scene | Frontend `README.md`, `package.json`, `src/model.js`, `src/views.js` and `src/style.css` at `3b158cc73e57a8175265e1d25a66eb09346679f9`; [PR #24](https://github.com/biopeia/frontend/pull/24) tests | Implemented presentation boundary | No real-browser rendering of authorized 3D geometry was run; no geometry contract or 3D renderer is currently exposed |
| World has a generic post-commit owner-publication verification path | World `observation_publication.py` at `51cea9f...` (source file unchanged since `a7c8099...`) | Implemented (source observed) | Does not establish complete scene membership or browser support |
| M1 physical-step inputs use a profile-configured same frame ID | World `m1_profile.py`, M1 profile JSON and `adapters/articulated_mujoco.py` at `51cea9f...` (source files unchanged since `a7c8099...`) | Implemented (source observed) | Adapter checks identifier equality only; it does not validate frame semantics. The M1 profile scene has `objects=()`, and no corresponding spatial Observation publication or browser contract is exposed |
| World validates owner publications against a committed cut, but the browser lacks a shared-cut proof in the current M1 subset | World `observation_publication.py` at `51cea9f...`; Observation `http_bridge.py` and family serializers at `a8b43af...`; design-base disposition [World #162](https://github.com/biopeia/world/issues/162#issuecomment-6200249455) | Implemented + independently reviewed gap; design direction accepted | Limited to the two currently allowlisted M1 families. Equal ticks are insufficient. Exact verifier, consumer trust path and affected-owner contract review remain open |
| Domain owners accepted the spatial publication direction as design base, permitting candidate schema/vector preparation only | [Embodiment #77](https://github.com/biopeia/embodiment/issues/77#issuecomment-6200248780), [Environment #73](https://github.com/biopeia/environment/issues/73#issuecomment-6200249144), [Observation #37](https://github.com/biopeia/observation/issues/37#issuecomment-6200249767) | Owner disposition recorded | Exact owner schemas, field bounds, publication families and implementation authorization remain open |

### Current-source capability and issue revalidation (2026-10-16)

This revalidation supersedes the earlier capability descriptions above where
they conflict with the source revisions listed here. It records source and
runtime evidence; it does not itself authorize work or constitute final Spatial
V1 acceptance. Existing Owner dispositions and linked issue decisions remain
the authorization record. Source-inspected capabilities are not automatically
public claims or cross-domain evidence, and this update does not change this
design's registry state.

| Repository and exact `main` revision | Capability status for Spatial V1 | Current source evidence and limit |
|---|---|---|
| Embodiment — `5019b94fc79ae5672eeee09ba308e382860af931` | `PARTIAL` | `src/embodiment/physics3d/spatial_render.py` provides bounded, authored box geometry, revolute-joint topology, a content digest, and validation/binding for supplied link poses. It explicitly does not compute kinematics or prove World commit membership. The candidate is limited to authored shapes/topology and an owner-provided transform source; it is not general articulated-model support. Issue [#77](https://github.com/biopeia/embodiment/issues/77) remains open. |
| Environment — `4eb1f8c3393a7cdbabcfaf35b8630aaf57de20c1` | `PARTIAL` | `src/environment/static_scene.py` and `spatial_render.py` support owner-authored ground planes and spheres plus bounded projection. The active M1 profile in World still constructs an empty `StaticPhysicalScene(..., objects=())`; the live run showed an empty Environment descriptor. A scalar field is not scene geometry. Issue [#73](https://github.com/biopeia/environment/issues/73) remains open. |
| World — `2432ea86cb2959b114c9cda0345ff66438f81f1a` | `PARTIAL` | `src/world/causal_cycle.py`, `observation_publication.py`, and the articulated MuJoCo adapter produce real post-step Embodiment link poses and bind dynamic owner publications to a confirmed World cut. The production cycle also emits static spatial projections separately. This does not create a verified joint Environment–Embodiment scene, and the active M1 Environment geometry is empty. [World #162](https://github.com/biopeia/world/issues/162) is closed for its bounded committed-cut association work; that closure is not V1 acceptance. |
| Observation — `2c506900aa5ad0864eef7f0ce0ed70d7e8e4ea07` | `PARTIAL` | `src/observation/embodiment.py`, `environment.py`, `spatial_contracts.py`, and the local current-view bridge validate and carry the bounded spatial claim families without computing owner semantics or joining the claims. This is current-view transport, not durable history, and does not make separate claims a coherent shared scene. Issue [#37](https://github.com/biopeia/observation/issues/37) remains open. |
| Frontend — `f719f6170b06a1031be51321cfa1de09795d2981` | `PARTIAL` | `src/main.js`, `spatial-renderer.js`, and `spatial-render-controller.js` consume validated owner projections, render authored geometry and supplied dynamic link transforms with WebGL, keep claims/frame interpretations separate, and expose provenance/empty/stale states. Current-main `npm run check` was recorded as 65/65 tests with a successful static build in the live acceptance record. A separate clean committed-lock browser run demonstrates one bounded `body.arm` orientation change reflected in WebGL; this is not a general multi-joint renderer or a shared Environment–Embodiment frame. [Frontend #27](https://github.com/biopeia/frontend/issues/27) and coordinator [#22](https://github.com/biopeia/frontend/issues/22) remain open. |
| Modality — `62af4aba07146d5dfdc978af07bb72111112d873` | `ABSENT` (spatial publication role) | Current source and README define scalar sensory/transduction responsibilities; no authority for body/environment geometry or a spatial-scene publication was identified. Do not infer such a role from sensor values. |
| Organism — `01c788b5844c7dc05b05160392fa9d860eb6fdd3` | `ABSENT` (physical geometry role) | Organism identity/lifecycle and its explicitly observable outputs are distinct from Embodiment physical geometry. No private cognition or motor intent is required or exposed by the spatial renderer. This audit did not establish a transition-level sensorimotor trace. |
| Lab — `bd24e440763fa1b1df42a168368a3299d75fad32` | `ABSENT` (reusable current-target renderer) | Current target `main` was checked directly; no reusable renderer corresponding to the historical path was established. Lab remains a potential source of scientific tooling, not a substitute owner for Frontend or domain geometry. |
| Docs — `08d6dc61d7ccc6c0e3356b65712c9c908d910c63` | `EXISTING` (design/governance record only) | `registry/designs.yaml` retains `document_status: proposed`, `implementation_status: not_evaluated`, and `architecture_scope: UNRESOLVED` for this design. The code and browser evidence below do not change those values. |
| Workspace — `97f26824d537f8cfb8c431a303b56ffb73da7fd3` | `PARTIAL` (local integration evidence) | `Makefile` and `tools/m1_operator.py` coordinate local `make run`/`make view`; the recorded run used exact domain source revisions and a real browser. The Workspace checkout also has uncommitted operator/test changes and local PNG artifacts, so those tool changes are not evidence of a clean committed Workspace build or CI result. |

#### Issue and dependency reconciliation

| Record | Live status on 2026-10-16 | Spatial V1 interpretation |
|---|---|---|
| Frontend #22 | Open | Existing coordinator; do not create a duplicate. Its live body also includes the broader ObsV1 transition-inspection requirement; current browser evidence does not yet demonstrate pre-cut state, authorized Organism command, adoption/fail-closed result, post-cut state, and resulting sensory publications as a contract-backed transition trace. |
| Embodiment #77 | Open | Owner-side geometry/pose capability and exact remaining contract/producer questions; not a dependency for inventing or computing transforms in Frontend. |
| Environment #73 | Open | Existing owner-authored plane/sphere projection exists. The active M1 world is empty; a real non-empty Environment scene must come from an authorized scenario, not a default visual or test fixture. |
| World #162 | Closed | Bounded cut-association work is integrated; does not assert full cross-owner scene compatibility, persistent history, or ObsV1 transition trace. |
| Observation #37 | Open | Passive current-view carriage exists; remaining issue scope must be checked before any additional family or bounds change. Observation must not join semantic claims. |
| Frontend #27 | Open | Existing renderer-integration child; its issue body limits it to approved carriers and does not authorize new contracts. |
| Frontend #4; Docs #167 | Open | Browser-adapter and deployment/security dependencies are tracked separately. Remote exposure is out of scope here; do not treat those remote gates as permission to alter local security controls. |

#### Real-browser evidence and remaining acceptance boundary

The first live-browser run is recorded in [Frontend #22, comment 6205006335](https://github.com/biopeia/frontend/issues/22#issuecomment-6205006335). Run `da40e237-b5a6-44c5-93db-7218af1ca11d` used profile `m1.scalar-sensorimotor.operator-r3`; World `2432ea86cb2959b114c9cda0345ff66438f81f1a`; Frontend `f719f6170b06a1031be51321cfa1de09795d2981`; Embodiment `73abbc9a639b29b6ebe04112e4b88dbb13de2ed8`; Environment `d59770c05366b24a604b220fc9f7b551b27877f7`; Organism `d8ed534d48188fb2f629faaa8dd85b95063a0c2d`; Modality `62af4aba07146d5dfdc978af07bb72111112d873`; Observation `2c506900aa5ad0864eef7f0ce0ed70d7e8e4ea07`; and MuJoCo `3.15.0`. The recorded Embodiment, Environment, and Organism runtime revisions predate their `main` revisions in the capability table; thus this runtime is not evidence for those exact current-`main` dependencies. In that browser session, the view advanced from cut 44 to cut 95, retained scroll/focus/canvas dimensions through refresh, showed a stale last-known view after World stopped, and issued only local GET requests. The UI distinguished confirmed World tick 263 from the last rendered pose cut 261 instead of claiming a common scene. The operator stopped World at confirmed tick 263 and no owned process remained. The comment also records the bounded performance sample and local artifact paths.

A second clean committed-lock run, recorded in [Frontend #22, comment 6205326260](https://github.com/biopeia/frontend/issues/22#issuecomment-6205326260), directly compared the authorized `render_link_pose` claim with WebGL output. Run `5e950d7d-1aae-4751-8190-49947bf90dea` used the same profile, World, Frontend, and dependency revisions listed above. For `body.arm`, the quaternion changed between confirmed cuts 145 and 159 (y: `0.1449832194` to `0.2815784084`; w: `0.9894341141` to `0.9595382222`), while the origin remained `[0, 0, -0.2]` m. Browser captures were both 418×361 and differed in 5,006 pixels (3.32%). This supports a bounded real pose-to-render change under that committed lock; it is not evidence for the newer Embodiment, Environment, or Organism main revisions, nor for general articulated behavior.

A subsequent live workspace-entrypoint run is recorded in [Frontend #22, comment 6205377946](https://github.com/biopeia/frontend/issues/22#issuecomment-6205377946). Run `1c996c10-0eaa-4142-9c86-a75f4b9abbeb` used profile SHA-256 `1b16404ff02b000f458f8f0718d27356681efcb5a5c7bcd9140b651c50e03bbb`, World `2432ea86cb2959b114c9cda0345ff66438f81f1a`, Frontend `f719f6170b06a1031be51321cfa1de09795d2981`, and the dependency revisions above. The browser's committed cut advanced from 95 to 148. The Workspace root was dirty (`Makefile`, `tools/m1.py`, `tools/m1_operator.py`, and `tests/unit/test_m1_supervisor.py` modified), so this is supplemental integration evidence, not a clean committed Workspace-main acceptance. SIGINT to the supervisor yielded exit 0 and reaped Node; Ctrl-C to the full PTY caused GNU Make to report `Interrupt` and exit 1, without a Python traceback. World was subsequently stopped with manifest status `COMMITTED` at causal tick 274, `pending_tick=null`, and no failure; no World or viewer process remained. Therefore clean child shutdown is observed, but a zero exit code for terminal-wide Ctrl-C is not demonstrated.

Taken together, the runs support a real, passive, bounded Embodiment geometry/pose view and stale/disconnect presentation. They do **not** demonstrate Environment geometry in the active profile, a jointly correlated Environment–Embodiment scene, a general articulated-motion model, the transition-level ObsV1 trace described in the current coordinator issue, or an end-to-end stop through `make` from a clean committed Workspace revision. Focused local lifecycle tests (9 selected, 45 deselected) do not replace that missing clean-workspace integration evidence.

No synthetic geometry or state is accepted as runtime evidence. The current environment's emptiness must remain visible until a genuinely authored and configured Environment scene is used. The full V1 acceptance and design registry states remain unchanged.
