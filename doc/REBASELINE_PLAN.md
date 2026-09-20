# Project Rebaseline Plan

Status: **ACTIVE DEVELOPMENT BASELINE**  
Adopted from: Stage 3 Final Project Rebaseline Plan + Final Review corrections  
Repository baseline inspected: `master` @ `d05b3dbbbf4806df07d2b310683923d5df01f2a5`  
Effective date: 2026-09-20

This file is the sole planning source of truth for future development sequencing. Product requirements and architecture constraints remain authoritative in D01–D08 and `doc/contracts/**`; historical Task, Handoff, Review, and verification files remain evidence, not current scheduling authority.

## Rebaseline ruling on counts

The approved prose says “6 Epics / 8 Tasks”, but its explicit tree names **7 Epics and 9 Task IDs**. No approved item is silently discarded. This baseline therefore adopts the explicit tree below: **3 Milestones / 7 Epics / 9 Tasks**. Owner may later normalize the labels or merge tasks through an explicit planning decision; until then the listed IDs are authoritative.

## Product goal

Deliver a safe Windows desktop workflow for importing local manga, acquiring text regions, configuring OCR/translation/image providers, translating and typesetting, then reading or exporting results without modifying user source files or losing manual edits, locks, revisions, or recovery state.

## Current verified capability state

- **Stable**: SQLite v2 core persistence, Managed Copy, image/PDF/MOBI import, Webtoon tiled reading, scheduler/executor, rendering/export, connection ownership, diagnostics wiring.
- **Partial**: Workbench execution and views exist, but manual region drawing is absent.
- **Blocked**: Production text detection is assembled with `detector=None`.
- **Missing**: Usable Settings UI and production QML implementation of F · Graphite Atelier.
- **Technical debt**: Reading progress and export history still use JSON stores.

No percentage-complete claim is used.

## Milestones and Epics

### Milestone 1 — Alpha Core Loop Closure

- **E1.1 Region Input & Detection**: production detection plus manual region creation.
- **E1.2 Settings UI & Provider Configuration**: user-accessible provider, credential, endpoint, and proxy settings.
- **E1.3 Branch Integration & Baseline Cleanup**: close TASK-065 and integrate the reviewed TASK-057 delivery safely.

### Milestone 2 — UI/UX Modernization & Polish

- **E2.1 QML Design Modernization**: implement F · Graphite Atelier in production QML.
- **E2.2 Interaction & Navigation Polish**: close reader/workbench dead ends and provisional error UI.

### Milestone 3 — Storage Convergence & Alpha Release Gate

- **E3.1 Persistence Unification**: move reading progress and export history into SQLite.
- **E3.2 Packaging & End-to-End Release Gate**: Windows package and clean-machine acceptance.

## Task tree and status

Only one task is active. `ACTIVE` here means released for the next execution cycle; implementation has not started under this rebaseline.

| Task | Title | State | Hard dependencies | Owner / Reviewer |
|---|---|---|---|---|
| **T1.3.2** | Close TASK-065 Slices | **ACTIVE — STOP before implementation** | none | Codex / Qoder |
| T1.3.1 | Integrate Backup Branch | PLANNED | none | Codex integrator; ZCode author / Qoder reviewer |
| T1.1.1 | Production Text Detector | PLANNED — **IMPLEMENTATION CHOICE REQUIRED** | none | DeepSeek Harness / Codex |
| T1.1.2 | Region Canvas & Creator | PLANNED | none | ZCode / Qoder |
| T1.2.1 | Settings UI & ViewModel | PLANNED | none | ZCode / Codex |
| T2.1.1 | Apply Design F to QML | PLANNED | T1.1.2, T1.2.1 | ZCode / Qoder + Codex |
| T2.2.1 | Reader & Workbench Polish | PLANNED | T2.1.1 | ZCode / Qoder |
| T3.1.1 | Unify Storage into SQLite | PLANNED | T1.3.1 | Codex / DeepSeek Harness |
| T3.2.1 | Windows Packaging & Gate | PLANNED | all preceding applicable tasks | Codex / Qoder + DeepSeek Harness |

## Task definitions

### T1.3.2 — Close TASK-065 Slices

- **Objective**: complete the docs/test precision work already approved in `doc/tasks/TASK-065.md`.
- **Scope**: make the shutdown-drain test prove an active worker existed; refresh full-suite evidence; correct stale connection typing/docs; remove the tautological stderr assertion.
- **Non-goals**: no product behavior, Schema, dependency, SQLite, QML, Managed Copy, or cleanup changes.
- **Preconditions**: this rebaseline is committed; TASK-065 AC and allowed paths are rechecked against the new HEAD.
- **Deliverables**: tests/docs changes, verification evidence, Handoff, independent Review.
- **Acceptance criteria**: all five TASK-065 ACs; collected tests not below 951; no added skip/xfail or weakened effective assertion.
- **Verification**: targeted shutdown-drain tests, collect-only count, full regression with environment/command/exit/skip evidence.
- **Done**: independent Review approved, Codex integration, post-integration regression, Closure Gate.

### T1.3.1 — Integrate Backup Branch

- **Objective**: reconcile and integrate the already reviewed TASK-057 backup/restore delivery without losing later master work.
- **Scope**: fixed delivery head `29546f7`; Qoder Review at `agent/qoder/TASK-057-review` records `approved`; rebase/merge impact analysis against current master; Codex whitelist ruling; integrate and verify. R-008/R-009 remain acceptance gaps of this integration task and may not escape into a new task if they prevent safe restore wiring.
- **Non-goals**: no backup-model redesign and no unrelated storage work.
- **Preconditions**: TASK-060/061 are integrated; refresh both branch heads before execution.
- **Deliverables**: reconciled review evidence, merge commit, updated Task/Handoff, post-integration verification.
- **Acceptance criteria**: backup/restore tests and full suite pass; restore admission protects every start path; user source files remain untouched; no hanging connection.
- **Verification**: `tests/maintenance/test_sqlite_backup.py`, affected workbench/connection tests, then full regression.
- **Done**: fixed reviewed head matches integrated content, findings are dispositioned, Codex closes the task.

### T1.1.1 — Production Text Detector

- **Objective**: remove production `detector=None` so page-level translation can create Regions for pages without existing annotations.
- **Implementation choice required**: do not select a provider during rebaseline. At task start, use repository evidence → technical evaluation → architecture decision to choose online Vision detection, DBNet, Comic Text Detector, or another actual detection provider. MangaOCR is recognition, not detection, and must not be used as the detector.
- **Scope**: implement the chosen `TextDetector` adapter and inject it through `build_production_handlers`.
- **Non-goals**: no scheduler rewrite, Detection contract rewrite, or OCR recognition work.
- **Preconditions**: TASK-049 detection-to-Region persistence path remains valid.
- **Deliverables**: architecture decision, adapter, bootstrap wiring, end-to-end page detection test.
- **Acceptance criteria**: an imported page with no Regions can run detection and persist at least one candidate Region without `PROVIDER_NOT_CONFIGURED`.
- **Verification**: end-to-end detection/Region test plus affected provider/pipeline/full regression suites.
- **Done**: architecture decision recorded, independent Review approved, Codex integration verified.

### T1.1.2 — Region Canvas & Creator

- **Objective**: let users draw text regions on the original page in the Workbench.
- **Scope**: QML canvas overlay for rectangle/polygon input; a ViewModel creation slot; existing `RegionEditingService.create_region` path.
- **Non-goals**: no Region storage-model or typesetting-engine redesign.
- **Preconditions**: TASK-008/049 Region services remain available.
- **Deliverables**: QML interaction, ViewModel binding, interaction tests.
- **Acceptance criteria**: drawing a region updates the inspector and creates matching `regions` and `region_revisions` rows.
- **Verification**: QML interaction plus service/persistence tests.
- **Done**: independent Review approved and Codex integration verified.

### T1.2.1 — Settings UI & ViewModel

- **Objective**: replace the Settings placeholder with usable provider, credential, endpoint, and proxy configuration.
- **Scope**: Settings ViewModel over existing settings/credential services; bootstrap registration; QML provider list, password input, base URL, local endpoint, proxy, and save behavior.
- **Non-goals**: no plugin marketplace or credential-encryption redesign.
- **Preconditions**: TASK-009/050 backend services remain valid.
- **Deliverables**: ViewModel, QML page, settings contract and tests.
- **Acceptance criteria**: user settings survive restart and are consumed by the pipeline; secrets are not exposed in logs/UI diagnostics.
- **Verification**: UI/service integration, persistence, credential boundary, and full regression tests.
- **Done**: independent Review approved and Codex integration verified.

### T2.1.1 — Apply Design F to QML

- **Objective**: implement TASK-059 F · Graphite Atelier across the four top-level pages.
- **Scope**: shared QML theme/tokens; AppShell, Bookshelf, Workbench, Reader, and Settings colors, spacing, typography, controls, and 158px card geometry.
- **Non-goals**: no business/ViewModel changes; no C glass, D top navigation, E command palette, or B chapter-card IA.
- **Preconditions**: M1 UI contracts are stable; ND-6 and any remaining TASK-059 implementation decisions are resolved.
- **Hard dependencies**: T1.1.2, T1.2.1.
- **Deliverables**: production QML, contract tests, visual evidence.
- **Acceptance criteria**: production QML consumes the chosen tokens; 158px bookshelf cards; required state contrast meets the accepted contract; four-page behavior remains intact.
- **Verification**: QML contract/interaction tests and offline screenshot/contrast audit.
- **Done**: Qoder visual Review and non-author engineering Review approved; Codex integration verified.

### T2.2.1 — Reader & Workbench Polish

- **Objective**: close the reader/workbench navigation dead ends and replace provisional command errors with the accepted F notification pattern.
- **Scope**: reader chapter picker, workbench empty-state picker, command error notification behavior.
- **Non-goals**: no unrelated feature expansion.
- **Dependencies**: T2.1.1.
- **Deliverables**: QML behavior and interaction tests.
- **Acceptance criteria**: chapter switching and empty-state selection are user-accessible; errors are visible, dismissible, and follow the accepted design.
- **Verification**: QML interaction tests plus regression.
- **Done**: independent Review approved and Codex integration verified.

### T3.1.1 — Unify Storage into SQLite

- **Objective**: replace JSON-backed export history and reading progress with transactional SQLite persistence and safe legacy-data migration.
- **Scope**: schema migration, repositories/adapters, one-time JSON import, rollback and compatibility tests.
- **Non-goals**: no export or reading business-rule change.
- **Hard dependency**: T1.3.1, because backup/recovery must protect the migration.
- **Execution-order constraint**: **recommended after M2 stabilization**. T2.1.1 is not a hard code dependency unless fresh implementation evidence proves otherwise.
- **Deliverables**: migration, adapters, safe import/rollback behavior, tests.
- **Acceptance criteria**: production no longer depends on JSON stores; old data migrates once without loss; rollback keeps metadata consistent.
- **Verification**: storage/migration/reading/export suites and full regression.
- **Done**: independent Review approved and Codex integration verified.

### T3.2.1 — Windows Packaging & Gate

- **Objective**: produce an installable Windows Alpha and verify the complete user workflow on a clean machine.
- **Scope**: PyInstaller packaging, required Qt/plugins/fonts/runtime assets, clean Windows 11 walkthrough, D08 release gate.
- **Non-goals**: no automatic updater.
- **Dependencies**: all preceding tasks required by the release path.
- **Deliverables**: versioned installer/build artifact and release acceptance report.
- **Acceptance criteria**: without a system Python install, the app launches, imports local manga, accepts provider settings, translates, reads/exports, and exits without a residual process.
- **Verification**: automated package checks plus clean-VM manual acceptance.
- **Done**: all release findings closed, reviewers approve, Codex signs the Alpha release candidate.

## Dependency and execution order

```text
ACTIVE: T1.3.2
  -> T1.3.1
  -> T1.1.1 + T1.1.2 (safe only after scopes are frozen; app.py integration remains serial)
  -> T1.2.1
  -> T2.1.1
  -> T2.2.1
  -> T3.1.1 (hard: T1.3.1; recommended after M2)
  -> T3.2.1
```

Every closed task triggers a fresh dependency check. Planned work does not become active merely because it is expected later.

## Legacy mapping

Legacy Task files remain in `doc/tasks/`; they are archived **logically, not erased or moved**, preserving links, Git history, decisions, Reviews, Handoffs, and verification evidence.

| Legacy Task | New location | Action |
|---|---|---|
| TASK-001–008 | M1 foundation | KEEP |
| TASK-009 | T1.2.1 | MERGE + REOPEN UI gap |
| TASK-010–012 | M1 foundation | KEEP |
| TASK-013 | T1.1.2 | MERGE + REOPEN canvas gap |
| TASK-014 | M1 foundation | KEEP |
| TASK-015 | T2.2.1 + T3.1.1 | MERGE remaining interaction/storage gaps |
| TASK-016–018 | research archive | KEEP (RESEARCH) |
| TASK-019 | T1.1.1 | MERGE + REOPEN detector gap |
| TASK-020 | M1 foundation | KEEP |
| TASK-021 | T1.3.1 | MERGE backup subset |
| TASK-022 | T1.2.1 + T2.1.1 | RETIRE / SUPERSEDED |
| TASK-023 | M1 foundation | KEEP |
| TASK-024 | contract archive | KEEP (CONTRACT) |
| TASK-025 | later backlog | RETIRE FROM ALPHA |
| TASK-026–027 | T3.2.1 | SUPERSEDED |
| TASK-028–046 | M1 foundation | KEEP |
| TASK-047 | rejected design archive | RETIRE (REJECTED) |
| TASK-048 | TASK-060 replacement history | SUPERSEDED |
| TASK-049–056 | M1 foundation | KEEP |
| TASK-057 | T1.3.1 | MERGE reviewed delivery |
| TASK-058 | M1 foundation | KEEP |
| TASK-059 | T2.1.1 | MERGE + EXTEND into QML implementation |
| TASK-060–064 | M1 foundation | KEEP |
| TASK-065 | T1.3.2 | MERGE / ACTIVE closure |

## Agent allocation and conflict control

- **Codex**: coordinator, architect, sole master integrator, closure owner.
- **Qoder**: repository impact analysis, QML/visual quality, non-author Review.
- **ZCode**: bounded UI/feature implementation on assigned branch.
- **DeepSeek Harness**: OCR/detection/translation/image specialist and non-author Review.
- Owner must not Review their own implementation.
- `src/bootstrap/app.py`, SQLite schema/migrations, and top-level QML shell changes are serialized through Codex.

## Governance

Approved rules:

- Repository reality outranks historical planning claims.
- Evidence precedes completion claims.
- Owner and Reviewer are different people/agents.
- Codex is merge owner and integrator.
- Prefer closing tasks over creating tasks.
- A bug/test/acceptance gap that blocks the active task remains inside that task.
- `DONE` requires implementation, targeted verification, full regression, independent Review, integration verification, and Closure Gate.

Proposed metrics, **not hard policy** until Owner approval:

- Task Expansion Ratio ≤ 0.2.
- Ratio > 0.5 warns of divergence.
- Ratio ≥ 1.0 suggests rebaseline.
- Open Tasks ≤ 8.

## Worktree safety

The authoritative snapshot is [WORKTREE_SAFETY_INVENTORY](WORKTREE_SAFETY_INVENTORY.md). No worktree removal or `git worktree prune` is authorized by this rebaseline. Refresh the inventory before any later cleanup.

## Activation and closure rule

T1.3.2 is the only active execution task. This rebaseline deliberately stops before its implementation. At task start, revalidate Objective, Scope, Non-goals, Acceptance Criteria, Verification, Done Definition, allowed paths, base/head, and pre-existing changes against current HEAD.
