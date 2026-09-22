# T1.1.1 Codex Integration Evidence

Date: 2026-09-22 (Asia/Shanghai)

## Recovery and scope

- Repository: `G:/CODEX/New Manga`
- Actual master before integration: `bec6c23992bb971dbaef97ead05f6ac9bf7bf41e`
  (the user-declared `94ab0d3` had already advanced through the CodeWiki-only
  commits `d7119a2` and the scope-blocker record `bec6c23`).
- Isolated integration branch: `agent/codex/T1.1.1-integration`
- Product merge commit: `f56f441c1ce981ff83a3af98c5862917e35711f1`
- ZCode author branch remains unchanged at `4a631355316e959e9a9704f1ead2eaed39cbf7a3`.
- No `git reset --hard` or `git clean -fd` was used.
- Main-worktree dirty files were not overwritten.

The user-authorized reconciliation includes the required production seam and
supporting tests: `src/bootstrap/app.py`, `tests/providers/t111_support.py`,
`tests/providers/test_detect_seam_t111.py`,
`tests/providers/test_detection_doctr_real.py`, and
`tests/providers/test_detector_assembly.py`. The detector implementation,
`requirements.txt`, and `verification/T1.1.1/**` are also in scope. No SQLite
schema, ports, QML, Settings, Roadmap, or export files were changed.

## Fresh verification

All commands below ran in the isolated integration worktree with
`G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe` (Python
3.12) and, where applicable, `PYTHONPATH=src`.

| Check | Command/result | Exit |
|---|---|---:|
| CPU focused detector suite | `pytest tests/providers/test_detection_doctr.py tests/providers/test_detection_doctr_real.py tests/providers/test_detector_assembly.py tests/providers/test_detect_seam_t111.py -q -p no:cacheprovider` → `46 passed in 16.50s` | 0 |
| Production bootstrap path | `python verification/T1.1.1/scripts/bootstrap_detect_sqlite_probe.py` → `BOOTSTRAP_DETECT_SQLITE_OK regions=2 revisions=2 detect_status=completed source_sha=266b124246d3f88049627b24898c180c002b4594bf239880fd9bda0cc5519896` | 0 |
| Bootstrap smoke | `python -m bootstrap.app --smoke-test --data-root <fresh temp>` | 0 |
| Compile | `python -m compileall -q src tests verification/T1.1.1/scripts/bootstrap_detect_sqlite_probe.py` | 0 |
| Diff check | `git diff --check -- src tests doc verification requirements.txt` | 0 |
| Real material quality | `real_material_check.py --material G:/CODEX/New Manga/material/17 --device cpu` → 169 pages, 5,244 candidates, mean 31.03/page, mean confidence 0.6298, exit 0 | 0 |
| Source protection | Material signature before/after: `83480c9d686a215ec48f22359881ddfcbaad5257d3353fdc503faea5663d3f66` / same, `UNCHANGED=True` | 0 |
| Export comparison | `test_start_export_completes_and_updates_history` passed in the targeted comparison run; the historical order-sensitive signal race remains deferred and is outside this diff | 0 |

Full suite command:

```powershell
$env:PYTHONPATH='src'
& 'G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe' -m pytest tests -q -p no:cacheprovider
```

Result: `1077 collected = 1070 passed + 6 skipped + 1 failed`, one warning,
exit `1`, in 67.00 seconds. The only failure is
`tests/providers/test_registry_readiness.py::test_no_model_runtime_is_installed_in_this_environment`:
the implementation venv intentionally contains `torch` for docTR, so this
environment-readiness assertion fails as expected. The six skips are the
existing OpenSSL-unavailable TLS cases. The warning is the existing `mobi`
`imghdr` deprecation warning. No detector test failed.

The targeted comparison of registry readiness plus export returned
`1 failed, 1 passed`, exit `1`: registry readiness failed for the same expected
torch-presence reason, while export passed in that run. The previously observed
export signal race is retained as an independent deferred maintenance finding;
it was not introduced by, or modified in, T1.1.1.

## Acceptance decision

The focused detector suite, actual bootstrap-to-detector-to-SQLite path,
real-page quality run, source protection, smoke, compile, and diff checks are
fresh and green. The only full-suite failure is an environment assertion that
contradicts the required docTR implementation environment; the approved
pre-existing export race remains outside scope. T1.1.1 has no blocking
integration finding and is **INTEGRATED / VERIFIED_COMPLETE**.

## Deferred findings

1. `test_registry_readiness` needs an environment-aware readiness assertion or
   a clean dependency-isolated environment; it is not a detector regression.
2. `tests/reading_export/test_viewmodels.py::test_start_export_completes_and_updates_history`
   has a pre-existing order-sensitive Qt signal race; it remains assigned to a
   separate export/reading reliability window.
