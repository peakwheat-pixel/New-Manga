---
id: FEA-12-CORE-C04B-RESIDUAL-3
title: R-1 代码修复：artifact 成员谓词补 media_artifacts.book_id（与 C-04b v1.2 / 删除谓词一致）
kind: implementation
governance_version: 3
status: proposed
approval: 用户 AUTORUN 指令（2026-11-08，全部授权/自主裁决/不询问用户）；权威 scope review `doc/reviews/FEA-12-CORE-C04B-RESIDUAL-scope-r1.md`（§2.1 R-1 事实：`library.py:1178-1190` page/chapter join vs 删除面 `:1920-1926` 与 `:1218-1225` 的 `book_id`；§3.3 末段「先契约 → 再实现卡 → 再复核」）；**DSH 裁决（2026-11-08，裁决人=DSH）**：拆出独立实现卡，依赖 `FEA-12-CORE-C04B-RESIDUAL-2`（契约先写谓词文字）；正常数据零变化；跨书损坏行保护集合偏差修复
suggested_owner: dsh
owner: null
reviewer: null
depends_on:
  - FEA-12-CORE-C04B-RESIDUAL-2
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-12-CORE-C04B-RESIDUAL-3
allowed_paths:
  - doc/tasks/FEA-12-CORE-C04B-RESIDUAL-3.md
  - doc/reviews/FEA-12-CORE-C04B-RESIDUAL-3-*.md
  - doc/handoffs/FEA-12-CORE-C04B-RESIDUAL-3-*.md
  - src/infrastructure/sqlite/library.py
  - tests/core/test_core_delete_preview_commands.py
  - verification/FEA-12-CORE-C04B-RESIDUAL-3/**
out_of_scope:
  - 契约字节（RESIDUAL-2 负责；本卡实现期 pins 18/18 零改动）
  - schema/迁移/依赖；wire/命令/能力/错误码/`PROTOCOL_MINOR`
  - 删除事务本身（`DELETE FROM media_artifacts WHERE book_id = ?` 不变）
  - `apps/**`、App/UI、Host 侧
  - 其它 residual（R-2/R-3/R-4/R-5/R-8 的**契约文字**由 RESIDUAL-2 修正；本卡不重复改）
  - STATUS/PLAN/LEDGER（Lead 维护）；push（Lead 统一）
---

# FEA-12-CORE-C04B-RESIDUAL-3：R-1 artifact 成员谓词代码修复

> **状态：`proposed`（待 `FEA-12-CORE-C04B-RESIDUAL-2` 完成后释放）。**
> 依据：`doc/reviews/FEA-12-CORE-C04B-RESIDUAL-scope-r1.md` §2.1（代码事实与风险）+
> `doc/plan/FEA-CONTRACT-FROZEN-C04b.md` §4A **L-3**（本偏差的 limitation 登记）。

## 目标

把 `list_book_artifact_current_pointers`（`src/infrastructure/sqlite/library.py:1178-1190`）的 artifact 成员谓词
从 **page/chapter join** 改为 **`media_artifacts.book_id = 本书`**，与删除路径（`:1920-1926`）和
`list_book_artifact_revision_ids`（`:1218-1225`）一致；与 C-04b v1.2 的谓词文字对齐。
**正常数据行为零变化**；仅修复「`media_artifacts.book_id` 与其 `page_id` 所属书不一致」的损坏行下
preview current 保护集合与删除集合不一致（多绑定/少绑定）。

## Acceptance Criteria

- [ ] **AC-1 谓词对齐**：`list_book_artifact_current_pointers` 使用 `media_artifacts.book_id = ?`；不再依赖
  page/chapter join 判定成员；静态断言 Core 内「preview 侧与删除侧的 artifact 成员谓词同源/一致」。 <<PENDING>>
- [ ] **AC-2 正常数据零回归**：既有 `tests/core/test_core_delete_preview_commands.py` 全绿；对 book_id 与 page
  所属书一致的正常数据，preview 的 `currentArtifactRevisionIds` 与修复前逐值相同（真实库 + 真实数据形态）。 <<PENDING>>
- [ ] **AC-3 损坏行判别**：新增用例——构造 `media_artifacts.book_id=A` 但 `page_id` 属于 B 的损坏行 → 修复后
  A 的 preview **不再**包含该 artifact、B 的 preview **包含**它（与删除集合一致）；判别性：把谓词改回 page join → 红。 <<PENDING>>
- [ ] **AC-4 零漂移**：`schema.py`/`apps/**`/契约字节/依赖零 diff；pins **18/18**；`check.ps1` PASS；scope ⊆ allowed_paths。 <<PENDING>>
- [ ] **AC-5 门禁/证据/不夸大**：定向 pytest + 全量 pytest 不降（起点 **3369/10**）；EV/Manifest/Closeout 完整；
  **不得**写「正常数据行为变化」；损坏 DB 属异常输入，修复后仅消除偏差。 <<PENDING>>

## 依赖与下一步

- 依赖：`FEA-12-CORE-C04B-RESIDUAL-2`（C-04b v1.2 谓词文字必须先落地）。
- 完成后：`L-3` 状态由「未修」更新为「已修（RESIDUAL-3）」，并在冻结记录 §4A 与 R-1 行更新（**由 Lead 在 closeout 维护**）。
