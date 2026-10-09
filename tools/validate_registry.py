#!/usr/bin/env python3
"""Validate the Biopeia documentation registry.

Two checks, both read-only:

* integrity (default): schema, closed vocabularies, internal cross-references
  and documentation paths. Needs only this repository.
* staleness (``--stale``): units whose referenced sources changed in another
  repository since the commit recorded as their review basis. Needs local
  checkouts of those repositories (``--repos-root``).

References to other repositories are written ``<repository>:<path>``. They are
resolved against local checkouts when ``--repos-root`` is given and reported as
unresolved, not as errors, when the checkout is absent.

Source files of other repositories are read as text or AST only. This tool
never imports a domain package.
"""

from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]

REGISTRY_KEYS = {
    "coverage": "units",
    "components": "components",
    "parameters": "parameters",
    "metrics": "metrics",
    "notation": "symbols",
    "glossary": "terms",
    "designs": "designs",
}
REFERENCE_FIELDS = ("implementation", "tests", "design", "adrs")
CODE_FIELDS = ("implementation", "tests")
# A change under these fields means the explanation may no longer hold.
REVIEW_FIELDS = ("implementation", "design", "adrs")

UNIT_ID_RE = re.compile(r"^[a-z]+[a-z0-9_-]*\.[a-z0-9_-]+$")
SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
DESIGN_ID_RE = re.compile(r"^design\.[a-z0-9-]+\.[a-z0-9.-]+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# The design register is the only authority for these; documents must not carry them.
FORBIDDEN_FRONT_MATTER_RE = re.compile(r"^(status|implementation_status):", re.M)


class UniqueKeySafeLoader(yaml.SafeLoader):
    """YAML loader that rejects duplicate keys."""


def _construct_mapping(loader: yaml.Loader, node: yaml.MappingNode, deep: bool = False) -> dict:
    loader.flatten_mapping(node)
    mapping: dict = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ValueError(
                f"Duplicate YAML key found: {key!r} at line {key_node.start_mark.line + 1}"
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping
)


def load_strict_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fp:
        data = yaml.load(fp, Loader=UniqueKeySafeLoader)
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: YAML root must be a mapping")
    return data


def load_registry(registry_dir: Path) -> dict[str, dict[str, Any]]:
    """Load schema.yaml and the registries; each registry maps id -> entry."""
    registry = {"schema": load_strict_yaml(registry_dir / "schema.yaml")}
    for name, key in REGISTRY_KEYS.items():
        entries = load_strict_yaml(registry_dir / f"{name}.yaml").get(key)
        if not isinstance(entries, dict):
            raise ValueError(f"{name}.yaml: {key!r} must be a mapping")
        registry[name] = entries
    return registry


def as_list(value: Any) -> list:
    if not value:
        return []
    return [value] if isinstance(value, str) else list(value)


def parse_reference(ref: Any) -> tuple[str, str] | None:
    """Split ``<repository>:<path>``; None when the reference is malformed."""
    if not isinstance(ref, str) or ":" not in ref:
        return None
    repo, path = ref.split(":", 1)
    if not repo or not path or path.startswith("/"):
        return None
    return repo, path


def resolve_symbol_in_ast(path: Path, symbol: str) -> bool:
    """Find a function, class, module constant or ``Class.attribute`` without importing."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return False

    def defines(body: list[ast.stmt], name: str) -> ast.stmt | None:
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name == name:
                    return node
            elif isinstance(node, ast.Assign):
                if any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
                    return node
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and node.target.id == name:
                    return node
        return None

    parts = symbol.split(".")
    if len(parts) == 1:
        return defines(tree.body, parts[0]) is not None
    if len(parts) == 2:
        cls = defines(tree.body, parts[0])
        return isinstance(cls, ast.ClassDef) and defines(cls.body, parts[1]) is not None
    return False


def validate(
    registry_dir: Path, docs_root: Path, repos_root: Path | None = None
) -> tuple[list[str], list[str]]:
    """Return (errors, unresolved external references)."""
    try:
        reg = load_registry(registry_dir)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return [str(exc)], []

    schema, units = reg["schema"], reg["coverage"]
    domains: dict[str, dict[str, str]] = schema["domains"]
    extra: dict[str, dict[str, bool]] = schema["extra_repositories"]
    authorities = {d for d, v in domains.items() if v["nature"] == "semantic-authority"}
    errors: list[str] = []
    unresolved: list[str] = []

    def repo_root(repo: str) -> Path | None:
        if repo == "docs":
            return docs_root
        if repos_root is not None and (repos_root / repo).is_dir():
            return repos_root / repo
        return None

    def check_reference(where: str, field: str, ref: Any) -> Path | None:
        """Validate one external reference; return its local path when resolvable."""
        parsed = parse_reference(ref)
        if parsed is None:
            errors.append(f"{where}: {field} reference {ref!r} is not '<repository>:<path>'")
            return None
        repo, path = parsed
        if repo not in domains and repo not in extra:
            errors.append(f"{where}: {field} names unknown repository {repo!r}")
            return None
        if field in CODE_FIELDS and extra.get(repo, {}).get("historical"):
            errors.append(
                f"{where}: {field} cites historical repository {repo!r}; "
                "it may only be a design or decision source"
            )
            return None
        if repo == "docs" and not path.startswith(schema["layout"].get(field, "")):
            errors.append(f"{where}: {field} must live under {schema['layout'][field]}: {ref}")
            return None
        root = repo_root(repo)
        if root is None:
            unresolved.append(f"{where}: {field} {ref}")
            return None
        if not (root / path).exists():
            errors.append(f"{where}: {field} references missing path: {ref}")
            return None
        return root / path

    def check_doc_paths(where: str, field: str, paths: Any) -> None:
        for rel in as_list(paths):
            if not str(rel).startswith(schema["layout"][field]):
                errors.append(f"{where}: {field} must live under {schema['layout'][field]}: {rel}")
            elif not (docs_root / rel).is_file():
                errors.append(f"{where}: {field} references missing document: {rel}")

    # --- designs ----------------------------------------------------------
    designs = reg["designs"]
    design_root = schema["layout"]["design"]
    design_paths: dict[str, str] = {}  # path -> design id
    for did, design in designs.items():
        where = f"Design {did}"
        if not DESIGN_ID_RE.match(str(did)):
            errors.append(f"{where}: id must look like 'design.<area>.<slug>'")
        if not isinstance(design, dict):
            errors.append(f"{where}: definition must be a mapping")
            continue
        if not str(design.get("title", "")).strip():
            errors.append(f"{where}: title is missing or empty")
        path = str(design.get("path", ""))
        if not path.startswith(design_root):
            errors.append(f"{where}: path must live under {design_root}: {path!r}")
        elif not (docs_root / path).is_file():
            errors.append(f"{where}: path references missing document: {path}")
        elif path in design_paths:
            errors.append(f"{where}: path already registered by {design_paths[path]}")
        else:
            design_paths[path] = did
            text = (docs_root / path).read_text(encoding="utf-8")
            if text.startswith("---\n") and FORBIDDEN_FRONT_MATTER_RE.search(
                text[4:].split("\n---", 1)[0]
            ):
                errors.append(
                    f"{where}: document front matter declares a status; "
                    "registry/designs.yaml is the only authority for it"
                )
        if design.get("domain") not in domains:
            errors.append(f"{where}: domain {design.get('domain')!r} not in {sorted(domains)}")
        for p in as_list(design.get("participating_domains")):
            if p not in domains or p == design.get("domain"):
                errors.append(f"{where}: invalid participating_domain {p!r}")
        for axis in ("document_status", "implementation_status", "architecture_scope"):
            allowed = schema[f"design_{axis}es" if axis.endswith("status") else f"design_{axis}s"]
            if design.get(axis) not in allowed:
                errors.append(f"{where}: {axis} {design.get(axis)!r} not in {allowed}")
        if design.get("implementation_status") not in ("not_evaluated", "not_applicable", None):
            evidence = design.get("implementation_evidence") or {}
            if not evidence.get("basis") or not str(evidence.get("observed", "")).strip():
                errors.append(
                    f"{where}: implementation_status {design.get('implementation_status')!r} "
                    "requires implementation_evidence with basis and observed"
                )
            for ref in as_list(evidence.get("tests")):
                check_reference(where, "tests", ref)
            for repo, sha in (evidence.get("basis") or {}).items():
                if repo not in domains or not SHA_RE.match(str(sha)):
                    errors.append(f"{where}: implementation_evidence.basis.{repo} is not a domain commit")
        if design.get("document_status") == "approved":
            decision = design.get("decision") or {}
            if not str(decision.get("reference", "")).strip():
                errors.append(f"{where}: an approved design requires decision.reference")
            elif str(decision["reference"]).startswith("docs:"):
                check_reference(where, "adrs", decision["reference"])
            if not DATE_RE.match(str(decision.get("date", ""))):
                errors.append(f"{where}: an approved design requires decision.date as YYYY-MM-DD")
        if design.get("document_status") == "superseded":
            decisions = as_list(design.get("superseded_by_decisions"))
            if design.get("superseded_by") not in designs and not decisions:
                errors.append(
                    f"{where}: a superseded design requires superseded_by naming a design "
                    "or superseded_by_decisions"
                )
            for ref in decisions:
                check_reference(where, "adrs", ref)
        source = design.get("source")
        if source is not None:
            if source.get("repository") not in domains and source.get("repository") not in extra:
                errors.append(f"{where}: source.repository {source.get('repository')!r} is unknown")
            if not SHA_RE.match(str(source.get("commit", ""))):
                errors.append(f"{where}: source.commit is not a commit SHA")
            if not str(source.get("path", "")).strip():
                errors.append(f"{where}: source.path is missing")

    if (docs_root / design_root).is_dir():
        for doc in sorted((docs_root / design_root).rglob("*.md")):
            rel = doc.relative_to(docs_root).as_posix()
            if doc.name != "README.md" and rel not in design_paths:
                errors.append(f"Design document {rel} has no entry in designs.yaml")

    # --- coverage ---------------------------------------------------------
    component_ids: dict[str, str] = {}  # component id -> unit id
    for uid, unit in units.items():
        where = f"Unit {uid}"
        if not UNIT_ID_RE.match(str(uid)):
            errors.append(f"{where}: id must look like '<kind>.<slug>'")
        if not isinstance(unit, dict):
            errors.append(f"{where}: definition must be a mapping")
            continue
        if not str(unit.get("title", "")).strip():
            errors.append(f"{where}: title is missing or empty")
        if unit.get("kind") not in schema["unit_kinds"]:
            errors.append(f"{where}: kind {unit.get('kind')!r} not in {schema['unit_kinds']}")
        if unit.get("status") not in schema["unit_statuses"]:
            errors.append(
                f"{where}: status {unit.get('status')!r} not in {schema['unit_statuses']}"
            )
        owner = unit.get("owner_domain")
        if owner not in domains:
            errors.append(f"{where}: owner_domain {owner!r} not in {sorted(domains)}")

        participants = as_list(unit.get("participating_domains"))
        if len(participants) != len(set(participants)):
            errors.append(f"{where}: duplicate participating_domains")
        for p in participants:
            if p not in domains:
                errors.append(f"{where}: participating_domain {p!r} not in {sorted(domains)}")
            if p == owner:
                errors.append(f"{where}: owner_domain {owner!r} repeated in participating_domains")

        if not as_list(unit.get("canonical_docs")):
            errors.append(f"{where}: at least one canonical_docs entry is required")
        check_doc_paths(where, "canonical_docs", unit.get("canonical_docs"))

        referenced_repos: set[str] = set()
        for field in REFERENCE_FIELDS:
            for ref in as_list(unit.get(field)):
                check_reference(where, field, ref)
                parsed = parse_reference(ref)
                if field == "design" and parsed and parsed[0] == "docs":
                    if parsed[1] not in design_paths:
                        errors.append(f"{where}: design {ref} is not in designs.yaml")
                if parsed and parsed[0] != "docs":
                    referenced_repos.add(parsed[0])

        review = unit.get("review") or {}
        if "status" in review and review["status"] not in schema["review_statuses"]:
            errors.append(
                f"{where}: review.status {review['status']!r} not in {schema['review_statuses']}"
            )
        basis = review.get("basis") or {}
        for repo in sorted(referenced_repos - set(basis)):
            errors.append(f"{where}: review.basis records no commit for repository {repo!r}")
        for repo, sha in basis.items():
            if not SHA_RE.match(str(sha)):
                errors.append(f"{where}: review.basis.{repo} {sha!r} is not a commit SHA")

        for dep in as_list(unit.get("depends_on")):
            if dep not in units:
                errors.append(f"{where}: depends_on references non-existent unit: {dep!r}")

        cid = unit.get("component_id")
        if unit.get("kind") == "component":
            if not isinstance(cid, str):
                errors.append(f"{where}: a component unit requires exactly one component_id")
            elif cid in component_ids:
                errors.append(f"{where}: component_id {cid} already used by {component_ids[cid]}")
            else:
                component_ids[cid] = uid
        elif cid is not None:
            errors.append(f"{where}: only component units may declare component_id")

    # --- components -------------------------------------------------------
    for cid, comp in reg["components"].items():
        where = f"Component {cid}"
        unit_id = comp.get("coverage_unit")
        unit = units.get(unit_id)
        if not isinstance(unit, dict):
            errors.append(f"{where}: coverage_unit {unit_id!r} missing from coverage.yaml")
            continue
        if component_ids.get(cid) != unit_id:
            errors.append(
                f"{where}: bidirectional mismatch (coverage maps {cid} to "
                f"{component_ids.get(cid)!r}, components.yaml to {unit_id!r})"
            )
        owner = unit.get("owner_domain")
        prefix = domains.get(owner, {}).get("prefix")
        if prefix and not re.match(rf"^{prefix}-[A-Z0-9]+$", str(cid)):
            errors.append(f"{where}: identifier must be '{prefix}-<CODE>' for owner {owner!r}")

        state = comp.get("state") or {}
        state_owner = state.get("owner")
        if state_owner not in schema["state_owners"]:
            errors.append(
                f"{where}: state.owner {state_owner!r} not in {schema['state_owners']}"
            )
        elif owner in authorities and state_owner not in (owner, "implementation-local"):
            errors.append(
                f"{where}: owned by {owner!r} but declares state owned by {state_owner!r}"
            )
        if state.get("family") not in schema["state_families"]:
            errors.append(
                f"{where}: state.family {state.get('family')!r} not in {schema['state_families']}"
            )

        authority = comp.get("authority") or {}
        for key in ("owns", "may_decide", "must_not"):
            if not authority.get(key):
                errors.append(f"{where}: authority.{key} is missing or empty")

        lifecycle = comp.get("lifecycle") or {}
        for axis, allowed in schema["lifecycle"].items():
            if lifecycle.get(axis) not in allowed:
                errors.append(
                    f"{where}: lifecycle.{axis} value {lifecycle.get(axis)!r} not in {allowed}"
                )

        for consumer in as_list(comp.get("consumers")):
            if UNIT_ID_RE.match(str(consumer)) and consumer not in units:
                errors.append(f"{where}: consumer {consumer!r} does not resolve in coverage.yaml")

    for cid, uid in component_ids.items():
        if cid not in reg["components"]:
            errors.append(f"Unit {uid}: component_id {cid} has no entry in components.yaml")

    # --- parameters -------------------------------------------------------
    for pid, param in reg["parameters"].items():
        where = f"Parameter {pid}"
        if param.get("owner") not in units:
            errors.append(f"{where}: owner {param.get('owner')!r} does not resolve in coverage.yaml")
        if param.get("source") not in schema["parameter_sources"]:
            errors.append(
                f"{where}: source {param.get('source')!r} not in {schema['parameter_sources']}"
            )
        for required in ("symbol", "dimension", "unit"):
            if not param.get(required):
                errors.append(f"{where}: missing required field {required!r}")
        if param.get("source") == "CODE":
            impl = param.get("implementation")
            if not isinstance(impl, dict) or not impl.get("ref") or not impl.get("symbol"):
                errors.append(f"{where}: source CODE requires implementation.ref and .symbol")
                continue
            target = check_reference(where, "implementation", impl["ref"])
            if target is not None and not resolve_symbol_in_ast(target, impl["symbol"]):
                errors.append(f"{where}: symbol {impl['symbol']!r} not found in {impl['ref']}")

    # --- metrics ----------------------------------------------------------
    for mid, metric in reg["metrics"].items():
        where = f"Metric {mid}"
        if metric.get("class") not in schema["metric_classes"]:
            errors.append(
                f"{where}: class {metric.get('class')!r} not in {schema['metric_classes']}"
            )
        if metric.get("owner_domain") not in domains:
            errors.append(
                f"{where}: owner_domain {metric.get('owner_domain')!r} not in {sorted(domains)}"
            )
        # Epistemic invariant: an external evaluation is never an organism signal.
        if metric.get("class") == "scientific_evaluation" and metric.get("owner_domain") != "lab":
            errors.append(f"{where}: scientific_evaluation must have owner_domain 'lab'")
        consumer = metric.get("consumer")
        if consumer and UNIT_ID_RE.match(str(consumer)) and consumer not in units:
            errors.append(f"{where}: consumer {consumer!r} does not resolve in coverage.yaml")

    # --- notation ---------------------------------------------------------
    symbols = reg["notation"]
    aliases: dict[str, str] = {}
    for sym, entry in symbols.items():
        where = f"Symbol {sym}"
        if not str(entry.get("meaning", "")).strip():
            errors.append(f"{where}: meaning is missing or empty")
        if entry.get("scope") not in schema["notation_scopes"]:
            errors.append(f"{where}: invalid scope {entry.get('scope')!r}")
        if not str(entry.get("owner", "")).strip():
            errors.append(f"{where}: owner is missing or empty")
        if not entry.get("forbidden_meanings"):
            errors.append(f"{where}: forbidden_meanings must be a non-empty list")
        for alias in as_list(entry.get("aliases")):
            if alias == sym:
                continue
            if alias in symbols:
                errors.append(f"{where}: alias {alias!r} collides with a canonical symbol")
            if alias in aliases:
                errors.append(
                    f"{where}: alias {alias!r} collides with alias of {aliases[alias]!r}"
                )
            aliases[alias] = sym

    # --- glossary ---------------------------------------------------------
    terms = reg["glossary"]
    for tid, entry in terms.items():
        where = f"Term {tid}"
        if not str(entry.get("term", "")).strip():
            errors.append(f"{where}: term is missing or empty")
        if len(str(entry.get("definition", "")).strip()) < 40:
            errors.append(f"{where}: definition must be at least 40 characters")
        distinctions = as_list(entry.get("distinguishes_from"))
        if tid in distinctions:
            errors.append(f"{where}: distinguishes_from contains itself")
        if len(distinctions) != len(set(distinctions)):
            errors.append(f"{where}: duplicate distinguishes_from entries")
        for other in distinctions:
            if other not in terms:
                errors.append(f"{where}: unknown glossary term {other!r}")
        for owner in as_list(entry.get("owners")):
            if owner not in units:
                errors.append(f"{where}: owner {owner!r} missing from coverage.yaml")
        if not as_list(entry.get("canonical_refs")):
            errors.append(f"{where}: at least one canonical_refs entry is required")
        check_doc_paths(where, "canonical_refs", entry.get("canonical_refs"))

    return errors, unresolved


def find_stale_units(
    registry_dir: Path, repos_root: Path, against: str = "origin/main"
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Return (stale units -> causes, downstream units -> stale units they depend on).

    A unit is stale when a referenced implementation, design or decision source
    differs between its review basis commit and ``against`` in that repository.
    Repositories without a local checkout are skipped.
    """
    units = load_registry(registry_dir)["coverage"]
    stale: dict[str, list[str]] = {}
    for uid, unit in units.items():
        basis = (unit.get("review") or {}).get("basis") or {}
        by_repo: dict[str, list[str]] = {}
        for field in REVIEW_FIELDS:
            for ref in as_list(unit.get(field)):
                parsed = parse_reference(ref)
                if parsed and parsed[0] in basis:
                    by_repo.setdefault(parsed[0], []).append(parsed[1])
        for repo, paths in sorted(by_repo.items()):
            checkout = repos_root / repo
            if not checkout.is_dir():
                continue
            diff = subprocess.run(
                ["git", "-C", str(checkout), "diff", "--name-only", basis[repo], against, "--", *paths],
                capture_output=True,
                text=True,
            )
            if diff.returncode != 0:
                stale.setdefault(uid, []).append(
                    f"{repo}: cannot compare {basis[repo]}..{against} ({diff.stderr.strip()})"
                )
            for changed in diff.stdout.split():
                stale.setdefault(uid, []).append(f"{repo}:{changed} changed since {basis[repo]}")

    downstream: dict[str, list[str]] = {}
    frontier = set(stale)
    seen = set(stale)
    while frontier:
        reached = {
            uid: [d for d in as_list(unit.get("depends_on")) if d in frontier]
            for uid, unit in units.items()
            if uid not in seen
        }
        frontier = {uid for uid, via in reached.items() if via}
        for uid in frontier:
            downstream[uid] = reached[uid]
        seen |= frontier
    return stale, downstream


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--registry", type=Path, default=ROOT / "registry")
    parser.add_argument("--docs-root", type=Path, default=ROOT)
    parser.add_argument("--repos-root", type=Path, help="directory holding sibling checkouts")
    parser.add_argument("--stale", action="store_true", help="also report stale units")
    parser.add_argument("--against", default="origin/main", help="revision compared to the basis")
    parser.add_argument("--fail-on-stale", action="store_true")
    args = parser.parse_args(argv)

    errors, unresolved = validate(args.registry, args.docs_root, args.repos_root)
    for line in errors:
        print(f"ERROR {line}")
    if unresolved:
        print(f"{len(unresolved)} external reference(s) not resolved (no local checkout):")
        for line in unresolved:
            print(f"  {line}")
    if errors:
        print(f"Registry integrity: FAIL ({len(errors)} error(s))")
        return 1
    print("Registry integrity: PASS")

    if args.stale:
        if args.repos_root is None:
            parser.error("--stale requires --repos-root")
        stale, downstream = find_stale_units(args.registry, args.repos_root, args.against)
        for uid, causes in sorted(stale.items()):
            print(f"STALE {uid}")
            for cause in causes:
                print(f"  {cause}")
        for uid, via in sorted(downstream.items()):
            print(f"DOWNSTREAM {uid} (depends on {', '.join(via)})")
        print(f"Staleness: {len(stale)} stale, {len(downstream)} downstream")
        if stale and args.fail_on_stale:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
