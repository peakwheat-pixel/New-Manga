---
id: FLAKY-PYTEST-1
title: 稳定 3 个既有 flaky 失败
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_round_2_5
suggested_owner: sandbox-verify
owner: null
reviewer: dsh
depends_on: []
base_commit: 13cf26f6c
branch: task/FLAKY-PYTEST-1
worktree: G:/CODEX/New Manga.workspace/worktrees/FLAKY-PYTEST-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FLAKY-PYTEST-1
allowed_paths:
  - doc/tasks/FLAKY-PYTEST-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - src/**; tests/**
  - verification/FLAKY-PYTEST-1/**
  - G:/CODEX/New Manga.workspace/task-envs/FLAKY-PYTEST-1/**
  - G:/CODEX/New Manga.workspace/worktrees/FLAKY-PYTEST-1/**
---

# FLAKY-PYTEST-1：稳定 3 个既有 flaky 失败

## 背景
pytest 长期稳定 3F/2772P/9S（如 `test_detection_manga_real` 两项、`test_sandbox_job_kills_grandchildren` 等，具体以当前失败名为准），每轮记录「0 新增」但始终红。需要根治或显式隔离。

## Acceptance Criteria
- [ ] **AC1 复现与归因**：列出当前 3 个失败名，逐个判定根因类别（环境/并发/数据缺失/真 bug），给证据（日志/最小重跑）。
- [ ] **AC2 处置**：真 bug → 修复；环境依赖 → 显式 skip 并给可判定 reason（不得静默跳过掩盖）；并发 flaky → 加隔离/重试上限并说明。
- [ ] **AC3 稳定性**：处理后**连续 5 次**全量 pytest 运行结果一致（0 failed 或稳定 skip 集合），给 5 次记录。
- [ ] **AC4 回归**：`scripts/test.ps1` 全绿（≥225）；vitest 60/567 不变。
- [ ] **AC5 门禁**：check.ps1 -TaskPath PASS；64-hex pin；Handoff + Record Decision（flaky 政策）。

## 允许修改范围

`src/**; tests/**`、本卡、STATUS/PLAN/LEDGER、`verification/FLAKY-PYTEST-1/**`、workspace。

## 禁止范围

不改协议/Host 契约/旧壳、不 push、不 gc/prune；不得伪造结果；**不得把任何 API key/secret 写入仓库、日志或证据**。
