from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_procedure_frontmatter import validate_documents  # noqa: E402


def write_doc(root: Path, relative: str, frontmatter: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}\n---\n\n# Example\n", encoding="utf-8")
    return path


def valid_metadata(identifier: str = "DN-0001", kind: str = "decision_note") -> str:
    return f"""id: {identifier}
title: Example record
document_type: {kind}
owner: project-owner
created: 2026-10-12
language: en
document_version: 1"""


def test_valid_frontmatter_and_optional_external_relations(tmp_path: Path) -> None:
    path = write_doc(
        tmp_path,
        "technical/decision-notes/DN-0001.md",
        valid_metadata()
        + "\nrelations:\n  - type: pull_request\n    url: https://github.com/biopeia/docs/pull/135",
    )
    errors, warnings = validate_documents(tmp_path, [path])
    assert errors == []
    assert warnings == []


def test_missing_and_invalid_fields_are_reported(tmp_path: Path) -> None:
    path = write_doc(tmp_path, "technical/decision-notes/DN-0001.md", "id: invalid\ndocument_type: unknown")
    errors, _ = validate_documents(tmp_path, [path])
    assert any("missing required fields" in error for error in errors)
    assert any("document_type" in error for error in errors)


def test_duplicate_ids_and_forbidden_lifecycle_metadata_are_reported(tmp_path: Path) -> None:
    first = write_doc(tmp_path, "technical/decision-notes/DN-0001.md", valid_metadata())
    second = write_doc(
        tmp_path,
        "technical/decision-notes/DN-0002.md",
        valid_metadata() + "\nstatus: accepted",
    )
    errors, _ = validate_documents(tmp_path, [first, second])
    assert any("duplicate id" in error for error in errors)
    assert any("status" in error for error in errors)


def test_missing_local_reference_fails_but_noncanonical_external_is_warning(tmp_path: Path) -> None:
    path = write_doc(
        tmp_path,
        "technical/decision-notes/DN-0001.md",
        valid_metadata()
        + "\nrelations:\n  - type: adr\n    path: technical/adr/ADR-9999-missing.md"
        + "\n  - type: issue\n    url: https://github.com/biopeia/docs/issues/latest",
    )
    errors, warnings = validate_documents(tmp_path, [path])
    assert any("missing local document" in error for error in errors)
    assert any("not fetched" in warning for warning in warnings)


def test_repository_records_pass_and_global_scan_is_narrow() -> None:
    errors, warnings = validate_documents(ROOT)
    assert errors == []
    assert warnings == []
