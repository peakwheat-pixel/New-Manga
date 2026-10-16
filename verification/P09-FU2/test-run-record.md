# P09-FU2 test run record

- Date: 2026-10-16
- Shell: PowerShell
- Python: `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe` (Python 3.12.3)
- Dependencies: existing task environment; no `pip install` or dependency changes.

| AC | Exact command | Result | Raw log |
|---|---|---|---|
| AC1 / AC5 | `& 'G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe' -m pytest tests/core/test_p09_fu2_import_pages.py::test_stdio_import_pages_runtime_response_and_import_report -vv -s` | pytest exit 0; `1 passed`; Core serve exit 0; response has `error: null` and an imported page | `logs/ac1-importpages-stdio.txt` |
| AC2 | `& 'G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe' -m pytest tests/core/test_p09_fu2_import_pages.py::test_import_source_reference_rejections_have_zero_side_effects -vv -s` | pytest exit 0; `12 passed`; every case asserts no library/Page or managed-file write | `logs/ac2-ref-rejections-zero-side-effects.txt` |
| AC3 / AC5 / AC6 | `& 'G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe' -m pytest tests/core/test_p09_fu2_import_pages.py::test_stdio_import_pages_runtime_response_and_import_report tests/core/test_p09_fu2_import_pages.py::test_unicode_folder_direct_children_natural_order_and_hashes tests/core/test_p09_fu2_import_pages.py::test_duplicate_skip_and_import_as_new_report_dimensions_and_side_effects tests/core/test_p09_fu2_import_pages.py::test_pdf_import_report_has_source_hash_page_hashes_and_real_page_order tests/core/test_p09_fu2_import_pages.py::test_pdf_duplicate_report_and_import_as_new tests/core/test_p09_fu2_import_pages.py::test_pdf_interruption_reports_committed_page_and_pending_remainder tests/core/test_p09_fu2_import_pages.py::test_corrupt_sources_are_rejected_without_managed_or_library_writes tests/core/test_p09_fu2_import_pages.py::test_encrypted_pdf_is_rejected_before_any_managed_copy_or_page -vv -s` | pytest exit 0; `9 passed` | `logs/ac3-importer-and-report-cases.txt` |
| AC4 | `& 'G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe' -m pytest tests/core/test_p09_fu2_import_pages.py::test_user_source_is_core_only_and_read_only tests/core/test_p09_fu2_import_pages.py::test_directory_grant_rejects_an_outside_child_before_import tests/core/test_p09_fu2_import_pages.py::test_request_path_fallback_is_rejected_as_malformed_reference -vv -s` | pytest exit 0; `3 passed` | `logs/ac4-user-source-scope.txt` |
| AC1–AC7 / AC9 regression | `& 'G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe' -m pytest tests/core -q` | pytest exit 0; `377 passed`, `0 failed`, `0 skipped`, `1` pre-existing Pillow deprecation warning | `logs/pytest-tests-core.txt` |

The AC1 stdio log records the actual `ImportPages` request and Core response. The test signature is redacted; the raw signature/key are not persisted. AC2 checks the six required `REF_*` cases plus host-session, missing-file, reparse, identity, size, and digest failures. Scope escape and request-path fallback are recorded under AC4.

The full suite warning is from `tests/core/test_rc4_stdio_render_preview.py` using Pillow's deprecated `Image.getdata`; it is unrelated to P09-FU2.
