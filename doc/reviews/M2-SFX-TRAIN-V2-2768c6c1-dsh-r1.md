# M2-SFX-TRAIN-V2 DSH r1 审查报告（2026-10-05）

> 审查对象：tip 2768c6c1（链 4e881720→75148bc4→093631d2→ba94fa76→2768c6c1）；Verdict=approved_with_conditions（0×P0/P1、3×P2、4×P3、5×P4）。
> DSH headless stdout 全文转录（137 行完整，无截断）。运行级验证由集成方执行（src 空 diff/pin 同值/check-ignore）。

# M2-SFX-TRAIN-V2 独立 Review（DSH，非作者，只读）

**审查方式声明**：本会话 shell 沙箱不可用（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(<workspace>)`，重试 2 次均失败），因此**无命令级复核**：`git diff` 范围、sha256 盘上重算、ONNX 推理重放、`SampleRecord.validate()`、ultralytics 扫描、349/349 零漂移重算、558 vs 351 页 sha 全量交集均**未在本轮独立验证**，相应声明按「文档转述/运行级未验证」对待。所有能被文本证据证实的部分（原始 JSON、CSV、日志、脚本、外部树只读引用、Git reflog）均已逐项静态核对，核对结果如下。

---

## Verdict

**approved_with_conditions**

交付主体（数据接入与重切、A/B 训练、导出冒烟、同链路三方评测、零 src 纪律、文档与证据链）**实质成立**：所有可静态复算的数字与原始产物逐项自洽（见下），无 P0/P1 级事实错误，未发现造假或凑数迹象；ISSUE-A 被作者主动发现并如实登记，**未影响评测结论**。

但验收条件中「文档口径一致」一项未完全闭合：报告在 §2.3 正确指认的「B 版 best 口径错位」，在 §0/§2.4/§7.1.5 被**再次犯下**——用 B 版**未被保存**的 epoch49 指标与 A 版**已保存**的 epoch79 指标相比，得出「两版 best fitness 持平级」。该句不成立（同口径下 A 明显更高），且已传播进 AC5 的 T3 材料刷新。因修复面为**纯文档**（无需重跑训练/评测），且附带 3 项措辞纪律问题，故判 **approved_with_conditions**，条件见「发现清单」P2 三条。

---

## 重点问题 Q1/Q2/Q3 裁定

### Q1【ISSUE-A best 口径错位】—— 错位属实；**不影响「B 版 5/5」结论**，但**推翻「两版 best fitness 持平级」**

**证据链（全部静态可验）**：
- 训练脚本 `experiments/M2-SFX-TRAIN-V2/train_v2.py:143-150`：wrapper 自算 `fitness = 0.9·mAP50-95(B) + 0.1·mAP50(B)`，`best_epoch = argmax(该值)`。这是**登记口径**，不是 ultralytics 保存 best.pt 的口径。
- `raw/train-v2b-log.txt:427`：`EarlyStopping: … Best results observed at epoch 45, best model saved as best.pt`（ultralytics 自身声明）。
- `raw/train-v2b-log.txt:442` `TRAIN_RESULT_JSON`：`best_epoch="49"`、mAP50(B)=0.03111。**两者并存于同一文件**，错位不是推断而是原始证据。
- 盘上 `training_data/sfx-v1/train-v2/runs/v2b/results.csv`（gitignored，本轮直读）逐行复算：
  - epoch45：mAP50(B)=**0.02786**、mAP50-95(B)=0.01728、mAP50(M)=0.03996、mAP50-95(M)=**0.01991**
  - epoch49：mAP50(B)=**0.03111**、mAP50-95(B)=0.01934、mAP50(M)=0.03156、mAP50-95(M)=0.01549
  - wrapper box-fitness：ep45=0.018338，ep49=0.020517 → argmax=49 ✓（报告 §2.3 描述准确）
  - ultralytics 系 seg-fitness（0.1·mAP50(M)+0.9·mAP50-95(M)）：ep45=0.021915，ep49=0.017097；对 75 行 M 列扫描，`mAP50-95(M)` 最大值确为 ep45 的 0.01991（次高 0.01791@ep65）→ **argmax=45，与 EarlyStopping 自洽** ✓

**两行差距（回答「差多少」）**：mAP50(B) 0.03111 vs 0.02786（Δ=−0.00325，相对 −10.4%）；mAP50-95(B) 0.01934 vs 0.01728（Δ=−0.00206，−10.7%）；bbox precision 0.62142 vs 0.48784；而 seg 侧反向：mAP50-95(M) 0.01549 vs 0.01991（ep45 高 +28.5%）。即**两个 epoch 各胜一半**，被保存的是 seg 侧更好的 ep45。

**是否影响「v2b 5/5 零误检 vs v2a 4/5」**：**不影响，作者的链路理解正确**。AC3 导出的是 `runs/v2b/weights/best.pt`（=ep45 权重，`export-smoke-v2.json` 登记 `best_pt_sha256 c22f0175…` 与 log 一致）→ `weights/v2b/best.onnx`（`944e8114…`）→ 评测实测推理。**结论建立在 best.pt 实物的实测输出上**，与登记口径无关；`eval-v2b.json` 与 `eval-comparison.json` 的 5/5、P=1.0 是真实测量值。

**但由此暴露一个必须修的文档缺陷（P2-1）**：报告 §0/§2.4 称「两版 best fitness 持平级（A 0.02083 vs B 0.02052，wrapper 口径）」——0.02052 属于**未保存的 ep49**。按同一口径比较**被评权重**：A(ep79) 0.020833 vs B(ep45) 0.018338 → **A 高约 13.6%**，不持平。该错位句已写入 §7.1.5「收敛后持平」并进入 T3 材料。**更大问题**：val 集 = 4 页 53 框，其中 pre-k08/pre-k09 共 **51 框为 KO 长条页（三方全 0）**，仅 2 个 ogkalu crop 框可判 → **val 对 A/B 基本无判别力**，任何基于 val 的 A/B 排序（无论「持平」还是「A 优」）都不该写。建议改为：「val 无判别力（53 框中 51 框落在三方均 0 召回的 KO 长条页，仅 2 个 crop 框可判）——A/B 判定只依据考卷实测」。

### Q2【KO letterbox 结构性发现】—— **证据充分，结论成立；呈报基本正确，附 1 项补强**

静态可验的三层证据（全部通过）：

1. **页尺寸/aspect 数字全部命中**（`manifest.val.json`/`manifest.test.json` 的 `image.width/height` 字段直读）：pre-k08 **690×51971**（1:75）、pre-k09 **690×100480**（1:146）、pre-k01 **690×62133**（1:90）、pre-k02 **600×18401**（1:31）——与 `eval-comparison.json` `ko_page_dimensions` 及报告 §4.4 逐字一致。
2. **chiqui7 复跑 n_pred=0 的原始证据在案**：`eval-chiqui7-rerun.json` 中 pre-k08/pre-k09 两页在 0.5/0.2 双口径下 `preds: []`、`n_pred: 0`、27/24 个 `gt_matched_flags` 全 false；KO-56 汇总 `0/56, n_pred=0`。现役权重在全 58 框上的 n_pred=2 全部落在 ogkalu crop 页（`eval-chiqui7-rerun.json` 中 imp-ogkalu-k09-r071 n_pred=2、matched=0）→ 汇总 0/58、P=0.0 与逐页一致 ✓。
3. **「V1 56/56 系切块口径产物」— 决定性旁证**（本轮独立找到，报告未直接引用代码行）：
   - R1 KO 域扫描器 `M2-SFX-ANNOTATE-R1-zcode/experiments/M2-SFX-ANNOTATE-R1/stage1_preannotate.py:6-8,280`：`scan_mode = "tile_690x1024_overlap128"`，注释原文「webtoon 宽 690 超长条，整页 letterbox 会把宽缩到 172px 丢失细节，故 690x1024 无缩放 tile、重叠 128」。
   - R2 BJ 域扫描器 `…ANNOTATE-R2/stage1_preannotate_bj_new.py:196-197`：`scan_mode="fullpage_letterbox", n_tiles=1`。
   - 即：**KO 的 GT/候选池来自原生分辨率 tile 扫描，而 V2 生产序列是整页 letterbox**——两个口径在物理成像层面就不同，56/56 与 0/56 不可直比；同时对 BJ 而言两口径相同，故 chiqui7 复跑 BJ 6 框与 worksheet 候选逐值相同属**确定性必然**（亦印证 §5.3.5 循环性裁定的证据 2）。
   - 结论定性「瓶颈=推理序列口径非权重」**证据充分**。

**对 T3/T4 呈报的裁定**：报告 §7.1.3「KO 门必须先解决序列口径」+ §7.2.4「KO 域切换影响=零（双向）」方向正确、与证据一致。两处建议精化：
- §7.1.3「**任何权重**都无法通过沿用整页序列的 KO 门」应限定为「**任何沿用整页 letterbox 序列**的权重」——这是口径命题不是权重命题（结论本身不变）。
- 建议补一句溯源（P3-5）：**KO val/test 的 GT 框本身派生于 chiqui7 的 tile 扫描检出**，故「chiqui7 复跑 0/58」与「V2 0/56」在该 GT 下都不是中立基准确证，避免读者把 KO 数字当作跨模型绝对能力。

### Q3【A/B 可比性与结论强度】—— 同口径**成立**；结论措辞**大体守纪律，有 3 处越界**

**可比性成立（脚本级证据）**：A/B 由**同一脚本同一入口**训练（`train_v2.py` 单一 `_train()` 路径），共享 `EPOCHS=150/PATIENCE=30/SEED=20261004/IMGSZ=1024/BATCH=8/WORKERS=2/DEVICE=0`，数据同为 train-v2 `dataset.yaml`；唯一变量=基座权重（这正是 A/B 的设计变量）。两版 `TRAIN_RESULT_JSON` 的 `batch_used=8`、`requested_epochs=150`、`patience=30` 一致，OOM 分支未触发（两 log 中 `out of memory` 匹配数=0）。**「同口径」断言成立**。
- 保留意见（不构成缺陷）：`optimizer=auto` 在 ultralytics 中按训练配置自动选择，且 GPU 训练本身非严格确定性；**单次运行的 5 框考卷差异不具统计意义**——这正是报告自己声明的纪律。

**结论强度**：报告 §4.6 明确「directional、统计功效低、禁用『显著』、V2 数字不作门判定」，Task/Handoff 亦如此；「B 版略优」限于 5 框考卷 + 全 63 框 7 vs 6，措辞总体守纪律。**但 3 处越界**（P3-3/P3-4/P2-1）：
- §2.4 标题句「初始 loss B **显著**低于 A」——使用本报告自设 `wording_discipline` 明令禁用的「显著」（虽指向 loss 而非模型优劣，仍属纪律自破）。
- §4.2/§7.1.1「B 版考卷零误检 precision 1.0，**超** chiqui7 独立复跑（P 0.8333）」——差异实为**1 个预测框**（6→5），且 chiqui7 的唯一「误检」是已被 R2 仲裁 delete 的气泡框；在 5 框考卷上称「超」超出功效。建议改为「与 chiqui7 复跑同级（差 1 个误检，功效不足以判优劣）」。
- §2.4/§0/§7.1.5 的「持平级」（见 Q1）。

**结论**：Q3 的「B 版略优」在**评测口径**上可保留为 directional，但必须与 val 口径脱钩（val 无判别力），且不得升级为门判定或生产切换依据——报告已作此声明，条件性通过。

---

## 发现清单

### P0（阻断）
无。

### P1（严重）
无。

### P2（须在集成前修正，纯文档）
- **P2-1 位置**：`train-v2-report.md` §0 摘要行 19、§2.4 行 93、§7.1.5 行 232；`doc/tasks/M2-SFX-TRAIN-V2.md:71`。
  **问题**：「两版 best fitness 持平级（A 0.02083 vs B 0.02052）」把 A 的**已保存**校重与 B 的**未保存** epoch49 指标并列；同口径下被评权重为 A(ep79) 0.020833 vs B(ep45) 0.018338（wrapper）/ A 0.027000 vs B 0.021915（ultralytics seg-fitness），**A 明显更高**。与 §2.3 自述的错位警告直接矛盾。
  **建议**：删除该对比，替换为「val 无判别力（53 框中 51 框落于 KO 长条页，仅 2 个 crop 框可判），A/B 判定只依据考卷实测；两版被评权重的 val 指标差（wrapper 0.020833 vs 0.018338）在无判别力 val 上不构成结论」。同步修 §7.1.5「收敛后持平」。
- **P2-2 位置**：`train-v2-report.md` §2.3 行 87-89；`doc/handoffs/M2-SFX-TRAIN-V2-zcode-20261005.md:79`。
  **问题**：§2.3 只纠正了 `best_epoch` 字段，未点明**commit `093631d2` message 内的持平框架**同样基于未保存 epoch——该 message 永久留在 Git（reflog 已核实其原文含「best mAP50(B) A 0.02833/B 0.03111…持平级」），是下游最可能被引用的载体。
  **建议**：在 §2.3/Handoff 风险段加一句：「commit 093631d2 message 中 A/B「持平级」基于 B 版未保存的 epoch49 指标，与 §2.3 双口径说明冲突，**以本报告口径为准**；历史不改写。」
- **P2-3 位置**：`train-v2-report.md` §0/§5；Task 行 74。
  **问题**：报告以「**独立复核（非作者）= PASS**」呈现 §5，但据交付链描述该复核为 workflow 内复核（作者侧/同批次），而 Task 的 `reviewer: DeepSeek Harness（非作者）` 尚未出具结论。读者可能把 §5 误读为本 Task 的正式独立审查。
  **建议**：§5 标题与 Task 行 74 改为「**作者侧复核（workflow 内，非本 Task 正式 Review）**」，并保留「正式独立 Review 结论见 doc/reviews/」。

### P3（建议修正，影响可读性/纪律）
- **P3-4 措辞**：`train-v2-report.md:94`「初始 loss B **显著**低于 A」→ 删「显著」或改「约低一半（9.196→4.814）」。
- **P3-5 措辞**：`train-v2-report.md:132` 与 `:228`「**超** chiqui7 独立复跑（P 0.8333）」→ 改为「差 1 个误检，功效不足以判优劣」。
- **P3-6 补强**：§4.4 增加一句「KO val/test 的 GT 框源自 chiqui7 tile 扫描检出（R1 `scan_mode=tile_690x1024_overlap128`），故 KO 数字并非跨模型中立基准」，把「两口径不可直比」的物理根因（tile vs letterbox）写明。
- **P3-7 新增边界**：报告未登记**训练集内同样存在 KO 长条页**（`manifest.train.json` 中 6 页 height≥10000：80494/28156/46000/81776/**131289**/100674，即 pre-k03..k07/k10）。这些页的 SFX 框在 imgsz=1024 整页下同为亚像素，对 901 页训练集构成潜在标签噪声。建议在 §6 诚实边界 + §7.1.3 各加一句，作为 T3 序列口径实验的数据侧议题。

### P4（cosmetic / 已登记项确认）
- **P4-8**：Task 行 72「KO 页 690×51971~100480（aspect 1:31~1:146）」宽度区间不含 pre-k02（600×18401）。建议写「690×51971~100480 与 600×18401」。（`eval-comparison.json` 内四页数字本身正确。）
- **P4-9**：§3「合成页双档 conf」对应 raw 实际为 `detect.conf_0.5` / `detect.conf_0.01`（非 0.2），措辞与 raw 对齐即可。
- **P4-10**：ISSUE-B 已确认属实——`training_data/sfx-v1/train-v2/export-summary.json` 内容为 AC1 准备摘要（`"task": "…AC1 数据准备…"`，与 `verification/…/prepare-summary.json` 同源），文件名易误读为 AC3 导出摘要。**gitignored 树，不入 Git，不影响证据链**；建议集成轮删除或改名。
- **P4-11**：`export-smoke-v2.json` v2b 段 `sha_gate.ok.production_pin = 27d162e94d7d`（v2a 残留）已由作者登记为 cosmetic ✓；门语义确由两次 `sha_gate.fired`（v2a/v2b 各自被 `PROVIDER_FAILED` 正确拒跑，detail 内 sha 前缀分别 27d/944）实证。
- **P4-12**：Task frontmatter `owner_claim` 未记 docs head hash（实际 tip=`2768c6c1`）。建议在 Task/Handoff 补 `docs_commit: 2768c6c1`，便于集成轮引用。

### 本轮静态复算通过项（供集成轮采信）
- **交付链**：`G:/CODEX/New Manga/.git/worktrees/M2-SFX-TRAIN-V2-zcode/logs/HEAD` 直读确认 `4e881720 → b0c338bc → 75148bc4(prep) → 093631d2(train) → ba94fa76(eval) → 2768c6c1(docs)=tip`，与审查指令链**逐字一致**。
- **分集数字**：`manifest.train.json` = **901** `sample_id` / **2304** `polygon`；`manifest.val.json` = **4** / **53**；`manifest.test.json` = **2** / **5**；`manifest.challenge.json` = 2 / 5（直读）；全量 `manifest.train-v2.json` = **909** / **2367**（=2304+53+5+5）✓ 与 `prepare-summary.json`、报告 §1.1 全数一致。
- **构成**：组合模式匹配总数 `"synth-r1"(324) + "group": "own-manga/"(558) + "annotation_status": "pseudo"(418) + "partial"(140) = 1440` = 实际匹配总数 ✓；R2 真实 19 页（pre-k03~07/k10 六个 + imp-ogkalu 十项 + pre-bj16/23/24）逐 id 可点；→ 901/2304、19+324+558 与 partial140/pseudo418 全部对账通过。
- **入册包**：`own-manga-ingest/own_manga_manifest_records.json` 中 `"sample_id": "imp-own-` **558** 条 ✓；两页考卷 sha（`7bee7f05…`/`87116db2…`）在该包内**零出现** ✓（考卷零重叠的页图 sha 层在 challenge 侧的抽样反证）。
- **指纹**：`345deeb7…0e63` 同时出现在 `manifest.challenge.json.fingerprint`、`prepare-summary.json.fingerprint`、报告/Task/Handoff ✓。
- **评测逐框算术**（三方 raw JSON 直读重算，全部吻合）：
  - v2b：BJ17 2/2 + BJ18 3/3 = 5/5（n_pred 5，P 1.0）；KO58 = 2（两 crop 各 1）/4 pred，P 0.5；KO56 n_pred=0；full63 7/9=0.7778 ✓
  - v2a：BJ17 2（多 1 误检 conf 0.6711）+ BJ18 2 = 4/5（n_pred 5，P 0.8）；KO58 = 2/4 pred；full63 6/9=0.6667 ✓
  - chiqui7 rerun：BJ17 2/3（B02 conf 0.8634 误检）+ BJ18 3/3 = 5/5（P 0.8333）；KO58 = 0/2 pred（imp-ogkalu-k09-r071）、KO56 n_pred=0；full63 5/8=0.625 ✓
  - GT 基数：2+3+27+24+1+1+2+3 = **63** ✓（`eval_v2.py:140` 断言 63 一致）
- **V1 基线引用真实性**：V1 worktree `eval-challenge.json` 确认 new_model 0/5@0.5、1/5@0.2（n_pred 3、P 0.3333）；`eval-kodelta.json` 确认 new_model 0/58@0.5、KO-56 chiqui7 预标注 56/56 P 0.8235 n_pred 68，且含「chiqui7 预标注仅覆盖 KO 页 4 样本，imp-ogkalu-* 2 样本预标注源=ogkalu rt-detr」范围注 → `eval-comparison.json.v1_baseline_git_reference` 逐值一致 ✓；`caliber_note`「两口径不可直比」的诚实定性与 V1 原文自洽 ✓。
- **零 src / pin**：`src/infrastructure/providers/detection_sfx.py:107-111` 现值为 `SFX_HF_REPO="chiqui7/yolo11-manga-seg"`、`SFX_HF_REVISION="7f5f5c04…"`、`SFX_WEIGHTS_SHA256="d87389af…b646"`，与 `eval_v2.py:38` `PROD_PIN_HEAD`、`eval-chiqui7-rerun.json.model.sha256`、`eval-comparison.json.sides.chiqui7_prod_rerun.model.sha` **四处逐字同值** ✓；`export_smoke` 中 pin 前缀 `d87389af4350` 一致 ✓。（盘上 onnx 文件 sha 重算=第四处实测，本轮无命令，未验证。）
- **ISSUE-A 数字**：见 Q1，全部由盘上 `results.csv` 复算（ep45/ep49/ep79 三行）+ 两 log 的 `TRAIN_RESULT_JSON`/EarlyStopping 交叉印证。
- **B 版基座登记**：`raw/b-base-readme-snapshot.md` `license: other`、Manga109-s 衍生声明、类别 `0:character/1:frame/2:speech_bubble`（推荐 checkpoint）✓；`raw/b-base-snapshot-metadata.json` 对应 `yolo11s_1024_b8` 快照（ep18，mask mAP50 0.86488）✓；T0 `preflight-report.md:69` 登记 `0:frame/1:speech_bubble/2:character` + `other` 未审计 ✓ → 报告 §2.2/§6 的「逐字一致」与「同 repo 不同 checkpoint 类别顺序」澄清**均属事实**；`train-v2b-log.txt:36` `Transferred 555/561` ✓；log 中 `base_sha256=1f0fd609…b77e0` ✓。
- **初始 loss**：`train-v2a-log.txt:59` epoch1 首 iter seg=**9.196**；`train-v2b-log.txt:54` epoch1 首 iter seg=**4.814** ✓（报告 §2.4 数字准确，仅措辞越界见 P3-4）。
- **16 文件允许面**：盘上可见 experiment 4 脚本 + `verification/M2-SFX-TRAIN-V2/{prepare-summary.json + raw 10 件}` + 本 Task = **16** ✓（与 `4e881720..ba94fa76` 声明一致；docs 提交的 report/handoff 不在该区间）；`__pycache__/*.pyc` 被 `.gitignore:1-2` 覆盖、`/training_data/` 由 `.gitignore:13` 覆盖（与报告引用一致）✓。**注**：`git diff --name-only`/`-- src/` 本身无命令，未独立验证。
- **AC5 归口**：`doc/REBASELINE_PLAN.md` 中尚无 T3/T4 Task 条目（仅 V1 行注明「T3/T4 裁决材料已呈报」），故 AC5 的「刷新呈报」落在报告 §7 属正确归口；§7.2 的 pin 单值替换/来源字段（已核实 `SFX_HF_REPO`/`SFX_HF_REVISION` 在位）/许可审计前置/KO 双向为零/回退=恢复 d87389af **逐条与 src 现状和证据一致**。

---

## 逐 AC 结论

- **AC1 PASS**：validate 558/558、指纹 `345deeb7…0e63`、组隔离 0 违例、考卷零重叠三层断言均有记录；本轮独立静态复算 901/2304、4/53、2/5、2/5、909/2367、558 own-manga（partial140/pseudo418）+324 synth+19 real **全数吻合**；pinned 经 `assign_splits(force=True,pinned=…)` 函数参数（脚本内、未改 T1a 交付物）；349/349 零漂移与 sha 全量交集为**运行级声明，本轮未验证**（沙箱无命令）。
- **AC2 PASS**：A/B 双版完整非 skip（两 log `TRAIN_RESULT_JSON`：A 109/150 best@79 1816.4s、B 75/150 1312.0s）、同口径参数在脚本级一致、OOM=0（两 log 无 out of memory）、权重 sha 登记齐全；**ISSUE-A 属实且已如实登记**，但登记口径错位被 §0/§2.4 复用（P2-1）→ AC2 判 PASS，条件随 P2 修正。
- **AC3 PASS**：`export-smoke-v2.json` `"exit": 0`、两版 `sha_gate.fired`→`full_chain_ok`、names/imgsz/(1,40,21504) 齐；P2-1 整改落地可证（`eval_v2.py` 全文无预标注池读取路径，`:129-131` 生产 sha 断言、`:197-201` `provider.detect` 真调用）；三方 8 页 63 框逐框算术与 raw JSON 完全一致；chiqui7「6 框与 worksheet 逐值相同」的循环性解释由 R2 `scan_mode=fullpage_letterbox,n_tiles=1` **独立坐实**。
- **AC4 PASS**：报告/Handoff/Task 回填齐、口径一致、诚实边界（own-manga 框=模型输出未收紧、chiqui7 同源性、BJ 主攻形态不在包内、许可备案）逐条在案；唯 §5「独立复核」署名需澄清（P2-3）及 3 处措辞（P3）。
- **AC5 PASS（附 1 项修正）**：T3/T4 材料以报告 §7 呈报，与证据一致（KO 序列口径前置、复跑口径固化、pin/来源/许可/回退四件套）；但「A/B 基座结论」项沿用了被推翻的「收敛后持平」（P2-1），须同步修正。
- **AC6 PASS（部分未验证）**：允许面 16 文件与盘上实况自洽、数据/权重/ONNX/run 全在 `/training_data/`（`.gitignore:13`）且 `*.pt/*.onnx` 另受 `.gitignore:9-10` 保护、入册包在 task-envs 外部树只读；`git diff -- src/` 为空与工作树干净属**运行级声明，本轮未独立验证**。

---

## 推荐下一步

1. **（Author=ZCode，条件闭合轮，纯文档）** 落 3 条 P2 修正：①删除/改写 §0/§2.4/§7.1.5 的「best fitness 持平级」，改提「val 无判别力（51/53 框落于 KO 长条页）」；②在 §2.3/Handoff 风险段注明 commit `093631d2` message 的持平框架基于未保存 epoch49、以报告为准；③§5 与 Task 行 74 的「独立复核」改称「作者侧复核（workflow 内）」。同时处理 P3-4/P3-5 两处措辞、P3-6/P3-7 两处补强、P4-8/P4-12 两处小修；`export-summary.json`（ISSUE-B）由集成轮删除或改名。**禁改 `src/**`；不得重写 Git 历史。**
2. **（Reviewer=DSH，本会话续轮，可选）** 条件落盘后做一次**限定范围复审**：仅核对 §2.3/§0/§2.4/§7 的措辞一致性与 Task/Handoff 同步，其余结论继承本轮。
3. **（Integrator=编排会话代行 Codex）** 复审通过后 merge `agent/zcode/M2-SFX-TRAIN-V2`（base `4e881720`，tip 以 docs head 后新提交为准）→ 回填 `doc/tasks/M2-SFX-TRAIN-V2.md`（`review_events` 追加本轮 review、`status=done`、`integration_commit`）与 `doc/STATUS.md`/`REBASELINE_PLAN`；落盘 review 文档 `doc/reviews/M2-SFX-TRAIN-V2-2768c6c1-dsh-r1.md`。集成 Gate：`git diff 4e881720..<merge> -- src/` 为空、`git show <merge>:src/infrastructure/providers/detection_sfx.py` 含 `d87389af`、`git check-ignore training_data/sfx-v1/train-v2/weights/v2b/best.onnx` 命中。
4. **（用户/编排裁决点，不随本 Task 释放）** ①T3 是否释放（BJ 深度扩标 + **KO 序列口径对照实验（tile/切块 vs 整页 letterbox）作为 KO 域 Gate 前置** + P2-1 复跑口径固化）；②T4 生产切换条件确认（v2b 为 directional 候选 `944e8114…`，**挪到生产前须先补 `license: other` 审计**，并处置 `SFX_HF_REPO`/`SFX_HF_REVISION` 来源语义）。**V2 数字不作门判定，不得据本报告直接切换生产。**
5. **（环境提示，交编排）** 本 worktree 的 DSH 命令沙箱本轮不可用（`grantWrite` Win32 5），导致 sha 重算/`git diff`/推理重放类验证无法执行；建议在集成轮换用可写沙箱或由 Codex 侧完成运行级复核，以免同类「无命令」再次阻断验证链路。
