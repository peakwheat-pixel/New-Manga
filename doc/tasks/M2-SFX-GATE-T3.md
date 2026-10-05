---
id: M2-SFX-GATE-T3
title: "SFX 正式评测门 T3：Gate 定义冻结（G1-G8）+双前置数据（R3-MISS 补画/KO 非派生 GT）+三方评测执行+判定与 T4 材料"
kind: feature
status: ready
owner_claim: —
approval: user_ruling_2026-10-05_按推荐_T3释放
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
depends_on: [M2-SFX-TRAIN-V2, M2-KO-TILE-CALIB, M2-SFX-ANNOTATE-R3]
base_commit: 87ca8724
branch: agent/zcode/M2-SFX-GATE-T3
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-GATE-T3-zcode
review_events: []
created: 2026-10-05
---

# Task: M2-SFX-GATE-T3 — SFX 正式评测门

## 背景与目标

T2-V2（done）证明方向可行（BJ 考卷 0/5→5/5），T3 前置双 Task（done）备齐：KO 口径提案（tile_ov128 冻结+循环性限制）、BJ 正集 8 页 18 框、R3-MISS 立项建议、own-manga 归因分层。用户裁决（2026-10-05「按推荐」）释放 T3，捆绑两前置子项。

**T3 交付四层：Gate 定义冻结 → 前置数据 → 正式评测 → 判定与 T4 材料。**

## 交付物（阶段化）

- **AC1 Gate 定义冻结（G1-G8）**：G1-G8 此前仅存在于方案提案语境（STATUS 提及「含端到端损害门 G7/部署门 G8」），无合同级定义——**本 AC 即定义权威化**。逐门产出：定义/评测数据/口径/阈值/判定规则（PASS/FAIL/directional），写入 `gate-definition.md` 并冻结（评测执行后不得改；确需改走显式变更登记）。定义输入=T0 preflight 技术事实+V1/V2 实测+KO-TILE 口径提案+R3 成果。**必含**：BJ 门（毛笔竖排召回，考卷+扩展）、KO 门（tile 冻结口径+**非派生 GT 切片**——防采集一致性冒充模型质量）、端到端损害门（新权重经生产序列替换后 SFX→翻译链路无退化，进程内重指沿 T0/V2 冒烟方式零 src）、部署门（ONNX/权重/来源/许可审计清单——v2b license:other 审计前置在此结算）。方向性纪律沿 V1/V2（directional/禁用「显著」如实延续，正式门明确哪些门是硬 Gate 哪些是 directional 记录）。
- **AC2 R3-MISS 补画（BJ32-37 六页）**：六页目检确认含毛笔竖排但 chiqui7 零候选——**AI 直接看图补画候选（无模型预标，conf 概念不适用）**：两个 AI 独立看整页画 SFX 框（各自不看对方）→比对（IoU 匹配+分歧仲裁）→双 AI 共识框入册 manifest.r4（沿 R3 provenance.stage3r3 语义，`mode=ai-direct-annotation` 新口径如实登记——非「补记模型检出」，是首个无模型预标的标注形态）→train-v4 重切（考卷不动）。产出框数如实（0 也如实）。
- **AC3 KO 非派生考题**：KO 4 页（pre-k01/k02/k08/k09）由两个 AI **独立看整页画 SFX 框（严禁参考任何模型输出/预标注/既有 GT）**→比对仲裁→非派生 GT 切片（预期每页数个至十余个 SFX；与 chiqui7 派生 GT 56 框的交集/差集统计=KO 域「GT 偏差」的直接度量，写进评测）。**隔离纪律**：标注 agent 的任务书不得含任何既有框坐标。
- **AC4 正式评测执行**：候选权重 v2a/v2b（best.onnx）vs chiqui7 现役基线，三方×数据集：①BJ 考卷（vol05 组 5 框，letterbox 现行口径）②BJ 扩展（R3-MISS 补画后 BJ 域全部 complete 页）③KO tile 冻结口径（chiqui7 派生 GT 56 框——标注「采集一致性」属性）④KO 非派生切片（模型质量度量）。逐框明细+汇总矩阵；零 src。
- **AC5 Gate 判定+T4 材料终稿**：G1-G8 逐门 PASS/FAIL 判定（含 FAIL 如实）；**T4 生产切换建议终稿**（切换候选权重/许可审计结算/生产序列 tile 化方案/回退方案）；报告+Handoff+Task 回填。

## 验收判据

AC1：gate-definition.md 冻结+逐门可判定（数据/口径/阈值齐）。
AC2/AC3：标注隔离纪律实证（任务书无泄漏）；判定闭环；留痕全链。
AC4：三方×四数据集矩阵+逐框明细；复算脚本与 raw JSON 一致。
AC5：逐门判定如实（FAIL 如实）+T4 终稿。

## Acceptance Criteria

- [ ] AC1 Gate 定义冻结（G1-G8 权威化，含 BJ/KO/损害/部署门）
- [ ] AC2 R3-MISS 补画（AI 直接标注新形态+manifest r4+train-v4）
- [ ] AC3 KO 非派生考题（隔离纪律+偏差统计）
- [ ] AC4 三方×四数据集正式评测
- [ ] AC5 Gate 判定+T4 材料终稿
- [ ] AC6 零 src；数据 gitignored；Git 只进摘要

## 允许修改范围

`experiments/M2-SFX-GATE-T3/**`（新建）、`verification/M2-SFX-GATE-T3/**`、本 Task/Handoff、`training_data/sfx-v1/{annotate-r4,train-v4,gate-t3}/**`（gitignored）、`doc/reviews/M2-SFX-GATE-T3-*.md`。

## 禁止范围

`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`、生产 pin、R1-R3/V1/V2 数据与脚本本体（只读引用）、cases.json（本轮无新页入池）、考卷 vol05 组定义。

## 依赖、风险与阻塞

- depends_on 全 done。风险：①AI 直接标注（无模型预标）是首例——标注质量依赖视觉能力，双 AI 独立+比对仲裁兜底，产量如实；②Gate 定义的前瞻性不足风险——定义阶段引用全部既有实测材料，冻结机制防漂移；③评测结论可能 FAIL——如实判定即为本 Task 成功（Gate 不是橡皮图章）；④KO 非派生 GT 与派生 GT 的差集可能大——这正是要度量的对象。
- 裁量点：G1-G8 具体门数可按 preflight 事实增删（登记理由）；BJ 扩展考卷的构成。

## 交付与运行记录

-（待 Owner 回填）
