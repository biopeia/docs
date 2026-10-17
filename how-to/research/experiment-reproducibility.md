---
diataxis_kind: how-to
document_id: HOWTO-LAB-EXPERIMENT-REPRODUCIBILITY
domain: lab
source_of_truth: lab#465, lab#466, lab#467; .github-private:workflow/agent-work-contract-v1.md (SCIENTIFIC)
review_basis: lab@08f95d1ea737065e72ee00dc01ec7f2aa349ccb0
---

# How to prepare, run and report a Biopeia experiment reproducibly

This guide puts in order the steps that Biopeia's existing rules already
require of an experiment. **It adds no rule.** Every step names the source
that requires it. Where the sources leave something undecided, the guide says
so instead of filling the gap; see [Undecided](#undecided-for-the-competent-owner).

Reviewed against `lab` at commit `08f95d1ea737065e72ee00dc01ec7f2aa349ccb0`
and `.github-private` at commit `361bd91e3d7359c7be70058f3d855b0e194f3d5a`.
The program issues were read on 2026-10-17.

**Current state: no experiment is authorized.** The scientific program
([lab#465](https://github.com/biopeia/lab/issues/465)) and its protocol
issues ([lab#466](https://github.com/biopeia/lab/issues/466) for habitat H0,
[lab#467](https://github.com/biopeia/lab/issues/467) for H1–H2) are open. Their
readiness gates are not met. This guide describes the path a protocol takes;
it does not open it.

## Who decides what

| Decision | Competent authority | Source |
|---|---|---|
| A scientific question, protocol or claim | Lab, as scientific apparatus; approval stays with the designated scientific authority | [ADR-0102](../../technical/adr/ADR-0102-lab.md); `review-policy.md`, "Authority-class overrides" |
| Durable evidence custody and admission | Lab / scientific apparatus. Observation emits facts and is not evidence | [ADR-0100](../../technical/adr/ADR-0100-observation-capability-and-evidence-custody.md) |
| Mechanisms under test (cognition, causality, body, environment) | Each owning domain | ADR-0102; lab#466 "Proposed design" |
| Whether a candidate hypothesis becomes an approved research question | The owner | [docs#235](https://github.com/biopeia/docs/issues/235); [research hypotheses](../../explanation/biopeia/research-hypotheses.md) |

An experiment, its scripts and its analyses are **SCIENTIFIC** work
(`agent-workflow.md`). Agents may prepare methods and evidence "only within an
authorized scientific protocol and custody model" (`agent-work-contract-v1.md`,
SCIENTIFIC).

## Steps

### 1. Start from a question the program has opened

Work under a protocol issue that is a child of lab#465, not from a free-standing
idea. lab#465 lists the research lines and the five gates. The first two are
executed, nontrivial learning relative to naive baselines, and verified
longitudinal continuation. Habitats H0, H1 and H2 are experimental conditions
set by Lab. **They are not goals or rewards for Organism** (lab#465, "Scientific
direction ratified for investigation").

State the question in observable terms. A candidate hypothesis from
[the research hypotheses](../../explanation/biopeia/research-hypotheses.md)
stays a candidate. Its owner disposition (docs#235) selects research
questions, not results. New Lab protocols name their operational hypotheses
`LAB-<PROTOCOL>-H<n>` (docs#235).

### 2. Write each hypothesis with its null

Every hypothesis needs a stated null, or an outcome that would count against
it. Write the outcome so that a run can come out negative. Required by
agent-work-contract-v1 ("explicit scientific question/hypothesis") and by lab#466
("explicit null hypotheses and controls").

The measure is set by existing decisions, not by what changed inside
Organism:

- lab#465 gate 1 asks for "executed, nontrivial learning relative to naive
  baselines";
- the owner's disposition of DOC-H1 makes held-out prediction of the following
  signal change the primary measure (docs#235);
- for DOC-H2, "used again" means context-conditional issuance followed by the
  observed effect, compared with matched controls, "not raw issue count".

A weight change or the appearance of a primitive is therefore not, by itself,
a measure of learning. For how strongly evidence supports a statement, use the
vocabulary in [evidence status](../../reference/evidence-status.md).

### 3. Choose the controls and baselines the protocol issues already name

| For | Controls and baselines named | Source |
|---|---|---|
| H0, development from birth | passive/yoked and randomized-action controls; plasticity-disabled control; birth structures A empty, B small, C larger; persistence, zero and random baselines; holdout sequences; causal ablation; equivalent exposure "as feasible" | lab#466, "Proposed design" |
| H1–H2, adaptation and transfer | matched seeds for changed and unchanged trajectories; frozen-plasticity, reset-organism and no-action controls "where scientifically meaningful"; held-out configurations | lab#467, "Design principles" |

No success signal may enter Organism (lab#466).

### 4. Fix the seeds, and check their pairing and disjointness

Lab provides seed checks and paired summaries. They are covered by
`tests/unit/test_pairing.py` and `tests/unit/test_statistics.py` at the
revision above.

**Executable example** (run against `lab@08f95d1`; outputs shown as observed):

```python
from lab.studies.common.pairing import assert_disjoint_seeds, assert_paired_seeds, assert_unique_seeds
from lab.studies.common.statistics import aggregate_metric, mean_delta, paired_deltas

treatment_seeds = [101, 127, 149]
control_seeds = [101, 127, 149]          # matched: same seeds, different condition
holdout_seeds = [163, 179]               # kept out of analysis design
assert_unique_seeds(treatment_seeds, "treatment")
assert_paired_seeds(treatment_seeds, control_seeds)
assert_disjoint_seeds(treatment_seeds, holdout_seeds, "design", "holdout")

treatment = [0.42, 0.40, None]            # None: a run that produced no value
baseline = [0.40, 0.41, 0.39]
paired_deltas(treatment, baseline)        # [0.02, -0.01]: pairs with a missing value are dropped
mean_delta(treatment, baseline)           # 0.005
aggregate_metric(treatment)               # {'mean': 0.41, 'median': 0.41, 'std': 0.0141..., 'count': 2}
```

`assert_paired_seeds([1, 2], [2, 1])` raises `ValueError: Seed pairing
mismatch`, because pairing is positional. These helpers summarise; they do not
test significance. `paired_deltas` silently drops a pair with a missing value,
so the dropped pair is absent from the summary.

### 5. Preregister the estimands, acceptance criteria and stopping conditions

Before any run, write down:

- what is measured;
- the comparison;
- what counts as positive, negative and inconclusive;
- when the run stops.

lab#466 lists these as deliverables: "Pre-register measurable learning against
persistence/zero/random baselines", plus "evaluation plan, power/replication
rationale, stop conditions and anti-leakage checks". lab#467 gate 3 asks for
"pre-specified adaptation/retention/transfer measures with proper controls and
uncertainty estimates".

### 6. Freeze the protocol, have it reviewed, and obtain run authorization

Publish the protocol at an exact Git revision with its file hash **before** any
data are collected, then have it reviewed by someone other than its author.
lab#466 readiness gate 4 requires that independent scientific review accepts the
protocol, budgets, controls, safeguards and stopping conditions. lab#467 gate 4
adds a "subsequent explicit run authorization". A passing test, benchmark or
run "does not by itself authorize a scientific claim"
(agent-work-contract-v1).

Under BAW-004 (`review-policy.md`), a reviewer is independent when they did not
author the candidate. For Lab documentary dispositions, the owner has accepted a
revision-pinned review recorded in a comment. A review of an earlier candidate
"cannot silently approve later edits"
([lab#141](https://github.com/biopeia/lab/issues/141#issuecomment-6231876478)).

### 7. Record an execution manifest while running

lab#466 asks to record the exact genome, seed, topology, revisions, timings,
sensory and effector traces, weights, nodes, edges, continuity identity and
checkpoints. agent-work-contract-v1 also requires "source-pinned inputs and
reproducible method". The sources give no exhaustive list. The items whose
absence limited Campaign V1's reproducibility are an illustration, not a
binding list:

- the clean-tree state of each repository;
- the environment lock;
- the exact command;
- the output paths;
- a configuration digest.

**Executable example** (`lab@08f95d1`, covered by `tests/unit/test_digests.py`):

```python
from lab.studies.common.digests import compute_config_digest

compute_config_digest({"protocol_id": "LAB-EXAMPLE-H1", "seeds": [101, 127, 149], "cycles": 20})
# '80ba1cff8a1fd604d739f77857290a364e128fb5d3c5eda8d6bbed225843d05c'
```

Lab's `ExperimentIntent` describes a planned operation for review. It is not an
authorization: `describe_intent` returns `'status': 'unapproved_intent'` and
dispatches nothing (`tests/unit/test_experiment_intent.py`,
`test_intent_does_not_authorize_execution`).

### 8. Record every deviation; never edit the frozen protocol

If execution departs from the frozen text (a parameter, a phase, a stopping
point, a script edited after a failure), record the deviation next to the
protocol. Report the results as outcomes of the variant actually run.
Correcting the protocol afterwards to match the results would make it
evidence of nothing. The preservation principle is
[ADR-0076](../../technical/adr/ADR-0076-preserving-scientific-meaning-without-backward-compatibility.md).

### 9. Report negative and inconclusive results, limitations and alternative explanations

agent-work-contract-v1 requires keeping "negative/inconclusive results" and
recording "limitations and alternative explanations". lab#465: "negative
results are valid".

### 10. Ask for acceptance from the competent authority

Evidence and claims are accepted by Lab as evidence owner, after independent
scientific review where required (agent-work-contract-v1). CI, a green test or
an Observation capture is not acceptance (ADR-0100). Keep the program issue
open until its own gates are met.

## Historical example: what Campaign V1 shows

The Campaign V1 pilot (2026-10-16) is a **record kept with care, not a learning
result**. Its custody record is in Lab under
`docs/campaigns/longitudinal-learning-v1/` (lab#561, lab#563). Read against
the steps above:

| Step | What happened |
|---|---|
| 5–6 | The protocol was written about four minutes before the runs, in the same session, and reviewed afterwards. It is classified as an exploratory pilot, not preregistered |
| 4, 9 | One deterministic run per cell; no seeds; no estimand |
| 7 | No clean-tree check or environment lock was recorded; the scripts used absolute paths |
| 8 | Execution deviated from the frozen text. The deviations are recorded in `deviations.md` without editing the protocol. This is step 8 done correctly |
| 2 | The pilot shows a weight change under an experimenter-scheduled update and the formation of one primitive. It shows **no** functional change (none was measured) and no adaptive learning |

lab#465 stays open; review observations B3 and B4 still block scientific
acceptance.

## Undecided (for the competent owner)

These are not settled by the sources above. Each is a decision for Lab's
scientific owner, not something this guide fixes:

1. **Replication.** lab#466 asks for a "power/replication rationale" but sets
   no minimum number of replicates or analysis convention.
2. **Preregistration record.** The sources require preregistration, but not
   where it is kept or how its timing is attested, for example a Lab PR merged
   before the first run.
3. **Run authorization.** lab#467 gate 4 requires an explicit run
   authorization; its form and its recording place are not specified.
4. **Long-term evidence store.** Lab is the custodian (ADR-0100). Campaign V1
   was kept in the Lab repository as a precedent, not as a ratified store.
