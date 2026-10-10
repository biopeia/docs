# The articulated body: what it is made of and where its joints are

Reviewed against `embodiment` at commit `a5129f03aa4b024e33d332f917b9235afe97959c`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run, or an accepted decision.

## What it is

A body with joints needs two kinds of statement. One says what the body is
made of: which rigid pieces, how heavy, joined where, turning about which
axis and how far. The other says where the body is now: the angle and
angular speed of every joint at one moment. The first changes only when the
body's shape changes. The second changes at every physical step.

Embodiment keeps the two apart, and puts a third value between them:

- a **specification** of the body, which is engine-neutral and from which a
  textual description is generated;
- an **active morphology descriptor**, a small value that binds one
  specification to one body, one embodiment episode and one morphology
  revision;
- the **articulated state**, which holds the joints' angles and speeds
  together with the body's free-root state, and can change only by adopting
  a solver's result.

The free-root state, the correlation of a physical step and the rules of
adoption for the root are described in
[the body's physical state](physical-state.md) and are not repeated here.
This document covers what an articulated body adds to them.

None of these three runs a solver. The specification module says of itself
that it "does not instantiate a solver, advance causal time, or own runtime
body state", and the state module that it "does not execute a solver or
coordinate a World causal commit".

## What a body is made of

A specification
(`embodiment:src/embodiment/physics3d/articulated_spec.py::ArticulatedBodySpec`)
is an immutable record built from the value types of
`embodiment:src/embodiment/physics3d/mechanics.py`:

- **segments**, by link name: a mass, the three sizes of a box, the offset of
  the box from the link's origin, and a colour;
- **joints**: a name, an axis, a lower and an upper limit, a maximum motor
  torque, a passive damping and a maximum velocity. Every joint is a hinge;
  the description generated from a specification contains no other kind;
- a **joint topology**: for each joint, the parent link, the child link and
  the origin of the joint in the parent;
- optional **fixed links**, rigidly attached to a parent;
- the name of the **base link**, a list of **contact link names**, pairs of
  **structural neighbours**, a **surface material** (friction, restitution
  and damping values), a flag for a **fixed base**, a **spawn height**, a
  body kind and a state schema version.

The record is immutable, but its segments are held in an ordinary mapping
that can still be changed in place; a specification cannot be hashed for
that reason (ad hoc run). Immutability of the joint and segment values is
covered by `test_physical_specifications_are_immutable_value_objects`.

### The description

One function turns a specification into text: a URDF document, the XML
format several physics engines read. It emits one link for the base, one for
the child of every joint and one for every fixed link, in that order; then
one hinge per joint and one fixed joint per fixed link. The same
specification always gives the same text
(`test_urdf_generation_is_deterministic_and_contains_morphology`).

Read from the code and confirmed by running the module at that revision:

- A link that has a segment is a box. Its moments of inertia are those of a
  uniform box of that mass and size, and the same box is its visible shape
  and its collision shape.
- A link named by the topology that has **no** segment is emitted as a
  massive point of 0.05, with no shape. Nothing reports the substitution.
- A segment that no joint or fixed link names is left out of the
  description, also without report.
- The limits written for a joint are **narrower** than the limits of the
  specification. Each end is moved inward by two degrees, or by a tenth of
  the joint's span if that is smaller. A joint specified from −0.8 to 0.8
  radians is described as ±0.765.
- Numbers are written with ten significant digits (twelve for joint limits,
  torque, velocity and damping). Two specifications whose masses differ in
  the thirteenth digit give the same text.

Only part of a specification reaches the description. The contact link
names, the structural neighbours, the surface material, the fixed-base flag,
the spawn height and the state schema version are not written into it.
A search of the source and test trees of all seven repositories at their
main branches on 2026-10-09 found that the contact link names are copied
into [the physical projection](physical-projection.md) and that the other
five are read by no code at all.

### What a specification does not check

Building a specification checks nothing, and neither do the joint and
segment values. The function that generates the description checks two
things: that there are as many topology entries as joints, and that they
come in the same order
(`test_urdf_rejects_mismatched_joint_spec_and_topology`).

Everything else is accepted (ad hoc run): a negative or non-numeric mass,
a joint whose lower limit is above its upper limit, a parent link that does
not exist, and a body kind containing characters that make the generated
text malformed XML. Inverted limits are refused one stage later, when a
descriptor is derived from the specification.

The names of the fields carry no units: `lower`, `upper`, `mass`, `size`,
`max_motor_torque`. That limits are radians and velocities radians per
second is stated only where the descriptor copies them into fields named
`lower_rad`, `upper_rad` and `max_velocity_rad_per_s`. The units of mass,
size, torque and damping are stated nowhere in these two modules.

### Counts and channel names

A specification also answers how many sensory and motor channels a body of
this shape would have. It gives two effector names per joint, `eff.0`,
`eff.1` and so on, and a number of receptor names, `rec.0` onward, computed
from the number of joints and of contact links, of which the last four are
called interoceptive (`test_spec_exposes_opaque_ordinal_channels`).

The comment at the head of the mechanics module reads: "Human-readable
anatomy exists only inside the apparatus." and says that the organism sees
only those opaque channel names. That is a statement of the code's author
about a design, not something this repository shows. The same search found
no code that reads these names or counts. Embodiment's
[actuation projection](actuation-projection.md) addresses effectors by
identifiers declared in its own descriptors, not by these ordinal names,
and nothing relates the two. Lab's
[interoception transducer](../lab/body-interoception-transducer.md) is not
given them either.

The mechanics module also defines three value types (a binding of a joint
to a pair of motor ports, a record of actuator work, a joint limit), a
ground material and four constants for the behaviour of a joint near the
end of its range and for a solver's tolerance at a limit. The same search
found them used by nothing except, for two of them, their own unit test
(`test_material_and_carrier_constants_are_physical_parameters`).

## The active morphology descriptor

A specification has no identity. It does not say whose body it is or which
revision of the shape it is. The descriptor
(`embodiment:src/embodiment/physics3d/articulated_state.py::ActiveArticulatedMorphology`)
adds that: a body identifier, an embodiment episode identifier, a morphology
revision, the SHA-256 of the generated description, and for each joint its
identifier, its limits and its maximum velocity.

It is normally derived from a specification, which generates the description
and hashes it. The joint ranges are stored sorted by joint identifier, so the
order in which a specification lists its joints does not matter afterwards.

Two limits of the descriptor are read from the code and confirmed by a run.

**It can be made by hand.** The class says so itself: "This value does not
authenticate its own origin: callers must not accept an arbitrary
caller-supplied descriptor as authority." A descriptor built directly, with
a digest of sixty-four zeros and invented joint ranges, is accepted, and so
is one with no joints.

**The digest covers the description, not the specification.** Because six
fields never reach the description, two specifications that differ in their
contact links, fixed-base flag or surface material give descriptors that
compare equal. The morphology revision is a label supplied by the caller;
nothing derives it from the specification, and the same label with a
different description gives a different, equally valid descriptor.

## The joint state

The articulated state
(`ArticulatedEmbodimentPhysicalState`) holds three things: the free-root
state, the descriptor, and one value per joint giving its identifier, its
position in radians and its velocity in radians per second. Like the root
state it carries a marker whose only permitted value is `EMBODIMENT_OWNED`,
and it is immutable.

It cannot be built unless (code; the first rule is covered by
`test_state_and_checkpoint_must_match_active_morphology_descriptor`):

- the root state names the body, the episode and the morphology revision of
  the descriptor;
- the joints are exactly the descriptor's joints, each once;
- every position lies within the descriptor's limits, ends included;
- no velocity exceeds the descriptor's maximum in either direction.

The limits enforced here are the specification's own, not the narrower ones
written into the description. A joint at 0.79 radians, beyond the 0.765
given to a solver for the joint above, is a valid state; 0.8 is valid and a
billionth beyond it is refused (ad hoc run). The module's constant for a
solver's tolerance at a joint limit plays no part.

Joints are stored sorted by identifier. The module states the principle:
"Joint names are stable identities within an explicit active morphology
binding, never positional authority."

## Adoption

A solver's proposal for an articulated body is a root candidate plus one
value per joint, which the code calls "Untrusted root and joint values
returned for one authorized step." Building one checks only that no joint
appears twice; a candidate with a joint far outside its range can be built
and is refused later.

Adoption takes that candidate and the correlation to expect, and proceeds
in this order:

1. the candidate's joints must be exactly the descriptor's joints;
2. the root adopts its candidate, with every check described in
   [the body's physical state](physical-state.md): the correlation, the
   World, tick, body, episode and morphology revision, the frames, the unit
   quaternion;
3. a new articulated state is built from the adopted root and the candidate's
   joints, which is where positions outside the limits and excessive
   velocities are refused.

Any failure raises and produces nothing. Since every value involved is
immutable, the state adopted from is unchanged whatever happens.

What the tests cover:

- A candidate listing the joints in the opposite order gives the same
  adopted state: joints are matched by identifier, and the tick advances by
  one (`test_adopts_joint_values_by_stable_identity_not_collection_position`).
- A missing joint, a duplicated one, an unknown one, a position out of
  range and a velocity over the maximum are each refused
  (`test_rejects_incomplete_duplicate_unknown_or_out_of_range_joint_results`).
- A candidate correlated with an older morphology revision is refused even
  though its joint names are the right ones
  (`test_rejects_stale_morphology_even_when_joint_names_match`).

A refused joint value is refused outright; nothing clamps it to the limit.

Everything the root's adoption does not check holds here as well, and was
confirmed for the articulated state by a run: the expected correlation is
supplied by the caller, invented environment and solver revisions are
adopted when candidate and expectation agree, and one state adopted two
different candidates for the same step. Those are recorded against the root
state and are not repeated as findings here.

One difference from the root is worth noticing. The root accepts any finite
velocity, however implausible. Joints are bounded: by position and by speed.

## Checkpoint

The state encodes itself as canonical JSON under schema version 1. The
bytes hold the root's own checkpoint, nested whole under its schema
version 2; the four fields that bind the descriptor (body, episode,
morphology revision, digest of the description); the joints; and the two
units, `rad` and `rad/s`, by name.

The bytes do **not** hold the joint limits, the description or the
specification. Restoring therefore needs something the checkpoint does not
contain: the caller must supply the active descriptor, and the state is
checked against it. The class explains the choice: state construction and
recovery "verify against this owner-supplied descriptor rather than
trusting checkpoint ranges."

Restoring is strict (`test_articulated_checkpoint_rejects_unknown_schema_and_implicit_units`,
`test_state_and_checkpoint_must_match_active_morphology_descriptor`, and an
ad hoc run for the rest): the set of top-level fields must be exactly the
expected one, the schema version must be the integer 1, the units must be
the two named, the binding must equal the supplied descriptor's field for
field, and the decoded state must pass every rule of construction. Altered
bytes with a joint out of range, a joint missing, an extra field in a joint,
another owner marker or another body in the root were all refused.

A state encoded and restored equals the original and encodes to the same
bytes (`test_articulated_checkpoint_is_deterministic_and_restores_exact_state`),
and a restored state can adopt the next step
(`test_restored_articulated_state_can_continue_on_the_next_causal_step`).
The repository's migration notes say of that second test that "it is not
evidence of process restart or durable recovery": both steps run in one
process, on values.

Four things follow, read from the code and confirmed by a run:

- **The binding is as wide as the digest.** A checkpoint was restored under
  a descriptor derived from a specification with different contact links
  and a fixed base, because that descriptor is equal to the original.
- **The body's shape has no checkpoint.** Nothing in Embodiment encodes a
  specification or a descriptor. After a restart the specification has to
  come from wherever the caller keeps it.
- **Equal states do not always give equal bytes.** Joint positions are kept
  as given. Two states built with the joint position `1` and `1.0` compare
  equal and encode differently, and so do `0.0` and `-0.0`. A state
  restored from bytes re-encodes to those same bytes.
- **Less is offered than by the root.** The root state has a digest of its
  checkpoint and an explicit statement that it has no durable reference.
  The articulated state has neither. Like the root, it does not answer the
  two validation questions of World's durable runtime, and the schema name
  under which World's fixture stores it,
  `embodiment-articulated-physical-state-v1`, appears only in that fixture
  (read at `world@c162b67e698de9b47450264402677b0165e6e20e`).

## Time

The only clock is the World causal tick held by the root, which adoption
advances by one. The specification and the descriptor carry no time. A
morphology revision is a label, not a counter; nothing in these modules
advances it.

## Lifecycle

What the code shows. A state is created by its caller from a root state, a
descriptor and initial joint values. It survives a restart only if its
bytes were stored elsewhere and the same descriptor is supplied again. It is
bound to one body, one episode and one morphology revision: a checkpoint is
refused under a descriptor that differs in any of them or in the digest.

What the code does not contain: any path that replaces a body, changes a
morphology revision, or creates the state of a successor or an offspring.
The refusal above is the only behaviour at that boundary. That a body's
physical truth belongs to Embodiment and ends with the body is the intent of
[ADR-0104](../../technical/adr/ADR-0104-body-schema-and-competence.md),
[ADR-0094](../../technical/adr/ADR-0094-somatic-state-ownership-body-holds-organism-regulates-and-feels.md)
and
[ADR-0095](../../technical/adr/ADR-0095-surviving-semantic-authorities.md),
not behaviour observed here.

## Where it is used

No source module of any repository uses these types (search of 2026-10-09
named above). They are used by two integration fixtures of World, described
in [the physical causal step](../world/physical-step.md). In
`test_articulated_mujoco_candidate_is_adopted_and_world_committed` a body of
two boxes and one hinge is stepped, its state is adopted and stored, the
owners are restored from the committed cut, and a second step is taken. The
fixture calls itself "a workspace-local integration fixture, not a production
solver adapter".

World's integration extra pins `embodiment` at an earlier commit,
`3fe3cda64516dd5a8148ec49b826c025925396c0`. The six modules described in
this document and in [the physical projection](physical-projection.md) are
identical at the two commits.

## Correspondence with the decisions

[ADR-0073](../../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md),
item 1, is about commands, and says: "Array/list position is never
authoritative" and "Public APIs have no implicit units". Set beside the
code: joint state and joint candidates are matched by identifier, and the
state and its checkpoint name radians and radians per second. The
specification and the mechanics values do not name their units, and the
specification's channel names are ordinals.

Item 3 lists what a correlation includes, among them "morphology revision".
The state refuses a candidate correlated with another revision. The revision
is a label the caller chooses, bound to the shape through a digest that does
not cover the whole specification.

[ADR-0104](../../technical/adr/ADR-0104-body-schema-and-competence.md)
distinguishes "actual physical body truth (Embodiment)" from what an
Organism has learned about bodies. These modules hold only the first; no
learned quantity appears in them.

This is a comparison of content, not a ruling on conformance.

## What supports this description

| Claim | Support |
|---|---|
| Determinism of the description, the two topology checks, channel names, immutability of the value types | Code and tests in `embodiment:tests/test_articulated_spec.py` and `embodiment:tests/test_physics3d_mechanics.py`, run at that revision (all pass) |
| Rules of construction of the state, adoption by identifier, refusals, stale morphology, checkpoint determinism and strictness, descriptor binding, continuation after restore | Code and tests in `embodiment:tests/test_articulated_state.py`, run at that revision (all pass) |
| Carrier links, dropped segments, narrowed limits, precision, absence of validation, malformed text | Code, and one ad hoc run of the modules at that revision; no test is kept for these |
| Hand-made descriptor accepted; digest blind to six fields; checkpoint restored under a descriptor from a different specification; equal states with different bytes; limits enforced at the specification's values | Code, and the same ad hoc run |
| Inherited limits of adoption (caller-supplied expectation, invented revisions, two candidates for one step) | The same ad hoc run, on the articulated state |
| Fields, names and constants read by no code; no source module uses these types | A search of the source and test trees of the seven repositories at their main branches on 2026-10-09 |
| Use in World's fixture; the schema name | Code of `world:tests/integration/physical_step/test_first_biopeia_physical_causal_step.py`, read; run by World's integration job at pinned revisions, not run for this document |
| Who owns body truth; what ends with a body | Accepted decisions ADR-0073, ADR-0098, ADR-0104, ADR-0094, ADR-0095; statements of intent, not test results |

No run with a real solver, no stored checkpoint and no experiment was
examined for this document.

## Open questions

- What makes a descriptor the active one, and who is entitled to build it.
- Whether everything that distinguishes two bodies should be covered by the
  digest, and how a morphology revision is tied to a specification.
- Where a body's shape is kept across a restart.
- Why the description's joint limits are narrower than the state's, and
  whether a solver result between the two is expected.
