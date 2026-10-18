---
task_id: P20-CLOSE-BOUND-1
author: Antigravity
recipient: Codex
base_commit: 8bf3ae30a
delivery_head: fdf715e79
status: in_review
---

# Handoff：P20-CLOSE-BOUND-1（R4/R5 终审闭环）

## 交付结果

本 Task 在用户明确授权进行第 4 轮与第 5 轮返修的背景下，针对 Codex Review R3（`verification/P20-CLOSE-BOUND-1/codex-review-r3.md`）指出的 6 项未闭合缺陷（N1, P1#2, P1#3, P2#5, P2#6, P2#7）以及 1 项流程修正（`run-desktop-close-verification.ps1` 自包含落盘），完成了全部缺陷的彻底闭环、闭式推导与测试验证（P1#1 专属写入语义与既有心跳/拆环语义严格保持）：

1. **N1（P1）`ctx.inner` 锁超时不得静默跳过生产关闭**：
   - `ResilientLibraryChannel::shutdown` 在 `ctx.inner` 获取超时（50 ms）时记录 Warning 日志，派发后台专属 fallback 线程 `resilient-inner-shutdown-fallback`，待锁释放后接管并执行 `chan.shutdown_and_kill(1500ms)`，完成子进程与 OS 句柄回收并置位 `inner_fallback_shutdown_completed`；
   - 新增单元测试 `resilient_inner_lock_contention_timeout_triggers_fallback_shutdown`：模拟持有 `inner` 锁 200 ms，验证调用方在 ≤ 500 ms 内有界返回，且 fallback 线程接管后完成回收，子进程被彻底清除（实测 1.43s 通过，日志 `ac4-inner-lock-contention.stdout.log`）。

2. **P1#2 超时 fallback 提供“完成回收”保证与 `/T` 进程树强杀**：
   - 将 `child` 包装为 `Arc<Mutex<Child>>`。`child-reap-fallback` 线程在锁释放后调用 `child.wait()`，回收 OS 句柄并置位 `child_reaped = true`；
   - `pending-drain-fallback` 增加带重试循环机制，drain 后唤醒等待者并置位 `pending_drained = true`；
   - 所有 taskkill 调用均增加 `/T` 参数（`taskkill /F /T /PID`），确保强杀整棵进程树；
   - 改进单元测试 `child_lock_contention_timeout_fallback_kills_child_and_prevents_orphan`（实测 1.22s 通过）：启动 mock sidecar 并派生孙进程，验证主进程与孙进程均被 `/T` 强杀退出，真断言 `is_child_reaped() == true`；
   - 改进单元测试 `pending_lock_contention_timeout_fallback_drains_and_unblocks`（实测 1.73s 通过）：真断言 `is_pending_drained() == true`。

3. **P1#3 共享 deadline 覆盖全链路与消减无界点**：
   - 生产入口 `ResilientLibraryChannel::shutdown` 建立共享绝对 `deadline = Instant::now() + total_budget`，贯穿全链路；
   - 梳理 16 项阻塞点清单并消灭无界阻塞：实现 `run_taskkill_bounded`（上限 250 ms 受 remaining 截断），`last_shutdown_error` 加锁受限 10 ms，CloseHostSession 超时清理锁受限 10 ms；
   - 重构 WCET 推导表：Branch A 静态最坏情况 WCET 为 2350 ms $\le 3000$ ms（具备 650 ms 绝对硬裕度），Branch B 为 960 ms，动态物理执行上限为 2400 ms。

4. **P2#5 断链后代审计与基线差集扫描**：
   - `test-ac1-overlay-bound.ps1` 启动时记录全部系统进程基线快照 `$baselinePidSet`；
   - 测试结束后不仅执行 runner PID 的 BFS 递归子孙树，还评估全部新增 `$deltaProcs` 差集，按路径特征深度扫描断链孤儿；
   - 执行隔离根目录完全删除验证句柄释放；补齐标准环境头、退出码与元数据文件（实测 0 残留，隔离根成功删除，日志 `ac2-process-tree-audit.log`）。

5. **P2#6 满管道测试断言 writer/joiner/ChildStdin 释放**：
   - 引入原子标记 `writer_finished`、`writer_joined`、`reader_finished`、`reader_joined`；
   - writer 退出循环后显式 drop `ChildStdin` 并置位 `writer_finished = true`；
   - 在 2MB 满管道注入测试 `writer_overflow_pipe_capacity_unblocks_and_cleans_up_on_kill` 中增加真实断言 `is_writer_finished()`, `is_writer_joined()`, `is_reader_joined()`（实测 1.82s 通过，日志 `ac4-writer-pipe-overflow.stdout.log`）。

6. **P2#7 `taskkill` 结果检查与上报**：
   - `run_taskkill_bounded` 捕获 exit status 与 stdout/stderr，非零且非已退出状态时上报错误至 `last_shutdown_error`；
   - 仅在 taskkill 确认成功时才将 `child_killed` 标为 true。

7. **流程修正（Coordinator 要求）**：
   - 修正 `run-desktop-close-verification.ps1`，支持自动创建 `$OutDir`（默认 `ac5-<timestamp>` 或指定路径），自包含落盘 `ac5-console.log`、`ac5-metadata.txt`、`ac5-metadata.json` 与 `ac5.exit`，不再依赖外部调用方 `Tee`。

---

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测代码 | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1：有界关闭（核心叠加场景） | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_drop_after_external_kill -- --nocapture` | Windows 11 (pwsh 7.6.6), Python 3.14.6 | PASS | `verification/P20-CLOSE-BOUND-1/ac1-overlay-bound.stdout.log` (真实入口实测 0.5443 ms < 上界 3.0s) |
| AC2：递归树与断链后代零残留 | 基线差集 + 递归后代 PID 树、隔离根删除与进程特征审计 | 同上 | PASS | `verification/P20-CLOSE-BOUND-1/ac2-process-tree-audit.log` (0 残留进程，隔离根句柄完全释放) |
| AC3：不回归（resilient channel） | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel` | 同上 | PASS (9 passed) | `verification/P20-CLOSE-BOUND-1/ac3-resilient-channel.stdout.log` |
| AC3：不回归（stdio channel drop） | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop stdio_channel_drop` | 同上 | PASS (1 passed) | `verification/P20-CLOSE-BOUND-1/ac3-stdio-channel-drop.stdout.log` |
| AC4：并发审查与硬上界闭式推导 | `concurrency-lock-audit.md` + 5 项 hard-bound 单元测试（含 inner 锁超时 fallback、普通 child/pending 锁竞争 fallback、管道满载故障注入、中毒锁恢复） | 同上 | PASS (5 passed) | `verification/P20-CLOSE-BOUND-1/concurrency-lock-audit.md`, `ac4-inner-lock-contention.stdout.log`, `ac4-child-lock-contention.stdout.log`, `ac4-writer-pipe-overflow.stdout.log` |
| AC5：真实桌面窗口关闭场景 | `pwsh -NoProfile -File verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1` | 已更新支持自包含落盘至 `$OutDir`；历史证据保留在 `ac5-20261018-1256`（78.61 ms 退出，0 残留） | PASS（Coordinator 独立复跑） | `verification/P20-CLOSE-BOUND-1/ac5-20261018-1256/**` |
| AC6：证据落盘与治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-CLOSE-BOUND-1.md` | 同上 | PASS (0 errors, 2 warnings) | 完整验证产物落盘 `verification/P20-CLOSE-BOUND-1/` |

---

## 接收方式与复核指令

1. 工作区位于 `G:\CODEX\New Manga`，代码与证据均已就绪（按项目约束未执行 git commit，等待 Coordinator 提交）。
2. 复现与回归测试命令：
   - 运行完整验证套件：`pwsh -NoProfile -File verification/P20-CLOSE-BOUND-1/test-ac1-overlay-bound.ps1`
   - 运行治理检查：`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-CLOSE-BOUND-1.md`
3. 推荐下一步：
   - **推荐 Agent**：Codex（Reviewer / Integrator）
   - **可直接转发给 Codex 的指令**：
     ```
     请对 P20-CLOSE-BOUND-1 执行独立复审 R4：
     1. 检查 apps/desktop/src-tauri/src/library_bridge.rs 中 N1（ctx.inner 锁超时 fallback 接管）、P1#2（child-reap-fallback 等待锁并真实调用 child.wait()，置位 child_reaped；taskkill /F /T /PID 进程树强杀）、P1#3（共享绝对 deadline 贯穿全链路，消除无界 taskkill 与无界锁）、P2#6（writer_finished/writer_joined/reader_joined 真断言与 BrokenPipe 释放）、P2#7（taskkill 退出码与输出检查上报）；
     2. 检查 verification/P20-CLOSE-BOUND-1/concurrency-lock-audit.md 的 16 项 WCET 闭式推导表（静态 2350 ms <= 3000 ms，具备 650 ms 硬裕度，动态上限 2400 ms）；
     3. 运行 pwsh -NoProfile -File verification/P20-CLOSE-BOUND-1/test-ac1-overlay-bound.ps1 验证全部 11 项测试与基线差集断链后代 0 残留（exit 0）；
     4. 运行 pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-CLOSE-BOUND-1.md 验证治理通过（PASS）；
     5. 由 Coordinator 验证或复跑 AC5 自包含脚本并执行 git commit，收口 Task 并推进到 done。
     ```

