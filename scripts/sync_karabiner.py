#!/usr/bin/env python3
"""
Deploy repo Karabiner adapters into the live Karabiner-Elements configuration.

Karabiner-Elements copies the manipulators of an enabled rule *inline* into
`~/.config/karabiner/karabiner.json`. Editing `hosts/macos/karabiner/*.json`
alone therefore changes nothing on the keyboard: the stale inline copy keeps
running. This helper reconciles both live layers from the repo:

  1. asset files under `~/.config/karabiner/assets/complex_modifications/`
     (skipped when already symlinked to the repo), and
  2. the inline rule bodies in `~/.config/karabiner/karabiner.json`.

It only ever rewrites rules whose description already exists in the live config
(an existing enabled rule); rules that are not enabled are reported, never
silently enabled — enabling a rule stays a deliberate act in the Karabiner UI.

Dry-run by default. `--apply` writes a timestamped backup first and lints the
repo adapters with Karabiner's own linter when it is available.

Usage:
  uv run scripts/sync_karabiner.py                  # show what would change
  uv run scripts/sync_karabiner.py --apply          # write changes (+ backup)
  uv run scripts/sync_karabiner.py --apply --reload # also reload Karabiner
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
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
    from lib.validation import fail, load_json
except ImportError:
    from scripts.lib.validation import fail, load_json

KARABINER_DIR = REPO_ROOT / "hosts" / "macos" / "karabiner"
KARABINER_HOME = Path(os.path.expanduser("~/.config/karabiner"))
KARABINER_PROFILE = KARABINER_HOME / "karabiner.json"
KARABINER_ASSETS = KARABINER_HOME / "assets" / "complex_modifications"
KARABINER_CLI = Path(
    "/Library/Application Support/org.pqrs/Karabiner-Elements/bin/karabiner_cli"
)
KARABINER_RELOAD_LABEL = "org.pqrs.service.agent.Karabiner-Console-User-Server"


def repo_adapters() -> dict[str, Any]:
    """Map rule description -> (source file name, rule object) for repo adapters."""
    adapters: dict[str, Any] = {}
    for path in sorted(KARABINER_DIR.glob("*.json")):
        data = load_json(path)
        for rule in data.get("rules", []):
            adapters[rule.get("description", "")] = (path.name, rule)
    return adapters


def lint_repo_adapters() -> None:
    """Fail fast when Karabiner's own linter rejects a repo adapter."""
    if not KARABINER_CLI.exists():
        print("NOTE: karabiner_cli not found; skipping Karabiner lint.")
        return
    patterns = [str(KARABINER_DIR / "*.json")]
    result = subprocess.run(
        [str(KARABINER_CLI), "--lint-complex-modifications", *patterns],
        capture_output=True,
        text=True,
        check=False,
    )
    print(result.stdout.strip() or result.stderr.strip())
    if result.returncode != 0:
        fail("Karabiner lint failed; refusing to deploy. Fix the adapter JSON first.")


def sync_assets(apply: bool, changed: list[str]) -> None:
    """Refresh non-symlinked asset copies from the repo."""
    for path in sorted(KARABINER_DIR.glob("*.json")):
        asset_path = KARABINER_ASSETS / path.name
        if asset_path.is_symlink():
            print(f"  symlink ok: {asset_path} -> {os.path.realpath(asset_path)}")
            continue
        if not asset_path.exists():
            print(f"  asset missing: {asset_path} (copy {path.name} to deploy it)")
            continue
        if asset_path.read_bytes() == path.read_bytes():
            print(f"  asset ok: {path.name} already matches repo")
            continue
        if apply:
            shutil.copy2(path, asset_path)
            changed.append(str(asset_path))
            print(f"  asset updated: {asset_path} <- {path.name}")
        else:
            print(f"  asset stale: {asset_path} differs from {path.name} (would copy)")


def sync_inline_rules(config: dict[str, Any], apply: bool, changed: list[str]) -> None:
    """Replace inline rule bodies for rules that are already enabled."""
    adapters = repo_adapters()
    for profile in config.get("profiles", []):
        profile_name = profile.get("name", "?")
        complex_mods = profile.get("complex_modifications", {})
        for rule in complex_mods.get("rules", []):
            description = rule.get("description", "")
            entry = adapters.get(description)
            if entry is None:
                print(
                    f"  note: live rule not found in repo (left alone): '{description[:70]}'"
                )
                continue
            source_name, repo_rule = entry
            if rule.get("manipulators") == repo_rule.get("manipulators"):
                print(
                    f"  inline ok: profile '{profile_name}' :: {source_name} :: "
                    f"{len(repo_rule.get('manipulators', []))} manipulators"
                )
                continue
            live_count = len(rule.get("manipulators", []))
            repo_count = len(repo_rule.get("manipulators", []))
            if apply:
                rule["manipulators"] = repo_rule["manipulators"]
                changed.append(f"karabiner.json[{profile_name}]: {description[:60]}")
                print(
                    f"  inline UPDATED: profile '{profile_name}' :: {source_name} :: "
                    f"{live_count} -> {repo_count} manipulators"
                )
            else:
                print(
                    f"  inline STALE: profile '{profile_name}' :: {source_name} :: "
                    f"{live_count} -> {repo_count} manipulators (would update)"
                )

    if apply:
        return

    # Report enabled repo rules that the live profile does not contain at all.
    live_descriptions = {
        rule.get("description", "")
        for profile in config.get("profiles", [])
        for rule in profile.get("complex_modifications", {}).get("rules", [])
    }
    for description, (source_name, _) in adapters.items():
        if description not in live_descriptions:
            print(
                f"  not enabled: '{description[:70]}' ({source_name}) — "
                f"enable it in Karabiner-Elements > Complex Modifications"
            )


def reload_karabiner() -> None:
    """Ask launchd to restart Karabiner's config server so edits take effect."""
    uid = os.getuid()
    result = subprocess.run(
        ["launchctl", "kickstart", "-k", f"gui/{uid}/{KARABINER_RELOAD_LABEL}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        print(f"Reloaded Karabiner ({KARABINER_RELOAD_LABEL}).")
    else:
        print(
            "WARNING: could not reload Karabiner automatically "
            f"({result.stderr.strip() or result.returncode}). "
            "Toggle the rule off/on in Karabiner-Elements to apply changes."
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Deploy repo Karabiner adapters into the live Karabiner-Elements config."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="write changes (a timestamped backup of karabiner.json is created first)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="ask launchd to reload Karabiner after writing changes",
    )
    args = parser.parse_args()

    if not KARABINER_HOME.exists():
        print("SKIP: Karabiner-Elements is not installed for this user; nothing to sync.")
        return
    if not KARABINER_PROFILE.exists():
        fail(f"Karabiner profile not found: {KARABINER_PROFILE}")

    print("=" * 70)
    print("KARABINER ADAPTER SYNC" + ("" if args.apply else " (DRY RUN)"))
    print("=" * 70)

    lint_repo_adapters()

    config = load_json(KARABINER_PROFILE)
    changed: list[str] = []

    print("Asset layer:")
    sync_assets(args.apply, changed)

    print("Inline rule layer:")
    sync_inline_rules(config, args.apply, changed)

    if not args.apply:
        print()
        print("DRY RUN: no files written. Re-run with --apply to deploy.")
        if changed:
            print("Pending changes:")
            for item in changed:
                print(f"  - {item}")
        return

    if not changed:
        print()
        print("PASS: live Karabiner configuration already matches the repository.")
        return

    backup = KARABINER_PROFILE.with_name(
        f"{KARABINER_PROFILE.name}.bak.{int(time.time())}"
    )
    shutil.copy2(KARABINER_PROFILE, backup)
    KARABINER_PROFILE.write_text(json.dumps(config, indent=4) + "\n")
    print(f"Backup: {backup}")
    print(f"Wrote:  {KARABINER_PROFILE}")
    print("Changed:")
    for item in changed:
        print(f"  - {item}")

    if args.reload:
        reload_karabiner()
    else:
        print("Reload Karabiner to apply (re-run with --reload, or toggle the rule in the UI).")

    print()
    print("Verify with: uv run scripts/check_host_drift.py")


if __name__ == "__main__":
    main()
