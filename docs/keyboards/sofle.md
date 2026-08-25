# Sofle v2 Keyboard Architecture & Reference

This document details the hardware, layout geometry, layer structure, and firmware configuration for the **Ergomech Sofle V2 Wireless** keyboard.

---

## 1. Hardware Architecture

- **Keyboard:** Sofle v2 60-key layout (6×4 grid + 5 thumb keys per half).
- **Controllers:** Two nice!nano v2 microcontrollers (one central left, one peripheral right).
- **Rotary Encoders:** Two EC11 rotary encoders with integrated push switches.
- **Displays:** Two SSD1306 OLED displays running custom status screens.
- **Wireless:** Bluetooth BLE with five selectable profiles.
- **Build Target:** `nice_nano@2.0.0//zmk` with shields `sofle_left nice_oled` and `sofle_right nice_oled`.

---

## 2. Physical Layout & Position Mapping

The 60 physical positions follow `zmk-helpers/key-labels/sofle.h`:

```text
LN5 LN4 LN3 LN2 LN1 LN0     │     RN0 RN1 RN2 RN3 RN4 RN5
LT5 LT4 LT3 LT2 LT1 LT0     │     RT0 RT1 RT2 RT3 RT4 RT5
LM5 LM4 LM3 LM2 LM1 LM0     │     RM0 RM1 RM2 RM3 RM4 RM5
LB5 LB4 LB3 LB2 LB1 LB0 LEC │ REC RB0 RB1 RB2 RB3 RB4 RB5
      LH4 LH3 LH2 LH1 LH0   │   RH0 RH1 RH2 RH3 RH4
```

- **`LEC` (index 42):** Left encoder push switch.
- **`REC` (index 43):** Right encoder push switch.
- **`LH4..LH0` (indices 50..54):** Left thumb cluster (outer $\rightarrow$ inner).
- **`RH0..RH4` (indices 55..59):** Right thumb cluster (inner $\rightarrow$ outer).

---

## 3. Visual Keymap & Cheatsheet References

* **One-Page Cheatsheet (SVG):** [`docs/generated/sofle-cheatsheet.svg`](../generated/sofle-cheatsheet.svg)
* **Printable Vector PDF:** [`docs/generated/sofle-cheatsheet.pdf`](../generated/sofle-cheatsheet.pdf)
* **Technical Keymap Diagram (keymap-drawer):** [`keymap-drawer/sofle.svg`](../../keymap-drawer/sofle.svg)
* **Cheatsheet Configuration:** [`cheatsheets/sofle.yaml`](../../cheatsheets/sofle.yaml)

To regenerate visual reference artifacts for Sofle:
```bash
uv run scripts/generate_cheatsheet.py sofle
```

---

## 4. The 10 Modernized Layers

| Index | Layer Name | Activation | Primary Purpose |
|-------|------------|------------|-----------------|
| 0 | `BASE` | Default | Colemak-DH base layer with dedicated number row, bilateral HRMs, 6 thumb layer-taps, outer modifier thumbs, and encoder bindings. |
| 1 | `NAV` | Hold `LH1` (Space) | Semantic editing (`F21`–`F24`), cursor navigation, Caps Word (`RM0`), line/page movement, and left bootloader (`LT5`). |
| 2 | `MOUSE` | Hold `LH2` (Esc) | Pointer movement, wheel scrolling, left modifiers, and MB1–MB5 mouse buttons. |
| 3 | `MEDIA` | Hold `LM5` | Consumer HID display brightness, transport controls, right encoder volume, left encoder track seek, stop/play/mute thumbs. |
| 4 | `NUM` | Hold `RH1` (Bspc) | Spatial numpad on left; mirrored modifiers and right bootloader (`RT5`) on right. |
| 5 | `SYM` | Hold `RH0` (Enter) | Shifted NUM symbols on left; mirrored modifiers on right. |
| 6 | `FUN` | Hold `RH2` (Delete) | F1–F12 function key grid on left; Caps Lock fallback (`RT0`) on right. |
| 7 | `HOST` | Hold `LH0` (Tab) | Semantic `F13`–`F20` host protocol for window management, launchers, and modal controls. |
| 8 | `GAME` | Via `ADJUST` | Complete standalone QWERTY layout with physical number row and direct modifiers. Deliberate exit to `BASE` via right encoder press (`REC`). |
| 9 | `ADJUST` | Hold `NAV + NUM` | Bluetooth management, power toggles, mirrored reset/bootloaders, Studio unlock, and GAME entry. |

> **No `BUTTON` or `GAME_FN`:** The obsolete `BUTTON` layer was removed. Sofle has a physical number row, eliminating the need for Corne's `GAME_FN` layer.

## 5. Rotary Encoders & Push Switches

### Normal Operation (`BASE`)
- **Left Encoder Rotation:** Page Up / Page Down
- **Left Encoder Press (`LEC`):** Caps Word (`&caps_word`)
- **Right Encoder Rotation:** Volume Down / Volume Up
- **Right Encoder Press (`REC`):** Mute toggle (`&kp C_MUTE`)

### Media Operation (`MEDIA`)
- **Left Encoder Rotation:** Previous Track / Next Track (`C_PREVIOUS` / `C_NEXT`)
- **Right Encoder Rotation:** Volume Down / Volume Up (`C_VOLUME_DOWN` / `C_VOLUME_UP`)

### Gaming Operation (`GAME`)
- **Right Encoder Press (`REC`):** Deliberate exit to `BASE` (`&to L_BASE`). Protects against accidental layer exit during intense gameplay.

## 6. Bootloader & Recovery Shortcuts

- **Left controller bootloader:** Hold `NAV` and press `LT5` (top-left alpha key).
- **Right controller bootloader:** Hold `NUM` and press `RT5` (top-right alpha key).
- **Mirrored software recovery:** Hold `ADJUST` (`NAV + NUM`), press `LT5` (left bootloader) or `RT5` (right bootloader).
- **Hardware recovery:** Double-tap physical reset button on nice!nano v2.

## 7. Mandatory Settings Reset After Migration

Because modern Sofle firmware completely overhauls layer numbering, switches to ZMK Studio locking, updates hold-tap timing, and enables deep sleep:

1. Flash `settings-reset.uf2` to **both** halves.
2. Flash `sofle-left.uf2` and `sofle-right.uf2`.
3. Forget previous Bluetooth pairing on your host device and re-pair cleanly.

## 8. Power & Display Policy

* **Sleep Timing:** Idle blank at 30 seconds (`CONFIG_ZMK_IDLE_TIMEOUT=30000`); deep sleep at 15 minutes (`CONFIG_ZMK_IDLE_SLEEP_TIMEOUT=900000`).
* **External Power Normalization:** `CONFIG_ZMK_RGB_UNDERGLOW_EXT_POWER=n` ensures external power lines remain energized for OLED status screens even when underglow is toggled.
* **OLED Widgets & Icons:** Workstation-oriented status screen featuring active layer, battery percentage, and Bluetooth profile status.
