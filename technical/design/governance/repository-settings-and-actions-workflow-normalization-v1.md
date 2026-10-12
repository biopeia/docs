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

This document-only proposal has low direct implementation risk. That must not
be used to classify the later settings and workflow rollout: implementation
has distinct risks involving permissions, credentials, repository access,
required checks and Dependabot execution. Assess those risks in the derived
implementation Issues before changing live configuration.

The scope includes all Biopeia repositories, including private repositories:
`organism`, `embodiment`, `environment`, `world`, `modality`, `observation`,
`lab`, `docs`, `.github`, `.github-private`, and `workspace` (the GitHub
repository `biopeia/workspace`; its local integration checkout is named
`biopeia-workspace`). Domain
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

The current exhaustive read-only baseline is the [Biopeia Repository Settings
and GitHub Actions Inventory — 2026-10-13](../../inventory/repository-settings-and-actions-2026-10-13.md),
prepared for [Docs #152](https://github.com/biopeia/docs/issues/152) and linked
to the implementation tracker [Docs #151](https://github.com/biopeia/docs/issues/151).
It records all eleven in-scope repositories, their inspected default-branch
revisions, every tracked workflow file, available required-check producers,
repository settings, branch rules and evidence limits. It supersedes the
preliminary 2026-10-12 snapshot retained below for historical context.

The inventory is a dated baseline, not proof that every workflow's latest run
passed or that mutable GitHub settings remain unchanged. Re-read the affected
repository's current configuration immediately before each implementation.
GitHub-generated dependency-graph workflows are not tracked YAML source files
and are excluded from the count of 43 tracked workflows.

### Historical preliminary snapshot (2026-10-12; superseded)

The following table and notes preserve the initial diagnostic collected for
Docs #143. They are not the current configuration baseline; use the linked
2026-10-13 inventory for current SHAs, exact workflow details, check producers,
settings observations, and access limitations.

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
| `workspace` | `ci.yml`, `compatibility-pins.yml`, `public-head-smoke.yml` | Workspace-tooling CI, manually dispatched pin verification, and PR/manual provenance smoke test. No domain semantic integration authority. |

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

At the time of this historical snapshot, the exact required-check mapping and
workflow catalog had not yet been recorded. Those gaps are addressed in the
linked 2026-10-13 inventory to the extent exposed by GitHub. Private ruleset
and protection details remain unknown where the API returned an access/plan
error; they must be verified through an authorized route before implementing
changes in those repositories. Required checks and branch rules are mutable
and must still be re-read immediately before rollout.

## 4. Proposed normalization policy

### 4.1 Repository settings

| Control | Proposed baseline | Allowed variation |
| --- | --- | --- |
| Default branch | Protect `main` from force-push and deletion; require PR-based delivery for code/workflow changes. | Existing repository-specific required checks remain distinct and may differ. |
| Approval count | Keep required human approvals at zero while Biopeia is a one-person project. | Add independent review only when team size/risk or a specific authority policy justifies it. CI and branch protection still apply. |
| Required checks | Require the repository's stable, meaningful CI and PR-contract checks; no check should be required if its trigger can leave a PR permanently pending. Record each required check's exact name, producing job, event, provider/source, and ruleset setting. | Required check names and domain-specific suites vary by repository. Cross-repository tests stay where their contracts are owned. |
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
   intended for public consumers. A public repository must never call a
   private reusable workflow: GitHub's access model permits public callers to
   use public workflows only. Put common non-secret logic in `.github`; run
   sensitive coordination through a separate mechanism with its own explicit
   authorization boundary, not as a private-workflow dependency of a public
   caller. Private repositories may call public or authorized private reusable
   workflows. [GitHub: reusable workflow access rules](https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations#access-to-reusable-workflows)
3. Keep reusable workflows on immutable full commit SHAs. Human-readable
   comments may identify the corresponding tag/release, but tags are not the
   pin. Dependabot should propose pin updates; review provenance and diff
   before merging.
4. For CI that serves PRs, run on `pull_request` and `push` to `main` unless a
   repository has a documented reason otherwise. Use explicit PR event types
   only when they preserve the required check behavior. Do not add path filters
   to required checks unless a separate always-present gate ensures GitHub
   receives a definitive result. Keep schedules/manual runs for their
   additional purpose, not as substitutes for PR validation. If a repository
   has an active merge queue and a workflow produces a required check, that
   workflow must also handle `merge_group` and validate the candidate merge
   group; do not impose this trigger where no merge queue is used. [GitHub:
   required checks and merge queues](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#merge_group)
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
   implicit default. Permissions passed to a reusable workflow chain may stay
   the same or become more restrictive, but must never increase at a nested
   call. Include this property in workflow validation. [GitHub: nested workflow
   permissions](https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations#access-and-permissions-for-nested-workflows)
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
- Separate external dependencies (packages, Actions and tools) from internal
  Biopeia domain dependencies and pins. Dependabot must not be treated as an
  authority to promote internal domain revisions: retain the workspace/Lab pin
  and compatibility-contract process, and validate internal pin changes
  against the relevant cross-repository checks. For applicable Python
  repositories, validate an actual `uv` dependency and lockfile update PR.
- CI for Dependabot-authored PRs must pass required checks with the default
  read-only `GITHUB_TOKEN` and without ordinary Actions secrets. Separate
  unprivileged code validation from any privileged triage or Project
  coordination job; grant credentials only to the latter when required, and
  verify the applicable Dependabot-secret behavior. [GitHub: Dependabot on
  Actions](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-on-actions)
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
| `observation` | `test-and-build` | Explicit permissions; remove its public-to-private reusable workflow dependency; keep public calls on `.github` and move sensitive coordination behind a separately authorized mechanism. |
| `lab` | `unit-tests`, `build-and-install`, `cross-repository-integration` | Explicit permissions; scope push to `main`; preserve Lab's integration responsibility and evidence boundaries. |
| `docs` | `registry`, `cross-repository`, `publication` | Explicit permissions per job; keep scheduled/dispatch validation and tag publication distinct; avoid granting publication write permissions to PR CI. |
| `.github` | `validate-pr-contract` and reusable triage/intake behavior | Add CI validating reusable workflow syntax/contracts and safe reusable-workflow changes; keep each caller's permission boundary explicit. |
| `.github-private` | private CI and private intake/triage wrappers | Explicit least privilege; test workflows from authorized private consumers; document unavailable ruleset/protection settings and access constraints. |
| `workspace` | tooling checks, compatibility pin verification, public-head provenance smoke test | Explicit least privilege; maintain separation from semantic/domain acceptance; make manual-only workflows' inputs and evidence clear. |

Every tracked workflow must have an inventory row in the implementation
tracking artifact containing: path, purpose, event/triggers, `GITHUB_TOKEN`
permissions, external actions/reusable calls and pin type, secrets, required
check names, producing job, triggering event, provider/source and the exact
ruleset requirement for each check, owner, and a disposition (`keep`,
`normalize`, `replace`, `remove`). Record whether a merge queue is enabled.
This catches dormant or specialized workflows that a common-file template
would otherwise miss. A manually dispatched run does not satisfy a required
PR check; validate the check's eligible event source and the current PR SHA.
[GitHub: troubleshooting required status checks](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)

Automatic deletion of a merged remote head branch is independent of local
branch/worktree cleanup. It never authorizes deleting a local branch, worktree,
evidence, or in-progress work; those remain subject to the workspace's explicit
worktree-cleanup policy.

## 6. Rollout and acceptance

Implementation proceeds in small PRs after the design is accepted:

1. Re-fetch effective configuration and workflow inventory for all 11
   repositories; capture default branch and exact source revisions. For each
   required check record its name, producing job, event, provider/source and
   ruleset requirement; establish merge-queue use. Confirm which private
   settings and security features are observable/available. Treat the current
   design snapshot as preliminary until this inventory is complete.
2. Add testable configuration/templates first (Dependabot files and workflow
   conventions), then update repositories in bounded groups. Grouping must
   follow independent verification and access boundaries, not a goal of one
   giant cross-repository PR.
3. Set merged-branch deletion to enabled in all 11 repositories and verify
   with a disposable merged PR or the documented GitHub behavior where a test
   PR is inappropriate.
4. Update workflow permissions/triggers and reusable references while
   preserving required check names or updating branch rules in the same
   change. Exercise public and private reusable callers; verify nested
   permissions never increase, and test `merge_group` for required checks in
   repositories with merge queues.
5. Enable and validate Dependabot updates ecosystem by ecosystem. Exercise a
   real `uv` manifest/lockfile update where applicable, distinguish action
   version updates from immutable-SHA pin updates, and verify Dependabot PR CI
   with read-only token permissions and no ordinary Actions secrets. Inspect
   resulting manifests/lockfiles and CI before accepting update PRs. Track
   security alerts, security-fix PRs and any exception separately from routine
   version-update configuration. Internal Biopeia pin updates must retain
   workspace/Lab compatibility validation.
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
  because of trigger/path-filter behavior; their exact producer, event,
  provider/source and ruleset requirement are recorded. A manually dispatched
  workflow is not accepted as evidence that a required PR check is satisfied.
- Where merge queues are enabled, every required Actions check reports on
  `merge_group`; no such requirement is added to repositories without a queue.
- Dependabot update PRs pass required code checks with default read-only token
  permissions and no ordinary Actions secrets. Privileged coordination is
  isolated and tested separately.
- Reusable workflow permission scopes do not increase along any nested call
  chain; public callers use public reusable workflows only.
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
| Public code calls a private workflow that consumers cannot access | Prohibit the dependency; migrate common logic to public `.github` and keep sensitive coordination on a separately authorized path. |
| Dependabot CI depends on write permissions or ordinary Actions secrets | Keep code validation unprivileged; isolate coordination actions and verify Dependabot-triggered behavior with read-only token permissions. |
| Internal domain pins are updated without cross-repository compatibility evidence | Keep internal Biopeia pin promotion under the workspace/Lab compatibility process; Dependabot updates external packages and Actions but does not authorize internal revision promotion. |
| Private plans/settings cannot provide equivalent protection | State the capability gap, do not claim parity, and select a proportionate compensating control. |
| Too many Dependabot PRs burden one maintainer | Weekly cadence, compatible patch/minor grouping, modest PR limit; tune based on observed backlog rather than blanket auto-merge. |
| Branch cleanup removes an intentionally persistent branch | Only merged PR head branches are auto-deleted; protect documented long-lived branches and verify behavior. |
| Remote branch deletion is confused with local worktree cleanup | Treat remote auto-delete and local branch/worktree/evidence retention as independent operations; follow workspace cleanup policy before local deletion. |

The main alternative is to centralize every workflow in `.github`. Rejected:
it would blur domain ownership, make failures harder to attribute and couple
unrelated CI. The proposed design centralizes only reusable mechanics while
keeping validation semantics at the repository that owns them.

## 8. Related records

- Tracking Issue: [`biopeia/docs#143`](https://github.com/biopeia/docs/issues/143)
- Governance anchor: [ADR-0111 — Design-First Work and Governance Procedure](../../adr/ADR-0111-design-first-work-and-governance-procedure.md)
- Current delivery tracking: [Biopeia Project #1](https://github.com/orgs/biopeia/projects/1)
- ADR-0111 supplies the design-first process; it does not implicitly authorize
  these controls. Before acceptance, map every proposed durable cross-repository
  rule to existing policy and identify its acceptance authority. Explicitly
  decide whether uncovered durable rules require an ADR, a Decision Note, or
  another existing governed record; do not create one automatically or leave
  the ratification path implicit.
