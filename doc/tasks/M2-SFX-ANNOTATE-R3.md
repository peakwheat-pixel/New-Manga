---
id: M2-SFX-ANNOTATE-R3
title: "SFX 标注轮 R3（T1b-R3 扩标轮）：BJ 候选池 44 页选页入池+低置信扩审+正集扩容"
kind: feature
status: ready
owner_claim: —
approval: user_ruling_2026-10-05_按推荐_T3释放
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
depends_on: [M2-SFX-ANNOTATE-R2, M2-SFX-DATA-INFRA]
base_commit: 9258afc0
branch: agent/zcode/M2-SFX-ANNOTATE-R3
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R3-zcode
review_events: []
created: 2026-10-05
---

# Task: M2-SFX-ANNOTATE-R3 — BJ 扩标轮 R3

## 背景与目标

V2 已实证「数据进来模型就学会」（BJ 考卷 V1 0/5→V2B 5/5）。BJ 主攻形态（毛笔竖排）正样本现仅 6 框（train 侧 BJ16×3+BJ23×2+BJ24×1）+考卷 5 框。本 Task 把 BJ 域正样本扩到几十框量级，为 T3 正式 Gate 备数据。

**候选池（已核实）**：R2 素材根 54 张渲染页中 44 张未入池（vol01 16/vol03 15/vol05 13，`G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R2-zcode/test_assets/comic_golden_suite/日漫_JA/01_black_jack_official/volXX/pages/`，只读复制）；遗留低置信 16 单元（R2 worksheet-bj-new.json：BJ16×4/BJ17×2/BJ18×1/BJ19×3/BJ20×2/BJ21×2/BJ22×2，conf<0.2 无判定，预览图在 R2 previews/）。

## 交付物

- **AC1 选页入池**：44 张候选页跑 chiqui7 密度扫描（沿 R2 material_scan_density 口径，seed=20261004 决胜），选 top-12 入池登记 **BJ26-BJ37**（cases.json 纯追加，字段沿 BJ16-25 先例含 pixel_size；剩余 32 张留池）。chiqui7 对毛笔竖排弱（R2 实证密度排序仍有效但偏保守），密度并列时**人工/AI 目检毛笔形态优先**作为二次决胜（登记选页理由）。
- **AC2 预标注+扩审**：①新 12 页整页 letterbox 扫描预标注（沿 R2 stage1_preannotate_bj_new 模式，targeted；**不设 conf 门槛**——R2 教训=BJ 候选 conf 天然低，新页全部检出候选入审）②遗留 16 单元（R2 conf<0.2 层）直接入审③两部分合并写 units+批次文件（≤20/批）→**双 AI 交叉审核**（codex+agy 独立逐图判定→共识+分歧第三方仲裁，`human_review=false` 保真，判定标准沿 R2 JUDGE_STD 含毛笔竖排主攻形态说明）。
- **AC3 manifest v3+重切**：判定并入（R2 底册 82 样本只读+新页样本+遗留单元判定更新）→manifest.r3.json（T1a schema 全量校验）→train-v3 数据集重建（challenge=vol05 组不动、seed=20261004、names 双通道、组隔离 0 违例；**合成 324+own-manga 558 并入沿 V2 口径**→train 页级≈913+）。BJ 正集前后对照数字如实登记。
- **AC4 报告+Handoff+Task 回填**（含 T3 材料更新：BJ 正集量级、考卷是否需要随正集扩容重划——仅提案不裁决）。

## 验收判据

AC1：cases.json 只增不改（既有 110 条 byte 级/深度等值不变）+选页理由登记。
AC2：判定全量覆盖（共识∪仲裁=范围全量，残留=0）；判定链留痕；AI 代审裁决链沿 R1/R2 登记口径。
AC3：指纹复现+组隔离 0 违例+考卷 5 框不动断言+BJ 正集对照表（R2 5 页 11 框→R3 实测）。
AC4：三文档齐。

## Acceptance Criteria

- [ ] AC1 候选池密度选页 top-12 入池（BJ26-BJ37 纯追加）
- [ ] AC2 新页预标注（无 conf 门槛）+遗留 16 单元+双 AI 交叉审核
- [ ] AC3 manifest v3+train-v3 重切（考卷不动+own-manga/合成并入）
- [ ] AC4 报告+Handoff+Task 回填+T3 材料更新
- [ ] AC5 零 src；数据本体 gitignored；Git 只进摘要与 cases.json 追加

## 允许修改范围

`experiments/M2-SFX-ANNOTATE-R3/**`（新建）、`verification/M2-SFX-ANNOTATE-R3/**`、本 Task/Handoff、`training_data/sfx-v1/annotate-r3/**` 与 `training_data/sfx-v1/train-v3/**`（gitignored）、`test_assets/comic_golden_suite/manifests/cases.json`（**仅追加 BJ26-BJ37**）、`doc/reviews/M2-SFX-ANNOTATE-R3-*.md`。

## 禁止范围

`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`、cases.json 既有 110 条、R1/R2/V1/V2 数据与脚本本体（只读引用）、R2 素材根候选页（只读复制）、考卷 vol05 组。

## 依赖、风险与阻塞

- depends_on 全 done。风险：①BJ 候选页密度分布未知（未入池 44 张=密度 top-11~54 位，SFX 密度可能偏稀）——选页数 12 为裁量值可上下浮动（登记）；②低置信单元质量（chiqui7 弱项）——双 AI 审核兜底；③判定量≈30-60 单元，双审时间可控。
- 裁量点：选页数量、毛笔形态二次决胜的执行方式、新页候选全审的批次切分。

## 交付与运行记录

-（待 Owner 回填）
