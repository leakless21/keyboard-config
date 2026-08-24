# Daily Usage & Development Workflow

This guide covers daily keyboard usage, layer navigation, gaming, and the firmware change workflow for **Corne** and **Sofle** keyboards.

---

## 1. Daily Keyboard Use

### BASE Layer (Colemak-DH)
- Default typing layer is **Colemak-DH** with bilateral home-row modifiers (`A R S T` $\rightarrow$ `GUI ALT CTRL SHIFT`; `N E I O` $\rightarrow$ `SHIFT CTRL ALT GUI`).
- **Outer-Left Home Key (`LM5`):** Momentary hold for `MEDIA` (`&mo L_MEDIA`).
- **Encoders (Sofle):** Left encoder rotates Page Up/Down and presses for Caps Word; Right encoder rotates Volume Down/Up and presses for Mute.

### Six Core Thumb Layer-Taps
| Thumb Position | Tap Action | Hold Layer | Functionality |
|----------------|------------|------------|---------------|
| Left Outer (`LH2`) | `Escape` | `MOUSE` | Pointer movement, wheel scroll, MB1–MB5 buttons, F21–F24 editing |
| Left Middle (`LH1`) | `Space` | `NAV` | Directional cursor, line/page nav, Caps Word (`RM0`), F21–F24 editing, left bootloader (`LT5`) |
| Left Inner (`LH0`) | `Tab` | `HOST` | Semantic F13–F20 workspace protocol, launchers, previous window, resize, service |
| Right Inner (`RH0`) | `Enter` | `SYM` | Shifted NUM symbols (`{ & * ( }`, `: $ % ^ +`, `~ ! @ # \|`) |
| Right Middle (`RH1`) | `Backspace` | `NUM` | Spatial numpad on left (`7 8 9`, `4 5 6`, `1 2 3`), right bootloader (`RT5`) |
| Right Outer (`RH2`) | `Delete` | `FUN` | Function keys F1–F12, Caps Lock fallback (`RT0`) |

---

## 2. Gaming Modes

### Corne Gaming (`GAME` + `GAME_FN`)
1. Enter `GAME` from `ADJUST` (`NAV + NUM` $\rightarrow$ press `GAME`).
2. Left-hand mouse gaming: Hold `Esc` (`LT5`) + `Q/W/E/R/T` for numbers `1`–`5`.
3. Two-handed access: Hold `RH1` for numbers `1`–`0`, F1–F10, and symbols.
4. Exit to BASE: Hold `Esc` or `RH1` to reach `GAME_FN`, then tap `RH2` (`&to L_BASE`).

### Sofle Gaming (Single Complete `GAME` Layer)
1. Enter `GAME` from `ADJUST` (`NAV + NUM` $\rightarrow$ press `GAME`).
2. Full QWERTY with dedicated physical number row `1`–`0`, direct Esc, Tab, Shift, Ctrl, Alt, Space.
3. No HRMs or sticky keys.
4. Exit to BASE: Press the **right rotary encoder** (`REC` $\rightarrow$ `&to L_BASE`).

---

## 3. ZMK Studio Policy & Lifecycle

ZMK Studio is enabled with hardware locking (`CONFIG_ZMK_STUDIO_LOCKING=y`) to ensure Git remains the canonical database.

### Three Operational States:
1. **Stock:** Active keymap exactly equals compiled Git firmware (recommended production state).
2. **Studio Experiment:** Runtime overrides stored in flash memory; active keymap differs from Git.
3. **Promoted:** Desired changes copied to Git $\rightarrow$ built $\rightarrow$ "Restore Stock Settings" in Studio $\rightarrow$ flash new `.uf2`.

> ⚠️ **Warning:** Flashing a new `.keymap` does NOT replace Studio runtime overrides stored in flash memory. You must click **"Restore Stock Settings"** in ZMK Studio before verifying new Git builds.

For complete rules on permitted vs forbidden Studio modifications, see [docs/development.md](development.md).

## 4. Smoke-Test Checklist

- [ ] **Base Typing:** Colemak-DH alphas, punctuation, bilateral HRMs.
- [ ] **Thumb Layers:** NAV, MOUSE, MEDIA, NUM, SYM, FUN, HOST accessible via thumbs.
- [ ] **Encoders (Sofle):** Page scroll on left, volume on right; Caps Word and Mute on presses.
- [ ] **Semantic Editing:** Copy (`F21`), Paste (`F22`), Cut (`F23`), Undo (`F24`), Redo (`Shift+F24`).
- [ ] **HOST Navigation:** Workspaces 1–5 (`F13`–`F17`), directional focus/move, launchers & desktop actions (`Alt+F13`–`Alt+F17`), Previous Window (`Alt+F16`), Language Toggle (`Alt+F17`).
- [ ] **Gaming:** QWERTY alphas, physical numbers (Sofle) or AUX numbers (Corne), safe non-accidental exit to BASE.
- [ ] **Bootloaders:** NAV LT5 triggers left bootloader; NUM RT5 triggers right bootloader.
