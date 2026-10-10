# The physical causal step, as it exists today

Reviewed against `world@95f5064c6b06bd66bb58a72110b066afe4ca70b0`. The
fixtures described here import the other repositories at the revisions pinned
in `world:pyproject.toml`, and that is where World's integration job runs
them: `organism@8bf1eafeb2c05459e4cbaae3a377d2f1c35504c6`,
`embodiment@badf444f8f62e91d1c5ed4a65f3fe23c6cbda6b8`,
`environment@7166f57c4879424d269337deda52f9f9c403dbba`,
`modality@cc74103099f63353e94e1bcdaeeada35a0b571fd` and
`observation@be82907d1d677b2362e369d15eb1e8e964d893aa`.

The heads of those repositories on 2026-10-11 are later:
`organism@ba0011797a6a3b4d48c7731651e50560c4043f18`,
`embodiment@597cc4a09f4a5c94095b17ad0f2ba510df6d02c3`,
`environment@e91bb67f81f3bc15715489cf1262328934454f1b`,
`modality@79b779152d4bff2ab4191dc6601c8f1640e4cae3` and
`observation@6aac3c76684834722440f53c9d8604ac4c16b138`. The searches below
were made at those heads, and the fixtures were run against them once, ad
hoc; the result is in its own section. Statements are marked by what supports
them: the code, a named test, that ad hoc run, or an accepted decision.

## What this is about

The approved design
[Biopeia Physical-Step and Causal-Commit Integration v1](../../technical/design/runtime/biopeia-physical-step-integration-v1.md)
describes how one physical step should cross the authorities: World
authorises it, Embodiment and Environment project their state, a solver
computes a candidate, each owner validates and adopts its own part, and World
commits the cut.

This document describes where that sequence exists in code today.
A protocol coordinator exists in World (`world:src/world/physical_step.py::run_physical_step`),
which issues explicit source and target causal ticks in a `PhysicalStepContext`
inside a durable World transition, sequences owner projections, numerical solving,
owner adoption, and checkpoint reference returns, and propagates failures to latch
recovery. The coordinator takes its six operations as ports supplied by the
caller. **In every place where it is called outside its unit tests, those
ports are functions written inside an integration test fixture.**

World's source now also holds an optional function that runs one MuJoCo step,
described in [the MuJoCo step executor](mujoco-step-executor.md). None of the
fixtures below calls it, and it is not shaped as a solver port of the
coordinator; that document says why.

The end-to-end integration sequence below is exercised through that coordinator
in `world:tests/integration/physical_step/test_first_biopeia_physical_causal_step.py`,
which says of itself that it is "not a scientific validation or a
production solver adapter". A second fixture,
`world:tests/integration/physical_step/test_procedural_sphere_world_step.py`,
carries out a shorter version of it over a generated scene, and a third,
`world:tests/integration/sensing/test_environment_to_organism_scalar_field.py`,
carries a sensed value the other way, from Environment to Organism. Each is
described in its own section below.

What is real production code are the coordinator and the pieces it calls:
`run_physical_step`, the [durable World runtime](durable-runtime.md), and
functions and types of Organism, Embodiment, Environment, Modality and
Observation.

## The sequence the fixture carries out

Before the tick, the fixture builds a World from a genesis specification with
three registered owners (one organism, one body, one environment) and one
presence linked to the organism. The environment owner is registered under an
owner identifier of its own, distinct from the identifier of the environment
it holds. Also before the tick, the fixture takes Organism's action path as
far as a commitment: an affordance is admitted, an intent is activated and a
proposal is arbitrated into a commitment.

Then one tick, through the coordinator. Everything from step 2 to step 9
happens inside the callback through which World asks the owners to save their
state, that is, after World has durably opened the transition and before it
commits.

1. **World opens the transition.** The manifest is preparing.
2. **World issues the context of the step.** The coordinator builds one
   `PhysicalStepContext` naming the World, the tick of the state the step
   starts from, the tick it would commit, the step, the body, the embodiment
   episode, the morphology revision, the environment revision and the solver
   configuration revision. Every port receives it.
3. **Embodiment projects the body** for the solver from its physical state
   and its active morphology, under a correlation the fixture copies from the
   context.
4. **Organism produces a command.** A controller issues a motor command for
   the commitment, for one actuator, and the command is delivered through the
   actuator surface. The second actuator is given no command.
5. **Embodiment projects the command** onto effectors by stable identity,
   giving one force channel.
6. **A MuJoCo step runs**, in a function of the fixture. The function reads
   the body description Embodiment projected, refuses anything but the one
   box it supports, writes a solver model by hand from it and from the
   Environment's static scene, applies the channel as a force and advances
   one step.
7. **Embodiment adopts the result.** The solver's output is wrapped as a
   candidate carrying a correlation. The body's physical state is handed the
   candidate and World's context, derives the correlation it expects from
   that context itself, and accepts the candidate only if the two are equal
   and name its own World, tick, body, episode and morphology revision.
8. **Environment validates and adopts** its side, a static scene, against an
   expected correlation that the fixture builds from the context before the
   solver runs. The owner is bound to one World and refuses a correlation
   naming another.
9. **The owners' checkpoints are written** and their references returned.
10. **World verifies and commits**, as described in
    [the durable runtime document](durable-runtime.md).
11. **Observation claims are built** for World, body and environment, only
    after the manifest is committed.

Steps 7 and 8 differ in where the expected correlation comes from. In
Embodiment the derivation is source code
(`embodiment:src/embodiment/physics3d/physical_transition.py::EmbodimentPhysicalState.adopt_candidate`):
it reads the context by attribute names through a protocol declared in
Embodiment, which does not import World. Its own documentation says that
"structural typing does not authenticate fabricated context values". In
Environment the expected correlation is still built by the caller, here the
fixture.

## What the tests establish

Run by World's integration job in CI at the pinned revisions.

- **Determinism across fresh runs, and under permutation.** Three runs give
  identical results and identical observations: two with the actuator
  surface in one order and one with it reversed
  (`test_first_biopeia_end_to_end_physical_causal_step_is_deterministic`).
  The effector reached is the same in all three, so identity, not position,
  selects it.
- **An omitted channel is no command.** Exactly one command channel exists
  and the omitted actuator appears in none (same test).
- **The Environment's gravity reached the solver.** The body moved along the
  commanded axis and fell (same test).
- **A stale morphology cannot commit.** A candidate carrying a previous
  morphology revision is refused by Embodiment against World's context, the
  body's state is unchanged, and the World is left requiring recovery at tick
  zero with tick one pending
  (`test_stale_morphology_candidate_cannot_publish_the_next_world_cut`).
- **An environment candidate naming another World cannot commit.**
  Environment refuses it, no checkpoint is written, no observation is built,
  and the World is left requiring recovery at tick zero with tick one pending
  (`test_wrong_world_environment_candidate_cannot_publish_the_next_world_cut`).
- **An articulated body can be stepped, restored and stepped again**
  (`test_articulated_mujoco_candidate_is_adopted_and_world_committed`). The
  projection carries the joint's position and velocity, and the fixture sets
  the solver's joint from the projection. The restore goes through the
  durable World runtime in the same process.

One more test, `test_fixture_owner_codecs_bind_checkpoint_identity_and_schema`,
checks the checkpoint contract class that the fixture itself defines. It says
nothing about any owner's code.

## The second fixture: a generated scene

`test_procedural_sphere_world_step.py` exercises the same owner adoption and
World commit without an organism, and now through the same coordinator. It
generates a scene with
[procedural genesis](../environment/procedural-genesis.md), places its
spheres in the solver, lets a body fall and touch them, has Embodiment and
Environment adopt, commits, restores both owners from the committed cut, and
takes one further step
(`test_procedural_spheres_are_adopted_committed_restored_and_reused`).

What it adds to the first fixture:

- **Generated geometry reaches the solver and changes the result.** The body
  touches a generated sphere, and the same step computed with and without the
  spheres gives a different outcome.
- **The generated scene survives the cut.** The Environment checkpoint named
  by the committed manifest restores the same scene with the same genesis
  provenance.
- **A step can follow a restore.**
- **Two runs give the same committed owners and the same claims**
  (`test_identical_runs_have_equal_adopted_cut_and_passive_semantic_claims`).
  The comparison leaves out the journal's prefix digest, which differs
  between runs because it now covers the paths of the owners' checkpoint
  files; see [the durable runtime document](durable-runtime.md).

It has its own function that runs the solver. It involves no Organism code
and no command. It describes itself as "a contract integration test, not
evidence of ecological quality, calibration, physical material properties,
or production crash durability".

## The third fixture: a sensed value

`test_environment_to_organism_scalar_field.py` uses the coordinator for the
inward direction. There is no MuJoCo in it. In one step:

1. Embodiment projects the point of a receptor on the body, given World's
   context.
2. Environment samples a scalar field at that point, under a correlation the
   fixture copies from the context.
3. Modality passes the sampled number through a declared identity mapping
   that accepts a finite value between 0 and 1 and returns it unchanged.
4. Organism's cognitive transition is advanced from that number, delivered as
   an opaque signal on one channel, and returns a candidate state and a
   frame in which one input node carries the value.
5. A stand-in for the solver returns the body where it was. Embodiment adopts
   it, the fixture checks the identity of the Environment sample, checkpoints
   are written and World commits.

Covered by
`test_environment_scalar_field_reaches_organism_as_opaque_signal_and_commits`;
a receptor carrying a stale morphology revision is refused before anything
is sampled, and the World is left requiring recovery
(`test_stale_receptor_morphology_is_rejected_without_next_committed_cut`).

What it does not do matters as much. The Organism checkpoint committed at
the new tick is the bytes of the cognitive state from before the step: the
candidate state computed in step 4 is not adopted. The fixture says so: "this
fixture does not claim that candidate was adopted into the committed Organism
continuation". Its owner contract accepts any non-empty bytes. It calls
itself "a narrow target contract, not scientific learning or a production
sensor/solver adapter".

## What they do not establish

Stated by the fixtures or evident from them:

- **Nothing in source wires a step together.** World provides the
  coordinator, Embodiment derives its expected correlation from World's
  context, and World's source holds an optional MuJoCo executor. The six
  ports handed to the coordinator, in all three fixtures, are functions of
  the fixtures. No source module of any repository calls `run_physical_step`.
- **The solver calls that take part in a step belong to the fixtures.** Each
  of the two MuJoCo fixtures has its own function that builds a model and
  advances the simulation; the articulated test does it inline. The executor
  in `world:src/world/adapters/mujoco.py` is called only by its own tests.
- **No fixture joins sensing to acting.** The first fixture takes a command
  from fixed values to a physical result and imports nothing of Organism's
  cognition or of Modality. The third takes a sampled value to a candidate
  cognitive state and imports nothing of Organism's actuation, and no solver.
  No test or source module runs sense, cognition, command and physics in one
  step.
- **The organism's state is a stand-in.** In the two MuJoCo fixtures the
  organism owner's checkpoint is a small JSON object under a schema named for
  the fixture, not an Organism checkpoint. The action path uses real Organism
  types fed with fixed values; the fixture comments that this is not a claim
  of autonomous cognition or learning.
- **The body's physiology is created inside the step**, with fixed values,
  rather than restored from the body's checkpointed state.
- **The scene is static.** Environment adopts an unchanged scene, written by
  hand in one fixture and generated in the other; nothing in the environment
  evolves. A separate integration test,
  `world:tests/integration/test_environment_dynamic_adoption_restore.py`,
  moves one Environment object by a fixed amount per tick, commits, restores
  and continues; it uses no solver and not the coordinator, and builds its
  context by hand.
- **Modality takes no part in the outward path.** The first fixture notes
  that its current contract is sensory transduction only. Its part in the
  third fixture is the identity mapping described above.
- **Durability and replay.** Local checkpoint writes "do not test power-loss
  durability", and continuation after restart "is not compared with
  uninterrupted replay".
- **Physical calibration.** Nothing here is a claim about physical accuracy.

## At the heads of the other repositories

The pinned revisions are behind the heads named at the top: Organism by 23
commits, Embodiment by 4, Environment by 3, Modality by 1, Observation by 2.
The integration job says nothing about the heads.

In an ad hoc run on 2026-10-11, the whole of `world:tests/integration` was
run with World and the five other repositories at their heads, MuJoCo 3.14.0
and Python 3.12. Of 31 test cases, 25 passed and 6 failed. The six are all
the tests of `test_procedural_sphere_world_step.py`, and all fail the same
way while building the scene: Environment's procedural genesis configuration
now requires a sliding friction coefficient that the fixture does not supply.
The requirement was added after the pinned Environment revision. The five
tests of the first fixture, the two of the third, and the tests of the
MuJoCo executor passed.

So the second fixture describes Environment as pinned, not as it is at its
head. This is recorded as a finding and nothing here was changed to make it
pass.

## What supports this description

| Claim | Support |
|---|---|
| The sequence and coordinator integration | Code of `world:src/world/physical_step.py` and the three fixtures, read in full at the World revision named at the top |
| Determinism, permutation, omitted channel, gravity, stale morphology, wrong World, articulated restore, the generated scene's effect, persistence and reuse, and the sensed value | The tests named, run by World's integration job in CI at the pinned revisions |
| Coordinator protocol invariants and solver failure propagation | Unit tests in `world:tests/unit/test_physical_step.py` |
| Embodiment derives its expected correlation from World's context | Code of `embodiment:src/embodiment/physics3d/physical_transition.py` at the pinned revision and at the head |
| Where a MuJoCo simulation is advanced, and who calls the coordinator | A search of the source and test trees of all seven repositories at the heads named at the top, on 2026-10-11. The call that advances a MuJoCo simulation appears in `world:src/world/adapters/mujoco.py` and in the two MuJoCo fixtures (once in a helper of each, and twice inline in the articulated test), and nowhere else. `execute_mujoco_step` is called only in `world:tests/integration/test_mujoco_adapter.py` and imported in `world:tests/test_mujoco_adapter_import.py`. `run_physical_step` is called only in the three fixtures and in `world:tests/unit/test_physical_step.py` |
| Behaviour at the heads of the other repositories | One ad hoc run on 2026-10-11, as described above; not a CI result |
