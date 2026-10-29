# V11R-D-1 证据：Design System (Avalonia)

Owner: `design-platform`。分支 `v11r/design-platform`，worktree
`G:/CODEX/New Manga.workspace/worktrees/V11R-DESIGN-PLATFORM`，基线 `c73239999`。
本目录证据由**真实执行**产生；未执行项明确标注 `NOT_RUN`。

## M0 里程碑（已完成）

M0 定义（Lead）：项目可编译 + token 管线 + 双主题字典 + 基础控件样式 + sln/App.csproj/App.axaml 接线 +
至少 3 个单测；`dotnet build NewManga.sln -warnaserror` 0 warning 0 error；`dotnet test` 绿。

| 项 | 命令（工作目录 `apps/desktop-avalonia`） | 结果 | 证据 |
|---|---|---|---|
| 构建 | `dotnet build NewManga.sln -warnaserror` | PASS（0 warning / 0 error） | `build.log` |
| 全量测试 | `dotnet test NewManga.sln --no-build` | PASS：DS 24 / App 137 / Host 39pass·21skip / CoreClient 39pass·22skip | `test.log` |
| token 重建（写入） | `dotnet run --project src/NewManga.DesignSystem/tools/NewManga.DesignSystem.TokenGen` | PASS，写入 9 个产物 | `token-generator-write.log` |
| token 重建一致性（校验） | `dotnet run --project src/NewManga.DesignSystem/tools/NewManga.DesignSystem.TokenGen -- --check` | PASS：`up to date: every generated artifact matches the frozen token source byte-for-byte` | `token-generator-check.log` |

M0 交付内容：

- 新项目 `apps/desktop-avalonia/src/NewManga.DesignSystem/`（net9.0，Avalonia 11.3.22，命名空间
  `NewManga.DesignSystem`，控件命名空间 `NewManga.DesignSystem.Controls`），已加入 `NewManga.sln`。
- 可复现生成器 `tools/NewManga.DesignSystem.TokenGen`：`doc/design/redesign-v1/40-fusion/tokens.json`
  → Avalonia `ResourceDictionary`（dark 35 / light 35 / global 71 全量键）+ C# 键常量 `NmKeys` +
  键映射表 `Generated/TokenMap.md`；LF 换行 + ordinal 排序 + 无时间戳，`--check` 逐字节校验。
- 双主题字典 `Themes/Tokens.Dark.axaml`、`Themes/Tokens.Light.axaml`；全局字典
  `Themes/Tokens.Global.axaml`；聚合入口 `Themes/NewMangaTheme.axaml`。
- 主题管理 `NewManga.DesignSystem.Theming.DesignSystemThemeManager`：只替换
  `Application.Resources.MergedDictionaries` 中的字典，不重建窗口；加载失败记录 `LastError` 并保持旧状态。
- 基础控件样式：Button（primary/secondary/ghost/danger × md/sm + icon，2px accent 焦点环）、
  TextBox（search/mono/invalid）、TextBlock（display/title/body/label/meta/data + muted/num）、
  Border（card/panel/raised/overlay/sunken/hairline）、Window 字体/画布。
- 接线：`NewManga.App.csproj` 引 DesignSystem；`App.axaml` 合并资源 + 样式；`App.axaml.cs` 启动时
  初始化主题管理器（在旧主题包应用之后，保证新 token 优先）。
- 单测 `tests/NewManga.DesignSystem.Tests`：24 个（token 映射完整性/可复现性/字典类型/主题切换
  动态刷新/对比度/回退/按钮样式与焦点环）。

## 进行中（AC4 余量 / AC5–AC10）

- AC4 其余控件：ComboBox / CheckBox / RadioButton / ToggleSwitch / TabControl / ScrollViewer+ScrollBar /
  ProgressBar / Separator / MenuFlyout / ContextMenu / ToolTip。
- AC5 自定义控件 M0 集：StatusGlyph / StatusBadge / Chip / Kbd / SegmentedControl / SearchField /
  EmptyState / AlertBanner / CountChips / Drawer / Modal / TopBand。
- AC6 状态七态三编码、AC8 焦点环/高对比/reduced-motion 的视觉证据、AC10 双主题截图。

偏差与冻结基线缺口见 `DEVIATIONS.md`。
