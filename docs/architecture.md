# Keyboard Architecture & Design Philosophy

This document outlines the core architecture, design philosophy, and physical contracts governing this keyboard configuration repository.

---

## 1. Top-Level Architectural Model

```text
Keyboard Hardware (Corne / Sofle)
                ↓
    Portable ZMK Firmware Behaviors
  (Colemak-DH, HRMs, Layers, HID Media)
                +
    Semantic HID Protocol (F13–F24)
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

### Non-Negotiable Invariants

1. **Firmware remains OS-neutral:**
   - Firmware contains letters, numbers, Colemak-DH base layer, bilateral home-row mods, navigation, mouse emulation, Consumer HID media keys, Bluetooth/device administration, gaming keys, standard F1–F12, and semantic high-function keys (`F13`–`F24`).
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
- **NUM / SYM / FUN:** Share the left-hand 5-column grid (spatial numpad $\rightarrow$ shifted symbols $\rightarrow$ F1–F12 grid).
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
