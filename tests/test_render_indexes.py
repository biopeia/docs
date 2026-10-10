from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import render_indexes  # noqa: E402
from validate_registry import broken_links, load_registry  # noqa: E402


def test_indexes_on_disk_are_current():
    assert render_indexes.main(["--check"]) == 0


def test_every_explanation_directory_has_an_index_in_reading_order():
    pages = render_indexes.render()
    directories = {p.name for p in (ROOT / "explanation").iterdir() if p.is_dir()}
    assert {f"explanation/{d}/README.md" for d in directories} <= set(pages)
    world = pages["explanation/world/README.md"]
    assert world.index("genesis-and-rosters.md") < world.index("recovery.md")
    for heading in ("Purpose", "Start here", "Reading order", "Canonical documents", "Related domains",
                    "Designs", "Decision records", "Open findings"):
        assert f"## {heading}" in world


def test_indexes_name_every_unit_document_and_have_no_broken_link():
    pages = "\n".join(render_indexes.render().values())
    for unit in load_registry(ROOT / "registry")["coverage"].values():
        for rel in unit["canonical_docs"]:
            assert Path(rel).name in pages
    assert broken_links(ROOT) == []
