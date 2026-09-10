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
OmniWM + SketchyBar        AutoHotkey v2
Karabiner-Elements         GlazeWM
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

3. **Semantic Protocol (`F13`–`F24` & `Hyper + F13`–`F24`):**
   - Abstract desktop and window management actions (`F13`–`F20`), desktop clipboard editing commands (`F21`–`F24`), and application/tab management controls (`Hyper + F13`–`F24`).
   - Translated by lightweight host bridges (Karabiner on macOS, AutoHotkey on Windows).
   - **Hyper Namespace (`Ctrl + Alt + Shift + GUI`):** Application semantics reside in the dedicated Hyper namespace. Because Hyper asserts all four ordinary modifiers, holding user modifiers (e.g. Shift for selection) cannot accidentally transmute one semantic command into another.
   - **Selection-Safe Shift Handling for Clipboard:** `F21`–`F24` support bare use and explicit Shift-safe invocation for selection workflows. Host bridges match bare `F21`–`F24` and explicit `Shift+F21`–`F24`, stripping held Shift before emitting target shortcuts so selecting text with Shift + NEIO and pressing Undo cannot accidentally emit Redo (`Cmd+Shift+Z`).
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

## 2. Layout Ancestry & Design Influences

The layout architecture harmonizes proven concepts across modern ergonomic keyboard design:

```text
BASE / Core         Miryoku influenced (Colemak-DH, 36-key core, 6-layer thumb model)
NAV                 Seniply Extend + Selenium concepts, NEIO directional geometry strictly retained
SYM                 Seniply+ inspired (paired delimiters, comparison/operators on strong columns)
HRMs                urob-style positional & timeless pattern (side-aware hold-taps)
Utility Modifiers   Callum / Seniply inspired (dedicated one-shot &skm on NUM/SYM/FUN rails)
HOST                Custom semantic desktop & window management protocol
```

### Rejection of Selenium's Physical-HJKL/MNEI Arrow Geometry
While the Selenium layout proposal explores placing physical arrows on `M N E I` to mimic QWERTY's `H J K L`, this was **deliberately rejected**:
- **NEIO Cross-Layer Invariant:** Maintaining `N E I O` as `← ↓ ↑ →` across `NAV`, `MOUSE`, `MEDIA`, and `HOST` establishes an unbroken internal spatial grammar.
- Dismantling `NEIO` would break the elegant spatial harmony between home-row arrows (`N E I O` $\rightarrow$ `← ↓ ↑ →`) and bottom-row paging (`H , . /` $\rightarrow$ `Home PgDn PgUp End`).

---

## 3. Directional Invariant & NEIO Spatial Grammar

> **Invariant:** `NEIO` (`RM1..RM4`) is the canonical four-direction home-row geometry across every functional layer.

| Layer | Column 1 (`N` / `RM1`) | Column 2 (`E` / `RM2`) | Column 3 (`I` / `RM3`) | Column 4 (`O` / `RM4`) | Spatial Meaning |
|---|---|---|---|---|---|
| **`NAV`** | `←` (`LEFT`) | `↓` (`DOWN`) | `↑` (`UP`) | `→` (`RIGHT`) | Text cursor navigation |
| **`MOUSE`** | `Pointer ←` (`MOVE_LEFT`) | `Pointer ↓` (`MOVE_DOWN`) | `Pointer ↑` (`MOVE_UP`) | `Pointer →` (`MOVE_RIGHT`) | Mouse pointer movement |
| **`MEDIA`** | `Prev` (`C_PREVIOUS`) | `Vol−` (`C_VOLUME_DOWN`) | `Vol+` (`C_VOLUME_UP`) | `Next` (`C_NEXT`) | Audio playback & volume |
| **`HOST`** | `Focus ←` (`LC(F13)`) | `Focus ↓` (`LC(F14)`) | `Focus ↑` (`LC(F15)`) | `Focus →` (`LC(F16)`) | Directional window focus |
| **`HOST (Move)`** | `Move ←` (`LC(LS(F13))`) | `Move ↓` (`LC(LS(F14))`) | `Move ↑` (`LC(LS(F15))`) | `Move →` (`LC(LS(F16))`) | Directional window moving |

Underneath `NEIO`, the bottom row (`RB1..RB4`) carries secondary directional navigation:
```text
N       E       I       O
←       ↓       ↑       →
(RM1)   (RM2)   (RM3)   (RM4)

H       ,       .       /
Home    PgDn    PgUp    End
(RB1)   (RB2)   (RB3)   (RB4)
```
Outer bottom column `RB0` carries `Insert`.
Outer top column `RT0..RT4` carries `Undo`, `Paste`, `Copy`, `Cut`, `Redo`.
Outer middle column `RM0` carries `Caps Word`.
Thumbs carry `Esc | [NAV held] | Tab | Enter | Bsp | Del` with `LH1` consuming the NAV activator (`&none`) to prevent layer-tap repeats.
## 4. Left NAV: Everyday Application & Tab Management Area

The left side of the `NAV` layer is dedicated to high-frequency everyday application controls:

```text
LEFT NAV
┌──────────────┬─────────────┬─────────────┬────────────┬──────────────┬───────────────┐
│ BOOT (LT5)   │ PrevTab     │ NextTab     │ NewTab     │ CloseTab     │ ReopenTab     │
├──────────────┼─────────────┼─────────────┼────────────┼──────────────┼───────────────┤
│ Sel All      │ GUI         │ Alt         │ Ctrl       │ Shift        │ Save          │
├──────────────┼─────────────┼─────────────┼────────────┼──────────────┼───────────────┤
│ Find         │ Word ←      │ Word →      │ Find Next  │ —            │ —             │
└──────────────┴─────────────┴─────────────┴────────────┴──────────────┴───────────────┘
```

1. **Top Row (Tabs):** One-handed browser/editor tab management (`PrevTab`, `NextTab`, `NewTab`, `CloseTab`, `ReopenTab`) operable while the right hand remains on a mouse.
2. **Home Row (Operations & Held Modifiers):** `Select All` on `LM5`, `Save` on `LM0`, and standard held modifiers (`GUI`, `Alt`, `Ctrl`, `Shift` on `LM4..LM1`) for text selection (`Shift + NEIO`) and application navigation (`Ctrl/Alt/GUI + NEIO`).
3. **Bottom Row (Secondary Navigation):** `Find` on `LB5`, cursor word jumps (`Word Left`, `Word Right` on `LB4..LB3`), and `Find Next` on `LB2`. Spare positions (`LB1`, `LB0`) remain deliberately unassigned.


## 5. Modifier Architecture: Dedicated `&sk` vs `&skm`

ZMK allows customizing sticky key behaviors, but globally adding `quick-release` to `&sk` interferes with sticky key chaining (e.g. chaining `Ctrl + Shift` in Callum-style usage).

This configuration explicitly separates sticky modifier roles:

1. **Dedicated Capitalization `&sk` (BASE layer `LB5`):**
   - Configured with `quick-release`, `lazy`, and `ignore-modifiers`.
   - Optimized specifically for fast single-letter capitalization.

2. **One-Shot Utility Modifiers `&skm` (NUM, SYM, FUN rails `RM1..RM4`):**
   - Configured with `lazy` and `ignore-modifiers`, but **deliberately NO `quick-release`**.
   - Enables Callum-style single-tap or chained-tap modifier chords (e.g., `SYM` $\rightarrow$ tap `Ctrl` $\rightarrow$ tap `Shift` $\rightarrow$ release `SYM` $\rightarrow$ tap target key).

3. **NAV Layer Modifiers (`LM4..LM1`):**
   - Retained as plain `&kp` modifiers so holding `Shift` + `NEIO` arrows for continuous text selection remains maximally predictable.

---
## 6. Recovery Topology & Bootloader Independence

Firmware implements side-aware, same-half recovery paths for split operation:

1. **Left Same-Half Recovery:**
   - Hold `BASE LH1` (`NAV`) + tap `LT5` $\rightarrow$ Left controller bootloader.
   - Both activator (`LH1`) and trigger (`LT5`) reside on the physical left half.

2. **Right Same-Half Recovery:**
   - Hold `BASE RH1` (`NUM`) + tap `RT5` $\rightarrow$ Right controller bootloader.
   - Both activator (`RH1`) and trigger (`RT5`) reside on the physical right half.
   - Same-half bootloader chords require no key from the opposite half during normal connected split operation.

3. **Full Maintenance (`ADJUST` Layer):**
   - Hold `NAV + NUM` $\rightarrow$ `ADJUST`.
   - `LT5` $\rightarrow$ Left bootloader, `LT4` $\rightarrow$ Left system reset.
   - `RT4` $\rightarrow$ Right system reset, `RT5` $\rightarrow$ Right bootloader.

> ⚠️ **Central Connectivity Caveat:** A peripheral keymap shortcut is not standalone if it cannot communicate with the central. ZMK's split architecture sends the peripheral key event to the central for keymap processing, even for source-local reset behaviors. If the right peripheral is disconnected or cannot reach the central, double-tap the physical reset button on the right nice!nano.

---

## 7. Deliberate Hardware Differences

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
