"""Build the semantic projection of a publication.

The projection is what will be published, before any presentation: the
ordered sections of the manifest, each chapter with its title, source path,
source hash and Markdown body, plus the sections generated from the registry.
Renderers (DOCX, PDF, later HTML) read the projection and nothing else.

Building fails closed: the registry must pass validation, links must resolve
and the manifest must account for every explanatory document. The same inputs
give the same bytes; nothing here reads a clock.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import MANIFEST, ManifestError, load_manifest, sections  # noqa: E402
from validate_registry import (  # noqa: E402
    ROOT,
    as_list,
    broken_links,
    load_registry,
    parse_reference,
    validate,
)

PROJECTION_SCHEMA = 1
H1_RE = re.compile(r"^# +(.+?)\s*$", re.M)
ADR_STATUS_RE = re.compile(r"^- \*\*Status:\*\* *(.+?)\s*$", re.M)


class ProjectionError(RuntimeError):
    """The publication cannot be built from the sources as they stand."""


# --- small Markdown helpers ---------------------------------------------------


def cell(value: Any) -> str:
    """Text safe inside one Markdown table cell."""
    return " ".join(str(value).split()).replace("|", "\\|")


def table(header: list[str], rows: list[list[Any]]) -> list[str]:
    return [
        "| " + " | ".join(header) + " |",
        "|" + "---|" * len(header),
        *("| " + " | ".join(cell(v) for v in row) + " |" for row in rows),
        "",
    ]


def bullets(label: str, items: Any) -> list[str]:
    items = as_list(items)
    return [f"**{label}**", "", *(f"- {' '.join(str(i).split())}" for i in items), ""] if items else []


def reference(ref: str) -> str:
    """A registry reference: a link when it is a document here, code text otherwise."""
    parsed = parse_reference(ref)
    if parsed and parsed[0] == "docs":
        return f"[{parsed[1]}]({parsed[1]})"
    return f"`{ref}`"


def none_registered(what: str) -> list[str]:
    return [f"No {what} is registered yet.", ""]


# --- sections generated from the registry -------------------------------------


def gen_domains(reg: dict[str, Any], docs_root: Path) -> tuple[str, str, list[str]]:
    units = reg["coverage"]
    rows = []
    for domain, spec in reg["schema"]["domains"].items():
        mine = [u for u in units.values() if u.get("owner_domain") == domain]
        statuses = sorted({u["status"] for u in mine})
        rows.append([domain.capitalize(), spec["nature"], f"`{spec['prefix']}-`", len(mine), ", ".join(statuses) or "none"])
    body = [
        "Generated from `registry/schema.yaml` and `registry/coverage.yaml`. The",
        "nature of a domain says whether it is a semantic authority, a capability",
        "or apparatus; seven repositories are not seven semantic authorities.",
        "",
        *table(["Domain", "Nature", "Component prefix", "Documented units", "Unit statuses"], rows),
    ]
    return "Domains and their nature", "registry/schema.yaml", body


def gen_contracts(reg: dict[str, Any], docs_root: Path) -> tuple[str, str, list[str]]:
    units = reg["coverage"]
    body = [
        "Generated from `registry/contracts.yaml`. Each entry describes where one",
        "domain relies on another and how the two sides are bound in code. It",
        "describes; it defines no contract and has no authority over any.",
        "",
    ]
    for contract in reg["contracts"].values():
        body += [f"## {contract['title']}", "", " ".join(contract["summary"].split()), ""]
        body += [f"How the sides are bound: **{contract['agreement']}**.", ""]
        rows = []
        for party in contract["parties"]:
            unit = units.get(party["unit"], {})
            rows.append([unit.get("title", party["unit"]), unit.get("owner_domain", ""), party["role"]])
        body += table(["Party", "Domain", "Role"], rows)
        body += bullets("Governed by", [reference(r) for r in as_list(contract.get("governed_by"))])
        body += bullets("Evidence", [reference(r) for r in as_list(contract.get("evidence"))])
        body += bullets("Explained in", [f"[{p}]({p})" for p in as_list(contract.get("documented_in"))])
        findings = as_list(contract.get("findings"))
        if findings:
            body += [f"Findings recorded against it in `registry/findings.yaml`: {', '.join(findings)}.", ""]
    if not reg["contracts"]:
        body += none_registered("cross-domain contract")
    return "Cross-domain contracts", "registry/contracts.yaml", body


def gen_contract_catalog(reg: dict[str, Any], docs_root: Path) -> tuple[str, str, list[str]]:
    units = reg["coverage"]
    rows = []
    for cid, contract in reg["contracts"].items():
        domains = sorted({units.get(p["unit"], {}).get("owner_domain", "?") for p in contract["parties"]})
        rows.append([f"`{cid}`", contract["title"], contract["agreement"], ", ".join(domains)])
    body = table(["Identifier", "Contract", "Binding", "Domains"], rows) if rows else none_registered("cross-domain contract")
    return "Cross-domain contract catalog", "registry/contracts.yaml", body


def gen_components(reg: dict[str, Any], docs_root: Path) -> tuple[str, str, list[str]]:
    units = reg["coverage"]
    body = ["Generated from `registry/components.yaml`.", ""]
    for domain in reg["schema"]["domains"]:
        mine = [
            (cid, c) for cid, c in reg["components"].items()
            if units.get(c["coverage_unit"], {}).get("owner_domain") == domain
        ]
        if not mine:
            continue
        body += [f"## {domain.capitalize()}", ""]
        for cid, comp in mine:
            unit = units[comp["coverage_unit"]]
            authority, state = comp.get("authority") or {}, comp.get("state") or {}
            body += [f"### {cid} — {comp['name']}", ""]
            body += [f"Status {unit['status']}. Owns {' '.join(str(authority.get('owns', 'nothing recorded')).split())}.", ""]
            body += [f"State owner: {state.get('owner', 'not recorded')}; state family: {state.get('family', 'not recorded')}.", ""]
            body += bullets("May decide", authority.get("may_decide"))
            body += bullets("Must not", authority.get("must_not"))
            body += bullets("Inputs", comp.get("inputs"))
            body += bullets("Outputs", comp.get("outputs"))
            body += bullets("Consumers", comp.get("consumers"))
            body += bullets("Explained in", [f"[{p}]({p})" for p in as_list(unit.get("canonical_docs"))])
    if not reg["components"]:
        body += none_registered("component")
    return "Canonical component catalog", "registry/components.yaml", body


def gen_glossary(reg: dict[str, Any], docs_root: Path) -> tuple[str, str, list[str]]:
    terms = reg["glossary"]
    body = ["Generated from `registry/glossary.yaml`.", ""]
    for entry in sorted(terms.values(), key=lambda e: e["term"].lower()):
        body += [f"**{entry['term']}.** {' '.join(entry['definition'].split())}", ""]
        others = [terms[t]["term"] for t in as_list(entry.get("distinguishes_from")) if t in terms]
        if others:
            body += [f"Not to be confused with: {', '.join(others)}.", ""]
    if not terms:
        body += none_registered("term")
    return "Glossary", "registry/glossary.yaml", body


def _plain_registry(name: str, title: str, what: str):
    def gen(reg: dict[str, Any], docs_root: Path) -> tuple[str, str, list[str]]:
        body = [f"Generated from `registry/{name}.yaml`.", ""]
        for key, entry in reg[name].items():
            body += [f"## {key}", ""]
            body += [f"- **{field}:** {' '.join(str(value).split())}" for field, value in entry.items()] + [""]
        if not reg[name]:
            body += none_registered(what)
        return title, f"registry/{name}.yaml", body

    return gen


def gen_decisions(reg: dict[str, Any], docs_root: Path) -> tuple[str, str, list[str]]:
    root = reg["schema"]["layout"]["adrs"]
    rows = []
    for doc in sorted((docs_root / root).glob("ADR-*.md")):
        text = doc.read_text(encoding="utf-8")
        heading, status = H1_RE.search(text), ADR_STATUS_RE.search(text)
        if heading is None or status is None:
            raise ProjectionError(f"{root}{doc.name}: decision record has no title or no Status line")
        number, _, title = heading.group(1).partition(" — ")
        rel = f"{root}{doc.name}"
        rows.append([f"[{number}]({rel})", title or number, status.group(1)])
    body = [
        f"Generated from the records under `{root}`. The status is the one each",
        "record states for itself; listing a record here does not accept it.",
        "",
        *(table(["Record", "Title", "Status"], rows) if rows else none_registered("decision record")),
    ]
    return "Decision record index", root, body


def gen_designs(reg: dict[str, Any], docs_root: Path) -> tuple[str, str, list[str]]:
    rows = [
        [
            f"[{d['title']}]({d['path']})",
            d["domain"],
            d["document_status"],
            d["implementation_status"],
            d["architecture_scope"],
        ]
        for d in reg["designs"].values()
    ]
    body = [
        "Generated from `registry/designs.yaml`, the only authority for the state",
        "of a design. The three states are independent: an approved design is",
        "never, by that fact, an implemented one.",
        "",
        *(table(["Design", "Domain", "Document", "Implementation", "Architecture scope"], rows)
          if rows else none_registered("design")),
    ]
    return "Design index", "registry/designs.yaml", body


GENERATORS = {
    "domains": gen_domains,
    "contracts": gen_contracts,
    "contract-catalog": gen_contract_catalog,
    "components": gen_components,
    "glossary": gen_glossary,
    "notation": _plain_registry("notation", "Notation", "symbol"),
    "parameters": _plain_registry("parameters", "Parameters", "parameter"),
    "metrics": _plain_registry("metrics", "Metrics", "metric"),
    "decisions": gen_decisions,
    "designs": gen_designs,
}


# --- provenance ---------------------------------------------------------------


def git_revision(repo: Path) -> dict[str, Any]:
    """HEAD of a checkout and whether it has local changes; unresolved when it is not one."""
    def git(*args: str) -> str | None:
        try:
            done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=False)
        except OSError:
            return None
        return done.stdout.strip() if done.returncode == 0 else None

    top = git("rev-parse", "--show-toplevel")
    if top is None or Path(top).resolve() != repo.resolve():
        return {"revision": None, "state": "unresolved"}
    dirty = bool(git("status", "--porcelain", "--untracked-files=no"))
    return {"revision": git("rev-parse", "HEAD"), "state": "modified" if dirty else "clean"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def registry_digest(registry_dir: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(registry_dir.glob("*.yaml")):
        digest.update(path.name.encode() + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()


def sources(reg: dict[str, Any], docs_root: Path, repos_root: Path | None) -> dict[str, Any]:
    """Revision of this repository and of each domain repository that is actually present.

    `reviewed_at` lists the commits the units were last checked against, taken
    from the registry. They are review bases, not the state of a checkout, and
    are never used to fill in a revision that was not resolved.
    """
    out = {"docs": git_revision(docs_root)}
    for domain in reg["schema"]["domains"]:
        found = git_revision(repos_root / domain) if repos_root else {"revision": None, "state": "unresolved"}
        bases = {u.get("review", {}).get("basis", {}).get(domain) for u in reg["coverage"].values()}
        out[domain] = {**found, "reviewed_at": sorted(b for b in bases if b)}
    return out


# --- the projection -----------------------------------------------------------


def chapter_from_document(rel: str, docs_root: Path) -> dict[str, Any]:
    raw = (docs_root / rel).read_bytes()
    text = raw.decode("utf-8")
    heading = H1_RE.search(text)
    if heading is None:
        raise ProjectionError(f"{rel}: document has no top-level heading to use as chapter title")
    body = (text[: heading.start()] + text[heading.end():]).strip() + "\n"
    return {
        "id": re.sub(r"[^a-z0-9]+", "-", rel.removesuffix(".md").lower()).strip("-"),
        "title": heading.group(1),
        "source": rel,
        "generated": False,
        "sha256": sha256(raw),
        "base": Path(rel).parent.as_posix(),
        "markdown": body,
    }


def chapter_generated(name: str, reg: dict[str, Any], docs_root: Path) -> dict[str, Any]:
    title, source, lines = GENERATORS[name](reg, docs_root)
    body = "\n".join(lines).strip() + "\n"
    return {
        "id": f"generated-{name}",
        "title": title,
        "source": source,
        "generated": True,
        "sha256": sha256(body.encode("utf-8")),
        "base": "",
        "markdown": body,
    }


def build_projection(
    registry_dir: Path = ROOT / "registry",
    docs_root: Path = ROOT,
    manifest_path: Path = MANIFEST,
    repos_root: Path | None = None,
) -> dict[str, Any]:
    errors, _unresolved = validate(registry_dir, docs_root, repos_root)
    errors += broken_links(docs_root)
    if errors:
        raise ProjectionError("registry validation failed:\n" + "\n".join(errors))
    try:
        manifest = load_manifest(manifest_path, docs_root)
    except ManifestError as exc:
        raise ProjectionError(f"publication manifest is not publishable:\n{exc}") from exc
    reg = load_registry(registry_dir)

    out_sections = []
    for section in sections(manifest):
        chapters = []
        # A section presents its keys in the order the manifest writes them.
        for key in section:
            if key == "chapters":
                chapters += [chapter_from_document(rel, docs_root) for rel in section["chapters"] or []]
            elif key == "generated":
                chapters += [chapter_generated(name, reg, docs_root) for name in section["generated"] or []]
        out_sections.append(
            {"id": section["id"], "title": section["title"], "group": section["group"], "chapters": chapters}
        )
    return {
        "schema_version": PROJECTION_SCHEMA,
        "publication": manifest["publication"],
        "sources": sources(reg, docs_root, repos_root),
        "registry_digest": registry_digest(registry_dir),
        "sections": out_sections,
    }


def projection_bytes(projection: dict[str, Any]) -> bytes:
    return (json.dumps(projection, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
