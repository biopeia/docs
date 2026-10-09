# Observation Architecture for Biopeia v1

This document is a **proposal**. It decides nothing. Its state is recorded in
`registry/designs.yaml`, which is the only authority for it; nothing here
should be read as approved or implemented.

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

Each proposal below is new in this document and awaits a decision.

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

The earlier design gave Lab the operational coordination, materialisation and
delivery of observations and deferred a standalone package. This design
proposes the opposite assignment: the live plane is part of the Observation
capability, and Lab is one of its consumers.

Reasons: ADR-0100 separates runtime projection and transport from evidence
custody, and gives only the last to Lab; ADR-0110 justifies a separate
Observation repository precisely to avoid coupling World to Lab; and a World
that may run without Lab
([ADR-0079](../../adr/ADR-0079-world-lifecycle-is-independent-from-lab.md))
would otherwise lose its observability when Lab is absent.

### P3. Each authority exposes one intentional observation boundary

An authority decides what it exposes and exposes it deliberately. The
Observation capability reads only through that boundary and never
reconstructs a claim by inspecting an authority's private objects. For
Organism this is already required by ADR-0092.

Whether an authority's package depends on the Observation package, or
Observation adapts values an authority exposes independently, is left open in
section 6.

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
  repository. That sentence reflects the superseded assignment.
- The enumeration of authority domains there includes Lab alongside the four
  authorities. This agrees with the semantic model only if Lab is used
  exclusively for Lab-created meaning, which the code does not by itself
  enforce.

## 6. Not decided here

- Records, schemas, wire formats, transports, endpoints and storage.
- Any semantic family and its contract.
- Whether authorities depend on the Observation package or are adapted from
  outside it (P3).
- How the plane is deployed: in process with World, in a separate process, or
  both.
- How evidence passes from the plane to the evidence custodian, and what
  makes that hand-over complete.
- Whether observation of a World continues when no consumer is attached, and
  what is retained in that case.

## 7. Questions for the Architecture Owner

1. Is P2 accepted: the live plane belongs to the Observation capability and
   Lab is a consumer and the evidence custodian?
2. Under P3, which dependency direction is intended between the authorities
   and the Observation package?
3. Should the copied projection of the source repository, which carries
   historical payload keys, remain in the `observation` repository or be
   dropped once a semantic family replaces it?
