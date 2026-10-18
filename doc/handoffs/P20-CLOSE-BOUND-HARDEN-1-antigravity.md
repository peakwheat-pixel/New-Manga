---
task_id: P20-CLOSE-BOUND-HARDEN-1
author: Antigravity
recipient: Codex
base_commit: a04e4ea78d5b33a0f91efcdc06b396391c4b165e
delivery_head: ed737b5d262d6f7d7b07d8b70900d6af71c11b3c
status: ready_for_review
---

# Handoff：P20-CLOSE-BOUND-HARDEN-1（第一轮返修）

## 交付结果

本轮返修针对 Codex Review R1（`verification/P20-CLOSE-BOUND-HARDEN-1/codex-review-r1.md`）提出的 4 项 Finding（CBH-R1-01 ~ CBH-R1-04）及元数据要求实施了彻底加固与闭环：

1. **CBH-R1-01（P1 / 闭环）—— Windows 同步 Pipe 取消与生命周期**：
   - **双重可验证取消与返回值检查**：实现统一封装 `cancel_worker_io(pipe_handle, thread_handle) -> PipeCancellationReport`，同时调用 `CancelIoEx`（解除阻塞在 pipe 的 I/O）与 `CancelSynchronousIo`（解除 worker 线程阻塞的同步系统调用），严密检查返回值与错误码并记录于报告。
   - **Worker 真实线程句柄持有**：`StdioLibraryChannel::adopt_child` 在 reader 和 writer 线程启动时通过 Windows API `DuplicateHandle` 获得对应 worker 线程真实有效句柄，存储于原子变量，在 Drop 时安全 `CloseHandle`。
   - **未收割线程追踪防丢弃**：reader reaper 与 writer reaper 在 200 ms 超时未结束时，将 JoinHandle 存入静态追踪列表 `UNREAPED_WORKER_HANDLES`，彻底消除静默丢弃 `JoinHandle`。
   - **真实系统调用阻塞测试**：彻底删除 `TEST_MOCK_READER_BLOCKED`、`TEST_MOCK_WRITER_BLOCKED` 及手动 sleep 钩子。新增真实阻塞在系统调用的单元测试：`ac4_cancel_pipe_io_returns_canceled_on_blocked_pipe_read`、`ac4_cancel_pipe_io_returns_canceled_on_blocked_pipe_write`、`ac4_fault_injection_blocked_reader_worker_bounds_and_cancels`、`ac4_fault_injection_blocked_writer_worker_bounds_and_cleans_up`，证明 worker 在有界时间内安全退出。
   - **句柄生命周期防串扰**：reader/writer 退出时采用 RAII 清理 guard 自动清零 handle，在取消前严格检查 worker finished 状态，杜绝由于 OS 句柄重用而导致并发测试受到串扰。

2. **CBH-R1-02（P2 / 闭环）—— Deadline CAS Monotonicity & Interim Expiration**：
   - `library_bridge.rs` 中 `register_atomic_deadline` 在 CAS 成功（或选定 tighter 值）后，立即比较 candidate deadline 与 `Instant::now()` 及 `created_at`。若线程在编码后被挂起导致 deadline 已过期，则通过单调原子操作以 sentinel 1 写入，并返回零预算（0 ms）。
   - 增加可控暂停测试钩子 `TEST_BEFORE_DEADLINE_CAS_HOOK`，并编写单元测试 `ac1_deadline_cas_expired_during_pause_writes_sentinel_1_and_returns_zero_budget`，验证 descheduled 线程在恢复后 CAS 写入 sentinel 1 并返回零预算。

3. **CBH-R1-03（P2 / 闭环）—— Artifact Lock Fault Injection & Verified Fallback Paths**：
   - `run-desktop-close-verification.ps1` 为 `ac5.exit`、`ac5-metadata.txt`、`ac5-metadata.json` 提供了完备的备用写入路径：`ac5.exit-fallback`、`ac5-metadata-fallback.txt`、`ac5-metadata-fallback.json`；并在 metadata 中精细记录各文件的 written / fallback_written 状态与 warning。
   - `test-artifact-lock-fault.ps1` 扩展为 9 个独立用例：
     - Case 1: 正常基线写入；
     - Case 2: console 独占锁 -> fallback 写入断言；
     - Case 3: console 独占锁 + 失败模拟；
     - Case 4: 二进制缺失异常路径；
     - Case 5: `ac5.exit` 独占锁 -> `ac5.exit-fallback` 写入与内容一致性断言；
     - Case 6: `ac5-metadata.json` 独占锁 -> `ac5-metadata-fallback.json` 写入与 JSON 可解析一致性断言；
     - Case 7: `ac5-metadata.txt` 独占锁 -> `ac5-metadata-fallback.txt` 写入断言；
     - Case 8: 极端争用（所有 4 个产物同时持有 `FileShare.None` 独占锁）-> 全部 4 个 fallback 文件均成功写入且退出码一致；
     - Case 9: 真实二进制（非 Mock 模式，启动 `m2rc1-desktop.exe`）启动下的锁争用与产物一致性验证。
   - 明确闭环边界为受保护产物集合（`ac5-console.log`、`ac5.exit`、`ac5-metadata.txt`、`ac5-metadata.json`）的主路径与备用路径，不扩大声称范围。

4. **CBH-R1-04（P2 / 闭环）—— Audit Scope & Command Nomenclature**：
   - 同步修改 `verification/P20-CLOSE-BOUND-1/test-ac1-overlay-bound.ps1` 第 345 行与 `verification/P20-CLOSE-BOUND-HARDEN-1/ac2-process-tree-audit.meta.json`，将命令名称由 Broken-Chain Orphan Audit 修正为 `Runner Descendants & Isolation Root Audit`，与缩窄后的范围完全匹配。

5. **AC7（NOT_RUN）**：
   - 交互桌面直跑按约定留给 Coordinator（非交互式会话缺少 WebView2 桌面交互支持，报 0x80070578），已如实标记为 `NOT_RUN`。脚本自身已通过 Case 9 真实二进制启动验证。

6. **AC8（PASS）—— 回归验证全绿**：
   - 运行 `run-ac8-regression.ps1`，全部 9 项核心测试（R-008, R-003, R-006, MAX_RETRIES_3, is_down, resilient_suite_9, stdio_channel_drop, shutdown_writes, pipe_overflow_2mb）100% 通过（ExitCode 0）。

7. **元数据与 Canonical Evidence**：
   - `doc/tasks/P20-CLOSE-BOUND-HARDEN-1.md` 更新为 `status: in_review`，`delivery_head: ed737b5d262d6f7d7b07d8b70900d6af71c11b3c`。
   - Canonical Evidence 表完整填报 123 个证据文件，SHA-256 全部按磁盘真实字节实算，commit 对应包含该路径的真实提交。

---

## 验证证据与结果对照表

| 场景/AC | 验证命令 | 结果 | 关键证据路径 |
|---|---|---|---|
| **CBH-R1-01** (同步 Pipe 取消与阻塞测试) | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop ac4_` | **PASS** (Exit 0) | [ac4-blocked-reader-worker.stdout.log](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/ac4-blocked-reader-worker.stdout.log)<br>[ac4-blocked-writer-worker.stdout.log](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/ac4-blocked-writer-worker.stdout.log) |
| **CBH-R1-02** (CAS 暂停点过期置 1 测试) | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop ac1_deadline_cas_expired_during_pause` | **PASS** (Exit 0) | [ac1-deadline-cas-monotonic.stdout.log](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/ac1-deadline-cas-monotonic.stdout.log) |
| **CBH-R1-03** (9项文件锁注入与Fallback断言) | `pwsh -NoProfile -File verification/P20-CLOSE-BOUND-HARDEN-1/test-artifact-lock-fault.ps1` | **PASS** (Exit 0) | [artifact-lock-fault.stdout.log](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/artifact-lock-fault.stdout.log)<br>[artifact-lock-fault.exit](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/artifact-lock-fault.exit) |
| **CBH-R1-04** (Runner Descendants 审计) | `pwsh -NoProfile -File verification/P20-CLOSE-BOUND-1/test-ac1-overlay-bound.ps1 -TargetDir verification/P20-CLOSE-BOUND-HARDEN-1` | **PASS** (Exit 0) | [ac2-process-tree-audit.meta.json](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/ac2-process-tree-audit.meta.json)<br>[ac2-process-tree-audit.log](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/ac2-process-tree-audit.log) (残余孤儿 0) |
| **AC7** (交互桌面直跑) | 留给 Coordinator 在交互式 Windows 桌面执行 | **NOT_RUN** | 待 Coordinator 执行 `run-desktop-close-verification.ps1` |
| **AC8** (9项核心回归测试) | `pwsh -NoProfile -File verification/P20-CLOSE-BOUND-HARDEN-1/run-ac8-regression.ps1` | **PASS** (Exit 0) | [ac8-regression-summary.md](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/ac8-regression-summary.md) |

---

## 接收方式

- 仓库：`G:\CODEX\New Manga`，分支 `main`。
- 实现提交：`ed737b5d262d6f7d7b07d8b70900d6af71c11b3c`
- 复现验证命令：
  - 自动化套件：`pwsh -NoProfile -File verification/P20-CLOSE-BOUND-1/test-ac1-overlay-bound.ps1 -TargetDir verification/P20-CLOSE-BOUND-HARDEN-1`
  - 文件锁与 fallback 故障注入套件：`pwsh -NoProfile -File verification/P20-CLOSE-BOUND-HARDEN-1/test-artifact-lock-fault.ps1`
  - AC8 回归测试套件：`pwsh -NoProfile -File verification/P20-CLOSE-BOUND-HARDEN-1/run-ac8-regression.ps1`

---

## 下一任务建议（必填）

- Task ID / 标题：P20-CLOSE-BOUND-HARDEN-1 Codex 复审（Round 2）与 AC7 交互桌面直跑
- 推荐 Agent / Reviewer：Codex（独立 Reviewer） / Coordinator（dsh，执行交互桌面直跑）
- 推荐原因与前置依赖：Antigravity 已彻底闭环 Codex R1 审查提出的所有 4 项 Finding，自动化测试与回归测试全绿；请 Codex 执行 Round 2 复核，并请 Coordinator 在真实桌面执行 AC7 直跑。
- Recovery point：`G:\CODEX\New Manga`，分支 `main`，HEAD 指向本次交付提交。
- 可直接转发给 Codex 的指令：
  ```
  请 Codex 对 P20-CLOSE-BOUND-HARDEN-1 进行 Round 2 复审，核对 CBH-R1-01（同步 Pipe 取消与真实阻塞测试）、CBH-R1-02（CAS 成功后过期置 1）、CBH-R1-03（artifact 锁注入与 fallback 路径断言）、CBH-R1-04（审计名称与范围对齐）的闭环情况；请 Coordinator 在真实交互式 Windows 桌面执行 verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1 补充 AC7 真实桌面产物。
  ```
