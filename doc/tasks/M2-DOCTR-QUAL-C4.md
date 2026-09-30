---
id: M2-DOCTR-QUAL-C4
title: "manga 域检测器评估（C1-C5 候选流程之 C4；用户裁决释放 2026-09-30）"
kind: experiment
status: ready
approval: user_ruling_2026-09-30
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者静态）
integrator: 编排会话代行 Codex（用户全权授权 2026-09-28/30）
depends_on: []
base_commit: 4416ab4f99f70227f919982e3f9db543b98c9798
branch: agent/zcode/M2-DOCTR-QUAL-C4
worktree: G:/CODEX/New Manga.worktrees/M2-DOCTR-QUAL-C4-zcode
---

# M2-DOCTR-QUAL-C4：manga 域检测器评估（候选流程 C4）

## 来源与目标

- 来源：[M2-DOCTR-QUAL-RUN](M2-DOCTR-QUAL-RUN.md) 正式结论 **FAIL**（block_coverage Recall 0.4776 < 0.92），其报告 §7 产出候选流程 C1-C5；C4 定义为「manga 域检测器或微调——唯一可能从 ~0.48-0.61 逼近 0.92 Gate 的候选类」，原建议 "Decide after C1"。
- 用户裁决 2026-09-30：**C4 评估先行释放**（在 C1 之前先取现成 manga 域检测器的实测对照数据，用数据决定是否值得投入 C4 完整主线/fine-tune 系列）。本 Task 是**评估**，不是 fine-tune 主线的实施。
- 一个可观察的交付结果：现成 manga 域文本检测模型在 KO webtoon 10 case（eval-manifest.full.seg05.json，511 regions / GT-A 917 伪 GT 框）上的 block_coverage 主判定对照报告 + 「能否逼近 0.92 Gate」的**可复核结论**，入 `verification/M2-DOCTR-QUAL/qualification/`。

## 冻结口径

- 评分口径全套沿用 [thresholds.json](../../../experiments/M2-DOCTR-QUAL/thresholds.json)（用户裁决 2026-09-30 冻结版）：**block_coverage 主判定**（生产合并块）、Gate 三项（Recall ≥ 0.92 / Mean coverage ≥ 0.60 / severe ≤ 0.05）、**生产 pad 6px 为正式结果** + pad 抵消（strip 6px）附报、Precision 仅受污染观测下界不作 Gate（GT 盲区：SFX/背景文字未标注——结论表述必须带此前提）。
- 对照基线（均已集成，直接引用）：fast_base 正式 Recall **0.4776**（MeanCov 0.7531 / severe 0.0385）、db_resnet50 **0.6085**（severe 0.0192）。
- 评测基座复用：manifest= `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/eval-manifest.full.seg05.json`；GT 与评分/合并逻辑复用已集成 `eval_detection.py`（生产合并 MERGE_PAD_PX=6、三层评分、一对一贪心匹配）——**以 import 复用为主，禁止修改已集成文件的判定逻辑**。

## 评测对象选型（受控权重纪律，fail-closed）

- 候选为**现成 manga 域文本检测模型**（非 docTR 标准架构），优先级由 Owner 侦察后冻结并在 Handoff 记录选型理由；参考候选（不限定）：
  1. `dmMaze/comic-text-detector`（GitHub；漫画文本检测社区成熟方案，输出文本/气泡 mask+框）；
  2. `ogkalu/comic-text-and-bubble-detector`（HuggingFace；YOLO 气泡/文本检测）。
- 硬纪律：①**许可核查先行**——许可不明/不可用于评估的候选不采用，如实报告（许可不明导致全部候选不可用=合法 FAIL 交付，不得硬凑）；②权重获取后 **SHA-256 pin 登记**（新增 weights manifest 或并入报告，注明来源 URL/版本/获取日期）；③权重文件**不入库**（落 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/` 或同类 gitignored 外部路径）；④下载后先验哈希/可加载再使用（吸取 M2-TA2C 附件审计教训）。
- 环境：优先**新建隔离 venv**（如 `M2-DOCTR-QUAL-C4-gpu-py312`，torch 对齐 cu128 系），不污染 preflight 冻结的 docTR GPU venv；若实测与现有 venv 无依赖冲突亦可复用，选择与理由入 Handoff。

## Acceptance Criteria

- [ ] AC1（选型+受控权重）：至少一个候选完成许可核查、权重获取、SHA-256 pin 登记；或如实交付「全部候选不可用」的 fail-closed 报告（同样满足本 AC）。
- [ ] AC2（适配评测）：外部模型输出 → 文本框映射 → 生产合并（pad 6px）→ 同一评分管线，在 seg05 全量 511 regions 上跑通；新评测入口为**新增独立脚本**（如 `eval_detection_manga.py`），`eval_detection.py` 等已集成文件零改动（如确需改动即停下登记，不得擅自改）。
- [ ] AC3（对照报告）：`verification/M2-DOCTR-QUAL/qualification/c4-manga-domain-report.md`——Gate 三项逐项 PASS/FAIL、与 fast_base/db_resnet50 正式结果对照、pad 抵消附报、GT 盲区前提下的「能否逼近 0.92 Gate」可复核结论（含对 C1 必要性/C4 fine-tune 主线是否值得投入的明确建议）。
- [ ] AC4（可复现）：报告引用的全部 results JSON 带 manifest_sha256 指纹；复现命令入报告/README；GPU 跑不了时的降级路径（CPU）如实标注。
- [ ] AC5（范围纪律）：diff 仅 `experiments/M2-DOCTR-QUAL/**` 新增文件 + `verification/M2-DOCTR-QUAL/qualification/**` + 本 Task + Handoff；生产 `src/**`、`requirements*.txt`、`apps/**`、`packaging/**`、contracts 零改动。

## 禁止范围

- `src/**`、`requirements*.txt`、`apps/**`、`packaging/**`、contracts、生产 merge 常数与 wire 行为
- 已集成评测文件（`eval_detection.py`/`build_eval_manifest.py`/`thresholds.json` 等）的判定逻辑改动
- 宣称或启动 C4 fine-tune 主线、数据集策展、训练（那是根据本 Task 结论的后续 Task，须另行释放）
- 修改 M2-DOCTR-QUAL-PREFLIGHT/RUN 的已归档证据与结论

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 选型+权重 | 许可核查记录 + sha256sum + 加载冒烟 | 网络 | RUN： | |
| AC2 全量评测 | 新评测入口 --device cuda（seg05 全量 511 regions） | 隔离 venv + 权重 | RUN： | |
| AC3 对照 | pad 抵消变体 + 报告汇总 | GPU venv | RUN： | |
| AC4 复现 | 报告复现命令重跑抽样核验 | — | RUN： | |

## 依赖、风险与阻塞

- 依赖：无未完成前置（preflight/RUN 均 done；manifest/GT/对照基线全部已集成）。
- 风险：①候选权重许可/可得性不明 → fail-closed 报告交付；②外部模型输出粒度（气泡框 vs 文字行）与 GT 粒度差异 → 按 block_coverage 主判定层（生产合并后）对齐，raw 对齐差异在报告中如实披露；③**预期结果可能仍 FAIL**——0.92 Gate 需 +31~44 pp recall，现成模型一次到位概率低；FAIL 本身即有价值的可复核结论（直接支撑「是否投入 fine-tune 主线」裁决），不得为凑结果调整口径或 GT。
- 阻塞：无。

## 交付与运行记录（终态）

- （待 Owner 交付后回填）
