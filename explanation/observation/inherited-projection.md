# The inherited projection

Reviewed against `observation` at commit `6aac3c76684834722440f53c9d8604ac4c16b138`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run of the module made at that
revision on 2026-10-11, or an accepted decision. A decision is intent, not a
result.

## What it is

Before the `observation` repository had a
[claim model](semantic-claim-model.md) or a [plane](observation-plane.md), it
received two pieces copied from the source repository: a function that turns
one flat record of telemetry into body and vitals records, with a cognition
record when recognized cognition data is present, and a data class for a
composed frame. They are still there, and they are the only part of the
repository that other Biopeia code calls today.

They are best understood as a transitional filter. The function takes a mapping that some
caller has assembled about one tick, picks out the keys it knows, tidies
their types, and returns body and vitals events plus a cognition event only
when recognized cognition data is present. It does not read any domain, hold
any state or deliver anything. Whatever the result means, it means because
of what the caller put in.

The names of those keys and event headings were inherited. The
repository's README says: "this is not a compatibility promise or a ratified
Biopeia API". This document describes the operations performed and treats
the names as copied labels.

## Records projected from one mapping

`observation:src/observation/projection.py::runtime_tick_events` accepts a
mapping and returns body and vitals dictionaries, plus a cognition dictionary
only when at least one recognized cognition field is present. Anything that
is not a mapping is refused
(`test_projection_does_not_invent_observations_and_rejects_non_mapping`).

Each record begins with up to four keys copied from the input when present:
`source`, `instance_id`, `run_id` (as text) and `sequence` (as an integer).
Here `sequence` is whatever the caller supplied; it is unrelated to the
delivery sequence of the plane.

For each record, the function recognizes the following keys and copies those
present and convertible:

- **body**: `tick`, `body_kind`, a base position and orientation, a resource
  position, a list of joints (name and position), a list of links (name,
  position and orientation) and four contact counts;
- **cognition, when emitted**: `tick`, and about thirty counters and scalars
  with names such as
  `schema_confidence`, `predictor_count` and `motor_primitives`, plus a few
  values passed through as they are, such as `prediction_error`;
- **vitals**: `tick`, `alive`, ages, distances and progress relative to a
  resource, `resource_remaining`, displacement, and several quantities of
  work in joules.

Nothing in this repository computes or interprets any of them. A name such
as `schema_confidence` is a key that is copied when a caller supplies it. It
is not evidence that any Organism holds a quantity of that meaning.

One inherited key has been removed. Up to `observation`
`be82907d1d677b2362e369d15eb1e8e964d893aa` the cognition and vitals records
also copied a second tick under the name `symbiont_tick`, a name that
predates
[ADR-0085](../../technical/adr/ADR-0085-project-identity-is-biopeia-and-the-individual-is-organism.md),
under which the individual is called Organism. The function no longer reads
that key. Supplying it has no effect, and it is not taken as another name
for `tick`, including when both are given with different values
(`test_projection_does_not_emit_or_alias_symbiont_tick`). The repository adds
that the remaining `tick` "does not by itself assert World causal time,
Organism progression, or any other domain-time semantics".

## The rule it follows: absent stays absent

The function's stated purpose is to "Project one canonical runtime tick
without fabricating absent observations." A key that is missing from the
input is missing from the output. Given only a tick number, the result contains body and vitals records, but no
cognition event; identity/tick context alone is not a cognition observation
(`test_projection_does_not_invent_observations_and_rejects_non_mapping`,
`test_projection_emits_cognition_only_when_cognition_data_is_present`). The
input is not modified
(`test_runtime_tick_projection_is_mapping_only_and_does_not_mutate_source`).

The same rule is applied to values the function cannot convert: a number
that cannot be read as a number is dropped without an error, as is a link
whose position does not have three components or whose orientation does not
have four. Cognition is omitted when recognized cognition keys are absent or
all recognized optional values are `None`.

That has a consequence for the caller. **A key the function does not know is
dropped silently**, exactly like a key that was never there. In an ad hoc
run, an input with `world_record_id` and an unknown key produced records
with neither, and no error or warning.

## Two keys left out on purpose

The source accepted two inputs about an energy reserve,
`metabolic_reserve` and `metabolic_reserve_ratio`. This repository's version
emits neither. A comment in the code says "These source telemetry keys have
distinct, unresolved meanings.", and the migration record adds that "They
are not interchangeable and no target semantic-family contract currently
authorizes either projection". The omission is tested for each key alone and
for both together
(`test_projection_omits_unratified_metabolic_reserve_semantics`).

## What the tidying does to values

Confirmed by ad hoc runs, and not covered by tests except where named:

- Text that reads as a number becomes a number: a tick given as the text `12` and
  a joint position given as the text `0.5` are converted
  (`test_runtime_tick_projection_is_mapping_only_and_does_not_mutate_source`).
- An integer key truncates: a tick of `3.9` becomes `3`. A boolean tick
  becomes `1` or `0`.
- A not-a-number value passes through unchanged for the floating-point keys.
- Boolean keys such as `alive` are copied only when the input is exactly a
  boolean; `1` is dropped.
- A few cognition keys, `prediction_error` among them, are passed through
  with no conversion at all. The output holds the caller's own object.
- An empty list of joints is kept as an empty list; an empty list of links
  is dropped. A base position of two components is kept, while a resource
  position must have exactly three.

## The frame

`observation:src/observation/contracts.py::ObservedFrame` is a frozen record
with a tick, a source, a run identifier, an optional organism identifier,
optional `body`, `cognition` and `vitals` mappings, a required `mind`
mapping, and optional instance, body and embodiment identifiers and a
topology revision.

Its one method, `as_event`, returns a dictionary of type `observed_frame`
with those fields and a fixed `provenance` block: an owner of `observer`,
three constant labels naming a projection and two contracts, and
`feeds_back` set to false
(`test_observed_frame_emits_explicit_passive_projection_provenance`). The
optional identity fields appear only when set.

Three things should be read carefully:

- `feeds_back: False` is a constant written into every event. It is a label.
  It is not a measurement, and no test examines whether anything flows back.
- The contract names are text constants. No contract with those names is
  defined in any Biopeia repository.
- The frame requires a `mind` mapping, but the function that built one in
  the source was deliberately not copied; the migration record gives the
  reason that it "imports Lab's Atlas implementation". Nothing in Biopeia
  produces that mapping.

The copies made by `as_event` are one level deep; nested values are shared
with the frame (ad hoc run). An empty run identifier is accepted (ad hoc
run), although the class documentation says that a frame "without run
identity cannot be safely composed with presentation state from an earlier
run".

No use of `ObservedFrame` was found in any other repository.

## Who calls the projection today

Two callers were found by a search of the seven repositories at their heads
on 2026-10-11. Both pin
`observation@be82907d1d677b2362e369d15eb1e8e964d893aa`, two commits behind
the revision reviewed here. Between the two, the one change to the
projection is that `symbiont_tick` is no longer copied; the frame is
unchanged. Neither caller supplies that key, so each gets back the same
records at its pin and at the head.

- **Lab**, in source code: the operator material transfer
  (`lab:src/lab/interventions/material_transfer.py`, at
  `lab@29e25d85e796d96a3f2e830fd870a2f74e8e2266`) calls the function after
  the World cut has been committed and returns the records as the
  `observations` of its result. It passes a source label, an instance, a
  sequence, a tick, a body-kind label and `resource_remaining`. It gets two
  records back, body and vitals, and no cognition record (ad hoc run at the
  heads). Lab's integration test checks those two tags, that none is
  cognition, and that no record carries a run identifier.
- **World**, in an integration test only
  (`world:tests/integration/test_first_biopeia_causal_tick.py`, at
  `world@95f5064c6b06bd66bb58a72110b066afe4ca70b0`), likewise after the
  commit. It passes a source label, an instance, a run identifier, a
  sequence, a tick, a body-kind label, `body_age_ticks` and one cognition
  counter, `cognitive_readouts`, and so gets three records.

Neither caller passes `metabolic_reserve_ratio` any longer, and the World
test no longer passes `world_record_id`; at the revisions first documented
both did, and the projection discarded them. Every key the two callers pass
today is one the function knows. In both callers the mapping is assembled by
hand from values of several owners: a resource's remaining quantity, a
body's age, a causal tick.

## Set beside the claim model

The two halves of this repository describe observations in different ways,
and the difference is the reason the projection is transitional.

The [claim model](semantic-claim-model.md) gives every claim one authority,
one subject, an epistemic kind and a typed domain time. The projection's
records have none of these. One `vitals` record can hold a body's age, a
resource's remaining quantity and work in joules together, under one `tick`
of unstated domain. The Observation Semantic Model v1 says that claims "with
different authorities, epistemic bases, subjects/scopes, or effective
times/revisions remain independent even if they are delivered together".

The repository's migration record classes the frame as to be rewritten and
keeps the function as a bounded extraction whose payload keys "are not
compatibility promises".

The
[Observation Architecture for Biopeia v1](../../technical/design/observation/observation-architecture-biopeia-v1.md)
decided the matter in its point P8: "The projection carried over from the
source repository is not kept for compatibility and does not become a stable
contract by existing." It is to be deferred "while it has necessary
consumers" and dropped "once a TARGET semantic family covers its function".
That design also observed that "the code does not yet mark it as
transitional".

At the revision reviewed: the function and the frame are exported from the
top of the package beside the plane; neither carries a marker of being
transitional in code; the README and the migration record state the limit in
prose; two callers exist; and no semantic family exists that could replace
it. Whether the two callers are *necessary* consumers in the sense of P8 is
not something this documentation decides.

## What supports this description

| Claim | Support |
|---|---|
| Body/vitals emission, conditional cognition emission, absence preservation, input non-mutation, non-mapping refusal, reserve-key omission, `symbiont_tick` neither emitted nor aliased, and frame provenance | Code and tests in `observation:tests/test_projection.py` at the reviewed revision; the file's 11 cases passed in an ad hoc run |
| Unknown keys dropped silently; numeric coercion; treatment of malformed lists; shallow nested copies in `ObservedFrame.as_event`; empty run identifier accepted | Code, and ad hoc runs of the module at the reviewed revision |
| The two callers and what they pass; no use of the frame | Text search of the seven repositories at their heads on 2026-10-11, and reading of `lab` and `world` at the commits named above; both pin `observation@be82907`, which differs from the reviewed revision in these two modules only by the removed `symbiont_tick` copy |
| Origin of the code and the reasons for what was left out | The repository's `MIGRATION.md`, a record of provenance and intent |
| That the projection is transitional | The approved design, point P8: a decision, not a property of the code |

No run-time trace of the projection in a live system was examined.

## Open questions

- Which semantic family is to cover what Lab's material transfer reports,
  so that P8's condition for dropping the projection can be met.
- Whether the callers should be told when a key they supply is discarded.
- Whether `ObservedFrame`, which has no caller and needs an input nothing
  produces, is covered by the same deferral or can be dropped now.
