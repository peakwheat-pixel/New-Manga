---
id: M2-DOCTR-QUAL-PREFLIGHT
title: "Real docTR qualification 前置：受控检测权重、隔离 GPU/CPU 实验环境与可复现检测评测基座"
kind: research
status: in_progress
approval: user_authorized_2026-09-29
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（待派发，非作者）
depends_on: []
base_commit: 14720230b101908cfc586b31273fcd9574f50097
branch: agent/zcode/M2-DOCTR-QUAL-PREFLIGHT
worktree: 主工作区（代行模式；allowed_paths 严格限定，见下）
integration_commit: null
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

- [ ] AC1（受控权重）：`fast_base-688a8b34.pt`（主检测权重，生产 pin）与 `db_resnet50-79bd7d70.pt`（对照检测权重）的来源 URL、artifact 版本（docTR v0.8.1）、License（Apache-2.0）、字节数、SHA-256 记录于 `verification/M2-DOCTR-QUAL/weights-manifest.json`；SHA-256 与生产 pin（fast_base）及 docTR 包内官方 checksum（db_resnet50）一致；权重快照固化到 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL/weights/`。生产 `requirements.txt`/`requirements-dev.txt` 与 `src/` 零改动。
- [ ] AC2（隔离环境）：新建独立 venv `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-gpu-py312`（Python 3.12），安装 `python-doctr==1.1.0` + torch 2.11.0+cu128 + torchvision 0.26.0+cu128（GPU 优先，RTX 5070 Ti `torch.cuda.is_available()=True`）；用 pin 权重加载 `fast_base` 完成检测冒烟；项目共享环境、生产 venv、requirements 与 lock 未被修改。CPU 对照（与生产 pin 同版本 torch 2.14.0）复用既有 `T1.1.1-impl-py312` 只读运行。
- [ ] AC3（质量阈值与评测基座）：`experiments/M2-DOCTR-QUAL/` 提供 `build_eval_manifest.py`（KO webtoon 10 case → `approved_regions` 切片 + GT manifest）、`eval_detection.py`（docTR raw 实例级 + 生产 adapter block 级双层指标）、`thresholds.json`（默认阈值 IoU≥0.5、Recall≥92%、Precision≥85%、Mean IoU≥60%、整页严重漏检≤5%）；评测集与 GT 口径（`text_seg` score≥0.5 伪 GT 子集）在 manifest 与报告中显式披露；切片图像等派生像素不入 Git。
- [ ] AC4（基线测量与判定界限）：smoke → 全量 GPU 运行完成，数值结果与预览索引入 `verification/M2-DOCTR-QUAL/`；本轮结果仅登记为「首跑基线」，正式 qualification PASS/FAIL 判定待独立 Review 后由 qualification run 作出；不使用 docTR recognition 的日/韩文识别结果参与 detector 判定。

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
| AC1 权重校验 | `python experiments/M2-DOCTR-QUAL/snapshot_weights.py` + sha256 复核 | 任意 Python；网络仅需元数据 | NOT_RUN | 待入 verification |
| AC2 GPU 冒烟 | GPU venv python 加载 fast_base pin 权重对样例图执行 detect | RTX 5070 Ti | NOT_RUN | 待入 verification |
| AC3 eval manifest | `python experiments/M2-DOCTR-QUAL/build_eval_manifest.py --level smoke\|full` | 标准库 | NOT_RUN | 待入 verification |
| AC3/AC4 评测 | `python experiments/M2-DOCTR-QUAL/eval_detection.py --manifest … --device cuda` | GPU venv | NOT_RUN | 待入 verification |
| AC4 adapter 一致性 | 生产 `DoctrDetectionProvider` 端到端抽查 N 切片与 harness block 输出比对 | GPU venv + PYTHONPATH=src | NOT_RUN | 待入 verification |

## 依赖、风险与阻塞

- 无未完成 Task 依赖（docTR 生产适配器已在 M2 基线集成）。
- 风险 1：`text_boxes` 为数据集清洗管线模型辅助标注（伪 GT），`text_ctd` 分数中位 0.057 不可用；GT 采用 `text_seg` score≥0.5 子集，召回/精度为「相对受控伪 GT」口径，须在报告显式披露，不得写成人工 GT 口径。
- 风险 2：GPU torch 版本（2.11.0+cu128）与生产 pin（2.14.0 CPU）不同号；以 T1.1.1 §5.1 CPU/GPU 一致性先例 + 本轮 CPU 对照子集弥合，差异如实记录。
- 风险 3：长条切片边界可能截断 GT 框；GT 按「框中心点所在切片」归属并在 manifest 记录排除规则。
- 阻塞：无。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无（交付后派发 DeepSeek Harness 静态 Review，非作者）。
- 实际测试：尚无。
- 后续实际记录包含日期、commit、环境、结果、遗留项；最终由 Codex 填写 integration_commit 并改 done。
