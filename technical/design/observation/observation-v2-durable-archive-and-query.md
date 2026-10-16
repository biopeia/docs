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

The accepted constitutional boundary in [ADR-0100](../../adr/ADR-0100-observation-capability-and-evidence-custody.md) separates passive runtime projection/transport from durable scientific evidence and provenance custody. **Assessment:** an operational archive remains within that boundary if it retains only source-authorized publications and capture-accounting records, exposes their limitations, and never admits evidence or creates scientific provenance. **Recommendation for this bounded design:** a derived constitutional ADR is not needed because the proposal preserves ADR-0100's custody boundary. This is a recommendation for Architecture Owner disposition, not a claim that the Owner has already resolved the question. If the Owner requires constitutional clarification, it must be prepared and ratified before implementation. A change that makes Observation custodian/admitter of scientific evidence, or changes its authority, would be a constitutional conflict and must return to the Architecture Owner; this proposal does neither. This assessment does not amend ADR-0100 or authorize implementation.

The existing [V1 observational data-lake proposal](observation-data-lake-v1.md) remains the conceptual predecessor. This V2 proposal narrows the architecture to implementable logical behavior and reuses the local archive already present in Observation; it selects no new public wire contract, remote service, infrastructure, or deployment.

## 2. Inputs and evidence basis

The design preserves ADR-0078 (causal passivity), ADR-0095/0099 (semantic authority and Modality boundary), ADR-0100 (evidence custody), ADR-0110 (capability boundary), and the bounded passive carriage direction in Observation #37. The exact repository snapshots reviewed for this proposal are recorded below; they are source snapshots, not claims that every consumer contract is approved.

| Repository | Reviewed revision | Relevant evidence and limit |
|---|---|---|
| Observation | `6a3bf96c90c78c13af69c6e98dc19569afd5c629` | PR #61 merged a local append-only SQLite archive and capture coverage accounting. `receipt_sequence` is local order; source watermarks bound local delivery only. Read API is local `read_page`; no browser historical-query contract is established. |
| World | `1e42240beb82f0647d89e796d4a325a240d1b147` | World owns causal commit/cut assertions. Observation must carry only explicit World-authored/verifiable association; matching tick labels alone cannot establish a shared cut. |
| Frontend | `b21748d0929e21286c179eb02ca866abb7d8a718` | Consumer readiness remains bounded to approved current-view claims. No durable archive query or history API is established by this design snapshot. |
| Organism | `cedce522696f7d5a0ba458018eebd61a18972a4c` | Source owner of Organism claims; no new source publication contract is introduced here. |
| Embodiment | `957af224e4400fc30a9d8d78d987cec16a8e959e` | Source owner of body/morphology claims; no new source publication contract is introduced here. |
| Environment | `4eb1f8c3393a7cdbabcfaf35b8630aaf57de20c1` | Source owner of environmental claims; no new source publication contract is introduced here. |
| Modality | `62af4aba07146d5dfdc978af07bb72111112d873` | Capability/transduction lineage only; it is not an independent semantic authority. |
| Lab | `03c7cb64c6e98226c0737fc6f8b8d341ae6eaf36` | Scientific apparatus/evidence custody remains separate. Archive retrieval is not evidence admission. |
| Docs | `5edb112a462c2436d71afa44949aef36ef15e768` | Includes ADR-0100, V1 proposal, security/deployment design, and registry. |

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

PR #61 implements bounded local accounting, including persisted rows, received-not-persisted outcomes, durable gap markers, open/unverifiable intervals, closure verification, and stricter interval completeness. PR #61 configures SQLite rollback-journal `DELETE`, `synchronous=FULL`, and foreign-key enforcement; it tests process interruption and injected capacity/write/marker failures. Durability still depends on the OS, filesystem, SQLite VFS, storage controller and hardware honoring SQLite's commit semantics; this is not proof against physical power loss or hardware failure. Disk-full or write failure cannot be made durable by Observation; if it cannot persist a loss/close marker, recovery must leave the session open/unverified rather than upgrade it to complete. The implementation's payload budget is not a physical disk quota.

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
| Spatial Explorer | **Partial** for separately carried static Environment/Embodiment owner projections; **not established** as a coherent dynamic scene. | No pose-to-geometry or shared-cut inference; requires owner/World evidence before a joined scene can be represented. |
| Causal Timeline | **Not established** as causal history or browser replay. Local `receipt_sequence` is only archive receipt order. | Requires explicit World cut assertions and a consumer read path; presentation order must not be labeled causal replay. |
| Sensorimotor Trace | **Not established** for a complete, linked sensorimotor claim graph. | Requires explicit typed owner links and access to all relevant authorized claims; no heuristic joins. |
| Claim Inspector | **Partial** for claims available in the current local view; durable cross-restart/browser inspection is **not established**. | Requires stable claim/publication references and provenance-preserving history queries. |
| Connection & Access | **Partial** for bounded local-process availability; shared/remote authorization is **not authorized**. | Docs #167 remains open for future shared/remote security and deployment; local-only readiness must stay distinct. |

Based on the exact source revisions in §2 and the merged capture-integrity increment:

| Readiness dimension | Current bounded evidence | V2 target / remaining gap |
|---|---|---|
| Passive authorized capture and local durable rows | Implemented locally by Observation PR #61 | Capture failure/coverage distinctions are present locally; verify owner-specific publication IDs, source ranges and closure declarations only where contracts define them. |
| Local ordering and recovery accounting | PR #61 implements receipt order and capture sessions; source sequence is explicitly local delivery accounting | No causal inference. Confirm per-source reset/continuity semantics; unknown intervals remain unverifiable. |
| World causal association | World owns cut authority; exact query may filter only explicit verified association | A consumer-verifiable shared-cut record and conformance cases must be evidenced by World; tick equality is insufficient. |
| Queryable durable history | SQLite archive query currently pages by family and local receipt cursor | The Python archive exposes `query(family, after_receipt_sequence, limit)`, `capture_sessions()` and `capture_coverage()`; the local HTTP bridge exposes bounded current-view `GET /v1/current`, not durable history. No public history API or browser transport is approved; query shapes above are logical requirements only. |
| Frontend consumer readiness | Current-view local reads and bounded static spatial claim carriage exist | The screen matrix above is not a readiness approval. Durable browser history and a coherent multi-owner scene are not established. |
| Lab same-process use | Observation #40 and Lab #332 disposition the bounded read-only same-process slice | Independent of durable archive/history queries; no automatic evidence admission. Lab retains its own evidence references and custody under ADR-0100. |
| Security/retention/operations | Local prototype bounds only | Docs #167, classification/access authority, deletion/retention and shared deployment remain unresolved. |

The V2 target does not add producer fields or transport behavior to make a row appear ready. Each publisher must separately define stable identity, source delivery accounting and any cut relationship within its own authority. Consumers must preserve unsupported and unverified states.

## 8. Incremental plan and acceptance

1. **Design disposition (this deliverable):** review the bounded archive/query design, ADR-0100 assessment, and responsibility split. No code or publication contract changes follow merely from document approval.
2. **Next implementable increment — local reader only:** extend the existing local reader (currently optional family plus receipt-cursor pagination) with exact subject, revision and domain-time selection using fields already present in archived owner publications; expose existing capture catalog/coverage. Results retain original provenance separately from receipt metadata and pagination remains anchored in local `receipt_sequence`. Selection must be scoped to an explicit scan cursor/window so sparse matches cannot be mistaken for a complete history. A World-cut filter is available only when a row already carries an explicit World-authored verifiable assertion; otherwise return `unsupported/not established`. Do not add tables/schema fields, producer contracts, HTTP/browser API, cross-run joins or remote access in this increment. Acceptance tests prove pagination, exact filtering, provenance, unsupported/unverified responses, no tick/run joins and no mutation. Existing PR #61 write-path, SQLite fault-injection, capacity and recovery tests are not repeated unless reader changes invalidate them.
3. **Owner-specific source/cut readiness:** each producer owner defines and tests any publication ID, source sequence/watermark, cut association, or explicit absence contract it owns. World alone tests cut validity. Observation consumes only approved records; no implementation can manufacture missing fields.
4. **Security and shared access gate:** Docs #167 and competent security/operations authority decide identity, authorization, classification, audit, deployment, backup/deletion and capacity operations before exposing data beyond local use.
5. **Consumer integration:** Frontend uses approved read contracts. Browser acceptance covers multiple sessions, explicit incomplete/stale state, provenance, and refusal to show a causally coherent combined scene without World verification. The already-dispositioned #40/#332 same-process Lab slice proceeds independently; any future Lab use of durable history needs its own consumer acceptance and separate evidence admission.

### Acceptance evidence required for Issue #38

- Contract examples cover persisted, received-not-persisted, known-gap, unverifiable, closed-verified, complete-interval, duplicate, conflicting identity, interrupted session, capacity exhaustion, corruption, and unsupported query cases.
- A consumer can retrieve a publication and its provenance without write authority; result distinguishes local receipt sequence from source sequence and World cut.
- Exact World-cut query returns only explicitly verified associations and does not infer from matching tick/run/time labels.
- Restart after a missing close marker leaves capture incomplete/unverifiable; no damaged or absent row is represented as persisted.
- Query behavior meets Frontend/run-history/analysis minimums without adding a remote service or broad API surface before security disposition.
- Retention/classification/access/recovery operational owners and limitations are explicit; no claim of scientific custody transfers from Lab.
- Observation #37 exact-source readiness is reconciled by its competent owners; Docs #167 security/access dependencies are dispositioned for the requested consumer profile.
- PR/CI and independent review validate the exact documentation candidate. Owner acceptance remains separate from CI and PR merge; Issue #38 remains open until all criteria are evidenced and accepted.

## 9. Decisions still open

These are bounded decisions, not requests to reopen the architecture direction:

1. Observation and producer owners: which currently published families provide stable publication identity and meaningful source sequence/watermark semantics, and which remain explicitly unverifiable?
2. World: what exact existing or minimal World-authored record proves that a publication belongs to a committed cut, and whether such association is individual or an explicitly complete shared projection?
3. Frontend consumer readiness: Observation owner disposition and author-distinct independent review of the exact-source #37 matrix above; until then it is a proposed readiness delta, not an approved client contract.
4. Security/operations authority under Docs #167: whether/when history may be served to Frontend outside the local process boundary and under what classification, access, audit, backup and deletion rules. Docs #167 still leaves shared/remote deployment unauthorized; it does not block the local-only reader increment.
5. Lab: any future durable-history consumer requirements and the distinct Lab evidence-admission reference, without making Observation the custodian. This is not a blocker for the #40 same-process slice already dispositioned.
6. Architecture Owner disposition of the ADR-0100 assessment: accept the recommendation that this bounded operational archive needs no derived constitutional ADR, or require a clarification before implementation. No ADR-0100 amendment is proposed by this design.

No human decision is requested for routine technical choices inside the bounded design. The remaining items require the listed authorities because they concern source-owned contracts, World causal authority, security/access, or Lab evidence custody. This proposal documents the next bounded reader increment but does not itself authorize code changes or any public/remote exposure.

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
