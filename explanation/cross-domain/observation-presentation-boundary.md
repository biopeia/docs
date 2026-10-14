# The human-facing presentation boundary

Reviewed against `frontend` at commit `02531dcaaf4419f5d9e11d0915486c7c758d2fe6`
(main on 2026-10-14). Statements are marked by what supports them: the code,
the tests, or an accepted decision. A decision states intent; it is not a
result.

## What it is

The human-facing presentation application is an independent, passive,
read-only presentation shell. It provides human inspection of runs,
spatial configuration, causal timelines, sensorimotor traces, and claim
provenance without participating in the simulation runtime or acquiring
semantic authority.

It belongs outside the seven Biopeia architectural domains
([ADR-0113](../../technical/adr/ADR-0113-independent-frontend-and-lab-boundary.md)).
That placement is constitutional: the application does not execute
simulation steps, does not control organism action, does not hold live
causal state, and does not custody scientific evidence. It is a consumer of
observation views, not a producer of truth.

## Seven peer views

The user experience model
([UX specification](../../technical/design/frontend/biopeia-frontend-ux-spec-v1.md))
defines seven peer-level screens without hierarchy (`frontend:src/model.js::ROUTES`):

1. **Worlds & Runs** (`/worlds`): Discovery and selection of known worlds,
   simulation runs, and committed cuts.
2. **World Overview** (`/overview`): High-level run state, active entities,
   and environmental summary.
3. **Spatial Explorer** (`/spatial`): Spatial arrangement of embodiment and
   environmental resources.
4. **Causal Timeline** (`/timeline`): Ordered sequence of committed World
   cuts, distinguishing causal time from delivery time.
5. **Sensorimotor Trace** (`/sensorimotor`): Physical pose, sensory samples,
   and motor activations across ticks.
6. **Claim Inspector** (`/claims`): Provenance, epistemic basis, and
   lineage verification of individual semantic observations.
7. **Connection & Access** (`/connection`): Status of loopback read adapters,
   governance gates, and security constraints.

## Fail-closed availability and baseline state

The presentation model initializes in an explicit disconnected baseline
(`frontend:src/model.js::initialSource`): status is `'not-configured'`, world,
run, cut, and delivery are `null`, and claims and capabilities are empty
arrays.

Fourteen distinct availability states are defined
(`frontend:src/model.js::AVAILABILITY`): `'not-configured'`, `'loading'`,
`'available'`, `'empty'`, `'unknown'`, `'denied'`, `'unavailable'`,
`'unsupported'`, `'disconnected'`, `'stale'`, `'incomplete'`, `'gap'`,
`'conflict'`, and `'error'`. Every state maps to a specific human-readable
text label; an unrecognized state throws an error.

The read-only model enforces strict data integrity:
`assertReadOnlySource` (`frontend:src/model.js:24-29`) throws an error if
claims or a cut receipt are attached to a source whose status is
`'not-configured'`. Disconnected views cannot be populated with synthetic or
fabricated domain data (`frontend:tests/model.test.js`).

## Epistemic boundaries enforced in presentation

The view renderer (`frontend:src/views.js`) and application shell
(`frontend:src/main.js`) encode strict epistemic limits:

- **Refusal of synthetic 3D geometry:** The Spatial Explorer and World
  Overview display an explicit fallback notice: *"No synthetic scene is
  displayed. Geometry, coordinate frame, units and checkpoint lineage must
  come from authorized publications."* The application refuses to fabricate
  meshes, spatial coordinates, or 3D renderings in the absence of
  authorized domain data (`frontend:tests/views.test.js`).
- **Separation of causal and delivery clocks:** The timeline view displays
  three separate timestamps: Source time, Delivery time, and Browser time
  (labeled *"Not causal time"*). The view states that committed cuts are
  determined by World, and browser delivery order never advances or
  replays the causal runtime.
- **No psychological or teleological inference:** The sensorimotor view
  explicitly enforces that published signals are not evidence of goals,
  intentions, learning, competence, or scientific efficacy unless supported
  by an explicit, competent source claim.
- **Truthful empty state:** When disconnected, the top banner reports:
  *"This is a disconnected application shell, not evidence of
  source-state absence."*

## Disconnection and Content-Security-Policy

The local development server (`frontend:scripts/serve.js`) serves the built
static shell on `127.0.0.1:4173` without external npm dependencies.

To enforce the passive boundary at the browser engine level, the server
issues a strict `Content-Security-Policy`:
`connect-src 'none'; default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; font-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'`.

The directive `connect-src 'none'` prevents the application from initiating
any HTTP fetch, WebSocket, or XMLHttpRequest network operations.

## Readiness gates before live adapter integration

The frontend implementation is a disconnected prototype. Live integration
with Observation is blocked pending the resolution of formal readiness
gates ([Approval and Readiness v1](../../technical/design/frontend/biopeia-frontend-approval-and-development-readiness-v1.md)):

- **Gate C (Observation Feasibility):** Direct in-process access to
  `ObservationPlane` from a browser is prohibited. A safe, loopback-only
  HTTP read bridge with strict origin allowlisting must be formally ratified
  (Observation issue #37).
- **Gate E (Security & Deployment Profile):** Security model, CORS/CSP
  constraints, and deployment boundaries remain unresolved (Docs issue
  #167).

Until these gates are formally resolved, the Connection & Access screen
truthfully displays `Browser read contract: BLOCKED` and
`Observation browser adapter: Not implemented`.

## What supports this description

| Claim | Support |
|---|---|
| Seven peer routes, fourteen availability states, fail-closed read-only assertion | Code in `frontend:src/model.js` and tests in `frontend:tests/model.test.js` |
| Textual fallback for spatial scenes, clock separation, epistemic boundary disclaimers | Code in `frontend:src/views.js` and tests in `frontend:tests/views.test.js` |
| Disconnected shell presentation, XSS escaping, truthful absence notice | Code in `frontend:src/main.js` and `frontend:src/style.css` |
| Enforced disconnection via CSP `connect-src 'none'` | Code in `frontend:scripts/serve.js:14` |
| Architectural role, separation from Lab, non-causal status | Accepted decisions ADR-0113, ADR-0078, ADR-0100, ADR-0101, ADR-0102 |
