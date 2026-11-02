# FEA-06-RESIDUAL-1 AC 覆盖评估（提交给独立 Review 的现状口径）

> 评估时点：2026-11-02 深夜（DSH 实施，双 agent 额度耗尽，D-7）。最终 AC 结论以独立 impl Review + DSH 集成验证为准；本表只登记**当前可复核事实**，不预判 PASS。

| AC | 内容 | 当前评估 | 依据 |
|---|---|---|---|
| AC1 | I-1/I-2/I-9/I-10/I-12/I-13/I-14 完成；B-1/B-2/B-3/B-6/B-7 BLOCKED 登记 | **待复核（倾向 MET）** | Batch A 交付 `9337cbbe1` + 33 测试；`batch-a-verification.log`；BLOCKED 表在 Task 范围 v3 |
| AC2 | I-4 组件×状态有效属性、I-5 三态×三类×分类、I-11 焦点环/浮层焦点/Tab 序；B-5 原生 a11y BLOCKED | **PARTIAL（impl-r1 changes_requested 返修中）** | I-4：Primary/Secondary/Danger/BookCard 的 normal/hover/pressed/selected + disabled 零触发 + SurfaceCard/Dialog/TabItem 有效属性 + 命令面板浮层焦点均已断言（`FluentComponentPointerStatesTests`/`FluentComponentStateEffectiveTests`/`FluentDisabledAutomationTests`/`FluentCommandPaletteFocusTests`）；仍 NOT_RUN：Toast 其余 severity 视觉、CommandPalette 结果/加载态、BookRow/disabled 视觉格。I-5：表驱动矩阵（`MotionMatrixResidualTests` 11 cells）+ nav/feedback 消费 + decorative 类别状态类；decorative 动画本体按 D-8 暂缓。I-11：2/3px、浮层焦点（设置/命令面板）、隐藏控件排除、四页各 1 场景、R3-004 Current 对照均达成 |
| AC3 | I-3 三分支 + 保存失败保护 + FEA-07 退出保护不退化；B-4 BLOCKED | **待复核（倾向 MET）** | Batch A `9337cbbe1`；`FluentResidualSettingsLeaveTests` 等；FEA-07 子集全绿 |
| AC4 | I-6 等价拆分 / I-7 opt-in / I-8 Elevation（standard+reduce 阴影不变、仅高对比回退） | **待复核（倾向 MET）** | I-6 `83fa1b186`；I-7 `ce0bee67d`（旧 PNG SHA 零漂移）；I-8 `a315bee02` + `eb13cfab0`（`HighContrastElevationFocusTests` 增加 reduce 阴影不变断言；`FluentCurrentComparisonTests` 覆盖 R3-004 Current 对照） |
| AC5 | 证据/回归基线、FEA-07 非回归、生成器、check、pins、临时根、旧证据字节不变 | **待复核（倾向 MET）** | 无过滤全量 **1197/0/57**（最新，`pre-review-verification.log` 快照 + 集成脚本 dry-run PASS）；旧 PNG 4×SHA 与 pin 一致；TokenGen/ThemeGen `--check` 0；check PASS(3)；pins 15/15；测试均临时根 |

## 阻塞/待裁决与恢复条件

- **B-5/D-1**：原生 200% DPI、原生桌面、原生 a11y、原生截图 —— 无硬件；恢复条件：硬件可用或用户书面 waiver。不因此伪造证据。
- **D-7**：双 agent 额度耗尽期间由 DSH 实施、Review 后补（已记录 checkpoint §81/§83.1）。
- **D-8**：decorative 三类视觉动画暂缓，转后续视觉任务（ZCode 主责）；理由见 Task「待裁决」区。
- **独立 impl Review**：prompt 已备（workspace `impl-review-prompt.md`）；待 Codex（00:23）或 ZCode（03:02）恢复后派发。

## 回归计数口径

- pre-I-7 安全回归（排除 PNG 用例）：**1137/0/57**。
- I-7 后无过滤全量起点：**1138/0/57**；Batch A +33、Batch B 追加：当前无过滤全量 **1195/0/57**（只增不减）。


## 当前快照（R2-005，2026-11-03）

> 本节取代前文“当前/最新”口径；前文及其1194/1195/1197等计数全部保留为历史快照，不自动升级为当前证据。历史impl-r2基线为 **1213/0/57**；本轮最新为 **1233/0/57**。
> 被测实现 head：`8b39b13982cfaae9e7606fe62f13353700be68fe`（`8b39b1398`）；后续交付只追加证据/Handoff，不改源码测试字节。证据：`impl-r2-rework-verification.log`；四条验收命令原文/输出/EXIT及57条skip逐项原因均在其中。
> build / 无过滤全量test / check.ps1 / verify_pins.ps1：**EXIT=0 / 0 / 0 / 0**；check PASS(3既有warnings)，pins **15/15**；TokenGen/ThemeGen --check 均EXIT=0。App=614/0/7、DesignSystem=97/0/0；合计1233 passed / 0 failed / 57 skipped（总1290），比基线+20（App+16、DS+4）。

| AC | 当前事实与判定 | 未完成/限制 |
|---|---|---|
| AC1 | IN范围既有功能回归通过；R2-001/003的Reader顶/底淡出、导航分类与最后交互后2s由真实输入/可控时钟断言 | 整体PARTIAL：B-1/B-2/B-3/B-6/B-7仍BLOCKED；不由测试总数推导完整产品AC |
| AC2 | R2-001/002/004/006已实现并有过程/中间值/生命周期/几何断言，等待上下文独立impl-r3复核 | PARTIAL：I-4剩余NOT_RUN格；D-8待独立裁决、decorative本体未实现；B-5原生a11y仍BLOCKED |
| AC3 | 设置三分支、保存失败保护、导航/Esc优先级及FEA-07退出保护现有断言通过 | 完整AC仍有B-4真实数据端口限制 |
| AC4 | I-6等价拆分既有证据保留；I-7默认内存渲染用例运行、旧四PNG字节不变；I-8 standard/reduce阴影与高对比回退既有断言通过 | 最新PNG opt-in采证NOT_RUN；旧opt-in成功仅为历史，不替代原生视觉验收 |
| AC5 | 本轮无过滤1233/0/57、生成器/治理/pins实跑通过；当前三表一致，57skip逐条原因与历史字节审计可复现 | 仍需DSH派独立Review及集成验证，不能以本实施者自测关闭Task |

D-8仍为**待DSH处置/独立Review确认**的建议；没有批准暂缓或完成decorative。B-1…B-7的依赖/恢复条件沿用Task范围v3；B-5需硬件可用或用户书面waiver。本轮NOT_RUN还包括200% DPI、原生桌面、原生a11y、逐像素视觉矩阵及PNG opt-in；I-4普通headless可验证格的未覆盖另见组件矩阵，不能统称硬件阻塞。

回归链：1137/0/57（pre-I-7过滤PNG）→1138/0/57（恢复全量）→历史批次→1213/0/57（impl-r2基线）→**1233/0/57（本轮无过滤）**。`pre-review-verification.log`保留其原始1194快照，不支撑“最新1197/1213/1233”的声明。
