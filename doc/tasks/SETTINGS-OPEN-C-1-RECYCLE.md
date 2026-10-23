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
  - apps/desktop/src-tauri/src/library_bridge.rs（仅补 Resilient 通道转发，见运行记录）
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
| AC1-AC4 | `npx vitest run src/settings/RecycleBinSettingsPanel.test.tsx src/settings/SettingsPage.test.tsx` | node_modules | PASS（7 + 17 tests） | ui-test-targeted.log |
| 全量前端 | `npm --prefix apps/desktop/frontend test` | node_modules | PASS（42 files / 413 tests） | ui-test-frontend.log |
| 类型 | `tsc --noEmit` | node_modules | PASS（exit 0） | ui-tsc.log |
| Rust 桥接 | `cargo test --locked -- --skip packaged_sidecar_tests --test-threads=1`（dev overlay + `M2RC1_PYTHON`） | Rust 1.98.1 | PASS（152 passed / 1 ignored / 12 filtered；编译含 `ResilientLibraryChannel::list_recycle_bin_books`） | wire-cargo-test-serial.log |
| 烟测 | dev preview：设置 → 回收站 → 清空 | 构建可用 | 读取 PASS（2 部作品）+ 确认 dialog PASS（2 部/三条提示/勾选控件）；实际删除的 checkbox 点击在 UIA/SendInput 下未切换 → 删除链路由 Vitest + Rust/Core 既有测试覆盖 | gui-smoke.md + screenshots/00..02 |

## 交付与运行记录

- 2026-10-23：dsh 按设计 §2 实现面板与设置页接线；待测试与独立 Review。
- 2026-10-23（烟测发现的既有缺口）：production（Resilient）通道**未实现** `list_recycle_bin_books`，trait 默认返回 `unavailable` → 书架回收站与设置页读取均 `CORE_UNAVAILABLE`（R-007 读取面在生产从未可用）。修复：`ResilientLibraryChannel` 补转发 `self.with_channel(|c| c.list_recycle_bin_books())`（与 `list_books` 同型）；无新 wire。`permanently_delete_books` 转发已存在，清空路径不受影响。
- 2026-10-23（烟测结果）：修复后 dev preview 设置页回收站**读取到 2 部软删除作品**（此前 R-007 读取面在生产恒为 `CORE_UNAVAILABLE`，见 screenshots/00）；"清空回收站"弹出二次确认 dialog（2 部作品、三条不可逆提示、"我理解不可恢复"勾选、取消/确认，见 screenshots/01/02）。**实际勾选并执行删除未在 GUI 完成**：UIA/SendInput 点击 checkbox 未触发切换（工具限制），删除链路由 `RecycleBinSettingsPanel.test.tsx`（含 25 本分批 payload 断言、整库保护）与既有 Rust/Core 删除测试覆盖。
- 环境注记：本 checkout 的 gitignored sidecar bundle 缺失；cargo test 需要 `M2RC1_DEV_PREVIEW=1` + `M2RC1_PYTHON`，并为 `tauri-build` 的 resource 探测创建了 `target/core-sidecar/core-sidecar/` 占位目录（不入库，真实 bundle 由 `packaging/m2ac5/build_sidecar.ps1` 生成）。
- 未执行：Core 改动（无新增 wire）。
## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
|EV-C1-GUI-SMOKE|AC1-AC5|verification/SETTINGS-OPEN-C-1-RECYCLE/gui-smoke.md|a653c8230ba30948b19e551a4450fa7a79920951|47c3494e813a53d0f8e0afb1126567ff343bd5f958cdcef7d9da85adb67ed9c1|CANONICAL|
|EV-C1-00-BRIDGE-GAP-BEFORE-FIX|AC1-AC5|verification/SETTINGS-OPEN-C-1-RECYCLE/screenshots/00-bridge-gap-before-fix.png|a653c8230ba30948b19e551a4450fa7a79920951|5f502ea6e6253ea3a1a41279e371f51daae43a0eb0f81348b86b917b9386b1f2|CANONICAL|
|EV-C1-01-RECYCLE-PANEL-2-BOOKS|AC1-AC5|verification/SETTINGS-OPEN-C-1-RECYCLE/screenshots/01-recycle-panel-2-books.png|a653c8230ba30948b19e551a4450fa7a79920951|2211bfefac723262ad834dd80169d2b34c1d794dfff1db5e7cf2fcea40bdfcb9|CANONICAL|
|EV-C1-02-CONFIRM-DIALOG-2-BOOKS|AC1-AC5|verification/SETTINGS-OPEN-C-1-RECYCLE/screenshots/02-confirm-dialog-2-books.png|a653c8230ba30948b19e551a4450fa7a79920951|318e9a60108db1f0266e95fd73f06bda6709e7df5e9c537499c2c59abb1521d7|CANONICAL|
|EV-C1-UI-TEST-FRONTEND|AC1-AC5|verification/SETTINGS-OPEN-C-1-RECYCLE/ui-test-frontend.log|a653c8230ba30948b19e551a4450fa7a79920951|5daa6e703cd6d0eef299044936f42b2801be0242ea2e1aa39f7013b9e2b74423|CANONICAL|
|EV-C1-UI-TEST-TARGETED|AC1-AC5|verification/SETTINGS-OPEN-C-1-RECYCLE/ui-test-targeted.log|a653c8230ba30948b19e551a4450fa7a79920951|db8aecf5534f06e95fef9ff558c2ec8a57bbf387ff533b825a73b261c4f3aa35|CANONICAL|
|EV-C1-UI-TSC|AC1-AC5|verification/SETTINGS-OPEN-C-1-RECYCLE/ui-tsc.log|a653c8230ba30948b19e551a4450fa7a79920951|e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855|CANONICAL|
|EV-C1-WIRE-CARGO-TEST-SERIAL|AC1-AC5|verification/SETTINGS-OPEN-C-1-RECYCLE/wire-cargo-test-serial.log|a653c8230ba30948b19e551a4450fa7a79920951|dc5ad222f35f2c6e363e935280a3dbb4f9edf74a26a518c7616c874a0a4ab95e|CANONICAL|

## Closeout Record

- Closeout：待独立 Review + GUI 烟测通过后关闭。
- canonical_evidence_status：complete；resource_closeout_status：complete。
- 删除/迁移/归档：0。
- 当前指针清理：STATUS/REBASELINE/LEDGER 登记本 Task。
