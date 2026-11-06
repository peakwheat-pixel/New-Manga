# Project Rebaseline Plan — 唯一 DAG

运行以 [STATUS](STATUS.md) 为准；目标架构 [AD-002](AD-002_TARGET_DESKTOP_ARCHITECTURE.md)（AD-001 已取代）。

## 当前 DAG

|节点/目标|依赖|状态|
|---|---|---|
|FEA-CONTRACT-WRAP-1|FEA-C14-DRAFT|done（L-3 Errata + PLAN 预算；R2 approved `6cfe7ab92`）|
|FEA-C11-PREREQ-1|FEA-C10-DRAFT|approved（U-09 前置登记：L-1/L-2/L-5 → 候选 Task 前置与 AC；r1 approved；待集成收口）|
|FEA-11-PREREQ-1|FEA-09、FEA-10|**done**（C-17 v1.0 FROZEN；pins 18/18；r1+轻量复核 approved P0/P1=0；集成提交见 Task）|
|FEA-11|FEA-09、FEA-10、FEA-11-PREREQ-1|**closed_with_limitations**（用户裁决；L-1…L-11；r1–r7）||
|FEA-11-SCAN-1|FEA-11|**done**（r2 窄面 approved；delivery `7080167e1`；AC-S1…S6 全 MET；AC11-1 终态 MET 带 limitation）|
|FEA-11-HOST-AUTH-1|FEA-11-PREREQ-1|**closed_with_limitations**（Codex 裁决 A；r8 approved；AC3 PARTIAL+10 limitation；`cbd561b4`）||
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
|FEA-07|FEA-00A-IMPL-1、FEA-04、FEA-05-PORT-1、FEA-06|**closed_with_limitations**（集成 `aedc7251c`；impl-r12 approved；全量 1138/0/57；AC7 MET、AC1–AC4/AC6/AC8 PARTIAL、AC5 BLOCKED/D-1）|
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

**V11R 程序**：[V11R_PROGRAM](V11R_PROGRAM.md) 为**唯一活动任务 DAG**（V1.1 整改 + 新 Avalonia UI/UX + Theme Studio）；接口契约 [V11R_AVALONIA_CONTRACT](plan/V11R_AVALONIA_CONTRACT.md)；设计基线 `doc/design/redesign-v1/40-fusion/`。历史节点原状保留；READY 节点由本 Plan 维护。

READY 节点：`FEA-11-RUN-GRANT-1`

完成：FEA-10 done；FEA-11-PREREQ-1 done；FEA-11 与 HOST-AUTH-1 `closed_with_limitations`；FEA-12 四卡 done；FEA-11 承接卡 AC4-GAPS-1/MATCH-1/SCAN-1/SCAN-2/WATCH-1 done（AC11-4/AC11-3 终态见各卡；AC11-1 2026-11-06 判 MET 带 L-STARTUP）；UNFREEZE C-04b v1.1+M2-C1 rev2.14（`fc9833479`）。

当前 DAG：FEA-11-PREREQ-1→FEA-11（closed_with_limitations）→ 承接卡 done → FEA-12 四卡 done → SCAN-2-PREREQ-1/SCAN-2/WATCH-1 done → FEA-11-RENDITION-1（done，a05a419f7；Core-only）→ FEA-12-UI-RESIDUAL-1（done，8e3bd03d6；App-only）→ FEA-11-RUN-GRANT-1-PREREQ-1（done，116a711ba；C-06 v1.2+C-16 v1.3）→ FEA-11-RUN-GRANT-1（CORE+HOST）

## 历史快照（终态节点，非当前 DAG）

已终止节点共 370+ 项（GOV-*、SETTINGS-OPEN-*、PLUGIN-*、UIUX-V2-*、PRODUCT-IDENTITY-1、HOST-CORECLIENT-1 等），明细以 [TASK_LEDGER](TASK_LEDGER.md) 与各 Task 卡为准。仍影响当前决策的终态约束：

- WORKSPACE-CONSOLIDATION-1：closed_with_limitations（r212），18 项受保护资源；不得清理/GC/prune。
- WORKSPACE-CLEANUP-TOOL-HARDENING-1 done（`368c07809`）；DECLARATION-REMEDIATION-1 done（`bb7887442`），残余 fail-closed；不因工具修复获得删除授权。
- 冻结 DAG 完整源：`fdca2057e:doc/REBASELINE_PLAN.md`（SHA-256 `1d2c83431273512787e58037260f1b27a2a0c3dab01e921e167fd6b51cf16ed7`）。
- 当前治理主线 `main`；2026-11-06 用户「全部授权」后，门禁全过时 `git push origin main` 已执行（`b1c1f5a5→57f62b3f`），后续 push 仍以门禁全过与用户授权为前提。

