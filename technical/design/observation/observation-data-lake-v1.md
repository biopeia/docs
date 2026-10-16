---
id: design.observation.observational-data-lake-v1
title: "Biopeia Observation — Passive Observational Data Lake v1"
document_type: design
owner: biopeia-observation-owner
created: 2026-10-13
language: en
document_version: 1
decision_reference: ADR-0100
---

# Biopeia Observation — Passive Observational Data Lake v1

**Lifecycle:** Proposed — not ratified
**Scope:** Observation; producer domains World, Organism, Embodiment, Environment and Modality; Lab as a read-only consumer and separate evidence custodian; Frontend as a future read-only consumer
**Normative basis:** ADR-0078, ADR-0095, ADR-0099, ADR-0100, ADR-0110; approved Observation Semantic Model v1 and Observation Architecture for Biopeia v1
**Implementation authorization:** None. This document selects no store, schema, API, transport, deployment or security mechanism.

## 1. Purpose and decision boundary

This proposal evaluates the Owner direction for Observation to become a durable,
searchable, passive collection of owner-authorized observations for multiple
read-only consumers. It describes the target responsibilities and the decisions
that must precede implementation; it does not assert that the current
Observation implementation is a data lake.

The existing approved Observation architecture assigns the live plane to
Observation and durable **scientific evidence/provenance custody** to Lab and
scientific apparatus. This design preserves that allocation. It proposes a
separate concept: an **operational observational archive** that retains
owner-authorized claims for read-only inspection and query. Such retention does
not admit data as evidence, validate a scientific method, establish
completeness, or transfer claim authority to Observation.

The Architecture Owner accepted this conceptual direction on 2026-10-13:
Observation is the passive operational observational archive, while Lab remains
the separate scientific-evidence custodian ([Observation #38 owner disposition](https://github.com/biopeia/observation/issues/38#issuecomment-6153128772)).
That acceptance is bounded to the responsibility separation and target
direction. It does not ratify this complete design or authorize a store,
schema, API, transport, retention/deletion policy, security profile, runtime
implementation or merge. Before this proposal can be marked approved, the
competent authority must determine whether the accepted direction is fully
covered by existing ADRs or needs a derived constitutional ADR; any proposed
change to ADR-0100 still requires its own explicit disposition.

## 2. Ratified constraints

The following are constraints, not proposals of this document:

1. Observation is causally passive: it may read, project, transport, buffer,
aggregate, visualize and record, but cannot modify observed causal state
(ADR-0078).
2. Observation is not a semantic authority. Organism, Embodiment, Environment
and World retain their own claim meanings. Modality is not an independent
semantic authority (ADR-0095, ADR-0099 and the Semantic Model).
3. A claim's authority, producer, asserter, measurement source, consumer,
domain time, revision, epistemic basis and provenance remain distinguishable.
Delivery time is not domain time.
4. World alone determines whether claims are associated with a committed World
causal cut. Observation may preserve and expose that assertion, but may not
infer or repair it.
5. Live replay is not scientific evidence. Durable scientific evidence and
its admission/provenance custody remain with Lab/scientific apparatus under
ADR-0100.
6. Lab and Frontend are consumers of Observation publications. Neither may
inject or edit source observations through a read path.
7. No legacy API, inherited `ObservedFrame`, compatibility bridge or
historical behavior is admitted as a TARGET contract (UC-0001).

## 3. Proposed responsibility model

The term “data lake” names a capability boundary, not a database product or
authority. The logical stages are:

```text
domain owner
  → owner-authorized outward publication
  → passive Observation capture
  → retained original observation + capture record
  → rebuildable read indexes/materializations
  → read-only consumer query or delivery
```

| Concern | Responsible authority | Boundary |
|---|---|---|
| Claim meaning, subject identity, effective domain time/revision | Claim's semantic owner | Owner defines and validates the claim; Observation does not reinterpret it |
| World-cut identity and commit status | World | Observation records only World-verified correlation; no synthetic joins |
| Publication eligibility and source completeness | Publishing owner under an explicit outward contract | A successful capture cannot prove the source emitted everything |
| Capture receipt, retained bytes and operational indexes | Observation | Operational retention only; no causal adoption or scientific admission |
| Consumer's study/run interpretation and scientific evidence admission | Lab | Lab may reference exact observations and add its own evidence records |
| Human-facing presentation | Frontend (when authorized) | Read-only rendering; no new claim, causal relation or source identity |
| Derived analysis and interpretation | The explicitly responsible consumer/authority | Derived data is separately identified and cannot overwrite source claims |

The ingestion set for this proposal is limited to the owner-authorized outward
boundaries of **Organism, Embodiment, Environment, World and Modality**. This
list does not make Modality a fifth semantic authority. A Modality-originated
representation is admissible only under an explicit contract that identifies
the actual semantic owner and preserves the applicable measurement and
transduction lineage. Lab, Frontend, workspace tools, researchers, UI clients,
external tools and Observation itself are not observational source producers.

## 4. Operational archive versus scientific evidence

The proposal uses two deliberately separate records of custody:

| Operational observational archive (Observation) | Scientific evidence custody (Lab/apparatus) |
|---|---|
| Captures owner-authorized claim publications and capture outcomes | Admits selected material into a study/run evidence record |
| Supports operational inspection, historical queries and future replay contracts | Supports scientific provenance, protocol context, analysis and retention obligations |
| May contain incomplete, duplicate, stale, unreviewed or non-admissible data | Must record its own admission decision, provenance and limitations |
| Does not establish scientific validity or method equivalence | Is the custodian for evidence; admission does not alter source claim meaning |

An observation may be absent from the archive even if its source state existed;
it may be present without being scientific evidence. An archive receipt is
not an evidence-admission receipt. Lab may reference the exact captured
observation identities/revisions as inputs to a separate evidence record, but
must retain the provenance and admission decision under Lab authority.

The archive should preserve original owner-authorized claim content and
provenance as immutable inputs once accepted by its capture boundary. Indexes,
query projections and consumer-specific views are derived and rebuildable; they
must retain lineage to the source observations and must not rewrite them.
Immutability here describes the logical accepted source record, not a selected
physical storage medium or backup technology.

## 5. Capture and completeness semantics

Capture is a passive side path. It must not make a World commit depend on
Observation availability unless a future causal contract explicitly says
otherwise and receives competent review. The expected failure behavior for
this proposal is:

```text
owner publishes / World commits
        ↓
Observation capture succeeds, is partial, duplicates, or fails
        ↓
causal result remains the owner/World result
capture outcome and any gap are reported separately
```

The architecture must distinguish at least:

- **Source-state absence:** the owner says no applicable state/claim exists.
- **No publication observed:** no matching publication was captured; this is
not evidence of source absence.
- **Capture gap:** a known publication/delivery interval or sequence is missing
under a declared owner contract.
- **Retention/query gap:** source material was not retained or is no longer
available through a declared archive capability.
- **Consumer delivery failure:** a retained publication was not delivered to a
particular consumer.
- **Unsupported:** no approved contract exists for the requested claim/query.

These conditions must never collapse into a numeric sentinel, empty value or
unqualified “no observation”. Completeness is always scoped to an identified
producer boundary, family/revision, subject/scope and applicable domain
interval. Observation cannot claim completeness merely because capture itself
was healthy.

Owner-committed World correlation, owner publication identity, Observation
capture identity, transport/delivery identity and consumer query identity are
separate concepts. Duplicate delivery may occur. The proposed
deduplication/idempotency and conflict semantics are specified in §5.1 for
owner review; they do not select a global exactly-once guarantee. If two
records conflict for the same owner identity/revision, the archive must
preserve the conflict and surface it, not choose a winner by arrival time.

### 5.1 Proposed logical identity, integrity and lifecycle rules

The following rules are a proposed logical contract for owner review. They do
not define schema fields, identifier encoding, a digest algorithm, a storage
engine, or an API. They are not approved implementation requirements until
the competent owners accept or amend them.

**Identity and deduplication.** Keep these identities distinct:

- semantic claim identity and its owner-defined revision;
- owner publication identity, if the publishing contract supplies one;
- Observation capture-attempt/receipt identity;
- delivery, query, or derived-view identity.

Deduplicate retries only when the owner publication contract supplies the same
stable publication identity within its declared scope. Do not deduplicate
merely because payloads compare equal: two distinct publications may
legitimately carry equal values. A repeated publication identity with the
same verified content is a duplicate capture of one logical source
publication, while its separate capture attempts may remain auditable. The
same identity with different content, owner revision, or provenance is a
conflict: preserve both received forms and the conflict evidence, mark the
logical record unresolved, and do not select a winner by arrival order or
silently overwrite an accepted original. If an owner contract provides no
stable publication identity, exact retry deduplication is not guaranteed and
the limitation must be exposed; Observation must not invent an owner identity.

**Integrity.** Once a source publication is accepted, its original logical
content and provenance are immutable. The archive design must bind an
integrity check to the exact accepted representation and verify it on
retrieval and recovery. The integrity mechanism and canonical representation
remain implementation decisions. A matching digest establishes content
integrity only; it does not establish semantic truth, source completeness,
scientific validity, or owner authority. A correction is a separately
identified owner publication/revision, never an in-place edit to history.

**Retention and deletion.** Retention is explicit policy, not incidental
storage cleanup. The Owner's blanket authorization was used to select this
conservative **proposed local-prototype policy**: accepted original
observations are retained without automatic age-based expiration; accepted
originals are not silently overwritten or pruned. This selection is recorded
in [Observation #38](https://github.com/biopeia/observation/issues/38#issuecomment-6211915578).
It is a proposal for the operational archive only, not an indefinite legal
retention promise, a legal hold, or a change to Lab's independent scientific
evidence policy under ADR-0100. No deletion mechanism or deletion authority is
defined here. A future deletion request must be authorized and recorded
separately from source correction; logical suppression/tombstoning and
physical erasure remain distinct outcomes, and legal hold blocks any deletion
it covers. The competent authorizer, grounds, scope, review path, and effects
on retained originals and cross-referenced evidence still require a specific
disposition before a deletion capability is implemented. Physical-erasure
obligations, including replicas/backups and legal exceptions, require
competent legal/security/operations disposition before implementation. No
consumer may infer source absence from an access-denied, suppressed, expired,
or unavailable record.

**Resource ceiling and capture gaps.** The local prototype must use a declared
resource ceiling. Reaching that ceiling stops further Observation capture
cleanly and records/reports an explicit capture or retention gap; it must not
block, roll back, or alter a World commit, and it must not trigger deletion of
older accepted originals. Capture may resume only when capacity is available,
and the uncovered interval remains visible as a gap. The ceiling, its
measurement and the operator-visible stop signal are implementation
parameters to validate; this design does not select a storage technology,
numeric quota, service, or deployment model. It does not authorize shared,
remote, or production exposure.

**Recovery.** Recovery must verify retained originals before exposing them,
rebuild derived indexes/views from verified originals, and report any missing,
corrupt, conflicting, or unavailable interval as a gap. Recovery may not
silently repair or invent source claims, infer completeness from a healthy
index, or re-execute a World/owner transition. An Observation capture retry,
where authorized, refers to the already committed owner publication/cut and
must remain distinct from a causal transition retry. A recovered archive
must identify its verified recovery point and any gaps; it must not claim
complete history unless the relevant owner publication contract proves that
bounded claim. The durable mechanism and recovery-point guarantees remain
open.

These proposed rules require explicit disposition by the Observation Owner
for archive identity, capture conflicts, integrity and recovery, and by the
Lab Owner for the separation from evidence retention/admission. The retention
selection above records the agent's conservative design choice under the
Owner's blanket authorization; it does not resolve the separate constitutional
question of whether this archive requires a derived ADR to clarify
ADR-0100/P7. The competent
authority for logical suppression/tombstoning and its effects on source-owner
records and Lab-held evidence remains unresolved and must be identified and
recorded before implementation. Architecture Owner disposition remains
required for the constitutional archive boundary and any policy that changes
ADR-0100. Security/legal/operations authorities must decide physical-erasure
and hold obligations where applicable.

## 6. Time, ordering, replay and revisions

The archive must preserve, without conflation:

1. domain-effective time/revision defined by the semantic family;
2. owner publication/capture correlation, where available;
3. Observation capture/receipt time, if recorded;
4. consumer delivery/query order, if provided.

Host wall clock is metadata only, never causal authority. Cross-domain ordering
is not implied by capture order. A projection may claim coherence with a World
cut only when every included claim has the World-verified cut association
required by the approved semantic model. Otherwise it must expose the
individual times/revisions and declared coherence limitations.

Historical query is not automatically causal re-execution. Any future
observation replay must state what was retained, ordering guarantees, gaps,
family revisions and unavailable intervals. It cannot imply that World was
re-run or that all owner state was captured. A query against a newer semantic
revision must not silently reinterpret older claim meanings; compatibility or
transformation rules require their own explicit family contract and lineage.

## 7. Conceptual layers and options

This design keeps logical responsibilities stable while leaving implementation
choices open:

| Layer | Required logical behavior | Implementation decision left open |
|---|---|---|
| Capture boundary | Accept only explicitly authorized owner publications; record acceptance/rejection/gap outcomes | In-process, separate process or hybrid placement |
| Original observation archive | Preserve accepted owner claim and provenance without silent rewrite | File, relational, object, log-structured or other storage |
| Read indexes/materializations | Support declared query use cases; rebuild from originals; retain source lineage | Index model, refresh strategy and partitioning |
| Live delivery/replay | Distinguish live bounded replay from retained history; expose actual gaps | Push/pull, protocol, endpoint and delivery cadence |
| Query/read contract | Return scoped results with availability/completeness and provenance | API, query language, client library and authorization mechanism |

Three high-level persistence options remain viable for later evaluation:

1. **Extend the current in-process plane.** Lowest initial complexity, but does
not by itself satisfy cross-process durability or restart history.
2. **Add a durable append-oriented archive behind the passive capture
boundary.** Could provide durable originals with rebuildable indexes, but
requires explicit recovery, retention, access and operational ownership.
3. **Use a split capture/archive arrangement.** May isolate causal processes
from archive availability, but introduces delivery gaps, buffering and
operational coordination that must be declared and tested.

The accepted target direction is an operational, durable and searchable
observational archive distinct from Lab evidence custody. Option 2 is therefore
the leading conceptual candidate for evaluation, not an approved architecture
choice. It does **not** select an implementation, accept a data-loss envelope
or authorize a new service. Option 1 alone cannot satisfy durable history;
option 3 may be selected if evidence shows it materially improves isolation
without hiding capture gaps. The choice among persistence arrangements remains
open until the data/lifecycle, security and operational contracts are accepted.

## 8. Supported and excluded consumer use cases

The following are target use cases only after the relevant family and read
contracts are approved. Current support is not implied.

| Use case | Minimum required source contract | Current readiness at inspected revisions |
|---|---|---|
| Browse Worlds/runs and available publication scopes | Stable typed identities and an authorized catalog/index source | Not established by the in-process Observation plane |
| Inspect a claim and provenance | Approved family/revision, subject identity, authority, epistemic basis, time/revision and provenance | Semantic model exists; browser/read contract not established |
| Inspect a World committed cut | Verified World cut and traceable owner claims | Bounded producer-side post-commit path exists; historical query/access contract not established |
| Explore spatial state | Owner-approved pose/geometry, units, frames, morphology/environment revisions and availability | Partial family readiness; not a complete consumer contract |
| Inspect sensorimotor relations | Explicit action/signal lineage and evidence boundaries; no inferred causal edge | No complete approved cross-domain consumer contract established |
| Review scientific evidence | Lab evidence record, study/run/protocol context and Lab admission | Out of scope for Observation; remains a Lab surface |
| Control, pause, step, inject, modify or launch a World | Separate attributable control/intervention contract | Excluded; never provided through this read-only archive |
| Infer goals, rewards, affordances, causal efficacy or learning from images/claims | Explicit competent scientific/semantic contract | Excluded unless independently established by the relevant authority |

The readiness statements above are a bounded snapshot, not owner approval.
The frontend must not consume an in-process-only path as if it were a browser
contract.

## 9. Security, privacy and operations boundary

Durable retention and query expand exposure and operational risk. A future
implementation design must address at minimum:

- producer authenticity and consumer authentication/authorization;
- least-privilege read scopes by World/run, subject, family and revision where
  needed;
- denied, expired, partial and unavailable access without leaking hidden
  identities or treating denial as source absence;
- secret handling, origin boundaries, browser storage and untrusted claim
  payloads;
- retention, deletion/legal holds, export, audit, backups and recovery;
- resource/cost budgets, operational ownership, monitoring and incident
  response;
- a threat model with independently reviewed abuse cases before shared or
  production access is authorized.

These are requirements, not selected mechanisms. Docs #167 owns the frontend
read-access security and deployment boundary. Its local-only versus
shared/production decision and competent security/operations disposition remain
open. This document must not pre-empt that work or authorize deployment.

## 10. Exact-revision readiness snapshot

This snapshot separates source implementation evidence from consumer readiness.
It was inspected against the following exact Biopeia revisions:

| Repository | Revision |
|---|---|
| `observation` | `e37f82dc0282074874ef68911eda69c3661bf9a8` |
| `world` | `e2be58700c870419a309ef3e2460b30b95c256be` |
| `lab` | `e65fa32fce2876d784aac9bd3d9ce6715fbc2f0b` |
| `environment` | `9d17ead3c2855990f9084deb6dd42aea1eafca98` |
| `embodiment` | `5a23e1fbeaa31109647aec4d4dc36eddbe0a6321` |
| `modality` | `93a4c3a4ea71dcf65269ce730aab736238fd3ea7` |
| `organism` | `0ddadac6d51ab39aeee909cb423a911b069b11dc` |

At those revisions (Biopeia `main` heads inspected on 2026-10-14), the bounded
in-process Observation plane supports current
materialization and bounded replay with explicit rebase/expiry behavior. It
does not establish durable cross-process history, a browser/network read path,
authentication, or a general query contract. World has a production causal
composition that publishes after owner adoption and World commit; the
associated integration tests exercise repeat/restore/continue behavior. This
demonstrates a bounded producer-side publication path, not durable archive
completeness or consumer access. Lab now has a bounded post-commit material-
transfer publication/association path tied to a committed World cut. The
authorization gate remains `UNSUPPORTED`; the focused verification below
confirms that the unauthorized operation is skipped, not that an experiment
was executed. This specific publication path does not establish a general
archive/read contract or durable retention.

The following verification record is a bounded test run against the exact
revisions above. It supports only the named local and integration behaviors;
it does not establish durable archive behavior, universal source completeness,
scientific validity, or a general consumer contract.

| Repository / question | Exact command from repository root | Result on 2026-10-14 |
|---|---|---|
| World post-commit publication and physical causal composition | `uv run pytest tests/integration/observation/test_world_post_commit_owner_publication.py tests/integration/physical_step/test_first_biopeia_physical_causal_step.py -q` | `16 passed` |
| Lab authorization boundary and material-transfer gate | `uv run pytest tests/integration/test_material_transfer_authorization.py tests/integration/test_operator_material_transfer.py -q` | `1 passed, 1 skipped`; the operation test is intentionally skipped because verified authorization is unsupported under Lab #330 |
| Observation in-process plane and adversarial boundary | `uv run pytest tests/test_plane.py tests/test_observational_boundary_adversarial.py -q` | `33 passed` |
| Lab passive Observation consumer and publication association | `uv run pytest tests/unit/test_observation_consumer.py tests/observation_integration/test_lab_observation_publication.py -q` | `21 passed` |

These are focused suites, not full-repository test runs. In particular, the
Lab skip is not a successful execution of a material-transfer experiment.
No experiment was run for this readiness review.

The following symbol crosswalk records the bounded implementation surface
found at those revisions. “Implemented” means the named local mechanism exists;
it does not mean the durable archive, general consumer contract, or end-to-end
capability is complete. The source packages remain authoritative for their
export status and contracts.

| Owner / capability | Verified implementation surface | Readiness for durable Observation consumers | Explicit limit |
|---|---|---|---|
| Observation plane | `ObservationPlane.publish`, `current`, `current_messages`, and `open_stream`; owner projection helpers for finite scalar field and body pose | `PARTIAL` — bounded in-process publication/replay exists | No durable cross-process history, browser/network contract, general query API, or authentication contract established |
| World publication | `publish_committed_owner_observations` and `run_scalar_sensorimotor_cycle_and_publish` | `PARTIAL` — production producer path publishes after owner adoption and committed World cut | Does not provide archive storage, consumer query, or delivery guarantees beyond the bounded in-process plane |
| Environment source | `IdentifiedFiniteResource.project_observation` | `PARTIAL` — stable resource identity and owner projection exist | Projection alone does not establish World commit or Observation retention |
| Embodiment source | `BodyPoseObservationProjection` and its owner projection path | `PARTIAL` — body/episode/morphology-bound pose projection exists | Projection is not a commit receipt and does not establish consumer delivery |
| Modality | `DimensionlessScalarFieldIdentityV1.transduce` | `IMPLEMENTED` for the narrow stateless scalar transduction | Not an Observation publisher or source-completeness contract |
| Organism | `advance_organism_from_sense_signals` | `PARTIAL` — opaque sensory input can enter the canonical Organism transition | This path does not establish an Observation publication API for Organism-owned claims |
| Lab | `MaterialTransferObservationPublication`, `LabObservationAssociation`, and the specific material-transfer operation | `PARTIAL` — bounded post-commit publication can be associated with a verified committed cut | Authorization remains `UNSUPPORTED`; no experiment was executed in the cited verification; no general Observation archive/read or operation-dispatch contract established |

This crosswalk is a source inspection, not an API approval. In particular,
`PARTIAL` and `IMPLEMENTED` above are capability-local labels only; neither
permits a frontend or Lab consumer to bypass an authorized Observation read
boundary. No durable archive, public browser API, transport, storage mechanism,
or authorization policy is implied by the named symbols.

| Repository / bounded question | Relevant existing test paths | Command from repository root | What it can establish; what it cannot |
|---|---|---|---|
| Observation: in-process plane and owner projections | `tests/test_plane.py`; `tests/test_environment_observation.py`; `tests/test_embodiment_observation.py` | `uv run --extra test pytest tests/test_plane.py tests/test_environment_observation.py tests/test_embodiment_observation.py` | Plane/projection behavior at this revision; not durable retention, browser access, or source completeness |
| World: committed owner publication and end-to-end causal composition | `tests/test_observation_publication.py`; `tests/integration/observation/test_world_post_commit_owner_publication.py`; `tests/integration/test_end_to_end_causal_cycle_acceptance.py` | `uv run --extra integration pytest tests/test_observation_publication.py tests/integration/observation/test_world_post_commit_owner_publication.py tests/integration/test_end_to_end_causal_cycle_acceptance.py` | World-side post-commit publication and composed causal path; not an archive or consumer query/read contract |
| Environment: identified resource and physical projection | `tests/test_identified_resource.py`; `tests/test_environment_physical_projection.py`; `tests/test_restoration.py` | `PYTHONPATH=src uv run pytest tests/test_identified_resource.py tests/test_environment_physical_projection.py tests/test_restoration.py` | Environment-owned resource/projection/restoration behavior; not Observation capture or cross-domain delivery |
| Embodiment: body-pose publication inputs | `tests/test_body_pose_observation_projection.py`; `tests/test_physics3d_observation_contract.py` | `uv run --extra dev pytest tests/test_body_pose_observation_projection.py tests/test_physics3d_observation_contract.py` | Embodiment projection contracts; not browser-readable consumer delivery |
| Modality: scalar-field transduction | `tests/test_scalar_field.py` | `uv run --extra test pytest tests/test_scalar_field.py` | Current scalar transduction contract; not source publication completeness or a cross-repository consumer API |
| Organism: sensory input and accepted transition | `tests/source_unit/cognition/test_sense_input.py`; `tests/source_unit/cognition/test_owner_transition.py`; `tests/source_unit/actuation/test_sensorimotor.py` | `uv run --extra dev pytest tests/source_unit/cognition/test_sense_input.py tests/source_unit/cognition/test_owner_transition.py tests/source_unit/actuation/test_sensorimotor.py` | Organism-side input/transition/action behavior; not Observation storage or transport |
| Lab: current migration boundaries around Observation | `tests/unit/test_migration_observation_facade_disposition.py`; `tests/unit/test_migration_integrated_habitat_runtime_disposition.py` | `uv run --extra dev pytest tests/unit/test_migration_observation_facade_disposition.py tests/unit/test_migration_integrated_habitat_runtime_disposition.py` | Recorded migration dispositions; not a general Lab read consumer or authorized operation-dispatch contract |

The source-level test map below remains a set of additional commands for
capability-specific review, not a claim that those additional suites ran in
this verification pass. The revisions above are an exact snapshot, not a
permanent pin; refresh them before any later readiness or implementation
decision. Owners must separately approve publication/read contracts and run
the checks required by those contracts.

## 11. ADR impact assessment and alternatives

### Alternative A — Keep ADR-0100 unchanged; retain only a bounded live plane

This has the smallest constitutional footprint and is consistent with the
approved architecture. It does not satisfy the new Owner direction for durable,
searchable historical observations across restarts and multiple consumers.

### Alternative B — Treat an Observation archive as a separate operational

capability while preserving Lab evidence custody (accepted direction)

This is the accepted conceptual direction: it can satisfy the target
requirement without making Observation scientific custodian. The Architecture
Owner has not approved the detailed durable-retention/query responsibilities,
completeness contract, policies or implementation. The next constitutional
step is to determine whether the accepted boundary needs a derived ADR or
clarification to ADR-0100; owners must still disposition source authority,
completeness claims and lifecycle policies before design approval.

### Alternative C — Put durable observational history under Lab

This would align physical custody with scientific evidence custody but would
couple ordinary Observation retention and consumers to Lab, contrary to the
approved separation of operational projection from scientific evidence
custody, and would make ordinary observation depend on the experimental
apparatus. Not recommended.

### Recommendation

Continue developing Alternative B as the accepted target direction, while
keeping the design Proposed. Do not ask the Architecture Owner to re-accept the
same conceptual separation. Before design ratification, record the competent
authority's determination of ADR impact and obtain any required derived
constitutional decision. The contract must state whether durable capture is
independent of causal commit without weakening World authority or implying
atomic publication. Until the remaining domain, lifecycle, security and
operational dispositions are complete, this document must not be marked
approved or implemented.

## 12. Staged acceptance and follow-up gates

| Gate | Required outcome | Competent disposition |
|---|---|---|
| A. Constitutional record / ADR impact | Treat the conceptual separation as accepted by the Architecture Owner; determine and record whether a derived constitutional ADR or ADR-0100 clarification is required for the detailed durable archive design | Architecture Owner; no re-acceptance of the same conceptual direction |
| B. Exact-source readiness | Approve exact revisions, owner publication paths, supported family/read capabilities and exclusions | Observation Owner with source-domain owners |
| C. Data/lifecycle contract | Accept or amend the proposed logical identity/deduplication, integrity, retention/deletion and recovery rules in §5.1; explicitly identify who may authorize logical suppression/tombstoning and its effects on source-owner records and Lab-held evidence; define completeness, time, gaps and revisions without conflating evidence admission | Observation Owner; Lab Owner for evidence separation; competent authority for suppression/tombstoning to be identified; Architecture Owner where ADR-0100 changes; Security/legal/operations for erasure/hold obligations |
| D. Security and operations | Threat model, access scopes, security/operations owner, local/shared deployment profiles | Competent Security/Operations authority; Docs #167 |
| E. Contract and implementation design | Select record, persistence, query and delivery mechanisms only after A-D; derive bounded owner issues | Relevant domain owners and reviewers |
| F. Implementation authorization | Explicit separate Owner start instruction, after all applicable readiness gates | Architecture Owner |

No implementation issue should claim authorization solely because this design
is reviewed, merged or approved. Frontend development remains deferred until
its own readiness gates and explicit start instruction are satisfied.

## 13. Acceptance criteria for this design proposal

This document is ready for review only if a reviewer can verify that it:

1. keeps source semantic authority and causal ownership in the existing owner
domains;
2. separates operational observational retention from Lab scientific evidence
custody;
3. preserves claim identity, provenance, domain time/revision, availability,
World-cut correlation and source/capture/delivery distinctions;
4. states explicit gaps and does not equate missing capture with source absence;
5. limits ingestion to owner-authorized outward publication boundaries and
does not make Modality an authority;
6. records concrete exact-revision readiness limits and does not claim
browser-accessible current support;
7. presents ADR impact, alternatives and a recommendation without accepting the
constitutional change;
8. identifies security/operations dependencies without choosing a mechanism;
9. grants no implementation, experiment, deployment, schema, API, transport or
storage authorization;
10. makes the proposed §5.1 lifecycle rules reviewable as logical semantics
while clearly leaving owner acceptance, implementation mechanisms, and
constitutional/security/legal dispositions open.

## 14. Candidate conformance tests before implementation acceptance

These are executable acceptance cases for a future local prototype; they do
not authorize implementation or select its mechanism. A prototype is not
conformant unless an independent test can demonstrate all of the following:

1. **World independence:** with Observation capture unavailable or at its
   resource ceiling, a valid World transition can still commit; Observation
   reports the capture gap separately and cannot roll back or delay the
   causal result.
2. **Retention at ceiling:** reaching the configured ceiling stops new
   capture without overwriting or pruning a previously accepted original.
3. **Visible gap:** the missed interval is reported as a gap, not as source
   absence, an empty result, or a complete history; its producer and scope
   are identified to the extent supported by the source contract.
4. **Resumption:** after capacity is available, capture resumes only for new
   eligible publications or an explicitly authorized retry of an existing
   publication. The uncovered interval remains visible unless an owner
   publication contract supplies and verifies the missing content.
5. **Integrity and recovery:** accepted originals remain byte/logically
   verifiable after process restart; corruption or missing records produce
   an explicit unavailable interval and never a fabricated repair.
6. **No accidental deletion:** neither restart, recovery, index rebuild nor
   normal resource pressure silently deletes accepted originals.

The prototype must record its declared ceiling and measurement, exact source
revisions, stop/resume events, accepted-original identities before and after
the test, World commit outcomes, and gap results. Passing these cases proves
only the tested local behavior; it does not establish unlimited retention,
scientific evidence custody, universal completeness, shared/remote security,
or production readiness.

## 15. References and related work

- [ADR-0078 — Observation is causally passive](../../adr/ADR-0078-observation-is-causally-passive.md)
- [ADR-0095 — Surviving semantic authorities](../../adr/ADR-0095-surviving-semantic-authorities.md)
- [ADR-0099 — Modality contract/library](../../adr/ADR-0099-modality-contract-library.md)
- [ADR-0100 — Observation capability and evidence custody](../../adr/ADR-0100-observation-capability-and-evidence-custody.md)
- [ADR-0102 — Lab](../../adr/ADR-0102-lab.md)
- [ADR-0110 — Repository consequence and dependency direction](../../adr/ADR-0110-repository-consequence-and-dependency-direction.md)
- [Observation Semantic Model v1](../observability/observation-semantic-model-v1.md)
- [Observation Architecture for Biopeia v1](observation-architecture-biopeia-v1.md)
- [Frontend approval and development readiness](../frontend/biopeia-frontend-approval-and-development-readiness-v1.md)
- [Observation #37 — approved read-only consumer boundary](https://github.com/biopeia/observation/issues/37)
- [Observation #38 — passive observational data lake design](https://github.com/biopeia/observation/issues/38)
- [Docs #167 — frontend read-access security and deployment boundary](https://github.com/biopeia/docs/issues/167)
