# P19-BOOT-1 真实启动证据

被测实现固定在 `c44b47dd9852121e18496502870f4e4cbaf5c737`。完整结果在 [real-startup-final.json](real-startup-final.json)，实际 stderr 在 [final-app.stderr.log](final-app.stderr.log)，启动命令与退出码在 [real-startup-final-run.log](real-startup-final-run.log)。

## 构建与启动

- 必需命令 `cargo build --locked --manifest-path apps/desktop/src-tauri/Cargo.toml`：`EXIT_CODE=0`，日志见 [cargo-build.log](cargo-build.log)。
- 为让 debug WebView 加载已构建的前端，又执行 `cargo build --locked --features tauri/custom-protocol --manifest-path apps/desktop/src-tauri/Cargo.toml`：`EXIT_CODE=0`，日志见 [cargo-build-custom-protocol.log](cargo-build-custom-protocol.log)。前端通过 `npm run build` 生成，日志见 [frontend-build.log](frontend-build.log)。
- 实际运行 `apps/desktop/src-tauri/target/debug/m2rc1-desktop.exe`，SHA-256 为 `ce13c1f8975d2831e67821fb361634911dcaddedc5672b53aa4959026b8b18b9`。
- 运行目录 `runtime-final6` 完全位于本 worktree 的 verification 目录。`APPDATA`、`LOCALAPPDATA`、`TEMP`、catalog、derived、managed、WebView2 UDF 均指向该隔离目录，没有使用或改写用户 `%APPDATA%` 数据。

## 复现状态和结果

[prepare_partial_state.py](prepare_partial_state.py) 只构造测试前置状态：通过现有 `initialize_namespace` 建立合法空 catalog，然后删除 `preview_namespace` 行和锁，确认 `catalog.sqlite` 存在且 `derived/` 为空。它不是修复步骤；修复由应用内 Core 启动链执行。启动前清单是 [partial-state-runtime-final6.json](partial-state-runtime-final6.json)，启动元数据是 [real-startup-launch-final.json](real-startup-launch-final.json)，其中 `catalog_exists=true`、`derived_entries_before_launch=0`。

真实启动结果：

- App exit code：`0`。
- WebView UIA 标题：`M2RC1|interactive|deny=5/5|allow=0/0|results=5`。
- stderr 含 `[core.derived_gc] orphan_files_removed=0 dead_rows_removed=0`；不含 `FileNotFoundError`、`JSONDecodeError` 或旧的误导性 `namespace busy (a managed peer holds a shared lease)` 文案。
- 实际鼠标点击导航并保存四个窗口截图：书架 [ui-bookshelf-real-window.png](ui-bookshelf-real-window.png)、工作台 [ui-workbench-real-window.png](ui-workbench-real-window.png)、阅读器 [ui-reader-real-window.png](ui-reader-real-window.png)、设置 [ui-settings-real-window.png)。
- 启动后 [runtime-binding-final.json](runtime-binding-final.json) 验证 lock 为 481 字节有效 JSON，catalog 中恰有一行 binding，lock 与 catalog binding、catalog/derived 的路径及文件身份完全匹配。

## 验证边界

这是按 Task 指定 Cargo debug host 运行的真实 Tauri 窗口，Core 由同一启动链通过 `M2RC1_SRC_ROOT` 加载 worktree 内的 Python 源码 sidecar；不是冻结的 PyInstaller sidecar 或安装包验收。Cargo 资源输入 `apps/desktop/src-tauri/target/core-sidecar` 是指向共享主仓库 target 的既有 junction；删除 junction 的操作被自动审批策略拒绝，未改变该 junction 或主仓库内容。因此本证据覆盖真实 debug host、Python Core 和四页 UI 启动，但不声称覆盖冻结 sidecar 的打包产物。
