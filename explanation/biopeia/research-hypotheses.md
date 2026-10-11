# What Biopeia sets out to find out: candidate hypotheses

**Every hypothesis in this document is a candidate.** The hypotheses of
Biopeia are born from the owner's curiosity, in conversation, and an agent
writes them down; a hypothesis stays a candidate until the owner has
confirmed it (decision recorded on
[docs#99](https://github.com/biopeia/docs/issues/99), 2026-10-10). None has
been confirmed yet. This is a first draft to be argued with, assembled from
the project's public statement of purpose and from what the unit documents
say exists.

This synthesis was refreshed after the cognition/continuity review at
`organism@ba0011797a6a3b4d48c7731651e50560c4043f18` and the cross-domain
review at `world@95f5064c6b06bd66bb58a72110b066afe4ca70b0`. It extends
neither review's evidence.

Nothing below is a result. Where it says what exists, it repeats a unit
document, which names the revision it was reviewed against. If a unit
document and this one disagree, the unit document is right.

## The question

[What Biopeia is](what-biopeia-is.md) gives the question the project asks:
what an artificial organism can come to do when its capabilities develop from
its own experience. The public statement adds the discipline under which it
is asked: a working implementation does not establish a capability; a claim
needs experiments, baselines, reproducibility and stated limits; a negative
or inconclusive outcome is a result.

## Why several hypotheses and not one

"The Organism learns" could mean at least five different things, and showing
one would not show the others. An Organism could acquire a relation between
a command and its consequence and still never form a reusable behaviour. It
could do both and lose everything when its body changes. It could keep
everything and owe nothing to what it inherited. The decision records keep
some of these apart already: a mechanism of reproduction, endogenous
reproduction, population dynamics, selection and evolution are distinct
([ADR-0082](../../technical/adr/ADR-0082-canonical-reproduction-is-endogenous-to-life.md)).

So each candidate below is stated as something that could be observed from
outside, with what would count as evidence for it, the mechanisms that bear
on it, and what stands between those mechanisms and a test. The words learn
and understand are avoided on purpose: what can be checked is what an
Organism does, and what it was given.

## The candidates

### H1. A relation between commands and consequences can be acquired from experience alone

**Candidate statement.** An Organism that starts with no information about
what its channels do comes, after acting, to hold a record of which commands
were followed by which changes in its signals, and that record is accurate
for the body it has.

**What would count as evidence (candidate).** For a body whose channels have
known effects, the Organism's record matches those effects more closely
after experience than before, and more closely than the record of an
Organism that received the same signals with commands shuffled. Inspection
of everything the Organism was given shows no label, no channel name with
meaning and no simulator identity.

**Mechanisms that bear on it.**
[Evidence that an actuator does something](../organism/actuator-evidence.md)
keeps, per channel, how activation went together with changes in what is
perceived.
[Effects, causal evidence and controllability](../organism/causal-evidence-and-controllability.md)
counts how often a change followed a kind of command compared with how often
it happened otherwise.
[The cognitive graph](../organism/cognitive-graph.md) and
[how it is changed](../organism/graph-plasticity.md) hold weights and rules
that could move them.

**What exists today.** The evidence structures are not an integrated
acquisition loop. A bounded
[sense-to-checkpoint composition](../organism/sense-to-checkpoint-transition.md)
now accepts bound opaque signals, activates a supplied graph, applies
caller-selected weight updates and saves the result as one accepted step.
Its parameters do not themselves come from prediction error, the genome or
an experiment selected by the Organism. Correlation is still not evidence
that an activation caused a change.

**What stands in the way.** The World sensing fixture samples an Environment
scalar field and passes it through Modality's narrow identity transduction
([Modality](../modality/current-state.md)) to a bound sense node. It uses the
sense-input helper, not the accepted checkpointed step, and joins neither
action selection nor the evidence structures to sensing. The packaged birth
graph is empty and the reviewed source supplies no first sense node. Those
bounded paths are not the acquisition process proposed in H1.

### H2. Repeated action with consequences gives rise to reusable behaviour

**Candidate statement.** Short patterns of activation that recur and are
followed by a similar change come to be kept, and are later used again in
circumstances where they apply.

**What would count as evidence (candidate).** Patterns are retained that
were not present at birth; a retained pattern is issued again, later, more
often than chance; and issuing it is followed by the change recorded for it.
The comparison is with an Organism whose retained patterns were replaced by
random ones of the same length.

**Mechanisms that bear on it.**
[How a repeated motor pattern becomes a competence](../organism/competence-development.md)
keeps statistics about four-step patterns and marks some as usable.
[Execution bindings and affordances](../organism/execution-binding-and-affordances.md)
separates having a pattern from being able to use it with the present body.
[From an affordance to a motor command](../organism/action-path.md) is the
path a use would take.
[The executive outcome ledger](../organism/executive-outcome-ledger.md) and
[prospective deliberation](../organism/prospective-deliberation.md) are the
two places where past outcomes could change what is chosen next.

**What exists today.** The competence and deliberation units do not
establish a running acquisition-and-reuse loop. The action path now has an
in-source `ActionDomain` coordinator. Its `admit` operation creates an intent
and checks consistency against the supplied supporting affordance; the
standalone intent constructor remains permissive. The coordinator arbitrates
a commitment, issues and validates commands, and can close an action with a
caller-supplied outcome sample. Unit tests and a World physical-step fixture
exercise that composition. It neither derives a competence from a retained
pattern nor authenticates the affordance's evidence or observes the outcome.

**What stands in the way.** A path from experienced consequences to an
acquired competence, binding and affordance, and a runtime joining that path
to sensing and action. The coordinator is not evidence that a retained
pattern is acquired or reused by an Organism.

### H3. Behaviour can be organised by internal regulation, without one reward imposed from outside

**Status of this one is itself open.** The public statement lists "internal
regulation without a global reward" among its research *principles*: a
constraint on how the system is built. Whether it is also a claim to be
tested, that such an Organism does come to behave in an organised way, or
only a rule the design obeys, has not been decided. It is written here as a
candidate so that the question is not lost.

**Candidate statement.** With no single externally assigned objective, what
an Organism does comes to depend on the state of its body, in a way that
tends to keep that body viable.

**What would count as evidence (candidate).** Choices differ with bodily
state; over a life, an Organism with the regulation spends longer viable
than one whose regulation is disconnected; and no quantity supplied from
outside the Organism and its body enters the choice.

**Mechanisms that bear on it.** A body holds energy, integrity, damage and
age, and the Organism holds what regulates
([ADR-0094](../../technical/adr/ADR-0094-somatic-state-ownership-body-holds-organism-regulates-and-feels.md);
[somatic state](../embodiment/somatic-state.md)).
[The genome's expression](../organism/genome-and-inheritance.md) moves five
numbers in response to six signals.
[Prospective deliberation](../organism/prospective-deliberation.md) keeps a
running value per outcome.

**What exists today.** The somatic-state unit describes a body record
and operations, not a demonstrated regulation loop. The action coordinator
can record supplied executive outcomes; that is not computing a value from
bodily state. The cognitive accepted step calls neither the expression
regulator nor prospective deliberation.

**What stands in the way.** The path from bodily state through interoceptive
transduction to Organism choices, and evidence that those choices preserve
viability without an externally imposed reward. Somatic dynamics are tracked
by [embodiment#20](https://github.com/biopeia/embodiment/issues/20); the issue
and somatic-state unit, not this candidate, carry their implementation status.

### H4. What was acquired survives a restart and a change of body, and the individual stays the same

**Candidate statement.** After a checkpoint and a restore, an Organism
behaves as its uninterrupted self would have. After re-embodiment it is the
same individual, keeps what it acquired, and recovers the use of it.

**What would count as evidence (candidate).** A restored Organism and its
uninterrupted twin, given the same inputs, diverge by no more than a stated
bound. After a change of body, the state acquired before is still present,
and behaviour that depended on the old body returns faster than it was first
acquired.

**Mechanisms that bear on it.**
[Identity and the checkpoint envelope](../organism/identity-and-checkpoint.md);
[what a cognitive checkpoint carries](../organism/cognitive-checkpoint.md);
the decisions that the Organism is longitudinal and that re-embodiment must
not silently erase what was learned
([ADR-0081](../../technical/adr/ADR-0081-the-canonical-organism-is-longitudinal.md),
[ADR-0104](../../technical/adr/ADR-0104-body-schema-and-competence.md)).

**What exists today.** The cognitive checkpoint now preserves graph
weights and eligibility traces exactly; tests compare future activation and
learning transitions before and after restore. It remains explicitly
incomplete: structural counts, agency/actuation state and some external
dependencies are not assembled into one complete continuation. A
[transition and continuation boundary](../organism/transition-and-continuation.md)
now counts accepted steps and records lifecycle changes. Dormancy followed by
reactivation can change the body-context reference while preserving identity
and the opaque envelope. Its registry guards leases within one registry
object, not across processes or copied stores.

**What stands in the way.** Complete state/dependency closure, durable
continuation authority, and revalidation or rebinding of body-specific state.
Changing a reference does not itself make retained competence executable on
the new body. The owner still has to approve the behavioural comparison;
exact graph round trips already have a stricter local test and should not be
described as an unresolved rounding problem.

### H5. What is inherited makes an observable difference, distinct from what is acquired

**Candidate statement.** Two Organisms with different genomes, given the
same experience, come to differ in what they do; and that difference can be
told apart from differences produced by different experience.

**What would count as evidence (candidate).** With experience held equal,
behaviour varies with the genome beyond what repeated runs of one genome
show. With the genome held equal, it varies with experience. The two sources
can be separated in the same measure.

**Mechanisms that bear on it.**
[The genome, its expression and the germline record](../organism/genome-and-inheritance.md):
42 numbers, five of them moved by a regulator, and a record of what they
were at birth.

**What exists today.** The table, its reader and its codecs. Nothing outside
the genetics directory reads a gene value. No operation produces an
offspring: there is no mutation, recombination or copying from parent to
child.

**What stands in the way.** Consumers of the gene values. Reproduction is
not needed for this hypothesis, only two genomes; it is needed for anything
about lineages.

## Directions with nothing to test yet

Two directions are named by the project and have no mechanism documented, so
no candidate can honestly be written for them.

- **Communication and social learning.** Listed among the research areas of
  the public statement. No unit documents anything between two Organisms.
- **Population and evolution.** Decided to be distinct from reproduction
  (ADR-0082), and to originate in the Organism
  ([ADR-0087](../../technical/adr/ADR-0087-organism-originates-ordinary-reproduction.md)).
  They wait on a reproduction that does not operate.

## What all five have in common today

Some bounded compositions now exist in source and are exercised by tests:
opaque sensing, checkpointed cognitive progression, action execution and
continuation bookkeeping. It is no longer accurate to say that every piece
is tested only alone or that all connections are absent.

None of the reviewed evidence establishes a candidate above as a scientific
result. [One step across the domains](one-step-across-the-domains.md) says what
the fixtures join and leave apart; no reviewed runtime joins sensing,
choosing, acting, acquired change and complete continuation over a life.
Component tests can constrain parts of a candidate and expose failures, but
cannot substitute for its proposed experimental comparison.

How strong the support for a statement is, once there is some, is said in
the vocabulary of
[Evidence status and review status](../../reference/evidence-status.md).

## Open, for the owner

- Which of these, if any, is the question that started the project, and
  which is missing.
- Whether H3 is a hypothesis to be tested or a principle of design.
- For H4, the behavioural comparison and tolerance, distinct from the exact
  graph-payload round-trip contract already tested.
- Whether the evaluation criteria above, all of them candidates, are the
  right kind: each compares with a baseline and each can come out negative.
