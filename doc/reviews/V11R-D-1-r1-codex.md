# 审查结论：FAIL

审查范围是 `819eea0d3` 的快照。文件链接指向当前工作区；括号内行号按该提交的文件内容标注。当前 `main` 已前进到 `672d72484`，其中后续提交修改了部分同名文件；这些后续变更不在本次结论范围内。

## 八项维度

| 维度 | 结论 | 依据摘要 |
|---|---|---|
| 契约一致性 | FAIL | `Nm.FontSize.2Xl` 被生成为 `Nm.FontSize.Xxl`；M0 控件面不完整。现有 Button 类名未发现额外词表项。 |
| 令牌管线 | PASS_WITH_ISSUES | 生成器可检查已生成文件漂移；但 `em` 被当作固定数值，且部分令牌不来自 `tokens.json`。 |
| Avalonia 用法 | PASS_WITH_ISSUES | Button 使用 `ControlTheme`、主题切换使用 `ThemeVariant` / `DynamicResource`；启动默认主题和失败回退有风险。 |
| 无裸值 / 无违规视觉 | FAIL | Button 中有裸 `Transparent` 颜色和 `-2` 间距；输入框焦点样式未按规范形成外侧 outline。 |
| 无障碍 | FAIL | 目标提交的状态色未达到 R-09 对照度要求；焦点实现及减少动态效果覆盖不完整。 |
| 测试质量 | PASS_WITH_ISSUES | 有真实令牌对比度计算和主题切换测试，但一个字典键测试近似自证；截图证据未运行。 |
| 回归风险 | FAIL | 全局 DS 样式在旧 `MainWindow` 仍运行时应用，可能覆盖旧界面样式；DS 默认 Dark 可能覆盖启动主题。 |
| 工程性 | PASS_WITH_ISSUES | 生成产物已入库且生成检查可发现文件漂移；发布裁剪/单文件场景未验证。 |

## Standards

1. **[P1] 深色和浅色状态色未符合 R-09 对照度要求** — [Tokens.Dark.axaml](<G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.DesignSystem/Tokens/Tokens.Dark.axaml>)（`819eea0d3:24`、`:25`、`:27`）、[Tokens.Light.axaml](<G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.DesignSystem/Tokens/Tokens.Light.axaml>)（`:27`）、[ContrastTokenTests.cs](<G:/CODEX/New Manga/apps/desktop-avalonia/tests/NewManga.DesignSystem.Tests/ContrastTokenTests.cs>)（`:56`）— Dark 的 Failed、Queued、Skipped 和 Light 的 Skipped 对比度不足；测试确实计算了对比度，却把这些低于门槛的值固定为预期结果。依据 DESIGN_SYSTEM §2.3、V11R_PROGRAM R-09。建议按 R-09 修正令牌及测试阈值。此处评价的是目标提交；R-09 裁定晚于该提交。

2. **[P1] Primary 按钮文本可能实际落到低对比度颜色** — [Text.Inline.axaml](<G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Text.Inline.axaml>)（`:6`）、[Button.axaml](<G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.DesignSystem/Themes/Controls/Button.axaml>)（`:80`）— Button 将父级 Foreground 设为 `Accent.On`，但全局 `TextBlock` 样式把文本设为 `Text.Primary`；文本型 Content 中的 `TextBlock` 样式值会高于继承值，计算结果约为 `1.92:1`。这低于 DESIGN_SYSTEM §2.3 的对比度要求。Avalonia 文档说明样式值优先于继承值：[属性值优先级](https://docs.avaloniaui.net/docs/properties/value-precedence)。建议调整文本样式/模板，并增加渲染后按钮文字的对比度验证。

3. **[P2] 字号令牌键不符合冻结命名** — [TokenMap.cs](<G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.DesignSystem/Generation/TokenMap.cs>)（`:64`）、[Tokens.Global.axaml](<G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.DesignSystem/Generated/Tokens.Global.axaml>)（`:20`）— `font.size.2xl` 映射成 `Nm.FontSize.Xxl`；契约 §2.2 明确要求 `Nm.FontSize.2Xl`。建议改映射并增加对冻结键名的断言。

4. **[P2] HighContrast / Density 存在令牌第二来源** — [TokenMap.cs](<G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.DesignSystem/Generation/TokenMap.cs>)（`:200`、`:242`）— 这些值在生成器中手工维护，但不在 `tokens.json` 中；`--check` 能发现生成文件相对生成器的漂移，不能发现这套值与规范源文件不一致。依据 DESIGN_SYSTEM 对唯一权威源的要求，以及契约 §2。建议将值纳入正式令牌源，或由 DSH 明确裁定并记录为冻结扩展。

5. **[P2] 组件中仍有未获规范例外覆盖的裸值** — [Button.axaml](<G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.DesignSystem/Themes/Controls/Button.axaml>)（`:44`、`:93`、`:94`、`:106`）— `Transparent` 是直接颜色值；`Margin="-2"` 也不属于契约 §2.2 的允许例外。D-8 虽记录了 `-2`，但目标提交没有把它纳入冻结契约例外。依据 DESIGN_SYSTEM §1/§9、契约 §2.2。建议移除裸颜色，并把任何必要几何例外提交 DSH 裁定后写入冻结规范。

6. **[P2] `em` 单位被解析成固定数值** — [TokenValues.cs](<G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.DesignSystem/Generation/TokenValues.cs>)（`:45`）— 解析会剥离 `em` 后缀，却不结合字号换算；例如 `-0.01em` 被输出为固定数值。Avalonia 的 `TextBlock.LetterSpacing` 单位是 DIP：[TextBlock 文档](https://docs.avaloniaui.net/controls/data-display/text-display/textblock)。建议保留单位语义或按对应字体尺寸转换，并覆盖非 1em 字号的测试。

7. **[P2] 输入框焦点边框不等同于规范要求的外侧焦点环** — [Inputs.axaml](<G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Inputs.axaml>)（`:27`、`:58`）— 焦点状态通过增加 BorderThickness 实现，没有 DESIGN_SYSTEM §8 规定的 2px accent outline 与 offset；边框加粗会改变控件内部几何。建议按规范实现外侧焦点环，并验证键盘焦点下的可见性。

## Spec

1. **[P1] 冻结的 M0 / AC4–6 控件面未交付** — [Controls.axaml](<G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.DesignSystem/Themes/Controls.axaml>)（`819eea0d3:6`）、[NewMangaStyles.axaml](<G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.DesignSystem/NewMangaStyles.axaml>)（`:5`）— 目标提交只有 Button 的 ControlTheme 和 TextBox/TextBlock/Border 样式；契约 §3.1 的标准控件及 §3.2 的 `StatusGlyph`、`StatusBadge`、`Chip`、`Kbd`、`EmptyState`、`AlertBanner`、`ProgressBar`、`Drawer`、`Modal`、`TopBand` 缺失。`V11R-D-1` AC4–6 也未满足。建议交付缺项后再将其作为完整 M0 或 UI 基线。

2. **[P1] 初始化时默认 Dark 可能覆盖启动/用户主题选择** — [DesignSystemThemeManager.cs](<G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.DesignSystem/DesignSystemThemeManager.cs>)（`:43`、`:224`）、[App.axaml.cs](<G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.App/App.axaml.cs>)（`:51`、`:52`）— `App` 调用 `Initialize()`，Manager 的默认 `Appearance` 为 Dark 并设置 `RequestedThemeVariant`；可能覆盖启动时先由 `ThemePackService` 应用的主题。建议把已加载的用户选择传入 Manager，并增加 Light/System 启动测试。

3. **[P2] 字典加载失败的回退可能清空现有令牌** — [DesignSystemThemeManager.cs](<G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.DesignSystem/DesignSystemThemeManager.cs>)（`:257`、`:258`）、[App.axaml.cs](<G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.App/App.axaml.cs>)（`:52`）— Manager 先移除当前 palette provider，再检查全局令牌能否加载；失败时可能留下不完整资源，且 `App` 未处理初始化失败。现有失败测试先清空资源，未覆盖保留初始聚合字典的场景。建议先构造并校验新字典，再原子替换；并测试从正常主题切换到坏字典的行为。

4. **[P2] ReducedMotion 未覆盖仍启用的旧界面动画** — [DesignSystemThemeManager.cs](<G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.DesignSystem/DesignSystemThemeManager.cs>)（目标提交 `SetReducedMotion` 附近）、[AppStyles.axaml](<G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.App/Styles/AppStyles.axaml>)（`:21`）— ReducedMotion 字典只更改令牌；旧 `AppStyles` 的过渡仍有固定时长，并未受令牌控制。依据契约 §4、V11R-D-1 AC8。建议让运行中的过渡绑定 ReducedMotion 状态，验证启用后实际动画关闭。

5. **[P2] DS 全局样式可能改变旧 UI 的外观** — [App.axaml](<G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.App/App.axaml>)（`:19`、`:22`）、[App.axaml.cs](<G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.App/App.axaml.cs>)（`:55`）— 旧 `MainWindow` 仍启动，而 DS 全局样式位于旧 `AppStyles` 后并作用于全应用；它可能覆盖旧界面的字体、TextBlock、TextBox、Border 等样式。建议在新 UI 根节点限定 DS 样式作用域，或增加旧页面兼容性回归验证。

6. **[P2] 令牌字典测试没有检查字典真实键集合** — [TokenResourceDictionaryTests.cs](<G:/CODEX/New Manga/apps/desktop-avalonia/tests/NewManga.DesignSystem.Tests/TokenResourceDictionaryTests.cs>)（`:114`）— `Density_and_motion_overlays_only_contain_contract_keys` 只遍历契约键并检查同一列表中的键，不能发现资源字典额外包含的未知键。建议读取实际 dictionary keys，与允许集合做双向差集断言。

## 已核实为正确的关键点

- 生成器按稳定顺序生成；`--check` 对生成文件内容进行精确比较，缺失或漂移文件可被发现。已有日志记录其通过，本次未重新运行。
- 令牌解析支持当前使用的 `rgba`、`px`、`em` 形态；缺少必需映射或遇到不支持值时会报错，而非静默忽略。
- 成功主题切换路径使用 `DynamicResource` 和 `RequestedThemeVariant`；测试覆盖了现存视觉树随主题切换更新。
- Button 采用 keyed `ControlTheme` 是恰当的用法；没有发现主题令牌值使用 `StaticResource`。
- 目标提交的 `Nm.Motion.Duration.Normal` 为 `140ms`，符合 V11R_PROGRAM R-10。
- 未发现组件使用阴影、渐变、模糊或超过 `3px` 的圆角；测试中未发现 `Sleep` / `Task.Delay` 式等待。

## 未覆盖 / 无法验证项

- **UNVERIFIED**：未重新运行 build/test，以保持只读并避免生成 `bin/obj` 等文件；构建与测试结果来自仓库现有日志。
- **UNVERIFIED**：没有双主题截图或像素级验证。`verification/V11R-D-1/M0-GATE.md` 标记截图 `NOT_RUN`。
- **UNVERIFIED**：Windows 实机启动、键盘/指针焦点、IME 与实际屏幕阅读器行为。
- **UNVERIFIED**：Trim、AOT、单文件自包含发布。目标提交只增加 DesignSystem 项目引用，没有对应发布验证证据。
- **UNVERIFIED**：`M0-GATE.md` 声称 M0 基础控件 Gate 通过，但这与冻结契约 §3.2 所列 M0 控件缺项不一致；`V11R-D-1` 当前仍为 `in_progress`。建议 DSH 对齐 Gate、Task 与实际交付范围。

**审查汇总：Standards 7 项（2 项 P1，5 项 P2）；Spec 6 项（2 项 P1，4 项 P2）。最严重问题：M0 控件面缺失、默认主题覆盖风险、状态色对比度不足及 Primary 按钮文本对比度风险。**

**是否可作为 UI 开发基线：不可以作为完整 UI 开发基线。** 可作为令牌生成与主题切换的部分脚手架；在控件面、R-09 对比度、主题初始化和焦点/动效问题处置并由独立审查确认前，不建议以此冻结 UI 基线。

本次只读；未修改文件、提交或推送。工作区保持 clean。**推荐下一步：由 DSH 将上述审查与 `819eea0d3` 之后的修复提交逐项对照，并指定未参与实现者审查当前修复结果，再决定是否接受为 UI 基线。**