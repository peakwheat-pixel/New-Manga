# Current Development Status

状态：2026-10-25 起 DSH 接任 Lead / Architect / Integrator；授权与字节保留见[接管记录](GOVERNANCE_TAKEOVER_2026-10-25.md)。
## 当前程序（2026-10-30）
- **V11R 程序 ACTIVE**：[V11R_PROGRAM](V11R_PROGRAM.md)（V1.1 整改 + 全新 Avalonia UI/UX + Theme Studio 重建的唯一 DAG）；契约 [V11R_AVALONIA_CONTRACT](plan/V11R_AVALONIA_CONTRACT.md)。
- 当前 Task：`V11R-BASELINE-1` done（审计受理、设计基线合并 `c78db96ed`/`c73239999`、DAG 建立）。进行中：`V11R-D-1`（Design System）、`V11R-A-1/A-2/A-3`（服务层与契约）、`V11R-C-RESEARCH-1`（主题框架研究）、`V11R-F0-1`（Region 写面）。
- 基线：`main@eaacd872d` + 设计合并；`dotnet build NewManga.sln` 0W/0E 实测；**不 push 远端**。
- 最近完成（上一程序）：READER-LIBRARY-WIRE-1 done（阅读器/沉浸，复核收口）。0.1.1 未签名发布。

## 当前 Task（上一程序，历史）
- 历史 Task：[NEW-MANGA-V1-FULL-AUDIT](tasks/NEW-MANGA-V1-FULL-AUDIT.md) blocked（历史审计，素材不传播）。
- 最近完成（新增）：[UPGRADE-LEGACY-LAYOUT-1](tasks/UPGRADE-LEGACY-LAYOUT-1.md) `done`（集成 `098c60381`；3 轮独立 Review PASS；单测 12/12、全量 2612P）。
- 最近完成：[LEGACY-SHELL-ARCHIVE-1](tasks/LEGACY-SHELL-ARCHIVE-1.md) `closed_with_limitations`（集成 `7d4c7764c`；公开 CI `40830315601` 全绿 17/17）；[CUDA-PACKAGE-DECISION-1](tasks/CUDA-PACKAGE-DECISION-1.md) `done`（defer）；[PUBLIC-RELEASE-P0-1](tasks/PUBLIC-RELEASE-P0-1.md) `done`（`cd58c50fe`）；[SIGNPATH-OSS-SIGNING-1](tasks/SIGNPATH-OSS-SIGNING-1.md) `done`（`f632ee39c`）。
- 更早：UIUX-V2-RUNTIME-NARROW-1（`e9a409927`）、UIUX-V2-RUNTIME-REALCORE-1、UIUX-V2-RUNTIME-1（`af421b9e6`）、DISPLAY-PERF-DECISION-1、REALCORE-2 `closed_with_limitations`。
- 发布线（绕开）：[GIT-CLEAN-PUBLICATION-1](tasks/GIT-CLEAN-PUBLICATION-1.md) `in_review`；Rust ISOLATION-1 `in_review` / CAPACITY-DESIGN-1 `ready`。
- 诊断/环境：DIAG-1 approved；CORE-ENV-2 proposed；FULL-AUDIT blocked；SIGNING-1 in_review。
- 更早：DESIGN-V2-IMPL-1 `done`（`e1fd738a7`）；插件 smoke、PRODUCT-IDENTITY-1 done；停用 agy、两 Rust Task 改 ZCode 审。
## 保留与已知限制
- WORKSPACE-CONSOLIDATION-1 `closed_with_limitations`（r212）；禁再清理/GC/prune。
- v1 收口（2026-10-21，HEAD `239b165c2`）：ACL 已修；source/packaged/前端/pytest/NSIS/Sandbox 实测过；签名待证书。
- ARCH-DOC-REBASELINE `closed_with_limitations`；P18 4/8；P20 6/7；DETECT-* / SEC-* / PDF-* / P09-AC3-* 等 `closed_with_limitations`。
- 台账 TASK_LEDGER（10 非终）；DIR-4/5=2/1000。
- 真机端到端：脚本化验收（run-i18 7/7、run-i36 10/10）。
- `?view=legacy` 保留历史容器；次级面板仍为令牌桥接；21 处非 gap 间距字面量与 2 处颜色字面量记 DESIGN-V2-IMPL-1 P2 债。
## Gate 与保留项
Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。P20 发布 Gate 已实测通过。此前授权只覆盖「干净源码快照新分支」push，不是 main 推送、不是产品发布验收。**2026-10-25 UIUX push 裁决：未执行**（main 含历史材料、干净快照 Gate 未清）。**2026-10-26 push 已执行（用户授权快照口径）**：`clean-snapshot-20261026`=`892b946e`；main 未推。
## 当前权威指针
- DAG 与节点状态：[REBASELINE_PLAN](REBASELINE_PLAN.md)（唯一权威）。
- 治理主线分支：`main`（见 [WORKSPACE_GOVERNANCE](WORKSPACE_GOVERNANCE.md)）。
- 恢复点：REALCORE-1 的脚本、命令、两版 exe SHA 见 `verification/UIUX-V2-RUNTIME-REALCORE-1/README.md`；UIUX-V2-RUNTIME-1 恢复点见其 Task 卡。


