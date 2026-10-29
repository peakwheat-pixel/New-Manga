# V11R-C-2 Theme Studio 独立页面 — 证据与交接

- Task：`V11R-C-2`（Owner：`theme-studio`；Lead：DSH）
- 分支：`v11r/theme-studio`，基线 `907339511`（merge(v11r): V11R-C-1 Part B …；含 R-19 证据纪律、R-20 App→ThemeEngine 引用、V11R-C-1 Part A+B）
- 规范：`doc/design/theming/THEME_STUDIO_SPEC.md`（FROZEN）、`doc/plan/V11R_AVALONIA_CONTRACT.md`、`doc/design/redesign-v1/40-fusion/{FUSION_SPEC,DESIGN_SYSTEM}.md`、`doc/plan/V11R_SCREEN_SPECS.md §6`
- 状态：实现完成，本地质量门全绿；等待独立 Review 与 V11R-INT-1 接线。

---

## 1. 结论摘要

Theme Studio 以 **独立覆盖式表面**（不是第五空间）实现：左栏 7 分区导航（图标 + 标题 + 副标题 + 脏标记）、主区随分区、右栏 320px 摘要（当前主题 / 外观 / 密度 / 布局 / 对比度校验 / 取消 / 应用）。

数据与行为全部走 **main 已合入的真实主题引擎**：`ThemeService`（Part B）负责主题语义、预览会话、持久化与回退；`ThemeRegistry` 负责目录/安装/卸载/导出；`ThemeValidator` 负责导入校验与对比度门槛；`ThemePaletteComposer` 负责 59 键主题层；`LegacyThemeMigration` 负责旧 ID 迁移；`DesignSystemThemeLayerSink` + `DesignSystemThemeManager` 负责应用级整层替换（不重建窗口）。

**关键架构（Lead 已批准）**：主题选择预览 = 引擎预览会话（应用级层替换 + Cancel 完整回滚）；**未保存的编辑器草稿**（未安装包）无法进入引擎会话，改用 **作用域 `ResourceDictionary` + `PaletteScope`** 渲染，因此编辑器实时预览 / 取消都不触碰应用级资源，天然满足 AC9 的像素不变要求。

---

## 2. 质量门（本分支最终代码）

| 门 | 命令（在 `apps/desktop-avalonia`） | 结果 | 日志 |
|---|---|---|---|
| 构建 | `dotnet build NewManga.sln -warnaserror -t:Rebuild` | **0 warning / 0 error**（EXIT=0） | [build.log](build.log) |
| 测试 | `dotnet test NewManga.sln --no-build` | **0 失败**：App.Tests 268 通过 / 6 跳过；ThemeEngine 200；DesignSystem 67；Host 42 / 24 跳过；CoreClient 42 / 25 跳过（EXIT=0） | [test.log](test.log) |
| 新增测试 | `--filter "FullyQualifiedName~V2ThemeStudio"` | **36/36 通过**（含 2 个 headless 截图测试） | test.log |

日志最后一行分别记录 `BUILD_EXIT=0` / `TEST_EXIT=0`。

---

## 3. 交付物

### 3.1 生产代码（全部在本任务写域内）

| 层 | 文件 | 职责 |
|---|---|---|
| 门面 | `ViewModels/V2/ThemeStudio/ThemeStudioServiceContracts.cs` | `IThemeStudioService`（UI 最小面）、`IThemeStudioFileGateway`、`ThemeStudioFavoritesStore` |
| 适配器 | `ViewModels/V2/ThemeStudio/ThemeEngineThemeStudioService.cs` | **真实实现**：包装 `ThemeService` + `ThemeRegistry` + `ThemeSettingsStore` + `ThemeValidator`；`CreateProduction(...)` 是唯一生产构造路径 |
| 调色板 | `ThemeStudioPaletteBuilder.cs` | 作用域层：`ThemePaletteComposer`(59 键) + DS 高对比/密度/减弱动效覆盖 |
| 对比度 | `ThemeStudioContrastAuditor.cs` | 用引擎 `ThemeContrast.Ratio`（WebAIM 公式）计算 13 行实时数值，不自造公式 |
| 模型 | `ThemeStudioModels.cs`、`ThemeStudioSectionItems.cs` | 分区/问题/能力/对话框/对比度行/卡片/选项模型 |
| 状态机 | `ThemeStudioViewModel.cs` | 唯一状态源：分区、脏标记、三出口、应用/取消/重置、键盘路由、对话框、像素作用域 |
| 分区 VM | `ThemeStudioLibraryAndMyThemesViewModels.cs`、`ThemeStudioPreviewAndAppearanceViewModels.cs`、`ThemeStudioEditorViewModel.cs`、`ThemeStudioImportExportAndResetViewModels.cs` | 7 分区的数据与命令 |
| 测试沙箱 | `StubThemeStudioService.cs` | **仅测试用**：真实引擎链路 + 临时目录 + `NullThemeLayerSink` + 确定性 fixture；生产 UI 不使用 |
| 视图 | `Views/V2/ThemeStudio/ThemeStudioView.axaml(.cs)` | 表面骨架、右栏、对话框、键盘/焦点 |
| 分区视图 | `Views/V2/ThemeStudio/Sections/*.axaml(.cs)` | 7 个分区 |
| 预览 | `Views/V2/ThemeStudio/Preview/*` | 书架 / 工作台 / 阅读器真实控件树 + 迷你三视图 + `IPreviewSurfaceProvider` seam |
| 控件 | `Views/V2/ThemeStudio/Controls/{PaletteScope,ThemeCardTemplates}` | 作用域调色板挂载、卡片模板 |
| 样式 | `Views/V2/ThemeStudio/Styles/ThemeStudioStyles.axaml` | 语义 class；全部值来自 `Nm.*` 令牌 |
| 集成宿主 | `Shell/V2/ThemeStudio/ThemeStudioSurface.axaml(.cs)` | 覆盖表面宿主：`OpenAsync(section)` / `Close()` / `RequestClose` |

### 3.2 测试

- `tests/NewManga.App.Tests/V2ThemeStudioTests.cs`：34 个行为/语义测试（分区状态机、脏标记/三出口、取消回滚、真实预览会话、编辑器草稿作用域、对比度审计、导入阻止、round-trip、9+2 迁移、键盘路由、响应式断点、收藏/复制/删除、重置、外观持久化）。
- `tests/NewManga.App.Tests/V2ThemeStudioScreenshotTests.cs`：2 个 headless 截图/像素测试。

### 3.3 证据

- `screens/*.png`：24 张真实渲染帧（`Avalonia.Headless` + Skia，`UseHeadlessDrawing=false`，`CaptureRenderedFrame()`，1600×1000 / 1280 / 1024）。
- `screens/screens.json`：每帧路径、尺寸、字节数、SHA-256、主背景色、64 格签名、渲染器与服务来源。
- `screens/pixel-hash.json`：固定像素画布 + 「未保存编辑」文本探针在预览前/预览中/取消后的 SHA-256 一致性。
- `compliance.md`：设计系统合规 grep 自检。
- `build.log` / `test.log`。

---

## 4. AC 覆盖（THEME_STUDIO_SPEC §6）

| AC | 结论 | 证据 |
|---|---|---|
| AC1 7 分区 + 左栏 + 右栏 + 应用/取消/恢复默认 | PASS | `SevenSections_AreInTheFrozenOrder_WithIconsAndSubtitles`、`SectionSwitch_KeepsTheDraft_AndDirtyMarkers`、`screens/studio-*-{dark,light}.png` |
| AC2 主题库：搜索/分类/筛选/收藏 + 卡片真实三视图 | PASS | `LibraryFilters_SearchCategoryAndAppearance`、`LibraryBreakpoints_AreFourThreeTwoColumns`、`screens/studio-library-{dark,light,highcontrast}.png`、`screens/library-{1280,1024}.png` |
| AC3 预览：三视图真实控件 + 明暗/高对比/密度/缩放 | PASS | `PreviewSwitches_ChangeModeAppearanceDensityAndZoom_WithScopedPalette`、`screens/studio-preview-{dark,light,highcontrast}.png`（三视图为真实控件树，非图片） |
| AC4 我的主题：已安装/收藏/自定义 + 应用/收藏/复制/导出/删除（内置不可删） | PASS | `FavoritesAndDelete_PersistAndProtectBuiltins`、`DuplicateTheme_CreatesIndependentUserCopy`、`screens/studio-mythemes-{dark,light}.png` |
| AC5 编辑 6 组 + 实时对比度 + 另存为 | PASS | `Editor_HasSixGroupsWithThirtyFiveSemanticColours_AndLiveRatios`、`ContrastAudit_UsesTheEngineFormula_AndFlagsFailures`、`screens/studio-editor-{dark,light,highcontrast}.png`、`screens/editor-dirty-dark.png` |
| AC6 外观立即生效（浅/深/系统 + 高对比 + 减少动效 + 跟随强调色） | PASS（含 GAP-3） | `AppearanceSettings_ApplyImmediately_AndPersist`、`screens/studio-appearance-{dark,light}.png`；「跟随系统强调色」受 GAP-3 限制（见 §6） |
| AC7 导入导出：逐条 issue、错误阻止、round-trip 等价 | PASS | `InvalidPackage_IsBlocked_WithPerItemIssues_AndCatalogUnchanged`、`ValidPackage_Imports_AndDuplicateIdRequiresOverwrite`、`ExportThenImport_RoundTripsToTheSameDocument`、`screens/import-failure-dark.png`、`screens/studio-importexport-{dark,light}.png` |
| AC8 恢复默认：二次确认、不删文件、重置后重启保持 | PASS | `ResetToDefault_RestoresSettings_AndKeepsUserThemeFilesUnlessAsked`、`ResetWithClearUserThemes_DeletesUserThemeFiles`、`screens/studio-reset-{dark,light}.png` |
| AC9 实时预览 + 取消完整回滚 + 画布像素不变 | PASS | `CancelPreview_RollsBackAppliedThemeAndPalette`（断言 `DesignSystemThemeManager.AppliedPaletteId` 与设置恢复）、`PreviewSession_DoesNotPersistUntilApply`（磁盘文档预览期不变）、`screens/rollback-{before,preview,after}.png` + `pixel-hash.json` |
| AC10 非法包 → issue + 回退默认不崩溃；旧 ID（9+2）迁移 | PASS | `InvalidPackage_IsBlocked_*`、`LegacyThemeIds_MigrateToDefault_WithVisibleNotice`（9 个 Theory 用例）、`UnknownOrEmptyThemeId_RecoversToDefault_WithoutCrashing`（未知/空 2 例） |
| AC11 键盘全可达、焦点可见、Esc 分级、无颜色单编码 | PASS | `EscLadder_DialogThenUnsavedThenClose`、`UnsavedDialog_ApplyAction_CommitsAndCloses`、`KeyboardRouting_EscCtrlEnterCtrlFAndArrows`、`StatusStates_AreTextEncoded_NotColourOnly`；焦点环由 DS Button/Input 内置 2px accent |
| AC12 证据：7 分区 × 暗/浅 + 高对比 + 导入失败 + 像素哈希 | PASS | `screens/`（24 帧）+ `screens.json` + `pixel-hash.json` |

### 4.1 真实服务（非 STUB）证据

- 截图与生产路径测试都使用 `ThemeEngineThemeStudioService.CreateProduction(Application, DesignSystemThemeManager, …)`：真实 `ThemeService` + `DesignSystemThemeLayerSink`；`screens/screens.json` 记录 `service` 与 `applied_palette_id`。
- `CancelPreview_RollsBackAppliedThemeAndPalette`：预览 fixture 时 `manager.AppliedPaletteId == fixture id`；`Cancel` 后回到 `newmanga-default`。
- `PreviewSession_DoesNotPersistUntilApply`：预览期间 `theme-settings.json` 字节不变；`ApplyAsync` 后磁盘含新主题 id；**新建 `ThemeSettingsStore` 重新 Load 得到同一 id**（重启保持）。
- `EditorDraft_Apply_PersistsAsUserTheme`：草稿应用后落为 `custom-*` 用户主题文件，设置文件同步更新。
- `AppearanceSettings_ApplyImmediately_AndPersist`：浅/深切换后从 `Application.Resources` 读到对应对照色，并持久化到设置文件。

---

## 5. STUB / NOT_WIRED / GAP 清单

| 编号 | 类型 | 内容 | 处置 |
|---|---|---|---|
| STUB-1 | 测试专用 | `StubThemeStudioService`（沙箱工厂）：真实引擎链路 + 临时目录 + `NullThemeLayerSink` + 确定性 fixture（只改字体/圆角/动效，不改颜色） | **生产 UI 不引用**；仅截图/单测。UI 在沙箱模式显示 `STUB` 徽标 + 「STUB 沙箱」来源标签 |
| NOT_WIRED-1 | 集成待接 | 文件选择器：`IThemeStudioFileGateway` 默认 `NullThemeStudioFileGateway`（`IsAvailable=false`） | UI 明示「文件选择器未接线（NOT_WIRED）：可拖入文件或粘贴 JSON」；导出仍生成 canonical `.nmtheme` 内容（`LastExportJson` 供 round-trip 断言），落盘待 INT-1 注入 `StorageProvider` |
| NOT_WIRED-2 | 集成待接 | `AppShellV2` / TopBand「主题」/ `Ctrl+,` / Console「外观」入口、`ShellState.SurfaceStack` 推入 | 归 `V11R-INT-1`（Lead）。入口已就绪：`ThemeStudioSurface.OpenAsync(section)` / `Close()` / `RequestClose` |
| NOT_WIRED-3 | 集成待接 | 应用启动时需把 **单一** `DesignSystemThemeManager` 传给 `CreateProduction` | `App._designSystemTheme` 目前是私有字段；INT-1 需暴露（或由 App 构造 Studio 服务），否则会出现两个 manager 竞争同一资源层 |
| GAP-3 | 引擎接口缺口（已报 Lead） | 冻结 `IThemeService` 没有 `SetFollowSystemAccentAsync`；`ThemeSettings.FollowSystemAccent` 无法经引擎持久化 | V1 该开关仅作用于本表面合成的作用域调色板（可见效果 = 使用应用级强调色基线），**不持久化**；UI 文案与右栏能力说明已标注「（仅作用域）」，待 Lead 裁定是否扩接口 |
| DEV-1 | 偏差（Lead 已批准） | 三视图未复用生产 `LibraryView` / `StudioWorkspaceView` | 生产视图依赖 `IHostController` + `ShellState` + notify/confirm 委托（且属 ui-shell 写域），作为预览宿主过重。改用**真实 Avalonia 控件树 + DS 令牌/Classes + 明示「示例内容」**，并以 `IPreviewSurfaceProvider` 预留替换 seam（INT-1 可注入生产视图） |
| DEV-2 | 偏差（记录） | 左栏宽度取 DS 令牌 `Nm.Size.TreeWidth`=200，而非规范文字 224px | 契约 §2.2 硬规则禁止裸间距；224 无对应令牌。右栏 320px 使用 `Nm.Size.InspectorExpanded`=320 ✓ |
| DEV-3 | 偏差（记录） | 动效三档映射 `fast(90/140/220) · normal(140/200/260) · slow(240/320/440)` | R-15 冻结令牌只有 Instant/Fast/Normal + `ThemeMotion.SlowMs` 默认 220；预设为 Studio 侧声明值，全部 ≤ `MaxDurationMs`(1000) |
| NOTE-1 | 说明 | 收藏（★）是 Theme Studio 自有 UI 状态，存 `%APPDATA%/NewManga/theme-studio-favorites.json`（schema `newmanga.theme-studio-favorites/1`） | 不进主题包 schema、不进引擎真值；文件损坏时按空集处理 |

---

## 6. 设计系统合规

- 生产 XAML/C# 中**无裸色值、裸字号、裸间距、裸圆角**；全部 `{DynamicResource Nm.*}` 或 `Auto`/`*`（见 `compliance.md` 自动 grep 结果）。
- 无阴影 / 渐变 / 模糊；圆角仅 `Nm.Corner.None/Sm/Md`（0/2/3px）。
- 无 emoji 图标：导航图标为 20×20、1.25px 描边的内联 `Geometry`；状态符号统一 `Nm.State.Symbol.*`（`● ◐ ✗ ▨ · – ▲`）。
- 状态非颜色单编码：卡片明暗徽标为文字；校验行为「级别 + 路径 + 说明 + 建议」；对比度同时显示数值与「通过/未通过」。
- 预览 / 编辑器草稿通过 `PaletteScope` 挂作用域 `ResourceDictionary`，不改应用级资源；应用级生效只经引擎 sink。

---

## 7. 复现命令

```powershell
# 1) 构建（0 warning / 0 error）
cd apps/desktop-avalonia
dotnet build NewManga.sln -warnaserror -t:Rebuild

# 2) 全量测试
dotnet test NewManga.sln --no-build

# 3) 仅 Theme Studio 测试（含截图；证据写入 verification/V11R-C-2）
$env:NEWMANGA_EVIDENCE_DIR = "G:\CODEX\New Manga.workspace\worktrees\V11R-THEME-STUDIO\verification\V11R-C-2"
dotnet test tests/NewManga.App.Tests/NewManga.App.Tests.csproj --no-build --filter "FullyQualifiedName~V2ThemeStudio"

# 4) 合规自检（重生成 compliance.md 的等价命令）
Get-ChildItem src/NewManga.App/Views/V2/ThemeStudio,src/NewManga.App/Shell/V2/ThemeStudio -Recurse -Include *.axaml |
  Select-String -Pattern '(Margin|Padding|Width|Height|Spacing|CornerRadius|FontSize)="[0-9]|#[0-9A-Fa-f]{3,8}|BoxShadow|Gradient|Blur'
```

截图渲染器：`Avalonia.Headless` + Skia（`UseHeadlessDrawing=false`）+ `Window.CaptureRenderedFrame()`；服务为真实引擎 + 真实 DS sink（非 STUB）。

---

## 8. 证据文件索引

| 文件 | 内容 |
|---|---|
| `build.log` | 全解决方案 Rebuild，0W/0E，`BUILD_EXIT=0` |
| `test.log` | 全量测试汇总，`TEST_EXIT=0` |
| `compliance.md` | 设计系统合规 grep 自检 |
| `screens/screens.json` | 24 帧元数据（SHA-256 / 主背景 / 64 格签名 / 渲染器） |
| `screens/pixel-hash.json` | 预览前/中/后固定像素画布哈希一致 |
| `screens/studio-{library,preview,mythemes,editor,appearance,importexport,reset}-{dark,light}.png` | 7 分区 × 暗/浅 |
| `screens/studio-{library,preview,editor}-highcontrast.png` | 高对比关键张 |
| `screens/import-failure-dark.png` | 非法包逐条 issue + 导入禁用 |
| `screens/editor-dirty-dark.png` | 编辑器未保存草稿 + 实时预览 + 脏标记 |
| `screens/rollback-{before,preview,after}.png` | 取消回滚前后帧 |
| `screens/library-{1280,1024}.png` | 响应式三/两列断点 |
