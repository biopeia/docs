---
id: design.cross-domain.biopeia-frontend-visual-design-v1
title: "Biopeia Frontend v1 — Visual Design Specification"
document_type: design
owner: biopeia-project-owner
created: 2026-10-13
language: en
document_version: 1
updated: 2026-10-13
parent_design: design.cross-domain.biopeia-frontend-v1
---

# Biopeia Frontend v1 — Visual Design Specification

> **Status:** Proposed visual direction, not ratified. This specification supports review of the product design; it does not resolve ADR-0102, approve Observation contracts, authorize a frontend repository or grant implementation authorization. The SVGs are static concept mockups with synthetic design content, not Biopeia observations or a running application.

## 1. Purpose and scope

This companion turns the product directions in the [functional and UX specification](biopeia-frontend-ux-spec-v1.md) into a concrete visual proposal for the two screens that establish the v1 visual language:

- **World Overview** — spatially led summary with source status and owner projections always visible.
- **Spatial Explorer** — dedicated spatial inspection surface with a truthful unavailable state when compatible published geometry is absent.

The proposal also defines a compact token palette, typography roles, responsive composition, interaction states and visual acceptance criteria. It is a design artifact only: no frontend component, asset pipeline, Observation model, renderer, or screen behavior is implemented here.

The seven screens remain equal peers in navigation. These first two receive design priority, not greater authority or navigation rank.

## 2. Visual design plan

### 2.1 Design principles

1. **Grounded immersion:** spatial content may dominate the canvas only when real compatible publications support it. Without them, the canvas remains a clear availability state, never a fabricated world.
2. **Quiet instrumentation:** precise source, cut, revision and delivery context is easy to find, but does not turn the whole application into a dense engineering console.
3. **Material, not game-like:** use layered surfaces, fine coordinate/grid motifs and restrained focus lighting. Avoid game HUDs, neon gradients, fictional target markers, decorative organism silhouettes and implied motion.
4. **Evidence before polish:** authority, coherence, availability and selected context stay visible when the user changes theme, viewport or screen.
5. **One strong focal point:** the spatial pane is the visual anchor; status strips and evidence panels use a disciplined typographic system.

### 2.2 Proposed color tokens

These are **candidate values for review**, not ratified Biopeia brand tokens. They are deliberately limited to a small neutral foundation, one teal accent and one amber caution color. Semantic states must always include text/icon; color alone never encodes meaning.

| Token | Light | Dark | Intended use |
|---|---|---|---|
| `canvas` | `#EDF1EE` | `#0E191B` | App background |
| `surface` | `#FBFCFA` | `#152427` | Main panels and cards |
| `surface-raised` | `#F3F6F3` | `#1B2D30` | Controls, inset cards, selected rows |
| `text-primary` | `#172D2D` | `#E5EFEC` | Headings and essential content |
| `text-secondary` | `#5D7370` | `#9EB3AE` | Supporting labels and metadata |
| `accent` | `#147A70` | `#72CABB` | Links, focus-adjacent emphasis, selected navigation |
| `caution` | `#82501F` | `#E0A45E` | Stale, unknown, disconnected or attention states with label/icon |
| `border` | `#D5DFDA` | `#304548` | Boundaries and dividers |

Normal-text contrast was checked for the proposed primary, secondary, accent and caution colors against their corresponding surface: all listed pairs exceed 4.5:1. This arithmetic check is not a WCAG conformance claim; final component states, icons, charts, focus and 3D annotations still require testing.

### 2.3 Typography and spacing

- **UI and prose:** system sans-serif stack, with an optional self-hosted humanist sans only after licensing and performance review. The mockups use `Inter` when available, then system UI fallback.
- **Identifiers and values:** system monospace; use tabular numerals for aligned quantities. Never truncate an identity without an accessible full-value route.
- **Hierarchy:** screen title 20–24 px; section heading 13–16 px; body 13–15 px; metadata 11–12 px; overline 10–11 px. Do not use tiny all-caps metadata for essential status.
- **Spacing:** 4 px base rhythm, favoring 8/12/16/24/32 px increments. Compact density is acceptable for source metadata only when text remains readable at 200% zoom.
- **Shape:** 8–12 px panel radii; thin borders; shadows used sparingly and never as the only layer distinction.

Exact typography packages, brand assets, CSS token names and responsive breakpoints remain subject to visual review and implementation authorization.

## 3. Screen composition

### 3.1 Shared shell

At desktop widths, use a stable left navigation rail, a compact global header, and a main content region. The seven peer-level navigation items appear as a single list; no Observatory/Inspector/Scientific Trace grouping is introduced. The header separates **source publication status** from the selected **World/run context**. A persistent warning is pinned above content when a material stale, gap, conflict, unsupported or access state affects the active view.

A context strip beneath the page title shows World, run, selected committed cut and delivery state in separate cells. Unknown or unavailable values use explicit words, not empty-looking dashes. `No source connected` in the mockups is a design-state example, not a claim that the production source is disconnected.

### 3.2 World Overview

Desktop composition uses a spatial panel as the main focal area, approximately 2/3 of the content width, with compact right-side publication, owner-projection and integrity panels. A publication history strip sits below both. This is a target layout only; the spatial panel may instead show an unavailable/unsupported state until actual contracts provide compatible geometry, frame, units and revisions.

The initial no-data design state must answer three questions without implying nonexistence:

- What is selected? (No authorized source/context, or the exact selected context if present.)
- What is missing? (No compatible spatial claim, source unavailable, access denied, etc., using the source-defined distinction.)
- What can the user do next? (Inspect available claims, retry an eligible read, or open Connection & Access.)

The state must not use “empty world”, “organism absent” or “nothing happened” unless a source claim explicitly supports that statement.

### 3.3 Spatial Explorer

The full spatial viewport is the primary surface, with a narrow context/action bar, clear frame/unit annotation only when supplied, and a selected-source detail pane. The layout includes a persistent non-WebGL path: a semantic list/table with the same available subject identities and provenance. Unsupported or missing geometry displays a centered explanation and links to available claims; it never substitutes a stock model.

Camera controls are visually secondary, keyboard accessible and presentation-only. Selected subject highlight may use a contour or border; do not use glow, scale change or animation in a way that implies physical force, salience or semantic importance. No interpolation or motion trail appears by default.

## 4. Static concept mockups

The included mockups show the two priority screens in light and dark themes:

- [World Overview — light and dark concept](assets/world-overview-visual-concepts.svg)
- [Spatial Explorer — light and dark concept](assets/spatial-explorer-visual-concepts.svg)

Each artboard is watermarked **SYNTHETIC DESIGN PREVIEW · NOT DATA**. All content in those illustrations is explanatory placeholder copy. The dashed abstract marks are decorative layout scaffolding and do not represent terrain, bodies, receptors, poses or environmental fields. The visible “not connected” and “unavailable” messages illustrate the truthful no-publication state, not current system status.

The diagrams are intentionally static. They do not imply an implemented frontend or approved spatial contract. Their purpose is to review hierarchy, density, theme treatment and empty-state behavior before components are authorized.

## 5. Component and state language

### 5.1 Shared components

- **Context strip:** World, run, committed cut and delivery state, each with distinct label and source context.
- **Publication badge:** icon + plain-language status + optional detail link. Never use green/red alone.
- **Owner projection card:** owner/domain label, source revision/time, availability, and source-claim affordance. No card is rendered as a composite authority.
- **Spatial availability panel:** source-backed state reason, supported alternatives and source link when available.
- **Provenance drawer:** claim identity, authority, epistemic basis, domain time/revision, unit/frame, coherence scope and lineage as provided by the source.
- **History lane:** cut ordering and delivery condition shown as distinct tracks; no inferred causal edge.

### 5.2 Interaction states

Every interactive control must have default, hover, keyboard-focus, pressed/selected, disabled and loading appearance. Screen-level states must include loading, populated, partial, stale, unsupported, unavailable, denied, disconnected, conflict and empty-result cases as relevant. Focus is never conveyed only by color; it uses a high-contrast 2 px outline with a visible offset. Reduced-motion preference disables decorative transition and camera animation.

Selection changes only the view. `Follow newest delivered committed cut` (if supported) and historical visual replay controls must state that they do not resume or re-execute a World. If no compatible time/replay contract exists, those controls are absent and a text explanation is shown.

## 6. Responsive and accessible behavior

- At wide desktop, keep navigation, spatial surface and provenance details simultaneously available without obscuring the source-status strip.
- At tablet width, allow the navigation rail to collapse to an accessible labeled menu; the selected context and integrity warning stay pinned.
- At narrow width, stack context, status, spatial/availability panel, owner projections and history. The source details open in a focus-managed drawer. Seven destinations remain individually reachable.
- At any size, a semantic table/list provides all values and source links without WebGL, pointer dragging or color perception.
- All content supports 200% zoom and reflow; no essential identity, warning, unit or provenance is hidden behind horizontal overflow.
- Spatial annotations use text and line/pattern differences in addition to hue. No flashing, rapid pulsing or auto-orbit.

Target remains WCAG 2.2 AA, with contrast and accessibility testing as specified in the UX companion. The proposed palette is not a substitute for testing rendered combinations, hover/focus states, charts or WebGL overlays.

## 7. Design acceptance checklist

This design may progress to review when all can be demonstrated in a later prototype (after implementation authorization):

1. Both themes preserve legibility and status distinctions without color-only meaning.
2. World Overview exposes selected context, publication health and source traceability before decorative content.
3. Spatial Explorer with no compatible source shows no body, terrain, pose, axis, receptor or resource as if real.
4. Every visible source-backed value can reach its source claim; no identity is generated from a scene node or display label.
5. The no-WebGL/keyboard path exposes the same available observations and provenance.
6. Responsive states preserve all seven destinations and every integrity warning.
7. Reduced motion and replay semantics never imply causal execution.
8. All mock data in design review remains visibly isolated from production mode.

These are design-review criteria, not evidence that an application exists or passes them.

## 8. Open review items

The following remain unresolved and are not decided by this companion:

- constitutional placement of a standalone frontend versus ADR-0102;
- actual Observation query/publication contracts and identity encodings;
- final Biopeia brand assets and whether the proposed palette is accepted;
- security model for local development versus multi-user deployment;
- numerical performance budgets based on representative real publication data;
- final responsive breakpoint values and typography licensing/package.

Resolve those through their competent design and architecture processes. Do not use a visual prototype to pre-empt them.

## References

- [Parent architecture/product design](biopeia-frontend-v1.md)
- [Functional, interaction and UX specification](biopeia-frontend-ux-spec-v1.md)
- [Docs #164 — Frontend design tracking](https://github.com/biopeia/docs/issues/164)
- [Docs #166 — Constitutional allocation decision](https://github.com/biopeia/docs/issues/166)
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
