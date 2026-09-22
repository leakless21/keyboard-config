"""
Cheatsheet Semantic Model & Binding Resolver.

Transforms parsed ZMK keymaps, protocol definitions, and keymap-drawer presentation
aliases into an intermediate semantic model for deterministic documentation and SVG rendering.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar, Literal, Protocol

try:
    from .keymap_parser import (
        ConditionalLayer,
        KeyboardConfig,
        parse_keymap_file,
    )
    from .protocol import load_protocol
    from .validation import load_yaml
except ImportError:
    try:
        from lib.keymap_parser import (
            ConditionalLayer,
            KeyboardConfig,
            parse_keymap_file,
        )
        from lib.protocol import load_protocol
        from lib.validation import load_yaml
    except ImportError:
        from scripts.lib.keymap_parser import (
            ConditionalLayer,
            KeyboardConfig,
            parse_keymap_file,
        )
        from scripts.lib.protocol import load_protocol
        from scripts.lib.validation import load_yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
KEYMAP_DRAWER_CONFIG_PATH = REPO_ROOT / "keymap_drawer.config.yaml"
CHEATSHEET_CONFIG_PATH = REPO_ROOT / "cheatsheets" / "corne.yaml"


@dataclass
class KeyView:
    """Semantic view of a single key on a layer."""
    position: str
    raw_binding: str
    tap: str | None
    hold: str | None
    kind: Literal["normal", "unused", "transparent", "transition", "system", "modifier", "held_activator"]
    target_layer: str | None = None
    transition_mode: Literal["hold", "momentary", "persistent", "tap"] | None = None
    is_modifier: bool = False
    is_bootloader: bool = False
    is_held_activator: bool = False

@dataclass
class LayerView:
    """Semantic view of an entire keyboard layer."""
    name: str
    index: int
    display_name: str
    description: str
    color: str
    keys: dict[str, KeyView] = field(default_factory=dict)
    key_list: list[KeyView] = field(default_factory=list)
    subtitle: str = ""
    activators: list[tuple[str, str | None, str | None]] = field(default_factory=list)
    def get_key(self, pos: str) -> KeyView:
        if pos not in self.keys:
            raise KeyError(f"Position '{pos}' not found in layer '{self.name}'")
        return self.keys[pos]


@dataclass
class CheatsheetConfig:
    """Loaded presentation configuration from cheatsheets/<keyboard>.yaml."""
    schema_version: int
    keyboard: str
    title: str
    base_layout: str
    colors: dict[str, str]
    descriptions: dict[str, str]


@dataclass
class CheatsheetModel:
    """Complete semantic cheatsheet model ready for SVG / visual rendering."""
    keyboard: str
    title: str
    base_layout: str
    layers: list[LayerView]
    layer_map: dict[str, LayerView]
    conditional_layers: list[ConditionalLayer]
    transition_graph: dict[str, list[tuple[str, str, str]]]  # from_layer -> [(trigger_desc, to_layer, mode)]
    bootloader_positions: list[tuple[str, str, str]]  # [(layer, pos, side)]
    presentation_config: CheatsheetConfig


class CheatsheetGeometry(Protocol):
    """Protocol for keyboard schematic geometry."""
    @property
    def positions(self) -> list[str]:
        ...

    @property
    def left_positions(self) -> list[str]:
        ...

    @property
    def right_positions(self) -> list[str]:
        ...

    def is_left(self, pos: str) -> bool:
        ...

    def is_right(self, pos: str) -> bool:
        ...


class CorneGeometry:
    """Immutable 42-position schematic geometry for Corne keyboard."""

    ORDERED_POSITIONS: ClassVar[list[str]] = [
        # Top row
        "LT5", "LT4", "LT3", "LT2", "LT1", "LT0", "RT0", "RT1", "RT2", "RT3", "RT4", "RT5",
        # Middle (Home) row
        "LM5", "LM4", "LM3", "LM2", "LM1", "LM0", "RM0", "RM1", "RM2", "RM3", "RM4", "RM5",
        # Bottom row
        "LB5", "LB4", "LB3", "LB2", "LB1", "LB0", "RB0", "RB1", "RB2", "RB3", "RB4", "RB5",
        # Thumbs
        "LH2", "LH1", "LH0", "RH0", "RH1", "RH2",
    ]

    LEFT_POSITIONS: ClassVar[list[str]] = [
        "LT5", "LT4", "LT3", "LT2", "LT1", "LT0",
        "LM5", "LM4", "LM3", "LM2", "LM1", "LM0",
        "LB5", "LB4", "LB3", "LB2", "LB1", "LB0",
        "LH2", "LH1", "LH0",
    ]

    RIGHT_POSITIONS: ClassVar[list[str]] = [
        "RT0", "RT1", "RT2", "RT3", "RT4", "RT5",
        "RM0", "RM1", "RM2", "RM3", "RM4", "RM5",
        "RB0", "RB1", "RB2", "RB3", "RB4", "RB5",
        "RH0", "RH1", "RH2",
    ]

    @property
    def positions(self) -> list[str]:
        return list(self.ORDERED_POSITIONS)

    @property
    def left_positions(self) -> list[str]:
        return list(self.LEFT_POSITIONS)

    @property
    def right_positions(self) -> list[str]:
        return list(self.RIGHT_POSITIONS)

    def is_left(self, pos: str) -> bool:
        return pos.startswith("L")

    def is_right(self, pos: str) -> bool:
        return pos.startswith("R")

class SofleGeometry:
    """Immutable 60-position schematic geometry for Sofle keyboard."""

    ORDERED_POSITIONS: ClassVar[list[str]] = [
        # Number Row
        "LN5", "LN4", "LN3", "LN2", "LN1", "LN0", "RN0", "RN1", "RN2", "RN3", "RN4", "RN5",
        # Top Row
        "LT5", "LT4", "LT3", "LT2", "LT1", "LT0", "RT0", "RT1", "RT2", "RT3", "RT4", "RT5",
        # Middle (Home) Row
        "LM5", "LM4", "LM3", "LM2", "LM1", "LM0", "RM0", "RM1", "RM2", "RM3", "RM4", "RM5",
        # Bottom Row & Encoders
        "LB5", "LB4", "LB3", "LB2", "LB1", "LB0", "LEC", "REC", "RB0", "RB1", "RB2", "RB3", "RB4", "RB5",
        # Thumbs
        "LH4", "LH3", "LH2", "LH1", "LH0", "RH0", "RH1", "RH2", "RH3", "RH4",
    ]

    LEFT_POSITIONS: ClassVar[list[str]] = [
        "LN5", "LN4", "LN3", "LN2", "LN1", "LN0",
        "LT5", "LT4", "LT3", "LT2", "LT1", "LT0",
        "LM5", "LM4", "LM3", "LM2", "LM1", "LM0",
        "LB5", "LB4", "LB3", "LB2", "LB1", "LB0", "LEC",
        "LH4", "LH3", "LH2", "LH1", "LH0",
    ]

    RIGHT_POSITIONS: ClassVar[list[str]] = [
        "RN0", "RN1", "RN2", "RN3", "RN4", "RN5",
        "RT0", "RT1", "RT2", "RT3", "RT4", "RT5",
        "RM0", "RM1", "RM2", "RM3", "RM4", "RM5",
        "REC", "RB0", "RB1", "RB2", "RB3", "RB4", "RB5",
        "RH0", "RH1", "RH2", "RH3", "RH4",
    ]

    @property
    def positions(self) -> list[str]:
        return list(self.ORDERED_POSITIONS)

    @property
    def left_positions(self) -> list[str]:
        return list(self.LEFT_POSITIONS)

    @property
    def right_positions(self) -> list[str]:
        return list(self.RIGHT_POSITIONS)

    def is_left(self, pos: str) -> bool:
        return pos.startswith("L")

    def is_right(self, pos: str) -> bool:
        return pos.startswith("R")


# Standard keycode to display text mapping
STANDARD_KP_MAP: dict[str, str] = {
    # Whitespace & Control
    "SPACE": "Space",
    "BACKSPACE": "Bsp",
    "DELETE": "Del",
    "ESCAPE": "Esc",
    "ENTER": "Enter",
    "TAB": "Tab",
    "CAPSLOCK": "Caps Lock",
    "PRINTSCREEN": "PrtSc",
    "SCROLLLOCK": "ScrLk",
    "PAUSE_BREAK": "Pause",
    "K_APP": "Menu",
    "INSERT": "Ins",
    "HOME": "Home",
    "END": "End",
    "PAGE_UP": "PgUp",
    "PAGE_DOWN": "PgDn",
    # Arrows
    "LEFT": "←",
    "DOWN_ARROW": "↓",
    "UP_ARROW": "↑",
    "RIGHT": "→",
    # Modifiers
    "LGUI": "Cmd",
    "LMETA": "Cmd",
    "LALT": "Alt",
    "LCTRL": "Ctrl",
    "LEFT_SHIFT": "Shift",
    "RIGHT_SHIFT": "RShift",
    "RCTRL": "RCtrl",
    "RIGHT_ALT": "RAlt",
    "RIGHT_GUI": "RCmd",
    # Punctuation / Brackets
    "LEFT_BRACKET": "[",
    "RIGHT_BRACKET": "]",
    "LEFT_BRACE": "{",
    "RIGHT_BRACE": "}",
    "LEFT_PARENTHESIS": "(",
    "RIGHT_PARENTHESIS": ")",
    "SEMICOLON": ";",
    "COLON": ":",
    "SQT": "'",
    "GRAVE": "`",
    "TILDE": "~",
    "MINUS": "-",
    "UNDERSCORE": "_",
    "EQUAL": "=",
    "PLUS": "+",
    "BACKSLASH": "\\",
    "PIPE": "|",
    "COMMA": ",",
    "LESS_THAN": "<",
    "GREATER_THAN": ">",
    "DOT": ".",
    "PERIOD": ".",
    "SLASH": "/",
    # Shifted symbols
    "EXCLAMATION": "!",
    "AT_SIGN": "@",
    "HASH": "#",
    "DOLLAR": "$",
    "PERCENT": "%",
    "CARET": "^",
    "AMPERSAND": "&",
    "ASTERISK": "*",
}

# Modifier name normalization
MODIFIER_MAP: dict[str, str] = {
    "LMETA": "Cmd",
    "LGUI": "Cmd",
    "LEFT_ALT": "Alt",
    "LALT": "Alt",
    "LCTRL": "Ctrl",
    "LEFT_SHIFT": "Shift",
    "LSHFT": "Shift",
    "RIGHT_SHIFT": "RShift",
    "RSHFT": "RShift",
    "RCTRL": "RCtrl",
    "RIGHT_ALT": "RAlt",
    "RALT": "RAlt",
    "RIGHT_GUI": "RCmd",
    "RGUI": "RCmd",
}


def load_cheatsheet_config(path: Path | None = None) -> CheatsheetConfig:
    """Load presentation metadata from cheatsheets/<keyboard>.yaml."""
    p = path or CHEATSHEET_CONFIG_PATH
    data = load_yaml(p)
    raw_schema_version = data.get("schema_version", 1)
    if not isinstance(raw_schema_version, int) or isinstance(raw_schema_version, bool):
        raise ValueError(f"Cheatsheet schema_version must be an integer: {raw_schema_version!r}")
    schema_version = raw_schema_version
    keyboard = str(data.get("keyboard", "corne"))
    title = str(data.get("title", "CORNE · ONE-PAGE LAYER CHEATSHEET"))
    base_layout = str(data.get("base_layout", "Colemak-DH"))
    colors = {str(k): str(v) for k, v in data.get("colors", {}).items()}
    descriptions = {str(k): str(v) for k, v in data.get("descriptions", {}).items()}
    return CheatsheetConfig(
        schema_version=schema_version,
        keyboard=keyboard,
        title=title,
        base_layout=base_layout,
        colors=colors,
        descriptions=descriptions,
    )


def load_presentation_aliases(path: Path | None = None) -> dict[str, str]:
    """Extract raw_binding_map from keymap_drawer.config.yaml."""
    p = path or KEYMAP_DRAWER_CONFIG_PATH
    data = load_yaml(p)
    parse_cfg = data.get("parse_config", {})
    raw_map = parse_cfg.get("raw_binding_map", {})
    return {str(k): str(v) for k, v in raw_map.items()}

def normalize_layer_name(raw_layer_ref: str) -> str:
    """Normalize a layer define/reference like 'L_NAV' or '1' to canonical layer name 'NAV'."""
    clean = raw_layer_ref.strip()
    if clean.startswith("L_"):
        return clean[2:]
    return clean


def format_kp_param(param: str) -> str:
    """Format a single keycode parameter string into a readable label."""
    param = param.strip()

    # 1. Exact match in standard map
    if param in STANDARD_KP_MAP:
        return STANDARD_KP_MAP[param]

    # 2. Single letter: Q, W, F, etc.
    if len(param) == 1 and param.isalpha():
        return param.upper()

    # 3. NUMBER_X -> X or NX -> X
    if param.startswith("NUMBER_"):
        return param[7:]
    if re.match(r"^N\d$", param):
        return param[1:]
    # 4. F1-F24 function keys
    if re.match(r"^F\d{1,2}$", param):
        return param

    # 5. Modifiers
    if param in MODIFIER_MAP:
        return MODIFIER_MAP[param]

    return param


def resolve_binding(
    raw_binding: str,
    layer_name: str,
    position: str,
    kb_config: KeyboardConfig,
    aliases: dict[str, str],
) -> KeyView:
    """
    Resolve a raw ZMK binding string into a typed KeyView according to the strict resolver rules:
      1. Exact display alias from keymap_drawer.config.yaml
      2. Layer / hold-tap behavior interpretation
      3. Standard &kp formatting
      4. Device-management behavior formatting
      5. Strict error for anything unknown
    """
    raw = raw_binding.strip()
    tokens = raw.split()
    if not tokens:
        raise ValueError(f"Empty binding at layer '{layer_name}', position '{position}'")

    op = tokens[0]

    # -------------------------------------------------------------------------
    # 1. Exact presentation alias check from keymap_drawer.config.yaml
    # -------------------------------------------------------------------------
    if raw in aliases:
        alias_label = aliases[raw]
        # Check if it's a modifier or system key
        is_mod = raw in ("&kp LEFT_SHIFT", "&kp RIGHT_SHIFT", "&kp LCTRL", "&kp RCTRL", "&kp LALT", "&kp RIGHT_ALT", "&kp LGUI", "&kp RIGHT_GUI")
        return KeyView(
            position=position,
            raw_binding=raw,
            tap=alias_label,
            hold=None,
            kind="system" if raw.startswith(("&studio", "&caps")) else ("modifier" if is_mod else "normal"),
            is_modifier=is_mod,
        )

    # -------------------------------------------------------------------------
    # 2. Transparent & Unused
    # -------------------------------------------------------------------------
    if op == "&trans":
        return KeyView(
            position=position,
            raw_binding=raw,
            tap=None,
            hold=None,
            kind="transparent",
        )

    if op == "&none":
        return KeyView(
            position=position,
            raw_binding=raw,
            tap=None,
            hold=None,
            kind="unused",
        )

    # -------------------------------------------------------------------------
    # 3. Bootloader and Reset
    # -------------------------------------------------------------------------
    if op == "&bootloader":
        return KeyView(
            position=position,
            raw_binding=raw,
            tap="BOOT",
            hold=None,
            kind="system",
            is_bootloader=True,
        )

    if op == "&sys_reset":
        return KeyView(
            position=position,
            raw_binding=raw,
            tap="RESET",
            hold=None,
            kind="system",
        )

    # -------------------------------------------------------------------------
    # 4. Standard Layer Behaviors (&mo, &lt, &to)
    # -------------------------------------------------------------------------
    if op == "&mo":
        if len(tokens) < 2:
            raise ValueError(f"Malformed &mo binding '{raw}' at {layer_name}:{position}")
        target = normalize_layer_name(tokens[1])
        return KeyView(
            position=position,
            raw_binding=raw,
            tap=target,
            hold=None,
            kind="transition",
            target_layer=target,
            transition_mode="momentary",
        )

    if op == "&to":
        if len(tokens) < 2:
            raise ValueError(f"Malformed &to binding '{raw}' at {layer_name}:{position}")
        target = normalize_layer_name(tokens[1])
        return KeyView(
            position=position,
            raw_binding=raw,
            tap=target,
            hold=None,
            kind="transition",
            target_layer=target,
            transition_mode="persistent",
        )

    if op == "&lt":
        if len(tokens) < 3:
            raise ValueError(f"Malformed &lt binding '{raw}' at {layer_name}:{position}")
        target = normalize_layer_name(tokens[1])
        tap_expr = tokens[2]
        tap_label = format_kp_param(tap_expr)
        return KeyView(
            position=position,
            raw_binding=raw,
            tap=tap_label,
            hold=target,
            kind="transition",
            target_layer=target,
            transition_mode="hold",
        )

    # -------------------------------------------------------------------------
    # 5. Sticky Keys (&sk, &skm)
    # -------------------------------------------------------------------------
    if op in ("&sk", "&skm"):
        if len(tokens) < 2:
            raise ValueError(f"Malformed {op} binding '{raw}' at {layer_name}:{position}")
        mod_name = tokens[1]
        mod_label = MODIFIER_MAP.get(mod_name, format_kp_param(mod_name))
        return KeyView(
            position=position,
            raw_binding=raw,
            tap=mod_label,
            hold="Sticky",
            kind="modifier",
            is_modifier=True,
        )
    # -------------------------------------------------------------------------
    # 6. Custom Hold-Tap Behaviors (e.g. host_lt, game_fn_lt, hml, hmr)
    # -------------------------------------------------------------------------
    behavior_name = op.lstrip("&")
    if behavior_name in kb_config.behaviors:
        beh = kb_config.behaviors[behavior_name]
        bindings_prop = beh.properties.get("bindings", [])

        # Generic hold-tap resolution based on behavior definition
        if beh.compatible == "zmk,behavior-hold-tap" and len(bindings_prop) == 2:
            hold_subop = bindings_prop[0].strip("<> ")
            tap_subop = bindings_prop[1].strip("<> ")

            if len(tokens) < 3:
                raise ValueError(f"Hold-tap '{raw}' requires 2 arguments at {layer_name}:{position}")

            param1 = tokens[1]
            param2 = tokens[2]

            # Case A: <&mo>, <&kp> -> Layer tap (e.g. host_lt, game_fn_lt)
            if hold_subop == "&mo" and tap_subop == "&kp":
                target = normalize_layer_name(param1)
                tap_label = format_kp_param(param2)
                return KeyView(
                    position=position,
                    raw_binding=raw,
                    tap=tap_label,
                    hold=target,
                    kind="transition",
                    target_layer=target,
                    transition_mode="hold",
                )

            # Case B: <&kp>, <&kp> -> Mod tap / Home Row Mod (e.g. hml, hmr)
            if hold_subop == "&kp" and tap_subop == "&kp":
                hold_label = MODIFIER_MAP.get(param1, format_kp_param(param1))
                tap_label = format_kp_param(param2)
                return KeyView(
                    position=position,
                    raw_binding=raw,
                    tap=tap_label,
                    hold=hold_label,
                    kind="normal",
                    is_modifier=True,
                )

    # -------------------------------------------------------------------------
    # 7. Device Management & Connectivity Behaviors
    # -------------------------------------------------------------------------
    if op == "&bt" and len(tokens) >= 2:
        bt_sub = tokens[1]
        if bt_sub == "BT_CLR":
            return KeyView(position=position, raw_binding=raw, tap="BT Clear", hold=None, kind="system")
        if bt_sub == "BT_NXT":
            return KeyView(position=position, raw_binding=raw, tap="BT Next", hold=None, kind="system")
        if bt_sub == "BT_PRV":
            return KeyView(position=position, raw_binding=raw, tap="BT Prev", hold=None, kind="system")
        if bt_sub == "BT_SEL" and len(tokens) >= 3:
            try:
                profile_idx = int(tokens[2]) + 1
            except ValueError as exc:
                raise ValueError(f"Malformed BT_SEL binding '{raw}' at {layer_name}:{position}") from exc
            return KeyView(position=position, raw_binding=raw, tap=f"BT {profile_idx}", hold=None, kind="system")

    if op == "&out" and len(tokens) >= 2:
        out_sub = tokens[1]
        if out_sub == "OUT_USB":
            return KeyView(position=position, raw_binding=raw, tap="Out USB", hold=None, kind="system")
        if out_sub == "OUT_BLE":
            return KeyView(position=position, raw_binding=raw, tap="Out BLE", hold=None, kind="system")

    if op == "&ext_power" and len(tokens) >= 2:
        ep_sub = tokens[1]
        if ep_sub == "EP_ON":
            return KeyView(position=position, raw_binding=raw, tap="Ext On", hold=None, kind="system")
        if ep_sub == "EP_OFF":
            return KeyView(position=position, raw_binding=raw, tap="Ext Off", hold=None, kind="system")

    # -------------------------------------------------------------------------
    # 8. Standard &kp formatting
    # -------------------------------------------------------------------------
    if op == "&kp":
        if len(tokens) < 2:
            raise ValueError(f"Malformed &kp binding '{raw}' at {layer_name}:{position}")
        param = tokens[1]

        # Check for nested modified keycodes like LS(F13), LC(F14), LA(F15), LC(LS(F13))
        # Note: All semantic F13-F24 modified combinations should have been caught in aliases!
        # If an unmapped modified key is found:
        mod_match = re.match(r"^([A-Z]{2})\((.+)\)$", param)
        if mod_match:
            mod_prefix = mod_match.group(1)
            inner = mod_match.group(2)
            inner_label = format_kp_param(inner)
            prefix_map = {"LS": "Shift+", "LC": "Ctrl+", "LA": "Alt+", "LG": "Cmd+"}
            return KeyView(
                position=position,
                raw_binding=raw,
                tap=f"{prefix_map.get(mod_prefix, mod_prefix + '+')}{inner_label}",
                hold=None,
                kind="normal",
            )

        tap_label = format_kp_param(param)
        is_mod = param in ("LGUI", "LMETA", "LALT", "LCTRL", "LEFT_SHIFT", "RIGHT_SHIFT", "RCTRL", "RIGHT_ALT", "RIGHT_GUI")
        return KeyView(
            position=position,
            raw_binding=raw,
            tap=tap_label,
            hold=None,
            kind="modifier" if is_mod else "normal",
            is_modifier=is_mod,
        )

    # -------------------------------------------------------------------------
    # 9. Mouse and Pointing Behaviors (&mmv, &msc, &mkp)
    # -------------------------------------------------------------------------
    if op == "&mmv" and len(tokens) >= 2:
        dir_map = {"MOVE_LEFT": "Pointer ←", "MOVE_DOWN": "Pointer ↓", "MOVE_UP": "Pointer ↑", "MOVE_RIGHT": "Pointer →"}
        return KeyView(position=position, raw_binding=raw, tap=dir_map.get(tokens[1], tokens[1]), hold=None, kind="normal")

    if op == "&msc" and len(tokens) >= 2:
        dir_map = {"SCRL_LEFT": "Scroll ←", "SCRL_DOWN": "Scroll ↓", "SCRL_UP": "Scroll ↑", "SCRL_RIGHT": "Scroll →"}
        return KeyView(position=position, raw_binding=raw, tap=dir_map.get(tokens[1], tokens[1]), hold=None, kind="normal")

    if op == "&mkp" and len(tokens) >= 2:
        btn_map = {"MB1": "Left click", "MB2": "Right click", "MB3": "Middle click", "MB4": "Back", "MB5": "Forward"}
        return KeyView(position=position, raw_binding=raw, tap=btn_map.get(tokens[1], tokens[1]), hold=None, kind="normal")

    # -------------------------------------------------------------------------
    # 10. Strict error for anything unknown
    # -------------------------------------------------------------------------
    raise ValueError(
        f"Unknown cheatsheet binding:\n"
        f"  layer: {layer_name}\n"
        f"  position: {position}\n"
        f"  binding: {raw}\n"
        f"Add an explicit display rule before regenerating."
    )


def generate_layer_subtitle(
    layer_name: str,
    layer_idx: int,
    description: str,
    layer_view: LayerView,
    base_layer_view: LayerView | None = None,
    conditional_layers: list[ConditionalLayer] | None = None,
) -> str:
    """
    Generate precise layer subtitle derived from BASE transitions and conditional layers
    rather than hardcoded manual strings.
    """
    if layer_name == "BASE":
        return f"BASE · L{layer_idx}   ({description})"

    # 1. Conditional layers (e.g. ADJUST) derived from keymap if-layers
    if conditional_layers:
        for cl in conditional_layers:
            if normalize_layer_name(cl.then_layer) == layer_name:
                if_names = [normalize_layer_name(src) for src in cl.if_layers]
                return f"{layer_name} · L{layer_idx}   (Hold {' + '.join(if_names)})"

    # 2. Single-activator layers derived from BASE transitions
    if layer_view.activators:
        pos, tap_lbl, _mode = layer_view.activators[0]
        if tap_lbl and tap_lbl != layer_name:
            return f"{layer_name} · L{layer_idx}   (Hold {pos} · {tap_lbl})"
        return f"{layer_name} · L{layer_idx}   (Hold {pos})"
    # 3. Dedicated entry layers
    if layer_name == "GAME":
        return f"GAME · L{layer_idx}   (Via ADJUST)"

    if layer_name == "GAME_FN":
        return f"GAME_FN · L{layer_idx}   (Hold Esc / R-thumb FN)"

    return f"{layer_name} · L{layer_idx}   ({description})"

def build_cheatsheet_model(
    keyboard: str = "corne",
    keymap_path: Path | None = None,
    cheatsheet_config_path: Path | None = None,
    aliases_path: Path | None = None,
    protocol_path: Path | None = None,
    geometry: CheatsheetGeometry | None = None,
) -> CheatsheetModel:
    """
    Construct the intermediate semantic model from firmware keymap, protocol,
    and presentation metadata for a given keyboard (corne or sofle).
    """
    kb = keyboard.lower()
    k_path = keymap_path or (REPO_ROOT / "config" / f"{kb}.keymap")
    c_path = cheatsheet_config_path or (REPO_ROOT / "cheatsheets" / f"{kb}.yaml")
    a_path = aliases_path or KEYMAP_DRAWER_CONFIG_PATH
    p_path = protocol_path or (REPO_ROOT / "protocol" / "semantic-v1.yaml")

    kb_config = parse_keymap_file(k_path, layout=kb)
    config = load_cheatsheet_config(c_path)
    aliases = load_presentation_aliases(a_path)
    # The cheatsheet needs the manifest to be valid, but reads aliases elsewhere.
    load_protocol(p_path)
    geom = geometry or (SofleGeometry() if kb == "sofle" else CorneGeometry())
    layers: list[LayerView] = []
    layer_map: dict[str, LayerView] = {}
    transition_graph: dict[str, list[tuple[str, str, str]]] = {}
    bootloader_positions: list[tuple[str, str, str]] = []

    # Map each layer
    for idx, layer_name in enumerate(kb_config.layer_order):
        parsed_layer = kb_config.layer(layer_name)
        color = config.colors.get(layer_name, "#94a3b8")
        desc = config.descriptions.get(layer_name, layer_name)

        layer_view = LayerView(
            name=layer_name,
            index=idx,
            display_name=parsed_layer.display_name or layer_name,
            description=desc,
            color=color,
        )

        layer_transitions: list[tuple[str, str, str]] = []

        # Iterate all positions defined by geometry
        for pos in geom.positions:
            raw_b = parsed_layer.pos(pos)
            key_view = resolve_binding(
                raw_binding=raw_b,
                layer_name=layer_name,
                position=pos,
                kb_config=kb_config,
                aliases=aliases,
            )
            layer_view.keys[pos] = key_view
            layer_view.key_list.append(key_view)

            # Record transitions
            if key_view.kind == "transition" and key_view.target_layer:
                trigger_desc = f"{pos} ({key_view.tap or key_view.hold})"
                layer_transitions.append((trigger_desc, key_view.target_layer, key_view.transition_mode or "hold"))

            # Record bootloader positions
            if key_view.is_bootloader:
                side = "left" if geom.is_left(pos) else "right"
                bootloader_positions.append((layer_name, pos, side))

        transition_graph[layer_name] = layer_transitions
        layer_map[layer_name] = layer_view
        layers.append(layer_view)

    # Derive activation metadata from BASE transitions
    base_layer = layer_map.get("BASE")
    if base_layer:
        for pos, k_view in base_layer.keys.items():
            if k_view.target_layer and k_view.target_layer in layer_map:
                layer_map[k_view.target_layer].activators.append((pos, k_view.tap, k_view.transition_mode))

    # Present held activators on layers where activation position is consumed (&none)
    for layer_view in layers:
        # Ordinary functional layer activators
        if layer_view.activators and layer_view.name != "BASE":
            for act_pos, _tap_lbl, _mode in layer_view.activators:
                if act_pos in layer_view.keys:
                    curr = layer_view.keys[act_pos]
                    if curr.raw_binding == "&none":
                        held_view = KeyView(
                            position=act_pos,
                            raw_binding=curr.raw_binding,
                            tap=layer_view.name,
                            hold="held",
                            kind="held_activator",
                            is_held_activator=True,
                        )
                        layer_view.keys[act_pos] = held_view

        # ADJUST conditional layer activators (NAV + NUM)
        if layer_view.name == "ADJUST" and kb_config.conditional_layers:
            for cl in kb_config.conditional_layers:
                if normalize_layer_name(cl.then_layer) == "ADJUST":
                    for if_l in cl.if_layers:
                        if_name = normalize_layer_name(if_l)
                        if if_name in layer_map and layer_map[if_name].activators:
                            for act_pos, _tap_lbl, _mode in layer_map[if_name].activators:
                                if act_pos in layer_view.keys and layer_view.keys[act_pos].raw_binding == "&none":
                                    layer_view.keys[act_pos] = KeyView(
                                        position=act_pos,
                                        raw_binding=layer_view.keys[act_pos].raw_binding,
                                        tap=if_name,
                                        hold="held",
                                        kind="held_activator",
                                        is_held_activator=True,
                                    )

        # Rebuild key_list in geometric order
        layer_view.key_list = [layer_view.keys[p] for p in geom.positions]

        # Derive layer subtitle
        layer_view.subtitle = generate_layer_subtitle(
            layer_name=layer_view.name,
            layer_idx=layer_view.index,
            description=layer_view.description,
            layer_view=layer_view,
            base_layer_view=base_layer,
            conditional_layers=kb_config.conditional_layers,
        )
    return CheatsheetModel(
        keyboard=config.keyboard,
        title=config.title,
        base_layout=config.base_layout,
        layers=layers,
        layer_map=layer_map,
        conditional_layers=kb_config.conditional_layers,
        transition_graph=transition_graph,
        bootloader_positions=bootloader_positions,
        presentation_config=config,
    )
