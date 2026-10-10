"""Render a publication projection as a DOCX package.

Three things are kept apart: the projection says what is published, the
style (publication/style.yaml) says how it looks, and this module lays it
out. Nothing here decides a typeface, a size or a colour.

The package is plain OpenXML written with the standard library, so the same
projection and style always give the same bytes: fixed entry order, fixed
entry timestamps, no clock and no random identifiers.

The table of contents is materialised text, not a field: a field would only
be filled in by a person opening the file. build_docx therefore takes the
page of each entry from the caller, who reads them from a first PDF pass.
"""

from __future__ import annotations

import io
import posixpath
import re
import zipfile
from pathlib import Path
from typing import Any, Callable
from xml.etree import ElementTree
from xml.sax.saxutils import escape, quoteattr

import markdown
import mermaid
from style import load_style, symbol_pattern
from validate_registry import ROOT

TWIPS_PER_MM = 1440 / 25.4
EMU_PER_TWIP, EMU_PER_PIXEL = 635, 9525
PAGE_PLACEHOLDER = "000"
ZERO_WIDTH_SPACE = "​"
# An identifier may break after one of these, never inside a word.
BREAK_AFTER_RE = re.compile(r"(::|[/._\-:])(?=[\w<{(])")
LONG_TOKEN = 18

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NAMESPACES = (
    f'xmlns:w="{W_NS}" xmlns:r="{R_NS}" '
    'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
    'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"'
)
XML_HEADER = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'

# Document headings sit below part (1) and chapter (2).
HEADING_STYLES = {1: "Heading1", 2: "Heading2", 3: "Heading3", 4: "Heading4"}
BULLET_NUM_ID = 1

# What a build says about itself. A published edition is one whose every
# source is a clean, identified revision; publish.py enforces it.
EDITIONS = {
    "working": ("Working edition", "Built from whatever state the sources were in. A source repository may be "
                "unresolved or carry local modifications, so this copy must not be cited as a state of Biopeia."),
    "published": ("Published edition", "Every source repository is a clean, identified revision."),
}


# Word reads a document strictly: the children of a properties element must
# come in the order the standard gives. Callers pass properties in whatever
# order is convenient and `ordered` sorts them.
PPR_ORDER = ("pStyle", "keepNext", "keepLines", "pageBreakBefore", "numPr", "pBdr", "shd", "tabs", "spacing",
             "ind", "jc", "outlineLvl", "sectPr")
RPR_ORDER = ("rStyle", "rFonts", "b", "i", "color", "spacing", "sz", "u", "lang")
ElementTree.register_namespace("w", W_NS)


def ordered(inner: str, order: tuple[str, ...]) -> str:
    if not inner:
        return inner
    root = ElementTree.fromstring(f'<w:x xmlns:w="{W_NS}" xmlns:r="{R_NS}">{inner}</w:x>')
    children = sorted(root, key=lambda child: order.index(child.tag.split("}", 1)[1]))
    return "".join(
        re.sub(r' xmlns:\w+="[^"]*"', "", ElementTree.tostring(child, encoding="unicode")) for child in children
    )


def roman(number: int) -> str:
    out = ""
    for value, symbol in ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
                          (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while number >= value:
            out, number = out + symbol, number - value
    return out


def plain(inlines: list[dict[str, Any]]) -> str:
    return "".join(run["text"] for run in inlines)


def cell(text: Any, code: bool = False) -> list[dict[str, Any]]:
    """One table cell of plain text, as inline runs."""
    return [{"text": str(text), "bold": False, "italic": False, "code": code, "href": None}]


def breakable(text: str) -> str:
    """Let a long identifier wrap after a separator instead of anywhere, or not at all."""
    if max((len(token) for token in text.split()), default=0) <= LONG_TOKEN:
        return text
    return BREAK_AFTER_RE.sub(lambda match: match.group(1) + ZERO_WIDTH_SPACE, text)


# Characters set in the symbols typeface; build_docx fills it in from the style.
_symbols: re.Pattern[str] | None = None


def text_run(text: str, bold: bool = False, italic: bool = False, code: bool = False, link: bool = False,
             size: float | None = None) -> str:
    def run(piece: str, style: str) -> str:
        props = ((f'<w:rStyle w:val="{style}"/>' if style else "") + ("<w:b/>" if bold else "")
                 + ("<w:i/>" if italic else "") + (f'<w:sz w:val="{round(size * 2)}"/>' if size else ""))
        return f'<w:r>{f"<w:rPr>{props}</w:rPr>" if props else ""}<w:t xml:space="preserve">{escape(piece)}</w:t></w:r>'

    style = "CodeChar" if code else "Hyperlink" if link else ""
    out = []
    # The code typeface has no zero-width space and neither fallback has every
    # symbol; each such character goes in a run of a typeface that has it.
    pattern = f"({ZERO_WIDTH_SPACE}" + (f"|{_symbols.pattern}" if _symbols else "") + ")"
    for piece in re.split(pattern, text):
        if piece == ZERO_WIDTH_SPACE:
            out.append(f"<w:r><w:t>{piece}</w:t></w:r>")
        elif piece and _symbols and _symbols.fullmatch(piece):
            out.append(run(piece, "SymbolChar"))
        elif piece:
            out.append(run(piece, style))
    return "".join(out) or run("", style)


def paragraph(style: str, content: str, properties: str = "") -> str:
    return f'<w:p><w:pPr>{ordered(f"""<w:pStyle w:val="{style}"/>{properties}""", PPR_ORDER)}</w:pPr>{content}</w:p>'


def field(instruction: str) -> str:
    return ('<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
            f'<w:r><w:instrText xml:space="preserve"> {instruction} </w:instrText></w:r>'
            '<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>1</w:t></w:r>'
            '<w:r><w:fldChar w:fldCharType="end"/></w:r>')


class Document:
    """Accumulates the body and the parts it refers to."""

    def __init__(self, projection: dict[str, Any], style: dict[str, Any], pages: dict[str, int] | None,
                 render_diagram: Callable[[str], bytes], edition: str, assets_root: Path) -> None:
        self.projection = projection
        self.style = style
        self.pages = pages
        self.render_diagram = render_diagram
        self.edition = edition
        self.assets_root = assets_root
        self.body: list[str] = []
        self.toc: list[dict[str, Any]] = []
        self.relationships: list[tuple[str, str, str, bool]] = []  # id, type, target, external
        self.media: dict[str, bytes] = {}
        self.headers: dict[str, str] = {}
        self.ordered_lists: list[int] = []  # start number of each numbered list, in order
        self.bookmarks = 0
        self.drawings = 0
        # Links between published chapters become links inside the document.
        self.chapter_bookmarks: dict[str, str] = {}
        self.empty_footer = ""

        page, margin = style["page"], style["page"]["margin_mm"]
        self.page_width, self.page_height = round(page["width_mm"] * TWIPS_PER_MM), round(page["height_mm"] * TWIPS_PER_MM)
        self.margins = {side: round(margin[side] * TWIPS_PER_MM) for side in ("top", "bottom", "left", "right")}
        self.text_width = self.page_width - self.margins["left"] - self.margins["right"]
        self.text_height = self.page_height - self.margins["top"] - self.margins["bottom"]

    def relate(self, kind: str, target: str, external: bool = False) -> str:
        for rid, known_kind, known_target, _ in self.relationships:
            if (known_kind, known_target) == (kind, target):
                return rid
        rid = f"rId{len(self.relationships) + 1}"
        self.relationships.append((rid, kind, target, external))
        return rid

    # --- inline ---------------------------------------------------------------

    def runs(self, inlines: list[dict[str, Any]], base: str, bold: bool = False, code_size: float | None = None) -> str:
        out = []
        for run in inlines:
            href = run["href"]
            anchor = None
            if href and not href.startswith(("http://", "https://", "mailto:")):
                target = posixpath.normpath(posixpath.join(base, href.split("#", 1)[0]))
                anchor = self.chapter_bookmarks.get(target)
            linked = bool(anchor) or bool(href and href.startswith(("http://", "https://", "mailto:")))
            text = breakable(run["text"]) if run["code"] else run["text"]
            xml = text_run(text, bold or run["bold"], run["italic"], run["code"], link=linked and not run["code"],
                           size=code_size if run["code"] else None)
            if anchor:
                xml = f'<w:hyperlink w:anchor="{anchor}">{xml}</w:hyperlink>'
            elif linked:
                rid = self.relate(f"{R_NS}/hyperlink", href, external=True)
                xml = f'<w:hyperlink r:id="{rid}">{xml}</w:hyperlink>'
            # A link to a document that is not part of the publication stays as its text.
            out.append(xml)
        return "".join(out)

    # --- blocks ---------------------------------------------------------------

    def bookmarked(self, content: str, bookmark: str) -> str:
        self.bookmarks += 1
        return (f'<w:bookmarkStart w:id="{self.bookmarks}" w:name="{bookmark}"/>{content}'
                f'<w:bookmarkEnd w:id="{self.bookmarks}"/>')

    def heading(self, level: int, text: str | list[dict[str, Any]], bookmark: str | None = None,
                listed_as: str | None = None, properties: str = "") -> None:
        # A heading taken from a document keeps its identifiers in the technical typeface.
        content = text_run(text) if isinstance(text, str) else self.runs(
            text, "", code_size=self.style["sizes"][("part", "chapter", "section", "subsection")[min(level, 4) - 1]] - 1)
        if bookmark:
            content = self.bookmarked(content, bookmark)
            if listed_as:
                self.toc.append({"bookmark": bookmark, "level": min(level, 2), "text": listed_as})
        self.body.append(paragraph(HEADING_STYLES[min(level, 4)], content, properties))

    def column_widths(self, rows: list[list[list[dict[str, Any]]]]) -> list[int]:
        """Widths that give every column room for its longest unbreakable piece.

        An identifier breaks only after a separator, so the piece between two
        separators is what must fit. What is left over is shared out by how
        much text each column holds.
        """
        sizes = self.style["sizes"]
        text_unit, code_unit = sizes["table"] * 20 * 0.52, (sizes["table"] - 0.5) * 20 * 0.62
        columns = len(rows[0])
        needed, weights = [0.0] * columns, [0.0] * columns
        for row in rows:
            for index, runs in enumerate(row[:columns]):
                for run in runs:
                    words = (BREAK_AFTER_RE.sub(lambda m: m.group(1) + " ", run["text"]) if run["code"] else run["text"]).split()
                    longest = max((len(word) for word in words), default=0)
                    needed[index] = max(needed[index], longest * (code_unit if run["code"] else text_unit) + 200)
                weights[index] = max(weights[index], min(60, max(6, len(plain(runs)))))
        needed = [min(need, self.text_width * 0.55) for need in needed]
        if sum(needed) >= self.text_width:
            return [int(self.text_width * need / sum(needed)) for need in needed]
        spare = self.text_width - sum(needed)
        return [int(need + spare * weight / sum(weights)) for need, weight in zip(needed, weights)]

    def table(self, block: dict[str, Any], base: str) -> None:
        rows = [block["header"], *block["rows"]]
        widths = self.column_widths(rows)
        shade, code_size = self.style["colours"]["shade"], self.style["sizes"]["table"] - 0.5
        xml = ['<w:tbl><w:tblPr><w:tblStyle w:val="RuledTable"/><w:tblW w:w="5000" w:type="pct"/>'
               '<w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid>']
        xml += [f'<w:gridCol w:w="{width}"/>' for width in widths]
        xml.append("</w:tblGrid>")
        for index, row in enumerate(rows):
            head = index == 0
            xml.append("<w:tr><w:trPr><w:cantSplit/>" + ("<w:tblHeader/>" if head else "") + "</w:trPr>")
            # The last row stays with the paragraph after the table, so that
            # paragraph never falls alone onto an empty page.
            keep = "<w:keepNext/>" if index == len(rows) - 1 else ""
            for width, runs in zip(widths, row):
                fill = f'<w:shd w:val="clear" w:color="auto" w:fill="{shade}"/>' if head else ""
                xml.append(f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>{fill}</w:tcPr>'
                           + paragraph("TableText", self.runs(runs, base, bold=head, code_size=code_size), keep)
                           + "</w:tc>")
            xml.append("</w:tr>")
        xml.append("</w:tbl>")
        self.body.append("".join(xml))
        # A table must be followed by a paragraph; this one also spaces it.
        self.body.append(paragraph("TableText", ""))

    def list(self, block: dict[str, Any], base: str) -> None:
        # ponytail: one numbering sequence per level of a list block; two
        # numbered sub-lists under different items would run on. The corpus
        # has no nested numbered list. Split per parent item if one appears.
        num_ids: dict[int, int] = {}
        for item in block["items"]:
            level = item["level"]
            if item["ordered"]:
                if level not in num_ids:
                    self.ordered_lists.append(item["number"])
                    num_ids[level] = BULLET_NUM_ID + len(self.ordered_lists)
                num_id = num_ids[level]
            else:
                num_id = BULLET_NUM_ID
            numbering = f'<w:numPr><w:ilvl w:val="{level}"/><w:numId w:val="{num_id}"/></w:numPr>'
            self.body.append(paragraph("ListParagraph", self.runs(item["inlines"], base), numbering))

    def code(self, block: dict[str, Any]) -> None:
        if block["language"] == "mermaid":
            self.diagram(block["text"])
            return
        lines = block["text"].split("\n")
        for index, line in enumerate(lines):
            # Padding above the first line and below the last, inside the shade.
            spacing = (f'<w:spacing w:before="{80 if index == 0 else 0}" '
                       f'w:after="{80 if index == len(lines) - 1 else 0}" w:line="240" w:lineRule="auto"/>')
            self.body.append(paragraph("Code", text_run(line), spacing))
        self.body.append(paragraph("TableText", ""))

    def image(self, data: bytes, name: str, cx: int, cy: int, properties: str = "") -> str:
        self.drawings += 1
        self.media[name] = data
        rid = self.relate(f"{R_NS}/image", f"media/{name}")
        number = self.drawings
        return (
            f'<w:p><w:pPr><w:pStyle w:val="Normal"/>{properties}</w:pPr><w:r><w:drawing>'
            f'<wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>'
            f'<wp:docPr id="{number}" name="Picture {number}"/>'
            '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:pic><pic:nvPicPr><pic:cNvPr id="{number}" name="{name}"/><pic:cNvPicPr/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
            "</a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>"
        )

    def diagram(self, source: str) -> None:
        data = self.render_diagram(source)
        width, height = mermaid.png_size(data)
        cx, cy = width * EMU_PER_PIXEL // mermaid.SCALE, height * EMU_PER_PIXEL // mermaid.SCALE
        shrink = min(1.0, self.text_width * EMU_PER_TWIP / cx, self.text_height * EMU_PER_TWIP * 0.8 / cy)
        number = sum(1 for name in self.media if name.startswith("diagram-")) + 1
        self.body.append(self.image(data, f"diagram-{number}.png", int(cx * shrink), int(cy * shrink),
                                    '<w:jc w:val="center"/>'))

    def chapter_body(self, chapter: dict[str, Any]) -> None:
        try:
            blocks = markdown.parse(chapter["markdown"])
        except markdown.MarkdownError as exc:
            raise markdown.MarkdownError(f"{chapter['source']}: {exc}") from exc
        base = chapter["base"]
        for block in blocks:
            if block["type"] == "heading":
                # '##' in a document is one level below its chapter heading.
                self.heading(block["level"] + 1, block["inlines"])
            elif block["type"] == "paragraph":
                self.body.append(paragraph("Normal", self.runs(block["inlines"], base)))
            elif block["type"] == "list":
                self.list(block, base)
            elif block["type"] == "table":
                self.table(block, base)
            else:
                self.code(block)

    # --- sections of the document --------------------------------------------

    def end_section(self, running: str, cover: bool = False) -> str:
        """Section properties for everything since the previous section, with its own running header."""
        name = f"header{sum(1 for h in self.headers if h != 'header0.xml') + 1}.xml"
        publication = self.projection["publication"]
        tab = f'<w:tabs><w:tab w:val="right" w:pos="{self.text_width}"/></w:tabs>'
        self.headers[name] = (
            f'{XML_HEADER}<w:hdr xmlns:w="{W_NS}">'
            + paragraph("Header", text_run(publication["title"]) + "<w:r><w:tab/></w:r>" + text_run(running), tab)
            + "</w:hdr>"
        )
        header, footer = self.relate(f"{R_NS}/header", name), self.relate(f"{R_NS}/footer", "footer1.xml")
        first = ""
        if cover:
            # The cover carries no running header or footer: its own are empty.
            self.headers["header0.xml"] = f'{XML_HEADER}<w:hdr xmlns:w="{W_NS}">{paragraph("Normal", "")}</w:hdr>'
            self.empty_footer = f'{XML_HEADER}<w:ftr xmlns:w="{W_NS}">{paragraph("Normal", "")}</w:ftr>'
            first = (f'<w:headerReference w:type="first" r:id="{self.relate(f"{R_NS}/header", "header0.xml")}"/>'
                     f'<w:footerReference w:type="first" r:id="{self.relate(f"{R_NS}/footer", "footer0.xml")}"/>')
        m = self.margins
        return (f'<w:sectPr><w:headerReference w:type="default" r:id="{header}"/>'
                f'<w:footerReference w:type="default" r:id="{footer}"/>{first}'
                f'<w:pgSz w:w="{self.page_width}" w:h="{self.page_height}"/>'
                f'<w:pgMar w:top="{m["top"]}" w:right="{m["right"]}" w:bottom="{m["bottom"]}" w:left="{m["left"]}" '
                'w:header="560" w:footer="560" w:gutter="0"/>'
                + ("<w:titlePg/>" if cover else "") + "</w:sectPr>")

    def close_section(self, running: str, cover: bool = False) -> None:
        # The section ends in its own last paragraph: a paragraph added only to
        # carry the break could fall alone onto an otherwise empty page.
        last = self.body[-1]
        assert last.startswith("<w:p><w:pPr>"), "a section must end in a paragraph"
        self.body[-1] = last.replace("</w:pPr>", self.end_section(running, cover) + "</w:pPr>", 1)

    def footer_text(self) -> str:
        return f"{EDITIONS[self.edition][0]} · {self.projection['release']['id']}"

    def footer_xml(self) -> str:
        tab = f'<w:tabs><w:tab w:val="right" w:pos="{self.text_width}"/></w:tabs>'
        left = self.footer_text()
        return (f'{XML_HEADER}<w:ftr xmlns:w="{W_NS}">'
                + paragraph("Footer", text_run(left) + "<w:r><w:tab/></w:r>" + text_run("Page ") + field("PAGE")
                            + text_run(" of ") + field("NUMPAGES"), tab)
                + "</w:ftr>")

    def outline(self) -> list[dict[str, Any]]:
        """Numbered headings of every section and chapter, in order."""
        out, part, appendix, chapter_number = [], 0, 0, 0
        for section in self.projection["sections"]:
            group = section["group"]
            if group == "parts":
                part += 1
                kicker, running = f"Part {roman(part)}", f"Part {roman(part)} — {section['title']}"
            elif group == "appendices":
                appendix += 1
                kicker, running = f"Appendix {chr(64 + appendix)}", f"Appendix {chr(64 + appendix)} — {section['title']}"
            else:
                kicker, running = "", section["title"]
            entry = {"kicker": kicker, "title": section["title"], "label": running, "group": group,
                     "bookmark": f"s{len(out) + 1}", "chapters": []}
            # A section made of one chapter is that chapter: no second heading.
            merged = group != "parts" and len(section["chapters"]) == 1
            for index, chapter in enumerate(section["chapters"], start=1):
                if group == "parts":
                    chapter_number += 1
                    title = f"{chapter_number}. {chapter['title']}"
                else:
                    title = f"{chr(64 + appendix)}.{index} {chapter['title']}"
                # Letters and digits only: the PDF keeps such a name unchanged.
                bookmark = entry["bookmark"] if merged else f"s{len(out) + 1}c{index}"
                entry["chapters"].append({"chapter": chapter, "label": None if merged else title, "bookmark": bookmark})
                if not chapter["generated"]:
                    self.chapter_bookmarks[chapter["source"]] = bookmark
            out.append(entry)
        return out

    def cover(self) -> None:
        publication, release, style = self.projection["publication"], self.projection["release"], self.style
        logo = style.get("logo") or {}
        if logo.get("path"):
            data = (self.assets_root / logo["path"]).read_bytes()
            width, height = mermaid.png_size(data)
            cx = round(logo["width_mm"] * TWIPS_PER_MM * EMU_PER_TWIP)
            self.body.append(self.image(data, "logo.png", cx, cx * height // width, '<w:spacing w:before="1200" w:after="900"/>'))
        self.body.append(paragraph("CoverBrand", text_run(publication["title"])))
        if publication.get("subtitle"):
            self.body.append(paragraph("CoverTitle", text_run(publication["subtitle"])))
        if publication.get("type"):
            self.body.append(paragraph("CoverMeta", text_run(publication["type"])))
        self.body.append(paragraph("CoverMeta", text_run(EDITIONS[self.edition][0]), '<w:spacing w:before="3600" w:after="40"/>'))
        self.body.append(paragraph("CoverMeta", text_run(f"Release {release['id']}")))
        if release["date"]:
            self.body.append(paragraph("CoverMeta", text_run(release["date"])))

    def identity_and_provenance(self) -> None:
        publication, release, sources = self.projection["publication"], self.projection["release"], self.projection["sources"]
        self.body.append(paragraph("FrontHeading", text_run("Publication identity"), "<w:pageBreakBefore/>"))
        name = " — ".join(t for t in (publication["title"], publication.get("subtitle")) if t)
        rows = [
            [cell("Publication"), cell(name)],
            [cell("Type"), cell(publication.get("type") or "not stated")],
            [cell("Edition"), cell(f"{EDITIONS[self.edition][0]}. {EDITIONS[self.edition][1]}")],
            [cell("Release"), cell(release["id"], code=True)],
            [cell("Date"), cell(release["date"] or "not available")],
        ]
        self.table({"header": [cell("Field"), cell("Value")], "rows": rows}, "")
        self.body.append(paragraph("Normal", text_run(
            "This document is generated. It presents the Biopeia documentation in reading order; the documents "
            "and registries of the documentation repository remain the only source, and nothing is stated here "
            "that is not stated there.")))
        self.body.append(paragraph("Heading4", text_run("Revision history")))
        self.body.append(paragraph("Normal", text_run(
            "No numbered release of this publication has been cut. A copy is identified by its release "
            "identifier, which is the day and revision of the documentation it was built from, and by the "
            "source revisions listed under provenance.")))

        self.body.append(paragraph("FrontHeading", text_run("Provenance and source revisions"), "<w:pageBreakBefore/>"))
        self.body.append(paragraph("Normal", text_run(
            "The revision of each repository the publication was built beside. A repository marked unresolved "
            "was not available to the build.")))
        rows = []
        for repo, source in sources.items():
            state = {"clean": "clean", "modified": "local modifications", "unresolved": "unresolved"}[source["state"]]
            rows.append([cell(repo), cell(source["revision"] or "—", code=bool(source["revision"])), cell(state)])
        self.table({"header": [cell(t) for t in ("Repository", "Revision", "State")], "rows": rows}, "")
        self.table({"header": [cell("Digest"), cell("SHA-256")],
                    "rows": [[cell("Registry"), cell(self.projection["registry_digest"], code=True)]]}, "")
        inventory = self.projection.get("inventory") or {}
        if inventory:
            self.body.append(paragraph("Heading4", text_run("What this publication holds")))
            self.table({"header": [cell("Inventory"), cell("Count")],
                        "rows": [[cell(label), cell(count)] for label, count in inventory.items()]}, "")

    def contents(self, outline: list[dict[str, Any]]) -> None:
        self.body.append(paragraph("FrontHeading", text_run("Contents"), "<w:pageBreakBefore/>"))
        entries = []
        for section in outline:
            entries.append((1, section["label"], section["bookmark"]))
            entries += [(2, c["label"], c["bookmark"]) for c in section["chapters"] if c["label"]]
        for level, label, bookmark in entries:
            page = str(self.pages[bookmark]) if self.pages is not None else PAGE_PLACEHOLDER
            link = f'<w:hyperlink w:anchor="{bookmark}">{text_run(label)}<w:r><w:tab/></w:r>{text_run(page)}</w:hyperlink>'
            self.body.append(paragraph(f"TOC{level}", link))

    def section(self, section: dict[str, Any], starts_document_section: bool) -> None:
        break_before = "" if starts_document_section else "<w:pageBreakBefore/>"
        if section["kicker"]:
            self.body.append(paragraph("Kicker", text_run(section["kicker"].upper()), break_before))
            break_before = ""
        self.heading(1, section["title"], section["bookmark"], listed_as=section["label"], properties=break_before)
        titled = [c for c in section["chapters"] if c["label"]]
        if len(titled) > 1:
            # The divider says what the part holds, so its page is never empty.
            for entry in titled:
                link = f'<w:hyperlink w:anchor="{entry["bookmark"]}">{text_run(entry["label"])}</w:hyperlink>'
                self.body.append(paragraph("ChapterList", link))
        for index, entry in enumerate(section["chapters"]):
            if entry["label"]:
                # The first chapter starts under the part heading. The others
                # follow on, or open a page, as the style says.
                self.heading(2, entry["label"], entry["bookmark"], listed_as=entry["label"],
                             properties="<w:pageBreakBefore/>" if index and self.style["layout"]["chapter_starts_page"]
                             else '<w:spacing w:before="640"/>')
            chapter = entry["chapter"]
            source = (text_run("Generated from ") if chapter["generated"] else text_run("Source: ")) + text_run(
                breakable(chapter["source"]), code=True, size=self.style["sizes"]["meta"])
            self.body.append(paragraph("Meta", source))
            self.chapter_body(chapter)

    def build(self) -> str:
        """Fill the body; return the section properties of the last section."""
        outline = self.outline()
        self.cover()
        self.identity_and_provenance()
        self.contents(outline)
        for section in (s for s in outline if s["group"] == "front"):
            self.section(section, starts_document_section=False)
        self.close_section(self.projection["publication"].get("subtitle") or "", cover=True)
        rest = [s for s in outline if s["group"] != "front"]
        for index, section in enumerate(rest):
            self.section(section, starts_document_section=True)
            if index < len(rest) - 1:
                self.close_section(section["label"])
        return self.end_section(rest[-1]["label"] if rest else "")

    # --- parts of the package -------------------------------------------------

    def relationships_xml(self) -> str:
        items = "".join(
            f'<Relationship Id="{rid}" Type="{kind}" Target={quoteattr(target)}'
            + (' TargetMode="External"' if external else "") + "/>"
            for rid, kind, target, external in self.relationships
        )
        return (f'{XML_HEADER}<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                f"{items}</Relationships>")

    def numbering_xml(self) -> str:
        def level(index: int, fmt: str, text: str) -> str:
            indent = 480 * (index + 1)
            return (f'<w:lvl w:ilvl="{index}"><w:start w:val="1"/><w:numFmt w:val="{fmt}"/>'
                    f'<w:lvlText w:val="{text}"/><w:lvlJc w:val="left"/>'
                    f'<w:pPr><w:ind w:left="{indent}" w:hanging="300"/></w:pPr></w:lvl>')

        out = [f'{XML_HEADER}<w:numbering xmlns:w="{W_NS}">',
               '<w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="hybridMultilevel"/>',
               level(0, "bullet", "•"), level(1, "bullet", "–"), "</w:abstractNum>",
               '<w:abstractNum w:abstractNumId="1"><w:multiLevelType w:val="hybridMultilevel"/>',
               level(0, "decimal", "%1."), level(1, "decimal", "%2."), "</w:abstractNum>",
               f'<w:num w:numId="{BULLET_NUM_ID}"><w:abstractNumId w:val="0"/></w:num>']
        for index, start in enumerate(self.ordered_lists, start=1):
            overrides = "".join(
                f'<w:lvlOverride w:ilvl="{lvl}"><w:startOverride w:val="{start}"/></w:lvlOverride>' for lvl in (0, 1)
            )
            out.append(f'<w:num w:numId="{BULLET_NUM_ID + index}"><w:abstractNumId w:val="1"/>{overrides}</w:num>')
        out.append("</w:numbering>")
        return "".join(out)

    def content_types_xml(self) -> str:
        overrides = {
            "/word/document.xml": "document.main",
            "/word/styles.xml": "styles",
            "/word/numbering.xml": "numbering",
            "/word/fontTable.xml": "fontTable",
            "/word/footer1.xml": "footer",
            **({"/word/footer0.xml": "footer"} if self.empty_footer else {}),
            **{f"/word/{name}": "header" for name in self.headers},
        }
        return (
            f'{XML_HEADER}<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Default Extension="png" ContentType="image/png"/>'
            + "".join(
                f'<Override PartName="{part}" ContentType="application/vnd.openxmlformats-officedocument.'
                f'wordprocessingml.{kind}+xml"/>' for part, kind in overrides.items())
            + "</Types>"
        )


def font_table_xml(style: dict[str, Any]) -> str:
    """Names the fallback of each typeface, for a reader who does not have it."""
    fonts = "".join(
        f'<w:font w:name="{font["name"]}"><w:altName w:val="{font["fallback"]}"/></w:font>'
        for font in style["fonts"].values()
    )
    return f'{XML_HEADER}<w:fonts xmlns:w="{W_NS}">{fonts}</w:fonts>'


def styles_xml(style: dict[str, Any], text_width: int) -> str:
    sizes, colours = style["sizes"], style["colours"]
    text_font, code_font = style["fonts"]["text"]["name"], style["fonts"]["code"]["name"]

    def fonts(name: str) -> str:
        return f'<w:rFonts w:ascii="{name}" w:hAnsi="{name}" w:cs="{name}"/>'

    def para(style_id: str, name: str, size: float, *, bold: bool = False, colour: str | None = None,
             before: int = 0, after: int = 120, extra: str = "", run: str = "", based: str | None = "Normal") -> str:
        return (f'<w:style w:type="paragraph" w:styleId="{style_id}"><w:name w:val="{name}"/>'
                + (f'<w:basedOn w:val="{based}"/>' if based else "")
                + "<w:pPr>" + ordered(f'{extra}<w:spacing w:before="{before}" w:after="{after}"/>', PPR_ORDER) + "</w:pPr>"
                + "<w:rPr>" + ordered(
                    run + ("<w:b/>" if bold else "") + (f'<w:color w:val="{colour}"/>' if colour else "")
                    + f'<w:sz w:val="{round(size * 2)}"/>', RPR_ORDER) + "</w:rPr></w:style>")

    def rule(side: str, colour: str, weight: int = 4, space: int = 4) -> str:
        return f'<w:{side} w:val="single" w:sz="{weight}" w:space="{space}" w:color="{colour}"/>'

    keep = "<w:keepNext/><w:keepLines/>"
    tab = f'<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="{text_width}"/></w:tabs>'
    code_shade = (f'<w:shd w:val="clear" w:color="auto" w:fill="{colours["shade"]}"/>'
                  '<w:ind w:left="120" w:right="120"/>')
    return "".join([
        f'{XML_HEADER}<w:styles xmlns:w="{W_NS}"><w:docDefaults><w:rPrDefault><w:rPr>{fonts(text_font)}',
        f'<w:color w:val="{colours["text"]}"/><w:sz w:val="{round(sizes["body"] * 2)}"/><w:lang w:val="en-GB"/>',
        '</w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:line="264" w:lineRule="auto"/></w:pPr></w:pPrDefault>',
        "</w:docDefaults>",
        para("Normal", "Normal", sizes["body"], based=None),
        para("CoverBrand", "Cover Brand", sizes["cover_brand"], bold=True, after=120),
        para("CoverTitle", "Cover Title", sizes["cover_title"], after=200,
             extra=f'<w:pBdr>{rule("bottom", colours["accent"], 12, 10)}</w:pBdr>'),
        para("CoverMeta", "Cover Meta", sizes["body"] + 1, colour=colours["secondary"], after=40),
        para("Kicker", "Kicker", sizes["kicker"], bold=True, colour=colours["accent"], after=40,
             extra=keep, run='<w:spacing w:val="40"/>'),
        para("Heading1", "heading 1", sizes["part"], bold=True, after=280,
             extra=keep + f'<w:pBdr>{rule("bottom", colours["accent"], 8, 6)}</w:pBdr><w:outlineLvl w:val="0"/>'),
        para("Heading2", "heading 2", sizes["chapter"], bold=True, before=120, after=80,
             extra=keep + '<w:outlineLvl w:val="1"/>'),
        para("Heading3", "heading 3", sizes["section"], bold=True, before=320, after=100,
             extra=keep + '<w:outlineLvl w:val="2"/>'),
        para("Heading4", "heading 4", sizes["subsection"], bold=True, before=220, after=80,
             extra=keep + '<w:outlineLvl w:val="3"/>'),
        para("FrontHeading", "Front Heading", sizes["chapter"], bold=True, after=240, extra=keep),
        para("ChapterList", "Chapter List", sizes["body"], colour=colours["secondary"], after=30),
        para("TOC1", "toc 1", sizes["body"], bold=True, before=140, after=30, extra=tab),
        para("TOC2", "toc 2", sizes["body"] - 0.5, after=10, extra=tab + '<w:ind w:left="300"/>'),
        para("ListParagraph", "List Paragraph", sizes["list"], after=50),
        para("TableText", "Table Text", sizes["table"], before=30, after=30),
        para("Code", "Code", sizes["code"], after=0, run=fonts(code_font), extra=code_shade),
        para("Meta", "Metadata", sizes["meta"], colour=colours["secondary"], after=200),
        para("Caption", "caption", sizes["caption"], colour=colours["secondary"], after=160),
        para("Header", "header", sizes["meta"], colour=colours["secondary"], after=0,
             extra=f'<w:pBdr>{rule("bottom", colours["rule"])}</w:pBdr>'),
        para("Footer", "footer", sizes["meta"], colour=colours["secondary"], after=0,
             extra=f'<w:pBdr>{rule("top", colours["rule"])}</w:pBdr>'),
        f'<w:style w:type="character" w:styleId="CodeChar"><w:name w:val="Code Char"/><w:rPr>{fonts(code_font)}'
        f'<w:sz w:val="{round((sizes["body"] - 1) * 2)}"/></w:rPr></w:style>',
        '<w:style w:type="character" w:styleId="SymbolChar"><w:name w:val="Symbol Char"/><w:rPr>'
        + fonts((style["fonts"].get("symbols") or style["fonts"]["text"])["name"]) + "</w:rPr></w:style>",
        '<w:style w:type="character" w:styleId="Hyperlink"><w:name w:val="Hyperlink"/>'
        f'<w:rPr><w:color w:val="{colours["accent"]}"/><w:u w:val="single"/></w:rPr></w:style>',
        '<w:style w:type="table" w:styleId="RuledTable"><w:name w:val="Ruled Table"/><w:tblPr><w:tblBorders>',
        rule("top", colours["secondary"], 8, 0), rule("bottom", colours["secondary"], 8, 0),
        rule("insideH", colours["rule"], 4, 0),
        '</w:tblBorders><w:tblCellMar><w:left w:w="70" w:type="dxa"/><w:right w:w="70" w:type="dxa"/>'
        "</w:tblCellMar></w:tblPr></w:style>",
        "</w:styles>",
    ])


ROOT_RELATIONSHIPS = (
    f'{XML_HEADER}<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    f'<Relationship Id="rId1" Type="{R_NS}/officeDocument" Target="word/document.xml"/></Relationships>'
)


def build_docx(
    projection: dict[str, Any],
    pages: dict[str, int] | None = None,
    render_diagram: Callable[[str], bytes] = mermaid.render,
    edition: str = "working",
    style: dict[str, Any] | None = None,
    assets_root: Path = ROOT,
) -> tuple[bytes, list[dict[str, Any]]]:
    """The DOCX bytes and its table-of-contents entries (bookmark, level, text).

    Without `pages` every entry shows a placeholder of fixed width, so that
    filling the real numbers in does not move any page.
    """
    global _symbols
    style = style or load_style()
    symbols = symbol_pattern(style)
    _symbols = re.compile(f"[{symbols}]+") if symbols else None
    document = Document(projection, style, pages, render_diagram, edition, assets_root)
    last_section = document.build()
    for name in ("styles", "numbering", "fontTable"):
        document.relate(f"{R_NS}/{name}", f"{name}.xml")
    body = f"{XML_HEADER}<w:document {NAMESPACES}><w:body>{''.join(document.body)}{last_section}</w:body></w:document>"
    parts = {
        "[Content_Types].xml": document.content_types_xml(),
        "_rels/.rels": ROOT_RELATIONSHIPS,
        "word/document.xml": body,
        "word/_rels/document.xml.rels": document.relationships_xml(),
        "word/styles.xml": styles_xml(style, document.text_width),
        "word/numbering.xml": document.numbering_xml(),
        "word/fontTable.xml": font_table_xml(style),
        "word/footer1.xml": document.footer_xml(),
        **({"word/footer0.xml": document.empty_footer} if document.empty_footer else {}),
        **{f"word/{name}": xml for name, xml in document.headers.items()},
        **{f"word/media/{name}": data for name, data in sorted(document.media.items())},
    }
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as package:
        for name, data in parts.items():
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o644 << 16
            package.writestr(info, data.encode("utf-8") if isinstance(data, str) else data)
    return buffer.getvalue(), document.toc
