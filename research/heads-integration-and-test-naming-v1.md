# Integration at the heads, and test names that claim capabilities (V-07, V-08, v1)

**Scope:** two read-only investigations for
[the verification strategy](verification-strategy-v1.md). They are evidence
for the owners and order no work. Implementation belongs to each repository.

## V-07. One integration run with every repository at its head

On 2026-10-16, one virtual environment was built from `git archive` copies
of every repository's `origin/main`. Python was 3.12 and MuJoCo exactly
3.15.0. The revisions were:

| Repository | Revision |
|---|---|
| lab | `4e14108f5bb9` |
| world | `d66ac6197c8e` |
| organism | `637bc21a7e2a` |
| embodiment | `8f9576a8cf5b` |
| environment | `4eb1f8c3393a` |
| observation | `572c86f8fce6` |
| modality | `62af4aba0714` |

| Suite | Result | Reading |
|---|---|---|
| World `tests/integration` | 95 passed, 6 failed | All 6 failures are `test_m1_process` exiting at preflight with return code 2. Archive installs carry no `direct_url` commit pins, so this is the environment, not a defect |
| Lab `tests/integration` and `tests/observation_integration` | 4 passed, 34 skipped, 1 failed | The skips are by design: material-transfer execution is disabled until verified authorization exists. The failure is F-0173: a test that loads World's test file through `runpy` breaks once World publishes spatial projections |

What this shows: the heads worked together for World's integration suite in
that run. They did not for one Lab test, which is pinned to an older World
and coupled to World's test internals. What it does not show: anything about
later heads. A scheduled, non-blocking run of the same kind (V-07 as
proposed) would keep this current without changing what a pin means. The
preflight failures show such a run needs `direct_url` pins, or World's
preflight in a mode meant for it; that is World's decision.

## V-08. Test names that assert a capability

`git grep` over all `tests/` at the heads above, for names containing
*learn*, *acquir*, *improv*, *understand*, *discover*, *generaliz* and
similar. Names where the word is used neutrally (for example *reason* as an
error reason, or *adapter*) are left out.

| Test (repository) | What the name suggests | What it checks |
|---|---|---|
| `test_longitudinal_learning_and_continuity_in_real_runtime` (world) | An Organism learns over a real run | A weight rises above 0.20 over 5 cycles, an activation crosses a threshold on one probe, and the state survives restore. That is internal modification and continuity, with no comparison to a baseline |
| `test_lagged_shadow_prediction_learns_delayed_relation_without_graph_mutation` (organism) | Learning | A candidate outside the graph reaches `supported` against persistence on ten supplied values; its own docstring says this is not a causal claim |
| `test_composed_shadow_prediction_uses_two_learned_local_relations` (organism) | Learned relations | Two least-squares slopes fitted from supplied samples |
| `test_cognitive_primitive_replays_only_learned_motor_pattern` (organism) | A learned pattern | Replays a pattern retained from supplied statistics |
| `test_exploration_can_discover_temporal_chunk_across_synergy_boundary` (organism) | Discovery | Chunk statistics cross a grouping boundary |

`organism#174` shows the convention that works. It renamed
`test_a_predictor_measurably_learns_…` to
`test_alternating_signal_oja_loop_does_not_beat_zero_output_baseline` and
compared against trivial baselines. Lab's
`test_sensory_regime_reversal_is_preserved_without_learning_claim` states its
non-claim in the name.

**Proposal (a convention, not a gate):**

- Rename the World test to say what it checks, for example
  `…_weight_change_and_continuity_…`. It is the precursor of the
  longitudinal-learning campaign, and its name should not be read as
  evidence for the campaign's question.
- For the Organism names, keep *learned* where it means fitted from supplied
  data, but the docs should not quote these names as evidence of learning.

## Limits

One run on one day. Name selection by keyword can miss names and include
false positives.
