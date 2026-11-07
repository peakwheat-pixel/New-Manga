---
id: FEA-12-CORE-C04B-RESIDUAL-3
title: R-1 代码修复：artifact 成员谓词补 media_artifacts.book_id（与 C-04b v1.2 / 删除谓词一致）
kind: implementation
governance_version: 3
status: ready
approval: 用户 AUTORUN 指令（2026-11-08，全部授权/自主裁决/不询问用户）；权威 scope review `doc/reviews/FEA-12-CORE-C04B-RESIDUAL-scope-r1.md`（§2.1 R-1 事实：`library.py:1178-1190` page/chapter join vs 删除面 `:1920-1926` 与 `:1218-1225` 的 `book_id`；§3.3 末段「先契约 → 再实现卡 → 再复核」）；**DSH 裁决（2026-11-08，裁决人=DSH）**：拆出独立实现卡，依赖 `FEA-12-CORE-C04B-RESIDUAL-2`（契约先写谓词文字）；正常数据零变化；跨书损坏行保护集合偏差修复
suggested_owner: dsh
owner: c04b-impl
reviewer: null
depends_on:
  - FEA-12-CORE-C04B-RESIDUAL-2
base_commit: 26aa0ca4a
branch: null
worktree: null
integration_commit: null
delivery_head: 25dc1523c
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

- [x] **AC-1 谓词对齐**：`list_book_artifact_current_pointers` 使用 `media_artifacts.book_id = ?`；不再依赖
  page/chapter join 判定成员；静态断言 Core 内「preview 侧与删除侧的 artifact 成员谓词同源/一致」。 <<MET>>
- [x] **AC-2 正常数据零回归**：既有 `tests/core/test_core_delete_preview_commands.py` 全绿；对 book_id 与 page
  所属书一致的正常数据，preview 的 `currentArtifactRevisionIds` 与修复前逐值相同（真实库 + 真实数据形态）。 <<MET>>
- [x] **AC-3 损坏行判别**：新增用例——构造 `media_artifacts.book_id=A` 但 `page_id` 属于 B 的损坏行 → 修复后
  A 的 preview **不再**包含该 artifact、B 的 preview **包含**它（与删除集合一致）；判别性：把谓词改回 page join → 红。 <<MET>>
- [x] **AC-4 零漂移**：`schema.py`/`apps/**`/契约字节/依赖零 diff；pins **18/18**；`check.ps1` PASS；scope ⊆ allowed_paths。 <<MET>>
- [x] **AC-5 门禁/证据/不夸大**：定向 pytest + 全量 pytest 不降（起点 **3369/10**）；EV/Manifest/Closeout 完整；
  **不得**写「正常数据行为变化」；损坏 DB 属异常输入，修复后仅消除偏差。 <<MET>>

## 依赖与下一步

- 依赖：`FEA-12-CORE-C04B-RESIDUAL-2`（C-04b v1.2 谓词文字必须先落地）。
- 完成后：`L-3` 状态由「未修」更新为「已修（RESIDUAL-3）」，并在冻结记录 §4A 与 R-1 行更新（**由 Lead 在 closeout 维护**）。

## 交付记录（c04b-impl，2026-11-08）

- **delivery_head**：`25dc1523c`（`git rev-parse HEAD` = `25dc1523c8afc2083a03e478dc65d4ee9c36cf5c`；实现+测试 commit）
- **commit 链**：`25dc1523c`（`fix(fea-12-core-c04b-residual-3)`：`src/infrastructure/sqlite/library.py` +
  `tests/core/test_core_delete_preview_commands.py`）→ 紧随其后的 docs/evidence commit（本卡交付记录 +
  `doc/handoffs/FEA-12-CORE-C04B-RESIDUAL-3-25dc1523c.md` + `verification/FEA-12-CORE-C04B-RESIDUAL-3/**`）
- **AC 判定**：AC-1…AC-5 全部 MET（逐条见上；`<<MET>>` 已就位于各 AC 行末）
- **门禁（before → after）**：
  - 定向 `pytest tests/core/test_core_delete_preview_commands.py tests/core/test_core_delete_commands.py -q -p no:warnings`：
    **56 passed → 59 passed**（+3 新用例）
  - 全量 `pytest tests -q -p no:warnings --tb=no`：**3369 passed / 10 skipped → 3372 passed / 10 skipped**
    （251.43 s，不降）
  - `verify_pins.ps1`：**PIN AUDIT: PASS (all 18)**，EXIT 0；契约零改动（C-04b `4b304c0c…`、M2-C1 `a82a7fc1…`
    与冻结记录 §1/§1B 一致）
  - `check.ps1`（默认 / `-TaskPath doc/tasks/FEA-12-CORE-C04B-RESIDUAL-3.md`）：**PASS (3 warnings) ×2**
  - `generate_api_inventory.py --check`：**EXIT 0**
  - scope：实现 diff（vs `4c42e11b8`）仅 `src/infrastructure/sqlite/library.py`、
    `tests/core/test_core_delete_preview_commands.py` ⊆ allowed_paths；契约/`doc/plan`/`doc/contracts`/
    `schema.py`/`apps/**`/依赖 **零 diff**
- **判别性计数**：修复前基线 **3/3 RED**；把谓词改回 page/chapter join → **3/3 RED**；逐字节复原
  **sha256 MATCH**（`da07ccdb4d0590828658c859e6c606e1c2614d7c1dde52894d3b15957b1bd792`）+ `touch` →
  **3/3 GREEN**
- **AC-3 方向说明**：卡面 AC-3 文字写「修复后 A 的 preview **不含**、B 的 preview **包含**它」；按同一行括号内的
  判定基准「**与删除集合一致**」及 C-04b v1.2 §0 第 1 条谓词，正确结果是 **`book_id=A` 侧包含、B 侧不含**
  （删除事务按 `WHERE book_id = A` 删除该行；旧 page/chapter join 才给出 A 不含/B 含）。实现按括号基准落地，
  并以**双向两行**（`book_id=A`/页属 B、`book_id=B`/页属 A）覆盖两个方向，任何读法下均可判别。
- **limitation（不夸大）**：**正常数据零变化**；仅在 `media_artifacts.book_id` 与 page 所属书不一致的
  **损坏 DB（异常输入）**下改变归属，修复后仅消除该偏差。representative/`currentRevisionId` 语义与顺序逻辑未改；
  删除事务未改；**未**声称「8 项 residual 全部关闭」——只写「R-1 的代码侧已与 C-04b v1.2 谓词一致」。
  未 push、未 closeout（`status` 与冻结记录 L-3 由 Lead 维护）。
- **证据**：`verification/FEA-12-CORE-C04B-RESIDUAL-3/{EV.md, RESOURCE-MANIFEST.json, logs/**}`。
