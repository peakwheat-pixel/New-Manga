# GUI smoke — PLUGIN-RUNTIME-1

- Time: 2026-10-23 ~14:54–14:57 +08:00
- App: `tools/dev/dev-preview.ps1`（Tauri dev window，隔离数据根 `G:\CODEX\New Manga.workspace\dev-preview\data\data-root`）
- Window: m2rc1-desktop.exe（pid 47132），URL http://localhost:5188/
- 授权：用户 2026-10-23「授权 PLUGIN-RUNTIME-1，按建议值 D1–D6」

## 预置数据（隔离数据根，不入库）

- `<data-root>/plugins/demo-detect/`：合法 manifest v1（`permissions: []`，`hooks: ["after_detect"]`，entry `plugin.py`）。
- `<data-root>/plugins/bad-permissions/`：manifest 声明 `permissions: ["files_read"]`（首发限制应拒绝）。

## 步骤与结果

1. `Ctrl+4` → 设置：**12 个分类全部可点**（Plugin/Hooks 不再有"未开放"徽标）；nav 显示 11 个原有分类 + Plugin/Hooks。
2. 打开「Plugin/Hooks」：标题/说明（本地目录插件、默认全部禁用、permissions: [] 首发、Hook 独立子进程 + 超时/崩溃隔离）、全局开关「启用插件系统（默认关闭）」为**未勾选**、打开插件目录/刷新按钮、列表 2 个插件：
   - `Demo Detect Plugin 1.0.0` — 已禁用，hooks `after_detect`，「启用」；
   - `bad-permissions` — **已拒绝** + 拒绝原因 `PLUGIN_PERMISSIONS_UNSUPPORTED: this release only loads plugins with permissions: []`，「启用」按钮 disabled。
   - 审计（最近 20 条）：`加载成功 demo-detect`、`拒绝加载 bad-permissions`（真实 `plugin_events` 行）。
3. 勾选全局开关 → notice「插件系统已启用…」；点 Demo 插件「启用」→ notice「已启用插件 demo-detect。」；列表状态变为**已启用**、按钮变「禁用」；审计新增 `已启用 __global__` 与 `已启用 demo-detect` 两条——`screenshots/01-plugin-panel-enabled.png`。
4. 关闭 app。

## 覆盖说明

- GUI 覆盖 AC1（发现 + 拒绝原因可见）、AC2（默认禁用 → 全局开关 → 逐插件启用）、AC4（审计可见）。
- **Hook 实际调用/崩溃/超时** 由单测覆盖（真实子进程）：`tests/infrastructure/test_plugin_runtime.py`（after_detect 结果、crash → `plugin_error`、slow → `PLUGIN_HOOK_TIMEOUT`、未知 hook/坏 payload、rejected 插件不可启用）。
- 流水线接线点（before/after detect/ocr/export 在真实 Run 中触发）不在本 Task：运行时 API `run_hook` 已就绪并有测试；接线属于后续批次（Task 未授权扩大范围）。

## 限制与备注

- 窗口焦点：UIA Invoke/TogglePattern 全程驱动（无 SendInput 点击），未出现焦点丢失。
- 插件目录为隔离数据根内 `<data-root>/plugins`（D4：dev preview 与生产各自解析 data root）。
