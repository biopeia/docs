---
id: design.observation.durable-archive-query-v2
title: "Biopeia Observation V2 — Durable Archive and Read Queries"
document_type: design
owner: biopeia-observation-owner
created: 2026-10-16
language: en
document_version: 1
decision_reference: ADR-0100
---

# Biopeia Observation V2 — Durable Archive and Read Queries

## 1. Purpose and boundary

This proposal completes the target design requested by [Observation #38](https://github.com/biopeia/observation/issues/38): Observation is a passive, durable, queryable archive of already-authorized Biopeia publications. It does not make a publication true, complete, scientifically admissible, or causally coherent. It does not replace Lab as scientific evidence custodian.

The accepted constitutional boundary in [ADR-0100](../../adr/ADR-0100-observation-capability-and-evidence-custody.md) separates passive runtime projection/transport from durable scientific evidence and provenance custody. **Assessment:** an operational archive remains within that boundary if it retains only source-authorized publications and capture-accounting records, exposes their limitations, and never admits evidence or creates scientific provenance.

Two dispositions were considered: (a) create a derived constitutional ADR before implementation, or (b) retain ADR-0100 unchanged and document the operational archive as a bounded design under its existing boundary. **Recommendation:** choose (b), because V2 adds retention/retrieval mechanics but assigns no evidence admission, scientific provenance, or semantic authority to Observation. This is a recommendation for Architecture Owner disposition, not a claim that the Owner has already resolved the question. If the Owner requires constitutional clarification, prepare and ratify it before implementation. Any change that makes Observation custodian/admitter of scientific evidence or changes its authority is a constitutional conflict and must return to the Architecture Owner. This assessment does not amend ADR-0100 or authorize implementation.

The existing [V1 observational data-lake proposal](observation-data-lake-v1.md) remains the conceptual predecessor. This V2 proposal narrows the architecture to implementable logical behavior and reuses the local archive already present in Observation; it selects no new public wire contract, remote service, infrastructure, or deployment.

## 2. Inputs and evidence basis

The design preserves ADR-0078 (causal passivity), ADR-0095/0099 (semantic authority and Modality boundary), ADR-0100 (evidence custody), ADR-0110 (capability boundary), and the bounded passive carriage direction in Observation #37. The exact repository snapshots reviewed for this proposal are recorded below; they are source snapshots, not claims that every consumer contract is approved.

| Repository | Reviewed revision | Relevant evidence and limit |
|---|---|---|
| Observation | `0e11ab728b4debb30e2d851ef3aa4149cc32dcb0` | PR #61 provides local append-only SQLite capture and bounded coverage accounting; PR #62 adds a read-only local reader. `receipt_sequence` is local order; source watermarks bound local delivery only. Neither PR establishes a browser historical-query contract. |
| World | `1e42240beb82f0647d89e796d4a325a240d1b147` | World owns causal commit/cut assertions. Observation must carry only explicit World-authored/verifiable association; matching tick labels alone cannot establish a shared cut. |
| Frontend | `b21748d0929e21286c179eb02ca866abb7d8a718` | Consumer readiness remains bounded to approved current-view claims. No durable archive query or history API is established by this design snapshot. |
| Organism | `823bb5effa32ff69770044eaea531a4b0f41dee3` | Source owner of Organism claims; current-main refresh includes the M3 compact ActionDomain checkpoint prototype, which does not add an Observation publication contract. |
| Embodiment | `957af224e4400fc30a9d8d78d987cec16a8e959e` | Source owner of body/morphology claims; no new source publication contract is introduced here. |
| Environment | `4eb1f8c3393a7cdbabcfaf35b8630aaf57de20c1` | Source owner of environmental claims; no new source publication contract is introduced here. |
| Modality | `62af4aba07146d5dfdc978af07bb72111112d873` | Capability/transduction lineage only; it is not an independent semantic authority. |
| Lab | `6198dff9a73e7150abedb5a30df335187092d71a` | Current `main` was rechecked after a Lab study-disposition update; the change touches study disposition/crosswalk records and consistency tests, not Observation's evidence-custody boundary. Scientific apparatus/evidence custody remains separate; archive retrieval is not evidence admission. |
| Docs | `06a2422b9cd2c1e2dafaa50014b3d45346d38959` | Includes ADR-0100, V1 proposal, security/deployment design, registry, and the merged V2 architecture proposal from PR #195. |

The source inspection distinguishes implemented behavior from proposed target behavior. In particular, the local archive and reader are not a remote deployment, a browser API, or a production retention/security policy. Observation #38 was closed administratively after the bounded reader increment; this does not mean the broader V2 target or all acceptance criteria in this proposal have been demonstrated.

Observation #40 is a separate, now-closed same-process Lab read-boundary decision. Its bounded in-process consumer disposition does not depend on durable archive queries, does not make Lab an Observation publisher, and does not authorize browser/network history access. Lab #332's limited consumer slice is likewise not a V2 archive acceptance gate. This proposal does not hold that work open or broaden its accepted scope.

## 3. Minimal record and identity model

Observation stores two logically separate things: (1) the immutable authorized semantic publication it received, and (2) an operational receipt/accounting record about that capture. Capture metadata must not be merged into, or presented as, source-owner semantics.

| Identity / time | Meaning | Authority and rule |
|---|---|---|
| Claim identity and revision | Which owner-defined proposition/revision is asserted | Semantic owner; Observation preserves it. |
| Source publication identity | Stable identity of one authorized owner publication, if that owner's contract supplies one | Publishing owner. Do not synthesize one from payload equality. |
| Observation capture identity | One local capture session/receipt and its `receipt_sequence` | Observation. Local monotonic append order only; not domain time, source causality, or a global order. |
| Source delivery sequence | Producer/delivery watermark where an approved source contract defines one | Source owner. Scope and reset are owner-defined; it can account for delivery gaps, never causal order. |
| Domain time | The time/interval the owner says the claim concerns | Source owner. Preserve as typed provenance; never replace with receipt time. |
| World causal cut | A World-authored committed-cut identity and its verification evidence, when present | World only. Preserve verbatim; no joining on tick, timestamp, run label, or arrival order. |
| Content digest | Integrity check over the exact archived representation | Observation implementation. Detects corruption/change only; not authorship, truth, or completeness. |

### Duplicates and conflicts

At-least-once delivery is allowed. If a stable source publication identity exists, repeated receipt of the same identity and identical authorized content may be exposed as repeated delivery of the same publication, while retaining capture receipt accounting. The archive must not silently erase receipt history. The same source identity with different content/provenance is a conflict: retain both captured representations when possible and report the conflict; never select by arrival order. Without a stable owner publication ID, retain each receipt and describe equivalence only as an analysis hint; payload hash equality is not semantic deduplication. No global exactly-once property is promised.

### Loss, order, and completeness

Every query and export distinguishes these facts:

1. **Persisted publication** — authorized bytes and the receipt row were committed to the local archive and pass integrity checks.
2. **Received but not persisted** — capture logic observed a publication but persistence failed. It is not in the archive; count/range/reason may be recorded only if the failure marker itself persists.
3. **Known delivery gap** — a source-owner sequence interval is explicitly known missing under that source contract.
4. **Unverifiable coverage interval** — available persisted evidence cannot prove whether publications were missed (including an uncleanly terminated session with no final watermark).
5. **Closed and verified capture** — a normal close marker and final declared local delivery bound exist, and all positions in that declared interval are accounted for as persisted records or explicit loss markers. This says nothing about publications the source never emitted or about coverage beyond that interval.
6. **Complete capture interval** — the closed interval is verified and every declared position has a persisted publication with no gap/loss. It is a narrow capture statement, not producer-wide completeness, causal completeness, or scientific completeness.

These are orthogonal to World commit status. `receipt_sequence` orders accepted local archive rows; source sequence can account for a delivery stream; neither orders World events. Only an explicit World-verified causal-cut reference can establish association with a committed cut. If the owner publication lacks it, the relation is “not established,” not inferred. A set of individually cut-associated claims is not necessarily an atomic or complete cross-domain snapshot unless World supplies an explicit shared-cut verification contract.

PR #61 implements bounded local accounting, including persisted rows, received-not-persisted outcomes, durable gap markers, open/unverifiable intervals, closure verification, and stricter interval completeness. PR #61 configures SQLite rollback-journal `DELETE`, `synchronous=EXTRA` (verified as effective value 3), and foreign-key enforcement; it tests process interruption and injected capacity/write/marker failures. Durability still depends on the OS, filesystem, SQLite VFS, storage controller and hardware honoring SQLite's commit semantics; this is not proof against physical power loss or hardware failure. Disk-full or write failure cannot be made durable by Observation; if it cannot persist a loss/close marker, recovery must leave the session open/unverified rather than upgrade it to complete. The implementation's payload budget is not a physical disk quota.

## 4. Storage and query architecture

### First profile: bounded local archive

Reuse the PR #61 SQLite append-only archive as the first local operational archive profile. Keep the existing semantic plane and archive separate. Use one local capture writer, immutable source payload/receipt rows, and rebuildable query indexes. The current schema and `query` behavior are implementation evidence, not a newly approved cross-domain schema/API. This is sufficient for bounded single-process local persistence and paginated local inspection; it is not selected as a universal multi-writer or distributed store.

No second database, event bus, service, cloud object store, remote API, compression, automatic expiry, silent pruning, or retention replication is introduced. If measured needs exceed the local profile, record a separate architecture decision with operational/security evidence rather than prebuilding speculative infrastructure.

### Logical read operations

Consumers need the following logical read capabilities; exact request/response schemas, transport, authentication and deployment remain outside this proposal and are gated by Docs #167 and owner contracts:

| Query | Minimum result |
|---|---|
| Capture/run catalog | Capture-session identity; World/run identity only where explicitly supplied and verified; source revisions; receipt-time bounds; session status and coverage summary. Do not derive a World run identity from a local capture ID. |
| Publications by owner family / subject / revision / domain-time range | Paginated authorized claims, source provenance, local receipt identity/order, content integrity status and availability/completeness status. Filters are exact, not inferred. |
| Capture coverage for a session and declared interval | Persisted positions, received-not-persisted outcomes, known gaps, unverifiable intervals, close/verification status, and explicit scope of the claim. |
| Publications associated with an exact World cut | Only claims carrying an explicit World-authorized and verified association to that cut; no tick-based join. Return partial/missing families rather than fabricating a complete scene. |
| Exact publication inspection | Original owner claim and provenance plus separate Observation capture metadata and any explicit owner-authored relations. |

For each unsupported filter or missing identity, the read result must say unsupported/not established/unavailable rather than silently return an apparently complete empty result. Queries are read-only and cannot annotate, correct, acknowledge into source state, or mutate World.

### Consumer scope

Frontend requires current view plus bounded history, provenance inspection, and truthful stale/unavailable/incomplete states. Run history consumers require exact run/session catalog and scoped publication/coverage queries. Observation analysis requires paginated owner-family/time/subject selection with provenance and capture-quality metadata. Lab may use archive reads as inputs, but must separately admit and preserve scientific evidence under Lab custody. Spatial or sensorimotor displays remain possible only for exact authorized claims and explicit World association; the archive cannot join claims into a scene.

## 5. Retention, classification, security, audit, recovery

- **Retention:** PR #61 has a local bounded payload budget and no age-based eviction. Preserve that conservative local behavior; do not generalize it as a Biopeia-wide retention policy. On capacity exhaustion, stop accepting new archive payloads, surface received-not-persisted where observable, and preserve previous durable rows. Never affect source or World commit. No deletion, erasure, expiry, backup or cross-run purge policy is chosen here.
- **Classification:** preserve source-provided classification and provenance. Observation must not lower or reinterpret sensitivity. If a source has no approved classification/access rule, serving beyond the local operator boundary is not authorized by this design.
- **Access:** the current local-only read path and filesystem permissions are bounded implementation facts, not a production authorization policy. No browser/network/shared-host access is approved here. Docs #167 must resolve threat model, trust boundaries, identity, authorization, deployment, audit access and operational controls before any shared or remote serving.
- **Audit:** retain capture lifecycle and loss/coverage outcomes as operational accounting. It is not tamper-proof scientific provenance, an evidence chain, or a substitute for Lab records. No administrator-edit or annotation channel is implied.
- **Recovery:** on reopen, verify archive structure and record digests; reconstruct only derived indexes. Preserve interrupted sessions as open and coverage-unverified unless durable terminal markers prove closure. Never infer absent rows, repair source sequences, or synthesize a terminal marker. Corrupt records are reported/quarantined from reads; they are not silently dropped or rewritten. A failed recovery must fail closed for affected queries while preserving unaffected verified records.
- **Physical durability limit:** a successful SQLite commit is the strongest local statement supported by the configured transaction and platform. Observation cannot promise persistence across hardware/controller/filesystem failures outside SQLite's guarantees; recovery must not claim a write that was not verified after reopen.

## 6. Responsibility matrix

| Responsibility | Owner | Explicitly not owned by |
|---|---|---|
| Claim meaning, identity, revision, domain time, publication ID and source-stream boundaries | Organism / Embodiment / Environment / World as applicable; Modality supplies declared transduction lineage | Observation, Frontend, Lab |
| Causal commit and cut association | World | Observation's receipt order or consumer joins |
| Authorized publication capture, local receipt identity/order, payload integrity, capture loss/coverage, local archive and read-only query implementation | Observation | Producers' meaning; World causality; Lab evidence admission |
| Historical presentation and explicit incomplete/stale states | Frontend | Frontend must not infer missing source facts or create joins |
| Study protocol, evidence selection/admission, scientific provenance and conclusions | Lab / designated scientific authority | Observation's durable archive |
| Shared/remote security and deployment decision | Docs #167 security/operations authority and relevant owners | This design or UI code |
| Architecture boundary/ADR change | Architecture Owner | CI, implementation PR, or this proposal |

## 7. Exact-source readiness delta for Observation #37

Observation #37 remains the exact-source Frontend consumer-readiness issue; this document does not close it or substitute for the required Observation-owner disposition and independent review. The following consumer matrix is a readiness delta against its seven-screen product specification, not an approval to implement those screens:

| Frontend screen / capability | Current source-backed status | Durable V2 / readiness gap |
|---|---|---|
| Worlds & Runs | **Not established** as a durable World/run catalog. Local capture sessions are Observation capture identities, not World/run identities. | Needs an owner-authorized run/catalog projection and stable references; do not derive them from capture IDs. |
| World Overview | **Partial** for the bounded local current-view claim set; **not established** for browser-accessible durable history. | Needs a stable read contract and explicit stale/incomplete state across capture sessions. |
| Spatial Explorer | **Partial** for source-authored static projections and the dynamic Embodiment link-pose projection explicitly associated by World with a verified cut. **Not established** as a complete or atomic multi-owner scene. | Render only present claims and their explicit references. Missing scene elements remain unavailable; no inferred placement, geometry, or cross-domain completeness. |
| Causal Timeline | **Not established** as causal history or browser replay. Local `receipt_sequence` is only archive receipt order. | Requires explicit World cut assertions and a consumer read path; presentation order must not be labeled causal replay. |
| Sensorimotor Trace | **Not established** for a complete, linked sensorimotor claim graph. | Requires explicit typed owner links and access to all relevant authorized claims; no heuristic joins. |
| Claim Inspector | **Partial** for claims available in the current local view; durable cross-restart/browser inspection is **not established**. | Requires stable claim/publication references and provenance-preserving history queries. |
| Connection & Access | **Partial** for bounded local-process availability; shared/remote authorization is **not authorized**. | Docs #167 remains open for future shared/remote security and deployment; local-only readiness must stay distinct. |

Based on the exact source revisions in §2 and the merged capture-integrity increment:

| Readiness dimension | Current bounded evidence | V2 target / remaining gap |
|---|---|---|
| Passive authorized capture and local durable rows | Implemented locally by Observation PR #61 | Capture failure/coverage distinctions are present locally; verify owner-specific publication IDs, source ranges and closure declarations only where contracts define them. |
| Local ordering and recovery accounting | PR #61 implements receipt order and capture sessions; source sequence is explicitly local delivery accounting | No causal inference. Confirm per-source reset/continuity semantics; unknown intervals remain unverifiable. |
| World causal association | World `observation_publication` / `spatial_projection` paths provide explicit verified association for the bounded render projections inspected at current `main` | This evidence is projection-specific, not a universal cross-domain join or complete snapshot contract. The local reader has no World-cut filter; such a query remains unsupported until an explicit source-authored association is represented and exposed for that query. Never infer from matching labels. |
| Queryable durable history | PR #62 implements a read-only local `ArchiveReader` over archive schema v2/v3 | `query_page` supports exact owner, family, subject, revision and domain-time filters with local receipt-sequence pagination; `capture_catalog`, `capture_coverage` and `integrity_check` are status-bearing/read-only. Original payload, decoded publication, digest and capture metadata are returned separately. Unsupported filters, unsupported capture metadata, missing capture IDs and unasserted subject identity are explicit. This remains a local Python reader, not a browser/HTTP history contract. |
| Frontend consumer readiness | Current-view local reads plus source-authored static geometry and explicitly World-associated dynamic link-pose rendering are present in current source | The screen matrix above is not a readiness approval. Durable browser history, browser archive access, and a complete/atomic multi-owner scene are not established. |
| Lab same-process use | Observation #40 and Lab #332 disposition the bounded read-only same-process slice | Independent of durable archive/history queries; no automatic evidence admission. Lab retains its own evidence references and custody under ADR-0100. |
| Security/retention/operations | Local prototype bounds only | Docs #167, classification/access authority, deletion/retention and shared deployment remain unresolved. |

The V2 target does not add producer fields or transport behavior to make a row appear ready. Each publisher must separately define stable identity, source delivery accounting and any cut relationship within its own authority. Consumers must preserve unsupported and unverified states.

### Current-source refresh (2026-10-16)

The source revisions in §2 are the exact local `main` heads inspected for this refresh. Relevant production paths were checked directly, in addition to comparing current revisions with the earlier #37 inventory. This is source inspection, not a new browser acceptance. PR #61's accepted capture/recovery behavior was not revalidated here; PR #62's reader tests were inspected in source, and the previously recorded focused result was 9 passing tests (not rerun for this documentation update).

- Observation `src/observation/archive.py` (blob `a0f2a58f250c109b0d59b40a6457160e50adb326`), `src/observation/capture.py` (`f7c82943e990537d5cd8f2101f1b1a862e32da22`), `src/observation/http_bridge.py` (`470944ca44b0b0d56513fc934c65a55d20cef861`) and `tests/test_archive_reader.py` (`cc047971feb47fa838c9d965b07ae08c0efa7e31`) were inspected. `ArchiveReader` opens an existing regular non-symlink archive in SQLite read-only/query-only mode; it accepts supported schema v2/v3 and fails explicitly on unsupported schema or missing capture metadata. `query_page` paginates by local `receipt_sequence`, applies exact owner/family/subject/revision/domain-time comparisons over decoded archived publications, verifies payload digest/size and indexed family/authority consistency, and returns original payload/provenance plus separate capture receipt fields. It does not create a World-tick filter; unsupported filters return `unsupported_filter`. Capture catalog and coverage are status-bearing, and reads roll back any read transaction without changing the archive. This local reader is not exposed through the HTTP bridge. The capture path remains bounded, opt-in, starts from the live plane watermark without backfill, and does not participate in source-publication success.
- World `src/world/observation_publication.py` (`6ba67ea351b111110126d7ab8a7d5cc9702e7a4a`) and `src/world/spatial_projection.py` provide a source-owned path for associating render projections with a verified committed cut and the exact Embodiment checkpoint reference. This is stronger than matching tick labels, but is not a general guarantee that arbitrary owner claims form a complete, atomic multi-domain snapshot.
- Frontend `src/spatial-render-controller.js` (`eaca2d0614873d3de6dd2f00362ec821671dd42a`) and `src/views.js` (`d553ad7e04d5e87e09a16da9223626e08127122d`) render source-authored static morphology/Environment projections and dynamic Embodiment link-pose claims with their explicit World association. This establishes a bounded render path; it does not authorize inferring missing bodies, joints, environmental geometry, or a complete scene.

This changes the #37 readiness finding for Spatial Explorer from “dynamic scene not established” to “partial dynamic rendering is source-backed for the explicit World-associated Embodiment link-pose projection.” The Observation reader updates local archive-query capability from “not implemented” to “implemented locally.” It does not change #37's required Observation-owner disposition, authorize a new archive API, or demonstrate browser history/replay. Lab main was rechecked at `4234ff0f5a182e587b5fc4eb66f837dcdab9912a`; this is not evidence that Lab consumes the durable archive or that Observation holds scientific custody. Organism main advanced from `cedce522696f7d5a0ba458018eebd61a18972a4c` to `823bb5effa32ff69770044eaea531a4b0f41dee3` during this refresh. The delta adds an M3 compact ActionDomain checkpoint/history prototype; it does not change the Observation publication/read boundary assessed here, and is not treated as an Observation contract or consumer-readiness evidence.

## 8. Incremental plan and acceptance

1. **Design disposition (this deliverable):** review the bounded archive/query design, ADR-0100 assessment, and responsibility split. No code or publication contract changes follow merely from document approval.
2. **Completed bounded increment — local read-only reader (Observation PR #62):** the existing archive reader supports receipt-sequence pagination; exact owner, family, subject, revision and domain-time filters over archived publication data; original payload/provenance with separate receipt metadata; capture catalog/coverage; integrity checks; and explicit unsupported, absent-identity, or unverifiable results. It adds no archive schema fields or producer contracts, exposes no HTTP/browser API, and makes no cross-run or causal joins. PR #62 implementation and its focused test result are evidence for this bounded slice only; they do not close the wider V2 requirements. No further implementation is authorized by this proposal alone.
3. **Owner-specific source/cut readiness:** each producer owner defines and tests any publication ID, source sequence/watermark, cut association, or explicit absence contract it owns. World alone tests cut validity. Observation consumes only approved records; no implementation can manufacture missing fields.
4. **Security and shared access gate:** Docs #167 and competent security/operations authority decide identity, authorization, classification, audit, deployment, backup/deletion and capacity operations before exposing data beyond local use.
5. **Consumer integration:** Frontend uses approved read contracts. Browser acceptance covers multiple sessions, explicit incomplete/stale state, provenance, and refusal to show a causally coherent combined scene without World verification. The already-dispositioned #40/#332 same-process Lab slice proceeds independently; any future Lab use of durable history needs its own consumer acceptance and separate evidence admission.

### Acceptance evidence required for Issue #38

- Contract examples cover persisted, received-not-persisted, known-gap, unverifiable, closed-verified, complete-interval, duplicate, conflicting identity, interrupted session, capacity exhaustion, corruption, and unsupported query cases.
- A consumer can retrieve a publication and its provenance without write authority; result distinguishes local receipt sequence from source sequence and World cut.
- Any future World-cut query returns only explicitly verified associations and does not infer from matching tick/run/time labels; the current local reader reports World-cut filtering as unsupported rather than implying that it can perform this query.
- Restart after a missing close marker leaves capture incomplete/unverifiable; no damaged or absent row is represented as persisted.
- Query behavior meets Frontend/run-history/analysis minimums without adding a remote service or broad API surface before security disposition. The present local reader does not meet all consumer/history requirements; unsupported World-cut and browser-history queries remain explicit gaps.
- Retention/classification/access/recovery operational owners and limitations are explicit; no claim of scientific custody transfers from Lab.
- Observation #37 exact-source readiness is reconciled by its competent owners; Docs #167 security/access dependencies are dispositioned for the requested consumer profile.
- PR/CI and independent review validate the exact documentation candidate. Owner acceptance remains separate from CI and PR merge. Observation #38 has been closed administratively; that closure does not mean the broader V2 architecture or acceptance criteria have been fully demonstrated or accepted. Remaining work is tracked by its relevant active issues and dependencies.

## 9. Decisions still open

These are bounded decisions, not requests to reopen the architecture direction:

1. Observation and producer owners: which currently published families provide stable publication identity and meaningful source sequence/watermark semantics, and which remain explicitly unverifiable?
2. World: what exact existing or minimal World-authored record proves that a publication belongs to a committed cut, and whether such association is individual or an explicitly complete shared projection?
3. Frontend consumer readiness: Observation owner disposition and author-distinct independent review of the exact-source #37 matrix above; until then it is a proposed readiness delta, not an approved client contract.
4. Security/operations authority under Docs #167: whether/when history may be served to Frontend outside the local process boundary and under what classification, access, audit, backup and deletion rules. Docs #167 still leaves shared/remote deployment unauthorized; it does not block the local-only reader increment.
5. Lab: any future durable-history consumer requirements and the distinct Lab evidence-admission reference, without making Observation the custodian. This is not a blocker for the #40 same-process slice already dispositioned.
6. ADR-0100 remains the governing boundary. The bounded local reader is assessed as a passive operational archive and does not require a derived constitutional ADR or amendment. Revisit only if a future proposal changes evidence custody, admission, semantic authority, or another constitutional boundary; none is authorized here.

No human decision is requested for routine technical choices inside the bounded design. The remaining items require the listed authorities because they concern source-owned contracts, World causal authority, security/access, or Lab evidence custody. The bounded local reader is implemented; this proposal does not authorize further code changes or any public/remote exposure. Observation #38's administrative closure is not evidence that every V2 criterion is satisfied.

## References

- [ADR-0078 — Observation is causally passive](../../adr/ADR-0078-observation-is-causally-passive.md)
- [ADR-0095 — Surviving semantic authorities](../../adr/ADR-0095-surviving-semantic-authorities.md)
- [ADR-0099 — Modality contract/library](../../adr/ADR-0099-modality-contract-library.md)
- [ADR-0100 — Observation capability and evidence custody](../../adr/ADR-0100-observation-capability-and-evidence-custody.md)
- [ADR-0110 — Repository consequence and dependency direction](../../adr/ADR-0110-repository-consequence-and-dependency-direction.md)
- [Observation #38](https://github.com/biopeia/observation/issues/38)
- [Observation #37](https://github.com/biopeia/observation/issues/37)
- [Docs #167 — Frontend security and deployment](https://github.com/biopeia/docs/issues/167)
- [Observation V1 — Passive Observational Data Lake](observation-data-lake-v1.md)
