# Observation Architecture for Biopeia v1

The state of this design is recorded in `registry/designs.yaml`, which is the
only authority for it. Section 7 records the decisions the Architecture Owner
took on its content. Nothing here says that the `observation` repository
implements it.

It is written new for Biopeia from three sources: the ratified decision
records, the approved
[Observation Semantic Model v1](../observability/observation-semantic-model-v1.md),
and the code of the `observation` repository at commit
`cb07ace206058719a9aa9df65e2eb1f837130ee9`. It replaces, without rewriting,
the earlier
[Observation Architecture v1 — Target Design](../observability/observation-architecture-target-design-v1.md),
which is kept as historical evidence.

## 1. What this design is for

The semantic model says what an observation *means*: who is the authority for
a claim, what it is about, at what time, with what lineage. It deliberately
does not say where observations are produced, who holds them while they are
live, who may consume them, and who keeps them as evidence. This design
proposes those assignments, and only those.

It does not define records, schemas, wire formats, transports, endpoints,
storage, or any semantic family. Those remain later steps, as the semantic
model states.

## 2. What is already decided

The following are ratified and are constraints on this design, not proposals
of it. Each is quoted or summarised from the record named.

- **Four semantic authorities.** Organism, Embodiment, Environment and World
  are distinct authorities and none owns another's private semantics
  ([ADR-0095](../../adr/ADR-0095-surviving-semantic-authorities.md)).
- **Observation is passive.** It "may read, project, transport, buffer,
  aggregate, visualize and record, but has no authority to modify observed
  causal state"
  ([ADR-0078](../../adr/ADR-0078-observation-is-causally-passive.md)).
- **Observation is a capability, not an authority.** It is a `PASSIVE CAPABILITY / BOUNDARY`,
  "not a semantic state authority". Three things are to
  be kept separate: runtime projection of authoritative state; transport and
  presentation, as application or infrastructure; and durable scientific
  evidence and provenance custody, which belongs to scientific apparatus and
  governance. "Observation can emit facts; Lab/scientific apparatus records
  durable evidence"
  ([ADR-0100](../../adr/ADR-0100-observation-capability-and-evidence-custody.md)).
- **Operator control is not observation.** Pause, step, resume, speed and
  inject are explicit attributable requests to the relevant causal authority
  and "must not mutate hidden state through Observation"
  ([ADR-0101](../../adr/ADR-0101-operator-control.md)).
- **Modality is not an authority.** It defines transduction, and any state it
  holds is assigned to Embodiment, Organism, Environment or to
  non-authoritative implementation
  ([ADR-0099](../../adr/ADR-0099-modality-contract-library.md)).
- **Organism private state is not read from outside.** Internal conditions
  are "exposed outward as Organism-emitted signals/actions, not obtained by
  another authority reading private internals", and observation projections
  "do not confer write or semantic ownership"
  ([ADR-0092](../../adr/ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md)).
- **Lab is apparatus.** It may capture evidence, analyse and present; it does
  not own Organism, World, Environment or Embodiment
  ([ADR-0102](../../adr/ADR-0102-lab.md)).
- **Dependency direction.** Observation "consumes passive projections/events
  without writeback"; a separate Observation repository is justified "if
  needed to prevent World↔Lab coupling"
  ([ADR-0110](../../adr/ADR-0110-repository-consequence-and-dependency-direction.md)).

The semantic model adds, as approved conceptual semantics, that each claim has
exactly one primary authority among those four, that Lab is an authority only
for meaning it creates, and that a snapshot may be called coherent with a
World causal cut only when every claim in it is linked to that cut.

## 3. What this design proposes

Each point below is new in this document. P2, P3 and P8 are marked
**Decided**: the Architecture Owner decided them first, in answer to three
questions this document posed. The remaining points were approved with the
design as a whole; section 7 records both.

### P1. Five roles, kept distinct

| Role | What it does | Who may hold it |
|---|---|---|
| Authority | Defines the meaning of a claim and holds the state behind it | Organism, Embodiment, Environment, World; Lab only for meaning Lab creates |
| Producer | Emits a claim through an intentional observation boundary | The authority itself, or a component acting under its contract |
| Observation plane | Holds live claims: current materialisation, fan-out, bounded replay | The Observation capability |
| Consumer | Reads claims for presentation, analysis or operation | Lab, tools, interfaces |
| Evidence custodian | Keeps durable scientific evidence and its provenance | Lab and scientific apparatus |

One component may hold more than one role. Holding a role never transfers
another: producing, hosting, transporting or recording a claim does not make
its holder the authority for it.

### P2. The plane belongs to the Observation capability, not to Lab

**Decided.** The live plane belongs to Observation, not to Lab. Observation
holds current materialisation, fan-out, operational replay and passive
transport. Lab consumes that plane and is the custodian of durable scientific
evidence.

The earlier design gave Lab the operational coordination, materialisation and
delivery of observations and deferred a standalone package; this reverses
that assignment. The decision also preserves that a World may keep running
without Lab
([ADR-0079](../../adr/ADR-0079-world-lifecycle-is-independent-from-lab.md)).
It is consistent with ADR-0100, which gives Lab evidence custody and not the
runtime projection, and with ADR-0110, which justifies a separate Observation
repository to avoid coupling World to Lab.

### P3. Each authority exposes its own boundary, and does not depend on Observation

An authority decides what it exposes and exposes it deliberately. The
Observation capability reads only through that boundary and never
reconstructs a claim by inspecting an authority's private objects. For
Organism this is already required by ADR-0092.

**Decided.** The dependency points outward. The authorities do not depend on
the `observation` package: they do not import its types and are not coupled
to its repository. Each authority defines contracts or projections of its
own, and Observation adapts those public surfaces from outside.

```text
Organism    ─┐
Embodiment  ─┤  each exposes its own contracts and projections
Environment ─┤
World       ─┘
        ↓
Observation adapters
        ↓
Observation plane
```

The reason given with the decision: a passive capability must not become a
structural dependency of the authorities.

### P4. No path from observation to causal state

Nothing reachable through the plane changes causal state. Operator control
uses a separate, attributable request path to the relevant causal authority,
as ADR-0101 requires. A consumer that both observes and controls uses two
paths and the observing one carries no command.

### P5. Coherence is declared, and tied to the World causal cut when claimed

A set of claims presented together declares its coherence scope. It may be
called coherent with a World causal cut only under the condition the semantic
model states. The plane's delivery sequence is delivery order; it is not
causal time and must not be presented as such.

### P6. Claims about transduced signals name the owner of what is transduced

Because Modality is not an authority, a claim arising from transduction names
as its authority the owner of the state it describes, as ADR-0099 assigns it:
Embodiment for body-local calibration and episode transducer state, Organism
for learned perceptual adaptation, Environment for medium parameters.

### P7. Live replay is not evidence

Bounded replay inside the plane serves consumers that reconnect. It is not a
record of what happened for scientific purposes. Durable evidence is what the
evidence custodian has recorded, with provenance, under ADR-0100.

### P8. The inherited projection is transitional

**Decided.** The projection carried over from the source repository is not
kept for compatibility and does not become a stable contract by existing. Its
disposition is `DEFER` while it has necessary consumers, as a bridge clearly
marked as transitional, and `DROP` once a TARGET semantic family covers its
function.

## 4. Relation to the superseded design

Carried over, because the review found them compatible with the ratified
decisions: no hidden transfer of authority by location or serialisation; a
semantic claim is distinct from its delivery; Lab is authoritative only for
meaning it creates; domains expose intentional boundaries.

Not carried over: its list of authority domains, which included Modality and
excluded World; the name Symbiont; and the assignment of the operational
plane to Lab (replaced by P2).

Its candidate semantic families and its source-to-contract assessment of body
pose describe the historical source code and are not restated here.

## 5. Relation to existing code

This section reports what exists. It is not an evaluation of conformance.

At `observation@cb07ace` the repository contains a semantic claim model, an
in-memory observation plane with bounded current materialisation, fan-out,
replay and explicit rebase signalling, and a projection carried over from the
source repository. Its README states that operator controls, evidence
custody, transport, user interface and domain-specific readers are excluded.

Two observations bear on the proposals above:

- The module documentation of the semantic model in that repository still
  says that "The Lab hosts this representation for the operational
  Observation Plane", while the plane now lives in the `observation`
  repository. That sentence reflects the superseded assignment and
  contradicts P2 as decided.
- The same documentation says that source domains "do not import this
  module" and that their observation boundaries expose domain-owned values
  adapted structurally. That agrees with P3 as decided.
- The inherited projection is present and, per the repository's README, is
  "not a compatibility promise or a ratified Biopeia API". P8 fixes its
  disposition; the code does not yet mark it as transitional.
- The enumeration of authority domains there includes Lab alongside the four
  authorities. This agrees with the semantic model only if Lab is used
  exclusively for Lab-created meaning, which the code does not by itself
  enforce.

## 6. Not decided here

- Records, schemas, wire formats, transports, endpoints and storage.
- Any semantic family and its contract.
- How the plane is deployed: in process with World, in a separate process, or
  both.
- How evidence passes from the plane to the evidence custodian, and what
  makes that hand-over complete.
- Whether observation of a World continues when no consumer is attached, and
  what is retained in that case.

## 7. Decisions recorded

All by the Architecture Owner, on 2026-10-09.

First, in answer to the three questions this document originally posed:

1. The live plane belongs to the Observation capability; Lab is a consumer
   and the evidence custodian. See P2.
2. The authorities do not depend on the `observation` package; Observation
   adapts their public surfaces from outside. See P3.
3. The inherited projection is deferred while it has necessary consumers and
   dropped when a TARGET semantic family covers its function. See P8.

Then the design was approved as it stood, with the remaining points found
coherent with the ratified decision records and introducing no new transfer
of authority:

- **P1** approved: authority, producer, observation plane, consumer and
  evidence custodian are distinct roles, and holding one transfers none of
  the others.
- **P4** approved: there is no path from Observation to causal state; any
  control follows a separate, attributable path.
- **P5** approved: coherence is declared; delivery sequence never stands in
  for causal time, and coherence with a World causal cut may be claimed only
  with full traceability to that cut.
- **P6** approved: transduction does not make Modality an authority; the
  authority of a claim remains the owner of the semantics observed.
- **P7** approved: live replay is not scientific evidence; Observation's
  operational replay and Lab's durable custody stay separate.

The approval states that it does not mean the `observation` repository
implements the design; its implementation status stays not evaluated. It also
classes the module documentation noted in section 5, which says that Lab
hosts the plane, as a documentary non-conformity of the implementation
against this design, to be corrected there, and not as an obstacle to the
approval.
