# Giving a resource a physical shape

Reviewed against `environment` at commit
`f97ec22272b6be1e6742770e37cd370e7d96d6bc`. Everything below describes that
revision.

## What it is

The [finite resource](finite-resource.md) has a position and a radius, but
they are not physical measurements. The module that projects them says so
directly: "The resource model stores relative lengths rather than calibrated
SI values". A physical step needs metres in a named frame. This small
component bridges the two, and is careful to add nothing that is not given to
it.

## What it does

Given a resource, a frame and a scale in metres per resource unit, it returns
a sphere: the resource's centre and radius multiplied by the scale, expressed
in that frame
(`environment:src/environment/physical.py::project_resource_geometry`,
`test_resource_geometry_projection_scales_into_explicit_frame`).

The frame and the scale must be supplied by the caller. There is no default
for either (`test_projection_requires_caller_declared_frame_and_scale`). The
scale used is kept on the result, so a sphere always says how it was
obtained.

## What it deliberately does not do

- **It does not calibrate.** The scale "is explicit configuration, not
  calibration evidence". The sphere records the number it was given, nothing
  more.
- **It does not transform coordinates.** The centre stays local to the frame;
  nothing is converted to the frame's parent
  (`test_projection_keeps_coordinates_local_to_nontrivial_frame`).
- **It does not turn the field into a collider.** Only the centre and the
  collision radius are projected. The resource's scalar field, its quantity
  and its transfer bound are left alone
  (`test_projection_does_not_treat_field_radius_as_collider_geometry`).
- **It does not change the resource.**

It also performs no contact detection and feeds no solver. The repository's
tests check that its runtime modules import no other domain
(`test_runtime_modules_do_not_import_peer_domains` in
`environment:tests/test_boundary.py`).

## What supports this description

Code and the tests in `environment:tests/unit/test_physical_projection.py`,
named above. A source search did not find a consumer of this projection in
the inspected Biopeia snapshots: Environment
`f97ec22272b6be1e6742770e37cd370e7d96d6bc`, World
`c162b67e698de9b47450264402677b0165e6e20e`, Embodiment
`a5129f03aa4b024e33d332f917b9235afe97959c`, Organism
`6543188ff302a5f2dc8002c0086252d6061e5310`, Observation
`397c0b4691b5e460e6ebc3914f9820ff434a3661`, Modality
`9bd1b77c9eabc271969109cfab52394dc5b52012`, and Lab
`4eee42796ac76af749a6b26f504c5ee88e21faf2`. The search for
`project_resource_geometry` and `PhysicalSphere` found only the Environment
definition, package export and tests in those snapshots; it did not find a
consumer in the other listed repositories. This bounded result does not rule
out consumers outside those snapshots. Where a projected resource sphere
enters a physical scene is not established by the inspected code.
