# M2-P1 Verification Evidence (Implementation & Tests @ 78e9637f)

- **Date:** 2026-09-28
- **Owner:** Antigravity
- **Worktree:** `G:/CODEX/New Manga.worktrees/M2-P1-agy`
- **Branch:** `agent/antigravity/M2-P1-regionless-region-rebinding`
- **Fixed Base:** `338266417437e3007345aaa8496c5e936745dfd6`
- **Implementation Head:** `78e9637fab8aa456b03f15bc1c632e6966b21a22`
- **Python Interpreter:** `G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe` (Python 3.12.3)
- **Shell:** PowerShell (pwsh)

---

## 1. pytest Verification (Tests Suite)

**Command:**
```powershell
& "G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe" -m pytest tests/pipeline/test_regionless_rebinding.py tests/providers/test_detect_handler.py tests/providers/test_bootstrap_providers.py -q
```

**Exit Code:** `0`

**Output:**
```text
.....................                                                    [100%]
21 passed in 1.03s
```

**Test Breakdown (21 total, 21 passed, 0 skipped, 0 failed):**
- `tests/pipeline/test_regionless_rebinding.py` (12 tests):
  - `test_r0_regionless_page_reocr_all_completed` (R0): PASSED
  - `test_r1_backfill_rebinds_target_id_and_preserves_unit_ids` (R1): PASSED
  - `test_r2_multiple_regions_only_primary_reocr_completed` (R2): PASSED
  - `test_r3_translate_all_stops_at_capability_gap_not_lock_changed` (R3): PASSED
  - `test_r5_subsequent_run_on_same_page_avoids_duplicate_regions` (R5): PASSED
  - `test_n1_tampered_input_refs_triggers_lock_changed_and_zero_write` (N1): PASSED
  - `test_n2_region_locked_between_detect_and_ocr` (N2): PASSED
  - `test_n3_detector_zero_candidates_fails_with_invalid_input` (N3): PASSED
  - `test_n4_no_ocr_provider_fails_with_provider_not_configured` (N4): PASSED
  - `test_n5_page_locked_skips_execution` (N5): PASSED
  - `test_n6_primary_soft_deleted_before_ocr` (N6): PASSED
  - `test_n7_detect_committed_then_interrupted_then_plan_continue` (N7): PASSED
- `tests/providers/test_detect_handler.py` (5 tests):
  - `test_page_level_plan_grows_a_leading_detect_unit`: PASSED
  - `test_detect_fails_typed_without_a_detector`: PASSED
  - `test_detect_lands_candidates_as_regions_and_ocr_advances`: PASSED
  - `test_detect_reuses_existing_live_regions`: PASSED
  - `test_detect_fails_typed_when_no_candidates`: PASSED
- `tests/providers/test_bootstrap_providers.py` (4 tests):
  - `test_production_stack_starts_without_heavy_runtimes`: PASSED
  - `test_run_with_unconfigured_provider_fails_closed`: PASSED
  - `test_ocr_handler_uses_the_managed_original_and_writes_one_region`: PASSED
  - `test_render_stack_and_full_chain_handlers_assemble`: PASSED

---

## 2. Reproduce Script (Defect Elimination Strong Discriminator)

**Command:**
```powershell
& "G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe" verification/DIAG-M2-REGIONLESS-LOCK-CHANGED-001/reproduce.py
```

**Exit Code:** `1` (Expected: defect NOT reproduced = fix verified)

**Output Summary:**
```text
===== AC2-C PlanUnit AFTER detect/backfill =====
target_id: <primary_region_id>
region_id: <primary_region_id>

===== AC2-G StepRun chain (input_refs / lock_snapshot / error) =====
detect: status=completed, error_code=null
ocr: status=completed, error_code=null, input_refs={'region': '<first_revision_id>'}

===== AC2-H final =====
run_status: completed, task_status: completed, planned=2, terminal=2

===== AC2-I region revisions =====
primary: 2, secondary: 1

===== AC1 VERDICT =====
  [PASS] detect step ran and committed  -- detect=completed
  [MISS] ocr step is FAILED with LOCK_CHANGED  -- ocr=None
  [MISS] failure is the writer guard on a None expectation  -- detail=None
  [MISS] smoking gun: ocr target_id still the Page, region_id set  -- target_id=<primary> region_id=<primary>
  [MISS] ocr input_refs carries no 'region' key  -- input_refs={'region': '<first_rev>'}
  [MISS] run ends COMPLETED_WITH_FAILURES  -- status=completed
  [MISS] no Region write happened (1 revision = detect first revision)  -- region_ids=[...]
  [PASS] counterfactual: the Region DOES have a current revision  -- region current_revision_id non-empty

VERDICT: NOT_REPRODUCED
```

---

## 3. Scope & Whitespace Check

**Command:**
```powershell
git diff --check 338266417437e3007345aaa8496c5e936745dfd6..HEAD
```

**Exit Code:** `0` (clean, zero whitespace/trailing errors)
