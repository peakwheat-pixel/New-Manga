# FEA-13-BK2-1 证据索引

- Task：`FEA-13-BK2-1`（backup/2 写端 + 版本协商 + backup/1 只读 adapter；FEA-13 首片）
- Base：`1aad960b8`；依据：`ADJ-2026-11-09-FEA13-ERRATA-AND-SPLIT`（D1 字面值）+ `FEA-13-scope-r1.md` §7 片 1
- 日期：2026-11-09

## 实现口径

| 项 | 结果 |
|---|---|
| 写端 | `create()` 只写 v2：`format:"nmbak"`、`version:2`、`database_id:null`（片 3 填实）、`schema_version`、每项 `sha256`+`size_bytes`；**无** `format_version` |
| 读端 | `_negotiate_manifest` 同时识别 v1（`nm-backup`/`format_version:1`）与 v2；v1 恢复完全只读、包字节/mtime 不变 |
| 拒绝 | 未知 format / 不支持的 version → `BACKUP_FORMAT_UNSUPPORTED`（Core 映射 `category=validation`、`retryable=false`），零副作用 |
| 错误码 | `BACKUP_CORRUPT` 只用于 v1/v2 结构损坏；格式不支持不伪装为 corrupt |

## 判别证据

| AC | 结果 | 证据 |
|---|---|---|
| AC1 写端 v2 | 断言 `format/version/database_id` 且无 `format_version` | `logs/pytest-backup-suite.log`（25/25 含该断言） |
| AC2 v1 只读 adapter | 真实 v1 字面包恢复成功；包 sha256 + mtime 前后一致 | 同上（`test_writer_emits_v2_and_legacy_v1_restores_without_touching_the_package`） |
| AC3 v3 拒绝零副作用 | `BACKUP_FORMAT_UNSUPPORTED`；DB/managed/包字节不变、无 `pre_restore` | 同上（`test_unsupported_v2_major_version_is_typed_and_has_zero_side_effects`） |
| AC4 未知 format | 同码，且显式断言 `!= "BACKUP_CORRUPT"` | 同上 |
| AC5 变异判别 | ①v3 分支改 `BACKUP_CORRUPT` → **1 failed / 3 passed**；②写端 `version` 改 1 → **1 failed**（read-back 拒绝）；复原后 **64 passed** | `logs/mutation-v3-corrupt.log`、`logs/mutation-writer-version.log` |
| AC6 门禁 | 备份相关 64 passed；`check.ps1`/pins 见卡与 Handoff | `logs/pytest-backup-suite.log` |

## 命令

```powershell
python -m pytest tests/storage/test_nmbak_backup.py tests/storage/test_nmbak_format.py tests/storage/test_backup_restore.py tests/core/test_core_backup_wire.py tests/infrastructure/test_nmbak_startup_backup.py -q
```

## 说明

- 旧二进制读 v2 包会在 `_read_manifest` fail-closed 拒绝（`format` 不匹配）——预期行为（旧端拒写/拒读新格式），已在 Handoff 登记。
- `test_nmbak_backup.py` 的 v1 布局断言已更新为 v2 断言（该文件在 allowed_paths 内）。
- 未跑全量 pytest（storage 全量在本环境超 10 分钟，改跑备份相关子集；全量门禁由后续集成验证覆盖）。
- 全量 `tests/storage` 未完成（超时终止），已如实记录。
