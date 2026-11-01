# 06 工作台页规格（Studio）

**页 ID**：`SpaceId.Studio`；模式 `StudioMode.Page` / `StudioMode.Batch`（C-02 §6.1，不得新增模式）
**参考**：方案 §15.3（S1–S6 状态迁出）、Current V2 工作台基线（`V2StudioPageTests`/`V2StudioBatchTests` 行为为不退化基线）

---

## 1. 布局（Expanded 断点）

```
┌──────────────────────────────────────────────────────────────────────────┐
│ 顶部命令条：空间 · 工位 · Tab[页面|批量|控制台] · 命令 · 窗口控制              │
├────────┬──────────────────────────────────┬──────────────────────────────┤
│ 左导航 │ 主画布（页面图 + region 框选）      │ 检查器（Inspector `Nm.Size.InspectorExpanded` 320）        │
│ `Nm.Size.TreeWidth`(200) │ 工具栏：缩放 · 适应 · 框选 · 工具    │ 文本/几何/样式 · 锁 · digest   │
├────────┴──────────────────────────────────┴──────────────────────────────┤
│ 底部操作条：保存草稿 · 应用 · 丢弃 · 状态文案        │ 状态条：Run 状态/进度      │
└──────────────────────────────────────────────────────────────────────────┘
```

- **Tab 页签**：页面（Page）/ 批量（Batch）/ 控制台（Console 视图入口）——对应 `StudioMode.Page`/`Batch`；控制台是独立空间（`SpaceId.Console`），此处 Tab 只作为快捷跳转入口，不改变 `SpaceId` 语义。
- **页面模式**：主画布单页；左侧 film-strip 缩略图（宽 `Nm.Size.FilmStripCollapsed`（56），可折叠）；检查器固定右栏。
- **批量模式**：主区为矩阵（行=页面，列=阶段，来自 `step_flow` 投影，不硬编码十列）；顶部筛选 chips + 作用域；操作条含翻译/重 OCR/重修复/重渲染。
- 检查器在 Narrow（<1024）断点变为抽屉；批量模式在 Narrow 下矩阵横向滚动 + 列固定首列（页面列）。

## 2. 组件与令牌

| 组件 | 令牌 |
|---|---|
| 主画布容器 | `Nm.Color.Bg.Sunken`、`Nm.Corner.Fluent.Lg`、内边距 `Nm.Space.*` |
| 页面图 | `Nm.Corner.None`（图像不圆角） |
| Region 框 | 1.5px 描边（选中 2px `Nm.Color.Accent.*`）；锁图标角标；hover 提升 |
| 检查器面板 | `Nm.Color.Bg.Raised`、`Nm.Corner.Fluent.Lg`、`Elevation.1` |
| 工具按钮 | `Nm.Corner.Fluent.Sm`；激活态背景 `Nm.Color.Accent.Muted` |
| 底部操作条 | `Nm.Color.Bg.Raised` + 顶部 1px 分隔线 |
| 批量矩阵单元格 | `Nm.Corner.Fluent.Sm`；七状态语义色（`Nm.Color.Status.*`）+ 图标 |
| 矩阵表头 | 吸顶；列宽最小 96（设计常量，FEA-05 登记/DSH 裁决，见 01 G-1b），阶段名可换行 |
| Run 投影条 | `Skeleton`/进度条既有组件；状态文案来自共享 RunMonitor |

## 3. 状态（AC1 必须齐全）

| 状态 | 触发 | 表现 |
|---|---|---|
| **空（无章节/页）** | 未选章节 | 主区空态：图标 + 「从书架选择章节」+ 按钮跳书架 |
| **空（批量无 Run）** | 批量模式无 Run | 空态卡：「开始处理」主按钮 + 说明；不显示矩阵 |
| **载入** | 加载页面/投影 | 画布骨架 + 检查器骨架；状态条「读取中」 |
| **错误** | Host 错误 | 错误卡（原因 + 重试 + 控制台入口）；画布保留上一帧（不清屏） |
| **满** | 正常编辑 | 画布 + 检查器 + 操作条；未保存标记（标题旁圆点 + 底部文案） |
| **部分/未决** | 有待确认操作（切页/切模式有未 flush 编辑） | 模态确认「保存 / 丢弃 / 取消」；`Esc` = 取消；确认前不切页（fail-closed） |
| **冲突** | 文本冲突 / binding 变更 / 锁冲突 | 检查器顶部冲突条（原因 + 「查看对照」）；不自动合并；应用被禁用 |
| **只读** | Host 只读 / 草稿非本会话 owner | 检查器全禁用 + 顶部警示条（原因 + 转移入口） |

## 4. 交互（对应 FEA-03/04 语义）

- 编辑先注册 Core draft token（FEA-03）；UI 响应前保留内存缓冲，journal ACK 后才承诺崩溃恢复。
- 切换页面/模式/空间前 flush 未保存编辑；flush 失败留在旧 UI，不切换。
- 「应用」（apply）走统一 apply seam：stale / 三锁 / protectionDigest 校验失败 → 结构化错误展示，不静默丢弃。
- 未决确认不自动执行；旧回调不重放（S2）。
- 批量操作（翻译/重 OCR/重修复/重渲染）必须经 Run intent key（C-03/R-22），丢 ACK 后重试复用同 key，不二次启动。

## 5. 响应式

| 断点 | 行为 |
|---|---|
| Narrow（<1024） | 检查器抽屉；film-strip 折叠（`Nm.Size.FilmStripCollapsed` 56）；批量矩阵横向滚动 |
| Medium（1024–1279） | 检查器 `Nm.Size.InspectorExpanded` 320；film-strip `Nm.Size.FilmStripExpanded` 200 |
| Compact/Full（≥1280） | 检查器 `Nm.Size.InspectorExpanded` 320；film-strip `Nm.Size.FilmStripExpanded` 200；画布最大宽 `Nm.Size.Breakpoint.Full` |

## 6. a11y 与键盘

- Tab 序：顶部页签条 → 左导航 → film-strip → 画布 → 检查器 → 底部操作条 → 状态条。
- `Tab`（全局，`studio.mode.toggle`）切换 页面/批量；页签条内用 `←`/`→` 切换（不使用无修饰 Tab）；`[`/`]` 翻页；`J`/`K` 对象导航；`Esc` 关闭浮层/取消确认。
- 画布 region 可用键盘聚焦（Tab 进入画布后 `方向键` 在 region 间移动），聚焦时显示焦点环；`Enter` 进入编辑。
- 检查器字段 `AutomationProperties.Name` = 字段标签；校验失败 `HelpText` = 原因 + live region。
- 状态点/进度：`Name` 含数值（例：「第 3 页 · 翻译 · 完成」）。

## 7. 数据与真值

- 画布 region 几何/文本/样式来自 Host/Core 投影；本地仅保留未 ACK 的编辑缓冲（DraftBuffer）。
- Run 投影来自共享 RunMonitor（单轮每 Run ≤1 次 snapshot/projection 查询，S5）；批量矩阵列来自 `step_flow`，不硬编码。
- 不引入第二份业务真值（FEA-04 AC3 同一原则）。

## 8. 评审检查点

- [ ] 八种状态齐全（§3），冲突/只读/未决态有明确恢复路径。
- [ ] 编辑→应用→失败路径与 FEA-03 规则一致（stale/锁/digest fail-closed）。
- [ ] 批量矩阵列来自投影 `step_flow`；intent key 复用符合 R-22。
- [ ] 所有视觉数值走令牌（§2）。
- [ ] 响应式与 a11y 符合 03/04 文档。
