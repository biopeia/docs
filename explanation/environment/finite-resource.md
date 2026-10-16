# The finite resource

Reviewed against `environment` at commit `d09e45c47fe86c23b2fc977e26938920eb9058b8`
(main on 2026-10-14); first written against `f97ec222`. Everything below
describes the later revision. Statements are marked by what supports them: the
code, the tests, or neither.

## What it is

Something in the environment that can be used up. The finite resource is the
smallest piece of environmental truth in Biopeia: a quantity that exists at a
place, can be drawn down, and does not come back.

It belongs to Environment. That placement is the point of the component.
How much of the resource remains is a fact about the world outside any
organism, and the code keeps it there: the class "does not determine contact,
cause an organism action, or assign meaning to the resource". It is not food,
reward or a goal. Those would be interpretations, and interpretations belong
to whoever makes them
([ADR-0095](../../technical/adr/ADR-0095-surviving-semantic-authorities.md)).

## What it holds

A position, a radius, the radius of a surrounding field, the quantity
remaining, and a bound on how much may be transferred in one tick
(`environment:src/environment/resource.py::FiniteResourceState`). All are
checked on creation: finite numbers, positive sizes, a non-negative quantity,
and a field wider than the resource itself
(`test_resource_rejects_invalid_configuration`).

None of these values carries a unit, and for the lengths that is deliberate.
The module that gives a resource a physical shape states that "The resource
model stores relative lengths rather than calibrated SI values": position,
radius and field radius share one relative scale, and become metres only when
a caller supplies a frame and a scale; see
[giving a resource a physical shape](resource-geometry.md). The quantity
remaining and the transfer bound are bare numbers with no unit and no such
projection.

## The field around it

At any point, the resource reports a scalar between zero and one that falls
off with distance and is zero beyond the field radius. It is a magnitude
only: it says nothing about direction and nothing about what the resource is
(`test_resource_field_is_local_scalar_and_extinguishes_when_depleted`).

The field does not shrink as the resource is used. It is the same whether the
resource is full or almost empty, and drops to zero only when nothing
remains. Confirmed by running the module: a resource holding a thousandth of
a unit reports the same field at its centre as a full one.

## How it is used up

Two operations, deliberately separate.

- The resource says how much it **offers** this tick: the lesser of the
  per-tick bound and what remains.
- A consumer reports how much it actually **accepted**, and the resource
  removes that, never more than the bound and never more than what remains.
  It returns the amount it really removed.

The separation matters because offering is not giving. What leaves the
environment is what the other side took, as reported by it. The module says
so: "the consumer reports only the amount it actually accepted". Covered by
`test_resource_debits_only_accepted_material_with_transfer_bound` and
`test_resource_rejects_invalid_consumption`.

There is no operation that adds to the resource. It is a source that does not
regenerate.

## What is not enforced

Read from the code and confirmed by running the module at that revision.

- **The per-tick bound is per call, not per tick.** The resource has no
  notion of a tick; its documentation speaks of "one caller-defined tick".
  Three successive calls each remove up to the bound. Keeping to one transfer
  per tick is the caller's responsibility.
- **Offering and accepting are not linked.** Nothing requires an offer before
  an acceptance, or that the accepted amount relate to what was offered.
- **The state can be assigned directly.** The remaining quantity is an
  ordinary attribute; code holding the object can set it without going
  through consumption.

## Identity and recovery

A resource by itself has no name. The identified resource
(`environment:src/environment/identified_resource.py::IdentifiedFiniteResource`)
pairs a state with a stable identifier and is what takes part in a causal
cut. The identity "belongs to the Environment owner boundary and is carried
by its checkpoint. It is not inferred from a caller's intervention request".

Its checkpoint is canonical JSON under an explicit type
(`biopeia.environment.identified-finite-resource`), version (1), and owner
schema (`environment-identified-resource-v2`). Restoring accepts exactly that
shape and nothing else: unknown fields are refused at each level, and the shape
used before the migration is refused without a compatibility path
(`test_identified_resource_checkpoint_preserves_owner_identity_and_state`,
`test_identified_resource_checkpoint_rejects_invalid_identity_or_shape`,
`test_identified_resource_checkpoint_rejects_unknown_fields_at_each_level`).

The identified resource validates checkpoints and verifies a restored owner
against an independent `OwnerRestorationReference`. It does so without
importing anything from World. The restoration interface is an instance
method `verify_restoration(reference)` that requires an adapter to match the
durable World runtime's interface; see
[the durable World runtime](../world/durable-runtime.md).

## Sampling the field and projecting an observation

An identified resource can be wrapped as an identified scalar field
(`environment:src/environment/identified_resource.py::IdentifiedFiniteScalarField`).
It binds resource identity and field revision to an Environment identity,
revision, and frame, and reports dimensionless values in `[0, 1]`. For this
wrapper only, positions and radii are expressed in metres.

The wrapper provides two distinct operations:

1. **Source-step field sampling** (`sample_field`): Evaluates the field before
   a physical step occurs, correlated with a `PhysicalStepCorrelation`. It
   emits a `FiniteScalarFieldSample` recording the active causal tick, frame,
   coordinates in metres, and the exact SHA-256 digest of the serialized
   owner checkpoint from which the sample was evaluated
   (`source_owner_checkpoint_sha256`).
2. **Post-adoption observation projection** (`project_observation`): Evaluates
   the field after Environment has adopted the state for a target step, for
   ingestion into Observation. The caller passes an
   `EnvironmentObservationContext`
   (`environment:src/environment/identified_resource.py::EnvironmentObservationContext`),
   which carries World identity, physical step identity, active Environment
   identity and revision, resource identity and field revision, and asserts
   that `target_causal_tick == source_causal_tick + 1`.

The resulting projection
(`environment:src/environment/identified_resource.py::FiniteScalarFieldObservationProjection`)
declares the semantic family `biopeia.environment.finite-scalar-field` (revision
`1`). It names `ENVIRONMENT` as the semantic authority,
`environment.identified_finite_scalar_field` as the asserter, and
`environment.identified_finite_scalar_field.project_observation` as the producer.
Its epistemic basis is `DOMAIN_DERIVED` and acquisition basis is
`environment_field_evaluation`.

To guarantee that the emitted value matches the recorded digest, both
operations serialize their owner state, restore a temporary instance from those
checkpoint bytes, and evaluate the field on the restored owner. Both verify
that the restored checkpoint matches the expected frame, environment identity,
and revision (`test_scalar_field_observation_projection_is_distinct_from_source_sample`,
`test_scalar_field_sample_rejects_invalid_checkpoint_digest`).

What this operation deliberately does not do:

- **It does not prove World authorization or adoption.** The context is
  caller-supplied correlation data, not a cryptographic receipt of World commit.
- **It does not identify a receptor or transduce a signal.** Embodiment owns
  receptor identity and Modality owns sensory transduction contracts.
- **It does not publish to Observation.** World and Observation own delivery
  to the observation plane.

## Projecting committed resource state

When World commits a causal cut, the remaining quantity of an identified
resource can be projected as an observational claim via
`project_committed_resource_state(checkpoint_bytes, *, committed_cut, owner_reference)`
(`environment:src/environment/identified_resource.py`).

Environment does not import World types. Instead, it interacts with World
records through two structural protocols:

- `_CommittedCheckpointReference`: expects `owner`, `owner_identity`,
  `checkpoint_id`, `schema_version`, and lowercase SHA-256 `sha256`.
- `_CommittedWorldCutReceipt`: expects `world_id`, `causal_tick` (integer $\ge 0$),
  `commit_id`, and a tuple `owner_checkpoint_references`.

The projection enforces strict structural consistency:

1. The `committed_cut` must carry non-empty `world_id` and `commit_id`, and a
   non-negative integer `causal_tick`.
2. The `owner_reference` must be an element of the receipt's
   `owner_checkpoint_references` tuple.
3. The `owner_reference.owner` must equal `"environment"`, and its
   `schema_version` must equal `IdentifiedFiniteResource.OWNER_SCHEMA`
   (`"environment-identified-resource-v2"`).
4. The exact `checkpoint_bytes` must hash to `owner_reference.sha256`.
5. Decoding `IdentifiedFiniteResource.from_checkpoint_bytes(checkpoint_bytes)`
   must succeed, and the restored resource's `resource_id` must match
   `owner_reference.owner_identity`.

If any check fails, the projection fails closed with `ValueError`
(`test_committed_resource_projection_requires_exact_world_owner_reference`,
`test_committed_resource_projection_rejects_wrong_digest_on_listed_reference`,
`test_committed_resource_projection_rejects_mismatched_listed_owner_reference`,
`test_committed_resource_projection_rejects_malformed_world_cut_fields`).

When valid, it returns a `ResourceStateObservationProjection` carrying the
resource identifier, `remaining` material, World commit coordinates, and the
SHA-256 digest of the exact source checkpoint. It belongs to the semantic
family `biopeia.environment.resource_state_snapshot` (revision `1`), under
authority `ENVIRONMENT`, asserter `environment.identified_finite_resource`, and
producer `environment.identified_finite_resource.project_committed_state`.

The trust boundary is explicit: Environment proves that the projection was
derived from the exact checkpoint referenced in the receipt and that the owner
reference is structurally listed in the cut. It does not authenticate World's
signature or commit authority; World remains the trust boundary for the receipt
itself.

## Time

None. The resource reads no clock and counts no ticks. Whatever paces its use
lives outside it.

## How it is used across domains

1. **Lab material transfer**: Lab's operator material transfer composes this
   resource with a body: the resource offers, the body accepts, the resource is
   debited by what was accepted, and World commits the result
   ([ADR-0073](../../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md)).
2. **Observation plane**: World adapters take committed cuts and owner
   checkpoints, invoke `project_committed_resource_state` and
   `project_observation`, and translate the resulting domain projections into
   passive observation records.

## What supports this description

| Claim | Support |
|---|---|
| Validation, offer and acceptance, checkpoint round trip and strictness | Code and tests in `environment:src/environment/resource.py`, `environment:tests/unit/test_resource.py`, and `environment:tests/test_identified_resource.py` |
| The field does not shrink with use; the bound is per call; direct assignment is possible | Code, and one ad hoc run of the module at that revision |
| Lengths are relative, by declaration; the quantity has no unit | Code of `environment:src/environment/resource.py` and `environment:src/environment/physical.py` |
| Identified scalar field, sample correlation, and post-adoption projection | Code in `environment:src/environment/identified_resource.py:215-554` and tests in `environment:tests/test_identified_resource.py:309-552` |
| Committed resource state projection, World receipt protocol, and strict rejection of unlisted or mismatched references | Code in `environment:src/environment/identified_resource.py:38-138` and tests in `environment:tests/test_identified_resource.py:43-204` |
| Why the quantity belongs to Environment | Accepted decision ADR-0095; a statement of intent |
