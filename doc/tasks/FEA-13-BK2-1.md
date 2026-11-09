---
id: FEA-13-BK2-1
title: backup/2 写端 + 版本协商 + backup/1 只读 adapter（FEA-13 首片）
kind: implementation
governance_version: 3
status: done
approval: 裁决 `ADJ-2026-11-09-FEA13-ERRATA-AND-SPLIT`（D1–D5 errata，0 pin；D1 定 v1/v2 字面值）+ 独立 scope review `doc/reviews/FEA-13-scope-r1.md` §7 片 1 + DSH 2026-11-09 扩域：`src/bootstrap/core_service.py` **仅**错误码映射表新增一行（`BACKUP_FORMAT_UNSUPPORTED`），不改其它
suggested_owner: dsh
owner: dsh
reviewer: 独立上下文子代理 r1/r2（`doc/reviews/FEA-13-BK2-1-r1.md`、`-r2.md`；r1 approved、r2 approved，均非实现会话）
depends_on: []
base_commit: 1aad960b8
branch: null
worktree: null
integration_commit: 7fc975e46
delivery_head: ac1882fc8
canonical_evidence_status: complete
resource_closeout_status: complete
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
| EV-BK2-README | AC1–AC6 | `verification/FEA-13-BK2-1/README.md` | `-` | `c1a2cfca2160b4f73088c8042047488bd83c22938234f78d9064cf723ae0be4d` | CANONICAL |
| EV-BK2-SUITE | AC1–AC4,AC6 | `verification/FEA-13-BK2-1/logs/pytest-backup-suite.log` | `-` | `901f5377d6e2ba933b99fe50a5b4d9686ad263f9a2e8e02bc76d50a3ad2045b1` | CANONICAL |
| EV-BK2-MUT-V3 | AC5 | `verification/FEA-13-BK2-1/logs/mutation-v3-corrupt.log` | `-` | `6cc1f94fcc3f914a5923d6bbda0d034e8335b29fb7f1cca73c9154a57438e485` | CANONICAL |
| EV-BK2-MUT-WRITER | AC5 | `verification/FEA-13-BK2-1/logs/mutation-writer-version.log` | `-` | `57de51bacae5d7db59397b3d4e0387b96719085603620994b19d9a1a714d36b0` | CANONICAL |
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

## Review 处置（r1，独立子代理 doc/reviews/FEA-13-BK2-1-r1.md：approved P0=0/P1=0/P2=3/P3=9）

| Finding | 处置 |
|---|---|
| R-001（P2）v1 golden 由 v2 relabel 合成、未覆盖无 `page_original_refs` 旧包 | README §证据局限如实登记；base-writer golden 与历史包回放列入片 2/后续残余（reviewer 探针已证行为正确） |
| R-002（P2）mutation 日志缺命令头/EXIT；README 25/25 与 64 passed 口径不一致 | 3 份日志全部重生成（`# command/# shell/# time/# EXIT=`）；README 口径统一为「备份相关 5 文件 64 passed」 |
| R-003（P2）SC-B07 ④ 加密源授权元数据未实现却写「SC-B07 落地」 | 措辞收窄为 **②③⑤⑥**；④ 与 SC-B01 源授权元数据入包**不在本片、也不在 6 片拆分内**，按 `doc/reviews/FEA-13-COV-2-sc01-decision.md` 单列 `FEA-13-SRC-6`（proposed），README 与 Handoff 同步 |
| R-004（P3）module/`_verify_package` docstring 陈旧 + 死 except | 已更新 docstring、删除死 `except (TypeError, ValueError)` |
| R-005（P3）`_as_int` 接受 `"2"` 无历史依据 | 删除 `_as_int`；版本字段只接受 int（bool 排除） |
| R-006（P3）缺 version 归 unsupported 而非 corrupt | 已知 format 但版本字段缺失/非整数 → `BACKUP_CORRUPT`；整数但不受支持 → `BACKUP_FORMAT_UNSUPPORTED` |
| R-007（P3）AC1 未断言 size_bytes；`... or True` 恒真断言 | 补 `size_bytes` 断言；恒真断言改为对 zip 内 `library.db` 的 sha256 正确断言 |
| R-008（P3）测试名仍写 v1 | 改为 `test_create_package_contains_frozen_v2_layout` |
| R-009（P3）wire 端到端不在 allowed_paths | 登记残余（wire envelope 用例另案） |
| R-010（P3）旧注释/设计文档未更新 | 登记残余（`core_service.py` 仅允许映射一行，注释另案） |
| R-011（P3）STATUS/PLAN/LEDGER 越出 allowed_paths | 属 DSH 生命周期写入惯例（先例 `7abc9194a`），登记不改 |
| R-012（P3）C-09 §9 控制字符 | append-only 记录，不改字节约；登记 |
| R-013（P3，r2）`_negotiate_manifest` docstring 与 corrupt 分支矛盾 | 已改写为「两类失败分离」的完整描述 |
| R-014（P3，r2）test 模块 docstring 仍写 v1 | 已改为 backup/2 v2 |
| R-015（P3，r2）README 局限第 1 条与既有测试不符 | 已更正：`test_old_package_without_page_originals_still_restores` 覆盖旧包；仍缺 base-writer 字节 golden（登记片 2/后续） |

**r2 复审**（独立子代理 `doc/reviews/FEA-13-BK2-1-r2.md`，head `389f30309`）：**approved**（FIXED 7 / PARTIAL 5 / OPEN 0；无新增 P0/P1）。r2 的 5 项 PARTIAL 已在本轮逐项处置：R-001 措辞更正 + 残余登记、R-002 日志重采（真实命令头/批次标注/口径并列）、R-003 措辞改为「④ 不在 6 片拆分内，独立裁决」、R-006 新增缺失/非整数负测、R-007 新增 page_original_refs digest/size 断言。AC1–AC6 维持 MET。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main；base `1aad960b8`） | NOT_APPLICABLE | — | — | 未创建 worktree |
| temp | pytest 临时目录（`tmp_path`） | NOT_APPLICABLE | — | — | 测试隔离 fixture |
| build | NOT_APPLICABLE（纯 Python） | NOT_APPLICABLE | — | — | 无构建产物 |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未访问真实库 |

## Closeout Record

- **2026-11-09 / DSH（关账）**：AC1–AC6 全部 MET；C-09 SC-B07 的 ②③⑤⑥ 落地（④ 独立裁决）。
- **Review**：r1 独立子代理 **approved**（P0=0/P1=0/P2=3/P3=9）→ 处置；r2 独立子代理 **approved**（FIXED 7 / PARTIAL 5 / OPEN 0；无新增 P0/P1）→ 5 项 PARTIAL 逐项处置（负测、page-original 断言、日志头、措辞收窄、旧包覆盖更正）。
- **门禁**：备份相关 5 文件 **66 passed**（EXIT 0）；变异① 1 failed/5 passed（EXIT 1）、变异② 1 failed（EXIT 1）、复原 27 passed（EXIT 0）；check.ps1 默认 + -TaskPath PASS（3 warnings）；erify_pins 18/18。
- **残余**：base-writer 字节 golden（片 2/后续）；SC-B07 ④ 独立裁决；wire envelope 端到端（另案）；core_service.py:6959-6962 注释更新（另案，片内仅允许映射一行）。
- **交付/集成**：实现 `ac1882fc8`；r2 返修 `389f30309`；r3 处置 `7fc975e46`（`integration_commit`）。本收口提交仅翻转状态与指针。
- **边界**：0 契约字节、0 pin 重算、0 C# 改动；diff ⊆ allowed_paths（`core_service.py` 仅映射一行 + 注释未动）。