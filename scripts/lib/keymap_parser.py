"""
Structural ZMK Keymap & DeviceTree Parser.

Provides typed, position-aware parsing of ZMK DTS keymap files for Corne (42 keys)
and Sofle (60 keys + rotary encoders).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Positional geometry for Corne (42 keys: 3x6 alphas + 3-key thumbs per side)
CORNE_POSITIONS: dict[str, int] = {
    # Left Hand - Top Row
    "LT5": 0, "LT4": 1, "LT3": 2, "LT2": 3, "LT1": 4, "LT0": 5,
    # Right Hand - Top Row
    "RT0": 6, "RT1": 7, "RT2": 8, "RT3": 9, "RT4": 10, "RT5": 11,
    # Left Hand - Middle (Home) Row
    "LM5": 12, "LM4": 13, "LM3": 14, "LM2": 15, "LM1": 16, "LM0": 17,
    # Right Hand - Middle (Home) Row
    "RM0": 18, "RM1": 19, "RM2": 20, "RM3": 21, "RM4": 22, "RM5": 23,
    # Left Hand - Bottom Row
    "LB5": 24, "LB4": 25, "LB3": 26, "LB2": 27, "LB1": 28, "LB0": 29,
    # Right Hand - Bottom Row
    "RB0": 30, "RB1": 31, "RB2": 32, "RB3": 33, "RB4": 34, "RB5": 35,
    # Thumbs (Left to Right)
    "LH2": 36, "LH1": 37, "LH0": 38,
    "RH0": 39, "RH1": 40, "RH2": 41,
}

# Positional geometry for Sofle (60 keys: number row, 3x6 alphas, encoders, 5-key thumbs)
SOFLE_POSITIONS: dict[str, int] = {
    # Number Row (Left 0..5, Right 6..11)
    "LN5": 0, "LN4": 1, "LN3": 2, "LN2": 3, "LN1": 4, "LN0": 5,
    "RN0": 6, "RN1": 7, "RN2": 8, "RN3": 9, "RN4": 10, "RN5": 11,
    # Top Row (Left 12..17, Right 18..23)
    "LT5": 12, "LT4": 13, "LT3": 14, "LT2": 15, "LT1": 16, "LT0": 17,
    "RT0": 18, "RT1": 19, "RT2": 20, "RT3": 21, "RT4": 22, "RT5": 23,
    # Middle (Home) Row (Left 24..29, Right 30..35)
    "LM5": 24, "LM4": 25, "LM3": 26, "LM2": 27, "LM1": 28, "LM0": 29,
    "RM0": 30, "RM1": 31, "RM2": 32, "RM3": 33, "RM4": 34, "RM5": 35,
    # Bottom Row & Encoders (Left 36..41, Encoders 42..43, Right 44..49)
    "LB5": 36, "LB4": 37, "LB3": 38, "LB2": 39, "LB1": 40, "LB0": 41,
    "LEC": 42, "REC": 43,
    "RB0": 44, "RB1": 45, "RB2": 46, "RB3": 47, "RB4": 48, "RB5": 49,
    # Thumbs (Left 50..54, Right 55..59)
    "LH4": 50, "LH3": 51, "LH2": 52, "LH1": 53, "LH0": 54,
    "RH0": 55, "RH1": 56, "RH2": 57, "RH3": 58, "RH4": 59,
}


@dataclass
class Layer:
    """Represents a single parsed keymap layer with exact positional mapping."""
    name: str
    label: str
    display_name: str
    bindings: list[str]
    sensor_bindings: list[str] = field(default_factory=list)
    pos_map: dict[str, int] = field(default_factory=dict)

    def pos(self, key_label_or_idx: str | int) -> str:
        """Return the exact binding expression at a given symbolic key label or 0-based index."""
        if isinstance(key_label_or_idx, int):
            idx = key_label_or_idx
        else:
            if key_label_or_idx not in self.pos_map:
                raise KeyError(f"Unknown position label '{key_label_or_idx}' for layer '{self.name}'")
            idx = self.pos_map[key_label_or_idx]
        if idx < 0 or idx >= len(self.bindings):
            raise IndexError(f"Position index {idx} out of range for layer '{self.name}' ({len(self.bindings)} keys)")
        return self.bindings[idx]

    def find_binding_positions(self, binding_pattern: str) -> list[str]:
        """Return list of symbolic position labels matching a regex pattern."""
        rev_map = {v: k for k, v in self.pos_map.items()}
        matches = []
        for idx, b in enumerate(self.bindings):
            if re.search(binding_pattern, b):
                matches.append(rev_map.get(idx, f"INDEX_{idx}"))
        return matches

    def all_by_pos(self) -> dict[str, str]:
        """Return mapping of all symbolic positions to their binding expressions."""
        rev_map = {v: k for k, v in self.pos_map.items()}
        return {rev_map[idx]: self.bindings[idx] for idx in range(len(self.bindings))}


@dataclass
class Behavior:
    """Represents a parsed ZMK custom behavior definition."""
    name: str
    node_name: str
    compatible: str
    properties: dict[str, Any]


@dataclass
class ConditionalLayer:
    """Represents a parsed conditional layer rule."""
    name: str
    if_layers: list[str]
    then_layer: str


@dataclass
class KeyboardConfig:
    """Root configuration object parsed from a ZMK DTS keymap file."""
    layout: str
    defines: dict[str, int]
    behaviors: dict[str, Behavior]
    conditional_layers: list[ConditionalLayer]
    layers: dict[str, Layer]
    layer_order: list[str]
    raw_content: str

    def layer(self, name: str) -> Layer:
        """Retrieve a Layer by name."""
        if name not in self.layers:
            raise KeyError(f"Layer '{name}' not found. Available layers: {list(self.layers.keys())}")
        return self.layers[name]


def tokenize_bindings(text: str) -> list[str]:
    """
    Tokenize ZMK DTS bindings into individual binding expressions.

    In ZMK DTS syntax, each binding in the <...> array begins with an ampersand (&)
    behavior reference (e.g. `&kp ESCAPE`, `&host_lt L_HOST TAB`, `&kp LC(LS(F13))`).
    """
    cleaned = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    cleaned = re.sub(r'//.*', '', cleaned)
    tokens = cleaned.split()
    bindings = []
    current: list[str] = []
    for tok in tokens:
        if tok.startswith('&'):
            if current:
                bindings.append(' '.join(current))
            current = [tok]
        else:
            current.append(tok)
    if current:
        bindings.append(' '.join(current))
    return bindings


def parse_keymap_content(content: str, layout: str | None = None) -> KeyboardConfig:
    """Parse DTS keymap content string into structured KeyboardConfig."""
    if layout is None:
        if "key-labels/sofle.h" in content or "REC" in content or "LN0" in content:
            layout = "sofle"
        else:
            layout = "corne"

    pos_map = SOFLE_POSITIONS if layout == "sofle" else CORNE_POSITIONS
    expected_key_count = 60 if layout == "sofle" else 42

    # 1. Parse #define integer constants (decimal, hex, binary, or octal literals)
    defines = {}
    value_pattern = r"(?:0[xX][0-9a-fA-F]+|0[bB][01]+|0[oO][0-7]+|\d+)"
    for m in re.finditer(rf'#define\s+(\w+)\s+({value_pattern})', content):
        raw_value = m.group(2)
        # int(raw, 0) rejects values with a leading zero such as "08", so pick the base
        # from the prefix instead. A bare (\d+) capture would read 0x1F as 0.
        base = {"0x": 16, "0b": 2, "0o": 8}.get(raw_value[:2].lower(), 10)
        # int() also rejects absurdly long digit strings (CPython's 4300-digit
        # str->int limit), so fail with the offending define name.
        try:
            defines[m.group(1)] = int(raw_value, base)
        except ValueError as exc:
            raise ValueError(f"Malformed #define value for {m.group(1)}: {raw_value!r}") from exc

    # 2. Parse custom behaviors
    def extract_dts_block(text: str, block_name: str) -> str:
        pattern = rf'\b{block_name}\s*\{{'
        m = re.search(pattern, text)
        if not m:
            return ""
        start = m.end() - 1
        depth = 0
        for idx in range(start, len(text)):
            if text[idx] == '{':
                depth += 1
            elif text[idx] == '}':
                depth -= 1
                if depth == 0:
                    return text[start + 1:idx]
        return ""

    # 2. Parse custom behaviors
    behaviors = {}
    b_body = extract_dts_block(content, "behaviors")
    if b_body:
        for m in re.finditer(r'(\w+):\s*(\w+)\s*\{([^\{\}]+(?:\{[^\{\}]*\}[^\{\}]*)*)\};', b_body, re.DOTALL):
            b_name = m.group(1)
            b_node = m.group(2)
            b_props_text = m.group(3)
            props: dict[str, Any] = {}
            clean_props_text = re.sub(r'/\*.*?\*/', '', b_props_text, flags=re.DOTALL)
            for stmt in clean_props_text.split(';'):
                stmt = stmt.strip()
                if not stmt or stmt.startswith('//'):
                    continue
                if '=' in stmt:
                    k, v = stmt.split('=', 1)
                    k = k.strip()
                    v = v.strip()
                    if '<' in v and '>' in v:
                        bracket_items = re.findall(r'<([^>]+)>', v)
                        if bracket_items:
                            if len(bracket_items) > 1 or ',' in v:
                                items = [f"<{it.strip()}>" for it in bracket_items]
                                props[k] = items
                            else:
                                props[k] = bracket_items[0].split()
                    else:
                        props[k] = v.strip('" ')
                else:
                    props[stmt] = True
            behaviors[b_name] = Behavior(
                name=b_name,
                node_name=b_node,
                compatible=props.get('compatible', ''),
                properties=props
            )

    # 3. Parse conditional layers
    conditional_layers = []
    c_body = extract_dts_block(content, "conditional_layers")
    if c_body:
        for m in re.finditer(r'(\w+)\s*\{([^\{\}]+)\};', c_body, re.DOTALL):
            c_name = m.group(1)
            c_block = m.group(2)
            if_m = re.search(r'if-layers\s*=\s*<([^>]+)>;', c_block)
            then_m = re.search(r'then-layer\s*=\s*<([^>]+)>;', c_block)
            if if_m and then_m:
                if_layers = if_m.group(1).split()
                then_layer = then_m.group(1).strip()
                conditional_layers.append(ConditionalLayer(name=c_name, if_layers=if_layers, then_layer=then_layer))

    # 4. Parse keymap and layer blocks
    km_body = extract_dts_block(content, "keymap")
    if not km_body:
        raise ValueError("Could not find 'keymap {' block in DTS")

    layers = {}
    layer_order = []

    layer_matches = re.finditer(
        r'(\w+)\s*\{([^\{\}]+(?:\{[^\{\}]*\}[^\{\}]*)*)\};',
        km_body,
        re.DOTALL
    )

    for lm in layer_matches:
        layer_name = lm.group(1)
        layer_body = lm.group(2)

        b_match = re.search(r'bindings\s*=\s*<([^>]+)>', layer_body, re.DOTALL)
        if not b_match:
            continue

        label_m = re.search(r'label\s*=\s*"([^"]+)"', layer_body)
        label = label_m.group(1) if label_m else layer_name

        display_m = re.search(r'display-name\s*=\s*"([^"]+)"', layer_body)
        display_name = display_m.group(1) if display_m else label

        bindings = tokenize_bindings(b_match.group(1))
        if len(bindings) != expected_key_count:
            raise ValueError(
                f"Layer '{layer_name}' in {layout} has {len(bindings)} bindings, expected {expected_key_count}"
            )

        sensor_bindings = []
        sb_match = re.search(r'sensor-bindings\s*=\s*(.*?);', layer_body, re.DOTALL)
        if sb_match:
            sb_clean = re.sub(r'/\*.*?\*/', '', sb_match.group(1), flags=re.DOTALL)
            sb_clean = re.sub(r'//.*', '', sb_clean)
            sensor_bindings = re.findall(r'<([^>]+)>', sb_clean)

        layer_obj = Layer(
            name=layer_name,
            label=label,
            display_name=display_name,
            bindings=bindings,
            sensor_bindings=sensor_bindings,
            pos_map=pos_map
        )
        layers[layer_name] = layer_obj
        layer_order.append(layer_name)

    return KeyboardConfig(
        layout=layout,
        defines=defines,
        behaviors=behaviors,
        conditional_layers=conditional_layers,
        layers=layers,
        layer_order=layer_order,
        raw_content=content
    )


def parse_keymap_file(path: str | Path, layout: str | None = None) -> KeyboardConfig:
    """Read and parse a keymap file from path."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Keymap file not found: {path}")
    return parse_keymap_content(p.read_text(encoding="utf-8"), layout=layout)
