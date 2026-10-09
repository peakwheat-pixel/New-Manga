# P02 Preflight R4 / R9 Scope Candidate Validation

- Validation time: 2026-10-10 02:54:38 +08:00 (Asia/Shanghai).
- Base/live main: ceffb7479cb1f79bd3b620afdaf6e9eaa0ae6d50; author branch/worktree: codex/P02-process-isolation / C:/Users/49745/.codex/worktrees/p02-process-isolation-plan/New Manga.
- Root protected manifest: 203 entries, 203 live, missing/extra/status-kind-size-hash mismatches=0, staged=0; digest=3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2.
- Candidate root-dirty-path intersection=0. The candidate writes only the R9 P02 process-isolation scope/evidence paths in the separate Codex worktree.
- Exact candidate paths: `verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md`; `verification/P02/codex-scratch-build-preflight-r2.md`; `verification/P02/codex-scratch-build-preflight-observations-r2.json`; `verification/P02/codex-checkpoint-p02-preflight-r4-start.md`; `verification/P02/codex-preflight-r4-validation.md`.
- `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`: EXIT=0; 196 audit nodes/classifications/dependencies, 105 integration ancestors, registered P Task states and Plan, 21-node roadmap/DAG, local navigation links, zero P01 product delta all PASS. Product tests/build/GUI=`NOT_RUN (planning-only)`.
- `git diff --check`: EXIT=0.
- Focused Markdown link scan: 3 R9 Markdown files, 6 relative links, 0 missing. The route validator independently checks the current plan/navigation files.
- Scope: no product code/tests, user data, P02 Owner allowlist, AC, IPC/Schema/dependency, Windows feature mutation, elevation, clone, Sandbox, Smoke, or build.
- Current preflight result=`PRESTART_STAGE_1_PASS`; WSB start remains not admitted while independent exact-head review is pending. Clone checkout, recursive HostFolder manifest and all Smoke runtime checks remain NOT_RUN.
- Required independent Reviewer=DeepSeek Harness, not the Codex author. Review decision not yet returned.


## R10 condition-closure candidate validation (2026-10-10 03:08 +08:00)

- Author branch/worktree: `codex/P02-process-isolation` / `C:/Users/49745/.codex/worktrees/p02-process-isolation-plan/New Manga`; base is the reviewed r9 HEAD `083d2b47f7051c2dedd0d9ae4346ae1affab6c1b`. The r10 candidate is validated in the working tree before its fixed commit; its final commit/tree are recorded by Git after freeze.
- Exact candidate path set (7): `verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md`; `verification/P02/codex-scratch-build-preflight-r2.md`; `verification/P02/codex-scratch-build-preflight-observations-r2.json`; `verification/P02/codex-checkpoint-p02-preflight-r4-start.md`; `verification/P02/codex-preflight-r4-validation.md`; `verification/P02/codex-checkpoint-p02-preflight-r4-condition-closure.md`; `verification/P02/codex-checkpoint-p02-smoke-admission-r1.md`.
- Root protection recheck: live root `main@ceffb7479cb1f79bd3b620afdaf6e9eaa0ae6d50`; fixed manifest/live status paths=`203/203`; missing/extra/content/status/kind/size/hash mismatches=`0`; staged=`0`; entries digest=`3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2`; candidate/root-dirty intersection=`0`. Root worktree was read only.
- Pinned-input consistency: 20/20 hashes match, 14/14 registered expected sizes match, 6 unregistered size comparisons are JSON `null`/`NOT_APPLICABLE`; HostFolder mapping domains=`12/12` match the frozen TSV.
- `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`: EXIT=0; 196 unique nodes/classifications/dependencies, 105 integration ancestors, Task/Plan state consistency, 21 planned nodes and dependency DAG, navigation links and governance checks passed. Product tests/build/GUI=`NOT_RUN (planning-only)`.
- Focused changed-candidate Markdown link scan: 6 local links, 0 new missing targets. `git diff --check`: EXIT=0. Final staged exact-path check and staged `git diff --cached --check` must be repeated after adding the validation record and before commit.
- DSH r9 exact-head result: `APPROVED_WITH_CONDITIONS`, P0/P1/P2=`0/0/0`, six P3 record-precision conditions; r10 dispositions are documented in the scope extension and condition checkpoint. Exact-head r10 follow-up Review remains required.
- Scope: documentation/evidence only. Smoke admission=`NOT_ADMITTED`; clone/Sandbox/Smoke=`NOT_RUN`; Build Gate=`BLOCKED`; build=`NOT_AUTHORIZED / NOT_RUN`; AC1–AC7=`BLOCKED / NOT_RUN`; Hard Build Barrier remains effective.
