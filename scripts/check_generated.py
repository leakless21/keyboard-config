#!/usr/bin/env python3
"""
Generated Artifacts & Freshness Validator.

Ensures:
1. All generated artifacts (e.g. docs/host-protocol.md) are strictly fresh and in sync with protocol/semantic-v1.yaml.
2. Undeclared Signal Detection: Scans firmware keymaps and host configs to ensure no undeclared F13-F24 signals or aliases exist.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Set

# Robust path configuration for local and package execution
SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from generate_protocol_files import generate_host_protocol_table
    from lib.cheatsheet import (
        CorneGeometry,
        SofleGeometry,
        build_cheatsheet_model,
        load_presentation_aliases,
    )
    from lib.cheatsheet_svg import render_cheatsheet_svg
    from lib.keymap_parser import parse_keymap_file
    from lib.protocol import ProtocolManifest, load_protocol
    from lib.validation import assert_eq, assert_in, assert_true, fail, load_json, load_yaml
except ImportError:
    from scripts.generate_protocol_files import generate_host_protocol_table
    from scripts.lib.cheatsheet import (
        CorneGeometry,
        SofleGeometry,
        build_cheatsheet_model,
        load_presentation_aliases,
    )
    from scripts.lib.cheatsheet_svg import render_cheatsheet_svg
    from scripts.lib.keymap_parser import parse_keymap_file
    from scripts.lib.protocol import ProtocolManifest, load_protocol
    from scripts.lib.validation import assert_eq, assert_in, assert_true, fail, load_json, load_yaml
import hashlib
import xml.etree.ElementTree as ET

DOCS_HOST_PROTOCOL_PATH = REPO_ROOT / "docs" / "host-protocol.md"
CORNE_KEYMAP_PATH = REPO_ROOT / "config" / "corne.keymap"
SOFLE_KEYMAP_PATH = REPO_ROOT / "config" / "sofle.keymap"
KARABINER_PATH = REPO_ROOT / "hosts" / "macos" / "karabiner.json"
GLAZEWM_PATH = REPO_ROOT / "hosts" / "windows" / "glazewm.yaml"
AHK_PATH = REPO_ROOT / "hosts" / "windows" / "keyboard.ahk"
KEYMAP_DRAWER_CONFIG_PATH = REPO_ROOT / "keymap_drawer.config.yaml"
CORNE_CHEATSHEET_CONFIG_PATH = REPO_ROOT / "cheatsheets" / "corne.yaml"
SOFLE_CHEATSHEET_CONFIG_PATH = REPO_ROOT / "cheatsheets" / "sofle.yaml"
DOCS_GENERATED_DIR = REPO_ROOT / "docs" / "generated"

def test_documentation_freshness(manifest: ProtocolManifest) -> None:
    """Verify that docs/host-protocol.md contains the exact generated protocol table."""
    content = DOCS_HOST_PROTOCOL_PATH.read_text(encoding="utf-8")
    expected_table = generate_host_protocol_table(manifest)
    if expected_table not in content:
        fail(
            "docs/host-protocol.md table is stale! "
            "Run 'uv run scripts/generate_protocol_files.py' to synchronize with protocol/semantic-v1.yaml"
        )
    print("PASS: docs/host-protocol.md is up to date with protocol/semantic-v1.yaml.")


def test_undeclared_firmware_signals(manifest: ProtocolManifest) -> None:
    """Scan firmware keymaps for any F13-F24 signals not declared in protocol."""
    declared_zmk_signals = manifest.all_zmk_signals()

    # Pattern matching any F13-F24 keycodes in ZMK DTS
    fkey_pattern = re.compile(r"&kp\s+(?:[A-Z_]+\()*F(?:1[3-9]|2[0-4])\)*")

    for path, name in [(CORNE_KEYMAP_PATH, "Corne"), (SOFLE_KEYMAP_PATH, "Sofle")]:
        cfg = parse_keymap_file(path, layout=name.lower())
        for l_name, layer in cfg.layers.items():
            for b in layer.bindings:
                for match in fkey_pattern.findall(b):
                    assert_in(
                        match,
                        declared_zmk_signals,
                        f"{name} layer '{l_name}' emits undeclared protocol signal '{match}'",
                    )

    print("PASS: No undeclared protocol signals found in Corne or Sofle firmware keymaps.")


def test_undeclared_host_aliases(manifest: ProtocolManifest) -> None:
    """Verify that host configurations do not bind undeclared F13-F24 keys or aliases."""
    declared_keys = {a.signal.key.lower() for a in manifest.actions.values()}

    # Check GlazeWM keybindings
    glazewm_data = load_yaml(GLAZEWM_PATH)
    fkey_token_pattern = re.compile(r"\bf(?:1[3-9]|2[0-4])\b", re.IGNORECASE)

    all_glaze_bindings = []
    for entry in glazewm_data.get("keybindings", []):
        all_glaze_bindings.extend(entry.get("bindings", []))
    for mode in glazewm_data.get("binding_modes", []):
        for entry in mode.get("keybindings", []):
            all_glaze_bindings.extend(entry.get("bindings", []))

    for b in all_glaze_bindings:
        for match in fkey_token_pattern.findall(b):
            assert_in(
                match.lower(),
                declared_keys,
                f"GlazeWM contains undeclared F-key binding '{b}' ({match})",
            )

    print("PASS: No undeclared protocol signals found in host configurations.")


def test_display_alias_protocol_coverage(manifest: ProtocolManifest) -> None:
    """Verify that all F13-F24 protocol actions have exact display aliases in keymap_drawer.config.yaml."""
    aliases = load_presentation_aliases(KEYMAP_DRAWER_CONFIG_PATH)
    declared_zmk_signals = {a.signal.to_zmk(): a_id for a_id, a in manifest.actions.items()}

    for zmk_signal, action_id in declared_zmk_signals.items():
        assert_in(
            zmk_signal,
            aliases,
            f"Protocol action '{action_id}' ({zmk_signal}) is missing a display alias in keymap_drawer.config.yaml",
        )

    # Check that no undeclared F13-F24 aliases exist in keymap_drawer.config.yaml
    for alias_raw in aliases.keys():
        if re.search(r"F(?:1[3-9]|2[0-4])", alias_raw):
            assert_in(
                alias_raw,
                declared_zmk_signals,
                f"keymap_drawer.config.yaml contains display alias for undeclared protocol signal '{alias_raw}'",
            )

    print("PASS: Protocol signals and presentation aliases (keymap_drawer.config.yaml) are 100% synchronized.")

def test_consumer_hid_display_alias_coverage() -> None:
    """Verify that all Consumer HID actions (&kp C_*) appearing in keymaps have display aliases in keymap_drawer.config.yaml."""
    aliases = load_presentation_aliases(KEYMAP_DRAWER_CONFIG_PATH)
    corne_cfg = parse_keymap_file(CORNE_KEYMAP_PATH, layout="corne")
    sofle_cfg = parse_keymap_file(SOFLE_KEYMAP_PATH, layout="sofle")

    for kb_name, cfg in [("Corne", corne_cfg), ("Sofle", sofle_cfg)]:
        for layer_name, layer_obj in cfg.layers.items():
            for binding in layer_obj.bindings:
                if binding.startswith("&kp C_"):
                    assert_in(
                        binding,
                        aliases,
                        f"{kb_name} layer '{layer_name}' binding '{binding}' is missing a display alias in keymap_drawer.config.yaml",
                    )

    print("PASS: All Consumer HID bindings (&kp C_*) in firmware keymaps have display aliases in keymap_drawer.config.yaml.")



def test_cheatsheet_svg_freshness(keyboard: str = "corne") -> None:
    """Verify that the committed cheatsheet SVG is identical to in-memory regenerated SVG."""
    kb = keyboard.lower()
    svg_path = DOCS_GENERATED_DIR / f"{kb}-cheatsheet.svg"
    if not svg_path.exists():
        fail(f"Cheatsheet SVG missing: {svg_path}. Run 'uv run scripts/generate_cheatsheet.py {kb}'")

    keymap_path = SOFLE_KEYMAP_PATH if kb == "sofle" else CORNE_KEYMAP_PATH
    cheatsheet_cfg = SOFLE_CHEATSHEET_CONFIG_PATH if kb == "sofle" else CORNE_CHEATSHEET_CONFIG_PATH

    model = build_cheatsheet_model(
        keyboard=kb,
        keymap_path=keymap_path,
        cheatsheet_config_path=cheatsheet_cfg,
        aliases_path=KEYMAP_DRAWER_CONFIG_PATH,
    )
    expected_svg = render_cheatsheet_svg(model)
    actual_svg = svg_path.read_text(encoding="utf-8")

    if actual_svg != expected_svg:
        fail(
            f"{svg_path.name} is stale! "
            f"Run 'uv run scripts/generate_cheatsheet.py {kb}' to synchronize documentation."
        )
    print(f"PASS: {svg_path.name} is up to date with firmware keymap and protocol.")


def test_cheatsheet_manifest(keyboard: str = "corne") -> None:
    """Verify that the generated manifest SHA256 hashes match current inputs and output artifacts."""
    kb = keyboard.lower()
    manifest_path = DOCS_GENERATED_DIR / f"{kb}-cheatsheet.manifest.json"
    if not manifest_path.exists():
        fail(f"Cheatsheet manifest missing: {manifest_path}. Run 'uv run scripts/generate_cheatsheet.py {kb}'")

    data = load_json(manifest_path)

    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    keymap_path = SOFLE_KEYMAP_PATH if kb == "sofle" else CORNE_KEYMAP_PATH
    cheatsheet_cfg = SOFLE_CHEATSHEET_CONFIG_PATH if kb == "sofle" else CORNE_CHEATSHEET_CONFIG_PATH

    assert_eq(data.get("schema"), 1, f"Cheatsheet manifest schema version mismatch for {kb}")
    assert_eq(data.get("keyboard"), kb, f"Cheatsheet manifest keyboard mismatch for {kb}")
    assert_eq(data.get("keymap_sha256"), sha(keymap_path), f"Manifest keymap_sha256 mismatch for {kb}")
    assert_eq(data.get("protocol_sha256"), sha(REPO_ROOT / "protocol" / "semantic-v1.yaml"), f"Manifest protocol_sha256 mismatch for {kb}")
    assert_eq(data.get("presentation_sha256"), sha(cheatsheet_cfg), f"Manifest presentation_sha256 mismatch for {kb}")
    assert_eq(data.get("aliases_sha256"), sha(KEYMAP_DRAWER_CONFIG_PATH), f"Manifest aliases_sha256 mismatch for {kb}")

    svg_path = DOCS_GENERATED_DIR / f"{kb}-cheatsheet.svg"
    assert_eq(data.get("svg_sha256"), sha(svg_path), f"Manifest svg_sha256 mismatch for {kb}")

    pdf_path = DOCS_GENERATED_DIR / f"{kb}-cheatsheet.pdf"
    if pdf_path.exists() and data.get("pdf_sha256"):
        assert_eq(data.get("pdf_sha256"), sha(pdf_path), f"Manifest pdf_sha256 mismatch for {kb}")

    print(f"PASS: {manifest_path.name} verified against all input and artifact SHAs.")


def test_cheatsheet_structure(keyboard: str = "corne") -> None:
    """Verify exact structural and semantic invariants of the generated SVG."""
    kb = keyboard.lower()
    svg_path = DOCS_GENERATED_DIR / f"{kb}-cheatsheet.svg"
    content = svg_path.read_text(encoding="utf-8")
    root = ET.fromstring(content)
    ns = {"svg": "http://www.w3.org/2000/svg"}

    # 1. Dimensions & Canvas
    assert_eq(root.attrib.get("viewBox"), "0 0 2970 2100", f"{kb} SVG viewBox must be A4 landscape (2970x2100)")
    assert_eq(root.attrib.get("width"), "297mm", f"{kb} SVG width must be 297mm")
    assert_eq(root.attrib.get("height"), "210mm", f"{kb} SVG height must be 210mm")

    # 2. Panel counts (12 total panels)
    layer_panels = [elem for elem in root.findall(".//svg:g", ns) if elem.attrib.get("id", "").startswith("layer-")]
    assert_eq(len(layer_panels), 12, f"{kb} Cheatsheet must have exactly 12 panels (layers + notes)")

    if kb == "sofle":
        expected_layers = [
            "BASE", "NAV", "MOUSE", "MEDIA", "NUM", "SYM", "FUN", "HOST", "GAME", "ADJUST"
        ]
        expected_positions = set(SofleGeometry.ORDERED_POSITIONS)
        keys_per_layer = 60
    else:
        expected_layers = [
            "BASE", "NAV", "MOUSE", "MEDIA", "NUM", "SYM", "FUN", "HOST", "GAME", "ADJUST", "GAME_FN"
        ]
        expected_positions = set(CorneGeometry.ORDERED_POSITIONS)
        keys_per_layer = 42

    assert_eq(len(expected_positions), keys_per_layer, f"{kb} must have exactly {keys_per_layer} positions")

    raw_pattern = re.compile(r"&(?:kp|mo|lt|to|trans|none|sk|hml|hmr)\b")

    for layer_name in expected_layers:
        panel_id = f"layer-{layer_name.lower()}"
        panel_elem = root.find(f".//svg:g[@id='{panel_id}']", ns)
        assert_true(panel_elem is not None, f"Panel '{panel_id}' missing in {kb} SVG")
        assert_eq(panel_elem.attrib.get("data-layer"), layer_name, f"Panel '{panel_id}' data-layer mismatch")

        # Check keys count
        keys = panel_elem.findall(".//svg:g[@data-position]", ns)
        assert_eq(len(keys), keys_per_layer, f"Layer '{layer_name}' in {kb} must contain {keys_per_layer} keys, found {len(keys)}")

        positions = [k.attrib.get("data-position") for k in keys]
        assert_eq(len(set(positions)), keys_per_layer, f"Layer '{layer_name}' contains duplicate positions")
        assert_eq(set(positions), expected_positions, f"Layer '{layer_name}' positions do not match {kb} geometry")

        # Verify no raw ZMK binding text leaked into visible text
        for text_elem in panel_elem.findall(".//svg:text", ns):
            if text_elem.text:
                assert_true(
                    not raw_pattern.search(text_elem.text),
                    f"Layer '{layer_name}' leaked raw ZMK syntax in text: '{text_elem.text}'",
                )

    # 3. Transition Invariants
    base_panel = root.find(".//svg:g[@id='layer-base']", ns)
    base_transitions = base_panel.findall(".//svg:g[@data-target-layer]", ns)
    assert_eq(len(base_transitions), 7, f"BASE layer must have exactly 7 layer transitions, found {len(base_transitions)}")

    adjust_panel = root.find(".//svg:g[@id='layer-adjust']", ns)
    adjust_transitions = adjust_panel.findall(".//svg:g[@data-target-layer]", ns)
    assert_eq(len(adjust_transitions), 1, f"ADJUST layer must have exactly 1 layer transition (GAME), found {len(adjust_transitions)}")
    assert_eq(adjust_transitions[0].attrib.get("data-target-layer"), "GAME", "ADJUST transition must target GAME")

    if kb == "sofle":
        game_panel = root.find(".//svg:g[@id='layer-game']", ns)
        game_transitions = game_panel.findall(".//svg:g[@data-target-layer]", ns)
        assert_eq(len(game_transitions), 1, f"GAME layer in Sofle must have exactly 1 BASE transition on REC, found {len(game_transitions)}")
        assert_eq(game_transitions[0].attrib.get("data-target-layer"), "BASE", "GAME transition must target BASE")
        assert_eq(game_transitions[0].attrib.get("data-position"), "REC", "GAME exit must be on REC")
    else:
        game_panel = root.find(".//svg:g[@id='layer-game']", ns)
        game_transitions = game_panel.findall(".//svg:g[@data-target-layer]", ns)
        assert_eq(len(game_transitions), 2, f"GAME layer in Corne must have exactly 2 GAME_FN transitions, found {len(game_transitions)}")
        for gt in game_transitions:
            assert_eq(gt.attrib.get("data-target-layer"), "GAME_FN", "GAME transitions must target GAME_FN")

        game_fn_panel = root.find(".//svg:g[@id='layer-game_fn']", ns)
        game_fn_transitions = game_fn_panel.findall(".//svg:g[@data-target-layer]", ns)
        assert_eq(len(game_fn_transitions), 1, f"GAME_FN layer must have exactly 1 BASE transition, found {len(game_fn_transitions)}")
        assert_eq(game_fn_transitions[0].attrib.get("data-target-layer"), "BASE", "GAME_FN transition must target BASE")

    # Verify Bootloaders are NOT transitions
    for panel_id in ["layer-nav", "layer-num", "layer-adjust"]:
        panel = root.find(f".//svg:g[@id='{panel_id}']", ns)
        boot_keys = panel.findall(".//svg:g[@data-binding='&bootloader']", ns)
        for bk in boot_keys:
            assert_true(
                "data-target-layer" not in bk.attrib,
                f"&bootloader in {panel_id} must not be marked as a layer transition",
            )

    # Notes panel
    notes_panel = root.find(".//svg:g[@id='layer-notes']", ns)
    assert_true(notes_panel is not None, f"Notes panel missing in {kb} SVG")

    print(f"PASS: {kb.capitalize()} Cheatsheet SVG structure, dimensions, and transition invariants verified.")


def main() -> None:
    print("=" * 70)
    print("RUNNING GENERATED ARTIFACT & PROTOCOL FRESHNESS CHECKS")
    print("=" * 70)
    manifest = load_protocol()
    test_documentation_freshness(manifest)
    test_undeclared_firmware_signals(manifest)
    test_undeclared_host_aliases(manifest)
    test_display_alias_protocol_coverage(manifest)
    test_consumer_hid_display_alias_coverage()
    for kb in ["corne", "sofle"]:
        test_cheatsheet_svg_freshness(kb)
        test_cheatsheet_manifest(kb)
        test_cheatsheet_structure(kb)
    print("=" * 70)
    print("ALL GENERATED ARTIFACT & PROTOCOL CHECKS PASSED.")
    print("=" * 70)

if __name__ == "__main__":
    main()
