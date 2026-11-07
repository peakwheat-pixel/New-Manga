---
task: FEA-12-CORE-C04B-INDEX-L4-1
title: C-04b L-4（media_artifacts.book_id 索引 / v9 迁移）实现 Review（r1）
reviewer: fresh subagent
reviewer_kind: subagent
session: 231cd1fe-cffa-431d-bb67-3b22feede577
author: index-impl
base_commit: 02c1a26d1
start_head: d7823a0e0
delivery_head: e593cc9d7
docs_evidence_head: 9618056f2
reviewed_head: e593cc9d7
verdict: approved
p0: 0
p1: 0
p2: 0
p3: 6
date: 2026-11-08
---

# Review：FEA-12-CORE-C04B-INDEX-L4-1（`media_artifacts.book_id` 索引 / v9 迁移）

> 我是 Lead（`lead`）委派的 **fresh subagent**（独立上下文；session `231cd1fe-cffa-431d-bb67-3b22feede577`），
> **未参与**本卡的实现/返修，也**未参与** `FEA-12-CORE`、`FEA-12-CORE-C04B-RESIDUAL-1/2/3` 的任何实现、返修或复核，
> 未参与 C-04b/C-15/C-17/CORE 的契约起草或 implementation scope review。本次只读被审对象；唯一写入仓库的文件是本报告。
> 临时备份、检查脚本与探针数据库写在 `G:\CODEX\New Manga.workspace\C04B-RESIDUAL\review-index\`；未 `git add/commit/push`。
> 结论只对 `reviewed_head=e593cc9d7`（代码）与 `docs_evidence_head=9618056f2`（卡/Handoff/EV/Manifest/logs）有效。

## 0. 结论（先给）

- **verdict: `approved`**；**P0=0、P1=0、P2=0、P3=6**。P3 全部为文档/门禁口径与测试强度备注（§4），不改变 AC-1…AC-6 的 MET 判定。
- 独立复算的关键结论：
  - `schema.py` 相对起点 `d7823a0e0` 是 **+22/−0**（只有新增行）；从 `git show` 载入两个 head 的生产模块逐项比较，**v1–v8 的 `(version, name, sql, checksum)` 8/8 完全相同**；新测试 `FROZEN_V1_V8` 的 8 个 sha256 与实算 **8/8 MATCH**。
  - v9 只加 `CREATE INDEX idx_media_artifacts_book ON media_artifacts(book_id);`（裸 `CREATE INDEX`，无 `IF NOT EXISTS`），在 `default_migrations()` 追加第 9 项；生产路径的 `latest_known` 由 `default_migrations()` 动态推导（`core_assembly.py:1162-1164`、`backup.py:189`、`nmbak.py:684`），**没有残留的硬编码 v8 latest**。
  - 定向 6 文件 pytest：**109 passed**（8.40 s，我的实跑）；判别性：把 v9 SQL 换成 `SELECT 1;` → **13 failed / 20 passed**（6.39 s），逐字节复原 `sha256=5fe87b69…` **MATCH** + `touch` → **33 passed**（3.21 s），工作树 clean。
  - `verify_pins.ps1` **PIN AUDIT: PASS (all 18)**（EXIT 0）；`check.ps1` 默认与 `-TaskPath` 均 **PASS (3 warnings)**（EXIT 0）；`generate_api_inventory.py --check` **EXIT 0**；`git diff --check` 空。
  - 证据 **20/20** 个 artifact 的 bytes 与 sha256 同时匹配 Manifest 与卡面 Canonical Evidence 表。
  - 同名索引风险实测：会 `OperationalError: index idx_media_artifacts_book already exists`，DB 停 v8、仍可写；人工 `DROP INDEX` 后重试成功到 v9 → 与 limitation 一致，fail-closed 可接受。

## 1. 审查对象与 head 口径

| 项 | 值 |
|---|---|
| 卡 | `doc/tasks/FEA-12-CORE-C04B-INDEX-L4-1.md`（`status: ready`；AC-1…AC-6 已 `<<MET>>`；closeout 字段 pending；含 DSH 扩域批准说明） |
| 实现 + 测试 | `e593cc9d7`（`e593cc9d70be3b2568569aea43f313b0bc28c413`），6 个文件：`schema.py` + 5 个测试/断言文件 |
| docs/evidence | `9618056f2`（卡交付记录 + Handoff + `verification/FEA-12-CORE-C04B-INDEX-L4-1/**`，23 个文件） |
| 实施起点 | `d7823a0e0`（Lead 释放 commit）；卡面 `base_commit=02c1a26d1` |
| 依赖/依据 | `FEA-12-CORE-C04B-RESIDUAL-3`（done `25dc1523c`）、`FEA-12-CORE`（done）；scope review `doc/reviews/FEA-12-CORE-C04B-INDEX-L4-scope-r1.md`；冻结记录 §4A **L-4**；RESIDUAL-3 Review R3-002 |
| 证据/Handoff | `verification/FEA-12-CORE-C04B-INDEX-L4-1/{EV.md, RESOURCE-MANIFEST.json, logs/**}`；`doc/handoffs/FEA-12-CORE-C04B-INDEX-L4-1-e593cc9d7.md` |
| 仓库状态 | `main`、HEAD=`9618056f2`、工作树 clean、`e593cc9d7` 是 HEAD 的祖先；未 push（与派发说明一致） |

**Head 口径**：实现与测试都在 `delivery_head=e593cc9d7`；`9618056f2` 只追加 docs/evidence（`git diff e593cc9d7..9618056f2 --name-only` 无代码/测试）。本报告对 `e593cc9d7` 的代码结论，在 docs commit 后保持不变。

## 2. AC 逐项判定

### AC-1 迁移形状与字节保留：**MET**

- `git diff d7823a0e0..e593cc9d7 --numstat -- src/infrastructure/sqlite/schema.py` = **22 / 0**；只有新增：
  - `schema.py:43` `SCHEMA_VERSION_V9 = 9`；
  - `schema.py:847` `MIGRATION_V9_NAME = "v9__media_artifacts_book_index"`；
  - `schema.py:859` `MIGRATION_V9_SQL = "CREATE INDEX idx_media_artifacts_book ON media_artifacts(book_id);"`（`IF NOT EXISTS` 不存在）；
  - `schema.py:872` 元组项 `Migration(SCHEMA_VERSION_V9, MIGRATION_V9_NAME, MIGRATION_V9_SQL),`。
- 我独立用 `git show <rev>:src/.../schema.py` 载入两个 head 的模块并比较：`(schema_version, migration_name, sql, checksum)` 在 v1–v8 **8/8 完全相同**；v9 SQL 的 checksum 为 `5b2a0e8c…`。
- 新测试 `tests/core/test_v9_migration.py:45-62` 的 `FROZEN_V1_V8` 是**硬编码** 8 组 `(版本, 名称, sha256(SQL))`；我把测试文件里的 8 组常量与生产模块的实算值逐项比对，**8/8 MATCH**。该断言读取的是生产 `default_migrations()`（不是 stub/复制 SQL），因此改动任一 v1–v8 SQL 会 RED；同时 `migrator.py:_verify_checksum` 的运行时校验仍在。
- 诚实边界：硬编码 checksum 无法阻止“同时改 SQL 与常量”的提交；那是流程/pin 层的防线，本卡未扩大该风险。`FROZEN_V1_V8` 的存在满足 AC-1 的机械判别要求。

### AC-2 旧库升级/守恒/幂等/失败回滚/旧端拒写：**MET**

- **逐起点升级**：`test_upgrade_from_legacy_version_creates_the_book_index[v1..v8]`（8 个参数化）用生产 `MigrationRunner` 从每个起点升到 v9；断言 `applied == start+1..9`、`schema_migrations=9`、`application_metadata=9`、`PRAGMA index_list(media_artifacts)` 含 `idx_media_artifacts_book` 且 `PRAGMA index_info` 首列=`book_id`、二次 `apply_pending()==[]`、重新 `open_database(..., latest_known_schema_version=LATEST)` 为 `READY/writable` 且不重建。
- **数据守恒**：`test_v8_upgrade_preserves_rows_and_query_results` 在 v8 库种 2 书/2 章/3 页/4 artifacts/3 revisions，升级前后 `_snapshot`（preview、revision ids、pinned、5 张表行数、artifacts 抽样行）**逐值相等**；`test_book_delete_inventory_is_unchanged_by_the_index` 的 `book_delete_inventory(..., storage=None)` 前后逐值相等。`tests/storage/test_upgrade_schema_data.py` 的 `test_synthetic_legacy_data_survives_full_upgrade[v1..v8]` 与 `test_upgrade_is_idempotent_for_synthetic_legacy_data[v1..v8]` 用合成 legacy 数据覆盖各起点（含 v8）的逐列守恒与 `_assert_latest`（`read_schema_version == LATEST_VERSION`）。
- **失败回滚**：`test_v9_failure_leaves_the_database_at_v8_without_the_index` 在 v9 SQL 后注入 `INSERT INTO no_such_table` → 抛 `sqlite3.Error`、版本仍 8、索引不存在、v8 仍可写。`migrator._apply_one` 的 `BEGIN IMMEDIATE … commit/rollback` 语义与测试相符（我另做了同名索引探针，见 §3）。
- **旧端拒写**：`test_old_v8_runner_refuses_the_v9_database` → `SchemaTooNewError`；`test_open_database_reports_too_new_to_a_v8_reader` → `SchemaState.TOO_NEW`、`writable=False`、写入抛 `OperationalError`（零写）。
- 测试真实性：全部使用真实 SQLite 文件、生产 `MigrationRunner`/`default_migrations()`/发布仓库方法；没有 mock、没有放宽为“不抛/任意版本”、没有 skip。`tests/fea11/test_source_gate_unify.py:213` 的 `[8] → [8, 9]` 是精确列表，保留了方向。

### AC-3 计划生效与结果等价：**MET**

我在独立临时库（生产迁移链，v9 后同库）用 `EXPLAIN QUERY PLAN` 复核：

| 查询 | 实测计划 |
|---|---|
| v8 `list_book_artifact_current_pointers`（trace 捕获的生产 SQL） | `SCAN ma \| SEARCH p … LEFT-JOIN \| SEARCH c … LEFT-JOIN \| USE TEMP B-TREE FOR ORDER BY` |
| v9 同一 SQL | **`SEARCH ma USING INDEX idx_media_artifacts_book (book_id=?)`** + 同上（SQL 文本前后相同） |
| v9 `list_book_artifact_revision_ids` | `SEARCH ma USING INDEX idx_media_artifacts_book (book_id=?) \| SEARCH ar USING INDEX idx_artifact_revisions_artifact (artifact_id=?)` |
| v9 `list_book_pinned_revision_ids` | 复合查询；artifact 分支 **`SEARCH ma USING INDEX idx_media_artifacts_book (book_id=?)`**，无 `SCAN` |
| v9 `SELECT COUNT(*) FROM media_artifacts WHERE book_id = ?` | **`SEARCH media_artifacts USING COVERING INDEX idx_media_artifacts_book (book_id=?)`** |
| v9 `DELETE FROM media_artifacts WHERE book_id = ?` | **`SEARCH media_artifacts USING COVERING INDEX idx_media_artifacts_book (book_id=?)`** + `SEARCH artifact_revisions USING COVERING INDEX idx_artifact_revisions_artifact (artifact_id=?)` |

- `tests/core/test_v9_migration.py:342-366` 用 `set_trace_callback` 捕获**发布方法实际执行的 SQL** 再 EXPLAIN，并断言 v9 前后 SQL 文本完全相同、`SCAN` 不再出现、结果逐值相等；`:369-402` 对 revision ids/pinned 同样用 trace；COUNT/DELETE 两条 SQL 字面量用 `inspect.getsource(SqliteLibraryRepository)` 与 `library.py:1550`/`:1940` 的生产原文逐字比对（我核对了源码：两处字面量唯一且一致）。
- 结果等价：preview、revision ids、pinned、`book_delete_inventory` 升级前后逐值相等（上述测试）。
- 备注（低风险，非 finding）：`list_book_artifact_revision_ids` 的 SQL 没有 `ORDER BY`，加索引后返回顺序在理论上可能变化；测试在种子数据上比较了列表本身且通过，且我在 `src/**` 未找到该方法的消费者（仅测试使用），因此不构成语义风险。preview 有 7 键全序 `ORDER BY`，不受影响。

### AC-4 断言同步（含 DSH 扩域）：**MET（1 处口径 P3）**

实际更新 **6 个位置**（全部等值更新、无删除/跳过/`>=` 化）：

| 文件:行 | 变更 | 方向 |
|---|---|---|
| `tests/fea09/test_v7_migration.py:76/139/248/263` | `== 8` → `== 9`（4 处） | 等值 |
| `tests/fea11/test_source_gate_unify.py:213` | `[8]` → `[8, 9]` | 精确列表 |
| `apps/.../Fea11SourceIpcTests.cs:60` | `Assert.Equal(8, …)` → `Assert.Equal(9, …)` | 等值 |
| `tests/fea11/support/ipc_seed.py` | **未改**；`:88-90` 是动态 `MAX(schema_version)`；我实跑 seed → receipt `schema_version=9` | 值来源正确 |
| `tests/storage/test_upgrade_schema_data.py`（DSH 扩域批准） | 新增 `_index_names()`（`:629-636`）；`assert new_tables` → `assert new_tables or new_indexes`（`:753-761`）；新增 `if version == 8: assert "idx_media_artifacts_book" in new_indexes`（`:762-767`）；保留 `assert all(name in after ...)` | 与 DSH 批准的“表或索引至少一项 + v8 起点显式断言”逐字一致；未跳断言 |

- v1–v7 起点的迁移行为未变（存储测试 v1..v7 仍全绿；`_assert_latest` 仍要求完整最新 schema）。
- 说明：扩域断言是 DSH 明确批准的形态；但严格看，`new_indexes` 在每个起点都至少含 v9 索引，因此 `or` 使“新增表”方向在 v1..v7 变为可被索引单独满足（见 R4-002，P3）。同测试的 `_assert_latest`（全表/关键列/索引/FK）与 `_assert_expected` 仍保留实质约束，故不影响 AC-4 MET。
- 口径不一致见 R4-006：卡面/Handoff 写“5 处”，实际列出并更新 6 个位置（EV 自己写“上表前 6 处”）。

### AC-5 门禁与零漂移：**MET**

- 我的实跑：定向 6 文件 **109 passed**；`verify_pins.ps1` **PASS (all 18)** EXIT 0；`check.ps1` 默认/`-TaskPath` **PASS (3 warnings) ×2** EXIT 0；`generate_api_inventory.py --check` **EXIT 0**；`git diff --check` 无输出（EXIT 0）。
- scope：`git diff d7823a0e0..9618056f2 --name-only` 共 29 个文件，全部 ⊆ `allowed_paths`（6 个实现/测试文件 + 卡/Handoff/EV/Manifest/19 个 logs）；`doc/plan`、`doc/contracts`、`pyproject.toml`/`requirements*.txt`/`uv.lock`、`apps/desktop-avalonia/Directory.Packages.props` **零 diff**；`apps/**` 仅 `Fea11SourceIpcTests.cs`。`doc/STATUS.md`/`doc/REBASELINE_PLAN.md`/`doc/TASK_LEDGER.md` 只出现在 Lead 的 `d7823a0e0`，不在本卡实现 diff 内。
- 全量数字采信交付日志并与 Manifest 交叉核对（我**未重跑**全量）：`full-before.txt` = **3372 passed / 10 skipped（273.61 s）**；`full-after.txt` = **3390 passed / 10 skipped（255.46 s）**；差值 +18 = 16 个新 v9 用例 + 2 个 `LEGACY_VERSIONS` 扩展参数；`dotnet-test-before/after` 8 个 assembly 汇总均为 **1683 passed / 0 failed / 96 skipped**；`dotnet-build-after` 0 warning/0 error。`verification/FEA-09` 零 diff、工作树 clean。

### AC-6 证据与不夸大：**MET**

- 我逐文件复算：`verification/FEA-12-CORE-C04B-INDEX-L4-1/**` 的 **20/20** artifact 的 bytes 与 sha256 同时等于 `RESOURCE-MANIFEST.json` 与卡面 Canonical Evidence 表（EV-01…EV-20）；无缺项、无多项。
- 未夸大：卡/Handoff/EV 中所有“回到旧谓词/性能已恢复”字样均出现在**否定/禁止**语境（“不承诺”“不得写”）；limitation 含 **1.53×** 与 **“回滚只走备份”**（卡交付记录 `:139-143`、EV `:176-187`、Handoff `:116-121`），并明确“未在真实用户库演练、外推成本、未做并发压测”。
- 唯一数值口径问题：卡面预登记 limitation 的“旧谓词 5.81”与 2.85/1.53× 矛盾（R4-001，P3）；交付记录/EV/Handoff 用的 2.85 与 1.53× 是正确值。

## 3. 独立实跑记录（确切数字）

| # | 命令/操作 | 结果 |
|---|---|---|
| 1 | `C:/Python314/python.exe -m pytest tests/core/test_v9_migration.py tests/fea09/test_v7_migration.py tests/fea11/test_source_gate_unify.py tests/storage/test_upgrade_schema_data.py tests/core/test_core_delete_preview_commands.py tests/core/test_core_delete_commands.py -q -p no:warnings` | **109 passed in 8.40s**（期望 ~109） |
| 2 | 临时把 `MIGRATION_V9_SQL` 改为 `SELECT 1;`（我的最小二进制替换；tampered sha256=`996e6e77…`）后重跑 `tests/core/test_v9_migration.py tests/storage/test_upgrade_schema_data.py` | **13 failed / 20 passed in 6.39s**；失败集与交付日志一致（shape、8 个起点、conservation、preview 计划、delete 面、storage `[v8]`） |
| 3 | 从 `schema.py.bak` 逐字节恢复 → `sha256=5fe87b693554d5e7b1f230f73cab75e04528466105b1d9f3a8f972dd68f92ce6`、git blob=`2fcd79d2…`，**MATCH**；`touch` 后重跑同两文件 | **33 passed in 3.21s**；`git status` clean |
| 4 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)**，EXIT 0 |
| 5 | `pwsh -NoProfile -File tools/governance/check.ps1`；`… -TaskPath doc/tasks/FEA-12-CORE-C04B-INDEX-L4-1.md` | **PASS (3 warnings) ×2**，EXIT 0（warnings：10 个非终态 Task；STATUS 3141 B/27 行；REBASELINE_PLAN 6970 B/64 行） |
| 6 | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | **EXIT 0** |
| 7 | `git diff --check`；`git status --porcelain` | 空；clean |
| 8 | 自写脚本载入 `d7823a0e0`/`e593cc9d7` 的 `schema.py`，比较 v1–v8 与 `FROZEN_V1_V8` | **8/8 identical**；常量 **8/8 MATCH**；`schema.py` diff **+22/−0** |
| 9 | 独立临时库 + 生产方法 trace + EXPLAIN（v8→v9 同库） | 见 AC-3 表；`PRAGMA index_info` = `['book_id']`；版本 9 |
| 10 | 同名索引风险探针（v8 库手工建 `idx_media_artifacts_book` 后 apply v9） | `OperationalError: index idx_media_artifacts_book already exists`；版本停 **8**、库仍可写；`DROP INDEX` 后重试 → applied `[9]`、version 9（fail-closed 与 limitation 一致） |
| 11 | `python tests/fea11/support/ipc_seed.py --data-root <workspace fixture> --db …/library.db` | `FEA11_IPC_SEED_OK {"schema_version": 9}`；receipt `schema_version: 9`（证明 C# 新断言值正确） |
| 12 | 复算 20 个 artifact 的 bytes/sha256 并与 Manifest + 卡面表比对 | **20/20 MATCH**（含 EV.md `a27fc912…`、Manifest 自身不在 artifact 列表） |

**未跑（如实声明）**：全量 `pytest tests`（按派发说明不重跑，仅核对交付日志与 Manifest）；全量 .NET `dotnet build/test`（未重跑；我仅从日志汇总 1683/0/96 与 build 0/0）；`NEWMANGA_FEA11_IPC=1` 的 opt-in C# 套件（未跑，仅跑 seed 验证 receipt）；真实用户库升级演练；性能基准/并发写压测；`ANALYZE`/大库首启计时。

## 4. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| R4-001 | P3 | `doc/tasks/FEA-12-CORE-C04B-INDEX-L4-1.md:85` | 预登记 limitation 写“旧谓词 **5.81**”，与卡 `:60` 的“1.53×旧谓词”、交付记录 `:139-140`（2.85）、EV `:178-179` 矛盾；4.36 ÷ 2.85 ≈ 1.53，5.81 无来源。纯文档数值错误，不影响实现/AC | 卡面三处数值对照；scope review §3.3 = 2.852 ms/书（旧谓词） | Lead 在 closeout 把 `:85` 的 5.81 更正为 2.85（或改引“1.53×”） | open |
| R4-002 | P3 | `tests/storage/test_upgrade_schema_data.py:753-767` | DSH 扩域批准的 `assert new_tables or new_indexes` 已按批准形态落地；但 v9 索引在每个起点都会新增，故 `new_indexes` 恒非空，v1..v7 的“必须新增 latest 表”方向被 `or` 兜底。严格看是测试强度弱化（非实现缺陷；同测试 `_assert_latest` 仍校验完整最新 schema，实际风险低） | 文件 `:759-761`；v9 只有索引迁移；`MIGRATIONS[:-1]` 含 v8 | 保持现状（符合 DSH 批准）；若未来收紧，可写 `(version < 8 and new_tables) or (version == 8 and "idx_media_artifacts_book" in new_indexes)` | open（非阻塞） |
| R4-003 | P3 | `tests/fea11/support/ipc_seed.py:1-6` | docstring 仍写“one isolated **v8** library”“migration chain (**v1..v8**)”，而脚本现在用 `default_migrations()` 升到 v9（我实跑 receipt=9）。纯注释过期，无功能影响 | 实跑 `FEA11_IPC_SEED_OK {"schema_version": 9}` | 下次触碰该文件时把 docstring 的 v8/v1..v8 改为“latest (v9)”/“v1..latest” | open |
| R4-004 | P3 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11SourceIpcTests.cs:60`（方法 `:24`，`[Fea11IpcFact]` `:23`） | 唯一改动的 .NET 断言位于 opt-in 测试（`NEWMANGA_FEA11_IPC=1`）；默认 `dotnet test` 前后日志均 **SKIP**，因此默认 .NET 门禁无法判别旧的 8。断言值本身正确（seed receipt=9） | `dotnet-test-before/after.txt` 均为 3 个 `Fea11SourceIpcTests` SKIP；我实跑 seed 得 9 | closeout 记录“该断言由 opt-in 套件覆盖”；如需常规门禁覆盖，可另立小卡（超出本卡范围） | open（非阻塞） |
| R4-005 | P3 | `verification/FEA-12-CORE-C04B-INDEX-L4-1/RESOURCE-MANIFEST.json:26` | `written_in_workspace` 声称临时 SQLite 库 `tmp/`“保留引用”，实测 `G:\CODEX\New Manga.workspace\index-l4\` 无 `tmp/`；`evidence_runner.py` 用 `tempfile.mkdtemp(dir=WORK)` 生成并在结尾 `shutil.rmtree`。日志/脚本仍在，可复算性不受影响 | 目录列举与 `evidence_runner.py:257-263` | 若刷新 Manifest，把 “临时 SQLite 库 tmp/” 改为 “由 evidence_runner.py 复建（跑完清理）” | open |
| R4-006 | P3 | 卡 `:72-77`、`:99`；Handoff `:34`；EV `:39-49`、`:51` | “**5 处**硬编码断言”与随后列出的 **6 个位置**（test_v7 的 4 处 + test_source_gate_unify 的 1 处 + C# 的 1 处）不一致；EV `:51` 自己写“上表前 6 处”。实现按列出的 6 处更新，方向正确 | 卡 AC-4 文字；`git diff` 6 处变更 | closeout 时把“5 处”统一改为“6 处（4+1+1）”或明确口径 | open |

**未发现 P0/P1/P2。** 在记录范围内没有发现实现错误、契约破坏、越界、证据造假或测试被 stub/放宽到不能判别的程度。

## 5. 残余风险与未覆盖

1. **同名索引**：裸 `CREATE INDEX` 在“已有同名索引”的库上 fail-loud（版本停 v8、库可写、需人工 `DROP INDEX` 后重试）。我实测了该路径；与 limitation 一致，属于可接受的 fail-closed 行为，但要求运维动作。
2. **顺序**：`list_book_artifact_revision_ids` 无 `ORDER BY`；加索引后返回顺序理论上可变。preview 有 7 键全序；pinned 在 Python 侧排序；该方法在 `src/**` 无消费者，风险低。
3. **大库首启成本**：`CREATE INDEX` 为一次性；卡面登记为外推（60k ≈ 30 ms；600k ≈ 0.3 s；6M ≈ 3 s），未实测；未做真实用户库演练与并发写压测。
4. **门禁范围**：全量 pytest/.NET、opt-in IPC 套件均未由我重跑；仅核对了交付日志、Manifest 与文件指纹。Lead 的集成复跑仍是最终依据。
5. **`tests/fea11/test_source_sync.py:993`** 仍传 `latest_known_schema_version=8`，位于空库分支（`connection.py:356-357` 返回 `EMPTY`，随后按 `default_migrations()` 升到 v9），不失败且不在 `allowed_paths`；仅语义陈旧，不影响本卡。
6. **回滚**：无自动降级；回滚只走升级前备份（C-01b SC-37），与卡面 limitation 一致。

## 6. 结论与建议下一步

- **结论：`approved`**。AC-1…AC-6 均可独立复核为 MET；0 pin 判定成立（pins 18/18、契约零 diff）；实现形状严格符合 scope review §2.4 与 DSH 裁决；判别性实验在我这里可复现（13/20 RED → 字节复原 MATCH → 33 GREEN）。
- **建议**：Lead 可进入 closeout：更新冻结记录 §4A **L-4** 为“已修（本卡）”、STATUS/PLAN/LEDGER、push。closeout 时顺手处理 R4-001/R4-006（文档数值/计数）、R4-003（docstring）、R4-005（Manifest 措辞）；R4-002/R4-004 为可选跟进，不阻塞。
- 本报告只对 `reviewed_head=e593cc9d7`（docs/evidence `9618056f2`）有效；若 head 再变，须重新设 appointment 与复审。

## 7. 真实性声明

1. **独立性**：fresh subagent（session `231cd1fe-cffa-431d-bb67-3b22feede577`），未参与本卡实现/返修，未参与 RESIDUAL-1/2/3、C-04b/CORE 或 L-4 scope review；与实现者 `index-impl`、scope review 作者均非同一上下文。
2. **写入范围**：唯一仓库写入是 `doc/reviews/FEA-12-CORE-C04B-INDEX-L4-1-r1.md`。临时备份/脚本在 `G:\CODEX\New Manga.workspace\C04B-RESIDUAL\review-index\`（`verify_frozen_v1_v8.py`、`verify_evidence.py`、`probe_same_index.py`、`probe_plans.py`、`schema.py.bak`）；`ipc_seed.py` 需要的临时 fixture 在 `G:\CODEX\New Manga.workspace\FEA-11\fixtures\review-l4-seed`（已删除）；探针临时库在系统 `%TEMP%`（已清理）。未打开真实用户库/AppData/外部卷。
3. **无副作用**：未 `git add/commit/push`；判别性实验后 `schema.py` 已逐字节复原（sha256 MATCH）、`touch`、`git status` clean；结束工作树 clean。
4. **不夸大**：我未重跑全量 pytest/.NET，未做真实库演练或基准计时；报告中所有“实跑”数字均为本机本次实际输出，其余数字明确标注为“交付日志/Manifest 采信”。
