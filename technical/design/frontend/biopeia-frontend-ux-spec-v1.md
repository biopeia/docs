---
id: design.cross-domain.biopeia-frontend-ux-spec-v1
title: "Biopeia Frontend v1 — Functional, Interaction and UX Specification"
document_type: design
owner: biopeia-project-owner
created: 2026-10-13
language: en
document_version: 3
updated: 2026-10-13
parent_design: design.cross-domain.biopeia-frontend-v1
---

# Biopeia Frontend v1 — Functional, Interaction and UX Specification

> **Status:** Proposed companion specification, not ratified. This document refines product design but does not amend ADR-0102, create Observation contracts, authorize a frontend repository, define a causal API, or grant implementation authorization. All source data in production must come through approved, read-only Observation publication/query paths.

## 1. Product definition

### 1.1 Mission

Provide an independent, human-facing scientific observation application that makes authorized Biopeia publications navigable, intelligible and inspectable, while explicitly preserving source authority, epistemic limits, temporal scope, availability, identity and provenance. The application **visualizes**; it neither orchestrates runs nor creates/adopts scientific evidence.

### 1.2 User outcomes

1. Find an authorized World and relevant run context, without implying that a run is a World.
2. Understand the latest **published** committed World cut and recognize when that information is delayed, partial or stale.
3. Inspect published bodies, pose and environment context without inventing geometry, sensations, interactions or intentions.
4. Navigate ordered cuts and retained publications without confusing presentation replay with causal replay.
5. Follow only explicitly asserted identities, lineage and correlation relationships.
6. Open any visible value's claim, authority, measurement basis, revision and scope.
7. Understand why a value is missing, inconsistent, unsupported or inaccessible, and what read-only recovery actions are available.

### 1.3 Explicit non-goals for v1

No World/run creation, starting/stopping, embodiment replacement, organism injection, experiment scheduling, body manipulation, command submission, authoring/annotation of domain state, acceptance of scientific evidence, synthetic scientific claims, cross-source heuristic joining, inferred learning/intention/competence, unapproved export, saved server-side views, or automatic semantic corrections. A possible future operator console is a separate authorization and product specification under its own control authority.

### 1.4 Seven peer-level screens (owner-approved product direction)

The application has **seven equally reachable, first-level screens**. Observatory, Inspector and Scientific Trace may describe user tasks in documentation, but they are **not navigation groups, workspaces, menus or additional routes**.

1. Worlds & Runs — discovery of authorized World/run contexts.
2. World Overview — selected run's published context, with the spatial surface as the primary focal point.
3. Spatial Explorer — full spatial investigation with source traceability.
4. Causal Timeline — committed cuts and publication history.
5. Sensorimotor Trace — explicitly linked published claims.
6. Claim Inspector — precise claim/envelope/provenance inspection.
7. Connection & Access — read-only source/access diagnosis.

The initial visual experience prioritizes **World and spatial presentation**, but does not privilege a visual inference over source authority. If a spatial contract is absent, the initial screen presents a truthful non-3D state, not substitute simulated geometry. Seven peer-level navigation items remain keyboard accessible; context-dependent screens clearly explain their prerequisites.

### 1.5 Product directions adopted on 2026-10-13

These are **owner-approved product design directions**, not constitutional ratification, contract approval, security approval, repository creation or implementation authorization:

- **Navigation:** seven peer-level screens, without three-workspace grouping.
- **First-use emphasis:** World and spatial visualization lead the experience, with source integrity continuously visible.
- **Visual identity:** immersive spatial environment with prominent 3D, restrained scientific instrumentation and never game-like invented state.
- **Language:** English UI for v1; localization-ready architecture and Spanish deferred to a separately scoped release.
- **Themes:** light and dark are both required for v1, each accessible and tested; no theme may encode epistemic status exclusively in color.

These directions refine UX only. All architecture, Observation, authority, no-legacy, privacy and causal/passive invariants remain unchanged.

## 2. Personas, jobs and top tasks

| Persona | Objective | Success evidence | Relevant surfaces |
|---|---|---|---|
| Researcher | Inspect what was published at a selected committed cut | Cut ID, scoped claims, revisions and limitations can be traced | Overview, Timeline, Claims |
| Domain owner | Check that authorized owner projection is displayed faithfully | Identity, unit, revision, provenance and availability preserved | Claims, Spatial, Overview |
| Developer | Diagnose absent/incompatible/delayed publication | Concrete distinction between no source data, no delivery, stale cache, unsupported contract and denied access | Worlds, Access, Claims |
| Scientific reviewer | Distinguish an observed correlation from a justified causal assertion | Every graph edge cites its asserted relation or is absent | Trace, Timeline, Claims |
| Accessibility/low-capability user | Use core inspection without WebGL, pointer dragging or high-frequency motion | Equivalent table/text representation, keyboard navigation and summarized updates | All |

Primary desktop use for investigation; narrow-screen usage supports inspection, not full simultaneous multi-panel density. No privileged admin role is assumed.

## 3. Invariants and mandatory display model

**F-01 / data authority:** All authoritative data traverses approved Observation. Any UI local state (selected run, camera, filters, playback cursor) is explicitly presentation state.

**F-02 / claim fidelity:** For each rendered claim, preserve, where published and applicable, issuer-scoped identity, typed subject, semantic family/revision, semantic authority, producer/asserter, epistemic basis, source domain time/revision, unit/frame, availability/completeness, lineage/provenance, configuration and coherence scope.

**F-03 / separate time axes:** Domain time, World cut order, source collection time, Observation delivery time and browser wall clock are never interchangeable. A single “latest” label is prohibited unless its reference axis is named.

**F-04 / cut semantics:** A World cut is marked committed only when its authority and commitment are explicit. Claim collections with distinct owner revisions must not masquerade as an atomic global snapshot. Label such a collection **best-available composite**, including its constituent revisions and coverage.

**F-05 / epistemic honesty:** Do not infer learning, reward, goals, intention, understanding, danger/food, competence, efficacy or biological validity. An owner-published field may retain its exact owner-defined term with source attribution; UI-authored interpretation is disallowed.

**F-06 / links:** No join on timestamps, file paths, names, display geometry, arrival order or numerical coincidence. Identity/correlation requires a typed, source-asserted link.

**F-07 / no legacy:** No Symbiont contracts, aliases, payload compatibility or retrospective coercion, per UC-0001.

**F-08 / failures are data:** Loading, empty, denied, unavailable, unsupported, unknown, disconnected, stale, incomplete, gap and conflict are distinct. Never silently replace missing live delivery with cached data.

**F-09 / passive interactions:** No interactive control in v1 can issue an operator/causal command. Even buttons named “play”, “pause” and “reset” must explicitly indicate presentation scope.

## 4. Information architecture and URL strategy

### 4.1 Proposed routes

| Route concept | Screen | URL identity caveat |
|---|---|---|
| `/worlds` | Authorized World / run browser | Accessible discovery only if publication contract supports it |
| `/worlds/:worldRef/runs/:runRef` | Overview | `worldRef` and `runRef` are safely encoded scoped references, not arbitrary global IDs |
| `/worlds/:worldRef/runs/:runRef/spatial` | Spatial Explorer | Context includes run explicitly to prevent ambiguous spatial state |
| `/worlds/:worldRef/runs/:runRef/timeline` | Timeline | Shareable cut/range only when reference semantics are stable |
| `/worlds/:worldRef/runs/:runRef/trace` | Sensorimotor Trace | Selected correlation remains a query/filter, never fabricated identity |
| `/claims/:issuerRef/:claimRef` | Claim Inspector | Illustrative scoped route; exact encoding awaits approved contract |
| `/connection` | Connection & Access | No secrets or sensitive source details in URL |
| `/not-found` | Invalid route | Read-only recovery path |

The exact URLs are **design placeholders**; issuer/scope serialization and authorization behavior must be specified from actual Observation identity contracts. A deep link is not an authorization token.

### 4.2 Navigation tree — seven peer-level destinations

```text
Biopeia
├─ Worlds & Runs
├─ World Overview          [requires authorized context]
├─ Spatial Explorer        [requires compatible publication for 3D]
├─ Causal Timeline         [requires context; replay is conditional]
├─ Sensorimotor Trace      [requires explicit linked claims for graph]
├─ Claim Inspector         [requires an authorized claim reference]
└─ Connection & Access
```

All seven are shown at the same navigation level in desktop sidebar and narrow-screen navigation. Connection & Access additionally exposes a persistent connection-status shortcut in the header; this is a shortcut to the same screen, not an eighth screen. World Overview is the default landing destination **when** an authorized context is already resolved; otherwise land on Worlds & Runs. Never fabricate a default World, run, committed cut or camera subject.

No navigation item suggests a capability exists when its corresponding approved contract is missing. Disabled or unavailable destinations show a plain-language reason and the exact missing prerequisite; navigation is never entirely hidden from investigators unless access itself is restricted.

### 4.3 Landing and visual hierarchy

- First visit without authorized resolved context: **Worlds & Runs**, visually emphasizing discovery of an actual World; do not show a fabricated scene.
- With an authorized resolved context: **World Overview**, emphasizing the 3D/spatial panel if source projections support it, otherwise a precise unavailable/unsupported panel and access to published claims.
- Each scene object points back to typed source identity and the claim(s) supporting its visible data. Camera motion, framing, hover glow, lighting and background are presentation-only and must not suggest physical properties.
- Prominent spatial content never suppresses global warnings, partial/coherence labels, selected cut identity, or keyboard-accessible provenance.
- Switching themes or screens preserves compatible read-only context and does not submit mutation commands.

### 4.4 Global shell

- Brand/app identity and environment indicator; do not confuse current browser environment with source World state.
- Seven-item peer-level navigation with current location and breadcrumbs; no workspace grouping.
- Authorized World/run context selector, only when source permits enumeration; otherwise context shows **not supplied**.
- Source publication health: connected / reconnecting / disconnected / unknown, with last **delivered** time separately from latest **domain** time.
- Pinned global integrity banner when stale, gap, conflict, unsupported revision or permission failure affects the active view. It cannot be dismissed while relevant; it may be collapsed to a persistent compact form.
- Primary main region, optional contextual inspector drawer, keyboard skip link and toast/live-region used only for non-critical action feedback.
- Account/identity display only when approved access mechanism provides it; no implied account system.
- Cross-screen selected cut and display mode maintained in **ephemeral UI state**. URL parameters encode only stable, authorized references and non-sensitive filters. No secrets in URLs.

## 5. Common interaction patterns

### 5.1 Selected context and navigation

Changing World or run invalidates incompatible selected cut, subject, claim, timeline range and camera target; it must not silently carry unrelated identities. Preserve reversible UI filters when meaningful and show a context-change confirmation only if a visible investigation would be lost. Browser back/forward must restore coherent navigation state, not re-create science state.

### 5.2 Progressive disclosure

**Level A — glance:** readable summary, freshness, selected cut and what can be inspected. **Level B — investigate:** underlying domain cards, annotations, filtered timelines and explicit source links. **Level C — verify:** claim inspector with source metadata and raw representation only if permitted/redacted by source. Every summary value has a “view source claim(s)” affordance.

### 5.3 Presentation-time behavior

“Follow newest **delivered committed cut**” is the only suggested auto-follow mode if the source supports it. When the user selects an older cut, stop auto-follow and say **Viewing historical publication**. Replay buttons are labeled **Play recorded publications** / **Pause visual replay**; button tooltips and accessible names describe non-causal behavior. If no retained replay contract is available, hide replay transport and explain **History not available from this Observation source**.

### 5.4 Selection and comparison

One active selection at a time for v1; secondary “compare” is limited to two source claims or cuts **only if both are independently addressable and comparable under approved scopes**. No derived differences presented as scientific claims. Differences are UI calculations, explicitly labeled **display-only difference**, retaining inputs, units and revisions. Full arbitrary multi-run scientific comparison is not part of v1.

### 5.5 Error recovery

Offer read-only **Retry query**, **Reconnect**, **Adjust time window**, **Return to Worlds**, **Inspect publication details** where supported. No failure state should recommend manipulating owner state or bypassing Observation. Retry limits and backoff are bounded; do not retry permission-denied or incompatible revision as though they were transient network errors.

## 6. Complete screen specifications

### S01 — Worlds & Runs (`/worlds`)

**Goal:** Find a published authorized context and understand its observable freshness before entering it.

**Layout:** Page title and source health; compact search/filter toolbar; responsive list/table of contexts; right-side or inline detail preview; persistent explanatory message for incomplete discovery.

**Fields (conditionally, if published):** issuer-scoped World identity, accessible run ID and explicitly asserted relation, study link if published, latest delivered committed cut reference, cut's domain time, last Observation delivery time, access scope, status and coverage. No fabricated run title or “currently running”.

**Actions:** Search exact IDs / names only where provided; filter availability/World; sort by an explicitly identified axis; refresh Observation read; open overview; inspect known claim. Search capability is conditional on provider contract and may be client filtering of authorized returned set only, not global lookup.

**States:** initial loading; no authorized publications; query returned zero results; source unreachable; cached stale results with banner; partial discovery; unsupported family/revision; access denied; populated. Distinguish `no authorized worlds` from `no runs returned for this World`.

**Acceptance:** each row's displayed identity has a source ref; no unauthorized rows; refresh produces reads only; sorting by delivery does not claim newest causal cut; zero results does not imply nonexistent World.

### S02 — World Run Overview (`/worlds/:worldRef/runs/:runRef`)

**Goal:** Answer what is *authoritatively visible* about the selected context and cut, and whether its pieces cohere.

**Layout:** (a) context and cut strip; (b) integrity/status line; (c) large spatial preview or grounded unsupported state; (d) domain summary cards; (e) recent cut/activity mini-timeline; (f) trace/association summary; (g) collapsible provenance drawer. Desktop should give the grounded spatial view primary emphasis (roughly 2/3) and supporting panels the remaining area; mobile stacks context, integrity, summary, spatial, history.

**Components:** World ID; run relation status; selected committed cut; per-domain cards for Organism, Embodiment, Environment and other authorized projections as present (never invent a state for Modality); source-specific unit/time; source coverage and availability; cut coherence label; source link on every card.

**Interactions:** Select published cut; open spatial; move to timeline or trace; select published body/subject; inspect card claim; copy *safe* scoped reference (not secrets); toggle between summary and provenance without changing domain state.

**Invariants:** a missing Organism claim becomes `not published in selected scope`, not “organism absent”; an owner card with different revision is clearly **not co-committed** unless World-cut contract says otherwise; an unasserted Presence/Body relation is `unresolved`.

**Acceptance:** user can trace any numeric datum and cut status; composite view identifies its revision constituents; nothing implies continuous execution from delivery cadence.

### S03 — Spatial Explorer (`/worlds/:worldRef/runs/:runRef/spatial`)

**Goal:** Inspect physically published state with no simulated details.

**Layout:** substantial canvas (or semantic table if no WebGL), source/cut bar above, layer/subject navigator left, selected-object provenance card right, keyboard-accessible camera controls and fallback toggle below; narrow view uses a modal/drawer list with stable accessible focus.

**Render rules:** render only declared geometry, pose, transform, coordinate frame, scale/unit, subject, morphology/environment revision and their compatible links. A projected shape is tagged as **schematic** where appropriate; `not published` objects are not drawn. Spatial occlusion must never be confused with nonexistence. Receptor rays, terrain, force arrows, contact points and action trajectories appear only if their owner claims explicitly support those elements. Geometric axes are labeled with frame and units. No invented anatomical or environmental mesh.

**Camera:** orbit, pan, zoom, reset; focus on source-identified subject; preset front/side/top views where frame semantics permit; scale legend; zoom min/max and clipping safety. Keyboard and single-pointer alternatives to every drag gesture; reset works under reduced motion. Selected WebGL object must be mapped via explicit validated source reference; scene graph key is never an identity.

**Temporal control:** selected committed cut controls which published pose is shown. No default interpolation. If interpolation is ever approved, source endpoints and **presentation interpolation** overlay are mandatory; not part of v1 acceptance.

**Fallback:** structured list/table exposes every selected rendered subject, pose component, declared unit/frame, revision, availability and source reference. Text mode is an equal route, not a last-resort error screen.

**States:** compatible 3D; WebGL2 unavailable; GPU context lost; no spatial publication; incompatible coordinate frame; missing geometry; unsupported semantic revision; partially available scene; stale/old cut; conflicting source. None may silently approximate source data.

**Acceptance:** source claim→scene object→inspector round-trip; mapping respects frame and unit; no GPU mode contains equivalent epistemic metadata; unlinked geometry is not attached heuristically to a body; GPU resource disposal on navigation.

### S04 — Causal Timeline & Publication Replay (`/worlds/:worldRef/runs/:runRef/timeline`)

**Goal:** Navigate publication history and recognize what is and is not causally ordered.

**Layout:** chronology scope selector and time-axis legend, range control, dense accessible timeline, detail rail, integrity strip and replay controls when permitted.

**Lane classes:** committed World cuts; owner semantic claims; physical candidate/step status where published; Observation delivery/duplication/gap; lifecycle publications. A rejected candidate must have an unmistakably distinct shape and textual label from a committed cut.

**Axis rules:** World cut order only within contract's declared scope; per-domain time shown separately; delivery time auxiliary. Different order scopes are displayed in different tracks or with explicit `not globally ordered` legend. Reordering by wall clock must never be visually presented as a causal chain.

**Actions:** Select cut/claim; restrict to family/authority/typed subject; choose range with inputs as alternative to dragging; step across retained publications; replay visual selection at selectable display speed; pause on navigation/selected detail; open claim or trace. If the retention/query interface cannot guarantee full window coverage, show `partial history`.

**Gaps:** show delivery-sequence gaps only where actual sequence/resume semantics allow their detection. Indicate known range boundaries, duplicate delivery and reconnects without inferring source absence. A missing event outside guaranteed retention is `not available`, not `lost event`.

**Acceptance:** arrival order does not change committed ordering; disabled replay when not guaranteed; no control calls mutation endpoints; keyboard can move focus and select items; gaps remain visible after changing filters if they affect interpretation.

### S05 — Sensorimotor Trace (`/worlds/:worldRef/runs/:runRef/trace`)

**Goal:** Trace explicitly published relations from a source committed cut through the available sensory/action/physical/adoption path to a resulting committed cut, without promoting correlation to causation.

**Layout:** correlation or lineage search/filter, horizontal/vertical directed graph, node inspector, edge explanation table, `unlinked publications` panel and provenance drawer. On narrow screens use ordered accessible list of nodes/edges instead of an unscrollable graph.

**Node types (only if published):** committed source cut; receptor/transduction; Organism action or intention *as publisher-defined family, not interpreted UI claim*; Embodiment command/result; explicit owner adoption; resulting committed cut. Node omission means no supported published item in this selection, not biological non-operation.

**Edge policy:** every edge stores and shows source reference, relation type, declaring authority, identity scope, evidence ref and constraints. No edge for timestamp adjacency or matching labels. Correlation is labeled `correlated with` or approved term; `caused by` only where contract explicitly asserts causal relation. Unresolved and conflicting edges are separated, not drawn as regular edges.

**Actions:** expand/collapse supported branches; filter relation types; select node/edge; open supporting claims; toggle graph/table; copy safe reference. No inference-based graph completion.

**Acceptance:** deleting/withholding a correlation ref removes the edge even if timestamps match; empty path shows `no linked publication in available scope`; all graph relationships accessible in an equivalent edge table.

### S06 — Claim Inspector (`/claims/:issuerRef/:claimRef`)

**Goal:** Verify the exact semantics and delivery context for one claim; this is the truth-checking endpoint for other screens.

**Layout:** identifying heading and validity/status summary; tabbed or sectioned content with (1) Semantic claim, (2) Authority & subject, (3) Time/coherence, (4) Provenance/lineage, (5) Delivery/envelope, (6) Source limitations and guarded payload (only if approved). Prefer sections with anchor links rather than hiding critical facts in tabs.

**Canonical display fields (where applicable):** issuer and scoped claim ID; semantic family and revision; typed subject; asserted links; source semantic authority; producer/asserter; measurement source; epistemic basis; availability/completeness; domain time and revision; original value with declared precision/unit/frame; provenance and effective configuration; World-cut relation and coherent scope; delivery transport ID/sequence/duplicate/gap and collection/delivery times only as supplied.

**Formatter constraints:** default native unit/precision; optional human-friendly formatting must show exact original representation and whether rounding/conversion is display-only. Dangerous or active payload content is always treated as inert escaped text. A raw payload view requires approved source redaction, access policy, explicit user action and resource limits.

**Actions:** navigate asserted links; open related cut or subject in context; copy permitted references/value; view previous/next retained publication only where supported. No editing and no claim admission.

**Acceptance:** one click from any visible card/chip to the precise source claim; broken links result in a scoped unavailable message; claim payload and delivery envelope are visually and semantically distinct; epistemic basis is never collapsed into a single generic `valid` badge.

### S07 — Connection & Access (`/connection`)

**Goal:** Explain technical reachability and authorization without exposing secrets.

**Layout:** status card, configured source identity safe summary, authenticated principal if available, granted read scopes, last successful query/delivery, contract support summary, retry/backoff status, and categorized actionable errors.

**Indicators:** `Connected to source` is not `World running`; `Latest response received` is not `latest committed cut`; `Authenticated` is not `authorized for this World`.

**Actions:** retry permitted read; reconnect using approved mechanism; clear scoped ephemeral query cache; inspect availability constraints. Session end only if provided by approved auth integration. No arbitrary source URL or token field in production UI.

**States:** no configured source; checking; connected/no publications; connected/read denied; contract incompatible; disconnected/cached; reconnecting; authentication expired; rate limited; partial permissions.

**Acceptance:** no secrets in DOM/logs/URL; a denied query never falls back to prior privileged cached content; status label states its precise meaning; cache clearing avoids displaying old private data under a different principal.

## 7. Cross-screen UI components

| Component | Behavior and provenance rule | Accessibility |
|---|---|---|
| Context switcher | Scoped World/run selection; only approved discovered relationships | Searchable list, keyboard selection, no selection leakage |
| Integrity banner | Persistent description of stale/gap/unsupported/conflict/denied state | Text+icon, focusable details, restrained live announcements |
| Claim value | Value+native unit+source link+revision; never invented number | Text equivalent, full precision accessible |
| Source chip | Authority/producer label with exact provenance link | Identified by text, not color alone |
| Availability indicator | Distinct statuses; separate delivery from source | Textual status, accessible tooltip/details |
| Cut selector | Only committed cuts selectable as committed | Keyboard order, selection announced |
| Provenance drawer | Authority, origin, time, scope, links | Focus handling, Esc, restore focus |
| Temporal range control | Declared order scope and bounded range | Numeric/input alternative to dragging |
| Object selection | 3D picking maps to source subject reference | Synchronized subject table |
| Empty/error panel | Precise reason and read-only recovery action | Heading, clear error summary |
| Relation edge | Explicit assertion evidence required | Alternative edge list |
| Replay bar | Never calls World control | Clear label `visual replay` and reduced motion |

### 7.1 Shared view-state ontology

**Transport/access:** `not-configured`, `connecting`, `connected`, `reconnecting`, `disconnected`, `access-denied`, `auth-expired`.

**Query:** `idle`, `loading`, `success`, `empty-authorized-result`, `error`, `rate-limited`, `unsupported-contract`.

**Publication integrity:** `freshness-unknown`, `current-as-of-delivery`, `stale-cache`, `partial`, `known-gap`, `duplicate-delivery`, `conflict`, `unavailable`, `unknown-source-state`.

**Scientific state:** `committed-cut`, `candidate`, `rejected`, `unresolved-association`, `asserted-association`, `conflicting-association`, `best-available-composite`.

These are **frontend labels/conceptual UX states**, not Observation wire enum definitions. Mapping must be from approved source contracts, may require more than one concurrent state, and must not collapse orthogonal axes into one “health” color. Freshness thresholds cannot be guessed: without approved source timing expectations display `last delivered at …; freshness not guaranteed`.

### 7.2 Status copy examples

- “Last delivered at 09:42; source freshness not guaranteed.”
- “Viewing a retained publication; this is not a running simulation.”
- “Two claims have different owner revisions. This is a best-available composite, not a coherent World snapshot.”
- “No correlation is published between these events.”
- “WebGL is unavailable. The same published attributes are accessible in table view.”
- “The selected claim is outside your authorized scope.”
- “Delivery gap detected in this source-defined sequence. The source event's existence is unknown.”

All times, values and references in these strings are **illustrative copy examples only**, never sample scientific data for production.

## 8. Wireframe-level layouts

### 8.1 Desktop Overview (concept; not implementation)

```text
┌ BIOPEIA ─ Worlds & Runs · World Overview · Spatial Explorer · ...       ┐
│ World [authorized selector]  Run [authorized selector]   Cut [selected]   │
│ INTEGRITY: committed source cut / [coverage] / [delivery freshness]       │
├──────────────────────────────────────┬────────────────────────────────────┤
│                                      │ ORGANISM  published claims / scope │
│    SPATIAL VIEW or PRECISE           │ EMBODIMENT published claims / ... │
│    UNSUPPORTED STATE                 │ ENVIRONMENT published claims / ...│
│                                      │ [Each value → exact source claim]  │
├──────────────────────────────────────┴────────────────────────────────────┤
│ RECENT COMMITTED CUTS / OWNER CLAIMS / DELIVERY TRACK                    │
├─────────────────────────────────────────────┬─────────────────────────────┤
│ CORRELATED TRACE SUMMARY                    │ PROVENANCE / LIMITATIONS    │
└─────────────────────────────────────────────┴─────────────────────────────┘
```

### 8.2 Spatial desktop

```text
┌ Context / Cut / Frame / Units / Source status ────────────────────────────┐
│ Subjects & Layers │  3D or semantic table │  Selected subject            │
│ (published only)  │  axes / scale /       │  source claim / revision     │
│                   │  presentation camera  │  provenance / availability   │
│                   │  controls             │  relation status            │
└───────────────────┴───────────────────────┴──────────────────────────────┘
```

### 8.3 Narrow view pattern

Stacked header and sticky status line; primary content first; navigation via labeled menu; drill-down subject/claim panels as full-height dialogs with keyboard focus; text/table alternatives prioritized over forcing pan/zoom on a tiny canvas. No hidden essential metadata behind hover-only affordances.

## 9. End-to-end user journeys

### UC-01 — Locate a run and open a coherent cut

**Given** an authorized Observation source provides discovery and committed cut references; **when** the user opens Worlds & Runs, chooses a World and explicit run relation, **then** Overview displays selected source context with committed cut identity, authoritative time and coverage. **Alternative:** discovery contract absent → show scope limitation rather than an empty global Worlds database.

### UC-02 — Check whether current delivery is stale

**Given** a previously successful response and later connectivity failure; **when** the user returns to Overview, **then** cached data is labeled stale with its original domain revision and last delivery time. No claim of current execution is made. **Recovery:** user retries authorized read; cache must not cross principal/scope changes.

### UC-03 — Inspect body position in 3D

**Given** published pose, geometry and a compatible explicit coordinate frame; **when** user selects a body, **then** scene highlights a source-grounded subject and inspector shows pose provenance, revision and native units. **Alternative:** pose present but geometry/frame missing → no invented avatar; show specific missing field plus semantic table.

### UC-04 — Follow committed cuts historically

**Given** approved retained history; **when** user selects a range and presses visual replay, **then** UI advances through available publications with known gaps/bounds shown, never invoking World execution. **Alternative:** retention/replay guarantee absent → latest authorized view only.

### UC-05 — Investigate a sensorimotor chain

**Given** claims contain explicit source-cited relation edges; **when** user opens trace, **then** only documented links are drawn. Missing link is reported as unlinked by available evidence; no time-proximity edge appears.

### UC-06 — Audit a precise value

**Given** a value appears in a domain card or 3D metadata; **when** user follows its source link, **then** Claim Inspector retains source identity, semantic revision, time, unit/frame, authority and epistemic basis. Raw payload is unavailable unless explicitly permitted and redacted.

### UC-07 — Handle mismatched owner revisions

**Given** different owner claims at different revisions; **when** UI aggregates their display, **then** a best-available composite warning and revisions are visible. It never labels the aggregate as a committed atomic snapshot.

### UC-08 — Recover from an unsupported claim revision

**Given** an unknown semantic family/revision; **when** decoder rejects it, **then** the user sees `unsupported contract` tied to source family/revision, a safe link to Connection & Access, and no invented fallback interpretation.

### UC-09 — Inspect with keyboard / without WebGL

**Given** WebGL2 unavailable or keyboard-only usage; **when** user opens Spatial Explorer and navigates to a subject, **then** semantic table and provenance functions match the graphics mode, focus remains visible, and camera drag-only actions are not prerequisites.

### UC-10 — Test access separation

**Given** a principal can access World A but not B; **when** selecting/opening a B URL, **then** service denies B and UI exposes neither B claims nor old privileged cached data. A direct URL does not authorize access.

### UC-11 — Recognize delivery gaps and duplicates

**Given** source contract supports sequence semantics and a gap/duplicate arrives; **when** timeline shows those deliveries, **then** integrity lane displays the exact source-defined condition while domain causal order remains unchanged.

### UC-12 — Navigate from 3D to source claim and back

**Given** a rendered subject has a source-backed identifier; **when** selected and its claim inspected, **then** user can return to selected World/run/cut with the same identity and a consistent view (unless access/source state changed).

### UC-13 — Empty but authorized publication

**Given** permitted discovery query has no returned runs; **when** Results load, **then** UI says `no runs returned in authorized scope`, not `no World exists` and not `disconnected`.

### UC-14 — No cross-domain relation

**Given** Organism and Embodiment claims lack an authoritative link; **when** both are visible in Overview or Trace, **then** no combined organism-body identity is invented; each is inspectable separately and association status remains unresolved.

### UC-15 — Responsive/mobile scientific inspection

**Given** narrow screen, text zoom and reduced-motion setting; **when** user opens any screen, **then** controls, data, warnings and provenance are reachable without horizontal clipping of essential text or motion dependence.

## 10. Visual language and design system proposal (requires separate ratification)

### 10.1 Direction

**Immersive spatial scientific environment**, not a game HUD. The primary composition is a generous 3D/world viewport grounded exclusively in published compatible state, with contextual overlays/panels that do not obscure provenance or availability. Visual hierarchy: **source integrity and context always visible → observed spatial World state → selective inspection → full evidence**. Spatial prominence must never imply completeness, animation continuity, agency or scientific validity. On unsupported spatial data, preserve the intended visual hierarchy with a clear availability panel and source-backed textual/table alternatives; never fill with fictional models. Biopeia brand identity may be used once its brand assets and usage rules are established; do not copy Symbiont visual tokens. Light and dark designs are coequal deliverables.

### 10.2 Proposed design-token families (names, not ratified values)

- Foundation: `color.bg`, `color.surface`, `color.text`, `color.text-muted`, `color.border`, `color.focus`, `color.accent`.
- Semantic: `status.committed`, `status.candidate`, `status.rejected`, `status.partial`, `status.stale`, `status.conflict`, `status.unavailable`, `status.unknown`, `status.denied`; always icon+word as well as color.
- Layout: 4/8-point spacing rhythm; compact/regular density; clear breakpoints based on content rather than device labels; tables with responsive column control and non-truncated IDs accessible in details.
- Typography: readable UI family, technical identifiers in monospaced text, tabular numerals for aligned values, sufficiently strong hierarchy for warnings.
- Accessibility: focus outline, hit area target, zoom/reflow, reduced motion, non-flashing status, high contrast and text equivalents.
- Spatial: source geometry vs schematic representation, selected object, unverified/incomplete projection, frame axes, unit labels, clipping notice and source overlay.

Exact color hex codes, typefaces, responsive breakpoints, branded logo treatment and component skins require visual review. Never rely on green/red alone to distinguish committed and rejected.

### 10.3 Required light and dark themes

Both accessible **light and dark themes are in v1 scope**. Each must receive independent WCAG 2.2 AA contrast, focus, icon, chart, 3D annotation, disabled-state, stale/conflict and reduced-motion tests. Follow the system preference on first use, provide an explicit reversible toggle, and avoid flashes of an unintended theme on initial render. Persist only a harmless theme preference if security policy permits; never persist claim data, session secrets or sensitive access metadata. Missing theme test evidence blocks visual-system sign-off.

### 10.4 Internationalization

Ship the v1 interface in **English only**. Structure all user-facing copy for subsequent localization; **Spanish translation is deferred** and does not block v1 acceptance. Scientific terms and family IDs must preserve exact canonical spelling; translated explanatory labels must not silently alter domain meaning. Locale formatting cannot change the original value or time axis.

## 11. Accessibility requirements and tests

Target **WCAG 2.2 AA**. In particular ensure accessible focus visibility and no overlay obscuring focus, single-pointer alternatives to dragging, adequate target size/spacing, and accessible authentication where authentication is selected. W3C references: https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/ and https://www.w3.org/TR/WCAG22/.

- Every route has page heading, landmark hierarchy, informative title and skip navigation.
- All drawers/dialogs trap focus only where modal, restore focus on close and remain operable at 200%/400% zoom as relevant.
- Keyboard controls exist for camera operations, graph inspection and timeline range changes; graph/table and spatial/table representations contain equivalent claims and links.
- Text status plus meaningful icon; accessible names include axis/authority/time where relevant.
- High-frequency updates are announced only as user-controlled summaries and never steal focus.
- Motion reduced when OS preference requests it; visual replay defaults paused and is user-started.
- Distinguish lack of accessible projection from a disability-related UI failure: fallback can be used by everyone, not only when WebGL fails.
- Test screen reader navigation, touch and keyboard separately with scenarios UC-03/04/05/09/15.

## 12. Data adapter, contract readiness and security

### 12.1 Required contract-discovery inventory before implementation

For each existing approved Observation contract, record: contract owner and approval reference; transport access path; authentication principal/scope; publisher/issuer identity; supported semantic families/revisions; type/subject identity; claim vs envelope identity; availability/epistemic basis; revision/time and ordering scope; committed-cut relation/coherence; frame/units; correlation and provenance links; retention/query/replay semantics; sequence/gap semantics; limits and rate constraints; data classification and redaction; error semantics and compatibility policy.

This inventory is a **mapping task**, not authorization to invent fields, transports or fallback schema. `World`, `run`, `Presence`, `Body`, `Claim` references in this proposal remain conceptual until approved contract encodings are identified.

### 12.1.1 Current source-backed contract status (discovery snapshot)

This is a source inspection, not approval of an integration contract. The original discovery snapshot was checked against `biopeia/observation` `origin/main` at `1456df093e4ac28032d956e4df30957f0bf87cec` on 2026-10-13. The bounded post-commit producer path is separately evidenced by merged Observation #28 and World #105/#106; refresh exact revisions and obtain owner approval under Observation #37 before implementation. “Confirmed” means the bounded implementation/evidence exists; it does not mean a frontend-consumable API, query/access path, or replay contract is approved.

| Capability or family | Source evidence at pinned revision | Status for frontend | Permitted design use / limitation |
|---|---|---|---|
| Semantic claim model | `src/observation/semantic.py`; README describes a transport-independent model | CONFIRMED, in-process model | Preserve conceptual fields in UX; no wire encoding or browser decoder is established. |
| Bounded Observation plane | `src/observation/plane.py`; README documents current materialization, fan-out, in-memory replay and explicit rebase | CONFIRMED, one process/plane instance | May inform delivery-state concepts. No persistence, cross-restart resume, network, query service or UI path is established. |
| Environment finite scalar field mapping | `src/observation/environment.py`, family `biopeia.environment.finite-scalar-field` revision `1` | CONFIRMED mapping; PARTIAL publication readiness | Environment-owned scalar projection can be represented in the passive model. It is not a receptor signal and the adapter alone does not prove owner adoption or World commit. |
| Embodiment BodyPose mapping | `src/observation/embodiment.py`, family `embodiment.body_pose` revision `v1` | CONFIRMED mapping; PARTIAL publication readiness | Body/episode/morphology, frame, metric position and quaternion are validated by the mapper. The mapper explicitly does not prove a committed World cut. |
| Owner-authorized post-commit publication with World committed-cut verification | Production publication composition and committed-cut/owner-reference verification are implemented in the bounded paths recorded by Observation #26/#28 and World #105/#106; current exact revisions still require refresh under Observation #37 | CONFIRMED for the bounded producer-side path; not a browser/client contract | Do not label a claim committed unless the consumed publication carries the verified cut association; do not infer broader completeness, query or replay guarantees. |
| Environment → Embodiment receptor → Modality → Organism signal family | No stable family/record at this Observation revision was identified for the complete path | NOT ESTABLISHED | Do not design a live sensorimotor visualization as an available production capability. UX remains conceptual. |
| Historical `ObservedFrame` and `runtime_tick_events` | README explicitly identifies these as transitional/inherited, not stable Biopeia semantic-family contracts | EXCLUDED | Must not be used as a frontend integration contract or compatibility fallback. |
| Browser-accessible delivery, authentication, query, replay across restart | The bounded producer-side publication path does not supply a browser/network/query/auth contract; the plane remains in-process and in-memory at the pinned discovery revision | NOT SUPPORTED / NOT APPROVED | No endpoint, auth model, URL, token, durable replay or cross-process behavior may be invented here. |

The current source therefore supports design discovery and bounded in-process mappings, but **does not establish an end-to-end frontend-readable Observation contract**. The contract-to-screen map below is intentionally a readiness matrix, not an API specification.

| Screen | Source-backed capability required | Current readiness | Safe behavior before contract exists |
|---|---|---|---|
| Worlds & Runs | Authorized context discovery and identifiers | NOT ESTABLISHED | Show a documented unavailable/setup state in prototype only; no fabricated run list in production. |
| World Overview | World-verified committed cut plus compatible owner projections, and a separately approved client read/access path | PARTIAL — bounded producer-side publication exists; frontend consumer/access contract is not established | Show unsupported/unavailable status until an approved client path exists; owner projections alone cannot imply a committed World. |
| Spatial Explorer | Compatible geometry/pose families, frame and scale linked to a verified cut | PARTIAL inputs only | Show claims/table if an approved source path exists; otherwise no scene. |
| Causal Timeline | Stable committed-cut identity/order plus delivery ordering | PARTIAL in-process delivery sequence only | Keep causal order and delivery order separate; no cross-process timeline claim. |
| Sensorimotor Trace | Explicitly asserted action/signal correlation and lineage | NOT ESTABLISHED | Display no inferred edges; no claim that action caused sensory change. |
| Claim Inspector | Approved family and source claim references accessible to client | PARTIAL model only | Design information hierarchy; do not claim browser access or stable public envelope. |
| Connection & Access | Approved client delivery and authentication/authorization contract | NOT ESTABLISHED | Explain that source access design is pending; never collect or persist credentials in a mock. |

### 12.1.2 Context prerequisites and no-context behavior

Every screen remains reachable without a selected World/run/claim. Opening a destination must not fabricate a default context or scene. The following table defines the truthful behavior for absent context; copy is illustrative and requires content review.

| Screen | Missing context | Display | Permitted next action | Prohibited implication/action |
|---|---|---|---|---|
| Worlds & Runs | No authorized source or no discoverable contexts | Distinguish “source not configured”, “no accessible contexts returned”, and “discovery unavailable” only if the source contract distinguishes them | Open Connection & Access; retry a permitted read | Do not show sample or synthetic runs as real. |
| World Overview | No selected World/run/cut | “Select an authorized context to view published state”; no scene | Navigate to Worlds & Runs | Do not call it an empty World or infer absence. |
| Spatial Explorer | No compatible geometry/pose claim or no selected cut | State which prerequisite is missing/unsupported; provide semantic list only when source data exists | Select a published context or open Claim Inspector | Do not render stock geometry, axes, body silhouettes or motion. |
| Causal Timeline | No selected World/run or no committed-cut contract | Explain that a context or causal-order contract is required | Select context; inspect Connection & Access | Do not substitute delivery sequence or wall-clock timestamps as causal ordering. |
| Sensorimotor Trace | No selected subject/cut or no explicit correlation claim | Explain that no source-asserted relation is available in this context | Select a source-backed claim/context | Do not draw inferred edges or imply failed sensing. |
| Claim Inspector | No claim selected/linked | Prompt to select a published claim; metadata fields remain absent, not blank-valued | Return to source-backed list or follow an authorized link | Do not create placeholder claims or use guessed IDs. |
| Connection & Access | No endpoint/principal configured | State configuration/access prerequisite without exposing secret fields | Read-only setup guidance approved by deployment policy | Do not imply authenticated/authorized state or ask for secrets in an unapproved client. |

### 12.1.3 Design review and implementation acceptance are separate gates

**Design Review Complete** is a documentation-only milestone. It may be reached when the seven-screen information architecture is consistent; all screen and no-context states are specified; visual concepts are clearly synthetic; the contract readiness matrix records exact source evidence and unsupported areas; accessibility, security and performance questions are bounded; and required independent/design/constitutional reviews are recorded. It does not require executable code, a working endpoint, or implementation authorization. Unresolved constitutional allocation and unavailable Observation paths remain explicit blockers to implementation.

**Implementation Acceptance** is a separate later gate. It requires competent authorization for the frontend boundary, approved client-consumable Observation contracts and access model, a real World-verified publication path, exact-revision integration evidence, acceptance tests for all implemented states, security/accessibility/performance validation, and independent review where risk policy requires it. A design review cannot satisfy this gate; green CI cannot create missing contracts or authority.

### 12.2 Adapter rules

A boundary validator rejects unknown revisions; a mapping step keeps source references immutable; feature gating checks required semantics; an isolated UI view model maps into clearly labeled display states; cache is keyed by principal, authorization scope, source identity, contract revision and selected context where feasible. Avoid leakage on login change. No client-side join upgrades epistemic authority. No direct domain-package imports or owner checkpoint reads.

### 12.3 Security model and threat cases

Review source access and data classification before deployment. Require HTTPS, approved server-enforced authorization, robust content security policy, escaped text (no injected HTML), safe cross-link protocols, bounded payload decoding, resource limits for graphs/meshes, no secret-bearing URLs or browser persistence, dependency audits and explicit session revocation/cache clearing. Consider phishing through source-provided labels, deep-link identifiers, malicious oversized claim, denial-of-service via pathological mesh, cross-principal cache pollution and unsupported schema confusion.

No BFF, new database, broker, auth provider, vendor or additional Observation transport is selected here. A required infrastructure component must receive its own independent design and approval.

## 13. Performance and observability — measurement plan

Proposed **test budgets** must be approved and benchmarked, not represented as achieved results:

| Area | Proposed initial acceptance budget or measurement |
|---|---|
| Initial shell | Interactive/navigation shell in ≤ 2 s on agreed reference desktop with local/controlled source; exclude network waiting but display loading state promptly |
| User input | Selection/filter feedback within 100 ms where local; network-dependent completion explicitly marked asynchronous |
| 3D rendering | Aim for ≥ 30 fps for agreed reference geometry; fallback remains functional regardless of GPU |
| Memory | Define max in-memory claim window and scene object budget from real sample sizes; no unbounded growth during replay |
| Timelines | Virtualize large result sets; verify responsiveness on reference retained-history scale from actual Observation data |
| Reconnect | Bounded backoff with visible status; no silent resend of causal commands (none exist) |
| Resource lifecycle | Dispose GPU buffers/textures/listeners on context change and unmount; test context loss |

Do not set numeric max claim count, model triangle count, retention limit or update frequency until actual data volumes and target hardware are measured. Keep performance telemetry about the **frontend itself**, separate from scientific Observation semantics and without exporting sensitive values by default.

## 14. Test strategy and evidence

### 14.1 Test layers

- Pure contract validator tests against real approved family/revision examples and negative cases.
- View-model property tests preserving identity, unit, authority, time, epistemic basis, gap and coherence; deliberately mismatch identities/revisions.
- UI state matrix for all seven screens: loading, empty, populated, denied, unavailable, partial, conflict, gap, stale, disconnected and unsupported (where relevant).
- Browser integration with keyboard/screen reader expectations, 3D fallback, responsive/zoom/reduced motion, route deep links and error recovery.
- Security injection and isolation tests including cross-principal cache.
- Real TARGET end-to-end acceptance: exact pinned revisions, approved principal/scope, committed World cut, actual Observation publication path, UI claim/cut links, negative cases and explicit limits.

### 14.2 Fixtures policy

Controlled fixtures are valid for **unit/component/UX negative tests** and storybook-like design verification if clearly labeled as synthetic and isolated from production mode. They must never be used to manufacture **final scientific or migration acceptance evidence**. No demo placeholder records in production mode. For E2E acceptance the observed publication originates from the authorized live/retained TARGET path.

### 14.3 Traceable acceptance IDs

- `FE-ACC-001` Passive Observation-only reads and no causal mutation endpoints.
- `FE-ACC-002` Source claim identity/authority/provenance survives every view-model layer.
- `FE-ACC-003` Commit label only for actual World-committed cut.
- `FE-ACC-004` Time axes and owner revisions remain distinguishable.
- `FE-ACC-005` Gap/disconnect/stale/partial/conflict/unsupported are not collapsed.
- `FE-ACC-006` No inference-based identity or correlation joins.
- `FE-ACC-007` Spatial view and text fallback preserve claims/metadata.
- `FE-ACC-008` Replay is presentation-only and conditional on actual replay guarantee.
- `FE-ACC-009` All core routes satisfy WCAG 2.2 AA test plan.
- `FE-ACC-010` Deep-link authorization enforced and caches principal-scoped.
- `FE-ACC-011` Unsupported revision fails safely and visibly.
- `FE-ACC-012` Real TARGET publication reaches Frontend without artificial joins.
- `FE-ACC-013` All visible summary values link to original authorized claim(s).
- `FE-ACC-014` Performance and disposal meet approved device/data benchmark budgets.
- `FE-ACC-015` Lab remains evidence owner; displayed values never acquire scientific admission status.

## 15. Delivery plan and issue decomposition

### Phase 0A — Constitutional and semantic prerequisites (blocking)

- **FE-GOV-01** ADR: reconcile ADR-0102 Workbench/UI allocation, assign separate frontend presentation application, preserve Lab authority.
- **FE-GOV-02** Re-scope Lab #63 as actual Lab scientific requirement and move presentation acceptance to frontend tracker; no loss of existing work.
- **FE-CON-01** Observation interface inventory with exact source owner, approved family/revision/transport, scope and negative semantics.
- **FE-SEC-01** Auth, data classification and deployment threat-model decision (local development vs production).
- **FE-UX-01** Approve information architecture, visual-system specification and screen states.

### Phase 0B — Design validation (non-causal, no runtime implementation authorization)

- **FE-UX-02** Low/high-fidelity wireframes for seven screens, desktop/narrow and populated/error/stale variants.
- **FE-UX-03** Usability walkthrough: UC-01, UC-03, UC-05, UC-06, UC-09; document confusing labels.
- **FE-UX-04** Accessibility test plan and design-token contrast review.
- **FE-ARCH-01** UI read adapter mapping proposal from discovered real contracts (no invented transport/schema).

### Phase 1 — Shell and authorized discovery (requires implementation authorization)

- **FE-IMP-01** Independent repo/CI and locked toolchain.
- **FE-IMP-02** Shell/router/context/connection, readonly authenticated integration.
- **FE-IMP-03** Strict contract decoder, source provenance representation and permission-scoped cache.
- **FE-IMP-04** Worlds & Runs with truthful empty/gap/access states.

### Phase 2 — Verifiable inspection

- **FE-IMP-05** Claim Inspector and source-link journeys.
- **FE-IMP-06** World Overview and per-owner cards/coherence labels.
- **FE-IMP-07** Timeline and replay only to supported Observation retention contract.

### Phase 3 — Spatial and trace

- **FE-IMP-08** 3D and semantic fallback under approved spatial contracts.
- **FE-IMP-09** Sensorimotor trace graph plus accessible edge table, only sourced asserted links.

### Phase 4 — independent acceptance and release

- **FE-VAL-01** Accessibility and security verification.
- **FE-VAL-02** Actual device/data performance profiling with approved budgets.
- **FE-VAL-03** TARGET real publication E2E with negative cases and documented limitations.
- **FE-REL-01** Operational owner/runbook/release decisions and rollout after production security authorization.

Issues should have parent links, owning repository, governance class, explicit blocking relationship, phase, priority, definition-of-done and evidence reference in Biopeia Project. Do not create duplicate canonical scientific records in frontend.

## 16. Decision register for ratification

| ID | Decision | Recommendation | Blocking |
|---|---|---|---|
| D-01 | ADR-0102 vs standalone frontend | Derived constitutional ADR, explicitly remove or narrow Lab Workbench/UI allocation | Yes |
| D-02 | Final repository | `biopeia/frontend`; presentation owner and independent release | Yes |
| D-03 | Observation interfaces | Adopt only actual approved contracts after inventory | Yes |
| D-04 | Source/discovery/replay availability | Feature-gate per real contract; never invent source semantics | Yes for applicable feature |
| D-05 | Auth/scope/data classification | Separate reviewed local and production models | Yes for production |
| D-06 | Visual system | Owner direction adopted: immersive spatial-first scientific environment, subject to token and accessibility approval | Yes before component styling |
| D-07 | Copy/language | Owner direction adopted: English-only v1; localization-ready; Spanish in subsequent scope | No for architecture |
| D-08 | Light/dark themes | Owner direction adopted: both required and independently tested in v1 | Yes for visual acceptance |
| D-09 | Replay/saved views/export | Replay conditional; saved views and export excluded by default | Replay contract blocks replay only |
| D-10 | Performance budgets | Approve test data, hardware and thresholds before release | Yes for release |
| D-11 | App-level run launch | Excluded in v1; future control-authority proposal | No (explicitly excluded) |
| D-12 | Full comparative analytics | Deferred; display-only two-source comparison conditional | No |
| D-13 | Top-level information architecture | Owner direction adopted: seven peer-level screens; no three-workspace grouping | Yes for UX sign-off |
| D-14 | First-use hierarchy | Owner direction adopted: spatial/World-first with permanent source health and provenance access; fallback truthful | Yes for UX sign-off |

## 17. Definition of ready for implementation

All checked: constitutional decision accepted; frontend repo owner named; Observation contract inventory signed off; every first-phase feature has real supported source path; threat model and access decision completed for target environment; UX screen/wireframe state catalogue accepted; visual tokens and accessibility review approved; acceptance tests mapped to issues; integration plan does not bypass World→Observation; no conflict with UC-0001. Until then, design/UX discovery may proceed but causal integration and production implementation are not authorized by this proposal.

## 18. Definition of done for frontend v1

Seven defined screens available to the extent the approved source contracts support their functions; unsupported abilities have accurate states and no simulated proof. Navigation, keyboard and non-3D views remain useful; every datum is traceable; selected cut semantics and delivery state are correct; security and accessibility checks pass; actual TARGET publication is rendered through approved Observation boundary; repository revisions, limits and non-proven scientific claims are documented. Migration's separate causal-cycle acceptance remains independent.

## 19. References

- Parent: [Biopeia Frontend v1 — Independent Visualization Application](biopeia-frontend-v1.md).
- ADR-0078: Observation causally passive.
- ADR-0100: Observation and evidence custody.
- ADR-0101: Operator Control.
- ADR-0102: Lab (allocation conflict to reconcile).
- Docs #164: https://github.com/biopeia/docs/issues/164
- Lab #63: https://github.com/biopeia/lab/issues/63
- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- W3C WCAG 2.2 new success criteria: https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/
