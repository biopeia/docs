"""Regression checks for Docs' security-sensitive Actions baseline."""

from pathlib import Path
import re

import yaml


ROOT = Path(__file__).parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
SHA = re.compile(r"^[0-9a-f]{40}$")


def load_yaml(path: Path) -> dict:
    return yaml.load(path.read_text(), Loader=yaml.BaseLoader)


def test_every_workflow_action_and_reusable_workflow_is_pinned_to_a_full_sha():
    for path in WORKFLOWS.glob("*.yml"):
        workflow = load_yaml(path)
        for job in workflow.get("jobs", {}).values():
            for step in job.get("steps", []):
                uses = step.get("uses", "")
                if uses:
                    ref = uses.rsplit("@", 1)[-1]
                    assert SHA.fullmatch(ref), f"{path}: mutable action reference {uses}"


def test_ci_has_least_privilege_and_required_stable_jobs_are_secretless():
    workflow = load_yaml(WORKFLOWS / "ci.yml")
    assert workflow["permissions"] == {"contents": "read"}
    assert {"registry", "cross-repository"} <= set(workflow["jobs"])
    text = (WORKFLOWS / "ci.yml").read_text()
    assert "${{ secrets." not in text
    assert "create-github-app-token" not in text
    assert "branches: [main]" in text


def test_publication_has_read_only_build_and_tag_scoped_release_write():
    workflow = load_yaml(WORKFLOWS / "publication.yml")
    assert workflow["permissions"] == {"contents": "read"}
    assert workflow["jobs"]["publication"].get("permissions") is None
    release = workflow["jobs"]["release"]
    assert release["permissions"] == {"contents": "write"}
    assert release["if"] == "startsWith(github.ref, 'refs/tags/docs-v')"
    assert "publication" in release["needs"]
    text = (WORKFLOWS / "publication.yml").read_text()
    assert "${{ secrets." not in text
    assert "create-github-app-token" not in text


def test_dependabot_tracks_uv_and_actions_with_bounded_grouping():
    config = load_yaml(ROOT / ".github" / "dependabot.yml")
    assert config["version"] == "2"
    updates = {entry["package-ecosystem"]: entry for entry in config["updates"]}
    assert set(updates) == {"uv", "github-actions"}
    for entry in updates.values():
        assert entry["schedule"]["interval"] == "weekly"
        assert entry["open-pull-requests-limit"] == "5"
        group = next(iter(entry["groups"].values()))
        assert set(group["update-types"]) == {"minor", "patch"}
