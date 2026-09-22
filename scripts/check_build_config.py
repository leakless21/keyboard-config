#!/usr/bin/env python3
"""
Structural validation test suite for ZMK build configuration and West manifest.

Enforces complete target object validation, pinned dependency revisions,
and synchronization between config/west.yml and GitHub Actions workflows.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

# Robust path configuration for local and package execution
SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from lib.validation import assert_eq, assert_in, assert_true, fail, load_yaml
except ImportError:
    from scripts.lib.validation import (
        assert_eq,
        assert_in,
        assert_true,
        fail,
        load_yaml,
    )
BUILD_YAML_PATH = REPO_ROOT / "build.yaml"
WEST_YML_PATH = REPO_ROOT / "config" / "west.yml"
BUILD_WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "build.yml"

EXPECTED_TARGETS: dict[str, dict[str, Any]] = {
    "corne-left": {
        "board": "nice_nano@2.0.0//zmk",
        "shield": "corne_left nice_oled",
        "snippet": "studio-rpc-usb-uart",
        "cmake-args": "-DCONFIG_ZMK_STUDIO=y",
        "role": "central",
    },
    "corne-right": {
        "board": "nice_nano@2.0.0//zmk",
        "shield": "corne_right nice_oled",
        "role": "peripheral",
    },
    "sofle-left": {
        "board": "nice_nano@2.0.0//zmk",
        "shield": "sofle_left nice_oled",
        "snippet": "studio-rpc-usb-uart",
        "cmake-args": "-DCONFIG_ZMK_STUDIO=y",
        "role": "central",
    },
    "sofle-right": {
        "board": "nice_nano@2.0.0//zmk",
        "shield": "sofle_right nice_oled",
        "role": "peripheral",
    },
    "settings-reset": {
        "board": "nice_nano@2.0.0//zmk",
        "shield": "settings_reset",
        "role": "recovery",
    },
}


def validate_build_yaml() -> None:
    """Validate build.yaml target matrix structurally using PyYAML."""
    data = load_yaml(BUILD_YAML_PATH)
    assert_true(isinstance(data, dict), "build.yaml root must be a YAML dictionary")
    assert_in("include", data, "build.yaml missing 'include' matrix")

    targets = data["include"]
    assert_true(isinstance(targets, list), "'include' must be a list of target specifications")

    found_artifacts = {}
    for entry in targets:
        artifact = entry.get("artifact-name")
        assert_true(artifact is not None, f"Target missing 'artifact-name': {entry}")
        found_artifacts[artifact] = entry

    for name, expected in EXPECTED_TARGETS.items():
        assert_in(name, found_artifacts, f"build.yaml missing expected target '{name}'")
        actual = found_artifacts[name]

        assert_eq(actual.get("board"), expected["board"], f"Target '{name}' board mismatch")
        assert_eq(actual.get("shield"), expected["shield"], f"Target '{name}' shield mismatch")

        if "snippet" in expected:
            assert_eq(actual.get("snippet"), expected["snippet"], f"Target '{name}' snippet mismatch")
        else:
            assert_true("snippet" not in actual, f"Target '{name}' should not specify snippet")

        if "cmake-args" in expected:
            assert_eq(actual.get("cmake-args"), expected["cmake-args"], f"Target '{name}' cmake-args mismatch")
        else:
            assert_true("cmake-args" not in actual, f"Target '{name}' should not specify cmake-args")

    print(f"PASS: build.yaml validated ({len(found_artifacts)} targets: {', '.join(sorted(found_artifacts))}).")


def validate_west_manifest() -> str:
    """Validate config/west.yml manifest and return pinned ZMK revision."""
    data = load_yaml(WEST_YML_PATH)
    assert_true(isinstance(data, dict), "config/west.yml root must be a dictionary")
    assert_in("manifest", data, "config/west.yml missing 'manifest' key")

    manifest = data["manifest"]
    assert_in("projects", manifest, "config/west.yml missing 'projects' list")

    projects = {p["name"]: p for p in manifest["projects"]}
    assert_in("zmk", projects, "config/west.yml missing 'zmk' project")
    assert_in("zmk-nice-oled", projects, "config/west.yml missing 'zmk-nice-oled' project")
    assert_in("zmk-helpers", projects, "config/west.yml missing 'zmk-helpers' project")

    # Verify immutable 40-character hex SHA revisions
    zmk_rev = projects["zmk"]["revision"]
    for proj_name in ["zmk", "zmk-nice-oled", "zmk-helpers"]:
        rev = projects[proj_name]["revision"]
        assert_true(
            bool(re.match(r"^[0-9a-f]{40}$", rev)),
            f"Project '{proj_name}' revision '{rev}' must be an immutable 40-char git commit SHA",
        )

    print("PASS: config/west.yml validated (all projects have immutable 40-character SHA revisions).")
    return zmk_rev


def validate_workflow_sync(zmk_rev: str) -> None:
    """Validate GitHub Actions workflows and verify ZMK revision synchronization."""
    if not BUILD_WORKFLOW_PATH.exists():
        fail(f"Workflow file not found: {BUILD_WORKFLOW_PATH}")

    content = BUILD_WORKFLOW_PATH.read_text(encoding="utf-8")

    # Verify reusable workflow reference matches config/west.yml
    workflow_sha_match = re.search(
        r"zmkfirmware/zmk/\.github/workflows/build-user-config\.yml@([0-9a-f]{40})",
        content,
    )
    if workflow_sha_match is None:
        fail("build.yml missing pinned zmkfirmware reusable workflow with 40-character SHA")
    workflow_sha = workflow_sha_match.group(1)
    assert_eq(
        workflow_sha,
        zmk_rev,
        f"ZMK reusable workflow SHA ({workflow_sha}) must match config/west.yml revision ({zmk_rev})",
    )

    print("PASS: .github/workflows/build.yml validated & synchronized with config/west.yml ZMK SHA.")


def main() -> None:
    print("=" * 70)
    print("RUNNING BUILD CONFIG & MANIFEST VALIDATION")
    print("=" * 70)
    validate_build_yaml()
    zmk_rev = validate_west_manifest()
    validate_workflow_sync(zmk_rev)
    print("=" * 70)
    print("ALL BUILD CONFIG & MANIFEST VALIDATION CHECKS PASSED.")
    print("=" * 70)


if __name__ == "__main__":
    main()
