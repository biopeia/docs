#!/usr/bin/env python3
"""Build the Biopeia publication.

Writes under build/publication/ (ignored by Git):

  <id>.json       the semantic projection: what is published, before presentation
  <output>.docx   the editable document, rendered from the projection

Run with --check to build twice and fail when the two builds differ.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import MANIFEST  # noqa: E402
import qa  # noqa: E402
from docx import build_docx  # noqa: E402
from markdown import MarkdownError  # noqa: E402
from mermaid import MermaidError  # noqa: E402
from projection import ProjectionError, build_projection, projection_bytes, sha256  # noqa: E402
from validate_registry import ROOT  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--output", type=Path, default=ROOT / "build" / "publication")
    parser.add_argument("--repos-root", type=Path, help="directory holding the domain checkouts")
    parser.add_argument("--check", action="store_true", help="build twice and compare")
    args = parser.parse_args(argv)

    def build() -> dict[str, bytes]:
        projection = build_projection(manifest_path=args.manifest, repos_root=args.repos_root)
        docx, _toc = build_docx(projection)
        problems = qa.check_docx(docx)
        if problems:
            raise ProjectionError("the DOCX package is malformed:\n" + "\n".join(problems))
        return {
            f"{projection['publication']['id']}.json": projection_bytes(projection),
            f"{projection['publication']['output']}.docx": docx,
        }

    try:
        files = build()
        if args.check and build() != files:
            print("Publication: FAIL (two builds from the same sources differ)")
            return 1
    except (ProjectionError, MarkdownError, MermaidError) as exc:
        print(f"Publication: FAIL\n{exc}")
        return 1
    args.output.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (args.output / name).write_bytes(data)
        print(f"{sha256(data)}  {name}")
    print("Publication: PASS" + (" (deterministic)" if args.check else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
