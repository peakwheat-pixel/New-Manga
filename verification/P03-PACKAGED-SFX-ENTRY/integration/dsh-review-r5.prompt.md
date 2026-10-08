# P03 DSH Formal Review R5 — fixed candidate

## Review target

- Task: `P03` — Packaged 第五 SFX 入口验收补齐
- Task base commit: `31abde9bf4b73aea2851931dcd48faa0f750b318`
- Exact reviewed head: `7677e9c324da2fde618e7cd6fdba2363abeb1f1b`
- Branch: `codex/P03-integration-4c04459`
- Worktree / project root: `G:/CODEX/New Manga.worktrees/P03-review-prep-85482c5b`
- Owner: Antigravity; this is an independent non-author review. Codex is the integrator.

Review the exact `base..head` diff and the referenced current Task, source code, tests, logs, manifests, raw output archive, prior Reviews, Handoffs, Plan and Status. Do not modify any file. Verify the present fixed head and changed-path scope; do not infer a newer head from a branch name or conversation.

## Purpose

R4 (`session-d27e8ea9-f983-4c1c-9258-a76cdaba0ac0`) approved `d717c049a41544a6d592943a0b0fe1b76a41a050` with 0 unresolved P0/P1, and recorded R4-01..07. Codex then recorded dispositions in the current candidate. This Review must independently verify each disposition, AC1–AC5, integration state, exact evidence binding, allowed paths, user-data protections and any new findings. The Task must remain `in_review` until Codex finishes integration and closure.

## R4 / Codex findings to verify

- R4-01: both current P03 RESUME files link to `doc/handoffs/P03-PACKAGED-SFX-ENTRY-140a6686-r3.md` using valid relative links.
- R4-02: Task frontmatter and current pointers record `integration_commit=d717c049...`, and accurately explain main's pre-R4 fast-forward from `423ea5f1` to `d717c049`; do not mistake that historical ordering for a Review of this candidate.
- R4-03: exact `d717c049` scope/diff trace 21 and normalization trace 22 are versioned and internally consistent.
- R4-04: log 23 records `check_snapshots.py` at source `d717c049`, 16 actual-predicate cases PASS, EXIT=0.
- R4-05: the Task distinguishes runner-observed installer SHA from the expected SHA recorded externally in Task/manifest and cross-checked with Gate output.
- R4-06: AC4 distinguishes four lab source fixtures from four unchanged host `%APPDATA%` files; no claim is made that the Gate accessed or verified a user's manga source folder.
- R4-07: the redundant test-description condition remains a documented, non-blocking cosmetic deferral; verify it has no behavioral consequence and does not undermine an AC.
- Codex C-004/C-005: old logs 19/20 remain unchanged; replacement logs 24/25 include PowerShell type/version, venv state, interpreter path/version, command and EXIT; both RESUME next instructions use live Git/current candidate, not stale `423ea5f1`.

## Verification/evidence bindings

- Installer SHA=`2de124f387bfaf1d0d01b1b0279ad319cd453850d223efa9620b0103ce88a814`, size 579,537,342 bytes. Runner build source is `a3aaf22979f2b432a46dbb51cd9702f35a60d7f4`.
- Logs 23–25 bind snapshot 16/16, targeted tests 40 passed / 0 skipped, and the same-installer packaged Gate 28/28 PASS to source `d717c049...`; every log carries shell/venv/interpreter/EXIT metadata.
- The new Gate output folder is retained locally. `raw-finalhead-d717-gate-output.zip` contains 11 files, has a SHA inventory in the manifest, and Codex verified every archived entry byte-for-byte against the retained folder. Inspect `cleanstart-gate.json` and the S1/S2 artifacts: real K07 probe, missing-page expected failure, install-dir zero writes, host APPDATA 4 files unchanged, four lab fixtures unchanged, five sidecars stopped.
- Logs 26–27 bind base..`051c086879e52058be80a83bd0b01c3ce080b67e`: 144 paths, 0 out of scope, `git diff --check` EXIT=0, both normalization verifiers 6/6 PASS. Current exact head `7677e9c3...` adds only P03 closeout evidence/pointers relative to that checked commit; independently inspect base..current-head scope and whitespace. Current base..head path count was 146, out-of-scope=0; `d717c049..head` touches 24 paths and the runner/test code diff is empty.
- Codex has not changed product code, tests, build inputs, schemas, dependencies or user data since `d717c049`.

## Review requirements

1. Report Architecture and Verification conclusions separately; also cover Standards/Spec if useful under project collaboration rules.
2. Check AC1–AC5 against current P03 Task and actual source/test/evidence, and verify no claim exceeds the evidence.
3. Inspect allowed paths and the full diff, not only the summary above. Note that Codex has already fast-forwarded `d717c049` to main before R4; this is historical. Do not claim this new `7677e9c3...` candidate is integrated unless live Git proves it.
4. Give each finding a severity, file/location, trigger, user/project impact, reproducible basis, minimum disposition, and status. Count unresolved P0/P1/P2/P3/P4.
5. State the exact reviewed base/head and your actual verification commands. If DSH cannot run Git, tests or Gate, mark each `NOT_RUN`; do not repeat prior unsupported claims. Web/Desktop visibility is unverified unless you actually verify it.
6. Return a clear decision (`approved`, `changes_requested`, or `blocked`) for this exact head. Approval does not mark the Task done and does not replace Codex integration closure.

## Protected material

Do not inspect or modify user comic files, databases, locks, current/pinned revisions, K07/ONNX external inputs, root checkout's 24 existing dirty paths, the retained raw Gate folders, or any other Agent's uncommitted files. Qoder is not a project participant.
