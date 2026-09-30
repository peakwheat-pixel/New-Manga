---
id: M2-DOCTR-QUAL-C4
title: "manga 域检测器评估（C1-C5 候选流程之 C4；用户裁决释放 2026-09-30）"
kind: experiment
status: done
claim: ZCode 2026-09-30 at delivery base 2e9f564d (branch agent/zcode/M2-DOCTR-QUAL-C4, worktree M2-DOCTR-QUAL-C4-zcode); scope per frozen AC1-AC5
delivery_head: 76fc593f37e8a5b0243796741c5dc580de72428f
integration_commit: d5b1831d
handoff: doc/handoffs/M2-DOCTR-QUAL-C4-19d1772e.md
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
  2. `ogkalu/comic-text-and-bubble-detector`（HuggingFace；气泡/文本检测。**集成更正注（N6，DSH r2）**：释放时误标「YOLO」——pinned `config.json` 证实为 RT-DETR-v2（`model_type=rt_detr_v2`、backbone `rt_detr_resnet`），Handoff 选型表已写对）。
- 硬纪律：①**许可核查先行**——许可不明/不可用于评估的候选不采用，如实报告（许可不明导致全部候选不可用=合法 FAIL 交付，不得硬凑）；②权重获取后 **SHA-256 pin 登记**（新增 weights manifest 或并入报告，注明来源 URL/版本/获取日期）；③权重文件**不入库**（落 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/` 或同类 gitignored 外部路径）；④下载后先验哈希/可加载再使用（吸取 M2-TA2C 附件审计教训）。
- 环境：优先**新建隔离 venv**（如 `M2-DOCTR-QUAL-C4-gpu-py312`，torch 对齐 cu128 系），不污染 preflight 冻结的 docTR GPU venv；若实测与现有 venv 无依赖冲突亦可复用，选择与理由入 Handoff。

## Acceptance Criteria

- [x] AC1（选型+受控权重）：至少一个候选完成许可核查、权重获取、SHA-256 pin 登记；或如实交付「全部候选不可用」的 fail-closed 报告（同样满足本 AC）。
- [x] AC2（适配评测）：外部模型输出 → 文本框映射 → 生产合并（pad 6px）→ 同一评分管线，在 seg05 全量 511 regions 上跑通；新评测入口为**新增独立脚本**（如 `eval_detection_manga.py`），`eval_detection.py` 等已集成文件零改动（如确需改动即停下登记，不得擅自改）。
- [x] AC3（对照报告）：`verification/M2-DOCTR-QUAL/qualification/c4-manga-domain-report.md`——Gate 三项逐项 PASS/FAIL、与 fast_base/db_resnet50 正式结果对照、pad 抵消附报、GT 盲区前提下的「能否逼近 0.92 Gate」可复核结论（含对 C1 必要性/C4 fine-tune 主线是否值得投入的明确建议）。
- [x] AC4（可复现）：报告引用的全部 results JSON 带 manifest_sha256 指纹；复现命令入报告/README；GPU 跑不了时的降级路径（CPU）如实标注。
- [x] AC5（范围纪律）：diff 仅 `experiments/M2-DOCTR-QUAL/**` 新增文件 + `verification/M2-DOCTR-QUAL/qualification/**` + 本 Task + Handoff；生产 `src/**`、`requirements*.txt`、`apps/**`、`packaging/**`、contracts 零改动。

## 禁止范围

- `src/**`、`requirements*.txt`、`apps/**`、`packaging/**`、contracts、生产 merge 常数与 wire 行为
- 已集成评测文件（`eval_detection.py`/`build_eval_manifest.py`/`thresholds.json` 等）的判定逻辑改动
- 宣称或启动 C4 fine-tune 主线、数据集策展、训练（那是根据本 Task 结论的后续 Task，须另行释放）
- 修改 M2-DOCTR-QUAL-PREFLIGHT/RUN 的已归档证据与结论

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 选型+权重 | 许可核查记录 + sha256sum + 加载冒烟 | 网络 | RUN（2026-09-30）：ogkalu/comic-text-and-bubble-detector 采用（Apache-2.0；GitHub API 核实 dmMaze 为 GPL-3.0 备选未采用）；`model.safetensors` sha256 `037930a8...3df80d`（171,543,900 B，HF API 元数据核对一致）+ config/preprocessor 双 pin；隔离 venv 加载 + 单 region 推理冒烟 EXIT=0，首检框与 K01 R1 GT 重合 | Handoff `doc/handoffs/M2-DOCTR-QUAL-C4-19d1772e.md` §选型表/§权重；报告 `c4-manga-domain-report.md` §1 |
| AC2 全量评测 | 新评测入口 --device cuda（seg05 全量 511 regions） | 隔离 venv + 权重 | RUN（EXIT=0，38.9 s，conf 0.5，511/511 regions）：**block_coverage Recall 0.9618（882/917）PASS / MeanCov 0.9965 PASS / severe 0.0000 PASS**；precision 0.8909（污染下界，非 Gate）；bubble 类丢弃 903；已集成文件零改动（import 复用） | `verification/M2-DOCTR-QUAL/qualification/results-formal-manga_rt_detr_v2-cuda-seg05.json`（manifest_sha256 `4f16425a...` 与基线一致） |
| AC3 对照 | pad 抵消变体 + 报告汇总 | GPU venv | RUN（均 EXIT=0）：pad 抵消（strip 6）Recall 0.9597 / meanCov 0.9582 / severe 0（与 docTR 去 pad 崩溃行为相反，框风格贴合伪 GT 证据）；conf 0.3 敏感性 Recall 0.9771；报告 Gate 三项逐项判定 + 基线对照 + 结论（Gate **PASS**；C4 fine-tune 主线在冻结口径内不投入——**条件式结论，以报告 §7.2 抽检协议通过为前提**；C1 缩减为抽检型校准审计）。DSH r1 approved_with_conditions 后 r2 已逐条处置 R1-R12 | `results-formal-manga_rt_detr_v2-cuda-seg05-padoffset.json`、`...-conf03.json`、`c4-manga-domain-report.md` §2/§3/§5/§7 |
| r2 返修 | 脚本 R9/R10 修改后行为等价证明（全量复跑 vs 入库 JSON 逐字段比对，排除运行元数据） | GPU venv | RUN（EXIT=0）：**字段 diffs = 0（行为等价 PASS）**，primary 数字逐一相同；三个正式 results JSON 零改动；许可证据入库 license-evidence.md（R6） | 返修 commit message + 外部路径 `results-r2-equivalence-check.json` + `license-evidence.md` |
| AC4 复现 | 报告复现命令重跑抽样核验 | — | RUN（EXIT=0）：正式命令 `--limit 24` 重跑，与正式 JSON 前 24 条 per_region 逐字段 0 diff（确定性复现）；三个 results JSON 均带 manifest_sha256 + 权重 sha256 + `reproduce_command`；CPU 降级路径支持但未跑（如实标注，正式结果全为 cuda） | 报告 §8；外部路径 `M2-DOCTR-QUAL-C4/results-repro-check24.json` |

## 依赖、风险与阻塞

- 依赖：无未完成前置（preflight/RUN 均 done；manifest/GT/对照基线全部已集成）。
- 风险：①候选权重许可/可得性不明 → fail-closed 报告交付；②外部模型输出粒度（气泡框 vs 文字行）与 GT 粒度差异 → 按 block_coverage 主判定层（生产合并后）对齐，raw 对齐差异在报告中如实披露；③**预期结果可能仍 FAIL**——0.92 Gate 需 +31~44 pp recall，现成模型一次到位概率低；FAIL 本身即有价值的可复核结论（直接支撑「是否投入 fine-tune 主线」裁决），不得为凑结果调整口径或 GT。
- 阻塞：无。

## 交付与运行记录（终态）

- 交付（2026-09-30，Owner=ZCode）：commit 链 `ae66fbbd`（claim）→ `19d1772e`（实现：`experiments/M2-DOCTR-QUAL/eval_detection_manga.py` + 3 个 results JSON + 报告）→ `a19d2254`（handoff/回填）→ `76fc593f`=**delivery_head**（r2 返修：DSH r1 R1-R12 逐条处置——报告 §7 条件式口径声明与抽检协议框架、合并空转量化、revision/许可证据入库、PowerShell 复现双写、脚本 R9/R10 + 行为等价 0 diff 证明；三个正式 results JSON 零改动）。base=`2e9f564d`。
- 正式结果：**Gate 三项全 PASS**（Recall 0.9618 / MeanCov 0.9965 / severe 0.0000，block_coverage 主判定，生产 pad 正式）；对照 fast_base 0.4776 / db_resnet50 0.6085。结论限定（伪 GT 同源性风险 + Precision 污染下界 + 合并空转/生产块级消费口径语义）见报告 §4/§5/§7 口径声明；建议：C4 fine-tune 主线冻结口径内不投入（条件式，待 §7.2 抽检确认），C1 缩减为抽检型校准审计（分层协议已冻结于报告 §7.2），生产集成另行释放 Task。
- Review：DSH r1 [approved_with_conditions](../reviews/M2-DOCTR-QUAL-C4-76fc593f-dsh-r1.md)（2026-09-30；0×P0/1×P1/2×P2/6×P3，R12/R13 为正面核验）→ Owner r2 返修（R1-R12 逐条处置，行为等价 0 diff）→ DSH r2 [approved_with_conditions](../reviews/M2-DOCTR-QUAL-C4-76fc593f-dsh-r2.md)（**r1 P1/P2 实质闭合**；新增 N1-N7：N1 交付 hash 未登记、N3/N4/N5/N6 文档小修=集成方闭合，N2/N7 框级数据依赖随 C1 抽检 Task 释放冻结）。
- 集成（2026-09-30，Codex 代行）：merge=`d5b1831d`（parents `840f8b91`+`76fc593f`，无冲突，8 文件全允许路径）；集成复跑：merge head 全量正式口径 EXIT=0 `verdict all_pass=True`、与入库正式 JSON 逐字段比对 **summary 0 diff / per_region 0/511 diff（确定性复现）**、集成修正后脚本 docstring 注释级改动冒烟 EXIT=0；集成修正 commit 一次性闭合 DSH r2 N1/N3/N4/N5/N6（frontmatter hash 链、D 层分母 72、docstring 同源限定、changed-paths 补 license-evidence.md、Task 架构更正注）+ DSH r1/r2 报告原字节 import。N2/N7/R7（复现证据归档、matched-pair 导出开关、B 层分层清单）移交 C1 抽检 Task 释放时冻结。记录：[integration-record-c4](../../verification/M2-DOCTR-QUAL/qualification/integration-record-c4/integration.md)。Owner branch/worktree 保留于 `76fc593f`。
- Handoff：[M2-DOCTR-QUAL-C4-19d1772e](../handoffs/M2-DOCTR-QUAL-C4-19d1772e.md)。
- 权重与环境（gitignored 外部路径）：`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector/`（sha256 pinned + HF 服务端 LFS sha256 交叉验证一致 + revision `16e8a622f91fabc6b5b65c96d32d1183f8843546`）；隔离 venv `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4-gpu-py312`（torch 2.11.0+cu128 / transformers 5.17.0）。
