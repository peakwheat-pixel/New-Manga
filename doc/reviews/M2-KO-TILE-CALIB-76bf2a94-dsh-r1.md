# M2-KO-TILE-CALIB DSH r1 审查报告（2026-10-05）

> 审查对象：tip 76bf2a94；Verdict=approved_with_conditions（1×P1、1×P2、8×P3、4×P4）。
> stdout 全文转录（86 行完整）。P1-1/P2-1 返修后定点复审请求见 doc/reviews/ 后续 r2 文件（如有）。

## Verdict

**approved_with_conditions**（1×P1、1×P2 硬条件；其余 P3/P4 集成轮或 T3 采信前闭合）

- 数字层：四组主矩阵 + 两组变体的**每一个数字**都能与盘上 raw JSON / run-full.log / 变体矩阵逐格对上；GT=56 框与 R2 manifest 一致；跨 tile NMS 去重语义正确（保高 conf 压低 conf），无重复计数。
- 实现层（Q1）：tile 口径确实复用生产 `dsfx._letterbox`/`_sfx_boxes` 函数本体，且我找到一条比作者自证更强的**逐位交叉证据**（见 Q1），等价性成立。
- 证据解释层（Q3）：**存在一处未登记的方法论循环性**——本 Task 的 GT 正是 chiqui7 在同一 `tile_690x1024_overlap128` 口径下的扫描候选经 AI 代审保留的框（`sources:["chiqui7-scan"]`、`human_review=false`）。因此 "chiqui7 tile ov128 56/56 满召回（P 0.8235）" 与 "ov128 实测最优" 是**同源复现/自洽**，不是独立召回证据；报告与提案却把它们当作口径优越性的主证据，且把"与 R1 采集口径同构"写成正面理由。这是 P1，必须在 T3 采信前登记并降级表述。
- **核心结论不因此被推翻**：letterbox 双权重双 conf 全部 `n_pred=0`（GT 无关的绝对事实）vs tile `n_pred=68/101`，"瓶颈=序列口径非权重" 仍站得住；死去的是"56/56/0.82 是独立性能数字"这层外衣。
- 运行级声明**无法验证**：本会话沙箱命令执行不可用（每次 `pwsh` 均 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`），故 `recompute_matrix.py` 复跑、`git diff/log`、`git status`、pin 落位 diff 全部未运行级验证；本报告为纯静态审查（AC5 仅静态可判部分）。
- 建议落盘路径：`doc/reviews/M2-KO-TILE-CALIB-76bf2a94-dsh-r1.md`（reviewer 落盘，本 Reviewer 只读不改）。

## 重点问题 Q1/Q2/Q3 裁定

### Q1【tile 实现等价性】= **成立（PASS），措辞需收窄一处（P3）**

属实且证据强于作者自证：

1. `tile_calib.py:288-289` 直接调用 `dsfx._letterbox(numpy, np.asarray(tile), imgsz)` + `dsfx._sfx_boxes(session, inp, scale, conf, page_w=..., page_h=th)`，即 `detection_sfx.py:516-532`/`:535-589` 的函数本体；生产 `detect()`（`detection_sfx.py:290-313`）用的是同两个函数、同参数语义（imgsz 同取自 `_build_engine`，`page_h=rgb.shape[0]` ↔ tile 的 `th`）。未使用的仅 `_validate_request`/`_frame_pixels`/`RegionCandidate` 打包，均不改像素。tile 恒 1024 高、宽 690/600 → `scale=1.0`，`_letterbox` 的 resize 为恒等、右侧灰边 334/424px，与"原生分辨率无缩放"一致。
2. **逐位交叉证据（我独立发现，比 §8-① 的行号核对更硬）**：`raw/eval-chiqui7-tile.json` 中 pre-k01 的两条 pred 为 `(322.1,35995.3,391.4,36049.9) conf=0.5927` 与 `(529.0,35915.0,592.5,35967.9) conf=0.5358`（`:2331-2346`），与 `manifest.test.json` pre-k01 的 GT polygon（`:18-58`）及 `boxes_meta.conf`（`:74`,`:85`）**逐字相同**；pre-k02 matched pred conf 0.8985/0.7474/0.5731 与 GT conf（`manifest.test.json:304/315/326`）逐位相同。GT 的 conf 来自 R1 `scan_mode=tile_690x1024_overlap128` 的 `chiqui7-scan` 采集（`stage1_preannotate.py:238-262`、`run_inference` 复用生产 `detection_sfx`），故该实验 tile 口径 ≡ R1 采集口径 ≡ 生产逐 tile 序列，三者在像素与数值上都等价。
3. 措辞缺陷：`tile_calib.py:24` 与报告 §4 的"与 letterbox 口径**唯一差异=成像口径**"对**推理序列**不严格成立——tile 化把类无关 NMS 0.7 的竞争集从"整页"变成"每 tile 内"，并新增了"仅 sfx 类、IoU 0.5"的页级合并（生产无对应步骤）。二者已在 `preprocess-caliber-table.md` §1 行 9/11 与 §2 登记、且是切块固有代价，故**合同风险条款所指的"预处理（letterbox/归一化/阈值语义）等价"成立**；但"唯一差异"应改为"预处理与成像口径唯一差异"，并把 NMS 作用域/页级合并阈值列为**有意新增步骤**。同理提案 §3.2"Gate 数字与生产序列语义严格同构、T4 切换时无口径换算"对页级合并不成立（T4 必须新造该层）。

### Q2【跨 tile 合并与重复计数】= **正确（PASS）**

1. 去重实现与 R1 逐字同构：`tile_calib.py:163-185` vs `stage1_preannotate.py:172-191`（conf 降序贪心、IoU≥0.5、先入者胜=保高 conf）。映射 `[b0, b1+y0, b2, b3+y0]`（`tile_calib.py:290`，沿 R1 `:257-258`）正确；`_map_back` 已把 y clip 到 tile 高，`y+y0 ≤ y1 ≤ page_h`，无需二次 clip（报告 §8-③ 该点正确）。
2. 计数自洽（我逐页复核）：chiqui7@0.5 raw 31+29+2+8=70 → 页级 NMS 后 30+28+2+8=68；chiqui7@0.2 89→84；v2b@0.5 109→101；v2b@0.2 245→213。与 `run-full.log:21/32/39/44/49/55`、`sfx_after_page_nms`（`eval-chiqui7-tile.json:738/1621/2352/2896` 等）及矩阵 `n_pred` 全部一致。逐页 matched（27/24/2/3、14/17/2/2）与 `gt_matched_flags` 自洽。
3. **12 个多余 pred 的性质已被我查实**：它们不是重复计数、也不是 NMS 失效，而是 R2 代审的"delete"集合——pre-k08 3 个（`manifest.val.json:966-983`）、pre-k09 4 个（`:2047-2068`）、pre-k01 0 个（`:107-108` kept_units=2、excluded_delete_boxes=[]）、pre-k02 5 个（`manifest.test.json:349-377`，kept_units=3），合计 3+4+0+5=**12** = 68−56。即 68 = 56 保留 + 12 弃用，框框可分、两两 IoU<0.5，页级 NMS 既未过度合并也未漏并。§8-③ 的 pre-k08 31→30 与唯一被压框（conf 0.5607 vs 保留 0.8229，IoU 0.6168）与盘上一致（0.8229 在 kept 中可见，`eval-chiqui7-tile.json:651`）。
4. 证据完备性小缺口：raw 只存 `per_tile[].sfx_raw` 计数与 NMS 后框，**不存 NMS 前框坐标**，故页级合并这一步无法仅凭盘上产物复算（须重跑推理，§8-③ 正是这么做的）；`recompute_matrix.py` 复算的是"矩阵↔raw"，不含该步。AC"数字从盘上产物复算"对矩阵成立，对 NMS 步不成立（P3）。

### Q3【口径建议的保守性】= **方向保守、论证不保守（P1 + P3）**

- **P1｜GT 同源性未登记（循环性）**：4 页 GT 的每一个框 sources 均为 `chiqui7-scan`，`quality_note` 自述"boxes=conf>=0.5 判定保留框（codex+agy 共识+分歧仲裁）…human_review=false"（`manifest.val.json:953`、`manifest.test.json:96`）。GT 由 chiqui7 在 ov128 tile 口径下产出并经 AI 剔除 12 框。后果：
  - "chiqui7 tile ov128 = 56/56 满召回"= **同源复现**（conf 逐位相同），不是独立召回度量；
  - "precision 0.8235" 的 68 个 pred 中 12 个正是被代审删除的同一批框，故 0.8235 ≈ 1−代审拒绝率，**不是**独立 GT 上的误检率；
  - "ov128 三相位实测最优（56/44/45）"是 GT 在 ov128 网格上采集的**必然后果**，不能作为"ov128 是更优口径"的独立证据；变体真正证明的是"tile 网格相位强烈调制召回"（这是真发现）；
  - 提案 §3.1 把"与 R1 采集口径完全同构 / Gate 数字与训练数据采集口径同构"写成**正面理由**——同一事实恰是循环性本身（框架倒置）。
  - 本项目已有先例：V1 的"预标注引用口径"循环性正是 T2-V2 的 P2-1 整改对象（`eval_v2.py:263-278`、STATUS）；本 Task 以新形式重新引入且未登记，应比照登记。
  - **核心结论仍成立**（不判 P0）：letterbox 双权重双 conf `n_pred=0` 是与 GT 无关的绝对事实（零输出，非低分），tile 侧 `n_pred=68/101` 亦与 GT 无关；"序列口径瓶颈非权重"由此独立成立。需要改的是标题数字的**证据等级**与提案的证据归属。
- **支撑充分的部分**：只跑 3 个相位就下"ov128 最优"结论在样本量上确实单薄，但报告已用"相位方差"登记不确定性、directional 纪律执行到位（全文无"显著"）；conf0.5 主口径建议保守且自洽（chiqui7 0.5→0.2 召回零增益纯增误检 68→84）；v2b 不入切换候选的裁定**恰当且更保守**（注意 v2b 还是在一个偏 chiqui7 的 GT 上测得的 35/56，实际劣势只会被放大而非缩小）。
- **P3｜"无跨 tile 切断"表述对 ov256 不成立**：我独立复算（详见发现清单 P3-1）——ov128 下 56/56 框完整落入某 tile（最高框 675.8px 落 y0=14336，余量 200.8px），ov448 亦 56/56，但 **ov256 下 pre-k08 #20（h=675.8，y 14483.2–15159.0）无法完整落入任何 tile**（最近网格 13824，d=659.2 > 348.2）；即 ov256 的召回损失至少一部分是**几何切断**而非纯相位。报告 §3/提案 §2 的"每框都可完整落入单 tile"应限定为"ov128/ov448 下"。
- **P3｜冻结 ov128 的鲁棒性未给结构规则**：保证任意对齐都容纳高 h 的框需 `step ≤ 1024−h`，即 `overlap ≥ h_max`；本 GT 的 h_max=675.8 → 需 overlap ≥ 676。ov128 仅对 h≤128 有结构保证；本页集 56/56 全落入本身也是"GT 由 ov128 网格产出"的推论，且有 5 框余量 <5px（pre-k09 #6 余量 0.0px、#17 余量 0.5px）。提案"已知风险①"只写了相位方差，应补这条硬约束（或给出自适应/锚定方案）供 T4。

## 发现清单

**P0（阻断）**：无。未发现伪造、数字不一致、范围违规或等价性缺陷。

**P1（重大；T3 采信前必须闭合）**
- **P1-1｜GT 同源性/循环性未登记，且被用作正面理由**。证据：`manifest.val.json:650-953`（pre-k08 27 框 sources 全 `chiqui7-scan`）、`:1764-2034`（pre-k09 24 框同）、`manifest.test.json:75-96/305-337`（pre-k01/k02 同）；`quality_note`（val:953 / test:96）"conf>=0.5 判定保留框…human_review=false"；R1 采集口径 `stage1_preannotate.py:211`（conf_floor 0.01）+`:238-262`。逐位复现证据见 Q1-2。要求：①在 `calib-report.md` §1/§9 与 `ko-caliber-proposal.md` §3 登记"GT=R2 正集，其框由 chiqui7 在 tile ov128 口径下采集并经 AI 代审保留（human_review=false）"；②把 "56/56 满召回 / P 0.8235" 改述为"同源复现（自洽性）"，把"ov128 实测最优"改述为"ov128 是与 GT 采集相位一致的相位；变体证明相位敏感"；③把该口径建议的证据基础明确锚定到 GT 无关事实（letterbox `n_pred=0` ↔ tile `n_pred>0`）；④把"与 R1 采集口径同构"从"理由"移入"限制"；⑤建议 T3 若要用该 Gate 度量模型质量而非采集一致性，需另建非 chiqui7 派生的 KO GT 切片（提请 T3 裁决）。

**P2（必须修，但可集成轮闭合）**
- **P2-1｜Handoff 记录的复现命令不可执行**：`doc/handoffs/M2-KO-TILE-CALIB-zcode-20261005.md:67`（"实际命令/步骤"）、`:84`（接收方式复现）、`:177`（运行次数）均写 `python experiments/M2-KO-TILE-CALIB/tile_calib.py --mode full`；但 `tile_calib.py:317-328` 的 argparse 无 `--mode`（仅 `--smoke/--overlap/--sides/--calibers/--out-suffix`），该命令 exit 2。`mode=full` 只是 `tile_calib.py:344` 的打印文本（`'smoke' if args.smoke else 'full'`），作者把日志字样误当 CLI 参数。要求改为实际命令（无参运行，如 `python experiments/M2-KO-TILE-CALIB/tile_calib.py`）。

**P3（应修；不阻断）**
- **P3-1｜"无跨 tile 切断"对 ov256 不成立**（复算见 Q3）：`calib-report.md:82-86`、`ko-caliber-proposal.md:44-47`、Handoff:47 应限定到 ov128/ov448，并对 ov256 的 pre-k08 #20 归因"几何切断 + 相位"。
- **P3-2｜提案 §2 变体 tiles 数列错**：`ko-caliber-proposal.md:41-42` 写 ov256 "~345"、ov448 "~445"；盘上 `n_tiles` 实测 ov256 = 68+131+81+24 = **304**（`eval-chiqui7-tile-ov256.json:723/1645/2458/3044`），ov448 = 90+174+108+32 = **404**（`eval-chiqui7-tile-ov448.json:696/1780/2868/3631`）。ov128 的 261（58+112+70+21，`run-full.log:4-7`）正确，故 §4 成本估计不受影响。
- **P3-3｜AC4 交付物所在 commit 未登记**：Task front matter `delivery_commit: 49253b09` 实为提案 commit；报告/Handoff/回填所在 docs 提交在 Task:75 与 Handoff:25 只写"（本次 docs 提交）"。建议回填 docs head（本轮 tip=76bf2a94）。
- **P3-4｜"唯一差异=成像口径"应限定为预处理/成像**（Q1-3）；`tile_calib.py:24`、`calib-report.md:92-98`、`ko-caliber-proposal.md:59-63`。
- **P3-5｜页级 NMS 步骤不可仅凭盘上产物复算**（Q2-4）：raw 未存 NMS 前框坐标（`tile_calib.py:300-303` 只落计数），建议后续实验落 pre-NMS 框以便复算。
- **P3-6｜治理登记缺口（owner=编排/集成）**：`doc/STATUS.md:14` 仍写"无 Active/无已释放待执行"，`doc/REBASELINE_PLAN.md:224` 仍写 T3"待释放"；本 Task 无 release 记录文件（对比 `verification/M2-AC5/release-6f79c040.md` 等先例），释放依据仅见 Task front matter `approval: user_ruling_2026-10-05_按推荐_T3释放`。因 `doc/STATUS.md` 在本 Task 禁止范围内，作者无法登记——集成前须由编排补 release 记录 + STATUS/PLAN 登记。
- **P3-7｜报告 §8 的"独立复核（非作者）= PASS"位于作者自己的交付物内**，未给复核者身份/落盘路径/证据 commit，易被后续读者误当作已完成的独立评审（真正的非作者评审是本轮）。建议改称"作者侧复核"或指向复核者报告；其"过程假差异如实登记"的诚实性应保留。
- **P3-8｜运行级声明未验证（声明性限制）**：本会话无 shell，`recompute_matrix.py` 复跑、`git diff --name-only`/`git log`、`git show <merge>:...grep d87389af`、外部引用（V2 worktree `eval_v2.py`/`v2b best.onnx`、R1 脚本）的**在盘一致性**均未运行级验证；`run-full.log` 是入库文件而非 shell 捕获流。AC5 我仅静态确认：`src/infrastructure/providers/detection_sfx.py:110-112` pin `d87389af…646` 逐字在位、`src/**` 无任何 tile 实现（grep `ko-tile-calib|tile_690x1024|TILE_OVERLAP|NEWMANGA_SFX_TILE` 零命中）、`.gitignore:13` `/training_data/` 覆盖中间产物。

**P4（可留待集成轮）**
- **P4-1｜"GT 框最高 676px"**：严格值 **675.8px**（pre-k08，y 14483.2–15159.0）；四舍五入可接受，建议写 675.8。
- **P4-2｜"15 文件"分解式不自洽**：Handoff:51-53 写"2 脚本+5 摘要/报告+7 raw+doc/tasks = 15"，但 `verification/M2-KO-TILE-CALIB` 下非 raw 产物实为 **6** 个（`eval-matrix.json`、`eval-matrix-ov256/448.json`、`preprocess-caliber-table.md`、`ko-caliber-proposal.md`、`calib-report.md`），加之 Handoff 与 Task 实为 17 路径。因无法运行 git，建议集成轮以实际 `git diff --name-only 9258afc0..<merge>` 复核并改写。
- **P4-3｜commit 号未见于交付链**：`preprocess-caliber-table.md:7`、`ko-caliber-proposal.md:89` 引 `tile_calib.py（1af31e4f+变体参数）`，而 Task:68-75/Handoff:17-25 的提交链无 `1af31e4f`。
- **P4-4｜环境/版本声明**（onnxruntime 1.30.0、venv、CPU EP）无法静态核验；`detection_sfx.py:426` 的 CPUExecutionProvider 与文献一致（代码层可证）。

**正向确认（供集成记录引用）**
- 报告 §8-① 与 §4 引用的**全部生产行号逐条核对无误**：`SFX_NMS_IOU=0.7`(:121)、`SFX_CLASS_ID=2`(:138)、CPU EP(:426)、sha 先验断言(:416-421)、`_letterbox`(:516)、`_sfx_boxes`(:535)、`_nms`(:592)、`_map_back`(:603)；`eval_v2.py` 的 `match_gt`(:68-97)、`IOU_MATCH`(:47)、`CONFS`(:46)、重指 pin(:179)、per-conf provider(:197-201)。
- v2b letterbox 确实加载 v2b 权重（`tile_calib.py:394-395` 在 letterbox 前重指 pin，`provider_factory` 内 `_build_engine` 断言 v2b sha；`:443-444` finally 恢复），不存在"用 chiqui7 出 v2b 数字"的混淆；chiqui7 侧 `:366-371` 在重指之前建 session，pin 原样。
- 变体 pre-k01 相位极端例可核：ov256 `sfx_after_page_nms=0`（`:2460`）→ 0/2；ov448 `=1`（`:3633`）→ 1/2；ov128 `=2` → 2/2，与报告 §3 表述一致。

## 逐 AC 结论

- **AC1**（chiqui7 两口径 4 页 56 框）：**PASS（数字全对、等价性成立）**，但"56/56 满召回 / P 0.8235"须按 P1-1 降级为同源复现——口径瓶颈结论改锚 `letterbox n_pred=0` 的 GT 无关事实。
- **AC2**（v2b 同实验）：**PASS**；letterbox 0/56×2、tile 35/56@0.5（P 0.3465，n_pred 101）/43/56@0.2 与盘上一致，"不入切换候选"裁定恰当且保守（GT 偏 chiqui7 只会低估 v2b）。
- **AC3**（口径建议固化 + 成本估计 + 零 src）：**PASS_WITH_CONDITIONS**；提案五条齐、成本 8.9s/页推导可核（71.6s/522 tile-passes≈0.137s/tile ✓），但需闭合 P1-1、P3-1、P3-2。
- **AC4**（报告+Handoff+Task 回填）：**PASS（有 P2）**；三文档齐且互相一致，但复现命令不可执行（P2-1）、docs head 未登记（P3-3）、文件数分解不自洽（P4-2）。
- **AC5**（零 src；产物 gitignored 或摘要入 Git）：**静态 PASS / 运行级未验证**；pin 逐字在位、src 无 tile 实现、`.gitignore` 覆盖 `/training_data/`；`git diff` 类断言因本会话无 shell 无法复核。

## 推荐下一步

1. **Owner（ZCode）返修（文档级，零 src，建议一次提交）**：按 P1-1 在 `calib-report.md`（§1 GT 行、§9）+`ko-caliber-proposal.md`（§3 五条，尤其第 1/5 条）+Handoff 增补"GT 同源性/循环性"限制段并改写"满召回/实测最优"表述；修 P2-1 命令（3 处）；修 P3-2 变体 tiles 数（304/404）；限定 P3-1 的"无切断"表述；回填 docs head（P3-3）；补 P3-5 证据缺口说明。修完提交 `doc/reviews/M2-KO-TILE-CALIB-<new-docs-head>-dsh-r2.md` 定点复审请求。
2. **编排（代行 Codex）集成**：集成轮落 `doc/reviews/M2-KO-TILE-CALIB-76bf2a94-dsh-r1.md`（本轮结论）+ 返修轮结论；merge 前完成 **P3-6 治理登记**（补 release 记录 + STATUS/PLAN 登记本 Task 的 T3 前置身份与 2026-10-05 用户裁决）；merge Gate 按 Handoff:115-118 执行 `git diff 9258afc0..<merge> -- src/ training_data/` 为空 + pin 在位 + `recompute_matrix.py` 8 格相等（这三项本轮无法运行级验证，必须由集成方复跑）。
3. **T3 采信前的裁决项（提请用户/Codex）**：本 Task 的 Gate 口径与 GT 同为 chiqui7-tile-ov128 产物，Gate 数字度量的是"采集口径一致性"而非"模型质量"。若 T3 要用 KO Gate 做模型取舍，建议**同轮补一片非 chiqui7 派生的 KO GT**（哪怕是少量人工核验框），否则 V2B 的 35/56 与 chiqui7 的 56/56 之差无法区分"模型差"与"GT 偏"。
4. **T4 材料补强（提案修订建议，非本 Task 阻断）**：把"冻结 ov128"的已知风险从"相位方差"升级为两条硬约束——①结构保证需 `overlap ≥ h_max`（本 GT h_max=675.8 → ≥676；ov128 仅保证 h≤128）；②页级合并阈值 0.5/sfx-only 在 T4 是新层，须与生产类无关 NMS 0.7 的作用域差异一并设计（`NEWMANGA_SFX_TILE_*` fail-fast 纪律），并保留 pre-NMS 框以便复算。
