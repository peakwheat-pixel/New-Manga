---
task_id: P20-ISOLATION-1
author: Antigravity
recipient: Codex
base_commit: dbeca3bab
delivery_head: eb62dbc7f
status: review
---

# Handoff：P20-ISOLATION-1

## 交付结果

针对 P20 的 AC6 实测缺口（强杀 `core_service` 后主窗口未白屏崩溃，但 UI 无异常提示且 8s 内 sidecar 未自动重生），Antigravity 已完成核心自愈机制与前端提示的实现：

1. **Rust 侧（Tauri Host Bridge）**：
   - 文件：`apps/desktop/src-tauri/src/library_bridge.rs`
     - 为 `StdioLibraryChannel` 添加 reader 线程 EOF 与读取异常的即时回调 `on_down`，实现毫秒级故障感知；
     - 实现自愈包装器 `ResilientLibraryChannel`（实现 `LibraryChannel` trait）：
       - 内置 `MAX_RETRIES = 3` 连续失败上限；
       - 指数退避策略：初始 500ms，按 500ms -> 1000ms -> 2000ms 退避，避免无限重启风暴；
       - 1.5s 后台轻量心跳探测线程，补充挂起超时回收；
       - 通过 `StatusEmitter` 广播生命周期状态：`restarting`（"后端服务异常，正在尝试热重启..."）、`recovered`（"后端服务已恢复正常"）、`fatal`（"后端服务异常，自动重启失败，请检查服务日志"）；
       - 编写并通过两个 Rust 单元测试：`resilient_channel_triggers_restart_and_emits_restarting_status` 与 `resilient_channel_caps_retries_and_emits_fatal_after_three_failures`。
   - 文件：`apps/desktop/src-tauri/src/main.rs`
     - 在桌面启动时将初始 channel 包装为 `ResilientLibraryChannel`，启动心跳，并通过 Tauri 事件发射器向前端广播 `core:lifecycle_status`。

2. **前端侧（React + TypeScript）**：
   - 文件：`apps/desktop/frontend/src/events.ts`
     - 隔离定义 `LIFECYCLE_STATUS_EVENT = "core:lifecycle_status"` 与 `onLifecycleStatusChanged`（保持原有 6 个领域事件常量不变，不破坏契约）。
   - 文件：`apps/desktop/frontend/src/shell/AppShell.tsx`
     - 监听 `core:lifecycle_status`，维护 `coreStatus`；
     - 增加 2.0s 前端主动心跳探测（`core_ping` 失败时置为 `restarting`，双重保险）；
     - 页面顶部渲染全局提示横幅 `core-status-banner`：
       - `restarting`：黄色警告，文案精确匹配 `"后端服务异常，正在尝试热重启..."`；
       - `fatal`：红色错误，文案 `"后端服务异常，自动重启失败，请检查服务日志"`，附带手动重试按钮；
       - `recovered`：绿色提示，文案 `"后端服务已恢复正常"`，2.5s 后自动淡出；
     - 四个一级页面容器采用 Keep-Alive 保全模式，不卸载未提交表单与输入状态。
   - 文件：`apps/desktop/frontend/src/shell/AppShell.lifecycle.test.tsx` (新增)
     - 包含 AC1、AC2、AC3 的完整组件级与状态保全集成测试，全部通过。

3. **测试与回归**：
   - 前端全量测试：`npm test` 288 个测试全部 PASS；
   - 前端构建：`npm run build` PASS；
   - 二进制 SHA-256：`core_service.exe` SHA-256 完全一致（`CD8DCC5E6DE568690694125D68162784C6A8427E6758C228080396B9599C98F1`）。

---

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1: 用户可见故障提示 | `npm test -- src/shell/AppShell.lifecycle.test.tsx` | Node.js (Vitest) | PASS | `apps/desktop/frontend/src/shell/AppShell.lifecycle.test.tsx` |
| AC2: 心跳与自愈包装器 | `cargo test --bin m2rc1-desktop resilient_channel --manifest-path apps/desktop/src-tauri/Cargo.toml` | Rust 1.82 (Windows) | PASS | `apps/desktop/src-tauri/src/library_bridge.rs` |
| AC3: 状态保全验证 | `npm test -- src/shell/AppShell.lifecycle.test.tsx` (未提交草稿在崩溃自愈后不丢失且可提交) | Node.js (Vitest) | PASS | `apps/desktop/frontend/src/shell/AppShell.lifecycle.test.tsx` |
| AC4: 前端全量回归 | `npm test` (29 files, 288 tests) | Node.js | PASS | 控制台输出 288 passed |
| AC4: 前端构建回归 | `npm run build` | Vite / TSC | PASS | `apps/desktop/frontend/dist` |
| AC4: Rust 编译回归 | `cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` | Cargo | PASS | 零报错 |
| AC4: SHA-256 一致性 | PowerShell Get-FileHash 对比 `target/core-sidecar` 与 `target/debug/resources` | Windows pwsh | PASS | 均为 `CD8DCC5E6DE568690694125D68162784C6A8427E6758C228080396B9599C98F1` |
| AC1 & AC2: 交互式端到端 UI 注入与自愈复测 | `pwsh -NoProfile -File verification/P20-ISOLATION-1/run-ac6-ui-verification.ps1` | Windows 交互式桌面 | 待 Coordinator 复核 | 脚本已固化在 `verification/P20-ISOLATION-1/run-ac6-ui-verification.ps1` |

> [!NOTE]
> **沙箱限制说明**：当前执行会话为无窗口沙箱环境，创建 WebView2 报错 `HRESULT 0x80070578: 无效的窗口句柄`。因此真实桌面端到端 UIAutomation 验证（`run-ac6-ui-verification.ps1`）需由 Coordinator 在有交互式桌面会话的环境复跑。

---

## 接收方式

- **工作区**：`G:\CODEX\New Manga`
- **分支/Commit**：`main` / `eb62dbc7f`
- **端到端复现命令**（在真实交互式桌面环境下）：
  ```powershell
  pwsh -NoProfile -ExecutionPolicy Bypass -File "G:\CODEX\New Manga\verification\P20-ISOLATION-1\run-ac6-ui-verification.ps1"
  ```

---

## 下一任务建议（必填）

- **Task ID / 标题**：`P20-ISOLATION-1` 独立复核与集成闭环
- **推荐 Agent / Reviewer**：Codex (Reviewer) / Coordinator
- **推荐原因与前置依赖**：Antigravity 已完成代码实现、Rust 单元测试、前端全量测试与状态保全测试。因沙箱无交互式窗口句柄，需由拥有真实桌面的 Coordinator/Codex 执行一次 `run-ac6-ui-verification.ps1` 并核验生成的 `trace.log` 与 `ui-after-kill.txt`，确认 UIA 成功捕获异常横幅文案及 sidecar 自动重生后即可完成 Task Closeout。
- **Recovery point**：`G:\CODEX\New Manga`，`main` 分支。
- **允许修改路径**：`verification/P20-ISOLATION-1/**`、`doc/tasks/P20-ISOLATION-1.md`、`doc/STATUS.md`。
- **禁止范围与新增授权条件**：不得修改既有 43 项未提交改动；测试须使用 `%TEMP%` 隔离根。
- **交付物**：`verification/P20-ISOLATION-1/run-<timestamp>/` 下的 UIA 证据与 Closeout 记录。
- **验证命令、环境与完成 Gate**：
  ```powershell
  pwsh -NoProfile -ExecutionPolicy Bypass -File "G:\CODEX\New Manga\verification\P20-ISOLATION-1\run-ac6-ui-verification.ps1"
  ```
- **可直接转发给 Agent 的指令**：
  > 请在真实桌面环境中运行 `pwsh -NoProfile -ExecutionPolicy Bypass -File "G:\CODEX\New Manga\verification\P20-ISOLATION-1\run-ac6-ui-verification.ps1"` 复核 P20-ISOLATION-1 的端到端自愈与 UI 横幅提示，核实 `trace.log` 中 `ac6:user-visible-error-indicated` 与 `ac6:sidecar-auto-respawned` 均为 PASS 后，推进 P20-ISOLATION-1 关闭。

---

## 风险与遗留

1. **冷启动与稳态强杀时机**：若在应用启动极早期（初始化 ping 尚未通过前）直接强杀 sidecar，Tauri 主进程会在 startup ping 报错退出。本方案在稳态（就绪后）对 sidecar 强杀具备毫秒级感知与自愈能力；交互式测试请确保等待 6s 稳态后再注入崩溃。
2. **无限重启防范**：已硬编码最多连续尝试 3 次并按 500ms、1000ms、2000ms 指数退避，第 3 次失败后进入 fatal 状态，UI 提供手动重试按钮，彻底避免无上限重启风暴。
