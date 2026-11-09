# FEA-13-BK2-1 证据索引

- Task：`FEA-13-BK2-1`（backup/2 写端 + 版本协商 + backup/1 只读 adapter；FEA-13 首片）
- Base：`1aad960b8`；依据：`ADJ-2026-11-09-FEA13-ERRATA-AND-SPLIT`（D1 字面值）+ `FEA-13-scope-r1.md` §7 片 1
- 日期：2026-11-09；证据批次：`fea-13-bk2-1-r3`

## 实现口径

| 项 | 结果 |
|---|---|
| 写端 | `create()` 只写 v2：`format:"nmbak"`、`version:2`、`database_id:null`（片 3 填实）、`schema_version`、每项 `sha256`+`size_bytes`；**无** `format_version` |
| 读端 | `_negotiate_manifest` 同时识别 v1（`nm-backup`/`format_version:1`）与 v2；v1 恢复完全只读、包字节/mtime 不变 |
| 两类失败分离 | ①格式/版本「整数但不支持」→ `BACKUP_FORMAT_UNSUPPORTED`（Core：validation、非 retryable）；②已知 format 但版本字段**缺失/非整数** → `BACKUP_CORRUPT`（manifest 结构损坏） |
| 零副作用 | 拒绝发生在 `pre_restore` 创建之前：DB/managed/包字节不变、不产生 `pre_restore` |

## 判别证据

| AC | 结果 | 证据 |
|---|---|---|
| AC1 写端 v2 | `format/version/database_id` + `size_bytes`（revision + page originals）断言、无 `format_version` | `logs/pytest-backup-suite.log`（66 passed） |
| AC2 v1 只读 adapter | v1 字面包恢复成功；包 sha256 + mtime 前后一致 | 同上 |
| AC3 v3 拒绝零副作用 | `BACKUP_FORMAT_UNSUPPORTED`；DB/managed/包字节不变、无 `pre_restore` | 同上 |
| AC4 未知 format | 同码，且显式断言 `!= "BACKUP_CORRUPT"` | 同上 |
| AC5 变异判别 | ①v3 分支改 `BACKUP_CORRUPT` → **1 failed / 5 passed**；②写端 `version` 改 1 → **1 failed**；复原后 **27 passed** | `logs/mutation-v3-corrupt.log`、`logs/mutation-writer-version.log` |
| AC6 门禁 | `check.ps1` 默认 + `-TaskPath` PASS；pins 18/18 | 卡/Handoff |

**测试口径**（两处数字不同不矛盾）：`pytest-backup-suite.log` = 备份相关 **5 个文件 66 passed**（含 base 既有测试）；`renewal` 类小集合 **2 个文件 27 passed** 仅用于变异前后的快速判别。

## 证据局限（如实登记）

1. **v1 golden fixture 的构造方式**：本片测试的 v1 包由**本片 v2 产物改写 manifest**（`format:"nm-backup"`+`format_version:1`）合成，未使用 base-writer 原始产物。**「无 `page_original_refs` 的旧包」已由既有测试 `test_old_package_without_page_originals_still_restores` 覆盖**（base 已有、本轮复跑通过），不属缺口；仍缺的是「base writer 产物逐字节 golden」——已登记为片 2/后续残余。
2. **SC-B07 ④（包内加密源授权元数据段）不在本片、也不在 6 片拆分内**：`FEA-13-scope-r1.md` §6.3 指出该数据的写域在 Core 之外（Host 侧），强行归入会把本片扩成跨域卡；处置为**独立裁决/后续立项**，本片只交付 ②③⑤⑥。
3. **wire 端到端**：AC3 的 `category/retryable` 在 Core 映射表层断言；wire envelope 端到端属 `tests/core/test_core_backup_wire.py`（不在本片 allowed_paths），未加新用例——登记残余。
4. **日志时间**：三份日志同一 `# time`（同一证据批次生成），`# command` 为真实命令；变异日志在命令后标注「after mutation … (expected RED)」。

## 命令

```powershell
python -m pytest tests/storage/test_nmbak_backup.py tests/storage/test_nmbak_format.py tests/storage/test_backup_restore.py tests/core/test_core_backup_wire.py tests/infrastructure/test_nmbak_startup_backup.py -q
```

## 说明

- 旧二进制读 v2 包会在 `_read_manifest` fail-closed 拒绝（`format` 不匹配）——预期行为（旧端拒读新格式）。
- `tests/storage` 全量在本环境 >10 分钟未完成（已如实记录）；备份相关 5 文件 66 passed 覆盖本片改动面。
- 新增负测：`test_known_format_with_missing_or_non_integer_version_is_corrupt`（R-006）；新增断言：`test_page_original_refs_record_digest_and_size`（R-007）。
