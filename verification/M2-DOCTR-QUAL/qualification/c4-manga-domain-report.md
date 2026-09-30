# M2-DOCTR-QUAL-C4 — Manga 域现成检测器对照评估报告

- Task: `M2-DOCTR-QUAL-C4`（user ruling 2026-09-30，C1-C5 候选流程 C4 评估先行；Owner=ZCode、Reviewer=DSH 非作者、Integrator=代行 Codex）
- Date: 2026-09-30 (UTC)
- Base commit: `2e9f564d`（delivery base；parent = release base `4416ab4f`）
- Claim commit: `ae66fbbd`（分支 `agent/zcode/M2-DOCTR-QUAL-C4`，worktree `G:/CODEX/New Manga.worktrees/M2-DOCTR-QUAL-C4-zcode`）
- 冻结口径：`experiments/M2-DOCTR-QUAL/thresholds.json`（QUAL-RUN 同一裁决版）——主判定层 `block_coverage`（生产合并块、生产 pad `MERGE_PAD_PX=6` 为正式）；Gate 三项 Recall ≥ 0.92 / Mean coverage ≥ 0.60 / severe page-miss ≤ 0.05；Precision = 受污染观测下界，**不作 Gate**；pad 抵消（strip 6px）附报；仅检测，recognition 不参与。
- 评测 manifest：`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/eval-manifest.full.seg05.json`，sha256 `4f16425a8ba72435051ef5f671bf36084a74adc7c4d05800ea2ae2150cf6f11e`（与 fast_base / db_resnet50 基线**同一 manifest 同一 GT**，511 regions / 917 伪 GT 框，KO webtoon 10 case K01-K10；GT = `text_seg` score≥0.5 机器伪 GT，非人工标注）。
- 运行环境：**新建隔离 venv** `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4-gpu-py312`（Python 3.12.3，torch 2.11.0+cu128 本地 wheels 离线安装，transformers 5.17.0，safetensors）。RTX 5070 Ti（driver 616.92）。不污染 preflight 冻结的 docTR GPU venv。
- 评测入口：`experiments/M2-DOCTR-QUAL/eval_detection_manga.py`（**新增独立脚本**，经 import 复用 `eval_detection.py` 的 `match_greedy` / `blocks_to_rects` / `iou` / `sha256_file` / `THRESHOLDS` 与生产 `infrastructure.providers.detection_doctr.cluster_words_into_blocks`；**已集成文件零改动**——`git diff --name-only 2e9f564d..HEAD` 可复核）。
- 机器可读证据：`results-formal-manga_rt_detr_v2-cuda-seg05.json`（正式）、`results-formal-manga_rt_detr_v2-cuda-seg05-padoffset.json`（pad 抵消附报）、`results-formal-manga_rt_detr_v2-cuda-seg05-conf03.json`（conf 敏感性附报），均带 `manifest_sha256`、权重 sha256、复现命令字段。

## 1. 选型与受控权重（AC1）

侦察范围：Task 契约给定的两个参考候选 + GitHub/HF 元数据核查（2026-09-30）。

| 候选 | 来源 | 许可证 | 核查结论 | 决定 |
|---|---|---|---|---|
| **ogkalu/comic-text-and-bubble-detector** | HuggingFace | **Apache-2.0**（模型卡标注 + API `tags`/`cardData.license` 一致） | 商用友好；RT-DETR-v2（pinned `config.json`：`RTDetrV2ForObjectDetection` / `model_type=rt_detr_v2` / backbone `rt_detr_resnet`；**r50vd 与 42.9M params 为模型卡口径**，HF API safetensors 元数据 `F32=42,861,209` 佐证）；训练数据约 11k 张 manga/**webtoon**/manhua/西方漫画（与 KO webtoon 评测集同域）；输出 3 类：`0=bubble`、`1=text_bubble`、`2=text_free` | **采用（主评）** |
| dmMaze/comic-text-detector | GitHub（379 stars） | **GPL-3.0**（GitHub API `license.spdx_id` 核实） | 对本地评估本身可用（不分发），但 copyleft 有传染义务；权重获取依赖 manga-image-translator 第三方 release / Google Drive（无官方校验和直链）；依赖链重（DBNet 文本分割 + YOLOv5 文本块两级系统）；训练集不公开 | **备选未采用**（理由登记如上；AC1 只要求至少一个候选完成全链，ogkalu 已满足） |

许可核查的原始 API 证据快照（抓取内容 + 时间 + 来源 URL + 快照 sha256）已入库：[license-evidence.md](license-evidence.md)。

权重受控纪律（controlled-weight discipline）：

- 获取方式：`hf download ogkalu/comic-text-and-bubble-detector`（2026-09-30，HF CLI，落地 gitignored 外部路径，**不入库**）。**pinned revision：`16e8a622f91fabc6b5b65c96d32d1183f8843546`**（HF API `sha` 字段；revision `lastModified` 2026-05-15）。
- 落地：`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector/`
- SHA-256 pin（`sha256sum` 实测，文件大小与 HF API `?blobs=true` 元数据逐一核对一致；`model.safetensors` 的**服务端 LFS sha256 与本地实测 pin 逐字符一致**，见 license-evidence.md §1）：
  - `model.safetensors`（171,543,900 B）= `037930a861e67870eb345be01b28cc70d7e2b7956528e48ee0ebdb0c093df80d`
  - `config.json`（2,320 B）= `b6d707933e12e9593a7025604be1c95add70a6db371fdd1532e8854e2256e072`
  - `preprocessor_config.json`（470 B）= `7e9e2245806aa3ef068a5321f5eebee3116fa4cec560173231954ffaca930eca`
- ONNX 变体存在性（同一 revision 含 `detector.onnx` 168.5 MB / `detector_int8.onnx` 43.8 MB / `detector-v4-s_int8.onnx` 11.1 MB）：**本评估不采用**——评测入口走 transformers `RTDetrV2ForObjectDetection` 检查点，与 docTR 基线的 torch 推理栈同构，避免引入 onnxruntime 额外推理栈变量；v4 量化 ONNX 无 transformers config/checkpoint 配套，无法与 pinned `config.json` 核对结构，不在本评估范围。
- 加载冒烟：隔离 venv 中 `from_pretrained`（本地目录）+ 单 region GPU 推理成功；首检框 `[155.6, 67.9, 431.0, 109.0]` conf 0.938 与 K01 R1 的 GT `[156, 64, 428, 110]` 基本重合（RUN 记录见 Handoff）。

## 2. Gate 判定（主判定层 block_coverage，生产 pad 正式口径）

正式运行：`results-formal-manga_rt_detr_v2-cuda-seg05.json`（device `cuda`，conf_threshold 0.5，511/511 regions，elapsed 38.9 s，EXIT=0）。

| Gate（block_coverage） | 阈值 | 实测 | 判定 |
|---|---|---|---|
| Recall | ≥ 0.92 | **0.9618**（tp 882 / gt 917） | **PASS** |
| Mean coverage（matched） | ≥ 0.60 | **0.9965** | **PASS** |
| Severe page-miss rate | ≤ 0.05 | **0.0000**（0 / 416 有 GT regions） | **PASS** |

**Gate 结果：PASS（三项全过）**。这是 C1-C5 候选流程中**已实测候选里**第一个、也是唯一越过 0.92 Gate 的候选（C2/C5 从未运行）：0.92 需较 fast_base（0.4776）**+44.2 pp**，本候选实达 **+48.4 pp**——现成 manga 域模型一次到位。该 PASS 的准确含义见 §7 开头的口径声明（生产块级消费口径达标，非 merge 中性的"检测质量高 48 pp"，见 §4 合并空转量化）。

诊断层（不判定，仅披露）：`block_strict`（IoU≥0.5 vs 块 GT）recall 0.9204 / mean IoU 0.7844；`raw_strict`（模型 text 框粒度直接 vs 块 GT，粒度诊断）recall 0.9553——与 docTR 的 raw_strict 0.1941（word 级 vs 块 GT 系统性低估）对照，说明该模型的输出粒度（行/块级 text 框）与块级伪 GT 天然对齐，这是结构性优势的一部分（见 §4、§5）。

## 3. 与基线对照 + 附报变体

### 3.1 正式口径对照（同一 manifest sha `4f16425a...`、同一 GT、同一生产合并+评分管线）

| 检测器 | Recall（主判定） | Mean coverage | Severe rate | Precision（污染下界，非 Gate） | GPU elapsed |
|---|---|---|---|---|---|
| docTR fast_base（QUAL-RUN 正式） | 0.4776（438/917） | 0.7531 | 0.0385（16/416） | 0.1250 | 22.2 s |
| docTR db_resnet50（QUAL-RUN 正式） | 0.6085（558/917） | 0.7751 | 0.0192（8/416） | 0.1858 | 17.2 s |
| **manga RT-DETR-v2（本报告）** | **0.9618（882/917）** | **0.9965** | **0.0000（0/416）** | **0.8909** | 38.9 s |

相对基线：recall **+48.4 pp vs fast_base / +35.3 pp vs db_resnet50**；severe miss 从 16/8 个 region 降到 0；逐 case spread 从 3.2x（0.2178-0.6991）收窄到 1.1x（0.9053-1.0000）——召回不再强依赖内容类型。

### 3.2 附报变体（均非正式口径，附报供敏感性复核）

| 变体 | Recall | Mean coverage | Severe | Precision（下界） | 说明 |
|---|---|---|---|---|---|
| pad 抵消（conf 0.5，`--strip-block-pad 6`） | 0.9597（880/917） | 0.9582 | 0.0000 | 0.8889 | 与 docTR 基线行为**相反**：fast_base 去 pad 崩到 0.2628（生产 6px pad 对 word 级合并是净收益），而本模型去 pad 几乎无损——其 text 级框与伪 GT 框天然贴合，不依赖生产 pad 贴补（同源性 caveat 证据之一，见 §5） |
| conf 敏感性（conf 0.3，pad 0） | 0.9771（896/917） | 0.9969 | 0.0000 | 0.8228 | 阈值降到 0.3 仅 +1.5 pp recall、precision 降 6.8 pp——0.5 阈值附近已饱和，正式口径对阈值不敏感 |

## 4. 粒度映射决策（适配披露）

- 模型输出 3 类：`bubble`（气球框）/ `text_bubble`（气球内文字）/ `text_free`（气球外文字）。**仅保留两个 text 类作检测候选**；bubble 类是气球形状而非文字框，若纳入会以非文字面积虚高 coverage 判据（intersection/gt_area）。正式运行共丢弃 903 个 bubble 类检测（每 region 计数在 per_region `n_bubble_dropped`）。
- 每个 text 框充当**一个合并输入（"word" 角色）**，与 `eval_detection.py` 中 docTR word 框的角色完全一致；之后走**同一**冻结生产合并（`cluster_words_into_blocks`，`MERGE_PAD_PX=6`、页界裁剪、确定性排序）产出被判定的 block 层。三个模型（fast_base / db_resnet50 / 本候选）共享同一 merge+评分路径，对照是 detector 单变量对照。
- 预处理使用模型自带 `preprocessor_config.json`（resize 640x640），**不做针对本数据集的适配调参**——本评估定位是"现成模型开箱即用"的真实能力测量；manifest region 尺寸 600-690 宽 × 最高 2047 高（57/511 regions 长宽比>2），直接 640x640 resize 未见构成瓶颈（结果见 §6）。
- **合并近乎空转的量化披露（DSH r1 R3）**：正式运行中原始 text 框 1021 个经生产合并后为 990 个块（−3.0%），对照 GT 917 框——本候选的原始输出**已近块级**、与伪 GT 粒度基本 1:1，生产合并对其近乎空转（对照例证：K04 r1 合并 11→11、K04 r18 13→12）。而 docTR 基线是词级框，必须经过对它们最具破坏性的 word→block 合并环节（fast_base 3505 检测块 / 3067 FP）。**代码路径同一，但实际处理不等价**：候选绕过了 docTR 最具破坏性的环节。因此 +48.4 pp 不是 merge 中性的"检测质量"增量，Gate PASS 的准确含义是"现成模型在**生产块级消费口径**下达标"（§7）。

## 5. 结论的前提与限定（GT 盲区 + 伪 GT 同源性，必须与 §7 结论一起读）

1. **GT 盲区**：GT 是 `text_seg` score≥0.5 的机器伪 GT，SFX/背景文字未标注。Precision 0.8909 是**受污染下界**：108 个 block_coverage FP 中可能包含落在盲区的真实文字检测，不能区分"模型幻觉"与"GT 盲区"（QUAL-RUN 的 union 层证据已证明此类 FP 无法在无人工复核时归因）。Precision 不参与 Gate（冻结裁决）。
2. **伪 GT 同源性风险（本报告新增的关键限定）**：本模型在约 11k 张漫画域图像上训练，其标注管线与 KO webtoon 伪 GT（`text_seg`）管线**无已知的同源关系，但也无法排除相似的标注风格偏好**。mean coverage 0.9965（docTR 仅 0.7531）和 pad 抵消几乎无损（docTR 去 pad 崩溃）这两个模式，既可以是"检测框质量高"，也可能部分来自"框风格与伪 GT 标注风格对齐"。**在冻结口径内这是合法 PASS**（Gate 本身就定义在该伪 GT 上），但把"block_coverage PASS"解读为"真实用户体验达标"之前，需要一次小规模人工抽检校验（协议见 §7.2，其中层 C 是本限定的直接检验）。
3. 训练数据含 webtoon（与评测集同域、同语言），不排除评测 case 存在于训练分布内的可能（作者未公开训练清单，无法核实去重）。这也是 §7.2 抽检保留的原因之一。

## 6. 逐 case 明细（正式口径）

| Case | GT 框 | TP（coverage） | Recall | （对照 fast_base） |
|---|---|---|---|---|
| K01 | 91 | 89 | 0.9780 | 0.4945 |
| K02 | 19 | 18 | 0.9474 | 0.6316 |
| K03 | 95 | 86 | 0.9053 | 0.2737 |
| K04 | 113 | 110 | 0.9735 | 0.6991 |
| K05 | 44 | 44 | 1.0000 | 0.4318 |
| K06 | 101 | 92 | 0.9109 | 0.2178 |
| K07 | 185 | 181 | 0.9784 | 0.6486 |
| K08 | 34 | 33 | 0.9706 | 0.3235 |
| K09 | 105 | 102 | 0.9714 | 0.4667 |
| K10 | 130 | 127 | 0.9769 | 0.4231 |

- 10/10 case 全部 ≥0.90（8/10 ≥0.94）；基线最佳 case（K04 0.6991）低于本模型最差 case（K03 0.9053）。
- 有 GT 未命中的 region 仅 **8 个，全部为 n_gt=1 的小 region**，按失效模式分两类（DSH r1 R12，供 §7.2 抽检分层）：
  - **真未检出**（`n_det_raw=0`，模型在 region 内零输出，6 个）：K06 r36/r38/r48/r94、K07 r79、K09 r14；
  - **有检出但 coverage 不达标**（存在检测框但未达 coverage≥0.5，2 个）：K07 r109（1 个检出框）、K08 r3（3 个检出框）——是粒度/边界问题，不是漏检。
  - 其中 K06 r94 同时出现在 fast_base 的 zero-detection 名单（QUAL-RUN §6）——该 region 的 GT 很可能是伪 GT 噪声（SFX/背景）。
- severe page-miss（≥3 GT 且 0 TP）为 0/416；基线为 16 处（K10 占 6 处）。

## 7. 可复核结论与建议

**口径声明（先于一切建议，DSH r1 R1/R3）**：在冻结口径（block_coverage 主判定、生产 pad、seg05 全量 511 regions、同一伪 GT）下，现成 manga 域检测器 ogkalu/comic-text-and-bubble-detector（Apache-2.0）一次性越过 0.92 Gate（Recall 0.9618 / MeanCov 0.9965 / severe 0.0，三项全 PASS），且对 pad 抵消和 conf 阈值两个敏感性方向均稳健。该 PASS 的准确含义是：**现成模型在「生产块级消费口径、对机器伪 GT」下达标**——不是 merge 中性的"检测质量高 48 pp"（§4：本候选绕过了对 docTR 最具破坏性的 word→block 合并环节，合并近乎空转），也不是"真实用户体验达标"（§5.2/5.3 同源性限定）。**§7.1-7.3 全部以 §7.2 抽检协议通过为前提**；抽检未完成前，本节结论只在该口径内有效。全部结果可用 §8 命令与三个 results JSON（带 manifest/权重双指纹）逐字段复核。

### 7.1 C4 fine-tune 主线：冻结口径内不投入（条件式结论）

契约预设的"唯一可能从 ~0.48-0.61 逼近 0.92 的候选类"已由零训练成本的现成模型在冻结口径内闭环：conf 0.3 敏感性上限 0.9771 距 1.0 仅 2.3 pp，且残差集中在 8 个单 GT 小 region（§6），fine-tune 无法针对性解决——**在冻结口径内无剩余收益空间**。**真实目标下的剩余空间待 §7.2 抽检结论后确认**：若抽检显示未匹配 GT 主要是伪 GT 噪声，则 0.9618 对真实目标是低估、"不投入"结论加强；若显示大量真实文字漏检/贴合失真（层 C），再议。在抽检闭合前，"不释放 C4 fine-tune 主线"是安全裁决（不投入的代价只是放弃一个口径内已饱和的方向，机会成本低）。

### 7.2 C1 抽检协议框架（分层定义冻结，执行细节移交 C1 Task）

原 C1"GT 盲区审计"按本评估结果缩减为**抽检型校准审计**，目标：把"口径内 PASS"校验为"用户可见层面的 PASS/FAIL"。分层定义与配额如下（随机种子、抽样执行与双人一致性规则——**移交 C1 抽检 Task 释放时冻结**）：

| 层 | 分母（正式 JSON 实测） | 配额 | 判定问题 |
|---|---|---|---|
| **A1 真未检出** | 6 region（K06 r36/r38/r48/r94、K07 r79、K09 r14；`n_det_raw=0`，各 1 个 GT 框） | 全查（6 框） | GT 框是真实文字（→真实漏检）还是伪 GT 噪声（SFX/背景，→伪 GT 噪声） |
| **A2 coverage 不达标** | 2 region（K07 r109：1 检出框；K08 r3：3 检出框） | 全查（2 region 共 4 框 vs 各自 GT） | 检出框与 GT 的错位是粒度/边界问题（→粒度不达标）还是 GT 本身噪声（→伪 GT 噪声） |
| **B1 有 GT region 的 FP** | 78 框（分布于 49 region） | 抽 15 框；按 conf 十分位分层比例配额 | FP 落在真实但未标注的文字上（→盲区 FP）还是无文字处（→模型幻觉） |
| **B2 无 GT region 的 FP** | 30 框（分布于 23 个 `n_gt=0` region） | 抽 15 框；同上分层 | 同 B1（该层是纯盲区/幻觉判别的最干净样本） |
| **C mean coverage 贴合样本** | matched coverage ∈ [0.5, 0.7) 的匹配对（区分"真匹配"与"边界对齐"；现有 results JSON 未存 per-pair coverage，需 eval 侧补 matched-pair 导出开关后生成清单——新增导出逻辑，不动已集成文件） | 抽 20 对 | 贴合匹配是真实文字的正确覆盖（→真匹配）还是把 GT 框"擦边盖住"（→粒度不达标）；**本层是 §5.2 同源性限定的直接检验** |
| **D 零检测/零标注 region 校准** | **78 个 `n_det_block=0` region（72 个 `n_gt=0` + 6 个有 GT 真未检出已入 A1）**；95 个 `n_gt=0` region 中 23 个产生 FP 已入 B2（集成更正注：分母 72 与"零检测=`n_det_block=0`"定义按 DSH r2 N3 更正，原「95」为 `n_gt=0` 口径、与配额对象不一致） | 随机抽 10 个零检测 region（`n_det_block=0`）全帧复核 | 模型零输出与伪 GT 零标注是否一致（校准 GT 盲区率与"模型幻觉为零"的陈述） |

分类枚举（每个抽样单元判定为且仅为以下之一）：**真实文字漏检 / 伪 GT 噪声 / 盲区 FP / 粒度不达标**（B 层前两类语义替换为"盲区 FP / 模型幻觉"）。

输出字段（每抽样单元）：`case_id`、`region_index`、框坐标（xyxy）、层别（A1/A2/B1/B2/C/D）、分类判定、一句话判定依据、图像证据文件引用（带 GT 绿框/检测红框的裁剪图）。

### 7.3 后续工作在集成侧，不在检测精度侧

把该模型替换生产 docTR 栈是生产 wire 行为变化（依赖 transformers 栈、新权重治理、Apache-2.0 合规登记、CPU/GPU 部署 envelope、延迟预算——GPU 38.9 s/511 regions ≈ 76 ms/region，CPU 路径未测），须由 Codex 另行释放范围化 Task；本 Task 不宣称、不启动该集成。

### 7.4 诚实披露的负结果面

本评估的 PASS 不构成对生产集成的推荐——精度之外的工程面（部署体积、推理延迟、长图行为、许可与供应链治理）未测；§5.2/5.3 的同源性限定在 §7.2 抽检完成前保留。复现核验证据目前部分依赖 gitignored 外部路径与运行自述（DSH r1 R7：committed 复现证据文件 + raw 日志归档列为遗留，随 C1 抽检 Task 一并闭合）。

## 8. 复现命令与证据物

环境：worktree `G:/CODEX/New Manga.worktrees/M2-DOCTR-QUAL-C4-zcode`，隔离 venv `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4-gpu-py312`（GPU；`--device cpu` 为降级路径，未用于正式结果——如实标注：正式结果全部为 cuda）。

```bash
# 正式（Gate 输入）— bash/Git Bash 写法
PYTHONPATH=src "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4-gpu-py312/Scripts/python.exe" \
  experiments/M2-DOCTR-QUAL/eval_detection_manga.py \
  --manifest "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/eval-manifest.full.seg05.json" \
  --weights-dir "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector" \
  --device cuda --conf-threshold 0.5 --task M2-DOCTR-QUAL-C4 \
  --out verification/M2-DOCTR-QUAL/qualification/results-formal-manga_rt_detr_v2-cuda-seg05.json

# pad 抵消附报：加 --strip-block-pad 6.0
# conf 敏感性附报：--conf-threshold 0.3
```

PowerShell 写法（等价，DSH r1 R8；在 worktree 根目录执行）：

```powershell
$env:PYTHONPATH = "src"
& "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4-gpu-py312/Scripts/python.exe" `
  experiments/M2-DOCTR-QUAL/eval_detection_manga.py `
  --manifest "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/eval-manifest.full.seg05.json" `
  --weights-dir "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector" `
  --device cuda --conf-threshold 0.5 --task M2-DOCTR-QUAL-C4 `
  --out verification/M2-DOCTR-QUAL/qualification/results-formal-manga_rt_detr_v2-cuda-seg05.json
```

（results JSON 内的 `reproduce_command` 字段为 POSIX 形式的正式产物，不重写；本节双写即 AC4 的可执行口径。）

证据物（均在 `verification/M2-DOCTR-QUAL/qualification/`，均带 `manifest_sha256=4f16425a...`、权重 sha256、`reproduce_command` 字段）：

| 文件 | 内容 |
|---|---|
| `results-formal-manga_rt_detr_v2-cuda-seg05.json` | 正式运行（Gate 输入），elapsed 38.9 s |
| `results-formal-manga_rt_detr_v2-cuda-seg05-padoffset.json` | pad 抵消附报 |
| `results-formal-manga_rt_detr_v2-cuda-seg05-conf03.json` | conf 0.3 敏感性附报 |
| `c4-manga-domain-report.md` | 本报告 |

复现核验（AC4，2026-09-30）：按上方正式命令重跑 `--limit 24` 抽样（EXIT=0），与正式 JSON 前 24 条 per_region 逐字段比对 **0 diff（确定性复现）**；核验产物 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/results-repro-check24.json`（外部路径，不入库）。

预览图（GT 绿框 / 检测红框）落 gitignored 外部路径 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/previews/`，不入库。
