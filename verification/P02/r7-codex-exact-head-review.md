# P02 Stage A r7 Codex Exact-Head Replay

Date: 2026-10-09 (Asia/Shanghai)

## Fixed object and scope

- Reviewed HEAD: `38959ba99b84f771aba7010b53b9b47ecdc75488`
- Tree: `5bf0c81a0ee814f857ad4c1f0b3f598f963fa1c5`
- Parent: `38672473f93971a4681aef682e5635e64b0bd896`
- Diff base: `5de8d44c784cbd20b23bcd41a8f1a7258c7addff`
- Frozen scope SHA-256: `27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425`
- Owner branch/worktree at delivery: `agent/antigravity/P02-real-webview-harness` / `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity`; clean at delivery.
- Codex replay worktree: `G:/CODEX/New Manga.worktrees/P02-stage-a-validation-38959ba99-exact`, detached at the reviewed HEAD.
- `base..HEAD`: 19 changed paths; all are within the frozen allowlist. `git diff --check`: EXIT 0. Scope inventory: [`r7-codex-commit-scope.json`](r7-codex-commit-scope.json).

The replay changed only generated evidence files in the detached worktree. The Owner delivery worktree remains clean and no commit was made or integrated by Codex.

## Exact-head verification

| Check | Result | Evidence |
|---|---|---|
| Focused TypeScript protocol check, TypeScript 5.9.3, strict/noEmit, ES2021 + DOM | PASS / EXIT 0 | `r7-codex-tsc-exact.*` |
| `git diff --check 5de8d44..38959ba` | PASS / EXIT 0 | `r7-codex-diff-check.*` |
| `-ProbeOnly` invoked by absolute path from `C:/Users/49745` using Windows PowerShell 5.1 | PASS / EXIT 0; confirms caller-CWD independent Git resolution | `r7-codex-external-cwd-probeonly.*` |
| Direct Python harness without a TypeScript invocation | PASS / EXIT 0; `execution_status=NOT_RUN`, `gate_status=NOT_RUN`, observed exit `null` | `r7-codex-direct-harness-not-run.*` |
| Direct harness with injected observed TypeScript exit `1` | Correctly records `execution_status=FAIL`, `gate_status=FAIL`, observed exit `1`; process EXIT 1 | `r7-codex-tsc-fail-gate.*` |
| PRE-03 injected low-contrast result through production `run_preflight_checks()` and `main()` | `PRE-03=FAIL`, verdict exit `1`, `main()`/process EXIT 1 | `r7-codex-pre03-production-failure-propagation.*` |
| `-ExceptionTest` on Windows PowerShell `5.1.26100.9549` | Expected EXIT 1; actual log records injected exception, stack trace, unavailable child output, null child exit, and `Status: FAILED` | `r7-codex-exception-test.*` |
| `-FinalizeFailTest` on Windows PowerShell 5.1 | Expected EXIT 42; actual full log ends `Status: FAILED (EXIT=42)` | `r7-codex-finalize-fail-test.*` |
| Normal `-ProbeOnly` and Full runner on fixed r7 | Both EXIT 0; PRE-01..03 PASS, AC1..AC6 BLOCKED | `r7-codex-external-cwd-probeonly.*`, `r7-codex-full-run.*` |
| Final artifact hashes | 5/5 declared hashes match the exact replay outputs | [`r7-codex-artifact-hash-check.json`](r7-codex-artifact-hash-check.json) |

The normal Full runner is the last harness run, so the committed-shape results and artifact hashes are restored to the successful r7 replay state. The six runtime ACs remain BLOCKED under the existing Hard Build Barrier.

## R6 conditions and residual review question

- R6-01 is exercised from an unrelated caller CWD and passes.
- R6-02 is exercised both with no TypeScript execution (`NOT_RUN`) and an observed failing exit (`FAIL`, exit 1); the normal Full runner records the real successful TypeScript run.
- R6-03 self-checks now call production helpers. The PRE-02 self-check asserts stale-report removal, subprocess exit 42, and final failed probe result. PRE-03's in-code self-check still asserts the production aggregate helper result but does not call `run_preflight_checks()` or `main()`; that remaining assertion gap was independently reported as P3 by the Codex read-only reviewer. To assess caller-level behavior without editing r7, Codex separately injected a low contrast result and invoked the actual production `run_preflight_checks()` and `main()`; the resulting PRE-03 verdict and top-level exit were both 1 (evidence above). DSH should decide whether this fixed-head dynamic evidence closes the review condition or whether a source self-check change and new commit are still required.
- R6-04 is exercised by the actual PowerShell 5.1 `-ExceptionTest` path, with the captured FAILED log.

## Limits

No Cargo/Tauri/sidecar build, frontend build, Vitest, product GUI, or real WebView interaction was run. These remain prohibited by the active Hard Build Barrier; PRE checks are Stage A harness evidence only and do not satisfy AC1..AC6.

