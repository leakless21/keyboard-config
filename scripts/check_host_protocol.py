#!/usr/bin/env python3
"""
End-to-end structural validation for the multi-keyboard semantic host protocol.

Validates the full architecture:
  Producers:
    - Corne firmware (config/corne.keymap)
    - Sofle firmware (config/sofle.keymap)
  macOS Consumers:
    - Karabiner-Elements translation (hosts/macos/karabiner.json)
    - AeroSpace window manager (hosts/macos/aerospace.toml)
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
    from lib.validation import assert_eq, assert_in, assert_true, fail, load_json, load_toml, load_yaml
except ImportError:
    from scripts.lib.keymap_parser import parse_keymap_file
    from scripts.lib.validation import assert_eq, assert_in, assert_true, fail, load_json, load_toml, load_yaml
CORNE_KEYMAP_PATH = REPO_ROOT / "config" / "corne.keymap"
SOFLE_KEYMAP_PATH = REPO_ROOT / "config" / "sofle.keymap"
KARABINER_PATH = REPO_ROOT / "hosts" / "macos" / "karabiner.json"
AEROSPACE_PATH = REPO_ROOT / "hosts" / "macos" / "aerospace.toml"
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
    "&kp LS(F18)",  # Resize mode
    "&kp F18",      # Previous workspace
    "&kp F19",      # Fullscreen
    "&kp F20",      # Float / tile
    # Extended semantic protocol
    "&kp LA(F13)",  # SYSTEM_LAUNCHER (Spotlight / Windows Search)
    "&kp LA(F14)",  # QUICK_TERMINAL (Ghostty scratchpad / Quake)
    "&kp LA(F15)",  # NEW_TERMINAL (Ghostty / Windows Terminal)
    "&kp LA(F16)",  # PREVIOUS_WINDOW (focus-back-and-forth / Alt+Tab)
    "&kp LA(F17)",  # LANGUAGE_TOGGLE (Input Source / EVKey)
    "&kp LA(F18)",  # SERVICE_MODE (AeroSpace / GlazeWM service)
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
# Layer B: macOS Host (Karabiner & AeroSpace)
# -----------------------------------------------------------------------------

def validate_karabiner_translator(karabiner_data: dict) -> None:
    """Verify that Karabiner maps all semantic signals and standard F1-F12 normalization."""
    rules = karabiner_data.get("rules", [])
    if len(rules) < 3:
        fail("Layer B (Karabiner): Expected at least 3 rules in karabiner.json")

    # Collect all manipulators across rules
    all_manipulators = []
    for r in rules:
        for m in r.get("manipulators", []):
            all_manipulators.append(m)

    # Classify manipulators into distinct architectural groups
    semantic_host_manipulators = []
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
        elif key_code in [f"f{i}" for i in range(13, 21)]:
            semantic_host_manipulators.append(m)
        elif key_code in [f"f{i}" for i in range(21, 25)]:
            semantic_editing_manipulators.append(m)
        elif key_code in [f"f{i}" for i in range(1, 13)]:
            standard_f_manipulators.append(m)
        else:
            unexpected_manipulators.append(m)

    assert_eq(
        len(unexpected_manipulators),
        0,
        f"Layer B (Karabiner): Found unexpected manipulators: {unexpected_manipulators}",
    )
    assert_eq(
        len(semantic_host_manipulators),
        28,
        f"Layer B (Karabiner): Expected exactly 28 HOST manipulators, found {len(semantic_host_manipulators)}",
    )
    assert_eq(
        len(semantic_app_manipulators),
        12,
        f"Layer B (Karabiner): Expected exactly 12 Hyper application manipulators, found {len(semantic_app_manipulators)}",
    )
    assert_eq(
        len(semantic_editing_manipulators),
        4,
        f"Layer B (Karabiner): Expected exactly 4 editing manipulators, found {len(semantic_editing_manipulators)}",
    )
    assert_eq(
        len(standard_f_manipulators),
        12,
        f"Layer B (Karabiner): Expected exactly 12 standard F-key normalizers, found {len(standard_f_manipulators)}",
    )
    assert_eq(
        len(all_manipulators),
        56,
        f"Layer B (Karabiner): Expected exactly 56 canonical manipulators (28 HOST + 12 Hyper app + 4 editing + 12 standard F), found {len(all_manipulators)}",
    )

    # Verify that all editing manipulators specify optional: ['any'] to tolerate extra held modifiers
    for m in semantic_editing_manipulators:
        opt_mods = m.get("from", {}).get("modifiers", {}).get("optional", [])
        assert_in(
            "any",
            opt_mods,
            f"Layer B (Karabiner): Editing manipulator {m.get('from')} must specify optional: ['any'] to tolerate held modifiers",
        )

    # Check device scoping conditions across all manipulators
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
                f"Layer B (Karabiner): Manipulator #{idx} ({m.get('from')}) "
                f"must be scoped with device_if excluding built-in keyboard (is_built_in_keyboard: false)"
            )

    # Validate Standard F1-F12 normalization group
    for i in range(1, 13):
        f_key = f"f{i}"
        matching = [m for m in standard_f_manipulators if m.get("from", {}).get("key_code") == f_key]
        assert_eq(
            len(matching),
            1,
            f"Layer B (Karabiner): Expected exactly 1 normalizer for {f_key}, found {len(matching)}",
        )
        norm_m = matching[0]

        # from.modifiers.optional must contain "any"
        optional_mods = norm_m.get("from", {}).get("modifiers", {}).get("optional", [])
        assert_in(
            "any",
            optional_mods,
            f"Layer B (Karabiner): {f_key} from.modifiers.optional must contain 'any' to preserve opposite-hand mods",
        )

        # to must map to same f-key with "fn" modifier
        to_list = norm_m.get("to", [])
        assert_true(
            len(to_list) > 0,
            f"Layer B (Karabiner): {f_key} normalizer must specify at least one 'to' target",
        )
        to_target = to_list[0]
        assert_eq(
            to_target.get("key_code"),
            f_key,
            f"Layer B (Karabiner): {f_key} normalizer must map to key_code '{f_key}'",
        )
        assert_in(
            "fn",
            to_target.get("modifiers", []),
            f"Layer B (Karabiner): {f_key} normalizer to.modifiers must contain 'fn'",
        )

        # conditions must contain system F-key preference condition
        conds = norm_m.get("conditions", [])
        has_sys_fkey_cond = False
        for c in conds:
            if (
                c.get("type") == "variable_if"
                and c.get("name") == "system.use_fkeys_as_standard_function_keys"
                and c.get("value") is False
            ):
                has_sys_fkey_cond = True
        assert_true(
            has_sys_fkey_cond,
            f"Layer B (Karabiner): {f_key} normalizer missing system.use_fkeys_as_standard_function_keys variable_if condition",
        )
    expected_translations: List[Tuple[str, Set[str], str, Set[str]]] = [
        # Directional move
        ("f13", {"control", "shift"}, "h", {"left_alt", "left_shift"}),
        ("f14", {"control", "shift"}, "j", {"left_alt", "left_shift"}),
        ("f15", {"control", "shift"}, "k", {"left_alt", "left_shift"}),
        ("f16", {"control", "shift"}, "l", {"left_alt", "left_shift"}),
        # Directional focus
        ("f13", {"control"}, "h", {"left_alt"}),
        ("f14", {"control"}, "j", {"left_alt"}),
        ("f15", {"control"}, "k", {"left_alt"}),
        ("f16", {"control"}, "l", {"left_alt"}),
        # Move to workspace 1-5
        ("f13", {"shift"}, "1", {"left_alt", "left_shift"}),
        ("f14", {"shift"}, "2", {"left_alt", "left_shift"}),
        ("f15", {"shift"}, "3", {"left_alt", "left_shift"}),
        ("f16", {"shift"}, "4", {"left_alt", "left_shift"}),
        ("f17", {"shift"}, "5", {"left_alt", "left_shift"}),
        # Resize mode
        ("f18", {"shift"}, "r", {"left_alt"}),
        # Extended semantic protocol
        ("f13", {"option"}, "spacebar", {"left_command"}),               # LAUNCHER -> Cmd+Space
        ("f14", {"option"}, "grave_accent_and_tilde", {"left_control"}),  # QTERM -> Ctrl+`
        ("f15", {"option"}, "return_or_enter", {"left_alt"}),            # TERM -> Alt+Enter
        ("f16", {"option"}, "grave_accent_and_tilde", {"left_alt"}),      # PREV WIN -> Alt+`
        ("f17", {"option"}, "spacebar", {"left_control"}),               # LANG -> Ctrl+Space
        ("f18", {"option"}, "semicolon", {"left_alt", "left_shift"}),     # SERVICE -> Alt+Shift+;
        # Workspace focus 1-5
        ("f13", set(), "1", {"left_alt"}),
        ("f14", set(), "2", {"left_alt"}),
        ("f15", set(), "3", {"left_alt"}),
        ("f16", set(), "4", {"left_alt"}),
        ("f17", set(), "5", {"left_alt"}),
        # Context controls
        ("f18", set(), "tab", {"left_alt"}),                             # PREV WS -> Alt+Tab
        ("f19", set(), "f", {"left_alt"}),                               # FULL -> Alt+F
        ("f20", set(), "spacebar", {"left_alt", "left_shift"}),          # FLOAT -> Alt+Shift+Space
        # Semantic editing
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
        # Semantic editing clipboard actions (4)
        ("f21", set(), "c", {"left_command"}),
        ("f22", set(), "v", {"left_command"}),
        ("f23", set(), "x", {"left_command"}),
        ("f24", set(), "z", {"left_command"}),
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
                f"Layer B (Karabiner): Missing translation for from=({from_key}, mods={from_mods}) "
                f"-> to=({to_key}, mods={to_mods})"
            )

    print(
        f"PASS: macOS Karabiner Translation validated ({len(expected_translations)} semantic mappings + {len(standard_f_manipulators)} standard F-key normalizers with device_if scoping)."
    )


def validate_aerospace_consumer(data: dict) -> None:
    """Verify AeroSpace config consumes all chords produced by Karabiner / laptop."""
    mode = data.get("mode", {})
    main_mode = mode.get("main", {})
    main_bindings = main_mode.get("binding", {})

    required_main_bindings = [
        "alt-1", "alt-2", "alt-3", "alt-4", "alt-5",
        "alt-shift-1", "alt-shift-2", "alt-shift-3", "alt-shift-4", "alt-shift-5",
        "alt-h", "alt-j", "alt-k", "alt-l",
        "alt-shift-h", "alt-shift-j", "alt-shift-k", "alt-shift-l",
        "alt-r", "alt-shift-semicolon", "alt-f", "alt-shift-space",
        "alt-tab", "alt-backtick", "alt-enter",
    ]
    for b in required_main_bindings:
        assert_in(b, main_bindings, f"AeroSpace: Missing binding '{b}' in [mode.main.binding]")

    resize_mode = mode.get("resize", {})
    resize_bindings = resize_mode.get("binding", {})
    required_resize_bindings = [
        "alt-h", "alt-j", "alt-k", "alt-l",
        "h", "j", "k", "l",
        "enter", "esc",
    ]
    for b in required_resize_bindings:
        assert_in(b, resize_bindings, f"AeroSpace: Missing binding '{b}' in [mode.resize.binding]")

    service_mode = mode.get("service", {})
    service_bindings = service_mode.get("binding", {})
    required_service_bindings = [
        "h", "j", "k", "l",
        "alt-h", "alt-j", "alt-k", "alt-l",
        "shift-h", "shift-j", "shift-k", "shift-l",
        "alt-shift-h", "alt-shift-j", "alt-shift-k", "alt-shift-l",
        "b", "r", "t", "a",
        "m", "shift-m",
        "enter", "esc",
    ]
    for b in required_service_bindings:
        assert_in(b, service_bindings, f"AeroSpace: Missing binding '{b}' in [mode.service.binding]")

    # Check on-window-detected list
    on_window_detected = data.get("on-window-detected", [])
    for rule in on_window_detected:
        app_id = rule.get("check-further-callbacks", {}).get("app-id", "") if isinstance(rule, dict) else ""
        run = rule.get("run", "") if isinstance(rule, dict) else ""
        if "com.mitchellh.ghostty" in str(rule) and "move-node-to-workspace" in str(rule):
            fail("AeroSpace: Ghostty must NOT have automatic workspace routing in on-window-detected")

    print("PASS: macOS AeroSpace Consumer validated (main, resize, service modes, and no Ghostty auto-routing).")


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
# Main Runner
# -----------------------------------------------------------------------------

def main() -> None:
    print("=" * 70)
    print("RUNNING MULTI-KEYBOARD & MULTI-HOST PROTOCOL VALIDATION")
    print("=" * 70)

    # 1. Producers
    validate_keymap_producer(CORNE_KEYMAP_PATH, "Corne")
    validate_keymap_producer(SOFLE_KEYMAP_PATH, "Sofle")

    # 2. macOS Host
    karabiner_data = load_json(KARABINER_PATH)
    aerospace_data = load_toml(AEROSPACE_PATH)
    validate_karabiner_translator(karabiner_data)
    validate_aerospace_consumer(aerospace_data)

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
