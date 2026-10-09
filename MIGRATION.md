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

## Open

- Where Biopeia architectural decisions and design documents will live. Until
  that is decided, `symbiont-lab` is accepted as a historical source for the
  `design` and `adrs` fields only.
- Whether `lab` remains a valid state owner. It is listed for apparatus state
  such as study records, never for organism life state.
- Read access from this repository's CI to the other private repositories,
  required before cross-repository checks can run in CI.
