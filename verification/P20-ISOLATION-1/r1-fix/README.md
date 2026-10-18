# P20-ISOLATION-1 Codex Review R1 返修验证报告

## 1. 概览与返修项说明

针对 Codex 对 Task「P20-ISOLATION-1」head `13da2211a` 独立复核（`verification/P20-ISOLATION-1/codex-review-r1.md`）提出的 4 项代码缺陷（R-001、R-002、R-003、R-006），在严格限定的授权路径内（Tauri/前端的 sidecar 生命周期、心跳、错误呈现、状态保活）完成了针对性返修与单元测试覆盖。

### R-001（P1，无限重启漏洞与总体重启上限）
- **修改位置**：`apps/desktop/src-tauri/src/library_bridge.rs`
- **问题根因**：重生"成功"后立即将 `consecutive_failures` 清零。若 sidecar 启动后很快退出，下一次故障会重置计数并从零再试三次，在短时间反复崩溃时形成无限重启风暴，且心跳限流也被绕过。
- **选择策略与参数**：
  - **重启预算与稳定存活冷却期机制（Crash Loop Budget with Cooldown Window）**：
    - `MAX_RETRIES = 3`：有界重试总预算维持 3 次。
    - `INITIAL_BACKOFF = 500ms`：指数退避序列保持 500ms -> 1000ms -> 2000ms。
    - `STABLE_DURATION = 30s`（30 秒稳定存活窗口）：记录进程成功启动时间戳 `last_spawn_time`。
  - **算法逻辑**：
    1. sidecar 启动成功后，**不立即重置**失败计数 `consecutive_failures`，而是保留当前已消耗的 attempt 预算，并记录 `last_spawn_time = Some(Instant::now())`。
    2. 只有当 sidecar 在后续运行中**稳定存活超过 30 秒**，在心跳巡检或下一次故障感知检查时，才将 `consecutive_failures` 重置为 0，补齐预算。
    3. 若 sidecar 在 30 秒内迅速崩溃（短命进程），`last_spawn_time.elapsed() < 30s`，预算**不予补齐**，继续累加失败计数。
    4. 累计达到 3 次后，置位 `is_fatal = true`，派发 `fatal` 状态通知，终止重试并不再创建恢复线程；心跳与 `with_channel` 均检查 `is_fatal`，不再重复派发重启。
- **测试覆盖**：新增单元测试 `resilient_channel_crash_loop_is_bounded_and_reaches_fatal`，模拟真实子进程快速退出（EOF）循环，断言在 3 次内进入 fatal，总 spawn 次数严格为 3，不再无限重启。

### R-002（P1，启动早期无保护）
- **修改位置**：`apps/desktop/src-tauri/src/main.rs`、`apps/desktop/src-tauri/src/library_bridge.rs`
- **问题根因**：`main.rs` 在启动早期同步等待 `spawn_with_startup_ping` 与 `open_host_session`，使用 `.expect(...)`；若 sidecar 启动失败或超时，直接 panic 终止宿主进程，监督器未能覆盖初始化阶段。
- **解决方案**：
  1. 移除 `main.rs` 中的 `.expect(...)` panic 调用，捕获初始启动异常。
  2. 若初始启动失败，打印警告日志，构造 `ResilientLibraryChannel::new(config, None)`，记录初始失败次数为 1。
  3. `LibraryChannel` trait 增加 `trigger_restart(&self)` 与 `is_unhealthy(&self) -> bool` 契约。
  4. 在 Tauri `setup` 钩子中，当 WebView 事件总线的 `status_emitter` 绑定完毕后，检查 `library.is_unhealthy()`，若异常则立即触发 `trigger_restart()`，向前端派发 `restarting` 状态并由后台自愈线程进行有界重试。宿主进程不再退出。
- **测试覆盖**：新增单元测试 `resilient_channel_early_startup_failure_recovers_without_panic`，断言初始 channel 为 None 时 `is_unhealthy()` 为 true，ping 返回 `CORE_UNAVAILABLE` 而不 panic，触发恢复后成功自愈并派发状态。

### R-003（P1，关闭时强引用环与资源清理）
- **修改位置**：`apps/desktop/src-tauri/src/library_bridge.rs`
- **问题根因**：`ResilientCoreContext.inner` 持有 `StdioLibraryChannel`，其 `on_down` 回调闭包强引用捕获了 `Arc<ResilientCoreContext>`，形成 `context -> channel -> callback -> context` 强引用环。`ResilientLibraryChannel::drop` 只设置了 `heartbeat_stop`，未拆解引用环，导致 `StdioLibraryChannel::drop`（发送 shutdown、等待进程、join reader）永远不被执行，残留孤儿进程与线程。
- **解决方案**：
  1. **断开强引用**：`on_down` 回调闭包改用弱引用捕获 `Weak<ResilientCoreContext>`（`let ctx_weak = Arc::downgrade(&ctx)`），调用时通过 `upgrade()` 尝试提升，解除环状所有权。
  2. **显式 Drop 触发**：在 `ResilientLibraryChannel::drop` 实现中，除置位 `heartbeat_stop` 外，显式加锁取出并丢弃内部 channel：`self.ctx.inner.lock().unwrap().take().map(drop)`，确保在 channel 释放时立即触发 `StdioLibraryChannel::drop`。
  3. 在 `StdioLibraryChannel::drop` 中执行 `core.shutdown`、进程回收（`wait_timeout_or_kill`）与 reader 线程 join。
- **测试覆盖**：新增单元测试 `resilient_channel_shutdown_breaks_cycle_and_reaps_child_process`，挂载真实子进程，断言 `weak_ctx.strong_count() == 1`，drop 后强引用归 0（证明环拆除），并断言 OS 进程已被终止回收（tasklist 无残留）。

### R-006（P1，fatal 后手动重试无效与按钮移除）
- **修改位置**：`apps/desktop/frontend/src/shell/AppShell.tsx`、`apps/desktop/frontend/src/shell/AppShell.lifecycle.test.tsx`
- **处理选择**：**移除误导用户的“重试连接”按钮**。
- **理由**：
  1. 当系统进入 `fatal` 致命降级态时，说明监督器已完成 3 次带指数退避（累计 3.5s+）的自动重试，此时 sidecar 属于不可逆故障（如执行文件缺失、核心数据库损坏、系统环境不兼容）。
  2. 此时在前端放置“重试连接”按钮并再次触发 ping/restart，若不设防会导致无限重启漏洞重现；若设防则仅会重复派发 fatal，给用户造成“按钮失效”的误导性负反馈。
  3. 移除按钮后，横幅精准传达语义：“后端服务异常，自动重启失败，请检查服务日志”，引导用户查看控制台或日志文件，符合 AD-001 的故障收敛规范，且无需改动 Tauri 命令清单与 ACL 白名单。
- **测试覆盖**：更新前端 `AppShell.lifecycle.test.tsx`，断言进入 `fatal` 态时横幅渲染提示文案，且确认不再渲染 `button`。

---

## 2. 测试执行记录（原始输出与退出码）

### 1) Rust 自愈与生命周期测试套件（5 项全 PASS）
- **执行命令**：`cargo test --bin m2rc1-desktop resilient_channel -- --nocapture`
- **执行时间**：2026-10-18T08:19:54
- **退出码**：`0`
- **测试摘要**：
  - `library_bridge::tests::resilient_channel_triggers_restart_and_emits_restarting_status ... ok`
  - `library_bridge::tests::resilient_channel_caps_retries_and_emits_fatal_after_three_failures ... ok`
  - `library_bridge::tests::resilient_channel_early_startup_failure_recovers_without_panic ... ok`（R-002）
  - `library_bridge::tests::resilient_channel_crash_loop_is_bounded_and_reaches_fatal ... ok`（R-001）
  - `library_bridge::tests::resilient_channel_shutdown_breaks_cycle_and_reaps_child_process ... ok`（R-003）
- **落盘日志**：`verification/P20-ISOLATION-1/r1-fix/rust-resilient-channel-tests.log` 与 `.meta.json`

### 2) 前端生命周期与状态保全测试（3 项全 PASS）
- **执行命令**：`npm test -- AppShell.lifecycle.test.tsx`
- **执行时间**：2026-10-18T08:20:07
- **退出码**：`0`
- **测试摘要**：
  - AC1：UI 呈现明确后端异常状态横幅并匹配关键词（PASS）
  - AC2：重启成功后呈现恢复横幅，fatal 呈现致命降级提示且无重试按钮（PASS，R-006）
  - AC3：崩溃与重启期间未提交草稿输入保全（PASS）
- **落盘日志**：`verification/P20-ISOLATION-1/r1-fix/frontend-lifecycle-test.log` 与 `.meta.json`

### 3) 前端全量回归测试（29 文件 288 测试全 PASS）
- **执行命令**：`npm test`
- **退出码**：`0`
- **测试结果**：`Test Files 29 passed (29), Tests 288 passed (288)`

### 4) 项目治理检查
- **执行命令**：`pwsh -NoProfile -File tools/governance/check.ps1`
- **退出码**：`0`
- **输出**：`Governance check: PASS (2 warnings)`
