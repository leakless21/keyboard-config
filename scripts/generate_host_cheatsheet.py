#!/usr/bin/env python3
"""Generate and verify the macOS/OmniWM workflow cheatsheet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from generate_cheatsheet import compute_sha256, generate_pdf
    from lib.host_cheatsheet import HOST_CHEATSHEET_INPUTS, build_host_cheatsheet_model
    from lib.host_cheatsheet_svg import render_host_cheatsheet_svg
    from lib.validation import load_json
except ImportError:
    from scripts.generate_cheatsheet import compute_sha256, generate_pdf
    from scripts.lib.host_cheatsheet import HOST_CHEATSHEET_INPUTS, build_host_cheatsheet_model
    from scripts.lib.host_cheatsheet_svg import render_host_cheatsheet_svg
    from scripts.lib.validation import load_json

DOCS_GENERATED_DIR = REPO_ROOT / "docs" / "generated"
HOST_SHEET_NAME = "macos-omniwm-cheatsheet"


def format_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def input_hashes() -> Dict[str, str]:
    return {
        f"{name}_sha256": compute_sha256(path)
        for name, path in HOST_CHEATSHEET_INPUTS.items()
    }


def check_manifest(
    manifest_path: Path,
    pdf_path: Path,
    expected_svg_sha: str,
    expected_input_hashes: Dict[str, str],
) -> int:
    if not manifest_path.exists():
        print(f"FAIL: Manifest artifact missing: {manifest_path}", file=sys.stderr)
        return 1
    try:
        manifest = load_json(manifest_path)
    except Exception as error:
        print(f"FAIL: Could not load {manifest_path}: {error}", file=sys.stderr)
        return 1

    if manifest.get("schema") != 1:
        print(f"FAIL: Host cheatsheet manifest schema mismatch in {manifest_path.name}.", file=sys.stderr)
        return 1
    if manifest.get("cheatsheet") != HOST_SHEET_NAME:
        print(f"FAIL: Host cheatsheet manifest identity mismatch in {manifest_path.name}.", file=sys.stderr)
        return 1

    for key, expected in expected_input_hashes.items():
        if manifest.get(key) != expected:
            print(f"FAIL: {key} mismatch in {manifest_path.name}.", file=sys.stderr)
            return 1

    if manifest.get("svg_sha256") != expected_svg_sha:
        print(f"FAIL: SVG SHA mismatch in {manifest_path.name}.", file=sys.stderr)
        return 1
    if not pdf_path.exists() or pdf_path.stat().st_size == 0:
        print(f"FAIL: Host cheatsheet PDF missing or empty: {pdf_path}", file=sys.stderr)
        return 1
    if manifest.get("pdf_sha256") != compute_sha256(pdf_path):
        print(f"FAIL: PDF SHA mismatch in {manifest_path.name}.", file=sys.stderr)
        return 1
    return 0


def generate_host_cheatsheet(
    *,
    check: bool = False,
    svg_only: bool = False,
    out_dir: Optional[Path] = None,
) -> int:
    """Generate host SVG/PDF/manifest artifacts, or check them without writing."""
    output_dir = out_dir or DOCS_GENERATED_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    svg_path = output_dir / f"{HOST_SHEET_NAME}.svg"
    pdf_path = output_dir / f"{HOST_SHEET_NAME}.pdf"
    manifest_path = output_dir / f"{HOST_SHEET_NAME}.manifest.json"

    try:
        model = build_host_cheatsheet_model()
    except Exception as error:
        print(f"ERROR: Failed to build host cheatsheet model: {error}", file=sys.stderr)
        return 1

    svg_content = render_host_cheatsheet_svg(model)
    svg_sha = compute_sha256(svg_content)
    hashes = input_hashes()

    if check:
        if not svg_path.exists():
            print(f"FAIL: SVG artifact missing: {svg_path}", file=sys.stderr)
            return 1
        if compute_sha256(svg_path) != svg_sha:
            print(
                f"FAIL: {svg_path.name} is stale. Regenerate using 'uv run scripts/generate_host_cheatsheet.py'.",
                file=sys.stderr,
            )
            return 1
        result = check_manifest(manifest_path, pdf_path, svg_sha, hashes)
        if result == 0:
            print(f"PASS: {HOST_SHEET_NAME} artifacts are up to date.")
        return result

    svg_path.write_text(svg_content, encoding="utf-8")
    print(f"Generated: {format_path(svg_path)}")

    pdf_sha = ""
    if not svg_only:
        if generate_pdf(svg_path, pdf_path):
            pdf_sha = compute_sha256(pdf_path)
            print(f"Generated: {format_path(pdf_path)}")
        elif pdf_path.exists() and pdf_path.stat().st_size > 0:
            pdf_sha = compute_sha256(pdf_path)
            print(f"NOTE: Kept existing PDF: {format_path(pdf_path)}")
        else:
            print("NOTE: 'rsvg-convert' not found or failed. Skipped host PDF generation.", file=sys.stderr)

    manifest: Dict[str, Any] = {
        "schema": 1,
        "cheatsheet": HOST_SHEET_NAME,
        **hashes,
        "svg_sha256": svg_sha,
        "pdf_sha256": pdf_sha,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Generated: {format_path(manifest_path)}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a deterministic A4 landscape macOS/OmniWM workflow cheatsheet."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify host cheatsheet freshness without modifying artifacts",
    )
    parser.add_argument(
        "--svg-only",
        action="store_true",
        help="Generate only the host SVG and manifest",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Custom output directory for generated artifacts",
    )
    args = parser.parse_args()
    sys.exit(generate_host_cheatsheet(check=args.check, svg_only=args.svg_only, out_dir=args.out_dir))


if __name__ == "__main__":
    main()
