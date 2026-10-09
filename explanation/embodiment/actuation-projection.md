# From a motor command to effector channels

Reviewed against `embodiment` at commit `a5129f03aa4b024e33d332f917b9235afe97959c`.
Everything below describes that revision. Statements are marked by what
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
- An **actuator surface**: a fingerprint, the morphology revision it was
  built for, and one entry per actuator saying which effector it drives,
  with what kind of command, quantity, unit, range, neutral value and
  saturation policy, and whether it is available.
- The **active morphology**: body, embodiment episode, morphology revision,
  and the effectors with their own declaration of quantity, unit, range,
  neutral value and saturation policy.
- A **body pose** and an **embodiment checkpoint**.

Embodiment does not import the Organism's command type or any morphology
class. The first three inputs are described structurally: any object with
the named attributes will do. The module gives the reason: "Organism owns
its command types
and Embodiment owns the active morphology".

## How a command is accepted

Everything is checked before anything is produced. Any failure raises and
there is no partial result.

**Provenance.** The command's surface fingerprint must be the surface's. The
pose and the checkpoint must be for the morphology's body, the checkpoint
for its episode, the command for that same episode, and the surface for the
morphology's revision
(`test_rejects_provenance_revision_or_unknown_channel`,
`test_rejects_checkpoint_or_pose_that_does_not_match_active_morphology`,
`test_rejects_checkpoint_episode_mismatch`).

**The surface against the morphology.** Effector identifiers are unique in
the morphology; actuator and effector identifiers are unique in the surface.
Every surface entry names an effector of the morphology and repeats its
quantity, unit, range, neutral value and saturation policy exactly, and
every effector of the morphology is covered by the surface. A surface for an
older revision, one that disagrees on a range, one that maps two actuators
to one effector, or one that leaves an effector out is refused
(`test_rejects_surface_revision_or_effector_contract_mismatch`,
`test_rejects_duplicate_surface_effector_and_missing_surface_coverage`).
Every surface entry must carry the kind of command being projected
(`test_rejects_wrong_command_kind_and_non_finite_values`).

**The command against the surface.** An actuator may appear once
(`test_rejects_duplicate_command_channels`). It must exist in the surface
and be available. Its value must be a finite number, not a boolean, and lie
within the effector's range, bounds included
(`test_rejects_unavailable_channel_command_and_out_of_range_value_without_saturation`).

## What comes out

A candidate
(`embodiment:src/embodiment/physics3d/actuation_projection.py::PhysicalActuationCandidate`)
carrying the body, episode, morphology revision, kind of command, the
command's provenance, and one channel per commanded effector. Each channel
repeats the body, episode, revision, effector and kind, and carries the
value with its quantity, unit, range and neutral value, taken from the
morphology.

Three properties matter.

**Identity, not order.** A value reaches the effector that the surface
associates with its actuator. Reversing the order of the surface entries
gives the same result
(`test_maps_by_stable_effector_id_and_omission_means_no_command`). The
output channels are sorted by effector identifier, whatever the order of the
command (ad hoc run).

**An omitted channel is absent.** An effector the command does not mention
has no channel in the output. It is not given zero, nor its neutral value. A
command with no channels at all produces a candidate with no channels
(`test_omitted_command_is_not_replaced_by_zero_or_neutral`). The neutral
value travels with each channel that is present as a declaration; the
projection never uses it as a value. An unavailable actuator must still be
declared by the surface, and a command that leaves it out is accepted (ad
hoc run).

**Nothing is clipped.** A value outside the range is refused. The only
saturation policy the code accepts, on either the morphology or the surface,
is the literal `reject`; any other is refused as unsupported (ad hoc run).

## What it does not check

Read from the code and confirmed by running the module at that revision.

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
| Provenance checks, surface and morphology agreement, coverage, uniqueness, availability, range, mapping by identifier, omission | Code and tests in `embodiment:tests/test_actuation_projection.py`, run at that revision (all pass) |
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
