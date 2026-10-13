---
id: design.cross-domain.biopeia-frontend-v1
title: "Biopeia Frontend v1 — Independent Visualization Application"
document_type: design
owner: biopeia-project-owner
created: 2026-10-13
language: en
document_version: 3
---

# Biopeia Frontend v1 — Independent Visualization Application

**Lifecycle:** Proposed; not ratified. The design register is authoritative
for lifecycle and implementation status.
**Owner direction:** Design a complete human-facing frontend as an independent
Biopeia repository/application, separate from Lab.
**Proposed repository:** `biopeia/frontend` (repository name only; not a new
semantic authority).
**Related work:** [Docs #164](https://github.com/biopeia/docs/issues/164),
[Lab #63](https://github.com/biopeia/lab/issues/63), and the Biopeia migration
end-to-end acceptance work.
**Implementation authorization:** Not granted by this proposal.

## 1. Purpose and status of the direction

This design specifies a standalone, complete human-facing application for
visualizing Biopeia runs from actual, authorized Observation publications. It
covers repository boundary, recommended technology, information architecture,
screens, data flow, security, accessibility, deployment concerns, testing and
incremental delivery.

The owner has directed that the frontend be independent rather than placed in
Lab. This is a target allocation direction for this design. It conflicts with
the currently accepted [ADR-0102 — Lab](../../adr/ADR-0102-lab.md), which
assigns Workbench/UI to Lab. That conflict must be reconciled through an
explicit derived constitutional ADR (or an explicit amendment to ADR-0102)
before this design can be ratified or implementation begins. This document
does not silently amend ADR-0102. Until that decision is recorded, the
standalone repository is a proposed application boundary, not an established
architecture fact.

The frontend is a **presentation application**, not a new causal or semantic
authority. Its independence means it has its own source, release and
presentation lifecycle; it does not mean it owns domain state, Observation
semantics, scientific evidence or runtime composition.

## 2. Architectural invariants

1. Domain owners retain authoritative state and meaning: Organism, Embodiment,
   Environment and World remain distinct authorities.
2. Observation is the sole approved passive publication boundary for data
   presented as Biopeia observations. The frontend consumes; it does not
   publish or mutate causal state.
3. A rendered value retains its claim identity, authority, producer/asserter,
   typed subject, epistemic basis, availability, domain time/revision, unit,
   frame, provenance and coherence metadata when applicable.
4. UI joins do not create identity. Cross-domain associations are shown with
   their asserted, unresolved or conflicting status.
5. Only a committed World cut may be labelled committed. Arrival order,
   local clock or animation state cannot establish causal ordering.
6. Missing delivery is not source absence. Stale, partial, unsupported,
   unavailable, unknown, gap and conflict conditions remain distinguishable.
7. No Symbiont interface, payload, identity, state model or behavior is
   supported for compatibility. UC-0001 remains in force: no legacy code and
   no backward compatibility.
8. No display infers goals, reward, food/danger semantics, cognition,
   understanding, learning, competence, efficacy or biological validity.
9. A user may navigate, filter, inspect, replay preserved publications and
   control the camera. These are presentation actions only. Runtime control
   and experiment intervention are explicitly outside v1.
10. A workspace launcher may pin repositories and start the app, but the
    frontend repository owns its presentation code and no domain behavior is
    placed in the workspace.

## 3. Repository and system boundary

### 3.1 Proposed topology

```text
biopeia/frontend       independent human-facing application
biopeia/observation    passive claims/publication capability
biopeia/world          causal runtime and committed-cut authority
biopeia/{organism,embodiment,environment,modality}
                       domain-owned state, contracts and projections
biopeia/lab            scientific apparatus, studies, evidence custody
biopeia/docs           canonical design and decisions
biopeia/workspace      local tooling/orchestration only
```

`frontend` is an application repository, not a domain authority and not a
replacement for Lab. Lab continues to own scientific studies, protocols,
experiment orchestration, evidence admission/custody and analysis. The
frontend may provide a human-facing view used during both exploratory and
scientific work, but displaying data does not admit it as evidence.

### 3.2 Runtime data path

```text
Domain owners
    ↓ owner-authorized projections
World committed causal cut (where causal coherence is claimed)
    ↓
Observation publication path
    ↓ authenticated, read-only consumer access
Frontend data adapter
    ↓ validated view models preserving source metadata
Screens / timeline / spatial renderer
```

The frontend must not import Python domain packages, open owner checkpoint
files, read solver internals, query Lab evidence stores as a substitute for
Observation, or fabricate missing publication joins. A browser-side adapter
may normalize a concrete approved Observation contract into internal view
models, but must preserve source identity/provenance and reject unknown or
incompatible contract revisions rather than silently reinterpret them.

No backend-for-frontend (BFF), gateway, database, or new Observation transport
is authorized by this design. If current deployment requires one, it must be
specified as a separate infrastructure component with a narrow read-only
purpose and its own owner/security review.

## 4. Recommended implementation technology

This is a bounded technology recommendation, not a claim that a stack already
exists in Biopeia. Pin supported versions in the implementation PR and update
them through normal dependency governance.

| Concern | Recommendation | Rationale / constraint |
|---|---|---|
| UI framework | React 19.x with strict TypeScript | Mature component model for a multi-screen data application; keep domain semantics out of components. |
| Dev/build | Vite | Small client-side application with static production assets; no server rendering requirement established. |
| Package manager | npm with committed `package-lock.json` | Keep a standalone repo reproducible without introducing workspace/monorepo coupling. |
| Routing | React Router | Explicit screen routes and shareable run/claim links. |
| Server data/cache | TanStack Query | Handles server-state lifecycle, retries and query cache; must not obscure delivery gaps or turn cached data into “live” claims. |
| 3D | Three.js `WebGLRenderer` behind a small renderer adapter | Mature explicit rendering surface; WebGL2 capability gate and a truthful non-3D fallback. Do not adopt WebGPU-only rendering for v1. |
| 2D charts/timeline | Native SVG/HTML first | Avoid a chart dependency until volume/performance evidence requires one. |
| Runtime validation | Zod or equivalent at the network boundary | Validate untrusted payload structure; family semantics still come from approved contracts, not generated guesses. |
| Unit/component tests | Vitest + Testing Library | Test interpretation, empty/error states and accessible interactions. |
| Browser integration | Playwright | Exercise actual routing, stream/query failure states, keyboard access and renderer fallback. |
| Accessibility target | WCAG 2.2 AA | Keyboard operation, visible focus, contrast, non-color status cues, reduced-motion support and text alternatives. |

The renderer is a presentation adapter only. Three.js object IDs, draw order,
scene graph indexes and interpolated positions are never Biopeia identities or
source state. A 2D/list fallback must preserve access to all values and
provenance without WebGL. For the current official docs: React documents 19.3
as its latest version, Vite provides a React TypeScript template and optimized
static build, and Three.js `WebGLRenderer` uses WebGL 2. These facts support
the stack choice but do not establish project compatibility or runtime
performance. See the [React versions page](https://react.dev/versions),
[Vite guide](https://vite.dev/guide/), and
[Three.js WebGLRenderer docs](https://threejs.org/docs/pages/WebGLRenderer.html).

### 4.1 Technology explicitly not selected

- No WebGPU-only renderer, game engine, digital-twin platform or 3D asset
  pipeline.
- No frontend-owned database or event broker.
- No GraphQL/REST/WebSocket/SSE choice until Observation's approved delivery
  and query contracts require it.
- No design-system package or final visual token system is selected here. A
  [proposed visual design companion](biopeia-frontend-visual-design-v1.md)
  supplies candidate tokens and static mockups for review; it is not ratified
  and does not authorize component styling or implementation. Do not borrow
  Symbiont UI tokens as Biopeia authority.
- No authentication provider, deployment vendor or public/private access
  posture is selected; those depend on the deployment threat model and data
  classification.

## 5. Users and v1 use cases

### Primary users

- Biopeia developers inspecting a local or controlled TARGET run.
- Researchers reviewing a run's published state and provenance without
  treating the viewer as evidence custody.
- Repository/domain owners verifying that public projections match committed
  owner state at the declared scope.

### V1 use cases

- Select an authorized World/run context and see whether publications are
  available, delayed, stale, incomplete or disconnected.
- Follow committed causal cuts and compare them with relevant owner claims
  without falsely presenting a global atomic snapshot.
- Inspect available embodied geometry/pose in 3D when contracts define the
  necessary subject, frame, unit and revision.
- Trace published sensory inputs, Organism-originated action claims, physical
  results, owner adoption and committed cut only where explicit correlation
  supports the links.
- Inspect a single claim's authority, epistemic basis, provenance, time and
  availability.
- Replay retained observational publications where the delivery contract
  guarantees replay; make no claim of causal re-execution.

## 6. Screen map and behavior

### 6.1 Application shell

Persistent shell contains Biopeia identity, current environment/run context,
connection/publication health, navigation, user/account controls and a
non-dismissable global warning area for stale/disconnected data. The header
must not show “running” or “paused” unless those states are explicitly
published with their authority and domain time.

Routes should be deep-linkable, e.g. `/worlds/{world_id}/runs/{run_id}` and
`/claims/{observation_id}` only when those identifiers exist under the
approved issuer/scope. IDs are encoded safely and do not substitute for
subject identity.

### 6.2 Screen 1 — Runs and World browser (`/worlds`)

Purpose: find authorized World/run contexts without implying that a run is a
World or that the frontend starts one.

Content:
- filterable list of World identity, run/study relation if published, latest
  committed cut, last publication time (labelled collection/delivery time),
  availability and access scope;
- explicit `No authorized World publication`, `No runs returned`, loading,
  failed query, stale cache and permission-denied states;
- source and query refresh controls that only re-read Observation.

No “Create World”, “Start”, “Resume” or intervention controls in v1.

### 6.3 Screen 2 — World run overview (`/worlds/{world_id}/runs/{run_id}`)

Purpose: high-level inspection of one run's published causal state.

Layout regions:
1. **Identity/context strip:** World ID, run/study IDs when real, selected
   committed cut, Organism/Presence/Body links only when explicitly asserted.
2. **State summary:** owner-projected cards for Organism, Embodiment and
   Environment with each domain's own time/revision and availability.
3. **Spatial canvas:** 3D scene, if compatible spatial claims exist; otherwise
   a precise unsupported/unavailable panel with a link to claims that are
   available.
4. **Recent causal timeline:** latest committed cuts and linked publications.
5. **Signal/action trace summary:** only explicit correlation edges; unlinked
   items remain separate rather than heuristically joined.
6. **Provenance drawer:** current selected cut's included claims, authorities,
   revisions, coherence scope and source references.

A summary is not a global snapshot unless every included claim meets the
World-cut coherence contract. Otherwise label `best-available composite` and
show the per-claim revisions.

### 6.4 Screen 3 — Spatial inspection (`/worlds/{world_id}/spatial`)

Purpose: inspect actual published physical state, not provide a game-like
simulation.

Controls: orbit/pan/zoom camera; reset view; select a published body/part or
environment feature; toggle available claim layers; select a committed cut.
All controls are local presentation actions.

Rules:
- Render only geometry and pose grounded in claims with explicit frame,
  units, subject and morphology/environment revisions.
- A body model may be schematic if the source contract only supports a
  schematic representation; label the representation and never imply missing
  morphology detail.
- Interpolation is off by default. If added later, label it `presentation
  interpolation`, show source endpoints and preserve the sampled states.
- No inferred terrain, resources, receptor rays, force arrows, body animation
  or contact points without published claims sufficient to support them.
- Provide a non-WebGL fallback with a structured list/table of the same
  selected entities and metadata.

### 6.5 Screen 4 — Causal timeline and replay (`/worlds/{world_id}/timeline`)

Purpose: navigate published causal history.

Timeline row types are visually distinct: committed World cut; owner claim;
physical step/candidate; Observation delivery/gap; lifecycle event. A candidate
or rejected step cannot use the committed-cut visual treatment.

Controls: select time range, filter by typed subject/authority/family,
step through retained publications, play/pause a **presentation replay** and
change playback speed. Playback does not advance World. Ordering uses the
contract's declared ordering scope; wall-clock timestamp is a secondary axis.
Gap detection and replay boundary are visible. If no replay contract exists,
only current/latest authorized view is exposed.

### 6.6 Screen 5 — Sensorimotor trace (`/worlds/{world_id}/trace`)

Purpose: inspect explicitly linked claims along the causal path.

Render an event/correlation graph using source references:

```text
committed source cut
  → receptor/transduction claim (if published)
  → Organism action/intention claim (if published)
  → Embodiment command/result claim (if published)
  → owner adoption claim(s)
  → committed resulting World cut
```

Each edge displays the exact shared correlation/lineage relation that supports
it. Missing edges are shown as `not linked by available evidence`, never
filled using time proximity, matching filenames or process order. The screen
must not label a relation `caused by` unless the source contract explicitly
asserts that relation; correlation alone is not causation.

### 6.7 Screen 6 — Claim inspector (`/claims/{claim_id}`)

Purpose: inspect one SemanticClaim and related delivery metadata.

The page separates semantic claim fields from envelope/delivery fields and
shows:
- family and semantic revision;
- issuer-scoped observation/claim ID, if supplied;
- typed subject and explicit cross-domain links;
- primary semantic authority, producer, asserter and measurement source;
- epistemic basis and availability/completeness;
- domain time/revision, separate from host collection/delivery time;
- value with declared units and frame;
- lineage/provenance links and effective configuration references;
- delivery sequence, duplication/gap/resume metadata only where defined;
- coherence scope/World cut relation;
- source limitations and unsupported interpretations.

No value formatter may silently convert units, round away meaningful
precision, flatten epistemic status or omit a material conflict. Raw payload
view may be offered only if access control permits and sensitive fields are
redacted by the source contract; raw payload is not a new canonical record.

### 6.8 Screen 7 — Access and connection status

A compact status page/drawer shows the configured Observation source, identity
of the authenticated principal where appropriate, granted read scope, last
successful fetch/delivery, reconnect/retry state and current error. It must
not expose tokens or secrets. A disconnected view must clearly mark cached
content as stale and preserve the timestamp/revision it came from.

### 6.9 Information depth across the seven screens

Observatory, Inspector and Scientific Trace are descriptive labels for
increasing information depth, not user-facing modes, navigation groups,
workspaces, menus or routes. The only first-level destinations are the seven
peer screens defined in the UX specification. Within any screen, a user may
drill from a readable summary to a subject/claim inspection and then to the
source-backed provenance available for that same selection. This changes
information density only; it does not change source identity, authority or
epistemic status. No navigation transition may upgrade correlation into
causation or a claim into scientific evidence.

### 6.10 Low-fidelity layout and navigation

The following wireframes define information hierarchy, not visual tokens or
final styling. The persistent shell exposes source/delivery health separately
from the selected causal cut. All panels link to the same source-backed
selection. The navigation illustration uses the seven peer-level screen
destinations only.

```text
OBSERVATORY — /worlds/{world_id}/runs/{run_id}
┌──────────────────────────────────────────────────────────────────────┐
│ Biopeia  World … / Run …       Cut: committed N   Delivery: delayed  │
├─────────────────┬───────────────────────────────────┬────────────────┤
│ Worlds & Runs   │                                   │ Published      │
│ World Overview  │   Spatial view / textual fallback│ subjects       │
│ Spatial Explorer│   (selected committed cut)        │ + availability │
│                 │                                   │                │
├─────────────────┴───────────────────────────────────┴────────────────┤
│ Causal Timeline · Sensorimotor Trace · Claim Inspector · Access        │
└──────────────────────────────────────────────────────────────────────┘

CLAIM INSPECTOR — /claims/{claim_id}
┌──────────────────────────────────────────────────────────────────────┐
│ Claim …  Family/revision …      Source: available / delivery: gap     │
├───────────────────────────────────┬──────────────────────────────────┤
│ Value (unit/frame)                │ Subject / authority / producer   │
│ Epistemic basis / availability    │ Domain time / revision           │
├───────────────────────────────────┴──────────────────────────────────┤
│ Provenance and explicit cross-domain links                           │
└──────────────────────────────────────────────────────────────────────┘

CAUSAL TIMELINE / SENSORIMOTOR TRACE — source-backed routes only
┌──────────────────────────────────────────────────────────────────────┐
│ Selected committed cut …       delivery continuity: gap detected    │
├──────────────────────────────────────────────────────────────────────┤
│ Claim A ── explicit relation ── Claim B ── no published link ── Claim C│
├──────────────────────────────────────────────────────────────────────┤
│ Source refs | epistemic status | revisions | replay boundary          │
└──────────────────────────────────────────────────────────────────────┘
```

Navigation consists only of the seven peer-level screens: Worlds & Runs,
World Overview, Spatial Explorer, Causal Timeline, Sensorimotor Trace, Claim
Inspector, and Connection & Access. A selected cut/claim remains visible in
the breadcrumb and URL only when a deep link is supported by the source
identity contract. No UI affordance may
suggest starting, pausing, changing or intervening in a World.

### 6.11 Interpretive restraint

Visual richness does not increase evidentiary strength. A rendered pose shows
only that a pose claim was published under the displayed authority,
revision, frame and epistemic basis. It does not demonstrate learning,
intention, competence, causal attribution, biological validity or scientific
success. Animation, labels, color, camera emphasis and summaries must not
imply any of those properties unless the source contract explicitly supports
that exact claim. In particular, body movement is not proof of learning or
intent.

## 7. Application architecture

Recommended separation inside `biopeia/frontend`:

```text
src/app/              routes, shell, feature composition
src/observation/      transport adapter and contract-version decoders
src/domain-view/      presentation view models preserving source refs
src/features/         run browser, overview, timeline, trace, claim inspector
src/spatial/          renderer adapter, scene lifecycle, non-WebGL fallback
src/accessibility/    shared keyboard/status/live-region primitives
```

### Data lifecycle

1. Establish identity/session using a separately approved access mechanism.
2. Query or subscribe to an approved Observation publication surface.
3. Validate the envelope and semantic family/revision at the boundary.
4. Preserve each source claim and delivery record without merging their
   identities.
5. Build presentation view models that carry source refs, revisions and
   limitations through every rendering layer.
6. On gap, disconnect, unsupported revision or authorization failure, expose
   the state explicitly; do not silently use stale cache as current.

V1 must support finite CPU/memory limits: bounded in-memory rendering window,
virtualized lists for large retained histories, explicit query ranges and
cleanup of renderer resources. These are frontend implementation controls,
not retention policy for Observation or World.

### Minimum consumable Observation contract (gate, not a schema)

The frontend must not be designed against guessed or fixture-only payloads.
Before a screen consumes a family, that family must have an approved
semantic-family contract and an actual supported Observation publication /
query contract. This section states required information, not a record,
envelope, endpoint or transport design.

At minimum the approved contracts used by a screen must make the following
distinctions available, either directly or through stable references:

| Required distinction | Why the frontend needs it |
|---|---|
| Family identity and semantic revision | Refuse unknown meanings; do not infer meaning from a transport version. |
| Typed, issuer-scoped claim and subject identity | Prevent subject identity from being confused with claim or message identity. |
| Primary authority, producer/asserter and epistemic basis | Present who owns the meaning separately from who emitted a representation and how it is known. |
| Domain time/revision, including relevant morphology/environment revision | Prevent host time or a newer delivery from silently changing source validity. |
| Availability/completeness and units/reference frame when applicable | Distinguish absent, unknown, partial, stale and uninterpretable values. |
| Provenance/lineage and explicit cross-domain links | Render relationships only when a source reference supports them. |
| Coherence scope and committed World-cut reference when claimed | Avoid calling a composite view an atomic snapshot. |
| Delivery ordering scope, stable delivery identity/sequence, duplication and gap semantics | Detect delivery discontinuity independently of source state. |
| Query/subscription completeness, resume/replay boundary and access scope | Tell the user what was requested, what was delivered and what is authorized. |

These requirements derive from the approved Observation Semantic Model v1;
they do not authorize a concrete schema or transport. If a needed distinction
is absent, the corresponding screen or interpretation remains unavailable
and the gap is reported. The frontend must not repair the source contract by
joining on timestamps, inventing identifiers or interpreting opaque values.

### Causal state and delivery state are orthogonal

Every live view keeps at least two independent status dimensions:

1. **Source/causal status:** authority-backed source value, domain time and
   revision, availability, and whether a World cut is committed.
2. **Delivery status:** connection, last received delivery identity/sequence,
   ordering scope, gap/resume state, completeness and collection time.

For example, a known committed cut may remain the latest confirmed source
state while its delivery is delayed or has a gap. Conversely, a healthy
connection does not prove that a complete or current source snapshot was
delivered. The shell and claim views must display both dimensions and must
not replace source availability with connection health. Cached content is
labelled with its original source revision and separately marked stale for
delivery purposes; a delivery failure never rewrites the source claim as
`UNKNOWN`.

## 8. Security, privacy and operational requirements

- Read-only access; no credentials embedded in static assets or local storage.
- Authentication and authorization are enforced by the approved service
  boundary. The frontend hides controls for denied operations but is not the
  security boundary itself.
- Least privilege: user sees only Worlds/runs allowed by the source.
- Treat all publication text and metadata as untrusted input; escape rendered
  content and reject active HTML.
- Deployment must use HTTPS, secure session handling, restrictive Content
  Security Policy and dependency scanning.
- Do not persist private cognitive state, secrets or raw scientific evidence
  in browser storage. Any local cache is scoped, bounded, user-clearable and
  contains only authorized Observation data.
- Audit logging, retention and data export require a security/privacy review;
  no export function is included by default.
- Protect against misleading stale data, identifier spoofing, unsafe links,
  oversized payloads and renderer resource exhaustion.

Exact authentication provider, session mechanism, network topology, data
classification, audit retention and hosting vendor remain unresolved and are
required security/deployment decisions before production exposure. A local
single-user development mode may use a local Observation endpoint only if it
still goes through the same authorized publication path; it must not read
owner files directly.

## 9. Accessibility and responsive behavior

Target WCAG 2.2 AA. All navigation, filters, timeline selection, drawers and
claim inspection must work by keyboard with visible focus. Status must use
text/icon plus color, not color alone. Dynamic updates must avoid announcing
every high-frequency event; provide a user-controlled summary/live-update
mode. Respect reduced motion and avoid forced camera movement. Ensure charts
and 3D scenes have equivalent textual summaries, contrast is sufficient, and
zoom/text scaling does not hide critical metadata. Test screen-reader names,
focus order, error recovery and responsive layouts at narrow and wide viewports.

The 3D canvas is never the only way to access a value or state. The view must
remain useful without GPU/WebGL support.

## 10. Visual design system

This proposal defines information hierarchy and behavior, not final brand
styling. Before UI implementation, create a small frontend-owned design
system specification covering:

- semantic status colors with non-color labels;
- typography and density for data-heavy inspection;
- spacing and responsive breakpoints;
- focus, hover, selected, disabled, loading, stale, partial, error and
  permission-denied states;
- chart/3D annotation conventions and data-vs-presentation distinction.

Do not copy Symbiont's visual tokens or represent aesthetic familiarity as
Biopeia's design authority. No component implementation should begin while
this required visual specification is absent.

### Provisional performance budgets

The following are **engineering targets for a first benchmark**, not
constitutional guarantees or claims about current Observation throughput.
They must be measured on a documented reference device/browser and a
versioned representative synthetic dataset before implementation acceptance.
If the benchmark shows a target is not appropriate, revise it with the
measurement and trade-off recorded rather than hiding overload or dropping
source history.

| Workload | Initial target |
|---|---|
| Shell and non-3D run overview usable after warm-cache navigation | p95 ≤ 2.5 s on the documented reference profile |
| Local UI response (selection, filtering loaded data, drawer open) | p95 ≤ 100 ms, excluding network/source query time |
| Spatial presentation | ≥ 30 frames/s at p95 on the reference scene, with explicit non-WebGL/list fallback |
| Live update rendering | Batch/coalesce presentation refreshes; do not render more than 10 UI refreshes/s per view by default. Do not discard received source claims merely to meet this rendering budget; retain source/delivery identities and expose overload or truncation. |
| In-memory history | Default to a bounded 10,000-row window per active timeline; query older ranges explicitly and release evicted view models/resources |
| Overload behavior | Surface lag, gap, truncation or unsupported scale; never silently claim complete delivery after local dropping |

The first benchmark must state device/browser/viewport, cache state, scene
complexity (entities, geometry and update rate), publication rate, history
length, concurrent claims and measurement method. It must report p50/p95,
memory, dropped/coalesced presentation updates and fallback behavior. These
targets constrain presentation work only; they do not change Observation
retention, delivery guarantees or causal runtime performance requirements.

## 11. Testing and acceptance

### Unit and contract tests

- decoder accepts only supported Observation envelope/family revisions;
- unknown or malformed revisions fail visibly and safely;
- authority, identity, domain time, availability, provenance and delivery
  metadata survive mapping into the view model;
- missing/gap/stale/partial/unsupported/conflicting states remain distinct;
- cross-domain identity joins require explicit source links;
- formatting does not silently convert units or erase epistemic basis.

### Component and browser tests

- screen states: loading, empty, permission denied, disconnected, stale,
  unsupported, partial, conflict, gap, and populated;
- timeline ordering follows declared scope, not arrival/wall clock;
- rejected/uncommitted candidates never look committed;
- playback never calls a causal mutation endpoint;
- camera controls cannot emit domain commands;
- 3D supported and WebGL-unavailable fallback;
- keyboard-only navigation, visible focus, reduced motion and screen-reader
  labels for all essential information;
- security cases for script/HTML injection, oversized payload and unsafe link.

### End-to-end acceptance

A real TARGET Observation publication from an actual committed World cut must
reach the standalone frontend through the approved production publication
path. No fixture may manufacture the final publication or bypass a missing
integration join. The report records exact repository revisions, config,
command, principal/access scope, claim/cut identities, displayed metadata,
negative cases, limitations and what the run does not prove. This frontend
acceptance is a presentation consumer test; the overall migration's separate
end-to-end causal-cycle criterion remains independent.

## 12. Delivery phases and dependencies

### Phase 0 — authority and contract reconciliation (blocking)

1. Record a derived constitutional decision reconciling independent frontend
   placement with ADR-0102.
2. Reconcile Lab #63: it must not describe Lab Workbench as the frontend
   target; separate any remaining Lab scientific-app requirements from the
   standalone presentation app.
3. Identify actual Observation publication/query/replay contracts and data
   scopes; do not create schemas here.
4. Approve the frontend visual-system and security/deployment specifications.

### Phase 1 — application shell and truthful data states

Create `biopeia/frontend` with the approved React/TypeScript/Vite stack,
application shell, routes, access/connection status, contract decoder and
read-only run browser. No fake demo records in production mode.

### Phase 2 — claim and timeline inspection

Implement claim inspector, committed-cut timeline, gap/stale/partial states
and provenance details using real approved publications.

### Phase 3 — spatial view and causal trace

Add the Three.js renderer adapter and textual fallback only once compatible
pose/geometry/family contracts exist. Add the sensorimotor trace only where
source publications have explicit links.

### Phase 4 — end-to-end acceptance and deployment

Exercise exact pinned domain revisions and authorized Observation path;
perform accessibility, security and performance checks; document limitations;
obtain independent review proportionate to risk. Deployment follows only
after auth/privacy decisions and operations ownership are ratified.

## 13. Alternatives and trade-offs

- **Lab-hosted Workbench:** simpler repository count and consistent with
  current ADR-0102, but contrary to the new Owner direction. Not selected for
  this design; the conflict requires explicit ADR reconciliation.
- **Standalone frontend application:** selected by Owner direction; provides
  independent release, UX and deployment lifecycle. Adds a repository and
  requires explicit cross-repo access/security contracts. It is not a new
  semantic authority.
- **UI inside Observation:** rejected; passive observation capability and
  human-facing presentation have different responsibilities.
- **UI in workspace:** rejected; workspace is tooling/orchestration, not a
  product or durable application repository.
- **Server-rendered/full-stack frontend or frontend-owned BFF:** deferred;
  no requirement currently justifies backend/data custody duplication.
- **Game engine / WebGPU-only renderer:** deferred; unnecessary to prove the
  first truthful visualization and carries support/performance costs.

## 14. Decisions still required before ratification/implementation

1. Explicit constitutional disposition of ADR-0102's Workbench/UI allocation.
2. Final repository name and ownership/release responsibility (proposed
   `biopeia/frontend`).
3. Actual Observation read/query/stream/replay contracts and supported family
   revisions.
4. Production authentication/authorization, data classification, deployment
   topology and operational ownership.
5. Frontend visual-system specification and approval.
6. Whether to expose local-run selection/launch controls; excluded from v1
   until separately authorized.
7. Whether saved views/export are required; excluded by default.

These are concrete gates. They do not prevent finishing this design proposal,
but they prevent its ratification or production implementation where they
would require authority or security assumptions.

## 15. Governance and scope of claims

This document is a proposed design, not an implementation authorization. It
does not amend ADR-0102, authorize a new semantic authority, define an
Observation schema or transport, admit scientific evidence, authorize runtime
control, or claim that a frontend currently exists. Acceptance of the
independent-repository direction must be recorded by the competent
constitutional process before implementation.

A frontend can make published state inspectable. It cannot by itself prove
causal correctness, complete publication, learning, efficacy, scientific
validity or successful migration closure.

## Companion specifications

- [Functional, interaction and UX specification](biopeia-frontend-ux-spec-v1.md)
- [Visual design specification and concept mockups](biopeia-frontend-visual-design-v1.md)
- [Approval and development readiness plan](biopeia-frontend-approval-and-development-readiness-v1.md)

The readiness plan is a Proposed companion. It records gates and follow-up
ownership; it does not authorize implementation or change this design's
status.

## References

- [ADR-0078 — Observation is causally passive](../../adr/ADR-0078-observation-is-causally-passive.md)
- [ADR-0100 — Observation capability and evidence custody](../../adr/ADR-0100-observation-capability-and-evidence-custody.md)
- [ADR-0101 — Operator Control](../../adr/ADR-0101-operator-control.md)
- [ADR-0102 — Lab](../../adr/ADR-0102-lab.md)
- [Observation Architecture for Biopeia v1](../observation/observation-architecture-biopeia-v1.md)
- [Observation Semantic Model v1](../observability/observation-semantic-model-v1.md)
- [Lab #63 — Render committed World projections](https://github.com/biopeia/lab/issues/63)
- [Docs #164 — Frontend design tracking](https://github.com/biopeia/docs/issues/164)
