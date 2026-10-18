---
task_id: P20-CLOSE-BOUND-1
author: Antigravity
recipient: Codex
base_commit: 8bf3ae30a
delivery_head: bae81ad29
status: in_review
---

# Handoff：P20-CLOSE-BOUND-1（R3 闭环返修）

## 交付结果

本 Task 在用户明确授权突破 DIR-4 进行第 3 轮返修的背景下，针对 Codex Review R2（`verification/P20-CLOSE-BOUND-1/codex-review-r2.md`）指出的 6 项未闭合缺陷（P1#2, P1#3, P2#4, P2#5, P2#6, P2#7），完成了全部缺陷的彻底闭环、闭式推导与测试验证（P1#1 由 Coordinator 修复并保持通过）：

1. **P1#2 锁超时不放弃回收**：
   - `StdioLibraryChannel` 保存确定性的 `child_id: u32`。若 `child` 锁获取超时（因普通锁竞争），关闭流程**绝不跳过回收**，而是直接通过 OS 层执行进程终止：`taskkill /F /PID {child_id}`，并调度后台 fallback 线程在锁释放后调用 `child.wait()` 回收句柄，标记 `child_killed: AtomicBool`。
   - `pending_responses` 锁超时同样调度后台 fallback 线程在锁释放后执行 drain 并唤醒等待者。
   - 新增覆盖普通锁竞争超时的单元测试：`child_lock_contention_timeout_fallback_kills_child_and_prevents_orphan` 与 `pending_lock_contention_timeout_fallback_drains_and_unblocks`，均 100% 通过。

2. **P1#3 ≤3000ms 闭式证明与轮询超调消除**：
   - 引入**单一共享绝对 `deadline`**（`deadline = Instant::now() + min(timeout, 2400ms)`），全链路所有子阶段（锁、写入、优雅等待、reap、join 守护）超时均取自身静态上限与 `remaining` 的最小值。
   - 所有轮询步长使用 `sleep_dur = poll.min(remaining)`，当 `remaining` 为 0 时直接退出，彻底消除轮询累加超调。
   - 13 项细分推导静态 WCET 为 **2120 ms $\le 3000$ ms**（具备 880 ms 确定性安全裕度），动态物理执行上限为 **2400 ms**。
   - `concurrency-lock-audit.md` 明确区分“已证明硬上界”与“实测观测值”。

3. **P2#4 叠加测试时序有效性与真实关闭入口测量**：
   - `StdioLibraryChannel` 引入 `in_flight_awaiting_response: AtomicUsize`。仅在 stdin 写入完成、通过 RAII guard 真正进入响应接收等待时递增该计数。
   - 叠加测试改为等待 `resilient.in_flight_awaiting_response() > 0`，确凿验证管道写已完成且正阻塞于响应接收后再 taskkill。
   - 测量改为针对真实的生产关闭入口 `resilient.shutdown(Duration::from_millis(2400))`，实测耗时 **0.5072 ms (507.2 µs)**，修复 metadata 毫秒精度截断。

4. **P2#5 递归 PID 树核验与残留强制失败**：
   - 脚本以 BFS 队列从当前 runner PID 递归检索所有后代 PID 集合；修复单/双反斜杠路径转义匹配。
   - 增加隔离根句柄真实释放检测：测试完成后执行 `Remove-Item -Recurse -Force $isolatedRoot`，若被句柄锁定无法删除则计入残留。
   - 脚本在 `$residualCount > 0` 或任一测试失败时**强制 `exit 1`**。

5. **P2#6 writer 超时与管道满载（> pipe capacity）故障注入**：
   - 新增专用测试 `writer_overflow_pipe_capacity_unblocks_and_cleans_up_on_kill`：向不读 stdin 的子进程注入 2MB 数据。
   - 证明：调用方在 ~100 ms 内超时返回，不被 OS pipe write 阻塞；强杀子进程后 Windows 内核自动破裂读端，writer 线程收到 `BrokenPipe` 并干净退出；writer/reader join guard 成功释放，零孤儿（实测 1.27s 通过）。

6. **P2#7 消除静默吞掉 kill 失败**：
   - `wait_timeout_or_kill` 中检查 `child.kill()` 返回值，若报错且进程尚未退出，打印明确错误日志；若 reap 超时返回带有 PID 的 `Err(TimedOut)`。
   - `shutdown_and_kill` 中捕获错误并记录至 `last_shutdown_error`，同时触发 OS 级直接强杀（taskkill /F /PID）兜底。

---

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测代码 | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1：有界关闭（核心叠加场景） | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_drop_after_external_kill -- --nocapture` | Windows 11 (pwsh 7.6.6), Python 3.14.6 | PASS | `verification/P20-CLOSE-BOUND-1/ac1-overlay-bound.stdout.log` (真实入口实测 0.5072 ms < 上界 3.0s) |
| AC2：递归树零残留与句柄释放 | 递归后代 PID 树、隔离根删除与 Python 进程审计 | 同上 | PASS | `verification/P20-CLOSE-BOUND-1/ac2-process-tree-audit.log` (0 残留进程，隔离根句柄完全释放) |
| AC3：不回归（resilient channel） | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel` | 同上 | PASS (9 passed) | `verification/P20-CLOSE-BOUND-1/ac3-resilient-channel.stdout.log` |
| AC3：不回归（stdio channel drop） | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop stdio_channel_drop` | 同上 | PASS (1 passed) | `verification/P20-CLOSE-BOUND-1/ac3-stdio-channel-drop.stdout.log` |
| AC4：并发审查与硬上界闭式推导 | `concurrency-lock-audit.md` + 4 项 hard-bound 单元测试（含普通锁竞争超时 fallback、管道满载故障注入、中毒锁恢复） | 同上 | PASS (4 passed) | `verification/P20-CLOSE-BOUND-1/concurrency-lock-audit.md`, `ac4-child-lock-contention.stdout.log`, `ac4-writer-pipe-overflow.stdout.log` |
| AC5：真实桌面窗口关闭场景 | `pwsh -NoProfile -File verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1` | 已由 Coordinator 于 11:55 在交互式桌面复跑通过（76.54 ms 退出，0 残留） | PASS（Coordinator 独立复跑） | `verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1` |
| AC6：证据落盘与治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-CLOSE-BOUND-1.md` | 同上 | PASS (2 warnings，预算预警) | 完整验证产物落盘 `verification/P20-CLOSE-BOUND-1/` |

---

## 接收方式与复核指令

1. 工作区位于 `G:\CODEX\New Manga`，代码与证据均已就绪（未执行 git commit，等待 Coordinator 提交）。
2. 复现与回归测试命令：
   - 运行完整验证套件：`pwsh -NoProfile -File verification/P20-CLOSE-BOUND-1/test-ac1-overlay-bound.ps1`
   - 运行治理检查：`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-CLOSE-BOUND-1.md`
3. 推荐下一步：
   - **推荐 Agent**：Codex（Reviewer / Integrator）
   - **可直接转发给 Codex 的指令**：
     ```
     请对 P20-CLOSE-BOUND-1 执行独立复审 R3：
     1. 检查 apps/desktop/src-tauri/src/library_bridge.rs 中共享绝对 deadline（deadline = Instant::now() + total_budget）、普通锁竞争超时 fallback、in_flight_awaiting_response 握手、管道满载 BrokenPipe 解除与 kill 错误上报；
     2. 检查 verification/P20-CLOSE-BOUND-1/concurrency-lock-audit.md 的 13 项 WCET 闭式推导表（静态 2120 ms <= 3000 ms，动态 2400 ms）；
     3. 运行 pwsh -NoProfile -File verification/P20-CLOSE-BOUND-1/test-ac1-overlay-bound.ps1 验证全部 10 项测试与递归 PID 树 0 残留；
     4. 由 Coordinator 执行 git commit，收口 Task 并推进到 done。
     ```
