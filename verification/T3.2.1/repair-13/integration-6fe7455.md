# T3.2.1-REPAIR-13 Codex Integration Record

Date: 2026-09-25 (Asia/Shanghai)

## Fixed points and integration method

- Product delivery: `aed009405fd523c52fa45e604afe40f01cef3d45`.
- Reviewed evidence/Handoff head: `13ae23f65e963cf1d5aea19634572627e5e709db` (parent `66a13f8a5a56be63f72ceca47406262ed9cfaa9a`).
- Independent Review report: `ccd26a4b4ef19a33ad91841602535614705213bd`, `APPROVE_WITH_CONDITIONS`; C1 was registered earlier and C2 was satisfied by the evidence-only follow-up.
- Pre-integration `master`: `1950ba54e426e377c92d0f866afa888e28ad27c7`.
- Codex integrated the exact fixed task delta `8738c41..13ae23f` as commit `6fe7455d0927ae0b4328b77f117893d373797d92`.

The author branch was not merged wholesale. Its common ancestor with current `master` predates the REPAIR-9 through REPAIR-12 candidate chain; a whole-branch merge would bring unrelated candidate history. The fixed REPAIR-13 delta applied cleanly (`git apply --check` exit 0), and only its 62 changed paths were staged. This integrates the reviewed task scope while leaving the author branch and all other worktrees intact.

## Scope and post-integration checks

- Staged scope: 62 paths: 7 authorized QML files, 2 authorized UI regression test files, 3 REPAIR-13 Handoffs, and 50 files under `verification/T3.2.1/repair-13/`.
- No changes to Python business logic, `packaging/**`, dependencies, SQLite schema, the parent T3.2.1 Task/Gate evidence, or historical Task/Review records.
- `git diff --cached --check`: exit 0 before integration.
- Post-integration command: `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/ui_shell tests/reading_export/test_qml_contract.py -q -p no:cacheprovider -rs`.
- Result: `162 passed in 7.16s`, exit 0.
- Fixed delivery-to-evidence code scope: `git diff aed0094 13ae23f -- src tests packaging` is empty.
- Full fixed-base whitespace check: `git diff --check 8738c41 13ae23f` is exit 0.

## C2 evidence verification and count discrepancy

- Screenshot path is a 100% Git rename from `.png` to `.jpg`; the old and new blob object IDs are both `a156cb5b7886bed673b46dcd5c85247a6fcb7199`.
- The screenshot reference changed in exactly two tracked locations: the final Handoff and `local-verification.md`.
- The three RED logs differ only by removal of trailing spaces/tabs; after trimming line endings, their line content and order are byte-equivalent. The resulting files have no trailing whitespace.
- Re-running `git diff --check 8738c41 66a13f8` produced exit 2 and 13 diagnostics: `discriminating-pre-repair.log` 5, `f13-2-pre-repair-red.log` 3, `f13-4-pre-repair-red.log` 5. The C2 supplement says 12 and labels the third log as 6 lines; those figures do not match the recorded command output. The cleanup itself removed all 13 reported sites, and the post-C2 full diff check is clean. This is recorded as a count-only documentation discrepancy; no author evidence or Review report was rewritten.

## Untracked review artifacts

The ZCode worktree still has three untracked files and they were not cleaned:

- `dsh-review-prompt-4.txt` and `dsh-review-run-4.log` remain preserved in the author worktree as manual dispatch/session artifacts; they are not part of the fixed C2 delivery.
- Its untracked `review-report-dsh.md` is byte-identical (SHA-256 `A78ED961D4D86E9D3AAC5BE8E870733BBD18C64C9A0EC933C40C5A59EC56FEF8`) to the canonical Review report already registered at `ccd26a4`; the duplicate was not added again.

No untracked files were deleted or modified.

## Parent Gate and successor state

This child integration does not change the parent T3.2.1 Full Release Gate: it remains `OPEN`; parent AC3 remains `BLOCKED`; the other parent criteria retain their existing `NOT_RUN` / `PARTIAL` / `OPEN` states. REPAIR-14 for F-13-3 remains `proposed / NOT_RELEASED`; no implementation was started or worktree created.
