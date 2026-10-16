# Organism tests that claim a universal property: inventory (V-01, v1)

**Scope:** a read-only inventory for V-01 of
[the verification strategy](verification-strategy-v1.md). It lists every
Organism test whose name claims a property for all inputs (`never`, `always`,
`invariant`), the property it claims, what it actually exercises, and which
technique would close the gap. It changes no test. Implementation belongs to
Organism (owner direction of 2026-10-17: incremental, invariants and codecs
first).

Read at `organism` `779c097d2123` (main on 2026-10-17). It replaces the "four
of 23 inspected" limit stated in V-01.

## Classes

- **U, universal over a domain:** the claim quantifies over numeric inputs or
  state sequences, and the test fixes one to three configurations. A
  property-based generator (Hypothesis), or a stateful machine for
  sequences, would test the claim as stated.
- **E, finite enumeration:** the domain is a product of small enums. An
  exhaustive `parametrize` over the product is complete; no generator is
  needed.
- **R, rejection contract:** the claim is that one kind of input is refused,
  and one example is tested. A generator adds value only if the refused class
  has internal structure, such as identities or payload shapes.

## Inventory

| Test (file) | Claimed property | Exercised | Class | Note |
|---|---|---|---|---|
| `test_too_few_pulses_never_enter` (test_causal_footprints.py) | Below `min_pulses`, no footprint enters | one estimate, pulses=3, min=4 | U | vary pulses, min and estimates |
| `test_zero_action_linked_hits_never_yield_positive_confidence` (test_controllability_model.py) | Zero action-linked hits give confidence 0 | 3 argument tuples | U | quantify over the other three arguments |
| `test_exclusive_motor_groups_never_babble_antagonistic_channels_together` (test_sensorimotor.py) | No exclusive group is ever co-active | 1,024 ticks of one 8-channel, 4-group configuration | U (stateful) | vary channel count, group layout and tick span |
| `test_output_is_always_bounded_by_tanh` (test_activation.py) | Normalizer output lies in (-1, 1) | 7 values | U | include ±inf, NaN and subnormals |
| `test_extreme_inputs_never_produce_nan_or_inf` (test_graph.py) | Activation is finite | 1 graph, 1 input (1e12) | U | vary topology, weights, bias and inputs, including non-finite |
| `test_oja_update_never_leaves_weight_range_under_repeated_extremes` (test_learning.py) | Weight stays in [-2, 2] | one positive extreme × 2,000 | U | non-finite inputs saturate to +2.0 (F-0171) |
| `test_identical_objectives_never_dominate_each_other` (test_metaplasticity.py) | No objective dominates an equal one | 1 objective | U | for all objectives |
| `test_meta_parameter_never_changes_while_frozen` (test_metaplasticity.py) | Frozen parameter never changes | 1 proposal | U | for all deltas and objectives |
| `test_meta_parameter_never_leaves_its_range` (test_metaplasticity.py) | Value stays in [min, max] | 1 proposal | U | for all values, steps and deltas |
| `test_safety_state_frozen_never_clears_without_explicit_reset` (test_metaplasticity.py) | Frozen until reset | one sequence | U (stateful) | random failure/success/reset sequences |
| `test_no_coactivation_never_reaches_support` (test_structure.py) | No coactivation never yields support | 10 ticks, one pair | U (stateful) | random activation patterns without coactivation |
| `test_already_connected_pair_is_never_reproposed` (test_structure.py) | An existing edge is never re-proposed | 5 ticks, one pair | U (stateful) | random graphs and coactivations |
| `test_advance_edge_age_increments_age_always_and_support_only_when_used` (test_structure.py) | Age +1 always; support +1 only when used | 2 calls | U (stateful) | random used/unused sequences |
| `test_binding_status_invariants` (test_competence_availability.py) | Status and reason combinations are valid | 3 invalid pairs | E | enumerate status × reason exhaustively |
| `test_neutral_outcomes_are_never_evidence` (test_executive_outcome.py) | A NEUTRAL outcome is refused | 1 sample | E | enumerate `OutcomeClass` |
| `test_failed_exploration_never_becomes_no_actuation` (test_exploration_composition.py) | Failed evaluation raises, never reported as no-actuation | 1 injected exception | R | vary the failure point |
| `test_cached_index_never_crosses_owners` (test_exploration_v5.py) | The cache never serves another owner | 1 other identity | R | generate identities |
| `test_missing_current_applicability_context_is_unknown_and_never_executable` (test_competence_availability.py) | Missing context is never executable | 1 binding | R | — |
| `test_epistemic_value_never_overrides_higher_pragmatic_utility` (test_policy.py) | Epistemic value never overrides higher pragmatic value | 1 scenario | U | vary values, confidences and margins (ordering property) |
| `test_counterfactual_is_generated_and_never_executes_an_intervention` (test_generative_counterfactual.py) | A counterfactual is never an intervention | 1 workspace | R | — |
| `test_remove_node_preserves_non_edge_graph_invariants` (test_reversible_structure_phase1.py) | Removal keeps the predictor-target invariant | 1 graph | U | random graphs and removals; check every graph invariant |
| `test_expression_restore_rejects_activation_on_never_updated_state` (test_checkpoint.py) | Activation is refused when update_count is 0 | 1 payload | R | generate payload mutations (overlaps V-02) |
| `test_effect_representation_enforces_opaque_identity_invariants` (test_label_invariance_conformance.py) | Non-organism identities are refused | a few strings | R | generate identifiers, including near-valid ones |

**Totals:** 15 U (10 numeric or ordering, 5 stateful), 2 E, 6 R.

## Order proposed to Organism (non-binding)

1. **Numeric bounds on the learning and activation path:** Oja, tanh,
   graph finiteness, meta-parameter range. These are where non-finite inputs
   matter (F-0171), and each property is a few lines.
2. **Stateful structure and safety machines:** structural plasticity, edge
   age, safety state, motor groups. These are `RuleBasedStateMachine`
   candidates, and they overlap V-06.
3. **The two E rows:** exhaustive `parametrize`, with no new dependency.
4. **R rows:** only where the refused class has structure; the rest stay
   example tests.

## Limits

Selection is by test name, so a universal property under another name is
missed. Classes and notes are a reading of the test bodies, not a run. No
test was changed or executed for this inventory.
