---
id: FEA-11-RUN-GRANT-1
title: Host Run-scoped source-read grant 切片（承接 FEA-11-RENDITION-1 L-R1；proposed 占位）
kind: implementation
governance_version: 3
status: proposed
approval: 占位卡：scope 尚未冻结，不得释放实施与生产改动；来源：`FEA-11-RENDITION-1` closeout L-R1（Run 无 source-read grant 通道 → 生产 referenced Run 仍被 typed 拒绝）+ Codex/ZCode 2026-11-06 决策（本候选已登记）；须先独立 scope review
suggested_owner: codex
owner: null
reviewer: null
depends_on:
  - FEA-11-RENDITION-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-RUN-GRANT-1
allowed_paths:
  - doc/tasks/FEA-11-RUN-GRANT-1.md
  - doc/reviews/FEA-11-RUN-GRANT-1-*.md
  - doc/handoffs/FEA-11-RUN-GRANT-1-*.md
  - verification/FEA-11-RUN-GRANT-1/**
out_of_scope:
  - 生产实现、Host/Core/App 代码、契约/schema/依赖、真实用户数据；push
---

# FEA-11-RUN-GRANT-1：Host Run-scoped source-read grant 切片（占位）

> **状态：`proposed` 占位卡；scope 未冻结，不得实施。** 由 DSH 在 `FEA-11-RENDITION-1` closeout 时登记为候选（L-R1）。

## 来源与目标（草案）

- **来源**：`doc/tasks/FEA-11-RENDITION-1.md` L-R1（F1：Run 无 source-read grant 通道；Host 只在 import/scan 铸/绑定 grant；`library_start_run` 走普通 CoreService；`run_source_guard` 在 commit 强制 live grant → 生产 referenced Run 在读图/提交被 typed 拒绝）。
- **目标（草案）**：让 Host 在 `StartRun`/`AcceptRun` 前为 Run 目标页铸造/绑定**短时 source-read grant**（复用 C-06/C-16 既有 grant 语义与 wire，不新增契约），使 Core 侧 RENDITION-1 的 referenced rendition 读路径在生产端到端可用；失败必须 typed（CORE_CAPABILITY_MISSING/SOURCE_ACCESS_DENIED 等既有 family），零业务写。

## 候选 Scope（待 scope review 冻结）

- **In（草案）**：Host `NewManga.Host`/`NewManga.CoreClient` 的 Run 授权/执行路径、Host 测试、`apps/desktop-avalonia/src/NewManga.App` 必要接线、`verification/FEA-11-RUN-GRANT-1/**`。
- **Out（草案）**：Core/Python 语义变更、契约/schema/依赖、UI/通知、真实用户数据；扫描/删除/GC；push。

## 依赖与下一步

- 依赖：`FEA-11-RENDITION-1`（done，`a05a419f7`）；**必须先做独立 scope review**（核验 C-06/C-16 grant 语义与 C-07/API 面影响；reviewer 记录 session），由 DSH 裁决后冻结释放。
- 若 scope review 判 BLOCKED（需契约 UNFREEZE 或 Host 权限边界不可行），登记 limitation 并回退候选。
