# FEA-07-RESIDUAL-4 scope review r1（独立上下文只读子代理）

| 项 | 值 |
|---|---|
| 审查者 | 独立只读 fresh subagent（由 DSH 主会话 `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5` 派发）；**未参与** FEA-07 / R4a / R4b 的实现或返修 |
| reviewer_kind | `subagent`（上下文独立；只读被审 head） |
| 审查类型 | **scope review**（任务卡 `status: proposed`；不改生产源码、不改契约字节） |
| 被审 base / head | `a49311cbe`（`main`；`git rev-parse HEAD` = `a49311cbedd9a1d308e59d11c83a2e5ea85147a8`；审查开始时工作树 clean） |
| 被审卡 | `doc/tasks/FEA-07-RESIDUAL-4.md`（`status: proposed`；`approval` 明确「scope 未冻结，不得实施」） |
| 结论 | **`NOT_RECOMMENDED`（现卡按现文）**；按本报告 §5/§6 缩窄为 **L-R4b-1-only** 后可 `READY-TO-FREEZE` |
| 方法 | 只读源码/文档/证据 + 静态枚举 + 只读真实 AppData 基线；未运行会写真实 `%APPDATA%` 的测试/进程；除本报告外未写任何文件 |

## 0. 审查者来源与独立性声明

- 本报告由 DSH 主会话派发的**独立上下文子代理**完成；该子代理未参与 FEA-07、FEA-07-RESIDUAL-2（R4a）、FEA-07-RESIDUAL-3（R4b）的任何实现、返修或证据生成，也未持有其实现会话上下文。
- 本审查全程只读：未修改生产源码、测试源码、任务卡、契约、pins 或 `verification/**` 既有字节；未 commit / push。
- 唯一新增文件为 `doc/reviews/FEA-07-RESIDUAL-4-scope-r1.md`。
- 本审查**未**在真实 `%APPDATA%` 上制造写入。唯一一次真实目录访问是**只读**读取 `window-material.log` 行数/尾部作为基线（§2.1）；未启动 App、未运行 App.Tests、未运行任何会写真实每用户目录的测试。
- 证据纪律：能核实的写 `file:line`；无法核实的写 `UNKNOWN` / `NOT_RUN` 并说明缺口，不把推测写成事实。

## 1. 结论 verdict

**`NOT_RECOMMENDED`（现卡按现文）**；**缩窄后可冻结**。

理由（按重要性）：

1. **核心问题真实存在**：L-R4b-1 **仍未修**。默认 `NewManga.App.Tests` 中仍有 **16 处** legacy `MainWindow.Show()` 使用无 `--log-dir` 的 `AppOptions`，`MainWindow.ResolveDiagnosticsRoot` 在无 `--log-dir` 时按设计回退到真实 `%APPDATA%\com.newmanga.desktop\logs`（`MainWindow.axaml.cs:1041-1047`），`Show()` 触发 `Opened` → 每次 1 行（`MainWindow.axaml.cs:137-141,1049-1057`）。因此本卡不能判 `DROP`。
2. **现卡范围不成立**：卡面把 L-R4b-1…5 + L-R4a-3 **6 项**混装（`doc/tasks/FEA-07-RESIDUAL-4.md:32-38`），其中只有 L-R4b-1 属于「测试隔离」同一风险面；L-R4b-2 属候选/结果证据、L-R4b-3 属 HostRuntime/原生 DPI、L-R4b-4 属运行纪律、L-R4b-5 属 pytest 登记、L-R4a-3 属产品规模性能。原样冻结会让一张测试隔离卡承担 DB 夹具、原生桌面、性能产品决策等不可同时验收的目标。
3. **原卡 AC 缺失**：现卡没有可判别 AC、没有 allowed_paths 测试面、没有「真实 AppData 零写入」的度量方法（`doc/tasks/FEA-07-RESIDUAL-4.md:27-42`）。按 §5/§6 改写后，范围小、判别强、回退清晰。
4. **不可在本审查内重测 delta**：任务红线禁止在真实 `%APPDATA%` 制造新写入，而现有 16 处 `Show()` 用例均不接收 `--log-dir`，无法「隔离地」驱动它们。故本轮 delta 只能记 `NOT_RUN`，用静态枚举 + 既有实测 `+16 行/轮` 互证（§2.1）。这不是把历史数字当本轮实测，见 §9 UNC-1。

## 2. 前置事实核对表（问题 1–2，逐项证据）

### 2.1 问题 1：L-R4b-1 是否仍存在

**判定：存在（未修）；不是「已修」也不是「部分修」。** 证据链如下。

| # | 核实点 | 证据（file:line / 命令） | 结果 |
|---|---|---|---|
| 1-1 | `--log-dir` / `--data-root` 可被解析 | `apps/desktop-avalonia/src/NewManga.App/AppOptions.cs:95-100`（`ValueKeys` 含 `data-root`/`log-dir`）；`:216-221`（赋值） | 两个参数均存在且大小写/等号/空格形式可解析 |
| 1-2 | 无 `--log-dir` 时的**产品默认**日志根 | `AppOptions.cs:343-348`：`dataRoot = DataRoot ?? %APPDATA%\com.newmanga.desktop`；`logDirectory = LogDirectory ?? <dataRoot>/logs` | 无参数 → 真实 AppData；仅 `--data-root` → Host 日志进隔离根 |
| 1-3 | **legacy 窗口**的日志根解析 | `apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml.cs:1041-1047`：`ResolveDiagnosticsRoot` 只看 `options.LogDirectory`；为空 → `%APPDATA%\com.newmanga.desktop\logs` | **仅 `--data-root` 不能隔离 `window-material.log`**；必须显式 `--log-dir`（或改产品） |
| 1-4 | 何时写 | `MainWindow.axaml.cs:137-141`：`Opened += … WriteMaterialDiagnostics()`；`:1049-1062` 每调用追加 1 行；`:142-161` + `:1068-1082` 是第二条 `RenderScaling` 分支（同样经 `ResolveDiagnosticsRoot`） | 构造不写；**`Show()` 才写**，每次 `Show()` 1 行材质行 |
| 1-5 | `StartupDiagnostics` 是否在 headless 测试中安装 | `apps/desktop-avalonia/src/NewManga.App/App.axaml.cs:41-44`（仅 `IClassicDesktopStyleApplicationLifetime` 分支安装）；`apps/desktop-avalonia/tests/NewManga.App.Tests/TestAppBuilder.cs:5,17-20`（headless + Skia，测试不经 desktop lifetime） | 默认套件**不**安装 `startup.log` sink；只读核对真实 `%APPDATA%\...\logs\startup.log` **不存在**，与代码一致 |
| 1-6 | 默认套件中构造并 `Show()` legacy `MainWindow` 的用例 | 见下方「16 处」表 | **16 处 / 6 文件**；与 R4b 实测 `+16 行/轮` 数量吻合 |
| 1-7 | 只构造、不 `Show()` 的 legacy 用例 | `ReaderChapterSelectorTests.cs:167,197,228,245,267,287,309,324`；`ReaderProgressTests.cs:104,112,278,295`；`ReaderLibraryTests.cs:123,144,160`；`StartupDiagnosticsTests.cs:181`（带 `--log-dir`，且不 `Show()`）；`StartupCompatibilityMatrixTests.cs:55-98`（经 `App.CreateShell`，只 `Close()`） | 不触发 `Opened`，不写 `window-material.log`；与 R4b「触发点是 `Show()` 而非构造」结论一致（`verification/FEA-07-RESIDUAL-3/DEFECTS.md:87`） |
| 1-8 | 既有实测 | `verification/FEA-07-RESIDUAL-3/DEFECTS.md:85-87`：**每轮 `NewManga.App.Tests`（默认门禁）稳定 `+16 行`**（对照实验 `14340 → 14356`）；`:87`：只跑 `StartupCompatibilityMatrixTests`（2 例、**无** `Show()`）→ `delta=0`；`verification/FEA-07-RESIDUAL-3/README.md:115` 同口径 | 机制与数量均有既有实测；本轮未重测（见 1-9） |
| 1-9 | 本轮 delta 度量 | **NOT_RUN**。原因：16 处 `Show()` 用例均不传 `--log-dir`，任何执行都会向真实 `%APPDATA%` 追加；任务红线禁止。只读基线：真实 `window-material.log` **14544 行**，最后写入 `2026-11-09T16:42:25.5938801+08:00`（最后一行 `2026-11-09T08:42:25.5940035Z`）；`startup.log` 不存在；cwd 下无 `com.newmanga.desktop` | 不改写、不删除；R4b closeout 表基线为 `14443`（`README.md:104`），当前 `14544` 的 `+101` 的归因未建立（UNC-2） |
| 1-10 | `--log-dir` 是否足以让这些用例零真实写入 | `MainWindow` 中 `_options` 仅作为 `ResolveDiagnosticsRoot` 的实参出现（`:654`、`:1053`、`:1072` 三处；另有字段/赋值 `:25,:57`），无其它行为依赖；16 个用例均注入 `FakeHostController`/`NullHostController`，不启动 Host | **测试侧补 `--log-dir` 即可**；不要求改产品。建议同时补 `--data-root` 作为未来防回归（当前非必需） |

**16 处默认套件 `MainWindow.Show()` 清单（构造点 / `Show()` 点 / 用例）**

| # | 文件 | 构造点 | `Show()` 点 | 默认套件用例（行） |
|---|---|---|---|---|
| 1 | `apps/desktop-avalonia/tests/NewManga.App.Tests/CredentialUiTests.cs` | 487 | 488 | `MainWindow_Closing_ClearsTheMaskedPlaintext`（482） |
| 2 | `.../F11HotkeyTests.cs` | 49（`NewWindow`） | 126 | `F11_IsIgnoredWhileSearchBoxHasFocus_AndDoesNotEatText`（123） |
| 3 | `.../LegacyAppearanceSyncTests.cs` | 83（`CreateWindow`） | 30 | `Cycle_theme_switches_both_the_variant_and_the_palette`（26） |
| 4 | 同上 | 83 | 54 | `Settings_appearance_row_switches_both_the_variant_and_the_palette`（50） |
| 5 | `.../ImportExportUiTests.cs` | 72（`OpenShell`） | 73 | `Bookshelf_ImportFiles_…`（153） |
| 6 | 同上 | 72 | 73 | `Bookshelf_ImportFolder_…`（196） |
| 7 | 同上 | 72 | 73 | `Bookshelf_ImportTypedFailure_…`（229） |
| 8 | 同上 | 72 | 73 | `Bookshelf_ImportPickerCancel_…`（251） |
| 9 | 同上 | 72 | 73 | `Workbench_ImportFiles_OpensTheSameFlow`（267） |
| 10 | 同上 | 309（`OpenReaderWithExport`） | 310 | `Reader_ExportFlow_…`（316） |
| 11 | 同上 | 309 | 310 | `Reader_ExportCancel_WhileRunning_…`（420） |
| 12 | 同上 | 309 | 310 | `Reader_ExportStartRefused_…`（481） |
| 13 | 同上 | 464 | 465 | `Reader_ExportWithoutTranslatedPages_DisablesStart`（458） |
| 14 | `.../RegionWorkbenchUiTests.cs` | 282 | 283 | `MainWindow_WorkbenchNavigation_LoadsTheRealRegionChain`（279） |
| 15 | `.../ThemeRetirementR4Tests.cs` | 56 | 60 | `Window_chrome_is_visual_only_and_keeps_real_window_behaviour`（53） |
| 16 | 同上 | 87 | 89 | `Startup_does_not_block_first_frame`（83） |

> 核对方法：`Select-String -Path apps/desktop-avalonia/tests/NewManga.App.Tests/*.cs -Pattern "new MainWindow\("` 共 **26** 处构造；其中 **16** 处存在可达 `Show()`；`dotnet test … --no-build --list-tests`（EXIT 0，仅列测试、不执行）确认上述 16 个用例均在默认套件。  
> `F11HotkeyTests.cs:244-245` 的 `F11_WhenImmersiveShowThrows_…` 已显式使用 `--log-dir`，是**反例**（不写真实目录），说明测试侧修复模式已在仓库存在；其 `LogImmersiveFailure` 也经同一 `ResolveDiagnosticsRoot`（`MainWindow.axaml.cs:650-663`）。

**问题 1 结论**：L-R4b-1 **存在（未修）**；不是「已修」，也不是「部分修」。R4b 的 r1/r2 只修了「有 `--log-dir` 时」的路径，未覆盖这批无 `--log-dir` 的既有用例（`DEFECTS.md:79-93`）。本卡有真实可交付内容。

### 2.2 问题 2：L-R4b-2/3/4/5 与 L-R4a-3 现状、可验证性与处置

| ID | 现状（证据） | 是否仍可验证 | 判定 | 理由 / 备注 |
|---|---|---|---|---|
| **L-R4b-2** | `region_candidates` 表在冻结 schema **不存在**；真实候选表是 `step_result_candidates`（`src/infrastructure/sqlite/schema.py:392`），V5 迁移建 `..._v5` 后 **rename 回** `step_result_candidates`（`schema.py:534-552`）。AC1 测试按「`_v5` 优先，否则 `step_result_candidates`，都无则 0」读（`apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea07Residual3IpcTests.cs:343,393-399`）；证据强度边界见 `verification/FEA-07-RESIDUAL-3/DEFECTS.md:5-10`、`README.md:109` | **可验证但成本高**：需用**生产装配**写出合法 `pipeline_runs`/`step_runs` 父行并让候选被解析。伪造 `run_json` 会让真实 Core 启动恢复崩溃：`src/application/tasks/service.py:1285-1302`（`recover_running_runs` → `_store.get`）→ `src/infrastructure/sqlite/pipeline.py:743-749`（`_read_run` → `_run(_load(run_json))`）→ `:382-407` `_run` 读 `value["run_id"]`（KeyError）；`DEFECTS.md:9` 已实测 | **SPLIT** | 与「测试隔离」无关；属候选/结果证据强化。建议另立「AC1 candidate 证据强化」卡（生产 run/step 父行 + 真实陈旧候选），不并入本卡。 |
| **L-R4b-3** | ①AC1 未过 `HostRuntime`/打包 sidecar：测试直接 `CoreServiceClient.StartAsync`（`Fea07Residual3IpcTests.cs:75`）+ `new HostCommandDispatcher(core: client)`（`:125`），没有 `HostRuntime`；`DEFECTS.md:103-108` 与 `README.md:110` 已如实登记。②AC4 缩放「调用点」未直接断言：`StartupDiagnosticsTests.cs:172-203` 直接调 `window.AppendScalingDiagnostics(...)`（`:186-187`），没有制造真实 `RenderScaling` 变化；真实进程矩阵用 `--shell=legacy` 只验证启动，不验证 DPI 变化（`README.md:91-93`） | ①**可验证**：Host 侧已有 gated `HostRuntime` 先例（如 `apps/desktop-avalonia/tests/NewManga.Host.Tests/HostRuntimeIntegrationTests.cs:20`、`HostFixture`），但需新增 gated 用例与打包 sidecar，属独立证据卡。②**headless 不可直接验证**：Avalonia headless 无真实 DPI 变化；原生侧 `FEA-07-AC5-NATIVE-1` 已用 `--shell=v2` + 隔离 `--log-dir`（`verification/FEA-07-AC5-NATIVE-1/README.md:7`；工具 `tools/run-native-matrix.ps1:95` 等），没有走 legacy 窗口的 `RenderScaling` 分支。可用原生 `--shell=legacy` + 隔离 `--log-dir` 补一次真实 DPI 断言（不碰真实 AppData），但属原生/AC5 范畴 | **SPLIT（HostRuntime 子项）/ DEFER（真实 DPI 子项）** | ①另立「AC1 HostRuntime 强化」gated 卡（可选，非阻塞）。②按用户 2026-11-08 授权豁免（`doc/reviews/ADJ-2026-11-RESIDUAL-WAIVER.md` §7.10 W-05：原生 DPI 矩阵 `NOT_APPLICABLE`，保留 `NOT_RUN`）与 `FEA-07-AC5-NATIVE-1` 的收窄口径，不并入本卡；reopen 条件 = 交互式原生会话 + legacy 壳真实 DPI 变化。 |
| **L-R4b-4** | 既有 `FluentResidual2VisualEvidenceTests.Captures_Residual2_Visual_Inventory_Only_When_Opted_In` 断言运行期间 `git status --porcelain -- verification` 前后相同（`apps/desktop-avalonia/tests/NewManga.App.Tests/FluentResidual2VisualEvidenceTests.cs:52,106`）；r1 首轮因并发写 `verification/` 假红，见 `DEFECTS.md:95-101`、`README.md:134-140` | 可复现但**不应靠改测试**解决；本卡可用运行纪律规避（静默树、串行、证据后写） | **DEFER（不修测试）** | 修改该 FEA-06 证据用例超出本卡范围，且会改既有证据断言。本卡证据计划强制「静默树 + 串行 + 运行后落证据」，并在日志中记录首次运行是否命中。 |
| **L-R4b-5** | `tests/fea09/test_referenced_flow.py::test_replay_conflicting_fingerprint_rejected`（`:424-446`）未在仓库任何 flake 清单登记；`doc/STATUS.md:20` 仅写「既有未登记 flake `test_referenced_flow` 隔离复跑绿」；`doc/tasks/FEA-07-RESIDUAL-3.md:114` 为唯一具名记录。机制上 `tests/fea09/conftest.py:33-44` 用 `sqlite3.connect(":memory:", check_same_thread=False)` 且 runtime 从 worker 线程提交，存在共享连接跨线程写入的 `sqlite3.InterfaceError` 风险（`DEFECTS`/卡面已观测） | 可验证（单文件隔离复跑绿；全量偶发）；但本卡零 Python diff，**不应跑 pytest** | **IN_SCOPE（仅登记，不修复、不运行）** | 以零代码方式在 `verification/FEA-07-RESIDUAL-4/DEFECTS.md` 登记：完整 node id、`sqlite3.InterfaceError`、隔离复跑结果、与既有 `test_plugin_sandbox.py::test_sandbox_job_kills_grandchildren` 区分；由 DSH 决定是否更新 STATUS。若 DSH 认为连登记也应拆分，可降为 `DEFER`。 |
| **L-R4a-3** | n50/n200/n500 的 p95 = **1196.19 / 2617.77 / 5668.25 ms**，均超 1000 ms，只记录、非 PASS（`verification/FEA-07-RESIDUAL-2/evidence/performance-scale-r4a.json`；`doc/tasks/FEA-07-RESIDUAL-2.md:51,194`；`PerformanceBaselineTests.cs:24-32,67-74`） | **可验证但属产品性能**：需决定「1000 ms 门槛是否适用于 n50/200/500」并可能改产品，不是测试隔离能解决 | **DROP（从本卡移除；保留独立 residual）** | 与 L-R4b-1 无共享代码/风险面；本卡做到也不改变规模性能。建议由 DSH/用户决定是否另立性能卡（profiling + 产品优化），在此之前维持「只记录、非 PASS」。 |

**问题 2 结论**：只有 **L-R4b-1 应进本卡**；L-R4b-2 **SPLIT**；L-R4b-3 **SPLIT（HostRuntime）/ DEFER（真实 DPI）**；L-R4b-4 **DEFER（运行纪律）**；L-R4b-5 **IN_SCOPE 仅登记**；L-R4a-3 **DROP（另案）**。

## 3. 建议 allowed_paths（精确到文件/目录）

> 原则：本卡是**纯测试隔离**卡；App 生产文件**零授权**。任何产品侧改动（例如让 `--data-root` 同时决定 `window-material.log` 根）都是**另一个 DSH 决策**，不在本卡。

### 3.1 Owner 可写（建议 11 条）

| # | path | 用途 | 备注 |
|---|---|---|---|
| 1 | `doc/tasks/FEA-07-RESIDUAL-4.md` | 冻结 scope/AC、实现记录、EV/Closeout | 仅追加/填写，不改历史字节 |
| 2 | `doc/reviews/FEA-07-RESIDUAL-4-*.md` | Review 链 | 含本 scope review |
| 3 | `doc/handoffs/FEA-07-RESIDUAL-4-*.md` | Handoff | 模板见 `doc/templates/HANDOFF.md` |
| 4 | `verification/FEA-07-RESIDUAL-4/**` | 证据目录（**必须**显式列入 `allowed_paths`，见 `doc/09_COLLABORATION.md` §4.2） | 含 `README.md`、`DEFECTS.md`、`logs/`、`evidence/`、`tools/` |
| 5 | `apps/desktop-avalonia/tests/NewManga.App.Tests/CredentialUiTests.cs` | 1 处改为隔离 options | 仅改构造参数，不改断言 |
| 6 | `apps/desktop-avalonia/tests/NewManga.App.Tests/F11HotkeyTests.cs` | 1 处改为隔离 options | 不触碰已有的 `--log-dir` 反例 |
| 7 | `apps/desktop-avalonia/tests/NewManga.App.Tests/LegacyAppearanceSyncTests.cs` | 2 处改为隔离 options | 不改主题断言 |
| 8 | `apps/desktop-avalonia/tests/NewManga.App.Tests/ImportExportUiTests.cs` | 9 处（经 3 个 helper）改为隔离 options | 不改导入/导出断言 |
| 9 | `apps/desktop-avalonia/tests/NewManga.App.Tests/RegionWorkbenchUiTests.cs` | 1 处改为隔离 options | 不改工作台断言 |
| 10 | `apps/desktop-avalonia/tests/NewManga.App.Tests/ThemeRetirementR4Tests.cs` | 2 处改为隔离 options | 不改 chrome/material 断言 |
| 11 | `apps/desktop-avalonia/tests/NewManga.App.Tests/LegacyWindowIsolationTests.cs`（**新增**） | 统一 helper（`IsolatedLegacyOptions()`）+ 源扫描守卫 + 真实 `MainWindow.Show()` 隔离判别测试 | 若实现者选择把 helper/test 并入既有文件，可去掉本条并按实际文件替换 |

**不建议**把整个 `apps/desktop-avalonia/tests/NewManga.App.Tests/**` 作为 glob 授权：改动面可枚举（6 文件 + 1 新文件），文件级更利于 diff 审计。

### 3.2 只能 DSH 单点提交（不得由本卡 Owner 修改）

| path | 约束 | 说明 |
|---|---|---|
| `apps/desktop-avalonia/NewManga.sln` | **本卡零 diff** | 共享组合根；本卡不新增项目/不改依赖 |
| `apps/desktop-avalonia/src/NewManga.App/App.axaml` | **本卡零 diff** | 组合根 UI；改它即越界 |
| `apps/desktop-avalonia/src/NewManga.App/App.axaml.cs` | **本卡零 diff** | 含 `StartupDiagnostics` 接线；本卡不碰启动语义 |
| `apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml.cs` | **本卡零 diff** | 若 DSH 决定把 `--data-root` 也纳入诊断根（产品行为变更），必须另立决策并由 DSH 单点提交，不得混入本卡 |
| `apps/desktop-avalonia/src/NewManga.App/AppOptions.cs` | **本卡零 diff** | 不改 CLI 语义；`--log-dir` 已存在，无需新参数 |
| `apps/desktop-avalonia/src/NewManga.App/Services/StartupDiagnostics.cs` | **本卡零 diff** | 已由 R4b 交付；本卡只测试隔离 |
| `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、`doc/tasks/README.md`、`doc/00_INDEX.md`、`doc/12_ROADMAP.md` | **DSH 生命周期写入** | 按 `doc/09_COLLABORATION.md` §3.6/§4；Owner 不回写状态 |
| `doc/plan/**`、`doc/contracts/**`、18 pins、`tools/governance/**` | **零 diff** | 冻结契约与门禁；本卡不改 |
| `src/**`（Python）、`tests/**`（Python） | **零 diff** | L-R4b-5 只登记，不修 Python |
| `apps/desktop-avalonia/tests/NewManga.Host.Tests/**`、`NewManga.Presentation.Avalonia.Tests/**` | **零 diff** | L-R4b-2/3 拆出后本卡不碰 |

### 3.3 共享组合根的单点提交规则

- `NewManga.sln`、`App.axaml`、`App.axaml.cs` 是**共享组合根**：即使未来确需改动，也只能由 **DSH 单点提交**（单独 commit，不与本卡测试改动混合），并在 Task 中记录授权依据。
- 本卡提交纪律：显式 pathspec，禁 `git add -A`；中文改动走 edit/UTF-8；提交前 `git diff --name-only` 必须 ⊆ §3.1；§3.2 必须零 diff。

## 4. 建议 AC（6 条；可观察、可判别、可挂证据）

> 所有 AC 都限定在 **headless / 默认套件**；本卡不需要真实 IPC、不需要桌面会话。

| AC | 断言（可观察） | 判别方式（失败即红） | 证据 |
|---|---|---|---|
| **AC-R4-1（站点完整）** | 默认套件中所有真实 `MainWindow.Show()` 站点（当前 16 处 / 6 文件，逐一列于 §2.1）都使用显式隔离 `--log-dir`（建议同时 `--data-root`）；不存在「默认 `AppOptions` + `Show()`」的 legacy 窗口 | 新增 `LegacyWindowIsolationTests.AllDefaultSuiteLegacyWindowShows_AreExplicitlyIsolated`（源扫描，先例 `V2ShellUiTests.cs:1047-1058`）：6 个文件内任何 `new MainWindow(` 若不在 `IsolatedLegacyOptions()` 上下文 → **RED**；`git grep -n "new MainWindow("` 人工核对 16/16 | 测试源码、`logs/mainwindow-sites.txt`、测试通过日志 |
| **AC-R4-2（真实 AppData 零写入，强断言）** | 默认 `NewManga.App.Tests` 整轮（无 `NEWMANGA_FEA07_*` 门禁）运行前后，真实 `%APPDATA%\com.newmanga.desktop` 与 `%APPDATA%\NewManga` 的递归快照不变：文件相对路径集合、字节长度、`logs/window-material.log` 行数、`logs/startup.log` 存在性全部 delta=0 | harness `verification/FEA-07-RESIDUAL-4/tools/appdata-isolation-check.ps1`：delta≠0 → **exit 1**；baseline 缺失/采集失败 → **fail closed（exit 1）**，不得 skip；日志必须含 before/after/delta 与命令头 | `evidence/appdata-isolation.json`、`logs/appdata-isolation.log`、`logs/app-tests-full.log` |
| **AC-R4-3（harness 自身可判别）** | harness 的「零写入」比较不是空断言：对**隔离临时文件**追加 1 行 → 必须报 `delta=1` 且 exit 1；不追加 → exit 0。全程不碰真实 AppData | `-SelfTest` 模式；若追加后仍 exit 0 → **RED**；若自检写到真实路径 → P0 违规 | `logs/appdata-isolation-selftest.log`、`evidence/appdata-isolation-selftest.json` |
| **AC-R4-4（产品契约仍成立）** | 真实 `MainWindow` + `--log-dir=<temp>` + `Show()` → `<temp>/window-material.log` **恰好 1 行**材质行；cwd 下无 `com.newmanga.desktop`；真实 `%APPDATA%` 行数不增长（只读比较） | 新测试：隔离文件不存在/行数≠1/cwd 出现标记/真实行数增长 → **RED**；**禁止**用「去掉 `--log-dir`」做变异（会写真实 AppData） | 测试日志、隔离目录清单 |
| **AC-R4-5（回归/门禁）** | diff ⊆ §3.1；§3.2 零 diff；build 0 warning/0 error；`NewManga.App.Tests` **0 failed** 且 passed ≥ 831 + 新增、skipped = 11（无新增 skip/gated）；全量 .NET 0 failed 且 passed ≥ 1794 / skipped 107（或给出新增测试后的总数与差值）；`check.ps1` PASS；pins 18/18；`git status` 仅预期文件 | 任一 gate 非 0、diff 越界、出现新 skip/failure → **RED**；全量首轮若命中既有 `FluentResidual2VisualEvidenceTests` 假红，必须按 §6 静默树复跑并保留首轮日志，不得静默改写 | `logs/build.log`、`logs/app-tests-full.log`、`logs/full-solution.log`、`logs/governance.log`、`logs/pins.log` |
| **AC-R4-6（residual 处置/证据）** | `doc/tasks/FEA-07-RESIDUAL-4.md` 与 `verification/FEA-07-RESIDUAL-4/DEFECTS.md` 明确：D-R4b-7 **resolved**（含 head、delta=0）；L-R4b-2 `SPLIT`、L-R4b-3 `SPLIT/DEFER`、L-R4b-4 `DEFER（运行纪律）`、L-R4b-5 `已登记`、L-R4a-3 `DROP（另案）`；L-R4b-5 含完整 node id/错误/复现/隔离结果；EV 表 + Resource Manifest + Handoff 齐全；Owner 不翻 `status` | 缺任一项 → **RED**；把 `NOT_RUN`/`SPLIT` 写成 PASS/MET → **RED** | 卡面、`DEFECTS.md`、EV 表、Handoff、`RESOURCE-MANIFEST.json` |

## 5. 证据计划

| # | 类别 | 命令/步骤 | 环境 | 期望/判别 | 证据 |
|---|---|---|---|---|---|
| E1 | 静态（headless，不执行） | `git grep -n "new MainWindow(" -- apps/desktop-avalonia/tests/NewManga.App.Tests` + `--list-tests`（只列不跑） | Windows / pwsh | 26 处构造、16 处 Show；6 文件 | `logs/mainwindow-sites.txt` |
| E2 | headless | `dotnet build apps/desktop-avalonia/NewManga.sln -c Debug` | .NET SDK 10.0.401（目标 net9.0） | 0 warning / 0 error | `logs/build.log` |
| E3 | headless | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --no-build --filter "FullyQualifiedName~CredentialUiTests|FullyQualifiedName~F11HotkeyTests|FullyQualifiedName~LegacyAppearanceSyncTests|FullyQualifiedName~ImportExportUiTests|FullyQualifiedName~RegionWorkbenchUiTests|FullyQualifiedName~ThemeRetirementR4Tests|FullyQualifiedName~LegacyWindowIsolationTests"` | headless Avalonia | 0 failed；对应 16 站点全绿 | `logs/app-tests-targeted.log` |
| E4 | headless（核心强断言） | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --no-build`，前后由 harness 采真实 AppData 快照 | headless；静默树；串行 | 0 failed；`window-material.log` delta=0；两棵树 delta=0；`startup.log` 不出现 | `logs/app-tests-full.log`、`evidence/appdata-isolation.json` |
| E5 | headless（回归） | `dotnet test apps/desktop-avalonia/NewManga.sln --no-build`（静默树/串行） | headless；运行前 `verification/FEA-09` clean；运行后 `git checkout -- verification/FEA-09` | 0 failed；≥1794 passed / 107 skipped；若首轮假红按 §6 复跑 | `logs/full-solution.log` |
| E6 | harness 自检 | `pwsh -NoProfile -File verification/FEA-07-RESIDUAL-4/tools/appdata-isolation-check.ps1 -SelfTest` | 隔离临时文件 | 追加 1 行 → delta=1/exit 1；不追加 → delta=0/exit 0 | `logs/appdata-isolation-selftest.log`、`evidence/appdata-isolation-selftest.json` |
| E7 | 治理 | `pwsh -NoProfile -File tools/governance/check.ps1`；`pwsh -NoProfile -File tools/governance/verify_pins.ps1`；`git status --short`；`git diff --name-only` | Windows / pwsh | EXIT 0；pins 18/18；diff ⊆ allowed_paths；§3.2 零 diff | `logs/governance.log`、`logs/pins.log` |
| E8 | pytest | **NOT_RUN**（本卡零 Python diff；L-R4b-5 仅登记）。若 DSH 要求，只跑单 node 并记录；不得把「隔离复跑绿」写成全量 PASS | Python 3.14.6 | 记录 `NOT_RUN` 原因 | `DEFECTS.md` |
| E9 | 真实进程 / IPC | **NOT_RUN / 不需要**。本卡不改 Host/IPC；产品契约由 E3/E4 的 headless 断言覆盖。可选：复用 R4b `startup-matrix.ps1` 的 `--shell=legacy` 案例做一次隔离 `--log-dir` 交叉核对（已有 delta=0 证据） | 交互桌面（仅可选） | 不得写真实 AppData；无桌面会话则 skip + reason | 可选 `logs/startup-matrix-legacy.log` |

**运行纪律（L-R4b-4 规避）**：E4/E5 必须在**静默树**执行——运行前所有文档/证据写入完成，运行期间不编辑 `verification/**`、不并发跑其它 Agent/门禁；harness 的 `before/after` 快照在内存/仓外 workspace 完成，`verification/FEA-07-RESIDUAL-4/**` 的日志与 JSON **运行结束之后**再落盘（否则 `FluentResidual2VisualEvidenceTests` 的 `git status --porcelain -- verification` 会把本卡证据误判为变更）。

## 6. 风险与回退

| ID | 风险 | 触发/影响 | 缓解 | 中止/回退边界 |
|---|---|---|---|---|
| R-1 | **红线：漏改站点 → 真实 AppData +1 行/Show** | 16 处中任一未带 `--log-dir`，E3/E4 就会写真实目录 | 先做 E1 静态枚举 + AC-R4-1 源扫描；E3 只跑 6 类（先小后大）；harness fail closed | 发现 delta>0 **立即停止**后续大套件；该行**不删除**（删除又是一次写），以新行数为基线并如实登记；修复后重跑 |
| R-2 | 并发写 `verification/` 假红（L-R4b-4） | E4/E5 期间任何 `verification/**` 变更 → `FluentResidual2VisualEvidenceTests` FAIL | 静默树、串行、证据后写；首轮日志保留 | 若命中，先 `git status --porcelain -- verification` 判定是否仅并发写入；静默树复跑；不得改该断言 |
| R-3 | `verification/FEA-09/logs/wire-redacted.ndjson` 既有副作用 | 全量 sln 时 CoreClient 测试改写该 tracked 文件 → git status 噪声/假红 | E5 前 clean；E5 后 `git checkout -- verification/FEA-09`；App.Tests 单独先跑 | 若 E5 因 FEA-09 失败，按既有 flaky 处置（复跑/恢复），不记本卡回归 |
| R-4 | pytest 既有 flake（L-R4b-5） | 若跑全量 pytest，可能命中 `sqlite3.InterfaceError` | 本卡 **NOT_RUN**，只登记 | 若 DSH 要求跑，单 node 隔离复跑；不得用重跑掩盖全量失败 |
| R-5 | 源扫描守卫脆弱（格式/换行/helper 重命名） | 误报 RED，浪费返修 | 只扫 6 个文件 + 允许 `IsolatedLegacyOptions()`；模式固定；把扫描作为**辅助**，AC-R4-2 的 delta 才是主证据 | 若扫描误报，修正扫描规则（不放松到「任意 options」） |
| R-6 | 临时目录泄漏/冲突 | 16 处共用固定目录会互相覆盖或残留 | 每处唯一 GUID 目录（`Path.Combine(Path.GetTempPath(), "nm-r4-legacy-" + Guid.NewGuid().ToString("N"))`）；`IDisposable` 清理；不删用户路径 | 清理失败只记 warning，不影响断言 |
| R-7 | 测试计数漂移 | 新增测试导致 passed 增加；若出现新 skip 说明门禁被误加 | 基线固定 831/0/11；新增 passed 计入并解释；skipped 必须仍为 11 | 出现新 skip → 视为 scope 变更，回 DSH |
| R-8 | 全量运行超时/资源竞争 | 全量 sln 可能 10+ 分钟；并行会放大 flake | 串行、后台 job、足够 timeout；先 App.Tests 再全量 | 超时记 `NOT_RUN`（不记 PASS）；重跑一次仍超时则拆分为项目级 |
| R-9 | `StartupDiagnostics` 进程级 `Trace` 状态 | 新测试若安装 sink，可能污染后续测试（`Trace.AutoFlush`） | 新测试**不安装** sink；如必须，`finally` 调 `ResetForTests()`（`StartupDiagnostics.cs:141-159`） | 发现跨测试污染 → 移除安装或加隔离 fixture |
| R-10 | 产品侧 scope creep | 为实现「`--data-root` 也隔离诊断」而改 `MainWindow.axaml.cs`/`AppOptions.cs` | 本卡零授权；该改动另立 DSH 决策 | 一旦需要改产品文件 → **停止本卡**，回 DSH 重新冻结 |

**回退**：本卡只改测试；回退 = revert 测试 commit（含新增测试文件），不涉及数据迁移、不删用户数据、不改 pins/契约。若发生真实 AppData 写入，按 R4b 先例「不删除、登记、重设基线」，并在 `DEFECTS.md` 写清 before/after。

## 7. 门禁结果（本审查，只读）

| 门禁 | 命令 | EXIT | 结果 | 备注 |
|---|---|---|---|---|
| 治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1` | **0** | **PASS (3 warnings)** | warnings：12 个非终态 Task；`doc/STATUS.md` 2985 bytes/29 lines 达 80%；`doc/REBASELINE_PLAN.md` 6989 bytes/63 lines 达 80% |
| Pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **0** | **PIN AUDIT: PASS (all 18)** | C01b…C17 + FEA01 全 OK |
| 工作树（审查开始） | `git status --short` | 0 | 空 | HEAD `a49311cbe`，clean |
| 工作树（报告写入后） | `git status --short` | 0 | 仅 `?? doc/reviews/FEA-07-RESIDUAL-4-scope-r1.md` | 本审查唯一新增文件 |
| 测试枚举（辅助，不执行） | `dotnet test … --no-build --list-tests` | **0** | 列出 16 个目标用例 | 不运行测试、不写真实 AppData；报告 §2.1 的 16 处依据 |

> 本审查**没有**运行 `NewManga.App.Tests`/全量 `dotnet test`/pytest/真实进程；因此不产生新的真实 AppData 写入。只读核对：真实 `window-material.log` 14544 行（最后写入 `2026-11-09T16:42:25+08:00`），`startup.log` 不存在，cwd 下无 `com.newmanga.desktop`。审查前后行数不变。

## 8. 剩余未知项与不确定性

| ID | 不确定性 | 缺什么证据 / 影响 |
|---|---|---|
| UNC-1 | **本轮 delta 未实测** | 红线禁止执行 16 处无 `--log-dir` 的 `Show()`。结论依赖：静态 16 处 + R4b 既有实测 `+16/轮`（`DEFECTS.md:85`）。不把历史数字写成本轮实测。 |
| UNC-2 | R4b closeout 基线 `14443`（`README.md:104`）→ 当前 `14544` 的 `+101` 归因 | 无运行记录/时间窗；可能来自后续多次 App.Tests、真实 App 启动或其它任务。未建立归因，不作为本卡新增缺陷。 |
| UNC-3 | 默认套件是否还写 `%APPDATA%\NewManga`（主题/外观） | 代码审查只见 `ThemeHomeTests` 明确使用临时/自定义路径并断言默认未变；**未**对全树做实跑度量。AC-R4-2 要求两棵树快照，正是为了在这次实现中回答；若命中，需 DSH 决定是否扩域。 |
| UNC-4 | L-R4b-2 的生产 run/step 父行夹具成本 | 未做 spike；已知伪造 `run_json` 会让 Core 恢复崩溃（`pipeline.py:382-407`）。拆分卡的实现者需先验证生产装配路径。 |
| UNC-5 | L-R4b-3 HostRuntime 强化的价值/成本 | 未做 spike；Host 侧有 gated `HostRuntime` 先例，但把 UI 切换接到 HostRuntime 可能需要新的 gated 夹具；不影响本卡。 |
| UNC-6 | L-R4b-3 真实 DPI 下 legacy `RenderScaling` 是否触发 | 现有原生证据用 `--shell=v2` + 隔离目录（`FEA-07-AC5-NATIVE-1/README.md:7`），未覆盖 legacy 分支；真实 DPI 行为仍 `NOT_RUN`，受 AC5 豁免/W-05 约束。 |
| UNC-7 | L-R4b-4 的假红是否可确定性复现 | 依赖运行期间外部写入；本审查只做静态确认（`FluentResidual2VisualEvidenceTests.cs:52,106`），未制造并发写。 |
| UNC-8 | L-R4b-5 flake 触发条件 | 本轮未跑 pytest；只确认登记缺失与共享连接线程模型（`tests/fea09/conftest.py:33-44`）。 |
| UNC-9 | L-R4a-3 的产品门槛解释 | 1000 ms 是否适用于 n50/200/500 是产品/DSH 决策；本审查不替用户决定。 |
| UNC-10 | `step_result_candidates_v5` 命名细节 | V5 迁移建 `_v5` 后 **rename 回** `step_result_candidates`（`schema.py:534-552`）；R4b 文档写「改名为 `_v5`」不精确。拆分卡应使用最终表名，避免再次踩 `region_candidates` 式口径。 |

## 9. Findings（scope 级）

| ID | 级别 | 位置 | 触发/影响 | 证据 | 建议 |
|---|---|---|---|---|---|
| S-01 | **P1** | `doc/tasks/FEA-07-RESIDUAL-4.md:32-38` | 6 项 residual 混装；4 项与测试隔离无关/不可同卡验收 | §2.2 逐项 | 只保留 L-R4b-1；其余按 §2.2 拆分/降级 |
| S-02 | **P1** | `doc/tasks/FEA-07-RESIDUAL-4.md:22-28` | 现卡 allowed_paths 无测试文件，AC 无可判别断言；按现文无法实施 | 卡面 22-28、40-42 | 按 §3/§4 改写 |
| S-03 | **P1** | `MainWindow.axaml.cs:1041-1047`；`AppOptions.cs:343-348` | `--data-root` **不能**隔离 `window-material.log`；只补 `--data-root` 的修复会假绿 | §2.1 1-2/1-3 | 修复必须显式 `--log-dir`（测试侧），或在 DSH 决策下改产品解析 |
| S-04 | **P2** | `doc/tasks/FEA-07-RESIDUAL-4.md:33` | 卡面「稳定 +16 行」是既有实测、本轮未重测；且 `DEFECTS.md:82-84` 的「16 个文件命中」与真实「16 处 Show / 6 文件」不一致 | §2.1 1-6/1-8 | 新卡用「16 处 Show / 6 文件」并记录实测 delta |
| S-05 | **P2** | `FluentResidual2VisualEvidenceTests.cs:52,106` | 本卡证据写入会触发既有假红；不在本卡修该测试 | §2.2 L-R4b-4 | 运行纪律 + 证据后写；另案修测试 |
| S-06 | **P2** | `doc/tasks/FEA-07-RESIDUAL-3.md:114`；`doc/STATUS.md:20` | L-R4b-5 只有一句「未登记」，没有完整 node/错误/复现 | §2.2 L-R4b-5 | 本卡 DEFECTS.md 登记；DSH 决定 STATUS 更新 |
| S-07 | **P3** | `verification/FEA-07-RESIDUAL-3/README.md:109`；`DEFECTS.md:7` | 候选表名表述不精确（`_v5` 是迁移中间名） | `schema.py:534-552` | 拆分卡按最终名 `step_result_candidates` 写 |
| S-08 | **P3** | `doc/STATUS.md`（2985 bytes/29 lines，80%）；`doc/REBASELINE_PLAN.md`（6989 bytes/63 lines，80%） | 释放新卡可能触预算；与本卡代码无关但影响 DSH 冻结 | check.ps1 warnings | DSH 冻结时压缩/替换旧行，不扩预算 |

## 10. 建议的冻结形态（供 DSH 直接采用）

- **卡名/ID**：保留 `FEA-07-RESIDUAL-4`（或改名 `FEA-07-LEGACY-TEST-ISOLATION-1`，但 ID 变更需改 LEDGER/指针，成本更高）。
- **标题**：`默认套件 legacy MainWindow.Show() 真实 AppData 零写入（L-R4b-1 / D-R4b-7）`。
- **范围**：仅 §3.1 的 11 条路径 + §4 的 6 条 AC；§3.2 零 diff。
- **Owner/Reviewer**：按现有治理；Reviewer 必须上下文独立（不得由实现会话/实例自审）。
- **re-home**：L-R4b-2 → 新候选证据卡；L-R4b-3 → HostRuntime 强化卡（可选）+ 原生 DPI `NOT_RUN`（AC5 豁免）；L-R4b-4 → 运行纪律（本卡）+ 测试卫生另案；L-R4b-5 → 本卡登记（零代码）；L-R4a-3 → 产品性能卡/维持只记录。
- **行文红线**：不得写「所有 headless 测试零 AppData 写入」直到 AC-R4-2 实测 delta=0；不得把 `NOT_RUN`/`SPLIT` 写成 PASS/MET。
