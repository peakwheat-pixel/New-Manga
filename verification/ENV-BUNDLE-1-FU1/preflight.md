# ENV-BUNDLE-1-FU1 Preflight

Timestamp: 2026-10-16 09:12 UTC onward. Agent: Codex. Worktree: `G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1-FU1`.

## Task worktree

- Branch: `codex/ENV-BUNDLE-1-FU1-packaged-acceptance`
- Start HEAD: `3bf2604dc9e8ef6be47bd80897e4df05cae077b3`
- Git common directory: `G:/CODEX/New Manga/.git`
- Initial worktree status: clean (`git status --porcelain=v1 --untracked-files=all` emitted no lines).

## Build feasibility probe

Commands were read-only probes; no Cargo command was run before the missing ignored inputs were built.

| Check | Result |
|---|---|
| `Get-Volume -DriveLetter G` | free `1,496,229,715,968` bytes of `2,048,405,794,816` bytes |
| Isolated Python | `G:/CODEX/New Manga.task-envs/m2ac5-build/Scripts/python.exe`; Python `3.12.3`; `pip check`: `No broken requirements found.` |
| PyInstaller | `6.22.3` in the existing venv; venv was not recreated |
| Node / npm | Node `v24.15.0`; npm `12.0.1` |
| Rust toolchain availability (without invoking Cargo) | `cargo.exe`, `rustc.exe`, `rustfmt.exe` found; `rustc 1.98.1 (48a229cea 2026-09-01)`; active toolchain `stable-x86_64-pc-windows-msvc` |
| Frontend lock | `apps/desktop/frontend/package-lock.json` exists; build script is `tsc && vite build` |
| Registry | `npm view --fetch-retries=0 --fetch-timeout=8000 typescript version` succeeded (`7.0.2`) |
| Current worktree ignored inputs | `apps/desktop/src-tauri/target/core-sidecar`, `apps/desktop/frontend/dist`, and `apps/desktop/frontend/node_modules` were absent |
| Pinned weights required by the full build | Manga model `171,543,900` bytes SHA-256 `037930a861e67870eb345be01b28cc70d7e2b7956528e48ee0ebdb0c093df80d`; `config.json` `2,320` bytes SHA-256 `b6d707933e12e9593a7025604be1c95add70a6db371fdd1532e8854e2256e072`; `preprocessor_config.json` `470` bytes SHA-256 `7e9e2245806aa3ef068a5321f5eebee3116fa4cec560173231954ffaca930eca`; SFX `yolo11s-seg.onnx` `40,824,255` bytes SHA-256 `944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d` |

The probe passed. The required no-`-SkipWeights` sidecar rebuild and locked frontend install/build are feasible to start.

## Main-worktree protected baseline

- Main path: `G:/CODEX/New Manga`; branch: `main`; HEAD: `4dcd5a9499f17d1b189f3b67f3a3ac59509b2337`.
- `git status --porcelain=v1 --untracked-files=no`: exactly the 19 user-owned dirty paths recorded in [`main-status-before.txt`](main-status-before.txt).
- Status bytes SHA-256: `a72d1076a20534021c50709972e760a66b7b65d220248284e518eb8f891d460a`.
- `git diff --binary`: 250,300 bytes; SHA-256 `fde78be03b5e5be8a01d10050703c2b2e587756b8d77a39be6bce05d1e7bfe35`.
- `git diff --name-status 3bf2604dc9e8ef6be47bd80897e4df05cae077b3 4dcd5a9499f17d1b189f3b67f3a3ac59509b2337 -- src apps/desktop packaging`: empty; the Task base and main have identical tracked product/build inputs in those paths.
- Before artifact refresh, the ignored `core_service.exe` was `68,604,146` bytes, SHA-256 `61f128d6878baad1c72fa24f7cda75675b31354ea47b43828861e7d8b2ca91f0`, last write `2026-10-14T07:09:42.0164828Z`.
- A direct isolated `core.ping` using the expected 2.3 request received `PROTOCOL_VERSION_UNSUPPORTED`; the old process identified its protocol as `1.6`. Raw output is in [`main-old-core-ping-before.log`](main-old-core-ping-before.log).
- Main `frontend/dist` was 2 files / 196,591 bytes, aggregate manifest SHA-256 `d6dd3bdbea477414f72a92fe19f75d402cd41c945e81d82f2842f64a1c96c041`; see [`main-artifacts-before.md`](main-artifacts-before.md).

This snapshot is the AC6 comparison baseline. The 19 dirty files are not task write targets.
