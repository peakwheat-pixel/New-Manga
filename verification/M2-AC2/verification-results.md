# shell: Git Bash (Owner=ZCode session)
# interpreter: TASK-012-py312 python.exe (Python 3.12.3)
# worktree HEAD: 01af773257c9b77e60e3519ccbc76cd534772ed4
# branch: agent/zcode/M2-AC2-data-integrity
2026-09-28T21:02:19+08:00

== pytest tests/m2_acceptance/test_data_integrity.py ==
============================= test session starts =============================
platform win32 -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0 -- G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe
cachedir: .pytest_cache
rootdir: G:\CODEX\New Manga.worktrees\M2-AC2-zcode
configfile: pytest.ini
collecting ... collected 10 items

tests/m2_acceptance/test_data_integrity.py::test_ac1_source_hash_matches_and_source_file_untouched PASSED [ 10%]
tests/m2_acceptance/test_data_integrity.py::test_ac1_duplicate_import_is_skipped_without_second_copy PASSED [ 20%]
tests/m2_acceptance/test_data_integrity.py::test_ac2_managed_copy_is_authoritative_byte_for_byte PASSED [ 30%]
tests/m2_acceptance/test_data_integrity.py::test_ac2_missing_managed_file_is_detectable_not_silent PASSED [ 40%]
tests/m2_acceptance/test_data_integrity.py::test_ac3_manual_translation_survives_pipeline_on_locked_region PASSED [ 50%]
tests/m2_acceptance/test_data_integrity.py::test_ac4_page_lock_yields_skip_lock PASSED [ 60%]
tests/m2_acceptance/test_data_integrity.py::test_ac4_region_lock_zero_write PASSED [ 70%]
tests/m2_acceptance/test_data_integrity.py::test_ac4_pinned_revision_survives_cleanup PASSED [ 80%]
tests/m2_acceptance/test_data_integrity.py::test_ac4_restore_revision_moves_current PASSED [ 90%]
tests/m2_acceptance/test_data_integrity.py::test_ac5_reassembly_preserves_every_integrity_promise PASSED [100%]

============================= 10 passed in 0.72s ==============================

== pytest tests/m2_acceptance (full suite regression) ==
..............                                                           [100%]
14 passed in 3.10s
