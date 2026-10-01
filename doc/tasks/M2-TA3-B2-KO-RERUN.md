---
id: M2-TA3-B2-KO-RERUN
title: "TA3-B2 ko qualification 重跑（用户裁决③：TILING+ALLOC 解锁后关闭 F1/F2）"
kind: qualification
status: ready
approval: user_ruling_2026-10-02_three_confirmations
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-TA3-B2, M2-DETECT-WEBTOON-TILING, M2-IMPORT-ALLOC-LIMIT, M2-TASKS-PRIMARY-SFX-GATE]
base_commit: f99a6c55
branch: agent/zcode/M2-TA3-B2-KO-RERUN
worktree: G:/CODEX/New Manga.worktrees/M2-TA3-B2-KO-RERUN-zcode
---

# M2-TA3-B2-KO-RERUN：ko 侧 qualification 重跑

## 背景（用户裁决③）

TA3-B2 首跑 ko 9 case fail-closed 于 F1（ogkalu webtoon 0 候选）与 F2（Qt 256MB 导入上限）。两缺口已修复集成：TILING（5 页 tiling GATE PASS）+ALLOC（K07/K09/K10 导入 PASS）。**本 Task 必须在 M2-TASKS-PRIMARY-SFX-GATE 集成后启动**（pipeline plan 语义定稿后跑，避免重跑产物语义中途变更）。

## 交付（AC）

1. **AC1 重跑执行**：`experiments/M2-TA3-B/run_qualification.py` 重跑 ko 10 case（K01-K11、K19；含 K03/K06 吗——**不**，沿 case-selection 20 case 原名单的 ko 10）；ja 侧不重跑（无变化）。断点续跑语义沿用；region 策略默认无截断。
2. **AC2 结果登记**：逐 case 结果对照首跑（F1 六 case 现状/K07-K10 导入现状/K11 对照）；**诚实登记**：K19 无字页仍 fail-closed INVALID_INPUT（F4 口径未修，登记）；任何新缺陷 typed 归因。
3. **AC3 评测更新**：ko G1 CER 重算（新 OCR 结果对齐 SVG GT——TILING 后 region 几何变化，对齐脚本沿用 measure_cer.py）；SFX translation 统计（K11 的 SFX region 现经 policy=skip 应 SKIP——新增：`sfx.policy=translate` 的对照跑可选择性做一个 case 验证端到端 SFX 翻译可达性，预算内）；对白可读性工作表 ko 侧增量预填（DeepSeek 自评，预算控制）。
4. **AC4 报告**：`verification/M2-TA3-B/phase2/ko-rerun/`（summaries+评测）+ `ko-rerun-report.md`（vs 首跑对照表：F1/F2 关闭确认、CER 对比、Gate 逐项现状）；全链 Gate 现状如实（ja PASS 维持+ko 新现状）。
5. **AC5 成本与纪律**：DeepSeek key 沿用 env 注入零明文；**翻译预算控制**——ko region 总量可能数百（K01 检测解锁后 180 region），预估请求数/先行一个 case 试算后再全量；重试走生产语义；fail-closed typed；src/tests/契约零改动（发现缺陷登记）。

## 允许修改面

`verification/M2-TA3-B/phase2/**`（ko-rerun 产物+报告）、`experiments/M2-TA3-B/**`（如 run_qualification.py 需 ko-rerun 参数微调——逻辑零变更）、`verification/M2-TA3-B/quality-report.md`（追加 ko-rerun 节）、Task/Handoff。

## 禁改面

`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、首跑产物（qual-*.json 首跑版本/quality-thresholds.md）、`doc/STATUS.md`、key 明文任何形态。

## 纪律

- 依赖序：**等 M2-TASKS-PRIMARY-SFX-GATE 集成 main 后启动**（编排会话负责时序，本 Task Owner 启动前自查 main HEAD 含该 Task）。
- directional 口径延续；阈值实测 vs 提案对照沿 quality-thresholds 双轨口径（确定性=相似度 Gate for remote）。
- 环境：融合 venv 方案 A 先例（phase2/env-manifest.txt）；TILING 语义下 detect 延迟预算 awareness（K01 ~20s/页 detect+全链）。
