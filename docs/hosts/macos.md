# macOS Host Integration Guide

This guide documents the canonical macOS host configuration for the semantic keyboard protocol using **OmniWM**, **Karabiner-Elements**, and **Ghostty** alongside the **native macOS menu bar**.

For the daily workflow, use the generated [macOS / OmniWM workflow cheatsheet](../generated/macos-omniwm-cheatsheet.svg) or its [printable PDF](../generated/macos-omniwm-cheatsheet.pdf). The Corne and Sofle sheets remain keyboard-layer references.

---

## 1. Architecture Overview

```text
                         macOS
                           │
       ┌───────────────────┴───────────────────┐
       │                                       │
     CORNE                                  MACBOOK
 semantic HID F13–F20               conventional Option chords
       │                                       │
       │                               Karabiner laptop adapter
       │                                       │
       │                                  OmniWM IPC
       │                           (/Applications/OmniWM.app/…/omniwmctl)
       │                                       │
       └───────────────────┬───────────────────┘
                           │
                         OmniWM
              logical actions + Quake terminal
                           │
              ┌────────────┴────────────┐
              │                         │
           OmniWM                  Karabiner external
      WM + Quake Terminal          OS/app semantics
```

Both input paths invoke the same logical OmniWM actions. Transport is intentionally asymmetric:

```text
Corne
  └─ semantic F13–F20 HID
       └─ OmniWM hotkey consumer

MacBook built-in keyboard
  └─ conventional Option shortcuts
       └─ Karabiner-Elements
            └─ OmniWM IPC (omniwmctl command …)
```

### Key Architectural Invariants
1. **OmniWM is the Complete Window Environment & Scratch Terminal:**
   - OmniWM consumes Corne window-management signals directly as raw `F13`–`F20` hotkeys.
   - OmniWM consumes MacBook window-management actions via IPC (`omniwmctl command …`). Both paths invoke the same logical actions.
   - **`Option+F14` / `toggle-quake-terminal` is a native OmniWM semantic action** opening the embedded libghostty Quake terminal (`[quakeTerminal]`). It no longer routes through Karabiner or Ghostty.
2. **Ghostty is Exclusively for Standalone Windows:**
   - Ghostty Quick Terminal is completely disabled.
   - `Option+F15` creates a new independent Ghostty window via AppleScript automation (`osascript -e 'tell application "Ghostty" to activate' -e 'tell application "Ghostty" to new window'`).
3. **Karabiner is Divided into Modular Adapters:**
   - `hosts/macos/karabiner/external-semantic.json`: Scoped to external keyboards (`is_built_in_keyboard: false`). Translates OS launchers (Spotlight, Ghostty window, Language), Hyper app actions, semantic editing (F21–F24), and F1–F12 normalizers. Does **not** intercept raw WM or Quake signals.
   - `hosts/macos/karabiner/laptop-omniwm.json`: Scoped to the built-in keyboard (`is_built_in_keyboard: true`). Maps conventional MacBook `Option` chords to OmniWM IPC (`/Applications/OmniWM.app/Contents/MacOS/omniwmctl command …`).
     - **Option is never a mandatory modifier.** Karabiner removes mandatory modifiers from `to` events ("Mandatory modifiers are removed from `to` events" — Karabiner JSON reference), which emits a phantom Option key-up. OmniWM reads that `flagsChanged` event as a release and hides the workspace bar mid-chord.
     - Instead, two pass-through trackers (`left_option`, `right_option`, matched with `optional: ["any"]` so shifted chords still track) set the `omniwm_option_held` variable on press, pass the physical key through unchanged, and reset the variable to `0` via `to_after_key_up`. macOS/OmniWM therefore observe exactly one Option-down per press and one Option-up per release.
     - Every IPC action requires `variable_if omniwm_option_held == 1` and declares Option only as an optional modifier. `Shift` and `Control` may remain mandatory; Option may not.
     - It also does not re-emit synthetic `F13`–`F20` events. Do not "clean this up" back to synthetic F-keys or mandatory Option — both recreate the workspace-bar flicker.
4. **Native macOS Menu Bar Architecture:**
   - The setup intentionally uses the native macOS menu bar for all system status (Wi-Fi, Battery, Clock, Audio, Control Center) and application menus.
   - SketchyBar was deliberately removed to simplify host configuration and avoid brittle status bar hacks or background polling daemons.
   - Do not add a replacement status bar (such as Ice, Bartender, SwiftBar, or Übersicht) unless explicitly requested. OmniWM independently provides window management and workspace switching.

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

This repository targets the current stable OmniWM configuration schema. Keep OmniWM on the stable Homebrew cask channel; do not pin an OmniWM version or add a supported-version lock file. When upgrading, validate the repository against the installed stable release:

```bash
brew update
brew upgrade --cask omniwm
uv run scripts/check_host_protocol.py
uv run scripts/check_host_drift.py
```

If upstream changes its schema or action IDs, adapt the repository configuration instead of holding OmniWM back.

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
opacity = 0.75
backgroundEffect = "standardBlur"
backgroundBlurRadius = 15
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

> **Enabling a rule copies it.** Karabiner stores the manipulators of an enabled rule **inline** in `~/.config/karabiner/karabiner.json`; the asset file is only the source. After editing `laptop-omniwm.json` or `external-semantic.json` you must re-apply the rule in **Complex Modifications** (remove the old rule, then add it again) — otherwise the previously enabled inline copy keeps running and the edit appears to do nothing. Symlinking the assets (above) keeps the asset layer in sync but does **not** update the inline copy.

Validate adapter JSON with Karabiner's own linter before enabling it:
```bash
"/Library/Application Support/org.pqrs/Karabiner-Elements/bin/karabiner_cli" \
  --lint-complex-modifications "$(pwd)/hosts/macos/karabiner/"*.json
```

**Deploying adapter edits (the step that is easy to miss):**
```bash
uv run scripts/check_host_drift.py               # is the live config running what the repo says?
uv run scripts/sync_karabiner.py                 # dry run: show what is stale
uv run scripts/sync_karabiner.py --apply --reload  # update assets + inline rules, reload Karabiner
uv run scripts/sync_karabiner.py --apply --prune-backups  # also drop stale karabiner.json backups (keeps newest 3)
```
`check_host_drift.py` compares the repo against the live asset files, the inline rule bodies in `karabiner.json`, and the live OmniWM settings symlink. It exits non-zero on drift, which is how a correct repo file can otherwise sit unused for months while an old inline copy keeps running.

---

## 3. Workspaces & Layout Strategy

OmniWM operates with five persistent virtual workspaces. WEB, DEV, RUN, and AUX pin `layoutType = "niri"`, while COMMS sets `layoutType = "default"` so it inherits `general.defaultLayoutType` (`niri`). All five workspaces therefore run Niri; Dwindle remains available per workspace, but no workspace selects it.

| Workspace | Role                    | Layout  |
| --------- | ----------------------- | ------- |
| 1 WEB     | Browser / research      | Niri    |
| 2 DEV     | Editor / development    | Niri    |
| 3 COMMS   | Chat / email / meetings | Default → Niri |
| 4 RUN     | Running apps / testing  | Niri    |
| 5 AUX     | Miscellaneous           | Niri    |

### Niri behavior: all five workspaces

- Niri presents a horizontal scrolling strip with one visible container (`visibleContainerCount = 1`).
- The default container span is 50% (`0.50`), with presets of `33%`, `50%`, `67%`, and `100%` (`[0.333, 0.5, 0.667, 1.0]`).
- **Cycle Size** (`Shift+F18`) cycles the focused container span through those presets (`1/3` $\\rightarrow$ `1/2` $\\rightarrow$ `2/3` $\\rightarrow$ `full` $\\rightarrow$ `1/3`).
- Columns can contain multiple vertically stacked windows. The same directional focus and move semantic keys work on every workspace: `Ctrl+F13`/`Ctrl+F16` focus left/right, `Ctrl+F14`/`Ctrl+F15` focus down/up, and the corresponding `Ctrl+Shift+F13..F16` keys move windows.

### Dwindle behavior (opt-in per workspace)

No workspace pins Dwindle today, so these notes describe what happens if one is switched to it in OmniWM's settings.

- Dwindle arranges windows as a binary split tree using the configured split ratio (`[dwindle].defaultSplitRatio`).
- **Cycle Size** (`Shift+F18`) cycles the focused Dwindle split ratio; it is not a global width control.
- The same directional focus and move semantic keys remain available, so workspace layout does not change the keyboard's window-management vocabulary.

### Shared workspace actions

- `F13`–`F17` focus workspaces 1–5; `Shift+F13`–`Shift+F17` move the active window to the corresponding workspace and follow it.
- **Overview:** `Alt+F18` (`Option+F18`) opens OmniWM's Overview thumbnail view.
- **Fullscreen & Floating:** `F19` toggles fullscreen, and `F20` toggles floating.
- **Previous Window:** `Alt+F16` switches to the previously focused window across workspaces.

### Conservative app routing

New windows are routed only for the deliberate workspace defaults below. Workspace switching and app launching remain separate actions.

- **WEB (`1`):** Chrome, Chrome for Testing, Safari, Firefox, Zen, and Dia.
- **DEV (`2`):** Codex, Zed, VS Code, and Obsidian.
- **COMMS (`3`):** Discord, Vesktop, Zalo, Outlook, Messages, and Spotify.
- **RUN (`4`) and AUX (`5`):** no automatic routing yet.
- Ghostty remains manual so a new standalone terminal opens in the current workspace. Unlisted applications remain in the workspace where they are opened.

---

## 4. MacBook Built-in Keyboard & Trackpad Workflow

The built-in MacBook keyboard adapter allows full daily-driving of the OmniWM environment without the physical Corne keyboard. It preserves the exact physical `Option` chords but transports them as OmniWM IPC rather than synthetic `F13`–`F20` events, so the physical `Option` key remains held and visible to OmniWM's workspace-bar reveal monitor.

| Built-in Key Chord | OmniWM IPC (`omniwmctl command …`) | OmniWM Action |
|---|---|---|
| `⌥ 1` … `5` | `switch-workspace 1` … `5` | Switch to workspace 1–5 |
| `⌥ ⇧ 1` … `5` | `move-to-workspace 1` … `5` | Move active window to workspace 1–5 |
| `⌥ H / J / K / L` | `focus left / down / up / right` | Focus Left / Down / Up / Right |
| `⌥ ⇧ H / J / K / L` | `move left / down / up / right` | Move Left / Down / Up / Right |
| `⌃ ⌥ Tab` | `switch-workspace back-and-forth` | Previous workspace back-and-forth |
| `⌥ Tab` | `focus previous` | Focus previous window across workspaces |
| `⌥ .` | `cycle-size forward` | Cycle Size |
| `⌥ ⇧ O` | `toggle-overview` | Toggle OmniWM Overview |
| `⌥ Return` | `toggle-fullscreen` | Toggle fullscreen |
| `⌥ ⇧ Space` | `toggle-focused-window-floating` | Toggle focused window floating |
| `⌥ \`` | `toggle-quake-terminal` | Toggle native Quake terminal |
| `⌃ ⌥ Space` | _(native OmniWM hotkey — not via Karabiner)_ | Open the OmniWM command palette |

All MacBook rules invoke the deterministic bundle binary `/Applications/OmniWM.app/Contents/MacOS/omniwmctl` (independent of Karabiner's `PATH`) and are strictly scoped to `is_built_in_keyboard: true` so the external Corne is unaffected.

`⌃ ⌥ Space` is the one exception to that routing: it is a native OmniWM hotkey (`Control+Option+Space` → `openCommandPalette` in `settings.toml`) that never passes through Karabiner, so it behaves identically on the built-in and external keyboards and is tracked against `settings.toml` rather than the adapter.

`Option` itself is tracked in the `omniwm_option_held` Karabiner variable by two pass-through trackers, and is declared only as an *optional* modifier on the actions above. Karabiner projects mandatory modifiers out of `to` events, so declaring Option mandatory would emit a phantom Option key-up that hides the workspace bar mid-chord.

**Verify in Karabiner-EventViewer:** hold `Option` for >200 ms and press `1 2 3 H L 1` without releasing it. The modifier stream must show a single `left_option down` … `left_option up`, with no intermediate Option events, and the **Variables** pane must show `omniwm_option_held` flipping `1` on press and `0` on release.

### Laptop Trackpad Gestures
Configured in `hosts/macos/omniwm/settings.toml`:
- `workspaceSwipeEnabled = true`
- **3-Finger Horizontal Swipe:** Scrolls Niri columns.
- **3-Finger Vertical Swipe:** Cycles OmniWM virtual workspaces.

---

### Workspace Bar (Option-Held Overlay)

Configured in `hosts/macos/omniwm/settings.toml` (`[workspaceBar]`):

```toml
position = "overlappingMenuBar"
notchMode = "moveBelowMenuBar"
revealModifier = "option"
revealHoldMilliseconds = 200.0
reserveLayoutSpace = false
```

- Hold `Option` alone → after ~200 ms the OmniWM workspace bar appears (overlapping the menu bar row; on a notched display it moves below the menu bar).
- Release `Option` → the workspace bar immediately hides.
- The bar stays visible while `Option` remains physically held, including while issuing `Option`-based workspace/focus/move shortcuts (MacBook IPC preserves modifier state; synthetic `F13`–`F20` would not).
- `position = "overlappingMenuBar"` is the intended placement (verified stable while OmniWM runs). `reserveLayoutSpace = false` is kept for semantic clarity: with `revealModifier` active the bar is overlay-only, so a `true` value would only be misleading.
- `hideInNativeFullscreen = true` is preserved: native fullscreen hides the bar per OmniWM's intended behavior.

---

## 5. Native macOS Menu Bar Architecture

The desktop environment purposefully relies on the native macOS menu bar rather than third-party replacement bars:

```text
Desktop
├── OmniWM         scrolling window manager
├── macOS menu bar native system/status controls
├── Spotlight      application/search launcher
└── Corne          primary power-user keyboard interface
```

### Architectural Policy
- **Native Status Handlers:** Clock, Battery, Wi-Fi, Sound, Bluetooth, Focus/Do Not Disturb, and Control Center remain fully managed by macOS natively.
- **Application Menus:** Native application menus (File, Edit, View, Window, Help) remain visible and accessible without IPC simulation.
- **Restraint:** No bar replacement (SketchyBar, Ice, Bartender, SwiftBar, Übersicht) should be introduced.
- **OmniWM Decoupling:** OmniWM focuses entirely on window layout, workspace switching, and the Quake terminal, without publishing state to an external status bar.
- **Menu Bar Visibility:** Menu bar autohide should remain disabled for standard desktop operation (`defaults write NSGlobalDomain _HIHideMenuBar -bool false`).
