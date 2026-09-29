---
id: M2-DOCTR-QUAL-RUN
title: "Real docTR 正式 qualification run（用户口径裁决 2026-09-30：coverage 主判定 + 生产 pad 正式 + Precision 下界不作 Gate）"
kind: acceptance
status: ready
approval: user_ruling_2026-09-30
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（待派发，非作者静态）
depends_on: []
base_commit: PENDING_SET_AT_CLAIM
branch: agent/zcode/M2-DOCTR-QUAL-RUN
worktree: G:/CODEX/New Manga.worktrees/M2-DOCTR-QUAL-RUN-zcode
integration_commit: null
---

# M2-DOCTR-QUAL-RUN：Real docTR 正式 qualification run

## 来源与目标

- 用户裁决 2026-09-30：①主判定 coverage；②pad 以生产原样 6px 为正式结果、附报抵消 pad 数据；③Precision 仅作受污染观测下界、**不作 Gate**；④按此完成正式 qualification 与独立 Review，并根据结果进入检测器调参/更换模型候选流程。
- 前置：M2-DOCTR-QUAL-PREFLIGHT `done` @`51229d49`（评测基座、权重、GPU 环境、首跑基线全部就绪）。
- 一个可观察的交付结果：按冻结口径的**正式 qualification 报告**（PASS/FAIL per Gate + 全部观测指标 + 调参/换模型候选评估建议），入 `verification/M2-DOCTR-QUAL/qualification/`。

## 冻结口径（thresholds.json @本 Task 版本，用户裁决落字）

- **Gate**（主判定层 = block_coverage，生产合并块，生产 pad 6px）：Recall ≥ 0.92；Mean coverage ≥ 0.60；严重整页漏检率 ≤ 0.05。
- **非 Gate 观测**（必须报告，不参与判定）：Precision（受污染下界，参考值 0.85）、block_strict（IoU 字面口径）、pad 抵消（收缩 6px）诊断、db_resnet50 对照、raw_strict 词级诊断。
- 检测 only；recognition 永不参与判定。

## Acceptance Criteria

- [ ] AC1（正式主跑）：GPU venv 下按 manifest `eval-manifest.full.seg05.json` 全量 511 regions 复跑 `eval_detection.py --arch fast_base --device cuda`，产出正式主结果（主判定层 Gate 三项逐项 PASS/FAIL）。
- [ ] AC2（附报诊断）：pad 抵消（`--strip-block-pad 6.0`）与 block_strict/raw_strict 观测值入报告；db_resnet50 对照（复跑 seg05 全量）入报告。
- [ ] AC3（正式报告）：`verification/M2-DOCTR-QUAL/qualification/qualification-report.md` —— Gate 判定表、观测表、与首跑基线/preflight 的一致性核对、**调参/换模型候选流程建议**（FAST box_thresh/warmup 调参扫描、DBNet 评估、GT 补盲区）。
- [ ] AC4（可复现）：报告引用的全部 results JSON 带 manifest_sha256 指纹；复现命令入 README。
- [ ] AC5（范围纪律）：diff 仅 experiments/M2-DOCTR-QUAL/**（报告脚本可选新增）+ verification/M2-DOCTR-QUAL/qualification/**；生产 src/requirements 零改动。

## 允许修改范围

- `experiments/M2-DOCTR-QUAL/**`（可新增报告汇总脚本，不改已集成评测逻辑）
- `verification/M2-DOCTR-QUAL/qualification/**`、本 Task、Handoff

## 禁止范围

- `src/**`、`requirements*.txt`、`apps/**`、`packaging/**`、生产 merge 常数与 wire 行为
- 不宣称检测器调参/换模型实施（那是根据本 Task 结论的后续 Task，须另行释放）

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 主跑 | eval_detection.py fast_base cuda（seg05 全量） | GPU venv + 权重快照 | NOT_RUN | 待入 qualification/ |
| AC2 附报 | --strip-block-pad 6.0 变体 + db_resnet50 对照 | GPU venv | NOT_RUN | 待入 qualification/ |
| AC3 报告 | 汇总脚本 + qualification-report.md | — | NOT_RUN | 待入 qualification/ |

## 依赖、风险与阻塞

- 依赖：无（preflight 已 done）。
- 风险：预期结果为 **FAIL**（首跑 Recall ≤0.48 << 0.92）——这正是正式结论，触发"调参/换模型候选流程"，不得为凑 PASS 调整口径或数据。
- 阻塞：无。

## 交付与运行记录

- Handoff：尚无。Review：尚无。实际测试：尚无。
