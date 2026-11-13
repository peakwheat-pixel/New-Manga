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
