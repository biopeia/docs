"""Render a Mermaid diagram to PNG with one pinned mermaid-cli version.

A diagram is part of the published text, so rendering fails closed: a missing
`mmdc`, a different version or a diagram that does not compile is an error,
never a silently dropped figure.
"""

from __future__ import annotations

import json
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path

# @mermaid-js/mermaid-cli. Change it here and in .github/workflows together.
PINNED_VERSION = "11.4.2"
# Pixels rendered per CSS pixel; the layout size is the PNG size divided by it.
SCALE = 2


class MermaidError(RuntimeError):
    pass


def available() -> bool:
    return shutil.which("mmdc") is not None


def render(source: str) -> bytes:
    """PNG bytes of one diagram."""
    mmdc = shutil.which("mmdc")
    if mmdc is None:
        raise MermaidError(f"a diagram needs mmdc (@mermaid-js/mermaid-cli@{PINNED_VERSION}), which is not installed")
    version = subprocess.run([mmdc, "--version"], capture_output=True, text=True, check=False).stdout.strip()
    if version != PINNED_VERSION:
        raise MermaidError(f"mmdc is version {version or 'unknown'}; the build is pinned to {PINNED_VERSION}")
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        (work / "diagram.mmd").write_text(source, encoding="utf-8")
        # Chromium refuses its sandbox as root, which is how CI containers run.
        (work / "puppeteer.json").write_text(json.dumps({"args": ["--no-sandbox"]}), encoding="utf-8")
        done = subprocess.run(
            [mmdc, "-i", "diagram.mmd", "-o", "diagram.png", "-s", str(SCALE), "-b", "white",
             "-p", "puppeteer.json", "-q"],
            cwd=work, capture_output=True, text=True, check=False,
        )
        output = work / "diagram.png"
        if done.returncode != 0 or not output.is_file():
            raise MermaidError(f"diagram does not render: {(done.stderr or done.stdout).strip()[:500]}")
        return output.read_bytes()


def png_size(data: bytes) -> tuple[int, int]:
    """Width and height in pixels, from the PNG header."""
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise MermaidError("diagram output is not a PNG")
    return struct.unpack(">II", data[16:24])
