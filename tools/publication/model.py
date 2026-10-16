"""The publication manifest: which sources one publication presents, in which order.

The manifest composes; it holds no documentary text. Loading fails closed: a
chapter that does not exist, a document listed twice, an unknown generated
section, or an explanatory document that is neither a chapter nor explicitly
excluded is an error, never a silent omission.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_registry import ROOT, load_strict_yaml  # noqa: E402

MANIFEST = ROOT / "publication" / "publications" / "biopeia-master.yaml"
TECHNICAL_REFERENCE_MANIFEST = ROOT / "publication" / "publications" / "biopeia-technical-reference.yaml"
DEFAULT_MANIFESTS = (MANIFEST, TECHNICAL_REFERENCE_MANIFEST)

# Sections rendered from the registry; projection.py holds one renderer each.
GENERATED_SECTIONS = (
    "reader-guide",
    "authority-map",
    "domains",
    "contracts",
    "contract-catalog",
    "components",
    "glossary",
    "notation",
    "parameters",
    "metrics",
    "decisions",
    "designs",
)
# Chapters may come from these top-level directories only.
CHAPTER_ROOTS = ("explanation/", "reference/")


class ManifestError(ValueError):
    """The manifest cannot be published as written."""


def sections(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Front matter, parts, then appendices, each marked with its group."""
    return [
        {**section, "group": group}
        for group in ("front", "parts", "appendices")
        for section in manifest.get(group) or []
    ]


def manifest_errors(manifest: dict[str, Any], docs_root: Path) -> list[str]:
    errors: list[str] = []
    publication = manifest.get("publication") or {}
    for key in ("id", "title", "output"):
        if not str(publication.get(key) or "").strip():
            errors.append(f"publication.{key} is missing")
    if not manifest.get("parts"):
        errors.append("parts is empty")

    seen_ids: set[str] = set()
    chapters: list[str] = []
    for section in sections(manifest):
        sid = section.get("id")
        where = f"{section['group']} {sid!r}"
        if not sid or sid in seen_ids:
            errors.append(f"{where}: id is missing or repeated")
        seen_ids.add(sid)
        if not str(section.get("title") or "").strip():
            errors.append(f"{where}: title is missing")
        unknown = set(section) - {"id", "title", "chapters", "generated", "group"}
        if unknown:
            errors.append(f"{where}: unknown keys {sorted(unknown)}")
        if not section.get("chapters") and not section.get("generated"):
            errors.append(f"{where}: has neither chapters nor generated sections")
        for name in section.get("generated") or []:
            if name not in GENERATED_SECTIONS:
                errors.append(f"{where}: unknown generated section {name!r}")
        for rel in section.get("chapters") or []:
            if not str(rel).startswith(CHAPTER_ROOTS) or ".." in Path(str(rel)).parts:
                errors.append(f"{where}: chapter must live under {' or '.join(CHAPTER_ROOTS)}: {rel}")
            elif not (docs_root / rel).is_file():
                errors.append(f"{where}: chapter does not exist: {rel}")
            chapters.append(rel)

    for rel in sorted({c for c in chapters if chapters.count(c) > 1}):
        errors.append(f"chapter listed more than once: {rel}")

    excluded: dict[str, str] = {}
    for entry in manifest.get("excluded") or []:
        path, reason = (entry or {}).get("path"), str((entry or {}).get("reason") or "").strip()
        if not path or not reason:
            errors.append(f"excluded entry needs a path and a reason: {entry!r}")
            continue
        if not (docs_root / path).is_file():
            errors.append(f"excluded document does not exist: {path}")
        if path in chapters:
            errors.append(f"document is both a chapter and excluded: {path}")
        excluded[path] = reason

    # A selection presents part of the corpus on purpose and accounts for no
    # more than it lists. Only a complete publication must place every document.
    if publication.get("selection"):
        return errors

    # Every explanatory document is accounted for. README.md files are
    # navigation indexes, not chapters.
    for doc in sorted((docs_root / "explanation").rglob("*.md")):
        rel = doc.relative_to(docs_root).as_posix()
        if doc.name != "README.md" and rel not in chapters and rel not in excluded:
            errors.append(f"explanatory document is neither a chapter nor excluded: {rel}")
    return errors


def corpus_coverage_errors(manifests: list[dict[str, Any]], docs_root: Path = ROOT) -> list[str]:
    """Check that across the suite of publications, all documentation is accounted for."""
    errors: list[str] = []
    all_chapters: set[str] = set()
    all_excluded: set[str] = set()
    all_generated: set[str] = set()

    for m in manifests:
        for s in sections(m):
            all_chapters.update(s.get("chapters") or [])
            all_generated.update(s.get("generated") or [])
        for entry in m.get("excluded") or []:
            if (entry or {}).get("path"):
                all_excluded.add(entry["path"])

    # Every document in explanation/ and reference/ must be published in at least one manifest
    # or explicitly listed as excluded with a reason.
    for root_dir in ("explanation", "reference"):
        folder = docs_root / root_dir
        if not folder.is_dir():
            continue
        for doc in sorted(folder.rglob("*.md")):
            rel = doc.relative_to(docs_root).as_posix()
            if doc.name != "README.md" and rel not in all_chapters and rel not in all_excluded:
                errors.append(f"corpus document is neither published in any manifest nor excluded: {rel}")

    # Every canonical generated section (contracts, catalogs, registers, decisions, designs)
    # must be published in at least one manifest.
    for gen in GENERATED_SECTIONS:
        if gen not in all_generated:
            errors.append(f"canonical generated section is not published in any manifest: {gen}")

    return errors


def load_manifest(path: Path = MANIFEST, docs_root: Path = ROOT) -> dict[str, Any]:
    """Load and validate the manifest; raise ManifestError listing every problem."""
    try:
        manifest = load_strict_yaml(path)
    except (OSError, ValueError) as exc:
        raise ManifestError(str(exc)) from exc
    errors = manifest_errors(manifest, docs_root)
    if errors:
        raise ManifestError("\n".join(errors))
    return manifest


if __name__ == "__main__":
    targets = [Path(p) for p in sys.argv[1:]] if len(sys.argv) > 1 else list(DEFAULT_MANIFESTS)
    failed = False
    loaded_manifests: list[dict[str, Any]] = []
    for target in targets:
        try:
            loaded = load_manifest(target)
            loaded_manifests.append(loaded)
        except ManifestError as exc:
            print(f"Publication manifest {target.name}: FAIL\n{exc}")
            failed = True
            continue
        count = sum(len(s.get("chapters") or []) for s in sections(loaded))
        print(f"Publication manifest {target.name}: PASS ({len(sections(loaded))} sections, {count} chapters)")

    if len(loaded_manifests) > 1 or (not sys.argv[1:] and loaded_manifests):
        coverage_errs = corpus_coverage_errors(loaded_manifests, ROOT)
        if coverage_errs:
            print("Publication corpus coverage: FAIL\n" + "\n".join(coverage_errs))
            failed = True
        else:
            print("Publication corpus coverage: PASS (all explanation and reference documents, plus generated sections, accounted for)")

    if failed:
        sys.exit(1)
