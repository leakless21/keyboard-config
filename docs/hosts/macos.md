# macOS Host Integration Guide

This guide documents the macOS host configuration for the semantic keyboard protocol using **OmniWM**, **SketchyBar**, **Karabiner-Elements**, and **Ghostty**.

---

## 1. Architecture Overview

```text
                         macOS
                           │
Corne / ZMK                │
Semantic F13-F24           │
       │                   │
       ├──── WM signals ───┴──> OmniWM
       │                      Niri workspaces (1-5)
       │                      window movement & focus
       │                      cycle column width presets
       │                      fullscreen / float / overview
       │
       └──── App signals ─────> Karabiner-Elements
                                Spotlight (Alt+F13)
                                Ghostty Quick Terminal (Alt+F14)
                                Ghostty New Window (Alt+F15)
                                Language Toggle (Alt+F17)
                                Semantic Editing (F21-F24)
                                Hyper App Actions (Hyper+F13-F24)
                                Standard F1-F12 Normalization

OmniWM
  │
  └── IPC / omniwmctl
          │
          ▼
     SketchyBar
     workspace state (WEB, DEV, COMMS, RUN, AUX)
     app icons & focused window
     system status (Wi-Fi, Volume, Battery, Clock)
```

The keyboard firmware emits clean, host-agnostic semantic HID signals (`F13`–`F24`).
OmniWM directly binds raw window management signals, while Karabiner-Elements translates application shortcuts, desktop launchers, and clipboard/navigation macros. SketchyBar visualizes OmniWM state via long-lived event IPC subscriptions.

---

## 2. Installation & Prerequisites

### 1. OmniWM (Tiling & Scrolling Window Manager)
- Install [OmniWM](https://omniwm.app/):
  ```bash
  brew install --cask omniwm
  ```
- Grant required macOS permissions in **System Settings** $\rightarrow$ **Privacy & Security**:
  - **Accessibility**: enabled
  - **Input Monitoring**: enabled
  - **Screen Recording**: enabled (for Overview thumbnails)
- Recommended display configuration:
  - Enable **Displays have separate Spaces** in Mission Control.
  - Maintain **one native macOS Space per display** (OmniWM manages virtual workspaces internally, avoiding macOS space-switch animations).
  - Enable **Start at Login** in OmniWM settings.
- Symlink the canonical configuration:
  ```bash
  mkdir -p ~/.config/omniwm
  ln -sfn "$(pwd)/hosts/macos/omniwm/settings.toml" ~/.config/omniwm/settings.toml
  ```
- Restart OmniWM:
  ```bash
  killall OmniWM && open -a OmniWM
  ```

### 2. SketchyBar (Status Bar & Workspace Presenter)
- Install SketchyBar and application font:
  ```bash
  brew tap felixkratz/formulae
  brew trust felixkratz/formulae
  brew install sketchybar lua
  brew install --cask font-sketchybar-app-font font-jetbrains-mono-nerd-font
  ```
- Symlink configuration:
  ```bash
  ln -sfn "$(pwd)/hosts/macos/sketchybar" ~/.config/sketchybar
  ```
- Start SketchyBar service:
  ```bash
  brew services start sketchybar
  ```
- SketchyBar automatically starts `helpers/omniwm_watch.sh` in the background, listening to OmniWM state events (`active-workspace`, `workspace-bar`, `focus`, `display-changed`, `layout-changed`) and performing synchronized single-pass rendering.

### 3. Karabiner-Elements (Desktop & Application Bridge)
- Install [Karabiner-Elements](https://karabiner-elements.pqrs.org/).
- Copy or symlink `hosts/macos/karabiner.json` to `~/.config/karabiner/assets/complex_modifications/karabiner.json`.
- In Karabiner-Elements Settings $\rightarrow$ **Complex Modifications** $\rightarrow$ **Add rule**:
  - Enable **"Semantic Desktop Actions & Launchers"** (`Alt+F13` Spotlight, `Alt+F14` Quick Terminal, `Alt+F15` New Terminal, `Alt+F17` Language).
  - Enable **"Hyper+F13-F24 Application & Navigation Bridge"** (Hyper+F13–F24 $\rightarrow$ app actions / tabs / cursor navigation).
  - Enable **"F21-F24 Semantic Clipboard & Editing"** (F21–F24 $\rightarrow$ Cmd+C/V/X/Z with selection-safe Shift handling).
  - Enable **"Standard F1-F12 normalization for external keyboard"** (guarantees application F1–F12).
- **Note:** Karabiner does **not** intercept raw `F13`–`F20` window management signals; those pass directly to OmniWM.

### 4. Ghostty Terminal
- Install [Ghostty](https://ghostty.org/).
- Symlink or copy `hosts/macos/ghostty.config` to `~/.config/ghostty/config`:
  ```bash
  mkdir -p ~/.config/ghostty
  ln -sfn "$(pwd)/hosts/macos/ghostty.config" ~/.config/ghostty/config
  ```
- This sets up the dropdown Quick Terminal on `Ctrl+``` (`Alt+F14`).

### 5. Input Source / Language Toggle (Ctrl+Space)
- The keyboard emits `Alt+F17` for `LANGUAGE_TOGGLE`.
- Karabiner-Elements translates `Option+F17` to `Control+Space`.
- Configure macOS input source shortcut in:
  **System Settings** $\rightarrow$ **Keyboard** $\rightarrow$ **Keyboard Shortcuts** $\rightarrow$ **Input Sources** $\rightarrow$ **Select previous input source** = `Control+Space`.

---

## 3. Workspaces & Niri Layout

OmniWM operates with five persistent virtual workspaces on the Niri layout engine:

| Omni ID | Display Name | Purpose                           | Keyboard Focus | Keyboard Move & Follow |
|:-------:|:------------:|:----------------------------------|:--------------:|:----------------------:|
| 1       | **WEB**      | browser / research                | `F13`          | `Shift+F13`            |
| 2       | **DEV**      | editor + terminals                | `F14`          | `Shift+F14`            |
| 3       | **COMMS**    | chat / email / meetings           | `F15`          | `Shift+F15`            |
| 4       | **RUN**      | running apps, testing, simulators | `F16`          | `Shift+F16`            |
| 5       | **AUX**      | Finder, docs, miscellaneous       | `F17`          | `Shift+F17`            |

### Niri Scrolling Columns & Width Presets
- **Layout:** Niri horizontal scrolling strip with 2 visible containers.
- **Default Container Span:** 50% (`0.50`).
- **Width Presets:** `33%`, `50%`, `67%`, `100%` (`[0.333, 0.5, 0.667, 1.0]`).
- **Cycle Width:** Pressing `Shift+F18` cycles the focused column width forward through presets (`1/3` $\rightarrow$ `1/2` $\rightarrow$ `2/3` $\rightarrow$ `full` $\rightarrow$ `1/3`).
- **Vertical Stacking:** Columns can contain multiple vertically stacked windows. Use `Ctrl+F14`/`Ctrl+F15` to navigate up/down within a column, and `Ctrl+F13`/`Ctrl+F16` to scroll columns horizontally.
- **Overview:** Pressing `Alt+F18` (`Option+F18`) opens OmniWM's Overview thumbnail view.
- **Fullscreen & Floating:** `F19` toggles fullscreen, and `F20` toggles floating.
- **Previous Window:** `Alt+F16` switches to the previously focused window across workspaces.

---

## 4. SketchyBar Integration

SketchyBar is organized in a modular Lua layout (`hosts/macos/sketchybar/`):

- **`sketchybarrc`:** Executable launcher invoking `init.lua`.
- **`colors.lua`:** Full Catppuccin Mocha palette with semantic pill tokens.
- **`icons.lua`:** Nerd Font and application glyph mapping (`JetBrainsMono Nerd Font`).
- **`bar.lua`:** Global bar geometry (height 32, blur 20, Catppuccin mantle background).
- **`items/workspaces.lua`:** Five workspace pills (WEB, DEV, COMMS, RUN, AUX) with live occupied app icons.
- **`items/workspaces_updater.lua`:** Single-pass event-driven parser that queries OmniWM and updates all 5 pills in one batch command.
- **`items/front_app.lua`:** Centered active application name and window title.
- **`items/media.lua`:** Centered media title/artist when audio is playing.
- **`items/status.lua`:** Right-side status indicators: Wi-Fi, Volume, Battery, and Clock.
- **`helpers/omniwm_watch.sh`:** Reconnecting `omniwmctl watch` daemon forwarding OmniWM state changes to `omniwm_state_changed`.

---

## 5. Standard F1–F12 Normalization

Karabiner-Elements normalizes incoming `F1`–`F12` from external keyboards:
1. Evaluates `system.use_fkeys_as_standard_function_keys` to ensure standard application function keys work regardless of macOS system media key settings.
2. Preserves mirrored modifiers (`Shift`, `Ctrl`, `Alt`, `Cmd`).
3. Scoped with `is_built_in_keyboard: false` to isolate external keyboards from built-in MacBook keys.
