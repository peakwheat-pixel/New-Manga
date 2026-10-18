# P20-CLOSE-BOUND-1 P1#1 回归修复证据包

- Owner: Antigravity
- 日期: 2026-10-18
- 针对问题: Codex Review R2 提出的 P1#1（正常关闭时协议级优雅关闭消息被永久拒绝）
- 修复范围: 仅限 `apps/desktop/src-tauri/src/library_bridge.rs` 中与关闭专用写入路径相关的最小改动 + 配套测试。

## 1. 根本原因与问题分析

在 `library_bridge.rs` 的原实现中：
- `shutdown_and_kill` 在入口处首先执行 `self.is_down.store(true, Ordering::SeqCst)`。
- 随后调用的 `write_stdin_timeout` 与 `exchange_expected_minor_timeout` 在入口处均检查 `if self.is_down.load(...) { return Err(...); }`。
- 导致无论是第 2 步的 `CloseHostSession` 还是第 3 步的 `core.shutdown`，都会在发起写入前直接被短路拒绝。
- 导致正常的桌面关闭流程无法向 Core sidecar 发送任何协议级关闭消息，最终只能依赖超时强杀。

## 2. 修复方案

1. **保留对外请求的拒绝语义**：
   - 普通对外 IPC 请求调用的 `write_stdin_timeout` 以及通过 `exchange_expected_minor_timeout` 发起的普通请求，在 `is_down` 为 true 时依然立即拒绝，返回 `Channel is shutting down` / `Core stdout closed (EOF)`，防止关闭过程中前端继续压入业务请求。
2. **设立底层定向写入与关闭专用入口**：
   - 提取出私有底包写入辅助函数 `write_stdin_raw_timeout`，直接与 writer 线程通信。
   - 对外接口 `write_stdin_timeout` 保持 `is_down` 校验后调用 `write_stdin_raw_timeout`。
   - 另设 `write_stdin_shutdown` 作为关闭专用定向写入口，不进行 `is_down` 拦截，供内部关闭流程使用。
3. **定向关闭 Exchange 路径**：
   - 增设 `exchange_shutdown_timeout`，内部调用 `exchange_expected_minor_timeout_internal(..., allow_during_shutdown = true)`。
   - 允许 `CloseHostSession` 在 `is_down == true` 的状态下顺利获取 transaction 锁、排入 pending、通过 `write_stdin_shutdown` 写出管道并等待响应（上限 250ms）。
4. **严格保持既有超时与有界预算不变**：
   - 预算保持 1500/1000/1200/500/150ms 与 writer 线程结构不变。

## 3. 配套自动化测试

在 `apps/desktop/src-tauri/src/library_bridge.rs` 中新增两个自动化端到端协议写入验证测试：

1. `shutdown_writes_protocol_shutdown_messages_with_session_to_sidecar_stdin`:
   - 启动一个采用 Python 编写的真实观测子进程（使用 `-u` 无缓冲模式），该子进程记录其标准输入收到的所有字节，并在收到 `CloseHostSession` 时通过标准输出回送合法协议响应，在收到 `core.shutdown` 时退出。
   - 在 channel 中激活 `HostSession` 并执行 `shutdown_and_kill`。
   - **严格断言**：
     - 子进程记录文件中确实收到了 `CloseHostSession` 协议消息，校验 protocol 为 `new-manga.core`，command 为 `CloseHostSession`，`host_session_id` 正确对应。
     - 子进程记录文件中确实收到了 `core.shutdown` 协议消息，校验 protocol 为 `new-manga.core`，command 为 `core.shutdown`，`request_id` 为 `shutdown-drop`。
     - 外部请求（如 `write_stdin_timeout` 和 `round_trip`）在关闭后均被拒绝，错误信息包含 `Channel is shutting down`。
     - 目标子进程 PID 顺利终止（tasklist 查无残留）。
2. `shutdown_writes_core_shutdown_to_sidecar_stdin_without_session`:
   - 验证无活跃 HostSession 时的关闭流程。
   - 严格断言子进程记录文件中恰好收到 1 条 `core.shutdown` 消息，并且正常外部写入被拒绝、进程干净退出。

## 4. 证据清单

| 文件名 | 内容说明 | Exit Code |
|---|---|---|
| `p1-1-shutdown-writes.stdout.log` | 新增写入测试执行日志（2 passed: 0.35s） | 0 |
| `p1-1-shutdown-writes.stderr.log` | 错误输出（空） | - |
| `p1-1-shutdown-writes.meta.json` | 执行元数据（耗时、环境、Python、命令） | 0 |
| `p1-1-resilient-channel.stdout.log` | Resilient channel 回归测试（9 passed: 0.35s） | 0 |
| `p1-1-resilient-channel.meta.json` | 回归测试元数据 | 0 |
| `p1-1-stdio-drop.stdout.log` | Stdio drop 回归测试（1 passed: 0.32s） | 0 |
| `p1-1-stdio-drop.meta.json` | Stdio drop 测试元数据 | 0 |
| `p1-1-governance.stdout.log` | 治理检查 PASS | 0 |
| `p1-1-governance.meta.json` | 治理检查元数据 | 0 |
| `verify-p1-1.ps1` | 一键自动化验证脚本 | 0 |
