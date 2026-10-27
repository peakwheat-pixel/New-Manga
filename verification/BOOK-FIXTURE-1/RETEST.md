# BOOK-FIXTURE-1 复测说明（一页）

> 测试书已建好：**book_id `14340ddad0ed472fbe687fe12340c5d8`**、8 页（1200×1660）、章节类型
> `webtoon`（reader layout = `webtoon_vertical`）。隔离数据根：
> `G:\CODEX\New Manga.workspace\task-envs\BOOK-FIXTURE-1\isolated-data`（8.1 MB，含 library.db /
> managed（8 页 Managed Copy）/ catalog / derived / _env）。**真实 `%APPDATA%` 未被触碰**
>（脚本前后指纹一致，见 `book-fixture.json.real_appdata.untouched=true`）。

## 1. 启动（隔离数据根）

```powershell
# 一键（优先使用 FINAL-VALIDATION-1 发布件；也可 -AppExe 指定任意 Avalonia 构建）
pwsh -NoProfile -File apps/desktop-avalonia/scripts/start-book-fixture.ps1
# 等价手工（注意：AppOptions 只认 "--data-root=<路径>" 等号形式；空格裸传会被解析成 "true"，
# 路径含空格时整段必须带引号）：
#   NewManga.App.exe --data-root="<DataRoot>"
# 只校验不启动：加 -NoLaunch
```

启动后：书架应出现「BOOK-FIXTURE-1 日漫_JA 测试书」（8 页）。App 的 Host 会把
`NEWMANGA_DATA_ROOT=<DataRoot>` 传给 `core_service.exe`，所有写入都留在隔离根内。
已做 app-level smoke（`app-smoke.json`）：发布件以 `--data-root="<DataRoot>" --exit-after=8000` 启动，
`logs/host.log` 记录 `data_root=<DataRoot>`，`logs/wire/core-service.ndjson` 出现 2 次 `ListBooks`
且含该 book_id；窗口出现、exit 0、无残留、真实 `%APPDATA%` 未变。

## 2. webtoon 工作集（AC3 的「阅读 4000×60000 webtoon ≤1.5GB」）

- 进入「阅读器」页：当前壳层的阅读器页使用 S4/T3 fixture（`NEWMANGA_S4_FIXTURES`，默认
  `task-envs/UI-WORKBENCH-READER-1/fixtures`；`TileDirectory` = DISPLAY-PERF 4000×60000 长条 tiles），
  滚动/翻页即可复现「4000×60000 webtoon 阅读」路径。
- 测量：任务管理器 → 详细信息 → **`NewManga.App` 与 `core_service.exe` 工作集峰值之和**；
  通过标准 **≤1.5GB**（记录 MB 与是否溢出）。
- 说明：库中书（8 页 webtoon_vertical）目前在 Core 侧可读（`list_books`/`GetReaderProjection` 均 PASS），
  但**壳层尚未把库中书接到阅读器页**（见 §3 缺口），因此工作集测量仍走 fixture 阅读器页。

## 3. 沉浸 Esc/H —— 当前 **BLOCKED（产品缺口，已回报 Lead）**

- 现状证据（repo 全量 grep）：
  - `apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml.cs:66-72`：阅读器页绑定
    `ReaderFixtureLocator.TypographyPaths()` 固定 fixture，不读取 `ListBooks` 的库中书；
  - `Views/ReaderWorkbenchPages.cs:449-487`：`ReaderWindow`（无边框全屏；**Esc 退出 / H 隐藏 HUD /
    F 切 fit**）只有**定义与构造函数**，全仓**没有任何 `new ReaderWindow(...)` 调用** → 沉浸入口不存在，
    Esc/H/F 无法触达。
- 结论：不是「缺书」，是**产品未接线**；加书无法修复。已回报 DSH，建议另开
  `READER-LIBRARY-WIRE-1`（库中书 → ReaderPage + 沉浸入口）。
- 待该 Task 完成后，同一数据根/启动命令即可复测：Esc 退出沉浸、H 切换 HUD、F 切 fit。

## 4. 清理与重建

```powershell
# 清理（只删隔离根；不要删真实 %APPDATA%\com.newmanga.desktop）
Remove-Item -Recurse -Force 'G:\CODEX\New Manga.workspace\task-envs\BOOK-FIXTURE-1\isolated-data'
# 重建（幂等：已存在则 status=existing；-Force 软删旧书后重导）
pwsh -NoProfile -File apps/desktop-avalonia/scripts/new-test-book.ps1 -PageLimit 8
# 自定义数据根/页数/页源（页源必须只读引用 golden suite）
pwsh -NoProfile -File apps/desktop-avalonia/scripts/new-test-book.ps1 -DataRoot <新根> -PageLimit 16
```

脚本参数：`-DataRoot`（隔离根）、`-PageLimit`（默认 8）、`-BookTitle`/`-ChapterTitle`、
`-PagesRoot`（默认 `test_assets/comic_golden_suite/日漫_JA`；worktree 不含被 gitignore 的页时自动回退到
主检出同一路径，只读引用不复制）、`-Force`、`-SkipVerify`、`-EvidencePath`。

## 5. 本次已自动验证（证据 `verification/BOOK-FIXTURE-1/`）

| 项 | 结果 |
|---|---|
| 建书 | `status=created`，book `14340…`，8 页，`import_report.failed=[]` |
| `ListBooks`（冻结 core_service，协议 2.3） | 找到该书，`page_count=8` |
| `list_chapters` / `GetReaderProjection` | 1 章；8 页均 `width_px/height_px > 0`；layout `webtoon_vertical` |
| 幂等重跑 | 第二次 `status=existing`，同 book_id / 8 页，未新增书 |
| 真实 `%APPDATA%` | 前后指纹一致（`untouched=true`） |
| 回归 | `scripts/test.ps1` 102/102；pytest 3F/2739P/9S（相对基线 0 新增） |
