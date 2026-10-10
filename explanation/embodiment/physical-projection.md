# What Embodiment hands to a solver: the physical projection, the body pose and its conventions

Reviewed against `embodiment` at commit `a5129f03aa4b024e33d332f917b9235afe97959c`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run, or an accepted decision.

## What it is

A solver cannot compute a step for a body it has not been told about. It
needs the body's shape and mass, where the body is, and how fast it is
moving. In Biopeia the solver is meant to receive these from the body's
owner and to hold no truth of its own
([ADR-0098](../../technical/adr/ADR-0098-physical-substrate-and-causal-integration.md)).

This document describes the values through which that happens in code, and
the conventions they rely on:

- the **body pose sample**, the value in which a position and an
  orientation are written down;
- the **physical projection**, one immutable value assembled for one
  physical step and given to a solver;
- two **declarations** of the frames and units these values are meant to be
  read in;
- a **duration** type, the only value in Embodiment that names physical
  time.

None of them is state. They are built, passed and discarded. What the body
holds between steps is described in
[the body's physical state](physical-state.md) and
[the articulated body](articulated-body.md).

## The body pose sample

A pose sample (`embodiment:src/embodiment/observation.py::BodyPoseSample`)
says where one body's base is: a body identifier, the name of a reference
frame, the name of the body's own frame, a position of three numbers in
metres, an orientation as a quaternion in the order x, y, z, w, and three
fields about the moment of the sample: a kind, a value, and an optional
time in seconds. It carries a contract revision, `v1` unless stated.

It checks, on construction:

- that the identifier, the two frame names, the kind and the revision are
  not empty; surrounding whitespace is removed;
- that the position is three finite numbers, stored as floating point
  (`test_body_pose_sample_normalizes_numeric_coordinates`);
- that the orientation is four finite numbers whose squared length is
  within one hundred-thousandth of one
  (`test_body_pose_sample_rejects_non_unit_quaternion`). It is stored as
  given, not normalised;
- that the time, when given, is finite
  (`test_body_pose_sample_rejects_non_finite_sample_time`).

It has no World identifier
(`test_body_pose_value_retains_frame_label_without_world_identity`). The
reference frame `physics3d.world` is a label for a coordinate frame; the
repository's migration notes say it "is not a `WorldId`, world authority, or
presence identity".

What it does not check, confirmed by running the module at that revision:

- **The frames.** Any non-empty text is a frame name, and any non-empty text
  a contract revision. A sample in a frame called `mars.left-handed` under
  revision `v999` was built.
- **The moment.** The kind and the value are free: a sample of kind
  `anything` with the value `whenever` was built, and so was one whose value
  is not a number. The time may be negative. Nothing says which clock the
  time is read from.
- **Scale.** A position of 10³⁰⁰ metres is accepted.
- **Equivalence.** A quaternion and its negation describe one orientation
  and are two unequal samples.

The module describes its values as "not wire records" that "do not authorize
publication by themselves", and the class adds: "The concrete Physics3D
producer must prove/convert its inputs before constructing this value." No
such producer exists in the repository; the samples that exist are built by
the physical state when it adopts a candidate or restores a checkpoint, and
by tests.

## The projection

The projection
(`embodiment:src/embodiment/physics3d/physical_projection.py::BodyPhysicalInput`)
is the solver's input for one body and one step. One function builds it from
four things: a body specification, a pose sample, a step correlation, and
the root's two velocities. The result holds:

- the body identifier and the correlation of the step;
- the body kind;
- the pose: both frame names, the position and the orientation;
- the linear velocity in metres per second and the angular velocity in
  radians per second, in the reference frame;
- the **description** of the body, generated from the specification as
  text (see [the articulated body](articulated-body.md));
- the contact link names of the specification.

Covered by `test_projection_snapshots_pose_morphology_and_contact_links`.
The value is immutable and building it changes neither the specification
nor the pose
(`test_projection_is_immutable_and_does_not_mutate_owner_inputs`). Because
the description is text generated at that moment, changing the
specification's segments afterwards does not change a projection already
made
(`test_projection_captures_description_instead_of_live_mutable_spec_mapping`).

The module is explicit about what the value is not: "It is not a solver, a
semantic physics authority, or a body-state transition."

### What is deliberately left out

Nothing of the body's physiology is projected. The function's own comment
gives the reason: "the CURRENT model defines no mapping from those values to
solver mass, geometry, force or constraint parameters". A body's energy,
integrity, temperature or fatigue
([somatic state](somatic-state.md)) therefore has no effect on what a solver
is given.

### What the projection does not carry or check

Read from the code and confirmed by running the module at that revision.

- **Joint state.** The projection has no field for a joint's angle or
  speed. For an articulated body it gives a solver the shape and the root's
  pose, and nothing about the configuration of the joints.
- **The surface material and the fixed-base flag** of the specification.
  They are not in the description and not in the projection.
- **That its inputs belong together.** The function takes a specification,
  a pose and two velocities as separate arguments; it does not take the
  body's state. It checks one thing: that the correlation and the pose name
  the same body. A projection was built with a correlation naming another
  World, another tick, another episode and another morphology revision than
  anything else in hand, and with a velocity of 10³⁰ metres per second
  unrelated to any state.
- **That contact links exist.** A contact link name that is no link of the
  description is carried through.
- **Itself, when built directly.** Only the two velocities are validated
  (`test_projection_rejects_nonfinite_root_velocity`). Built without the
  function, a projection with an empty identifier, a non-numeric position
  and a description that is not XML was accepted.

The morphology revision in the correlation and the specification given to
the function are related only by the caller. A specification carries no
revision, so the function has nothing to compare.

## The declared conventions

A third module
(`embodiment:src/embodiment/physics3d/observation_contract.py`) writes down,
as two read-only tables, how poses and joints are meant to be read.

For a body pose: positions in metres, a right-handed frame, the positive z
axis up, quaternions in the order x, y, z, w, the reference frame
`physics3d.world`, the body frame `body.root`, revision `v1`.

For joint kinematics: hinge joints, positions in radians, velocities in
radians per second, identities local to a body, revision `v1`.

Each table can be obtained as a fresh copy, so a caller changing its copy
does not change the declaration
(`test_body_pose_semantics_are_canonical_and_copied`,
`test_joint_kinematics_semantics_are_canonical_and_copied`).

These are declarations and nothing more. The test file states it: its
assertions "do not verify that a runtime emits samples conforming to the
declarations or that any physical simulation is valid". A search of the
source and test trees of all seven repositories at their main branches on
2026-10-09 found the two tables read by their own test and by nothing else.
In particular:

- the pose sample does not consult them: it accepts any frame names and any
  revision, as shown above;
- the checkpoints of the physical state and of the articulated state name
  their units as text of their own, which agrees with the tables because
  the same words were typed in both places;
- handedness and the up axis are compared with nothing.

What does hold frames together across steps is narrower and lives in the
physical state: a candidate is adopted only if it names the frames of the
pose it replaces. A lineage of states therefore keeps the frames it started
with, whatever they were.

Environment declares the same two properties for its scenes in its own
words. Its frame is `RIGHT_HANDED` with up axis `Z`
(`environment:src/environment/static_scene.py`, read at
`environment@f97ec22272b6be1e6742770e37cd370e7d96d6bc`), where Embodiment
writes `right` and `+z`. Neither repository imports the other. That a body
and a scene given to one solver share a frame is ensured by whoever puts
them together.

## Time

Three notions of time touch these values, and they are not connected.

**The causal tick** is carried by the correlation inside a projection. It
is World's count of committed transitions.

**The sample time** of a pose is an optional number of seconds. The physical
state does not set it when it adopts a candidate: the pose it builds is
labelled with the identifier of the step and has no time (ad hoc run).

**The physical duration**
(`embodiment:src/embodiment/duration.py::PhysicalDuration`) is a number of
seconds described as "Continuous metric time elapsed in the physical
substrate, in seconds." It is a floating-point number that refuses to be
negative, infinite or not a number, and refuses anything that is not a plain
integer or float, including booleans and subclasses of either
(`test_physical_duration_accepts_plain_non_negative_numeric_seconds`,
`test_physical_duration_rejects_negative_or_non_finite_values`,
`test_physical_duration_rejects_non_plain_numeric_values`,
`test_physical_duration_rejects_other_numeric_subclasses`). It prints as
itself (`test_physical_duration_repr_is_explicit`).

The type holds a number someone supplies. The migration notes say of it that
"it does not measure or source time". The search named above found that
**nothing uses it**: no module in any of the seven repositories imports it,
apart from its own test. The pose's sample time is a plain float, not this
type. Its guarantees also end at construction: adding or subtracting two
durations gives a plain float, and the difference of a smaller and a larger
one is negative (ad hoc run).

So no Embodiment value records how much physical time a step covers. The
projection does not say how long the solver should advance, and the
candidate does not say how long it did. In World's fixtures the step is a
hundredth of a second because the fixture writes that number into the
solver's model, and it reaches the correlation only as part of a text the
fixture composes for the solver configuration revision.

[ADR-0090](../../technical/adr/ADR-0090-host-wall-clock-time-is-never-implicit-causal-authority.md)
reads: "Host wall-clock time is never implicit causal authority", and
requires that causal times "must be explicit and distinct". Set beside the
code: the source tree of `embodiment` at that revision contains no import of
a clock and no read of host time (search of 2026-10-09 for the `time` and
`datetime` modules), so nothing here takes its time from the host. A type
for physical time exists and is distinct from the tick. No value carries
it. The decision leaves open which authority advances each time. This is a
comparison of content, not a ruling on conformance.

## Where it is used

No source module of any repository builds a projection (same search). Two
integration fixtures of World do, described in
[the physical causal step](../world/physical-step.md); read at
`world@c162b67e698de9b47450264402677b0165e6e20e`.

In both, a function of the fixture parses the description as XML, takes
from it the masses, the sizes of the boxes and, for the articulated body,
the joint's origin, axis, limits and damping, and writes a model for MuJoCo
by hand. It then places the root from the projection's pose and velocities,
reordering the quaternion to the solver's own order. The description's
moments of inertia, torque limit and velocity limit are not used.

In `test_articulated_mujoco_candidate_is_adopted_and_world_committed`, the
second step starts from a restored state whose hinge is no longer at zero.
The fixture sets the hinge's angle and speed in the solver by reading them
from the restored state directly, since the projection does not carry them.

`test_procedural_spheres_are_adopted_committed_restored_and_reused` uses a
single-box body and checks, before stepping, that the projection names the
frame of the generated scene.

## Correspondence with the decisions

[ADR-0098](../../technical/adr/ADR-0098-physical-substrate-and-causal-integration.md)
says that "the physical substrate executes numerical coupled resolution over
owner projections". Set beside the code: there is one value that an owner
builds for a solver, and it is immutable and separate from the state. For
an articulated body it does not contain all of the state a solver needs, and
it is assembled from arguments that the function cannot tie to the state.

[ADR-0073](../../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md),
item 3, says that "Embodiment and Environment provide their projections".
The function exists; what calls it is a test.

This is a comparison of content, not a ruling on conformance.

## What supports this description

| Claim | Support |
|---|---|
| Checks of the pose sample; absence of a World identifier | Code and tests in `embodiment:tests/test_body_pose_sample.py`, run at that revision (all pass) |
| Content, immutability and snapshot behaviour of the projection; refusal of non-finite velocities | Code and tests in `embodiment:tests/test_physical_projection.py`, run at that revision (all pass) |
| Content of the two declarations and that copies are independent | Code and tests in `embodiment:tests/test_physics3d_observation_contract.py`, run at that revision (all pass) |
| What a duration accepts and refuses | Code and tests in `embodiment:tests/test_duration.py`, run at that revision (all pass) |
| Free frame names, revision, kind and value; negative time; unnormalised quaternion; projection built from unrelated inputs or directly; arithmetic on durations; adopted pose has no time | Code, and one ad hoc run of the modules at that revision; no test is kept for these |
| No joint state, material or fixed-base flag in the projection | Code (the fields of the value), and the same run |
| The declarations and the duration are read by nothing; no source module builds a projection; no clock is read | A search of the source and test trees of the seven repositories at their main branches on 2026-10-09 |
| How World's fixtures consume the projection; Environment's frame vocabulary | Code of the two fixtures under `world:tests/integration/physical_step/` and of `environment:src/environment/static_scene.py`, read; not run for this document |
| That a solver works over owner projections; that host time is not causal authority | Accepted decisions ADR-0098, ADR-0073, ADR-0090; statements of intent, not test results |

No run with a real solver and no experiment was examined for this document.

## Open questions

- Whether the projection of an articulated body should carry its joint
  state, and whether it should be built from the state rather than from
  separate arguments.
- Which value, owned by whom, records the physical time a step covers.
- Whether the declared frames and units should be enforced by the values
  that are meant to follow them, and how Embodiment's and Environment's
  frame declarations are to be compared.
