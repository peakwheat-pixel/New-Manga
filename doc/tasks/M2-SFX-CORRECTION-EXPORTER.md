---
id: M2-SFX-CORRECTION-EXPORTER
title: "纠错样本导出器：revision 链扫描→训练样本资格判定→T1a schema 导出（T5c；命令式零生产写路径）"
kind: feature
status: ready
approval: user_ruling_2026-10-04_释放T1b_T5b_T5c
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
depends_on: [M2-SFX-DATA-INFRA, M2-REGION-RETYPE-CONTRACT]
base_commit: 69321db7
branch: agent/zcode/M2-SFX-CORRECTION-EXPORTER
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-CORRECTION-EXPORTER-zcode
integration_commit: null
---

# M2-SFX-CORRECTION-EXPORTER：纠错样本导出器（T5c）

## 来源与目标

纠错积累链的采集端（Codex 方案第 7 点）：用户在未来的改标 UI/流程中产生的类型纠错，经本导出器**命令式**转为训练样本。纪律：**训练样本资格判断留在导出阶段，生产编辑只可靠保存纠错事实**（Core 侧持久化归 T5b）；导出器只读 SQLite+写外部树，零生产写路径。

## Acceptance Criteria

- [ ] AC1 纠错事件识别：扫描 SQLite revision 链，提取**类型纠错事件**——按 rev 1.4 语义：①region 类型变化（跨 revision diff region_type）②撤销关系解析（RESTORED 链回溯最终有效状态，被撤销的纠错不入册）③**排除**纯几何/文本编辑/reading_order 变化（这些也产生 user revision 但非类型纠错——导出器不得把所有 origin=user 当纠错）。用 T5a 冻结的语义+T5b 交付后的真实链验证（T5b 未集成前用 fixture 构造 revision 链单测）。
- [ ] AC2 样本构建：纠错事件→T1a schema 样本（页面图引用+改标后类型的框/多边形+标注状态=complete[用户确认]或 partial[仅改标未确认几何]）+provenance=revision 链（region_id/revision_no/event 序列，可溯源可回放）。
- [ ] AC3 资格判定（导出阶段）：①来源许可标签继承（cases.json source→备案状态，按二次裁决全备案不阻断）②几何确认度门（无几何确认的改标标 partial，不入正集可选入辅助集——阈值冻结并登记）③去重（与 T1a 已册样本查重）。
- [ ] AC4 导出格式：T1a manifest+YOLO seg 导出双形态（与 T1b 产物同构，训练侧零适配）；输出外部树 training_data/sfx-corrections/，Git 只进摘要。
- [ ] AC5 零 src：只读 SQLite（复用 T1a 只读访问模式）；CLI 可运行（--help/selfcheck EXIT=0）；fixture 单测（构造含类型纠错/撤销/几何编辑混合的 revision 链，断言识别正确性先红后绿）。
- [ ] AC6 与 T1b 产物互操作：导出物可被 T1a 拆分器/训练集构建器直接消费（分组隔离规则继承）。

## 允许修改范围

`experiments/M2-SFX-CORRECTION-EXPORTER/**`、`verification/M2-SFX-CORRECTION-EXPORTER/**`、Task/Handoff、`training_data/sfx-corrections/**`（gitignored）。

## 禁止范围

`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`、SQLite 写路径（只读铁律）。

## 测试要求

| 场景/AC | 计划步骤 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 事件识别 | fixture 链（纠错+撤销+几何编辑混合）断言 | dev venv | NOT_RUN | 无 |
| AC5 CLI | --help/selfcheck | dev venv | NOT_RUN | 无 |
| AC6 互操作 | 导出物过 T1a builder | 同上 | NOT_RUN | 无 |

## 依赖、风险与阻塞

depends_on 均 done（T5b 是运行时数据来源而非本 Task 硬依赖——fixture 先行，T5b 集成后跑一次真库冒烟登记）。风险：revision 链语义误读→单测 fixture 按 T5a 契约断言逐条构造，DSH review 核对。

## 交付与运行记录

- Handoff：尚无。Review：尚无。
