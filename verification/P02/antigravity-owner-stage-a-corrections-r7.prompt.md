# Antigravity continuation: P02 Stage A r7 corrections

Continue the existing P02 Owner conversation `054911c9-b133-4514-b471-143b80249fce`. This is an authorized correction pass inside the already frozen P02 scope, not a new scope freeze.

## Fixed context

- Repository: `G:/CODEX/New Manga`
- Owner worktree: `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity`
- Branch: `agent/antigravity/P02-real-webview-harness`
- Reviewed r6 HEAD/tree: `38672473f93971a4681aef682e5635e64b0bd896` / `2aa967bbf961a0e9e58dd3e1489d74635491e28f`
- Parent r5: `172eee84240e101186b12f1aa09e8a2f9ec92d68`
- Diff base/main: `5de8d44c784cbd20b23bcd41a8f1a7258c7addff`
- Frozen P02 scope SHA-256: `27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425`
- P02 remains `in_progress / ACTIVE`; `integration_commit: null`.

## Formal review input

DeepSeek Harness formal r6 Review: `verification/P02/implementation-stage-a-r6-dsh-review.md`; decision `approved_with_conditions` for Stage A only; counts P0/P1/P2/P3=`0/0/0/4`, open=4. R5-01..R5-06 are closed. Codex exact replay is in `verification/P02/r6-codex-exact-head-review.md` and `verification/P02/r6-codex-artifact-hash-check.json`.

## Required corrections for all R6 findings

- **R6-01 (P3, TypeScript resolver CWD dependency):** `run-webview.ps1` currently runs `git rev-parse --git-common-dir` using the caller's current directory. Resolve Git metadata explicitly from `$RepoRoot` (e.g. `git -C $RepoRoot rev-parse --git-common-dir` or a safe `Push-Location $RepoRoot`) so invoking the script by absolute path from another directory does not falsely report the installed shared-root tsc as missing. Add a focused check from both worktree root and an unrelated CWD.
- **R6-02 (P3, machine gate means presence, not execution):** `typescript_contract_gate.gate_status` must distinguish the compiler being found from TypeScript having actually run and passed. A direct Python harness invocation without a TS run must not report `PASS`; use explicit `NOT_RUN` or pass the actual observed Step 2 exit into the report and aggregate a failed/not-run gate appropriately for the Stage A runner. Keep the normal runner fail-closed and do not install dependencies/network.
- **R6-03 (P3, self-checks duplicate formulas):** Make PRE-02 stale-PASS/nonzero-retry and PRE-03 failed-ratio checks exercise the same production helper/caller path used by the real verdicts, then assert the resulting PRE verdict and exit status. An injected subprocess or focused production helper with temporary synthetic inputs is acceptable; avoid a copied Boolean expression that can stay green after the production path regresses.
- **R6-04 (P3, microprobe Scenario C not executed):** Either execute a reproducible Windows PowerShell 5.1 catch-path failure and archive the command/output/exit plus actual FAILED log, or relabel Scenario C as static-only/NOT_RUN. Update Task/Handoff/RESUME so only actually executed scenarios are called runtime microprobes; keep Scenario A/B evidence unchanged and preserve prior DSH reports.

## Verification and delivery

- Keep all changes within the frozen Owner allowlist; do not alter AC, requirements, product code, shared contracts, dependencies, or scope.
- Run focused tests only: strict E2E TypeScript check; direct Python harness must show `NOT_RUN` (or true observed status) absent a tsc result; normal ProbeOnly and Full runner; R6-01 caller-CWD check; the production-path R6-03 self-checks; PowerShell 5.1 Scenario C only if choosing to execute it; `git diff --check`.
- No Cargo/Tauri/sidecar build, frontend build, Vitest, product GUI, real WebView interaction, or user-data access. Keep Hard Build Barrier active and AC1–AC6 BLOCKED. Do not shut down the machine or stop unrelated work.
- Commit r7 on the existing Owner branch; report fixed HEAD/tree/parent, clean Owner worktree, exact per-finding disposition, real commands/outputs/exits, and limitations. Do not merge/integrate to main.
- Preserve user source/data, current/pinned revisions, locks, recoverability, root dirty/untracked files and historical Review artifacts. Do not claim r6 or r7 has been integrated.
