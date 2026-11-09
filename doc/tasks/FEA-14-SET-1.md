---
id: FEA-14-SET-1
title: FEA-14 切片 1：设置/字体面板（可切换前端架构线 S5 收口切片）
kind: implementation
governance_version: 3
status: proposed
approval: 占位卡（FEA-14 六切片之一；scope 未冻结，**不得实施**）。来源：FEA 线 S5 阶段收口计划（`doc/REBASELINE_PLAN.md`）。实施前须由 DSH 派 scope review 冻结 allowed_paths/AC/证据。
suggested_owner: zcode
owner: null
reviewer: null
depends_on:
  - FEA-13-SRC-6
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-14-SET-1
allowed_paths:
  - doc/tasks/FEA-14-SET-1.md
  - doc/reviews/FEA-14-SET-1-*.md
  - doc/handoffs/FEA-14-SET-1-*.md
  - verification/FEA-14-SET-1/**
out_of_scope:
  - **scope 未冻结，不得实施**；allowed_paths 待 scope review 后按实际写域补齐
  - 不改冻结契约字节与 18 pins（如需载体另走 UNFREEZE）
---

# FEA-14-SET-1：设置/字体面板（占位）

## 背景

FEA 线 S5 剩余六切片（SET/FONT/LIB/READ/EDIT/AI）尚未建卡；本卡为**第一切片占位**，用于 DAG 推进与范围冻结入口。FEA-13（备份/恢复/迁移）已收口（SRC-6 完成于 2026-11-10）。

## 预估范围（待 scope review）

| 项 | 预估 |
|---|---|
| 设置面板 | Fluent 风格设置页与既有 settings IPC 面的对齐（C-03/P15） |
| 字体 | 字体选择/预览与 Theme Studio 的边界 |
| 契约 | 若需新命令/字段 → 先 scope 裁决（可能触发 UNFREEZE） |
| 证据 | 截图基线 + 交互测试 + 门禁 |

## Acceptance Criteria

- 待 scope review 冻结（当前仅占位；不得实施）。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（proposed 占位） | NOT_APPLICABLE | — | — | 未创建 worktree |
| temp | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 无 |
| build | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 无构建 |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未访问真实数据 |

## Closeout Record

- 未开始（proposed）。
