# The cognitive graph and its explicit-tick transition

Reviewed against `organism` at commit `6543188ff302a5f2dc8002c0086252d6061e5310`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run, or an accepted decision.

## What it is

The package called `cognition` is built around one structure: a small directed
graph of named nodes joined by weighted edges. Numbers are placed on some of
its nodes, one pass of arithmetic is run, and a number comes out for every
node. Nothing else happens in that pass. No weight changes, nothing is
remembered inside the graph, and nothing is done to a body.

The repository's migration notes describe what was copied into this package
with a disclaimer that applies to every name used below: "Copied cognitive
structures, learning and private-model implementation. No efficacy claim is
implied." The names in the code (sense, concept, predictor, gate, readout) are
labels on nodes. This document says what the code does with each label, which
in most cases is less than the label suggests.

Three pieces make up the unit:

- the **graph**, a validated, bounded table of nodes and edges;
- the **transition**, the only function that advances the graph for an
  identified Organism at an explicit tick, and the small state it carries from
  one tick to the next;
- two helpers at the edges: a **normalizer** that turns a raw reading into a
  bounded number, and the **birth** loader that supplies the initial graph.

How weights and structure are changed is a separate mechanism, described in
[how the graph is changed](graph-plasticity.md). What is saved is described in
[the cognitive checkpoint](cognitive-checkpoint.md).

## The graph

A node (`organism:src/organism/cognition/graph.py::PlasticNode`) has an
identifier, one of six kinds, a bias, a divisor called `tau`, and, for one
kind only, the identifier of another node. An edge (`PlasticEdge`) has a
source, a target, one of four kinds, a weight in [-2, 2], a number called
`plasticity` in [0, 1], a delay of 0 or 1 tick, and five bookkeeping fields
(`eligibility`, `support`, `age_ticks`, `stable_ticks`, `last_use_tick`).

Construction checks the whole table and refuses it otherwise. The rules, each
covered by a test in `organism:tests/source_unit/cognition/test_graph.py`:

- identifiers are unique and well formed (`test_rejects_duplicate_node_id`,
  `test_rejects_malformed_node_id`);
- every edge joins declared nodes (`test_rejects_dangling_edge_source`,
  `test_rejects_dangling_edge_target`), and at most one edge of a given kind
  joins a given pair (`test_rejects_duplicate_source_target_kind_edge`,
  `test_allows_two_edges_same_endpoints_different_kind`);
- no edge may arrive at a node of kind sense
  (`test_rejects_a_sense_node_with_an_incoming_edge`);
- an edge with delay 0 must leave a sense node
  (`test_rejects_delay_zero_from_a_non_sense_source`); the code gives the
  reason: "only a SENSE source has a value available this tick";
- a node of kind predictor must name an existing node that it "predicts", and
  no other kind may (`test_predictor_node_without_predicts_node_id_is_rejected`,
  `test_non_predictor_node_with_predicts_node_id_is_rejected`);
- the numbers of nodes, of concept nodes and of edges stay under ceilings held
  in a separate value (`test_rejects_node_count_exceeding_kernel_limit`,
  `test_rejects_concept_count_exceeding_kernel_limit`,
  `test_rejects_edge_count_exceeding_kernel_limit`).

Those ceilings (`organism:src/organism/cognition/limits.py::KernelLimits`)
default to 768 nodes, 192 concept nodes and 6144 edges. The class describes
itself as "Hard, owner-configured resource ceilings for the cognitive graph".
It holds twenty-three numbers; constructing a graph reads three of them. Several others
refer to an episodic memory and a consolidation schedule that are not in this
package.

## One pass of activation

Read from `CognitiveGraph.activate` and confirmed by running it.

For each node, in order:

1. A **sense** node takes the number supplied for it, or 0 if none was
   supplied (`test_activate_echoes_sense_inputs_directly`).
2. Any other node sums its incoming edges. An edge with delay 0 contributes
   its weight times the number supplied *this* tick for its source; an edge
   with delay 1 contributes its weight times the source's value from the
   *previous* pass, or 0 if there was none
   (`test_delay_zero_sense_edge_reacts_immediately`,
   `test_delay_one_edge_ignores_this_ticks_input_uses_previous`,
   `test_cold_start_with_no_previous_treats_delay_one_sources_as_zero`).
3. Edges of kind **gating** are handled first and differently: each gives a
   factor, its contribution clipped to [0, 1], and the factors are multiplied
   together. Every other incoming edge is scaled by that product
   (`test_gating_edge_near_zero_suppresses_a_co_targeting_edge`,
   `test_two_gating_edges_combine_by_product`).
4. The node's value is `tanh((bias + sum) / tau)`, so always strictly between
   -1 and 1 (`test_extreme_inputs_never_produce_nan_or_inf`).

The result is a frame: the tick it was given, the value of every node, and the
subset belonging to nodes of kind **readout**
(`test_readouts_contains_only_readout_kind_nodes`). The result does not depend
on the order in which nodes and edges were declared
(`test_activation_is_independent_of_node_and_edge_construction_order`).

### What the kinds do, and do not do

This is where names outrun behaviour. Read from the code and confirmed by a
run in which every case below was constructed.

| Name in the code | What `activate` does with it |
|---|---|
| Node kind `sense` | Copies its input. Cannot have incoming edges. |
| Node kind `readout` | Computed like any other node; its value is also listed separately in the frame. |
| Node kind `predictor` | Computed like any other node. The node it names is not read during activation. |
| Node kinds `concept`, `state`, `gate` | Computed like any other node. Three nodes of these kinds with the same incoming edge gave the same value. `concept` is additionally counted against a ceiling. |
| Edge kind `gating` | Multiplicative factor, as above. |
| Edge kinds `excitatory`, `inhibitory`, `predictive` | Identical. Each adds weight times source value. An edge of kind `inhibitory` with weight +1 raised its target exactly as an `excitatory` one did; whether an edge inhibits is decided by the sign of its weight alone. |
| `tau` | A divisor inside the `tanh`. It is not a time constant: a node keeps no value between passes that could decay. |
| `plasticity`, `stable_ticks` on an edge | Validated, stored and saved. No activation or update function uses `plasticity`, and nothing writes `stable_ticks` (search of `organism:src` for both names, 2026-10-09). |
| The tick | Copied into the frame. It does not enter the arithmetic. |

A node of kind `gate` and the constant `GATE_RANGE` are declared and nothing
uses them; gating is a property of edges, not of that node kind.

There is no node kind for action. The code says so and a test pins it
(`test_no_action_node_kind_exists`): "There is deliberately no ACTION kind --
readouts feed existing, already-governed consultative circuits; the graph
itself never acts." What consumes a readout is outside this package; see
[where it is used](#where-it-is-used).

### "Immutable" means the table, not the numbers

The class documents itself as immutable; one of its docstrings says "the
graph never mutates after __init__" and that a change "builds a whole new
CognitiveGraph". That holds for the set
of nodes and edges. It does not hold for the numbers on the edges. An edge is
a mutable object, the graph keeps the objects it was given, and a graph built
from another graph shares them.

Confirmed by running the module:

- changing an edge's weight after construction changed the graph's next
  readout, with no validation: a weight of 5, outside the permitted range,
  was used as given;
- after a structural change produced a second graph, changing a weight
  through the second graph changed it in the first, because both hold the
  same edge object.

The second point matters wherever an "old" graph is kept as something to fall
back on. It is recorded as finding F-0072.

## The transition

`organism:src/organism/cognition/transition.py::advance_cognition` is the
entry point that ties a pass to an Organism and to time. It takes a state, a
graph, a mapping of numbers called `opaque_signals`, and a tick that the
caller must supply. It returns a new state and the frame.

The state (`CognitiveTransitionState`) is three things: the Organism's
identity, the last tick advanced, and the previous frame's values as a sorted
tuple. It is immutable. The module describes it as "an in-memory value; it is
not by itself a portable checkpoint or a complete Organism continuation."

What the function enforces, each with a test in
`organism:tests/source_unit/cognition/test_transition.py`:

- the tick is a non-negative integer strictly greater than the last one
  (`test_transition_rejects_repeated_or_decreasing_causal_tick`);
- every supplied signal names a node of kind sense in this graph and is a
  finite number (`test_transition_rejects_non_sense_or_unknown_signal_nodes`,
  `test_transition_rejects_nonfinite_or_nonnumeric_signal`);
- a refused call leaves the caller's state as it was
  (`test_transition_rejects_invalid_tick_without_changing_prior_state`);
- the previous frame is what delay-1 edges read
  (`test_transition_uses_explicit_tick_and_prior_activation`).

What it does not enforce, confirmed by running it:

- **Ticks need not be consecutive.** Advancing from tick 1 to tick 1000 gave
  the same frame as advancing to tick 2. The number of ticks skipped has no
  effect, which follows from the tick not entering the arithmetic.
- **The state is not tied to a graph.** A state whose previous frame named a
  node absent from the graph was accepted, and the stray value ignored. The
  graph carries no identity, so one graph can be advanced under any identity.
- **A missing signal is a zero.** A sense node with no entry in
  `opaque_signals` takes 0, indistinguishable from a reading of 0.

The function reads no host clock and draws no random number. The only time it
knows is the tick argument. That is the behaviour
[ADR-0090](../../technical/adr/ADR-0090-host-wall-clock-time-is-never-implicit-causal-authority.md)
asks for when it says causal times "must be explicit and distinct". The whole
package was searched for other sources; the result is in
[time and randomness](#time-and-randomness).

## The normalizer

A raw reading can be any size; a sense node expects something bounded.
`organism:src/organism/cognition/activation.py::SensoryNormalizer` keeps a
running mean and variance for one named sense, and converts each reading to
`tanh` of its clipped z-score against those statistics before updating them
(`test_output_is_always_bounded_by_tanh`,
`test_repeated_identical_values_converge_toward_zero_activation`,
`test_a_fresh_outlier_after_a_stable_baseline_produces_a_large_magnitude`).

Two consequences should be stated plainly. First, what reaches the graph is
not the reading but its departure from that sense's own recent history: a
constant reading tends to zero whatever its size. Second, the normalizer
considers itself established only after five readings
(`test_established_after_minimum_samples`), and only established normalizers
are saved.

Nothing in the package connects a normalizer to the transition. The transition
accepts whatever numbers it is given; whether they were normalized is the
caller's affair (search of `organism:src` for `SensoryNormalizer`,
2026-10-09: it is constructed only by the checkpoint codec).

## Birth

`organism:src/organism/cognition/birth.py` loads two packaged files: a base
genome and a base graph. The base graph is empty. The file contains no nodes
and no edges, and the test is named for it
(`test_base_graph_is_a_true_tabula_rasa`). The module says: "The germinal
cognitive graph is intentionally empty; body surfaces are connected
independently after birth."

Advancing the empty graph works and yields an empty frame (confirmed by a
run). The connection of body surfaces that the sentence refers to is not in
this repository: no function in `organism:src` calls the loader, and the only
code able to add a node is the generic structural change described in
[how the graph is changed](graph-plasticity.md), which nothing calls either
(search of `organism:src` for `load_base_cognition`, `load_base_graph` and
`apply_mutations`, 2026-10-09). So at
this revision an Organism born from the packaged defaults has a graph that
computes nothing, and the only graphs that compute something are the ones
tests construct by hand.

## Where it is used

Within `organism:src`, nothing calls `advance_cognition` or `activate`
(search of `organism:src` for both names, 2026-10-09). The callers are tests:

- this repository's own unit tests;
- two integration tests in the World repository,
  `world:tests/integration/test_first_biopeia_causal_tick.py` and
  `world:tests/integration/test_durable_checkpoint_restore_slice.py`, which
  build a graph of two nodes and one edge, feed it a constant 0.5 that the
  fixture names as its own input, and advance it inside a World tick.

In the first of those the fixture reads one readout and the test asserts it
differs from the input. Neither fixture changes a weight. That fixture describes itself: "The cognitive graph produces consultative
readouts; it does not select or execute body actions." The admission stage of the [action path](action-path.md)
takes a mapping it calls `primitive_readouts`; no code at this revision passes
a frame's readouts to it.

So the phrase "cognitive tick" has, at this revision, exactly this content:
one `tanh` pass over a hand-built graph, run by a test.

## Time and randomness

ADR-0090 states: "Host wall-clock time is never implicit causal authority."
The cognition package was searched for anything that could bring host time or
unseeded entropy into state (pattern over `organism:src/organism/cognition`
for `time`, `datetime`, `uuid`, `secrets`, `urandom`, `perf_counter`,
`monotonic`, `os.environ`, `hash(`, `id(` and `random`, 2026-10-09).

The result: no module reads a clock. One module imports `random`, and only to
type an argument: the function that names a new concept node takes a
`random.Random` from its caller and draws 64 bits from it, and the same seed
gives the same name (`test_propose_concept_is_deterministic_for_the_same_seed`).
No module creates a generator of its own.

Hash randomisation of strings is a host-dependent source that a search for
names does not show. A scripted run of the generative part of the package
(thirty-nine steps, reconciliations, a replay and a recombination) was executed
under two values of `PYTHONHASHSEED` and produced byte-identical saved state.
That is one scenario, not a proof.

This is a description of what was searched and found. Whether it satisfies
the decision is not ruled on here.

## Names that point outside the repository

Several docstrings in the package refer to things that are not in it. The
node and edge catalogues and the ceilings cite sections of a "master doc"; the
normalizer cites `AdaptiveSenseModel`, `SelfModel` and a file `CLAUDE.md`; the
checkpoint codec cites `CognitiveBridge` and `WeightStabilityTracker`; the
generative package cites a `StructuralContention` owner (search of
`organism:src` for each name, 2026-10-09: none is defined). They are traces of
where the code came from and should not be read as descriptions of this
repository. One small mismatch of the same kind: the pattern for node
identifiers permits a colon, and the error message printed on refusal shows a
pattern without one (confirmed by a run). Recorded as finding F-0077.

## At each lifecycle boundary

| Boundary | What happens | Support |
|---|---|---|
| Birth | The packaged graph is empty and the initial state has no tick and no values | Code and tests |
| Checkpoint | State is saved exactly; the graph is saved with weights rounded to 17 levels and without `eligibility` | Code, tests and a run; see [the cognitive checkpoint](cognitive-checkpoint.md) |
| Restart | Nothing in the package restarts anything; decoding returns a state and a graph | Code and tests |
| Re-embodiment | No operation exists. Sense nodes are named by strings the caller chooses; nothing rebinds or invalidates them | Absence in the code (search for `reembod` and `rebind` in `organism:src/organism/cognition`, 2026-10-09); that cognition is not silently reset is [ADR-0081](../../technical/adr/ADR-0081-the-canonical-organism-is-longitudinal.md), a statement of intent |
| Reproduction | No operation copies a graph to an offspring; the loader always returns the empty graph | Code and `test_base_graph_is_a_true_tabula_rasa` |

## What supports this description

| Claim | Support |
|---|---|
| Construction rules and ceilings | Code and tests in `organism:tests/source_unit/cognition/test_graph.py`, `test_limits.py`, `test_types.py` |
| The arithmetic of one pass, delays, gating | Code and tests in `test_graph.py` |
| Node kinds other than sense and readout, and edge kinds other than gating, are computed identically; `tau` is a divisor; the tick does not enter the arithmetic | Code, and one ad hoc run of the module at that revision; no test is kept for these |
| Edge objects are shared between graphs and can be changed after validation | Code, and the same ad hoc run |
| Transition: explicit increasing tick, sense-only finite signals, prior state untouched on refusal | Code and tests in `test_transition.py` |
| Ticks may skip; stray previous values are accepted; a missing signal is zero | Code, and the same ad hoc run |
| Normalizer behaviour | Code and tests in `test_activation.py` |
| The packaged graph is empty | The file, and tests in `test_birth.py` |
| Nothing in the source calls the transition, the loader or the normalizer | Searches of `organism:src` on 2026-10-09, named in the text |
| Use inside a World tick | Two test fixtures in the World repository; they are fixtures, not a composed Organism |
| No host time, no unseeded randomness | Search named in the text, and one scripted run under two hash seeds |
| What time authority and continuity must mean | Accepted decisions ADR-0090, ADR-0081, ADR-0092, ADR-0105; statements of intent, not test results |

No run of an Organism whose graph was grown from the empty graph was examined,
because no component at this revision can produce one.

## Open questions

- What is meant to add the first sense node to an empty graph, and in which
  repository that step belongs.
- Whether the six node kinds and four edge kinds are meant to differ in
  activation, or only as labels read by other mechanisms.
- Whether a graph is meant to be safe to keep after a structural change, and
  if so whether edges should be copied.
- Whether a skipped tick should be distinguishable from an adjacent one.
