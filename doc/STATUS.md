# Current Development Status

状态：2026-10-25 起 DSH 接任 Lead / Architect / Integrator；授权与字节保留见[接管记录](GOVERNANCE_TAKEOVER_2026-10-25.md)。

## 当前 Task

- 当前 Task：[GRANT-ISSUER-1](tasks/GRANT-ISSUER-1.md) `ready`（待作者 rebase 后集成）；并行 RUN-BINDING-FIX-1、CORE-PIPELINE-FIX-1。
- 已收口：[DISPLAY-PERF-DECISION-1](tasks/DISPLAY-PERF-DECISION-1.md) `done`。
- 最近完成：[UIUX-V2-RUNTIME-NARROW-1](tasks/UIUX-V2-RUNTIME-NARROW-1.md) `done`（根因 `.nm-app min-width:1024`；900 档四页 900/900；`e9a409927`）。
- 前序：REALCORE-2 `closed_with_limitations`（run-i36 10/10）。
- 最近完成：[UIUX-V2-RUNTIME-REALCORE-1](tasks/UIUX-V2-RUNTIME-REALCORE-1.md) `done`（真实 Tauri+Core 7/7；修 P0 中文落库乱码 + P1 死按钮；ZCode r1 approved）。DAG 无 READY。
- 前序：[UIUX-V2-RUNTIME-1](tasks/UIUX-V2-RUNTIME-1.md) `done`（四页真实 IPC + 设置页 + 单一 UI；集成 `af421b9e6`）。
- 发布线（绕开）：[GIT-CLEAN-PUBLICATION-1](tasks/GIT-CLEAN-PUBLICATION-1.md) `in_review`（push-gate approved；AC4/AC5 未过）。
- Rust：[ISOLATION-1](tasks/GIT-CLEAN-RUST-ISOLATION-1.md) `in_review`（r2 blocked 保留）；[CAPACITY-DESIGN-1](tasks/GIT-CLEAN-RUST-CAPACITY-DESIGN-1.md) `ready`。
- 诊断/环境：DIAG-1 approved；CORE-ENV-2 proposed；FULL-AUDIT blocked；SIGNING-1 in_review。
- 更早：DESIGN-V2-IMPL-1 `done`（`e1fd738a7`）；插件 smoke done；PRODUCT-IDENTITY-1 done。Reviewer 改派：停用 agy，两 Rust Task 改 ZCode 审。


## 保留与已知限制

- WORKSPACE-CONSOLIDATION-1 `closed_with_limitations`（r212）；禁再清理/GC/prune。
- v1 收口（2026-10-21，HEAD `239b165c2`）：ACL 已修；source/packaged/前端/pytest/NSIS/Sandbox 各线实测过；签名待证书。
- ARCH-DOC-REBASELINE `closed_with_limitations`；P18 4/8；P20 6/7；DETECT-* / SEC-* / PDF-* / P09-AC3-* 等 `closed_with_limitations`。
- 台账 TASK_LEDGER（8 非终）；DIR-4/5=2/1000。
- 真机端到端：脚本化验收（run-i18 7/7、run-i36 10/10）。
- `?view=legacy` 保留历史容器；次级面板仍为令牌桥接；21 处非 gap 间距字面量与 2 处颜色字面量记 DESIGN-V2-IMPL-1 P2 债。

## Gate 与保留项

Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。P20 发布 Gate 已实测通过。此前授权只覆盖「干净源码快照新分支」push，不是 main 推送、不是产品发布验收。**2026-10-25 UIUX push 裁决：未执行**（main 含历史材料、干净快照 Gate 未清）。**2026-10-26 push 已执行（用户授权快照口径）**：`clean-snapshot-20261026`=`892b946e`；main 未推。

## 当前权威指针

- DAG 与节点状态：[REBASELINE_PLAN](REBASELINE_PLAN.md)（唯一权威）。
- 治理主线分支：`main`（见 [WORKSPACE_GOVERNANCE](WORKSPACE_GOVERNANCE.md)）。
- 恢复点：REALCORE-1 的脚本、命令、两版 exe SHA 见 `verification/UIUX-V2-RUNTIME-REALCORE-1/README.md`；UIUX-V2-RUNTIME-1 恢复点见其 Task 卡。


