# NewManga.ThemeEngine（V11R-C-1）

新主题引擎。**取代**旧 `NewManga.Theme`（`ThemePack` 架构）；旧预设（Saber/Midnight/Sakura/Emerald/Mono/macOS…）不再提供，旧配置按退役计划迁移到内置默认主题。

## 1. 架构边界（Lead 裁定）

```
App ──消费──> NewManga.ThemeEngine ──依赖──> NewManga.DesignSystem
```

| 层 | 拥有 |
|---|---|
| `NewManga.DesignSystem`（main 已交付） | 令牌资源键（`Nm.*`）、样式、控件、应用资源字典机制（含 palette seam） |
| `NewManga.ThemeEngine`（本项目） | 主题包 schema / 注册表 / 校验 / 持久化 + 旧 ID 迁移 / 导入导出 / 预览会话 / 回退 / `ThemePackage → Nm.*` 主题层合成 |
| `App` | 只通过 `IThemeService` 等冻结接口消费；实现为 `ThemeService`（Part B） |

禁止：ThemeEngine 被 DesignSystem 引用；ThemeEngine 依赖 App；在主题包里出现布局/导航/密度字段（布局是 `LayoutProfile`，独立持久化）。

公开面严格对应 `doc/plan/V11R_AVALONIA_CONTRACT.md` §4（`ThemeKind`/`AppearanceMode`/`ContrastMode`/`ThemeDescriptor`/`ThemePackage`/`LayoutProfile`/`ThemeSettings`/`ThemeValidationIssue`/`ThemeValidationResult`/`ThemeApplyResult` 与 6 个接口）。
契约未定义的两个记录在此定稿（Lead 批准）：`ThemeTokenSet`（每变体：35 色 + 字体族/缩放/行高预设 + 圆角 + material/elevation + 动效）+ `ThemeMetadata`（engineVersion / generator / extra / 读取期 LoadWarnings，后者不序列化）。

## 2. Schema `newmanga.theme/1`

- 读写器 `ThemePackageJson`：**手写** `JsonDocument`/`Utf8JsonWriter`（无反射元数据，App 的 trim 路径安全）；输出确定（排序键、2 空格缩进、LF、结尾换行），同一 package 重复写字节一致。
- 未知字段：**容忍**，逐条 warning（`package.unknown-field`）；但字段名声明了被禁的视觉效果（shadow/gradient/blur/backdrop/filter/mica/acrylic/glass/glow）→ **error**（`package.forbidden-declaration`）。
- schema 版本：仅 `newmanga.theme/1`；其它值 → error（`package.schema-unsupported`）。
- 结构错误（坏 JSON、缺 `descriptor`/`light`/`dark` 等）→ 不产出 package（`ThemeReadResult.Package == null`），绝不半解析。
- 内置默认主题：`Themes/newmanga-default.nmtheme`（嵌入资源，生成产物）。样例全文见该文件；顶层结构：

```jsonc
{
  "schema": "newmanga.theme/1",
  "descriptor": { "id": "newmanga-default", "name": "New Manga Default", "version": "1.0.0", "kind": "builtin", "tags": [...], "supportsLight": true, "supportsDark": true },
  "light": { "colors": { "Nm.Color.Bg.Canvas": "#F4F3F0", ...35 }, "font": {...}, "corners": { "none": 0, "sm": 2, "md": 3 }, "material": "solid", "elevation": "none", "motion": { "fastMs": 90, "normalMs": 140 } },
  "dark":  { ... },
  "metadata": { "engineVersion": "1", "generator": "newmanga-theme-gen/1", "extra": {} }
}
```

## 3. 可复现生成（不手抄令牌值）

`Themes/../tools/NewManga.ThemeEngine.ThemeGen` 从冻结的 `doc/design/redesign-v1/40-fusion/tokens.json` 生成：

- `Themes/newmanga-default.nmtheme`（内置包；dark+light 两套 35 色，逐值来自 tokens.json）
- `Generated/ThemeTokenBaseline.g.cs`（字号基数 / 行高乘数 / 绝对行高层级；供 palette 合成缩放用户主题）

```pwsh
# 在 apps/desktop-avalonia 下
dotnet run --project src/NewManga.ThemeEngine/tools/NewManga.ThemeEngine.ThemeGen -- --check   # 可复现校验（CI 门）
dotnet run --project src/NewManga.ThemeEngine/tools/NewManga.ThemeEngine.ThemeGen             # 重新生成
```

`--check` 比较产物与 tokens.json 的字节（含 tokens.json SHA-256 指纹）；tokens.json 变化（如 R-09 令牌修订）后必须重跑生成器。生成文件目录含 `.gitattributes`（`*.nmtheme`、`Generated/*.g.cs` 固定 `eol=lf`）。

## 4. Palette（主题层）合成

`ThemePaletteComposer.Compose(package, PaletteVariant)` → `IReadOnlyDictionary<string, object?>`，**59** 个 `Nm.*` 键（R-15 白名单），可直接作为 Avalonia `ResourceDictionary` 值（白名单权威见 `doc/design/theming/THEME_ENGINE_LAYER.md`，与 DS `ThemeLayerRequiredKeys` 逐字一致）：

| 组 | 键 | 说明 |
|---|---|---|
| 颜色 | 35 × `Nm.Color.*` | 选定变体的完整色盘（不可变 brush，便于资源字典共享） |
| 字体族 | `Nm.FontFamily.Ui/Data/Display` | `FontFamily` |
| 字号 | `Nm.FontSize.Xs…Xxl` | 基数 × `ThemeTypography.Scale`（0.8–1.3） |
| 行高 | `Nm.LineHeight.Tight/Normal/Loose`（乘数）+ `Display/Title/Body/Label/Meta/Data`（绝对 px） | 绝对层 = 字号 × DESIGN_SYSTEM §3 层级比 × 预设比（Tight/1.25、Normal/1.45、Loose/1.6 相对 Normal 的比值） |
| 圆角 | `Nm.Corner.None/Sm/Md` | `CornerRadius`；硬规则 ≤3px |
| 动效 | `Nm.Motion.Duration.Fast/Normal/Slow`（R-15，默认 90/140/220ms；`Instant` 是 DS 全局不变量，不在主题层） | `TimeSpan` |

`ComposeColorLayer` 只含 35 色（供 DS 颜色 seam / 校验 / 预览快照）。
`material`/`elevation` 是被校验的**声明**，但冻结令牌词汇里没有对应 `Nm.*` 键——本引擎不发明第二套令牌，故不进生成层（高对比模式与层级表达由 DS 五级明度 + `line.*` 承担）。\n**主题不变量派生色**（`Nm.Color.Scrim`，Modal 遮罩）属于 DS 全局令牌字典，**不参与主题包校验、也不属于 59 键白名单**（R-21）；主题包声明它会得到 warning 并被忽略。
布局/密度/间距/尺寸/图标/状态符号**不在**主题层（属 DS 或布局设置）。

## 5. 校验（`IThemeValidator`）

`error` 使 package 无效（阻止安装/导入），`warning` 允许继续：

| 规则 | 结果码 |
|---|---|
| schema / engineVersion | `package.schema-unsupported`（error/warning）、`metadata.engine-version`（warning） |
| 描述符 id slug / name / 至少一种外观 / tags | `descriptor.*` |
| 35 色必填键缺失 | `colors.missing-key`（error） |
| 未知色键 / 非法色值 | `colors.unknown-key`（warning）/ `colors.invalid-value`（error） |
| 圆角 <0 或 >3px | `corners.radius-out-of-range`（error，DESIGN_SYSTEM §1 rule 4） |
| 字体族为空/仅 CSS 通用族/带字体文件路径；字号缩放越界 | `typography.font-family-invalid` / `typography.font-scale-out-of-range`（error） |
| 动效时长越界 / 三档无序（fast≤normal≤slow） | `motion.duration-out-of-range`（error）/ `motion.duration-order`（warning） |\n| 主题不变量派生色（Scrim）被声明 | `colors.unknown-key`（warning，忽略；R-21） |
| WCAG 2.1 对比度 | `contrast.*`，见下 |
| 读取期诊断（未知字段、被禁声明、重复字段） | 折入校验结果 |

**对比度判定依据**（Lead 对 V11R-C-1 的裁决，R-09 修订后）：

- 正文 `Text.Primary` 对 `Bg.Panel`/`Bg.Canvas` ≥ **7:1** → error；
- 次要 `Text.Secondary` 同上 ≥ **4.5:1** → error；
- 状态 7 色对 `Bg.Panel` ≥ **4.5:1** → error（状态组件所在表面为规范表面）；
- 状态色对 `Bg.Raised`/`Bg.Canvas` 不达标 → **warning**（同一变体同一表面聚合成 1 条）：R-09 基线只保证 panel 门槛，raised/canvas 是次要/边缘表面，属已知特征化缺口；
- `Accent.On` 对 `Accent.Base` ≥ 4.5:1、`Accent.Base` 对 `Bg.Panel` ≥ 3:1（焦点环非文本门槛）→ error。

## 6. 注册表 / 持久化 / 迁移

- 内置：`newmanga-default`（嵌入资源，id 保留，不可覆盖/卸载）。
- 用户主题：`%APPDATA%/NewManga/themes/{id}.nmtheme`（也扫描 `*.json`；同名时 `.nmtheme` 优先）。安装 = 校验通过后**规范化**写盘（kind 归一为 `user`、未知字段丢弃）；损坏/非法文件被隔离进 `ThemeRegistry.Diagnostics`，不进入 `All`、不影响启动。
- 设置：`%APPDATA%/NewManga/theme-settings.json`（`newmanga.theme-settings/1`）；损坏/缺省回退出厂设置，不抛异常、不阻塞启动；读写含旧键名 `theme`/`variant` 别名。
- 旧 ID 迁移（退役计划 §2.1，全部覆盖）：`saber-purple→Dark`、`saber-light→Light`、`midnight→Dark`、`sakura→Light`、`emerald→Dark`、`mono→Dark`；`macos-sonoma/split` 保留配置的外观；`macos-launchpad` 额外 `Density.Compact`；未知 id → 默认主题 + Dark + warning；空值 → 默认主题（外观沿用配置）。

## 7. 预览会话（`IThemePreviewEngine`）

纯逻辑状态机：`Begin()` 捕获 baseline → `Update(themeId)`（未知 id 抛 `ThemePreviewException`）→ `Commit()`（引擎 `CurrentSettings` 前移到会话主题，幂等）/ `Cancel()`（回到 baseline，幂等）。事件 `Changed` 携带 `Began/Updated/Committed/Cancelled` 与 settings/descriptor。预览**不写持久化**：Studio「应用」= `Commit()` + `IThemeService.ApplyAsync`（THEME_STUDIO_SPEC §4）。

## 8. Part B 服务（`ThemeService` + `IThemeLayerSink`）

- `ThemeService : IThemeService`：`InitializeAsync`（注册表刷新 → 设置读取 → 旧 ID 迁移 → 应用 → 必要时回存）/
  `ApplyAsync` / `SetAppearanceAsync` / `SetContrastAsync` / `SetLayoutAsync` / `SetReducedMotionAsync` /
  `ResetToDefaultAsync` + `Changed`；`LastError`/`LastIssues`/`IsInitialized`/`PreviewEngine` 供 App/Studio 诊断。
- 内部持有 `ThemePreviewEngine` 并把预览事件同步到应用层：`Update` 即时应用会话主题层，`Cancel` 回滚到已应用层；
  预览不写持久化。
- **回退策略**：未知 id / 包损坏 / 校验不通过 / 层应用失败 → 逐级回退 `newmanga-default` → DS 内建
  `RevertToBuiltInLayer()`；全程不抛异常（启动路径）、不半应用；失败写入 `LastError` + `LastIssues`。
- 对比度 warning **不阻塞**应用（`IsValid` 只由 error 决定）；Studio 应把 warning 呈现为“可选改进”，
  error 才阻止导入/应用。
- `IThemeLayerSink` 是 Avalonia-free 的应用面 seam（`ApplyThemeLayer/RevertToBuiltInLayer/SetAppearance/
  SetContrast/SetReducedMotion/PlatformIsLight/LastError`），单测用 fake 注入。等 DS `ApplyThemeLayer`
  合入后，适配器仅需把合成的 `IReadOnlyDictionary<string, object?>` 转成 `ResourceDictionary` 并委托
  `DesignSystemThemeManager`（3 行级改动）。

## 9. 测试与证据

`tests/NewManga.ThemeEngine.Tests`（xUnit）：schema 往返/未知字段/禁用声明、校验 20+ 错误分支、迁移 13 例、注册表安装/卸载/导出/隔离、预览状态机 17 例、palette 语义等价（与 DS 生成盘逐色一致）、生成器可复现与 `--check`、Part B 服务状态机/回退/持久化/预览接线（`ThemeServiceTests`）。
证据目录：`verification/V11R-C-1/`。
