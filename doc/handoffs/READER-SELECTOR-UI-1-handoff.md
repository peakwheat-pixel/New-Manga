---
task_id: READER-SELECTOR-UI-1
author: saber-ui-spec (DSH team)
recipient: DeepSeek Harness
base_commit: 558a48a76
delivery_head: 05a55e1bec81d8500113dd8613f618badeb2ca56
status: ready-for-integration
---

# Handoff：READER-SELECTOR-UI-1（book/chapter 选择器，替代手填 id）

## 交付结果

实现提交 **`05a55e1bec81d8500113dd8613f618badeb2ca56`**（branch `task/READER-SELECTOR-UI-1`，worktree `G:/CODEX/New Manga.workspace/worktrees/READER-SELECTOR-UI-1`；卡面 base `49c9e7f24`，按 DSH 指令从当前 HEAD `558a48a76` 建分支）；本 Handoff 与任务卡 pin 在后续文档提交中记录。未改 Python Core / 协议 / Host 契约 / 旧壳；未 push / gc / prune；不显示/记录 secret；未伪造结果。

| AC | 结论 | 说明 |
|---|---|---|
| AC1 书选择 | **MET** | Provider 绑定卡 scope=book/chapter 显示书籍下拉（`library_list_books`，书名）与章节下拉（`list_chapters`，章名），取代裸 id 输入。 |
| AC2 联动 | **MET** | 选书→加载章节并默认首章；切 scope 重置选择与章节列表；未选齐时「绑定」禁用 + 提示；空库/无章节书明确空态。 |
| AC3 测试 | **MET** | 5 项 headless：章节 scope 选书→章节→bindings 参数含真实 `chapter_id`；book scope `book_id`；空库空态+禁用+0 调用；无章节+scope 重置；选章后可提交。 |
| AC4 回归 | **MET** | test.ps1 **215/215**（61/55/99，0 skipped）；vitest **60/567**；pytest **3F/2772P/9S**（同一组 3 失败，0 新增）。 |
| AC5 门禁 | **MET** | check.ps1 -TaskPath PASS；11 条 64-hex pin；本 Handoff 含 Record Decision。 |

## 选择器结构

```
Scope 类型（global / book / chapter）
书籍（book，来自 library_list_books）      [ComboBox: 书名 …]           ← scope=book/chapter 时显示
章节（chapter，选书后来自 list_chapters）  [ComboBox: 章名 …]           ← scope=chapter 时显示
选择状态提示                               ← 空库 / 请选择书籍 / 已加载 N 章 / 该书籍没有章节
能力（capability） / Provider profile
[绑定] [清除绑定] [解析当前绑定] [刷新列表]  ← 未选齐时「绑定」禁用
```

数据来源：`Views/Pages.cs` 为 `ProviderBindingsSection` 注入两个委托——
- `listBooks` = `RefreshBooksAsync()` + `IHostController.Snapshot.Books`（`library_list_books`）；
- `listChapters` = `IHostController.ListChaptersAsync(bookId)`（`list_chapters`）。
未新增 seam 方法/Host 命令/dispatcher 变更。

## Record Decision

1. **复用既有读取面**：书籍下拉直接用 `Snapshot.Books`（README/书架同一数据源，先 `RefreshBooksAsync` 保证新鲜）；章节用既有 `ListChaptersAsync`。不新增 Host 命令，不引入第二个书籍查询入口。
2. **显示**：下拉显示 `BookSummary.Title` / `ChapterSummary.Title`，空标题回退 id；不把裸 id 作为主标签（满足 AC1）。
3. **联动语义**：选书即加载章节并默认选中第一项（chapter scope 可直接提交）；切 scope 类型重置书籍/章节选择、清空章节列表；book scope 隐藏章节下拉（book_id 绑定不需要章节）。
4. **提交边界**：未选齐（book 无书 / chapter 无书或无章）→「绑定」禁用 + 选择状态提示；点击也做本地校验并给出原因，0 命令调用；Core 仍独立校验 id 存在性（`SETTINGS_ITEM_NOT_FOUND` 等 typed 错误照常显示）。
5. **空态**：空书库 →「书库为空：请先在书架导入或创建书籍」；书无章节 →「该书籍没有章节：请先在书架/阅读器中创建或导入章节」；均不发送命令。
6. **兼容/回归**：移除旧手填 `book_id/chapter_id` 输入框；`SettingsProfileUiTests.BindingsSection_SetClear_WithGlobalAndBookScopes...` 改为选择器路径（真实 book-0），global 行为不变。
7. **并发**：`route-research` 的 IMPORT-EXPORT-UI-1 可能同改 `Views/**`；本卡改动仅 `ProviderBindingsSection.cs`、`ProfileSections.cs`（删旧类）、`Pages.cs` 接线与测试；冲突按先落地者为准，后落地者 rebase 并重跑 gate。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境 | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1/AC3 章节 scope | `ChapterScope_SelectBook_LoadsChapters_AndBindingUsesRealIds` | Avalonia Headless 11.3.22 + FakeHostController（Snapshot books=`library_list_books`；ChaptersByBook=`list_chapters`） | 书「我的漫画」；章节「第一话/第二话」；绑定 `chapter_id=chapter-2`（scope 无 book_id） | `reader-selector-ui/chapter-scope.json` |
| AC1/AC3 book scope | `BookScope_SelectBook_BindsBookId_AndKeepsChapterHidden` | 同上 | book scope 无章节下拉；绑定 `book_id=book-0` | `reader-selector-ui/book-scope.json` |
| AC2 空库 | `EmptyLibrary_ShowsEmptyState_AndDisablesBindingSubmit` | 空书库 | 0 项、「书库为空」、按钮禁用、0 调用 | `reader-selector-ui/empty-library.json` |
| AC2 无章节/重置 | `BookWithoutChapters_ShowsEmptyState_AndScopeSwitchResetsSelections` | 有书无章节 | 0 章节 + 提示；切 scope 后书籍/章节均 -1、列表清空 | `reader-selector-ui/chapterless-and-scope-switch.json` |
| AC2 可提交 | `SelectedBook_LoadsChaptersOnlyOncePerSelection_AndHintExplainsMissingChapter` | 有书有章节 | 选章后「绑定」可用 | `reader-selector-ui/chapter-ready.json` |
| AC4 全量 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence` | Windows 10.0.26300 | **215/215**（61/55/99），0 skipped | `test/summary.json`、`test/dotnet-test-Debug.log`、`test/results-*.trx` |
| AC4 vitest / pytest | `npm test`（主仓）/ `PYTHONPATH=src python -m pytest -q`（worktree） | 旧壳/Python 未改 | 60 files / 567 tests；3F/2772P/9S（0 新增） | `test/vitest.log`、`test/pytest.log` |
| AC5 治理 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/READER-SELECTOR-UI-1.md` | 本卡 + 文档提交 | PASS | 任务卡 pin |

## 接收方式

- 分支/worktree：`task/READER-SELECTOR-UI-1` / `G:/CODEX/New Manga.workspace/worktrees/READER-SELECTOR-UI-1`；delivery head `05a55e1be`。
- 复现：`verification/READER-SELECTOR-UI-1/REPORT.md §7`。
- 前置：无 sidecar 需求（headless）；真实链路读取无新增网络/磁盘依赖。
- 需要 DSH 做：独立 Review（Owner 不自审）→ 重跑 test.ps1（215/215；注意其它 Agent 的 NewManga.App 占用全局互斥体时 LegacyShellRealTests 会假失败）→ 集成 → closeout。
- 并发说明：IMPORT-EXPORT-UI-1 若先落地并改动 `Views/Pages.cs`，本卡 rebase 后重跑 gate；冲突以先落地者为准。

## 下一任务建议（必填）

- Task ID / 标题：**无必须由我立即释放的实现任务**；可选后续（由 DSH 裁决）：
  1. `SETTINGS-PROFILE-UI-2`：book scope 下预览章节（当前 book scope 不显示章节）；
  2. `APP-TEST-EVIDENCE-FLAKE-1`：App.Tests 证据文件并发写 flake 清理。
- 推荐 Agent / Reviewer：UI 后续 = saber-ui-spec；flake 清理 = Antigravity/Codex；Reviewer = 未参与实现者（DSH 排班）。
- 推荐原因与前置依赖：选择器已可用；book scope 章节预览属体验增强；flake 影响 gate 稳定性但与本卡无关。
- Recovery point：仓库 `G:/CODEX/New Manga`；delivery head `05a55e1be`；base `558a48a76`。
- 允许修改路径：`apps/desktop-avalonia/**`、新任务卡、STATUS/PLAN/LEDGER、`verification/<新任务>/**`。
- 禁止范围：不改 Core 语义/协议/Host 契约/旧壳；不显示/记录 secret；不 push/gc/prune。
- 交付物：后续实现 + headless 测试 + 证据 + Handoff。
- 验证命令与完成 Gate：test.ps1 全绿（≥215）、vitest 60/567、pytest 无新增失败、`check.ps1 -TaskPath` PASS、64-hex pin、独立 Review。
- 可直接转发给 Agent 的指令：

```text
作为独立 Reviewer（未参与实现），复核 READER-SELECTOR-UI-1（delivery 05a55e1be，walkthrough 见 doc/handoffs/READER-SELECTOR-UI-1-handoff.md 与 verification/READER-SELECTOR-UI-1/REPORT.md）。
只读：不要修改代码。核对 AC1–AC5 与 11 条 pin（sha256 与文件一致）；抽查 Provider 绑定卡在 book/chapter scope 的选择器行为（书籍来自 Snapshot.Books/RefreshBooksAsync、章节来自 ListChaptersAsync、显示 Title、切 scope 重置、未选齐禁用提交、空库/无章节空态）；确认 bindings 参数使用真实 book_id/chapter_id 且未新增 Host 命令；重跑 pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1（应 215/215；注意其它 Agent 的 NewManga.App 占用全局互斥体时 LegacyShellRealTests 会假失败）与 dotnet test --filter FullyQualifiedName~ReaderSelectorUiTests（应 5/5）；给出 PASS / 有条件 PASS / 返修 结论与具体证据行。
```

## 风险与遗留

1. 真实 Core 读取未在本卡 UI 测试中执行（用 FakeHostController seam）；由既有 READER-LIBRARY-WIRE-1/CHAPTER-SELECTOR-1 冻结 sidecar 测试覆盖。
2. 本卡 AC 未要求真机截图；选择器行为由 5 项 headless 覆盖（若 DSH 需要视觉证据可补一次设置页截屏）。
3. 书籍列表在进入设置页/刷新时读取；书架新增书籍后不跨页 live 更新。
4. book scope 不显示章节（book 级绑定只需 book_id）；如需 book 下预览章节另开 Task。
5. 与 IMPORT-EXPORT-UI-1 的 `Views/**` 并发需 rebase（先落地者为准）。
6. 需独立 Review（Owner 不得自审）。
