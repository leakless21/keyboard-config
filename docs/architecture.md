# Keyboard Architecture & Design Philosophy

This document outlines the core architecture, design philosophy, and physical contracts governing this keyboard configuration repository.

---

## 1. Top-Level Architectural Model

```text
Keyboard Hardware (Corne / Sofle)
                ↓
┌────────────────────────────────────────────────────────┐
│  1. Standard HID        (letters, navigation, F1–F12)  │
│  2. Consumer HID        (brightness, volume, playback) │
│  3. Semantic Protocol   (F13–F24 desktop actions)      │
└────────────────────────────────────────────────────────┘
                ↓
         Host OS Adapters
  ┌─────────────┴─────────────┐
  ▼                           ▼
macOS                      Windows
Karabiner-Elements         AutoHotkey v2
AeroSpace                  GlazeWM
Ghostty                    Windows Terminal
Spotlight                  Windows Search
```

### Three Classes of Emitted Signals

1. **Standard HID:**
   - Alphanumeric characters, punctuation, modifiers, navigation keys, and standard application `F1`–`F12` on the `FUN` layer.
   - Sent directly to the host OS. On macOS, Karabiner normalizes `F1`–`F12` to guarantee applications receive standard function keys regardless of the host's Apple function-row mode.

2. **Consumer HID:**
   - Display brightness (`C_BRI_DN`, `C_BRI_UP`), audio volume (`C_VOLUME_DOWN`, `C_VOLUME_UP`, `C_MUTE`), and media playback (`C_PREVIOUS`, `C_NEXT`, `C_PLAY_PAUSE`, `C_STOP`).
   - Handled natively by modern operating systems without third-party daemon translation.
   - **`MEDIA` is the project's portable laptop-Fn equivalent**, grouping brightness, volume, and playback controls without requiring proprietary OEM Fn firmware scancodes.

3. **Semantic Protocol (`F13`–`F24`):**
   - Abstract desktop and window management actions (`F13`–`F20`) and desktop editing commands (`F21`–`F24`).
   - Translated by lightweight host bridges (Karabiner on macOS, AutoHotkey on Windows).
   - `LANG` (`Alt+F17`) is a cross-platform semantic language/input-source action (`Ctrl+Space` on macOS, EVKey toggle on Windows). It is **not** a raw Apple `GLOBE` key, ensuring identical muscle memory across platforms.

### Non-Negotiable Invariants

1. **Firmware remains OS-neutral:**
   - Firmware contains letters, numbers, Colemak-DH base layer, bilateral home-row mods, navigation, mouse emulation, Consumer HID media/brightness keys, Bluetooth/device administration, gaming keys, standard F1–F12, and semantic high-function keys (`F13`–`F24`).
   - Firmware **never** contains OS-specific shortcuts (e.g., `Cmd+C` or `Ctrl+C`), window manager commands, launcher paths, or application names.

2. **Semantic F13–F24 Protocol as Common Bridge:**
   - Rather than encoding operating system shortcuts into firmware, the keyboards emit high-function key signals.
   - Host adapters translate these signals to native desktop actions.
   - Muscle memory is 100% identical regardless of whether connected to macOS or Windows.

3. **Separation of Workspace Switching and App Launching:**
   - Focusing a workspace (e.g., `DEV` / `F14`) strictly means *focus workspace DEV*.
   - It must never automatically summon terminals, launch IDEs, or route apps.
   - Terminal, application launchers, and language toggle (`Alt+F13`–`Alt+F17`) are explicit, separate actions.

4. **Internal Laptop Keyboards Remain Untouched:**
   - Laptop keyboards remain standard QWERTY without background remappings or key swaps.

5. **No Literal FN Layer or Fake Universal Fn HID Key:**
   - `MEDIA` serves as the portable laptop-Fn layer (brightness, volume, transport).
   - `FUN` serves as the true F1–F12 application function-key layer.
---

## 2. Shared Multi-Keyboard Layout Principles

While Corne and Sofle differ in physical dimensions and hardware features, they share the exact same core design grammar:

```text
                                 ┌──────── Corne (42 keys, ultra-compact)
                                 │
Shared 5-Column Core Principles ──┼──────── Sofle (60 keys, number row + encoders)
                                 │
                                 ▼
                     • Colemak-DH Alpha Core
                     • Bilateral Positional HRMs (A R S T / N E I O)
                     • 6-Layer Primary Thumb Architecture
                     • Directional Home-Row Navigation (N E I O → ← ↓ ↑ →)
                     • Semantic F13–F24 HOST & Editing Signals
```

### Bilateral Positional Home-Row Modifiers (HRMs)
Both keyboards use symmetrical, side-aware balanced hold-taps (`hml` on the left hand, `hmr` on the right hand):
- **Timing:** 280 ms tapping term, 175 ms quick-tap, 150 ms prior idle requirement, `hold-trigger-on-release`.
- **Positional Gating:** Left-hand HRMs hold only when triggered by opposite (right-hand) keys + thumb keys; right-hand HRMs mirror this.
- **Mod Order:**
  - Left hand (`A R S T`): `GUI`, `ALT`, `CTRL`, `SHIFT`
  - Right hand (`N E I O`): `SHIFT`, `CTRL`, `ALT`, `GUI`

### Six Functional Thumb Layer-Taps
The three primary thumb keys on each half activate the six core layers:
- Left Outer: `Tap Esc` $\rightarrow$ `Hold MOUSE`
- Left Middle: `Tap Space` $\rightarrow$ `Hold NAV`
- Left Inner: `Tap Tab` $\rightarrow$ `Hold HOST` (`host_lt`: 200 ms balanced, no idle requirement)
- Right Inner: `Tap Enter` $\rightarrow$ `Hold SYM`
- Right Middle: `Tap Backspace` $\rightarrow$ `Hold NUM`
- Right Outer: `Tap Delete` $\rightarrow$ `Hold FUN`

### Spatial & Functional Geometry
- **Outer-Left Home Key (`LM5`):** Momentary hold for `MEDIA` (`&mo L_MEDIA`).
- **NAV / MOUSE / MEDIA:** Share the right-hand directional geometry (`RM1`–`RM4` $\rightarrow$ `← ↓ ↑ →`, pointer movement, volume/track controls).
- **NUM:** Miryoku-derived 5-column numpad core + Corne/Sofle outer-column arithmetic rail (`/ * +`), with mirrored right-hand modifiers.
- **SYM:** Seniply+-inspired 6-column symbol grammar with paired delimiters, direct comparisons/operators, programming sigils, and mirrored right-hand modifiers.
- **FUN:** Retains Miryoku-style 5-column F1–F12 function key grid with mirrored right-hand modifiers.
- **Shared Core vs. 6-Column Extensions:** The core 5 columns maintain portable Miryoku ancestry; both Corne and Sofle utilize the available 6th column for high-value extensions (arithmetic rail on NUM, extended symbol grammar on SYM).
- **HOST:** Left home visits workspaces 1–5; left top moves window to workspace 1–5; left bottom launches search & terminals; right hand controls directional focus/move and modal states.
---

## 3. Deliberate Hardware Differences

We deliberately do **not** force artificial parity where hardware differs:

| Feature | Corne (42 keys) | Sofle (60 keys) | Rationale |
|---------|-----------------|-----------------|-----------|
| **Physical Keys** | 3×6 + 3 thumbs per side | 6×4 + 5 thumbs per side | Corne is compact portability; Sofle is full workstation ergonomics. |
| **Number Row** | Virtual via `NUM` layer | Dedicated physical number row | Sofle hardware includes number row; never layer-gated. |
| **Encoders** | None | Two rotary encoders with push switches | Left: Page navigation / Track; Right: Volume control. |
| **Encoder Presses** | None | Left: Caps Word; Right: Mute / Game Exit | Immediate hardware utility. |
| **Thumb Clusters** | 3 keys per side | 5 keys per side | Sofle adds dedicated outer `GUI`/`ALT` modifiers. |
| **Gaming Architecture** | `GAME` + `GAME_FN` | Single complete `GAME` layer | Corne needs `GAME_FN` for 1–0/F-keys; Sofle has physical numbers. |
| **Total Layers** | 11 layers (0–10) | 10 layers (0–9) | Sofle does not inherit Corne's `GAME_FN` constraint. |
