# What a cognitive checkpoint carries

Reviewed against `organism@de16558faeba04f05eee6d2035a8f7f1e64b822b` and
`world@e2be58700c870419a309ef3e2460b30b95c256be` (main on 2026-10-14); first written against `ba001179`.
Everything below describes those revisions. Statements are marked by what
supports them: the code, the tests, an ad hoc run, or an accepted decision.

## What it is

[The checkpoint envelope](identity-and-checkpoint.md) carries bytes it does
not understand. This document is about the one thing at this revision that
fills it: a composition of cognitive state into those bytes, and its
restoration. One layer further out, the envelope can itself be carried in a
[transition state](transition-and-continuation.md) that counts steps.

The composition is a value holding six cognitive/memory parts and, optionally,
one genetic-state group made of three parts that a caller hands it. It encodes
them as one JSON document and can rebuild them from it. It does not find the
state to save; it saves what it is given. Its own description draws the
boundary twice: "This payload includes only explicitly supplied state." and
"This is not a complete Organism checkpoint."

Two properties decide what such a checkpoint is worth:

- **It is exact for what it carries.** A restored graph has the same
  weights and traces as the saved one and computes the same numbers.
- **It is bounded and fail-closed.** It carries effective `KernelLimits`
  and rejects any external generative dependency closure fail-closed.

Both are described below with what was run to confirm them.

## The payload parts

`organism:src/organism/cognition/portable_checkpoint.py::CognitiveRuntimeCheckpoint`:

| Part | Required | What is written |
|---|---|---|
| Transition state | yes | Identity, last tick, previous frame's values, exactly |
| Graph | yes | Nodes and edges exactly, including each edge's weight and `eligibility` |
| Experience records | yes (empty list valid) | Each record's canonical form |
| Safety state | yes (explicit null valid) | A failure count and a flag |
| Sensory normalizers | yes (empty object valid) | Mean, variance and count of every normalizer supplied |
| Generative resident | yes (explicit null valid) | The resident's own export (schema v6) |
| Genetic-state group | yes (all or none null/object) | Genome, germline state and expression state |
| Dependency closure | yes (must be empty list `[]`) | External dependencies are rejected fail-closed |
| Kernel limits | yes | Serialized configuration of effective `KernelLimits` |

The document has exactly 14 required top-level fields under schema
`biopeia.organism.cognitive-runtime` version 9. Duplicate JSON keys are
strictly rejected (`_reject_duplicate_json_fields`). Encoding is
deterministic: keys sorted, no optional whitespace.

Restoration enforces that the caller provides an explicit `KernelLimits`
matching the checkpoint's recorded configuration
(`matches_checkpoint_configuration()`); any mismatch raises
`CognitiveRuntimeCheckpointError`. Furthermore, if the generative resident
declares external model registrations or factual resolvers, serialization
and restoration reject the payload fail-closed.

Constructing the value already checks that the parts belong together: every
experience record and the resident must carry the same identity as the
transition state, and record identifiers must be unique
(`test_cognitive_checkpoint_rejects_experience_from_another_identity`,
`test_cognitive_checkpoint_rejects_duplicate_experience_record_identity`,
`test_portable_checkpoint_rejects_generative_state_for_another_organism`).
Construction also checks genetic consistency against the genome; serialization
repeats that check because nested genetic values are mutable despite the frozen
outer dataclass (`test_portable_checkpoint_rejects_inconsistent_genetic_state_at_construction`,
`test_portable_checkpoint_rejects_genetic_state_mutated_after_construction`).

The graph itself carries no identity. Nothing checks that a graph belongs to
the Organism it is saved with.

## Restoring

Decoding is strict about shape and returns the supplied state parts
(`test_cognitive_graph_and_recurrent_state_round_trip_through_organism_envelope`).
It refuses any other set of top-level fields, any other schema name or
version, a missing graph, and an identity that differs between the document
and the transition state inside it
(`test_cognitive_checkpoint_rejects_unknown_fields`,
`test_portable_checkpoint_schema_v6_is_not_accepted_as_a_current_payload`,
`test_portable_checkpoint_rejects_non_integer_schema_version`,
`test_cognitive_checkpoint_rejects_identity_mismatch`). Earlier versions are
refused, not migrated: a payload written at the previously reviewed revision,
which carried version 5, cannot be read at this one.

The strictness now reaches every nested part. Each decoder requires exactly
the fields its writer emits and refuses a missing or an unknown one, where
several used to supply a default for a missing field or ignore an extra one
(`test_restore_rejects_unknown_checkpoint_fields`,
`test_safety_state_restore_rejects_unknown_fields`,
`test_normalizer_restore_rejects_invalid_or_noncanonical_entries`,
`test_cognitive_checkpoint_requires_experience_records_in_current_schema`,
`test_resident_checkpoint_requires_all_emitted_fields_and_rejects_unknowns`,
`test_workspace_restore_rejects_missing_or_unknown_emitted_fields`). The
repository keeps its own inventory of the required fields in
`organism:CHECKPOINT_DECODER_MATRIX.md`, which describes itself as "a
decoder-field inventory, not a claim that this bounded payload is the
complete Organism continuation checkpoint."

When genetic state is present, restore requires the caller to provide the
running software version; it validates/restores the genome first, then the
germline and expression against that genome
(`test_portable_checkpoint_genetic_restore_requires_explicit_running_version`,
`test_portable_checkpoint_round_trips_genome_germline_and_expression_as_one_unit`).
This is an explicit restore input, not data inferred from the checkpoint.

The restored graph is rebuilt through the ordinary constructor, so every
construction rule is applied again to what was read
(`test_restore_rejects_a_payload_that_would_violate_kernel_limits`). The
ceilings used are the ones the restoring caller passes; they are not in the
document. A checkpoint written under one set of ceilings was refused under a
smaller one (ad hoc run), with the general error "malformed cognitive runtime
checkpoint".

When the payload arrives inside an envelope that declares dependencies, a
reader must be supplied and the closure is verified first
(`test_organism_checkpoint_restore_requires_and_verifies_dependency_closure`);
the envelope document describes that check and its limits. Nothing in the
composition declares a dependency of its own.

## Exact: the graph comes back as it was

Edge weights are real numbers in [-2, 2]. The checkpoint writes each one as
the number it is, together with the edge's `eligibility` trace and its five
other fields. Restoring requires both to be floating-point numbers inside
their bounds and rebuilds the edge with them
(`test_weight_and_eligibility_round_trip_exactly`,
`test_tentative_weight_is_exact_in_codec_v4`,
`test_restore_rejects_eligibility_outside_learning_bound`). The export
refuses a live weight that has been pushed outside its range
(`test_export_rejects_mutated_invalid_edge_state`).

This reverses what the previous review of this document found. The codec was
then at version 3: it stored a weight as one of 17 classes, wrote no trace
and restored the trace as zero, and gave as its reason a guard against
"differencing attacks" on exported learned state. A weight of 0.4 came back
as 0.5 and one of 0.009 as zero. The codec is now version 4. The classes, the
rounding functions, the stated reason and the optional table of class
overrides are gone from the source, and two successive exports either side
of a small weight change now differ, which a test pins
(`test_consecutive_checkpoints_preserve_exact_live_weight_changes`). A graph
payload written by the earlier codec is refused
(`test_restore_rejects_missing_or_noncurrent_weight_codec_version`).

The consequence was measured again by running the module: a graph of one
edge was advanced, its trace set to 0.37, saved, restored, and both the live
and the restored copy were advanced one more tick on the same input.

| Weight before | Weight after restore | Trace after restore | Next readout, live and restored |
|---|---|---|---|
| 0.4 | 0.4 | 0.37 | equal |
| 1.0 | 1.0 | 0.37 | equal |
| 0.009 | 0.009 | 0.37 | equal |
| 0.05 | 0.05 | 0.37 | equal |
| -1.7 | -1.7 | 0.37 | equal |

Saving a restored checkpoint again gives the same bytes. The repository's
own test goes further than one tick: it runs the same sequence of activation
and weight updates from a live graph and from its restored copy and compares
them (`test_exact_graph_restore_preserves_identical_future_learning_transitions`).
The test in the World repository that restores this payload after a
committed tick still compares the transition state and does not compare the
graph.

What this establishes is narrow and should be read that way. A graph and a
transition state that are stopped and resumed from this payload continue as
the uninterrupted pair would have. It says nothing about state that is not
in the payload, which is the next section. The repository draws the same
line about the change: it "removes the graph codec's quantization/reset loss
only. It does not establish a complete Organism continuation, caller
completeness, full dependency closure".

[ADR-0081](../../technical/adr/ADR-0081-the-canonical-organism-is-longitudinal.md)
says that canonical re-embodiment "preserves same-Organism continuity and
does not silently reset cognition", and
[ADR-0103](../../technical/adr/ADR-0103-portable-organism-state.md) that
"Private learned state belongs to Organism longitudinal continuity". The
earlier review set a rounding codec beside those sentences and recorded the
tension as finding F-0073. The rounding half of that finding no longer
describes the code. Its other half, incompleteness, still does.

## Not complete: what has no place in it

Read from the code; each absence was confirmed by inspecting an encoded
payload or by a restore at the reviewed revision.

| State | Where it lives | In the checkpoint |
|---|---|---|
| Co-activation counts, association counts, cooldowns | `StructuralPlasticity` in [graph plasticity](graph-plasticity.md) | No. The class has its own export and restore; the composition has no field for them |
| Shadow prediction losses and histories | the three shadow classes | No. No export exists |
| A tuned parameter's value | `MetaParameter` | No. No export exists |
| Genome, germline state and expression state | `organism:src/organism/genetics` | Optional all-or-none group. Other genetic/runtime details remain outside this composition |
| The ceilings the graph was built under | `KernelLimits` | No. Supplied again at restore |
| Registered models | the resident's registry | No. A registry may be passed at restore |
| The evidence resolver | the resident | No. The code calls it "deliberately transient (never checkpointed)". A restored resident has none, and a reconciliation attempted on it changed nothing (ad hoc run) |
| The count of targets dropped for lack of room | the resident | No. A resident whose count was 7 came back with 0 (ad hoc run) |
| Experience records not handed over | an experience ledger | Only what the caller passes |
| The step counter, lifecycle, body reference and World correlation of the Organism | the [transition state](transition-and-continuation.md) | No, and by design: they live one layer out, around the envelope that carries this payload |
| State of the agency and actuation code | their own tables | No. The composition has no field for any of them; see [the executive outcome ledger](executive-outcome-ledger.md) for one |

Four rows of the earlier version of this table are gone, because the state
they named is now saved:

- **Normalizers with fewer than five readings** are written like any other
  (`test_unestablished_normalizer_state_is_preserved_for_continuation`,
  `test_portable_checkpoint_preserves_unestablished_normalizer_continuation`;
  a normalizer with one reading was exported in an ad hoc run).
- **The resident's per-step limits** are written and restored. A resident
  built with a limit of 4 states came back with 4, where it used to come back
  with the default of 64; a restore that is also handed a different budget
  is refused
  (`test_resident_checkpoint_preserves_effective_budget_and_rejects_conflicting_override`).
- **Each hypothesis's count of reconciliations** is written and restored
  (`test_resident_checkpoint_preserves_hypothesis_reconciliation_history_exactly`).
- **The use tracker's order of insertion**, which decides what it discards
  when full, is written beside its sorted rows. A full tracker and its
  restored copy, given the same new token, discarded the same entry, the
  oldest inserted and not the first in sorted order (ad hoc run;
  `test_generative_use_checkpoint_preserves_representation_eviction_order`).
  The earlier review found the two discarding different entries and recorded
  it in finding F-0076; that part of the finding no longer describes the
  code.

The repository says the same in general terms about each addition to the
payload. Of the resident's state: "It does not establish that all Organism
callers include it, that model-weight/dependency closure is portable, that a
complete Organism continuation is captured". Of the safety and normalizer
state, that it "does not prove a complete cognitive or Organism continuation".
And of the set of stricter decoders as a whole: "this is a bounded set of
component codecs, not a complete Organism-owned continuation or proof that
every private state component is assembled by callers."

## Who calls it

At the earlier revision nothing in `organism:src` constructed a
`CognitiveRuntimeCheckpoint`. One function now does (search of the seven
repositories, 2026-10-11). The
[accepted step](sense-to-checkpoint-transition.md#the-accepted-step) restores
the composition from the envelope of a transition state, replaces its
transition state and its graph with the result of one composed pass, and
writes the composition back into a new envelope. Every other part is written
back as it was read. That function has no caller in the source of any
repository; it is run by
`organism:tests/source_unit/cognition/test_owner_transition.py`.

The composition is otherwise constructed by this repository's tests and by
one integration test in the World repository,
`world:tests/integration/test_durable_checkpoint_restore_slice.py`, where a
fixture wraps it in an envelope, writes the bytes to a file and hands World a
reference to them. That fixture passes only the two required parts.

So one function in source now carries a payload from one step to the next,
and it preserves whatever optional parts it finds. No code decides which
optional parts a real Organism would include in the first place: the first
payload of a line is still built by whoever calls the constructor, and only
tests do. The composition is a container with a tested shape; what goes into
it in practice is not yet written. Recorded as finding F-0140.

## What supports this description

| Claim | Support |
|---|---|
| The six cognitive/memory parts, optional genetic group, 12 fields, schema version 7, identity and genetic consistency checks | Code and tests in `organism:tests/source_unit/cognition/test_portable_checkpoint.py`; the field count and versions also by an inspected payload |
| Strict decoding at every level, version refusal, closure check through the envelope | Code, the same tests, tests in `test_graph_checkpoint.py`, `test_generative_cognition_persistence.py` and `organism:tests/source_unit/cognition/test_generative_resident.py`, and the repository's `organism:CHECKPOINT_DECODER_MATRIX.md` |
| Exact weight and trace, refusal of the earlier codec, safety and normalizer export | Code and tests in `test_graph_checkpoint.py` |
| Restored weights, traces and readouts equal to the live ones; identical bytes on a second save; refusal under smaller ceilings | Code, and one ad hoc run of the module at `organism` `ba0011797a6a3b4d48c7731651e50560c4043f18` |
| What the codec did at the earlier revision | The previous version of this document, reviewed at `organism` `20634a7d27e8834cd65c96f8bd44087d603aebc8`, and the diff of `organism:src/organism/cognition/checkpoint.py` between the two revisions |
| What is absent from the payload; the dropped-target count and the resolver after restore; the budget, reconciliation count and eviction order now preserved | Code, an inspected payload, the tests named in the text and the same ad hoc run |
| The limits the repository states about itself | `organism:MIGRATION.md` and `organism:CHECKPOINT_DECODER_MATRIX.md` |
| One function in source constructs the composition, and nothing in source calls that function | Search of the seven repositories on 2026-10-11 |
| What continuity and portability must mean | Accepted decisions ADR-0081, ADR-0092, ADR-0103; statements of intent, not test results |

No checkpoint written by a running Organism was examined, because no
component at this revision writes one outside tests.

## Open questions

- Which component decides what a complete cognitive payload is, so that
  "supplied" can be compared with "required".
- Whether structural counts, shadow predictions and the state of the agency
  and actuation code belong in this payload or in sibling payloads of the
  same envelope.
- Whether the envelope that carries an exact copy of learned weights in the
  clear needs any protection, now that the codec no longer rounds them for a
  stated reason.
- How a payload written under an earlier schema version is meant to be
  continued, given that earlier versions are refused and not migrated.
