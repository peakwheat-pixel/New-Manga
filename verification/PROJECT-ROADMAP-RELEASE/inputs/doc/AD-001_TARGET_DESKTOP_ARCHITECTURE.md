# AD-001 — Target Desktop Architecture
Status: ACCEPTED_TARGET_ARCHITECTURE. Decision authority: User. Target fixed by the 2026-09-28 user ruling. This document records the approved target; it does not release implementation work.

## Decision

The sole product target is **Windows + React + TypeScript + Tauri/Rust + Python Core + SQLite + Managed Copy**.

| Boundary | Responsibility and authority |
|---|---|
| React + TypeScript | UI presentation, interaction and frontend state projection. It does not directly access SQLite, arbitrary OS paths, models or domain business logic. |
| Tauri / Rust | Desktop shell, sidecar lifecycle, explicit IPC transport and system permission boundary. It does not own domain business logic or write persistent database state. |
| Python Core | Business/domain/application logic and authoritative persistence, including SQLite writes. The target Core must be usable without a Qt GUI. |
| SQLite | Persistent structured source of truth, written under Python Core authority. |
| Managed Copy | Project-managed working files protect original user sources, manual edits, locks, current/pinned revisions and recoverability. |

The product remains organized around four top-level areas: Bookshelf, Workbench, Reader and Settings. This decision fixes implementation architecture; it does not expand product scope.

## Migration and evidence boundaries

- **Legacy Production Baseline:** Python + PySide6/QML + SQLite describes the historical production state. Existing QML code, tests, mappings and packaging evidence remain historical reference only.
- **Migration intermediate state:** a stage-specific implementation state is not a second product target. Only a currently released Task may define its scope; historical QML-retention or parity wording does not release new Legacy work.
- **User final target:** React + TypeScript + Tauri/Rust + Python Core + SQLite + Managed Copy remains the only architecture for continued product evolution.
- React/WebView reaches Python Core through the explicit Tauri IPC boundary; it does not access the database, arbitrary filesystem paths or models directly.
- Large images, tiles and model weights must not pass through ordinary JSON/Base64 IPC. A current contract/Task must freeze the applicable transfer mechanism.
- Existing domain/application/ports logic should be preserved where suitable. Qt-coupled infrastructure requires an explicit headless/migration audit before replacement decisions.
- A PyInstaller/QML result cannot establish a Tauri/Python Core packaging result. New architecture claims require their own current Task and evidence.
- Architecture approval alone does not authorize implementation, migration, deletion or release. The current Plan and STATUS govern Task release and execution.

## Historical registration

The pre-Rebaseline AD-001 contained the original 2026-09-25 registration material, later QML migration/parity wording, an M2 release snapshot, open questions and obsolete Qoder role proposals. The complete pre-Rebaseline document is preserved verbatim for audit at [AD-001 pre-Rebaseline snapshot](../archive/history/2026-10-13/document-rebaseline/source/doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md). That snapshot is non-authoritative; its historical open-decision and ownership text is not current.
