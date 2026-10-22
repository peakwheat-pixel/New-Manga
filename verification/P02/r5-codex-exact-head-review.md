# P02 Stage A r5 Codex exact-head replay

更新时间：2026-10-09（Asia/Shanghai）。本报告核验 r5 Owner 交付的固定对象；它是 DSH Review 输入，不代表 DSH 已批准或 P02 可集成。

## 固定对象与范围

- Base=`5de8d44c784cbd20b23bcd41a8f1a7258c7addff`
- Parent r4=`cc1bd7505f3fc48079db7ea2719040e77a8c58dd`
- Owner branch=`agent/antigravity/P02-real-webview-harness`
- Owner worktree=`G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity`
- Fixed r5 HEAD=`172eee84240e101186b12f1aa09e8a2f9ec92d68`
- Fixed tree=`a5b1af3e0708463df6865c8e49c9679e57e3fa85`
- Task scope SHA-256=`27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425`
- HEAD parent、tree、branch、worktree root/common-dir 与 Owner 报告相符；Owner worktree clean。
- r5 差量 16 paths，均位于冻结允许的 `apps/desktop/frontend/e2e/**`、`verification/P02/**`、`doc/handoffs/P02-*.md`、`doc/tasks/P02.md`；未修改生产 frontend `src/**`、Tauri/Rust、Python Core、SQLite、共享 IPC/Schema、依赖、设计 token 或 Codex-only 治理路径。Task AC/基线/allowlist SHA 未改，Task=`in_progress / ACTIVE`，`integration_commit: null`。

## Codex exact-head 命令

两种模式分别在从 r5 HEAD 新建的干净 detached worktree 运行：

| 检查 | Exit | 证据 |
|---|---:|---|
| `git diff --check 5de8d44c784cbd20b23bcd41a8f1a7258c7addff 172eee84240e101186b12f1aa09e8a2f9ec92d68` | 0 | `r5-codex-diff-check.stdout.log`, `.stderr.log`, `.exit` |
| focused strict TypeScript check on detached r5 `workbench_driver_protocol.ts` | 0 | `r5-codex-tsc-exact.stdout.log`, `.stderr.log`, `.exit` |
| `powershell.exe -NoProfile -ExecutionPolicy Bypass -File verification/P02/run-webview.ps1 -ProbeOnly` | 0 | `r5-codex-exact-probeonly.stdout.log`, `.stderr.log`, `.exit` |
| `powershell.exe -NoProfile -ExecutionPolicy Bypass -File verification/P02/run-webview.ps1` | 0 | `r5-codex-exact-full.stdout.log`, `.stderr.log`, `.exit` |

The runner's TypeScript command also ran in both exact replays. The detached checkouts contain no local `node_modules`; the committed runner selects the existing TypeScript binary at `G:/CODEX/New Manga/apps/desktop/frontend/node_modules/typescript/bin/tsc`. No package install or network access occurred.

## Exact Full report and artifact bytes

The Full report in the second detached worktree records `source_head=172eee84240e101186b12f1aa09e8a2f9ec92d68`, `source_tree=a5b1af3e0708463df6865c8e49c9679e57e3fa85`, and `finalization_status=FINALIZED`. PRE-01/02/03 are `PASS` with exit 0; AC1–AC6 remain `BLOCKED` with `exit_code: null`.

All five finalized hashes in `p02-harness-results.json` match the exact bytes in that Full detached worktree:

| Artifact | SHA-256 | Result |
|---|---|---|
| `env-identity-report.json` | `a1eb4396e547ce84919d97500980f5df4ab194ac323fef373d4b084d64b2a731` | match |
| `static-control-report.json` | `33343b793bd1129ece097ab5188146a0ec5a3e92c87ebd7d293b50b00ac3bdc1` | match |
| `p02-harness-results.txt` | `7111d9d99cdbe6efd905c077d0b7994bac62941a877b72fc586ff01243199d0d` | match |
| `probe-execution-probeonly.log` | `e2d31bf1b6b6fcb77be64c94e4dcb730d5d1e29a6f3e5f774b4d2d6c123c6b20` | match |
| `probe-execution-full.log` | `4c799d3e28b580780dff154698305056304b67e428c6e7f0d61bd95e6b778da0` | match |

Both Codex-generated mode logs are UTF-8 without BOM and use LF only; each includes the focused TypeScript step. The runner truncates the per-mode log at start and marks it `IN_PROGRESS`; Full then records the Stage A completion and returns exit 0. Exact stdout/stderr/exit artifacts and detached worktrees remain preserved.

## Focused failure-path check for R4-06/R4-10

In a third disposable detached worktree at the same fixed r5 HEAD, Codex set child PowerShell 5.1 `NODE_OPTIONS=--require=C:\__p02_missing_preload__.js` to inject a deterministic Node/TypeScript process failure. The runner returned exit 1 and replaced the mode log with a fresh `IN_PROGRESS` record. Evidence: `r5-codex-failure-path.stdout.log`, `.stderr.log`, `.exit`; the isolated worktree is `G:/CODEX/New Manga.worktrees/P02-stage-a-validation-172eee84-failureprobe`.

The injected failure shows R4-10's stale-log protection works for this failed Step 2 run. R4-06 is **not yet fully evidenced as closed**: the log captures the failed step, command/arguments, exception type and `LastExitCode: 1`, but `Exception Message` contains only the first line (`node:internal/modules/cjs/loader:1479`); the full process diagnostic is present in the outer PowerShell stdout/stderr artifacts, but the runner's mode log does not attach it as the failed Step 2 output or record a dedicated failed-output field. The r5 owner report claims a PowerShell 5.1 microprobe, but no standalone microprobe artifact is committed. DSH should independently disposition this residual; Codex is not silently marking R4-06 closed.

## Gate disposition

Exact fixed-head replay and path/scope checks passed, so r5 is ready for the requested formal DSH review. This is not Integration Gate approval: the independent DSH Review is pending, and the failure-path observation above should be considered. No Cargo/Tauri/sidecar build, Vitest, product GUI, real WebView interaction, or AC1–AC6 execution was performed.
