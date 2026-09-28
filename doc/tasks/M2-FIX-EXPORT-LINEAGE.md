---
id: M2-FIX-EXPORT-LINEAGE
title: Export history 持久层补 included_stale/missing page ids（F-1 修复候选）
kind: fix
status: proposed
release_state: NOT_RELEASED
approval: null
suggested_owner: ZCode
owner: null
reviewer: DeepSeek Harness
integrator: Codex（届时新会话代行）
depends_on: [M2-AC4]
base_commit: null
branch: null
worktree: null
delivery_head: null
review: null
integration_merge: null
dispatch_state: NOT_RELEASED
---

# M2-FIX-EXPORT-LINEAGE — Export history 持久层 included_stale/missing page ids 修复

## 来源与目标

**proposed / NOT_RELEASED 候选**——登记于 M2-AC4 集成收口（2026-09-28，integration merge `fc991821`，[集成记录](../verification/M2-AC4/integration-890f0c74/integration.md)）。来源 = M2-AC4 缺陷 **F-1**（AC1(a) FAIL 证据；AC2(b) 持久留痕缺口）+ [DSH r1 非作者 Review](../reviews/M2-AC4-890f0c74-dsh-r1.md) §3 独立裁定（证据充分、定性准确）与 P2-3 范围裁定要求。本文件仅为登记，base/branch/worktree 未冻结，**禁止在任何会话中未经 Rebaseline Plan 释放流程实施**。

缺陷：`ExportService` 落库的 export history 行**不含** `included_stale_page_ids`/`included_missing_page_ids`。CONTINUE 放行了哪些 stale 页在持久 lineage 中不可追溯（内存 `ExportResult` 字段正确，仅持久层缺失）。

证据链（DSH r1 §3 逐行核对，全部 verified-by-reading）：
- `src/application/export/service.py:425-464` `_record` 落库 13 键无 included ids；`:467-479` `_scope_snapshot` 只序列化 `page_ids/filenames/mode/overwrite_policy/stale_policy`；`:175-191` `ExportRecord` 无该字段；`:159-172` `ExportResult` 有（内存正确）。
- `src/infrastructure/sqlite/schema.py:436-450` `export_history` 表 13 列无该列；`src/infrastructure/sqlite/reading_export.py:146-174/:206-232`（SELECT/INSERT/ON CONFLICT）及 legacy import 均无。
- 全仓 grep `included_stale|included_missing`：`src/**` 仅内存 dataclass（`service.py:170-171/234-235`）与 UI 展示计数（`ui/viewmodels/export/viewmodel.py:286-287`），无任何持久化落点。
- 探针与 xfail 场景双证据：`verification/M2-AC4/raw/probe-output.log`；`tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py` xfail 场景 `test_ac2_history_records_which_stale_pages_were_included`（断言点 `:583-586`）。

## 缺陷描述与触点清单（释放时由 Codex 冻结）

触点（DSH r1 §3 划法）：
- `src/application/export/service.py`（`_record`/`_scope_snapshot`/`ExportRecord`）
- `src/infrastructure/sqlite/schema.py`（新 migration：加列或 `scope_snapshot_json` 版本化 schema）
- `src/infrastructure/sqlite/reading_export.py`（SELECT/INSERT/legacy import 映射）
- 必要时导出 DTO 与前端展示
- `tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py`（xfail 移除与断言转 PASS，见 AC）

**方案取舍（释放时冻结，二选一）**：
- **方案 A（低成本）**：`scope_snapshot_json` 内加 `included_stale_page_ids`/`included_missing_page_ids` 键。`_parse_scope`（`service.py:482-491`）只校验 `page_ids` 是 list，加键向后兼容，旧行解析无歧义。
- **方案 B（强契约）**：独立列 + migration，可查询性更好但触碰 schema；按仓库 migration 纪律（版本号 + checksum）补齐。

**per-page revision 范围裁定（DSH r1 P2-3，释放时必须显式裁定）**：记录里也没有 per-page 导出 revision/内容指纹（`_scope_snapshot` 无、schema 无）。AC1(a) 原文「页 scope（book/chapter/page **版本**）」若解释为含 revision，则仅补 included ids 仍无法从历史行复原「那次导出实际用了哪一版渲染」。释放时必须裁定：本 Task 是否包含 per-page revision 字段，还是拆独立 Task。

## Acceptance Criteria（释放时冻结为正式 AC）

1. **核心**：移除 `tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py` 中 `test_ac2_history_records_which_stale_pages_were_included` 的 `@pytest.mark.xfail`（`strict=True`）标记，断言转 PASS；**XPASS 一旦出现即处理**（先证实修复再移除标记，不留「意外通过」）。
2. 补 legacy 前向兼容断言：schema 变更后，变更前写入的旧 history 行（无新键/新列）经新代码读取解析不报错、语义为「无 included ids 记录」而非崩溃或伪造。
3. 若选方案 B：按仓库 migration 纪律补版本号 + checksum。
4. 回归 `tests/m2_acceptance -q` 保持既有场景全绿（修复后该套件应为 33 passed + 1 xfailed——仅剩 F-2 xfail——或按届时状态如实记录）。
5. 并发风险评估（DSH r1 P3-7）：`src/infrastructure/sqlite/reading_export.py:176-240` 的 `write` 是 read-modify-write + `DELETE … NOT IN (active_ids)`，并发导出会互相删除记录；本修复触碰同一函数，释放时一并评估是否同期修复或登记独立缺陷。

## 允许修改范围（释放时冻结）

- 上列触点文件 + `tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py`（**显式含对应 `@pytest.mark.xfail` 的移除与断言转 PASS**——这是 DSH r1 §5 承接条件，修复 Task 必须授权该测试文件）
- `doc/tasks/M2-FIX-EXPORT-LINEAGE.md`、`verification/M2-FIX-EXPORT-LINEAGE/**`、`doc/handoffs/M2-FIX-EXPORT-LINEAGE-*.md`

## 禁止范围

- **未释放禁止实施**（status=proposed / NOT_RELEASED）。
- 不得顺手把「导出失败留 failed 记录」等 accepted-but-unspecified 语义一起改：被拒导出零任何记录是 D03 §31 语义澄清事项（M2-AC4 Handoff 已披露），应单独裁定。
- 不修改与 F-1 无关的 IPC 契约、Library page-count 面（归 M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN）。

## 交付与运行记录

- 尚无。释放时按 TASK 模板补全 Contract 并登记 release checkpoint。
