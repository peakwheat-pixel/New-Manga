# V11R-D-1 证据：Design System (Avalonia)

Owner: `design-platform`。分支 `v11r/design-platform`，worktree
`G:/CODEX/New Manga.workspace/worktrees/V11R-DESIGN-PLATFORM`，基线 `c73239999`。
本目录证据由**真实执行**产生；未执行项明确标注 `NOT_RUN`，不伪造。

> 当前状态：M0 已过 Gate；AC1–AC10 与 R-09/R-14/R-15 处置、Codex 独立审查 P1/P2 返修已完成。
> 最终 SHA 以 Handoff 消息为准（本文件与代码同一次提交）。

## 执行结果（工作目录 `apps/desktop-avalonia`）

| 项 | 命令 | 结果 | 证据 |
|---|---|---|---|
| 构建 | `dotnet build NewManga.sln -warnaserror` | PASS（0 warning / 0 error） | `build.log` |
| 全量测试 | `dotnet test NewManga.sln --no-build` | PASS：DS 64 / App 137 / Host 39pass·21skip / CoreClient 39pass·22skip，0 fail | `test.log` |
| token 重建（写入） | `dotnet run --project src/NewManga.DesignSystem/tools/NewManga.DesignSystem.TokenGen` | PASS，写入 10 个生成产物（277 行令牌） | `token-generator-write.log` |
| token 一致性（校验） | `... TokenGen -- --check` | PASS：`up to date: every generated artifact matches the frozen token source byte-for-byte` | `token-generator-check.log` |
| 视觉证据 | `NM_DS_EVIDENCE_DIR=verification/V11R-D-1/screenshots dotnet test ... --filter VisualEvidence` | PASS 2：gallery dark/light/HC + 键盘焦点环 dark/light | `screenshot-run.log`、`screenshots/` |

## 交付内容

- 新项目 `apps/desktop-avalonia/src/NewManga.DesignSystem/`（net9.0，Avalonia 11.3.22），已加入 `NewManga.sln`。
- 可复现生成器 `tools/NewManga.DesignSystem.TokenGen`：`tokens.json` → 10 个产物（dark 35 / light 35 /
  high-contrast 35 / global 92 / density ×2 / motion / `NmKeys.g.cs` / `StatusCatalog.g.cs` /
  `TokenMap.md`）；LF + ordinal 排序 + 无时间戳，`--check` 逐字节校验；生成期内置 R-14/R-15 派生规则断言
  （行高别名 ∈ {1.25,1.45,1.6}、密度 Compact<Comfortable<Spacious、高对比文本 ≥7:1/状态 ≥4.5:1、em 跟踪值
  必须为比率、`Xxl` 命名）。
- 主题管理 `NewManga.DesignSystem.Theming.DesignSystemThemeManager`：
  - 只替换 `Application.Resources.MergedDictionaries`，不重建窗口（AC7）；加载/校验失败保持原状并记录
    `LastError`（AC9）；**先校验后原子替换**（P2-5）。
  - `Initialize(AppearanceMode?)` 接受宿主传入的启动外观（`App` 从 `--variant` 读取），未提供时才用
    Dark 默认（P1-2）。
  - Theme Engine seam（契约 §4.1 / R-15）：`ApplyThemeLayer(ResourceDictionary, themeId)` 白名单 59 键
    （颜色 35 + 字体族 3 + 字号 6 + 行高 9 + 圆角 3 + 动效 3），白名单外键**忽略并记入
    `ThemeLayerIssues`**；`ApplyPalette` 是仅颜色子集的便捷入口（非颜色键从当前主题令牌继承）；
    `AppliedPaletteId` / `AppliedThemeLayerId` 暴露；`RevertPalette()` 恢复内置；material/elevation
    不接受。
- 标准控件（AC4）：Button（4 变体 × 2 尺寸 + icon）、TextBox（search/mono/invalid）、TextBlock 6 层级、
  Border 5 级表面、ComboBox（compact）、CheckBox、RadioButton、ToggleSwitch、TabControl/TabItem、
  ScrollViewer/ScrollBar、ProgressBar、Separator、MenuFlyout/ContextMenu、ToolTip。全部走
  `DynamicResource Nm.*`，无裸色值/字号/间距/阴影/渐变/模糊，圆角 ≤3px。
- 自定义控件（AC5）：`StatusGlyph`、`StatusBadge`、`Chip`、`Kbd`、`SegmentedControl`、`SearchField`、
  `EmptyState`、`AlertBanner`、`CountChips`、`Drawer`、`Modal`、`TopBand`（基础版）+ `NmIcon`（27 线性图标）。
- 断点语义（R-18）：`Nm.Size.Breakpoint.Full(1600)/Compact(1280)/Narrow(1024)` 作为两个 UI 工作面唯一共享断点，禁止各自造 1400/1200 等本地常量。
- 状态语言（AC6）：9 状态（7 冻结 + 未开始 + 锁定）色相/符号/文字三编码，符号常量由 `StatusCatalog` 生成，
  UI 不得自造。
- 焦点与无障碍（AC8）：2px accent **外侧 outline**（`FocusRing` 附加行为，overlay 层承载，不改变控件几何，
  不用阴影）；`Focus` 显示/失焦移除；reduced-motion 覆盖 DS 动效令牌；DESIGN_SYSTEM §2.3 对比度由测试与
  生成器断言。
- 接线：`NewManga.App.csproj` 引 DesignSystem；`App.axaml` 资源 + 样式；`App.axaml.cs` 在旧主题包之后初始化
  主题管理器并传入启动外观。

## AC 对照

| AC | 状态 | 证据 |
|---|---|---|
| AC1 可复现 token 生成 | PASS | `token-generator-check.log`；`TokenPipelineTests` |
| AC2 编译 0 warning | PASS | `build.log` |
| AC3 `Nm.*` 键 + C# 常量 | PASS | `Generated/NmKeys.g.cs`；`R14ContractTests`、字典键双向差集 |
| AC4 标准控件 | PASS | `StandardControlsThemeTests`、`ButtonThemeTests` |
| AC5 自定义控件 | PASS | `CustomControlsTests`（含 Skeleton 三形态、41 图标覆盖） |
| AC6 状态三编码 | PASS | `StatusCatalog.g.cs`、`CustomControlsTests`；R-18 断点由 `Breakpoint_tokens_are_the_single_shared_layout_scale` 校验 |
| AC7 主题/密度/高对比实时切换 | PASS | `ThemeManagerTests`、`screenshots/gallery-*` |
| AC8 焦点/高对比/reduced-motion | PASS | 焦点环截图 `focus-ring-*.png`；`ContrastTokenTests`；`VisualEvidenceTests` |
| AC9 失败回退 | PASS | `ThemeManagerTests`（坏字典切换/坏源回退，原子性） |
| AC10 证据 | PASS | 本目录全部日志 + 5 张截图 + `DEVIATIONS.md` |

## 审查处置（Codex r1）

P1/P2 逐条处置与证据路径见 `REVIEW-R1-DISPOSITION.md`；两处 P1（Primary 按钮文字对比度、初始化默认 Dark
覆盖用户选择）已修复并有渲染后断言；P2 全部处置（部分登记为偏差）。

## 未执行 / NOT_RUN

- Windows 实机启动、键盘/IME/屏幕阅读器人工验证：`NOT_RUN`（headless 渲染 + 单测覆盖）。
- Trim / AOT / single-file 发布：`NOT_RUN`（DS 未引入 trim 特性；发布路径不在本 Task 范围）。
- 真实桌面 DPI/多屏缩放视觉核验：`NOT_RUN`。
- 旧壳 `MainWindow` 在 DS 全局样式下的兼容性回归：过渡期接受，见 `DEVIATIONS.md`。

偏差与冻结基线缺口见 `DEVIATIONS.md`。



