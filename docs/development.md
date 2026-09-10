# Firmware Development & Studio Policy

This document formalizes the development lifecycle, validation suite, and canonical Git-first policy for **ZMK Studio** on **Corne** and **Sofle** keyboards.

---

## 1. The Three Keymap States

```text
       ┌────────────────────────┐
       │     1. Stock State     │ ◄─── (Canonical, production state)
       │  Active == Compiled    │
       └───────────┬────────────┘
                   │
                   ▼  (Connect to ZMK Studio)
       ┌────────────────────────┐
       │  2. Studio Experiment  │ ◄─── (Temporary runtime overrides)
       │  Active != Compiled    │
       └───────────┬────────────┘
                   │
                   ▼  (Promote to Git)
       ┌────────────────────────────────────────────────────────┐
       │                  3. Promoted Workflow                  │
       │  1. Copy desired bindings into config/*.keymap         │
       │  2. Commit to Git & build new firmware .uf2            │
       │  3. In ZMK Studio: Click "Restore Stock Settings"      │
       │  4. Flash new .uf2 $\rightarrow$ Back to Stock State   │
       └────────────────────────────────────────────────────────┘
```

### State 1: Stock (Production)
* `Active Runtime Keymap == Compiled Git Keymap`.
* This is the recommended, stable state for daily use.

### State 2: Studio Experiment (Temporary)
* `Active Runtime Keymap != Compiled Git Keymap`.
* Changes are written to the nice!nano's persistent runtime storage.
* Useful for rapid layer experiments or testing a key placement without compiling.

### State 3: Promoted (Integration)
* Experimental changes that proved valuable are codified in Git:
  1. Transfer changes into `config/corne.keymap` or `config/sofle.keymap`.
  2. Run local validation suite (`scripts/check_*.py`).
  3. Push to Git and download newly compiled `.uf2` artifacts.
  4. **Restore Stock Settings** in ZMK Studio to erase the runtime override partition.
  5. Flash the new `.uf2` firmware.

---

## 2. Critical Studio Warning

> ⚠️ **CRITICAL WARNING: FLASHING DOES NOT ERASE STUDIO OVERRIDES**
>
> When you flash a newly built `.uf2` file, the controller's persistent settings partition retains any active ZMK Studio runtime overrides. If a key was customized in Studio, the keyboard will continue using the Studio binding rather than the newly flashed `.keymap`!
>
> **Always click "Restore Stock Settings" in ZMK Studio before verifying newly flashed Git builds.**

---

## 3. What ZMK Studio May and May Not Modify

To prevent architecture erosion, strict boundaries govern ZMK Studio usage:

### Permitted in ZMK Studio:
* Temporary alpha or symbol position experiments.
* Evaluating layer access ergonomics.
* Quick testing of single-key variations.

### Forbidden in ZMK Studio (Git Canonical Only):
* **Custom Behaviors & Macros:** Home-row mods (`hml`/`hmr`), `host_lt`, `game_fn_lt`.
* **Timing & Flavor Parameters:** `tapping-term-ms`, `quick-tap-ms`, `require-prior-idle-ms`, `hold-trigger-key-positions`.
* **Protocol & Host Signals:** Semantic `F13`–`F20` and `F21`–`F24` bindings.
* **Gaming Architecture:** QWERTY game layers, number rows, deliberate exit protections.
* **ADJUST & Recovery Bindings:** Bootloaders, hardware resets, Studio unlock, BT profile switching.

---

## 4. Local Validation Suite

Before committing any keymap, host, or configuration change, run all local checks:

```bash
# 1. Validate Corne structural & positional invariants
uv run scripts/check_corne_keymap.py

# 2. Validate Sofle structural & positional invariants
uv run scripts/check_sofle_keymap.py

# 3. Validate build targets, manifest SHAs, and CI workflow sync
uv run scripts/check_build_config.py

# 4. Validate multi-host semantic protocol (OmniWM, Karabiner, AHK, GlazeWM)
uv run scripts/check_host_protocol.py

# 5. Validate generated documentation freshness & undeclared signal detection
uv run scripts/check_generated.py
```

To re-generate documentation tables from `protocol/semantic-v1.yaml`:
```bash
uv run scripts/generate_protocol_files.py
```

To re-generate visual reference cheatsheet artifacts (SVG, PDF, and manifest):
```bash
# Default generation (SVG + vector PDF + manifest):
uv run scripts/generate_cheatsheet.py corne

# Generate SVG only:
uv run scripts/generate_cheatsheet.py corne --svg-only

# Export optional 300-DPI PNG:
uv run scripts/generate_cheatsheet.py corne --png

# Verify freshness without modifying disk artifacts:
uv run scripts/generate_cheatsheet.py corne --check

# Render with debug position overlays (LT5..RH2):
uv run scripts/generate_cheatsheet.py corne --debug
```
---

## 5. Manual Smoke Test Sequences

### A. General Firmware Smoke Test (Both Keyboards)
1. **BASE Layer:** Type alphabet sentence, punctuation, bilateral HRMs (`A R S T` / `N E I O`).
2. **NAV Layer:** Left bootloader on `LT5`, directional arrows, line/page jump, Caps Word on `RM0`, editing `RT0..RT4` (Undo, Paste, Copy, Cut, Redo).
3. **MOUSE Layer:** Mouse pointer movement (`mmv`), wheel scrolling (`msc`), buttons MB1–MB5, editing `RT0..RT4` (Undo, Paste, Copy, Cut, Redo).
4. **MEDIA Layer:** Display brightness down (`RT2`) / up (`RT3`), Previous/Next track, Volume Down/Up, Stop, Play/Pause, Mute.
5. **NUM & SYM Layers:** Left spatial numpad / symbols, right mirrored modifiers, right bootloader on `RT5`.
6. **FUN Layer:** Standard function keys `F1`–`F12`, modified F-keys (`Shift+F5`, `Ctrl+F5`, `Cmd+F5`, `Alt+F5`), Caps Lock fallback on `RT0`.
7. **HOST Layer:** All 28 semantic signals (see below).
### B. Host Semantic Smoke Test (macOS & Windows)
* **Workspaces:** Tap `F13`–`F17` $\rightarrow$ Visits workspaces 1–5 (`WEB`, `DEV`, `COMMS`, `RUN`, `AUX`).
* **Move Window:** Tap `Shift+F13`–`Shift+F17` $\rightarrow$ Moves active window to target workspace and follows.
* **Focus Window:** Tap `Ctrl+F13`–`Ctrl+F16` $\rightarrow$ Directional focus ← ↓ ↑ →.
* **Move Window:** Tap `Ctrl+Shift+F13`–`Ctrl+Shift+F16` $\rightarrow$ Directional window move ← ↓ ↑ →.
* **Context & Modals:**
  * `F18` $\rightarrow$ Previous / recent workspace.
  * `Shift+F18` $\rightarrow$ Enter Resize mode (exit with `Esc` / `Enter`).
  * `Alt+F18` $\rightarrow$ Enter Service mode (exit with `Esc` / `Enter`).
  * `F19` $\rightarrow$ Toggle fullscreen.
  * `F20` $\rightarrow$ Toggle floating / tiling.
* **Launchers & Desktop Actions:**
  * `Alt+F13` $\rightarrow$ System Search (Spotlight / Windows Search).
  * `Alt+F14` $\rightarrow$ Quick Terminal (Ghostty dropdown / Windows Terminal Quake).
  * `Alt+F15` $\rightarrow$ New Terminal window (`Ghostty` / `wt.exe`).
  * `Alt+F16` $\rightarrow$ Previous active window across workspaces.
  * `Alt+F17` $\rightarrow$ Language toggle (macOS input source `Ctrl+Space` / Windows EVKey toggle).
* **Editing:**
  * `F21` $\rightarrow$ Copy (`Cmd+C` / `Ctrl+C`).
  * `F22` $\rightarrow$ Paste (`Cmd+V` / `Ctrl+V`).
  * `F23` $\rightarrow$ Cut (`Cmd+X` / `Ctrl+X`).
  * `F24` $\rightarrow$ Undo (`Cmd+Z` / `Ctrl+Z`).
  * `Hyper+F24` $\rightarrow$ Redo (`Cmd+Shift+Z` / `Ctrl+Y`).
  * `Shift+F21..F24` $\rightarrow$ Selection-safe Copy/Paste/Cut/Undo (Shift stripped before emitting target).
* **Standard Function Keys (macOS Karabiner Verification):**
  * macOS Function Keys setting **OFF** (media mode): Press `FUN` + `F1`..`F12` $\rightarrow$ Target application receives real `F1`..`F12` (not brightness/media).
  * macOS Function Keys setting **ON** (standard F-keys mode): Press `FUN` + `F1`..`F12` $\rightarrow$ Target application still receives `F1`..`F12`.
  * Modified F-keys (`Shift+F5`, `Ctrl+F5`, `Cmd+F5`) pass through with modifiers intact.
### C. Keyboard-Specific Hardware Tests
* **Corne Gaming:**
  1. Hold `NAV + NUM` $\rightarrow$ `ADJUST` $\rightarrow$ press `to L_GAME`.
  2. Verify plain QWERTY, no HRMs, tap `Esc`.
  3. Hold `Esc` + `Q/W/E/R/T` $\rightarrow$ yields numbers `1`–`5`.
  4. Hold `RH1` + tap `RH2` $\rightarrow$ deliberate exit to `BASE`.
* **Sofle Hardware:**
  1. Physical number row `1`–`0` on BASE and GAME.
  2. Left encoder: Rotate Page Up/Down; press for Caps Word.
  3. Right encoder: Rotate Volume Down/Up; press for Mute.
  4. Enter `GAME` $\rightarrow$ press right encoder (`REC`) $\rightarrow$ returns cleanly to `BASE`.
