# macOS Host Integration Guide

This guide documents the canonical macOS host configuration for the semantic keyboard protocol using **OmniWM**, **SketchyBar**, **Karabiner-Elements**, and **Ghostty**.

---

## 1. Architecture Overview

```text
                         macOS
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
     CORNE                               MACBOOK
 semantic HID                         normal keyboard
 F13–F24                                  │
        │                                 │
        │                     Karabiner laptop adapter
        │                                 │
        └──────────── semantic HID ◄───────┘
                           │
             ┌─────────────┴─────────────┐
             │                           │
          OmniWM                     Karabiner
     WM + Quake Terminal          OS/app semantics
             │                           │
             │                       Spotlight
             │                       Ghostty new window
             │                       language
             │                       editing/tabs
             │
             └──── IPC ──────► SketchyBar
                               visual state
```

### Key Architectural Invariants
1. **OmniWM is the Complete Window Environment & Scratch Terminal:**
   - OmniWM directly consumes all window management signals (`F13`–`F20` combinations).
   - **`Option+F14` is a native OmniWM semantic action** opening the embedded libghostty Quake terminal (`[quakeTerminal]`). It no longer routes through Karabiner or Ghostty.
2. **Ghostty is Exclusively for Standalone Windows:**
   - Ghostty Quick Terminal is completely disabled.
   - `Option+F15` creates a new independent Ghostty window via AppleScript automation (`osascript -e 'tell application "Ghostty" to activate' -e 'tell application "Ghostty" to new window'`).
3. **Karabiner is Divided into Modular Adapters:**
   - `hosts/macos/karabiner/external-semantic.json`: Scoped to external keyboards (`is_built_in_keyboard: false`). Translates OS launchers (Spotlight, Ghostty window, Language), Hyper app actions, semantic editing (F21–F24), and F1–F12 normalizers. Does **not** intercept raw WM or Quake signals.
   - `hosts/macos/karabiner/laptop-omniwm.json`: Scoped to the built-in keyboard (`is_built_in_keyboard: true`). Adapts standard MacBook chords into the exact same semantic F13–F20 signals consumed by OmniWM.
4. **SketchyBar is Notch-Aware and Event-Driven:**
   - Visualizes multi-monitor workspace state with compact pills.
   - Front application sits at `q` (left of notch) and media sits at `e` (right of notch), coexisting seamlessly without mutual hiding.
   - Application glyphs rendered using **SketchyBar App Font** (`sketchybar-app-font`).
   - Simplified, low-overhead status items: Wi-Fi (icon only), Volume (icon only), Battery (icon + %), Clock (HH:mm, 60s frequency).
   - Robust POSIX shell escaping for all dynamic strings (`hosts/macos/sketchybar/lib/shell.lua`).

---

## 2. Installation & Configuration

### 1. OmniWM (Tiling Window Manager & Quake Terminal)
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

### 2. Quake Terminal Configuration
OmniWM's embedded Quake terminal is configured in `hosts/macos/omniwm/settings.toml`:
```toml
[quakeTerminal]
enabled = true
position = "top"
widthPercent = 90.0
heightPercent = 50.0
monitorMode = "focusedWindow"
autoHide = true
opacity = 0.94
backgroundEffect = "standardBlur"
backgroundBlurRadius = 18
animationDuration = 0.0

[[hotkeys]]
binding = "Option+F14"
id = "toggleQuakeTerminal"
```

*Note on Testing:* OmniWM stores manually adjusted Quake window dimensions in its runtime state rather than `settings.toml`. To ensure deterministic acceptance testing, reset the Quake window frame before evaluating.

Inside OmniWM's Quake terminal, native ghostty tabs and splits are supported:
- `Cmd+T` / `Cmd+W`: New tab / close tab
- `Cmd+Shift+[` / `Cmd+Shift+]`: Previous / next tab
- `Cmd+D` / `Cmd+Shift+D`: Split horizontal / split vertical
- `Cmd+Shift+W`: Close split pane
- `Cmd+Option+Arrows`: Navigate split panes

### 3. Ghostty Terminal (Standalone Windows)
- Install [Ghostty](https://ghostty.org/).
- Symlink `hosts/macos/ghostty.config` to `~/.config/ghostty/config`:
  ```bash
  mkdir -p ~/.config/ghostty
  ln -sfn "$(pwd)/hosts/macos/ghostty.config" ~/.config/ghostty/config
  ```
- Standalone configuration:
  ```text
  theme = Catppuccin Mocha
  background = #161616
  background-opacity = 0.8
  background-blur = true
  background-blur-radius = 20
  ```
- Quick Terminal is disabled in Ghostty. All global dropdown terminal summons route through OmniWM.

### 4. Karabiner-Elements Adapters
Install [Karabiner-Elements](https://karabiner-elements.pqrs.org/).
Symlink or copy both adapter rule files to `~/.config/karabiner/assets/complex_modifications/`:
```bash
mkdir -p ~/.config/karabiner/assets/complex_modifications
ln -sfn "$(pwd)/hosts/macos/karabiner/external-semantic.json" ~/.config/karabiner/assets/complex_modifications/external-semantic.json
ln -sfn "$(pwd)/hosts/macos/karabiner/laptop-omniwm.json" ~/.config/karabiner/assets/complex_modifications/laptop-omniwm.json
```
In Karabiner-Elements Settings $\rightarrow$ **Complex Modifications** $\rightarrow$ **Add rule**:
1. Enable rules from **"Keyboard Semantic Host Bridge - External"** for external keyboards.
2. Enable rules from **"MacBook Built-in Keyboard OmniWM Adapter"** for the built-in keyboard.

### 5. SketchyBar Setup
- Install dependencies:
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
  brew services restart sketchybar
  ```

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

## 4. MacBook Built-in Keyboard & Trackpad Workflow

The built-in MacBook keyboard adapter allows full daily-driving of the OmniWM environment without the physical Corne keyboard:

| Built-in Key Chord | Semantic Protocol Output | OmniWM Action |
|---|---|---|
| `⌥ 1` … `5` | `F13` … `F17` | Switch to workspace 1–5 |
| `⌥ ⇧ 1` … `5` | `Shift+F13` … `Shift+F17` | Move active window to workspace 1–5 |
| `⌥ H / J / K / L` | `Ctrl+F13 / F14 / F15 / F16` | Focus Left / Down / Up / Right |
| `⌥ ⇧ H / J / K / L` | `Ctrl+Shift+F13 / F14 / F15 / F16` | Move Left / Down / Up / Right |
| `⌃ ⌥ Tab` | `F18` | Previous workspace back-and-forth |
| `⌥ Tab` | `Option+F16` | Focus previous window across workspaces |
| `⌥ .` | `Shift+F18` | Cycle column width forward |
| `⌥ ⇧ O` | `Option+F18` | Toggle OmniWM Overview |
| `⌥ Return` | `F19` | Toggle fullscreen |
| `⌥ ⇧ Space` | `F20` | Toggle focused window floating |
| `⌥ \`` | `Option+F14` | Toggle native Quake terminal |

### Laptop Trackpad Gestures
Configured in `hosts/macos/omniwm/settings.toml`:
- `workspaceSwipeEnabled = true`
- **3-Finger Horizontal Swipe:** Scrolls Niri columns.
- **3-Finger Vertical Swipe:** Cycles OmniWM virtual workspaces.

---

## 5. SketchyBar Notch-Aware Layout

### Bar Geometry
- **Height:** 32px
- **Notch Height & Width:** `notch_display_height=32`, `notch_width=180`
- **Color:** Transparent (`0x00000000`), no global bar background or blur strip; backgrounds are drawn exclusively around logical item groups.

### Layout Across Displays
- **Internal Notched Display:**
  - `front_app` is placed at `q` (left of notch): displays current app icon + clean name (e.g. ` Ghostty`).
  - `media` is placed at `e` (right of notch): displays `♫ Song Title` when playing.
  - Notch area remains clear. Both items coexist without mutual hiding.
- **External Display:**
  - `front_app` dynamically relocates to `center`.
  - `media` renders compactly adjacent or drawing=off when idle.

### Compact Workspace Rendering Rules
- **ACTIVE:** Number + semantic name + app icons (e.g. `[2 DEV   󰨞]`, lavender pill).
- **OCCUPIED:** Number + app icons only (e.g. `[1 ]`, surface0 pill, no redundant name).
- **EMPTY:** Number only (e.g. `[4]`, transparent background).

### Typography
- **SF Pro:** Regular labels and titles.
- **JetBrains Mono Nerd Font:** Status and control glyphs.
- **SketchyBar App Font:** Automatic application icons via ligature lookup (`hosts/macos/sketchybar/lib/app_icons.lua`).
