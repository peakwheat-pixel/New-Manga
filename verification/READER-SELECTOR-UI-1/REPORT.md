# READER-SELECTOR-UI-1 验证报告（book/chapter 选择器，替代手填 id）

- Task：`doc/tasks/READER-SELECTOR-UI-1.md`（team task-46）
- Branch / worktree：`task/READER-SELECTOR-UI-1` / `G:/CODEX/New Manga.workspace/worktrees/READER-SELECTOR-UI-1`
- Base：`558a48a76`（卡面 `49c9e7f24`，按 DSH 指令用当前 HEAD）
- 未改 Python Core / 协议 / Host 契约 / 旧壳；未 push / gc / prune；不显示/记录 secret；未伪造结果。

## 1. 结论

| AC | 结论 | 证据 |
|---|---|---|
| AC1 书选择 | **MET** | Provider 绑定卡的 scope=book/chapter 时显示两次真实下拉：书籍（`library_list_books`，显示书名）、章节（`list_chapters`，显示章名），不再裸填 id。 |
| AC2 联动 | **MET** | 选书→自动加载该书的 `list_chapters` 并默认选中首章；切换 scope 类型重置书籍/章节选择与章节列表；未选书/未选章时「绑定」按钮禁用且提示原因；空库、无章节书均有明确空态提示。 |
| AC3 测试 | **MET** | 5 项 headless：选书→章节加载→bindings 参数含真实 `book_id`/`chapter_id`；book scope 只含 book_id；空库空态+禁用提交+0 调用；无章节书空态；scope 切换重置；选章后提交可用。证据：`reader-selector-ui/*.json`。 |
| AC4 回归 | **MET** | `scripts/test.ps1` **215/215 passed, 0 skipped**（coreclient 61 / host 55 / app 99）；vitest **60 files / 567 tests**；pytest **3F/2772P/9S**（与基线同一组 3 失败，0 新增）。 |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS；11 条 64-hex pin；Handoff 含 Record Decision。 |

## 2. 选择器结构（Provider 绑定卡）

```
Scope 类型（global / book / chapter）
书籍（book，来自 library_list_books）      [ComboBox: "我的漫画" …]        ← scope=book/chapter 时显示
章节（chapter，选书后来自 list_chapters）  [ComboBox: "第一话","第二话" …]  ← scope=chapter 时显示
选择状态提示                               ← 空库 / 请选择书籍 / 已加载 N 章 / 该书籍没有章节
能力（capability） / Provider profile
[绑定] [清除绑定] [解析当前绑定] [刷新列表]    ← 未选齐时「绑定」禁用
```

实现：`Views/ProviderBindingsSection.cs`（从 `ProfileSections.cs` 拆出并重写选择器逻辑）；`Views/Pages.cs` 注入 `listBooks`（`RefreshBooksAsync()` + `Snapshot.Books`，即 `library_list_books`）与 `listChapters`（`IHostController.ListChaptersAsync`，即 `list_chapters`）；不新增 Host 命令、不改 dispatcher。

## 3. Record Decision

| 项 | 决定 |
|---|---|
| 书籍数据源 | 复用 `IHostController.Snapshot.Books`（`library_list_books` 结果），打开设置页/刷新时先 `RefreshBooksAsync()`；不新增 seam 方法 |
| 章节数据源 | 复用既有 `IHostController.ListChaptersAsync(bookId)`（`list_chapters`） |
| 显示 | 下拉显示 `BookSummary.Title` / `ChapterSummary.Title`（标题为空时回退 id），不展示裸 id 作为主标签 |
| 联动 | 选书触发 `list_chapters` 并自动选中首章；切 scope 重置书籍/章节选择与章节列表；book scope 不显示章节下拉 |
| 提交边界 | 未选齐（book 需书、chapter 需书+章）→ 「绑定」禁用 + 状态/提示说明；点击也做本地校验，0 命令调用 |
| 空态 | 空库 →「书库为空：请先在书架导入或创建书籍」；书无章节 →「该书籍没有章节：请先在书架/阅读器中创建或导入章节」 |
| 兼容 | 旧手填 `book_id/chapter_id` 输入框移除；`SettingsProfileUiTests` 的 bindings 用例改为选择器路径（真实 book-0） |
| 并发 | `route-research` 的 IMPORT-EXPORT-UI-1 同改 `Views/**`；本卡仅动 Provider 绑定卡与 Pages 接线，冲突按先落地者为准、后落地者 rebase（Handoff 已注明） |

## 4. 实现摘要（全部 `apps/desktop-avalonia/**`）

| 文件 | 改动 |
|---|---|
| `Views/ProviderBindingsSection.cs`（新，自 ProfileSections 拆出） | 书籍/章节选择器、scope 联动、状态提示、提交禁用/校验、空态。 |
| `Views/ProfileSections.cs` | 移除旧 `ProviderBindingsSection`（手填 id 版本）。 |
| `Views/Pages.cs` | Bindings 接线新增 `listBooks`（`RefreshBooksAsync`+`Snapshot.Books`）与 `listChapters`（`ListChaptersAsync`）。 |
| `tests/NewManga.App.Tests/ReaderSelectorUiTests.cs`（新，5 项） | 章节 scope 全链路（真实 id）、book scope、空库、无章节+scope 重置、选章后提交可用。 |
| `tests/NewManga.App.Tests/SettingsProfileUiTests.cs` | bindings 用例改为选择器路径（book-0）。 |

## 5. 验证证据

| AC/场景 | 实际命令/步骤 | 环境 | 结果 | 产物 |
|---|---|---|---|---|
| AC1/AC3 章节 scope | `ChapterScope_SelectBook_LoadsChapters_AndBindingUsesRealIds` | Avalonia Headless 11.3.22 + FakeHostController（Snapshot books = `library_list_books`；`ChaptersByBook` = `list_chapters`） | 书下拉 1 项「我的漫画」；选书后章节 2 项「第一话/第二话」并自动选首章；绑定参数 `chapter_id=chapter-2`（scope 无 book_id） | `reader-selector-ui/chapter-scope.json` |
| AC1/AC3 book scope | `BookScope_SelectBook_BindsBookId_AndKeepsChapterHidden` | 同上 | book scope 无章节下拉；绑定参数 `book_id=book-0` | `reader-selector-ui/book-scope.json` |
| AC2 空库 | `EmptyLibrary_ShowsEmptyState_AndDisablesBindingSubmit` | 同上（`ReadySnapshot()` 空书库） | 书下拉 0 项、提示「书库为空…」、绑定按钮禁用、0 次绑定调用 | `reader-selector-ui/empty-library.json` |
| AC2 无章节/切换重置 | `BookWithoutChapters_ShowsEmptyState_AndScopeSwitchResetsSelections` | 同上 | 选书后章节 0 项 +「该书籍没有章节」；切 global/book 后书籍/章节选择均 -1、章节列表清空 | `reader-selector-ui/chapterless-and-scope-switch.json` |
| AC2 选章后可提交 | `SelectedBook_LoadsChaptersOnlyOncePerSelection_AndHintExplainsMissingChapter` | 同上 | 选书→1 章→「绑定」可用 | `reader-selector-ui/chapter-ready.json` |
| AC3 回归 | `SettingsProfileUiTests.BindingsSection_SetClear_WithGlobalAndBookScopes_SendExactArguments`（更新） | 同上 | global 与 book 参数仍精确（book-0），未回归 | `test/results-app.trx` |
| AC4 全量 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence` | Windows 10.0.26300 | **215/215**（61/55/99），0 skipped | `test/summary.json`、`test/dotnet-test-Debug.log`、`test/results-*.trx` |
| AC4 vitest / pytest | `npm test`（主仓）/ `PYTHONPATH=src python -m pytest -q`（worktree） | 旧壳/Python 未改 | 60 files / 567 tests；3F/2772P/9S（0 新增） | `test/vitest.log`、`test/pytest.log` |
| AC5 治理 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/READER-SELECTOR-UI-1.md` | 本卡 + 文档提交 | PASS | 任务卡 pin |

## 6. 遗留 / 未关闭项（记录不阻塞）

1. **真实 Host 链路**：选择器数据来自 `IHostController` seam（FakeHostController 在测试中代表 `library_list_books`/`list_chapters`）；真实 Core 读取由既有 READER-LIBRARY-WIRE-1 / CHAPTER-SELECTOR-1 测试覆盖，本卡不重复写真实数据根。
2. **真机截图未附**：本卡 AC 未要求截图；选择器行为由 5 项 headless 覆盖（如 DSH 需要真机视觉证据，可补一次设置页滚动截屏）。
3. **章节选择器仅在 chapter scope 显示**：book scope 只显示书籍；若未来需要 book scope 下预览章节，可再扩展。
4. **书籍列表刷新时机**：进入设置页 / 刷新列表时读取；书架新增书籍后需刷新设置页一次才出现（未做跨页 live 同步）。
5. **并发**：IMPORT-EXPORT-UI-1 若先落地并改动 `Pages.cs`，本卡 rebase 后需重跑 gate（Handoff 已注明）。
6. 需独立 Review（Owner 不自审）。

## 7. 复现

```pwsh
# 1) 全量回归（215 项，含 5 项选择器 headless）
pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 `
  -EvidenceDirectory G:\CODEX\New Manga.workspace\task-envs\READER-SELECTOR-UI-1\evidence

# 2) 只看选择器测试
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj `
  -c Debug --filter "FullyQualifiedName~ReaderSelectorUiTests"
```
