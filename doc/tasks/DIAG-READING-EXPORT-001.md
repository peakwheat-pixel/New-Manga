---
id: DIAG-READING-EXPORT-001
title: Reading/export completion signal and connection-lifetime flaky diagnosis
kind: diagnostic
status: proposed
approval: pending_release
suggested_owner: DeepSeek Harness
owner: null
reviewer: Codex
depends_on: []
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# DIAG-READING-EXPORT-001 — reading_export 间歇失败诊断提案

## 来源与目标

[M2-I1 R3 非作者 Review](../reviews/M2-I1-09ad43a-deepseek.md) P3-004 在隔离的 `master@0275290` 全仓首次运行观测到 `tests/reading_export/test_viewmodels.py::test_start_export_completes_and_updates_history` 失败：`exportFinished` 未触发，同时 teardown 有后台 `settleReadingTime` 对已关闭 SQLite 连接写入。第二次基线全仓、交付树两次全仓及两树各三次单文件运行均通过。I1 修改范围不含该测试、reader/export ViewModel 或连接实现，故不归因 I1。

这并非首次出现的症状：[T1.1.1 独立 Review](../../verification/T1.1.1/review-2f116a2.md) 已对**同一测试**记录既有 export/Qt 信号竞态并建议独立修复窗口；[TASK-034](TASK-034.md) 的诊断涉及另一导出测试和终态信号观察。当前证据说明问题仍可能存在，且新的连接关闭异常值得单独定位。此 Task 只诊断根因与可复现条件，不把一次全仓失败误判为 M2-I1 回归，也不预先授权修复。

## Acceptance Criteria

- [ ] 固定启动时实际 `master` base、测试解释器/PySide6/SQLite 版本、shell、`openssl` 与 `QT_QPA_PLATFORM`，保存每次运行的原始输出和 exit。
- [ ] 对比全仓、单文件、最小测试组合及不同收集顺序；区分 `exportFinished` 信号投递、测试等待、reader heartbeat/`settleReadingTime`、SQLite 连接生命周期，给出可证伪的根因假设与判别探针。
- [ ] 若可复现，保存修前失败 artefact；若不可复现，记录实际运行次数、环境和 `NOT_REPRODUCED`，不得写成已修复。
- [ ] 产出诊断报告、风险界定及必要的独立修复 Task 建议；修复范围另由 Codex 冻结并释放。

## 允许修改范围（释放前均不可实施）

- `doc/tasks/DIAG-READING-EXPORT-001.md`、拟建 `doc/research/DIAG-READING-EXPORT-001.md`、`verification/DIAG-READING-EXPORT-001/**`、自己的 Handoff。
- 只读检查 `tests/reading_export/**`、`src/ui/viewmodels/{reader,export}/**`、相关 SQLite/服务代码及历史证据。

## 禁止范围

不改生产代码、测试断言/等待预算、Schema、Domain Contract、依赖、M2-I1/I2 产品文件或 T3.2.1 Gate。任何修复或范围扩大需独立授权；不得用 skip/重跑后通过掩盖首次失败。

## 测试计划

| 场景 | 计划步骤 | 当前结果 |
|---|---|---|
| 基线复现 | `python -m pytest -q -p no:cacheprovider -rs tests`，固定 shell/venv/openssl，逐次保存输出 | NOT_RUN（本 Task 尚未释放） |
| 定向与顺序 | `tests/reading_export/test_viewmodels.py` 单文件及相关前置组合，循环与顺序矩阵须先限定次数 | NOT_RUN |
| 根因判别 | 只读或独立探针对终态信号、线程退出、heartbeat 与连接关闭时序记录 | NOT_RUN |

## 依赖与启动 Gate

本诊断为 Legacy reliability backlog 的独立 `proposed` Task，**未释放**，不属于 M2 第一波四个 Task，也不改变 T3.2.1 Full Gate。Codex 若决定启动，须先核对当时真实 `master`、冻结 branch/worktree/allowed paths、将 Task 标 `ready`；Owner=DeepSeek Harness，Reviewer=Codex。当前证据见 `verification/M2-I1/review-09ad43a/` 与本次 I1 [集成记录](../../verification/M2-I1/integration-cff1e0a/record.md)。
