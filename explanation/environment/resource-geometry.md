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
named above. No consumer of this projection was found in the source of the
other repositories; where a projected resource sphere enters a physical
scene is not established by any code read here.
