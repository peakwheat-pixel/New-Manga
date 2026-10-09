# Antigravity continuation: P02 Stage A R8-01 correction

Continue the existing authorized P02 Owner conversation `054911c9-b133-4514-b471-143b80249fce`. This is one narrowly scoped correction inside the already frozen P02 Task, not a new Task or scope freeze.

## Fixed context

- Repository: `G:/CODEX/New Manga`
- Owner worktree: `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity`
- Branch: `agent/antigravity/P02-real-webview-harness`
- Fixed parent/base for this correction: r7 HEAD `38959ba99b84f771aba7010b53b9b47ecdc75488`, tree `5bf0c81a0ee814f857ad4c1f0b3f598f963fa1c5`; P02 source base remains `5de8d44c784cbd20b23bcd41a8f1a7258c7addff`.
- Frozen scope SHA-256: `27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425`.
- P02 remains `in_progress / ACTIVE`, `integration_commit: null`; keep the existing acceptance criteria, allowlist, behavior baseline and dependencies unchanged.
- DSH formal r7 Review: `approved_with_conditions` (Stage A only), P0/P1/P2/P3=`0/0/0/2`; R6-01..04 closed. Read `verification/P02/implementation-stage-a-r7-dsh-review.stdout.md`, `verification/P02/r7-codex-exact-head-review.md`, and `verification/P02/codex-checkpoint-after-r7-dsh-review.md` before editing.

## Required change: R7-01 only

DSH finding R7-01 (P3) says `self_test_pre03_failure_propagation()` currently proves the aggregation helper's boolean/dictionary but does not leave a durable in-repository regression check for the production PRE-03 `FAIL` verdict, recorded exit code `1`, and the top-level exit result used by `main()`.

Make the smallest change that makes the repository's own self-check assert failure propagation through the production PRE-03 verdict path and the exit decision consumed by `main()`. Prefer reusing the actual caller/helper over copying its boolean expression. If calling the whole `main()` directly would recurse through constructor self-checks or create unrelated artifact writes, extract a narrow production helper used by `main()` and the self-check, and prove the real PRE-03 `record_verdict` status/exit mapping plus that helper's nonzero result. Keep the existing normal PASS path intact.

The Codex fixed-r7 caller injection evidence already demonstrated the current production path returns PRE-03 `FAIL / exit_code=1` and `main()=1`; the requested r8 change is to make this a durable regression guard, not to change the product behavior.

## R7-02 disposition

Do not broaden this correction to runner startup/finalization behavior. DSH explicitly permits R7-02 (an early Step 2/3 failure can leave a previous `FINALIZED` JSON beside the current failed run log) to be deferred. Record it as an explicit deferred P3 in the Task-local Handoff/RESUME or Task review-disposition notes, with the trigger and the reason it remains open. Do not call it fixed or imply that the report is fresh after an early failure.

## Scope and safety

- Make changes only in the frozen Owner allowlist, especially `verification/P02/harness/**` and Task-local `verification/P02/**`, `doc/tasks/P02.md`, and `doc/handoffs/P02-*.md` as already authorized.
- Do not modify acceptance criteria, scope contract, requirements, shared contracts, dependency files, product source, Rust/Tauri source, Python Core, SQLite, or P01 artifacts.
- Keep the Hard Build Barrier active. Do not run Cargo/Tauri/sidecar builds, frontend builds, Vitest, product GUI, or real WebView/CDP/mouse/keyboard actions. Keep AC1–AC6 `BLOCKED`.
- No user manga/library data, locks, current/pinned revisions, credentials or production data. Do not integrate, push, publish, deploy, or shut down the machine.

## Verification and delivery

Run only the focused checks needed for this slice: production PRE-03 failure-propagation self-check; strict focused TypeScript check; direct harness invocation without TS must stay `NOT_RUN`; injected `--tsc-exit 1` must fail the gate; normal `-ProbeOnly` and Full runner; `-ExceptionTest` under Windows PowerShell 5.1; `-FinalizeFailTest`; final artifact hashes; `git diff --check`. Preserve each command, environment, output, exit code and skip reason. The final successful Full run must restore PRE-01..03 PASS, AC1–AC6 BLOCKED, and finalized evidence hashes.

Commit the R8 correction as a child of r7 on the existing Owner branch. Report exact HEAD/tree/parent, clean Owner worktree, path allowlist, R7-01 closure proof, R7-02 deferred disposition, and all tests with exits. Do not merge or alter `main`; Codex will perform a detached exact-head replay followed by formal DSH re-review.
