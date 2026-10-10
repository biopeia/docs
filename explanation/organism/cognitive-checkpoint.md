# What a cognitive checkpoint carries

Reviewed against `organism` at commit `6543188ff302a5f2dc8002c0086252d6061e5310`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run, or an accepted decision.

## What it is

[The checkpoint envelope](identity-and-checkpoint.md) carries bytes it does
not understand. This document is about the one thing at this revision that
fills it: a composition of cognitive state into those bytes, and its
restoration.

The composition is a value holding up to six things that a caller hands it.
It encodes them as one JSON document and can rebuild them from it. It does not
find the state to save; it saves what it is given. Its own description draws
the boundary twice: "This payload includes only explicitly supplied cognitive
state." and "This is not a complete Organism checkpoint."

Two properties decide what such a checkpoint is worth, and both are easy to
miss from the names:

- **It is not exact.** A restored graph is a rounded version of the saved one
  and computes different numbers.
- **It is not complete.** Several kinds of state that the package's own
  mechanisms keep have no place in it.

Both are described below with what was run to confirm them.

## The six parts

`organism:src/organism/cognition/portable_checkpoint.py::CognitiveRuntimeCheckpoint`:

| Part | Required | What is written |
|---|---|---|
| Transition state | yes | Identity, last tick, previous frame's values, exactly |
| Graph | yes | Nodes exactly; edges with the weight replaced by a class number |
| Experience records | no, default none | Each record's canonical form |
| Safety state | no | A failure count and a flag |
| Sensory normalizers | no | Mean, variance and count, for established normalizers only |
| Generative resident | no | The resident's own export |

The document has exactly nine top-level fields: those six, the identity, a
schema name and a schema version, which is 4. Encoding is deterministic: keys
sorted, no optional whitespace.

Constructing the value already checks that the parts belong together: every
experience record and the resident must carry the same identity as the
transition state, and record identifiers must be unique
(`test_cognitive_checkpoint_rejects_experience_from_another_identity`,
`test_cognitive_checkpoint_rejects_duplicate_experience_record_identity`,
`test_portable_checkpoint_rejects_generative_state_for_another_organism`).

The graph itself carries no identity. Nothing checks that a graph belongs to
the Organism it is saved with.

## Restoring

Decoding is strict about shape and returns the six parts
(`test_cognitive_graph_and_recurrent_state_round_trip_through_organism_envelope`).
It refuses any other set of top-level fields, any other schema name or
version, a missing graph, and an identity that differs between the document
and the transition state inside it
(`test_cognitive_checkpoint_rejects_unknown_fields`,
`test_portable_checkpoint_schema_v3_is_not_accepted_as_a_current_payload`,
`test_cognitive_checkpoint_rejects_identity_mismatch`). Earlier versions are
refused, not migrated.

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

## Not exact: the graph comes back rounded

Edge weights are real numbers in [-2, 2]. A checkpoint stores each as one of
17 classes: zero, and eight magnitudes on each side (0.03125, 0.0625, 0.125,
0.25, 0.5, 0.75, 1.25, 2.0). Anything within 0.01 of zero becomes zero; any
other weight becomes the nearest magnitude. The `eligibility` trace of every
edge is not written and is restored as zero, which the code marks: "labile:
never restored from a checkpoint".

This is deliberate, and the reason given in the code is not compactness. A
docstring says of exported learned state that it "must guard against
differencing attacks", and a test pins the
property: two exports either side of a tiny weight change are identical
(`test_two_consecutive_checkpoints_cannot_be_differenced_to_recover_exact_weight`).
Another pins that a small weight does not vanish
(`test_tentative_weight_does_not_collapse_to_zero_in_codec_v3`), and a third
that the round trip is approximate
(`test_weight_survives_quantized_round_trip_approximately`).

The consequence was measured by running the module: a graph of one edge was
advanced, saved, restored, and both the live and the restored copy were
advanced one more tick on the same input.

| Weight before | Weight after restore | Next readout, live | Next readout, restored |
|---|---|---|---|
| 0.4 | 0.5 | 0.1974 | 0.2449 |
| 1.0 | 0.75 | 0.4621 | 0.3584 |
| 0.009 | 0.0 | 0.0045 | 0.0000 |
| 0.05 | 0.0625 | 0.0250 | 0.0312 |
| -1.7 | -2.0 | -0.6911 | -0.7616 |

Saving a restored checkpoint again gives the same bytes, so the loss happens
once. The transition state survives exactly; the test in the World repository
that restores this payload after a committed tick compares the state and does
not compare the graph.

Two things follow, stated as facts and not as judgments.

A run that is stopped and resumed from a checkpoint does not continue as the
uninterrupted run would have. The graph it resumes with differs, by up to 25
per cent in a weight in the cases above, and a weight under 0.01 is gone.

[ADR-0081](../../technical/adr/ADR-0081-the-canonical-organism-is-longitudinal.md)
says that canonical re-embodiment "preserves same-Organism continuity and
does not silently reset cognition", and
[ADR-0103](../../technical/adr/ADR-0103-portable-organism-state.md) that
"Private learned state belongs to Organism longitudinal continuity". Beside
them stands a codec that rounds learned weights by design, for a stated
reason. Whether rounding is a reset, and whether the reason outweighs exact
continuation, is for the owners of those decisions. It is recorded as finding
F-0073.

The export function can take a table of weight classes to write in place of
rounding the live weights. Its docstring attributes that table to a
`WeightStabilityTracker` and says a `CognitiveBridge` "always passes a
complete override map". Neither exists in this repository, and the
composition calls the export without the table (search of `organism:src` for
both names, 2026-10-09).

## Not complete: what has no place in it

Read from the code; each absence was confirmed by inspecting an encoded
payload or by a restore.

| State | Where it lives | In the checkpoint |
|---|---|---|
| Co-activation counts, association counts, cooldowns | `StructuralPlasticity` in [graph plasticity](graph-plasticity.md) | No. The class has its own export and restore; the composition has no field for them |
| Shadow prediction losses and histories | the three shadow classes | No. No export exists |
| A tuned parameter's value | `MetaParameter` | No. No export exists |
| The genome | `organism:src/organism/genetics` | No. A genome export and restore sit in the same module as the graph codec and are tested there; the composition does not use them |
| The ceilings the graph was built under | `KernelLimits` | No. Supplied again at restore |
| Normalizers with fewer than five readings | the normalizer | No, by design (`test_unestablished_normalizer_is_not_exported`); the reason given is that a young mean "can equal raw readings" |
| Registered models | the resident's registry | No. A registry may be passed at restore |
| The evidence resolver | the resident | No. The code calls it "deliberately transient (never checkpointed)" |
| The resident's per-step limits | its budget | No. A restored resident has the default limits; the last workspace keeps its own. A resident built with a limit of 4 states came back with 64 |
| The count of targets dropped for lack of room | the resident | No. Restored as zero |
| Each hypothesis's count of reconciliations | the hypothesis | No, in this export. Restored as zero |
| Experience records not handed over | an experience ledger | Only what the caller passes |

The repository says the same in general terms about each addition to the
payload. Of the resident's state: "It does not establish that all Organism
callers include it, that model-weight/dependency closure is portable, that a
complete Organism continuation is captured". Of the safety and normalizer
state, that it "does not prove a complete cognitive or Organism continuation".

One restore changes later behaviour without changing any saved number. The
use tracker discards its oldest-inserted token when full. Its export writes
tokens in sorted order, so after a restore the oldest is whichever
sorts first. A full tracker and its restored copy, given the same new
token, discarded different entries (ad hoc run). Recorded with the other
restore differences as finding F-0076.

## Who calls it

Nothing in `organism:src` constructs a `CognitiveRuntimeCheckpoint` (search,
2026-10-09). It is constructed by this repository's tests and by one
integration test in the World repository,
`world:tests/integration/test_durable_checkpoint_restore_slice.py`, where a
fixture wraps it in an envelope, writes the bytes to a file and hands World a
reference to them. That fixture passes only the two required parts.

So no code at this revision decides which of the optional parts a real
Organism would include. The composition is a container with a tested shape;
what goes into it in practice is not yet written.

## What supports this description

| Claim | Support |
|---|---|
| The six parts, the nine fields, identity checks at construction | Code and tests in `organism:tests/source_unit/cognition/test_portable_checkpoint.py` |
| Strict decoding, version refusal, closure check through the envelope | Code and the same tests |
| The weight codec, the dropped trace, safety and normalizer export | Code and tests in `test_graph_checkpoint.py` |
| Restored weights and the readouts they give; idempotence of a second save; refusal under smaller ceilings | Code, and one ad hoc run of the module at that revision |
| What is absent from the payload; budget, counters and eviction order after restore | Code, an inspected payload and the same ad hoc run |
| The limits the repository states about itself | `organism:MIGRATION.md` |
| Nothing in the source constructs the composition | Search of `organism:src` on 2026-10-09 |
| What continuity and portability must mean | Accepted decisions ADR-0081, ADR-0092, ADR-0103; statements of intent, not test results |

No checkpoint written by a running Organism was examined, because no
component at this revision writes one outside tests.

## Open questions

- Whether a resumed Organism is meant to continue exactly, and if not, how
  much divergence from the uninterrupted run is acceptable.
- What threat the rounding answers at this revision, given that the envelope
  carries the payload in the clear to whoever holds it.
- Which component decides what a complete cognitive payload is, so that
  "supplied" can be compared with "required".
- Whether structural counts, the genome and the resident's limits belong in
  this payload or in sibling payloads of the same envelope.
