# The MuJoCo step executor

Reviewed against `world` at commit `95f5064c6b06bd66bb58a72110b066afe4ca70b0`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run made at that revision on
2026-10-11, or a statement by the repository about its own intent.

## What it is

World's source holds one function that advances a MuJoCo simulation by one
step: `world:src/world/adapters/mujoco.py::execute_mujoco_step`. A caller
hands it a model that MuJoCo has already compiled, the positions and
velocities to start from, and the control values to apply. It runs one step
and returns the positions and velocities afterwards, together with the
[physical step context](physical-step.md) it was given.

That is all it is. It is a way to ask MuJoCo for one number-crunching step
and get the answer back as an immutable value. It decides nothing about the
World, a body or an environment, and it is not the solver of
[the physical causal step](physical-step.md): no code path of that step
reaches it. The module describes itself as "An optional, engine-specific
MuJoCo single-step executor", and the package it sits in as adapters that
"execute numerical capabilities only" and "do not own or adopt World,
Environment, or Embodiment state".

It is optional in a literal sense. MuJoCo is not a dependency of the World
package; it is declared in an extra named `mujoco`, pinned to version 3.14.0.
Importing World, or importing this module, does not import MuJoCo
(`test_adapter_module_import_does_not_import_optional_engine`); calling the
function does, and fails with a plain error when MuJoCo is absent
(`test_executor_reports_missing_optional_dependency`). The function is not
exported from the top of the World package (ad hoc run).

## What goes in and what comes out

In:

- a `PhysicalStepContext`, the value World's coordinator issues for a step;
- a compiled MuJoCo model;
- three sequences of numbers in MuJoCo's own layout: generalized positions
  (`qpos`), generalized velocities (`qvel`) and controls (`ctrl`).

Out: a `MujocoStepCandidate` holding that same context and the positions and
velocities after one step, as tuples.

The control sequence must always be given, even when the model has no
actuator, in which case it is empty
(`test_executor_requires_explicit_control_vector`). The function's
documentation gives the reason: it "does not infer an absent control vector".

## What it checks

Read from the code; each is covered by the test named.

- The context is a `PhysicalStepContext`
  (`test_executor_rejects_untyped_correlation_context`).
- The model is a compiled MuJoCo model
  (`test_executor_rejects_non_mujoco_model`) and its time step is a positive
  finite number. The second half has no test.
- Each of the three sequences contains only finite numbers, booleans
  excluded, and has exactly the length the model expects
  (`test_executor_rejects_invalid_explicit_vectors`).

Nothing else is checked. Two things in particular are not:

- **That World issued the context.** The type is checked and the content is
  not. In an ad hoc run a context naming a World that did not exist, at ticks
  41 and 42, was accepted and returned. The documentation says the context
  "is carried for correlation only: this function checks its type but does
  not prove that World issued it or authorize the transition".
- **That the model is the one the context describes.** The context carries a
  morphology revision, an environment revision and a solver configuration
  revision. The function compares none of them with the model. Its
  documentation says it "can verify only the compiled model's effective
  timestep, not whether its author explicitly declared it or whether the
  configuration revision is truthful".

## What it deliberately does not do

The module's own description lists these, and the code agrees with each:

- **It defines no Biopeia scene.** It takes a model already compiled. How a
  body from Embodiment and a scene from Environment become that model is
  left to the caller, and nothing in source does it.
- **It assembles no owner projection.** It never sees Embodiment's body
  input or Environment's scene.
- **It derives no units and no identity.** Positions and velocities are
  MuJoCo's flat vectors. Which entry belongs to which body, joint or
  actuator, and in what unit, is the caller's business: "Callers must resolve
  domain units, stable body/actuator correspondence, and omitted-command
  semantics before this boundary."
- **It changes no owner's state.** It reads its inputs and returns a new
  value; the input sequences were unchanged afterwards (ad hoc run).
- **It commits nothing.** "The returned values are only a solver candidate;
  owner validation/adoption and World commit remain separate operations."

Three further limits are not stated by the module and follow from the code:

- **The result is not split by owner.** The coordinator expects a solver to
  return a candidate with a part for the body and a part for the
  environment (`world:src/world/physical_step.py::PhysicalStepCandidate`).
  This function returns one pair of vectors for the whole model, in a type
  of its own that is not that one.
- **Only positions, velocities and controls are set.** Forces applied
  directly to a body or to a joint cannot be passed. Both MuJoCo fixtures of
  the physical step drive the body that way, not through controls.
- **Each call starts from a fresh simulation state.** The function creates a
  new MuJoCo data object, writes the three vectors into it and steps once.
  Anything else MuJoCo carries from one step to the next starts from its
  default every time. Two ad hoc runs show what that means in practice. For
  a sphere falling onto a plane, 200 calls chained by feeding each result
  into the next differed from 200 steps of one continuous simulation by at
  most 4.5e-11 in any position or velocity: close, not identical; the cause
  was not investigated. For a model whose actuator has an internal
  activation state, a control of 1 left the joint velocity at exactly zero
  after the call. The function has no input for that activation and returns
  none, so a chain of calls cannot carry it.

Contacts, sensor readings and the simulation time are not returned.

## Who calls it

A search of the source and test trees of all seven repositories at their
heads on 2026-10-11, for the function, its result type, its error type and
the module path:

- **In source: nobody.** No module of World or of any other repository
  imports `world.adapters.mujoco`.
- **In tests: its own two test files, both in World.**
  `world:tests/integration/test_mujoco_adapter.py` calls it, and
  `world:tests/test_mujoco_adapter_import.py` imports the module without
  MuJoCo installed.

The three fixtures that drive World's coordinator do not call it. The two
that use MuJoCo each build a model and advance it in functions of their own.

Its contract tests live under `tests/integration`, which World's default
test run does not collect; they need MuJoCo. World's integration job in CI
installs it and runs them. In an ad hoc run at the reviewed revision all ten
cases passed, as did the import test.

## How this bears on what was said before

Until this revision, the documentation of the physical step said that the
call advancing a MuJoCo simulation existed only inside two test fixtures, and
that no solver adapter existed in any repository's source. The first half is
no longer true: the call now also exists in World's source, in this module.

What remains true is narrower and should be said exactly:

- a function that runs one MuJoCo step exists in source;
- nothing in source or in tests uses it to carry out a physical step;
- it could not be handed to the coordinator as its solver without more code,
  because it takes a compiled model and raw vectors where the coordinator
  passes the owners' projections, and returns a different type;
- the code that would turn the owners' projections into a model and vectors,
  and the result back into candidates for each owner, exists only in the
  fixtures, written for the one body each supports.

The repository says the same of its own change: the module "does not
establish the repository/owner for a production solver adapter, settle
cross-domain authorization/correlation, or implement projection/owner-adoption
composition", and the issue that tracks the missing adapter "must not be
closed by this executor alone".

## State, time and failure

The function holds no state between calls and writes nothing to disk. It
reads no clock; the time step is the model's. It is not part of a causal cut
and a failed World transition leaves nothing of it behind.

It carries the two ticks of the context through unchanged and does not
compare them with anything.

## Beside the accepted decisions

[ADR-0098](../../technical/adr/ADR-0098-physical-substrate-and-causal-integration.md)
and
[ADR-0073](../../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md)
govern the physical substrate and the contracts of a physical step. They are
set beside the code here and no conformance is ruled. The repository's README
says of this function: "MuJoCo remains an optional numerical substrate, not a
semantic authority. No calibration or physical-equivalence claim is made."

## What supports this description

| Claim | Support |
|---|---|
| Inputs, outputs and the checks made | Code of `world:src/world/adapters/mujoco.py`, read in full, and the tests in `world:tests/integration/test_mujoco_adapter.py` |
| Importing does not require MuJoCo | `test_adapter_module_import_does_not_import_optional_engine` in `world:tests/test_mujoco_adapter_import.py`, part of World's default suite |
| The tests pass | World's integration job in CI; and an ad hoc run at the reviewed revision with MuJoCo 3.14.0 and Python 3.12 |
| A fabricated context is accepted; inputs are not modified; not exported from the package; chained calls against one simulation; the actuator with activation state | Ad hoc runs at the reviewed revision; no test |
| Who calls it | Text search of the seven repositories at their heads on 2026-10-11 |
| What it is for and what it leaves open | The module's and the repository's own statements (`world:README.md`, `world:MIGRATION.md`); statements of intent, not results |

No test checks the positive time step, a model with actuators, or a result
against an independent calculation. One test asserts that two calls with the
same input give the same output and that a free body gains downward velocity
(`test_executor_returns_deterministic_candidate_with_supplied_step_context`).
Nothing here is a claim about physical accuracy.

## Open questions

- Which repository is to own the code that turns owner projections into a
  solver model, and solver output into candidates per owner. The repository
  leaves it open.
- Whether a step executor should carry solver state between steps, and
  whether forces applied to bodies or joints are to be expressible.
- Whether the revisions in the context are meant to be checked against the
  model by anyone.
