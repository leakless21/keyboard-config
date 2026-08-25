#!/usr/bin/env python3
"""
Structural & Positional Invariant Validator for Corne Keyboard (42 keys).

Asserts exact position-level behaviors and semantic signals across all layers
using the structured keymap parser.
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
KEYMAP_PATH = REPO_ROOT / "config" / "corne.keymap"
CONF_PATH = REPO_ROOT / "config" / "corne.conf"

EXPECTED_LAYER_NAMES = [
    "BASE", "NAV", "MOUSE", "MEDIA", "NUM", "SYM", "FUN", "HOST", "GAME", "ADJUST", "GAME_FN"
]


def test_layer_indices(cfg: KeyboardConfig) -> None:
    """Verify that all layer defines match expected 0-based indices in sequential order."""
    for idx, name in enumerate(EXPECTED_LAYER_NAMES):
        def_name = f"L_{name}"
        assert_in(def_name, cfg.defines, f"Missing #define for {def_name}")
        assert_eq(cfg.defines[def_name], idx, f"Layer index for {def_name} should be {idx}")
        assert_in(name, cfg.layers, f"Keymap missing layer '{name}'")

    print(f"PASS: All {len(EXPECTED_LAYER_NAMES)} layer indices and names verified structurally.")


def test_base_layer(cfg: KeyboardConfig) -> None:
    """Verify exact physical positions on the BASE layer."""
    base = cfg.layer("BASE")

    # Esc on LT5
    assert_eq(base.pos("LT5"), "&kp ESCAPE", "LT5 must be &kp ESCAPE")

    # Left top alphas: Q W F P B
    assert_eq(base.pos("LT4"), "&kp Q", "LT4 must be Q")
    assert_eq(base.pos("LT3"), "&kp W", "LT3 must be W")
    assert_eq(base.pos("LT2"), "&kp F", "LT2 must be F")
    assert_eq(base.pos("LT1"), "&kp P", "LT1 must be P")
    assert_eq(base.pos("LT0"), "&kp B", "LT0 must be B")

    # Right top alphas: J L U Y SQT BACKSPACE
    assert_eq(base.pos("RT0"), "&kp J", "RT0 must be J")
    assert_eq(base.pos("RT1"), "&kp L", "RT1 must be L")
    assert_eq(base.pos("RT2"), "&kp U", "RT2 must be U")
    assert_eq(base.pos("RT3"), "&kp Y", "RT3 must be Y")
    assert_eq(base.pos("RT4"), "&kp SQT", "RT4 must be SQT")
    assert_eq(base.pos("RT5"), "&kp BACKSPACE", "RT5 must be BACKSPACE")

    # Left middle: MEDIA on LM5, Bilateral HRMs on LM4..LM1, G on LM0
    assert_eq(base.pos("LM5"), "&mo L_MEDIA", "LM5 must be &mo L_MEDIA")
    assert_eq(base.pos("LM4"), "&hml LMETA A", "LM4 must be &hml LMETA A")
    assert_eq(base.pos("LM3"), "&hml LEFT_ALT R", "LM3 must be &hml LEFT_ALT R")
    assert_eq(base.pos("LM2"), "&hml LCTRL S", "LM2 must be &hml LCTRL S")
    assert_eq(base.pos("LM1"), "&hml LEFT_SHIFT T", "LM1 must be &hml LEFT_SHIFT T")
    assert_eq(base.pos("LM0"), "&kp G", "LM0 must be G")

    # Right middle: M on RM0, Bilateral HRMs on RM1..RM4, Semicolon on RM5
    assert_eq(base.pos("RM0"), "&kp M", "RM0 must be M")
    assert_eq(base.pos("RM1"), "&hmr RIGHT_SHIFT N", "RM1 must be &hmr RIGHT_SHIFT N")
    assert_eq(base.pos("RM2"), "&hmr RCTRL E", "RM2 must be &hmr RCTRL E")
    assert_eq(base.pos("RM3"), "&hmr RIGHT_ALT I", "RM3 must be &hmr RIGHT_ALT I")
    assert_eq(base.pos("RM4"), "&hmr RIGHT_GUI O", "RM4 must be &hmr RIGHT_GUI O")
    assert_eq(base.pos("RM5"), "&kp SEMICOLON", "RM5 must be SEMICOLON")

    # Left bottom: Sticky Shift on LB5, Z X C D V on LB4..LB0
    assert_eq(base.pos("LB5"), "&sk LSHFT", "LB5 must be &sk LSHFT")
    assert_eq(base.pos("LB4"), "&kp Z", "LB4 must be Z")
    assert_eq(base.pos("LB3"), "&kp X", "LB3 must be X")
    assert_eq(base.pos("LB2"), "&kp C", "LB2 must be C")
    assert_eq(base.pos("LB1"), "&kp D", "LB1 must be D")
    assert_eq(base.pos("LB0"), "&kp V", "LB0 must be V")

    # Right bottom: K H COMMA DOT SLASH RIGHT_SHIFT
    assert_eq(base.pos("RB0"), "&kp K", "RB0 must be K")
    assert_eq(base.pos("RB1"), "&kp H", "RB1 must be H")
    assert_eq(base.pos("RB2"), "&kp COMMA", "RB2 must be COMMA")
    assert_eq(base.pos("RB3"), "&kp DOT", "RB3 must be DOT")
    assert_eq(base.pos("RB4"), "&kp SLASH", "RB4 must be SLASH")
    assert_eq(base.pos("RB5"), "&kp RIGHT_SHIFT", "RB5 must be RIGHT_SHIFT")

    # Thumbs: LH2 (MOUSE/Esc), LH1 (NAV/Space), LH0 (HOST/Tab), RH0 (SYM/Enter), RH1 (NUM/Backspace), RH2 (FUN/Delete)
    assert_eq(base.pos("LH2"), "&lt L_MOUSE ESCAPE", "LH2 must be MOUSE/Esc layer-tap")
    assert_eq(base.pos("LH1"), "&lt L_NAV SPACE", "LH1 must be NAV/Space layer-tap")
    assert_eq(base.pos("LH0"), "&host_lt L_HOST TAB", "LH0 must be dedicated HOST/Tab layer-tap")
    assert_eq(base.pos("RH0"), "&lt L_SYM ENTER", "RH0 must be SYM/Enter layer-tap")
    assert_eq(base.pos("RH1"), "&lt L_NUM BACKSPACE", "RH1 must be NUM/Backspace layer-tap")
    assert_eq(base.pos("RH2"), "&lt L_FUN DELETE", "RH2 must be FUN/Delete layer-tap")

    print("PASS: BASE layer exact physical positions verified.")


def test_game_layer(cfg: KeyboardConfig) -> None:
    """Verify GAME layer invariants (plain QWERTY, no HRMs, dedicated Esc hold-tap, momentary AUX)."""
    game = cfg.layer("GAME")

    # Esc hold-tap on LT5
    lt5_binding = game.pos("LT5")
    assert_true(
        "ESCAPE" in lt5_binding and "game_fn_lt" in lt5_binding,
        f"LT5 on GAME must be dedicated hold-tap &game_fn_lt with ESCAPE, got: {lt5_binding}"
    )

    # QWERTY alphas
    assert_eq(game.pos("LT4"), "&kp Q")
    assert_eq(game.pos("LT3"), "&kp W")
    assert_eq(game.pos("LT2"), "&kp E")
    assert_eq(game.pos("LT1"), "&kp R")
    assert_eq(game.pos("LT0"), "&kp T")
    assert_eq(game.pos("LM4"), "&kp A")
    assert_eq(game.pos("LM3"), "&kp S")
    assert_eq(game.pos("LM2"), "&kp D")
    assert_eq(game.pos("LM1"), "&kp F")
    assert_eq(game.pos("LM0"), "&kp G")

    # Direct modifiers
    assert_eq(game.pos("LM5"), "&kp TAB")
    assert_eq(game.pos("LB5"), "&kp LEFT_SHIFT")
    assert_eq(game.pos("LH2"), "&kp LCTRL")
    assert_eq(game.pos("LH1"), "&kp SPACE")
    assert_eq(game.pos("LH0"), "&kp LALT")

    # Momentary FN on RH1
    rh1_binding = game.pos("RH1")
    assert_eq(
        rh1_binding,
        "&mo L_GAME_FN",
        f"RH1 on GAME must be momentary access to gaming utility layer, got: {rh1_binding}"
    )

    # No HRMs or sticky keys
    for pos_label, b in game.all_by_pos().items():
        assert_true("&hml" not in b and "&hmr" not in b, f"GAME layer must not contain HRMs at {pos_label}")
        assert_true("&sk" not in b, f"GAME layer must not contain sticky keys at {pos_label}")
        assert_true("&to L_BASE" not in b, f"GAME layer must not directly exit to BASE at {pos_label}")

    print("PASS: GAME layer invariants verified (no HRMs, dedicated Esc hold-tap, momentary AUX/FN).")


def test_game_fn_layer(cfg: KeyboardConfig) -> None:
    """Verify GAME_FN layer (1-0 numbers, F1-F10, punctuation, deliberate exit to BASE)."""
    fn = cfg.layer("GAME_FN")

    # Numbers 1-5 on top-left, 6-0 on top-right
    assert_eq(fn.pos("LT4"), "&kp NUMBER_1")
    assert_eq(fn.pos("LT3"), "&kp NUMBER_2")
    assert_eq(fn.pos("LT2"), "&kp NUMBER_3")
    assert_eq(fn.pos("LT1"), "&kp NUMBER_4")
    assert_eq(fn.pos("LT0"), "&kp NUMBER_5")
    assert_eq(fn.pos("RT0"), "&kp NUMBER_6")
    assert_eq(fn.pos("RT1"), "&kp NUMBER_7")
    assert_eq(fn.pos("RT2"), "&kp NUMBER_8")
    assert_eq(fn.pos("RT3"), "&kp NUMBER_9")
    assert_eq(fn.pos("RT4"), "&kp NUMBER_0")

    # F1-F5 on home-left, F6-F10 on home-right
    assert_eq(fn.pos("LM4"), "&kp F1")
    assert_eq(fn.pos("LM3"), "&kp F2")
    assert_eq(fn.pos("LM2"), "&kp F3")
    assert_eq(fn.pos("LM1"), "&kp F4")
    assert_eq(fn.pos("LM0"), "&kp F5")
    assert_eq(fn.pos("RM0"), "&kp F6")
    assert_eq(fn.pos("RM1"), "&kp F7")
    assert_eq(fn.pos("RM2"), "&kp F8")
    assert_eq(fn.pos("RM3"), "&kp F9")
    assert_eq(fn.pos("RM4"), "&kp F10")

    # Deliberate exit to BASE at RH2
    assert_eq(fn.pos("RH2"), "&to L_BASE", "GAME_FN RH2 must be deliberate exit &to L_BASE")

    print("PASS: GAME_FN layer invariants verified (1-0, F1-F10, deliberate exit to BASE at RH2).")


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

    # Media directional and brightness controls
    assert_eq(media.pos("RT2"), "&kp C_BRI_DN", "MEDIA RT2 must be Brightness Down (&kp C_BRI_DN)")
    assert_eq(media.pos("RT3"), "&kp C_BRI_UP", "MEDIA RT3 must be Brightness Up (&kp C_BRI_UP)")
    assert_eq(media.pos("RM1"), "&kp C_PREVIOUS")
    assert_eq(media.pos("RM2"), "&kp C_VOLUME_DOWN")
    assert_eq(media.pos("RM3"), "&kp C_VOLUME_UP")
    assert_eq(media.pos("RM4"), "&kp C_NEXT")
    assert_eq(media.pos("RH0"), "&kp C_STOP")
    assert_eq(media.pos("RH1"), "&kp C_PLAY_PAUSE")
    assert_eq(media.pos("RH2"), "&kp C_MUTE")

    # Semantic editing signals on NAV and MOUSE (RT0..RT4)
    for l_name, l_obj in [("NAV", nav), ("MOUSE", mouse)]:
        assert_eq(l_obj.pos("RT0"), "&kp LS(F24)", f"{l_name} RT0 must be Redo &kp LS(F24)")
        assert_eq(l_obj.pos("RT1"), "&kp F22", f"{l_name} RT1 must be Paste &kp F22)")
        assert_eq(l_obj.pos("RT2"), "&kp F21", f"{l_name} RT2 must be Copy &kp F21)")
        assert_eq(l_obj.pos("RT3"), "&kp F23", f"{l_name} RT3 must be Cut &kp F23)")
        assert_eq(l_obj.pos("RT4"), "&kp F24", f"{l_name} RT4 must be Undo &kp F24)")

    print("PASS: Cross-platform bindings verified (Consumer media HID brightness/volume/transport, semantic F21-F24 editing on NAV/MOUSE).")

def test_caps_behavior(cfg: KeyboardConfig) -> None:
    """Verify Caps Word on NAV (RM0) and Caps Lock fallback on FUN (RT0)."""
    nav = cfg.layer("NAV")
    fun = cfg.layer("FUN")

    assert_eq(nav.pos("RM0"), "&caps_word", "NAV RM0 must be &caps_word")
    assert_eq(fun.pos("RT0"), "&kp CAPSLOCK", "FUN RT0 must be &kp CAPSLOCK fallback")

    print("PASS: Caps behavior verified (&caps_word on NAV, &kp CAPSLOCK fallback on FUN).")

def test_num_layer(cfg: KeyboardConfig) -> None:
    """Verify NUM layer exact physical positions (operator rail, numpad, thumbs, modifiers, bootloader)."""
    num = cfg.layer("NUM")

    # Left hand operator rail
    assert_eq(num.pos("LT5"), "&kp SLASH", "NUM LT5 must be /")
    assert_eq(num.pos("LM5"), "&kp ASTERISK", "NUM LM5 must be *")
    assert_eq(num.pos("LB5"), "&kp PLUS", "NUM LB5 must be +")

    # Left hand spatial numpad core
    assert_eq(num.pos("LT4"), "&kp LEFT_BRACKET", "NUM LT4 must be [")
    assert_eq(num.pos("LT3"), "&kp NUMBER_7", "NUM LT3 must be 7")
    assert_eq(num.pos("LT2"), "&kp NUMBER_8", "NUM LT2 must be 8")
    assert_eq(num.pos("LT1"), "&kp NUMBER_9", "NUM LT1 must be 9")
    assert_eq(num.pos("LT0"), "&kp RIGHT_BRACKET", "NUM LT0 must be ]")

    assert_eq(num.pos("LM4"), "&kp SEMICOLON", "NUM LM4 must be ;")
    assert_eq(num.pos("LM3"), "&kp NUMBER_4", "NUM LM3 must be 4")
    assert_eq(num.pos("LM2"), "&kp NUMBER_5", "NUM LM2 must be 5")
    assert_eq(num.pos("LM1"), "&kp NUMBER_6", "NUM LM1 must be 6")
    assert_eq(num.pos("LM0"), "&kp EQUAL", "NUM LM0 must be =")

    assert_eq(num.pos("LB4"), "&kp GRAVE", "NUM LB4 must be `")
    assert_eq(num.pos("LB3"), "&kp NUMBER_1", "NUM LB3 must be 1")
    assert_eq(num.pos("LB2"), "&kp NUMBER_2", "NUM LB2 must be 2")
    assert_eq(num.pos("LB1"), "&kp NUMBER_3", "NUM LB1 must be 3")
    assert_eq(num.pos("LB0"), "&kp BACKSLASH", "NUM LB0 must be \\")

    # Left thumbs
    assert_eq(num.pos("LH2"), "&kp PERIOD", "NUM LH2 must be .")
    assert_eq(num.pos("LH1"), "&kp NUMBER_0", "NUM LH1 must be 0")
    assert_eq(num.pos("LH0"), "&kp MINUS", "NUM LH0 must be -")

    # Right hand mirrored modifiers and bootloader
    assert_eq(num.pos("RT5"), "&bootloader", "NUM RT5 must be bootloader")
    assert_eq(num.pos("RM1"), "&kp RIGHT_SHIFT", "NUM RM1 must be Right Shift")
    assert_eq(num.pos("RM2"), "&kp RCTRL", "NUM RM2 must be Right Ctrl")
    assert_eq(num.pos("RM3"), "&kp RIGHT_ALT", "NUM RM3 must be Right Alt")
    assert_eq(num.pos("RM4"), "&kp RIGHT_GUI", "NUM RM4 must be Right GUI")

    print("PASS: Corne NUM Seniply+/operator geometry verified.")


def test_sym_layer(cfg: KeyboardConfig) -> None:
    """Verify SYM layer exact Seniply+ physical positions and mirrored modifiers."""
    sym = cfg.layer("SYM")

    # Left hand top row: @ # $ ] } )
    assert_eq(sym.pos("LT5"), "&kp AT_SIGN", "SYM LT5 must be @")
    assert_eq(sym.pos("LT4"), "&kp HASH", "SYM LT4 must be #")
    assert_eq(sym.pos("LT3"), "&kp DOLLAR", "SYM LT3 must be $")
    assert_eq(sym.pos("LT2"), "&kp RIGHT_BRACKET", "SYM LT2 must be ]")
    assert_eq(sym.pos("LT1"), "&kp RIGHT_BRACE", "SYM LT1 must be }")
    assert_eq(sym.pos("LT0"), "&kp RIGHT_PARENTHESIS", "SYM LT0 must be )")

    # Left hand middle row: ! < > [ { (
    assert_eq(sym.pos("LM5"), "&kp EXCLAMATION", "SYM LM5 must be !")
    assert_eq(sym.pos("LM4"), "&kp LESS_THAN", "SYM LM4 must be <")
    assert_eq(sym.pos("LM3"), "&kp GREATER_THAN", "SYM LM3 must be >")
    assert_eq(sym.pos("LM2"), "&kp LEFT_BRACKET", "SYM LM2 must be [")
    assert_eq(sym.pos("LM1"), "&kp LEFT_BRACE", "SYM LM1 must be {")
    assert_eq(sym.pos("LM0"), "&kp LEFT_PARENTHESIS", "SYM LM0 must be (")

    # Left hand bottom row: & | * - = +
    assert_eq(sym.pos("LB5"), "&kp AMPERSAND", "SYM LB5 must be &")
    assert_eq(sym.pos("LB4"), "&kp PIPE", "SYM LB4 must be |")
    assert_eq(sym.pos("LB3"), "&kp ASTERISK", "SYM LB3 must be *")
    assert_eq(sym.pos("LB2"), "&kp MINUS", "SYM LB2 must be -")
    assert_eq(sym.pos("LB1"), "&kp EQUAL", "SYM LB1 must be =")
    assert_eq(sym.pos("LB0"), "&kp PLUS", "SYM LB0 must be +")

    # Left thumbs: \ / _
    assert_eq(sym.pos("LH2"), "&kp BACKSLASH", "SYM LH2 must be \\")
    assert_eq(sym.pos("LH1"), "&kp SLASH", "SYM LH1 must be /")
    assert_eq(sym.pos("LH0"), "&kp UNDERSCORE", "SYM LH0 must be _")

    # Right hand mirrored modifiers
    assert_eq(sym.pos("RM1"), "&kp RIGHT_SHIFT", "SYM RM1 must be Right Shift")
    assert_eq(sym.pos("RM2"), "&kp RCTRL", "SYM RM2 must be Right Ctrl")
    assert_eq(sym.pos("RM3"), "&kp RIGHT_ALT", "SYM RM3 must be Right Alt")
    assert_eq(sym.pos("RM4"), "&kp RIGHT_GUI", "SYM RM4 must be Right GUI")

    print("PASS: Corne SYM Seniply+ geometry verified.")

def test_cross_keyboard_parity(corne_cfg: KeyboardConfig) -> None:
    """Verify exact parity between Corne and Sofle across all shared NUM and SYM positions."""
    sofle_keymap_path = REPO_ROOT / "config" / "sofle.keymap"
    sofle_cfg = parse_keymap_file(sofle_keymap_path, layout="sofle")

    shared_positions = [
        "LT5", "LT4", "LT3", "LT2", "LT1", "LT0",
        "LM5", "LM4", "LM3", "LM2", "LM1", "LM0",
        "LB5", "LB4", "LB3", "LB2", "LB1", "LB0",
        "LH2", "LH1", "LH0",
        "RT0", "RT1", "RT2", "RT3", "RT4", "RT5",
        "RM0", "RM1", "RM2", "RM3", "RM4", "RM5",
        "RB0", "RB1", "RB2", "RB3", "RB4", "RB5",
        "RH0", "RH1", "RH2",
    ]

    for layer_name in ["NUM", "SYM"]:
        corne_layer = corne_cfg.layer(layer_name)
        sofle_layer = sofle_cfg.layer(layer_name)
        for pos in shared_positions:
            c_val = corne_layer.pos(pos)
            s_val = sofle_layer.pos(pos)
            assert_eq(
                c_val,
                s_val,
                f"Cross-keyboard parity mismatch on {layer_name} {pos}: Corne={c_val}, Sofle={s_val}",
            )

    print("PASS: Cross-keyboard NUM and SYM common geometry parity verified (Corne == Sofle).")

def test_fun_layer(cfg: KeyboardConfig) -> None:
    """Verify FUN layer exact physical grid (F1-F12, system keys, modifiers, and thumbs)."""
    fun = cfg.layer("FUN")

    # Left hand 3x4 F-key grid (mirrors NUM geometry)
    assert_eq(fun.pos("LT4"), "&kp F12", "FUN LT4 must be F12")
    assert_eq(fun.pos("LT3"), "&kp F7", "FUN LT3 must be F7")
    assert_eq(fun.pos("LT2"), "&kp F8", "FUN LT2 must be F8")
    assert_eq(fun.pos("LT1"), "&kp F9", "FUN LT1 must be F9")

    assert_eq(fun.pos("LM4"), "&kp F11", "FUN LM4 must be F11")
    assert_eq(fun.pos("LM3"), "&kp F4", "FUN LM3 must be F4")
    assert_eq(fun.pos("LM2"), "&kp F5", "FUN LM2 must be F5")
    assert_eq(fun.pos("LM1"), "&kp F6", "FUN LM1 must be F6")

    assert_eq(fun.pos("LB4"), "&kp F10", "FUN LB4 must be F10")
    assert_eq(fun.pos("LB3"), "&kp F1", "FUN LB3 must be F1")
    assert_eq(fun.pos("LB2"), "&kp F2", "FUN LB2 must be F2")
    assert_eq(fun.pos("LB1"), "&kp F3", "FUN LB1 must be F3")

    # Left hand outer column system keys
    assert_eq(fun.pos("LT0"), "&kp PRINTSCREEN", "FUN LT0 must be PrintScreen")
    assert_eq(fun.pos("LM0"), "&kp SCROLLLOCK", "FUN LM0 must be ScrollLock")
    assert_eq(fun.pos("LB0"), "&kp PAUSE_BREAK", "FUN LB0 must be Pause/Break")

    # Right hand CapsLock fallback and mirrored modifiers
    assert_eq(fun.pos("RT0"), "&kp CAPSLOCK", "FUN RT0 must be CapsLock fallback")
    assert_eq(fun.pos("RM1"), "&kp RIGHT_SHIFT", "FUN RM1 must be Right Shift")
    assert_eq(fun.pos("RM2"), "&kp RCTRL", "FUN RM2 must be Right Ctrl")
    assert_eq(fun.pos("RM3"), "&kp RIGHT_ALT", "FUN RM3 must be Right Alt")
    assert_eq(fun.pos("RM4"), "&kp RIGHT_GUI", "FUN RM4 must be Right GUI")

    # Left thumbs
    assert_eq(fun.pos("LH2"), "&kp K_APP", "FUN LH2 must be App / Menu key")
    assert_eq(fun.pos("LH1"), "&kp SPACE", "FUN LH1 must be Space")
    assert_eq(fun.pos("LH0"), "&kp TAB", "FUN LH0 must be Tab")

    # Invariant: F1-F12 appear exactly once on the layer
    for i in range(1, 13):
        f_sig = f"&kp F{i}"
        count = fun.bindings.count(f_sig)
        assert_eq(count, 1, f"FUN layer must contain {f_sig} exactly once, found {count}")

    print("PASS: FUN layer F1-F12 grid, system keys, modifiers, and exact occurrence invariants verified.")


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
    """Verify ZMK Studio unlock behavior on ADJUST layer."""
    adjust = cfg.layer("ADJUST")
    assert_eq(adjust.pos("RM0"), "&studio_unlock", "ADJUST RM0 must be &studio_unlock")
    print("PASS: ZMK Studio locking and unlock behavior verified.")


def test_conf_constraints() -> None:
    """Verify corne.conf Kconfig constraints."""
    if not CONF_PATH.exists():
        fail(f"Config file not found: {CONF_PATH}")
    content = CONF_PATH.read_text(encoding="utf-8")
    for bad_symbol in ["CONFIG_ZMK_KSCAN_DEBOUNCE_PRESS_MS", "CONFIG_ZMK_KSCAN_DEBOUNCE_RELEASE_MS", "CONFIG_ZMK_HID_REPORT_TYPE_NKRO"]:
        if bad_symbol in content:
            fail(f"corne.conf must not modify {bad_symbol}")
    print("PASS: corne.conf constraints verified (no debounce or NKRO changes).")


def main() -> None:
    cfg = parse_keymap_file(KEYMAP_PATH, layout="corne")
    test_layer_indices(cfg)
    test_base_layer(cfg)
    test_game_layer(cfg)
    test_game_fn_layer(cfg)
    test_bootloader_shortcuts(cfg)
    test_cross_platform_bindings(cfg)
    test_caps_behavior(cfg)
    test_num_layer(cfg)
    test_sym_layer(cfg)
    test_cross_keyboard_parity(cfg)
    test_fun_layer(cfg)
    test_host_layer_bindings(cfg)
    test_studio_configuration(cfg)
    test_conf_constraints()
    print("\nALL CORNE STATIC KEYMAP INVARIANTS PASSED.")


if __name__ == "__main__":
    main()
