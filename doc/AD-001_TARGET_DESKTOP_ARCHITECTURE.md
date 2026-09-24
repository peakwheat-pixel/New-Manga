# AD-001 — Target Desktop Architecture

Status: **ACCEPTED_TARGET_ARCHITECTURE / IMPLEMENTATION_NOT_RELEASED**

Decision owner: User. Registration owner: Codex. Registration base: `master` @ `1e8cb1157c987945316351728f725073b8b109f9` (2026-09-25). Independent review: DeepSeek Harness, pending. This decision records the user's approved target; it does not approve any implementation Task.

## Scope and authority

This Architecture Decision records target intent. [REBASELINE_PLAN](REBASELINE_PLAN.md) remains the sole planning source; [STATUS](STATUS.md) remains the live execution source. The existing [02 technical architecture](02_TECHNICAL_ARCHITECTURE_.md), QML mappings, nonfunctional requirements and acceptance criteria still describe the legacy production baseline until a separately released Architecture Documentation Rebaseline Task updates them. Historical Task, Handoff, Review and `verification/**` evidence is interpreted against its own PySide6/QML baseline and is not rewritten.

## CURRENT_REALITY

The current production program and T3.2.1 candidate use **Python + PySide6/QML + SQLite**. QML is the current production UI and remains supported during migration. The current T3.2.1 Windows Packaging & Release Gate remains under its existing Owner, scope and acceptance criteria. Its Full Gate is OPEN; AC3 is BLOCKED at image import, and REPAIR-13 is released to Qoder. This decision neither closes, narrows, cancels nor redefines that Gate. Existing PyInstaller/QML packaging evidence applies to legacy production closure only.

## TARGET_INTENT and decision

The future desktop architecture is **React + TypeScript + Tauri + Python Core**, with SQLite as the persistent source of truth:

| Boundary | Authority and responsibility | Exclusions |
|---|---|---|
| React + TypeScript | Presentation: UI, interaction, Workspace, Library, Reader, Settings, Canvas/WebGL presentation and frontend state projection. | No direct SQLite access, OCR execution or domain logic. |
| Tauri / Rust | Desktop shell and system bridge: window, process, Python sidecar lifecycle, IPC transport, system integration and permission boundary. | Rust carries no domain business logic and is not a DB writer. |
| Python Core | Business, domain, application, ports, reusable infrastructure business adapters, SQLite persistence, OCR, detection, translation, inpainting, rendering business semantics, export, provider, task, revision and lock authority. | Core must ultimately run headless; UI/Qt GUI coupling needs audit before decoupling choices. |
| SQLite | Persistent source of truth, written under Python Core authority. | React and Rust cannot become independent DB writers. |

The four top-level product areas remain Library/Bookshelf, Workspace/Workbench, Reader and Settings. This decision changes the future desktop implementation technology, not their approved product scope.

## Migration constraints

1. **Incremental / Strangler migration; no big bang rewrite.** Keep PySide6/QML as Legacy / Current Production UI until each replacement feature passes its own parity gate. Do not immediately remove QML.
2. **Protect Python Core.** Do not rewrite correctly functioning `src/domain/**`, `src/application/**` or `src/ports/**` merely to replace the UI. Reuse `src/infrastructure/**` where the audit confirms it is suitable.
3. **Parity before removal.** A legacy QML feature may be removed only after the corresponding React feature has Implementation + Tests + Visual / Behaviour Verification + Feature Parity Evidence and an authorized release decision.
4. **Large binary boundary.** Large comic images, Webtoon assets and model weights must not traverse ordinary JSON IPC or Base64 IPC. A later spike must choose image/tile transport and verify capacity, lifecycle and safety.
5. **Headless Python.** The final Python Core must be usable without the Qt GUI. Existing Qt imaging/rendering dependencies in infrastructure and bootstrap are `MIGRATION_AUDIT_REQUIRED`; this ADR does not choose their replacements or classify every dependency as unsuitable.
6. **SQLite authority.** Python Core alone owns persistent state writes. IPC contracts must preserve source-file safety, Managed Copy, human edits, Lock, current/pinned Revision and recoverable task state.
7. **Packaging evidence is baseline-specific.** The current Packaging/QML Release Gate closes Legacy Production Baseline requirements. Future Tauri + Python Sidecar packaging belongs to the Migration Milestone and needs new evidence; a PyInstaller/QML PASS cannot be copied into a Tauri packaging PASS.

## Governance and open decisions

The future migration is registered in [REBASELINE_PLAN](REBASELINE_PLAN.md) as **M2 — Desktop Architecture Migration, PLANNED / NOT_RELEASED**. Its logical order is Architecture Decision → Migration Discovery / Headless Audit → Python Core Decoupling → Contract / IPC → Tauri + React Skeleton → Incremental Feature Migration → Feature Parity → Packaging → Legacy QML Removal. This is a dependency sketch, not released implementation work. The only successor proposal is Headless & Qt Coupling Audit (`research / audit`). Its audit output will classify findings as `KEEP`, `DECOUPLE`, `REPLACE`, `LEGACY` or `UNVERIFIED`.

The proposed audit must inspect `src/domain`, `src/application`, `src/ports`, `src/infrastructure`, `src/bootstrap` and `src/ui`. It must trace PySide6 imports, QObject, QImage, QPdfWriter, Qt compositor/layout/font handling, Webtoon tile decoding, importing, bootstrap engine coupling, SQLite writer paths and headless entry feasibility. Its deliverable is an evidence-linked `KEEP` / `DECOUPLE` / `REPLACE` / `LEGACY` / `UNVERIFIED` matrix with risks and follow-up candidates; no code migration is authorized by that audit proposal.

- **USER_DECISION_REQUIRED — T3.2.1 investment:** finish the original Gate in full, or redefine a Legacy Closure boundary while retaining data safety and critical Release Evidence. Until the user decides otherwise through a separate authorized governance change, the original Gate remains in force.
- **USER_DECISION_REQUIRED — React UI ownership:** Qoder, Zcode or feature-based allocation. Current role definitions are unchanged. Qoder owns existing UI/UX and QML design, while Zcode owns independent features and long implementation work; either single-owner option concentrates continuity, while feature allocation shares delivery but needs tighter contract coordination. The user chooses in a later release decision.
- **DOCUMENT_DRIFT — remote:** on the registration base, `git remote -v` reports `origin=https://github.com/peakwheat-pixel/New-Manga.git`, while [09 collaboration](09_COLLABORATION.md) says “无 remote”. This ADR Task does not authorize editing that protocol; a later scoped correction should reconcile it.

Codex authors this registration. DeepSeek Harness should independently review the fixed documentation commit before Codex integrates it, checking decision fidelity, current/target separation, historical evidence, T3.2.1 preservation, implementation authorization, headless/DB/IPC/binary/parity boundaries and document links. Review approval does not itself release the successor audit or migration implementation.
