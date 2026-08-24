#!/usr/bin/env python3
"""
Structural & Positional Invariant Validator for Sofle Keyboard (60 keys + encoders).

Asserts exact position-level behaviors, rotary encoder bindings, and semantic signals
across all layers using the structured keymap parser.
"""

from __future__ import annotations

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
    from lib.keymap_parser import KeyboardConfig, parse_keymap_file
    from lib.validation import assert_eq, assert_in, assert_true, fail
except ImportError:
    from scripts.lib.keymap_parser import KeyboardConfig, parse_keymap_file
    from scripts.lib.validation import assert_eq, assert_in, assert_true, fail
KEYMAP_PATH = REPO_ROOT / "config" / "sofle.keymap"
CONF_PATH = REPO_ROOT / "config" / "sofle.conf"

EXPECTED_LAYER_NAMES = [
    "BASE", "NAV", "MOUSE", "MEDIA", "NUM", "SYM", "FUN", "HOST", "GAME", "ADJUST"
]


def test_layer_indices(cfg: KeyboardConfig) -> None:
    """Verify that all layer defines match expected 0-based indices and no extra layers exist."""
    for idx, name in enumerate(EXPECTED_LAYER_NAMES):
        def_name = f"L_{name}"
        assert_in(def_name, cfg.defines, f"Missing #define for {def_name}")
        assert_eq(cfg.defines[def_name], idx, f"Layer index for {def_name} should be {idx}")

    # Verify no BUTTON or GAME_AUX in defines or layers
    for prohibited in ["L_BUTTON", "BUTTON", "L_GAME_AUX", "GAME_AUX", "L_GAME_FN", "GAME_FN"]:
        assert_true(prohibited not in cfg.defines, f"Sofle must not define {prohibited}")
        assert_true(prohibited not in cfg.layers, f"Sofle must not contain layer {prohibited}")

    assert_eq(len(cfg.layers), 10, f"Sofle must have exactly 10 layers, found {len(cfg.layers)}")
    for name in EXPECTED_LAYER_NAMES:
        assert_in(name, cfg.layers, f"Keymap missing layer '{name}'")
        assert_eq(len(cfg.layer(name).bindings), 60, f"Layer '{name}' must have exactly 60 keys")

    print(f"PASS: All {len(EXPECTED_LAYER_NAMES)} layer indices and names verified (60 keys per layer).")


def test_base_layer(cfg: KeyboardConfig) -> None:
    """Verify exact physical positions, encoders, and thumbs on the BASE layer."""
    base = cfg.layer("BASE")

    # Number row (LN5..LN0, RN0..RN5)
    assert_eq(base.pos("LN5"), "&kp GRAVE", "LN5 must be GRAVE")
    assert_eq(base.pos("LN4"), "&kp N1", "LN4 must be N1")
    assert_eq(base.pos("LN3"), "&kp N2", "LN3 must be N2")
    assert_eq(base.pos("LN2"), "&kp N3", "LN2 must be N3")
    assert_eq(base.pos("LN1"), "&kp N4", "LN1 must be N4")
    assert_eq(base.pos("LN0"), "&kp N5", "LN0 must be N5")
    assert_eq(base.pos("RN0"), "&kp N6", "RN0 must be N6")
    assert_eq(base.pos("RN1"), "&kp N7", "RN1 must be N7")
    assert_eq(base.pos("RN2"), "&kp N8", "RN2 must be N8")
    assert_eq(base.pos("RN3"), "&kp N9", "RN3 must be N9")
    assert_eq(base.pos("RN4"), "&kp N0", "RN4 must be N0")
    assert_eq(base.pos("RN5"), "&kp DELETE", "RN5 must be DELETE")

    # Top row: ESC on LT5, Colemak-DH alphas
    assert_eq(base.pos("LT5"), "&kp ESCAPE", "LT5 must be ESCAPE")
    assert_eq(base.pos("LT4"), "&kp Q", "LT4 must be Q")
    assert_eq(base.pos("LT3"), "&kp W", "LT3 must be W")
    assert_eq(base.pos("LT2"), "&kp F", "LT2 must be F")
    assert_eq(base.pos("LT1"), "&kp P", "LT1 must be P")
    assert_eq(base.pos("LT0"), "&kp B", "LT0 must be B")
    assert_eq(base.pos("RT0"), "&kp J", "RT0 must be J")
    assert_eq(base.pos("RT1"), "&kp L", "RT1 must be L")
    assert_eq(base.pos("RT2"), "&kp U", "RT2 must be U")
    assert_eq(base.pos("RT3"), "&kp Y", "RT3 must be Y")
    assert_eq(base.pos("RT4"), "&kp SQT", "RT4 must be SQT")
    assert_eq(base.pos("RT5"), "&kp BACKSPACE", "RT5 must be BACKSPACE")

    # Middle row: MEDIA on LM5, Bilateral HRMs, G on LM0, M on RM0, Semicolon on RM5
    assert_eq(base.pos("LM5"), "&mo L_MEDIA", "LM5 must be &mo L_MEDIA")
    assert_eq(base.pos("LM4"), "&hml LMETA A", "LM4 must be &hml LMETA A")
    assert_eq(base.pos("LM3"), "&hml LEFT_ALT R", "LM3 must be &hml LEFT_ALT R")
    assert_eq(base.pos("LM2"), "&hml LCTRL S", "LM2 must be &hml LCTRL S")
    assert_eq(base.pos("LM1"), "&hml LEFT_SHIFT T", "LM1 must be &hml LEFT_SHIFT T")
    assert_eq(base.pos("LM0"), "&kp G", "LM0 must be G")
    assert_eq(base.pos("RM0"), "&kp M", "RM0 must be M")
    assert_eq(base.pos("RM1"), "&hmr RIGHT_SHIFT N", "RM1 must be &hmr RIGHT_SHIFT N")
    assert_eq(base.pos("RM2"), "&hmr RCTRL E", "RM2 must be &hmr RCTRL E")
    assert_eq(base.pos("RM3"), "&hmr RIGHT_ALT I", "RM3 must be &hmr RIGHT_ALT I")
    assert_eq(base.pos("RM4"), "&hmr RIGHT_GUI O", "RM4 must be &hmr RIGHT_GUI O")
    assert_eq(base.pos("RM5"), "&kp SEMICOLON", "RM5 must be SEMICOLON")

    # Bottom row & Encoders
    assert_eq(base.pos("LB5"), "&sk LSHFT", "LB5 must be Sticky Shift")
    assert_eq(base.pos("LEC"), "&caps_word", "LEC must be Caps Word on left encoder press")
    assert_eq(base.pos("REC"), "&kp C_MUTE", "REC must be Mute on right encoder press")
    assert_eq(base.pos("RB5"), "&kp RIGHT_SHIFT", "RB5 must be RIGHT_SHIFT")

    # Thumbs: 5-key thumb clusters
    assert_eq(base.pos("LH4"), "&kp LGUI", "LH4 must be LGUI")
    assert_eq(base.pos("LH3"), "&kp LALT", "LH3 must be LALT")
    assert_eq(base.pos("LH2"), "&lt L_MOUSE ESCAPE", "LH2 must be MOUSE/Esc")
    assert_eq(base.pos("LH1"), "&lt L_NAV SPACE", "LH1 must be NAV/Space")
    assert_eq(base.pos("LH0"), "&host_lt L_HOST TAB", "LH0 must be dedicated HOST/Tab")
    assert_eq(base.pos("RH0"), "&lt L_SYM ENTER", "RH0 must be SYM/Enter")
    assert_eq(base.pos("RH1"), "&lt L_NUM BACKSPACE", "RH1 must be NUM/Backspace")
    assert_eq(base.pos("RH2"), "&lt L_FUN DELETE", "RH2 must be FUN/Delete")
    assert_eq(base.pos("RH3"), "&kp RALT", "RH3 must be RALT")
    assert_eq(base.pos("RH4"), "&kp RGUI", "RH4 must be RGUI")

    # Sensor bindings (rotary encoders)
    assert_eq(len(base.sensor_bindings), 2, "BASE layer must have 2 sensor bindings")
    assert_eq(base.sensor_bindings[0], "&inc_dec_kp PAGE_DOWN PAGE_UP", "Left encoder rotation must be Page Down/Up")
    assert_eq(base.sensor_bindings[1], "&inc_dec_kp C_VOLUME_DOWN C_VOLUME_UP", "Right encoder rotation must be Volume Down/Up")

    print("PASS: BASE layer verified (Colemak-DH, bilateral HRMs, number row, thumb layer-taps, encoder presses & rotation).")


def test_game_layer(cfg: KeyboardConfig) -> None:
    """Verify GAME layer (plain QWERTY, number row, no HRMs, right encoder exit to BASE)."""
    game = cfg.layer("GAME")

    # Physical number row 1-0
    assert_eq(game.pos("LN4"), "&kp NUMBER_1")
    assert_eq(game.pos("LN3"), "&kp NUMBER_2")
    assert_eq(game.pos("LN2"), "&kp NUMBER_3")
    assert_eq(game.pos("LN1"), "&kp NUMBER_4")
    assert_eq(game.pos("LN0"), "&kp NUMBER_5")
    assert_eq(game.pos("RN0"), "&kp NUMBER_6")
    assert_eq(game.pos("RN1"), "&kp NUMBER_7")
    assert_eq(game.pos("RN2"), "&kp NUMBER_8")
    assert_eq(game.pos("RN3"), "&kp NUMBER_9")
    assert_eq(game.pos("RN4"), "&kp NUMBER_0")

    # Plain QWERTY
    assert_eq(game.pos("LT5"), "&kp ESCAPE")
    assert_eq(game.pos("LT4"), "&kp Q")
    assert_eq(game.pos("LT3"), "&kp W")
    assert_eq(game.pos("LT2"), "&kp E")
    assert_eq(game.pos("LT1"), "&kp R")
    assert_eq(game.pos("LT0"), "&kp T")

    # Modifiers
    assert_eq(game.pos("LM5"), "&kp TAB")
    assert_eq(game.pos("LB5"), "&kp LEFT_SHIFT")
    assert_eq(game.pos("LH4"), "&kp LCTRL")
    assert_eq(game.pos("LH3"), "&kp LALT")

    # Deliberate exit on right encoder press (REC)
    assert_eq(game.pos("REC"), "&to L_BASE", "REC must be &to L_BASE on GAME")

    # No HRMs or sticky keys
    for pos_label, b in game.all_by_pos().items():
        if pos_label != "REC":
            assert_true("&to L_BASE" not in b, f"GAME layer must not exit to BASE at {pos_label}")
        assert_true("&hml" not in b and "&hmr" not in b, f"GAME layer must not contain HRMs at {pos_label}")
        assert_true("&sk" not in b, f"GAME layer must not contain sticky keys at {pos_label}")

    print("PASS: GAME layer verified (plain QWERTY, number row, no HRMs, no sticky keys, right encoder exit to BASE).")


def test_bootloader_shortcuts(cfg: KeyboardConfig) -> None:
    """Verify bootloader and reset positions across NAV, NUM, and ADJUST."""
    nav = cfg.layer("NAV")
    num = cfg.layer("NUM")
    adjust = cfg.layer("ADJUST")

    # NAV left bootloader at LT5
    assert_eq(nav.pos("LT5"), "&bootloader", "NAV LT5 must be left &bootloader")

    # NUM right bootloader at RT5
    assert_eq(num.pos("RT5"), "&bootloader", "NUM RT5 must be right &bootloader")

    # ADJUST mirrored recovery positions
    assert_eq(adjust.pos("LT5"), "&bootloader", "ADJUST LT5 must be left &bootloader")
    assert_eq(adjust.pos("LT4"), "&sys_reset", "ADJUST LT4 must be left &sys_reset")
    assert_eq(adjust.pos("RT4"), "&sys_reset", "ADJUST RT4 must be right &sys_reset")
    assert_eq(adjust.pos("RT5"), "&bootloader", "ADJUST RT5 must be right &bootloader")

    print("PASS: Bootloader routing invariants verified (NAV LT5, NUM RT5, ADJUST mirrored left/right).")


def test_cross_platform_bindings(cfg: KeyboardConfig) -> None:
    """Verify standard Consumer media and semantic editing signals (F21-F24)."""
    media = cfg.layer("MEDIA")
    nav = cfg.layer("NAV")
    mouse = cfg.layer("MOUSE")

    # Media directional controls
    assert_eq(media.pos("RM1"), "&kp C_PREVIOUS")
    assert_eq(media.pos("RM2"), "&kp C_VOLUME_DOWN")
    assert_eq(media.pos("RM3"), "&kp C_VOLUME_UP")
    assert_eq(media.pos("RM4"), "&kp C_NEXT")
    assert_eq(media.pos("RH0"), "&kp C_STOP")
    assert_eq(media.pos("RH1"), "&kp C_PLAY_PAUSE")
    assert_eq(media.pos("RH2"), "&kp C_MUTE")

    # Sensor bindings on MEDIA
    assert_eq(media.sensor_bindings[0], "&inc_dec_kp C_PREVIOUS C_NEXT")
    assert_eq(media.sensor_bindings[1], "&inc_dec_kp C_VOLUME_DOWN C_VOLUME_UP")

    # Semantic editing signals on NAV and MOUSE (RT0..RT4)
    for l_name, l_obj in [("NAV", nav), ("MOUSE", mouse)]:
        assert_eq(l_obj.pos("RT0"), "&kp LS(F24)", f"{l_name} RT0 must be Redo &kp LS(F24)")
        assert_eq(l_obj.pos("RT1"), "&kp F22", f"{l_name} RT1 must be Paste &kp F22)")
        assert_eq(l_obj.pos("RT2"), "&kp F21", f"{l_name} RT2 must be Copy &kp F21)")
        assert_eq(l_obj.pos("RT3"), "&kp F23", f"{l_name} RT3 must be Cut &kp F23)")
        assert_eq(l_obj.pos("RT4"), "&kp F24", f"{l_name} RT4 must be Undo &kp F24)")

    print("PASS: Cross-platform bindings verified (Consumer media HID, semantic F21-F24 editing on NAV/MOUSE).")


def test_host_layer_bindings(cfg: KeyboardConfig) -> None:
    """Verify all 28 semantic signals on the HOST layer at exact physical positions."""
    host = cfg.layer("HOST")

    # Top row: Move window to workspace (LT4..LT0)
    assert_eq(host.pos("LT4"), "&kp LS(F13)", "LT4 must be Move WS 1")
    assert_eq(host.pos("LT3"), "&kp LS(F14)", "LT3 must be Move WS 2")
    assert_eq(host.pos("LT2"), "&kp LS(F15)", "LT2 must be Move WS 3")
    assert_eq(host.pos("LT1"), "&kp LS(F16)", "LT1 must be Move WS 4")
    assert_eq(host.pos("LT0"), "&kp LS(F17)", "LT0 must be Move WS 5")

    # Home row: Visit workspace (LM4..LM0)
    assert_eq(host.pos("LM4"), "&kp F13", "LM4 must be Focus WS 1")
    assert_eq(host.pos("LM3"), "&kp F14", "LM3 must be Focus WS 2")
    assert_eq(host.pos("LM2"), "&kp F15", "LM2 must be Focus WS 3")
    assert_eq(host.pos("LM1"), "&kp F16", "LM1 must be Focus WS 4")
    assert_eq(host.pos("LM0"), "&kp F17", "LM0 must be Focus WS 5")

    # Bottom left: Launchers (LB4..LB2)
    assert_eq(host.pos("LB4"), "&kp LA(F13)", "LB4 must be Launcher")
    assert_eq(host.pos("LB3"), "&kp LA(F14)", "LB3 must be Quick Terminal")
    assert_eq(host.pos("LB2"), "&kp LA(F15)", "LB2 must be New Terminal")
    assert_eq(host.pos("LB1"), "&kp LA(F17)", "LB1 must be Language Toggle")

    # Right top: Modals & Esc (RT1, RT2, RT5)
    assert_eq(host.pos("RT1"), "&kp LS(F18)", "RT1 must be Resize Mode")
    assert_eq(host.pos("RT2"), "&kp LA(F18)", "RT2 must be Service Mode")
    assert_eq(host.pos("RT5"), "&kp ESCAPE", "RT5 must be Escape")

    # Right home: Prev Window & Directional Focus (RM0..RM4)
    assert_eq(host.pos("RM0"), "&kp LA(F16)", "RM0 must be Previous Window")
    assert_eq(host.pos("RM1"), "&kp LC(F13)", "RM1 must be Focus Left")
    assert_eq(host.pos("RM2"), "&kp LC(F14)", "RM2 must be Focus Down")
    assert_eq(host.pos("RM3"), "&kp LC(F15)", "RM3 must be Focus Up")
    assert_eq(host.pos("RM4"), "&kp LC(F16)", "RM4 must be Focus Right")

    # Right bottom: Directional Move (RB1..RB4)
    assert_eq(host.pos("RB1"), "&kp LC(LS(F13))", "RB1 must be Move Left")
    assert_eq(host.pos("RB2"), "&kp LC(LS(F14))", "RB2 must be Move Down")
    assert_eq(host.pos("RB3"), "&kp LC(LS(F15))", "RB3 must be Move Up")
    assert_eq(host.pos("RB4"), "&kp LC(LS(F16))", "RB4 must be Move Right")

    # Right thumbs: Context Actions (RH0..RH2)
    assert_eq(host.pos("RH0"), "&kp F19", "RH0 must be Fullscreen")
    assert_eq(host.pos("RH1"), "&kp F18", "RH1 must be Previous Workspace")
    assert_eq(host.pos("RH2"), "&kp F20", "RH2 must be Float")

    print("PASS: HOST layer semantic signals verified at exact physical positions.")


def test_studio_configuration(cfg: KeyboardConfig) -> None:
    """Verify ZMK Studio unlock behavior on ADJUST layer and encoder resolution in sofle.conf."""
    adjust = cfg.layer("ADJUST")
    assert_eq(adjust.pos("RM0"), "&studio_unlock", "ADJUST RM0 must be &studio_unlock")

    if not CONF_PATH.exists():
        fail(f"Config file not found: {CONF_PATH}")
    conf_content = CONF_PATH.read_text(encoding="utf-8")
    assert_true("CONFIG_EC11=y" in conf_content, "sofle.conf must enable CONFIG_EC11=y")
    assert_true("CONFIG_EC11_TRIGGER_GLOBAL_THREAD=y" in conf_content, "sofle.conf must enable global thread for EC11")

    print("PASS: ZMK Studio locking, unlock behavior, and encoder config verified.")


def main() -> None:
    cfg = parse_keymap_file(KEYMAP_PATH, layout="sofle")
    test_layer_indices(cfg)
    test_base_layer(cfg)
    test_game_layer(cfg)
    test_bootloader_shortcuts(cfg)
    test_cross_platform_bindings(cfg)
    test_host_layer_bindings(cfg)
    test_studio_configuration(cfg)
    print("\nALL SOFLE STATIC KEYMAP INVARIANTS PASSED.")


if __name__ == "__main__":
    main()
