# Biopeia docs

Canonical home of the Biopeia **explanatory documentation** and of the
**registry and tooling** that keep that documentation traceable to code,
tests and decisions held in the other Biopeia repositories.

This repository holds no domain logic and no semantic authority. It is
canonical for explanation only. It is **not** the home of scientific evidence,
architectural decisions or the constitution; it links to those in their
designated canonical location and never restates them as a second source of
truth.

> Status: bootstrap. The registry is empty. No Biopeia mechanism is documented
> here yet, and nothing in this repository claims that any extracted
> repository conforms to the Biopeia target architecture.

## Layout

| Path | Purpose |
|---|---|
| `registry/schema.yaml` | Closed vocabularies: domains and their component prefixes, statuses, state owners, lifecycle values |
| `registry/coverage.yaml` | Canonical units: owner, explanation, and the code, tests, design and decisions each is traced to |
| `registry/components.yaml` | Authority, state ownership and lifecycle of each component |
| `registry/parameters.yaml`, `metrics.yaml`, `notation.yaml`, `glossary.yaml` | Reference registries |
| `reference/evidence-status.md` | How to state the strength of a claim, and how that differs from review status |
| `tools/validate_registry.py` | Registry validator and staleness check |
| `MIGRATION.md` | What was taken from the source repository, and what was not |

Explanatory documents live in this repository and are referenced from the
registry by path. Sources in other repositories are referenced as
`<repository>:<path>`, and each unit records in `review.basis` the commit of
every referenced repository at which its explanation was last checked.

Component identifiers carry the prefix of their owning domain: `ORG-`, `EMB-`,
`ENV-`, `WLD-`, `MOD-`, `OBS-`, `LAB-`.

The method for writing and maintaining the documentation is the
scientific-documentation skill kept in `biopeia/.github-private` under
`agents/`.

## Validation

```bash
# Integrity: needs only this repository. This is what CI runs.
python -m pytest
python tools/validate_registry.py

# From the integration workspace: also resolve references into the sibling
# checkouts and report units whose sources changed since their review basis.
uv run --no-project --with pyyaml python repos/docs/tools/validate_registry.py \
    --repos-root repos --stale
```

CI blocks on registry integrity only. It cannot read the other private
repositories, so cross-repository references are reported as unresolved there
and staleness is not evaluated. Staleness is informative: it exits non-zero
only with `--fail-on-stale`. No domain repository runs a documentation check.
