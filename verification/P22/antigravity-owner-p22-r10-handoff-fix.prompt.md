# P22 R10 Owner Handoff metadata correction

You are the existing Antigravity Owner for P22. Continue in the existing Owner conversation and worktree; do not create another worktree.

## Fixed inputs

- Repository/worktree: `G:\CODEX\New Manga.worktrees\P22-roundtrip-serialization-antigravity`
- Branch: `agent/antigravity/P22-roundtrip-serialization`
- Required starting HEAD and parent of your new commit: R9 `791f1c9bb85a43ff38f3e518c831df81450c3148` (tree `1300e72b55fa1ef078925ff991a78ae2aa2a6c23`; parent R8 `a99d092fbf0fe71079f17d6510ad697c547a3fa2`)
- Current P22 Task snapshot: `doc/tasks/P22.md`, SHA-256=`B7A8094B102248B235685747B7BC3A31B972026E78787A1D7FC62161AE31423F`
- DSH R9 report: main-repository `verification/P22/dsh-p22-review-r9.stdout.md`, SHA-256=`29219ADC4FF03E7CA4E9F759EF54AE8A7A44424C5D27C2E5CEFD73BCAF4C6ED1`
- Codex R9 adjudication: main-repository `verification/P22/codex-p22-r9-review-adjudication.md`

## Exact write scope

Modify and commit only this file in the Owner worktree:

`verification/P22/antigravity-owner-p22.handoff.md`

Resolve DSH findings F9-1 and F9-2, and make no unrelated edits:

1. In the YAML frontmatter, change `revision: R8_doc_fix` to `revision: R9_doc_fix`. Update both the frontmatter `title:` value and the matching H1 so they identify this as the Owner R9 document revision while retaining the existing P22 subject and R2 delivery context.
2. Add these R8 predecessor fields to the frontmatter, following the existing R3–R7 field naming pattern:
   - `r8_doc_commit: a99d092fbf0fe71079f17d6510ad697c547a3fa2`
   - `r8_doc_tree: 417ae9572399e584dce8f237ab9622db3a57bc2d`
   - `r8_doc_parent: bcbe8632beea067047630c0bc94e6901ced72eda`
3. In the NOTE under “工作区与证据根路径区分说明（R7-1）”, narrow “下文引用的 R1~R4…” to the main prose in §1–§6, and add one sentence that the Owner-worktree relative paths in the §7 forwardable block resolve against the absolute Owner-worktree root declared in that block. Preserve the R5/R6/R7 main-repository evidence-root statement and all paths.

Do not rewrite the historical R8 body sections or add R9 delivery self-attestation; Codex records the R9/R10 commits and review in the live Task. Do not change source code, tests, Task files, Gate/status declarations, any other file, or existing untracked/user files. Do not delete, stage, revert, clean, stash, or overwrite unrelated files.

## Delivery and acceptance

- Verify the starting HEAD is exactly the R9 commit above. If not, stop without editing and report the actual state.
- Make only the specified Handoff edits, run `git diff --check`, and commit only that file as a child of R9 on the existing branch.
- Leave all pre-existing untracked files untouched and uncommitted. Report commit, tree, parent, changed paths, Handoff SHA-256, `git diff --check` exit, and tracked/untracked worktree status. Do not run tests, Cargo, builds, runtime, Sandbox, or OS/Gate operations.
- Do not review or approve your own change.
