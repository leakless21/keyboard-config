#!/usr/bin/env python3
"""
Cheatsheet Generation & Freshness Verification CLI.

Generates deterministic A4 landscape cheatsheet artifacts (SVG, PDF, and manifest)
from parsed firmware keymaps, semantic protocol definitions, and presentation metadata
for Corne and Sofle keyboards.

Usage:
  uv run scripts/generate_cheatsheet.py corne
  uv run scripts/generate_cheatsheet.py sofle
  uv run scripts/generate_cheatsheet.py all
  uv run scripts/generate_cheatsheet.py all --check
  uv run scripts/generate_cheatsheet.py corne --png
  uv run scripts/generate_cheatsheet.py sofle --debug
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Robust path setup for standalone execution
SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from lib.cheatsheet import build_cheatsheet_model
    from lib.cheatsheet_svg import render_cheatsheet_svg
    from lib.validation import fail, load_json
except ImportError:
    from scripts.lib.cheatsheet import build_cheatsheet_model
    from scripts.lib.cheatsheet_svg import render_cheatsheet_svg
    from scripts.lib.validation import fail, load_json

DOCS_GENERATED_DIR = REPO_ROOT / "docs" / "generated"


def compute_sha256(data_or_path: Path | bytes | str) -> str:
    """Compute SHA256 hex digest for a file path or raw bytes/string."""
    hasher = hashlib.sha256()
    if isinstance(data_or_path, Path):
        hasher.update(data_or_path.read_bytes())
    elif isinstance(data_or_path, str):
        hasher.update(data_or_path.encode("utf-8"))
    else:
        hasher.update(data_or_path)
    return hasher.hexdigest()


def generate_pdf(svg_path: Path, pdf_path: Path) -> bool:
    """
    Render SVG to vector A4 landscape PDF using rsvg-convert with SOURCE_DATE_EPOCH=0.
    Returns True if successful, False if rsvg-convert is missing or fails.
    """
    rsvg_bin = shutil.which("rsvg-convert")
    if not rsvg_bin:
        return False

    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = "0"

    cmd = [
        rsvg_bin,
        "--format=pdf1.5",
        "--page-width=297mm",
        "--page-height=210mm",
        str(svg_path),
        "-o",
        str(pdf_path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if res.returncode != 0:
        print(f"WARNING: rsvg-convert failed: {res.stderr.strip()}", file=sys.stderr)
        return False
    return True


def generate_png(svg_path: Path, png_path: Path) -> bool:
    """Render SVG to 300-DPI A4 landscape PNG using rsvg-convert."""
    rsvg_bin = shutil.which("rsvg-convert")
    if not rsvg_bin:
        return False

    cmd = [
        rsvg_bin,
        "--width=3508",
        "--height=2480",
        "--keep-aspect-ratio",
        str(svg_path),
        "-o",
        str(png_path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode == 0


def generate_single_cheatsheet(
    keyboard: str = "corne",
    svg_only: bool = False,
    png: bool = False,
    debug: bool = False,
    check: bool = False,
    out_dir: Optional[Path] = None,
) -> int:
    """Generate cheatsheet artifacts for a single keyboard target."""
    kb = keyboard.lower()
    if kb not in ("corne", "sofle"):
        print(f"ERROR: Unsupported keyboard '{keyboard}'. Supported: 'corne', 'sofle', 'all'", file=sys.stderr)
        return 1

    keymap_path = REPO_ROOT / "config" / f"{kb}.keymap"
    cheatsheet_config_path = REPO_ROOT / "cheatsheets" / f"{kb}.yaml"
    aliases_path = REPO_ROOT / "keymap_drawer.config.yaml"
    protocol_path = REPO_ROOT / "protocol" / "semantic-v1.yaml"

    output_dir = out_dir or DOCS_GENERATED_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    svg_path = output_dir / f"{kb}-cheatsheet.svg"
    pdf_path = output_dir / f"{kb}-cheatsheet.pdf"
    png_path = output_dir / f"{kb}-cheatsheet.png"
    manifest_path = output_dir / f"{kb}-cheatsheet.manifest.json"

    # 1. Build intermediate semantic model
    try:
        model = build_cheatsheet_model(
            keyboard=kb,
            keymap_path=keymap_path,
            cheatsheet_config_path=cheatsheet_config_path,
            aliases_path=aliases_path,
            protocol_path=protocol_path,
        )
    except Exception as e:
        print(f"ERROR: Failed to build cheatsheet model for '{kb}': {e}", file=sys.stderr)
        return 1

    # 2. Render SVG
    svg_content = render_cheatsheet_svg(model, debug=debug)
    svg_bytes = svg_content.encode("utf-8")
    current_svg_sha = compute_sha256(svg_bytes)

    # Compute input hashes
    keymap_sha = compute_sha256(keymap_path)
    presentation_sha = compute_sha256(cheatsheet_config_path)
    aliases_sha = compute_sha256(aliases_path)
    protocol_sha = compute_sha256(protocol_path)

    # In --check mode: verify disk state without writing
    if check:
        if not svg_path.exists():
            print(f"FAIL: SVG artifact missing: {svg_path}", file=sys.stderr)
            return 1
        if not manifest_path.exists():
            print(f"FAIL: Manifest artifact missing: {manifest_path}", file=sys.stderr)
            return 1

        disk_svg_sha = compute_sha256(svg_path)
        if disk_svg_sha != current_svg_sha:
            print(
                f"FAIL: {svg_path.name} is stale. Regenerate using 'uv run scripts/generate_cheatsheet.py {kb}'.",
                file=sys.stderr,
            )
            return 1

        try:
            manifest_data = load_json(manifest_path)
        except Exception as e:
            print(f"FAIL: Could not load manifest: {e}", file=sys.stderr)
            return 1

        if manifest_data.get("keymap_sha256") != keymap_sha:
            print(f"FAIL: Keymap SHA mismatch in {manifest_path.name}.", file=sys.stderr)
            return 1
        if manifest_data.get("presentation_sha256") != presentation_sha:
            print(f"FAIL: Cheatsheet config SHA mismatch in {manifest_path.name}.", file=sys.stderr)
            return 1
        if manifest_data.get("aliases_sha256") != aliases_sha:
            print(f"FAIL: Presentation aliases SHA mismatch in {manifest_path.name}.", file=sys.stderr)
            return 1
        if manifest_data.get("protocol_sha256") != protocol_sha:
            print(f"FAIL: Semantic protocol SHA mismatch in {manifest_path.name}.", file=sys.stderr)
            return 1
        if manifest_data.get("svg_sha256") != current_svg_sha:
            print(f"FAIL: SVG SHA mismatch in {manifest_path.name}.", file=sys.stderr)
            return 1

        print(f"PASS: Cheatsheet artifacts for '{kb}' are up to date.")
        return 0

    # Normal generation mode: write SVG
    svg_path.write_text(svg_content, encoding="utf-8")
    print(f"Generated: {svg_path.relative_to(REPO_ROOT)}")

    # PDF generation
    pdf_sha = ""
    if not svg_only:
        if generate_pdf(svg_path, pdf_path):
            pdf_sha = compute_sha256(pdf_path)
            print(f"Generated: {pdf_path.relative_to(REPO_ROOT)}")
        else:
            if shutil.which("rsvg-convert") is None:
                print("NOTE: 'rsvg-convert' not found. Skipped PDF generation.", file=sys.stderr)
                if pdf_path.exists():
                    pdf_sha = compute_sha256(pdf_path)
            else:
                print(f"WARNING: PDF generation failed for '{kb}'.", file=sys.stderr)

    # Optional PNG generation
    if png:
        if generate_png(svg_path, png_path):
            print(f"Generated: {png_path.relative_to(REPO_ROOT)}")
        else:
            print(f"WARNING: PNG generation failed for '{kb}' (rsvg-convert required).", file=sys.stderr)

    # Generate Manifest
    manifest = {
        "schema": 1,
        "keyboard": kb,
        "keymap_sha256": keymap_sha,
        "protocol_sha256": protocol_sha,
        "presentation_sha256": presentation_sha,
        "aliases_sha256": aliases_sha,
        "svg_sha256": current_svg_sha,
        "pdf_sha256": pdf_sha,
    }

    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Generated: {manifest_path.relative_to(REPO_ROOT)}")
    return 0


def generate_cheatsheet(
    keyboard: str = "all",
    svg_only: bool = False,
    png: bool = False,
    debug: bool = False,
    check: bool = False,
    out_dir: Optional[Path] = None,
) -> int:
    """Dispatch cheatsheet generation for requested keyboard(s)."""
    kb = keyboard.lower()
    targets: List[str] = ["corne", "sofle"] if kb == "all" else [kb]

    exit_code = 0
    for target in targets:
        code = generate_single_cheatsheet(
            keyboard=target,
            svg_only=svg_only,
            png=png,
            debug=debug,
            check=check,
            out_dir=out_dir,
        )
        if code != 0:
            exit_code = code

    return exit_code


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate deterministic A4 landscape cheatsheet artifacts for Corne and Sofle keyboards."
    )
    parser.add_argument(
        "keyboard",
        nargs="?",
        default="all",
        help="Keyboard name to generate cheatsheet for: 'corne', 'sofle', or 'all' (default: all)",
    )
    parser.add_argument(
        "--svg-only",
        action="store_true",
        help="Generate SVG only, skip PDF/PNG generation",
    )
    parser.add_argument(
        "--png",
        action="store_true",
        help="Also export 300-DPI PNG artifact",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify artifact freshness without modifying files",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Render debug position overlays on keycaps",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Custom output directory for generated files",
    )

    args = parser.parse_args()
    code = generate_cheatsheet(
        keyboard=args.keyboard,
        svg_only=args.svg_only,
        png=args.png,
        debug=args.debug,
        check=args.check,
        out_dir=args.out_dir,
    )
    sys.exit(code)


if __name__ == "__main__":
    main()
