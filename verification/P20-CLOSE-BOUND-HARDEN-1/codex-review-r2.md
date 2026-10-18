---
task_id: P20-CLOSE-BOUND-HARDEN-1
reviewer: Codex
author: Antigravity
base_commit: a04e4ea78d5b33a0f91efcdc06b396391c4b165e
reviewed_head: ed737b5d262d6f7d7b07d8b70900d6af71c11b3c
decision: changes_requested
---

# P20-CLOSE-BOUND-HARDEN-1 第二轮独立 Review

## 范围与结论

复审固定实现提交 ed737b5d262d6f7d7b07d8b70900d6af71c11b3c；Task/Handoff 元数据提交为 1f4c6a6f0431bd443765ef98d355299c05a2088a，当前 HEAD 与其一致。目标代码在元数据提交中未再变化。读取了上一轮 Review、Task AC、Handoff、返修 diff、相关调用链、测试和审计表。

**结论：changes_requested；不可批准集成。** R1-01 的 worker 生命周期与取消失败路径仍未闭环；另有线程句柄泄漏、过期 sentinel 更新没有硬重试上限、artifact 故障一致性断言不完整，以及 AC5 审计表未随代码更新。AC7 仍为 NOT_RUN。

## 逐项结论

| 项目 | 结论 | 依据 |
|---|---|---|
| CBH-R1-01 / AC4 | **FAIL，未闭环** | 已加入 CancelSynchronousIo，且本轮真实 pipe 阻塞与直接取消测试均通过；但生产路径丢弃取消结果，句柄复制失败未处理，超时 worker 没有有限、可观测的最终回收；reaper 创建失败时仍会丢失 JoinHandle。详见 Finding CBH-R1-01。 |
| CBH-R1-02 | **指定修复 PASS；AC1 整体 PARTIAL** | 代码在注册后检查原 deadline，过期时尝试单调写 sentinel 1 并返回零预算；可控暂停测试本轮通过。该新增 fetch_update 没有 32 次重试上限，违反 AC1 单次调用硬上界，详见 Finding CBH-R2-01。测试 hook 实际在 encode_deadline 之前触发（源码 1282-1288；测试注释 7920-7923 称在编码与 CAS 之间），虽能令候选 deadline 在 CAS 前过期并断言 sentinel，但注释位置不准确。 |
| CBH-R1-03 | **PARTIAL** | ac5.exit 与 JSON metadata 各有独占锁注入和 fallback 路径；但 Case 5/6 使用 MockExitCode，未在各故障用例中成对比较所有落盘 exit 值、metadata exit_code 与实际进程退出码。真实二进制 Case 9 只锁定 console log。详见 Finding CBH-R1-03。 |
| CBH-R1-04 | **PASS** | test-ac1-overlay-bound.ps1:348 和 ac2-process-tree-audit.meta.json:2 均使用 Runner Descendants & Isolation Root Audit；指定的旧 Broken-Chain Orphan Audit 标签已消失。 |
| AC5 并发审计 | **FAIL** | concurrency-lock-audit.md 未出现在本轮实现提交变更列表中，仍称仅使用 CancelIoEx、保留旧源码行号，并声称 CAS 更新严格 32 次。详见 Finding CBH-R2-03。 |
| AC7 桌面直跑 | **NOT_RUN** | Handoff 仍将交互式桌面直跑标为 NOT_RUN；未有 exact build/head 的桌面运行产物。 |
| AC8 回归 | **PASS** | 本轮实际执行脚本及其 9 个回归命令，runner 与每项命令退出码均为 0；resilient suite 为 9 passed、0 failed。 |
| Canonical Evidence | **PASS（按仓库实表）** | 当前 Task 实表有 123 个 pin（Handoff 同样记 123；与任务请求中的 145 不一致）。逐项按磁盘真实字节计算 SHA-256，123/123 匹配；逐项验证对应 commit 含该 path，123/123 存在。 |

## Findings

### CBH-R1-01 — P1 — 同步 I/O 取消与失败 worker 生命周期仍不满足 AC4

实现已添加 CancelSynchronousIo：apps/desktop/src-tauri/src/library_bridge.rs:1367-1402。但关闭主路径 :1840-1856 和 reader/writer reaper :3342-3348、:3436-3442 都以 let _ = cancel_worker_io(...) 丢弃取消状态与错误码；DuplicateHandle 失败时 :1680-1682、:1772-1774 也只是不存 handle、不报告失败。直接取消测试 :8031-8035、:8148-8153 接受 ioex_canceled || sync_canceled，因此没有断言同步取消确实成功。

200 ms reaper 超时后，worker JoinHandle 会在 :3362-3369、:3456-3463 放入 UNREAPED_WORKER_HANDLES（定义及存储函数 :1424-1429）。该静态 Vec 没有 drain、join、查询或重试消费者，不能证明阻塞 worker 最终结束；track_unreaped_worker_handle 的普通 Mutex lock 也没有期限。若 reaper 的 Builder::spawn 失败，错误分支在 :3373-3380、:3467-3474 运行，而闭包拥有的原 worker JoinHandle 随失败闭包销毁，worker 被 detach。

本轮实跑的 pipe 阻塞和取消测试通过（见验证表），说明当前环境下测试路径可结束，但未覆盖取消失败、DuplicateHandle 失败、reaper spawn 失败或未回收 worker。AC4 要求所有 worker 可安全取消并确认结束，或提供明确、有限且可观测的替代生命周期；当前实现未达到要求。修复需处理并传播取消结果，对句柄复制失败采取可验证的失败策略，并让超时/重试及 reaper 创建失败路径保留且最终回收 worker。

### CBH-R2-01 — P2 — 过期 sentinel 更新绕过 CAS 硬重试上限

初始注册循环在 :1290-1308 最多尝试 32 次，但新增过期分支 :1316-1324 使用 AtomicU64::fetch_update，该操作在竞争下会内部重试，没有受 MAX_DEADLINE_CAS_RETRIES 限制。极端并发更新时，调用仍可能超出 AC1 要求的单次硬上界；审计表 concurrency-lock-audit.md:135 的“CAS 更新受 32 次硬约束”因此不准确。应把 sentinel 更新也纳入显式有限次 CAS，并定义达到上限时不延长 deadline 的结果。

### CBH-R2-02 — P2 — worker 正常退出时泄漏 duplicated Windows thread HANDLE

reader/writer 在线程内用 DuplicateHandle 建立拥有所有权的线程 HANDLE（:1669-1682、:1761-1774）。正常 worker 退出时 Cleaner 只把两个 atomic slot 清零（:1641-1648、:1733-1740），没有调用 CloseHandle；随后 channel Drop 在 :3499-3508 交换到的已是 0，无法关闭该 HANDLE。因此每个正常结束的 channel 生命周期最多泄漏两个 Windows HANDLE；反复重启/关闭会累积内核句柄。Cleaner 应以原子交换获取并关闭拥有的句柄，同时避免与 Drop 双重关闭。

### CBH-R1-03 — P2 — exit 与 metadata 故障用例未证明完整的跨 artifact / 真实退出码一致性

独占锁与 fallback 用例已新增：Case 5 锁 ac5.exit 并检查 ac5.exit-fallback 内容（test-artifact-lock-fault.ps1:145-174）；Case 6 锁 ac5-metadata.json 并读取 ac5-metadata-fallback.json（:177-200）。备用路径也已明确实现：run-desktop-close-verification.ps1:235-265、:305-348。

但 Case 5/6 分别通过 -MockExitCode 0 启动（测试 :156、:188），Case 5 没有断言 metadata 的 exit_code 等于子进程真实退出码；Case 6 只断言 fallback metadata 的 exit_code 为 0 和 exit_written 为 true，没有读取 primary ac5.exit 并与之比较。真实二进制 Case 9（:265-301）只锁 console log，没有在 exit 或 metadata 写失败场景核对真实退出码。故障套件日志虽记 exit 0，但现有断言不足以覆盖 AC7 的一致性条件。补齐每种失败下 primary/fallback exit、metadata exit_code 和启动进程 ExitCode 的逐项相等断言，并至少以实际进程退出路径验证。

### CBH-R2-03 — P2 — AC5 并发审计未对应本轮源码

verification/P20-CLOSE-BOUND-1/concurrency-lock-audit.md:20-24 仍声称取消仅靠 CancelIoEx；:34 及 worker 表 :127-128 保留旧源码行号；:135 声称所有 CAS 更新严格受 32 次限制；:145 仍只讨论 CancelIoEx。当前源码新增 CancelSynchronousIo、DuplicateHandle、全局 unreaped handle 存储及 fetch_update；这些调用点和失败生命周期未进入审计表。该文件不在 ed737b5d 的变更路径中。AC5 要求与源码调用点一对一并说明 worker lifetime，因此此项未通过。

## 验证记录

环境：Windows PowerShell 7.6.6、Cargo 1.98.1、rustc 1.98.1。Cargo target 与脚本输出均置于新建的隔离目录：C:/Users/49745/AppData/Local/Temp/P20-CLOSE-BOUND-HARDEN-1-r2-51d01ca1ebef4ba6bb3c91cbde8849f7。没有遇到 Cargo 锁；未覆盖版本化证据文件。

### AC8 本轮实跑

总命令：pwsh -NoProfile -File verification/P20-CLOSE-BOUND-HARDEN-1/run-ac8-regression.ps1 -TargetDir C:/Users/49745/AppData/Local/Temp/P20-CLOSE-BOUND-HARDEN-1-r2-51d01ca1ebef4ba6bb3c91cbde8849f7/ac8-rerun；CARGO_TARGET_DIR 指向同一隔离根下的 cargo-target；runner exit 0。

| 回归项 | 实际 cargo test 命令 | Exit |
|---|---|---:|
| R-008 心跳恢复 | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_heartbeat_detects_unresponsive_child_and_recovers -- --nocapture | 0 |
| R-003 拆环与 reap | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_shutdown_breaks_cycle_and_reaps_child_process -- --nocapture | 0 |
| R-006 错误呈现 | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_triggers_restart_and_emits_restarting_status -- --nocapture | 0 |
| MAX_RETRIES=3 | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_caps_retries_and_emits_fatal_after_three_failures -- --nocapture | 0 |
| is_down 普通写拒绝 / 关机写放行 | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop shutdown_writes_core_shutdown_to_sidecar_stdin_without_session -- --nocapture | 0 |
| resilient suite | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel | 0；9 passed |
| stdio drop | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop stdio_channel_drop_with_unresponsive_session_completes_in_bounded_time -- --nocapture | 0 |
| shutdown writes | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop shutdown_writes -- --nocapture | 0 |
| 2 MB pipe overflow | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop writer_overflow_pipe_capacity_unblocks_and_cleans_up_on_kill -- --nocapture | 0 |

### 本轮其他检查

| 检查 | 命令 | 结果 |
|---|---|---|
| Reader/writer 实际 pipe 阻塞 | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop ac4_fault_injection_blocked_ -- --nocapture | Exit 0；2 passed |
| 直接同步取消测试 | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop ac4_cancel_ -- --nocapture | Exit 0；2 passed |
| CAS 过期竞态 | cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop ac1_deadline_cas_expired_during_pause -- --nocapture | Exit 0；1 passed |
| artifact lock fault suite | 本轮 NOT_RUN；审阅了提交内的 artifact-lock-fault.exit（内容 0）与 stdout（报告 9 个 fault case 均 PASS），并复核了断言源码；上列 CBH-R1-03 说明尚存的断言缺口。 |
| AC7 交互桌面直跑 | NOT_RUN；Handoff doc/handoffs/P20-CLOSE-BOUND-HARDEN-1-antigravity.md 仍标 NOT_RUN。 |
| 权威文档检查（写 Review 前） | pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-CLOSE-BOUND-HARDEN-1.md | Exit 0；PASS，2 个体量警告（STATUS 与 REBASELINE_PLAN）。 |
| 权威文档检查（写 Review 后） | 同上 | Exit 0；PASS，3 个警告；新增项为本 Review 文件未登记在 Task evidence_dir。受本轮唯一写入范围限制，未更新 Task pin。 |
| 目标进程收尾 | 查询 m2rc1-desktop、core_service、host_bridge 精确进程名及 Python 入口名 | 未发现运行中的目标进程。 |

## 集成决定

当前固定 head **不可批准集成**。未解决的 P1 CBH-R1-01 已触及 AC4 的关闭硬边界；AC1、AC5 仍有 P2 缺口，AC7 关键桌面验证未执行。Task 仍处于 in_review；本 Review 不修改 Task/STATUS，也不代替后续状态登记。

## 下一步与可转发指令

下一步由 Antigravity 继续本 Task 返修；Task 状态须按生命周期流程进入 changes_requested / in_progress 后再实施。恢复点为 G:/CODEX/New Manga、branch main、当前 HEAD 1f4c6a6f0431bd443765ef98d355299c05a2088a；Owner=Antigravity、Reviewer=Codex。允许范围沿用 Task：apps/desktop/src-tauri/src/library_bridge.rs、verification/P20-CLOSE-BOUND-1/**、verification/P20-CLOSE-BOUND-HARDEN-1/** 及 Task/Handoff；禁止触碰前端、verification/P20-AC4-FPS-1/**、契约/Schema/ACL/依赖和 .qoder-credits/report.json。

可直接转发：

> Antigravity：请在 P20-CLOSE-BOUND-HARDEN-1 按 changes_requested 返修，恢复点为 G:/CODEX/New Manga、branch main、当前 HEAD 1f4c6a6f0431bd443765ef98d355299c05a2088a。先按生命周期流程将 Task 恢复至 in_progress；不得扩大 Task 范围。闭合 P1 CBH-R1-01（传播并处理 CancelSynchronousIo 结果、DuplicateHandle/reaper 失败及 worker 最终回收），修复正常退出时 duplicated thread HANDLE 泄漏，令 sentinel CAS 也受显式重试上限约束，补齐 exit/metadata 与实际进程退出码的一致性故障断言，并更新 concurrency-lock-audit.md 使调用点和 worker lifetime 对应当前源码。更新 Handoff 和 Canonical Evidence；重跑 AC4、AC8 与 artifact fault suite，逐项记录 command、shell/环境、stdout/stderr/exit。AC7 仍需在交互式桌面补跑。不要修改前端、verification/P20-AC4-FPS-1/** 或 .qoder-credits/report.json，也不要修改契约、Schema、ACL 或依赖；提交新 delivery head 后交 Codex 独立复审。