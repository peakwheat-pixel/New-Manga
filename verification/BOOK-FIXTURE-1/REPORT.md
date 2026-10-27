# BOOK-FIXTURE-1 报告：隔离数据根测试书（webtoon/Esc-H 复测前置）

- Task: `doc/tasks/BOOK-FIXTURE-1.md`（team task-20）；Branch/Worktree: `task/BOOK-FIXTURE-1` /
  `G:/CODEX/New Manga.workspace/worktrees/BOOK-FIXTURE-1`；Base: `c6934cba5`
- 未 push；未改产品源码/协议/Host 契约；未触碰真实用户数据。

## 0. 结论

| AC | 判定 | 证据 |
|---|---|---|
| AC1 一键建书（隔离 env、幂等、只读引用 golden suite） | **MET** | `apps/desktop-avalonia/scripts/new-test-book.ps1` + `new_test_book.py`；`book-fixture.json` |
| AC2 数据校验（list_books/页数/页面尺寸） | **MET** | 冻结 `core_service.exe` 协议 2.3 复核：`ListBooks` page_count=8、`list_chapters` 1 章、`GetReaderProjection` 8 页均 `1200×1660`（可解析）、layout `webtoon_vertical` |
| AC3 供复测（一页说明） | **PARTIAL** | `verification/BOOK-FIXTURE-1/RETEST.md`：数据根/启动/清理/webtoon 工作集步骤已给；**沉浸 Esc/H 因产品缺口不可达（已回报 Lead）**，非缺书可解 |
| AC4 回归 | **MET** | `scripts/test.ps1` **102/102**；pytest **3F/2739P/9S**（相对基线 0 新增）；真实 `%APPDATA%` 前后指纹一致 |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS；64-hex pin；Handoff |

**测试书事实**：book_id **`14340ddad0ed472fbe687fe12340c5d8`**，标题「BOOK-FIXTURE-1 日漫_JA 测试书」，
1 章（`webtoon`），**8 页**（每页 1200×1660，Managed Copy 8 个，源文件来自
`test_assets/comic_golden_suite/日漫_JA/**` 只读引用）。数据根
`G:/CODEX/New Manga.workspace/task-envs/BOOK-FIXTURE-1/isolated-data`（8.1 MB）。

## 1. AC1 一键建书

**脚本**（均在 `apps/desktop-avalonia/scripts/`，未改产品源码）：

| 文件 | 作用 |
|---|---|
| `new-test-book.ps1` | 一键：创建隔离 env → 调 helper 建书 → 用冻结 sidecar 协议复核 → 写证据 JSON；`-Force`/`-SkipVerify`/`-PageLimit`/`-PagesRoot`/`-EvidencePath` |
| `new_test_book.py` | 行为：`assemble_production_core` + 生产 `Importer.import_files`（真实导入路径，非伪造 DB），幂等逻辑 |
| `start-book-fixture.ps1` | 用 `--data-root <隔离根>` 启动 Avalonia App（自动解析 FINAL-VALIDATION-1 发布件；`-NoLaunch` 只校验） |

隔离方式（脚本内、只对子进程生效，退出即恢复）：`NEWMANGA_DATA_ROOT`、`APPDATA`、`LOCALAPPDATA`、
`TEMP`/`TMP` 全部指向 `<DataRoot>/_env/*`；`M2RC1_DERIVED_ROOT`/`M2RC2_CATALOG_DB`/`M2RC1_MANAGED_ROOT`
落在隔离根内。真实 `%APPDATA%\com.newmanga.desktop` 在运行前后做存在性+文件数+LastWriteUtc 指纹比对，
证据里 `real_appdata.untouched=true`（脚本末尾再断言，变化即 throw）。

页源：`test_assets/comic_golden_suite/日漫_JA/**`（`*.jpg/jpeg/png`，排序后取 `-PageLimit` 个）。注意该目录
`.gitignore = /*`（页体不入 Git），linked worktree 检出不含页体 → 脚本按「worktree 路径 > 主检出路径」自动回退，
只读引用、不复制进仓库。

**幂等实测**：第一次 `status=created`（8 页）；第二次 `status=existing`，**同 book_id、同 8 页、未新增书**
（`book-fixture.json` vs `book-fixture-rerun.json`）。`-Force` 会先软删旧书再重导。

## 2. AC2 数据校验（用真实 Host 协议面）

验证不靠内部脚本自证，而是启动**冻结 `core_service.exe`**（`task-envs/FINAL-VALIDATION-1/sidecar-copy`，
SHA-256 入证据）以 `NEWMANGA_DATA_ROOT=<隔离根>` 服务，按协议 2.3 发命令：

| 命令 | 结果 |
|---|---|
| `core.ping` | `status=ready` |
| `ListBooks` | 找到该 book_id；`page_count = 8` |
| `list_chapters` | 1 条（`第 1 章`） |
| `GetReaderProjection` (`mode=original`, `start_position=beginning`) | 8 页；`width_px=1200, height_px=1660` 全部 >0；`layout=webtoon_vertical` |

`page_dimensions_parseable=true`；Core stderr 仅出现预期的模型缺失 WARNING（base 件不含模型，检测/运行需模型包，
不影响阅读/复测）。

## 3. AC3 供复测 + **产品缺口（必要缺陷，已回报）**

一页说明：`verification/BOOK-FIXTURE-1/RETEST.md`（启动/参数/数据根/webtoon 工作集/清理/重建）。

**缺口（阻断 Esc/H 复测，不是缺书）**：
- `apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml.cs:66-72`：「阅读器」页绑定
  `ReaderFixtureLocator.TypographyPaths()` 固定 fixture，**没有**从 `ListBooks` 读取库中书；
- `apps/desktop-avalonia/src/NewManga.App/Views/ReaderWorkbenchPages.cs:449-487`：`ReaderWindow`
  （无边框全屏；Esc 退出 / H 隐 HUD / F 切 fit）**全仓只有定义与构造函数，没有任何 `new ReaderWindow(...)`
  调用**（repo 全量 grep 2 处命中）→ 沉浸入口不存在，Esc/H/F 不可达。

因此 AC3 记 **PARTIAL**：数据根/书/说明/校验已交付，webtoon 工作集可按说明用现有 fixture 阅读器页测，
**沉浸 Esc/H 需先补产品接线**。建议另开 `READER-LIBRARY-WIRE-1`（库中书 → ReaderPage 分页 + 沉浸入口），
完成后同一数据根与启动命令即可复测。已向 Lead 回报并请求裁决。

**app-level smoke（发布件，`app-smoke.json`）**：`NewManga.App.exe --data-root="<隔离根>" --exit-after=8000`
→ 主窗口出现（handle 3477932）→ exit 0 → 无残留进程 → 真实 `%APPDATA%` 文件数 17→17 未变；
`<隔离根>/logs/host.log` 记录 `data_root=G:\...\BOOK-FIXTURE-1\isolated-data`（Host 确实用了隔离根），
`logs/wire/core-service.ndjson` 出现 **2 次 `ListBooks`** 且含该 **book_id**（壳层已从 Core 列出本书）。
注意 `AppOptions` 只认 `--data-root=<路径>` 等号形式（裸传 `--data-root <路径>` 会被解析成字面量 `"true"`；
路径含空格时整段要带引号）——launcher 已按此实现。

## 4. AC4 回归

| 门 | 结果 |
|---|---|
| `apps/desktop-avalonia/scripts/test.ps1`（新 sidecar 副本） | **TEST PASS (Debug): 102/102 passed, 0 skipped** |
| `python -m pytest -q` | **3 failed, 2739 passed, 9 skipped**（失败集合=基线 3 项，0 新增） |
| 真实 `%APPDATA%` | 未污染（前后指纹一致，`untouched=true`） |
| 产品源码/协议/契约 | 零改动（`git status` 仅本 Task 脚本+证据+文档） |

## 5. 遗留 / NOT_RUN

1. **沉浸 Esc/H（AC3）BLOCKED/PARTIAL**：产品缺口（见 §3），建议 `READER-LIBRARY-WIRE-1`。
2. 库中书在壳层可见（ListBooks）、但**点开阅读**尚不可用（同上缺口）。
3. base 发布件不含模型：对本书做「运行/检测」需 models 包或放置模型；阅读/复测不需要。
4. 工作集测量的人工步骤（任务管理器读数）仍需用户在真机执行（脚本不代填数字）。
5. 数据根为书 fixture，不随仓库提交（task-env PRESERVE_REFERENCED）。

## 6. 证据索引

`verification/BOOK-FIXTURE-1/{book-fixture.json, book-fixture-rerun.json, new-test-book.helper.log,
new-test-book.creation.json, RETEST.md, pytest.log, scripts-test.log}`；
脚本：`apps/desktop-avalonia/scripts/{new-test-book.ps1,new_test_book.py,start-book-fixture.ps1}`。
