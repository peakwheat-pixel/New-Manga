---
task_id: P20-CLOSE-BOUND-HARDEN-1
author: Antigravity
recipient: Codex
base_commit: 01129315100928751546c9608456868f5085fa8c
delivery_head: 待提交后更新
status: ready_for_review
---

# Handoff：P20-CLOSE-BOUND-HARDEN-1

## 交付结果

本任务针对 Codex Review R6 §7 提出的 5 项未闭合点（CBH-01 ~ CBH-05）和 AC1 ~ AC8 验收标准实施了彻底加固：

1. **CBH-01（P1）→ AC3 + AC4**：
   - 彻底禁止 deadline 到期后的任何清理动作：`child-reap-fallback` 与 `pending-drain-fallback` 启动前与循环中严格检查 deadline，到期后严禁调用 `child.kill()` 或 `child.try_wait()`。
   - `StdioLibraryChannel` 保存原始 OS 管道句柄并实现 `cancel_active_pipes()`，在等待 reader/writer 线程前调用 Windows `CancelIoEx` 取消挂起 I/O，确保阻塞在读写的 worker 接收到管道破裂并正常退出。
   - 引入 `ThreadFinishedGuard`，仅在 worker 局部变量和流完全析构后置位 `finished = true`；**仅对确认已结束的线程调用 `join()`**，未确认 finished 严禁 `join()`。
   - `run_taskkill_bounded` 捕获 `child.kill()` 返回值，并在 taskkill reaper、reader reaper、writer reaper 轮询中将 sleep 与错误锁等待时间全部纳入 200 ms 剩余预算截断，绝不跨越 200 ms。
   - 新增 4 个针对永久阻塞 reader/writer、taskkill 失败、post-deadline 清理禁止的故障注入单元测试。

2. **CBH-02（P1）→ AC1 + AC2 + AC5**：
   - 为 deadline CAS 建立硬重试上限 `MAX_DEADLINE_CAS_RETRIES = 32`，防止高并发无界自旋。
   - 建立单调性与零/过期预算保护：`encode_deadline` / `tighter_encoded_deadline` / `decode_deadline` 将 0 与已过期预算绝对编码为 1（0 ms 剩余），绝不映射为未来预算；新 deadline 只能收窄已有 deadline。
   - 逐调用点审计与 240 ms 会话包络纠正：更正原 R6 审计表第 4 项误记为 80 ms 的表述（实际传参为 `session_timeout` ≤ 240 ms）。
   - **禁止继续引用 2370 ms 作为全路径 WCET**：重构 WCET 为双层闭式模型（软件受控超时包络 $\le 2400\,\text{ms}$ + 操作系统内核系统调用边界），并将系统调用（`Command::spawn`、`child.kill`、6 次 `thread::Builder::spawn`、条件 `join`）显式列为物理 Limitation，提供 600 ms 的安全裕度。

3. **CBH-03（P2）→ AC6**：
   - 修正 `test-ac1-overlay-bound.ps1` 声明措辞为“Runner Descendants & Isolation Root Audit”，明确仅证明 runner 后代树与隔离根命中，去除 broken-chain 全覆盖不实措辞。

4. **CBH-04 & CBH-05（P2）→ AC7**：
   - `run-desktop-close-verification.ps1` 完全解耦 console / exit / metadata 写入；在 console log 遭遇独占文件锁（如调用方 `Tee-Object`）时自动写入 fallback console 并向 metadata 记录 warning。
   - 保证无论任何单个产物写入成败，始终写出与进程实际 exit code 一致的 `ac5.exit` 与 metadata。
   - 增加 `test-artifact-lock-fault.ps1` 故障注入套件，全覆盖验证正常写入、console 文件锁写入、失败退出码锁定写入及异常路径写入。

5. **AC8 回归测试**：
   - 全量回归 R-008 心跳恢复、R-003 拆环与 reap、R-006 错误呈现、MAX_RETRIES=3、is_down 关机写放行、既有 resilient 9 项、stdio drop、shutdown writes、2 MB pipe overflow，全部通过（ExitCode 0）。

---

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| **AC1/AC2/AC3/AC4/AC6** (CBH-01/02/03) | `pwsh -NoProfile -File verification/P20-CLOSE-BOUND-1/test-ac1-overlay-bound.ps1 -TargetDir verification/P20-CLOSE-BOUND-HARDEN-1` | Windows 11, pwsh 7, Rust 1.83+ | **PASS** (Exit 0) | [ac2-process-tree-audit.log](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/ac2-process-tree-audit.log)<br>[ac1-deadline-cas-monotonic.stdout.log](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/ac1-deadline-cas-monotonic.stdout.log) (残余孤儿 0) |
| **AC4/AC5** (CBH-01/02 故障注入) | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop ac4_fault_injection` | 同上 | **PASS** (Exit 0) | [ac4-blocked-reader-worker.stdout.log](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/ac4-blocked-reader-worker.stdout.log)<br>[ac4-blocked-writer-worker.stdout.log](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/ac4-blocked-writer-worker.stdout.log)<br>[ac4-taskkill-fault-injection.stdout.log](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/ac4-taskkill-fault-injection.stdout.log) |
| **AC7** (CBH-04/05 文件锁与产物韧性) | `pwsh -NoProfile -File verification/P20-CLOSE-BOUND-HARDEN-1/test-artifact-lock-fault.ps1` | 同上 | **PASS** (Exit 0) | [artifact-lock-fault.stdout.log](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/artifact-lock-fault.stdout.log)<br>[artifact-lock-fault.exit](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/artifact-lock-fault.exit) |
| **AC7 交互桌面直跑** | 任务明确规定由 Coordinator 在交互式 Windows 桌面执行（非交互 agy 会报 WebView2 0x80070578） | 待 Coordinator 交互桌面执行 | **NOT_RUN** | 待 Coordinator 在真实桌面执行 `run-desktop-close-verification.ps1` 并 pin 产物 |
| **AC8 回归套件** (9项核心回归) | `pwsh -NoProfile -File verification/P20-CLOSE-BOUND-HARDEN-1/run-ac8-regression.ps1` | 同上 | **PASS** (Exit 0) | [ac8-regression-summary.md](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/ac8-regression-summary.md)<br>9项测试全绿 |

---

## 接收方式

- 仓库：`G:\CODEX\New Manga`，分支 `main`。
- 直接复现命令：
  - 自动化验证套件：`pwsh -NoProfile -File verification/P20-CLOSE-BOUND-1/test-ac1-overlay-bound.ps1 -TargetDir verification/P20-CLOSE-BOUND-HARDEN-1`
  - 文件锁故障注入套件：`pwsh -NoProfile -File verification/P20-CLOSE-BOUND-HARDEN-1/test-artifact-lock-fault.ps1`
  - AC8 回归测试套件：`pwsh -NoProfile -File verification/P20-CLOSE-BOUND-HARDEN-1/run-ac8-regression.ps1`
- 审查重点：
  - [library_bridge.rs](file:///G:/CODEX/New%20Manga/apps/desktop/src-tauri/src/library_bridge.rs) 中 `ThreadFinishedGuard`、`cancel_active_pipes()`、CAS deadline 单调性与零保护、reaper 轮询受限；
  - [concurrency-lock-audit.md](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-1/concurrency-lock-audit.md) 中逐调用点映射、更正的第 4 项说明、双层 WCET 闭式推导与 Limitation 声明；
  - [run-desktop-close-verification.ps1](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1) 中的 artifact 写入解耦与一致性保障。

---

## 下一任务建议（必填）

- Task ID / 标题：P20-CLOSE-BOUND-HARDEN-1 独立 Review 与交互桌面 AC7 证据收集
- 推荐 Agent / Reviewer：Codex（独立 Review） / Coordinator (dsh，执行交互桌面直跑)
- 推荐原因与前置依赖：Antigravity 已完成 CBH-01~05 全部代码加固、审计表重算和自动化套件验证；需要 Codex 执行独立代码审查与裁决，并在交互桌面运行 AC7 直跑。
- Recovery point：`G:\CODEX\New Manga`，分支 `main`，HEAD 指向本次交付提交。
- 允许修改路径：`verification/P20-CLOSE-BOUND-HARDEN-1/**`，`doc/tasks/P20-CLOSE-BOUND-HARDEN-1.md`，`doc/STATUS.md`。
- 禁止范围与新增授权条件：禁止触碰用户 20 个 dirty 文件；禁止修改 IPC 协议与产品公共 API。
- 交付物：Codex Review 报告（`verification/P20-CLOSE-BOUND-HARDEN-1/codex-review-r1.md`）及 Coordinator 的 AC7 桌面直跑产物。
- 验证命令、环境与完成 Gate：
  1. 检查 Rust 单元测试与 PS 验证脚本全部 PASS；
  2. 交互桌面执行 `run-desktop-close-verification.ps1` 退出码 0 且无残余孤儿；
  3. Codex 签署通过。
- 可直接转发给 Agent 的指令：
  ```
  请 Codex 对 P20-CLOSE-BOUND-HARDEN-1 进行独立审查，核对 CBH-01 ~ CBH-05 的闭环情况及 verification/P20-CLOSE-BOUND-1/concurrency-lock-audit.md 的重构结论；请 Coordinator 在交互式 Windows 桌面执行 verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1 收集 AC7 真实桌面直跑产物。
  ```

---

## 风险与遗留

1. **AC7 桌面直跑需由 Coordinator 补充**：非交互式 CLI 环境无法渲染 WebView2 窗口，故 AC7 桌面直跑如实标记为 `NOT_RUN`，脚本自身的健壮性已通过 `test-artifact-lock-fault.ps1` 充分验证。
2. **系统调用物理 Limitation**：操作系统进程创建和驱动层 I/O 取消属于内核不可抗力边界，已在审计表中做诚实声明，由 600 ms 的安全裕度吸收。
