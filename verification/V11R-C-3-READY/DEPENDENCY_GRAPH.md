# V11R-C-3 旧主题依赖图（当前 main 重核）

- 任务：`V11R-C-3-READY`（C-3 拆除前置就绪包）
- 基线 commit：`c5037b65fb4c80a42e96869789d12a6e2427e954`（当前 `main`，已合入新 UI / ThemeEngine Part B / DS D-1 终态 / B-4 I2b）
- 生成方式：`pwsh -NoProfile -File tools/v11r/build-dependency-graph.ps1`
- 机器可读证据：`dependency-graph.json`（631 条引用明细，`references[]` 含 file/line/symbol/kind/fate/text）
- 人类可读全表：`dependency-graph-table.md`
- 扫描范围：`git grep` 全部 tracked 文件（排除 `archive/**`、`bin/obj/node_modules`），符号 12 个
  `ThemePack/ThemePacks/ThemePackService/ThemePackMetrics/LayoutKind/NavPlacement/ShelfStyle/SettingsStyle/MotionProfile/LayoutProfile/LayoutProfiles`（`ThemePack` 的正则同时覆盖其派生符号）。

## 1. 总量与分类

| 分类 | 引用数 | 文件数 | 处置 |
|---|---:|---:|---|
| `legacy-theme-source`（`src/NewManga.Theme/ThemePack.cs`） | 83 | 1 | **DELETE-WITH-C3**：R5 删除项目 |
| `legacy-shell-production`（`src/NewManga.App/**` 旧壳） | 192 | 10 | **MIGRATE-THEN-DELETE**：R3 先迁移入口 |
| `legacy-tests`（`tests/NewManga.App.Tests/**` 旧测试） | 218 | 5 | **REPLACE-BEFORE-DELETE**：R4 替换断言后删 |
| `new-architecture`（src/**） | 14 | 6 | **NOT-A-DEPENDENCY**：新 `LayoutProfile` 类型 / 退役说明文字 |
| `new-architecture-tests`（tests/**） | 19 | 4 | **NOT-A-DEPENDENCY**：新架构测试引用新 `LayoutProfile` |
| `platform-struct-unrelated` | 19 | 12 | **NOT-A-DEPENDENCY**：`[StructLayout(LayoutKind...)]` P/Invoke，与主题无关 |
| `evidence-or-documentation` | 86 | 30 | **EVIDENCE-PIN-PROTECTED**：不改不删，按字节保留 |
| **合计** | **631** | **68** | — |

按符号：`ThemePackService=238`、`ThemePacks=108`、`ThemePack=81`、`LayoutKind=54`（其中 19 为 P/Invoke 假阳性）、
`LayoutProfile=56`（其中约 20 为新架构同名类型）、`LayoutProfiles=18`、`ThemePackMetrics=19`、`ShelfStyle=18`、
`NavPlacement=17`、`SettingsStyle=13`、`MotionProfile=9`。

## 2. 真实代码依赖（C-3 必须消除的部分）

生产路径 10 个文件（192 处）：

| 文件 | 引用 | 迁移动作 | 依赖的退役步骤 |
|---|---:|---|---|
| `src/NewManga.App/Views/Pages.cs` | 124 | 主题中心/旧书架页面：主题选择→Theme Studio/ThemeEngine；`ThemePackService.Brush`→`DynamicResource Nm.*`；旧页面随旧壳退役 | R3 + INT-1 |
| `src/NewManga.App/Views/MainWindow.axaml.cs` | 33 | 窗口级主题应用/标题栏 macOS 红黄绿：换 DS 根样式 + 新壳窗口 chrome | R3 |
| `src/NewManga.App/Views/ReaderWorkbenchPages.cs` | 13 | 旧工作台页：随旧壳退役，或迁移到 V2 Studio 页面 | R3 + INT-1 |
| `src/NewManga.App/Views/ProfileSections.cs` | 7 | 旧设置分区：迁移到新设置页（DS 控件） | R3 |
| `src/NewManga.App/Views/ImportExportPanels.cs` | 4 | 4 处 `Brush("CardBg"/"CardBorder")`→DS `Border.card` class | R3 |
| `src/NewManga.App/Views/CredentialSection.cs` | 4 | 4 处 `Brush(...)`→DS class/令牌 | R3 |
| `src/NewManga.App/App.axaml.cs` | 3 | 移除 `ThemePackService.ApplyDefault/Apply/ApplyVariant`；改由 ThemeEngine/DS 初始化（启动外观已由 `--variant` 映射到 `DesignSystemThemeManager.Initialize`） | R3 |
| `src/NewManga.App/ViewModels/MainViewModels.cs` | 2 | 旧主题选择模型（`ThemePacks`/`SelectedPack`）删除；换 Theme Studio 绑定 | R3 |
| `src/NewManga.App/Views/ProviderBindingsSection.cs` | 1 | 1 处 `Brush(...)`→DS class | R3 |
| `src/NewManga.App/AppOptions.cs` | 1 | `--theme`/`--variant` 旧证据钩子：改为新 `--theme-id`（`--variant` 保留给 DS 启动外观） | R5 |

旧主题项目自身 `src/NewManga.Theme/{ThemePack.cs,NewManga.Theme.csproj}`：83 处自引用，R5 整项目删除。

### 2.1 关键结论：新壳不依赖旧主题

新 UI 目录 `src/NewManga.App/Shell/**`（V2 AppShell、Studio、Reader、Commands）**零旧符号引用**；新设置/主题能力
已由 `NewManga.ThemeEngine` + `NewManga.DesignSystem` 承接。C-3 的删除对象被限定在旧 `Views/**`、旧
`ViewModels/**`、旧测试与 `NewManga.Theme`，**不会触碰新壳**。

## 3. 旧测试（218 处 / 5 文件）与替代映射

| 旧测试文件 | 引用 | 替代断言（新测试，已存在） |
|---|---:|---|
| `tests/NewManga.App.Tests/ThemeMacosTests.cs` | 88 | `ThemeEngine.Tests/BuiltInThemeGeneratorTests`（默认主题由 tokens 生成）、`ThemeServiceTests`（apply/appearance/切换失败回退）、`ThemePaletteComposerTests`（`ThemePackage→Nm.*`）、`ThemeValidatorTests`（对比度）、`DesignSystemThemeLayerSinkTests`（reduced-motion 令牌）、`V2ShellUiTests.ThemeToggle_SwapsTokens_WithoutRebuildingShellOrLosingSelection`（切换不丢选择/不重建）、`VisualEvidenceTests`（dark/light/HC 渲染） |
| `tests/NewManga.App.Tests/ThemeLayoutsTests.cs` | 100 | `V2ShellUiTests.Shell_RendersAt1600x1000_...`、`Shell_RendersAt1280And1024_WithoutBreakingLayout`（R-18 断点）、`ThemeServiceTests.SetLayout...`（`LayoutProfile` 独立持久化）、`V2ShellCoreTests.SpaceAndModeSwitch_...` |
| `tests/NewManga.App.Tests/ThemeMacosAuditTests.cs` | 9 | 字体：`ThemeEngine.Tests` 内置主题 schema/字体字段校验 + DS `TokenResourceDictionaryTests`（字体族令牌）；窗口 chrome：`V2ShellUiTests`（TopBand/窗口布局）+ `V2ConformanceTests`。**字体二进制审计无 1:1 替代**，C-3 R4 必须新增一条“仓库内无字体二进制”断言（脚本 `git ls-files '*.ttf' '*.otf'` 为空） |
| `tests/NewManga.App.Tests/S3ShellTests.cs` | 20 | `V2ShellUiTests`（TopBand/StatusBand/Library 渲染、1280/1024、键盘焦点、IME）、`V2ShellCoreTests`（选择/过滤/滚动保留、命令注册）、`V2ConformanceTests`（无裸值/禁用特效/令牌存在） |
| `tests/NewManga.App.Tests/S4ReaderWorkbenchTests.cs` | 1 | `ReaderLibraryTests`、`ReaderProgressTests`、`ReaderChapterSelectorTests`、`RegionWorkbenchUiTests`、`V2ShellUiTests.ReaderOverlay_...` |

删除顺序与门禁见 `DELETION_BATCHES.md`；**任一替代断言缺失时不得删除对应旧测试**（硬门）。

## 4. 假阳性说明（不得计入零引用门）

1. `LayoutKind` × 19：`[StructLayout(LayoutKind.Sequential)]` 等 P/Invoke 声明（`Host/Credentials`、
   `Host/Resources/TileChannel.cs`、`CoreClient/Issuer`、`scripts/smoke.ps1`、历史 verification 脚本）。
2. `LayoutProfile` × 17（新架构）：`NewManga.ThemeEngine.Models.LayoutProfile` 是新类型，与旧
   `NewManga.Theme.LayoutProfile` 同名不同命名空间；C-3 零引用门必须按**命名空间/文件路径**区分，禁止
   简单文本 grep 直接判失败。
3. `ThemePack` × 少数：ThemeEngine 的 README/csproj 中“取代旧 ThemePack 架构”的说明文字，以及新增的
   `NewManga.ThemeEngine.Tests/DependencyBoundaryTests.cs`（该测试**主动断言**新引擎程序集不引用旧符号，属于
   保护性引用，不计入依赖）。

## 5. C-3 R6 零引用门命令（按分类判定）

```powershell
# 1) 真实代码依赖必须为 0（新架构/文档/假阳性除外）
$graph = Get-Content verification/V11R-C-3-READY/dependency-graph.json -Raw | ConvertFrom-Json
$graph.references | Where-Object { $_.fate -in @('DELETE-WITH-C3','MIGRATE-THEN-DELETE','REPLACE-BEFORE-DELETE') }
# 2) 旧测试文件必须已删；3) NewManga.Theme 项目目录必须不存在
# 4) git grep 旧项目引用应为 0（允许 ThemeEngine README 的“已取代”说明，需人工确认）
# 5) 全仓 build -warnaserror + 全部测试绿（新架构项目）
```

随机漂移时重新运行生成脚本即可刷新 `dependency-graph.json` 与全表。

## 6. 证据 pin 保护清单（86 处 / 30 文件，禁止修改或删除）

- 计划/契约/任务/交接：`doc/plan/V11R_THEME_RETIREMENT_PLAN.md`（13）、`doc/plan/V11R_AVALONIA_CONTRACT.md`（3）、
  `doc/tasks/V11R-C-3.md`（3）、`doc/tasks/THEME-MACOS-1.md`（7）、`doc/tasks/THEME-MACOS-2.md`（3）、
  `doc/handoffs/THEME-MACOS-1/-2-*.md`（10）、`doc/handoffs/UI-SHELL-THEME-1-handoff.md`（2）、
  `doc/handoffs/PDF-EXPORT-UI-1-handoff.md`（4）、`doc/V11R_PROGRAM.md`（5）、`doc/V11R_TRACEABILITY.md`（1）、
  `doc/AD-002_TARGET_DESKTOP_ARCHITECTURE.md`（3）、`doc/design/ADR-0001_...md`（1）、
  `doc/reviews/V11R-D-1-r1-codex.md`（1）。
- 历史验证证据：`verification/THEME-MACOS-2/**`（7）、`verification/PDF-EXPORT-1|PDF-EXPORT-UI-1/REPORT.md`（3）、
  `verification/PUBLIC-RELEASE-P0-1/ls-tree.txt`（1）、`verification/RELEASE-REPACK-5/**`（2）、
  `verification/V11R-C-1/**`（4）、`verification/V11R-B-1/layout/hot-switch.json`（1）。
- 处理原则：C-3 代码改动不得修改这些字节；如新事实与旧文档冲突，按治理规则由 Lead 追加说明/新证据，不就地改写。


