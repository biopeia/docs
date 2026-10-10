"""Mechanical checks of what the publisher produced. Each returns a list of problems."""

from __future__ import annotations

import io
import posixpath
import re
import zipfile
from xml.etree import ElementTree

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
PKG = "{http://schemas.openxmlformats.org/package/2006/relationships}"


def check_docx(data: bytes) -> list[str]:
    """Package opens, every part is well-formed, and nothing points at something absent."""
    try:
        package = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile as exc:
        return [f"not a zip package: {exc}"]
    problems: list[str] = []
    names = package.namelist()
    if len(names) != len(set(names)):
        problems.append("package holds a part twice")
    trees = {}
    for name in names:
        if name.endswith((".xml", ".rels")):
            try:
                trees[name] = ElementTree.fromstring(package.read(name))
            except ElementTree.ParseError as exc:
                problems.append(f"{name}: not well-formed XML: {exc}")
    for required in ("[Content_Types].xml", "_rels/.rels", "word/document.xml", "word/styles.xml"):
        if required not in names:
            problems.append(f"missing part {required}")
    document, rels = trees.get("word/document.xml"), trees.get("word/_rels/document.xml.rels")
    if document is None or rels is None:
        return problems + ["document or its relationships are unreadable"]

    targets = {}
    for rel in rels.iter(f"{PKG}Relationship"):
        targets[rel.get("Id")] = rel
        if rel.get("TargetMode") != "External" and posixpath.join("word", rel.get("Target")) not in names:
            problems.append(f"relationship {rel.get('Id')} points at missing part {rel.get('Target')}")
    for element in document.iter():
        for attribute in (f"{R}id", f"{R}embed"):
            rid = element.get(attribute)
            if rid and rid not in targets:
                problems.append(f"document uses unknown relationship {rid}")

    bookmarks = [b.get(f"{W}name") for b in document.iter(f"{W}bookmarkStart")]
    if len(bookmarks) != len(set(bookmarks)):
        problems.append("a bookmark name is used twice")
    for link in document.iter(f"{W}hyperlink"):
        anchor = link.get(f"{W}anchor")
        if anchor and anchor not in bookmarks:
            problems.append(f"internal link points at missing bookmark {anchor}")

    styles = {s.get(f"{W}styleId") for s in trees.get("word/styles.xml", ElementTree.Element("x")).iter(f"{W}style")}
    used = {e.get(f"{W}val") for tag in ("pStyle", "rStyle", "tblStyle") for e in document.iter(f"{W}{tag}")}
    for style in sorted(used - styles):
        problems.append(f"document uses undefined style {style}")

    numbering = trees.get("word/numbering.xml")
    nums = {n.get(f"{W}numId") for n in numbering.iter(f"{W}num")} if numbering is not None else set()
    for num in {e.get(f"{W}val") for e in document.iter(f"{W}numId")} - nums:
        problems.append(f"document uses undefined list numbering {num}")
    if re.search(rb"[\x00-\x08\x0b\x0c\x0e-\x1f]", package.read("word/document.xml")):
        problems.append("document contains control characters")
    return problems


def check_pagination(
    toc: list[dict], first: dict[str, int], final: dict[str, int], first_pages: int, final_pages: int
) -> list[str]:
    """The page numbers printed in the contents list are the pages of the final PDF."""
    problems = []
    if first_pages != final_pages:
        problems.append(f"page count changed between passes: {first_pages} then {final_pages}")
    previous = 0
    for entry in toc:
        bookmark = entry["bookmark"]
        if first.get(bookmark) != final.get(bookmark):
            problems.append(
                f"{entry['text']!r} is listed on page {first.get(bookmark)} but is on page {final.get(bookmark)}"
            )
        if final.get(bookmark, 0) < previous:
            problems.append(f"{entry['text']!r} comes before the heading that precedes it")
        previous = final.get(bookmark, previous)
    return problems


def check_density(pages: list[str], limits: dict) -> tuple[list[str], list[int]]:
    """Problems that fail the build, and the pages that are merely sparse.

    A page is measured by the characters of its body: its first line (the
    running header) and its last two (the footer) are left out. The cover is
    exempt. A page with nothing on it is a layout fault; many sparse pages
    mean the layout wastes paper.
    """
    counts = []
    for page in pages:
        lines = [line for line in page.splitlines() if line.strip()]
        counts.append(len("".join("".join(lines[2:-2]).split())))
    blank = [n for n, count in enumerate(counts, start=1) if n > 1 and count < limits["blank_page_chars"]]
    sparse = [n for n, count in enumerate(counts, start=1) if n > 1 and count < limits["sparse_page_chars"]]
    problems = [f"page {n} is empty or nearly so" for n in blank]
    if pages and len(sparse) / len(pages) > limits["max_sparse_share"]:
        problems.append(
            f"{len(sparse)} of {len(pages)} pages are sparse, more than the {limits['max_sparse_share']:.0%} allowed"
        )
    return problems, sparse


def check_fonts(used: list[str], expected: list[str]) -> list[str]:
    """The PDF is set only in the typefaces the style names as fallbacks."""
    allowed = {name.replace(" ", "") for name in expected}
    strays = [font for font in used if not any(font.startswith(name) for name in allowed)]
    return [f"PDF uses a typeface the style does not name: {font}" for font in strays]
