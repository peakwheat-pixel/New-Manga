---
id: FEA-11-RENDITION-1
title: FEA-11 referenced 图源/rendition 承接（proposed 占位；L10 缺口，待 scope review）
kind: design
governance_version: 3
status: proposed
approval: 占位卡：scope 尚未冻结，不得释放实施与生产改动；来源：FEA-11-LINEAGE-1 L10（Run/provider 仍依赖 `managed_original_ref`，真实 referenced 图源/rendition 未承接）+ Codex 2026-11-06 决策 Top2（需新卡 + 独立 scope review）
suggested_owner: codex
owner: null
reviewer: null
depends_on:
  - FEA-11-LINEAGE-1
  - FEA-11-SCAN-2
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-RENDITION-1
allowed_paths:
  - doc/tasks/FEA-11-RENDITION-1.md
  - doc/reviews/FEA-11-RENDITION-1-*.md
  - doc/handoffs/FEA-11-RENDITION-1-*.md
  - verification/FEA-11-RENDITION-1/**
out_of_scope:
  - 生产实现、Core/Host/App 代码、契约/schema/依赖、真实用户数据；push
---

# FEA-11-RENDITION-1：referenced 图源/rendition 承接（占位）

> **状态：`proposed` 占位卡；scope 未冻结，不得实施。** 本卡由 DSH 在 WATCH-1 closeout 时登记为下一候选（Codex 2026-11-06 决策 Top2；ZCode 亦列为 Top2）。

## 来源与目标（草案）

- **来源**：`doc/reviews/FEA-11-LINEAGE-1-r4.md` 的 L10（Run/provider 消费 `managed_original_ref`，真实 referenced 图源/rendition 未承接）；`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md` §7.2/§7.3 已冻结的选择函数与证据映射；`doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md` referenced 存储语义。
- **目标（草案）**：让 Run/provider 读取**当前持久化 binding** 的真实 referenced rendition（而非仅 managed original）；用真实新旧不同图像判别，禁止 stub；不改变冻结契约的语义/字节，不引入第二套匹配规则。

## 候选 Scope（待 scope review 冻结）

- **In（草案）**：Core 侧读路径/reference 解析、binding→rendition 选择、Run/provider 消费改造、旧 managed-original 兼容、真实 v7/新库 fixture 与判别测试。
- **Out（草案）**：删除/GC/回收站、扫描/周期调度（SCAN-1/2）、watcher（WATCH-1）、UI/通知、契约/依赖/schema 变更（如需另行 UNFREEZE）。

## 依赖与下一步

- 依赖：LINEAGE-1（done）、SCAN-2（done）；**必须先做独立 scope review**（reviewer 记录 session），由 DSH 裁决可行性/契约影响/写域，再冻结并释放。
- 若 scope review 判 BLOCKED（如需契约变更且用户不授权），登记 limitation 并回退候选。
