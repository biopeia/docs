from __future__ import annotations

import io
import struct
import sys
import zipfile
import zlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "publication"))

import markdown  # noqa: E402
import mermaid  # noqa: E402
import qa  # noqa: E402
from docx import PAGE_PLACEHOLDER, build_docx  # noqa: E402
from projection import build_projection  # noqa: E402


def png(width: int, height: int) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    rows = b"".join(b"\x00" + b"\xff" * width for _ in range(height))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))


def chapter(source: str, text: str, title: str = "Title") -> dict:
    return {"id": source.replace("/", "-").removesuffix(".md"), "title": title, "source": source,
            "generated": False, "sha256": "0", "base": str(Path(source).parent), "markdown": text}


def small(*chapters: dict) -> dict:
    return {
        "publication": {"id": "p", "title": "P", "subtitle": "S", "output": "P"},
        "sources": {"docs": {"revision": None, "state": "unresolved"}},
        "sections": [
            {"id": "one", "title": "One", "group": "parts", "chapters": list(chapters)},
            {"id": "app", "title": "Catalog", "group": "appendices", "chapters": [chapter("reference/x.md", "Text.\n")]},
        ],
    }


def document_xml(data: bytes) -> str:
    return zipfile.ZipFile(io.BytesIO(data)).read("word/document.xml").decode("utf-8")


# --- Markdown -------------------------------------------------------------------


def test_markdown_blocks():
    blocks = markdown.parse(
        "Intro that\nwraps.\n\n## Head\n\n1. one\n   continued\n   - nested\n2. two\n\n"
        "| A | B |\n|---|---|\n| `x|y` | b \\| c |\n\n```text\n  keep  this\n```\n"
    )
    assert [b["type"] for b in blocks] == ["paragraph", "heading", "list", "table", "code"]
    assert blocks[0]["inlines"][0]["text"] == "Intro that wraps."
    items = blocks[2]["items"]
    assert [(i["level"], i["ordered"], i["number"]) for i in items] == [(0, True, 1), (1, False, None), (0, True, 2)]
    assert items[0]["inlines"][0]["text"] == "one continued"
    assert [c[0]["text"] for c in blocks[3]["rows"][0]] == ["x|y", "b | c"]
    assert blocks[4] == {"type": "code", "language": "text", "text": "  keep  this"}


def test_markdown_inline_styles_nest():
    runs = markdown.parse_inline("a **b `c`** *d* [e `f`](g.md#h) 2 * 3 * 4")
    assert [(r["text"], r["bold"], r["italic"], r["code"], r["href"]) for r in runs] == [
        ("a ", False, False, False, None),
        ("b ", True, False, False, None),
        ("c", True, False, True, None),
        (" ", False, False, False, None),
        ("d", False, True, False, None),
        (" ", False, False, False, None),
        ("e ", False, False, False, "g.md#h"),
        ("f", False, False, True, "g.md#h"),
        (" 2 * 3 * 4", False, False, False, None),
    ]


def test_markdown_numbered_line_does_not_break_a_paragraph():
    assert len(markdown.parse("It happened in\n2026. Nothing else.\n")) == 1


def test_markdown_unclosed_fence_is_an_error():
    with pytest.raises(markdown.MarkdownError):
        markdown.parse("```text\nnever closed\n")


# --- DOCX -----------------------------------------------------------------------


def test_real_publication_builds_a_sound_deterministic_package():
    projection = build_projection()
    first, toc = build_docx(projection)
    assert build_docx(projection)[0] == first
    assert qa.check_docx(first) == []
    chapters = sum(len(s["chapters"]) for s in projection["sections"] if s["group"] == "parts")
    assert len(toc) == len(projection["sections"]) + chapters
    assert [e["level"] for e in toc[:2]] == [1, 2]
    assert len({e["bookmark"] for e in toc}) == len(toc)


def test_links_between_published_chapters_stay_inside_the_document():
    text = "See [b](b.md#part), [gone](../../technical/x.md) and [web](https://example.org).\n"
    data, _ = build_docx(small(chapter("explanation/w/a.md", text), chapter("explanation/w/b.md", "B.\n")))
    xml = document_xml(data)
    assert 'w:anchor="chapter_explanation_w_b"' in xml
    assert "gone" in xml and "technical/x.md" not in xml
    rels = zipfile.ZipFile(io.BytesIO(data)).read("word/_rels/document.xml.rels").decode("utf-8")
    assert 'Target="https://example.org" TargetMode="External"' in rels
    assert qa.check_docx(data) == []


def test_contents_shows_placeholders_then_real_pages():
    projection = small(chapter("explanation/w/a.md", "A.\n"))
    draft, toc = build_docx(projection)
    assert document_xml(draft).count(f">{PAGE_PLACEHOLDER}<") == len(toc) == 3
    final, _ = build_docx(projection, pages={e["bookmark"]: 40 + i for i, e in enumerate(toc)})
    assert f">{PAGE_PLACEHOLDER}<" not in document_xml(final) and ">42<" in document_xml(final)


def test_single_chapter_appendix_has_one_heading():
    _, toc = build_docx(small(chapter("explanation/w/a.md", "A.\n")))
    assert [e["text"] for e in toc] == ["Part I — One", "1. Title", "Appendix A — Catalog"]


def test_numbered_lists_restart_and_keep_their_first_number():
    data, _ = build_docx(small(chapter("explanation/w/a.md", "1. a\n2. b\n\nText.\n\n3. c\n")))
    numbering = zipfile.ZipFile(io.BytesIO(data)).read("word/numbering.xml").decode("utf-8")
    assert numbering.count("<w:num ") == 3
    assert '<w:startOverride w:val="3"/>' in numbering
    assert qa.check_docx(data) == []


def test_text_is_escaped():
    data, _ = build_docx(small(chapter("explanation/w/a.md", "a < b & `c > d`\n", title="T & <U>")))
    assert qa.check_docx(data) == []
    assert "T &amp; &lt;U&gt;" in document_xml(data)


def test_diagram_is_embedded_and_scaled_to_the_page():
    rendered = []

    def render(source: str) -> bytes:
        rendered.append(source)
        return png(4000, 1000)

    data, _ = build_docx(small(chapter("explanation/w/a.md", "```mermaid\ngraph TD; A-->B\n```\n")), render_diagram=render)
    assert rendered == ["graph TD; A-->B"]
    package = zipfile.ZipFile(io.BytesIO(data))
    assert package.read("word/media/diagram-1.png") == png(4000, 1000)
    assert 'cx="5731510" cy="1432877"' in document_xml(data)
    assert qa.check_docx(data) == []


def test_diagram_without_renderer_fails_closed(monkeypatch):
    monkeypatch.setattr(mermaid.shutil, "which", lambda name: None)
    with pytest.raises(mermaid.MermaidError, match="not installed"):
        build_docx(small(chapter("explanation/w/a.md", "```mermaid\ngraph TD; A-->B\n```\n")))


def test_check_docx_reports_damage():
    data, _ = build_docx(small(chapter("explanation/w/a.md", "A.\n")))
    source = zipfile.ZipFile(io.BytesIO(data))
    damaged = io.BytesIO()
    with zipfile.ZipFile(damaged, "w") as out:
        for name in source.namelist():
            body = source.read(name)
            if name == "word/document.xml":
                body = body.replace(b'w:anchor="section_1"', b'w:anchor="nowhere"').replace(b'"Normal"', b'"Absent"')
            out.writestr(name, body)
    problems = qa.check_docx(damaged.getvalue())
    assert any("missing bookmark nowhere" in p for p in problems)
    assert any("undefined style Absent" in p for p in problems)
    assert qa.check_docx(b"not a zip")


@pytest.mark.skipif(not mermaid.available(), reason="mmdc (mermaid-cli) is not installed; publication.yml installs it")
def test_pinned_mermaid_renders_a_png():
    width, height = mermaid.png_size(mermaid.render("graph TD\n  A[World] --> B[Organism]\n"))
    assert width > 0 and height > 0
