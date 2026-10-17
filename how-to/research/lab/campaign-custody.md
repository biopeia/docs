---
diataxis_kind: how-to
document_id: HOWTO-LAB-CAMPAIGN-CUSTODY
domain: lab
source_of_truth: lab:migration/custody-reconciliation-80d372a.md; lab:docs/campaigns/longitudinal-learning-v1/
review_basis: lab@08f95d1ea737065e72ee00dc01ec7f2aa349ccb0
---

# How to keep a Lab campaign's evidence under custody

This guide describes how Lab already keeps the artifacts of a study or campaign
under custody:

- originals stay as they are;
- each artifact is recorded with its provenance and hash;
- deviations and rectifications are written down;
- negative and unresolved results are kept;
- admission is left to the competent authority.

**It adds no obligation.** Each step points to where Lab already does it.
Designing and running an experiment is covered by
[How to prepare, run and report a Biopeia experiment reproducibly](../experiment-reproducibility.md);
this guide starts once there are artifacts to keep.

Reviewed against `lab` at commit `08f95d1ea737065e72ee00dc01ec7f2aa349ccb0`.

**Custody is not acceptance.** Lab is the custodian of scientific evidence;
Observation emits facts but does not hold evidence
([ADR-0100](../../../technical/adr/ADR-0100-observation-capability-and-evidence-custody.md)).
A custody label says how an artifact is kept, not that it is valid
(`migration/custody-reconciliation-80d372a.md`, lines 7–13).

## Steps

### 1. Leave the original where it is, unchanged

The historical source stays read-only. Lab's custody reconciliation records
that "no source artifact was modified, copied, deleted, or scientifically
admitted". It also records that `symbiont-lab` "remains the read-only
historical source" (`custody-reconciliation-80d372a.md`, line 15).

When an original exists only somewhere volatile or private, and Lab copies it
into custody, the copy is byte for byte and is checked against the original by
hash. Campaign V1 did this: its scripts, data and dossier were copied from an
agent's private directory, and its run outputs from `/tmp`
(`docs/campaigns/longitudinal-learning-v1/provenance.md`, "Artifacts").

### 2. Record each artifact in a ledger

Lab's custody ledger, `migration/scientific-custody-80d372a.tsv`, has one row
per artifact. Its columns are:

`source_repository`, `source_path`, `source_commit`, `source_blob`, `bytes`,
`content_sha256`, `artifact_version_or_identity`, `custody_classification`,
`protocol_or_run_linkage`, `producer_or_source`, `seed_and_configuration`,
`custodian`, `known_limitations_and_rationale`, `proposed_review_class`,
`proposal_source_map`, `proposal_review_status`.

For a campaign's own record, Campaign V1 keeps comparable facts, not the same
columns, in `provenance.md`, with a `SHA256SUMS` file per directory. Where something could
not be established, the record says so: no clean-tree check, no environment
lock, no seeds. It is not filled in by inference ("Reproducibility limits",
"Not found").

### 3. Classify custody with the existing labels

The labels and their meanings are those the Architecture Owner ratified,
applied in `custody-reconciliation-80d372a.md`:

| Label | Means | Does not mean |
|---|---|---|
| `SCIENTIFIC_EVIDENCE` | kept as a result-bearing record | validated, reproducible, admissible or TARGET-applicable |
| `PROTOCOL` | kept as a protocol | scientifically accepted or executed |
| `HISTORICAL_RECORD` | retained historical material | — |
| `WORKING_ARTIFACT` | a working file | permission to delete |
| `DEFER` | an explicitly documented unresolved exception, preserved at source | admitted |

Owner-accepted rows carry `LAB_OWNER_ACCEPTED_CUSTODY_CLASSIFICATION;
NOT_SCIENTIFICALLY_VALIDATED; NOT_ADMITTED` in `proposal_review_status`.

### 4. Record a study's disposition separately from its custody

What Lab does with a historical study's method is a separate record:
`migration/study-disposition-register-80d372a.tsv`. Its dispositions include
`DEFER`, `HISTORICAL_PROTOCOL` and `REIMPLEMENT_METHOD`. Rows record an
owner basis. Every `DEFER` row also states a condition for reopening, as do a
few of the others. Whether a current research question
needs a historical method is the Lab Owner's decision, recorded per manifest
(for example [lab#141](https://github.com/biopeia/lab/issues/141), owner
comment 6223647599).

### 5. Keep unresolved, negative and inconclusive material

A `DEFER` row keeps its reason and a condition for reopening. It is
"preserved", "not silently classified" (`custody-reconciliation-80d372a.md`,
line 24). A result that is negative or inconclusive is kept like any other
result. The SCIENTIFIC work contract requires "negative/inconclusive results
retained" (`.github-private:workflow/agent-work-contract-v1.md` at
`361bd91e3d7359c7be70058f3d855b0e194f3d5a`).

### 6. Write deviations and rectifications next to the record; do not rewrite history

When the execution departed from the frozen protocol, list the departures in a
separate document. When a written account overstated the data, add a dated
rectification that keeps the historical version intact. Campaign V1 has both,
`deviations.md` and `dossier-rectification.md`. Its frozen protocol and its
original dossier are kept byte for byte. The principle is
[ADR-0076](../../../technical/adr/ADR-0076-preserving-scientific-meaning-without-backward-compatibility.md).

### 7. Make the hashes checkable

**Executable example** (from a Lab checkout at the revision above):

```sh
# from the root of the Lab checkout
(cd docs/campaigns/longitudinal-learning-v1/artifacts/original && sha256sum -c SHA256SUMS)  # 7 files: OK
(cd docs/campaigns/longitudinal-learning-v1/artifacts && sha256sum -c SHA256SUMS)           # archive and manifest: OK
python -m pytest -q tests/unit/test_campaign_v1_custody.py                                   # 6 passed
```

The custody test fails if a single byte of a preserved file changes. Lab's
migration records are checked differently:
`tests/unit/test_study_disposition_consistency.py` checks that the ledgers
agree with each other, and does not hash file contents.

### 8. Have the record reviewed by someone who did not write it

BAW-004 (`.github-private:workflow/review-policy.md`) requires at least one
independent review before merge when a change can materially affect
"migration disposition or scientific evidence handling". It also says that
"the reviewer must inspect the actual candidate diff and relevant primary
evidence". A reviewer is independent when they did not author the candidate.

As a precedent for one bounded historical-migration disposition, the Lab Owner
accepted an author-distinct review recorded in a comment. The condition was
that the exact candidate and any later changes are checked, because "a review
on an earlier candidate cannot silently approve later edits"
([lab#141](https://github.com/biopeia/lab/issues/141#issuecomment-6231876478)).

### 9. Leave admission to Lab

Custody records keep `NOT_ADMITTED` until Lab decides otherwise. For Campaign
V1, the program issue [lab#465](https://github.com/biopeia/lab/issues/465) is
kept open, by owner instruction, because review observations B3 and B4 still
block scientific acceptance.

## Example: Campaign V1

`docs/campaigns/longitudinal-learning-v1/` (lab#563, merged with the frozen
protocol from lab#561) is a custody record of an exploratory pilot. It is **not
an accepted result and not a demonstration of learning**. Its `README.md`
lists what may and may not be stated. It applies steps 1, 2, 6 and 7 to a
campaign that had none of them while it ran. It carries no custody label (step
3), and has not been admitted (step 9). For designing and running an
experiment, see
[the experiment reproducibility guide](../experiment-reproducibility.md).

## Undecided (for Lab's scientific owner)

1. **Where campaign records live.** Campaign V1 is kept in the Lab repository,
   including a 1.3 MB archive. No ratified rule sets the store, or the size
   above which artifacts go elsewhere.
2. **Admission.** The sources say who admits (Lab) and that custody is not
   admission. They state no criteria or procedure for admitting a campaign's
   evidence.
3. **Retention.** ADR-0076 says preservation "may" be required, and leaves
   item-level retention open.
