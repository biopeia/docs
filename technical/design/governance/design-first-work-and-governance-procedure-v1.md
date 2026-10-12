---
id: design.cross-domain.design-first-work-and-governance-procedure-v1
title: "Design-First Work and Governance Procedure v1"
document_type: design
owner: biopeia-project-owner
created: 2026-10-12
language: en
document_version: 1
---

# Design-First Work and Governance Procedure v1

## 1. Purpose and decision boundary

This design defines a proportionate, traceable procedure for proposing,
authorizing, executing, reviewing and closing work across Biopeia. It is
universal in scope but not uniform in ceremony: every work item is traceable;
the amount of design, decision recording and review depends on its governance
class, impact, risk and reversibility.

This is an **accepted design** under [ADR-0111](../../adr/ADR-0111-design-first-work-and-governance-procedure.md). Its document state is held in the design registry. Acceptance authorizes planning and implementation only through scoped Issues and applicable repository controls; it does not itself change live Project #1 fields or automations, grant experiment authorization, modify domain contracts, or authorize a scientific conclusion. Existing repository, scientific, frozen-artifact, constitutional and review policies remain in force.

The procedure applies to `organism`, `embodiment`, `environment`, `world`,
`modality`, `observation`, `lab`, and the shared documentation and governance
repositories. The Biopeia workspace remains composition and tooling only; it
does not acquire domain or scientific authority.

## 2. Design principles

1. **Traceability is universal; ceremony is proportional.** Small work can be
   specified in its Issue. A standalone design is not required for every
   correction.
2. **Design precedes governed implementation.** An accepted design authorizes
   only the implementation planning and work within its decision boundary. It
   does not imply implementation, scientific acceptance or deployment.
3. **Exploration is distinct from authorization.** Research may precede an
   accepted design, while experiments and protected changes remain governed by
   their applicable authorization.
4. **One concept has one canonical owner.** Designs describe proposal and
   impact; ADRs and DNs record decisions; Issues coordinate or define
   executable work; PRs carry changes and verification; the scientific record
   carries evidence and scientific disposition.
5. **Execution evidence is not authority.** Agent analysis, code review, CI,
   merge and successful execution do not by themselves accept a design,
   authorize an experiment, validate a scientific claim or close a larger
   integration deliverable.
6. **No implicit downgrade or promotion.** An executor cannot reclassify work
   to avoid controls, broaden an authorization, or infer approval from silence,
   a green check, a merged PR or a closed Issue.
7. **Keep the process reversible and low-friction.** Reuse existing fields,
   templates and automation where they fit safely. Add new board fields,
   states or reconciler logic only when a demonstrated need justifies them.

## 2.1 Unified topic-first and design-first lifecycle

Topic-first intake and design-first execution are stages of one procedure, not
competing alternatives. Every new concern starts with a traceable owning Issue
that records its purpose, question or objective, initial scope, owner, affected
domain/repository, known constraints and next decision or evidence needed. For
lightweight work, that Issue may contain the complete specification; a separate
design document is not required merely to create a topic record.

Triage then determines the applicable work class, risk, authority, uncertainty
and impact. The Issue may proceed directly to bounded work when existing
contracts and policy fully govern it. Otherwise, it may produce research or a
separate design. Research and protocol preparation may precede design
acceptance within their authorized limits; they do not authorize experiments,
protected changes or implementation beyond those limits. Governed
implementation starts only after the required design and decision are accepted.

A coordinating parent Issue is required when independently deliverable child
work, cross-repository responsibilities or dependencies need integration. It is
not required as ceremony for every standalone correction or investigation.
When a parent is used, each executable or research slice is a related subissue
in its owning repository, and closure includes the parent's own integration
acceptance. This refines the proposed Topic-first model in `.github-private#41`
without creating a second universal parent-issue requirement.

## 3. Proportionate procedure depth

Procedure depth is not a new Biopeia governance class. It is selected from the
existing `ORDINARY`, `SCIENTIFIC`, `FROZEN` and `CONSTITUTIONAL` classes,
affected boundaries and contracts, risk, irreversibility and uncertainty. If
classification is uncertain or impacts conflict, use the more restrictive
applicable path and ask the competent authority to classify the work. No agent
may lower the depth unilaterally.

| Depth | Typical use | Minimum starting specification | Minimum gate |
| --- | --- | --- | --- |
| **Lightweight** | Local correction, maintenance or minor documentation change without material semantic, contractual or evidence effect | Objective, scope/non-goals, affected repository, acceptance check and evidence in the Issue | Issue is sufficiently scoped and authorized for its class/risk before execution; PR evidence and applicable review remain required |
| **Standard** | Feature, bounded refactor, local contract or cross-domain change within accepted architecture | Brief standalone design linked from the Issue; include material alternatives, impact map, risks, dependencies and acceptance | Design is accepted by the competent authority before implementation; record a decision separately only when needed |
| **Governed** | Scientific, frozen, constitutional, cross-domain semantic/authority, irreversible or high-consequence change | Formal design, explicit decision/authorization path, impact analysis, evidence/reproducibility plan and integration/acceptance plan | Explicit approval by the authority named by the applicable class or artifact policy before protected implementation or execution |

Depth may be raised when scope or evidence changes. A lower depth is allowed
only when a competent authority records the reason and confirms that no
stronger class, risk or artifact policy applies. Routine reversible
implementation details need not each receive an ADR or DN.

## 4. Exploration, protocols and experiments

Every research activity has a traceable Issue identifying its question, scope,
restrictions, intended evidence and owner. Research can precede formal design
acceptance when it stays within those limits.

| Activity | May precede accepted design? | Authorization rule |
| --- | --- | --- |
| Documentary/theoretical research; hypothesis or model formulation | Yes | Research Issue; comply with access, safety, evidence and applicable work-class rules |
| Protocol design or preparation | Yes | Review appropriate to class, risk and affected invariants; preparation is not permission to run |
| Exploratory experiment | Sometimes | May run without new individual approval only if a current policy or prior authorization explicitly covers the category and defines scope, limits, isolation, resources and required evidence |
| Governed experiment or experiment affecting protected invariants/state | No, unless an existing authorization expressly covers it | Explicit scientific authorization before execution |
| Change to organism behavior, a governed contract, authority boundary or constitutional invariant | No, not as an implication of research or experiment | Accepted design and the decision/authorization required by the relevant class |

A category authorization identifies its owner, category, scope, exclusions,
permitted environment and resources, isolation and safety limits, required
protocol/evidence, validity or revalidation condition, and escalation
conditions. An agent may execute within a valid authorization without
repetitive individual approval. It MUST stop and seek authority before
expanding scope or acting outside an explicit limit.

Execution does not accept results. A scientific disposition such as
`unresolved`, `supported`, `refuted` or `inconclusive` belongs in the canonical
scientific record and is scoped to the protocol, conditions and evidence.
`Done` on an Issue means the contracted work is complete; it does not mean the
hypothesis is supported or the scientific claim accepted.

## 5. Authority, roles and acceptance

The Issue identifies an accountable owner and the competent decision or
acceptance authority when those differ. Roles describe responsibilities, not
new powers:

| Role | Responsibility | Limit |
| --- | --- | --- |
| Researcher | Frame the question, alternatives, uncertainties and evidence needs | Does not authorize protected execution by proposing it |
| Design owner | Keep scope, impact map, dependencies, decisions and acceptance criteria coherent | Cannot accept a class-controlled decision without authority |
| Coordinator | Maintain parent/child work, cross-repository dependencies and integration state | Coordination does not confer domain authority |
| Executor (person or agent) | Implement only authorized scope; preserve provenance and validation evidence | Cannot widen scope or self-authorize an experiment |
| Reviewer | Examine the exact candidate, evidence and claims against criteria and applicable review policy | A recommendation is not scientific or constitutional acceptance |
| Human decision authority | Accept decisions/claims reserved to the owner or designated scientific/constitutional authority | Authority must be named by applicable policy; Project permissions alone do not grant it |

One person may hold multiple roles on ordinary work where repository policy
allows. A one-person team is not forced into an unnecessary second-human gate.
This does not waive independent review required by the applicable risk-based
review policy, and agent review does not substitute for human scientific or
constitutional authorization. Design acceptance, technical acceptance,
integration acceptance, scientific acceptance, merge and deployment are
distinct.

- **Technical acceptance:** implementation, tests, documentation and local
  contracts meet the Issue criteria.
- **Integration acceptance:** the combined deliverable works across affected
  domains and its evidence and limitations are recorded.
- **Scientific acceptance:** the designated authority accepts a specified
  scientific conclusion based on admissible, sufficient evidence.

Only applicable acceptances are required for an Issue. A successful build or
merged change cannot stand in for an acceptance that has not occurred.

## 6. Canonical artifacts and identifiers

| Artifact | Canonical responsibility | Rule |
| --- | --- | --- |
| Design/specification | Proposal, rationale, boundaries, uncertainty, affected domains, options and acceptance plan | One flexible design template with a short mandatory core and optional sections. It links associated records instead of copying them. IDs retain `design.<area>.<slug>-vN`. |
| ADR | Durable, cross-domain, contractual, authority, constitutional or established-decision replacement | Required only when such a decision exists. Use `ADR-XXXX`; numbering continues the canonical ADR sequence in `technical/adr/`. A replacement explicitly supersedes its predecessor; history is retained. |
| DN (Decision Note) | Material but local and reversible decision too consequential for an Issue comment but not an ADR | Separate records at `technical/decision-notes/`, with a separate sequential `DN-XXXX` namespace and index. |
| Parent Issue | Integration coordination, scope, affected repositories, dependencies and closure authority | One coordinating parent when work spans independently deliverable child work or repositories. Its owner is the integration coordinator, not every executor. |
| Subissue | Bounded, independently verifiable work owned by one repository/domain | Create related subissues for independently deliverable parts. Research may finish without a PR; implementation may require more than one PR. |
| PR | Repository-scoped change, exact candidate revision, review and validation evidence | Each PR has coherent, verifiable scope. Multiple PRs per repository are allowed when deliveries are independent. Link each PR to the Issue(s) it advances or completes. |
| Scientific/evidence record | Protocol, admitted evidence, limitations, reproducibility and scientific disposition | Keep it with the scientific apparatus or other designated canonical owner; link it rather than duplicate it. |

An Issue's core fields are objective, owner, owning repository, affected
domains, class, risk, priority, work type, non-goals, dependencies, acceptance
criteria/evidence, applicable authorization and decision references. Optional
material stays out of lightweight work. GitHub Project #1 is the operational
coordination and traceability view, not the canonical scientific record or a
substitute for repository Issue/PR history.

## 7. Impact map and traceability graph

Every design/specification includes a compact impact map:

| Required item | Minimum content |
| --- | --- |
| Change and intended result | What changes and why; distinguish goal from demonstrated effect |
| Domain/repository | Affected domain, owning repository and accountable owner |
| Work and dependencies | Candidate Issue(s), deliverable slices, predecessor/dependency and integration owner |
| Risks and uncertainty | Technical/scientific risk, unresolved assumptions, reversibility and blocking questions |
| Decisions/authority | Applicable ADR/DN, decision needed, competent authority, and whether work can proceed safely |
| Acceptance and evidence | Technical/integration/scientific acceptance needed, evidence source and explicit non-claims |

If no Issue is ready, state why and identify the investigation or decision that
will make it ready. Issues and PRs link back to their source design when one
exists. PR closing keywords are used only when that PR's merge completes the
linked Issue. A partial PR never closes a parent or remaining deliverable.

Each actionable Issue is added to Project #1 and verified there. A parent
closes only after required child work is reconciled and its integration
acceptance is recorded; closing every child is necessary but not sufficient.
Cancelled or superseded work closes with a reason and replacement link when
applicable. Blocked work records the cause, competent authority or dependency,
next action and condition for resumption.

## 8. Frontmatter and templates

Every versioned Markdown artifact belonging to this procedure MUST carry
frontmatter. Templates define one small common identity schema and
type-specific optional fields. No empty placeholders are required.

The proposed common required fields are:

```yaml
---
id: design.cross-domain.design-first-work-and-governance-procedure-v1
title: "Design-First Work and Governance Procedure v1"
document_type: design
owner: biopeia-project-owner
created: 2026-10-12
language: en
document_version: 1
---
```

`document_version` is independent of an API/contract version. A contract
version is included only in artifacts that specify a contract. Typed links to
ADR, DN, Issue, PR and evidence are included only when present; no blank
relationship fields are required.

Frontmatter MUST NOT create duplicate lifecycle authority. For a design,
document status, implementation status and architecture scope remain in
`registry/designs.yaml`. ADR/DN acceptance is recorded in its canonical
decision record. GitHub Issue/PR state remains in GitHub and Project #1.
Templates may add type-specific metadata that does not compete with these
sources. Non-Markdown GitHub forms use their native syntax and equivalent
fields where supported; they do not use Markdown frontmatter.

The implementation package should include the design template, ADR and DN
templates/index, Issue and subissue templates, PR template, and a concise
emergency follow-up record. All share traceability terms while allowing
lightweight work to omit irrelevant sections.

## 9. Project #1 state model

Project #1 tracks both Issues and PRs under the target policy. They are separate
records with separate meanings; a PR's state is not the linked Issue's
acceptance state. The target values are `Backlog`, `Ready`, `In Progress`,
`In Review`, `Ready to merge`, `Blocked`, and `Done`.

`Ready to merge` is added for PR merge readiness. `Ready for deploy` is not
added: deployment is not currently a distinct acceptance stage. Revisit only
if deployment becomes a separate acceptance boundary.

| Status | Entry condition | Exit condition / rule |
| --- | --- | --- |
| **Backlog** | Identified but not committed or sufficiently scoped | Move to Ready when owner, scope, class/risk, authorization, dependencies and acceptance criteria are clear; move to Blocked when a required decision/dependency prevents safe progress |
| **Ready** | Bounded, authorized work with owner and verifiable acceptance criteria | Move to In Progress when execution actually begins; do not use as a queue for unresolved mandatory decisions |
| **In Progress** | Active research, preparation or implementation within authorized scope; draft PRs remain here | Move to In Review when a reviewable candidate/protocol/evidence package is submitted; return here for requested changes; use Blocked for external or authority blockers |
| **In Review** | Human/independent review, checks, evidence or acceptance are pending | Move to Ready to merge only when all applicable merge gates pass; return to In Progress for changes; use Blocked only when progress is stopped by a blocker |
| **Ready to merge** | PR only: required approvals exist, required checks pass on the exact candidate, conflicts are absent, review conversations are resolved and repository/queue rules permit merge | Merge under repository protections, or return to In Review/In Progress if a gate becomes unsatisfied. A merge queue must pass its final required validation |
| **Blocked** | Safe progress depends on a named decision, external dependency or unresolved failure | Record cause, authority/dependency, next action and restart condition; the competent authority or dependency owner records resolution before unblocking |
| **Done** | The individual tracked deliverable met its acceptance conditions and closure evidence is recorded | A PR reaches Done after merge; an Issue reaches Done only after its own acceptance, not merely because a PR merged or its children closed |

Review approval and CI/check status are separate signals. A failed check
requiring code changes returns the PR to `In Progress`; an unavailable external
service or unresolved infrastructure failure may be `Blocked`. A PR awaiting
review or checks is not `Ready to merge`.

A PR closed without merge is not completed work: archive its Project item to
remove it from active views while preserving its record; do not mark it Done.
Keep the linked Issue open unless the work is explicitly cancelled or
superseded, and record why. A merged PR reaches Done for that PR, but this does
not automatically close any linked Issue. Review and test existing close/archive
automations against multi-PR, parent/child, cancelled and scientific work
before changing live settings. Automation reports state; it does not certify
acceptance.

Existing Project fields for domain, priority, work class, work type, risk,
evidence status, decision required and owner remain conceptually distinct.
Review/check signals must not be overloaded into scientific evidence status.
Whether an additional field is necessary is an implementation question; do not
add one without a tested query or reporting need.

## 10. Change, emergency and closure rules

When an accepted design changes, publish a new version and reassess its impact
map. Pause or revise only affected work; preserve old decisions and evidence.
A new design version does not silently replace an ADR or DN. A governing
decision must be explicitly superseded through its decision record.

For an emergency with immediate material operational or scientific harm, the
responder may act before full design and workflow artifacts exist when delay
would worsen the harm. Record a minimal timestamped incident marker at the time
of action when that does not delay containment, then complete the linked Issue,
scope, authority, evidence and follow-up record within 24 hours after
containment. This exception does not waive constitutional restrictions,
scientific authorization, repository protections, review/merge gates or
post-incident traceability. It is not for ordinary schedule pressure.

Closure reconciles linked deliverables: Issue criteria, PR dispositions,
canonical ADR/DN/design state, integration evidence, scientific record where
applicable, limitations and Project status. Inconclusive or negative results
can be Done when they satisfy the agreed deliverable. Completion means the
contracted work is complete, not that every hypothesis is confirmed.

## 11. Validation and rollout

This design alone changes no live setting. Introduce the policy in reversible
stages:

1. **Ratify the design and governing decision.** The competent authority
   confirms the work class from the actual protected impact and identifies the
   ratification authority under existing policy; cross-domain scope alone does
   not make the change `CONSTITUTIONAL`. The proposed decision record is an ADR
   because it establishes a durable shared procedure; the ADR records the
   confirmed class, authority and rationale. If review finds that the procedure
   changes a protected invariant or authority boundary, apply the corresponding
   constitutional gate. Use DNs only for material local/reversible decisions
   that actually arise.
2. **Derive work from the accepted impact map.** Create owning-repository
   Issues for authorized implementation slices and add each to Project #1. Use
   one coordinating parent with linked subissues when independent deliverables,
   cross-repository responsibilities or dependencies require integration; do
   not create a parent solely to satisfy a universal formality. Confirm exact
   owners and repository requirements when the Issues are created.
3. **Implement templates and minimum checks.** Start with frontmatter and
   relation validation, template adoption, and documented entry/exit semantics.
   Do not build a general-purpose governance platform before it is needed.
4. **Reconcile Project automation.** Capture live settings first. Test a
   multi-PR parent, an unmerged closed PR, a cancelled Issue, a blocked decision
   and a scientific deliverable with inconclusive evidence. Change only
   workflows that violate the ratified policy; keep a before/after record.
5. **Pilot without blocking existing work.** Apply the procedure to one
   lightweight task, one cross-domain delivery and one scientific task. Review
   active legacy items opportunistically; that review must not stop progress.
6. **Review after seven days of operation.** Track process overhead, repeated
   manual corrections, automation errors, unlinked records, decision latency
   and review/merge delays. Record the review as a Project Issue and adjust only
   where evidence demonstrates a bottleneck.

The initial target is a human-auditable, idempotent set of templates and
automation. A reconciler is an option only if native workflows cannot preserve
the accepted invariants. It must begin read-only/dry-run, use least privilege,
be idempotent and logged, and be tested against the cases above. Informational
traceability warnings are distinct from failures that justify blocking merge.

## 12. Affected domains and repository consequences

| Candidate child work (under one coordinating parent) | Owner/repository scope | Deliverable and closure evidence |
| --- | --- | --- |
| Ratifying decision | `docs` decision record; competent cross-domain authority | Accepted ADR explicitly ratifies, rejects or revises this design; decision links to the parent Issue |
| Canonical procedure and templates | `.github-private` | Procedure plus design/ADR/DN/Issue/PR/emergency templates; template frontmatter and linking rules validated |
| Registry and document validation | `docs` | Cross-domain design scope, schema/validator support and rendered indexes; tests and registry validation pass |
| Project #1 policy and automation | `.github-private` plus Project #1 configuration | Before/after settings, tested status semantics and closure/archive behavior; any live changes authorized and evidenced |
| Repository applicability review | `organism`, `embodiment`, `environment`, `world`, `modality`, `observation`, `lab` | Per-repository decision: adopt shared templates/checks, link to canonical policy, or record why no local change is needed; do not create implementation work where no delta exists |
| Pilot and seven-day review | Governance owner, with participating domains as needed | Linked lightweight, cross-domain and scientific pilots; review records measurements, friction, failures and recommended adjustments |
| Workspace validation (only if needed) | `biopeia-workspace` | Tests only workspace-owned composition/tooling invariants; no domain or cross-domain semantic authority |

This is a target-impact statement, not proof that all repositories have
identical GitHub configuration or need a code change. Implementation Issues
must inspect each live repository/project setting and justify its delta. No
domain owner, scientific policy or semantic contract changes without that
domain's required decision.

The table is the candidate Issue decomposition, not a claim that these Issues
or Project items already exist. Each row becomes a subissue only if it has
independently verifiable work; repository applicability review may conclude
that no local change is required. If one candidate row expands into separately
deliverable parts, split it into related subissues under that row's Issue.

## 13. Implementation questions and acceptance checklist

The principles are settled. These items are implementation and validation work,
not reasons to reopen the architecture unless a pilot exposes a conflict:

- exact common/type-specific frontmatter fields and machine validation;
- template placement for internal versus public repositories;
- exact Project #1 view/filter behavior, including archival of merged PRs after
  completion;
- verified live workflow settings, overlap/race behavior and automation
  credentials;
- whether native Project workflows suffice or a narrow reconciler is needed;
- required versus advisory Issue/PR metadata and traceability checks;
- pilot work items, owners, measurements and review date.

The design is ready for formal review when the design register and ratifying
ADR make explicit that:

- affected domains and repositories are mapped;
- procedure depth derives from existing governance class, impact and risk;
- research, protocol preparation and experiment execution are separate;
- category authorization has bounded scope and cannot be widened by agents;
- authority, review and three acceptance types are distinct;
- Issues, subissues, multiple PRs, project states, closure and archival are
  traceable without equating merge with integration or scientific acceptance;
- frontmatter sources of truth do not conflict;
- emergency follow-up and non-blocking rollout are defined; and
- the pilot and post-adoption review are linked to Project #1.

## References

- Class, execution and evidence contract: `biopeia/.github-private`
  `workflow/agent-work-contract-v1.md` and `workflow/agent-workflow.md`.
- Risk-based independent review requirements:
  `biopeia/.github-private/workflow/review-policy.md`.
- Observed Project #1 settings and governance contract:
  `biopeia/.github-private/workflow/project-1-governance.md`.
- Project automation implementation record:
  `biopeia/.github-private/workflow/project-1-auto-add-app.md`.
- Documentation registry constraints: `registry/schema.yaml`,
  `registry/designs.yaml` and `tools/validate_registry.py`.
- GitHub Project #1: <https://github.com/orgs/biopeia/projects/1>.
