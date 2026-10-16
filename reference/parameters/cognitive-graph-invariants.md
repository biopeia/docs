---
diataxis_kind: reference
document_id: REF-ORG-COGNITIVE-GRAPH-INVARIANTS
domain: organism
source_of_truth: organism:src/organism/cognition/graph.py
review_basis: organism@9c9339a
---

# Cognitive Graph Parameters and Topological Invariants

Reviewed against `organism` at commit `9c9339a` (main on 2026-10-14). Statements are marked by what supports them: the code, the tests, or an accepted decision.

## Topological elements

The Organism cognitive graph is an explicitly ticked directed graph of cognitive nodes and activation edges (`organism:src/organism/cognition/graph.py`).

### Node categories

| Category | Role | State Ownership | Invariants |
|---|---|---|---|
| `sensory` | Accepts bound sensory receptors from modality projection. | Transient (per cut) | Immutable topology during execution step; values normalized in $[0.0, 1.0]$. |
| `internal` | Intermediate associative activation dynamics. | Adaptive longitudinal | Bounded activation levels; subject to synaptic weight plasticity. |
| `motor` | Drives effector commands to embodiment actuation. | Transient (per cut) | Direct output projection; saturation bounds strictly clamped. |

### Invariant parameters

| Parameter | Type | Default / Range | Meaning |
|---|---|---|---|
| `max_nodes` | integer | 1024 | Hard limit on maximum vertex capacity per individual organism. |
| `max_edges` | integer | 4096 | Upper ceiling on total directed connections to preserve longitudinal determinism. |
| `decay_factor` | float | 0.95 ($0.0 < \lambda \le 1.0$) | Exponential decay multiplier applied to node activations at each causal tick. |
| `activation_threshold` | float | 0.1 | Minimum aggregate input required for non-linear node excitation. |
| `plasticity_rate` | float | 0.01 | Hebbian-style adaptation rate bounded per causal step. |

## Boundary limitations

- Node types labeled as `predictor` or `concept` denote internal structural classifications and edge routing heuristics; they do not represent validated autonomous cognitive understanding.
- Graph plasticity occurs only within approved commit windows; arbitrary mutation during an active causal cycle is forbidden by causal commit semantics ([ADR-0083](../../technical/adr/ADR-0083-causal-cycles-have-explicit-commit-semantics.md)).

## What supports this specification

| Claim | Support |
|---|---|
| Directed graph node and edge classes | `organism:src/organism/cognition/graph.py` |
| Maximum node and edge bounds | `organism:src/organism/cognition/limits.py` |
| Bounded decay and plasticity rules | `organism:src/organism/cognition/learning.py` and `organism:src/organism/cognition/metaplasticity.py` |
| Graph checkpoint serialization | `organism:src/organism/cognition/portable_checkpoint.py` and `organism:tests/source_unit/cognition/test_portable_checkpoint.py` |
