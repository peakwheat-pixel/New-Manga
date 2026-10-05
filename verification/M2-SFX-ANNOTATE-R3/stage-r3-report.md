# M2-SFX-ANNOTATE-R3 交付报告（AC1 选页入池 + AC2 预标注/双 AI 交叉审核 + AC3 manifest.r3/train-v3 重建 + AC4 报告）

- Owner：ZCode（本工作区）；Task：[doc/tasks/M2-SFX-ANNOTATE-R3.md](../../doc/tasks/M2-SFX-ANNOTATE-R3.md)
- 基线：Task frontmatter `base_commit=9258afc0`；分支 `agent/zcode/M2-SFX-ANNOTATE-R3` 自 main `7dd5402d` 分出。
  交付链：material @`579af8a5` → prep @`d1a6da43` → 判定并入+重切 @`85435bb9`（本文档收尾轮 docs 提交在其后）。
- 工具：`experiments/M2-SFX-ANNOTATE-R3/`（material_select_r3 / scan_pool_density_r3 / stage1_preannotate_bj_r3 /
  build_r3_judgments / stage2_finalize_r3 / make_contact_sheet，三脚本 @579af8a5+两脚本 @d1a6da43）。
- 生成：2026-10-05；**本文档收尾轮（docs 轮）撰写**——口径沿 R2 stage-r2-report.md 先例：全部统计数字由文档收尾轮
  从盘上产物复算（命令与输出见 §2.2），不转抄交付轮消息文本。**措辞澄清（沿 R2 先例）**：「复算」均指同 workflow
  内文档收尾 agent 的复算，属 Owner 自核、非独立第三方 Review；独立 Review 由 DeepSeek Harness（非作者）另行执行
  （Task status=in_review，待审）。
- 判定输入：`training_data/sfx-v1/annotate-r3/judgments/{units,consensus,divergence}.json` + codex/agy/arbiter
  batch 文件（codex+agy 双评审+第三方仲裁，由编排会话按用户全权授权组织；本 Task 代理只消费判定、不生产判定）。
- 数据树：`training_data/sfx-v1/annotate-r3/` + `training_data/sfx-v1/train-v3/`（repo gitignored；R2/R1 树在
  本 worktree 外只读；own-manga 入册包在 task-envs 外部树只读）。本报告内数据路径均相对 `training_data/sfx-v1/` 根。
- 复核轮：交付后复核 **=PASS**（五项独立重算，材料随收尾输入提供，§8 摘录；复核报告本体未落本目录，
  正式非作者 Review 待 DeepSeek Harness）。

## 0. 模式与边界（先读）

**GT 性质=ai-consensus，沿 R1 §0 口径不变**：本轮判定继续由编排组织的 codex+agy 双评审+分歧第三方仲裁产出，
**`human_review=false` 全量保真**（`stage2_finalize_r3.py` 产物与 `judgments/consensus.json` 留痕），provenance 写
`provenance.stage3r3`（R2 底册 `provenance.stage2r2` 判定链不覆盖写），**不谎称人工**。R1 的 ai-consensus 一致性
上限警示对 R3 新增 confirm/correct 框同样适用：T3 Gate 归因时「标注质量」与「模型质量」两层误差仍须分开，
用户抽检/翻案通道仍是唯一升级为人工背书的路径。

**本轮判定范围（22 单元）**：`judgments/units.json` counts=`{bj_new: 6, bj_lowconf_leftover: 16}`。
6=BJ26-37 新页整页 letterbox 预标注（**无 conf 门槛全检出入审**，R2 教训=BJ 候选 conf 天然低；BJ32-37 零候选
→ 页级 miss 补画通道留 pseudo 负证据）；16=R2 worksheet 遗留 conf<0.2 层（BJ16×4/BJ17×2/BJ18×1/BJ19×3/
BJ20×2/BJ21×2/BJ22×2）。conf 分层按 R3 整页 letterbox 重扫口径登记（prep-summary）：
`conf_lt_0.2=19 / conf_ge_0.5=2 / conf_0.2_to_0.5=1`。

**覆盖完备性**：consensus(19) ∪ divergence(3) = units(22)，uncovered=0（§4.2 复算）；分歧 3 单元全部经编排
逐图实看终裁，残留=0。

**底册口径差异如实登记**：ask 字面「R2 final manifest 82 样本」与文件事实不符——`R2 final/manifest.r2.json`
实为 351 样本（27 complete+324 synthetic）；82 样本底册本体=`R2 preannotate/manifest.r2.json`（27 complete+
55 pseudo）。遗留 16 单元判定更新对象 pre-bj19/20/21/22 pseudo 页只在该 82 底册，且 R2 stage2r2 语义的底册
正是此文件——按语义正确方案执行（82 底册只读并入），已在 `stage-r3-summary.json` 的
`manifest_merge.base_manifest_caliber_note` 如实登记。

## 1. 交付概览

| AC | 内容 | 状态 | 证据 |
|---|---|---|---|
| AC1 选页入池 | 44 页候选池 chiqui7 密度扫描（kept=1 六页 rank1-6 无并列直选 + kept=0 38 页全并列 AI 目检毛笔竖排形态二次决胜选 6，REF=BJ16/17/18/23/24 校准）→ BJ26-BJ37 cases.json **纯追加** | **PASS** | `test_assets/comic_golden_suite/manifests/cases.json`（122 条，+900/−0）；`selection/material-selection-r3.json`；`selection/inspect-batch-1..5.png`（§3） |
| AC2 预标注+扩审 | BJ26-37 新页整页 letterbox 预标注（无 conf 门槛）6 单元 + R2 遗留 conf<0.2 16 单元 → 22 单元双 AI 交叉审核（批次 [6,16] ≤20/批） | **PASS（判定全量覆盖 uncovered=0，仲裁终裁 3，残留=0）** | `judgments/{units,consensus,divergence}.json` + `judgments/{codex,agy,arbiter}/batch-*.json`（§4） |
| AC3 manifest v3+重切 | 判定并入 manifest.r3.json（real 94，T1a schema 0 错误）→ train-v3 重建 912 全量（考卷 5 框不动、组隔离 0 违例、own-manga 558+合成 324 并入）；BJ 正集对照表回填 | **PASS** | `annotate-r3/preannotate/manifest.r3.json`；`train-v3/manifest.train-v3.json`；指纹 `d57353b1…28de`（§5） |
| AC4 报告+Handoff+Task 回填 | 本报告 + Handoff + Task 回填 + T3 材料更新（§6，仅提案不裁决） | **PASS（本次 docs 提交）** | `verification/M2-SFX-ANNOTATE-R3/stage-r3-report.md`；`doc/handoffs/M2-SFX-ANNOTATE-R3-zcode-20261005.md` |
| AC5 零 src | 零 src 修改；数据本体 gitignored；Git 只进摘要与 cases.json 追加 | **PASS** | `git diff 9258afc0 HEAD -- src/` 输出 0 字节（§7） |

## 2. 执行记录

### 2.1 交付轮命令（Owner，产物在盘 + `stage-r3-summary.json` generated_at=2026-10-05T02:46:59Z）

```text
python experiments/M2-SFX-ANNOTATE-R3/scan_pool_density_r3.py     # 44 页候选池 chiqui7 密度扫描（seed=20261004）
python experiments/M2-SFX-ANNOTATE-R3/material_select_r3.py       # rank1-6 密度直选 + rank7-12 目检决胜 → cases.json BJ26-37
python experiments/M2-SFX-ANNOTATE-R3/stage1_preannotate_bj_r3.py # BJ26-37 整页 letterbox 预标注（无 conf 门槛）+ 遗留 16 并入 → units+批次
# 双 AI 交叉审核：codex/agy 逐批判定（judgments/codex|agy/）→ build_r3_judgments.py 比对
python experiments/M2-SFX-ANNOTATE-R3/build_r3_judgments.py       # 共识 19 + 分歧 3 → 编排逐图实看终裁 → arbiter/batch-1.json
python experiments/M2-SFX-ANNOTATE-R3/stage2_finalize_r3.py --step all  # 判定并入 manifest.r3 + train-v3 重建 + summary
```

### 2.2 本文档收尾轮复算记录（独立执行，非转抄）

| # | 命令/步骤 | 输出 |
|---|---|---|
| 1 | python 统计 `judgments/codex/{batch-1,batch-2}.json` verdict 分布 | codex n=22 `{delete:15, confirm:7}`（correct=0） |
| 2 | python 统计 `judgments/agy/{batch-0,batch-1}.json` verdict 分布 | agy n=22 `{delete:14, confirm:8}`（correct=0） |
| 3 | python 读 `judgments/units.json` / `consensus.json` / `divergence.json` | units 22（bj_new 6+bj_lowconf_leftover 16）；consensus 19（confirm6+delete13）；divergence 3（§4.3） |
| 4 | python 读 `annotate-r3/preannotate/manifest.r3.json` | 94 样本；annotation_status complete=30/pseudo=64；BJ complete 8 页=pre-bj16/17/18/22/23/24/28/29 |
| 5 | python 读 `train-v3/manifest.train-v3.json` + dataset images 目录计数 | 912 样本：train 904/2311 框、val 4/53、test 2/5、challenge 2/5；lock.seed=20261004、fingerprint=`d57353b1db…28de`；images 904/4/2/2 |
| 6 | T1a schema：`SampleRecord.from_dict().validate()` 全量（sys.path 指向 `experiments/M2-SFX-DATA-INFRA`） | manifest.r3 94 样本 0 错误；manifest.train-v3 912 样本 0 错误 |
| 7 | python 深度对比本 worktree 与 R2 worktree 的 cases.json | R3 122 条 vs R2 110 条；**前 110 条逐条深度等值=True**；顶层元数据零差异 |
| 8 | `git diff --numstat 579af8a5~1 579af8a5 -- test_assets/comic_golden_suite/manifests/cases.json` | `900  0`（纯追加） |
| 9 | `git diff 9258afc0 HEAD -- src/ \| wc -c` | `0`（零 src） |
| 10 | `git diff --no-index` 本 worktree vs R2 worktree 的 `src/infrastructure/providers/detection_sfx.py` | 逐字节一致（exit=0）；pin：`SFX_HF_REVISION="7f5f5c04…"`（detection_sfx.py:108）、`SFX_WEIGHTS_SHA256="d87389af…"`（detection_sfx.py:110-112）、`SFX_CONF_THRESHOLD=0.5`（detection_sfx.py:118） |
| 11 | grep `SEED_DEFAULT` | `SEED_DEFAULT = 20261004`（experiments/M2-SFX-DATA-INFRA/sfx_data_infra/splits.py:30）= train-v3 lock.seed |
| 12 | python sha256 对盘 `stage-r3-summary.json` artifacts 4 件 | manifest.r3.json / manifest.train-v3.json / dataset.yaml / _export_stats.json 全 MATCH |
| 13 | `git status --short`（worktree） | 干净（docs 提交前） |

未运行项：ultralytics `check_det_dataset` 扫描冒烟（GPU venv 在 task-envs 外部树，收尾轮只读纪律下未执行；
出厂登记 `_export_stats.json` PASS，本收尾轮以同维度 yaml 双通道+目录计数（#5）替代覆盖，见 §9-1）；
双 AI 判定推理与仲裁实看（Owner 判定轮已执行、判定链留痕，收尾轮只复算其产物）。

## 3. AC1 选页入池（BJ26-BJ37）

- **候选池**：44 页=R2 素材根 54 张渲染页 − BJ16-25 已入池 10 张；与 R2 `material-selection.json`
  `bj_runner_up_pool` 逐项一致（`material-selection-r3.json.candidate_pool`）。
- **密度分布极稀（chiqui7 BJ 盲区再现）**：kept=1 仅 6 页、kept=0 达 38 页（`density_distribution`）。
  rank1-6（vol01_p0132/vol05_p0039/vol01_p0198/vol03_p0152/vol05_p0014/vol03_p0163）density=1 且**无并列直选**
  （`selection_basis=density_kept_ge_1_no_tie`）；kept=0 组 38 页全并列 → **AI 目检毛笔竖排形态二次决胜选 6**
  （rank7-12，`visual_tiebreak_tier=strong`；contact sheet 分批 5 张 `selection/inspect-batch-*.png`+原图复核，
  REF=BJ16/17/18/23/24 五页校准；seed=20261004 决胜口径沿 R1/R2）。例证：rank7 vol05_p0026 彩色扉页巨大
  「あぎゃぁぁぁぁ＋ぉぉぉ」毛笔书法竖排+尖刺冲击框（全池最强毛笔形态，chiqui7 kept=0 完全盲区的典型例证）。
- **cases.json 纯追加**：+900/−0，BJ26-BJ37 共 12 条（case_id 连续、pixel_size 字段沿 BJ16-25 先例、
  page_sha256 逐页）；既有 110 条与前 110 条深度等值（本收尾轮 #7 复算 True）+顶层元数据零差异。
  剩余 32 张留池（后续轮免重扫描）。
- git 提交 @`579af8a5`（material 三脚本+cases.json 追加）。

## 4. AC2 预标注+双 AI 交叉审核

### 4.1 判定单元构成（22 单元，批次 [6,16] ≤20/批）

- `bj_new` 6：BJ26-31 各 1 候选（BJ32-37 六页 chiqui7 零候选 → 不产生单元，页级保持 pseudo 零框负证据，
  miss 补画通道，§9-2）。批次文件 `judgments/batch-list/batch-1.json`（6 单元）。
- `bj_lowconf_leftover` 16：R2 worksheet 遗留 conf<0.2 层。批次文件 `judgments/batch-list/batch-2.json`（16 单元）。
- 判定标准沿 R2 内嵌 judge_std（`prep-summary.json.judge_std`）：confirm/correct/delete/miss 四值 +
  BJ 主攻形态=毛笔/书法竖排效果音说明 + 负例清单 + `human_review=false` 保真声明。

### 4.2 双审统计与覆盖完备性（收尾轮复算 #1-#3）

| 评审 | 单元 | confirm | correct | delete | 批次文件 |
|---|---|---|---|---|---|
| codex | 22 | 7 | 0 | 15 | `judgments/codex/batch-1.json`+`batch-2.json` |
| agy | 22 | 8 | 0 | 14 | `judgments/agy/batch-0.json`+`batch-1.json` |

- 共识 19（confirm 6+delete 13，双方 rationale 全文保留于 `consensus.json`）∪ 分歧 3（`divergence.json`）
  = units 22，**uncovered=0**；批次清单 6+16=22 对账一致；**consensus ∩ divergence = ∅，仲裁无多余单元**。
- 终判分布：**confirm 6 + correct 1 + delete 15 = 22**（correct 与仲裁 delete 2 均来自分歧终裁；
  final 分布与 `stage-r3-summary.json.r3_judgments.final_verdict_dist` 一致）。
- 登记注记：双审 ask 中 agy 批次文件写作 batch-0/batch-1、codex 写作 batch-1/batch-2（codex batch-1.json
  note 已自述此差异），两 AI 批次文件名错位不影响单元覆盖断言（22=22）。

### 4.3 分歧 3 单元与仲裁终裁（编排逐图实看，rationale 全文 `judgments/arbiter/batch-1.json`）

| 单元 | codex | agy | 仲裁终裁 | 依据（commit 85435bb9+复核抽看） |
|---|---|---|---|---|
| R3-BJ27-B00 | confirm | delete | **delete** | 实为花纹领带（几何方块花纹）非文字，采 agy |
| R2-BJ20-B01 | delete | confirm | **delete** | 圆角矩形器件牌框内潦草字符、非独立效果音，采 codex |
| R2-BJ22-B01 | delete | confirm | **correct** | 右缘竖长白底椭圆框内锯齿粗笔画（艺术化拟声）成立但框需收缩——revision 留痕（needs_fix=true、坐标保留原值、`fix_hint_xyxy_page=[1840,60,2100,570]`、`coordinates_changed=false`），重框留后续 revision |

- BJ19/20/21 遗留候选全 delete → 三页关闭为空框 pseudo 负证据留痕。
- 复核轮超抽 4 图实看（3 分歧行+1 共识行 R3-BJ26-B00 delete=圆顶物体轮廓非文字）verdict/rationale 全一致（§8）。

## 5. AC3 manifest.r3 + train-v3 重建

### 5.1 manifest.r3.json（判定并入，real 94）

- 构成：R2 底册 82 样本（`R2 preannotate/manifest.r2.json` **只读**，`provenance.stage2r2` 不覆盖）+
  BJ26-37 新 12 页（`annotate-r3/preannotate/manifest-bj-new.json`）→ **94 样本**（收尾轮 #4/#6 复算：
  94 样本、complete=30、T1a schema 0 错误）。
- stage3r3 判定更新 7 页（`@85435bb9` 逐页明细）：pre-bj16 +B04/05/06 confirm 回填=6 框（completed）；
  pre-bj17/18 考卷页遗留全 delete 框不动留痕（kept_complete_delete_leftovers_excluded）；pre-bj19/20/21 全
  delete→空框负证据；pre-bj22 B00 confirm+B01 correct→complete 2 框（completed）。
- 新 12 页：BJ28/29 confirm→complete（+pre-bj16/22 合计 completed=4）；BJ26/27/30/31 delete→空框 pseudo
  负证据（与 pre-bj19/20/21 合计 kept_pseudo_zero_box_negative_evidence=7）；BJ32-37 零候选
  kept_pseudo_zero_candidates_negative_evidence=6；底册未触碰 75 页 action=「—」。
- `manifest_merge.base_manifest_caliber_note` 口径登记见 §0。

### 5.2 BJ 正集前后对照（manifest.r3.json 实测，收尾轮 #4 复算 8 页 complete）

| sample_id | case | group | split | 框 | 构成/形态 |
|---|---|---|---|---|---|
| pre-bj16 | BJ16 | densho810/vol01 | train | 6 | 斜向粗毛笔片假名（シャ/ゴ类）+R3 回填 B04/05/06（consensus confirm） |
| pre-bj17 | BJ17 | densho810/vol05 | challenge | 2 | 竖排毛笔假名（考卷不动） |
| pre-bj18 | BJ18 | densho810/vol05 | challenge | 3 | 竖排/斜置粗毛笔片假名（考卷不动） |
| pre-bj22 | BJ22 | densho810/vol01 | train | 2 | 手术室潦草拟声：B00 consensus confirm+B01 arbiter correct（本轮新 complete） |
| pre-bj23 | BJ23 | densho810/vol03 | train | 2 | — |
| pre-bj24 | BJ24 | densho810/vol03 | train | 1 | — |
| pre-bj28 | BJ28 | densho810/vol01 | train | 1 | 竖排字块（R3-BJ28-B00 consensus confirm） |
| pre-bj29 | BJ29 | densho810/vol03 | train | 1 | 竖排拟声（R3-BJ29-B00 consensus confirm） |
| **合计** | **8 页** | | | **18** | train 6 页 13 框 + challenge 2 页 5 框 |

- **对照 R2 时点 5 页 11 框**（BJ16×3+BJ17×2+BJ18×3+BJ23×2+BJ24×1；train 侧 3 页 6 框+challenge 考卷 2 页
  5 框）→ **R3 8 页 18 框：+3 页 +7 框**（train 侧 3 页 6 框→6 页 13 框；考卷 5 框不动）。
  Task 合同方向「扩到几十框量级」——18 框**达成方向、如实报数**（未到字面「几十」，§6 提案）。
- BJ26-37 六页（BJ32-37）零候选负证据页留 miss 补画通道；BJ19/20/21 低置信候选全 delete 关闭。

### 5.3 train-v3 重建（912 全量，收尾轮 #5/#6 复算）

| split | 样本 | 框 | real | partial | pseudo | synthetic | images | 组数 |
|---|---|---|---|---|---|---|---|---|
| train | 904 | 2311 | 22 | 140 | 418 | 324 | 904 | 16 |
| val | 4 | 53 | 4 | 0 | 0 | 0 | 4 | 2 |
| test | 2 | 5 | 2 | 0 | 0 | 0 | 2 | 2 |
| challenge | 2 | 5 | 2 | 0 | 0 | 0 | 2 | 1（densho810/vol05） |
| **合计** | **912** | **2374** | **30** | **140** | **418** | **324** | **912** | |

- 构成：pos 30（complete）+ synthetic 324（R1 只读并入，pinned train）+ own-manga 558（六组页数
  125/103/88/105/53/84、框数 481/319/203/295/153/287=1738；入册包 sha256 `af116457…`，validate 558 0 错误；
  license=source=user-own-manga，2026-10-04 用户裁决备案）+ partial 140/pseudo 418（own-manga 分级如实，
  框坐标=chiqui7 模型输出未手工收紧，V2 边界沿袭）。
- split 算法：`assign_splits(force=True, pinned=…)` group-hash-rank-v2 函数参数传参（T1a 同款），
  seed=20261004（`splits.py:30 SEED_DEFAULT`，收尾轮 #11 复核）；pinned 8 组（vol05→challenge、own 六组→train、
  synthetic→train）。
- **断言全过**（交付轮执行、`stage-r3-summary.json` 登记）：① fingerprint=
  `d57353b1db87749fbf20da4a4f2b555c60266db41fc69a594110bd7658c328de`；② assign_splits pinned 重算对 R2 非
  vol05 组**零漂移**（`zero_drift_vs_r2_factory=true`；train 904/2311=V2 基准 901/2304+Δ3/7，val/test/challenge
  不变）；③ 组隔离 **0 违例**（每 group 单 split，challenge 仅 densho810/vol05）；④ 考卷零重叠：own 558 与
  densho810 组**组名/样本 id/页图 sha256 三层零交集**；⑤ 期望分集全数命中。
- **考卷 5 框不动**：challenge=pre-bj17×2+pre-bj18×3（densho810/vol05 组），坐标逐位=R2 final 出厂；
  本组 R3 遗留单元（R2-BJ17-B03/B04、R2-BJ18-B03）全 delete **留痕不入考卷**（`exam_dossier.r3_deleted_leftover_units`）。

### 5.4 YOLO 导出校验（`train-v3/dataset/`）

- 四分集 images 904/4/2/2（收尾轮 #5 目录计数复核）+`dataset.yaml` names 双通道 PASS（读回断言+pyyaml 6.0.3
  独立解析=`{0:bubble, 1:panel, 2:sfx, 3:text}`，nc=4）；ultralytics `check_det_dataset` 扫描 PASS（904/4/2/2，
  出厂登记于 `_export_stats.json`；收尾轮未独立复跑，§9-1）。
- R2 出厂 351 label **逐字节交叉比对 0 失配**（pre-bj16 特判=原 3 行逐字节前缀一致+3 行新增；新 complete
  pre-bj22/28/29 无出厂对照走导出后自洽校验）；sha256 抽验 22 张三方一致；stem_mismatch_total=0。
- labels 为 YOLO seg 归一化多边形（cls=2），stem 规则=sample_id 中 `/`→`__`。

## 6. AC4 T3 材料更新提案（仅提案，不裁决）

1. **BJ 正集量级**：毛笔竖排主攻形态正样本 5 页 11 框→**8 页 18 框**（train 侧 6 页 13 框）——达成合同
   「扩到几十框量级」方向，绝对量仍小（18 框，如实报数）；BJ 域深度继续依赖 324 合成（横排系统字体/限定
   毛笔字体，与真竖排毛笔形态覆盖度未经验证）+own-manga 558（模型输出框未收紧）。T3 Gate 归因时
   「标注质量×数据量」两层须分开。
2. **考卷是否随正集扩容重划（仅提案）**：challenge 现仍=vol05 组 5 框（pre-bj17×2+pre-bj18×3），本轮按合同
   不动。train 侧 BJ 正集扩容后，考卷对「新回填形态」（如 pre-bj16 回填 3 框、pre-bj28/29 新形态）零覆盖——
   可提案 T3 释放时评估从 BJ 正集页或 BJ26-31 已审页划拨 challenge 页；**是否重划属用户/编排裁决，本轮不执行**。
3. **T3 材料清单**：train-v3 指纹 `d57353b1…28de`、912 全量（pos 30+synth 324+own 558）、BJ 正集 18 框、
   考卷 5 框逐位=R2 出厂、`_export_stats.json`/`dataset.yaml` 在 `train-v3/dataset/`。
4. **检测盲区口径持续登记**：chiqui7 对 BJ 毛笔竖排三连实证（R2 conf 天然低→R3 密度全≤1→BJ32-37 毛笔页
   零检出）——**T3 引入新检测权重前，该盲区口径需持续登记**（BJ32-37 miss 补画通道开放）。

## 7. AC5 零 src 与 pin（收尾轮 #9-#12 复算）

- `git diff 9258afc0 HEAD -- src/` 输出 **0 字节**；本轮改动仅 doc/tasks+experiments/M2-SFX-ANNOTATE-R3+
  cases.json 追加+verification 摘要（docs 提交再进三文档）。
- `src/infrastructure/providers/detection_sfx.py` 与 R2 worktree **逐字节一致**（`git diff --no-index` exit=0）；
  pin 常量未动：`SFX_HF_REVISION="7f5f5c0464f2eeb57282f16da760eb8828a8716a"`（detection_sfx.py:108）、
  `SFX_WEIGHTS_SHA256="d87389af4350954143a216bcfe40fd2ad93312cb136534e6073c9c740d98b646"`（detection_sfx.py:110-112）、
  `SFX_CONF_THRESHOLD=0.5`（detection_sfx.py:118）。
- seed pin：`SEED_DEFAULT=20261004`（experiments/M2-SFX-DATA-INFRA/sfx_data_infra/splits.py:30）=
  train-v3 lock.seed=20261004。
- 数据本体 gitignored（`training_data/sfx-v1/{annotate-r3,train-v3}/`）；Git 进：两阶段脚本（5 个）+
  `stage-r3-summary.json` + cases.json 追加；摘要 4 个 artifacts sha256 与盘上文件全 MATCH（#12）。

## 8. 复核轮结论摘录（=PASS，材料随收尾输入提供）

五项复核全部独立重算通过，未发现错误或口径违背：

1. **cases.json**：R3=122 条恰为 R2 110 条纯追加（逐 ID JSON 全等、顶层元数据零差异=深度等值；与本收尾轮
   #7 复算结论一致）；BJ26-37 与 BJ16-25 同构（38 字段键集合逐字一致+全字段类型一致；BJ01-12=36/
   BJ13-15=37 字段系历史代际缺 pixel_size/registration_note，非 R3 引入）。
2. **判定闭环**：codex 22+agy 22 原始判定重算，同判 19=consensus.json、异判 3=divergence.json；共识 verdict
   与双 AI 原判零不一致；共识 19∪仲裁 3=units 22 全量、交集空、仲裁无多余单元；批次清单 6+16=22；
   final=confirm6+correct1+delete15。**抽 4 图实看（超抽 1）verdict/rationale 全一致**：R3-BJ27-B00 预览=
   几何方块花纹非文字→delete✓；R3-BJ26-B00 预览=圆顶物体轮廓非文字→delete✓；R2-BJ20-B01 原页
   vol05_p0052 裁剪实看=圆角矩形器件牌框内潦草字符→delete✓；R2-BJ22-B01 原页 vol01_p0067 裁剪实看=右缘
   竖长白底椭圆框内锯齿粗笔画（艺术化拟声）、候选框右缘 x=1863.4 确实只碰椭圆左缘→correct✓。
3. **manifest.r3**：T1a schema 94 样本 0 错误（本收尾轮 #6 复跑一致）、boxes_meta 索引零失配、completed
   空框违例 0；BJ 正集重算 8 页 18 框（pre-bj16:6/pre-bj17:2/pre-bj18:3/pre-bj22:2/pre-bj23:2/pre-bj24:1/
   pre-bj28:1/pre-bj29:1）vs R2 出厂 5 页 11 框=+3 页+7 框；摘要 4 个 artifacts sha256 与盘上全部一致（#12）。
4. **train-v3**：总量 912=train 904/2311+val 4/53+test 2/5+challenge 2/5 ✓；考卷 5 框不动（坐标逐位=R2 final
   出厂）；组隔离 0 违例（每 group 单 split，challenge 仅 densho810/vol05）；R2 非 vol05 组零漂移=0；names
   双通道 PASS；own-manga 558（六组 125/103/88/105/53/84、1738 框）+synthetic 324 全 train；status
   complete30+synthetic324+partial140+pseudo418=912；dataset images/labels 904/4/2/2 对齐；label 逐字节抽验
   4 样本（test/val）独立 PASS；pre-bj22-B01 correct 坐标保留原值（逐位=R2 底册）+revision.correction_note+
   fix_hint[1840,60,2100,570]+coordinates_changed=false。
5. **零 src+pin**：与本收尾轮 #9-#12 复算一致（src 空 diff、detection_sfx.py 逐字节一致、三 pin 常量+seed
   逐值核对）。

## 9. 非阻断登记（4 条）

1. **ultralytics `check_det_dataset` 扫描冒烟未独立复跑**（GPU venv 在 task-envs 外部树，复核/收尾只读纪律下
   未执行）；`_export_stats.json` 出厂登记 PASS（names/nc=4/dir_counts 904/4/2/2），收尾轮以同维度 yaml
   双通道+目录计数替代覆盖。DSH Review 如需可独立复跑。
2. **BJ32-37 六页 AC1 目检确认含毛笔 SFX 但 chiqui7 零候选**→保持 pseudo 零框负证据（miss 补画通道），属
   honest_notes 已披露的已知盲区口径，非本轮错误。
3. **R2-BJ22-B01 correct 框坐标未实际修正**（needs_fix=true 留 revision 链），沿 R2 correct 口径执行且已如实
   留痕（fix_hint[1840,60,2100,570]），重框留给后续 revision。
4. **BJ26-37 的 chiqui7 预标注 conf 极低（0.02 量级）仍全部入审**——AC2「无 conf 门槛全检出入审」的既定
   设计，复核确认 22 单元无一遗漏；T3 引入新检测权重前该盲区口径需持续登记。

## 10. 限制与 honest_notes

（`stage-r3-summary.json.honest_notes` 全量）：

- BJ26-37 六页（BJ32-37，AC1 目检确认含毛笔竖排 SFX）chiqui7 零候选：保持 pseudo 零框负证据，SFX 标注留
  miss 补画通道（chiqui7 BJ 盲区实证三连：R2 conf 天然低→R3 密度全≤1→毛笔页零检出）。
- BJ19/20/21 遗留候选全 delete→空框 pseudo 负证据留痕（R3 扩审关闭该三页的低置信候选）。
- R2-BJ22-B01 correct：框保留原坐标+revision 留痕（R2 stage2r2 correct 口径），重框参考区域在
  `revision.fix_hint_xyxy_page`。
- 底册口径差异如实登记（§0）。
- own-manga 框坐标=chiqui7 模型输出未手工收紧（V2 边界沿袭）；partial 140/pseudo 418 分级如实。
- pre-bj16 label 与 R2 出厂比对走特判（原 3 行逐字节前缀一致+3 行新增）；其余 R2 出厂 348 入集样本逐字节一致。
- challenge 考卷页的 R3 遗留单元（BJ17×2/BJ18×1）全 delete 已留痕：考卷内容零改动。

其他边界：本轮无模型训练/推理质量评估（T3 范围）；GT=ai-consensus（human_review=false），不声称人工标注
质量；densho810 报告义务（2026-11-02 前）由素材责任方继续跟踪。
