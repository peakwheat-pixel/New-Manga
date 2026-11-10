# Project Rebaseline Plan — 唯一 DAG

运行以 [STATUS](STATUS.md) 为准；目标架构 [AD-002](AD-002_TARGET_DESKTOP_ARCHITECTURE.md)（AD-001 已取代）。

## 当前 DAG

|节点/目标|依赖|状态|
|---|---|---|
|FEA-CONTRACT-WRAP-1|FEA-C14-DRAFT|done（L-3 Errata + PLAN 预算；R2 approved `6cfe7ab92`）|
|FEA-C11-PREREQ-1|FEA-C10-DRAFT|**done**（集成 `b7018e19b`；U-09 前置登记 L-1/L-2/L-5；r1 approved；2026-11-02 收口）|
|FEA-DOC-RECONCILE-1|—|**done**（文档对账 7 项；GOV-11/D07 关闭；BRIDGE 不独立释放；r3 approved）|
|FEA-07-RESIDUAL-4|FEA-07、FEA-07-RESIDUAL-3|**done**（L-R4b-1 隔离；真实 AppData delta=0；r2 approved；`7aa1e5778`）|
|FEA-11-2C-RESIDUAL-1|FEA-11-RUN-GRANT-2C|**done**（预算超限保留 typed stop；+3 判别测试；r1 approved；`a2c4c1d8c`）|
|FEA-11-HOST-AUTH-3|FEA-11-HOST-AUTH-2|**done**（C-17 v1.2 载体；5 轮独立 Review；崩溃正/反例 PASS）|
|FEA-13-BK2-1…SCHED-5|—|**done**（五片：backup/2+协商、覆盖二期、DatabaseId、merge restore、调度保留；详见各卡）|
|FEA-13-SRC-6|FEA-13-COV-2、FEA-11-HOST-AUTH-3|**done**（C-09 SC-B07 ④；extras+handoff+Host 导入；2 轮 Review；`ef0618e57`）|
|FEA-11-PREREQ-1|FEA-09、FEA-10|**done**（C-17 v1.0 FROZEN；pins 18/18；r1+轻量复核 approved P0/P1=0；集成提交见 Task）|
|FEA-11|FEA-09、FEA-10、FEA-11-PREREQ-1|**done**（2026-11-08 翻转：R4A `fbe337f95`；AC11-1…10 MET；L-STARTUP 子项 NA；L-M1/L-M4/needs_confirmation re-home；L-1…L-11 原文保留）||
|FEA-11-SCAN-1|FEA-11|**done**（r2 窄面 approved；delivery `7080167e1`；AC-S1…S6 全 MET；AC11-1 终态 MET 带 limitation）|
|FEA-11-HOST-AUTH-1|FEA-11-PREREQ-1|**done**（2026-11-08：AC3 MET（fresh+重发/恢复 e2e）；崩溃点 re-home HOST-AUTH-3；`f7016d3fb`）||
|FEA-11-LINEAGE-1|FEA-11-PREREQ-1|**done**（r4 approved；delivery `90a8c8218`；r7 硬约束解除；残余 L4-L11 见卡）||
|FEA-12-PREREQ-1|—|**done**（r2 approved；delivery `3e37c595b`；M2-C1 rev 2.13 + Host 投影；R-002 移交 CORE）||
|FEA-12-CORE|FEA-12-PREREQ-1、FEA-11-LINEAGE-1|**done**（r4 approved；UNFREEZE `fc9833479`；`51e139eff`；AC1–AC12 MET）||
|FEA-12-DSIM-1|—|**done**（r2 approved；delivery `beee351bb`；模拟切片，真实 D NOT_RUN）||
|FEA-12-UI|FEA-12-PREREQ-1、FEA-12-CORE|**done**（r2 approved；delivery `a46d4d5c7`；AC1–AC10 全 MET；L3 NOT_RUN）||
|FEA-11-MATCH-1|FEA-11|**done**（r2 窄面 approved；delivery `869b6d5d5`；AC-M1…M6 全 MET；AC11-3 回填 MET 带 L-M1/L-M4 limitation）||
|FEA-11-AC4-GAPS-1|FEA-11|**done**（r1 approved；delivery `2d9a4a219`；AC11-4 可判 MET；test-only）||
|FEA-01-FREEZE-1|FEA-C11-PREREQ-1|**done**（FEA-01 冻结 v2，pin `0370c189…`；集成 `bf1c8eb00`；15/15）|
|FEA-02-CORE|FEA-01-FREEZE-1|**done**（集成 `135479270`；delivery `5efb8f58c`；r1 approved）|
|FEA-00A-PREP-1|FEA-02-CORE|**done**（集成 `aec780362`；评估文档 v2 + R1 approved）|
|FEA-00A-IMPL-1|FEA-00A-PREP-1|**done**（集成 `e0ba29eba`；delivery `007094517`；实现复核 r1 approved P0/P1=0；AC7b 限制登记）|
|FEA-03|FEA-00A-IMPL-1、FEA-01-FREEZE-1|**done**（集成 `76d947923`；r5 approved；范围 v6 + C-13 v6 UNFREEZE；AC11b deferral）|
|FEA-04|FEA-02-CORE、FEA-03|**done**（集成 `f4d8a32ec`；实现复核 r3 approved P0/P1=0；sln 931/0/60；AC11b 无）|
|FEA-04b|FEA-01|**done**（设计基线 `fluent-v1.0.0` FROZEN；r5 approved；AC5 用户确认由 DSH 裁决替代）|
|FEA-05-WIRE-1|FEA-03、FEA-04|**done**（Draft 命令面 wire C078–C083；实现复核 impl-r3 approved；全量 931/0/60）|
|FEA-05-PORT-1|FEA-05-WIRE-1|**done**（Draft 端口面 + registry + Region 契约 v1.6；impl r3 approved；949/0/57）|
|FEA-06|FEA-04b、FEA-05-PORT-1、FEA-06-PREREQ-1/2|**done**（集成 `b26840acd`；impl-r2 approved；全量 1034/0/57；AC8–AC10 MET；AC1–AC7 residual→FEA-06-RESIDUAL-1）|
|FEA-07|FEA-00A-IMPL-1、FEA-04、FEA-05-PORT-1、FEA-06|**done**（2026-11-09 翻转：R4a `a03a6794a` + R4b `8e9420f41`；AC1–AC4/AC6–AC8 MET；AC5 原生矩阵 NA/NOT_RUN；L-R4a-1…4 + L-R4b-1…5 具名登记）|
|FEA-06-RESIDUAL-2|FEA-06-RESIDUAL-1|**done**（2026-11-08 翻转：RESIDUAL-3 `ddc29ecb3` 关 4 格 + Tab/a11y；格 3→RESIDUAL-4；原生 NA）|
|D-14-STATUS-COLOR-FIX|FEA-06-RESIDUAL-2|**done**（D-14 裁决 A 实施 `5ecc1e4c6`+证据补正 `075dc1682`；impl-r3 approved（ZCode，P0=0/P1=0/P2=2）；集成 `e36a7442b`；全量 **1292/0/57**）|
|FEA-06-PREREQ-2|FEA-06-PREREQ-1|**done**（集成 `92cac5ab1`；scope-r4 + impl-r2 approved；全量 1022/0/57；Fluent 激活/V2 并存 + W-9 承接，W-12/W-13 写域登记）|
|FEA-10-PREREQ-1|FEA-01-FREEZE-1|**done**（C-08 块②协议注册；集成 `728c8bb0`；impl r1 approved）|
|FEA-10|FEA-00A、03、09、FEA-10-PREREQ-1|**done**（最终 head `290717f1`，delivery `d1972f0f`；7 轮独立 Review approved P0/P1=0；AC1–AC10 MET；债务 R-005…R-016/F5-01…03）|
|FEA-C10-DRAFT|—|**done**（C-10 **FROZEN** v5，`T=4 DIP`；pin `ec8fd862…`；[冻结记录](plan/FEA-CONTRACT-FROZEN-C10.md)）|
|FEA-14-SET-1 / FEA-14-S5-PREQ-1|FEA-13-SRC-6|**done**（SET-1 r3 approved delivery `c543b51cc`；PREQ r2 approved delivery `5459c9220`；C-07 v1.2；wire 25 条 + errata 0 pin + DDL v10 计划）|
|FEA-14-EXPORT-1|FEA-14-S5-PREQ-1|**done**（r3 approved；delivery `0720686a6`；零新 wire/零 DDL）|
|FEA-15-A2-1|FEA-14-EXPORT-1|**done**（r2 approved；四页 4/4；双根隔离）|
|FEA-15-A3-1|FEA-15-A2-1|**closed_with_limitations**（r3 approved；四壳/四页 4/4；AC3 limitation：window-material.log 固定真实根 +166B）|
|NEW-MANGA-V1-FULL-AUDIT|—|blocked（素材不传播；resume=in_progress）|

## 当前活动程序（FEA 线 S5 + FEA-15 验收）

**FEA 线 S5**：FEA-14 七切片经 PREQ-1 口径/共用 wire 冻结；FEA-15 A2/A3/A4 机测推进；V11R 已收官。
READY 节点：FEA-15-A4-1


## 历史快照（终态节点，非当前 DAG）

已终止节点共 370+ 项（GOV-*、SETTINGS-OPEN-*、PLUGIN-*、UIUX-V2-*、PRODUCT-IDENTITY-1、HOST-CORECLIENT-1 等），明细以 [TASK_LEDGER](TASK_LEDGER.md) 与各 Task 卡为准。仍影响当前决策的终态约束：

- WORKSPACE-CONSOLIDATION-1：closed_with_limitations（r212），18 项受保护资源；不得清理/GC/prune。
- WORKSPACE-CLEANUP-TOOL-HARDENING-1 done（`368c07809`）；DECLARATION-REMEDIATION-1 done（`bb7887442`），残余 fail-closed；不因工具修复获得删除授权。
- 冻结 DAG 完整源：`fdca2057e:doc/REBASELINE_PLAN.md`（SHA-256 `1d2c83431273512787e58037260f1b27a2a0c3dab01e921e167fd6b51cf16ed7`）。
- 当前治理主线 `main`；2026-11-06 用户「全部授权」后，门禁全过时 `git push origin main` 已执行（`b1c1f5a5→57f62b3f`），后续 push 仍以门禁全过与用户授权为前提。
