请对 P02 R9 Review 条件闭合候选做非作者、只读、exact-head Review。不得修改文件、切换候选、创建 clone、启动 Windows Sandbox、运行 Smoke、Build 或产品测试。

## 固定审查目标

- author branch/worktree: `codex/P02-process-isolation` / `C:/Users/49745/.codex/worktrees/p02-process-isolation-plan/New Manga`
- exact reviewed HEAD: `92dc7361194f1db8fdf7aff3a15a3d234ae56678`
- exact tree: `73511f7ba03d6b2215f4dad9c5a3c7f442471a6f`
- exact parent/base: `083d2b47f7051c2dedd0d9ae4346ae1affab6c1b`
- project live main at candidate validation: `ceffb7479cb1f79bd3b620afdaf6e9eaa0ae6d50`
- review branch/worktree: `review/deepseek/P02-preflight-r4-condition-closure-92dc7361` / `C:/Users/49745/.codex/worktrees/P02-preflight-r4-condition-closure-92dc7361-review-dsh`
- Owner/author=Codex; non-author Reviewer=DeepSeek Harness; Integrator=Codex.

Review only `083d2b47..92dc7361` (seven committed paths) and necessary cited context. Confirm HEAD/tree/parent, clean reviewer worktree, path count and no product-code/schema/IPC/dependency/User data changes. Candidate paths are:
1. `verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md`
2. `verification/P02/codex-scratch-build-preflight-r2.md`
3. `verification/P02/codex-scratch-build-preflight-observations-r2.json`
4. `verification/P02/codex-checkpoint-p02-preflight-r4-start.md`
5. `verification/P02/codex-preflight-r4-validation.md`
6. `verification/P02/codex-checkpoint-p02-preflight-r4-condition-closure.md`
7. `verification/P02/codex-checkpoint-p02-smoke-admission-r1.md`

## Review questions

The prior exact-head r9 Review (`083d2b47`) returned `APPROVED_WITH_CONDITIONS`, no blocking P0/P1/P2, six P3 findings plus one note. Independently decide whether each finding is now accurately closed:

- C-01: six input records have empty `expected_size_bytes`; do their `size_match` values now use `null`, with the report/summary accurately separating 20 hash checks, 14 registered size checks and 6 unregistered sizes?
- C-02: are the five original r9 candidate paths and seven r10 candidate paths explicitly enumerated, with exact committed path set agreeing?
- C-03: do all 12 `mapping_domain` values match `verification/P02/codex-scratch-build-preflight-hostfolders-r1.tsv`?
- C-04: is the user's renewed authorization traceable to the r7 authorization-basis section and P02 Task checkpoint?
- C-05: does the separate Smoke admission checkpoint explicitly require a non-elevated interactive host shell, a fresh `wsb list --raw` immediately before launch, and binding the started Sandbox UI window/screenshot to that same returned session?
- C-06: is the known temporary mismatch between shared docs' `UNKNOWN / BLOCKED` and the measured r9 `InstallState=1` / `PRESTART_STAGE_1_PASS` documented, with shared updates held until exact-head review passes?

Also check whether any remaining defect blocks documenting a later Smoke admission after a fresh non-elevated preflight. Do not mark Smoke admitted, isolation proven, Build Gate passed, Hard Build Barrier lifted, or any AC passed. The smoke admission checkpoint must remain separate from this documentation review.

Inspect the author-side validation but independently run any safe static checks available to you (e.g. `git diff --check`, route validator, JSON/TSV consistency, local links). Do not claim root 203-entry manifest was independently checked if unavailable; mark it `NOT_RUN` and report whether the author-side evidence is internally consistent. No tests/build/GUI/Sandbox are expected.

## Required final response

Return a formal Simplified Chinese Markdown Review in stdout (not process reasoning). Include exact reviewed HEAD/tree/base, checkout status, findings with severity and exact file/line, dispositions C-01..C-06, checks with exit codes and NOT_RUN items, and explicit separate states for:
1. process-isolation plan/design review,
2. this r10 documentation condition-closure Review,
3. Smoke admission,
4. Build Gate / Hard Build Barrier,
5. product acceptance and AC1–AC7.

Decision must be one of `APPROVED`, `APPROVED_WITH_CONDITIONS`, `CHANGES_REQUESTED`, or `BLOCKED`. Use `APPROVED` only if no unresolved P0/P1/P2/P3 review condition remains for this evidence candidate. If anything remains open, say exactly what needs repair. Do not copy any file contents into the report beyond short necessary excerpts.

