---
task_id: M2-DOCTR-QUAL-RUN
author: ZCode
recipient: Codex
base_commit: 5b3a477a371a662288998f86d23ae56439179524
delivery_head: 3b9cf180709b0bdb71f3f0ce80ec3fb93adaa3fa
status: in_review
---

# Handoff：M2-DOCTR-QUAL-RUN（Real docTR formal qualification run）

- Date: 2026-09-30 (UTC). Branch `agent/zcode/M2-DOCTR-QUAL-RUN`, worktree `G:/CODEX/New Manga.worktrees/M2-DOCTR-QUAL-RUN-zcode`. Status `in_review`.
- Formal runs executed at HEAD `f98941845d5140ea697d13a654fe66c1edbeef34`; delivery head (implementation artifacts) `3b9cf180709b0bdb71f3f0ce80ec3fb93adaa3fa`.
- **Formal Result: FAIL** — Recall 0.4776 < 0.92 gate (primary layer `block_coverage`, production pad formal, frozen ruling criteria `experiments/M2-DOCTR-QUAL/thresholds.json`). Mean coverage 0.7531 PASS, severe page-miss 0.0385 PASS. This is the expected and correct formal outcome; it triggers the detector tuning / model-swap candidate flow, not a criteria change.

## 交付结果（Delivery）

Commit chain (4 commits on top of base `5b3a477a`):

1. `6384c807` — claim (Task `ready`→`in_progress`, `base_commit` pinned).
2. `f9894184` — **disclosed contract adaptation** (see Risks): `eval_detection.py` verdict block aligned to the frozen nested-gates thresholds schema; Precision demoted to non-gate observation; new `--task` metadata argument. Measurement logic untouched.
3. `3b9cf180` — implementation artifacts: 3 formal results JSONs + `consistency-and-summary.json` + `summarize_qualification.py` + `qualification-report.md` + 4 raw run logs + experiments README qualification section.
4. (this commit) — Task backfill (`in_review`, AC checkboxes, test table) + this handoff.

Changed paths: `experiments/M2-DOCTR-QUAL/**` (README, `summarize_qualification.py` new, `eval_detection.py` adaptation), `verification/M2-DOCTR-QUAL/qualification/**` (new), `doc/tasks/M2-DOCTR-QUAL-RUN.md`, `doc/handoffs/`. Production `src/**`, `requirements*.txt` untouched.

AC 对照：AC1–AC5 全部满足（AC5 含已披露偏差，见 Risks）。正式报告：`verification/M2-DOCTR-QUAL/qualification/qualification-report.md`（含 Gate 判定表、全部非 Gate 观测、一致性核对、调参/换模型候选流程建议 §7、复现附录 §9）。

## 验证证据（Evidence）

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 formal main run | `eval_detection.py --manifest .../eval-manifest.full.seg05.json --weights .../fast_base-688a8b34.pt --arch fast_base --device cuda --previews 0 --task M2-DOCTR-QUAL-RUN --out ...` (PYTHONPATH=src, GPU venv) | torch 2.11.0+cu128, doctr 1.1.0, HEAD `f9894184` | RUN, EXIT=0, 22.2 s: Recall 0.4776 **FAIL** / MeanCov 0.7531 PASS / severe 0.0385 PASS | `verification/M2-DOCTR-QUAL/qualification/results-formal-fast_base-cuda-seg05.json`, `raw/formal-run2-fast_base-cuda-seg05.log` |
| AC2 pad-offset | same + `--strip-block-pad 6.0` | same | RUN, EXIT=0, 20.9 s: Recall 0.2628, mean Cov 0.6842, severe 0.1034 | `results-formal-fast_base-cuda-seg05-padoffset.json`, `raw/formal-run3-*.log` |
| AC2 db_resnet50 | `--weights db_resnet50-79bd7d70.pt --arch db_resnet50` (seg05 full) | same | RUN, EXIT=0, 17.2 s: Recall 0.6085, severe 0.0192, mean Cov 0.7751 (still 31.2 pp below gate) | `results-formal-db_resnet50-cuda-seg05.json`, `raw/formal-run4-*.log` |
| AC3 report | `summarize_qualification.py --out .../consistency-and-summary.json` (stdlib, read-only) | repo root | RUN, EXIT=0 | `qualification-report.md`, `consistency-and-summary.json` |
| Determinism check | recursive field compare vs preflight first runs | — | PASS: fast_base / db_resnet50 / pad-offset all `deterministic_reproduction=true`, summary and 511 per_region entries 0 diff; manifest sha256 `4f16425a...` matches | `consistency-and-summary.json` |
| Not run | union-manifest FP re-attribution | — | NOT_RUN by design: preflight union evidence (2985 FP → 2 with text evidence / 2983 pure) cited as Precision-lower-bound support per dispatch; no re-run needed | `results-fast_base-cuda-union.json` (main repo) |

Integrity: weights SHA-256 pinned and verified by the runner (`688a8b34...`, `79bd7d70...`); every results JSON carries `manifest_sha256`; `git diff --check` clean.

## 接收方式（Receiving）

- Branch/worktree as above. Reviewer entry point: `verification/M2-DOCTR-QUAL/qualification/qualification-report.md`, then `consistency-and-summary.json`, then raw logs.
- Reproduction: see report §9 (or `experiments/M2-DOCTR-QUAL/README.md` §正式 qualification run). Prereqs: GPU venv `M2-DOCTR-QUAL-gpu-py312`, weights + manifests under `G:/CODEX/New Manga.task-envs/` (unchanged from preflight).
- Reviewer-specific checks suggested: (1) verify the §4 contract-adaptation diff of `eval_detection.py` is measurement-neutral (diff `f9894184^..f9894184`); (2) recompute the gate table from `results-formal-fast_base-cuda-seg05.json`; (3) spot-check the determinism claim via `summarize_qualification.py`.

## 下一任务建议（必填）

- Task ID / 标题：**M2-DOCTR-CANDIDATE**（建议名）— docTR 检测器调参/换模型候选流程第一轮：GT 盲区人工校准（C1）+ FAST 阈值扫描（C2 附录）。
- 推荐 Agent / Reviewer：ZCode 实现；DeepSeek Harness 独立 Review（非作者）。C1 的人工标注环节需用户或用户授权的标注者参与。
- 推荐原因与前置依赖：本 Task 正式 FAIL（Recall 0.4776），候选流程已由报告 §7 给出结构化建议；C1（伪 GT 盲区校准）是所有后续决策（DBNet 换型 C3 / manga-domain 检测器 C4 立项）的解释基础，C2 是最低成本探测。依赖：本 Task done；无代码依赖。
- Recovery point：仓库 `G:/CODEX/New Manga`；branch/worktree：待 Codex 创建（建议 base = 本 Task 集成后的 master head）。
- 允许修改路径：`experiments/M2-DOCTR-QUAL/**`（新增审计协议/扫描脚本）、`verification/M2-DOCTR-QUAL/qualification/**`、新 Task 文件；若阈值参数需进入生产 provider，须由 Codex 先冻结范围。
- 禁止范围与新增授权条件：`src/**` 生产行为零改动（阈值扫描先 eval 侧）；不改 thresholds.json 冻结口径；标注样本外的素材不入库。
- 交付物：C1 校准报告（分层样本 16 severe + 随机 ≥35 regions 的逐 GT 判定 + 噪声修正后的 recall 重估）+ C2 阈值扫描矩阵（box_thresh/bin_thresh × recall/coverage）。
- 验证命令、环境与完成 Gate：复用 qualification 复现命令；Gate = 校准结论可解释 ≥90% 未匹配 GT 样本 + 扫描矩阵完整 + DSH review approved。
- 可直接转发给 Agent 的指令：
  > 在 `experiments/M2-DOCTR-QUAL/` 新建候选流程 Task（依据 `verification/M2-DOCTR-QUAL/qualification/qualification-report.md` §7）：①写 GT 校准审计协议并对分层样本（16 个 severe-miss regions 全量 + 随机 ≥35 个含 GT regions）逐未匹配 GT 判定「真文字 / 伪 GT 噪声」，产出噪声修正 recall 重估报告；②实现 FAST 阈值扫描（box_thresh/bin_thresh 矩阵，eval 侧参数透传，零 src/ 改动）并产出矩阵。GPU 环境与 manifest 复用 qualification Task 既有资产。

## 风险与遗留（Risks）

- **已披露偏差（须 Codex 裁定）**：commit `f9894184` 修改了集成文件 `eval_detection.py` 的 verdict 段。根因：裁决 commit `7b17e02d` 将 `thresholds.json` 重写为嵌套 gates 契约（Precision 降非 Gate），但 runner verdict 仍读 preflight 扁平键且将 Precision 计为 Gate，正式主跑在 verdict 构建时崩溃（`KeyError: 'min_recall'`，证据 `raw/formal-run1-fast_base-cuda-seg05.log` EXIT=1）。适配仅限阈值 schema 读取 + Precision 非 Gate + `--task` 元数据；测量逻辑零改动（三组一致性自检 summary/per_region 逐字段 0 diff 证明）。若 Codex 认定应改回（例如恢复扁平 thresholds 契约），只需 revert `f9894184` 并以旧口径重跑 verdict，结果 JSON 的 summary/per_region 不受影响。
- Recall 0.4776 的解释受伪 GT 污染（`text_seg` score>=0.5 机器标注；union 层 2983/2985 FP 无文本证据可辨）——在 C1 校准完成前，任何"检测器真实质量"结论都过早。
- pad 敏感性：生产 6px pad 为净正贡献（strip 后 Recall 0.4776→0.2628、severe 0.0385→0.1034 会 FAIL）；若未来调整 `MERGE_PAD_PX` 须整组重评测。
- `--previews 0`：正式跑未产出标注预览图（preflight 既有 previews 仍可用）；severe-miss 16 regions 清单在 `consistency-and-summary.json`，C1 审计时可按需补生成预览。

## 实验附录（Experiment appendix）

- Data: KO Cleaned Webtoon 10 cases (`test_assets/comic_golden_suite`, user-authorized local testing, no pixels in Git); 511 regions / 917 pseudo-GT boxes; manifest sha256 `4f16425a8ba72435051ef5f671bf36084a74adc7c4d05800ea2ae2150cf6f11e` (seg05), union evidence layer `c62b7014...`.
- Models: `fast_base-688a8b34.pt` sha256 `688a8b34...62ace` (production pin), `db_resnet50-79bd7d70.pt` sha256 `79bd7d70...ca483` (comparison); both SHA-verified by the runner.
- Runtime/hardware: GPU venv torch 2.11.0+cu128, CUDA available; doctr 1.1.0; runs 17.2–22.2 s each (511 regions), single run per config (determinism proven against preflight first runs).
- Parameters: production path (`PYTHONPATH=src`, `cluster_words_into_blocks`, `MERGE_PAD_PX=6` formal; pad-offset diagnostic strips 6 px/side); IoU/coverage match threshold 0.5; greedy confidence-ordered matching; recognition outputs never consulted.
- Raw results: `verification/M2-DOCTR-QUAL/qualification/results-formal-*.json` + `raw/*.log` (each log carries `# shell=... cwd=... HEAD=... date=... cmd=...` header and `# EXIT=n` trailer).
- Quality judgment: frozen gates on `block_coverage` only; all other layers reported as observations. Failure samples: severe-miss region list (16) and zero-detection region list (4) in `consistency-and-summary.json`.
- Limitations: pseudo-GT pollution (see Risks); single-dataset scope (KO webtoon); GPU-only this round (production CPU envelope unchanged).
