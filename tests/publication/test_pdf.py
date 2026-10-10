from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "publication"))

import mermaid  # noqa: E402
import pdf  # noqa: E402
import publish  # noqa: E402
import qa  # noqa: E402

needs_renderer = pytest.mark.skipif(
    not (pdf.available() and mermaid.available()),
    reason="LibreOffice, poppler or mermaid-cli is not installed; publication.yml installs them",
)

TOC = [
    {"bookmark": "s1", "level": 1, "text": "Part I — World"},
    {"bookmark": "s1c1", "level": 2, "text": "1. The causal journal"},
    {"bookmark": "s1c2", "level": 2, "text": "2. Recovery"},
]


def test_locate_reads_pages_from_destinations_and_fails_when_one_is_missing():
    assert pdf.locate(TOC, {"s1": 3, "s1c1": 3, "s1c2": 6, "other": 9}) == {"s1": 3, "s1c1": 3, "s1c2": 6}
    with pytest.raises(pdf.PdfError, match="2. Recovery"):
        pdf.locate(TOC, {"s1": 3, "s1c1": 3})


def test_density_check_fails_on_an_empty_page_and_reports_sparse_ones():
    limits = {"blank_page_chars": 120, "sparse_page_chars": 400, "max_sparse_share": 0.5}
    furniture = "Biopeia\nPart I\n{}\nWorking edition\nPage 1 of 4\n"
    pages = ["cover", furniture.format("x" * 900), furniture.format("y" * 200), furniture.format("one orphaned line of a chapter")]
    assert qa.body_characters(pages) == [0, 900, 200, 25]
    # A short last page of a section is how it ends; an orphaned line is a fault even there.
    problems, sparse = qa.check_density(pages, limits, terminal={3, 4})
    assert problems == ["page 4 holds only an orphaned line or two"] and sparse == [3, 4]
    # The same short page in the middle of a section is a fault.
    problems, _ = qa.check_density(pages[:3], limits, terminal=set())
    assert problems == ["page 3 is sparse in the middle of a section"]
    problems, _ = qa.check_density(pages[:3], {**limits, "max_sparse_share": 0.1}, terminal={3})
    assert problems == ["1 of 3 pages are sparse, more than the 10% allowed"]


def test_font_check_reports_a_typeface_the_style_does_not_name():
    allowed = ["Liberation Sans", "Liberation Mono", "DejaVu Sans"]
    assert qa.check_fonts(["LiberationSans-Bold", "LiberationMono", "DejaVuSans"], allowed) == []
    assert qa.check_fonts(["NotoColorEmoji"], allowed) == ["PDF uses a typeface the style does not name: NotoColorEmoji"]


def test_pagination_check_reports_moved_headings():
    first = {"s1": 3, "s1c1": 4, "s1c2": 6}
    assert qa.check_pagination(TOC, first, dict(first), 6, 6) == []
    problems = qa.check_pagination(TOC, first, {"s1": 3, "s1c1": 4, "s1c2": 7}, 6, 7)
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


def test_published_edition_refuses_links_it_could_not_check(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(publish, "unclean_sources", lambda sources: [])
    assert publish.main(["--no-pdf", "--release", "--output", str(tmp_path)]) == 1
    assert "links to code could not be checked" in capsys.readouterr().out


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

    rendered = (tmp_path / "Biopeia-Master.pdf").read_bytes()
    pages = pdf.page_texts(rendered)
    assert len(pages) == record["pages"] > 50
    start = next(i for i, page in enumerate(pages) if page.lstrip().startswith("Biopeia") and "\nContents\n" in page)
    contents = " ".join(" ".join(pages[start : start + 3]).split())
    assert "000" not in contents
    # The page printed beside a chapter in the contents list is the page it starts on.
    title = re.search(r"\d+\. World recovery", contents).group(0)
    printed = int(contents.split(title, 1)[1].lstrip(". ").split()[0])
    assert title in " ".join(pages[printed - 1].split())
    # Rendered only in the fallback typefaces, whatever this machine has installed.
    assert record["layout"]["typefaces"] == pdf.fonts_used(rendered)
    assert all(f.startswith(("LiberationSans", "LiberationMono", "DejaVuSans")) for f in record["layout"]["typefaces"])
    assert "\u200b" not in "".join(pages)
    assert "Page 1 of" not in pages[0] and f"Page 2 of {len(pages)}" in pages[1]
    assert record["release"]["id"] in pages[1]
    assert pdf.has_outline(rendered)
    assert pdf.properties(rendered)["Title"].startswith("Biopeia")
    # No domain checkout beside this build: links to code are made but not checked.
    assert record["links"]["unverified"] > 0 and record["links"]["verified"] > 0
    logo = record["style"]["logo"]
    assert hashlib.sha256((ROOT / logo["path"]).read_bytes()).hexdigest() == logo["sha256"]
