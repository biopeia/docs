# From an affordance to a motor command

Reviewed against `organism` at commit `6543188ff302a5f2dc8002c0086252d6061e5310`.
The one place where the stages are joined is a test fixture of World, read at
`world` commit `c162b67e698de9b47450264402677b0165e6e20e`. Everything below
describes those revisions. Statements are marked by what supports them: the
code, the tests, an ad hoc run, or an accepted decision.

## What it is

Before anything moves in a body, the Organism has to produce a value that says
how much to apply on which channel. This document follows how such a value, a
motor command, comes to exist in the Organism package, starting from the
earliest record that something could be done at all.

The package does this in six separate steps. Each step produces a small record
and hands a few of its fields to the next. No step moves anything: the last
record is still only a value, and what happens to a body is decided elsewhere,
in Embodiment and in a solver.

The names of the records (affordance, intent, proposal, commitment) are taken
from the code. They are used here as names of data structures. This document
describes the operations performed on them and does not claim that an Organism
intends, decides or knows anything in a wider sense; nothing reviewed here
would support such a claim.

**The most important fact about this mechanism is that no code in the Organism
repository joins the steps.** Each is a separate class or function with its
own checks. Nothing in `src/` calls the admission function, the arbitrator,
the controller or the command binding; nothing in `src/` or in the Organism
tests ever constructs an intent, and a commitment is constructed only by one
test module. The only place where the six are executed in sequence is the
physical step fixture of World, described under
[the physical causal step](../world/physical-step.md). What follows therefore
describes six mechanisms and one hand-written composition of them, not a
running loop.

## The six steps at a glance

```text
ActionAffordance ──admit──▶ ProspectiveDecision ──copied by caller──▶ ActionIntent
                                                                          │ id only
ActionProposal ◀──────────────────────────────built by caller────────────┘
      │ arbitrate
      ▼
ArbitrationDecision ──read by caller──▶ ActionCommitment
                                              │ controller
                                              ▼
                                       ControllerFrame ──bind──▶ MotorCommand
```

Every arrow labelled "caller" is a place where the package offers no function:
whoever composes the path copies fields from one record into the next by hand.

## Step 1: an affordance

An affordance (`organism:src/organism/agency/affordance.py::ActionAffordance`)
is an immutable record naming a competence, an effect expected from it, an
optional context and embodiment, three numbers between zero and one
(prediction confidence, controllability, executability confidence) and
references to supporting evidence. The module describes its content as "this
competence appears executable now and is expected to produce this Effect in
this situation" and its status as "never checkpointed, without lifecycle,
without motor authority and without actuator semantics".

The record enforces the last of these in one narrow way: an evidence reference
that begins with `actuator.`, `motor.` or `channel.` is refused. The numbers
must lie in the unit interval. Nothing else is checked; in particular the
record does not know whether the competence it names exists.

The package contains a resolver that derives affordances from competence,
prediction, controllability and binding state
(`organism:src/organism/agency/affordances.py::AffordanceResolver`). It is not
constructed anywhere in the repository, in source or in tests, and it was not
exercised for this document. In the fixture the affordance is written out by
hand with constant values.

## Step 2: admission

Admission (`organism:src/organism/agency/prospective.py::admit_afforded_action`,
described by its own docstring as "Model-free executive admission of one
currently afforded competence.") takes a collection of affordances and returns
at most one decision. It is a pure function: it holds no state and changes
none. What it computes is arithmetic, and it is worth stating exactly.

1. **Which affordances are considered.** An affordance is a candidate if the
   caller supplies, for its competence, a finite number at or above the
   policy's readout threshold (0.1 by default). The size of that number beyond
   the threshold plays no further part. Affordances supplied through the
   second, "generative" argument are candidates without any readout.
2. **Relevance.** For each candidate two numbers are formed. The first is the
   larger of a caller-supplied epistemic value and one minus the affordance's
   prediction confidence. The second is a caller-supplied homeostatic
   relevance. Relevance is the larger of the two.
3. **History.** If the caller supplies a history callback, a candidate it
   reports as suppressed is dropped, and otherwise relevance is multiplied by
   the factor it returns. The intended source of that callback is the
   [executive outcome ledger](executive-outcome-ledger.md).
4. **Threshold and choice.** Candidates whose relevance is below the policy's
   minimum (0.2 by default) are dropped. Of the rest, the one with the highest
   relevance is returned; ties are broken by controllability, then prediction
   confidence, then the generative route, then the competence identifier.

Two consequences follow from the arithmetic and were confirmed by running the
function. Because relevance is at least one minus the prediction confidence,
a *less* predictable affordance outranks a more predictable one when nothing
else differs: of two candidates with prediction confidence 0.9 and 0.1, the
second was returned, and a single candidate with prediction confidence 0.9 and
no other relevance was not admitted at all. And the affordance's executability
confidence is not read: a candidate with executability confidence zero was
admitted.

The tests cover the conditions of admission:
`test_primitive_readout_alone_does_not_form_intent`,
`test_readout_plus_affordance_without_executive_admission_does_not_form_intent`,
`test_readout_plus_affordance_plus_admission_can_form_intent`,
`test_inactive_readout_is_not_represented`,
`test_homeostatic_relevance_can_admit_a_predictable_competence` and
`test_generative_anticipation_is_a_representation_route`. Despite the word
"intent" in their names, these tests exercise the function's return value; no
intent record is created in them.

The result (`ProspectiveDecision`) repeats the affordance's competence, effect
and prediction reference, carries the two relevance numbers, and lists where
it came from: a readout reference and the affordance identifier.

## Step 3: an intent

An intent (`organism:src/organism/agency/intention.py::ActionIntent`) is the
first mutable record on the path. It holds what the decision held, three
ticks (created, activated, last progress), a status and, once ended, a reason.

The status is a small state machine and is the whole of the record's
behaviour:

```text
PENDING ──▶ ACTIVE ──▶ SATISFIED | FAILED | INTERRUPTED | INVALIDATED
   └──────▶ REJECTED | INVALIDATED
```

Moving to any ending status requires a reason; no status can be left once it
is an ending one. Confirmed by running the module: a pending intent cannot be
marked satisfied, an active one cannot be activated again, a failed one cannot
be reactivated.

The record refuses a competence or an origin reference that begins with
`actuator.`, `motor.`, `channel.`, `joint.` or `controller.`. Its module says
of it: "It has no motor authority; only the ActionArbitrator grants that,
through an ActionCommitment." That sentence describes a design. What the code
establishes is narrower and is set out under
[what the path does not establish](#what-the-path-does-not-establish).

What is not checked, confirmed by running the module:

- **That an intent came from an admission.** No function turns a decision into
  an intent. An intent naming a competence that appears in no affordance and
  no decision was constructed without objection.
- **That an intent starts pending.** One can be constructed already active.
- **The order of ticks on activation.** An intent created at tick 5 was
  activated at tick 2.

An intent can be exported to a plain mapping and restored from one, and the
round trip returned an equal record. No Organism test covers the intent
record at all.

## Step 4: a proposal and its arbitration

A proposal (`organism:src/organism/actuation/action.py::ActionProposal`) is an
immutable request. It names a source, one of exploration, competence,
prospection, protection and regulation, optionally a competence, an effect
and an intent identifier, and carries an evaluation: up to eight numbers in
the unit interval, which the code describes as "Vector-valued evaluation;
deliberately not a scalar reward." A proposal from the exploration source may
not carry an intent, and one that carries an intent must name a competence.

The arbitrator
(`organism:src/organism/actuation/arbitration.py::ActionArbitrator`) receives
a set of proposals, optionally the commitment currently in force, and a tick,
and returns one of the proposals or none. It holds no state. Its rule is an
order of precedence between sources rather than a weighted sum, read from the
code and confirmed by running it:

1. Proposals whose estimated risk is 1.0 are discarded.
2. If any remaining proposal is from the protection source with a protective
   relevance above zero, the highest of these is returned. This happens even
   when a commitment is in force and has not reached its minimum duration.
3. Otherwise, if a commitment is in force and has not reached its maximum
   duration, nothing is returned and the commitment is to be kept. A
   commitment without a maximum duration is kept at every tick: with one in
   force, three ordinary proposals were refused at tick one million.
4. Otherwise proposals from the prospection or competence source that name a
   competence take precedence over all others, whatever the numbers: a
   proposal of that kind with effect confidence 0.01 was returned ahead of a
   regulation proposal with homeostatic relevance 1.0 and an exploration
   proposal with epistemic relevance 1.0.
5. Then regulation, then exploration, then whatever remains by identifier.

The arbitrator returns a decision and a reason string. **It does not create,
alter or end a commitment.** When a commitment has passed its maximum
duration the arbitrator returns a new proposal and the old commitment is left
active. The commitment's `interruptibility` field is not read by the
arbitrator or by anything else in the package. The arbitrator has no test in
the Organism repository and no caller in its source.

## Step 5: a commitment

A commitment
(`organism:src/organism/actuation/commitment.py::ActionCommitment`) is the
second mutable record. It names a proposal, optionally an intent, a
competence and an effect, the tick at which it started, a controller, the
fingerprint of an actuator surface and optionally an embodiment. Its status
begins as active and can be ended once, with a tick and a reason; a second
attempt to end it is ignored without error.

It can answer whether it is compatible with a given surface fingerprint and
embodiment, and it can be exported and restored with a strict check of the
field set (the round trip was confirmed by running it).

The commitment is where the sentence quoted in step 3 would have to be
enforced, and the code does not enforce it. Confirmed by running the module:

- A commitment naming a proposal identifier that never existed, and an intent
  identifier that never existed, was constructed and was active.
- Two active commitments were held at once. Nothing in the package records
  which commitment, if any, is the one in force; the arbitrator is told by its
  caller.

## Step 6: a controller frame and the command

A controller
(`organism:src/organism/actuation/controller.py::SequenceController`) holds a
fixed sequence of steps, each a set of pairs of actuator identifier and
activation, and a position in that sequence. Asked for a frame under an active
commitment whose controller identifier matches its own, it returns the
current step and advances; after the last step it returns the last step again
at every call. An empty sequence yields a frame with no channels.

The controller's position is the only state on the path that is neither
exported nor restorable: the class has no checkpoint. The tick it is given is
stamped on the frame and compared only with the commitment's start; frames for
tick 2 and then tick 1 were both produced, each advancing the position.

A frame is not yet a command. The code says so: "A frame cannot cross the body
boundary. ActionDomain must convert it into a provenance-bearing MotorCommand
under the active ActionCommitment." No `ActionDomain` exists in the
repository. The conversion that does exist is a function
(`organism:src/organism/actuation/command.py::motor_command_from_frame`). It
refuses an inactive commitment, a frame from another controller, commitment or
competence, a tick that is not an integer, precedes the commitment or differs
from the frame's
(`test_active_organism_commitment_binds_frame_to_explicit_causal_tick`,
`test_binding_rejects_frame_from_another_controller_or_competence`,
`test_binding_rejects_inactive_commitments_and_ticks_before_start`,
`test_binding_requires_explicit_integer_tick`,
`test_binding_rejects_frame_from_another_commitment_and_tick`).

Its own description of its limits is accurate: "It does not validate an
actuator surface, execute the command, or mutate the commitment/controller."
A frame naming an actuator that belongs to no surface was bound into a
command. The command identifier is supplied by the caller and is not checked
for reuse: two different identifiers were issued for one frame.

The result (`organism:src/organism/actuation/action.py::MotorCommand`) is an
immutable value: its own identifier, the commitment, controller and competence
it came from, a surface fingerprint, an optional embodiment identifier, a tick
and the channels. Each channel is an actuator identifier with an activation in
the unit interval; an identifier may appear once.

## The actuator surface

The channels of a command are named against an actuator surface
(`organism:src/organism/actuation/surface.py::ActuatorSurface`): a list of
channels, each with an opaque identifier, a legal range inside the unit
interval, a neutral value and an availability flag, together with a
fingerprint of the whole. The module states the intent: "The surface states
only which opaque commands are legal." Nothing about what a channel does is
present, and `test_surface_is_command_contract_not_body_model` checks that
some such fields are absent.

How the identifiers are made matters. Each is a hash of a fixed schema string
and the channel's ordinal position. The schema string still carries the
historical name `symbiont`. Read from the code and confirmed by
running it:

- Any two surfaces with at least two channels have the same first two
  identifiers. A surface of two channels and a surface of three built for
  another body shared them; only the fingerprints differed
  (`test_actuator_ids_are_unique_and_stable_for_same_body_cardinality`,
  `test_body_contract_metadata_changes_fingerprint_not_opaque_channel_ids`).
- A surface built from named physical ports does not keep the names. Built
  from the ports `left, right` and from `right, left` with the same contract
  string, the two surfaces were equal: same identifiers, same fingerprint.
  Without a contract string the fingerprints differed and the identifiers were
  still the same.

So an actuator identifier identifies a position in a list, and which physical
thing sits at that position is known only to whoever built the surface.

The package also contains a class
(`organism:src/organism/actuation/system.py::ActuatorSystem`) that checks a
command against a surface: same fingerprint, every channel present, available
and in range. It returns, per channel, the requested and the delivered value,
which are always equal (`test_system_rejects_channel_outside_surface`,
`test_system_rejects_command_for_another_surface`). It is described in the
code as handing a command "across the opaque body boundary"; what it does is
validate and return. It has no knowledge of commitments: a command naming a
commitment that was never created was accepted. The World fixture does not
use it.

## Time

No step on the path reads a clock, and the Organism package has none. Every
tick in every record, created, activated, started, generated, issued, is a
number handed in by the caller. The command binding insists that the issuing
tick equal the frame's tick and not precede the commitment; beyond that,
nothing relates the ticks of one record to those of another, and nothing
relates any of them to World's causal tick except the caller's choice to pass
that number in.

## What the path does not establish

- **That a command descends from an admission.** Each record carries the
  identifier of the one before it as a plain string. None of those strings is
  resolved. A command proves only that some active commitment object with a
  matching controller identifier was at hand when the function was called.
- **That exactly one commitment holds control.** See step 5.
- **That anything was executed.** A command is a value. The package's own
  record for an executed command (`ActionAttempt`) is not constructed anywhere
  in the repository.
- **That an outcome was fed back.** Nothing on this path ends an intent or a
  commitment in response to what happened afterwards, and nothing records an
  outcome in the executive outcome ledger.
- **Anything about cognition or learning.** In the only composition that
  exists, every input is a constant: the affordance is written by hand, the
  readout is the literal 0.9, the epistemic and homeostatic callbacks return
  nothing and zero, and the controller's sequence is one fixed step. The
  fixture says as much of itself.

## The one composition: World's physical step fixture

The fixture builds a surface of two channels, one affordance with prediction
confidence 0.4, and admits it (relevance 0.6 against a minimum of 0.2). It
copies the decision into an intent and activates it, builds one proposal from
the prospection source, passes it alone to the arbitrator, builds a commitment
by hand, and gives a controller one step that drives the first channel at 0.5.
Inside the World transition it asks the controller for a frame and binds it
into a command for the tick being committed.

From there the command leaves the Organism package. Embodiment projects it
onto effectors using a mapping from actuator identifier to effector that the
fixture itself writes down, and a solver is stepped. The fixture introduces
the Organism part with the comment "This exercises the target-native admitted
action path from an explicit," and continues that it is a deterministic
readout and no claim of cognition; it calls the controller "only the
low-level" controller, and says of the outbound path "Modality is not in this
outbound path".

The Organism's state in that fixture is a small JSON document written by the
fixture, recording the identifier of the last command. It is not built from
any of the records above and does not use the Organism's
[checkpoint envelope](identity-and-checkpoint.md). That the organism
checkpoint there is a stand-in is already recorded as finding F-0002.

## Beside the decision on commands

[ADR-0073](../../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md)
fixes two contracts that bear on a command. They are set beside the code here
without a ruling on conformance; the decision addresses Embodiment commands,
and the Embodiment side was not reviewed.

| The decision says | The Organism code at this revision |
|---|---|
| "Omission is not a command." An omitted channel "does not imply zero or neutral." | A command lists only the channels the controller named. The surface check returns results only for those, and an empty command yields an empty result. In the fixture one of two channels is commanded and the comment reads "the missing right channel remains NO COMMAND". Every surface channel nevertheless carries a neutral value, 0.0 unless set otherwise; nothing reviewed here applies it. |
| A command is bound to `body_id`, `embodiment_episode_id`, `morphology_revision`, `effector_id` and `command_kind`. | A motor command carries a surface fingerprint, an optional embodiment identifier and opaque actuator identifiers. It has no body, morphology revision, effector or kind. In the fixture those are supplied at Embodiment's projection. |
| "Array/list position is never authoritative." | An actuator identifier is a hash of the channel's position in the surface. |
| Public APIs have no implicit units; the effector descriptor defines the valid range. | An activation is a bare number required to lie between zero and one. |

[ADR-0095](../../technical/adr/ADR-0095-surviving-semantic-authorities.md)
assigns agency and competence to the Organism, and
[ADR-0092](../../technical/adr/ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md)
says internal conditions are exposed outward as Organism-emitted signals or
actions. A motor command is the only outward value on this path. Those are
statements of intent; this document does not test them.

## What supports this description

| Claim | Support |
|---|---|
| Conditions under which admission returns a decision | Code and tests in `organism:tests/source_unit/agency/test_executive_admission.py` |
| A less predictable affordance outranks a more predictable one; executability confidence is not read; readout size beyond the threshold is not used | Code, and one ad hoc run of the module at that revision; no test is kept for it |
| The intent state machine, and that an intent needs no admission, may be born active and may be activated before it was created | Code and the same ad hoc run; the intent record has no test |
| The arbitrator's order of precedence, that it holds no state and does not end a commitment | Code and the same ad hoc run; the arbitrator has no test |
| A commitment needs no arbitration; two can be active at once | Code and the same ad hoc run |
| What the command binding refuses | Code and tests in `organism:tests/source_unit/actuation/test_command_binding.py` |
| Controller repeats its last step, accepts repeated and decreasing ticks, has no checkpoint | Code and the same ad hoc run |
| Actuator identifiers depend on position only; reordered ports under one contract string give equal surfaces | Code, tests in `organism:tests/source_unit/actuation/test_surface.py` for the first part, the ad hoc run for the second |
| What the surface check accepts and refuses | Code and tests in `organism:tests/source_unit/actuation/test_system.py`; the acceptance of a command with no commitment from the ad hoc run |
| No Organism source joins the steps; the resolver, the arbitrator and the attempt record have no caller | Search of the repository at that revision |
| The composition in the fixture | Code of `world:tests/integration/physical_step/test_first_biopeia_physical_causal_step.py`; it was read, not run, for this document |
| What a command must be bound to, and that omission is not a command | Accepted decision ADR-0073; a statement of intent |

The modules that would produce the inputs of this path (the competence
library, the effect and controllability models, the execution bindings, the
prospective deliberation that offers a second route to a decision) were not
reviewed. No run of a composed Organism was examined, because none exists at
this revision.

## Open questions

- Which component is meant to own the path as a whole: construct the intent
  from a decision, the commitment from an arbitration, keep the one commitment
  in force, and close both when an outcome is known.
- Whether the controller's position belongs in the Organism's checkpoint. In
  the fixture the Organism state names a controller and an initial step, and
  no code reads them back.
- Whether the Organism-side surface check and Embodiment's projection are both
  meant to stand, and which of them is the body boundary.
