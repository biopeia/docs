# From an opaque sense signal to an accepted step

Reviewed against `organism@637bc21a7e2a1aa9e0870f55f134e839657687f4`,
`world@d66ac6197c8ea8489dc4f2689641ff0a88b6482a` and
`modality@62af4aba07146d5dfdc978af07bb72111112d873` (main on 2026-10-16); first written against `ba001179`.
Everything below describes those revisions. Statements are marked by what
supports them: the code, the tests, an ad hoc run, or an accepted decision.
Searches of the seven repositories were made on 2026-10-11.

## What it is

Earlier revisions of the Organism repository held a graph transition, a set
of weight-update functions, a checkpoint composition and nothing that called
them in sequence. Three modules now do. Read from the inside out:

1. **Sense input** (`organism:src/organism/cognition/sense_input.py`) checks a
   set of numeric signals against a declared binding and turns them into the
   mapping of numbers that the graph transition takes.
2. **Composition** (`organism:src/organism/cognition/composition.py`) runs the
   graph transition on a copy of the graph, computes the comparison the code
   calls prediction error, and applies a weight update to the edges a caller
   names, with the parameters the caller gives.
3. **Owner transition**
   (`organism:src/organism/cognition/owner_transition.py`) restores the
   cognitive payload from the envelope of an
   [Organism transition state](transition-and-continuation.md), runs the
   composition, writes the result into a new envelope and has it accepted as
   one step.

The result is one function,
`organism:src/organism/cognition/owner_transition.py::advance_organism_from_sense_signals`,
that goes from signals to a next transition state whose counter is one
higher.

What this is not is stated by the modules themselves, and the rest of this
document keeps to it. The composition module: "This composes opaque sensory
activation and optional, explicitly configured edge plasticity. It does not
create graph structure, invent learning parameters, publish actions, or claim
to be a complete Organism transition." The owner transition module: "This
operation composes the already-declared cognitive graph state only. It does
not compose agency, generative cognition, motor intent, or a complete
Organism dependency closure."

**Nothing in the source of any repository calls the function.** It is called
by one test file in the Organism repository. It is a tested path from signal
to checkpoint, not a running Organism.

## A signal and its binding

A signal (`organism:src/organism/cognition/sense_input.py::OpaqueSenseSignal`)
is one number with eight labels: a channel identifier, a receptor identifier,
a provenance record, and four fields naming a contract. Its constructor
refuses a boolean, a non-finite number and any value outside [0, 1], and
refuses any contract other than one: identifier
`biopeia.modality.dimensionless-scalar-field-identity`, revision 1, quantity
kind `dimensionless_scalar_field`, unit `1`
(`test_invalid_scalar_values_fail_closed`,
`test_incompatible_semantic_contract_is_rejected`). So at this revision
exactly one kind of signal can enter by this path.

Those four constants are written out in the Organism module. The Modality
repository defines the same four values on its own class
(`modality:src/modality/scalar_field.py::DimensionlessScalarFieldIdentityV1`).
The Organism package does not import Modality (search of `organism:src` for
imports of the other six packages, 2026-10-11: none). The two definitions
agree because they were written to agree. The World integration test below
fills a signal from the Modality class and the Organism constructor accepts
it; that test is what holds them together. Recorded as finding F-0145.

The provenance record
(`organism:src/organism/cognition/sense_input.py::SenseProvenance`) is ten
values: a World identifier and causal tick, a physical step identifier, an
environment identifier and revision, a sample frame and position, and a body
identifier, embodiment episode identifier and morphology revision. Its
docstring fixes what they are: "These identifiers are correlation data, not
claims that Organism owns or independently verifies the referenced World,
Environment, or Body state."

A binding
(`organism:src/organism/cognition/sense_input.py::SenseChannelBinding`) names
a channel, a receptor and one node of kind sense in the graph.

`organism:src/organism/cognition/sense_input.py::bind_opaque_sense_signals`
takes a graph, bindings, signals and the provenance the caller expects, and
returns a mapping from sense node to number. It refuses, each with a test in
`organism:tests/source_unit/cognition/test_sense_input.py`:

- a binding to a node that is absent or not of kind sense, and a set of
  bindings that does not cover exactly the graph's sense nodes
  (`test_unbound_sense_node_and_non_sense_binding_target_are_rejected`);
- a signal on a channel with no binding, and a repeated channel
  (`test_unconfigured_or_duplicate_channels_are_rejected`);
- a signal whose receptor differs from the binding's
  (`test_channel_binding_rejects_mismatched_stable_receptor_identity`);
- a signal whose provenance is not equal, field for field, to the expected
  one (`test_stale_or_mismatched_source_provenance_is_rejected`);
- a bound channel with no signal
  (`test_missing_signal_is_not_silently_converted_to_zero`).

The last is a change in behaviour worth stating beside
[the graph document](cognitive-graph.md#the-transition): the bare graph
transition still treats a sense node with no number as zero. This path does
not, because it refuses before the transition runs. The result does not
depend on the order of the signals
(`test_opaque_signals_bind_by_stable_channel_identity_not_collection_order`).

What the check is, and is not, in the module's words: it "detects stale or
mismatched material, but is not authentication and does not make Organism
authoritative over those owners." The expected provenance is an argument.
The function compares two values it was handed.

The signal's number is passed through unchanged. The
[sensory normalizer](cognitive-graph.md#the-normalizer) is not applied on
this path: in an ad hoc run a normalizer stored in the payload for the bound
sense node had the same sample count after two steps as before them.

The module also offers
`organism:src/organism/cognition/sense_input.py::advance_cognition_from_sense_signals`,
which binds and then calls the bare graph transition, with no composition and
no checkpoint. The World test below uses that one.

## The composition

`organism:src/organism/cognition/composition.py::compose_cognition_transition`
takes a transition state, a graph, the mapping of numbers, a tick, and a
tuple of learning instructions that is empty by default. It works on a copy
of the graph, so that the caller's graph is unchanged whether the call
succeeds or fails
(`test_invalid_signal_or_learning_instruction_does_not_mutate_prior_graph`,
`test_explicit_plasticity_updates_only_candidate_graph`). The copy is a
field-by-field copy of every node and edge; this is the one place in the
package that does not share edge objects between graphs (compare
[the graph document](cognitive-graph.md#immutable-means-the-table-not-the-numbers)).

It then does three things in order and reports each as a stage with a status.

**Activation.** One call to the
[graph transition](cognitive-graph.md#the-transition). Always executed.

**Prediction error.** If the graph has a node of kind predictor, the
comparison described in
[how the graph is changed](graph-plasticity.md#changing-a-weight) is computed
from the new frame and the previous one. The status is `executed` when there
is at least one result, `waiting_for_history` when there are predictors and
no result (the first step, when there is no previous frame), and
`not_applicable` when there is no predictor
(`test_composition_executes_opaque_sense_graph_and_reports_inapplicable_stages`,
`test_composition_computes_predictor_errors_after_activation`). The results
are returned. **They are not used.** Nothing in the function passes an error
to the update that follows.

**Plasticity.** For each learning instruction, the named edge's eligibility
trace is updated and then the Oja update is applied. An instruction
(`organism:src/organism/cognition/composition.py::EdgeLearningInstruction`)
names one edge by source, target and kind
(`test_learning_selects_parallel_edge_by_kind`) and carries a learning rate,
a number called modulation, a decay for the trace, and two booleans,
`eligible` and `frozen`. With no instructions the status is `not_applicable`
and no weight moves.

Every number that decides whether and how far a weight moves comes from the
caller, in the instruction. The class says so: "Explicit per-edge learning
inputs; no rates or eligibility are inferred." Read from the code and
confirmed by an ad hoc run:

- The modulation is not the prediction error. A caller who wants an error to
  scale an update must compute that and put it in the instruction; no code
  does.
- `eligible` is the caller's boolean. The trace is updated and saved, and the
  update does not read it
  (`test_learning_without_action_linked_eligibility_does_not_change_weight`
  passes `eligible` as false and checks that the weight is unchanged).
- The edge's `plasticity` field, the genome and the
  [expression state](genome-and-inheritance.md) are not read. The learning
  rate is whatever the instruction says.
- The safety state is not read. In the run, a payload whose safety state was
  frozen was advanced with one learning instruction and the weight changed.
  `frozen` on the instruction is a separate boolean supplied by the caller.
- The graph's structure is never changed. No function of
  [structural plasticity](graph-plasticity.md#changing-the-structure) is
  called.

So the open question that the plasticity document used to carry, which
component calls the weight functions, has a narrow answer: this one does,
for the edges and with the parameters some caller chooses, and no caller in
source chooses any. No function in source constructs a learning instruction
(search of the seven repositories for `EdgeLearningInstruction`, 2026-10-11:
defined, re-exported, named in a signature of the owner transition, and
constructed only in `organism:tests/source_unit/cognition/test_composition.py`).
Recorded as finding F-0142.

`organism:src/organism/cognition/composition.py::compose_cognition_from_sense_signals`
binds signals and then composes, in one call.

## The accepted step

`organism:src/organism/cognition/owner_transition.py::advance_organism_from_sense_signals`
takes a current transition state, bindings, signals, the expected provenance,
the graph ceilings, and optionally a dependency reader, a model registry, a
software version and learning instructions. In order, read from the code:

1. It refuses unless the lifecycle is `ACTIVE` and the state has an
   embodiment reference.
2. It refuses unless the body identifier, episode identifier and morphology
   revision in the expected provenance equal those of the state's embodiment
   reference (`test_wrong_embodiment_context_is_rejected_before_cognition`).
3. If the state is correlated with the same World, it refuses a tick that is
   not greater than the recorded one
   (`test_stale_world_correlation_is_rejected_without_advancing`).
4. It restores a
   [cognitive runtime checkpoint](cognitive-checkpoint.md) from the state's
   envelope, verifying declared dependencies if there are any. An envelope
   that holds anything else is refused
   (`test_invalid_or_non_cognition_owner_checkpoint_fails_closed`).
5. It binds the signals and composes one transition on the restored graph
   and state, using the provenance's causal tick as the tick.
6. It builds the next payload from the restored one with the transition
   state and the graph replaced, wraps it in an envelope that declares the
   same dependencies as before, and proposes it with a World correlation
   taken from the provenance.
7. It calls the
   [step acceptance](transition-and-continuation.md#an-ordinary-step) and
   returns the accepted state together with the composition.

If any step raises, no next state exists and the current one is unchanged
(`test_mismatched_signal_is_rejected_without_publishing_or_incrementing`).
On success the counter is one higher and the new envelope restores to a
cognitive state at the provenance's tick
(`test_opaque_sense_and_cognition_are_accepted_as_one_checkpointed_step`,
`test_accepted_cognition_state_round_trips_with_transition_counter`).

### What one step carries forward, and what it leaves alone

Confirmed by an ad hoc run in which a payload holding a graph with a
predictor, a frozen safety state, one normalizer, a generative resident that
had run one step, and one declared dependency was advanced twice, at ticks 10
and 50, with one learning instruction.

| Part of the payload | After two steps |
|---|---|
| Transition state | Replaced: last tick 50, previous frame from the second pass |
| Graph | Replaced: the instructed edge's weight moved from 0.05 to 0.0537 and its trace from 0 to 0.0281; both restored exactly from the new envelope |
| Safety state, normalizers, genetic group | Byte for byte as before |
| Experience records | Byte for byte as before when `experience_policy` is None; updated deterministically when an `ExperienceRecordingPolicy` is supplied |
| Generative resident | Byte for byte as before. It is restored and written back; it is not stepped |
| Declared dependencies | The same list, copied to the new envelope |

Three consequences, stated as facts.

The step advances the graph, and optionally accumulates experience records when
an explicit `ExperienceRecordingPolicy` is passed (`organism:src/organism/cognition/owner_transition.py:106-136`).
The [generative resident](generative-resident.md), the
[action path](action-path.md), and the
[expression regulator](genome-and-inheritance.md) are not called. The frame's
readouts are returned inside the composition and no code passes them on.

The dependencies are copied, not derived. The function does not ask whether
the new payload still needs what the old envelope declared, or needs
something more. That is the same limit as the envelope's own
([declared, not required](identity-and-checkpoint.md#what-the-closure-and-the-digests-do-not-establish)),
now carried from step to step. Recorded as finding F-0143.

Ticks need not be consecutive, here as in the bare transition: the run's
second step was at tick 50 after tick 10. And the tick inside the cognitive
state is the World's causal tick. A state correlated with one World and then
offered a signal from another World with a lower tick passes the check in
step 3, which compares only within one World, and is then refused by the
graph transition, which requires its tick to increase whatever the World
(ad hoc run). The counter of accepted steps is independent of both.

### The packaged graph cannot take this path

The graph loaded at [birth](cognitive-graph.md#birth) has no nodes. Binding
requires at least one binding and requires the bindings to cover exactly the
graph's sense nodes. In an ad hoc run, an envelope holding the packaged empty
graph was offered to the function with no bindings and no signals and was
refused: "at least one explicit SENSE channel binding is required". An
Organism born from the packaged defaults therefore cannot be advanced by
this function until something gives its graph a sense node, and nothing in
source does (see [how the graph is changed](graph-plasticity.md)). Recorded
as finding F-0144.

## Who calls it

Searched in all seven repositories on 2026-10-11 for
`advance_organism_from_sense_signals`, `compose_cognition_transition`,
`compose_cognition_from_sense_signals`, `bind_opaque_sense_signals`,
`advance_cognition_from_sense_signals`, `OpaqueSenseSignal` and
`EdgeLearningInstruction`.

- **In source**, the three modules call one another as described, and the
  package re-exports the names. Nothing else in the Organism source, and no
  source in the other six repositories, calls any of them.
- **In the Organism tests**, three files:
  `organism:tests/source_unit/cognition/test_sense_input.py`,
  `organism:tests/source_unit/cognition/test_composition.py` and
  `organism:tests/source_unit/cognition/test_owner_transition.py`. Only the
  last calls the accepted step, on a graph of two nodes and one edge, without
  learning instructions.
- **In World**, one integration test,
  `world:tests/integration/sensing/test_environment_to_organism_scalar_field.py`.
  Its fixture samples an Environment scalar field at a point projected from
  an Embodiment receptor, passes the value through the Modality mapping,
  builds one signal, and calls `advance_cognition_from_sense_signals` on a
  graph of a single sense node inside a World physical step
  (`test_environment_scalar_field_reaches_organism_as_opaque_signal_and_commits`).
  It does not call the composition or the accepted step, and no
  `organism_step` exists in it. The fixture says of the cognitive result:
  "this fixture does not claim that candidate was adopted into the committed
  Organism continuation." It also describes itself as exercising "a narrow
  target contract, not scientific learning or a production sensor/solver
  adapter."

So two partial paths exist and they do not meet. From Environment to a sense
node, across four domains, inside a World step: one World test, ending at a
frame that is not kept. From a signal to an accepted, checkpointed step with
optional weight updates: Organism tests only, with signals the test writes.
Recorded as finding F-0140.

## Time and randomness

None of the three modules reads a clock or draws a random number. The tick
is the provenance's causal tick. Nothing here generates an identifier.

## What supports this description

| Claim | Support |
|---|---|
| What a signal, a provenance record and a binding are; what binding refuses | Code of `organism:src/organism/cognition/sense_input.py` and tests in `organism:tests/source_unit/cognition/test_sense_input.py` |
| The Organism and Modality constants are separate definitions with equal values | Code of both modules; search of `organism:src` for imports of other packages, 2026-10-11 |
| The three stages and their statuses; the copy of the graph; selection of an edge by kind; no update when `eligible` is false | Code of `organism:src/organism/cognition/composition.py` and tests in `organism:tests/source_unit/cognition/test_composition.py` |
| Prediction error does not enter the update; `plasticity`, the genome, the expression state and the safety state are not read; structure is not changed | Code; for the safety state also the ad hoc run below |
| The order of checks in the accepted step; failure publishes nothing; the counter and round trip; optional experience policy accumulation | Code of `organism:src/organism/cognition/owner_transition.py` and tests in `organism:tests/source_unit/cognition/test_owner_transition.py` |
| Which parts of the payload change over two steps; the learned weight and trace persist exactly; the resident is not stepped; the normalizer is not applied; dependencies are copied; a frozen safety state does not stop an update; ticks 10 and 50 accepted; a lower tick from another World refused by the graph transition; the packaged empty graph refused | Code, and one ad hoc run at `organism` `ba0011797a6a3b4d48c7731651e50560c4043f18`; no test is kept for these |
| No caller in the source of any repository; the callers in tests | Searches on 2026-10-11 of the seven repositories at the revisions in `registry/coverage.yaml` for this unit and for [the transition boundary](transition-and-continuation.md) |
| What the World test does and what it disclaims | Code of `world:tests/integration/sensing/test_environment_to_organism_scalar_field.py` |
| What the modules claim and disclaim about themselves | Their docstrings, quoted |

No run of an Organism advanced by this path over more than two steps was
examined, and none exists in the repository. Nothing here supports a
statement that an Organism senses, predicts or learns. What is supported is
that a number checked against a binding reaches a sense node, that a weight
named by a caller moves by a rule with the caller's parameters, and that the
result is saved exactly and counted as one step.

## Open questions

- Which component will call the accepted step for a running Organism, and
  where the bindings and the expected provenance will come from.
- Which component will write learning instructions, and whether the
  prediction error, the eligibility trace, the edge's `plasticity`, the
  expression state or the safety state are meant to enter them.
- Whether the readouts of an accepted step are meant to reach the action
  path, and whether the resident is meant to be stepped in the same
  transition.
- Whether the dependencies of the next envelope should be derived from the
  next payload.
- Whether the World test is meant to adopt the cognitive candidate through
  the accepted step, so that the two partial paths meet.
- What gives the packaged empty graph its first sense node.
