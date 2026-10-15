#!/usr/bin/env python3
"""Validate frontmatter on the procedure's opted-in Markdown records.

The validator intentionally does not scan all documentation. Its scope is the
procedure design, ADR-0111, and numbered decision notes in technical/.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "id", "title", "document_type", "owner", "created", "language", "document_version"
}
ID_PATTERNS = {
    "design": re.compile(r"^design\.[a-z0-9-]+\.[a-z0-9.-]+$"),
    "adr": re.compile(r"^ADR-\d{4}$"),
    "decision_note": re.compile(r"^DN-\d{4}$"),
}
GITHUB_ISSUE_OR_PR = re.compile(
    r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/(?:issues|pull)/\d+$"
)
FORBIDDEN_LIFECYCLE_FIELDS = {"status", "implementation_status", "architecture_scope"}


def procedure_documents(docs_root: Path) -> list[Path]:
    """Return only the procedure's canonical design, ADR, and DN records."""
    paths = [
        docs_root / "technical/design/governance/design-first-work-and-governance-procedure-v1.md",
        docs_root / "technical/adr/ADR-0111-design-first-work-and-governance-procedure.md",
    ]
    notes = docs_root / "technical/decision-notes"
    if notes.is_dir():
        paths.extend(sorted(notes.glob("DN-*.md")))
    return paths


def parse_frontmatter(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None, "missing opening YAML frontmatter delimiter"
    _, separator, remainder = text[4:].partition("\n---\n")
    if not separator:
        return None, "missing closing YAML frontmatter delimiter"
    try:
        data = yaml.safe_load(remainder.split("\n", 1)[0] if False else text[4 : 4 + text[4:].index("\n---\n")])
    except (yaml.YAMLError, ValueError) as exc:
        return None, f"invalid YAML frontmatter: {exc}"
    if not isinstance(data, dict):
        return None, "frontmatter must be a YAML mapping"
    return data, None


def validate_documents(docs_root: Path, paths: list[Path] | None = None) -> tuple[list[str], list[str]]:
    """Return structural errors and informational external-reference warnings."""
    errors: list[str] = []
    warnings: list[str] = []
    seen: dict[str, Path] = {}
    for path in paths if paths is not None else procedure_documents(docs_root):
        where = path.relative_to(docs_root).as_posix()
        if not path.is_file():
            errors.append(f"{where}: required procedure document is missing")
            continue
        metadata, parse_error = parse_frontmatter(path)
        if parse_error:
            errors.append(f"{where}: {parse_error}")
            continue
        assert metadata is not None
        missing = REQUIRED - metadata.keys()
        if missing:
            errors.append(f"{where}: missing required fields {sorted(missing)}")
        for field in FORBIDDEN_LIFECYCLE_FIELDS & metadata.keys():
            errors.append(f"{where}: {field!r} duplicates lifecycle authority and is forbidden")

        kind = metadata.get("document_type")
        identifier = metadata.get("id")
        if kind not in ID_PATTERNS:
            errors.append(f"{where}: document_type must be one of {sorted(ID_PATTERNS)}")
        elif not isinstance(identifier, str) or not ID_PATTERNS[kind].fullmatch(identifier):
            errors.append(f"{where}: id {identifier!r} is invalid for document_type {kind!r}")
        elif identifier in seen:
            errors.append(f"{where}: duplicate id {identifier!r}; first used by {seen[identifier]}")
        else:
            seen[identifier] = path

        for field in ("title", "owner", "language"):
            if field in metadata and (not isinstance(metadata[field], str) or not metadata[field].strip()):
                errors.append(f"{where}: {field} must be a non-empty string")
        if "created" in metadata:
            value = metadata["created"]
            if not isinstance(value, (date, str)) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(value)):
                errors.append(f"{where}: created must be an ISO date (YYYY-MM-DD)")
            else:
                try:
                    date.fromisoformat(str(value))
                except ValueError:
                    errors.append(f"{where}: created is not a calendar date")
        if "document_version" in metadata and (
            not isinstance(metadata["document_version"], int) or metadata["document_version"] < 1
        ):
            errors.append(f"{where}: document_version must be a positive integer")

        relations = metadata.get("relations", [])
        if relations is None:
            errors.append(f"{where}: omit relations when none exist; do not use null")
        elif not isinstance(relations, list):
            errors.append(f"{where}: relations must be a list when present")
        else:
            for index, relation in enumerate(relations):
                label = f"{where}: relations[{index}]"
                if not isinstance(relation, dict):
                    errors.append(f"{label} must be a mapping")
                    continue
                relation_type = relation.get("type")
                if relation_type in {"design", "adr", "decision_note"}:
                    target = relation.get("path")
                    if not isinstance(target, str) or not target:
                        errors.append(f"{label} requires a local path for type {relation_type!r}")
                    elif Path(target).is_absolute() or ".." in Path(target).parts:
                        errors.append(f"{label} path must be repository-relative and stay within Docs")
                    elif not (docs_root / target).is_file():
                        errors.append(f"{label} references missing local document {target!r}")
                elif relation_type in {"issue", "pull_request"}:
                    url = relation.get("url")
                    if not isinstance(url, str) or not GITHUB_ISSUE_OR_PR.fullmatch(url):
                        warnings.append(f"{label} external GitHub link is absent or non-canonical; not fetched")
                else:
                    errors.append(f"{label} has unsupported type {relation_type!r}")
    return errors, warnings


def main() -> int:
    errors, warnings = validate_documents(ROOT)
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        print("Procedure frontmatter validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(f"Procedure frontmatter validation passed ({len(procedure_documents(ROOT))} documents).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
