"""The generated reference page must match the registry."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import render_units  # noqa: E402


def test_reference_page_is_current() -> None:
    assert render_units.main(["--check"]) == 0


def test_every_unit_appears_once() -> None:
    text = render_units.render(ROOT / "registry")
    units = render_units.load_registry(ROOT / "registry")["coverage"]
    for uid in units:
        assert text.count(f"`{uid}` ·") == 1
