"""Source-backed semantic model for the macOS/OmniWM workflow cheatsheet."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    from .keymap_parser import parse_keymap_file
    from .protocol import ProtocolManifest, load_protocol
    from .validation import load_json, load_toml, load_yaml
except ImportError:
    try:
        from lib.keymap_parser import parse_keymap_file
        from lib.protocol import ProtocolManifest, load_protocol
        from lib.validation import load_json, load_toml, load_yaml
    except ImportError:
        from scripts.lib.keymap_parser import parse_keymap_file
        from scripts.lib.protocol import ProtocolManifest, load_protocol
        from scripts.lib.validation import load_json, load_toml, load_yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

HOST_PRESENTATION_PATH = REPO_ROOT / "cheatsheets" / "macos-omniwm.yaml"
HOST_PROTOCOL_PATH = REPO_ROOT / "protocol" / "semantic-v1.yaml"
HOST_SETTINGS_PATH = REPO_ROOT / "hosts" / "macos" / "omniwm" / "settings.toml"
HOST_LAPTOP_KARABINER_PATH = REPO_ROOT / "hosts" / "macos" / "karabiner" / "laptop-omniwm.json"
HOST_EXTERNAL_KARABINER_PATH = REPO_ROOT / "hosts" / "macos" / "karabiner" / "external-semantic.json"
HOST_CORNE_KEYMAP_PATH = REPO_ROOT / "config" / "corne.keymap"
HOST_ALIASES_PATH = REPO_ROOT / "keymap_drawer.config.yaml"

HOST_CHEATSHEET_INPUTS: Dict[str, Path] = {
    "protocol": HOST_PROTOCOL_PATH,
    "omniwm_settings": HOST_SETTINGS_PATH,
    "laptop_karabiner": HOST_LAPTOP_KARABINER_PATH,
    "external_karabiner": HOST_EXTERNAL_KARABINER_PATH,
    "presentation": HOST_PRESENTATION_PATH,
    # These two inputs supply the user-facing Corne HOST labels.
    "corne_keymap": HOST_CORNE_KEYMAP_PATH,
    "aliases": HOST_ALIASES_PATH,
}

HOST_ACTION_GROUPS: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    (
        "workspaces",
        tuple(f"workspace_{index}" for index in range(1, 6)),
    ),
    (
        "move_workspace",
        tuple(f"move_workspace_{index}" for index in range(1, 6)),
    ),
    ("focus", ("focus_left", "focus_down", "focus_up", "focus_right")),
    ("move", ("move_left", "move_down", "move_up", "move_right")),
    (
        "context",
        ("previous_workspace", "resize_mode", "fullscreen_toggle", "float_toggle"),
    ),
    (
        "desktop",
        (
            "system_launcher",
            "quick_terminal",
            "new_terminal",
            "previous_window",
            "language_toggle",
            "service_mode",
        ),
    ),
)


@dataclass(frozen=True)
class HostWorkspace:
    name: str
    display_name: str
    layout_type: str


@dataclass(frozen=True)
class HostRouting:
    bundle_id: str
    display_name: str
    workspace_name: str
    workspace_display_name: str


@dataclass(frozen=True)
class HostActionGroup:
    key: str
    title: str
    values: Tuple[str, ...]


@dataclass(frozen=True)
class HostMacBookControl:
    chord: str
    label: str
    commands: Tuple[str, ...]
    # Native controls are backed by an OmniWM hotkey binding in settings.toml instead of
    # by an omniwmctl IPC command in the Karabiner adapter. `binding` records the exact
    # OmniWM key string that must match, so the chord cannot drift from the live config.
    native: bool = False
    binding: str = ""


@dataclass(frozen=True)
class HostCheatsheetPresentation:
    schema_version: int
    title: str
    subtitle: str
    routing_labels: Dict[str, str]
    section_titles: Dict[str, str]
    host_group_titles: Dict[str, str]
    macbook_controls: Tuple[HostMacBookControl, ...]
    behavior_notes: Dict[str, str]


@dataclass(frozen=True)
class HostCheatsheetModel:
    presentation: HostCheatsheetPresentation
    workspaces: Tuple[HostWorkspace, ...]
    routing: Tuple[HostRouting, ...]
    host_action_groups: Tuple[HostActionGroup, ...]
    macbook_controls: Tuple[HostMacBookControl, ...]
    behavior_notes: Dict[str, str]


def _string_map(value: Any) -> Dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {str(key): str(item) for key, item in value.items()}


def load_host_presentation(path: Path = HOST_PRESENTATION_PATH) -> HostCheatsheetPresentation:
    """Load presentation-only metadata for the host cheatsheet."""
    data = load_yaml(path)
    if not isinstance(data, dict):
        raise ValueError(f"Host cheatsheet presentation must be a mapping: {path}")

    controls: List[HostMacBookControl] = []
    for index, raw_control in enumerate(data.get("macbook_controls", [])):
        if not isinstance(raw_control, dict):
            raise ValueError(f"MacBook control #{index + 1} must be a mapping")
        commands = raw_control.get("commands", [])
        if not isinstance(commands, list) or not commands:
            raise ValueError(f"MacBook control #{index + 1} must list at least one command")
        native = bool(raw_control.get("native", False))
        binding = str(raw_control.get("binding", ""))
        if native and not binding:
            raise ValueError(
                f"MacBook control #{index + 1} is native and must declare the OmniWM 'binding' it represents"
            )
        controls.append(
            HostMacBookControl(
                chord=str(raw_control.get("chord", "")),
                label=str(raw_control.get("label", "")),
                commands=tuple(str(command) for command in commands),
                native=native,
                binding=binding,
            )
        )

    return HostCheatsheetPresentation(
        schema_version=int(data.get("schema_version", 1)),
        title=str(data.get("title", "macOS · OMNIWM WORKFLOW CHEATSHEET")),
        subtitle=str(data.get("subtitle", "")),
        routing_labels=_string_map(data.get("routing_labels", {})),
        section_titles=_string_map(data.get("section_titles", {})),
        host_group_titles=_string_map(data.get("host_group_titles", {})),
        macbook_controls=tuple(controls),
        behavior_notes=_string_map(data.get("behavior_notes", {})),
    )


def _workspace_model(settings: Dict[str, Any]) -> Tuple[HostWorkspace, ...]:
    workspaces = settings.get("workspaces", [])
    if not isinstance(workspaces, list):
        raise ValueError("OmniWM settings must contain a workspaces array")
    return tuple(
        HostWorkspace(
            name=str(workspace.get("name", "")),
            display_name=str(workspace.get("displayName", "")),
            layout_type=str(workspace.get("layoutType", "")),
        )
        for workspace in workspaces
        if isinstance(workspace, dict)
    )


def _routing_model(
    settings: Dict[str, Any],
    workspaces: Tuple[HostWorkspace, ...],
    presentation: HostCheatsheetPresentation,
) -> Tuple[HostRouting, ...]:
    workspace_by_name = {workspace.name: workspace for workspace in workspaces}
    workspace_order = {workspace.name: index for index, workspace in enumerate(workspaces)}
    routes: List[Tuple[int, HostRouting]] = []

    for index, rule in enumerate(settings.get("appRules", [])):
        if not isinstance(rule, dict) or "assignToWorkspace" not in rule:
            continue
        bundle_id = str(rule.get("bundleId", ""))
        workspace_name = str(rule.get("assignToWorkspace", ""))
        if workspace_name not in workspace_by_name:
            raise ValueError(
                f"App rule for {bundle_id} targets undefined workspace {workspace_name!r}"
            )
        workspace = workspace_by_name[workspace_name]
        routes.append(
            (
                index,
                HostRouting(
                    bundle_id=bundle_id,
                    display_name=presentation.routing_labels.get(bundle_id, bundle_id),
                    workspace_name=workspace_name,
                    workspace_display_name=workspace.display_name,
                ),
            )
        )

    routes.sort(key=lambda item: (workspace_order[item[1].workspace_name], item[0]))
    return tuple(route for _index, route in routes)


def _host_action_groups(
    manifest: ProtocolManifest,
    host_bindings: set[str],
    aliases: Dict[str, str],
    presentation: HostCheatsheetPresentation,
) -> Tuple[HostActionGroup, ...]:
    groups: List[HostActionGroup] = []
    for group_key, action_ids in HOST_ACTION_GROUPS:
        labels: List[str] = []
        for action_id in action_ids:
            raw_binding = manifest.action(action_id).signal.to_zmk()
            if raw_binding not in host_bindings:
                raise ValueError(
                    f"Corne HOST layer is missing protocol binding {raw_binding!r} for {action_id}"
                )
            if raw_binding not in aliases:
                raise ValueError(
                    f"Presentation aliases are missing Corne HOST binding {raw_binding!r}"
                )
            labels.append(aliases[raw_binding])

        if group_key in ("move_workspace", "focus", "move"):
            prefixes = {
                "move_workspace": "Move→",
                "focus": "Focus ",
                "move": "Move ",
            }
            prefix = prefixes[group_key]
            labels = [label[len(prefix):] if label.startswith(prefix) else label for label in labels]

        groups.append(
            HostActionGroup(
                key=group_key,
                title=presentation.host_group_titles.get(group_key, group_key),
                values=tuple(labels),
            )
        )
    return tuple(groups)


def _laptop_shell_commands(data: Dict[str, Any]) -> Tuple[str, ...]:
    commands: List[str] = []
    for rule in data.get("rules", []):
        if not isinstance(rule, dict):
            continue
        for manipulator in rule.get("manipulators", []):
            if not isinstance(manipulator, dict):
                continue
            for event in manipulator.get("to", []):
                if isinstance(event, dict) and "shell_command" in event:
                    commands.append(str(event["shell_command"]))
    return tuple(commands)


def _validate_macbook_controls(
    controls: Tuple[HostMacBookControl, ...],
    laptop_data: Dict[str, Any],
    settings_data: Dict[str, Any],
) -> None:
    shell_commands = _laptop_shell_commands(laptop_data)
    hotkey_bindings = {
        str(hotkey.get("id")): str(hotkey.get("binding", ""))
        for hotkey in settings_data.get("hotkeys", [])
        if isinstance(hotkey, dict) and "id" in hotkey
    }
    for control in controls:
        if control.native:
            # Native chords are OmniWM hotkeys and never pass through the Karabiner
            # adapter, so they are tracked against settings.toml rather than the adapter.
            for command in control.commands:
                if command not in hotkey_bindings:
                    raise ValueError(
                        f"MacBook control {control.chord!r} is not backed by an OmniWM hotkey id: {command!r}"
                    )
                actual = hotkey_bindings[command]
                if actual != control.binding:
                    raise ValueError(
                        f"MacBook control {control.chord!r} declares binding {control.binding!r} but "
                        f"OmniWM hotkey {command!r} is bound to {actual!r}"
                    )
            continue
        missing = [
            command
            for command in control.commands
            if not any(command in shell_command for shell_command in shell_commands)
        ]
        if missing:
            raise ValueError(
                f"MacBook control {control.chord!r} is not backed by laptop OmniWM IPC commands: {missing}"
            )


def build_host_cheatsheet_model() -> HostCheatsheetModel:
    """Build a host reference model from the repository's current configuration."""
    presentation = load_host_presentation()
    settings = load_toml(HOST_SETTINGS_PATH)
    protocol = load_protocol(HOST_PROTOCOL_PATH)
    laptop_data = load_json(HOST_LAPTOP_KARABINER_PATH)
    # Load the external bridge as a required source input. Raw WM actions must
    # remain absent from it, but it still participates in the freshness contract.
    load_json(HOST_EXTERNAL_KARABINER_PATH)
    keymap = parse_keymap_file(HOST_CORNE_KEYMAP_PATH, layout="corne")
    aliases_data = load_yaml(HOST_ALIASES_PATH)
    aliases = {
        str(key): str(value)
        for key, value in aliases_data.get("parse_config", {}).get("raw_binding_map", {}).items()
    }

    workspaces = _workspace_model(settings)
    routing = _routing_model(settings, workspaces, presentation)
    host_bindings = set(keymap.layer("HOST").bindings)
    host_action_groups = _host_action_groups(protocol, host_bindings, aliases, presentation)
    _validate_macbook_controls(presentation.macbook_controls, laptop_data, settings)

    return HostCheatsheetModel(
        presentation=presentation,
        workspaces=workspaces,
        routing=routing,
        host_action_groups=host_action_groups,
        macbook_controls=presentation.macbook_controls,
        behavior_notes=presentation.behavior_notes,
    )
