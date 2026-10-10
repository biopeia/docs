from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "publication"))

from model import GENERATED_SECTIONS, load_manifest, sections  # noqa: E402
from projection import GENERATORS, ProjectionError, build_projection, projection_bytes  # noqa: E402
from validate_registry import load_registry  # noqa: E402


@pytest.fixture(scope="module")
def projection():
    return build_projection()


def chapters(projection):
    return [c for s in projection["sections"] for c in s["chapters"]]


def test_every_generated_section_has_a_generator():
    assert set(GENERATORS) == set(GENERATED_SECTIONS)


def test_projection_is_deterministic(projection):
    assert projection_bytes(build_projection()) == projection_bytes(projection)


def test_projection_follows_the_manifest_order(projection):
    wanted = [rel for s in sections(load_manifest()) for rel in s.get("chapters") or []]
    assert [c["source"] for c in chapters(projection) if not c["generated"]] == wanted
    assert [s["id"] for s in projection["sections"]] == [s["id"] for s in sections(load_manifest())]


def test_publication_opens_with_the_system_view(projection):
    assert projection["sections"][0]["id"] == "reader-guide"
    first = next(s for s in projection["sections"] if s["group"] == "parts")["chapters"]
    ids = [c["id"] for c in first]
    assert {"generated-domains", "explanation-biopeia-one-step-across-the-domains"} <= set(ids)
    assert ids.index("explanation-biopeia-one-step-across-the-domains") < ids.index("generated-domains")


def test_chapter_title_is_lifted_out_of_the_body(projection):
    chapter = next(c for c in chapters(projection) if c["source"] == "explanation/world/recovery.md")
    assert chapter["title"] and not chapter["markdown"].startswith("# ")
    assert chapter["base"] == "explanation/world"


def test_registry_sections_reflect_the_registry(projection):
    reg = load_registry(ROOT / "registry")
    by_id = {c["id"]: c["markdown"] for c in chapters(projection)}
    for contract in reg["contracts"].values():
        assert f"## {contract['title']}" in by_id["generated-contracts"]
    for cid, component in reg["components"].items():
        assert f"### `{cid}` — " in by_id["generated-components"]
        assert f"| Unit | `{component['coverage_unit']}` |" in by_id["generated-components"]
    assert projection["inventory"]["Components"] == len(reg["components"])
    placed = sum(len(s.get("chapters") or []) for s in sections(load_manifest()))
    assert projection["inventory"]["Chapters taken from documents"] == placed
    empty = {c["id"] for c in chapters(projection) if c.get("empty")}
    assert empty == {f"generated-{name}" for name in ("notation", "parameters", "metrics") if not reg[name]}
    for param in reg["parameters"].values():
        assert f"`{param['symbol']}`" in by_id["generated-parameters"]
    for metric in reg["metrics"]:
        assert f"`{metric}`" in by_id["generated-metrics"]
    for symbol in reg["notation"]:
        assert f"**{symbol}**" in by_id["generated-notation"]
    # Reverse index: a record lists the units that cite it, a component the contracts it is party to.
    assert "| Cited by |" in by_id["generated-decisions"] and "World causal journal" in by_id["generated-decisions"]
    assert "| Contracts |" in by_id["generated-components"]
    assert "ADR-0073" in by_id["generated-decisions"]


def test_findings_register_is_not_published(projection):
    reg = load_registry(ROOT / "registry")
    text = "\n".join(c["markdown"] for c in chapters(projection) if c["generated"])
    finding = next(iter(reg["findings"].values()))
    assert " ".join(finding["summary"].split())[:80] not in " ".join(text.split())


def test_unresolved_repositories_are_said_to_be_unresolved(projection):
    assert projection["sources"]["world"]["revision"] is None
    assert projection["sources"]["world"]["state"] == "unresolved"
    assert projection["sources"]["world"]["reviewed_at"]


def copy_sources(tmp_path: Path) -> Path:
    for name in ("registry", "explanation", "technical", "reference", "publication"):
        shutil.copytree(ROOT / name, tmp_path / name)
    return tmp_path


def build_in(root: Path):
    return build_projection(root / "registry", root, root / "publication" / "biopeia-master.yaml")


def test_copy_outside_git_builds_with_unresolved_revision(tmp_path):
    built = build_in(copy_sources(tmp_path))
    assert built["sources"]["docs"] == {"revision": None, "state": "unresolved", "committed_on": None}
    assert built["release"] == {"id": "unversioned", "date": None, "numbered": False}


def test_release_is_the_day_and_revision_of_the_documentation(projection):
    docs = projection["sources"]["docs"]
    assert projection["release"]["id"].startswith(f"{docs['committed_on'].replace('-', '.')}-{docs['revision'][:7]}")


def test_broken_registry_fails_closed(tmp_path):
    root = copy_sources(tmp_path)
    (root / "explanation" / "world" / "recovery.md").unlink()
    with pytest.raises(ProjectionError, match="registry validation failed"):
        build_in(root)


def test_unplaced_document_fails_closed(tmp_path):
    root = copy_sources(tmp_path)
    (root / "explanation" / "world" / "new-thing.md").write_text("# New thing\n", encoding="utf-8")
    with pytest.raises(ProjectionError, match="neither a chapter nor excluded"):
        build_in(root)


def test_tagged_commit_is_the_numbered_release_and_needs_its_history_entry(tmp_path):
    from projection import ProjectionError as Error, load_history, release_of

    docs = {"revision": "a" * 40, "state": "clean", "committed_on": "2026-10-31"}
    history = [{"id": "2026.10.1", "date": "2026-10-31", "summary": "First."}]
    assert release_of(docs, history, "docs-v2026.10.1") == {"id": "2026.10.1", "date": "2026-10-31", "numbered": True}
    assert release_of(docs, history, None)["id"] == "2026.10.31-aaaaaaa"
    assert release_of({**docs, "state": "modified"}, history, "docs-v2026.10.1")["numbered"] is False
    with pytest.raises(Error, match="no entry"):
        release_of(docs, history, "docs-v2026.11.1")
    (tmp_path / "publication").mkdir()
    (tmp_path / "publication" / "releases.yaml").write_text("releases:\n  - {id: '1', date: '2026-10-31', summary: x}\n")
    with pytest.raises(Error, match="malformed"):
        load_history(tmp_path)


def test_no_release_has_been_cut(projection):
    assert projection["history"] == [] and projection["release"]["numbered"] is False
