# 融合设计系统（DESIGN_SYSTEM）— 冻结版 v1

> 唯一权威：本文件 + `tokens.json`。任何组件、页面、状态都必须从这两份派生；出现第三份定义即判不合规。
> 编译目标：CSS 自定义属性（`--nm-{group}-{name}`），供 React + CSS Modules / 原生 CSS 使用。

---

## 1. 令牌编译规则

`tokens.json` → CSS 变量，命名：`--nm-{group}-{token}`，主题作用域 `:root[data-theme="dark"|"light"]`。

```css
:root[data-theme="dark"] {
  --nm-color-bg-canvas: #0F1012;
  --nm-color-status-stale: #9A8AB0;
  --nm-size-hTop: 36px;
  --nm-font-family-ui: "Segoe UI Variable Text", "Microsoft YaHei UI", "Noto Sans SC", system-ui, sans-serif;
}
```

**硬规则**
1. 组件 CSS 中**禁止**出现裸色值、裸字号、裸间距（1px 线宽与 0 除外）。
2. 禁止使用阴影表达层级；层级只用 `bg.sunken → bg.canvas → bg.panel → bg.raised → bg.overlay` 五级明度 + `line.*` 描边。
3. 禁止 `linear-gradient` / `radial-gradient` / `backdrop-filter` / `filter: blur`（唯一例外：画布上的磨损贴图由 SVG 绘制，不参与 UI 层级）。
4. 圆角只允许 `radius.none / sm(2px) / md(3px)`；`border-radius > 3px` 视为违规。

---

## 2. 色彩使用规则

### 2.1 强调色与状态色严格分离

| 用途 | 令牌 | 允许出现的位置 |
|---|---|---|
| **强调**（琥珀） | `color.accent.*` | 当前焦点环、激活态、正在编辑的字段边框、选中对象描边、主按钮 |
| **状态**（七态） | `color.status.*` | 状态符号、状态文字、矩阵单元格、对象角标、进度条 |
| **中性** | `color.text.*` / `color.line.*` | 其余一切 |

**禁止**：用状态色做装饰；用强调色表达状态；同一元素同时用强调与状态色（选中 + 失败的 Region 用"强调描边 + 失败角标"两个独立通道表达）。

### 2.2 状态七态映射（唯一口径）

| 语义 | 令牌 | 符号 | 典型场景 |
|---|---|---|---|
| 排队/等待 | `status.queued` | `·` | Task pending、等待上游 |
| 进行中 | `status.running` | `◐` | StepRun、Run running |
| 完成（有效） | `status.done` | `●` | completed、confirmed |
| 失败 | `status.failed` | `✗` | failed、错误 |
| 阻塞 | `status.blocked` | `▲` | blocked、需用户解除 |
| 过期 | `status.stale` | `▨` | 曾成功但上游变更 |
| 跳过 | `status.skipped` | `–` | skipped、not_applicable |
| 未开始 | `text.disabled` | `○` | not_started |
| 锁定 | `status.blocked` | `▮` | 四把 Lock |

**每个状态必须同时具备**：色相 + 符号；文本场景必须带文字标签（如 "过期"），不得仅靠颜色。

### 2.3 对比度下限

- 正文（primary on panel/canvas）≥ 7:1
- 次要文字（secondary）≥ 4.5:1
- 状态文字与符号 ≥ 4.5:1（stale 的紫灰在暗色下需校验，浅色主题用 `#6B5E82`）
- 焦点环与相邻背景 ≥ 3:1
- 任何状态不得仅靠颜色区分（见 2.2）

---

## 3. 排版

| 层级 | 字号 | 字重 | 行高 | 用途 |
|---|---|---|---|---|
| Display | 24px | 400（衬线） | 1.25 | 空态标题、空间标题 |
| Title | 18px | 600 | 1.25 | 面板标题、对话框标题 |
| Body | 13–14px | 400 | 1.45 | 正文、表格内容 |
| Label | 12px | 500 | 1.35 | 字段名、按钮文字 |
| Meta | 11px | 400 | 1.35 | 次要信息、时间、计数 |
| Data | 11–13px mono | 400 | 1.3 | 页码、坐标、百分比、ID、错误码 |

规则：中文正文优先 `Microsoft YaHei UI`（100–150% DPI）与 `Noto Sans SC`（200%）；数据一律 `tabular-nums`；禁止用字重区分状态（用符号与颜色）；标题衬线只用于 Display 级。

---

## 4. 间距与密度

- 间距刻度：2 / 4 / 8 / 12 / 16 / 20 / 24 / 32。
- 面板内边距：8–12px；表格单元格左右 8px；按钮内边距 8/12px。
- **两档密度**（同一套令牌，不同组合）：
  - `Page 模式`：行高 26–28px（胶片条、检查器列表）
  - `Batch 模式`：矩阵行 22px、表格行 26px、数据字号 11px
- 1600×1000 下，Batch 矩阵单屏 ≥ 24 行 × 9 列可见；Page 模式胶片条单屏 ≥ 14 项。

---

## 5. 图标

- 1.25px stroke，20×20 viewBox，24px 显示（密集区 16px）。
- 只用线性；只有"当前/激活"可用 `accent` 着色，其余用 `text.secondary`。
- 禁止 emoji、禁止彩色图标、禁止混用填充风格。
- 图标必须有 `aria-hidden="true"` + 可读的 `title` 或同层文字标签。

---

## 6. 组件清单（40 个）

### 6.1 基础（10）

| 组件 | 变体 | 状态 | 关键约束 |
|---|---|---|---|
| `Button` | primary / default / ghost / danger；sm / md | default/hover/active/focus-visible/disabled/loading | 主按钮用 accent；danger 只用于破坏性动作；加载态文字不变宽 |
| `IconButton` | sm / md；可带 label | 同上 + pressed | 必须有 `title` 与 `aria-label` |
| `SegmentedControl` | 2–4 段 | selected | 用于呈现切换（页面/成品/分屏）、模式切换（Page/Batch） |
| `Chip` | filter / count | off/on/hover | 用于筛选与计数胶囊；on 用 accent.muted + accent 描边 |
| `Input` / `SearchField` | plain / with icon / with clear | default/focus/error/disabled | IME 安全；`Esc` 清空并退出 |
| `Select` / `Menu` | list / grouped | open/closed | 键盘全导航；`Esc` 关闭回焦 |
| `Checkbox` / `Radio` / `Toggle` | — | on/off/indeterminate/disabled | 命中区 ≥ 24×24 |
| `ProgressBar` | determinate / indeterminate | — | 必须显示分母（18/23）；不确定态只显示当前步骤名 |
| `Badge` / `Kbd` | status / count / key | — | 状态 Badge 必须带符号 |
| `Divider` / `ScrollArea` | hairline / section | — | 滚动条 8px，hover 才显形 |

### 6.2 结构（12）

| 组件 | 说明 |
|---|---|
| `TopBand` | 36px：空间切换 / breadcrumb / 作用域选择器 / 需要我处理的聚合 / 命令 / 状态演示 / 主题 |
| `SpaceTabs` | 3 个：Library / Studio / Console；带键位提示；激活态 accent 描边 |
| `Breadcrumb` | 作品 › 章节 › 页；每级可点击；末级不可点 |
| `ScopeSelector` | 本章 / 选中 N 页 / 当前页 / 当前 Region；**始终可见** |
| `AttentionMenu` | 待确认 N · 失败 M · 阻塞 K · 过期 P；点击跳 Batch 对应筛选 |
| `SidePanel` | 左：胶片条（Page）/ 资源树（Batch）；可折叠 56↔200 / 0↔200 |
| `Inspector` | 右：40px 图标条 ↔ 320px 面板；5 页签（文本/样式/修复/锁定/历史） |
| `Drawer` | 右滑出 360px（Batch 详情、Console 分区详情）；不遮挡主区滚动位置 |
| `StatusBand` | 底部：Page=流水线带 28/240px；Batch=Run 带 24px + 展开面板 |
| `AlertBanner` | blocked / stale / interrupted / 导入部分失败；含图标 + 一句后果 + 动作按钮 |
| `Modal` | 确认/危险/中断恢复；默认焦点在"取消"；`Esc` 关闭 |
| `CommandPalette` | Ctrl+K：命令 + 对象跳转；每项标注「空间·模式·作用域」与键位 |

### 6.3 数据（10）

| 组件 | 说明 |
|---|---|
| `DataTable` | 表头 sticky；列宽固定；行 hover；数字右对齐 tabular-nums；空态与加载骨架内置 |
| `StatusMatrix` | 行=页、列=10 阶段；单元格 18×18；支持单选/框选/Shift 多选/双击下钻；图例常驻 |
| `MatrixCell` | 7 态符号 + 可选焦点环；`aria-label` 为"页 023 · 翻译 · 失败" |
| `CountChips` | 概览计数胶囊：总/完成/失败/过期/待确认/阻塞；点击即筛选 |
| `PageGrid` | 页缩略网格（Library）；密度 96–140px；状态角标 |
| `FilmStrip` / `FilmItem` | 纵向缩略流；56px 收起（44×56 缩略 + 序号 + 状态点）；200px 展开（+文件名 + 计数） |
| `RunStrip` | Run 摘要 + 进度 + 控制（暂停/继续/停止）；与 StatusBand 同源 |
| `StageRail` | Batch 顶部阶段轨道：5 阶段 + 队列；每段完成度 + 异常计数 + 门禁警示 |
| `RevisionList` | 版本列表（r1..rn）：时间/来源/变化/current 标记；支持预览与恢复 |
| `Timeline` | StepRun 时间线（可选，用于 Run 详情） |

### 6.4 画布（8）

| 组件 | 说明 |
|---|---|
| `CanvasViewport` | 缩放（86% 默认）/平移/适应窗口；滚轮与手势遵循 `14_INPUT_SPEC` |
| `PageSurface` | 页面图（资源通道 URL）；支持页面/成品/分屏三态 |
| `RegionOverlay` | 绝对定位 Region 层；百分比坐标；不拦截页面拖拽 |
| `RegionBox` | 选中（accent 描边 + 4 角标）/悬停（accent.hover 描边）/失败（failed 角标）/锁定（▮ 角标） |
| `HUDRing` | 选中 Region 周围 8 个动作位（N/NE/E/SE/S/SW/W/NW）；`Tab` 循环、`Enter` 执行 |
| `HUDAction` | 22×22；图标 + 键位提示；禁用态 40% 不透明 |
| `TrackStrip` | 四轨指示（原图/文本/修复/排版）的完成与 stale 状态 |
| `SplitCompare` | 分屏对照（页面 vs 成品，或修复前 vs 修复后），中线可拖动 |

### 6.5 业务（10）

| 组件 | 说明 |
|---|---|
| `TextTierPanel` | 四级文本：ocr_text / machine_translation / edited_translation / final_translation；可视化来源与锁定 |
| `ReviewQueueBar` | 待确认队列条：当前/总数、下一条、批量确认（显示影响面） |
| `LockControls` | 四把锁的开关 + 解释文案（"因人工编辑而锁定"） |
| `TermConflictCard` | 术语冲突：原文/期望译文/实际译文/来源/一键应用并重渲染 |
| `ExportPreflight` | 导出预检：未确认/过期/失败计数 + stale 策略二选一 + 格式与范围 |
| `ImportDock` | 导入进度：每文件状态 + 失败原因 + 重试/跳过 |
| `ProviderStatusCard` | Provider 就绪状态、最近测试结果、凭据状态 |
| `TaskPanel` | Run 任务面板（展开态）：页网格 + 失败聚合 + 控制 |
| `EmptyState` | 一句话 + 一个主操作 + 可选事实行；禁止插画 |
| `Toast` | 只用于"操作已完成"类确认；可恢复错误必须进就地标记 |

---

## 7. 交互状态矩阵（组件级）

每个可异步组件必须实现：

```
idle → loading（骨架保持布局）→ ready（含 empty）→ error（就地 + 重试）→ partial（部分成功）→ stale（曾成功已失效）
```

硬规则：
- 加载不得整页闪白，不得用居中 spinner 替代结构性骨架。
- 错误必须可从发生位置定位：对象 → 阶段 → 错误码 → 摘要 → 建议动作。
- `stale` 必须有独立视觉（`status.stale` + `▨` + 原因文案）。

---

## 8. 键盘与焦点

- 全局：`Ctrl+K` 命令面板、`Ctrl+P` 跳转、`Ctrl+E` 导出、`Ctrl+,` 设置、`F1` 速查、`Esc` 逐级退出。
- 空间：`Ctrl+1/2/3`；模式：`Tab`。
- 对象：`J/K`、`[` `]`、`Shift+[` `]`、`F5`/`Ctrl+Shift+F`。
- 焦点：`2px` `accent` 环 + `accent.ring` 外发光替代（不用 box-shadow，使用 `outline` + `outline-offset`）。
- 浮层：打开时焦点入首项，`Tab` 循环，关闭后回焦触发元素；`aria-modal` + 焦点陷阱。
- IME：输入框获得焦点时，全部字母快捷键让位。

---

## 9. 反面清单（出现即返工）

1. 渐变背景、玻璃拟态、模糊滤镜、彩色投影。
2. `border-radius > 3px`、卡片堆叠、每块内容都装箱。
3. emoji 当图标、彩色图标、混用线性与填充。
4. 用颜色单独表达状态（无符号/无文字）。
5. 把 `stale` 显示成"未完成"或"失败"。
6. 看不出作用域的操作按钮。
7. 只有 toast 的错误反馈。
8. 整页 spinner 替代骨架。
9. 页面级跳转导致上下文丢失。
10. 各处独立定义的色值/字号/间距（绕过令牌）。
