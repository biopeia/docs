---
id: ADR-0112
title: "Repository Settings and GitHub Actions Baseline"
document_type: adr
owner: biopeia-project-owner
created: 2026-10-12
language: en
document_version: 1
---

# ADR-0112 — Repository Settings and GitHub Actions Baseline

## Status and authority

- **Status:** ACCEPTED — adopted by the Architecture/Repository Owner on 2026-10-13. This acceptance authorizes implementation planning, not live configuration changes.
- **Work class:** `ORDINARY`.
- **Operational risk:** `MEDIUM` for the later implementation; this record is
  documentation-only.
- **Decision authority:** Biopeia Architecture/Repository Owner for the shared
  operational baseline. Repository-owned contracts and any protected domain,
  scientific, frozen or constitutional authority remain with their existing
  competent owners.
- **Disposition:** Accepted on 2026-10-13 and recorded in [Docs Issue #145](https://github.com/biopeia/docs/issues/145#issuecomment-6134380656). Review, CI, merge, Issue state and Project state alone do not constitute a disposition.

## Context

The proposed [Repository Settings and GitHub Actions Workflow Normalization
v1](../design/governance/repository-settings-and-actions-workflow-normalization-v1.md)
defines a proportionate common baseline for the eleven Biopeia repositories,
including public and private repositories. Its aim is consistent safety and
maintainability for a one-person project without forcing identical workflows,
checks or domain responsibilities.

The design was merged as a proposal in [Docs PR
#144](https://github.com/biopeia/docs/pull/144). The registry continues to
classify it as `proposed`. [ADR-0111](ADR-0111-design-first-work-and-governance-procedure.md)
establishes the design-first process, but does not authorize this separate
repository-settings baseline. The proposed Biopeia Repository Contract v1 is
not ratified and is narrower in scope. Existing repository-specific rules,
including `.github`'s review path, remain authoritative within their stated
scope and must not be silently replaced by a common baseline.

The owner has determined that the shared rules in the design form a durable,
proportionate operational baseline. This ADR records that normative decision;
it does not repeat repository-by-repository implementation details.

## Decision

Adopt the referenced design as Biopeia's common operational baseline for
repository settings and GitHub Actions, subject to these boundaries:

1. Apply common safety and maintenance principles across all eleven in-scope
   repositories, including private repositories, while preserving repository-
   specific contracts, workflows, ownership and scientific/architectural
   authority.
2. Require least-privilege workflow permissions, safe reusable-workflow
   visibility boundaries, immutable references for third-party Actions, and
   checks whose names, events and provenance are explicit. Public workflows
   must not depend on private reusable workflows; nested workflows must not
   increase token permissions.
3. Enable deletion of merged remote feature branches consistently. This does
   not authorize deleting local branches, worktrees, evidence or unmerged work.
4. Maintain appropriate Dependabot security and version-update coverage for
   applicable ecosystems. Dependency automation does not authorize automatic
   merging or promotion of Biopeia-internal contract pins.
5. Keep protection and required-check rules proportionate to a one-person
   maintainer model. Do not require an unavailable independent approver or
   impose a gate that cannot be satisfied. Where a merge queue is enabled,
   required Actions checks must validate its candidate integration event.
6. Treat the design's implementation inventory and rollout as a separate
   phase. No live setting, workflow, branch rule, secret, credential, or
   Dependabot configuration changes are authorized by this ADR.
   Implementation requires scoped Issues, exact-revision evidence, and the
   approvals and repository access applicable to each change.

The proposed common layer is additive: where an accepted repo-specific rule is
stricter or more specific, retain it unless its competent authority explicitly
changes it. Any conflict must be recorded and resolved before changing that
repository. Private repositories require a separate capability and access
verification; inability to inspect a setting is not evidence of compliance.

## Alternatives considered

- **Treat the merged design as self-ratifying:** rejected. A PR merge confirms
  integration of the proposal, not acceptance of new durable policy.
- **Use ADR-0111 as blanket authority:** rejected. ADR-0111 governs process and
  explicitly does not implicitly authorize unrelated controls.
- **Use only a Decision Note:** rejected. The accepted baseline spans eleven
  repositories and establishes durable shared rules for workflow permissions,
  branch handling, dependency automation and merge checks; an ADR is the
  appropriate decision record.
- **Apply identical workflow files and required checks everywhere:** rejected.
  Repository responsibilities and contracts differ; normalization concerns
  safe defaults and explicit evidence, not uniform job graphs.
- **Change live configuration before ratification:** rejected. The design
  separates proposal, decision and implementation.

## Consequences

- The referenced design is recorded as `approved` in the canonical design
  registry with this ADR as its decision reference.
- A parent implementation Issue and independently verifiable subissues must
  be derived from the accepted impact matrix and tracked in Biopeia Project #1.
  The implementation should start with a verified current-state inventory,
  then proceed in small repository groups, including private repositories.
- Each repository's actual branch protection/rulesets, default branch,
  `delete_branch_on_merge`, workflow permissions, triggers, reusable workflow
  calls, required checks and Dependabot settings must be inspected at current
  revisions before edits. Unreadable settings and plan limitations must be
  recorded explicitly.
- Ordinary tests should not depend on privileged secrets. Workflows requiring
  GitHub App credentials or project mutation need separate permission and
  Dependabot-event handling.
- Existing domain-specific validation remains owned by its contract owner.
  CI success, merge, Project status or Issue closure does not establish
  scientific acceptance or cross-domain integration acceptance.
- A later change to this shared baseline requires a new decision or explicit
  supersession; individual repository implementation PRs do not silently
  redefine the common policy.

## References

- Governance and ratification Issue: [biopeia/docs#145](https://github.com/biopeia/docs/issues/145)
- Proposed design: [Repository Settings and GitHub Actions Workflow Normalization v1](../design/governance/repository-settings-and-actions-workflow-normalization-v1.md)
- Design proposal PR: [biopeia/docs#144](https://github.com/biopeia/docs/pull/144)
- Process authority: [ADR-0111 — Design-First Work and Governance Procedure](ADR-0111-design-first-work-and-governance-procedure.md)
- Existing `.github` review path: [biopeia/.github `docs/review-path.md`](https://github.com/biopeia/.github/blob/main/docs/review-path.md)
- Existing Project #1 coordination policy: [biopeia/.github-private `workflow/project-1-governance.md`](https://github.com/biopeia/.github-private/blob/main/workflow/project-1-governance.md)
