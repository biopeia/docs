# The causal provenance log

Reviewed against `organism` at commit `fc8a91c61d865663ba6f9468216171506fd29e7a`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run, or neither. Searches of the
repository were made on 2026-10-10 at that revision.

## What it is

A value in a running system has a history: something produced it, from
something else. The provenance log is a small structure meant to keep the
answer to one question about anything still in use: what were its immediate
causes?

It does this with three pieces
(`organism:src/organism/provenance.py`). A **reference** is a pair of
strings, a kind and an identifier, standing for some thing. An **event** says
that at a given tick, an operation on a subject, caused by a list of
references, produced a list of references. A **log** receives events, keeps
the most recent ones in a ring, and keeps a second table, the frontier, that
maps each produced reference to the event that produced it and to that
event's causes.

The module's own summary is "Timestamps say when; provenance says why." What
the log records is narrower than why. It records what its caller declared as
causes. It cannot check that the declared causes were causes, and it holds
"No raw values, no semantics: refs are structural kinds and opaque ids."

**No log exists in a running path at this revision.** One class in the
actuation code can emit events to a log if it is given one, and by default it
is given none. A search found no code, in source or in tests, that
constructs a log. The module has no test. Everything below about behaviour
comes from the code and from one ad hoc run.

## An event

An event (`organism:src/organism/provenance.py::CausalEvent`) carries a tick,
a domain, an operation, a subject, the causes, what was produced, an optional
rule name and a small table of scalar parameters. Its identifier is derived
from its content: the first 24 hexadecimal digits of a SHA-256 over all of
those fields. Two events with the same content therefore have the same
identifier (ad hoc run), and an event read back from plain data is refused
if the identifier it carries does not match its content.

Limits, read from the code and seen in the run:

- at most 64 causes; the list of produced references has no limit, and an
  event producing 500 was accepted;
- parameters must be scalars; a list was refused; floating-point values are
  rounded to twelve decimal places before hashing;
- the tick is whatever integer the caller gives. A negative tick was
  accepted, and the log does not require ticks to increase.

No host time enters an event. The tick is an argument.

## The ring and the frontier

Emitting an event does three things: appends it to the ring, records it in
the frontier under each reference it produced (or under its subject, if it
produced none), and passes it to any subscriber.

The ring holds the last 8192 events by default and forgets older ones. The
frontier does not forget by age. That is the design the module describes:
"The frontier is bounded by the number of live references, not by age, and
is checkpointed, so any live reference stays explainable after the ring
wraps."

Three properties of the frontier decide what that sentence means in practice.

**It keeps one level.** For a reference it holds the identifier of the
producing event and that event's causes. To go further back one asks about
each cause in turn, and the answer exists only if the cause is itself still
in the frontier. There is no function that walks the chain.

**It keeps the last word.** If a reference is produced a second time, the
entry is replaced. In the run, a reference first caused by one thing and
then produced again from another answered with the second cause only.

**Its bound is the caller's.** An entry leaves the frontier only when a
caller retires the reference. The log has no limit of its own on the
frontier: 9000 events with distinct subjects, none retired, left 8192 events
in the ring and 9000 entries in the frontier (ad hoc run). The bound stated
in the module holds if every producer retires what it stops using.

## The one producer

The registry of footprints in the actuation code
(`organism:src/organism/actuation/footprint.py::FootprintRegistry`) accepts
an optional log. When it has one, it emits an event for each estimate and
each new version of a footprint, naming as causes the commitments and
passive windows behind an estimate and the previous version and estimates
behind a version, and it retires the references a new version supersedes.
Its code states that "emission never changes registry behaviour". That
registry is described under
[causal evidence and controllability](causal-evidence-and-controllability.md);
it was read here only for these calls.

The module's opening says every state-changing decision emits an event. At
this revision one class can, and no other module imports the log.

## Subscribers, and a journal that is elsewhere

A log passes each event to callbacks registered with it. The module
describes them as "Outward-only observers (e.g. the lab journal); never read
back", and says that "Durable history is the lab's append-only journal, fed
passively from the observation stream; it never feeds back into the
organism."

Nothing in the Organism repository registers a subscriber, and the Organism
package imports nothing from Lab or Observation. Whether another repository
subscribes was not examined, and no code here would let it: there is no log
to subscribe to. The relation to a journal is, at this revision, a sentence
in a docstring. A subscriber is called inside the emitting call, and an
exception it raises would reach the emitter; the code does not guard
against that.

## Across a restart

A log writes its capacity, its count of emitted events and its frontier. It
does not write the ring. After reading a log back, in the run, the frontier
and the count were as before and the ring was empty. This is as the module
says, "The frontier only: bounded by live references, never by age", and it
means that after a restart the content of recent events is gone unless
something outside the Organism kept it. Subscribers are not restored.

Reading back checks the schema version and nothing else about the entries.

No checkpoint includes the log. A search of the checkpoint envelope and of
the composed cognitive payload, described under
[identity and the checkpoint envelope](identity-and-checkpoint.md), found no
reference to it.

## At each lifecycle boundary

| Boundary | What happens | Support |
|---|---|---|
| Birth | A new log is empty | Code |
| Checkpoint | The frontier and the count can be exported; the ring is not; no checkpoint includes the export | Code and ad hoc run; search of the repository |
| Restart | The frontier is rebuilt; recent events and subscribers are not | Code and ad hoc run |
| Re-embodiment | Nothing here reacts | Code; no operation performs a re-embodiment |
| Reproduction | No operation exists | Search of the repository |

## Beside the decisions

[ADR-0092](../../technical/adr/ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md)
says that Observation and Lab projections "do not confer write or semantic
ownership" over the Organism's private state. The log's subscribers are
described as outward-only, and the code gives a subscriber the event and
takes nothing back, which is consistent with that as far as it goes.

[ADR-0090](../../technical/adr/ADR-0090-host-wall-clock-time-is-never-implicit-causal-authority.md)
asks that causal times be explicit. The event's tick is explicit and
supplied. Which clock it belongs to is not stated by the type.

Neither is a finding of conformance. The decisions define a target, and the
log is not in use.

## What supports this description

| Claim | Support |
|---|---|
| Content of a reference and of an event; derivation of the identifier; the limit on causes; the ring and its default size; what emitting, retiring and exporting do | Code of `organism:src/organism/provenance.py` |
| Equal content gives equal identifiers; a mismatched identifier is refused; parameters are rounded and non-scalars refused; no limit on produced references; negative ticks accepted; a reference produced twice keeps its last causes; the frontier grows past the ring when nothing is retired; the ring is empty after reading back | Code, and one ad hoc run of the module at that revision. The module has no test |
| How the registry of footprints uses a log | Code of `organism:src/organism/actuation/footprint.py`, read for those calls only |
| No log is constructed in source or tests; no subscriber is registered; no other module imports the log; no checkpoint includes it | Searches of `src` and `tests` at that revision, made on 2026-10-10, for the constructor, the subscribe call and imports of the module |
| What a journal outside the Organism is meant to do with events | Docstring of the module; a statement of intent. The design document that docstring cites is not in the repository |

No event emitted by a run of an Organism was examined, because none can exist
at this revision.

## Open questions

- Which component creates the log for an Organism and hands it to producers.
- Whether the frontier should have a bound of its own.
- Whether the log belongs in the Organism's portable checkpoint, and what is
  expected to hold the events the ring forgets.
- Which clock the tick of an event belongs to.
