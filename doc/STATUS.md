# Current Development Status

状态：2026-10-25 起 DSH 接任 Lead / Architect / Integrator；授权与字节保留见[接管记录](GOVERNANCE_TAKEOVER_2026-10-25.md)。

## 当前 Task

- 当前 Task：[NSIS-INSTALLER-1](tasks/NSIS-INSTALLER-1.md) ready（NSIS 无签名安装包：per-user 安装/卸载/数据根保留；Reviewer dsh）。
- 最近完成：[AGPL-RELEASE-1](tasks/AGPL-RELEASE-1.md) `done`（`9948c3209`；models 包 AGPL-3.0 声明 + 全文随包 + 重打包验证）；[REGION-WORKBENCH-1](tasks/REGION-WORKBENCH-1.md) `done`（`60d087627`；工作台真实 region 读/改标/撤销/重渲染 + 只读门）。
- 登记表：[AD002-FOLLOWUPS-1](tasks/AD002-FOLLOWUPS-1.md) proposed（20 项遗留）。
- 更早：UIUX-V2-RUNTIME-NARROW-1（`e9a409927`）、UIUX-V2-RUNTIME-REALCORE-1、UIUX-V2-RUNTIME-1（`af421b9e6`）、DISPLAY-PERF-DECISION-1、REALCORE-2 `closed_with_limitations`。
- 发布线（绕开）：[GIT-CLEAN-PUBLICATION-1](tasks/GIT-CLEAN-PUBLICATION-1.md) `in_review`；Rust ISOLATION-1 `in_review` / CAPACITY-DESIGN-1 `ready`。
- 诊断/环境：DIAG-1 approved；CORE-ENV-2 proposed；FULL-AUDIT blocked；SIGNING-1 in_review。
- 更早：DESIGN-V2-IMPL-1 `done`（`e1fd738a7`）；插件 smoke、PRODUCT-IDENTITY-1 done；停用 agy、两 Rust Task 改 ZCode 审。

## 保留与已知限制

- WORKSPACE-CONSOLIDATION-1 `closed_with_limitations`（r212）；禁再清理/GC/prune。
- v1 收口（2026-10-21，HEAD `239b165c2`）：ACL 已修；source/packaged/前端/pytest/NSIS/Sandbox 实测过；签名待证书。
- ARCH-DOC-REBASELINE `closed_with_limitations`；P18 4/8；P20 6/7；DETECT-* / SEC-* / PDF-* / P09-AC3-* 等 `closed_with_limitations`。
- 台账 TASK_LEDGER（11 非终）；DIR-4/5=2/1000。
- 真机端到端：脚本化验收（run-i18 7/7、run-i36 10/10）。
- `?view=legacy` 保留历史容器；次级面板仍为令牌桥接；21 处非 gap 间距字面量与 2 处颜色字面量记 DESIGN-V2-IMPL-1 P2 债。

## Gate 与保留项

Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。P20 发布 Gate 已实测通过。此前授权只覆盖「干净源码快照新分支」push，不是 main 推送、不是产品发布验收。**2026-10-25 UIUX push 裁决：未执行**（main 含历史材料、干净快照 Gate 未清）。**2026-10-26 push 已执行（用户授权快照口径）**：`clean-snapshot-20261026`=`892b946e`；main 未推。

## 当前权威指针

- DAG 与节点状态：[REBASELINE_PLAN](REBASELINE_PLAN.md)（唯一权威）。
- 治理主线分支：`main`（见 [WORKSPACE_GOVERNANCE](WORKSPACE_GOVERNANCE.md)）。
- 恢复点：REALCORE-1 的脚本、命令、两版 exe SHA 见 `verification/UIUX-V2-RUNTIME-REALCORE-1/README.md`；UIUX-V2-RUNTIME-1 恢复点见其 Task 卡。
