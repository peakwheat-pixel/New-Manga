# V11R-A11Y-1：UIA 可访问名称修复 + 回归防线

- 日期：2026-10-30；分支：`v11r/ui-shell`（基于 main `7588ddc7a`，未 push）
- 来源：真机 L4 UIA 审计（`verification/V11R-L4-EVIDENCE/real-machine/{uia-tree.json,checklist.md}`）
- 结论：**修前 7 个 Button 的类型名（6×`Avalonia.Controls.StackPanel` + 1×`...Shell.Controls.Kbd`）→ 修后 0（真实 UIA 21/21 可读）**；新增 headless 回归测试覆盖 Shell/Library/Console/Studio Page+Batch/ThemeStudio 7 分区/覆盖层共 15 个视图。

## 1. 根因

UIA 的 Name 回退顺序使 Content 为控件树的 Button 暴露 CLR 类型名：`Content=StackPanel`/`Grid`/`Border` → `Avalonia.Controls.StackPanel`；`Content=Kbd` → `...Controls.Kbd`。仅设置 `Content` 字符串的按钮天然有名称，因此缺陷集中在自定义模板按钮。

## 2. 修复（系统性，不只 7 个）

1. **组件级可访问名**（`NewManga.DesignSystem`，Lead 已授权）：`NewManga.DesignSystem.Controls.Kbd` 增加 `KbdAutomationPeer`，`GetNameCore` 返回「快捷键 {Gesture}」，并同步 `AutomationProperties.Name`。App 侧 `Views/V2/Shell/Controls/Kbd` 同样实现（两者都是真实使用的 keycap）。
2. **机械兜底** `Shell/V2/V2AccessibleNames.cs`：注册 `Button.ContentProperty` 类处理器；无显式 `AutomationProperties.Name` 时从 Content 推导可读文本（字符串 / 嵌套 Kbd / 逻辑子树 TextBlock），DataTemplate 内容延迟填充时在 `Loaded` 重试一次。显式名称永远优先，图标按钮仍必须显式命名（测试守护）。
3. **动作语义显式命名**（关键交互，避免只显示文本碎片的机器名）：
   - SpaceTabs：`资料柜空间 / 工位空间 / 控制台空间`（`SpaceTabItem.AutomationName`）
   - TopBand：`命令面板（Ctrl+K）`、`键位速查（F1）`
   - ScopeSelector：`作用域：{ScopeText}`；AttentionMenu：`需要我处理：待办事项`
   - 书卡：`打开作品：{Title}`；章节行：`打开章节：{Title}`（`BookRowViewModel/ChapterRowViewModel.AutomationName`）
   - Studio 流水线点：`流水线阶段：{key}（跳到批次并高亮）`
4. **测试** `V2AccessibilityTests`：遍历 15 个视图/状态的视觉树，收集可见 Button + 全部 Kbd；有效名称规则（显式名 > Content 字符串 > Kbd gesture）必须非空、不以 `Avalonia.`/`NewManga.`/`System.Windows.` 开头、不等于控件类型名；失败信息列出「视图 + 控件类型 + 内容 + classes」。

## 3. 真实 UIA 审计（修前 → 修后）

脚本：`tools/e2e/uia-audit.ps1`（真实 App + 真实 sidecar + 隔离 data/log；UIA 枚举 Button/Edit/ComboBox；任一 Button 空名或类型名 → exit 1；带超时与进程树清理）。

| 时点 | 枚举 | Button | 可读 | 未命名/类型名 | exit |
|---|---|---|---|---|---|
| 修前（main 7588ddc7a 工作树） | 23 | 21 | 14 | **7** | 1 |
| 修后（本 commit） | 23 | 21 | **21** | **0** | 0 |

- 修前 JSON：`uia-audit-before.json`；修后：`uia-audit.json`
- 修后真实窗口按钮名称包含：`资料柜空间`、`作用域：未选择对象`、`命令面板（Ctrl+K）`、`键位速查（F1）`、`全部`、`导入文件` 等（完整列表见 `uia-audit.json`）
- 命令：

```powershell
pwsh -NoProfile -File tools/e2e/uia-audit.ps1 `
  -SidecarDir "G:\CODEX\New Manga\apps\desktop-avalonia\build\sidecar\core-sidecar\core-sidecar" `
  -OutFile "verification\V11R-A11Y-1\uia-audit.json"
```

> 路径含空格时必须 `--key="path"`；脚本内部以单个已引号化参数串传给 Start-Process（避免空格被拆参）。

## 4. headless 回归（红 → 绿）

`V2AccessibilityTests` 同一份测试：
- 修前树（main，临时 worktree）：**失败**，`123 unnamed/type-named control(s) across 15 views`，首条即 `Shell/Library: Button content=StackPanel[资料柜|1]`（`test-a11y-before.log`）
- 修后：**通过**（`test-a11y-after.log`）

## 5. 门禁

- `dotnet build NewManga.sln -warnaserror`：**0 warnings / 0 errors**（`build.log`）
- `dotnet test --settings tests/NewManga.runsettings`：**0 失败**（`test.log`）
  - App 318（311 passed/7 skipped）、Host 77、ThemeEngine 235、DesignSystem 85、CoreClient 141
- 未改变布局/行为：只增加自动化属性、Kbd peer 与命名；真实窗口截图（见 L4）无视觉差异。

## 6. 文件

| 文件 | 说明 |
|---|---|
| `tools/e2e/uia-audit.ps1` | 真实 UIA 审计脚本（可复跑，exit code 门禁） |
| `src/NewManga.App/Shell/V2/V2AccessibleNames.cs` | Button Content→Name 兜底 |
| `src/NewManga.App/Views/V2/Shell/Controls/Kbd.cs` | App Kbd peer/Name |
| `src/NewManga.DesignSystem/Controls/Badges.cs` | DS Kbd peer/Name（唯一 DS 变更，Lead 授权） |
| SpaceTabs/TopBand/ScopeSelector/AttentionMenu/LibraryView/BookDetailPanel XAML | 显式动作语义名称 |
| `test-a11y-before.log` / `test-a11y-after.log` | 回归红/绿 |
| `uia-audit-before.json` / `uia-audit.json` | 真机修前/修后 |
| `before-after.md` | 逐项对照 |

## 7. 边界

- 仅覆盖 V2 界面（`Views/V2/**` + V2 Studio 控件构造代码）；legacy `Views/Pages.cs` 未纳入本任务。
- 本任务不修主题持久化隔离（`FOLLOW-UP-E2E-1`）与发布配置（`FOLLOW-UP-PUB-1`）。
- 真机审计只枚举当前可见窗口（21 Button）；headless 测试覆盖更多视图/状态（含隐藏分区），二者互补。
