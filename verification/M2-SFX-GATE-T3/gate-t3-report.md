# M2-SFX-GATE-T3 · 正式评测门判定报告（G1-G8 逐门判定 + T4 材料终稿）

- Task：[doc/tasks/M2-SFX-GATE-T3.md](../../doc/tasks/M2-SFX-GATE-T3.md) AC5 ｜ Owner：ZCode ｜ Reviewer：DeepSeek Harness（非作者，待 review）｜ 日期：2026-10-05
- 分支 `agent/zcode/M2-SFX-GATE-T3`（base_commit=`87ca8724`）｜ worktree：`G:/CODEX/New Manga.worktrees/M2-SFX-GATE-T3-zcode` ｜ AC4 评测执行 head=`2e95760a`
- 门定义事实源：[gate-definition.md](gate-definition.md) **v1.0-frozen**（commit `907011a2`，评测执行开始后零修改——冻结时序实证见 §5-①）。本报告逐门判定均依据 gate-definition v1.0 §4.Gx，引用非冻结版本定义的判定无效（§5.4）。
- 判定纪律（§0.4）：统计功效低，禁用「显著」；0 也如实；**FAIL 如实判定即为本 Task 成功**。

## 0. 判定速览

| 门 | 类型 | chiqui7（基线，pin 原样） | v2a（候选） | v2b（候选） | 判定 |
|---|---|---|---|---|---|
| G1 BJ 毛笔竖排召回门 | 硬 | 5/5 R=1.0 P=0.8333（判据基线值） | 4/5 R=0.8 **P=0.8 < 0.8333** | 5/5 R=1.0 P=1.0 | **v2a FAIL / v2b PASS** |
| G2 KO 长条页门（tile 冻结口径，双 GT） | 硬 | 口径合规✓；KO-B 基线 41/135 R=0.3037 | 口径合规✓；KO-B **0.2593 < 0.3037** | 口径合规✓；KO-B **0.3556 ≥ 0.3037** | **v2a FAIL / v2b PASS** |
| G3 数据健全先决门 | 硬·先决 | 9/9 断言 PASS（S1-S9，冻结六断言超集） | 同左 | 同左 | **PASS（先决成立，全部评测数字可作门判定）** |
| G4 考卷覆盖门 | directional | — | — | — | **登记（§4.4，无 PASS/FAIL）** |
| G5 生产序列契约门 | 硬 | pin 原样（sha 逐字自检） | 5/5 断言 | 5/5 断言 | **双候选 PASS** |
| G6 域差/噪声归因门 | directional | — | — | — | **登记（§4.6，无 PASS/FAIL）** |
| G7 端到端损害门 | 硬 | 同链对照全程 | 零新增故障（检测契约面） | 零新增故障（检测契约面） | **PASS（条件性：T4 补证前置）**（§4.7） |
| G8 部署门 checklist | 硬·候选资格 | — | 审计只登记（已因 G1/G2 丧失资格） | **7/7 出证，license:other 审计 PASS** | **v2b 候选资格保持** |

**候选资格结论**：**v2b（best.onnx `944e8114…`）= 唯一通过全部定资格硬门（G1/G2/G5/G8）的切换候选**（G7=PASS（条件性：T4 补证前置），对两候选同约束、不改变本结论，§4.7）；v2a 因 G1（P 0.8<0.8333）+G2（KO-B 不回退失败）双 FAIL **丧失候选资格**。切换与否=T4 用户裁决点（§7）。

## 1. Gate 定义摘要（权威定义=gate-definition v1.0 §4，此处仅为判定引用摘要）

- **G1（§4.G1，硬）**：vol05 组考卷原始 5 框（**不变判据集**，pre-bj17×2+pre-bj18×3，坐标逐值（0.1 精度）等值=R2 出厂）整页 letterbox 严格 conf≥0.50 召回 **≥4/5** 且 precision **≥ chiqui7 同链路独立复跑基线**（V2 参考值 0.8333＝6 pred 5 匹配；以 T3 当轮复跑实测值为判据值）。R3-MISS 补画后 BJ 全 complete 页扩展集 **directional**（challenge 侧=泛化 / train 侧=记忆性，不作判据）。
- **G2（§4.G2，硬）**：KO 长条页在 tile_690x1024_ov128 **冻结口径**（逐字=KO-TILE 提案 §3）下评测，双 GT 属性分离——①口径合规硬判据；②**AC3 非派生切片上候选权重 recall ≥ chiqui7 基线**（模型质量属性=硬判据载体）；chiqui7 派生 56 框=采集一致性属性仅 directional（同源复现上界）。KO-B 0 框判 INDETERMINATE；隔离纪律实证失败判 FAIL-数据无效。
- **G3（§4.G3，硬·先决）**：组隔离 0 违例 / challenge 单组 / 考卷 5 框逐位=出厂 / names 双通道 / 指纹可复现 / 考卷零重叠三层——六断言全零违例；任一 FAIL 则全轮评测数字不作门判定。
- **G4（§4.G4，directional）**：形态×页×held-out 覆盖矩阵登记（已知缺口原样入表）；考卷重划=用户/编排裁决项，本门不执行。
- **G5（§4.G5，硬）**：五断言——①SHA 门先证 PROVIDER_FAILED 拒跑外来权重；②进程内重指全链 EXIT=0 零 src pin 零改动；③names 逐字；④imgsz `metadata_parsed`=1024；⑤输出张量 `(1, 40, N)`。
- **G6（§4.G6，directional）**：评测差值按「样本量/合成-真实域差/标签噪声/GT 循环性」四层归因登记，own-manga 418 自蒸馏框不与 BJ 正集同权；无 PASS/FAIL。
- **G7（§4.G7，硬）**：新权重进程内替换后 SFX→翻译链路冒烟（≥1 合成+≥1 真实页，沿 T0/V2 方式零 src）——①全链 EXIT=0；②契约合法 fail-closed 保持（0 候选=合法空输入）；③vs 基线同链对照新增故障=0；框集差异 directional。
- **G8（§4.G8，硬·checklist）**：7 项部署 checklist（产物 sha/来源链/metadata/许可结算/pin 替换与来源字段处置/回退语义/数据备案）全项出证；**v2b `license:other` 审计在本门结算**，审计 FAIL 即丧失候选资格。

## 2. 前置数据（AC2/AC3 产物，判定的数据底座）

### 2.1 R3-MISS 补画（R3MISS：A=13 框 / B=17 框（6 页）→ 终裁框集）

- 六页（pre-bj32~37）双 AI 独立看整页画框：a=13 框 / b=17 框；独立配对（IoU≥0.5、IoU 降序+面积降序）= matched 12 / only_a 1 / only_b 5，与盘上 consensus.json/divergence.json per_page 逐值一致（复核 ③）。
- 终裁框集：**BJ32-35 转正 15 框**（12 consensus union + 3 arbiter keep，`manifest.r4` 与 consensus/arbiter 框集合逐位一致，S8）；**BJ36/37 双 AI 终裁零 SFX = 0 框**（留底册 pseudo 不入，schema 零框页先例 pre-bj25）——0 也如实。
- 新口径 `mode=ai-direct-annotation` 首例登记（无模型预标，conf 概念不适用）；train-v4 重切 916 全量、challenge 3 页 8 框（pre-bj32 随 vol05 组入 challenge，组隔离优先——ask「钉 train」表述与 G3 冲突的处置登记于 prepare-train-v4-summary.json `bj3237_pin_divergence`）。

### 2.2 KO 非派生考题（KONPD：A=128 框 / B=135 框（4 页）→ 切片+与派生 GT 偏差统计）

- 双 AI 独立整页标注（任务书零既有坐标，`npd-gt.json isolation_discipline: task_brief_leak_check=PASS`）：a=128 / b=135，matched 106 / only_a 22 / only_b 29（逐值一致，复核 ③）。
- 定稿切片 **135 框** = 106 keep-union + 29 arbitrated kept（keep 19+keep-merged 9+correct 1）；removed 22（delete 8+delete-duplicate 14）；51/51 终裁 final_xyxy 与落册框逐位一致（S7）。
- **与派生 GT 56 框偏差统计（G2-B 数据基础）**：matched(IoU≥0.5) **40** / derived_only **16** / npd_only **95**（S9 + npd-gt derived_gt_crosscheck.summary 一致）——差集两向=GT 偏差的直接度量（G6 ④层归因输入）。
- 隔离旁证（复核 ②）：a/b 互比 matched IoU 连续分布（npd n=106 min 0.5033/max 0.9893，逐位相同=0）；标注坐标 100% 整数 vs 模型 preds 整数占比 12.8%（过程观察，未舍入坐标未落盘，不可复算）——数值形态完全分离，无抄写痕迹。

## 3. 三方 × 四数据集矩阵（M2-SFX-GATE-T3 AC4 · commit 2e95760a）

匹配：box IoU≥0.5 conf 降序贪心（eval_v2.py:68-97 逐字）；推理：letterbox=生产 SfxDetectionProvider.detect 全序列，KO tile=tile_ov128 冻结口径（tile_calib.py tile 实现逐字）+letterbox 对照并行。

| 数据集 → | ① bj-exam（考卷 5 框，letterbox，GT=derived） | ② bj-ext（BJ complete 12 页 33 框，letterbox，GT=mixed） | ③ ko-tile（KO 4 页派生 GT 56 框，tile_ov128，GT=derived/采集一致性） | ④ ko-npd（非派生 GT 135 框，tile_ov128，GT=non-derived/模型质量） |
|---|---|---|---|---|
| **chiqui7**（pin d87389af 原样零重指） | conf0.5：**5/5** R=1.0 P=0.8333（n_pred=6）｜conf0.2：5/5 P=0.8333 | conf0.5：**13/33** R=0.3939 P=0.9286（challenge 5/8｜train 8/25）｜conf0.2：13/33 P=0.9286 | conf0.5：**56/56** R=1.0 P=0.8235（n_pred=68）｜conf0.2：56/56 P=0.6667｜letterbox 对照：0/56 双 conf | conf0.5：**41/135** R=0.3037 P=0.6029｜conf0.2：42/135 P=0.5｜letterbox 对照：0/135 双 conf |
| **v2a**（27d162e9…，进程内重指） | conf0.5：**4/5** R=0.8 P=0.8（n_pred=5）｜conf0.2：4/5 P=0.6667 | conf0.5：**15/33** R=0.4545 P=0.9375（challenge 4/8｜train 11/25）｜conf0.2：17/33 P=0.7727 | conf0.5：**28/56** R=0.5 P=0.3333（n_pred=84）｜conf0.2：36/56 P=0.1765｜letterbox 对照：0/56 双 conf | conf0.5：**35/135** R=0.2593 P=0.4167｜conf0.2：51/135 P=0.25｜letterbox 对照：0/135 双 conf |
| **v2b**（944e8114…，进程内重指） | conf0.5：**5/5** R=1.0 P=1.0（n_pred=5）｜conf0.2：5/5 P=1.0 | conf0.5：**13/33** R=0.3939 P=0.8667（challenge 5/8｜train 8/25）｜conf0.2：15/33 P=0.8333 | conf0.5：**35/56** R=0.625 P=0.3465（n_pred=101）｜conf0.2：43/56 P=0.2019｜letterbox 对照：0/56 双 conf | conf0.5：**48/135** R=0.3556 P=0.4752｜conf0.2：64/135 P=0.3005｜letterbox 对照：0/135 双 conf |

GT 属性标注（每格）：①考卷 5 框=R2 出厂（chiqui7 扫描候选派生，GT⊂候选池循环性）；②bj-ext=R2/R3 判定链 8 页 18 框 derived + R4-BJ32-35 补画 4 页 15 框 ai-direct（ai-direct-annotation 首例）；③ko-tile=chiqui7 派生 56 框（采集一致性 directional）；④ko-npd=AC3 双 AI 独立标注 135 框（模型质量，G2-B 硬判据载体）。

复算核验：experiments/M2-SFX-GATE-T3/recompute_eval_t3.py（GT 四源盘上重读+匹配算法独立重实现，不 import 评测脚本）——36 格（24 主格+12 letterbox 对照格）全部 == eval-matrix.json，输出 ALL CELLS RECOMPUTED == eval-matrix.json。**本 AC5 轮（2026-10-05）再次复跑：同输出，EXIT=0**（§5-⑤）。

## 4. G1-G8 逐门判定

### 4.1 G1 · BJ 毛笔竖排召回门【硬】——v2a FAIL / v2b PASS

依据 gate-definition v1.0 §4.G1。判据值=chiqui7 当轮同链路复跑 precision **0.8333**（eval-matrix.json matrix.chiqui7.bj-exam."0.5"，n_pred=6；与 V2 参考值一致）。conf≥0.50 严格口径：

| 方 | 召回（≥4/5？） | precision（≥0.8333？） | 判定 |
|---|---|---|---|
| v2a | 4/5（0.8）✓ | **0.8 ✗**（5 pred 中 1 误检） | **FAIL**（条件②不成立） |
| v2b | 5/5（1.0）✓ | **1.0 ✓**（5 pred 零误检） | **PASS** |

- chiqui7 基线自身 5/5 P=0.8333：GT⊂其候选池，召回=数学必然自洽上界（§3.5 循环性总登记），其 precision 中唯一误检=曾被 R2 仲裁 delete 的气泡框（与判定链自洽）。
- directional 扩展集（bj-ext 12 页 33 框，不影响判定）：challenge 侧（泛化考题）chiqui7 5/8=v2b 5/8 > v2a 4/8；train 侧（记忆性）v2a 11/25 > chiqui7 8/25=v2b 8/25——**v2b 主攻形态考卷达标但扩展集泛化未证超越基线**（G6 ②层归因输入；T4 建议附带条件）。
- 已知限制沿用：5 框功效低（1 框差=20%），判据对单框波动敏感；v2a 的 FAIL 对单框+1 误检敏感，如实判定、不作统计解读。

### 4.2 G2 · KO 长条页门（tile_ov128 冻结口径，双 GT）【硬】——v2a FAIL / v2b PASS

依据 gate-definition v1.0 §4.G2。**条件①口径合规=PASS**（两候选同判）：冻结参数逐字复刻断言在位——K_TILE_H=1024/K_TILE_OVERLAP=128/TILE_PAGE_NMS_IOU=0.5（eval_gate_t3.py:104-106）、tile_ys 步长 896+末尾补页底锚点（:218-226）、页级跨 tile conf 降序贪心 NMS 0.5（:194-215）、每 tile 生产序列本体 `dsfx._letterbox`+`dsfx._sfx_boxes`（:428-429）；实测 tile_stats_total n_tiles=261（=4 页 tile 数合计，双 conf 一致）；**letterbox 对照并行 12 格全 0/56、0/135（n_pred=0 双 conf）**——零输出结构性事实复现；chiqui7 ko-tile 56/56 P=0.8235 与 KO-TILE 参考矩阵**逐位一致**（同链路复现上界）。

**条件②KO-B 非派生切片相对不回退**（ko-npd 135 框，conf≥0.50；基线=chiqui7 41/135 R=0.3037）：

| 方 | KO-B recall | 判定 |
|---|---|---|
| v2a | **35/135（0.2593）< 0.3037** | 条件②不成立 → **FAIL** |
| v2b | **48/135（0.3556）≥ 0.3037** | 条件②成立 → **PASS** |

- INDETERMINATE 分支未触发：KO-B=135 框非 0；隔离纪律实证 PASS（task_brief_leak_check=PASS）——非数据无效。
- directional（不作判据）：ko-tile 派生 56 框 v2a 28/56、v2b 35/56（v2b 与 KO-TILE 参考逐位一致）；precision 全 directional（chiqui7 0.8235≈1−代审拒绝率非独立误检率）；宽松 conf0.2 仅诊断（v2a ko-tile P 崩至 0.1765，复现 0.2 档奖励高误检的理由）。
- **v2b 派生侧下降（56→35/56）与非派生侧上升（基线→0.3556）并存**：恰为双 GT 属性分离要捕捉的现象——派生 GT 相位/粒度偏差（G6 ④）与模型质量（G2-B）不可由派生侧单独区分；G2 硬线按冻结定义落在非派生侧。

### 4.3 G3 · 数据集健全性与考卷完整性门【硬·先决】——PASS

依据 gate-definition v1.0 §4.G3。`verify_data_integrity.py` 落盘独立复算 **9/9 PASS**（S1 schema r4=94/train-v4=916 零错误、S2 指纹 `6bb0ea13…` seed=20261004 可复现且 lock 一致、S3 组隔离 0 违例+challenge 仅 densho810/vol05、S4 考卷 5 框逐值（0.1 精度）等值=R2 出厂、S5 names 双通道={0:bubble,1:panel,2:sfx,3:text}、S6 考卷零重叠三层（组名/样本 id/页图 sha256）=0、S7 npd chain 135 全溯、S8 r4 框源 15/15、S9 交集 56/135/40/16/95）——冻结六断言（①-⑥）全在位且零违例，S7-S9 为 AC2/AC3 链路附加断言（超集）。**先决成立：G1/G2/G7 全部评测数字可作门判定。**

### 4.4 G4 · 考卷覆盖门【directional】——登记

依据 gate-definition v1.0 §4.G4。覆盖矩阵（形态×页×held-out；train-v4 split 归属；形态=R3 §5.2 对照表，人工/AI 归类非受控词表）：

| 形态 | 页（框数，split） | 有无独立考题（challenge/held-out） |
|---|---|---|
| 竖排毛笔假名（主攻） | pre-bj17（2，challenge） | **有**（考卷） |
| 竖排/斜置粗毛笔片假名 | pre-bj18（3，challenge） | **有**（考卷） |
| 毛笔竖排（BJ32，ai-direct 首例） | pre-bj32（3，challenge） | **有**（随组入 challenge，新增） |
| 斜向粗毛笔片假名（シャ/ゴ类）+回填 | pre-bj16（6，train） | **无** |
| 手术室潦草拟声 | pre-bj22（2，train） | **无** |
| 竖排字块 | pre-bj28（1，train） | **无** |
| 竖排拟声 | pre-bj29（1，train） | **无** |
| 毛笔竖排（BJ33-35，ai-direct 首例） | pre-bj33/34/35（3/3/6，train） | **无** |
| （pre-bj23/24 既有 complete 页） | pre-bj23（2）/pre-bj24（1），train | **无** |

- **已知缺口（R3 §6.2 原样入表）**：考卷对新回填形态（pre-bj16 回填 3 框、pre-bj28/29 新形态、pre-bj22 潦草拟声、BJ33-35 ai-direct 页）**零覆盖**——G1 判定结论只对考卷覆盖形态（竖排毛笔假名/斜置粗毛笔片假名）可外推。
- 考卷重划=用户/编排裁决项，**本门不执行**（R3 §6.2 提案语义顺延）；bj-ext split_buckets（§4.1）为 G1 外推边界提供 challenge/train 分列读数。

### 4.5 G5 · 生产序列契约门【硬】——双候选 PASS（5/5）

依据 gate-definition v1.0 §4.G5。逐断言（v2a/v2b 同判）：

1. **SHA 门先证 PROVIDER_FAILED**：**T3 当轮未复跑**（eval_gate_t3.py:477-487 的「先验断言」=盘上权重 sha256 实算比对，非拒跑反向验证）；判定依据=**V2 当轮证据显式收编**：export-smoke-v2.json sha_gate.fired=:38-43/:122-127（v2a/v2b error_code=PROVIDER_FAILED）+sha_gate.ok=:44-50/:128-134，gate-definition §4.G5 阈值依据「三轮全过，正式门原样收编」。收编合法性依据：收编证据（export-smoke-v2.json）的 v2a/v2b onnx sha（:5/:11 `27d162e9…`/`944e8114…`）与 T3 被测权重 sha（eval-matrix.json weights）逐字相同（`27d162e9…`/`944e8114…`）——收编对象为同一批工件，非异批引用。
2. **进程内重指全链 EXIT=0、零 src、pin 零改动**：T3 当轮=eval_gate_t3.py 进程内重指（build 窗口 :509-519+finally 恢复；推理窗口 :529-531+:711-712），三方 36 格全链跑完 EXIT=0（raw/run-full.log 完整落盘+eval-matrix.json 写出）；src/tests/contracts/packaging/apps diff=0（base 87ca8724..HEAD 26 文件全在 Task 允许路径，§5-⑥）；pin 现值 `d87389af…`（detection_sfx.py:110-112）base..HEAD 逐字一致。
3. **names 逐字**：`_build_engine` 装载期断言 drift 即拒（detection_sfx.py:433-443）——T3 三权重 engine build 全过；V2 逐字登记 names_metadata=`{0: 'bubble', 1: 'panel', 2: 'sfx', 3: 'text'}`（export-smoke-v2.json:55/139）。
4. **imgsz `metadata_parsed`=1024**：T3 三权重 engine 逐行实测（raw/run-full.log:6-8）+eval-matrix.json weights.imgsz_source。
5. **输出张量 `(1, 40, N)`**：V2 实测 [1,40,21504]（export-smoke-v2.json:92-98 v2a / :176-181 v2b）；T3 侧生产 `_sfx_boxes` 按 (1,40,N) 消费（detection_sfx.py:551-552）且 36 格全链成功（含 chiqui7 与 KO-TILE 参考矩阵逐位复现的功能性旁证）。

### 4.6 G6 · 合成-真实域差与标签噪声归因门【directional】——登记

依据 gate-definition v1.0 §4.G6。四层归因（登记性推断，无消融支撑，层间可能混杂）：

1. **样本量层**：考卷 5 框（1 框差=20%）、ko-tile 56 框、ko-npd 135 框、bj-ext 33 框——全部低功效；v2a G1 FAIL 由 1 漏检+1 误检决定，v2b G2-B 达线差=+0.052（7 框）——门判定对个位数框敏感，「样本量不足为首要瓶颈」（V1 §6 DSH P3-3）仍是方向性假设。
2. **合成-真实域差层**：train-v4 构成=synthetic 324（横排系统字体/限定毛笔字体，与真竖排毛笔形态覆盖度**未经验证**，R3 §6.1）+own-manga 558（框=模型输出未手工收紧）vs BJ 真实正集 12 页 33 框——v2b 考卷 5/5 但 bj-ext challenge 5/8 与基线持平：合成监督对主攻形态考卷有效、对扩展形态泛化未证。
3. **标签噪声层**：own-manga 418 自蒸馏框带框入 train 当 GT（DSH P3-4 处置不对称——densho810 64 pseudo 不入 train）**不与 BJ 正集同权**；KO 长条页 6 页训练侧标签在整页 letterbox 下亚像素（DSH P3-7）——v2a/v2b ko-npd 与 chiqui7 的差值部分可归此层（与 GT 偏差层混杂，不可分离）。
4. **GT 循环性层**：bj-exam 5 框与 ko-tile 56 框 GT⊂chiqui7 候选池——chiqui7 5/5、56/56 为自洽上界非独立性能（§3.5），「基线vs候选」在 derived GT 上的差值无法区分模型差与 GT 偏；ko-npd 135 框=ai-consensus 非人工 GT（见 §6 诚实边界），跨模型中立性成立但标注质量层误差在。

### 4.7 G7 · 端到端损害门【硬】——PASS（条件性：T4 补证前置）

依据 gate-definition v1.0 §4.G7（口径=「沿 T0/V2 冒烟方式零 src」）。三条件：

1. **全链 EXIT=0** ✓：V2 双版导出+生产序列冒烟 `"exit": 0`（export-smoke-v2.json:184）；T3 当轮三方 36 格全链（进程内重指→`SfxDetectionProvider.detect`/tile 序列）跑完零异常，全量产物落盘。
2. **契约合法、fail-closed 保持** ✓：V2 冒烟 detect 步骤实测 `class_filter=sfx`、`coordinate_space=page-global`（export-smoke-v2.json:67-87/150-170）；conf≥0.5 零候选=合法空输入非异常（T0 §5 先例，0 也如实）；T3 全部 raw JSON 契约面同构。
3. **vs 基线同链对照新增故障=0** ✓（验证边界=检测契约面）：同页同参 chiqui7 基线同链路全程在列（V2 §4 三方同序列+T3 36 格三方对照）；v2a/v2b 未引入任何错误/异常/超时新增；框集差异 directional 登记（如 bj-exam v2b 5 框 vs 基线 6 框=基线少 1 误检，系新权重的目的非损害）。

**执行边界（如实）与条件**：翻译链入口的深层调用（run_qualification 级 policy=translate 端到端，先例=M2-SFX-E2E-MATERIAL BJ06 8/8）在 T3 当轮与 T0/V2 均未以新权重执行——G7 链路证据止于检测契约面（此即冻结口径「T0/V2 冒烟方式」的边界；编排裁决（2026-10-05）已确认该边界口径并写入 Task `review_events`）。因此本判定为**条件性 PASS**：**条件=T4 部署前必须以新权重补跑一次 BJ06 型 policy=translate 端到端冒烟（run_qualification 级深层调用），未补证前不得把 G7 记为部署就绪**（§7-④；对 v2a/v2b 同约束）。该条件不影响候选资格结论（v2b 资格由 G1/G2/G5/G8 定，§0）。

### 4.8 G8 · 部署门【硬·checklist】——v2b 7/7 出证 PASS（候选资格保持）；v2a 审计只登记（已因 G1/G2 丧失资格）

依据 gate-definition v1.0 §4.G8。checklist 逐项证据：

1. **产物 sha** ✓：v2b best.onnx sha256=`944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d`（本 AC5 轮盘上重算一致；eval-matrix.json weights+raw/run-full.log:4+V2 export-smoke-v2.json:119 四处同值）。
2. **来源链可溯源** ✓：基座 .pt=`1f0fd609e7dc29c831255db67586ed5623f9bebae6a1e29fae197c1c6d7b77e0`（HF `anonimkaq4/manga-page-element-segmentation` snapshots/yolo11s_1024_b8，81,340,348 B；V2 报告 §2.2 盘上重算一致）→ 训练 log raw/train-v2b-log.txt TRAIN_RESULT_JSON（best.pt=`c22f0175…`）→ export-smoke-v2.json:104（best_pt_sha256=`c22f0175…`）→:119（best.onnx=`944e8114…`）——全链无断点。
3. **metadata 契约** ✓：引用 G5 结果（names/imgsz/张量形 5/5 PASS）。
4. **许可结算** ✓（本门执行，结论=**PASS 附登记义务**，v2b 候选资格保持）：
   - 快照证据：`verification/M2-SFX-TRAIN-V2/raw/b-base-readme-snapshot.md` frontmatter `license: other`；datasets 含 `hal-utokyo/Manga109-s`+MangaSeg+synthetic-sharded。
   - **Manga109-s 衍生声明核验**：README :85 原文逐字在位——「This repository does not include or grant rights to the original Manga109-s images or MangaSeg annotations. Review and comply with the MangaSeg, Manga109-s, and Ultralytics licenses before … redistributing this checkpoint, or using it commercially.」
   - 审计结论：本项目用途=基座 checkpoint **本地衍生训练**（未使用 Manga109-s 图像/MangaSeg 标注本体；训练数据=own-manga/densho810/合成/HF webtoon）；衍生权重 gitignored 外部树（`.gitignore:13`）**未入库未分发非商业**；Ultralytics AGPL 属性沿 v2a 同一用户备案（2026-10-04 降权备案）覆盖——当前用途范围内**无未决阻塞**。
   - 登记义务：①若未来分发/发布 v2b 衍生权重或公布数据集衍生图像，须先复核 Manga109-s/MangaSeg 授权边界（**本结论不外推到分发场景**）；②MangaSeg 论文引用（README :94-100）登记为备案项；③credit 义务保守登记：b-base README :91 明示「If you use the model, its training data, or derived results, cite the MangaSeg paper」——若未来公布衍生权重或衍生视觉结果则触发 citation 义务；当前本地未分发场景不触发，分发场景复核（「Copyrighted by Minshan Xie」README :87 同此口径）。审计=文档证据链审计非法律意见（§4.G8 已知限制）。
   - v2a：基座官方 yolo11s-seg.pt AGPL-3.0——用户 2026-10-04 许可降权备案覆盖沿 T0 §6（非阻断）；v2a 已因 G1/G2 FAIL 丧失候选资格，其审计仅登记。
5. **pin 替换语义** ✓（方案出证，执行属 T4）：现值实测 `SFX_WEIGHTS_SHA256=d87389af…`（detection_sfx.py:110-112）、`SFX_HF_REPO/SFX_HF_REVISION=chiqui7/yolo11-manga-seg@7f5f5c04…`（:107-108）；方案=sha 单值替换（SHA 门语义不变）+来源字段处置=HF 发布通道 or 本地发布通道登记（V2 §7.2.3）——终稿见 §7-③。
6. **回退语义** ✓（方案出证）：恢复 `SFX_WEIGHTS_SHA256=d87389af…`+旧权重文件在位（chiqui7 权重随包 NSIS 通道不变——M2-SFX-PROD-1 交付；本轮 packaging/ 零 diff 实测）。
7. **训练数据许可备案引用** ✓：own-manga=用户自有（2026-10-04 备案）、densho810 报告义务（2026-11-02 窗口前达标，`74fa71e9` 履行登记）、HF webtoon/P&C 沿二次裁决备案（T0 §6 表原样引用）。

## 5. 作者侧复核（workflow 内 phase 5，非本 Task 正式独立 Review）

**AC4 后作者侧复核=PASS**（六项复核全部执行于本 worktree，HEAD=`2e95760a`，base=`87ca8724`；未发现隔离失败或数字矛盾；2 条非阻断观察见 §5.1；正式独立 Review（DSH，非作者）见 doc/reviews/，集成轮落盘）：①Gate 定义完备性 PASS（五节齐备+冻结时序实证：`git log -- gate-definition.md` 仅 `907011a2` 一个提交（12:21），其后 AC2/AC3（`3c84f438`，20:07）与 AC4（`2e95760a`，20:38）均未触碰——评测执行开始后零修改；定义引用生产契约行号本 worktree 直验一致）；②标注独立性间接验证 PASS（作者侧脚本重算：a/b 互比 IoU 连续分布无逐位重合、npd vs 派生 GT matched 40 无 1.0、坐标数值指纹 100% 整数 vs preds 整数占比 12.8%（过程观察，未舍入坐标未落盘，不可复算）分离；「任务书无泄漏」为作者自查字段，本项为产物级间接验证）；③比对仲裁闭环重算 PASS（BJ32-37 a13/b17/matched12/only_a1/only_b5 与 npd a128/b135/matched106/only_a22/only_b29 逐值一致，135=106+29、51/51 final_xyxy 逐位）；④断言复跑 PASS（9/9+git diff 为空）；⑤评测矩阵复算 PASS（36 格全量超抽格要求）；⑥零 src+pin PASS（26 文件全在允许路径，禁止路径 diff 空，pin base..HEAD 逐字一致）。

**2 条非阻断观察（原样保留）**：(1) T3 当轮未复跑 PROVIDER_FAILED 拒跑反向验证——G5-① 判定须显式引用 V2 证据（本报告 §4.5-1 已照办）；(2) AC5（G1-G8 逐门判定+T4 终稿）在复核时点尚未产出——即本报告。

**本 AC5 轮自证复跑（本 ask 实测，2026-10-05）**：

| # | 命令 | 结果 |
|---|---|---|
| 1 | `git diff --name-only 87ca8724..HEAD`（+禁止路径过滤） | 26 文件全在 doc/tasks+experiments/M2-SFX-GATE-T3+verification/M2-SFX-GATE-T3；src/tests/doc/contracts/packaging/apps/doc/STATUS.md diff=0 |
| 2 | python hashlib 三权重 sha256 盘上重算 | chiqui7=`d87389af…`（=生产 pin 逐字）/v2a=`27d162e9…`/v2b=`944e8114…` 全一致 |
| 3 | `python experiments/M2-SFX-GATE-T3/verify_data_integrity.py` | 9/9 PASS，EXIT=0；复算后 data-integrity-asserts.json `git diff` 为空（与提交版本逐位一致） |
| 4 | `python experiments/M2-SFX-GATE-T3/recompute_eval_t3.py` | 36 格 ALL CELLS RECOMPUTED == eval-matrix.json，EXIT=0 |
| 5 | `grep -n` 生产 pin 行号 | detection_sfx.py:108 SFX_HF_REVISION / :110-112 SFX_WEIGHTS_SHA256=`d87389af…` / :118 SFX_CONF_THRESHOLD=0.5 / :121 SFX_NMS_IOU=0.7 / :137 SFX_CLASS_MAP / :138 SFX_CLASS_ID——与 gate-definition §1 引用一致 |

## 6. 诚实边界

1. **AI 直接标注首例**：R4-BJ32-35 15 框与 ko-npd 135 框均为 ai-direct-annotation（无模型预标，conf 概念不适用）——首例形态，标注质量依赖双 AI 视觉能力+比对仲裁兜底，无逐框人工确认（human_review=false）。
2. **非派生 GT 也是 AI 共识非人工**：ko-npd 135 框=双 AI 独立标注+仲裁（ai-consensus）——G2-B「模型质量硬判据载体」的绝对值本身带标注质量层误差；G2-B 判据为**相对不回退**（同一 GT 下比较），相对结论对该层误差较不敏感，但 135 vs 56 交集 40/差集 95（derived_only 16/npd_only 95）表明两套 GT 粒度差异大，绝对 recall 不应解读为「全量 SFX 检出率」。
3. **统计功效低**：考卷 5 框（1 框=20%）、ko-tile 56 框、ko-npd 135 框；全部判定禁用「显著」；G1/G2 的 PASS/FAIL 是合同门判定不是统计结论；v2a 的双 FAIL 由个位数框决定。
4. **GT 循环性**：bj-exam 5 框+ko-tile 56 框 GT⊂chiqui7 候选池——chiqui7 5/5、56/56 为自洽上界；跨模型中立考题只有 ko-npd。
5. **证据边界**：G5-① 的 PROVIDER_FAILED 反向验证=T3 当轮未复跑、引用 V2 当轮证据（§4.5-1）；G7=**PASS（条件性：T4 补证前置）**——翻译链深层调用未以新权重执行，G7 链路证据止于检测契约面；T4 部署前必须以新权重补跑一次 BJ06 型 policy=translate 端到端冒烟（run_qualification 级深层调用），未补证前不得把 G7 记为部署就绪（§4.7）。
6. **own-manga 418 自蒸馏框**不与 BJ 正集同权（G6 ③层）；合成数据对真竖排毛笔形态覆盖度未经验证。
7. **形态归类**为人工/AI 归类非受控词表（G4 限制）；BJ36/37 双 AI 终裁零 SFX（0 框）如实登记。

## 7. T4 材料终稿（生产切换建议 · 交编排/用户裁决；不随本 Task 自动释放）

### 7.1 切换候选权重建议

- **推荐候选=v2b（best.onnx `944e8114…`）——唯一通过全部定资格硬门的候选**：G1 5/5 P=1.0（≥基线 0.8333）、G2-B 0.3556≥0.3037、G5 5/5、G7 PASS（条件性：T4 补证前置，§4.7）、G8 审计 PASS。v2a 丧失候选资格（G1 P=0.8<0.8333+G2-B 0.2593<0.3037 双 FAIL）。
- **切换与否=T4 用户裁决点**（沿 V2 §7.2.1 口径顺延；T3 起为门判定支持下的裁决）。附带条件如实：①**KO 域改善=0**——letterbox 下 KO 全零是序列口径问题非权重问题，仅切权重不解决 KO（tile 化是 KO 改善前置，见 7.3）；②bj-ext challenge 5/8 与基线持平、train 8/25 持平——主攻形态考卷外的泛化改善未证；③低功效 directional，切换收益=考卷零误检（P 1.0 vs 0.8333，差 1 框）+非派生 KO 切片 +0.052——量级如实。
- 若用户裁决暂不切换：v2b 权重与证据链已完整登记，可随时按 §7-③④ 走部署。

### 7.2 许可审计结算（G8-4 终态）

v2b 基座 `license: other` 审计=**PASS 附登记义务**（§4.8-4：本地衍生使用/未分发范围成立；分发场景须复核；MangaSeg 引用备案；credit 保守登记——当前未分发场景不触发，分发场景复核）——**v2b 候选资格保持**。v2a AGPL 备案沿 T0（非阻断；已丧失候选资格仅登记）。densho810 报告义务窗口 **2026-11-02**——部署时点核查归 T4。

### 7.3 生产 tile 化方案（KO 域，src 变更=T4 专属授权）

- 现状：生产 `SfxDetectionProvider.detect` 整页 letterbox 下 KO 长条页（宽 600/690、aspect 1:31~1:146）SFX 亚像素化，**三方含现役全零**——KO 域 SFX 从 0 到有的唯一路径=序列口径 tile 化。
- 方案：按 G2 冻结口径实现 KO 分支——tile 宽=页宽原生无缩放、高 1024、重叠 128（步长 896）、末尾补 `page_h-1024` 锚点、tile 内生产序列本体、页级跨 tile IoU 0.5 conf 降序贪心 NMS（eval_gate_t3.py tile 实现即蓝本，已过 KO-TILE 参考矩阵逐位复现+36 格复算）；按页宽/aspect 阈值路由（宽≤690 量级页走 tile，普通页走 letterbox——阈值定值=T4 裁量点）。
- **性能预算裁决前置**：T3 实测 tile 口径 @CPUExecutionProvider 每页 17-81s（pre-k08 17-18s/pre-k09 50s/pre-k01 71-74s/pre-k02 77-81s，58-112 tiles/页）——生产可用性须先做性能裁决（GPU 推理/降采样策略/异步化或接受时延）。
- 相位依赖登记：ov128 与 GT 采集相位一致（T4 落地复测偏离 56/56 上界先查相位，KO-TILE 限制②）；宽≠690/600 的 KO 页 tile 参数化未覆盖（KO-TILE §9）。

### 7.4 回退方案与部署 checklist 补证项

- 回退：`SFX_WEIGHTS_SHA256` 单值恢复 `d87389af…`+chiqui7 权重随包 NSIS 通道不动；SHA 门语义不变（拒跑外来权重已实证）；回退后 KO 域回到「零召回」现状（与切换前一致，无额外损害）。
- T4 部署前补证项：①以新权重（若裁决切换=v2b）补跑一次 BJ06 型 policy=translate 端到端冒烟（run_qualification 级深层调用）——**G7 条件性 PASS 的补证义务（§4.7）：未补证前不得把 G7 记为部署就绪**；②`SFX_HF_REPO`/`SFX_HF_REVISION` 来源字段处置落地（HF 发布通道 or 本地发布通道登记）；③densho810 义务窗口 2026-11-02 时点核查；④pin 替换 src 变更由 Codex 授权 T4 专属新 Task 执行（T3 零 src 红线不破）。

## 8. 证据索引

| 类别 | 路径 |
|---|---|
| 门定义（v1.0-frozen） | verification/M2-SFX-GATE-T3/gate-definition.md（commit 907011a2） |
| 评测矩阵+逐框明细 | verification/M2-SFX-GATE-T3/eval-matrix.json + raw/eval-{chiqui7,v2a,v2b}-{bj-exam,bj-ext,ko-tile,ko-npd}.json + raw/run-full.log |
| 数据健全断言 | verification/M2-SFX-GATE-T3/data-integrity-asserts.json（9/9）；prepare-train-v4-summary.json |
| 前置数据 | training_data/sfx-v1/gate-t3/npd-gt.json（gitignored：135 框+isolation+crosscheck）、annotate-r4/manifest.r4.json、consensus/divergence（gitignored 树） |
| 脚本（零 src，共 8 个） | experiments/M2-SFX-GATE-T3/{eval_gate_t3,verify_data_integrity,recompute_eval_t3,prepare_dataset_v4,stage_r4_manifest,compare_judgments,arb_previews_npd,finalize_npd}.py |
| G5/G8 引用的先例证据 | verification/M2-SFX-TRAIN-V2/raw/export-smoke-v2.json（sha_gate.fired/exit:0/names/imgsz/张量形）、raw/b-base-{readme-snapshot.md,args.yaml,snapshot-metadata.json}、raw/train-v2{a,b}-log.txt；T0 preflight-report.md §5/§6 |
| 基线口径先例 | experiments/M2-SFX-TRAIN-V2/eval_v2.py:68-97/129-131/197-201；experiments/M2-KO-TILE-CALIB/tile_calib.py（tile 实现蓝本） |
| 生产契约 | src/infrastructure/providers/detection_sfx.py:108/110-112/118/121/137/138（本 worktree grep 实测） |
