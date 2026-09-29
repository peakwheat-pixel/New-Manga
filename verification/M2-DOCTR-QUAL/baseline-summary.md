# M2-DOCTR-QUAL-PREFLIGHT：Real docTR Detection 首跑基线摘要（r5）

Task：[M2-DOCTR-QUAL-PREFLIGHT](../../doc/tasks/M2-DOCTR-QUAL-PREFLIGHT.md) · 日期：2026-09-29 · 执行：ZCode（用户全权授权）· Review：DeepSeek Harness r1 `changes_requested` → r2 `approved_with_conditions` → r3/r4 `changes_requested`（定点）→ r5 修正待复核（本文档为 r5 版；全部修订点见文末 §8）

## 0. 一句话结论

三项前置（受控权重 / 隔离 GPU 环境 / 可复现评测与阈值）全部就绪；首跑基线显示**生产 pin 的 `fast_base` 在真实韩漫 webtoon 域不满足默认质量阈值**：主判定层（block_coverage）Recall 0.4776 / Precision 0.1250（GT 盲区污染下界）FAIL，严格 IoU 块口径（block_strict）Recall 0.4515 / Precision 0.1181 同 FAIL；pad 敏感性对照把真实 Recall 夹在 **[0.26, 0.48]** 区间——FAIL 结论对匹配口径稳健。官方对照 `db_resnet50` 显著更优（0.6085 / 0.1858）但仍不达标。正式 qualification PASS/FAIL 判定待独立 Review 与用户裁决后作出；本轮交付可复现评测基座与首跑基线证据。

## 1. 受控权重（AC1）

| 文件 | 角色 | 来源 artifact | 大小 | SHA-256 | 校验 |
|---|---|---|---|---|---|
| `fast_base-688a8b34.pt` | 主（生产 pin） | doctr-static **v0.8.1**（与 `detection_doctr.py` pin 同 URL） | 65,814,772 B | `688a8b34…2ace` | = 生产 pin ✓ |
| `db_resnet50-79bd7d70.pt` | 对照 | doctr-static **v0.7.0**（doctr 1.1.0 `default_cfgs` URL 锚点） | 102,021,912 B | `79bd7d70…a483` | 文件名内嵌 hash 与内容一致 ✓ |

- License：Apache-2.0（docTR project / MINDEE，[LICENSE](https://github.com/mindee/doctr/blob/main/LICENSE)；artifact 经 doctr-static.mindee.com 分发，无独立 license 文件，随项目 license）。
- 快照：`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL/weights/`（源头 `~/.cache/doctr/models/` 只读，未改动）。
- 明细与校验命令：[weights-manifest.json](weights-manifest.json)（`schema@2`，`verified_by`/`command` 字段记录生成方式）；独立复算原文：[hash-recomputation.txt](hash-recomputation.txt)（快照字节 + 评测集 `cases.json` 与 10 个 `info.json` 的 SHA-256）。
- 复现脚本：[experiments/M2-DOCTR-QUAL/snapshot_weights.py](../../experiments/M2-DOCTR-QUAL/snapshot_weights.py)（哈希不符即中止，不落快照）。
- 生产 `requirements.txt` / `requirements-dev.txt` / `src/**` 零改动：[git-evidence.txt](git-evidence.txt)（`git diff --stat base..delivery` 对 requirements*/src 为空 + 全量文件清单）。

## 2. 隔离环境（AC2）

| 项 | GPU 实验环境 | 生产 pin（对照） |
|---|---|---|
| Python | 3.12.3 | 3.12（同） |
| torch | **2.11.0+cu128** | 2.14.0（PyPI CPU） |
| torchvision | **0.26.0+cu128** | 0.29.0（PyPI CPU） |
| python-doctr | **1.1.0（=生产 pin，无偏差）** | 1.1.0 |
| numpy / Pillow | 2.3.5 / 12.3.0 | — |
| GPU | RTX 5070 Ti 16GB，`cuda=True` | CPU |

- cu128 索引无 torch 2.14.0（2026-09-29 复核仅 2.10/2.11 cp312 win）；GPU 与生产版本偏差含 **torch 与 torchvision 两项**（r1 P2-7 补记），python-doctr 无偏差。
- CPU/GPU 一致性弥合：同 manifest limit80 双跑，78/80 per-region 全同；2 个差异 region 全部在 raw（词级）层（K01 R5 raw 16↔15；K01 R17 raw 23↔22 且 block 20↔19——raw 79→(78/80 全同，2 region 词框 ±1)；block（79/80 全同，1 region 块数 ±1）），主指标一致（precision 0.0682/0.0683、recall 全同），与 T1.1.1 §5.1 记录的浮点阈值边界效应同性质。逐字段 diff：[consistency-and-sensitivity.json](consistency-and-sensitivity.json)。
- 机器可读环境证据（版本/`cuda.is_available()`/device name/计时/峰值显存）：[env-gpu-py312.json](env-gpu-py312.json)。
- CPU 对照复用既有 `T1.1.1-impl-py312`（torch 2.14.0 = 生产精确 pin）只读运行，未改共享环境。

## 3. 评测集（AC3）

- 素材：`test_assets/comic_golden_suite` KO Cleaned Webtoon 10 case（K01–K10，真实韩漫长条；`license_class=noncommercial_research_source_restricted`，[cases.json 原文表述](../../test_assets/comic_golden_suite/manifests/cases.json)，用户授权本机测试，派生像素不入 Git）。
- 切片：每 case 按 `info.json.approved_regions` → **511 regions**（690×~500-690 px；脚本断言 region 全宽且 y 区间不重叠后执行 GT 归属）。
- GT（伪 GT，诚实口径）：`text_boxes` 中 `model=='text_seg'` 且 `score>=0.5` → **917 框**（GT-A / seg05，判定口径）；GT 盲区（SFX 拟声词、未清洗文字普遍无标注）是已知覆盖局限，见 §6。
- GT 归属：框中心点（x、y）所在 region，零跨区丢失（10/10 case assigned=total）。
- manifest：`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/eval-manifest.full.seg05.json`（`schema@2`；SHA-256 已写入每份 results JSON 的 `manifest_sha256`，数值↔输入绑定可校验）。
- 重建：`python experiments/M2-DOCTR-QUAL/build_eval_manifest.py --level full --gt-mode seg05`（需 Pillow，实验 venv 已含）。
- 素材 hash：[hash-recomputation.txt](hash-recomputation.txt)。

## 4. 评测口径（方法论记录，r1 P1-4/P2-4 后修订）

粒度实测发现（预览证据 + 量化统计，三轮口径迭代后定型）：

1. docTR raw 输出为**词级**框，GT 为**块级**（清洗 mask 派生）：GT-bearing region 平均 **6.34 个词框 / GT 框**（5350 词框 vs 917 GT 框，[consistency-and-sensitivity.json](consistency-and-sensitivity.json)）；词对块的 IoU 数学上不可达 0.5（K01 预览：一行对白 GT 1 框 vs 逐词红框）→ raw 层只作诊断，**不参与判定**。
2. union GT-B（并入 text_ctd + uncleaned）实测引入大量交叉错位坏框（diag-K03：两个绿框互相横跨对白与空白；text_ctd 分数中位 0.057）→ **弃用为判定口径**，保留为 FP 归因证据层。
3. 最终判定层 = **block_coverage**：生产冻结 merge policy（`cluster_words_into_blocks`，只读 import）聚块后，与块级 GT 按 `intersection/gt_area ≥ 0.5` 一对一贪心匹配。

**口径契约披露（r1 P1-4）**：用户默认阈值文本规定 IoU≥0.5 匹配；主判定层实际用 coverage（inter/GT_area）替代 IoU 以弥合块边界差异。**该替代属判定契约偏离，已作为待裁决项提交**（`thresholds.json` 的 `primary_layer`/`judging_criterion` 显式声明）；两种口径数值在所有结果中并列（下表），`block_strict`（真 IoU）始终可得。

**pad 偏置披露（r1 P2-4）**：生产 merge 对候选块每边扩张 `MERGE_PAD_PX=6` 后再与未扩张 GT 比较，系统性抬高 coverage 匹配（方向对 detector 有利）。敏感性对照（收缩 6px，[consistency-and-sensitivity.json](consistency-and-sensitivity.json)）：Recall 0.4776→0.2628、severe_miss 0.0385→0.1034。**两个口径夹住真实 Recall ∈ [0.26, 0.48]**——远低于 0.92 阈值，FAIL 结论对 pad 处理方式稳健。

| 层 | 检出 | 匹配 | 用途 |
|---|---|---|---|
| `raw_strict` | docTR 词级 | IoU≥0.5 | 粒度诊断，不判定 |
| `block_strict` | 生产块 | IoU≥0.5 | 严格块口径（用户默认文本的字面口径） |
| `block_coverage`（**主判定，待裁决**） | 生产块 | inter/GT_area≥0.5 | 与默认阈值对照 |

严重整页漏检定义（主层 block_coverage 上统计）：GT≥3 且检出为 0 的 region 占含 GT region 比例。

## 5. 首跑基线（AC4，2026-09-29 GPU，v2 manifest 指纹绑定）

511 regions，双口径并列（[results-fast_base-cuda-seg05.json](results-fast_base-cuda-seg05.json)）：

| 指标 | 阈值 | fast_base block_coverage（主） | fast_base block_strict（IoU 字面口径） | db_resnet50 block_coverage | 判定 |
|---|---|---|---|---|---|
| Recall | ≥0.92 | **0.4776** | 0.4515 | 0.6085 | **FAIL**（两口径） |
| Precision | ≥0.85 | **0.1250**（GT 盲区污染下界） | 0.1181（同） | 0.1858（同） | **FAIL**（两口径） |
| Mean matched | ≥0.60 | 0.7531（coverage） | 0.7034（IoU） | 0.7751 | PASS |
| 严重整页漏检率 | ≤0.05 | **0.0385** | — | 0.0192 | PASS（pad 收缩对照 0.1034 超，见 §4） |
| 耗时 | — | 23.31 s（GPU，results JSON `elapsed_seconds`） | 同次前向 | 17.11 s | — |

（db_resnet50 明细：[results-db_resnet50-cuda-seg05.json](results-db_resnet50-cuda-seg05.json)；union 证据层对照：[results-fast_base-cuda-union.json](results-fast_base-cuda-union.json)）

### 一致性验证

- **CPU（torch 2.14.0 生产 pin）vs GPU（2.11.0+cu128）**：见 §2。证据：[results-fast_base-gpu-limit80.json](results-fast_base-gpu-limit80.json) / [results-fast_base-cpu-limit80-torch2.14.json](results-fast_base-cpu-limit80-torch2.14.json) / 逐字段 [consistency-and-sensitivity.json](consistency-and-sensitivity.json)。
- **生产 adapter 端到端一致性**：6/6 region 块数一致且**块坐标最大绝对偏差 0.0 px**（harness 侧独立复算前向+聚类后逐块比对）。证据：[adapter-spot-check-cuda.json](adapter-spot-check-cuda.json)（`n_match`/`coords_max_abs_delta_px` 字段）。

### FP 性质（人工预览审计，n=4 case 抽样）

- **归因层证据力声明（r1 P1-3 修订）**：seg05 manifest 不携带 `supplementary_boxes`，其 FP 归因**结构性不可用**——脚本输出 `attribution_available: false`，不再据此计算归因计数（JSON 中残留的 `pure: 0` 为零分母占位，无观测含义）。可用的自动归因仅在 union 口径：2985 个 block_coverage FP 中仅 **2 个（0.07%）** 与辅助标注重叠（IoU≥0.3）——该归因层的证据力极弱，因为 SFX/背景文字在数据集辅助标注中几乎不存在，无法自动区分"GT 盲区正确检出"与"真误报"。
- 人工抽样预览（4 case）：K05 型（**GT 盲区 FP**）——整段未清洗对白被正确检出但 text_seg 只标了部分片段；K07 型（**真误报**）——人脸/纹理被检为文字。真实 Precision 夹在「下界 0.125」与「盲区修正后的未知值」之间，无法用本集高置信度度量。
- 预览图（含版权像素，**不入 Git**）：`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/previews/`（12 张 GT+检出）、`fp-previews/`（4 张 FP 归因）、`diag-K03.png`（union 坏框证据）。

## 6. 判定界限与下一步

1. 本轮**不宣称**产品级 qualification PASS/FAIL；阈值表 FAIL 仅表示「生产 pin 配置 × 默认阈值 × 本评测集」的现状测量，且该结论对匹配口径（IoU/coverage）与 pad 处理均稳健。
2. 已暴露的核心 gap：①docTR 默认检测权重（文档域训练）到韩漫 webtoon 域的适配缺口（FAST 词级碎片化 + SFX/人脸误检）；②数据集伪 GT 的覆盖局限（SFX 无标注 → Precision 可测性不足）；③生产 merge pad 对块级匹配的系统性偏置（需要评测侧协议固化）。
3. 正式 qualification run 前需要裁决（**超出本 Task 作者自决范围**）：a) 主判定口径（coverage vs IoU）与 pad 处理协议；b) Precision 的可测性方案（人工审计子集规模与流程）；c) 是否评估 DBNet 架构替换 FAST（属共享契约变更，独立切片）。

## 7. 复现命令

见 [experiments/M2-DOCTR-QUAL/README.md](../../experiments/M2-DOCTR-QUAL/README.md)。全部脚本确定性运行（无随机源）；权重 SHA-256 先校验后加载；results 与 manifest 以 SHA-256 指纹绑定。

## 8. r1 → r5 修订与 Review 轨迹记录

DSH r1 verdict `changes_requested`（P0×1 P1×6 P2×9 P3×8，事实层全部独立确认）。r2 修订（含 r1 P3-5 git 层证据）：P0-1 Handoff 固定 head；P1-1 `snapshot_weights.py` 入库；P1-2 [env-gpu-py312.json](env-gpu-py312.json)；P1-3 FP 归因 `attribution_available` 语义修正 + 报告改用 union 2985/2；P1-4 `thresholds.json` 显式 `primary_layer`/`judging_criterion` + 双口径并列 + 裁决项上交；P1-5 results 增加 `manifest_sha256`/`gt_mode`/`n_gt_boxes`（全部重跑绑定 v2 manifest）；P1-6 adapter 坐标比对（maxΔ=0.0）；P2-1/2/3/5/6/7/8/9 与 P3-1/2/3/4/6/7/8 落实（Pillow 声明、manifest 文件名、region 断言、severe 层级标注、CPU/GPU diff 精确化、torchvision 披露、license 措辞统一 cases.json 原文、素材 hash、UTC 时间戳、manifest `verified_by`/`command`、三处 pin 注释、IoU 措辞、AC 勾选注记 owner 自评、docstring 同步、`union_params` 结构化）；P2-4 pad 敏感性对照新增（§4）。Git 层证据（ls-tree + diff --stat，r1 与 r2 两段）：[git-evidence.txt](git-evidence.txt)。

DSH r2 verdict `approved_with_conditions`（r2 head=`3e86c800`；AC1–AC4 事实层经独立复算确认成立，0 open）。r3 提交 `fc9bfd61` 闭合 C1–C5：C1 Handoff 登记 r2 head + git-evidence 追加 r2 段；C2 计时口径统一为机器可读证据值（env-gpu：engine_build 0.54 s / first_inference 0.38 s / 稳态 33.4–34.6 ms / 峰值 522.6 MiB；全量 fast_base 23.31 s、db_resnet50 17.11 s——早期会话叙述值 4.2 s/0.59 s/38 ms 为含冷启动的另一次测量，口径不同，以 JSON 为准）；C3 §5 归因措辞修正；C4 adapter/consistency JSON 补 UTC、manifest 脚本 `generated_at` 改真实 UTC（schema@2 既有 manifest 为硬编码日期，内容不受影响，脚本修正对未来运行生效）；C5 adapter 空块集语义（两侧 0 块 = match）。不阻塞项：N6 severe 层注记、N7 REBASELINE_PLAN/Task reviewer 字段同步。DSH r3 复核：C1/C3/C4/C5 closed，C2 三处残留计时值 open（+P3-N2..N4）→ r4 提交 `3ec7704a` 修正（因作者脚本缺陷，handoff 冒烟行与本文档标题/导语两处未写回）→ DSH r4 复核：#2/#3/#5/#6 closed，#1（handoff:60 冒烟行）/#4（本文档标题/导语）open，另 P1-2 STATUS 事实性声称、P2-1 轨迹登记、P3-1 git-evidence 缺 r3/r4 段、P3-2 review 报告未落盘 → r5 提交修正全部六点（本文档标题/导语/§8 即 r5 产物；review 报告 r1–r4 已入 [doc/reviews/](../../doc/reviews/)）。
