---
id: FEA-12-UI-RESIDUAL-1
title: FEA-12-UI 残余 P3 收尾（delete-time capability 防御边 / preview BOOK_NOT_FOUND 刷新 / 第二次 cleanup retry 测试 / 只读与能力缺失文案）
kind: implementation
governance_version: 3
status: proposed
approval: 占位卡：scope 尚未冻结，不得释放实施与生产改动；来源：`FEA-12-UI` closeout（2026-11-06）登记的 P3 follow-up ①–④ + 本会话下一队列（RENDITION-1 closeout 后）；须先独立 scope review
suggested_owner: zcode
owner: null
reviewer: null
depends_on:
  - FEA-12-UI
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-12-UI-RESIDUAL-1
allowed_paths:
  - doc/tasks/FEA-12-UI-RESIDUAL-1.md
  - doc/reviews/FEA-12-UI-RESIDUAL-1-*.md
  - doc/handoffs/FEA-12-UI-RESIDUAL-1-*.md
  - verification/FEA-12-UI-RESIDUAL-1/**
out_of_scope:
  - 生产实现（apps/desktop-avalonia/**）与任何 Core/Host 改动；契约/schema/依赖；真实用户数据；push
---

# FEA-12-UI-RESIDUAL-1：FEA-12-UI 残余 P3 收尾（占位）

> **状态：`proposed` 占位卡；scope 未冻结，不得实施。** 由 DSH 在 RENDITION-1 closeout 时登记为下一候选（FEA-12-UI closeout P3 follow-up ①–④）。

## 来源与目标（草案）

- **来源**：`doc/tasks/FEA-12-UI.md` Closeout（P3 处置/follow-up 清单，2026-11-06）：
  1. delete-time `CORE_CAPABILITY_MISSING` 仍置页级 missing 的**防御边**（当前 Host/Core 不可达、无测试）；
  2. preview `BOOK_NOT_FOUND` 未自动 `ReloadAsync`（AC4「提示并刷新」的手动路径可用）；
  3. AC6 第二次 cleanup retry → `BOOK_NOT_FOUND` 有实现无测试；
  4. Host 只读 + 能力缺口时真实 `HOST_READ_ONLY` banner 被抑制的**文案取舍**（只读/能力缺失文案）。
- **目标（草案）**：把上述 4 项 UI 残余收口为可验证行为/测试/文案，不改变冻结契约与 Core/Host wire；DOTNET UI 测试门禁不降。

## 候选 Scope（待 scope review 冻结）

- **In（草案）**：App 侧 `TrashViewModel`/preview/只读 banner 相关代码与测试、`verification/FEA-12-UI-RESIDUAL-1/**`；如需 Host 只读能力探测接线，须在 scope review 明确最小面。
- **Out（草案）**：Core/Host 语义变更、契约/schema/依赖、回收站系统 API、真实用户数据；FEA-12-UI 已 OUT 的 L1–L10。

## 依赖与下一步

- 依赖：`FEA-12-UI`（done，`a46d4d5c7`）；**必须先做独立 scope review**（reviewer 记录 session），由 DSH 裁决可行性/契约影响/写域，再冻结并释放。
- 若 scope review 判 BLOCKED（如需 Host/Core 新能力或契约变更），登记 limitation 并回退候选或拆分。
