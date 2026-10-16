# The articulated body: what it is made of and where its joints are

Reviewed against `embodiment` at commit `8f9576a8cf5bc7213940c593033a1f0f4d0584d4` (main on
2026-10-16); first written against `97cb09a8`. Everything below describes the
later revision. Statements are marked by what supports them: the code, the
tests, or an accepted decision.

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

An `ArticulatedBodySpec` is not itself guaranteed to detach a caller's
`segments` mapping. When the owner creates its active morphology, it snapshots
and freezes the normalized declared payload. That owner-bound payload has a
canonical serialization and SHA-256 identity distinct from the digest of
generated description text.

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

Only part of a specification reaches the URDF description. The full
normalized declared specification is nevertheless covered by its separate
payload hash; the URDF hash identifies the generated description, not all
morphology content.

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

The active morphology records both the specification payload identity and
the generated-description identity. The morphology revision remains a
caller-supplied label; hashing does not allocate or advance it.

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

Adoption is invoked via `ArticulatedEmbodimentPhysicalState.adopt_candidate`
(`embodiment:src/embodiment/physics3d/articulated_state.py:241`), consuming a
`SolverArticulatedCandidate` and a `world_context: WorldPhysicalStepContext`.
Embodiment derives the expected step correlation from `world_context` and requires
`world_context.target_causal_tick == world_context.source_causal_tick + 1`.

The check order is strict:

1. the candidate's joints must be exactly the active morphology's declared joints;
2. the root adopts its candidate against `world_context`, with every check described in
   [the body's physical state](physical-state.md): the correlation, the
   World, tick, body, episode and morphology revision, the frames, and the unit
   quaternion;
3. a new articulated state is built from the adopted root and the candidate's
   joints, where positions outside the limits (`lower_rad`, `upper_rad`) and
   excessive velocities (`max_velocity_rad_per_s`) raise `ValueError`.

Any failure raises and produces nothing. Since every value involved is
immutable, the state adopted from is unchanged whatever happens.

### Full articulated state lineage for body pose

An articulated state can project its root pose for passive observation via
`body_pose_observation_projection()` (`articulated_state.py:214`).
Although `BodyPoseObservationProjection` carries only the root pose sample,
its `source_state_sha256` digest is explicitly computed from the **full articulated
checkpoint bytes** (`self.checkpoint_digest`, line 232), not the embedded root state's
digest (`self.root.checkpoint_digest`). This binds the published pose directly to the
complete physical truth of root, morphology and joint positions.

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

The state encodes itself as canonical JSON under the current checkpoint
schema. The checkpoint carries the owner-bound active morphology/specification
payload, its identity, the nested root checkpoint, joints and explicit units.

The checkpoint carries the active morphology/specification payload and its
identity with the articulated state. Restore validates this state against
the active owner descriptor; it does not silently accept a different
morphology. This owner boundary does not authenticate the descriptor's
external origin.

The canonical outer schema identifier is
`ARTICULATED_PHYSICAL_CHECKPOINT_SCHEMA = "embodiment-articulated-physical-checkpoint-v2"`;
the nested root checkpoint has its own schema. Restore is strict: the set of
top-level fields must be exact, units explicit, the binding must match the
active descriptor field for field, and decoded state must pass construction
rules. `validate_checkpoint` independently checks checkpoint bytes against
the active morphology, schema and SHA-256 reference;
`verify_restoration` checks that restored state corresponds exactly to the
referenced bytes. These checks do not authenticate the external origin of
the descriptor and do not establish durable storage or recovery after
process failure. Tests cover altered bytes, invalid state, wrong owner
identity, and mismatched restored state.

A state encoded and restored equals the original and encodes to the same
bytes (`test_articulated_checkpoint_is_deterministic_and_restores_exact_state`),
and a restored state can adopt the next step
(`test_restored_articulated_state_can_continue_on_the_next_causal_step`).
The repository's migration notes say of that second test that "it is not
evidence of process restart or durable recovery": both steps run in one
process, on values.

Four things follow, read from the code and confirmed by a run:

- **Equal states do not always give equal bytes.** Joint positions are kept
  as given. Two states built with the joint position `1` and `1.0` compare
  equal and encode differently, and so do `0.0` and `-0.0`. A state
  restored from bytes re-encodes to those same bytes.
- **The verification boundary is limited.** Owner validation and restoration
  verification exist in Embodiment, but they verify against a supplied
  independent reference; they do not authenticate who created it or prove
  durable storage/recovery. The World integration fixture still supplies
  the adapter and does not make this a production-integrated checkpoint.

## Bounded static render morphology projection

The repository exposes a bounded, read-only render morphology projection
(`embodiment:src/embodiment/physics3d/spatial_render.py::RenderMorphologyProjection`).
It projects explicitly authored box geometry and revolute joint topology from
the active morphology into detached JSON-compatible data:

- up to 128 links and 128 segments;
- up to 127 revolute joints;
- non-empty, trimmed string identities;
- coordinate system strictly `right_handed_z_up` and length unit `m`;
- maximum descriptor payload of 256 KiB;
- deterministic RFC 8785 canonical JSON bytes with a SHA-256 digest
  (`render_morphology_sha256`).

The module also provides validation of already-computed dynamic link pose
candidates (`validate_dynamic_pose_candidate` and
`validate_dynamic_pose_candidate_binding`). It never calculates kinematics or
proves a World commit: dynamic pose candidates come from a physical step, and
World remains responsible for binding a published sample to a confirmed causal
cut (candidate contract in
`docs/design/spatial-render-projection-contract-candidate-v1.md`).
Supported by unit tests in `embodiment:tests/test_spatial_render.py`.

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

No production source module was identified using these types in the reviewed
repository trees. World contains two integration fixtures that use them, described
in [the physical causal step](../world/physical-step.md). In
`test_articulated_mujoco_candidate_is_adopted_and_world_committed` a body of
two boxes and one hinge is stepped, its state is adopted and stored, the
owners are restored from the committed cut, and a second step is taken. The
fixture calls itself "a workspace-local integration fixture, not a production
solver adapter".

World's integration extra pins `embodiment` at
`badf444f8f62e91d1c5ed4a65f3fe23c6cbda6b8`, earlier than the reviewed
Embodiment revision. That fixture therefore does not exercise the current
owner-validation and restoration-verification methods described above.

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
| Bounded static render morphology projection and dynamic link pose candidate validation | Code in `embodiment:src/embodiment/physics3d/spatial_render.py` and tests in `embodiment:tests/test_spatial_render.py` |
| Rules of construction of the state, adoption by identifier, refusals, stale morphology, checkpoint determinism and strictness, descriptor binding, owner validation and restoration verification | Code and tests in `embodiment:tests/test_articulated_state.py` |
| Carrier links, dropped segments, narrowed limits, precision, malformed text | Code and tests in `embodiment:tests/test_articulated_spec.py` and `embodiment:tests/test_articulated_state.py` |
| Hand-made descriptor accepted; digest blind to six fields; checkpoint restored under a descriptor from a different specification; equal states with different bytes; limits enforced at the specification's values | Code, and the same ad hoc run |
| Inherited limits of adoption (caller-supplied expectation, invented revisions, two candidates for one step) | The same ad hoc run, on the articulated state |
| Fields, names and constants read by no code; no source module uses these types | A search of the source and test trees of the seven repositories at their main branches on 2026-10-09 |
| Use in World's fixture | Code of `world:tests/integration/physical_step/test_first_biopeia_physical_causal_step.py`; fixture composition, not production wiring |
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
