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

## 实施记录与 limitation（DSH，2026-11-05）

- **AC1 写入**：`RevisionLineage` 在 `application.editing.ports`；`regions.py` 写路径同事务 INSERT；`RegionEditingService(lineage_binding=...)` 写 native；测试 6/6（single/batch/回滚/服务层）。
- **AC2 渲染读守卫**：`RenderService.lineage_binding/lineage_of_revision` + `LineageBindingMismatch`；`core_assembly` 从 `SourceSyncStore` 注入；测试 3/3；全量 pytest 3060/0/10 通过。
- **limitation L1（导出/Run/ListRegions 守卫）**：`CoreServices` 增加 store 字段会破坏 59 项导出/验收测试（冻结 dataclass 装配敏感）；`_export_regions` 窄批守卫同样破坏面大。两项均回退，登记为后续独立装配变更。
- **limitation L2（AC11-5 完整集成测试）**：页面 binding 切换的种子数据（source_versions/source_entries/page_bindings 约束 + `LineageBindingMismatch` 集成）构造复杂，两轮尝试回退；以渲染守卫 3 项 mismatch 测试作为核心证据。
- **limitation L3（same_content 边）**：C-17 §7.1 的 publication.previous/same_content 链未在仓库实现（FEA-11 已登记为 read 兼容后续）；本卡的读守卫按 binding 精确匹配，same_content 继承 deferral。
- **验证**：pytest 全量 3060/0/10；fea11 9/9（lineage native）；未 push。

## Acceptance Criteria

- [ ] **AC1**：region/draft 写路径同事务登记 native lineage（C-17 §7.1）；B1/R1→B2、same_content 边、changed 切断有测试。 <<PARTIAL: 写入路径已完成（RevisionLineage 值对象在 application.editing.ports；regions.py 同事务 INSERT；RegionEditingService 注入 lineage_binding 写 native；测试 6/6）；B1/R1→B2、same_content、changed 边测试待补>>
- [ ] **AC2**：ListRegions/渲染/导出/Run/编辑入口的 lineage 读守卫（region 当前 revision 的 binding 必须等于当前 binding，否则 typed 拒绝）。 <<PARTIAL: 渲染入口已实现并接线（RenderService._active_regions + LineageBindingMismatch + 3 测试；core_assembly 从 SourceSyncStore 注入只读 providers）；编辑入口写入 native lineage 已接线；**导出/Run/ListRegions 守卫未实现**（两次窄批尝试均因影响面回退：CoreServices 字段暴露会破坏 59 项导出/验收测试；导出 `_export_regions` 守卫同）→ 登记 limitation（owner DSH，目标：Source 线后续以独立装配变更实现）>>
- [ ] **AC3**：AC11-5 隔离证据（旧坐标对新图不可见）与回归测试；FEA-11 r3 复审接受。 <<PARTIAL: 渲染守卫的 mismatch 拒绝测试已构成「旧坐标不可见」的核心证据（3 项）；完整 AC11-5 集成测试（页面 binding 切换 + 旧 region 拒绝）因种子数据复杂度登记 limitation（owner DSH）>>
