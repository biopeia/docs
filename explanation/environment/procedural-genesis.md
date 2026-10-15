# Procedural genesis of a scene

Reviewed against `environment` at commit
`d09e45c47fe86c23b2fc977e26938920eb9058b8` (main on 2026-10-14); first written against `f97ec222`. Everything below describes that
revision. Statements are marked by what supports them: the code, the tests,
or neither.

## What it is

A [static scene](static-scene.md) can be written by hand. It can also be
generated. Procedural genesis is one generator: given a seed and an explicit
configuration, it produces a ground plane and a number of spheres placed
inside a box.

Its purpose is reproducibility, not realism. At this generator revision, the
test gives equal scenes for identical complete specifications, and the scene
records how it was made. Cross-machine portability has not been tested and is
not claimed. The module is explicit about the limits of its claims: it "makes
no guarantee of non-overlap, terrain quality, ecological meaning, or
scientific suitability", and describes itself as "one genesis capability,
not a universal Environment representation or a solver scene format".

## What goes in

A specification
(`environment:src/environment/procedural_genesis.py::EnvironmentGenesisSpec`)
names the seed, the generator and its revision, and a configuration: the
environment's identifier and revision, the frame, gravity, the ground plane,
the two corners of the box, how many spheres, and the smallest and largest
radius. Lengths are metres in the scene's frame. A configuration with an
empty box, a negative count or an inverted radius range is refused
(`test_rejects_invalid_generation_configuration`).

Only one generator exists, under one identity and one revision. A
specification naming any other is refused
(`test_rejects_unknown_generator_contract_and_non_integer_seed`).

## How a scene is produced

The whole specification is written in a canonical form. For each sphere, a
SHA-256 is taken over that form and the sphere's index, and four numbers
between zero and one are read from the digest: three place the centre inside
the box, the fourth picks the radius within the range.

The generator's canonical inputs include the seed and the full configuration,
including the sliding-friction coefficient for generated spheres. Plane and
sphere friction are retained in the generated scene and in the canonical
configuration used for its digest. The function's own description says it
"does not read host time, process state, or global RNG". Changing the seed
or configuration changes the scene
(`test_seed_and_configuration_are_causal_generator_inputs`), and equal
specifications give equal scenes
(`test_same_complete_spec_generates_same_scene_and_explicit_provenance`).

## What comes out

An ordinary static scene, with the generated spheres as its geometry and the
seed, generator, revision and configuration attached as its provenance. From
then on it is Environment's truth like any other scene: the
[owner](static-scene.md) holds it, checkpoints it in full and adopts steps
against it (`test_generated_geometry_is_scene_authority_and_checkpoint_restores_it`).

Restoring a checkpoint does not run the generator again. The scene is stored
complete and the provenance is kept as an opaque record of how it came to be
(`test_checkpoint_keeps_generator_configuration_structured_and_opaque_on_restore`).
A scene therefore survives a later change of the generator; whether the
provenance still regenerates it is not checked.

## What it does not ensure

Stated by the module and confirmed by running it at that revision.

- **The spheres may overlap one another.** Forty spheres of radius 0.2 to
  0.5 m in a two-metre box gave 107 overlapping pairs.
- **The spheres may cross or lie under the ground plane.** The box is
  independent of the plane; in the same run 23 spheres did.
- **Nothing is said across revisions.** The description limits determinism to
  "this exact generator identity and revision" and "does not promise
  cross-revision equivalence".
- **The spheres mean nothing.** They carry an index as identifier and no
  label. The repository's README notes that the placement "carries no
  cognitive labels".

## Time

None. Generation happens once, before the scene exists, and reads no clock.

## What supports this description

| Claim | Support |
|---|---|
| Inputs (including sphere friction), refusal of invalid or unknown specifications, determinism, sensitivity to seed and configuration, provenance, checkpoint of a generated scene | Code and tests in `environment:tests/test_genesis.py` |
| Overlapping spheres and spheres under the ground | Code, and one ad hoc run of the module at that revision |
| The limits of what is claimed | The module's own documentation and the repository's README |
