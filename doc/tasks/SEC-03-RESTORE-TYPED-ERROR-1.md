---
id: SEC-03-RESTORE-TYPED-ERROR-1
title: nmbak restore 失败收敛为 typed error 并返回 rollback ID
kind: implementation
governance_version: 3
status: done
resume_status: done
approval: user_authorized_2026-11-14 (所有任务交 DSH、自动裁决/规划、全部授权、无需用户介入)
suggested_owner: DSH
owner: DSH
reviewer: "DSH auto-adjudication (2026-11-14 owner directive); independent sub-agent review optional"
depends_on: [SEC-02-REMOTE-DISPOSITION-1]
base_commit: 509f99ad6
branch: main
worktree: G:/CODEX/New Manga
integration_commit: baeda3042fd674a8cdf94331475adb3124014352
delivery_head: baeda3042fd674a8cdf94331475adb3124014352
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/SEC-03-RESTORE-TYPED-ERROR-1
allowed_paths:
  - src/infrastructure/sqlite/nmbak.py
  - tests/infrastructure/**
  - tests/storage/**
  - verification/SEC-03-RESTORE-TYPED-ERROR-1/**
  - doc/tasks/SEC-03-RESTORE-TYPED-ERROR-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
---

# SEC-03-RESTORE-TYPED-ERROR-1：nmbak restore 失败收敛为 typed error 并返回 rollback ID

## 来源与目标

`SEG-B-PROBES-002`（Medium / High confidence，TRIAGED）：restore 的隔离磁盘写失败复现为 `database_changed=true`、`typed_error=false`、`rollback_id_in_error=false`、`pre_restore_packages=1`。根因锚点：`src/infrastructure/sqlite/nmbak.py:1180-1210` 的逐文件 `write_bytes` 路径未包装为带 `pre_restore` id 的 typed error。目标：把 restore 文件 I/O 失败收敛到冻结错误合同（如 `BACKUP_RESTORE_INCOMPLETE`），并在错误中返回可用的 pre_restore `backup_id`；不改变既有成功 restore 语义与冻结契约字节。

## Acceptance Criteria

- [x] **AC1**：只读核对 C-07 / nmbak 冻结错误语义与 restore 调用链，记录当前行为、错误类型与上层 Core/wire 映射。 <<MET>>
- [x] **AC2**：restore 文件写失败返回 typed error（`BACKUP_RESTORE_INCOMPLETE` 或合同允许等价类型），并携带可用的 pre_restore `backup_id`；数据库状态与 pre_restore 包保留语义有明确断言。 <<MET>>
- [x] **AC3**：故障注入测试覆盖单文件失败、多文件部分写、数据库状态、pre_restore 包可用与既有成功 restore 回归；相关测试通过并记录命令/EXIT。 <<MET>>
- [x] **AC4**：证据 pin、四项门禁、资源 closeout 完成，DSH 自动裁决；真实库/断电/多文件部分写等未测项标 NOT_RUN。 <<MET>>

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| SEC03-PYTEST-LOG-1 | AC3 | `verification/SEC-03-RESTORE-TYPED-ERROR-1/logs/pytest-sec03.log` | `baeda3042fd674a8cdf94331475adb3124014352` | `A1BD55001A7E3AE0BFB0E433773EB20738A1938A329A8D8506F867E0192CB11A` | CANONICAL | BLOB |
| SEC03-PYTEST-RESULT-1 | AC3 | `verification/SEC-03-RESTORE-TYPED-ERROR-1/evidence/pytest-sec03.json` | `baeda3042fd674a8cdf94331475adb3124014352` | `91CC7C7252098206F771FB33AAD82A1DA4F14A783AE577A3CD89291377FF213E` | CANONICAL | BLOB |
| SEC03-SOURCE-1 | AC2 | `src/infrastructure/sqlite/nmbak.py` | `baeda3042fd674a8cdf94331475adb3124014352` | `72166B9A0EBD43B2A47D3A6AEEEFDF32F67F1CD8BF9A0514C77D7051199C53EB` | CANONICAL | BLOB |
| SEC03-TEST-1 | AC3 | `tests/storage/test_nmbak_restore_typed_error.py` | `baeda3042fd674a8cdf94331475adb3124014352` | `E14A0E21CAFE3AD6D07EBB2EA1031619B4E746A73F40854E6F43343C86333272` | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga | PRESERVE_REFERENCED | doc | verification/SEC-03-RESTORE-TYPED-ERROR-1/evidence/pytest-sec03.json | 主工作区保留 |
| task-env | - | NOT_APPLICABLE | doc | verification/SEC-03-RESTORE-TYPED-ERROR-1/evidence/pytest-sec03.json | 无独立 task-env |
| agent-output | - | NOT_APPLICABLE | doc | verification/SEC-03-RESTORE-TYPED-ERROR-1/evidence/pytest-sec03.json | 无 agent-output |
| artifact | verification/SEC-03-RESTORE-TYPED-ERROR-1 | PRESERVE_REFERENCED | doc | verification/SEC-03-RESTORE-TYPED-ERROR-1/evidence/pytest-sec03.json | 测试证据保留 |
| dataset/model/test-material | - | NOT_APPLICABLE | doc | verification/SEC-03-RESTORE-TYPED-ERROR-1/evidence/pytest-sec03.json | 合成 fixture |
| exchange | - | NOT_APPLICABLE | doc | verification/SEC-03-RESTORE-TYPED-ERROR-1/evidence/pytest-sec03.json | 无外部传输 |

## 允许修改范围

- `src/infrastructure/sqlite/nmbak.py`（restore 失败路径错误包装）
- `tests/infrastructure/**`（新增/修改 restore 故障注入测试）
- `verification/SEC-03-RESTORE-TYPED-ERROR-1/**`
- 本 Task 卡、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`

## 禁止范围

冻结契约字节、共享 Schema 变更、其他产品模块、真实用户数据、远端操作、安装/发布、历史改写。

## 测试要求

故障注入（只读隔离 fixture）验证 typed error、rollback ID、pre_restore 包可用、DB 状态；既有成功 restore 回归；记录命令、EXIT 与限制。
