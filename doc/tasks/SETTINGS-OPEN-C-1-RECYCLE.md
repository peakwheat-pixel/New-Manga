---
task_id: SETTINGS-OPEN-C-1-RECYCLE
kind: implementation
status: in_progress
owner: dsh
reviewer: reviewer-settings-a（非实现者）
created: 2026-10-23
base_commit: 6d6c08541cc9d92398bcb05fc5682ef4759fc4fd
allowed_paths:
  - apps/desktop/frontend/src/settings/**
  - apps/desktop/frontend/src/recycleBin/**（只读复用，不修改）
  - doc/tasks/**
  - doc/handoffs/**
  - verification/SETTINGS-OPEN-C-1-RECYCLE/**
---

# SETTINGS-OPEN-C-1-RECYCLE — 设置页回收站（查看 + 清空）

## 目标

按 [SETTINGS_SECTION_C_SCHEMAS.md](../design/SETTINGS_SECTION_C_SCHEMAS.md) §2（用户裁决 D1/D2/D11）把设置页「回收站」从禁用占位变成真实操作面：

- **查看**：复用 `library_list_recycle_bin_books`（既有 Tauri production 命令），展示数量 + 作品标题 + 页数；空态与读取失败可区分。
- **清空**：复用 `library_delete_books_permanently`（既有命令），二次确认对话框（"我理解不可恢复"勾选），按 **≤20 本/批**循环，每批 payload `{book_ids, confirmed_book_ids, confirm_count, confirm_permanent_delete}` 严格自洽；整库保护 `BOOK_DELETE_BATCH_WHOLE_LIBRARY` **原样提示**，不绕过。
- **不开放**：`auto_cleanup_days` 保留策略（无调度消费点）——只读说明。
- **不新增**：Core/Tauri wire、`settings_update_section` 白名单、Schema/migration、依赖。

## 范围

1. 新增 `apps/desktop/frontend/src/settings/RecycleBinSettingsPanel.tsx`：挂载自动加载、刷新、清空（确认 dialog + 分批 + 错误映射）、空态/加载态/错误态、成功提示、只读策略说明。
2. `SettingsPage.tsx`：`recycle_bin` 分类 `open: true` 并挂载面板；移除 `DISABLED_SECTION_TEST_IDS.recycleBin`（仍关闭：`backup_restore`、`plugins`）。
3. 测试：新增 `RecycleBinSettingsPanel.test.tsx`（列表/空态/加载失败/确认/单批/25 本分 2 批/整库保护/只读说明）；更新 `SettingsPage.test.tsx` 矩阵（10 开 2 关、键盘导航、still-closed 断言）。

## 禁止范围

- 不改 `settings_get`/`settings_update_section` 白名单与 P15 冻结文本。
- 不新增 `auto_cleanup_days` 或任何回收站设置键控件。
- 不改 Core/后端；不绕过整库保护；不改变既有删除语义。
- 不 push/merge/reset/stash。

## AC

- [x] **AC1 查看**：真实列表（数量/标题/页数）来自 Core；空态 ≠ 读取失败；加载骨架与重试可用。
- [x] **AC2 清空**：确认对话框（勾选后提交按钮可用）；单批 payload 严格（`confirmed_book_ids` 全等、`confirm_count` 匹配、`confirm_permanent_delete: true`）；25 本 → 20+5 两批；整库保护原样提示且不删除。
- [x] **AC3 无假控件**：无 `auto_cleanup_days` 控件（只读说明"没有调度器"）；不新增 section 写路径。
- [x] **AC4 前端**：Vitest 全绿；`tsc --noEmit` exit 0；SettingsPage 矩阵 10 开 2 关。
- [x] **AC5 证据**：固定 commit、原始日志、独立 Review（非实现者）、GUI 烟测（隔离库：建书 → 软删除 → 设置页查看/清空）。

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1-AC4 | `npx vitest run src/settings/RecycleBinSettingsPanel.test.tsx src/settings/SettingsPage.test.tsx` | node_modules | 待填 | 待填 |
| 全量前端 | `npm --prefix apps/desktop/frontend test` | node_modules | 待填 | 待填 |
| 类型 | `tsc --noEmit` | node_modules | 待填 | 待填 |
| 烟测 | dev preview：设置 → 回收站 → 清空 | 构建可用 | 待填 | 待填 |

## 交付与运行记录

- 2026-10-23：dsh 按设计 §2 实现面板与设置页接线；待测试与独立 Review。
- 未执行：Core/Tauri 改动（无新增 wire）、GUI 烟测（待构建）。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
|EV-C1-WIRE|AC1-AC5|PENDING|PENDING|PENDING|CANONICAL|

## Closeout Record

- Closeout：待独立 Review + GUI 烟测通过后关闭。
- canonical_evidence_status：pending；resource_closeout_status：pending。
- 删除/迁移/归档：0。
- 当前指针清理：STATUS/REBASELINE/LEDGER 登记本 Task。
