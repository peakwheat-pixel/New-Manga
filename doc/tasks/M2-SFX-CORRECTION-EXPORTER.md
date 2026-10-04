---
id: M2-SFX-CORRECTION-EXPORTER
title: "纠错样本导出器：revision 链扫描→训练样本资格判定→T1a schema 导出（T5c；命令式零生产写路径）"
kind: feature
status: in_review
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

> 注记（DSH r1 P3-5）：下列 AC 勾选状态为 **Owner 自评（PASS 结论来自
> verification/M2-SFX-CORRECTION-EXPORTER/exporter-report.md 的 AC 对照表），
> 待 Reviewer（DeepSeek Harness）确认后才算 Task 级验收**；r1=changes_requested
> 已按修订段处置，待 r2。

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
| AC1 事件识别 | fixture 链（纠错+撤销+几何编辑混合）断言 | dev venv T1.1.1-impl-py312 @ 9c7cf7bc + r1 返修（分支 tip） | PASS：15 region 矩阵 17 测试逐条断言；红态 5×ModuleNotFoundError→绿态 50/50（r1 返修重跑） | verification/M2-SFX-CORRECTION-EXPORTER/evidence/red-run.txt + green-run.txt |
| AC2 样本构建 | T1a schema 逐条 validate+provenance 链 trace | 同上 | PASS（7 测试，含 rgO bbox 语义判别） | 同上 green-run.txt |
| AC3 资格判定 | 许可继承/几何门/去重 | 同上 | PASS（9 测试；阈值冻结 eligibility.CONSTANTS） | 同上 |
| AC4 双形态导出 | manifest main+auxiliary + YOLO seg + dataset.yaml names 锚定 + --yolo-scope | 同上 | PASS（11 测试含确定性指纹与 yolo-scope main/all） | 同上 |
| AC5 CLI | --help/selfcheck/只读铁律 | 同上 | PASS：EXIT=0/0，selfcheck 6/6；UPDATE/DELETE 只读连接被拒 | evidence/selfcheck.txt |
| AC6 互操作 | 导出物过 T1a load_manifest+TrainingSetBuilder | 同上 | PASS（challenge 隔离+组原子性+SplitAccessError+注册表组继承） | green-run.txt |
| fixture 全流程冒烟 | fixture 库（生产 v1–v4 DDL）→ 导出 | 同上 | EXIT=0：14 region/36 rev→12 事件（8 存活/6 sfx 向）→ main2+aux4→train5+challenge1→YOLO main 2 labels（--yolo-scope 默认 main；all=6） | fixture-smoke-summary.json |
| 真库冒烟（空结果） | export --db 主仓库 library.db | 同上 | EXIT=0，CORRECTIONS_EMPTY=expected（T5b 未集成真库 0 region；集成后由集成方补跑） | real-db-smoke-summary.json |

## 依赖、风险与阻塞

depends_on 均 done（T5b 是运行时数据来源而非本 Task 硬依赖——fixture 先行，T5b 集成后跑一次真库冒烟登记）。风险：revision 链语义误读→单测 fixture 按 T5a 契约断言逐条构造，DSH review 核对。**实现后登记**：识别规则已按契约 §5.4 钉死于 fixture 矩阵（rgB/rgF/rgG/rgI 判别用例；r1 返修增 rgO2 保守误杀角例）；T5b 集成后真库链形态若与本规则偏差会红态暴露。

## 交付与运行记录

- Handoff：[M2-SFX-CORRECTION-EXPORTER-zcode-delivery-9c7cf7bc.md](../handoffs/M2-SFX-CORRECTION-EXPORTER-zcode-delivery-9c7cf7bc.md)（delivery_head=9c7cf7bc；提交链 1b765007→df0e05c4 claim→9c7cf7bc 实现→文档回填；尾部附 DSH r1 修订段）。
- Review：DSH r1=changes_requested（P1-1 必修 + P2-1 + P3×5 + P4×10），已于 r1 返修 commit 全量处置（对照见 Handoff「DSH r1 修订段」findings_disposition）；待 DSH r2。
- 实现：`experiments/M2-SFX-CORRECTION-EXPORTER/`（scanner/samples/eligibility/export/fixture/cli + 50 测试（r1 返修后）+ README）；报告 [exporter-report.md](../verification/M2-SFX-CORRECTION-EXPORTER/exporter-report.md)；导出物 training_data/sfx-corrections/（gitignored，Git 只进摘要）。
