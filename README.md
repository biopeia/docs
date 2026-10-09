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
decision here does not accept it, and green CI never stands in for acceptance.
Who accepts a new decision depends on its class:

| Class | Accepted by |
|---|---|
| Ordinary, including migration implementation decisions | During the migration, the advisor may accept |
| Architecture refinement within already ratified invariants | During the migration, the advisor may accept |
| Scientific | The corresponding scientific authority and review |
| Frozen | The authority named by its review policy |
| Constitutional | The Architecture Owner / repository owner |

The advisor is the reviewer model that the Claude agent carrying out the
migration consults (Claude Code's advisor). Its acceptance role is a temporary
exception for the migration: it ends with it, never extends to constitutional
decisions, and changes no role definition elsewhere. Outside the migration the
repository owner accepts. Acceptance is written in the record's own Status
section with its date and who accepted it.

Records copied or transcribed from the source keep the ratification they
already carry; reviewing that a copy is faithful is not an acceptance of the
decision.

Scientific evidence and experiment records are **not** kept here;
they stay with the scientific apparatus that produced them and are linked,
never restated as a second source of truth.

> Status: bootstrap. The registry now documents initial Biopeia mechanisms.
> Those scoped records do not establish that any extracted repository
> conforms to the Biopeia target architecture.

## Layout

| Path | Purpose |
|---|---|
| `explanation/` | Explanatory documents. Created with the first documented unit |
| `technical/adr/`, `technical/design/` | Decision records and design documents |
| `registry/schema.yaml` | Closed vocabularies: domains and their component prefixes, statuses, state owners, lifecycle values |
| `registry/coverage.yaml` | Canonical units: owner, explanation, and the code, tests, design and decisions each is traced to |
| `registry/designs.yaml` | Design register: document status, implementation status and architecture scope of every design |
| `registry/contracts.yaml` | Cross-domain contracts: parties, how the two sides are bound in code, governing decisions, evidence and findings |
| `registry/findings.yaml` | Findings discovered while documenting, classified, with the issue raised for each material one |
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

The design register is the only authority for the state of a design. It keeps
three independent axes: whether the document is approved, whether Biopeia code
implements it, and whether it describes the current, target or historical
architecture. An approved design is therefore never, by that fact, an
implemented one. Design documents do not declare these states themselves, and
the validator rejects one that does.

A component's state is described by dimensions that depend on which domain
owns it. Organism and Embodiment components use the lifecycle axes (birth,
checkpoint, restart, re-embodiment, reproduction). World components answer
three questions instead: is the state durable, is it part of a causal cut,
and what can a failed transition leave behind. Other domains have no required
dimensions yet; none is defined before components of that domain have been
documented.

Where one domain relies on another, the reliance is recorded in
`registry/contracts.yaml`: who the parties are, which decisions govern it,
which tests exercise it, and how the two sides are actually bound in code
(one shared definition, methods that merely match by name, separate
definitions held together by convention, or a meeting that happens only in a
test fixture). That file describes; it defines no contract and has no
authority over any.

Documentation work records what it finds and fixes nothing. Each finding is
classified in `registry/findings.yaml`; a material one is raised as an issue
in the repository that owns the code and linked from its entry. A finding
describes the code at one commit. It is not a decision and creates no
requirement by itself.

`.local/` is ignored by Git. It may hold a local reference copy of the source
repository's documentation; nothing in it is Biopeia documentation.

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

CI runs two jobs. `registry` needs only this repository and blocks on registry
integrity. `cross-repository` clones the seven domain repositories with a
short-lived token from the read-only `biopeia-ci-read` GitHub App
(`CI_READ_APP_ID` variable, `CI_READ_APP_PRIVATE_KEY` secret), blocks when a
reference into them does not resolve, and reports staleness in the job summary
without blocking. It can also be started by hand, since a unit becomes stale
when a domain repository changes, not when this one does. References to
`symbiont-lab` are never resolved in CI. No domain repository runs a
documentation check.
