# Daily Usage & Development Workflow

This guide covers daily keyboard usage, layer navigation, gaming, and the firmware change workflow for **Corne** and **Sofle** keyboards.

---

## 1. Daily Keyboard Use

### BASE Layer (Colemak-DH)
- Default typing layer is **Colemak-DH** with bilateral home-row modifiers (`A R S T` $\rightarrow$ `GUI ALT CTRL SHIFT`; `N E I O` $\rightarrow$ `SHIFT CTRL ALT GUI`).
- **Outer-Left Home Key (`LM5`):** Momentary hold for `MEDIA` (`&mo L_MEDIA`) for display brightness and audio/playback controls.

### Six Core Thumb Layer-Taps
| Thumb Position | Tap Action | Hold Layer | Functionality |
|----------------|------------|------------|---------------|
| Left Outer (`LH2`) | `Escape` | `MOUSE` | Pointer movement, wheel scroll, MB1–MB5 buttons, F21–F24 editing |
| Left Middle (`LH1`) | `Space` | `NAV` | Directional cursor, line/page nav, Caps Word (`RM0`), editing (`RT0..RT4`), left same-half bootloader (`LT5`), consumes activator (`LH1 = &none`) |
| Left Inner (`LH0`) | `Tab` | `HOST` | Semantic F13–F20 workspace protocol, launchers, previous window, resize, service |
| Right Inner (`RH0`) | `Enter` | `SYM` | Seniply+ symbols (delimiter pairs, `< >`, `- = +`, sigils, `\ / _`), mirrored modifiers |
| Right Middle (`RH1`) | `Backspace` | `NUM` | Spatial numpad on left with arithmetic rail (`/ * +`), mirrored modifiers, right bootloader (`RT5`) |
| Right Outer (`RH2`) | `Delete` | `FUN` | Standard application function keys F1–F12 across all hosts, Caps Lock fallback (`RT0`), mirrored modifiers |

### NUM+ (Numpad & Arithmetic Rail)
```text
NUM · left hand

/    [    7    8    9    ]
*    ;    4    5    6    =
+    `    1    2    3    \

          .    0    -
```
- **Spatial Numpad Core:** Standard 3×3 phone/numpad layout (`789`, `456`, `123`, `0`).
- **Outer Arithmetic Rail:** `/` on top (`LT5`), `*` on home (`LM5`), `+` on bottom (`LB5`).
- **Calculation & Brackets:** Delimiters `[` `]`, `;`, `=`, `` ` ``, `\`, `.`, `-` easily accessible.
- **Right Hand:** Mirrored home-row modifiers (`Shift`, `Ctrl`, `Alt`, `GUI`) and bootloader on `RT5`.

### SYM (Seniply+ Symbol Grammar)
```text
SYM · left hand

@    #    $    ]    }    )
!    <    >    [    {    (
&    |    *    -    =    +

          \    /    _
```
- **Paired Delimiters (closers stacked above openers):**
  - `] } )` (top row `LT2..LT0`)
  - `[ { (` (home row `LM2..LM0`)
- **Common Operators Together:** `- = +` (bottom row `LB2..LB0`).
- **Direct Comparisons:** `< >` on home row strong positions (`LM4`, `LM3`).
- **Logic & Operator Symbols:** `! & | *` on left column and bottom row.
- **Common Programming Sigils:** `@ # $` on top row (`LT5..LT3`).
- **Path & Identifier Punctuation on Thumbs:** `\` (left outer `LH2`), `/` (left middle `LH1`), `_` (left inner `LH0`).
- **Right Hand:** Mirrored home-row modifiers (`Shift`, `Ctrl`, `Alt`, `GUI`).

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

> ⚠️ **Warning:** Flashing a new `.keymap` does NOT replace Studio runtime overrides stored in flash memory. You must click **"Restore Stock Settings"** in ZMK Studio after flashing new firmware. Do **not** use a full settings reset (`settings-reset.uf2`), as that wipes Bluetooth pairing data.
For complete rules on permitted vs forbidden Studio modifications, see [docs/development.md](development.md).

## 4. Smoke-Test Checklist

- [ ] **Base Typing:** Colemak-DH alphas, punctuation, bilateral HRMs.
- [ ] **Thumb & Auxiliary Layers:** NAV, MOUSE, MEDIA (brightness + audio/playback), NUM, SYM, FUN (F1–F12), HOST accessible via thumbs and LM5.
- [ ] **Encoders (Sofle):** Page scroll / track on left, volume on right; Caps Word and Mute on presses.
- [ ] **Everyday Application Actions (Left NAV):** Tabs (PrevTab, NextTab, NewTab, CloseTab, ReopenTab), Select All (`Hyper+F13`), Save (`Hyper+F14`), Find (`Hyper+F15`), Word Left/Right (`Hyper+F21/F22`), Find Next (`Hyper+F23`).
- [ ] **Semantic Editing (Right NAV & MOUSE):** Undo (`RT0` / `F24`), Paste (`RT1` / `F22`), Copy (`RT2` / `F21`), Cut (`RT3` / `F23`), Redo (`RT4` / `Hyper+F24`).
- [ ] **Directional Invariant (NEIO):** `N E I O` consistently controls `← ↓ ↑ →` across NAV, pointer on MOUSE, volume/track on MEDIA, and window focus on HOST.
- [ ] **Gaming:** QWERTY alphas, physical numbers (Sofle) or AUX numbers (Corne), safe non-accidental exit to BASE.
- [ ] **Bootloaders:** NAV LT5 triggers left same-half bootloader; NUM RT5 triggers right same-half bootloader during connected operation.
