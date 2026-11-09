---
id: FEA-13-BK2-1
title: backup/2 写端 + 版本协商 + backup/1 只读 adapter（FEA-13 首片）
kind: implementation
governance_version: 3
status: in_review
approval: 裁决 `ADJ-2026-11-09-FEA13-ERRATA-AND-SPLIT`（D1–D5 errata，0 pin；D1 定 v1/v2 字面值）+ 独立 scope review `doc/reviews/FEA-13-scope-r1.md` §7 片 1 + DSH 2026-11-09 扩域：`src/bootstrap/core_service.py` **仅**错误码映射表新增一行（`BACKUP_FORMAT_UNSUPPORTED`），不改其它
suggested_owner: dsh
owner: dsh
reviewer: 待指派（必须独立上下文）
depends_on: []
base_commit: 1aad960b8
branch: null
worktree: null
integration_commit: null
delivery_head: pending
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/FEA-13-BK2-1
allowed_paths:
  - doc/tasks/FEA-13-BK2-1.md
  - doc/reviews/FEA-13-BK2-1-*.md
  - doc/handoffs/FEA-13-BK2-1-*.md
  - verification/FEA-13-BK2-1/**
  - src/infrastructure/sqlite/nmbak.py
  - tests/storage/test_nmbak_backup.py
  - tests/storage/test_nmbak_format.py
  - src/bootstrap/core_service.py
out_of_scope:
  - `core_service.py` 只允许错误码映射表新增一行；不改 handler/其它逻辑
  - 不改 C-09/C-01b 契约字节、18 pins、M2-C1、V11R wire 文档
  - 不实现 `DatabaseId` 真值（片 3 `FEA-13-ID-3`）：v2 manifest 的 `database_id` 本片写 `null`（unknown）
  - 不实现覆盖清单二期（片 2）、merge restore（片 4）、调度保留（片 5）、数据根迁移（单列）
  - 不改 `SqliteBackupService`（生产 0 接线的旧路径）
  - 不 push
---

# FEA-13-BK2-1：backup/2 写端 + 版本协商 + backup/1 只读 adapter

## 来源与冻结依据

- `FEA-13` scope review r1 §7 片 1（首片）；裁决 `ADJ-2026-11-09-FEA13-ERRATA-AND-SPLIT` **D1** 定死字面值：
  - `backup/1`（只读兼容）：`format:"nm-backup"` + `format_version:1`
  - `backup/2`（写端）：`format:"nmbak"` + `version:2`（不再写 `format_version`）
- C-09 SC-B07 要求：版本协商 + legacy adapter 只读 + 写端只写 v2；`backup/1` 只读恢复、**不就地升级**。

## 实现口径

| 项 | 要求 |
|---|---|
| 写端 | 只写 v2 manifest（`format:"nmbak"`、`version:2`、`database_id:null`（unknown，片 3 填实）、`schema_version`、每项 `sha256`+`size_bytes`） |
| 读端 | 同时识别 v1（`nm-backup`/`format_version:1`）与 v2；v1 包恢复完全只读（包字节与 mtime 不变） |
| 拒绝 | 未知 `format`/`version`（含 v3）→ typed `BACKUP_FORMAT_UNSUPPORTED`（category=`validation`、retryable=`false`），**零副作用**：DB 不变、managed 不变、不产生 `pre_restore` 包、包字节不变 |
| 错误码 | `BACKUP_CORRUPT` 仅用于「v1/v2 结构损坏」；格式不支持不得伪装为 corrupt |

## Acceptance Criteria

- [x] **AC1 写端 v2**：`create()` 产物 `manifest.json` 有 `format:"nmbak"`、`version:2`、`database_id:null`、`schema_version`、每项 `sha256`+`size_bytes`；**无** `format_version` 键。 <<MET>>
- [x] **AC2 v1 只读 adapter**：真实 v1 包（`format:"nm-backup"`、`format_version:1`）恢复成功；恢复前后包字节 sha256 与 mtime 不变（不就地升级）。 <<MET>>
- [x] **AC3 v3 拒绝零副作用**：`version:3` 包 → `BACKUP_FORMAT_UNSUPPORTED`（category=validation、retryable=false）；DB/managed 不变、不产生 `pre_restore` 包、包字节不变。 <<MET>>
- [x] **AC4 未知 format**：未知 `format` 字符串 → 同一个 `BACKUP_FORMAT_UNSUPPORTED`（不伪装 `BACKUP_CORRUPT`）。 <<MET>>
- [x] **AC5 变异判别**：把 v3 分支改成 `BACKUP_CORRUPT` → AC3/AC4 用例 RED；把写端 `version` 改成 1 → AC1 RED；变异后复原（sha256 一致）。 <<MET>>
- [x] **AC6 门禁**：定向 pytest（备份面）全绿；`check.ps1`（默认 + `-TaskPath`）PASS；pins 18/18；diff ⊆ allowed_paths。 <<MET>>

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-BK2-README | AC1–AC6 | `verification/FEA-13-BK2-1/README.md` | `-` | `017258736df5df3ebdc5107763be6ed41ae2dc684897a79937616915fe78ac90` | CANONICAL |
| EV-BK2-SUITE | AC1–AC4,AC6 | `verification/FEA-13-BK2-1/logs/pytest-backup-suite.log` | `-` | `76760d13222b5c3d154e55a014def7d99d35123ddb931c5b89ae5301310d6929` | CANONICAL |
| EV-BK2-MUT-V3 | AC5 | `verification/FEA-13-BK2-1/logs/mutation-v3-corrupt.log` | `-` | `9b4119aea9181b7d315fe95c810623bae195fadd0eb2a6a4df732243dfbcf882` | CANONICAL |
| EV-BK2-MUT-WRITER | AC5 | `verification/FEA-13-BK2-1/logs/mutation-writer-version.log` | `-` | `2fe45c4be6dd20a21a9760b932ed108c894a178e0f8740040955874c08f9e566` | CANONICAL |
## 证据计划

| # | 命令 | 判别 |
|---|---|---|
| E1 | `python -m pytest tests/storage/test_nmbak_backup.py tests/storage/test_nmbak_format.py -q` | 0 failed |
| E2 | v1 golden fixture（由修复前 writer 生成并快照 sha256）恢复 | 恢复成功 + 包字节/mtime 不变 |
| E3 | v3/未知 format 负向 | `BACKUP_FORMAT_UNSUPPORTED` + 零副作用（DB/managed/pre_restore/包字节） |
| E4 | 变异（v3→BACKUP_CORRUPT、写端 version=1） | 至少 1 例 RED；复原后 sha256 一致 |
| E5 | `check.ps1` 默认 + `-TaskPath`；`verify_pins` | PASS / 18/18 |

## 风险与回退

- **旧二进制读新包**：旧端 `_read_manifest` 会 fail-closed 拒绝 v2（`format` 不匹配）——符合方案「旧端拒写新 schema」的同类语义，需在 Handoff 明确为预期。
- **`test_nmbak_backup.py:122-123`** 的 v1 布局断言改为 v2 布局断言（在 allowed_paths 内）。
- 回退：`git revert` 单提交；不涉及数据迁移。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main；base `1aad960b8`） | NOT_APPLICABLE | — | — | 未创建 worktree |
| temp | pytest 临时目录（`tmp_path`） | NOT_APPLICABLE | — | — | 测试隔离 fixture |
| build | NOT_APPLICABLE（纯 Python） | NOT_APPLICABLE | — | — | 无构建产物 |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未访问真实库 |

## Closeout Record

- 待独立 Review 通过后由 DSH 填写。
