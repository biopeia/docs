# The static scene and its owner

Reviewed against `environment` at commit
`f97ec22272b6be1e6742770e37cd370e7d96d6bc`. Everything below describes that
revision. Statements are marked by what supports them: the code, the tests,
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
`test_checkpoint_v3_persists_spheres_and_rejects_v2_without_compatibility`).

Like the [finite resource](finite-resource.md), the owner answers World's
two validation questions without importing World.

## Time

The owner counts adopted steps, starting so that the first step it adopts is
tick zero. In the physical step fixture of World that same step is committed
by World as tick one, because the correlation names the tick of the state the
step starts from and World names the tick of the cut it produces. The two
numbers describe the same step and differ by one. The scene's revision is a
separate marker and is a string chosen by whoever builds the scene; nothing
in this module advances it.

## What is not checked

Read from the code and confirmed by running the module at that revision.

- **That World authorised the correlation.** The class is documented as a
  "World-authorized correlation value; Environment does not mint authority",
  and the owner compares the candidate with an expected correlation. Both are
  handed to it by its caller. Environment cannot tell whether World
  authorised either.
- **That successive steps belong to the same World.** The owner checks the
  environment, the revision and the tick. A step carrying a different World
  identifier was adopted as the next tick.
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
| Scene validation, projection, adoption rules, checkpoint strictness, replay refused after restore | Code and tests in `environment:tests/test_static_scene.py` |
| A step from another World is adopted; owner and environment identifiers are not tied | Code, and one ad hoc run of the module at that revision |
| The offset of one between the owner's tick and World's | Code of this module and of World's physical step fixture |
| That a solver does not own the scene | Accepted decision ADR-0098; a statement of intent |

Procedural generation of scenes and the projection of resource geometry,
which the repository also contains, are not covered here.
