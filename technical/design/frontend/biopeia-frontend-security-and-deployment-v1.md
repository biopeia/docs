---
id: design.cross-domain.biopeia-frontend-security-and-deployment-v1
title: "Biopeia Frontend v1 — Security and Deployment Boundary"
document_type: design
owner: biopeia-project-owner
created: 2026-10-13
language: en
document_version: 1
---

# Biopeia Frontend v1 — Security and Deployment Boundary

**Lifecycle:** Proposed; `registry/designs.yaml` is authoritative.
**Decision status:** Not ratified. This document records a recommendation and unresolved competent-owner dispositions.
**Implementation authorization:** Prospective authorization exists but is deferred. This document does not authorize implementation or deployment.
**Related work:** [Docs #164](https://github.com/biopeia/docs/issues/164), [Docs #167](https://github.com/biopeia/docs/issues/167), [Docs #166](https://github.com/biopeia/docs/issues/166), [Observation #37](https://github.com/biopeia/observation/issues/37), [Lab #63](https://github.com/biopeia/lab/issues/63), [Docs PR #165](https://github.com/biopeia/docs/pull/165).

## 1. Purpose and limits

This proposal defines a security decision boundary for a future read-only Biopeia presentation application. It separates a constrained developer-local profile from any shared or production profile, identifies the assets and trust boundaries, and lists the decisions and evidence required before either profile can be accepted.

The approved design direction is an independent presentation application that consumes only owner-authorized Observation publications. It does not own domain state, Observation semantics, causal execution, scientific evidence, authentication policy, or deployment operations. A rendered screen is not an access-control boundary.

This proposal does not select an identity provider, transport, API, backend-for-frontend, gateway, hosting platform, public exposure, credential format, or data classification. It does not authorize those systems. The selected design direction is a **local-only first profile recommendation**, not an accepted owner decision. Shared or production use remains blocked until its own security and operations owners approve an explicit target.

## 2. Normative constraints and assumptions

The following are constraints already established by the frontend design direction and Biopeia authority boundaries:

- Frontend is read-only. It must not issue World commands, interventions, experiment operations, evidence admissions, or owner-state mutations.
- Observation is the only approved publication boundary for presented Biopeia observations. A browser-readable route is not presumed to exist.
- Access, delivery, publication and semantic authority are distinct. A successful observation publication does not establish browser access or user authorization.
- Frontend must not read domain checkpoint files, solver state, Lab evidence stores, or private owner internals to bypass a missing Observation contract.
- Missing, partial, stale, denied, unsupported and unavailable data remain distinguishable; cached or delayed data must not be presented as current or committed without evidence.
- No legacy Symbiont path or compatibility bridge is permitted.

The threat analysis assumes standard browser same-origin isolation and that a malicious page/script running in the trusted application origin can access data available to that application. Local machine compromise, browser-profile compromise, malicious browser extensions, and user-authorized export are residual risks, not risks the application can eliminate.

## 3. Assets and security objectives

| Asset | Objective | Owner / boundary |
|---|---|---|
| Published claims and provenance | Preserve source meaning, confidentiality classification, integrity and authorized scope | Semantic domain owners; published through Observation |
| Identity and cross-domain links | Avoid unauthorized disclosure or fabricated associations | Issuing/authority domains; Observation carries explicit typed links |
| User and session identity | Authenticate only where a supported target requires it; expire and revoke access correctly | Competent identity/security owner, not yet named |
| Read scopes and access decisions | Enforce least privilege at a trusted service boundary, not only in UI | Data-serving authority; exact service boundary not established |
| Source and build artifacts | Prevent injected scripts, dependencies or deployment changes from acquiring trusted origin privileges | Frontend repository and release owner, not yet named |
| Browser cache, local storage and exports | Prevent accidental retention or misleading reuse of restricted/stale data | Frontend plus deployment owner |
| Operational logs and diagnostics | Support fault/security investigation without leaking tokens or unnecessary scientific payloads | Operations owner, not yet named |
| User-visible status and errors | Fail closed and distinguish denied, expired, partial, stale, unavailable and unsupported states | Frontend presentation; source status remains with Observation/owners |

Security objective: a viewer may disclose only the claims a user is authorized to read under an approved source contract, and any failure must not silently broaden access, mutate causal state, or present unverified data as current or committed.

## 4. Actors and trust boundaries

### 4.1 Actors

- **Local developer:** starts a development build and may inspect only a locally authorized, non-sensitive run or publication.
- **Shared user:** accesses an explicitly deployed shared instance; identity and read scope must be established by an approved service, not inferred by the browser.
- **Frontend maintainer/release operator:** produces and deploys application assets; must not gain domain-owner authority by deployment access.
- **Observation publisher/consumer service:** publishes or serves claims under its own authorization boundary. The exact consumer service is not yet established.
- **Untrusted input source:** any publication, URL, label, identifier, saved filter, imported file, or network response not yet validated against a specific approved contract.
- **Attacker:** may attempt script injection, credential theft, cross-origin access, unauthorized query, malicious export/import, dependency compromise, or misleading replay/cache behavior.

### 4.2 Trust zones

```text
LOCAL PROFILE
developer workstation
  ├── loopback-only development server (proposed constraint)
  ├── developer browser/profile
  └── explicitly approved local publication source (not established)

SHARED / PRODUCTION PROFILE — NOT APPROVED
user/browser
  ── authenticated, protected channel ──> approved read service (not selected)
  ── authorized Observation publications ──> frontend view

BIOPEIA AUTHORITY ZONES
domain owners -> World causal coordination -> Observation publication
       (frontend has no write path into these zones)
```

The local profile and shared profile are not interchangeable deployment configurations. A locally running development server that connects to a remote/shared source inherits the remote source's authentication, authorization, CORS, logging and data-classification requirements and must not be called local-only for security purposes.

## 5. Deployment profiles

### 5.1 Profile L — developer-local, recommended first target

**Recommendation:** if the competent owners approve a first implementation target, begin with a developer-local, single-user profile bound to loopback and without public, LAN, tunnel, or shared-user access.

Required constraints for an accepted Profile L:

- Bind the development server to loopback only; fail startup if the effective bind address is wildcard, LAN-reachable, or otherwise not loopback. A warning or UI banner is not sufficient. Any tunnel, reverse proxy, or remote source moves the use case outside Profile L and requires the applicable shared-access review.
- No hosted deployment, public ingress, shared account, remote administration, tunneling, or production dataset is part of this profile.
- No credential, API key, token, private endpoint, or secret is committed, embedded in a static bundle, URL, example, or localStorage.
- No cross-origin remote source is usable until a separate source owner approves its access contract and the exact origin/access mechanism is reviewed.
- The first runnable shell may present an explicit unavailable/unsupported state; it must not fabricate a publication or use fixtures as evidence of a production join.
- Any local source must be documented with its owner, data classification, access mechanism and retention behavior. If those are unknown, use no real source data.
- Local cache defaults to in-memory session state. Persisted cache is not authorized for sensitive/restricted claims. It must be clearable and must retain source revision/time/status metadata.
- The user is responsible for workstation and browser-profile security. This profile does not claim protection against another local user, administrator, malware, or a compromised extension.

Profile L does not imply that an unauthenticated local server is safe for data from a remote or shared authority. Localhost binding limits network exposure; it does not replace authorization at a remote data service.

### 5.2 Profile S — shared or production use

**Status:** not approved; excluded from implementation start until a competent security/operations authority is named and explicitly accepts a target design.

Before any shared/production profile is considered, the following must be decided and evidenced:

1. User principal and identity lifecycle, including session expiry, logout, revocation and reauthentication behavior.
2. Resource and action scopes at the authoritative read service. The frontend is read-only, but the service must enforce access on every request; hidden controls and client-side filters do not authorize data.
3. Data classification, tenant/World/run isolation and rules for unknown or absent classification. Default to deny for unclassified or out-of-scope data.
4. Hosting topology, trusted origins, TLS termination, CORS policy, security headers, dependency/build provenance and release ownership.
5. Cache, offline, export, URL sharing, browser history and log/telemetry retention policies.
6. Incident response, auditability, operational monitoring, access revocation and support ownership.
7. Any required server-side component (BFF/gateway/proxy) as a separately owned and threat-modeled design. It cannot be smuggled in as frontend plumbing.

No identity provider, hosting vendor, BFF, gateway, database, remote endpoint or cross-domain origin is selected by this proposal.

## 6. Threats and required controls

| Threat / abuse case | Impact | Required design response before relevant profile is accepted |
|---|---|---|
| Untrusted claim text or metadata is rendered as executable markup | Script execution in trusted origin; claim disclosure or session misuse | Treat all payloads as untrusted; schema/contract validation at boundary; text rendering by default; no unsafe HTML; safe URL scheme and destination handling; security tests for hostile content |
| Malicious or compromised dependency/build step | Code executes with access to all browser-visible data | Locked, reviewed dependencies; provenance and CI checks; narrow release permissions; dependency update review; no secrets in client build; production integrity checks owned by release authority |
| Token or secret embedded in bundle, source map, URL or browser storage | Credential theft or persistent unauthorized access | Never embed credentials in static assets or URLs; do not store bearer/session credentials in localStorage/sessionStorage; if authenticated shared access needs a server-held session or BFF, design and review it separately |
| Overbroad CORS or wildcard credentialed access | Unauthorized browser origins can read protected responses | CORS is configured by the serving authority for exact approved origins; no wildcard credentialed access; no browser assumption that CORS is authorization |
| Client-side filtering treated as authorization | User can alter requests or UI state and access out-of-scope data | Trusted read service enforces access for every resource; deny by default; frontend only reflects the returned access scope |
| Stale or partial cache appears current/committed | Incorrect causal interpretation; possible disclosure after access changes | Mark source cut/revision, availability and collection/delivery state; clear or revalidate when scope/session changes; do not promote cached status to committed/current; sensitive persistence remains unapproved |
| Cross-user, cross-World or cross-tenant cache collision | Disclosure or identity mix-up | Cache keys include issuer, authorized scope and stable resource identity; isolate sessions; clear on logout/scope change; verify with negative tests before shared use |
| Unsafe deep link or open redirect from published data | Phishing, credential capture or navigation to hostile origin | Allow only explicitly supported schemes and safe link targets; external navigation is visibly disclosed; no redirect target is trusted from a claim |
| Large, malformed or adversarial payload | Resource exhaustion, parser/rendering failure | Bound sizes/depth/rates at the source and consumer boundary; fail closed with a visible unsupported/error state; resource budgets need benchmark and owner disposition |
| Browser history, telemetry or logs include sensitive identifiers/data | Unintended retention or disclosure | Minimize identifiers and payloads in URLs/logs; no tokens in logs; retention and access for operational telemetry require owner approval |
| Loopback development service exposed on LAN/tunnel | Unauthenticated access by other devices/users | Enforce loopback binding outside the UI; do not advertise LAN access; document tunnel/proxy as shared deployment requiring Profile S review |
| Observation read path absent or unauthorized | Fake integration, direct owner reads, or misleading empty state | Do not bypass Observation; report `not established`, `unsupported`, `unavailable` or `access denied` distinctly; this is a gate owned by Observation #37 |

The proposed controls follow general browser security guidance: OWASP warns against placing sensitive information or session identifiers in Web Storage because same-origin scripts can access them; OWASP recommends narrowly scoped CORS origins and notes CORS is a browser access mechanism, not an authorization model; NIST SP 800-63B-4 describes session secret lifecycle and browser cookie protections. These sources inform the threat model but do not choose Biopeia's deployment or authentication design: [OWASP HTML5 Security](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html), [OWASP REST Security](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html), [NIST SP 800-63B-4 Session Management](https://pages.nist.gov/800-63-4/sp800-63b/session/), and [OWASP Content Security Policy](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html).

## 7. Access and failure behavior

The UI must treat access status as an observation about the consumer request, not as evidence that the underlying source state does or does not exist.

| Condition | Required user-visible behavior | Prohibited behavior |
|---|---|---|
| No supported consumer/read contract | State that the capability is not established; provide no fabricated data | Direct file/database access or mock success |
| Explicit denied/forbidden scope | Show access denied at the declared scope; do not reveal hidden resource details | Treat as empty World/run or silently broaden scope |
| Expired/revoked session or access scope | Immediately stop new reads and remove all data in the revoked scope from the active view and application-managed in-memory caches; clear persisted copies if any were explicitly authorized; offer reauthentication only if supported | Leave revoked data visible as stale, continue reads, retry forever, store a refresh token in browser storage, or claim secure physical memory erasure |
| Partial authorization | Identify which visible scopes/capabilities are available and which are denied where the service contract permits; never infer inaccessible records are absent | Merge partial data into an apparently complete scene/list |
| Network failure/disconnection | Preserve last known data only as visibly stale and tied to source cut/revision; show delivery failure separately | Advance causal time or imply source unavailable |
| Malformed/unknown contract revision | Reject incompatible interpretation and show unsupported/error; preserve diagnostics without sensitive payload | Best-effort reinterpret unknown fields or fallback to historical format |
| Oversized/untrusted payload | Reject or truncate only under an explicit contract that preserves completeness status; explain limitation | Silent partial rendering as a complete claim set |

## 8. Screen capability exclusions pending Observation #37

Until exact-current-source review and Observation-owner disposition exist, none of the seven screens may assume a browser-readable contract. In particular:

- **Worlds & Runs:** no complete discoverable World/run catalogue is established.
- **World Overview / Spatial Explorer:** no browser-accessible world/geometry/pose contract or universal coordinate assumption is established.
- **Causal Timeline:** no arbitrary browser query or durable replay contract is established merely by committed-cut publication.
- **Sensorimotor Trace:** no full Environment → Embodiment receptor → Modality → Organism publication chain is established.
- **Claim Inspector:** semantic claim concepts do not by themselves establish a supported remote read endpoint.
- **Connection & Access:** can only report an implemented and owner-approved access mechanism; the screen cannot create identity or authorize requests.

An implementation may begin only for the capability slices whose exact source and access contracts are approved, and only after the other readiness gates and separate start instruction. Unsupported screens may be omitted or visibly non-operational; they must not be fulfilled with fabricated TARGET records.

## 9. Privacy, retention and export

- Default to no durable browser storage of claims or credentials. An accepted profile may authorize caching only after data classification, scope isolation, expiry, invalidation and clear-on-logout behavior are defined. On revocation or scope loss, the fail-closed default is to hide and remove affected claims from application-managed views and caches before any reauthentication flow; this does not claim that JavaScript can securely erase physical memory or browser-managed copies.
- Do not place credentials, secrets or sensitive claim payloads in URLs, analytics, crash reports or client error messages.
- Export is disabled by default until a source contract identifies what may be exported, whether the output includes provenance/limitations, and what handling is required. Any enabled export must preserve the source identity, epistemic kind, availability, domain time/revision and provenance needed for correct interpretation.
- The interface must distinguish browser display/download from Lab evidence admission. Export does not make an artifact scientific evidence and does not transfer custody to Frontend.
- Retention duration, deletion, operational log access and incident preservation are unassigned pending an operations authority; do not invent a retention period.

## 10. Verification and release gates

Before accepting Profile L:

- verify loopback-only binding with a network-level test, not a UI assertion;
- verify no credential/secret is emitted in static bundle, source maps, URLs, browser storage or logs;
- exercise hostile markup, unsafe schemes, malformed/oversized payloads, unavailable source and denied scope;
- prove source/publication and delivery failure states remain distinct;
- verify session/cache clearing behavior for the exact local data classification and access mechanism;
- verify the effective listener rejects every non-loopback bind, and that revocation immediately removes the affected scope from visible/application-managed state without claiming physical-memory erasure;
- record exact repository revisions, commands and limitations.

Before accepting Profile S:

- all Profile L-independent security requirements in §5.2 have an accepted owner disposition;
- security and operations authorities are named and approve data class, identity, authorization, topology, origins, retention, monitoring and incident response;
- authorization is tested at the trusted service, including cross-user/cross-scope negative cases;
- session expiration/revocation, cache isolation, CORS, headers, build provenance, export and audit behavior are tested in the target deployment;
- a separate production readiness and deployment approval is recorded.

Passing UI tests, CI, or a localhost demo is not security approval and does not establish a remote access contract.

## 11. Decision and ownership ledger

| Item | Proposed disposition | Competent authority | Current state / closure trigger |
|---|---|---|---|
| Initial deployment profile | Prefer Profile L only as a bounded first target; keep Profile S excluded | Architecture Owner plus competent security/operations authority | **OPEN:** Owner disposition and security review required; no named security/operations authority is recorded |
| Identity and session mechanism | No provider or mechanism selected; require authenticated principal for shared use | Security/identity authority and serving-domain owner | **OPEN:** decide before any shared access; link implementation/security issue |
| Read authorization | Enforce per-resource at trusted serving boundary, default deny; UI is not enforcement | Observation/data-serving authority plus security authority | **OPEN:** Observation #37 must identify real access boundary; then owner approves scopes |
| Data classification and retention | No classification/retention period inferred; default to no persisted sensitive browser data | Data owner and operations/security authority | **OPEN:** classify first-use data and approve retention before persistence/export/shared deployment |
| Local development exposure | Loopback-only, no LAN/tunnel, no sensitive/remote source absent separate approval | Frontend repository owner and security reviewer | **PROPOSED:** confirm as part of implementation-start gate |
| Shared deployment and incident response | Excluded from v1 start until separate review | Named operations owner plus security authority | **OPEN:** assign owners and produce target deployment record before shared release |

The available decision record does not establish a competent security or operations owner. This is a real unresolved governance dependency, not a reason to assign the role implicitly to the Docs owner or Frontend maintainer. The specific trigger to reopen is appointment of a named accountable security/operations reviewer by the Biopeia owner. Until then, Profile S and any handling of restricted/sensitive data remain excluded; Docs #167 cannot be considered fully accepted as a deployment decision.

## 12. Follow-up gates and closure criteria

| Follow-up | Owner | Dependency | Closure trigger |
|---|---|---|---|
| Exact-current Observation read/access inventory | Observation owner; World/domain owners for their assertions | Observation #37 | Exact revisions and owner-approved supported/excluded capabilities; no inferred browser path |
| Lab/Frontend responsibility reconciliation | Lab owner | Lab #63 and accepted ADR-0113 | Lab-only apparatus needs and frontend presentation needs separated without lost work/evidence |
| Security/operations authority appointment and Profile L disposition | Biopeia owner / Architecture Owner | This proposal | Named competent reviewer records disposition; local exposure/data-class assumptions explicitly accepted |
| Shared/production profile | Named operations and security owners | Separate deployment design | Target service, identity, scope, data class, topology, retention and monitoring accepted; separate release authorization |
| Frontend implementation start | Architecture Owner | Docs #164 gates C/D/E, applicable contract/UX/review gates | All relevant readiness evidence accepted and a separate explicit Owner start instruction |

This design can be reviewed as a proposal while the named owners are being identified. It may not be marked approved, and the frontend is not ready to start, until each decision required for the selected implementation target is recorded by its competent authority. Closing Docs #167 alone does not authorize implementation or deployment.

## References

- [Docs #164 — Frontend design](https://github.com/biopeia/docs/issues/164)
- [Docs #166 — Constitutional boundary decision](https://github.com/biopeia/docs/issues/166)
- [Observation #37 — Read-only consumer boundary](https://github.com/biopeia/observation/issues/37)
- [Lab #63 — Workbench / presentation reconciliation](https://github.com/biopeia/lab/issues/63)
- [Docs #167 — Security and deployment design](https://github.com/biopeia/docs/issues/167)
- [Docs PR #165 — Approved design package, pending merge](https://github.com/biopeia/docs/pull/165)
