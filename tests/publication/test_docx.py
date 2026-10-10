from __future__ import annotations

import io
import re
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
from docx import PAGE_PLACEHOLDER, breakable, build_docx  # noqa: E402
from style import StyleError, load_style  # noqa: E402
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
        "release": {"id": "2026.01.02-abcdef0", "date": "2026-01-02"},
        "registry_digest": "0" * 64,
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
    # Every chapter of a part is listed; elsewhere a lone chapter is its section.
    chapters = sum(
        sum(1 for c in s["chapters"] if not c.get("empty"))
        for s in projection["sections"] if s["group"] == "parts" or len(s["chapters"]) > 1
    )
    assert len(toc) == len(projection["sections"]) + chapters
    assert toc[0]["level"] == 1 and {e["level"] for e in toc} == {1, 2}
    assert len({e["bookmark"] for e in toc}) == len(toc)


def test_links_between_published_chapters_stay_inside_the_document():
    text = "See [b](b.md#part), [gone](../../technical/x.md) and [web](https://example.org).\n"
    data, _ = build_docx(small(chapter("explanation/w/a.md", text), chapter("explanation/w/b.md", "B.\n")))
    xml = document_xml(data)
    assert 'w:anchor="s1c2"' in xml
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


def test_front_page_names_the_edition():
    projection = small(chapter("explanation/w/a.md", "A.\n"))
    assert "Working edition." in document_xml(build_docx(projection)[0])
    published = document_xml(build_docx(projection, edition="published")[0])
    assert "Published edition." in published and "Working edition." not in published


def test_pages_carry_publication_part_edition_release_and_page_of_total():
    data, _ = build_docx(small(chapter("explanation/w/a.md", "A.\n")), edition="published")
    package = zipfile.ZipFile(io.BytesIO(data))
    headers = [package.read(n).decode("utf-8") for n in sorted(package.namelist()) if n.startswith("word/header")]
    # Empty one for the cover, then front matter, Part I, Appendix A.
    assert len(headers) == 4 and ">P<" in headers[1]
    assert "Part I — One" in headers[2] and "Appendix A — Catalog" in headers[3]
    footer = package.read("word/footer1.xml").decode("utf-8")
    assert "Published edition · 2026.01.02-abcdef0" in footer and " PAGE " in footer and " NUMPAGES " in footer
    assert qa.check_docx(data) == []


def test_cover_has_identity_and_no_revision_hash():
    projection = small(chapter("explanation/w/a.md", "A.\n"))
    projection["sources"]["docs"] = {"revision": "f" * 40, "state": "clean"}
    xml = document_xml(build_docx(projection)[0])
    cover = xml[: xml.index("Publication identity")]
    assert "logo.png" in cover and ">P<" in cover and ">S<" in cover and "Release 2026.01.02-abcdef0" in cover
    assert "fffffff" not in cover and ">fffffff<" in xml  # short, in the provenance table, linking to the commit
    assert "f" * 40 not in re.sub(r"<w:hyperlink.*?>", "", xml)


def test_style_is_data_and_changes_only_the_look():
    projection = small(chapter("explanation/w/a.md", "A.\n"))
    style = load_style()
    other = {**style, "colours": {**style["colours"], "accent": "AA0000"}, "sizes": {**style["sizes"], "body": 12}}
    first, changed = build_docx(projection, style=style)[0], build_docx(projection, style=other)[0]
    assert document_xml(first) == document_xml(changed)
    styles = zipfile.ZipFile(io.BytesIO(changed)).read("word/styles.xml").decode("utf-8")
    assert "AA0000" in styles and 'w:ascii="Aptos"' in styles and 'w:ascii="Consolas"' in styles
    fonts = zipfile.ZipFile(io.BytesIO(first)).read("word/fontTable.xml").decode("utf-8")
    assert '<w:font w:name="Aptos"><w:altName w:val="Liberation Sans"/>' in fonts


def test_long_identifiers_break_after_separators_only():
    text = "See `world:src/world/durable_runtime.py::DurableWorldRuntime` and `short.py`.\n"
    xml = document_xml(build_docx(small(chapter("explanation/w/a.md", text)))[0])
    assert "world:\u200b" not in xml  # the break is its own run, in a typeface that has the character
    assert xml.count("<w:r><w:t>\u200b</w:t></w:r>") >= 5 and ">short.py<" in xml
    assert breakable("a/b") == "a/b"
    assert breakable("explanation/organism/x.md") == "explanation/\u200borganism/\u200bx.\u200bmd"


def test_empty_registries_are_rows_of_one_small_table_not_chapters():
    projection = small(chapter("explanation/w/a.md", "A.\n"))
    empties = [
        {**chapter(f"registry/{name}.yaml", "No registered entries at this revision.\n", title=name.capitalize()),
         "generated": True, "empty": True}
        for name in ("notation", "metrics")
    ]
    projection["sections"][1] = {"id": "app", "title": "Notation and metrics", "group": "appendices", "chapters": empties}
    data, toc = build_docx(projection)
    xml = document_xml(data)
    assert [e["text"] for e in toc][-1] == "Appendix A — Notation and metrics"  # no entry per empty registry
    assert xml.count("No registered entries at this revision.") == 2 and ">Entries<" in xml
    assert "A.1 Notation" not in xml and qa.check_docx(data) == []


def test_cover_spacing_comes_from_the_style():
    projection = small(chapter("explanation/w/a.md", "A.\n"))
    style = load_style()
    moved = {**style, "cover": {**style["cover"], "top_space_mm": 10}}
    assert 'w:before="567"' in document_xml(build_docx(projection, style=moved)[0])
    assert 'w:before="567"' not in document_xml(build_docx(projection, style=style)[0])


def test_logo_is_a_file_of_this_repository():
    logo = ROOT / load_style()["logo"]["path"]
    assert logo.is_file() and ROOT in logo.resolve().parents


def linked(xml: str, data: bytes) -> dict[str, str]:
    """Text of every external link of a document, by the address it leads to."""
    rels = zipfile.ZipFile(io.BytesIO(data)).read("word/_rels/document.xml.rels").decode("utf-8")
    targets = dict(re.findall(r'Id="(rId\d+)" Type="[^"]+/hyperlink" Target="([^"]+)"', rels))
    out = {}
    for rid, inner in re.findall(r'<w:hyperlink r:id="(rId\d+)">(.*?)</w:hyperlink>', xml):
        out["".join(re.findall(r">([^<]*)</w:t>", inner)).replace("\u200b", "")] = targets[rid].replace("&amp;", "&")
    return out


def test_references_become_links_to_github():
    text = "See `world:src/world/journal.py::CausalJournal`, finding F-0001, ADR-0107 and `not.a.reference`.\n"
    one = chapter("explanation/w/a.md", text)
    one["references"] = {
        "world:src/world/journal.py::CausalJournal": {"url": "https://github.com/biopeia/world/blob/abc/src/world/journal.py#L9"},
        "F-0001": {"url": "https://github.com/biopeia/world/issues/28"},
        "ADR-0107": {"url": "https://github.com/biopeia/docs/blob/abc/technical/adr/ADR-0107-journal-role.md"},
    }
    one["source_url"] = "https://github.com/biopeia/docs/blob/abc/explanation/w/a.md"
    data, _ = build_docx(small(one))
    xml = document_xml(data)
    links = linked(xml, data)
    assert links["world:src/world/journal.py::CausalJournal"].endswith("journal.py#L9")
    assert links["F-0001"].endswith("/world/issues/28") and links["ADR-0107"].endswith("ADR-0107-journal-role.md")
    assert links["explanation/w/a.md"] == one["source_url"]
    assert "not.a.reference" not in links and 'w:val="CodeLink"' in xml
    assert qa.check_docx(data) == []


def test_revision_is_shown_short_and_still_links_to_the_commit():
    sha = "6543188ff302a5f2dc8002c0086252d6061e5310"
    one = chapter("explanation/w/a.md", f"Reviewed against `organism` at commit `{sha}`.\n")
    one["references"] = {sha: {"url": f"https://github.com/biopeia/organism/commit/{sha}", "label": "2026.10.09-6543188"}}
    data, _ = build_docx(small(one))
    xml = document_xml(data)
    assert sha not in xml
    assert linked(xml, data)["2026.10.09-6543188"].endswith(f"/organism/commit/{sha}")


def test_component_identifier_links_to_its_sheet_and_anchor_links_to_its_section():
    reader = chapter("explanation/w/a.md", "It uses `WLD-JRN`. See [why](b.md#why-it-exists) and [here](#local-part).\n\n## Local part\n\nText.\n")
    reader["references"] = {"WLD-JRN": {"component": "WLD-JRN"}}
    other = chapter("explanation/w/b.md", "## Why it exists\n\nBecause.\n")
    projection = small(reader, other)
    catalog = {**chapter("registry/components.yaml", "### `WLD-JRN` — journal\n\nSheet.\n"), "generated": True}
    projection["sections"][1] = {"id": "app", "title": "Catalog", "group": "appendices", "chapters": [catalog]}
    projection["links"] = {"components": ["WLD-JRN"], "github": "https://github.com/biopeia", "docs_tree": None}
    data, _ = build_docx(projection)
    xml = document_xml(data)
    names = dict(re.findall(r'w:name="(h\d+)"/>(?:<w:r>.*?</w:r>)*?<w:r>(?:<w:rPr>.*?</w:rPr>)?<w:t xml:space="preserve">([^<]+)<', xml))
    by_text = {text: name for name, text in names.items()}
    assert f'w:anchor="{by_text["WLD-JRN"]}"' in xml          # the mention in prose
    assert f'w:anchor="{by_text["Why it exists"]}"' in xml     # a section of another chapter
    assert f'w:anchor="{by_text["Local part"]}"' in xml        # a section of the same chapter
    assert qa.check_docx(data) == []


def test_link_to_a_document_outside_the_publication_goes_to_github():
    one = chapter("explanation/w/a.md", "See [the decision](../../technical/adr/ADR-0107-journal-role.md).\n")
    projection = {**small(one), "links": {"docs_tree": "https://github.com/biopeia/docs/blob/abc/", "components": []}}
    data, _ = build_docx(projection)
    assert linked(document_xml(data), data)["the decision"] == (
        "https://github.com/biopeia/docs/blob/abc/technical/adr/ADR-0107-journal-role.md")


def test_document_carries_title_subject_and_the_date_of_its_sources():
    data, _ = build_docx(small(chapter("explanation/w/a.md", "A.\n")), edition="published")
    core = zipfile.ZipFile(io.BytesIO(data)).read("docProps/core.xml").decode("utf-8")
    assert "<dc:title>P — S</dc:title>" in core and "Published edition · Release 2026.01.02-abcdef0" in core
    assert "2026-01-02T00:00:00Z" in core and qa.check_docx(data) == []


def test_identifier_in_a_heading_keeps_the_technical_typeface():
    xml = document_xml(build_docx(small(chapter("explanation/w/a.md", "## `WLD-JRN` — journal\n")))[0])
    heading = xml[xml.index('w:val="Heading3"'):]
    assert '<w:rStyle w:val="CodeChar"/>' in heading[: heading.index("</w:p>")]


def test_chapters_follow_on_or_open_a_page_as_the_style_says():
    projection = small(chapter("explanation/w/a.md", "A.\n"), chapter("explanation/w/b.md", "B.\n"))
    style = load_style()
    flowing = document_xml(build_docx(projection, style={**style, "layout": {"chapter_starts_page": False}})[0])
    paged = document_xml(build_docx(projection, style={**style, "layout": {"chapter_starts_page": True}})[0])
    assert paged.count("pageBreakBefore") == flowing.count("pageBreakBefore") + 1


def wide_table(rows: int) -> str:
    head = "| A | B | C | D | E | F |\n|---|---|---|---|---|---|\n"
    return head + "".join("| " + " | ".join(f"cell {r} {c} some words here" for c in range(6)) + " |\n" for r in range(rows))


def test_genuinely_wide_table_gets_sideways_pages_of_its_own():
    data, _ = build_docx(small(chapter("explanation/w/a.md", "Before.\n\n" + wide_table(12) + "\nAfter.\n")))
    xml = document_xml(data)
    assert xml.count('w:orient="landscape"') == 1
    before, after = xml.index("Before."), xml.index("After.")
    assert before < xml.index('w:orient="landscape"') < after
    package = zipfile.ZipFile(io.BytesIO(data))
    assert "word/footer2.xml" in package.namelist() and qa.check_docx(data) == []


def test_small_or_narrow_tables_stay_in_the_text():
    small_wide = document_xml(build_docx(small(chapter("explanation/w/a.md", wide_table(2))))[0])
    narrow = document_xml(build_docx(small(chapter("explanation/w/a.md", "| A | B |\n|---|---|\n" + "| x | y |\n" * 200)))[0])
    assert "landscape" not in small_wide and "landscape" not in narrow


def test_identifier_at_the_break_limit_is_given_room_whole():
    table = "| Name | Text |\n|---|---|\n| `confidence_classes` | " + "word " * 80 + "|\n"
    xml = document_xml(build_docx(small(chapter("explanation/w/a.md", table)))[0])
    grid = xml[xml.rindex("<w:tblGrid>"):]
    first = int(re.search(r'<w:gridCol w:w="(\d+)"/>', grid).group(1))
    assert first > 18 * 8 * 20 * 0.6  # eighteen characters of the technical typeface, unbroken


def test_part_divider_says_its_list_is_the_chapters_of_the_part():
    xml = document_xml(build_docx(small(chapter("explanation/w/a.md", "A.\n"), chapter("explanation/w/b.md", "B.\n")))[0])
    assert "Chapters in this part" in xml


def test_symbols_the_fallbacks_lack_are_set_in_the_symbols_typeface():
    xml = document_xml(build_docx(small(chapter("explanation/w/a.md", "Go ▶ there.\n")))[0])
    assert '<w:rStyle w:val="SymbolChar"/></w:rPr><w:t xml:space="preserve">▶</w:t>' in xml


def test_identifier_columns_get_the_room_they_need():
    table = "| Id | Text |\n|---|---|\n| `component.world-causal-journal` | " + "word " * 60 + "|\n"
    xml = document_xml(build_docx(small(chapter("explanation/w/a.md", table)))[0])
    grid = xml[xml.rindex("<w:tblGrid>"):]
    widths = [int(w) for w in re.findall(r'<w:gridCol w:w="(\d+)"/>', grid[: grid.index("</w:tblGrid>")])]
    assert widths[0] > 1100 and widths[1] > widths[0] and sum(widths) <= 9300


def test_chapter_names_its_source_and_front_page_its_inventory():
    projection = {**small(chapter("explanation/w/a.md", "A.\n")), "inventory": {"Components": 34}}
    xml = document_xml(build_docx(projection)[0])
    assert "Source: " in xml and ">explanation/w/a.md<" in xml
    assert "What this publication holds" in xml and ">Components<" in xml and ">34<" in xml


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
    cx, cy = map(int, re.search(r'diagram-1.png.*?<a:ext cx="(\d+)" cy="(\d+)"/>', document_xml(data)).groups())
    assert cx <= 9298 * 635 and abs(cx / cy - 4) < 0.01  # as wide as the text, proportions kept
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
                body = body.replace(b'w:anchor="s1"', b'w:anchor="nowhere"').replace(b'"Normal"', b'"Absent"')
            out.writestr(name, body)
    problems = qa.check_docx(damaged.getvalue())
    assert any("missing bookmark nowhere" in p for p in problems)
    assert any("undefined style Absent" in p for p in problems)
    assert qa.check_docx(b"not a zip")


@pytest.mark.skipif(not mermaid.available(), reason="mmdc (mermaid-cli) is not installed; publication.yml installs it")
def test_pinned_mermaid_renders_a_png():
    width, height = mermaid.png_size(mermaid.render("graph TD\n  A[World] --> B[Organism]\n"))
    assert width > 0 and height > 0


def test_style_file_is_validated(tmp_path):
    text = (ROOT / "publication" / "style.yaml").read_text(encoding="utf-8")
    bad = tmp_path / "style.yaml"
    bad.write_text(text.replace('accent: "0B4F8A"', 'accent: "blue"'), encoding="utf-8")
    with pytest.raises(StyleError, match="colours.accent"):
        load_style(bad)
