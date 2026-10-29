# V11R-C-1 新 Theme Engine — 交付证据（Part A）

- Task：`task-10 / V11R-C-1`（10 子系统，取代旧 `ThemePack` 架构）
- Owner：theme-engine（独立 Reviewer 由 Lead 指派；Owner 未自审）
- Worktree：`G:/CODEX/New Manga.workspace/worktrees/V11R-THEME-ENGINE`
- Branch：`v11r/theme-engine`
- 基线：`bb957359e`（main，已含 R-09 令牌修订 `18a6a7782` 与 DS palette seam `a297a5eac`）
- **代码 head（本证据的构建/测试对象）**：`46837ba7c17d350263d4546ab42ed8f9c9325e80`
- 本文件所在 commit 仅新增本证据目录，不改代码；最终 delivery head 以 Lead 记录的 Handoff 为准。
- 状态：**Part A 完成**；Part B（`IThemeService` + DS 应用适配器）等待 Lead 通知 `ApplyThemeLayer` seam 就绪。

## 1. 质量门（全部通过）

| 门 | 命令（`apps/desktop-avalonia`） | 结果 | 日志 |
|---|---|---|---|
| 构建 | `dotnet build NewManga.sln -warnaserror -t:Rebuild -v m -nologo` | **0 warning / 0 error**，EXIT=0（13 个项目全部重新编译） | [build.log](build.log) |
| 全量测试 | `dotnet test NewManga.sln --no-build -v q --nologo` | **失败 0 / 通过 409 / 跳过 48 / 总计 457**，EXIT=0 | [dotnet-test-full.log](dotnet-test-full.log) |
| 本任务测试 | `dotnet test tests/NewManga.ThemeEngine.Tests -v n` | **135/135 通过** | [dotnet-test-themeengine.log](dotnet-test-themeengine.log) |
| 生成器可复现 | `dotnet run --project src/NewManga.ThemeEngine/tools/NewManga.ThemeEngine.ThemeGen -- --check` | up to date（逐字节一致），EXIT=0 | [generator-check.log](generator-check.log) |
| 变更规模 | `git diff --stat HEAD~4 HEAD` | 33 files / +6987（全部新增；既有项目源码 0 改动，仅 `NewManga.sln` +新增项目） | [git-diff-stat.log](git-diff-stat.log) |

分套件（既有套件无回归）：

| 套件 | 通过 | 跳过 | 总计 | 说明 |
|---|---|---|---|---|
| NewManga.ThemeEngine.Tests（本任务新增） | 135 | 0 | 135 | 证据见上 |
| NewManga.App.Tests | 156 | 5 | 161 | 5 个跳过为 sidecar fixture 缺失时的**自带** self-skip |
| NewManga.Host.Tests | 39 | 21 | 60 | 同上（`HostSidecarFact`） |
| NewManga.CoreClient.Tests | 39 | 22 | 61 | 同上（`SidecarFact`） |
| NewManga.DesignSystem.Tests | 40 | 0 | 40 | DS 全绿 |

> 既有 322 个测试（161+60+61+40）在本环境中 **274 通过 + 48 环境性 self-skip、0 失败**；
> skip 是既有 `Skip = reason` 机制（无 AC11 sidecar 副本时保持裸 `dotnet test` 绿），
> 与本次改动无关（本任务未修改既有测试/源码）。已有 CI 侧证据：`verification/V11R-A-2/` 记录 322/322 通过。

## 2. Acceptance Criteria 覆盖（Part A）

| # | 任务要求 | 实现 | 证据 |
|---|---|---|---|
| A1 | 新建 `src/NewManga.ThemeEngine`（net9.0 + Avalonia 11.3.22 + DS，入 sln，命名空间 `NewManga.ThemeEngine`） | `NewManga.ThemeEngine.csproj`；`dotnet sln add` | [build.log](build.log)、`git-diff-stat.log` |
| A2 | 模型严格按契约 §4 | `Models/ThemeModels.cs`、`Models/ThemeContracts.cs`（含 6 个冻结接口；契约缺口 `ThemeTokenSet`/`ThemeMetadata` 已获 Lead 批准，见 DEVIATIONS D-1） | 单测全绿；`Written_package_declares_no_layout_navigation_or_density` |
| A3 | JSON schema `newmanga.theme/1`：读写/版本/未知字段容忍/`.nmtheme` 与 `.json` | `Serialization/ThemePackageJson.cs`；手写 `JsonDocument`/`Utf8JsonWriter`（trim 安全）、确定性输出、未知字段 warning、被禁效果 error、schema 版本 error | `ThemePackageJsonTests`（15 例）、[schema-sample.nmtheme](schema-sample.nmtheme) |
| A4 | 内置 `newmanga-default` 由 `tokens.json` 生成（dark+light，生成器 + `--check`，勿手抄） | `Themes/BuiltInThemeGenerator.cs` + `tools/NewManga.ThemeEngine.ThemeGen`；产物 `Themes/newmanga-default.nmtheme`、`Generated/ThemeTokenBaseline.g.cs` | `BuiltInThemeGeneratorTests`（16 例）、[generator-check.log](generator-check.log) |
| A5 | `IThemeRegistry`：内置 + `%APPDATA%/NewManga/themes/`；`All/Find/Load/RefreshAsync/InstallAsync/UninstallAsync/ExportAsync` | `Registry/ThemeRegistry.cs`；内置 id 保留、校验后规范化落盘、损坏文件隔离进 `Diagnostics`、`.nmtheme`/`.json` 双扩展 | `ThemeRegistryTests`（15 例） |
| A6 | `IThemeValidator`：必填键/颜色格式/圆角 ≤3px/禁阴影渐变模糊/对比度/ schema/未知字段警告 | `Validation/ThemeValidator.cs` + `ThemeContrast.cs`；对比度判定表面口径见 DEVIATIONS D-3 | `ThemeValidatorTests`（34 例，含每错误分支） |
| A7 | `IThemePersistence`：设置文件 + 旧 ID 迁移 + 损坏文件回退不抛不阻塞 | `Persistence/ThemeSettingsStore.cs`、`LegacyThemeMigration.cs`；路径 `%APPDATA%/NewManga/theme-settings.json` | `LegacyThemeMigrationTests`（16 例）、[MIGRATION_CASES.md](MIGRATION_CASES.md)（9 旧 ID + 未知 + 空 = 11 类全覆盖） |
| A8 | `IThemePreviewEngine` 纯逻辑：Begin/Update/Commit/Cancel 状态机 + 回滚语义单测 | `Preview/ThemePreviewEngine.cs`；`Changed` 事件流（Began/Updated/Committed/Cancelled）；Commit/Cancel 幂等、Dispose 未提交回滚、单活会话 | `ThemePreviewEngineTests`（17 例） |
| A9 | Palette 合成：`ThemePackage + variant → IReadOnlyDictionary<string, object?>`（`Nm.*`，可直接应用到 Avalonia Resources） | `Palette/ThemePaletteComposer.cs`：整层 59 键（D-2）+ 35 色子集；不可变 brush | `ThemePaletteComposerTests`（18 例；含与 DS 生成盘逐色语义一致、字体缩放/行高预设/圆角/动效生效） |
| A10 | 单测：schema 往返、校验错误分支、迁移 11 类、注册表安装/卸载/导出、预览回滚、对比度计算 | 135 tests（见 §1） | [dotnet-test-themeengine.log](dotnet-test-themeengine.log) |

## 3. 关键决策（完整清单见 [DEVIATIONS.md](DEVIATIONS.md)）

- 契约缺口补全：`ThemeTokenSet`（35 色 + typography + corners + material/elevation + motion）与
  `ThemeMetadata`（engineVersion/generator/extra/LoadWarnings）经 Lead 批准；`ThemePackage` 不含任何布局/导航/密度字段（单测断言）。
- 对比度：正文 ≥7:1/次要 ≥4.5:1（panel+canvas）与状态对 panel ≥4.5:1 为 **error**；状态对
  canvas/raised 为聚合 **warning**（R-09 基线只保证 panel；Lead 裁决）。
- Palette 整层 59 键；`material`/`elevation` 无冻结令牌键，只校验不发明令牌。
- 旧 `ThemePack` 未被引用/修改；`NewManga.DesignSystem/**`、旧 `NewManga.Theme/**`、App `Views/**`/`Services/**`、Python 均 **0 改动**（git diff 仅新增目录 + sln）。

## 4. 未决项 / Part B 依赖

1. **Part B 等待 Lead**：DS `ApplyThemeLayer(ResourceDictionary layer, string themeId)` seam 就绪后实现
   `IThemeService`（`ApplyAsync/SetAppearanceAsync/SetContrastAsync/SetLayoutAsync/SetReducedMotionAsync/ResetToDefaultAsync + Changed`）、
   整层应用适配器、失败回退默认 + `LastError`、不重建窗口/不改画布像素。
2. **高对比**：Part B 由 DS 既有高对比盘叠加（DEVIATIONS D-11），ThemeEngine 不复制第三份令牌。
3. **动效 slow 档**：Studio 规格提到 slow，但契约/冻结令牌只有 Instant/Fast/Normal；需先改冻结基线（D-4）。
4. **Reviewer**：Owner 未自审；请 Lead 指派未参与实现的 Reviewer（建议同时核对契约 §4 签名逐字一致）。

## 5. 证据文件

| 文件 | 内容 |
|---|---|
| [build.log](build.log) | `-warnaserror -t:Rebuild` 全量构建原始日志（含命令/HEAD/EXIT） |
| [dotnet-test-full.log](dotnet-test-full.log) | 全解决方案测试日志 |
| [dotnet-test-themeengine.log](dotnet-test-themeengine.log) | 本任务 135 例逐例日志 |
| [generator-check.log](generator-check.log) | 生成器 `--check` 可复现校验 |
| [git-diff-stat.log](git-diff-stat.log) | `HEAD~4..HEAD` 变更规模（证明只新增） |
| [schema-sample.nmtheme](schema-sample.nmtheme) | 内置默认主题包全文样例（生成产物副本） |
| [MIGRATION_CASES.md](MIGRATION_CASES.md) | 旧 ID 迁移 11 类用例表 + 测试映射 |
| [DEVIATIONS.md](DEVIATIONS.md) | 偏差、契约缺口、裁决记录 |
| [git-head.txt](git-head.txt) | 证据采集时的代码 HEAD 与分支 |
