# Project Rebaseline Plan — 唯一 DAG

运行以 [STATUS](STATUS.md) 为准；目标架构 [AD-002](AD-002_TARGET_DESKTOP_ARCHITECTURE.md)（AD-001 已取代）。

## 当前 DAG

|节点/目标|依赖|状态|
|---|---|---|
|FEA-CONTRACT-WRAP-1|FEA-C14-DRAFT|done（L-3 Errata + PLAN 预算；R2 approved `6cfe7ab92`）|
|FEA-C11-PREREQ-1|FEA-C10-DRAFT|approved（U-09 前置登记：L-1/L-2/L-5 → 候选 Task 前置与 AC；r1 approved；待集成收口）|
|FEA-01-FREEZE-1|FEA-C11-PREREQ-1|**done**（FEA-01 冻结 v2，pin `0370c189…`；集成 `bf1c8eb00`；15/15）|
|FEA-02-CORE|FEA-01-FREEZE-1|**done**（集成 `135479270`；delivery `5efb8f58c`；r1 approved）|
|FEA-00A-PREP-1|FEA-02-CORE|**done**（集成 `aec780362`；评估文档 v2 + R1 approved）|
|FEA-00A-IMPL-1|FEA-00A-PREP-1|**done**（集成 `e0ba29eba`；delivery `007094517`；实现复核 r1 approved P0/P1=0；AC7b 限制登记）|
|FEA-03|FEA-00A-IMPL-1、FEA-01-FREEZE-1|**done**（集成 `76d947923`；实现复核 r5 approved P0/P1=0；范围 v6 + C-13 v6 UNFREEZE approved；AC11b V19 组合 deferral）|
|FEA-04|FEA-02-CORE、FEA-03|**done**（集成 `f4d8a32ec`；实现复核 r3 approved P0/P1=0；sln 931/0/60；AC11b 无）|
|FEA-04b|FEA-01|**done**（设计基线 `fluent-v1.0.0` FROZEN；r5 approved；AC5 用户确认由 DSH 裁决替代）|
|FEA-05-WIRE-1|FEA-03、FEA-04|**done**（Draft 命令面 wire C078–C083；实现复核 impl-r3 approved；全量 931/0/60）|
|FEA-05-PORT-1|FEA-05-WIRE-1|**done**（Draft 端口面 + registry + Region 契约 v1.6；impl r3 approved；949/0/57）|
|FEA-06|FEA-04b、FEA-05-PORT-1、FEA-06-PREREQ-1/2|**done**（集成 `b26840acd`；scope-r3 + impl-r2 approved；全量 **1034/0/57**；AC8–AC10 MET，AC1–AC7 residual 转 FEA-06-RESIDUAL-1）|
|FEA-07|FEA-00A-IMPL-1、FEA-04、FEA-05-PORT-1、FEA-06|**closed_with_limitations**（集成 `aedc7251c`；scope-r2 + impl-r12 approved；全量 **1138/0/57**；AC7 MET、AC1–AC4/AC6/AC8 PARTIAL、AC5 BLOCKED/D-1；residual 见 Task 卡；AC5 原生矩阵待硬件/waiver）|
|FEA-06-RESIDUAL-1|FEA-06、FEA-07|**in_progress**（2026-11-02 范围 v3 冻结（scope-r3 approved）；impl Batch A 完成 `9337cbbe1`（I-1/I-2/I-3/I-6/I-9/I-10/I-12/I-13/I-14；安全回归 1170/0/57）；Batch B 收尾 `7ca725bbf`（I-4 有效属性/I-5 矩阵+消费/I-8/I-11；1191/0/57）；I-4 剩余状态/审查待续；FEA-09/10/11/12/13 仅为 BLOCKED 承接方）|
|FEA-06-PREREQ-1|FEA-04b|**done**（impl-r4 approved；AC1/AC3/AC5 residual 转 PREREQ-2，Q-33）|
|FEA-06-PREREQ-2|FEA-06-PREREQ-1|**done**（集成 `92cac5ab1`；scope-r4 + impl-r2 approved；全量 1022/0/57；Fluent 激活/V2 并存 + W-9 承接，W-12/W-13 写域登记）|
|FEA-C10-DRAFT|—|**done**（C-10 **FROZEN** v5，`T=4 DIP`；pin `ec8fd862…`；[冻结记录](plan/FEA-CONTRACT-FROZEN-C10.md)）|
|FEA-C14-DRAFT、FEA-D06-GAP|—|done（2026-11-01 收口；证据见各 Task 卡）|
|NEW-MANGA-V1-FULL-AUDIT|—|blocked（素材不传播；resume=in_progress）|

2026-10 及更早的**非活动节点**（31 行；含 1 条 blocked、1 条 Rust 线冻结快照）**原样迁入** [PLAN-HISTORY](PLAN-HISTORY.md)（含依赖/状态/集成 commit，迁出未改字节）。

## 当前活动程序（2026-10-30 起）

**V11R 程序**：[V11R_PROGRAM](V11R_PROGRAM.md) 为当前**唯一活动任务 DAG**（V1.1 整改 + 全新 Avalonia UI/UX + Theme Studio 重建）；共享接口契约：[V11R_AVALONIA_CONTRACT](plan/V11R_AVALONIA_CONTRACT.md)；冻结设计基线：`doc/design/redesign-v1/40-fusion/`。
本 Plan 的历史节点全部保持原状（证据/署名/字节不变），仅"READY 节点"由 V11R 程序接管。

READY 节点：无
进行中：FEA-06-RESIDUAL-1（范围 v3 冻结；Batch A 完成 `9337cbbe1`；Batch B 待派；BLOCKED=B-1…B-7）

当前 DAG：FEA-06-PREREQ-1（**done**）→ FEA-06-PREREQ-2（**done**）→ FEA-06（**done**，`b26840acd`，1034/0/57）→ FEA-07（**closed_with_limitations**，集成 `aedc7251c`，1138/0/57；AC5 D-1 residual）；下一节点 FEA-06-RESIDUAL-1（**in_progress**，范围 v3 冻结、Batch A 完成 `9337cbbe1`、Batch B 待派）

## 历史快照（终态节点，非当前 DAG）

已终止节点共 370+ 项（GOV-*、SETTINGS-OPEN-*、PLUGIN-*、UIUX-V2-*、PRODUCT-IDENTITY-1、HOST-CORECLIENT-1 等），明细以 [TASK_LEDGER](TASK_LEDGER.md) 与各 Task 卡为准。仍影响当前决策的终态约束：

- WORKSPACE-CONSOLIDATION-1：closed_with_limitations（r212），18 项受保护资源；不得清理/GC/prune。
- WORKSPACE-CLEANUP-TOOL-HARDENING-1 done（`368c07809`）；DECLARATION-REMEDIATION-1 done（`bb7887442`），残余 fail-closed；不因工具修复获得删除授权。
- 冻结 DAG 完整源：`fdca2057e:doc/REBASELINE_PLAN.md`（SHA-256 `1d2c83431273512787e58037260f1b27a2a0c3dab01e921e167fd6b51cf16ed7`）。
- 当前治理主线 `main`；远端仅允许用户授权的新分支快照 push，不 push main。
















