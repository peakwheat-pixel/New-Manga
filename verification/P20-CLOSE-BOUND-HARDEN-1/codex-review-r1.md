---
task_id: P20-CLOSE-BOUND-HARDEN-1
reviewer: Codex
author: Antigravity
base_commit: a04e4ea78d5b33a0f91efcdc06b396391c4b165e
reviewed_head: 3e8f85a1221e2e0ce98c25be8d150a932cf27580
decision: changes_requested
---

# 独立 Review

## 结论与范围

审查绑定实现及证据提交 3e8f85a1221e2e0ce98c25be8d150a932cf27580。a95486e296bfaac8c3231eab14704d69db04250f 只追加 Handoff pin，没有改动目标源码。复核了目标文件、相关调用点、故障注入、审计表和真实磁盘证据；verification/P20-CLOSE-BOUND-HARDEN-1/SHA256SUMS.txt 的 121 项哈希全部匹配。

当前仓库 HEAD 为 8f73a4202275c49e6eb22634c2f8f6590c9bd697。按本轮约束没有修改 Task 或其他文件。Task 仍是 ready、delivery_head 为 null、Canonical Evidence 表为空；Owner response 的第 10 行把 base_commit 写为 01129315100928751546c9608456868f5085fa8c（ZCode 的 P20-AC4-FPS-1 实现提交），与本 Task 冻结的 a04e4ea78d5b33a0f91efcdc06b396391c4b165e 不同。上述是已知元数据缺口，不改变本报告所审查的精确代码 head，但当前 Task 生命周期记录仍未闭合。tools/governance/check.ps1 -TaskPath doc/tasks/P20-CLOSE-BOUND-HARDEN-1.md 本轮返回 FAIL（1 error、2 warnings）：READY Task 未出现在 Plan READY 节点；STATUS 与 Plan 另有体量预算 warning。

## Findings

| ID | 级别 | 状态 | file:line 依据 | 最小修法 |
|---|---|---|---|---|
| CBH-R1-01 | P1 | FAIL | apps/desktop/src-tauri/src/library_bridge.rs:1447-1452 使用标准 Rust ChildStdin/ChildStdout pipe；:1311-1322 只调用 CancelIoEx 并忽略返回值；:1521-1530、:1582-1596 的阻塞故障注入实际是在测试钩子中 sleep；测试 :7694-7716、:7750-7766 只在 shutdown 返回后手动解除钩子；reader/writer reaper :3097-3123、:3175-3201 到 200 ms 后会丢弃 JoinHandle。[Rust Windows CommandExt 文档](https://doc.rust-lang.org/std/os/windows/process/trait.CommandExt.html)说明默认 pipes 可能是同步 I/O；[Microsoft ReadFile 文档](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-readfile)对同步 I/O 指示使用 CancelSynchronousIo。 | 为同步 pipe worker 使用可验证的取消方案（例如持有对应 worker thread handle 并调用 CancelSynchronousIo，或切换到受控的 overlapped I/O）；检查取消结果，并用真实阻塞的 ChildStdout/ChildStdin 故障注入证明 worker 在有界时间内结束。当前测试不能证明 CancelIoEx 会解除这些同步读写。 |
| CBH-R1-02 | P2 | PARTIAL | apps/desktop/src-tauri/src/library_bridge.rs:1243-1250 仅在编码前检查 deadline；:1276-1302 之后才进行最多 32 次 CAS 并解码。若调用线程在编码后被挂起，近未来 deadline 可在 CAS 成功前过期；编码值仍是正预算，且毫秒量化可能令返回值晚于已过期的原 deadline。测试 :7576-7584 只传入调用时已过期 500 ms 的值，没有覆盖编码到 CAS 期间过期的竞态。 | CAS 成功后再次比较原 deadline 与 Instant::now()；若已过期，以单调 CAS 写入过期 sentinel 1 并返回零预算。增加可控暂停点的竞态测试。 |
| CBH-R1-03 | P2 | PARTIAL | verification/P20-CLOSE-BOUND-HARDEN-1/test-artifact-lock-fault.ps1:53-86 确实通过 FileShare.None 对 ac5-console.log 注入真实独占文件锁，并验证 fallback、ac5.exit 与 metadata；但各用例以 MockExitCode 运行，没有启动桌面进程。verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1:233-248 对 ac5.exit 写入失败只将脚本退出码置 1，未提供该 artifact 的备用写入位置；:250-293 对 metadata 写入也只有独立 try/catch，无故障 fallback。故障套件未锁定/注入 ac5.exit 或 metadata 写失败。 | 保留现有真实 console-lock 用例；补充 exit 与 metadata 各自的写失败注入和一致性断言，并在真实进程执行结果上验证。对不能写回原路径的 artifact 明确提供可核验的备用路径，不能声称任意 artifact 写失败均已闭环。 |
| CBH-R1-04 | P2 | PARTIAL | verification/P20-CLOSE-BOUND-1/test-ac1-overlay-bound.ps1:239-240、:313 已把覆盖范围缩为 runner 后代与隔离根，并明确排除全局 broken-chain 扫描；但 verification/P20-CLOSE-BOUND-1/test-ac1-overlay-bound.ps1:345 和 verification/P20-CLOSE-BOUND-HARDEN-1/ac2-process-tree-audit.meta.json:2 仍把命令标成 Broken-Chain Orphan Audit，容易被误读为全覆盖。 | 将旧 metadata 的命令描述同步改为 Runner Descendants & Isolation Root Audit，并确认报告、metadata 与脚本范围一致。 |

## 逐项状态

| 项目 | 状态 | 核验依据 |
|---|---|---|
| CBH-01：deadline 后 fallback 不 kill/try_wait；reaper sleep 与错误锁等待受剩余时间截断 | PARTIAL | child-reap-fallback 与 pending-drain-fallback 在循环和操作前检查 deadline（library_bridge.rs:2733-2754、:2967-3014）；sleep 和 last_shutdown_error 锁等待都用剩余预算截断。deadline 已过期的 child fallback 用例本轮复跑通过。但 CancelIoEx 对此处同步 pipe I/O 的取消语义未成立，且 reader/writer 故障用例没有真正阻塞在系统读写调用中；见 CBH-R1-01。 |
| CBH-02：CAS 上界、过期语义、WCET 与系统调用限制 | PARTIAL | MAX_DEADLINE_CAS_RETRIES=32 且源码循环严格有界（library_bridge.rs:1235-1236、:1276-1302）；近未来 deadline 的注册竞态未覆盖，见 CBH-R1-02。审计表明确把 2370 ms 说明为旧的静态超时参数算术，并不再称作全路径物理 WCET；当前模型是软件超时包络 ≤2400 ms 加系统调用边界（concurrency-lock-audit.md:63-113）。Command/thread spawn、pipe 操作和 kill 等系统调用限制有明示，但对 CancelIoEx 的同步 I/O 能力说明不正确（:143-146）。 |
| CBH-03：残留扫描声明范围 | PARTIAL | 脚本与主日志已缩窄为 runner 后代 + 隔离根；剩余旧标签见 CBH-R1-04。 |
| CBH-04/05：artifact 故障时 exit 与 metadata 独立一致；锁故障真实注入 | PARTIAL | 本轮复跑的 pwsh -NoProfile -File verification/P20-CLOSE-BOUND-HARDEN-1/test-artifact-lock-fault.ps1 为 exit 0；FileShare.None 独占锁是真实文件锁注入，覆盖 console log 与 fallback。它没有覆盖 ac5.exit/metadata 的写失败，也用 MockExitCode 跳过真实桌面进程。 |
| AC7：真实交互桌面直跑 | NOT_RUN | 本轮没有启动桌面应用；这仍须由交互式 Coordinator 运行并记录 exact build/head。 |
| AC8：回归套件 | PASS | 下表为本轮实跑结果，全部 exit 0。 |

### AC8 本轮复跑

环境：PowerShell 7.6.6、Cargo 1.98.1；CARGO_TARGET_DIR 指向新建的 %TEMP% 隔离根，不写入 apps/desktop/src-tauri/target。执行 verification/P20-CLOSE-BOUND-HARDEN-1/run-ac8-regression.ps1 时使用 -TargetDir 指向同一隔离根。

| 回归项 | 命令过滤器 | 退出码 |
|---|---|---:|
| R-008 心跳恢复 | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_heartbeat_detects_unresponsive_child_and_recovers -- --nocapture | 0 |
| R-003 拆环 reap | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_shutdown_breaks_cycle_and_reaps_child_process -- --nocapture | 0 |
| R-006 错误呈现 | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_triggers_restart_and_emits_restarting_status -- --nocapture | 0 |
| MAX_RETRIES=3 | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_caps_retries_and_emits_fatal_after_three_failures -- --nocapture | 0 |
| is_down 写路由/关机写放行 | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop shutdown_writes_core_shutdown_to_sidecar_stdin_without_session -- --nocapture | 0 |
| resilient 9 项 | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel | 0 |
| stdio drop | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop stdio_channel_drop_with_unresponsive_session_completes_in_bounded_time -- --nocapture | 0 |
| shutdown writes | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop shutdown_writes -- --nocapture | 0 |
| 2 MB pipe overflow | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop writer_overflow_pipe_capacity_unblocks_and_cleans_up_on_kill -- --nocapture | 0 |

另行复跑：
- cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop ac1_deadline_cas_concurrent_monotonic_and_zero_expired -- --nocapture：exit 0。
- cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop ac3_child_fallback_forbids_post_deadline_actions -- --nocapture：exit 0。
- cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop ac4_fault_injection -- --nocapture：3 tests passed，exit 0。此结果不能替代真实阻塞 pipe 测试。
- pwsh -NoProfile -File verification/P20-CLOSE-BOUND-HARDEN-1/test-artifact-lock-fault.ps1：exit 0。

## 未能验证项

1. Windows 同步 ChildStdout/ChildStdin 真正阻塞时 CancelIoEx 能否解除、以及 worker 是否在 200 ms 后仍存活；当前 fault injection 只模拟 sleep。
2. 真实桌面 AC7 的窗口关闭、exact build/head、ac5.exit 与 metadata。
3. ac5.exit 和 metadata 自身的文件锁/写失败注入及真实桌面退出结果一致性。
4. CAS 编码后、写入前 deadline 到期的竞态。

## 集成建议

**不可批准集成。** CBH-R1-01 违反 reader/writer 有界退出的核心验收；CBH-R1-02 与 CBH-R1-03 仍有未闭合语义和证据缺口。Task 仍是 ready、delivery_head=null、Canonical Evidence 为空；本报告不代替 Coordinator 更新生命周期元数据，也不授权集成。