# Fluent v1 设计基线（FEA-04b）

**版本**：`fluent-v1.0.0`（设计基线，非代码）
**Task**：`doc/tasks/FEA-04b.md`（design，写域 `doc/design/fluent-v1/**`）
**上游契约**：C-02（V11R 修订单，已冻结：V-05 Fluent 视觉例外、V-08b `KeyMap`）、C-03（外观持久化，已冻结：`motion.mode` 三态、`motion.categories` 三类）、C-05（页可见性，已冻结）
**上游方案**：`doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md` §12.1/§15.3/§15.6
**适用范围**：`builtin.fluent` frontend + `builtin.fluent-dark` 视觉主题下的四页（书架 / 工作台 / 阅读器 / 设置）交互与视觉基线；**不适用于** `builtin.current-v2`（Current 视觉由既有 V2 规范约束）。

---

## 1. 目标与非目标

**目标**：给 FEA-05/06 提供可直接实现、可机械评审的数值与结构基线——四页布局骨架、状态矩阵、令牌取值、动效参数、键盘与 a11y。

**非目标**：
- 不写生产源码（无 `src/`/`apps/` 写权）；不实现 Fluent 界面。
- 不改冻结契约字节；不新增契约字段（令牌名以 C-02 冻结定义为准，见 `01-design-tokens.md`）。
- 不替换 Current 视觉；Current 的既有令牌与基线不变（C-02 V-05 判据②）。

## 2. 文档索引

| 文件 | 覆盖 AC | 内容 |
|---|---|---|
| [01-design-tokens.md](01-design-tokens.md) | AC2 | 圆角/材质/层次令牌取值、C-02 V-05 判据①映射、裸值禁令 |
| [02-motion.md](02-motion.md) | AC3 | 动效三态 × 三类参数表、C-03 §3 判据 ①–⑤ 对应、浮层归属判定 |
| [03-accessibility.md](03-accessibility.md) | AC4 | 焦点顺序、快捷键（`KeyMap` 对齐）、高对比、屏幕阅读器标签 |
| [04-layout-responsive.md](04-layout-responsive.md) | AC1/AC5(响应式) | 页面骨架、断点、分栏折叠、双屏/拔屏、DPI |
| [05-page-shelf.md](05-page-shelf.md) | AC1 | 书架页：布局/层级/状态/空错载 |
| [06-page-workbench.md](06-page-workbench.md) | AC1 | 工作台页：布局/层级/状态/空错载 |
| [07-page-reader.md](07-page-reader.md) | AC1 | 阅读器页：布局/层级/状态/空错载 |
| [08-page-settings.md](08-page-settings.md) | AC1 | 设置页：布局/层级/状态/空错载 |
| [09-state-matrix.md](09-state-matrix.md) | AC1 | 四页状态矩阵（空/载入/错/满/部分）汇总 |
| [10-component-inventory.md](10-component-inventory.md) | AC1/AC2 | 组件清单（名称/令牌依赖/状态/尺寸） |

## 3. 全局设计原则（四页共用，评审基线）

1. **令牌唯一来源**：任何颜色/圆角/材质/阴影/间距/字号必须引用 `Nm.*` 令牌；Fluent 例外仅限 C-02 V-05 允许的 `Nm.Material.*`/`Nm.Elevation.*`/`Nm.Corner.Fluent.*`，且只在该 frontend+visualTheme 组合下生效。
2. **状态优先于样式**：每页必须先定义状态（空/载入/错/满/部分），样式只描述满态；`09-state-matrix.md` 为唯一状态清单。
3. **焦点可见且可预测**：Tab 顺序按视觉阅读序；焦点环始终可见（高对比下加强）；不得用鼠标悬停替代焦点态。
4. **动效可降级**：所有动效必须能在 `motion.mode=reduce` 下降级为无动画或纯色变化（见 `02-motion.md`），且降级不改变布局与层级。
5. **键盘可达**：所有可操作控件有快捷键或可 Tab 到达；快捷键以 C-02 V-08b `KeyMap` 为唯一键位来源（见 `03-accessibility.md`）。
6. **不改变数据语义**：UI 只展示 Host/Core 投影；不引入本地业务真值（与 FEA-04 Current 适配同一原则）。

## 4. 版本与变更规则

- 版本号语义：`fluent-vMAJOR.MINOR.PATCH`；布局/状态/令牌**取值**变化 → MINOR；仅文字/示例 → PATCH；MAJOR 需 DSH 裁决并重冻结。
- 变更流程：改文档 → 独立上下文复核 → DSH 冻结 → 升版本号并在本节记录。
- 与实现的关系：FEA-05/06 实现若偏离本文数值，必须在 Task 中登记偏差并重走复核；不得静默偏离。

## 5. 评审检查点（供 Reviewer 机械核对）

- [ ] 四页各含：布局骨架、层级、全部状态（空/载入/错/满/部分）、响应式断点（`04-layout-responsive.md` §2）。
- [ ] 每个视觉数值指向令牌（`01-design-tokens.md` §3 对表），无裸值。
- [ ] 动效表覆盖 `auto`/`full`/`reduce` × `navigation`/`feedback`/`decorative`，且逐条满足 C-03 §3 判据 ①–⑤。
- [ ] 快捷键表与 C-02 V-08b `KeyMap` 无冲突（`03-accessibility.md` §3）。
- [ ] 状态矩阵与四页正文一致（`09-state-matrix.md`）。
