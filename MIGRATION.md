# Migration record

## Provenance

- Source repository: `https://github.com/alessbarb/symbiont-lab`
- Source checkout SHA: `80d372a186513035f85a769db886e505cabba52d`
- Migration mode: non-destructive. The source repository was not modified.

## Scope

Only the documentation **methodology** was migrated: the registry model, its
validation rules and the staleness idea. No document, registry entry, design
asset or publication manifest was copied. Biopeia documentation is to be
written from Biopeia code; the source corpus under `symbiont/docs/` remains
historical evidence in its own repository.

## Disposition

| Original source path | Disposition | Target path | Notes |
|---|---|---|---|
| `tests/docs/test_canonical_references.py` (vocabulary constants) | `REWRITE` | `registry/schema.yaml` | The closed vocabularies lived as constants inside a test module. Domains are now the Biopeia domains with one component prefix each; `TARGET` status, review statuses and state owners were added. |
| `tests/docs/test_canonical_references.py` (rules) | `REWRITE` | `tools/validate_registry.py` | Rules became a library returning errors instead of test functions imported by the gate. Dropped: the fixed count of 48 components, the `SYM-` prefix, non-empty assertions, and the invariants on individual Symbiont notation symbols, which were content rather than method. |
| `tests/docs/test_glossary_registry.py` | `REWRITE` | `tools/validate_registry.py` | Glossary shape and cross-reference rules. |
| `symbiont/docs/coverage.yaml` and `symbiont/docs/reference/*.yaml` | `REWRITE` (structure) / `DROP` (content) | `registry/*.yaml` | Empty registries. Paths became `<repository>:<path>` references; `master.ids` became `component_id`; `review.basis` was added. |
| `symbiont/docs/canonical_impact.py` | `REWRITE` | `tools/validate_registry.py::find_stale_units` | Reduced to its cross-repository core: a unit is stale when a referenced source changed since its review basis, and units depending on it are reported downstream. The per-diff impact report and its reason vocabulary were not carried over. |
| `symbiont/docs/documentation_impact_gate.py` | `REWRITE` / `DEFER` | `.github/workflows/ci.yml`, `tools/validate_registry.py` | Its integrity half is the CI check here. Its change-set half assumed code and documentation change in one pull request of one repository, which cannot hold across repositories; staleness replaces it. Enforcement in the domain repositories is deferred. |
| `symbiont/docs/reference/evidence-status.md` | `REWRITE` | `reference/evidence-status.md` | Evidence status kept; review status and architectural status separated from it. |
| `symbiont/docs/master_projection.py`, `publish_master.py`, `publishers/`, `reference/master-projection.yaml` | `DEFER` | — | Publication waits for content and for a new visual style. |
| `symbiont/docs/audit_legacy_master.py` | `DROP` | — | One-off forensic audit of the Symbiont legacy master document. |
| `DESIGN.md` and the documentation UI kit | `DROP` | — | Deprecated by owner decision; a new style will be defined. |
| `symbiont/docs/**/*.md`, `symbiont/docs/source-map.md` | not migrated | — | Historical corpus; stays in the source repository. |
| Remaining `tests/docs/*` | `DROP` | — | They verify one-time repairs of the source corpus. |

## Validation

`python -m pytest` exercises every rule against a synthetic registry, because
the real registry is empty. Passing it shows that the validator detects the
defects it is tested for. It says nothing about any Biopeia mechanism.

## Resolved after bootstrap

- **Home of decisions and designs.** By owner decision this repository has
  three parts: explanatory documentation, technical documentation (decision
  records and designs) and, later, the Biopeia pages. `registry/schema.yaml`
  records the layout and the validator enforces it. `symbiont-lab` remains an
  accepted historical source for the `design` and `adrs` fields, because the
  Biopeia decisions taken so far (ADR-0073, ADR-0074 and the physical-step
  integration design) are still recorded there. They have not been moved.
- **`lab` as a state owner.** Kept. The migration records show Lab owning
  durable apparatus state: `lab:MIGRATION.md` describes a Lab
  intervention-evidence checkpoint written before World publishes a causal cut
  and registered as a step participant, and Lab run identity distinct from
  intervention identity; the owner authorization places scientific evidence
  custody with the scientific apparatus rather than with Observation. The same
  records bound it: that checkpoint is "Lab provenance, not authority over
  Environment or Embodiment state", and Lab does not own ordinary autonomous
  life. The validator therefore accepts `lab` as a state owner and rejects a
  component owned by a semantic authority that declares Lab-owned state.
  Observation and Modality are not state owners: their retained state is
  `implementation-local` or belongs to the authority it describes.

## Design register

The source repository kept a design status register
(`docs/design/register.md`) with two states per design: a design state and an
implementation state. Its method was migrated; its 91 rows were not.

| Original source path | Disposition | Target path | Notes |
|---|---|---|---|
| `docs/design/register.md` (method and state vocabularies) | `REWRITE` | `registry/designs.yaml`, `registry/schema.yaml`, `tools/validate_registry.py` | A validated registry instead of a Markdown table. A third axis, architecture scope, was added, because the source register could not say whether a design described the current or the target architecture. `not_evaluated` was added to the implementation states. |
| `docs/design/register.md` (91 rows) | not migrated | — | They describe designs of the historical system and their implementation in the source repository. They are evidence to consult, not a backlog to recreate. |

Reasons for the changes, from the source at `cfa137e`:

- The source implementation state describes code in the source repository. It
  is recorded per design under `source` as provenance and never inherited;
  every copied design starts as `not_evaluated`.
- The source kept the states twice, in the register and in the front matter of
  each document. Of the 64 registered designs with front matter, 37 disagreed
  with their register row, and 27 registered designs had no front matter. Here
  the register is the only authority and the validator rejects a design
  document that declares a status.
- Four non-archived designs had no register row, against the register's own
  rule. Here the validator requires an entry for every design document.

### Copied designs

| Original source path | Source blob | Target path | Scope recorded here |
|---|---|---|---|
| `docs/design/runtime/biopeia-physical-step-integration-v1.md` | `a0c7b3e70` | `technical/design/runtime/` | `TARGET` |
| `docs/design/observability/observation-semantic-model-v1.md` | `9aeb1e9a8` | `technical/design/observability/` | `TARGET` |
| `docs/design/observability/observation-architecture-target-design-v1.md` | `72da79533` | `technical/design/observability/` | `UNRESOLVED` |

All three were copied from `cfa137e`. The Observation target design was
approved on 2026-10-07, before the Biopeia Architecture v1 baseline was
ratified, and has not been reviewed against it; it is recorded as `UNRESOLVED`
rather than as Biopeia target. It was copied because the semantic model
depends on it. The `status` and `implementation_status` keys were removed from
the front matter of the physical-step design.

`docs/design/world/world-responsibility-map-v1.md` was **not** copied. Its own
front matter classes it as a reference document: an inventory of the
historical system. A Biopeia design for the World runtime, if needed, is to be
written new.

## Copied Biopeia decision records

By owner decision the Biopeia decision records were **copied**, not moved. The
originals are retained unchanged in the source repository.

By owner decision of 2026-10-09 the source repository is being retired from
active use and Biopeia is the way forward. From this copy onward **the copies
in this repository are the canonical text** of these decisions: changes are
made here, and the originals are the historical record of how the text stood
at the source commit.

- Source commit: `cfa137e167081acac3590fb52ae069adfda605d4`, the head of the
  open candidate alessbarb/symbiont-lab#465. It was **not** on the source
  `main` branch when copied; `main` was at `80d372a` and contained none of
  these three documents.

| Original source path | Source blob | Target path |
|---|---|---|
| `docs/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md` | `07b7b8abd` | `technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md` |
| `docs/adr/ADR-0074-biopeia-world-environment-authority-split.md` | `22a5732f5` | `technical/adr/ADR-0074-biopeia-world-environment-authority-split.md` |

### Architecture decisions AD-0001 to AD-0036

By owner decision the architecture decisions of the audit were transcribed
into independent decision records that continue the numbering: `AD-0001` to
`AD-0036` are `ADR-0075` to `ADR-0110`, one record each, in source order.

- Source: the sealed architecture audit dossier, archive `.audit.zip`
  (SHA-256 `ff258afc…57df2`, recorded in the source repository as
  `BIOPEIA_ARCHITECTURE_V1_AUDIT_BASELINE`). `AD-0001` to `AD-0020` come from
  their rows in `.audit/registers/decisions.md`; `AD-0021` to `AD-0036` from
  their sections in `.audit/ARCHITECTURE_OWNER_TANDA2_RATIFICATION.md`, with
  their register rows.
- Disposition: `SPLIT`, as documentary normalization only, with no semantic
  change. Decision, status and ratification texts are verbatim and were
  checked mechanically against the source. Added: the record number, section
  headings, a Provenance section, a References list mapping cited `AD-`
  identifiers to records here, and, for `AD-0001` to `AD-0020` only, a title,
  because the source rows have none. Those titles are editorial and
  non-normative, and each record says so.
- Where the source does not record an acceptance date or an authority, the
  record says `NOT RECORDED IN SOURCE`. Neither was reconstructed. The
  register rows of `AD-0001` to `AD-0020` carry no date; the row of `AD-0003`
  names no authority.
- The opening and closing statements of the ratification apply to all sixteen
  of its decisions and are reproduced in each of those records. The addenda of
  the register are attached to the decision they concern (`AD-0015`,
  `AD-0020`).
- `UC-0001`, a user constraint of the same register that `AD-0002` and
  `AD-0011` rely on, is reproduced in `technical/adr/README.md`. It is not an
  architecture decision and received no record number.
- Not copied: the review, evidence, finding and open-point records cited by
  identifier, and the rest of the dossier.
- Transcription review: on 2026-10-09 the advisor reviewed the transcription
  and found it acceptable as a faithful transcription, on the basis of the
  mechanical check that every decision, status and ratification text appears
  unmodified, and of two records read in full. That review concerns fidelity
  only. The decisions were ratified by the Architecture Owner, as each record
  states; the advisor did not accept or re-ratify them.

Each copy carries a provenance note under its title. The text is otherwise
unchanged, except that relative links to documents that were not copied
(the constitution, ADR-0060, ADR-0066, ADR-0070, ADR-0072 and the World
responsibility map) now point to the source commit. The other 73 decision
records and the remaining design documents of the source repository describe
the historical system and were not copied.
