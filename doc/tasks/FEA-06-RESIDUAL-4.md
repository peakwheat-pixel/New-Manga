---
id: FEA-06-RESIDUAL-4
title: RegionBox 逐 region 冲突投影与「查看对照」（原 RESIDUAL-2 格 3；需 C-07 additive）
kind: implementation
governance_version: 3
status: proposed
approval: 占位卡：由 `FEA-06-RESIDUAL-3` scope review r1（格 3 未解除）与 DSH 2026-11-08 裁决 re-home；**scope 未冻结，不得实施**；须先独立 scope review + 可能需要 C-07/UNFREEZE 类载体
suggested_owner: dsh
owner: null
reviewer: null
depends_on:
  - FEA-06-RESIDUAL-3
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-06-RESIDUAL-4
allowed_paths:
  - doc/tasks/FEA-06-RESIDUAL-4.md
  - doc/reviews/FEA-06-RESIDUAL-4-*.md
  - doc/handoffs/FEA-06-RESIDUAL-4-*.md
  - verification/FEA-06-RESIDUAL-4/**
out_of_scope:
  - 未 scope review 前不得实施任何实现
---
# FEA-06-RESIDUAL-4：RegionBox 冲突投影与「查看对照」（占位）

## 来源与已核事实

`FEA-06-RESIDUAL-2` 的 BLOCKED 表**格 3**「RegionBox 冲突态（查看对照）」在 `FEA-06-RESIDUAL-3` scope review 中被判**未解除**：

- `RegionSummary` 无任何冲突字段（`apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs:172-178`）；
- 区域文本投影 `list_page_region_texts` 已注册（`HostCommandRegistry.cs:191`）但**未经 `IHostController` 暴露**（`RegionTextProjection.cs:224-281` 仅测试使用）；
- 术语/冲突面为 NOT_WIRED（`StudioTermsViewModel.cs:36-62`）；
- **Current V2 也没有**「查看对照」；现有仅"并发冲突横幅 + 禁止伪造对照"（RESIDUAL-1 已完成，`FluentResidualBatchATests.cs:613-641`）。

## 阻塞与候选路线（须 scope review 定稿）

1. 补数据：把 `list_page_region_texts`（或等价的逐 region 冲突投影）加入 `IHostController` → 触 `tools/generate_api_inventory.py` 抽取面与 **C-07 pin** → 需 `FEA-C07` additive UNFREEZE 载体 + API inventory 重算。
2. 或降级产品范围：正式裁决「不提供查看对照，仅保留冲突横幅与 typed 原因」→ 以 `NOT_APPLICABLE: 产品范围决定` 记录（必须写清用户可见后果）。

## 验收（草案，待冻结）

- 若走 1：逐 region 冲突字段投影 + UI 对照面板 + 判别测试；契约/pin 变更须走 UNFREEZE 且独立 byte-level 复核。
- 若走 2：DSH/用户裁决记录 + `FEA-06-RESIDUAL-2` 卡面 append-only 更新（不得删改原 limitation 字节）。
