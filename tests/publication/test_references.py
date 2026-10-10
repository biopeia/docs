from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "publication"))

from references import GITHUB, ReferenceError, Resolver, slug, symbol_line  # noqa: E402
from validate_registry import load_registry  # noqa: E402


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.org", "-c", "commit.gpgsign=false", *args],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


@pytest.fixture
def world(tmp_path):
    """A `world` checkout with two commits: journal.py at both, late.py only at the second."""
    repo = tmp_path / "repos" / "world"
    (repo / "src").mkdir(parents=True)
    (repo / "tests").mkdir()
    git(repo, "init", "-q")
    (repo / "src" / "journal.py").write_text("LIMIT = 3\n\n\nclass Journal:\n    def append(self):\n        pass\n")
    (repo / "tests" / "test_journal.py").write_text("\ndef test_append_keeps_order():\n    pass\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "one")
    first = git(repo, "rev-parse", "HEAD")
    (repo / "src" / "late.py").write_text("x = 1\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "two")
    return tmp_path / "repos", first, git(repo, "rev-parse", "HEAD")


def resolver(repos_root, head=None):
    sources = {"docs": {"revision": None}, "world": {"revision": head}}
    return Resolver(load_registry(ROOT / "registry"), ROOT, repos_root, sources)


def test_symbol_line_finds_classes_members_and_constants():
    source = "LIMIT = 3\n\n\nclass Journal:\n    size: int = 0\n\n    def append(self):\n        pass\n"
    assert [symbol_line(source, s) for s in ("LIMIT", "Journal", "Journal.append", "Journal.size", "Absent")] == [1, 4, 7, 5, None]


def test_slug_matches_the_anchor_of_a_heading():
    assert slug("What it is") == "what-it-is"
    assert slug("The chain today, in one table") == "the-chain-today-in-one-table"


def test_code_is_linked_at_the_reviewed_revision_with_the_line_of_its_symbol(world):
    repos, first, head = world
    r = resolver(repos, head)
    found = r.code_token("world:src/journal.py::Journal.append", {"world": first})
    assert found == {"url": f"{GITHUB}/world/blob/{first}/src/journal.py#L5"}
    assert r.code_token("world:src", {"world": first}) == {"url": f"{GITHUB}/world/tree/{first}/src"}
    assert r.stats["verified"] == 2 and r.stats["unverified"] == 0


def test_file_added_after_the_review_is_linked_at_the_build_revision(world):
    repos, first, head = world
    r = resolver(repos, head)
    assert r.code_token("world:src/late.py", {"world": first}) == {"url": f"{GITHUB}/world/blob/{head}/src/late.py"}
    assert r.stats["at_build_revision"] == 1


def test_reference_to_nothing_fails(world):
    repos, first, head = world
    with pytest.raises(ReferenceError, match="world:src/absent.py does not exist"):
        resolver(repos, head).code_token("world:src/absent.py", {"world": first})


def test_cited_test_is_linked_to_its_definition(world):
    repos, first, head = world
    r = resolver(repos, head)
    assert r.code_token("test_append_keeps_order", {"world": first}) == {
        "url": f"{GITHUB}/world/blob/{first}/tests/test_journal.py#L2"}
    assert r.code_token("test_that_nobody_wrote", {"world": first}) is None and r.stats["tests_not_located"] == 1


def test_without_a_checkout_the_link_is_made_and_counted_unverified():
    r = resolver(None)
    sha = "a" * 40
    assert r.code_token("world:src/world/journal.py", {"world": sha}) == {
        "url": f"{GITHUB}/world/blob/{sha}/src/world/journal.py"}
    assert r.stats["unverified"] == 1
    assert r.code_token("world:src/world/journal.py", {}) is None and r.stats["without_revision"] == 1


def test_commits_issues_and_components():
    r = resolver(None)
    sha = "b" * 40
    assert r.code_token(f"world@{sha}", {}) == {"url": f"{GITHUB}/world/commit/{sha}", "label": "world@bbbbbbb"}
    assert r.plain_token("world#29") == {"url": f"{GITHUB}/world/issues/29"}
    component = next(iter(load_registry(ROOT / "registry")["components"]))
    assert r.plain_token(component) == {"component": component} == r.code_token(component, {})
    assert r.plain_token("ADR-0001") is None  # a historical record this repository does not hold
    assert r.code_token("not a reference", {}) is None


def test_chapter_collects_references_from_code_and_prose():
    r = resolver(None)
    found = r.chapter("See `world@" + "c" * 40 + "`, world#29 and `plain code`.", {})
    assert set(found) == {"world@" + "c" * 40, "world#29"}


def test_document_not_yet_committed_is_linked_and_counted_unverified(tmp_path):
    docs = tmp_path / "docs"
    (docs / "explanation").mkdir(parents=True)
    (docs / "technical" / "adr").mkdir(parents=True)
    git(docs, "init", "-q")
    (docs / "explanation" / "old.md").write_text("# Old\n")
    git(docs, "add", "-A")
    git(docs, "commit", "-qm", "one")
    head = git(docs, "rev-parse", "HEAD")
    (docs / "explanation" / "new.md").write_text("# New\n")
    r = Resolver(load_registry(ROOT / "registry"), docs, None, {"docs": {"revision": head}})
    assert r.blob("docs", "explanation/new.md", {}) == f"{GITHUB}/docs/blob/{head}/explanation/new.md"
    assert r.stats["unverified"] == 1
    with pytest.raises(ReferenceError):
        r.blob("docs", "explanation/absent.md", {})


def test_revision_is_shown_by_its_day_and_short_hash(world):
    repos, first, head = world
    r = resolver(repos, head)
    found = r.code_token(first, {})
    assert found["url"] == f"{GITHUB}/world/commit/{first}"
    assert re.fullmatch(r"\d{4}\.\d{2}\.\d{2}-" + first[:7], found["label"])
    assert re.fullmatch(r"world@\d{4}\.\d{2}\.\d{2}-" + first[:7], r.code_token(f"world@{first[:12]}", {})["label"])
