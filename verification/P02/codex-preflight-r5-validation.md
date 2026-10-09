# P02 Preflight R5 Candidate Validation

- Validation time: 2026-10-10 03:34 +08:00.
- Base/live main=ceffb7479cb1f79bd3b620afdaf6e9eaa0ae6d50; author branch/worktree=codex/P02-process-isolation / C:/Users/49745/.codex/worktrees/p02-process-isolation-plan/New Manga; current HEAD before candidate freeze=92dc7361194f1db8fdf7aff3a15a3d234ae56678.
- Formal R10 Review was exact-head DSH APPROVED; erratum preserves the final decision and corrects metadata/withdraws O-3. R9 C-01..C-06 are closed. R9 authorization permits the current P02 gate-state segments in STATUS, Plan, Index and P02 Task to be refreshed after Review.
- Fresh stage-1 observation is PRESTART_STAGE_1_PASS at 2026-10-10 03:30:19 +08:00. All 16 recorded thresholds are true. Source pin table consistency=20/20; actual input hashes=20/20; registered sizes=14/14; unregistered sizes=6 with null comparisons; HostFolder table consistency=12/12. Detailed machine values and explicit aggregator corrections are in codex-scratch-build-preflight-observations-r3.json (SHA-256=68f60207271da4a419effaf76aa2eaebc7fd5ebee438cf5421220d73afd3e8ca).
- Root protection check: live main@ceffb7479cb1f79bd3b620afdaf6e9eaa0ae6d50; frozen/live entries=203/203; missing/extra/mismatches=0/0/0; staged=0; canonical digest=3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2; candidate/root dirty-path intersection=0. Four tracked root modifications are unrelated to the candidate; current P02 status docs are clean in root.
- Route validator command: python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py; EXIT=0. It validated 196 roadmap nodes, 105 integration ancestors, registered task/plan state, the 21-node DAG and local navigation links. Product tests/build/GUI remain NOT_RUN.
- Pre-stage git diff --check: EXIT=0. Final staged diff-check excluding only the immutable dispatched R10 prompt: EXIT=0. The unfiltered staged check reports exactly one new blank line at EOF in that prompt; its preserved SHA-256 is d732a51950d2428fb7b95587b90ac2ad0236d0505ab8aeb88e0968653eeb25ed. The R5 start checkpoint EOF was normalized. Focused Markdown scan: 15 files, 27 local links, 0 missing; observations JSON matches the frozen pin and HostFolder TSVs with zero mismatches.
- Exact candidate commit path set (23):
  1. doc/00_INDEX.md
  2. doc/REBASELINE_PLAN.md
  3. doc/STATUS.md
  4. doc/tasks/P02.md
  5. verification/P02/codex-checkpoint-p02-preflight-r4-condition-review-start.md
  6. verification/P02/codex-checkpoint-p02-preflight-r4-condition-review.md
  7. verification/P02/codex-checkpoint-p02-preflight-r5-start.md
  8. verification/P02/codex-preflight-r5-validation.md
  9. verification/P02/codex-scratch-build-preflight-observations-r3.json
  10. verification/P02/codex-scratch-build-preflight-r3.md
  11. verification/P02/dsh-review-p02-preflight-r4-condition-closure-correction.exit.txt
  12. verification/P02/dsh-review-p02-preflight-r4-condition-closure-correction.prompt.md
  13. verification/P02/dsh-review-p02-preflight-r4-condition-closure-correction.response.md
  14. verification/P02/dsh-review-p02-preflight-r4-condition-closure.exit.txt
  15. verification/P02/dsh-review-p02-preflight-r4-condition-closure.mount.txt
  16. verification/P02/dsh-review-p02-preflight-r4-condition-closure.prompt.md
  17. verification/P02/dsh-review-p02-preflight-r4-condition-closure.response.md
  18. verification/P02/dsh-review-p02-preflight-r4-condition-closure.session.json
  19. verification/P02/dsh-review-p02-preflight-r4.exit.txt
  20. verification/P02/dsh-review-p02-preflight-r4.mount.txt
  21. verification/P02/dsh-review-p02-preflight-r4.prompt.md
  22. verification/P02/dsh-review-p02-preflight-r4.response.md
  23. verification/P02/dsh-review-p02-preflight-r4.session.json
- Two process-only files, dsh-review-p02-preflight-r4.stderr.txt and the empty dsh-review-p02-preflight-r4.stdout.md, are excluded. No product code/test, dependency, IPC/Schema, user data or additional task scope is changed.
- Gate remains separate: complete preflight=BLOCKED / INCOMPLETE; Smoke admission=NOT_ADMITTED pending fixed-candidate DSH Review and separate Codex decision; no clone/Sandbox/Smoke; Build Gate=BLOCKED; build=NOT_AUTHORIZED / NOT_RUN; P02 AC1–AC7=BLOCKED / NOT_RUN; Hard Build Barrier effective.
- Next exact action: stage only the 23 paths above, rerun staged exact-path/diff checks and root manifest/path-intersection checks, freeze one commit, then dispatch DeepSeek Harness for non-author exact-head Review. If any review finding or evidence mismatch appears, keep Smoke unadmitted and resolve it before proceeding.