# Project Rebaseline Plan

Status: **ACTIVE DEVELOPMENT BASELINE — T3.1.1 VERIFIED_COMPLETE; T3.2.1 IMPLEMENTATION RELEASED, FULL RELEASE GATE OPEN**

Audit date: 2026-09-21 (Asia/Shanghai)

Initial rebaseline code audit: `master` @ `ce21ff9ea5738970bbda9a86079b673918c76048`

Current integration checkpoint (2026-09-22): T1.1.1 product merge `f56f441`;
T1.2.1 is integrated and verified at code merge `9a14310`, with final evidence
commit `e92c414`. The R5 B-003 credential-store repair passed non-author review
and production probe. T3.1.1 is integrated at product merge `0c70e44` after
DeepSeek Harness approval `4e1eb3a`; its integration evidence is
`verification/T3.1.1/integration-899bd3c.md`. Live HEAD and execution details are in
[`STATUS.md`](STATUS.md).

This file is the sole source of truth for sequencing. `doc/STATUS.md` is the
only live execution checkpoint. `doc/tasks/`, `doc/handoffs/`, `doc/reviews/`
and `verification/` are historical evidence unless this file explicitly
releases a task.

## Architecture decision and future migration registration

[AD-001 Target Desktop Architecture](AD-001_TARGET_DESKTOP_ARCHITECTURE.md) records the user's accepted future target: React + TypeScript presentation, Tauri/Rust desktop shell and IPC, headless Python Core business/persistence authority, and SQLite as persistent source of truth. Status: `ACCEPTED_TARGET_ARCHITECTURE / IMPLEMENTATION_NOT_RELEASED`. This is target intent. The current production baseline remains Python + PySide6/QML + SQLite; historical evidence and current T3.2.1 acceptance remain judged against that baseline.

**M2 — Desktop Architecture Migration: PLANNED / NOT_RELEASED for implementation.** This future Milestone is not the current Active product Task. Its logical dependency order is AD-001 → Migration Discovery / Headless & Qt Coupling Audit → Python Core Decoupling → Contract / IPC → Tauri + React Skeleton → Incremental Feature Migration → Feature Parity → Tauri + Python Sidecar Packaging → Legacy QML Removal. Only [M2-D1 Headless & Qt Coupling Audit](tasks/M2-D1.md) was released as a read-only `research / audit` Task from code base `307a940`; it is now `done` after Codex non-author [Review](reviews/M2-D1-0a27a54.md) `approved` and integration merge `100abfb`. Its [research report](research/M2-D1_HEADLESS_QT_COUPLING_AUDIT.md) records candidates, not implementation authorization. No React, Tauri, IPC, Python migration implementation, shared contract or Schema change is released. T3.2.1 remains the sole Active product Task.

T3.2.1 remains the sole Active product Task with Full Release Gate OPEN. Child [REPAIR-13](tasks/T3.2.1-REPAIR-13.md) is `done`: fixed base=`8738c41`, product delivery=`aed0094`, final Handoff/evidence head=`13ae23f`, independent Review=`ccd26a4` (`APPROVE_WITH_CONDITIONS`, C1/C2 satisfied), Codex integration=`6fe7455`. Integration used only the 62-path fixed task delta; the full author branch was not merged because its ancestry includes unrelated REPAIR-9–12 candidate history. Post-integration focused suite: 162 passed, exit 0. C2 cleanup cleared all trailing whitespace; Codex recount found 13 pre-cleanup diagnostics vs 12 stated in the supplement, recorded in the integration report. Parent Full Gate remains OPEN and parent AC3 remains `BLOCKED`; this child completion does not change them. The former Sandbox attempts remain historical evidence; the parent clean-Windows/Sandbox Gate is unchanged. [REPAIR-14](tasks/T3.2.1-REPAIR-14.md) for F-13-3 is `done`: fixed base=`4ab6f58c06cb0691413e2630cb48a145c18c383a`, delivery=`43b24ee`, Handoff tip=`2f0d266`, DeepSeek Harness Review=`f616175e` (`approved`), Codex integration=`296131b`. R14-008 records the accepted fixture-seeding deviation and unrun GUI-native creation substep; R14-010 path counts are corrected in the integration record. Parent Gate remains OPEN / AC3 BLOCKED.

## Current implemented state

### Verified complete on the integrated product baseline

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
- T1.1.1 Production Text Detector: docTR local detector and production bootstrap
  injection are integrated at `f56f441`; focused detector tests, bootstrap to
  SQLite, real-material detection and source protection passed. Its full suite
  was `1077 collected = 1070 passed + 6 skipped + 1 known environment failure`,
  exit 1; see [integration evidence](../verification/T1.1.1/integration-f56f441.md).
- Earlier T1.1.2 integration verification: `1031 collected = 1025 passed + 6
  skipped`, exit 0; smoke test exit 0. The six skips were existing
  OpenSSL-unavailable TLS cases.

### Partial, blocked or missing

- **T1.2.1 verified complete:** Settings UI/ViewModel, provider/network
  persistence, fail-closed policy, production bootstrap credential injection,
  and authenticated proxy path are integrated and independently verified.
  See the [R5 review](../verification/T1.2.1/review-e5716ac.md) and
  [integration evidence](../verification/T1.2.1/integration-9a14310.md).
- **T2.1.1 gap:** the selected F · Graphite Atelier design is documented, but
  production QML still uses the pre-F hard-coded palette and has no shared
  token/theme layer.
- **T3.1.1 verified complete:** reading progress and export history now use the
  SQLite v4 adapters with non-destructive one-time legacy import; P2 follow-ups
  are recorded in the Task and integration evidence.
- **T3.2.1 gap:** packaging implementation and Sandbox smoke evidence now exist
  on isolated repair branches, but no final product head has passed the full
  Release Gate or been integrated. The `c2fcb1c` decision was **PASS TO START**
  (implementation authorization), not a release pass. Clean interactive Windows,
  data-safety, optional-dependency, performance and final Review evidence remain open.
- Real provider quality and external endpoint behavior are not proven by the
  unit suite; adapters and fail-closed paths are not production quality claims.

## Historical Task audit

Classification is based on current source, current tests, fixed integration
commits and review evidence. It does not copy the old `status: done` field.
Historical files are not rewritten merely to change this classification.

| Classification | Tasks | Audit reason |
|---|---|---|
| `VERIFIED_COMPLETE` | TASK-005–015, TASK-029–032, TASK-034–046, TASK-049–065 | Integrated implementation or contract has current code and reproducible review/test evidence. TASK-013 is complete for its original progress/workbench scope; the canvas gap is a later slice. TASK-059 is a verified design deliverable, not production QML implementation. |
| `IMPLEMENTED_NOT_VERIFIED` | none | No current Task remains in this state; historical TASK-001–065 classifications are retained separately from the current roadmap. |
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
  R4 writes: bounded registry/runtime/VM/bootstrap repair and focused tests
  gate: five R3 findings, new Handoff, non-author re-review, Codex integration

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
| 2 | T1.1.1 Production Text Detector | **VERIFIED_COMPLETE**; integrated `f56f441` | ZCode implementation / Codex non-author review and integration | A page without regions creates a persisted candidate Region through a selected real detector; configured path no longer fails as `PROVIDER_NOT_CONFIGURED`. |
| 3 | [T1.2.1 Settings UI & ViewModel](tasks/T1.2.1.md) | **VERIFIED_COMPLETE**; integrated `9a14310`, evidence `e92c414` | ZCode implementation / Codex non-author review and integration | Provider, credential, endpoint and proxy settings survive restart, feed the pipeline and never enter logs/diagnostics; B-003 production credential path verified. |
| 4 | [T2.1.1 Apply Design F to QML](tasks/T2.1.1.md) | **VERIFIED_COMPLETE**; product code integrated at `5da1cf6` | Qoder / Codex non-author review and integration; base `7f34135` | Shared F tokens use `pragma Singleton` + `qmldir`; all four pages consume them; 158px bookshelf geometry, accepted/completed-state contrast, and a discriminating hard-code guard are verified without business-logic changes. Review/integration evidence: [`review-bc49ef9`](../verification/T2.1.1/review-bc49ef9.md), [`integration-5da1cf6`](../verification/T2.1.1/integration-5da1cf6.md). |
| 5 | [T2.2.1 Reader & Workbench Polish](tasks/T2.2.1.md) | **VERIFIED_COMPLETE**; integrated `fe9fca0` | ZCode functional implementation + Qoder QML/UI/UX / Codex non-author review and integration | Chapter picker, Workbench empty-state picker, dismissible command-error notification, and webtoon canvas consistency are accessible and tested. Evidence: [`review-0846573`](../verification/T2.2.1/review-0846573.md), [`integration-aad510b`](../verification/T2.2.1/integration-aad510b.md). |
| 6 | [T3.1.1 Unify Storage into SQLite](tasks/T3.1.1.md) | **VERIFIED_COMPLETE**; product integrated `0c70e44` | Antigravity implementation / DeepSeek Harness independent Review; Codex Lead / Architect / Integrator | JSON progress/export stores migrate once into transactional SQLite with rollback, non-destructive legacy import and no data loss. Evidence: [review-899bd3c](../verification/T3.1.1/review-899bd3c.md), [integration-899bd3c](../verification/T3.1.1/integration-899bd3c.md). |
| 7 | [T3.2.1 Windows Packaging & Release Gate](tasks/T3.2.1.md) | **IN PROGRESS; FULL RELEASE GATE OPEN**; parent AC3 remains `BLOCKED`; child [REPAIR-13](tasks/T3.2.1-REPAIR-13.md) is `done` at integration `6fe7455` (delivery `aed0094`, evidence head `13ae23f`, Review C1/C2 conditions satisfied). Child [REPAIR-14](tasks/T3.2.1-REPAIR-14.md) for F-13-3 is `done` at integration `296131b` (delivery `43b24ee`, Handoff `2f0d266`, Review `f616175e` approved); R14-008 deviation is explicit and parent Gate remains unchanged. | Codex owns Gate closeout/integration; ZCode completed REPAIR-13; Antigravity completed the bounded REPAIR-14 implementation; DeepSeek Harness independently reviewed it | REPAIR-13 and REPAIR-14 are child slices only and do not establish the parent clean-Windows Gate. REPAIR-14's R14-008 GUI-native creation substep remains `NOT_RUN` and is not claimed as PASS; accepted deviation is recorded. Full parent AC3 and remaining Gate criteria stay open. See [Codex closeout](../verification/T3.2.1/release-gate-closeout-b800d11.md), [AC3 manual observations](../verification/T3.2.1/ac3-interactive-20260925/manual-observations.md), and [REPAIR-14 integration record](../verification/T3.2.1/repair-14/integration-record.md). |

The [formal T1.2.1 Task](tasks/T1.2.1.md), [R5 review](../verification/T1.2.1/review-e5716ac.md)
and [integration evidence](../verification/T1.2.1/integration-9a14310.md) record
the completed Task. T2.1.1 passed its release gate at base `7f34135`, received
non-author review, was integrated at `5da1cf6`, and is now
`VERIFIED_COMPLETE`; its fresh evidence is recorded in
`verification/T2.1.1/`.

The formal [T3.1.1 Task](tasks/T3.1.1.md), its independent
[Release Gate](../verification/T3.1.1/release-gate-e771179.md), DeepSeek Harness
Review, and Codex [integration evidence](../verification/T3.1.1/integration-899bd3c.md)
are complete. The product delivery is integrated at `0c70e44`; R-002 and the
remaining P2 follow-ups are explicitly deferred rather than hidden.

The formal [T3.2.1 Task](tasks/T3.2.1.md) and
[Release Gate](../verification/T3.2.1/release-gate-c2fcb1c.md) use the product
baseline `c2fcb1c`. The Gate decision is **PASS TO START** only. Current Codex
closeout state, fixed repair/review objects, remaining findings and the executable
Windows Sandbox plan are in
[release-gate-closeout-b800d11](../verification/T3.2.1/release-gate-closeout-b800d11.md).

Review status is slice-specific: REPAIR-8 (`3cdfdee` / `37d5488`) was approved
for documentation only; REPAIR-9 (`d2bf6a8` / `eeb095e`) remains
`changes_requested` after Review `85f8c59`; REPAIR-10 (`be5200e` / `d7edea5`)
was approved for packaging-test path independence only. REPAIR-11 Delivery
`9622395` / Handoff `941dbc8` received `changes_requested` from independent
Review `4f2f8a0`; the evidence findings were corrected by REPAIR-12 Delivery
`a2f6695` / Handoff `8738c41`, which received slice-only `approved` Review
`a656486`. The new review does not alter the historical REPAIR-11 decision or
approve the full product Gate. AC3's required interactive workflow remains
`NOT_RUN` and blocks release; AC5=`NOT_RUN`, AC6/AC7=`PARTIAL / NOT_RUN`,
AC8/AC9=`NOT_RUN`, and R-014–R-016=`OPEN`. Codex's current closeout records
O-12-2 and keeps the legacy REPAIR-11 Handoff outside the integration candidate.
No REPAIR-7/9/10/11/12 or related branch may be merged to `master` before full
Gate closure and final independent Review.

## Project control baseline — 2026-09-22

The detailed modified-V2 audit is [PROJECT-AUDIT-2026-09-22](../verification/PROJECT-AUDIT-2026-09-22.md).
It is evidence and a derived map, not a second planning source. The current
project overview, repository/code architecture map, Task ↔ Code ↔ Test
traceability, module maturity, parallel matrix and Dependency Blocking Chain
are maintained there; this Plan retains the authoritative phase, dependency
and release order. The live dashboard, `TaskStatus`/`ExecutionState`, current
branch/HEAD, dirty-file safety and next actions remain in [STATUS](STATUS.md).

Current blocking chain:

```text
T1.2.1 VERIFIED_COMPLETE
  → independent T2.1.1 Release Gate (PASSED)
  → T2.1.1 VERIFIED_COMPLETE @ 5da1cf6
  → T2.2.1 VERIFIED_COMPLETE @ fe9fca0
  → T3.1.1 VERIFIED_COMPLETE @ 0c70e44
  → T3.2.1 implementation authorization (PASS TO START) @ c2fcb1c
  → T3.2.1 full Release Gate OPEN; parent AC3 BLOCKED pending complete fixed-package workflow
  → REPAIR-13 done @ integration `6fe7455` (delivery `aed0094`, evidence `13ae23f`; parent Gate unchanged)
  → REPAIR-14 F-13-3 done @ integration `296131b` (delivery `43b24ee`, Handoff `2f0d266`, Review `f616175e` approved; R14-008/010 disposition recorded; parent Gate OPEN / AC3 BLOCKED)
  → parent T3.2.1 clean-Windows/Sandbox AC3 run + full independent Review remain separately required
```

This is a dependency blocking chain, not a schedule critical path; no reliable
duration model exists. Research-only storage work and knowledge-map refreshes
may be conditional/safe parallel work when their write sets stay isolated.

Audit note: Roadmap ID `T1.1.2` is verified through historical `TASK-013`,
integration `5b91745` and its verification records, but has no dedicated
`doc/tasks/T1.1.2.md`. This is a traceability gap recorded for future document
maintenance; it does not reopen the integrated implementation.

## Directory and document governance

- Keep `src/`, `tests/`, `doc/01–09`, contracts, task/review/handoff evidence
  and verification logs.
- Keep historical tasks in place; archive them logically through the mapping in
  this file instead of moving or deleting them.
- Treat `verification/` as evidence, not generated cache. Do not delete logs
  during this rebaseline.
- `.pytest_cache/` is generated and ignored. The untracked-file inventory in
  the initial audit is historical; refresh `git status` before any edit and
  preserve other agents' material.
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
```

Resume only after confirming the current branch, dirty files, `STATUS.md`,
this plan and the latest verification artifact. Do not infer progress from
chat history.
