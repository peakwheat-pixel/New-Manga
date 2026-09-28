# shell: Git Bash (Owner=ZCode session)
# interpreter: TASK-012-py312 python.exe (Python 3.12.3)
# workspace tip (delivery head): 8db6d150225d59719abd94179ba76d6f9bbb0f32
# note: tip = rework 8d72f91f (code) + evidence/handoff/C3 amends; see HEAD ledger in the Handoff
# branch: agent/zcode/M2-AC2-data-integrity
2026-09-28T21:29:51+08:00

== cmd 1: pytest tests/m2_acceptance/test_data_integrity.py -v ==
============================= test session starts =============================
platform win32 -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0 -- G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe
cachedir: .pytest_cache
rootdir: G:\CODEX\New Manga.worktrees\M2-AC2-zcode
configfile: pytest.ini
collecting ... collected 11 items

tests/m2_acceptance/test_data_integrity.py::test_ac1_source_hash_matches_and_source_file_untouched PASSED [  9%]
tests/m2_acceptance/test_data_integrity.py::test_ac1_duplicate_import_is_skipped_without_second_copy PASSED [ 18%]
tests/m2_acceptance/test_data_integrity.py::test_ac2_managed_copy_is_authoritative_byte_for_byte PASSED [ 27%]
tests/m2_acceptance/test_data_integrity.py::test_ac2_missing_managed_file_is_detectable_not_silent PASSED [ 36%]
tests/m2_acceptance/test_data_integrity.py::test_ac3_manual_translation_survives_pipeline_on_locked_region PASSED [ 45%]
tests/m2_acceptance/test_data_integrity.py::test_ac4_page_lock_yields_skip_lock PASSED [ 54%]
tests/m2_acceptance/test_data_integrity.py::test_ac4_region_lock_zero_write PASSED [ 63%]
tests/m2_acceptance/test_data_integrity.py::test_ac4_pinned_revision_survives_cleanup PASSED [ 72%]
tests/m2_acceptance/test_data_integrity.py::test_ac4_restore_revision_moves_current PASSED [ 81%]
tests/m2_acceptance/test_data_integrity.py::test_ac5_reassembly_preserves_every_integrity_promise PASSED [ 90%]
tests/m2_acceptance/test_data_integrity.py::test_ac5_running_run_is_reaped_as_interrupted_on_reassembly PASSED [100%]

============================= 11 passed in 0.77s ==============================
EXIT(cmd1)=0

== cmd 2: pytest tests/m2_acceptance -q ==
...............                                                          [100%]
15 passed in 2.93s
EXIT(cmd2)=0

== cmd 3: git diff --check 61f9db9b..8db6d150225d59719abd94179ba76d6f9bbb0f32 ==
EXIT(cmd3)=0
