---
task_id: FEA-14-READ-2
reviewer: fresh 独立上下文子 agent（续接 r1/r2；未参与实现；只读）
reviewer_kind: subagent
author: dsh
base_commit: 9b1837e00
reviewed_head: bd6aa5246
decision: approved
---

# Review：FEA-14-READ-2（r2 处置后复核，r3）

## 0. 审查对象与环境

- 仓库 `G:\CODEX\New Manga`，`main`；**HEAD = `bd6aa52464f3aefa497b728d54ff5a7048fee817`**。审查开始 `2026-11-10T13:43:02+08:00`、结束 `13:44+08:00`，两次 `git status --short` 均 **clean**，HEAD 不变。
- 增量：`9b1837e00..bd6aa5246`，**7 文件**：`ReaderViewModel`（Mode/Vertical public set）、测试（新增 mode/vertical 保存用例）、卡面、README、两份日志、r2 报告。全部 ⊆ READ-2 allowed_paths（OUT=0）；无 Core/wire/契约/DDL 改动。
- 只读纪律：仅写本文件；未改源码/测试/契约/卡面/证据，未 commit/push。门禁/测试日志写仓外 `G:\CODEX\New Manga.workspace\temp\FEA-14-READ-2-r3\`。

## 1. 结论

**`approved`**（P0=0 / P1=0 / P2=0 / **P3=3**）。

r2 的 P2/P3 已关闭：README/卡面/日志统一 **6 passed**，App 全量重跑 **873/0/11**（含第 6 个测试）；`Mode`/`VerticalDirection` 改为可写；新增“改 Mode/vertical 只发对应字段”的保存测试；Canonical 3 行刷新。剩余 3 个 P3：日志 HEAD 为 r2 提交（非最终 head）、README AC1 说明仍未列 Mode/vertical、public setter 无值域/互斥校验。

## 2. r2 findings 关闭判定

| r2 ID | r2 级别 | r3 判定 | 依据 |
|---|---|---|---|
| R2-001 | P2 | **CLOSED（P3 残留）** | README AC4/日志说明改 **6 passed**；App 全量 **873 passed / 0 failed / 11 skipped**；卡面 AC4=6；`reader-reading-prefs.log` 6/0；Canonical 3 行 hash 匹配。残余：两份日志头 `HEAD=9b1837e00`（r2 提交）而非最终 `bd6aa5246`（R3-001） |
| R2-002 | P3 | **CLOSED（P3 风险）** | `ReaderViewModel.cs:114,117` `Mode`/`VerticalDirection` 已改 public set；可由 View 修改；但无值域/互斥校验（R3-002） |
| R2-003 | P3 | **CLOSED** | 新增 `ChangingModeOrVerticalSendsOnlyThatField`：改 Mode→只发 Mode；改 Vertical→Direction=vertical 且 Mode null；与 dirty-only 一致 |

## 3. R3 Findings

| ID | 级别 | 位置 | 事实与影响 | 建议 |
|---|---|---|---|---|
| R3-001 | P3 | `verification/FEA-14-READ-2/logs/dotnet-app-tests.log:1`；`logs/reader-reading-prefs.log:1` | 两份日志头均为 `HEAD=9b1837e00`（r2 提交），生成于 r3 提交前的工作树；App 873/Reader 6 本身是当前代码结果，但严格 provenance 不是最终 head。 | 在最终 head 重生成日志，或在日志/README 注明「生成时 HEAD=9b1837e00，工作树含 r3 改动」 |
| R3-002 | P3 | `ReaderViewModel.cs:114,117`；`SaveReadingPreferencesAsync` | `Mode`/`VerticalDirection` public set 后没有值域/互斥校验：Mode 可设任意字符串（含 bogus，Save 后 Core 拒绝）、Vertical 与 ReverseDirection 可同时 true（direction 映射时 vertical 优先）。当前无可见 UI 绑定，风险有限，但 View 层必须约束。 | 在 View/VM 层限制 Mode 枚举、Vertical/Reverse 互斥（或 setter 内互斥）；补无效值测试 |
| R3-003 | P3 | `verification/FEA-14-READ-2/README.md:11` | README AC1 说明仍只写「应用 Zoom/DoublePage/ReverseDirection/Layout」，未列新增的 Mode/VerticalDirection（卡面/测试已含）；属文档残留，易让读者以为 mode/vertical 未接。 | README AC1 补 Mode/VerticalDirection，并按 r3 的 6 tests 说明 |

## 4. AC 逐项

| AC | 状态 | 依据 |
|---|---|---|
| AC1 偏好应用 | **MET（VM 层，P3）** | Load 后 Apply Mode/Zoom/DoublePage/rtl/vertical/Layout；dirty-only partial 保存（Zoom/Mode/Vertical 测试；无脏不保存）；Mode/Vertical public set；UI 可见控件仍 partial；public setter 风险 R3-002 |
| AC2 书签 UI | **PARTIAL** | VM CRUD/往返测试；可见按钮/列表面板未接线（README limitation） |
| AC3 整书进度 UI | **PARTIAL** | VM `BookProgress/Label/reset confirm`；页面 TextBlock/按钮未接线（limitation） |
| AC4 测试 | **MET（P3 日志 HEAD）** | `ReaderReadingPreferencesTests` **6 passed / 0 failed**；App.Tests 全量 **873/0/11**；日志 HEAD 注记见 R3-001 |
| AC5 NOT_RUN | **MET（登记）** | 真实 UI 手势/IME/多屏/DPI/主题/托盘、真实进程重启、可见 UI 截图 NOT_RUN |
| AC6 门禁与证据 | **MET（P3）** | check 默认/TaskPath PASS、pins 18/18、API 68、Canonical 3/3；日志 HEAD 注记 |

## 5. 门禁与测试

| # | 命令/检查 | 时点（+08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `pwsh -NoProfile -File tools/governance/check.ps1` | 13:43:51 → 13:43:51 | PASS（3 warnings：11 非终态 / STATUS 3159 B·31 L / PLAN 6980 B·64 L） | **0** |
| 2 | `... check.ps1 -TaskPath doc/tasks/FEA-14-READ-2.md` | 13:43:51 → 13:43:51 | PASS（同上） | **0** |
| 3 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 13:43:51 | **PIN AUDIT: PASS (all 18)** | **0** |
| 4 | `python tools/generate_api_inventory.py --check` | 13:43:51 | `OK: rendered counts match FEA-C07 doc`；合计 68 | **0** |
| 5 | `dotnet test ... --filter "FullyQualifiedName~ReaderReadingPreferencesTests"` | 13:43:43 → 13:43:51 | **6 passed / 0 failed** | **0** |
| 6 | App.Tests 全量（日志） | 13:38:01 | **873 passed / 0 failed / 11 skipped**（HEAD=9b1837e00，见 R3-001） | **0** |
| 7 | `git status --short` + `git rev-parse HEAD`（开始/结束） | 13:43:02 / 13:44+ | 两次均 **clean**；HEAD 均 `bd6aa5246…` | — |
| 8 | 范围/Canonical | 13:43+ | 7 文件全部 ⊆ allowed（OUT=0）；READ-2 Canonical 3/3 sha256 匹配 | — |

## 6. NOT_RUN

- 可见 UI 按钮/列表面板/TextBlock/reset 确认：未接线（README limitation）。
- 真实 UI 手势/IME/多屏/DPI/主题/托盘、真实进程重启、可见 UI 截图：NOT_RUN。
- 未改/未重跑 Core/wire/契约/DDL；App 全量采用 873 日志（未由本审查重跑）。

## 7. 处置建议

1. R3-001（P3）：在最终 head 重生成日志或注明生成时 HEAD/工作树。
2. R3-002（P3）：ViewModel/View 层约束 Mode 枚举、Vertical/Reverse 互斥；补无效值测试。
3. R3-003（P3）：README AC1 补 Mode/VerticalDirection 与 6 tests 口径。
4. AC2/AC3 可见 UI 接线留后续 UI 卡；保持 PARTIAL。

## 8. 审查者声明

本报告由未参与 FEA-14-READ-2 实现的独立上下文子 agent 出具（续接 r1/r2；历史报告为本审查者前轮产出，不构成对实现的参与）。只读审查，唯一写入为本文件；PASS 基于本次实测/日志/逐行核对；未执行项在 §6 记 NOT_RUN。
