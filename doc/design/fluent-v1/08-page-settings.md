# 08 设置页规格（Settings）

**页 ID**：设置页以 `ShellSurface.ThemeStudio`（主题工作室）外壳承载外观分组；其余分组（Provider/网络/备份/关于）沿用既有设置 surface。不新增 `SpaceId`，入口来自顶部命令条与左导航。
**参考**：C-03（外观持久化 `presentation-settings.json`、`motion.mode` 三态、`motion.categories` 三类、`Contrast`、`ReducedMotion` 迁移）、C-02（frontend/visualTheme 标识）

---

## 1. 布局（Medium 断点）

```
┌──────────────────────────────────────────────────────────────┐
│ 顶部命令条：返回 · 设置 · 搜索设置 · 窗口控制                    │
├──────────────┬───────────────────────────────────────────────┤
│ 分组列表 240 │ 分组内容（表单卡片区，可滚动）                    │
│ 外观/Provider│ ┌ 外观 ──────────────────────────────────────┐  │
│ 网络/备份    │ │ 视觉主题 · 深/浅 · 对比度 · 动效三态/三类 ·   │  │
│ 关于         │ │ 圆角/材质（Fluent 时可用）                   │  │
│              │ └────────────────────────────────────────────┘  │
├──────────────┴───────────────────────────────────────────────┤
│ 底部操作条：保存 · 取消 · 重置该分组        状态条：保存结果     │
└──────────────────────────────────────────────────────────────┘
```

- 分组固定：外观、Provider 与凭据、网络、备份与恢复、关于。
- 表单卡片：`Nm.Color.Bg.Raised` + `Nm.Corner.Fluent.Md` + `Elevation.1`。
- 危险操作（重置、清理）单独分组卡片 + 二次确认（`Elevation.3` 对话框）。

## 2. 组件与令牌

| 组件 | 令牌 |
|---|---|
| 分组列表项 | `Nm.Corner.Fluent.Sm`；选中 `Nm.Color.Accent.Muted` |
| 表单卡片 | `Nm.Corner.Fluent.Md`、`Elevation.1`、内边距 `Nm.Space.*` |
| 输入框 | `Nm.Corner.Fluent.Sm`；错误时 1px `Nm.Color.Status.Failed` 边框 + HelpText |
| 开关/滑块 | 既有 `Feedback.cs`/`Inputs.cs` 组件 |
| 保存按钮 | `Nm.Color.Accent.*` 主按钮；禁用态语义 |
| 危险按钮 | `Nm.Color.Status.Failed` 边框（outline） |
| 对话框 | `Nm.Corner.Fluent.Lg` + `Elevation.3` + 遮罩 |
| 状态提示 | `InfoBar` 风格（`Skeleton`/`Status.cs` 组件） |

## 3. 分组与字段（冻结清单）

| 分组 | 字段 | 存储/契约 |
|---|---|---|
| 外观 | 视觉主题（`theme.visualThemeId`：`newmanga-default` / `builtin.fluent-dark`） | C-02/C-03 |
| 外观 | frontend（`theme.frontendId`：`builtin.current-v2` / `builtin.fluent`） | C-02 |
| 外观 | 深/浅（C-03 §2.2 `appearance`） | C-03 |
| 外观 | 对比度（C-03 §2.2 `contrast`） | C-03 |
| 外观 | 动效模式（C-03 §2.2 `motion.mode`：`auto`/`full`/`reduce`） | C-03 |
| 外观 | 动效三类（C-03 §2.2 `motion.categories`：`navigation`/`feedback`/`decorative` 各开/关；关 = 该类在 `full` 下也按 `reduce` 列执行） | C-03 |
| 外观 | 圆角/材质（C-03 §2.2 `corners`/`material`；Fluent 视觉主题下可用，Current 下忽略不报错） | C-02/C-03 |
| 外观 | 布局档（C-03 §2.2 `layout.*`：navigation/shelf/density/workbench/reader） | C-03 |
| 外观 | 跟随系统强调色（C-03 §2.2 `followSystemAccent`） | C-03 |
| 外观 | 设置 schema 版本（`schemaVersion`，只读展示/迁移状态） | C-03 |
| Provider 与凭据 | Provider 列表/启用/凭据引用（不显示明文） | Host/凭据管理 |
| 网络 | 代理/超时/并发 | 既有设置 |
| 备份与恢复 | 备份目录/频率/恢复入口（恢复须整库锁 L-5） | C-09/ADJ-001 |
| 关于 | 版本/许可证/开源声明 | — |

**外观保存铁律**（C-03 §3）：`presentation-settings.json` 只由 `AppearanceCoordinator` 写；保存失败必须对用户可见（不得静默降级）；旧文件迁移幂等。

## 4. 状态（AC1 必须齐全）

| 状态 | 触发 | 表现 |
|---|---|---|
| **空** | 无分组（不应发生；防御） | 整页空态 + 重试；不崩溃 |
| **载入** | 读取设置 | 卡片骨架；分组列表可先显示 |
| **错误** | 读取/保存失败 | 顶部错误条（原因 + 重试）；保存失败保留未保存值并提示 |
| **满** | 正常 | 全部分组可编辑 |
| **部分** | 某些字段不可用（如 Fluent 材质在 Current 下；Provider 未配置） | 字段禁用 + 原因 Tooltip；不隐藏 |
| **权限/只读** | Host 只读 | 全部保存禁用 + 顶部警示；仍可浏览 |

## 5. 交互

- 修改即标记脏（底部「保存」启用）；离开页面有未保存修改 → 确认（保存/丢弃/取消）。
- `Esc` = 取消当前编辑（若有对话框先关对话框）。
- 保存：走 `AppearanceCoordinator`（外观）；失败显示 `InfoBar` 错误 + 重试。
- 搜索设置：顶部搜索框过滤分组/字段（仅前端过滤，不改数据）。
- 重置该分组：二次确认后调用对应服务（外观重置回默认；其他分组各自语义）。

## 6. 响应式

| 断点 | 行为 |
|---|---|
| Narrow（<1024） | 分组列表折叠为下拉/面包屑；内容单列 |
| Medium（1024–1279） | 分组列表 `Nm.Size.TreeWidth` 200 + 内容 |
| Compact/Full（≥1280） | 同 Medium，内容最大宽 `Nm.Size.Breakpoint.Narrow`（1024）内居中 |

## 7. a11y 与键盘

- Tab 序：返回 → 分组列表 → 分组内容（自上而下）→ 底部操作条。
- 输入框 `Name` = 标签；错误 `HelpText` + live region；保存成功/失败用 `LiveSetting=Polite` 播报。
- 危险操作确认框默认焦点在「取消」；`Esc` = 取消。
- 开关控件有明确状态名（「动效模式：跟随系统」）。

## 8. 评审检查点

- [ ] 分组/字段清单与 C-03 迁移后的 `presentation-settings.json` 字段一一对应。
- [ ] 外观保存走 `AppearanceCoordinator`；失败可见（不静默）。
- [ ] 六种状态齐全（§4）。
- [ ] 危险操作二次确认、默认焦点在取消。
- [ ] 令牌使用（§2）；响应式/a11y 符合 03/04。
