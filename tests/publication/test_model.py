from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "publication"))
from model import (  # noqa: E402
    DEFAULT_MANIFESTS,
    MANIFEST,
    TECHNICAL_REFERENCE_MANIFEST,
    ManifestError,
    corpus_coverage_errors,
    load_manifest,
    manifest_errors,
)


def write(root: Path, manifest: dict) -> Path:
    for rel in ("explanation/world/a.md", "explanation/world/b.md", "explanation/world/README.md"):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text("# Title\n", encoding="utf-8")
    path = root / "manifest.yaml"
    path.write_text(yaml.safe_dump(manifest), encoding="utf-8")
    return path


def manifest(**overrides) -> dict:
    base = {
        "publication": {"id": "p", "title": "P", "output": "P"},
        "parts": [
            {"id": "world", "title": "World", "chapters": ["explanation/world/a.md", "explanation/world/b.md"]}
        ],
    }
    return {**base, **overrides}


def test_repository_manifest_is_publishable():
    assert manifest_errors(load_manifest(MANIFEST), ROOT) == []


def test_technical_reference_manifest_is_publishable():
    assert manifest_errors(load_manifest(TECHNICAL_REFERENCE_MANIFEST), ROOT) == []


def test_all_default_manifests_are_publishable():
    for m in DEFAULT_MANIFESTS:
        assert manifest_errors(load_manifest(m), ROOT) == []


def test_default_manifests_cover_entire_corpus():
    manifests = [load_manifest(m) for m in DEFAULT_MANIFESTS]
    assert corpus_coverage_errors(manifests, ROOT) == []


def test_corpus_coverage_fails_closed_if_document_or_section_missing(tmp_path):
    (tmp_path / "reference").mkdir(parents=True)
    (tmp_path / "reference" / "extra.md").write_text("# Extra\n", encoding="utf-8")
    manifests = [{"publication": {"id": "m"}, "parts": [{"id": "p", "title": "P", "chapters": []}]}]
    errors = corpus_coverage_errors(manifests, tmp_path)
    assert any("reference/extra.md" in err for err in errors)
    assert any("canonical generated section is not published" in err for err in errors)


def test_valid_manifest_loads_and_readme_is_not_a_chapter(tmp_path):
    assert load_manifest(write(tmp_path, manifest()), tmp_path)["publication"]["id"] == "p"


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"parts": [{"id": "w", "title": "W", "chapters": ["explanation/world/a.md"]}]}, "neither a chapter nor excluded"),
        (
            {"parts": [{"id": "w", "title": "W", "chapters": ["explanation/world/a.md", "explanation/world/b.md", "explanation/world/missing.md"]}]},
            "does not exist",
        ),
        (
            {"parts": [{"id": "w", "title": "W", "chapters": ["explanation/world/a.md", "explanation/world/a.md", "explanation/world/b.md"]}]},
            "more than once",
        ),
        (
            {"parts": [{"id": "w", "title": "W", "chapters": ["explanation/world/a.md", "explanation/world/b.md"], "generated": ["nope"]}]},
            "unknown generated section",
        ),
        (
            {"parts": [{"id": "w", "title": "W", "chapters": ["explanation/world/a.md", "explanation/world/b.md", "registry/schema.yaml"]}]},
            "must live under",
        ),
        ({"excluded": [{"path": "explanation/world/a.md"}]}, "needs a path and a reason"),
        ({"excluded": [{"path": "explanation/world/a.md", "reason": "x"}]}, "both a chapter and excluded"),
    ],
)
def test_manifest_fails_closed(tmp_path, change, message):
    with pytest.raises(ManifestError, match=message):
        load_manifest(write(tmp_path, manifest(**change)), tmp_path)


def test_excluded_document_with_reason_is_accepted(tmp_path):
    data = manifest(
        parts=[{"id": "w", "title": "W", "chapters": ["explanation/world/a.md"]}],
        excluded=[{"path": "explanation/world/b.md", "reason": "superseded draft"}],
    )
    load_manifest(write(tmp_path, data), tmp_path)


def test_a_selection_need_not_place_every_document(tmp_path):
    data = manifest(
        publication={"id": "p", "title": "P", "output": "P", "selection": True},
        parts=[{"id": "w", "title": "W", "chapters": ["explanation/world/a.md"]}],
    )
    load_manifest(write(tmp_path, data), tmp_path)


def test_howto_and_tutorial_chapters_are_accepted_by_model(tmp_path):
    (tmp_path / "how-to" / "operator").mkdir(parents=True)
    (tmp_path / "tutorials" / "getting-started").mkdir(parents=True)
    (tmp_path / "how-to" / "operator" / "run.md").write_text("# Run\n", encoding="utf-8")
    (tmp_path / "tutorials" / "getting-started" / "start.md").write_text("# Start\n", encoding="utf-8")

    data = {
        "publication": {"id": "ops", "title": "Ops", "output": "Ops", "selection": True},
        "parts": [
            {"id": "guides", "title": "Guides", "chapters": ["how-to/operator/run.md"]},
            {"id": "learn", "title": "Learn", "chapters": ["tutorials/getting-started/start.md"]},
        ],
    }
    m = write(tmp_path, data)
    loaded = load_manifest(m, tmp_path)
    assert len(loaded["parts"]) == 2


def test_corpus_coverage_fails_closed_for_howto_and_tutorials(tmp_path):
    (tmp_path / "how-to" / "operator").mkdir(parents=True)
    (tmp_path / "tutorials" / "getting-started").mkdir(parents=True)
    (tmp_path / "how-to" / "operator" / "orphan_guide.md").write_text("# Orphan\n", encoding="utf-8")
    (tmp_path / "tutorials" / "getting-started" / "orphan_tut.md").write_text("# Orphan Tut\n", encoding="utf-8")

    manifests = [{"publication": {"id": "m"}, "parts": [{"id": "p", "title": "P", "chapters": []}]}]
    errors = corpus_coverage_errors(manifests, tmp_path)
    assert any("how-to/operator/orphan_guide.md" in err for err in errors)
    assert any("tutorials/getting-started/orphan_tut.md" in err for err in errors)
