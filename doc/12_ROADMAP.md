# Roadmap

This file is a short navigation view. The authoritative roadmap, dependency
graph, acceptance boundaries and historical Task audit live in
[REBASELINE_PLAN.md](REBASELINE_PLAN.md). Live execution state lives in
[STATUS.md](STATUS.md).

## Future architecture milestone

[M2 — Desktop Architecture Migration](REBASELINE_PLAN.md#architecture-decision-and-future-migration-registration) 为 FIRST_WAVE_RELEASED / BOUNDED_IMPLEMENTATION；M2-I1/I2/R1/UI1、M2-D1 与 M2-C1 均已完成。T3.2.1 为 closed_with_limitations / SUPERSEDED_BY_M2。后续 [M2-S1](tasks/M2-S1.md) 仅完成 Codex 范围登记，`proposed / NOT_RELEASED`；不代表大媒体资源通道或 IPC runtime 已实现。

## Current order

1. **T1.1.2, T1.1.1, T1.2.1, T2.1.1, T2.2.1, T3.1.1**: verified complete; fixed commits and evidence are in the authoritative Plan.
2. **[T3.2.1 — Windows Packaging & Release Gate](tasks/T3.2.1.md)**：`CLOSED_WITH_LIMITATIONS / SUPERSEDED_BY_M2`；原 AC6/AC8/AC9 `PARTIAL` 与 NOT_RUN 清单均保留。未完成 Legacy AC 不阻塞 M2。详见 [closure evidence](../verification/T3.2.1/legacy-closure-audit-20260926.md)。
3. **[M2-C1 — Typed IPC Contract](tasks/M2-C1.md)**：`done`；Owner=ZCode；Qoder Review=`0d73983a5e1f37f104c76d8bd4c70c6f98fa36f5`、DSH r3 Review=`96666bf063c8a514b3f8a58f78453a397dd93f75`，均 `APPROVED` 且绑定 `reviewed_head=b2377288680569dbee4e2299fd7dfae4de067c54`。Gate=`PASSED`，集成 merge=`c1765aa2`，Contract blob 保持固定；M2-S1=`NOT_RELEASED`。
4. **[M2-S1 — Large-Media Resource Channel Feasibility Spike](tasks/M2-S1.md)**：仅范围登记；固定候选 base=`0c2e202c6aded5326bec9a5460b5142155db0240`，建议 DeepSeek Harness Owner / Codex 非作者 Reviewer；`proposed / NOT_RELEASED`。研究执行须另行释放并创建专属工作区。

Historical phases and task ledgers remain in place for traceability; they do
not override the rebaseline.
