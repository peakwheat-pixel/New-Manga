# M2-SFX-TRAIN-V1 DSH r1 审查报告（2026-10-04）

> 审查对象：tip d5ea34af（链 7945c5de→45ae05a4→5fe62a91→c89c85e2→d5ea34af）；Verdict=approved_with_conditions（0×P0/P1、1×P2、4×P3、4×P4）。
> DSH headless stdout 全文转录（124 行完整，无截断）；运行级验证由集成方实测闭合（见 Handoff「集成运行级验证」）。

## Verdict

**approved_with_conditions**

理由：交付链的数字、结构与证据在**静态可核范围内全部自洽**——challenge 5 框逐框可溯源、351 images/labels 计数闭环、训练产物与日志逐值对得上、评测 JSON 可独立复算、可见范围内无伪造、无凑数、无越界改动迹象；`.bak` 残留已清除（观察项 1 闭合）。未发现 P0/P1。

但有两处必须随集成轮闭合，故不给无条件 approved：
1. **AC4 的 chiqui7 对照口径不等价且报告未披露**（Q1，P2）：GT 直接派生自 chiqui7 预标注候选框，`recall=1.0` 是结构性结果而非测量值；「vs chiqui7 5/5」的表述强度超出证据。
2. **AC6 的文件数陈述在 docs HEAD 下已失效**（`11` 应为 `13`），且「EXIT=0」缺少字面退出码证据。

**审查范围与限制（重要）**：本会话沙箱命令通道不可用（`SetNamedSecurityInfoW failed (Win32 5)`，提权无审批通道），`git`/`hashlib`/进程复算一律无法执行。因此下列**运行级声明本次未验证**，须由具备 git 的集成轮独立确认，不得因本 Review 视为已证：`git diff --name-status a85d8853..HEAD` 文件清单与 `-- src/` 空 diff、生产 pin 在 HEAD/base/main 三处同值、sha256 复算（best.pt/last.pt/best.onnx/基座/artifacts）、指纹 `badb0605` 重算、351 labels 全量逐字节。以下结论凡依赖这些者已逐条标注。

---

## 重点问题 Q1/Q2/Q3 裁定

### Q1【评测对照公正性】→ **不等价；chiqui7 数字是结构性上界而非独立测量（但「回退」方向仍成立）**

三条独立理由：

1. **GT 派生性（决定性）**。challenge 的 5 个 GT 框 = R2 判定链 `confirm` 单元，其 `polygon` 的外接矩形与 chiqui7 预标注候选框**逐值相同**：`manifest.challenge.json:18-35` 的 `[1660.4,2394.9,1773.2,2624.7]` 与 `eval-challenge.json:85-90` 的 chiqui7 `xyxy` 完全一致，故所有匹配 `pairs.iou` 恒 `1.0`（`eval-challenge.json:123,128,298,306,311`）。KO 同理：R1 池按 `sources=["chiqui7-scan"]` 过滤（`eval_challenge.py:152`），匹配 `iou` 亦恒 `1.0`（`eval-kodelta.json:219-221` 等）。**结论**：`5/5`、`56/56` 在数学上是「GT ⊂ 该模型候选池」的必然结果，任何为 GT 提供种子的模型都会得满分。这不是伪造（chiqui7 确实在该页产出 conf 0.83–0.93 的真实候选，且这些框就是它的推理输出），但它是**自洽上界**，不是「同链路重推理」的对照测量。
2. **口径不对等**。新模型 = 原始生产管线输出按阈值筛（`SfxDetectionProvider.detect` 全序列）；chiqui7 = **已判定单元池**（`worksheet` 的 `units`）按 `ai_conf` 筛。后者是经 codex+agy 审定/仲裁后的精选集合，既非模型原始输出全集，其 precision（0.833）也不可与新模型的原始管线 precision（0.333）直接相减。
3. **双口径对 chiqui7 是空转**。池内确实存在 `<0.2` 的候选（`R2-BJ17-B03 0.108`、`B04 0.0832`、`R2-BJ18-B03 0.1082`，见 `manifest.challenge.json:117-128,274-280`），两档阈值都将其排除，故 chiqui7 的 `0.5` 与 `0.2` 两行**逐值相同**（`n_pred=6/6`、`precision=0.8333/0.8333`，`eval-challenge.json:35-48`）。用户前提「conf 0.833–0.932 均高于双口径阈值」只对 GT/已判单元成立——但既然多出的候选全在阈值之下，报告的六个数其实就是**一次测量报了两次**；同理 KO 的 `56/56·P=0.824` 与 `56/56·P=0.667` 才是有差异的两档。

**是否高估、是否影响「回退」结论**：recall 已是上界故不可能被低估，差值的**幅度**被夸大（不可作定量比较）；但方向性结论**不反转**——新模型 `0/5`、`0/56` 是绝对量，不依赖基线定义；且 chiqui7 的真实候选确实存在。故 AC4 的「如实」轴部分受损于**表述**而非数字。建议改述为「对照=GT 来源模型的自洽上界（IoU 结构性 1.0，非独立复跑）」，并在 T3/V2 基线中补一次**同链路独立推理**（成本 ≈ 一次 torch/onnx 前向，`eval_challenge.py` 现成可复用）以消除循环性。

### Q2【欠拟合归因与 V2 启示】→ **欠拟合被证据支撑；「数据量不足为首要瓶颈」属未被排除的假设；V2 启示偏薄**

**支撑成立的部分**：train loss 全程单调下降（box 2.109→0.607、seg 4.929→1.093，`results.csv:2,117`），而 val 指标全程贴地（`R ≤ 0.03774`、`mAP50 ≤ 0.0175`）；best fitness 停在 epoch 86 后 30 epoch 无改善并早停（`train-log.txt:636,639`）；best.pt 复评 `R=0.0189`（`train-log.txt:647`）——即模型在训练分布上都只能召回约 2% 实例；独立生产管线在 challenge/KO 上 `0/5`、`0/56`（`eval-challenge.json:20-34`、`eval-kodelta.json:39-53`）与训练期 val **同向**，排除了「只是自建评测管线口径 bug」的解释。这一层归因是硬证据。

**未排除的替代解释（报告未讨论）**：
- **合成:真实 = 324:19 的域差**：训练 343 中 324 为合成（`prepare-summary.json:26-44`），而 val/test/challenge **全部是真实页**。val `R≈2%` 完全可以由 synth→real 迁移失败解释，而未必是「绝对量不足」。报告只在 §1.1 登记了配比，未把它作为候选原因处置。
- **单类监督**：`dataset.yaml` names 四类，但 labels `cls` 恒 `2`（629 框全 sfx；`_export_stats`/脚本断言），即 nc=4 中三类零监督。`cls` 分支的负类行为对 mAP 的影响未讨论。
- **近域基座未纳入**：T0 自己登记了 `anonimkaq4` manga yolo11s-seg `.pt` 作 A/B 初始化选项（`preflight-report.md:69,129`），报告 §7.1 的 V2 路径只提「扩标后重训」，未把它列为杠杆。
- 学习率口径：`lr0=0.01/lrf=0.01/optimizer=auto` 已在 `args.yaml:73-74,20` 与日志回显（`train-log.txt:5`）登记，但报告 §2 未列，故「学习率口径」这一项**只有登记、没有分析**。

**V2 启示与越界**：报告给出了「样本量是首要瓶颈 → T3 扩标 → 训 V2 → 跑 G1-G8」（`train-v1-report.md:156-157`），未越界（未替 T3/T4 定方案、未动阈值）。但「样本量首要瓶颈」是**由 5 框/56 框单点 directional 观测推得**，建议降级为待验证假设，并补一句训练策略层的可选杠杆（初始化/单类/配比/epochs）。

### Q3【管线验证声明完整性】→ **证据链实质完整，但三处口径需收紧；无致命缺口**

- **train-log 完整性：成立**。651 行、epoch 1..116、`EarlyStopping … best results observed at epoch 86`（`:636`）、`116 epochs completed in 0.233 hours.`（`:639`）、best.pt 复评段（`:643-648`）、末行 `TRAIN_RESULT_JSON`（`:651`，含 `actual_epochs=116/early_stopped=true/best_epoch=86/train_sec=868.8` 与权重 sha）；`results.csv` 117 行 = 表头+116，末行与汇报逐值一致。best epoch=86 我按 `train_script` 的 fitness（0.9·mAP50-95+0.1·mAP50）独立复算确认（86 行 0.012608 为全表最大）。
- **ONNX metadata 逐字断言：成立，但归属应更正**。断言确实存在，且**在生产代码内**（`src/infrastructure/providers/detection_sfx.py:436`：`parsed != SFX_CLASS_MAP` → `ProviderInvalidOutput`）。冒烟脚本自身只断言 `imgsz_source == "metadata_parsed"` 与 `imgsz == 1024`（`export_smoke_v1.py:112-113`），names 只记录不断言。报告 §3 的「names metadata 逐字（断言 PASS）」应注明断言来自 `_build_engine` 而非冒烟脚本。
- **SHA 门先证后指：逻辑闭合**。`sha_gate.fired(PROVIDER_FAILED)` → `sha_gate.ok` → `build_engine.full_chain_ok`（`export-smoke-v1.json:25-50`）；`_build_engine` 在调用时读取模块级 `SFX_WEIGHTS_SHA256`（`:417`），故 `dsfx.SFX_WEIGHTS_SHA256 = onnx_sha`（`export_smoke_v1.py:101`）的进程内重指确实生效，src 零改动在代码层可解释。
- **点出的证据缺口**：(a) 训练**无字面退出码**——我 grep 全文 `EXIT|Traceback|error|Error` **零命中**，`EXIT=0` 只能由「脚本跑到末尾打印结构化摘要」推断；(b) 冒烟的 `"exit": 0` 是脚本**硬编码写入**的字段（`export_smoke_v1.py:187`），不是调用方捕获的进程退出码；(c) 冒烟/评测**只有脚本自产 JSON，无控制台原始日志**（对照 T0 存了 `raw/export_smoke_console.log`），单点证据源。
- 未做（合同未要求，不作为缺口）：ONNX ↔ best.pt 输出一致性对拍。

---

## 发现清单

**P0**：无。

**P1**：无。

**P2-1｜chiqui7 对照口径非独立、报告未披露（Q1）**
- 位置：`verification/M2-SFX-TRAIN-V1/train-v1-report.md:100-105`、`raw/eval-challenge.json:35-48`、`raw/eval-kodelta.json:54-67`、`experiments/M2-SFX-TRAIN-V1/eval_challenge.py:156-157,179-185,249-256`、`doc/handoffs/...-20261004.md:93`
- 问题：chiqui7 的 recall=5/5、56/56 是「GT ⊂ 该模型候选池、IoU 结构性 =1.0」的必然结果；且两档阈值对 chiqui7 输出逐值相同（双口径空转）。报告以「vs chiqui7 5/5」「双口径 5/5」并列呈现，读者会误读为独立同口径测量。
- 建议：在 §4.1/§4.2 与 Handoff 附注加一句定性——「chiqui7 对照 = GT 来源模型的自洽上界，非同链路独立复跑；其 recall 结构性为 1.0，差值不构成定量结论，仅作方向性参照」；并把 chiqui7 的「双口径」改为「单口径（两档同值，因池内低置信候选 <0.2）」；T3/V2 基线补一次同链路独立推理。

**P3-1｜AC6 文件数在 docs HEAD 下已失效**
- 位置：`doc/tasks/M2-SFX-TRAIN-V1.md:62`、`train-v1-report.md:130`
- 问题：`git diff --name-status a85d8853..HEAD 仅 11 文件` 是 **c89c85e2 时点**的复核值；docs 提交新增 `train-v1-report.md` + Handoff 后应为 **13**（均在允许范围内，非越界，仅数字陈旧）。
- 建议：docs 轮改为 `13`，或注明「11 = c89c85e2 时点；docs 提交后 13」。

**P3-2｜「EXIT=0」证据口径（Q3）**
- 位置：`raw/train-log.txt`（全文无 EXIT/Traceback）、`raw/export-smoke-v1.json:94`、`experiments/M2-SFX-TRAIN-V1/export_smoke_v1.py:187`、报告 `:17,90`
- 问题：训练无字面退出码；冒烟的 `"exit": 0` 由脚本自写，非调用方捕获。
- 建议：报告中把两处明确标注为「脚本完成即返回 0（结构化摘要/断言链走到末尾）」的推断口径，或在集成轮附 console 捕获日志。

**P3-3｜Q2 归因不完整**
- 位置：`train-v1-report.md:18,78,114,156-157`
- 问题：未讨论合成:真实=324:19 的域差、nc=4 单类监督、「样本量首要瓶颈」的证据强度；T0 已登记的近域基座未纳入 V2 杠杆。
- 建议：§6/§7.1 补一句「上述归因为方向性假设，合成-真实域差与单类监督为未排除的并列解释」，并列出初始化/配比等可选 V2 杠杆。

**P3-4｜「results.csv 末行」与「best.pt final val」同源未说明**
- 位置：`train-v1-report.md:73-74`、`raw/train-log.txt:647`、`results.csv:87`
- 问题：`final val`（P 0.48288/R 0.01887/mAP50 0.01583）与 epoch 86 行逐值相同（同为 best.pt 在同 val 集上的确定性复评），报告并列呈现易被当作两次独立测量；且 0.48288 截断为 0.482（四舍五入应为 0.483）。
- 建议：注明二者同源，或统一取整口径。

**P4-1｜自引「DSH 独立复核 = PASS」无独立产物**
- 位置：`train-v1-report.md:10,123-136`、`doc/tasks/M2-SFX-TRAIN-V1.md:83`、Handoff `:33`
- 问题：`doc/reviews/` 下无 M2-SFX-TRAIN-V1 记录；该复核系在作者 workflow 内执行，不能计入独立验证。真正的非作者独立审查是本 Review。
- 建议：集成轮把本 Review 落 `doc/reviews/`，报告 §5 改引独立产物路径。

**P4-2｜docs commit hash 缺位、recovery point 不完整**
- 位置：Handoff `:22,55,65`、报告 `:9`、Task `:6`
- 问题：三文档均无 docs 提交 hash，Handoff 称「docs head 随本提交更新于 Task 回填」但回填中并无该 hash（沿 R2 同款措辞惯例，属低优先）。
- 建议：集成轮补记 docs head。

**P4-3｜`.gitignore` 行号表述**
- 位置：`doc/tasks/M2-SFX-TRAIN-V1.md:62`
- 问题：「`*.pt`/`*.onnx` 8-10 行」实为 **9-10 行**（`.gitignore:8` 是 `*.safetensors`；`/training_data/` 确在第 13 行 ✓）。
- 建议：改为 9-10 行。

**P4-4｜eval 脚本 KO 池按 `case_id` 索引（潜在混池风险）**
- 位置：`eval_challenge.py:235,249`
- 问题：`chiqui7_ko` 以 `case_id` 为键，`pre-k08` 与 `imp-ogkalu-k08-r025` 共享 `K08`；当前因 `is_ko_page` 过滤 imp 样本而无影响，扩大样本时有混池风险。
- 建议：改按 `sample_id` 索引，或加断言。

**已闭合/正向确认**：`.bak` 残留已清除（`verification/M2-SFX-TRAIN-V1/**` 现仅 7 文件，无 `.bak`）——独立复核观察项 1 闭合；`honest_notes` 对 BJ22（非零框）与 BJ25（真零框）措辞差异如实登记（`prepare-summary.json:309-315`）；T3/T4 呈报数字 **16+44+10 与 R2 登记一致**（R2 `stage-r2-report.md:182` 「44 张 BJ 候选（54−10：vol01 16+vol03 15+vol05 13）+ 10 张 KO 候选」、`:230,356` 「16 个 conf<0.2 候选留 worksheet-bj-new.json」）；生产 pin 值 `d87389af4350…b646` 与 T0（更早 base）引文逐字相同（`preflight-report.md:107`），构成 pin 未被本 Task 改动的**间接**证据。

---

## 逐 AC 结论

- **AC1 — PASS**。`manifest.challenge.json` 恰 2 样本 5 框，逐框 `unit_id/conf/verdict` 与 `prepare-summary.json:90-148` 及 `worksheet` 判定链一致（0.932/0.9096/0.8951/0.8636/0.8333，全 `codex+agy-consensus` confirm；`R2-BJ17-B02` delete 排除留痕在案，池内 `<0.2` 候选 B03/B04/B03 亦如实登记）；`images/{train,val,test,challenge}` = 343/4/2/2 = 351（glob 实测），labels 351；`pre-bj17/pre-bj18` label 与 R2 树逐字节相同（抽验）；指纹 `badb0605…` 在 manifest lock/`prepare-summary`/`_export_stats` 三处同值；组隔离 0 违例有脚本断言。**未验证**：sha256 复算、`git` 侧底册核对。
- **AC2 — PASS（附 P3-2 口径）**。`args.yaml` 与 `train-log.txt:3` 回显 imgsz 1024/batch 8/workers 2/epochs 150/patience 30/seed 20261004/device 0，全沿 T0（`preflight-report.md:15,49,92,97` b8=7488MiB）口径；`results.csv` 末行 P 0.24725/R 0.03774/mAP50 0.00875/mAP50-95 0.00535 与汇报一致；best epoch 86 经 fitness 复算确认；早停 116−86=30=patience 自洽；best.pt sha/大小登记在案且可从 `TRAIN_RESULT_JSON` 复读。低数字如实、明示不作门判定。
- **AC3 — PASS（附 P3-2/Q3 口径）**。`best.onnx` sha `fb60b460…`/40,824,255 B 与 JSON 一致；SHA 门 `PROVIDER_FAILED` 正确命中后进程内重指；names 逐字断言来自生产 `_build_engine:436`（真实生效）；`imgsz=1024 metadata_parsed`、`raw=[1024,1024]`、张量 `(1,40,21504)`；`bj17-demo.json` 双档（0.5→0/0.2→1 @0.2049）与报告一致；生产 pin 未见改动迹象（与 T0 同值）。零 src 仅声明级。
- **AC4 — PARTIAL**。数字本身如实且可复算：BJ `0/5`（严格）/`1/5`（宽松，唯一匹配 BJ18-B00 IoU 0.6058——我按 GT/预测坐标独立算出 0.6061，一致）、KO `0/56`、全 6 样本 `0/58`（5 检出全不匹配）；imp-ogkalu 对照不可得如实登记。**扣分项 = Q1**：chiqui7 对照为非独立的结构性上界且未披露，「双口径 5/5」对 chiqui7 实为一次测量，与「同页同口径」的可比性声称不符。
- **AC5 — PASS**。报告/Handoff/Task 三文档齐，结构完整，诚实边界齐全（BJ train 剩 6 框、KO 功效低、V1 不承诺 G1-G8、AGPL 备案在案）；§7 T3 候选 16+44+10 与 R2 登记一致，§7.2 T4 条件清单含 pin/`SFX_HF_REPO/REVISION` 替换语义。**扣分项仅 P4-1/P4-2**（自引复核无独立产物、docs hash 缺位）。
- **AC6 — PARTIAL**。静态可证：`/training_data/` 命中 `.gitignore:13`，`*.pt`/`*.onnx` 命中 `:9-10`；数据/权重/ONNX 全在 gitignored 外树且已在盘（未入库）；生产 pin 与更早 T0 引文同值。**不可证**：`git diff` 文件清单与 `-- src/` 空 diff（沙箱无命令）。**已知缺陷**：AC6 文本「仅 11 文件」在 docs HEAD 下应为 13（P3-1）。

---

## 推荐下一步

1. **集成轮（编排会话代行 Codex，具备 git）先补运行级验证**，这是本次静态审查的唯一空白：`git diff --name-status a85d8853..<docs HEAD>`（预期 13 文件、全在 Task 允许范围）、`git diff --name-status a85d8853..<docs HEAD> -- src/`（预期空）、`git show HEAD|a85d8853|main:src/infrastructure/providers/detection_sfx.py` 三处 pin 同值、`git check-ignore` 三条命中、`hashlib` 重算 best.pt/best.onnx/基座 sha 与指纹 `badb0605`。
2. **闭合 C1（P2-1，必做）**：在 `train-v1-report.md` §4.1/§4.2 与 Handoff 附录加「chiqui7 对照 = GT 来源模型的自洽上界，非独立同口径测量」定性注，并说明双口径对 chiqui7 同值的原因；无需返工数据。
3. **闭合 C2/C3（P3-1/P3-2，随文档提交）**：文件数 11→13、EXIT=0 口径标注（或在集成轮附 console 日志）。
4. **建议（非阻断，交 T3 裁决输入）**：T3 的 V2 基线与正式 Gate 中，把 challenge 对照改为**同链路独立复跑 chiqui7**（复用 `eval_challenge.py`，成本≈一次推理），并在 V2 归因里补合成:真实配比、单类监督两个并列解释。
5. **将本 Review 落 `doc/reviews/M2-SFX-TRAIN-V1-<head>-dsh-r1.md`**，替换报告 §5 对 workflow 内自引复核的依赖（P4-1）。

**可直接转发给集成 Agent 的指令**：
> 对分支 `agent/zcode/M2-SFX-TRAIN-V1`（base `a85d8853`、delivery `c89c85e2` + docs 提交）执行集成验证：①`git diff --name-status a85d8853..HEAD` 应含 13 个文件（`doc/tasks/M2-SFX-TRAIN-V1.md`、`experiments/M2-SFX-TRAIN-V1/` 四脚本、`verification/M2-SFX-TRAIN-V1/{prepare-summary.json,train-v1-report.md}` 与 `raw/` 五件、`doc/handoffs/M2-SFX-TRAIN-V1-zcode-20261004.md`），全部在 Task 允许范围；②`-- src/` 空 diff；③pin `d87389af4350…b646` 在 HEAD/base/main 三处同值；④`git check-ignore` 命中 `dataset.yaml`/`best.pt`/`best.onnx`；⑤`hashlib` 重算 best.pt `f212bfc6…`/best.onnx `fb60b460…`/基座 `1caa81c0…` 与指纹 `badb0605…`；⑥把 DSH r1 Review（结论 `approved_with_conditions`）落 `doc/reviews/`，并按下文条件更新报告后 merge：报告 §4.1/§4.2 增「chiqui7 对照为 GT 来源模型的自洽上界、非独立复跑、recall 结构性 1.0、双口径对 chiqui7 同值」定性注（必做）；AC6 行「11 文件」改为「13 文件」；训练/冒烟 EXIT=0 标注为「脚本完成即返回 0」口径或附 console 捕获（二者均在 Task 允许文档路径内，无需改代码）。T3/T4 不随本集成释放。
