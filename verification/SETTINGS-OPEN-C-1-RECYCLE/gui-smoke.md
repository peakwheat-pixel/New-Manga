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
4. **未完成**：在 GUI 中勾选"我理解不可恢复"并点击确认执行删除。UIA/SendInput 对该 checkbox 的点击未触发切换（工具限制，见备注），因此实际删除未在 GUI 执行；删除路径由 `RecycleBinSettingsPanel.test.tsx`（单批 payload 严格断言、25 本→20+5 分批、整库保护原样提示）与既有 Rust/Core 删除测试覆盖。
5. 环境注记：cargo test 需 `M2RC1_DEV_PREVIEW=1` + `M2RC1_PYTHON`；本 checkout 缺 gitignored sidecar bundle，为 `tauri-build` 的 resource 探测创建了 `target/core-sidecar/core-sidecar/` 占位目录（不入库）。

## 备注

- 烟测数据全部在隔离数据根，未触碰用户源文件/用户库。
- 保留策略（`auto_cleanup_days`）未开放：面板只读说明"没有调度器消费自动清理天数"。
