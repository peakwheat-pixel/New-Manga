---
id: M2-SFX-GATE-T3
title: "SFX 正式评测门 T3：Gate 定义冻结（G1-G8）+双前置数据（R3-MISS 补画/KO 非派生 GT）+三方评测执行+判定与 T4 材料"
kind: feature
status: done
owner_claim: ZCode @b35536af（2026-10-05，DSH r1 条件+r2 N1-N5 全闭终态；评测执行 head=2e95760a）
approval: user_ruling_2026-10-05_按推荐_T3释放
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
integration_commit: 27817412（merge into main，2026-10-05）
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

- [x] AC1 Gate 定义冻结（G1-G8 权威化，含 BJ/KO/损害/部署门）@`907011a2` gate-definition.md v1.0-frozen
- [x] AC2 R3-MISS 补画（AI 直接标注新形态+manifest r4+train-v4）@`3c84f438`（BJ32-35 转正 15 框，BJ36/37 终裁 0 框如实）
- [x] AC3 KO 非派生考题（隔离纪律+偏差统计）@`3c84f438`（npd GT 135 框，task_brief_leak_check=PASS，交集 40/差集 16+95）
- [x] AC4 三方×四数据集正式评测 @`2e95760a`（36 格全落盘，复算 ALL CELLS == eval-matrix.json）
- [x] AC5 Gate 判定+T4 材料终稿 @本 docs 提交（gate-t3-report.md：G1-G8 逐门判定+T4 终稿）
- [x] AC6 零 src；数据 gitignored；Git 只进摘要（26 文件（HEAD=2e95760a 时点）+2 docs（AC5 轮：gate-t3-report.md+本 Handoff/Task 回填）全在允许路径实测；pin `d87389af…` 零改动）

## 允许修改范围

`experiments/M2-SFX-GATE-T3/**`（新建）、`verification/M2-SFX-GATE-T3/**`、本 Task/Handoff、`training_data/sfx-v1/{annotate-r4,train-v4,gate-t3}/**`（gitignored）、`doc/reviews/M2-SFX-GATE-T3-*.md`。

## 禁止范围

`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`、生产 pin、R1-R3/V1/V2 数据与脚本本体（只读引用）、cases.json（本轮无新页入池）、考卷 vol05 组定义。

## 依赖、风险与阻塞

- depends_on 全 done。风险：①AI 直接标注（无模型预标）是首例——标注质量依赖视觉能力，双 AI 独立+比对仲裁兜底，产量如实；②Gate 定义的前瞻性不足风险——定义阶段引用全部既有实测材料，冻结机制防漂移；③评测结论可能 FAIL——如实判定即为本 Task 成功（Gate 不是橡皮图章）；④KO 非派生 GT 与派生 GT 的差集可能大——这正是要度量的对象。
- 裁量点：G1-G8 具体门数可按 preflight 事实增删（登记理由）；BJ 扩展考卷的构成。

## 交付与运行记录

- Owner=ZCode；分支 `agent/zcode/M2-SFX-GATE-T3`，base=`87ca8724`，worktree `G:/CODEX/New Manga.worktrees/M2-SFX-GATE-T3-zcode`。
  交付链：`907011a2`（AC1 Gate 定义冻结 v1.0-frozen：G1-G8 合同级权威化+冻结声明/变更登记规则；全部行号本 worktree 直验）→ `3c84f438`（AC2 后半+AC3 后半：R4 比对仲裁入册 BJ32-35 转正 15 框/BJ36-37 终裁 0 框如实+npd 非派生 GT 135 框定稿+train-v4 重切 916 全量，9 断言落盘复算全 PASS）→ `2e95760a`（AC4 正式评测：三方 chiqui7 pin 原样/v2a `27d162e9…`/v2b `944e8114…` 进程内重指 ×四数据集 bj-exam 5 框/bj-ext 12 页 33 框/ko-tile 56 框/ko-npd 135 框，conf0.5 主+0.2 诊断，36 格含 12 letterbox 对照格全落盘）→ docs（AC5：判定报告+Handoff+本回填）。
- **AC5 逐门判定**（[gate-t3-report.md](../../verification/M2-SFX-GATE-T3/gate-t3-report.md)，依据 gate-definition v1.0 §4，FAIL 如实）：G3 先决 PASS（9/9）；**G1：v2a FAIL（P 0.8<基线 0.8333）/v2b PASS（5/5 P=1.0）**；**G2：v2a FAIL（KO-B 0.2593<0.3037）/v2b PASS（0.3556≥0.3037；口径合规两候选均过，letterbox 对照 12 格全零复现）**；G4/G6 directional 登记（覆盖矩阵含「考卷对新回填形态零覆盖」原样入表/四层归因含 own-manga 418 自蒸馏框不同权）；G5 双候选 PASS 5/5（①SHA 门 PROVIDER_FAILED 引用 V2 当轮证据 export-smoke-v2.json 显式收编——T3 当轮未复跑，观察①）；**G7 PASS（条件性：T4 补证前置）**——冻结口径=T0/V2 冒烟方式（边界=检测契约面，编排裁决 2026-10-05 已确认），翻译链深层调用未以新权重执行，T4 部署前必须补跑 BJ06 型 policy=translate 端到端冒烟，未补证前不得把 G7 记为部署就绪；G8 **v2b 7/7 出证 PASS——license:other 审计本门执行=PASS 附登记义务（Manga109-s 衍生声明核验逐字在位+本地衍生未分发范围成立；分发场景须复核）**，v2a 已因 G1/G2 丧失候选资格。
- **候选资格结论**：v2b（best.onnx `944e8114…`）=唯一通过全部定资格硬门（G1/G2/G5/G8）+G7 条件性（同约束不改变结论）的切换候选；切换与否=T4 用户裁决点。T4 终稿四件齐：切换候选建议（附 KO 改善=0/bj-ext 泛化未证/低功效三条件）+许可审计结算+生产 tile 化方案（G2 冻结口径实现+性能实测 17-81s/页@CPU 须预算裁决+相位依赖）+回退方案（pin 恢复 `d87389af…`+NSIS 通道不动）。
- 验证：`verify_data_integrity.py` 9/9 PASS（AC5 轮复跑，复算后与提交版逐位一致）；`recompute_eval_t3.py` ALL CELLS RECOMPUTED（AC5 轮复跑 EXIT=0）；三权重 sha256 AC5 轮盘上重算与 pin/矩阵一致；零 src 实测（26 文件（HEAD=2e95760a 时点）+2 docs（AC5 轮）全在允许路径，src/tests/contracts/packaging/apps/doc/STATUS.md diff=0）。AC4 后作者侧复核=PASS 六项（含 2 条非阻断观察，报告 §5 原样登记；正式独立 Review=DSH r1）。
- 诚实边界：AI 直接标注首例/非派生 GT=ai-consensus 非人工/统计功效低（5 框量级禁用「显著」）/GT 循环性（chiqui7 5/5、56/56=自洽上界）——报告 §6。

## 集成记录（2026-10-05，编排会话代行 Codex）

- **DSH r1**（审查对象 head=e53a2629，报告落盘 `doc/reviews/M2-SFX-GATE-T3-e53a2629-dsh-r1.md`）：approved_with_conditions（P0=0/P1=1/P2=3/P3=5/P4=4）；36 格矩阵/逐页求和/交叉核对静态逐值一致，数字层零发现。
- **Owner 返修**：r1 条件 commit `32fa3bab`（P1-1/P2-1/P2-2/P2-3/P3/P4 全闭）；DSH r2 定点复核（报告落盘 `doc/reviews/M2-SFX-GATE-T3-32fa3bab-dsh-r2.md`）=**条件全闭建议集成**（12/12 通过；P2-2 v1.1 经全文逐行核对确认 §5.3 追加式成立；P3-2 tile 口径运行期断言按 r1 定位转 T4 承接；N1-N5 为编辑性问题）。
- **N1-N5 修正**：commit `b35536af`（行号引用对齐/v1.0 段零修改措辞限定/裁决登记位置表述/候选资格措辞统一/diff 声称精度）。
- **集成 Gate（编排实测）**：`git diff --name-only 87ca8724..b35536af`=28 文件全在允许路径（doc/handoffs 1+doc/tasks 1+experiments 8+verification 18）；`detection_sfx.py` pin（SFX_HF_REVISION=7f5f5c04…/SFX_WEIGHTS_SHA256=d87389af…）base..HEAD 逐字一致；`verify_data_integrity.py` 复跑 9/9 PASS EXIT=0；`recompute_eval_t3.py` 复跑 ALL CELLS RECOMPUTED EXIT=0；复跑后 data-integrity-asserts.json git diff 空。
- **编排裁决登记（r1 Q1）**：接受「G7 冻结口径边界=检测契约面」——G7=PASS（条件性：T4 补证前置），T4 部署前必须以新权重补跑 BJ06 型 policy=translate 端到端冒烟；裁决依据=gate-definition §4.G7 口径原文「沿 T0/V2 冒烟方式」+报告执行边界如实披露。

## Review 返修记录（review-fix(GATE-T3 r1)，2026-10-05）

DSH r1（非作者，只读）结论=**approved_with_conditions**（P0=0/P1=1/P2=3/P3=5/P4=4）。编排裁决（2026-10-05，登记于此代替 review_events 回填）：**Q1/G7 接受「冻结口径边界=检测契约面」**——G7 改标「PASS（条件性：T4 补证前置）」，条件=T4 部署前必须以新权重补跑一次 BJ06 型 policy=translate 端到端冒烟（run_qualification 级深层调用），未补证前不得把 G7 记为部署就绪；候选资格结论不变（v2b 由 G1/G2/G5/G8 定资格）。逐项处置：

- **P1-1**：报告 §0 速览/§4.7/§6-5/§7.4-①/§7.1+本 Task+Handoff 的 G7 同步改标条件性 PASS（条件文本写入报告 §4.7）。
- **P2-1**：AC3 51 单元仲裁终裁导出独立档案 `training_data/sfx-v1/gate-t3/npd-judgments/arbiter/batch-1.json`（与 AC2 `annotate-r4/judgments/arbiter/batch-1.json` 同构）+`finalize_npd.py` 改为读取该档案并逐单元断言（对齐 `stage_r4_manifest.py:52/67-68` 模式）+`divergence.json` arbiter 指针修正为 `npd-judgments/arbiter/batch-1.json`。重跑验证：npd-gt.json 除 generated_at_utc/divergence.json arbitrated_at_utc 时间戳与 P4-4 coincidence_evidence 措辞外逐位不变（135 框坐标/rationale/chain/verdict_dist/crosscheck 56/135/40/16/95 逐位）；`verify_data_integrity.py` 9/9 PASS 且 `data-integrity-asserts.json` 与提交版 git diff 为空；`recompute_eval_t3.py` ALL CELLS RECOMPUTED。
- **P2-2**：gate-definition.md §6 追加**不回溯**版本行 v1.1（challenge 成员随 vol05 组转正扩展为 pre-bj17/pre-bj18/pre-bj32 三页 8 框，组隔离优先于 ask「钉 train」表述；**G1 判据集不变=原始 5 框**，S4 original_5box_bitwise_r2 断言保持）+§4.G3 措辞修正——**待 DSH 确认**。
- **P2-3**：报告 §5 改称「作者侧复核（workflow 内 phase 5，非本 Task 正式独立 Review）」；「preds 整数占比 12.8%」标注（过程观察，未舍入坐标未落盘，不可复算）；「独立脚本重算」→「作者侧脚本重算」。
- **P3-1/P3-3/P3-4/P3-5**：报告 §4.5-1 补「收编证据 sha 与被测 sha 逐字相同」收编合法性依据；§4.8-4 credit 义务改保守登记（公布衍生权重/结果则触发 citation 义务，README :91，当前未分发场景不触发）；§8 证据索引补 `arb_previews_npd.py`（共 8 脚本）；本 Task/Handoff「26 文件」改述为「26 文件（HEAD=2e95760a 时点）+2 docs」。
- **P4-1/P4-2/P4-3/P4-4**：「逐位=R2 出厂」统一为「逐值（0.1 精度）等值」（比较逻辑零改动）；`prepare_dataset_v4.py:72` 开发期核算注释删除；Handoff/报告 export-smoke-v2.json 行号引用统一为「sha_gate.fired=:38-43/:122-127，sha_gate.ok=:44-50/:128-134」；npd-gt.json coincidence_evidence 改双向表述（客观性旁证/泄漏信号双向解释、决定性不足，隔离判定以 task_brief_leak_check+产物级间接验证为准）。
