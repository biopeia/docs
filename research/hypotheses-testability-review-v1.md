# Testability review of the candidate hypotheses H1–H5 (v1)

**Scope:** a methodological review of the five candidate hypotheses in
[What Biopeia sets out to find out](../explanation/biopeia/research-hypotheses.md).
It proposes nothing binding. The hypotheses are the owner's candidates
(docs#99); this report does not rewrite, confirm or reject any of them. It
asks, for each one, whether it is falsifiable as stated, what an experiment
would have to fix before running, and whether the current code could carry
that experiment at all. It authorizes no study and sets no numeric
threshold. Lab owns protocols; Organism owns the mechanisms named.

Checked on 2026-10-16 against `docs@23df190`, `organism@637bc21a7e2a`,
`world@d66ac6197c8e`, `embodiment@8f9576a8cf5b` and `lab@b583717a51ab`.

## How the claims stand today

The evidence vocabulary is that of
[evidence status](../reference/evidence-status.md). No row is above
*Covered by tests*, and no hypothesis has been tested.

| Hypothesis | Mechanisms that exist | Best evidence status of those mechanisms | Status of the hypothesis |
|---|---|---|---|
| H1 command → consequence acquired from experience | Actuator evidence, causal evidence counters, graph plasticity | Implemented; Covered by tests as bounded components | Untested candidate |
| H2 reusable behaviour from repeated action | Competence development, bindings, action path | Implemented; Covered by tests. The production cycle issues *bounded exploration*, not affordance-chosen action ([causal cycle](../explanation/world/causal-cycle.md); the exploration composer refuses to run while an intention commitment is active) | Untested candidate; no running acquisition-and-reuse loop |
| H3 organisation by internal regulation | Somatic body record; genome expression regulator | Implemented as records; no regulation loop | Not testable at these revisions (see H3) |
| H4 survival of restart and re-embodiment | Checkpoints, continuation, compact v5 history | Covered by tests: exact graph round trip; one continued tick after a fresh-process restore matches an uninterrupted run (`test_committed_cycle_restores_and_continues_in_fresh_process`) | Restart part partly a contract; re-embodiment part untested |
| H5 inherited differences | Genome table, codecs, germline record | Implemented. Gene values are loaded and persisted (`cognition/birth.py`, `portable_checkpoint.py`), but no behaviour reads them | Not testable at these revisions (see H5) |

## Per hypothesis

### H1. A relation between commands and consequences can be acquired from experience alone

- **Falsifiable as stated?** Yes, once "matches those effects more closely"
  has a metric. The shuffled-command comparator is the right kind: it keeps
  the signal statistics and breaks the contingency.
- **What must be fixed first.**
  1. **Ground truth.** For a body with known channels, state per channel the
     sign, or the rank, of each channel's effect on each perceived signal. One
     example is the effect of a small command on the receptor signal at a
     fixed posture. The metric is agreement between that ground truth and
     what the Organism records, such as sign agreement or rank correlation.
     "Closer" is then a difference in this metric between conditions.
  2. **A second control.** Shuffling commands also destroys their temporal
     structure. Add a *yoked* control: an Organism that receives another
     Organism's signal stream while issuing its own commands. Its signal
     statistics are identical, and its commands are causally disconnected
     from what it senses.
  3. **A hidden common cause.** Co-occurrence counting cannot tell a
     consequence from a change that shares a cause with the command. The Lab
     proposal for action-linked evidence under a hidden common cause
     (lab#59; `lab:migration/protocol-proposal-action-linked-hidden-common-cause.md`,
     PROPOSED) is the matching test. H1 should declare whether it depends on
     it.
  4. **"No label, no channel name with meaning."** This is a precondition
     on the software, not an outcome. Check it by code audit and record it
     with the run. Do not report it as a result.
- **Runnable now?** Not as an Organism-level claim. At these revisions the
  evidence structures are not joined to the production cycle's sensing.

### H2. Repeated action with consequences gives rise to reusable behaviour

- **Falsifiable as stated?** Partly. "Issued again more often than chance"
  needs an explicit null model.
- **Circularity risk.** A pattern is retained *because* it occurred often.
  It will therefore be issued often again under the same babbling
  distribution, whether or not it is reused. A comparison against "random
  patterns of the same length" does not remove that bias. The informative
  measure is **context-conditional**: the rate at which a retained pattern
  is issued when its recorded applicability context holds, minus the rate
  when it does not, compared across conditions. A lesion control helps: the
  same Organism with retention disabled, or retained patterns replaced at
  matched frequency.
- **What must be fixed first.** The applicability context and how it is
  observed from outside; the outcome measure, meaning that issuing the
  pattern is followed by the recorded change; the window; and the null.
- **Runnable now?** No. The production cycle issues bounded exploration
  commands, and no reviewed runtime derives a competence from a retained
  pattern and then uses it.

### H3. Behaviour can be organised by internal regulation, without one reward imposed from outside

- **Falsifiable as stated?** Not while its status is open. As a design
  *principle* it is a constraint and cannot be refuted by an experiment; it
  is checked by audit. As a *hypothesis* it needs three things. A viability
  measure, for example time until death on reserve depletion, which
  Embodiment implements (`embodiment 8f9576a`). A lesion comparator with the
  regulation disconnected. And an auditable definition of "a quantity
  supplied from outside the Organism and its body".
- **Precondition missing.** For choices to differ with bodily state, bodily
  state has to reach the Organism. In the World production cycle at
  `world@d66ac6197c8e`, the only signal that reaches it is the Environment
  scalar-field sample (stages 1–3 of the cycle). Embodiment declares
  interoceptive receptor identifiers (`physics3d/articulated_spec.py:73`), but
  no reviewed path transduces bodily state to the Organism. The earlier Lab
  transducer was removed (lab `81af15b`). Today, a run would show "no
  dependence on bodily state" by construction. **Such a negative result
  would be an artefact of the wiring, not a finding about regulation.**
- **Recommendation.** Decide the principle-or-hypothesis question first (it
  is already open for the owner). If it is a hypothesis, record its
  dependence on an interoceptive path as a precondition.

### H4. What was acquired survives a restart and a change of body, and the individual stays the same

H4 joins three claims of different kinds. They should be separated.

1. **Identity is preserved.** In the current design this is *definitional*:
   identity is carried by the checkpoint envelope and continuation records.
   It is verified as a contract by tests and audit, not discovered by
   experiment.
2. **A restored Organism behaves as its uninterrupted self.** In a
   deterministic simulator with exact restore, this reduces to byte or
   summary equality. That equality is already a tested contract for one
   tick. A behavioural "stated bound" adds information only if a source of
   nondeterminism is declared, or if restore is deliberately lossy. The
   owner already notes this distinction. The proposal is to keep exact
   continuation as an engineering contract, extend it to multi-tick
   equality, and not spend an experiment on it.
3. **After re-embodiment, prior acquisition shortens re-acquisition.** This
   is the scientific core. It fits a *savings* design: time to criterion on
   the new body for a transferred Organism, compared with (a) a naive
   Organism on the new body and (b) the same Organism re-acquiring on its
   original body after a reset. It needs a **competence criterion** observable
   from outside, which H2 also lacks. Without one, "returns faster" has no
   measure.

- **Runnable now?** Part 2 runs as a test today. Part 3 waits on a
  re-embodiment operation that rebinds body-specific state, and on H2's
  criterion.

### H5. What is inherited makes an observable difference, distinct from what is acquired

- **Falsifiable as stated?** Yes. The genome × experience design it
  describes is the standard one: crossing genomes with experience
  histories, then decomposing variance, or using intraclass correlation,
  between and within genomes.
- **Precondition missing.** Gene values are loaded at birth and persisted
  in the checkpoint, but no behavioural code path reads them. A run today
  would find no genome effect **by construction**.
- **What must be fixed first.** At least one consumer of gene values on a
  path that affects behaviour, decided by Organism. The sources of variation
  that "repeated runs of one genome" means: in a deterministic simulator,
  identical seeds give identical runs, so the replicates must vary declared
  seeds of the environment or of noise. And the measure in which the two
  sources are separated.
- **Runnable now?** No.

## Cross-cutting requirements for any of these studies

These restate practice already present in Lab's dispositions and in the
lab#59 proposal, applied to H1–H5.

1. **Replicates and seeds.** The simulator is deterministic, so a replicate
   is defined by the seeds that vary: environment genesis, initial state,
   noise. Every protocol must name which seeds vary and which stay fixed.
   Choose the replicate count by a design calculation, as in
   `lab:migration/protocol-design-calculation-hidden-common-cause.md`, not
   by convention.
2. **Pre-specification.** Fix the metric, comparator, window, analysis and
   decision rule in a reviewed protocol revision before any run. Report
   every pre-specified outcome, including negative and inconclusive ones.
3. **Effect sizes, not pass/fail.** Report an effect with its uncertainty
   across replicates. A threshold is a decision rule, not a result.
4. **Precondition audits are not results.** Absence of labels, absence of
   external reward, and that the cognition step is actually joined to the
   cycle: record each as an audited precondition of the run. Never count one
   as evidence for the hypothesis.
5. **Engineering tests are not experiments.** A unit or integration test
   constrains the software contract. Test names must not assert capability
   (cf. organism#174, which renamed a "measurably learns" test after it was
   shown not to beat a zero-output baseline; finding F-0071).

## Summary for the owner

- H3 and H5 cannot be tested at these revisions. Each lacks a code path:
  an interoceptive input for H3, a behavioural consumer of gene values for
  H5. Any run now would return a negative caused by the wiring.
- H2's chance comparison is circular as written. A context-conditional
  measure with a lesion control avoids that.
- H4 mixes a definitional claim, an engineering contract and one scientific
  claim, savings after re-embodiment. Only the last needs an experiment, and
  it needs a competence criterion.
- H1 is the closest to testable. It needs a ground-truth metric and a yoked
  control, and it is bounded by the hidden-common-cause question that the
  Lab proposal already addresses.
