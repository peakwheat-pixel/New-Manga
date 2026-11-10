---
task_id: FEA-14-READ-2
reviewer: fresh 独立上下文子 agent（续接 r1；未参与实现；只读）
reviewer_kind: subagent
author: dsh
base_commit: bd6defc84
reviewed_head: 9b1837e00
decision: changes_requested
---

# Review：FEA-14-READ-2（r1 处置后复核，r2）

## 0. 审查对象与环境

- 仓库 `G:\CODEX\New Manga`，`main`；**HEAD = `9b1837e002a2b2324f0a5ed3418150e97ce65be4`**。审查开始 `2026-11-10T13:35:58+08:00`、结束 `13:37+08:00`，两次 `git status --short` 均 **clean**，HEAD 不变。
- 增量：`bd6defc84..9b1837e00`，**5 文件**：`ReaderViewModel.cs`、`ReaderReadingPreferencesTests.cs`、卡面、r1 报告、Reader 定向日志。全部 ⊆ READ-2 allowed_paths（OUT=0）。
- 卡面 `base_commit` 已改 `034962ea7`；无 Core/wire/契约/DDL 改动。
- 只读纪律：仅写本文件；未改源码/测试/契约/卡面/证据，未 commit/push。门禁/测试日志写仓外 `G:\CODEX\New Manga.workspace\temp\FEA-14-READ-2-r2\`。

## 1. 结论

**`changes_requested`**（P0=0 / P1=0 / **P2=1** / **P3=2**）。

R1-001 的 dirty-only 语义已实现并通过负向测试（只改 Zoom 时 Mode/Direction/DoublePage/Layout 均为 null；无脏不保存），Mode/vertical 应用也已加入；R1-002/R1-003/R1-005 关闭。剩余问题主要是 **证据/文档与代码不同步**：README 仍写 4 passed / App 871（实际定向 5 passed，全量应为 872），且 VM 的 `Mode`/`VerticalDirection` 是 private set，没有用户可触发的修改/保存路径；AC1 只能算 VM 层 MET，UI 仍 partial。

## 2. r1 findings 关闭判定

| r1 ID | r1 级别 | r2 判定 | 依据 |
|---|---|---|---|
| R1-001 | P2 | **CLOSED（P3 残余）** | `ReaderViewModel.cs:111-170`：`_appliedPreferences` 快照；`SaveReadingPreferencesAsync` 逐字段比较只发变化项，无变化直接 return；Mode/vertical 在 `ApplyReadingPreferencesAsync` 应用；保存后更新快照。测试：只改 Zoom 时 Mode/Direction/DoublePage/Layout 均 null；无脏不保存。残余：`Mode`/`VerticalDirection` 为 private set（R2-002），无用户修改/自动保存触发 |
| R1-002 | P2 | **CLOSED** | allowed_paths 已补 `ReaderReadingPreferencesTests.cs`；`bd6..9b1` 5 文件 OUT=0 |
| R1-003 | P3 | **CLOSED** | 新增/收紧负向断言：只改 Zoom 发送单字段；mode/vertical 应用测试；无脏不保存 |
| R1-004 | P3 | **PARTIAL（P2）** | 卡面 AC4 已改 `ReaderReadingPreferencesTests` **5 passed**；但 README 仍写 **4 passed**、`logs/reader-reading-prefs.log` 行仍称 4（实际文件 5），App 全量日志仍是 4 测试时期的 **871**；证据不同步（R2-001） |
| R1-005 | P3 | **CLOSED** | 卡面 `base_commit: 034962ea7` |

## 3. R2 Findings

| ID | 级别 | 位置 | 事实与影响 | 建议 |
|---|---|---|---|---|
| R2-001 | **P2** | `verification/FEA-14-READ-2/README.md:11,14,22,24`；`logs/dotnet-app-tests.log`；卡 `:62` | **证据不同步**：README AC4 仍写 4 passed、`logs/reader-reading-prefs.log` 说明仍写 4；实际 `reader-reading-prefs.log` 为 **5 passed/0 failed**、卡面 AC4 写 5。App 全量日志仍为 **871/0/11**（HEAD=034962，4 测试时）；新增第 5 个测试后全量应为 **872**，但未重跑/刷新。Canonical README hash 虽匹配，但内容仍是旧版。 | 同步 README（4→5、App 871→872 或注明未重跑）；重跑 App 全量并刷新 EV-RD2-001；若只保留定向 5，删除 README 的 4 与旧 871 断言 |
| R2-002 | P3 | `ReaderViewModel.cs:114,117,149-170` | **Mode/VerticalDirection 是 private set**：只能由 `ApplyReadingPreferencesAsync` 设置；用户/View 无法通过属性修改，也没有自动触发 `SaveReadingPreferencesAsync` 的路径。AC1 的“修改后 partial 保存”只有 Zoom 测试覆盖；Mode/vertical 只能“应用”，不能从 VM 侧保存。 | 给 Mode/Vertical 提供可绑定 setter（或显式切换方法）；在属性变更时触发保存（或明确由命令调用保存），补 Mode/vertical 保存测试 |
| R2-003 | P3 | `ReaderReadingPreferencesTests.cs:93-115`；README AC1 | 新增的 `ApplyReadingPreferencesAppliesModeAndVerticalDirection` 测试只验证应用与“无脏不保存”，未验证用户把 mode/vertical 改后再保存；AC1 的 partial patch 仅 Zoom 路径，VM 层 UI 接线仍不完整（可见 UI 未接是已知 limitation）。 | 增加“Mode 变更→只发 Mode”“Vertical→只发 Direction”的保存测试；与 AC1 的修改后保存口径对齐 |

## 4. AC 逐项

| AC | 状态 | 依据 |
|---|---|---|
| AC1 偏好应用 | **MET（VM 层，P3）** | Load 后 Apply（Mode/Zoom/DoublePage/rtl/vertical/Layout）；dirty-only partial 保存（Zoom 测试；无脏不保存）；但 Mode/Vertical 为 private set、无自动保存触发（R2-002/R2-003） |
| AC2 书签 UI | **PARTIAL** | VM CRUD 与往返测试；可见按钮/列表仍未接线（`ReaderWorkbenchPages.cs` 无 diff），如实 PARTIAL |
| AC3 整书进度 UI | **PARTIAL** | VM `BookProgress/Label/reset confirm` 完成；页面 TextBlock/按钮未接线，如实 PARTIAL |
| AC4 测试 | **MET（P2 证据）** | 定向 `ReaderReadingPreferencesTests` **5 passed/0 failed**（本次实测）；但 README/App 全量仍是 4/871 旧值（R2-001） |
| AC5 NOT_RUN | **MET（登记）** | 真实手势/IME/多屏/DPI/主题/托盘、真实进程重启、可见 UI 截图均 NOT_RUN |
| AC6 门禁与证据 | **MET（P2/P3）** | check 默认/TaskPath PASS、pins 18/18、API 68、Canonical 3/3；证据同步问题见 R2-001 |

## 5. 门禁与测试

| # | 命令/检查 | 时点（+08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `pwsh -NoProfile -File tools/governance/check.ps1` | 13:36:51 → 13:36:54 | PASS（3 warnings：11 非终态 / STATUS 3159 B·31 L / PLAN 6980 B·64 L） | **0** |
| 2 | `... check.ps1 -TaskPath doc/tasks/FEA-14-READ-2.md` | 13:36:51 → 13:36:54 | PASS（同上） | **0** |
| 3 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 13:36:51 → 13:36:54 | **PIN AUDIT: PASS (all 18)** | **0** |
| 4 | `python tools/generate_api_inventory.py --check` | 13:36:51 → 13:36:54 | `OK: rendered counts match FEA-C07 doc`；合计 68 | **0** |
| 5 | `dotnet test ... --filter "FullyQualifiedName~ReaderReadingPreferencesTests"` | 13:36:43 → 13:36:51 | **5 passed / 0 failed** | **0** |
| 6 | App.Tests 全量（旧日志） | 13:27:16 | **871 passed / 0 failed / 11 skipped**（HEAD=034962；未重跑，见 R2-001） | **0（旧日志）** |
| 7 | `git status --short` + `git rev-parse HEAD`（开始/结束） | 13:35:58 / 13:37+ | 两次均 **clean**；HEAD 均 `9b1837e00…` | — |
| 8 | 范围/Canonical | 13:36+ | 5 文件全部 ⊆ allowed（OUT=0）；READ-2 Canonical 3/3 sha256 匹配 | — |

## 6. NOT_RUN

- 可见 UI 按钮/列表面板/TextBlock/reset 确认：未接线（README limitation）。
- 真实 UI 手势/IME/多屏/DPI/主题/托盘、真实进程重启、可见 UI 截图：NOT_RUN。
- 未改/未重跑 Core/wire/契约/DDL；未重跑 App 全量（仅旧日志）。

## 7. 处置建议

1. **R2-001（P2）**：同步 README（4→5、App 871→872 或明确未重跑）、重跑 App 全量并刷新 EV-RD2-001；`reader-reading-prefs.log` 内部说明也要改 4→5。
2. R2-002/R2-003（P3）：提供 Mode/Vertical 可修改路径与保存触发；补 Mode/vertical 保存测试。
3. AC2/AC3 的可见 UI 留后续 UI 卡；保持 PARTIAL。
4. 修后重跑 check/pins/API/定向测试；真实 UI 仍 NOT_RUN。

## 8. 审查者声明

本报告由未参与 FEA-14-READ-2 实现的独立上下文子 agent 出具（续接 r1；r1 报告为本审查者前轮产出，不构成对实现的参与）。只读审查，唯一写入为本文件；PASS 基于本次实测/逐行核对；未执行项在 §6 记 NOT_RUN。
