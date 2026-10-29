# V11R 旧主题系统退役计划（C4 前置依赖图 + 替换清单）

状态：`PREPARED`（2026-10-30，DSH）。执行任务：`V11R-C-3`（高风险，必须独立审查）。
原则：**先建新、后迁移、再删除**；新系统具备等效能力且迁移/回滚测试通过前，不得删除仍被生产页面引用的资源。

---

## 1. 旧系统范围（已核实）

### 1.1 代码资产

| 资产 | 位置 | 规模 |
|---|---|---|
| 旧主题实现 | `apps/desktop-avalonia/src/NewManga.Theme/ThemePack.cs` | 34 KB / 1 文件 / 64 处符号 |
| 旧主题项目 | `apps/desktop-avalonia/src/NewManga.Theme/NewManga.Theme.csproj` | 被 `NewManga.App.csproj` 引用 |
| 旧主题测试 | `tests/NewManga.App.Tests/{ThemeMacosTests(88),ThemeLayoutsTests(96),ThemeMacosAuditTests(9),S3ShellTests(20),S4ReaderWorkbenchTests(1)}.cs` | 5 文件 / 214 处符号 |

### 1.2 公开符号（删除对象）

`MotionProfile`、`ThemePackMetrics`、`LayoutKind`、`NavPlacement`、`ShelfStyle`、`SettingsStyle`、`LayoutProfile`、`LayoutProfiles`、`ThemePack`、`ThemePacks`（含 `SaberPurple/SaberLight/Midnight/Sakura/Emerald/Mono/MacOsSonoma/MacOsLaunchpad/MacOsSplit/Default/ById/IsMacOsPack`）、`ThemePackService`（`Apply/ApplyVariant/ApplyDefault/Brush/ColorOf`）。

### 1.3 引用方（按引用密度）

| 引用方 | 引用数 | 说明 |
|---|---|---|
| `src/NewManga.App/Views/Pages.cs` | 108 | 旧书架/设置/主题中心（将随旧壳退役） |
| `tests/NewManga.App.Tests/ThemeLayoutsTests.cs` | 96 | 旧布局测试（退役） |
| `tests/NewManga.App.Tests/ThemeMacosTests.cs` | 88 | 旧 macOS 主题测试（退役） |
| `src/NewManga.App/Views/MainWindow.axaml.cs` | 29 | 窗口级主题应用/标题栏 |
| `tests/NewManga.App.Tests/S3ShellTests.cs` | 20 | 旧壳测试（需迁移断言到新 DS/Theme） |
| `src/NewManga.App/Views/ReaderWorkbenchPages.cs` | 13 | 旧工作台（将随旧壳退役） |
| `src/NewManga.App/Views/ProfileSections.cs` | 7 | 旧设置分区 |
| `src/NewManga.App/Views/ImportExportPanels.cs` | 4 | 旧导入导出面板 |
| `src/NewManga.App/Views/CredentialSection.cs` | 4 | 旧凭据区 |
| `src/NewManga.App/App.axaml.cs` | 3 | 启动应用主题 |
| `src/NewManga.App/ViewModels/MainViewModels.cs` | 2 | 主题选择模型 |
| `src/NewManga.App/AppOptions.cs` | 1 | `--theme/--variant` 证据钩子 |
| `tests/.../ThemeMacosAuditTests.cs` | 9 | 旧审计测试 |
| Host/CoreClient | 3 处单点 | 仅在注释/无关字符串中出现，需逐项确认非真实依赖 |

---

## 2. 旧 → 新 替换映射

| 旧概念 | 新概念（`NewManga.ThemeEngine`） | 迁移规则 |
|---|---|---|
| `ThemePack`（颜色+材质+布局+圆角+动效混合） | `ThemePackage`（仅性格：颜色/字体/圆角/材质/阴影/动效） | 不复用；新内置主题从 `tokens.json` 生成 |
| `ThemePackService.Apply(Application, pack)` | `IThemeService.ApplyAsync(themeId)` | 资源字典整体替换；失败回退默认 |
| `ThemePackService.ApplyVariant` | `IThemeService.SetAppearanceAsync(Light/Dark/System)` | 外观与主题解耦 |
| `LayoutKind`/`NavPlacement`/`ShelfStyle`/`SettingsStyle`（在主题包里） | `LayoutProfile`（独立持久化：Navigation/Shelf/Density/Workbench/Reader） | 从主题包剥离；V1 仅实现 `Navigation=TopBand`，其余枚举保留 |
| `ThemePackMetrics`（圆角/阴影） | 令牌 `Nm.Corner.*`、`Nm.Shadow.*` | 进主题包的 radius/shadow 段 |
| `MotionProfile` | `IThemeService.SetReducedMotionAsync` + `Nm.Motion.*` | 动效全局可关 |
| `ThemePacks.Default`（SaberPurple） | 新默认主题 `newmanga-default` | 见 §3 |
| `ById(id)`（宽松返回 Default） | `IThemeRegistry.Find(id)` + 未知 ID 回退 | 需显式 issue 记录 |

### 2.1 旧主题 ID → 新主题/外观 迁移表（必须全部覆盖，缺一不可）

| 旧 ID | 旧名称 | 新主题 | 新外观 | 备注 |
|---|---|---|---|---|
| `saber-purple` | Saber Purple | `newmanga-default` | `Dark` | 旧默认 → 新默认 |
| `saber-light` | Saber Light | `newmanga-default` | `Light` | 明暗随包迁移 |
| `midnight` | Midnight | `newmanga-default` | `Dark` | 旧预设不再提供 |
| `sakura` | Sakura | `newmanga-default` | `Light` | 同上 |
| `emerald` | Emerald | `newmanga-default` | `Dark` | 同上 |
| `mono` | Mono | `newmanga-default` | `Dark` | 同上 |
| `macos-sonoma` | macOS Sonoma | `newmanga-default` | 保留旧变体 | 旧布局枚举不迁移（V1 仅 TopBand） |
| `macos-launchpad` | macOS Launchpad | `newmanga-default` | 保留旧变体 | 书架密度可迁移到 `Density=Compact` |
| `macos-split` | macOS Split | `newmanga-default` | 保留旧变体 | 用户可后续在 Theme Studio 选布局（V1 仅 TopBand 生效） |
| 未知/损坏 ID | — | `newmanga-default` | `Dark` | 不抛异常、不阻塞启动，写一条 migration issue |
| 空/缺失 | — | `newmanga-default` | `System` | 首次启动默认 |

---

## 3. 新默认主题要求（`newmanga-default`）

- 直接由 `doc/design/redesign-v1/40-fusion/tokens.json` 的 dark/light 两套生成，键名 `Nm.*`，不得手抄值。
- 必须覆盖契约 §2.2 全部组；缺失键在校验阶段报 issue 并回退。
- 不得引用旧 `ThemePack` 任何代码或值。

---

## 4. 删除顺序与回滚点

| 步骤 | 动作 | 前置 | 回滚点 |
|---|---|---|---|
| R1 | 新引擎 + Theme Studio + 新壳切换全部合入 main，旧壳仍可启动（`--legacy-shell` 或等价开关） | C-1/C-2/INT-1 | `git tag v11r-pre-retire` |
| R2 | 迁移测试：构造含 9 个旧 ID 的旧配置，逐个启动断言映射正确 & 不崩溃 | R1 | 回退配置文件（测试专用 fixture） |
| R3 | 删除旧主题 UI 入口（旧设置页主题中心、旧 `ThemePack` 选择器） | R2 PASS | R1 tag |
| R4 | 删除旧测试（`ThemeMacosTests/ThemeLayoutsTests/ThemeMacosAuditTests`）并以新 DS/Theme 测试替代 | R3 | R1 tag |
| R5 | 删除 `NewManga.Theme` 项目 + 引用 + `AppOptions --theme/--variant` 旧钩子（改为新 `--theme-id`） | R4 | R1 tag |
| R6 | 全仓 `ThemePack|ThemePacks|ThemePackService|LayoutKind|NavPlacement|ShelfStyle|SettingsStyle` 零引用断言 + 构建/测试全绿 | R5 | R1 tag |

**硬门**：R3–R6 任一步出现"仍有生产页面引用"或"旧配置无法启动"，立即回滚到 R1 tag 并记录原因。

---

## 5. 验证清单（V11R-C-3 AC）

- [ ] 旧 9 个 ID + 未知 ID + 空值 三类迁移用例全部 PASS（启动不崩溃、外观正确、写 issue）。
- [ ] 新系统下主题切换不改变：漫画原图像素、译图、未保存编辑（像素哈希 + 状态断言）。
- [ ] `ThemePack` 等 12 个旧符号全仓零引用（含注释）。
- [ ] `NewManga.Theme` 项目删除后 `NewManga.sln`/`App.csproj` 构建 0 warning。
- [ ] 旧测试文件删除，等价断言在新 DS/Theme 测试中存在（不是简单删测试）。
- [ ] 回滚演练：`git checkout v11r-pre-retire` 可启动（脚本记录）。
- [ ] 独立审查（非实现者）签署。

## 6. 风险

| 风险 | 影响 | 对策 |
|---|---|---|
| 旧配置迁移漏 ID → 启动失败 | 用户无法启动 | 未知 ID 一律回退默认；迁移单测覆盖全 9+2 |
| 删除时仍有生产引用 → 编译失败 | 集成阻塞 | R6 零引用断言作为门 |
| 新引擎缺键 → 界面局部无样式 | 视觉破损 | 逐键回退 + 校验器报 issue |
| 布局枚举迁移过度 | 用户设置丢失 | V1 只映射到 TopBand，其余保留默认并记录 |
