---
id: M2-SFX-ANNOTATE-R1
title: "SFX 标注轮 R1：AI 预标注+用户审核工作表+三集隔离产出（T1b 两阶段；阶段二含用户逐条审核）"
kind: feature
status: ready
approval: user_ruling_2026-10-04_释放T1b_T5b_T5c
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
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

## Acceptance Criteria

- [ ] AC1 预标注（阶段一）：三源合并草稿——①chiqui7 低 conf dump（复用 DOMAIN-EXT L1 九档 raw：BJ13/14/15/BJ06 现成）②ogkalu text/panel 类候选（SFX 位置先验）③既有 pseudo 43 region+7 参照框。全部标 `pseudo` 入 T1a schema。
- [ ] AC2 审核工作表导出（阶段一）：沿 C1 形态——每候选预览裁切图+页级清单（AI 预判列/用户裁决列/user_rationale 列）；页面选取：BJ SFX 密集页 ≥25、KO ≥15、域内回放 ≥5（cases.json source 组内选取，seed 冻结）；工具+预览产物齐备后**停点**，回报用户预估审核量（框数×页数）。
- [ ] AC3 用户审核（阶段二，WAITING_USER_LABELING 解除后）：用户逐条裁决（确认/修正/删除+漏标补画）；user_rationale 留痕；审核完成标注状态 pseudo→complete（修正行记 revision 链）。
- [ ] AC4 三集产出（阶段二）：经 T1a 拆分器组隔离（作品组不跨集、test 对训练不可见）→train/val/test+challenge(BJ13/14/15) manifest+sha256；**YOLO seg 训练格式导出**（dataset.yaml names 顺序逐字=SFX_CLASS_MAP——T0 P3-6 硬约束；多边形 mask 沿 T1a 包络口径）。
- [ ] AC5 合成批量（阶段二）：T1a 渲染管线 ≥200 样本（毛笔体/艺术字字体×旋转/透视/弯曲/遮挡参数网格），标 synthetic 入 train/val 不入 test。
- [ ] AC6 零 src；数据本体外部树，Git 只进 manifest 摘要。

## 允许修改范围

`experiments/M2-SFX-ANNOTATE-R1/**`、`verification/M2-SFX-ANNOTATE-R1/**`、Task/Handoff、`training_data/sfx-v1/**`（gitignored 外部树）。

## 禁止范围

`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`、`test_assets/**` 既有 manifest。

## 测试要求

| 场景/AC | 计划步骤 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1-AC2 | 预标注跑通+工作表导出+审核量预估 | dev venv+图像本地 | NOT_RUN | 无 |
| AC3 | 用户逐条审核（真实人工） | 用户介入 | NOT_RUN/BLOCKED_ON_USER | 无 |
| AC4 | 拆分+YOLO 导出+names 校验 | AC3 完成 | NOT_RUN | 无 |

## 依赖、风险与阻塞

depends_on 已 done。阻塞点=阶段二等用户审核（预估 1-2 小时级，阶段一回报精确数字）。风险：BJ 域页 SFX 密度不均→阶段一选取时按框数报告再定终集。

## 交付与运行记录

- Handoff：尚无。Review：阶段二交付后一并 DSH 审查（阶段一交付+停点登记即可先报）。
