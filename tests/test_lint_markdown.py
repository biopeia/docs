from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import lint_markdown  # noqa: E402


def test_markdownlint_passes_with_zero_issues():
    if not shutil.which("npx"):
        pytest.skip("npx not available in environment")
    assert lint_markdown.run_markdownlint() == 0
