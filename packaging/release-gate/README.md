# M2 Release Gate runner (M2-RG1)

`run_release_gate.py` is the machine-verifiable executor for the M2 Release
Gate (doc/tasks/M2-RG1.md) — Windows local-machine ruling, 2026-09-29:
**this machine (Windows 11 x64, build 26200) is the clean Windows basis; a
local pass ⇒ gate PASS.**

## What it does

| AC | Scenarios | Method |
|---|---|---|
| AC1 | RG1-E2 | binds every gate run to the installer sha256 (NSIS bundle built in the owner worktree) |
| AC2 ① | RG1-PE1 | installed `m2rc1-desktop.exe` PE OptionalHeader Subsystem == 2 (GUI), parsed with stdlib only (e_lfanew@0x3C → optional header +68 → u16) |
| AC2 ② | RG1-CW0/CW1/CW2 | runtime EnumWindows observation over BOTH console-host classes (`ConsoleWindowClass` + `CASCADIA_HOSTING_WINDOW_CLASS`, the latter owned by WindowsTerminal.exe under Win11 default-terminal delegation — pid attribution is impossible there by design, the title heuristic carries attribution; boundary disclosed in code + registry snapshot): visible console-host windows owned by {app pid + live sidecar pids} or titled with any frozen entry name must be 0 — sampled while the app runs (production mode, app alive + sidecar pids asserted present) and after a graceful clean exit. `RG1-CW0-positive-control` proves the detector can see RED: a `powershell` child spawned with CREATE_NEW_CONSOLE (deliberately no CREATE_NO_WINDOW) must be observed (>= 1 hit) before being reaped |
| AC2 ③ | RG1-PE2 | static source audit: `windows_subsystem` stays behind `cfg_attr(not(debug_assertions), …)`; every `creation_flags(CREATE_NO_WINDOW)` sits inside `#[cfg(windows)]`; `core_sidecar.spec` keeps `console=True` |
| AC3 | RG1-CS1/CS2/CS3 | record-only cold-start timers (no thresholds, frozen ruling): app window-appearance, `core_service.exe` stdio ready, `acceptance_bridge.exe` ready; ≥3 samples each, min/median/max; purged PATH + per-round lab APPDATA |
| AC4 | RG1-DC1a/DC1b/DC2/DC3/DC4, RG1-W1 | four install-state stdio round trips (core_service ping + ListBooks — the data root is seeded first through the acceptance bridge's `seed_fixture` so ListBooks must return >= 1 fully-keyed row, host_bridge ping+issue/resolve/revoke over a loader-seeded catalog, acceptance_bridge handshake, catalog_loader seed + sqlite read-back with CLI args confirmed from the worktree source); the ONE merged PyInstaller warn file for the spec is copied to raw/ and every missing module is classified (PyInstaller 6 emits one warn-<spec>.txt covering all four entries) |

## Usage

```powershell
# from the repository root (acceptance tooling may use the dev venv python)
python packaging/release-gate/run_release_gate.py [--installer <path>] [--samples 3]
```

Artifacts: `verification/M2-RG1/raw/rg1-gate.json` (machine-readable; installer
sha256 + per-scenario verdict + timings + environment snapshot), the runner
console transcript (redirected by the caller into
`verification/M2-RG1/raw/rg1-gate-run.log`) and `rg1-warn-*.txt`.

## Safety (M2-AC5 r1 P2-4 red line)

The runner deletes ONLY lab / install directories it created under the system
temp dir. It NEVER writes or deletes the host's real
`%APPDATA%\com.newmanga.m2rc1.desktop` (P2-4 red line). Zero-touch rests on
TWO mechanisms, not one (DSH r1 P2-3; corrected r2 P1-1(N)): (1) every spawned
process (app and sidecars) receives `APPDATA` pinned into the lab, and (2) the
packaged host derives the data roots from that lab APPDATA and passes them
explicitly to the core sidecar (main.rs `packaged_user_root()` +
library_bridge `NEWMANGA_DATA_ROOT`), while core_service's un-pinned fallback
would be `%LOCALAPPDATA%\New Manga`. `NEWMANGA_DATA_ROOT` is pinned explicitly
only inside the core/ac1/seed/DC1b/DC3 probes — the app rounds
(`timed_app_cold_start`) do NOT pin it; their zero-touch rests on the APPDATA
pin plus the host-side derivation and explicit pass-down. The host user
profile is unreachable by construction.
