# The body's physical state and the adoption of a solver candidate

Reviewed against `embodiment` at commit `a5129f03aa4b024e33d332f917b9235afe97959c`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run, or an accepted decision.

## What it is

A physical solver computes where a body ends up after one step. That number
is a proposal. Something has to decide whether the proposal becomes the
body's position, and in Biopeia that something is meant to be the body's own
domain, Embodiment, not the solver
([ADR-0098](../../technical/adr/ADR-0098-physical-substrate-and-causal-integration.md)).

This component is where that happens in code. It holds where one body is and
how fast it is moving at one World causal tick, and it offers a single way
to move forward: hand it a solver's result together with the identity of the
step that was authorised, and it either returns the body's state at the next
tick or refuses. The module says of itself that it "does not execute a solver
or commit a World cut".

Only the free root of the body is covered: one position, one orientation and
two velocities. Joint angles of an articulated body live in a separate type
(`embodiment:src/embodiment/physics3d/articulated_state.py`) that is not
described here, and neither is the projection that turns this state into the
solver's input (`embodiment:src/embodiment/physics3d/physical_projection.py`).

## Three values

**The correlation**
(`embodiment:src/embodiment/physics3d/physical_transition.py::PhysicalStepCorrelation`)
names one physical execution: the World, the causal tick the step starts
from, the step, the body, the embodiment episode, and three revisions, of the
morphology, of the environment and of the solver configuration. Every text
field must be non-empty and is stored with surrounding whitespace removed;
the tick is a non-negative integer.

`adopt_candidate` now receives a `WorldPhysicalStepContext`, not a separately
supplied `expected_step`. Embodiment derives the expected correlation from
that context and requires the target tick to be the immediate successor of
the source tick. This is structural validation of a Python value, not
cryptographic proof of World authorization. Adoption returns a staged new
value; World chooses which reference becomes authoritative at commit.

**The candidate** (`SolverBodyCandidate`) is what a solver proposes: a
correlation, the names of the reference frame and body frame, a position in
metres, an orientation as an `xyzw` quaternion, a linear velocity in metres
per second and an angular velocity in radians per second, both expressed in
the reference frame. The code calls it an "Untrusted numerical result
proposed for owner adoption". Constructing one checks only the two velocity
vectors. A candidate with a non-unit quaternion can be built; it is refused
later, at adoption (ad hoc run).

**The state** (`EmbodimentPhysicalState`) is what Embodiment holds: World,
tick, body, episode, morphology revision, a pose, the two velocities, and
the correlation of the last step it accepted, if any. It carries a marker,
`state_owner`, whose only permitted value is `EMBODIMENT_OWNED`. It is
immutable.

A state cannot be built unless it is consistent with itself. The pose must
belong to the same body. If a last step is recorded, it must name the same
World, body, episode and morphology revision, its tick must be exactly one
less than the state's, and the pose must be labelled as produced by that
step. The morphology and body cases are covered by
`test_owner_state_rejects_last_step_with_mismatched_identity_or_revision`;
the others are read from the code.
Velocities must be three finite numbers
(`test_owner_state_rejects_invalid_root_velocity_vectors`). A state with no
last step is an initial state and may be created at any tick (ad hoc run).

## Adoption

Adoption takes a candidate and a World step context and returns a new state.
It proceeds in this order, and any failure raises without producing
anything:

1. Embodiment derives the expected correlation from the supplied context;
   the candidate's correlation must equal it, field for field.
2. That correlation must name this state's World, tick, body, episode and
   morphology revision.
3. The candidate's frames must be explicit and be the frames of the current
   pose.
4. A new pose is built from the candidate's position and orientation, which
   is where non-finite coordinates and non-unit quaternions are refused.
5. The new state is built one tick later, with the candidate's velocities
   and the expected correlation recorded as its last step.

The state adopted from is not changed, because it cannot be: adoption
returns another value
(`test_adoption_requires_exact_authorized_step_and_returns_new_owner_state`).
Changing any one of the eight fields of the correlation makes adoption fail
(`test_rejects_stale_or_wrong_correlation_without_mutating_owner_state`),
and so does a candidate whose correlation is right for the state but differs
from the expected one
(`test_current_candidate_cannot_be_adopted_under_another_authorized_step`).

A stale morphology is the case the decisions single out. A candidate
computed for a previous morphology revision does not match the state and is
refused; in World's integration fixture this leaves the World requiring
recovery rather than committed (see
[the physical causal step](../world/physical-step.md)).

The adopted pose is labelled with the identifier of the step. It carries no
sample time, and neither the correlation nor the state carries a duration.
The only clock in this component is the World causal tick, which adoption
advances by one.

## What adoption does not check

Read from the code and confirmed by running the module at that revision.

- **That World authorised the step.** The expected correlation is an
  argument. The caller supplies both it and the candidate, and Embodiment
  has no means to tell whether World authorised either.
- **The environment and solver revisions.** The state holds no environment
  or solver revision. Those two fields of the candidate are compared only
  with the same fields of the expected correlation. A correlation with
  invented values for both, and an invented step identifier, was adopted
  when candidate and expectation agreed.
- **That a step is adopted once.** Because adoption returns a new value and
  leaves the old one usable, the same starting state adopted two different
  candidates for the same step, giving two different states at the next
  tick. The adopted state does refuse the step it came from, since its tick
  has moved on. Which of several values is the body's state is decided by
  whoever keeps the reference. Environment's counterpart is an object that
  records the last step it accepted; see
  [the static scene](../environment/static-scene.md).
- **Physical plausibility.** A candidate placing the body 10¹² metres away
  with a velocity of 10³⁰ metres per second was adopted. The checks are on
  identity, frames, finiteness and the unit quaternion, nothing else.

The first two are Embodiment's side of what was already recorded for
Environment: each of the two domains defines its own type named
`PhysicalStepCorrelation`, with different fields, and neither can vouch for
the correlation it is given.

## Checkpoint

The state can encode itself as bytes: canonical JSON, keys sorted, under
schema version 2. Besides the fields of the state, the bytes name their
units and conventions explicitly: metres, `xyzw`, metres per second, radians
per second, and the frame the velocities are expressed in.

Restoring is strict. The set of fields must be exactly the expected one at
each level, the schema version must be 2, the units and the quaternion order
must be the supported ones, the velocity frame must be the pose's reference
frame, and the decoded state must pass every consistency rule above
(`test_checkpoint_restore_rejects_unsupported_units_and_malformed_bytes`,
`test_checkpoint_restore_rejects_inconsistent_last_step_and_nonfinite_pose_sample`).
A state encoded and restored equals the original and has the same digest
(`test_checkpoint_bytes_are_deterministic_and_restore_exact_adopted_state`).

Adoption now receives `WorldPhysicalStepContext`; Embodiment derives the
physical-step correlation from that context and requires the target tick to
be the immediate successor of the source tick. The context is a structural
Python value, not cryptographic proof of authorization. The transition is
staged; World selects which reference becomes authoritative at commit.

The component is explicit that bytes are not durability. Its checkpoint
"has no durable checkpoint reference until an
external store persists and verifies its bytes"; the state refuses to be
built with a durable reference, and its property `durably_referenceable`
always answers false, before and after a restore
(`test_adopted_state_explicitly_has_no_durable_checkpoint_reference`).
Nothing in this component writes a file.

Two things follow that a reader of World's documents should know:

- This physical-state type still does not itself provide World-owner
  checkpoint validation and restoration methods. In the reviewed World
  integration fixture, these operations are supplied by test code; that does
  not establish a production adapter or durable recovery path.
- A body therefore has two unrelated checkpoints, this one and the somatic
  one. This one names a World and a causal tick; the somatic one names
  neither.

## Lifecycle

What the code shows: a state is created by its caller with an initial pose;
it survives a restart only if its bytes were stored elsewhere and restored;
it is bound to one body and one embodiment episode and refuses steps that
name another.

What the code does not contain: any path for a body being replaced or for
reproduction. That a body's state ends with the body and that offspring get
their own is the intent of
[ADR-0094](../../technical/adr/ADR-0094-somatic-state-ownership-body-holds-organism-regulates-and-feels.md)
and
[ADR-0095](../../technical/adr/ADR-0095-surviving-semantic-authorities.md),
not behaviour that can be observed here.

## Correspondence with the decision on solver candidates

[ADR-0073](../../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md),
item 3, reads in part: "The solver has no semantic
authority and never mutates authoritative owner state directly", and lists
what a correlation includes: "World identity/tick, physical-step identity,
applicable body and
episode identities, Environment revision, morphology revision, and
solver/configuration revision".

Set beside the code: the correlation type has a field for each item of that
list, and the state can only change by adoption, which the solver does not
perform. The same item begins "World authorizes the causal physical
step"; this component receives a correlation and cannot tell who produced
it. This is a comparison of content, not a ruling on conformance.

## What supports this description

| Claim | Support |
|---|---|
| Consistency rules of the state, adoption from `WorldPhysicalStepContext`, immutability, checkpoint determinism and strictness, absence of a durable reference | Code and tests in `embodiment:tests/test_physical_transition.py` |
| Frames must match; non-unit quaternion and non-finite position refused at adoption, not at construction of the candidate | Code, and one ad hoc run of the module at that revision; no test is kept for these |
| Invented environment and solver revisions adopted; one state adopting two candidates for one step; implausible values adopted; initial state at any tick | Code, and the same ad hoc run |
| That owners adopt and solvers do not; what ends with a body | Accepted decisions ADR-0073, ADR-0098, ADR-0094, ADR-0095; statements of intent, not test results |

No run with a real solver, no stored checkpoint and no experiment was
examined for this document.

## Open questions

- Who defines the correlation of a physical step, and how an owner can know
  that World authorised it.
- Whether adopting a step once should be enforced by Embodiment or remains
  the caller's obligation.
- Whether the physical state should answer World's validation questions
  itself, and under which schema name.
