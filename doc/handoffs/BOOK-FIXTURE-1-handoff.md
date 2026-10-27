# BOOK-FIXTURE-1 Handoff（隔离数据根测试书）

- Task: `doc/tasks/BOOK-FIXTURE-1.md`（team task-20）
- Branch: `task/BOOK-FIXTURE-1`；Worktree: `G:/CODEX/New Manga.workspace/worktrees/BOOK-FIXTURE-1`
- Base: `c6934cba5`（卡面 `4deb9ef3e` 为释放前；实际分支含 followups 释放提交）
- Delivery head: `f0142fccd`（实现+证据提交；任务卡 Canonical Evidence 的 pin 均指向它）
- 未 push；未改产品源码/协议/Host 契约；未触碰真实用户数据。

## 1. 交付摘要

| AC | 结论 | 证据 |
|---|---|---|
| AC1 一键建书 | **MET** | `apps/desktop-avalonia/scripts/new-test-book.ps1` + `new_test_book.py`；真实导入路径；幂等（第二次 `status=existing`，同 book_id/8 页） |
| AC2 数据校验 | **MET** | 冻结 `core_service.exe` 协议 2.3：`ListBooks` page_count=8、`list_chapters` 1 章、`GetReaderProjection` 8 页均 1200×1660（可解析）、layout `webtoon_vertical` |
| AC3 供复测 | **PARTIAL** | `verification/BOOK-FIXTURE-1/RETEST.md` 已给数据根/启动/webtoon 工作集/清理；**沉浸 Esc/H 因产品缺口不可达（已回报 Lead）** |
| AC4 回归 | **MET** | `scripts/test.ps1` **102/102**；pytest **3F/2739P/9S**（0 新增）；真实 `%APPDATA%` 未污染 |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS；64-hex pin；本 Handoff |

**测试书**：book_id `14340ddad0ed472fbe687fe12340c5d8`（「BOOK-FIXTURE-1 日漫_JA 测试书」），1 章
（webtoon），**8 页**（1200×1660；Managed Copy 8 个；源 = `test_assets/comic_golden_suite/日漫_JA/**`
只读引用）。数据根 `G:/CODEX/New Manga.workspace/task-envs/BOOK-FIXTURE-1/isolated-data`（8.1 MB）。

## 2. 新增文件（全部在允许范围）

| 文件 | 作用 |
|---|---|
| `apps/desktop-avalonia/scripts/new-test-book.ps1` | 一键：隔离 env（NEWMANGA_DATA_ROOT/APPDATA/LOCALAPPDATA/TEMP…）→ 建书 → 冻结 sidecar 协议复核 → 证据 JSON；支持 `-DataRoot/-PageLimit/-BookTitle/-ChapterTitle/-PagesRoot/-Force/-SkipVerify/-EvidencePath` |
| `apps/desktop-avalonia/scripts/new_test_book.py` | helper：`assemble_production_core` + 生产 `Importer.import_files`；按标题幂等；`--force` 软删重导 |
| `apps/desktop-avalonia/scripts/start-book-fixture.ps1` | 用 `--data-root <隔离根>` 启动 Avalonia App（自动解析 FINAL-VALIDATION-1 发布件；`-NoLaunch` 只校验并打印要点） |
| `verification/BOOK-FIXTURE-1/RETEST.md` | AC3 一页复测说明（含缺口说明与清理方法） |
| `verification/BOOK-FIXTURE-1/REPORT.md` | 完整报告 |

## 3. 用法（可直接转发给用户/复测人）

```powershell
# 建书（幂等；-Force 重建）——默认数据根在 task-env（不在仓库）
pwsh -NoProfile -File apps/desktop-avalonia/scripts/new-test-book.ps1 -PageLimit 8
# 仅校验 + 打印复测要点（不启动 GUI）
pwsh -NoProfile -File apps/desktop-avalonia/scripts/start-book-fixture.ps1 -NoLaunch
# 启动 App（读隔离数据根；Host 将 NEWMANGA_DATA_ROOT 传给 Core sidecar）
pwsh -NoProfile -File apps/desktop-avalonia/scripts/start-book-fixture.ps1
# 清理（只删隔离根）
Remove-Item -Recurse -Force 'G:\CODEX\New Manga.workspace\task-envs\BOOK-FIXTURE-1\isolated-data'
```

app-level smoke（已做，自关闭）：从 FINAL-VALIDATION-1 发布件以
`--data-root="<隔离根>" --exit-after=8000` 启动 → 主窗口出现（handle 3477932）→ exit 0 → 无残留进程；
`<隔离根>/logs/host.log` 记录 `data_root=<隔离根>`，`logs/wire/core-service.ndjson` 出现 2 次 `ListBooks`
且含 book_id（壳层实际列到本书）；真实 `%APPDATA%` 文件数前后一致（17→17）。
注意：`AppOptions` 只认 `--data-root=<路径>` 等号形式，裸传 `--data-root <路径>` 会被解析成字面量 `"true"`；
路径含空格需整段带引号——`start-book-fixture.ps1` 已按此实现。

## 4. 产品缺口（已回报 Lead，请求裁决）

**Avalonia 壳层未把库中书接到阅读器，且沉浸窗无入口**：

1. `apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml.cs:66-72`：阅读器页绑定
   `ReaderFixtureLocator.TypographyPaths()`（S4 fixture），不读取 `ListBooks` 的库中书；
2. `apps/desktop-avalonia/src/NewManga.App/Views/ReaderWorkbenchPages.cs:449-487`：`ReaderWindow`
   （无边框全屏；Esc 退出 / H 隐 HUD / F 切 fit）**全仓只有定义+构造函数，无任何 `new ReaderWindow(...)`
   调用**（repo 全量 grep 2 处命中）→ Esc/H/F 不可达。

→ 所以「加书」无法让 Esc/H 可测；建议另开 **`READER-LIBRARY-WIRE-1`**：库中书/chapter/pages → `ReaderPage`
（分页 + 当前页/滚动进度）+ 增加沉浸入口（按钮/双击/快捷键）→ 之后同一数据根与启动命令即可复测 Esc/H。
BOOK-FIXTURE-1 因此 AC3 记 **PARTIAL**（说明与数据已交付，复测动作中 Esc/H 部分待产品接线）。

## 5. 回归与不污染

- pytest `3 failed, 2739 passed, 9 skipped`（与基线 3F/2739P/9S 相同失败集合，0 新增）。
- `apps/desktop-avalonia/scripts/test.ps1 -SidecarDirectory <新 sidecar 副本>`：`TEST PASS (Debug): 102/102 passed, 0 skipped`。
- 真实 `%APPDATA%\com.newmanga.desktop`：脚本前后指纹（存在性/文件数/LastWriteUtc）一致并断言；
  建书跑 2 次 + app smoke 1 次后仍一致（`book-fixture.json`、`book-fixture-rerun.json`、`app-smoke.json`）。
- 因 golden suite 页体被 `.gitignore`（`test_assets/**/.gitignore=/*`），linked worktree 不含页；脚本按
  「worktree 路径 > 主检出路径」只读回退，无复制入仓。

## 6. 遗留 / NOT_RUN

1. **沉浸 Esc/H（AC3 部分）**：BLOCKED by 产品缺口（§4），建议 `READER-LIBRARY-WIRE-1`。
2. 壳层「阅读库中书」同样待 §4 接线；Core 侧已证明书/页/读者投影可用。
3. 工作集人工读数（任务管理器，≤1.5GB）仍需用户在真机执行；说明见 RETEST.md（当前走 fixture 阅读器页）。
4. base 发布件不含模型：对本书跑检测/运行需 models 包或放置模型（阅读复测不需要）。
5. 数据根 fixture 在 task-env（PRESERVE_REFERENCED），不提交仓库；关闭时按 workspace 裁决保留/清理。
6. 需独立 Review（Owner 不得自审）。
