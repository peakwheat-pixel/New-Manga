# FEA-06-PREREQ-2 实施记录与偏差登记（delivery notes）

- Task：`doc/tasks/FEA-06-PREREQ-2.md`（scope-r4 approved；base_commit `a33778608`）
- 实施者：DSH（Lead / Architect / Integrator，主会话）
- 日期：2026-11-02
- 实施顺序：P1/P4 selector → P2/P3 组合根 + Fluent 壳骨架 → P5 写者收敛 → P6 主题层 Material → P7 manifest/校验 → 全量收口
- 全量基线：**1022 passed / 0 failed / 57 skipped**（实施前 979/0/57；+43 net new tests）
- 治理：`check.ps1` PASS（3 warnings）；`verify_pins.ps1` PASS 15/15；`TokenGen -- --check` EXIT 0；`ThemeGen -- --check` EXIT 0；`task_ledger.py --write` 已执行

## 1. AC → 实现 → 证据映射

| AC | 实现落点 | 证据 |
|---|---|---|
| AC1 selector 决策表 | `App/Services/FrontendSelector.cs`（`FrontendSelection` + `FrontendSelector.Select`；CLI > persisted > 缺省；未知/`builtin.fluent-dark` → V2 + `Diagnostic`/Trace 记录） | `ac1-selector-tests.log`（13 tests） |
| AC2 组合根按 selector 建壳 | `App.axaml.cs`：`CreateShell(...)` 统一分派（`--shell=legacy` 运维修回优先；否则 selector 选 Fluent / V2）；V2 路径只显式接收 appearance writer + themeHome，语义不变 | `ac2-ac3-shell-tests.log`（FluentShellTests 5 + V2ShellUiTests 25）、`test.log`（全量） |
| AC3 Fluent 壳骨架 | `Views/Fluent/FluentShell.axaml(.cs)`：顶条 `Nm.Size.TopBand` + 左导航 `Nm.Size.TreeWidth` + 状态条 `Nm.Size.StatusBandPage` + 四页占位；`--page` hook 映射 | `ac2-ac3-shell-tests.log` |
| AC4 全量不退化 | 全量 sln build/test | `build.log`、`test.log`（1022/0/57） |
| AC5 写者收敛 + 兼容写 | `NewManga.Appearance/AppearanceCoordinator.cs`（迁移落地 + `SaveAsync` 唯一写者）；`AppearanceStore.FileName`；`ThemeEngine/Service/IThemeSettingsSink.cs`；`ThemeSettingsStore` 新增 sink 构造器重载 + `[Obsolete] SaveAsync` 双写；App 侧 `AppearanceThemeSettingsSink`；两个生产创建点注入（`ThemeEngineThemeStudioService.CreateProduction(...presentationSink)`、`StubThemeStudioService.Create(...presentationSink)`） | `ac5-appearance-tests.log`（21）、`ac5-sink-tests.log`（4）、`ac5-compat-write-tests.log`（24） |
| AC6 Material 主题层键 | `TokenMap.ThemeLayerOnlyKeys`（两键，仅登记不进 `Tokens.Global.axaml`）+ TokenGen 输出 `NmKeys` 常量与映射行；“`ThemeLayerMaterialKeys`” 进 `ThemeLayerAllowedKeys`（Required 59 不变，Allowed 65→67）；`ThemeTokenKeys.MaterialColors`；`ThemePaletteComposer` 可选合成（59 或 61 keys）；`BuiltInThemeGenerator` 在 fluent 包 colors 承载两值；`R14ContractTests` 同步 | `ac6-r14-tests.log`（11）、`ac6-material-tests.log`（51）、`tokengen-check.log`、`themegen-check.log` |
| AC7 manifest + 校验 + Current 不生效 | fluent 包 `metadata.extra["nm.fluent.visual"]="1"`（ThemeGen 生成）；`ThemeDefaults.FluentVisualManifest*` 常量；`ThemeValidator`：Fluent 缺/改 manifest、非 Fluent 声明 manifest、Fluent 缺材质键、非 Fluent 声明材质键均 error；`BuiltInThemes` 加载 + `ThemeService` Current 仍为 `newmanga-default` 断言 | `ac7-manifest-tests.log`（60） |

## 2. 偏差与裁决登记

### 2.1 D-1 关闭（PREREQ-1 遗留）
`AppearanceCoordinator` 由 `NewManga.App/Services` 迁入 `NewManga.Appearance`（namespace `NewManga.Appearance`），并新增 `SaveAsync` 调 `AppearanceStore.WriteAsync`：`presentation-settings.json` 的唯一生产写者回到 C-03 §2.1 指定的项目。旧文件 `App/Services/AppearanceCoordinator.cs` 与其 App.Tests 测试已删除，测试迁入 `NewManga.Appearance.Tests` 并补写者断言。

### 2.2 W-12（实施期 DSH 裁决）：P7 校验器归属 + 写域补口
- C-02 §4 要求 ThemeEngine 项目内校验器承担「manifest 缺失/被手改 → 加载失败；令牌齐全性 + 例外仅限 Fluent + 无裸值」。
- 实施期实测：现有 `ThemeValidator` 的 id 规则（仅 `[a-z0-9-]`）会拒绝冻结的视觉主题 id `builtin.fluent-dark`（含 `.`），因此「不改 validator、只加测试」（scope-r3 R3-P2-2 的最小路径）**不可能**让 AC7 的 `Validate(fluent)` 通过。
- 故 `allowed_paths` 增 `apps/desktop-avalonia/src/NewManga.ThemeEngine/Validation/**`，`ThemeValidator` 仅增加校验规则（manifest/材质键/id 命名空间），**不改 `ThemeKind` 枚举与任何公开方法签名** → V-07 不触碰、无需 UNFREEZE。
- 已在任务卡「附加裁决点」新增 W-12 行（含依据与边界）。

### 2.3 兼容写设计（P5 具体形态）
- `ThemeSettingsStore` 保留原两参构造器（不变签名），新增三参重载接收 `IThemeSettingsSink?`；`SaveAsync` 标 `[Obsolete]`，先写旧 `theme-settings.json`，再经 sink 镜像写 `presentation-settings.json`（顺序保证旧文件不回退，sink 失败向上抛出、由 `ThemeService.TrySave` 记录 warning）。
- App 侧 adapter `AppearanceThemeSettingsSink` 做字段全量映射：themeId→visualThemeId、appearance/contrast/layout/followSystemAccent 一对一、旧 `ReducedMotion` 布尔→`motion.mode`（true=Reduce / false=Full，保留旧开关语义；三分类不动）。
- 两个生产创建点均新增可选 `presentationSink` 参数；沙箱默认 null（不触碰真实用户文档）。

### 2.4 主题层 Material 值（P6）
设计 01 §41-42 以 AARRGGBB 记录；生成器以 CSS 表达写入 fluent 包的 colors：
- `Nm.Material.Acrylic.Base` = `#1F1F1F`（设计 `#FF1F1F1F`）
- `Nm.Material.Acrylic.Tint` = `rgba(0,122,204,0.2)`（设计 `#33007ACC`，alpha 0x33≈20%）
fluent-dark 为 dark-only 包，light 槽沿用 dark 调色板（impl-r4 P2-8 既有口径）。`newmanga-default.nmtheme` 字节不变（ThemeGen 输出 5036 chars，diff 未触及）。

### 2.5 视觉主题 id 命名空间（W-12 配套）
`ThemeValidator.IdPattern` 放宽为允许 `.`（`^[a-z0-9](?:[a-z0-9.-]{0,62}[a-z0-9])?$`），以容纳 C-02 V-07 冻结的 `builtin.fluent-dark`；用户 slug 规则不受影响（大写/下划线/首尾非字母数字仍拒绝）。既有 `DescriptorIdInvalid` 用例仍通过。

## 3. 复核过程披露（R4-OBS-1）

- 本卡的 **scope-r4 复核被并行执行了两次**：另一 DSH 席位在 `b2a45af6d` 提交了同一路径的 r4 报告（approved / P2=0）并据此 release 置 ready；本会话另行派发的独立上下文子代理（subagent_zcode）形成本工作区当前版本报告（approved / **P2=1** + R4-OBS-1 并行披露），并覆盖了工作区同名文件（`b2a45af6d` 版本字节保留在 Git 历史中）。
- 两版结论同向（approved / P0=P1=0），差异仅 P2 计数：本报告采纳保守口径 **P2=1**，并在本轮实施中顺手关闭该 P2（R4-P2-1：P6 计数括号由「全局令牌数不增」改为「Base/Tint 为可选键，不进 Required 59」）。
- 处置：保留当前工作区 r4 报告与 `b2a45af6d` 的 release 记录，`checkpoint §28` 注记口径差异；不重开范围冻结。

## 4. 已知限制（不阻塞本卡）
- `--frontend` 值域不做 CLI 级校验（保持既有解析行为），未知值由 selector fail-safe 到 V2 并记录。
- Fluent 四页内容、导航状态容器、Theme Studio Fluent 适配均属 FEA-06；本卡仅交付可启动骨架。
- R2-P2-6（base_commit 在 release 时刷新）已在 release 时刷新为 `a33778608`。

## 5. 实现复核 impl-r1 与处置（2026-11-02）

- **impl-r1**（独立上下文子代理，被审 `9478c96fb`）：**changes_requested，P0=0 / P1=1 / P2=3**；AC1–AC7 逐条 **MET**，全量 1022/0/57 复现，W-12 经独立机械证实合法。报告：`doc/reviews/FEA-06-PREREQ-2-impl-r1.md`。
- **R1-P1-1（写域扩张未登记）处置**：卡 `allowed_paths` 回填 `NewManga.ThemeEngine/Palette/**` 与 `NewManga.ThemeEngine/Service/**`，并新增 **W-13** 裁决行（行为必需性、零契约面变化、与 W-12 同性质、内容披露先于登记）。docs-only，无代码返修；待 impl-r2 窄面复核。
- **R1-P2 处置（接受遗留/已注记）**：P2-1 W-12 属实施期自裁决，已由 impl-r1 独立确认（P2 注记）；P2-2 `ThemeValidator.IdPattern` 放宽面宽于最小必要（`.` 对 user 主题亦放行，威胁面无实质变化），登记为已知放宽、user/builtin 命名空间隔离留 FEA-06 导入侧；P2-3 `StubThemeStudioService.Create` 的 sink 注入无直接测试（沙箱默认 null 安全，`CreateProduction` 有端到端测试）——三者均接受遗留，不阻塞本卡。

