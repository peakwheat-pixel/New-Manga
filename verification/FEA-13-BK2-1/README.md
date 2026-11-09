# FEA-13-BK2-1 证据索引

- Task：`FEA-13-BK2-1`（backup/2 写端 + 版本协商 + backup/1 只读 adapter；FEA-13 首片）
- Base：`1aad960b8`；依据：`ADJ-2026-11-09-FEA13-ERRATA-AND-SPLIT`（D1 字面值）+ `FEA-13-scope-r1.md` §7 片 1
- 日期：2026-11-09

## 实现口径

| 项 | 结果 |
|---|---|
| 写端 | `create()` 只写 v2：`format:"nmbak"`、`version:2`、`database_id:null`（片 3 填实）、`schema_version`、每项 `sha256`+`size_bytes`；**无** `format_version` |
| 读端 | `_negotiate_manifest` 同时识别 v1（`nm-backup`/`format_version:1`）与 v2；v1 恢复完全只读、包字节/mtime 不变 |
| 拒绝 | 未知 format / 不支持的整数版本 → `BACKUP_FORMAT_UNSUPPORTED`（Core 映射 `category=validation`、`retryable=false`），零副作用；**已知 format 但版本字段缺失/非整数 → `BACKUP_CORRUPT`**（结构损坏，不是「App 太旧」） |
| 错误码 | `BACKUP_CORRUPT` 只用于结构损坏；格式不支持不伪装为 corrupt |

## 判别证据（口径：备份相关 5 个测试文件，64 passed）

| AC | 结果 | 证据 |
|---|---|---|
| AC1 写端 v2 | `format/version/database_id` 断言 + `size_bytes` 断言 + 无 `format_version` | `logs/pytest-backup-suite.log`（64 passed） |
| AC2 v1 只读 adapter | v1 字面包恢复成功；包 sha256 + mtime 前后一致 | 同上 |
| AC3 v3 拒绝零副作用 | `BACKUP_FORMAT_UNSUPPORTED`；DB/managed/包字节不变、无 `pre_restore` | 同上 |
| AC4 未知 format | 同码，且显式断言 `!= "BACKUP_CORRUPT"` | 同上 |
| AC5 变异判别 | ①v3 分支改 `BACKUP_CORRUPT` → **1 failed / 3 passed**；②写端 `version` 改 1 → **1 failed**（read-back 拒绝）；复原后 **25 passed** | `logs/mutation-v3-corrupt.log`、`logs/mutation-writer-version.log` |
| AC6 门禁 | `check.ps1` 默认 + `-TaskPath` PASS；pins 18/18 | 卡/Handoff |

## 证据局限（如实登记）

1. **v1 golden fixture 的构造方式**：本片测试的 v1 包由**本片 v2 产物改写 manifest**（`format:"nm-backup"`+`format_version:1`）合成，未使用 base-writer 原始产物，也**未覆盖「无 `page_original_refs`」的历史包**。reviewer 用独立探针验证了该路径行为正确；真正的 base-writer golden 与历史包回放列入残余（片 2/后续）。
2. **SC-B07 ④（包内加密源授权元数据段）不在本片**：本片只实现 ②③⑤⑥（v2 写端/版本协商/legacy 只读 adapter/未知格式 typed 码）；④ 与 SC-B01 的「源授权元数据入包」归片 2（`FEA-13-COV-2`）或独立裁决。
3. **wire 端到端**：AC3 的 `category/retryable` 在 Core 映射表层断言；wire envelope 端到端在 `tests/core/test_core_backup_wire.py`（不在本片 allowed_paths），未加新用例。

## 命令

```powershell
python -m pytest tests/storage/test_nmbak_backup.py tests/storage/test_nmbak_format.py tests/storage/test_backup_restore.py tests/core/test_core_backup_wire.py tests/infrastructure/test_nmbak_startup_backup.py -q
```

## 说明

- 旧二进制读 v2 包会在 `_read_manifest` fail-closed 拒绝（`format` 不匹配）——预期行为（旧端拒读新格式）。
- `tests/storage` 全量在本环境 >10 分钟未完成（已如实记录）；备份相关 5 文件 64 passed 覆盖本片改动面。
