"""Render a publication projection as a DOCX package.

The package is written as plain OpenXML with the standard library, so the
same projection always gives the same bytes: fixed entry order, fixed entry
timestamps, no clock and no random identifiers.

Biopeia has no visual style yet. The styles below are the neutral minimum a
word processor needs to lay the text out (one metric-stable typeface family,
a size per heading level, a grid for tables). They are placeholders, not a
design decision; see publication/README.md.

The table of contents is materialised text, not a field: a field would only
be filled in by a person opening the file. build_docx therefore takes the
page of each entry from the caller, who reads them from a first PDF pass.
"""

from __future__ import annotations

import io
import posixpath
import zipfile
from typing import Any, Callable
from xml.sax.saxutils import escape, quoteattr

import markdown
import mermaid

# A4 in twentieths of a point, with one-inch margins.
PAGE_WIDTH, PAGE_HEIGHT, MARGIN = 11906, 16838, 1440
TEXT_WIDTH = PAGE_WIDTH - 2 * MARGIN
EMU_PER_TWIP, EMU_PER_PIXEL = 635, 9525
MAX_IMAGE_HEIGHT = (PAGE_HEIGHT - 2 * MARGIN) * EMU_PER_TWIP * 8 // 10
PAGE_PLACEHOLDER = "000"

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


# What the front page says about the build. A published edition is one whose
# every source is a clean, identified revision; publish.py enforces it.
EDITIONS = {
    "working": ("Working edition.", "Built from whatever state the sources were in. A repository below may be "
                "unresolved or carry local modifications, so this copy must not be cited as a state of Biopeia."),
    "published": ("Published edition.", "Every source repository below is a clean, identified revision."),
}


def roman(number: int) -> str:
    out = ""
    for value, symbol in ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
                          (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while number >= value:
            out, number = out + symbol, number - value
    return out


def plain(inlines: list[dict[str, Any]]) -> str:
    return "".join(run["text"] for run in inlines)


def text_run(text: str, bold: bool = False, italic: bool = False, code: bool = False, link: bool = False) -> str:
    style = "CodeChar" if code else "Hyperlink" if link else ""
    props = (f'<w:rStyle w:val="{style}"/>' if style else "") + ("<w:b/>" if bold else "") + ("<w:i/>" if italic else "")
    return f'<w:r>{f"<w:rPr>{props}</w:rPr>" if props else ""}<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


def cell(text: Any, code: bool = False) -> list[dict[str, Any]]:
    """One table cell of plain text, as inline runs."""
    return [{"text": str(text), "bold": False, "italic": False, "code": code, "href": None}]


def paragraph(style: str, content: str, properties: str = "") -> str:
    return f'<w:p><w:pPr><w:pStyle w:val="{style}"/>{properties}</w:pPr>{content}</w:p>'


class Document:
    """Accumulates the body and the parts it refers to."""

    def __init__(self, projection: dict[str, Any], pages: dict[str, int] | None,
                 render_diagram: Callable[[str], bytes], edition: str = "working") -> None:
        self.projection = projection
        self.edition = edition
        self.pages = pages
        self.render_diagram = render_diagram
        self.body: list[str] = []
        self.toc: list[dict[str, Any]] = []
        self.relationships: list[tuple[str, str, str, bool]] = []  # id, type, target, external
        self.media: dict[str, bytes] = {}
        self.ordered_lists: list[int] = []  # start number of each numbered list, in order
        self.bookmarks = 0
        # Links between published chapters become links inside the document.
        self.chapter_bookmarks: dict[str, str] = {}

    def relate(self, kind: str, target: str, external: bool = False) -> str:
        for rid, known_kind, known_target, _ in self.relationships:
            if (known_kind, known_target) == (kind, target):
                return rid
        rid = f"rId{len(self.relationships) + 1}"
        self.relationships.append((rid, kind, target, external))
        return rid

    # --- inline ---------------------------------------------------------------

    def runs(self, inlines: list[dict[str, Any]], base: str, bold: bool = False) -> str:
        out = []
        for run in inlines:
            href = run["href"]
            anchor = None
            if href and not href.startswith(("http://", "https://", "mailto:")):
                target = posixpath.normpath(posixpath.join(base, href.split("#", 1)[0]))
                anchor = self.chapter_bookmarks.get(target)
            linked = bool(anchor) or bool(href and href.startswith(("http://", "https://", "mailto:")))
            xml = text_run(run["text"], bold or run["bold"], run["italic"], run["code"], link=linked and not run["code"])
            if anchor:
                xml = f'<w:hyperlink w:anchor="{anchor}">{xml}</w:hyperlink>'
            elif linked:
                rid = self.relate(f"{R_NS}/hyperlink", href, external=True)
                xml = f'<w:hyperlink r:id="{rid}">{xml}</w:hyperlink>'
            # A link to a document that is not part of the publication stays as its text.
            out.append(xml)
        return "".join(out)

    # --- blocks ---------------------------------------------------------------

    def heading(self, level: int, text: str, bookmark: str | None = None, listed: bool = False) -> None:
        content = text_run(text)
        if bookmark:
            self.bookmarks += 1
            content = (f'<w:bookmarkStart w:id="{self.bookmarks}" w:name="{bookmark}"/>{content}'
                       f'<w:bookmarkEnd w:id="{self.bookmarks}"/>')
            if listed:
                self.toc.append({"bookmark": bookmark, "level": level, "text": text})
        self.body.append(paragraph(HEADING_STYLES[min(level, 4)], content))

    def table(self, block: dict[str, Any], base: str) -> None:
        rows = [block["header"], *block["rows"]]
        # Column widths follow the longest cell of each column, within bounds,
        # so an identifier column does not take as much room as a prose one.
        weights = [max(6, min(60, max(len(plain(row[c])) for row in rows))) for c in range(len(block["header"]))]
        widths = [TEXT_WIDTH * weight // sum(weights) for weight in weights]
        xml = ['<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="5000" w:type="pct"/>'
               '<w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid>']
        xml += [f'<w:gridCol w:w="{width}"/>' for width in widths]
        xml.append("</w:tblGrid>")
        for index, row in enumerate(rows):
            xml.append("<w:tr>" + ("<w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>" if index == 0 else "<w:trPr><w:cantSplit/></w:trPr>"))
            for width, cell in zip(widths, row):
                xml.append(f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/></w:tcPr>'
                           + paragraph("TableText", self.runs(cell, base, bold=index == 0)) + "</w:tc>")
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
        for line in block["text"].split("\n"):
            self.body.append(paragraph("Code", text_run(line)))
        self.body.append(paragraph("TableText", ""))

    def diagram(self, source: str) -> None:
        data = self.render_diagram(source)
        width, height = mermaid.png_size(data)
        cx, cy = width * EMU_PER_PIXEL // mermaid.SCALE, height * EMU_PER_PIXEL // mermaid.SCALE
        shrink = min(1.0, TEXT_WIDTH * EMU_PER_TWIP / cx, MAX_IMAGE_HEIGHT / cy)
        cx, cy = int(cx * shrink), int(cy * shrink)
        number = len(self.media) + 1
        name = f"diagram-{number}.png"
        self.media[name] = data
        rid = self.relate(f"{R_NS}/image", f"media/{name}")
        self.body.append(
            '<w:p><w:pPr><w:pStyle w:val="Normal"/><w:jc w:val="center"/></w:pPr><w:r><w:drawing>'
            f'<wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>'
            f'<wp:docPr id="{number}" name="Diagram {number}"/>'
            '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:pic><pic:nvPicPr><pic:cNvPr id="{number}" name="{name}"/><pic:cNvPicPr/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
            "</a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>"
        )

    def chapter_body(self, chapter: dict[str, Any]) -> None:
        try:
            blocks = markdown.parse(chapter["markdown"])
        except markdown.MarkdownError as exc:
            raise markdown.MarkdownError(f"{chapter['source']}: {exc}") from exc
        base = chapter["base"]
        for block in blocks:
            if block["type"] == "heading":
                # '##' in a document is one level below its chapter heading.
                self.heading(block["level"] + 1, plain(block["inlines"]))
            elif block["type"] == "paragraph":
                self.body.append(paragraph("Normal", self.runs(block["inlines"], base)))
            elif block["type"] == "list":
                self.list(block, base)
            elif block["type"] == "table":
                self.table(block, base)
            else:
                self.code(block)

    # --- whole document -------------------------------------------------------

    def outline(self) -> list[dict[str, Any]]:
        """Numbered headings of every section and chapter, in order."""
        out, part, appendix, chapter_number = [], 0, 0, 0
        for section in self.projection["sections"]:
            if section["group"] == "parts":
                part += 1
                label = f"Part {roman(part)} — {section['title']}"
            else:
                appendix += 1
                label = f"Appendix {chr(64 + appendix)} — {section['title']}"
            entry = {"label": label, "bookmark": f"section_{len(out) + 1}", "chapters": []}
            # An appendix made of one chapter is that chapter: no second heading.
            merged = section["group"] == "appendices" and len(section["chapters"]) == 1
            for index, chapter in enumerate(section["chapters"], start=1):
                if section["group"] == "parts":
                    chapter_number += 1
                    title = f"{chapter_number}. {chapter['title']}"
                else:
                    title = f"{chr(64 + appendix)}.{index} {chapter['title']}"
                bookmark = entry["bookmark"] if merged else f"chapter_{chapter['id'].replace('-', '_')}"
                entry["chapters"].append({"chapter": chapter, "label": None if merged else title, "bookmark": bookmark})
                if not chapter["generated"]:
                    self.chapter_bookmarks[chapter["source"]] = bookmark
            out.append(entry)
        return out

    def front_matter(self, outline: list[dict[str, Any]]) -> None:
        publication, sources = self.projection["publication"], self.projection["sources"]
        self.body.append(paragraph("Title", text_run(publication["title"])))
        if publication.get("subtitle"):
            self.body.append(paragraph("Subtitle", text_run(publication["subtitle"])))
        self.body.append(paragraph("Normal", text_run(EDITIONS[self.edition][0], bold=True)
                                   + text_run(" " + EDITIONS[self.edition][1])))
        self.body.append(paragraph("Normal", text_run(
            "This document is generated. It presents the Biopeia documentation in reading order; the "
            "documents and registries of the documentation repository remain the only source. It was built "
            "from the revisions below. A repository marked unresolved was not available to the build.")))
        rows = []
        for name, source in sources.items():
            state = {"clean": "", "modified": "with local modifications", "unresolved": "unresolved"}[source["state"]]
            rows.append([cell(name), cell(source["revision"] or "—", code=bool(source["revision"])), cell(state)])
        self.table({"header": [cell(t) for t in ("Repository", "Revision", "State")], "rows": rows}, "")
        inventory = self.projection.get("inventory") or {}
        if inventory:
            self.body.append(paragraph("Normal", text_run("What this publication holds:")))
            self.table({"header": [cell("Inventory"), cell("Count")],
                        "rows": [[cell(label), cell(count)] for label, count in inventory.items()]}, "")

        self.body.append(paragraph("ContentsHeading", text_run("Contents"), "<w:pageBreakBefore/>"))
        entries = []
        for section in outline:
            entries.append((1, section["label"], section["bookmark"]))
            entries += [(2, c["label"], c["bookmark"]) for c in section["chapters"] if c["label"]]
        for level, label, bookmark in entries:
            page = str(self.pages[bookmark]) if self.pages is not None else PAGE_PLACEHOLDER
            link = (f'<w:hyperlink w:anchor="{bookmark}">{text_run(label)}<w:r><w:tab/></w:r>{text_run(page)}</w:hyperlink>')
            self.body.append(paragraph(f"TOC{level}", link))

    def build(self) -> None:
        outline = self.outline()
        self.front_matter(outline)
        for section in outline:
            self.heading(1, section["label"], section["bookmark"], listed=True)
            for entry in section["chapters"]:
                if entry["label"]:
                    self.heading(2, entry["label"], entry["bookmark"], listed=True)
                if not entry["chapter"]["generated"]:
                    self.body.append(paragraph("SourceLine", text_run("Source: ")
                                               + text_run(entry["chapter"]["source"], code=True)))
                self.chapter_body(entry["chapter"])

    # --- parts of the package -------------------------------------------------

    def document_xml(self) -> str:
        footer = self.relate(f"{R_NS}/footer", "footer1.xml")
        header = self.relate(f"{R_NS}/header", "header1.xml")
        section = (f'<w:sectPr><w:headerReference w:type="default" r:id="{header}"/>'
                   f'<w:footerReference w:type="default" r:id="{footer}"/>'
                   f'<w:pgSz w:w="{PAGE_WIDTH}" w:h="{PAGE_HEIGHT}"/>'
                   f'<w:pgMar w:top="{MARGIN}" w:right="{MARGIN}" w:bottom="{MARGIN}" w:left="{MARGIN}" '
                   'w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>')
        return f"{XML_HEADER}<w:document {NAMESPACES}><w:body>{''.join(self.body)}{section}</w:body></w:document>"

    def header_xml(self) -> str:
        publication = self.projection["publication"]
        title = " — ".join(t for t in (publication["title"], publication.get("subtitle")) if t)
        text = f"{title} · {EDITIONS[self.edition][0].rstrip('.')}"
        return (f'{XML_HEADER}<w:hdr xmlns:w="{W_NS}"><w:p><w:pPr><w:pStyle w:val="Header"/></w:pPr>'
                f"{text_run(text)}</w:p></w:hdr>")

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
            indent = 720 * (index + 1)
            return (f'<w:lvl w:ilvl="{index}"><w:start w:val="1"/><w:numFmt w:val="{fmt}"/>'
                    f'<w:lvlText w:val="{text}"/><w:lvlJc w:val="left"/>'
                    f'<w:pPr><w:ind w:left="{indent}" w:hanging="360"/></w:pPr></w:lvl>')

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


def styles_xml() -> str:
    def para(style_id: str, name: str, size: int, *, bold: bool = False, before: int = 0, after: int = 120,
             extra: str = "", run: str = "", based: str | None = "Normal") -> str:
        return (f'<w:style w:type="paragraph" w:styleId="{style_id}"><w:name w:val="{name}"/>'
                + (f'<w:basedOn w:val="{based}"/>' if based else "")
                + f'<w:pPr><w:spacing w:before="{before}" w:after="{after}"/>{extra}</w:pPr>'
                + f'<w:rPr>{run}{"<w:b/>" if bold else ""}<w:sz w:val="{size}"/></w:rPr></w:style>')

    keep = "<w:keepNext/>"
    mono = '<w:rFonts w:ascii="Liberation Mono" w:hAnsi="Liberation Mono" w:cs="Liberation Mono"/>'
    tab = f'<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="{TEXT_WIDTH}"/></w:tabs>'
    border = "".join(f'<w:{side} w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
                     for side in ("top", "left", "bottom", "right", "insideH", "insideV"))
    return "".join([
        f'{XML_HEADER}<w:styles xmlns:w="{W_NS}"><w:docDefaults><w:rPrDefault><w:rPr>',
        '<w:rFonts w:ascii="Liberation Serif" w:hAnsi="Liberation Serif" w:cs="Liberation Serif"/>',
        '<w:sz w:val="22"/><w:lang w:val="en-GB"/></w:rPr></w:rPrDefault></w:docDefaults>',
        para("Normal", "Normal", 22, based=None),
        para("Title", "Title", 56, bold=True, before=2400, after=240),
        para("Subtitle", "Subtitle", 28, after=720),
        para("Heading1", "heading 1", 36, bold=True, after=240, extra=keep + '<w:pageBreakBefore/><w:outlineLvl w:val="0"/>'),
        para("Heading2", "heading 2", 30, bold=True, after=200, extra=keep + '<w:pageBreakBefore/><w:outlineLvl w:val="1"/>'),
        para("Heading3", "heading 3", 26, bold=True, before=280, extra=keep + '<w:outlineLvl w:val="2"/>'),
        para("Heading4", "heading 4", 22, bold=True, before=200, extra=keep + '<w:outlineLvl w:val="3"/>'),
        para("ContentsHeading", "Contents Heading", 36, bold=True, after=240),
        para("TOC1", "toc 1", 22, bold=True, before=120, after=40, extra=tab),
        para("TOC2", "toc 2", 22, after=20, extra=tab + '<w:ind w:left="360"/>'),
        para("ListParagraph", "List Paragraph", 22, after=60),
        para("TableText", "Table Text", 18, after=0),
        para("Code", "Code", 15, after=0, run=mono),
        para("Footer", "footer", 18, after=0, extra='<w:jc w:val="center"/>'),
        para("Header", "header", 18, after=0, extra='<w:jc w:val="right"/>'),
        para("SourceLine", "Source Line", 18, after=200),
        f'<w:style w:type="character" w:styleId="CodeChar"><w:name w:val="Code Char"/><w:rPr>{mono}</w:rPr></w:style>',
        '<w:style w:type="character" w:styleId="Hyperlink"><w:name w:val="Hyperlink"/>'
        '<w:rPr><w:u w:val="single"/></w:rPr></w:style>',
        '<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/><w:tblPr>'
        f'<w:tblBorders>{border}</w:tblBorders><w:tblCellMar><w:left w:w="80" w:type="dxa"/>'
        '<w:right w:w="80" w:type="dxa"/></w:tblCellMar></w:tblPr></w:style>',
        "</w:styles>",
    ])


CONTENT_TYPES = (
    f'{XML_HEADER}<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Default Extension="png" ContentType="image/png"/>'
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
    '<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>'
    '<Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>'
    '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
    "</Types>"
)
ROOT_RELATIONSHIPS = (
    f'{XML_HEADER}<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    f'<Relationship Id="rId1" Type="{R_NS}/officeDocument" Target="word/document.xml"/></Relationships>'
)
def _field(instruction: str) -> str:
    return ('<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
            f'<w:r><w:instrText xml:space="preserve"> {instruction} </w:instrText></w:r>'
            '<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>1</w:t></w:r>'
            '<w:r><w:fldChar w:fldCharType="end"/></w:r>')


FOOTER = (
    f'{XML_HEADER}<w:ftr xmlns:w="{W_NS}"><w:p><w:pPr><w:pStyle w:val="Footer"/></w:pPr>'
    f'{text_run("Page ")}{_field("PAGE")}{text_run(" of ")}{_field("NUMPAGES")}</w:p></w:ftr>'
)


def build_docx(
    projection: dict[str, Any],
    pages: dict[str, int] | None = None,
    render_diagram: Callable[[str], bytes] = mermaid.render,
    edition: str = "working",
) -> tuple[bytes, list[dict[str, Any]]]:
    """The DOCX bytes and its table-of-contents entries (bookmark, level, text).

    Without `pages` every entry shows a placeholder of fixed width, so that
    filling the real numbers in does not move any page.
    """
    document = Document(projection, pages, render_diagram, edition)
    document.build()
    document.relate(f"{R_NS}/styles", "styles.xml")
    document.relate(f"{R_NS}/numbering", "numbering.xml")
    body = document.document_xml()
    parts = {
        "[Content_Types].xml": CONTENT_TYPES,
        "_rels/.rels": ROOT_RELATIONSHIPS,
        "word/document.xml": body,
        "word/_rels/document.xml.rels": document.relationships_xml(),
        "word/styles.xml": styles_xml(),
        "word/numbering.xml": document.numbering_xml(),
        "word/footer1.xml": FOOTER,
        "word/header1.xml": document.header_xml(),
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
