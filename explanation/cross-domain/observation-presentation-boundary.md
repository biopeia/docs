# The human-facing presentation boundary

Reviewed against `frontend` at commit `496c05dcd062eb0833abdfb1030cfb87f6f80aa7`
(main on 2026-10-15). Statements are marked by what supports them: the code,
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
(`frontend:src/model.js::initialSource`): status is `'not-configured'`,
`claims` is an empty array, and `scope`, `freshness`, `coherence`, and
`error` are `null`.

Fourteen distinct availability states are defined
(`frontend:src/model.js::AVAILABILITY`): `'not-configured'`, `'loading'`,
`'available'`, `'empty'`, `'unknown'`, `'denied'`, `'unavailable'`,
`'unsupported'`, `'disconnected'`, `'stale'`, `'incomplete'`, `'gap'`,
`'conflict'`, and `'error'`. Every state maps to a specific human-readable
text label; an unrecognized state throws an error.

The read-only model enforces strict data integrity:
`assertReadOnlySource` (`frontend:src/model.js:25-29`) throws an error if
claims or an error are attached to a source whose status is
`'not-configured'`. Disconnected views cannot be populated with synthetic or
fabricated domain data (`frontend:tests/model.test.js`).

## The bounded M1 local read profile

The bounded local M1 read profile
([Approval and Readiness v1](../../technical/design/frontend/biopeia-frontend-approval-and-development-readiness-v1.md),
`frontend:docs/observation-browser-adapter-readiness-v0.md`)
defines a strictly scoped path for local browser inspection without
compromising security or simulation isolation:

1. **Same-origin local proxy (`frontend:scripts/frontend-server.js`):**
   The browser engine never connects directly to the Observation bridge.
   Instead, `frontend-server.js` serves the static assets on `127.0.0.1:4173`
   and exposes a local endpoint `GET /api/observation/current`. Incoming
   requests must match `127.0.0.1:4173` in the `Host` header and require
   same-origin credentials. The proxy forwards valid requests upstream to
   the loopback Observation bridge (`http://127.0.0.1:4174/v1/current`) with
   strict 1 MB payload limits.
2. **Content Security Policy with `connect-src 'self'`:**
   The server enforces a strict CSP:
   `default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; font-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'`.
   The directive `connect-src 'self'` permits same-origin requests to
   `/api/observation/current` while blocking all cross-origin or external
   connections (`frontend:tests/frontend-server.test.js`).
3. **Approved claim family filtering (`frontend:src/observation-client.js`):**
   The client decodes the envelope schema `biopeia.observation.current.v1`
   and validates incoming messages against two approved semantic families:
   - `embodiment.body_pose` (contract `embodiment.body_pose`, revision `v1`):
     validates 3D position vector in meters, XYZW unit quaternion orientation,
     reference frames, context times containing `world_causal_tick`, and
     parent lineage hash `embodiment_state_sha256`.
   - `environment.finite_scalar_field` (contract `biopeia.environment.finite-scalar-field`, revision `1`):
     validates dimensionless scalar value in range `[0.0, 1.0]`, sample point
     in meters, context times containing `world_source_causal_tick` and
     `world_target_causal_tick`, and parent lineage hash `owner_checkpoint_sha256`.
   Any unapproved semantic family is skipped; if no approved claims remain,
   status transitions to `'unsupported'`.

## Serial snapshot refresh and temporal disclaimers

Snapshot updates are governed by a stateful controller
(`frontend:src/snapshot-refresh.js::createSnapshotRefresh`):

- **Minimum interval:** Successive polls enforce a minimum interval of 1000 ms
  (`SNAPSHOT_REFRESH_INTERVAL_MS = 1000`).
- **Serial non-overlapping execution:** An active read sets an `inFlight`
  guard; manual refresh clicks during an active fetch are coalesced.
- **Tab visibility awareness:** The controller subscribes to
  `document.visibilitychange`. If the browser tab is hidden, polling timers
  are paused immediately; upon returning to visible state, an immediate
  fresh read is triggered.
- **Fail-closed claim clearing:** On network error, disconnected bridge, or
  unrecognized payload, `claims` is cleared to an empty array and status is set
  to the error status (`disconnected`, `unavailable`, `unsupported`, or
  `error`). Stale claims are never retained silently.
- **Clock disclaimers in presentation:** Rendered cards display the local
  browser completion timestamp with an explicit disclaimer: *"Local browser
  request completion time; not source time or freshness"*. Sensorimotor and
  overview cards label the delivery sequence clearly: *"Local delivery
  sequence · not causal time"*.

## Live multi-cycle browser acceptance

End-to-end integration is verified by an automated multi-cycle browser suite
(`frontend:scripts/m1-live-session-acceptance.py`,
`frontend:scripts/acceptance-live-browser.mjs`):

1. **Pre-flight dependency pin validation:** Verifies that git clones of
   all runtime dependencies (`world`, `organism`, `embodiment`, `environment`,
   `modality`, `observation`) contain the exact commits specified in
   `world/pyproject.toml`.
2. **Headless Chrome prestart & early polling:** Headless Chrome is launched
   over the Chrome DevTools Protocol (CDP) before World initializes. The
   browser polls the loopback proxy and confirms receipt of truthful 503
   unavailable responses (`browser-ready.json`), proving pre-world attachment.
3. **Live 20-cycle session:** Once browser readiness is recorded, `world-m1`
   executes 20 sensorimotor cycles. The browser refreshes, captures rendered
   cards, extracts lineage hashes, and verifies observation delivery across
   multiple ticks.
4. **Temporal proof rule:** The acceptance runner enforces the invariant
   `browser_attached_at <= world_committed_at <= browser_observed_at` across at
   least two distinct committed World ticks.
5. **Truthful unavailability check:** A separate test against an unreachable
   bridge port (`http://127.0.0.1:1/v1/current`) verifies that the UI
   displays an unavailable diagnostic without claiming absence of underlying
   source state.

## Readiness gate status

Under the M1 milestone, **Gate C (Observation Feasibility)** and **Gate E
(Security & Deployment Profile)** are resolved strictly for the **M1 Bounded
Local Read Profile**. Broader Frontend v1 readiness (interactive controls,
historical runs catalog, external network access, and generalized multi-tenant
deployment) remains intentionally unratified and blocked.

## What supports this description

| Claim | Support |
|---|---|
| Seven peer routes, fourteen availability states, fail-closed read-only assertion | Code in `frontend:src/model.js` and tests in `frontend:tests/model.test.js` |
| Same-origin proxy, loopback isolation, CSP `connect-src 'self'` | Code in `frontend:scripts/frontend-server.js` and tests in `frontend:tests/frontend-server.test.js` |
| Approved claim decoding, typed validation, unsupported filtering | Code in `frontend:src/observation-client.js` and tests in `frontend:tests/observation-client.test.js` |
| Serial non-overlapping refresh, tab visibility pause, fail-closed clearing | Code in `frontend:src/snapshot-refresh.js` and tests in `frontend:tests/snapshot-refresh.test.js` |
| Live multi-cycle Chrome CDP session, temporal proof rule, negative relay bounds | Code in `frontend:scripts/m1-live-session-acceptance.py` and `frontend:scripts/acceptance-live-browser.mjs` |
| M1 bounded readiness acceptance and broader v1 gating | `frontend:docs/observation-browser-adapter-readiness-v0.md` and `docs:technical/design/frontend/` |
| Architectural role, separation from Lab, non-causal status | Accepted decisions ADR-0113, ADR-0078, ADR-0100, ADR-0101, ADR-0102 |
