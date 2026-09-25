# Roadmap

This file is a short navigation view. The authoritative roadmap, dependency
graph, acceptance boundaries and historical Task audit live in
[REBASELINE_PLAN.md](REBASELINE_PLAN.md). Live execution state lives in
[STATUS.md](STATUS.md).

## Future architecture milestone

[M2 — Desktop Architecture Migration](REBASELINE_PLAN.md#architecture-decision-and-future-migration-registration) is `PLANNED / NOT_RELEASED`. [AD-001](AD-001_TARGET_DESKTOP_ARCHITECTURE.md) records the accepted React + TypeScript + Tauri + Python Core target while PySide6/QML remains the current production UI. [M2-D1 Headless & Qt Coupling Audit](tasks/M2-D1.md) is `done` as read-only `research / audit` after [Codex Review](reviews/M2-D1-0a27a54.md); implementation remains unreleased. T3.2.1 retains its existing full Gate and owner.

## Current order

1. **T1.1.2, T1.1.1, T1.2.1, T2.1.1, T2.2.1, T3.1.1**: verified complete; fixed commits and evidence are in the authoritative Plan.
2. **[T3.2.1 — Windows Packaging & Release Gate](tasks/T3.2.1.md)**: current Active product Task; full Gate OPEN and parent AC3 BLOCKED pending the complete fixed-package workflow. ZCode's [REPAIR-13](tasks/T3.2.1-REPAIR-13.md) is `in_review` at Delivery `aed0094` / Handoff and evidence head `66a13f8`; DeepSeek Harness Review is `APPROVE_WITH_CONDITIONS`, child AC4=PASS, and child local fixed-package AC1–AC5 are accepted. ZCode has one evidence-only F-1/F-3 correction pending before Codex product integration. [REPAIR-14](tasks/T3.2.1-REPAIR-14.md) is proposed for Antigravity to investigate F-13-3 after REPAIR-13 closes; implementation is not released. Parent Gate requirements remain unchanged.

Historical phases and task ledgers remain in place for traceability; they do
not override the rebaseline.
