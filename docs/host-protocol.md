# Semantic Host Protocol Specification (F13–F24)

This document is the canonical source of truth for the semantic high-function key protocol (`F13`–`F24`) shared by all keyboards in this repository.

---

## 1. Canonical Protocol Matrix

| Signal | Semantic Action | macOS Host (Karabiner + AeroSpace + Ghostty + Spotlight) | Windows Host (GlazeWM + AutoHotkey + Windows Terminal + Search) |
|---|---|---|---|
| `F13` | Switch to workspace 1 (WEB) | AeroSpace: alt-1 (Workspace 1) | GlazeWM: focus --workspace 1 |
| `F14` | Switch to workspace 2 (DEV) | AeroSpace: alt-2 (Workspace 2) | GlazeWM: focus --workspace 2 |
| `F15` | Switch to workspace 3 (COMMS) | AeroSpace: alt-3 (Workspace 3) | GlazeWM: focus --workspace 3 |
| `F16` | Switch to workspace 4 (RUN) | AeroSpace: alt-4 (Workspace 4) | GlazeWM: focus --workspace 4 |
| `F17` | Switch to workspace 5 (AUX) | AeroSpace: alt-5 (Workspace 5) | GlazeWM: focus --workspace 5 |
| `Shift+F13` | Move active window to workspace 1 and follow | AeroSpace: alt-shift-1 (Move to 1 and follow) | GlazeWM: move --workspace 1; focus --workspace 1 |
| `Shift+F14` | Move active window to workspace 2 and follow | AeroSpace: alt-shift-2 (Move to 2 and follow) | GlazeWM: move --workspace 2; focus --workspace 2 |
| `Shift+F15` | Move active window to workspace 3 and follow | AeroSpace: alt-shift-3 (Move to 3 and follow) | GlazeWM: move --workspace 3; focus --workspace 3 |
| `Shift+F16` | Move active window to workspace 4 and follow | AeroSpace: alt-shift-4 (Move to 4 and follow) | GlazeWM: move --workspace 4; focus --workspace 4 |
| `Shift+F17` | Move active window to workspace 5 and follow | AeroSpace: alt-shift-5 (Move to 5 and follow) | GlazeWM: move --workspace 5; focus --workspace 5 |
| `Ctrl+F13` | Focus window to the left | AeroSpace: alt-h (Focus left) | GlazeWM: focus --direction left |
| `Ctrl+F14` | Focus window below | AeroSpace: alt-j (Focus down) | GlazeWM: focus --direction down |
| `Ctrl+F15` | Focus window above | AeroSpace: alt-k (Focus up) | GlazeWM: focus --direction up |
| `Ctrl+F16` | Focus window to the right | AeroSpace: alt-l (Focus right) | GlazeWM: focus --direction right |
| `Ctrl+Shift+F13` | Move active window to the left | AeroSpace: alt-shift-h (Move left) | GlazeWM: move --direction left |
| `Ctrl+Shift+F14` | Move active window down | AeroSpace: alt-shift-j (Move down) | GlazeWM: move --direction down |
| `Ctrl+Shift+F15` | Move active window up | AeroSpace: alt-shift-k (Move up) | GlazeWM: move --direction up |
| `Ctrl+Shift+F16` | Move active window to the right | AeroSpace: alt-shift-l (Move right) | GlazeWM: move --direction right |
| `F18` | Focus previous / recent workspace | AeroSpace: alt-tab (workspace-back-and-forth) | GlazeWM: focus --recent-workspace |
| `Shift+F18` | Enter directional resize modal mode | AeroSpace: alt-r (mode resize) | GlazeWM: wm-enable-binding-mode --name resize |
| `Alt+F18` | Enter WM management / service mode | AeroSpace: alt-shift-semicolon (mode service) | GlazeWM: wm-enable-binding-mode --name service |
| `F19` | Toggle active window fullscreen | AeroSpace: alt-f (fullscreen) | GlazeWM: toggle-fullscreen |
| `F20` | Toggle active window float / tile | AeroSpace: alt-shift-space (layout floating tiling) | GlazeWM: toggle-floating --centered |
| `Alt+F13` | Summon system search / launcher (Spotlight / Windows Search) | Karabiner: Cmd+Space (Spotlight) | AutoHotkey: Win+S (Windows Search) |
| `Alt+F14` | Toggle quick dropdown scratchpad terminal (Quake mode) | Karabiner: Ctrl+` (Ghostty Quick Terminal) | AutoHotkey: Windows Terminal _quake dropdown |
| `Alt+F15` | Launch new independent terminal window | Karabiner: Alt+Enter (Ghostty new window) | AutoHotkey: wt.exe new window |
| `Alt+F16` | Switch to previous active window across workspaces | Karabiner: Alt+` (AeroSpace focus-back-and-forth) | AutoHotkey: Alt+Tab (Previous Window) |
| `Alt+F17` | Toggle primary input language / input method | Karabiner: Ctrl+Space (switch input source) | AutoHotkey: trigger configured EVKey E/V toggle |
| `F21` | Copy selected text to clipboard | Karabiner: Cmd+C | AutoHotkey: Ctrl+C |
| `F22` | Paste text from clipboard | Karabiner: Cmd+V | AutoHotkey: Ctrl+V |
| `F23` | Cut selected text to clipboard | Karabiner: Cmd+X | AutoHotkey: Ctrl+X |
| `F24` | Undo last text action | Karabiner: Cmd+Z | AutoHotkey: Ctrl+Z |
| `Shift+F24` | Redo last undone text action | Karabiner: Cmd+Shift+Z | AutoHotkey: Ctrl+Y |
---

## 2. Protocol Producers

Both keyboards implement the full protocol:
1. **`config/corne.keymap`:** Emits `F13`–`F20` on `HOST`, `F21`–`F24` on `NAV` and `MOUSE`.
2. **`config/sofle.keymap`:** Emits `F13`–`F20` on `HOST`, `F21`–`F24` on `NAV` and `MOUSE`.

## 3. Protocol Consumers

1. **macOS Host Adapters:**
   - **`hosts/macos/karabiner.json`:** Device-scoped complex rules translating high-function keys to macOS chords.
   - **`hosts/macos/aerospace.toml`:** AeroSpace window manager configuration consuming `main`, `resize`, and `service` modes.
   - **`hosts/macos/ghostty.config`:** Ghostty terminal configuration with dropdown toggle.

2. **Windows Host Adapters:**
   - **`hosts/windows/keyboard.ahk`:** AutoHotkey v2 script translating clipboard, launcher, and terminal signals.
   - **`hosts/windows/glazewm.yaml`:** GlazeWM window manager configuration natively consuming `F13`–`F20` signals and binding modes.
   - **`hosts/windows/windows-terminal-actions.jsonc`:** Windows Terminal action snippet for `_quake` global summon.

---

## 4. Design Decisions & Implementation Notes

### Cross-Platform Language Toggle (`Alt+F17 = LANGUAGE_TOGGLE`)
- **Firmware Emission:** Emits `&kp LA(F17)` (`Alt+F17`) from the launcher row on the `HOST` layer.
- **macOS Translation:** Karabiner maps `Option+F17` $\rightarrow$ `Control+Space` (macOS native input source toggle).
- **Windows Translation:** AutoHotkey maps `Alt+F17` $\rightarrow$ `ToggleInputLanguage()` (triggering EVKey E/V toggle via `Ctrl+Shift`).
- **Why `&kp GLOBE` is intentionally not used in firmware:**
  - Apple-oriented behavior with platform-specific caveats.
  - Not a reliable or standard interface for Windows or IME engines like EVKey / UniKey.
  - Semantic host translation delivers identical physical muscle memory while allowing each OS to handle input switching natively.
