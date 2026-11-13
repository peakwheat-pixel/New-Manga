# Current Development Status

状态：2026-10-25 起 DSH 接任 Lead / Architect / Integrator；授权与字节保留见[接管记录](GOVERNANCE_TAKEOVER_2026-10-25.md)。

## 当前程序
- **FEA 线 ACTIVE（S5）**：[FEA-00 方案](design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md)；V11R 程序已收官（v0.1.1）。
- 当前 Task：[NEW-MANGA-V1-FULL-AUDIT](tasks/NEW-MANGA-V1-FULL-AUDIT.md) `done`（DSH 自动裁决；Codex 最终回退复审 ACCEPT_WITH_LIMITATIONS；pins 548/548；AC1–4 MET；Gate BLOCKED；下一 R1 SEC-01）。
- 刚收口：FEA-15-PIN-BASIS-ENFORCE-1 `closed_with_limitations`（AC5 MET；R-001 CLOSED）；DIAG-ACL-1/[ACCEPT-1](tasks/FEA-15-ACCEPT-1.md) 同为 `closed_with_limitations`；PIN-POLICY-1 `done`。
- FEA-11/12 线：WATCH/SCAN/MATCH/LINEAGE/HOST-AUTH、FEA-12 四卡均 `done`。
- **AC11-1 MET with limitation**（2026-11-06，[裁决](reviews/FEA-11-AC11-1-adjudication-2026-11-06.md)）：冷启动枚举、registry/root 核验及每次访问的 live grant+lease+digest 检查；启动不做全量扫描（L-STARTUP）。

- **Gate**：`G-CONTRACT`/`G-DELETE-CONTRACT` ✅ CLOSED（[裁定](plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md)）；四表 DDL 已冻 = L-1 前置已满足（C-15 schema v7 + C-17 v1.1 schema v8；L-2…L-9 保留）；裁决 [ADJ-2026-11-01](reviews/ADJ-2026-11-01-FEA-DECISIONS.md)、[ADJ-2026-11-05](reviews/ADJ-2026-11-05-FEA-12-SCOPE.md)。
- **FEA 方案（非 Task）**：[r8](reviews/FEA-00-dsh-r8.md) approved（0 P0/0 P1/9 P2）；17 契约 + [FEA-01](plan/FEA-01_CONTRACT_DRAFT.md) 已冻结（18 pins）；存储 [AD-003](AD-003_REFERENCED_SOURCE_ARCHITECTURE.md)；删除 [ADJ-001](contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md)。
- 审查报告在 `doc/reviews/`；`verify_pins.ps1` 18/18 PASS（机械校验，不替代复核）。

## 近期完成
- **FEA-14-S5-PREQ-1** `done`（`5459c9220`；r2 approved；C-07 UNFREEZE v1.2 pin `5673b1c4…`；wire 25 条 + errata 0 pin + DDL v10 计划）。
- **FEA-14-SET-1** `done`（`c543b51cc`；3 轮独立复核；字体只读投影；零契约字节）。
- **FEA-10** `done`（`d1972f0f`；P0/P1=0）；**FEA-09-UI-1** `done`（`b14e04da`）；**FEA-09** `done`（`87ca5070`）。

## 保留与已知限制
- 台账 [TASK_LEDGER](TASK_LEDGER.md)；DIR-4/5=2/1000；真机端到端 run-i18 7/7、run-i36 10/10。
- PREREQ-2 历史：pytest 3446/0/10；.NET 1804/0/107；验收复跑见 FEA-15-ACCEPT-1 卡。

## Gate 与保留项
Technical Gate=NOT_SATISFIED；private_registry_absence=UNPROVABLE；Owner Risk Acceptance=APPROVED；Disposition=WAIVED_BY_OWNER。push `clean-snapshot-20261026`=`892b946e`、`clean-snapshot-20261102`=`ac7d488e`；**main 2026-11-08 push（2C/L-R11/C-04b/SCAN-RH/INDEX-L4-1/UI-RESIDUAL-2；§27；AHEAD=0）**。

## 当前权威指针
- DAG/节点：[REBASELINE_PLAN](REBASELINE_PLAN.md)（唯一权威）；主线 `main`；工作区 [WORKSPACE_GOVERNANCE](WORKSPACE_GOVERNANCE.md)。
- 恢复点：rolling checkpoint + 各 Task 卡与 `verification/**`。
- 残余收口：[PLAN](plan/RESIDUAL-CLOSEOUT-PLAN-2026-11-08.md)（4 节点→done，6 卡方案）。
