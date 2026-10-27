---
task_id: CHAPTER-SELECTOR-1
author: saber-ui-spec (DSH team)
recipient: DeepSeek Harness
base_commit: 230164c5c
delivery_head: 126d055183b6852259b8fd292ca1c408c5fdd1b6
status: ready-for-integration
---

# Handoff：CHAPTER-SELECTOR-1（多章选择器 + 多书入口）

## 交付结果

实现提交 **`126d055183b6852259b8fd292ca1c408c5fdd1b6`**（branch `task/CHAPTER-SELECTOR-1`，worktree `G:/CODEX/New Manga.workspace/worktrees/CHAPTER-SELECTOR-1`，base `10a0308c1` = READER-PROGRESS-1 delivery head）；本 Handoff 与任务卡 pin 在后续文档提交中记录。未 push、未改 Python Core/旧壳/协议语义/Host 契约语义。

| AC | 结论 | 说明 |
|---|---|---|
| AC1 章节列表 | **MET** | 阅读器工具栏「书：… · 章：…」上下文 + `ChapterSelector`（`list_chapters`）+ 上一章/下一章按钮；单章隐藏、边界禁用；切章重投影并更新页数/布局。 |
| AC2 多书入口 | **MET** | 书卡双击 / 详情「进入阅读」打开该 `bookId`；切书/切章前 flush 当前进度；不再固定第一本第一章。 |
| AC3 测试 | **MET** | headless 12 项 + Host 真 sidecar 2 项（含 12 路并发读串行化）；真机双书三章数据根：书 A 8 页 → 下一章 4 页；第二本 3 页。 |
| AC4 回归 | **MET** | test.ps1 **145/145**；vitest **60/567**；pytest **3F/2739P/9S**（基线同）。 |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS；14 条 64-hex pin；本 Handoff。 |

### 代码变更（全部 `apps/desktop-avalonia/**`）

- `src/NewManga.Host/HostRuntime.cs`：`ListChaptersAsync` / `GetReaderProjectionAsync` 统一走 `_readerIoGate`（core_service 严格一问一答；chapter list 与投影并发会串响应）。
- `src/NewManga.App/Services/{IHostController,HostController,NullHostController}.cs`：`ListChaptersAsync(bookId)`（只读；失败降级空列表，不抛 UI 异常）。
- `src/NewManga.App/Views/Pages.cs`：书卡双击 → `OpenReaderRequested`；详情面板「进入阅读」（`OpenReaderFromDetail`）；`RequestOpenReader`。
- `src/NewManga.App/Views/ReaderWorkbenchPages.cs`：工具栏 Grid（两行上下文 + 上下章 + 下拉 + 沉浸）；`LoadChapters`/`SetBookContext`/`SelectAdjacentChapter`/`ChapterSelectionRequested`；仅页图/webtoon 栈上的按压翻页（工具栏/下拉/滚动条不再误翻页）；工具栏按钮主题色可读；章节标签去重「第 N 章」前缀。
- `src/NewManga.App/Views/MainWindow.axaml.cs`：`OpenReaderForBookAsync(bookId, chapterId)`（flush → resume 投影 → 导航 → 填充章节）、`PopulateChaptersAsync`（丢弃过期响应）、事件接线、`CurrentReaderBookId/ChapterId`、沉浸窗上下文。
- 测试：`tests/NewManga.App.Tests/ReaderChapterSelectorTests.cs`（12）、`tests/NewManga.Host.Tests/HostReaderChaptersIntegrationTests.cs`（2）；`FakeHostController` 增加多书/多章脚本。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC4 全量 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory G:/CODEX/New Manga.workspace/task-envs/CHAPTER-SELECTOR-1/evidence` | Windows 10.0.26300；`126d05518` | PASS 145/145（coreclient 40 / host 42 / app 63） | `verification/CHAPTER-SELECTOR-1/test/summary.json`、`test/dotnet-test-Debug.log`、`test/results-*.trx` |
| AC4 vitest | `cd apps/desktop/frontend && npm test`（主仓；`git diff 10a0308c1 -- apps/desktop/frontend` 为空） | 旧壳未改动 | PASS 60 files / 567 tests | `test/vitest.log` |
| AC4 pytest | `PYTHONPATH=src python -m pytest -q`（worktree；C:\Python314） | 未改 Python | 3F/2739P/9S（基线一致） | `test/pytest.log` |
| AC1 真机 | 启动 `start-book-fixture.ps1 -AppExe <pkg>/NewManga.App.exe -DataRoot <isolated-data> -ExtraArgs '--demo-write'`；打开阅读器（书 A 第 1 章 8 页）→ 点「下一章」 | 双书三章测试根（BOOK-FIXTURE 副本扩展）；发布件 29.4 MB + FINAL-VALIDATION-1 sidecar | PASS：第二章 4 页，上下文/下拉同步；wire 重新 `GetReaderProjection` + `list_chapters` | `live-evidence.json`、`screens/02-*.png`、`screens/03-*.png`、`runtime-logs/wire-real-machine.ndjson` |
| AC2 真机 | 书架（2 本）→ 第二本详情 →「进入阅读」 | 同上 | PASS：副本B · 第 1 章 · 3 页；wire `list_chapters(book=a5beee49…)` + 投影 | `screens/01-*.png`、`screens/04-*.png`、`live-evidence.json` |
| AC1 Host | `dotnet test ... --filter FullyQualifiedName~HostReaderChaptersIntegrationTests`（带 sidecar/fixture 环境） | 真 core_service | PASS 2/2：list_chapters 与投影一致、12 路并发读写全部成功 | `host/reader-chapters-list.json`、`host/reader-chapters-concurrent.json` |

明确未运行：书卡双击手势与 ComboBox 弹层的真机注入（Avalonia popup 为独立窗口，自动化无法稳定捕获/点击）；两条路径由 headless 覆盖，真机用同一事件链的按钮入口验证。沉浸窗内切章未实现（显示上下文、隐藏选择器）。

## 接收方式

- 分支/worktree：`task/CHAPTER-SELECTOR-1` / `G:/CODEX/New Manga.workspace/worktrees/CHAPTER-SELECTOR-1`；delivery head `126d05518`；base `10a0308c1`。
- 复现：见 `verification/CHAPTER-SELECTOR-1/REPORT.md §6`（含双书三章测试数据根构造脚本）。
- 真机前置：发布单文件 App + `app/core-sidecar`；测试数据根用脚本生成（**源 BOOK-FIXTURE 不被修改**）；写权限需 `--demo-write`。
- 需要 DSH 做：独立 Review（Owner 不自审）→ 运行 test.ps1 复核 → 合入/集成 → closeout（resource manifest 复核后决定 task-env 去留）。

## 下一任务建议（必填）

- Task ID / 标题：**无新增实现任务需要立即释放**；A 组第一批三张卡（NS-WIRE-A1 / READER-PROGRESS-1 / CHAPTER-SELECTOR-1）实现侧已全部交付，当前瓶颈在集成与独立 Review。
- 推荐 Agent / Reviewer：集成 = DSH；独立 Reviewer = 未参与实现的 Codex / ZCode / Antigravity（按 DSH 排班）。
- 推荐原因与前置依赖：三张卡均已有 delivery head 与 64-hex pin，需先由 DSH 运行 Gate、判定合入顺序（READER-PROGRESS-1 依赖链在 CHAPTER-SELECTOR-1 之前）并执行 closeout；是否从 REBASELINE_PLAN 释放下一批（S4 NS 第二批 / 阅读器后续）由 DSH 裁决，本卡不再派生。
- Recovery point：仓库 `G:/CODEX/New Manga`；三张卡 delivery head：读取器进度 `10a0308c1`、多章选择器 `126d05518`、NS-WIRE-A1 见其 Handoff。
- 允许修改路径：`apps/desktop-avalonia/**`、`doc/tasks/CHAPTER-SELECTOR-1.md`、STATUS/PLAN/LEDGER、`verification/CHAPTER-SELECTOR-1/**`、workspace task-env。
- 禁止范围：不改 Python Core/旧壳/协议与 Host 契约语义；不 push；不 gc/prune。
- 交付物：本卡实现 + 证据 + Handoff 已完成；DSH 集成验证结论与 closeout 记录。
- 验证命令与完成 Gate：`test.ps1` 145/145、vitest 60/567、pytest 3F/2739P/9S、`check.ps1 -TaskPath` PASS、14 条 pin、独立 Review 通过。
- 可直接转发给 Agent 的指令：

```text
作为独立 Reviewer（未参与实现），复核 CHAPTER-SELECTOR-1（delivery 126d05518，walkthrough 见 doc/handoffs/CHAPTER-SELECTOR-1-handoff.md 与 verification/CHAPTER-SELECTOR-1/REPORT.md）。
只读：不要修改代码。核对 AC1–AC5 与 14 条 pin（sha256 与文件一致），重跑 pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1（应 145/145）与 check.ps1 -TaskPath doc/tasks/CHAPTER-SELECTOR-1.md（应 PASS），抽查 HostRuntime 的 reader I/O 门与 MainWindow.OpenReaderForBookAsync 的 flush→投影→填充顺序，给出 PASS / 有条件 PASS / 返修 结论与具体证据行。
```

## 风险与遗留

1. ComboBox 弹层与书卡双击的真机注入未覆盖（弹层是独立 popup 窗口；双击手势注入不稳定）→ headless 已覆盖事件与选择逻辑，真机用同一路径的按钮入口。
2. 章节列表返回全量、无分页/搜索；百章以上书籍的列表渲染与 `list_chapters` 载荷未做性能测试。
3. 沉浸窗不提供切章（避免双窗状态分叉）。
4. `GetReaderProjectionAsync` 现在也占用 reader I/O 门：首屏投影与页图读串行排队，实测单章加载无可感知延迟；高延迟磁盘/大图场景需在性能卡中复核。
5. 需独立 Review（Owner 不得自审）。
