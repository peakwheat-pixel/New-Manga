# FEA-13-ID-3 证据索引

- Task：`FEA-13-ID-3`（DatabaseId 原语 + manifest/恢复过滤 + backup.list 投影；FEA-13 片 3）
- Base：`54453abb3`；依赖 `FEA-13-BK2-1`、`FEA-13-COV-2`（done）
- 依据：C-01b SC-18、C-09 SC-B03、`FEA-13-scope-r1.md` §7 片 3
- 证据批次：`fea-13-id-3`

## 实现口径

| 项 | 实现 |
|---|---|
| 存储 | 既有 `application_metadata`（`metadata_key='database_id'`，`value_json`=UUID4 JSON 字符串）；**无新 DDL、schema 仍 v9** |
| 写 | `ensure_database_id`：`INSERT OR IGNORE` + 回读（原子、幂等）；装配在迁移成功后调用（pre-migration 备份如实报告 unknown） |
| 读 | `read_database_id`：缺失/非法 → `None`（unknown，**不是**空串/书名/hash） |
| manifest | v2 包写 `database_id`（unknown → `null`）；**pre-migration 钩子同样读取真实身份**（r1 R-001 修复）；v1 包无该字段 → 读作 unknown |
| restore | 双方均已知且不等 → `BACKUP_DATABASE_MISMATCH`（category=`conflict`、非 retryable），在 `pre_restore` 之前拒绝（零副作用）；任一 unknown → 允许（不阻断旧包恢复） |
| list | `backup.list` 每项含 `database_id`（null=unknown）；C# `BackupPackageInfo.DatabaseId?` 解析（默认 null，兼容旧构造点） |

## 判别证据

| AC | 结果 | 证据 |
|---|---|---|
| AC1 原子写入/幂等 | `ensure` 两次返回同一 UUID4；schema 版本不变 | `logs/pytest-backup-suite.log`（80 passed） |
| AC2 旧库回填 | 无键时 `read` = None、`ensure` 后写入恰好一行；回填前 unknown | 同上 |
| AC3 manifest 携带 | 包内 `database_id` == 库身份；**pre_migration 包也携带**（新增用例）；unknown 时 `null`；v1 包读作 unknown 且不被阻断（新增用例） | 同上 |
| AC4 跨库拒绝零副作用 | 不同身份 → `BACKUP_DATABASE_MISMATCH`；无 `pre_restore`、包字节不变 | 同上 |
| AC5 list 投影 | 列表项含 `database_id`；C# 字段解析（build 0/0） | 同上 + `logs/build.log` |
| AC6 门禁 | 备份面 80 passed；build 0/0；Host 备份相邻测试 3 passed；`check.ps1`/pins 见卡与 Handoff | 同上 |
| 变异判别 | 关闭跨库门禁（`if False and ...`）→ **1 failed / 7 passed**；复原后 8 passed | `logs/mutation-db-gate.log` |

## 命令

```powershell
python -m pytest tests/storage/test_nmbak_backup.py tests/storage/test_nmbak_format.py tests/storage/test_nmbak_coverage.py tests/storage/test_nmbak_identity.py tests/storage/test_backup_restore.py tests/core/test_core_backup_wire.py tests/infrastructure/test_nmbak_startup_backup.py -q
dotnet build apps/desktop-avalonia/NewManga.sln -c Debug --nologo
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests --no-build --filter "FullyQualifiedName~Backup"
```

## 残余 / 未覆盖

- **UI 展示**：`backup.list` 的 `database_id` 仅到 CoreClient DTO，未接 UI（另案）。
- **wire 文档**：V11R `backup.list` 行未同步 `database_id`（本片未改 wire 文档；按需后续同步）。
- **C# 解析测试**：`ParseBackupPackage` 的 null 保持语义仅由编译验证（C# 测试文件不在本片 allowed_paths）；登记后续。
- **纵深防御**：manifest 无签名，手工改 `database_id=null` 可关闭跨库门禁（R-002 已归一化 strip；签名/摘要属后续硬化）。
- **跨机恢复**：不同机器的 DPAPI/身份差异不在本片（属片 4 恢复语义）。
- `tests/storage` 全量未跑（环境 >10 分钟），备份面 7 文件 80 passed 覆盖改动面。
- 全量 `dotnet test` 未跑（本片 C# 仅 DTO 字段 + 解析；build 0/0 + Host 备份相邻 3 passed）。
