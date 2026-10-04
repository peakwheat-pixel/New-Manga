---
id: M2-SFX-ANNOTATE-R1
title: "SFX 标注轮 R1：AI 预标注+用户审核工作表+三集隔离产出（T1b 两阶段；阶段二含用户逐条审核）"
kind: feature
status: done
owner_claim: 2026-10-04 14:55 +0800 by zcode subagent @1b765007（stage-1：AC1+AC2；AC3-AC5 阶段二停点后）
approval: user_ruling_2026-10-04_释放T1b_T5b_T5c
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
integration_commit: 由编排会话 merge 后回填至 main（merge of a14fce36）
depends_on: [M2-SFX-FINETUNE-PREFLIGHT, M2-SFX-DATA-INFRA]
base_commit: 69321db7
branch: agent/zcode/M2-SFX-ANNOTATE-R1
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R1-zcode
integration_commit: null
---

# M2-SFX-ANNOTATE-R1：SFX 标注轮 R1（T1b，两阶段）

## 来源与目标

A′ 路线裁决（T0 收口）的采纳输入条件=「T1b 承诺最小标注量」；本 Task 交付 V1 训练的全部人用数据。**两阶段**：阶段一（agent 自动）=预标注+审核工作表导出→**WAITING_USER_LABELING 停点**；阶段二（用户逐条审核后）=裁决回填+三集产出+训练就绪 manifest。沿 M2-DOCTR-QUAL-C1 混合判定先例（AI 预判预填+用户逐条审核+user_rationale 列）。

## 标注量承诺（AC 前置，A′ 采纳条件）

真实页标注：**BJ 域 ≥25 页 + KO 域 ≥15 页**（SFX 框目标 300-600）；合成样本 ≥200（程序渲染零人工，T1a 管线批量）。域内回放：BJ06+J 系 sfx 页 ≥5 页（防灾难性遗忘）。

> **A′ 采纳输入条件未满足（DSH r1 C1，2026-10-04，交编排/用户裁决——T2 释放前置）**：本轮交付后
> BJ 15/25 页、KO 10/15 页、**BJ 域正集=0**（主攻毛笔竖排形态零真实正样本）、challenge 空集、
> 回放 5 页未产正例——详见 stage2-report.md §8.1 对照表与处置选项 (a)/(b)/(c)。
> 合成 324/≥200 为唯一满足项。

## Acceptance Criteria

> 集成收口统一勾选（2026-10-04，DSH r2 后集成）：AC1-AC6 全 PASS（AC3=PASS WITH DEVIATION AI 代审已裁决登记）。

- [x] AC1 预标注（阶段一）：三源合并草稿——①chiqui7 低 conf dump（复用 DOMAIN-EXT L1 九档 raw：BJ13/14/15/BJ06 现成）②ogkalu text/panel 类候选（SFX 位置先验）③既有 pseudo 43 region+7 参照框。全部标 `pseudo` 入 T1a schema。
- [x] AC2 审核工作表导出（阶段一）：沿 C1 形态——每候选预览裁切图+页级清单（AI 预判列/用户裁决列/user_rationale 列）；页面选取：BJ SFX 密集页 ≥25、KO ≥15、域内回放 ≥5（cases.json source 组内选取，seed 冻结）；工具+预览产物齐备后**停点**，回报用户预估审核量（框数×页数）。
- [x] AC3 用户审核（阶段二，WAITING_USER_LABELING 解除后）：用户逐条裁决（确认/修正/删除+漏标补画）；user_rationale 留痕；审核完成标注状态 pseudo→complete（修正行记 revision 链）。
  **判据修订（2026-10-04，DSH r1 C2 落档）**：用户裁决原文"T1b交给codex和antigravity同时进行审核，
  减少人工工作量"——AC3 执行形态由"用户逐条裁决"修订为"codex+agy 双 AI 交叉审核+分歧第三方仲裁，
  共识∪仲裁=全覆盖，`human_review=false` 保真不谎称人工，残留/翻案走 user-residual.json 交用户"。
- [x] AC4 三集产出（阶段二）：经 T1a 拆分器组隔离（作品组不跨集、test 对训练不可见）→train/val/test+challenge(BJ13/14/15) manifest+sha256；**YOLO seg 训练格式导出**（dataset.yaml names 顺序逐字=SFX_CLASS_MAP——T0 P3-6 硬约束；多边形 mask 沿 T1a 包络口径）。
- [x] AC5 合成批量（阶段二）：T1a 渲染管线 ≥200 样本（毛笔体/艺术字字体×旋转/透视/弯曲/遮挡参数网格），标 synthetic 入 train/val 不入 test。
- [x] AC6 零 src；数据本体外部树，Git 只进 manifest 摘要。

## 允许修改范围

`experiments/M2-SFX-ANNOTATE-R1/**`、`verification/M2-SFX-ANNOTATE-R1/**`、Task/Handoff、`training_data/sfx-v1/**`（gitignored 外部树）。

## 禁止范围

`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`、`test_assets/**` 既有 manifest。

## 测试要求

| 场景/AC | 计划步骤 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1-AC2（阶段一） | 预标注跑通+工作表导出+审核量预估 | dev venv+图像本地 | **PASS（2026-10-04 stage-1）**：scan/assemble/worksheet 三步 EXIT=0；T1a schema 全量校验 0 错误；预览三张人工目检符合预期 | verification/M2-SFX-ANNOTATE-R1/stage1-report.md；training_data/sfx-v1/annotate-r1/{preannotate,selection,worksheet,previews,scan}；Git 内摘要 stage1-manifest-summary.json |
| AC3 | 用户逐条审核（真实人工） | 用户介入 | **PASS WITH DEVIATION（2026-10-04 stage-2，编排裁定 AI 代审；GT 性质=ai-consensus，用户裁决转移质量责任，`human_review=false` 不谎称人工）**：codex 判 413 单元（confirm 304/correct 1/delete 108）、agy 判 413 单元（confirm 297/correct 3/delete 113）——共识 397 单元 + 分歧仲裁 16 单元，共识∪分歧=413 **无未决残留（残留=0）**，conf>=0.5 全部 413 单元回填 worksheet（`reviewer=…`+rationale 全文留痕）；verdict=confirm 297/delete 111/correct 5（correct 框 revision 链留痕、坐标未动）；806−413=393 未判定单元（conf<0.5+ref 无 conf）+ 回放 5 页保持 pseudo → `judgments/user-residual.json` 交用户扩标 | training_data/sfx-v1/annotate-r1/worksheet/worksheet.{json,md}（backfill 块）；judgments/{codex,agy}/batch-*.json + consensus/divergence/arbiter（原始判定，文档收尾轮内部复算逐数一致）；judgments/user-residual.json；verification/M2-SFX-ANNOTATE-R1/stage2-report.md §0/§3 |
| AC4 | 拆分+YOLO 导出+names 校验 | AC3 完成 | **PASS（2026-10-04 stage-2）**：T1a assign_splits 组隔离（组不跨集内部复算 0 违例 + seed=20261004 冻结 + 五份 manifest 指纹同值 f9ea1c80…9271）→ train 342 样本 585 框（18 真实 261 框+324 合成）/val 3 样本 31 框（组 651664/701535）/test 1 样本 2 框（K01，组 724815，对 TrainingSetBuilder 不可见）/challenge 空集如实登记（BJ13 唯一判定=delete、BJ14/15 无判定，不凑数；manifest.challenge.json sample_count=0+note，dataset.yaml 不写 challenge 键）；YOLO seg 导出 names 顺序逐字=SFX_CLASS_MAP 双通道校验 PASS（脚本读回断言 stage2_finalize.py:572 ≡ 生产 detection_sfx.py:436 形态 + pyyaml 独立解析，真独立第二通道保留）；labels 内部重算 train 585/val 31/test 2 行全部 cls=2、坐标∈[0,1]、多边形≥4 点、stem 0 失配；图像 sha256 抽查（synth 1+K 页 3）三方一致 | training_data/sfx-v1/annotate-r1/final/{manifest.*.json,yolo/}；verification/M2-SFX-ANNOTATE-R1/stage2-report.md §4/§5；Git 内摘要 stage2-final-summary.json |
| AC5 | 合成批量（阶段二） | — | **PASS（2026-10-04 stage-2 并入）**：synthetic 324 样本（≥200 承诺达成，e85c546a）读 manifest 并入，pinned `synthetic/annotate-r1`→train 全落 train，`in_test=0` 断言通过 | training_data/sfx-v1/annotate-r1/synthetic/manifest.json；final/manifest.train.json；stage2-report.md §6 |
| AC6 | 零 src+数据外部树 | — | **PASS（2026-10-04 stage-1+stage-2 全链）**：`git diff 1b765007..HEAD -- src/ tests/` 零变更（生产 SFX_CLASS_MAP detection_sfx.py:137 只读 import、T1a schema/atomicio/splits/TrainingSetBuilder 只读复用）；数据本体 gitignored `training_data/sfx-v1/annotate-r1/`，Git 只进摘要（stage1-manifest-summary.json、synthetic-summary.json、stage2-final-summary.json，含产物 sha256） | Git 提交链 79e8dfad/e85c546a/7273c2d1；stage2-final-summary.json artifacts_sha256 |

## 依赖、风险与阻塞

depends_on 已 done。阻塞点=阶段二等用户审核（预估 1-2 小时级，阶段一回报精确数字）。风险：BJ 域页 SFX 密度不均→阶段一选取时按框数报告再定终集。

**阶段一实测回报（2026-10-04）**：全量 806 单元（bj=20/ko=613/replay-j=6/ogkalu=167）按 C1 实测速率（1-2 分钟/单元，doc/tasks/M2-DOCTR-QUAL-C1.md:25）估 13.4-26.9 小时，超出合同预估一个量级——主因 chiqui7 对 KO 域 conf@0.01 检出 613 框；用户可在停点按 conf 分层/域优先裁定审核范围。标注量承诺缺口：BJ 15/25 页（素材树仅 BJ01-15 在盘）、KO 10/15 页（K11-25 的 local_path 路径不存在），60 MISSING case 逐条登记于 selection.json，不凑数；缺口需素材扩充后补轮。

## 交付与运行记录

- **阶段一（2026-10-04，stage-1）**：AC1+AC2 交付，claim fe62677e。三源预标注合并（chiqui7 L1+新扫 / ogkalu 43 region / BJ06+l3 参照框；跨源 IoU≥0.5 去重，全部 pseudo，72 样本 806 框）；页面选取 seed=20261004 冻结（BJ 15 页全选+KO 10 页全选+回放 BJ06+J38/J41/J43/J51）；审核工作表（806 单元×20% 边距裁切预览 808 张+JSON/md 清单，AI 预判列预填/用户裁决列与 user_rationale 列留空，沿 C1 先例）。工具 `experiments/M2-SFX-ANNOTATE-R1/stage1_preannotate.py`（scan/assemble/worksheet，零 src 复用 T1a schema/importers/splits 与 DOMAIN-EXT 生产推理序列）。数据本体 gitignored `training_data/sfx-v1/annotate-r1/`；Git 内摘要 `verification/M2-SFX-ANNOTATE-R1/stage1-manifest-summary.json`。**状态：WAITING_USER_LABELING 停点**——AC3-AC5（阶段二）待用户完成逐条审核并裁定审核范围后释放。
- **阶段二（2026-10-04，stage-2；finalize @7273c2d1 + stage2-docs 修订轮）**：AC3 回填+AC4 三集+AC5 并入交付。**编排裁定：AC3 以 AI 代审落地，GT 性质=ai-consensus（用户 2026-10-04 裁决转移质量责任）**——codex 判 413 单元（confirm 304/correct 1/delete 108）、agy 判 413 单元（confirm 297/correct 3/delete 113），共识 397+分歧仲裁 16，共识∪分歧=413 **无未决残留（残留=0）**；`human_review=false` 全量留痕，不谎称人工；806−413=393 未判定单元+回放 5 页保持 pseudo 交用户扩标。回填 worksheet 413 单元（confirm 297/delete 111/correct 5，correct 框 revision 链留痕）；manifest 22 样本 pseudo→complete（294 正集框，delete/unjudged 全文留痕于 provenance.stage2）；T1a 拆分器组隔离（组不跨集复核 0 违例，seed 冻结，五份 manifest 指纹同值 f9ea1c80…9271）→train 342/585（324 合成 pinned train + 18 真实）/val 3/31/test 1/2/challenge 空集如实登记；YOLO seg 导出 names 逐字=SFX_CLASS_MAP 双通道校验 PASS、labels cls 恒 2、图像 sha256 抽查三方一致（stage2-docs 修订轮全部内部复算）。工具 `experiments/M2-SFX-ANNOTATE-R1/stage2_finalize.py`（backfill/manifest/split/yolo/summary 五步，零 src 复用 T1a schema/atomicio/splits/TrainingSetBuilder 与生产 SFX_CLASS_MAP 只读 import）。数据本体 gitignored `training_data/sfx-v1/annotate-r1/final/`；Git 内摘要 `verification/M2-SFX-ANNOTATE-R1/stage2-final-summary.json`；报告 `stage2-report.md`（rev3）。**已知边界**：BJ 域正集 0（BJ06 属回放排除、BJ13 唯一判定=delete、其余页 conf<0.5 未判定）；challenge 空集；test 仅 1 组；标注量承诺缺口 BJ 15/25 页+KO 10/15 页（见「依赖、风险与阻塞」节，素材扩充后补轮）——均不凑数，扩素材+用户扩标后重跑 split/yolo 即扩集。
- Handoff：doc/handoffs/M2-SFX-ANNOTATE-R1-zcode-stage1-20261004.md（阶段一+停点）；doc/handoffs/M2-SFX-ANNOTATE-R1-zcode-stage2-20261004.md（阶段二全链+DSH 审查入口与可转发指令）。
- Review：**DSH r1（2026-10-04）=approved_with_conditions（0×P0、2×P1、3×P2、8×P3、5×P4）**——必闭条件 C1（A′ 输入条件未满足显式登记+交裁决）、C2（AI 代审用户裁决原文落档+AC3 判据修订）与 C3-C5（措辞边界/回放偏差/证据强度上限）已在返修 commit 全部落实（纯文档，零 src 零数据本体）；P3×8/P4×5 明细因 DSH headless 输出截断未保留全文，DSH r2 复核时重列。编排代验补充：agy 413 行 id 唯一性校验 PASS（r1 边界说明 1 的数学闭包前提钉死）。**DSH r2（2026-10-04）=approved_with_conditions（0×新 P0/P1/P2；C1/C2/C4/C5 全闭、C3 残项文本级收尾；实质层数字 r2 独立重算全部自洽；明示无需再开 DSH 轮）——文本级收尾后交编排集成收口。**
