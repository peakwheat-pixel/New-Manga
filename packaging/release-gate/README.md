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
| AC2 ② | RG1-CW1/CW2 | runtime EnumWindows observation: visible `ConsoleWindowClass` top-level windows owned by {app pid + live sidecar pids} or titled with any frozen entry name must be 0 — sampled while the app runs (production mode) and after a graceful clean exit |
| AC2 ③ | RG1-PE2 | static source audit: `windows_subsystem` stays behind `cfg_attr(not(debug_assertions), …)`; every `creation_flags(CREATE_NO_WINDOW)` sits inside `#[cfg(windows)]`; `core_sidecar.spec` keeps `console=True` |
| AC3 | RG1-CS1/CS2/CS3 | record-only cold-start timers (no thresholds, frozen ruling): app window-appearance, `core_service.exe` stdio ready, `acceptance_bridge.exe` ready; ≥3 samples each, min/median/max; purged PATH + per-round lab APPDATA |
| AC4 | RG1-DC1..DC4, RG1-W1 | four install-state stdio round trips (core_service ping+ListBooks, host_bridge ping+issue/resolve/revoke over a loader-seeded catalog, acceptance_bridge handshake, catalog_loader seed + sqlite read-back with CLI args confirmed from the worktree source); four PyInstaller warn files copied to raw/ and every missing module classified |

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
`%APPDATA%\com.newmanga.m2rc1.desktop`. Every spawned process (app and
sidecars) receives `APPDATA` pinned into the lab, so the host user profile is
unreachable by construction (scenario RG1-Z1 documents the path).
