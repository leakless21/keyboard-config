# Implementation Checklist

- [x] Codify exact mixed OmniWM workspace layouts and validation.
- [x] Add clarified app routing: Chrome/Safari/Firefox/Zen/Dia → `1`, Codex/Zed → `2`, Discord/Outlook/Messages/Spotify → `3`.
- [x] Disable the unused OmniWM Hidden Bar integration.
- [x] Correct display aliases and regenerate Corne/Sofle keyboard sheets.
- [x] Add the generated A4 landscape macOS/OmniWM workflow cheatsheet.
- [x] Validate host-cheatsheet freshness and add CI PDF smoke coverage.
- [x] Run the repository acceptance suite and review the final diff.
- [ ] Reconcile the live macOS drift check after the preserved OmniWM settings edits are committed or otherwise reconciled with `HEAD`.

## Checkpoint: Host configuration

- [x] Host docs and protocol checks pass.
- [x] App routing and Hidden Bar settings are validated.

## Checkpoint: Generated references

- [x] Corne/Sofle artifacts are fresh.
- [x] Host SVG/PDF/manifest are fresh and semantically complete.

## Checkpoint: Complete

- [x] All repository acceptance criteria pass.
- [ ] Live macOS drift check passes after the preserved settings edits are reconciled with `HEAD`.
- [x] No firmware, protocol, Karabiner, or OmniWM hotkey mappings changed.
