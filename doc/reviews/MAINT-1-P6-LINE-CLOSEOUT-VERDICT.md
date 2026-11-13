# FEA 线收口判定报告（P6 收官核对）— 2026-11-14

**判定：线未收口（DoD 5 条中 2 条未达成）**。本报告不构成完成声明。

基线：`main` @ `da76f7797`，工作区 clean。门禁：`check.ps1` PASS(3w)、`verify_pins` 18/18 PASS。

## 1. DoD-Line 逐条核对

| # | 判据 | 判定 | 证据 / 缺口 |
|---|---|---|---|
| 1 | DAG 中 FEA-* 全部 done，或 done + 显式 waiver（含 NOT_APPLICABLE 原因与保留的 NOT_RUN 证据） | **未达成** | 48 行节点全终态（41 行 done + 7 行含 closed），但 9 个 `closed_with_limitations` **未被逐条转为 done+waiver 或 done+MET**；triage 已分类，未落 waiver 载体 |
| 2 | 无 in_progress/pending/blocked 的 FEA 节点；proposed 已逐张处置 | **达成** | FEA 范围 `proposed` 清零（4 张全 OUT）；ACTIVE 仅 `MAINT-1`（非 FEA 节点）；`PLAN:58` |
| 3 | 所有 limitation 逐条处置（C1 补实现并 MET；C3/C4 转 OUT + waiver；无悬空 L-*） | **未达成** | `MAINT-1-P3-LIMITATION-TRIAGE.md`：C1 约 13、C2 5、C3 7、C4 10。**C1 未实现、C2 未裁决、C3/C4 未出正式 waiver 载体**；Q6（pytest 16F）未决 |
| 4 | 四项门禁全绿 | **有条件达成** | `check.ps1` 默认+TaskPath 均 `EXIT=0`；`verify_pins` 18/18 `EXIT=0`；`generate_api_inventory --check` `EXIT=0`；`.NET` 真实仓库 Release **1875 passed / 0 failed / 109 skipped `EXIT=0`**（高于登记基线 1804/0/107）；**`pytest` 仍为登记基线内 16 failed**（`V1_COMMITMENT_MANIFEST:16` 登记为既有失败），属"已归因但未清零" |
| 5 | STATUS / PLAN / TASK_LEDGER 三处一致且与证据一致 | **达成** | `STATUS:6-7` 记「FEA 已收口；当前 Task MAINT-1 `in_progress`」；`PLAN:58` 记 `ACTIVE：MAINT-1`；`TASK_LEDGER` 重生成后 `non-terminal 6`、`named in the plan 5`；三者互相吻合 |

## 2. 逐节点终态表（FEA-*）

| 状态 | 行数 | 说明 |
|---|---:|---|
| `done` | 41 | 含 S0–S4 全部、S5 的 SET/S5-PREQ/EXPORT/A2-1/A4-1/PIN-POLICY/GOV 三卡 |
| `closed_with_limitations` | 7 行 / 9 节点 | ACCEPT-1、AI-1、EDIT-1、FONT-1、LIB-1、READ-1、READ-2、A3-1、PIN-BASIS-ENFORCE-1 |
| `proposed` | 0 | 4 张全部 OUT（2 直接、2 双签） |
| `in_progress`/`pending`/`blocked` | 0 | — |

## 3. 仍保留的 OUT / waiver / 待办清单

**已生效的 OUT（2 项，均为产品/范围决定，可撤销）**：
- `FEA-11-HOST-AUTH-4`：测试/健壮性观测项，无产品可见变化。
- `FEA-11-L-S1-B2-ROOTS-AVAILABILITY-1`：字段已冻结但无消费者。
- `FEA-06-RESIDUAL-4`：**产品范围缩减**——放弃「查看对照」这条冻结设计意图（用户可见后果已记录；**待用户事后确认**）。
- `FEA-11-HOST-AUTH-5`：不新建全链路实现卡（链已存在且 opt-in 执行过）。

**未处置（DoD §3 的实际缺口）**：
- C1 约 13 项（AI-2、EDIT 清理、FONT 补测、LIB-2、READ-2 可见控件、pin 口径治理等）。
- C2 5 项（name 规范化、position 形状、LIB-1 R-11 deferral、READ P12/P15 偏差、AI-1 UPDATE OR REPLACE）。
- C3 7 项 / C4 10 项：**已分类但未出正式 waiver 载体**（无 `NOT_APPLICABLE: 原因` 记录）。
- Q6：pytest 16 failed——修复 or 永久登记，未裁。
- 治理债：`FEA-06-PREREQ-1` 13 个 TaskPath 错误（含 4 条证据 SHA 漂移，保持 FAIL 未修）。

## 4. 线外发布缺口（明确排除在 DoD 之外，不得写成 PASS）

`audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md` 维持 **BLOCKED**，缺：真实 clean install、真实 GUI 全验收、真实模型 API 调用、完整验收证据。
`Technical Gate=NOT_SATISFIED`；`private_registry_absence=UNPROVABLE`；`Disposition=WAIVED_BY_OWNER`。
本轮 P2 的四页冒烟与 P1 的 .NET 归因**不构成** clean install 或完整 GUI 全验收。

## 5. 结构阻塞（决定下一阶段能否推进）

`doc/REBASELINE_PLAN.md` 为 **64/64 行、6954/7000 字节**，行余量 0、字节余量 46。
而 `check.ps1:702` 要求任何 `in_progress` 任务必须登记在当前 DAG → **新开 C1 实现卡会直接触发预算 FAIL**。

**解法（下一轮采用）**：C1 实现卡以 `MAINT-2-*` 形式登记，其 ID 并入「当前活动程序」段既有的表外节点行（不新增行，仅增加约 35 B，预算内）；同步更新 `READY/ACTIVE` 声明。若后续需多卡，再压缩 PLAN 的冗余注释。

## 6. 结论与下一步

**结论**：FEA 线**工程实现层已全部收口**，**验收/限制层未收口**。目标保持 active，不得标记完成。

**按优先级的下三轮建议**：
1. **P7**：释放 `MAINT-2-C1-BATCH-1`（单卡承载价值最高的 3–4 项 C1，如 READ-2 可见控件 + FONT 补测 + pin 口径治理），Codex/ZCode 实现，独立 Review。
2. **P8**：出 C3/C4 的正式 waiver 载体（`NOT_APPLICABLE: 原因` + 保留 `NOT_RUN` 证据），逐节点关闭 limitation。
3. **P9**：Q6（pytest 16F）裁决 + 复跑 P6 核对，若 DoD 仍缺则继续。

**需要用户决策的只有一项**：Q7「查看对照」的产品范围缩减是否接受（已生效、可随时推翻）。
