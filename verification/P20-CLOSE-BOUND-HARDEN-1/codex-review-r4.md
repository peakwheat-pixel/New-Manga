---
task_id: P20-CLOSE-BOUND-HARDEN-1
reviewer: Codex
author: Antigravity
base_commit: 1b7bb9791a938da1291881da686b941ffaf9947f
reviewed_head: 35770fe91
decision: changes_requested
---

# P20-CLOSE-BOUND-HARDEN-1 第四轮独立 Review

## 范围与结论

固定基线为本轮交付前主线 `1b7bb9791`，审查 head 为 `35770fe91`。审查范围包括 `library_bridge.rs` 的 registry/worker 生命周期、CAS deadline 注册、artifact-lock Case 9、`concurrency-lock-audit.md` 与 AC8。未发现 IPC、Schema、ACL、依赖版本或 frontend 变更。

**结论：`changes_requested`，不可批准集成。** R3-02 与 R3-03 已闭合；R3-04 行号已修正但语义仍有过度承诺。R3-01 的 `Option` 保留解决了 registry 锁失败时的直接丢弃，但后续持久 holder 没有有限生命周期，holder 创建失败还会丢弃捕获的 `JoinHandle`，因此 AC4 的 worker 生命周期仍未闭合。AC8 九项本轮实跑全部 exit 0。AC7 真实交互桌面直跑保持 `NOT_RUN`，留给 Coordinator。

## R3 Findings 逐项复核

| 上轮项目 | R4 结论 | 依据 |
|---|---|---|
| R3-01（P1）worker 生命周期 | **OPEN（P1）** | `track_unreaped_worker` 仅在拿到 registry 锁且确认有容量后才 `take()` Option（`library_bridge.rs:1515-1569`）；registry 上限为 32（`:1496, :1532-1549`），生产代码确实调用 `reap_unreaped_workers`（`:3856-3859, :3891-3892, :4873, :5250-5253, :5266`）。但锁持续争用或容量持续饱和后，调用方启动的 `persistent-*-holder` 没有退出 deadline，也没有 holder 数量上限（`:3630-3647, :3665-3682, :3787-3804, :3822-3839`）。因此 32 只约束 registry，不约束 registry 外的 holder/句柄总数。并且这些 `Builder::spawn(...)` 的 `Result` 被 `let _ =` 丢弃；若 holder 创建失败，已 move 进闭包的 `h` 随失败闭包释放，`JoinHandle` 再次被 drop。容量测试 `ac4_unreaped_worker_registry_capacity_cap_and_lock_failure_retains_handle`（`:8744-8795`）只验证容量与常规入队/收割，没有注入 registry 锁获取失败或 holder spawn 失败。 |
| R3-02 CAS 耗尽 | **CLOSED** | 初始注册重试耗尽后回读 atomic；若仍为 0 尝试 CAS，若已有值则以 `store(1)` / `fetch_min` 单调收紧，并在 `:1335-1336` 再读回共享值（`:1290-1336`）。sentinel 耗尽分支回读、必要时写入 1，并断言读回值为 1（`:1364-1378`）。初始与 sentinel 两条确定性耗尽测试分别位于 `:8797-8825`、`:8832-8864`。 |
| R3-03 Case 9 子进程退出码 | **CLOSED** | runner 从真实桌面进程对象读取 `$proc.ExitCode`（`run-desktop-close-verification.ps1:178-180`），将 `desktop_exit_code` 写入 metadata（`:310-311, :343-351`），并在非零退出时传播该码（`:223-227`）。Case 9a/9b/9c 将 metadata 中的 `desktop_exit_code` 与 artifact 值核对（`test-artifact-lock-fault.ps1:336-342, :360-368, :383-391`）；相应已提交日志记录真实 binary 子进程退出码 101，且 metadata、`ac5.exit`/fallback 与 runner 均匹配（`artifact-lock-fault.stdout.log:105-137`）。这并不构成 AC7 真实桌面 Gate 的执行。 |
| R3-04 审计表 | **PARTIAL（P2 内容仍需修正）** | `concurrency-lock-audit.md:113` 的 `CloseHandle` 行号现在与源码一致：`1857, 1965, 3880, 3886`。但 `:26, :134-135, :147-150` 仍宣称句柄“绝不被 drop”并将有限 registry/reaping 描述成完整生命周期保证；R4-01 所列 holder spawn 失败及无界 holder 生命周期尚未覆盖，审计结论仍不准确。 |

## Finding

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R4-01（延续 R3-01） | P1 | `apps/desktop/src-tauri/src/library_bridge.rs:1527-1569, 3630-3647, 3665-3682, 3787-3804, 3822-3839`；审计 `verification/P20-CLOSE-BOUND-1/concurrency-lock-audit.md:26, 134-150` | registry 连续锁超时或达到 32 项容量后，fallback holder 以无上限 `while ho.is_some()` 重试；registry 之外的 holder 数量与存活时间都没有上界。若 holder `Builder::spawn` 失败，忽略的 `Err` 会释放 move closure 及其中的 `JoinHandle`，恢复隐式 detach。两条路径都不满足 AC4 的“明确、有限且可观测”的替代生命周期。 | 静态核对四个生产 holder 创建调用点；`ac4_unreaped_worker_registry_capacity_cap_and_lock_failure_retains_handle` 未故障注入锁超时/holder spawn 失败。 | 让句柄在 holder 创建失败时仍由可访问的所有者保留；为 holder 等待与总量建立明确上限/背压和可观察收口路径；增加锁超时、容量饱和、holder spawn 失败的确定性故障注入。同步修正审计表。 | open |

## AC8：R4 实际复跑

环境：Windows，PowerShell 7.6.6，cargo 1.98.1，rustc 1.98.1。新隔离根为 `%TEMP%\P20-CLOSE-BOUND-HARDEN-1-r4-74006cb4059c4098951685d5f8d33ca6`；`CARGO_TARGET_DIR` 指向该根下的 `cargo-target`，runner 输出也在该根。执行 `pwsh -NoProfile -File verification/P20-CLOSE-BOUND-HARDEN-1/run-ac8-regression.ps1 -TargetDir C:\Users\49745\AppData\Local\Temp\P20-CLOSE-BOUND-HARDEN-1-r4-74006cb4059c4098951685d5f8d33ca6`，runner exit **0**。

| # | 实际 cargo test 命令 | Exit |
|---:|---|---:|
| 1 | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_heartbeat_detects_unresponsive_child_and_recovers -- --nocapture` | 0 |
| 2 | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_shutdown_breaks_cycle_and_reaps_child_process -- --nocapture` | 0 |
| 3 | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_triggers_restart_and_emits_restarting_status -- --nocapture` | 0 |
| 4 | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_caps_retries_and_emits_fatal_after_three_failures -- --nocapture` | 0 |
| 5 | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop shutdown_writes_core_shutdown_to_sidecar_stdin_without_session -- --nocapture` | 0 |
| 6 | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel` | 0 |
| 7 | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop stdio_channel_drop_with_unresponsive_session_completes_in_bounded_time -- --nocapture` | 0 |
| 8 | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop shutdown_writes -- --nocapture` | 0 |
| 9 | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop writer_overflow_pipe_capacity_unblocks_and_cleans_up_on_kill -- --nocapture` | 0 |

九条命令全部 exit 0；runner 汇总为 9/9 PASS。第一条因隔离 target 首次构建耗时约 57.8 秒，未观察到 cargo 锁等待。

## 其他 Gate 与治理

| 项目 | 结论 | 依据 |
|---|---|---|
| AC7 真实交互桌面直跑 | `NOT_RUN` | 本轮未启动 WebView2 桌面窗口；AC8 和 artifact-lock suite 不替代 AC7，留给 Coordinator。 |
| 目标进程收尾 | PASS | AC8 完成后未发现 `m2rc1-desktop`、`core_service`、`host_bridge`、`cargo` 或 `rustc` 进程残留。 |
| 现有 Canonical Evidence | PASS，125/125 | 逐项按磁盘字节重算 SHA-256，并用 `git cat-file -e <commit>:<path>` 检查当前 Task 表内路径；125 项均匹配。 |
| 40 位 SHA | PASS | Frontmatter `base_commit` 已用 `git cat-file -e` 验证存在；`reviewed_head` 使用用户指定的短 SHA。 |

## Architecture 与 Verification 结论

- **Architecture：**变更限于 Tauri/Rust 的 shutdown/worker 生命周期及验证材料；没有越过 IPC、Schema 或依赖边界。
- **Verification：**CAS 与 Case 9 代码及证据闭环；AC8 实跑 9/9 exit 0；AC7 `NOT_RUN`。R3-01 的 holder 生命周期/失败保留缺口是本轮 P1 阻断项。

## 结论与下一步

`35770fe91` **不可批准集成**。请修复 R4-01，更新 `concurrency-lock-audit.md` 的生命周期边界，并在新 head 上覆盖锁超时、容量饱和及 holder spawn 失败；AC7 仍由 Coordinator 在真实交互桌面执行。AC8 本轮通过不改变 R3-01 的 P1 结论。
