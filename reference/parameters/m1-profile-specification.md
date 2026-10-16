---
diataxis_kind: reference
document_id: REF-WLD-M1-PROFILE
domain: world
source_of_truth: world:src/world/m1_profile.py
review_basis: world@1f35e92611ed76f1863136916601f07fc2fd78c1
---

# M1 Operator Profile Specification

Reviewed against `world` at commit `1f35e92611ed76f1863136916601f07fc2fd78c1` (main on 2026-10-15). Statements are marked by what supports them: the code, the tests, or an accepted decision.

## Schema identity and parameters

The M1 operator profile schema is identified as:
`biopeia.world.m1.scalar-sensorimotor-profile` version `1` (`world:src/world/m1_profile.py`).

Configuration files conform to strict validation against this schema prior to runtime instantiation.

### Top-level fields

| Field | Type | Required | Description |
|---|---|:---:|---|
| `schema_name` | string | Yes | Must equal `"biopeia.world.m1.scalar-sensorimotor-profile"`. |
| `schema_version` | integer | Yes | Must equal `1`. |
| `world_id` | string | Yes | Unique string identifying the World instance. |
| `physics` | object | Yes | Physics engine configuration block. Must specify `engine: "mujoco"` and `solver_version: "3.15.0"`. |
| `embodiment` | object | Yes | Morphology, mass, joint damping, actuator bindings, and sensor receptor geometry. |
| `environment` | object | Yes | Static arena boundaries, resource genesis, and scalar gradient field parameters. |
| `organism` | object | Yes | Cognitive graph parameters, initial state seeds, and epistemic conventions. |
| `runtime` | object | Yes | Process execution limits, maximum tick steps, and bridge bind settings. |

### Physics engine invariants

- **Solver engine:** `mujoco`
- **Pinned version:** `3.15.0` (`world:src/world/m1_process.py:53-56`).
- **Integrator:** Semi-implicit Euler / standard MuJoCo time-step (typically 0.002s to 0.01s).

### Command-line interface syntax

`world-m1` entry point arguments:

```bash
world-m1 --profile <PATH_TO_PROFILE_JSON> \
         --state-root <PATH_TO_NEW_DIRECTORY> \
         --cycles <INT_BETWEEN_1_AND_10000>
```

- `--profile`: Path to a valid JSON profile matching `biopeia.world.m1.scalar-sensorimotor-profile` v1.
- `--state-root`: Path to an unallocated directory where `manifest/`, `journal/`, and `checkpoints/` will be generated.
- `--cycles`: Integer bounded in the interval $[1, 10000]$.

## What supports this specification

| Claim | Support |
|---|---|
| Schema name and version | `world:src/world/m1_profile.py::load_operator_profile` |
| MuJoCo 3.15.0 version constraint | `world:src/world/m1_process.py:53-56` |
| CLI arguments and cycle range `[1, 10000]` | `world:src/world/m1_process.py:parse_args` and `world:pyproject.toml:12-13` |
| Profile fixture validation | `world:tests/test_m1_profile.py::test_exemplary_m1_profile_validates` |
