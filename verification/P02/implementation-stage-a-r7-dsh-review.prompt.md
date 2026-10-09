# Formal DSH Review: P02 Stage A r7

Continue the existing formal DSH review session `session-9ab84346-f806-42f3-9f90-30245d488e65` from its registered Owner worktree and profile. Review the fixed r7 commit only. This is an independent, read-only review; do not edit files, commit, integrate, or change task scope.

## Fixed review target

- Repository/common Git directory: `G:/CODEX/New Manga` / `G:/CODEX/New Manga/.git`
- Owner worktree and branch (the required DSH session cwd): `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity` / `agent/antigravity/P02-real-webview-harness`
- Exact reviewed HEAD/tree/parent: `38959ba99b84f771aba7010b53b9b47ecdc75488` / `5bf0c81a0ee814f857ad4c1f0b3f598f963fa1c5` / `38672473f93971a4681aef682e5635e64b0bd896`
- Diff base: `5de8d44c784cbd20b23bcd41a8f1a7258c7addff`
- Frozen scope SHA-256: `27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425`
- P02 remains `in_progress / ACTIVE`, `integration_commit: null`; no P01 work and no P02 refreeze are authorized or requested.

First independently confirm `git rev-parse HEAD`, tree, parent and clean Owner worktree match these values. Read the full `base..HEAD` diff and the current `doc/tasks/P02.md`, `doc/REBASELINE_PLAN.md`, `doc/STATUS.md`, `doc/09_COLLABORATION.md`, the prior r6 DSH report, the r7 Handoff/RESUME, and affected production caller/helper code. Treat the exact commit as the review boundary; do not infer approval from owner or Codex summaries.

## Prior formal review and requested dispositions

Read `verification/P02/implementation-stage-a-r6-dsh-review.md` and verify each R6 condition at this exact head:

1. R6-01: PowerShell TypeScript resolver must anchor Git common-dir lookup at `$RepoRoot`, not caller CWD.
2. R6-02: TypeScript binary resolution and actual check execution must be distinct machine states; absent execution must not report PASS; observed failing exit must fail the gate and top-level runner.
3. R6-03: PRE-02/PRE-03 checks must use production paths and prove failure propagation, not only duplicate an expression.
4. R6-04: PowerShell 5.1 exception Scenario C must either be actually executed and logged with a FAILED run, or labeled static-only/NOT_RUN.

A separate Codex read-only reviewer identified one residual P3: the PRE-03 in-code self-check calls the production aggregation helper but does not itself call `run_preflight_checks()` and assert the recorded verdict/status/exit, nor the `main()` exit. The exact r7 source appears to have the correct production propagation path; determine whether the following independent fixed-head dynamic evidence closes R6-03, or whether r8 source changes are still required:

- `verification/P02/r7-codex-exact-head-review.md`
- `verification/P02/r7-codex-pre03-production-failure-propagation.output.log`
- `verification/P02/r7-codex-pre03-production-failure-propagation.exit`
- `verification/P02/r7-codex-pre03-production-failure-propagation-results.json`

The Codex probe injected a low contrast result while invoking the actual production `run_preflight_checks()` and `main()`. Its recorded result is PRE-03 `FAIL`, PRE-03 exit `1`, main/process exit `1`. Do not treat the Codex execution as a replacement for your code review; independently inspect whether it reaches the actual production caller and whether the remaining maintainability/regression gap merits a finding.

## Codex exact-head evidence

Read `verification/P02/r7-codex-exact-head-review.md` and supporting evidence:

- `verification/P02/r7-codex-commit-scope.json`
- `verification/P02/r7-codex-artifact-hash-check.json`
- `verification/P02/r7-codex-tsc-exact.stdout.log` and `.exit`
- `verification/P02/r7-codex-direct-harness-not-run-results.json`
- `verification/P02/r7-codex-tsc-fail-gate-results.json` and `.exit`
- `verification/P02/r7-codex-external-cwd-probeonly-run.log` and `.exit`
- `verification/P02/r7-codex-full-run.log`, `.exit`, and `r7-codex-full-run-results.json`
- `verification/P02/r7-codex-exception-test-run.log` and `.exit`
- `verification/P02/r7-codex-finalize-fail-test-run.log` and `.exit`

Codex reports fixed-head exact replay: scope 19/19 within allowlist; `git diff --check` EXIT 0; focused strict TypeScript check EXIT 0; external-CWD ProbeOnly EXIT 0; direct harness records TS `NOT_RUN`; injected TS exit 1 records gate `FAIL`; PRE-03 injected low-contrast caller-flow exits 1; normal full runner EXIT 0 with PRE-01..03 PASS and AC1..AC6 BLOCKED; PowerShell 5.1 exception test EXIT 1 with exception/stack/child-exit details; finalizer failure test EXIT 42; artifact hashes 5/5. Verify these are supplementary Codex evidence and distinguish them from anything DSH itself could execute.

## Review rules and output

- Inspect code and docs at the exact fixed HEAD. Do not modify files or execute build/GUI/WebView commands.
- No Cargo/Tauri/sidecar build, frontend build, Vitest, product GUI, or real WebView/CDP/keyboard/mouse operation. Hard Build Barrier remains active and AC1..AC6 must remain BLOCKED; this Stage A review cannot imply product AC completion.
- Return a complete Chinese review with: fixed HEAD/tree confirmation if observable; decision (`approved`, `approved_with_conditions`, or `changes_requested`); P0/P1/P2/P3 counts and open count; each finding's ID/severity/path/line/trigger/impact/evidence/recommendation; explicit R6-01..04 disposition; explicit verdict on whether Codex's caller-level PRE-03 evidence closes the remaining concern; and what exact correction/re-review is needed if not.
- If DSH's shell cannot inspect Git or execute commands, state that as `NOT_RUN`/unverified. Do not invent hash, runtime, or build evidence.
