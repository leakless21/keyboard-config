#!/usr/bin/env python3
"""
Protocol File Generator.

Generates mechanical artifacts and canonical documentation tables directly
from protocol/semantic-v1.yaml to prevent manual drift.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Robust path configuration for local and package execution
SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from lib.protocol import ProtocolManifest, load_protocol
    from lib.validation import fail
except ImportError:
    from scripts.lib.protocol import ProtocolManifest, load_protocol
    from scripts.lib.validation import fail
DOCS_HOST_PROTOCOL_PATH = REPO_ROOT / "docs" / "host-protocol.md"


def generate_host_protocol_table(manifest: ProtocolManifest) -> str:
    """Generate Markdown matrix table from canonical protocol actions."""
    lines = [
        "| Signal | Semantic Action | macOS Host (OmniWM + Karabiner + Ghostty + Spotlight) | Windows Host (GlazeWM + AutoHotkey + Windows Terminal + Search) |",
        "|---|---|---|---|",
    ]

    for action in manifest.actions.values():
        sig_str = f"`{action.signal.canonical_str}`"
        desc = action.description
        macos = action.host_implementations.get("macos", "-")
        windows = action.host_implementations.get("windows", "-")
        lines.append(f"| {sig_str} | {desc} | {macos} | {windows} |")

    return "\n".join(lines)


def update_host_protocol_doc(manifest: ProtocolManifest) -> bool:
    """Update docs/host-protocol.md with the generated matrix table."""
    if not DOCS_HOST_PROTOCOL_PATH.exists():
        fail(f"File not found: {DOCS_HOST_PROTOCOL_PATH}")

    content = DOCS_HOST_PROTOCOL_PATH.read_text(encoding="utf-8")
    table = generate_host_protocol_table(manifest)

    # Replace section between ## 1. Canonical Protocol Matrix and the next ---
    pattern = r"(## 1\. Canonical Protocol Matrix\s*\n\s*\n)(?:\|[^\n]+\|\n)+(?=\s*\n---)"
    replacement = rf"\g<1>{table}"

    new_content, count = re.subn(pattern, replacement, content)
    if count == 0:
        # If pattern didn't match, attempt general matrix replacement
        pattern2 = r"(## 1\. Canonical Protocol Matrix\s*\n\s*\n)([\s\S]*?)(?=\n---)"
        new_content, count = re.subn(pattern2, rf"\g<1>{table}\n", content)

    if count == 0:
        fail("Could not find Protocol Matrix section in docs/host-protocol.md")

    if new_content != content:
        DOCS_HOST_PROTOCOL_PATH.write_text(new_content, encoding="utf-8")
        return True
    return False


def main() -> None:
    manifest = load_protocol()
    updated = update_host_protocol_doc(manifest)
    if updated:
        print("Updated docs/host-protocol.md from protocol/semantic-v1.yaml.")
    else:
        print("docs/host-protocol.md is up to date.")


if __name__ == "__main__":
    main()
