# P20-ISOLATION-1 证据目录与自愈验证说明

## 1. 任务背景与核心改动
- **前置缺陷**：`P20` AC6 实测表明，强杀 `core_service` 后 Tauri 窗口存活，但 UI 无故障提示，且 8s 内 sidecar 未重生。
- **改动范围**：
  1. `apps/desktop/src-tauri/src/library_bridge.rs`：
     - `StdioLibraryChannel` 支持 reader 线程 EOF/读取异常即时感知并调用 `on_down` 回调；
     - 实现自愈包装器 `ResilientLibraryChannel`（最大连续失败上限 3 次，指数退避 500ms -> 1000ms -> 2000ms，1.5s 后台轻量心跳探测）；
     - 通过状态事件派发器广播 `restarting`、`recovered`、`fatal` 状态。
  2. `apps/desktop/src-tauri/src/main.rs`：
     - 将 channel 包装为 `ResilientLibraryChannel`，启动心跳线程；
     - 注入 `app_handle.emit("core:lifecycle_status", ...)`。
  3. `apps/desktop/frontend/src/events.ts`：
     - 隔离定义 `LIFECYCLE_STATUS_EVENT = "core:lifecycle_status"` 与 `onLifecycleStatusChanged`（保持原有 6 个领域事件常量不变）。
  4. `apps/desktop/frontend/src/shell/AppShell.tsx`：
     - 监听 `core:lifecycle_status` 并引入 2.0s 前端主动心跳探测；
     - 渲染全局提示横幅 `core-status-banner`：
       - `restarting`：`"后端服务异常，正在尝试热重启..."`
       - `fatal`：`"后端服务异常，自动重启失败，请检查服务日志"`（含重试按钮）
       - `recovered`：`"后端服务已恢复正常"`
     - 容器采用 Keep-Alive 保全模式，不卸载未提交表单与子页面。

---

## 2. 自动化测试证据（单元与集成测试）
- **Rust 单元测试**：
  - 测试命令：`cargo test --test resilient_channel --manifest-path apps/desktop/src-tauri/Cargo.toml`
  - 测试用例：
    - `resilient_channel_triggers_restart_and_emits_restarting_status`: PASS
    - `resilient_channel_caps_retries_and_emits_fatal_after_three_failures`: PASS
- **前端集成与状态保全测试**：
  - 测试文件：`apps/desktop/frontend/src/shell/AppShell.lifecycle.test.tsx`
  - 测试命令：`npm test -- src/shell/AppShell.lifecycle.test.tsx`
  - 覆盖 AC：
    - AC1：UI 呈现明确后端异常状态横幅并匹配关键词。
    - AC2：重启成功后呈现恢复横幅，连续失败呈现致命降级横幅。
    - AC3：崩溃与重启期间未提交草稿（书籍标题输入框）保全，状态不丢失且恢复后可正常提交。
  - 前端全量测试：`npm test`（29 测试文件，288 测试用例全 PASS）。
- **SHA-256 二进制一致性（AC4）**：
  - `apps\desktop\src-tauri\target\core-sidecar\core-sidecar\core_service.exe` 与 `apps\desktop\src-tauri\target\debug\resources\core-sidecar\core_service.exe` 校验一致：`CD8DCC5E6DE568690694125D68162784C6A8427E6758C228080396B9599C98F1`。

---

## 3. 端到端 UI 验证复跑指南（供 Coordinator/Reviewer）
由于无桌面会话限制（WebView2 创建报错 `HRESULT 0x80070578: 无效的窗口句柄`），端到端 UIAutomation 验证须在真实桌面会话执行。

**复跑命令**：
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File "G:\CODEX\New Manga\verification\P20-ISOLATION-1\run-ac6-ui-verification.ps1"
```
**产物说明**：
- 脚本会自动使用 `$env:TEMP` 隔离目录作为数据根；
- 生成 `verification/P20-ISOLATION-1/run-<timestamp>/` 目录，包含：
  - `trace.log`：完整的事件时间线与断言结果（`ac6:window-before-kill`、`ac6:sidecar-running`、`ac6:main-window-survives-sidecar-death`、`ac6:user-visible-error-indicated`、`ac6:sidecar-auto-respawned`、`ac6:window-still-alive-after-test`）；
  - `ui-before-kill.txt`：强杀前的 UI 元素树；
  - `ui-after-kill.txt`：强杀后的 UI 元素树（检验异常横幅文案）；
  - `ui-after-respawn.txt`：自愈后的 UI 元素树（检验恢复文案）；
  - `metadata.txt`：PID 与重生状态元数据。
