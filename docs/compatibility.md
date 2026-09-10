# Host & Firmware Compatibility Matrix

This document tracks tested, validated versions of all upstream firmware modules, host window managers, bridges, and terminal applications.

---

## 1. Tested Version Matrix

| Component | Tested Version / SHA | Tested Date | Role | Configuration Path |
|---|---|---|---|---|
| **ZMK Firmware** | `6e2ef41e022d555b10f116e395832913f71717b3` | 2026-08-22 | Core keyboard firmware | `config/west.yml` |
| **zmk-helpers** | `95edb8f15ef1d1bd8332810555f8cf5837fbdd27` | 2026-08-22 | Key labels & layer macros | `config/west.yml` |
| **zmk-nice-oled** | `de5b2afbd05f1a136e31ca28659373cd07d1e443` | 2026-08-22 | OLED display widgets & status | `config/west.yml` |
| **keymap-drawer** | `0.23.0` (`a44809b8cc718cbff646641f49a8f71a9368336d`) | 2026-08-22 | Keymap diagram rendering | `.github/workflows/draw-keymap.yml` |
| **OmniWM** | `0.6.8+` (schema v3) | 2026-09-10 | macOS Tiling & Scrolling Window Manager | `hosts/macos/omniwm/settings.toml` |
| **SketchyBar** | `2.24.0+` | 2026-09-10 | macOS Status Bar & Workspace Presenter | `hosts/macos/sketchybar/` |
| **Karabiner-Elements** | `15.3.0+` | 2026-08-22 | macOS HID Translation Bridge | `hosts/macos/karabiner.json` |
| **Ghostty** | `1.1.0+` | 2026-08-22 | macOS Terminal & Scratchpad | `hosts/macos/ghostty.config` |
| **GlazeWM** | `3.9.0+` (modern schema) | 2026-08-22 | Windows Tiling Window Manager | `hosts/windows/glazewm.yaml` |
| **AutoHotkey** | `v2.0.18+` | 2026-08-22 | Windows Desktop Bridge | `hosts/windows/keyboard.ahk` |
| **Windows Terminal** | `1.22.0+` | 2026-08-22 | Windows Terminal & Quake mode | `hosts/windows/windows-terminal-actions.jsonc` |

---

## 2. Upgrade & Maintenance Procedures

Always upgrade **one external component at a time** to maintain deterministic regression isolation.

### A. Upgrading Firmware Dependencies (ZMK / Modules)
1. In `config/west.yml`, update the project revision SHA.
2. If upgrading `zmk`, update the matching reusable workflow SHA in `.github/workflows/build.yml`.
3. Run local build config validation:
   ```bash
   uv run scripts/check_build_config.py
   ```
4. Push to a branch, build all 5 target artifacts (`corne-left`, `corne-right`, `sofle-left`, `sofle-right`, `settings-reset`).
5. Flash **both halves** of the target keyboard.
6. Perform manual firmware smoke tests (see [docs/development.md](development.md)).
7. Update the version SHA and date in this file.

### B. Upgrading GlazeWM (Windows)
1. Review GlazeWM upstream release notes for command syntax or schema changes.
2. Update `hosts/windows/glazewm.yaml`.
3. Run protocol validation:
   ```bash
   uv run scripts/check_host_protocol.py
   ```
4. Reload GlazeWM on Windows host and exercise all workspace, navigation, resize, and service shortcuts.
5. Update tested version in this file.

### C. Upgrading OmniWM, SketchyBar, or Karabiner (macOS)
1. Review upstream release notes.
2. If necessary, adjust `hosts/macos/omniwm/settings.toml`, `hosts/macos/sketchybar/`, or `hosts/macos/karabiner.json`.
3. Run protocol validation:
   ```bash
   uv run scripts/check_host_protocol.py
   ```
4. Perform smoke test on macOS.
5. Update tested version in this file.
