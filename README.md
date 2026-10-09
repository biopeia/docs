# Biopeia docs

Canonical home of the Biopeia documentation, in three parts:

1. **Explanatory documentation** (`explanation/`): how Biopeia works, traced
   to code, tests and decisions.
2. **Technical documentation** (`technical/adr/`, `technical/design/`):
   architectural decision records and design documents.
3. **Biopeia pages**: the published site. Not started.

A **registry and its tooling** keep the explanation traceable to sources held
here and in the other Biopeia repositories.

This repository holds no domain logic and no semantic authority. Recording a
decision here does not accept it: a decision record is authoritative only once
its authorized owner has accepted it, and green CI never stands in for that
acceptance. Scientific evidence and experiment records are **not** kept here;
they stay with the scientific apparatus that produced them and are linked,
never restated as a second source of truth.

> Status: bootstrap. The registry is empty. No Biopeia mechanism is documented
> here yet, and nothing in this repository claims that any extracted
> repository conforms to the Biopeia target architecture.

## Layout

| Path | Purpose |
|---|---|
| `explanation/` | Explanatory documents. Created with the first documented unit |
| `technical/adr/`, `technical/design/` | Decision records and design documents. Created with the first record |
| `registry/schema.yaml` | Closed vocabularies: domains and their component prefixes, statuses, state owners, lifecycle values |
| `registry/coverage.yaml` | Canonical units: owner, explanation, and the code, tests, design and decisions each is traced to |
| `registry/components.yaml` | Authority, state ownership and lifecycle of each component |
| `registry/parameters.yaml`, `metrics.yaml`, `notation.yaml`, `glossary.yaml` | Reference registries |
| `reference/evidence-status.md` | How to state the strength of a claim, and how that differs from review status |
| `tools/validate_registry.py` | Registry validator and staleness check |
| `MIGRATION.md` | What was taken from the source repository, and what was not |

Explanatory documents are referenced from the registry by path and must live
under `explanation/`. Decisions and designs kept here are referenced as
`docs:technical/adr/...` and `docs:technical/design/...`. Sources in other
repositories are referenced as `<repository>:<path>`, and each unit records in `review.basis` the commit of
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
