# Project Rebaseline Plan — 唯一 DAG

运行以 [STATUS](STATUS.md) 为准；目标架构 [AD-002](AD-002_TARGET_DESKTOP_ARCHITECTURE.md)（AD-001 已取代）。

## 当前 DAG

|节点/目标|依赖|状态|
|---|---|---|
|FEA-CONTRACT-WRAP-1|FEA-C14-DRAFT|done（L-3 Errata + PLAN 预算；R2 approved `6cfe7ab92`）|
|FEA-C11-PREREQ-1|FEA-C10-DRAFT|approved（U-09 前置登记：L-1/L-2/L-5 → 候选 Task 前置与 AC；r1 approved；待集成收口）|
|FEA-11-PREREQ-1|FEA-09、FEA-10|**done**（C-17 v1.0 FROZEN；pins 18/18；r1+轻量复核 approved P0/P1=0；集成提交见 Task）|
|FEA-11|FEA-09、FEA-10、FEA-11-PREREQ-1|**changes_requested**（实施完成；r1→r2→r3→r4 均 changes_requested；r4 后 P1-04 已修，r5 待派）||
|FEA-11-SCAN-1|FEA-11|**proposed**（定时扫描/后台调度；卡已建，待 FEA-11 done 后独立 scope review；承接 AC11-1 延期项）|
|FEA-11-HOST-AUTH-1|FEA-11-PREREQ-1|**proposed**（承接 r2 P0-1：Host durable authorization 自签/编排；可与 FEA-11 并行，FEA-11 done 前须完成或获用户接受 limitation）||
|FEA-11-LINEAGE-1|FEA-11-PREREQ-1|**proposed**（承接 r2 R-009：lineage native 写入 + 读路径隔离；AC11-5 安全属性，完成前 FEA-11 不得 done，但本卡不依赖 FEA-11，可并行）||
|FEA-11-MATCH-1|FEA-11-PREREQ-1|**proposed**（承接 r2 R-012：pixel profile 提取/旧库 fixture/独立 match 测试；AC11-3 done-with-limitation 的落实前提）||
|FEA-11-AC4-GAPS-1|FEA-11-PREREQ-1|**proposed**（承接 r4 P2-11：AC11-4 并发 apply/DB 失败/第三区域证据；可与 FEA-11 并行）||
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
|FEA-06-RESIDUAL-2|FEA-06-RESIDUAL-1|**closed_with_limitations**（impl-r4 approved P0=0/P1=0/P2=3，172 图 172 PASS/0 REJECT；交付 `832103393`；集成 `d1df8035a`；全量 **1289/0/57**；AC1–AC4 MET；BLOCKED=原生 DPI/a11y、OUT=loading/危险加载/新增组件状态）|
|D-14-STATUS-COLOR-FIX|FEA-06-RESIDUAL-2|**done**（D-14 裁决 A 实施 `5ecc1e4c6`+证据补正 `075dc1682`；impl-r3 approved（ZCode，P0=0/P1=0/P2=2）；集成 `e36a7442b`；全量 **1292/0/57**）|
|FEA-06-PREREQ-1|FEA-04b|**done**（impl-r4 approved；AC1/AC3/AC5 residual 转 PREREQ-2，Q-33）|
|FEA-06-PREREQ-2|FEA-06-PREREQ-1|**done**（集成 `92cac5ab1`；scope-r4 + impl-r2 approved；全量 1022/0/57；Fluent 激活/V2 并存 + W-9 承接，W-12/W-13 写域登记）|
|FEA-09-UI-1|FEA-09|**done**（`b14e04da`；AC1–5 MET；r4 approved）|
|FEA-10-PREREQ-1|FEA-01-FREEZE-1|**done**（C-08 块②协议注册；集成 `728c8bb0`；impl r1 approved）|
|FEA-10|FEA-00A、03、09、FEA-10-PREREQ-1|**done**（最终 head `290717f1`，delivery `d1972f0f`；7 轮独立 Review approved P0/P1=0；AC1–AC10 MET；债务 R-005…R-016/F5-01…03）|
|FEA-C10-DRAFT|—|**done**（C-10 **FROZEN** v5，`T=4 DIP`；pin `ec8fd862…`；[冻结记录](plan/FEA-CONTRACT-FROZEN-C10.md)）|
|NEW-MANGA-V1-FULL-AUDIT|—|blocked（素材不传播；resume=in_progress）|

2026-10 及更早的**非活动节点**（31 行；含 1 条 blocked、1 条 Rust 线冻结快照）**原样迁入** [PLAN-HISTORY](PLAN-HISTORY.md)（含依赖/状态/集成 commit，迁出未改字节）。

## 当前活动程序（2026-10-30 起）

**V11R 程序**：[V11R_PROGRAM](V11R_PROGRAM.md) 为当前**唯一活动任务 DAG**（V1.1 整改 + 全新 Avalonia UI/UX + Theme Studio 重建）；共享接口契约：[V11R_AVALONIA_CONTRACT](plan/V11R_AVALONIA_CONTRACT.md)；冻结设计基线：`doc/design/redesign-v1/40-fusion/`。
本 Plan 的历史节点全部保持原状（证据/署名/字节不变），仅"READY 节点"由 V11R 程序接管。

READY 节点：无

完成：FEA-10 **done**（`d1972f0f`）；FEA-11-PREREQ-1 **done**（C-17 v1.0 FROZEN，pins 18/18，集成 `75d11739b`）。当前：**FEA-11 changes_requested（r4 后返修，r5 待派）**。

当前 DAG：FEA-08（done）→ FEA-09-PREREQ-1（done）→ FEA-09（done）→ FEA-09-UI-1（done）→ FEA-10-PREREQ-1（done）→ **FEA-10（done）** → **FEA-11-PREREQ-1（done，C-17 FROZEN/pins 18）** → **FEA-11（changes_requested，r2；返修→r5）**；承接 HOST-AUTH-1/LINEAGE-1/MATCH-1/SCAN-1（proposed）；FEA-12 待 `G-DELETE-IMPL`

## 历史快照（终态节点，非当前 DAG）

已终止节点共 370+ 项（GOV-*、SETTINGS-OPEN-*、PLUGIN-*、UIUX-V2-*、PRODUCT-IDENTITY-1、HOST-CORECLIENT-1 等），明细以 [TASK_LEDGER](TASK_LEDGER.md) 与各 Task 卡为准。仍影响当前决策的终态约束：

- WORKSPACE-CONSOLIDATION-1：closed_with_limitations（r212），18 项受保护资源；不得清理/GC/prune。
- WORKSPACE-CLEANUP-TOOL-HARDENING-1 done（`368c07809`）；DECLARATION-REMEDIATION-1 done（`bb7887442`），残余 fail-closed；不因工具修复获得删除授权。
- 冻结 DAG 完整源：`fdca2057e:doc/REBASELINE_PLAN.md`（SHA-256 `1d2c83431273512787e58037260f1b27a2a0c3dab01e921e167fd6b51cf16ed7`）。
- 当前治理主线 `main`；远端仅允许用户授权的新分支快照 push，不 push main。

