# Roadmap

This file is a short navigation view. The authoritative roadmap, dependency
graph, acceptance boundaries and historical Task audit live in
[REBASELINE_PLAN.md](REBASELINE_PLAN.md). Live execution state lives in
[STATUS.md](STATUS.md).

## Future architecture milestone

[M2 — Desktop Architecture Migration](REBASELINE_PLAN.md#architecture-decision-and-future-migration-registration) 为 FIRST_WAVE_RELEASED / BOUNDED_IMPLEMENTATION；M2-I1/I2/R1/UI1、M2-D1、[M2-C1](tasks/M2-C1.md) 契约、[M2-S1](tasks/M2-S1.md) 研究、[M2-S2](tasks/M2-S2.md) 安全验证与 [M2-C2](tasks/M2-C2.md) 契约修订均已完成。T3.2.1 为 closed_with_limitations / SUPERSEDED_BY_M2。大媒体资源通道与 IPC runtime 尚未实现。

## Current order

1. **T1.1.2, T1.1.1, T1.2.1, T2.1.1, T2.2.1, T3.1.1**: verified complete; fixed commits and evidence are in the authoritative Plan.
2. **[T3.2.1 — Windows Packaging & Release Gate](tasks/T3.2.1.md)**：`CLOSED_WITH_LIMITATIONS / SUPERSEDED_BY_M2`；原 AC6/AC8/AC9 `PARTIAL` 与 NOT_RUN 清单均保留。未完成 Legacy AC 不阻塞 M2。详见 [closure evidence](../verification/T3.2.1/legacy-closure-audit-20260926.md)。
3. **[M2-C1 — Typed IPC Contract](tasks/M2-C1.md)**：`done`；Owner=ZCode；Qoder Review=`0d73983a5e1f37f104c76d8bd4c70c6f98fa36f5`、DSH r3 Review=`96666bf063c8a514b3f8a58f78453a397dd93f75`，均 `APPROVED` 且绑定 `reviewed_head=b2377288680569dbee4e2299fd7dfae4de067c54`。Gate=`PASSED`，集成 merge=`c1765aa2`，Contract blob 保持固定。
4. **[M2-S1 — Large-Media Resource Channel Feasibility Spike](tasks/M2-S1.md)**：`done`；固定 base=`85a2aa7`，DeepSeek Harness Owner / Codex 非作者[复审](reviews/M2-S1-64c87d1.md) `APPROVED`，merge=`4103493`。研究给出条件性 A/B 建议；12 项产品验证与 7 项阈值决定仍未完成，产品实现未释放。
5. **[M2-S2 — Resource Channel Security Verification Spike](tasks/M2-S2.md)**：`done`（2026-09-26）；Owner=ZCode（delivery `d502aa5a`）、Reviewer=Antigravity（非作者；[Review](reviews/M2-S2-fbdf1bc2.md) `ea11d109` `approved`）、base=`67c3d56e`、integration=`bf1d1230`。原型层关闭 S1-B11（TOCTOU open-then-verify-from-handle，16/16）与 S1-B12（映射 ID 保密，8/8）；产品级保证保留 `UNVERIFIED`；§7 产品阈值已由用户授权代行[裁决](../verification/M2-S1/product-thresholds-ruling-67c3d56.md)，结果作为 Contract 修订与 runtime Task 输入。
6. **[M2-C2 — Typed IPC Contract Revision](tasks/M2-C2.md)**：`done`（2026-09-26）；Owner=ZCode（delivery `67f814ff`）、Reviewer=DeepSeek Harness（非作者；[Review](reviews/M2-C2-c18f273a.md) `approved`，4×P3 deferred）、base=`3f468e6e`、integration=`d574ec1e`。Contract 原位修订 `1.0`→`1.1`（blob `4b503a17`→`fc359138`）：T1–T7 阈值与安全语义以设计要求口径落约；既有保护语义零放松；不授权 runtime 实现。

Historical phases and task ledgers remain in place for traceability; they do
not override the rebaseline.
