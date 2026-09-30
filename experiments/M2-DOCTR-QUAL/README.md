# experiments/M2-DOCTR-QUAL — Real docTR Detection qualification 前置基座

Task：[M2-DOCTR-QUAL-PREFLIGHT](../../doc/tasks/M2-DOCTR-QUAL-PREFLIGHT.md)（用户 2026-09-29 全权授权）。

目的：为正式 Real docTR qualification 提供三项可复现前置——受控检测权重、隔离 GPU/CPU 实验环境、真实素材检测评测与质量阈值。本目录代码只做实验评测；生产 `src/`、`requirements*.txt`、默认 Pipeline 零改动。

## 评测对象与界限

- 评测 **Detection only**：docTR detection 模型（生产 pin `fast_base`，对照 `db_resnet50`）在真实漫画页面上的文本实例框检出质量。
- **不使用** docTR recognition 输出（默认非 CJK 识别模型）判定 detector 成败；识别质量属后续独立工作。
- 结论界限：结果为「相对受控伪 GT」口径（见下），不宣称产品级 PASS。

## 素材与 GT 口径（诚实披露）

- 主评测集：KO Cleaned Webtoon 10 case（`test_assets/comic_golden_suite`，真实韩漫长条，用户授权本机测试，不得入库）。
- 切片：每 case 按 `info.json.approved_regions` 切为区域图（生产 digest per-chunk 同构）。
- GT：`info.json.text_boxes` 中 `model=='text_seg'` 且 `score>=0.5` 的框（数据集清洗管线的模型辅助标注 = **伪 GT**，非人工标注）。`text_ctd` 分数中位约 0.06 不可用；`uncleaned_boxes` 是清洗记账不是评分 GT。
- GT 归属：框中心点所在 region；跨边界框按 region 裁剪（与检测器所见一致）。
- 因此 Recall/Precision 是「相对受控伪 GT 子集」的口径；GT 盲区（text_seg 漏检的文字）会使绝对召回被高估，报告必须保留此披露。

## 阈值（用户默认，thresholds.json）

IoU≥0.5 匹配；Recall≥92%；Precision≥85%；Mean IoU≥60%；严重整页漏检≤5%（定义：GT≥3 且 0 检出的 region 占含 GT region 比例）。

## 运行

~~~powershell
# 0) 受控权重快照与校验（哈希不符即中止）
python experiments/M2-DOCTR-QUAL/snapshot_weights.py

# 1) 评测集（切片与 manifest 写到仓库外 task-envs，版权像素不入 Git；需 Pillow）
python experiments/M2-DOCTR-QUAL/build_eval_manifest.py --level full --gt-mode seg05

# 2) 检测评测（GPU venv；raw_strict 诊断 + block_strict + block_coverage 主判定；权重 SHA-256 先校验）
$env:PYTHONPATH="src"
python experiments/M2-DOCTR-QUAL/eval_detection.py `
  --manifest "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/eval-manifest.full.seg05.json" `
  --weights "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL/weights/fast_base-688a8b34.pt" `
  --arch fast_base --device cuda `
  --out verification/M2-DOCTR-QUAL/results-fast_base-cuda-seg05.json

# 3) 生产 adapter 端到端一致性（块数 + 坐标逐块比对）
python experiments/M2-DOCTR-QUAL/smoke_adapter_check.py `
  --manifest "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/eval-manifest.smoke.json" `
  --weights "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL/weights/fast_base-688a8b34.pt" `
  --device cuda --out verification/M2-DOCTR-QUAL/adapter-spot-check-cuda.json

# 4) pad 敏感性对照（收缩生产 MERGE_PAD_PX=6 的块扩张后再匹配）
#    eval_detection.py 追加 --strip-block-pad 6.0
~~~

## 三层指标（口径定型记录）

实测粒度事实：docTR raw 输出为**词级**框，GT（text_seg）为**块级**；词对块 IoU 数学上不可达 0.5，union 口径并入的 text_ctd/uncleaned 框存在交叉错位坏框（见 verification/M2-DOCTR-QUAL/baseline-summary.md §4 与 task-envs `diag-K03.png`）。定型口径：

| 层 | 检出 | 匹配 | 用途 |
|---|---|---|---|
| `raw_strict` | docTR 词级 | IoU≥0.5 | 粒度诊断，不判定 |
| `block_strict` | 生产块 | IoU≥0.5 | 严格块口径诊断 |
| `block_coverage`（**主判定**） | 生产块 | inter/GT_area≥0.5 | 与默认阈值对照 |

- block 层使用生产冻结 word-to-block merge policy（`cluster_words_into_blocks`，只读 import），产品实际消费的块级口径；生产 adapter 端到端一致性 6/6（verification/adapter-spot-check-cuda.json）。
- 匹配：按置信度降序一对一贪心。
- union manifest（`--gt-mode union`）仅作 FP 证据层（`supplementary_boxes`），不用于判定。

## 已知界限

- GPU torch（2.11.0+cu128）与生产 pin（2.14.0 CPU PyPI）不同号；cu128 索引无 2.14.0（2026-09-29 复核）。T1.1.1 author-verification §5.1 已证 CPU/GPU 结果一致；本轮另做 CPU 对照子集。
- Pepper&Carrot（JA/KO）SVG 文字层每页仅 0–4 个 `<text>`，只作定性附录，不进阈值判定集。

## 正式 qualification run（M2-DOCTR-QUAL-RUN，2026-09-30）

冻结口径 `thresholds.json`（用户裁决 2026-09-30）：主判定层 `block_coverage`（生产合并块 + 生产 pad 6px 正式），Gate = Recall≥0.92 / Mean coverage≥0.60 / severe≤0.05；Precision 为受污染观测下界、不作 Gate；pad 抵消（`--strip-block-pad 6.0`）附报。正式结论 **FAIL**（Recall 0.4776）与调参/换模型候选流程建议见 [qualification/qualification-report.md](../../verification/M2-DOCTR-QUAL/qualification/qualification-report.md)。

~~~powershell
# 正式主跑 / 附报 / 对照（GPU venv；运行时 HEAD=f9894184；原始日志在 qualification/raw/）
$env:PYTHONPATH = "src"
python experiments/M2-DOCTR-QUAL/eval_detection.py `
  --manifest "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/eval-manifest.full.seg05.json" `
  --weights "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL/weights/fast_base-688a8b34.pt" `
  --arch fast_base --device cuda --previews 0 --task M2-DOCTR-QUAL-RUN `
  --out verification/M2-DOCTR-QUAL/qualification/results-formal-fast_base-cuda-seg05.json
# pad 抵消附报：追加 --strip-block-pad 6.0，--out 改 ...-padoffset.json
# db_resnet50 对照：--weights db_resnet50-79bd7d70.pt --arch db_resnet50，--out 改 results-formal-db_resnet50-cuda-seg05.json

# 汇总 + 与 preflight 首跑一致性证据（只读，stdlib）
python experiments/M2-DOCTR-QUAL/summarize_qualification.py `
  --out verification/M2-DOCTR-QUAL/qualification/consistency-and-summary.json
~~~

注意：`eval_detection.py` 自本 Task 起 verdict 段按冻结 gates 契约读取（嵌套 `gates`，Precision 非 Gate；扁平旧阈值文件保持 legacy 行为），并新增 `--task` 元数据参数；测量逻辑零改动（见 qualification-report.md §4 披露）。
