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
