# GUI smoke — SETTINGS-OPEN-C-1-RECYCLE

- Time: 2026-10-23 ~07:36–08:02 +08:00
- App: `tools/dev/dev-preview.ps1`（Tauri dev window，隔离数据根 `G:\CODEX\New Manga.workspace\dev-preview\data`）
- Window: m2rc1-desktop.exe（pid 41156 最终轮），URL http://localhost:5188/
- 数据准备：在隔离库 `data-root/library.db` 建 2 部作品，并将其 `deleted_at` 置为非空（软删除；书架页"删除作品"按钮当前 GAP-G2 未接入，故用隔离库 SQL 软删除准备烟测数据，未触碰用户数据）。

## 发现并修复的既有缺口

1. 首次烟测（07:36）：设置页回收站面板显示 `CORE_UNAVAILABLE`，书架页「回收站」同样失败（`screenshots/00-bridge-gap-before-fix.png`）。
2. 根因：production 使用 `ResilientLibraryChannel`，其 `LibraryChannel` impl **未实现** `list_recycle_bin_books` → 继承 trait 默认 `unavailable`；`StdioLibraryChannel` 的实现从未被生产通道转发（R-007 读取面在生产恒可用性为 0）。
3. 修复：`ResilientLibraryChannel` 补 `fn list_recycle_bin_books(&self) { self.with_channel(|c| c.list_recycle_bin_books()) }`（与 `list_books` 同型；`permanently_delete_books` 转发原已存在）。`cargo test` 152 passed 验证。

## 步骤与结果

1. `Ctrl+4` → 设置分类：回收站可点击（10 开 2 关：备份/恢复、Plugin 仍"未开放"）。
2. 打开回收站：**真实读取 2 部作品**（标题列表、数量"回收站：2 部作品"、刷新/清空按钮、只读策略说明）——`screenshots/01-recycle-panel-2-books.png`。
3. 点击「清空回收站」：弹出二次确认 dialog——标题"永久删除确认（不可逆）"、2 部作品列表、三条不可逆提示、"我理解不可恢复"勾选、取消/确认按钮——`screenshots/02-confirm-dialog-2-books.png`。
4. **真实清空（08:25–08:31）**：勾选方式为键盘（Tab 聚焦 checkbox → Space），确认执行后：
   - 第一次执行时回收站 = 全库 → Core 返回 `BOOK_DELETE_BATCH_WHOLE_LIBRARY`，dialog 原样显示"不能删除整个书库：回收站包含全部作品，请保留至少一部作品。"（整库保护在真实链路生效，见 `screenshots/03-whole-library-guard.png`）。
   - 在书架新建 1 部活跃作品（ActiveBook）后再次清空 → 成功：面板显示"回收站：0 部作品"、"已永久删除 2 部作品。"、"回收站为空。"，清空按钮禁用（`screenshots/04-clear-success.png`）。
   - 数据库核对（隔离库）：`books` 仅剩 `ActiveBook`（`deleted_at IS NULL`），回收站 2 部作品的行已被真实删除（非软删除残留）。
5. **结论**：React → Tauri → Core 的回收站查看/清空链路端到端可用；≤20 分批由 Vitest（25→20+5 payload 断言）覆盖，GUI 实测 2 部一次成功。
6. 环境注记：cargo test 需 `M2RC1_DEV_PREVIEW=1` + `M2RC1_PYTHON`；本 checkout 缺 gitignored sidecar bundle，为 `tauri-build` 的 resource 探测创建了 `target/core-sidecar/core-sidecar/` 占位目录（不入库）。

## 备注

- 烟测数据全部在隔离数据根，未触碰用户源文件/用户库。
- 保留策略（`auto_cleanup_days`）未开放：面板只读说明"没有调度器消费自动清理天数"。
