# The physical causal step, as it exists today

Reviewed against `world` at commit `f496422a5cfb62cd4710ffc61522c9d43b49c6c5`,
with `organism@f15c4c5`, `embodiment@3fe3cda`, `environment@f97ec22` and
`observation@cb07ace`, the revisions pinned by World's integration extra at
`c162b67`. First written against `world@cb4bd6b`; updated when a second
fixture was found, and when World added its protocol-driven physical-step
coordinator in `world:src/world/physical_step.py`.

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
recovery. However, **the solver calls and domain adapters belong to integration test
fixtures, not production adapters.** No solver adapter exists in source, and the
scene projection contracts remain fixture-specific.

The end-to-end integration sequence below is exercised through that coordinator
in `world:tests/integration/physical_step/test_first_biopeia_physical_causal_step.py`,
which says of itself that it is "not a scientific validation or a
production solver adapter". A second fixture,
`world:tests/integration/physical_step/test_procedural_sphere_world_step.py`,
carries out a shorter version of it over a generated scene and is described
in its own section below.

What is real production code are the coordinator and the pieces it calls:
`run_physical_step`, the [durable World runtime](durable-runtime.md), and
functions and types of Organism, Embodiment, Environment and Observation.

## The sequence the fixture carries out

Before the tick, the fixture builds a World from a genesis specification with
three registered owners (one organism, one body, one environment) and one
presence linked to the organism.

Then one tick, in this order. Everything from step 2 to step 9 happens inside
the callback through which World asks the owners to save their state, that
is, after World has durably opened the transition and before it commits.

1. **World opens the transition.** The manifest is preparing.
2. **A correlation is fixed.** It names the World, the tick of the state the
   step starts from, the step, the body, the embodiment episode, the
   morphology revision, the environment revision and the solver
   configuration revision.
3. **Embodiment projects the body** for the solver from its physical state.
4. **Organism produces a command.** An affordance is admitted, an intent is
   activated, a proposal is arbitrated into a commitment, and a controller
   produces a motor command for one actuator. The second actuator is given
   no command.
5. **Embodiment projects the command** onto effectors by stable identity,
   giving one force channel.
6. **A MuJoCo step runs**, in a function of the fixture, over the projected
   body, the Environment's static scene and that channel.
7. **Embodiment adopts the result.** The solver's output is wrapped as a
   candidate tied to the correlation, and the body's physical state accepts
   it only if the correlation is the expected one.
8. **Environment validates and adopts** its side, a static scene tied to its
   own correlation.
9. **The owners' checkpoints are written** and their references returned.
10. **World verifies and commits**, as described in
    [the durable runtime document](durable-runtime.md).
11. **Observation claims are built** for World, body and environment, only
    after the manifest is committed.

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
  morphology revision is refused by Embodiment, the body's state is
  unchanged, and the World is left requiring recovery at tick zero with tick
  one pending
  (`test_stale_morphology_candidate_cannot_publish_the_next_world_cut`).
- **An articulated body can be stepped, restored and stepped again**
  (`test_articulated_mujoco_candidate_is_adopted_and_world_committed`).

## The second fixture: a generated scene

`test_procedural_sphere_world_step.py` exercises the same owner adoption and
World commit without an organism. It generates a scene with
[procedural genesis](../environment/procedural-genesis.md), places its
spheres in the solver, lets a body fall and touch them, has Embodiment and
Environment adopt, commits through the durable World runtime, restores both
owners from the committed cut, and takes one further step
(`test_procedural_spheres_are_adopted_committed_restored_and_reused`).

What it adds to the first fixture:

- **Generated geometry reaches the solver and changes the result.** The body
  touches a generated sphere, and the same step computed with and without the
  spheres gives a different outcome.
- **The generated scene survives the cut.** The Environment checkpoint named
  by the committed manifest restores the same scene with the same genesis
  provenance.
- **A step can follow a restore.**

It has its own function that runs the solver. It involves no Organism code
and no command. It describes itself as "a contract integration test, not
evidence of ecological quality, calibration, physical material properties,
or production crash durability".

## What they do not establish

Stated by the fixture or evident from it:

- **No production solver adapter or domain adapter exists in source.** While
  World provides the protocol coordinator (`run_physical_step`), the domain
  projections, solver invocation, and adoption ports are wired inside the
  integration test fixtures.
- **The solver calls belong to the fixtures.** Each of the two has its own
  function that advances the simulation. There is no solver adapter in any
  repository's source.
- **The organism's state is a stand-in.** The organism owner's checkpoint is
  a small JSON object under a schema named for the fixture, not an Organism
  checkpoint. The action path uses real Organism types fed with fixed values;
  the fixture comments that this is not a claim of autonomous cognition or
  learning.
- **The body's physiology is created inside the step**, with fixed values,
  rather than restored from the body's checkpointed state.
- **The scene is static.** Environment adopts an unchanged scene, written by
  hand in one fixture and generated in the other; nothing in the environment
  evolves.
- **Modality takes no part.** The fixture notes that its current contract is
  sensory transduction only.
- **Durability and replay.** Local checkpoint writes "do not test power-loss
  durability", and continuation after restart "is not compared with
  uninterrupted replay".
- **Physical calibration.** Nothing here is a claim about physical accuracy.

## What supports this description

| Claim | Support |
|---|---|
| The sequence and coordinator integration | Code of `world:src/world/physical_step.py` and the fixture, read in full |
| Determinism, permutation, omitted channel, gravity, stale morphology, articulated restore, and the generated scene's effect, persistence and reuse | The tests named, run by World's integration job in CI at pinned revisions |
| Coordinator protocol invariants and solver failure propagation | Unit tests in `world:tests/unit/test_physical_step.py` |
| Absence of a production solver adapter | A search of the source and test trees of all seven repositories at their main branches on 2026-10-09 found the call that advances a MuJoCo simulation in these two fixtures and nowhere else; the fixtures' own statements |
