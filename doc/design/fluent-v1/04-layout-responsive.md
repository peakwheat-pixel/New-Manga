# 04 布局与响应式基线（Fluent v1）

**范围**：四页共用的窗口骨架、断点、分栏折叠、双屏/拔屏、DPI 缩放规则。
**令牌来源**：`Nm.Size.*` / `Nm.Size.Breakpoint.*` / `Nm.Space.*` / `Nm.Padding.*` / `Nm.ZIndex.*`（`Tokens.Global.axaml` 实际取值，本文件引用令牌名，不重复裸值）。
**上游**：方案 §15.3（多窗口草稿）、C-02 V-05（Fluent 例外）、C-05（页可见性）。

---

## 1. 窗口骨架（四页共用）

```
┌──────────────────────────────────────────────────────────────┐
│ 顶部命令条 TopBand：空间 1/2/3 · 标题 · 搜索/命令 · 窗口控制     │  Nm.Size.TopBand (36)
├──────────────┬───────────────────────────────────────────────┤
│ 左导航 rail  │ 主内容区（页面按 05–08 规格）                    │
│ Nm.Size.TreeWidth (200) / 折叠隐藏                             │
├──────────────┴───────────────────────────────────────────────┤
│ 状态条 StatusBand：Host/Run 状态 · 进度 · 错误入口              │  Nm.Size.StatusBandPage (28)
└──────────────────────────────────────────────────────────────┘
```

- 顶部命令条与状态条四页恒定；左导航默认展开 `Nm.Size.TreeWidth`（200），折叠后隐藏（不占位），由顶部命令条按钮恢复。
- 状态条高度：页面模式 `Nm.Size.StatusBandPage`（28）；批量/控制台 `Nm.Size.StatusBandBatch`（24）；展开详情 `Nm.Size.StatusBandExpanded`（240，仅状态详情面板）。
- 主内容区四页各自定义（05–08）。
- 所有尺寸必须引用上列令牌（或对应 `Nm.Size.*`）；**禁止**在实现中写死 36/200/28 等裸数。

## 2. 响应式断点（三档，与冻结令牌一致）

| 断点 | 令牌 | 窗口宽度 | 行为 |
|---|---|---|---|
| `Narrow` | `Nm.Size.Breakpoint.Narrow` = 1024 | < 1024 | 左导航折叠隐藏；主内容单栏；检查器/详情改为抽屉（`Nm.ZIndex.Drawer`、`Nm.Size.Drawer`）；film-strip 折叠（`Nm.Size.FilmStripCollapsed` 56） |
| `Medium`（1024–1279） | — | 1024–1279 | 左导航 `Nm.Size.TreeWidth` 200；主内容双栏（列表 + 内容）；检查器 `Nm.Size.InspectorCollapsed`（40）可展开 |
| `Compact`（1280–1599） | `Nm.Size.Breakpoint.Compact` = 1280 | 1280–1599 | 左导航 200；主内容三栏（列表 + 画布 + 检查器 `Nm.Size.InspectorExpanded` 320） |
| `Full` | `Nm.Size.Breakpoint.Full` = 1600 | ≥ 1600 | 同 Compact；画布区最大宽 1600 居中，两侧留白 |

> **说明**：断点只有 `Narrow/Compact/Full` 三个冻结令牌值（1024/1280/1600）；上表把 1024–1279 归为 `Medium` 行为区间（借用 Narrow 与 Compact 之间的既有布局），**不新增令牌**。

最小窗口：`Nm.Size.Breakpoint.Narrow` = 1024 宽为最小；低于则提示并禁止继续缩小（不允许裁切可操作控件）。

## 3. 分栏折叠

- 折叠单位：左导航、检查器/详情、film-strip 三处；折叠后由顶部命令条或页内按钮恢复。
- 折叠状态属于 UI memento（跨页面保留），不写入业务数据。
- 折叠不得导致主内容区宽度 < 512（即 `Nm.Size.Breakpoint.Narrow` 的一半）——低于则强制进入抽屉模式。

## 4. 双屏 / 拔屏

- 第二窗口只承载**只读或独立会话**内容（阅读器视图 / 主题预览）；不复制主窗口的可编辑画布（避免双写）。
- 同一 `(SessionId, RegionId)` 草稿仍由主窗口单一 owner 写入（FEA-03 语义）；第二窗口只读，切换/编辑需转移（`CurrentFrontend` 语义）。
- 拔屏（显示器移除）：第二窗口内容关闭并回到主窗口对应页面；未 flush 的编辑态按 fail-closed 保留在主窗口缓冲，不丢。

## 5. DPI 缩放

- 支持 100% / 125% / 150% / 200%；所有尺寸按逻辑像素计算，由 Avalonia 缩放。
- 200% 下：左导航强制折叠；检查器改抽屉；顶部条保持单行（超出用省略号 + Tooltip）。
- 图标与文字在缩放切换后不得重叠；最小可点击区域 `Nm.Size.ControlHeight` × `Nm.Size.ControlHeight`（取令牌值）。

## 6. 层级（z-order，用冻结 `Nm.ZIndex.*`）

| 层 | 内容 | 令牌 |
|---|---|---|
| 0 | 页面背景（材质/表面） | `Nm.Material.*` / `Nm.Color.Bg.*` |
| 1 | 主内容 | `Nm.ZIndex.Base` |
| 2 | 左导航 / 检查器 | `Nm.ZIndex.Base` + `Nm.Elevation.1` |
| 3 | 浮层（抽屉/命令面板） | `Nm.ZIndex.Drawer` + `Nm.Elevation.2` |
| 4 | 模态对话框 + 遮罩 | `Nm.ZIndex.Modal` + `Nm.Elevation.3` |
| 5 | Tooltip / 通知条 | `Nm.ZIndex.Modal`（置顶）+ `Nm.Elevation.3` |

## 7. 评审检查点

- [ ] 四页都使用 §1 骨架（顶部条 + 左导航 + 状态条恒定），尺寸全部引用令牌。
- [ ] 断点只用 `Narrow/Compact/Full` 三档（§2），未新增断点令牌。
- [ ] 折叠不导致主内容 < 512；折叠状态属 memento。
- [ ] 双屏只读/独立会话，不双写草稿。
- [ ] 200% DPI 下无裁切/重叠；最小点击区域用 `Nm.Size.ControlHeight`。
- [ ] z-order 使用 `Nm.ZIndex.*` 与 Fluent Elevation 令牌。
