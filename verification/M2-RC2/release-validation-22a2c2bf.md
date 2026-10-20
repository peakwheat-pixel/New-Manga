# M2-RC2 Post-Release Baseline Validation

- **Date/time:** 2026-09-27, 15:00–15:02 Asia/Shanghai.
- **Purpose:** User-requested fixed-command check after release, run against the unchanged Owner branch/base `22a2c2bf9a70d8c3b81edcdbe0e1ef146db556e5` before RC2 implementation. These results confirm the RC1 baseline/environment only; they do **not** satisfy RC2 acceptance criteria.
- **Worktree/branch:** `C:/Users/49745/.codex/worktrees/m2-rc2-zcode/New Manga`, `agent/zcode/M2-RC2-resource-channel-hardening`.
- **Environment:** Windows 11 Pro build `26200`; PowerShell `7.6.6`; Python `3.14.6`; Cargo `1.98.1 (797e8a9bc 2026-08-05)`; rustc `1.98.1 (48a229cea 2026-09-01)`; Node `v24.15.0`; npm `12.0.1`; Vitest `v2.1.9`.

## Environment preparation

The first Cargo attempt exited `1` because `apps/desktop/frontend/dist` was absent; its Tauri build script regenerated two tracked schema files, which were restored to `HEAD` after validation. The first frontend attempt exited `1` because Vitest was not installed in this new worktree. The frontend package has a committed `package-lock.json`; dependencies were installed without changing manifests or lockfiles, then the frontend build generated the required ignored `dist` directory:

| Command | Exit | Result |
|---|---:|---|
| `npm ci --prefix apps/desktop/frontend` | 0 | 99 packages added. npm reported 5 audit findings (3 moderate, 1 high, 1 critical) and a blocked `esbuild` install script; no audit fix or dependency change was made. |
| `npm run build --prefix apps/desktop/frontend` | 0 | TypeScript and Vite production build passed; `dist` generated. |

## Fixed Task commands

| Command | Exit | Status / output |
|---|---:|---|
| `python -m pytest tests/m2_resource_channel -q` | 0 | `43 passed in 2.03s`; `PASS` for baseline suite. |
| `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --locked` | 0 | `12 passed; 0 failed`; three existing unused-import warnings in `src/main.rs`; `PASS` for baseline suite. |
| `npm test --prefix apps/desktop/frontend -- --run` | 0 | Vitest `v2.1.9`; 1 file / 8 tests passed; `PASS` for baseline suite. |
| `python verification/M2-RC2/run_e2e.py` | 1 | `BLOCKED`: runner does not exist yet; Python reported `[Errno 2] No such file or directory`. This runner is a required RC2 Owner deliverable. No WebView2/sidecar E2E behavior was exercised. |

The initial pre-setup attempts were: the same Cargo command exit `1` (`frontendDist` absent) and the same frontend test command exit `1` (`vitest` not recognized). Both passed after locked environment preparation above. The missing RC2 E2E runner remains blocked rather than being counted as a test failure or pass.

Afterward, test-generated tracked schema files were restored to the clean fixed base. The Owner branch has no tracked changes; ignored dependency/build caches (`node_modules`, frontend `dist`, Cargo `target`) remain available in this worktree. No source implementation or dependency/lockfile was changed.
