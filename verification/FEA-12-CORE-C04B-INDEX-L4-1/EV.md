# FEA-12-CORE-C04B-INDEX-L4-1：`media_artifacts.book_id` 索引（v9 迁移）— 证据（EV）

> 本 EV 只陈述**实改/实跑**事实。本卡是**实现卡（0 pin）**：`schema.py` 追加 v9 迁移，只创建一条
> `CREATE INDEX idx_media_artifacts_book ON media_artifacts(book_id);`（裸 `CREATE INDEX`），并同步因版本
> bump 而受影响的断言；**v1–v8 迁移字节零改动**、契约字节零改动、`library.py` 查询语义零改动。
> 目标是把 `FEA-12-CORE-C04B-RESIDUAL-3` 把 artifact 成员谓词改为 `media_artifacts.book_id = ?` 后引入的
> **`SCAN ma` 全库放大**（冻结记录 §4A **L-4**）从计划层消除；**不承诺**回到旧谓词水平（见 §9 limitation）。

- Task：`doc/tasks/FEA-12-CORE-C04B-INDEX-L4-1.md`（`status`/closeout 由 Lead 维护）
- `delivery_head`：见 Handoff（`doc/handoffs/FEA-12-CORE-C04B-INDEX-L4-1-<head>.md`）与卡面交付记录
- `base_commit`：`02c1a26d1`（卡面）；本卡**实际工作起点** `d7823a0e0`（Lead 的任务释放 commit：
  scope review 入库 + 冻结释放，仅 5 个 `doc/**` 文件；工作树 clean，本卡对该 commit 零回改）
- 依赖：`FEA-12-CORE-C04B-RESIDUAL-3`（done `25dc1523c`，引入 `ma.book_id` 谓词）、`FEA-12-CORE`（done）
- 环境：Windows 11 / PowerShell 7 / CPython 3.14；真实 production `MigrationRunner` + `default_migrations()`；
  临时库全部在仓外 `G:\CODEX\New Manga.workspace\index-l4\`（`tmp/**`），**从未打开真实用户库/AppData/外部卷**
- 权威依据：`doc/reviews/FEA-12-CORE-C04B-INDEX-L4-scope-r1.md`（§2 0 pin 判定、§2.4 迁移形状、§3 基准、§5 成本）
  + 冻结记录 `doc/plan/FEA-CONTRACT-FROZEN-C04b.md` §4A **L-4**

## 1. 生产改动（唯一：`src/infrastructure/sqlite/schema.py`，+22/−0 行）

```python
SCHEMA_VERSION_V9 = 9

MIGRATION_V9_NAME = "v9__media_artifacts_book_index"
MIGRATION_V9_SQL = "CREATE INDEX idx_media_artifacts_book ON media_artifacts(book_id);"

# default_migrations() 末尾追加：
Migration(SCHEMA_VERSION_V9, MIGRATION_V9_NAME, MIGRATION_V9_SQL),
```

- **裸 `CREATE INDEX`（无 `IF NOT EXISTS`）**：按 scope review §2.4 取舍——幂等由版本门
  （`migrator.py:161-163`）提供；若某库已被人工建过同名索引，迁移必须 **fail-loud**（typed 失败、DB 停 v8），
  而不是「静默跳过却记为已应用」。代价（需人工 `DROP INDEX` 后重试）登记为 limitation。
- `CREATE INDEX` 与 `schema_migrations`/`application_metadata` 写入在**同一事务**（`migrator.py:227-276`），
  失败即回滚：要么 v9 + 索引在，要么 v8 + 无索引残留（§5 失败路径实测）。
- **`library.py`、其它表/索引/DDL、wire/命令/能力/错误码/`PROTOCOL_MINOR`、依赖：零改动**。
- `schema.py` SHA-256（交付字节）：`5fe87b693554d5e7b1f230f73cab75e04528466105b1d9f3a8f972dd68f92ce6`。

## 2. 断言同步（AC-4；版本 bump 的既有成本，逐处按 8→9 等值更新）

| 文件:行 | 原文 | 更新后 | 说明 |
|---|---|---|---|
| `tests/fea09/test_v7_migration.py:76` | `...fetchone()[0] == 8` | `== 9` | v7 全链后最新版本 |
| `tests/fea09/test_v7_migration.py:139` | `...fetchone()[0] == 8` | `== 9` | validator 通过路径 |
| `tests/fea09/test_v7_migration.py:248` | `...fetchone()[0] == 8` | `== 9` | 可读原件路径 |
| `tests/fea09/test_v7_migration.py:263` | `...fetchone()[0] == 8` | `== 9` | 空库迁移路径 |
| `tests/fea11/test_source_gate_unify.py:213` | `== [8]` | `== [8, 9]` | `_seed_v7_legacy_library` 从 v7 起升到最新，现应用 v8+v9 |
| `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11SourceIpcTests.cs:60` | `Assert.Equal(8, ...)` | `Assert.Equal(9, ...)` | seed receipt 的真实库版本（`ipc_seed.py:87-90` 动态 `MAX(schema_version)`，**无需改**） |
| `tests/storage/test_upgrade_schema_data.py:741-743` | `assert new_tables`（由 `LEGACY_VERSIONS = MIGRATIONS[:-1]` 派生） | 见 §5.2（DSH 扩域批准后已修） | v9 是**纯索引**迁移，v8 起点不新增表 → 该断言结构性失效；修复为「升级后必须有新 schema 对象（表**或**索引）」+ v8 起点显式断言 `idx_media_artifacts_book` 新出现，不放宽方向 |

- **未放宽断言方向**：上表前 6 处均为等值更新（`8`→`9`、`[8]`→`[8,9]`），无删除/跳过/`>=` 化。
- `tests/fea11/test_source_sync.py:993` 的 `latest_known_schema_version=8` 位于空库分支（`connection.py:356-357`
  返回 `EMPTY`，随后用 `default_migrations()` 升到最新），不在本卡 `allowed_paths`，**未改**且全量实测未失败。

## 3. 新迁移测试（`tests/core/test_v9_migration.py`，16 用例，全绿）

| 用例 | 判据 |
|---|---|
| `test_v9_shape_and_v1_v8_bytes_are_frozen` | `SCHEMA_VERSION_V9==9`、名称、SQL **逐字**等于卡面要求、**不含 `IF NOT EXISTS`**、`default_migrations()` 共 9 项且版本连续 1..9、`MIGRATIONS[:8]` 的 `(版本, 名称, sha256 SQL)` 逐项等于硬编码冻结值（=v1–v8 字节保留） |
| `test_upgrade_from_legacy_version_creates_the_book_index[v1..v8]`（8 个参数化） | 生产 `MigrationRunner` 从每个 legacy 起点升级：`applied` 恰为 `start+1..9`、`schema_migrations=9`、`application_metadata=9`、`PRAGMA index_list(media_artifacts)` 含索引且 `index_info` 列为 `book_id`；第二次 `apply_pending()==[]`；**重新 `open_database`** 后仍 `READY/writable`、不重建、不报错 |
| `test_v8_upgrade_preserves_rows_and_query_results` | v8→v9 前后 `list_book_artifact_current_pointers`/`list_book_artifact_revision_ids`/`list_book_pinned_revision_ids` 结果、5 张表行数、artifacts 抽样行**逐值相等** |
| `test_book_delete_inventory_is_unchanged_by_the_index` | `book_delete_inventory(book-a, [], storage=None)` 升级前后**逐值相等**（含 `artifact_current_pointers`/`artifacts` 计数） |
| `test_v9_failure_leaves_the_database_at_v8_without_the_index` | 在 v9 SQL 后注入必失败语句 → 抛 `sqlite3.Error`、版本仍 8、索引**不存在**、库仍可读写（无半迁移残留） |
| `test_old_v8_runner_refuses_the_v9_database` | 只认识 v1..v8 的 runner 对 v9 库抛 `SchemaTooNewError` |
| `test_open_database_reports_too_new_to_a_v8_reader` | `open_database(..., latest_known_schema_version=8)` → `TOO_NEW`/只读、写操作抛 `OperationalError`（零写） |
| `test_preview_statement_scans_on_v8_and_searches_the_index_on_v9` | **同一生产 SQL**（trace 捕获）：v8 计划含 `SCAN ma` 且无索引；v9 计划含 `SEARCH ma USING INDEX idx_media_artifacts_book`、不含 `SCAN`；SQL 文本前后**完全相同**；preview 结果逐值相等 |
| `test_delete_face_enumeration_and_count_use_the_book_index` | `list_book_artifact_revision_ids`/`list_book_pinned_revision_ids` 计划含索引且无 `SCAN`；`SELECT COUNT(*) ... WHERE book_id=?` 与 `DELETE ... WHERE book_id=?` 计划走**覆盖索引**；两处 SQL 字面量经 `inspect.getsource(SqliteLibraryRepository)` 确认是**生产原文**（非手抄） |

## 4. AC-1：v1–v8 迁移字节保留（硬编码 checksum，实测通过）

| 版本 | 名称 | `Migration.checksum`（sha256(SQL)） |
|---|---|---|
| 1 | `v1__storage_base` | `f68cb4ab8facda4b6e701a934ed14b240bce13c50fe1527a3989de1c987994bd` |
| 2 | `v2__library_region_persistence` | `b984eaeeb5a3a162040d2de458f09ecde1479519d30a48fd7c36118295875d5b` |
| 3 | `v3__production_pipeline_persistence` | `359d97f42cad9cb18d676ffc113abae4e81cb237c4841ef82262a8736518a0c2` |
| 4 | `v4__reading_export_storage` | `c8e0b4899026784bda958c49e6e1d13896f7ac083dafd1acf04a030677a88394` |
| 5 | `v5__detach_pipeline_history` | `6b12ad337ab2fe0fb0b4d6bdd6835a69166c080a36fc1ac80326ff4faa03597c` |
| 6 | `v6__plugin_runtime` | `eef3ddb5dadd819e3af6de030aec8edff010e1a0d012409bf14330fb5fb43331` |
| 7 | `v7__source_storage` | `abbf4e5f9415f392596faebc38690b6a58dd7f96941f51802621b68a2a3f8a91` |
| 8 | `v8__source_sync` | `d8e76e80a5abadcb335edc7be75c1cffbd8e5311d45d2fe3fa5d49f4c82b21d1` |

- 上述值由**改动前 HEAD** 的生产模块实算并硬编码进测试；v9 落地后测试复算仍全部相等 → v1–v8 的
  SQL/name/checksum 未变（既有库的 `_verify_checksum` 不会因此失败）。

## 5. AC-2：真实升级、守恒、幂等、失败闭锁

### 5.1 迁移报告（临时库，生产迁移链）

`logs/discriminative-and-explain.txt` §1 原文摘要：

```
v8 max(schema_migrations)   = 8 ; application_metadata = 8
v8 media_artifacts indexes  = ['idx_media_artifacts_page', 'sqlite_autoindex_media_artifacts_1']
v8 -> v9 applied            = [9]
v9 max(schema_migrations)   = 9 ; application_metadata = 9
v9 media_artifacts indexes  = ['idx_media_artifacts_book', 'idx_media_artifacts_page', 'sqlite_autoindex_media_artifacts_1']
row counts (before)         = {'books': 2, 'chapters': 2, 'pages': 3, 'media_artifacts': 4, 'artifact_revisions': 3}
row counts (after)          = {'books': 2, 'chapters': 2, 'pages': 3, 'media_artifacts': 4, 'artifact_revisions': 3}
data/query equivalence      = True
second apply_pending        = []
```

### 5.2 既有升级测试的派生断言修复（DSH 扩域批准，已修复并实测）

`tests/storage/test_upgrade_schema_data.py` 的 `LEGACY_VERSIONS = [m.schema_version for m in MIGRATIONS[:-1]]`
在 v9 后自动包含 **v8 起点**，而用例断言「升级必须新增 `LATEST_TABLES` 中的表」——v9 只新增索引，故必然
`new_tables=[]` → 该参数化用例失败（全量首跑实测 `1 failed`）。DSH 裁决（2026-11-08）授权扩 `allowed_paths`
加该文件做**不放宽方向**的最小修复：

- 新增 `_index_names(connection)`（`sqlite_master` 中 `type='index'` 且非 `sqlite_%`）；
- 迁移前采集索引集，迁移后计算 `new_indexes`；
- `assert new_tables` → **`assert new_tables or new_indexes`**（每个 legacy 起点都必须新增表**或**索引）；
- **v8 起点显式断言** `idx_media_artifacts_book in new_indexes`；
- 保留 `assert all(name in after for name in new_tables)`；v1–v7 起点断言行为不变（它们仍有新表）。

实测：`tests/storage/test_upgrade_schema_data.py` = **17 passed**（含 `[v8]`）。判别性：把 v9 SQL 换成
`SELECT 1;`（无索引）后，该文件的 `[v8]` 用例同样 RED（`assert ([] or [])`，见 §9）。

## 6. AC-3：计划生效与结果等价（EXPLAIN QUERY PLAN，同一库同一 SQL）

| 查询（生产 SQL，trace 捕获） | v8（无索引） | v9（有索引） |
|---|---|---|
| `list_book_artifact_current_pointers`（preview） | `SCAN ma` → `SEARCH p ... LEFT-JOIN` → `SEARCH c ... LEFT-JOIN` → `USE TEMP B-TREE FOR ORDER BY` | **`SEARCH ma USING INDEX idx_media_artifacts_book (book_id=?)`** → 同上两个 LEFT-JOIN → `USE TEMP B-TREE FOR ORDER BY` |
| `list_book_artifact_revision_ids` | `SCAN ma` → `SEARCH ar USING INDEX idx_artifact_revisions_artifact` | **`SEARCH ma USING INDEX idx_media_artifacts_book (book_id=?)`** → `SEARCH ar ...` |
| `list_book_pinned_revision_ids`（artifact 分支） | `SCAN ma` | **`SEARCH ma USING INDEX idx_media_artifacts_book (book_id=?)`** |
| `SELECT COUNT(*) FROM media_artifacts WHERE book_id = ?`（inventory 计数） | `SCAN media_artifacts` | **`SEARCH media_artifacts USING COVERING INDEX idx_media_artifacts_book (book_id=?)`** |
| `DELETE FROM media_artifacts WHERE book_id = ?`（删除事务） | `SCAN media_artifacts` | **`SEARCH media_artifacts USING COVERING INDEX idx_media_artifacts_book (book_id=?)`** |

- **结果等价**：preview / revision ids / pinned / `book_delete_inventory` 在升级前后**逐值相等**（§3、§5.1）。
- 计划不是手抄 SQL 得出：preview/revision-id/pinned 三处由 `set_trace_callback` 捕获**发布方法实际执行的 SQL**
  再 `EXPLAIN QUERY PLAN`；COUNT/DELETE 两处 SQL 字面量在测试内与 `library.py` 源码逐字比对。
- 据 scope review §3.3：索引消除的是**扫描放大**，不是全部差值（60k 厚数据集 8.90 → 4.36 ms/书，仍 1.53× 旧谓词）；
  本卡**不重跑基准计时**，只做计划与等价性机械判据。

## 7. AC-5：门禁数字（before → after）

| 门禁 | before（工作起点 `d7823a0e0`，未改） | after（本卡） | 结果 |
|---|---|---|---|
| 定向 pytest（v9 新测试 + fea09 v7 迁移 + fea11 gate unify + delete preview/commands） | **76 passed**（4 个既有文件，实跑） | **92 passed**（+16 新用例） | 不降 |
| 定向 pytest 扩域版（上列 + `tests/storage/test_upgrade_schema_data.py`） | — | **109 passed**（=92 + storage 17） | 不降 |
| 全量 pytest `tests -q --tb=no` | **3372 passed / 10 skipped**（273.61 s） | **3390 passed / 10 skipped / 0 failed**（255.46 s；=3372+18） | 不降 |
| 全量 .NET `dotnet test ... -c Release --no-build` | **1683 passed / 0 failed / 96 skipped** | **1683 passed / 0 failed / 96 skipped** | 不降 |
| `dotnet build ... -c Release` | 0 warning / 0 error | 0 warning / 0 error | 通过 |
| `verify_pins.ps1` | 18/18（契约零改动） | **PIN AUDIT: PASS (all 18)**，EXIT 0 | 不变 |
| `check.ps1`（默认） | PASS (3 warnings) | **PASS (3 warnings)**，EXIT 0 | 不变 |
| `check.ps1 -TaskPath` | PASS (3 warnings) | **PASS (3 warnings)**，EXIT 0 | 不变 |
| `generate_api_inventory.py --check` | EXIT 0 | **EXIT 0** | 不变 |
| `git diff --check` | — | 空（EXIT 0） | 通过 |
| scope | — | 实现 diff ⊆ `allowed_paths`（见 §8） | 通过 |

## 8. scope / 零漂移

- 本卡 diff（相对工作起点 `d7823a0e0`）：`src/infrastructure/sqlite/schema.py`、`tests/fea09/test_v7_migration.py`、
  `tests/fea11/test_source_gate_unify.py`、`tests/storage/test_upgrade_schema_data.py`（DSH 扩域批准）、
  `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11SourceIpcTests.cs`、`tests/core/test_v9_migration.py`、
  `verification/FEA-12-CORE-C04B-INDEX-L4-1/**`、卡面/Handoff；全部 ⊆ `allowed_paths`。
- 相对卡面 `base_commit=02c1a26d1` 额外含 Lead 的释放 commit `d7823a0e0`（`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、
  `doc/TASK_LEDGER.md`、scope review、本卡）——那是 Lead 的任务释放动作（`out_of_scope` 明列 STATUS/PLAN/LEDGER
  由 Lead 维护），**非本卡实现 diff**；本卡对该 commit 零回改。
- `doc/plan/**`、`doc/contracts/**`、依赖（`pyproject.toml`/`requirements*.txt`/`uv.lock`）**零 diff**；
  `apps/**` 仅 `Fea11SourceIpcTests.cs` 一处断言（allowed）；`verification/FEA-09/**` 在 .NET 测试后已
  `git checkout -- verification/FEA-09` 复原（零 diff）。

## 9. 判别性（AC-2/AC-3 的 RED→GREEN）

`logs/discriminative-and-explain.txt` §3（仓外脚本 `G:\CODEX\New Manga.workspace\index-l4\evidence_runner.py`）：

1. 交付字节 `schema.py` sha256 = `5fe87b69…`。
2. **临时把 `MIGRATION_V9_SQL` 改为 `SELECT 1;`（去掉 `CREATE INDEX`，即「迁移记成 v9 但索引不存在」的假成功态）**
   → sha256 `3449af76…` → `pytest tests/core/test_v9_migration.py tests/storage/test_upgrade_schema_data.py`
   = **13 failed / 20 passed**（shape 断言、8 个起点升级、守恒、preview 计划、删除面计划、storage `[v8]` 起点全部 RED；
   preview 计划实测变为 `SCAN ma | ...`、`list_book_artifact_revision_ids` 实测 `SCAN ma`、
   storage 实测 `assert ([] or [])`）。
3. **逐字节复原** → sha256 `5fe87b69…` **MATCH** → 重跑 = **33 passed**（16 + 17）。

## 10. 不夸大与 limitation

- **不承诺**「preview 回到旧谓词水平 / 性能已全面恢复」：索引只消除**全库扫描放大**；60k 厚数据集
  8.90 → 4.36 ms/书（scope review §3.3），仍为旧谓词 2.85 ms/书的 1.53×，差值来自 artifacts 驱动 + 7 键临时排序，
  属谓词语义固有成本。
- **未在真实用户库演练**：所有库为仓外临时库；大库首启建索引成本按行数线性外推（60k ≈ 30 ms；600k ≈ 0.3 s；
  6M ≈ 3 s，均为外推，非实测）。
- **裸 `CREATE INDEX` 遇同名索引会 fail-loud**：不支持态需人工 `DROP INDEX` 后重试（不用 `IF NOT EXISTS` 以免假成功）。
- **回滚只走升级前备份**（C-01b SC-37 口径，无自动降级）；失败自动回滚、DB 停 v8。
- **不改损坏行语义**（`book_id` 与 page 归属不一致仍按 `book_id` 归属）与 **L-5**（`preview_lifecycle` 按 page
  归属漏清，保留未修）。
- 写放大未做并发压测；scope review 在 2,000 行插入规模测得噪声级（本卡未复测）。

## 11. 真实性声明

1. 所有数字来自本机本次实跑；日志在 `verification/FEA-12-CORE-C04B-INDEX-L4-1/logs/**`，仓外原始脚本/临时库在
   `G:\CODEX\New Manga.workspace\index-l4\`。
2. 未打开真实用户数据库/AppData/外部卷；未改任何契约字节（`verify_pins.ps1` 18/18）；未改 STATUS/PLAN/LEDGER；
   未 push、未 closeout。
3. 全量 pytest 的最终数字见下方「最终门禁」（修复 §5.2 后重跑，替换本节占位）。

## 最终门禁（实跑，最终交付树）

- 全量 pytest：**3390 passed / 10 skipped / 0 failed**（255.46 s，`logs/full-after.txt`；起点 3372/10）
- 定向 pytest（卡面 5 文件）：**92 passed**（`logs/targeted-after.txt`）；扩域版 6 文件：**109 passed**
  （`logs/targeted-after-extended.txt`）
- 全量 .NET：**1683 passed / 0 failed / 96 skipped**（`logs/dotnet-test-after.txt`；起点 1683/0/96）；
  `dotnet build -c Release` 0 warning / 0 error（`logs/dotnet-build-after.txt`）；跑后
  `git checkout -- verification/FEA-09`（工作树零 diff）
- `verify_pins.ps1`：**PIN AUDIT: PASS (all 18)**，EXIT 0（`logs/pins.txt`）
- `check.ps1` 默认 + `-TaskPath`：**PASS (3 warnings) ×2**，EXIT 0（`logs/check-default.txt`、`logs/check-taskpath.txt`）
- `generate_api_inventory.py --check`：**EXIT 0**（`logs/api-inventory.txt`）
- scope / 零漂移 / `git diff --check`：见 `logs/scope.txt`（`EXIT=0 output=[]`）
