# DSH read-only follow-up Review: P02 current prestart R5 findings

## Assignment

Act as the independent Reviewer for the Codex-owned repair of `P02-PRESTART-R5-01` through `P02-PRESTART-R5-05`. This is a documentation/evidence repair only. Do not modify the worktree, create commits, or run any product or sandbox operation.

## Exact-head and scope rules

At the start, record `git rev-parse HEAD`, `git rev-parse HEAD^{tree}`, `git rev-parse HEAD^`, `git status --porcelain=v1`, and the current branch. Review the exact detached HEAD you receive; bind the report to its full HEAD/tree and the full review base `4183e7f7cf366c27aa8ad8a0bc7300af48783470`. The preceding R5 Review was bound to `68bafd3741f376bfab297b8ced911191e96bd424` / tree `e4f6d50ed5f7de2404743feeb6d51c90ae6e5994`; it returned `CHANGES_REQUESTED` with P0/P1/P2/P3=`0/0/1/4`, open=5.

Allowed changed paths from the full review base are only `doc/00_INDEX.md`, `doc/REBASELINE_PLAN.md`, `doc/STATUS.md`, `doc/tasks/P02.md`, and `verification/P02/**`. Any other changed path blocks approval. Keep the worktree read-only. Do not inspect raw DSH JSONL or stderr artifacts.

## Required review

Read the full base-to-HEAD diff and surrounding current Task/Plan/Status/checkpoint context. Independently verify that:

1. R5-01: `doc/STATUS.md` clearly labels the R4 paragraph as historical and has no competing R4 current recovery pointer; current pointers in Index/Plan/Status agree.
2. R5-02: D13 route/diff/scope logs are committed and correctly bound to `68bafd3741f376bfab297b8ced911191e96bd424` / `e4f6d50ed5f7de2404743feeb6d51c90ae6e5994`. Newer package validation must be bound to its recorded HEAD. Do not describe the old D13 logs as checks on the new review HEAD.
3. R5-03: the SHA/EOL errata explicitly names both R2 and R3 raw-worktree hash assertion logs and distinguishes raw worktree hashes from committed Git blob hashes.
4. R5-04: Index records `hook/cache=BLOCKED / NOT_VERIFIED` without changing the gate.
5. R5-05: R4 session metadata identifies Git blob bytes, UTF-8 LF, and the actual source commit `3f243b1993dc577ea98aa8130c1a822ac57763a4`.
6. R2/R3/R4/R5 response hashes match committed Git blob bytes and their session metadata; R5 decision/counts/session/exit/mount/report agree.
7. R6 and R7 exit=1 records remain unchanged and are not represented as PASS. Build Gate remains `BLOCKED`; build is `NOT_AUTHORIZED / NOT_RUN`; hook/cache is `BLOCKED / NOT_VERIFIED`; AC1–AC7 are `BLOCKED / NOT_RUN`; Hard Build Barrier is `EFFECTIVE`; `wsb start=NOT_RUN` and Smoke=`NOT_RUN`.
8. Current checkpoint pointers resolve and route state is consistent; review only evidence in the allowed scope.

## Required independent commands

Run each command and report its exact exit and concise output summary:

- `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`
- `python -B -X utf8 verification/P02/verify_current_prestart_r5_repair.py`
- `git diff 4183e7f7cf366c27aa8ad8a0bc7300af48783470 HEAD --check`
- `git diff HEAD^ HEAD --check`
- `git diff --name-only 4183e7f7cf366c27aa8ad8a0bc7300af48783470 HEAD`

The verification script performs the full path-scope, status, pointer, finding-disposition, historical R6/R7, and committed response-hash assertions. Independently inspect the script and its outputs. If a command cannot run, mark it `NOT_RUN` or `BLOCKED`, never PASS.

## Findings and result

Explicitly disposition R5-01..05 as closed or open with evidence. Report any new findings with severity, file/line, impact, and minimal fix. Approval requires zero unresolved P0/P1/P2 and no missing required verification; P3 findings must have explicit disposition. State all unrun product checks as `NOT_RUN`. Do not claim Sandbox start, HostFolder scan/hash/list, Build, GUI, or product tests occurred.

Return a Markdown Review report, command exits, finding counts, and exact reviewed HEAD/tree. Do not change files.
