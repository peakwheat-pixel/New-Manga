---
id: M2-DOCTR-QUAL-RUN
title: "Real docTR 正式 qualification run（用户口径裁决 2026-09-30：coverage 主判定 + 生产 pad 正式 + Precision 下界不作 Gate）"
kind: acceptance
status: done
approval: user_ruling_2026-09-30
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（待派发，非作者静态）
depends_on: []
base_commit: 5b3a477a371a662288998f86d23ae56439179524
branch: agent/zcode/M2-DOCTR-QUAL-RUN
worktree: G:/CODEX/New Manga.worktrees/M2-DOCTR-QUAL-RUN-zcode
integration_commit: e8c9c120a5bb3c71ab3f41c32b4985f7578aef61
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

- [x] AC1（正式主跑）：GPU venv 下按 manifest `eval-manifest.full.seg05.json` 全量 511 regions 复跑 `eval_detection.py --arch fast_base --device cuda`，产出正式主结果（主判定层 Gate 三项逐项 PASS/FAIL）。
- [x] AC2（附报诊断）：pad 抵消（`--strip-block-pad 6.0`）与 block_strict/raw_strict 观测值入报告；db_resnet50 对照（复跑 seg05 全量）入报告。
- [x] AC3（正式报告）：`verification/M2-DOCTR-QUAL/qualification/qualification-report.md` —— Gate 判定表、观测表、与首跑基线/preflight 的一致性核对、**调参/换模型候选流程建议**（FAST box_thresh/warmup 调参扫描、DBNet 评估、GT 补盲区）。
- [x] AC4（可复现）：报告引用的全部 results JSON 带 manifest_sha256 指纹；复现命令入 README。
- [x] AC5（范围纪律）：diff 仅 experiments/M2-DOCTR-QUAL/**（报告脚本可选新增）+ verification/M2-DOCTR-QUAL/qualification/**；生产 src/requirements 零改动。

AC5 owner 自评注记：除上述范围外，另有一个已披露的契约适配 commit `f9894184`（`eval_detection.py` verdict 段按冻结 gates 契约读取 + Precision 非 Gate + `--task` 元数据参数）——属"已集成评测文件"的最小必要修改，根因是裁决 commit `7b17e02d` 改写 thresholds.json 后 runner 未同步（首跑崩溃证据 qualification/raw/formal-run1-fast_base-cuda-seg05.log EXIT=1）；测量逻辑零改动，三组一致性自检证明 summary/per_region 与 preflight 首跑逐字段一致。交 Codex 复核裁定。

## 允许修改范围

- `experiments/M2-DOCTR-QUAL/**`（可新增报告汇总脚本，不改已集成评测逻辑）
- `verification/M2-DOCTR-QUAL/qualification/**`、本 Task、Handoff

## 禁止范围

- `src/**`、`requirements*.txt`、`apps/**`、`packaging/**`、生产 merge 常数与 wire 行为
- 不宣称检测器调参/换模型实施（那是根据本 Task 结论的后续 Task，须另行释放）

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 主跑 | eval_detection.py fast_base cuda（seg05 全量） | GPU venv + 权重快照 | RUN：Gate FAIL（Recall 0.4776<0.92；MeanCov 0.7531 PASS；severe 0.0385 PASS）；EXIT=0，22.2s | qualification/results-formal-fast_base-cuda-seg05.json + raw/formal-run2-*.log |
| AC2 附报 | --strip-block-pad 6.0 变体 + db_resnet50 对照 | GPU venv | RUN：pad 抵消 Recall 0.2628 / block_strict 0.4515（主跑口径）/ raw_strict 0.1941；db_resnet50 Recall 0.6085、severe 0.0192；均 EXIT=0 | qualification/results-formal-*-padoffset.json、results-formal-db_resnet50-cuda-seg05.json、raw/formal-run3-*/run4-*.log |
| AC3 报告 | 汇总脚本 + qualification-report.md | — | RUN：报告 + consistency-and-summary.json 入库；三组一致性 deterministic_reproduction=true（summary/per_region 0 diff） | qualification/qualification-report.md、consistency-and-summary.json |
| 附加：确定性自检 | summarize_qualification.py（对比 preflight 首跑） | 主仓 verification 只读 | RUN：fast_base / db_resnet50 / pad 抵消 三组均 0 diff | consistency-and-summary.json §consistency |

## 依赖、风险与阻塞

- 依赖：无（preflight 已 done）。
- 风险：预期结果为 **FAIL**（首跑 Recall ≤0.48 << 0.92）——这正是正式结论，触发"调参/换模型候选流程"，不得为凑 PASS 调整口径或数据。**已按预期发生**（正式 Recall 0.4776，Formal Result: FAIL），候选流程建议已入报告 §7。
- 阻塞：无。

## 交付与运行记录（终态）

- **正式结论（Formal Result: FAIL）**：Gate（block_coverage，生产 pad 6px）：Recall **0.4776** < 0.92 **FAIL**、Mean coverage 0.7531 PASS、severe 0.0385 PASS；Precision 0.1250=受污染观测下界（非 Gate）。附报：pad 抵消 Recall 0.2628、block_strict 0.4515、db_resnet50 0.6085、raw_strict 0.1941。
- **集成（2026-09-30，Codex 代行）**：merge=`e8c9c120`；[integration record](../../verification/M2-DOCTR-QUAL/qualification/integration-record/integration.md)、[正式报告](../../verification/M2-DOCTR-QUAL/qualification/qualification-report.md)（含 C1-C5 候选流程建议）。
- Review：DSH r1 APPROVED_WITH_MINOR_ISSUES（[报告](../../doc/reviews/M2-DOCTR-QUAL-RUN-eb01cd76-dsh-r1.md)）；处置：P1-1 接受 f9894184（集成裁定）、P2-1 312→314、P3-1 +9→+5、P3-2/P3-3 落字。
- 下一 Task 候选（须另行释放）：C1 GT 盲区人工校准（需用户/授权标注者参与）；C2 FAST 阈值扫描；C3 DBNet 评估（Hold）；C4 manga 域检测器（C1 后裁决）。

- Handoff：[M2-DOCTR-QUAL-RUN-f989418](../../doc/handoffs/M2-DOCTR-QUAL-RUN-f989418.md)（delivery_head=实现提交 `3b9cf180`，正式跑执行 HEAD=`f9894184`）。Review：待派发 DeepSeek Harness（非作者静态）。实际测试：上表，2026-09-30。
- 提交链：claim `6384c807` → 契约适配 `f9894184`（已披露）→ 实现产物 `3b9cf180` → 本回填。
- 正式结论：**Formal Result: FAIL**（Recall 0.4776 << 0.92，coverage 主判定层、生产 pad 正式口径）。
