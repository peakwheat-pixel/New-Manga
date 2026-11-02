# FEA-06-RESIDUAL-1 子项状态台账（I-1…I-14，供独立 Review / 集成验证）

> 事实来源：Git 提交、各验证日志、测试源码。row 的「状态」只表示**当前可复核实现/证据**，最终 AC 以独立 Review + DSH 集成验证为准。BLOCKED 子项（B-1…B-7）不在此表，见 Task 范围 v3 §B。

| 子项 | 内容摘要 | 交付 commit | 主要断言/测试 | 状态 | 缺口 / NOT_RUN |
|---|---|---|---|---|---|
| I-1 | Fluent 页面级 UI memento（塌陷/滚动/选中，运行期 frontend 切换与页面往返） | `9337cbbe1` | `FluentResidualBatchATests`（memento 恢复、新窗口默认、无数据文件写临时根） | 完成 | 无（未落盘为设计约束） |
| I-2 | Shelf/Workbench 分栏折叠（按钮/分隔约束/键盘联动 memento） | `9337cbbe1` | Batch A tests（点击/键盘/0 宽/约束/恢复） | 完成 | 无 |
| I-3 | 设置页离开三分支 + 保存失败保护 + Esc 优先级 | `9337cbbe1` | `FluentResidualSettingsLeaveTests`（三分支/失败留页留稿/退出保护） | 完成 | 无 |
| I-4 | 组件 full 状态矩阵（有效属性/命令/浮层开合） | `a315bee02`、`6edf24904`、`922a116ca`、`60fd4fe56`、`3e879fba1`、`b79241c9a`、`981719a13` | `FluentComponentStateEffectiveTests`（Primary/Danger/SurfaceCard/Dialog/TabItem）、`FluentComponentPointerStatesTests`（Primary/Secondary/Danger/BookCard hover/pressed/selected）、`FluentDisabledAutomationTests`（disabled 零触发）、`FluentCommandPaletteFocusTests`（浮层焦点）、`I11_LeaveOverlay...` | **部分（仅剩少数视觉/NOT_RUN 格）** | 仍 NOT_RUN：Toast 其余 severity 视觉、CommandPalette 结果/加载态、BookRow/disabled 视觉；矩阵见 `component-state-matrix.md` |
| I-5 | motion 三态×三类×分类矩阵 + 消费 | `a315bee02`、`918e4a2e3`、`7ca725bbf`、`eb13cfab0` | `MotionTimings` 表 + `MotionMatrixResidualTests`（11 cells）、`FluentMotionResidualTests`（nav/feedback 过渡、运行时重放、decorative 状态类） | **部分（decorative 动画本体暂缓 D-8）** | 表/开关/reduce 禁用语义与类别状态类已覆盖；渐变循环/翻页粒子/空态漂浮等视觉动画本体未实现（D-8） |
| I-6 | 四 Fluent VM 拆分（1408 行→四文件+基类） | `83fa1b186` | 既有测试不改弱 + 全量不退化 | 完成 | 无 |
| I-7 | PNG 采证显式 opt-in（默认零仓库/证据面写入） | `ce0bee67d` | `FluentPages_RenderHeadlessPngEvidence`（默认帧断言零写入；opt-in 写本卡 png/）；旧 pin SHA 对照 | 完成 | 无 |
| I-8 | `Nm.Elevation.*` 消费 + 高对比回退（standard/reduce 阴影不变；仅高对比 1px 边框） | `a315bee02` | `HighContrastElevationFocusTests`（standard 阴影非空/high contrast 置空且 hairline 保留）；生成 token 文件与 V2 零改动 | 完成 | 像素级视觉对比 NOT_RUN（headless 属性级断言） |
| I-9 | 未保存 dirty 圆点（设置/工作台可见状态） | `9337cbbe1` | Batch A tests（dirty true/false、切前端往返） | 完成 | 无 |
| I-10 | Reader 顶/底条 2s 淡出、点击中部切换、reduce 直接切换；右侧条常显可隐藏 | `9337cbbe1` | Batch A tests（R3-003 两类条语义） | 完成 | 右侧条逐像素视觉验收 NOT_RUN（状态语义已断言） |
| I-11 | 焦点环 2px/offset 1/高对比 3px；浮层焦点移入/返还；隐藏控件出 Tab 序；四页各 1 场景；Current 对照 | `a315bee02`、`6edf24904`、`9203c0031`、`981719a13`、`c2d4ce4b6` | `FocusRingHighContrastTests`、`I11_LeaveOverlay...`、`FluentCommandPaletteFocusTests`、`FocusOrderResidualTests`、`FluentFocusPageCoverageTests`、`FluentCurrentComparisonTests` | 完成 | 隐藏控件 Tab 序为「不可聚焦」语义断言（未做完整 Tab 遍历序列） |
| I-12 | Console 空间入口导航 + 错误卡控制台入口；占位诚实 | `9337cbbe1` | Batch A tests（导航/可达/占位无假数据） | 完成 | 控制台内容投影仍 B-1/B-6 BLOCKED（不属本项） |
| I-13 | 工作台 9 行状态视觉骨架（只读/错误/控制台入口态） | `9337cbbe1` | Batch A tests（9 行视觉/禁用/空态） | 完成（视觉骨架） | 数据绑定仍 B-2 BLOCKED |
| I-14 | 源不可用只读警示 banner/文案/禁用操作 | `9337cbbe1` | Batch A tests（警示可见/禁用态） | 完成 | 恢复动作仍 B-3 BLOCKED（不属本项） |

## 当前 AC 映射（沿用 `ac-coverage.md`，此处仅索引）

- AC1 ← I-1/I-2/I-9/I-10/I-12/I-13/I-14（均完成）＋ B-1/B-2/B-3/B-6/B-7 登记。
- AC2 ← I-4（部分）/I-5（部分，D-8）/I-11（完成）＋ B-5 登记。
- AC3 ← I-3（完成）＋ B-4 登记。
- AC4 ← I-6/I-7/I-8（完成）。
- AC5 ← 全量/生成器/治理/pins/临时根/旧证据字节（见 `batch-a-verification.log`、`batch-b-verification.log`）。

## 全量与基线

- 最新无过滤全量：**1195 passed / 0 failed / 57 skipped**（DS 93 + App 580；预复核快照与集成脚本 dry-run 均 PASS）。
- pre-I-7 安全基线 1137/0/57 → I-7 后起点 1138/0/57 → Batch A +33 → Batch B 追加（I-4/I-5/I-11 等）只增不减。
- 旧 `verification/FEA-06/screens/**` 字节零漂移（每次全量后 `git status` 核对）。
