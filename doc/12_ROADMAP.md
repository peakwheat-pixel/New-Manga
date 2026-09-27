# Roadmap

This file is a short navigation view. The authoritative roadmap, dependency
graph, acceptance boundaries and historical Task audit live in
[REBASELINE_PLAN.md](REBASELINE_PLAN.md). Live execution state lives in
[STATUS.md](STATUS.md).

## Future architecture milestone

[M2 — Desktop Architecture Migration](REBASELINE_PLAN.md#architecture-decision-and-future-migration-registration) 为 FIRST_WAVE_RELEASED / BOUNDED_IMPLEMENTATION；M2 首波与 [M2-RC2](tasks/M2-RC2.md) F-03/F-05 切片均已集成。M2-RC1 merge=`3a246840`；M2-RC2 Codex integration=`88f972fe`，复跑 pytest 66、Cargo 20、Vitest 15、E2E GATE 10/10 / probe 13/13 与 TTL 探针全部 EXIT=0。Contract 1.1 blob=`fc359138` 未变；S1-B3/B6/B8=`NOT_RUN`、S1-B5=`UNVERIFIED`，产品级安全/打包声明仍受限。S1-B1=`PASS` 仅限单宿主/Rust 模拟表/一次性 body/非打包探针。T3.2.1 为 closed_with_limitations / SUPERSEDED_BY_M2；无 M2 successor 获得释放。独立 Legacy reliability 只读诊断 [DIAG-READING-EXPORT-001](tasks/DIAG-READING-EXPORT-001.md) 已按 §5.1 释放 `ready`，不授权实现。

## Current order

1. **T1.1.2, T1.1.1, T1.2.1, T2.1.1, T2.2.1, T3.1.1**: verified complete; fixed commits and evidence are in the authoritative Plan.
2. **[T3.2.1 — Windows Packaging & Release Gate](tasks/T3.2.1.md)**：`CLOSED_WITH_LIMITATIONS / SUPERSEDED_BY_M2`；原 AC6/AC8/AC9 `PARTIAL` 与 NOT_RUN 清单均保留。未完成 Legacy AC 不阻塞 M2。详见 [closure evidence](../verification/T3.2.1/legacy-closure-audit-20260926.md)。
3. **[M2-C1 — Typed IPC Contract](tasks/M2-C1.md)**：`done`；Owner=ZCode；Qoder Review=`0d73983a5e1f37f104c76d8bd4c70c6f98fa36f5`、DSH r3 Review=`96666bf063c8a514b3f8a58f78453a397dd93f75`，均 `APPROVED` 且绑定 `reviewed_head=b2377288680569dbee4e2299fd7dfae4de067c54`。Gate=`PASSED`，集成 merge=`c1765aa2`，Contract blob 保持固定。
4. **[M2-S1 — Large-Media Resource Channel Feasibility Spike](tasks/M2-S1.md)**：`done`；固定 base=`85a2aa7`，DeepSeek Harness Owner / Codex 非作者[复审](reviews/M2-S1-64c87d1.md) `APPROVED`，merge=`4103493`。研究给出条件性 A/B 建议；12 项产品验证与 7 项阈值决定仍未完成，产品实现未释放。
5. **[M2-S2 — Resource Channel Security Verification Spike](tasks/M2-S2.md)**：`done`（2026-09-26）；Owner=ZCode（delivery `d502aa5a`）、Reviewer=Antigravity（非作者；[Review](reviews/M2-S2-fbdf1bc2.md) `ea11d109` `approved`）、base=`67c3d56e`、integration=`bf1d1230`。原型层关闭 S1-B11（TOCTOU open-then-verify-from-handle，16/16）与 S1-B12（映射 ID 保密，8/8）；产品级保证保留 `UNVERIFIED`；§7 产品阈值已由用户授权代行[裁决](../verification/M2-S1/product-thresholds-ruling-67c3d56.md)，结果作为 Contract 修订与 runtime Task 输入。
6. **[M2-C2 — Typed IPC Contract Revision](tasks/M2-C2.md)**：`done`（2026-09-26）；Owner=ZCode（delivery `67f814ff`）、Reviewer=DeepSeek Harness（非作者；[Review](reviews/M2-C2-c18f273a.md) `approved`，4×P3 deferred）、base=`3f468e6e`、integration=`d574ec1e`。Contract 原位修订 `1.0`→`1.1`（blob `4b503a17`→`fc359138`）：T1–T7 阈值与安全语义以设计要求口径落约；既有保护语义零放松；不授权 runtime 实现。
7. **[M2-S3 — Tauri Asset Protocol Feasibility Probe](tasks/M2-S3.md)**：`done`；base=`90c3e459`，Owner=ZCode / DeepSeek Harness 非作者 Review=`approved` @`233d0901`；Codex 核对 Owner follow-up 至 `bcef79e7` 并集成于 `6799c73a`。S1-B1=`PASS` 仅限报告 §5/§6 边界，禁改产品路径为零；[集成核验](../verification/M2-S3/integration-bcef79e7/integration.md)。S1-B6 冷缓存测量由 runtime Task 执行。原改派记录：[reassignment-9b2d40c2](../verification/M2-S3/reassignment-9b2d40c2.md)。
8. **[M2-RC1 — Contract-Aligned Large-Media Resource Channel Runtime](tasks/M2-RC1.md)**：`done`；base=`2dca20cd`，reviewed head=`2f6a31cd`（DeepSeek Harness round-4 `approve`），Owner evidence tip=`ce3c3771`，Codex merge=`3a246840`。Codex 复跑四套验证：pytest 43、Cargo 12、Vitest 8、E2E 10/10 ×2，均 exit 0；Contract blob=`fc359138` 不变。集成证据：[integration](../verification/M2-RC1/integration-2f6a31cd/integration.md)。
9. **[M2-RC2 — Resource Channel Command Surface and Sidecar Boundary Hardening](tasks/M2-RC2.md)**：done；base=`22a2c2bf`，FIX/reviewed head=`eac5cb3e`，DSH Review=approved，Codex integration=`88f972fe`；Codex 集成复验及 SHA256 导入清单见 [integration record](../verification/M2-RC2/integration-88f972fe/integration.md)。No M2 successor is released.

Separate Legacy reliability backlog：[DIAG-READING-EXPORT-001](tasks/DIAG-READING-EXPORT-001.md) 为 `ready` 的只读诊断，由 DeepSeek Harness 执行、Codex 非作者 Review；固定 base=`83de13df`，需先通过环境启动 Gate。释放记录：[release-83de13df](../verification/DIAG-READING-EXPORT-001/release-83de13df.md)。

Historical phases and task ledgers remain in place for traceability; they do
not override the rebaseline.
