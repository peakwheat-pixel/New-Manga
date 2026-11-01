# 03 键盘与无障碍基线（Fluent v1）

**上游**：C-02 V-08b（`KeyMap` 单一注册表 + 上下文路由 `(frontendId, windowRole, focusScope)`）。
**唯一键位来源**：`Shell/V2/ShellCommands.cs` 的 `Definitions`（`KeyMap` 由其构建；注册冲突启动断言失败）。本文件**不新增**全局键位；只定义 Fluent 的焦点顺序、页内交互键与 a11y 标注。

---

## 1. 全局键位（与 Current 必须一致，来自 `ShellCommands.cs`）

| 键位 | 命令 Id | 说明 |
|---|---|---|
| `Ctrl+1` / `Ctrl+2` / `Ctrl+3` | `space.library` / `space.studio` / `space.console` | 空间切换（资料柜 / 工位 / 控制台） |
| `Tab` | `studio.mode.toggle` | 工位 页面 ↔ 批次（仅在 Studio 空间生效） |
| `Ctrl+K` | `command.palette` | 命令面板 |
| `Ctrl+P` | `go.to` | 快速跳转（作品/章节/页） |
| `Ctrl+E` | `export.run` | 导出（未接线，标记不可用原因） |
| `Ctrl+,` | `settings.theme` | 主题工作室 |
| `F1` | `help.shortcuts` | 键位速查 |
| `F5` / `Ctrl+Shift+F` | `attention.next` | 下一个需处理项（未接线） |
| `Esc` | `surface.back` | 返回 / 关闭浮层 |
| `J` / `K` | `object.next` / `object.previous` | 资料柜对象导航 |
| `[` / `]` | `page.previous` / `page.next` | 翻页 |
| `Shift+[` / `Shift+]` | `chapter.previous` / `chapter.next` | 翻章 |

**Fluent 侧约束**：以上键位在 Fluent frontend 下**必须映射到同一命令 Id**；Fluent 不得注册冲突键位（`KeyMap` 启动断言）。Fluent 新增键位必须先在 `ShellCommands.cs` 注册（共享文件由 DSH 单点提交），不得在 Fluent 侧私建第二份注册表。

## 2. 页内交互键（非全局，聚焦于控件时生效；不注册进 `KeyMap`）

| 上下文 | 键 | 行为 |
|---|---|---|
| 书架列表 | `↑`/`↓` | 移动选中项（单选）；`Shift+↑/↓` 扩展多选 |
| 书架列表 | `Space` | 切换当前项选中状态（多选） |
| 书架列表 | `Enter` | 打开选中项（作品→章节；章节→阅读器） |
| 工作台 Tab 页签（焦点在页签条时） | `←`/`→` | 切换页签（页面/批量/控制台）；**不使用无修饰 `Tab`**（全局 `Tab` 已被 `studio.mode.toggle` 占用） |
| 工作台表单 | `Enter` | 提交当前编辑（等同主按钮）；`Esc` 放弃并还原 |
| 阅读器 | `←`/`→`/`PgUp`/`PgDn` | 翻页（单页模式）；`↑`/`↓` 滚动（滚动模式） |
| 阅读器 | `+`/`-`/`0` | 缩放；`0` 复位 |
| 阅读器 | `F` | 全屏切换 |
| 设置 | `Tab`/`Shift+Tab` | 分组内顺序遍历（见 §3） |
| 任意 | `Esc` | 关闭当前浮层（若有），否则返回上一级（`surface.back`） |

## 3. 焦点顺序（四页，Tab 序 = 视觉阅读序）

**书架**：左导航（空间列表）→ 书籍列表 → 章节列表 → 页面缩略图 → 右侧操作区 → 状态栏。

**工作台**：顶部 Tab 条 → 左导航 → film-strip → 主画布 → 右侧检查器 → 底部操作条 → 状态栏。

**阅读器**：返回 → 页面视图 → 翻页按钮 → 浮动工具条 → 底部进度 → 顶部信息条（隐藏时不在 Tab 序）。

**设置**：返回 → 左侧分组列表 → 分组内容（自上而下控件）→ 底部保存/取消。

规则：
- 焦点环始终可见（`Nm.Focus.Ring.Width`=2 / `Nm.Focus.Ring.Offset`=1 / `Nm.Focus.Ring.Color`；**该三键待 FEA-05 生成，见 01 G-1c**），高对比模式加粗（§4）。
- 浮层打开时焦点移入浮层首个可聚焦控件；关闭后回到触发控件。
- 不允许把焦点移入不可见控件；隐藏状态控件从 Tab 序移除。

## 4. 高对比与可读性

| 项 | 要求 |
|---|---|
| 对比度 | 正文 ≥ 4.5:1；大字号（≥18.66px bold 或 ≥24px）≥ 3:1；图形/边框 ≥ 3:1 |
| 高对比模式 | 由 `Contrast` 设置驱动（C-03 `Appearance.Contrast`）；高对比下：阴影 → 1px 边框；材质 → 不透明表面色；焦点环 3px |
| 颜色非唯一线索 | 状态（成功/失败/阻塞）必须同时有图标或文字；不得仅靠颜色区分 |
| 字号 | 跟随 `Nm.FontSize.*`；用户缩放（DPI 125%/150%/200%）下布局不裁切（见 `04-layout-responsive.md`） |

## 5. 屏幕阅读器标签

每个可交互控件必须有 `AutomationProperties.Name`（中文语义名）与必要的 `HelpText`：
- 按钮：`Name` = 动作名（例：「保存草稿」「取消」）；带图标无文字的按钮必须给 `Name`。
- 列表项：`Name` = 主文本 + 状态（例：「第 3 页 · 已完成」）。
- 输入框：`Name` = 标签；错误时 `AutomationProperties.HelpText` = 错误原因，并触发 `LiveSetting=Polite` 播报。
- 只读状态（进度/状态点）：`Name` 包含数值（例：「进度 62%，全部翻译，运行中」）。

## 6. 评审检查点

- [ ] 全局键位表与 `ShellCommands.cs` 完全一致（命令 Id 一一对应，无新增全局键）。
- [ ] Fluent 未私建第二份 `KeyMap`；上下文键覆盖 `(frontendId, windowRole, focusScope)`。
- [ ] 四页焦点顺序可机械核对（§3 顺序与页面骨架一致）。
- [ ] 每个可交互控件有 `AutomationProperties.Name`；错误有 `HelpText` + live region。
- [ ] 高对比模式有明确降级规则（阴影→边框、材质→不透明）。
