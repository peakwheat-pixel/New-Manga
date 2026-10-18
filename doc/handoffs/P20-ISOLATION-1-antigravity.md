---
task_id: P20-ISOLATION-1
author: Antigravity
recipient: Codex
base_commit: dbeca3bab
delivery_head: 796613ef4
status: review
---

# Handoff：P20-ISOLATION-1（Codex Review R2 返修交付）

## 1. 交付背景与返修项说明

针对 Codex 在 `verification/P20-ISOLATION-1/codex-review-r2.md` 中确认的结论：
- 前序 R-001/R-002/R-003/R-006 已确认修复闭环；
- Coordinator 侧已修复 R-004/R-005/R-007/R-011/R-012/R-013；
- 本次针对 Codex 新提出的 3 项 P1（R-008、R-009、R-010）及 1 项 P2（R-014）在严格授权范围内完成返修、代码实现与自动化验证：

### R-008（P1，存活但 IPC 无响应不会被发现）
- **修改位置**：`apps/desktop/src-tauri/src/library_bridge.rs`
- **问题根因**：原心跳仅依赖 `chan.is_down` 和 `child.try_wait()`。当进程存活但不处理 IPC（死锁/挂起/断管道）时，`try_wait()` 始终返回运行中，导致永远无法触发重启自愈。
- **方案策略**：
  1. 心跳增加**请求级超时探测**机制：当子进程存活时，心跳循环通过 `chan.ping_timeout(heartbeat_ping_timeout)` 向 sidecar 发送 `core.ping` 探测。
  2. 探测超时参数：生产默认心跳巡检间隔 `heartbeat_interval = 1500ms`，探测超时 `heartbeat_ping_timeout = 2000ms`。
  3. AC1/AC2 有界时间对齐：最差情况下（刚巡检完即发生挂起），下一次巡检开始（1.5s）+ ping 超时判定（2.0s）= **3.5s ≤ 5.0s**，严格符合 AC1 与 AC2「有界时间内（≤5s）提示并恢复」的指标要求。
  4. 事务锁有界等待：`acquire_transaction_lock(timeout)` 支持超时轮询，若在途请求挂起，心跳不会无限阻塞在锁上，而是及时判定超时并触发重启。
  5. 探测超时后，立即判定 no-response 并调用 `ctx.trigger_restart()`，进入相同的退避自愈状态机（发射 `restarting` 状态，回收旧挂起进程，按预算重生或 fatal）。
- **单元测试**：
  - `resilient_channel_heartbeat_detects_unresponsive_child_and_recovers`（PASS：真实 `cmd /c pause` 进程存活但不响应 ping，心跳超时判定并在有界时间内成功自愈至 `recovered`，旧挂起进程被回收）。
  - `resilient_channel_heartbeat_unresponsive_child_caps_retries_and_reaches_fatal`（PASS：持续不响应场景下，心跳重试严格消耗预算，达 3 次上限后进入 `fatal`，不再无限重试）。

### R-009（P1，Drop / 关闭可能无限等待）
- **修改位置**：`apps/desktop/src-tauri/src/library_bridge.rs`
- **问题根因**：
  1. `with_channel` 在整个 IPC 请求期间一直持有 `ctx.inner` 互斥锁，挂起请求导致外部无法拿锁执行 `drop` 或自愈回收；
  2. `StdioLibraryChannel::drop` 在关闭时调用无超时的 `CloseHostSession` round-trip，挂起进程导致永远卡在 `rx.recv()`，无法执行到 5 秒 kill 逻辑。
- **方案策略**：
  1. 解耦 `with_channel` 锁范围：`inner` 结构改用 `Mutex<Option<Arc<StdioLibraryChannel>>>`，`with_channel` 仅短暂获取锁克隆 `Arc` 指针后**立即释放 `inner` 锁**，调用 IPC 期间不再占用 `inner` 互斥体；
  2. `StdioLibraryChannel` 提供有界回收方法 `shutdown_and_kill(kill_timeout)`：
     - 原子设置 `is_down = true`；
     - 立即排干并失败所有等待响应的信道（`pending_responses.drain()` 发送 Err），使在途挂起线程立即退出解脱；
     - 非阻塞尝试关闭 host session（`host_session.try_lock()` + 500ms 严格超时），若锁被占用或超时则直接跳过，绝不卡死；
     - 非阻塞尝试向 stdin 写入 `core.shutdown`；
     - 执行 `wait_timeout_or_kill(&mut child, kill_timeout)`，超时强制杀死子进程；
     - Join 并回收 reader 线程；
  3. `ResilientLibraryChannel::drop` 调用 `chan.shutdown_and_kill(Duration::from_millis(1500))`，确保关闭在有界时间内完成，杜绝残留进程。
- **单元测试**：
  - `resilient_channel_drop_with_in_flight_unresponsive_call_terminates_in_bounded_time`（PASS：挂起请求在途时执行 drop，3 秒内完成关闭，在途线程安全退出，`tasklist` 验证无残留子进程）。
  - `stdio_channel_drop_with_unresponsive_session_completes_in_bounded_time`（PASS：活跃 host session 且进程挂起时，drop 在 3 秒内完成且子进程被清理）。

### R-010（P1，AC3 真实注入脚本与验证层级明确）
- **修改位置**：`verification/P20-ISOLATION-1/run-r010-ac3-real-injection.ps1`、`apps/desktop/frontend/src/shell/AppShell.lifecycle.test.tsx`
- **方案策略**：
  1. **明确界限区分**：
     - **组件级已证**：`AppShell.lifecycle.test.tsx`（已通过前端测试套件验证：验证 React 组件 Keep-Alive 容器、新建作品对话框、表单草稿输入在生命周期事件广播下不被重置，恢复后可正常提交，断言覆盖完整）。
     - **真实注入待 Coordinator 复跑**：编写完整可判定的自动化脚本 `run-r010-ac3-real-injection.ps1`，供拥有交互式桌面的 Coordinator 执行端到端真实注入验收。
  2. **端到端脚本执行链路**：
     - 启动桌面真实程序 `m2rc1-desktop.exe`（使用 `%TEMP%` 隔离根）；
     - UIA 等待主窗口就绪并点击「+ 新建作品」按钮打开对话框；
     - 向草稿输入框键入测试标题 `Real Injection Draft Manga <timestamp>`；
     - 故障注入：`Stop-Process -Force` 真实强杀 `core_service.exe`；
     - 断言故障态：黄色异常横幅出现，新建作品对话框依然开启，输入框内的草稿文本未丢失，截取截图 `01-draft-preserved-during-crash.png`；
     - 等待自愈：sidecar 自动重生为新 PID，恢复横幅出现，对话框与草稿文本依然完好保留，截取截图 `02-draft-preserved-after-recovery.png`；
     - 提交草稿：点击对话框中的「创建作品」提交按钮；
     - 断言草稿落盘：书架列表中成功出现该标题作品，截取截图 `03-draft-submitted-successfully.png`；
     - 脚本输出标准 `ASSERT PASS/FAIL` 行，进程全部安全回收，失败时非零退出。

### R-014（P2，AC2 说明与实现细节参数对齐）
- **修改位置**：`doc/tasks/P20-ISOLATION-1.md`（AC2/AC3 描述、风险与记录部分，未触碰 Canonical Evidence 表）及本 Handoff。
- **对齐参数**：
  - 心跳巡检周期：`1500ms`；
  - 心跳探测超时：`2000ms`；
  - 故障感知上限：`3.5s ≤ 5.0s`；
  - 快速崩溃冷却期（稳定存活窗口）：`30s`；
  - 连续失败最大重试次数：`3 次`；
  - 指数退避序列：`500ms -> 1000ms -> 2000ms`；
  - 强制回收上限：`ResilientChannel::drop` / 重启自愈阶段 `1500ms`，`StdioChannel::drop` `5000ms`。

---

## 2. 自动化验证证据与测试记录

测试输出与元数据已完整落盘于 `verification/P20-ISOLATION-1/r2-fix/`：

| 测试套件 | 测试命令 | 退出码 | 结果 | 关键断言覆盖 |
|---|---|---|---|---|
| Rust 自愈与生命周期 (全量) | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel` | `0` | 8 passed; 0 failed | R-001 预算上限、R-002 启动自愈、R-003 弱引用环、R-008 存活无响应心跳探测恢复、R-008 持续无响应退避至 fatal、R-009 在途请求有界关闭且无残留进程 |
| Rust 底层 Channel 有界 Drop | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop stdio_channel_drop` | `0` | 1 passed; 0 failed | R-009 活跃 session 且进程挂起时 drop 在 3s 内完成且子进程被 reap |
| 前端生命周期与保全 | `npm test -- AppShell.lifecycle.test.tsx` (in `apps/desktop/frontend`) | `0` | 3 passed; 0 failed | AC1 异常横幅、AC2 恢复/致命态提示与重试按钮移除（R-006）、AC3 草稿跨故障与恢复保全并可提交 |
| 项目治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-ISOLATION-1.md` | `0` | 仅待 Coordinator 登记新 Evidence PIN |

落盘文件列表：
- `verification/P20-ISOLATION-1/r2-fix/rust-r2-tests.log`
- `verification/P20-ISOLATION-1/r2-fix/rust-r2-tests.exit` (内容: 0)
- `verification/P20-ISOLATION-1/r2-fix/rust-r2-tests.meta.json`
- `verification/P20-ISOLATION-1/r2-fix/frontend-r2-tests.log`
- `verification/P20-ISOLATION-1/r2-fix/frontend-r2-tests.exit` (内容: 0)
- `verification/P20-ISOLATION-1/r2-fix/frontend-r2-tests.meta.json`
- `verification/P20-ISOLATION-1/run-r010-ac3-real-injection.ps1`

---

## 3. 证据界限说明（能证明 vs 不能证明）

- **能证明的事项**：
  1. **R-008（存活无响应探测）**：单元测试明确断言存活但挂起的子进程（`cmd /c pause`）在心跳探测超时（`ping_timeout`）后被正确识别，立即发射 `restarting` 状态，强制回收旧挂起进程并成功恢复；若持续无响应，重试预算严格受限并终止于 `fatal`。
  2. **R-009（有界关闭与在途解脱）**：在途 IPC 请求挂起时，channel drop 能在 < 3 秒内安全退出，在途线程立即获得错误返回，挂起子进程被强制终止并在 `tasklist` 中确认无残留。
  3. **R-010（组件级草稿保全）**：在 Vitest/jsdom 环境下，新建作品对话框的标题输入在经历 `restarting` 故障广播与 `recovered` 恢复广播期间完全不丢失，恢复后提交成功调用 IPC。
  4. **代码无锁死与回归**：所有 9 项 Rust 渠道测试与 3 项前端生命周期测试全部 PASS，执行时间均在秒级以内。
- **不能证明的事项**：
  1. 当前无交互式桌面的 headless 沙箱环境无法创建真实 WebView2 窗口（报错 `0x80070578: 无效的窗口句柄`），因此本 Agent **不得也不声称**端到端真实桌面 UI 断言通过。
  2. 真实桌面下的 AC3 真实强杀草稿保全验证需要由 Coordinator / Reviewer 在交互式桌面执行 `run-r010-ac3-real-injection.ps1` 进行闭环验收。

---

## 4. 未完成项与下一步操作建议

- **未完成项**：
  1. `apps/desktop/src-tauri/src/library_bridge.rs` 的工作区 SHA-256 已随本次修复变更，按硬约束 Antigravity 未动 `doc/tasks/P20-ISOLATION-1.md` 的 Canonical Evidence 表，待 Coordinator 统一更新 PIN。
  2. 端到端真实桌面验收脚本 `run-r010-ac3-real-injection.ps1` 待 Coordinator 在交互式桌面执行。
- **建议下一步**：
  由拥有交互式桌面权限的 **Coordinator / Codex** 在真实桌面执行 AC3 注入脚本与 AC1/AC2 timeline 脚本并更新 Evidence PIN：
  ```powershell
  # 1. 真实桌面 AC3 草稿保全端到端注入复跑
  pwsh -NoProfile -ExecutionPolicy Bypass -File "G:\CODEX\New Manga\verification\P20-ISOLATION-1\run-r010-ac3-real-injection.ps1"

  # 2. 真实桌面 AC1/AC2 故障横幅与自愈 timeline 复跑
  pwsh -NoProfile -ExecutionPolicy Bypass -File "G:\CODEX\New Manga\verification\P20-ISOLATION-1\run-r004-timeline.ps1"
  ```
  执行通过并更新 Task Canonical Evidence 表后，即可推进 Codex 第三轮复审（R3）或闭环本 Task。
