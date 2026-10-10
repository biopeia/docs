# What Biopeia sets out to find out: candidate hypotheses

**Every hypothesis in this document is a candidate.** The hypotheses of
Biopeia are born from the owner's curiosity, in conversation, and an agent
writes them down; a hypothesis stays a candidate until the owner has
confirmed it (decision recorded on
[docs#99](https://github.com/biopeia/docs/issues/99), 2026-10-10). None has
been confirmed yet. This is a first draft to be argued with, assembled from
the project's public statement of purpose and from what the unit documents
say exists.

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

**What exists today.** The pieces, each tested alone. The evidence
structures are constructed nowhere, in source or in tests. The rules that
change the graph are called by nothing. What an activation correlated with
is not shown to be what it caused; the unit document says so.

**What stands in the way.** Nothing turns a phenomenon in the environment
into a signal for the Organism: Modality holds no transduction
([Modality](../modality/current-state.md)). Nothing reports a transition to
the evidence structures.

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

**What exists today.** Each piece, tested alone. The competence engine has
never been run against a body in the repository and is constructed only by
its own tests. No component turns a usable pattern into a competence record,
a binding and an affordance. The six steps of the action path are joined only
in a test fixture. The result of deliberation goes nowhere.

**What stands in the way.** The composition: something that owns the path as
a whole.

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

**What exists today.** The body's record and a few operations on it; nothing
advances a body through time. No component computes the six signals. No
component records a value.

**What stands in the way.** Somatic dynamics, which Embodiment records as a
required capability not yet implemented
([embodiment#20](https://github.com/biopeia/embodiment/issues/20)), and the
path from bodily state to the Organism.

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

**What exists today.** An identity and an envelope that carry bytes exactly.
The one thing that fills the envelope is not exact (a restored graph computes
different numbers) and not complete (it describes itself as "not a complete
Organism checkpoint"). No operation performs a re-embodiment. The competence
engine refuses to restore for another body and drops what it held for one.

**What stands in the way.** A decision on how much divergence a resumed
Organism may show, which the checkpoint document lists as open; and a
re-embodiment operation.

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

Read the five "what exists today" paragraphs together. In each, the pieces
are present and tested alone, and what would connect them is absent. No
hypothesis here can be tested at this revision, and the reason is the same
for all: there is no run of the whole, which
[One step across the domains](one-step-across-the-domains.md) shows link by
link. The first evidence any of them could have is the same evidence: one
Organism, in one body, in one World, acting over time.

How strong the support for a statement is, once there is some, is said in
the vocabulary of
[Evidence status and review status](../../reference/evidence-status.md).

## Open, for the owner

- Which of these, if any, is the question that started the project, and
  which is missing.
- Whether H3 is a hypothesis to be tested or a principle of design.
- For H4, how much a resumed Organism may differ from its uninterrupted self.
- Whether the evaluation criteria above, all of them candidates, are the
  right kind: each compares with a baseline and each can come out negative.
