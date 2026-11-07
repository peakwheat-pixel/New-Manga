---
task_id: FEA-12-CORE-C04B-INDEX-L4-1
author: index-impl（DSH Agent Teams 成员；Lead `lead`）
recipient: DeepSeek Harness
base_commit: 02c1a26d1
start_head: d7823a0e0
delivery_head: e593cc9d7
status: in_review
supersedes_handoff: null
---

# Handoff — FEA-12-CORE-C04B-INDEX-L4-1（`media_artifacts.book_id` 索引 / v9 迁移，0 pin）

- Task：`doc/tasks/FEA-12-CORE-C04B-INDEX-L4-1.md`（`status` 由 Lead 维护，本 Handoff 不改）
- 交付日期：2026-11-08（Asia/Shanghai）
- 权限依据：卡面 `status: ready`（Owner=`index-impl`）+ 权威 scope review
  `doc/reviews/FEA-12-CORE-C04B-INDEX-L4-scope-r1.md`（verdict `recommended`；§2 判定 **0 pin**、§2.4 迁移形状、
  §7 卡面草案）+ 冻结记录 `doc/plan/FEA-CONTRACT-FROZEN-C04b.md` §4A **L-4**
- **三处 head**：卡面 `base_commit=02c1a26d1` → 本卡**实际工作起点** `d7823a0e0`（Lead 的任务释放 commit：
  scope review 入库 + 冻结释放；**仅 5 个 `doc/**` 文件**，工作树 clean；本卡对该 commit 零回改）→
  **`delivery_head=e593cc9d7`**（实现+测试 commit；本 Handoff / EV / 证据 / 卡面交付记录为紧随其后的
  docs/evidence 提交）
- 环境：Windows 11 / PowerShell 7 / CPython 3.14 / .NET 9；真实 production `MigrationRunner` + `default_migrations()`；
  所有临时 SQLite 库在仓外 `G:\CODEX\New Manga.workspace\index-l4\`；**未打开真实用户 DB/AppData/外部卷**
- **未 push、未 closeout**：Task `status`、冻结记录 §4A L-4 状态、STATUS/PLAN/LEDGER 由 Lead 维护

## 1. 交付结果（AC-1…AC-6 全 MET；卡面已 `<<MET>>`，`status` 未改）

| AC | 结果 | 关键证据 |
|---|---|---|
| **AC-1 迁移形状与字节保留** | MET | `schema.py` +`SCHEMA_VERSION_V9=9`、+`MIGRATION_V9_NAME="v9__media_artifacts_book_index"`、+`MIGRATION_V9_SQL`（**单条裸 `CREATE INDEX idx_media_artifacts_book ON media_artifacts(book_id);`**，无 `IF NOT EXISTS`）、+1 元组项；新测试硬编码 v1–v8 的 `(版本, 名称, sha256(SQL))` 逐项比对**不变** |
| **AC-2 旧库升级与守恒** | MET | 生产 runner 从 **v1…v8 每个起点**升到 v9：`schema_migrations=9` + `application_metadata=9`、`PRAGMA index_list('media_artifacts')` 含索引且列为 `book_id`；5 张表行数 + preview/revision ids/pinned/`book_delete_inventory` **逐值守恒**；二次 `apply_pending()==[]`、重新 `open_database` 不重建不报错；注入 v9 事务内失败 → 停 v8 + **无索引残留** + 库仍可读写；旧 v8 runner → `SchemaTooNewError`、`open_database(latest=8)` → `TOO_NEW` 零写 |
| **AC-3 计划生效与结果等价** | MET | preview **生产 SQL**（trace 捕获）：v8 `SCAN ma` → v9 **`SEARCH ma USING INDEX idx_media_artifacts_book (book_id=?)`**，SQL 文本前后完全相同；`list_book_artifact_revision_ids`/`list_book_pinned_revision_ids` 同样由 `SCAN` → `SEARCH`；`SELECT COUNT(*) ... WHERE book_id=?` 与 `DELETE ... WHERE book_id=?` 走 **覆盖索引**（两处 SQL 字面量经 `inspect.getsource` 与 `library.py` 逐字比对）；preview/删除面结果**逐值等价** |
| **AC-4 硬编码 v8 断言同步** | MET | 5 处按 8→9 等值更新（`tests/fea09/test_v7_migration.py:76/139/248/263`、`tests/fea11/test_source_gate_unify.py:213` `[8]→[8,9]`、`Fea11SourceIpcTests.cs:60`）；`ipc_seed.py:87-90` 为动态 `MAX(schema_version)`，无需改；**DSH 扩域批准**（2026-11-08）后修 `tests/storage/test_upgrade_schema_data.py` 的派生断言（见 §6） |
| **AC-5 门禁** | MET | 定向 **76→92**（扩域版 **109**）；全量 pytest **3372/10 → 3390 passed / 10 skipped / 0 failed**；全量 .NET **1683/0/96 → 1683/0/96**；`verify_pins` **18/18**；`check.ps1` 默认 + `-TaskPath` **PASS(3 warnings)**；API **EXIT 0**；scope ⊆ allowed_paths；`git diff --check` 空 |
| **AC-6 证据与不夸大** | MET | EV/Manifest/Closeout 完整；未写「preview 回到旧谓词水平 / 性能已全面恢复」；limitation 含「未回到旧谓词（1.53×）」与「回滚只走备份」 |

## 2. 生产改动（唯一：`src/infrastructure/sqlite/schema.py`，+22/−0）

```python
SCHEMA_VERSION_V9 = 9

MIGRATION_V9_NAME = "v9__media_artifacts_book_index"

#: （注释说明 L-4 背景、裸 CREATE INDEX 的 fail-loud 取舍、单事务语义）
MIGRATION_V9_SQL = "CREATE INDEX idx_media_artifacts_book ON media_artifacts(book_id);"

# default_migrations() 末尾：
Migration(SCHEMA_VERSION_V9, MIGRATION_V9_NAME, MIGRATION_V9_SQL),
```

- **裸 `CREATE INDEX`**（无 `IF NOT EXISTS`）：幂等由版本门（`migrator.py:161-163`）提供；同名索引已存在时
  **fail-loud**（typed 失败、DB 停 v8），避免「静默跳过却记为已应用」的假成功。代价：需人工 `DROP INDEX` 后重试
  （limitation）。
- `CREATE INDEX` 与 `schema_migrations`/`application_metadata` 同事务（`migrator.py:227-276`）：失败即回滚，
  要么 v9 + 索引在，要么 v8 + 零残留（实测，见 §4 失败路径）。
- **零改动**：`library.py` 查询语义/排序键、其它表/索引/DDL、v1–v8 迁移字节、契约字节、wire/命令/能力/错误码/
  `PROTOCOL_MINOR`、依赖、STATUS/PLAN/LEDGER。
- `schema.py` SHA-256：`5fe87b693554d5e7b1f230f73cab75e04528466105b1d9f3a8f972dd68f92ce6`（git blob `2fcd79d2…`）。

## 3. 测试改动

1. **新增** `tests/core/test_v9_migration.py`（+402 行，16 用例）：见 EV §3。核心判据是**生产发布方法/生产 SQL**
   （trace 捕获 + `inspect.getsource` 比对），不是手抄 SQL。
2. **断言同步**：`tests/fea09/test_v7_migration.py`（4 处 `==8→==9`）、`tests/fea11/test_source_gate_unify.py`
   （`[8]→[8,9]`）、`Fea11SourceIpcTests.cs`（`8→9`）；均等值更新、未放宽。
3. **`tests/storage/test_upgrade_schema_data.py`**（DSH 扩域批准，+25/−1）：
   - 新增 `_index_names(connection)`（`sqlite_master` 的 `type='index'` 且非 `sqlite_%`）；
   - 迁移前采集索引集；`assert new_tables` → **`assert new_tables or new_indexes`**；
   - **v8 起点显式断言** `"idx_media_artifacts_book" in new_indexes`；
   - 保留 `assert all(name in after for name in new_tables)`；v1–v7 起点断言不变。

## 4. 验证证据（实跑；`delivery_head=e593cc9d7`）

| 场景 | 命令 | 结果 | 日志 |
|---|---|---|---|
| 定向 before | `pytest tests/fea09/test_v7_migration.py tests/fea11/test_source_gate_unify.py tests/core/test_core_delete_preview_commands.py tests/core/test_core_delete_commands.py -q -p no:warnings`（临时 stash 回退到工作起点） | **76 passed** | `logs/targeted-before.txt` |
| 定向 after | `pytest tests/core/test_v9_migration.py tests/fea09/test_v7_migration.py tests/fea11/test_source_gate_unify.py tests/core/test_core_delete_preview_commands.py tests/core/test_core_delete_commands.py -q -p no:warnings` | **92 passed** | `logs/targeted-after.txt` |
| 定向 after（扩域版） | 上列 + `tests/storage/test_upgrade_schema_data.py` | **109 passed** | `logs/targeted-after-extended.txt` |
| 全量 before | `pytest tests -q -p no:warnings --tb=no` | **3372 passed / 10 skipped**（273.61 s） | `logs/full-before.txt` |
| 全量 after | 同上 | **3390 passed / 10 skipped / 0 failed**（255.46 s） | `logs/full-after.txt` |
| .NET before | `dotnet build ...; dotnet test ... --no-build` | **1683 passed / 0 failed / 96 skipped** | `logs/dotnet-build-before.txt`、`logs/dotnet-test-before.txt` |
| .NET after | 同上 | **1683 passed / 0 failed / 96 skipped**；build 0 warning/0 error | `logs/dotnet-build-after.txt`、`logs/dotnet-test-after.txt` |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)**，EXIT 0 | `logs/pins.txt` |
| check（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)**，EXIT 0 | `logs/check-default.txt` |
| check（`-TaskPath`） | `... -TaskPath doc/tasks/FEA-12-CORE-C04B-INDEX-L4-1.md` | **PASS (3 warnings)**，EXIT 0 | `logs/check-taskpath.txt` |
| API inventory | `python tools/generate_api_inventory.py --check` | **EXIT 0** | `logs/api-inventory.txt` |
| scope / 零漂移 | `git diff d7823a0e0 --name-only`；`git diff d7823a0e0 -- doc/plan doc/contracts ...` | 实现 diff ⊆ allowed_paths；`doc/plan`/`doc/contracts`/依赖 **空**；`apps/**` 仅允许的 C# 断言 | `logs/scope.txt` |
| 指纹 | `Get-FileHash` + `git hash-object` | 见 `logs/sha256-files.txt` | `logs/sha256-files.txt` |
| EXPLAIN + 迁移报告 | 仓外 `G:\CODEX\New Manga.workspace\index-l4\evidence_runner.py` | v8 `SCAN ma` → v9 `SEARCH ma USING INDEX ...`；数据/结果等价；二次 apply 空 | `logs/discriminative-and-explain.txt` |

## 5. 判别性实验（RED → sha256 MATCH → GREEN）

`logs/discriminative-and-explain.txt` §3：

1. 交付 `schema.py` sha256 = `5fe87b69…`。
2. **临时把 `MIGRATION_V9_SQL` 改为 `SELECT 1;`**（去掉 `CREATE INDEX`，即「迁移记成 v9 但索引不存在」的假成功态）
   → sha256 `3449af76…` → `pytest tests/core/test_v9_migration.py tests/storage/test_upgrade_schema_data.py`
   = **13 failed / 20 passed**（含 preview 计划实测 `SCAN ma`、`list_book_artifact_revision_ids` 实测 `SCAN ma`、
   storage `[v8]` 实测 `assert ([] or [])`）。
3. **逐字节复原** → sha256 `5fe87b69…` **MATCH** → 重跑 = **33 passed**。

## 6. 越界发现与 DSH 裁决记录（如实登记）

- 实现完成后全量首跑 = **1 failed / 3389 passed / 10 skipped**，唯一失败
  `tests/storage/test_upgrade_schema_data.py::test_synthetic_legacy_data_survives_full_upgrade[v8]`。
- **根因**：该测试 `LEGACY_VERSIONS = [m.schema_version for m in MIGRATIONS[:-1]]` 在 v9 后自动包含 v8 起点，
  而用例断言「升级必须新增 `LATEST_TABLES` 中的表」；v9 是**纯索引**迁移 → `new_tables=[]` 必然失败。
  这是版本 bump 的结构性耦合（scope review §5 的 5 处清单按硬编码 8 列，未覆盖这处派生断言）。
- **处置**：我未擅自改该文件（不在原 `allowed_paths`），上报 Lead；**DSH 裁决（2026-11-08，裁决人=DSH）授权扩
  `allowed_paths` 加该文件**，按「不得跳断言/改方向」做 §3 的最小修复；修复后全量 **3390/10 / 0 failed**。
- 属主：`index-impl`；未改任何断言方向、未删除/跳过任何用例。

## 7. Limitation / 不构成什么（不夸大）

- **不承诺**「preview 回到旧谓词水平 / 性能已全面恢复」：索引只消除**全库扫描放大**；scope review §3.3 实测
  60k 厚数据集 8.90 → 4.36 ms/书，仍为旧谓词 2.85 ms/书的 **1.53×**（artifacts 驱动 + 7 键临时排序的固有成本）。
  本卡只做**计划与等价性**机械判据，不重跑基准计时。
- **未在真实用户库演练**；大库首启建索引成本为线性外推（60k ≈ 30 ms；600k ≈ 0.3 s；6M ≈ 3 s，均非实测）。
- **裸 `CREATE INDEX` 遇同名索引会 fail-loud**：不支持态需人工 `DROP INDEX` 后重试。
- **回滚只走升级前备份**（C-01b SC-37；无自动降级）；失败自动回滚停 v8。
- **不改损坏行语义**（`book_id` 与页归属不一致仍按 `book_id`）与 **L-5**（`preview_lifecycle` 按 page 归属漏清）。
- 写放大未做并发/大库压测（scope review 2,000 行插入为噪声级，本卡未复测）。
- **不构成**契约变更（18 pins 零改动，非 UNFREEZE）；**不构成** push 授权与 Task closeout；
  L-4 的「未修 → 已修」由 Lead 在 closeout 维护。

## 8. 建议下一步（Lead）

1. 派发**上下文独立 Review**（只读 `delivery_head=e593cc9d7`；reviewer 未参与本卡实现）。
2. Review approved 后 closeout：冻结记录 §4A **L-4** → 「已修（本卡）」；STATUS/PLAN/LEDGER 更新；push。
3. 如未来另有必须 bump schema 的卡，按 scope review §6.2 优先合并，避免 v9/v10 反复 bump 与断言更新。

## 9. 复现

```powershell
cd 'G:\CODEX\New Manga'
C:/Python314/python.exe -m pytest tests/core/test_v9_migration.py tests/fea09/test_v7_migration.py `
  tests/fea11/test_source_gate_unify.py tests/core/test_core_delete_preview_commands.py `
  tests/core/test_core_delete_commands.py tests/storage/test_upgrade_schema_data.py -q -p no:warnings
C:/Python314/python.exe -m pytest tests -q -p no:warnings --tb=no
dotnet build apps/desktop-avalonia/NewManga.sln -c Release
dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build
git checkout -- verification/FEA-09   # .NET 测试产物复原（跑后必做）
pwsh -NoProfile -File tools/governance/verify_pins.ps1
pwsh -NoProfile -File tools/governance/check.ps1
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-CORE-C04B-INDEX-L4-1.md
C:/Python314/python.exe tools/generate_api_inventory.py --check
C:/Python314/python.exe 'G:\CODEX\New Manga.workspace\index-l4\evidence_runner.py'   # EXPLAIN/迁移报告/判别性
```
