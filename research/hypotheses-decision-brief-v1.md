# Candidate hypotheses H1–H5: formulations for an owner decision (v1)

**Scope:** a decision brief for the owner. It quotes each candidate hypothesis
of [What Biopeia sets out to find out](../explanation/biopeia/research-hypotheses.md)
verbatim. It then separates what in each is an architectural principle, a
definition or contract, or a falsifiable hypothesis, and proposes a falsifiable
formulation. **Nothing here is accepted.** All five remain candidates
(docs#99). Owner direction of 2026-10-17: do not promote them automatically,
and do not fix results or tolerances before observable mechanisms and
protocols exist. Lab owns any protocol; Organism owns the mechanisms named.

The testability analysis behind these proposals is in
[the testability review](hypotheses-testability-review-v1.md). Code facts are
at `organism` `637bc21a7e2a`, `world` `d66ac6197c8e` and `embodiment`
`8f9576a8cf5b`.

**Naming.** Lab's scientific program (lab#465) labels its protocols H0 and
H1–H2, and lab#466 also uses H0/H1 for null and alternative hypotheses. To
keep one name per claim, the formulations below are written **DOC-H1 … DOC-H5**.
Their nulls are written N1 … N5.

## How to read each entry

- **Kind.** *Principle*: a design constraint, checked by audit, not refuted
  by experiment. *Definition or contract*: true by construction, checked by
  tests. *Hypothesis*: an empirical claim with a null that a run can fail to
  reject.
- **Proposed formulation.** One alternative and one null. Every unfixed value
  is written ⟨…⟩, to be set in a reviewed Lab protocol, never here.
- **Preconditions.** What must exist in code before a run can be informative.
  A run without them gives a negative caused by the wiring.
- **Decision for the owner.** The one question this brief cannot answer.

## DOC-H1 — command–consequence relation from experience

> **Verbatim.** An Organism that starts with no information about what its
> channels do comes, after acting, to hold a record of which commands were
> followed by which changes in its signals, and that record is accurate for
> the body it has.

- **Kind.** Hypothesis. The clause "starts with no information … no label,
  no channel name with meaning" is a **principle** (precondition audit), not
  part of the claim.
- **Proposed formulation.** Let *A* be the agreement, measured as ⟨sign
  agreement or rank correlation⟩, between the Organism's per-channel effect
  record and a ground-truth effect table for a body with known channels.
  DOC-H1: after ⟨exposure⟩ of contingent experience, *A* exceeds its value at
  birth and its value under (a) shuffled-command and (b) yoked controls by at
  least ⟨margin⟩ across ⟨replicates varying declared seeds⟩. N1: it does not.
- **Preconditions.** The evidence structures (actuator evidence, causal
  evidence) must be joined to the production sensing path. At these revisions
  they are not. A ground-truth table must also exist for the body used.
- **Decision for the owner.** Is "accurate for the body" to be measured
  against a ground-truth effect table (proposed), or by out-of-sample
  prediction of signal change?

## DOC-H2 — reusable behaviour from repeated action

> **Verbatim.** Short patterns of activation that recur and are followed by a
> similar change come to be kept, and are later used again in circumstances
> where they apply.

- **Kind.** Hypothesis.
- **Proposed formulation.** For retained patterns, let *R* be the issue rate
  when the pattern's recorded applicability context holds, minus the rate
  when it does not. DOC-H2: *R* exceeds ⟨margin⟩ and exceeds *R* under a
  lesion control (retention disabled, or retained patterns replaced at
  matched frequency). Issuing the pattern is followed by its recorded change
  more often than ⟨null rate⟩. N2: it is not.
- **Preconditions.** A runtime in which competence derived from retained
  patterns chooses actions. The production cycle issues bounded exploration,
  which refuses to run while an intent-backed commitment exists (docs#221).
- **Decision for the owner.** Does "used again" mean issued **conditionally on
  context** (proposed; avoids the circularity of comparing with chance), or
  only issued more often?

## DOC-H3 — organisation by internal regulation without external reward

> **Verbatim.** With no single externally assigned objective, what an
> Organism does comes to depend on the state of its body, in a way that tends
> to keep that body viable.

- **Kind.** Two claims. "No single externally assigned objective" is a
  **principle** of the project (audit). "Comes to depend on the state of its
  body … keeps it viable" is a **hypothesis**.
- **Proposed formulation (hypothesis part).** DOC-H3: action choice carries
  information about interoceptive state (⟨measure⟩ above ⟨threshold⟩), and
  time viable until reserve-depletion death (embodiment `8f9576a`) exceeds that
  of a lesion control with the interoceptive input disconnected, by ⟨margin⟩.
  N3: it does not.
- **Preconditions.** An authorized interoceptive path from bodily state to
  the Organism. None exists in World's production cycle. The earlier Lab
  transducer was removed (lab `81af15b`).
- **Decision for the owner.** Confirm the split: principle checked by audit,
  hypothesis gated on an interoceptive contract. No tolerance is set until the
  path exists.

## DOC-H4 — survival of restart and re-embodiment; same individual

> **Verbatim.** After a checkpoint and a restore, an Organism behaves as its
> uninterrupted self would have. After re-embodiment it is the same
> individual, keeps what it acquired, and recovers the use of it.

- **Kind.** Three claims.
  1. "Same individual": a **definition** carried by the checkpoint envelope
     and continuation records, checked as a contract.
  2. "Behaves as its uninterrupted self after restore": an **engineering
     contract** in a deterministic simulator. One continued tick is tested
     (`test_committed_cycle_restores_and_continues_in_fresh_process`);
     extending it to many ticks is a test, not an experiment.
  3. "Recovers the use of it after re-embodiment": a **hypothesis**.
- **Proposed formulation (part 3).** With *T* the time to reach ⟨competence
  criterion⟩, DOC-H4: *T* after re-embodiment of an experienced Organism is
  lower than *T* for a naive Organism on the same new body, by ⟨margin⟩ across
  ⟨replicates⟩ (a savings design). N4: it is not.
- **Preconditions.** A re-embodiment operation that rebinds body-specific
  state, and an externally observable competence criterion. DOC-H2 needs the
  same criterion.
- **Decision for the owner.** Accept the three-way split, and state that no
  behavioural tolerance is set until the competence criterion exists. Owner
  direction already says this.

## DOC-H5 — inherited difference distinct from acquired

> **Verbatim.** Two Organisms with different genomes, given the same
> experience, come to differ in what they do; and that difference can be told
> apart from differences produced by different experience.

- **Kind.** Hypothesis.
- **Proposed formulation.** In a genome × experience crossed design, DOC-H5:
  between-genome variance of ⟨behavioural measure⟩ at fixed experience
  exceeds within-genome variance across ⟨replicates varying declared seeds⟩,
  and the genome and experience components are separately estimable
  (⟨variance decomposition or ICC⟩). N5: the genome component is not
  distinguishable from zero.
- **Preconditions.** A behavioural consumer of gene values. None exists
  (organism#48), so a run today is negative by construction.
- **Decision for the owner.** Keep DOC-H5 as a **future** hypothesis until
  Organism decides on a consumer. Owner direction already says not to build
  one only to test it.

## Summary

| Candidate | Principle or definition parts | Hypothesis part | Runnable now? | Owner decision |
|---|---|---|---|---|
| DOC-H1 | No labels or meaningful names given (audit) | Effect record accuracy | No: evidence not joined to sensing | Metric: ground-truth table or prediction |
| DOC-H2 | — | Context-conditional reuse | No: no competence-driven runtime | Accept the conditional measure |
| DOC-H3 | No external objective (principle) | Bodily-state dependence and viability | No: no interoceptive path | Confirm the split |
| DOC-H4 | Identity (definition); exact restore (contract) | Savings after re-embodiment | No: no rebinding or criterion | Confirm the split |
| DOC-H5 | — | Genome × experience separation | No: no gene consumer | Keep as future |
