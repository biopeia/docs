---
diataxis_kind: reference
document_id: REF-ORG-COGNITIVE-GRAPH-INVARIANTS
domain: organism
source_of_truth: organism:src/organism/cognition/graph.py
review_basis: organism@779c097
---

# Cognitive Graph Parameters and Topological Invariants

This is a **bounded source-code reference**, not a claim of learned cognition or autonomous efficacy. The source snapshot used for this update is `organism@779c097` (2026-10-16). The values below describe the default `KernelLimits` and declared types at that revision; callers may configure stricter valid ceilings.

## Node and edge catalogs

`NodeKind` is a closed enumeration with the exact values `sense`, `concept`, `state`, `predictor`, `gate` and `readout`. There is no `motor`, `sensory` or `internal` node category in this enumeration. The graph itself does not directly issue motor commands.

`EdgeKind` is a closed enumeration with `excitatory`, `inhibitory`, `predictive` and `gating`.

| Element | Field / invariant | Actual contract |
| --- | --- | --- |
| Node | `node_id` | Unique identifier, validated on graph construction |
| Node | `tau` | Finite float in `[0.1, 10.0]` |
| Predictor node | `predicts_node_id` | Must name an existing node; forbidden on non-predictor nodes |
| Edge | `weight` | Finite float in `[-2.0, 2.0]` |
| Edge | `plasticity` | Finite float in `[0.0, 1.0]` |
| Edge | `delay_ticks` | Integer 0 or 1 |
| Edge | Endpoints | Both must name declared nodes; duplicate source/target/kind combinations rejected |
| Graph | `max_concepts` | Concept nodes are counted independently of total nodes |

## Default resource ceilings

These are `KernelLimits` defaults, **not genome-inherited or learned values**:

| Field | Default | Source |
| --- | ---: | --- |
| `max_nodes` | 768 | `KernelLimits.max_nodes` |
| `max_concepts` | 192 | `KernelLimits.max_concepts` |
| `max_edges` | 6144 | `KernelLimits.max_edges` |
| `max_tentative_edges` | 512 | `KernelLimits.max_tentative_edges` |
| `max_structural_mutations_per_consolidation` | 16 | `KernelLimits.max_structural_mutations_per_consolidation` |
| `consolidation_interval_ticks` | 32 | `KernelLimits.consolidation_interval_ticks` |

This is a selected reference table, not an exhaustive inventory of every `KernelLimits` field. The full class also bounds checkpoint sizes, consolidation and episodic memory.

## Learning and transition boundaries

The graph's activation pass and the learning operations are distinct. Eligibility updating accepts a caller-supplied `decay`; Oja updating accepts a caller-supplied `learning_rate`, `modulation` and `eligible`. Neither is a universal default `decay_factor = 0.95` or `plasticity_rate = 0.01` defined by `KernelLimits`. This reference does **not** claim a universal `activation_threshold = 0.1`.

A node named `concept` or `predictor` does not establish conceptual understanding or empirically effective prediction. See [ADR-0083](../../technical/adr/ADR-0083-causal-cycles-have-explicit-commit-semantics.md) for the architectural commitment boundary; do not infer that every graph mutation is an autonomous committed learning event.

## What supports this specification

| Claim | Code source |
| --- | --- |
| Node/edge enumerations and ranges | `organism:src/organism/cognition/types.py` |
| Graph topology validation | `organism:src/organism/cognition/graph.py` |
| Kernel ceiling defaults | `organism:src/organism/cognition/limits.py` |
| Eligibility and Oja update inputs | `organism:src/organism/cognition/learning.py` |

A change in any cited source requires a new source-revision check before the tables are described as current.
