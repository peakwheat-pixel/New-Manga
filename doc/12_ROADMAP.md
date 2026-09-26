# Roadmap

This file is a short navigation view. The authoritative roadmap, dependency
graph, acceptance boundaries and historical Task audit live in
[REBASELINE_PLAN.md](REBASELINE_PLAN.md). Live execution state lives in
[STATUS.md](STATUS.md).

## Future architecture milestone

[M2 — Desktop Architecture Migration](REBASELINE_PLAN.md#architecture-decision-and-future-migration-registration) is `FIRST_WAVE_RELEASED / BOUNDED_IMPLEMENTATION`; M2-I1/I2/R1/UI1 and M2-D1 are integrated and done. T3.2.1 is `closed_with_limitations / SUPERSEDED_BY_M2`; its unfinished Legacy ACs do not block M2. The next authorized candidate is M2-C1 — Typed IPC Contract, currently `in_review` pending Qoder formal R3; M2-S1 remains unreleased.

## Current order

1. **T1.1.2, T1.1.1, T1.2.1, T2.1.1, T2.2.1, T3.1.1**: verified complete; fixed commits and evidence are in the authoritative Plan.
2. **[T3.2.1 — Windows Packaging & Release Gate](tasks/T3.2.1.md)**：`CLOSED_WITH_LIMITATIONS / SUPERSEDED_BY_M2`；原 AC6/AC8/AC9 `PARTIAL` 与 NOT_RUN 清单均保留。未完成 Legacy AC 不阻塞 M2。详见 [closure evidence](../verification/T3.2.1/legacy-closure-audit-20260926.md)。
3. **M2-C1 — Typed IPC Contract**：已授权候选，`in_review`；Qoder 对固定 head 的正式 R3 Review/evidence 待交付。C1 完成前不启动 M2-S1。

Historical phases and task ledgers remain in place for traceability; they do
not override the rebaseline.
