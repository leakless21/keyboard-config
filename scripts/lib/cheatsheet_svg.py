"""
Cheatsheet Deterministic SVG Renderer (Compact Print / Light Theme).

Renders intermediate CheatsheetModel (Corne or Sofle) into a compact, high-contrast,
print-optimized A4 landscape SVG document with:
  - Pure white background and crisp light card panels
  - Compact inter-card gaps and zero wasted bottom whitespace
  - Exact schematic geometry (42-pos Corne or 60-pos Sofle with rotary encoders)
  - Machine-readable data-* attributes for structural validation
  - Layer-accent colored transition outlines
  - Deterministic label sizing and multi-line wrapping
  - Auto-generated layer access graph, encoder documentation, and system notes
"""

from __future__ import annotations

import html

try:
    from .cheatsheet import (
        CheatsheetModel,
        KeyView,
        LayerView,
    )
except ImportError:
    try:
        from lib.cheatsheet import (
            CheatsheetModel,
            KeyView,
            LayerView,
        )
    except ImportError:
        from scripts.lib.cheatsheet import (
            CheatsheetModel,
            KeyView,
            LayerView,
        )


# =============================================================================
# Layout Constants (A4 Landscape at 2970 x 2100 ViewBox)
# =============================================================================
PAGE_WIDTH = 2970
PAGE_HEIGHT = 2100

# Margins
MARGIN_X = 33
MARGIN_TOP = 26

# Header
HEADER_Y = 28
HEADER_HEIGHT = 58

# 3x4 Grid Geometry (Compact, tight inter-card gaps)
GRID_Y = 94
GRID_COLS = 3
GRID_ROWS = 4
COL_GAP = 12
ROW_GAP = 10

CARD_WIDTH = 960
CARD_HEIGHT = 472

# Corne Keyboard Geometry (Keys fill card vertically with 24px bottom pad)
CORNE_KEY_W = 72
CORNE_KEY_H = 96
CORNE_KEY_GAP = 6
CORNE_SPLIT_GAP = 26
CORNE_KEY_RX = 6
CORNE_KBD_LEFT_X = 5
CORNE_KBD_TOP_Y = 40
CORNE_THUMB_GAP_Y = 12

# Sofle Keyboard Geometry (60 keys: 5 rows incl. number row & encoders)
SOFLE_KEY_W = 62
SOFLE_KEY_H = 74
SOFLE_KEY_GAP = 5
SOFLE_SPLIT_GAP = 18
SOFLE_KEY_RX = 5
SOFLE_KBD_LEFT_X = 7
SOFLE_KBD_TOP_Y = 38
SOFLE_THUMB_GAP_Y = 8

# Color Palette (Clean White / High-Contrast Print Theme)
COLOR_BG = "#ffffff"
COLOR_CARD_BG = "#ffffff"
COLOR_CARD_BORDER = "#e2e8f0"
COLOR_TEXT_PRIMARY = "#0f172a"
COLOR_TEXT_SECONDARY = "#475569"
COLOR_TEXT_MUTED = "#64748b"

COLOR_KEY_BG = "#ffffff"
COLOR_KEY_BORDER = "#cbd5e1"
COLOR_KEY_UNUSED_BG = "#f8fafc"
COLOR_KEY_UNUSED_BORDER = "#e2e8f0"
COLOR_KEY_TRANS_BG = "#f8fafc"
COLOR_KEY_TRANS_BORDER = "#94a3b8"


def escape(text: str | None) -> str:
    """XML/HTML escape a text string."""
    if text is None:
        return ""
    return html.escape(str(text))


def parse_grid_index(position: str, char_index: int) -> int:
    """Extract an integer grid index from a position label such as 'LT3'.

    Position labels come from the geometry tables, so a malformed label means the
    geometry itself is corrupt. Fail with the offending label instead of a bare
    ValueError from int().
    """
    try:
        return int(position[char_index])
    except (IndexError, ValueError) as exc:
        raise ValueError(f"Malformed keyboard position label: {position!r}") from exc


def compute_corne_key_coords(pos: str, card_x: float, card_y: float) -> tuple[float, float, float, float]:
    """Compute absolute (x, y, w, h) for a Corne key position within a card."""
    row_step = CORNE_KEY_H + CORNE_KEY_GAP
    col_step = CORNE_KEY_W + CORNE_KEY_GAP
    left_start_x = card_x + CORNE_KBD_LEFT_X
    right_start_x = left_start_x + (6 * CORNE_KEY_W + 5 * CORNE_KEY_GAP) + CORNE_SPLIT_GAP
    alpha_top_y = card_y + CORNE_KBD_TOP_Y
    thumb_y = alpha_top_y + (3 * CORNE_KEY_H + 2 * CORNE_KEY_GAP) + CORNE_THUMB_GAP_Y

    # Left Hand Matrix
    if pos.startswith("LT"):
        col_idx = 5 - parse_grid_index(pos, 2)
        return left_start_x + col_idx * col_step, alpha_top_y, CORNE_KEY_W, CORNE_KEY_H
    if pos.startswith("LM"):
        col_idx = 5 - parse_grid_index(pos, 2)
        return left_start_x + col_idx * col_step, alpha_top_y + row_step, CORNE_KEY_W, CORNE_KEY_H
    if pos.startswith("LB"):
        col_idx = 5 - parse_grid_index(pos, 2)
        return left_start_x + col_idx * col_step, alpha_top_y + 2 * row_step, CORNE_KEY_W, CORNE_KEY_H

    # Left Hand Thumbs
    if pos == "LH2":
        return left_start_x + 3 * col_step, thumb_y, CORNE_KEY_W, CORNE_KEY_H
    if pos == "LH1":
        return left_start_x + 4 * col_step, thumb_y, CORNE_KEY_W, CORNE_KEY_H
    if pos == "LH0":
        return left_start_x + 5 * col_step, thumb_y, CORNE_KEY_W, CORNE_KEY_H

    # Right Hand Matrix
    if pos.startswith("RT"):
        col_idx = parse_grid_index(pos, 2)
        return right_start_x + col_idx * col_step, alpha_top_y, CORNE_KEY_W, CORNE_KEY_H
    if pos.startswith("RM"):
        col_idx = parse_grid_index(pos, 2)
        return right_start_x + col_idx * col_step, alpha_top_y + row_step, CORNE_KEY_W, CORNE_KEY_H
    if pos.startswith("RB"):
        col_idx = parse_grid_index(pos, 2)
        return right_start_x + col_idx * col_step, alpha_top_y + 2 * row_step, CORNE_KEY_W, CORNE_KEY_H

    # Right Hand Thumbs
    if pos == "RH0":
        return right_start_x + 0 * col_step, thumb_y, CORNE_KEY_W, CORNE_KEY_H
    if pos == "RH1":
        return right_start_x + 1 * col_step, thumb_y, CORNE_KEY_W, CORNE_KEY_H
    if pos == "RH2":
        return right_start_x + 2 * col_step, thumb_y, CORNE_KEY_W, CORNE_KEY_H

    raise ValueError(f"Unknown Corne position: {pos}")


def compute_sofle_key_coords(pos: str, card_x: float, card_y: float) -> tuple[float, float, float, float]:
    """Compute absolute (x, y, w, h) for a Sofle key position within a card."""
    row_step = SOFLE_KEY_H + SOFLE_KEY_GAP
    col_step = SOFLE_KEY_W + SOFLE_KEY_GAP
    left_start_x = card_x + SOFLE_KBD_LEFT_X
    right_start_x = left_start_x + (7 * SOFLE_KEY_W + 6 * SOFLE_KEY_GAP) + SOFLE_SPLIT_GAP

    n_top_y = card_y + SOFLE_KBD_TOP_Y
    t_top_y = n_top_y + row_step
    m_top_y = n_top_y + 2 * row_step
    b_top_y = n_top_y + 3 * row_step
    thumb_y = n_top_y + 4 * row_step + SOFLE_THUMB_GAP_Y

    # Number Row (LN5..LN0, RN0..RN5)
    if pos.startswith("LN"):
        col_idx = 5 - parse_grid_index(pos, 2)
        return left_start_x + col_idx * col_step, n_top_y, SOFLE_KEY_W, SOFLE_KEY_H
    if pos.startswith("RN"):
        col_idx = parse_grid_index(pos, 2) + 1
        return right_start_x + col_idx * col_step, n_top_y, SOFLE_KEY_W, SOFLE_KEY_H

    # Top Row (LT5..LT0, RT0..RT5)
    if pos.startswith("LT"):
        col_idx = 5 - parse_grid_index(pos, 2)
        return left_start_x + col_idx * col_step, t_top_y, SOFLE_KEY_W, SOFLE_KEY_H
    if pos.startswith("RT"):
        col_idx = parse_grid_index(pos, 2) + 1
        return right_start_x + col_idx * col_step, t_top_y, SOFLE_KEY_W, SOFLE_KEY_H

    # Middle Row (LM5..LM0, RM0..RM5)
    if pos.startswith("LM"):
        col_idx = 5 - parse_grid_index(pos, 2)
        return left_start_x + col_idx * col_step, m_top_y, SOFLE_KEY_W, SOFLE_KEY_H
    if pos.startswith("RM"):
        col_idx = parse_grid_index(pos, 2) + 1
        return right_start_x + col_idx * col_step, m_top_y, SOFLE_KEY_W, SOFLE_KEY_H

    # Bottom Row & Encoders
    if pos.startswith("LB"):
        col_idx = 5 - parse_grid_index(pos, 2)
        return left_start_x + col_idx * col_step, b_top_y, SOFLE_KEY_W, SOFLE_KEY_H
    if pos == "LEC":
        return left_start_x + 6 * col_step, b_top_y, SOFLE_KEY_W, SOFLE_KEY_H
    if pos == "REC":
        return right_start_x + 0 * col_step, b_top_y, SOFLE_KEY_W, SOFLE_KEY_H
    if pos.startswith("RB"):
        col_idx = parse_grid_index(pos, 2) + 1
        return right_start_x + col_idx * col_step, b_top_y, SOFLE_KEY_W, SOFLE_KEY_H

    # Thumbs (LH4..LH0, RH0..RH4)
    if pos.startswith("LH"):
        idx = parse_grid_index(pos, 2)
        col_idx = 5 - idx
        return left_start_x + col_idx * col_step, thumb_y, SOFLE_KEY_W, SOFLE_KEY_H
    if pos.startswith("RH"):
        idx = parse_grid_index(pos, 2)
        col_idx = idx + 1
        return right_start_x + col_idx * col_step, thumb_y, SOFLE_KEY_W, SOFLE_KEY_H

    raise ValueError(f"Unknown Sofle position: {pos}")


def compute_key_coords(pos: str, card_x: float, card_y: float, keyboard: str = "corne") -> tuple[float, float, float, float]:
    """Compute key coordinates dynamically based on keyboard target."""
    if keyboard == "sofle" or pos.startswith(("LN", "RN")) or pos in ("LEC", "REC") or pos in ("LH4", "LH3", "RH3", "RH4"):
        return compute_sofle_key_coords(pos, card_x, card_y)
    return compute_corne_key_coords(pos, card_x, card_y)


def render_key_svg(
    key: KeyView,
    card_x: float,
    card_y: float,
    layer_name: str,
    color_palette: dict[str, str],
    keyboard: str = "corne",
    debug: bool = False,
) -> str:
    """Render a single keycap group with machine-readable XML attributes."""
    x, y, w, h = compute_key_coords(key.position, card_x, card_y, keyboard=keyboard)
    cx = x + w / 2
    cy = y + h / 2
    rx = SOFLE_KEY_RX if keyboard == "sofle" else CORNE_KEY_RX

    classes = ["key", key.kind]
    if key.is_modifier:
        classes.append("mod")
    if key.is_bootloader:
        classes.append("bootloader")
    if key.is_held_activator:
        classes.append("held-activator")
    if key.position in ("LEC", "REC"):
        classes.append("encoder")
    attrs = [
        f'class="{" ".join(classes)}"',
        f'data-layer="{escape(layer_name)}"',
        f'data-position="{escape(key.position)}"',
        f'data-binding="{escape(key.raw_binding)}"',
    ]
    if key.target_layer:
        attrs.append(f'data-target-layer="{escape(key.target_layer)}"')
    if key.transition_mode:
        attrs.append(f'data-transition-mode="{escape(key.transition_mode)}"')

    # Visual border & fill logic for clean print
    border_color = COLOR_KEY_BORDER
    fill_color = COLOR_KEY_BG
    border_width = 1.2
    stroke_dash = ""

    if key.kind == "unused":
        fill_color = COLOR_KEY_UNUSED_BG
        border_color = COLOR_KEY_UNUSED_BORDER
        border_width = 1.0
    elif key.kind == "transparent":
        fill_color = COLOR_KEY_TRANS_BG
        border_color = COLOR_KEY_TRANS_BORDER
        border_width = 1.2
        stroke_dash = 'stroke-dasharray="3,3"'
    elif key.kind == "transition":
        target_color = color_palette.get(key.target_layer or "", "#0284c7")
        border_color = target_color
        border_width = 2.4
        fill_color = "#ffffff"
    elif key.kind == "held_activator" or key.is_held_activator:
        layer_color = color_palette.get(layer_name, "#0284c7")
        border_color = layer_color
        border_width = 1.8
        fill_color = "#f8fafc"
    elif key.is_bootloader:
        border_color = "#e11d48"
        border_width = 2.0
        fill_color = "#fff1f2"
    elif key.position in ("LEC", "REC"):
        fill_color = "#f1f5f9"
        border_color = "#94a3b8"
        border_width = 1.6
    elif key.is_modifier:
        fill_color = "#f8fafc"
        border_color = "#cbd5e1"
        border_width = 1.2

    rect_attrs = [
        f'x="{x:.1f}"',
        f'y="{y:.1f}"',
        f'width="{w:.1f}"',
        f'height="{h:.1f}"',
        f'rx="{rx}"',
        f'ry="{rx}"',
        f'fill="{fill_color}"',
        f'stroke="{border_color}"',
        f'stroke-width="{border_width}"',
    ]
    if stroke_dash:
        rect_attrs.append(stroke_dash)

    out = [f'  <g {" ".join(attrs)}>']
    out.append(f'    <rect {" ".join(rect_attrs)} />')

    # Distinct rotary encoder dial ring
    if key.position in ("LEC", "REC"):
        out.append(
            f'    <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{min(w, h) * 0.38:.1f}" fill="none" stroke="#cbd5e1" stroke-width="1.2" stroke-dasharray="4,2" />'
        )

    # Label rendering
    if key.kind == "transparent":
        # Subtle pass-through indicator
        out.append(f'    <text x="{cx:.1f}" y="{cy + 5:.1f}" class="lbl-trans">▿</text>')
    elif key.kind != "unused":
        tap_lbl = key.tap
        hold_lbl = key.hold

        # Case 1: Both Tap and Hold (e.g. thumb layer-taps or home row mods)
        if tap_lbl and hold_lbl:
            tap_fs = 18 if len(tap_lbl) <= 2 else (14.5 if len(tap_lbl) <= 5 else 12.5)
            out.append(
                f'    <text x="{cx:.1f}" y="{y + (h * 0.38):.1f}" class="lbl-tap" font-size="{tap_fs}">{escape(tap_lbl)}</text>'
            )
            if key.kind == "transition":
                hold_color = color_palette.get(key.target_layer or "", "#0284c7")
                out.append(
                    f'    <text x="{cx:.1f}" y="{y + (h * 0.78):.1f}" class="lbl-hold-layer" font-size="13" fill="{hold_color}">{escape(hold_lbl)}</text>'
                )
            elif key.kind == "held_activator" or key.is_held_activator:
                layer_color = color_palette.get(layer_name, "#0284c7")
                out.append(
                    f'    <text x="{cx:.1f}" y="{y + (h * 0.78):.1f}" class="lbl-hold-layer" font-size="13" fill="{layer_color}">{escape(hold_lbl)}</text>'
                )
            else:
                out.append(
                    f'    <text x="{cx:.1f}" y="{y + (h * 0.78):.1f}" class="lbl-hold" font-size="13">{escape(hold_lbl)}</text>'
                )

        # Case 2: Only Tap / Primary Label
        elif tap_lbl:
            if key.kind == "transition" and key.target_layer:
                target_color = color_palette.get(key.target_layer, "#0284c7")
                fs = 14 if len(tap_lbl) > 5 else 16
                out.append(
                    f'    <text x="{cx:.1f}" y="{cy + 5.5:.1f}" class="lbl-trans-only" font-size="{fs}" fill="{target_color}">{escape(tap_lbl)}</text>'
                )
            elif key.is_bootloader:
                out.append(
                    f'    <text x="{cx:.1f}" y="{cy + 5.5:.1f}" class="lbl-boot" font-size="15">{escape(tap_lbl)}</text>'
                )
            elif len(tap_lbl) == 1:
                fs = 24 if keyboard == "sofle" else 28
                out.append(
                    f'    <text x="{cx:.1f}" y="{cy + 8.5:.1f}" class="lbl-single" font-size="{fs}">{escape(tap_lbl)}</text>'
                )
            elif "→" in tap_lbl and " " not in tap_lbl:
                parts = tap_lbl.split("→", 1)
                p1 = parts[0] + "→"
                p2 = parts[1]
                fs = 13.5 if max(len(p1), len(p2)) <= 5 else 12
                out.append(
                    f'    <text x="{cx:.1f}" y="{cy - 6:.1f}" class="lbl-multi" font-size="{fs}">{escape(p1)}</text>'
                )
                out.append(
                    f'    <text x="{cx:.1f}" y="{cy + 16:.1f}" class="lbl-multi" font-size="{fs}">{escape(p2)}</text>'
                )
            elif " " in tap_lbl or "/" in tap_lbl or len(tap_lbl) > 8:
                parts = tap_lbl.split(" ", 1) if " " in tap_lbl else (tap_lbl.split("/", 1) if "/" in tap_lbl else [tap_lbl[:5], tap_lbl[5:]])
                p1 = parts[0] + ("/" if "/" in tap_lbl and " " not in tap_lbl else "")
                p2 = parts[1]
                fs = 13.5 if max(len(p1), len(p2)) <= 5 else (12.5 if max(len(p1), len(p2)) <= 7 else 11.5)
                out.append(
                    f'    <text x="{cx:.1f}" y="{cy - 6:.1f}" class="lbl-multi" font-size="{fs}">{escape(p1)}</text>'
                )
                out.append(
                    f'    <text x="{cx:.1f}" y="{cy + 16:.1f}" class="lbl-multi" font-size="{fs}">{escape(p2)}</text>'
                )
            else:
                fs = 16 if len(tap_lbl) <= 4 else (14 if len(tap_lbl) <= 7 else 12.5)
                out.append(
                    f'    <text x="{cx:.1f}" y="{cy + 5.5:.1f}" class="lbl-word" font-size="{fs}">{escape(tap_lbl)}</text>'
                )

    # Debug position overlay
    if debug:
        out.append(
            f'    <text x="{x + 3:.1f}" y="{y + 10:.1f}" class="lbl-debug">{escape(key.position)}</text>'
        )

    out.append("  </g>")
    return "\n".join(out)


def render_layer_panel(
    layer: LayerView,
    card_x: float,
    card_y: float,
    color_palette: dict[str, str],
    keyboard: str = "corne",
    debug: bool = False,
) -> str:
    """Render a single layer panel containing the keyboard schematic."""
    layer_id = f"layer-{layer.name.lower()}"
    accent_color = layer.color

    out = [f'<g id="{layer_id}" data-layer="{escape(layer.name)}">']

    # Background card
    out.append(
        f'  <rect x="{card_x:.1f}" y="{card_y:.1f}" width="{CARD_WIDTH:.1f}" height="{CARD_HEIGHT:.1f}" '
        f'rx="8" ry="8" fill="{COLOR_CARD_BG}" stroke="{COLOR_CARD_BORDER}" stroke-width="1.2" />'
    )

    # Top accent bar
    out.append(
        f'  <rect x="{card_x + 10:.1f}" y="{card_y + 8:.1f}" width="4.5" height="22" rx="2.2" fill="{accent_color}" />'
    )

    # Layer Header Tag & Subtitle
    out.append(
        f'  <text x="{card_x + 22:.1f}" y="{card_y + 25:.1f}" class="panel-title" fill="{accent_color}">{escape(layer.name)}</text>'
    )
    out.append(
        f'  <text x="{card_x + 24 + len(layer.name) * 15:.1f}" y="{card_y + 25:.1f}" class="panel-sub">{escape(layer.subtitle)}</text>'
    )

    # Render all keys
    for key in layer.key_list:
        out.append(render_key_svg(key, card_x, card_y, layer.name, color_palette, keyboard=keyboard, debug=debug))

    out.append("</g>")
    return "\n".join(out)


def render_corne_notes_panel(
    card_x: float,
    card_y: float,
    model: CheatsheetModel,
    color_palette: dict[str, str],
) -> str:
    """Render the Corne ACCESS & SYSTEM NOTES panel."""
    out = ['<g id="layer-notes" data-layer="NOTES">']

    out.append(
        f'  <rect x="{card_x:.1f}" y="{card_y:.1f}" width="{CARD_WIDTH:.1f}" height="{CARD_HEIGHT:.1f}" '
        f'rx="8" ry="8" fill="{COLOR_CARD_BG}" stroke="{COLOR_CARD_BORDER}" stroke-width="1.2" />'
    )
    out.append(
        f'  <rect x="{card_x + 10:.1f}" y="{card_y + 8:.1f}" width="4.5" height="22" rx="2.2" fill="#0284c7" />'
    )
    out.append(
        f'  <text x="{card_x + 22:.1f}" y="{card_y + 25:.1f}" class="panel-title" fill="#0284c7">ACCESS &amp; SYSTEM NOTES</text>'
    )
    out.append(
        f'  <text x="{card_x + 350:.1f}" y="{card_y + 25:.1f}" class="panel-sub">Reference &amp; Hardware Rules</text>'
    )

    col1_x = card_x + 20
    col2_x = card_x + 338
    col3_x = card_x + 652
    body_y = card_y + 68

    out.append(f'  <text x="{col1_x:.1f}" y="{body_y:.1f}" class="notes-header">LAYER ACCESS</text>')
    c1_y = body_y + 30

    access_rows = [
        ("MEDIA", "Hold LM5", color_palette.get("MEDIA", "#ea580c")),
        ("MOUSE", "Hold L-thumb Esc (LH2)", color_palette.get("MOUSE", "#0d9488")),
        ("NAV", "Hold L-thumb Space (LH1)", color_palette.get("NAV", "#0284c7")),
        ("HOST", "Hold L-thumb Tab (LH0)", color_palette.get("HOST", "#6366f1")),
        ("SYM", "Hold R-thumb Enter (RH0)", color_palette.get("SYM", "#9333ea")),
        ("NUM", "Hold R-thumb Bsp (RH1)", color_palette.get("NUM", "#d97706")),
        ("FUN", "Hold R-thumb Del (RH2)", color_palette.get("FUN", "#db2777")),
        ("ADJUST", "Hold NAV + NUM (Space+Bsp)", color_palette.get("ADJUST", "#c026d3")),
    ]

    for name, trigger, col in access_rows:
        out.append(f'  <circle cx="{col1_x + 6:.1f}" cy="{c1_y - 5:.1f}" r="4.5" fill="{col}" />')
        out.append(f'  <text x="{col1_x + 18:.1f}" y="{c1_y:.1f}" class="notes-badge" fill="{col}">{escape(name)}</text>')
        out.append(f'  <text x="{col1_x + 82:.1f}" y="{c1_y:.1f}" class="notes-text">{escape(trigger)}</text>')
        c1_y += 40

    out.append(f'  <text x="{col2_x:.1f}" y="{body_y:.1f}" class="notes-header">SPECIAL MECHANICS</text>')
    c2_y = body_y + 30

    special_items = [
        ("ADJUST", "NAV + NUM conditional rule (L1+L4)", color_palette.get("ADJUST", "#c026d3")),
        ("GAME", "Entered via ADJUST RT3 (&amp;to L_GAME)", color_palette.get("GAME", "#dc2626")),
        ("GAME_FN", "Hold Esc (LT5) or Hold RH1 (&amp;mo)", color_palette.get("GAME_FN", "#4f46e5")),
        ("EXIT GAME", "GAME_FN RH2 (&amp;to L_BASE)", color_palette.get("BASE", "#475569")),
    ]

    for label, desc, col in special_items:
        out.append(f'  <text x="{col2_x:.1f}" y="{c2_y:.1f}" class="notes-badge-bold" fill="{col}">{label}</text>')
        out.append(f'  <text x="{col2_x:.1f}" y="{c2_y + 19:.1f}" class="notes-text">{desc}</text>')
        c2_y += 54

    out.append(
        f'  <rect x="{col2_x - 4:.1f}" y="{c2_y - 2:.1f}" width="292" height="66" rx="6" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1" />'
    )
    out.append(f'  <text x="{col2_x + 8:.1f}" y="{c2_y + 20:.1f}" class="notes-alert-title">GAME RH2 Transparent Note</text>')
    out.append(f'  <text x="{col2_x + 8:.1f}" y="{c2_y + 44:.1f}" class="notes-alert-desc">RH2 falls through to BASE Del/FUN. Not an exit.</text>')

    out.append(f'  <text x="{col3_x:.1f}" y="{body_y:.1f}" class="notes-header">HARDWARE &amp; PROTOCOL</text>')
    c3_y = body_y + 30

    out.append(f'  <text x="{col3_x:.1f}" y="{c3_y:.1f}" class="notes-badge-bold" fill="#e11d48">BOOTLOADER SHORTCUTS</text>')
    out.append(f'  <text x="{col3_x:.1f}" y="{c3_y + 19:.1f}" class="notes-text">Left side: NAV LT5 / ADJUST LT5</text>')
    out.append(f'  <text x="{col3_x:.1f}" y="{c3_y + 37:.1f}" class="notes-text">Right side: NUM RT5 / ADJUST RT5</text>')
    c3_y += 74

    out.append(
        f'  <rect x="{col3_x - 4:.1f}" y="{c3_y - 2:.1f}" width="292" height="74" rx="6" fill="#fff1f2" stroke="#fecdd3" stroke-width="1" />'
    )
    out.append(f'  <text x="{col3_x + 8:.1f}" y="{c3_y + 20:.1f}" class="notes-alert-warn">Peripheral Bootloader Caveat</text>')
    out.append(f'  <text x="{col3_x + 8:.1f}" y="{c3_y + 42:.1f}" class="notes-alert-desc-warn">Right BOOT requires split link. Use</text>')
    out.append(f'  <text x="{col3_x + 8:.1f}" y="{c3_y + 59:.1f}" class="notes-alert-desc-warn">physical reset button if unlinked.</text>')
    c3_y += 98

    out.append(f'  <text x="{col3_x:.1f}" y="{c3_y:.1f}" class="notes-badge-bold" fill="#6366f1">HOST PROTOCOL (F13–F24)</text>')
    out.append(f'  <text x="{col3_x:.1f}" y="{c3_y + 19:.1f}" class="notes-text">HOST and edit semantic signals require</text>')
    out.append(f'  <text x="{col3_x:.1f}" y="{c3_y + 37:.1f}" class="notes-text">the active macOS or Windows host bridge.</text>')

    out.append("</g>")
    return "\n".join(out)


def render_sofle_access_notes_panel(
    card_x: float,
    card_y: float,
    model: CheatsheetModel,
    color_palette: dict[str, str],
) -> str:
    """Render Sofle Panel 10 (col 1, row 3): ACCESS & SYSTEM NOTES."""
    out = ['<g id="layer-notes" data-layer="NOTES">']

    out.append(
        f'  <rect x="{card_x:.1f}" y="{card_y:.1f}" width="{CARD_WIDTH:.1f}" height="{CARD_HEIGHT:.1f}" '
        f'rx="8" ry="8" fill="{COLOR_CARD_BG}" stroke="{COLOR_CARD_BORDER}" stroke-width="1.2" />'
    )
    out.append(
        f'  <rect x="{card_x + 10:.1f}" y="{card_y + 8:.1f}" width="4.5" height="22" rx="2.2" fill="#0284c7" />'
    )
    out.append(
        f'  <text x="{card_x + 22:.1f}" y="{card_y + 25:.1f}" class="panel-title" fill="#0284c7">ACCESS &amp; SYSTEM NOTES</text>'
    )
    out.append(
        f'  <text x="{card_x + 350:.1f}" y="{card_y + 25:.1f}" class="panel-sub">Layer Transitions &amp; Recovery</text>'
    )

    col1_x = card_x + 20
    col2_x = card_x + 338
    col3_x = card_x + 652
    body_y = card_y + 68

    # Col 1: Layer Access
    out.append(f'  <text x="{col1_x:.1f}" y="{body_y:.1f}" class="notes-header">LAYER ACCESS</text>')
    c1_y = body_y + 30
    access_rows = [
        ("MEDIA", "Hold LM5", color_palette.get("MEDIA", "#ea580c")),
        ("MOUSE", "Hold L-thumb Esc (LH2)", color_palette.get("MOUSE", "#0d9488")),
        ("NAV", "Hold L-thumb Space (LH1)", color_palette.get("NAV", "#0284c7")),
        ("HOST", "Hold L-thumb Tab (LH0)", color_palette.get("HOST", "#6366f1")),
        ("SYM", "Hold R-thumb Enter (RH0)", color_palette.get("SYM", "#9333ea")),
        ("NUM", "Hold R-thumb Bsp (RH1)", color_palette.get("NUM", "#d97706")),
        ("FUN", "Hold R-thumb Del (RH2)", color_palette.get("FUN", "#db2777")),
        ("ADJUST", "Hold NAV + NUM (Space+Bsp)", color_palette.get("ADJUST", "#c026d3")),
    ]
    for name, trigger, col in access_rows:
        out.append(f'  <circle cx="{col1_x + 6:.1f}" cy="{c1_y - 5:.1f}" r="4.5" fill="{col}" />')
        out.append(f'  <text x="{col1_x + 18:.1f}" y="{c1_y:.1f}" class="notes-badge" fill="{col}">{escape(name)}</text>')
        out.append(f'  <text x="{col1_x + 82:.1f}" y="{c1_y:.1f}" class="notes-text">{escape(trigger)}</text>')
        c1_y += 40

    # Col 2: Special Layer Mechanics
    out.append(f'  <text x="{col2_x:.1f}" y="{body_y:.1f}" class="notes-header">SPECIAL MECHANICS</text>')
    c2_y = body_y + 30
    special_items = [
        ("ADJUST", "NAV + NUM conditional rule (L1+L4)", color_palette.get("ADJUST", "#c026d3")),
        ("GAME", "Entered via ADJUST RT3 (&amp;to L_GAME)", color_palette.get("GAME", "#dc2626")),
        ("EXIT GAME", "Right Encoder press REC (&amp;to L_BASE)", color_palette.get("BASE", "#475569")),
        ("NUMBER ROW", "Dedicated physical numbers on BASE/GAME", color_palette.get("BASE", "#475569")),
    ]
    for label, desc, col in special_items:
        out.append(f'  <text x="{col2_x:.1f}" y="{c2_y:.1f}" class="notes-badge-bold" fill="{col}">{label}</text>')
        out.append(f'  <text x="{col2_x:.1f}" y="{c2_y + 19:.1f}" class="notes-text">{desc}</text>')
        c2_y += 54

    out.append(
        f'  <rect x="{col2_x - 4:.1f}" y="{c2_y - 2:.1f}" width="292" height="66" rx="6" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1" />'
    )
    out.append(f'  <text x="{col2_x + 8:.1f}" y="{c2_y + 20:.1f}" class="notes-alert-title">Gaming Architecture Note</text>')
    out.append(f'  <text x="{col2_x + 8:.1f}" y="{c2_y + 44:.1f}" class="notes-alert-desc">Plain QWERTY, no HRMs. Tap REC to exit.</text>')

    # Col 3: Hardware Bootloaders
    out.append(f'  <text x="{col3_x:.1f}" y="{body_y:.1f}" class="notes-header">HARDWARE RECOVERY</text>')
    c3_y = body_y + 30
    out.append(f'  <text x="{col3_x:.1f}" y="{c3_y:.1f}" class="notes-badge-bold" fill="#e11d48">BOOTLOADER SHORTCUTS</text>')
    out.append(f'  <text x="{col3_x:.1f}" y="{c3_y + 19:.1f}" class="notes-text">Left side: NAV LT5 / ADJUST LT5</text>')
    out.append(f'  <text x="{col3_x:.1f}" y="{c3_y + 37:.1f}" class="notes-text">Right side: NUM RT5 / ADJUST RT5</text>')
    c3_y += 74

    out.append(
        f'  <rect x="{col3_x - 4:.1f}" y="{c3_y - 2:.1f}" width="292" height="74" rx="6" fill="#fff1f2" stroke="#fecdd3" stroke-width="1" />'
    )
    out.append(f'  <text x="{col3_x + 8:.1f}" y="{c3_y + 20:.1f}" class="notes-alert-warn">Peripheral Bootloader Caveat</text>')
    out.append(f'  <text x="{col3_x + 8:.1f}" y="{c3_y + 42:.1f}" class="notes-alert-desc-warn">Right BOOT requires split link. Use</text>')
    out.append(f'  <text x="{col3_x + 8:.1f}" y="{c3_y + 59:.1f}" class="notes-alert-desc-warn">physical reset button if unlinked.</text>')

    out.append("</g>")
    return "\n".join(out)


def render_sofle_encoders_notes_panel(
    card_x: float,
    card_y: float,
    model: CheatsheetModel,
    color_palette: dict[str, str],
) -> str:
    """Render Sofle Panel 11 (col 2, row 3): ENCODERS & PROTOCOL."""
    out = ['<g id="layer-encoder-notes" data-layer="ENCODERS">']

    out.append(
        f'  <rect x="{card_x:.1f}" y="{card_y:.1f}" width="{CARD_WIDTH:.1f}" height="{CARD_HEIGHT:.1f}" '
        f'rx="8" ry="8" fill="{COLOR_CARD_BG}" stroke="{COLOR_CARD_BORDER}" stroke-width="1.2" />'
    )
    out.append(
        f'  <rect x="{card_x + 10:.1f}" y="{card_y + 8:.1f}" width="4.5" height="22" rx="2.2" fill="#6366f1" />'
    )
    out.append(
        f'  <text x="{card_x + 22:.1f}" y="{card_y + 25:.1f}" class="panel-title" fill="#6366f1">ENCODERS &amp; PROTOCOL</text>'
    )
    out.append(
        f'  <text x="{card_x + 350:.1f}" y="{card_y + 25:.1f}" class="panel-sub">EC11 Rotary Knobs &amp; Host HID</text>'
    )

    col1_x = card_x + 20
    col2_x = card_x + 338
    col3_x = card_x + 652
    body_y = card_y + 68

    # Col 1: Left Encoder (LEC)
    out.append(f'  <text x="{col1_x:.1f}" y="{body_y:.1f}" class="notes-header">LEFT ENCODER (LEC)</text>')
    c1_y = body_y + 30
    out.append(f'  <text x="{col1_x:.1f}" y="{c1_y:.1f}" class="notes-badge-bold" fill="#0284c7">ROTATION BEHAVIORS</text>')
    out.append(f'  <text x="{col1_x:.1f}" y="{c1_y + 19:.1f}" class="notes-text">Default / NAV: Page Down / Page Up</text>')
    out.append(f'  <text x="{col1_x:.1f}" y="{c1_y + 37:.1f}" class="notes-text">MEDIA layer: Previous / Next track</text>')
    out.append(f'  <text x="{col1_x:.1f}" y="{c1_y + 55:.1f}" class="notes-text">MOUSE layer: Volume Down / Vol Up</text>')
    c1_y += 90
    out.append(f'  <text x="{col1_x:.1f}" y="{c1_y:.1f}" class="notes-badge-bold" fill="#0284c7">PUSH SWITCH (LEC)</text>')
    out.append(f'  <text x="{col1_x:.1f}" y="{c1_y + 19:.1f}" class="notes-text">BASE: Caps Word toggle</text>')
    out.append(f'  <text x="{col1_x:.1f}" y="{c1_y + 37:.1f}" class="notes-text">GAME: None (disabled)</text>')

    # Col 2: Right Encoder (REC)
    out.append(f'  <text x="{col2_x:.1f}" y="{body_y:.1f}" class="notes-header">RIGHT ENCODER (REC)</text>')
    c2_y = body_y + 30
    out.append(f'  <text x="{col2_x:.1f}" y="{c2_y:.1f}" class="notes-badge-bold" fill="#0d9488">ROTATION BEHAVIORS</text>')
    out.append(f'  <text x="{col2_x:.1f}" y="{c2_y + 19:.1f}" class="notes-text">Default / NAV: Volume Down / Vol Up</text>')
    out.append(f'  <text x="{col2_x:.1f}" y="{c2_y + 37:.1f}" class="notes-text">MOUSE layer: Page Down / Page Up</text>')
    c2_y += 72
    out.append(f'  <text x="{col2_x:.1f}" y="{c2_y:.1f}" class="notes-badge-bold" fill="#0d9488">PUSH SWITCH (REC)</text>')
    out.append(f'  <text x="{col2_x:.1f}" y="{c2_y + 19:.1f}" class="notes-text">BASE: Mute toggle</text>')
    out.append(f'  <text x="{col2_x:.1f}" y="{c2_y + 37:.1f}" class="notes-text">GAME: Exit to BASE (&amp;to L_BASE)</text>')

    # Col 3: Host Semantic Protocol
    out.append(f'  <text x="{col3_x:.1f}" y="{body_y:.1f}" class="notes-header">HOST PROTOCOL (F13–F24)</text>')
    c3_y = body_y + 30
    out.append(f'  <text x="{col3_x:.1f}" y="{c3_y:.1f}" class="notes-badge-bold" fill="#6366f1">CROSS-PLATFORM HID</text>')
    out.append(f'  <text x="{col3_x:.1f}" y="{c3_y + 19:.1f}" class="notes-text">F13–F17: Workspaces 1–5</text>')
    out.append(f'  <text x="{col3_x:.1f}" y="{c3_y + 37:.1f}" class="notes-text">Shift+F13..F17: Move to WS</text>')
    out.append(f'  <text x="{col3_x:.1f}" y="{c3_y + 55:.1f}" class="notes-text">Ctrl+F13..F16: Directional Focus</text>')
    out.append(f'  <text x="{col3_x:.1f}" y="{c3_y + 73:.1f}" class="notes-text">F21–F24: Copy / Paste / Cut / Undo</text>')
    c3_y += 105

    out.append(
        f'  <rect x="{col3_x - 4:.1f}" y="{c3_y - 2:.1f}" width="292" height="66" rx="6" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1" />'
    )
    out.append(f'  <text x="{col3_x + 8:.1f}" y="{c3_y + 20:.1f}" class="notes-alert-title">Host Bridge Dependency</text>')
    out.append(f'  <text x="{col3_x + 8:.1f}" y="{c3_y + 44:.1f}" class="notes-alert-desc">Requires active Karabiner or AHK bridge.</text>')

    out.append("</g>")
    return "\n".join(out)


def render_header(
    title: str,
    base_layout: str,
    color_palette: dict[str, str],
    keyboard: str = "corne",
) -> str:
    """Render top title banner and visual legend."""
    out = ['<g id="header">']

    subtitle_extra = "60 Positions · 2x Rotary Encoders" if keyboard == "sofle" else "42 Positions · 6-Thumb Layer Model"

    out.append(
        f'  <text x="{MARGIN_X:.1f}" y="52" class="title-main">{escape(title)}</text>'
    )
    out.append(
        f'  <text x="{MARGIN_X:.1f}" y="76" class="title-sub">'
        f'{escape(base_layout)} · Bilateral Home-Row Mods · Semantic F13–F24 Protocol · {subtitle_extra}'
        f'</text>'
    )

    # Top Right Legend
    legend_x = 2140
    legend_y = 52

    # 1. Colored outline: Layer transition
    out.append(
        f'  <rect x="{legend_x:.1f}" y="{legend_y - 14:.1f}" width="18" height="18" rx="3" fill="#ffffff" stroke="#0284c7" stroke-width="2" />'
    )
    out.append(
        f'  <text x="{legend_x + 26:.1f}" y="{legend_y:.1f}" class="legend-text">Layer Access / Transition</text>'
    )

    # 2. Dashed outline: Transparent
    out.append(
        f'  <rect x="{legend_x + 260:.1f}" y="{legend_y - 14:.1f}" width="18" height="18" rx="3" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="3,3" />'
    )
    out.append(
        f'  <text x="{legend_x + 286:.1f}" y="{legend_y:.1f}" class="legend-text">Transparent / Fallthrough</text>'
    )

    # 3. Faint solid: Unused
    out.append(
        f'  <rect x="{legend_x + 550:.1f}" y="{legend_y - 14:.1f}" width="18" height="18" rx="3" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1" />'
    )
    out.append(
        f'  <text x="{legend_x + 576:.1f}" y="{legend_y:.1f}" class="legend-text">Unused on this Layer</text>'
    )

    out.append("</g>")
    return "\n".join(out)


def render_cheatsheet_svg(
    model: CheatsheetModel,
    debug: bool = False,
) -> str:
    """
    Render complete A4 landscape SVG document for the cheatsheet model.
    Grid layout (3 columns x 4 rows):
      For Corne (11 layers):
        Row 0: BASE (0),    NAV (1),     MOUSE (2)
        Row 1: MEDIA (3),   NUM (4),     SYM (5)
        Row 2: FUN (6),     HOST (7),    GAME (8)
        Row 3: ADJUST (9),  GAME_FN (10), ACCESS / NOTES (11)
      For Sofle (10 layers):
        Row 0: BASE (0),    NAV (1),     MOUSE (2)
        Row 1: MEDIA (3),   NUM (4),     SYM (5)
        Row 2: FUN (6),     HOST (7),    GAME (8)
        Row 3: ADJUST (9),  ACCESS NOTES (10), ENCODER NOTES (11)
    """
    color_palette = model.presentation_config.colors
    kb = model.keyboard.lower()

    svg_parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {PAGE_WIDTH} {PAGE_HEIGHT}" width="297mm" height="210mm">',
        '  <defs>',
        '    <style><![CDATA[',
        '      /* Global Reset & Clean Typography */',
        '      text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "DejaVu Sans", Ubuntu, sans-serif; }',
        '      .title-main { font-size: 24px; font-weight: 800; fill: #0f172a; letter-spacing: 0.8px; }',
        '      .title-sub { font-size: 13px; font-weight: 500; fill: #64748b; letter-spacing: 0.2px; }',
        '      .legend-text { font-size: 13px; font-weight: 500; fill: #334155; }',
        '      .panel-title { font-size: 18px; font-weight: 800; letter-spacing: 0.8px; }',
        '      .panel-sub { font-size: 12.5px; font-weight: 500; fill: #64748b; }',
        '      .lbl-single { font-size: 26px; font-weight: 700; fill: #0f172a; text-anchor: middle; }',
        '      .lbl-word { font-weight: 600; fill: #0f172a; text-anchor: middle; }',
        '      .lbl-multi { font-weight: 600; fill: #0f172a; text-anchor: middle; }',
        '      .lbl-tap { font-weight: 700; fill: #0f172a; text-anchor: middle; }',
        '      .lbl-hold { font-weight: 600; fill: #64748b; text-anchor: middle; }',
        '      .lbl-hold-layer { font-weight: 800; text-anchor: middle; letter-spacing: 0.4px; }',
        '      .lbl-trans-only { font-weight: 800; text-anchor: middle; letter-spacing: 0.4px; }',
        '      .lbl-boot { font-weight: 800; fill: #e11d48; text-anchor: middle; letter-spacing: 0.4px; }',
        '      .lbl-trans { font-size: 18px; fill: #94a3b8; text-anchor: middle; }',
        '      .lbl-debug { font-family: "DejaVu Sans Mono", monospace; font-size: 8px; fill: #0284c7; font-weight: bold; }',
        '      .notes-header { font-size: 13.5px; font-weight: 800; fill: #0f172a; letter-spacing: 0.6px; }',
        '      .notes-badge { font-size: 13px; font-weight: 800; letter-spacing: 0.3px; }',
        '      .notes-badge-bold { font-size: 13px; font-weight: 800; letter-spacing: 0.3px; }',
        '      .notes-text { font-size: 13px; font-weight: 500; fill: #334155; }',
        '      .notes-alert-title { font-size: 12px; font-weight: 700; fill: #0284c7; }',
        '      .notes-alert-warn { font-size: 12px; font-weight: 700; fill: #e11d48; }',
        '      .notes-alert-desc { font-size: 11px; font-weight: 500; fill: #475569; }',
        '      .notes-alert-desc-warn { font-size: 11px; font-weight: 500; fill: #881337; }',
        '    ]]></style>',
        '  </defs>',
        f'  <rect x="0" y="0" width="{PAGE_WIDTH}" height="{PAGE_HEIGHT}" fill="{COLOR_BG}" />',
    ]

    # Render Header
    svg_parts.append(render_header(model.title, model.base_layout, color_palette, keyboard=kb))

    # Grid mapping for 10/11 layers
    grid_coords = [
        (0, 0),  # BASE
        (1, 0),  # NAV
        (2, 0),  # MOUSE
        (0, 1),  # MEDIA
        (1, 1),  # NUM
        (2, 1),  # SYM
        (0, 2),  # FUN
        (1, 2),  # HOST
        (2, 2),  # GAME
        (0, 3),  # ADJUST
        (1, 3),  # GAME_FN (Corne only)
    ]

    for layer_idx, layer in enumerate(model.layers):
        if layer_idx >= len(grid_coords):
            break
        col, row = grid_coords[layer_idx]
        card_x = MARGIN_X + col * (CARD_WIDTH + COL_GAP)
        card_y = GRID_Y + row * (CARD_HEIGHT + ROW_GAP)
        svg_parts.append(render_layer_panel(layer, card_x, card_y, color_palette, keyboard=kb, debug=debug))

    # Reference / Notes Panels
    if kb == "sofle":
        # Sofle: Panel 10 at (1, 3) = Access & System Notes
        p1_x = MARGIN_X + 1 * (CARD_WIDTH + COL_GAP)
        p1_y = GRID_Y + 3 * (CARD_HEIGHT + ROW_GAP)
        svg_parts.append(render_sofle_access_notes_panel(p1_x, p1_y, model, color_palette))

        # Sofle: Panel 11 at (2, 3) = Encoders & Protocol Notes
        p2_x = MARGIN_X + 2 * (CARD_WIDTH + COL_GAP)
        p2_y = GRID_Y + 3 * (CARD_HEIGHT + ROW_GAP)
        svg_parts.append(render_sofle_encoders_notes_panel(p2_x, p2_y, model, color_palette))
    else:
        # Corne: Panel 11 at (2, 3) = Notes Panel
        notes_col, notes_row = (2, 3)
        notes_card_x = MARGIN_X + notes_col * (CARD_WIDTH + COL_GAP)
        notes_card_y = GRID_Y + notes_row * (CARD_HEIGHT + ROW_GAP)
        svg_parts.append(render_corne_notes_panel(notes_card_x, notes_card_y, model, color_palette))

    svg_parts.append("</svg>")
    return "\n".join(svg_parts) + "\n"
