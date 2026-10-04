# M2-SFX-ANNOTATE-R1 阶段二收尾报告（AC3 裁决回填 + AC4 三集导出 + AC5 合成并入）

- Owner：ZCode（本工作区）；Task：[doc/tasks/M2-SFX-ANNOTATE-R1.md](../../doc/tasks/M2-SFX-ANNOTATE-R1.md)
- 基线：stage-1 @79e8dfad / AC5 合成 @e85c546a（本分支）；finalize 实现+数据 @7273c2d1；工具 `experiments/M2-SFX-ANNOTATE-R1/stage2_finalize.py`
- 生成：2026-10-04T11:03Z 前后（finalize 五步）；**rev2（stage2-docs 修订轮，2026-10-04）**——§3 增补双审各自 verdict 分布与「残留 0」覆盖口径，§0 增补 GT 性质登记，§8 增补承诺缺口数字；rev2 全部统计经文档收尾轮从盘上原始数据内部复算（见 §3/§4/§5 各「内部复算」条）。**措辞澄清（DSH r1 C3，rev3）**：本文各处「内部复算」均指同 workflow 内文档收尾 agent 的复算，属 Owner 自核、非独立第三方 Review；独立 Review 由 DSH 另行执行（r1=approved_with_conditions，2026-10-04）
- 判定输入：`training_data/sfx-v1/annotate-r1/judgments/{units,consensus,divergence}.json + arbiter/batch-*.json`
  （codex+agy 双评审 + 第三方仲裁，由编排会话按用户全权授权组织；本 Task 代理只消费判定、不生产判定）

## 0. 模式与边界（先读）

**AC3 本轮以 AI 代审落地（编排裁定 2026-10-04）**：合同原文为"用户逐条审核"；实际执行=
codex+agy 双评审共识（397 单元）+ 分歧单元第三方仲裁（16 单元），覆盖 conf>=0.5 全部 413 单元，
**无未决残留（残留=0，口径见 §3）**。manifest 与工作表一律 `human_review=false` 留痕、
provenance 补 ai-consensus/arbiter 判定链，**不谎称人工**。

**本轮 GT 性质=ai-consensus（用户 2026-10-04 裁决：质量责任由"用户逐条审核"转移为"编排组织
的双评审+仲裁，交用户抽检/翻案通道"）**；provenance 保真：22 个 complete 样本 `provenance.stage2`
逐样本留痕 `mode=ai-review-backfill`、`human_review=false`、`judgments_sources`、kept/excluded/
unjudged 逐框清单与 correction_notes，不将 AI 共识标注表述为人工标注。

**AI 代审的用户裁决原文（DSH r1 C2 落档，2026-10-04）**："T1b交给codex和antigravity同时进行审核，
减少人工工作量"（用户消息原文；对应停点裁定链：stage-1 WAITING_USER_LABELING 停点 @61fe5cd5
登记 conf≥0.5 默认裁定 → 用户裁决双 AI 交叉审核 → AC3 判据修订 @de1b7bf9）。

**ai-consensus 证据强度上限（DSH r1 C5）**：本 GT 不能声称人工标注质量等级——一致性 96.1% 是
两个 AI 评审员的一致，不等于人工正确率；T3 Gate（尤其 G7 端到端损害门）据此应把"标注质量"与
"模型质量"两层误差分开归因，翻案通道（user-residual.json + 抽检）是唯一升级为人工背书的路径。

残留口径双登记（两者不矛盾，勿混读）：① **已判定域残留=0**——consensus(397)∪divergence(16)=413
无遗漏（内部复算 uncovered=0，§3）；② **未判定单元 393**（conf<0.5 与 ref 无 conf，即 806−413）
+ 域内回放 5 页保持 pseudo，单列 `judgments/user-residual.json` 交用户，留后续扩标（编排裁定范围外）。

## 1. 交付概览

| AC | 内容 | 状态 | 证据 |
|---|---|---|---|
| AC3 回填 | 413/806 单元最终判定回填 worksheet（verdict 列 + user_rationale 列=`reviewer=…`+rationale 全文） | **PASS（AI 代审模式，见 §0）** | `worksheet/worksheet.{json,md}`（backfill 块 + md 尾部回填记录）；`judgments/user-residual.json`（393 残留） |
| AC3 manifest | 判定保留框入正集、样本 pseudo→complete（22 个）；delete 框排除留痕；correct 框 revision 链留痕 | **PASS** | `preannotate/manifest.json`（`provenance.stage2`，schema 全量校验 0 错误） |
| AC4 三集 | T1a 拆分器组隔离（组不跨集 + seed=20261004 冻结）→ train/val/test+challenge manifest + 指纹 | **PASS**（challenge 空集如实登记，见 §4） | `final/manifest.{r1,train,val,test,challenge}.json`，指纹 `f9ea1c80…9271` |
| AC4 YOLO seg | dataset.yaml names 顺序逐字=SFX_CLASS_MAP + 归一化多边形导出 + 写后读回断言 | **PASS** | `final/yolo/`（`dataset.yaml`；names 断言 PASS，pyyaml 交叉解析 PASS） |
| AC5 合成并入 | synthetic 324 读 manifest 并入，pinned train、不入 test | **PASS** | `ac5`：`splits_landed={"train":324}`、`in_test=0` |
| AC6 零 src | 零 src 修改；数据本体 gitignored；Git 只进摘要 | **PASS** | `git status`（仅 experiments/M2-SFX-ANNOTATE-R1 + verification/M2-SFX-ANNOTATE-R1 + gitignored 树） |

## 2. 执行记录（实际命令）

```text
"G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" \
  experiments/M2-SFX-ANNOTATE-R1/stage2_finalize.py --step backfill
# → units backfilled=413 residual=393 md_rows=413；verdict dist {confirm:297, delete:111, correct:5}

… --step manifest
# → samples=72 updated_to_complete=22；actions {completed:22, kept_pseudo_no_positive_verdict:26,
#   kept_pseudo_zero_box_negative_evidence:19, kept_pseudo_replay_page:5}

… --step split
# → pos=22 synth=324 by_split {train:342, val:3, test:1}（challenge 空集）；
#   指纹 f9ea1c801e53f705c9ab68c1cac55ff736af926f64108bf71d2aa95af6009271

… --step yolo
# → train 342img/585box、val 3/31、test 1/2、challenge 空集；names assert PASS

… --step summary
# → final/export-summary.json + verification/M2-SFX-ANNOTATE-R1/stage2-final-summary.json
```

## 3. AC3 双审统计（共识/仲裁/残留）

**双审各自 verdict 分布（内部复算：本修订轮从 `judgments/{codex,agy}/batch-*.json` 逐批重算，
与 ask 口径逐数一致）**：

| 评审 | 单元数 | confirm | correct | delete |
|---|---|---|---|---|
| codex | 413 | 304 | 1 | 108 |
| agy | 413 | 297 | 3 | 113 |

**共识/分歧/仲裁与覆盖完备性**：

- **共识（reviewer=codex+agy-consensus）**：397 单元（同判 confirm 294 / 同判 delete 103；
  无 correct 同判对）；user_rationale 列保留双方 rationale 全文（`codex: … ｜ agy: …`）。
- **分歧**：16 单元（divergence.json），与共识**互斥且并集恰为 413**（内部复算：
  consensus_ids ∪ divergence_ids == unit_ids，uncovered=0 → **已判定域残留=0**）。
- **仲裁（reviewer=arbiter）**：16 单元 = 分歧全量（内部复算 arbiter 覆盖 id 集==divergence id 集），
  终判 confirm 3 / correct 5 / delete 8；user_rationale=仲裁 rationale 全文；分歧原判永留
  `divergence.json`。
- **最终 verdict 分布（回填 worksheet）**：confirm 297 / delete 111 / correct 5（=413）。
- **correct（5 框）revision 链**：boxes_meta 该框加 `revision={type:correction_note, needs_fix:true,
  note:…, reviewer:arbiter, coordinates_changed:false}`——AC3"修正行记 revision 链"落地；
  本轮无新坐标（人工补框属扩标），坐标未动、修正需求如实留痕（manifest correction_notes 5 处）。
- **残留（`judgments/user-residual.json`，交用户）**：393 单元 = conf_lt_0.2 262 + conf_0.2-0.5 124 +
  ref_no_conf 7（l3 参照框）；按域 bj 11 / replay-j 5 / ko 305 / ko-ogkalu-crop 72。
  清单附 user_action_guide（逐单元回填 verdict/user_rationale + miss 补画，完成后重跑
  manifest/split/yolo/summary 即扩集）。

## 4. AC4 三集数字（seed=20261004 冻结，group-hash-rank-v2，指纹 `f9ea1c801e53…9271`）

| split | 样本 | 框 | 真实/合成 | 作品组 |
|---|---|---|---|---|
| train | 342 | 585 | 18 真实（261 框）+ 324 合成 | synthetic/annotate-r1（pinned train）+ vasyanator2×7 |
| val | 3 | 31 | 3 真实 | vasyanator2/651664(K02 页 3 框) + 701535(K08 页 27 框+K08 crop 1 框) |
| test | 1 | 2 | 1 真实 | vasyanator2/724815(K01) |
| challenge | 0 | 0 | — | **空集，如实登记** |

内部复算（本修订轮，从盘上五份分集 manifest 重算）：train 342/585、val 3/31、test 1/2、
challenge 0/0 逐一相符；五份 manifest fingerprint 同值 `f9ea1c801e53f705c9ab68c1cac55ff736af926f64108bf71d2aa95af6009271`。

- 组隔离内部复算：从盘上分集 manifest 重算 `group→splits`，**跨集违例=0**（BJ/ko 页与同 case
  ogkalu crop 同组不泄漏；test 组 724815 对训练侧 TrainingSetBuilder 不可见——T1a 设计铁律，
  train/val 图像导出走 builder，test/challenge 走独立导出路径）。
- **challenge 空集原因（不凑数）**：本轮正集无 BJ13/14/15 complete 样本——BJ13 唯一 conf>=0.5
  判定单元被判 delete；BJ14/BJ15 全部框 conf<0.5 未判定（编排裁定不入本轮正集）。三页保持 pseudo
  留待用户扩标；补齐正框后重跑 split+yolo 即由 T1a 拆分器自动单列。`manifest.challenge.json`
  照写（`sample_count=0` + `note: 空集（见 manifest.r1.json lock.challenge_note）`），
  dataset.yaml 不写 challenge 键（防 ultralytics 空目录扫描报错；内部复算解析 keys=
  names/path/train/val/test，确无 challenge）。
- **BJ 域本轮正集为 0（如实登记）**：BJ01-12 页候选框全部 conf<0.5 未判定；BJ06 8 confirm 属回放页
  （编排裁定排除，§7）；BJ13 唯一判定=delete。真实页正集全部来自 KO 域（K01-K10 页 + 12 个 ogkalu crop）。

## 5. AC4 YOLO seg 导出与 names 硬约束校验

- `final/yolo/dataset.yaml` names 逐字：

  ```yaml
  names:
    0: bubble
    1: panel
    2: sfx
    3: text
  ```

  校验链（两条独立通道均 PASS）：① 脚本写后读回断言（`stage2_finalize.py:572`
  `_assert_names_literal`，与生产 `src/infrastructure/providers/detection_sfx.py:436` 同一断言形态
  `parsed != {str(k): v for k, v in SFX_CLASS_MAP.items()}` 即拒绝导出；`SFX_CLASS_MAP`
  自生产模块 `detection_sfx.py:137` 只读 import，零复制）；② 内部复算（本修订轮）pyyaml
  `safe_load` 解析得 `{0:'bubble',1:'panel',2:'sfx',3:'text'}` 相等，且字面逐行在文件中。
- labels 口径：`cls x1 y1 …`（归一化 6 位小数，clip [0,1]）；cls 恒 `2=sfx`（本轮唯一 GT 类；
  独立重算（本修订轮）train 585 / val 31 / test 2 行**全部 cls=2**，坐标越界 0 行，点数 <4
  0 行，images/labels stem 失配 0；challenge 目录未导出）。多边形 = T1a 实例包络口径
  （非字形像素 mask）。
- 图像拷贝保真抽查（synth 1 + K 页 3，本修订轮复跑）：`pre-k03`(train)、`imp-ogkalu-k08-r025`(val)、
  `pre-k01`(test) src==dst==manifest.image.sha256 三方一致；`synth-r1-0000-f0t0r0p0a0o0`(train)
  源（data_root 相对路径 `synthetic/…png`）==manifest==导出副本三方一致。
- 文件名规则：YOLO stem = sample_id 中 `/`→`__`（`synth-r1/synth-r1-0000-…` → `synth-r1__synth-r1-0000-…`）。

## 6. AC5 合成并入

- 读 `synthetic/manifest.json`（stage2_synth_batch.py 产物，324 样本，T1a 渲染管线只读复用），
  `SampleRecord.from_dict` 逐条 schema 校验后并入；组 `synthetic/annotate-r1` 按 T1a 先例
  pinned train（r1 P1-3：单一大合成组不参与比例切片），**test 零合成**（断言 + 摘要 `in_test=0`）。

## 7. 保持 pseudo 不入本轮训练集的处置（编排裁定范围外，留后续扩标）

| 处置 | 样本数 | 说明 |
|---|---|---|
| kept_pseudo_replay_page | 5 | 回放 5 页 BJ06+J38/J41/J43/J51（含 BJ06 的 8 个 confirm——判定仅回填 worksheet 留痕） |
| kept_pseudo_no_positive_verdict | 26 | 本轮判定无 confirm/correct（全 delete 或未判定） |
| kept_pseudo_zero_box_negative_evidence | 19 | 零检出负证据页/crop（T1a schema 允许 pseudo 空框） |
| completed（入正集） | 22 | boxes=判定保留框（294 框）；excluded/unjudged 留痕于 provenance.stage2 |

## 8. 已知边界与后续（诚实登记）

1. **AI 代审非人工 / GT 性质=ai-consensus**：`human_review=false` 全量留痕（§0）；用户抽检/翻案走
   user-residual.json 的 action_guide（补裁 + miss 补画）后重跑 split/yolo/summary 扩集，无需重写工具。
2. **标注量承诺缺口（如实登记，不凑数）**：BJ 域 15/25 页（素材树仅 BJ01-15 在盘）、KO 域 10/15 页
   （K11-25 local_path 不存在），60 MISSING case 逐条登记于 `selection/selection.json`
   （stage-1 回报，Task「依赖、风险与阻塞」节）；缺口需素材扩充后补轮。
3. **challenge/BJ 正集空**：见 §4；不凑数。BJ 域标注承诺（≥25 页）需素材扩充 + 用户扩标轮补齐。
4. **test 仅 1 组 1 样本（K01 页 2 框）**：组数=10 的比例切片下限（round(0.15×10)=2 val、余 1 test）；
   组隔离优先于样本量（合同 AC4 组不跨集硬约束）。test 统计功效有限，评估解读需连同 challenge
   一起看；扩素材后组数增长自然缓解。
5. **correct 5 框坐标未动**：needs_fix=true 留痕，补框属人工扩标轮。
6. 部分覆盖页入正集时，未判定框已从 GT 剔除（不谎称 complete 整页）——页面上未判定区域在训练中
   作背景，属编排裁定"conf<0.5 不入本轮训练集"的既定噪声口径，扩标后收敛。

### 8.1 A′ 采纳输入条件未满足（DSH r1 C1，交编排/用户裁决——T2 释放前置；DSH r1 C4 回放偏差并入）

对照 `verification/M2-SFX-FINETUNE-PREFLIGHT/preflight-report.md:61`（A′ 路线采纳的输入条件），
本 Task 交付后实际状态：

| A′ 输入条件 | 承诺 | 实际 | 状态 |
|---|---|---|---|
| BJ 域真实页标注 | ≥25 页 | 15 页（素材仅 BJ01-15 在盘） | **未满足** |
| KO 域真实页标注 | ≥15 页 | 10 页（K11-25 路径缺失） | **未满足** |
| BJ 域正集样本 | 主攻形态覆盖 | **0**（BJ06 8 confirm 属回放页被排除出训练集；BJ13 唯一 conf≥0.5 判定=delete；BJ01-05/07-12 候选框全部 conf<0.5 未判定） | **未满足（最关键）** |
| challenge 集（BJ13/14/15） | 有正样本可评 | 空集（如实登记不凑数） | **未满足** |
| 合成样本 | ≥200 | 324 | 满足 |

**对 T2 训练的含义（如实呈现，不粉饰）**：A′ 主攻目标=BJ 毛笔竖排召回恢复，但 V1 训练集 BJ 域
正集=0——现有数据训出的模型**对该主攻形态没有真实正样本可学**（324 合成为横排系统字体/限定
毛笔字体，与真竖排毛笔形态的覆盖度未经验证）；若按现状释放 T2，G1 BJ 门大概率不可达。
处置选项（交裁决）：(a) 补素材轮（下载 BJ 缺口 10 页+K11-25）+ BJ conf 0.2-0.5 层扩审（124 候选）
后再 T2；(b) 先用现有 KO 域+合成数据跑 T2 管线验证（不承诺 Gate），BJ 补齐后 V2 正式训；
(c) T1a 渲染管线扩展 BJ 竖排毛笔形态合成（需真字体与版式参数）。

**回放 5 页目的偏差（DSH r1 C4 登记）**：合同对域内回放（BJ06+J38/J41/J43/J51）的目的是
"防灾难性遗忘"（隐含其正样本应入 train），但编排裁定把回放页排除出本轮判定范围（保持 pseudo、
仅 worksheet 留痕）——回放页**未按合同目的产出训练正例**。该偏差并入上表 A′ 条件未满足项，
留扩标轮补（user-residual.json 已含回放页单元）。
