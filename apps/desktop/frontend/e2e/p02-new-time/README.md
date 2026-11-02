# P02-NEW-TIME-X6-AC1-AC7 — WebView2 e2e drivers

零新增依赖的 Node 脚本组（Node >= 22，使用内置 `fetch`/`WebSocket`/`child_process`）。它们启动**固定 packaged EXE**（只读）并通过 WebView2 官方 `WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS=--remote-debugging-port=9333` 建立 CDP 驱动；所有可写路径全部隔离在 `G:/CODEX/New Manga.workspace/task-envs/P02-NEW-TIME-X6-AC1-AC7/run-r1/<scenario>/`（`lib/env.mjs` 在启动前断言场景目标目录为空，任何预存内容都会中止）。

## 运行（按 AC 顺序）

```
node ac1-identity.mjs      # AC1 身份：进程/窗口/WebView2/OS/allowlist 公告 + 截图（真实 IPC）
node ac2-navigation.mjs    # AC2 真实鼠标/键盘导航 Workbench + 按钮状态 + 截图（真实 IPC）
node ac3-debounce.mjs      # AC3 300ms 静默期/切页取消/迟到响应（Phase A 真实 IPC，Phase B 标注 MOCK_IPC）
node ac4-write-refresh.mjs # AC4 retype/undo/restore 三项写后即时 readback（REAL_WEBVIEW_MOCK_IPC）
node ac5-keyboard.mjs      # AC5 Tab/Shift+Tab/Enter/Space/Escape 与焦点（真实 IPC）
node ac6-contrast.mjs      # AC6 computed colors + WCAG ratio + F token 映射（真实 IPC）
```

每个脚本独立启动/退出应用；证据先落 `run-r1/<scenario>/logs/`，随后将整个目录复制为 canonical 证据到 `verification/P02-NEW-TIME-X6-AC1-AC7/<scenario>/`。

## 分层（mock 面，逐场景如实标注）

- `ac1/ac2/ac5/ac6`：无 mock —— 真实 Tauri IPC + packaged sidecar Core + 空合成 catalog。
- `ac3` Phase A：仅安装 observer wrapper（透传记录 invoke 时序），行为全真实；Phase B：仅 `resolve_page_resource` / `list_regions` 两个命令在 invoke 边界 mock（构造迟到响应），产品 React 代码与 timer 全真实，无 fake timer。
- `ac4`：`REAL_WEBVIEW_MOCK_IPC` —— invoke 边界 mock 合成数据（镜像 production 表面的允许/拒绝形状），真实 WebView2 + 真实组件 + 默认 `resolveDebounceMs=300` / `regionDebounceMs=300`；**不**声称验证真实 Core/SQLite 持久化。

## 安全约束（编码在 `lib/env.mjs`）

- 启动前 `assertLaunchTargetsClean(scenarioRoot)`：run-r1/<scenario>/ 内所有目标必须 ABSENT 或 EMPTY，否则中止。
- 环境重建时清除全部 `M2RC1_* / M2RC2_* / M2AC1_* / NEWMANGA_*`；永不设置 `M2RC1_PROBE_OUT`、`M2AC1_TEST_MODE`（保持 production interactive 表面，Console/Workbench 导航才会出现）。
- `APPDATA/LOCALAPPDATA/TEMP/TMP/NEWMANGA_DATA_ROOT/M2RC1_DERIVED_ROOT/M2RC1_MANAGED_ROOT/M2RC2_CATALOG_DB/WEBVIEW2_USER_DATA_FOLDER` 全部指向 run-r1/<scenario>/ 子目录。

## 时钟

所有行为时序取自页面内 `performance.now()`（单调时钟），由 `window.__p02InvokeLog` 记录并通过 CDP binding 同步到 Node 侧日志；不使用 fake timer。
