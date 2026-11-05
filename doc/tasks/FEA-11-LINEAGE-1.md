---
id: FEA-11-LINEAGE-1
title: FEA-11 lineage native 写入与读路径隔离（C-17 §7.1 续）
kind: implementation
governance_version: 3
status: ready
approval: 承接自 FEA-11 Review r1（DSH 2026-11-05 裁决）；scope review 完成（DSH 2026-11-05，见下）
suggested_owner: codex
owner: dsh（2026-11-05 scope review 冻结；实施由 DSH 承担）
reviewer: null
depends_on:
  - FEA-11-PREREQ-1
base_commit: 81c28d305
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
  - src/application/export/**
  - src/bootstrap/core_service.py
  - tests/fea11/test_source_lineage.py
  - verification/FEA-11-LINEAGE-1/**
---

# FEA-11-LINEAGE-1

## Scope Review（DSH，2026-11-05，冻结）

- **范围（冻结）**：
  1. **AC1 native lineage 写入**：`src/infrastructure/sqlite/regions.py` 的 revision 写路径（`add_revision`/`commit_region_revision`/`commit_region_batch_guarded`/`_insert_revision`）在**同一 SQLite 事务**内登记 `source_revision_lineage`（复用 `source_sync.py` 的 `insert_lineage`）；覆盖 B1/R1→B2、same_content 边、changed 切断；draft 写路径（若适用）同口径。
  2. **AC2 读守卫**：`list_regions`（及渲染/导出/Run/编辑入口经 `src/application/rendering/**`、`src/application/export/**`）校验 region 当前 revision 的 lineage binding 与页面当前 binding 一致；不一致 → typed 拒绝（render/export/Run 明确错误码，不静默返回旧坐标）。
  3. **AC3 证据**：旧坐标对新图不可见（AC11-5 隔离）回归测试；`verification/FEA-11-LINEAGE-1/` 证据（含测试日志）。
- **依据**：C-17 §7.1；`doc/reviews/FEA-11-r1.md` R-009；AC11-5 隔离部分；`doc/reviews/FEA-11-r7-acceptance.md` 硬约束（LINEAGE-1 完成前任何 UI/读路径/渲染/导出/Run 不得消费同步 binding）。
- **现状核验**：`source_sync.py` 已有 lineage 表操作（insert_lineage/lineage_of_revision/lineage_for_binding/lineage_exists_for_regions）；`service.py` 已有 `_capture_lineage`（first-switch capture）。**缺口**：regions.py 写路径未同事务登记 lineage；读路径无 binding 一致性守卫。
- **实施顺序**：AC1（写入+测试）→ AC2（守卫+测试）→ AC3（证据）→ 独立 Review（fresh subagent）→ closeout。
- **allowed_paths 确认**：现有列表覆盖全部计划文件（regions.py/service.py/runtime.py/source_sync.py/rendering/export/core_service.py/tests/verification）；`src/infrastructure/sqlite/regions.py` 已在列。
- **边界（不变）**：不 push；不改冻结契约字节（C-17/ADJ-001/FEA-01…）；不碰真实用户数据/AppData/外部卷/回收站；不新建依赖；实现者不自审。



承接 FEA-11 Review r1 的 R-009：lineage 的 native 写入与读路径消费/隔离。

- 范围：region/draft 写路径同事务登记 native lineage（C-17 §7.1）；ListRegions/渲染/导出/Run/编辑入口的 lineage 读守卫（region 当前 revision 的 binding 必须等于当前 binding）；B1/R1→B2、same_content 边、changed 切断的测试。
- 依据：`doc/reviews/FEA-11-r1.md` R-009；C-17 §7.1；AC11-5 的隔离部分。
- 状态：proposed（DSH 2026-11-05 裁决承接；FEA-11 已实现 captured_v7/legacy_unverified/migrated 写入与 2 个 seam 测试）。

## Acceptance Criteria

- [ ] **AC1**：region/draft 写路径同事务登记 native lineage（C-17 §7.1）；B1/R1→B2、same_content 边、changed 切断有测试。 <<PARTIAL: 待实施>>
- [ ] **AC2**：ListRegions/渲染/导出/Run/编辑入口的 lineage 读守卫（region 当前 revision 的 binding 必须等于当前 binding，否则 typed 拒绝）。 <<PARTIAL: 待实施>>
- [ ] **AC3**：AC11-5 隔离证据（旧坐标对新图不可见）与回归测试；FEA-11 r3 复审接受。 <<PARTIAL: 待实施>>
