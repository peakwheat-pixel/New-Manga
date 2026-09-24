# M2-D1 evidence manifest and coverage checklist

Read-only audit. Frozen points: code base `307a940265fc325076fe77698750392531f8fce1`,
Owner worktree HEAD at audit start `bbeb4892746795be4bca92f4e5dda91a77c422a3`
(branch `agent/deepseek/M2-D1-headless-qt-coupling-audit`).

Every file below is a **new** artifact created by this Task under `verification/M2-D1/**`.
No pre-existing `verification/**` evidence was modified. Raw command output is stored
verbatim; the `EXIT` values below are copied from the run that produced each log.

## 1. Evidence files

| # | File | What it records | Recorded exit codes |
|---|---|---|---|
| 01 | `01-fixed-point-and-environment.log` | repo/HEAD/branch/git-common-dir, base ancestry, registration-only diff, toolchain (rg/python/py -0p), six-directory file counts | all commands `EXIT=0` |
| 02 | `02-required-rg.log` | the Task-mandated start command `rg -n 'PySide6\|QObject\|QImage\|QPdfWriter\|sqlite3\|connect' src/domain src/application src/ports src/infrastructure src/bootstrap src/ui`, raw stdout, per-directory and per-pattern counts | `EXIT=0`, 286 match lines |
| 03 | `03-supplementary-searches.log` | 17 supplementary read-only searches (A1–H) with command, raw output and exit code per section | A1–H all `EXIT=0` |
| 04 | `04-writer-and-entry-searches.log` | writer-authority and entry-point searches W1–W8 plus E4–E6 | `W1 EXIT=1` (0 hits), `E4 EXIT=1` (0 hits), all others `EXIT=0` |
| 05 | `05-probe-P1-core-import.log` | Core import probe (domain+ports+application) on an isolated temp data root | `EXIT=0`; `imported_ok=102 imported_failed=0`; `qt_available=False` |
| 05b | `05-probe-P1-core-import-ATTEMPT1-failed.log` | first attempt of the same probe, kept because it failed | `EXIT=2` (`AttributeError: module 'importlib' has no attribute 'util'` in the probe itself) |
| 06 | `06-probe-P2-P3-entry.log` | production entry `python -B -m bootstrap.app --smoke-test`, composition-root import, and an AST check of the module-level Qt import lines | `P2_EXIT=1`, `P3_EXIT=1` (both `ModuleNotFoundError: No module named 'PySide6'` at `src/bootstrap/app.py:36`), `P3b_EXIT=0` |
| 07 | `07-probe-P4-infrastructure-bootstrap-import.log` | import probe over `src/infrastructure` (56 modules) and `src/bootstrap` (2 modules) | `EXIT=0`; `imported_ok=53 imported_failed=5` |
| 08 | `08-probe-P5-ui-import.log` | import probe over `src/ui` (21 modules) | `EXIT=0`; `imported_ok=5 imported_failed=16` |
| 10 | `10-probe-P6-qtfree-ui-modules.log` | per-file load of the two Qt-free UI modules, with and without the package `__init__` chain | `EXIT=0`; both `A_by_module_name=FAIL (PySide6)` / `B_by_file_path=OK` |
| 10b | `10-probe-P6-qtfree-ui-modules-ATTEMPT1-failed.log` | first attempt of P6, kept because the probe itself was wrong | `EXIT=0` but `B_by_file_path=FAIL AttributeError` (synthetic module not registered in `sys.modules`; probe defect, not a source fact) |
| — | `probes/core_import_probe.py` | probe: import every module of a named tree and report OK/FAIL | n/a |
| — | `probes/ui_qtfree_bridge_probe.py` | probe: import a module by name vs by file path (P6) | n/a |

Log-ordering caveat: `2>&1` merges stdout and stderr, so within a raw block the
traceback (stderr, unbuffered) can appear **before** earlier stdout lines (visible in
`05-probe-P1-core-import-ATTEMPT1-failed.log`). Counts and `EXIT` values are unaffected.

## 2. Coverage checklist — D1-AC1

| Tree | Files (py) | Audited | Import-probed | Qt-blocked modules |
|---|---|---|---|---|
| `src/domain` | 13 | yes | 13/13 OK | 0 |
| `src/ports` | 23 | yes | 23/23 OK | 0 |
| `src/application` | 66 | yes | 66/66 OK | 0 |
| `src/infrastructure` | 56 | yes | 51 OK / 5 FAIL (4 are `rendering/*`, 5th is `bootstrap.app`, counted below) | 4 |
| `src/bootstrap` | 2 | yes | 1 OK / 1 FAIL | 1 |
| `src/ui` | 21 (+25 QML) | yes | 5 OK / 16 FAIL **by module name**; 2 of those 16 load OK **by file path** (P6) | 16 (14 genuinely Qt-bound + 2 Qt-free modules stranded behind Qt package `__init__`) |
| **total** | **181 py + 25 qml** | **all six trees** | **160 OK / 21 Qt-blocked by module name; 162 OK / 19 Qt-bound at file level** | **21 by module name** |

No directory was skipped; zero-hit searches are recorded with their command and
`EXIT=1` in `03-`/`04-` logs (e.g. `W1` writes outside `sqlite/`, `E4` entry points).

## 3. Environment facts that bound the audit

| Fact | Value | Evidence |
|---|---|---|
| Python interpreters available | 3.10 / 3.11 / 3.12 / 3.14 (`py -0p`) | `01-…log:71-76` |
| `python` on PATH | `C:\Python314\python.exe`, Python 3.14.6 | `01-…log:60-64` |
| PySide6 installed | **No** (none of the four interpreters has it) | `05-…log` `qt_available=False`; `06-…log` `ModuleNotFoundError` |
| ripgrep | 15.2.0 | `01-…log:51-58` |
| shell | pwsh 7.6.6 on Windows 10.0.26200 | `01-…log:4-5` |
| `__pycache__` written into `src/**` | 0 (probes ran with `python -B` + `PYTHONDONTWRITEBYTECODE=1`) | `07-…log`, `08-…log` (post-run count printed) |

## 4. Honest NOT_RUN / UNVERIFIED list

- Product test suite: **NOT_RUN** (source untouched; PySide6 absent, so the Qt-dependent
  suites cannot execute in this environment).
- Runtime headless assembly of the production stack: **UNVERIFIED** (blocked by the
  absent PySide6 and by the entry's unconditional `QGuiApplication`).
- Any Qt-platform behaviour (fonts, QPainter, QML loading): **UNVERIFIED** here; only
  static evidence plus the repository's own test-fixture statements were used.
- `packaging/**`, `*.spec`, frozen-entry behaviour: **NOT PRESENT** on this branch
  (`git ls-files` → `E4 EXIT=1`); not audited.
- Real user data root: never touched; all probes used generated temp directories under
  `%TEMP%` that were deleted after the run.
