# Legacy Shell Archive (AD-001 era)

**Status: HISTORICAL — archived 2026-10-29 by LEGACY-SHELL-ARCHIVE-1.**

This directory holds the archived parts of the AD-001 desktop shell that could be moved **without breaking
product imports or historical evidence pins**. Two things intentionally stay in place:

1. `apps/desktop/**` (Tauri/React shell) — **42+ historical done-task Canonical Evidence pins** reference
   files under `apps/desktop/src-tauri/src/**` and `apps/desktop/frontend/src/**`; the governance rule
   "files still referenced by current Gate/Task/Review/evidence pins stay at their original path" applies.
   See `apps/desktop/LEGACY_FROZEN.md`.
2. `src/ui/**` (PySide6/QML shell) — **product code imports it**: `src/bootstrap/app.py` imports
   `ui.viewmodels.bookshelf.viewmodel` at module level, and 6+ core tests reach it through
   `bootstrap.app.assemble_services`. Moving it would break product imports and test collection.

## Contents (moved)

| Path | Origin | Tracked files |
|---|---|---|
| `tests-ui-shell/` | `tests/ui_shell/` (PySide6 UI tests) | 12 |
| `tests-packaging/test_frozen_runtime_contract.py` | `tests/packaging/` (QML path contract) | 1 |
| `tests-packaging/test_packaging_contract.py` | `tests/packaging/` (old PyInstaller spec contract) | 1 |
| `tests-workbench/test_qml_workbench.py` | `tests/workbench/` (loads QML workbench view) | 1 |
| `packaging/new_manga.spec` | `packaging/` (old PySide6 PyInstaller spec) | 1 |
| `tools-dev/dev-preview.ps1` | `tools/dev/` (old shell dev preview launcher) | 1 |

## Reference migration

- The moved paths had **0 Canonical Evidence pins** (verified 2026-10-29), so the governance checker is
  unaffected.
- Historical prose references in `doc/tasks/**`, `doc/handoffs/**`, `doc/reviews/**`, `verification/**`
  and `audit/**` are kept byte-for-byte (historical records are not rewritten); they are listed in the
  task evidence as "historically stale references".
- **Build chain decoupled**: `packaging/m2ac5/build_sidecar.ps1`, `apps/desktop-avalonia/scripts/package.ps1`,
  `README.md`, `packaging/m2ac5/README.md` and `.github/workflows/build-release.yml` now use
  `apps/desktop-avalonia/build/sidecar/` instead of the legacy `apps/desktop/src-tauri/target/` path.

## What stays for archaeology

- `src/ui/` — retained in place (product import chain; see above).
- `apps/desktop/` — retained in place (evidence pins; see above).
- `packaging/new_manga.spec` moved here; `packaging/m2ac5/core_sidecar.spec` remains the live spec.
