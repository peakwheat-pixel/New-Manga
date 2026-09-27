---
id: DIAG-READING-EXPORT-001-FIX-A
title: Export terminal-state wait/signal-delivery semantics fix (symptom A)
kind: fix
status: in_progress
approval: released_by_user_overnight_2026-09-28
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: []
base_commit: 32ef1dd60cd82ac3a5fa18dfc5f834ec8639164a
branch: agent/zcode/DIAG-READING-EXPORT-001-FIX-A-terminal-wait-semantics
worktree: G:/CODEX/New Manga.worktrees/DIAG-FIX-A-zcode
integration_commit: null
---

# DIAG-READING-EXPORT-001-FIX-A — 导出终态等待/信号投递语义修复（症状 A）

## 来源与目标

[DIAG-READING-EXPORT-001](DIAG-READING-EXPORT-001.md) 定位的**症状 A**：导出在工作线程 `_finish()` 内完成
（`src/ui/viewmodels/export/viewmodel.py:379-394`：写状态 → `changed.emit()` → `exportFinished.emit()` → 清 `_running` → `changed.emit()`），
主线程槽走 Qt **排队投递**；而 `tests/reading_export/test_viewmodels.py::test_start_export_completes_and_updates_history`
的等待谓词只轮询普通属性 `vm.running`（`:274`），可在终态信号被派发前看到 `running == False`，随后
`len(finished) == 1` 断言失败——与 2026-09-27 `master@0275290` 全仓历史失败及 [T1.1.1 Review R2-I02](../../verification/T1.1.1/review-2f116a2.md)
记录的既有竞态同形。隔离探针 0/400、忙碌主线程探针 26/200 命中，机制已实证。

目标：使"测试观察到的 `running == False`"与"`exportFinished` 已投递"重新成为可靠顺序——优先改测试等待语义
（等待"终态信号已到达或终态状态已发布"）；产品侧方案（终态信号经队列调用/`QMetaObject.invokeMethod` 在主线程派发）
仅在测试侧不足以关闭窗口时评估，且必须先分析对 QML 可观察时序的影响。

**释放记录（2026-09-28 00:2x，用户全夜自主推进指令授权）：** 本 Task 已按协作协议 §5.1 由代行 Codex（ZCode
会话）释放为 `ready`。固定 base 冻结为释放时 main HEAD；branch/worktree 已创建；Owner=ZCode 开始实现，
交付 head 冻结后交 DeepSeek Harness 非作者 Review；Integrator=代行 Codex（集成记录标注"代行 Codex"供事后追认）。
FIX-B 保持 `proposed / NOT_RELEASED`，待本 Task 集成后串行释放（两者在 `tests/reading_export/**` 写集合重叠）。

## 固定恢复点与角色

- 固定 base：`32ef1dd60cd82ac3a5fa18dfc5f834ec8639164a`（main，DIAG 集成与链接修正后的治理 head）。
- Owner：ZCode（本会话亲自实现）；非作者 Reviewer：DeepSeek Harness（诊断方，非修复作者）；Integrator：代行 Codex（ZCode 会话，待追认）。
- branch/worktree：`agent/zcode/DIAG-READING-EXPORT-001-FIX-A-terminal-wait-semantics` / `G:/CODEX/New Manga.worktrees/DIAG-FIX-A-zcode`。
- depends_on：`[]`（诊断已 done）。与 FIX-B 串行释放。

## Acceptance Criteria

- [ ] 历史失败形态不可再命中：忙碌主线程判别探针（复用/扩展诊断探针 1 的两阶段设计，隔离入库 `verification/**`）在修复后跑 ≥200 次无 `running=False, finished=[]` 形态命中；探针只读，不编辑/monkeypatch 产品或测试文件。
- [ ] 目标测试在等待语义修改后仍具判别力：对"终态未达"的注入故障保持红（先红后绿的回归证据入库）。
- [ ] 若采用产品侧主线程派发：必须先在 Task 记录 QML 侧可观察时序影响分析，并经 Reviewer 确认无契约破坏；默认不采用。
- [ ] 定向套件与全仓回归：`tests/reading_export` 全部通过；全仓运行结果按实际环境分列 passed/skipped，skip 逐条给原因。
- [ ] 未以 sleep、重试、放宽断言或新增 skip 掩盖竞态；不引入新依赖。
- [ ] Handoff 与非作者 Review 齐备；Codex 集成核验通过后才可 `done`。

## 允许修改范围（释放时最终冻结）

- `tests/reading_export/test_viewmodels.py`（等待谓词与相关断言）。
- `src/ui/viewmodels/export/viewmodel.py`（仅在采用产品侧方案时；默认不动）。
- `verification/DIAG-READING-EXPORT-001-FIX-A/**`、本 Task 文件、`doc/handoffs/DIAG-READING-EXPORT-001-FIX-A-*.md`。
- 只读参考：`src/ui/qml/**`、诊断报告与探针。

## 禁止范围

不改 reader 侧任何文件（FIX-B 范围）、SQLite 连接实现、Schema、Domain Contract、依赖清单、其他 QML/ViewModel、
`src/bootstrap/**`；不改写 DIAG-READING-EXPORT-001 的报告/Handoff/证据；不加 sleep/重试/skip。

## 验证 Gate（草案，释放时冻结命令与环境）

1. 忙碌主线程判别探针 ≥200 次 0 命中（诊断环境的同款 `TASK-012-py312` 或释放时冻结环境），EXIT=0 入库。
2. `python -m pytest -q -p no:cacheprovider tests/reading_export` 全绿（passed/skipped 分列）。
3. 全仓 `python -m pytest -q -p no:cacheprovider -rs tests` 一次，结果如实记录（本 Task 不以单次全仓绿作为竞态消除证明——判别探针才是）。
4. 非作者 Review approved + Codex 集成核验（scope/`diff --check`/合并历史完整）。

## 已知阻塞

- 未释放：等待用户/Codex 排期与 §5.1 释放登记；base/branch/worktree 未冻结前不得开工。
