---
id: design.cross-domain.repository-settings-and-actions-workflow-normalization-v1
title: "Repository Settings and GitHub Actions Workflow Normalization v1"
document_type: design
owner: biopeia-project-owner
created: 2026-10-12
language: en
document_version: 1
---

# Repository Settings and GitHub Actions Workflow Normalization v1

## 1. Purpose and decision boundary

This design proposes a small, common baseline for repository settings and
GitHub Actions across Biopeia. The goal is predictable, maintainable delivery
for a one-person project, not enterprise process or identical workflows in
repositories with different responsibilities. The design is **proposed**;
the registry is authoritative for its status. It does not itself change live
GitHub settings, authorize implementation, or approve any repository's current
configuration.

The scope includes all Biopeia repositories, including private repositories:
`organism`, `embodiment`, `environment`, `world`, `modality`, `observation`,
`lab`, `docs`, `.github`, `.github-private`, and `biopeia-workspace`. Domain
repositories remain independently owned; `.github` owns public reusable
workflow implementations, `.github-private` owns private-only workflows, and
Docs owns this cross-repository design and its derived tracking records.

This is a baseline design, not a migration plan. Implementation issues should
be created after design acceptance, grouped by the smallest independently
verifiable repository sets, and tracked on [Biopeia Project #1](https://github.com/orgs/biopeia/projects/1).
Private-repository changes are in scope for the eventual rollout, but their
protection settings may require a separate access/plan check before claiming
they are protected equivalently.

## 2. Goals and non-goals

### Goals

1. Review every tracked Actions workflow in each repository and make its
   triggers, permissions, dependencies, branch/check behavior and ownership
   explicit.
2. Remove merged feature branches consistently in every repository.
3. Provide appropriate Dependabot security and version-update coverage for
   each applicable dependency ecosystem, including workflow actions.
4. Keep per-repository CI and reusable workflows specific to their real
   contracts; normalize safe defaults without forcing artificial uniformity.
5. Preserve low-friction operation for the current one-person team.

### Non-goals

- Replacing the current branch rulesets, inventing mandatory two-person
  reviews, or forcing one merge strategy across all repositories.
- Centralizing domain-specific CI jobs into a monolithic workflow.
- Automatically merging dependency updates or treating a green check as
  acceptance.
- Changing runtime, domain, scientific or cross-domain contracts.
- Defining a workflow release/versioning system beyond the controls necessary
  for safe reusable-workflow consumption.

## 3. Current-state snapshot and evidence limits

The inventory below is a live GitHub repository/workflow snapshot collected
for Issue `biopeia/docs#143` on 2026-10-12. It records workflow files visible
on the inspected default branches, not proof that every workflow's latest run
passed. A GitHub-generated Dependabot dependency-graph workflow may appear in
the UI; it is not a tracked YAML file and is not counted as a source workflow.
The rollout must re-inventory default branches before changing them.

| Repository | Tracked workflow files and responsibility | Current notable differences / review points |
| --- | --- | --- |
| `organism` | `auto-issue-triage.yml`, `auto-pr-checks.yml`, `ci.yml`, `project-1-auto-add-issue.yml` | CI declares `contents: read`; push is limited to `main`; three common workflows call public `.github` reusable workflows at immutable SHAs. |
| `embodiment` | Same four roles as `organism` | CI and reusable-call wrappers have no explicit top-level `permissions`; CI runs on all pushes. Includes `test` and distribution build/test checks. |
| `environment` | Same four roles as `embodiment` | Same permission and push-trigger differences; CI has test and distribution build/test checks. |
| `world` | Same four roles as `embodiment` | Same permission and push-trigger differences; CI has `package` and `integration` checks. |
| `modality` | Same four roles as `embodiment` | Same permission and push-trigger differences; CI has `test`. |
| `observation` | `auto-issue-triage.yml`, `auto-pr-checks.yml`, `ci.yml`, `project-1-auto-add-issue.yml` | Triage and Project intake call `.github-private`; PR checks call public `.github`; CI lacks explicit top-level permissions and runs on all pushes. Cross-visibility dependency requires validation. |
| `lab` | Same four common roles | CI lacks explicit top-level permissions and runs on all pushes; checks include unit, distribution, and cross-repository integration work. |
| `docs` | Common triage, PR checks, Project intake, `ci.yml`, `publication.yml` | CI includes scheduled and manual validation; publication also handles `docs-v*` tags. Both workflows lack explicit top-level permissions. Publication must remain independent of ordinary CI semantics. |
| `.github` | `auto-issue-triage.yml`, `auto-pr-checks.yml`, `project-1-auto-add-issue.yml` | Reusable workflows use `workflow_call`; permissions are declared. Project intake pins `actions/create-github-app-token` to a full commit SHA. |
| `.github-private` | Private triage, PR checks, Project intake reusable workflows; `ci.yml` | Reusable workflows use `workflow_call`; CI declares `contents: read`. Duplicated public/private workflow responsibilities need an explicit ownership rule. Private ruleset/protection state was not independently readable in the audit. |
| `biopeia-workspace` | `ci.yml`, `compatibility-pins.yml`, `public-head-smoke.yml` | Workspace-tooling CI, manually dispatched pin verification, and PR/manual provenance smoke test. No domain semantic integration authority. |

Observed patterns from this snapshot:

- All repositories had vulnerability alerts enabled; Dependabot security
  updates were disabled where the setting was readable. No repository had a
  tracked `.github/dependabot.yml` at the inspected default-branch revisions.
- Public repositories had secret scanning and push protection enabled. Private
  settings were not completely verifiable through the available API/plan.
- `delete_branch_on_merge` was enabled for `organism`, `embodiment`,
  `environment`, `world`, `observation` and `lab`; disabled for `modality`,
  `docs`, `.github`, `.github-private` and the workspace.
- Public repositories had a `Biopeia main review gate` ruleset on `main`, with
  pull requests, zero required approvals, resolved conversations and required
  status checks. Private protection status returned an access/plan error, so
  absence of protection must not be inferred.
- The inspected repositories allowed merge, squash and rebase; auto-merge was
  disabled. This design does not propose changing those settings absent a
  concrete maintenance problem.

The snapshot is not a substitute for an implementation-time API audit. Names
of required checks can change; those names and exact branch rules must be read
from current GitHub state immediately before rollout.

## 4. Proposed normalization policy

### 4.1 Repository settings

| Control | Proposed baseline | Allowed variation |
| --- | --- | --- |
| Default branch | Protect `main` from force-push and deletion; require PR-based delivery for code/workflow changes. | Existing repository-specific required checks remain distinct and may differ. |
| Approval count | Keep required human approvals at zero while Biopeia is a one-person project. | Add independent review only when team size/risk or a specific authority policy justifies it. CI and branch protection still apply. |
| Required checks | Require the repository's stable, meaningful CI and PR-contract checks; no check should be required if its trigger can leave a PR permanently pending. | Required check names and domain-specific suites vary by repository. Cross-repository tests stay where their contracts are owned. |
| Conversations | Require review conversations to be resolved before merge. | None proposed. |
| Merged branch deletion | Enable automatic deletion of head branches after PR merge in all 11 repositories. | If a release/integration branch is intentionally long-lived, document the exception and protect that branch explicitly; feature branches are not exceptions. |
| Merge methods | Retain current merge/squash/rebase choices. | Narrow only if actual history/release practice demonstrates a need. |
| Auto-merge | Keep disabled by default. | Revisit only if required checks and review/authority semantics remain unambiguous. |
| Repository security | Keep vulnerability alerts enabled. Enable secret scanning/push protection where available and supported for public and private repositories. | For unavailable features, record the plan/visibility limitation and compensating control; do not silently imply coverage. |

GitHub documents automatic head-branch deletion as a repository setting,
while also noting that branch rules can prevent deletion. Validate it with a
merged, disposable test PR during rollout rather than relying only on the
checkbox. [GitHub: managing automatic branch deletion](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-the-automatic-deletion-of-branches)

### 4.2 Workflow structure and triggers

Normalize safe behavior, not file count:

1. Keep each repository's CI in that repository and preserve its meaningful
   checks. The workspace may validate workspace-owned tooling only; it must
   not become semantic authority for domain integration.
2. Use public reusable workflows from `biopeia/.github` for common behavior
   intended for public consumers. Use `.github-private` only for private
   operations. A public repository must not depend on a private reusable
   workflow unless repository visibility/access is explicitly demonstrated,
   intentionally approved and tested from a clean consumer context. Prefer
   moving genuinely common, non-secret logic into `.github` and keeping
   private wiring/secrets in private wrappers.
3. Keep reusable workflows on immutable full commit SHAs. Human-readable
   comments may identify the corresponding tag/release, but tags are not the
   pin. Dependabot should propose pin updates; review provenance and diff
   before merging.
4. For CI that serves PRs, run on `pull_request` and `push` to `main` unless a
   repository has a documented reason otherwise. Use explicit PR event types
   only when they preserve the required check behavior. Do not add path filters
   to required checks unless a separate always-present gate ensures GitHub
   receives a definitive result. Keep schedules/manual runs for their
   additional purpose, not as substitutes for PR validation.
5. Keep publication/release workflows separate from ordinary CI when they
   require tags, credentials, or different authority. Grant publication
   permissions only to the publishing job and only for the publishing event.
6. Avoid `pull_request_target` for untrusted PR code and do not expose secrets
   to PR validation jobs. If a workflow needs write access, isolate that action
   in a narrow job after the untrusted-code boundary and grant only the
   required permission.
7. Apply an explicit, least-privilege `permissions` block at workflow or job
   scope in every workflow. Start with `contents: read` for ordinary CI;
   triage gets only the issue permission it needs; Project intake uses its
   GitHub App token with only the installed permissions needed to add the
   issue to Project #1; publishing gets only the contents/deployment/package
   permission actually used. Unspecified permissions are not an acceptable
   implicit default.
8. Use concurrency cancellation for superseded PR CI runs where safe; do not
   cancel publication, release, deployment, or evidence-producing runs whose
   completion is meaningful.

Actions security settings should be reviewed as part of the same audit:
restrict allowed actions to GitHub-owned, verified marketplace, or explicitly
approved sources if this does not break needed workflows; require full-SHA
pinning for third-party actions when the organization/repository supports it;
keep token permissions read-only by default. [GitHub: managing Actions settings](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)

### 4.3 Dependabot

Adopt a small checked-in `.github/dependabot.yml` policy for every repository:

- Enable the `github-actions` ecosystem at the repository root, checked
  weekly, to update both action dependencies and reusable workflow references
  where supported.
- Enable security alerts and Dependabot security updates for each repository
  where GitHub supports them. Keep security-fix PRs reviewable; no automatic
  merge is proposed.
- For Python repositories, configure the ecosystem matching the actual
  dependency manager and committed manifests. The repositories using `uv`
  (`pyproject.toml` and `uv.lock`) should use Dependabot's `uv` ecosystem if
  confirmed supported at rollout; repositories without a lockfile need a
  deliberate choice between adding/maintaining `uv.lock` and configuring the
  ecosystem their manifests actually support. Do not add a fictitious manager
  merely to make files identical. GitHub currently documents `uv` support in
  its Dependabot options reference; confirm behavior in a test PR before
  standardizing it. [Dependabot options reference](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference)
- Group compatible patch/minor updates to limit PR noise, but keep major
  upgrades and security updates independently reviewable unless a repository
  has evidence supporting broader grouping. Set a small open-PR limit (default
  5 per ecosystem) and adjust only when updates are being starved.
- Avoid unnecessary updates for vendored/generated artifacts and repositories
  with no applicable package manager. The workspace and Docs each declare
  Python dependencies and should be evaluated as applicable Python projects;
  workflow-only `.github` repos still need `github-actions` updates.

GitHub distinguishes version updates from security updates; security updates
depend on alerts being enabled and may be configured alongside, but not
replaced by, scheduled version updates. [Configure Dependabot version updates](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/configure-version-updates), [configure security updates](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/configure-security-updates), [Dependabot for Actions](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/auto-update-actions).

## 5. Repository-level workflow normalization matrix

These are design targets, not a declaration that current jobs are defective.
Implementation issues should make the minimum changes needed to meet the
baseline and preserve each row's domain-specific test semantics.

| Repository | Keep distinct checks | Normalize common workflow behavior |
| --- | --- | --- |
| `organism` | `test-and-build` | Explicit permissions; scope push to `main`; retain common intake/review calls on public `.github` immutable SHAs. |
| `embodiment` | `test`; `Build and test distributions` | Explicit permissions; scope push to `main`; preserve distribution artifact checks and stable required check names. |
| `environment` | `test`; `Build and test distributions` | Same as `embodiment`; preserve environment-specific tests. |
| `world` | `package`; `integration` | Explicit permissions; scope push to `main`; retain separate integration check and do not conflate packaging with integration acceptance. |
| `modality` | `test` | Explicit permissions; scope push to `main`; keep modality contract tests local. |
| `observation` | `test-and-build` | Explicit permissions; resolve public-to-private reusable workflow dependency; retain only the workflows that have a clear public/private owner. |
| `lab` | `unit-tests`, `build-and-install`, `cross-repository-integration` | Explicit permissions; scope push to `main`; preserve Lab's integration responsibility and evidence boundaries. |
| `docs` | `registry`, `cross-repository`, `publication` | Explicit permissions per job; keep scheduled/dispatch validation and tag publication distinct; avoid granting publication write permissions to PR CI. |
| `.github` | `validate-pr-contract` and reusable triage/intake behavior | Add CI validating reusable workflow syntax/contracts and safe reusable-workflow changes; keep each caller's permission boundary explicit. |
| `.github-private` | private CI and private intake/triage wrappers | Explicit least privilege; test workflows from authorized private consumers; document unavailable ruleset/protection settings and access constraints. |
| `biopeia-workspace` | tooling checks, compatibility pin verification, public-head provenance smoke test | Explicit least privilege; maintain separation from semantic/domain acceptance; make manual-only workflows' inputs and evidence clear. |

Every tracked workflow must have an inventory row in the implementation
tracking artifact containing: path, purpose, event/triggers, `GITHUB_TOKEN`
permissions, external actions/reusable calls and pin type, secrets, required
check names, owner, and a disposition (`keep`, `normalize`, `replace`,
`remove`). This catches dormant or specialized workflows that a common-file
template would otherwise miss.

## 6. Rollout and acceptance

Implementation proceeds in small PRs after the design is accepted:

1. Re-fetch configuration and workflow inventory for all 11 repositories;
   capture default branch and exact source revisions. Confirm which private
   settings and security features are observable/available.
2. Add testable configuration/templates first (Dependabot files and workflow
   conventions), then update repositories in bounded groups. Grouping must
   follow independent verification and access boundaries, not a goal of one
   giant cross-repository PR.
3. Set merged-branch deletion to enabled in all 11 repositories and verify
   with a disposable merged PR or the documented GitHub behavior where a test
   PR is inappropriate.
4. Update workflow permissions/triggers and reusable references while
   preserving required check names or updating branch rules in the same
   change. Exercise public and private reusable callers.
5. Enable and validate Dependabot updates ecosystem by ecosystem. Inspect the
   resulting manifests/lockfiles and CI before accepting update PRs.
6. Reconcile Project #1 only after each repository's configured state and
   workflow runs have been checked; close the coordinating Issue only after
   all child work, integration checks, and documented exceptions are
   complete.

The rollout acceptance checklist is:

- Every repository and tracked workflow has an audited, current inventory
  disposition and exact revision.
- All 11 repositories have merged-branch deletion enabled or a specifically
  approved documented exception.
- Every applicable ecosystem has an active Dependabot configuration and a
  demonstrated update PR/security-update status; unsupported capabilities
  are recorded rather than claimed.
- Workflow token permissions are explicit and least-privilege; action and
  reusable-workflow refs meet the selected immutable pin policy.
- Required checks remain effective on PR updates and do not remain pending
  because of trigger/path-filter behavior.
- Public/private caller boundaries and private branch protection limitations
  have been tested or precisely recorded.
- No implementation is represented as complete solely because configuration
  files merged; actual repository settings and workflow runs are verified.

The rollout should be piloted on one domain repository and one shared
workflow repository, then applied across remaining repositories. If the pilot
reveals friction or check-name instability, adjust before broad rollout.

## 7. Risks and alternatives

| Risk | Treatment |
| --- | --- |
| `uv` support or lockfile behavior differs from expectations in Dependabot | Test a real update PR first; use the ecosystem matching the actual manager; document any repository-specific exception. |
| Updating shared reusable workflows breaks several callers | Immutable SHA pins make changes explicit; update shared workflow and callers through traced Issues/PRs; keep a rollback path. |
| Tightened permissions break an action | Audit every `GITHUB_TOKEN` use and job boundary; grant only the missing permission at the narrowest scope and record why. |
| Required check names or events change, blocking merges | Read current ruleset requirements before edits and test `opened`, `synchronize`, `reopened` and ready-for-review behavior. |
| Public code calls a private workflow that consumers cannot access | Verify using a clean, least-privileged consumer context; migrate shared behavior to public `.github` or retain private calls only in private repositories. |
| Private plans/settings cannot provide equivalent protection | State the capability gap, do not claim parity, and select a proportionate compensating control. |
| Too many Dependabot PRs burden one maintainer | Weekly cadence, compatible patch/minor grouping, modest PR limit; tune based on observed backlog rather than blanket auto-merge. |
| Branch cleanup removes an intentionally persistent branch | Only merged PR head branches are auto-deleted; protect documented long-lived branches and verify behavior. |

The main alternative is to centralize every workflow in `.github`. Rejected:
it would blur domain ownership, make failures harder to attribute and couple
unrelated CI. The proposed design centralizes only reusable mechanics while
keeping validation semantics at the repository that owns them.

## 8. Related records

- Tracking Issue: [`biopeia/docs#143`](https://github.com/biopeia/docs/issues/143)
- Governance anchor: [ADR-0111 — Design-First Work and Governance Procedure](../../adr/ADR-0111-design-first-work-and-governance-procedure.md)
- Current delivery tracking: [Biopeia Project #1](https://github.com/orgs/biopeia/projects/1)
- No ADR is proposed yet: create one only if acceptance establishes durable
  cross-repository rules that require decision authority beyond this design.
