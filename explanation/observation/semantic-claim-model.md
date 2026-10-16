# The semantic claim model

Reviewed against `observation` at commit `572c86f8fce66a73cc3899a4a929448416f1e6bf` (main on
2026-10-16); first written against `397c0b4`. Everything below describes the
later revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run of the module, or an
accepted decision. A decision is intent, not a result.

## What it is

When one part of Biopeia says something about the state of another, several
different parties are involved and they are easy to confuse. A body pose is
*about* a body. Its meaning is defined by Embodiment. It may have been
sampled by a physics apparatus, packaged by an adapter, and shown by a
laboratory tool. If only the number travels, every later reader has to guess
which of those parties vouches for it, at what moment it held, and whether it
was read, estimated or inferred.

The semantic claim model is a set of immutable value types that make those
answers explicit fields of the value itself. It is a vocabulary, not a
mechanism: it holds no state, performs no delivery and reads nothing from any
domain. Its own module documentation says it "deliberately does not define
wire fields, serialization, events, delivery, replay, endpoints, or
transport".

The types live in `observation:src/observation/semantic.py`. Observation is
not the authority for anything they describe.
[ADR-0100](../../technical/adr/ADR-0100-observation-capability-and-evidence-custody.md)
ratifies Observation as a passive capability, "not a semantic state
authority". The model is the place where the real authority of each claim is
written down.

## A claim, and an observation of it

The model separates two things.

A **semantic claim** (`SemanticClaim`) is one assertion. It has four parts:

- a **family**, which names the authority domain, a path such as
  `body_pose`, and the contract and revision under which the value is to be
  read;
- a **subject**, saying what the claim is about;
- an **epistemic kind**, a token saying what sort of knowledge it is;
- a **value**, of any shape. The code says the model "deliberately does not
  prescribe a universal payload shape".

A **semantic observation** (`SemanticObservation`) is a claim together with
the circumstances of its making: how it was acquired, who asserts it, who
produced the representation, the domain time at which it holds, time
references of other domains given as context, identity links, lineage,
conditions on its availability or completeness, and optionally the laboratory
run it was collected in.

The authority of an observation is always that of its claim's family. Nothing
else in the observation can change it.

## Who is who

Four roles are separate fields, and none is derived from another:

| Role | Where it is recorded |
|---|---|
| Authority: the domain that defines the meaning | `SemanticFamily.authority` |
| Asserter: who backs the claim | `SemanticObservation.asserter` |
| Producer: who built this representation | `SemanticObservation.producer` |
| Measurement source: the instrument, when there is one | `AcquisitionBasis.measurement_source` |

The first test of the module builds a body pose whose authority is
Embodiment, whose measurement source is a physics apparatus, whose asserter
is the Embodiment runtime and whose producer is the laboratory, and checks
that all four survive side by side
(`test_body_pose_expresses_embodiment_measurement_without_lab_authority`). A
claim that involves no measurement leaves the measurement source empty
(`test_body_local_physiology_is_modeled_state_not_measurement`).

### The authority domains

`AuthorityDomain` has five members: Organism, Embodiment, Environment, World
and Lab. Modality is not among them; asking for it raises an error (ad hoc
run; no test covers it).

Lab is treated differently from the other four. A claim whose family names
Lab as authority must have the epistemic kind `lab_derived`, or construction
fails with the message "LAB authority is reserved for lab_derived claims"
(`test_lab_authority_requires_lab_derived_epistemic_basis`). A Lab-derived
claim can name the claims it was derived from without becoming their
authority (`test_lab_derived_claim_does_not_take_authority_over_parent`).

What that check does and does not do should be stated exactly. It compares
one token with one enumeration member. It runs in one direction only: a claim
under Embodiment authority may also carry the kind `lab_derived` (ad hoc
run). And the asserter is a free field: an observation of Embodiment
authority may name the laboratory as its asserter (ad hoc run). The model
records who is said to hold each role. It cannot know whether that is true.

## What a claim is about

A subject (`SubjectScope`) has a kind and at least one of: a local key,
identity assertions, or participants. An empty subject is refused (ad hoc
run).

Identities are not bare strings. An `IdentityRef` has a kind, a value, an
issuer and optionally a scope and a lifetime. An `IdentityAssertion` adds who
is asserting it; the code describes it as "An actor asserting an identifier
without becoming its issuer or authority." Two bodies with the same value
issued by different parties are therefore different identities.

The local key is weaker, and the code says so: it is "a local scope
descriptor, not by itself a stable subject identity". The test
`test_environment_resource_scope_does_not_require_durable_resource_entity`
uses a key for a resource at a location that has no durable identity of its
own.

Where two identities issued by different parties are believed to name the
same thing, that belief is a separate object, an `IdentityLink`, with its own
asserter and a state: asserted, conflict or unresolved. A link in conflict
does not invalidate the claim it travels with; the observation only reports
that a conflict is present
(`test_conflicting_identity_link_does_not_invalidate_independent_claim`).

The laboratory run in which an observation was collected is kept apart from
the subject (`test_run_context_remains_separate_from_source_subject_identity`).
The code calls it an "Optional Lab-run association that never substitutes
source identity."

## Time

There is no shared clock in the model. A `DomainTimeRef` names a domain, a
kind of time or revision within it, and a value.

Two tuples carry time on an observation. `domain_time` is the time at which
the claim holds, in its own authority's terms: every reference there must
name the claim's authority, or construction fails
(`test_primary_domain_time_must_match_claim_authority`). `context_time` is
for the clocks of other domains, kept as context
(`test_cross_domain_time_is_allowed_only_as_explicit_context`).

A time value may be an integer, a finite number or a text. Booleans and
non-finite numbers are refused
(`test_boolean_is_not_a_domain_time_value`,
`test_non_finite_float_is_not_a_domain_time_value`,
`test_finite_numeric_and_text_domain_time_values_remain_valid`).

The model also refuses to let delivery order pass for domain time. Three
kinds are rejected by name: `observation_sequence`, `transport_sequence` and
`delivery_sequence`
(`test_transport_sequence_cannot_be_used_as_domain_time`).

The limits of these checks, confirmed by ad hoc runs:

- The rule that primary time belongs to the claim's authority compares the
  `domain` field only. The `kind` is free. A reference can say
  domain `EMBODIMENT` with kind `world_causal_tick` and be accepted. The physical
  step integration test in the `world` repository does exactly this for the
  body pose it builds (read at `world@c162b67e698de9b47450264402677b0165e6e20e`,
  which pins `observation@cb07ace206058719a9aa9df65e2eb1f837130ee9`).
- Only those three kind names are refused. `wall_clock` and `sequence` are
  accepted as kinds.
- An observation may carry no domain time at all. Negative values are
  accepted.

## Where a claim came from

`AcquisitionBasis` records a method token and, optionally, the measurement
source. `Lineage` records the parent claims a value was derived from, as
namespaced references, and optionally the transformation that produced it:
its identifier, its revision and its effective configuration as key and value
pairs. The code describes lineage as "Interpretively sufficient derivation
lineage, not execution genealogy."

One rule is enforced: a transformation without parents is refused (ad hoc
run). The reverse is not: a claim of kind `lab_derived`, or any other derived
kind, is accepted with an empty lineage (ad hoc run). Parent references are
text; nothing resolves them.
`test_organism_affordance_retains_authority_with_cross_domain_lineage` shows
an Organism claim with parents in three namespaces keeping Organism
authority. The word affordance there is a fixture name in a test; it shows
nothing about what an Organism represents.

## Conditions

An `ObservationCondition` qualifies a claim. It has a dimension
(availability or completeness), an origin (source or plane), a kind token
and optional detail text.

The origin is the point of it. A claim can be partial because its source
could only offer part of it, or unavailable because a delivery was lost, and
those are different facts.
`test_plane_condition_is_distinct_from_source_availability` builds an
observation carrying one of each and reads them back separately through
`source_conditions()` and `plane_conditions()`.
`test_unknown_body_pose_unit_can_be_expressed_as_source_nonconformance` uses
a source condition to say that a pose came without a declared unit.

The kind is a free token. The model does not enumerate availability states.
At this revision no code sets a condition of plane origin: the
[observation plane](observation-plane.md) reports its own losses through a
separate signal, not by attaching conditions to observations.

## What the types enforce, and what they leave to the caller

Every type is a frozen dataclass: its fields cannot be reassigned (ad hoc
run). Text fields are normalised and checked. Kinds, methods, relations and
identifiers of contracts are tokens: lower-case, starting with a letter,
segments joined by dots or hyphens. A family path segment may not contain a
dot. An upper-case token is refused (ad hoc run).

Freezing is shallow. The claim value is whatever object the caller supplied,
and is neither copied nor made immutable. In an ad hoc run, a list inside a
claim value was extended after the observation had been built, and the
observation showed the change. An observation whose value is a dictionary
cannot be hashed.

The model therefore guarantees the *shape* of a claim and a small number of
cross-field rules. It does not, and cannot, guarantee that a claim is true,
that the named asserter made it, or that its value follows the contract its
family names. No contract is defined in this repository: `SemanticContractRef`
is two pieces of text.

## The model and the decisions that govern it

Two approved designs and several decision records apply. They state intent.
What follows sets them beside the code; whether the code conforms is recorded
in `registry/designs.yaml`, not here.

The [Observation Semantic Model v1](../../technical/design/observability/observation-semantic-model-v1.md)
defines a claim as "exactly one semantically interpretable assertion under
one primary semantic authority and one epistemic basis". The code gives a
claim one family, hence one authority, and one epistemic kind.

The same model lists epistemic bases it recognises, and availability states,
and adds that "Future contracts need not encode these names literally". The
code encodes none of them: both are free tokens, except `lab_derived`.

The model says that "Every physical magnitude has explicit units defined by
its semantic family" and asks for explicit reference frames. While the core
dataclasses (`observation:src/observation/semantic.py`) leave the payload shape open,
Observation's domain projection adapters now define four concrete semantic families:

| Qualified family | Authority | Epistemic kind | Units / Representations | Source |
|---|---|---|---|---|
| `embodiment.body_pose` (v1) | Embodiment | `authoritative_state` | position: `"m"`; orientation: `"unit_quaternion_xyzw"` (`"right_handed_hamilton_q_v_q_conjugate"`) | `src/observation/embodiment.py:180` |
| `biopeia.embodiment.reserve_state_snapshot` (1) | Embodiment | `authoritative_state` | amount/capacity: `quantity_kind="model_amount"`; fraction: `unit="1"` | `src/observation/embodiment.py:62` |
| `biopeia.environment.finite-scalar-field` (1) | Environment | `domain_derived` | value: `[0.0, 1.0]`, `unit="1"`; sample point: metres | `src/observation/environment.py:161` |
| `biopeia.environment.resource_state_snapshot` (1) | Environment | `authoritative_state` | `remaining`: unitless finite float | `src/observation/environment.py:61` |

Each family declares explicit reference frames (`reference_frame`, `body_frame`),
typed identities (`body`, `embodiment_episode`, `environment_resource`), owner
checkpoint digests, and correlation ticks (`world_causal_tick`).

The model describes itself as "a conceptual model, not a Python type system".
The module's own documentation says it "implements the common in-memory
concepts approved by Observation Semantic Model v1". The second sentence is
the module describing itself.

The [Observation Architecture for Biopeia v1](../../technical/design/observation/observation-architecture-biopeia-v1.md)
decides that the authorities "do not depend on the `observation` package".
The module documentation agrees in words: source domains "do not import this
module". Searching the source packages of `organism`, `embodiment`,
`environment`, `world` and `modality` at their main branches found no import
of it. The integration tests of `world`, installed through a test-only extra,
do import these types and build observations with them.

That design also noted that this module's documentation said the laboratory
hosted the plane. At the revision reviewed here it reads "The Observation
capability hosts this representation for the operational Observation Plane."

[ADR-0095](../../technical/adr/ADR-0095-surviving-semantic-authorities.md)
ratifies four semantic authorities and
[ADR-0099](../../technical/adr/ADR-0099-modality-contract-library.md) keeps
Modality from being one. The enumeration has those four, plus Lab under the
restriction described above, and no Modality.

## What supports this description

| Claim | Support |
|---|---|
| Separate authority, asserter, producer and measurement source; Lab authority requires `lab_derived`; typed identities, links and conflicts; run context kept apart; primary and context time; rejection of boolean, non-finite and delivery-sequence times; lineage with cross-domain parents; source and plane conditions read separately | Code and tests in `observation:tests/test_semantic_model.py` (22 test cases, passing in an extraction of that revision) |
| No Modality authority; `lab_derived` accepted under other authorities; free asserter; time checked by domain only; `wall_clock` accepted as a kind; a transformation needs parents but a derived claim needs no lineage; shallow freezing and mutable values; token grammar | Code, and ad hoc runs of the module at that revision |
| No field for units, frames or observation identity; no contract or family defined | Code reading |
| No source package of another domain imports the module; `world` integration tests do | Text search of each repository's main branch on the day of review; not a test |
| Roles, authorities and the meaning of a claim as intended | The two designs and ADR-0095, ADR-0099, ADR-0100: intent, not results |

The tests exercise construction of values. No test, and nothing examined
here, shows these types carrying a claim from a real authority at run time.

## Open questions

- Which component is meant to check that the named asserter and authority of
  a claim are the real ones, if any is.
- Whether the epistemic bases and availability states of the approved model
  are to become closed vocabularies, and where.
- Where units and reference frames are to be declared once a family exists.
- Whether a claim value should be made immutable when a claim is built.
