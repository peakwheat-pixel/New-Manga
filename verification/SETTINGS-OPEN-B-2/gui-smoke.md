# GUI smoke evidence (SETTINGS-OPEN-B-2)

- Time: 2026-10-22 ~23:19–23:33 +08:00
- App: `tools/dev/dev-preview.ps1`（Tauri dev window；隔离数据根 `G:\CODEX\New Manga.workspace\dev-preview\data`）
- Window: m2rc1-desktop.exe pid 21548, title "M2-RC1 resource channel runtime", URL http://localhost:5188/
- Build identity: `cleanup_preview` / `cleanup_run` / `cleanup_retry_pending` present in the production allowlist log line.

## 步骤与结果

1. `Ctrl+4` → 设置 → 分类列表确认 9 开 3 关：Provider / 网络代理 / OCR / 翻译 / 图片修复 / 排版样式 / 模型GPU / 任务并发 / **缓存Revision** 可点；回收站 / 备份恢复 / Plugin-Hooks 仍显示"未开放"。
2. 打开 缓存/Revision：面板挂载即自动 preview，显示"可清理 0 个文件 / 0 B、挂起项 0 个、无可清理文件"；两个按钮禁用（空态）。截图 `screenshots/03-cache-empty-idle.png`。
3. 在隔离数据根预置 3 个演示 tile（`data\data-root\managed\cache\webtoon-tiles\tile-demo-{1,2,3}.png`，每个 2048 B —— 注意 Core 的 managed root 是 `NEWMANGA_DATA_ROOT/managed`，不是 dev-preview 的 `data\managed`）。
4. 切换分类再回到 缓存/Revision：预览"可清理 **3** 个文件 / **6.0 KB**、挂起项 0 个"；"清理缓存"可用、"重试挂起项"禁用。截图 `screenshots/01-cache-preview-3-files.png`。
5. 点击"清理缓存"：结果条显示"清理结果：成功 **3** 个 · 失败 **0** 个 · 跳过 **0** 个"，预览归零、按钮回到空态禁用。截图 `screenshots/02-cache-cleaned.png`。
6. 目录核对：`tile-demo-*.png` 已被删除（只剩空的 `cache/webtoon-tiles`）。

## 备注

- 清理只作用于 `<managed_root>/cache/**` 安全前缀；演示文件在隔离数据根内创建，非用户库数据。
- 未制造失败场景（pending 重试路径由 `tests/core/test_core_cleanup_wire.py` 覆盖：失败进 pending、重试清空）。
- 自动清理天数 / Revision 保留策略不开放（面板只读说明）。
