---
id: DIAG-READING-EXPORT-001-FIX-B
title: Reader heartbeat lifecycle fix (symptom B)
kind: fix
status: ready
approval: released_by_user_overnight_2026-09-28
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: []
base_commit: a8b94df1f1ee091a9cca894c421e9ffc3ad30614
branch: agent/zcode/DIAG-READING-EXPORT-001-FIX-B-reader-heartbeat-lifecycle
worktree: G:/CODEX/New Manga.worktrees/DIAG-FIX-B-zcode
integration_commit: null
---

# DIAG-READING-EXPORT-001-FIX-B — Reader 心跳生命周期修复（症状 B）

## 来源与目标

[DIAG-READING-EXPORT-001](DIAG-READING-EXPORT-001.md) 定位的**症状 B**：`ReaderViewModel` 的 5 s `QTimer`
心跳由 `openChapter()` 启动、仅 `closeReader()` 停止（`src/ui/viewmodels/reader/viewmodel.py:42,69-72,104-105,110-112`）；
`settleReadingTime()`（`:441-451`）对"存储已关闭/连接失效"无保护。全仓中 `closeReader()` 仅被
`tests/reading_export/test_viewmodels.py:163` 调用过一次；`test_qml_contract.py`（多处 `openChapter`）与
`tests/core/test_bootstrap.py:604-611`（生产装配 + SQLite reading store）都不关闭读者。心跳在连接关闭后触发即
`sqlite3.ProgrammingError: Cannot operate on a closed database`（诊断探针 2 确定性复现，栈帧
`viewmodel.py:450 → service.py:241/377/380 → reading_export.py:84 → connection.py:292` 与历史 stderr 逐帧相同，
且失败后心跳仍 active、每 5 s 重复）。

目标：给读者心跳一个明确的终结点（离开读者页 / `closeReader` / `aboutToQuit` 的生产装配路径），并让
`settleReadingTime` 在存储不可用时不再写入——**不以 `try/except` 吞异常代替生命周期修复**；同时让测试在
teardown 关闭读者，使诊断未决项 U1（哪个用例留下活心跳）/U2（store 类型归属）在修复后自然收口。

**释放记录（2026-09-28 01:3x，用户全夜自主推进指令授权；FIX-A 集成后按串行规则释放）：** 本 Task 已由代行
Codex（ZCode 会话）释放为 `ready`。FIX-A 已 `done`（integration=`a8b94df1`，DSH r2 approved），`tests/reading_export/**`
写集合冲突解除。Owner=ZCode 开始实现，交付后交 DeepSeek Harness 非作者 Review；Integrator=代行 Codex（待追认）。

## 固定恢复点与角色

- 固定 base：`a8b94df1f1ee091a9cca894c421e9ffc3ad30614`（FIX-A 集成 merge，治理提交之前）。
- Owner：ZCode（本会话亲自实现）；非作者 Reviewer：DeepSeek Harness（诊断方，非修复作者）；Integrator：代行 Codex（ZCode 会话，待追认）。
- branch/worktree：`agent/zcode/DIAG-READING-EXPORT-001-FIX-B-reader-heartbeat-lifecycle` / `G:/CODEX/New Manga.worktrees/DIAG-FIX-B-zcode`。
- depends_on：`[]`（FIX-A 已 done；串行释放已执行）。

## Acceptance Criteria

- [ ] 心跳生命周期闭环：存在明确的"离开读者"终结点使 `_heartbeat.stop()` 必达；泄漏形态（连接关闭后心跳触发写库）不再可复现——复用/扩展诊断探针 2（只读、隔离入库）验证修复后 0 次未处理异常。
- [ ] `settleReadingTime` 对存储不可用路径的行为有类型化、可诊断的处理（记录或转发），**不吞 `ProgrammingError`**；失败后心跳不得继续重复报错。
- [ ] 相关测试 teardown 关闭读者（至少覆盖 `tests/reading_export/test_viewmodels.py`、`tests/reading_export/test_qml_contract.py` 的 `openChapter` 用例与 `tests/core/test_bootstrap.py` 的生产装配读者路径）；新增"心跳不泄漏"回归测试先红后绿。
- [ ] U1/U2 收口记录：修复后以 teardown 枚举/日志确认无存活心跳指向已关闭连接（探针或测试断言均可），在 Task/Handoff 记录结论。
- [ ] 定向套件与全仓回归：`tests/reading_export` 与 `tests/core` 相关文件全部通过；passed/skipped 分列，skip 逐条给原因。
- [ ] 未新增 skip、未放宽既有断言、不引入新依赖。
- [ ] Handoff 与非作者 Review 齐备；Codex 集成核验通过后才可 `done`。

## 允许修改范围（释放时最终冻结）

- `src/ui/viewmodels/reader/viewmodel.py`（心跳终结点与 `settleReadingTime` 存储不可用路径）。
- `tests/reading_export/**`（teardown 与回归测试）。
- `tests/core/test_bootstrap.py`（仅生产装配读者路径的 teardown）。
- `verification/DIAG-READING-EXPORT-001-FIX-B/**`、本 Task 文件、`doc/handoffs/DIAG-READING-EXPORT-001-FIX-B-*.md`。
- 只读参考：`src/bootstrap/**`、`src/infrastructure/sqlite/**`、诊断报告与探针 2。

## 禁止范围

不改 export 侧任何文件（FIX-A 范围）、SQLite 连接/存储实现本身（`src/infrastructure/sqlite/**`、
`src/application/reading/**` 只读）、Schema、Domain Contract、依赖清单、QML 文件、`src/bootstrap/**`；
不改写 DIAG-READING-EXPORT-001 的报告/Handoff/证据；不加 sleep/重试/skip、不以 try/except 吞 `ProgrammingError`。

## 验证 Gate（草案，释放时冻结命令与环境）

1. 心跳泄漏判别探针（诊断探针 2 修复版）：真实事件循环跨 ≥2 个心跳周期，0 次未处理异常，EXIT=0 入库。
2. `python -m pytest -q -p no:cacheprovider tests/reading_export tests/core/test_bootstrap.py` 全绿（passed/skipped 分列）。
3. 全仓 `python -m pytest -q -p no:cacheprovider -rs tests` 一次，结果如实记录；teardown 后无 `Cannot operate on a closed database` 噪音。
4. 非作者 Review approved + Codex 集成核验（scope/`diff --check`/合并历史完整）。

## 已知阻塞

- 未释放：等待用户/Codex 排期与 §5.1 释放登记；base/branch/worktree 未冻结前不得开工。
- 产品侧"离开读者页"信号的接线（`src/bootstrap/**`）当前在禁止范围；若实现发现必须动 bootstrap 才能关闭终结点，停止并交 Codex 作范围决定。
