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
    from lib.validation import assert_eq, assert_in, assert_true, fail, is_exactly_true
except ImportError:
    from scripts.lib.keymap_parser import KeyboardConfig, parse_keymap_file
    from scripts.lib.validation import (
        assert_eq,
        assert_in,
        assert_true,
        fail,
        is_exactly_true,
    )
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


def test_recovery_topology_and_destructive_bindings(cfg: KeyboardConfig) -> None:
    """
    Verify same-half independent recovery routing, conditional maintenance layer,
    and strict allowlisting of destructive &bootloader / &sys_reset bindings.
    """
    base = cfg.layer("BASE")
    nav = cfg.layer("NAV")
    num = cfg.layer("NUM")
    adjust = cfg.layer("ADJUST")

    # 1. LEFT SAME-HALF RECOVERY:
    #    BASE LH1 hold activates NAV, NAV LT5 invokes &bootloader.
    #    Both activator (LH1) and trigger (LT5) must reside on physical LEFT half.
    base_lh1 = base.pos("LH1")
    assert_true(
        "L_NAV" in base_lh1,
        f"BASE LH1 must activate NAV layer on hold, got: {base_lh1}",
    )
    assert_eq(nav.pos("LT5"), "&bootloader", "NAV LT5 must be left &bootloader")
    assert_true("LH1".startswith("L"), "NAV activator LH1 must be on the left half")
    assert_true("LT5".startswith("L"), "NAV bootloader LT5 must be on the left half")

    # 2. RIGHT SAME-HALF RECOVERY:
    #    BASE RH1 hold activates NUM, NUM RT5 invokes &bootloader.
    #    Both activator (RH1) and trigger (RT5) must reside on physical RIGHT half.
    base_rh1 = base.pos("RH1")
    assert_true(
        "L_NUM" in base_rh1,
        f"BASE RH1 must activate NUM layer on hold, got: {base_rh1}",
    )
    assert_eq(num.pos("RT5"), "&bootloader", "NUM RT5 must be right &bootloader")
    assert_true("RH1".startswith("R"), "NUM activator RH1 must be on the right half")
    assert_true("RT5".startswith("R"), "NUM bootloader RT5 must be on the right half")

    # 3. FULL MAINTENANCE:
    #    Conditional layer NAV + NUM -> ADJUST with mirrored reset & bootloader controls.
    assert_true(
        len(cfg.conditional_layers) > 0,
        "Keymap must declare conditional layer for ADJUST",
    )
    adjust_cond = next((c for c in cfg.conditional_layers if c.then_layer in ("L_ADJUST", "ADJUST")), None)
    if adjust_cond is None:
        fail("Missing conditional layer targeting ADJUST")
    assert_true(
        set(adjust_cond.if_layers) == {"L_NAV", "L_NUM"},
        f"ADJUST conditional layer must require if-layers <L_NAV L_NUM>, got: {adjust_cond.if_layers}",
    )

    assert_eq(adjust.pos("LT5"), "&bootloader", "ADJUST LT5 must be left &bootloader")
    assert_eq(adjust.pos("LT4"), "&sys_reset", "ADJUST LT4 must be left &sys_reset")
    assert_eq(adjust.pos("RT4"), "&sys_reset", "ADJUST RT4 must be right &sys_reset")
    assert_eq(adjust.pos("RT5"), "&bootloader", "ADJUST RT5 must be right &bootloader")

    # 4. DESTRUCTIVE BINDING ALLOWLISTING:
    #    Scan every position of every layer to ensure no unapproved &bootloader or &sys_reset exists.
    allowed_bootloader = {("NAV", "LT5"), ("NUM", "RT5"), ("ADJUST", "LT5"), ("ADJUST", "RT5")}
    allowed_sys_reset = {("ADJUST", "LT4"), ("ADJUST", "RT4")}

    for layer_name, layer_obj in cfg.layers.items():
        for pos_label, binding in layer_obj.all_by_pos().items():
            if "&bootloader" in binding:
                assert_in(
                    (layer_name, pos_label),
                    allowed_bootloader,
                    f"Disallowed &bootloader binding found at {layer_name} {pos_label}: '{binding}'",
                )
            if "&sys_reset" in binding:
                assert_in(
                    (layer_name, pos_label),
                    allowed_sys_reset,
                    f"Disallowed &sys_reset binding found at {layer_name} {pos_label}: '{binding}'",
                )

    print("PASS: Same-half recovery topology and destructive binding allowlist verified.")


def test_functional_layer_activators_are_consumed(cfg: KeyboardConfig) -> None:
    """
    Verify that all functional layers consume their own activation key (&none)
    so BASE layer-taps do not leak into repeats or transparent fallthrough.
    """
    expected_activators = {
        "MOUSE": ("LH2", "&none"),
        "NAV": ("LH1", "&none"),
        "HOST": ("LH0", "&none"),
        "SYM": ("RH0", "&none"),
        "NUM": ("RH1", "&none"),
        "FUN": ("RH2", "&none"),
        "MEDIA": ("LM5", "&none"),
    }

    for l_name, (pos_label, expected_val) in expected_activators.items():
        actual_val = cfg.layer(l_name).pos(pos_label)
        assert_eq(
            actual_val,
            expected_val,
            f"Functional layer '{l_name}' must consume its activation key at {pos_label} with {expected_val}, got: '{actual_val}'",
        )

    # Also verify ADJUST's two activation thumbs (LH1 and RH1) are consumed with &none
    adjust = cfg.layer("ADJUST")
    assert_eq(adjust.pos("LH1"), "&none", "ADJUST LH1 must be &none to consume left activator")
    assert_eq(adjust.pos("RH1"), "&none", "ADJUST RH1 must be &none to consume right activator")

    print("PASS: Functional-layer activator keys verified consumed (&none) across all layers.")

def test_directional_neio_geometry(cfg: KeyboardConfig) -> None:
    """Verify that NEIO (RM1..RM4) maintains strict Left Down Up Right directional geometry across layers."""
    nav = cfg.layer("NAV")
    mouse = cfg.layer("MOUSE")
    media = cfg.layer("MEDIA")
    host = cfg.layer("HOST")

    # NAV RM1..RM4 = Left Down Up Right
    assert_eq(nav.pos("RM1"), "&kp LEFT", "NAV RM1 must be Left Arrow (&kp LEFT)")
    assert_eq(nav.pos("RM2"), "&kp DOWN", "NAV RM2 must be Down Arrow (&kp DOWN)")
    assert_eq(nav.pos("RM3"), "&kp UP", "NAV RM3 must be Up Arrow (&kp UP)")
    assert_eq(nav.pos("RM4"), "&kp RIGHT", "NAV RM4 must be Right Arrow (&kp RIGHT)")

    # MOUSE RM1..RM4 = MoveLeft MoveDown MoveUp MoveRight
    assert_eq(mouse.pos("RM1"), "&mmv MOVE_LEFT", "MOUSE RM1 must be Move Left")
    assert_eq(mouse.pos("RM2"), "&mmv MOVE_DOWN", "MOUSE RM2 must be Move Down")
    assert_eq(mouse.pos("RM3"), "&mmv MOVE_UP", "MOUSE RM3 must be Move Up")
    assert_eq(mouse.pos("RM4"), "&mmv MOVE_RIGHT", "MOUSE RM4 must be Move Right")

    # MEDIA RM1..RM4 = Prev Vol- Vol+ Next
    assert_eq(media.pos("RM1"), "&kp C_PREVIOUS", "MEDIA RM1 must be C_PREVIOUS")
    assert_eq(media.pos("RM2"), "&kp C_VOLUME_DOWN", "MEDIA RM2 must be C_VOLUME_DOWN")
    assert_eq(media.pos("RM3"), "&kp C_VOLUME_UP", "MEDIA RM3 must be C_VOLUME_UP")
    assert_eq(media.pos("RM4"), "&kp C_NEXT", "MEDIA RM4 must be C_NEXT")

    # HOST directional semantics maintain Left Down Up Right ordering on RM1..RM4 (Focus) and RB1..RB4 (Move)
    assert_eq(host.pos("RM1"), "&kp LC(F13)", "HOST RM1 must be focus_left (&kp LC(F13))")
    assert_eq(host.pos("RM2"), "&kp LC(F14)", "HOST RM2 must be focus_down (&kp LC(F14))")
    assert_eq(host.pos("RM3"), "&kp LC(F15)", "HOST RM3 must be focus_up (&kp LC(F15))")
    assert_eq(host.pos("RM4"), "&kp LC(F16)", "HOST RM4 must be focus_right (&kp LC(F16))")

    assert_eq(host.pos("RB1"), "&kp LC(LS(F13))", "HOST RB1 must be move_left (&kp LC(LS(F13)))")
    assert_eq(host.pos("RB2"), "&kp LC(LS(F14))", "HOST RB2 must be move_down (&kp LC(LS(F14)))")
    assert_eq(host.pos("RB3"), "&kp LC(LS(F15))", "HOST RB3 must be move_up (&kp LC(LS(F15)))")
    assert_eq(host.pos("RB4"), "&kp LC(LS(F16))", "HOST RB4 must be move_right (&kp LC(LS(F16)))")

    print("PASS: NEIO directional navigation geometry verified across NAV, MOUSE, MEDIA, and HOST.")


def test_nav_layer(cfg: KeyboardConfig) -> None:
    """Verify Sofle NAV layer exact physical positions (tabs, app controls, modifiers, NEIO arrows, page navigation)."""
    nav = cfg.layer("NAV")

    # Top row left: Bootloader & Tab Management (LT5..LT0)
    assert_eq(nav.pos("LT5"), "&bootloader", "NAV LT5 must be left &bootloader")
    assert_eq(nav.pos("LT4"), "&kp LC(LA(LS(LG(F16))))", "NAV LT4 must be PrevTab (Hyper+F16)")
    assert_eq(nav.pos("LT3"), "&kp LC(LA(LS(LG(F17))))", "NAV LT3 must be NextTab (Hyper+F17)")
    assert_eq(nav.pos("LT2"), "&kp LC(LA(LS(LG(F18))))", "NAV LT2 must be NewTab (Hyper+F18)")
    assert_eq(nav.pos("LT1"), "&kp LC(LA(LS(LG(F19))))", "NAV LT1 must be CloseTab (Hyper+F19)")
    assert_eq(nav.pos("LT0"), "&kp LC(LA(LS(LG(F20))))", "NAV LT0 must be ReopenTab (Hyper+F20)")

    # Home row left: SelectAll, held modifiers, Save (LM5..LM0)
    assert_eq(nav.pos("LM5"), "&kp LC(LA(LS(LG(F13))))", "NAV LM5 must be Select All (Hyper+F13)")
    assert_eq(nav.pos("LM4"), "&kp LGUI", "NAV LM4 must be plain &kp LGUI")
    assert_eq(nav.pos("LM3"), "&kp LALT", "NAV LM3 must be plain &kp LALT")
    assert_eq(nav.pos("LM2"), "&kp LCTRL", "NAV LM2 must be plain &kp LCTRL")
    assert_eq(nav.pos("LM1"), "&kp LEFT_SHIFT", "NAV LM1 must be plain &kp LEFT_SHIFT")
    assert_eq(nav.pos("LM0"), "&kp LC(LA(LS(LG(F14))))", "NAV LM0 must be Save (Hyper+F14)")

    # Bottom row left: Find, word navigation, Find Next (LB5..LB0)
    assert_eq(nav.pos("LB5"), "&kp LC(LA(LS(LG(F15))))", "NAV LB5 must be Find (Hyper+F15)")
    assert_eq(nav.pos("LB4"), "&kp LC(LA(LS(LG(F21))))", "NAV LB4 must be Word Left (Hyper+F21)")
    assert_eq(nav.pos("LB3"), "&kp LC(LA(LS(LG(F22))))", "NAV LB3 must be Word Right (Hyper+F22)")
    assert_eq(nav.pos("LB2"), "&kp LC(LA(LS(LG(F23))))", "NAV LB2 must be Find Next (Hyper+F23)")
    assert_eq(nav.pos("LB1"), "&none", "NAV LB1 must be &none (spare)")
    assert_eq(nav.pos("LB0"), "&none", "NAV LB0 must be &none (spare)")

    # Top row right: Clipboard & Editing (RT0..RT5)
    assert_eq(nav.pos("RT0"), "&kp F24", "NAV RT0 must be Undo (&kp F24)")
    assert_eq(nav.pos("RT1"), "&kp F22", "NAV RT1 must be Paste (&kp F22)")
    assert_eq(nav.pos("RT2"), "&kp F21", "NAV RT2 must be Copy (&kp F21)")
    assert_eq(nav.pos("RT3"), "&kp F23", "NAV RT3 must be Cut (&kp F23)")
    assert_eq(nav.pos("RT4"), "&kp LC(LA(LS(LG(F24))))", "NAV RT4 must be Redo (Hyper+F24)")
    assert_eq(nav.pos("RT5"), "&none", "NAV RT5 must be &none")

    # Home row right: Caps Word & NEIO Arrow cluster (RM0..RM5)
    assert_eq(nav.pos("RM0"), "&caps_word", "NAV RM0 must be &caps_word")
    assert_eq(nav.pos("RM1"), "&kp LEFT", "NAV RM1 must be &kp LEFT")
    assert_eq(nav.pos("RM2"), "&kp DOWN", "NAV RM2 must be &kp DOWN")
    assert_eq(nav.pos("RM3"), "&kp UP", "NAV RM3 must be &kp UP")
    assert_eq(nav.pos("RM4"), "&kp RIGHT", "NAV RM4 must be &kp RIGHT")
    assert_eq(nav.pos("RM5"), "&none", "NAV RM5 must be &none")

    # Bottom row right: Secondary navigation / paging (RB0..RB5)
    assert_eq(nav.pos("RB0"), "&kp INSERT", "NAV RB0 must be &kp INSERT")
    assert_eq(nav.pos("RB1"), "&kp HOME", "NAV RB1 must be &kp HOME")
    assert_eq(nav.pos("RB2"), "&kp PAGE_DOWN", "NAV RB2 must be &kp PAGE_DOWN")
    assert_eq(nav.pos("RB3"), "&kp PAGE_UP", "NAV RB3 must be &kp PAGE_UP")
    assert_eq(nav.pos("RB4"), "&kp END", "NAV RB4 must be &kp END")
    assert_eq(nav.pos("RB5"), "&none", "NAV RB5 must be &none")

    # Encoders & Thumbs
    assert_eq(nav.pos("LEC"), "&trans", "NAV LEC must be &trans")
    assert_eq(nav.pos("REC"), "&trans", "NAV REC must be &trans")
    assert_eq(nav.pos("LH2"), "&kp ESCAPE", "NAV LH2 must be Escape")
    assert_eq(nav.pos("LH1"), "&none", "NAV LH1 must be &none (NAV held activator consumed)")
    assert_eq(nav.pos("LH0"), "&kp TAB", "NAV LH0 must be Tab")
    assert_eq(nav.pos("RH0"), "&kp ENTER", "NAV RH0 must be Enter")
    assert_eq(nav.pos("RH1"), "&kp BACKSPACE", "NAV RH1 must be Backspace")
    assert_eq(nav.pos("RH2"), "&kp DELETE", "NAV RH2 must be Delete")
    print("PASS: Sofle NAV layer verified (tabs, app controls, held modifiers, NEIO arrows, paging, thumbs).")


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

    # Sensor bindings on MEDIA
    assert_eq(media.sensor_bindings[0], "&inc_dec_kp C_PREVIOUS C_NEXT")
    assert_eq(media.sensor_bindings[1], "&inc_dec_kp C_VOLUME_DOWN C_VOLUME_UP")

    # Semantic editing signals on NAV and MOUSE (RT0..RT4)
    for l_name, l_obj in [("NAV", nav), ("MOUSE", mouse)]:
        assert_eq(l_obj.pos("RT0"), "&kp F24", f"{l_name} RT0 must be Undo (&kp F24)")
        assert_eq(l_obj.pos("RT1"), "&kp F22", f"{l_name} RT1 must be Paste &kp F22)")
        assert_eq(l_obj.pos("RT2"), "&kp F21", f"{l_name} RT2 must be Copy &kp F21)")
        assert_eq(l_obj.pos("RT3"), "&kp F23", f"{l_name} RT3 must be Cut &kp F23)")
        assert_eq(l_obj.pos("RT4"), "&kp LC(LA(LS(LG(F24))))", f"{l_name} RT4 must be Redo (Hyper+F24)")

    print("PASS: Cross-platform bindings verified (Consumer media HID brightness/volume/transport, semantic F21-F24 and Hyper+F24 editing on NAV/MOUSE).")


def test_modifier_behaviors(cfg: KeyboardConfig) -> None:
    """Verify modifier architecture: dedicated &sk on BASE, &skm on NUM/SYM/FUN, plain &kp on NAV."""
    base = cfg.layer("BASE")
    nav = cfg.layer("NAV")
    num = cfg.layer("NUM")
    sym = cfg.layer("SYM")
    fun = cfg.layer("FUN")

    # BASE sticky shift
    assert_eq(base.pos("LB5"), "&sk LSHFT", "BASE LB5 must use dedicated capitalization &sk LSHFT")

    # NAV modifiers must be plain &kp
    assert_eq(nav.pos("LM4"), "&kp LGUI", "NAV LM4 must be plain &kp LGUI")
    assert_eq(nav.pos("LM3"), "&kp LALT", "NAV LM3 must be plain &kp LALT")
    assert_eq(nav.pos("LM2"), "&kp LCTRL", "NAV LM2 must be plain &kp LCTRL")
    assert_eq(nav.pos("LM1"), "&kp LEFT_SHIFT", "NAV LM1 must be plain &kp LEFT_SHIFT")

    # NUM, SYM, FUN must use one-shot modifier &skm on RM1..RM4
    for l_name, l_obj in [("NUM", num), ("SYM", sym), ("FUN", fun)]:
        assert_eq(l_obj.pos("RM1"), "&skm RIGHT_SHIFT", f"{l_name} RM1 must be &skm RIGHT_SHIFT")
        assert_eq(l_obj.pos("RM2"), "&skm RCTRL", f"{l_name} RM2 must be &skm RCTRL")
        assert_eq(l_obj.pos("RM3"), "&skm RIGHT_ALT", f"{l_name} RM3 must be &skm RIGHT_ALT")
        assert_eq(l_obj.pos("RM4"), "&skm RIGHT_GUI", f"{l_name} RM4 must be &skm RIGHT_GUI")

    # Validate skm custom behavior definition in DTS
    assert_in("skm", cfg.behaviors, "DTS missing custom behavior 'skm'")
    skm_beh = cfg.behaviors["skm"]
    assert_eq(skm_beh.compatible, "zmk,behavior-sticky-key", "skm must be compatible with zmk,behavior-sticky-key")
    assert_eq(skm_beh.properties.get("release-after-ms"), ["1000"], "skm release-after-ms must be 1000")
    assert_true(is_exactly_true(skm_beh.properties.get("lazy")), "skm must have lazy property")
    assert_true(is_exactly_true(skm_beh.properties.get("ignore-modifiers")), "skm must have ignore-modifiers property")
    assert_true("quick-release" not in skm_beh.properties, "skm must NOT have quick-release (to allow modifier chaining)")

    print("PASS: Modifier architecture verified (&sk on BASE, &skm on NUM/SYM/FUN rails, plain &kp on NAV, skm behavior properties).")

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

    # Left primary thumbs
    assert_eq(num.pos("LH2"), "&kp PERIOD", "NUM LH2 must be .")
    assert_eq(num.pos("LH1"), "&kp NUMBER_0", "NUM LH1 must be 0")
    assert_eq(num.pos("LH0"), "&kp MINUS", "NUM LH0 must be -")

    # Right hand mirrored modifiers and bootloader
    assert_eq(num.pos("RT5"), "&bootloader", "NUM RT5 must be bootloader")
    assert_eq(num.pos("RM1"), "&skm RIGHT_SHIFT", "NUM RM1 must be Right Shift (&skm)")
    assert_eq(num.pos("RM2"), "&skm RCTRL", "NUM RM2 must be Right Ctrl (&skm)")
    assert_eq(num.pos("RM3"), "&skm RIGHT_ALT", "NUM RM3 must be Right Alt (&skm)")
    assert_eq(num.pos("RM4"), "&skm RIGHT_GUI", "NUM RM4 must be Right GUI (&skm)")

    print("PASS: Sofle NUM Seniply+/operator geometry verified.")


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

    # Left primary thumbs: \ / _
    assert_eq(sym.pos("LH2"), "&kp BACKSLASH", "SYM LH2 must be \\")
    assert_eq(sym.pos("LH1"), "&kp SLASH", "SYM LH1 must be /")
    assert_eq(sym.pos("LH0"), "&kp UNDERSCORE", "SYM LH0 must be _")

    # Right hand mirrored modifiers
    assert_eq(sym.pos("RM1"), "&skm RIGHT_SHIFT", "SYM RM1 must be Right Shift (&skm)")
    assert_eq(sym.pos("RM2"), "&skm RCTRL", "SYM RM2 must be Right Ctrl (&skm)")
    assert_eq(sym.pos("RM3"), "&skm RIGHT_ALT", "SYM RM3 must be Right Alt (&skm)")
    assert_eq(sym.pos("RM4"), "&skm RIGHT_GUI", "SYM RM4 must be Right GUI (&skm)")

    print("PASS: Sofle SYM Seniply+ geometry verified.")


def test_cross_keyboard_parity(sofle_cfg: KeyboardConfig) -> None:
    """
    Verify exact parity between Corne and Sofle across all 42 shared core positions
    for all standard shared layers (BASE, NAV, MOUSE, MEDIA, NUM, SYM, FUN, HOST, ADJUST).
    GAME and GAME_FN are explicitly excluded because gaming architecture intentionally differs.
    """
    corne_keymap_path = REPO_ROOT / "config" / "corne.keymap"
    corne_cfg = parse_keymap_file(corne_keymap_path, layout="corne")

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

    shared_layers = ["BASE", "NAV", "MOUSE", "MEDIA", "NUM", "SYM", "FUN", "HOST", "ADJUST"]

    for layer_name in shared_layers:
        corne_layer = corne_cfg.layer(layer_name)
        sofle_layer = sofle_cfg.layer(layer_name)
        for pos in shared_positions:
            c_val = corne_layer.pos(pos)
            s_val = sofle_layer.pos(pos)
            assert_eq(
                s_val,
                c_val,
                f"Cross-keyboard parity mismatch on {layer_name} {pos}: Corne={c_val}, Sofle={s_val}",
            )

    print(f"PASS: Cross-keyboard common 42-key geometry parity verified across all {len(shared_layers)} shared layers.")

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
    assert_eq(fun.pos("RM1"), "&skm RIGHT_SHIFT", "FUN RM1 must be Right Shift (&skm)")
    assert_eq(fun.pos("RM2"), "&skm RCTRL", "FUN RM2 must be Right Ctrl (&skm)")
    assert_eq(fun.pos("RM3"), "&skm RIGHT_ALT", "FUN RM3 must be Right Alt (&skm)")
    assert_eq(fun.pos("RM4"), "&skm RIGHT_GUI", "FUN RM4 must be Right GUI (&skm)")

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
    test_recovery_topology_and_destructive_bindings(cfg)
    test_functional_layer_activators_are_consumed(cfg)
    test_directional_neio_geometry(cfg)
    test_nav_layer(cfg)
    test_cross_platform_bindings(cfg)
    test_modifier_behaviors(cfg)
    test_num_layer(cfg)
    test_sym_layer(cfg)
    test_cross_keyboard_parity(cfg)
    test_fun_layer(cfg)
    test_host_layer_bindings(cfg)
    test_studio_configuration(cfg)
    print("\nALL SOFLE STATIC KEYMAP INVARIANTS PASSED.")
if __name__ == "__main__":
    main()
