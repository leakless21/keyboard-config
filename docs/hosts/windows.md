# Windows Host Integration Guide

This guide documents the Windows host configuration for the semantic keyboard protocol using GlazeWM, AutoHotkey v2, Windows Terminal, and Windows Search.

---

## 1. Architecture Overview

```text
Keyboard (Corne / Sofle)
      ↓
Semantic F13–F24 HID Signals
      │
      ├───────────────────────────────┐
      ▼                               ▼
   GlazeWM                        AutoHotkey v2
(Window Management)             (Desktop Actions & Editing)
      │                               │
  Workspaces 1–5                  Clipboard (F21–F24)
  Focus & Move                    Windows Search (Alt+F13)
  Resize Mode                     Quick Terminal summon (Alt+F14)
  Service Mode                    New Terminal window (Alt+F15)
  Fullscreen & Float              Previous Window (Alt+F16)
                                  Language Toggle (Alt+F17)
```

---

## 2. Installation & Setup

### 1. AutoHotkey v2 (Desktop Actions & Editing)
- Install [AutoHotkey v2](https://www.autohotkey.com/).
- Copy `hosts/windows/keyboard.ahk` to your Windows system.
- Place a shortcut to `keyboard.ahk` in your Windows Startup directory (`Win+R` $\rightarrow$ `shell:startup`).
- **Input Language / EVKey Toggle (`Alt+F17`):** AutoHotkey maps `Alt+F17` to `ToggleInputLanguage()`, which simulates `Ctrl+Shift` (or your chosen EVKey toggle hotkey). Ensure EVKey is configured with the matching toggle shortcut.

### 2. GlazeWM (Tiling Window Manager)
- Install [GlazeWM](https://github.com/glzr-io/glazewm) (e.g., `winget install glzr-io.glazewm`).
- Copy `hosts/windows/glazewm.yaml` to `%USERPROFILE%/.glzr/glazewm/config.yaml`.
- Launch GlazeWM.

### 3. Windows Terminal & Quick Terminal (Quake Mode)
- Install [Windows Terminal](https://apps.microsoft.com/detail/9n0dx20hk701).
- Open Settings $\rightarrow$ **Open JSON file** (`Ctrl+Shift+,`).
- Add the action snippet from `hosts/windows/windows-terminal-actions.jsonc` into your `"actions"` array.
- This creates the `_quake` global summon dropdown terminal triggered by `Ctrl+Alt+``` (summoned via `Alt+F14`).

---

## 3. Workspaces & Modal Operations

GlazeWM operates with five virtual workspaces:
- `1` / `WEB` (`F13`)
- `2` / `DEV` (`F14`)
- `3` / `COMMS` (`F15`)
- `4` / `RUN` (`F16`)
- `5` / `AUX` (`F17`)

### Binding Modes:
- **`resize` Mode (`Shift+F18`):** Directional window resize ($\pm 50$ px) via `Ctrl+F13..F16` or `H/J/K/L`. Exit with `Esc` or `Enter`.
- **`service` Mode (`Alt+F18`):** Move workspace to next/prev monitor (`Ctrl+F16`/`Ctrl+F13`), reload config (`F19`), redraw (`F20`). Exit with `Esc` or `Enter`.
