---
task_id: SETTINGS-OPEN-C-1-RECYCLE
author: dsh (Lead, epoch 10)
recipient: Codex / 下一批次 Owner
base_commit: 6d6c08541cc9d92398bcb05fc5682ef4759fc4fd
delivery_head: a653c8230ba30948b19e551a4450fa7a79920951
status: in_review
---

# Handoff — SETTINGS-OPEN-C-1-RECYCLE（设置页回收站：查看 + 清空）

## 1. 交付摘要

按 [SETTINGS_SECTION_C_SCHEMAS.md](../design/SETTINGS_SECTION_C_SCHEMAS.md) §2 与用户裁决 D1/D2/D11，把设置页「回收站」从禁用占位变成真实操作面：

- **查看**：新增 `RecycleBinSettingsPanel`，挂载即调用既有 `library_list_recycle_bin_books`；显示数量 + 作品标题 + 页数；空态（"回收站为空"）与读取失败（`CORE_UNAVAILABLE` 提示 + 重试）严格区分；不新增 `deleted_at`（D2）。
- **清空**：复用既有 `library_delete_books_permanently`，二次确认对话框（复用 `PermanentDeleteConfirmDialog`：勾选"我理解不可恢复"后才可提交），按 **≤20 本/批**循环，每批 payload `{book_ids, confirmed_book_ids: 同序全等, confirm_count, confirm_permanent_delete: true}`；整库保护 `BOOK_DELETE_BATCH_WHOLE_LIBRARY` 原样提示不绕过；失败映射（preflight/not-found/限批）。
- **不开放**：`auto_cleanup_days` 保留策略（无调度消费点）——只读说明；无 `settings_update_section` 写路径（D11）。
- **设置页**：`recycle_bin` 分类 `open: true`，`DISABLED_SECTION_TEST_IDS` 仅剩 `backupRestore`/`plugins`（10 开 2 关）。
- **Rust 修复（烟测发现的既有缺口）**：production 通道 `ResilientLibraryChannel` 未实现 `list_recycle_bin_books`，继承 trait 默认 `unavailable` → R-007 读取面在生产恒为 `CORE_UNAVAILABLE`（书架回收站同样失效）。已补 `self.with_channel(|c| c.list_recycle_bin_books())`；`permanently_delete_books` 转发原已存在。

## 2. 验证

| 命令 | 结果 |
|---|---|
| `npx vitest run src/settings/RecycleBinSettingsPanel.test.tsx src/settings/SettingsPage.test.tsx` | PASS（7 + 17 tests） |
| `npm --prefix apps/desktop/frontend test` | PASS（**42 files / 413 tests**） |
| `tsc --noEmit` | exit 0 |
| `cargo test --locked -- --skip packaged_sidecar_tests --test-threads=1`（dev overlay + `M2RC1_PYTHON`） | PASS（**152 passed / 1 ignored / 12 filtered**） |
| GUI 烟测（dev preview，隔离数据根） | 修复前：书架与设置页回收站均 `CORE_UNAVAILABLE`（screenshots/00）；修复后：设置页回收站读取 **2 部作品** + 清空按钮弹出二次确认 dialog（2 部/三条提示/勾选控件，screenshots/01–02） |

原始日志与截图：`verification/SETTINGS-OPEN-C-1-RECYCLE/**`。

## 3. 未执行 / 遗留

1. **GUI 实际删除未执行**：UIA/SendInput 对该 dialog 的 checkbox 点击未触发切换（工具限制）；删除路径由 7 个 Vitest 用例（单批 payload 严格断言、25 本→20+5 分批、整库保护、错误映射）与既有 Rust/Core 删除测试覆盖。若需要端到端 GUI 证据，可由人工或后续自动化补一次勾选+确认。
2. **packaged sidecar**：本 checkout 缺 gitignored bundle；cargo 测试用 dev overlay（`M2RC1_DEV_PREVIEW=1` + `M2RC1_PYTHON`）并创建了 `target/core-sidecar/core-sidecar/` 占位目录（不入库）。
3. **书架页"删除作品"仍为 GAP-G2 未接入**（本次烟测靠隔离库 SQL 软删除准备数据）；不属本 Task 范围，未改动。

## 4. 推荐下一步

按裁决顺序释放 **`SETTINGS-OPEN-C-2-BACKUP`**（备份/恢复）：`.nmbak` v1 包格式、4/5 条应用层命令、恢复覆盖 + 强制 pre_restore + running Run 拒绝、Tauri dialog 文件选择、面板 + 测试 + GUI 烟测；之后 C-3 Plugin 管理面。
