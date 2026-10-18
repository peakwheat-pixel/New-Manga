---
task_id: P20-CLOSE-BOUND-HARDEN-1
author: Antigravity
recipient: Codex
base_commit: a04e4ea78d5b33a0f91efcdc06b396391c4b165e
delivery_head: 35770fe91ab722b6d6c5e06e1f855c062d15c0a2
status: ready_for_review
---

# Handoff：P20-CLOSE-BOUND-HARDEN-1（第三轮返修 —— 终轮加固交付）

## 交付结果

本轮返修针对 Codex Review R3（`verification/P20-CLOSE-BOUND-HARDEN-1/codex-review-r3.md`）提出的全部 Review Findings（R3-01 ~ R3-04）进行了严格、彻底的闭环重构与证据更新：

1. **R3-01（P1 / 闭环）—— Worker 句柄防丢弃（Option 取出语义与保底持有）、有界容量与生产全链路收割**：
   - **Handle 零丢弃与受控转移（Option 取出语义）**：`track_unreaped_worker` 签名重构为 `track_unreaped_worker(name, handle_slot: &mut Option<JoinHandle<()>>, ...)`。采用 10 次跨 500 ms 尝试获取锁，**仅在成功获锁且容量未达上限时才执行 `handle_slot.take()`**。若获锁失败或容量超限，句柄保留在调用方槽位中，由调用方（`reader_reaper` / `writer_reaper` 超时路径或 spawn 失败路径）立即派发专用的后台守护线程 `persistent-reader-holder` / `persistent-writer-holder` 持续持有并周期重试转交，彻底杜绝 Rust 因 Handle 被 drop 导致的线程 detach 风险。
   - **Registry 容量硬上限与自动修剪**：引入常量 `pub const MAX_UNREAPED_WORKERS: usize = 32`。入队前由 `prune_finished_unreaped_workers_locked` 对已结束的 worker 立即执行非阻塞 `join()` 并移出 vector；活跃数量达到 32 上限时触发紧急 `cancel_worker_io` 取消并等待背压槽位，杜绝无界内存与线程膨胀。
   - **生产全链路主动收割（5 处调用点）**：在 `StdioLibraryChannel::shutdown_and_kill_with_deadline`、`StdioLibraryChannel::drop`、`ResilientLibraryChannel::shutdown_with_deadline`、`ResilientLibraryChannel::drop` 以及 `core-self-healing` 恢复自愈线程中全面调用 `reap_unreaped_workers`，确保进程生命周期内和关闭时均有确定性收割。
   - **锁争用修复**：`reap_unreaped_workers` 循环在 `sleep` 前显式 `drop(lock)`，并在预算耗尽时支持 0 ms 无等待清理已完成 Worker。新增单测 `ac4_unreaped_worker_registry_capacity_cap_and_lock_failure_retains_handle` 实跑通过。

2. **R3-02（P2 / 闭环）—— CAS 32 次重试耗尽后的共享状态回读与强制生效断言**：
   - 在 `register_atomic_deadline` 中，初始注册 CAS 循环在 32 次重试耗尽后，强制通过 `load(Ordering::SeqCst)` 回读共享 atomic 当前真实值；若当前值宽松于 candidate 则强制单调收紧（`fetch_min` / `store(1)`），返回值严格取自共享 atomic 的真实生效时间，杜绝保留旧截止时间；
   - 过期 sentinel 判定分支在 32 次 CAS 耗尽后若仍非 1，强制执行 `store(1, Ordering::SeqCst)` 并断言 `verified_sentinel == 1`；
   - 新增两项确定性故障注入单测 `ac1_deadline_cas_initial_retries_exhaustion_reads_back_and_enforces_shared_tightening` 与 `ac1_deadline_cas_sentinel_retries_exhaustion_reads_back_and_enforces_sentinel_1`，实跑全过。

3. **R3-03（P2 / 闭环）—— 比对真实桌面子进程 ExitCode 并保留一致性断言**：
   - 在 `run-desktop-close-verification.ps1` 中扩展支持 `$AppArgs` 参数；子进程启动后加入快速退出检测（`$proc.HasExited` 跳出避免空等）；真实子进程退出后提取 `$proc.ExitCode` 并写入 `$appExitCode`，若非零退出则脚本退出码设置为该退出码，同时在 `ac5.exit`、`ac5-metadata.json`（字段 `desktop_exit_code` 与 `exit_code`）与 `ac5-metadata.txt` 中完整记录；
   - 在 `test-artifact-lock-fault.ps1` 的 Case 9（Case 9a、9b、9c）中，全面将断言更新为比对**真实桌面子进程**退出码（`$jsonObj9*.desktop_exit_code`），并严格断言与 `ac5.exit` 内容、metadata `exit_code` 及 runner 退出码一致；
   - 新增 Case 8b 测试子进程非零退出码（42）的透明传播与产物一致性，验证通过。

4. **R3-04（P2 / 闭环）—— AC5 审计表行号修正与真实语义重写**：
   - 在 `verification/P20-CLOSE-BOUND-1/concurrency-lock-audit.md` 中，更正 `CloseHandle` 的真实行号为 `library_bridge.rs:1857, 1965, 3880, 3886`，`DuplicateHandle` 位于 `1886, 1994`；
   - 同步修正 Table 1.1 中全部 22 处调用点及 Section 3 中 Worker 1~6 的最新精确行号；
   - 按 R3-01 修复后的真实语义重写 Section 1、Table 3 与 Section 4：明确 `MAX_UNREAPED_WORKERS = 32` 硬容量上限、`Option` 取出语义、持久持有线程保底与生产 5 处主动收割调用链路。

5. **元数据与 Canonical Evidence 表更新**：
   - Task `doc/tasks/P20-CLOSE-BOUND-HARDEN-1.md` 的 `delivery_head` 更新为 `35770fe91ab722b6d6c5e06e1f855c062d15c0a2`（通过 `git rev-parse HEAD` 实取，并通过 `git cat-file -e` 校验）；
   - 登记本轮 Review 报告 `codex-review-r3.md` 为 `SOURCE_PIN`；更新全部 125 项 Canonical Evidence 条目，SHA-256 均基于 Windows CRLF 真实磁盘字节实算；
   - 运行 `tools/governance/check.ps1` 校验全绿通过（PASS，0 errors）。

---

## 验证证据与结果对照表

| 场景/AC | 验证命令 | 结果 | 关键证据路径 |
|---|---|---|---|
| **AC1** (CAS 32次上限、耗尽回读与置1断言) | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop ac1_` | **PASS** (Exit 0, 10/10 通过) | [ac1-deadline-cas-monotonic.stdout.log](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/ac1-deadline-cas-monotonic.stdout.log) |
| **AC4** (Worker 句柄防丢弃、容量上限与取消收割) | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop ac4_` | **PASS** (Exit 0, 7/7 通过) | [ac4-blocked-reader-worker.stdout.log](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/ac4-blocked-reader-worker.stdout.log)<br>[ac4-blocked-writer-worker.stdout.log](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/ac4-blocked-writer-worker.stdout.log) |
| **AC5** (并发锁与系统调用审计) | 静态审计比对与精确行号核查 | **PASS** (行号与真实语义100%匹配) | [concurrency-lock-audit.md](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-1/concurrency-lock-audit.md) |
| **AC7 故障注入** (跨产物锁与真实子进程退出码比对) | `pwsh -NoProfile -File verification/P20-CLOSE-BOUND-HARDEN-1/test-artifact-lock-fault.ps1` | **PASS** (Exit 0, 10/10 场景全过) | [artifact-lock-fault.stdout.log](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/artifact-lock-fault.stdout.log) |
| **AC7 桌面直跑** (真实交互桌面运行) | 留给 Coordinator 在交互式 Windows 桌面执行 | **NOT_RUN** | 待 Coordinator 执行 `run-desktop-close-verification.ps1` |
| **AC8** (9项核心回归测试全绿) | `pwsh -NoProfile -File verification/P20-CLOSE-BOUND-HARDEN-1/run-ac8-regression.ps1` | **PASS** (Exit 0, 9/9 项全过) | [ac8-regression-summary.md](file:///G:/CODEX/New%20Manga/verification/P20-CLOSE-BOUND-HARDEN-1/ac8-regression-summary.md) |
| **治理检查** (Governance Check) | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-CLOSE-BOUND-HARDEN-1.md` | **PASS** (Exit 0, 125项证据全过) | tools/governance/check.ps1 输出 PASS |

---

## 接收方式

- 仓库：`G:\CODEX\New Manga`，分支 `main`。
- 实现提交：`35770fe91ab722b6d6c5e06e1f855c062d15c0a2`
- 复现验证命令：
  - CAS 与 Registry 单元测试：`cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop ac1_` 及 `ac4_`
  - 产物锁与真实二进制退出码比对套件：`pwsh -NoProfile -File verification/P20-CLOSE-BOUND-HARDEN-1/test-artifact-lock-fault.ps1`
  - AC8 回归测试套件：`pwsh -NoProfile -File verification/P20-CLOSE-BOUND-HARDEN-1/run-ac8-regression.ps1`
  - 治理合规性检查：`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-CLOSE-BOUND-HARDEN-1.md`

---

## 下一任务建议（必填）

- Task ID / 标题：P20-CLOSE-BOUND-HARDEN-1 Codex 第四轮复审（Round 4，终审）与 AC7 交互桌面直跑
- 推荐 Agent / Reviewer：Codex（独立 Reviewer） / Coordinator（dsh，执行交互桌面直跑）
- 推荐原因与前置依赖：Antigravity 已彻底闭环 Codex R3 审查提出的全部 4 项 Finding（R3-01 ~ R3-04），完成 Worker Handle 零丢弃与持有保底、Registry 32 容量上限与生产全链路收割、CAS 耗尽回读校验、真实桌面子进程 ExitCode 比对断言、审计表行号与真实语义对齐，以及 125 项 Canonical Evidence 校验。请 Codex 执行 Round 4 复审，并请 Coordinator 在真实交互桌面执行 AC7 直跑。
- Recovery point：`G:\CODEX\New Manga`，分支 `main`，HEAD 指向本次交付提交。
- 可直接转发给 Codex 的指令：
  ```
  请 Codex 对 P20-CLOSE-BOUND-HARDEN-1 进行 Round 4 复审（最后一次复审），核对 R3-01（worker 句柄防丢弃 Option 取出语义、持久持有保底、MAX_UNREAPED_WORKERS=32 容量上限与生产 5 处主动收割调用链路）、R3-02（CAS 32 次上限耗尽后的共享 atomic 回读与 store(1) 单调收紧断言）、R3-03（Case 9 比对真实桌面子进程 ExitCode 与 Case 8b 非零退出码传播）、R3-04（CloseHandle 与 22 处调用点精确行号修正及真实语义重写）以及 125 项 Canonical Evidence 的闭环情况；请 Coordinator 在真实交互式 Windows 桌面执行 verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1 补充 AC7 真实桌面产物。
  ```
