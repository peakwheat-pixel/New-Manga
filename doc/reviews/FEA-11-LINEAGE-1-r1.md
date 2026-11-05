---
task_id: FEA-11-LINEAGE-1
reviewer: 独立上下文 fresh subagent（DSH 派发；未参与实现/返修）
reviewer_kind: subagent
author: DSH（Lead/Architect/Integrator；本卡实施）
base_commit: 81c28d305
reviewed_head: acd3f2263
decision: changes_requested
---

# Review：FEA-11-LINEAGE-1（r1）

> 本报告由 DSH 依据 r1 Reviewer 返回的完整报告正文落盘（2026-11-05）。Reviewer 只读仓库（起始 HEAD `6cece326f`，审查中 DSH 追加证据提交至 `acd3f2263`；产品代码零差异）；工作树前后 clean；C-17 零 diff；pins 18/18；未 push。

## 结论
**changes_requested：P0=1 / P1=5 / P2=7。**

**P0-1（阻断）**：读守卫对「无 lineage 行」fail-closed，而写入侧只覆盖 `create_region`/`_commit` 与 batch 两类路径；`save_manual_translation`/`confirm_final`/`set_locks`/`restore_revision`/draft apply/Run `_write_region_candidate`/`add_revision` 共 6 条写路径未登记 lineage。后果：这类 revision 成为 current 后，「重渲染当前页」抛 `LineageBindingMismatch` → UNKNOWN 内部错误（已用 `:memory:` + 生产类复现）；且 `_capture_lineage` 会把漏写 revision 永久标 `legacy_unverified`（数据归属污染）。3060 全绿无法发现（无真实仓储+装配链路测试）。

## AC 判定
- **AC1 PARTIAL**：结构正确（同事务、值对象在 application 层、无分层违规），但 6 条写路径缺、三条边测试缺。
- **AC2 PARTIAL**：仅 page rerender 一条入口；`rerender_region`/ListRegions/export/Run 未守卫；无 typed 错误码（裸 RuntimeError → UNKNOWN）。
- **AC3 PARTIAL**：3 项守卫测试为 fake repo + `__new__`，无真实 DB/装配链路；无 AC11-5 集成证据；「FEA-11 r3 复审接受」为复制残留。

## Findings
- **P0-1**：读守卫 fail-closed × 写入覆盖不全 = 主工作流渲染回归（详见上）。
- **P1-1**：same_content 读边缺失，且 L3 现象描述与代码事实不符（写边已由 FEA-11 落地 `insert_publication` relation）；C-17 §7.1 要求可沿 same_content 边读取。
- **P1-2**：AC2 typed 拒绝与入口覆盖均不成立；C-17 §8 无 lineage 类局部码，新增 code 必须 DSH 裁决。
- **P1-3**：5 个文件超出 allowed_paths（`application/editing/ports.py`、`application/editing/service.py`、`bootstrap/core_assembly.py`（共享组合根）、`tests/fea11/test_source_lineage_native.py`、`doc/TASK_LEDGER.md`）；卡内「allowed_paths 确认覆盖」为事实错误。
- **P1-4**：隔离两侧 opt-in + fail-open（providers None 跳过；无 provider 静默不写）；无装配级断言。
- **P1-5**：测试判别力不足（fake repo/`__new__` 绕过 `__init__`；无 missing-lineage 用例；种子 JSON 无法被真实仓储读取；回滚用例在 INSERT 前返回，证据为空）。
- **P2**：协议漂移（ports 未声明 lineage、type: ignore、InMemory `del lineage`）、未复用 `insert_lineage`、`RevisionLineage` 契约过弱、风格/局部 import、卡元数据/证据卫生、守卫 N+1。

## 门禁复核（Reviewer 只读复跑）
fea11 49 passed；native 9/9；全量 pytest 3060/0/10（EXIT 0）；check PASS；pins 18/18；C-17/冻结契约/依赖零 diff；工作树 clean；全量 .NET NOT_RUN（只读约束）。

## limitation 意见
- L1（导出/Run/ListRegions 守卫）：**不可按现状 deferral**；若 defer 须读门保持关闭 + 开硬依赖后续卡。
- L2（AC11-5 集成测试）：**不可 deferral**（AC3 唯一实体证据）。
- L3（same_content 边）：理由不成立；需实现或 DSH 显式契约偏差裁决。

## done / closed_with_limitations
- 当前不可 done，也不建议 closed_with_limitations：P0-1 是本卡新引入的回退；L1+L3 使 AC11-5 处于半隔离状态。
- 可接受收口路径：先修 P0-1（写路径补齐 + 存量 backfill + 守卫区分「无 lineage」）、P1-1、P1-2、P1-5；L1 作为有硬依赖后续卡，L2 用最小集成测试闭环，L3 或实现或 DSH 契约偏差裁决。

## 自审声明
fresh subagent，未参与实现/返修；只读仓库；未 commit/push；仅在仓外写 pytest 日志。
