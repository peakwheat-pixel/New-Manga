# Theme Engine 消费指南（Theme Studio / UI 集成）

面向 `V11R-C-2` Theme Studio（以及任何 UI 消费方）。API 契约见
`doc/plan/V11R_AVALONIA_CONTRACT.md` §4；主题层白名单见
`doc/design/theming/THEME_ENGINE_LAYER.md`。本指南只描述**真实实现**（`NewManga.ThemeEngine` 程序集），
不含 stub 行为。

## 1. 依赖与构造

Theme Studio 不自行 new 引擎对象，由 App/宿主注入；但了解构造链有助于测试与诊断：

```csharp
// 1) 设计系统单例（App 持有；ThemeEngine 不拥有它）
var manager = new DesignSystemThemeManager(Application.Current!);
manager.Initialize();                       // 加载 global tokens + 当前外观盘

// 2) 引擎对象（App 组装一次）
var registry = new ThemeRegistry();         // 内置 newmanga-default + %APPDATA%/NewManga/themes/*.{nmtheme,json}
var persistence = new ThemeSettingsStore(registry: registry); // %APPDATA%/NewManga/theme-settings.json
var sink = new DesignSystemThemeLayerSink(Application.Current!, manager); // 真实 Avalonia 适配器
var themeService = new ThemeService(registry, persistence, sink);         // IThemeService
await themeService.InitializeAsync();       // 读设置/迁移旧 ID/应用主题；主题问题不抛异常
```

Studio 通常只需要注入 `IThemeService` + `IThemeRegistry`（+ 需要时 `IThemeValidator` / `IThemePreviewEngine`）：

```csharp
public ThemeStudioViewModel(IThemeService themeService, IThemeRegistry registry)
{
    _themeService = themeService;
    _registry = registry;
}
```

约束：

- `IThemeService.PreviewEngine`（返回具体类型 `ThemePreviewEngine`，实现 `IThemePreviewEngine`）与
  `IThemeService` **必须是同一个服务实例**；Studio 不要自己 new `ThemePreviewEngine`，否则预览的应用/回滚
  不与服务状态一致。
- 所有调用在 **UI 线程**（Avalonia Dispatcher）；`Changed` 同步在调用线程触发。

## 2. `IThemeService` 用法

| 成员 | 行为 | 失败语义 |
|---|---|---|
| `ThemeDescriptor Current` | 已应用主题的 descriptor（catalog 为空时返回内置默认的合成 descriptor，绝不为 null） | — |
| `ThemeSettings Settings` | 已应用设置快照（ThemeId/Appearance/Contrast/Layout/ReducedMotion/FollowSystemAccent） | — |
| `event EventHandler? Changed` | 主题/外观/对比度/布局/减弱动效**成功应用并持久化后**触发；预览更新与失败不触发 | — |
| `Task InitializeAsync(ct)` | 注册表刷新 → 读取设置 → 旧 ID 迁移 → 应用外观/对比度/动效 → 应用主题层 → 必要时回存；幂等 | **不抛**（启动路径），问题进 `LastError`/`LastIssues` |
| `Task<ThemeApplyResult> ApplyAsync(themeId, ct)` | 解析+校验+合成+应用；成功后持久化并触发 `Changed` | 未知 id/损坏包/校验 error/层应用失败 → 回退 `newmanga-default`（`Success=true, Recovered=true`，issues 说明）；连默认层与 DS 内建层都失败 → `Success=false`，Settings 不变，`LastError` 有值 |
| `Task SetAppearanceAsync(mode)` | 切浅/深/系统并重算当前主题层；System 跟随平台 | sink 失败 → 保持原设置 + `LastError`；层应用失败 → 回滚外观与旧层 |
| `Task SetContrastAsync(mode)` | 委托 DS 高对比覆盖层 | 失败保持原设置 + `LastError` |
| `Task SetLayoutAsync(LayoutProfile)` | 仅持久化布局（V1 仅 `Navigation=TopBand` 生效，其余枚举保留）；不换主题层 | null → `ArgumentNullException` |
| `Task SetReducedMotionAsync(bool)` | 委托 DS reduced-motion 覆盖层 | 失败保持原设置 + `LastError` |
| `Task ResetToDefaultAsync()` | 重置主题/外观/对比度/布局/动效到出厂默认并应用 | 主题层失败时仍重置设置并记录 `LastError` |
| `LastError` / `LastIssues`（concrete `ThemeService`） | 最近一次可恢复错误/结构化 issue，供状态条与“为什么变成默认主题”提示 | — |

`ThemeApplyResult`：`Success`（是否已应用）、`AppliedThemeId`、`Issues`（含 **warning**，例如默认主题的
3 条“边缘表面状态对比度”提示）、`Recovered`（是否回退过）。**warning 不阻塞应用**：Studio 把 warning
显示为“可选改进”，只有 `error` 才阻止导入/应用。

`ThemeValidationResult`：`IsValid` 只由 error 决定；`Errors`/`Warnings` 分开列出。Studio 校验面板直接
渲染 `Issues`（每条含 `Code`/`Severity`/`Message`/`Path`，`Severity` 为 `"error"`/`"warning"`）。

## 3. 预览 → 应用推荐流程（Theme Studio §4）

```csharp
// 进入 Theme Studio（表面栈压入时）
var session = _themeService.PreviewEngine.Begin();   // 捕获当前 Settings 为回滚基线；同一时刻仅一个会话
// 用户点选主题卡片 / 编辑器实时改动：
session.Update(themeId);                             // 只换资源层，不写盘、不改 Settings；未知 id 抛 ThemePreviewException
// ...
// 应用：
session.Commit();                                    // 会话提交（不写盘）
var result = await _themeService.ApplyAsync(themeId);// 真正应用 + 持久化 + Changed
session.Dispose();
if (!result.Success) { /* 保持会话？服务已尝试默认回退；显示 LastError/issues，允许重试/取消 */ }

// 取消 / 关闭：
session.Cancel();                                    // 服务重放已应用主题层（完整回滚）
session.Dispose();
```

规则（已由单测固定）：

- `Begin()` 时若已有活动会话，旧会话自动 `Cancel()`（回滚）后开新会话。
- `Update` 只在 Active 状态可用；`Commit`/`Cancel` 幂等；`Commit` 后再 `Cancel` 不会回滚。
- `Dispose` 未提交会话 = `Cancel`。
- 服务在会话未提交时被 `ApplyAsync` 会被取消（自愈）而不是抛异常。
- **预览不写持久化**；只有 `ApplyAsync` 落盘。预览期间 `IThemeService.Settings` 不变。
- 预览工具栏的“明暗/高对比模拟”属于 Studio 自身的预览渲染（可用
  `ThemePaletteComposer.Compose(package, PaletteVariant.Light/Dark)` 取快照），不要调用
  `SetAppearanceAsync`——那会改真实设置。

## 4. 主题库 / 我的主题 / 导入导出

```csharp
// 列表（内置在前，用户主题按 id 排序）
IReadOnlyList<ThemeDescriptor> all = _registry.All;

// 加载完整包（校验/预览/编辑器读取）
ThemePackage package = _registry.Load(themeId);
ThemeValidationResult validation = ThemeValidator.Default.Validate(package);

// 编辑器实时对比度（WCAG 2.1；返回 1–21 的比例）
double ratio = ThemeContrast.Ratio("#E9EAEC", "#1A1C1F");

// 导入：任意 .nmtheme/.json 流；校验通过才落盘（规范化 kind=user、未知字段丢弃）
ThemeValidationResult install = await _registry.InstallAsync(stream);
if (!install.IsValid) ShowIssues(install.Errors);

// 导出：规范化 JSON（可直接写 .nmtheme）；round-trip 与安装/导出等价
string json = await _registry.ExportAsync(themeId);

// 删除（内置 id 恒 false；用户主题删除文件）
bool removed = await _registry.UninstallAsync(themeId);

// 外部文件变化后刷新目录（损坏文件被隔离进 Diagnostics，不进入 All、不抛）
await _registry.RefreshAsync();
IReadOnlyList<ThemeValidationIssue> diagnostics = ((ThemeRegistry)_registry).Diagnostics;
```

主题编辑器“从当前主题另存为”：

```csharp
var current = _registry.Load(_themeService.Settings.ThemeId);
var draft = current with
{
    Descriptor = current.Descriptor with { Id = newId, Name = name, Kind = ThemeKind.User, Author = author },
    // Colors / Typography / Corners / Material / Elevation / Motion 按编辑值替换（保留 35 色完整性）
};
ThemeValidationResult check = ThemeValidator.Default.Validate(draft);
if (check.IsValid) await _registry.InstallAsync(new MemoryStream(Encoding.UTF8.GetBytes(ThemePackageJson.Write(draft))));
```

## 5. 旧 ID 迁移入口

- 持久化层已自动迁移：`ThemeSettingsStore.Load()` 内部走 `LegacyThemeMigration`（退役计划 §2.1 的
  9 个旧 id + 未知 + 空 → `newmanga-default`，保留外观/launchpad→Compact；未知 id 在注入注册表时回退
  Dark + warning）。Studio 只需读 `IThemeService.Settings`，无需自己映射。
- 需要显式映射（例如 `--theme-id` 兼容）时使用公开 API：
  `LegacyThemeMigration.Mappings`（旧 id → `LegacyThemeMapping`）与
  `LegacyThemeMigration.Migrate(settings, isKnownTheme)`。
- 恢复默认：`ResetToDefaultAsync()` 不删除用户主题文件（只重置选择）；“同时清除我的主题”由 UI 逐项
  `UninstallAsync` 并二次确认。

## 6. 线程/Dispatcher 要求与错误呈现

- 所有服务/注册表调用在 UI 线程；`InitializeAsync/ApplyAsync` 内部文件 IO 很小，但持久化走异步写
  （原子替换），不要把 UI 线程锁死在大文件上（主题包上限 1 MiB）。
- `Changed` 同步触发；不要在里面做重活。
- 错误一律“就地 + 可重试”，不整页跳转：显示 `LastError`/`Issues`（含 Path），并明确当前是否仍在
  使用默认主题。
- 对比度/主题层的 warning 文案按“可选改进”呈现，不得显示为错误（默认主题自带 3 条边缘表面 warning）。
