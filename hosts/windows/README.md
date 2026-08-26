# Windows Host Integration Guide

This guide documents the Windows integration for the semantic keyboard protocol (`F13`–`F24`).

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
```

---

## 2. Prerequisites & Installation

### 1. AutoHotkey v2 (Desktop Actions & Editing)
- Install [AutoHotkey v2](https://www.autohotkey.com/).
- Copy `hosts/windows/keyboard.ahk` to your machine.
- Place a shortcut to `keyboard.ahk` in your Windows Startup directory (`Win+R` $\rightarrow$ `shell:startup`).

### 2. GlazeWM (Tiling Window Manager)
- Install [GlazeWM](https://github.com/glzr-io/glazewm) (e.g. via `winget install glzr-io.glazewm`).
- Copy `hosts/windows/glazewm.yaml` to `%USERPROFILE%/.glzr/glazewm/config.yaml`.
- Launch GlazeWM.

### 3. Windows Terminal & Quick Terminal
- Install [Windows Terminal](https://apps.microsoft.com/detail/9n0dx20hk701).
- Open Windows Terminal Settings $\rightarrow$ **Open JSON file** (`Ctrl+Shift+,`).
- Add the action from `hosts/windows/windows-terminal-actions.jsonc` into your `"actions"` array.
- This creates the `_quake` global summon dropdown terminal triggered by `Ctrl+Alt+``` (summoned by `Alt+F14`).

---

## 3. Semantic Mapping Reference

| Semantic Signal | Windows Receiver | Action |
|-----------------|------------------|--------|
| `F13`–`F17` | GlazeWM | Focus workspace 1–5 (`WEB`, `DEV`, `COMMS`, `RUN`, `AUX`) |
| `Shift+F13`–`Shift+F17` | GlazeWM | Move focused window to workspace 1–5 and focus |
| `Ctrl+F13`–`Ctrl+F16` | GlazeWM | Focus window ← ↓ ↑ → |
| `Ctrl+Shift+F13`–`Ctrl+Shift+F16` | GlazeWM | Move window ← ↓ ↑ → |
| `Shift+F18` | GlazeWM | Enter Resize Mode |
| `Alt+F18` | GlazeWM | Enter Service Mode |
| `F18` | GlazeWM | Focus previous / recent workspace |
| `F19` | GlazeWM | Toggle fullscreen |
| `F20` | GlazeWM | Toggle floating / tiling |
| `Alt+F13` | AutoHotkey | Windows Search / Launcher (`Win+S`) |
| `Alt+F14` | AutoHotkey $\rightarrow$ Terminal | Toggle Quake dropdown terminal |
| `Alt+F15` | AutoHotkey | Launch new independent Windows Terminal (`wt.exe`) |
| `Alt+F16` | AutoHotkey | Previous Window (`Alt+Tab`) |
<!-- Editing & Application Actions -->
| `Hyper+F13` | AutoHotkey | Select All (`Ctrl+A`) |
| `Hyper+F14` | AutoHotkey | Save (`Ctrl+S`) |
| `Hyper+F15` | AutoHotkey | Find (`Ctrl+F`) |
| `Hyper+F16` | AutoHotkey | Previous Tab (`Ctrl+Shift+Tab`) |
| `Hyper+F17` | AutoHotkey | Next Tab (`Ctrl+Tab`) |
| `Hyper+F18` | AutoHotkey | New Tab (`Ctrl+T`) |
| `Hyper+F19` | AutoHotkey | Close Tab (`Ctrl+W`) |
| `Hyper+F20` | AutoHotkey | Reopen Closed Tab (`Ctrl+Shift+T`) |
| `Hyper+F21` | AutoHotkey | Word Left (`Ctrl+Left`) |
| `Hyper+F22` | AutoHotkey | Word Right (`Ctrl+Right`) |
| `Hyper+F23` | AutoHotkey | Find Next (`F3`) |
| `Hyper+F24` | AutoHotkey | Redo (`Ctrl+Y`) |
| `F21` | AutoHotkey | Copy (`Ctrl+C`) |
| `F22` | AutoHotkey | Paste (`Ctrl+V`) |
| `F23` | AutoHotkey | Cut (`Ctrl+X`) |
| `F24` | AutoHotkey | Undo (`Ctrl+Z`) |
---

## 4. Smoke Test Checklist

1. **Clipboard:** On NAV or MOUSE, press Copy (`F21`), Paste (`F22`), Cut (`F23`), Undo (`F24`), Redo (`Shift+F24`).
2. **Workspaces:** On HOST, press home-row keys (`F13`–`F17`) to switch workspaces in GlazeWM.
3. **Move to Workspace:** On HOST, press top-row keys (`Shift+F13`–`Shift+F17`) to move window and follow.
4. **Directional Focus/Move:** On HOST, press right home-row (`Ctrl+F13`–`Ctrl+F16`) and bottom-row (`Ctrl+Shift+F13`–`Ctrl+Shift+F16`).
5. **Launchers:** On HOST, press `Alt+F13` (Search), `Alt+F14` (Quick Terminal), `Alt+F15` (New Terminal).
6. **Resize & Service Modes:** On HOST, press `Shift+F18` (Resize) and `Alt+F18` (Service). Confirm `Esc`/`Enter` exit.
