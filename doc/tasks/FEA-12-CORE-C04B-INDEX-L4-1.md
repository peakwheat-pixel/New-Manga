---
id: FEA-12-CORE-C04B-INDEX-L4-1
title: media_artifacts.book_id 索引（v9 迁移；消 preview/删除面 SCAN 放大，0 pin）
kind: implementation
governance_version: 3
status: ready
approval: 用户 AUTORUN 指令（2026-11-08：全部授权/自主裁决/不询问用户）；独立 scope review `doc/reviews/FEA-12-CORE-C04B-INDEX-L4-scope-r1.md`（fresh subagent session `6f66c01a-…`；verdict **recommended**；**pin=0**：C-15 冻结字节是 v7 规范 DDL 块，`media_artifacts` 不在其中，`:50` 的 v8+ 追加仅限两张同步表，`:343`/FROZEN-C15 `:56` 明示不冻结 FEA-11/12/13 结构，18 pin 不含 `schema.py`）；**DSH 裁决（2026-11-08，裁决人=DSH）**：按 AUTORUN §2 判据 (c)「需改核心存储才有运行时收益」立项；0 pin、无 PREREQ；形状=SCHEMA_VERSION_V9 + 单条 `CREATE INDEX idx_media_artifacts_book ON media_artifacts(book_id);`（裸 CREATE INDEX，fail-loud）
suggested_owner: dsh
owner: index-impl
reviewer: null
depends_on:
  - FEA-12-CORE-C04B-RESIDUAL-3
  - FEA-12-CORE
base_commit: 02c1a26d1
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-12-CORE-C04B-INDEX-L4-1
allowed_paths:
  - doc/tasks/FEA-12-CORE-C04B-INDEX-L4-1.md
  - doc/reviews/FEA-12-CORE-C04B-INDEX-L4-1-*.md
  - doc/handoffs/FEA-12-CORE-C04B-INDEX-L4-1-*.md
  - verification/FEA-12-CORE-C04B-INDEX-L4-1/**
  - src/infrastructure/sqlite/schema.py
  - tests/fea09/test_v7_migration.py
  - tests/fea11/test_source_gate_unify.py
  - tests/fea11/support/ipc_seed.py
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11RunGrantIpcTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11SourceIpcTests.cs
  - tests/core/test_v9_migration.py
out_of_scope:
  - 契约字节（18 pins 零改动；本卡 0 pin，无需 UNFREEZE）
  - 其它表/索引/DDL（只加 `media_artifacts(book_id)` 一个索引；v1–v8 迁移逐字节不变）
  - 数据回填/数据修复；损坏行语义（L-5 保留未修）
  - wire/命令/能力/错误码/`PROTOCOL_MINOR`；App/UI；Host 逻辑
  - RH-3 根治（C-17 additive）；B2（无消费者）
  - 真实用户数据/AppData/外部卷（红线）
  - STATUS/PLAN/LEDGER（Lead 维护）；push（Lead 统一）
---

# FEA-12-CORE-C04B-INDEX-L4-1：`media_artifacts.book_id` 索引（v9 迁移，0 pin）

> **状态：`ready`（DSH 已裁决；Owner `index-impl`；base `02c1a26d1`；0 pin、无 PREREQ）。**
> 依据：`doc/reviews/FEA-12-CORE-C04B-INDEX-L4-scope-r1.md`（recommended；§2 契约/pin 判定、§3 收益基准、§4 卡面草案、§5 成本提醒）+ 冻结记录 §4A **L-4** + RESIDUAL-3 Review **R3-002**。

## 目标

给 `media_artifacts(book_id)` 加索引（v9 迁移），消除 RESIDUAL-3 把谓词改为 `ma.book_id = ?` 后引入的
**`SCAN ma` 放大**：

- **preview**：单本成本原本 ∝ 全库 artifacts 总量（6k 库 0.50 → 60k 库 **5.94 ms/书**，11.8×）；加索引后
  60k 宽库 → **0.376 ms/书**（scope review 实测）。
- **删除面顺带修复（更强的立项理由）**：`book_delete_inventory` 计数（`:1549-1551`）、`list_book_artifact_revision_ids`
  （`:1232-1239`）、pinned 查询（`:1252-1254`）、事务内 `DELETE ... WHERE book_id`（`:1940`）均由 `SCAN` → `SEARCH`
  （DELETE/COUNT 走覆盖索引）。
- **不承诺**回到旧谓词水平：scope review 实测 60k 厚数据集 8.90 → 4.36 ms/书（仍 1.53×旧谓词，差值来自 artifacts
  驱动 + 7 键排序），**如实登记 limitation**。

## Acceptance Criteria

- [ ] **AC-1 迁移形状与字节保留**：`schema.py` 新增 `SCHEMA_VERSION_V9 = 9` 与 `MIGRATION_V9_NAME`（建议
  `v9__media_artifacts_book_index`），在 `default_migrations()` 追加**单条** `CREATE INDEX idx_media_artifacts_book
  ON media_artifacts(book_id);`（**裸 CREATE INDEX**，不用 `IF NOT EXISTS`，fail-loud）；**v1–v8 迁移逐字节不变**。 <<PENDING>>
- [ ] **AC-2 旧库升级与守恒**：真实 production migrations 库从 v8 升级到 v9：数据行数/内容守恒、索引存在、`schema_version=9`；
  重跑迁移幂等（第二次不重复建索引/不报错）；升级脚本对**只读/迁移失败**路径 fail-closed（沿既有 SC-19 口径）。 <<PENDING>>
- [ ] **AC-3 计划生效与结果等价**：`EXPLAIN QUERY PLAN` 对 `list_book_artifact_current_pointers` 的新谓词恢复
  `SEARCH ma USING INDEX`（不再是 `SCAN ma`）；preview 结果与升级前**逐值等价**（正常数据）；删除面计数/枚举结果等价。 <<PENDING>>
- [ ] **AC-4 硬编码 v8 断言同步**：更新 5 处硬编码 schema 版本断言（`tests/fea09/test_v7_migration.py:76/139/248/263`、
  `tests/fea11/test_source_gate_unify.py:213`、`Fea11SourceIpcTests.cs:60`；值来源 `tests/fea11/support/ipc_seed.py:88-90`），
  使既有套件在 v9 下全绿；不得放宽断言方向。 <<PENDING>>
- [ ] **AC-5 门禁**：定向（迁移/删除/preview/gated IPC 相关）+ 全量 pytest **≥3372/10**、全量 .NET **≥1683/0/96**
  （跑后 `git checkout -- verification/FEA-09`）、`verify_pins.ps1` **18/18**（契约零改动）、`check.ps1`（默认 + `-TaskPath`）、
  API inventory、scope ⊆ allowed_paths、`git diff --check`。 <<PENDING>>
- [ ] **AC-6 证据与不夸大**：EV（before/after `EXPLAIN` + 基准数字 + 迁移测试）、Manifest、Closeout 完整；
  **不得**写「preview 回到旧谓词水平 / 性能已全面恢复」；limitation 必须含「未回到旧谓词（1.53×）」与「回滚只走备份」。 <<PENDING>>

## limitation（预登记）

- **未回到旧谓词水平**：60k 厚数据集 8.90 → 4.36 ms/书（旧谓词 5.81），差值为 artifacts 驱动 + 7 键排序固有成本。
- **大库首启成本为外推**：scope review 以 tmp 库模拟（6k/60k artifacts），未在真实用户库演练。
- **不改损坏行语义**：`book_id` 与 page 归属不一致的损坏行，preview 归属仍按 `book_id`（C-04b v1.2），本卡不动。
- **回滚只走备份**：v9 迁移不回滚（沿既有迁移纪律）；失败即 fail-closed。
- **L-5 未修**：`preview_lifecycle` 清理枚举按 page 归属的漏清问题保留。

## 依赖与下一步

- 依赖：`FEA-12-CORE-C04B-RESIDUAL-3`（done `25dc1523c`，引入 `ma.book_id` 谓词）、`FEA-12-CORE`（done）。
- 完成后：`L-4` 状态由「未修」更新为「已修（本卡）」，并在冻结记录 §4A 与 R3-002 处置中回填（**由 Lead 在 closeout 维护**）。
