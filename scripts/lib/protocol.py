"""
Semantic Protocol v1 Specification Loader & Mapping Helpers.

Provides typed access to protocol/semantic-v1.yaml and bidirectional mapping
helpers between semantic signals and host/firmware representations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

try:
    from .validation import fail, load_yaml
except ImportError:
    try:
        from lib.validation import fail, load_yaml
    except ImportError:
        from scripts.lib.validation import fail, load_yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROTOCOL_PATH = REPO_ROOT / "protocol" / "semantic-v1.yaml"

MOD_CANONICAL: Dict[str, str] = {
    "ctrl": "ctrl",
    "control": "ctrl",
    "lc": "ctrl",
    "rctrl": "ctrl",
    "lctrl": "ctrl",
    "alt": "alt",
    "option": "alt",
    "la": "alt",
    "lalt": "alt",
    "ralt": "alt",
    "shift": "shift",
    "ls": "shift",
    "lshift": "shift",
    "rshift": "shift",
    "lshft": "shift",
    "rshft": "shift",
    "gui": "gui",
    "cmd": "gui",
    "command": "gui",
    "lg": "gui",
    "lgui": "gui",
    "rgui": "gui",
    "meta": "gui",
    "lmeta": "gui",
    "rmeta": "gui",
}


@dataclass
class SemanticSignal:
    key: str
    modifiers: List[str] = field(default_factory=list)

    @property
    def normalized_key(self) -> str:
        return self.key.upper()

    @property
    def normalized_modifiers(self) -> frozenset[str]:
        return frozenset(
            MOD_CANONICAL[m.lower()]
            for m in self.modifiers
            if m.lower() in MOD_CANONICAL
        )

    @property
    def identity(self) -> tuple[str, frozenset[str]]:
        """Normalized signal identity: (Key, frozenset({modifiers}))."""
        return (self.normalized_key, self.normalized_modifiers)

    @property
    def canonical_str(self) -> str:
        if not self.modifiers:
            return self.key
        mods = "+".join(m.capitalize() for m in self.modifiers)
        return f"{mods}+{self.key}"

    def to_zmk(self) -> str:
        """Convert to ZMK keycode expression (e.g., '&kp LC(LS(F13))')."""
        if not self.modifiers:
            return f"&kp {self.key}"

        mod_map = {
            "ctrl": "LC",
            "shift": "LS",
            "alt": "LA",
            "gui": "LG",
        }
        zmk_mods = [mod_map[m.lower()] for m in self.modifiers if m.lower() in mod_map]
        expr = self.key
        for m in reversed(zmk_mods):
            expr = f"{m}({expr})"
        return f"&kp {expr}"

    def to_glazewm(self) -> str:
        """Convert to GlazeWM binding string (e.g., 'ctrl+shift+f13')."""
        parts = [m.lower() for m in self.modifiers] + [self.key.lower()]
        return "+".join(parts)

    def to_ahk_trigger(self) -> str:
        """Convert to AutoHotkey v2 trigger string (e.g., '^+F13::')."""
        prefix = ""
        for m in self.modifiers:
            if m.lower() == "ctrl":
                prefix += "^"
            elif m.lower() == "shift":
                prefix += "+"
            elif m.lower() == "alt":
                prefix += "!"
            elif m.lower() == "gui":
                prefix += "#"
        return f"{prefix}{self.key}::"

    @classmethod
    def from_zmk(cls, expr: str) -> Optional[SemanticSignal]:
        """Parse a ZMK keycode binding like '&kp LC(LA(LS(LG(F24))))' or '&kp F24'."""
        m = re.match(r"^&kp\s+(.+)$", expr.strip())
        if not m:
            return None
        inner = m.group(1)
        mods: List[str] = []
        while True:
            wrap_m = re.match(r"^([A-Z_]+)\((.+)\)$", inner)
            if wrap_m:
                mod_code = wrap_m.group(1).lower()
                if mod_code in MOD_CANONICAL:
                    mods.append(MOD_CANONICAL[mod_code])
                inner = wrap_m.group(2)
            else:
                break
        key = inner.upper()
        return cls(key=key, modifiers=mods)

    @classmethod
    def from_karabiner(cls, key_code: str, mandatory_mods: List[str]) -> SemanticSignal:
        """Parse Karabiner from.key_code and from.modifiers.mandatory."""
        key = key_code.upper()
        mods = [MOD_CANONICAL[m.lower()] for m in mandatory_mods if m.lower() in MOD_CANONICAL]
        return cls(key=key, modifiers=mods)

    @classmethod
    def from_glazewm(cls, binding: str) -> SemanticSignal:
        """Parse GlazeWM binding string like 'ctrl+shift+f13' or 'f13'."""
        parts = binding.strip().split("+")
        key = parts[-1].upper()
        mods = [MOD_CANONICAL[m.lower()] for m in parts[:-1] if m.lower() in MOD_CANONICAL]
        return cls(key=key, modifiers=mods)

    @classmethod
    def from_ahk(cls, trigger: str) -> Optional[SemanticSignal]:
        """Parse AutoHotkey trigger like '^!+#F24::', '!F13::', or '*F21::'."""
        m = re.match(r"^\*?([\^!+#]*)(F\d{1,2})::$", trigger.strip(), re.IGNORECASE)
        if not m:
            return None
        mod_syms, key = m.group(1), m.group(2).upper()
        mods: List[str] = []
        if "^" in mod_syms:
            mods.append("ctrl")
        if "!" in mod_syms:
            mods.append("alt")
        if "+" in mod_syms:
            mods.append("shift")
        if "#" in mod_syms:
            mods.append("gui")
        return cls(key=key, modifiers=mods)

@dataclass
class SemanticAction:
    id: str
    signal: SemanticSignal
    category: str
    description: str
    host_implementations: Dict[str, str] = field(default_factory=dict)


@dataclass
class ProtocolManifest:
    version: int
    name: str
    actions: Dict[str, SemanticAction]

    def action(self, action_id: str) -> SemanticAction:
        if action_id not in self.actions:
            raise KeyError(f"Action '{action_id}' not found in protocol")
        return self.actions[action_id]

    def all_zmk_signals(self) -> Set[str]:
        return {a.signal.to_zmk() for a in self.actions.values()}

    def all_glazewm_signals(self) -> Set[str]:
        return {a.signal.to_glazewm() for a in self.actions.values()}


def load_protocol(path: Optional[Path] = None) -> ProtocolManifest:
    p = path or PROTOCOL_PATH
    data = load_yaml(p)
    if not isinstance(data, dict):
        fail(f"Invalid protocol YAML root in {p}")

    version = data.get("version", 1)
    name = data.get("name", "Semantic Protocol")
    actions_raw = data.get("actions", {})

    actions = {}
    for action_id, info in actions_raw.items():
        sig_info = info.get("signal", {})
        key = sig_info.get("key", "")
        modifiers = sig_info.get("modifiers", [])
        signal = SemanticSignal(key=key, modifiers=modifiers)

        action = SemanticAction(
            id=action_id,
            signal=signal,
            category=info.get("category", "general"),
            description=info.get("description", ""),
            host_implementations=info.get("host_implementations", {}),
        )
        actions[action_id] = action

    return ProtocolManifest(version=version, name=name, actions=actions)
