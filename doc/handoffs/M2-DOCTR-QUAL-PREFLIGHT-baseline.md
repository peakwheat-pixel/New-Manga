# Handoff：M2-DOCTR-QUAL-PREFLIGHT（Real docTR qualification 三项前置 + 首跑基线）

- 日期：2026-09-29
- Owner：ZCode（用户 2026-09-29 全权授权，ZCode 代行 Codex 登记）
- Reviewer：DeepSeek Harness（待派发，非作者静态 Review）
- base_commit：`14720230b101908cfc586b31273fcd9574f50097`（main）
- release commit：`480f12a2`（治理登记）
- delivery head：本文件提交前的任务分支 tip（见 git log `agent/zcode/M2-DOCTR-QUAL-PREFLIGHT`）
- 分支：`agent/zcode/M2-DOCTR-QUAL-PREFLIGHT`（主工作区，代行模式）
- 状态：`in_review`

## 1. 交付内容

### 前置 1：受控检测权重（AC1 ✓）

- 主权重 `fast_base-688a8b34.pt`（生产 pin，doctr-static **v0.8.1** artifact）：65,814,772 B，SHA-256 `688a8b3489e9f5d0290c476c6272ec3b18de3ee646c8a0dc158203b1a9c62ace`（与 `src/infrastructure/providers/detection_doctr.py` pin 一致，实测复核）。
- 对照权重 `db_resnet50-79bd7d70.pt`（doctr-static **v0.7.0** artifact，doctr 1.1.0 `default_cfgs` URL 锚点）：102,021,912 B，SHA-256 `79bd7d702506703b89cf11afa42d12aebf5cf25c3618e6ffd5f85772240ca483`（内容哈希与官方文件名内嵌 hash 前缀一致）。
- License：Apache-2.0（docTR project / MINDEE；权重经 doctr-static.mindee.com 分发，无独立 license 文件，随项目 license）。
- 快照：`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL/weights/`（自 `~/.cache/doctr/models/` 只读复制，缓存未改动）。
- 明细：[weights-manifest.json](../../verification/M2-DOCTR-QUAL/weights-manifest.json)。
- **生产依赖与默认 Pipeline 零改动**：`requirements.txt`/`requirements-dev.txt`/`src/**` 本任务未触碰。

### 前置 2：隔离实验环境（AC2 ✓）

- venv：`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-gpu-py312`（Python 3.12.3，独立新建）。
- 栈：torch **2.11.0+cu128**、torchvision **0.26.0+cu128**、**python-doctr==1.1.0（=生产 pin）**、numpy 2.3.5、Pillow 12.3.0。
- GPU：RTX 5070 Ti 16GB（`cuda=True`），推理稳态 ~37 ms/region，峰值显存 523 MiB。
- 版本差异披露：cu128 索引无 torch 2.14.0（2026-09-29 HEAD 复核），GPU 环境与生产 CPU pin（2.14.0）不同号；延续 T1.1.1 §5.1 已验证组合并另做 CPU 对照弥合（见 §3）。
- CPU 对照环境：复用既有 `T1.1.1-impl-py312`（torch 2.14.0 = 生产精确 pin）只读运行。
- 生产共享 venv、数据根、模型缓存均未修改。

### 前置 3：评测基座与质量阈值（AC3 ✓）

- 代码：[experiments/M2-DOCTR-QUAL/](../../experiments/M2-DOCTR-QUAL/README.md)（`build_eval_manifest.py`、`eval_detection.py`、`smoke_adapter_check.py`、`thresholds.json`）。
- 评测集：KO Cleaned Webtoon **10 case → 511 regions**（真实韩漫长条按 `approved_regions` 切片），GT = `text_seg` score≥0.5 伪 GT **917 框**（GT-A 判定口径），跨区丢失 0。
- 阈值（用户默认，[thresholds.json](../../experiments/M2-DOCTR-QUAL/thresholds.json)）：IoU≥0.5 匹配、Recall≥92%、Precision≥85%、Mean IoU≥60%、严重整页漏检≤5%（GT≥3 且 0 检出）。
- 判定口径（实测粒度事实后定型）：docTR 词级检出 vs 块级 GT 的 IoU 数学错配 → 主判定层 = **block_coverage**（生产冻结 merge policy 聚块，`intersection/gt_area≥0.5` 一对一贪心）；raw_strict/block_strict 为诊断层。union GT-B（并入 text_ctd/uncleaned）实测有交叉坏框，降级为 FP 证据层。论证与预览证据：[baseline-summary §4](../../verification/M2-DOCTR-QUAL/baseline-summary.md)。
- 版权纪律：切片、预览等派生像素全部在仓库外 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/`，Git 内只有数值 JSON 与本文字证据。

## 2. 首跑基线（AC4 ✓，2026-09-29 GPU）

| 指标 | 阈值 | fast_base（生产 pin） | db_resnet50（对照） |
|---|---|---|---|
| Recall | ≥0.92 | **0.4776 FAIL** | 0.6085 FAIL |
| Precision | ≥0.85 | **0.1250 FAIL**（GT 盲区污染下界） | 0.1858 FAIL |
| Mean coverage | ≥0.60 | 0.7531 PASS | 0.7751 PASS |
| 严重整页漏检 | ≤0.05 | 0.0385 PASS | 0.0192 PASS |

- 一致性：CPU（2.14.0 生产 pin）vs GPU（2.11.0+cu128）80 regions 中 78 per-region 全同、2 个 ±1（浮点阈值边界，与 T1.1.1 §5.1 同性质），主指标一致；生产 adapter 端到端抽查 6/6 块数一致。
- 证据：[baseline-summary.md](../../verification/M2-DOCTR-QUAL/baseline-summary.md) 与同目录 5 份 results JSON + adapter-spot-check。
- **判定界限**：本轮不宣称产品级 qualification PASS/FAIL；FAIL 数值 = 「生产 pin 配置 × 默认阈值 × 本评测集」现状测量。核心 gap：①docTR 默认检测权重（文档域）→ 韩漫 webtoon 域适配缺口；②伪 GT 的 SFX/背景文字标注盲区使 Precision 无法用此集高置信度度量（FP 人工抽样：K05 型 GT 盲区正确检出 + K07 型人脸纹理真误报，预览在 task-envs `previews/`、`fp-previews/`、`diag-K03.png`）。

## 3. 实际测试命令与结果（摘要）

全部 executed 2026-09-29，明细见 Task 测试表：

- 权重校验：SHA-256 复核 fast_base=pin 一致 ✓
- GPU 冒烟：engine 4.2s / 稳态 38ms / 523 MiB ✓
- manifest：`build_eval_manifest.py --level full --gt-mode seg05|union` → 511/917、511/1184 ✓
- 评测：`eval_detection.py`（fast_base cuda seg05+union、db_resnet50 cuda seg05、fast_base cpu limit80、fast_base cuda limit80）✓
- adapter：`smoke_adapter_check.py` → 6/6 ✓
- 未跑项：无（AC1–AC4 全部 executed）；DBNet 替换与阈值调优**不在本 Task 范围**。

## 4. 风险与遗留

1. 正式 qualification run + 阈值口径裁决（Precision 可测性 / 人工审计子集 / 是否调阈值）= 下一个 Task，需独立 Review 裁决，**不属于本 Task**。
2. 架构输入：db_resnet50 显著优于生产 pin 的 fast_base（Recall +0.13 / Precision +0.06 / severe −0.02）；替换检测架构属共享契约变更，须独立切片 + Codex 授权。
3. union GT-B 的 text_ctd 坏框（交叉错位）已实证；该数据集的 text_ctd/uncleaned 标注不可用作精度 GT。
4. GPU torch 与生产 CPU pin 不同号（cu128 无 2.14.0）；一致性已用双跑弥合，但正式 qualification 报告须保留此披露。

## 5. 复现方式

见 [experiments/M2-DOCTR-QUAL/README.md](../../experiments/M2-DOCTR-QUAL/README.md) §运行。权重快照、venv、manifest、预览均在 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL*/`，全部命令确定性（无随机源）。

## 6. 下一接收者

DeepSeek Harness（静态 Review，非作者）：审 [baseline-summary](../../verification/M2-DOCTR-QUAL/baseline-summary.md)、评测口径（block_coverage 主判定论证）、阈值判定与版权纪律（派生像素未入库）。Review 通过后由 Codex（代行）集成收口；正式 qualification run 的释放裁决随 Review 结论一并提出。
