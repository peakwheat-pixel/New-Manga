# Roadmap

This file is a short navigation view. The authoritative roadmap, dependency
graph, acceptance boundaries and historical Task audit live in
[REBASELINE_PLAN.md](REBASELINE_PLAN.md). Live execution state lives in
[STATUS.md](STATUS.md).

## Future architecture milestone

[M2 — Desktop Architecture Migration](REBASELINE_PLAN.md#architecture-decision-and-future-migration-registration) is `PLANNED / NOT_RELEASED`. [AD-001](AD-001_TARGET_DESKTOP_ARCHITECTURE.md) records the accepted React + TypeScript + Tauri + Python Core target while PySide6/QML remains the current production UI. [M2-D1 Headless & Qt Coupling Audit](tasks/M2-D1.md) is `done` as read-only `research / audit` after [Codex Review](reviews/M2-D1-0a27a54.md); implementation remains unreleased. T3.2.1 retains its existing full Gate and owner.

## Current order

1. **T1.1.2, T1.1.1, T1.2.1, T2.1.1, T2.2.1, T3.1.1**: verified complete; fixed commits and evidence are in the authoritative Plan.
2. **[T3.2.1 — Windows Packaging & Release Gate](tasks/T3.2.1.md)**: current Active product Task; full Gate OPEN and AC3 BLOCKED pending the complete fixed-package workflow. ZCode's [REPAIR-13](tasks/T3.2.1-REPAIR-13.md) is `in_progress` after Delivery `2f18e78` / Handoff `df95ad1`; its R13-1 dialog-readability continuation starts from `33f2ff7`. No REPAIR-13 product change is integrated or independently approved. Its user-updated R13-AC5 requires a fixed-package EXE GUI run on the current Windows host with an isolated temporary data root; that child check is pending. The former Sandbox attempt remains historical evidence, and the parent T3.2.1 clean-Windows Gate is unchanged.

Historical phases and task ledgers remain in place for traceability; they do
not override the rebaseline.
