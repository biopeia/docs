"""Parse the Markdown the corpus actually uses into plain blocks.

Supported: headings, paragraphs, bullet and numbered lists with one nested
level, pipe tables, fenced code, and inline code, bold, italic and links.
That is the whole of what the documentation uses today; anything else is
rendered as the text it is. An unclosed code fence is an error.

Blocks and inline runs are plain dicts so every renderer can share them:

  {"type": "heading", "level": 2, "inlines": [...]}
  {"type": "paragraph", "inlines": [...]}
  {"type": "list", "items": [{"level": 0, "ordered": True, "number": 1, "inlines": [...]}]}
  {"type": "table", "header": [[...]], "rows": [[[...]]]}
  {"type": "code", "language": "text", "text": "..."}

  inline run: {"text": "...", "bold": False, "italic": False, "code": False, "href": None}
"""

from __future__ import annotations

import re
from typing import Any

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
FENCE_RE = re.compile(r"^(\s*)```\s*([\w-]*)\s*$")
LIST_RE = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")
TABLE_RULE_RE = re.compile(r"^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$")
INLINE_RE = re.compile(
    r"(?P<tick>`+)(?P<code>.+?)(?P=tick)"
    r"|\*\*(?P<bold>.+?)\*\*"
    r"|\*(?!\s)(?P<italic>[^*]+?)(?<!\s)\*"
    r"|\[(?P<label>[^\]]+)\]\((?P<href>[^)\s]+)\)"
)


class MarkdownError(ValueError):
    """The document cannot be parsed without guessing."""


def parse_inline(text: str, **style: Any) -> list[dict[str, Any]]:
    base = {"bold": False, "italic": False, "code": False, "href": None, **style}
    runs: list[dict[str, Any]] = []
    position = 0
    for match in INLINE_RE.finditer(text):
        if match.start() > position:
            runs.append({**base, "text": text[position : match.start()]})
        if match.group("code") is not None:
            runs.append({**base, "text": match.group("code"), "code": True})
        elif match.group("bold") is not None:
            runs += parse_inline(match.group("bold"), **{**base, "bold": True})
        elif match.group("italic") is not None:
            runs += parse_inline(match.group("italic"), **{**base, "italic": True})
        else:
            runs += parse_inline(match.group("label"), **{**base, "href": match.group("href")})
        position = match.end()
    if position < len(text):
        runs.append({**base, "text": text[position:]})
    return runs


def _flow(lines: list[str]) -> list[dict[str, Any]]:
    """Hard-wrapped source lines are one flow of text."""
    return parse_inline(" ".join(" ".join(lines).split()))


def _cells(line: str) -> list[str]:
    """Split a table row on pipes that are neither escaped nor inside code."""
    cells, current, in_code, i = [], "", False, 0
    line = line.strip()
    while i < len(line):
        char = line[i]
        if char == "\\" and line[i + 1 : i + 2] == "|":
            current, i = current + "|", i + 2
            continue
        if char == "`":
            in_code = not in_code
        if char == "|" and not in_code:
            cells.append(current.strip())
            current = ""
        else:
            current += char
        i += 1
    cells.append(current.strip())
    return cells[1:-1] if line.startswith("|") and line.endswith("|") else cells


def _starts_block(lines: list[str], i: int) -> bool:
    line = lines[i]
    item = LIST_RE.match(line)
    return bool(
        HEADING_RE.match(line)
        or FENCE_RE.match(line)
        or (item and (not item.group(2)[0].isdigit() or item.group(2) == "1."))
        or (line.lstrip().startswith("|") and i + 1 < len(lines) and TABLE_RULE_RE.match(lines[i + 1]))
    )


def parse(text: str) -> list[dict[str, Any]]:
    lines = text.splitlines()
    blocks: list[dict[str, Any]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        fence = FENCE_RE.match(line)
        if fence:
            indent, body = len(fence.group(1)), []
            i += 1
            while i < len(lines) and not FENCE_RE.match(lines[i]):
                body.append(lines[i][indent:] if lines[i][:indent].isspace() else lines[i])
                i += 1
            if i == len(lines):
                raise MarkdownError("code fence is never closed")
            blocks.append({"type": "code", "language": fence.group(2) or "text", "text": "\n".join(body)})
            i += 1
            continue

        heading = HEADING_RE.match(line)
        if heading:
            blocks.append(
                {"type": "heading", "level": len(heading.group(1)), "inlines": parse_inline(heading.group(2))}
            )
            i += 1
            continue

        if line.lstrip().startswith("|") and i + 1 < len(lines) and TABLE_RULE_RE.match(lines[i + 1]):
            header = [parse_inline(c) for c in _cells(line)]
            rows = []
            i += 2
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                cells = [parse_inline(c) for c in _cells(lines[i])]
                # A short or long row is padded or cut to the header's width.
                rows.append((cells + [[]] * len(header))[: len(header)])
                i += 1
            blocks.append({"type": "table", "header": header, "rows": rows})
            continue

        if LIST_RE.match(line):
            items: list[dict[str, Any]] = []
            texts: list[list[str]] = []
            while i < len(lines):
                item = LIST_RE.match(lines[i])
                if FENCE_RE.match(lines[i]):
                    break
                if item:
                    marker = item.group(2)
                    items.append(
                        {
                            "level": 1 if len(item.group(1)) >= 2 else 0,
                            "ordered": marker[0].isdigit(),
                            "number": int(marker[:-1]) if marker[0].isdigit() else None,
                        }
                    )
                    texts.append([item.group(3)])
                elif lines[i].strip():
                    texts[-1].append(lines[i])
                else:
                    # A blank line ends the list unless the list goes on after it.
                    following = next((l for l in lines[i + 1 :] if l.strip()), "")
                    if not (LIST_RE.match(following) or following[:1].isspace()) or FENCE_RE.match(following):
                        break
                i += 1
            for entry, text in zip(items, texts):
                entry["inlines"] = _flow(text)
            blocks.append({"type": "list", "items": items})
            continue

        paragraph = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not _starts_block(lines, i):
            paragraph.append(lines[i])
            i += 1
        blocks.append({"type": "paragraph", "inlines": _flow(paragraph)})
    return blocks
