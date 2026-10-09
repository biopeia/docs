"""Checks for the registry validator.

The real registry starts empty, so the rules are exercised against a small
synthetic registry built in a temporary directory. Each sentinel corrupts that
registry in one way and asserts the validator names the defect.
"""

from __future__ import annotations

import copy
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import validate_registry as vr  # noqa: E402

GENOME_SOURCE = "class Genome:\n    min_support = 2\n"


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def example_registry(basis: str) -> dict[str, dict[str, Any]]:
    return {
        "coverage": {
            "concept.organism": {
                "kind": "concept",
                "title": "Organism",
                "status": "TARGET",
                "owner_domain": "organism",
                "canonical_docs": ["explanation/organism.md"],
            },
            "component.genome": {
                "kind": "component",
                "title": "Genome",
                "status": "CURRENT",
                "owner_domain": "organism",
                "participating_domains": ["embodiment"],
                "component_id": "ORG-GEN",
                "canonical_docs": ["explanation/organism.md"],
                "implementation": ["organism:src/organism/genome.py"],
                "adrs": ["symbiont-lab:docs/adr/ADR-0074.md", "docs:technical/adr/ADR-0001.md"],
                "depends_on": ["concept.organism"],
                "review": {
                    "status": "RECORDED",
                    "basis": {"organism": basis, "symbiont-lab": "80d372a"},
                },
            },
            "mechanism.inheritance": {
                "kind": "mechanism",
                "title": "Inheritance",
                "status": "DESIGN",
                "owner_domain": "organism",
                "canonical_docs": ["explanation/organism.md"],
                "design": ["docs:technical/design/genome/inheritance-v1.md"],
                "depends_on": ["component.genome"],
            },
        },
        "designs": {
            "design.genome.inheritance-v1": {
                "title": "Inheritance v1",
                "path": "technical/design/genome/inheritance-v1.md",
                "domain": "organism",
                "participating_domains": ["world"],
                "document_status": "approved",
                "implementation_status": "not_evaluated",
                "architecture_scope": "TARGET",
                "decision": {
                    "reference": "docs:technical/adr/ADR-0001.md",
                    "date": "2026-10-09",
                },
                "source": {
                    "repository": "symbiont-lab",
                    "commit": "80d372a",
                    "path": "docs/design/genome/genome-v3.md",
                },
            },
        },
        "components": {
            "ORG-GEN": {
                "coverage_unit": "component.genome",
                "name": "Genome",
                "authority": {
                    "owns": "heritable representation",
                    "may_decide": ["genotype structure"],
                    "must_not": ["contain acquired knowledge"],
                },
                "state": {"owner": "organism", "family": "identity_longitudinal"},
                "lifecycle": {
                    "birth": "initialize",
                    "checkpoint": "preserve",
                    "restart": "preserve",
                    "reembodiment": "preserve",
                    "reproduction": "inherit_allowed",
                },
                "consumers": ["mechanism.inheritance"],
            }
        },
        "parameters": {
            "genome.min_support": {
                "owner": "component.genome",
                "symbol": "N_supp",
                "dimension": "count",
                "unit": "1",
                "source": "CODE",
                "implementation": {
                    "ref": "organism:src/organism/genome.py",
                    "symbol": "Genome.min_support",
                },
            }
        },
        "metrics": {
            "genome.diversity": {
                "owner_domain": "lab",
                "class": "scientific_evaluation",
                "definition": "Allele diversity across a population.",
                "unit": "1",
                "consumer": "component.genome",
            }
        },
        "notation": {
            "G_t": {
                "meaning": "Genome at organism time t.",
                "scope": "global",
                "owner": "formal-model",
                "aliases": ["G(t)"],
                "forbidden_meanings": ["phenotype"],
            }
        },
        "glossary": {
            "genotype": {
                "term": "Genotype",
                "definition": "The heritable representation carried by one organism lineage.",
                "distinguishes_from": ["phenotype"],
                "owners": ["component.genome"],
                "canonical_refs": ["explanation/organism.md"],
            },
            "phenotype": {
                "term": "Phenotype",
                "definition": "The expressed organization that develops from a genotype.",
                "distinguishes_from": ["genotype"],
                "owners": ["concept.organism"],
                "canonical_refs": ["explanation/organism.md"],
            },
        },
    }


class Workspace:
    def __init__(self, root: Path) -> None:
        self.registry = root / "docs" / "registry"
        self.docs = root / "docs"
        self.repos = root / "repos"
        self.organism = self.repos / "organism"
        (self.docs / "explanation").mkdir(parents=True)
        (self.docs / "explanation" / "organism.md").write_text("# Organism\n")
        (self.docs / "technical" / "adr").mkdir(parents=True)
        (self.docs / "technical" / "adr" / "ADR-0001.md").write_text("# ADR-0001\n")
        self.design_doc = self.docs / "technical" / "design" / "genome" / "inheritance-v1.md"
        self.design_doc.parent.mkdir(parents=True)
        self.design_doc.write_text("---\ntitle: Inheritance v1\n---\n# Inheritance v1\n")
        self.registry.mkdir()
        shutil.copy(ROOT / "registry" / "schema.yaml", self.registry / "schema.yaml")
        (self.organism / "src" / "organism").mkdir(parents=True)
        (self.organism / "src" / "organism" / "genome.py").write_text(GENOME_SOURCE)
        git(self.organism, "init", "-q")
        git(self.organism, "add", "-A")
        git(self.organism, "commit", "-q", "-m", "genome")
        self.basis = git(self.organism, "rev-parse", "HEAD")
        self.data = example_registry(self.basis)
        self.write()

    def write(self) -> None:
        for name, key in vr.REGISTRY_KEYS.items():
            content = {"schema_version": 1, key: self.data[name]}
            (self.registry / f"{name}.yaml").write_text(yaml.safe_dump(content))

    def validate(self, with_repos: bool = True) -> tuple[list[str], list[str]]:
        return vr.validate(self.registry, self.docs, self.repos if with_repos else None)


@pytest.fixture
def ws(tmp_path: Path) -> Workspace:
    return Workspace(tmp_path)


def test_repository_registry_is_valid() -> None:
    errors, unresolved = vr.validate(ROOT / "registry", ROOT)
    assert errors == []
    assert unresolved == []


def test_example_registry_is_valid(ws: Workspace) -> None:
    errors, unresolved = ws.validate()
    assert errors == []
    # symbiont-lab has no checkout under the repositories root.
    assert unresolved == ["Unit component.genome: adrs symbiont-lab:docs/adr/ADR-0074.md"]


def test_missing_checkout_is_unresolved_not_an_error(ws: Workspace) -> None:
    errors, unresolved = ws.validate(with_repos=False)
    assert errors == []
    assert len(unresolved) == 3


def test_design_document_must_not_declare_its_own_status(ws: Workspace) -> None:
    ws.design_doc.write_text("---\ntitle: Inheritance v1\nstatus: approved\n---\n# Inheritance v1\n")
    errors, _ = ws.validate()
    assert any("front matter declares a status" in e for e in errors)


def test_every_design_document_needs_a_register_entry(ws: Workspace) -> None:
    (ws.design_doc.parent / "unregistered.md").write_text("# Unregistered\n")
    errors, _ = ws.validate()
    assert any("unregistered.md has no entry in designs.yaml" in e for e in errors)


def test_two_entries_cannot_register_the_same_document(ws: Workspace) -> None:
    ws.data["designs"]["design.genome.copy-v1"] = dict(ws.data["designs"][D])
    ws.write()
    errors, _ = ws.validate()
    assert any("path already registered by" in e for e in errors)


def test_duplicate_yaml_keys_are_rejected(ws: Workspace) -> None:
    (ws.registry / "metrics.yaml").write_text("schema_version: 1\nmetrics: {}\nmetrics: {}\n")
    errors, _ = ws.validate()
    assert any("Duplicate YAML key" in e for e in errors)


def _set(registry: str, entry: str, path: str, value: Any) -> Callable[[dict], None]:
    def mutate(data: dict) -> None:
        target = data[registry][entry]
        *parents, leaf = path.split(".")
        for key in parents:
            target = target[key]
        if value is None:
            target.pop(leaf, None)
        else:
            target[leaf] = value

    return mutate


def _rename_component(data: dict) -> None:
    data["components"]["EMB-GEN"] = data["components"].pop("ORG-GEN")
    data["coverage"]["component.genome"]["component_id"] = "EMB-GEN"


D = "design.genome.inheritance-v1"

SENTINELS: list[tuple[Callable[[dict], None], str]] = [
    (_set("coverage", "component.genome", "kind", "module"), "kind 'module' not in"),
    (_set("coverage", "component.genome", "status", "DONE"), "status 'DONE' not in"),
    (_set("coverage", "component.genome", "owner_domain", "symbiont"), "owner_domain 'symbiont'"),
    (
        _set("coverage", "component.genome", "participating_domains", ["organism"]),
        "repeated in participating_domains",
    ),
    (_set("coverage", "component.genome", "canonical_docs", ["explanation/missing.md"]), "missing document"),
    (_set("coverage", "component.genome", "canonical_docs", None), "canonical_docs entry is required"),
    (
        _set("coverage", "component.genome", "canonical_docs", ["technical/adr/ADR-0001.md"]),
        "canonical_docs must live under explanation/",
    ),
    (
        _set("coverage", "component.genome", "adrs", ["docs:explanation/organism.md"]),
        "adrs must live under technical/adr/",
    ),
    (
        _set("coverage", "component.genome", "design", ["docs:technical/design/absent.md"]),
        "references missing path",
    ),
    (
        _set("coverage", "component.genome", "design", ["docs:technical/design/genome/other.md"]),
        "is not in designs.yaml",
    ),
    (_set("designs", D, "document_status", "accepted"), "document_status 'accepted' not in"),
    (_set("designs", D, "implementation_status", "done"), "implementation_status 'done' not in"),
    (_set("designs", D, "implementation_status", None), "implementation_status None not in"),
    (_set("designs", D, "architecture_scope", "FUTURE"), "architecture_scope 'FUTURE' not in"),
    (_set("designs", D, "domain", "runtime"), "domain 'runtime' not in"),
    (_set("designs", D, "participating_domains", ["organism"]), "invalid participating_domain"),
    (_set("designs", D, "path", "explanation/organism.md"), "path must live under technical/design/"),
    (_set("designs", D, "path", "technical/design/genome/gone.md"), "missing document"),
    (_set("designs", D, "decision", None), "requires decision.reference"),
    (_set("designs", D, "decision.date", "October 2026"), "requires decision.date"),
    (
        _set("designs", D, "decision.reference", "docs:technical/adr/ADR-9999.md"),
        "references missing path",
    ),
    (_set("designs", D, "document_status", "superseded"), "requires superseded_by"),
    (_set("designs", D, "source.commit", "main"), "source.commit is not a commit SHA"),
    (_set("designs", D, "source.repository", "elsewhere"), "source.repository 'elsewhere'"),
    (
        _set("coverage", "component.genome", "implementation", ["src/organism/genome.py"]),
        "is not '<repository>:<path>'",
    ),
    (
        _set("coverage", "component.genome", "implementation", ["physics:src/x.py"]),
        "unknown repository 'physics'",
    ),
    (
        _set("coverage", "component.genome", "implementation", ["organism:src/gone.py"]),
        "references missing path",
    ),
    (
        _set("coverage", "component.genome", "tests", ["symbiont-lab:tests/test_genome.py"]),
        "cites historical repository",
    ),
    (
        _set("coverage", "component.genome", "review.basis", {"organism": "abc1234"}),
        "no commit for repository 'symbiont-lab'",
    ),
    (
        _set("coverage", "component.genome", "review.basis.organism", "main"),
        "is not a commit SHA",
    ),
    (_set("coverage", "component.genome", "review.status", "APPROVED"), "review.status 'APPROVED'"),
    (_set("coverage", "component.genome", "depends_on", ["concept.absent"]), "non-existent unit"),
    (_set("coverage", "component.genome", "component_id", None), "requires exactly one component_id"),
    (_set("coverage", "concept.organism", "component_id", "ORG-ORG"), "only component units"),
    (_rename_component, "identifier must be 'ORG-<CODE>'"),
    (_set("components", "ORG-GEN", "coverage_unit", "concept.organism"), "bidirectional mismatch"),
    (_set("components", "ORG-GEN", "state.owner", "embodiment"), "declares state owned by 'embodiment'"),
    (_set("components", "ORG-GEN", "state.owner", None), "state.owner None not in"),
    (_set("components", "ORG-GEN", "state.family", "eternal"), "state.family 'eternal'"),
    (_set("components", "ORG-GEN", "authority.must_not", []), "authority.must_not is missing"),
    (_set("components", "ORG-GEN", "lifecycle.reembodiment", "forget"), "lifecycle.reembodiment"),
    (_set("components", "ORG-GEN", "consumers", ["component.absent"]), "consumer 'component.absent'"),
    (_set("parameters", "genome.min_support", "owner", "component.absent"), "does not resolve"),
    (_set("parameters", "genome.min_support", "source", "GUESS"), "source 'GUESS'"),
    (_set("parameters", "genome.min_support", "unit", None), "missing required field 'unit'"),
    (
        _set("parameters", "genome.min_support", "implementation.symbol", "Genome.absent"),
        "symbol 'Genome.absent' not found",
    ),
    (_set("metrics", "genome.diversity", "owner_domain", "organism"), "must have owner_domain 'lab'"),
    (_set("metrics", "genome.diversity", "class", "vanity"), "class 'vanity'"),
    (_set("notation", "G_t", "forbidden_meanings", []), "forbidden_meanings must be"),
    (_set("notation", "G_t", "scope", "universal"), "invalid scope"),
    (_set("notation", "G_t", "aliases", ["G_t", "G_t'", "G_t'"]), "collides with alias"),
    (_set("glossary", "genotype", "definition", "Too short."), "at least 40 characters"),
    (_set("glossary", "genotype", "distinguishes_from", ["genotype"]), "contains itself"),
    (_set("glossary", "genotype", "distinguishes_from", ["allele"]), "unknown glossary term"),
    (_set("glossary", "genotype", "owners", ["component.absent"]), "missing from coverage.yaml"),
    (_set("glossary", "genotype", "canonical_refs", []), "canonical_refs entry is required"),
]


@pytest.mark.parametrize(("mutate", "expected"), SENTINELS, ids=[s[1] for s in SENTINELS])
def test_sentinel_detects_corruption(
    ws: Workspace, mutate: Callable[[dict], None], expected: str
) -> None:
    ws.data = copy.deepcopy(ws.data)
    mutate(ws.data)
    ws.write()
    errors, _ = ws.validate()
    assert any(expected in e for e in errors), errors


def test_component_unit_without_registry_entry(ws: Workspace) -> None:
    ws.data["components"].clear()
    ws.write()
    errors, _ = ws.validate()
    assert any("has no entry in components.yaml" in e for e in errors)


def test_unit_is_not_stale_at_its_review_basis(ws: Workspace) -> None:
    assert vr.find_stale_units(ws.registry, ws.repos, against="HEAD") == ({}, {})


def test_source_change_after_basis_marks_unit_and_dependents_stale(ws: Workspace) -> None:
    (ws.organism / "src" / "organism" / "genome.py").write_text(GENOME_SOURCE + "# changed\n")
    (ws.organism / "README.md").write_text("unrelated\n")
    git(ws.organism, "add", "-A")
    git(ws.organism, "commit", "-q", "-m", "change genome")

    stale, downstream = vr.find_stale_units(ws.registry, ws.repos, against="HEAD")

    assert stale == {
        "component.genome": [f"organism:src/organism/genome.py changed since {ws.basis}"]
    }
    assert downstream == {"mechanism.inheritance": ["component.genome"]}


def test_unknown_basis_commit_is_reported_not_ignored(ws: Workspace) -> None:
    ws.data["coverage"]["component.genome"]["review"]["basis"]["organism"] = "0" * 40
    ws.write()
    stale, _ = vr.find_stale_units(ws.registry, ws.repos, against="HEAD")
    assert "cannot compare" in stale["component.genome"][0]


def test_cli_passes_on_repository_registry(capsys: pytest.CaptureFixture[str]) -> None:
    assert vr.main([]) == 0
    assert "Registry integrity: PASS" in capsys.readouterr().out
