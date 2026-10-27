---
id: RUN-STORE-CACHE-RACE-FIX-1
title: 修复 SqlitePipelineStore 共享缓存跨线程对象替换竞态
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_goal_auto_except_recommended
suggested_owner: sandbox-verify
owner: null
reviewer: dsh
depends_on: []
base_commit: 97de0fa99
branch: task/RUN-STORE-CACHE-RACE-FIX-1
worktree: G:/CODEX/New Manga.workspace/worktrees/RUN-STORE-CACHE-RACE-FIX-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/RUN-STORE-CACHE-RACE-FIX-1
allowed_paths:
  - doc/tasks/RUN-STORE-CACHE-RACE-FIX-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - src/**
  - verification/RUN-STORE-CACHE-RACE-FIX-1/**
  - G:/CODEX/New Manga.workspace/task-envs/RUN-STORE-CACHE-RACE-FIX-1/**
  - G:/CODEX/New Manga.workspace/worktrees/RUN-STORE-CACHE-RACE-FIX-1/**
---

# RUN-STORE-CACHE-RACE-FIX-1：修复共享缓存跨线程对象替换竞态

## 背景（SCHEDULER-THREAD-DIAG-1 实证）

`SqlitePipelineStore._cache` 是跨线程共享可变 dict；`GetTaskProjection(fresh=True)` → `store.refresh()` 读 DB 后把 `_cache[run_id]` 替换为**新克隆**，执行线程接着用克隆提交（detect completed+backfill 只落克隆），`execute_run` 局部 run 未回填 → regionless ocr 报 `INVALID_INPUT`；旧对象随后整份 `_persist` 回写（last-writer-wins）→ 已提交 StepRun 回退 `running`。

复现：执行线程 + 100ms `GetTaskProjection(fresh=True)` 轮询 → 3/3 复现；frozen sidecar `2b36bfeb…` 同样复现。**GUI 当前不轮询故未触发，但属 latent 生产缺陷，重打包不能视为已修。**

## Acceptance Criteria

- [ ] **AC1 最小修复**：`refresh()`/`fresh=True` 读取**不替换** `_cache`（视图读与执行缓存分离；返回独立读取对象）；不改 Core 语义、不改协议。
- [ ] **AC2 写入加固**：`run_json` 写入加 owner 归属或 revision CAS，防旧快照覆盖新提交（推荐；如实施需单测）。
- [ ] **AC3 并发回归**：新增并发测试——执行线程 + 100ms projection 轮询，断言 **0 卡 running、0 regionless INVALID_INPUT**（用原复现脚本证明修复前失败/修复后通过）。
- [ ] **AC4 回归**：pytest 相对基线（3F/2753P/9S）无新增失败；`scripts/test.ps1` 全绿（≥177）。
- [ ] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff + Record Decision（缓存/所有权模型）。

## 允许修改范围

`src/**`（sqlite pipeline store / projection 读取 / 相关测试）、本卡、STATUS/PLAN/LEDGER、`verification/RUN-STORE-CACHE-RACE-FIX-1/**`、workspace。

## 禁止范围

不改协议/Host 契约/旧壳、不 push、不 gc/prune；不得用"禁用 fresh 轮询"绕过；不得放宽并发/输入校验。
