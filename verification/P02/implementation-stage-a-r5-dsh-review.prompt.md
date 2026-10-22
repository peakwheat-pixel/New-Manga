# P02 Stage A r5 formal DSH review (read-only)

Continue the existing formal DSH review session `session-9ab84346-f806-42f3-9f90-30245d488e65` in the same Owner worktree/profile. Review only the fixed r5 commit below. Do not modify files or attempt to integrate anything.

## Fixed target

- Task: `doc/tasks/P02.md` (P02 remains `in_progress / ACTIVE`; `integration_commit: null`)
- Repository/common dir: `G:/CODEX/New Manga` / `G:/CODEX/New Manga/.git`
- Owner worktree: `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity`
- Branch: `agent/antigravity/P02-real-webview-harness`
- Base: `5de8d44c784cbd20b23bcd41a8f1a7258c7addff`
- Parent r4: `cc1bd7505f3fc48079db7ea2719040e77a8c58dd`
- Reviewed r5 HEAD: `172eee84240e101186b12f1aa09e8a2f9ec92d68`
- Expected tree: `a5b1af3e0708463df6865c8e49c9679e57e3fa85`
- Frozen owner scope SHA-256: `27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425`

## Evidence to read

- Previous formal review: `verification/P02/implementation-stage-a-r4-dsh-review.md` (`changes_requested`, P0/P1/P2/P3=`0/0/3/8`, R4-01..R4-11).
- Codex's r4 corroboration: `verification/P02/r4-codex-independent-review.md`.
- Owner's r5 handoff, Task, recovery: `doc/handoffs/P02-stage-a-foundation-handoff.md`, `doc/tasks/P02.md`, `verification/P02/RESUME.md`.
- Owner response captured by Codex: `G:/CODEX/New Manga/verification/P02/antigravity-owner-stage-a-corrections-r5.response.md`.
- Codex exact-head replay and scope evidence: `G:/CODEX/New Manga/verification/P02/r5-codex-exact-head-review.md`; exact stdout/stderr/exit artifacts use `r5-codex-exact-*` prefixes.
- Codex failure-path observation for R4-06/R4-10: `G:/CODEX/New Manga/verification/P02/r5-codex-failure-path.stdout.log`, `.stderr.log`, `.exit`; the isolated worktree is `G:/CODEX/New Manga.worktrees/P02-stage-a-validation-172eee84-failureprobe`.

## Review requirements

Independently review the exact r4..r5 diff and all R4-01..R4-11 dispositions. Verify that fixes work in the code path and that Handoff/Task/RESUME claims match the committed source and evidence. Check changed paths against the frozen allowlist; do not accept Owner claims as proof by themselves. The Codex exact replay is Codex evidence, not DSH execution. If your shell/runtime is blocked, say so and distinguish static review from Codex-executed checks.

Give special scrutiny to these concrete questions, then report your own conclusions:

1. Does a missing focused `tsc` binary make the runner warn and pass without performing R4-01's required check?
2. Can the PRE-02 caller pass based on an old `overall_status=PASS`/`exit_code=0` after input freshness fails and a retry errors before replacing the old report? Does it require `report_is_fresh` as part of the PASS predicate?
3. In a thrown PowerShell native-process error, does the runner record the complete failed output and an observed child exit code, or only an exception summary / possibly stale `$LASTEXITCODE`? Does the recorded R4-06 microprobe exist and prove the claim?
4. If `--finalize` returns nonzero (without throwing), does the finalized execution log accurately capture failure rather than already stating successful completion?
5. Do all five artifact hashes bind bytes after finalization, and is report/TXT self-reference avoided? Codex independently recomputed the five values on the fixed r5 Full detached run; compare those values to the code and committed claims.
6. Verify the enum closed sets, fail-closed parser, all four actual mutation tests/counters, `large_text` threshold, nullable page_count and geometry structure.

## Output

Return a complete formal Chinese Review, not just a progress summary. Include `decision` (`approved`, `approved_with_conditions`, `changes_requested`, or `blocked`), P0/P1/P2/P3 counts and open count; list each finding with ID, severity, exact path/line, trigger, impact, and smallest correction; give explicit closure/deferment status for every R4-01..R4-11; assess architecture/scope and AC status; distinguish checks you actually ran from Codex evidence and all NOT_RUN items. Do not claim P02 complete: AC1–AC6 stay BLOCKED, the hard build barrier remains active, and `integration_commit` stays null.
