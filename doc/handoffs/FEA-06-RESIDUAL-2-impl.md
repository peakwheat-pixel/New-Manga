# FEA-06-RESIDUAL-2 实施 Handoff（DSH 收尾，2026-11-03 05:18）

## 范围与状态
- Task `doc/tasks/FEA-06-RESIDUAL-2.md`（scope v3 已冻结，scope-r3 approved）；当前 `in_progress`，impl-r1 复核 changes_requested（报告 `doc/reviews/FEA-06-RESIDUAL-2-impl-r1.md`）。
- 本切片交付：IN-1 装饰动画、IN-2A 有效属性断言、IN-2B 像素证据（含 R2 返修），DSH 在 Codex/ZCode 额度窗口不可用期间按 D-7 实施，后续须独立 impl-r2 Review（实施会话不得自审）。

## 提交
- `d854d91b2` IN-1（shelf 渐变 8s、reader 粒子 400ms、三态降级/暂停/无泄漏、12 测试）
- `1d2df1d15` IN-2A（16+1 组有效属性、派生控件 class-only 选择器修复、coverage 同步、14→15 测试）
- `998d75bdb` / `bfacfe09c` / `21e305249` / `9f5723cb0` / `7e21b4de8` / 本轮 IN-2B 与 R2 返修（真实 themes、inventory head、日志格式、Slider thumb、SurfaceCard/IconButton 状态通道）
- 本轮最新：R2-001 **真实 decor 帧**（5 张，ManualFluentMotionClock 驱动产品装饰层：shelf first/mid/reduce、粒子 mid/reduce）+ `FluentResidual2DecorativeTests.Decor_Frames_Are_Captured_Only_When_Opted_In`。

## 验证（最新）
- build 0/0；无过滤全量 **1274 passed / 0 failed / 57 skipped**（App 640、DesignSystem 112）。
- `NEWMANGA_CAPTURE_RESIDUAL2_PNGS=1` 生成 `verification/FEA-06-RESIDUAL-2/visuals/**`：pages 8（真实 light/dark）、components 19、decor 5 + `visual-inventory.md`（含 head 列）；默认运行零仓库写入；旧 `verification/FEA-06/**` PNG SHA 不变。
- `expected-tokens.md` 在库；check.ps1 PASS；verify_pins 15/15。

## 限制与未完成
- **D-14（待裁决）**：`StatusCatalog.ColorKey(NotStarted)` = Text.Disabled 与 `Controls.Status.axaml` = Text.Secondary 冲突；测试按样式权威断言并特判，未写达成。
- 组件像素格 theme 标注为 `current`（headless 下组件窗口 palette 解析不随 variant 改变；页面为真实 light/dark）。
- 逐图 `signed_by` 仍待独立 Reviewer 签署（未签署 = NOT_RUN）。
- OUT/BLOCKED（loading/Dialog 危险/加载、数据端口格、B-5/D-1）未写达成。
- 未 push。

## 交接要求
1. 独立 impl-r2 Review（fresh 上下文）逐图签署并核验 R2 findings 处置；
2. Reviewer 通过后 DSH 集成验证（integration-verify 等价命令）→ Task done/closed_with_limitations；
3. ZCode 08:05 备用；D-14 需 DSH 裁决后另行修复（超本卡 allowed_paths）。
