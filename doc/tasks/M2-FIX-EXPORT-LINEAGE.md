---
id: M2-FIX-EXPORT-LINEAGE
title: Export history 持久层补 included_stale/missing page ids（F-1 修复）
kind: fix
status: ready
release_state: M2_FIX_EXPORT_LINEAGE_RELEASED
approval: released_by_orchestrator_2026-09-29_goal_g2 (Codex 代行,用户授权 2026-09-28;代理裁决,用户可撤销)
execution_approval: released_by_orchestrator_2026-09-29_goal_g2
suggested_owner: ZCode
owner: ZCode（待认领）
reviewer: DeepSeek Harness
integrator: Codex（另一子 agent 以 Codex 身份执行，保持 Owner≠Integrator）
depends_on: [M2-AC4]
base_commit: 8b0d9040
branch: agent/zcode/M2-FIX-EXPORT-LINEAGE
worktree: G:/CODEX/New Manga.worktrees/M2-FIX-EXPORT-LINEAGE-zcode
delivery_head: null
review: null
integration_merge: null
dispatch_state: RELEASED
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

**方案取舍（2026-09-29 释放时由编排会话冻结，代理裁决，用户可撤销）**：**采用方案 A**——`scope_snapshot_json` 内加 `included_stale_page_ids`/`included_missing_page_ids` 键。理由：`_parse_scope`（`service.py:482-491`）只校验 `page_ids` 是 list，加键向后兼容、旧行解析无歧义；不触碰 schema migration 纪律；方案 B 的可查询性收益当前无命令面消费者。**若实现中发现方案 A 不可行必须动 schema，停下登记 FAIL/BLOCKED 证据，不得擅自升级为方案 B**（那是范围变更）。

**per-page revision 范围裁定（DSH r1 P2-3，2026-09-29 冻结）**：**拆出本 Task 范围**——per-page 导出 revision/内容指纹需要触达导出执行路径抓取 revision 信息，范围显著更大，登记为未来独立候选（登记与否留 planning），本 Task 仅补 included ids。

**并发风险评估（DSH r1 P3-7，2026-09-29 冻结）**：`reading_export.py:176-240` write 的 read-modify-write + `DELETE … NOT IN` 并发互删问题**不在本 Task 修复范围**（既有问题、非本修复引入），Owner 在验证记录中做评估留痕即可，修复另立候选。

## Acceptance Criteria（2026-09-29 释放时冻结为正式 AC）

- [ ] **AC1 — 方案 A 落地：** `_scope_snapshot` 序列化新增 `included_stale_page_ids`/`included_missing_page_ids` 键（CONTINUE 放行时非空；ABORT 拒绝场景「零任何记录」语义不变）；`_record` 落库经 `scope_snapshot_json` 携带新键；`_parse_scope` 解析兼容（新键缺省为空、类型校验 list）。`ExportRecord`/读取路径（`reading_export.py` SELECT/INSERT/legacy import）如需映射同步补齐——**以最小变更为限，不新增列、不动 schema.py**。
- [ ] **AC2 — xfail 移除转 PASS：** 移除 `tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py` 中 `test_ac2_history_records_which_stale_pages_were_included` 的 `@pytest.mark.xfail`（strict）标记，断言转 PASS；**先证实修复再移除标记**（修复前该测试证红留痕）；XPASS 一旦出现即处理，不留「意外通过」。
- [ ] **AC3 — legacy 前向兼容：** 新增断言：变更前写入的旧 history 行（`scope_snapshot_json` 无新键）经新代码读取解析不报错、语义为「无 included ids 记录」而非崩溃或伪造。
- [ ] **AC4 — 回归如实：** `tests/m2_acceptance -q` 修复后预期 **33 passed + 1 xfailed**（仅剩 F-2 xfail）；如实际数字不同，如实记录原因。既有其余测试面（tests/core 等）零回归。
- [ ] **AC5 — 证据纪律：** 命令日志带 shell、解释器、固定 HEAD、EXIT；P3-7 并发评估留痕；`git diff --check <base>..<delivery-head>` exit 0；范围自检仅落允许路径。

## 允许修改范围（2026-09-29 冻结）

- `src/application/export/service.py`（`_record`/`_scope_snapshot`/`_parse_scope`/`ExportRecord` 映射）
- `src/infrastructure/sqlite/reading_export.py`（SELECT/INSERT/legacy import 的 scope_snapshot 映射，**不新增列**）
- `tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py`（**显式授权**：F-1 xfail 移除转 PASS + legacy 兼容新增断言；其余场景断言不改语义）
- `doc/tasks/M2-FIX-EXPORT-LINEAGE.md`、`verification/M2-FIX-EXPORT-LINEAGE/**`、`doc/handoffs/M2-FIX-EXPORT-LINEAGE-*.md`

## 禁止范围

- `src/infrastructure/sqlite/schema.py`（方案 A 不动 schema；发现必须动 schema 即停下登记，不得擅自升级方案 B）、per-page revision 字段（已裁定拆出）、并发 write 修复（P3-7 只评估）。
- 不得顺手把「导出失败留 failed 记录」等 accepted-but-unspecified 语义一起改：被拒导出零任何记录是 D03 §31 语义澄清事项（M2-AC4 Handoff 已披露），应单独裁定。
- 不修改与 F-1 无关的 IPC 契约、Library page-count 面（归 M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN，仍 proposed/NOT_RELEASED）；不修改 F-2 xfail 场景；不修改其他 src 路径、apps/**、doc/contracts/**、依赖。

## 交付与运行记录

- 尚无。释放时按 TASK 模板补全 Contract 并登记 release checkpoint。
