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
| Formally defined | The mechanism or property has a precise formal statement (an equation, an invariant, a state machine or a type with stated laws) in a decision, design or reference document, with every term defined |
| Historical | Describes a previous architecture or superseded behaviour |
| Unresolved | Available evidence is insufficient or contradictory |

*Formally defined* says only that the statement is precise. It is not
*Implemented*, *Covered by tests* or *Supported*, and it is not *Intended*:
an intention can be stated in prose, and a formal statement can describe
something nobody has decided to build. A claim can carry several statuses at
once, for example *Formally defined* and *Covered by tests*, each with its
own source. A formal proof about a definition is evidence about the
definition, not about the code, until a test or audit ties the code to it.
In the registry, a parameter whose `source` is `FORMAL`
(`registry/schema.yaml`) takes its value from such a definition; its symbols
belong in `registry/notation.yaml`.

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

### What a review basis covers

A unit's documentation is in one of three situations, and the text must not
let a reader confuse them:

- **Unit reviewed at its basis.** `review.basis` is the revision at which the
  whole explanation was last checked. Moving it requires checking the whole
  unit against the new revision.
- **Section updated.** One identified section was checked against a newer
  revision. The section carries a dated note naming that revision, the
  sources examined and, where it matters, which parts of the unit remain
  covered by the older basis. `review.basis` does not move: a section note is
  not a review of the unit.
- **Unit partly stale.** Sources named by the unit changed after its basis
  and no section note covers the change. The staleness report shows this; it
  is not hidden by editing text.

A section update is enough when the change is confined to what that section
describes. When a change alters a cross-domain contract, an invariant, or a
dependency that the reasoning of other sections relies on, the whole unit is
reviewed and `review.basis` moves.

A review label says that a reviewer examined the explanation against its
sources. It is not a scientific approval and does not raise the evidence
status of any claim: a `CONFIRMED` unit can still describe behaviour that is
only `Implemented` and never `Observed`.

## Architectural status of a unit

`status` in `registry/coverage.yaml` is a third, separate axis: `CURRENT`,
`TARGET`, `DESIGN`, `HISTORICAL`, `EXPERIMENTAL`, `UNRESOLVED`. `TARGET` marks
accepted architecture that the extracted code is not yet claimed to implement.
