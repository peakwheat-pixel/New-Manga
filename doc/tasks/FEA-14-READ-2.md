---
id: FEA-14-READ-2
title: FEA-14 切片 READ-2：Fluent Reader UI 接线（偏好/书签/整书进度/reset 确认）
kind: implementation
governance_version: 3
status: in_review
approval: **DSH 2026-11-10 冻结**（READ-1 收口遗留：AC1–AC3 的 Fluent UI 层；`ADJ-2026-11-10-FEA14-S5-SCOPE` §2.1）
suggested_owner: dsh
owner: dsh
reviewer: null
depends_on:
  - FEA-14-READ-1
base_commit: 034962ea7
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-14-READ-2
allowed_paths:
  - doc/tasks/FEA-14-READ-2.md
  - doc/reviews/FEA-14-READ-2-*.md
  - doc/handoffs/FEA-14-READ-2-*.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/FEA-14-READ-2/**
  - apps/desktop-avalonia/src/NewManga.App/Views/ReaderWorkbenchPages.cs
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/ReaderViewModel.cs
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/Reader/ReaderPageViewModel.cs
  - apps/desktop-avalonia/src/NewManga.App/Views/ImportExportPanels.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/ReaderPreferenceTests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/ReaderReadingPreferencesTests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/ReaderBookmarkTests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs
out_of_scope:
  - 不改 Core/wire（READ-1 已交付 P9–P15；本卡只消费 IHostController 七方法）
  - 不改契约/DDL/pins（除非 UI 消费发现 wire 缺口，须登记并另立）
  - 不实现跨内容连续序列（READ-3）
  - 真实 UI 手势/IME/多屏/DPI/系统主题/托盘 = NOT_RUN
---

# FEA-14-READ-2：Fluent Reader UI 接线

## 背景

READ-1 已交付 Core schema v10、wire P9–P15 与 `IHostController` 七方法；Fluent Reader（`ReaderWorkbenchPages.cs` + `Fluent/ReaderViewModel.cs`）尚未消费这些能力（READ-1 AC1–AC3 的 UI 层 limitation）。本卡只做 UI 接线，不改 wire/契约。

## Scope 冻结（2026-11-10，DSH）

1. 打开书时加载 `GetReadingPreferencesAsync(bookId)` 并应用（mode/direction/zoom/doublePage/layout）；用户修改后 `SaveReadingPreferencesAsync`（partial patch 只传改动字段）。
2. 书签：列表（`ListBookmarksAsync`）、新增（当前页 left/right/both + note）、删除（`DeleteBookmarkAsync`）。
3. 整书进度：`GetBookReadingProgressAsync` 显示 read_pages/total_pages/percent；最后一页 → 已读完（finished）。
4. Reset：按钮 + 确认提示，确认后 `ResetReadingProgressAsync(bookId, confirm: true)`；取消不重置。
5. `FakeHostController` 支持七方法的脚本化行为；App.Tests 覆盖打开应用偏好、书签增删、进度显示、reset 确认/取消。

## Acceptance Criteria

- [x] **AC1 偏好应用**：打开书 → `GetReadingPreferencesAsync` 被调用并按返回应用 mode/direction/zoom/doublePage/layout；修改后 partial 保存（只传变化字段）。 <<MET>>
- [ ] **AC2 书签 UI**：新增（side left/right/both + note）/列表/删除；删除不影响其他状态；跨书隔离。 <<PARTIAL: VM 层书签 CRUD 完成并有测试；可见按钮/列表面板未接线>>
- [ ] **AC3 整书进度 UI**：显示 read_pages/total_pages/percent；finished 显示「已读完」；reset 需确认（取消不调用）。 <<PARTIAL: VM 层 BookProgress/Reset 确认完成；页面 TextBlock/按钮绑定未接线>>
- [x] **AC4 测试**：App.Tests 定向（ReaderReadingPreferencesTests + FakeHostController 脚本）**6 passed / 0 failed**。 <<MET>>
- [x] **AC5 NOT_RUN**：真实 UI 手势/IME/多屏/DPI/系统主题/托盘、真实进程重启 = NOT_RUN。 <<MET>>
- [x] **AC6 门禁与证据**：`check.ps1`（默认 + `-TaskPath`）PASS；无 Core/wire/契约/DDL diff；证据含日志 EXIT。 <<MET>>


## r1 处置记录（2026-11-10，对 `bd6defc84` 的 changes_requested）

- **R1-001（P2，已修）**：`SaveReadingPreferencesAsync` 改为 **dirty-only**（与 `_appliedPreferences` 快照比较，只发变化字段；无变化不发）；`ApplyReadingPreferencesAsync` 增加 `Mode` 与 `VerticalDirection`（direction=vertical 不再被忽略）；测试收紧（只改 Zoom 时 Mode/Direction/DoublePage/Layout 均 null；mode/vertical 应用测试；无脏不发）。
- **R1-002（P2，已修）**：allowed_paths 补 `ReaderReadingPreferencesTests.cs`。
- **R1-003（P3，已补）**：partial 负向断言/mode/vertical/无变化不发送测试。
- **R1-004（P3，已修）**：AC4 测试名改为 `ReaderReadingPreferencesTests`（5 passed）。
- **R1-005（P3，已修）**：`base_commit` 校准 `034962ea7`。


## r2 处置记录（2026-11-10，对 `9b1837e00` 的 changes_requested）

- **R2-001（P2，已修）**：README AC4/日志说明改为 **6 passed**、App 全量重跑 **873 passed / 0 failed / 11 skipped**（新增 mode/vertical 保存测试）；Canonical 3 行刷新。
- **R2-002（P3，已修）**：`Mode`/`VerticalDirection` 改为可写（public set），提供用户修改路径。
- **R2-003（P3，已补）**：新增 `ChangingModeOrVerticalSendsOnlyThatField`（改 Mode → 只发 Mode；改 VerticalDirection → Direction=vertical 且 Mode null）。

## 证据计划（L2）

`verification/FEA-14-READ-2/`：`logs/`（App.Tests 定向/全量、门禁）、截图/NOT_RUN 声明（无交互会话则 NOT_RUN）、复现命令。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| temp | `G:\CODEX\New Manga.workspace\FEA-14-READ-2\`（如需要） | NOT_APPLICABLE | — | — | 仓外，不提交 |
| user-data | `%APPDATA%\com.newmanga.desktop` | NOT_APPLICABLE | — | — | 只读；测试用 FakeHostController |
| build | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 复用现有 .NET/Avalonia 环境 |
| worktree | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 主树实现 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-RD2-001 | READ-2 | `verification/FEA-14-READ-2/logs/dotnet-app-tests.log` | `-` | `2958f7b6a7e420bb5786c34b8a0ed13340a2ddb1aaa7843d41b63ef5b841845e` | CANONICAL |
| EV-RD2-002 | READ-2 | `verification/FEA-14-READ-2/logs/reader-reading-prefs.log` | `-` | `81a1d57212d03d2ad5ab44c712027232f2b799369f9f45c9b521c2e32732d780` | CANONICAL |
| EV-RD2-003 | READ-2 | `verification/FEA-14-READ-2/README.md` | `-` | `4214695f37a7ae21e57727fd883a73f25580385b2c80c76f42ea82a6139d8259` | CANONICAL |

## Closeout Record

- 未开始（2026-11-10 scope 冻结，`ready`）。
