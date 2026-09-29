# M2-DOCTR-QUAL-PREFLIGHT：Real docTR Detection 首跑基线摘要

Task：[M2-DOCTR-QUAL-PREFLIGHT](../../doc/tasks/M2-DOCTR-QUAL-PREFLIGHT.md) · 日期：2026-09-29 · 执行：ZCode（用户全权授权）· Reviewer：DeepSeek Harness（待派发）

## 0. 一句话结论

三项前置（受控权重 / 隔离 GPU 环境 / 可复现评测与阈值）全部就绪；首跑基线显示**生产 pin 的 `fast_base` 在真实韩漫 webtoon 域不满足默认质量阈值**（primary block_coverage 口径 Recall 0.478 < 0.92，Precision 0.125 < 0.85，且 Precision 口径受 GT 盲区污染属下界），官方对照 `db_resnet50` 显著更优（Recall 0.609 / Precision 0.186）但仍不达标。正式 qualification PASS/FAIL 判定待独立 Review 后作出；本轮交付的是可复现评测基座与首跑基线证据。

## 1. 受控权重（AC1）

| 文件 | 角色 | 来源 artifact | 大小 | SHA-256 | 校验 |
|---|---|---|---|---|---|
| `fast_base-688a8b34.pt` | 主（生产 pin） | doctr-static **v0.8.1**（与 `detection_doctr.py` pin 同 URL） | 65,814,772 B | `688a8b34…2ace` | = 生产 pin ✓ |
| `db_resnet50-79bd7d70.pt` | 对照 | doctr-static **v0.7.0**（doctr 1.1.0 `default_cfgs` URL 锚点） | 102,021,912 B | `79bd7d70…a483` | 文件名内嵌 hash 与内容一致 ✓ |

- License：Apache-2.0（docTR project / MINDEE；artifact 经 doctr-static CDN 分发，无独立 license 文件）。
- 快照：`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL/weights/`（源头 `~/.cache/doctr/models/` 只读复用，未改动）。
- 明细：[weights-manifest.json](weights-manifest.json)。
- 生产 `requirements.txt` / `requirements-dev.txt` / `src/**` 零改动（git diff 为证）。

## 2. 隔离环境（AC2）

| 项 | 值 |
|---|---|
| venv | `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-gpu-py312`（Python 3.12.3，独立创建） |
| GPU 栈 | torch **2.11.0+cu128**、torchvision 0.26.0+cu128、python-doctr **1.1.0**（= 生产 doctr pin）、numpy 2.3.5、Pillow 12.3.0 |
| GPU | NVIDIA GeForce RTX 5070 Ti 16GB，`torch.cuda.is_available()=True`；推理 ~37 ms/region，峰值显存 523 MiB |
| 版本说明 | cu128 索引无 torch 2.14.0（2026-09-29 复核仅 2.10/2.11 cp312 win），故 GPU 环境与生产 CPU pin（2.14.0）不同号；延续 T1.1.1 §5.1 已验证组合，并另行做了同版本生产 pin 的 CPU 对照 |
| CPU 对照 | 复用既有 `T1.1.1-impl-py312`（torch 2.14.0 = 生产 pin）只读运行，未改任何共享环境 |

## 3. 评测集（AC3）

- 素材：`test_assets/comic_golden_suite` KO Cleaned Webtoon **10 case**（真实韩漫长条，K01–K10；用户授权本机测试，派生像素不入 Git）。
- 切片：按每 case `info.json.approved_regions` → **511 regions**（690×~500-690 px）。
- GT（伪 GT，诚实口径）：`text_boxes` 中 `model=='text_seg'` 且 `score>=0.5` → **917 框**（GT-A / seg05，判定口径）；GT 盲区（SFX 拟声词、未清洗文字普遍无标注）是已知覆盖局限，见 §6。
- GT 归属：框中心点所在 region，零跨区丢失（10/10 case assigned=total）。
- manifest：`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/eval-manifest.full.seg05.json`（另有 union/GT-B 变体，仅作 FP 证据层，见 §5）。
- 重建命令：`python experiments/M2-DOCTR-QUAL/build_eval_manifest.py --level full --gt-mode seg05`（标准库）。

## 4. 评测口径（方法论记录）

粒度实测发现（预览证据，三轮口径迭代后定型）：

1. docTR raw 输出为**词级**框，GT 为**块级**（清洗 mask 派生）；词对块的 IoU 数学上不可达 0.5（K01 预览：一行对白 GT 1 框 vs 逐词红框 3-4 个）→ raw 层只作诊断，**不参与判定**。
2. union GT-B（并入 text_ctd + uncleaned）实测引入大量交叉错位坏框（diag-K03：两个绿框互相横跨对白与空白）→ **弃用为判定口径**，保留为 FP 归因证据层。
3. 最终判定层 = **block_coverage**：生产冻结 merge policy（`cluster_words_into_blocks`，只读 import）聚块后，与块级 GT 按 `intersection/gt_area ≥ 0.5` 一对一贪心匹配——块对块粒度一致，coverage 容忍块边界差异。

每层含义：

| 层 | 检出 | 匹配 | 用途 |
|---|---|---|---|
| `raw_strict` | docTR 词级 | IoU≥0.5 | 粒度诊断，不判定 |
| `block_strict` | 生产块 | IoU≥0.5 | 严格块口径诊断 |
| `block_coverage`（**主判定**） | 生产块 | inter/GT_area≥0.5 | 与默认阈值对照 |

严重整页漏检定义：GT≥3 且 block_coverage 检出为 0 的 region 占含 GT region 比例。

## 5. 首跑基线（AC4，2026-09-29，GPU）

511 regions，fast_base 主口径（[results-fast_base-cuda-seg05.json](results-fast_base-cuda-seg05.json)）：

| 指标 | 阈值 | fast_base（生产 pin） | db_resnet50（对照） | 判定 |
|---|---|---|---|---|
| Recall | ≥0.92 | **0.4776** | 0.6085 | **FAIL** |
| Precision | ≥0.85 | **0.1250**（GT 盲区污染下界） | 0.1858（同上） | **FAIL** |
| Mean coverage（TP） | ≥0.60 | 0.7531 | 0.7751 | PASS |
| 严重整页漏检率 | ≤0.05 | **0.0385** | 0.0192 | PASS |
| 耗时 | — | 23.4 s（GPU） | 22.0 s（GPU） | — |

（db_resnet50 明细：[results-db_resnet50-cuda-seg05.json](results-db_resnet50-cuda-seg05.json)；union 口径对照：[results-fast_base-cuda-union.json](results-fast_base-cuda-union.json)）

### 一致性验证

- **CPU（torch 2.14.0 生产 pin）vs GPU（2.11.0+cu128）**，80 regions：78 个 per-region 完全一致，2 个 region 检出数 ±1（浮点阈值边界效应，与 T1.1.1 §5.1 记录同性质）；主指标 precision 0.0682/0.0683、recall 一致。证据：[results-fast_base-gpu-limit80.json](results-fast_base-gpu-limit80.json) / [results-fast_base-cpu-limit80-torch2.14.json](results-fast_base-cpu-limit80-torch2.14.json)。
- **生产 adapter 端到端抽查**：6/6 region 块数与 harness block 层完全一致（`DoctrDetectionProvider` rgb32 全链路）。证据：[adapter-spot-check-cuda.json](adapter-spot-check-cuda.json)。

### FP 性质（人工预览审计，n=4 case 抽样）

- K05 型（**GT 盲区 FP**）：整段未清洗对白被正确检出，但 text_seg 只标了部分片段 → 大量"正确检出"被计 FP；辅助标注中 SFX/背景文字几乎无标注，故自动归因（3067 FP 中 0% 有辅助证据）**不能**解释为全真误报。
- K07 型（**真误报**）：人脸/纹理区域被检为文字（GT 准确的页面上仍出现脸部红框）。
- 预览图（含版权像素，**不入 Git**）：`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/previews/`（12 张 GT+检出）与 `fp-previews/`（4 张 FP 归因）与 `diag-K03.png`（union 坏框证据）。

## 6. 判定界限与下一步

1. 本轮**不宣称**产品级 qualification PASS/FAIL；阈值表 FAIL 仅表示"生产 pin 配置 × 默认阈值 × 本评测集"的现状测量。
2. 已暴露的核心 gap：docTR 默认检测权重（文档域训练）到韩漫 webtoon 域的适配缺口（FAST 词级碎片化 + SFX/人脸误检），以及数据集伪 GT 的覆盖局限（SFX 无标注 → Precision 无法用此集高置信度度量）。
3. 正式 qualification run 需要独立方（DeepSeek Harness）复核本基线后裁决：阈值口径（含 Precision 的可测性）、是否引入 DBNet 架构替换 FAST、以及是否需要补充人工标注的 precision 审计子集。

## 7. 复现命令

见 [experiments/M2-DOCTR-QUAL/README.md](../../experiments/M2-DOCTR-QUAL/README.md)。全部脚本确定性运行（无随机源）；权重 SHA-256 先校验后加载。
