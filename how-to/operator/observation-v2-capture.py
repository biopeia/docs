#!/usr/bin/env python3
"""Run a bounded local World session while capturing its ObservationPlane."""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import importlib
import json
import subprocess
import uuid
from pathlib import Path

from observation import ArchiveReader, LocalObservationArchiveCapture
from world.causal_cycle import run_scalar_sensorimotor_session
from world.m1_process import verified_revisions
from world.m1_profile import construct_fresh_runtime, load_operator_profile


REPOSITORIES = ("world", "organism", "embodiment", "environment", "modality", "observation")


def git(root: Path, repo: str, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root / "repos" / repo), *args],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def source_snapshot(root: Path) -> dict[str, dict[str, object]]:
    result = {}
    for name in REPOSITORIES:
        status = git(root, name, "status", "--porcelain", "--untracked-files=all")
        result[name] = {
            "git_sha": git(root, name, "rev-parse", "HEAD"),
            "worktree_clean": not bool(status),
            "worktree_status": status.splitlines(),
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cycles", type=int, default=10)
    args = parser.parse_args()
    root = args.workspace.resolve()
    output = args.output.resolve()
    if not 1 <= args.cycles <= 100:
        parser.error("--cycles must be between 1 and 100")
    output.mkdir(parents=True, exist_ok=False)
    archive_dir = output / "archive-dir"
    archive_dir.mkdir()
    state_parent = output / "state-parent"
    state_parent.mkdir()
    archive_path = archive_dir / "observations.sqlite"
    state_root = state_parent / "world-state"

    profile_path = root / "repos/world/profiles/m1/scalar-sensorimotor-mujoco-3.15-v2.json"
    profile, profile_sha = load_operator_profile(profile_path)
    revisions = verified_revisions()
    before = source_snapshot(root)
    for name in REPOSITORIES:
        revisions[name] = str(before[name]["git_sha"])
        revisions[f"{name}_worktree"] = "clean" if before[name]["worktree_clean"] else "dirty"

    module_names = {name: name for name in REPOSITORIES}
    module_paths = {
        name: str(Path(importlib.import_module(module_name).__file__).resolve())
        for name, module_name in module_names.items()
    }
    for name, module_path in module_paths.items():
        if not Path(module_path).is_relative_to((root / "repos" / name).resolve()):
            raise RuntimeError(f"{name} imported outside its recorded checkout: {module_path}")

    run_id = f"observation-v2-{uuid.uuid4()}"
    runtime = construct_fresh_runtime(profile, profile_sha, state_root, revisions, observation_port=0)
    capture = LocalObservationArchiveCapture(runtime.observation_plane, archive_path, max_payload_bytes=100_000_000)
    try:
        capture.start()
        result = run_scalar_sensorimotor_session(
            runtime.world,
            runtime.observation_plane,
            run_id=run_id,
            cycle_inputs=runtime.cycle_inputs,
            source_revisions=revisions,
            max_cycles=args.cycles,
            retain_cycle_results=False,
        )
    finally:
        # A failed capture shutdown must not leak the bridge. ``stop`` is
        # safe after a partially completed start and reports worker errors in
        # the capture status when it can do so.
        try:
            capture.stop()
        finally:
            runtime.observation_bridge.close()
    if result.status.value != "completed" or result.completed_cycle_count != args.cycles:
        raise RuntimeError(
            f"World session did not complete the requested cycles: "
            f"status={result.status.value}, completed={result.completed_cycle_count}, "
            f"requested={args.cycles}, error={result.error}"
        )
    capture_status = dataclasses.asdict(capture.status())
    if capture_status["error"] is not None:
        raise RuntimeError(f"capture reported error: {capture_status['error']}")
    after = source_snapshot(root)
    if before != after:
        raise RuntimeError("source checkout identity/status changed during capture")

    with ArchiveReader(archive_path) as reader:
        integrity = reader.integrity_check()
        catalog = reader.capture_catalog()
        coverage_result = reader.capture_coverage(capture.capture_id)
    coverage = coverage_result.coverage
    report = {
        "run_id": run_id,
        "world_status": result.status.value,
        "completed_cycle_count": result.completed_cycle_count,
        "last_committed_tick": result.last_committed_cut.causal_tick if result.last_committed_cut else None,
        "last_commit_id": result.last_committed_cut.commit_id if result.last_committed_cut else None,
        "session_error": result.error,
        "profile_id": profile["profile_id"],
        "profile_sha256": profile_sha,
        "source_revisions": revisions,
        "source_module_paths": module_paths,
        "source_snapshot_before": before,
        "source_snapshot_after": after,
        "capture_id": capture.capture_id,
        "capture_status": capture_status,
        "catalog_status": catalog.status,
        "coverage_result_status": coverage_result.status,
        "coverage": dataclasses.asdict(coverage) if coverage else None,
        "integrity_check": integrity,
        "archive_sha256": hashlib.sha256(archive_path.read_bytes()).hexdigest(),
    }
    (output / "runtime-capture.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
