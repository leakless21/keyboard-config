"""Deterministic A4 landscape SVG renderer for the macOS/OmniWM reference."""

from __future__ import annotations

import html

try:
    from .host_cheatsheet import HostCheatsheetModel
except ImportError:
    try:
        from lib.host_cheatsheet import HostCheatsheetModel
    except ImportError:
        from scripts.lib.host_cheatsheet import HostCheatsheetModel

PAGE_WIDTH = 2970
PAGE_HEIGHT = 2100
MARGIN = 70
COLUMN_GAP = 30
LEFT_WIDTH = 1370
RIGHT_X = MARGIN + LEFT_WIDTH + COLUMN_GAP
RIGHT_WIDTH = PAGE_WIDTH - MARGIN - RIGHT_X
HEADER_BOTTOM = 145
TOP_Y = 175
WORKSPACE_HEIGHT = 650
LOWER_Y = TOP_Y + WORKSPACE_HEIGHT + 30
LOWER_HEIGHT = PAGE_HEIGHT - MARGIN - LOWER_Y
MACBOOK_HEIGHT = 990
BEHAVIOR_Y = TOP_Y + MACBOOK_HEIGHT + 30
BEHAVIOR_HEIGHT = PAGE_HEIGHT - MARGIN - BEHAVIOR_Y

COLOR_BG = "#f8fafc"
COLOR_PANEL = "#ffffff"
COLOR_BORDER = "#cbd5e1"
COLOR_TEXT = "#0f172a"
COLOR_MUTED = "#475569"
COLOR_SUBTLE = "#64748b"
COLOR_ACCENT = "#4f46e5"
COLOR_WEB = "#0284c7"
COLOR_DEV = "#6366f1"
COLOR_COMMS = "#c026d3"
COLOR_RUN = "#db2777"
COLOR_AUX = "#64748b"


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def text(x: float, y: float, value: object, class_name: str = "body", fill: str | None = None) -> str:
    fill_attr = f' fill="{fill}"' if fill else ""
    return f'  <text x="{x:.1f}" y="{y:.1f}" class="{class_name}"{fill_attr}>{escape(value)}</text>'


def panel(x: float, y: float, width: float, height: float, title: str, subtitle: str = "") -> list[str]:
    out = [
        f'  <g class="panel" data-panel="{escape(title)}">',
        f'    <rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height:.1f}" rx="16" fill="{COLOR_PANEL}" stroke="{COLOR_BORDER}" stroke-width="2" />',
        f'    <rect x="{x + 24:.1f}" y="{y + 25:.1f}" width="7" height="38" rx="3.5" fill="{COLOR_ACCENT}" />',
        text(x + 52, y + 53, title, "panel-title"),
    ]
    if subtitle:
        out.append(text(x + 52, y + 83, subtitle, "panel-subtitle"))
    return out


def finish_panel(out: list[str]) -> None:
    out.append("  </g>")


def layout_label(layout_type: str) -> str:
    return layout_type[:1].upper() + layout_type[1:]


def workspace_color(name: str) -> str:
    return {
        "1": COLOR_WEB,
        "2": COLOR_DEV,
        "3": COLOR_COMMS,
        "4": COLOR_RUN,
        "5": COLOR_AUX,
    }.get(name, COLOR_ACCENT)


def render_workspace_panel(model: HostCheatsheetModel) -> str:
    x, y, width, height = MARGIN, TOP_Y, LEFT_WIDTH, WORKSPACE_HEIGHT
    out = panel(
        x,
        y,
        width,
        height,
        model.presentation.section_titles.get("workspace_model", "WORKSPACE MODEL"),
        "Persistent workspaces and deliberate new-window defaults",
    )

    table_x = x + 28
    table_y = y + 108
    row_height = 58
    columns = (table_x, table_x + 240, table_x + 845)
    out.append(text(columns[0], table_y, "WORKSPACE", "table-header"))
    out.append(text(columns[1], table_y, "ROLE", "table-header"))
    out.append(text(columns[2], table_y, "LAYOUT", "table-header"))

    for index, workspace in enumerate(model.workspaces):
        row_y = table_y + 25 + index * row_height
        fill = "#f8fafc" if index % 2 == 0 else "#ffffff"
        out.append(
            f'    <rect x="{table_x:.1f}" y="{row_y - 23:.1f}" width="{width - 56:.1f}" height="{row_height:.1f}" rx="7" fill="{fill}" />'
        )
        out.append(
            f'    <circle cx="{columns[0] + 10:.1f}" cy="{row_y - 5:.1f}" r="6" fill="{workspace_color(workspace.name)}" />'
        )
        out.append(text(columns[0] + 28, row_y, f"{workspace.name} {workspace.display_name}", "table-value"))
        role = {
            "WEB": "Browser / research",
            "DEV": "Editor / development",
            "COMMS": "Chat / email / meetings",
            "RUN": "Running apps / testing",
            "AUX": "Miscellaneous",
        }.get(workspace.display_name, workspace.display_name)
        out.append(text(columns[1], row_y, role, "table-value"))
        out.append(text(columns[2], row_y, layout_label(workspace.layout_type), "table-value"))

    routing_y = table_y + 25 + len(model.workspaces) * row_height + 24
    out.append(text(table_x, routing_y, model.presentation.section_titles.get("routing", "CONSERVATIVE ROUTING"), "small-header", COLOR_ACCENT))
    grouped: dict[str, list[str]] = {workspace.name: [] for workspace in model.workspaces}
    for route in model.routing:
        grouped.setdefault(route.workspace_name, []).append(route.display_name)
    for index, workspace in enumerate(model.workspaces):
        names = grouped.get(workspace.name, [])
        if not names:
            continue
        out.append(
            text(
                table_x,
                routing_y + 32 + index * 30,
                f"{' / '.join(names)} → {workspace.display_name}",
                "routing-value",
                workspace_color(workspace.name),
            )
        )

    finish_panel(out)
    return "\n".join(out)


def render_macbook_panel(model: HostCheatsheetModel) -> str:
    x, y, width, height = RIGHT_X, TOP_Y, RIGHT_WIDTH, MACBOOK_HEIGHT
    out = panel(
        x,
        y,
        width,
        height,
        model.presentation.section_titles.get("macbook", "MACBOOK EQUIVALENTS"),
        "Option-held shortcuts through the OmniWM IPC adapter",
    )

    row_x = x + 34
    row_y = y + 116
    row_height = 67
    chord_x = row_x + 10
    label_x = row_x + 475
    out.append(text(chord_x, row_y, "CHORD", "table-header"))
    out.append(text(label_x, row_y, "ACTION", "table-header"))

    for index, control in enumerate(model.macbook_controls):
        current_y = row_y + 34 + index * row_height
        fill = "#f8fafc" if index % 2 == 0 else "#ffffff"
        out.append(
            f'    <rect x="{row_x:.1f}" y="{current_y - 27:.1f}" width="{width - 68:.1f}" height="{row_height:.1f}" rx="7" fill="{fill}" />'
        )
        out.append(text(chord_x, current_y, control.chord, "shortcut"))
        out.append(text(label_x, current_y, control.label, "body"))

    finish_panel(out)
    return "\n".join(out)


def render_corne_panel(model: HostCheatsheetModel) -> str:
    x, y, width, height = MARGIN, LOWER_Y, LEFT_WIDTH, LOWER_HEIGHT
    out = panel(
        x,
        y,
        width,
        height,
        model.presentation.section_titles.get("corne_host", "CORNE HOST ACTIONS"),
        "Semantic window, workspace, and desktop actions for daily use",
    )

    groups = {group.key: group for group in model.host_action_groups}
    ordered_keys = ("workspaces", "move_workspace", "focus", "move", "context", "desktop")
    row_x = x + 38
    first_y = y + 137
    row_height = 132
    values_x = row_x + 330

    for index, key in enumerate(ordered_keys):
        group = groups[key]
        current_y = first_y + index * row_height
        out.append(
            f'    <rect x="{row_x - 14:.1f}" y="{current_y - 42:.1f}" width="{width - 48:.1f}" height="{row_height - 12:.1f}" rx="10" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1" />'
        )
        out.append(text(row_x, current_y, group.title, "action-title", COLOR_ACCENT))
        separator = " / " if key in ("workspaces", "move_workspace") else "   "
        out.append(text(values_x, current_y, separator.join(group.values), "action-values"))

    finish_panel(out)
    return "\n".join(out)


def render_behavior_panel(model: HostCheatsheetModel) -> str:
    x, y, width, height = RIGHT_X, BEHAVIOR_Y, RIGHT_WIDTH, BEHAVIOR_HEIGHT
    out = panel(
        x,
        y,
        width,
        height,
        model.presentation.section_titles.get("behavior", "BEHAVIOR NOTES"),
        "The same semantic actions follow the active layout",
    )

    content_x = x + 40
    current_y = y + 135
    blocks = [
        ("Niri:", model.behavior_notes.get("niri", ""), COLOR_WEB),
        ("Dwindle:", model.behavior_notes.get("dwindle", ""), COLOR_COMMS),
        ("Quake", model.behavior_notes.get("quake", ""), COLOR_ACCENT),
        ("NewTerm", model.behavior_notes.get("newterm", ""), COLOR_ACCENT),
        ("Hold Option ~200 ms", model.behavior_notes.get("option", ""), COLOR_ACCENT),
    ]
    for index, (label, value, color) in enumerate(blocks):
        block_height = 105 if index < 2 else 108
        out.append(text(content_x, current_y, label, "note-title", color))
        out.append(text(content_x, current_y + 35, value, "note-body"))
        current_y += block_height

    # Keep the routing clarification visible without exposing implementation details.
    out.append(
        text(
            content_x,
            y + height - 58,
            "Launch shortcuts and workspace shortcuts remain separate concepts.",
            "note-footer",
            COLOR_MUTED,
        )
    )

    finish_panel(out)
    return "\n".join(out)


def render_host_cheatsheet_svg(model: HostCheatsheetModel) -> str:
    """Render a complete deterministic A4 landscape host workflow cheatsheet."""
    title = model.presentation.title
    subtitle = model.presentation.subtitle
    svg: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {PAGE_WIDTH} {PAGE_HEIGHT}" width="297mm" height="210mm">',
        "  <defs>",
        "    <style><![CDATA[",
        '      text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "DejaVu Sans", Ubuntu, sans-serif; dominant-baseline: alphabetic; }',
        "      .title { font-size: 42px; font-weight: 800; fill: #0f172a; letter-spacing: 1px; }",
        "      .subtitle { font-size: 19px; font-weight: 500; fill: #64748b; letter-spacing: 0.3px; }",
        "      .panel-title { font-size: 27px; font-weight: 800; fill: #0f172a; letter-spacing: 0.7px; }",
        "      .panel-subtitle { font-size: 16px; font-weight: 500; fill: #64748b; }",
        "      .table-header, .small-header { font-size: 15px; font-weight: 800; letter-spacing: 1px; }",
        "      .table-header { fill: #64748b; }",
        "      .small-header { fill: #4f46e5; }",
        "      .table-value { font-size: 20px; font-weight: 600; fill: #0f172a; }",
        "      .routing-value { font-size: 17px; font-weight: 700; }",
        "      .shortcut { font-size: 24px; font-weight: 800; fill: #0f172a; }",
        "      .body { font-size: 20px; font-weight: 600; fill: #334155; }",
        "      .action-title { font-size: 20px; font-weight: 800; }",
        "      .action-values { font-size: 25px; font-weight: 700; fill: #0f172a; }",
        "      .note-title { font-size: 23px; font-weight: 800; }",
        "      .note-body { font-size: 21px; font-weight: 600; fill: #334155; }",
        "      .note-footer { font-size: 15px; font-weight: 600; }",
        "    ]]></style>",
        "  </defs>",
        f'  <rect x="0" y="0" width="{PAGE_WIDTH}" height="{PAGE_HEIGHT}" fill="{COLOR_BG}" />',
        text(MARGIN, 67, title, "title"),
        text(MARGIN, 105, subtitle, "subtitle"),
        f'  <line x1="{MARGIN}" y1="{HEADER_BOTTOM}" x2="{PAGE_WIDTH - MARGIN}" y2="{HEADER_BOTTOM}" stroke="#cbd5e1" stroke-width="2" />',
    ]

    svg.append(render_workspace_panel(model))
    svg.append(render_macbook_panel(model))
    svg.append(render_corne_panel(model))
    svg.append(render_behavior_panel(model))
    svg.append("</svg>")
    return "\n".join(svg) + "\n"
