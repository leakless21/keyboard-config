# Implementation Plan: macOS OmniWM Architecture Polish

## Context

The repository already has the stable Corne/Sofle semantic HID protocol, direct Corne-to-OmniWM window-management path, MacBook Karabiner-to-OmniWM IPC adapter, native macOS menu bar, and Option-held OmniWM workspace-bar overlay. This pass documents and validates mixed workspace layouts, adds deliberately limited app routing, corrects presentation labels, and adds a separate host workflow reference.

The user clarified the routing exception in the supplied plan: **all currently listed browser apps** (Chrome, Safari, Firefox, Zen, and Dia) should route to workspace `1`, and Spotify should route to workspace `3`. This supersedes the earlier non-goal that browsers and Spotify remain manual. Ghostty remains intentionally manual; no app is routed to RUN or AUX.

A pre-existing uncommitted edit exists in `hosts/macos/omniwm/settings.toml` (Quake appearance, workspace-bar empty-workspace behavior, and workspace-bar accent color). It must be preserved while applying the requested changes.

## Approach

1. Keep firmware keymaps, protocol signal identities, HOST positions, Karabiner behavior, and OmniWM hotkeys unchanged.
2. Make workspace definitions an explicit five-entry model with per-workspace layout validation and actionable property-specific failures.
3. Reuse existing OmniWM `[[appRules]]` entries for the five browser apps, Spotify, Codex, Zed, Discord, Outlook, and Messages; add only `assignToWorkspace` values.
4. Correct only presentation aliases, then regenerate the canonical Corne/Sofle keyboard sheets.
5. Build a small host-specific deterministic A4-landscape generator from repository configuration, with manifest hashes for all required source inputs and output artifacts.
6. Extend generated-artifact and CI checks without duplicating protocol semantics validation.
7. Preserve the stable OmniWM update policy (`schemaVersion = 3`, `updateChecksEnabled = true`) and disable only the unused Hidden Bar integration.

## Files to Modify

- `docs/hosts/macos.md`
- `scripts/check_host_protocol.py`
- `hosts/macos/omniwm/settings.toml`
- `keymap_drawer.config.yaml`
- `scripts/check_generated.py`
- `.github/workflows/validate.yml`
- New host cheatsheet presentation/generator/support files under `cheatsheets/`, `scripts/`, and `scripts/lib/`
- Generated artifacts under `docs/generated/`
- `tasks/plan.md` and `tasks/todo.md` to preserve the clarified implementation plan

No firmware keymap, semantic protocol, Karabiner, or OmniWM hotkey mapping changes are intended.

## Steps

### Phase 1: Canonical host model

- [x] Document WEB/DEV/COMMS/RUN/AUX with explicit Niri/Dwindle layouts, cross-layout directional semantics, and layout-specific Size behavior.
- [x] Validate exact workspace names, display names, and layout types without asserting UUIDs or unnecessary monitor assignments.
- [x] Add app routing: Codex/Zed → `2`; all five listed browsers → `1`; Discord/Outlook/Messages/Spotify → `3`; assert Ghostty has no assignment.
- [x] Disable `hiddenBar.enabled` while retaining schema keys.

### Phase 2: Presentation and generated references

- [x] Rename presentation aliases to Quake, NewTerm, and Size using the existing raw bindings only.
- [x] Regenerate and freshness-check Corne/Sofle keyboard sheets.
- [x] Add `cheatsheets/macos-omniwm.yaml` and a focused host cheatsheet generator that derives workspace, routing, semantic HOST, and MacBook workflow facts from repository configuration.
- [x] Generate host SVG/PDF/manifest and validate content, hashes, terminology, workspace layouts, and required controls.

### Phase 3: CI and final verification

- [x] Add host PDF smoke generation to CI while retaining existing Corne/Sofle smoke checks.
- [x] Run the repository acceptance commands, inspect diagnostics, review the final diff, and confirm no firmware/protocol/Karabiner/OmniWM hotkey drift.
- [ ] Reconcile the live macOS drift check after the preserved OmniWM settings edits are committed or otherwise reconciled with `HEAD`.

## Verification

Required local checks:

```bash
uv run scripts/check_corne_keymap.py
uv run scripts/check_sofle_keymap.py
uv run scripts/check_build_config.py
uv run scripts/check_host_protocol.py
uv run scripts/check_generated.py
uv run scripts/generate_cheatsheet.py all --check
uv run scripts/generate_host_cheatsheet.py --check
```

Generation checks:

```bash
uv run scripts/generate_cheatsheet.py all
uv run scripts/generate_host_cheatsheet.py
```

On macOS, also run:

```bash
uv run scripts/check_host_drift.py
```

In this working tree, that read-only check reports the intentionally preserved, pre-existing `settings.toml` edits as uncommitted drift; it will pass after those edits are committed or reconciled with `HEAD`.

The final diff must show no changes to `config/**/*.keymap`, `protocol/semantic-v1.yaml`, `hosts/macos/karabiner/*.json`, or OmniWM hotkey bindings.

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Browser routing conflicts with the prior manual-browser policy | Medium | Treat the user's clarification as authoritative and encode all five current browser bundle IDs explicitly in the allowlist. |
| Generated host sheet drifts from host configuration | High | Hash every required input and validate regenerated SVG/PDF hashes plus key terminology and layout content. |
| Existing uncommitted OmniWM settings are overwritten | High | Inspect and preserve the existing diff; make only targeted additions/changes around it. |
| Alias regeneration changes keyboard artifacts broadly | Medium | Modify only the three requested raw alias values and run both keyboard generation/check commands. |
| OmniWM schema changes upstream | Medium | Keep schema version/update checks unchanged and validate current checked-in settings rather than pinning a release. |

## Open Questions

None. Browser routing was clarified as all currently listed browser apps → workspace `1`; Spotify → workspace `3`.
