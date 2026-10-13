# Lab–World–Observation Integration v1 — AS-IS Evidence and Proposed Boundaries

**Implementation authorization:** Not granted by this document  
**Design issue:** [Docs #170](https://github.com/biopeia/docs/issues/170)  
**Review basis:** Exact repository revisions listed in §2, inspected 2026-10-13

## 1. Purpose and decision boundary

This document records the current production evidence and a bounded integration direction for a first reproducible Lab–World–producer-domain–Observation composition. It distinguishes two independent boundaries:

1. **Lab → target authorities:** Lab may request a declared operation; the target domain validates and owns its state transition; World coordinates and commits applicable causal changes; Lab retains experiment and evidence provenance.
2. **Owner domains → World publication → Observation → read-only consumers:** semantic owners produce projections; World verifies their relationship to a committed causal cut; Observation passively retains/delivers the resulting observations; consumers read without acquiring authority.

This is an evidence map and proposal, not a new contract. It does not decide the open owner questions in Observation #40/#38 or Lab #330/#332. It authorizes no protocol execution, new API/schema, transport, durable store, authentication/authorization mechanism, browser access, or Frontend implementation. Green tests establish only their stated code behavior.

The applicable boundaries remain governed by ADR-0078 (passive Observation), ADR-0099 (Modality is not an independent semantic authority), ADR-0100 (Observation capability and Lab evidence custody), ADR-0113 (independent Frontend/Lab presentation boundary), the Observation Semantic Model v1, and the ratified World/Environment and causal-commit decisions. This document does not amend them.

## 2. Revision-pinned evidence basis

The following `main` revisions were queried from GitHub during this review. Reproduce the local source inspection from the workspace with `git -C repos/<repo> show <sha>:<path>`; the values are source revisions, not runtime deployment identifiers.

| Repository | Revision |
|---|---|
| `world` | `940c674d077860c44f07050cb79750e517d0099e` |
| `organism` | `0ddadac6d51ab39aeee909cb423a911b069b11dc` |
| `embodiment` | `56e9a34a6a778a298493dabca9d15b0912066803` |
| `environment` | `d1dc309636fc66471e755d1f691826ebf8c552fe` |
| `modality` | `93a4c3a4ea71dcf65269ce730aab736238fd3ea7` |
| `observation` | `1456df093e4ac28032d956e4df30957f0bf87cec` |
| `lab` | `4f37ce9f7f141be3e955f6f286487a358c9b8222` |
| `docs` | `b595d69ed3de8c114b1083b673061334e411bbe2` |

Focused evidence paths at those revisions:

- `world:src/world/observation_publication.py`, `world:tests/test_observation_publication.py`.
- `observation:src/observation/plane.py`, `observation:src/observation/semantic.py`, `observation:src/observation/environment.py`, `observation:src/observation/embodiment.py`, and their focused tests `tests/test_plane.py`, `tests/test_environment_observation.py`, `tests/test_embodiment_observation.py`.
- `environment:src/environment/physical.py` and `environment:tests/test_physical_projection.py`.
- `embodiment:src/embodiment/observation.py`, `embodiment:src/embodiment/observation_family.py`, and `embodiment:tests/test_body_pose_observation_projection.py`.
- `lab:src/lab/interventions/material_transfer.py` and `lab:tests/integration/test_material_transfer_intervention.py`.
- `organism` and `modality` were searched at the pinned revisions for Observation publication/adapters; no production semantic-family adapter for these domains was established by this audit. This is a bounded search result, not a claim that no related capability exists anywhere.

Candidate-only evidence is kept separate from `main`: World PR #136 has an adversarial independent review with outcome **BOUNDED**. Its exact candidate verifies a World post-commit publication non-interference slice, but its fixture returns unchanged projections and no-op adoption callbacks. It therefore does not demonstrate that non-trivially adopted physical state is what the post-commit projection publishes. See [review record](https://github.com/biopeia/world/pull/136#issuecomment-6151958948) and [World #135](https://github.com/biopeia/world/issues/135#issuecomment-6151960668). The PR remains independent candidate evidence and must not be read as merged `main` behavior.

## 3. AS-IS capability map

Status terms describe evidence only: `IMPLEMENTED` means the named bounded path exists in the pinned code; `PARTIAL` means only part of the desired capability is evidenced; `MISSING` means this audit did not establish a TARGET path; `PROPOSED` means design/candidate only; `BLOCKED` means an owner decision or dependency prevents implementation.

| Capability | Status | Evidence and limit |
|---|---|---|
| Environment-owned finite scalar-field observation projection | `IMPLEMENTED` | Environment supplies a typed projection and Observation maps it without claiming to define Environment truth. This is one family, not a general Environment publication API. |
| Embodiment-owned body-pose projection | `IMPLEMENTED` | Pose projection carries body/episode/morphology and causal correlation fields. It is not itself proof of a World commit. |
| World verification of post-commit publication input | `IMPLEMENTED` | `publish_committed_owner_observations` re-verifies a World-issued committed-cut receipt, requires owner references to belong to that cut, authority to match the owner, provenance to reference the checkpoint digest, World tick to match, and configuration to identify the World. World does not interpret claim values or read owner checkpoint bytes. |
| Multi-observation publication atomicity | `PARTIAL` | All input validations occur before publication begins, but plane writes are sequential. Failure during delivery may leave a prefix published; no transactional multi-message guarantee is stated. |
| Observation in-process retention/read/replay | `IMPLEMENTED` | `ObservationPlane` has bounded current materialization, bounded replay by delivery sequence, live queues, detached value snapshots, and explicit rebase signaling on known replay/queue boundaries. |
| Durable observational history/restart recovery | `MISSING` | The pinned plane is in-memory. No durable archive, restart recovery, or historical query implementation was established. Observation #38 is a proposed design issue, not implementation evidence. |
| Lab read-only consumption of `ObservationPlane` | `MISSING` | No Lab production dependency/path to `current_messages`, `open_stream`, or `PlaneStreamSubscription` was established. The material-transfer path calls `observation.projection.runtime_tick_events`, which is not a read of authorized Observation messages. |
| General Lab request-to-owner authorization boundary | `PARTIAL` / `BLOCKED` | The material-transfer request is caller-declared and explicitly not authentication or permission. It implements one controlled operation, not a general dispatch/authorization contract. Lab #330 remains the design gate. |
| `ExperimentIntent` as executable/authorized operation | `PROPOSED` | Lab PR #329 is an experimental, non-executing declaration model. It does not authorize, dispatch, or execute an operation. |
| Observation owner decision on Lab's same-process read boundary | `BLOCKED` | Observation #40 is open and requires explicit Observation-owner disposition plus Lab-side requirements confirmation. |
| Observation owner decision for durable observational lake | `BLOCKED` | Observation #38 remains proposed; no archive implementation or accepted storage contract is evidenced. |
| Browser/network consumer contract | `MISSING` / out of scope | No browser-accessible transport, endpoint, authentication, or consumer contract is established by these pinned sources. Observation #37 is a separate browser-readiness gate. |
| Organism/Modality semantic projection to Observation | `MISSING` in this audit | No production adapter/path was established at the pinned revisions. Modality may not be promoted to an independent semantic authority by inference. |

## 4. Boundary A — Lab request to target authority

The supported architectural direction, without freezing an envelope or dispatch mechanism, is:

```text
Lab protocol/run context
    → explicit request with provenance and intended target
    → target domain validates its own state and operation conditions
    → target owner adopts or rejects its candidate
    → World coordinates/commits the applicable causal transition
    → Lab records experiment/evidence provenance under Lab custody
```

`request`, `authenticated principal`, `authorization`, `target-owner acceptance`, and `committed causal action` are distinct concepts. A caller-supplied operator/principal string or `ExperimentIntent` is not authentication or permission. World is not the semantic owner of Environment or Embodiment state; Lab is not an authority over those states; Observation is not an intervention path. Existing controlled material-transfer behavior is evidence for one bounded operation only and does not generalize to arbitrary Lab operations.

Lab #330 owns the request/target-authority design decision. Lab #332 depends on approved Lab and Observation boundaries before implementing a reader. This document makes no new decision about whether Lab may execute a specific protocol or operation.

## 5. Boundary B — owner publication to read-only consumer

The existing post-commit path is:

```text
owner state / owner-authored projection
    → World-issued committed-cut receipt
    → World verifies owner reference, authority, lineage digest, World identity and causal tick
    → ObservationPlane.publish(owner observation)
    → in-process consumer reads/replays bounded retained messages
```

The layers must remain distinguishable:

- **Semantic authority:** the owner of the asserted domain state.
- **Projection/producer:** the component that forms a contract-approved observation from owner state.
- **World verification:** evidence that the publication is associated with a committed cut; World does not reinterpret the claim.
- **Observation:** passive bounded retention and delivery; not an owner of source truth and not Lab's scientific evidence custodian.
- **Consumer:** reads detached observations; its view is not a complete census and does not change causal state.

The plane's `current_messages()` returns the bounded retained materialization, not a source census. Eviction, stream expiry, consumer overflow, or unavailable delivery is not source-state absence. Replay sequence is delivery metadata, not World causal time or a domain clock. A rebase signal says the consumer must obtain an authorized new view by a supported mechanism; it does not state what that mechanism is for a future durable or remote consumer.

Observation #40 must decide whether Lab may use the current same-process read boundary and state its precise limits. Observation #38 separately owns the durable-lake design and any required constitutional derivation. Observation #37 concerns a future browser consumer and is not a prerequisite for the in-process Lab question. No one issue implicitly settles the others.

## 6. Identity, time, provenance, and custody constraints

Any later implementation proposal must preserve these already-governed distinctions:

1. Typed, issuer-scoped subject identities are not interchangeable across domains; associations must be explicit.
2. World causal tick and commit identity are not Observation delivery sequence, Lab run identity, or host wall-clock time.
3. Owner lineage/checkpoint references remain opaque to World except for the authorized correlation checks it performs.
4. Observation delivery/capture metadata cannot overwrite claim authority, producer identity, epistemic basis, or owner domain time.
5. Lab owns scientific artifacts/evidence; observing or retaining a claim in Observation does not admit it as scientific evidence.
6. An observation missing from a bounded or unavailable consumer view cannot be interpreted as source absence, non-existence, or a failed causal event.

These are constraints on future work, not a new serialized identity/time/provenance schema.

## 7. Adversarial acceptance cases for downstream implementation

The following cases are design-derived test obligations; they are not evidence that an implementation currently passes them:

| Case | Required safe interpretation |
|---|---|
| Owner projection references a checkpoint outside the committed World cut | Reject publication; do not create a delivery sequence. |
| Owner, authority, lineage digest, World identity, or causal tick mismatch | Reject before publication; no reinterpretation or silent repair. |
| A multi-message publication fails after one message was accepted | Treat delivery as potentially partial; do not claim batch atomicity or roll back a committed World cut. Retry semantics require the applicable owner contract. |
| `current_messages()` omits a subject after bounded eviction | Treat as not present in this retained view; do not infer source absence. |
| Replay watermark is expired/future or a subscriber queue overflows | Surface explicit rebase/unavailable delivery; do not fabricate a continuous history. |
| Consumer mutates a returned snapshot | Retained plane state remains unchanged; verify against the actual supported value types. |
| World advances while Lab is not reading | Do not claim the bounded plane provides a durable complete history. |
| Lab request is malformed, unauthorized, rejected by owner, or interrupted | No owner adoption/World commit unless the owner contract accepts and World commits; provenance must distinguish requested, rejected, interrupted, and committed outcomes. Exact record/API semantics remain unselected. |
| Observation is unavailable while a causal owner is healthy | Delivery failure must not mutate or redefine source truth. |

## 8. Current experimental PRs and their limits

- [Observation PR #39](https://github.com/biopeia/observation/pull/39) adds adversarial tests around bounded eviction, snapshot mutation, and run/history boundaries. It is a draft candidate, not a durable data lake and not a consumer API decision.
- [Lab PR #329](https://github.com/biopeia/lab/pull/329) introduces an experimental declaration-only `ExperimentIntent`; it does not execute or authorize an operation and is not a production Observation reader.
- [World PR #136](https://github.com/biopeia/world/pull/136) is a separately reviewed candidate regression with the bounded fixture limitation stated in §2. It is not evidence of general post-adoption projection correctness.

These candidate changes are not merged by this document and do not satisfy the independent owner decisions in Observation #40/#38 or Lab #330/#332.

## 9. Gates and bounded stopping point

This design tranche is complete when the document is independently reviewed against the exact PR head, its source claims and limits are traceable to the pinned revisions, and the owning issues link to the review evidence. That is a documentation stopping point, not completion of the integration.

Any executable Lab consumer remains blocked until the competent owners resolve Observation #40 and Lab #330, and Lab #332 confirms the approved consumer boundary. Durable historical query remains blocked on the distinct Observation #38 design/decision. Browser/Frontend implementation remains outside this tranche and subject to Observation #37 and the approved Frontend readiness plan. After these gates, a separately scoped implementation issue must identify the approved in-process boundary, real producer publication, exact failure semantics, CI evidence, and independent review requirements.

Do not extend this document into unapproved schemas, APIs, storage, transport, authentication, protocol execution, or scientific conclusions. If evidence reveals incompatible current contracts, record the conflict and route it to the competent owner rather than papering it over here.

## 10. Reproduction commands and evidence limits

The source audit is reproducible by checking out the SHAs in §2 and inspecting the focused paths listed there. Focused tests already present on their respective pinned repositories are:

```text
world:       tests/test_observation_publication.py
             tests/integration/observation/test_world_post_commit_owner_publication.py
observation: tests/test_plane.py
             tests/test_environment_observation.py
             tests/test_embodiment_observation.py
environment: tests/test_physical_projection.py
embodiment:  tests/test_body_pose_observation_projection.py
lab:         tests/integration/test_material_transfer_intervention.py
```

No new test run is claimed by this document. The audit evidence is source inspection at exact revisions plus the separately attributed review/test result of World PR #136. These sources do not prove durable retention, complete capture, scientific admission, browser access, generalized authorization, all-domain semantic publication, functional competence, or end-to-end cross-process execution.
