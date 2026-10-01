---
id: M2-QUAL-DETERM-CALIB
title: "F5 确定性 Gate 重定义落地：reading_order 对齐译文相似度口径校准（用户裁决采纳候选方案）"
kind: qualification
status: done  # DSH r1 approved_with_conditions（4×P2 Gate 定义完备性）→ 条件返修 R1-R14 全 closed（复跑逐值一致）→ r2 approved 0×新 P0/P1/P2

approval: user_ruling_2026-10-01_all_four
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-TA3-B2]
base_commit: 8e0de8d0
fork_commit: 8996ca55 # 分支实际 fork 自 release 8996ca55（e3b7c48d 的父提交即 8996ca55，dsh r1 R14 注记）
branch: agent/zcode/M2-QUAL-DETERM-CALIB
worktree: G:/CODEX/New Manga.worktrees/M2-QUAL-DETERM-CALIB-zcode
---

# M2-QUAL-DETERM-CALIB：确定性口径重定义与阈值校准

## 背景（M2-TA3-B2 F5 + 用户裁决）

TA3-B2 定案：export 复制 Run1 渲染产物；remote 翻译采样天然非逐位确定（K11 Run2 译文浮动 7/11）。「export 字节逐位一致」口径在 remote 翻译下被证伪（thresholds §5 已标 superseded-pending）。用户裁决采纳候选方案：**按 reading_order 对齐的译文相似度**重定义确定性 Gate。本 Task 落地：用已有产物校准数值+修订权威口径。

## 交付（AC）

1. **AC1 校准数据**：`experiments/M2-QUAL-DETERM-CALIB/calibrate_determinism.py`——从 `verification/M2-TA3-B/phase2/summaries/qual-K11{,.rerun}.json` 与 `qual-BJ02{,.rerun}.json` 提取两次 run 的 region 译文（按 reading_order 对齐，方法学事实：region_id 每 run 重生成），计算逐对归一相似度（Levenshtein/字符级）分布：min/median/P10/逐值清单；区分「浮动对」（7/11）与「相同对」。
2. **AC2 阈值建议**：基于分布给出 Gate 阈值建议（如 median≥0.95 且 min≥0.80——数字以实测分布为据，附推理），明确「相似度 Gate 度量的是翻译稳定性而非逐位复现」的语义边界；BJ02（该样本两次逐位相同）作为上界参照。
3. **AC3 权威口径修订**：`verification/M2-TA3-B/quality-thresholds.md` §5（双轨条目+尾注）/§7（总表第 10 行）的 superseded-pending 条目替换为新口径（相似度阈值+测量方法+语义边界），标注修订来源（本 Task+用户裁决 2026-10-01）；`phase2-plan.md` §1 交付物/§2.1 确定性复跑/§4 步骤 5 对应条目同步。（dsh r1 R11 核对：本 AC 原文「§5/§7/§1」中的 §1 经核对为**空修订面**——R9 原注只落在 §5 行、§5 尾注与 §7 行 10，§1 无 superseded-pending 条目；另 quality-report.md :189/:199 的历史 superseded-pending 引用已于 r1 返修按 R10 加关系注解除。）
4. **AC4 局限登记**：n=2 case 校准的样本量局限；Run1 层相似度未测（K11 export 差异根因未逐层隔离）；后续 qualification run 应同时落盘逐对相似度。

## 允许修改面 / 禁改面

允许：`experiments/M2-QUAL-DETERM-CALIB/**`、`verification/M2-TA3-B/**`（thresholds/plan 修订+本 Task 产物）、Task/Handoff。
禁改：`src/**`、`tests/**`、`doc/contracts/**`、`experiments/M2-TA3-A/**`、`doc/STATUS.md`、TA3-B2 已交付 run 产物 JSON（qual-*.json 等，只读）。

## 纪律

- 阈值建议必须附实测分布（不拍脑袋）；修订不动其他阶段阈值；directional 口径保留。

## 交付记录（2026-10-01，ZCode）

- 本 Task 由 ZCode 续接前一个熔断 agent 的半成品完成（半成品=未跟踪的 `experiments/M2-QUAL-DETERM-CALIB/calibrate_determinism.py` 草稿；本轮修复其 `global` 声明 SyntaxError、补浮动对子集统计（按各口径 similarity<1.0 定义）、修正合成探针判定语义（min-leg / 完整 gate 双维度）与报告推导数学）。
- AC1：`experiments/M2-QUAL-DETERM-CALIB/calibrate_determinism.py`（stdlib、确定性、fail-closed）→ `verification/M2-QUAL-DETERM-CALIB/calibration.json` + `calibration.md`。数据源只读复用 TA3-B2 产物 `qual-K11{,.rerun}.json`、`qual-BJ02{,.rerun}.json`（零改动）。
- AC2：建议 Gate（normalized 口径）= **median ≥ 0.95 且 min ≥ 0.70**。锚：K11/BJ02 实测 18 对，浮动对（normalized）6 对全部 1 编辑差、幅度 [0.75, 0.875]（K11 浮动对 min=median=0.75）；判别力以确定性合成漂移对照演示（实测分布与单字符浮动逐对 PASS；40%/70% 字符替换 FAIL、全 region 浮动 median leg FAIL）。
- AC3：`quality-thresholds.md` §5 双轨条目 + F5 修订注、§7 总表第 10 行；`phase2-plan.md` §1 交付物/§2.1 确定性复跑/§4 步骤 5——superseded-pending 解除，修订来源「M2-QUAL-DETERM-CALIB + 用户裁决 2026-10-01（全部进行）」，mock 链 export 字节逐位口径保留。
- AC4：n=2 局限、无自然 FAIL 样本、极短译文粒度边界、Run1 层相似度未测、归一化口径依赖——登记于 calibration.md §6 与 calibration.json `limitations`。
- 交接：[doc/handoffs/M2-QUAL-DETERM-CALIB-e3b7c48d.md](../handoffs/M2-QUAL-DETERM-CALIB-e3b7c48d.md)（delivery_head=e3b7c48d）；review：DeepSeek Harness（非作者）→ Codex 集成。
