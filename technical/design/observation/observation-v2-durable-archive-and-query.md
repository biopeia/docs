---
id: design.observation.durable-archive-query-v2
title: "Biopeia Observation V2 — Durable Archive and Read Queries"
document_type: design
owner: biopeia-observation-owner
created: 2026-10-16
language: en
document_version: 2
decision_reference: ADR-0100
---

# Biopeia Observation V2 — Durable Archive and Read Queries

## 1. Purpose and boundary

This proposal completes the target design requested by [Observation #38](https://github.com/biopeia/observation/issues/38): Observation is a passive, durable, queryable archive of already-authorized Biopeia publications. It does not make a publication true, complete, scientifically admissible, or causally coherent. It does not replace Lab as scientific evidence custodian.

The accepted constitutional boundary in [ADR-0100](../../adr/ADR-0100-observation-capability-and-evidence-custody.md) separates passive runtime projection/transport from durable scientific evidence and provenance custody. **Assessment:** an operational archive remains within that boundary if it retains only source-authorized publications and capture-accounting records, exposes their limitations, and never admits evidence or creates scientific provenance.

Two dispositions were considered: (a) create a derived constitutional ADR before implementation, or (b) retain ADR-0100 unchanged and document the operational archive as a bounded design under its existing boundary. **Owner direction for this bounded work:** use ADR-0100 without a derived constitutional ADR while Observation remains a passive archive and does not admit or custody scientific evidence. This does not amend ADR-0100. Any proposal that changes Observation's authority or transfers evidence admission/custody remains out of scope and requires a constitutional decision.

The existing [V1 observational data-lake proposal](observation-data-lake-v1.md) remains the conceptual predecessor. This V2 proposal narrows the architecture to implementable logical behavior and reuses the local archive already present in Observation; it selects no new public wire contract, remote service, infrastructure, or deployment.

## 2. Inputs and evidence basis

The design preserves ADR-0078 (causal passivity), ADR-0095/0099 (semantic authority and Modality boundary), ADR-0100 (evidence custody), ADR-0110 (capability boundary), and the bounded passive carriage direction in Observation #37. The original design snapshots are recorded below; they are source snapshots, not claims that every consumer contract is approved. The current Observation reader and Frontend-readiness status are refreshed after PRs #62/#63 and Docs #197 in the dated updates below.

| Repository | Reviewed revision | Relevant evidence and limit |
|---|---|---|
| Observation | `6a3bf96c90c78c13af69c6e98dc19569afd5c629` | At this design baseline, PR #61 had merged a local append-only SQLite archive and capture coverage accounting. `receipt_sequence` is local order; source watermarks bound local delivery only. The later reader increment is recorded in the 2026-10-16 update below. |
| World | `1e42240beb82f0647d89e796d4a325a240d1b147` | World owns causal commit/cut assertions. Observation must carry only explicit World-authored/verifiable association; matching tick labels alone cannot establish a shared cut. |
| Frontend | `b21748d0929e21286c179eb02ca866abb7d8a718` | Consumer readiness remains bounded to approved current-view claims. No durable archive query or history API is established by this design snapshot. |
| Organism | `cedce522696f7d5a0ba458018eebd61a18972a4c` | Source owner of Organism claims; no new source publication contract is introduced here. |
| Embodiment | `957af224e4400fc30a9d8d78d987cec16a8e959e` | Source owner of body/morphology claims; no new source publication contract is introduced here. |
| Environment | `4eb1f8c3393a7cdbabcfaf35b8630aaf57de20c1` | Source owner of environmental claims; no new source publication contract is introduced here. |
| Modality | `62af4aba07146d5dfdc978af07bb72111112d873` | Capability/transduction lineage only; it is not an independent semantic authority. |
| Lab | `6198dff9a73e7150abedb5a30df335187092d71a` | Current `main` was rechecked after a Lab study-disposition update; the change touches study disposition/crosswalk records and consistency tests, not Observation's evidence-custody boundary. Scientific apparatus/evidence custody remains separate; archive retrieval is not evidence admission. |
| Docs | `fa9d32abb8fd3081c25eaac65417e0247dcac51a` | Includes ADR-0100, V1 proposal, security/deployment design, registry, and the merged V2 architecture proposal from PR #195. |

The source inspection distinguishes implemented behavior from proposed target behavior. In particular, the local archive is not a remote deployment, a browser API, or a production retention/security policy.

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

Observation #37 is closed after the Owner accepted the bounded exact-source consumer-readiness inventory. That disposition is limited to readiness assessment; it is not a browser-history contract, approval of Spatial Visualization V1, remote access authorization, or scientific acceptance. The following consumer matrix remains a bounded readiness inventory against its seven-screen product specification, not an approval to implement those screens:

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
| World causal association | World `observation_publication` / `spatial_projection` paths provide explicit verified association for the bounded render projections inspected at current `main` | This evidence is projection-specific, not a universal cross-domain join or complete snapshot contract; query only exact verified associations. |
| Queryable durable history | SQLite archive query pages by local receipt cursor; the read-only reader supports only its declared filters | The Python reader exposes `query_page(filters, after_receipt_sequence, limit)`, `capture_catalog()`, `capture_coverage()` and `integrity_check()`; the local HTTP bridge exposes bounded current-view `GET /v1/current`, not durable history. No public history API or browser transport is approved; query shapes above are logical requirements only. |
| Frontend consumer readiness | Current-view local reads plus source-authored static geometry and explicitly World-associated dynamic link-pose rendering are present in current source | The screen matrix above is not a readiness approval. Durable browser history, browser archive access, and a complete/atomic multi-owner scene are not established. |
| Lab same-process use | Observation #40 and Lab #332 disposition the bounded read-only same-process slice | Independent of durable archive/history queries; no automatic evidence admission. Lab retains its own evidence references and custody under ADR-0100. |
| Security/retention/operations | Local prototype bounds only | Docs #167, classification/access authority, deletion/retention and shared deployment remain unresolved. |

The V2 target does not add producer fields or transport behavior to make a row appear ready. Each publisher must separately define stable identity, source delivery accounting and any cut relationship within its own authority. Consumers must preserve unsupported and unverified states.

### Current-source refresh (2026-10-16)

The source revisions in §2 are the exact `main` heads inspected for this refresh. Relevant production paths were checked directly, in addition to comparing current revisions with the earlier #37 inventory. This is source inspection, not a new test run or browser acceptance; PR #61's accepted capture/recovery implementation and tests were not repeated.

- Observation `src/observation/archive.py` (blob `a0f2a58f250c109b0d59b40a6457160e50adb326`), `src/observation/capture.py` (`f7c82943e990537d5cd8f2101f1b1a862e32da22`) and `src/observation/http_bridge.py` (`bbe207e9097cb91d7727b94570d7ffa6759555c7`) still implement the local append-only archive and opt-in bounded capture path. `receipt_sequence` remains archive-local. Capture starts from the live plane watermark, is not backfilled, and does not participate in source-publication success. The HTTP bridge remains a local-only current-view bridge; it is not a durable-history endpoint.
- World `src/world/observation_publication.py` (`6ba67ea351b111110126d7ab8a7d5cc9702e7a4a`) and `src/world/spatial_projection.py` provide a source-owned path for associating render projections with a verified committed cut and the exact Embodiment checkpoint reference. This is stronger than matching tick labels, but is not a general guarantee that arbitrary owner claims form a complete, atomic multi-domain snapshot.
- Frontend `src/spatial-render-controller.js` (`eaca2d0614873d3de6dd2f00362ec821671dd42a`) and `src/views.js` (`d553ad7e04d5e87e09a16da9223626e08127122d`) render source-authored static morphology/Environment projections and dynamic Embodiment link-pose claims with their explicit World association. This establishes a bounded render path; it does not authorize inferring missing bodies, joints, environmental geometry, or a complete scene.

This changes the #37 readiness finding for Spatial Explorer from “dynamic scene not established” to “partial dynamic rendering is source-backed for the explicit World-associated Embodiment link-pose projection.” Docs PR #197 records the exact-source readiness inventory; the Owner accepted that inventory as a readiness assessment, not as a client contract. Observation #37 is closed on that limited basis. The disposition does not authorize a new archive API or demonstrate browser history/replay, and it does not approve a complete coherent scene.

### Local archive reader status (2026-10-16)

Observation PR #62 is merged on `main` at `0e11ab728b4debb30e2d851ef3aa4149cc32dcb0`. Source inspection of `src/observation/archive.py` (blob `a0f2a58f250c109b0d59b40a6457160e50adb326`) confirms that `ArchiveReader` opens the SQLite file read-only (`mode=ro` and `query_only`), verifies record integrity before returning original payload bytes and decoded owner publication, and supports pagination using the archive-local `receipt_sequence`. The exact supported filters are owner, family, subject, revision, and domain time where the stored publication metadata contains those identities. It also exposes status-bearing capture catalog and coverage results, plus integrity checking; unsupported filters, malformed identities, missing files and corrupt rows are not represented as successful empty history.

The reader does not add or infer metadata, does not join claims by World tick/run/time, and does not provide an HTTP endpoint, browser history, remote/shared access, receipt-time filter, capture-scoped publication filter, or a general World-cut filter. Pagination is in local receipt order; it is not a causal cursor. The capture catalog/coverage describes persisted local accounting, not source-wide publication completeness. These restrictions remain true at the current source below.

Observation PR #63 merged on `main` at `29a6ba7a8cdd9772eec0e40087f748a7b7df2444` (candidate `b416a1db5d33452cf1af5f171accc838b689ceb3`). Its diff adds an integration test exercising the existing ObservationPlane-to-capture-to-ArchiveReader path; it does not change the reader or capture contract. Against the current Observation `main`, `uv run pytest -q tests/test_archive_reader.py` passed **10 tests** and `uv run pytest -q` passed **188 tests** on 2026-10-16. These test outcomes cover repository behavior on that revision only; they do not establish a historical consumer, remote access, or full V2 acceptance.

**Owner-specific readiness delta from current source inspection:** the current Observation adapters include Environment static scene/resource/finite-scalar claims and Embodiment morphology/reserve/body-pose/render-link-pose claims; there is no Organism publication adapter in the inspected Observation source. This is a statement about the inspected adapter set, not proof that no other approved route can publish Organism-owned claims. The adapters preserve owner-scoped subject identities and owner contract revisions where defined. A generic stable source-publication ID or owner sequence is not established across these families; `source_sequence` in the archive is the Observation plane's local delivery sequence recorded for a capture, not a producer-authored identity or cross-restart continuity guarantee. Domain-time metadata is family-specific and may be absent. The Embodiment render-link-pose adapter retains a World cut identity, exact Embodiment checkpoint reference, and candidate digest; Observation structurally validates the bounded payload but explicitly does not itself verify World causality. Do not generalize this association to unrelated families or interpret it as a universal World-cut query capability. Relevant current source blobs: `src/observation/embodiment.py` (`db720b00971359e30491abf314aac1f8db5ff2db`) and `src/observation/environment.py` (`e4259490cc4a9b6ae45b8e987f7913371d33237b`).

**World historical-cut readiness disposition (2026-10-16):** World #176's source-owned design review against `world/main@c165acb21794ec3f72677a25b2b4947142e15e15`, its two focused regression tests (`2 passed, 61 deselected`), and an independent technical review conclude that existing contracts do **not** provide a consumer-verifiable historical association between a committed cut and a durably archived Observation publication. World retains per-cut descriptors, but `committed_cut_for` verifies only the active cut; publication associations are transient and do not prove archive receipt membership or projection-set completeness. The focused tests establish present-cut binding and fail-closed behavior after a rejected transition only. They do not establish historical lookup, archived membership, or complete/atomic multi-owner coverage. See [World #176 disposition](https://github.com/biopeia/world/issues/176#issuecomment-6222287876), [focused-test supplement](https://github.com/biopeia/world/issues/176#issuecomment-6222294861), and [independent review](https://github.com/biopeia/world/issues/176#issuecomment-6223164149). World #176 was closed after this review; its [closure comment](https://github.com/biopeia/world/issues/176#issuecomment-6223184625) explicitly records that closure completes only the design investigation and does not accept a new contract or authorize implementation. Do not infer membership from equal tick, run, timestamp, checkpoint reference, or local receipt order. A durable World-authored association would be a new cross-domain contract and is outside current implementation authorization; this negative readiness conclusion does not block retrieval of locally archived original publications.

### O1–O5 evidence refresh (2026-10-16)

This refresh records the bounded local archive and reader against Observation `572c86f8fce66a73cc3899a4a929448416f1e6bf`, Frontend `b21748d0929e21286c179eb02ca866abb7d8a718`, Docs design baseline `7642ebe711de047bc71ea4e035ed6b935a4c8a28`, and canonical World `origin/main@c165acb21794ec3f72677a25b2b4947142e15e15`. It does not elevate the source snapshots, unit tests, or a bounded smoke run into V2 acceptance.

| Criterion | Evidence and outcome | Limit / next proof |
|---|---|---|
| O1 — authentic capture, reopen and query | `.local/m2-observation-runtime-20261016/run-real-001/archive/observations.sqlite` reopens through `ArchiveReader`; SQLite integrity is `ok`. Capture `93b11801-11e1-4825-97fc-3e70f02f6a01` is stopped with declared final local source sequence 11; persisted positions are 1–11, with no recorded received-not-persisted result, known gap, or unverifiable interval. Coverage is `closed_verified` / complete only for this declared local interval. The World manifest records commit tick 3. The archive contains 11 publications: 3 `body_pose`, 3 `finite_scalar_field`, 3 `render_link_pose`, 1 `render_scene`, and 1 `render_morphology`; page size 4 returned 4+4+3. | **Observed bounded artifact, not reproducibly invoked.** `runtime-capture.json` is empty. Read-only audit found `/tmp/biopeia-m2-runtime-capture-current.py`, whose logic creates a fresh runtime and capture adapter for three cycles, but its required argv (profile, state root, archive path) are not recorded. Shell history and tracked workspace scripts do not establish the invocation or connect ordinary `make run` to durable capture. Do not claim the file is reproducibly generated by `make run`, nor that it demonstrates more than three cycles. |
| O2 — catalog, filters, original/provenance, coverage | Current `ArchiveReader` is read-only and exposes `query_page(filters, after_receipt_sequence, limit)`, `capture_catalog()`, `capture_coverage()` and `integrity_check()`. Supported exact filters are owner/family/subject/revision/domain time where metadata exists. Original payload/provenance is returned without semantic reinterpretation. | **Local reader implemented; consumer needs partial.** No receipt-time or capture-scoped publication filter, arbitrary time range, World-cut query, or history HTTP/browser API. Missing/unsupported identities must stay explicit, not turn into complete-looking empty results. |
| O3 — causal association / completeness | World `origin/main@c165acb` and World #176 disposition establish that present-cut association is active-cut scoped and transient; it does not prove durable archive receipt membership or projection-set completeness. Observation receipt sequence is local accounting only. | **Historical coherent-cut query unsupported by current contracts.** No join by tick, run label, timestamp, checkpoint, or arrival order. A durable World-authored association is a distinct cross-domain contract, not part of this increment. |
| O4 — consumers and access | Frontend `b21748d` exposes current-view reads (`GET /api/observation/current`), not archive history. Observation #37 is closed as a bounded readiness inventory; Docs #167 remains open. Local reader access is not remote/browser access. | **No archive-backed browser or multi-run history acceptance.** The user-reported `make view` attempts failed in the supplied runs: first `EADDRINUSE` on 4173, then active bridge HTTP 403 on 4174. These are operational observations, not proof of archive corruption or an Observation V2 consumer path. |
| O5 — SQLite limits and operations | Artifact SHA256 `fab5d55f03ce34373f7490d1ec8ad9406f9dc50579eb7aa23e6b49fe5da117ec`; 28 pages × 4 KiB, freelist 0, `DELETE` journal; integrity `ok`. Writer config sets `synchronous=EXTRA` and foreign keys. Existing capture tests cover injected capacity/write/marker failures, interruption and ambiguous commit recovery. A local raw-SQL microbenchmark on this 11-row file (1,000 repetitions) reported count p50/p95/p99 4.39/4.75/7.44 µs, family 4.72/4.95/8.08 µs, and receipt-page 5.37/5.66/8.86 µs. | **No scale or physical-failure guarantee.** This is not end-to-end query timing, disk-full hardware testing, power-loss evidence, or a basis for extrapolating throughput. Index inspected is `(family, receipt_sequence)`; subject/revision/domain-time may scan. Payload-byte budget is not a physical disk quota. No measured need justifies a second DB, compression, or distributed infrastructure. |

The O1 artifact demonstrates that a bounded capture can be reopened and queried; it does **not** establish a durable, documented, reproducible operator path. The next candidate implementation increment is a reproducible, auditable, opt-in local capture invocation (record exact command/arguments, source revisions, profile identity, archive location, stop outcome and artifact digest), without changing producer contracts or adding network access. Before implementation, confirm that the existing local capture adapter can be composed with the approved runtime entry point without changing publication success semantics. If it cannot, record the precise integration boundary and keep the feature opt-in; do not silently make `make run` start archive capture. Acceptance evidence should include a bounded real session, archive reopen, complete pagination, and interruption/recovery with an explicit non-complete outcome. This design proposal does not authorize that runtime change: it must be separately scoped against the existing issue/authorization before implementation. It is not permission to add HTTP/browser history, infer World-cut joins, or change storage infrastructure.

## 8. Incremental plan and acceptance

1. **Design and local-reader increments — implemented:** the bounded archive design is recorded here; Observation PR #61 implements capture durability/accounting, PR #62 implements the read-only local reader, and PR #63 adds an integration test for that existing path. This does not complete Observation V2 or authorize remote consumers.
2. **Candidate next increment — reproducible local runtime capture, not a new cut contract:** the reader and bounded metadata-supported query path already exist. This proposal identifies one traceable, opt-in local runtime capture invocation with exact inputs and artifact identity, followed by archive reopen and query. Preserve source publication behavior if capture/storage fails and leave interrupted coverage unverified. This remains a proposed scope, not an implementation authorization; scope it against the governing issue/authorization before code changes. Do not infer World-cut history; World #176's negative design conclusion remains in force. Any durable World-authored association is separately scoped and requires a distinct cross-domain decision before implementation.
3. **Consumer readiness:** Observation #37's bounded inventory is complete and closed. Keep current-view projection, local archive reading and browser history as separate capabilities. Do not build a browser history client until the consumer and security boundaries explicitly cover it.
4. **Security and shared access gate:** Docs #167 and competent security/operations authority decide identity, authorization, classification, audit, deployment, backup/deletion and capacity operations before exposing data beyond local use.
5. **Consumer integration:** Frontend uses approved read contracts. Browser acceptance covers multiple sessions, explicit incomplete/stale state, provenance, and refusal to show a causally coherent combined scene without World verification. The already-dispositioned #40/#332 same-process Lab slice proceeds independently; any future Lab use of durable history needs its own consumer acceptance and separate evidence admission.

### V2 completion evidence still outstanding

GitHub state was rechecked on 2026-10-16: Observation #38 is **open** (`closed_at` is null; last updated `2026-10-16T19:49:36Z`), Observation #37 is closed, and Docs #167 is open. An earlier statement in this document incorrectly described #38 as closed; this correction does not change the design registry's `proposed / partial / UNRESOLVED` status or imply V2 acceptance. The current evidence refresh below is additive to the historical snapshots above. It uses Observation `572c86f8fce66a73cc3899a4a929448416f1e6bf`, Frontend `b21748d0929e21286c179eb02ca866abb7d8a718`, Docs `7642ebe711de047bc71ea4e035ed6b935a4c8a28`, and World `c165acb21794ec3f72677a25b2b4947142e15e15` (origin/main; the local World checkout is not used as canonical evidence). World #174 is included in that World revision but did not change the specific cut-association limitation cited here.

| #38 criterion | Current evidence and source/test basis | Status and limit |
| --- | --- | --- |
| Derived constitutional ADR / ADR-0100 impact | Sections 1 and 9 distinguish an operational observation archive from Lab's scientific evidence custody and assess the bounded local archive against ADR-0100. | **DESIGN ASSESSED, bounded only.** No new constitutional ADR is proposed for passive local storage/query; the design does not change ADR-0100, Lab custody, or evidence admission. Any future change to those boundaries remains outside this design and requires the competent constitutional disposition. |
| Capture boundary, duplicate/gap/order/completeness, source vs receipt time | Observation `capture.py` / `archive.py`; `tests/test_capture.py` (`test_capture_persists_explicit_plane_delivery_gap`, `test_interrupted_capture_remains_explicitly_unfinished_after_reopen`, `test_append_write_error_is_persisted_as_received_loss_not_success`, `test_commit_then_write_error_is_ambiguous_not_persisted_and_lost`, `test_failed_loss_marker_keeps_capture_open_and_unverifiable`, and capacity cases) and `tests/test_archive.py` (`test_reopen_keeps_records_and_repeated_claims_as_distinct_receipts`, `test_query_filters_and_paginates_by_local_receipt_sequence`). | **IMPLEMENTED + TESTED for bounded local capture accounting.** It records local delivery/persistence outcomes. It does not prove source-wide completeness, producer publication success, or causal completeness. `receipt_sequence` is local; source sequence is not inferred. |
| Immutable archive, live delivery and read projection roles | Observation `archive.py`, `capture.py`, and `http_bridge.py`; reader tests in `tests/test_archive_reader.py`. | **IMPLEMENTED + TESTED for append-only local archive, opt-in capture, read-only SQLite reader, and local current-view bridge.** The bridge is not a historical query API; no remote or browser archive transport is established. |
| Identity, provenance and paginated read queries | `ArchiveReader` in Observation `archive.py`; `tests/test_archive_reader.py`, notably pagination/filter, unsupported/missing identity, coverage, digest/schema, indexed-metadata drift, missing file, and symlink/immutability cases. | **IMPLEMENTED + TESTED within fields actually stored.** Pagination follows local `receipt_sequence`; supported exact filters are owner/family/subject/revision/domain time only where metadata exists. No producer-global identity, receipt-time filter, capture-scoped query, arbitrary time-range query, or World-cut filter is claimed. |
| World-cut history and multi-owner coherent queries | World #176 is closed as a design investigation after independent review at `world/main@c165acb21794ec3f72677a25b2b4947142e15e15`: current verification is active-cut-only; render-pose associations are transient; journal descriptors do not prove Observation receipt membership or projection-set completeness. | **CURRENT CONTRACTS INSUFFICIENT; DESIGN RESOLVED NEGATIVELY.** No historical World-cut query, archive membership proof, or complete/atomic multi-owner snapshot is supported. Matching tick/run/time/checkpoint references or receipt order are not proof. Any durable association is a new cross-domain contract, not authorized here. |
| Worlds/Runs, claim inspection, spatial and sensorimotor consumers | Observation #37 readiness inventory is closed on its bounded scope; Frontend current-view/spatial projection and local archive reader are separate capabilities. `tests/test_http_bridge.py`, `tests/test_archive_reader.py`, and owner-adapter tests cover components, not a combined historical consumer. | **PARTIAL; NO END-TO-END HISTORICAL CONSUMER ACCEPTANCE.** There is no archive-backed Frontend/browser history, multi-run historical UX, or joined sensorimotor trace demonstrated by these tests. Keep unsupported views explicit. |
| Classification, access, retention/deletion, audit, budgets, recovery and threat review | Local reader refuses writes and tests owner-only file permissions/symlink paths; capture tests cover local interruption and storage failures. Docs #167 remains open for broader Frontend access/deployment security. | **LOCAL SAFEGUARDS PARTIAL; OPERATIONS/SHARED ACCESS UNRESOLVED.** No remote/shared exposure, comprehensive retention/deletion policy, backup/restore service, cost budget or independent threat-model acceptance is evidenced here. Lab remains scientific evidence custodian. |
| Exact-source delta against #37, tests, and distinct owner disposition | Current-source inventory in this document; Observation #37 closed after a bounded readiness inventory; Observation #38 remains open as checked on 2026-10-16. Earlier reader/full-suite results (10/188) are historical results on the then-tested revision, not asserted for current `572c86f8`. | **READINESS INVENTORY RECORDED; NOT FULL V2 ACCEPTANCE.** No current full-suite rerun is claimed here. Existing tests do not establish browser E2E, full V2 acceptance, scientific validity, or remote access authorization. |

The merged increments #61 and #62, with the #63 integration-test addition, already demonstrate the following **bounded local behaviors**; they are not outstanding requirements merely because they are narrower than the target V2 archive:

- Capture tests distinguish persisted receipts from received-but-not-persisted losses, explicit delivery/capacity gaps, duplicate receipts, interrupted/open sessions, close-marker failures, and corrupt records. Reopening an interrupted capture leaves it open/unverifiable; these are local archive guarantees and do not prove that every producer publication reached Observation.
- The local read-only `ArchiveReader` retrieves stored original publications and their available provenance, paginates by local receipt sequence, exposes capture catalog/coverage, reports unsupported filters or absent identity metadata explicitly, and refuses write/symlink paths. It does not infer source ordering or a World cut.

The following **broader V2 capabilities remain unimplemented, unverified, or unresolved** and must not be implied by those local tests:

- An exact World-cut query or multi-owner coherent history that returns only explicitly verified associations and never infers a join from matching tick/run/time labels.
- A combined Frontend/run-history/analysis consumer that meets the minimum query needs without adding an unauthorized remote service or broad API surface.
- Comprehensive retention, classification, access, deletion, backup/restore, operational ownership, resource budgets, and independent threat-model acceptance for broader/shared access. No claim of scientific custody transfers from Lab.
- Observation #37 remains a bounded readiness inventory, not a client contract. Docs #167 shared/remote security and access disposition remains outstanding; it is not required for the local-only reader.
- These implemented increments and tests do not establish full #38 acceptance. Any later capability requires its own evidence and review; Owner acceptance remains separate from CI and PR merge.

## 9. Decisions still open

These are bounded decisions, not requests to reopen the architecture direction:

1. Observation and producer owners: which currently published families provide stable publication identity and meaningful source sequence/watermark semantics, and which remain explicitly unverifiable?
2. World historical-cut association: World #176 is closed after independent review as a design investigation, with the disposition that **current contracts are insufficient**; no consumer-verifiable historical lookup or durable Observation receipt membership exists. Current consumers must present unsupported/unverifiable status and must not join by labels. The remaining product/authority decision is whether to authorize a separately scoped durable World-authored contract; closure of #176 does not authorize that implementation.
3. Frontend consumer readiness: the exact-source readiness inventory is recorded in Docs PR #197 and accepted as an inventory, not as a client contract. Observation #37 is closed on that bounded basis; browser history is not authorized by that inventory.
4. Security/operations authority under Docs #167: whether/when history may be served to Frontend outside the local process boundary and under what classification, access, audit, backup and deletion rules. Docs #167 still leaves shared/remote deployment unauthorized; it does not block the local-only reader increment.
5. Lab: any future durable-history consumer requirements and the distinct Lab evidence-admission reference, without making Observation the custodian. This is not a blocker for the #40 same-process slice already dispositioned.
6. ADR-0100 is unchanged for this bounded operational archive under the Owner's direction above. Any future change to evidence admission, scientific custody, or Observation's authority is a new constitutional matter; no such change is proposed here.

No human decision is requested for routine technical choices inside the bounded design. The remaining items require the listed authorities because they concern source-owned contracts, World causal authority, security/access, or Lab evidence custody. This proposal records implemented local increments and a next bounded readiness increment; it does not itself authorize code changes to other domains or any public/remote exposure.

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
