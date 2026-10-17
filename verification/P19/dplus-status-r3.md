# P19 发现 R3：应用可启动，但 CDP 通道不可用 + 当前为诊断面

- 时间：2026-10-17
- 前提：P19-BOOT-1 修复 + **sidecar 重建**（`build_sidecar.ps1`，HEAD=c6d2e9a3，11:15 完成）+ cargo build 刷新资源（hash 一致 `41932CED…`）
- **结果 A（正面）**：应用**成功启动**——pid 存活、窗口标题 `M2-RC1 resource channel runtime`、`responding=True`；stderr 显示 `[core.derived_gc] orphan_files_removed=0 dead_rows_removed=0`（新自举逻辑生效）与 `[m2rc2-allowlist] production:…`（含 49 条生产面，包含 P15 全部 settings 命令与 `credential_put`/`credential_clear`）。
- **结果 B（负面，如实登记）**：**CDP 不可用**。设 `WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS=--remote-debugging-port=9222` 启动后：所有 `msedgewebview2.exe` 命令行**均不含** `remote-debugging-port`，9222 **无监听** → **Tauri 覆盖了该环境变量**。→ **D+ 的 CDP 通道在本构建上不可用**，需改用 **CUA（截图 + UIA + 输入）** 作为验收通道（即 D 变体，仍为**真实 WebView2**）。
- **结果 C（待查）**：当前窗口内容为**诊断/probe 面**（UIA 可见 `Pane 'M2RC1|interactive|deny=5/5|allow=0/0|results=5'`），**非四页 UI** → 验收前需确定如何进入四页界面（构建/模式/环境变量问题）。
- 处置：应用已关闭（桌面已复原）；下一轮先解决"进入四页 UI"与"CDP 替代通道（CUA）"两项，再执行四页断言。