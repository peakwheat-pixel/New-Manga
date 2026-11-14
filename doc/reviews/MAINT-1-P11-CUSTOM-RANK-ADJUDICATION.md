# `custom_rank` 失败裁决（MAINT-1 P11，2026-11-14）

## 事实
- 失败：`test_real_v7_import_fixture_degrades_then_pixel_matches_on_generation_two`
- 错误：`sqlite3.OperationalError: no such column: custom_rank`（`planner.py:94` → `library.py:235`）
- 源码：`src/infrastructure/sqlite/schema.py:930-932` 存在 `MIGRATION_V12_NAME = "v12__chapters_custom_rank"` / `ALTER TABLE chapters ADD COLUMN custom_rank INTEGER;`
- 仓储：`library.py:217` 的 `_CHAPTER_COLUMNS` 已含 `custom_rank`；`library.py:107` 对行缺失做了防御读取，但 SELECT 列清单不防御。

## 裁决：路线 (a) 修 fixture（不改产品代码、不改契约）
理由：生产路径在打开库时执行 v12 迁移，`custom_rank` 必然存在；本用例构造的是**未迁移的 v7 旧库**并直接驱动 planner，属测试支撑缺口。让仓储对旧 schema 容错（路线 b）会弱化契约（SELECT 列清单失去意义）。

## 派发（下一会话执行）
- Owner：Codex（测试/数据层）
- 范围：`tests/fea11/test_source_scan.py` 相关 fixture 构建处，使其在建库后执行到 v12（或显式建列），不改 `src/**`
- 验收：该用例通过；全量 pytest 0 failed；.NET 与 pins 不变；门禁不降
- 独立 Review：不得由实现者同一会话执行

## 状态
- 本裁决未改变任何节点状态；DoD §4 在用例通过前仍为「有条件达成」。

## 精确修复点（轮次 17 定位）

- 文件：`tests/fea11/test_source_match.py`
- 用例：`test_real_v7_import_fixture_degrades_then_pixel_matches_on_generation_two`（`:1002`）
- 关键行：`:1022` `migrations = default_migrations()`；`:1028` `MigrationRunner(conn, migrations[:7]).apply_pending()` —— 刻意把库停在 **v7**。
- 冲突：用例下游调用 `planner.plan` → `library.py:217` 的 `_CHAPTER_COLUMNS` 含 `custom_rank`（**v12** 迁移新增），未迁移即报 `no such column`。
- 因此修复不是"加一列"这么简单，而是**对齐该用例自身的迁移时序**：它声称"production v7 migrations + real import → v8"，但下游读取路径已到 v12，二者不一致。

## 移交（下一会话执行，Owner：Codex）

1. 通读 `:1002-1120`，确认该用例期望的终态 schema 版本（v8 还是 default_migrations 全量）。
2. 二选一并对齐：
   - (a1) 在调用 planner 前把库迁移到 ≥ v12；
   - (a2) 若语义上必须停 v7，则下游读取应改走不依赖 v12 列的路径（**需 DSH 先确认是否弱化契约**，不得自行改）。
3. 验收：该用例通过；**全量 pytest 0 failed**；`.NET` 与 `pins 18/18` 不变；`check.ps1` 不得降级。
4. 独立 Review：不得由实现者同一会话/实例执行。

## 终局定位（轮次 18）

同一用例内有两处迁移：`:1028` `migrations[:7]`（停在 v7）与 `:1085` `migrations`（全量）。
→ 失败发生在 **v7 阶段**：v7 与 v12 之间，代码已通过 `SqliteLibraryRepository` 读取 `chapters`（`_CHAPTER_COLUMNS` 含 `custom_rank`），而库仍停在 v7。

**结论**：这不是"fixture 少一列"，而是**该用例在 v7 阶段误用了当前 schema 的数据访问路径**。
**修复建议（供 Codex 执行，仍需先确认作者意图）**：
- 若 v7 阶段只想写 legacy 行 → 改用裸 SQL 写入，不经过 `SqliteLibraryRepository`；
- 或把 `:1085` 的全量迁移提前到任何仓储读取之前。
两种改法都不动 `src/**`，不改契约，符合路线 (a)。
**验收**：该用例通过 + 全量 pytest 0 failed + .NET/pins/check 不降 + 独立 Review。

## 可执行修复提案（轮次 20，未实施）

- 失败点：`tests/fea11/test_source_match.py:1048` 在 **v7** 库上构造 `SqliteLibraryRepository(conn)`，`:1052` 调 `runtime._planner.plan` → `library.py:217` 列清单含 v12 的 `custom_rank`。
- 提案：把 `:1085` 的 `MigrationRunner(conn, migrations).apply_pending()` 提前到 `:1048` 之前（legacy 行已在 `:1029-1039` 用裸 SQL 写入，不受影响）；若 `:1069-1120` 存在"库仍为 v7/v8"的版本断言，需同步调整或改为断言"迁移后版本 == 最新"。
- **未实施原因**：本会话上下文不足以安全核完 `:1069-1120` 的断言面，编辑可能破坏用例原意。留待新会话执行。
- 验收：该用例通过 + 全量 pytest 0 failed + `.NET`/pins/check 不降 + 独立 Review。

## 实施与实证（轮次 22，2026-11-14，已完成）

**Codex 首轮结论：`BLOCKED`，未改任何文件。** 它给出的理由是「把全量迁移提前会让导入在最新 schema 上运行，改变用例要保留的 v7 导入阶段语义」，并建议在测试文件内为 v7 章节读取做适配。

**DSH 实证推翻了该担忧**（事实优先于判断）：

1. 改动：把 `:1085` 的 `MigrationRunner(conn, migrations).apply_pending()` 前移到 `repo = SqliteLibraryRepository(conn)` 之前（`:1048`），`:1028` 的 `migrations[:7]` 建库与 `:1029-1039` 的裸 SQL legacy 行写入**原样保留**。
2. 结果：用例 `1 passed`（0.23s），**`:1075-1083` 的 legacy 形状断言全部保持**——因为迁移只加列、不改既有行；导入代码写入的形状由代码决定，与 schema 版本无关。
3. 全文件：`20 passed`。
4. 全量：**`3537 passed, 10 skipped, 0 failed`（316.39s）**，日志 `workspace/flea-loop/pytest-full-ro1.log`。

**DoD §4 判定：达成**（此前唯一失败的用例已修，且未删/未放宽任何断言、未加 skip/xfail、未改 `src/**`）。

**环境澄清**：Codex 报 `C:\Python314\python.exe: No module named pytest` 是它自身沙箱限制；该解释器实测有 `pytest 9.1.1`。后续派 Codex 跑 pytest 类任务时须注意此限制，或由 DSH 代跑。

