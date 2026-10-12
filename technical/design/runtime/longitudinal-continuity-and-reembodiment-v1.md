---
id: design.cross-domain.longitudinal-continuity-and-reembodiment-v1
title: "Biopeia — Longitudinal Continuity and Re-embodiment Protocol v1"
document_type: design
owner: biopeia-project-owner
created: 2026-10-13
language: en
document_version: 1
decision_reference: ADR-0081
---

# Biopeia — Longitudinal Continuity and Re-embodiment Protocol v1

**Document type:** Design  
**Lifecycle:** Proposed — not ratified  
**Scope:** Organism, Embodiment, World, Modality; Lab for scientific validation  
**Normative basis:** ADR-0081  
**Implementation authorization:** Not granted  

## 1. Purpose

Define how the same canonical Organism may leave one embodiment and later enter
another while preserving its contract-relevant longitudinal state, maintaining
domain sovereignty and ensuring recoverable causal transitions.

This protocol must not be implemented through a reduced cognitive seed, implicit
state reset, positional actuator mapping, historical compatibility shim or
Lab-owned lifecycle shortcut.

## 2. Core invariants

1. **Identity continuity:** A canonical re-embodiment preserves `OrganismId`,
   longitudinal progression, learning, memory, private models, agency and
   competencies within the accepted continuation closure.
2. **Independent lifecycles:** Organism lifecycle, Embodiment episode
   lifecycle and World presence lifecycle are distinct.
3. **Owner sovereignty:** Each domain validates, adopts and persists its
   authoritative state. World coordinates causal publication using opaque owner
   checkpoint references.
4. **No silent loss:** Required longitudinal components may not be omitted
   merely because the current portable checkpoint cannot serialize them.
5. **No false competence:** Previously learned abilities are preserved as
   knowledge but may require revalidation before their execution in a new
   embodiment.
6. **No external semantics:** Re-acclimatization must not inject semantic
   interpretations, target competencies or environmental ground truth into
   Organism.
7. **Recoverable boundaries:** Every published causal transition must satisfy
   World’s participant completeness, persistence and recovery requirements.
8. **Scientific independence:** A correct lifecycle transition does not
   establish preservation of functional competence, adaptation or learning
   efficacy.

## 3. Owner responsibilities

### Organism

Owns identity, lifecycle decisions and the complete private continuation
closure.

It must expose an owner-authorized continuation candidate that explicitly
accounts for all required longitudinal components.

Changes to an Embodiment association occur only through an accepted lifecycle
transition. Ordinary active progression may not replace its embodiment context.

### Embodiment

Owns body identity, morphology, somatic state, episode transitions and
authoritative descriptions of available effectors and receptors.

It must distinguish body termination from other valid reasons for ending an
embodiment episode.

It does not determine Organism identity or evaluate the meaning of previously
learned cognitive representations.

### World

Owns causal time, presence registration, participant completeness, causal
ordering, commit and recovery coordination.

It does not inspect, modify or reconstruct Organism cognition or Embodiment
somatic truth.

Each committed transition must be independently recoverable. The protocol must
not presume atomicity across multiple successive committed causal cuts.

### Modality

Supplies the applicable transduction contracts and identity-bound channel
declarations without becoming the owner of persistent cognitive or somatic
state.

### Lab

May prepare and execute specifically authorized experiments, capture evidence
and evaluate scientific hypotheses.

It does not acquire ordinary reproduction, cognitive, lifecycle or causal
authority.

## 4. Lifecycle protocol

### Stage A — Leave the current embodiment

An authorized lifecycle request identifies the Organism, current embodiment
episode, applicable World context, cause and provenance.

The relevant owners validate their proposed changes. World publishes a
consistent causal cut recording the approved departure or presence transition.

The Organism may become `DORMANT` without terminating its identity. The
departure need not be caused by body death.

### Stage B — Preserve longitudinal continuity

Organism preserves its declared complete continuation closure.

Dependencies are classified as portable internal state, externally resolvable
state, embodiment-dependent state, or disposable temporary machinery.

A required dependency that cannot be restored blocks canonical continuation. It
must not be silently removed or replaced with an empty initial state.

An Organism may remain dormant without a new Embodiment and without requiring a
pending World presence.

### Stage C — Attach a new embodiment

Embodiment establishes or validates the new body and episode identities.

Organism validates a new `EmbodimentContextRef` through its authorized
`DORMANT → ACTIVE` transition.

World coordinates any required presence changes and commits a causally
consistent cut containing the appropriate owner references.

A failed attachment leaves the previously committed state authoritative.

### Stage D — Resume and adapt

Organism resumes with its preserved longitudinal state.

Knowledge or competencies associated with the previous embodiment may be marked
as requiring applicability validation. Such status must distinguish preserved
knowledge from current executability.

Any recalibration proceeds through authorized sensorimotor interaction. The
protocol does not prescribe a fixed duration, adaptation algorithm or artificial
learning objective.

## 5. Continuation closure

Before implementation, Organism must publish a versioned declaration
identifying every required longitudinal component and its owner, persistence
mechanism, dependencies, validation rules and reactivation semantics.

The inventory must examine at least:

- Identity, lifecycle and longitudinal progression.
- Cognitive graph, recurrent activation and learned parameters.
- Memory and experience records.
- Private predictive and generative models.
- Agency, commitments, exploration and learned motor competencies.
- Genetic, germline and epigenetic state.
- Normalization, metaplasticity and learning safety state.
- Dependency references and model-resolution requirements.

Existing `CognitiveRuntimeCheckpoint` remains a bounded component until
explicitly proven sufficient for the declared closure. It must not be relabeled
as complete by convention.

## 6. Failure and recovery

The implementation design must cover interrupted departure, failed owner
checkpoint validation, unavailable model dependencies, invalid morphology,
duplicate or stale episode identity, failed presence registration and
interrupted reactivation.

For every case, it must identify the last authoritative committed state, the
recoverable owner references and the conditions for safe retry.

Idempotency and replay must be evaluated per operation. Recovery may not infer
uncommitted state from timestamps, temporary artifacts or partially written
evidence.

## 7. Technical acceptance

A conforming implementation must demonstrate:

1. Identity preservation across body and episode changes.
2. Explicit, valid lifecycle transitions without ordinary progression bypass.
3. Complete owner-declared continuation closure with no silent omissions.
4. Exact participant and checkpoint reference validation.
5. Recovery to an unambiguous committed causal cut.
6. Rejection of stale or mismatched morphology and episode references.
7. Separation of retained competencies from their immediate executability.
8. No unauthorized cross-domain state mutation.
9. Successful restoration of required private dependencies.
10. No regressions in existing causal, persistence and constitutional contracts.

## 8. Scientific acceptance

Separately authorized Lab protocols should investigate:

- Retention of cognitive knowledge after embodiment changes.
- Differences between preserved knowledge and usable motor competence.
- Adaptation to changed morphology or transduction.
- Distinction between genuine transfer and experimenter-provided mapping.
- Effects of dormant duration and repeated embodiment changes.

Negative and inconclusive results must remain admissible scientific outcomes.
Passing technical tests does not establish any of these hypotheses.

## 9. Decisions required before implementation

- Exact completeness and versioning semantics for the Organism continuation
  closure.
- Whether embodiment-dependent competence applicability requires new persisted
  metadata or can be derived from existing state.
- Exact ordering and coordination of departure, dormancy, attachment and World
  presence transitions.
- Handling of generative models with active external dependencies.
- Episode closure semantics and the existing Embodiment APIs that can implement
  them.
- Recovery and idempotency requirements for each transition boundary.

These decisions must be reconciled against existing contracts before proposing
new schemas or public APIs.

## 10. Governance

This design refines ADR-0081 but does not amend it.

It does not authorize implementation, experimental execution, replacement of
established contracts or closure of existing migration findings.

Implementation work must be derived into repository-owned Issues after
acceptance by the competent authority.

No compatibility code for the historical Symbiont implementation is required or
permitted solely to reproduce its old API.
