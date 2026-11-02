# FEA-06-RESIDUAL-1 当前证据索引（impl-r4 approved 后，取代旧“当前”入口；旧文件字节保留）

> 本文件是 **R4-001 处置** 追加的当前证据入口，不覆盖任何历史日志/Review/pin。
> 旧证据（`batch-a-verification.log`、`batch-b-verification.log`、`pre-review-verification.log`、`component-state-matrix.md`、`ac-coverage.md`、`item-status.md`）保留原字节，其正文中的计数/head 视为历史快照。

## 最新事实
| 项 | 值 |
|---|---|
| approved Review | `doc/reviews/FEA-06-RESIDUAL-1-impl-r4.md` — **approved，P0=0/P1=0/P2=1**（reviewed_head `669a4ae02`，implementation_head `3c3afe170`，session `01a19d7c-…`） |
| 生产 head | `3c3afe170`（R3-001 Reader 中部点击双向显隐） |
| 交付/证据 head | `669a4ae02`（验证日志 + Handoff） |
| 集成验证 | `verification/FEA-06-RESIDUAL-1/integration-verification.log`（DSH 本轮运行，contents 见该文件） |
| 全量 | **1245 passed / 0 failed / 57 skipped**（App.Tests 626；其余程序集见集成日志） |
| 基线 | 1137（pre-I-7 安全口径）→ 1138（I-7 后）→ Batch A/B/R 系列递增至 1245，只增不减 |
| 旧 FEA-06 PNG | 4×SHA 与 pin 一致（reader `8533c2…`/settings `fd30b1…`/shelf `307f8f…`/workbench `d5d878…`） |
| 生成器/治理 | TokenGen/ThemeGen `--check` EXIT=0；check.ps1 PASS(3)；verify_pins 15/15 |

## 历史快照（勿当最新）
- `batch-a-verification.log`（9337cbbe1，1170/0/57）与 `batch-b-verification.log`（1198 前后增量记录）：历史批次记录，最终计数以本文件/集成日志为准。
- `pre-review-verification.log`（84abc9c71，1194/0/57）：impl-r1 前快照。
- `component-state-matrix.md` / `ac-coverage.md` / `item-status.md`：保留历史内容；当前 AC/组件口径以下方及 Task 为准。
- `verify-r2-evidence.py`：R2 历史证据审计脚本（固定 8b39b1398/1233），仅作历史审计，不作为当前入口。

## 当前 AC 评估（待 DSH 集成处置）
- AC1（I-1/2/9/10/12/13/14 + BLOCKED 登记）：实现与回归齐备，B-1/2/3/6/7 按 BLOCKED 登记 → 倾向 MET。
- AC2：I-5（三态×三类矩阵、nav/feedback/decorative 消费、动画时序）、I-11（焦点环 2/3px、offset=1、浮层焦点、四页场景、Current 对照）已达成；I-4 hover/pressed/disabled/命令面板等有效属性已断言；**剩余 NOT_RUN**：I-4 少数纯视觉状态格、D-8 decorative 视觉动画（转 ZCode 视觉任务）、B-5 原生 a11y → **PARTIAL**。
- AC3（I-3 三分支/失败保护/FEA-07 退出保护）：回归齐备 → 倾向 MET；B-4 BLOCKED。
- AC4（I-6 等价拆分/I-7 opt-in/I-8 Elevation+高对比+Current 对照）：齐备 → 倾向 MET。
- AC5（证据/回归/生成器/治理/pins/临时根/旧字节不变）：本文件 + integration log 支撑 → 倾向 MET。
- BLOCKED：B-1/2/3/4/5/6/7（D-1 无硬件等），不写达成。
- 待裁决：D-7（已完成执行口径）、D-8、D-10（已完成 Codex 交付；ZCode 视觉复核保留）。
