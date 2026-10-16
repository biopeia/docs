#!/usr/bin/env python3
"""Run markdownlint-cli2 across all documentation in biopeia/docs."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_markdownlint(fix: bool = False) -> int:
    npx = shutil.which("npx")
    if not npx:
        print("warning: npx not found; skipping markdownlint execution", file=sys.stderr)
        return 0

    cmd = [npx, "--yes", "markdownlint-cli2"]
    if fix:
        cmd.append("--fix")

    result = subprocess.run(cmd, cwd=ROOT)
    return result.returncode


def main() -> int:
    fix = "--fix" in sys.argv
    return run_markdownlint(fix=fix)


if __name__ == "__main__":
    sys.exit(main())
