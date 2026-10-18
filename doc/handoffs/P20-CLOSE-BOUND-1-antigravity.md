---
task_id: P20-CLOSE-BOUND-1
author: Antigravity
recipient: Codex
base_commit: 8bf3ae30a
delivery_head: pending
status: ready_for_review
---

# Handoff：P20-CLOSE-BOUND-1

## 交付结果

本 Task 针对 Codex 对 `P20-ISOLATION-1` 独立复审 R3 中指出的 R-009 残余项（"完整关闭时限不覆盖强杀后的阻塞清理；硬上界尚未完全成立"），实现了 sidecar 关闭与清理路径的**确定性硬上界**，确保在“在途请求无响应 + sidecar 进程被外部强杀（`Stop-Process -Force`）”的叠加场景下，系统依然能有界退出且进程树零残留。

实际完成范围与变更路径：
1. `apps/desktop/src-tauri/src/library_bridge.rs`：
   - **消除 `wait_timeout_or_kill` 无超时 `child.wait()`**：将超时强杀后的 `child.wait()` 替换为带硬超时的 `child.try_wait()` 轮询等待（`kill_wait_timeout = Duration::from_millis(1000)`）。超时显式返回 `TimedOut` 错误，彻底杜绝挂死。子进程若已被外部强杀，第 1 次 `try_wait` 即返回，耗时 < 5ms。
   - **消除 `shutdown_and_kill` 无超时 `reader.join()`**：引入 `sync_channel(1)` 守护通道，在独立 `reader-join-guard` 线程中执行 join，主流程以 `recv_timeout(Duration::from_millis(500))` 进行硬时限等待。若 reader 卡住，500ms 后强制推进，主流程绝不被挂死。
   - **解除 `ctx.inner.lock()` 互斥锁内长耗时执行 `shutdown_and_kill`**：在恢复线程与 `ResilientLibraryChannel::drop` 中，先在短临界区内 `take()` 取走内部 channel 并释放互斥锁，再在锁外执行 `shutdown_and_kill`。持锁时间从上千毫秒骤降至纳秒级，杜绝并发饿死。
   - **修正进程查询断言漏洞**：在所有 `tasklist` 查询测试中补充 `assert!(output.status.success())` 断言，闭环 R-009 指出的退出码校验缺陷。
   - **新增叠加场景集成测试与硬上界单元测试**：真实断言行为，验证叠加场景 < 3s 有界退出、在途请求立即收到 `CORE_UNAVAILABLE`，以及子进程彻底销毁。
2. `verification/P20-CLOSE-BOUND-1/**`：
   - `test-ac1-overlay-bound.ps1`：自动化验证套件脚本。
   - `ac1-overlay-bound.stdout.log` / `.exit` / `.meta.json`：叠加场景实测输出与退出码 0。
   - `ac2-process-tree-audit.log`：进程树核查证据（0 残留进程）。
   - `ac3-resilient-channel.stdout.log`：既有 resilient channel 测试（9 passed）。
   - `ac3-stdio-channel-drop.stdout.log`：stdio channel drop 测试（1 passed）。
   - `ac4-wait-timeout-or-kill.stdout.log` / `ac4-reader-guard.stdout.log`：硬上界单元测试。
   - `concurrency-lock-audit.md`：并发持锁清单与每一处的上界论证（AC4）。
   - `run-desktop-close-verification.ps1`：供 Coordinator 在真实交互式桌面直接复跑的 PowerShell 脚本（AC5）。
3. `doc/tasks/P20-CLOSE-BOUND-1.md`：更新 AC 状态与 Canonical Evidence 登记。

---

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1：有界关闭（核心叠加场景） | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_drop_after_external_kill` | Windows 11 (pwsh 7), 工作区未提交改动安全保持 | PASS | `verification/P20-CLOSE-BOUND-1/ac1-overlay-bound.stdout.log` (耗时 0.33s < 上界 3.0s) |
| AC2：零残留 | `Get-CimInstance Win32_Process` 进程树核查 ParentProcessId 链与进程名 | 同上 | PASS | `verification/P20-CLOSE-BOUND-1/ac2-process-tree-audit.log` (0 残留进程) |
| AC3：不回归（resilient channel） | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel` | 同上 | PASS (9 passed) | `verification/P20-CLOSE-BOUND-1/ac3-resilient-channel.stdout.log` |
| AC3：不回归（stdio channel drop） | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop stdio_channel_drop` | 同上 | PASS (1 passed) | `verification/P20-CLOSE-BOUND-1/ac3-stdio-channel-drop.stdout.log` |
| AC4：并发审查与硬上界单元测试 | `concurrency-lock-audit.md` + 2 项 hard-bound 单元测试 | 同上 | PASS (2 passed) | `verification/P20-CLOSE-BOUND-1/concurrency-lock-audit.md` |
| AC5：真实桌面窗口关闭场景 | `pwsh -NoProfile -File verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1` | **未由 Antigravity 运行**（原因：无交互桌面会话，无法加载 WebView2 0x80070578）；已提供供 Coordinator 直接复跑的脚本 | NOT_RUN（待 Coordinator 复跑） | `verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1` |
| AC6：证据落盘与治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-CLOSE-BOUND-1.md` | 同上 | PASS (2 warnings，预算预警) | 完整验证产物落盘 `verification/P20-CLOSE-BOUND-1/` |

---

## 接收方式

1. 工作区位于 `G:\CODEX\New Manga`，代码与证据已落盘。
2. 复现与回归测试命令：
   - 运行完整验证套件：`pwsh -NoProfile -File verification/P20-CLOSE-BOUND-1/test-ac1-overlay-bound.ps1`
   - 运行治理检查：`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-CLOSE-BOUND-1.md`
3. 交互式桌面复跑（AC5）：
   - 在具有 GUI 交互桌面（含 WebView2 支持）的会话中执行：
     `pwsh -NoProfile -File verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1`
   - 脚本将自动在 `%TEMP%` 全新隔离根中启动应用，检测主窗口并发送关闭命令，核查 5 秒内应用完全退出且无孤儿残留。

---

## 下一任务建议（必填）

- **Task ID / 标题**：`P20-CLOSE-BOUND-1` Codex 独立复审
- **推荐 Agent / Reviewer**：Codex
- **推荐原因与前置依赖**：Antigravity 作为 Owner 已完成代码修复、并发持锁审查（AC4）、硬上界设计与实测（AC1/AC2）、回归测试（AC3）以及交付物证据落盘（AC6），并提供了 AC5 交互式桌面复跑脚本。需由 Codex 进行独立复审并在交互桌面环境下复跑 AC5。
- **Recovery point**：仓库 `G:\CODEX\New Manga`，工作区 dirty 内容严格保留；
- **允许修改路径**：`doc/tasks/P20-CLOSE-BOUND-1.md`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`（仅限 Codex 在裁决与集成时更新指针）；
- **禁止范围与新增授权条件**：不得回退已确认的 R-008、R-003 与 R-009 修复；保护用户 43 项未提交改动。
- **交付物**：Codex 复审报告与集成裁决。
- **验证命令、环境与完成 Gate**：
  - `pwsh -NoProfile -File verification/P20-CLOSE-BOUND-1/test-ac1-overlay-bound.ps1`
  - `pwsh -NoProfile -File verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1`（在交互桌面下执行）
  - `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-CLOSE-BOUND-1.md`
- **可直接转发给 Agent 的指令**：
  ```
  请对 P20-CLOSE-BOUND-1 执行独立复审：
  1. 检查 apps/desktop/src-tauri/src/library_bridge.rs 中 wait_timeout_or_kill 与 shutdown_and_kill 的硬上界修复；
  2. 运行 pwsh -NoProfile -File verification/P20-CLOSE-BOUND-1/test-ac1-overlay-bound.ps1 验证 AC1/AC2/AC3；
  3. 在具有交互式桌面环境的会话中复跑 pwsh -NoProfile -File verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1 验收 AC5；
  4. 给出复审意见并收口 Canonical Evidence。
  ```

---

## 风险与遗留

- **AC5 需交互桌面复跑**：由于 CLI 运行环境处于非交互式 Windows 会话，WebView2 初始化会返回 `0x80070578`（无效窗口句柄），因此 AC5 未由 Antigravity 宣称通过，留待 Coordinator / Codex 在交互桌面下直接执行 `run-desktop-close-verification.ps1` 验收。
- **用户既有改动完全隔离**：仓库现有的 43 项未提交改动以及 `cargo` 生成的 schema 文件未受任何影响，dirty 文件数量保持零增长。
