# MAINT-1 维护记录（AC1–AC4 汇总，2026-11-14）

本文件是 `MAINT-1-RELEASE-MONITOR` 的维护记录正本，逐条对应卡面 Acceptance Criteria。
所有结论只引用 STATUS / PLAN / V1 清单 / 原始门禁输出，不引入第二套事实源。

## AC1 · 维护记录：DAG 收口状态、V1 承诺清单、Release Gate BLOCKED 依据

**DAG 收口状态**（`doc/REBASELINE_PLAN.md`，HEAD `5ec365f14` 前后同值）：
- FEA 线 48 行节点**全部终态**（41 行全 `done` + 7 行含 `closed_with_limitations`，涉及 9 节点）。
- `proposed` 在 FEA 范围内**已清零**（4 张于 2026-11-14 处置：2 OUT 直接裁、2 OUT 经双签）。
- 非 FEA 非终态：`GIT-CLEAN-*` 系 5 张 + `MAINT-1` 本身（见 §后续）。
- 表外节点（FEA-08/09、PUBLISH-FIX-1、REL-GATE-1、SEC-01/02/03、CORE-01、AUDIT-*）已在 PLAN「当前活动程序」段落登记。

**V1 承诺清单**：`doc/design/V1_COMMITMENT_MANIFEST.md`（V1.0，2026-11-14 DSH 记录）。
其 16 项交付承诺中，UI 实现类多为「实现完成、真实 GUI NOT_RUN」；质量门禁项为「18/18 pins、API 86、EXIT 0」。

**Release Gate BLOCKED 依据**：`audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md` 维持 **BLOCKED**，缺四项：clean install、真实 GUI 全验收、真实模型 API 调用、完整验收证据。
`doc/STATUS.md` 同步记 `Technical Gate=NOT_SATISFIED`、`private_registry_absence=UNPROVABLE`、`Owner Risk Acceptance=APPROVED`、`Disposition=WAIVED_BY_OWNER`。

## AC2 · 监测规则

**规则**：
1. 四项门禁在任何 Task / 证据 / 指针变更后**必须复跑**，并把原始输出（含 `EXIT=`）落到 `verification/MAINT-1-RELEASE-MONITOR/logs/`。
2. 门禁全绿阈值为：`check.ps1` 默认与 `-TaskPath` 均 `EXIT=0`；`verify_pins` 18/18 `EXIT=0`；`generate_api_inventory.py --check` `EXIT=0`。
3. 门禁 PASS **不等于**产品发布 PASS；不得据以改写 Release Gate 结论。
4. `TASK_LEDGER` 由 `tools/governance/task_ledger.py --write` 重生成，任何状态变更后必须重跑，否则检查器报「TASK_LEDGER 已过期」。

**2026-11-14 实测原始输出**：`logs/gates-2026-11-14.log`（7,374 B）

| 门禁 | 结果 |
|---|---|
| `check.ps1`（默认） | `Governance check: PASS (3 warnings)`，`EXIT=0` |
| `check.ps1 -TaskPath MAINT-1` | `PASS (3 warnings)`，`EXIT=0` |
| `verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`，`EXIT=0` |
| `generate_api_inventory.py --check` | `EXIT=0` |

3 warnings 为固定项：10（现 6）张非终态 Task 提示、`STATUS.md` 与 `REBASELINE_PLAN.md` 达到 80% 预算。

## AC3 · 重新评估入口

**触发条件**（满足任一即按 `13_RELEASE_GATE.md` 要求复评）：获得 clean install 环境；获得真实模型 API 凭据与费用；获得安装验证条件（可执行 `setup.exe /S` 的隔离环境）。

**当前状态**：上述条件**均未获得** → Release Gate 保持 **BLOCKED**。
**禁令**：不得因本卡存在而把 BLOCKED 写成 PASS；不得以「仅进程级启动成功」或「打包产物生成成功」替代 clean install / 真实 GUI 全验收证据。

**已补齐的可执行证据**（不改变 Gate 结论）：
- P1：`.NET` 127 failed 归因（环境 + 3 类根因，产品回归 0 条），真实仓库 Release 全量 **1875 passed / 0 failed / 109 skipped，`EXIT=0`**（`P1-DOTNET-BASELINE-ATTRIBUTION.md`）。
- P2：四页可见 UI 冒烟 **PASS**（窗口 1.53–1.58 s、截图 28–60 KB、`exit=0`、真实 `%APPDATA%` 零变化）（`P2-UI-SMOKE.md`）。
- 二者**仍不构成** clean install 与完整 GUI 全验收。

## AC4 · 范围与历史字节自证

- 本卡未扩大产品范围：所有提案处置方向为 **OUT**（2 张直接裁、2 张经双签）；唯一产品可见缩减（Q7「查看对照」）已按「冻结设计意图的放弃」标准记录用户可见后果与重开条件，并标记可随时推翻。
- 未改写任何历史证据：`REL-GATE-1`、`FEA-15-*`、`FEA-14-*` 等卡的历史字节均未编辑；更正一律以 append-only errata 或独立 `doc/reviews/` 记录落盘。
- 未重算或覆盖任何 pin：`verify_pins` 18/18 保持 PASS；`FEA-06-PREREQ-1` 的 4 条 SHA 漂移**保持 FAIL 未修**，作为治理债登记（`MAINT-1-P3A-TASKPATH-DIAGNOSIS.md`）。
- 全部改动均落在本卡 `allowed_paths` 内；每次扩展 allowed_paths 均在改动前登记。

## 后续（不在本卡 AC 内，不得读作已完成）

残留待办由 P3 triage 列出，本卡不认领实现：
- **C1 工程可闭环 13 项**（AI-2、EDIT 清理、FONT 补测、LIB-2、READ-2 可见控件、pins 口径治理等）。
- **C2 契约对齐 5 项**、**C3 设计选择 7 项**、**C4 硬件 10 项**。
- `FEA-06-PREREQ-1` 的 13 个 `TaskPath` 错误（含 4 条证据 SHA 漂移）仍为治理债。
- Release Gate BLOCKED（线外发布缺口）。
