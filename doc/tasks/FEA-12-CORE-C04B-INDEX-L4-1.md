---
id: FEA-12-CORE-C04B-INDEX-L4-1
title: media_artifacts.book_id 索引（v9 迁移；消 preview/删除面 SCAN 放大，0 pin）
kind: implementation
governance_version: 3
status: done
approval: 用户 AUTORUN 指令（2026-11-08：全部授权/自主裁决/不询问用户）；独立 scope review `doc/reviews/FEA-12-CORE-C04B-INDEX-L4-scope-r1.md`（fresh subagent session `6f66c01a-…`；verdict **recommended**；**pin=0**：C-15 冻结字节是 v7 规范 DDL 块，`media_artifacts` 不在其中，`:50` 的 v8+ 追加仅限两张同步表，`:343`/FROZEN-C15 `:56` 明示不冻结 FEA-11/12/13 结构，18 pin 不含 `schema.py`）；**DSH 裁决（2026-11-08，裁决人=DSH）**：按 AUTORUN §2 判据 (c)「需改核心存储才有运行时收益」立项；0 pin、无 PREREQ；形状=SCHEMA_VERSION_V9 + 单条 `CREATE INDEX idx_media_artifacts_book ON media_artifacts(book_id);`（裸 CREATE INDEX，fail-loud）
suggested_owner: dsh
owner: index-impl
reviewer: null
depends_on:
  - FEA-12-CORE-C04B-RESIDUAL-3
  - FEA-12-CORE
base_commit: 02c1a26d1
branch: null
worktree: null
integration_commit: e593cc9d7
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-12-CORE-C04B-INDEX-L4-1
allowed_paths:
  - doc/tasks/FEA-12-CORE-C04B-INDEX-L4-1.md
  - doc/reviews/FEA-12-CORE-C04B-INDEX-L4-1-*.md
  - doc/handoffs/FEA-12-CORE-C04B-INDEX-L4-1-*.md
  - verification/FEA-12-CORE-C04B-INDEX-L4-1/**
  - src/infrastructure/sqlite/schema.py
  - tests/fea09/test_v7_migration.py
  - tests/fea11/test_source_gate_unify.py
  - tests/fea11/support/ipc_seed.py
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11RunGrantIpcTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11SourceIpcTests.cs
  - tests/core/test_v9_migration.py
  - tests/storage/test_upgrade_schema_data.py
out_of_scope:
  - 契约字节（18 pins 零改动；本卡 0 pin，无需 UNFREEZE）
  - 其它表/索引/DDL（只加 `media_artifacts(book_id)` 一个索引；v1–v8 迁移逐字节不变）
  - 数据回填/数据修复；损坏行语义（L-5 保留未修）
  - wire/命令/能力/错误码/`PROTOCOL_MINOR`；App/UI；Host 逻辑
  - RH-3 根治（C-17 additive）；B2（无消费者）
  - 真实用户数据/AppData/外部卷（红线）
  - STATUS/PLAN/LEDGER（Lead 维护）；push（Lead 统一）
---

# FEA-12-CORE-C04B-INDEX-L4-1：`media_artifacts.book_id` 索引（v9 迁移，0 pin）

> **状态：`ready`（DSH 已裁决；Owner `index-impl`；base `02c1a26d1`；0 pin、无 PREREQ）。**
> 依据：`doc/reviews/FEA-12-CORE-C04B-INDEX-L4-scope-r1.md`（recommended；§2 契约/pin 判定、§3 收益基准、§4 卡面草案、§5 成本提醒）+ 冻结记录 §4A **L-4** + RESIDUAL-3 Review **R3-002**。

## 目标

给 `media_artifacts(book_id)` 加索引（v9 迁移），消除 RESIDUAL-3 把谓词改为 `ma.book_id = ?` 后引入的
**`SCAN ma` 放大**：

- **preview**：单本成本原本 ∝ 全库 artifacts 总量（6k 库 0.50 → 60k 库 **5.94 ms/书**，11.8×）；加索引后
  60k 宽库 → **0.376 ms/书**（scope review 实测）。
- **删除面顺带修复（更强的立项理由）**：`book_delete_inventory` 计数（`:1549-1551`）、`list_book_artifact_revision_ids`
  （`:1232-1239`）、pinned 查询（`:1252-1254`）、事务内 `DELETE ... WHERE book_id`（`:1940`）均由 `SCAN` → `SEARCH`
  （DELETE/COUNT 走覆盖索引）。
- **不承诺**回到旧谓词水平：scope review 实测 60k 厚数据集 8.90 → 4.36 ms/书（仍 1.53×旧谓词，差值来自 artifacts
  驱动 + 7 键排序），**如实登记 limitation**。

## Acceptance Criteria

- [x] **AC-1 迁移形状与字节保留**：`schema.py` 新增 `SCHEMA_VERSION_V9 = 9` 与 `MIGRATION_V9_NAME`（建议 <<MET>>
  `v9__media_artifacts_book_index`），在 `default_migrations()` 追加**单条** `CREATE INDEX idx_media_artifacts_book
  ON media_artifacts(book_id);`（**裸 CREATE INDEX**，不用 `IF NOT EXISTS`，fail-loud）；**v1–v8 迁移逐字节不变**。 <<MET>>
- [x] **AC-2 旧库升级与守恒**：真实 production migrations 库从 v8 升级到 v9：数据行数/内容守恒、索引存在、`schema_version=9`； <<MET>>
  重跑迁移幂等（第二次不重复建索引/不报错）；升级脚本对**只读/迁移失败**路径 fail-closed（沿既有 SC-19 口径）。 <<MET>>
- [x] **AC-3 计划生效与结果等价**：`EXPLAIN QUERY PLAN` 对 `list_book_artifact_current_pointers` 的新谓词恢复 <<MET>>
  `SEARCH ma USING INDEX`（不再是 `SCAN ma`）；preview 结果与升级前**逐值等价**（正常数据）；删除面计数/枚举结果等价。 <<MET>>
- [x] **AC-4 硬编码 v8 断言同步**：更新 6 处硬编码 schema 版本断言（`test_v7_migration.py` ×4 + `test_source_gate_unify.py` ×1 + `Fea11SourceIpcTests.cs` ×1）（`tests/fea09/test_v7_migration.py:76/139/248/263`、 <<MET>>
  `tests/fea11/test_source_gate_unify.py:213`、`Fea11SourceIpcTests.cs:60`；值来源 `tests/fea11/support/ipc_seed.py:88-90`），
  使既有套件在 v9 下全绿；不得放宽断言方向。**DSH 扩域批准（2026-11-08，裁决人=DSH）**：实现中发现册外的派生断言
  `tests/storage/test_upgrade_schema_data.py`（`LEGACY_VERSIONS = [m.schema_version for m in MIGRATIONS[:-1]]` + `assert new_tables`；
  v9 后 v8 起点必然 `new_tables=[]`）——结构性失效，**授权扩 allowed_paths 加该文件**，做**不放宽方向**的最小修复
  （改为「新增表**或**新增索引至少一项」，并在 v8 起点断言 `idx_media_artifacts_book` 新出现）；不得跳断言/改方向。 <<MET>>
- [x] **AC-5 门禁**：定向（迁移/删除/preview/gated IPC 相关）+ 全量 pytest **≥3372/10**、全量 .NET **≥1683/0/96** <<MET>>
  （跑后 `git checkout -- verification/FEA-09`）、`verify_pins.ps1` **18/18**（契约零改动）、`check.ps1`（默认 + `-TaskPath`）、
  API inventory、scope ⊆ allowed_paths、`git diff --check`。 <<MET>>
- [x] **AC-6 证据与不夸大**：EV（before/after `EXPLAIN` + 基准数字 + 迁移测试）、Manifest、Closeout 完整； <<MET>>
  **不得**写「preview 回到旧谓词水平 / 性能已全面恢复」；limitation 必须含「未回到旧谓词（1.53×）」与「回滚只走备份」。 <<MET>>

## limitation（预登记）
- **未回到旧谓词水平**：60k 厚数据集 8.90 → 4.36 ms/书（旧谓词实测 2.85），差值为 artifacts 驱动 + 7 键排序固有成本。
- **大库首启成本为外推**：scope review 以 tmp 库模拟（6k/60k artifacts），未在真实用户库演练。
- **不改损坏行语义**：`book_id` 与 page 归属不一致的损坏行，preview 归属仍按 `book_id`（C-04b v1.2），本卡不动。
- **回滚只走备份**：v9 迁移不回滚（沿既有迁移纪律）；失败即 fail-closed。
- **L-5 未修**：`preview_lifecycle` 清理枚举按 page 归属的漏清问题保留。

## 依赖与下一步

- 依赖：`FEA-12-CORE-C04B-RESIDUAL-3`（done `25dc1523c`，引入 `ma.book_id` 谓词）、`FEA-12-CORE`（done）。
- 完成后：`L-4` 状态由「未修」更新为「已修（本卡）」，并在冻结记录 §4A 与 R3-002 处置中回填（**由 Lead 在 closeout 维护**）。

## 交付记录（index-impl，2026-11-08）

- **delivery_head**：`e593cc9d7`（`e593cc9d70be3b2568569aea43f313b0bc28c413`；实现+测试 commit）
- **commit 链**：`e593cc9d7`（`feat(fea-12-core-c04b-index-l4)`：`schema.py` v9 + 6 处断言等值同步 +
  `tests/core/test_v9_migration.py`（16 用例）+ `tests/storage/test_upgrade_schema_data.py` 派生断言修复）
  → 紧随其后的 docs/evidence commit（本卡交付记录 + `doc/handoffs/FEA-12-CORE-C04B-INDEX-L4-1-e593cc9d7.md` +
  `verification/FEA-12-CORE-C04B-INDEX-L4-1/**`）
- **实施起点**：`d7823a0e0`（Lead 的任务释放 commit；卡面 `base_commit=02c1a26d1`）；本卡对该 commit 零回改
- **AC 判定**：AC-1…AC-6 全部 MET（逐条见上；`<<MET>>` 已就位于各 AC 行末）

### 门禁（before → after，实跑）

- 定向 `pytest tests/core/test_v9_migration.py tests/fea09/test_v7_migration.py
  tests/fea11/test_source_gate_unify.py tests/core/test_core_delete_preview_commands.py
  tests/core/test_core_delete_commands.py -q -p no:warnings`：**76 passed（4 个既有文件）→ 92 passed**（+16 新用例）；
  扩域版 6 文件 **109 passed**
- 全量 `pytest tests -q -p no:warnings --tb=no`：**3372 passed / 10 skipped（273.61 s）→
  3390 passed / 10 skipped / 0 failed（255.46 s）**
- 全量 .NET `dotnet build` + `dotnet test ... --no-build`：**1683 / 0 / 96 → 1683 / 0 / 96**（build 0 warning / 0 error）；
  跑后 `git checkout -- verification/FEA-09`（零 diff）
- `verify_pins.ps1`：**PIN AUDIT: PASS (all 18)**，EXIT 0（契约零改动）
- `check.ps1`（默认 / `-TaskPath doc/tasks/FEA-12-CORE-C04B-INDEX-L4-1.md`）：**PASS (3 warnings) ×2**
- `generate_api_inventory.py --check`：**EXIT 0**
- scope：实现 diff（vs `d7823a0e0`）⊆ allowed_paths；`doc/plan`/`doc/contracts`/依赖 **零 diff**；
  `apps/**` 仅 `Fea11SourceIpcTests.cs` 一处断言；`git diff --check` 空（EXIT 0）

### 计划与迁移（AC-1/AC-2/AC-3 关键实测）

- `EXPLAIN QUERY PLAN`（生产 SQL，trace 捕获）：preview v8 **`SCAN ma`** → v9
  **`SEARCH ma USING INDEX idx_media_artifacts_book (book_id=?)`**；`list_book_artifact_revision_ids`/
  `list_book_pinned_revision_ids` 同理；inventory COUNT 与事务 DELETE **走覆盖索引**
- 迁移：v1…v8 每起点 → v9，`schema_migrations`/`application_metadata` 双源=9，索引存在，
  数据与查询结果**逐值守恒**，二次 `apply_pending()==[]`；注入失败 → 停 v8 + 无索引残留 + 库可读写；
  旧 v8 runner → `SchemaTooNewError`，`open_database(latest=8)` → `TOO_NEW` 零写

### 判别性

把 `MIGRATION_V9_SQL` 临时改为 `SELECT 1;`（去掉 `CREATE INDEX`）→ `tests/core/test_v9_migration.py` +
`tests/storage/test_upgrade_schema_data.py` = **13 failed / 20 passed**（preview 计划实测 `SCAN ma`）；
逐字节复原 → sha256 **MATCH**（`5fe87b69…`）→ **33 passed**。

### limitation（不夸大）

- **不承诺**「preview 回到旧谓词水平 / 性能已全面恢复」：索引只消除全库扫描放大；60k 厚数据集
  8.90 → 4.36 ms/书（仍 1.53× 旧谓词 2.85），差值来自 artifacts 驱动 + 7 键临时排序
- 大库首启成本为外推（60k≈30 ms；600k≈0.3 s；6M≈3 s，未实测）；**未在真实用户库演练**；写放大未做并发压测
- 裸 `CREATE INDEX` 遇同名索引会 fail-loud（需人工 `DROP INDEX`）；**回滚只走升级前备份**
- 不改损坏行语义与 **L-5**；未 push、未 closeout（`status` 与冻结记录 L-4 由 Lead 维护）
- **证据**：`verification/FEA-12-CORE-C04B-INDEX-L4-1/{EV.md, RESOURCE-MANIFEST.json, logs/**}`

## Canonical Evidence

| evidence_id | AC | 路径 | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC-1..AC-6 | verification/FEA-12-CORE-C04B-INDEX-L4-1/EV.md | 9618056f2 | a27fc91220c7883c1536d2e40e8fdf13b6a3e170126992ebe089e54772e4dc2a | CANONICAL |
| EV-02 | AC-5 | verification/FEA-12-CORE-C04B-INDEX-L4-1/logs/api-inventory.txt | 9618056f2 | 6d1e41178756c82c9500e141743fe5783c00f75d4ca09b4c6206323efb02e4b7 | CANONICAL |
| EV-03 | AC-5 | verification/FEA-12-CORE-C04B-INDEX-L4-1/logs/check-default.txt | 9618056f2 | 9d503f6a87d17b35b2b2ad7eb9078798c4cb3d7aefad5ff644189ec425362ec7 | CANONICAL |
| EV-04 | AC-5 | verification/FEA-12-CORE-C04B-INDEX-L4-1/logs/check-taskpath.txt | 9618056f2 | 9d503f6a87d17b35b2b2ad7eb9078798c4cb3d7aefad5ff644189ec425362ec7 | CANONICAL |
| EV-05 | AC-1/AC-2/AC-3 | verification/FEA-12-CORE-C04B-INDEX-L4-1/logs/discriminative-and-explain.txt | 9618056f2 | 69e2a639db58376d63bc6483a5b2db7f95c3ee6078cdd50eaadd6f1b6b64b2d7 | CANONICAL |
| EV-06 | AC-5 | verification/FEA-12-CORE-C04B-INDEX-L4-1/logs/dotnet-build-after.txt | 9618056f2 | 0b40e96882d1243653a2b4d40c13f56fdd5f9ae64d185fd0f550330e466e0096 | CANONICAL |
| EV-07 | AC-5 | verification/FEA-12-CORE-C04B-INDEX-L4-1/logs/dotnet-build-before.txt | 9618056f2 | 56293050197398cff5d39f1b5cfe922e01842afaefb9146b6dac7a998b4013a5 | CANONICAL |
| EV-08 | AC-5 | verification/FEA-12-CORE-C04B-INDEX-L4-1/logs/dotnet-test-after.txt | 9618056f2 | 27ea2018a05623a220e2fe44f92fe12eccfb9568fd8d87665eed3b4df80a3eae | CANONICAL |
| EV-09 | AC-5 | verification/FEA-12-CORE-C04B-INDEX-L4-1/logs/dotnet-test-before.txt | 9618056f2 | d25368a45425c5f2ec550d971a20be30095b08acd574c32f9da765b76961cd6c | CANONICAL |
| EV-10 | AC-4 | verification/FEA-12-CORE-C04B-INDEX-L4-1/logs/eol-and-restore-note.txt | 9618056f2 | c0b3f884f63aa4676d94fb132b09cff3f47cdc96911aec2279367119bc64925b | CANONICAL |
| EV-11 | AC-5 | verification/FEA-12-CORE-C04B-INDEX-L4-1/logs/full-after.txt | 9618056f2 | e93d8cda6ec1687e0f2c51d8ca9540dc46e2100e2bf82c6963f7ae08dc8304e2 | CANONICAL |
| EV-12 | AC-5 | verification/FEA-12-CORE-C04B-INDEX-L4-1/logs/full-before.txt | 9618056f2 | 0b188fff491f1acf97813a668573d8ce6882b623a2b741cd8606ef507e5865a5 | CANONICAL |
| EV-13 | AC-5 | verification/FEA-12-CORE-C04B-INDEX-L4-1/logs/pins.txt | 9618056f2 | aedf5a6b579c255e4b1544ccc1479aaf8517d6cdd711f9e7a12018f08e6f118d | CANONICAL |
| EV-14 | AC-5 | verification/FEA-12-CORE-C04B-INDEX-L4-1/logs/scope-post-code-commit.txt | 9618056f2 | bbbf45f49e38aa52f3726c75078678a0a4dbb5d9e11a7670ae3dc0e71c566a18 | CANONICAL |
| EV-15 | AC-5 | verification/FEA-12-CORE-C04B-INDEX-L4-1/logs/scope.txt | 9618056f2 | 6660d7f003e98aadae95743b43ebd6575502f75e595ed4a85f97329743fca761 | CANONICAL |
| EV-16 | AC-4 | verification/FEA-12-CORE-C04B-INDEX-L4-1/logs/sha256-after-edits.txt | 9618056f2 | 8457385f2ff6384f2f9baf5470d055c5aaf67ee7521d0397291f4d270e4b65f9 | CANONICAL |
| EV-17 | AC-4 | verification/FEA-12-CORE-C04B-INDEX-L4-1/logs/sha256-files.txt | 9618056f2 | db69c0a57b6f5cf3f0cf9235c1fc76cacb504f8275ce94fe4e26d9456fa33b99 | CANONICAL |
| EV-18 | AC-5 | verification/FEA-12-CORE-C04B-INDEX-L4-1/logs/targeted-after-extended.txt | 9618056f2 | be484d7f1bda2fecb0147ca0dda6040ed699f0e6147a7e324c9420ed8523414f | CANONICAL |
| EV-19 | AC-5 | verification/FEA-12-CORE-C04B-INDEX-L4-1/logs/targeted-after.txt | 9618056f2 | 3367247f667ac9a08cbb29c6beff7af930158e010ed75288ccd89b41ee56876a | CANONICAL |
| EV-20 | AC-5 | verification/FEA-12-CORE-C04B-INDEX-L4-1/logs/targeted-before.txt | 9618056f2 | 49b7b897d07a2f2d78bee7afb5135a7199092b2b709c30da4b0fef19b5d72fd2 | CANONICAL |
| EV-21 | AC-6 | verification/FEA-12-CORE-C04B-INDEX-L4-1/RESOURCE-MANIFEST.json | 9618056f2 | 1e4647e97fd3510afde7630204d451b056a7e519c9d0b704f69368b4e8fe6490 | CANONICAL |

## Resource Manifest

| resource_type | 资源 | disposition | 目标 | 完整性 | 引用/进程检查结果 |
|---|---|---|---|---|---|
| 无删除/移动/归档（仓内） | - | NOT_APPLICABLE | - | - | 本卡仓内 0 删除/0 移动/0 归档；仅改 `schema.py` + 5 个测试文件 + 卡/Handoff/证据；仓外 `workspace\index-l4` 脚本/临时库/日志副本保留（无独有数据）；无残留进程 |

## Closeout Record（2026-11-08；Lead）

- **状态**：`done`；`integration_commit`/`delivery_head` = **`e593cc9d7`**（实现+测试）；docs/evidence = `9618056f2`。
- **AC 判定**：AC-1…AC-6 **全 MET**。
- **Review 链**：独立 fresh subagent **r1 `approved`（P0=0/P1=0/P2=0/P3=6；session `231cd1fe-…`）**；reviewer 独立复跑判别性（`MIGRATION_V9_SQL` 改 `SELECT 1;` → 13 failed → 复原 `5fe87b69…` MATCH + touch → 33 passed）、pins 18/18、check×2、API、证据 20/20 MATCH、**v1–v8 8/8 逐字节不变**、风险探针（同名索引已存在 → fail-closed 停 v8，DROP 后重试到 9）。
- **Lead 集成门禁**：build **0 warning/0 error**；定向 **109 passed**；全量 pytest **3390 passed / 10 skipped EXIT=0**（起点 3372/10 → +18）；全量 .NET **1683 passed / 0 failed / 96 skipped EXIT=0**（不降）；pins **18/18**（契约零改动，0 pin）；check（默认 + `-TaskPath`）**PASS(3 warnings)**；API **EXIT=0**；scope 29 文件全 ⊆ allowed_paths；跑后 `git checkout -- verification/FEA-09` 已恢复。
- **实现要点**：`schema.py` **+22/−0**——`SCHEMA_VERSION_V9=9`、`MIGRATION_V9_NAME="v9__media_artifacts_book_index"`、单条**裸** `CREATE INDEX idx_media_artifacts_book ON media_artifacts(book_id);`、+1 元组项，**v1–v8 迁移字节零改**；`EXPLAIN` 由 `SCAN ma` → **`SEARCH ma USING INDEX idx_media_artifacts_book`**；COUNT/DELETE 走覆盖索引。
- **P2/P3 处置**：**R4-001**（limitation「旧谓词 5.81」与 1.53× 矛盾）→ 已更正为「实测 2.85」；**R4-006**（「5 处」实为 **6 处**：`test_v7_migration.py` ×4 + `test_source_gate_unify.py` ×1 + `Fea11SourceIpcTests.cs` ×1）→ 已更正；**R4-003**（`ipc_seed.py` docstring 仍写 v8/v1..v8）→ **不改**（注释过时、无功能影响；改它连锁变更 sha/manifest，成本高于收益），登记 P3；**R4-005**（manifest `written_in_workspace` 的 `tmp/` 措辞与实际 `workspace\index-l4\` 不符）→ 本条补正说明（manifest 为证据文件不改字节）；**R4-002**（storage `assert new_tables or new_indexes` 严格符合 DSH 扩域批准，但 v1–v7 的「新增表」方向被 `or` 兜底）→ 登记 P3；**R4-004**（唯一 .NET 断言位于 opt-in skipped 测试，默认门禁不判别）→ 登记 P3。
- **limitation 保留**：**未回到旧谓词水平**（60k 厚数据集 8.90 → 4.36 ms/书；旧谓词实测 **2.85**，仍 1.53×；差值来自 artifacts 驱动 + 7 键排序固有成本）；**大库基准为 tmp 库外推**；**不改损坏行语义**（L-5 保留）；**回滚只走备份**。**不得**写「preview 回到旧谓词水平 / 性能全面恢复」。
- **Resource Manifest**：仓内 0 删除/0 移动/0 归档；仓外临时库/日志保留。
- **指针清理**：Lead 更新 STATUS/PLAN/TASK_LEDGER；冻结记录 §4A **L-4 → 已修（本卡）**。
- **push**：随本轮 Lead 统一 push（记录见 handoff §26）。
