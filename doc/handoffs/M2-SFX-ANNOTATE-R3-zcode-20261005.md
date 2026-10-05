---
task_id: M2-SFX-ANNOTATE-R3
author: ZCode
recipient: DeepSeek Harness（独立 Review）→ 编排会话代行 Codex（集成）
base_commit: 9258afc0
delivery_head: 85435bb9
status: in_review
---

# Handoff：M2-SFX-ANNOTATE-R3（T1b-R3 扩标轮：BJ 候选池 44 页选页入池+低置信扩审+正集扩容）

## 交付结果

分支 `agent/zcode/M2-SFX-ANNOTATE-R3`（worktree `G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R3-zcode`），
基线 9258afc0（分支自 main `7dd5402d` 分出），交付提交：

| commit | 内容 |
|---|---|
| 579af8a5 | AC1 选页入池：44 页候选池密度扫描（kept=1 六页 rank1-6 直选+kept=0 38 页并列 AI 目检毛笔形态决胜选 6）→ cases.json 纯追加 BJ26-BJ37（+900/−0，既有 110 条深度等值）+ material 三脚本 |
| d1a6da43 | AC2 清单：BJ26-37 新页整页 letterbox 预标注（无 conf 门槛全检出入审）+ R2 遗留 conf<0.2 16 单元并入 → units.json（bj_new 6+bj_lowconf_leftover 16=22）+ 双审批次 [6,16]（≤20/批）+ stage1 工具 |
| 85435bb9 | AC2 后半+AC3：双 AI 判定比对（共识 19+分歧 3→仲裁终裁逐图实看）→ final 22 单元 confirm6+correct1+delete15 → 判定并入 manifest.r3（real 94，T1a schema 0 错误）+ train-v3 重建 912 全量（考卷 5 框不动） |
| （本次 docs 提交） | stage-r3-report.md + 本 Handoff + Task 回填（见 delivery_head 后的 docs head） |

与 AC 逐项对照（全部数字复算口径见 [stage-r3-report.md](../../verification/M2-SFX-ANNOTATE-R3/stage-r3-report.md)）：

- **AC1 选页入池：PASS**。44 页候选池（R2 素材根 54−已入池 10，与 R2 runner_up_pool 逐项一致）chiqui7
  密度扫描：密度分布极稀（kept=1 仅 6 页/kept=0 38 页，chiqui7 BJ 盲区再现）→ rank1-6 无并列直选 +
  rank7-12 全并列 AI 目检毛笔竖排形态二次决胜（REF=BJ16/17/18/23/24 校准，contact sheet 5 批留证）→
  cases.json BJ26-BJ37 纯追加（+900/−0，既有 110 条深度等值+顶层元数据零差异）；剩余 32 张留池。
- **AC2 预标注+扩审：PASS**。新 12 页整页 letterbox 预标注（**无 conf 门槛全检出入审**，BJ32-37 六页零候选
  → pseudo 负证据+miss 补画通道）6 单元 + R2 遗留 conf<0.2 16 单元 = 22 单元双 AI 交叉审核（批次 [6,16]
  ≤20/批，judge_std 沿 R2 含毛笔竖排主攻形态说明，`human_review=false` 保真）：codex 22（confirm7/correct0/
  delete15）、agy 22（confirm8/correct0/delete14）→ 共识 19（confirm6+delete13）+ 分歧 3 → 编排逐图实看终裁
  （R3-BJ27-B00 delete 花纹领带非文字 / R2-BJ20-B01 delete 器件牌字符 / R2-BJ22-B01 correct 椭圆拟声成立框需
  收缩）→ final **confirm6+correct1+delete15**；**判定全量覆盖：consensus(19)∪divergence(3)=units(22)，
  uncovered=0，残留=0**；BJ19/20/21 低置信候选全 delete 关闭。
- **AC3 manifest v3+重切：PASS**。R2 底册 82（preannotate/manifest.r2.json 只读，stage2r2 链不覆盖写）+
  BJ26-37 新 12 页 → **manifest.r3.json real 94 样本，T1a schema 0 错误**（底册口径差异如实登记：
  ask 字面「R2 final 82」实为 preanimate 82/final 351，见 report §0）→ train-v3 重建 **912 全量**
  （train 904/2311=val/text 基准 901/2304+Δ3/7、val 4/53、test 2/5、challenge 2/5 **考卷 5 框不动**
  坐标逐位=R2 出厂；pos 30+synthetic 324+own-manga 558 并入；指纹
  `d57353b1db87749fbf20da4a4f2b555c60266db41fc69a594110bd7658c328de`，seed=20261004）。断言全过：
  assign_splits pinned 重算对 R2 非 vol05 组零漂移、组隔离 0 违例、考卷零重叠（组名/样本 id/页图 sha256
  三层零交集）、期望分集全数命中；YOLO 四分集+names 双通道+check_det_dataset 扫描 PASS、R2 出厂 351 label
  逐字节比对 0 失配（pre-bj16 特判）、sha256 抽验 22 张三方一致。**BJ 正集 5 页 11 框→8 页 18 框**
  （train 侧 3 页 6 框→6 页 13 框：pre-bj16 回填+3、pre-bj22 新 complete+2、pre-bj28/29 新页+1×2；
  考卷 5 框不动）——合同「扩到几十框量级」方向达成、18 框如实报数。
- **AC4 报告+Handoff+Task 回填：PASS（本次 docs 提交）**。T3 材料更新见 report §6（正集量级 18 框/考卷是否
  随正集扩容重划**仅提案不裁决**/盲区口径持续登记）。
- **AC5 零 src：PASS**。`git diff 9258afc0 HEAD -- src/` 0 字节；detection_sfx.py 与 R2 worktree 逐字节一致，
  pin 未动（SFX_HF_REVISION=7f5f5c04…、SFX_WEIGHTS_SHA256=d87389af…、SFX_CONF_THRESHOLD=0.5，
  detection_sfx.py:108-118）；seed pin SEED_DEFAULT=20261004（splits.py:30）；数据本体 gitignored。

交付后复核轮 **=PASS**（五项独立重算，含超抽 4 图实看 verdict/rationale 全一致；非阻断登记 4 条，
report §8-§9）。GT 性质=**ai-consensus**（human_review=false，沿 R1 §0 口径），不声称人工标注质量。

## 验证证据

环境：Windows；python（复算）= 系统 python；数据链工具环境=交付轮 GPU venv（task-envs 外部树，
收尾/复核只读纪律下未复跑推理）；被测 commit=85435bb9（数据）+ 579af8a5（素材）+ d1a6da43（清单）。

| AC/场景 | 实际命令/步骤 | 结果 | 日志/产物 |
|---|---|---|---|
| AC1 cases.json 保真 | python 深度对比两 worktree cases.json；`git diff --numstat 579af8a5~1 579af8a5 -- …cases.json` | PASS（R3 122 vs R2 110，前 110 条逐条深度等值+顶层元数据零差异；+900/−0 纯追加） | `test_assets/comic_golden_suite/manifests/cases.json`；report §2.2#7-8 |
| AC1 选页留证 | `selection/material-selection-r3.json`（44 池/密度分布/rank1-12 选页理由+visual_evidence）+ inspect-batch-1..5.png | PASS（kept=1 六页 no-tie 直选；kept=0 38 页并列目检决胜 tier=strong） | `annotate-r3/selection/` |
| AC2 双审统计 | python 逐批重算 judgments/{codex,agy}/batch-*.json | PASS（codex 22=7/0/15；agy 22=8/0/14；共识 19；分歧 3；仲裁 3；uncovered=0） | `judgments/{consensus,divergence}.json`；report §4.2 |
| AC2 覆盖闭环 | python 对账 units/consensus/divergence/批次清单 | PASS（19∪3=22 全量、交集空、批次 6+16=22、final 6/1/15） | `judgments/units.json`；report §4.2-4.3 |
| AC2 仲裁实看 | 编排逐图实看终裁（3 单元）+复核轮超抽 4 图 | PASS（verdict/rationale 全一致） | `judgments/arbiter/batch-1.json`；report §4.3/§8 |
| AC3 manifest.r3 | python 读回+T1a `SampleRecord.from_dict().validate()` 全量 | PASS（94 样本 0 错误；complete=30；BJ complete 8 页） | `annotate-r3/preannotate/manifest.r3.json`；report §5.1 |
| AC3 BJ 正集对照 | python 重算 8 页 complete 框数 vs R2 出厂 | PASS（8 页 18 框=5 页 11 框+3 页+7 框；train 13 框+考卷 5 框） | report §5.2 |
| AC3 train-v3 | python 读回 manifest.train-v3+images 目录计数 | PASS（912=train 904/2311+val 4/53+test 2/5+challenge 2/5；指纹 d57353b1…28de；seed=20261004） | `train-v3/manifest.train-v3.json`；report §5.3 |
| AC3 断言组 | 交付轮 stage2_finalize_r3 断言（零漂移/组隔离/考卷零重叠三层/期望分集） | PASS（summary 登记，复核轮④独立重算一致） | `stage-r3-summary.json.train_v3` |
| AC3 YOLO | names 双通道（读回+pyyaml 6.0.3）+R2 出厂 351 label 逐字节比对+sha256 抽验 22 张 | PASS（names={0:bubble,1:panel,2:sfx,3:text}；0 失配；pre-bj16 特判=前缀+3 行新增） | `train-v3/dataset/`；report §5.4 |
| AC3/AC4 T1a schema | manifest.r3 94+manifest.train-v3 912 全量 from_dict+validate | PASS（0 错误；收尾轮复跑一致） | report §2.2#6 |
| AC4 artifacts | python sha256 对盘 summary artifacts 4 件 | PASS（全 MATCH） | `stage-r3-summary.json.artifacts`；report §2.2#12 |
| AC5 零 src+pin | `git diff 9258afc0 HEAD -- src/`；`git diff --no-index` vs R2 worktree detection_sfx.py；grep pin 常量 | PASS（0 字节；逐字节一致 exit=0；pin 三常量+SEED_DEFAULT=20261004 逐值核对） | report §2.2#9-11、§7 |

未运行项：ultralytics `check_det_dataset` 扫描冒烟未在收尾/复核轮独立复跑（GPU venv 在 task-envs 外部树，
只读纪律；出厂 `_export_stats.json` 登记 PASS+同维度 yaml 双通道/目录计数替代覆盖，非阻断登记 §9-1）；
双 AI 判定推理与仲裁实看为判定轮已执行（判定链留痕），收尾轮只复算其产物；本轮无模型训练/质量评估
（T3 范围）。

## 接收方式

- 仓库：G:/CODEX/New Manga（Git linked worktree `G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R3-zcode`），
  分支 `agent/zcode/M2-SFX-ANNOTATE-R3`，base=9258afc0，head=85435bb9+docs。
- 复现核对（Reviewer 最小集）：
  1. python 读 `verification/M2-SFX-ANNOTATE-R3/stage-r3-summary.json` 与
     `verification/M2-SFX-ANNOTATE-R3/stage-r3-report.md` §2.2 复算记录，抽任一数字复算
     （数据树=`training_data/sfx-v1/{annotate-r3,train-v3}/`，gitignored）；
  2. python 逐批重算 `training_data/sfx-v1/annotate-r3/judgments/` 覆盖闭环（19∪3=22、uncovered=0）；
  3. `git diff 9258afc0 HEAD -- src/` 应为空；cases.json 与 R2 worktree 深度对比（前 110 条等值）。
- 数据路径：`training_data/sfx-v1/annotate-r3/{preannotate,judgments,worksheet,scan,selection,previews}` +
  `training_data/sfx-v1/train-v3/{manifest.train-v3.json,dataset/}`；R1/R2 树与 own-manga 入册包在
  本 worktree/task-envs 外部树只读。
- 依赖变化：无（复算仅 python 标准库+`experiments/M2-SFX-DATA-INFRA` schema；pyyaml 既有依赖）。

## 下一任务建议（必填）

- Task ID / 标题：M2-SFX-ANNOTATE-R3 独立 Review（DSH）→ 集成（编排会话代行 Codex）。
- 推荐 Agent / Reviewer：DeepSeek Harness（非作者 Review，Task frontmatter reviewer 已指定）；
  Review 通过后由编排会话代行 Codex 集成（沿 R1/R2 先例：审查→merge→Task done 回填）。
- 推荐原因与前置依赖：Task 合同要求 Reviewer=DeepSeek Harness（非作者）；本交付为 T3 正式 Gate 前置，
  DSH 需复核判定闭环与 BJ 正集对照（report §5.2）、底册口径差异登记（report §0）与 T3 提案（report §6）
  是否可接受。
- Recovery point：仓库 G:/CODEX/New Manga；branch `agent/zcode/M2-SFX-ANNOTATE-R3`；
  base=9258afc0，实现 head=85435bb9（docs 提交在其后）。
- 允许修改路径（Review 轮）：`verification/M2-SFX-ANNOTATE-R3/**`（审查证据）、
  `doc/tasks/M2-SFX-ANNOTATE-R3.md`（review_events 回填）、`doc/reviews/M2-SFX-ANNOTATE-R3-*.md`。
- 禁止范围与新增授权条件：`src/**`、`tests/**`、`doc/contracts/**`、数据树（gitignored 只读）、cases.json
  既有条目、R1/R2/V1/V2 交付物、考卷 vol05 组；Review 不改实现代码与判定数据（问题走 review_events 交
  Owner 返工）。
- 交付物：DSH review 报告（沿 doc/templates/REVIEW.md）落 `doc/reviews/M2-SFX-ANNOTATE-R3-85435bb9-dsh-r1.md`
  （或 verification/ 沿先例）；结论 approved / approved_with_conditions / changes_requested + P0-P4 分级。
- 验证命令、环境与完成 Gate：上节「复现核对」三项；Gate=判定范围覆盖复核（22 单元 uncovered=0）+
  BJ 正集 8 页 18 框对照复核 + 考卷 5 框不动断言复核 + 底册口径差异登记可接受性意见。
- 可直接转发给 DSH 的指令：

> 请对 M2-SFX-ANNOTATE-R3 做独立 Review（非作者）。工作区
> `G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R3-zcode`，分支 `agent/zcode/M2-SFX-ANNOTATE-R3`，
> 基线 9258afc0，交付 commit 579af8a5（素材）+d1a6da43（清单）+85435bb9（判定并入+重切）+docs。先读
> [Project Rebaseline Plan] 与 [doc/tasks/M2-SFX-ANNOTATE-R3.md] 核对合同，再读
> [verification/M2-SFX-ANNOTATE-R3/stage-r3-report.md]（全部数字为 Owner/收尾轮侧复算，需抽验）与
> stage-r3-summary.json。重点：①AC1 选页链（cases.json 既有 110 条深度等值、BJ26-37 登记口径与 BJ16-25
> 同构、密度选页+目检决胜留证）；②双审统计复算（codex 22=7/0/15、agy 22=8/0/14、共识 19/分歧 3/仲裁 3、
> uncovered=0、human_review=false 保真、arbiter rationale 逐图实看留痕）；③manifest.r3（94 样本 T1a schema、
> BJ 正集 5 页 11 框→8 页 18 框对照、底册口径差异登记 report §0 是否可接受）；④train-v3（指纹
> d57353b1…28de、912 全量、考卷 5 框坐标逐位=R2 出厂、组隔离 0 违例、own-manga 558 并入、R2 出厂 351
> label 逐字节比对）；⑤零 src+pin（src 空 diff、detection_sfx.py pin 未动）；⑥T3 材料更新提案（report §6
> 考卷是否随正集扩容重划仅提案）给出裁决意见。输出 REVIEW 模板报告，结论+P0-P4 分级；不改实现与数据。

## 风险与遗留

1. **BJ 正集绝对量仍小**：8 页 18 框（train 侧 13 框）；BJ 域深度依赖 324 合成+own-manga 558（模型输出框
   未收紧，partial 140/pseudo 418 分级如实）——T3 Gate 归因时「标注质量×数据量×域差」多层分开。
2. **chiqui7 BJ 盲区口径**：BJ32-37 六页目检确认含毛笔 SFX 但零候选（pseudo 负证据+miss 补画通道）；
   BJ26-37 预标注 conf 极低（0.02 量级）全入审属既定设计——T3 引入新检测权重前该盲区口径需持续登记。
3. **R2-BJ22-B01 correct 未实际重框**：needs_fix=true 留 revision 链（fix_hint[1840,60,2100,570]、
   coordinates_changed=false），重框留给后续 revision。
4. **底册口径差异**：ask 字面「R2 final manifest 82」与文件事实不符（final 实为 351、82 底册本体=
   preannotate/manifest.r2.json）——按语义正确方案执行并如实登记（report §0），DSH Review 请给出可接受性意见。
5. **ultralytics 扫描未独立复跑**：出厂登记 PASS+替代覆盖（yaml 双通道+目录计数），DSH 如需可在 GPU venv
   独立复跑（非阻断）。
6. **跨 worktree 依赖**：R2 遗留单元预览图引用 R2 worktree 绝对路径；R1/R2 树与 own-manga 入册包在
   外部树只读——复算时勿跨树写入。
7. **GT 性质**：ai-consensus（human_review=false），不声称人工标注质量；用户抽检/翻案通道（R1
   user-residual.json）仍开放。
8. **densho810 报告义务**：公开使用后 1 个月内邮件报告（窗口至 2026-11-02）由素材责任方跟踪。

## 实验附录（实验任务）

- **数据来源与许可**：BJ=densho810.com 官方免费卷 vol01/03/05（作者 free-use 条款+强制署名「ブラックジャックに
  よろしく 佐藤秀峰」+公开使用后 1 个月内邮件报告 info@densho810.com——报告窗口至 2026-11-02；禁 Kindle
  商店分发；JASRAC 卷 2/7/11 未触碰）；页图为 R2 素材根只读复制。合成=R1 渲染产物只读并入（324）。
  own-manga=用户自有素材（source=user-own-manga，2026-10-04 用户裁决备案；入册包 sha256 `af116457…`）。
- **数据 Hash**：cases.json page_sha256 逐页（BJ26-37）；manifest.r3.json=`1c6a97bc…8fed`、
  manifest.train-v3.json=`ab7b68de…8e50`、dataset.yaml=`71dbe2c3…b281`、_export_stats.json=`4d4a178c…ad36`
  （artifacts 4 件收尾轮对盘全 MATCH）；train-v3 指纹 `d57353b1db87749fbf20da4a4f2b555c60266db41fc69a594110bd7658c328de`。
- **模型/权重版本与 Hash**：chiqui7 密度扫描/预标注引擎=yolo11s-seg.onnx（生产 detection_sfx 同款；
  SFX_HF_REVISION=`7f5f5c04…`、SFX_WEIGHTS_SHA256=`d87389af…`，detection_sfx.py:108-112，本轮未变更）。
- **Provider/Runtime**：onnxruntime（交付轮 GPU venv）；图像校验 PIL；复算=python 标准库+pyyaml 6.0.3。
- **网络策略**：本轮零新增网络下载（BJ 页图复用 R2 素材根渲染；own-manga 本地素材）。
- **参数**：seed=20261004（选页决胜+split 沿 T1a splits.SEED_DEFAULT=splits.py:30）；密度扫描沿 R2 口径
  （整页 letterbox）；AC2 新页预标注**无 conf 门槛全检出入审**；批次 ≤20/批=[6,16]；split=group-hash-rank-v2
  组隔离+pinned 8 组（vol05→challenge/own 六组→train/synthetic→train）。
- **运行次数**：各步骤单次（summary generated_at=2026-10-05T02:46:59Z）；收尾/复核轮为独立重读复算，非重跑。
- **原始结果**：双审 codex 22=7/0/15、agy 22=8/0/14；共识 19+分歧 3 仲裁终裁（delete2+correct1）→
  final confirm6+correct1+delete15；manifest.r3 94 样本（complete 30）；train-v3 912（train 904/2311、
  val 4/53、test 2/5、challenge 2/5）；BJ 正集 5 页 11 框→8 页 18 框。
- **质量判断办法**：判定=双 AI 共识+分歧逐图实看仲裁（rationale 全文留痕）；GT 硬校验=T1a schema 全量+
  names 双通道+label 逐字节比对+sha256 抽验；无模型质量评估（T3 范围）。
- **失败样例**：BJ32-37 六页零候选（chiqui7 盲区，如实登记非失败）；BJ26/27/30/31 候选 delete（空框负证据）。
- **限制**：见「风险与遗留」1-8。
- **建议**：T3 释放裁决以 report §6 提案为准（考卷重划仅提案）；BJ 正集量级 18 框如实报数，Gate 归因注意
  ai-consensus 上限（R1 §0）。
