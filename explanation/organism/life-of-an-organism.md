# The life of an Organism, as the code has it

This document is derived. It adds no fact of its own: every statement comes
from one of the unit documents it links to, each of which names the commit it
was reviewed against, or from an accepted decision record. If a unit document
and this one disagree, the unit document is right and this one is out of
date. In the registry it depends on every unit it draws from.

The unit documents describe the Organism one mechanism at a time. This one
follows a single life through them, in order, and says at each stage what is
decided, what exists, and what joins that stage to the next. It is not a
story of an Organism living: at the revisions reviewed, no Organism has.

## The life that is decided

An Organism is one individual over time. It is born with an inherited
constitution and no acquired knowledge, acts through a body, changes with
what happens to it, and goes on being the same individual when its process,
its checkpoint or its body changes
([ADR-0081](../../technical/adr/ADR-0081-the-canonical-organism-is-longitudinal.md)).
A body can die without the Organism dying; dormancy, re-embodiment and death
are different events
([ADR-0088](../../technical/adr/ADR-0088-lifecycle-event-ontology.md)).
Reproduction, when it happens, originates in the Organism
([ADR-0087](../../technical/adr/ADR-0087-organism-originates-ordinary-reproduction.md)).
[What Biopeia is](../biopeia/what-biopeia-is.md) gives the rest.

## The life in one table

| Stage | What exists | What joins it to the next stage |
|---|---|---|
| Being born | An identity that is wrapped, a genome read from a packaged seed, an empty graph, empty tables | Nothing in source performs a birth |
| Receiving a signal | A function that turns a raw reading into a bounded number | No transduction exists; nothing adds a first sense node |
| Activating | One pass of arithmetic over the graph, at an explicit tick | Nothing calls the transition |
| Changing | Rules that move weights and add or remove nodes and edges | No code calls them, together or at all |
| Finding what follows what | Per-channel correlation; counts of changes after commands | The structures are constructed nowhere |
| Keeping a pattern | Statistics on four-step patterns, some marked usable | Constructed only by its own tests; nothing turns a pattern into a competence record |
| Being able to use it now | A table of bindings to a body's surface; a resolver | Nothing consults the table |
| Choosing | Admission with a factor from past outcomes; a second chooser by expected value | No code ends an attempt and records it; the second chooser's result goes nowhere |
| Acting | Six steps from an affordance to a motor command | Joined only in a test fixture |
| Guessing ahead | Bookkeeping for guesses and their later confirmation | There is no model; only an interface for one |
| Keeping a record | A format for an episode and a bounded list; a log of declared causes | Nothing creates a record from something that happened |
| Being saved | An exact envelope; one payload that fills it | The payload is not exact and not complete; most state is exported by nothing |
| Resuming | Decoders that rebuild what was saved | Nothing in the package restarts anything |
| Changing body | Refusals and flags in two components | No operation performs a re-embodiment |
| Reproducing | Fields that a reproduction step would need | No operation produces an offspring |

Read the right-hand column. At every stage the mechanism is present, and
what would hand its result to the next stage is not. The sections below say
the same thing stage by stage, with what each unit document adds.

## Being born

Two values answer which Organism this is and what must be kept for it to
continue: an identity, which is a wrapped identifier supplied by the caller,
and a checkpoint envelope
([identity and the checkpoint envelope](identity-and-checkpoint.md)).

What it inherits is a genome: an immutable table of 42 numbers. Five numbers
derived from it can be moved by a regulator, between bounds the genome sets,
and a germline record notes what they were at birth
([the genome](genome-and-inheritance.md)). Nothing outside the genetics
directory reads a gene value, so at this revision the inheritance does not
reach the mechanisms it would be expected to shape.

What it knows at birth is nothing, and here the code agrees with the
decision: the packaged graph is empty and the initial state has no tick and
no values ([the cognitive graph](cognitive-graph.md)); every ledger and table
below starts empty.

## Meeting an environment

A reading becomes a bounded number through a normalizer, and numbers placed
on some nodes of the graph are propagated in one pass
(the cognitive graph). That is all a pass does: no weight changes, nothing is
remembered inside the graph, nothing is done to a body.

What would feed it is missing on both sides. Outside the Organism, Modality
holds no transduction
([Modality](../modality/current-state.md)). Inside, the graph is born with no
sense node, and what is meant to add the first one is an open question of
the unit.

## Changing with what happens

The functions that could change the graph are separate from the function
that runs it: rules that move the weight of an edge, rules that add and
remove edges and nodes, and two values meant to restrain them
([how the graph is changed](graph-plasticity.md)). No code calls them. Where
one runs, a test runs it; where several run in order, the order is written in
the test. The unit document draws the conclusion: it does not describe how an
Organism learns, only pieces from which a learning loop could be assembled.

## Finding what follows what

Two components keep what could become knowledge of consequences.
[Actuator evidence](actuator-evidence.md) keeps, for each channel, how its
activation went together with changes in what is perceived. It shows that
two series moved together, not that one caused the other.
[Effects, causal evidence and controllability](causal-evidence-and-controllability.md)
counts how often a change followed a kind of command compared with how often
it happened otherwise, and computes numbers it calls controllability and
agency. Nothing there intervenes or tests; it counts what a caller reports,
and no code reports to it.

## From a pattern to something that can be done

[The competence engine](competence-development.md) is told, each tick, what
the body's signals were and which activations were delivered, and proposes
the next ones. It keeps statistics about short patterns that recurred and
were followed by a similar change, and marks some as usable.

Having a pattern and being able to use it with the present body are kept
apart on purpose.
[An execution binding](execution-binding-and-affordances.md) says a
competence was confirmed on one particular surface and whether that still
holds; a resolver turns competences that pass into affordances.

Between the two there is a gap the units name: no component turns a usable
pattern into a competence record with an effect and a controller, and so
into a binding and an affordance.

## Choosing and acting

[The action path](action-path.md) runs in six steps from an affordance to a
motor command. The last record is still only a value; what happens to a body
is decided in Embodiment and in a solver. No code in the domain composes the
six steps.

Two things could let the past weigh on a choice.
[The executive outcome ledger](executive-outcome-ledger.md) keeps the last
outcomes of each competence and effect and returns a factor that admission
multiplies in. [Prospective deliberation](prospective-deliberation.md) takes
candidates, asks a supplied function what each would lead to, and returns
the one whose outcome was valued highest. No code records an outcome or a
value outside tests, and the result of deliberation is used by nothing.

[Attention allocation](attention-allocation.md) ranks candidates by
uncertainty and cost within a budget; nothing uses it.

## Guessing ahead and keeping a record

[The generative resident](generative-resident.md) picks one unresolved item,
asks whatever answer-producing objects are plugged in for a guess, files it,
and later marks it as agreeing or disagreeing with what happened. Everything
it stores is labelled as not being an observation. There is no model in the
repository: no weights, no training, no inference.

[The experience record and its ledger](experience-record-and-ledger.md) are
a format for one episode and a bounded list of them. Nothing recalls,
retrieves by content or consolidates, and nothing creates a record from
something that happened.
[The provenance log](causal-provenance-log.md) keeps, for anything still in
use, what its caller declared as its causes.

Much of this state lives in bounded tables that drop something when full;
[capacity pressure](capacity-pressure-and-pair-statistics.md) counts what a
table did at its limit. The constants that would turn counts into classes
are mostly read by nothing
([foundation conventions](foundation-conventions.md)).

## Being saved and resuming

The envelope carries an identity, bytes only the Organism understands, and a
list of what those bytes depend on, and it carries them exactly
(identity and the checkpoint envelope).

One thing fills it:
[the cognitive checkpoint](cognitive-checkpoint.md), six cognitive and
memory parts and optionally the three genetic ones, as a caller supplies
them. Two properties decide what it is worth. It is not exact: a restored
graph is a rounded version of the saved one and computes different numbers.
It is not complete: it describes itself as "not a complete Organism
checkpoint".

Most components can write their state out and read it back, and the
component catalog records `preserve` for them at checkpoint and restart.
Their unit documents add what that leaves unsaid: the experience ledger, the
provenance log, the competence engine, the executive outcome ledger, the
value ledger and the binding registry each have an export that no composed
checkpoint carries. Being able to be saved and being saved are different,
and for those six only the first is true.

A restored resident comes back with no models and no resolver unless they
are passed in again, so until then its reconciliation is inert.

## Changing body

No operation performs a re-embodiment. What the components would do if one
did is recorded in the component catalog, and it is not uniform:

- Most keep their state unchanged: the envelope has no field that names a
  body; ledgers are keyed by competence, effect or outcome, not by body.
- The competence engine refuses to restore for another body and drops the
  candidates it held for one. The decision that re-embodiment must not
  silently erase what was learned
  ([ADR-0104](../../technical/adr/ADR-0104-body-schema-and-competence.md))
  is the one to read beside it; whether patterns of an earlier body are meant
  to stay in Organism state while unusable is an open question of the unit.
- The binding registry reports a row for another surface as not executable,
  and no code marks it stale.
- Sense nodes are named by strings the caller chose; nothing rebinds or
  invalidates them.

## Reproducing, resting, ending

No operation produces an offspring. The words mutation, recombination and
inheritance appear in the genetics code as names of fields that a
reproduction step would need; the step is absent (the genome).

Dormancy and the death of an Organism are decided to be distinct events
(ADR-0088). None of the eighteen Organism units documents an operation for
either.

## What this adds up to

Eighteen mechanisms, each complete in itself and most of them tested, and no
Organism: nothing constructs them together, advances them tick by tick, and
hands the result of one to the next. That is not a defect of any one of
them. It is the piece that is missing, and several units ask in their open
questions which component is meant to be it.

Why it matters for what Biopeia wants to find out is in
[the candidate hypotheses](../biopeia/research-hypotheses.md): none of them
can be tested until something does.
