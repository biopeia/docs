# The static scene and its owner

Reviewed against `environment` at commit `4eb1f8c3393a7cdbabcfaf35b8630aaf57de20c1`
(main on 2026-10-15); first written against `f97ec22`. Everything below describes
that revision. Statements are marked by what supports them: the code, the tests,
or neither.

## What it is

A physical step needs to know what the body is standing on and which way is
down. The static scene is Environment's answer in its simplest form: a frame
of reference, a gravity vector, and some fixed geometry. Nothing in it moves.

The scene is Environment's truth, and the module keeps it independent of any
solver: it "has no solver dependency and makes no assumptions about spatial
indexing or terrain generation". A solver is given the scene; it does not
own it
([ADR-0098](../../technical/adr/ADR-0098-physical-substrate-and-causal-integration.md)).
The module describes itself as "a small target capability, not a universal
scene schema".

## What a scene says

A scene (`environment:src/environment/static_scene.py::StaticPhysicalScene`)
names an environment and a revision of it, and carries:

- a **frame**: its identifier, its parent, its origin, three axes and which
  axis is up. The axes must be unit vectors, mutually orthogonal and
  right-handed; anything else is refused;
- **gravity**, in metres per second squared, in that frame;
- **ground planes**, each an infinite plane given by a unit normal and an
  offset in metres;
- **spheres**, each with a centre and radius in metres, in the scene's frame;
- optionally, the **provenance** of a generated scene: seed, generator,
  generator revision and its configuration.

Every object has an identifier, unique within the scene. Units are part of
the names of the fields. Covered by
`test_requires_explicit_sane_frame_units_and_stable_unique_identity`.

A scene is immutable. Projecting it for a consumer returns the same content
with its objects in a canonical order, so two scenes that list the same
objects in different orders project identically
(`test_projection_is_pure_and_collection_order_invariant`,
`test_projection_canonicalizes_sphere_order_by_stable_identity`).

## The owner, and what "adopting" means for something that never changes

The scene has an owner
(`environment:src/environment/static_scene.py::StaticEnvironmentOwner`),
whose role is to take part in a physical step on Environment's behalf.

In the design of the physical step each owner receives a candidate result and
decides whether to adopt it. For a static scene the only acceptable result is
no change at all. The owner therefore adopts a candidate only when:

- the candidate's correlation is exactly the one it was told to expect;
- that correlation names this environment and this revision;
- its tick is the one immediately after the last adopted;
- and the candidate scene is identical to the scene it holds.

When all four hold, nothing about the scene changes; the owner records the
correlation as the last one it accepted. A changed scene is refused, and so
is a repeated or skipped tick
(`test_owner_adopts_only_same_scene_and_next_correlation`).

So adoption here is not a state change. It is Environment's durable mark
that it took part in a step and found its truth unchanged.

## Recovery

The owner's checkpoint is canonical JSON holding the whole scene and the last
accepted correlation. Restoring is strict: unknown fields are refused at
every level, the previous schema version is refused with no compatibility path,
and a restored owner refuses to adopt again a step it had already accepted
(`test_checkpoint_persists_accepted_step_and_rejects_replay_after_restore`,
`test_checkpoint_rejects_unknown_fields_at_each_scene_level`,
`test_checkpoint_v5_persists_contact_properties_and_rejects_v4_without_compatibility`).

Like the [finite resource](finite-resource.md), the owner validates its
checkpoint and verifies restoration against an independent reference without
importing World. Its `verify_restoration(OwnerRestorationReference)` API
requires adaptation to the World runtime's interface; that is not automatic
production wiring.

The owner also exposes a physical projection bound to scene revision,
geometry, units and World step context. It fails closed if contact properties
are absent or the context is stale. Checkpoint schema v5 preserves explicit
sliding-friction properties for the plane and sphere; v4 is rejected without
a compatibility path.

## Bounded static render projection

The repository provides a bounded, read-only static render projection for local
presentation (`environment:src/environment/spatial_render.py`). It projects only
owner-authored static planes and spheres into detached JSON-compatible data.

The module explicitly does not publish, transport, infer a causal cut, or
establish coordinate-frame compatibility with other domains; a proposed contract
is recorded in `environment:contracts/spatial-static-scene-v1.proposed.md`.
The projection enforces strict structural bounds:

- a maximum of 128 render items;
- a maximum of 128 UTF-8 bytes for text identifiers, with control characters
  forbidden;
- finite numbers for coordinates, offsets and radii;
- positive radius for spheres and frame alignment with the scene frame;
- canonical ordering by UTF-8 encoded item identifier;
- a deterministic RFC 8785 canonical JSON digest (`render_geometry_sha256`)
  with a maximum descriptor payload of 65,536 UTF-8 bytes.

Tested by `test_empty_descriptor_matches_approved_jcs_vector` and
`test_sphere_descriptor_matches_approved_jcs_vector` in
`environment:tests/test_spatial_render.py`.

## Time

The owner counts adopted steps, starting so that the first step it adopts is
tick zero. In the physical step fixture of World that same step is committed
by World as tick one, because the correlation names the tick of the state the
step starts from and World names the tick of the cut it produces. The two
numbers describe the same step and differ by one. The scene's revision is a
separate marker and is a string chosen by whoever builds the scene; nothing
in this module advances it.

## What is checked about the World, and what is not

First written against `environment@f97ec22`, when the owner was not tied to
any World. Since `environment@0a9f4fb` it is: an owner is created for one
World, refuses an expected correlation that names another
(`test_checkpoint_rejects_last_correlation_from_another_world` covers the
restored case), and writes the World into its checkpoint, whose schema
changed for that reason. A run of the module at that revision confirmed that
a step carrying another World identifier is refused; at the earlier revision
it had been adopted.

What remains outside the owner's reach, read from the code and confirmed by
the same run:

- **That World authorised the correlation.** The class now says so itself:
  the correlation "is not proof of World authorization" and is derived by an
  integration adapter from World's context. The owner compares the candidate
  with an expected correlation, and both are handed to it by its caller.
- **That the owner's identifier is the environment's.** An owner created with
  an unrelated identifier holds, and validates a checkpoint for, a scene of
  another environment identifier.

A related observation concerns the contract between domains rather than this
module. Environment and Embodiment each define a type named
`PhysicalStepCorrelation`, with different fields, and neither imports the
other's or World's. That the two correlations of one step agree is ensured by
whoever builds them, which today is a test fixture; see
[the physical causal step](../world/physical-step.md).

## What supports this description

| Claim | Support |
|---|---|
| Scene validation, physical projection, adoption rules, checkpoint strictness, contact-property preservation and replay refused after restore | Code and tests in `environment:tests/test_static_scene.py`, `environment:tests/test_environment_physical_projection.py`, and `environment:tests/test_restoration.py` |
| Bounded static render projection and JCS canonical digest verification | Code in `environment:src/environment/spatial_render.py` and tests in `environment:tests/test_spatial_render.py` |
| A step from another World is refused; owner and environment identifiers are not tied | Code, tests, and one ad hoc run of the module at that revision |
| The offset of one between the owner's tick and World's | Code of this module and of World's physical step fixture |
| That a solver does not own the scene | Accepted decision ADR-0098; a statement of intent |

Procedural generation of scenes and the projection of resource geometry,
which the repository also contains, are not covered here.
