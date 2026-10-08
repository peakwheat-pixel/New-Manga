# Roadmap

当前工作：P08设计范围已冻结；DSH R7正式批准fixed head fe222464，Codex集成Gate通过，P08=approved、Task收口提交待完成；P03为下一候选但未创建/释放；最新恢复点见verification/P08/RESUME.md。

## 当前整体路线（2026-10-08，PLAN_ONLY）

最新人员裁决：Qoder退出，未来UI/UX设计及React/Tauri实现由ZCode主责，DSH非作者审查，Codex契约/集成；额度接管候选为ZCode、Antigravity。历史交付中的Qoder署名保留。

权威排期见 Plan顶部P01–P21候选任务路线、中文分层依赖图、代码深读与完整台账、额度中断恢复材料。当前P08=approved：DSH R7已批准fe222464，Codex集成Gate通过，Task收口提交待完成；P03仍未创建/释放。完整产品条件主链为：范围/parity冻结→真实导入/凭据/长任务契约→书架/后台Pipeline→工作台/设置/阅读导出→真实质量→整体E2E→Windows发布。基础Reader已由D1解冻，跨页/缩略图延期。

下方2026-09早期导航保留历史，不覆盖本段或Plan；其中旧“ready/planning only”任务多已由后继完成，不能作为当前待办。

This file is a short navigation view. The authoritative roadmap, dependency
graph, acceptance boundaries and historical Task audit live in
[REBASELINE_PLAN.md](REBASELINE_PLAN.md). Live execution state lives in
[STATUS.md](STATUS.md).

## Future architecture milestone

[M2 — Desktop Architecture Migration](REBASELINE_PLAN.md#architecture-decision-and-future-migration-registration) 为 FIRST_WAVE_RELEASED / BOUNDED_IMPLEMENTATION；M2 首波、[M2-RC2](tasks/M2-RC2.md) F-03/F-05 切片与 successor [M2-AC1](tasks/M2-AC1.md) 均已集成。M2-RC1 merge=`3a246840`；M2-RC2 integration=`88f972fe`；M2-AC1 Codex merge=`f162193b`（base=`7db0e7b6`，Owner=`51f70ed1`，DSH r4 static Review=`approved` @`d102bf70`）。M2-AC1 集成复跑 pytest 4、Cargo 26、Vitest 19、E2E 45/45 及全仓 pytest 1316 passed/11 skipped，全部 EXIT=0；F-008 仅追认 9 个测试模式 Tauri ACL 机制文件。其他 M2 Acceptance Backlog 行仍未登记。Contract 1.1 blob=`fc359138` 未变；S1-B3/B6/B8=`NOT_RUN`、S1-B5=`UNVERIFIED`，产品级安全/打包声明仍受限。S1-B1=`PASS` 仅限单宿主/Rust 模拟表/一次性 body/非打包探针。T3.2.1 为 closed_with_limitations / SUPERSEDED_BY_M2。独立 Legacy reliability 诊断 [DIAG-READING-EXPORT-001](tasks/DIAG-READING-EXPORT-001.md) 已 `done`（integration=`e0a0e784`）；症状 A 修复 [FIX-A](tasks/DIAG-READING-EXPORT-001-FIX-A.md) `done`（integration=`a8b94df1`，DSH r2 approved，测试等待语义）；症状 B 修复 [FIX-B](tasks/DIAG-READING-EXPORT-001-FIX-B.md) `done`（`9c9c9087`）；生产接线 [FIX-C](tasks/DIAG-READING-EXPORT-001-FIX-C.md) `done`（`0f2e9e31`，DSH r6 approved，零 QML）。

自 2026-09-28 用户裁决起，后续 Task、缺陷和验收只在 React + TypeScript + Tauri + Python Core + SQLite 新架构推进。Legacy PySide6/QML 台账只作历史追溯，不再生成工作项；相关产品行为统一转写为 M2 需求。

## Historical order（早期迁移快照，无当前排期效力）

1. **T1.1.2, T1.1.1, T1.2.1, T2.1.1, T2.2.1, T3.1.1**: verified complete; fixed commits and evidence are in the authoritative Plan.
2. **[T3.2.1 — Windows Packaging & Release Gate](tasks/T3.2.1.md)**：`CLOSED_WITH_LIMITATIONS / SUPERSEDED_BY_M2`；原 AC6/AC8/AC9 `PARTIAL` 与 NOT_RUN 清单均保留。未完成 Legacy AC 不阻塞 M2。详见 [closure evidence](../verification/T3.2.1/legacy-closure-audit-20260926.md)。
3. **[M2-C1 — Typed IPC Contract](tasks/M2-C1.md)**：`done`；Owner=ZCode；Qoder Review=`0d73983a5e1f37f104c76d8bd4c70c6f98fa36f5`、DSH r3 Review=`96666bf063c8a514b3f8a58f78453a397dd93f75`，均 `APPROVED` 且绑定 `reviewed_head=b2377288680569dbee4e2299fd7dfae4de067c54`。Gate=`PASSED`，集成 merge=`c1765aa2`，Contract blob 保持固定。
4. **[M2-S1 — Large-Media Resource Channel Feasibility Spike](tasks/M2-S1.md)**：`done`；固定 base=`85a2aa7`，DeepSeek Harness Owner / Codex 非作者[复审](reviews/M2-S1-64c87d1.md) `APPROVED`，merge=`4103493`。研究给出条件性 A/B 建议；T1–T7 后由 M2-S2/C2 裁决并落约，未完成的产品级验证边界继续保留。
5. **[M2-S2 — Resource Channel Security Verification Spike](tasks/M2-S2.md)**：`done`（2026-09-26）；Owner=ZCode（delivery `d502aa5a`）、Reviewer=Antigravity（非作者；[Review](reviews/M2-S2-fbdf1bc2.md) `ea11d109` `approved`）、base=`67c3d56e`、integration=`bf1d1230`。原型层关闭 S1-B11（TOCTOU open-then-verify-from-handle，16/16）与 S1-B12（映射 ID 保密，8/8）；产品级保证保留 `UNVERIFIED`；§7 产品阈值已由用户授权代行[裁决](../verification/M2-S1/product-thresholds-ruling-67c3d56.md)，结果作为 Contract 修订与 runtime Task 输入。
6. **[M2-C2 — Typed IPC Contract Revision](tasks/M2-C2.md)**：`done`（2026-09-26）；Owner=ZCode（delivery `67f814ff`）、Reviewer=DeepSeek Harness（非作者；[Review](reviews/M2-C2-c18f273a.md) `approved`，4×P3 deferred）、base=`3f468e6e`、integration=`d574ec1e`。Contract 原位修订 `1.0`→`1.1`（blob `4b503a17`→`fc359138`）：T1–T7 阈值与安全语义以设计要求口径落约；既有保护语义零放松；不授权 runtime 实现。
7. **[M2-S3 — Tauri Asset Protocol Feasibility Probe](tasks/M2-S3.md)**：`done`；base=`90c3e459`，Owner=ZCode / DeepSeek Harness 非作者 Review=`approved` @`233d0901`；Codex 核对 Owner follow-up 至 `bcef79e7` 并集成于 `6799c73a`。S1-B1=`PASS` 仅限报告 §5/§6 边界，禁改产品路径为零；[集成核验](../verification/M2-S3/integration-bcef79e7/integration.md)。S1-B6 冷缓存测量由 runtime Task 执行。原改派记录：[reassignment-9b2d40c2](../verification/M2-S3/reassignment-9b2d40c2.md)。
8. **[M2-RC1 — Contract-Aligned Large-Media Resource Channel Runtime](tasks/M2-RC1.md)**：`done`；base=`2dca20cd`，reviewed head=`2f6a31cd`（DeepSeek Harness round-4 `approve`），Owner evidence tip=`ce3c3771`，Codex merge=`3a246840`。Codex 复跑四套验证：pytest 43、Cargo 12、Vitest 8、E2E 10/10 ×2，均 exit 0；Contract blob=`fc359138` 不变。集成证据：[integration](../verification/M2-RC1/integration-2f6a31cd/integration.md)。
9. **[M2-RC2 — Resource Channel Command Surface and Sidecar Boundary Hardening](tasks/M2-RC2.md)**：done；base=`22a2c2bf`，FIX/reviewed head=`eac5cb3e`，DSH Review=approved，Codex integration=`88f972fe`；Codex 集成复验及 SHA256 导入清单见 [integration record](../verification/M2-RC2/integration-88f972fe/integration.md)。
10. **[M2-AC1 — end-to-end acceptance on the M2 baseline](tasks/M2-AC1.md)**：`done`；fixed base=`7db0e7b6`，Owner tip=`51f70ed1`，DSH r4 `approved` @`d102bf70`（静态），Codex merge=`f162193b`。Codex 独立复跑 Core/Cargo/Vitest/E2E 全通过；[integration evidence](../verification/M2-AC1/integration-51f70ed1/integration.md)。

### Historical released Task and follow-ups（已由后继状态取代）

1. [DIAG-M2-REGIONLESS-LOCK-CHANGED-001](tasks/DIAG-M2-REGIONLESS-LOCK-CHANGED-001.md)：`ready / AWAITING_EXTERNAL_DISPATCH`；Owner=DeepSeek Harness，Reviewer=Antigravity，Integrator=Codex，fixed base=`5789b30b`。只诊断，不改产品代码。
2. `M2-P1 Regionless Detection Fan-out and Guard Rebinding`：planning only；等待 DIAG 根因与最小范围，不得提前实施。
3. `M2-IPC1 Production Core Lifecycle + Read-only Library Vertical Slice`：planning only；由 Codex 冻结 production IPC seam 后建议 Antigravity 实现、DSH Review。
4. `M2-AC2 Data Integrity Acceptance`：planning only；等待 P1 与 IPC1，以真实 production seam 验收 source hash、Managed Copy、人工修改、Lock 和 current/pinned Revision。

其余 Acceptance Backlog、建议分工与 Mermaid 流程见 [权威 Plan](REBASELINE_PLAN.md#2026-09-28-全量任务盘点与当前流程)。未释放节点不授予写权限。

Separate Legacy reliability backlog：[DIAG-READING-EXPORT-001](tasks/DIAG-READING-EXPORT-001.md) 已 `done`（2026-09-28；integration=`e0a0e784`）。症状 A 修复 [FIX-A](tasks/DIAG-READING-EXPORT-001-FIX-A.md) 已 `done`（integration=`a8b94df1`；DSH 双轮 Review，R2 `approved`；测试等待语义——终态信号消费者等待信号到达，判别探针旧谓词 324/400 miss → 新谓词 0 miss + 故障注入检出）；症状 B 修复 [FIX-B](tasks/DIAG-READING-EXPORT-001-FIX-B.md) `done`（`9c9c9087`）；生产接线 [FIX-C](tasks/DIAG-READING-EXPORT-001-FIX-C.md) `done`（`0f2e9e31`；DSH 六轮 Review R6 `approved`；纯 Python bootstrap 接线：离开读者页 `closeReader` + `aboutToQuit`，零 QML）。诊断家族（DIAG+FIX-A+FIX-B+FIX-C）全部 `done`，历史 reading_export flaky 两机制均已修复；诊断 U3（真实全仓触发条件）为唯一未决知识项。集成核验：[FIX-A integration-a8b94df1](../verification/DIAG-READING-EXPORT-001-FIX-A/integration-a8b94df1/integration.md)。

Historical phases and task ledgers remain in place for traceability; they do
not override the rebaseline.
