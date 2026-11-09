---
id: FEA-13-ID-3
title: DatabaseId 原语 + manifest/恢复过滤 + backup.list 投影（FEA-13 片 3）
kind: implementation
governance_version: 3
status: in_review
approval: `FEA-13-scope-r1.md` §7 片 3 + `ADJ-2026-11-09-FEA13-ERRATA-AND-SPLIT`；依赖 `FEA-13-BK2-1`、`FEA-13-COV-2`（done）；DSH 裁决错误码 `BACKUP_DATABASE_MISMATCH`（conflict、非 retryable）
suggested_owner: dsh
owner: dsh
reviewer: 待指派（必须独立上下文）
depends_on:
  - FEA-13-BK2-1
  - FEA-13-COV-2
base_commit: 54453abb3
branch: null
worktree: null
integration_commit: null
delivery_head: 3d8b5507e
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/FEA-13-ID-3
allowed_paths:
  - doc/tasks/FEA-13-ID-3.md
  - doc/reviews/FEA-13-ID-3-*.md
  - doc/handoffs/FEA-13-ID-3-*.md
  - verification/FEA-13-ID-3/**
  - src/infrastructure/sqlite/identity.py
  - src/infrastructure/sqlite/nmbak.py
  - src/bootstrap/core_assembly.py
  - src/bootstrap/core_service.py
  - apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - tests/storage/test_nmbak_identity.py
  - tests/core/test_core_backup_wire.py
out_of_scope:
  - 不改 C-01b/C-09 契约字节、18 pins；不新增 DDL（`DatabaseId` 存既有 `application_metadata`）
  - 不改 M2-C1 字节（backup 命令不在 M2-C1；V11R wire 文档只在需要时同步行）
  - 不实现 merge restore（片 4）、调度保留（片 5）、数据根迁移（单列）、SC-B01 ④（`FEA-13-SRC-6`）
  - 不改 UI 展示层（只做 Core/Host 投影字段；UI 消费另案）
---

# FEA-13-ID-3：DatabaseId 原语 + manifest/恢复过滤

## 依据

- `FEA-13-scope-r1.md` §7 片 3；C-01b **SC-18**（`DatabaseId`，引用不复写）；C-09 SC-B03（引用）。
- 存储载体：既有 `application_metadata(metadata_key, value_json, updated_at)`（`schema.py:128-132`），**无新 DDL、schema 仍 v9**。
- 身份语义：UUID4；缺失 ≠ 空串/书名/hash，统一读作 **unknown（`None`）**。

## 实现口径

| 项 | 要求 |
|---|---|
| 写 | 首次可写启动（装配后）`ensure_database_id`：`INSERT OR IGNORE` + 回读，原子且幂等；重复启动不改变 |
| 旧库 | 无该键的旧库在首次 ensure 时回填；回填前读作 unknown |
| manifest | v2 包写 `database_id`（来自当前库；unknown 时写 `null`）；v1 包无该字段 → adapter 读作 unknown |
| restore | 包 `database_id` 与当前库 `database_id` **均非空且不等** → `BACKUP_DATABASE_MISMATCH`（conflict、非 retryable），在 `pre_restore` 之前拒绝（零副作用）；任一 unknown → 允许（不阻断） |
| list | `backup.list` 每项含 `database_id`（null=unknown）；C# `BackupPackageInfo` 增加 `DatabaseId?` 并解析 |

## Acceptance Criteria

- [x] **AC1 原子写入/幂等**：首次装配写入 UUID4 到 `application_metadata.database_id`；二次启动不变；schema 版本不变（v9）。 <<MET>>
- [x] **AC2 旧库回填**：无该键的库在 `ensure` 时回填；回填前 `read_database_id` 返回 `None`（unknown，非空串）。 <<MET>>
- [x] **AC3 manifest 携带**：v2 包 `database_id` 与库一致；unknown 时为 `null`；v1 包读作 unknown。 <<MET>>
- [x] **AC4 跨库 restore 拒绝**：不同 `database_id` → `BACKUP_DATABASE_MISMATCH`；DB/managed/包字节不变、无 `pre_restore`、无写回。 <<MET>>
- [x] **AC5 list 投影**：`backup.list` 每项含 `database_id`；C# `BackupPackageInfo.DatabaseId` 解析（null 保持 null）。 <<MET>>
- [x] **AC6 门禁**：定向 pytest 全绿；`dotnet build` 0/0；`check.ps1`（默认 + `-TaskPath`）PASS；pins 18/18；diff ⊆ allowed_paths。 <<MET>>

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-ID3-README | AC1–AC6 | `verification/FEA-13-ID-3/README.md` | `-` | `b2dfe9619fb863aaf51b973c932bafdaba98b912c8c6b68fca93e8a9808fd5e9` | CANONICAL |
| EV-ID3-SUITE | AC1–AC5 | `verification/FEA-13-ID-3/logs/pytest-backup-suite.log` | `-` | `db2682d3618344d3625c146d1209477e4a61c1eb9a7bdf14892e8588b8a33114` | CANONICAL |
| EV-ID3-MUT | AC4（变异判别） | `verification/FEA-13-ID-3/logs/mutation-db-gate.log` | `-` | `6fcc5b0c6b8fe3e2ebeb10154841ca26de7233ebb0e7b0d60bce1c649c9d2c89` | CANONICAL |
| EV-ID3-BUILD | AC5,AC6 | `verification/FEA-13-ID-3/logs/build.log` | `-` | `a1f492e5bed7ba67708748a6553ee858f491eabe64fdb298f7ab6de1702aacef` | CANONICAL |
## 证据计划

| # | 命令/步骤 | 判别 |
|---|---|---|
| E1 | pytest `tests/storage/test_nmbak_identity.py` + 备份面 6 文件 | 0 failed |
| E2 | ensure 并发/幂等/旧库回填 | 值稳定、非空 UUID |
| E3 | 跨库 restore | typed 拒绝 + 零副作用 |
| E4 | `dotnet build` + wire 解析测试 | 0/0；`DatabaseId` 解析正确 |
| E5 | 变异（关闭跨库检查 / list 丢字段） | 至少 1 例 RED |
| E6 | `check.ps1`、`verify_pins` | PASS / 18/18 |

## 风险与回退

- 旧库首次回填发生在装配期：失败必须 fail-closed（不产出半身份）。
- 跨库检查只作用于「双方均已知」；unknown 不阻断（避免旧包全部不可恢复）。
- 回退：`git revert`；`database_id` 键可保留（无破坏性）。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main；base `54453abb3`） | NOT_APPLICABLE | — | — | 未创建 worktree |
| temp | pytest 临时目录 | NOT_APPLICABLE | — | — | 测试隔离 fixture |
| build | `apps/desktop-avalonia/**/bin,obj` | NOT_APPLICABLE | — | — | 既有 ignore |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未访问真实库 |

## Closeout Record

- 待独立 Review 通过后由 DSH 填写。
