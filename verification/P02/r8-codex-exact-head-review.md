# P02 Stage A r8 Codex Exact-Head Replay

Date: 2026-10-09 (Asia/Shanghai)

## Fixed object and scope

- Reviewed HEAD: `89413f45a601966eb40d7af7abea65cbdfc754b3`
- Tree: `f1063c981b8f4164f51248f92b7825fc205dd07d`
- Parent (r7): `38959ba99b84f771aba7010b53b9b47ecdc75488`
- Diff base: `5de8d44c784cbd20b23bcd41a8f1a7258c7addff`
- Frozen scope SHA-256: `27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425`
- Owner branch/worktree at delivery: `agent/antigravity/P02-real-webview-harness` / `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity`; independently verified clean at delivery.
- Codex replay worktree: `C:/Users/49745/.codex/worktrees/p02-stage-a-r8-exact/New Manga`, detached at the reviewed HEAD, sharing `G:/CODEX/New Manga/.git`.
- `base..HEAD`: 19 changed paths; 0 outside frozen allowlist. `git diff --check`: EXIT 0. See [`r8-codex-commit-scope.json`](r8-codex-commit-scope.json).

## Exact-head verification

| Check | Result | Evidence |
|---|---|---|
| Focused TypeScript protocol check, TypeScript 5.9.3, strict/noEmit, ES2021 + DOM | PASS / EXIT 0 | `r8-codex-tsc-exact.*` |
| Direct Python harness without a TypeScript invocation | EXIT 0; `execution_status=NOT_RUN`, `gate_status=NOT_RUN`, observed exit `null` | `r8-codex-direct-harness-not-run.*` |
| Direct harness with observed TypeScript exit `1` | `execution_status=FAIL`, `gate_status=FAIL`, observed exit `1`; process EXIT 1 | `r8-codex-tsc-fail-gate.*` |
| PRE-03 injected low contrast through production `run_preflight_checks()` and `main()` | PRE-03 `FAIL / exit_code=1`; `main()`/process EXIT 1 | `r8-codex-pre03-production-failure-propagation.*` |
| Absolute-path `-ProbeOnly` from `C:/Users/49745` using Windows PowerShell 5.1 | PASS / EXIT 0 | `r8-codex-external-cwd-probeonly.*` |
| `-ExceptionTest` on Windows PowerShell `5.1.26100.9549` | Expected EXIT 1; run log contains injected exception, stack trace, null child exit and `Status: FAILED` | `r8-codex-exception-test.*` |
| `-FinalizeFailTest` on Windows PowerShell 5.1 | Expected EXIT 42; run log records `Status: FAILED (EXIT=42)` | `r8-codex-finalize-fail-test.*` |
| Normal Full runner on fixed r8 | EXIT 0; PRE-01..03 PASS, AC1..AC6 BLOCKED | `r8-codex-full-run.*` |
| Final artifact hashes | 5/5 declared hashes match exact replay outputs | [`r8-codex-artifact-hash-check.json`](r8-codex-artifact-hash-check.json) |

The normal Full runner is the last harness run, so result JSON and final artifact hashes represent the successful exact r8 replay state. The six runtime ACs remain BLOCKED under the active Hard Build Barrier.

## R7 finding dispositions

- **R7-01 (P3):** r8 adds production `build_pre03_verdict`, `record_pre03_evaluation`, and `compute_harness_exit_code`. The production preflight calls the same recording method and `main()` calls the same exit helper. The in-repository self-check asserts a failing PRE-03 result has `status=FAIL`, `exit_code=1`, and a blocker reason; that the production recorder appends the corresponding verdict; and that the exit helper returns 1. It also asserts the all-pass verdict and exit are 0. Exact replay runs that self-check on both direct harness and Full invocations. Codex additionally injected a low contrast result through the actual production preflight/main path and observed PRE-03 `FAIL / 1` and main/process `1`.
- **R7-02 (P3):** explicitly recorded as `deferred (P3)` in `doc/tasks/P02.md`, `doc/handoffs/P02-stage-a-foundation-handoff.md`, and `verification/P02/RESUME.md`. Trigger: Step 2/3 failure before Step 4/5 may leave a prior `FINALIZED` JSON report beside the current failed mode log. No claim that it was fixed.

The independent Codex reviewer found R7-01 closed, R7-02 accurately deferred, and no new substantive issue in r7..r8; its disposition is recorded separately in `r8-codex-independent-review.md`.

## Limits

No Cargo/Tauri/sidecar build, frontend build, Vitest, product GUI, or real WebView interaction was run. These remain prohibited by the active Hard Build Barrier; Stage A checks do not satisfy AC1..AC6.

