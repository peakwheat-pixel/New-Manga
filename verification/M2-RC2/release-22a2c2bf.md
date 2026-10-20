# M2-RC2 Release Record

- **Decision:** User explicitly authorized Codex on 2026-09-27 to review, register, and separately release M2-RC2.
- **Task:** [M2-RC2 — Resource Channel Command Surface and Sidecar Boundary Hardening](../../doc/tasks/M2-RC2.md)
- **Release state:** `ready / RESOURCE_CHANNEL_COMMAND_SURFACE_RELEASED`
- **Owner / Reviewer / Integrator:** ZCode / DeepSeek Harness (non-author) / Codex
- **Dependency:** M2-RC1=`done` at integration `3a24684007fd5a5e855f324077ad996841300f27`.
- **Fixed implementation base:** `22a2c2bf9a70d8c3b81edcdbe0e1ef146db556e5` (master at release review).
- **Registration/release commit:** `9617cbd3e597a613629b278db65e1627aafc8d0e`; the Owner branch remains at the fixed base.
- **Post-release baseline evidence commit:** `cb8336d6bf9f514eff0ea36c9bbba30ecb5feb82`; this adds the requested fixed-command ledger without moving the Owner branch.
- **Owner branch:** `agent/zcode/M2-RC2-resource-channel-hardening`
- **Owner worktree:** `C:/Users/49745/.codex/worktrees/m2-rc2-zcode/New Manga`
- **Contract baseline:** `fc35913801297ee1876ea395f9c5041a16226f20` (`HEAD:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`).

## Independent release review

Codex checked the M2-RC1 `done` dependency and reviewed the proposed Task scope against its F-03/F-05 accepted deferrals. The release freezes the command allowlist and denial coverage, Tauri capability/ACL/CSP boundary, Core/SQLite catalog authority, and an independently launchable Python resource-channel sidecar. The Task does not authorize edits to shared Contract, SQLite schema/migrations, root dependency/lock files, Legacy QML, user source files, or packaging/release paths. `src/infrastructure/__init__.py` is conditionally allowed only if an isolation test demonstrates need and the Owner records the reason in Task/Handoff.

The Owner worktree was created by Codex's managed worktree facility from the exact base, then switched from detached HEAD to the registered Owner branch without changing its tree. Initial verification:

| Check | Result |
|---|---|
| `git rev-parse --show-toplevel` | `C:/Users/49745/.codex/worktrees/m2-rc2-zcode/New Manga` |
| `git rev-parse --path-format=absolute --git-common-dir` | `G:/CODEX/New Manga/.git` |
| `git branch --show-current` | `agent/zcode/M2-RC2-resource-channel-hardening` |
| `git status --short --branch` | clean; branch has no implementation changes |
| `git rev-parse HEAD` | `22a2c2bf9a70d8c3b81edcdbe0e1ef146db556e5` |
| Contract blob | `fc35913801297ee1876ea395f9c5041a16226f20` |

## Fixed verification gate

After Owner implementation and before independent Review, run the following commands from the repository root on Windows and preserve raw output, exact environment/tool versions, timestamps, and process exit codes under `verification/M2-RC2/`:

| Stack | Fixed command | Required evidence |
|---|---|---|
| Python/Core | `python -m pytest tests/m2_resource_channel -q` | Command-boundary denial and Core/SQLite catalog authority cases included; raw log and exit code. |
| Tauri/Rust | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --locked` | Command allow/deny and capability-boundary cases; raw log and exit code. |
| Frontend | `npm test --prefix apps/desktop/frontend -- --run` | WebView invoke allow/deny behavior with synthetic resources; raw log and exit code. |
| E2E/sidecar | `python verification/M2-RC2/run_e2e.py` | This runner is a required Task deliverable. Exercise the real sidecar launch/import boundary and command denial cases; capture loaded module set, raw log, and exit code. |

The E2E runner does not exist at release and is explicitly a planned Owner deliverable. Each command must be recorded as `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`; do not infer success from missing output. Required environment includes Windows, project Python environment, Rust/Cargo, Node/npm, and WebView2 for E2E. Use synthetic resources only. Owner Handoff must state `S1-B3/B5/B6/B8` individually and retain `UNVERIFIED`/`NOT_RUN` where evidence is absent. At RC1 closeout, S1-B3/B6/B8 were `NOT_RUN`; S1-B5 covered only that old IDs do not rebind after Core restart, while key lifecycle remains unverified. No product-level security, install, or packaging readiness statement is authorized.

No product implementation was performed as part of release registration. Post-release baseline suite results at the unchanged fixed-base branch are recorded separately in [release-validation-22a2c2bf](release-validation-22a2c2bf.md); they exercise the RC1 baseline and do not satisfy RC2 Acceptance Criteria. The Owner must copy only `doc/tasks/M2-RC2.md` from post-release evidence commit `cb8336d6bf9f514eff0ea36c9bbba30ecb5feb82` to the fixed-base branch, commit `ready` → `in_progress`, then begin implementation. Do not merge any master governance commit into the Owner branch.
