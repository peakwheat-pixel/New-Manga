---
id: SCHEDULER-THREAD-DIAG-1
title: 调度线程 detect 卡 running 诊断（只诊断）
kind: research
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_goal_auto_except_recommended
suggested_owner: baseline-scout
owner: null
reviewer: dsh
depends_on: []
base_commit: 97de0fa99
branch: task/SCHEDULER-THREAD-DIAG-1
worktree: G:/CODEX/New Manga.workspace/worktrees/SCHEDULER-THREAD-DIAG-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/SCHEDULER-THREAD-DIAG-1
allowed_paths:
  - doc/tasks/SCHEDULER-THREAD-DIAG-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/SCHEDULER-THREAD-DIAG-1/**
  - verification/SCHEDULER-THREAD-DIAG-1/**
  - G:/CODEX/New Manga.workspace/task-envs/SCHEDULER-THREAD-DIAG-1/**
  - G:/CODEX/New Manga.workspace/worktrees/SCHEDULER-THREAD-DIAG-1/**
---

# SCHEDULER-THREAD-DIAG-1：调度线程内 detect StepRun 卡 running 诊断（只诊断）

## 背景

CORE-PIPELINE-FIX-1 报告可复现异常：经 `python -m bootstrap.core_service` **调度线程**执行同一 Run 时，detect StepRun 卡 `running`、下游 regionless ocr 报 `INVALID_INPUT`；进程内直接 `execute_run` 正常（3 份证据）。疑 `ThreadRoutedConnection`/`write_in_current_transaction` 事务路径。

## Acceptance Criteria

- [ ] **AC1 最小复现**：按报告路径（`-m bootstrap.core_service` + 同 Run 请求）稳定复现，给出线程/事务/连接路由信息。
- [ ] **AC2 根因**：定位是事务可见性（写未提交跨线程不可见）、连接路由复用、调度线程未 commit、还是 StepRun 状态机未收尾；给可判定证据（日志/DB 快照/线程栈）。
- [ ] **AC3 影响面**：是否影响真实产品路径（Host→core_service 子进程调度）？给出「会影响/不会影响」的证据（例如产品实际走 execute_run 与否）。
- [ ] **AC4 建议**：修复建议（最小改动）+ 是否需要新 Task；不改 Core 语义。
- [ ] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff。

## 允许修改范围

`verification/SCHEDULER-THREAD-DIAG-1/**`、本卡、STATUS/PLAN/LEDGER、workspace。**只读**产品源码/Core。

## 禁止范围

不改 Python Core 语义/产品源码/协议/旧壳、不 push、不 gc/prune；不伪造复现。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/SCHEDULER-THREAD-DIAG-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/SCHEDULER-THREAD-DIAG-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
