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


## 当前快照（R2-005，2026-11-03）

> 本节取代前文“当前/最新”口径；前文及其1194/1195/1197等计数全部保留为历史快照，不自动升级为当前证据。历史impl-r2基线为 **1213/0/57**；本轮最新为 **1233/0/57**。
> 被测实现 head：`8b39b13982cfaae9e7606fe62f13353700be68fe`（`8b39b1398`）；后续交付只追加证据/Handoff，不改源码测试字节。证据：`impl-r2-rework-verification.log`；四条验收命令原文/输出/EXIT及57条skip逐项原因均在其中。
> build / 无过滤全量test / check.ps1 / verify_pins.ps1：**EXIT=0 / 0 / 0 / 0**；check PASS(3既有warnings)，pins **15/15**；TokenGen/ThemeGen --check 均EXIT=0。App=614/0/7、DesignSystem=97/0/0；合计1233 passed / 0 failed / 57 skipped（总1290），比基线+20（App+16、DS+4）。

| 子项 | 当前实现/证据事实 | 当前限制 |
|---|---|---|
| I-1 / I-2 | 页面memento、分栏/约束/键盘既有回归通过 | 未新增持久化 |
| I-3 | 三分支、失败保护、Reader导航不绕过确认、分层Esc既有回归通过；Settings两类浮层200/160ms新增断言 | B-4不算完成 |
| I-4 | 已有有效属性、真实指针态、disabled自动化零触发、命令面板结果/空态与焦点断言；新增Providers/Backup/Workbench重建后的真实hover/pressed | PARTIAL；loading/checked及其余状态格NOT_RUN详见组件矩阵 |
| I-5 | Reader淡出与分类、四种页面浮层200/160、hover120/pressed90/badge150消费及运行时降级、排队回调失效均有行为断言 | PARTIAL；D-8待处置，decorative三类本体未实现 |
| I-6 | 原拆分提交83fa1b186及等价证据保留，旧测试未删除 | 本轮不重新移动VM |
| I-7 | 全量包含默认内存渲染用例；四张旧PNG逐字节与base相同 | 本轮opt-in NOT_RUN；不重写旧采证 |
| I-8 | standard/reduce阴影、高对比回退与Current往返既有断言通过 | 原生像素视觉NOT_RUN |
| I-9 | dirty状态点150ms过程及设置/工作台既有断言通过 | 原生视觉NOT_RUN |
| I-10 | 顶/底160ms过程、最后真实press/release/wheel/handled键后2s、中心点击释放保持切换、detach停止计时均已验证；侧栏原语义保留 | 全屏/原生视觉沿用原有限制，未凭headless计原生PASS |
| I-11 | R2-006几何修复现已验证：Fluent offset=1，2/3px实时stroke、四边gap与滚动裁剪；Current默认offset=0 | 不再将旧stroke-only证据称完整I-11达成；整体待独立复核，完整Tab遍历/原生a11y仍NOT_RUN |
| I-12 / I-13 / I-14 | Console入口、九行骨架、源不可用只读警示既有断言通过 | 内容/Run投影/恢复动作仍分别由B-1/B-2/B-3/B-6承接 |

当前NOT_RUN：上述I-4未断言格、完整Tab遍历、原生视觉/DPI/a11y、最新opt-in采证。D-8待DSH独立裁决，未转成“完成”。新矩阵和本日志为当前事实；前文“全部完成/最新1195”等只属历史叙述。Task/STATUS/PLAN及Canonical Evidence登记由DSH更新，本实施者遵守本轮写域未改它们。
