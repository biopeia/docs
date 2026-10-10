# The causal provenance log

Reviewed against `organism` at commit `ba0011797a6a3b4d48c7731651e50560c4043f18`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run, or neither. Searches were
repeated on 2026-10-11 over the source and tests of all seven repositories,
and the ad hoc run was repeated at that revision.

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
is given none. A search found no source, in any of the seven repositories,
that constructs a log. At the earlier revision no test constructed one
either and the module had no test. It now has one test file,
`organism:tests/source_unit/test_checkpoint_fail_closed.py`, which constructs
logs to exercise how a log and an event are read back from plain data. No
test hands a log to the class that can emit to it. What is said below about
emitting, the ring and the frontier still comes from the code and from one
ad hoc run; what is said about reading back also rests on those tests.

## An event

An event (`organism:src/organism/provenance.py::CausalEvent`) carries a tick,
a domain, an operation, a subject, the causes, what was produced, an optional
rule name and a small table of scalar parameters. Its identifier is derived
from its content: the first 24 hexadecimal digits of a SHA-256 over all of
those fields. Two events with the same content therefore have the same
identifier (ad hoc run), and an event read back from plain data is refused
if the identifier it carries does not match its content. Reading an event
back now requires exactly the nine fields the writer emits, the identifier
among them, each of its written type; a payload without an identifier, which
used to be accepted, is refused
(`test_causal_event_payload_round_trips_complete_serialized_state`,
`test_causal_event_payload_rejects_missing_or_unknown_serialized_fields`,
`test_causal_event_payload_rejects_malformed_serialized_field`).

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

Reading back used to check the schema version and nothing else. It now
requires exactly the four fields the writer emits, a positive capacity, a
non-negative count, and for each frontier entry a well-formed reference, an
event identifier of the written form, at most 64 causes and no repeated
reference; reading from nothing is refused
(`test_provenance_checkpoint_requires_complete_frontier`,
`test_provenance_checkpoint_rejects_malformed_and_duplicate_frontier_refs`,
`test_provenance_checkpoint_rejects_malformed_frontier_event_id`). What it
checks is form. An entry naming a well-formed identifier of an event that
never existed was accepted, and so was a count of zero beside a non-empty
frontier (ad hoc run); with the ring not saved there is nothing to check
either against. Recorded in finding F-0147.

No checkpoint includes the log. A search of the checkpoint envelope, of
the composed cognitive payload and of the transition state and continuation
that now wrap them, described under
[identity and the checkpoint envelope](identity-and-checkpoint.md) and
[the transition boundary](transition-and-continuation.md), found no
reference to it. The repository says of its stricter event reader that it
"does not make the bounded `ProvenanceLog` event ring durable, create a
complete Organism checkpoint, or establish full causal-history
continuation".

## At each lifecycle boundary

| Boundary | What happens | Support |
|---|---|---|
| Birth | A new log is empty | Code |
| Checkpoint | The frontier and the count can be exported; the ring is not; no checkpoint includes the export | Code and ad hoc run; search of the repository |
| Restart | The frontier is rebuilt from a complete, well-formed export and refused otherwise; recent events and subscribers are not restored | Code, tests in `organism:tests/source_unit/test_checkpoint_fail_closed.py` and ad hoc run |
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
| Equal content gives equal identifiers; a mismatched identifier is refused; non-scalar parameters are refused; no limit on produced references; negative ticks accepted; a reference produced twice keeps its last causes; the frontier grows past the ring when nothing is retired; the ring is empty after reading back; an exception raised by a subscriber reaches the emitter | Code, and one ad hoc run of the module at `organism` `ba0011797a6a3b4d48c7731651e50560c4043f18`. No test covers emitting, the ring or retiring |
| What reading a log or an event back requires and refuses | Code and tests in `organism:tests/source_unit/test_checkpoint_fail_closed.py`; the two accepted cases of form without substance by the same ad hoc run |
| How the registry of footprints uses a log | Code of `organism:src/organism/actuation/footprint.py`, read for those calls only |
| No log is constructed in the source of any repository; one test file constructs logs for the reader; no subscriber is registered; no other module imports the log; no checkpoint includes it | Searches of `src` and `tests` in the seven repositories at that revision, made on 2026-10-11, for the constructor, the subscribe call and imports of the module |
| What a journal outside the Organism is meant to do with events | Docstring of the module; a statement of intent. The design document that docstring cites is not in the repository |

No event emitted by a run of an Organism was examined, because none can exist
at this revision.

## Open questions

- Which component creates the log for an Organism and hands it to producers.
- Whether the frontier should have a bound of its own.
- Whether the log belongs in the Organism's portable checkpoint, and what is
  expected to hold the events the ring forgets.
- Which clock the tick of an event belongs to.
