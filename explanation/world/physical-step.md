# The physical causal step, as it exists today

Reviewed against `world` at commit `cb4bd6b0506b554bf4187b36c23095a7521c4504`,
with `organism@f15c4c5`, `embodiment@3fe3cda`, `environment@f2ef8c2` and
`observation@cb07ace`, the revisions pinned by World's integration extra.

## What this is about

The approved design
[Biopeia Physical-Step and Causal-Commit Integration v1](../../technical/design/runtime/biopeia-physical-step-integration-v1.md)
describes how one physical step should cross the authorities: World
authorises it, Embodiment and Environment project their state, a solver
computes a candidate, each owner validates and adopts its own part, and World
commits the cut.

This document describes where that sequence exists in code today. The answer
needs stating plainly at the start: **it exists as an integration test
fixture, not as a component.** No module in `world`, or in any other
repository, orchestrates a physical step. The sequence below is carried out
by one function inside
`world:tests/integration/physical_step/test_first_biopeia_physical_causal_step.py`.
The fixture says of itself that it is "not a scientific validation or a
production solver adapter".

What is real production code are the pieces the fixture calls: the
[durable World runtime](durable-runtime.md), and functions and types of
Organism, Embodiment, Environment and Observation.

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

## What they do not establish

Stated by the fixture or evident from it:

- **No orchestrating component exists.** The order of the steps above is the
  order of statements in a test. Nothing enforces it elsewhere.
- **The solver call belongs to the fixture.** There is no solver adapter in
  any repository's source.
- **The organism's state is a stand-in.** The organism owner's checkpoint is
  a small JSON object under a schema named for the fixture, not an Organism
  checkpoint. The action path uses real Organism types fed with fixed values;
  the fixture comments that this is not a claim of autonomous cognition or
  learning.
- **The body's physiology is created inside the step**, with fixed values,
  rather than restored from the body's checkpointed state.
- **The scene is static.** Environment adopts an unchanged scene; nothing in
  the environment evolves.
- **Modality takes no part.** The fixture notes that its current contract is
  sensory transduction only.
- **Durability and replay.** Local checkpoint writes "do not test power-loss
  durability", and continuation after restart "is not compared with
  uninterrupted replay".
- **Physical calibration.** Nothing here is a claim about physical accuracy.

## What supports this description

| Claim | Support |
|---|---|
| The sequence | Code of the fixture, read in full |
| Determinism, permutation, omitted channel, gravity, stale morphology, articulated restore | The tests named, run in World's CI at pinned revisions |
| Absence of an orchestrating component and of a solver adapter | A search of the source trees of all seven repositories at their main branches on 2026-10-09 found no call that advances a MuJoCo simulation outside this fixture; the fixture's own statements |
