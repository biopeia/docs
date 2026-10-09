#!/usr/bin/env python3
"""Render the registry as one reference page, reference/units.md.

The page is generated: it restates nothing that is not in the registry, and
the registry stays the only source. For every unit it gathers the answers the
registry holds to the questions a reader asks of a component: what it is
responsible for, who owns it, where it is implemented, what state it keeps,
which contracts it takes part in, which decisions and designs govern it, which
tests back it, at which commit it was reviewed, and what is known to be open.

Run with --check to fail when the page on disk is out of date.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_registry import ROOT, as_list, load_registry, parse_reference  # noqa: E402

OUTPUT = ROOT / "reference" / "units.md"
DOMAIN_ORDER = ("world", "environment", "embodiment", "organism", "modality", "observation", "lab")


def link(path: str) -> str:
    return f"[{path}](../{path})"


def reference(ref: str) -> str:
    parsed = parse_reference(ref)
    if parsed and parsed[0] == "docs":
        return link(parsed[1])
    return f"`{ref}`"


def render(registry_dir: Path) -> str:
    reg = load_registry(registry_dir)
    units, components = reg["coverage"], reg["components"]
    by_unit = {c["coverage_unit"]: (cid, c) for cid, c in components.items()}
    findings, contracts = reg["findings"], reg["contracts"]
    out = [
        "# Units",
        "",
        "Generated from `registry/` by `tools/render_units.py`. Do not edit: change the",
        "registry and render again. The registry is the only source; this page",
        "restates it so that the answers about one unit can be read in one place.",
        "",
        f"{len(units)} units, {len(contracts)} cross-domain contracts, {len(findings)} findings.",
        "",
    ]
    for domain in DOMAIN_ORDER:
        mine = [(uid, u) for uid, u in units.items() if u.get("owner_domain") == domain]
        if not mine:
            continue
        out += [f"## {domain.capitalize()}", ""]
        for uid, unit in mine:
            out += [f"### {unit['title']}", "", f"`{uid}` · {unit['kind']} · {unit['status']}", ""]
            rows: list[tuple[str, str]] = []
            cid, comp = by_unit.get(uid, (None, None))
            if comp:
                rows.append(("Identifier", f"`{cid}`"))
                rows.append(("Responsible for", comp["authority"]["owns"]))
                rows.append(("Must not", "; ".join(as_list(comp["authority"]["must_not"]))))
            owner = domain
            others = as_list(unit.get("participating_domains"))
            rows.append(("Owned by", owner + (f"; also involves {', '.join(others)}" if others else "")))
            rows.append(("Explained in", ", ".join(link(p) for p in as_list(unit.get("canonical_docs")))))
            if as_list(unit.get("implementation")):
                rows.append(("Implemented in", ", ".join(f"`{r}`" for r in as_list(unit["implementation"]))))
            if comp:
                state = comp["state"]
                text = f"owner {state['owner']}, family {state['family']}"
                if "causal_state" in comp:
                    cs = comp["causal_state"]
                    text += (
                        f"; durable: {'yes' if cs['durable'] else 'no'}; in a causal cut: "
                        f"{'yes' if cs['in_causal_cut'] else 'no'}; a failed transition can leave: "
                        f"{cs['failed_transition_residue']}"
                    )
                if "lifecycle" in comp:
                    text += "; " + ", ".join(f"{k}: {v}" for k, v in comp["lifecycle"].items())
                rows.append(("State", text))
            mine_contracts = [
                f"{c['title']} ({c['agreement']})"
                for c in contracts.values()
                if any(p.get("unit") == uid for p in c.get("parties", []))
            ]
            if mine_contracts:
                rows.append(("Cross-domain contracts", "; ".join(mine_contracts)))
            if as_list(unit.get("depends_on")):
                rows.append(("Depends on", ", ".join(f"`{d}`" for d in as_list(unit["depends_on"]))))
            governed = as_list(unit.get("adrs")) + as_list(unit.get("design"))
            if governed:
                rows.append(("Governed by", ", ".join(reference(r) for r in governed)))
            if as_list(unit.get("tests")):
                rows.append(("Tests", ", ".join(f"`{r}`" for r in as_list(unit["tests"]))))
            review = unit.get("review") or {}
            if review.get("basis"):
                basis = ", ".join(f"{repo}@{str(sha)[:12]}" for repo, sha in review["basis"].items())
                rows.append(("Reviewed at", f"{basis} ({review.get('status', 'no review status')})"))
            mine_findings = [(fid, f) for fid, f in findings.items() if uid in as_list(f.get("units"))]
            if mine_findings:
                parts = []
                for fid, f in mine_findings:
                    where = f["status"]
                    if f.get("issue"):
                        where = f"[issue]({f['issue']})"
                    parts.append(f"{fid} {f['class'].replace('_', ' ')} ({where})")
                rows.append(("Known findings", "; ".join(parts)))
            out += ["| | |", "|---|---|"] + [f"| {k} | {v.strip()} |" for k, v in rows] + [""]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if the page is out of date")
    args = parser.parse_args(argv)
    text = render(ROOT / "registry")
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != text:
            print("reference/units.md is out of date; run python tools/render_units.py")
            return 1
        print("reference/units.md is current")
        return 0
    OUTPUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
