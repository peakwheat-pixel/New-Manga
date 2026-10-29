# 设计裁决记录：A + C 融合

- 日期：2026-10-25
- 裁决人：用户
- 内容：从三套全新设计方向中选择 **A（暗房）+ C（工坊）** 组合，进入阶段 4 统一实施。
- 记录人：DSH（Lead / Architect / Integrator）

---

## 1. 裁决内容

用户在阶段 3 Gate 选择 `A+C`，即：

> 以 **A 暗房**（画布中心、空间化、HUD 环、精细图像工位）的产品骨架与视觉母语为主体，
> 吸收 **C 工坊**（批次/阶段轨道/状态矩阵/异常治理/批量动作）的能力与状态系统，
> 融合为**一套单一设计**后实施。

B（校阅台）不被采纳为方向；其"逐条校对流"的思想以 `ReviewQueueBar` + `全部确认` 等组件形式局部吸收，不构成独立导航范式。

## 2. 融合判定（为什么不是拼盘）

| 决策 | 内容 | 理由 |
|---|---|---|
| 空间数量 | **3 个**：Library / Studio / Console（不新增第四空间） | 避免回退到旧版"四页面平级"结构；批次不是页面，是 Studio 的第二种工作模式 |
| Studio 形态 | **双模式**：Page（默认，A 形态）↔ Batch（C 形态），`Tab` 切换 | 两种粒度回答不同问题；同空间内切换可保住上下文，且下钻/上浮成为一条连续路径 |
| 选择模型 | **单一 store**，两模式共用 selection | 防止"Batch 框选 3 页、切到 Page 只剩 1 页"这类双重真值 |
| 状态语言 | 采用 C 的七态完备系统（queued/running/done/failed/blocked/stale/skipped）+ 未开始/锁定，全部配符号 | A 原有语义色不够覆盖 Batch 矩阵；C 的编码更完备，但按 A 的低饱和色调重校准 |
| 强调色 | 保留 A 的琥珀，**只**用于焦点/激活/选中，与状态色严格分离 | 避免"强调色当状态色"的常见错误 |
| 视觉母语 | A 的暗房层级 + 无阴影 + 1.25px 图标 + 三字体栈 | 保留 A 的专业质感；C 的等宽数据与矩阵密度作为 Batch 模式的局部规则并入 |
| 阅读 | 不设独立空间，作为 Library 内浮层 | 旧版"阅读器页面"是最容易丢上下文的一页 |
| 批次对象 | **不新增实体**：批次 = PipelineRun 的作用域投影 | 避免为 UI 造领域对象 |

## 3. 对复核意见的回应

独立复核曾指出"A 的视觉轮廓是三套中最接近旧 Shell 的"。融合版通过以下四点结构性消除该风险：

1. 旧版是四页面平级 + 侧栏点击切换；融合版是三空间 + 双模式 + 键位/命令面板切换。
2. 旧版页面跳转丢上下文；融合版 selection/滚动/筛选跨模式与空间保留。
3. 旧版进度只存在于工作台底部；融合版 Run 状态在两模式常驻且同源。
4. 旧版无批量与异常治理；融合版 Batch 模式提供矩阵 + 概览 + 批量动作 + 阶段门禁。

## 4. 生效范围

- 冻结文件：`40-fusion/FUSION_SPEC.md`、`40-fusion/DESIGN_SYSTEM.md`、`40-fusion/tokens.json`、`40-fusion/IMPLEMENTATION_PLAN.md`。
- 三套方向的原始产物（`20-directions/A-darkroom`、`C-atelier`）保留为**设计证据与视觉参考基线**，不再作为实施依据；B-parlor 同时保留为未采纳方案证据。
- 实施期间任何偏离冻结规范的行为，必须先修改冻结文件并在此记录理由。

---

## 5. R-09：冻结令牌对比度修订

- 日期：2026-10-30
- 裁决人：DSH（Lead / Architect / Integrator），裁决编号 **R-09**
- 来源规范条款：`DESIGN_SYSTEM.md` §2.3（正文 ≥7:1；次要文字与状态文字/符号 ≥4.5:1；焦点环 ≥3:1）
- 触发：`V11R-D-1`（Design System Avalonia）用 WCAG 2.1 公式实测冻结 `tokens.json`，发现标准盘
  部分状态色与浅色强调色不满足 §2.3（详见该任务 `verification/V11R-D-1/DEVIATIONS.md`）。
- 裁决：**规范条款优先于数据**；修订 `tokens.json` 数据而非放宽规范；高对比模式
  （`Themes/Tokens.HighContrast.axaml`）继续保留为更强分离档。
- 范围：仅修订下表令牌；其余令牌保持原字节；`statusMuted.*` 是装饰性底色，不受正文对比度约束，
  保持不变。

| 令牌 | 修订前 | 修订前对比度 | 修订后 | 修订后对比度 |
|---|---|---|---|---|
| `color.dark.status.queued` | `#5C6169` | 2.74:1（bg.panel） | `#8A9099` | 5.31:1（bg.panel） |
| `color.dark.status.skipped` | `#4A4F55` | 2.07:1（bg.panel） | `#82878E` | 4.72:1（bg.panel） |
| `color.dark.status.failed` | `#C9634F` | 4.38:1（bg.panel） | `#CC6A57` | 4.69:1（bg.panel） |
| `color.light.status.skipped` | `#8A8F94` | 3.26:1（bg.panel） | `#73777B` | 4.51:1（bg.panel） |
| `color.light.accent.base` | `#B4791F` | 3.69:1（白字） | `#96651A` | 5.03:1（白字）/ 4.53:1（bg.canvas） |
| `color.light.accent.hover` | `#9C6717` | 亮度 0.1683 | `#7F5515` | 亮度 0.1106 |
| `color.light.accent.active` | `#8A5A12` | 亮度 0.1276 | `#6B470F` | 亮度 0.0767 |
| `color.light.accent.muted` | `rgba(180,121,31,0.12)` | — | `rgba(150,101,26,0.12)` | — |
| `color.light.accent.ring` | `rgba(180,121,31,0.40)` | — | `rgba(150,101,26,0.40)` | — |

浅色强调色修订后亮度仍保持 `base > hover > active` 单调（0.1587 > 0.1106 > 0.0767），交互态层级不变。

- 验证：`V11R-D-1` 的 `ContrastTokenTests` 已从"特征化冻结值缺口"改为**合规断言**
  （标准盘状态文字对 `bg.panel` 全部 ≥4.5:1；浅色主按钮白字 ≥4.5:1；强调色明度单调），
  高对比档断言保留；token 生成器 `--check` 在修订后仍逐字节一致。

---

## 6. D-1 I2 / P1-2：状态徽标合成背景对比度补丁

- 日期：2026-10-30
- 裁决来源：Lead `V11R-D-1-r2` 独立审查 **P1-2**（Light `Skipped` 徽标实测 ≈4.01:1，低于
  §2.3 的 4.5:1）；同时授权"调整 Light Skipped 前景/背景组合（或状态徽标改用不透明的状态底色
  令牌）"。
- 根因：状态徽标背景是半透明 `statusMuted.*`，实际有效背景是它与父面板的**合成色**；
  原 R-09 只对 `bg.panel` 验证，故按合成背景复测时 7 个状态/主题组合低于 4.5:1。
- 裁决：沿用 R-09"规范条款优先于数据"的原则，仅修订下表 7 个状态前景令牌，使**在合成徽标背景
  上** ≥4.5:1；`statusMuted.*` 装饰底色保持不变，其余令牌保持原字节。
- 伴随实现修正（不涉及令牌）：`StatusGlyph.notstarted` / `TextBlock.nm-status-notstarted` 由
  `Text.Disabled` 改为 `Text.Secondary`——unstarted 是真实状态而非禁用控件，避免 2.52:1 的
  低对比符号（dark 8.18:1 / light 5.86:1 on `bg.sunken`）。

| 令牌 | 修订前 | 修订前（合成徽标底） | 修订后 | 修订后（合成徽标底 / bg.panel） |
|---|---|---|---|---|
| `color.dark.status.running` | `#5B93B8` | 4.10:1 | `#689CBE` | **4.60:1** / 5.76:1 |
| `color.dark.status.failed` | `#CC6A57` | 3.89:1 | `#D27A69` | **4.54:1** / 5.47:1 |
| `color.dark.status.stale` | `#9A8AB0` | 4.26:1 | `#9F90B4` | **4.58:1** / 5.79:1 |
| `color.dark.status.skipped` | `#82878E` | 4.35:1 | `#868B91` | **4.58:1** / 4.97:1 |
| `color.light.status.queued` | `#6E7378` | 4.13:1 | `#676C71` | **4.58:1** / 5.30:1 |
| `color.light.status.blocked` | `#8A6A1F` | 4.32:1 | `#84661E` | **4.61:1** / 5.38:1 |
| `color.light.status.skipped` | `#73777B` | 4.01:1 | `#6A6D71` | **4.62:1** / 5.20:1 |

- 验证：新增 `BadgeCompositeContrastTests` 从 headless 真实渲染帧采样徽标背景像素、与解析后的
  `StatusGlyph`/标签前景计算 WCAG 对比度，覆盖 9 状态 × dark/light × standard/high-contrast，
  全部 ≥4.5:1；`R14ContractTests`/`ContrastTokenTests` 保持通过；token 生成器
  `--check` 与 ThemeEngine 内置主题基线（`newmanga-default.nmtheme`、
  `ThemeTokenBaseline.g.cs`）同步再生成。
- 证据：`verification/V11R-D-1/REVIEW-R2-DISPOSITION.md`、
  `verification/V11R-D-1/I2/badge-contrast-tests.log`。

---

## 7. D-1 I3 / r3-P1：状态徽标全部允许表面的对比度

- 日期：2026-10-30
- 裁决来源：Lead `V11R-D-1` 终审 r3 **P1**——`BadgeCompositeContrastTests` 只采样 `Bg.Panel` 父背景；
  规范/样式未限制状态文字只能落 panel，dark blocked 经 muted 合成到 `Bg.Raised` ≈4.26:1 < 4.5。
- 裁决：采用 Lead 优先方案 (a)——**提高状态前景令牌**，使"状态色经 `statusMuted` 合成到
  `bg.panel / bg.raised / bg.overlay` 三类允许表面"后均 ≥4.5:1；`statusMuted.*` 语义不变。
- 范围：标准盘 dark 7 色 + light 7 色，高对比盘 dark 4 色 + light 1 色（HC 扩展同步重生成）；
  其余令牌保持原字节。允许表面清单写入 `BadgeCompositeContrastTests.AllowedSurfaces` 并在
  `verification/V11R-D-1/I3/README.md` 说明。
- 结果：标准盘与高对比盘的状态前景在 panel/raised/overlay 三类合成背景上全部 ≥4.5:1；
  `tools/v11r/contrast-matrix.ps1` 重算后标准盘未达标行/对为 **0 / 0**。
- 验证：`BadgeCompositeContrastTests` 扩到 3 类允许表面 × 9 状态 × dark/light × standard/HC
  全绿；`R14ContractTests`/`ContrastTokenTests` 保持通过；token 生成器 `--check` 与 ThemeEngine
  内置主题基线同步再生成。
- 证据：`verification/V11R-D-1/I3/{README,badge-surface-tests.log,contrast-matrix.log,matrix.json}`。



