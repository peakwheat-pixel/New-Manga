# M2-SFX-TRAIN-V2 训练 V2 交付报告（T2-V2：own-manga 接入+A/B 基座重训+同链路对照评测）

- docs commit：2768c6c1（本返修 commit 见链尾——DSH r1 P4-12）
---
task: M2-SFX-TRAIN-V2
author: ZCode
date: 2026-10-05
base_commit: 4e881720
branch: agent/zcode/M2-SFX-TRAIN-V2
delivery_commits: 75148bc4（AC1 prep）/ 093631d2（AC2 train）/ ba94fa76（AC3 eval）/ docs 提交（AC4/AC5：本报告+Handoff+Task 回填）
independent_review: 独立复核（非作者，全部基于复核轮独立执行的重算与命令，未采信文档转述）= **PASS**（四项复核全部实测通过；附 1 项中级登记口径错位 + 2 项低级/澄清，见 §6）
report_caliber: 本文数字除标注「引自独立复核记录」外，均由文档收尾轮从盘上产物复算/重读确认（results.csv 双 fitness 口径重算、全部权重 sha256 盘上重算、eval JSON 逐框重读、训练 log TRAIN_RESULT_JSON/EarlyStopping/OOM/初始 loss 提取、git diff 零 src 实测）
---

## 0. 摘要与定位

**V2 = own-manga 冻结池接入后的 A/B 基座重训 + 同链路对照评测；仍不是正式 G1-G8 Gate**（正式 Gate 属 T3，沿 V1 合同口径）。

- **数据结论：训练集翻 2.6 倍。** train 343→**901 页/2304 框**（19 R2 真实+324 合成+558 own-manga）；考卷（densho810/vol05 组 2 页 5 框）、val（4/53）、test（2/5）与 V1 完全不变——与合同 AC1 期望全数命中（`prepare-summary.json` `expected_vs_actual` 逐项相等，fail-fast 断言通过）。
- **训练结论：A/B 双版完整完成（无 skip）。** A 版 v2a（官方 yolo11s-seg.pt）与 B 版 v2b（anonimkaq4 近域基座）同口径各训一跑，均早停收敛、零 OOM。**两版 best 的 val 指标对比**不构成结论**——val 无判别力（53 框中 51 框落于三方均零召回的 KO 长条页，仅 2 个 crop 框可判），A/B 判定只依据考卷实测（DSH r1 P2-1：同口径被评权重 A(ep79) wrapper 0.020833 vs B(ep45) 0.018338，A 更高；此前「持平级」对比误将 B 版未保存的 epoch49 指标与 A 版已保存权重并列）
- **评测结论：V1→V2 directional 大幅改善。** BJ 考卷新模型 0/5（V1）→ **v2a 4/5、v2b 5/5**；B 版考卷零误检 precision 1.0 超 chiqui7 独立复跑（5/5，P 0.8333）。KO crop 页 2/2 全中（V1 0/2）。**结构性发现如实登记：KO 长条页 4 样本 56 框三方（含现役 chiqui7 独立复跑）全部 0/56**——瓶颈在推理序列口径（整页 letterbox vs 切块）非模型权重，归 T3/T4 议题。
- **P2-1 整改落地：chiqui7 对照从「预标注引用」（V1）改为「同链路独立复跑」（V2）**——生产 pin d87389af 权重原样加载走同一 `SfxDetectionProvider` 序列（`eval_v2.py:129-131` sha 自检、`:197-201` provider.detect 真调用），循环性特别核查裁定整改成立（§6.3）。
- 独立复核 **PASS**（§6）：重切/训练真实性/评测复算/零 src 四项全部实测通过；ISSUE-A（v2b best 双口径登记错位，中级）如实登记（§2.3）。

---

## 1. 数据：own-manga 冻结池接入 + train-v2 重切（AC1）

证据：`verification/M2-SFX-TRAIN-V2/prepare-summary.json`（Git 内摘要）；数据本体 `training_data/sfx-v1/train-v2/`（gitignored 外部树，`.gitignore:13`）。提交 75148bc4。

### 1.1 分集数字（对照合同 AC1 期望）

| split | 样本 | 框数 | 构成 | 合同期望 |
|---|---|---|---|---|
| train | **901** | **2304** | 19 R2 真实 + 324 合成 + 558 own-manga（partial 140 / pseudo 418） | 901 / 约 2304 ✓ |
| val | 4 | 53 | 4 真实（逐样本不变） | 4/53 ✓ |
| test | 2 | 5 | 2 真实（逐样本不变） | 2/5 ✓ |
| challenge | 2 | 5 | densho810/vol05 组考卷（沿 V1 不变） | 2/5 ✓ |

- own-manga 六组恰 558 页全在 train：v01 125 / v02s 103 / v12 88 / v13 105 / v15 53 / v16 84（框数 481/319/203/295/153/287，合计 1738）。
- **指纹** `345deeb72b9a609ba9a42eeeabec0506e2efe51a14e6176c6a7df884ddeb0e63`（seed=20261004；T1a `splits.split_fingerprint` 工具零重写复用）。R2 出厂指纹=`564498e13651bb2e…ccfa`（对照）。
- **重切方法**：T1a `assign_splits(force=True, pinned=…)` 函数参数传参对全量 909 重算（**不改 T1a splits.py 交付物**）。pinned=`densho810/vol05→challenge` + own-manga 六组与 synthetic→train；`moved` 恰=`[pre-bj17, pre-bj18]`（train→challenge）；对 R2 `manifest.r2.json` 351 样本逐样本核对：非 vol05 组 **349/349 split 零漂移**（复现 R2 出厂分桶）。
- **组隔离**：全量 909 样本 20 个 group→set(split) 重算，违例=0。
- **考卷零重叠三层断言 PASS**：own-manga 558 页 sha256 与 R2 351 页 sha256 交集=0（组名/样本 id/页图 sha256 三层，challenge 2 页专项复核无泄漏）。
- **合同括号笔误如实登记**：AC1 原文「（343+558；629+1738 框）」中 629 为笔误——V1 实测 train=566 框，566+1738=2304 与合同「约 2304 框」自洽（prepare-summary.json `expected_vs_actual.note`）。

### 1.2 数据集健全性

- **names 双通道 PASS**：dataset.yaml 字面行解析与 pyyaml 6.0.3 独立解析均 `{0:bubble, 1:panel, 2:sfx, 3:text}`，且与 `src/infrastructure/providers/detection_sfx.py` `SFX_CLASS_MAP`（sfx=2）一致。
- **ultralytics 8.4.172 `check_det_dataset` 扫描 PASS**（训练 venv M2-SFX-FINETUNE-gpu-py312）：challenge 键可扫描，四分集图像计数 901/4/2/2。
- **label 口径**：R2 351 全量与 R2 yolo 树原分集同名 label 逐字节相等（重切只动 split 归属、不动框几何）；own-manga 558 走导出后自洽校验（行数==框数 / cls 恒 2 / 坐标归一化域合法）；pseudo 含空框页按 YOLO 背景图惯例导出空 label。
- **图像**：909 张 copy2 后大小全量断言相等；sha256 抽验 19 张（R2 侧 13 张含 BJ 5 页必验 + own-manga 每卷 1 张共 6 张，dst==源==manifest.image.sha256 三方一致）。
- polygon 口径=T1a 实例包络（归一化 6 位小数，cls 恒 2=sfx）；own-manga 558 页为 .jpg 与 R2 系 .png 混树（YOLO 按文件扫描，无影响）。

### 1.3 考卷（沿 V1 不变）

challenge=densho810/vol05 组 `pre-bj17`（BJ17，vol05_p0167，竖排毛笔假名主攻形态，2 框：R2-BJ17-B00 conf 0.932 + B01 0.9096）+ `pre-bj18`（BJ18，vol05_p0065，竖排/斜置粗毛笔片假名，3 框：R2-BJ18-B00 0.8951 + B01 0.8636 + B02 0.8333）=5 框，与 R2 出厂框几何逐字节一致（独立复核重算确认）。排除留痕：R2-BJ17-B02 仲裁 delete（气泡对白非 SFX）不在考卷。同组 pseudo pre-bj25（零框负证据）不入训练 manifest。

---

## 2. 训练 V2 A/B 双版（AC2）

证据：`verification/M2-SFX-TRAIN-V2/raw/train-v2a-log.txt`（2.16MB）+ `raw/train-v2b-log.txt`（1.49MB，全程 stdout 均入 Git）；run 产物 `training_data/sfx-v1/train-v2/runs/{v2a,v2b}/`（gitignored）。提交 093631d2。

### 2.1 A 版 v2a（官方基座）

- **基座**：Ultralytics 官方 `yolo11s-seg.pt`，sha256 `1caa81c0195412efa411b632bcfb8c184939dddb6ae41f6a80c41b211ff257c3`（20,669,228 B；文档收尾轮盘上重算与 log 登记逐位一致）。
- **口径（沿 V1）**：imgsz 1024 / batch 8 / epochs 150 / patience 30 / seed 20261004 / device 0。
- **运行**：**109/150 epochs 早停**（log EarlyStopping 行 best@79；79+30=109 数学自洽；results.csv 实测 109 行）。耗时 **1816.4s ≈ 30.3 min** @RTX 5070 Ti。**batch=8 全程无 OOM**（log grep「out of memory」=0；无需减半重试）。
- **best fitness 行（双口径恰同为 epoch 79，文档收尾轮 results.csv 重算）**：mAP50(B)=**0.02833**、mAP50-95(B)=**0.02000**、precision(B)=0.51157、recall(B)=0.03774；wrapper box-fitness=0.020833。
- **results.csv 末行（epoch 109）**：mAP50(B)=0.02367 / mAP50-95(B)=0.01453。
- **权重 sha256（log TRAIN_RESULT_JSON 登记，文档收尾轮盘上重算一致）**：best.pt=`3e6276cf9fc340570d3f302052bd5d88b249a57600434471fe91c7065a5f65d4`（20,584,356 B）；last.pt=`c9c1b774415af61535d8b2b69910db47bfcc53b526d69694854b3f7f922544a8`。
- log=`verification/M2-SFX-TRAIN-V2/raw/train-v2a-log.txt`（入 Git）；run_dir=`training_data/sfx-v1/train-v2/runs/v2a/`（gitignored）。

### 2.2 B 版 v2b（近域基座）

- **基座**：按 T0 `verification/M2-SFX-FINETUNE-PREFLIGHT/preflight-report.md:69` 指路，从 HF `anonimkaq4/manga-page-element-segmentation` 下载 `snapshots/yolo11s_1024_b8/manga-yolo11s-seg-validation-best.pt`（**81,340,348 B**；sha256 `1f0fd609e7dc29c831255db67586ed5623f9bebae6a1e29fae197c1c6d7b77e0`，文档收尾轮盘上重算与 log 登记逐位一致）。类别面登记 `0:frame / 1:speech_bubble / 2:character`（无 sfx 无 text）与 preflight 登记逐字一致；`license: other` 未审计——留证快照 `raw/b-base-readme-snapshot.md`（含 Manga109-s 衍生声明「does not include or grant rights to the original Manga109-s images or MangaSeg annotations」）与 `raw/b-base-snapshot-metadata.json`、`raw/b-base-args.yaml`。
- **换头留痕**：ultralytics 迁移日志 `Transferred 555/561`（head 层 3→4 类重初始化）。
- **口径**：与 v2a 完全同口径（imgsz 1024 / batch 8 / epochs 150 / patience 30 / seed 20261004 / device 0）。
- **运行**：**75/150 epochs 早停**（log EarlyStopping 行 best@**45**；45+30=75 自洽；results.csv 实测 75 行）。耗时 **1312.0s ≈ 21.9 min**。batch=8 全程无 OOM（grep=0）。
- **TRAIN_RESULT_JSON 登记（wrapper 口径）**：best_epoch=**49**（`train_v2.py:145` 自定义 box-fitness 0.9·mAP50-95(B)+0.1·mAP50(B) 的 argmax；fitness=0.020517）：mAP50(B)=**0.03111**、mAP50-95(B)=0.01934、precision(B)=0.62142、recall(B)=0.03774。
- **results.csv 末行（epoch 75）**：mAP50(B)=0.02781 / mAP50-95(B)=0.01767。
- **权重 sha256**：best.pt=`c22f0175ffe7b453fd660161831aa9fce2a736fc32d29e574650ba9731131c08`（20,578,084 B）；last.pt=`112732c2601fc881dd5ec19a353994b6a0fd98bf4833284a907b24f127348bdf`。
- log=`raw/train-v2b-log.txt`（入 Git）；run_dir=`runs/v2b/`（gitignored）。

### 2.3 双口径登记错位（ISSUE-A，中级，诚实登记）

**登记口径错位属实（文档收尾轮 results.csv 重算证实）**：commit 093631d2/ba94fa76 与 TRAIN_RESULT_JSON 称 v2b「best@49、best mAP50(B)=0.03111」——该 49 是 wrapper 自定义 box-fitness（`train_v2.py:145`，0.9·B95+0.1·B50）的 argmax（epoch 49 fitness=0.020517 为最大，属实）；但 **best.pt/best.onnx（评测实际用的权重）由 ultralytics 按 mask-fitness（0.1·mAP50(M)+0.9·mAP50-95(M)）保存于 epoch 45**（该行 mAP50(B)=**0.02786**、mAP50-95(B)=0.01728、mAP50-95(M)=0.01991 为最大；log EarlyStopping 行 best@45 同源）。即**登记的 B 版 best mAP50(B)=0.03111 不是被评权重的指标**（被评权重=epoch 45，mAP50(B)=0.02786）。v2a 两口径恰同为 79，无此问题。

定性：**登记口径误导，非数字造假**——两个 epoch 的数字均真实存在于 results.csv，早停数学（45+30=75）自洽，被评权重 sha 链完整。建议后续文档与 T3/T4 呈报一律标注双口径（wrapper best_epoch=49 vs ultralytics best.pt=epoch 45）。

> **DSH r1 P2-2**：commit `093631d2` message 中 A/B「持平级」框架基于 B 版**未保存**的 epoch49 指标（wrapper box-fitness argmax），与本节双口径说明冲突——**以本报告口径为准**；历史 commit message 不改写。

### 2.4 A/B 对比口径与初始 loss

- **两版 best 的 val 指标对比**不构成结论**——val 无判别力（53 框中 51 框落于三方均零召回的 KO 长条页，仅 2 个 crop 框可判），A/B 判定只依据考卷实测（DSH r1 P2-1：同口径被评权重 A(ep79) wrapper 0.020833 vs B(ep45) 0.018338，A 更高；此前「持平级」对比误将 B 版未保存的 epoch49 指标与 A 版已保存权重并列）
- **初始 loss B 显著低于 A，近域先验可见（文档收尾轮 log 提取）**：epoch 1 首 iter seg loss v2a=**9.196** vs v2b=**4.814**（近域基座起点约低一半）；epoch 1 末 iter 已接近（v2a 2.423 vs v2b 2.544）——起点优势在一个 epoch 内被追平，收敛后两版持平。复核材料口径「seg 2.57 vs 9.2」对应 v2b epoch 1 收尾即时值（2.544≈2.57 量级）与 v2a 首迭代值，取样点不同、方向一致。
- torch 读 best.pt train_args 确认两版基座、同口径 epochs150/patience30/imgsz1024/batch8/seed20261004、names 四类正确（独立复核记录）。
- 裁量点处置：单类 nc=1 第三跑**未做**（A/B 完成即达合同最低要求，时间盒内不追加）；v15 组钉 val 不做（沿合同）。

---

## 3. 导出 + 生产序列冒烟（AC3 前半，零 src）

证据：`verification/M2-SFX-TRAIN-V2/raw/export-smoke-v2.json`（逐步 STEPS + `"exit": 0`）。提交 ba94fa76。

- **best.onnx**：v2a=`27d162e94d7dd2150b177f5636613e3bfce836dfdb08240975b86fce85b97d43`、v2b=`944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d`（两文件大小恰好同为 **40,824,255 B** 但 sha 不同——同架构导出正常；文档收尾轮盘上重算一致）。
- **SHA 门先证后指（两版均正确命中）**：v2a/v2b 导出物直接调 `_build_engine` → **`PROVIDER_FAILED` 正确拒跑**（门对外来权重生效，两次 `sha_gate.fired` 实证）→ 随后进程内重指放行，全链冒烟 **EXIT=0**，零 src、生产 pin `SFX_WEIGHTS_SHA256=d87389af…`（`src/infrastructure/providers/detection_sfx.py:110-111`）零改动。
- **全链逐字零漂移（两版同）**：names metadata 逐字 `{0: 'bubble', 1: 'panel', 2: 'sfx', 3: 'text'}`（断言 PASS）；imgsz=1024（`metadata_parsed`，raw=[1024,1024]）；输出张量 `(1, 40, 21504)`＝生产假设 (1,40,N)（4+4cls+32mask）；合成页双档 conf 结构合法（`class_filter=sfx`、`coordinate_space=page-global`）。
- **杂注（cosmetic，如实登记）**：`export-smoke-v2.json` 中 v2b 段 `sha_gate.ok` 的 `production_pin` 字段显示 `27d162e94d7d`（v2a 重指残留值）——V1 蓝本单版无此暴露，属脚本字段回显残留；**门语义由两次 `sha_gate.fired` 实证**（两版外来权重均先被正确拒绝），不影响证据链。

---

## 4. 三方同链路评测（AC3 后半）+ V1↔V2 同口径对比

证据：`raw/eval-v2a.json` / `raw/eval-v2b.json` / `raw/eval-chiqui7-rerun.json`（逐框明细）+ `raw/eval-comparison.json`（汇总+structural_finding+v1_baseline_git_reference）。提交 ba94fa76。

### 4.1 口径与 P2-1 整改落地

- **GT**：challenge 2 页 5 框（BJ 考卷）+ val 4 样本 53 框 + test 2 样本 5 框 = **8 页 63 框**，与 V1 同批（AC1 重切未动 challenge/val/test；断言通过）。
- **匹配**：box IoU≥0.5、pred conf 降序贪心；**conf≥0.50 生产冻结 / ≥0.20 宽松双口径**。
- **P2-1 整改（DSH V1-r1）落地实证**：chiqui7 对照=**同链路独立复跑**——生产 pin d87389af 权重**原样加载**（`eval_v2.py:38` 登记期望值、`:129-131` 运行前 `assert prod_sha == PROD_PIN_HEAD`）走同一 `SfxDetectionProvider.detect` 生产序列（`:197-201` 真调用），**非预标注引用**。v2a/v2b=进程内重指同序列。三方同序列可直比。
- V1 基线数字自 Git `verification/M2-SFX-TRAIN-V1/raw/eval-challenge.json` + `eval-kodelta.json` 引用（同考卷同 GT 同阈值同 IoU；new_model onnx fb60b460…）。

### 4.2 BJ 考卷 2 页 5 框（主攻形态）

| 方 | 严格 conf≥0.50 | 宽松 conf≥0.20 |
|---|---|---|
| **v2a**（官方基座） | **4/5**（P=0.80，5 pred；漏 R2-BJ18-B00；BJ17 页多 1 误检 conf 0.6711） | 4/5（6 pred，P=0.6667） |
| **v2b**（近域基座） | **5/5**（**P=1.0，5 pred 零误检**） | **5/5**（P=1.0） |
| chiqui7 独立复跑（现役） | **5/5**（P=0.8333，6 pred，IoU 0.999 级——GT 本源自其检出，符合预期） | 5/5（P=0.8333） |
| V1 基线（Git 引用） | 0/5（0 检出） | 1/5（P=0.3333，3 pred） |

- v2a 唯一漏检=R2-BJ18-B00；chiqui7 复跑唯一误检 conf 0.8634=**曾被仲裁 delete 的 R2-BJ17-B02 气泡框**（与 R2 判定链自洽，沿 V1 观察）。
- **B 版考卷零误检 precision 1.0，与 chiqui7 独立复跑同级（差 1 个误检——chiqui7 唯一误检=曾被 R2 仲裁 delete 的气泡框；5 框考卷功效不足以判优劣，DSH r1 P3-5）**。

### 4.3 KO val+test 6 样本 58 框

| 方 | conf≥0.50 | conf≥0.20 |
|---|---|---|
| v2a | **2/58**（P=0.5，4 pred） | 2/58（P=0.3333） |
| v2b | **2/58**（P=0.5，4 pred） | 2/58（P=0.5） |
| chiqui7 独立复跑 | **0/58**（n_pred=2 全不匹配） | 0/58 |
| V1 基线（Git 引用） | 0/58 | 0/58（5 pred 全不匹配） |

- 两版的 2 中均来自 **imp-ogkalu crop 页 2/2 全中**（imp-ogkalu-k08-r025 1/1 + imp-ogkalu-k09-r071 1/1；V1 为 0/2）——近域 crop 形态可学。
- chiqui7 复跑在该 2 crop 页 0/2（其检出 2 框与 GT 不匹配）。

### 4.4 结构性发现：KO 长条页 4 样本 56 框三方全部 0/56

> **DSH r1 P3-6 溯源注**：KO val/test 的 GT 框本身派生于 chiqui7 的 tile 扫描检出（R1 `stage1_preannotate.py` `scan_mode=tile_690x1024_overlap128`，注释原文=webtoon 宽 690 超长条整页 letterbox 会缩到 172px 丢细节）——KO 数字并非跨模型中立基准；「两口径不可直比」的物理根因=tile（原生分辨率切块）vs letterbox（整页缩放）。

**【KO 页 only 4 样本 56 框】三方全部 0/56（含现役 chiqui7 独立复跑 n_pred=0）**——如实登记：

- KO 页=690×51971~100480 长条 webtoon（aspect 1:31~1:146：pre-k02 600×18401、pre-k01 690×62133、pre-k08 690×51971、pre-k09 690×100480）；**整页 letterbox 1024 下 SFX 亚像素化**。
- **现役模型在生产整页序列下同样零召回**——这是 P2-1 整改（独立复跑）暴露的、被 V1 预标注引用口径掩盖的**序列级事实**。
- **V1 预标注引用口径的 chiqui7 56/56 系素材线切块扫描采集产物**（R1 KO 域候选=切块扫描入库），与整页推理口径**不可直比**（V1 报告 §5 已将该口径定性为「GT ⊂ 候选池的自洽上界」；本轮复跑给出序列口径真值）。
- **瓶颈在推理序列口径（整页 letterbox vs 切块）非模型权重**——V2 新模型 KO 页 0/56 与现役持平（无回退）；序列口径实验（tiling/分辨率策略）归 **T3/T4 议题**，不在本 Task 范围内解决。

### 4.5 全 8 页 63 框汇总（conf≥0.50）

| 方 | matched/63 | precision | n_pred |
|---|---|---|---|
| v2a | 6/63 | 0.6667 | 9 |
| **v2b** | **7/63** | **0.7778** | 9 |
| chiqui7 独立复跑 | 5/63 | 0.625 | 8 |

### 4.6 V1↔V2 同口径对比与结论纪律

- **方向性结论（同口径可直比部分：新模型侧）**：V1→V2 BJ 考卷 0/5→4/5、5/5；KO crop 0/2→2/2；KO 长条页 0/56→0/56（持平）。**支持 own-manga 接入+V2 重训方向**。
- **A/B 同口径**：B 版考卷表现略优（5/5 零误检 vs 4/5），KO 持平无回退；全 63 框 v2b 7/63 vs v2a 6/63。
- **措辞纪律**：directional 评测统计功效低（考卷 5 框/KO 56 框单点观测），**禁用「显著」**；0 也如实；V2 数字仍不作门判定（正式 Gate 属 T3）。
- V1 侧 chiqui7 预标注口径（56/56、5/5）与 V2 复跑口径**不可直比**（`eval-comparison.json` `caliber_note`）；可直比的是新模型 V1↔V2 与 V2 轮三方同序列数字。
- 复跑口径对 V1 的覆盖扩展：独立复跑覆盖全部 8 页——含 imp-ogkalu-* 2 页（V1 预标注口径下 chiqui7 基线不可得的页，因预标注源=ogkalu rt-detr 非 chiqui7）。

---

## 5. 作者侧复核（workflow 内，非本 Task 正式 Review）= PASS；正式独立 Review 见 doc/reviews/M2-SFX-TRAIN-V2-2768c6c1-dsh-r1.md（DSH r1=approved_with_conditions）

> 复核记录要点引自复核会话（全部结论基于复核轮**本轮独立执行的重算与命令**，未采信任何文档转述）；其中 §2.3 双口径、§2.1/2.2 权重 sha、results.csv 行数、§1.3 考卷 GT、§4 逐框匹配与漏检误检、log TRAIN_RESULT_JSON/EarlyStopping/OOM、§3 sha 与 pin、零 src diff 等，文档收尾轮已按同一口径重算/重读，全部一致。

**【1. 重切——全部重算通过】**
- manifest.train-v2.json 全量 909 样本重算：train 901 页/2304 框、val 4/53、test 2/5、challenge 2/5；own-manga 六组恰 558 页全在 train；challenge 恰 densho810/vol05 组 pre-bj17(2 框)+pre-bj18(3 框)，与 R2 出厂框几何逐字节一致。
- 组隔离全量重算：20 个 group→set(split) 违例=0；对 R2 manifest.r2.json 351 样本逐样本零漂移核对：非 vol05 组 349/349 split 逐一相同，moved 恰=pre-bj17/pre-bj18。
- own-manga 入册包（`task-envs/own-manga-ingest/own_manga_manifest_records.json`）与 manifest 双向核对：558 sample_id 集合全等、框数逐条一致、合计 1738 框；own-manga 558 页 sha256 与 R2 351 页 sha256 交集=0（challenge 2 页专项亦无交集）。
- names 双通道：dataset.yaml 字面行解析与 pyyaml 解析均 `{0:bubble,1:panel,2:sfx,3:text}`，与 `detection_sfx.py` 的 SFX_CLASS_MAP（sfx=2）一致。
- validate 复跑抽样 20 条（random.seed=20261004 从 558 抽样，id 列表已留存）：图像在盘、sha256 真实重算与登记一致、框坐标全在图像域内、cls 恒 sfx、包记录与 train-v2 manifest 框逐值一致、YOLO label 行数==框数/cls==2/坐标归一化域合法、images/train 同名图像在盘——**20/20 全过**。

**【2. 训练真实性——盘上重算通过，1 项口径错位（ISSUE-A，见 §2.3）】**
- 权重 sha 重算：runs/v2a best.pt=3e6276cf…/last.pt=c9c1b774…，runs/v2b best.pt=c22f0175…/last.pt=112732c2…，与两份训练 log 末行 TRAIN_RESULT_JSON 登记值逐位一致；weights/v2a/best.onnx=27d162e9…、weights/v2b/best.onnx=944e8114…（两文件大小恰好同为 40824255B 但 sha 不同），与 export-smoke-v2.json 一致。基座实测：yolo11s-seg.pt=1caa81c0…、anonimkaq4-manga-yolo11s-seg-validation-best.pt=1f0fd609…(81340348B)，与 log/commit 登记一致；torch 读 best.pt train_args 确认基座、同口径与 names 四类正确。
- results.csv 重算：v2a 109 epochs（1-109）、v2b 75 epochs（1-75），与早停声明一致；早停自洽（v2a log EarlyStopping 行 best@79，79+30=109；v2b log 行 best@45，45+30=75）——log 行与 csv fitness 重算互相印证。
- ISSUE-A（中级）：登记口径错位——TRAIN_RESULT_JSON/commit 称 v2b best@49（wrapper box-fitness argmax，属实），被评 best.pt 实为 ultralytics mask-fitness 保存的 epoch 45（mAP50(B)=0.02786）；登记的 0.03111 不是被评权重的指标。登记口径误导、非数字造假；建议后续文档标注双口径。

**【3. 评测复算（BJ17 页三方逐框 IoU）——重算通过】**
- GT 从 manifest.challenge.json 重读（pre-bj17：R2-BJ17-B00 [1660.4,2394.9,1773.2,2624.7]、B01 [1816.3,2123.4,1921.0,2383.6]），用 eval_v2.py 同款 iou_xyxy+conf 降序贪心独立重算：三方在 0.5/0.2 双口径下 matched/n_pred/配对索引/conf 与 eval-{v2a,v2b,chiqui7-rerun}.json 完全一致（BJ17 均 2/2；v2a 多 1 误检 conf 0.6711、chiqui7 多 1 误检=曾被判 delete 的 B02 框 conf 0.8634、v2b 零误检）；BJ18 页抽查同样一致（v2a 2/3、v2b 3/3、chiqui7 3/3→BJ 汇总 4/5、5/5、5/5 与 summary 吻合）。IoU 数值第 4 位小数微差（如 0.9564 vs 0.956、chiqui7 1.0 vs 0.9995）系 eval 匹配用未舍入原始 float 而复核用 json 内 0.1px 舍入值的口径差，不影响 ≥0.5 判定。

**【3.5 循环性特别核查——P2-1 整改成立】**
- chiqui7-rerun 的 BJ17/BJ18 共 6 个预测框（坐标+conf）与 ANNOTATE-R2 `worksheet-bj-new.json` 候选框（R2-BJ17-B00/B01/B02、R2-BJ18-B00/B01/B02，sources=chiqui7-scan）**逐值完全相同**——ask 指定判据字面触发。但**四重证据链支持「真独立推理」而非引用**：
  1. `eval_v2.py` 全文无任何预标注池/worksheet 读取路径，预测来自 `provider.detect()` 真调用（`eval_v2.py:197-201`），运行前 `assert` 生产 onnx sha==pin（`:129-131`）；
  2. R2 BJ 域候选本就产自 chiqui7 **整页 letterbox** 扫描（`experiments/M2-SFX-ANNOTATE-R2/stage1_preannotate_bj_new.py:7,196-197` scan_mode=fullpage_letterbox, n_tiles=1），同权重+同页图+同生产序列的确定性输出必然逐值相同；
  3. KO 4 页复跑 n_pred=**0**/56 vs 候选池 56 框完全不同——若引用池子不可能为 0，反证成立；
  4. **决定性实证**：复核会话本人用生产 pin 权重（M2-SFX-DETECT/weights/yolo11s-seg.onnx）经生产 SfxDetectionProvider 序列独立复跑 pre-bj17，0.5/0.2 双口径输出与 eval-chiqui7-rerun.json 逐值完全一致——推理可达性证实。
- **裁定：不构成循环性未整改，P2-1 整改成立；与 ask 字面判据的冲突如实登记。**

**【4. 零 src——核对通过（文档收尾轮同口径实测）】**
- `git diff --name-only 4e881720..ba94fa76`：16 个文件全部落在 doc/tasks/M2-SFX-TRAIN-V2.md、experiments/M2-SFX-TRAIN-V2/{4 个新脚本}、verification/M2-SFX-TRAIN-V2/{prepare-summary.json+10 raw}；`-- src/` 改动数=0；工作树对 HEAD 无未提交改动。
- 生产 pin 四处同值（三处文档+一处实测）：`src/infrastructure/providers/detection_sfx.py:111`、`experiments/M2-SFX-TRAIN-V2/eval_v2.py:38`、`verification raw/eval-chiqui7-rerun.json` model.sha256（eval-comparison.json sides.chiqui7_prod_rerun.model.sha 同值）均为 `d87389af4350954143a216bcfe40fd2ad93312cb136534e6073c9c740d98b646`；第四处=生产 onnx 文件 sha256 独立重算==pin（复核轮实测 True）。export-smoke-v2.json sha_gate.ok 步骤显示先证后指真实发生（两版均先按生产 pin 加载被拒后按自身 sha 放行）。

**【低级提示】**
- **ISSUE-B**：`training_data/sfx-v1/train-v2/export-summary.json`（gitignored 外部树，不入 Git）文件名与内容不符：内容实为 AC1 数据准备摘要（比 verification prepare-summary.json 少 yolo_layout/data_root_gitignored 两字段，08:03 生成），易误读为 AC3 导出摘要；AC3 导出摘要在 `verification raw/export-smoke-v2.json`。V1 train-v1 无同名文件。**不影响 Git 内证据链。**
- **未跑项（如实登记）**：未重放 v2a/v2b 侧的 ONNX 推理本身（评测数字的可信度由 sha 链+匹配结构一致+chiqui7 侧独立复现支撑）；ultralytics 扫描冒烟未在复核轮复跑（仅核对其登记与目录实况一致：images/{train,val,test,challenge} 计数 901/4/2/2 抽验相符；AC1 轮 PASS 登记在 prepare-summary.json）。

---

## 6. 诚实边界

> **DSH r1 P3-7 新增边界**：训练集内同样存在 KO 长条页（manifest.train 中 6 页 height≥10000：80494/28156/46000/81776/131289/100674=pre-k03..k07/k10）——其 SFX 框在 imgsz=1024 整页 letterbox 下同为亚像素，对 901 页训练集构成潜在标签噪声；T3 序列口径实验（tile vs letterbox）须一并处置训练侧。

- **own-manga 框坐标=模型输出**（chiqui7/yolo11s-seg.onnx，0.1px）**未手工收紧**——定位精度受 chiqui7 上限约束；partial 140 页=用户核验 SFX 存在性（annotation_grade=human-verified-existence）但框未手工收紧，不冒充 complete；pseudo 418 页=模型产出+AI 内容复核过滤，无逐框人工确认。标签噪声影响 V2 不做 partial/pseudo 分层消融（合同时间盒裁量），如实登记为边界。
- **chiqui7 同源性对毛笔竖排无补**：own-manga 候选框全部源自 chiqui7 检出（AI 复核过滤假阳但覆盖不了 chiqui7 漏检类型）；chiqui7 弱项（毛笔竖排漏检）需独立补框通道，本包不覆盖；**BJ 主攻形态（考卷 BJ17/18 竖排毛笔）不在本包覆盖内**——V2 的 BJ 改善来自整体 SFX 监督量翻倍（566→2304 框）与近域基座的一般化效应，非该形态直接补标。
- **val 仅 KO 4 页 53 框**：训练期 val 指标噪声大，两版 best 的 val 指标对比**不构成结论**——val 无判别力（53 框中 51 框落于三方均零召回的 KO 长条页，仅 2 个 crop 框可判），A/B 判定只依据考卷实测（DSH r1 P2-1：同口径被评权重 A(ep79) wrapper 0.020833 vs B(ep45) 0.018338，A 更高；此前「持平级」对比误将 B 版未保存的 epoch49 指标与 A 版已保存权重并列）
- **KO 页 0/56 是序列口径瓶颈**（§4.4），不是 V2 权重的回退；V1 预标注口径 56/56 与整页推理口径不可直比。
- **统计功效低**：directional 评测，禁用「显著」；V2 数字不作门判定。
- **许可备案**：A 版基座=官方 yolo11s-seg.pt AGPL-3.0（用户许可降权备案覆盖，沿 T0）；B 版基座=`license: other` **未审计**（快照留证 `raw/b-base-readme-snapshot.md`，含 Manga109-s 衍生声明；上生产面前须补审计）。衍生权重均 gitignored 外部树，未入库未分发；生产 pin 零改动。
- **B 版基座类别顺序注（澄清）**：README 快照内示例 checkpoint（yolo11m_1024_synthetic_mangaseg）的类别 ID 顺序为 `0: character, 1: frame, 2: speech_bubble`，与本次实际下载 yolo11s_1024_b8 checkpoint 的 preflight 登记（`0:frame/1:speech_bubble/2:character`）顺序不同——属同 repo 不同 checkpoint 的差异；换头训练后 names 被生产四类契约逐字覆盖（§3 断言 PASS），对训练/导出正确性无影响。
- 训练曲线/run 产物 gitignored；Git 只进摘要、全程日志与评测 JSON。
- ISSUES 汇总：**1 项中级**（ISSUE-A：v2b best 双口径登记错位，§2.3——后续文档标注双口径）；**2 项低级/澄清**（ISSUE-B：gitignored 树 export-summary.json 文件名误导，§5；B 版基座 README 类别顺序澄清，本节）。

---

## 7. T3/T4 材料刷新（AC5，交编排/用户；不随本 Task 释放）

### 7.1 V2 结果对 T3（评测 Gate G1-G8）可达性的含义

1. **考卷可达性已证**：densho810/vol05 考卷（BJ 主攻形态）在 V1 全零（0/5）之后，V2 两版达 4/5、5/5——901 页/2304 框规模下考卷**可通过训练改善**，支持 V1「正样本饥渴」首要假设的方向；且 B 版（近域基座）考卷零误检达 P 1.0，**超过现役 chiqui7 独立复跑（P 0.8333，唯一误检=仲裁 delete 的气泡框）**——G1 BJ 门的质量可达性从「未证」升级为「directional 已证、待正式 Gate 定量」。
2. **BJ 深度扩标仍是主要瓶颈假设**：own-manga 不含毛笔竖排形态（chiqui7 同源性边界），V2 的 BJ 改善不能外推到「该形态已学透」；train 内该形态真实正样本仍仅 6 框（BJ16×3+BJ23×2+BJ24×1）。T3 前置扩标候选沿 V1 呈报口径不变（conf<0.2 层 16 单元+44 张 BJ 候选池页+10 张 KO 候选）。
3. **KO 门必须先解决序列口径**：KO 长条页整页 letterbox 1024 下三方（含现役）0/56——**在序列口径（切块/tiling/分辨率策略）实验完成前，任何权重都无法通过沿用整页序列的 KO 门**。T3 Gate 设计须先做序列口径对照实验（切块扫描 vs 整页 letterbox 的召回差已是 0/56 vs 56/56 量级）；建议 T3 把「推理序列口径」列为 KO 域 Gate 的前置实验项。
4. **评测基线口径固化**：P2-1 整改模式（同链路独立复跑）应作为 T3 正式评测的对照基线口径（`eval_v2.py` 模式可复用，成本≈每方一次全序列推理）；预标注引用口径（V1）永久退役。
5. **A/B 基座结论供 T3 复用**：近域基座（B 版）考卷略优、起点 loss 低一半、收敛后持平——T3 若扩标后重训，B 版基座方向值得保留（同口径 A/B 一次对照成本≈52min GPU）。

### 7.2 T4（生产切换）pin 替换语义具体化（若未来改善成立）

1. **候选权重**：directional 口径下 v2b（best.onnx `944e8114…`）为优选（BJ 考卷 5/5 零误检 P 1.0、KO 持平、全 63 框 7/63 最优）；v2a（`27d162e9…`）次之。**切换与否=T4 用户裁决点，V2 数字不作门判定。**
2. **pin 替换语义**：生产 pin `SFX_WEIGHTS_SHA256`（`src/infrastructure/providers/detection_sfx.py:110-111`，现值 d87389af…）更新为通过门判定的新 onnx sha256（单值替换，SHA 门语义不变——本轮两次 `sha_gate.fired` 已实证对外来权重拒跑在位）。
3. **来源字段语义处置**：`SFX_HF_REPO`/`SFX_HF_REVISION` 现指 `chiqui7/yolo11-manga-seg@7f5f5c04`——V2 权重为本地产物（非 HF 发布物），切换时须一并处置：或将新权重建立 HF 发布通道后更新 repo/revision，或将来源语义改为本地发布通道登记。**src 改动=Codex 授权的 T4 专属新 Task；T2 零 src 红线不破。**
4. **KO 域切换影响=零（双向）**：序列口径解决前，V2 与现役在 KO 长条页同为 0 召回——切换不造成 KO 回退（0→0），也不带来改善；KO 改善路径在序列口径（T3/T4 实验），不在权重替换。
5. **许可门**：B 版基座 `license: other` 未审计——**若 v2b 上生产，许可审计是切换前置条件**（快照已留证）；A 版 AGPL 备案沿 T0 用户裁决。
6. **回退语义**：pin 为单值，切换后回退=恢复 d87389af 值+旧权重文件在位（chiqui7 权重随包 NSIS 通道不变）。

---

## 8. 证据索引

| 产物 | 路径 | 状态 |
|---|---|---|
| 数据摘要 | verification/M2-SFX-TRAIN-V2/prepare-summary.json | Git @75148bc4 |
| 训练全程日志 A 版（2.16MB） | verification/M2-SFX-TRAIN-V2/raw/train-v2a-log.txt | Git @093631d2 |
| 训练全程日志 B 版（1.49MB） | verification/M2-SFX-TRAIN-V2/raw/train-v2b-log.txt | Git @093631d2 |
| B 版基座留证（README 快照/args/metadata） | verification/M2-SFX-TRAIN-V2/raw/b-base-{readme-snapshot.md,args.yaml,snapshot-metadata.json} | Git @093631d2 |
| 导出冒烟+SHA 门（双版） | verification/M2-SFX-TRAIN-V2/raw/export-smoke-v2.json | Git @ba94fa76 |
| 评测逐框明细（三方） | verification/M2-SFX-TRAIN-V2/raw/eval-{v2a,v2b,chiqui7-rerun}.json | Git @ba94fa76 |
| 评测汇总+结构性发现+V1 基线引用 | verification/M2-SFX-TRAIN-V2/raw/eval-comparison.json | Git @ba94fa76 |
| 数据集/权重/ONNX/run 产物 | training_data/sfx-v1/train-v2/{dataset,weights,runs,manifest.*.json} | gitignored 外部树 |
| 实验脚本 | experiments/M2-SFX-TRAIN-V2/{prepare_dataset_v2,train_v2,export_smoke_v2,eval_v2}.py | Git |
| V1 基线（Git 引用） | verification/M2-SFX-TRAIN-V1/raw/{eval-challenge,eval-kodelta}.json | Git @merge 35cb3db0 |
| own-manga 入册包（只读） | G:/CODEX/New Manga.task-envs/sfx-synth-exp/own-manga-ingest/own_manga_manifest_records.json | 外部树只读 |

复现命令（venv=M2-SFX-FINETUNE-gpu-py312，ultralytics 8.4.172，RTX 5070 Ti）：
`python experiments/M2-SFX-TRAIN-V2/prepare_dataset_v2.py --step all`（AC1）→ `train_v2.py`（AC2 A/B 两跑）→ `export_smoke_v2.py`（AC3 冒烟，EXIT=0）→ `eval_v2.py`（AC3 三方评测）。指纹/组隔离/考卷 5 框断言内置 fail-fast。

---

*报告完。文档收尾轮（2026-10-05）：全部关键数字从盘上产物复算/重读确认；未复算处如实标注「引自独立复核记录」；未跑项如实登记（§5 低级提示）。*
