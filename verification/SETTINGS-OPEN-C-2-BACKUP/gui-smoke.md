# GUI smoke — SETTINGS-OPEN-C-2-BACKUP

- Time: 2026-10-23 ~10:31–10:43 +08:00
- App: `tools/dev/dev-preview.ps1`（Tauri dev window，隔离数据根 `G:\CODEX\New Manga.workspace\dev-preview\data`）
- Window: m2rc1-desktop.exe（pid 496），URL http://localhost:5188/
- 数据：隔离库已有 `ActiveBook`（1 部）；备份根 `<data-root>/backups/`（Core 固定，不含用户选择路径）。

## 步骤与结果

1. `Ctrl+4` → 设置：分类列表 **11 开 1 关**（备份/恢复已可点；Plugin/Hooks 仍"未开放"）。
2. 打开「备份/恢复」：标题/说明、`备份：0 个`、刷新/立即备份、空态"还没有备份…"、只读说明"自动备份（定时 / 启动时）未开放——当前没有调度器消费自动备份计划与保留策略"——`screenshots/01-backup-panel-empty.png`。
3. 点「立即备份」→ 生成 **1 个 manual 包**（2026/10/23 10:35:20 / 10.9 KB / 校验通过），notice"已创建备份 6c798990（校验通过）。"；磁盘核对 `backups/6c7989900a684b548937595993be836e.nmbak` 存在（11 159 bytes，zip 含 manifest/library.db/sidecar）——`screenshots/02-backup-created.png`。
4. 改数据：向隔离库插入 `PostBackupBook`（模拟备份后新增作品；恢复前 DB 为 ActiveBook + PostBackupBook 两本）。
5. 点 manual 行的「恢复」→ 二次确认（"恢复备份（覆盖当前全部数据）"+ 从 6c798990 / 2026/10/23 10:35:20 恢复 + "用备份中的数据库与受管文件覆盖当前数据；操作前会自动创建 pre_restore 备份，恢复失败可回滚" + 取消/覆盖并恢复）——`screenshots/03-restore-confirm-dialog.png`。
6. 点「覆盖并恢复」→ **成功**：notice"已从备份 6c798990 恢复（恢复前备份 6ba741fa）。其他页面可能仍显示旧数据，请手动刷新。"；列表变为 3 个（2 个 pre_restore + 1 个 manual），全部"校验通过"——`screenshots/04-restore-success.png`。
7. 数据库核对（隔离库）：恢复后 `books` 仅剩 `ActiveBook`（`PostBackupBook` 已被覆盖消失）；`backups/` 下新增 `pre_restore` 包（f7cae7c4、6ba741fa）。

## 补充：managed 文件往返（review r1 P2）

1. 隔离库 seed：`book-1/chapter-1/page-1` + `art-1` + `rev-1`（current/pinned），managed 文件 `managed/books/book-1/chapters/chapter-1/original/page-1.png` = `ORIGINAL-MANAGED-BLOB`。
2. 设置 → 备份/恢复 → 立即备份：生成 `0db3692b…nmbak`（11.6 KB，zip 含 `managed/…/page-1.png`；manifest `managed_file_count=1`、`revision_refs` 含 `rev-1` 与 `region_id: null`），列表"校验通过"。
3. 篡改 managed 文件为 `TAMPERED-AFTER-BACKUP` → 对该包「恢复」→「覆盖并恢复」→ notice"已从备份 0db3692b 恢复（恢复前备份 fceb8a60）"。
4. 核对：managed 文件字节恢复为 `ORIGINAL-MANAGED-BLOB`；备份列表 5 个（含新 pre_restore）——`screenshots/05-managed-restore.png`。

## 限制与备注

- 窗口在 UIA 操作间多次被最小化（driver 的 SendInput 点击与 UIA invoke 交替时 Windows 焦点切换），截图前用 `ShowWindow(SW_RESTORE)` 还原；操作本身均通过 UIAutomation Invoke/ValuePattern 完成。
- 备份/恢复全部在隔离数据根执行，未触碰用户源文件；恢复只读写 DB 与受管根。
- 环境注记：cargo test 需 `M2RC1_DEV_PREVIEW=1` + `M2RC1_PYTHON`；本 checkout 缺 gitignored sidecar bundle，`tauri-build` 的 resource 探测用 `target/core-sidecar/core-sidecar/` 占位目录（不入库）。
