---
task: MAINT-2-C1-BATCH-1
reviewer: independent sub-agent (r1, read-only, not involved in implementation)
verdict: approved
date: 2026-11-14
reviewed_head: b122fb926
p0: 0
p1: 0
p2: 5
p3: 2
---

# MAINT-2-C1-BATCH-1 独立复核 r1

## 0. 结论

**`approved`。P0 = 0，P1 = 0，P2 = 5，P3 = 2。**

本报告由未参与实现的独立上下文子 agent（父会话 `session-90dc2552-798c-4921-abff-823ae8e6ca5e` 派生）在**只读**约束下完成：`reviewed_head = b122fb926c106b2292c64c656ed2ba8002b4f2c7`，被审区间 `4d90336e7..b122fb926`（12 文件 / +778 / −18；实际 5 个 commit，`4d90336e7` 为区间基线裁决 commit）。复核期间未 commit / push / checkout，未直接修改任何既有文件（测试副作用出现与还原见 §6）；本文件是唯一新增文件。

**硬结论**：

1. **M2-C1 rev 2.16 是真 additive**：numstat 精确 `+3 / −1`，2 个 hunk（新增 rev 2.16 头段 + §5 `ListChapters` 行原位替换）；既有四键名字/类型/语义不变，`sort_order` 仍是唯一排序键；`PROTOCOL_MAJOR=2` / `PROTOCOL_MINOR=3` / `ChapterPagesMinor=6`（per-command minor 6）零变更。缺陷只有**修订登记不完整**：文档状态行仍写 rev `2.15`，`## Revision history` 无 `2.16` 条目（P2-1，两行可补，不影响 wire 语义）。
2. **AC4/AC5 判别测试能变红**：Python wire 用例对 `kind`/`custom_rank` 做**值相等**断言（不是"不抛异常"），投影回退会 `KeyError`，`custom_rank` 截断 int32 会让 `2**40` 断言失败；C# `Parse` 用例对 `long?` 与显式 null 做值断言，`long` 降为 `int` 即失败。空跑：定向 11 passed、`CoreClient.Tests` 180 passed。
3. **`ChapterSummary.Parse` 收紧不违反"不改既有四字段语义"**（PASS），但它是 AC4/AC5 范围外的行为变化，且 `FormatException` 未被 `HostController.ListChaptersAsync` 的错误过滤捕获（P2-3）。
4. **AC1 三处控件真的接到 Host**（经 `ReaderViewModel` → `IHostController` → `HostController`，测试断言 Fake Host 的副作用），但布局/定位有 P2：整书进度复用 `fluent-reader-title` 造成 `FirstOrDefault` 定位依赖插入顺序；书签面板无最大高度/滚动容器且位于 2 秒自动隐藏条内。
5. **全量测试与四门禁由复核者独立复跑，全部通过**：pytest `3544 passed, 10 skipped` / EXIT=0；`NewManga.App.Tests` 914 passed / 11 skipped / 0 failed；`CoreClient.Tests` 180 passed；`Host.Tests` 321 passed；`check.ps1`（默认 + TaskPath）PASS；`verify_pins` 18/18；`generate_api_inventory --check` OK。
6. **AC8 如实登记为 PARTIAL**：README 明写"复跑留证 = PARTIAL / 不得写成复跑通过"，两套基线数字与原始输出均保留；复核者复跑 PIN-BASIS suite 精确复现 `12 failed, 56 passed, 60 subtests passed`（EXIT=1）。AC8 未被写成 MET。

**DoD §3 回答见 §5。**

## 1. 复核方法与边界

- 起点：`git rev-parse HEAD` = `b122fb926c106b2292c64c656ed2ba8002b4f2c7`；首次 `git status --porcelain` 在 11:42:47 曾显示 ` M doc/tasks/MAINT-2-C1-BATCH-1.md`，下一次调用即恢复为空（未进入任何 commit；12 文件 diff 不含 task 卡）。此后至复核结束，除**测试副作用**（§6）外工作树为空。
- 只读检查：`git diff --numstat` / `--name-only` / `-G`、源码与测试逐行阅读、`git show` 基线代码对比。
- 独立复跑：全量 pytest、三套 dotnet test（App / CoreClient / Host）、PIN-BASIS governance suite、`check.ps1` ×2、`verify_pins.ps1`、`generate_api_inventory.py --check`。
- 未做：未 checkout / 未改动被审对象；载体 `CONTRACT-UNFREEZE-2026-11-14-M2C1.md` §7 仍为 `pending`（本复核只能新增本文件，不能追写该载体；请 DSH 在处置时补记或引用本报告）。

## 2. 逐项裁决（对应任务 1–9）

| # | 复核项 | 裁决 | 关键证据 |
|---|---|---|---|
| 1 | 契约修订真 additive | **PASS**（附 P2-1） | numstat `3 1`；四键逐字保留；协议常量零变更 |
| 2 | AC4/AC5 判别测试能变红 | **PASS** | 值相等断言 + `2**40` + 精确键集；定向 11 passed、CoreClient 180 passed |
| 3 | `ChapterSummary.Parse` 收紧 | **PASS**（约束未违反；附 P2-3） | 四键本就是契约必填；`RegionTextDetail.Parse` 先例严格 |
| 4 | `kind` 契约文字 | **P2** | rev 2.16 只写来源/取值域，未写"每个存活章节必须返回"；载体 §3 有该约束 |
| 5 | AC1 控件实现 | **PASS**（附 P2-4） | 三处均经 VM→IHostController→HostController；布局/定位 P2 |
| 6 | AC8 口径 | **PASS**（附 P2-5） | README PARTIAL、双基线、未写 MET；复跑 12F/56P 复现 |
| 7 | 全量测试 | **PASS** | pytest 3544/10/EXIT=0；App.Tests 914/11/0/EXIT=0 |
| 8 | 四件套 | **PASS** | 4 条命令全 EXIT=0，与 gates 日志一致 |
| 9 | 越界 | **PASS** | 12 文件全在 `allowed_paths`；无 pin / STATUS / PLAN / LEDGER 改动 |

### 2.1 契约修订是否真 additive（PASS）

- `git diff --numstat 4d90336e7 b122fb926 -- doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` = **`3	1`**，与实现者声称一致；全区间合计 `12 files, +778/−18`，契约只占这 2 个 hunk：
  - `:18` 新增 rev 2.16 头部说明（引用块 + 空行 = 2 增）；
  - `:203` §5 表 `ListChapters` 行原位替换（旧 4 键行 → 同 4 键 + `kind?`/`custom_rank?` = 1 删 1 增）。
- 既有四键 `chapter_id` / `title` / `chapter_number` / `sort_order` 在类型行里**逐字保留**，仍是必填（无 `?`）；新增两键带 `?`，且头部/行注记均写"可选"。
- 排序语义未动：Core 投影仍来自 `list_chapters` 的 `ORDER BY sort_order`（`src/infrastructure/sqlite/library.py:241-247`），`custom_rank` 不进排序；未知 `book_id` 仍为空数组（`tests/core/test_library_wire.py:260-262` 断言）。
- 协议 zero-change：`src/bootstrap/core_service.py:296` `PROTOCOL_MAJOR=2`、`:324` `PROTOCOL_MINOR=3`；`apps/.../Wire/CoreProtocol.cs:11-12` `Major=2` / `DefaultMinor=3`；`CoreServiceClient.cs:408` `ChapterPagesMinor=6`。`git diff -G "minor|Minor|PROTOCOL"` 只命中契约与载体文本（载体为新增文件），无代码常量改动。
- M2-C1 不在 `verify_pins.ps1` 的 18 份 pin 表（脚本内无 M2-C1 条目），故本修订没有 pin 需重算；`verify_pins` 仍 18/18（载体 §5 的说明属实）。

**P2-1（不否定 additivity）**：`M2-C1_TYPED_IPC_CONTRACT.md:30` 仍写"状态：文档 rev `2.15`"，`## Revision history`（`:32-34`）从 `2.15` 起，**没有 `2.16` 条目**。该契约此前的 2.12–2.15 均在 `## Revision history` 有条目，且状态行指向最新 rev；本次头部升到 2.16 但状态行/历史列表未同步，导致契约自我声明的当前 rev 与头部不一致。修法：状态行改 `rev 2.16` 并在 `## Revision history` 顶部加一条 2.16 摘要（两行级）。

### 2.2 AC4/AC5 判别测试是否真能变红（PASS）

- `tests/core/test_library_wire.py:215` `test_list_chapters_exposes_optional_kind_and_custom_rank`：经 `UpdateChapterMetadata` 写入 `kind="webtoon"`、`custom_rank=7` / `2**40`，再经 wire `list_chapters` 读回；断言 `kind == "webtoon"` / `"paged"`、`custom_rank == 7` / `2**40`、未设置者为**显式 null**、四键为其子集、顺序仍 `[first, second]`、未知 book 空数组。
  - 若 Core 投影回退四键：`by_id[...]["kind"]` 触发 `KeyError` → **FAIL**（不是"不抛异常"）。
  - 若 `custom_rank` 被 int32 截断：`2**40` 断言直接失败。
- `tests/core/test_page_nav_projection.py:95-108`：既有形状断言从"精确 4 键"改为"精确 6 键"（`assert rows[0] == {...}` 与 `assert set(rows[1].keys()) == {...}`），仍是精确相等，不是放宽。
- `apps/.../ChapterSummaryParseTests.cs:33-59`：`Parse_WidenedRow_ReadsKindAndCustomRank` 断言 `"webtoon"`/`7L`；`Parse_ExplicitNullRank_And_Int64RankBothWork` 断言 `1099511627776L > int.MaxValue`。若 DTO/解析改成 `int`（`TryGetInt32` 或强转），该用例返回 null 或抛异常 → **FAIL**。`:19-31` 的"旧四键行"用例则刻意保持合法（向后兼容），Core 侧回退由 Python 用例判别——两层各司其职，覆盖正确。
- 独立空跑：`pytest tests/core/test_library_wire.py tests/core/test_page_nav_projection.py -q` → **11 passed in 4.34s / EXIT=0**；`dotnet test NewManga.CoreClient.Tests` → **180 passed / 24 skipped / 0 failed / EXIT=0**（含 4 条新 Parse 用例）。

### 2.3 `ChapterSummary.Parse` 行为收紧（PASS，附 P2-3）

- 基线（`4d90336e7`）行为：`ReadString(...) ?? string.Empty`、`ReadInt(...)` 缺省 0（`CoreServiceClient.cs:2698-2714`），即缺键/错型被静默降级。新行为：四键缺失/错型抛 `FormatException`（`CoreServiceClient.cs:53-86`，含 `RequiredString`）。
- **是否违反"不改既有四字段与键集语义"：不违反。** 冻结契约（rev 1.8）本就规定这四键必填（`M2-C1:203` 旧行与 §5.10.4），缺键的行**已经是违约行**；本次只改"违约行的客户端处理"，没有改任何字段的名字、类型、语义或键集定义。仓库先例 `RegionTextDetail.Parse`（`Commands/RegionTextProjection.cs:63-64`）对所有字段严格抛 `FormatException`，严格解析符合本仓 DTO 惯例。
- 但仍登记 **P2-3**：① 它超出 AC4/AC5"只加可选字段"的范围，属主动加固，需在证据里明示；② `FormatException` 不是 `SidecarException`，`HostController.ListChaptersAsync` 的过滤（`HostController.cs:946-950`：`CoreOperationException/SidecarException/BridgeException/OperationCanceledException/IOException`）不捕获它，而 `Malformed(...)` 返回的恰是 `SidecarException`（`CoreServiceClient.cs:2622`）。也就是说，一个违约行现在会把 `FormatException` 抛到调用方，绕过既有"降级为空列表"路径。建议在 `ListChaptersAsync` 内 `catch (FormatException) → throw Malformed(...)`（或让 `Parse` 直接抛 `Malformed`），同时把 `Parse_MissingFrozenKey_Throws` 的期望同步为 `SidecarException`；若坚持 fail-fast，也应在契约/证据里写清。
- 该收紧已被测试固定（`ChapterSummaryParseTests.cs:61-70`），不是无意副作用。

### 2.4 `kind` 契约文字（P2）

- rev 2.16 头部（`M2-C1:18`）与行注记（`:203`）只写：来源 `chapters.chapter_type`、取值域 `"paged"`/`"webtoon"`、字段可选。**没有**写"任何存活章节都必须返回 `kind`"。
- 该约束只存在于载体 `CONTRACT-UNFREEZE-2026-11-14-M2C1.md:35`（"实现**必须总是返回** `kind`（既有列，非空）"）。实现确实恒返回（`core_service.py:4608` `chapter.chapter_type.value`；`chapters.chapter_type NOT NULL DEFAULT 'paged'`，`schema.py:203-204`），但契约本身若被单独阅读，允许实现省略 `kind` 而不违约，AC4 的"字段存在"就缺契约锚点。
- **一行级补充建议**（加在 `M2-C1:18` rev 2.16 段末，或 `:203` 行注记末）："`kind` 对每个存活章节恒存在（`chapters.chapter_type NOT NULL`，缺省 `paged`）；`kind?` 仅表示旧读取端可忽略/旧 Core 可省略，不表示新 Core 可自由省略。"

### 2.5 AC1 控件实现（PASS，附 P2-4）

- **接线到 Host，而非仅 UI 状态**：视图调用 `_viewModel.ListBookmarksAsync/CreateBookmarkAsync/DeleteBookmarkAsync`（`ReaderPageView.cs:326-356`）→ `ReaderViewModel`（`:200-235`）→ `IHostController`（`IHostController.cs:194-206`）→ `HostController`（`:459-547`）→ Host runtime。判别测试断言的是 **Host 侧副作用**：`host.Bookmarks.Count` 1→2→1、新书签 `PageId=="p1"`、`host.LastResetConfirmed` 在确认前 false、确认后 true（`ReaderVisibleControlsTests.cs:58-124`）；整书进度只显示 VM 从 Host 投影得到的 `BookProgress`（`ReaderViewModel.cs:111-118`，视图 `:532-533`），无投影时 `IsVisible=false`、文本为空。
- **底栏插入是否挤压既有布局**：`_resetConfirmRow`、`_bookmarkPanelHost` 追加在底栏垂直 StackPanel（`ReaderPageView.cs:422-425`），默认 `IsVisible=false`，Avalonia 下隐藏子项不占布局 → 默认态**不挤压**。但一旦打开：书签列表是无 `MaxHeight`/`ScrollViewer` 的 StackPanel（`:286-302`），书签多时底栏（根 Grid `Auto` 行）无限增高、挤压 `*` 阅读区；且底栏 2 秒无交互即淡出并 `IsVisible=false`（`:28`；`FluentVisibilityMotion.cs:56`），面板/确认行会在用户阅读确认文案时消失（移动鼠标可唤醒）。顶栏新增第 7 个子项后仍是无滚动/无省略的水平 StackPanel，`FluentUi.Text` 默认 `TextWrapping.Wrap` 在水平栈里按无限宽测量，长进度文案可能横向溢出挤掉按钮。
- **`fluent-reader-title` 复用造成脆弱定位**：`_bookProgressText` 复用了 `fluent-reader-title` 类（`:146`），该类在仓库中没有样式定义，仅被 `Render()` 当定位键用：`_topBar.Children.OfType<TextBlock>().FirstOrDefault(block => block.Classes.Contains("fluent-reader-title"))`（`:529`）。目前正确只是因为标题先于进度加入（`:271` 在 `:273` 之前）；任何插入顺序调整都会让标题写成进度、进度写成标题。建议用独立 `_titleText` 字段或给进度用独立类（如 `fluent-reader-book-progress`）。
- 以上均不影响 AC1 的功能验收（控件存在、绑定既有命令、测试通过），记 **P2-4**（布局/可维护性），建议后续 UI 收口或本卡尾修。

### 2.6 AC8 口径（PASS）

- `verification/MAINT-2-C1-BATCH-1/README.md:5` 明写"AC8 复跑留证 = `PARTIAL`"；`:18` 表格 AC8 为 **PARTIAL**；`:42` 小节标题"AC8 基线漂移（必须如实登记，不得写成"复跑通过"）"；`:44` 历史基线 `3 failed / 61 passed / 2 skipped / 62 subtests`（validation clone `4ed7f32`）与 `:45` 本次 `12 failed / 56 passed / 60 subtests` 两套数字**都保留**；task 卡 `:57` 为 `<<PARTIAL: …不得写 MET>>`。**AC8 未被写成 MET。**
- 复核者独立复跑 `python -m pytest tools/governance/tests -q` → **`12 failed, 56 passed, 60 subtests passed in 122.36s`，EXIT=1**，与 README 的主工作树数字一致；历史原始输出 `verification/FEA-15-PIN-BASIS-ENFORCE-1/ac2ac3-full-pytest-4ed7f32.log` 仍存在且为 `3 failed, 61 passed, 2 skipped, 62 subtests passed in 114.79s`。两套基线可复核。
- **P2-5**：`README.md:49` 仍写"本批 4 个 commit 只改 `src/application/library/service.py`、`src/infrastructure/sqlite/prompt_templates.py` 与 4 个测试文件"——这是 AC8 复跑时（`ac69bb955` 前后）的旧描述，已不适用于最终 5 commit / 12 文件（含契约、载体、`ReaderPageView`、`CoreClient`）。它不改变 AC8=PARTIAL 的结论，但作为 AC8 的因果论证证据，应改写为"AC8 复跑发生的 4 个 commit 只改 …；其后 AC4/AC5/AC1 的 commit 未改 `core`/`application` 中影响该 suite 的字节"或类似限定。

### 2.7 全量测试（PASS，复核者独立复跑）

| 命令 | 实测（本次复核） | README 声称 | 对比 |
|---|---|---|---|
| `C:\Python314\python.exe -m pytest -q` | **`3544 passed, 10 skipped, 11 warnings in 279.21s` / EXIT=0** | `3544 passed, 10 skipped, 11 warnings in 272.33s` / EXIT=0 | 计数一致（耗时差异正常） |
| `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests` | **914 passed / 11 skipped / 0 failed / 925 total / 5m03s / EXIT=0** | 914 / 0 / 11 / EXIT=0 | 一致 |
| `dotnet test apps/desktop-avalonia/tests/NewManga.CoreClient.Tests` | **180 passed / 24 skipped / 0 failed / 204 total / EXIT=0** | 180 / 0 / 24 / EXIT=0 | 一致（含 4 条新增） |
| `dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests` | **321 passed / 74 skipped / 0 failed / 395 total / EXIT=0** | 321 / 0 / 74 / EXIT=0 | 一致 |
| 定向 `pytest tests/core/test_library_wire.py tests/core/test_page_nav_projection.py -q` | **11 passed in 4.34s / EXIT=0** | —（补充） | AC4/AC5 定向绿 |

- 仓库内证据 `logs/pytest-full-after-ac45.log:104` 确为 `3544 passed, 10 skipped, 11 warnings in 272.33s`；`logs/pytest-full.log` 为 `3543 passed …`（前一次基线），两文件哈希不同、内容不同，非复制。
- 未观察到新增 failed / error；pytest 末尾的 QML `TypeError` 是既有 Qt 警告，EXIT=0。

### 2.8 四件套（PASS）

| 命令 | 实测 | EXIT |
|---|---|---|
| `pwsh -NoProfile -File tools/governance/check.ps1` | `Governance check: PASS (3 warnings)` | 0 |
| `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/MAINT-2-C1-BATCH-1.md` | `Governance check: PASS (3 warnings)` | 0 |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`（C01b…FEA01 全 OK） | 0 |
| `C:\Python314\python.exe tools/generate_api_inventory.py --check` | `OK: rendered counts match FEA-C07 doc` | 0 |

- 与 `verification/MAINT-2-C1-BATCH-1/logs/gates-2026-11-14-final.log` 一致；该日志记录 HEAD=`153c6af7c`（最终 commit `b122fb926` 之前，只加证据文件），复核者在 `b122fb926` 上复跑结果不变。

### 2.9 越界（PASS）

- `git diff --name-only 4d90336e7 b122fb926` 共 **12 个文件**，全部落在 task 卡 `allowed_paths`（`doc/contracts/M2-C1…`、`doc/reviews/CONTRACT-UNFREEZE-2026-11-14-M2C1.md`、`src/bootstrap/**`、`tests/**`、`apps/.../NewManga.CoreClient/**`、`apps/.../NewManga.App/**`、`apps/.../tests/**`、`verification/MAINT-2-C1-BATCH-1/**`）。无 `src/application/library/service.py`、`src/infrastructure/sqlite/**` 改动——两者已含 `custom_rank`/`chapter_type`（`sqlite/library.py:104/107`、`schema.py:203-204/932`），本卡无需 schema/DDL，合理。
- `git diff --name-only … -- doc/STATUS.md doc/REBASELINE_PLAN.md doc/TASK_LEDGER.md doc/plan doc/pins` 为**空**；18 份 pin 全 PASS；无 `.gitattributes`/依赖/Release Gate 改动。
- task 卡本身不在 diff 内（`doc/tasks/MAINT-2-C1-BATCH-1.md` 未改）；实现方只在 `4d90336e7`（区间基线）与既有提交中登记 AC 状态。

## 3. P0 / P1 / P2 / P3 清单

| ID | 级别 | 位置 | 问题 | 建议 | 阻断？ |
|---|---|---|---|---|---|
| P2-1 | P2 | `M2-C1:30`、`:32-34` | 状态行仍 `rev 2.15`；`Revision history` 缺 `2.16` 条目 | 状态行改 2.16；history 顶部补一条 2.16 摘要（两行） | 否（语义不变，但建议收口前修） |
| P2-2 | P2 | `M2-C1:18`、`:203` | 契约未写"每个存活章节恒有 `kind`"，该约束只在载体 §3 | 按 §2.4 一行补充 | 否 |
| P2-3 | P2 | `CoreServiceClient.cs:53-86`、`HostController.cs:946-950` | `Parse` 收紧为抛 `FormatException`，且该异常不被 `ListChaptersAsync` 降级路径捕获 | `catch (FormatException) → Malformed(...)`；或明示 fail-fast 并同步测试期望 | 否（仅违约 Core 触发） |
| P2-4 | P2 | `ReaderPageView.cs:146/271/273/286-302/423-424/529`、`:28` | 进度文本复用 title 类导致定位依赖顺序；书签面板无高度上限/滚动；底栏 2 秒自动隐藏会带走面板/确认行；顶栏长文案可能溢出 | 独立 `_titleText`/进度类；面板加 `MaxHeight`+`ScrollViewer`；面板/确认行打开时暂停自动隐藏或提升为浮层 | 否 |
| P2-5 | P2 | `verification/…/README.md:49` | "本批 4 个 commit 只改 … 4 个测试文件"已过时（现 5 commit / 12 文件） | 限定为 AC8 复跑时的 commit 集，或改写为不依赖 commit 数的因果表述 | 否（不改 AC8 结论） |
| P3-1 | P3 | commit `3bc2a2561` | `test_page_nav_projection.py` 的形状断言更新被放进 AC1 commit，而非 AC4/AC5 测试 commit `153c6af7c` | 无需返工；记录 commit 归属 | 否 |
| P3-2 | P3 | 载体 `CONTRACT-UNFREEZE-2026-11-14-M2C1.md:18` | 写"**无删除行**、无既有条款改写"，但 numstat 为 +3/−1（1 行原位替换） | 改为"1 行原位改写（仅追加可选键）" | 否 |

- **P0 = 0，P1 = 0。** 批准门槛（P0/P1 未解决或关键验证缺失不可批准）满足。
- **既有实现观察（非本批引入，不计 finding）**：`ReaderViewModel.ResetReadingProgressAsync(bool confirm = false)` 内部恒传 `confirm: true`（`ReaderViewModel.cs:229-235`），即 UI 的确认门是唯一守卫；该方法不在本 diff 内。

## 4. 复核者未覆盖/受限项

- 未逐条重跑 AC2/AC3/AC6/AC7 的定向判别测试（它们位于区间基线 `4d90336e7` 之前的 commit，不在 `4d90336e7..b122fb926`）；其回归由全量 pytest 覆盖（3544 passed），AC2/3/6/7 的证据行由卡面/README 保留。若 DSH 要求对 8 项逐一字节级复核，需另开范围。
- 未在真实 Avalonia 窗口中做像素级布局检查；P2-4 的布局判断基于控件树/样式实现与无头测试，未做视觉回归。
- 未运行 Release Gate / 远端操作（不在本卡范围，且禁止）。

## 5. DoD §3 的 8 项 C1 是否可判达成

**结论：按 DSH 2026-11-14 裁决与卡面口径，可判达成——但只能表述为"7 项 MET + AC8 PARTIAL（留证完成、基线不可比已裁决）"，不得写成"8/8 MET"或"AC8 通过"。**

理由：

1. 卡面 AC1–AC7 均为 `<<MET>>`，本次复核逐项确认有判别测试且全量/定向复跑通过（AC1/AC4/AC5 为本区间新增；AC2/AC3/AC6/AC7 由既有提交与全量回归保障）。
2. AC8 的 AC 定义是"复跑专项 suite 并保留原始输出为证"——该动作已完成：主工作树 `12F/56P/60 subtests` 与 validation clone `3F/61P/2S/62 subtests` 两套原始输出均在仓库内，复核者复跑精确复现 12F/56P；卡面与 DSH 裁决明确 AC8 只能是 `PARTIAL`（"复跑留证 ≠ 复跑通过"），不得写 MET。
3. 因此"8 项落地"在**实现与留证**层面已经满足；AC8 的 PARTIAL 是 DSH 已裁决的接受口径（"留证完成 + 基线不可比已说明"），不是未实施。
4. **唯一歧义**：若 DoD §3 的字面口径被解释为"8 项全部 MET"，则当前**尚不可判达成**（差 AC8 的 MET），且该解释与卡面 `:57` / 卡面 `:106` 的裁决冲突。建议 DSH 在收口记录中明确采用"7 MET + AC8 PARTIAL 计为达成"的口径，并保留 12F 为 known limitation / 另开 EOL 口径卡。

## 6. 复核环境说明（重要）

1. **测试副作用（已在复核结束前被外部还原）**：复核者执行 `dotnet test` 后，`verification/FEA-09/logs/wire-redacted.ndjson` 曾被追加 1 行（测试自身产物，内容为既有 REDACTED 样本；时间戳 `2026-11-14T03:48:58Z`）。该副作用在 `README.md:57` 已有登记（"副作用 … 已 `git checkout --` 还原"）。受本任务"只读 + 不 checkout + 不修改既有文件"约束，复核者**未执行** `git checkout --`；复核结束前该行已被外部/并发进程还原，`git diff -- verification/FEA-09/logs/wire-redacted.ndjson` 为空。最终 `git status --porcelain` 仅剩本报告的 `??`。请 DSH 在提交前仍按 README 的做法校验该文件为空 diff。
2. **commit 数**：任务描述写"6 个 commit（`430b56def → b122fb926`）"，`git rev-list --count 4d90336e7..b122fb926` = **5**（`430b56def`、`77d145c92`、`153c6af7c`、`3bc2a2561`、`b122fb926`）；`4d90336e7` 是区间基线的 AC4/AC5 裁决 commit。若把基线计入则为 6，不影响复核结论。
3. **task 卡瞬时改动**：复核起点 11:42:47 的一次 `git status` 显示 ` M doc/tasks/MAINT-2-C1-BATCH-1.md`，随后立即恢复；该文件不在任何被审 commit 或最终 diff 中。提示可能有并发写入，但无证据表明影响被审 head。
4. **载体 §7 仍 `pending`**：本复核只能新建 `doc/reviews/MAINT-2-C1-BATCH-1-r1.md`，不能追写 `CONTRACT-UNFREEZE-2026-11-14-M2C1.md` §7；请 DSH 在处置时补记"r1 approved（见本报告）"或按流程另指派。

## 7. 复跑命令与原始结果（摘录）

```text
HEAD = b122fb926c106b2292c64c656ed2ba8002b4f2c7
git rev-list --count 4d90336e7..b122fb926 = 5
git diff --numstat 4d90336e7 b122fb926 -- doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md = 3	1

C:\Python314\python.exe -m pytest -q
  3544 passed, 10 skipped, 11 warnings in 279.21s (0:04:39)   EXIT=0

C:\Python314\python.exe -m pytest -q tests/core/test_library_wire.py tests/core/test_page_nav_projection.py
  11 passed in 4.34s                                          EXIT=0

dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests
  失败: 0，通过: 914，已跳过: 11，总计: 925，5 m 3 s        EXIT=0

dotnet test apps/desktop-avalonia/tests/NewManga.CoreClient.Tests
  失败: 0，通过: 180，已跳过: 24，总计: 204，23 s           EXIT=0

dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests
  失败: 0，通过: 321，已跳过: 74，总计: 395，6 s            EXIT=0

C:\Python314\python.exe -m pytest tools/governance/tests -q
  12 failed, 56 passed, 60 subtests passed in 122.36s         EXIT=1

check.ps1 (default)            = PASS (3 warnings)            EXIT=0
check.ps1 -TaskPath <本卡>      = PASS (3 warnings)            EXIT=0
verify_pins.ps1                = PIN AUDIT: PASS (all 18)     EXIT=0
generate_api_inventory.py --check = OK: rendered counts match FEA-C07 doc  EXIT=0
```

---

**复核者签名**：independent sub-agent (r1, read-only, not involved in implementation)，父会话 `session-90dc2552-798c-4921-abff-823ae8e6ca5e`，2026-11-14。
