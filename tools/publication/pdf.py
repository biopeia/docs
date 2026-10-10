"""Convert the DOCX to PDF with LibreOffice and read where each heading landed.

The table of contents needs real page numbers, and only a rendered document
has them. So the document is rendered once with placeholders, the page of
every listed heading is read from that PDF, and it is rendered again with the
numbers filled in.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unicodedata
from pathlib import Path
from typing import Any


class PdfError(RuntimeError):
    pass


def soffice() -> str | None:
    return shutil.which("soffice") or shutil.which("libreoffice")


def available() -> bool:
    return soffice() is not None and shutil.which("pdftotext") is not None


def tool_versions() -> dict[str, str]:
    def first_line(*command: str) -> str:
        done = subprocess.run(command, capture_output=True, text=True, check=False)
        return ((done.stdout or done.stderr).strip().splitlines() or ["unknown"])[0]

    return {"libreoffice": first_line(soffice() or "soffice", "--version"), "pdftotext": first_line("pdftotext", "-v")}


def convert(docx: bytes) -> bytes:
    """PDF bytes of a DOCX, rendered by LibreOffice in a throwaway profile."""
    binary = soffice()
    if binary is None:
        raise PdfError("LibreOffice (soffice) is needed to render the PDF and is not installed")
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        (work / "document.docx").write_bytes(docx)
        # Its own profile: no state from, and no lock against, another LibreOffice.
        done = subprocess.run(
            [binary, "--headless", f"-env:UserInstallation={(work / 'profile').as_uri()}",
             "--convert-to", "pdf", "--outdir", str(work), str(work / "document.docx")],
            capture_output=True, text=True, check=False, timeout=600,
        )
        output = work / "document.pdf"
        if done.returncode != 0 or not output.is_file():
            raise PdfError(f"LibreOffice did not produce a PDF: {(done.stderr or done.stdout).strip()[:500]}")
        return output.read_bytes()


def page_texts(pdf: bytes) -> list[str]:
    """The text of each page, in order."""
    if shutil.which("pdftotext") is None:
        raise PdfError("pdftotext (poppler-utils) is needed to read page numbers and is not installed")
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "document.pdf"
        path.write_bytes(pdf)
        done = subprocess.run(["pdftotext", "-enc", "UTF-8", str(path), "-"], capture_output=True, check=False)
    if done.returncode != 0:
        raise PdfError(f"pdftotext failed: {done.stderr.decode('utf-8', 'replace').strip()[:500]}")
    pages = done.stdout.decode("utf-8").split("\f")
    return pages[:-1] if pages and not pages[-1].strip() else pages


def _normal(text: str) -> str:
    """Line breaks, runs of spaces and ligatures do not distinguish two texts."""
    return " ".join(unicodedata.normalize("NFKC", text).split())


def locate(toc: list[dict[str, Any]], pages: list[str]) -> dict[str, int]:
    """Page (from 1) of every table-of-contents heading.

    Headings are searched in order, each from where the previous one was
    found. The first sweep runs through the contents list itself, which names
    them all in the same order; the second, starting where the first ended,
    finds the headings in the body. Every listed heading is numbered, so its
    text does not occur in prose that merely mentions the chapter.
    """
    text, starts = "", []
    for page in pages:
        starts.append(len(text))
        text += _normal(page) + " "

    def sweep(position: int, where: str) -> tuple[int, list[int]]:
        found = []
        for entry in toc:
            needle = _normal(entry["text"])
            at = text.find(needle, position)
            if at < 0:
                raise PdfError(f"heading not found in {where}: {entry['text']!r}")
            found.append(at)
            position = at + len(needle)
        return position, found

    end_of_contents, _ = sweep(0, "the contents list")
    _, offsets = sweep(end_of_contents, "the body")
    out = {}
    for entry, offset in zip(toc, offsets):
        out[entry["bookmark"]] = max(i for i, start in enumerate(starts, start=1) if start <= offset)
    return out
