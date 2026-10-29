# 第二轮审查结论：**FAIL**

固定审查对象是 `be76f168105aaab3ce6756f8f6ee7a4e9bdb6d49`。发现两个仍影响正常启动或无障碍的 P1，另有多项令牌语义与焦点行为问题。**D-1 目前不能收口为 `done` 或 `closed_with_limitations`，也不适合作为冻结的 UI 基线。**

## 上一轮 P1/P2 关闭表

| 上一轮问题 | 状态 | 本轮核对 |
|---|---|---|
| P1：R-09 状态色对比度 | **PARTIAL** | 令牌测试已检查状态色与纯 `bg.panel` 的对比度，但没有检查徽标实际使用的 muted 背景。Light `Skipped` 前景与合成后的 muted 背景约 **4.01:1**，仍低于 4.5:1。见 [`Tokens.Light.axaml:27,34`](</G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.DesignSystem/Themes/Tokens.Light.axaml:27>)、`Controls.Status.axaml:33,109`、`ContrastTokenTests.cs:43-50`。 |
| P1：Primary 按钮文字对比度 | **CLOSED** | 全局 `TextBlock.Foreground` setter 已移除；[`ButtonThemeTests.cs:61-90`](</G:/CODEX/New Manga/apps/desktop-avalonia/tests/NewManga.DesignSystem.Tests/ButtonThemeTests.cs:61>) 在显示窗口中读取按钮内实际 `TextBlock` 的前景笔刷，并断言计算对比度 ≥4.5:1。 |
| P1：M0 控件面缺项 | **CLOSED** | 标准控件和 D-1 所需自定义控件均已交付，并有对应测试。 |
| P1：启动默认 Dark 覆盖选择 | **PARTIAL** | [`App.axaml.cs:35-59`](</G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.App/App.axaml.cs:35>) 先应用 `StartupThemeId`，但初始化只把 `StartupVariant` 传给 manager；无该参数时仍走默认 Dark。`StartupThemeId` 对应的主题外观没有传入，现有 Light/System 测试也只直接测试 manager，未覆盖真实 App 启动。 |
| P2：`Xxl` 命名 | **CLOSED** | 有断言 `Xxl` 存在、`2Xl` 不存在：`R14ContractTests.cs:15-27`。 |
| P2：HC/Density 第二来源 | **PARTIAL** | 已登记为规则派生扩展，但密度验证器跳过无全局映射的行，并直接跳过 `Padding`：`TokenGenerator.cs:426-435`。 |
| P2：`Transparent` / `Margin="-2"` 裸值 | **PARTIAL** | `Margin="-2"` 已移除；契约只允许控件模板中的 `Transparent`，而多个普通样式仍直接使用它，且扫描测试未限定作用域。见契约 `§2.4` 第 83 行、`Controls.Custom.axaml:49-62`、`Controls.Navigation.axaml:8,31`、`Controls.Selection.axaml:86`、`DesignRulesTests.cs:49-65`。 |
| P2：`em` 被当固定值 | **CLOSED** | 已作为 `EmRatio` 比率输出，并在 D-13 登记 Avalonia 字距不支持 em 的限制。 |
| P2：焦点环无外侧 outline | **PARTIAL** | 外侧 2px ring 已实现，不改控件几何；但没有处理滚动容器裁切，也没有区分键盘与指针焦点，详见新问题。 |
| P2：失败回退原子性 | **NOT_CLOSED** | 正常的单层替换先加载、再验证，但真实 App 的聚合资源会在初始化时被整体移除；此外切换失败时 manager 状态也可能已改变。 |
| P2：旧壳动画不受 ReducedMotion 控制 | **CLOSED** | 已在 D-12 登记为旧壳退役前的过渡限制。 |
| P2：DS 全局样式影响旧壳 | **CLOSED** | 已在 D-9 登记旧壳共存限制。 |
| P2：字典键测试近似自证 | **CLOSED** | 测试现在读取真实 `ResourceDictionary.Keys` 并比较集合：`TokenResourceDictionaryTests.cs:32,89,108,138-157`。 |
| P2：M0 Gate 与控件交付范围不一致 | **NOT_CLOSED** | 当前契约说 M0 包含 §3.1 及一组指定控件（`V11R_AVALONIA_CONTRACT.md:112`），而 [`M0-GATE.md:19-20`](</G:/CODEX/New Manga/verification/V11R-D-1/M0-GATE.md:19>) 又说控件面不属 M0。 |
| P2：Trim/AOT/单文件发布验证 | **NOT_CLOSED** | D-16 已记录，但仍为 `NOT_RUN`。 |

## 新问题

- **[P1]** `NewMangaTheme.axaml:7-9`、`DesignSystemThemeManager.cs:491-505,604-620` — 正常 App 启动会丢失全局令牌。App 聚合资源同时含 Global 与 Dark palette；`EnsureGlobalTokens()` 看到聚合字典含 `Nm.Space.3` 就认为全局令牌已加载，随后 `RemovePaletteProviders()` 因它也含 `Nm.Color.Bg.Canvas` 而移除整个聚合字典，只重新加入 palette。全局间距、字号、`Nm.Color.Scrim` 等因此消失。隔离测试 harness 没有加载 App 的聚合字典，未覆盖此路径。建议拆分并保留全局 provider，只替换 palette；增加使用真实 `App.axaml` 资源栈的启动测试，断言 `Nm.Space.3`、`Nm.FontSize.Md`、`Nm.Color.Scrim` 可解析。

- **[P1]** [`Tokens.Light.axaml:27,34`](</G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.DesignSystem/Themes/Tokens.Light.axaml:27>)、`Controls.Status.axaml:33,109`、`ContrastTokenTests.cs:43-50` — Light `Skipped` 徽标的实际对比度约为 4.01:1。测试将状态前景与纯白 `bg.panel` 比较，没有把 `#1F8A8F94` muted 背景合成后再比较。建议调整 `Skipped` 前景/背景组合，并对实际渲染徽标取笔刷、合成背景后断言 ≥4.5:1。

- **[P2]** `DesignSystemThemeManager.cs:59-71`、`TokenMap.cs:203-213`、`Styles/Text.Inline.axaml:14,20,26,34` — R-15 要求行高乘数 3 键和绝对行框 6 键；白名单实际包含 3 个乘数加 6 个语义别名，没有包含被文本样式使用的 `Nm.TextLineBox.*` 绝对值。应用主题层改了 `Nm.LineHeight.Body`，实际 `TextBlock.LineHeight` 仍读固定行框。建议按 R-15 纳入 6 个行框键或明确派生更新，并增加真实控件行高断言。

- **[P2]** `DesignSystemThemeManager.cs:658-704` — 有 overlay 时，`ReorderOverlays()` 把 palette 放到索引 0、overlay 放到末尾。存在单独 Global provider 时，Global 的位置可能晚于 palette，覆盖主题层中的字体、字号、行高等值；当前主题层测试没有在主题层应用后切换 overlay。建议固定为 Global → palette/theme layer → overlays，并覆盖各 overlay 的开关测试。

- **[P2]** `DesignSystemThemeManager.cs:255-268,507-519` — `ApplyPalette` 补齐非颜色值时按 merged dictionary 的正序取第一个值；Global provider 在活动主题层之前时，会用默认字号/字体覆盖当前主题层值。建议从当前活动主题层或 Avalonia 实际资源优先级取值，并测试“应用主题层后再应用 palette”是否保留字体与字号。

- **[P2]** `TokenGenerator.cs:179-185`、`TokenMap.cs:184`、`TokenResourceDictionaryTests.cs:138-143` — ReducedMotion 表漏掉已登记的 `Nm.Motion.Duration.Slow=220ms`，因此开启减少动态效果后 Slow 仍可能保留非零时长。建议从全部 duration 键生成零值表，并断言 Fast/Normal/Slow 均为零。

- **[P2]** `FocusRing.cs:69-74,130-156` — ring 通过 `GotFocus` 无条件显示，没有键盘焦点模态判断；定位只转换坐标和控件 bounds，没有计算祖先 `ScrollViewer` 的裁剪区域，控件滚出视口后 ring 仍可能画在可见内容上。`IsHitTestVisible=false` 已避免 ring 拦截点击。建议只对键盘导航显示，并按裁剪区域隐藏/裁切 ring；补充滚动、指针聚焦和弹层测试。

- **[P2]** `DesignSystemThemeManager.cs:198-203,278-335,339-350,544-553` — 失败的 palette/overlay 加载仍可能留下错误 manager 状态：调用前已更新 `Appearance`、contrast/density/motion 字段或 `RequestedThemeVariant`，而失败测试 `ThemeManagerTests.cs:268-286` 只检查颜色、空间值和 palette ID。建议先验证资源，再一次性提交属性、`RequestedThemeVariant` 和 provider 状态；测试失败后所有状态均未改变。

- **[P2]** `TokenGenerator.cs:426-435` — 密度单调性验证对无映射项 `continue`，对 `Padding` 也直接跳过，注释声称比较聚合值但实际没有比较。`--check` 能检查生成文件与生成器输出的字节漂移，不能发现生成器自身漏检规则。建议逐项解析 `Thickness` 并比较 Compact / Comfortable / Spacious，或为派生项登记可执行比较规则。

- **[P3]** `VisualEvidenceTests.cs:52` — `Assert.Same(window.Content, window.Content)` 是恒真断言，不证明主题切换没有重建窗口，违反 R-25 的断言纪律。另有有效的 live-control 测试 `ThemeManagerTests.cs:186-208`，但建议删除恒真断言，并保存切换前后的窗口内容引用比较。

- **[P3]** `CustomControlsTests.cs:295-318` — 图标测试只验证选定图标；`Enum.IsDefined` 对编译期枚举常量保障有限，数量断言仅要求 `>=40`，实现虽有 41 个枚举/几何映射，测试不能确保所有映射都存在。建议遍历所有 41 个值并逐个断言有效几何。

## 已核实正确

- Primary 按钮修复有显示窗口中的有效前景笔刷与对比度断言，不是只检查资源键。
- `ApplyThemeLayer` 白名单总数为 59，`AppliedThemeLayerId` 只在成功替换后更新；白名单外键会被忽略并记录 issue，material/elevation 不在允许键中。
- `PaletteColorKeys` 是公开集合，明确排除 `Nm.Color.Scrim`，符合 R-21；实现正确，但建议补显式 `DoesNotContain(Scrim)` 断言。
- R-18 断点值为 1600/1280/1024，测试逐项断言。
- `Skeleton` 的形状/尺寸有测试，且实现为静态控件，没有 pulse/shimmer 动画。
- `Nm.Motion.Duration.Slow` 已纳入主题层白名单；问题仅在 ReducedMotion overlay 漏掉它。
- 主题切换使用资源替换；`ThemeManagerTests.cs:186-208` 验证现存控件更新，没有重建窗口。
- 记录的 `--check` 日志报告所有生成产物与冻结 token 源逐字节一致；它能防输出漂移，但不能替代派生规则本身的语义检查。

## UNVERIFIED

- **规范 pin 缺失**：`be76` 的 tree 不含用户指定的 `doc/plan/V11R_AVALONIA_CONTRACT.md`、`doc/V11R_PROGRAM.md` 等文件。本轮按用户列出的规范使用当前 main 对应版本核对，不能确认这些规范在 `be76` 当时的文件快照。建议由 DSH 确认该规范版本是否就是 D-1 的适用冻结版本。
- **未重跑测试或实机验证**：本轮只读检查源码、测试和已记录日志；没有重跑测试。键盘/指针焦点、滚动容器裁切、真实 App 聚合资源启动与双主题徽标对比度，建议在修复后运行对应渲染测试并做 Windows 截图验证。
- `be76` 已是 main 的祖先，但当前 main 合入树与该 pin 不完全相同。建议修复后针对最终集成 commit 重新固定审查 pin，确认集成树保留这些验证结果。

**D-1 不可收口为 `done` 或 `closed_with_limitations`，不可作为 UI 基线。** 推荐下一步：由 DSH 释放修复任务，优先解决两个 P1（全局令牌丢失、Light `Skipped` 对比度），并处理 R-15 行框与主题层资源优先级；修复后对最终集成 commit 进行独立复审。