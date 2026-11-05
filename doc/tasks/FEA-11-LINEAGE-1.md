---
id: FEA-11-LINEAGE-1
title: FEA-11 lineage native 写入与读路径隔离（C-17 §7.1 续）
kind: implementation
governance_version: 3
status: in_review
approval: 承接自 FEA-11 Review r1（DSH 2026-11-05 裁决）；scope review 完成（DSH 2026-11-05，见下）
suggested_owner: codex
owner: dsh（2026-11-05 scope review 冻结；实施由 DSH 承担）
reviewer: 独立上下文 fresh subagent（doc/reviews/FEA-11-LINEAGE-1-r1.md）
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
  - src/application/editing/ports.py
  - src/application/editing/service.py
  - src/application/sources/service.py
  - src/application/sources/runtime.py
  - src/infrastructure/sqlite/source_sync.py
  - src/infrastructure/sqlite/regions.py
  - src/application/rendering/**
  - src/application/export/**
  - src/bootstrap/core_service.py
  - src/bootstrap/core_assembly.py（DSH 窄批：仅 lineage providers 注入，r1 后已回退）
  - tests/fea11/test_source_lineage.py
  - tests/fea11/test_source_lineage_native.py
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
- **allowed_paths**（r1 P1-3 更正）：实际改动超出原列表——`application/editing/ports.py`、`application/editing/service.py`、`bootstrap/core_assembly.py`（共享组合根，需单独授权）、`tests/fea11/test_source_lineage_native.py`、`doc/TASK_LEDGER.md` 已按 DSH 窄批登记进本卡；`core_assembly.py` 的接线在 r1 后已回退，仅保留授权记录。
- **边界（不变）**：不 push；不改冻结契约字节（C-17/ADJ-001/FEA-01…）；不碰真实用户数据/AppData/外部卷/回收站；不新建依赖；实现者不自审。



承接 FEA-11 Review r1 的 R-009：lineage 的 native 写入与读路径消费/隔离。

- 范围：region/draft 写路径同事务登记 native lineage（C-17 §7.1）；ListRegions/渲染/导出/Run/编辑入口的 lineage 读守卫（region 当前 revision 的 binding 必须等于当前 binding）；B1/R1→B2、same_content 边、changed 切断的测试。
- 依据：`doc/reviews/FEA-11-r1.md` R-009；C-17 §7.1；AC11-5 的隔离部分。
- 状态：proposed（DSH 2026-11-05 裁决承接；FEA-11 已实现 captured_v7/legacy_unverified/migrated 写入与 2 个 seam 测试）。

## 实施记录与 limitation（DSH，2026-11-05；r1 复审后修订）

- **AC1 写入**：`RevisionLineage` 在 `application.editing.ports`；`regions.py` 写路径同事务 INSERT；`RegionEditingService._commit`/batch 注入；测试 6/6。**r1 P0-1**：6 条写路径未覆盖（save_manual_translation/confirm_final/set_locks/restore_revision/draft apply/Run/add_revision）。
- **AC2 读守卫**：守卫类 `LineageBindingMismatch` + `_active_regions` 校验 + 3 测试；**r1 P0-1 后接线已回退**（守卫默认不启用，恢复预 LINEAGE-1 行为）——原因是守卫对「无 lineage 行」fail-closed，而写入覆盖不全，导致正常保存译文后重渲染失败（UNKNOWN）。回退即遵守 r7-acceptance 硬约束（LINEAGE-1 完成前读路径不消费同步 binding）。
- **limitation 修订（r1）**：
  - **L1（导出/Run/ListRegions/单区域渲染守卫）**：未实现；「CoreServices 字段破坏 59 项测试」是装配/测试耦合问题，可在窄批解决；**前提**：读门保持关闭（UI/导出/Run 不消费同步后的新 binding），并开硬依赖后续卡。
  - **L2（AC11-5 集成测试）**：不可 deferral——它是 AC3 的唯一实体证据；最小可行集成测试应覆盖 native 写入 → changed 拒绝 / same_content 放行 / 无 lineage 诊断。
  - **L3（same_content 读边）**：写边已由 FEA-11 落地（`insert_publication` relation）；缺的是读边遍历，L3 原「仓库未实现」理由不成立；需实现或 DSH 显式契约偏差裁决（C-17 §7.1 是冻结条款）。
- **P2（r1）**：协议漂移（ports 未声明 lineage 参数、type: ignore）、未复用 `insert_lineage`、`RevisionLineage` 契约过弱（provenance 无 Literal/枚举、dead fields）、风格/局部 import、卡元数据/证据卫生、守卫 N+1。
- **验证**：pytest 全量 3060/0/10（r1 时点）；回退后待复跑；未 push。

## Acceptance Criteria

- [ ] **AC1**：region/draft 写路径同事务登记 native lineage（C-17 §7.1）；B1/R1→B2、same_content 边、changed 切断有测试。 <<PARTIAL: 仅 create_region/_commit 与 batch 两类路径；r1 P0-1 指出 save_manual_translation/confirm_final/set_locks/restore_revision/draft apply/Run/add_revision 共 6 条写路径未登记，且历史 revision 无 lineage 行→守卫 fail-closed 会拒绝正常渲染（已回退接线）；三条边测试全缺>>
- [ ] **AC2**：ListRegions/渲染/导出/Run/编辑入口的 lineage 读守卫（region 当前 revision 的 binding 必须等于当前 binding，否则 typed 拒绝）。 <<PARTIAL: 守卫类与测试已存在（RenderService._active_regions + LineageBindingMismatch + 3 测试），但 **r1 P0-1 后接线已回退**（守卫默认不启用）；`rerender_region`/ListRegions/export/Run 未守卫；无 typed 错误码（裸 RuntimeError → UNKNOWN）。AC2 实质未完成>>
- [ ] **AC3**：AC11-5 隔离证据（旧坐标对新图不可见）与回归测试。 <<PARTIAL: 3 项守卫测试为 fake repo + __new__，无真实 DB/装配链路；无 AC11-5 集成证据；文本的「FEA-11 r3 复审接受」为复制残留（本卡 r1）>>
