# V11R-D-1 Codex r1 审查处置表

- 审查对象：Codex 独立只读审查 `doc/reviews/V11R-D-1-r1-codex.md`（快照 `819eea0d3`）
- 返修分支：`v11r/design-platform`（DS Owner：design-platform）
- 结论：Standards 7 项（2 P1 / 5 P2）+ Spec 6 项（2 P1 / 4 P2）逐条处置如下；两处 P1 已修复并有渲染后/
  启动路径断言。所有结论可由仓库内测试与证据复核。

## P1（Standards）

| # | 问题 | 处置 | 证据 |
|---|---|---|---|
| S-P1-1 | 深/浅色状态色未达 R-09 对比度（审查快照 `819eea0d3` 时点） | **已修**：按 Lead R-09 修订冻结 `tokens.json`（5 处状态/accent 值），`ContrastTokenTests` 改为合规断言；`DECISION_LOG` §5 记录 | `18a6a7782`；`ContrastTokenTests`；`DEVIATIONS.md` D-3 |
| S-P1-2 | Primary 按钮文本实际落到 ~1.92:1 | **已修**：删除全局 `TextBlock` Foreground setter（`Text.Inline.axaml`、旧 `AppStyles.axaml` 同步删除），改由 `Window` 根级设置 `Foreground/FontSize/FontFamily`，文本通过 Avalonia `TextElement` 继承链取色；新增渲染后断言：Primary 按钮内 TextBlock.Foreground == `Accent.On`、实际渲染对比度 ≥4.5，且 `Accent.On/Accent.Base ≥4.5` | `ButtonThemeTests.Primary_and_secondary_button_labels_inherit_the_right_foreground_and_contrast` |
| S-P2-3 | `Nm.FontSize.2Xl` 命名 | **已按 Lead R-14 处置**：契约 §2.2 冻结键改为 `Xxl`，DS 代码无需改；新增断言 `NmKeys.FontSize.Xxl` 存在、`2Xl` 不存在，`TokenMap.md` 注明 | `R14ContractTests.Font_size_key_is_Xxl_and_2Xl_does_not_exist` |
| S-P2-4 | 输入框焦点用加粗边框、无外侧 outline | **已修**：`FocusRing` 附加行为把 2px accent outline 放在 OverlayLayer 外侧定位（tokened 线宽、无阴影、不改模板几何）；覆盖 Fluent TextBox 聚焦蓝边框；键盘焦点截图 | `Styles/Focus.axaml`、`Theming/FocusRing.cs`；`ButtonThemeTests.Keyboard_focus_...`、`StandardControlsThemeTests.TextBox_focus_...`；`screenshots/focus-ring-{dark,light}.png`；`DEVIATIONS.md` D-8 |
| S-P2-5 | 失败回退非原子 | **已修**：先加载/校验替换层，再确保全局令牌存在，最后才移除旧 palette provider；失败保持原状并 `LastError`；新增“正常主题 → 坏 light palette”切换测试 | `ThemeManagerTests.Switching_to_a_broken_palette_keeps_the_previous_state`、`Apply_theme_layer_rejects_missing_keys_and_wrong_types_atomically` |
| S-P2-6 | `em` 被当固定数值 | **已修**：新增 `TokenValueKind.EmRatio` 与 `TokenValues.ParseEmRatio`，生成的 `Nm.FontTracking.*` 明确为 em **比率**（非 px），生成器断言 tracking 必须 em/0；文档注明 Avalonia 无 em 字距 | `R14ContractTests.Tracking_tokens_keep_em_ratio_semantics_and_are_not_pixels`；`DEVIATIONS.md` D-13 |
| S-P2-7 | 字典键测试近似自证 | **已修**：`TokenResourceDictionaryTests` 改为读取真实 `ResourceDictionary.Keys`，与白名单/生成行做**双向差集**（dark/light/global/HC/density/motion 全覆盖） | `TokenResourceDictionaryTests` 4 个用例 |
| S-P2-8 | 裸值（Transparent / Margin -2） | **已修/登记**：`Margin="-2"` 已随 D-8 重构移除（焦点环由行为定位）；`Transparent` 与 0/1px 为契约 §2.4 登记例外；其余裸尺寸已 token 化（`Nm.Size.Marker/MarkerCore/ScrollBar`），新增扫描测试禁止裸 Width/Height/裸色/`StaticResource`/阴影/渐变/模糊 | `R14ContractTests.Design_system_sources_have_no_naked_pixel_sizes...`、`DesignRulesTests` |

## P2（Spec）

| # | 问题 | 处置 | 证据 |
|---|---|---|---|
| P2-3 | HC/Density 第二来源 | **登记为规则派生扩展**（R-14，契约 §2.4），生成器生成期断言 HC 文本 ≥7:1、状态 ≥4.5:1、密度单调；`TokenMap.md` 注明非第二真值源 | `TokenGenerator.ValidateDerivationRules`；`ContrastTokenTests.High_contrast...`；`DEVIATIONS.md` D-1/D-17 |
| P2-4 | M0 控件面缺项 | **已交付**：AC4 标准控件 + AC5 自定义控件 + AC6 状态语言（详见 README AC 对照）；M0-GATE 范围已澄清（M0 仅令牌管线/主题管理/基础样式，控件面属 D-1 AC4/AC5） | `CustomControlsTests`、`StandardControlsThemeTests`、`M0-GATE.md` |
| P2-5 | 初始化默认 Dark 覆盖启动/用户选择 | **已修**：`Initialize(AppearanceMode?)` 接受宿主外观，`App.axaml.cs` 从 `--variant` 传入；未提供才用 Dark；新增 Light/System 启动测试 | `ThemeManagerTests.Initialize_with_an_explicit_light_appearance...`、`...system_appearance...` |
| P2-6 | 旧界面动画不受 ReducedMotion | **登记不修（过渡期）**：ReducedMotion 覆盖 DS 动效令牌；旧 `AppStyles` 过渡随旧壳 C-3 退役 | `DEVIATIONS.md` D-12 |
| P2-7 | DS 全局样式影响旧 UI | **登记不修（过渡期）**：旧壳将被替换；INT-1 后 DS 样式全局生效；旧壳 `TextBlock` 强制前景已删除以免双源 | `DEVIATIONS.md` D-9 |
| P2-8 | 字典键未检查真实集合 | 同 S-P2-7 | `TokenResourceDictionaryTests` |
| P2-9 | M0 Gate 与 Task AC 不对齐 | **已修**：`M0-GATE.md` 明确 M0 范围，AC4/AC5 属 D-1 终态 | `M0-GATE.md` |
| P2-10 | Trim/单文件发布未验证 | **NOT_RUN**，记录于偏差 | `DEVIATIONS.md` D-16 |

## 追加交付：Theme Engine seam（Lead 提级，R-15）

`DesignSystemThemeManager` 新增/收敛契约 §4.1 接口：

- `ApplyThemeLayer(ResourceDictionary layer, string themeId)`：59 键白名单替换（35 色 + 3 字体族 +
  6 字号 + 9 行高 + 3 圆角 + 3 动效）；白名单外键**忽略并记入 `ThemeLayerIssues`**；缺键/类型错 → 失败且
  保持原状（原子）；`AppliedThemeLayerId` 暴露；material/elevation 不接受。
- `ApplyPalette(...)`：仅颜色子集的便捷入口，内部补齐其余 24 键后走同一 `ApplyThemeLayer` 路径，因此也会
  报告 `AppliedThemeLayerId` 与非颜色键 issue。
- `RevertPalette()` 回到内置盘；`Nm.Motion.Duration.Slow(220ms)` 已补入令牌（R-15 扩展）。
- 测试：`ThemeManagerTests` 主题层应用/回滚/缺键/类型错/白名单外键 issue/`ApplyPalette` 继承/原子切换；
  `R14ContractTests.Theme_layer_whitelist_covers_exactly_the_registered_groups`（59 键、无 material/elevation）。

## 追加交付（Lead A 项，R-18/图标/骨架）

| 项 | 处置 | 证据 |
|---|---|---|
| A1 断点语义尺寸 R-18 | **已交付**：Nm.Size.Breakpoint.Full/Compact/Narrow（1600/1280/1024）派生令牌 | CustomControlsTests.Breakpoint_tokens_are_the_single_shared_layout_scale；Tokens.Global.axaml |
| A2 图标集覆盖 | **已交付**：NmIconKind 扩充到 41 个，覆盖 4 个一级空间 + Lead 列出的状态/操作图标；1.25px stroke、20×20、线性、颜色走令牌 | CustomControlsTests.Icon_set_covers_the_primary_spaces_and_state_actions；gallery-*.png 底部图标行 |
| A3 Skeleton 骨架 | **已交付**：Skeleton 三形态（书卡/行/面板）+ 样式，静态无动画（reduced-motion 安全）；EmptyState/AlertBanner 完整样式已在 AC5 | CustomControlsTests.Skeleton_renders_the_three_canonical_shapes_from_tokens；screenshots/gallery-*.png |
| A4 Nm.Motion.Duration.Slow | **已交付**：220ms 派生令牌（R-15 扩展），主题层白名单含 Fast/Normal/Slow | Tokens.Global.axaml；ThemeManagerTests 主题层动效覆盖 |
| A5 ApplyThemeLayer / AppliedThemeLayerId | **已交付**：59 键白名单、material/elevation 不接受、白名单外键忽略并记 ThemeLayerIssues；ApplyPalette 为其颜色子集；失败原子 | 见上文"追加交付：Theme Engine seam"；ThemeManagerTests、R14ContractTests |
