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
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import MANIFEST, ManifestError, load_manifest, sections  # noqa: E402
from references import GITHUB, ReferenceError, Resolver  # noqa: E402
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


NO_ENTRIES = "No registered entries at this revision."


def none_registered(what: str) -> list[str]:
    return [NO_ENTRIES, ""]


# --- sections generated from the registry -------------------------------------


def gen_reader_guide(reg: dict[str, Any], docs_root: Path) -> tuple[str, str, list[str]]:
    manifest = reg["manifest"]
    rows = [
        [section["title"], len(section.get("chapters") or []) + len(section.get("generated") or [])]
        for section in manifest["parts"]
    ]
    prefixes = [[d.capitalize(), f"`{spec['prefix']}-`", spec["nature"]] for d, spec in reg["schema"]["domains"].items()]
    body = [
        "This publication presents the Biopeia documentation as one ordered work. It is",
        "generated: the documents and registries of the documentation repository remain",
        "the only source, and every chapter names the document it was taken from.",
        "",
        "## How it is ordered",
        "",
        "The system view comes first, then each domain, then what binds the domains. The",
        "appendices are for looking things up.",
        "",
        *table(["Part", "Chapters"], rows),
        "## How to read a chapter",
        "",
        "- The line under a chapter title gives its source document. A chapter marked as",
        "  generated is rendered from the registry and has no document of its own.",
        "- A chapter usually opens by naming the revision of each repository it was",
        "  reviewed against. What it states holds for that revision.",
        "- Chapters describe what exists in code, and say so when something is only",
        "  decided, or only exercised by a test.",
        "- A reference to code, a test, a commit, a decision record or an issue is a link",
        "  to GitHub. Code is linked at the revision the chapter was reviewed against, so",
        "  a link shows the code the text describes, not today's. The Biopeia",
        "  repositories are private: the links open only for a reader with access.",
        "- A component identifier is a link to its sheet in the component catalog.",
        "",
        "## Words that carry a state",
        "",
        f"A documented unit carries one architectural status: {', '.join(reg['schema']['unit_statuses'])}.",
        "TARGET is accepted architecture that the code is not yet claimed to implement.",
        "How strong the support for a statement is, and how that differs from whether its",
        "documentation was reviewed, is set out in",
        "[Evidence status and review status](reference/evidence-status.md).",
        "",
        "## Identifiers",
        "",
        "A component identifier carries the prefix of the domain that owns it.",
        "",
        *table(["Domain", "Prefix", "Nature"], prefixes),
        "## Editions",
        "",
        "A published edition is built only from clean, identified revisions of every",
        "source repository. Anything else is a working edition, says so on every page,",
        "and must not be cited as a state of Biopeia.",
    ]
    return "Reader guide", "publication/biopeia-master.yaml", body


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
            body += [f"### `{cid}` — {comp['name']}", ""]

            def many(values: Any) -> str:
                return " • ".join(" ".join(str(v).split()) for v in as_list(values)) or "none recorded"

            rows = [
                ["Unit", f"`{comp['coverage_unit']}`"],
                ["Status", unit["status"]],
                ["Owner domain", unit["owner_domain"]],
                ["State owner", state.get("owner", "not recorded")],
                ["State family", state.get("family", "not recorded")],
                ["Owns", authority.get("owns", "nothing recorded")],
                ["May decide", many(authority.get("may_decide"))],
                ["Must not", many(authority.get("must_not"))],
                *([["At each lifecycle boundary", many(f"{k}: {v}" for k, v in comp["lifecycle"].items())]]
                  if comp.get("lifecycle") else []),
                *([["In a causal cut", many(f"{k.replace('_', ' ')}: {v}" for k, v in comp["causal_state"].items())]]
                  if comp.get("causal_state") else []),
                ["Inputs", many(comp.get("inputs"))],
                ["Outputs", many(comp.get("outputs"))],
                ["Consumers", many(comp.get("consumers"))],
                ["Implementation", many(reference(r) for r in as_list(unit.get("implementation")))],
                ["Tests", many(reference(r) for r in as_list(unit.get("tests")))],
                ["Decisions", many(reference(r) for r in as_list(unit.get("adrs")))],
                ["Explained in", many(f"[{p}]({p})" for p in as_list(unit.get("canonical_docs")))],
            ]
            body += table(["Field", "Value"], rows)
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
    "reader-guide": gen_reader_guide,
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
    def git(*args: str, env: dict[str, str] | None = None) -> str | None:
        try:
            done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=False,
                                  env={**os.environ, **(env or {})})
        except OSError:
            return None
        return done.stdout.strip() if done.returncode == 0 else None

    top = git("rev-parse", "--show-toplevel")
    if top is None or Path(top).resolve() != repo.resolve():
        return {"revision": None, "state": "unresolved", "committed_on": None}
    dirty = bool(git("status", "--porcelain", "--untracked-files=no"))
    return {
        "revision": git("rev-parse", "HEAD"),
        "state": "modified" if dirty else "clean",
        # The day of the commit in UTC: the same on every machine.
        "committed_on": git("-c", "log.showSignature=false", "log", "-1", "--date=format-local:%Y-%m-%d",
                            "--format=%cd", env={"TZ": "UTC"}),
    }


def release_of(docs: dict[str, Any]) -> dict[str, Any]:
    """Identifier and date of a build: the day and revision of the documentation it was built from."""
    if not docs["revision"]:
        return {"id": "unversioned", "date": None}
    suffix = "+modified" if docs["state"] == "modified" else ""
    return {"id": f"{docs['committed_on'].replace('-', '.')}-{docs['revision'][:7]}{suffix}", "date": docs["committed_on"]}


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
        found = git_revision(repos_root / domain) if repos_root else git_revision(Path("/nonexistent"))
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


# Generated sections that render one registry, by the registry they render.
REGISTRY_OF = {"contracts": "contracts", "contract-catalog": "contracts", "components": "components",
               "glossary": "glossary", "notation": "notation", "parameters": "parameters", "metrics": "metrics",
               "designs": "designs"}


def chapter_generated(name: str, reg: dict[str, Any], docs_root: Path) -> dict[str, Any]:
    title, source, lines = GENERATORS[name](reg, docs_root)
    body = "\n".join(lines).strip() + "\n"
    return {
        # A section whose registry holds nothing; renderers show it compactly.
        "empty": name in REGISTRY_OF and not reg[REGISTRY_OF[name]],
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
    reg = {**load_registry(registry_dir), "manifest": manifest}

    found = sources(reg, docs_root, repos_root)
    resolver = Resolver(reg, docs_root, repos_root, found)
    out_sections = []
    for section in sections(manifest):
        chapters = []
        # A section presents its keys in the order the manifest writes them.
        for key in section:
            if key == "chapters":
                chapters += [chapter_from_document(rel, docs_root) for rel in section["chapters"] or []]
            elif key == "generated":
                chapters += [chapter_generated(name, reg, docs_root) for name in section["generated"] or []]
        for chapter in chapters:
            basis = resolver.basis_of(None if chapter["generated"] else chapter["source"])
            try:
                chapter["references"] = resolver.chapter(chapter["markdown"], basis)
                chapter["source_url"] = resolver.blob("docs", chapter["source"].rstrip("/"), {})
            except ReferenceError as exc:
                raise ProjectionError(f"{chapter['source']}: {exc}") from exc
        out_sections.append(
            {"id": section["id"], "title": section["title"], "group": section["group"], "chapters": chapters}
        )
    listed = [c for s in out_sections for c in s["chapters"]]
    inventory = {
        "Parts": sum(1 for s in out_sections if s["group"] == "parts"),
        "Appendices": sum(1 for s in out_sections if s["group"] == "appendices"),
        "Chapters taken from documents": sum(1 for c in listed if not c["generated"]),
        "Sections generated from the registry": sum(1 for c in listed if c["generated"]),
        "Documented units": len(reg["coverage"]),
        "Components": len(reg["components"]),
        "Cross-domain contracts": len(reg["contracts"]),
        "Glossary terms": len(reg["glossary"]),
        "Designs": len(reg["designs"]),
        "Decision records": len(list((docs_root / reg["schema"]["layout"]["adrs"]).glob("ADR-*.md"))),
        "Parameters": len(reg["parameters"]),
        "Metrics": len(reg["metrics"]),
        "Notation symbols": len(reg["notation"]),
    }
    return {
        "schema_version": PROJECTION_SCHEMA,
        "publication": manifest["publication"],
        "inventory": inventory,
        "sources": found,
        # Where links lead and how many could be checked against a checkout.
        "links": {
            "github": GITHUB,
            "docs_tree": f"{GITHUB}/docs/blob/{found['docs']['revision']}/" if found["docs"]["revision"] else None,
            "components": sorted(reg["components"]),
            **{key: resolver.stats[key] for key in
               ("verified", "unverified", "at_build_revision", "without_revision", "symbol_not_located",
                "tests_not_located")},
        },
        "release": release_of(found["docs"]),
        "registry_digest": registry_digest(registry_dir),
        "sections": out_sections,
    }


def projection_bytes(projection: dict[str, Any]) -> bytes:
    return (json.dumps(projection, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
