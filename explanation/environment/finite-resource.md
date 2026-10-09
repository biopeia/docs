# The finite resource

Reviewed against `environment` at commit
`f97ec22272b6be1e6742770e37cd370e7d96d6bc`. Everything below describes that
revision. Statements are marked by what supports them: the code, the tests,
or neither.

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

Its checkpoint is canonical JSON under an explicit type and version. Restoring
accepts exactly that shape and nothing else: unknown fields are refused at
each level, and the shape used before the migration is refused without a
compatibility path (`test_resource_checkpoint_rejects_source_era_v1_shape`,
`test_identified_resource_checkpoint_rejects_unknown_fields_at_each_level`).

The identified resource also answers the two questions World asks of any
owner during a causal cut: are these bytes a valid checkpoint for this
identity under this schema, and, after a restoration, are they still
(`test_owner_checkpoint_validation_checks_identity_schema_and_bytes`). It does
so without importing anything from World. The agreement between the two is
one of shape: World calls two methods by name, and Environment happens to
provide them. See
[the durable World runtime](../world/durable-runtime.md).

## Time

None. The resource reads no clock and counts no ticks. Whatever paces its use
lives outside it.

## How it is used across domains

Lab's operator material transfer composes this resource with a body: the
resource offers, the body accepts, the resource is debited by what was
accepted, and World commits the result.
[ADR-0073](../../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md)
limits what such a transfer may claim: a "controlled experimental transfer
only, not equivalence to an endogenous physical mechanism". Lab's code was
not reviewed for this document.

## What supports this description

| Claim | Support |
|---|---|
| Validation, the field, offer and acceptance, checkpoint round trip and strictness, owner validation | Code and tests in `environment:tests/unit/test_resource.py` and `environment:tests/test_identified_resource.py` |
| The field does not shrink with use; the bound is per call; direct assignment is possible | Code, and one ad hoc run of the module at that revision |
| Lengths are relative, by declaration; the quantity has no unit | Code of this module and of `environment:src/environment/physical.py` |
| Why the quantity belongs to Environment | Accepted decision ADR-0095; a statement of intent |
