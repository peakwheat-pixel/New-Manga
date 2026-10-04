# M2-SFX-TRAIN-V1 训练 V1 交付报告（T2，A′ 路线首训）

---
task: M2-SFX-TRAIN-V1
author: ZCode
date: 2026-10-04
base_commit: a85d8853
branch: agent/zcode/M2-SFX-TRAIN-V1
delivery_commits: 45ae05a4（AC1 prep）/ 5fe62a91（AC2 train）/ c89c85e2（AC3+AC4 eval）/ docs 提交（AC5 本报告+Handoff+Task 回填）
independent_review: DeepSeek Harness 独立复核 = PASS（四项全过，3 条非阻塞观察项，见 §5）
---

## 0. 摘要与定位

**V1 = 管线验证 + directional 评测，不是正式 G1-G8 Gate**（Task 合同原文；正式 Gate 属 T3，待 BJ 深度扩标后）。

- **管线结论：训练/导出/生产链路全通。** AC1 重切→AC2 yolo11s-seg 微调→AC3 ONNX 导出+SHA 门+进程内重指生产序列冒烟，全链 EXIT=0、零 src、生产 pin `d87389af…` 零改动。
- **质量结论：V1 全面低于 chiqui7 现役（如实登记）。** BJ challenge 考卷（5 框）新模型严格 conf≥0.50 = **0/5**、宽松 conf≥0.20 = **1/5**；chiqui7 对照双口径 **5/5**。KO 页 4 样本 56 框新模型双口径 **0/56**（零检出）vs chiqui7 **56/56**。方向性结论与「343 样本小数据 + COCO 基座无 manga 先验 + 欠拟合（val R=0.019）」一致。
- **数字用途：仅作 V1↔V2 对比基线，不作门判定**（Task 合同 AC2 原文）。低数字如实登记，不凑数。
- 独立复核（DSH，非作者）四项全 PASS：重切正确性/训练真实性/评测复算/零 src 实证（§5）。

---

## 1. 数据：challenge 划拨重切 + train-v1 数据集（AC1）

证据：`verification/M2-SFX-TRAIN-V1/prepare-summary.json`（Git 内摘要）；数据本体 `training_data/sfx-v1/train-v1/`（gitignored 外部树）。提交 45ae05a4。

### 1.1 分集数字（对照 R2 出厂）

| split | R2 出厂 | train-v1 | 框数 | 构成 |
|---|---|---|---|---|
| train | 345 | **343** | 566 | 324 合成 + 19 真实（R2 出厂 324+21；**345→343 由 vol05 组 2 页 5 框移出**） |
| val | 4 | 4 | 53 | 4 真实（逐样本不变） |
| test | 2 | 2 | 5 | 2 真实（逐样本不变） |
| challenge | 0 | **2** | 5 | densho810/vol05 组整组考卷 |

组隔离：**全量 351 样本 group→split 重算 0 违例**（prepare-summary.json `group_isolation_violations=0`；DSH 另以「分集成员清单口径 351 样本 14 组」与「底册 manifest.train-v1.json split 字段口径」两种口径全量复算，违例均=0，无跨集样本、dup ids=0）。重切方法=不重算 assign_splits：train 中 densho810/vol05 整组迁移 challenge，其余逐样本保持 R2 出厂 split（逐样本断言，`moved=[pre-bj17, pre-bj18]`）。

### 1.2 challenge 考卷：densho810/vol05 组整组（用户裁决 ②(a)）

`pre-bj17`（BJ17，vol05_p0167，**竖排毛笔假名主攻形态**，2 框）+ `pre-bj18`（BJ18，vol05_p0065，竖排/斜置粗毛笔片假名，3 框）= **5 框**。

逐框溯源（与 R2 judgments 判定链逐一核对，全部 `codex+agy-consensus` confirm）：

| unit_id | 样本 | 页 | conf | verdict |
|---|---|---|---|---|
| R2-BJ17-B00 | pre-bj17 | vol05_p0167 | 0.932 | confirm（竖排毛笔假名 ヒチヤ类） |
| R2-BJ17-B01 | pre-bj17 | vol05_p0167 | 0.9096 | confirm（竖排毛笔假名 ヒチヤ类） |
| R2-BJ18-B00 | pre-bj18 | vol05_p0065 | 0.8951 | confirm（竖排/斜置粗毛笔片假名 サッ类） |
| R2-BJ18-B01 | pre-bj18 | vol05_p0065 | 0.8636 | confirm（同上） |
| R2-BJ18-B02 | pre-bj18 | vol05_p0065 | 0.8333 | confirm（同上） |

排除留痕：**R2-BJ17-B02 仲裁 delete（气泡对白非 SFX，arbiter 判定）**，已排除出考卷并在 pre-bj17 stage2r2 留痕，判定源核对一致。同组 pseudo：pre-bj25（vol05，零框负证据）不在 351 训练 manifest，未来转正按组不跨集自动入 challenge。

### 1.3 数据集健全性

- **dataset.yaml challenge 键在位**（`challenge: images/challenge`），ultralytics 8.4.172 `check_det_dataset` 扫描 **PASS**（challenge 目录 2 图可扫描；断言在训练 venv M2-SFX-FINETUNE-gpu-py312 落实）。
- **names=SFX_CLASS_MAP 双通道 PASS**：dataset.yaml names `{0:bubble, 1:panel, 2:sfx, 3:text}` 逐字等于 `src/infrastructure/providers/detection_sfx.py:137` `SFX_CLASS_MAP`（脚本读回断言 + pyyaml 6.0.3 独立解析双通道）。
- **指纹**：`badb0605ccc498fe9f268721d176df5ea190d0d6cdb5ce3b59f64cff4367b00c`（seed=20261004 冻结；T1a `splits.split_fingerprint` 工具零重写复用，算法见 `experiments/M2-SFX-DATA-INFRA/sfx_data_infra/splits.py:160`；两次运行复现一致）。R2 出厂指纹=`564498e13651bb2e…ccfa`（对照登记）。manifest.train-v1.json lock 与 prepare-summary 三方同值；prepare-summary.artifacts_sha256 全部 7 个文件逐一匹配。
- **label 351 全量与 R2 树逐字节一致**（重切只动 split 归属、不动框几何）；图像 351 张大小全量相等；sha256 三方抽验 13 张（dst==R2 源==manifest.image.sha256，**BJ 5 页必验**）。cls 分布恒 `{2: sfx: 629}`。
- train 剩余 BJ 真实正样本 **6 框**：pre-bj16×3（vol01）+ pre-bj23×2 + pre-bj24×1（vol03）；pre-bj22（候选 2 框 conf<0.2 未入判定，pseudo）与 pre-bj25（零框负证据）均不入 351 manifest——honest note 如实登记（prepare-summary.json `honest_notes`）。

---

## 2. 训练 V1（AC2）

> DSH r1 P3-2 证据口径注：本文「EXIT=0」=「脚本完成即返回 0」的推断口径——训练无字面退出码行（以 TRAIN_RESULT_JSON 结构化摘要收尾=正常走完），冒烟 `"exit": 0` 为脚本断言链走完后自写（export_smoke_v1.py:187）；两者均为「断言链走到末尾」语义。冒烟/评测无控制台原始日志（单点证据源=自产 JSON），T3 轮补 console 捕获。

证据：`verification/M2-SFX-TRAIN-V1/raw/train-log.txt`（923KB 全程 stdout，已入 Git @5fe62a91）；run 产物 `training_data/sfx-v1/train-v1/runs/train_v1/`（gitignored）。提交 5fe62a91。

- **基座**：Ultralytics 官方 `yolo11s-seg.pt`，sha256 `1caa81c0195412efa411b632bcfb8c184939dddb6ae41f6a80c41b211ff257c3`（20,669,228 B，与 T0 §8 一致）——T0 preflight 指路 `G:/CODEX/New Manga.task-envs/M2-SFX-FINETUNE-gpu-py312/weights/yolo11s-seg.pt` 在盘复用未下载，训练前 sha 自检通过（train-log.txt 首行）。
- **kwargs（全沿 T0 实测口径）**：`imgsz 1024 / batch 8 / workers 2 / epochs 150 / patience 30 / seed 20261004 / device 0`（train-log.txt 第 3 行 train kwargs JSON）。
- **运行**：单次运行 EXIT=0，无 OOM——batch=8 全程 GPU_mem 6.45G（T0 实测 7488MiB 口径内），减半重试未触发。实际 **116/150 epochs**（patience=30 早停：best epoch 86 + 30 = 116）；耗时 **868.8s ≈ 14.5 min** @RTX 5070 Ti。
- **收尾指标**：
  - results.csv 末行（epoch 116）：Box P **0.24725** / R **0.03774** / mAP50 **0.00875** / mAP50-95 **0.00535**；seg（M）同值。
  - **best.pt（epoch 86）final validation**（val 4 图 53 sfx 实例，train-log 末段 classwise 原文）：Box P **0.482** / R **0.0189** / mAP50 **0.0158** / mAP50-95 **0.0123**；Mask 同值。
- **权重 sha256（训练脚本 TRAIN_RESULT_JSON 结构化登记，盘上复核一致）**：
  - `best.pt` = `f212bfc66b524a0b768169c50d1ddd9c061a93e542f75d10c06e5660a2226740`（20,585,636 B，epoch 86）
  - `last.pt` = `c1706a951fae66bac5510b49cd85c81e9d8af604a763bdfcb82e0693f54a7c70`
- **小数据预期管理（Task 合同 AC2 原文）**：343 样本（324 合成+19 真实）训练的 mAP 数字**仅作 V1↔V2 对比基线，不作门判定**；欠拟合形态（val R=0.0189）如实登记不凑数。

---

## 3. 导出 + 生产序列冒烟（AC3，零 src）

证据：`verification/M2-SFX-TRAIN-V1/raw/export-smoke-v1.json`（含逐步 STEPS 与 `"exit": 0`）；BJ17 真实页推理演示 `raw/bj17-demo.json`。提交 c89c85e2。

- **best.onnx** = `fb60b4605ae44fa66d65dbaf56d07cd4c539d766b4dd3ec8bec1bff1a5b329f6`（40,824,255 B，imgsz 1024 导出）。
- **SHA 门先证在位**：`_build_engine` 直载新 onnx 正确命中 `PROVIDER_FAILED`（权重 sha256 ≠ 生产 pin 即拒跑）→ 随后**进程内重指**完成全链冒烟，**零 src、生产 pin `SFX_WEIGHTS_SHA256=d87389af…`（`src/infrastructure/providers/detection_sfx.py:110`）零改动**。
- **全链逐字零漂移**：names metadata 逐字 `{0:bubble, 1:panel, 2:sfx, 3:text}`（断言 PASS）；imgsz=1024（`metadata_parsed`，raw=[1024,1024]）；输出张量 `(1, 40, 21504)`（4+4cls+32mask）；合成页双档 conf 结构合法（conf 0.5 → 1 candidate / conf 0.01 → 5 candidates，`class_filter=sfx`、`coordinate_space=page-global`）。
- **BJ17 真实页推理演示**（`raw/bj17-demo.json`，2946×4167，sha256 `7bee7f05…`）：生产序列 conf≥0.5 = **0 检出**；conf≥0.2 = 1 检出（[2413.8, 2914.2, 2502.7, 3096.8]，conf 0.2049）——主攻形态上的原始输出如实留档（该唯一检出与 2 GT IoU 均 <0.5，见 §4）。
- 冒烟 **EXIT=0**（export-smoke-v1.json `"exit": 0`；`experiments/M2-SFX-TRAIN-V1/export_smoke_v1.py:191` 收尾设计）。

---

## 4. directional 评测（AC4）

> **DSH r1 C1（P2-1）对照口径定性注（必读）**：chiqui7 对照=**GT 来源模型的自洽上界，非同链路独立复跑**——challenge 5 个 GT 框源自 chiqui7 预标注候选（R2 判定链 confirm），故其 IoU 结构性=1.0、recall=5/5 是「GT ⊂ 该模型候选池」的数学必然；且双口径对 chiqui7 逐值同值（池内低置信候选 conf<0.2 被两档阈值同排除），实为一次测量。**新模型 0/5、0/56 是绝对量、方向性结论不反转；但差值幅度不可作定量比较**。T3/V2 正式评测须改为同链路独立复跑 chiqui7（复用 eval_challenge.py，成本≈一次推理）以消除循环性。

证据：`raw/eval-challenge.json`（BJ challenge）+ `raw/eval-kodelta.json`（KO 不回退）。口径：生产 `SfxDetectionProvider.detect` 全序列（letterbox 1024 / 类无关 NMS 0.7 / sfx 过滤）；GT=manifest polygon 原页坐标（2946×4167）；匹配=box IoU≥0.5、pred conf 降序贪心。**统计功效低，仅 directional，结论禁用「显著」；0 也如实。**

### 4.1 BJ challenge 主考卷（5 框）

| 口径 | 新模型（best.onnx） | chiqui7 对照（R2 预标注） |
|---|---|---|
| 严格 conf≥0.50 | **0/5**（0 检出；**BJ17 竖排主攻形态零检出**） | **5/5**（6 检出，P=0.833） |
| 宽松 conf≥0.20 | **1/5**（3 检出，P=0.333；唯一匹配=R2-BJ18-B00，IoU 0.606 @conf 0.343） | **5/5**（6 检出，P=0.833） |

chiqui7 唯一 FP = R2-BJ17-B02 气泡框（正是 §1.2 仲裁 delete 被排除出考卷的框）——对照组口径与 R2 判定链自洽。**考卷结论：BJ 考卷新模型 0–1/5 vs chiqui7 5/5。**

### 4.2 KO 不回退检查（val 4 样本 53 框 + test 2 样本 5 框）

| 范围 | 新模型 | chiqui7 |
|---|---|---|
| KO 页 4 样本 56 框（pre-k01/k02/k08/k09） | 严格/宽松均 **0/56**（零检出） | 严格 **56/56**（68 检出，P=0.824）/ 宽松 **56/56**（84 检出，P=0.667） |
| 全 6 样本 58 框（含 imp-ogkalu-* 2 样本） | 宽松 **0/58**（5 检出全不匹配） | imp-ogkalu-* 2 样本（2 框）**预标注不可得，如实登记**（预标注源=ogkalu rt-detr 非 chiqui7，R1 worksheet domain=ko-ogkalu-crop） |

- **KO directional 回退如实登记：新模型全面回退。** 与 343 样本小数据 + COCO 基座无 manga 先验 + 欠拟合（val R=0.019）一致。
- 措辞纪律：56 框量级统计功效低，禁用「显著」；差值仅作 V1↔V2 基线登记。

### 4.3 结论

V1 = 管线验证（训练/导出/生产链路全通 EXIT=0）；质量数字作 V1↔V2 基线不作门判定；不满足任何生产切换条件（T4 条件清单见 §7.2）。

---

## 5. 独立复核（DSH，非作者）= PASS

四项复核全部实测通过，未发现数据/训练/评测/边界方面的实质问题。逐项证据（复算命令与输出原文见 DSH 复核记录）：

1. **重切正确性 PASS**：4 个 manifest + yolo 树全量重算——challenge 恰 2 图 5 框（labels cls 全=2）；train 无 vol05 组（组集合 9 组不含 densho810/vol05）；组隔离两种口径全量重算 0 违例、无跨集样本；与 prepare-summary.json 逐数字对照全一致；深度校验 351 label 与 R2 只读树（M2-SFX-ANNOTATE-R2-zcode/training_data/sfx-v1/annotate-r2/final/yolo）sha256 逐字节全等、底册 manifest 框数 vs yolo label 0 mismatch、cls {2:629} 恒一；names 双通道实测（dataset.yaml 逐字等于 `src/infrastructure/providers/detection_sfx.py:137`）；指纹按 `splits.py:160` 算法重算复现=badb0605…，artifacts_sha256 全 7 文件逐一匹配。
2. **训练真实性 PASS**：train-log.txt 651 行，epoch 进度行覆盖 1..116 连续无缺口；第 639 行 `116 epochs completed in 0.233 hours.`；尾行 TRAIN_RESULT_JSON（actual_epochs=116、early_stopped=true、best_epoch=86、train_sec=868.8）——早停自洽（116−86=30=patience）；results.csv 117 行=表头+116 epochs，末行与汇报逐值一致；sha256 盘上重算（hashlib 分块）vs 登记四方一致（best.pt/last.pt/best.onnx/基座）。
3. **评测复算 PASS**：GT 取 manifest.challenge.json polygon（原页 2946×4167），独立实现 IoU≥0.5 贪心重算——BJ17 页（new@0.5 无 pred→0/2；@0.2 唯一 pred 与 2 GT IoU 均<0.5→matched 0；chiqui7 B00/B01 IoU=1.0→2/2、P=2/3）、BJ18 页（new@0.2 2 pred 中 1 个 IoU=0.6058→1/3；chiqui7 3/3）逐框一致；汇总四组一致。KO val 抽 pre-k08（27 GT）从 R1 worksheet（68 单元）独立重算 @0.5 = 30 pred/27 matched/P=0.9、@0.2 = 38 pred/P=0.7105、top5 conf 逐一相同——与 eval-kodelta.json 一致；汇总算术自洽（56/68=0.8235、56/84=0.6667）。
4. **零 src 实证 PASS**：`git diff --name-status a85d8853..HEAD`（merge-base 实测=a85d8853）共 13 文件（集成实测；Owner 计 11 为 c89c85e2 时点——DSH r1 P3-1），全在 Task 允许范围（doc/tasks/M2-SFX-TRAIN-V1.md + experiments/M2-SFX-TRAIN-V1/ 四脚本 + verification/M2-SFX-TRAIN-V1/ 摘要+raw×5）；`git diff a85d8853..HEAD -- src/` 空、src 相关提交 0；生产 pin d87389af… 在 HEAD/base/main 三处 `git show` 同值；dataset.yaml/best.pt/best.onnx 均 `git check-ignore` 命中 `.gitignore:13 '/training_data/'`（另有 `*.pt`/`*.onnx` 第 8–10 行双保险）。

**非阻塞观察项（3 条，如实登记）**：

1. **盘面残留**：`verification/M2-SFX-TRAIN-V1/prepare-summary.json.bak`（10,463 B，untracked 未入库）为 atomic_write_json 前版备份，内容=重切前旧摘要（旧 manifest sha256 `198937fb…` vs 正式 `e454429a…`，仅 generated_at_utc+artifacts_sha256 不同）。无实质影响，属可清理残留（对照 R2 轮 P3-5 删 .bak 的整改精神），留集成轮处置。
2. **EXIT 证据口径说明**：train-log.txt 本身不含字面 `EXIT` 行——训练脚本以 TRAIN_RESULT_JSON 结构化摘要收尾（`experiments/M2-SFX-TRAIN-V1/train_v1.py:134`，在盘验证为 log 末行）；EXIT=0 的字面与结构化证据在 export-smoke-v1.json（`"exit": 0`，`export_smoke_v1.py:191`）。此为脚本设计差异，非日志缺失（epochs/results.csv 末行两项均验证完整）。
3. **AC5 报告时点**：复核时 `train-v1-report.md` 不在盘（Task AC5 交付物中最后一项）——**本报告即该缺项的补齐**，文档收尾轮交付。

---

## 6. 诚实边界

> **DSH r1 P3-3 归因强度注**：「样本量不足为首要瓶颈」系 5 框/56 框单点 directional 观测推得的**方向性假设**；未排除的并列解释：①合成:真实=324:19 的域差（val 全真实页，synth→real 迁移失败可独立解释 val R≈2%）；②nc=4 单类监督（labels cls 恒 2，三类零监督的负类行为未评估）。V2 可选杠杆（交 T3 裁决）：近域基座初始化（T0 已登记 anonimkaq4 manga yolo11s-seg .pt 作 A/B 选项）/配比调整/单类 nc=1 训练/更长 epochs+增广。

- **BJ train 剩 6 框真实正样本**（BJ16×3+BJ23×2+BJ24×1），量级仍小——BJ 深度靠 T3 扩标轮补，V1 不解决主攻形态学习问题。
- **KO val/test 功效低**（4 样本 53 框 + 2 样本 5 框），directional 措辞纪律，禁用「显著」；imp-ogkalu-* 2 样本 chiqui7 对照不可得如实登记。
- **V1 不承诺 G1-G8 Gate**（Task 合同原文；正式 Gate 属 T3）。
- **低数字如实登记不凑数**：mAP/召回数字仅作 V1↔V2 对比基线不作门判定。
- **AGPL 备案在案**：基座 yolo11s-seg.pt=AGPL-3.0（用户许可降权备案覆盖）；衍生 best.pt/best.onnx 均 gitignored 外部树，未入库未分发。
- 训练曲线/run 产物 gitignored（runs/ 曲线/args.yaml/weights）；Git 只进摘要与全程日志。

---

## 7. T3/T4 呈报材料（交编排/用户）

### 7.1 T3 前置：BJ 深度扩标候选（T2 视角的输入材料）

- **候选池（沿 Task AC5 原文口径）**：BJ conf<0.2 层 16 单元 + 44 张 BJ 候选池页 + 10 张 KO 扩标候选（R2 轮未入池候选，留 `training_data/sfx-v1/annotate-r2/` 扩标池）。
- **V1 失败形态佐证（扩标优先级输入）**：竖排毛笔假名主攻形态（BJ17）零检出——train 该形态真实正样本仅个位数框；粗毛笔片假名（BJ18-B00）有低置信响应（IoU 0.606 @conf 0.343，未达匹配生产冻结口径）——形态并非完全不可学，样本量是首要瓶颈。
- 建议路径：T3 扩标轮后正式训 V2 并跑 G1-G8 正式 Gate（challenge 考卷复用本轮 densho810/vol05 组，指纹与判定链可溯源）。

### 7.2 T4 生产切换条件清单（建议，最终以 T4 Task 释放为准）

1. **质量门**：BJ challenge 考卷（5 框）严格 conf≥0.50 召回达标（生产冻结 `SFX_CONF_THRESHOLD=0.5` 精度优先口径，`detection_sfx.py:118`；阈值由用户裁决）+ KO 不回退（directional 无回退，扩样后复核）。
2. **正式 Gate**：G1-G8 由 T3 正式评测轮出具；V1/V2 数字均不作门判定。
3. **链路门**：best.onnx→SHA 门→`_build_engine` 进程内重指生产序列冒烟 EXIT=0（本轮 export_smoke_v1.py 模式可复用）+ names metadata 逐字=`SFX_CLASS_MAP` + imgsz `metadata_parsed`。
4. **替换语义**：生产 pin `SFX_WEIGHTS_SHA256`（`src/infrastructure/providers/detection_sfx.py:110`，现值 d87389af…）更新为通过门判定的新 onnx sha256；HF repo/revision 字段（`SFX_HF_REPO`/`SFX_HF_REVISION`，现指 chiqui7 源）语义须随新权重来源一并处置。**src 改动=Codex 授权的新 Task；T2 零 src 红线不破。**
5. **许可**：AGPL-3.0 基座衍生权重上生产面的备案复核（用户已备案覆盖原则沿袭）。
6. **用户裁决**：生产切换本身=T4 用户裁决点。

---

## 8. 证据索引

| 产物 | 路径 | 状态 |
|---|---|---|
| 数据摘要 | verification/M2-SFX-TRAIN-V1/prepare-summary.json | Git |
| 训练全程日志（923KB） | verification/M2-SFX-TRAIN-V1/raw/train-log.txt | Git @5fe62a91 |
| 导出冒烟+SHA 门+BJ17 演示登记 | verification/M2-SFX-TRAIN-V1/raw/export-smoke-v1.json | Git |
| BJ17 真实页推理演示 | verification/M2-SFX-TRAIN-V1/raw/bj17-demo.json | Git |
| BJ challenge 评测 | verification/M2-SFX-TRAIN-V1/raw/eval-challenge.json | Git |
| KO 不回退评测 | verification/M2-SFX-TRAIN-V1/raw/eval-kodelta.json | Git |
| 数据集/权重/ONNX/run 产物 | training_data/sfx-v1/train-v1/（dataset/ weights/ runs/train_v1/） | gitignored 外部树 |
| 实验脚本 | experiments/M2-SFX-TRAIN-V1/{prepare_dataset,train_v1,export_smoke_v1,eval_challenge}.py | Git |

复现命令：`python experiments/M2-SFX-TRAIN-V1/prepare_dataset.py --step all`（AC1 重切+摘要）；训练/冒烟/评测各脚本入口同目录（环境 venv=M2-SFX-FINETUNE-gpu-py312，ultralytics 8.4.172，RTX 5070 Ti）。
