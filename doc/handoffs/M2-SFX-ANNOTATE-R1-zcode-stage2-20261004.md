---
task_id: M2-SFX-ANNOTATE-R1
author: ZCode（本工作区 subagent）
recipient: DeepSeek Harness（审查，非作者）→ Codex/编排会话（集成裁定）
base_commit: 1b765007
delivery_head: 67172ed6（r1 返修）；r2 文本级收尾 commit 见提交链末
status: stage2_complete_IN_REVIEW
---

# Handoff：M2-SFX-ANNOTATE-R1 阶段二（AC3-AC6 全链收口）

## 交付结果

**阶段一+阶段二全链交付完毕；DSH r1=approved_with_conditions（2026-10-04）、r2=approved_with_conditions（0×新 P0/P1/P2，C1/C2/C4/C5 全闭、C3 残项本轮收尾），文本级收尾后交编排集成。**
阶段一（AC1+AC2，@79e8dfad）交付三源预标注+审核工作表并在 WAITING_USER_LABELING 停点；
阶段二按**编排裁定（2026-10-04，用户全权授权）以 AI 代审落地 AC3**，AC4 三集+YOLO seg 导出、
AC5 合成并入、AC6 零 src 纪律全部完成。提交链：
`1b765007（release）→ fe62677e（claim stage-1）→ 79e8dfad（stage-1 实现）→ e85c546a（AC5 合成 324）→ cc51cd6e（stage-1 handoff 回填）→ 7273c2d1（stage-2 finalize 实现+数据+报告）→ 本文档提交（stage2-docs）`。

变更路径：`experiments/M2-SFX-ANNOTATE-R1/{stage1_preannotate.py, stage2_synth_batch.py,
stage2_finalize.py}`、`verification/M2-SFX-ANNOTATE-R1/{stage1-report.md, stage1-manifest-summary.json,
synthetic-summary.json, stage2-final-summary.json, stage2-report.md}`、Task 回填。
数据本体在 gitignored 树 `training_data/sfx-v1/annotate-r1/`（preannotate/worksheet/judgments/
final/{manifest.*.json, yolo/}），Git 只进摘要。

**核心数字**（全部可由盘上原始数据内部复算，stage2-report.md rev3 已复算一轮）：

- AC3：conf>=0.5 共 413 单元全覆盖——codex 判 413（confirm 304/correct 1/delete 108）、
  agy 判 413（confirm 297/correct 3/delete 113）；共识 397 + 分歧仲裁 16，共识∪分歧=413
  **无未决残留（残留=0）**；最终 verdict confirm 297/delete 111/correct 5；correct 5 框
  revision 链留痕（坐标未动）；**GT 性质=ai-consensus（用户 2026-10-04 裁决转移质量责任），
  `human_review=false` 全量留痕不谎称人工**；806−413=393 未判定单元 + 回放 5 页 pseudo
  交用户（`judgments/user-residual.json`）。
- AC4：T1a `assign_splits` 组隔离（组不跨集内部复算 0 违例；seed=20261004 冻结；五份 manifest
  指纹同值 `f9ea1c801e53…9271`）→ train 342 样本/585 框（324 合成 pinned train + 18 真实 261 框）/
  val 3 样本/31 框（组 651664/701535）/ test 1 样本/2 框（K01，组 724815，对 TrainingSetBuilder
  不可见）/ **challenge 0/0 空集如实登记**（BJ13 唯一判定=delete、BJ14/15 无判定，不凑数）；
  YOLO seg 导出 `final/yolo/{images,labels}/{train,val,test}/`（challenge 空集未导出；
  dataset.yaml 不写 challenge 键）；names 顺序逐字=SFX_CLASS_MAP 双通道校验 PASS
  （脚本读回断言 `stage2_finalize.py:572` ≡ 生产 `detection_sfx.py:436` 形态 + pyyaml 独立解析）；
  labels 独立重算 train 585/val 31/test 2 行全部 cls=2、坐标∈[0,1]、多边形≥4 点、stem 0 失配；
  图像拷贝 sha256 抽查（synth 1+K 页 3）三方一致。
- AC5：synthetic 324（≥200 承诺达成）并入 train，`in_test=0` 断言通过。
- AC6：零 src（`SFX_CLASS_MAP`/T1a schema/atomicio/splits/TrainingSetBuilder 只读复用）；
  数据本体 gitignored。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 三源合并 | `stage1_preannotate.py --step assemble` + T1a schema 全量校验 | T1.1.1-impl-py312 @79e8dfad | PASS（72 样本/806 框/0 错误/全 pseudo） | `preannotate/manifest.json`；stage1-report.md |
| AC2 密度扫描+工作表 | `stage1_preannotate.py --step scan/worksheet`（seed=20261004 冻结） | C4-gpu-py312 / T1.1.1 @79e8dfad | PASS（BJ 15p+KO 10p+回放 5p；806 单元/808 预览） | `selection/selection.json`、`worksheet/worksheet.{json,md}` |
| AC3 回填（AI 代审） | `stage2_finalize.py --step backfill/manifest`；文档收尾轮内部复算 `judgments/{codex,agy}/batch-*.json`+consensus/divergence/arbiter 覆盖并集 | T1.1.1-impl-py312 @7273c2d1 | PASS（413 回填；双审分布与共识/分歧/仲裁覆盖逐数复核一致，uncovered=0） | `worksheet/worksheet.{json,md}` backfill 块；`judgments/user-residual.json`；stage2-report.md §3 |
| AC4 三集+组隔离 | `stage2_finalize.py --step split`；文档收尾轮从盘上 manifest 重算 group→splits + 指纹比对 | T1.1.1-impl-py312 @7273c2d1 | PASS（342/3/1/0；跨集违例=0；五指纹同值） | `final/manifest.{r1,train,val,test,challenge}.json`；stage2-final-summary.json |
| AC4 YOLO+names | `stage2_finalize.py --step yolo`；文档收尾轮 pyyaml 解析+labels 行级重算+sha256 三方抽查 | T1.1.1-impl-py312 @7273c2d1 | PASS（names 双通道；cls 恒 2；stem 0 失配；抽查 4/4 一致） | `final/yolo/`（dataset.yaml、_export_stats.json）；stage2-report.md §5 |
| AC5 合成并入 | `stage2_synth_batch.py`（e85c546a）+ `--step split` 并入断言 | T1.1.1-impl-py312 @7273c2d1 | PASS（324 全落 train，in_test=0） | `synthetic/manifest.json`；`final/manifest.train.json` |
| AC6 零 src | `git diff 1b765007..HEAD --stat -- src/ tests/` | 本分支 | PASS（零变更） | Git |
| DSH 审查 | r1+r2 报告纪要 | — | **r1=approved_with_conditions（0×P0、2×P1、3×P2、8×P3、5×P4）；r2=approved_with_conditions（0×新 P0/P1/P2，C1/C2/C4/C5 全闭，C3 残项收尾）** | verification/M2-SFX-ANNOTATE-R1/dsh-r{1,2}-verdict-summary.md |

未运行项：无（DSH r1 于 2026-10-04 完成=approved_with_conditions，必闭条件 C1-C5 返修落实；r2 复核同日完成=approved_with_conditions 0×新 P0/P1/P2，残项文本级已收尾；r1 主报告全文因 headless stdout 截断未保留、纪要落盘有披露）。
用户抽检/翻案通道（user-residual.json）未运行——属用户后续扩标轮，编排裁定范围外。

## 接收方式

- 分支/工作区：`agent/zcode/M2-SFX-ANNOTATE-R1` @ `G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R1-zcode`
- 入口文档：`verification/M2-SFX-ANNOTATE-R1/stage2-report.md`（rev3，含全部数字与内部复算记录）+
  `stage2-final-summary.json`（机器可读摘要+产物 sha256）；阶段一背景见 stage1-report.md 与
  stage1 handoff
- 数据复算入口（审查建议路径）：`training_data/sfx-v1/annotate-r1/judgments/`（判定原始数据）→
  `final/manifest.*.json`（三集）→ `final/yolo/`（导出物）；python 用
  `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe`
- 接收者（DSH）需做的检查：①stage2-report.md §3 双审统计与 judgments/ 原始数据对账；
  ②§4 三集数字与 manifest 对账+组隔离复核；③§5 names/labels 校验复跑；④AC3 AI 代审偏离
  （human_review=false、GT 性质=ai-consensus）是否按编排裁定放行；⑤challenge/BJ 空集与
  承诺缺口（BJ 15/25、KO 10/15）登记是否如实

## 下一任务建议（必填）

- Task ID / 标题：M2-SFX-ANNOTATE-R1 **集成收口**（编排/ZCode 代行 Codex；r2 已明示无需再开 DSH 轮）
- 推荐 Agent / Reviewer：DeepSeek Harness（非作者，协作协议要求）
- 推荐原因与前置依赖：Task 已置 in_review；前置=本 Handoff + stage2-report.md rev2 已入库
- Recovery point：仓库 `G:/CODEX/New Manga`，branch `agent/zcode/M2-SFX-ANNOTATE-R1`，
  base @1b765007，delivery_head @7273c2d1 + 本文档提交；本 worktree 现成
- 允许修改路径：审查报告落 `verification/M2-SFX-ANNOTATE-R1/`（review 文档）；不改动数据本体与工具
- 禁止范围与新增授权条件：同合同禁止范围（src/tests/contracts/packaging/apps/STATUS）；审查不通过
  的 rework 由 ZCode 在同分支执行
- 交付物：REVIEW 报告（沿 doc/templates/REVIEW.md，引用实际文件与 commit）
- 验证命令、环境与完成 Gate：见「接收方式」检查清单；Gate=DSH r1 结论（approved / approved_with_conditions /
  changes_requested），条件项闭环后交编排会话集成
- 可直接转发给 Agent 的指令：
  > 在 worktree G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R1-zcode 审查 M2-SFX-ANNOTATE-R1
  > 阶段二（delivery_head 7273c2d1 + stage2-docs 提交）：读 doc/handoffs/M2-SFX-ANNOTATE-R1-zcode-stage2-20261004.md
  > 与 verification/M2-SFX-ANNOTATE-R1/stage2-report.md；对账三组数字——①judgments/ 双审分布
  > （codex 413=304/1/108、agy 413=297/3/113、共识 397+仲裁 16=413 无残留）②final/manifest.*.json
  > 三集（train 342/585、val 3/31、test 1/2、challenge 0/0 空集）+组隔离 0 违例+指纹 f9ea1c80…
  > ③final/yolo/ names 双通道+labels cls 恒 2+sha256 抽查。重点裁定：AC3 AI 代审偏离（human_review=false、
  > GT 性质=ai-consensus，用户 2026-10-04 裁决）与空集/缺口如实登记是否符合合同。按 REVIEW 模板出报告。

## 风险与遗留

1. **unresolved 残留清单**：`judgments/user-residual.json` 393 单元（conf<0.5 386 + ref 无 conf 7；
   按域 bj 11/replay-j 5/ko 305/ko-ogkalu-crop 72）+ 回放 5 页 pseudo——用户抽检/翻案/扩标通道，
   完成后重跑 `stage2_finalize.py --step manifest/split/yolo/summary` 即扩集，无需改工具。
2. **素材缺口补轮**：BJ 15/25 页（素材树仅 BJ01-15 在盘）、KO 10/15 页（K11-25 local_path 不存在），
   60 MISSING case 逐条登记于 `selection/selection.json`；BJ 域本轮正集=0、challenge 空集——
   需用户补素材后补轮（补轮顺带覆盖 correct 5 框 needs_fix 补框）。
3. **AI 代审偏离待审**：AC3 合同原文"用户逐条审核"，实际 AI 代审（编排裁定+用户裁决转移质量责任），
   DSH 审查需对此裁定放行与否表态；若翻案，user-residual 通道可回退到人工全审路径。
4. test 仅 1 组（K01，2 框）：统计功效有限（stage2-report.md §8.4），评估解读需连同 challenge 一起看。
5. synthetic 源树 `synthetic/*.png` 在 gitignored 外部树（324 张在盘已核对），若清理需先重跑
   AC5 合成步再导出。

## 实验附录（仅实验任务）

- 数据来源与许可：cases.json 在册素材（densho810/BJ、Vasyanator2/KO webtoon、Manga109、
  peppercarrot CC）；ogkalu 模型 apache-2.0；chiqui7=yolo11s-seg.onnx（T0 A′ 路线既有权重）
- 数据 Hash：manifest/worksheet/final 全量 sha256 见 `stage2-final-summary.json.artifacts_sha256`
  与 `stage1-manifest-summary.json`；三集指纹 `f9ea1c801e53f705c9ab68c1cac55ff736af926f64108bf71d2aa95af6009271`
- 模型/权重：chiqui7 imgsz=1024 conf@0.01 NMS IoU 0.7（生产序列）；ogkalu harvest 0.25（stage-1）
- Provider/Runtime：onnxruntime 1.30.0（C4-gpu-py312，stage-1 扫描）；阶段二纯 CPU
  （T1.1.1-impl-py312，无推理）
- 参数：split seed=20261004、group-hash-rank-v2、pinned synthetic/annotate-r1→train；
  YOLO seg 归一化 6 位小数 clip [0,1]、cls=2=sfx、包络多边形口径
- 运行次数：各一步（确定性管线，seed 冻结可复现）；失败样例：无（五步 EXIT=0）
- 限制：GT=ai-consensus 非人工；部分覆盖页未判定区域训练中作背景（既定噪声口径）；
  BJ 域承诺缺口

## r1 返修记录（2026-10-04，DSH approved_with_conditions → 本轮文档返修）

- **DSH r1 结论**：approved_with_conditions（0×P0、2×P1、3×P2、8×P3、5×P4）；完整报告全文因
  headless stdout 截断未保留，结论以最终输出（补充说明+结论重申）为准，纪要落
  `verification/M2-SFX-ANNOTATE-R1/dsh-r1-verdict-summary.md`。
- **本轮落实**：C1=stage2-report.md §8.1「A′ 采纳输入条件未满足」对照表（BJ 15/25、KO 10/15、
  **BJ 域正集 0**、challenge 空、回放未产正例）+T2 处置选项 (a)/(b)/(c) 交裁决；C2=用户裁决原文
  落档（Task AC3 修订注记+报告 §0）；C3=全文「独立复核/独立复算」→「内部复算」+rev3 措辞澄清；
  C4=回放 5 页目的偏差登记（§8.1）；C5=ai-consensus 证据强度上限声明（§0）。
- **编排代验补充**：agy 判定 413 行 id 唯一性校验 PASS（r1 补充说明 1 的数学闭包前提）。
- **未动**：数据本体、experiments 工具、零 src——纯文档/登记返修。
- **待 DSH r2**：复核 C1-C5 闭合+重列 P3/P4 明细（r1 全文截断项）。

## r2 复核记录（2026-10-04，approved_with_conditions，0×新 P0/P1/P2）

- **实质层全部自洽**（r2 独立重算：共识 397=294 confirm+103 delete、分歧 16 逐条、仲裁 16=confirm 3/correct 5/delete 8、回填 297/111/5、残留 393=262+7+124、三集 342/3/1/0、五指纹同值、names 逐字约束）——数字与导出物无新发现。
- **C1/C2/C4/C5 全闭**；C3 残项=Handoff 措辞（r1 返修脚本 git 还原重做时遗漏本文件），本轮收尾统一为「内部复算」。
- P3×8/P4×5（重列+新发现）全部文本级，本轮逐项落实：措辞统一、版本号 rev3、验证证据表回填、提交链/delivery_head 补齐、下一任务建议改集成收口、「穯集」错字、§8.1 承诺列标注推定性质、纪要括注标注、agy id 校验留证 raw/、units.json 代理复算口径注记。
- **r2 明示：残项收尾后即可回填 integration_commit 进 done，无需再开 DSH 复审。**
- r2 结论纪要：`verification/M2-SFX-ANNOTATE-R1/dsh-r2-verdict-summary.md`。
