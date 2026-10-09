# Evidence status and review status

Two different questions are asked about a documented claim. They use two
different vocabularies and must not be merged.

## Evidence status: how strong is the support for the claim?

Use this language in prose when stating what the system does.

| Status | Meaning |
| --- | --- |
| Implemented | A current code path realises the mechanism |
| Covered by tests | Tests exercise the stated behaviour under defined conditions |
| Observed | A recorded runtime or experiment exhibited the behaviour |
| Supported | Multiple observations or a controlled study support an interpretation |
| Intended | Present in a specification or accepted decision but not established as current behaviour |
| Historical | Describes a previous architecture or superseded behaviour |
| Unresolved | Available evidence is insufficient or contradictory |

Avoid "proves", "guarantees", "always" and "never" unless the claim is
genuinely established by the relevant contract and all reachable code paths.
Make the scope of a claim visible: name the repository, the revision and the
conditions under which it holds.

## Review status: has the documentation of a unit been independently checked?

Recorded per unit in `registry/coverage.yaml` as `review.status`, together with
`review.basis`, the commit of each referenced repository at which the
explanation was last checked. The labels are the coordination labels proposed
in the shared Biopeia evidence policy: `RECORDED`, `REVIEW_PENDING`,
`CONFIRMED`, `CONFIRMED_WITH_LIMITATIONS`, `NOT_REPRODUCED`, `SUPERSEDED`.

A review label says that a reviewer examined the explanation against its
sources. It is not a scientific approval and does not raise the evidence
status of any claim: a `CONFIRMED` unit can still describe behaviour that is
only `Implemented` and never `Observed`.

## Architectural status of a unit

`status` in `registry/coverage.yaml` is a third, separate axis: `CURRENT`,
`TARGET`, `DESIGN`, `HISTORICAL`, `EXPERIMENTAL`, `UNRESOLVED`. `TARGET` marks
accepted architecture that the extracted code is not yet claimed to implement.
