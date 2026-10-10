# What Embodiment hands to a solver: the physical projection, the body pose and its conventions

Reviewed against `embodiment` at commit `97cb09a82b0bc9bf4ad11f6497cce071b85efedd`.
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
is built from one `ArticulatedEmbodimentPhysicalState` and an explicit step
correlation. It snapshots owner state into solver-facing input, including:

- body, episode and morphology identity and the source state's causal context;
- root pose, frame names, linear velocity in `m/s` and angular velocity in
  `rad/s`;
- the complete morphology-content digest and generated description;
- articulated joint position/range data keyed by stable `joint_id`;
- contact links, surface material and fixed-base declaration.

The projection is immutable and does not retain mutable morphology mappings.
Current tests cover complete owner-state projection by stable joint identity,
input isolation and rejection of correlation that is not bound to the source
state. The module remains a projection, not a solver, semantic physics
authority or state transition.

### What is deliberately left out

Nothing of the body's physiology is projected. The function's own comment
gives the reason: "the CURRENT model defines no mapping from those values to
solver mass, geometry, force or constraint parameters". A body's energy,
integrity, temperature or fatigue
([somatic state](somatic-state.md)) therefore has no effect on what a solver
is given.

### What the projection does not carry or check

- **World authorization.** The correlation is checked against the source
  state's context, but the projection does not authenticate that World
  authorized the step. A caller-constructible correlation is not proof of
  World authority.
- **Whether a solver's candidate is authoritative.** The projection supplies
  inputs only; Embodiment adoption remains a separate owner validation.
- **Production execution.** Current consumers are World integration fixtures;
  this does not demonstrate a production solver adapter.

Directly constructed solver inputs are validated against finite values and
active morphology constraints. Tests cover those fail-closed checks, including
rejection of stale/wrong morphology correlation. This is structural/domain
validation, not proof of physical calibration.

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
declarations or that any physical simulation is valid". A search at the pinned
revisions found the two tables read by their own test and by nothing else.
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
`environment@0a9f4fbb1922cc6ca9e7b2489cf891606ef9ee41`), where Embodiment
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
a clock and no read of host time (source search at the pinned revision), so
nothing here takes its time from the host. A type
for physical time exists and is distinct from the tick. No value carries
it. The decision leaves open which authority advances each time. This is a
comparison of content, not a ruling on conformance.

## Where it is used

Embodiment's source module defines `project_body_physical_input`, which builds
the projection from one validated owner state and a correlation. World's
reusable physical-step coordinator calls injected projection ports; the
current concrete consumers are World integration fixtures, described in
[the physical causal step](../world/physical-step.md), read at
`world@a8d07fd791da76365aa74080eef1e82b11a599fd`. No production solver
adapter or non-test caller is established by these sources.

In both, a function of the fixture parses the description as XML, takes
from it the masses, the sizes of the boxes and, for the articulated body,
the joint's origin, axis, limits and damping, and writes a model for MuJoCo
by hand. It then places the root from the projection's pose and velocities,
reordering the quaternion to the solver's own order. The description's
moments of inertia, torque limit and velocity limit are not used.

In `test_articulated_mujoco_candidate_is_adopted_and_world_committed`, the
second step starts from a restored state whose hinge is no longer at zero.
The projection carries the restored joint state keyed by `joint_id`; the
fixture maps that projected value into MuJoCo's joint arrays.

`test_procedural_spheres_are_adopted_committed_restored_and_reused` uses a
single-box body and checks, before stepping, that the projection names the
frame of the generated scene.

## Correspondence with the decisions

[ADR-0098](../../technical/adr/ADR-0098-physical-substrate-and-causal-integration.md)
says that "the physical substrate executes numerical coupled resolution over
owner projections". Set beside the code: Embodiment now provides an immutable
projection from one validated owner state. World coordinates the step through
injected ports, but the repository does not yet provide a production solver
adapter. The projection is not a solver, authority or state transition.

[ADR-0073](../../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md),
item 3, says that "Embodiment and Environment provide their projections".
The Embodiment projection function exists; the demonstrated caller is an
integration fixture, not a production runtime adapter.

This is a comparison of content, not a ruling on conformance.

## What supports this description

| Claim | Support |
|---|---|
| Checks of the pose sample; absence of a World identifier | Code and tests in `embodiment:tests/test_body_pose_sample.py`, run at that revision (all pass) |
| Projection from one owner state, stable joint identities, detachment from morphology mappings, correlation binding, and direct-value validation | Code and tests in `embodiment:tests/test_physical_projection.py` at the pinned Embodiment revision |
| Content of the two declarations and that copies are independent | Code and tests in `embodiment:tests/test_physics3d_observation_contract.py`, run at that revision (all pass) |
| What a duration accepts and refuses | Code and tests in `embodiment:tests/test_duration.py`, run at that revision (all pass) |
| Free frame names, revision, kind and value; negative sample time; arithmetic on durations; adopted pose has no time | Code and bounded ad hoc observations; these are not established by the listed tests |
| Joint state and active morphology properties are included in the projection | Code (`BodyPhysicalInput`) and the projection tests at the pinned Embodiment revision |
| The declarations and duration have no production consumers in the pinned source trees; the projection function is source-defined but has no demonstrated non-test caller | Source search across the pinned repositories; tests are excluded from the production-caller claim |
| How World's fixtures consume the projection; Environment's frame vocabulary | Code of the World integration fixtures and `environment:src/environment/static_scene.py` at the pinned revisions; read, not run for this document |
| That a solver works over owner projections; that host time is not causal authority | Accepted decisions ADR-0098, ADR-0073, ADR-0090; statements of intent, not test results |

No run with a real solver and no experiment was examined for this document.

## Open questions

- Which production solver adapter, if any, should consume the engine-neutral
  projection; the current fixtures do not establish a production adapter.
- Which value, owned by whom, records the physical time a step covers.
- Whether the declared frames and units should be enforced by the values
  that are meant to follow them, and how Embodiment's and Environment's
  frame declarations are to be compared.
