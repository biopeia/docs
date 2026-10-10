#!/usr/bin/env python3
"""Build the Biopeia publication.

Writes under build/publication/ (ignored by Git):

  <id>.json                   the semantic projection: what is published, before presentation
  <output>.docx               the editable document, contents list with real page numbers
  <output>.pdf                the publication
  publication-manifest.json   source revisions, digests, tools and the SHA-256 of each artifact

The PDF is rendered twice: once to learn the page of every heading, once with
those pages in the contents list. The build fails if the second rendering
does not put every heading where the contents list says.

--no-pdf builds without LibreOffice: it writes the projection only and checks
that the document can be assembled. It writes no DOCX, because a contents
list without page numbers is not a publishable document.

--release builds the published edition: every source repository must be
resolved (--repos-root) to a clean revision, or the build fails. Without it
the document is a working edition and says so on its front page.

--check also assembles everything twice and fails when the two differ. The
PDF itself is not compared: LibreOffice stamps each file with a creation time
and an identifier.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mermaid  # noqa: E402
import pdf  # noqa: E402
import qa  # noqa: E402
from docx import build_docx  # noqa: E402
from markdown import MarkdownError  # noqa: E402
from model import MANIFEST  # noqa: E402
from style import STYLE, StyleError, font_substitutions, load_style  # noqa: E402
from projection import ProjectionError, build_projection, projection_bytes, sha256  # noqa: E402
from validate_registry import ROOT  # noqa: E402

MANIFEST_NAME = "publication-manifest.json"


class QualityError(RuntimeError):
    pass


def require(problems: list[str], what: str) -> None:
    if problems:
        raise QualityError(f"{what}:\n" + "\n".join(problems))


def unclean_sources(sources: dict) -> list[str]:
    """Why these sources cannot back a published edition."""
    return [
        f"{name}: {'not resolved to a revision' if source['state'] == 'unresolved' else 'has local modifications'}"
        for name, source in sources.items()
        if source["state"] != "clean"
    ]


def build(
    manifest: Path, repos_root: Path | None, with_pdf: bool, check: bool, release: bool = False
) -> tuple[dict[str, bytes], dict]:
    projection = build_projection(manifest_path=manifest, repos_root=repos_root)
    if release:
        require(unclean_sources(projection["sources"]), "a published edition needs every source at a clean revision")
        unchecked = projection["links"]["unverified"] + projection["links"]["without_revision"]
        require([f"{unchecked} links to code could not be checked against a checkout"] if unchecked else [],
                "a published edition needs every link verified")
    edition = "published" if release else "working"
    projection_json = projection_bytes(projection)
    style = load_style()
    if with_pdf and pdf.soffice() is None:
        # Said first: without it nothing that follows can produce a publication.
        raise pdf.PdfError("LibreOffice (soffice) is needed to render the PDF and is not installed")
    # A projection-only check assembles the document without rendering diagrams,
    # so that it needs neither LibreOffice nor mermaid-cli.
    render = mermaid.render if with_pdf else mermaid.placeholder
    draft, toc = build_docx(projection, edition=edition, style=style, render_diagram=render)
    require(qa.check_docx(draft), "the DOCX package is malformed")
    if check:
        again = build_projection(manifest_path=manifest, repos_root=repos_root)
        if projection_bytes(again) != projection_json or build_docx(again, edition=edition, style=style, render_diagram=render)[0] != draft:
            raise QualityError("two builds from the same sources differ")

    publication = projection["publication"]
    files = {f"{publication['id']}.json": projection_json}
    record = {
        "publication": publication["id"],
        "edition": edition,
        "release": projection["release"],
        "revision": projection["sources"]["docs"]["revision"],
        "sources": projection["sources"],
        "registry_digest": projection["registry_digest"],
        "links": {key: value for key, value in projection["links"].items() if isinstance(value, int)},
        "projection_digest": sha256(projection_json),
        "tools": {"mermaid_cli_pinned": mermaid.PINNED_VERSION},
        # What gave the build its look: the style file and the mark it names.
        "style": {
            "sha256": sha256(STYLE.read_bytes()),
            "logo": {"path": style["logo"]["path"], "sha256": sha256((ROOT / style["logo"]["path"]).read_bytes())},
        },
    }
    if with_pdf:
        substitutions = font_substitutions(style)
        first_pdf = pdf.convert(draft, substitutions)
        first = pdf.locate(toc, pdf.destinations(first_pdf))
        final, _ = build_docx(projection, pages=first, edition=edition, style=style, render_diagram=render)
        require(qa.check_docx(final), "the final DOCX package is malformed")
        rendered = pdf.convert(final, substitutions)
        first_pages, final_pages = pdf.page_texts(first_pdf), pdf.page_texts(rendered)
        require(
            qa.check_pagination(toc, first, pdf.locate(toc, pdf.destinations(rendered)), len(first_pages), len(final_pages)),
            "the contents list does not match the rendered pages",
        )
        require([] if pdf.has_outline(rendered) else ["the PDF has no outline of parts and chapters"],
                "the PDF cannot be navigated")
        title = pdf.properties(rendered).get("Title", "")
        require([] if publication["title"] in title else [f"the PDF title is {title!r}"],
                "the PDF does not carry the publication's title")
        used = pdf.fonts_used(rendered)
        require(qa.check_fonts(used, [font["fallback"] for font in style["fonts"].values()]),
                "the PDF is not set in the typefaces of the style")
        # The page before each part or appendix opens, and the last one.
        terminal = {first[entry["bookmark"]] - 1 for entry in toc if entry["level"] == 1} | {len(final_pages)}
        # A sideways table forces a page break before and after it: the page
        # before a run of sideways pages and the last of the run may be short.
        sideways = pdf.sideways_pages(rendered)
        terminal |= {n - 1 for n in sideways if n - 1 not in sideways} | {n for n in sideways if n + 1 not in sideways}
        problems, sparse = qa.check_density(final_pages, style["qa"], terminal)
        require(problems, "the layout has pathological pages")
        files[f"{publication['output']}.docx"] = final
        files[f"{publication['output']}.pdf"] = rendered
        record["pages"] = len(final_pages)
        fullest = max(qa.body_characters(final_pages))
        record["layout"] = {"sideways_pages": sorted(sideways), "sparse_pages": sparse, "fullest_page_characters": fullest, "typefaces": used}
        record["tools"].update(pdf.tool_versions())
    return files, record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--output", type=Path, default=ROOT / "build" / "publication")
    parser.add_argument("--repos-root", type=Path, help="directory holding the domain checkouts")
    parser.add_argument("--no-pdf", action="store_true", help="projection only; needs no LibreOffice")
    parser.add_argument("--check", action="store_true", help="also assemble twice and compare")
    parser.add_argument("--release", action="store_true", help="published edition: all sources clean, or fail")
    args = parser.parse_args(argv)

    try:
        files, record = build(args.manifest, args.repos_root, not args.no_pdf, args.check, args.release)
    except (ProjectionError, MarkdownError, mermaid.MermaidError, pdf.PdfError, QualityError, StyleError) as exc:
        print(f"Publication: FAIL\n{exc}")
        return 1

    # The only clock in the build, and it is in no digest. SOURCE_DATE_EPOCH pins it.
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    now = datetime.datetime.fromtimestamp(int(epoch), datetime.UTC) if epoch else datetime.datetime.now(datetime.UTC)
    record["generated_at"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    record["artifacts"] = {name: {"sha256": sha256(data), "bytes": len(data)} for name, data in sorted(files.items())}
    files[MANIFEST_NAME] = (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")

    args.output.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (args.output / name).write_bytes(data)
        if name != MANIFEST_NAME:
            print(f"{sha256(data)}  {name}")
    print(f"Publication: PASS, {record['edition']} edition" + (f" ({record['pages']} pages)" if "pages" in record else " (projection only)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
