# FEA-06-RESIDUAL-1 Handoff（Batch B 部分交付，2026-11-02）

> 事实以 Git 与仓库文件为准。实现执行：DSH（双 agent 额度耗尽，按 D-7 推荐口径）；独立 impl Review 待 Codex（约 00:23）或 ZCode（约 03:02）恢复后补做。

## 1. 交付指针

| 项 | 值 |
|---|---|
| Task | `doc/tasks/FEA-06-RESIDUAL-1.md` — `in_progress`，范围 v3 冻结 |
| base_commit | `82529a3d5864a39f362e414b67bca774d743f862` |
| Batch A | `83fa1b186`（I-6）+ `9337cbbe1`（I-1/I-2/I-3/I-9/I-10/I-12/I-13/I-14） |
| I-7 | `ce0bee67d`（PNG opt-in） |
| Batch B | 见 Batch B commit（I-5/I-8/I-11 + I-4 声明覆盖 + 设计规则对齐） |
| 证据 | `verification/FEA-06-RESIDUAL-1/batch-a-verification.log`、`batch-b-verification.log` |
| 全量 | **1177 passed / 0 failed / 57 skipped**（无过滤；PNG 用例默认零写入，旧 pin 字节不变） |
| 治理 | build 0/0；TokenGen/ThemeGen `--check` up-to-date；check PASS(3)；pins 15/15 |

## 2. 本批完成

- **I-5**：`MotionTimings` 冻结参数表（02-motion §2）+ FluentShellSurface 消费 navigation 页面过渡（240ms）与运行时设置变更重放（Dispatcher 编组）；reduce/category-off → 无过渡。
- **I-8**：`Nm.Elevation.*` 消费（card/detail=1、drawer=2、dialog=3）；高对比运行时注入 `Nm.Border.Focus=3px` + Elevation 置空（1px 边框仍在），standard/reduce 阴影不变；生成文件与 Current V2 零改动。
- **I-11（部分）**：焦点环 2px→高对比 3px（测试断言 ring 几何）；设置页离开浮层焦点移入/取消返还（DSH 补）；隐藏控件 Tab 序未单测。
- **I-4（部分）**：组件×状态声明覆盖测试（primary/secondary/danger/book-card/book-row/space-button/command-row 的 hover/pressed/disabled + surface/detail/dialog/drawer）；`DesignRulesTests` “禁止阴影”旧规则更新为只允许 `DynamicResource Nm.Elevation.*`（与冻结设计 01 §2.3 对齐）。

## 3. 未完成 / NOT_RUN（诚实记录）

- I-4 其余组件状态未逐一补齐：IconButton、ToggleSwitch、Slider、SegmentedControl、TabStrip、SearchField、CommandPalette、ContextMenu、Tooltip、Toast/InfoBar、BatchMatrix/RunProjectionBar；hover/pressed 视觉未截图（headless 伪类渲染不可靠），仅声明覆盖 + 功能态。
- I-11：隐藏/不可见控件移出 Tab 序未加显式断言。
- I-5：feedback/decorative 的实际动画消费未接入（表已覆盖）。

## 4. 下一步

1. agent 恢复后派 fresh 独立 impl Review（Codex 优先，否则 ZCode），覆盖 Batch A/I-7/Batch B 全部 commits 与本 handoff/证据；P0/P1 处置 → DSH 集成验证。
2. 续做 I-4 剩余组件状态 + I-11 Tab 序断言 + I-5 feedback/decorative 消费；然后重跑全量/证据/Handoff。
3. 全部完成后：DSH 集成验证（build/全量/生成器/治理/pins/证据索引）→ 按实际 AC 结果 done 或 closed_with_limitations；BLOCKED B-1…B-7 保持。
