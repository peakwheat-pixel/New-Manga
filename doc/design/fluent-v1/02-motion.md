# 02 动效基线（Fluent v1）

**上游**：C-03 `doc/plan/FEA-C03_PRESENTATION_SETTINGS_DRAFT.md` §2.3（三态 `auto`/`full`/`reduce`、三类 `navigation`/`feedback`/`decorative`）与 §3 判据 ①–⑤。
**原则**：所有动效必须能在 `reduce` 下降级；降级只改时长/曲线，不改布局、不改层级、不改可读性。

---

## 1. 三态定义（与 C-03 一致）

| `motion.mode` | 语义 | 来源 |
|---|---|---|
| `auto` | 跟随系统辅助功能设置（Windows：`SPI_GETCLIENTAREAANIMATION` / WinRT `UISettings.AnimationsEnabled`） | 用户显式选择或新安装默认 |
| `full` | 始终完整动效（显式覆盖系统） | 用户显式选择 |
| `reduce` | 始终减弱（三类分别降级） | 用户显式选择；旧 `ReducedMotion=true` 迁移后落此值且三类全禁 |

**读取失败降级**：平台读取失败按 `full` 处理并记 warning（C-03 §2.3）。
**优先级**：用户显式优先（U-05c A）：`auto` 跟随系统；`full` 覆盖系统；`reduce` 强制减弱。
**分类开关语义**：`motion.categories[x]=关` 表示该类**在 `full` 下也按 `reduce` 列执行**；`=开` 表示按 `motion.mode` 列执行；三类独立，互不影响。

## 2. 三类动效 × 三态参数表（冻结）

时长单位 ms；曲线为 cubic-bezier。

### 2.1 `navigation`（页面/Tab/浮层切换）

| 场景 | `full` | `auto`（系统开） | `auto`（系统关）/ `reduce` |
|---|---|---|---|
| 一级页面切换（书架↔工作台↔阅读器↔设置） | 240ms `ease-out` `(.2,0,0,1)` | 同 full | **0ms（无动画切换）** |
| Tab 切换（工作台 页面/批量/控制台） | 180ms `ease-out` `(.2,0,0,1)` | 同 full | 0ms |
| 浮层（对话框/抽屉/命令面板）进入 | 200ms `ease-out` `(.2,0,0,1)` + 遮罩淡入 160ms | 同 full | 0ms + 直接显示 |
| 浮层退出 | 160ms `ease-in` `(.4,0,1,1)` | 同 full | 0ms |

> **浮层归属判定（C-03 `:49` 要求）**：浮层过渡归 **`navigation`**（页面级上下文切换），**不归** `decorative`；`reduce` 下按上表 0ms，`full` 下允许位移 ≤ 8px。

### 2.2 `feedback`（控件反馈）

| 场景 | `full` | `auto`（系统开） | `reduce` |
|---|---|---|---|
| 按钮 hover 背景 | 120ms `ease` `(.4,0,.2,1)` | 同 full | **保留颜色变化、无位移**；`motion.categories.feedback=关` 或旧值迁移后颜色过渡亦置 0ms（§3 判据⑤） |
| 按钮 pressed 形变 | 缩放 0.98，90ms | 同 full | **无缩放**（仅颜色） |
| 状态点/徽标出现 | 淡入 150ms + 缩放 0.9→1 | 同 full | 纯淡入 0ms（直接显示） |
| 保存/提交进行中 | 进度条扫光 1.2s 循环 | 同 full | **静态进度条**（无扫光） |
| 错误抖动 | 位移 ±4px 2 次 200ms | 同 full | **无抖动**（仅红色高亮） |

### 2.3 `decorative`（环境装饰）

| 场景 | `full` | `auto`（系统开） | `reduce` |
|---|---|---|---|
| 书架背景渐变缓动 | 8s 循环 | 同 full | **完全禁用**（静态背景） |
| 阅读器翻页装饰粒子 | 400ms | 同 full | 完全禁用 |
| 空态插画漂浮 | 6s 循环 | 同 full | 完全禁用 |

## 3. C-03 §3 判据 ①–⑤ 对应（每条给出可验证断言）

| 判据 | 要求 | 本基线落点 | 可验证断言 |
|---|---|---|---|
| ① | `reduce` 下 `decorative` 时长 0 | §2.3 全列 `禁用` | 单测：`motion.mode=reduce` → `decorative` 动画对象时长为 0 / 不创建 |
| ② | `full` 下不跟随系统 | §1 优先级 + §2 全表 `full` 列独立于系统 | 单测：注入系统「关动画」→ `full` 仍执行 full 时长 |
| ③ | `auto` 按注入的假平台设置切换 | §2 表 `auto` 两列 | 单测：`IMotionPreferenceSource` 返回 true/false → 对应列 |
| ④ | `navigation` 在 `reduce` 下无动画切换 | §2.1 `0ms` | 单测：页面切换在 `reduce` 下无 transition 附加 |
| ⑤ | 旧 `ReducedMotion=true` 迁移后三类全禁（**包括 `feedback` 的颜色过渡也置 0**，等价 C-03 `:57`「所有时长置 0」） | §1 + §2 全表；`feedback` 在 `reduce` 下颜色过渡也取 0ms | 迁移测试：旧值 → `motion.mode=reduce` + 三类「关」；断言所有类别时长（含 `feedback` 颜色过渡）= 0ms |

## 4. 实现约束（供 FEA-05/06）

- 动效时长/曲线必须来自令牌或本表常量（`Nm.Motion.*` 既有键 + 本表参数），UI 代码不得散落魔法数。
- 动效降级**不得**改变布局（不改变尺寸/位置/层级）；`reduce` 下浮层直接出现/消失，不保留不可见占位。
- 长时间循环动效（`decorative`）在窗口失焦/不可见时暂停（省电与性能）。
- 屏幕截图/自动化测试环境（无渲染）必须可关闭全部动效（供 FEA-05 测试复用）。
