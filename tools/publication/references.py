"""Turn the references a chapter makes into links.

A chapter names code (`world:src/world/journal.py::CausalJournal`), tests,
commits, decision records, findings, issues and components. Each becomes a
link: to GitHub at an exact revision, or to a place inside the publication.

Code links point at the revision the chapter was reviewed against, because
that is the code its text describes; a file that did not exist then is
linked at the revision of the build instead. Every link is checked against
the local checkouts, without network. A reference that exists at neither
revision fails the build. A reference that cannot be checked, because the
repository or the revision is not available, is still linked and counted as
unverified; a published edition allows none.
"""

from __future__ import annotations

import ast
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

GITHUB = "https://github.com/biopeia"
CODE_SPAN_RE = re.compile(r"`([^`\n]+)`")
SHA_RE = re.compile(r"[0-9a-f]{7,40}")
TEST_RE = re.compile(r"test_\w+")
DOCS_PATH_RE = re.compile(r"[\w./-]+\.(?:md|yaml|py|yml|toml)")


class ReferenceError(RuntimeError):
    """A reference names something that exists at no revision the build knows."""


def slug(heading: str) -> str:
    """The anchor GitHub gives a heading; links between documents use it."""
    kept = re.sub(r"[^\w\- ]", "", heading.strip().lower())
    return kept.replace(" ", "-")


def symbol_line(source: str, symbol: str) -> int | None:
    """Line of `Class`, `function` or `Class.member` in Python source."""
    try:
        scope: Any = ast.parse(source)
    except SyntaxError:
        return None
    found = None
    for name in symbol.split("."):
        found = next(
            (node for node in ast.walk(scope)
             if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name),
            None,
        ) or next(
            (node for node in ast.walk(scope)
             if isinstance(node, (ast.Assign, ast.AnnAssign))
             and any(getattr(target, "id", None) == name
                     for target in (node.targets if isinstance(node, ast.Assign) else [node.target]))),
            None,
        )
        if found is None:
            return None
        scope = found
    return found.lineno if found is not None else None


class Resolver:
    def __init__(self, reg: dict[str, Any], docs_root: Path, repos_root: Path | None, sources: dict[str, Any]) -> None:
        self.domains = list(reg["schema"]["domains"])
        self.repos = [*self.domains, "docs"]
        self.docs_root, self.repos_root, self.sources = docs_root, repos_root, sources
        self.findings, self.components = reg["findings"], set(reg["components"])
        self.units = reg["coverage"]
        # Which repository a reviewed commit belongs to, for a bare hash in prose.
        self.sha_repo: dict[str, str] = {}
        for unit in self.units.values():
            for repo, sha in (unit.get("review", {}).get("basis") or {}).items():
                self.sha_repo[str(sha)] = repo
        for repo, source in sources.items():
            if source.get("revision"):
                self.sha_repo[source["revision"]] = repo
        adr_root = reg["schema"]["layout"]["adrs"]
        self.records = {doc.name[:8]: f"{adr_root}{doc.name}" for doc in sorted((docs_root / adr_root).glob("ADR-*.md"))}
        alternatives = "|".join(re.escape(r) for r in self.repos)
        prefixes = "|".join(spec["prefix"] for spec in reg["schema"]["domains"].values())
        self.code_ref = re.compile(rf"({alternatives}):([^\s:`]+)(?:::([\w.]+))?")
        self.repo_at = re.compile(rf"({alternatives})@([0-9a-f]{{7,40}})")
        self.plain = re.compile(
            rf"\b(F-\d{{4}}|ADR-\d{{4}}|(?:{alternatives}|workspace)#\d+|(?:{prefixes})-[A-Z0-9]+(?:-[A-Z0-9]+)*)\b")
        self.stats: Counter[str] = Counter()
        self._cache: dict[tuple, Any] = {}

    # --- git, cached ----------------------------------------------------------

    def _dir(self, repo: str) -> Path | None:
        if repo == "docs":
            path = self.docs_root
        elif self.repos_root is not None:
            path = self.repos_root / repo
        else:
            return None
        return path if (path / ".git").exists() else None

    def _git(self, repo: str, *args: str) -> str | None:
        key = (repo, *args)
        if key not in self._cache:
            root = self._dir(repo)
            out = None
            if root is not None:
                done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)
                out = done.stdout if done.returncode == 0 else None
            self._cache[key] = out
        return self._cache[key]

    def _commit(self, repo: str, revision: str) -> str | None:
        """Full hash of a revision, when the checkout has it."""
        out = self._git(repo, "rev-parse", "--verify", "--quiet", f"{revision}^{{commit}}")
        return out.strip() if out else None

    def _kind(self, repo: str, commit: str, path: str) -> str | None:
        out = self._git(repo, "cat-file", "-t", f"{commit}:{path.rstrip('/')}")
        return out.strip() if out else None

    # --- links ----------------------------------------------------------------

    def blob(self, repo: str, path: str, basis: dict[str, str], symbol: str | None = None) -> str | None:
        """Link to a file or directory, at the reviewed revision when it existed there."""
        wanted = [basis.get(repo)] if repo != "docs" else []
        wanted.append((self.sources.get(repo) or {}).get("revision"))
        wanted = list(dict.fromkeys(str(r) for r in wanted if r))
        if not wanted:
            self.stats["without_revision"] += 1
            return None
        checked = False
        for position, revision in enumerate(wanted):
            commit = self._commit(repo, revision)
            if commit is None:
                continue
            checked = True
            kind = self._kind(repo, commit, path)
            if kind is None:
                continue
            self.stats["verified"] += 1
            self.stats["at_build_revision"] += position
            url = f"{GITHUB}/{repo}/{'tree' if kind == 'tree' else 'blob'}/{commit}/{path.rstrip('/')}"
            if symbol and path.endswith(".py"):
                line = symbol_line(self._git(repo, "show", f"{commit}:{path}") or "", symbol)
                if line is None:
                    self.stats["symbol_not_located"] += 1
                else:
                    url += f"#L{line}"
            return url
        if checked and repo == "docs" and (self.docs_root / path).exists():
            # Written but not yet committed: it will exist at the revision that publishes it.
            self.stats["unverified"] += 1
            return f"{GITHUB}/{repo}/blob/{wanted[0]}/{path.rstrip('/')}"
        if checked:
            raise ReferenceError(f"{repo}:{path} does not exist at {' or '.join(r[:12] for r in wanted)}")
        self.stats["unverified"] += 1
        return f"{GITHUB}/{repo}/blob/{wanted[0]}/{path.rstrip('/')}"

    def commit_url(self, repo: str, sha: str) -> str:
        return f"{GITHUB}/{repo}/commit/{self._commit(repo, sha) or sha}"

    def test(self, name: str, basis: dict[str, str]) -> str | None:
        """Link to where a cited test is defined, searched at the reviewed revision of each repository."""
        for repo in [*basis, *(d for d in self.domains if d not in basis)]:
            revision = basis.get(repo) or (self.sources.get(repo) or {}).get("revision")
            commit = self._commit(repo, str(revision)) if revision else None
            if commit is None:
                continue
            hits = self._git(repo, "grep", "-n", "-E", rf"def {name}\(", commit, "--", "*.py")
            if hits:
                _, path, line, _ = hits.splitlines()[0].split(":", 3)
                self.stats["verified"] += 1
                return f"{GITHUB}/{repo}/blob/{commit}/{path}#L{line}"
        self.stats["tests_not_located"] += 1
        return None

    def code_token(self, token: str, basis: dict[str, str]) -> dict[str, str] | None:
        """What a piece of code-formatted text refers to, if anything."""
        if token in self.components:
            return {"component": token}
        match = self.code_ref.fullmatch(token)
        if match:
            url = self.blob(match.group(1), match.group(2), basis, match.group(3))
            return {"url": url} if url else None
        match = self.repo_at.fullmatch(token)
        if match:
            return {"url": self.commit_url(match.group(1), match.group(2))}
        if SHA_RE.fullmatch(token):
            repo = next((r for sha, r in self.sha_repo.items() if sha.startswith(token)), None)
            return {"url": self.commit_url(repo, token)} if repo else None
        if TEST_RE.fullmatch(token):
            url = self.test(token, basis)
            return {"url": url} if url else None
        if DOCS_PATH_RE.fullmatch(token) and (self.docs_root / token).is_file():
            url = self.blob("docs", token, basis)
            return {"url": url} if url else None
        return None

    def plain_token(self, token: str) -> dict[str, str] | None:
        """What an identifier written in running text refers to."""
        if token in self.components:
            return {"component": token}
        if token.startswith("F-"):
            issue = (self.findings.get(token) or {}).get("issue")
            return {"url": issue} if issue else None
        if token.startswith("ADR-"):
            path = self.records.get(token)
            url = self.blob("docs", path, {}) if path else None
            return {"url": url} if url else None
        if "#" in token:
            repo, number = token.split("#")
            return {"url": f"{GITHUB}/{repo}/issues/{number}"}
        return None

    def chapter(self, markdown: str, basis: dict[str, str]) -> dict[str, dict[str, str]]:
        """Every reference of one chapter, keyed by the text that makes it."""
        out: dict[str, dict[str, str]] = {}
        for token in dict.fromkeys(CODE_SPAN_RE.findall(markdown)):
            found = self.code_token(token, basis)
            if found:
                out[token] = found
        for token in dict.fromkeys(self.plain.findall(markdown)):
            if token not in out:
                found = self.plain_token(token)
                if found:
                    out[token] = found
        return out

    def basis_of(self, document: str | None) -> dict[str, str]:
        """Revisions a document was reviewed against: those of the units it is the explanation of.

        A generated chapter has no document; it takes every unit's revisions,
        the first to name a repository winning.
        """
        basis: dict[str, str] = {}
        for unit in self.units.values():
            if document is None or document in (unit.get("canonical_docs") or []):
                for repo, sha in (unit.get("review", {}).get("basis") or {}).items():
                    basis.setdefault(repo, str(sha))
        return basis
