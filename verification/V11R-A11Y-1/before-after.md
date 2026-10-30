# V11R-A11Y-1 修前/修后对照

## 1. 真机 UIA（真实 sidecar，初始资料柜窗口）

### 修前（main `7588ddc7a`，`uia-audit-before.json`）

| # | 控件类型 | UIA Name（缺陷） | 实际内容 |
|---|---|---|---|
| 1 | Button | `Avalonia.Controls.StackPanel` | 资料柜空间（StackPanel：资料柜 + Kbd 1） |
| 2 | Button | `Avalonia.Controls.StackPanel` | 工位空间（StackPanel：工位 + Kbd 2） |
| 3 | Button | `Avalonia.Controls.StackPanel` | 控制台空间（StackPanel：控制台 + Kbd 3） |
| 4 | Button | `Avalonia.Controls.StackPanel` | 作用域（StackPanel：作用域 + 范围文本） |
| 5 | Button | `Avalonia.Controls.StackPanel` | 需要我处理（StackPanel：需要我处理 + 待办） |
| 6 | Button | `Avalonia.Controls.StackPanel` | 命令（StackPanel：命令 + Kbd Ctrl+K） |
| 7 | Button | `NewManga.App.Views.V2.Shell.Controls.Kbd` | 帮助（Button Content=Kbd F1） |

统计：Button 21，可读 14，**未命名/类型名 7**；exit 1。

### 修后（本 commit，`uia-audit.json`）

统计：Button 21，可读 **21**，未命名 **0**；exit 0。

修后名称（真实窗口）：`资料柜空间`、`工位空间`、`控制台空间`、`作用域：未选择对象`、`需要我处理：待办事项`、`命令面板（Ctrl+K）`、`主题工作室`、`深色`、`键位速查（F1）`、`全部`、`收藏`、`已归档`、`导入文件`、`导入文件夹`、`新建作品`、`回收站` 等。

## 2. headless 回归（同一测试，修前/修后）

| 时点 | 结果 | 失败摘要 |
|---|---|---|
| 修前（main 临时 worktree + 同一测试文件） | 红 | `123 unnamed/type-named control(s) across 15 views`；首条 `Shell/Library: Button content=StackPanel[资料柜|1]` |
| 修后 | 绿 | 0；15 视图全部可读 |

修复前失败覆盖视图：Shell/Library、CommandPalette、Jump、Help、Confirm、Console、Studio/Page、Studio/Batch、ThemeStudio 7 分区。

## 3. 关键命名对照

| 位置 | 修前 UIA Name | 修后 |
|---|---|---|
| SpaceTabs 三个标签 | `Avalonia.Controls.StackPanel` | `资料柜空间` / `工位空间` / `控制台空间` |
| 作用域按钮 | `Avalonia.Controls.StackPanel` | `作用域：{ScopeText}` |
| 需要我处理 | `Avalonia.Controls.StackPanel` | `需要我处理：待办事项` |
| 命令 / 速查 | `Avalonia.Controls.StackPanel` / `...Controls.Kbd` | `命令面板（Ctrl+K）` / `键位速查（F1）` |
| 书卡 | 类型名（模板按钮） | `打开作品：{Title}` |
| 章节行 | 类型名（模板按钮） | `打开章节：{Title}` |
| Studio 流水线点 | 空/类型名 | `流水线阶段：{key}（跳到批次并高亮）` |
| Console 分区行 | 类型名 | `任务与队列` 等（Content 文本兜底） |
| Theme Studio 主题卡/外观 chips | 类型名 | 卡片标题/外观文本兜底 |
| Kbd（App + DS） | 类型名/无 | `快捷键 {gesture}`（peer `GetNameCore`） |

## 4. 备注

- `Avalonia.Controls.StackPanel`×6 + `...Controls.Kbd`×1 与真机 L4 报告的 7 个完全一致。
- 修后没有把类型名改成裸文本了事：关键动作（空间切换/作用域/命令/帮助/打开作品/打开章节/流水线跳转）均使用动作语义；纯文本按钮保留其自然名称。
- 回归测试只针对**当前渲染出的可见 Button** 与全部 Kbd 断言，避免把未实现的数据模板误报；真实 UIA 审计作为第二道防线。
