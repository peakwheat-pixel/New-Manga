# M2-SFX-ANNOTATE-R3 DSH r1 审查报告（2026-10-05）

> 审查对象：tip 65a6e038；Verdict=approved_with_conditions（0×P0/P1、2×P2、5×P3、5×P4）。
> stdout 全文转录（143 行完整）。C1（BJ22 落框）/C2（correct 先例更正）已由集成轮闭合。

## 审查前置说明（环境限制，先声明）

本 worktree 的 `pwsh` 无法启动（两次尝试均沙箱级失败：`SetNamedSecurityInfoW failed (Win32 5): grantWrite(...M2-SFX-ANNOTATE-R3-zcode)`），**本轮无任何命令执行能力**。因此：

- **已独立核对（静态、直接读盘）**：所有 JSON/PNG/脚本/文档的逐字段、逐行、逐数值对账（详下）。
- **未验证（运行级）**：`git diff 9258afc0 HEAD -- src/` 空 diff、`git diff --numstat …cases.json` 的 `900/0`、`ultralytics check_det_dataset` 复跑、全部 sha256 实测。这些只做了"产物自洽 + 与我可读盘的事实一致"层面核对，不作运行级背书。

---

## Verdict

**approved_with_conditions**（0×P0、0×P1、2×P2、5×P3、5×P4）

判据：AC1–AC4 的验收判据在静态可核对范围内**全部成立且数字逐项闭合**（110→122 纯追加、22 单元闭环、94/912 对账、考卷 5 框逐位不动均有盘上直接证据）；无伪造、无越范围、口径差异如实登记。阻断级问题为零。两个 P2 均为"必须做决定的已知缺口"，不推翻交付。

**条件 C1（T3 Gate 消费 train-v3 之前必须处置）**：`pre-bj22` 的 `R2-BJ22-B01`（仲裁终裁 `correct`）坐标未落，当前以原候选宽框进入训练 GT（见 P2-1）。
**条件 C2（集成回填时）**：correct 先例引用更正为 R1（R2 本轮 correct=0），并在报告 §5.2 明写"BJ 正集有效框数"（见 P3-2/P2-1）。

---

## 重点问题 Q1/Q2/Q3 裁定

### Q1【BJ 正集扩容质量】= 基本成立，1 框有实质缺陷（P2-1）、1 框证据偏弱（P3-1）

我对 6 个可读预览图做了**独立实看**（BJ16-B04/05/06、BJ28、BJ29，以及后文 BJ26/BJ27）：

| 单元 | conf | 我实看结论 | 与双 AI 判定 |
|---|---|---|---|
| R2-BJ16-B04 | 0.1074 | 白描粗笔「コッ」+双短顿点，网点底，无气泡 → **确认扎实** | 一致（confirm） |
| R2-BJ16-B06 | 0.0351 | 斜置粗毛笔「十/ナ」形＋双竖点，无气泡 → **可信** | 一致（confirm） |
| R2-BJ16-B05 | 0.0443 | 71×205 窄框内两条平行收锋竖笔画＋2 小短块 → **最弱**：字形可读性不足，agy 的理由主要靠"与同页拟声呼应"的页级联想；残留"大字形片段/速度线"误升风险 | 一致（confirm），但证据强度低于另两框 |
| R3-BJ28-B00 | 0.9108 | 手写风「ヒッ…」，白底无气泡 → **确认扎实** | 一致（confirm） |
| R3-BJ29-B00 | 0.6038 | 椭圆描边内重度艺术化粗毛笔笔画 → **可信**（非规整台词字） | 一致（confirm） |
| R3-BJ26/BJ27 | 0.0217/0.0167 | BJ26 圆顶物体轮廓（delete 正确）；BJ27 我未取得该原页上下文，但仲裁 rationale 给出"几何方块花纹领带逐块吻合"的可核查论证，且原页为病房对话页（无效果音叙事动机）→ **delete 裁定可信** | 与终裁一致 |

**BJ16 回填 3 框的硬事实链完整**：units.json 的 conf/xyxy 与 R2 worksheet `ai_conf`/`xyxy` 逐值一致（0.1074/0.0443/0.0351；坐标逐位相同）；manifest.r3 中 B04/05/06 以 `added_units` 留痕并保留 `backfill_note`；导出 label 为"原 3 行 + 新 3 行"（`labels/train/pre-bj16.txt` 6 行，前 3 行与 R2 出厂同值）。**BJ28/29 判定链完整**（units→共识 rationale→manifest `stage3r3.added`→label 1 行）。

**但 BJ22 有实质缺陷**：见 P2-1 —— 仲裁自己判定"框需收缩"，交付却把**已知错框**作为新正样本 GT 导出，而该框此前只在 pseudo 底册（不入训练），是**本轮新注入**的错误标签，不是沿袭旧噪声。

### Q2【负证据页与 miss 通道】= 与 R1/R2 口径**一致**；但 ask 摘要的前提描述有误，且 miss 通道"开放未执行"（P2-2）

**先纠正前提**：ask 摘要写"零框 pseudo 入 train 作背景"——**盘上事实不是这样，也没有背景污染风险**：

1. `stage2_finalize_r3.py:514` 只取 `annotation_status == "complete"` 作为正集：`pos = [m for m in r3_samples if m["annotation_status"] == "complete"]`；
2. 数字自证：train 904 = real 22 + partial 140 + pseudo 418 + synthetic 324，而 own-manga 恰好 558 = partial 140 + pseudo 418 —— 故 train 里的 418 pseudo **全部是 own-manga**，64 个 BJ pseudo（含 BJ19/20/21、BJ26/27/30/31、BJ32-37）**一个都没进 train-v3**；
3. 直接核验：`manifest.train-v3.json` 中 densho810 的 sample_id 仅 `pre-bj16/17/18/22/23/24/28/29`（8 个），无 `pre-bj19/20/21/25/26/27/30~37`；
4. `912 = 30 complete + 324 synthetic + 558 own`（976 − 64 = 912），与 R2 final `351 = 27 complete + 324 synthetic` 的"pseudo 一律不入训练集"口径**同源**（R2 报告明写"回放页保持 pseudo 不入训练集"）。

**留痕完整性（BJ19/20/21 全 delete 关闭）**：manifest.r3 中 pre-bj19/20/21 为 `boxes: []`、`boxes_meta: []`、`stage3r3.action=kept_pseudo_zero_box_negative_evidence`，且 `excluded_delete_units` 逐条带 unit_id+verdict+reviewer+双 AI rationale 全文（我已逐条比对与 consensus.json 文本一致）；BJ26/27/30/31 同构（`excluded_delete_boxes`）；BJ32-37 为 `kept_pseudo_zero_candidates_negative_evidence`。**RL 判定链 stage2r2 未被覆盖**（原 stage2r2 块保留）。

**缺口（P2-2）**：BJ32-37 是 AC1 目检**明确确认含毛笔竖排 SFX** 的页，因 chiqui7 零候选 → 无单元 → **没有任何 reviewer 走过 `miss` 补画**。这 6 页占本轮新入池 12 页的一半，本轮实际监督产出只有 4 框/12 页。合同 AC2 字面只要求"全部检出候选入审"，故非违约；但 judge_std 已定义 `miss`＝页级漏标补记坐标，报告 §9-2 把通道写成"开放"，实际是"已识别、未执行"。

### Q3【底册口径登记】= Owner 的语义判断**正确且必要**，登记充分

盘上事实（我直接读了两份 R2 manifest）：

- `R2 final/manifest.r2.json`：`kind=sfx-data-infra/manifest@1`、`sample_count=351`（R2 报告复算：27 complete + 324 synthetic）；
- `R2 preannotate/manifest.r2.json`：82 样本，且 **pre-bj19(19988 行)/pre-bj22(20300)/pre-bj25(20584)** 只存在于这一份里。

遗留 16 单元的判定更新对象恰恰是 pre-bj19/20/21/22 的 pseudo 页 —— **在 351 底册中根本不存在**。若按 ask 字面用 final/351，本轮 16 单元中 9 个（BJ19×3/BJ20×2/BJ21×2/BJ22×2）**无处落地**，判定链直接断。所以"按 preannotate 82 底册执行"不是妥协而是唯一语义正确方案。

登记充分性：`stage-r3-summary.json.manifest_merge.base_manifest_caliber_note` + 报告 §0 + §10 honest_notes + Task 第 79 行 + Handoff 风险 4 四处一致，且明确写出"final 实为 351（27 complete+324 synthetic）、82 底册本体=preannotate/manifest.r2.json（27 complete+55 pseudo）"。**判定：可接受，且建议后续 ask 直接写文件路径而非"final manifest"这类易漂的别名。**

附带加分：从 82 分支重推的风险已用**强断言闭合**——`_export_stats.json.label_crosscheck_vs_r2.checked=351 / mismatch=[]`（R2 出厂 351 label 逐字节，pre-bj16 走前缀特判），我抽样复核 `labels/challenge/pre-bj17.txt`、`train/pre-bj18.txt` 与 R2 出厂**逐字节相同**。

---

## 发现清单

### P0（阻断）
无。

### P1（严重）
无。

### P2-1【`pre-bj22` 已知错框作为新正样本 GT 导出】（条件 C1）
- 位置：`manifest.r3.json:20444-20467`（`revision.needs_fix=true`、`fix_hint_xyxy_page=[1840,60,2100,570]`、`coordinates_changed=false`）；`dataset/labels/train/pre-bj22.txt:2`。
- 事实：仲裁判定"是 SFX 但候选宽框只碰到椭圆左缘，需收缩重框至 ≈[1840,60,2100,570]"。导出 GT 仍是 `[1052.8,0.3,1863.4,559.0]`（810.6×558.7），与真实 SFX 主体（x≈1840-2100）**宽向交集仅约 23px**，框内主体是手术室场景（医护+器械车）。
- 影响：`pre-bj22` 此前是 pseudo（V2 明确断言其不得入训练 manifest），本轮升 complete 后该框被写入训练 label —— 属**本轮新注入**的域内错标签；报告 §5.2/§6.1 把它计入"BJ 正集 18 框"，会让 T3 Gate 把无效框当有效正样本归因。
- 处置建议（任选，二选一必须留痕）：①**推荐**：按 `fix_hint` 落框（或撤该框），重跑 `--step all`，同步 4 份文档/摘要 + 指纹（train 框数不变 2311，正集框数 18→18 或 →17）；②接受现状：在报告 §5.2/§6 明写"BJ 正集有效框 = 17（BJ22-B01 待 revision）"，并列入 T3 Gate 前置。成本极低（单框、已知坐标），不建议长期挂 needs_fix。

### P2-2【BJ32-37 miss 补画通道"开放未执行"，本轮 6/12 新页零监督产出】（条件 C2/立项）
- 位置：`manifest.r3.json:21105/21137/21169/21201/21233/21265`（6 页 `kept_pseudo_zero_candidates_negative_evidence`，note 写"SFX 标注留给判定轮 miss 补画通道"）；报告 §0/§9-2/§10。
- 事实：`worksheet-bj-new.json.zero_box_pages` 6 页（BJ32-37）**未生成任何 unit**，`judgments/batch-list/*` 只有 bj_new 6 + leftover 16 = 22，**无一个 miss 单元**；取缔标准里的 `miss` 语义从未被使用。
- 影响：AC1 用"毛笔形态目检"专门挑出的最强形态页（如 vol05_p0026 巨大婴儿哭声竖排、vol03_p0117「ハィィィ」），最终对训练**零贡献**；合同背景目标"扩到几十框量级"仅达 18 框（已如实登记）。
- 建议：要么本轮返修增补 miss 单元（走同一双 AI+仲裁链），要么在 T3 释放时立刻立独立任务（"BJ32-37 miss 补画"），并把报告措辞从"通道开放"改为"已识别未执行"。这是 T3 Gate 前**性价比最高的补数据动作**。

### P3-1【BJ16-B05 回填证据强度低于同批另两框】
- 位置：`units.json:172-189`（conf 0.0443、71.4×205.4）；`consensus.json:58-68`。
- agy rationale 以"与同页拟声呼应"支撑，codex 以"非均匀速度线"排除；我实看该裁切为两条平行收锋竖笔画＋2 短块，字形可读性不足。建议 T3 前对这 1 框做用户抽检，或在 `boxes_meta` 加 `needs_spot_check`（conf/rationale 已可追溯，故不阻断）。

### P3-2【correct 先例引用错误：应为 R1 而非 R2】
- `stage2_finalize_r3.py:68/279`、报告 §0/§9-3、Handoff 风险 3 均写"沿 R2 stage2r2 correct 口径/语义"。
- 事实：**R2 本轮 correct=0**（R2 报告 §4.2：codex 11/0/8、agy 12/0/7，"无 correct 对"；R2 全量 judgments 内无 `correct` 字样）。真实先例是 **R1 stage2 的 5 个 correct**（R1 报告："correct 5 框坐标未动，needs_fix=true 留痕，补框属人工扩标轮"）。
- 影响：口径溯源不准；且正是这条"沿 R2 口径"掩盖了 P2-1（R2 从未验证过 correct 框进训练集的效果）。更正后请在 T3 材料中显式声明该先例的已知代价。

### P3-3【治理登记滞后：Plan/STATUS 未反映本 Task】
- `doc/REBASELINE_PLAN.md` 任务表无 M2-SFX-ANNOTATE-R3 行，且 line 224 仍写"T3 评测 Gate G1-G8 · 待释放（BJ 深度扩标后）"；`doc/STATUS.md:14` 仍写"**无 Active / 无已释放待执行（2026-10-05）**"，并把"T3 释放"列为待用户裁决。
- 本 Task 凭 `doc/tasks/M2-SFX-ANNOTATE-R3.md:7 approval: user_ruling_2026-10-05_按推荐_T3释放` 运行；`doc/STATUS.md` 与 Plan 在 Task 禁止范围内（Owner 不可改），故**必须由集成会话/Codex 在 merge 时回填**，否则授权链无法回溯。另建议把该 user ruling 落一份可检索证据（STATUS 或 checkpoint），目前仓库内仅此一行 frontmatter。

### P3-4【噪声分层不对称未显式登记】
- densho810 的 64 个 pseudo **不入 train**；own-manga 的 418 pseudo **带模型输出框入 train 当 GT**（`_export_stats`/报告 §5.3 数字自证）。两者 `annotation_status` 同名却处置相反（V2 边界沿袭，已分别披露），但报告未把这一**不对称本身**写进 §6 T3 归因材料。建议补一句：T3 归因时 own-manga 418 框是"自蒸馏"性质 GT，不可与 BJ 正集同权。

### P3-5【目检 tier 内顺序来源未登记】
- 报告 §3/selection JSON 记录了 tier=strong/medium/weak 与理由，但 rank7-12 的**组内先后**（如 weak 组 p0140 先于 p0103）来自目检结论顺序，而非 `sha256(seed:source_id)` 机械序（kept=0 组 38 页在机械序里本有确定次序）。合同允许"目检优先"，登记也完整，但建议一句话说明"tier 内顺序=目检结论顺序，无量级依据"，避免被读成机械决胜。

### P4-1【manifest.r3 内 `occluded` 键不一致】
- `pre-bj16` 原 3 框带 `"occluded": false`，R3 回填的 B04/05/06 **无该键**（`_unit_box()` 未写；而 correct 分支第 274 行显式补键）。schema 侧合法（`schema.py:40` 默认 False、`:137` `b.get("occluded", False)`、`:196` required 仅 `["polygon","cls"]`），功能无影响，属产物美观/一致性瑕疵。

### P4-2【"无 conf 门槛"应写明引擎下限 0.01】
- `conf_scan_diag.py:121` `for i in np.where(confs >= 0.01)[0]`：候选实际是 conf≥0.01 的结果；`scan-bj-new.json.conf_floor=0.01` 与 worksheet 的 `conf_gate: null` 并存易被读成"0 门槛"。22 单元与 BJ32-37 零候选结论不受影响，但口径表述应收紧为"无人工门槛，仅引擎下限 0.01"。

### P4-3【cases.json BJ26-37 的 registration_note 模板不贴合 rank1-6】
- `cases.json:7191`（及 BJ27-37 同文）写"kept=0 tie group visually adjudicated…"，而 BJ26-31 是 `density kept>=1` 机械直选（其 `feature_notes:7189` 已正确）。同一 note 覆盖两类 basis，逐条阅读会误读。建议按 `selection_basis` 分叉模板。

### P4-4【label 比对措辞含混】
- 报告 §5.4/Handoff 写"R2 出厂 351 label 逐字节交叉比对 0 失配（pre-bj16 特判…）"。实际为 `checked=351 / mismatch=[] / bj16_suffix_checked=true`，即 **350 项逐字节 + 1 项前缀特判**。建议改为该表述以免被质疑"351 全逐字节"含特判矛盾。

### P4-5【ask 摘要的双审数字与盘上不符（非交付缺陷）】
- 本轮 ask"交付声称"写 codex `confirm 6/delete 16`、agy `confirm 6/correct 2/delete 14`；盘上三处（codex/batch-1+2、agy/batch-0+1）重算为 **codex 7/0/15、agy 8/0/14**，与 Task:73、报告 §4.2、Handoff、summary 完全一致；我已 grep 全仓 `*.md/*.json`，**不存在**支持摘要数字的文件。以盘上为准，提示 ask 摘要注意更正（我未发现被污染的登记源）。

### P4-6【跨 worktree 绝对路径绑定】
- `manifest.r3.json` 中 R2 图案指向 `…M2-SFX-ANNOTATE-R2-zcode…`，previews 同样跨树；`dataset.yaml:7` 的 `path` 绑定本 worktree。已登记为 Handoff 风险 6，但 T3 从别处消费时需重写前缀，建议在摘要给出 path 重写规则。

---

## 逐 AC 结论

- **AC1（选页入池/纯追加）**：**PASS**。候选池 44 页=盘上实存 54（vol01 18/vol03 18/vol05 18）− 已入池 10，且 vol01 16/vol03 15/vol05 13 与合同一致；`density-scan-pool.json` 恰 44 页、kept=1 六页/kept=0 38 页与 `material_select_r3.py:203` 断言一致；kept=1 六页与 R2 `bj_runner_up_pool` 前 6 项（density=1）逐项相同；R3 剩余池 32 = R2 池 44 − 本 12，逐项同序。cases.json 122 条=110（与 R2 110 条 case_id 行号/顺序完全对齐，仅 BJ25 收尾 `}`→`},`）+ BJ26-37，BJ26 实为 38 键、`page_sha256` 与 selection JSON 逐页一致、12 张 PNG 已在盘。
- **AC2（预标注+双 AI 扩审全量覆盖）**：**PASS**。16 遗留单元 = R2 worksheet `ai_conf<0.2` 精确集合（BJ16×4/BJ17×2/BJ18×1/BJ19×3/BJ20×2/BJ21×2/BJ22×2），id/conf/xyxy 逐值一致；6 新页单元 conf/xyxy 与 scan-bj-new 一致；22 单元=6+16；从 batch 文件重算 **codex 7/0/15、agy 8/0/14**；共识 19（confirm6+delete13）与 3 分歧**算术闭合**（7−1=6、15−2=13；（15−2)+(13)=? 逐项校验均成立）；终裁 confirm6+correct1+delete15；`build_r3_judgments.py:95/121/163` 三重覆盖断言；arbiter rationale 逐图实看留痕、理由具体可核。
- **AC3（manifest.r3+trian-v3 重切）**：**PASS（带 P2-1 条件）**。manifest.r3 94=82+12、complete 30/pseudo 64、BJ complete 8 页；`stage3r3` action census（75+4+2+7+6=94）；train-v3 `sample_count=912`、904/2311+4/53+2/5+2/5、fingerprint `d57353b1…28de` 三处一致、lock/pinned 8 组/challenge_members=[pre-bj17,pre-bj18] 齐备；`labels/challenge/pre-bj17.txt`、`pre-bj18.txt` 与 R2 出厂**逐字节相同**（考卷 5 框不动的直接证据）；`dataset.yaml` names={0:bubble,1:panel,2:sfx,3:text}；R2 351 label `checked=351/mismatch=[]`、`stem_mismatch_total=0`、sha 抽验 22 张。**唯一实质扣分＝P2-1**。
- **AC4（报告+Handoff+Task 回填+T3 材料）**：**PASS**。三文档齐且互洽；T3 提案仅提案不裁决，且主动登记"18 框未达字面几十"；§0/§9/§10 honest_notes 与 summary 全量一致；§2.2 十三项复算记录与盘上可核项逐项吻合。扣分项为 P3-2 先例引用与 P4-4 措辞。
- **AC5（零 src/数据 gitignored/Git 只进摘要与 cases.json）**：**静态 PASS、运行级未验证**。`detection_sfx.py` 与 R2 同文件 12 处命中**行号与文本完全一致**，pin 三常量（`7f5f5c04…`/`d87389af…`/0.5）与报告逐值相符；`.gitignore:13 /training_data/` 覆盖数据树；Git 内容面（脚本 5 个 + 摘要 + cases.json 追加）与报告所述一致。**`git diff` 空 diff、numstat `900/0`、ultralytics 复跑均因无 shell 未独立复算**（其中 cases.json 纯追加我已用逐行对齐的更强方式独立确认）。

---

## 推荐下一步

1. **集成会话/Codex（代行）**：以 `approved_with_conditions` 处理，先闭合 **C2**（correct 先例改 R1、报告补"有效正样本框数"表述）→ 回填 `doc/tasks/M2-SFX-ANNOTATE-R3.md` 的 `review_events` 与 `doc/reviews/M2-SFX-ANNOTATE-R3-*.md` → 视 **C1** 选择"落框重跑"或"接受并写 Gate 前置" → 再 merge，并同步回填 `doc/STATUS.md` 与 `doc/REBASELINE_PLAN.md`（P3-3，Owner 不可改）。
2. **Owner（ZCode，若选 C1①）**：`R2-BJ22-B01` 按 `fix_hint=[1840,60,2100,570]` 落框或撤框 → 重跑 `stage2_finalize_r3.py --step all` → 同步报告/摘要/Task/Handoff 的指纹与 Δ 数字（预期 train 仍 904/2311，正集 18 或 17）。
3. **T3 释放时立独立任务**：`M2-SFX-ANNOTATE-R3-MISS`（BJ32-37 六页 miss 补画，走同一 codex+agy+仲裁链），这是把 BJ 正集从 18 框推向"几十框量级"最快的一步；同时把 own-manga 418 自蒸馏框的分层影响写进 Gate 归因方案（P3-4）。

**无需下一步操作的部分**：Q3 口径判断与登记（可接受，无需返修）；AC1 选页链与 cases.json 纯追加（已验证，无需返修）。
