# Troubleshooting & Diagnostics Guide

This guide provides an operational decision tree and step-by-step diagnostic workflows for resolving hardware, Bluetooth, ZMK Studio override, and host protocol issues on **Corne** and **Sofle** keyboards.

---

## 1. Troubleshooting Decision Tree

```text
Problem Detected
│
├─ Keymap change not appearing after flashing?
│  ├─ Has ZMK Studio EVER been used on this board?
│  │  └─ YES: Unlock on ADJUST (RM0) -> Open ZMK Studio -> Click "Restore Stock Settings"
│  └─ Did change affect encoders, displays, or peripheral half?
│     └─ YES: Flash BOTH halves (left and right .uf2)
│
├─ Only one OLED display works or display is blank?
│  ├─ 1. Verify battery/power switch is ON for BOTH halves.
│  ├─ 2. Flash peripheral half with the latest peripheral UF2 (corne-right / sofle-right).
│  └─ 3. If still blank, run full Settings Reset procedure on BOTH halves.
│
├─ Halves fail to connect or communicate wirelessly?
│  └─ Perform full Settings Reset on BOTH halves (see Section 2.C below).
│
├─ Host Bluetooth pairing fails, drops, or acts sluggish?
│  ├─ 1. On keyboard: Switch to profile on ADJUST (BT_SEL 0..4) -> Press BT_CLR.
│  ├─ 2. On host OS: Forget / Remove "ZMK" or keyboard device in Bluetooth settings.
│  ├─ 3. Turn Bluetooth off and on again on host.
│  └─ 4. Re-pair fresh.
│
└─ Semantic shortcut (F13–F24) not working on host?
   ├─ 1. Test raw signal: Use Karabiner-EventViewer (macOS) or AHK KeyHistory (Windows).
   ├─ 2. Is raw F-key received?
   │  ├─ NO: Check active keymap layer (must be on HOST or NAV/MOUSE).
   │  └─ YES: Check host adapter process:
   │     ├─ macOS: Is Karabiner running? Is AeroSpace running? Is Ghostty running?
   │     └─ Windows: Is AutoHotkey script running? Is GlazeWM running?
   └─ 3. Run static validator: uv run scripts/check_host_protocol.py
```

---

## 2. Four Distinct Flashing & Reset Procedures

Do not confuse firmware updates, split settings resets, and ZMK Studio resets. They target completely different flash memory partitions.

### A. Normal Firmware Update (Central Only)
Used for routine Git keymap changes that only affect central key assignments:
1. Double-press reset button on **left (central)** half to enter bootloader.
2. Drag and drop `corne-left.uf2` or `sofle-left.uf2` onto the `NICENANO` USB volume.
3. Controller reboots automatically.

### B. Flash Both Halves
**Mandatory** when changing:
* Split communication or BLE configuration.
* Peripheral OLED display behavior / widgets.
* Rotary encoders (Sofle).
* Pinned dependency SHAs or West manifest.
* Kconfig files (`corne.conf` / `sofle.conf`).

**Procedure:**
1. Flash **left half** with `corne-left.uf2` / `sofle-left.uf2`.
2. Connect **right half** via USB-C, enter bootloader, and flash with `corne-right.uf2` / `sofle-right.uf2`.

### C. Settings Reset (Full Flash Wipe)
Used only for corrupted BLE bonding, desynchronized split halves, or major firmware migrations:
1. Power off both halves.
2. Connect **left half** via USB-C $\rightarrow$ enter bootloader $\rightarrow$ flash `settings-reset.uf2`. Wait 5 seconds.
3. Enter bootloader again $\rightarrow$ flash `corne-left.uf2` / `sofle-left.uf2`.
4. Connect **right half** via USB-C $\rightarrow$ enter bootloader $\rightarrow$ flash `settings-reset.uf2`. Wait 5 seconds.
5. Enter bootloader again $\rightarrow$ flash `corne-right.uf2` / `sofle-right.uf2`.
6. Power on both halves simultaneously. They will establish a fresh split bond.
7. Remove old pairing from host computer $\rightarrow$ pair fresh.

### D. ZMK Studio Reset ("Restore Stock Settings")
Used when runtime experiments in ZMK Studio override the Git keymap:
1. On the keyboard, hold `NAV + NUM` to reach `ADJUST`, then press `studio_unlock` (`RM0`).
2. Open ZMK Studio in Chrome / Edge (via WebUSB) or the desktop app.
3. Connect to the keyboard.
4. Click **"Restore Stock Settings"** (or Discard Changes).
5. The runtime flash partition is cleared, and active bindings immediately revert to the compiled Git firmware.

> ⚠️ **Critical Troubleshooting Note:** If ZMK Studio has ever saved a modified keymap, use **Restore Stock Settings** after flashing a firmware keymap change.
> Studio stores runtime keymap changes persistently and will otherwise override later `.keymap` changes.
> Do **not** use a full settings reset (`settings-reset.uf2`) just to update the keymap, as that wipes Bluetooth pairing and split bonding.

---

## 3. Usage & Compatibility Caveats

### Caps Word & Vietnamese Telex IME
- **Behavior:** Caps Word (`RM0` on NAV or Left Encoder push on Sofle) automatically capitalizes subsequent alpha characters until a word boundary (Space, Enter, punctuation) is typed.
- **Vietnamese Telex Interaction:** In Vietnamese Telex IMEs, alpha keys (such as `s`, `f`, `r`, `x`, `j`, `w`, `a`, `e`, `o`) also double as diacritic and tone commands. When Caps Word sends shifted keycodes, certain IMEs may interpret them differently than unshifted characters. Caps Word is primarily optimized for uppercase identifiers (e.g., `CONSTANTS_IN_CODE`). If typing Vietnamese text, prefer standard Shift / Sticky Shift (`&sk LSHFT`).

### Application Tab Shortcuts
- **Semantic Abstraction:** The firmware emits semantic `Hyper+F16` (`Previous Tab`) and `Hyper+F17` (`Next Tab`).
- **macOS App Customization:** While macOS browsers, Finder, Ghostty, and editors use `Cmd+Shift+[` and `Cmd+Shift+]` by default, any app-specific shortcut variations should be handled in `hosts/macos/karabiner.json` using application filters rather than altering firmware keymaps.
---

## 4. Host Bridge Diagnostics

### macOS
* **Verify Karabiner complex modifications:** Check that `~/.config/karabiner/assets/complex_modifications/karabiner.json` is enabled in Karabiner-Elements Settings $\rightarrow$ Complex Modifications.
* **Verify AeroSpace status:** Run `aerospace list-workspaces --focused` or `aerospace reload-config` in terminal.
* **Verify Ghostty:** Check that `ghostty.config` contains `quick-terminal-position = top` and `quick-terminal-screen = main`.

### Windows
* **Verify AutoHotkey v2:** Look for the green `H` icon in the Windows notification tray. Right-click $\rightarrow$ **Open** $\rightarrow$ **View** $\rightarrow$ **Key history and script info** to verify received F-keys.
* **Verify GlazeWM:** Check that `%USERPROFILE%/.glzr/glazewm/config.yaml` parses without errors. Reload with `Alt+F18` $\rightarrow$ `F19` or restart GlazeWM from terminal.
