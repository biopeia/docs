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
| `symbiont/docs/documentation_impact_gate.py` | `REWRITE` | `.github/workflows/ci.yml`, `tools/validate_registry.py` | Only registry-integrity and staleness concepts were reconstructed. The source change-set enforcement is not transferred; cross-repository enforcement is a separate future governance requirement, not a deferred disposition of this source file. |
| `symbiont/docs/reference/evidence-status.md` | `REWRITE` | `reference/evidence-status.md` | Evidence status kept; review status and architectural status separated from it. |
| `symbiont/docs/master_projection.py`, `publish_master.py`, `publishers/`, `reference/master-projection.yaml` | `DROP` | — | These produce the historical Symbiont master-document publication format. Biopeia has no accepted TARGET requirement for that format; a future publication product would require a new Biopeia-owned design and does not keep these source implementations deferred. |
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
  integration design) are still recorded there. They were later copied here; see below.
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

## First documented unit

The first unit written with the migrated method is the World causal journal
(`component.world-causal-journal`, `WLD-JRN`), reconstructed from `world` at
`dce2c94`. Nothing was taken from the source corpus. Writing it showed two
places where the migrated vocabularies assumed an organism:

- no state family fitted the committed history of a World, so
  `causal_history` was added;
- the `reembodiment` lifecycle axis had no value for a component that
  re-embodiment does not concern, so `not_applicable` was added.

The five lifecycle axes themselves (birth, checkpoint, restart, re-embodiment,
reproduction) are still those of the source registry. They were kept, but two
of the five are not applicable to this component, which suggests they may not
be the right axes for World, Environment or Observation components.

### Lifecycle axes after four World units

Four World components are now registered: the causal journal, the causal
manifest, the journal snapshot store and the durable runtime. How the five
lifecycle axes of the source registry applied to them:

| Axis | Journal | Manifest | Snapshot store | Durable runtime |
|---|---|---|---|---|
| birth | empty | initialize | empty | initialize |
| checkpoint | preserve | not applicable | not applicable | not applicable |
| restart | reset | preserve | preserve | reset |
| re-embodiment | not applicable | not applicable | not applicable | not applicable |
| reproduction | not applicable | not applicable | not applicable | not applicable |

Re-embodiment and reproduction applied to none of the four, and checkpoint to
one. Only birth and restart distinguished these components. What the four
documents needed to say, and the axes do not capture, was whether the
component's state is durable, whether it is part of a causal cut, and what a
failed transition leaves behind.

The review followed. `registry/schema.yaml` now says which block describes a
component's state by owning domain: the lifecycle axes for Organism and
Embodiment, and a `causal_state` block for World that answers exactly those
three questions. The lifecycle axes were not stretched: the `not_applicable`
value added for re-embodiment was removed again, and the validator rejects
lifecycle axes on a World component. Environment, Observation, Modality and
Lab have no required block; none is defined before their components have been
documented. The five World components were migrated.

One limit already visible: `in_causal_cut` is true or false, and the journal
needed a sentence to say that its records are named by a cut only when a
durable runtime drives it.

### Environment, the second domain

Two Environment components were documented from `environment@f97ec22`: the
finite resource and the static scene with its owner. No state dimensions were
defined for Environment. What the two documents had to say about state, as
input for that later decision:

| Question | Finite resource | Static scene |
|---|---|---|
| Does the state change? | Yes, by consumption only | No; only the last accepted step is recorded |
| Does it carry a revision? | No | Yes, a string set by its builder |
| Does it carry units? | No | Yes, in field names |
| Does it take part in a causal cut? | Through an identified checkpoint | Through its owner's checkpoint |
| Does it adopt candidates? | No | Yes, and only an unchanged one |

A state family, `environmental_state`, was added: none of the existing
families described environmental truth.

Two further Environment components followed, procedural genesis and the
physical projection of resource geometry. Both are pure functions that hold
no state of their own; they are registered with implementation-local,
ephemeral state. With four components documented, the state questions that
recur for Environment are: does the state change; does it adopt candidates;
is it revisioned; and are its quantities physical or relative. These are
still not turned into required dimensions here; that is a decision to take
with the other domains in view.

### All seven domains

Embodiment, Organism, Observation, Modality and Lab were then documented in
parallel, each from the main branch of its repository on 2026-10-09, bringing
the registry to units in all seven domains. What that did to the schema:

- **Lifecycle axes on Organism and Embodiment.** Birth, checkpoint and restart
  had meaning for every component. Re-embodiment and reproduction had no code
  path in any of the four components documented; their values were taken from
  the intent of the decision records and say so. No allowed value means "no
  code path". The axes also cannot tell "this component can export and restore
  its state" from "the composed organism keeps it": one Organism component
  round-trips exactly and is carried by no checkpoint.
- **A stateless function is not well described as a component.** Embodiment's
  actuation projection was registered as a mechanism for that reason, and so
  has no authority block.
- **Whether a mechanism that exists only as separate pieces is CURRENT.**
  Organism's action path is CURRENT because every stage is merged source, and
  its document states that the stages are joined only in a World fixture.
- **Observation.** No state block. The plane holds references to values owned
  by each claim's authority, which a single owner field cannot express; it is
  recorded as implementation-local.
- **Lab.** A state family, `evidence_record`, was added for the evidence
  checkpoint. Lab's store also holds files whose bytes belong to Environment
  and Embodiment; the schema cannot express that split.
- **Modality.** No state to ask about: the package is empty, and its unit is
  a concept with status TARGET.
- **Findings can only name a domain repository**, so a tension between two
  decision records kept in this repository cannot be registered as one.

The questions about state that recurred, by domain, and are still not turned
into required dimensions:

| Domain | Questions its documents had to answer |
|---|---|
| Environment | Does the state change; does it adopt candidates; is it revisioned; are its quantities physical or relative |
| Observation | Is it durable; whose are the values it holds, and are they copies; is an absence evidence of anything; is its ordering a domain time |
| Lab | Whose is a record Lab wrote about another owner's state; is the record in a causal cut, and for how long; what marks a record of a failed transition |
| Modality | None today; by decision, who would own a transducer's state |

A registry of cross-domain contracts and a generated reference page were
added at the same time, and the first explanation that crosses all the
domains, derived from the unit documents.

### Measuring what is covered

`tools/validate_registry.py --coverage` counts, per domain repository, the
source modules named by some unit, and lists those named by none. Measured on
2026-10-09 against the main branches:

| Repository | Source modules | Named by a unit |
|---|---:|---:|
| world | 4 | 4 |
| environment | 5 | 5 |
| observation | 4 | 4 |
| lab | 5 | 5 |
| embodiment | 14 | 8 |
| organism | 90 | 14 |
| modality | 0 | 0 |

Modality has no source module at all: its package is an `__init__.py` that
exports nothing, with one test asserting that. Its unit therefore documents
everything the repository holds, and a second unit would have nothing to
describe. That is the real state of the domain, not a gap in documentation;
the gap is in the code, and is tracked as a finding with an issue.

### What the staleness check cannot see

The staleness check compares, for each unit, the paths the unit already
names. It found nothing when `world` gained a second physical-step fixture
after the physical step was documented, because a new file is not a changed
path. The document then said "one fixture" and was wrong. It was noticed by a
reader, not by the check.

The check therefore answers "did what I cited change", not "did something
new appear that I should have cited". A unit that makes a claim of absence
(no other caller, no other fixture, no consumer) is exposed to this, and such
claims should name the search they rest on and its date, as the corrected
documents now do.

### Findings

`registry/findings.yaml` was added so that what documentation discovers
becomes work that can be tracked instead of prose that can be missed. The
classes are those set by the owner: implementation finding, contract gap,
evidence gap, performance concern, recovery or durability gap, documentation
inconsistency. The first twelve entries come from the World documents; six
are material and each has an issue in `biopeia/world`.

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
| `docs/design/observability/observation-architecture-target-design-v1.md` | `72da79533` | `technical/design/observability/` | `HISTORICAL`, superseded |

All three were copied from `cfa137e`. The Observation target design was
approved on 2026-10-07, before the Biopeia Architecture v1 baseline was
ratified. It was copied because the semantic model depends on it. On review
it conflicts with the ratified authorities, and the Architecture Owner classed
it `HISTORICAL` and superseded on 2026-10-09. It is preserved unchanged as
evidence; a Biopeia Observation design is to be written new. The `status` and `implementation_status` keys were removed from
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

## Provisional historical source-artifact inventory

The rows below close the initial *classification pass*, not migration approval.
They are scoped to source tree `alessbarb/symbiont-lab` at
`80d372a186513035f85a769db886e505cabba52d` unless a row explicitly names a
separate source revision. `DEFER` means no target transfer is authorized yet;
it is not a final disposition. Historical sources remain in their source
repository as provenance. No source file, document, dossier, audit artifact,
or design asset is copied or edited by this inventory. Any later Biopeia
explanation must be reconstructed from Biopeia implementation and evidence.

| Source path / family at pinned source | Target repo / path (candidate only) | Provisional disposition | Reason and caveat / revisit trigger |
|---|---|---|---|
| `docs/adr/ADR-0001-*.md`–`ADR-0072-*.md`, `docs/adr/README.md` | None as direct source copies | `DROP` | These are historical Symbiont decision records, not Biopeia authority. The pinned source tree and individual blob identities are recorded in [the disposition evidence manifest](technical/migration/source-disposition-evidence-80d372a.md). This disposition means no direct transfer of these source files; it does not delete the source or deny that separately ratified Biopeia decisions may have historical provenance. The Biopeia records ADR-0075–ADR-0110 are separately transcribed decision artifacts, not proof that each source ADR maps one-to-one. |
| `docs/adr/ADR-0073-*.md`, `ADR-0074-*.md` at source candidate commit `cfa137e167081acac3590fb52ae069adfda605d4` | `docs` / `technical/adr/ADR-0073-*`, `ADR-0074-*` | `SPLIT` | The current canonical migration record says decision records were copied, not moved, and are canonical text in Biopeia; the original source records remain historical provenance. This row classifies those source originals only and does not revise target authority or any PR status. |
| `docs/design/**` (including `docs/design/register.md`) | Relevant owner repo contract/design or `docs/design/` after fresh reconstruction; no direct transfer target | `SPLIT` | The source set spans Organism, Embodiment, Environment, World, Observation, Lab, governance, experiments, historical and implementation-specific material. Inventory each design against current Biopeia code/evidence and assign an owner before any new target document is written; historical source stays intact. |
| `docs/design/observability/observation-semantic-model-v1.md` and `docs/design/runtime/biopeia-physical-step-integration-v1.md` at source candidate commit `cfa137e167081acac3590fb52ae069adfda605d4` | `docs` / `technical/design/observability/` and `technical/design/runtime/` | `SPLIT` | The current canonical migration record lists these as copied target design documents; the historical source files remain unchanged. This row classifies source originals only and does not change the target designs’ existing status or authority. |
| `docs/design/archive/**`, `docs/history/design/**`, `docs/history/roadmap-log.md` | None; source repository remains historical record | `DROP` | Historical/archive material has no justified direct target role. Preserve source history; revisit only if a specific scientific or provenance question requires a newly reconstructed Biopeia explanation. |
| `docs/governance/constitution.md`, `docs/governance/README.md`, `docs/governance/decision-gates.md` | None as source copies; Biopeia governance is maintained in its own canonical records | `REWRITE` | The source constitution/governance describes Symbiont authority and policy. Never transplant it as Biopeia law; any needed invariant must be independently ratified and recorded by Biopeia. |
| `docs/governance/*.toml` (active-work, agent-policy, change-surfaces, frozen-artifacts, owner-root, project-state, publication, resource, test-impact, validation matrices) | None; source repo operational governance | `DROP` | These files govern source repository operations, not target domain semantics. Revisit only if a separately justified Biopeia governance requirement is identified and accepted. |
| `docs/history/governance/**` | None | `DROP` | Historical authority grants are source-specific operational history; preserve in source and do not reproduce as target authority. Revisit only for a documented provenance need. |
| External `.audit.zip` archive and its `.audit/` dossier (associated with source baseline reference `ff258afc…57df2`; archive is absent from pinned Git tree `80d372a186513035f85a769db886e505cabba52d`) | `docs` / `technical/adr/ADR-0075`–`ADR-0110` for AD-0001…AD-0036; remainder has no target copy | `SPLIT` | The current canonical migration record says AD-0001…AD-0036 were transcribed into separate decision records; review/evidence/finding/open-point materials and the rest of the dossier were not copied. The archive’s full digest is not verified in this inventory; retain it as external provenance and revisit only if specific source evidence is needed. |
| `docs/design/register.md` and source design-status rows | `docs` / `registry/coverage.yaml` only as methodology analogue; individual source entries have no direct destination | `REWRITE` | The registry/validation method was independently adapted; source design rows/statuses are not migrated. Revisit entries only through Biopeia design review against target code and current status. |
| `docs/methodology/**` | `lab` / future methodology documentation (no source copy) | `REWRITE` | Methodological ideas may be useful, but the source program and scientific claims are not Biopeia defaults. Reconstruct against Biopeia study/run/evidence boundaries; revisit when Lab implementation supports a concrete explanation. |
| `docs/safety/README.md` | None as a direct source copy | `DROP` | The only file in this source family at the pinned tree is a Symbiont-specific host-boundary policy: it governs synthetic cognition and read-only local host discovery. No such Biopeia host-discovery capability or accepted target contract is present in the audited Modality tree; copying this policy would falsely transfer source semantics. The exact source blob is listed in [the disposition evidence manifest](technical/migration/source-disposition-evidence-80d372a.md). This is not a blanket Biopeia safety determination: any future host-facing capability requires its own Biopeia-owned safety contract before implementation. |
| `docs/development/**` | None | `DROP` | Source maintainability, type-checking and scanner baselines are repository-specific tooling. Revisit only if Biopeia establishes equivalent tooling needs independently. |
| `docs/README.md`, `docs/architecture.md`, `docs/glossary.md`, `docs/roadmap.md`, `docs/CHANGELOG.md`, `docs/VERSIONING.md` | `docs` / Biopeia-specific documentation only after reconstruction | `REWRITE` | These describe historical Symbiont architecture, terms, plans and releases. Do not copy or preserve them as target commitments; write Biopeia material from target-owned implementation and decisions when needed. |
| `symbiont/docs/00-foundations-and-epistemology.md`–`14-mathematical-map.md` | None as source copies | `DROP` | Legacy explanatory corpus is explicitly not a migration input under the Biopeia documentation policy. Preserve only at source; a future target explanation must be independently reconstructed from Biopeia evidence. |
| `symbiont/docs/anatomy/**`, `atlas/**`, `decisions/**`, `executive/**`, `explanation/**` (including concepts/math), `index.md` | None as source copies | `DROP` | These are source-specific projections and interpretations; copying would carry historical semantics into target. Revisit only for a concrete Biopeia phenomenon, then reconstruct rather than translate/copy. |
| `symbiont/docs/source-map.md` | None | `DROP` | The path map points into source implementation and cannot be authoritative for Biopeia. Revisit only to create a new source map against Biopeia code when such documentation is requested. |
| `symbiont/docs/coverage.yaml`, `reference/components.yaml`, `reference/glossary.yaml`, `reference/metrics.yaml`, `reference/notation.yaml`, `reference/parameters.yaml`, `reference/master-projection.yaml` | `docs` / `registry/*.yaml` for empty schema/methodology only | `REWRITE` | Structure was considered/adapted in the registry, but no source entries, IDs, metrics, notation, parameter values or content were transferred. Revisit only for independently evidenced Biopeia entries. |
| `symbiont/docs/reference/domain-map.md`, `evidence-status.md`, `state-ownership.md` | `docs` / future reference documents, not source copies | `REWRITE` | Source owner/evidence model is not identical to Biopeia. Reconstruct from accepted authority and evidence contracts; do not assume direct semantic equivalence. |
| `symbiont/docs/canonical_impact.py`, `documentation_impact_gate.py` | `docs` / `tools/validate_registry.py` | `REWRITE` | Registry integrity/staleness concepts were reduced and adapted. Source-specific impact selection/enforcement was not carried over. Any future domain-repository enforcement is a separate Biopeia governance change; it is not a pending disposition of either source file. |
| `symbiont/docs/master_projection.py`, `publish_master.py`, `publishers/**`, `reference/master-projection.yaml` | None | `DROP` | These generate/publish the historical master-document format and are not needed for target documentation. No Biopeia publication product is being deferred here; any future product requires a separate design and implementation. |
| `symbiont/docs/audit_legacy_master.py` | None | `DROP` | One-off audit of a source legacy master document; no target behavior to preserve. |
| `DESIGN.md`, `_agents/skills/symbiont-design/**`, `symbiont/docs/ui_kits/**` and related source documentation UI assets | None | `DROP` | Source-specific presentation system is not a scientific/documentation authority for Biopeia and is excluded from migration. Revisit only under an explicit Biopeia-owned design brief. |
| `tests/docs/test_canonical_impact.py`, `test_documentation_impact_gate.py` (registry-integrity/staleness assertions only) | `docs` / `tests/test_validate_registry.py` | `REWRITE` | Only target-neutral registry/staleness behavior is covered by the Biopeia validator tests; source impact selection is excluded. Confirm target tests remain adequate whenever validator behavior changes. |
| `tests/docs/test_canonical_references.py`, `test_glossary_registry.py` | `docs` / `tools/validate_registry.py` and `tests/test_validate_registry.py` | `REWRITE` | Methodology and neutral structural constraints were adapted; source vocabulary, identifiers, fixed counts and Symbiont-specific assertions were dropped. |
| `tests/docs/test_all_markdown_links_resolve.py`, `test_canonical_references.py` (source-only reference assertions), `test_executive_reference_integrity.py`, `test_portal_index_and_glossary.py`, `test_web_no_milestone_vocabulary.py`, `test_web_readme.py`, `test_web_sources_exist.py` | None | `DROP` | These assert source-site layout/content and one-time repairs, not Biopeia behavior. Revisit only if a Biopeia docs-site feature is independently implemented and needs new tests. |
| `tests/docs/test_architecture_merge.py`, `test_design_consolidation.py`, `test_design_reference_repair.py`, `test_roadmap_references_repaired.py`, `test_roadmap_split.py`, `test_changelog_consolidation.py`, `test_internal_is_gone.py` | None | `DROP` | These are one-off source corpus cleanup/repair tests. No legacy tests or cleanup-only behavior is migrated. |
| `tests/docs/test_biological_memory_citations.py`, `test_fuentes_taxonomy.py`, `test_legacy_audit.py`, `test_master_projection.py`, `test_repository_layout.py`, `test_glossary_registry.py` (source-specific assertions), plus `tests/docs/README.md`, `tests/docs/__init__.py`, `tests/docs/conftest.py`, `tests/docs/fixtures/**` | None | `DROP` | Source-specific citation, taxonomy, forensic audit, publication, layout, fixtures and harness are not justified target capabilities. Keep source history intact; write new target tests only for implemented Biopeia contracts. |

A `DROP` disposition means “not transferred to Biopeia”; it does not authorize
deleting or rewriting the historical source. A `REWRITE` or `SPLIT` entry is
not permission to retain legacy code, content, APIs or compatibility behavior.
Any `DEFER` row remains open and must be revisited before declaring the
inventory complete. This table distinguishes dispositions of source artifacts
from the canonicality and lifecycle status of any selected Biopeia documents;
it changes neither those existing records nor Docs PR status.
