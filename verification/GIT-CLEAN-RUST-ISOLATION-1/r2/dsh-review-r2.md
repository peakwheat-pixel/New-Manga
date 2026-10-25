---
task_id: GIT-CLEAN-RUST-ISOLATION-1
reviewer: DeepSeek Harness
author: ZCode（Codex 接收修正并代跑验证）
base_commit: e34a90d001cce1fa966aec7d2b032bb5ad1cf148
reviewed_head: 1829a38a41587a0d680001a40d206886afb0911d
parent_commit: 3b035365682db0965bbde4b0a6113e3e000ae7e7
decision: blocked
---

# Review r2：GIT-CLEAN-RUST-ISOLATION-1

Reviewer：DeepSeek Harness（独立只读复审；未实现、未改 Task/源码/文档/旧证据/manifest/refs/ACL，未 push/done/集成/清理）。
Session：`session-18334d70-a233-467c-8159-2c90e6203409`（上一轮 r1 的 Review 字节保留；本轮是新 head、新 Appointment，不沿用旧结论）。
审查对象只限 `reviewed_head` `1829a38a41587a0d680001a40d206886afb0911d` 的独立 implementation artifact。它不是 main 集成，也不是父候选升级；任何 head 变化后本 Review 自动成为历史。

## 范围与依据

- 实现仓库：`G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/source-r2`，branch `codex/git-clean-rust-isolation-r2`，HEAD `1829a38a…`，parent `3b035365…`，累计 base `e34a90d…`；`git remote -v` 为空，`git status --porcelain` 为空。
- 源 main 固定 `349e61faff5f93067af5d4ce2d9e394e0d665b8c`；父候选/父审查仍 r1 blocked；本 Task 仍 `in_review`。本 Review 不改变这些指针。
- r2 相对 parent 只改两个文件：`library_bridge.rs`、`multichannel_stress_tests.rs`；`main.rs` 未改（SHA 与 r1 相同 `b315e632…`）；`Cargo.toml`、共享契约、Python Core、React/frontend、依赖均未改。
- 已读：主仓 `AGENTS.md`、`doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md`、`doc/STATUS.md` 当前段、`doc/REBASELINE_PLAN.md` 当前 DAG、`doc/tasks/GIT-CLEAN-RUST-ISOLATION-1.md`、`doc/templates/REVIEW.md`、`r2/APPOINTMENT.md`、`r2/SCOPE.md`、`r2/CODEX_VALIDATION.md`、`r2/RECEIVER_NOTES.md`、`r2/checkpoint-current.md`、`r2/RESULT.md`、`r2/HANDOFF.md`、`review-package-r2/PACKAGE_MANIFEST.json`、`SOURCE_TREE.json`、`codex-validation-r2/` 日志与 `codex_verify_r2.py`。
- Owner 的 `RESULT.md`/`HANDOFF.md` 明确是“未编译/未运行/HTTP429/exit1”的来源阶段；`zcode-delivery-r2` 是原始快照。最终运行事实以 `1829` 源码、Codex 运行器与 `codex-validation-r2` 为准。Owner 预期不作为实测通过。
- 未审/未运行：packaged sidecar、安装包、模型、GUI/WebView、release、main 集成。它们不作为本 Review 的 PASS。

### 独立核查动作（只读）

- `git rev-parse HEAD`、`git status --porcelain`、`git diff --name-status 3b03536..1829a38`、`git show --stat`、`git remote -v`、`git log`。
- `PACKAGE_MANIFEST.json` 59 个文件逐一重算 SHA256：59/59 匹配，0 mismatch/missing（manifest 不含自身，符合其说明）。
- `SOURCE_TREE.json` 734 个文件逐一重算 SHA256：734/734 匹配，0 mismatch/missing；head 字段为 `1829a38…`。
- Task Canonical Evidence 66 行（EV-001..EV-066）逐一重算路径 SHA256：66/66 匹配，0 mismatch/missing。
- 三个实际 Rust 文件 SHA256 与 manifest、`source-fixed-r*.json` 的 `rust_source_sha256` 一致：`library_bridge.rs=145a6a2a…`、`multichannel_stress_tests.rs=dd2dfeaa…`、`main.rs=b315e632…`。
- 静态计数：head 171 tests = base 166 + 5 压力测试；实际 ignored 6 个（1 个旧 perf + 5 个专用 stress）；`packaged_sidecar_tests.rs` 12 个；默认 `running 159 = 153 可执行 + 6 ignored`，12 filtered。
- 未重跑旧 3b 默认失败（已两次上限）、当前 fault 同条件失败或任何全套；只核验已记录的运行、源码与哈希。

## Architecture

### 结论摘要

**生产边界：PASS（静态检查范围）。** `with_unreaped_registry` 的 `cfg(not(test)) #[inline]` 版本只调用 `f(&UNREAPED_WORKER_REGISTRY)`；`track_unreaped_worker`、`unreaped_worker_count`、`reap_unreaped_workers` 的生产目标仍是同一个进程级 registry。`MAX_UNREAPED_WORKERS=32`、锁超时/10 次尝试、容量满时 cancel/prune、拒绝时保留 handle、holder 无限退避、Drop/shutdown 的 kill/join/reap 预算均未改。`main.rs` 未改，`Cargo.toml`/契约/依赖零改动；新增的 `kill_and_wait_for_test`、`process_handle_for_test`、`resources_for_test`、holder 继承、fail-closed 观察均为 `cfg(test)`。生产 `cargo check` exit0。

**测试隔离：显著改善，正常路径可接受。** R004 现在让 holder 通过 thread-local 继承同一 `Arc<Mutex<Vec<UnreapedWorker>>>`，ac1 在持锁期间 spawn holder、等待真实锁超时、释放后在同一 registry 观察注册；R005 在 override 槽读失败且 `IN_REGISTRY_TEST` 时 panic，安装/清除读回验证；R006 用 Arc 替代 `Box::leak`，guard drop 显式 `reap_now`。这解决了 r1 的“holder 走全局、同 registry 关系断开”和“静默回退 global”的核心问题；默认两轮 153/0/6/12 支持该判断。剩余问题集中在异常/未完成 worker 的 guard 清理，以及新增观察断言强度（见 Findings），不是生产 registry 语义变化。

**AC3 的饱和设计：仍未达成。** r2 的 fault 注入确实变成了真实阻塞：20/20 请求 `stdin write timed out`（约 3.0s），20/20 在超时后 writer/reader 都未结束；Drop 后 20/20 自有进程句柄 signaled、PID 消失、worker finished+joined、四个 pipe/thread handle 槽为 0。但生产 Drop 先杀 child + cancel pipes，writer/reader 在 join 窗口内结束，**没有 worker 进入 unreaped registry**，`peak_registry=0`，故 `peak>=32` 失败、exit101。机制上这是“未泄漏 worker”的设计结果，不是饱和证据；AC3 仍 BLOCKED。不能把 20 个成功往返、资源回收通过或 `0<=32` 当容量通过。

### 分层、契约、依赖与安全

- 没有越过 AD-001：没有 Python Core、React/WebView、SQLite、Managed Copy、共享接口/Schema/依赖改动。
- 真实 Core 场景使用本副本 `src`、`C:/Python314/python.exe`、per-channel 临时 DB/数据根，数据/`APPDATA`/`LOCALAPPDATA`/`TEMP`/`TMP` 在本 Task r2 环境；未使用用户素材或真实用户库。
- 故障 sidecar 是明确标记的 `FAULT_INJECTION_FAULT_SIDECAR_NOT_REAL_CORE` 真 OS 进程/真管道，不是真实 Core；与真实 Core 场景分开记录。
- 未发现新的依赖、契约、系统 ACL 或生产持久化路径修改；没有 push/集成/done。

### 测试隔离与资源观察的真实性

1. **同 registry holder**：`spawn_persistent_holder` 在 test build 通过 `current_thread_override_registry()` 把当前 guard 的 Arc 传给 holder 线程；holder 在 `track_unreaped_worker` 中先查 `TEST_THREAD_REGISTRY`，命中后使用同一 registry。ac1 在锁仍持有时 spawn holder，等待 `TEST_HOLDER_LOCK_TIMEOUTS>0`，再检查锁内无 `ac1-holder`，释放后通过 `snapshot_names()` 在同一 registry 观察到注册。该证明成立，R004/R005 的核心缺口关闭。
2. **生产选择**：`with_unreaped_registry` 在 `Some(slot)` 且 owner 为当前线程时用私有 registry；非 owner/生产方式走 global；`None` 且 `IN_REGISTRY_TEST` 时 panic。所有 `cfg(not(test))` 路径只走 global，生产等价。
3. **Windows 身份**：`OwnedProcessHandle` 复制 `Child` 的进程句柄，使用 `GetProcessTimes` 读 OS 创建时间、`WaitForSingleObject` 等待确切进程对象；`tasklist` 作为次要探测，检查 `tasklist` exit status，失败按“仍存活”fail-safe。每 channel 的 reader/writer finished/joined 与 pipe/thread handle 槽都被观测并断言。该设计避免了“测试墙钟 + PID”被复用混淆，R003 的核心真实性成立。
4. **仍有残余**：
   - `RegistryTestGuard::drop` 只 `reap_now(2s)`，未对 `remaining` 断言；未完成的 worker 会被打印后 detach，若异常/panic 时仍有 holder 持有 Arc，私有 registry 可能晚于 guard 存在。正常路径（ac1/ac2/ac4）已通过，但“所有异常路径都无 detach”未被证明。
   - fault 场景把 `writer_unfinished`/`reader_unfinished` 打印出来，但测试没有断言它们或 `stdin write timed out` 错误码；`res.is_err()` 仍是唯一硬断言。日志具有很强的判别力，但测试本身不强制。
   - `threads_spawned/joined` 只打印，`channel_reader_writer_threads` 是计算常量；真正的 per-channel flags/handles 已断言，但“线程账本全部相等”不是断言。
   - `child_lock` 测试的 `tasklist` 调用仍不检查自身 exit status（压力测试的 `pid_still_alive` 已检查）；若 tasklist 失败，孙进程消失可假性通过。该检查是既有的，r2 未完全收紧。

### Architecture 结论

测试隔离架构和 Windows 资源观察比 r1 明显更真实，生产路径在静态检查中保持不变；没有证据表明 r2 改了 MAX/锁/背压/holder/kill 预算。但 AC3 的饱和边界仍未触及，guard 异常清理和 fault 断言强度还有残余，不能据此给可集成结论。

## Verification

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| head/分支/父提交/远端 | `git rev-parse`、`git branch`、`git rev-list --parents`、`git remote -v`、`git status` | `1829a38`，parent `3b03536`，branch `codex/git-clean-rust-isolation-r2`，无 remote，worktree clean | PASS | 本次独立 Git 输出；提交只改 2 文件 |
| 59 文件包 | 对 `PACKAGE_MANIFEST.json` 逐文件 `Get-FileHash` | Review 时点 | PASS：59/59 | `review-package-r2/PACKAGE_MANIFEST.json` |
| 734 文件源码树 | 对 `SOURCE_TREE.json` 逐文件 `Get-FileHash` | Review 时点 | PASS：734/734 | `review-package-r2/SOURCE_TREE.json` |
| Task EV-001..066 | 逐行路径 SHA256 重算 | Review 时点 | PASS：66/66 | `doc/tasks/GIT-CLEAN-RUST-ISOLATION-1.md` |
| 源码绑定 | 三个 Rust 文件对照 manifest/日志 | `1829a38` 工作树 | PASS：`145a6a2a…`、`dd2dfeaa…`、`b315e632…` | `source-fixed-r*.json` |
| 接收编译 | `cargo test --locked --offline --no-run` | 3b + dirty，exit0；编译输入 SHA 与最终 1829 相同 | PASS（接收阶段） | `compile-reception-r1.log`；`compile-reception-r1.json` |
| 生产 check | `cargo check --locked --offline` | `1829a38`，生产配置，exit0 | PASS | `production-check.log` 末尾 `EXIT=0` |
| 默认并发 r1 | `cargo test --locked --offline -- --skip packaged_sidecar_tests::`，默认并发，unset `RUST_TEST_THREADS`/`M2RC1_PACKAGED` | `1829a38`，exit0，12.68s | PASS：153 passed / 0 failed / 6 ignored / 12 filtered | `source-fixed-r1.log` 尾部；`source-fixed-r1.json` |
| 默认并发 r2 | 同 r1，未改源码/输入 | `1829a38`，exit0，12.68s | PASS：153 passed / 0 failed / 6 ignored / 12 filtered | `source-fixed-r2.log` 尾部；`source-fixed-r2.json` |
| 真实 Core 1 channel 正常关停 | `--ignored … --exact`，真实 `StdioLibraryChannel` + Python Core | `1829a38`，exit0 | PASS（场景）：1 passed / 170 filtered；ping_ok=true；worker flags true、handle 槽 0、handle signaled、pid gone | `stress-real-1.log` |
| 真实 Core 8 channels 正常关停 | 同上 | `1829a38`，exit0 | PASS（场景）：1 passed / 170 filtered；8/8；OS/worker checks 8/8 | `stress-real-8.log` |
| 真实 Core 20 channels 正常关停 | 同上 | `1829a38`，exit0 | PASS（场景）：1 passed / 170 filtered；20/20；OS/worker checks 20/20 | `stress-real-20.log` |
| 真实 Core 20 并发取消 | `kill_and_wait_for_test` + Drop，独立进程 | `1829a38`，exit0 | PASS（场景）：1 passed / 170 filtered；20/20 kill/wait true、drop_completed、handle signaled、pid gone | `stress-cancel-20.log` |
| 故障 sidecar 20 真实管道阻塞 | `--ignored … --exact`，4MB，fault sidecar | `1829a38`，exit101，26.86s（wrapper 27.38s） | FAIL（AC3 BLOCKED）：20/20 `stdin write timed out` 约 3s，20/20 writer/reader unfinished；`assert_pid_gone` 的 20/20 句柄/PID/worker 检查先于 peak 执行并通过；`peak_registry=0 <32`，`reaped=0`，`remaining=0`（日志值；`remaining==0` 断言在 peak 之后未执行）；边界断言失败 | `stress-fault-20.log`；`stress-fault-20.json` |
| packaged 12 | 默认命令 `--skip packaged_sidecar_tests::` | `1829a38` | NOT_RUN（12 filtered） | `source-fixed-r*.log`；未从本 head 新建冻结 sidecar |
| frontend 前置 | `npm ci --offline` 直接执行、`npm run build`；第一次 cmd 包装空格引用 exit1 保留 | 3b + dirty（Rust），exit0 direct | PASS（前置构建，有限制）：dist 产出；不是 final head 的 Rust 验收 | `prerequisite-npm-ci-direct.log`；`prerequisite-frontend-build.log`；`prerequisite-npm-ci.log` exit1 |
| 测试计数 | 静态 `#[test]`/`#[ignore]` + 运行日志 | `1829a38` | PASS（口径）：171 = 166+5；running 159 = 153 + 6；packaged 12 filtered | 本次静态统计；`source-fixed-r*.log` |
| Owner 阶段 | ZCode CLI 最终 exit1/HTTP429，无有效 JSON；原始文件快照 | `zcode-delivery-r2` | NOT_RUN/来源阶段；不作为 final head PASS | `CODEX_VALIDATION.md`；Owner 快照 |

### 数量与判别力

- 171 个 `#[test]`：base 166 + 5 个专用 stress；默认 `running 159`，其中 153 passed（两轮均 0 failed）+ 6 ignored；12 个 packaged 被显式 filter。
- 6 个 ignored 逐项：1 个旧 `perf_chunk_request_digest_cost`，5 个 stress（1/8/20/取消/fault）；不是 skip 失败。
- 五个 stress 均各自 `--ignored … --exact` 运行，日志显示 `1 passed … 170 filtered`（fault 为 `0 passed/1 failed/170 filtered`）。`170 filtered` 只是精确选择，不是全套 PASS。
- `source-fixed-r1/r2` 是同一 `1829a38`、同一源码 SHA、同一参数下的两次连续默认运行；未设单线程，未改输入。AC2 仅证明当前 head 的默认 source 范围，不覆盖 packaged、未来 head 或父候选。
- fault 的 `peak=0` 不是“0<=32 所以通过”；测试在 `peak>=32` 处故意失败。真实 Core 的正常/取消通过不能替代 capacity 证据。

## Standards / Spec（可选视角）

- **Standards**：没有发现 r2 修改越过允许范围、共享契约、依赖或生产语义；变更集中在 test 隔离/观察和 stress。`remaining_final` 未使用赋值、`track_unreaped_worker_handle` dead-code 是低价值警告，不是阻断项。
- **Spec**：AC2 在当前 head 有连续两次通过证据；AC3 明确未满足；AC1 的主要真实性改进成立但有残余；AC4 只完成精确 artifact/Appointment 绑定，不是 main 集成或父升级。未发现 scope creep。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态/修订 commit |
|---|---|---|---|---|---|---|
| R-001 | P1→closed（current head） | `library_bridge.rs:8434-8585`（child_lock 测试） | r1 的默认并发失败在 1829 上不再复现：两次 153/0/6/12 exit0；测试新增持锁握手、600ms 持锁、fallback 分支判别，且未改 250ms/1500ms/fallback 预算。 | `source-fixed-r1/r2.log` 两次 `child_lock… ok` 与总数；`CODEX_VALIDATION.md` | 保持该测试；不要把“两次通过”扩大为所有负载下生产 taskkill 可靠性结论。残余 tasklist 状态检查见 R2-F04。 | closed（本 head 测试证据） |
| R-002 | P1→partial | `multichannel_stress_tests.rs:700-744`、`811-822` | 注入现在真实：20/20 `stdin write timed out`（~3s），20/20 writer/reader unfinished；但测试仍只硬断言 `res.is_err()`，没有断言 unfinished/错误码；Drop 后 worker 被 kill/cancel/join，`peak=0`，没有触发 32 容量接受/拒绝路径。 | `stress-fault-20.log` 的 20 条 `blocked_request_timeout_ms≈3006`、`writer_unfinished=true reader_unfinished=true`、`peak_registry=0`、`capacity boundary NOT reached` | 保留 `peak>=32` 门槛；在测试侧把 `writer_unfinished && reader_unfinished`、`stdin write timed out` 变成断言，并记录 post-Drop 所有权。容量注入/验证设计需另 Task 或另议，不得改生产预算凑 32。 | partial（诊断改进，饱和 open） |
| R-003 | P1→closed（stress 范围） | `multichannel_stress_tests.rs:68-233`；`library_bridge.rs:3193-3205` | 每个 child 有复制自 `Child` 的自有进程句柄、OS 创建时间、`WaitForSingleObject`；`tasklist` 检查 exit status、失败按存活处理；每 channel 断言 finished/joined 与四个 pipe/thread handle 槽，20/20 句柄 signaled、PID gone。 | `stress-real-*.log`、`stress-cancel-20.log`、`stress-fault-20.log` 的 `worker_finished_joined=[true,true,true,true]`、`pipe_thread_handle_slots=[0,0,0,0]`、`handle_signaled=true`、`pid_gone=true`；20/20 counts | 核心 R-003 关闭。把 `threads_spawned/joined` 从“打印”改成断言，见 R2-F04；`child_lock` 的 raw tasklist 状态检查补齐。 | closed（核心），R2-F04 残余 |
| R-004 | P1→closed | `library_bridge.rs:1666-1727`、`1825-1875`、`9560-9660` | holder 通过 `TEST_THREAD_REGISTRY` 继承同一 Arc registry；ac1 持锁 spawn holder，等待真实 `TEST_HOLDER_LOCK_TIMEOUTS>0`，锁内确认无 holder，释放后同 registry 注册，最后 `reap_now` remaining=0。 | 代码；`source-fixed-r1/r2.log` 的 `ac1_consecutive… ok`；默认两轮 | 保持；不要再用全局 registry 观察 holder。 | closed |
| R-005 | P1→closed | `library_bridge.rs:1706-1727`、`6069-6145` | `with_unreaped_registry` 在 override 槽读失败且 `IN_REGISTRY_TEST` 时 panic；guard 安装/清除读回 assert；非 owner/生产方式 global；生产 `cfg(not(test))` 只 global。 | 代码；默认两轮通过（guarded 路径）；无静默回退日志 | 核心关闭。补一个直接触发 fail-closed 分支的测试，见 R2-F05；owner mismatch 只应发生在非 owner 线程。 | closed（核心） |
| R-006 | P2→partial | `library_bridge.rs:6069-6145`（guard drop） | `Box::leak` 已由 `Arc` 替代，正常 ac1/ac2/ac4 都有显式 reap；但 guard drop 的 `reap_now` 不 assert `remaining==0`，未完成 worker 会打印后 detach；异常展开/仍有 holder 持 Arc 时不能证明私有 registry 一定在 guard 后释放。 | 代码 6118-6145；`source-fixed` 正常日志无未回收，但无异常路径证据 | 在 guard drop 中记录并断言可回收数量；对 holder 继承 Arc 的生命周期加显式收尾/超时；异常路径声明为 PARTIAL，不把正常日志当所有路径证明。 | partial |
| R-007 | P1→closed | `library_bridge.rs:3177-3191`；`multichannel_stress_tests.rs:484-535` | `kill_and_wait_for_test` 返回 kill/wait 结果；取消场景 20/20 分别断言 `cancel_kill_ok`、`cancel_wait_ok`，Drop 完成单独记录，再检查 PID 消失。 | `stress-cancel-20.log` 20/20 `cancel_kill_ok=true cancel_wait_ok=true`、`drop_completed=true`、`pid_gone=true`；`test result: ok` | 保持。 | closed |

### 新增问题

| ID | 级别 | 文件/行 | 问题与影响 | 证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R2-F01 | P1 | `multichannel_stress_tests.rs:811-822` | AC3 容量边界未达到：fault `peak=0`，`reaped=0`，测试在 `peak>=32` 失败。真实 Core 1/8/20/取消通过只证明正常/取消回收，不是 32 饱和、backpressure 或 rejected handle 路径。这是当前不能 approved 的直接原因。 | `stress-fault-20.log`；`SUMMARY.json` fault `EXIT=101` | 保留失败与 BLOCKED；若要继续，另开**测试/故障注入与容量验证设计** Task（test-only）。不要为凑 32 改生产 MAX/锁/背压/taskkill/reap 预算。若在该 Task 也无法在不变生产语义下达到 32，应交 Codex/用户重新裁定 AC，而不是放宽门槛。 | open |
| R2-F02 | P2 | `multichannel_stress_tests.rs:729-737` | `writer_unfinished`/`reader_unfinished` 与 `error_envelope` 只打印，不 assert；`res.is_err()` 不能单独证明写阻塞。日志目前很好，但未来回归可在错误类型/worker 已结束时仍进入后续断言。 | 20/20 日志 `stdin write timed out` + unfinished；测试只 `assert!(res.is_err())` | 断言 `writer_unfinished && reader_unfinished`，断言错误码/消息包含 `stdin write timed out`；把 pre-drop flags 与 post-drop registry/ownership 分开记录。 | open |
| R2-F03 | P2 | `library_bridge.rs:6118-6145` | R006 的异常路径：`reap_now` 对未完成 worker 只打印；guard drop 不 assert remaining；继承 Arc 的 holder 可能在 guard 之后仍持有 registry。正常 ac1/ac2/ac4 通过，但不能声称所有清理路径无 detach。 | 代码；`source-fixed` 正常路径无 remaining 日志，但无 panic/异常场景 | 增加“未完成即记录/断言”的清理账本；对 holder Arc 生命周期设显式收尾；异常路径标注 PARTIAL。 | open |
| R2-F04 | P2 | `multichannel_stress_tests.rs:417,565`；`library_bridge.rs:8549,8559` | R003 的 ledger `threads_spawned/joined` 只打印、不 assert；`channel_reader_writer_threads` 是常量不是实测；`child_lock` 的 `tasklist` 调用不检查 exit status，失败可假性通过孙进程消失检查。 | 代码；`stress-real-*.log` 的 ledger 行；`child_lock` 的 raw `tasklist` | 断言 `threads_spawned==threads_joined`（或记录真实 join 计数）；`tasklist` 检查 `status.success()`；per-channel flags/handles 已强，继续保留。 | open |
| R2-F05 | P2 | `library_bridge.rs:1706-1727` | R005 的 fail-closed panic 分支没有被直接测试；`with_unreaped_registry` 在 `Some(slot)` 但 owner 不匹配时仍回 global（对非 owner 线程是设计，但如果 owner 线程发生则仍静默）。 | 代码；默认两轮只覆盖正常 guard 路径 | 加一个测试：持有 override 锁使槽读失败，确认 owner guard 线程 panic 而非 global；明确 owner mismatch 的不可达/断言。 | open |

## 结论与复审

### Decision：`blocked`

不批准 `1829a38a…` 交 Codex 集成。理由：

1. **AC2：当前 head 满足。** `source-fixed-r1/r2` 两次连续 `153 passed / 0 failed / 6 ignored / 12 filtered`，exit0，默认并发、unset 正确、源码未变。该结论只覆盖当前 head 的默认 source 范围，**不覆盖** packaged、未来 head 或父候选；不能把 AC2 通过当成 AC3/整体通过。
2. **AC3：未满足，直接阻断。** fault 场景 `peak_registry=0 < 32`，`reaped=0`，exit101；真实 Core 1/8/20/取消通过只是正常/取消路径与资源回收，不是 32 饱和、容量接受/拒绝或 backpressure。20/20 `stdin write timed out` 与 writer/reader unfinished 证明注入有效，但也证明生产 kill/cancel/join 会在 track 前解除阻塞；这不是可通过“0<=32”或“20 个成功往返”覆盖的 Gate。
3. **AC1：主要真实性改进成立，但仍有残余。** R004/R005/R007 核心关闭，R003 的 OS 身份/回收核心关闭；R006 的异常/未完成 guard 清理仍 PARTIAL，R002 的 fault 断言仍只部分强制。没有证据表明生产 MAX/锁/背压/holder/kill 预算被改，故不是生产缺陷；但这些残余不允许把 AC1 说成完全无保留。
4. **AC4：仅 artifact 绑定。** head、59 文件包、734 文件源码树、66 行 EV、Appointment 均可核对；但本 Review 不解除 AC3，也不授权 main 集成/父候选升级。packaged/模型/GUI/安装包均为 NOT_RUN。
5. **旧证据不可移植。** r1/3b 的 PASS 与失败均不自动适用；Owner 的 HTTP429/exit1 阶段不是 final head 运行；最终事实只以 `1829` 源码 + Codex 日志/包为准。

### 后续建议

**测试/验证范围（可另开 Task，不要求改生产）：**

- 为 AC3 设计一个**不改变生产预算**的容量验证/故障注入方案，证明 accepted/refused handle 的 32 边界、backpressure 与 holder 归属；若在冻结生产语义下无法构造，明确记录“AC3 结构性不可达”，交 Codex/用户重新裁定 AC，而不是放宽 `peak>=32`。
- 将 fault 的 `writer_unfinished`/`reader_unfinished`/`stdin write timed out` 变成硬断言；增加 post-Drop 所有权证据。
- 收尾 R006 异常路径：guard drop 显式统计/断言 remaining，holder 继承 Arc 的生命周期有界；避免未完成 worker detach 后无账本。
- 收紧 R003 ledger：assert `threads_spawned==threads_joined`；`child_lock` 的 tasklist 检查 exit status。
- R005 增加 fail-closed 分支测试；R002/R006 的残余不应被“正常日志无 remaining”替代。

**如另立 Task，必须区分：**

- **测试注入/容量验证设计 Task**：只改测试/运行器/观察，不改生产 MAX、锁、容量、backpressure、holder、Drop/shutdown、taskkill 预算。当前证据没有证明生产缺陷，不应以“让测试达到 32”为由改生产。
- **真正生产缺陷 Task**：只有在独立证据显示生产 kill/reaper/join 时序或 registry 语义有缺陷时才另冻；不能因为 fault 场景无法达到 32 就推定生产必须改预算。若确需改生产，必须单独定义风险、AC 和证据，并由 Codex/用户裁定。

**状态与边界：**

- 本 Review 只写 `verification/GIT-CLEAN-RUST-ISOLATION-1/r2/dsh-review-r2.md`；未改 Task/源码/Status/Plan/其它证据/manifest/refs/远端/ACL，未 push/done/集成/清理。
- 父候选/父审查仍 r1 blocked；本 Task 仍 `in_review`；AC3 未满足前不得 approved。任何新 head 必须重新 Appointment，本 Review 不自动升级。
