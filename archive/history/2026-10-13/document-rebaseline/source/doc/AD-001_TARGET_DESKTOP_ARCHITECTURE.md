# AD-001 — Target Desktop Architecture

Status: **ACCEPTED_TARGET_ARCHITECTURE**. Registration-time M2 first-wave release snapshot: `M2_FIRST_WAVE_RELEASED` (2026-09-25; historical; live Task state is in [REBASELINE_PLAN](REBASELINE_PLAN.md)).

Decision owner: User. Registration owner: Codex. Registration base: `master` @ `1e8cb1157c987945316351728f725073b8b109f9` (2026-09-25). Registration-time independent review state: DeepSeek Harness, pending. This decision records the user's approved target; it does not approve any implementation Task.

> **Current target clarification (2026-10-12):** the frozen target is **Windows + React + TypeScript + Tauri/Rust + Python Core + SQLite + Managed Copy**. PySide6/QML is the Legacy Production Baseline and Migration Reference only. The historical registration snapshot below records decisions and ownership as of 2026-09-25; its QML retention wording, M2 release list, and Qoder assignments do not release current work or override the 2026-09-28 user architecture ruling, current `AGENTS.md` role rules, or live `REBASELINE_PLAN` / `STATUS`.

## Scope and authority

This Architecture Decision records target intent. [REBASELINE_PLAN](REBASELINE_PLAN.md) remains the sole planning source; [STATUS](STATUS.md) remains the live execution source. The existing [02 technical architecture](02_TECHNICAL_ARCHITECTURE_.md) and QML maps record the Legacy Production Baseline / Migration Reference; they are not the current target. Current architecture-document classifications are in [WORKSPACE_GOVERNANCE](WORKSPACE_GOVERNANCE.md). Historical Task, Handoff, Review and `verification/**` evidence is interpreted against its own PySide6/QML baseline and is not rewritten.

## Historical registration snapshot: CURRENT_REALITY (2026-09-25)

At registration time, the production program and T3.2.1 candidate used **Python + PySide6/QML + SQLite**. The statement that QML remained supported during migration, and the listed T3.2.1 Gate / REPAIR-13 ownership, describe that historical state only. They do not authorize new QML work or restore Qoder's project role. Existing PyInstaller/QML packaging evidence applies to the Legacy Production Baseline only. Current product direction and task release are governed by this AD's target intent plus live `AGENTS.md`, `REBASELINE_PLAN`, and `STATUS`.

## TARGET_INTENT and decision

The future desktop architecture is **React + TypeScript + Tauri + Python Core**, with SQLite as the persistent source of truth:

| Boundary | Authority and responsibility | Exclusions |
|---|---|---|
| React + TypeScript | Presentation: UI, interaction, Workspace, Library, Reader, Settings, Canvas/WebGL presentation and frontend state projection. | No direct SQLite access, OCR execution or domain logic. |
| Tauri / Rust | Desktop shell and system bridge: window, process, Python sidecar lifecycle, IPC transport, system integration and permission boundary. | Rust carries no domain business logic and is not a DB writer. |
| Python Core | Business, domain, application, ports, reusable infrastructure business adapters, SQLite persistence, OCR, detection, translation, inpainting, rendering business semantics, export, provider, task, revision and lock authority. | Core must ultimately run headless; UI/Qt GUI coupling needs audit before decoupling choices. |
| SQLite | Persistent source of truth, written under Python Core authority. | React and Rust cannot become independent DB writers. |

The four top-level product areas remain Library/Bookshelf, Workspace/Workbench, Reader and Settings. This decision changes the future desktop implementation technology, not their approved product scope.

## Migration boundaries and historical strategy

The Core, IPC, data-safety and binary-boundary constraints below record approved architecture boundaries. Any migration implementation or removal work still requires an explicitly released current Task. The original incremental-migration, QML-retention/parity and packaging-gate sequence is a 2026-09-25 strategy snapshot; it does not require new QML maintenance, define current release gates, or authorize Legacy work. Current authorization and ordering are read from `AGENTS.md`, `REBASELINE_PLAN`, and `STATUS`.

1. **Historical incremental migration strategy.** The original plan favored a Strangler migration over a big bang rewrite. This preserves the decision record; it neither makes PySide6/QML a current target nor releases new Legacy features.
2. **Protect Python Core.** Do not rewrite correctly functioning `src/domain/**`, `src/application/**` or `src/ports/**` merely to replace the UI. Reuse `src/infrastructure/**` where the audit confirms it is suitable.
3. **Historical parity gate.** The original migration plan required implementation, tests, visual/behaviour verification and parity evidence before removing corresponding QML features. A current removal Task must be explicitly released under the live Plan; this historical sequence is not a current Gate by itself.
4. **Large binary boundary.** Large comic images, Webtoon assets and model weights must not traverse ordinary JSON IPC or Base64 IPC. A later spike must choose image/tile transport and verify capacity, lifecycle and safety.
5. **Headless Python.** The final Python Core must be usable without the Qt GUI. Existing Qt imaging/rendering dependencies in infrastructure and bootstrap are `MIGRATION_AUDIT_REQUIRED`; this ADR does not choose their replacements or classify every dependency as unsuitable.
6. **SQLite authority.** Python Core alone owns persistent state writes. IPC contracts must preserve source-file safety, Managed Copy, human edits, Lock, current/pinned Revision and recoverable task state.
7. **Packaging evidence is baseline-specific.** A PyInstaller/QML PASS cannot be copied into a Tauri + Python Core packaging PASS; new architecture packaging needs its own current Task and evidence. References to a current QML Packaging Release Gate describe the registration-time legacy gate only.

## Governance and open decisions

> **Historical registration snapshot (2026-09-25):** the initial M2 release list, proposed audit, open questions, and Qoder ownership text below record the state at registration. They are not the live Task DAG or current role assignments. In particular, the Qoder UI ownership proposal is superseded by current `AGENTS.md`; no Qoder work is to be assigned.

The original registration marked M2 `PLANNED / NOT_RELEASED`. On 2026-09-25 the user separately authorized the bounded first wave: [M2-I1](tasks/M2-I1.md), [M2-I2](tasks/M2-I2.md), [M2-R1](tasks/M2-R1.md) and [M2-UI1](tasks/M2-UI1.md). [REBASELINE_PLAN](REBASELINE_PLAN.md) owns the current release state and [STATUS](STATUS.md) the execution state. The logical order remains Architecture Decision → Migration Discovery / Headless Audit → Python Core Decoupling → Contract / IPC → Tauri + React Skeleton → Incremental Feature Migration → Feature Parity → Packaging → Legacy QML Removal. Only the four named first-wave Tasks are released; contract/IPC, skeleton, product React UI, packaging and QML removal are not.

The proposed audit must inspect `src/domain`, `src/application`, `src/ports`, `src/infrastructure`, `src/bootstrap` and `src/ui`. It must trace PySide6 imports, QObject, QImage, QPdfWriter, Qt compositor/layout/font handling, Webtoon tile decoding, importing, bootstrap engine coupling, SQLite writer paths and headless entry feasibility. Its deliverable is an evidence-linked `KEEP` / `DECOUPLE` / `REPLACE` / `LEGACY` / `UNVERIFIED` matrix with risks and follow-up candidates; no code migration is authorized by that audit proposal.

- **USER_DECISION_REQUIRED — T3.2.1 investment:** finish the original Gate in full, or redefine a Legacy Closure boundary while retaining data safety and critical Release Evidence. Until the user decides otherwise through a separate authorized governance change, the original Gate remains in force.
- **USER_DECISION_REQUIRED — React UI ownership:** Qoder, Zcode or feature-based allocation. Current role definitions are unchanged. Qoder owns existing UI/UX and QML design, while Zcode owns independent features and long implementation work; either single-owner option concentrates continuity, while feature allocation shares delivery but needs tighter contract coordination. The user chooses in a later release decision.
- **DOCUMENT_DRIFT — remote:** on the registration base, `git remote -v` reports `origin=https://github.com/peakwheat-pixel/New-Manga.git`, while [09 collaboration](09_COLLABORATION.md) says “无 remote”. This ADR Task does not authorize editing that protocol; a later scoped correction should reconcile it.

Codex authors this registration. DeepSeek Harness should independently review the fixed documentation commit before Codex integrates it, checking decision fidelity, current/target separation, historical evidence, T3.2.1 preservation, implementation authorization, headless/DB/IPC/binary/parity boundaries and document links. Review approval does not itself release the successor audit or migration implementation.
