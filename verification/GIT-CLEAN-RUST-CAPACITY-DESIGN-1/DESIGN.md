# GIT-CLEAN-RUST-CAPACITY-DESIGN-1 · DESIGN（ZCode 设计交付，DSH 集成）

- **交付者**：ZCode（`zcode.cjs` headless，`--mode plan`，session `sess_be120ee8-a555-4c37-84cb-62539081bfd3`）
- **派发者/集成者**：DSH（Lead）
- **交付时间**：2026-11-17
- **输入**：`1829a38a41587a0d680001a40d206886afb0911d`；`verification/GIT-CLEAN-RUST-ISOLATION-1/r2/dsh-review-r2.md`
- **性质**：只读设计（未改产品源码、未跑压力测试）；已标注 `[实测]`/`[推断]`/`[建议]`
- **未做**：独立复核（AC4）与实施 — 均不在本次切片内

---

代码核实完毕。所有关键符号、行号、分支均已对照 `1829a38` 精确字节（三文件 SHA256 与评审记录一致）。以下是设计交付正文。

---

# DESIGN.md — Rust 真实容量注入与残余测试收紧设计（GIT-CLEAN-RUST-CAPACITY-DESIGN-1）

**基准**：`1829a38a41587a0d680001a40d206886afb0911d`（隔离仓 `source-r2` 工作树，三 Rust 文件 SHA256 复算一致：`library_bridge.rs=145a6a2a…`、`multichannel_stress_tests.rs=dd2dfeaa…`、`main.rs=b315e632…`）。
**性质**：只读设计交付。标注口径：`[实测]`=DSH r2 Review 记录的运行事实；`[推断]`=读 `1829a38` 代码的静态结论；`[建议]`=本设计提出、未实施。

---

## AC1 资源与时序链

### 1.1 每 channel 资源清单（`StdioLibraryChannel::adopt_child`，library_bridge.rs:2106-2380）

| 资源 | 创建点 | 归属 |
|---|---|---|
| 真实 OS 子进程 `child: Arc<Mutex<Child>>` | 2103（stress 经 `spawn_with_startup_ping`:multichannel_stress_tests.rs:299-307 / fault 经 `adopt_child_for_test`:368） | channel |
| stdin 写端 + stdout 读端（真实 pipe，raw handle 存 `raw_stdin_handle`/`raw_stdout_handle`:2146-2149） | `Child` spawn 继承 | channel |
| writer 线程 `stdio-library-writer`（2264-2346） | 循环 `writer_rx.recv()` → `stdin.write_all`+`flush`（2332-2342）；**写错误即 break**（2335-2337） | channel 持 `writer_join_handle` |
| reader 线程 `stdio-library-reader`（2156-2262） | 循环 `read_line`（2223）；`Ok(0)`/`Err` → drain pending + `on_down` + break（2225-2256） | channel 持 `reader_join_handle` |
| 线程退出钩子 | `ThreadFinishedGuard` 置 `*_finished`（2159/2267，1339-1345）；`Reader/WriterHandleCleaner` 清 handle 槽位并 `CloseHandle` 线程句柄（2160-2178/2268-2286） | 线程自身 |

### 1.2 请求阻塞路径（fault 场景 Phase 2，实测 20/20）

`round_trip_timeout`（2842）→ `exchange_expected_minor_timeout`（2665）→ `write_stdin_raw_timeout`（2499-2526）：请求发 `writer_tx`，调用方 `reply_rx.recv_timeout(3s)` 超时返回 `"stdin write timed out"`（2513-2515）。**超时只放弃等待，不取消 writer**——writer 仍阻塞在 2332 的 `write_all`（4MB pad，multichannel_stress_tests.rs:712），reader 阻塞在 2223 `read_line`。此时 `is_writer_finished()==false`、`is_reader_finished()==false`（729-730 记录的 blocked-phase 证据，[实测] 20/20 为 true）。

### 1.3 Drop 时序链（`shutdown_and_kill_with_deadline`:3427，Drop impl:4171-4202，默认 deadline 2400ms:4176）

| 步骤 | 行号 | 动作 | 对阻塞 worker 的解除机制 | track 是否可达 |
|---|---|---|---|---|
| 幂等 guard | 3429 | `shutdown_executed` CAS；重入分支只补 kill（3432-3535） | — | — |
| 1 drain pending | 3539-3613 | 清空超时请求的 sender | 释放调用方，不触碰 worker | 否 |
| 2 CloseHostSession | 3615-3640 | 240ms 有界 | fault 无 session，跳过 | 否 |
| 3 core.shutdown 写 | 3642-3656 | 60ms 有界（writer 阻塞时该写排队后丢弃） | 无效但无害 | 否 |
| 4 kill child | 3658-3693（锁可得：`wait_timeout_or_kill_with_reap`:3216，graceful 1000ms → `child.kill()`:3254 → reap 400ms）；锁不可得：taskkill /F /T fallback（3755-3782） | **child 死 → sidecar 的 stdin 读端全关 → writer `write_all` 立即 broken-pipe 失败 → 2335 break** | 否（writer 已解锁） |
| 5 join reader | 3895-4027：先 `cancel_active_pipes()`（3896 → `cancel_worker_io`:1550-1568 = `CancelSynchronousIo`(线程) + `CancelIoEx`(pipe)）；100ms join 窗口（3903-3919） | child 死 → stdout EOF → reader `Ok(0)` break（2225） | 否（reader 已解锁） |
| 6 join writer | 4029-4162：`send(Shutdown)`（4035）+ `cancel_active_pipes`（4036）；80ms join 窗口（4038-4054） | 同上 | 否 |
| 5/6 兜底 reaper | 若 join 窗口内未结束：spawn detached `reader/writer-join-bounded-reaper`（3932/4067），200ms 内反复 `cancel_worker_io` + 轮询 finished（3941-3971/4076-4106）；**仍不结束才 `track_unreaped_worker`**（3980/4115） | 唯一 track 入口 | **是（本链未到达）** |
| track 内部 | 1748-1809：锁 10×50ms 重试（1761）；容量满 → 对在册 worker 发 cancel + prune（1767-1778）→ 仍满则 20ms 等待重试；10 次后 **refuse，handle 留调用者**（1787-1796 take、1806-1807 false） | — | — |
| refused 兜底 | `spawn_persistent_holder`（3983-3989/4118-4124 → 1825-1878）：50ms→500ms 指数退避**无限重试** track；spawn 失败则同步 join（1871-1877） | — | — |
| 尾部 | `reap_unreaped_workers(50ms)`（4164-4167）；Drop 后 `reap(20ms)`（4200）+ `CloseHandle` 线程句柄（4180-4197） | reap = prune + cancel + join（1906-1949） | — |

### 1.4 为什么「20 真实 pipe、峰 0」

- 场景矩阵冻结 **20 channel**（multichannel_stress_tests.rs:652-657）= 20 对真实 pipe = **40 个 reader/writer worker 候选**。`MAX_UNREAPED_WORKERS=32`（1606）是 **registry 的 worker 容量**，不是 channel 数；20×2=40>32 的设计意图是“若 track 路径可达即可触界”。
- [实测] 结果：Drop 串行逐 channel（753-770），第 4 步 kill child 即解除 write_all（broken pipe），第 5/6 步 EOF+cancel 解除 read_line，两 worker 均在 join 窗口内 finished+joined（`worker_finished_joined=[true×4]`、`peak_registry=0`、exit101 于 819-822）。**track 分支（3980/4115）从未执行**。这是“未泄漏 worker”的设计结果，不是容量证据——`peak>=32` 按设计故意失败。

### 1.5 到 32 需要的故障前提（逐分支排除，[推断]）

worker 必须在「kill child（pipe 断）+ `CancelSynchronousIo` + `CancelIoEx`（第 5/6 步一次 + 200ms reaper 内反复）」全部之后仍不结束。候选前提：

| 前提 | 可行性 | 排除理由 |
|---|---|---|
| F1 child 死后 stdin 读端仍开（第三方进程继承读端） | 真实 OS 可构造（见 AC2-L1） | **单独不够**：writer_thread_handle 由 DuplicateHandle 在线程启动时写入（2320），线程阻塞期间非 0（Cleaner 只在线程退出时清零，2268-2286），`CancelSynchronousIo` 对阻塞在内核 WriteFile 的同步 IO 有效（1553-1560）→ writer 仍会被解除 |
| F2 cancel 双失败（CancelSynchronousIo 与 CancelIoEx 均 OS 级失败） | 不可确定性构造 | 同进程 DUPLICATE_SAME_ACCESS 句柄有效；无生产级注入面，不改生产无法触发；不能作为 Gate |
| F3 worker 阻塞在非 IO 等待 | 当前代码不存在 | writer 阻塞点仅 `write_all`/`recv`（recv 由 4035 send(Shutdown) 解除）；reader 仅 `read_line`。无第四形态 |
| F4 调度饥饿（cancel 生效但 200ms 内线程未跑到） | 非确定性 | 竞态，不可作 Gate |

**结论（AC1）**：在冻结生产语义 + 真实 worker/pipe + 测试侧仅能构造外部进程故障的约束下，32 饱和**结构性不可达**：shutdown 的层层解除先于 track 到达。唯一未闭环的反证窗口是 F1+「cancel 对该形态无效」的组合——AC2-L1 实验专门检验它。

---

## AC2 可实现的注入方案（不改生产语义）

### 分层定义（真实 → 替身，严格区分）

**L0 真实 worker+pipe（现状，保留）**：real Core 1/8/20 graceful、20 concurrent cancel（`kill_and_wait_for_test`:3177-3190 断言 kill+wait）、fault 20 blocked-pipe。[实测] 已全跑；只证明正常/取消回收。

**L1 真实 pipe + 强故障 sidecar v2 [建议]**——「逃逸读端持有者」实验，F1 的可证伪对照：
- sidecar 脚本改为：应答首个 ping 后，spawn A（`subprocess` 继承 stdin 读端），A 再 spawn B（再继承读端）后 A 立即退出，sidecar sleep。B 的 PPID 指向已退出的 A；`run_taskkill_bounded` 的 `/T` 按父链快照 BFS（3318-3323），从 sidecar 根**枚举不到 B** → child 树死后 B 仍持读端 → writer 的 `write_all` 不 broken，持续阻塞。
- **预注册判据（防 cherry-picking）**：预期 `peak==0` 且 writer 在 cancel 后结束（机制同 1.5 排除表）；若实测 `peak>0`，即为「AC3 真实可达」的反证，立即原样上报，两种结果都记录。
- 边界证据：沿用 sampler（10ms 采样 `unreaped_worker_count`，426-434/666-674）、`unreaped_worker_names`、capacity warning 行（1780）。
- 预算与停止：`SCENARIO_WALL_LIMIT=120s`（:50）+ `CLEANUP_BUDGET=30s`（:51）in-test 断言（827-830/823-826）；sampler 绝对上限 180s（:55）防 unwind 死锁。**清理条件**：B 进程带 argv 标记（同 `stress_mark`:349 模式），测试收尾在 CLEANUP_BUDGET 内显式 `taskkill /F /PID` 清 B，不留给环境；停止条件 = `remaining==0` 或 30s 耗尽（783-791）。
- 定位声明：仍是 `FAULT_INJECTION` 真实 OS 进程/管道，非真实 Core；不构成生产饱和通过证据，只为定案 F1。

**L2 registry 语义边界（真实 OS 线程、直接 track）[建议]**——扩展 `ac2_saturated_registry_answers_boundedly_and_never_loses_the_handle`（9665-9715）：fill **32** 个真实 sleep 线程 + 第 **33** 个，断言：`track_unreaped_worker` 第 33 个返回 false 且 handle 留在调用者（refused 证据，9710-9712 已 join 证明 handle 活着）；`unreaped_worker_count()==32`（accepted 证据）；触发 1767-1784 capacity 分支（cancel 在册 + prune + 等待）。**明确标注**：这是人工阻塞替身（sleep 线程），证明 32 边界的 accepted/refused/holder 语义，**不是**生产饱和，不得写进 AC3 通过依据（任务卡禁止范围）。

**L3 test-only 观察/调度（r2 已有）**：`TEST_REGISTRY_OVERRIDE`/`TEST_THREAD_REGISTRY`/`IN_REGISTRY_TEST`（1641-1656）、`RegistryTestGuard`（6069-6145）、holder 继承（1840-1848）、ledger/sampler。AC3 各修订把它们从“打印”升为“断言”（见下）。

### 结构性不可达的处置

若 L1 实测 `peak==0`（预期）：AC3 维持 **BLOCKED**，交付物 = L1 对照数据 + L2 语义边界证明 + 1.5 排除表，交 Codex/用户裁定 AC 口径（是否改口径为「不可达证明+边界验证」），不放宽 `peak>=32`（819-822 原样保留）。

---

## AC3 R2-F02..05 最小修订

### R2-F02：fault 断言硬化（multichannel_stress_tests.rs:729-737）

- **修订**（全部在 `#[ignore]` stress 函数内）：`assert!(res.is_err())`（734）之前加两条硬断言：`assert!(writer_unfinished && reader_unfinished)`、`assert!(err_detail.contains("stdin write timed out"))`。post-Drop 所有权已有分层：pre-drop flags（756-757/764）+ post-Drop `assert_pid_gone` 的 flags/handles/句柄信号/PID 检查（199-232）+ `remaining_final==0`（823-826）；补一行注释明确 pre/post 分界，不改语义。
- **测试计划**：重跑 fault 场景一次；预期 20/20 新断言通过、仍在 819-822 处 exit101（BLOCKED 保留）。若新断言失败 = 注入形态漂移，停下诊断。
- **不改变生产的证明**：diff 仅该 cfg(test) 场景文件；生产 `cfg(not(test))` 字节不变；默认套件 153/6/12 口径不变（场景被 `#[ignore]`）。

### R2-F03：guard 收尾账本与 Arc 生命周期（library_bridge.rs:6118-6145，cfg(test)）

- **修订**：guard drop 的 `remaining>0` 分支（6124-6128）从 eprintln 升级：`TEST_GUARD_DROP_UNRECLAIMED`（新增 AtomicUsize）累加；slot 清除后（6139 之后）有界等待 holder 放 Arc：`strong_count(&self.registry)>1` 时最多等 2s（10ms 步进），结果记入 `TEST_GUARD_DROP_ARC_HELD`。**仅当账本非 0 才等待**，正常路径零成本。
- **新测试 a**：ac4/ac1/ac2 正常路径结尾断言 `TEST_GUARD_DROP_UNRECLAIMED==0`（guard drop 的 remaining==0 成为断言）。
- **新测试 b**：panic 路径——guarded 测试内 `catch_unwind(AssertUnwindSafe(..))` 中途 panic，断言 guard drop 账本仍为 0（非 0 = 测试失败，暴露 detach）。
- **覆盖调用者**：所有 `RegistryTestGuard::acquire()` 调用点（9462/9498/9561/9666 等 registry 语义测试）经测试 a 间接全覆盖。
- **不改变生产**：guard 与账本全在 `#[cfg(test)]` tests 模块（6048 起模块内）；生产 `with_unreaped_registry`（1727-1731）字节不动。风险披露：最坏拉长 registry 语义测试串行 +2s（EXCLUSIVE 锁内），正常为零。

### R2-F04：线程账本断言 + tasklist fail-safe（multichannel_stress_tests.rs:417,565,797；library_bridge.rs:8549-8567）

- **修订 1**：两处 ledger 行（565、797）后加 `assert_eq!(threads_spawned, threads_joined)`（`threads_spawned` 计数已含 ping/cancel worker + sampler：417-418/485/554）。
- **修订 2**：child_lock 测试两处裸 `Command::new("tasklist")`（8549-8553、8559-8563）改用等价断言 `assert!(!pid_still_alive(pid))`——`pid_still_alive`（146-159）已检查 `status.success()` 且失败按“存活”fail-safe，tasklist 失败时孙进程消失检查**不再假性通过**。helper 在 stress 文件（同 bin 的 cfg(test) 模块），需提为 `pub(crate)` 或在 library_bridge tests 模块放同一 8 行实现（建议前者，单一来源）。
- **测试计划**：child_lock 属默认套件 → 重跑默认 153 口径；两 stress 场景抽跑核 ledger 断言。taskkill/tasklist 失败注入无法确定性构造（不改生产），fail-safe 语义以代码审查 + 可选手动对照（临时 PATH 遮蔽 tasklist，可选非 Gate）。
- **不改变生产**：两处均为 cfg(test) 测试代码。

### R2-F05：fail-closed 直接分支与 owner mismatch（library_bridge.rs:1706-1727，cfg(test)）

- **修订**：新增两测试（不动 `with_unreaped_registry` 本体）：
  - **fail-closed 正分支**：`RegistryTestGuard::acquire()` 后，辅助线程持 `TEST_REGISTRY_OVERRIDE` 锁 ≥60ms；owner 线程 `catch_unwind(AssertUnwindSafe(|| with_unreaped_registry(|r| registry_count(r))))` → 断言 panic 且消息含 `fail-closed`（1717-1721 的 30ms 锁超时 None 分支被真实触发）。
  - **owner mismatch 分支**：guard 持有期间，非 owner 线程调 `with_unreaped_registry`（如 `unreaped_worker_count`）→ 断言不 panic、作用于 global（1712-1714 `_ =>` 分支）、私有 registry 状态不变；同时确认 owner 线程自身走 override 正常分支（现有 ac 测试已覆盖，此处补 mismatch 侧）。
- **测试计划**：默认套件内新增，预期 153→155；`catch_unwind` 用 `AssertUnwindSafe`，panic 输出噪音可接受（或临时静默 hook）。
- **不改变生产**：`cfg(not(test))` 版本（1727-1731）零改动，`cargo check` 生产路径不变。

---

## 结论与裁定项

**判断**：
1. 本设计（AC1 时序链/分支排除表、AC2 分层方案、AC3 四项最小修订）为**可释放**的完整设计切片——但按任务卡 AC4，须由 Codex 冻结新 head SHA 并新 Appointment 交 DSH 独审后才能定案；本交付不自批。
2. 父 Task（GIT-CLEAN-RUST-ISOLATION-1）AC3 真实 32 饱和：**读代码推断 + r2 实测（peak=0）支持结构性不可达**；唯一反证窗口（F1 组合）由 AC2-L1 检验。在 L1 落地实测前，AC3 维持 BLOCKED。

**需 Codex/用户裁定**：
1. **AC3 口径**：若 L1 实测 `peak==0`，是否将 AC3 改判「结构性不可达证明 + L2 边界语义验证」或永久 BLOCKED——这是 AC 修订，只能用户/Codex 裁定，本设计无权自改。
2. **实施范围冻结**：L1/L2/R2-F02..05 若采纳，须另立实施 Task（Codex 冻 SHA），不能由本设计 Task 直接实施。
3. **F04 helper 共享方式**：`pid_still_alive` 提 `pub(crate)`（跨 cfg(test) 模块）vs 就地复制，二选一（建议前者）。

---

**推荐下一步**：本设计正文交 DSH 独审（Codex 冻结本 Task 新 head + Appointment）；独审通过后由 Codex 另冻实施 Task 承载 L1 对照实验与 R2-F02..05 收紧，实测数据回填后再裁定 AC3 口径。无需我方再执行其他操作。