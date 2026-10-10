"""The editorial style: typefaces, sizes, colours and layout limits.

Style is data (publication/style.yaml), read only by the renderers. The
semantic projection does not know it exists, so a change of style cannot
change what a publication says.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_registry import ROOT, load_strict_yaml  # noqa: E402

STYLE = ROOT / "publication" / "style.yaml"
REQUIRED = {
    "page": ("width_mm", "height_mm", "margin_mm"),
    "fonts": ("text", "code"),
    "colours": ("text", "secondary", "rule", "shade", "accent"),
    "sizes": ("cover_brand", "cover_title", "part", "chapter", "section", "subsection", "body", "list",
              "table", "code", "caption", "meta", "kicker"),
    "qa": ("blank_page_chars", "sparse_page_chars", "max_sparse_share"),
}


class StyleError(ValueError):
    pass


def load_style(path: Path = STYLE) -> dict[str, Any]:
    try:
        style = load_strict_yaml(path)
    except (OSError, ValueError) as exc:
        raise StyleError(str(exc)) from exc
    problems = [
        f"{group}.{key} is missing"
        for group, keys in REQUIRED.items()
        for key in keys
        if key not in (style.get(group) or {})
    ]
    for name, value in (style.get("colours") or {}).items():
        if not re.fullmatch(r"[0-9A-Fa-f]{6}", str(value)):
            problems.append(f"colours.{name} is not a six-digit hex colour")
    for role, font in (style.get("fonts") or {}).items():
        if not (isinstance(font, dict) and font.get("name") and font.get("fallback")):
            problems.append(f"fonts.{role} needs a name and a fallback")
    if problems:
        raise StyleError("\n".join(problems))
    return style


def symbol_pattern(style: dict[str, Any]) -> str:
    """Regular-expression character class of the characters set in the symbols typeface."""
    ranges = (style["fonts"].get("symbols") or {}).get("ranges") or []
    return "".join(f"\\u{low.zfill(4)}-\\u{high.zfill(4)}" for low, high in (r.split("-") for r in ranges))


def font_substitutions(style: dict[str, Any]) -> dict[str, str]:
    """Typeface named in the document -> typeface the PDF is rendered with."""
    return {font["name"]: font["fallback"] for font in style["fonts"].values() if font["name"] != font["fallback"]}
