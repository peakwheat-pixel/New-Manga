# Integration record — DIAG-M2-REGIONLESS-LOCK-CHANGED-001

- **Merge:** `b5ac097f98d9c06e2548c69d7361d475c0f13388` (parents `1103f3d1` + Owner delivery `7a03ac5f9677c359c6e13c007d77d46e604e8df0`); strategy `ort`, no conflicts, 8 files added, 0 modified/deleted.
- **Fixed base:** `5789b30b37dfbf79d9bca707b5fdaaa562ada707`; Owner branch `agent/deepseek/DIAG-M2-REGIONLESS-LOCK-CHANGED-001` preserved at `7a03ac5f`; worktree `G:/CODEX/New Manga.worktrees/DIAG-M2-REGIONLESS-LOCK-CHANGED-001-dsh` preserved.
- **Integrator:** Codex role executed by ZCode session acting as Codex (user full authorization 2026-09-28).

## Delivery chain (proxy-execution pattern, per the M2-C2 precedent)

1. **Owner (DeepSeek Harness) delivered as text.** The DSH headless sandbox has no shell (`SetNamedSecurityInfoW failed (Win32 5): grantWrite`, byte-identical across 4 direct + 2 subagent probes, recorded in `dsh-dispatch/diag-err.log`) and cannot write outside its session workspace, so the full static diagnosis, `reproduce.py` and Handoff arrived inside the DSH answer; the integrator imported them byte-for-byte in the single Owner-branch commit `7a03ac5f` and executed the verification commands on the Owner's behalf:
   - `reproduce.py` → `DEFECT_REPRODUCED`, 8/8 checks PASS, `EXIT=0` (first-red evidence; `reproduce-run-01.log`);
   - `pytest tests/providers/test_detect_handler.py tests/providers/test_bootstrap_providers.py -q` → 9 passed, `EXIT=0`;
   - `git diff --check 5789b30b..7a03ac5f` → `EXIT=0` (after stripping trailing whitespace from the DSH reasoning archive; chore inside the same commit).
2. **Independent non-author Review (Antigravity):** [approved](../../../doc/reviews/DIAG-M2-REGIONLESS-LOCK-CHANGED-001-7a03ac5f.md), `conversation_id bdf7cf60-f078-4ece-bca7-299e18fa1bb6`. All four axes `executed`; AC1–AC5 all PASS; 0×P0/P1/P2, 2×P3 observations (stale `Delivery head: NONE` wording inside the imported Handoff — superseded by this record; `unit_id` naming debt). Reviewer independently re-ran `reproduce.py` (8/8 PASS, EXIT 0), the pytest pair (9 passed), `diff --check` (EXIT 0) and spot-checked 5 `path:line` citations against base `5789b30b` — 100% match. Dispatch record: `review-agy-import/`.

## Post-integration replay (this merge head)

- `reproduce.py` → `DEFECT_REPRODUCED`, 8/8 PASS, `EXIT=0`
- pytest pair → 9 passed, `EXIT=0`
- Transcript: [replay.log](replay.log)

## Scope audit

- Owner delta `base..7a03ac5f`: 8 paths, all inside the Task's allowed scope (`doc/research/**`, `doc/handoffs/**`, `verification/DIAG-M2-REGIONLESS-LOCK-CHANGED-001/**`); zero `src/**`, `tests/**`, `doc/contracts/**` changes; product code untouched.
- Full-range `git diff --check 5789b30b..HEAD`: the only remaining report is `verification/M2-I2/review-a4705a9/full-suite.log:1302 "leftover conflict marker"` — a false positive: the line is pytest's summary separator `======= 1 failed, 1248 passed, 6 skipped ... =======` inside a historical (2026-09-25, commit `be36490f`) evidence file imported verbatim by the ratification batch; preserved byte-for-byte, disclosed here. Six genuine EOF-blank-line defects in the same imported batch were fixed in `d782d66f`.

## Diagnosis result (for the successor fix Task)

Root cause: `_backfill_detected_regions` (`src/application/tasks/service.py:921-946`) rebinds only `PlanUnit.region_id`, not `target_id`; the `ocr` `StepRun.input_refs` therefore snapshot the **Page** target (no `"region"` key → `None`) while the handler writes the **Region**, and `RegionStepWriter._persist` (`src/infrastructure/providers/step_writes.py:219-231`) compares `None` against the Region's real current revision → `LockBlocked` (`error_code="LOCK_CHANGED"`). Full chain, counterfactuals (multi-Region fan-out, terminal counting, restart self-healing masking the defect), minimal fix scope (`service.py:_backfill_detected_regions` alone; rebind `target_id` **and** `region_id`; never touch `unit_id`), regression matrix R0–R5, negative matrix N1–N7 and persistence risks R-a–R-c: [diagnosis report](../../../doc/research/DIAG-M2-REGIONLESS-LOCK-CHANGED-001.md).

**No fix is authorized by this Task.** The successor fix Task (M2-P1 candidate) must be separately registered and released.
