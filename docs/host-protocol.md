# Semantic Host Protocol Specification (F13–F24)

This document is the canonical source of truth for the semantic high-function key protocol (`F13`–`F24`) shared by all keyboards in this repository.

---

## 1. Canonical Protocol Matrix

| Signal | Semantic Action | macOS Host (OmniWM + Karabiner + Ghostty + Spotlight) | Windows Host (GlazeWM + AutoHotkey + Windows Terminal + Search) |
|---|---|---|---|
| `F13` | Switch to workspace 1 (WEB) | OmniWM: switch-workspace 1 (F13) | GlazeWM: focus --workspace 1 |
| `F14` | Switch to workspace 2 (DEV) | OmniWM: switch-workspace 2 (F14) | GlazeWM: focus --workspace 2 |
| `F15` | Switch to workspace 3 (COMMS) | OmniWM: switch-workspace 3 (F15) | GlazeWM: focus --workspace 3 |
| `F16` | Switch to workspace 4 (RUN) | OmniWM: switch-workspace 4 (F16) | GlazeWM: focus --workspace 4 |
| `F17` | Switch to workspace 5 (AUX) | OmniWM: switch-workspace 5 (F17) | GlazeWM: focus --workspace 5 |
| `Shift+F13` | Move active window to workspace 1 and follow | OmniWM: move-to-workspace 1 and follow (Shift+F13) | GlazeWM: move --workspace 1; focus --workspace 1 |
| `Shift+F14` | Move active window to workspace 2 and follow | OmniWM: move-to-workspace 2 and follow (Shift+F14) | GlazeWM: move --workspace 2; focus --workspace 2 |
| `Shift+F15` | Move active window to workspace 3 and follow | OmniWM: move-to-workspace 3 and follow (Shift+F15) | GlazeWM: move --workspace 3; focus --workspace 3 |
| `Shift+F16` | Move active window to workspace 4 and follow | OmniWM: move-to-workspace 4 and follow (Shift+F16) | GlazeWM: move --workspace 4; focus --workspace 4 |
| `Shift+F17` | Move active window to workspace 5 and follow | OmniWM: move-to-workspace 5 and follow (Shift+F17) | GlazeWM: move --workspace 5; focus --workspace 5 |
| `Ctrl+F13` | Focus window to the left | OmniWM: focus left (Ctrl+F13) | GlazeWM: focus --direction left |
| `Ctrl+F14` | Focus window below | OmniWM: focus down (Ctrl+F14) | GlazeWM: focus --direction down |
| `Ctrl+F15` | Focus window above | OmniWM: focus up (Ctrl+F15) | GlazeWM: focus --direction up |
| `Ctrl+F16` | Focus window to the right | OmniWM: focus right (Ctrl+F16) | GlazeWM: focus --direction right |
| `Ctrl+Shift+F13` | Move active window to the left | OmniWM: move left (Ctrl+Shift+F13) | GlazeWM: move --direction left |
| `Ctrl+Shift+F14` | Move active window down | OmniWM: move down (Ctrl+Shift+F14) | GlazeWM: move --direction down |
| `Ctrl+Shift+F15` | Move active window up | OmniWM: move up (Ctrl+Shift+F15) | GlazeWM: move --direction up |
| `Ctrl+Shift+F16` | Move active window to the right | OmniWM: move right (Ctrl+Shift+F16) | GlazeWM: move --direction right |
| `F18` | Focus previous / recent workspace | OmniWM: switch-workspace back-and-forth (F18) | GlazeWM: focus --recent-workspace |
| `Shift+F18` | Cycle window size forward (OmniWM) / modal resize (GlazeWM) | OmniWM: cycle-size forward (Shift+F18) | GlazeWM: wm-enable-binding-mode --name resize |
| `Alt+F18` | Toggle overview (OmniWM) / service mode (GlazeWM) | OmniWM: toggle-overview (Option+F18) | GlazeWM: wm-enable-binding-mode --name service |
| `F19` | Toggle active window fullscreen | OmniWM: toggle-fullscreen (F19) | GlazeWM: toggle-fullscreen |
| `F20` | Toggle active window float / tile | OmniWM: toggle-focused-window-floating (F20) | GlazeWM: toggle-floating --centered |
| `Alt+F13` | Summon system search / launcher (Spotlight / Windows Search) | Karabiner: Cmd+Space (Spotlight) | AutoHotkey: Win+S (Windows Search) |
| `Alt+F14` | Toggle quick dropdown scratchpad terminal (Quake mode) | Karabiner: Ctrl+` (Ghostty Quick Terminal) | AutoHotkey: Windows Terminal _quake dropdown |
| `Alt+F15` | Launch new independent terminal window | Karabiner: Alt+Enter (Ghostty new window) | AutoHotkey: wt.exe new window |
| `Alt+F16` | Switch to previous active window across workspaces | OmniWM: focus previous (Option+F16) | AutoHotkey: Alt+Tab (Previous Window) |
| `Alt+F17` | Toggle primary input language / input method | Karabiner: Ctrl+Space (switch input source) | AutoHotkey: trigger configured EVKey E/V toggle |
| `F21` | Copy selected text to clipboard | Karabiner: Cmd+C | AutoHotkey: Ctrl+C |
| `F22` | Paste text from clipboard | Karabiner: Cmd+V | AutoHotkey: Ctrl+V |
| `F23` | Cut selected text to clipboard | Karabiner: Cmd+X | AutoHotkey: Ctrl+X |
| `F24` | Undo last text action | Karabiner: Cmd+Z | AutoHotkey: Ctrl+Z |
| `Ctrl+Alt+Shift+Gui+F13` | Select all text or items in active context | Karabiner: Cmd+A (Select All) | AutoHotkey: Ctrl+A (Select All) |
| `Ctrl+Alt+Shift+Gui+F14` | Save active file or document | Karabiner: Cmd+S (Save) | AutoHotkey: Ctrl+S (Save) |
| `Ctrl+Alt+Shift+Gui+F15` | Open in-context search / find | Karabiner: Cmd+F (Find) | AutoHotkey: Ctrl+F (Find) |
| `Ctrl+Alt+Shift+Gui+F16` | Switch to previous tab in active application | Karabiner: Cmd+Shift+[ (Previous Tab) | AutoHotkey: Ctrl+Shift+Tab (Previous Tab) |
| `Ctrl+Alt+Shift+Gui+F17` | Switch to next tab in active application | Karabiner: Cmd+Shift+] (Next Tab) | AutoHotkey: Ctrl+Tab (Next Tab) |
| `Ctrl+Alt+Shift+Gui+F18` | Open new tab in active application | Karabiner: Cmd+T (New Tab) | AutoHotkey: Ctrl+T (New Tab) |
| `Ctrl+Alt+Shift+Gui+F19` | Close active tab in application | Karabiner: Cmd+W (Close Tab) | AutoHotkey: Ctrl+W (Close Tab) |
| `Ctrl+Alt+Shift+Gui+F20` | Reopen last closed tab in application | Karabiner: Cmd+Shift+T (Reopen Tab) | AutoHotkey: Ctrl+Shift+T (Reopen Tab) |
| `Ctrl+Alt+Shift+Gui+F21` | Move text cursor one word to the left | Karabiner: Option+Left (Word Left) | AutoHotkey: Ctrl+Left (Word Left) |
| `Ctrl+Alt+Shift+Gui+F22` | Move text cursor one word to the right | Karabiner: Option+Right (Word Right) | AutoHotkey: Ctrl+Right (Word Right) |
| `Ctrl+Alt+Shift+Gui+F23` | Jump to next search match | Karabiner: Cmd+G (Find Next) | AutoHotkey: F3 (Find Next) |
| `Ctrl+Alt+Shift+Gui+F24` | Redo last undone text action | Karabiner: Cmd+Shift+Z (Redo) | AutoHotkey: Ctrl+Y (Redo) |

---

## 2. Protocol Producers

Both keyboards implement the full protocol:
1. **`config/corne.keymap`:** Emits `F13`–`F20` on `HOST`, `F21`–`F24` on `NAV` and `MOUSE`.
2. **`config/sofle.keymap`:** Emits `F13`–`F20` on `HOST`, `F21`–`F24` on `NAV` and `MOUSE`.

## 3. Protocol Consumers

1. **macOS Host Adapters:**
   - **`hosts/macos/omniwm/settings.toml`:** OmniWM window manager configuration consuming raw `F13`–`F20` signals for Niri workspaces, directional focus/movement, cycle size, overview, fullscreen, and float.
   - **`hosts/macos/sketchybar/`:** SketchyBar configuration driven by OmniWM IPC events for workspace state, app icons, and system status.
   - **`hosts/macos/karabiner.json`:** Device-scoped complex rules translating desktop launchers, Hyper+F13–F24 application actions, F21–F24 editing, and F1–F12 normalization (raw WM signals pass directly to OmniWM).
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
