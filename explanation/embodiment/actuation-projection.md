# From a motor command to effector channels

Reviewed against `embodiment` at commit `5a23e1fbeaa31109647aec4d4dc36eddbe0a6321` (main on
2026-10-14); first written against `a5129f0`. Everything below describes the
later revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run, or an accepted decision.

## What it is

The Organism issues a motor command. It addresses actuators by opaque
identifiers and gives each a number. A body, on the other hand, has
effectors: named places where something physical can be commanded, each with
a quantity, a unit and a range. Something has to translate the first into
the second, and in doing so answer three questions that are easy to get
wrong silently:

- which effector does this number go to;
- what does the number mean, in what unit, and is it allowed;
- what happens to an effector the command says nothing about.

The actuation projection
(`embodiment:src/embodiment/physics3d/actuation_projection.py::project_motor_command`)
is that translation. It is a pure function. It holds no state, calls no
solver and changes no body: the module says its result "neither invokes a
solver nor mutates authoritative body state". What comes out is a candidate
input for a physical step.

Its answers are: by identifier, never by position; as declared by the active
morphology, and refused if out of range; and nothing at all.

## What goes in

The function takes five things and the kind of command being projected.

- A **motor command**: its own identifier, the identifiers of the commitment
  and controller it came from, optionally a competence, the fingerprint of
  the actuator surface it was written for, the tick it was issued at, the
  embodiment episode it targets, and its channels, each a pair of actuator
  identifier and value.
- An **actuator binding**, described in the next section.
- The **active morphology**: body, embodiment episode, morphology revision,
  and the effectors with their own declaration of quantity, unit, range,
  neutral value and saturation policy.
- A **body pose** and an **embodiment checkpoint**.

Embodiment does not import the Organism's command type or any morphology
class. The command and the morphology are described structurally: any object
with the named attributes will do. The module gives the reason: "Organism
owns its command types and Embodiment owns the active morphology". The
binding is different: it must be Embodiment's own type, and an object that
merely has the right attributes is refused (ad hoc run).

## The actuator binding

Between the actuators an Organism addresses and the effectors a body has,
something must say which is which. That is the binding
(`embodiment:src/embodiment/physics3d/actuator_binding.py::EmbodimentActuatorBinding`),
and it belongs to Embodiment: the module calls it "Embodiment-owned,
revision-bound".

A binding is made for one exact body, one embodiment episode and one
morphology revision, and records the fingerprint of the actuator surface the
commands will be written for. It holds one entry per actuator: the effector
it drives, the kind of command, the quantity, unit, range and neutral value,
the saturation policy, and whether the actuator is available. Actuator and
effector identifiers are each unique within a binding, and the only
saturation policy accepted is the literal `reject`
(`test_binding_rejects_duplicate_channel_identity_and_invalid_contract`).

It is immutable and has an identity: a SHA-256 over its whole content,
including its own identifier, independent of the order of its entries. The
module is careful about what that identity is not: it "is not a solver or
World authorization token".

It can be saved and restored. The checkpoint is canonical JSON with the
fingerprint inside; restoring accepts exactly that shape, recomputes the
fingerprint, and refuses unknown fields or content that no longer matches it
(`test_binding_checkpoint_restores_identical_identity_and_projection`,
`test_restore_rejects_unknown_fields_or_tampered_content`).

The binding does not provide the two validation methods World asks of an
owner in a causal cut, so it cannot by itself be a participant of one
(inspection of the class).

## How a command is accepted

Everything is checked before anything is produced. Any failure raises and
there is no partial result.

**Provenance.** The command's surface fingerprint must be the one the binding
records. The binding must be for the morphology's body, episode and
revision. The pose and the checkpoint must be for the morphology's body, the
checkpoint for its episode, and the command for that same episode
(`test_rejects_command_binding_or_episode_mismatch`,
`test_rejects_binding_body_episode_or_morphology_mismatch`,
`test_rejects_checkpoint_or_pose_that_does_not_match_active_morphology`).

**The binding against the morphology.** Every binding entry names an effector
of the morphology and repeats its quantity, unit, range, neutral value and
saturation policy exactly, and every effector of the morphology is covered by
the binding (`test_rejects_missing_binding_coverage_and_out_of_range_values`).
Every binding entry must carry the kind of command being projected; a
projection asked for another kind was refused (ad hoc run).

**The command against the binding.** An actuator may appear once. It must
exist in the binding and be available. Its value must be a finite number and
lie within the effector's range
(`test_rejects_unavailable_unknown_or_duplicate_command_channel`,
`test_rejects_missing_binding_coverage_and_out_of_range_values`).

## What comes out

A candidate
(`embodiment:src/embodiment/physics3d/actuation_projection.py::PhysicalActuationCandidate`)
carrying the body, episode, morphology revision, kind of command, the
command's provenance, the identifier and fingerprint of the binding used, and
one channel per commanded effector. Each channel
repeats the body, episode, revision, effector and kind, and carries the
value with its quantity, unit, range and neutral value, taken from the
morphology.

Three properties matter.

**Identity, not order.** A value reaches the effector that the binding
associates with its actuator. Reversing the order of the binding's entries
gives the same result, and the same binding fingerprint
(`test_maps_by_stable_effector_id_and_omission_means_no_command`). The
output channels are sorted by effector identifier, whatever the order of the
command (ad hoc run).

**An omitted channel is absent.** An effector the command does not mention
has no channel in the output. It is not given zero, nor its neutral value. A
command with no channels at all produces a candidate with no channels
(`test_omitted_command_is_not_replaced_by_zero_or_neutral`). The neutral
value travels with each channel that is present as a declaration; the
projection never uses it as a value. An unavailable actuator must still be
declared by the binding, and a command that leaves it out is accepted (ad
hoc run).

**Nothing is clipped.** A value outside the range is refused. The only
saturation policy the code accepts, on either the morphology or the binding,
is the literal `reject`; any other is refused as unsupported (ad hoc run).

## What it does not check

Read from the code and confirmed by running the module again at the revision
reviewed.

- **The pose and checkpoint are identity checks only.** The pose is read for
  its body identifier; the checkpoint for its body and episode identifiers.
  Nothing else in them is consulted. An object that is not a checkpoint but
  has those two attributes was accepted, which is also what the tests pass.
- **The body's condition.** A command for a body whose vital state is dead
  was projected normally. No somatic value reaches this function.
- **When the command was issued.** The tick must be a non-negative integer
  and is copied to the candidate. It is compared with nothing: the function
  is not told the current tick.
- **Which step the candidate is for.** The candidate carries no World
  identifier and no physical-step correlation. Its tie to the step in which
  it is applied is made by the caller. See
  [the physical state](physical-state.md) for the correlation.
- **Whitespace.** Identifiers must be non-empty strings; a command
  identifier consisting of spaces was accepted. The physical state in the
  same package removes surrounding whitespace and refuses what is left
  empty.

## Revision-bound joint torque projection

Beyond the generic effector binding, Embodiment provides an explicit joint-torque
command projection (`embodiment:src/embodiment/physics3d/joint_torque.py`).
`EmbodimentJointTorqueBinding` (schema version 1) associates each actuator identifier
with a stable morphology `joint_id` and unit axis.

A `JointTorqueRequest` is projected via `project_joint_torque_command` (lines 247-280):
- Every channel must declare quantity `"joint_torque"` and unit `"N*m"`.
- Torque values must be finite and within `[-max_motor_torque, +max_motor_torque]`
  of the active morphology joint spec.
- Neutral value is strictly `0.0` N·m; saturation policy is `reject`.
- An omitted joint produces no output channel.

## Composing paired motor activations into joint torque

For organisms with paired antagonistic motor channels (e.g., flexor/extensor pairs),
Embodiment provides `compose_differential_motor_command`
(`embodiment:src/embodiment/physics3d/differential_motor_composition.py:154`).

`EmbodimentDifferentialMotorBinding` (schema version 1) binds pairs of positive and negative
actuators to a morphology joint with a non-negative scale factor:
$$\tau = (a_{\text{positive}} - a_{\text{negative}}) \times \tau_{\text{max}} \times \text{scale}$$

Rules enforced in code:
- Activations must lie in $[0.0, 1.0]$.
- Both channels of a pair must be present, or both omitted. A partial pair raises `ValueError`.
- Equal non-zero activations produce an explicit net torque of `0.0` N·m.
- Omitted pairs produce no torque channel.
- Resulting torque must not exceed $\tau_{\text{max}}$; no clipping occurs.
- The emitted `JointTorqueRequest` is validated against the active `EmbodimentJointTorqueBinding`
  before being returned.

## Correspondence with the decision on commands

[ADR-0073](../../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md)
governs this, in its items 1 and 2. Decision and code are set side by side;
this is not a ruling on conformance.

| The decision says | The code does |
|---|---|
| "Array/list position is never authoritative." | Association is by actuator and effector identifier; covered by a test under permutation |
| A command is bound to `body_id`, `embodiment_episode_id`, `morphology_revision`, `effector_id` and `command_kind` | Each output channel carries those five |
| "Public APIs have no implicit units." | Quantity and unit are required non-empty strings on every effector and copied to every channel. They are opaque text: nothing interprets or converts them |
| The descriptor defines an "optional neutral value" | A numeric neutral value is required, between minimum and maximum |
| "Out-of-range values are rejected unless the descriptor explicitly declares saturation." | Out-of-range values are rejected. A descriptor cannot declare saturation: only `reject` is accepted |
| "It does not imply zero or neutral." | An omitted channel produces no output channel; covered by a test |

## Where it is used

In World's integration fixture one command for one of two actuators becomes
one force channel, which the fixture applies to a solver; see
[the physical causal step](../world/physical-step.md). No module in the
`embodiment` repository calls this function, and a search of the main
branches of the seven domain repositories on 2026-10-09 found no other
caller than that fixture.

## What supports this description

| Claim | Support |
|---|---|
| Provenance checks, binding and morphology agreement, coverage, uniqueness, availability, range, mapping by identifier, omission, binding checkpoint | Code and tests in `embodiment:tests/test_actuation_projection.py`, run at that revision (all pass) |
| Output sorted by effector; bounds inclusive; only `reject` accepted; numeric neutral required; unavailable actuator may be left uncommanded | Code, and one ad hoc run of the module at that revision |
| Dead body projected; issue tick unchecked; a stand-in object accepted as checkpoint; whitespace-only identifier accepted | Code, and the same ad hoc run; no test is kept for these |
| What a command must be bound to and what omission means | Accepted decision ADR-0073; a statement of intent |

Nothing here is evidence about motor control. The tests exercise the
function with hand-written values; no command produced by a running
Organism was examined.

## Open questions

- Whether a body's viability, or the age of a command, should gate
  projection, and if so in which domain.
- Whether the neutral value is meant to be optional, as the decision words
  it, and what a descriptor that allows saturation would look like.
- What the pose and checkpoint arguments are for beyond identity.
