---
id: FEA-11-LINEAGE-1
title: FEA-11 lineage native 写入与读路径隔离（C-17 §7.1 续）
kind: implementation
governance_version: 3
status: proposed
approval: 承接自 FEA-11 Review r1（DSH 2026-11-05 裁决）；待 scope review
suggested_owner: codex
owner: null
reviewer: null
depends_on:
  - FEA-11
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-LINEAGE-1
allowed_paths:
  - doc/tasks/FEA-11-LINEAGE-1.md
  - doc/reviews/FEA-11-LINEAGE-1-*.md
  - doc/handoffs/FEA-11-LINEAGE-1-*.md
  - src/application/sources/service.py
  - src/application/sources/runtime.py
  - src/infrastructure/sqlite/source_sync.py
  - src/infrastructure/sqlite/regions.py
  - src/application/rendering/**
  - src/application/exporting/**
  - src/bootstrap/core_service.py
  - tests/fea11/test_source_lineage.py
  - verification/FEA-11-LINEAGE-1/**
---

# FEA-11-LINEAGE-1

承接 FEA-11 Review r1 的 R-009：lineage 的 native 写入与读路径消费/隔离。

- 范围：region/draft 写路径同事务登记 native lineage（C-17 §7.1）；ListRegions/渲染/导出/Run/编辑入口的 lineage 读守卫（region 当前 revision 的 binding 必须等于当前 binding）；B1/R1→B2、same_content 边、changed 切断的测试。
- 依据：`doc/reviews/FEA-11-r1.md` R-009；C-17 §7.1；AC11-5 的隔离部分。
- 状态：proposed（DSH 2026-11-05 裁决承接；FEA-11 已实现 captured_v7/legacy_unverified/migrated 写入与 2 个 seam 测试）。

## Acceptance Criteria

- [ ] **AC1**：region/draft 写路径同事务登记 native lineage（C-17 §7.1）；B1/R1→B2、same_content 边、changed 切断有测试。 <<PARTIAL: 待实施>>
- [ ] **AC2**：ListRegions/渲染/导出/Run/编辑入口的 lineage 读守卫（region 当前 revision 的 binding 必须等于当前 binding，否则 typed 拒绝）。 <<PARTIAL: 待实施>>
- [ ] **AC3**：AC11-5 隔离证据（旧坐标对新图不可见）与回归测试；FEA-11 r3 复审接受。 <<PARTIAL: 待实施>>
