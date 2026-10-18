---
task_id: P20-CLOSE-BOUND-HARDEN-1
reviewer: Codex
author: Antigravity
base_commit: a04e4ea78d5b33a0f91efcdc06b396391c4b165e
reviewed_head: 53aac7d69081615fd1ddb90cecab00d5d733a94f
decision: changes_requested
---

# P20-CLOSE-BOUND-HARDEN-1 第三轮独立 Review

## 范围与结论

固定审查交付提交 53aac7d69081615fd1ddb90cecab00d5d733a94f；Task base_commit 为 a04e4ea78d5b33a0f91efcdc06b396391c4b165e。目标代码、任务 AC、R2 Review、返修报告、AC5 审计表及相关脚本均已核对。交付提交包含 Rust 目标文件及对应证据；未见其修改 frontend/**、契约、Schema、ACL 或依赖。

**结论：changes_requested，不可批准集成。** AC8 九项本轮实跑全通过；线程句柄正常清理、artifact 文件间一致性断言及 32 次 CAS 循环均有进展。但 AC4 的 JoinHandle 仍可在 registry 锁超时分支被丢弃，registry 没有容量上限且生产代码没有调用收割函数；CAS 上限耗尽时也未保证 sentinel 写入共享状态。AC7 真实交互桌面直跑保持 NOT_RUN。

指定 Task metadata commit 39abea258a69888df5522ce22c601e0d37e6d4ff 在当前 Git object database 中不可解析（git cat-file exit 128）。以下 Task 内容核对基于工作区文件；该文件相对 reviewed_head 无工作区差异，delivery_head 指向本次 reviewed_head。

## Architecture

本次生产代码变更限于 Tauri/Rust 侧 library_bridge.rs，未发现越过 React/Tauri/Python/SQLite 边界的新增行为，也未发现共享契约或依赖变更。仍未解决的 worker 生命周期问题触及 Task AC4 的关闭边界，不能以分层合规替代该项验收。

## R2 五项闭环核对

| 上轮项目 | 结论 | 依据 |
|---|---|---|
| ① Worker 取消失败路径 / AC4 | FAIL，P1 未闭环 | library_bridge.rs:1391-1416 返回结构化双 API 结果，但 registry 锁获取失败会丢弃传入 JoinHandle，且生产没有调用 registry 收割函数，见 Findings R3-01。 |
| ② duplicated thread HANDLE 泄漏 | PASS（结构检查） | reader/writer cleaner 与 Channel Drop 均用 swap(0) 后 CloseHandle，library_bridge.rs:1735-1751、1843-1859、3673-3689。 |
| ③ CAS 重试上限 | PARTIAL，P2 | 初始及过期 sentinel 循环均最多 32 次；但耗尽时没有确认共享 atomic 已写入 sentinel，见 Findings R3-02。 |
| ④ artifact 一致性断言 | PARTIAL，P2 | Case 5–9 增加文件间与启动的 PowerShell runner 退出码断言，入库 artifact-lock-fault.exit 为 0；Case 9 比对的仍是 runner 退出码，不是桌面子进程退出码，见 Findings R3-03。 |
| ⑤ AC5 审计表缺口 | FAIL，P2 | 表已补充 worker/cancel 说明，但仍有 CloseHandle 行号错误，并把未设容量、未被生产调用的 registry 描述为有限收割，见 Findings R3-04。 |

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R3-01 | P1 | apps/desktop/src-tauri/src/library_bridge.rs:1447-1465、1486-1523、3517、3531、3632、3646 | track_unreaped_worker 按值接收 JoinHandle；registry 锁在 50 ms 内取不到时只记录日志，函数返回即 drop handle，Rust 会 detach 仍可能阻塞的 worker。registry 是无容量上限的 Vec；生产调用点只有 track，reap_unreaped_workers 仅在测试 8516 调用，故失败 worker 没有自动收割或有限生命周期保证。 | 对照全文件 reap_unreaped_workers( 调用结果：定义 1486 与测试 8516；锁超时分支 1463-1465。 | 锁竞争失败时仍须保留 handle；给 registry 设明确容量/背压并接入生产收割路径，覆盖锁超时、取消失败及长期阻塞故障注入。 | open |
| R3-02 | P2 | apps/desktop/src-tauri/src/library_bridge.rs:1290-1315、1321-1330、8092 | 重试次数现有明确上限 32；但 sentinel CAS 连续失败 32 次后无成功标记或共享状态回读校验，仍直接返回 created_at。共享 atomic 可能保留更晚 deadline，其他关闭路径仍读到旧值；初始注册循环的上限耗尽分支也只生成本地 committed 值。 | ac1_deadline_cas_expired_during_pause_writes_sentinel_1_and_returns_zero_budget 覆盖暂停后成功置 sentinel，不覆盖连续 32 次 CAS 失败。 | 明确上限耗尽时共享 deadline 的安全语义，并加入确定性 CAS 冲突/耗尽测试；不能只证明循环退出有界。 | open |
| R3-03 | P2 | verification/P20-CLOSE-BOUND-HARDEN-1/test-artifact-lock-fault.ps1:306-318、327-340、349-360；verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1:144-149、190-203 | Case 9 启动的 proc9a/proc9b/proc9c 是 pwsh runner。runner 等待桌面子进程退出，但不读取其 ExitCode；无残留时固定把 scriptExitCode 设为 0。因此当前断言只证明 artifact 与 runner 退出码相等，未证明与 m2rc1-desktop.exe 实际退出码相等。artifact-lock-fault.exit=0 不能闭合该要求。 | 将桌面子进程设为非零退出但在时限内正常退出即可暴露：runner 仍走 190-203 的成功分支并写 0。该故障用例尚未存在。 | runner 记录并传播桌面子进程实际 ExitCode，再断言 primary/fallback exit、metadata 与其一致；保留 Mock 与真实子进程两类用例。 | open |
| R3-04 | P2 | verification/P20-CLOSE-BOUND-1/concurrency-lock-audit.md:21-25、111、132-145；apps/desktop/src-tauri/src/library_bridge.rs:1447-1465、1744-1749、1852-1857、3676-3688 | 审计表 line 111 将 CloseHandle 标在 3629/3635，当前源码实际为 worker cleaner 1744/1852 与 Channel Drop 3676/3681/3687。表 24 行称未回收 registry 有限，但源码无容量上限；表 132-133 声称可通过主动收割，未注明生产路径没有调用者，亦未覆盖锁超时丢 handle 分支。故 AC5 调用点/worker lifetime 审计仍与源码不完全一致。 | 直接对照所列行号及 reap_unreaped_workers( 全文件调用点。 | 更正 CloseHandle 行号，逐项纳入 registry 容量、锁失败、生产收割调用链及真实 worker 最坏存活边界。 | open |

## Verification

### AC8：本轮实际复跑

环境：Windows PowerShell 7.6.6；cargo 1.98.1；rustc 1.98.1。新建隔离目录 C:\Users\49745\AppData\Local\Temp\P20-CLOSE-BOUND-HARDEN-1-r3-c6dbee8f807d462db2f6ae138396d625。Cargo target 与 runner 逐项 stdout/stderr/exit 均写入该临时目录；未写回仓库证据目录。

执行命令：

- $env:CARGO_TARGET_DIR = C:\Users\49745\AppData\Local\Temp\P20-CLOSE-BOUND-HARDEN-1-r3-c6dbee8f807d462db2f6ae138396d625\cargo-target
- pwsh -NoProfile -File verification/P20-CLOSE-BOUND-HARDEN-1/run-ac8-regression.ps1 -TargetDir C:\Users\49745\AppData\Local\Temp\P20-CLOSE-BOUND-HARDEN-1-r3-c6dbee8f807d462db2f6ae138396d625\ac8
- runner exit：0

| 回归项 | 实际 cargo test 命令 | Exit |
|---|---|---:|
| R-008 心跳恢复 | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_heartbeat_detects_unresponsive_child_and_recovers -- --nocapture | 0 |
| R-003 拆环与 reap | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_shutdown_breaks_cycle_and_reaps_child_process -- --nocapture | 0 |
| R-006 错误呈现 | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_triggers_restart_and_emits_restarting_status -- --nocapture | 0 |
| MAX_RETRIES=3 | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_caps_retries_and_emits_fatal_after_three_failures -- --nocapture | 0 |
| is_down 写路由 | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop shutdown_writes_core_shutdown_to_sidecar_stdin_without_session -- --nocapture | 0 |
| resilient 9 项 | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel | 0 |
| stdio drop | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop stdio_channel_drop_with_unresponsive_session_completes_in_bounded_time -- --nocapture | 0 |
| shutdown writes | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop shutdown_writes -- --nocapture | 0 |
| 2 MB pipe overflow | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop writer_overflow_pipe_capacity_unblocks_and_cleans_up_on_kill -- --nocapture | 0 |

九条命令全部 exit 0；六个单测命令各 1 passed，resilient suite 为 9 passed，shutdown_writes 为 2 passed；各次均 0 failed、0 ignored。存在测试过滤项（147–155 filtered out），它们不是 skipped 项。

### AC7、artifact fault、Canonical Evidence 与环境收尾

| 检查 | 结论 | 证据 |
|---|---|---|
| AC7 真实交互桌面直跑 | NOT_RUN | 本轮未执行交互式桌面直跑；artifact lock suite 不替代该 Gate。 |
| Artifact fault suite | 子项 PASS；进程码一致性仍 PARTIAL | 交付证据 verification/P20-CLOSE-BOUND-HARDEN-1/artifact-lock-fault.exit 为 0，stdout 显示 Case 5–9 全部断言通过；但 Case 9 的 proc 是 PowerShell runner，见 R3-03。 |
| 现有 Canonical Evidence pins | PASS，124/124 | 对 Task 表内 124 个路径逐个以 Get-FileHash SHA256 按磁盘真实字节计算，并以 git ls-tree 验证唯一 pin commit 53aac7d69081615fd1ddb90cecab00d5d733a94f 包含全部路径；哈希与 pin 全部匹配。 |
| Governance check | PASS，exit 0 | pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-CLOSE-BOUND-HARDEN-1.md；创建 Review 前 exit 0、有 2 项体量预算警告（STATUS、REBASELINE_PLAN）；创建后复跑 exit 0、有 3 项警告（新增本 Review 未登记在 evidence_dir）。受本轮只写 Review 的授权限制，未更新 Task pin；Task 的 canonical_evidence_status 仍为 pending。 |
| 目标进程收尾 | PASS | m2rc1-desktop、core_service、host_bridge 均未发现运行进程。 |

本 Review 本身未加入 Task Canonical Evidence 表，因为本次授权只允许写 Review 文件。AC8 本轮临时日志留在上述隔离 TEMP 根目录，Review 记录了完整命令、环境及逐项退出码。

## 结论与复审

reviewed_head 53aac7d69081615fd1ddb90cecab00d5d733a94f **不可批准集成**。阻断项为 AC4 P1 worker 生命周期缺口；AC1 sentinel 耗尽语义、AC7 实际子进程退出码断言及 AC5 审计准确性仍有 P2 缺口。AC7 真实交互桌面验证仍为 NOT_RUN，不得记 PASS。

建议下一步由 Antigravity 返修 R3-01 至 R3-04，交付新 head 和对应测试证据；随后由 Coordinator 在真实交互桌面执行 AC7。