# Rebaseline Verification

Date: 2026-09-21 (Asia/Shanghai)

Scope: read-only audit of the code baseline `ce21ff9`; no product feature was
implemented in this Stage A pass.

## Environment

- Shell: PowerShell on Windows.
- Audit interpreter: `C:\Users\49745\AppData\Local\Temp\new-manga-audit-py314-20260921\Scripts\python.exe`.
- Python: 3.14.6; pytest 9.1.1; dependencies installed from the repository's
  `requirements-dev.txt` via the public PyPI index into a temporary venv.
- `PYTHONPATH=src`, `PYTHONDONTWRITEBYTECODE=1`, `QT_QPA_PLATFORM` unset.
- The main checkout had unrelated dirty files; `src/**` and `tests/**` were not
  modified by those changes.

## Fresh commands and results

| Check | Result | Evidence |
|---|---|---|
| `python -m pytest tests --collect-only -q -p no:cacheprovider` | **PASS**, 982 collected, exit 0 | Collection completed in the isolated venv. |
| `python -m pytest tests -q -p no:cacheprovider -rs` | **PASS**, 976 passed, 6 skipped, exit 0 | Six skips are `tests/network` OpenSSL-unavailable TLS cases; no xfail. |
| `python -m compileall -q src tests` | **PASS**, exit 0 | No compile errors. |
| `python -m bootstrap.app --smoke-test --data-root <temporary directory>` | **PASS**, exit 0 | Created `library.db` and `managed/` in the temporary data root. |

## Direct code checks

- `src/bootstrap/app.py` passes `detector=None` to
  `build_production_handlers`; this is the production detection blocker.
- `src/ui/qml/settings/SettingsView.qml` contains only the fixed category list
  and a "settings will be connected later" placeholder; no Settings VM exists.
- Production QML contains the old hard-coded light palette and no shared F
  token/theme module.
- `src/application/reading/service.py` uses `reading_progress.json` and
  `src/application/export/ports.py` uses a JSON history store; SQLite migration
  is not yet implemented for these stores.
- No product `.spec`, packaging script, CI release workflow or product build
  artifact exists. The TASK-004 experiment is intentionally not counted as a
  product package.

## Non-results and limits

- No external OCR/translation endpoint or model-quality benchmark was run.
- No clean-machine Windows release check was possible; T3.2.1 remains planned.
- No files, worktrees, caches or user data were deleted.
- Global Python was not used as completion evidence because it lacked required
  project packages and contained unrelated ML packages that invalidate several
  environment-assumption tests.
