from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "publication"))

import pdf  # noqa: E402
import publish  # noqa: E402
import qa  # noqa: E402

needs_renderer = pytest.mark.skipif(
    not pdf.available(),
    reason="LibreOffice or pdftotext is not installed; publication.yml installs both",
)

TOC = [
    {"bookmark": "s1", "level": 1, "text": "Part I — World"},
    {"bookmark": "c1", "level": 2, "text": "1. The causal journal"},
    {"bookmark": "c2", "level": 2, "text": "2. Recovery, and what a failed transition leaves behind"},
]


def test_locate_skips_the_contents_list_and_prose_mentions():
    pages = [
        "Title page",
        "Contents\nPart I — World ..... 000\n1. The causal journal ..... 000\n"
        "2. Recovery, and what a failed transition\nleaves behind ..... 000",
        "Part I — World",
        "1. The causal journal\nSee Recovery, and what a failed transition leaves behind.",
        "more of the journal, where the ﬁrst record is",
        "2. Recovery, and what a failed\ntransition leaves behind\nText.",
    ]
    assert pdf.locate(TOC, pages) == {"s1": 3, "c1": 4, "c2": 6}


def test_locate_fails_when_a_heading_is_absent():
    with pytest.raises(pdf.PdfError, match="the body"):
        pdf.locate(TOC[:1], ["Contents Part I — World 000"])


def test_pagination_check_reports_moved_headings():
    first = {"s1": 3, "c1": 4, "c2": 6}
    assert qa.check_pagination(TOC, first, dict(first), 6, 6) == []
    problems = qa.check_pagination(TOC, first, {"s1": 3, "c1": 4, "c2": 7}, 6, 7)
    assert any("page count changed" in p for p in problems)
    assert any("listed on page 6 but is on page 7" in p for p in problems)


def test_projection_only_build_writes_no_document(tmp_path, monkeypatch):
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "0")
    assert publish.main(["--no-pdf", "--check", "--output", str(tmp_path)]) == 0
    assert sorted(p.name for p in tmp_path.iterdir()) == ["biopeia-master.json", "publication-manifest.json"]
    record = json.loads((tmp_path / "publication-manifest.json").read_text())
    assert record["generated_at"] == "1970-01-01T00:00:00Z" and "pages" not in record
    assert record["edition"] == "working"


def test_published_edition_refuses_unresolved_or_modified_sources(tmp_path, capsys):
    # No --repos-root: the domain repositories are not resolved.
    assert publish.main(["--no-pdf", "--release", "--output", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "a published edition needs every source at a clean revision" in out
    assert "world: not resolved to a revision" in out and not list(tmp_path.iterdir())
    sources = {"docs": {"state": "clean"}, "world": {"state": "modified"}}
    assert publish.unclean_sources(sources) == ["world: has local modifications"]


def test_build_without_libreoffice_fails_closed(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(pdf, "soffice", lambda: None)
    assert publish.main(["--output", str(tmp_path)]) == 1
    assert "LibreOffice" in capsys.readouterr().out and not list(tmp_path.iterdir())


@needs_renderer
def test_full_build_has_real_page_numbers_and_a_truthful_manifest(tmp_path):
    assert publish.main(["--check", "--output", str(tmp_path)]) == 0
    record = json.loads((tmp_path / "publication-manifest.json").read_text())
    assert set(record["artifacts"]) == {"biopeia-master.json", "Biopeia-Master.docx", "Biopeia-Master.pdf"}
    for name, artifact in record["artifacts"].items():
        data = (tmp_path / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == artifact["sha256"] and len(data) == artifact["bytes"]
    assert record["projection_digest"] == record["artifacts"]["biopeia-master.json"]["sha256"]
    assert set(record["sources"]) == {"docs", "organism", "embodiment", "environment", "world", "modality", "observation", "lab"}

    pages = pdf.page_texts((tmp_path / "Biopeia-Master.pdf").read_bytes())
    assert len(pages) == record["pages"] > 50
    contents = " ".join(" ".join(pages[1:4]).split())
    assert "000" not in contents
    # The page printed beside a chapter in the contents list is the page it starts on.
    title = re.search(r"\d+\. World recovery", contents).group(0)
    printed = int(contents.split(title, 1)[1].lstrip(". ").split()[0])
    assert title in " ".join(pages[printed - 1].split())
