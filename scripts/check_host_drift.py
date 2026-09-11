#!/usr/bin/env python3
"""
Live host drift check: does the machine's active configuration still match the repo?

Karabiner-Elements stores the manipulators of an *enabled* rule inline in
`~/.config/karabiner/karabiner.json`. The asset file in
`~/.config/karabiner/assets/complex_modifications/` is only the source it was
copied from. Both layers can therefore hold a stale copy while the checked-in
`hosts/macos/karabiner/*.json` files look perfectly correct — which is exactly
how a fixed adapter can appear to have no effect on the keyboard.

This check compares, for every adapter rule in the repo:
  1. the live asset copy (following symlinks), and
  2. the live inline rule in the active Karabiner profile

It also verifies the OmniWM settings symlink still points at the repo file and
that the running app has not rewritten the checked-in file.

Read-only: it never writes, and exits 1 when drift is detected.
Remediate with `uv run scripts/sync_karabiner.py --apply`.

Usage:
  uv run scripts/check_host_drift.py
  uv run scripts/check_host_drift.py --verbose
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

# Robust path setup for standalone execution
SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from lib.validation import load_json
except ImportError:
    from scripts.lib.validation import load_json

KARABINER_DIR = REPO_ROOT / "hosts" / "macos" / "karabiner"
OMNIWM_REPO_PATH = REPO_ROOT / "hosts" / "macos" / "omniwm" / "settings.toml"

KARABINER_HOME = Path(os.path.expanduser("~/.config/karabiner"))
KARABINER_PROFILE = KARABINER_HOME / "karabiner.json"
KARABINER_ASSETS = KARABINER_HOME / "assets" / "complex_modifications"
OMNIWM_LIVE_LINK = Path(os.path.expanduser("~/.config/omniwm/settings.toml"))


def adapter_rules() -> dict[str, list[dict[str, Any]]]:
    """Map rule description -> rule object for every repo Karabiner adapter."""
    rules: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(KARABINER_DIR.glob("*.json")):
        data = load_json(path)
        for rule in data.get("rules", []):
            description = rule.get("description", "")
            rules.setdefault(description, []).append(
                {"rule": rule, "source": path.name}
            )
    return rules


def profile_rules(data: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Map rule description -> inline rules for every Karabiner profile."""
    found: dict[str, list[dict[str, Any]]] = {}
    for profile in data.get("profiles", []):
        complex_mods = profile.get("complex_modifications", {})
        for rule in complex_mods.get("rules", []):
            found.setdefault(rule.get("description", ""), []).append(
                {"profile": profile.get("name", "?"), "rule": rule}
            )
    return found


def check_karabiner(verbose: bool) -> list[str]:
    """Return a list of drift problems for the live Karabiner configuration."""
    problems: list[str] = []

    if not KARABINER_HOME.exists():
        print("SKIP: Karabiner-Elements config not present (not this machine).")
        return problems

    repo_rules = adapter_rules()

    # --- Layer 1: asset copies -------------------------------------------------
    for description, entries in repo_rules.items():
        for entry in entries:
            source_name = entry["source"]
            asset_path = KARABINER_ASSETS / source_name
            if not asset_path.exists():
                problems.append(
                    f"Karabiner asset missing: {asset_path} "
                    f"(repo file {source_name} is not deployed)"
                )
                continue

            asset_data = load_json(asset_path)
            asset_rule = next(
                (r for r in asset_data.get("rules", []) if r.get("description") == description),
                None,
            )
            if asset_rule is None:
                problems.append(
                    f"Karabiner asset {source_name} is missing rule '{description[:60]}...'"
                )
                continue
            if asset_rule.get("manipulators") != entry["rule"].get("manipulators"):
                problems.append(
                    f"Karabiner asset drift: {asset_path} rule '{description[:60]}...' "
                    f"differs from {source_name} "
                    f"(asset has {len(asset_rule.get('manipulators', []))} manipulators, "
                    f"repo has {len(entry['rule'].get('manipulators', []))})"
                )
            elif verbose:
                print(f"  ok asset: {source_name} :: {description[:60]}")

    # --- Layer 2: inline rules in the active profile ---------------------------
    if not KARABINER_PROFILE.exists():
        problems.append(
            f"Karabiner profile missing: {KARABINER_PROFILE} "
            f"(rules cannot be active without it)"
        )
        return problems

    live_rules = profile_rules(load_json(KARABINER_PROFILE))

    for description, entries in repo_rules.items():
        inline = live_rules.get(description)
        if not inline:
            print(
                f"NOTE: rule not enabled in Karabiner: '{description[:70]}' "
                f"— enable it in Karabiner-Elements > Complex Modifications."
            )
            continue

        for match in inline:
            live_manipulators = match["rule"].get("manipulators", [])
            repo_manipulators = entries[0]["rule"].get("manipulators", [])
            if live_manipulators != repo_manipulators:
                problems.append(
                    f"Karabiner inline drift (profile '{match['profile']}'): rule "
                    f"'{description[:60]}...' has {len(live_manipulators)} live manipulators "
                    f"but repo has {len(repo_manipulators)} — the keyboard is running a stale copy"
                )
            elif verbose:
                print(
                    f"  ok inline: profile '{match['profile']}' :: {description[:60]} "
                    f"({len(live_manipulators)} manipulators)"
                )

    return problems


def check_omniwm(verbose: bool) -> list[str]:
    """Return a list of drift problems for the live OmniWM configuration."""
    problems: list[str] = []

    if not OMNIWM_LIVE_LINK.exists():
        print("SKIP: OmniWM live settings not present (not this machine).")
        return problems

    if OMNIWM_LIVE_LINK.is_symlink():
        target = Path(os.path.realpath(OMNIWM_LIVE_LINK))
        if target != OMNIWM_REPO_PATH.resolve():
            problems.append(
                f"OmniWM settings symlink points elsewhere: {OMNIWM_LIVE_LINK} -> {target} "
                f"(expected {OMNIWM_REPO_PATH})"
            )
        elif verbose:
            print(f"  ok symlink: {OMNIWM_LIVE_LINK} -> {target}")
    else:
        live_bytes = OMNIWM_LIVE_LINK.read_bytes()
        repo_bytes = OMNIWM_REPO_PATH.read_bytes()
        if live_bytes != repo_bytes:
            problems.append(
                f"OmniWM live settings differ from repo file: {OMNIWM_LIVE_LINK} "
                f"(not a symlink; content drift)"
            )
        elif verbose:
            print("  ok copy: OmniWM live settings match repo file contents")

    # The running app can rewrite its settings file; surface that as repo drift.
    if (REPO_ROOT / ".git").exists():
        result = subprocess.run(
            ["git", "diff", "--quiet", "--", str(OMNIWM_REPO_PATH.relative_to(REPO_ROOT))],
            cwd=REPO_ROOT,
            capture_output=True,
            check=False,
        )
        if result.returncode == 1:
            problems.append(
                "OmniWM settings.toml differs from HEAD: either you have uncommitted edits, or the "
                "running OmniWM app rewrote the live file it owns through the symlink. The checked-in "
                "config and the active config disagree until one side is reconciled."
            )
        elif verbose and result.returncode == 0:
            print("  ok git: OmniWM settings.toml matches HEAD")

    return problems


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify the live macOS host configuration still matches this repository."
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="print per-rule status for rules that are in sync",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("CHECKING LIVE HOST CONFIGURATION DRIFT")
    print("=" * 70)

    problems = check_karabiner(args.verbose) + check_omniwm(args.verbose)

    if problems:
        print()
        for problem in problems:
            print(f"DRIFT: {problem}")
        print()
        print("Remediate Karabiner drift with:")
        print("  uv run scripts/sync_karabiner.py --apply")
        print("(then confirm no stale copy remains: uv run scripts/check_host_drift.py)")
        sys.exit(1)

    print()
    print("PASS: live host configuration matches the repository (no drift).")


if __name__ == "__main__":
    main()
