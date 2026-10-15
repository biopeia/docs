# The life of an Organism, as the code has it

This document is derived. It adds no fact of its own: every statement comes
from one of the unit documents it links to, each of which names the commit it
was reviewed against, or from an accepted decision record. If a unit document
and this one disagree, the unit document is right and this one is out of
date. In the registry it depends on every unit it draws from.

The unit documents describe the Organism one mechanism at a time. This one
follows a single life through them, in order, and says at each stage what is
decided, what exists, and what joins that stage to the next. It is not a
report of an Organism living: no full-lifecycle runtime execution was examined.
The cognition and continuity synthesis is refreshed at
`organism@ba0011797a6a3b4d48c7731651e50560c4043f18`, with the World fixtures
reviewed at `world@95f5064c6b06bd66bb58a72110b066afe4ca70b0`. A composed
source operation, a test of it and an observed life remain different evidence.

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

| Stage | What exists | What joins it to the next stage, or remains absent |
|---|---|---|
| Being born | Caller-supplied identity, packaged seed genome and empty graph | No reviewed source birth operation creates and binds a complete Organism |
| Receiving a signal | Explicit opaque-signal binding; narrow scalar-field transduction | World sensing fixture reaches a hand-built graph, not the accepted checkpointed Organism step; birth graph still has no sense nodes |
| Activating and changing a weight | Source composition activates the graph and applies explicit per-edge learning instructions | Accepted cognitive step invokes it and checkpoints the result; the instructions still come from the caller |
| Changing structure | Rules that add or remove nodes and edges | No source caller of structural plasticity in the reviewed units |
| Finding what follows what | Per-channel correlation and counts of changes after commands | No documented running acquisition loop reports experienced transitions to these structures |
| Keeping a pattern | Statistics on four-step patterns, some marked usable | No documented path turns a retained pattern into a competence record, binding and affordance |
| Choosing and acting | Admission, arbitration and an in-source action coordinator | ActionDomain joins supplied decisions to registered commands and explicit closure; no reviewed runtime joins graph readouts to this path |
| Guessing ahead | Resident bookkeeping and adapters for supplied models | Accepted cognitive step preserves resident state but does not step it |
| Keeping a record | Episode format, bounded ledger and declared-cause log | No reviewed source producer constructs an episode from a lived transition |
| Being saved | Exact graph/cognitive payload inside an exact envelope; outer transition metadata | Optional state is caller-selected; structural and agency/actuation state are not all assembled |
| Resuming | Strict decoders and in-memory continuation leases | No durable cross-process continuation authority or full runtime restart established |
| Changing body | Dormancy/reactivation can replace a body reference, preserving envelope and identity | Private body-dependent bindings and competence are not rebound by that operation |
| Reproducing | Genetic fields and codecs | No reviewed reproductive operation produces offspring |

The right-hand column no longer says every connection is absent. Several
bounded compositions exist in source and have tests. What remains missing is
the runtime and complete state closure that would join them into a life.

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

[Opaque sense binding](sense-to-checkpoint-transition.md) now checks a
signal's channel and explicit provenance before it reaches a graph. Outside
the Organism, Modality has a narrow, stateless identity transduction for one
dimensionless scalar field ([Modality](../modality/current-state.md)). A World
fixture samples that field through a receptor and calls the sense-input
helper with a hand-built sense node. It does not call the checkpointed accepted
step or join sensing to motor selection.

Birth remains a separate boundary: the packaged graph is empty, and the
reviewed source does not add its first sense node. The accepted sense path
requires at least one binding, so the packaged defaults cannot enter that
path unchanged.

## Changing with what happens

[Graph plasticity](graph-plasticity.md) separates activation, weight changes
and structural changes. Three weight functions now have a source caller:
[the cognitive composition](sense-to-checkpoint-transition.md#the-composition)
computes predictor comparisons, updates eligibility and applies the weight
rule to edges named in explicit learning instructions. A checkpointed accepted
step invokes that composition and saves its graph and transition result.

This is a bounded composition, not an autonomous learning policy. The caller
supplies the selected edges, rate, modulation and eligibility/frozen flags;
the composition does not derive them from prediction error, gene values or
somatic state. Structural changes and shadow candidates still have no source
caller in the reviewed unit. The outer accepted step has no source runtime
caller in the seven repositories; tests exercise it.

## Finding what follows what

Two components keep what could become knowledge of consequences.
[Actuator evidence](actuator-evidence.md) keeps, for each channel, how its
activation went together with changes in what is perceived. It shows that
two series moved together, not that one caused the other.
[Effects, causal evidence and controllability](causal-evidence-and-controllability.md)
counts how often a change followed a kind of command compared with how often
it happened otherwise, and computes numbers it calls controllability and
agency. Nothing there intervenes or tests; it counts what a caller reports,
and the reviewed unit establishes no running producer of experienced transitions.

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
is decided in Embodiment and in a solver. An in-source `ActionDomain` now
joins intent materialization, arbitration, commitment registration, command
issue/execution and terminal closure. It creates an intent from a decision
only after checking consistency against a supplied supporting affordance;
the standalone intent constructor remains more permissive. The coordinator
does not authenticate the affordance's evidence or construct a learned
competence, proposal or controller for its caller. Unit tests and a World
physical-step fixture exercise the path, not a running Organism.

Two things could let the past weigh on a choice.
[The executive outcome ledger](executive-outcome-ledger.md) keeps the last
outcomes of each competence and effect and returns a factor that admission
multiplies in. [Prospective deliberation](prospective-deliberation.md) takes
candidates, asks a supplied function what each would lead to, and returns
the one whose outcome was valued highest. `ActionDomain.close` can now
record a supplied executive outcome sample in its supplied ledger, after
checking consistency with terminal status, reason and tick. It does not
observe consequences or infer that sample. The prospective-deliberation unit
still establishes no runtime use of the chooser's result, and the accepted
cognitive step does not call either mechanism.

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

[The cognitive checkpoint](cognitive-checkpoint.md) holds six cognitive and
memory parts and optionally the three genetic ones supplied as a group. The
graph codec now preserves weights and eligibility exactly; tests compare
future activation and learning transitions of live and restored copies.
Normalizer state, resident budget, reconciliation history and insertion order
are also preserved when supplied. The earlier rounding/reset description is
no longer true at this revision.

Completeness is a different question. Structural counts and agency/actuation
state are not in this cognitive composition. Experience records are included
only if supplied; an experience ledger's full state is not thereby assembled.
Models and the factual evidence resolver are external restore inputs; a
restored resident without them cannot resume all its operations. An exact
codec proves neither that every required component was supplied nor that all
external dependencies were declared.

[The accepted cognitive step](sense-to-checkpoint-transition.md#the-accepted-step)
restores the payload, replaces graph and cognitive transition state, carries
optional parts unchanged and wraps it in a new envelope. One step is then
counted by the outer
[Organism transition boundary](transition-and-continuation.md). That outer
state carries lifecycle, accepted-step counter and optional body/World
references. These are not missing fields of the inner cognitive payload:
they live one layer outside it. The accepted step does not run the resident,
agency, motor intent or expression regulator.

A continuation registry now refuses duplicate leases and stale continuations
within one registry object. Its snapshots and branching metadata do not
provide cross-process canonical authority: copied stores can grant separate
leases, and a durable atomic authority store is not implemented there.
Neither this registry nor the accepted step has a reviewed source runtime
caller. Round-trip and lease tests are not evidence of a complete deployed
restart.

## Changing body

The transition boundary permits `ACTIVE` to `DORMANT`, then `DORMANT` to
`ACTIVE` with a new explicit body-context reference. It preserves identity,
step count and opaque envelope through the change. It is therefore no longer
accurate to say that no body-context change operation exists.

Its limit matters just as much: the operation is told the lifecycle change,
and never opens private bytes. It neither rebinds sense channels nor
revalidates body-specific competence/evidence. The competence engine's
body-specific restore/reset behaviour and the binding registry's surface
checks must still be evaluated by the integration that performs the change.
A preserved envelope and new reference are not evidence that an Organism
recovers the use of what it acquired on another body. The relevant requirement
is [ADR-0104](../../technical/adr/ADR-0104-body-schema-and-competence.md), not
a result shown by the metadata operation.

## Reproducing, resting, ending

No operation produces an offspring. The words mutation, recombination and
inheritance appear in the genetics code as names of fields that a
reproduction step would need; the step is absent (the genome).

Dormancy and the death of an Organism are distinct events (ADR-0088).
The transition boundary now records explicit dormancy, reactivation and
termination requests and rejects transitions out of termination. It does not
decide those events from a body's death or a World's presence loss, and no
reviewed runtime drives them. A branch under a new identity is continuation
metadata, not reproductive offspring.

## What this adds up to

Several bounded pieces are now joined in source: checked signals can reach a
checkpointed cognitive step, admitted action can reach a registered command,
and explicit lifecycle/continuation operations can preserve identity metadata.
These are substantive changes from the earlier inventory of isolated pieces.

The reviewed evidence still does not show one runtime constructing complete
state, advancing these paths together, and handing sensory and motor
consequences to acquired change over a life. In particular, the World sensing
fixture and the accepted checkpointed cognitive step do not meet, and no
reviewed source connects cognitive readouts to action admission. This is an
integration and state-closure limit, not a claim that every local mechanism
is absent or that no component test is useful.

[The candidate hypotheses](../biopeia/research-hypotheses.md) set out the
experimental comparisons that remain unconfirmed. The tests of these bounded
paths constrain implementation; they do not demonstrate those hypotheses.
