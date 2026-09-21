# Project Rebaseline Plan

Status: **ACTIVE DEVELOPMENT BASELINE — Stage B T1.1.2 complete**

Audit date: 2026-09-21 (Asia/Shanghai)

Code baseline audited: `master` @ `ce21ff9ea5738970bbda9a86079b673918c76048`

This file is the sole source of truth for sequencing. `doc/STATUS.md` is the
only live execution checkpoint. `doc/tasks/`, `doc/handoffs/`, `doc/reviews/`
and `verification/` are historical evidence unless this file explicitly
releases a task.

## Current implemented state

### Verified complete at the current code baseline

- SQLite v2 schema, migrations, region/revision persistence, connection
  ownership and managed-copy safety boundaries.
- Local image, PDF and picture-MOBI import paths, with typed failure behavior.
- Scheduler/executor, pause/stop/retry/recovery state, render/export adapters,
  Webtoon tiled reading and diagnostics wiring.
- Four top-level QML routes and the existing Bookshelf/Workbench/Reader shell.
- Backup/restore service and restore admission/latch tests; production backup
  UI/bootstrap exposure is not part of this verified list.
- T1.1.2 Region Canvas & Creator: rectangle/polygon creation, canonical page
  coordinate conversion, real SQLite persistence, deletion, Inspector sync and
  production `region_creator`/`region_deleter` wiring.
- Fresh Codex integration verification: `1031 collected = 1025 passed + 6
  skipped`, exit 0. The six skips are the existing OpenSSL-unavailable TLS
  cases.
- Fresh smoke verification: `python -m bootstrap.app --smoke-test` exit 0.

### Partial, blocked or missing

- **T1.1.1 gap:** production assembly still passes `detector=None`; page-level
  detection fails closed with `PROVIDER_NOT_CONFIGURED`. No production
  `DetectionProvider` implementation is selected or wired.
- **T1.2.1 gap:** `SettingsView.qml` is a category placeholder and there is no
  Settings ViewModel or usable provider/credential/endpoint/proxy save flow.
- **T2.1.1 gap:** the selected F · Graphite Atelier design is documented, but
  production QML still uses the pre-F hard-coded palette and has no shared
  token/theme layer.
- **T3.1.1 gap:** reading progress and export history still use JSON document
  stores; core library/pipeline persistence is already SQLite.
- **T3.2.1 gap:** no product PyInstaller spec/build script or clean-machine
  release artifact exists. The old TASK-004 experiment is evidence for a Qt
  smoke binary, not a product package.
- Real provider quality and external endpoint behavior are not proven by the
  unit suite; adapters and fail-closed paths are not production quality claims.

## Historical Task audit

Classification is based on current source, current tests, fixed integration
commits and review evidence. It does not copy the old `status: done` field.
Historical files are not rewritten merely to change this classification.

| Classification | Tasks | Audit reason |
|---|---|---|
| `VERIFIED_COMPLETE` | TASK-005–015, TASK-029–032, TASK-034–046, TASK-049–058, TASK-060–065 | Integrated implementation or contract has current code and reproducible review/test evidence. TASK-013 is complete for its original progress/workbench scope; the canvas gap is a later slice. |
| `IMPLEMENTED_NOT_VERIFIED` | TASK-059 | Design artifacts are integrated, but the latest evidence round still awaits the independent review checkpoint; production QML implementation is intentionally a later task. |
| `PARTIAL` | TASK-004, TASK-016–021, TASK-023, TASK-033 | The bounded slice exists, but its own evidence records a clean-machine gate, model/endpoint quality limitation, large-page limitation, deferred sub-slices, deferred MOBI history, or missing real-provider capability. |
| `BLOCKED` | none | No historical task is promoted to blocked when a bounded delivered slice exists; the current blockers are represented as gaps in the new roadmap. |
| `NOT_STARTED` | none | Former proposed tasks were replaced or retained in the new roadmap rather than left as an unowned queue. |
| `SUPERSEDED` | TASK-022, TASK-025–027, TASK-047, TASK-048 | Replaced by T1.2.1/T2.1.1/T2.2.1/T3.2.1 or by the later connection-ownership implementation. TASK-047 was explicitly rejected. |
| `DUPLICATE` | none | No additional independent delivery was found to be a pure duplicate. |
| `OBSOLETE` | none | Retired scope is recorded as superseded so its history remains traceable. |
| `DOC_ONLY` | TASK-001–003, TASK-024, TASK-028 | These are intentionally document/contract/design deliverables; their completion does not imply product implementation. |

The old task ledgers remain in place for traceability. Their frontmatter is
historical metadata, not a second scheduling source of truth.

## Dependency graph

```text
T1.1.2 Region Canvas & Creator
  requires: TASK-008/TASK-049 region service and current Workbench VM seam
  writes:  QML workbench overlay, Workbench VM creator slot, interaction tests
  serial integration: src/bootstrap/app.py region_creator injection

T1.1.1 Production Text Detector
  requires: detector choice and provider contract decision
  writes: selected DetectionProvider adapter + bootstrap wiring + E2E test
  must not: use MangaOCR as a detector or silently fall back

T1.2.1 Settings UI & ViewModel
  requires: existing TASK-009/TASK-050 settings/credential services
  writes: settings VM, provider/credential/endpoint/proxy QML, persistence tests

T2.1.1 Graphite Atelier QML
  requires: T1.1.2 and T1.2.1 contracts stable
  -> T2.2.1 Reader/Workbench polish

T3.1.1 SQLite progress/export history
  requires: TASK-057 backup/recovery slice; recommended after T2 stabilization
  -> T3.2.1 packaging and clean-machine release gate
```

No downstream task is released before its prerequisite is integrated. Product
code, shared contracts, `src/bootstrap/app.py`, SQLite migrations and top-level
QML shell changes are serialized through Codex.

## New roadmap and execution order

| Order | Task | State | Owner / reviewer | Acceptance boundary |
|---:|---|---|---|---|
| 1 | **T1.1.2 Region Canvas & Creator** | **VERIFIED_COMPLETE** | Qoder implementation / Codex non-author review and integration; base `b985d9c`, integrated `5b91745` | Draw a rectangle/polygon on the original page; inspector updates; matching `regions` and `region_revisions` rows are created; no source-file write. |
| 2 | T1.1.1 Production Text Detector | PLANNED; evaluation may be document-only | DeepSeek Harness / Codex | A page without regions creates a persisted candidate Region through a selected real detector; no `PROVIDER_NOT_CONFIGURED` on the configured path. |
| 3 | T1.2.1 Settings UI & ViewModel | PLANNED | ZCode / Codex | Provider, credential, endpoint and proxy settings survive restart, feed the pipeline, and never enter logs/diagnostics. |
| 4 | T2.1.1 Apply Design F to QML | PLANNED | ZCode / Qoder + Codex | Shared F tokens are consumed by all four pages; 158px bookshelf geometry and accepted state contrast are verified without business-logic changes. |
| 5 | T2.2.1 Reader & Workbench Polish | PLANNED | ZCode / non-author reviewer | Chapter picker, Workbench empty-state picker and dismissible command-error notification are accessible and tested. |
| 6 | T3.1.1 Unify Storage into SQLite | PLANNED | Codex / DeepSeek Harness | JSON progress/export stores migrate once into transactional SQLite with rollback and no data loss. |
| 7 | T3.2.1 Windows Packaging & Release Gate | PLANNED | Codex / Qoder + DeepSeek Harness | Product onedir launches on clean Windows without Python, completes the core workflow, and exits without a residual process. |

Preparation-only research for T1.1.1 may run without changing `src/**` or
`tests/**`. No second product task becomes active until Order 1 is integrated.

## Directory and document governance

- Keep `src/`, `tests/`, `doc/01–09`, contracts, task/review/handoff evidence
  and verification logs.
- Keep historical tasks in place; archive them logically through the mapping in
  this file instead of moving or deleting them.
- Treat `verification/` as evidence, not generated cache. Do not delete logs
  during this rebaseline.
- `.pytest_cache/` is generated and ignored. `.codewiki/`, `wiki/`,
  `.repowikiignore` and `.qoder-credits/` are untracked agent/generated
  material; preserve them for owner review and do not add them to the product
  baseline in this checkpoint.
- `experiments/TASK-017/README.md` is another agent's uncommitted change;
  preserve it and keep it outside this audit commit.
- The 2026-09-20 worktree inventory is evidence only and must be refreshed
  before any future worktree deletion. No worktree deletion or prune is
  authorized here.

## Recovery checkpoint

```powershell
Set-Location 'G:\CODEX\New Manga'
git status --short --branch
git rev-parse HEAD
Get-Content doc\STATUS.md
git log -8 --oneline --decorate
$env:PYTHONPATH='src'
& 'C:\Users\49745\AppData\Local\Temp\new-manga-audit-py314-20260921\Scripts\python.exe' -m pytest tests -q -p no:cacheprovider -rs
```

Resume only after confirming the current branch, dirty files, `STATUS.md`,
this plan and the latest verification artifact. Do not infer progress from
chat history.
