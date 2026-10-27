---
id: READER-SELECTOR-UI-1
title: book/chapter 选择器（替代手填 id）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_goal_auto_except_recommended
suggested_owner: saber-ui-spec
owner: saber-ui-spec
reviewer: dsh
depends_on: []
base_commit: 558a48a76
branch: task/READER-SELECTOR-UI-1
worktree: G:/CODEX/New Manga.workspace/worktrees/READER-SELECTOR-UI-1
integration_commit: null
delivery_head: 05a55e1bec81d8500113dd8613f618badeb2ca56
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/READER-SELECTOR-UI-1
allowed_paths:
  - doc/tasks/READER-SELECTOR-UI-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/READER-SELECTOR-UI-1/**
  - G:/CODEX/New Manga.workspace/task-envs/READER-SELECTOR-UI-1/**
  - G:/CODEX/New Manga.workspace/worktrees/READER-SELECTOR-UI-1/**
---

# READER-SELECTOR-UI-1：book/chapter 选择器

> 交付状态：**ready-for-integration**（实现 `05a55e1be` + 证据 + Handoff 已完成；待 DSH 复核/集成；Owner 不自审）。
> 说明：卡面 base 记 `49c9e7f24`；按 DSH 指令分支从当前 HEAD **`558a48a76`** 创建。

## 背景

SETTINGS-PROFILE-UI-1 的「Provider 绑定」scope=book/chapter 仍需手填 id；书架/阅读器已有真实书与章节数据。

## Acceptance Criteria

- [x] **AC1 书选择**：scope=book/chapter 时提供书本下拉（`library_list_books`）与章节下拉（`list_chapters`），显示书名/章名而非裸 id。→ **MET**：`ProviderBindingsSection` 新增书籍/章节下拉；书籍来自 `RefreshBooksAsync()+Snapshot.Books`（`library_list_books`），章节来自 `IHostController.ListChaptersAsync`（`list_chapters`）；显示 Title。
- [x] **AC2 联动**：选书→加载章节；切换 scope 类型重置选择；未选时禁用 bindings 提交并提示。→ **MET**：选书触发章节加载并默认首章；切换 scope 重置书籍/章节与章节列表；未选齐时「绑定」禁用 + 选择状态提示；空库/无章节书有明确空态。
- [x] **AC3 测试**：Headless 覆盖「选书→章节加载→bindings 参数含真实 id」；空库空态。→ **MET**：5 项 headless（章节 scope 全链路真实 id、book scope、空库、无章节+scope 重置、选章后可提交）。证据：`reader-selector-ui/*.json`。
- [x] **AC4 回归**：test.ps1 全绿（≥210）；vitest 60/567；pytest 无新增失败。→ **MET**：test.ps1 **215/215, 0 skipped**（61/55/99）；vitest **60/567**；pytest **3F/2772P/9S**（同一组 3 失败，0 新增）。
- [x] **AC5 门禁**：check.ps1 -TaskPath PASS；64-hex pin；Handoff。→ **MET**：check PASS；11 条 64-hex pin；Handoff 含 Record Decision。

## Record Decision（摘要，完整版在 Handoff / REPORT）

| 项 | 决定 |
|---|---|
| 数据源 | 书籍复用 `Snapshot.Books`（先 `RefreshBooksAsync`）；章节复用既有 `ListChaptersAsync`；不新增 Host 命令/seam |
| 显示 | `BookSummary.Title` / `ChapterSummary.Title`（空标题回退 id） |
| 联动 | 选书加载章节并默认首章；切 scope 重置；book scope 隐藏章节下拉 |
| 提交边界 | 未选齐 → 禁用 + 提示；本地校验后仍由 Core 复核；0 命令调用 |
| 空态 | 空库/无章节书各自提示，不假装可提交 |
| 兼容 | 移除手填 id 输入框；更新既有 bindings 测试走选择器 |

## 实现摘要

- `Views/ProviderBindingsSection.cs`（新，自 ProfileSections 拆出）：书籍/章节选择器、scope 联动、状态提示、提交禁用/校验、空态。
- `Views/ProfileSections.cs`：移除旧手填 id 版本。
- `Views/Pages.cs`：Bindings 接线注入 `listBooks`/`listChapters`。
- `tests/NewManga.App.Tests/ReaderSelectorUiTests.cs`（新，5 项）；`SettingsProfileUiTests.cs` bindings 用例改选择器路径。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| RS-TEST-SUMMARY | AC4 | verification/READER-SELECTOR-UI-1/test/summary.json | 05a55e1bec81d8500113dd8613f618badeb2ca56 | a6171f8fb0c9b39bf85940dad971a94f20bf3ccf6ae4ef60eddc7854a4413daa | CANONICAL |
| RS-TEST-LOG | AC4 | verification/READER-SELECTOR-UI-1/test/dotnet-test-Debug.log | 05a55e1bec81d8500113dd8613f618badeb2ca56 | 3f281c65a9d2392833171dd24264a2dcde404d7ecfca91db9eb379f9937a4561 | CANONICAL |
| RS-VITEST | AC4 | verification/READER-SELECTOR-UI-1/test/vitest.log | 05a55e1bec81d8500113dd8613f618badeb2ca56 | f18be061be45285747c7f13e78476cbc69611e934d6f3029490b0456a19c5ace | CANONICAL |
| RS-PYTEST | AC4 | verification/READER-SELECTOR-UI-1/test/pytest.log | 05a55e1bec81d8500113dd8613f618badeb2ca56 | ea6bf1e95ecd9896a25c7ef0db4a91394e0d06e93ad6ba7a94c049d479137ffc | CANONICAL |
| RS-TEST-PS1-LOG | AC4 | verification/READER-SELECTOR-UI-1/test/test.ps1-final.log | 05a55e1bec81d8500113dd8613f618badeb2ca56 | da5d569d1a1ef5790577045543f27750a9f8950af411e6153e1d747078d7f2dc | CANONICAL |
| RS-CHAPTER-SCOPE | AC1/AC2/AC3 | verification/READER-SELECTOR-UI-1/reader-selector-ui/chapter-scope.json | 05a55e1bec81d8500113dd8613f618badeb2ca56 | 8b791b5d7500d744e9aafd0f39b1421773f30f32114d3aa95f800360aec503cf | CANONICAL |
| RS-BOOK-SCOPE | AC1/AC3 | verification/READER-SELECTOR-UI-1/reader-selector-ui/book-scope.json | 05a55e1bec81d8500113dd8613f618badeb2ca56 | 0573cb4361f2d0c048e27379c8123467a64f743d1c40ba06d6d0691dee455b87 | CANONICAL |
| RS-EMPTY-LIBRARY | AC2/AC3 | verification/READER-SELECTOR-UI-1/reader-selector-ui/empty-library.json | 05a55e1bec81d8500113dd8613f618badeb2ca56 | 0a607fc1bee74cf13c9e3a4e01100edcdbfc4f57f09c3fed9d8d0e0e18546dce | CANONICAL |
| RS-CHAPTERLESS-SCOPE | AC2/AC3 | verification/READER-SELECTOR-UI-1/reader-selector-ui/chapterless-and-scope-switch.json | 05a55e1bec81d8500113dd8613f618badeb2ca56 | 17981ddab72c81de5e3ef00a5ec3b8a3d58fe62579394a31571ba810cd8963b8 | CANONICAL |
| RS-CHAPTER-READY | AC2/AC3 | verification/READER-SELECTOR-UI-1/reader-selector-ui/chapter-ready.json | 05a55e1bec81d8500113dd8613f618badeb2ca56 | 2f1079dd61c68f348b9150d03d71aa6ddefbf7f88de591975487fa7404863d58 | CANONICAL |
| RS-REPORT | AC5 | verification/READER-SELECTOR-UI-1/REPORT.md | 05a55e1bec81d8500113dd8613f618badeb2ca56 | e973ec85299fe1f20de1b8716ee743ef0c018b6dec15d5ee82756c468c34939e | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/READER-SELECTOR-UI-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/READER-SELECTOR-UI-1 | `evidence/`（test/reader-selector-ui/logs） | 2026-10-27 收口时存在；`reader-selector-ui/*.json` 与 `test/summary.json` 引用其路径；未移动/未删除；关闭时由 DSH 复核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写（owner 交付 `05a55e1be`，待 DSH 集成验证与独立 Review）。
- canonical_evidence_status：`complete`（11 条 CANONICAL pin，指向 delivery_head）。
- resource_closeout_status：`pending`（task-env 保留引用）。
- 删除、迁移、归档数量/字节数：0（本任务未删除任何文件；真实 `%APPDATA%` 未触碰）。
- 未关闭项及保留原因：真实 Core 读取由既有 READER-LIBRARY-WIRE-1/CHAPTER-SELECTOR-1 测试覆盖；本卡 AC 未要求真机截图（行为由 5 项 headless 覆盖）；书籍列表刷新为进入设置页触发（无跨页 live 同步）；IMPORT-EXPORT-UI-1 若先落地需 rebase；需独立 Review。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
