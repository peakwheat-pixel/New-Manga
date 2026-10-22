# Antigravity continuation: P02 Stage A r6 corrections

Continue existing P02 Owner conversation `054911c9-b133-4514-b471-143b80249fce`. This is an authorized continuation inside the already frozen P02 scope, not a new scope freeze.

## Fixed context

- Repository: `G:/CODEX/New Manga`
- Owner worktree: `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity`
- Branch: `agent/antigravity/P02-real-webview-harness`
- Current reviewed HEAD: `172eee84240e101186b12f1aa09e8a2f9ec92d68`
- Current tree: `a5b1af3e0708463df6865c8e49c9679e57e3fa85`
- Parent r4: `cc1bd7505f3fc48079db7ea2719040e77a8c58dd`
- Diff base: `5de8d44c784cbd20b23bcd41a8f1a7258c7addff`
- Frozen P02 scope/allowlist SHA-256: `27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425`
- P02 remains `in_progress / ACTIVE`; `integration_commit: null`.
- Do not redo P01, alter product requirements, re-freeze P02, broaden the allowlist, or modify source implementation/shared contracts/dependencies. Read the current P02 Task, collaboration protocol, Handoff and RESUME before editing. Only use paths already allowed by the frozen Task.

## Review inputs

- Formal DSH r5 report: `G:/CODEX/New Manga/verification/P02/implementation-stage-a-r5-dsh-review.md` (decision `changes_requested`, P0/P1/P2/P3=`0/0/2/4`, open=6).
- Codex exact replay: `G:/CODEX/New Manga/verification/P02/r5-codex-exact-head-review.md`.
- Codex independent supplement: `G:/CODEX/New Manga/verification/P02/r5-codex-independent-review.md`.
- Owner r5 response: `G:/CODEX/New Manga/verification/P02/antigravity-owner-stage-a-corrections-r5.response.md`.

## Required dispositions for all DSH r5 findings

- **R5-01 (P2):** Keep the true probe `proc.returncode` separate from report data. Every PRE-02 PASS predicate must require the consumed report to be fresh and valid, observed process exit `0`, report exit `0`, and overall `PASS`. A retry failure before JSON replacement must never let the previous report pass. Add one minimal caller-level self-check that simulates stale prior PASS + nonzero retry and asserts PRE-02 is not PASS.
- **R5-02 (P2):** Do not log Full Stage A success before `--finalize` succeeds. Treat finalization as a logged step. On nonzero finalizer exit, append explicit FAILED status, command, and exit code and flush before exit. On success, write an explicit terminal `COMPLETED` status and flush. Exercise both success and a deterministic nonzero finalizer path without running build/product GUI.
- **R5-03 (P3):** Make thrown native-process failure evidence truthful: retain captured stdout/stderr (or clearly mark each unavailable), record an observed child exit only when known, otherwise `null/UNKNOWN` rather than stale `$LASTEXITCODE`, and include exception type/message/stack. Run a reproducible Windows PowerShell 5.1 failure microprobe and archive its command/output/exit under `verification/P02/**`; if any claim cannot be reproduced, reduce the Task/Handoff/RESUME claim.
- **R5-04 (P3):** Resolve the installed TypeScript compiler without a hardcoded `G:\CODEX\New Manga\...` checkout path (e.g. current repo root plus linked-worktree Git common repo root). If absent, fail closed or record an explicit machine-readable NOT_RUN/FAIL and ensure the overall Stage A runner cannot falsely report success. Add a small focused assertion for the missing-compiler branch; do not install packages or use the network.
- **R5-05 (P3):** Derive PRE-03 status and `all_passed` from all calculated token/live/alpha contrast results; one FAIL must make the scenario fail. Add a minimal self-check proving a failed ratio cannot leave the top-level PRE-03 PASS.
- **R5-06 (P3):** Correct Task/Handoff/RESUME: R4-04/R4-06 must not be described as fully closed when residuals remain; distinguish earlier claimed microprobe from newly archived evidence. Preserve all source DSH reports and historical snapshots; do not rewrite history or change AC/scope.

## Verification and delivery

- Run only focused P02 checks: the strict E2E TypeScript check, PRE-01..03 and their self-checks, ProbeOnly and Full runner, injected failure/finalization probes, and `git diff --check`.
- Do not run Cargo, Tauri, sidecar build, Vitest, product GUI or real WebView interactions. Keep AC1–AC6 BLOCKED and Hard Build Barrier active.
- Preserve user source/data, locks, current/pinned revisions, recovery paths, and root dirty/untracked files. Do not shut down the machine or stop unrelated work.
- Commit r6 on the existing Owner branch; return fixed HEAD/tree/parent and a clean Owner worktree. Do not merge/integrate to `main`.
- Update Task/Handoff/RESUME with exact per-finding disposition, commands and outputs/exits, limitations, and next Gate. Keep P02 active and `integration_commit: null`.
- Response must separate completed, failed, and NOT_RUN checks; do not claim findings closed or testing passed unless evidence supports it.
