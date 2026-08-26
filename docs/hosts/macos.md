# macOS Host Integration Guide

This guide documents the macOS host configuration for the semantic keyboard protocol using Karabiner-Elements, AeroSpace, Ghostty, and Spotlight.

---

## 1. Architecture Overview

```text
Keyboard (Corne / Sofle)
      ↓
Semantic F13–F24 HID Signals
      ↓
Karabiner-Elements (hosts/macos/karabiner.json)
      ↓
Native macOS Chords (Alt + Cmd shortcuts)
      ┌─────────────────┼─────────────────┐
      ▼                 ▼                 ▼
  AeroSpace          Ghostty          Spotlight
(Window Manager)   (Terminal)        (Launcher)
```

---

## 2. Installation & Prerequisites

### 1. Karabiner-Elements (Host Bridge)
- Install [Karabiner-Elements](https://karabiner-elements.pqrs.org/).
- Copy `hosts/macos/karabiner.json` to `~/.config/karabiner/assets/complex_modifications/karabiner.json`.
- In Karabiner-Elements Settings $\rightarrow$ **Complex Modifications** $\rightarrow$ **Add rule**:
  - Enable **"F13-F20 Semantic Window Management Bridge"** (F13–F20 $\rightarrow$ AeroSpace chords).
  - Enable **"Hyper+F13-F24 Application & Navigation Bridge"** (Hyper+F13–F24 $\rightarrow$ app actions / tabs / cursor navigation).
  - Enable **"F21-F24 Semantic Clipboard & Editing"** (F21–F24 $\rightarrow$ Cmd+C/V/X/Z with modifier tolerance).
  - Enable **"Standard F1-F12 normalization for external keyboard"** (guarantees application F1–F12).
### 2. AeroSpace (Tiling Window Manager)
- Install [AeroSpace](https://nikitabobko.github.io/AeroSpace/).
- Grant **Accessibility** permission in macOS System Settings $\rightarrow$ Privacy & Security $\rightarrow$ Accessibility.
- Symlink or copy `hosts/macos/aerospace.toml` to `~/.config/aerospace/aerospace.toml`:
  ```bash
  mkdir -p ~/.config/aerospace
  ln -sfn "$(pwd)/hosts/macos/aerospace.toml" ~/.config/aerospace/aerospace.toml
  ```
- Reload with `aerospace reload-config`.

### 3. Ghostty Terminal
- Install [Ghostty](https://ghostty.org/).
- Symlink or copy `hosts/macos/ghostty.config` to `~/.config/ghostty/config`:
  ```bash
  mkdir -p ~/.config/ghostty
  ln -sfn "$(pwd)/hosts/macos/ghostty.config" ~/.config/ghostty/config
  ```
- This sets up the dropdown Quick Terminal on `Ctrl+``` (`Alt+F14`).


### 4. Input Source / Language Toggle (Ctrl+Space)
- The keyboard emits `Alt+F17` for `LANGUAGE_TOGGLE`.
- Karabiner-Elements translates `Option+F17` to `Control+Space`.
- Configure macOS input source shortcut in:
  **System Settings** $\rightarrow$ **Keyboard** $\rightarrow$ **Keyboard Shortcuts** $\rightarrow$ **Input Sources** $\rightarrow$ **Select previous input source** = `Control+Space` (or `Select next source in Input menu`).
  With two primary input sources (e.g. English and Vietnamese), `Control+Space` acts as a clean toggle.
---

## 3. Workspaces & Modal Operations

AeroSpace operates with five persistent virtual workspaces:
- `WEB` (Slot 1 / `F13` / `Alt-1`)
- `DEV` (Slot 2 / `F14` / `Alt-2`)
- `COMMS` (Slot 3 / `F15` / `Alt-3`)
- `RUN` (Slot 4 / `F16` / `Alt-4`)
- `AUX` (Slot 5 / `F17` / `Alt-5`)

### Binding Modes:
- **`main` Mode:** Standard workspace focus, window focus (`Alt-H/J/K/L`), and window moving (`Alt-Shift-H/J/K/L`).
- **`resize` Mode (`Shift+F18` / `Alt-R`):** Directional window dimension adjustments ($\pm 50$ px). Exit with `Esc` or `Enter`.
- **`service` Mode (`Alt+F18` / `Alt-Shift-;`):** Tree surgery, joining, swapping, and monitor movements. One-shot commands automatically return to `main`.

---

## 4. Standard F1–F12 Normalization

By default, macOS interprets incoming HID `F1`–`F12` keycodes as Apple media and display brightness keys unless the user enables **"Use all F1, F2, etc. keys as standard function keys"** in macOS **System Settings** $\rightarrow$ **Keyboard** $\rightarrow$ **Keyboard Shortcuts** $\rightarrow$ **Function Keys**.

To ensure that the `FUN` layer reliably emits application `F1`–`F12` across any Mac without requiring global system setting alterations:

1. **System Variable Awareness:**
   Karabiner-Elements evaluates `system.use_fkeys_as_standard_function_keys`.
   - When standard function keys mode is **OFF** (macOS media mode), Karabiner transforms external `F1`–`F12` into `Fn + F1`–`Fn + F12`, which macOS translates to standard application function keys.
   - When standard function keys mode is **ON**, the rule does not intervene, passing `F1`–`F12` directly.

2. **Modifier Preservation (`optional: ["any"]`):**
   The `FUN` layer provides mirrored modifiers on the opposite hand (`Shift`, `Ctrl`, `Alt`, `Cmd`). Karabiner's `optional: ["any"]` specification ensures that modified combinations (e.g., `Shift+F5`, `Ctrl+F5`, `Cmd+F5`) pass through with their modifier flags fully intact.

3. **Isolation to External Keyboards:**
   Scoped with `is_built_in_keyboard: false` so that the MacBook's physical built-in Touch Bar or top function row remains unaffected.
---

## 5. Device Scoping & Built-in Keyboard Isolation

To prevent high-function keys (`F13`–`F24`) on the built-in laptop keyboard or other standard peripherals from being intercepted, every rule manipulator in `hosts/macos/karabiner.json` is scoped with a `device_if` condition:

```json
"conditions": [
  {
    "type": "device_if",
    "identifiers": [
      {
        "is_keyboard": true,
        "is_built_in_keyboard": false
      }
    ]
  }
]
```

### Matching Specific ZMK Hardware (Optional USB / BLE Targeting)
If you wish to restrict translation to specific external ZMK controllers only:
1. Open **Karabiner-EventViewer** $\rightarrow$ **Devices** tab.
2. Locate your connected Corne / Sofle controller (USB VID/PID or BLE Device Address).
3. Replace or supplement the `identifiers` array in `hosts/macos/karabiner.json` with your controller's exact `vendor_id` and `product_id`:
   ```json
   {
     "type": "device_if",
     "identifiers": [
       {
         "vendor_id": 12056,
         "product_id": 1
       }
     ]
   }
   ```
