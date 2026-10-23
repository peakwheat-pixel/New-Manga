---
task_id: SETTINGS-OPEN-C-1-RECYCLE
author: dsh (Lead, epoch 10)
recipient: Codex / 下一批次 Owner
base_commit: 6d6c08541cc9d92398bcb05fc5682ef4759fc4fd
delivery_head: 984311f0a706058bd39226296514be5492760e4c
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
| GUI 烟测（dev preview，隔离数据根） | 修复前：书架与设置页回收站均 `CORE_UNAVAILABLE`（screenshots/00）；修复后：读取 **2 部作品** + 二次确认 dialog（screenshots/01–02）；**实际清空**：整库保护先原样提示（screenshots/03），补 1 部活跃作品后清空成功——"回收站：0 部作品"+"已永久删除 2 部作品。"（screenshots/04），隔离库核对仅剩 ActiveBook |

原始日志与截图：`verification/SETTINGS-OPEN-C-1-RECYCLE/**`。

## 3. 未执行 / 遗留

1. ~~GUI 实际删除未执行~~ → **r1 复审后已补**：键盘勾选（Tab→Space）→ Space 确认，实测整库保护 + 成功清空 + DB 核对（screenshots/03/04）。
2. **packaged sidecar**：本 checkout 缺 gitignored bundle；cargo 测试用 dev overlay（`M2RC1_DEV_PREVIEW=1` + `M2RC1_PYTHON`）并创建了 `target/core-sidecar/core-sidecar/` 占位目录（不入库）。
3. **书架页"删除作品"仍为 GAP-G2 未接入**（本次烟测靠隔离库 SQL 软删除准备数据）；不属本 Task 范围，未改动。

## 3.1 Review r1 处置（changes_requested → r2）

- **P1-1**：补真实 GUI 清空（整库保护 → 补活跃书 → 成功）+ DB 核对；证据 screenshots/03、04。
- **P1-2**：Task 置 `in_review`，canonical/resource 回退 `pending`，Review 通过后再 closeout。
- **P2-1**：allowed_paths 补 `library/client.ts`、`client.test.ts`，并记录 Lead 集成的 doc 指针（design/STATUS/REBASELINE/LEDGER）。
- **P2-2**：实现范围写清 `6d6c085..984311f0`（前端面板 `cb50b15`，Rust+证据 `a653c823`，复审修复 `984311f0`）。
- **P2-3**：前端日志重录，含命令与 exit 行。
- **P2-4**：`listRecycleBinBooks` 非数组 → `RECYCLE_BIN_MALFORMED` typed error + 2 个测试。
- **P2-5**：批量失败后 `await load()` 再抛，重试不重发已删除 ID。

## 4. 推荐下一步

按裁决顺序释放 **`SETTINGS-OPEN-C-2-BACKUP`**（备份/恢复）：`.nmbak` v1 包格式、4/5 条应用层命令、恢复覆盖 + 强制 pre_restore + running Run 拒绝、Tauri dialog 文件选择、面板 + 测试 + GUI 烟测；之后 C-3 Plugin 管理面。
