# Setup & Recovery Guide

This guide covers initial hardware setup, firmware flashing, clean settings resets, and Bluetooth pairing for **Corne** and **Sofle** keyboards.

---

## 1. Project Overview

This repository is a unified **ZMK firmware** configuration with shared semantic host adapters for macOS and Windows.

| File / Directory | Purpose |
|------------------|---------|
| `config/corne.keymap` / `config/corne.conf` | Corne 42-key keymap and Kconfig settings |
| `config/sofle.keymap` / `config/sofle.conf` | Sofle 60-key keymap with encoders and Kconfig settings |
| `config/west.yml` | Single canonical West manifest pinning ZMK and helpers |
| `build.yaml` | GitHub Actions matrix for Corne, Sofle, and settings-reset |
| `hosts/macos/` | macOS adapters: OmniWM, SketchyBar, Karabiner, Ghostty |
| `hosts/windows/` | Windows adapters: AutoHotkey v2, GlazeWM, Windows Terminal |
| `keymap-drawer/` | Generated SVG and YAML layout diagrams |

---

## 2. Hardware Targets & Artifacts

| Artifact | Hardware Target | Shield(s) | Features |
|----------|-----------------|-----------|----------|
| `corne-left.uf2` | nice!nano v2 | `corne_left nice_oled` | Central half, ZMK Studio RPC enabled |
| `corne-right.uf2` | nice!nano v2 | `corne_right nice_oled` | Peripheral half |
| `sofle-left.uf2` | nice!nano v2 | `sofle_left nice_oled` | Central half, ZMK Studio RPC enabled |
| `sofle-right.uf2` | nice!nano v2 | `sofle_right nice_oled` | Peripheral half |
| `settings-reset.uf2` | nice!nano v2 | `settings_reset` | Erases persistent storage/bonds |

---

## 3. Four Distinct Flashing & Recovery Operations

### A. Normal Firmware Update (Central Only)
For routine Git keymap edits:
1. Double-press physical reset on the **left (central)** half to enter bootloader mode.
2. Drag and drop `corne-left.uf2` or `sofle-left.uf2` onto the `NICENANO` USB volume.

### B. Flash Both Halves
Required when modifying split settings, peripheral display configs, rotary encoders, or dependencies:
1. Flash the **left half** with `corne-left.uf2` or `sofle-left.uf2`.
2. Connect the **right half** via USB-C and flash with `corne-right.uf2` or `sofle-right.uf2`.

### C. Settings Reset (Full Flash Wipe)
Used for corrupted Bluetooth bonding or major migrations:
1. Power off both halves.
2. Connect **left half** via USB-C $\rightarrow$ enter bootloader $\rightarrow$ flash `settings-reset.uf2` $\rightarrow$ wait 5s.
3. Enter bootloader $\rightarrow$ flash `corne-left.uf2` or `sofle-left.uf2`.
4. Connect **right half** via USB-C $\rightarrow$ enter bootloader $\rightarrow$ flash `settings-reset.uf2` $\rightarrow$ wait 5s.
5. Enter bootloader $\rightarrow$ flash `corne-right.uf2` or `sofle-right.uf2`.
6. Power on both halves simultaneously to establish split connection.
7. Forget keyboard in host Bluetooth settings $\rightarrow$ re-pair fresh.

### D. Studio Reset ("Restore Stock Settings")
Used to clear runtime overrides applied via ZMK Studio:
1. Hold `NAV + NUM` $\rightarrow$ `ADJUST` $\rightarrow$ press `studio_unlock` (`RM0`).
2. Open ZMK Studio and connect to keyboard.
3. Click **"Restore Stock Settings"** to revert all keys to the compiled Git firmware.

> ⚠️ **Important:** If ZMK Studio has ever saved a modified keymap, use **Restore Stock Settings** after flashing a firmware keymap change.
> ZMK Studio stores runtime keymap changes persistently in flash memory and will otherwise override later `.keymap` changes.
> Do **not** use a full settings reset (`settings-reset.uf2`) just to update the keymap, as that clears Bluetooth split bonds and pairing keys. ZMK provides Studio's **Restore Stock Settings** specifically for this purpose.

For detailed diagnostic flowcharts, see [docs/troubleshooting.md](troubleshooting.md).
---

## 4. Bluetooth Pairing & Switching

- **Select Profile:** On `ADJUST` (`NAV + NUM`), press `BT_SEL 0` through `BT_SEL 4` in the home row core.
- **Pair:** Open host Bluetooth settings and pair with "ZMK" or keyboard name.
- **Clear Bond:** On `ADJUST`, press `BT_CLR` to clear the active profile bond, then remove device from host before re-pairing.
