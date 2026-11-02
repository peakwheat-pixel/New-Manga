# FEA-06-RESIDUAL-1 AC 覆盖评估（提交给独立 Review 的现状口径）

> 评估时点：2026-11-02 深夜（DSH 实施，双 agent 额度耗尽，D-7）。最终 AC 结论以独立 impl Review + DSH 集成验证为准；本表只登记**当前可复核事实**，不预判 PASS。

| AC | 内容 | 当前评估 | 依据 |
|---|---|---|---|
| AC1 | I-1/I-2/I-9/I-10/I-12/I-13/I-14 完成；B-1/B-2/B-3/B-6/B-7 BLOCKED 登记 | **待复核（倾向 MET）** | Batch A 交付 `9337cbbe1` + 33 测试；`batch-a-verification.log`；BLOCKED 表在 Task 范围 v3 |
| AC2 | I-4 组件×状态有效属性、I-5 三态×三类×分类、I-11 焦点环/浮层焦点/Tab 序；B-5 原生 a11y BLOCKED | **PARTIAL（仅剩视觉动画/少数格子）** | I-4：Primary/Secondary/Danger/BookCard 的 normal/hover/pressed/selected + disabled 零触发 + SurfaceCard/Dialog/TabItem 有效属性 + 命令面板浮层焦点均已断言（`FluentComponentPointerStatesTests`/`FluentComponentStateEffectiveTests`/`FluentDisabledAutomationTests`/`FluentCommandPaletteFocusTests`）；仍 NOT_RUN：Toast 其余 severity 视觉、CommandPalette 结果/加载态、BookRow/disabled 视觉格。I-5：表驱动矩阵（`MotionMatrixResidualTests` 11 cells）+ nav/feedback 消费 + decorative 类别状态类；decorative 动画本体按 D-8 暂缓。I-11：2/3px、浮层焦点（设置/命令面板）、隐藏控件排除、四页各 1 场景、R3-004 Current 对照均达成 |
| AC3 | I-3 三分支 + 保存失败保护 + FEA-07 退出保护不退化；B-4 BLOCKED | **待复核（倾向 MET）** | Batch A `9337cbbe1`；`FluentResidualSettingsLeaveTests` 等；FEA-07 子集全绿 |
| AC4 | I-6 等价拆分 / I-7 opt-in / I-8 Elevation（standard+reduce 阴影不变、仅高对比回退） | **待复核（倾向 MET）** | I-6 `83fa1b186`；I-7 `ce0bee67d`（旧 PNG SHA 零漂移）；I-8 `a315bee02` + `eb13cfab0`（`HighContrastElevationFocusTests` 增加 reduce 阴影不变断言；`FluentCurrentComparisonTests` 覆盖 R3-004 Current 对照） |
| AC5 | 证据/回归基线、FEA-07 非回归、生成器、check、pins、临时根、旧证据字节不变 | **待复核（倾向 MET）** | 无过滤全量 **1195/0/57**（最新，`pre-review-verification.log` 快照 + 集成脚本 dry-run PASS）；旧 PNG 4×SHA 与 pin 一致；TokenGen/ThemeGen `--check` 0；check PASS(3)；pins 15/15；测试均临时根 |

## 阻塞/待裁决与恢复条件

- **B-5/D-1**：原生 200% DPI、原生桌面、原生 a11y、原生截图 —— 无硬件；恢复条件：硬件可用或用户书面 waiver。不因此伪造证据。
- **D-7**：双 agent 额度耗尽期间由 DSH 实施、Review 后补（已记录 checkpoint §81/§83.1）。
- **D-8**：decorative 三类视觉动画暂缓，转后续视觉任务（ZCode 主责）；理由见 Task「待裁决」区。
- **独立 impl Review**：prompt 已备（workspace `impl-review-prompt.md`）；待 Codex（00:23）或 ZCode（03:02）恢复后派发。

## 回归计数口径

- pre-I-7 安全回归（排除 PNG 用例）：**1137/0/57**。
- I-7 后无过滤全量起点：**1138/0/57**；Batch A +33、Batch B 追加：当前无过滤全量 **1195/0/57**（只增不减）。
