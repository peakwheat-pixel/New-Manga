# CHAPTER-SELECTOR-1 验证报告（多章选择器 + 多书入口）

- Task: `doc/tasks/CHAPTER-SELECTOR-1.md`（team task-25）
- Branch / worktree: `task/CHAPTER-SELECTOR-1` / `G:/CODEX/New Manga.workspace/worktrees/CHAPTER-SELECTOR-1`
- Base: `10a0308c1`（READER-PROGRESS-1 delivery head；任务卡冻结 base 仍记 `230164c5c`）
- 未 push；未改协议/Host 契约语义；未改 Python Core；未改旧壳；未启动旧壳。

## 1. 结论

| AC | 结论 | 证据 |
|---|---|---|
| AC1 章节列表 + 切章 | **MET** | 阅读器工具栏新增「章：…」上下文 + 章节下拉 + 上一章/下一章按钮；数据来自真实 `list_chapters`（经 `HostRuntime.ListChaptersAsync`，与页图/投影共用 reader I/O 串行门）；切章后重新投影并渲染该章页数，当前书/章始终可见。真机：书 A 第 1 章 8 页 →「下一章」→ 第二章 4 页（截图 02/03 + wire 投影 chapter_id 更替）。 |
| AC2 多书入口 | **MET** | 书架书卡双击 / 详情面板「进入阅读」打开**该书**（不再固定第一本第一章）；`OpenReaderForBookAsync(bookId, chapterId)` 支持任意书/章，切书前 flush 当前进度。真机：书架两本书，从第二本详情进入 → 阅读器显示副本B 3 页（截图 01/04 + wire book_id）。 |
| AC3 测试 | **MET** | Headless 12 项（切章更新页数/投影/上下文、上一章/下一章边界、多书分别打开、打开他书 flush、默认入口仍开第一本、空 chapter list 降级、工具栏点击不翻页、沉浸窗上下文）；真机双书三章数据根验证；Host 真 sidecar 集成 2 项（`list_chapters` 与投影一致、并发 chapter/projection 读取被串行化）。 |
| AC4 回归 | **MET** | `scripts/test.ps1` **145/145 passed, 0 skipped**（coreclient 40 / host 42 / app 63；上一卡 131 + 本轮 14）；旧壳 vitest **60 files / 567 tests**；pytest **3F/2739P/9S**（与基线一致，0 新增）。 |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS；下方 64-hex pin；`doc/handoffs/CHAPTER-SELECTOR-1-handoff.md`。 |

## 2. 实现摘要（全部 `apps/desktop-avalonia/**`）

| 文件 | 改动 |
|---|---|
| `src/NewManga.App/Services/IHostController.cs` | 新增 `ListChaptersAsync(bookId)`（只读章节列表）。 |
| `src/NewManga.App/Services/HostController.cs` | 实现：Host 未就绪/读取失败 → 空列表（选择器隐藏，退回单章行为），不抛 UI 异常。 |
| `src/NewManga.App/Services/NullHostController.cs` | 空列表实现。 |
| `src/NewManga.Host/HostRuntime.cs` | `ListChaptersAsync` 与 `GetReaderProjectionAsync` 统一走 `_readerIoGate`（core_service 严格一问一答；此前仅页图/save 走门，chapter list 与投影并发会串响应）。 |
| `src/NewManga.App/Views/Pages.cs` | 书卡双击 → `OpenReaderRequested`；详情面板新增「进入阅读」按钮（`OpenReaderFromDetail`）；`RequestOpenReader` 供窗口/测试调用。 |
| `src/NewManga.App/Views/ReaderWorkbenchPages.cs` | 工具栏改为 Grid 两行上下文（书/章 + 摘要）；章节下拉 `ChapterSelector` + 上一章/下一章按钮（单章隐藏、边界禁用）；`LoadChapters`/`SetBookContext`/`HideChapterSelector`/`SelectAdjacentChapter`/`CurrentChapterIndex`；`ChapterSelectionRequested` 事件；恢复页时同步选择器；工具栏按钮按主题着色；**指针命中判定**：只有落在页图/webtoon 栈上的按压才翻页（工具栏/下拉/滚动条不再误触发翻页）。 |
| `src/NewManga.App/Views/MainWindow.axaml.cs` | `OpenReaderForBookAsync(bookId, chapterId)`（切书/切章前 flush 进度 → 投影 resume → 导航 → 填充章节列表）；`PopulateChaptersAsync`（丢弃过期响应）；书架事件与章节事件接入；`LastReaderNavigation`/`CurrentReaderBookId`/`CurrentReaderChapterId` 供测试与证据；沉浸窗显示上下文但隐藏选择器。 |
| `tests/NewManga.App.Tests/ReaderChapterSelectorTests.cs`（新，12 项） | 见 §1 AC3。`FakeHostController` 增加多书/多章脚本映射与 `ListChaptersAsync`。 |
| `tests/NewManga.Host.Tests/HostReaderChaptersIntegrationTests.cs`（新，2 项） | 真 sidecar：`list_chapters` 与投影一致；12 个并发 chapter/projection 读取全部成功（证明串行门）。 |

## 3. 真机证据（AC3）

测试数据根 `task-envs/CHAPTER-SELECTOR-1/isolated-data`：BOOK-FIXTURE durable 状态副本（源 fixture 不动），由 `tools/dev/test-data` 同款脚本（本任务 workspace 副本 `runtime-logs/chapter-selector-data.py`）扩展出**书 A 第二章 4 页**与**副本 B（3 页）**；页记录使用新 page_id + 复制后的 managed 文件，原引用不被改写。

发布件 `task-envs/CHAPTER-SELECTOR-1/pkg/app/NewManga.App.exe`（Release single-file；`core-sidecar` junction 指向 FINAL-VALIDATION-1 打包件）；启动 `start-book-fixture.ps1 -ExtraArgs '--demo-write'`；host.log：`mode=ReadWrite reason=parity reached`。

| 步骤 | 结果 | 证据 |
|---|---|---|
| 书架 | 2 本（12 页 / 3 页），"已加载 2 本" | `screens/01-bookshelf-two-books.png` |
| 打开阅读器（默认书 A） | 书 A · 第 1 章 · **8 页**；下拉「第 1 章」；上一章禁用、下一章可用 | `screens/02-reader-chapter-selector.png` |
| 点「下一章」 | 重新投影到第二章：书 A · 第二章 测试章 · **4 页**；上下文与下拉同步；上一章可用、下一章禁用 | `screens/03-reader-chapter-2.png` + wire（`GetReaderProjection` chapter_id 由 `240bdba5…` → 第二章 id，`list_chapters` 重取） |
| 书架详情 →「进入阅读」第二本 | 阅读器切到副本B · 第 1 章 · 副本 · **3 页**；单章故选择器/切换按钮隐藏 | `screens/04-reader-book-b.png` + wire（`list_chapters(book=a5beee49…)`、`GetReaderProjection(book=a5beee49…)`、3 个 `resolve_page_resource`） |

`live-evidence.json.assertions` 全 true：两本书被列出、书 A 两章、默认投影 8 页、切章投影 4 页且同书、第二本书投影 book_id 匹配且 3 页、两本书都调用过 `list_chapters`、所有投影均 `start_position="resume"`。

## 4. 回归（AC4）

| 门 | 命令 | 结果 |
|---|---|---|
| Avalonia 全量 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence` | **145/145 passed, 0 skipped**（coreclient 40 / host 42 / app 63） |
| 旧壳 vitest | `cd apps/desktop/frontend && npm test`（主仓运行；`git diff 10a0308c1 -- apps/desktop/frontend` 为空） | **60 files / 567 tests passed** |
| pytest | `PYTHONPATH=src python -m pytest -q`（worktree 内，未改 Python） | **3 failed / 2739 passed / 9 skipped**（失败集合与基线相同，0 新增） |
| 治理 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/CHAPTER-SELECTOR-1.md` | PASS |

## 5. 已知遗留 / 未覆盖（记录不阻塞）

1. **真机只验证「详情面板进入阅读」**：书卡双击是同一 `OpenReaderRequested` 入口（headless 覆盖 `RequestOpenReader`），但自动化无法稳定注入双击手势；双击路径未在真机重复。
2. **下拉弹层未在真机展开验证**：Avalonia ComboBox 弹层是独立 popup 窗口，截图/点击工具无法稳定捕获；真机切章用「下一章」按钮走同一条 `ChapterSelectionRequested` → `OpenReaderForBookAsync` 路径（headless 已验证下拉选择事件）。
3. **沉浸窗不提供章节切换**（显示书/章上下文、隐藏选择器），避免全屏窗与主窗双状态；如需沉浸窗内切章，另开任务。
4. 章节列表不做翻页/搜索；百章以上书的列表性能未测（`list_chapters` 返回全量）。
5. 需独立 Review（Owner 不得自审）。

## 6. 复现

```pwsh
# 1) 回归（145 项）
pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory G:\CODEX\New Manga.workspace\task-envs\CHAPTER-SELECTOR-1\evidence

# 2) 构造双书三章测试数据根（源 fixture 不动）
python G:\CODEX\New Manga.workspace\worktrees\CHAPTER-SELECTOR-1\verification\CHAPTER-SELECTOR-1\runtime-logs\chapter-selector-data.py

# 3) 真机
pwsh -NoProfile -File apps/desktop-avalonia/scripts/start-book-fixture.ps1 `
  -AppExe G:\CODEX\New Manga.workspace\task-envs\CHAPTER-SELECTOR-1\pkg\app\NewManga.App.exe `
  -DataRoot G:\CODEX\New Manga.workspace\task-envs\CHAPTER-SELECTOR-1\isolated-data -ExtraArgs '--demo-write'
# 书架 → 阅读器（书 A 第 1 章）→ 下一章（4 页）→ 书架 → 第二本详情 → 进入阅读（3 页）
```
