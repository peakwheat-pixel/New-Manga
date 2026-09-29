---
id: M2-DOCTR-QUAL-PREFLIGHT
title: "Real docTR qualification 前置：受控检测权重、隔离 GPU/CPU 实验环境与可复现检测评测基座"
kind: research
status: done
approval: user_authorized_2026-09-29
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者；r1 `changes_requested`、r2 `approved_with_conditions`、r3 `changes_requested`、r4 `changes_requested`，报告在 doc/reviews/M2-DOCTR-QUAL-*）
depends_on: []
base_commit: 14720230b101908cfc586b31273fcd9574f50097
branch: agent/zcode/M2-DOCTR-QUAL-PREFLIGHT
worktree: 主工作区（代行模式；allowed_paths 严格限定，见下）
integration_commit: 51229d4956d4a83c3892d551a34082ff760690ee
---

# M2-DOCTR-QUAL-PREFLIGHT：Real docTR qualification 三项前置

## 来源与目标

- REBASELINE_PLAN backlog 行「Real docTR qualification | backlog；未登记 | 需要受控权重、环境和质量阈值」。
- 用户 2026-09-29 指令全权授权（聊天记录）：启动三项前置——①受控 docTR 官方检测权重；②隔离实验环境（优先 GPU）；③真实素材检测评测与质量阈值。生产依赖与默认 Pipeline 禁止改动。
- 前置事实（本机实测，2026-09-29）：
  - 生产已 pin `python-doctr==1.1.0` + `torch==2.14.0`（PyPI CPU）+ `fast_base-688a8b34.pt`（`src/infrastructure/providers/detection_doctr.py`，SHA-256 `688a8b34…2ace`，官方 URL `doctr-static.mindee.com/models?id=v0.8.1/…`）。
  - `verification/T1.1.1/` 已有 GPU 先例：torch 2.11.0+cu128（RTX 5070 Ti）与 CPU 结果一致（author-verification.md §5.1）；cu128 索引无 torch 2.14.0（本日 HEAD 复核仅 2.10.0/2.11.0 cp312 win）。
  - `~/.cache/doctr/models/` 已有 `fast_base-688a8b34.pt` 与 `db_resnet50-79bd7d70.pt`（2026-09-21 下载）；本轮正式校验并固化为受控快照。
  - `test_assets/comic_golden_suite`：KO Cleaned Webtoon 10 case（真实韩漫长条，80 文件 / 884,913,245 bytes，`info.json` 含模型辅助标注 `text_boxes`）；JA/KO Pepper&Carrot 文字层稀疏（每页 0–4 个 `<text>`），只能作定性附录。
- 一个可观察的交付结果：qualification 的权重、环境、评测集与阈值全部可复现落盘，且完成一次真实 docTR Detection 基线测量（正式 PASS/FAIL 判定不在本轮宣称）。

## Acceptance Criteria

> 注记（r1 P3-6）：以下勾选为 **Owner 自评**，待 DeepSeek Harness Reviewer 确认后才在 `done` 时最终确认。r1 Review 返回 `changes_requested`（事实层全部确认），r2 已按 P0-1/P1-1..6/P2-1..9/P3-* 修订（记录见 [baseline-summary §8](../../verification/M2-DOCTR-QUAL/baseline-summary.md)）。

- [x] AC1（受控权重）：`fast_base-688a8b34.pt`（主检测权重，生产 pin）与 `db_resnet50-79bd7d70.pt`（对照检测权重）的来源 URL、artifact 版本（docTR v0.8.1 / v0.7.0）、License（Apache-2.0）、字节数、SHA-256 记录于 `verification/M2-DOCTR-QUAL/weights-manifest.json`；SHA-256 与生产 pin（fast_base）一致、db_resnet50 内容哈希与官方文件名内嵌 hash 一致；权重快照固化到 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL/weights/`。生产 `requirements.txt`/`requirements-dev.txt` 与 `src/` 零改动。（2026-09-29 实测：fast_base 65,814,772 B SHA `688a8b34…2ace`=pin；db_resnet50 102,021,912 B）
- [x] AC2（隔离环境）：新建独立 venv `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-gpu-py312`（Python 3.12.3），安装 `python-doctr==1.1.0`（=生产 pin）+ torch 2.11.0+cu128 + torchvision 0.26.0+cu128（RTX 5070 Ti `torch.cuda.is_available()=True`，稳态 33.4–34.6 ms/region，峰值 522.6 MiB，见 env-gpu-py312.json）；pin 权重 SHA 校验后加载 fast_base 检测冒烟通过；项目共享环境与生产 venv 未动。cu128 索引无 torch 2.14.0（2026-09-29 复核），GPU 与生产 CPU pin 不同号以 T1.1.1 §5.1 先例 + 本轮 CPU 对照（torch 2.14.0，80 regions 78 全同/2 个 ±1 浮点边界、主指标一致）弥合。
- [x] AC3（质量阈值与评测基座）：`experiments/M2-DOCTR-QUAL/` 交付 `build_eval_manifest.py`（KO webtoon 10 case → `approved_regions` 511 regions + GT manifest，重建命令确定性）、`eval_detection.py`（三层判定：raw_strict 诊断 / block_strict / block_coverage 主判定）、`smoke_adapter_check.py`（生产 adapter 端到端一致性）、`thresholds.json`（IoU≥0.5、Recall≥92%、Precision≥85%、Mean IoU≥60%、整页严重漏检≤5%）；GT 口径（text_seg score≥0.5 伪 GT）与粒度事实（词级检出 vs 块级 GT）在 manifest 与 baseline-summary §4 显式披露；切片/预览等派生像素全部在仓库外 task-envs，未入 Git。
- [x] AC4（基线测量与判定界限）：全量 GPU 运行完成（fast_base seg05/union + db_resnet50 seg05 + CPU 对照 limit80 + adapter 抽查 6/6），数值与预览索引入 `verification/M2-DOCTR-QUAL/`（[baseline-summary.md](../../verification/M2-DOCTR-QUAL/baseline-summary.md)）；结果仅登记为「首跑基线」——默认阈值下 Recall 0.4776 / Precision 0.1250（GT 盲区污染下界）FAIL，Mean coverage 0.7531 / 严重整页漏检 0.0385 PASS；正式 qualification PASS/FAIL 判定留待独立 Review 后的 qualification run；未使用任何 docTR recognition 输出参与 detector 判定。

## 允许修改范围

- `doc/tasks/M2-DOCTR-QUAL-PREFLIGHT.md`、`doc/handoffs/M2-DOCTR-QUAL-PREFLIGHT-*.md`
- `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`doc/tasks/README.md`（仅状态回填与 Task 导航）
- `experiments/M2-DOCTR-QUAL/**`（新增实验代码与配置）
- `verification/M2-DOCTR-QUAL/**`（新增证据：weights manifest、环境清单、评测结果 JSON/MD、预览索引）
- 仓库外：`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-*/`（venv、权重快照、切片工作目录、预览图）

## 禁止范围

- `src/**`、`requirements.txt`、`requirements-dev.txt`、`apps/desktop/**`、`packaging/**`：零改动。
- `test_assets/**`：只读；KO 素材（CC BY-NC 边界、用户授权本机测试）与任何版权像素不得入库。
- 生产共享 venv、数据根（app.db、用户漫画库）、模型缓存（`~/.cache/doctr` 只读复用，不删改）。
- M2 Contract、SQLite schema/migration、Tauri ACL、默认 Pipeline 行为。
- 不宣称产品级 qualification PASS；不修改生产 word-to-block merge policy 冻结常数。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 权重校验 | `python experiments/M2-DOCTR-QUAL/snapshot_weights.py` | 标准库 | **executed 2026-09-29（r2）**：fast_base=pin 一致、db_resnet50=官方文件名 hash 一致、快照字节级复算一致、失败即中止；命令与 verified_by 入 manifest | verification/M2-DOCTR-QUAL/weights-manifest.json、hash-recomputation.txt |
| AC2 GPU 冒烟 | GPU venv 加载 fast_base pin 权重对样例 region detect | RTX 5070 Ti / torch 2.11.0+cu128 | **executed 2026-09-29（r3 数值与证据同步）**：engine_build 0.54 s、首次推理 0.38 s、稳态 33.4–34.6 ms、峰值 522.6 MiB（早期叙述 4.2 s/0.59 s/38 ms 为含冷启动的另一次测量，口径不同，以机器可读证据为准） | verification/M2-DOCTR-QUAL/env-gpu-py312.json（机器可读） |
| AC3 eval manifest | `python experiments/M2-DOCTR-QUAL/build_eval_manifest.py --level full --gt-mode seg05\|union` | 标准库 | **executed 2026-09-29**：10 cases / 511 regions / GT-A 917 框、GT-B 1184 框、跨区丢失 0 | task-envs/M2-DOCTR-QUAL-work/eval-manifest.full.*.json |
| AC3/AC4 评测 | `eval_detection.py --arch fast_base\|db_resnet50 --device cuda\|cpu` | GPU venv / impl venv | **executed 2026-09-29**：fast_base seg05 primary Recall 0.4776 / Precision 0.1250 / meanCov 0.7531 / severe 0.0385（FAIL×2 PASS×2）；db_resnet50 0.6085/0.1858/0.7751/0.0192 | verification/M2-DOCTR-QUAL/results-*.json |
| AC4 adapter 一致性 | `smoke_adapter_check.py` vs harness 独立复算（块数 + 逐块坐标） | GPU venv + PYTHONPATH=src | **executed 2026-09-29（r2）**：6/6 块数一致且坐标最大绝对偏差 0.0 px | verification/M2-DOCTR-QUAL/adapter-spot-check-cuda.json |
| AC4 CPU/GPU 一致性 | 同 manifest limit80 双环境对比 | torch 2.14.0 CPU vs 2.11.0+cu128 | **executed 2026-09-29（r2）**：78/80 per-region 全同；差异全部在 raw 层（K01 R5 raw 16↔15；K01 R17 raw 23↔22 且 block 20↔19），浮点阈值边界效应；主指标一致（precision 0.0682/0.0683、recall 全同） | verification/M2-DOCTR-QUAL/results-fast_base-{gpu-limit80,cpu-limit80-torch2.14}.json、consistency-and-sensitivity.json |

## 依赖、风险与阻塞

- 无未完成 Task 依赖（docTR 生产适配器已在 M2 基线集成）。
- 风险 1：`text_boxes` 为数据集清洗管线模型辅助标注（伪 GT），`text_ctd` 分数中位 0.057 不可用；GT 采用 `text_seg` score≥0.5 子集，召回/精度为「相对受控伪 GT」口径，须在报告显式披露，不得写成人工 GT 口径。
- 风险 2：GPU torch 版本（2.11.0+cu128）与生产 pin（2.14.0 CPU）不同号；以 T1.1.1 §5.1 CPU/GPU 一致性先例 + 本轮 CPU 对照子集弥合，差异如实记录。
- 风险 3：长条切片边界可能截断 GT 框；GT 按「框中心点所在切片」归属并在 manifest 记录排除规则。
- 阻塞：无。

## 交付与运行记录

- **2026-09-29 ZCode 交付（delivery head 见 Handoff）**：三项前置全部完成。受控权重快照+manifest；独立 GPU venv（doctr 1.1.0 = 生产 pin）；评测基座（511 regions / 917 GT-A 框 / 三层判定口径 / 用户默认阈值）；首跑基线：fast_base（生产 pin）primary block_coverage **Recall 0.4776 / Precision 0.1250（GT 盲区污染下界）FAIL**，meanCov 0.7531 / severe_miss 0.0385 PASS；db_resnet50 对照 0.6085/0.1858 仍 FAIL；CPU/GPU 一致、adapter 6/6。核心 gap：docTR 默认检测权重到韩漫 webtoon 域的适配缺口 + 伪 GT 的 SFX 标注盲区（Precision 无法用此集高置信度度量）。证据：[baseline-summary](../../verification/M2-DOCTR-QUAL/baseline-summary.md)。
- Review 轨迹：DSH r1 `changes_requested`（2026-09-29，24 项，事实层全部独立确认）→ r2 修订 `3e86c800`（20 closed / 2 partially_closed / 0 open）→ DSH r2 `approved_with_conditions`（AC1–AC4 事实层经原始 JSON 复算确认成立；条件 C1–C5）→ r3 提交 `fc9bfd61` 闭合 C1–C5 → DSH r3 `changes_requested`（C2 残留 3 处计时值 + P3-N2..N4）→ r4 提交 `3ec7704a`（部分修正；两处因作者脚本缺陷未写回）→ r5 提交 `d99ad695` 修正全部 open 项 → DSH r5 `approved`（定点复核 6/6 closed，报告 [d99ad695-dsh-r5](../../doc/reviews/M2-DOCTR-QUAL-d99ad695-dsh-r5.md)，随收口提交补录）。状态：`done`（Codex 代行集成，见 integration_commit）；遗留裁决项移交正式 qualification Task。
- Handoff：[M2-DOCTR-QUAL-PREFLIGHT-baseline](../handoffs/M2-DOCTR-QUAL-PREFLIGHT-baseline.md)。
- Review：见上方 Review 轨迹（DSH r1–r5；r5 `approved`）。
- 遗留：①正式 qualification run 的三项裁决（均超出作者自决范围）：主判定口径（coverage 替代用户默认文本的 IoU，见 thresholds.json `judging_criterion`）、pad 处理协议（生产 MERGE_PAD_PX=6 使真实 Recall 夹在 [0.26, 0.48]，见 baseline-summary §4 敏感性对照）、Precision 可测性方案（人工审计子集）；②架构选型输入：db_resnet50 显著优于 fast_base，替换属产品/契约变更须独立切片；③union GT-B 坏框问题与 text_ctd 低分框不可用已记录于 baseline-summary §4-5；④GPU 环境 torch/torchvision 与生产 pin 的偏差（2.11.0+cu128/0.26.0+cu128 vs 2.14.0/0.29.0，cu128 无 2.14.0）已披露并以 CPU 对照弥合。
