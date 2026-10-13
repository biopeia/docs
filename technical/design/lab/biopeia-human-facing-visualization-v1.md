---
id: design.lab.biopeia-human-facing-visualization-v1
title: "Biopeia Human-Facing Visualization v1"
document_type: design
owner: biopeia-project-owner
created: 2026-10-13
language: en
document_version: 1
---

# Biopeia Human-Facing Visualization v1

**Lifecycle:** Proposed; not ratified. The design register is authoritative
for lifecycle and implementation status.  
**Scope:** Lab Workbench as a passive consumer of committed World projections
published through Observation.  
**Related implementation issue:** [Lab #63 — Render committed World
projections from Observation publications in Workbench](https://github.com/biopeia/lab/issues/63).  
**Design tracking issue:** [Docs #164](https://github.com/biopeia/docs/issues/164).  
**Implementation authorization:** Not granted by this proposal.

## 1. Purpose

Define a bounded human-facing visualization for inspecting a Biopeia run: its
committed causal progression, publicly observable Organism/Embodiment state,
relevant Environment state, and the observed consequences of interaction.
The first useful view should help an operator answer **what was published, by
which authority, for which subject and causal cut, and with what evidence or
limitations**. It must not imply that a displayed correlation proves learning
or that a visualization is the runtime itself.

The immediate use case is to see a Biopeia Organism embodied in a World and
follow the public sensory/action/physical/observation path where corresponding
TARGET publications exist. Missing implementation or missing claims must be
visible as a limitation, not filled with a fabricated value or legacy path.

This design is a presentation/application proposal. It does not choose a
concrete schema, API, transport, storage, renderer, frontend framework,
deployment topology, or scientific protocol.

## 2. Existing decisions that constrain this design

The following are constraints, not new decisions in this document:

- **Lab may own Workbench/UI.** ADR-0102 places Workbench/UI, operator
  tooling, studies, evidence/provenance tooling and analysis in Lab, while Lab
  does not own Organism cognition, Embodiment body truth, Environment truth,
  or World causality.
- **Observation is passive.** ADR-0078 permits visualization but prohibits
  Observation from modifying observed causal state. ADR-0100 separates the
  Observation capability from presentation and durable scientific evidence
  custody.
- **Operator control is separate.** ADR-0101 requires pause, step, resume,
  speed changes and interventions to be explicit attributable requests to
  the relevant authority. The observation/display path cannot issue them.
- **Authority and presentation are distinct.** The approved Observation
  Semantic Model v1 distinguishes authority, producer, semantic asserter,
  measurement source, transport and consumer. UI co-location does not transfer
  authority.
- **Claims are not global snapshots by default.** A World-cut-coherent view
  may be claimed only when included claims are linked to the same committed
  cut or explicitly compatible revisions. Composite displays preserve their
  individual times/revisions.
- **No legacy compatibility.** Historical Symbiont UI, endpoints, payloads,
  snapshots, identities and rendering assumptions are not TARGET contracts.

## 3. Proposed ownership and location

### 3.1 Recommendation

Keep the first human-facing viewer inside the **Lab Workbench application**;
do not create a new frontend repository for this bounded visualization.
This follows ADR-0102's existing Lab responsibility for Workbench/UI and keeps
the Lab application boundary explicit. Lab owns presentation and application
composition only; it is not thereby a World runtime or a domain authority.

The application reads through the TARGET Observation publication path. It
must not import private owner state or call owner internals to complete a
display. If Lab's current repository lacks the application surface, that is an
implementation gap under Lab #63, not permission to relocate the design into
the workspace or create an unapproved semantic owner.

### 3.2 Boundaries

```text
Organism / Embodiment / Environment / World
    own their respective authoritative meanings and state
                ↓ authorized projections/publications
Observation
    passive observation projection and delivery capability
                ↓ actual publications
Lab Workbench
    human-facing presentation and application composition
                ↓
Human viewer
```

The viewer is outside the causal path. Lab may separately host operator
controls or scientific apparatus, but those are out of scope for this
read-only visualization slice and must use explicit authorized paths.

## 4. First-release goals and non-goals

### Goals

1. Let a human select and inspect a run/World context without conflating
   `world_id`, presence, `organism_id`, `body_id`, episode, receptor, or
   observation identity.
2. Show a time-ordered view of committed World causal cuts and available
   owner projections.
3. Where explicit compatible spatial claims are available, present an
   inspectable spatial view of body/environment state. Without those claims,
   do not invent geometry or pose; show the available data and its limitation.
4. Expose public sensory inputs, Organism-originated action claims, physical
   outcomes and owner adoption/commit evidence only when those are actually
   published and authorized for presentation.
5. Make authority, subject, domain time/revision, provenance, availability and
   coherence inspectable alongside rendered values.
6. Support inspection of a bounded run's retained Observation history where
   the delivery contract actually supports it.

### Non-goals

- Starting, advancing, pausing, stepping, mutating or terminating a World.
- Creating interventions, experiment protocols or evidence admissions.
- Displaying private cognitive graph/state, hidden memory, internal weights or
  unexposed Organism state.
- Inferring goals, rewards, food/danger meaning, intent, learning, competence,
  efficacy, biological validity or causal attribution from a visual pattern.
- Reconstructing absent claims from domain internals, filenames, solver state,
  timestamps, positional indexes or legacy outputs.
- Requiring all claims to form one global atomic snapshot.
- Choosing a production renderer, 3D asset pipeline, concrete Observation
  family schema, wire/API contract, transport or storage technology.

## 5. Proposed information architecture

The following are conceptual view responsibilities. They do not prescribe a
pixel layout, styling system or specific frontend components.

### 5.1 Run and identity context

The view should display the declared run/World context and explicit identity
links available in the published claims. Cross-domain links must retain their
asserted, unresolved or conflicting status; a UI join must not upgrade an
unresolved association into identity fact.

### 5.2 Causal timeline

The timeline is ordered by the declared causal/delivery contract. It must
label World causal tick separately from Organism step, physics step/substep,
environment revision, embodiment episode/revision and host collection time.
Host wall time may aid navigation but is not causal ordering.

Only committed World cuts may be presented as committed. Candidate,
preparing, rejected or recovery-required results must never be rendered as
committed state. If the publication omits commit status or cut identity, the
viewer must not infer either from arrival order.

### 5.3 Spatial view

The design recommends a spatial canvas for body/world inspection when explicit
frame-bound pose and geometry claims exist. Every displayed geometry or pose
must remain traceable to its claim, semantic family/revision, frame, subject,
source authority and effective domain time/revision.

The renderer may use visual interpolation for readability only if it labels
interpolated content as presentation-derived and preserves source endpoints;
interpolation cannot be passed back into the causal system or presented as an
authoritative sampled state. In the absence of a compatible family/claim, the
spatial view reports unsupported/unavailable rather than manufacturing a
body, terrain, trajectory, or environment.

### 5.4 Signals and action sequence

When authorized claims exist, the viewer may display an ordered trace such
as:

```text
committed source cut
  → receptor/transduced signal publication
  → Organism public action/intention publication
  → Embodiment-bound command/result publication
  → owner adoption and committed World cut
```

This trace proves only that the linked claims were published with the stated
provenance and correlation. It does not prove that the Organism understood a
stimulus, learned a mapping, selected an action because of a stimulus, or
achieved a goal. Those require separate contracts/evidence.

### 5.5 Claim detail and provenance

Every rendered claim must provide an inspection path to the fields required
by its semantic family, including at minimum:

- semantic authority, producer and semantic asserter when distinguished;
- typed subject identity and any explicit cross-domain link;
- semantic family and revision;
- epistemic basis and availability/completeness state;
- domain time and structural revision relevant to interpretation;
- units and reference frame where applicable;
- provenance/lineage references where material;
- World cut/coherence link when a cut-coherent view is claimed.

The UI may format values for readability but may not silently convert units,
collapse epistemic categories, hide incompatible revisions or turn a
derived/estimated claim into authoritative state.

## 6. Missing, stale, partial and conflicting data

The viewer must distinguish at least:

- **No publication received** from **source says unavailable/no data**.
- **Unsupported family/capability** from **temporarily unavailable source**.
- **Partial coverage** from a complete view; identify the missing scope when
  the source contract makes it available.
- **Stale claim** from current claim, including the reference time/revision
  against which it is stale where declared.
- **Delivery gap or replay boundary** from a source-state transition.
- **Unresolved/conflicting identity linkage** from an established join.
- **Best-available composite** from World-cut-coherent snapshot.

The viewer must not treat an empty result, disconnected consumer, lost
delivery, absent capability or failed adapter as evidence that the source
state does not exist. It must preserve the difference between a source
availability condition and Observation delivery availability.

## 7. User interaction and control boundary

The first visualization slice is **read-only**. Selection, filtering,
navigation, playback of preserved observational history, camera/view control
and metadata inspection are presentation actions only. They do not mutate
World or domain state.

Operator controls and experimental interventions are explicitly excluded.
If later requested, they require a separately scoped design/Issue and must
issue attributable requests to the competent authority. They must not be
implemented as hidden callbacks from the observation stream or as writeback
from the viewer to Observation.

## 8. Minimum evidence path and acceptance

The implementation target is Lab #63, which already requires actual
owner-authorized committed-cut publications to reach the Workbench view
boundary. A conforming first slice should demonstrate:

1. Exact participating repository revisions and a reproducible run command.
2. A real committed World cut reaching Observation through the TARGET
   publication path and then reaching the Lab Workbench consumer; no test
   fixture fabricates the final publication.
3. Visible preservation of authority, identity, time/revision, availability,
   provenance and commit/coherence boundary for the claims actually present.
4. A negative case showing that an uncommitted/rejected result is not shown as
   committed.
5. A missing/gap or unsupported-data case that is not misrepresented as
   source absence.
6. Evidence that the display path cannot mutate causal state.
7. A report of what is and is not demonstrated; no claim of learning, efficacy
   or scientific interpretation based only on the visualization.

The precise family-specific evidence depends on the contracts and publications
that exist when Lab implements #63. This design does not authorize inventing
new claims or bypassing a missing family contract.

## 9. Affected domains and implementation responsibilities

| Domain/repository | Proposed responsibility | Required boundary |
| --- | --- | --- |
| `lab` | Workbench application, presentation, navigation and claim inspection | Consume published claims; no private-domain reads or causal authority |
| `observation` | Passive projection/delivery path and actual publication semantics | No UI ownership, causal writeback or evidence custody by virtue of delivery |
| `world` | Commit identity/status and causal cut links exposed under World contract | World owns causality/commit, not external environment or owner internals |
| `environment` | Environment-owned claims needed for a view | UI cannot infer geometry/resources from missing data |
| `embodiment` | Body/episode/morphology/part claims needed for a view | Stable identities, explicit frames/revisions; no positional identity |
| `organism` | Public Organism-originated signals/actions suitable for presentation | Private longitudinal cognition remains private unless deliberately exposed through an authorized boundary |
| `modality` | Relevant transduction context only where its contract requires it | Not a semantic authority; UI does not reinterpret transduced values |
| `docs` | Canonical cross-domain design and decision/impact traceability | Design status in registry; no implementation ownership |

This map is a proposal, not proof that every domain currently publishes the
listed claim families. Any missing required publication is an owner-domain
contract/implementation gap to be tracked by the competent repository, not
filled in Lab or in a frontend test fixture.

## 10. Decisions deliberately left open

The following choices require later design/implementation evidence and are
not frozen here:

- Exact semantic families and revisions for spatial geometry, body pose,
  sensory input, action/command, adoption and committed-cut status.
- Whether the Lab Workbench is hosted in-process, as a separate process, or
  served by another application boundary.
- Concrete connection, authentication/authorization and deployment model.
- Transport, replay/query interface, retention, rate/cadence and backpressure.
- Renderer/scene representation, rendering library and asset model.
- Supported run selection, multi-World browsing and replay controls.
- Whether any operator control is later in scope and which authority owns its
  authorization path.

These are not reasons to transfer UI ownership to Observation or to make the
workspace a semantic runtime. The initial implementation should use existing
approved contracts and keep this design's omissions visible.

## 11. Alternatives considered

### A. Lab Workbench as the initial frontend — recommended

Consistent with ADR-0102 and Lab #63. Lab owns the application and
presentation boundary; it consumes Observation and remains outside ordinary
causal runtime ownership.

### B. A new independent frontend repository — not selected for v1

This could be reconsidered if a real deployment/security/versioning need
demonstrates that the UI should ship independently. It adds another repository
and authority/ownership surface now, while ADR-0102 already assigns Workbench/UI
to Lab. This proposal does not prohibit a future owner decision to split it.

### C. Put the UI in Observation — rejected

Observation is a passive capability/plane, not the human-facing application
or authority. Its ability to visualize data does not make it the correct
application owner.

### D. Put the UI or orchestration in the workspace — rejected

The workspace is composition/tooling only and has no domain or application
authority. It may later pin revisions and launch components, but it must not
contain canonical presentation semantics or missing runtime joins.

## 12. Governance and next steps

This document is a proposed design. It does not amend ADR-0102, ADR-0101, the
Observation macro-architecture or the approved Semantic Model. It does not
authorize implementation, operator control, experiment execution, new
Observation schemas/families, a frontend repository, or deployment.

The review path is:

1. Review the proposal against the current Lab, Observation, World and domain
   contracts; preserve any disagreement and exact evidence.
2. The competent Architecture/Repository Owner accepts, narrows or rejects
   the proposal. If acceptance changes an existing authority boundary, use
   the applicable constitutional decision path; this document cannot do so.
3. Once accepted, Lab #63 may proceed only within its own acceptance criteria
   and existing contracts. Missing semantic families or owner publications
   become owner-specific Issues before their implementation.
4. Any visual build or interactive control proposal receives its own
   repository-owned specification, risk review and acceptance evidence.

## References

- [ADR-0078 — Observation is causally passive](../../adr/ADR-0078-observation-is-causally-passive.md)
- [ADR-0100 — Observation capability and evidence custody](../../adr/ADR-0100-observation-capability-and-evidence-custody.md)
- [ADR-0101 — Operator Control](../../adr/ADR-0101-operator-control.md)
- [ADR-0102 — Lab](../../adr/ADR-0102-lab.md)
- [Observation Architecture for Biopeia v1](../observation/observation-architecture-biopeia-v1.md)
- [Observation Semantic Model v1](../observability/observation-semantic-model-v1.md)
- [Lab #63 — Render committed World projections from Observation publications in Workbench](https://github.com/biopeia/lab/issues/63)
