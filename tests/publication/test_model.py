from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "publication"))

from model import ManifestError, load_manifest, manifest_errors  # noqa: E402


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
    assert manifest_errors(load_manifest(), ROOT) == []


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
