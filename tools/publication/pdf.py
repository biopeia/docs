"""Convert the DOCX to PDF with LibreOffice and read where each heading landed.

The table of contents needs real page numbers, and only a rendered document
has them. So the document is rendered once with placeholders, the page of
every listed heading is read from that PDF's named destinations, and it is
rendered again with the numbers filled in.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape


class PdfError(RuntimeError):
    pass


def soffice() -> str | None:
    return shutil.which("soffice") or shutil.which("libreoffice")


def available() -> bool:
    return soffice() is not None and all(shutil.which(tool) for tool in ("pdftotext", "pdfinfo", "pdffonts"))


def tool_versions() -> dict[str, str]:
    def first_line(*command: str) -> str:
        done = subprocess.run(command, capture_output=True, text=True, check=False)
        return ((done.stdout or done.stderr).strip().splitlines() or ["unknown"])[0]

    return {"libreoffice": first_line(soffice() or "soffice", "--version"), "pdftotext": first_line("pdftotext", "-v")}


# Bookmarks become named destinations, which is how the page of a heading is
# read back. Images are kept lossless: JPEG turns the white of the mark and of
# a diagram into an off-white box on the page.
EXPORT_FILTER = ('pdf:writer_pdf_Export:{"ExportBookmarksToPDFDestination":{"type":"boolean","value":"true"},'
                 '"UseLosslessCompression":{"type":"boolean","value":"true"}}')


def _substitution_settings(substitutions: dict[str, str]) -> str:
    """LibreOffice settings that always render one typeface as another."""
    pairs = "".join(
        f'<node oor:name="_{index}" oor:op="replace">'
        f'<prop oor:name="ReplaceFont" oor:op="fuse"><value>{escape(name)}</value></prop>'
        f'<prop oor:name="SubstituteFont" oor:op="fuse"><value>{escape(fallback)}</value></prop>'
        '<prop oor:name="Always" oor:op="fuse"><value>true</value></prop>'
        '<prop oor:name="OnScreenOnly" oor:op="fuse"><value>false</value></prop></node>'
        for index, (name, fallback) in enumerate(sorted(substitutions.items()))
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<oor:items xmlns:oor="http://openoffice.org/2001/registry" '
        'xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        '<item oor:path="/org.openoffice.Office.Common/Font/Substitution">'
        '<prop oor:name="Replacement" oor:op="fuse"><value>true</value></prop></item>'
        f'<item oor:path="/org.openoffice.Office.Common/Font/Substitution/FontPairs">{pairs}</item>'
        "</oor:items>\n"
    )


def convert(docx: bytes, substitutions: dict[str, str] | None = None) -> bytes:
    """PDF bytes of a DOCX, rendered by LibreOffice in a throwaway profile.

    `substitutions` maps a typeface the document names to the one it is
    rendered with, on every machine, whether or not the named one is
    installed. That keeps page breaks the same everywhere.
    """
    binary = soffice()
    if binary is None:
        raise PdfError("LibreOffice (soffice) is needed to render the PDF and is not installed")
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        (work / "document.docx").write_bytes(docx)
        # Its own profile: no state from, and no lock against, another LibreOffice.
        if substitutions:
            (work / "profile" / "user").mkdir(parents=True)
            (work / "profile" / "user" / "registrymodifications.xcu").write_text(
                _substitution_settings(substitutions), encoding="utf-8")
        done = subprocess.run(
            [binary, "--headless", f"-env:UserInstallation={(work / 'profile').as_uri()}",
             "--convert-to", EXPORT_FILTER, "--outdir", str(work), str(work / "document.docx")],
            capture_output=True, text=True, check=False, timeout=600,
        )
        output = work / "document.pdf"
        if done.returncode != 0 or not output.is_file():
            raise PdfError(f"LibreOffice did not produce a PDF: {(done.stderr or done.stdout).strip()[:500]}")
        return output.read_bytes()


def _poppler(tool: str, pdf: bytes, *arguments: str) -> bytes:
    if shutil.which(tool) is None:
        raise PdfError(f"{tool} (poppler-utils) is needed to read the PDF and is not installed")
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "document.pdf"
        path.write_bytes(pdf)
        done = subprocess.run([tool, *arguments, str(path), *(["-"] if tool == "pdftotext" else [])],
                              capture_output=True, check=False)
    if done.returncode != 0:
        raise PdfError(f"{tool} failed: {done.stderr.decode('utf-8', 'replace').strip()[:500]}")
    return done.stdout


def destinations(pdf: bytes) -> dict[str, int]:
    """Page (from 1) of every bookmark of the document, read from the PDF's named destinations."""
    out = {}
    for line in _poppler("pdfinfo", pdf, "-dests").decode("utf-8", "replace").splitlines():
        match = re.match(r'\s*(\d+)\s+\[.*\]\s+"(.+)"\s*$', line)
        if match:
            out[match.group(2)] = int(match.group(1))
    return out


def fonts_used(pdf: bytes) -> list[str]:
    """Names of the typefaces embedded in the PDF."""
    lines = _poppler("pdffonts", pdf).decode("utf-8", "replace").splitlines()[2:]
    return sorted({line.split()[0].split("+")[-1] for line in lines if line.split()})


def locate(toc: list[dict[str, Any]], dests: dict[str, int]) -> dict[str, int]:
    """Page of every table-of-contents heading; fails when one has no destination."""
    missing = [entry["text"] for entry in toc if entry["bookmark"] not in dests]
    if missing:
        raise PdfError("headings without a destination in the PDF: " + "; ".join(missing))
    return {entry["bookmark"]: dests[entry["bookmark"]] for entry in toc}


def page_texts(pdf: bytes) -> list[str]:
    """The text of each page, in order."""
    pages = _poppler("pdftotext", pdf, "-enc", "UTF-8").decode("utf-8").split("\f")
    return pages[:-1] if pages and not pages[-1].strip() else pages
