---
task_id: FEA-14-READ-2
reviewer: fresh 独立上下文子 agent（未参与实现；只读）
reviewer_kind: subagent
author: dsh
base_commit: 034962ea7
reviewed_head: bd6defc84
decision: changes_requested
---

# Review：FEA-14-READ-2（r1）

## 0. 审查对象与环境

- 仓库 `G:\CODEX\New Manga`，`main`；**HEAD = `bd6defc8412f9226a532a79e0c8751770361d700`**。审查开始 `2026-11-10T13:33:00+08:00`、结束 `13:34+08:00`，两次 `git status --short` 均 **clean**，HEAD 不变。
- 增量：`034962ea7..bd6defc84`，**9 文件**：`ReaderViewModel.cs`、`FakeHostController.cs`、`ReaderReadingPreferencesTests.cs`（新）、PLAN/ledger/card/README/logs。
- 无 Core/wire/契约/DDL 改动；但 **新测试文件不在 allowed_paths**（R1-002）。
- 用户用 base `034962ea7`；卡面 `base_commit: 4de1c54f0`（READ-1 r4 而非 READ-1 收口 034962），provenance 见 R1-005。
- 只读纪律：仅写本文件；未改源码/测试/契约/卡面/证据，未 commit/push。门禁/测试日志写仓外 `G:\CODEX\New Manga.workspace\temp\FEA-14-READ-2-r1\`。

## 1. 结论

**`changes_requested`**（P0=0 / P1=0 / **P2=2** / **P3=3**）。

VM 层接线确实存在，测试 4/4、App 871/0/11、门禁全绿；但 **AC1 的“partial 保存”不成立**：`SaveReadingPreferencesAsync` 每次发送 Zoom/DoublePage/Layout/Direction 四个字段，且完全没有 `mode`；`ApplyReadingPreferencesAsync` 也不应用 `mode`，`direction` 只处理 rtl、vertical 未处理。因此 AC1 标 MET 过高，应 PARTIAL。另有新测试文件超出 allowed_paths。

## 2. Findings

| ID | 级别 | 位置 | 事实与影响 | 建议 |
|---|---|---|---|---|
| R1-001 | **P2** | `apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/ReaderViewModel.cs:112-157`；`ReaderReadingPreferencesTests.cs:56-68` | **AC1 的 partial patch 名不副实**：`SaveReadingPreferencesAsync` 构造 `new ReadingPreferencesPatch(Zoom: Zoom, DoublePage: DoublePage, Layout: Layout, Direction: ...)`，四个字段全部非 null，且**没有 Mode**；`ApplyReadingPreferencesAsync` 只应用 Zoom/DoublePage/ReverseDirection(rtl)/Layout，**不应用 mode**，`direction=vertical` 也被忽略。测试 `SavePreferencesSendsThePartialPatch` 只断言 `Zoom==2.0`，没有断言其他字段为 null 或 Mode 行为，属假阳性。 | 按“只传变化字段”维护 dirty 字段集合；扩展 `ReadingPreferencesPatch`/VM 保存 Mode；方向映射至少区分 ltr/rtl/vertical；测试断言 patch 只含变化字段及 mode 保存/应用 |
| R1-002 | **P2** | `apps/desktop-avalonia/tests/NewManga.App.Tests/ReaderReadingPreferencesTests.cs`；卡 allowed_paths `:33-35` | **范围 OUT=1**：新增测试文件不在 allowed_paths（允许的是 ReaderPreferenceTests.cs/ReaderBookmarkTests.cs/FakeHostController.cs）。用户要求“无未授权文件”不成立。 | 扩 allowed_paths 加入 `ReaderReadingPreferencesTests.cs` 并记录，或把测试并入已授权文件；重跑范围审计 |
| R1-003 | P3 | `ReaderReadingPreferencesTests.cs:56-68`；README AC1 | AC1 测试只覆盖 Zoom 变化；没有 partial patch 的负向断言（其他字段未发送）、mode 应用、vertical 方向、属性变更自动保存触发。AC1 README/card `MET` 的“partial”证据不足。 | 补断言：保存后 patch 仅含变化字段；Load 后 Mode/vertical；属性变更触发保存（或明确“手动调用”口径） |
| R1-004 | P3 | 卡 `:62`；README `:14` | 卡面 AC4 写「ReaderPreferenceTests/ReaderBookmarkTests」，实际新增/执行的是 **ReaderReadingPreferencesTests**；测试计数 4 对，但名称/证据不一致。 | 改 AC4 为 ReaderReadingPreferencesTests（或同时列旧两类），README/日志同步 |
| R1-005 | P3 | 卡 `:13`；用户 base `034962ea7`；实现提交 `29541dd69`；PLAN 收口提交 | 卡面 `base_commit: 4de1c54f0`（READ-1 r4），用户/本报告 base `034962ea7`（READ-1 收口）；实际实现提交 29541dd69 在 034962 之后。三者不同，provenance 不统一。 | 卡面 base 改 034962ea7（或注明实现起点头）；README/Review 统一 base |

## 3. AC 逐项

| AC | 状态 | 依据 |
|---|---|---|
| AC1 偏好应用 | **PARTIAL** | `LoadAsync` 后调用 `ApplyReadingPreferencesAsync`，应用 Zoom/DoublePage/rtl/Layout；测试 4/4 有偏好应用；但 **partial 保存发送全字段、无 Mode、vertical 未处理**（R1-001）；不能标 MET |
| AC2 书签 UI | **PARTIAL** | VM 层 `CreateBookmarkAsync/ListBookmarksAsync/DeleteBookmarkAsync` 完成，测试往返；**可见按钮/列表未接线**（README limitation；`ReaderWorkbenchPages.cs` 无 diff），PARTIAL 如实 |
| AC3 整书进度 UI | **PARTIAL** | `BookProgress/BookProgressLabel`（含“已读完”）与 reset confirm 在 VM 层完成；**页面 TextBlock/按钮绑定未接线**，PARTIAL 如实 |
| AC4 测试 | **MET** | ReaderReadingPreferencesTests **4 passed / 0 failed**；App.Tests 全量 **871/0/11**；日志 EXIT 0 |
| AC5 NOT_RUN | **MET（登记）** | 真实手势/IME/多屏/DPI/主题/托盘、真实进程重启、可见 UI 截图均 NOT_RUN |
| AC6 门禁与证据 | **MET（P3）** | check 默认/TaskPath PASS、pins 18/18、API 68；Canonical 3/3 hash 匹配；新测试文件 scope 见 R1-002 |

## 4. 门禁与测试

| # | 命令/检查 | 时点（+08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `pwsh -NoProfile -File tools/governance/check.ps1` | 13:33:37 → 13:33:40 | PASS（3 warnings：11 非终态 / STATUS 3159 B·31 L / PLAN 6980 B·64 L） | **0** |
| 2 | `... check.ps1 -TaskPath doc/tasks/FEA-14-READ-2.md` | 13:33:37 → 13:33:40 | PASS（同上） | **0** |
| 3 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 13:33:37 → 13:33:40 | **PIN AUDIT: PASS (all 18)** | **0** |
| 4 | `python tools/generate_api_inventory.py --check` | 13:33:37 → 13:33:40 | `OK: rendered counts match FEA-C07 doc`；合计 68 | **0** |
| 5 | `dotnet test ... --filter "FullyQualifiedName~ReaderReadingPreferencesTests"` | 13:33:40 → 13:33:48 | **4 passed / 0 failed** | **0** |
| 6 | App.Tests 全量（日志） | 13:27:16 起 | **871 passed / 0 failed / 11 skipped** | **0** |
| 7 | `git status --short` + `git rev-parse HEAD`（开始/结束） | 13:33:00 / 13:34+ | 两次均 **clean**；HEAD 均 `bd6defc84…` | — |
| 8 | 范围/Canonical | 13:33+ | 9 文件，OUT=1（ReaderReadingPreferencesTests.cs 不在 allowed）；Canonical **3/3 sha256 匹配** | — |

## 5. NOT_RUN

- 可见 UI 按钮/列表/TextBlock/reset 确认对话框未接线（`ReaderWorkbenchPages.cs` 无 diff）；AC2/AC3 仅 VM 层。
- 真实 UI 手势/IME/多屏/DPI/主题/托盘、真实进程重启、可见 UI 截图：NOT_RUN。
- 未修改/重跑 Core/wire/契约/DDL；无产品数据写入。

## 6. 处置建议

1. **R1-001（P2）**：实现真正的 partial patch（dirty 字段），补 Mode 应用/保存与 vertical 方向；测试断言 patch 只含变化字段。
2. **R1-002（P2）**：把 `ReaderReadingPreferencesTests.cs` 加入 allowed_paths（或并入已授权测试文件），重跑范围检查。
3. P3：补 AC1 负向/mode/vertical/自动保存测试；AC4 名称与实际测试对齐；卡面 base 改 034962ea7。
4. AC2/AC3 可见 UI 接线留后续 UI 卡；保持 PARTIAL，不冒充 MET。

## 7. 审查者声明

本报告由未参与 FEA-14-READ-2 实现的独立上下文子 agent 出具；只读审查，唯一写入为本文件。PASS 基于本次实测（4/4、App 871 日志、门禁）与逐行核对；未执行项在 §5 记 NOT_RUN；AC1 的 partial 保存按 head 代码判定为不成立。
