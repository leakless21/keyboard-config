# Corne Keyboard Architecture & Reference

This document details the hardware, layout geometry, layer structure, and firmware configuration for the **Corne (CRKBD)** split keyboard.

---

## 1. Hardware Architecture

- **Keyboard:** Corne (CRKBD) 42-key layout (3×6 alpha grid + 3 thumb keys per half).
- **Controllers:** Two nice!nano v2 microcontrollers (one central left, one peripheral right).
- **Displays:** Two SSD1306 OLED displays running custom status screens.
- **Wireless:** Bluetooth BLE with five selectable profiles.
- **Build Target:** `nice_nano@2.0.0//zmk` with shields `corne_left nice_oled` and `corne_right nice_oled`.

---

## 2. Physical Layout & Position Mapping

The 42 physical positions follow `zmk-helpers/key-labels/42.h`:

```text
LT5 LT4 LT3 LT2 LT1 LT0 | RT0 RT1 RT2 RT3 RT4 RT5
LM5 LM4 LM3 LM2 LM1 LM0 | RM0 RM1 RM2 RM3 RM4 RM5
LB5 LB4 LB3 LB2 LB1 LB0 | RB0 RB1 RB2 RB3 RB4 RB5
              LH2 LH1 LH0 | RH0 RH1 RH2
```

---

## 3. Visual Keymap & Cheatsheet References

* **One-Page Cheatsheet (SVG):** [`docs/generated/corne-cheatsheet.svg`](../generated/corne-cheatsheet.svg)
* **Printable Vector PDF:** [`docs/generated/corne-cheatsheet.pdf`](../generated/corne-cheatsheet.pdf)
* **Technical Keymap Diagram (keymap-drawer):** [`keymap-drawer/corne.svg`](../../keymap-drawer/corne.svg)
* **Cheatsheet Configuration:** [`cheatsheets/corne.yaml`](../../cheatsheets/corne.yaml)

To regenerate all visual reference artifacts from the current keymap:
```bash
uv run scripts/generate_cheatsheet.py corne
```

---

## 4. The 11 Layers

| Index | Layer Name | Activation | Primary Purpose |
|-------|------------|------------|-----------------|
| 0 | `BASE` | Default | Colemak-DH base layer with bilateral HRMs, `LM5` MEDIA hold, and 6 thumb layer-taps. |
| 1 | `NAV` | Hold `LH1` (Space) | Semantic editing (`F21`–`F24`), cursor navigation, Caps Word (`RM0`), and left bootloader (`LT5`). |
| 2 | `MOUSE` | Hold `LH2` (Esc) | Pointer movement, wheel scrolling, left modifiers, and MB1–MB5 mouse buttons. |
| 3 | `MEDIA` | Hold `LM5` | Consumer HID display brightness, previous/volume/next transport controls, and stop/play/mute thumbs. |
| 4 | `NUM` | Hold `RH1` (Bspc) | Spatial numpad on left; mirrored modifiers and right bootloader (`RT5`) on right. |
| 5 | `SYM` | Hold `RH0` (Enter) | Shifted NUM symbols on left; mirrored modifiers on right. |
| 6 | `FUN` | Hold `RH2` (Delete) | F1–F12 function key grid on left; Caps Lock fallback (`RT0`) on right. |
| 7 | `HOST` | Hold `LH0` (Tab) | Semantic `F13`–`F20` host protocol for window management, launchers, and modal controls. |
| 8 | `GAME` | Via `ADJUST` | Tap-only QWERTY for gaming; `game_fn_lt` on `LT5`, momentary `RH1` FN. |
| 9 | `ADJUST` | Hold `NAV + NUM` | Bluetooth management (`LM4`–`LM0`), power toggles, mirrored reset/bootloaders, Studio unlock. |
| 10 | `GAME_FN` | Hold `Esc` / `RH1` | Gaming numbers 1–0, F1–F10, missing symbols, and deliberate exit to `BASE` (`RH2`). |

## 5. Bootloader & Recovery Shortcuts

- **Left controller bootloader:** Hold `NAV` and press `LT5` (top-left key).
- **Right controller bootloader:** Hold `NUM` and press `RT5` (top-right key).
- **Mirrored software recovery:** Hold `ADJUST` (`NAV + NUM`), press `LT5` (left bootloader) or `RT5` (right bootloader).
- **Hardware recovery:** Double-tap physical reset button on nice!nano v2.

## 6. Artifacts & Flashing

- `corne-left.uf2` (left half, includes ZMK Studio RPC over USB-UART)
- `corne-right.uf2` (right half)
- `settings-reset.uf2` (settings partition wipe utility)

## 7. Power & Display Policy

* **Sleep Timing:** Idle blank at 30 seconds (`CONFIG_ZMK_IDLE_TIMEOUT=30000`); deep sleep at 15 minutes (`CONFIG_ZMK_IDLE_SLEEP_TIMEOUT=900000`).
* **External Power Normalization:** `CONFIG_ZMK_RGB_UNDERGLOW_EXT_POWER=n` ensures external power lines remain energized for OLED status screens even when underglow is toggled.
* **OLED Widgets:** Compact status screen displaying active layer, battery percentage/charging status, Bluetooth profile, and active modifier indicators (macOS style).
