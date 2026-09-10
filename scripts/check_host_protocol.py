#!/usr/bin/env python3
"""
End-to-end structural validation for the multi-keyboard semantic host protocol.

Validates the full architecture:
  Producers:
    - Corne firmware (config/corne.keymap)
    - Sofle firmware (config/sofle.keymap)
  macOS Host:
    - Karabiner-Elements external adapter (hosts/macos/karabiner/external-semantic.json)
    - Karabiner-Elements laptop adapter (hosts/macos/karabiner/laptop-omniwm.json)
    - OmniWM window manager & native Quake terminal (hosts/macos/omniwm/settings.toml)
  Windows Consumers:
    - AutoHotkey v2 bridge (hosts/windows/keyboard.ahk)
    - GlazeWM window manager (hosts/windows/glazewm.yaml)

Enforces that every emitted firmware signal has a corresponding host translation on both OSes.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

# Robust path configuration for local and package execution
SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from lib.keymap_parser import parse_keymap_file
    from lib.protocol import ProtocolManifest, SemanticSignal, load_protocol
    from lib.validation import assert_eq, assert_in, assert_true, fail, load_json, load_toml, load_yaml
except ImportError:
    from scripts.lib.keymap_parser import parse_keymap_file
    from scripts.lib.protocol import ProtocolManifest, SemanticSignal, load_protocol
    from scripts.lib.validation import assert_eq, assert_in, assert_true, fail, load_json, load_toml, load_yaml
CORNE_KEYMAP_PATH = REPO_ROOT / "config" / "corne.keymap"
SOFLE_KEYMAP_PATH = REPO_ROOT / "config" / "sofle.keymap"
KARABINER_EXTERNAL_PATH = REPO_ROOT / "hosts" / "macos" / "karabiner" / "external-semantic.json"
KARABINER_LAPTOP_PATH = REPO_ROOT / "hosts" / "macos" / "karabiner" / "laptop-omniwm.json"
OMNIWM_PATH = REPO_ROOT / "hosts" / "macos" / "omniwm" / "settings.toml"
AHK_PATH = REPO_ROOT / "hosts" / "windows" / "keyboard.ahk"
GLAZEWM_PATH = REPO_ROOT / "hosts" / "windows" / "glazewm.yaml"

# -----------------------------------------------------------------------------
# Layer A: Firmware Protocol Producers (Corne & Sofle)
# -----------------------------------------------------------------------------

EXPECTED_HOST_SIGNALS = [
    # Workspaces 1-5 (WEB, DEV, COMMS, RUN, AUX)
    "&kp F13", "&kp F14", "&kp F15", "&kp F16", "&kp F17",
    # Move window to workspace 1-5 + follow
    "&kp LS(F13)", "&kp LS(F14)", "&kp LS(F15)", "&kp LS(F16)", "&kp LS(F17)",
    # Directional focus (Left, Down, Up, Right)
    "&kp LC(F13)", "&kp LC(F14)", "&kp LC(F15)", "&kp LC(F16)",
    # Directional move (Left, Down, Up, Right)
    "&kp LC(LS(F13))", "&kp LC(LS(F14))", "&kp LC(LS(F15))", "&kp LC(LS(F16))",
    # Context & modes
    "&kp LS(F18)",  # Resize mode / cycle size
    "&kp F18",      # Previous workspace
    "&kp F19",      # Fullscreen
    "&kp F20",      # Float / tile
    # Extended semantic protocol
    "&kp LA(F13)",  # SYSTEM_LAUNCHER (Spotlight / Windows Search)
    "&kp LA(F14)",  # QUICK_TERMINAL (Ghostty scratchpad / Quake)
    "&kp LA(F15)",  # NEW_TERMINAL (Ghostty / Windows Terminal)
    "&kp LA(F16)",  # PREVIOUS_WINDOW (OmniWM focus previous / Alt+Tab)
    "&kp LA(F17)",  # LANGUAGE_TOGGLE (Input Source / EVKey)
    "&kp LA(F18)",  # OVERVIEW / SERVICE_MODE (OmniWM Overview / GlazeWM service)
]

EXPECTED_EDITING_SIGNALS = [
    "&kp F21",                  # Copy
    "&kp F22",                  # Paste
    "&kp F23",                  # Cut
    "&kp F24",                  # Undo
    "&kp LC(LA(LS(LG(F24))))",  # Redo
]

EXPECTED_APP_SIGNALS = [
    "&kp LC(LA(LS(LG(F13))))",  # Select All
    "&kp LC(LA(LS(LG(F14))))",  # Save
    "&kp LC(LA(LS(LG(F15))))",  # Find
    "&kp LC(LA(LS(LG(F16))))",  # Previous Tab
    "&kp LC(LA(LS(LG(F17))))",  # Next Tab
    "&kp LC(LA(LS(LG(F18))))",  # New Tab
    "&kp LC(LA(LS(LG(F19))))",  # Close Tab
    "&kp LC(LA(LS(LG(F20))))",  # Reopen Tab
    "&kp LC(LA(LS(LG(F21))))",  # Word Left
    "&kp LC(LA(LS(LG(F22))))",  # Word Right
    "&kp LC(LA(LS(LG(F23))))",  # Find Next
    "&kp LC(LA(LS(LG(F24))))",  # Redo
]


def validate_keymap_producer(path: Path, board_name: str) -> None:
    """Verify that all expected semantic signals exist on the HOST and NAV/MOUSE layers."""
    cfg = parse_keymap_file(path, layout=board_name.lower())
    assert_in("HOST", cfg.layers, f"{board_name}: Missing HOST layer")
    assert_in("NAV", cfg.layers, f"{board_name}: Missing NAV layer")
    assert_in("MOUSE", cfg.layers, f"{board_name}: Missing MOUSE layer")

    host_bindings = set(cfg.layer("HOST").bindings)
    for signal in EXPECTED_HOST_SIGNALS:
        assert_in(signal, host_bindings, f"{board_name}: Missing signal '{signal}' in HOST layer")

    nav_bindings = set(cfg.layer("NAV").bindings)
    mouse_bindings = set(cfg.layer("MOUSE").bindings)
    for sig in EXPECTED_EDITING_SIGNALS:
        assert_in(sig, nav_bindings, f"{board_name}: Missing editing signal '{sig}' in NAV layer")
        assert_in(sig, mouse_bindings, f"{board_name}: Missing editing signal '{sig}' in MOUSE layer")

    for sig in EXPECTED_APP_SIGNALS:
        assert_in(sig, nav_bindings, f"{board_name}: Missing application signal '{sig}' in NAV layer")

    print(
        f"PASS: Firmware Producer ({board_name}) validated "
        f"({len(EXPECTED_HOST_SIGNALS)} HOST signals + {len(EXPECTED_EDITING_SIGNALS)} editing signals + {len(EXPECTED_APP_SIGNALS)} app signals)."
    )

# -----------------------------------------------------------------------------
# Layer B: macOS Host (Karabiner & OmniWM)
# -----------------------------------------------------------------------------

def validate_karabiner_external(karabiner_data: dict) -> None:
    """Verify that Karabiner external adapter maps application/editing/launcher signals and standard F1-F12 normalization,
    and CRITICALLY does NOT intercept raw window management or Quake signals intended directly for OmniWM."""
    rules = karabiner_data.get("rules", [])
    if len(rules) < 3:
        fail("Layer B (Karabiner External): Expected at least 3 rules in external-semantic.json")

    all_manipulators = []
    for r in rules:
        for m in r.get("manipulators", []):
            all_manipulators.append(m)

    semantic_launcher_manipulators = []
    semantic_app_manipulators = []
    semantic_editing_manipulators = []
    standard_f_manipulators = []
    unexpected_manipulators = []

    for m in all_manipulators:
        key_code = m.get("from", {}).get("key_code", "")
        mandatory_mods = set(m.get("from", {}).get("modifiers", {}).get("mandatory", []))
        is_hyper = mandatory_mods == {"control", "option", "shift", "command"}

        if is_hyper and key_code in [f"f{i}" for i in range(13, 25)]:
            semantic_app_manipulators.append(m)
        elif mandatory_mods == {"option"} and key_code in ["f13", "f15", "f17"]:
            semantic_launcher_manipulators.append(m)
        elif key_code in [f"f{i}" for i in range(21, 25)]:
            semantic_editing_manipulators.append(m)
        elif key_code in [f"f{i}" for i in range(1, 13)]:
            standard_f_manipulators.append(m)
        else:
            unexpected_manipulators.append(m)

    assert_eq(
        len(unexpected_manipulators),
        0,
        f"Layer B (Karabiner External): Found unexpected manipulators: {unexpected_manipulators}",
    )
    assert_eq(
        len(semantic_launcher_manipulators),
        3,
        f"Layer B (Karabiner External): Expected exactly 3 desktop launcher manipulators (Alt+F13, F15, F17), found {len(semantic_launcher_manipulators)}",
    )
    assert_eq(
        len(semantic_app_manipulators),
        12,
        f"Layer B (Karabiner External): Expected exactly 12 Hyper application manipulators, found {len(semantic_app_manipulators)}",
    )
    assert_eq(
        len(semantic_editing_manipulators),
        8,
        f"Layer B (Karabiner External): Expected exactly 8 editing manipulators (4 Shift-safe + 4 bare), found {len(semantic_editing_manipulators)}",
    )
    assert_eq(
        len(standard_f_manipulators),
        12,
        f"Layer B (Karabiner External): Expected exactly 12 standard F-key normalizers, found {len(standard_f_manipulators)}",
    )
    assert_eq(
        len(all_manipulators),
        35,
        f"Layer B (Karabiner External): Expected exactly 35 canonical manipulators (3 launcher + 12 Hyper app + 8 editing + 12 standard F), found {len(all_manipulators)}",
    )

    # CRITICAL INVARIANT: Karabiner external adapter must NOT intercept OmniWM signals!
    disallowed_karabiner_signals = [
        # Raw workspace switching (F13-F17)
        ("f13", set()), ("f14", set()), ("f15", set()), ("f16", set()), ("f17", set()),
        # Move to workspace (Shift + F13-F17)
        ("f13", {"shift"}), ("f14", {"shift"}), ("f15", {"shift"}), ("f16", {"shift"}), ("f17", {"shift"}),
        # Directional focus (Ctrl + F13-F16)
        ("f13", {"control"}), ("f14", {"control"}), ("f15", {"control"}), ("f16", {"control"}),
        # Directional move (Ctrl + Shift + F13-F16)
        ("f13", {"control", "shift"}), ("f14", {"control", "shift"}), ("f15", {"control", "shift"}), ("f16", {"control", "shift"}),
        # Context & mode controls
        ("f18", set()),                    # Previous workspace
        ("f18", {"shift"}),                # Cycle size forward
        ("f18", {"option"}),               # Overview (Alt+F18)
        ("f19", set()),                    # Fullscreen
        ("f20", set()),                    # Float
        ("f16", {"option"}),               # Previous window (Alt+F16)
        ("f14", {"option"}),               # Quake Terminal (Alt+F14) -> Native OmniWM!
    ]
    for k_dis, m_dis in disallowed_karabiner_signals:
        for m in all_manipulators:
            m_from = m.get("from", {})
            if m_from.get("key_code") == k_dis and set(m_from.get("modifiers", {}).get("mandatory", [])) == m_dis:
                fail(f"Layer B (Karabiner External): Karabiner must NOT intercept OmniWM signal ({k_dis}, {m_dis})")

    # Verify Alt+F15 uses Ghostty automation shell command
    f15_manips = [m for m in semantic_launcher_manipulators if m.get("from", {}).get("key_code") == "f15"]
    assert_eq(len(f15_manips), 1, "Layer B (Karabiner External): Expected exactly 1 Alt+F15 manipulator")
    to_f15 = f15_manips[0].get("to", [])
    assert_true(len(to_f15) == 1 and "shell_command" in to_f15[0], "Layer B (Karabiner External): Alt+F15 must use shell_command")
    shell_cmd = to_f15[0]["shell_command"]
    assert_true("Ghostty" in shell_cmd and "new window" in shell_cmd, "Layer B (Karabiner External): Alt+F15 shell_command must trigger Ghostty new window")

    # Verify Shift-safe editing handlers appear before bare editing handlers
    shift_safe_keys = []
    bare_keys = []
    for m in semantic_editing_manipulators:
        k = m.get("from", {}).get("key_code")
        mods = m.get("from", {}).get("modifiers", {})
        mand = mods.get("mandatory", [])
        opt = mods.get("optional", [])
        assert_eq(opt, ["caps_lock"], f"Layer B (Karabiner External): Editing manipulator for {k} must have optional: [caps_lock]")
        if mand == ["shift"]:
            shift_safe_keys.append(k)
        elif not mand:
            bare_keys.append(k)
        else:
            fail(f"Layer B (Karabiner External): Unexpected mandatory modifiers {mand} on editing manipulator {k}")

    assert_eq(shift_safe_keys, ["f21", "f22", "f23", "f24"], "Layer B (Karabiner External): Expected 4 Shift-safe editing handlers in order")
    assert_eq(bare_keys, ["f21", "f22", "f23", "f24"], "Layer B (Karabiner External): Expected 4 bare editing handlers in order")

    for idx, m in enumerate(all_manipulators):
        conditions = m.get("conditions", [])
        has_device_if = False
        for c in conditions:
            if c.get("type") == "device_if":
                identifiers = c.get("identifiers", [])
                for ident in identifiers:
                    if ident.get("is_built_in_keyboard") is False or "vendor_id" in ident:
                        has_device_if = True
        if not has_device_if:
            fail(
                f"Layer B (Karabiner External): Manipulator #{idx} ({m.get('from')}) "
                f"must be scoped with device_if excluding built-in keyboard (is_built_in_keyboard: false)"
            )

    # Validate Standard F1-F12 normalization group
    for i in range(1, 13):
        f_key = f"f{i}"
        matching = [m for m in standard_f_manipulators if m.get("from", {}).get("key_code") == f_key]
        assert_eq(
            len(matching),
            1,
            f"Layer B (Karabiner External): Expected exactly 1 normalizer for {f_key}, found {len(matching)}",
        )
        norm_m = matching[0]

        # from.modifiers.optional must contain "any"
        optional_mods = norm_m.get("from", {}).get("modifiers", {}).get("optional", [])
        assert_in(
            "any",
            optional_mods,
            f"Layer B (Karabiner External): {f_key} from.modifiers.optional must contain any to preserve opposite-hand mods",
        )

        # to must map to same f-key with "fn" modifier
        to_list = norm_m.get("to", [])
        assert_true(
            len(to_list) == 1 and to_list[0].get("key_code") == f_key and set(to_list[0].get("modifiers", [])) == {"fn"},
            f"Layer B (Karabiner External): {f_key} must map to {f_key} with modifiers [fn]",
        )

        # conditions must evaluate system.use_fkeys_as_standard_function_keys == false
        conditions = norm_m.get("conditions", [])
        has_sys_fkey_cond = False
        for c in conditions:
            if (
                c.get("type") == "variable_if"
                and c.get("name") == "system.use_fkeys_as_standard_function_keys"
                and c.get("value") == 0
            ):
                has_sys_fkey_cond = True
        assert_true(
            has_sys_fkey_cond,
            f"Layer B (Karabiner External): {f_key} normalizer missing system.use_fkeys_as_standard_function_keys variable_if condition",
        )

    expected_translations: List[Tuple[str, Set[str], str, Set[str]]] = [
        # Desktop launchers & controls (Alt+F15 handled via AppleScript shell_command above)
        ("f13", {"option"}, "spacebar", {"left_command"}),               # LAUNCHER -> Cmd+Space
        ("f17", {"option"}, "spacebar", {"left_control"}),               # LANG -> Ctrl+Space
        # Semantic editing (4 Shift-safe variants + 4 bare variants)
        ("f21", {"shift"}, "c", {"left_command"}),
        ("f22", {"shift"}, "v", {"left_command"}),
        ("f23", {"shift"}, "x", {"left_command"}),
        ("f24", {"shift"}, "z", {"left_command"}),
        ("f21", set(), "c", {"left_command"}),
        ("f22", set(), "v", {"left_command"}),
        ("f23", set(), "x", {"left_command"}),
        ("f24", set(), "z", {"left_command"}),
        # Hyper application actions (12)
        ("f13", {"control", "option", "shift", "command"}, "a", {"left_command"}),
        ("f14", {"control", "option", "shift", "command"}, "s", {"left_command"}),
        ("f15", {"control", "option", "shift", "command"}, "f", {"left_command"}),
        ("f16", {"control", "option", "shift", "command"}, "open_bracket", {"left_command", "left_shift"}),
        ("f17", {"control", "option", "shift", "command"}, "close_bracket", {"left_command", "left_shift"}),
        ("f18", {"control", "option", "shift", "command"}, "t", {"left_command"}),
        ("f19", {"control", "option", "shift", "command"}, "w", {"left_command"}),
        ("f20", {"control", "option", "shift", "command"}, "t", {"left_command", "left_shift"}),
        ("f21", {"control", "option", "shift", "command"}, "left_arrow", {"left_alt"}),
        ("f22", {"control", "option", "shift", "command"}, "right_arrow", {"left_alt"}),
        ("f23", {"control", "option", "shift", "command"}, "g", {"left_command"}),
        ("f24", {"control", "option", "shift", "command"}, "z", {"left_command", "left_shift"}),
    ]
    for from_key, from_mods, to_key, to_mods in expected_translations:
        found = False
        for m in all_manipulators:
            m_from = m.get("from", {})
            m_key = m_from.get("key_code")
            m_mods = set(m_from.get("modifiers", {}).get("mandatory", []))

            if m_key == from_key and m_mods == from_mods:
                to_list = m.get("to", [])
                if to_list:
                    t = to_list[0]
                    t_key = t.get("key_code")
                    t_mods = set(t.get("modifiers", []))
                    if t_key == to_key and t_mods == to_mods:
                        found = True
                        break
        if not found:
            fail(
                f"Layer B (Karabiner External): Missing translation for from=({from_key}, mods={from_mods}) "
                f"-> to=({to_key}, mods={to_mods})"
            )

    print(
        f"PASS: macOS Karabiner External Adapter validated ({len(expected_translations) + 1} semantic mappings + {len(standard_f_manipulators)} standard F-key normalizers with device_if scoping; no raw WM or Quake signals intercepted)."
    )


def validate_karabiner_laptop(karabiner_data: dict) -> None:
    """Verify that the MacBook built-in keyboard adapter maps conventional chords to semantic F13-F20 signals,
    strictly scoped to is_built_in_keyboard=true, preserving the semantic HID protocol without invoking shell commands."""
    rules = karabiner_data.get("rules", [])
    assert_true(len(rules) >= 1, "Layer B (Karabiner Laptop): Expected at least 1 rule in laptop-omniwm.json")

    all_manipulators = [m for r in rules for m in r.get("manipulators", [])]
    assert_eq(len(all_manipulators), 25, f"Layer B (Karabiner Laptop): Expected exactly 25 manipulators, found {len(all_manipulators)}")

    # Every manipulator must be scoped to is_built_in_keyboard: true
    for idx, m in enumerate(all_manipulators):
        conditions = m.get("conditions", [])
        has_builtin_scope = False
        for c in conditions:
            if c.get("type") == "device_if":
                identifiers = c.get("identifiers", [])
                for ident in identifiers:
                    if ident.get("is_built_in_keyboard") is True:
                        has_builtin_scope = True
        assert_true(has_builtin_scope, f"Layer B (Karabiner Laptop): Manipulator #{idx} missing is_built_in_keyboard: true scoping")

        to_list = m.get("to", [])
        assert_true(len(to_list) == 1, f"Layer B (Karabiner Laptop): Manipulator #{idx} must have exactly 1 'to' action")
        to_act = to_list[0]
        assert_true("shell_command" not in to_act, f"Layer B (Karabiner Laptop): Manipulator #{idx} must map to semantic signal, not shell_command")
        to_key = to_act.get("key_code", "")
        assert_true(to_key in [f"f{i}" for i in range(13, 21)], f"Layer B (Karabiner Laptop): Manipulator #{idx} maps to non-semantic key '{to_key}'")

    # Required mappings: (from_key, from_mandatory_mods, to_key, to_mods)
    expected_laptop_mappings = [
        # ⌥⇧1…5 -> Shift+F13…F17
        ("1", {"option", "shift"}, "f13", {"left_shift"}),
        ("2", {"option", "shift"}, "f14", {"left_shift"}),
        ("3", {"option", "shift"}, "f15", {"left_shift"}),
        ("4", {"option", "shift"}, "f16", {"left_shift"}),
        ("5", {"option", "shift"}, "f17", {"left_shift"}),
        # ⌥1…5 -> F13…F17
        ("1", {"option"}, "f13", set()),
        ("2", {"option"}, "f14", set()),
        ("3", {"option"}, "f15", set()),
        ("4", {"option"}, "f16", set()),
        ("5", {"option"}, "f17", set()),
        # ⌥⇧H/J/K/L -> Ctrl+Shift+F13..F16
        ("h", {"option", "shift"}, "f13", {"left_control", "left_shift"}),
        ("j", {"option", "shift"}, "f14", {"left_control", "left_shift"}),
        ("k", {"option", "shift"}, "f15", {"left_control", "left_shift"}),
        ("l", {"option", "shift"}, "f16", {"left_control", "left_shift"}),
        # ⌥H/J/K/L -> Ctrl+F13..F16
        ("h", {"option"}, "f13", {"left_control"}),
        ("j", {"option"}, "f14", {"left_control"}),
        ("k", {"option"}, "f15", {"left_control"}),
        ("l", {"option"}, "f16", {"left_control"}),
        # ⌃⌥Tab -> F18
        ("tab", {"control", "option"}, "f18", set()),
        # ⌥Tab -> Option+F16
        ("tab", {"option"}, "f16", {"left_alt"}),
        # ⌥. -> Shift+F18
        ("period", {"option"}, "f18", {"left_shift"}),
        # ⌥⇧O -> Option+F18
        ("o", {"option", "shift"}, "f18", {"left_alt"}),
        # ⌥Return -> F19
        ("return_or_enter", {"option"}, "f19", set()),
        # ⌥⇧Space -> F20
        ("spacebar", {"option", "shift"}, "f20", set()),
        # ⌥` -> Option+F14
        ("grave_accent_and_tilde", {"option"}, "f14", {"left_alt"}),
    ]

    for from_key, from_mods, to_key, to_mods in expected_laptop_mappings:
        found = False
        for m in all_manipulators:
            m_from = m.get("from", {})
            m_key = m_from.get("key_code")
            m_mods = set(m_from.get("modifiers", {}).get("mandatory", []))
            if m_key == from_key and m_mods == from_mods:
                t = m.get("to", [])[0]
                t_key = t.get("key_code")
                t_mods = set(t.get("modifiers", []))
                if t_key == to_key and t_mods == to_mods:
                    found = True
                    break
        assert_true(found, f"Layer B (Karabiner Laptop): Missing mapping for {from_key} (mods={from_mods}) -> {to_key} (mods={to_mods})")

    print(f"PASS: macOS Karabiner Built-in Laptop Adapter validated ({len(expected_laptop_mappings)} semantic mappings scoped to is_built_in_keyboard=true).")


def validate_omniwm_consumer(data: dict) -> None:
    """Verify OmniWM settings consume all raw F13-F20 window management signals directly."""
    assert_eq(data.get("schemaVersion"), 3, "OmniWM: schemaVersion must be 3")

    general = data.get("general", {})
    assert_true(general.get("ipcEnabled") is True, "OmniWM: general.ipcEnabled must be true for CLI/IPC control")
    assert_eq(general.get("defaultLayoutType"), "niri", "OmniWM: general.defaultLayoutType must be niri")
    assert_true(general.get("hotkeysEnabled") is True, "OmniWM: general.hotkeysEnabled must be true")

    ws_bar = data.get("workspaceBar", {})
    assert_true(ws_bar.get("enabled") is True, "OmniWM: workspaceBar.enabled must be true")
    assert_eq(ws_bar.get("position"), "belowMenuBar", "OmniWM: workspaceBar.position must be belowMenuBar")
    assert_true(ws_bar.get("reserveLayoutSpace") is True, "OmniWM: workspaceBar.reserveLayoutSpace must be true")
    assert_eq(ws_bar.get("revealModifier"), "off", "OmniWM: workspaceBar.revealModifier must be off for persistent visibility")

    niri = data.get("niri", {})
    assert_true(niri.get("visibleContainerCount") in (1, 2, 3), "OmniWM: niri.visibleContainerCount must be between 1 and 3")
    assert_eq(niri.get("centerFocusedColumn"), "onOverflow", "OmniWM: niri.centerFocusedColumn must be onOverflow")
    assert_eq(niri.get("singleWindowFit"), "fill", "OmniWM: niri.singleWindowFit must be fill")
    assert_true(niri.get("infiniteLoop") is False, "OmniWM: niri.infiniteLoop must be false")

    presets = niri.get("containerPrimarySpanPresets", [])
    for expected_preset in [0.5, 1.0]:
        assert_true(any(abs(p - expected_preset) < 0.01 for p in presets), f"OmniWM: preset {expected_preset} missing in niri presets")

    # Validate 5 semantic workspaces
    workspaces = data.get("workspaces", [])
    ws_display_names = [w.get("displayName") for w in workspaces]
    assert_eq(ws_display_names, ["WEB", "DEV", "COMMS", "RUN", "AUX"], "OmniWM: Expected workspaces [WEB, DEV, COMMS, RUN, AUX]")

    # Validate hotkey bindings
    hotkeys = data.get("hotkeys", [])
    hk_map = {h.get("id"): h.get("binding") for h in hotkeys if isinstance(h, dict) and "id" in h}

    required_bindings = {
        # Workspaces 1-5 (F13-F17)
        "switchWorkspace.0": "F13",
        "switchWorkspace.1": "F14",
        "switchWorkspace.2": "F15",
        "switchWorkspace.3": "F16",
        "switchWorkspace.4": "F17",
        # Move to workspace 1-5 (Shift+F13..F17)
        "moveToWorkspace.0": "Shift+F13",
        "moveToWorkspace.1": "Shift+F14",
        "moveToWorkspace.2": "Shift+F15",
        "moveToWorkspace.3": "Shift+F16",
        "moveToWorkspace.4": "Shift+F17",
        # Directional focus (Ctrl+F13..F16)
        "focus.left": "Control+F13",
        "focus.down": "Control+F14",
        "focus.up": "Control+F15",
        "focus.right": "Control+F16",
        # Directional move (Ctrl+Shift+F13..F16)
        "move.left": "Control+Shift+F13",
        "move.down": "Control+Shift+F14",
        "move.up": "Control+Shift+F15",
        "move.right": "Control+Shift+F16",
        # Context & modes
        "workspaceBackAndForth": "F18",
        "cycleSizeForward": "Shift+F18",
        "toggleOverview": "Option+F18",
        "toggleFullscreen": "F19",
        "toggleFocusedWindowFloating": "F20",
        "focusPrevious": "Option+F16",
        "toggleQuakeTerminal": "Option+F14",
    }

    for hk_id, expected_binding in required_bindings.items():
        actual = hk_map.get(hk_id)
        assert_eq(actual, expected_binding, f"OmniWM: Hotkey {hk_id} expected binding {expected_binding}, got {actual}")

    quake_cfg = data.get("quakeTerminal", {})
    assert_true(quake_cfg.get("enabled") is True, "OmniWM: quakeTerminal.enabled must be true")

    # Verify no duplicate active bindings among hotkeys
    active_bindings = [h.get("binding") for h in hotkeys if h.get("binding") != "Unassigned"]
    dups = [b for b in active_bindings if active_bindings.count(b) > 1]
    assert_eq(len(set(dups)), 0, f"OmniWM: Duplicate active hotkey bindings found: {set(dups)}")

    print(
        f"PASS: macOS OmniWM Consumer validated ({len(required_bindings)} required hotkey bindings, "
        f"5 semantic workspaces, Niri settings, native Quake terminal, ipcEnabled=true, persistent workspaceBar=true)."
    )


# -----------------------------------------------------------------------------
# Layer C: Windows Host (AutoHotkey & GlazeWM)
# -----------------------------------------------------------------------------

def validate_windows_ahk(content: str) -> None:
    """Verify AutoHotkey translates all required editing, app, and desktop signals."""
    required_ahk_bindings = [
        # Hyper application actions (12)
        ("^!+#F13::", "^a", "Select All -> Ctrl+A"),
        ("^!+#F14::", "^s", "Save -> Ctrl+S"),
        ("^!+#F15::", "^f", "Find -> Ctrl+F"),
        ("^!+#F16::", "+{Tab}", "Previous Tab -> Ctrl+Shift+Tab"),
        ("^!+#F17::", "^{Tab}", "Next Tab -> Ctrl+Tab"),
        ("^!+#F18::", "^t", "New Tab -> Ctrl+T"),
        ("^!+#F19::", "^w", "Close Tab -> Ctrl+W"),
        ("^!+#F20::", "^+t", "Reopen Tab -> Ctrl+Shift+T"),
        ("^!+#F21::", "^{Left}", "Word Left -> Ctrl+Left"),
        ("^!+#F22::", "^{Right}", "Word Right -> Ctrl+Right"),
        ("^!+#F23::", "{F3}", "Find Next -> F3"),
        ("^!+#F24::", "^y", "Redo -> Ctrl+Y"),
        # Semantic editing clipboard fallbacks (with wildcard * modifier tolerance)
        ("*F21::", "^c", "Copy -> Ctrl+C"),
        ("*F22::", "^v", "Paste -> Ctrl+V"),
        ("*F23::", "^x", "Cut -> Ctrl+X"),
        ("*F24::", "^z", "Undo -> Ctrl+Z"),
        # Desktop launchers & controls
        ("!F13::", "#s", "Launcher -> Win+S"),
        ("!F14::", "wt", "Quick Terminal"),
        ("!F15::", "wt.exe", "New Terminal -> wt.exe"),
        ("!F16::", "Tab", "Previous Window -> Alt+Tab"),
        ("!F17::", "ToggleInputLanguage", "Language Toggle -> EVKey"),
    ]

    for trigger, target, desc in required_ahk_bindings:
        if trigger not in content:
            fail(f"Windows AutoHotkey: Missing hotkey trigger '{trigger}' for {desc}")

    # Ensure Hyper triggers appear before wildcard/bare triggers
    for key in ["F21", "F22", "F23", "F24"]:
        hyper_trigger = f"^!+#{key}::"
        wildcard_trigger = f"*{key}::"
        idx_hyper = content.find(hyper_trigger)
        idx_wildcard = content.find(wildcard_trigger)
        if idx_hyper == -1 or idx_wildcard == -1 or idx_hyper > idx_wildcard:
            fail(f"Windows AutoHotkey: {hyper_trigger} must precede {wildcard_trigger}")

    print("PASS: Windows AutoHotkey Bridge validated (12 Hyper app actions, editing F21-F24 with * modifier tolerance, desktop Alt+F13-F17).")

def validate_glazewm_consumer(data: dict) -> None:
    """Verify GlazeWM binds all semantic window management signals."""
    assert_in("keybindings", data, "GlazeWM missing 'keybindings' array")
    keybindings = data["keybindings"]

    all_bindings = set()
    for entry in keybindings:
        for b in entry.get("bindings", []):
            all_bindings.add(b.lower())

    # Collect mode bindings
    binding_modes = {mode["name"]: mode for mode in data.get("binding_modes", [])}
    assert_in("resize", binding_modes, "GlazeWM missing 'resize' binding mode")
    assert_in("service", binding_modes, "GlazeWM missing 'service' binding mode")

    required_glazewm_bindings = [
        # Workspaces 1-5
        "f13", "f14", "f15", "f16", "f17",
        "shift+f13", "shift+f14", "shift+f15", "shift+f16", "shift+f17",
        # Directional focus
        "ctrl+f13", "ctrl+f14", "ctrl+f15", "ctrl+f16",
        # Directional move
        "ctrl+shift+f13", "ctrl+shift+f14", "ctrl+shift+f15", "ctrl+shift+f16",
        # Modals & context
        "f18", "f19", "f20",
        "shift+f18",  # Resize mode
        "alt+f18",    # Service mode
    ]

    for b in required_glazewm_bindings:
        assert_in(b, all_bindings, f"Windows GlazeWM: Missing keybinding '{b}' in keybindings")

    # Check resize mode keybindings
    resize_kb = {
        b.lower()
        for entry in binding_modes["resize"].get("keybindings", [])
        for b in entry.get("bindings", [])
    }
    for b in ["ctrl+f13", "ctrl+f14", "ctrl+f15", "ctrl+f16", "escape", "enter"]:
        assert_in(b, resize_kb, f"Windows GlazeWM resize mode missing binding '{b}'")

    # Check service mode keybindings
    service_kb = {
        b.lower()
        for entry in binding_modes["service"].get("keybindings", [])
        for b in entry.get("bindings", [])
    }
    for b in ["ctrl+f13", "ctrl+f16", "f19", "f20", "escape", "enter"]:
        assert_in(b, service_kb, f"Windows GlazeWM service mode missing binding '{b}'")

    print("PASS: Windows GlazeWM Consumer validated (workspaces, navigation, resize mode, and service mode).")


# -----------------------------------------------------------------------------
# Layer D: Protocol Manifest & Signal Identity Consistency
# -----------------------------------------------------------------------------

def validate_protocol_signal_identities(manifest: ProtocolManifest) -> None:
    """Verify that all actions in protocol/semantic-v1.yaml have unique, well-formed signal identities."""
    seen_identities: Dict[Tuple[str, frozenset[str]], str] = {}
    for action_id, action in manifest.actions.items():
        ident = action.signal.identity
        if ident in seen_identities:
            fail(
                f"Protocol collision: Action '{action_id}' has duplicate signal identity {ident} "
                f"already used by '{seen_identities[ident]}'"
            )
        seen_identities[ident] = action_id

    assert_eq(
        len(manifest.actions),
        len(seen_identities),
        f"Expected {len(manifest.actions)} unique signal identities, got {len(seen_identities)}",
    )
    print(f"PASS: Protocol manifest validated ({len(manifest.actions)} unique semantic signal identities).")


# -----------------------------------------------------------------------------
# Main Runner
# -----------------------------------------------------------------------------

def main() -> None:
    print("=" * 70)
    print("RUNNING MULTI-KEYBOARD & MULTI-HOST PROTOCOL VALIDATION")
    print("=" * 70)

    # 0. Protocol Manifest
    manifest = load_protocol()
    validate_protocol_signal_identities(manifest)

    # 1. Producers
    validate_keymap_producer(CORNE_KEYMAP_PATH, "Corne")
    validate_keymap_producer(SOFLE_KEYMAP_PATH, "Sofle")

    # 2. macOS Host
    karabiner_ext_data = load_json(KARABINER_EXTERNAL_PATH)
    karabiner_laptop_data = load_json(KARABINER_LAPTOP_PATH)
    omniwm_data = load_toml(OMNIWM_PATH)
    validate_karabiner_external(karabiner_ext_data)
    validate_karabiner_laptop(karabiner_laptop_data)
    validate_omniwm_consumer(omniwm_data)

    # 3. Windows Host
    if not AHK_PATH.exists():
        fail(f"AutoHotkey file not found: {AHK_PATH}")
    ahk_content = AHK_PATH.read_text(encoding="utf-8")
    glazewm_data = load_yaml(GLAZEWM_PATH)
    validate_windows_ahk(ahk_content)
    validate_glazewm_consumer(glazewm_data)

    print("=" * 70)
    print("ALL MULTI-KEYBOARD & MULTI-HOST PROTOCOL CHECKS PASSED.")
    print("=" * 70)


if __name__ == "__main__":
    main()
