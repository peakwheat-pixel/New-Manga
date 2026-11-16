# GIT-CLEAN-RUST-CAPACITY-DESIGN-1 · DESIGN（v2，ZCode 修订版，DSH 集成）

> **版本说明**：v1 于 2026-11-17 被上下文独立复核判 **BLOCKED**（P1=4，报告
> `doc/reviews/GIT-CLEAN-RUST-CAPACITY-DESIGN-1-INDEPENDENT-REVIEW-2026-11-17.md`）。
> 本 v2 由 ZCode 针对 4 条 P1 + 6 条 P2 修订（session `sess_e7e80041-fdd8-4db6-a48f-86d3eed3e62b`），
> 仍属**只读设计**：未改产品源码、未跑压力测试、未实施。v1 原文保留在 git 历史（commit `d37f7c4df`）。

核对完毕。所有 P1 涉及的代码事实已在 `1829a38` 隔离仓逐一对齐（track 四调用点 3980/4004/4115/4139、fault ledger 行 796-799 的常量与 `joined_flags`、`resources_for_test` 的 Arc 克隆序、`assert_pid_gone` 195-233 既有 flags 断言、guard Drop 6118-6145、acquire 点 9462/9498/9561/9666、sidecar 脚本 333-344、`run_taskkill_bounded` 3305-3323）。下面是修订版设计全文。

---

# DESIGN.md v2 — Rust 真实容量注入与残余测试收紧设计（GIT-CLEAN-RUST-CAPACITY-DESIGN-1，修订版）

- **修订者**：ZCode（设计 Owner；本版为对 2026-11-17 独立复核 BLOCKED 判定的修订）
- **响应**：`doc/reviews/GIT-CLEAN-RUST-CAPACITY-DESIGN-1-INDEPENDENT-REVIEW-2026-11-17.md`（P1=4 全部处置，P2=6 一并处置）
- **基准**：`1829a38a41587a0d680001a40d206886afb0911d`（隔离仓 `source-r2`，三 Rust 文件 SHA256 复算一致：`library_bridge.rs=145a6a2a…`、`multichannel_stress_tests.rs=dd2dfeaa…`、`main.rs=b315e632…`）
- **性质**：只读设计（未改源码、未跑测试）。标注口径：`[实测]`=DSH r2 Review 记录的运行事实；`[推断]`=读 `1829a38` 代码/MSDN 的静态结论；`[建议]`=本设计提出、未实施。

---

## 0. 本次修订对照（v1 → v2）

| P1 | 复核意见（摘要） | v2 处置 | 所在节/行 |
|---|---|---|---|
| **P1-1** AC1 分支不全 | 「唯一 track 入口 3980/4115」漏 4004/4139（reaper spawn 失败直接 track）；排除表须逐分支 | 1.3 表改为**四个 track 入口 TA..TD**（3980/4004/4115/4139，另有 1861 holder 重投递不产生新 worker）；1.5 补 **F5**；论证重构为「共同前置 P + 两条后续分支」，删除「唯一 track 入口/唯一反证窗口」措辞；完整排除论证见 1.5 结论段 | §1.3 / §1.5 |
| **P1-2** R2-F04 断言点不存在 | 797 处无 `threads_spawned/threads_joined`（只有常量 `20*2`），修订不可编译 | 797 断言**撤销**。改为：(a) `run_real_core_scenario` 在 scope 结束后对**真实局部变量**断言（可编译）；(b) fault 侧真实 join 账本 = `ChildIdentity.worker_flags`（`resources_for_test` 3200-3205 已暴露 4 个 Arc，Drop 后存活），在 `assert_pid_gone` 循环后加聚合断言；797 行保留打印并加注释澄清其为结构常量 | §3.4 |
| **P1-3** AC2-L1 B 清理不可执行 | B 无 PID 发现通路，`taskkill /F /PID` 无从下手 | L1 v2 脚本让 **B 自写 pidfile**（argv 传路径）；测试收尾有界发现（≤2s）→ `run_taskkill_bounded`（5s）→ `wait_for_pid_exit`（10s）复核，全部计入 wall 预算；pidfile 缺失 = fail-loud + 人工处置指引；Job Object 评估后不采用（理由见 §2.3） | §2.2 / §2.3 |
| **P1-4** R2-F03 断言位置错误 | 字面在 guard 隐式 drop 前执行，账本恒 0；全局 Atomic 有并行污染 | guard 新增 `finish(self) -> GuardFinishReport`（显式消耗，返回 reaped/remaining/arc_released，**断言读返回值**）；Drop 走共享 `cleanup()` 并写 **thread-local** 账本（每测试一线程，天然隔离，兼修 P2-5）；测试 b 经 `catch_unwind` 后**同线程**读 thread-local 断言；既有 4 个 acquire 点全部迁移到 `finish()` | §3.3 |

P2 处置一览：P2-1→§1.3 注 a（taskkill /T 表述改写）；P2-2→§1.4 首句；P2-3→§2.2（A/B 全 DEVNULL）；P2-4→§3.5（mpsc 握手）；P2-5→§3.3（thread-local）；P2-6→§5 交付说明（design-only head + HANDOFF，Codex/DSH 执行）。

---

## AC1 资源与时序链

### 1.1 每 channel 资源清单（`StdioLibraryChannel::adopt_child`，library_bridge.rs:2106-2380）

与 v1 相同（复核 A2/A3 全 PASS），不重复：真实 OS 子进程（2103）、stdin/stdout raw handle（2146-2149）、writer 线程 `stdio-library-writer`（2264-2346，写错误即 break 2335-2337）、reader 线程 `stdio-library-reader`（2156-2262，`Ok(0)`/`Err` → drain+on_down+break 2224-2255）、`ThreadFinishedGuard`（1339-1345）与 `Reader/WriterHandleCleaner`（2160-2178/2268-2286）。

### 1.2 请求阻塞路径（fault 场景 Phase 2，[实测] 20/20）

与 v1 相同：`round_trip_timeout`（2842）→ `exchange_expected_minor_timeout`（2665）→ `write_stdin_raw_timeout`（2499-2526），3s 超时返回 `"stdin write timed out"`（2513-2515）；writer 仍阻塞在 2332 `write_all`（4MB pad，stress:712），reader 阻塞在 2223 `read_line`；729-730 的 blocked-phase 证据 [实测] 20/20 为 true。

### 1.3 Drop 时序链（`shutdown_and_kill_with_deadline`:3427，Drop impl:4171-4202，默认 deadline 2400ms:4176）

前 4 步与 v1 相同（复核 A4 PASS）：幂等 guard（3429）→ drain pending（3539-3613）→ CloseHostSession（3615-3640）→ core.shutdown（3642-3656）→ kill child（3658-3693；锁不可得走 taskkill /F /T fallback 3755-3782）。第 5/6 步修订如下：

| 步骤 | 行号 | 动作 | 对阻塞 worker 的解除机制 |
|---|---|---|---|
| 5 join reader | 3895-4027：**先** `cancel_active_pipes()`（3896 = `cancel_worker_io`:1550-1568，`CancelSynchronousIo`(线程)+`CancelIoEx`(pipe) 各一次），再 100ms join 窗口轮询 finished（3903-3919） | child 死 → stdout EOF → reader break（2225）；或 cancel 解除 |
| 6 join writer | 4029-4162：**先** `send(Shutdown)`（4035）+ `cancel_active_pipes()`（4036），再 80ms join 窗口（4038-4054） | child 死 → stdin 读端全关 → `write_all` broken-pipe（2335 break）；或 Shutdown 解除 `recv`、cancel 解除 `write_all` |
| 5/6 窗口耗尽 | worker 未 finished → spawn detached reaper（3932/4067），200ms 内反复 `cancel_worker_io` + 轮询（3941-3971/4076-4106） | 反复 cancel |

**track 入口全表**（`git grep -n "track_unreaped_worker("` 的全部生产调用点）：

| 入口 | 行号 | 触发条件 | 前置 |
|---|---|---|---|
| TA | 3980 | reader reaper 200ms 内 reader 仍未 finished | 前置 P（见下）+ 熬过 200ms 反复 cancel |
| TB | **4004** | **reader reaper 线程 spawn 失败**（3999 `if let Err(e) = spawn_res`）→ 锁回 handle 后**立即** track，**不经历** 200ms 反复 cancel | 前置 P + F5 |
| TC | 4115 | writer reaper 200ms 内 writer 仍未 finished | 前置 P + 熬过 200ms 反复 cancel |
| TD | **4139** | **writer reaper 线程 spawn 失败**（4134）→ 立即 track | 前置 P + F5 |

另：1861（`spawn_persistent_holder` 循环内）是对 **refused handle 的重投递**，不引入新 worker，handle 最终来源仍是 TA..TD；1882 附近为测试辅助面。**首次** track 只能经 TA..TD。

> 注 a（P2-1，改写 v1 表述）：`run_taskkill_bounded`（3308-3323）只构造 `taskkill /F /T /PID` 命令并检查其输出；「按父链快照 BFS 枚举进程树」是 **Windows taskkill /T 在调用时刻的 OS 行为**，不是本仓 Rust 代码——正因如此，父先退出的孙进程（B 的 PPID 已死）**不在该快照的可枚举链上**，这是 §2 L1 实验的机制前提。[推断]

track 内部（1748-1809）与 refused 兜底 holder（1825-1878，50→500ms 退避无限重试、spawn 失败同步 join 1871-1877）同 v1（复核抽样 PASS）。

### 1.4 为什么「20 真实 pipe、峰 0」

**20 是冻结测试场景矩阵的上限（stress:652-657 `for idx in 0..20`），不是生产 channel cap——代码中不存在生产 channel 数量上限**（P2-2 明示）。20 对真实 pipe = 40 个 reader/writer worker 候选；`MAX_UNREAPED_WORKERS=32`（1606）是 registry 的 worker 容量。40>32 的设计意图是「若 track 可达即可触界」。

[实测]（R2 Review）：Drop 串行逐 channel（753-770），kill child 解除 `write_all`、EOF+cancel 解除 `read_line`，两 worker 均在 join 窗口内 finished+joined（`worker_finished_joined=[true×4]`、`peak_registry=0`、exit101 于 819-822）。**TA..TD 四入口均未执行**——这是「未泄漏 worker」的设计结果，不是容量证据；`peak>=32` 按设计故意失败（819-822 原样保留）。

### 1.5 到 32 的完整排除论证（[推断]，逐分支）

**共同前置 P**（到达 TA..TD 任一入口的必要条件）：worker 线程在「kill child（pipe 断）→ `send(Shutdown)`（writer）→ `cancel_active_pipes()` 一次（3896/4036）→ join 窗口（100/80ms）轮询」之后仍未 finished。

P 的候选成立条件：

| 前提 | 可行性 | 排除理由 |
|---|---|---|
| F1 stdin 读端被第三方进程持有（child 死后 `write_all` 不 broken） | 真实 OS 可构造（§2 L1） | **单独不够**：writer_thread_handle 由 DuplicateHandle 在线程启动时写入（2320），线程阻塞期间非 0（Cleaner 只在线程退出清零，2268-2286）；join 窗口前已发出一次 `CancelSynchronousIo`，对阻塞在内核同步 WriteFile 的线程有效（MSDN 语义，[推断]）→ writer 仍在窗口内结束 |
| F2 cancel 双失败（`CancelSynchronousIo` 与 `CancelIoEx` 均 OS 级失败） | 不可确定性构造 | 同进程 DUPLICATE_SAME_ACCESS 句柄有效；无生产注入面，不改生产无法触发；不能作 Gate |
| F3 worker 阻塞在非 IO 等待 | 当前代码不存在 | writer 阻塞点仅 `write_all`/`recv`（后者由 4035 Shutdown 解除）；reader 仅 `read_line`；无第四形态 |
| F4 调度饥饿（cancel 生效但窗口内线程未跑到） | 非确定性 | 竞态，不可作 Gate |

P 成立后的两条后续分支：

| 分支 | 前提 | 可行性 | 排除理由 |
|---|---|---|---|
| 走 TA/TC | P + 200ms reaper 反复 cancel 后仍不结束 | 非确定 | 反复 cancel ⊇ 窗口前那次 cancel 的解除面；解除不了只剩 F2/F4 |
| 走 TB/TD（**F5**） | P + reaper 线程 spawn 失败 | 不可确定性构造 | OS 线程创建失败仅见于地址空间/句柄/内存耗尽，与 F2 同属资源面，无注入面；不改生产无法触发；不能作 Gate |

**结论（AC1，修订）**：到 32 需要「≥32 个 worker 同时满足前置 P」且 P 之后落入 TA/TC 或 TB/TD 任一分支。P 的唯一确定性构造途径是 F1，而 F1 单独不成立（窗口前的 cancel 已覆盖）；F5 只改变 P 之后的路径（跳过 200ms 反复 cancel），**不放宽 P 本身**——四入口共享 P，P 不可达则四入口全不可达。故 32 饱和**结构性不可达**的论证在补入 TB/TD 后仍然成立，但其支柱是「前置 P 不可确定性构造 + 两条后续分支均不可构造」，而**不是** v1 错称的「track 入口唯一」。确定性反证窗口收敛于 F1 组合（F1 + cancel 对该形态无效）——它同时是四入口的共同反证点，由 §2 L1 实验检验：若 L1 中 writer 熬过前置 P，则 reaper spawn 成功时经 TA/TC、失败时经 TB/TD，**两条都会进 registry 且 `peak>0`**，L1 对 P 的检验不被 F5 干扰。

---

## AC2 可实现的注入方案（不改生产语义）

### 2.1 分层定义（真实 → 替身，严格区分）

**L0 真实 worker+pipe（现状，保留）**：real Core 1/8/20 graceful、20 concurrent cancel、fault 20 blocked-pipe。[实测] 已全跑；只证明正常/取消回收。

**L3 test-only 观察/调度（r2 已有）**：`TEST_REGISTRY_OVERRIDE`/`TEST_THREAD_REGISTRY`/`IN_REGISTRY_TEST`（1638-1656）、`RegistryTestGuard`（6069-6145）、holder 继承（1840-1848）、`resources_for_test`（3199-3205）。

### 2.2 L1 真实 pipe + 强故障 sidecar v2 [建议] ——「逃逸读端持有者」实验（F1 的可证伪对照）

新增 L1 专用常量 `FAULT_SIDECAR_V2_SCRIPT` 与 `spawn_fault_sidecar_channel_v2`（**不动**既有 `FAULT_SIDECAR_SCRIPT`/`spawn_fault_sidecar_channel`，既有 fault 场景字节不变）：

- **脚本 v2**：应答首个 ping（协议同 v1，333-341）后：sidecar 用 `subprocess.Popen([sys.executable, "-c", WRAPPER, pidfile, mark_b], stdin=sys.stdin, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)` spawn 中间进程 A；WRAPPER 内再以同样姿势 spawn B（B 脚本：`open(sys.argv[1],'w').write(str(os.getpid())); time.sleep(3600)`，argv[1]=pidfile、argv[2]=mark_b）后 A 立即退出；sidecar 随后 `time.sleep(3600)`。argv[1]/argv[2] 由测试经 `cmd.arg()` 传入（同 349-353 现有 argv 通道）。
- **继承面收敛（P2-3）**：A 与 B 的 stdout/stderr 一律 `DEVNULL`，**只**经 `stdin=sys.stdin` 继承 sidecar 的 stdin 读端；sidecar 自身 stdout（应答通道）不受污染 → child 死后 reader 仍正常 EOF，实验保持「writer 单独阻塞」的 F1 形态。
- **PID 发现通路（P1-3 修复）**：B 自己把 PID 写入测试传入的 pidfile（`dir.path().join("escape_b.pid")`，per-channel TempDir 内）。测试**持有 pidfile 路径**（自己构造的），无需按命令行扫描进程表。
- **预注册判据（防 cherry-picking）**：预期 `peak==0` 且 writer 在 cancel 后结束、reader 经 EOF 正常 finished（blocked-phase 采集点 729-730 + post-Drop `worker_flags`）；若实测 `peak>0`，即为「前置 P 真实可达 → AC3 反证」，原样上报，两种结果都记录。**若 reader 也未在清理后 finished = 注入形态漂移（stdout 继承泄漏），停下诊断，不解读数据。**
- **B 的清理（可执行版）**：L1 场景函数尾部、wall 断言（827-830）之前：
  1. pidfile 有界发现：≤2s/10ms 步进等待文件出现并 parse `u32`；**超时或 parse 失败 = 测试失败（fail-loud）**，并在失败消息中附人工处置指引（`wmic process get ProcessId,CommandLine` 按 `mark_b` 前缀 `m2rc1-fault-b-` 定位后手动 taskkill）——自动化通路只承诺 pidfile 成功写出的情形，缺文件时诚实失败而非静默跳过。
  2. `run_taskkill_bounded(b_pid, 5s)`（3308，B 无子进程，`/T` 无害）：Err = 测试失败。
  3. `assert!(wait_for_pid_exit(b_pid, 10s))`（已有 helper 170-179）复核消失。
  全部计入 `SCENARIO_WALL_LIMIT=120s`（:50）口径；sampler 绝对上限 180s（:55）防 unwind 死锁不变。
- **定位声明**：仍是 `FAULT_INJECTION` 真实 OS 进程/管道，非真实 Core；不构成生产饱和通过证据，只为定案前置 P（F1 组合）。

### 2.3 B 清理的备选方案评估（不采用 Job Object）

Windows Job Object（kill-on-close）可结构性兜底全部后代，但需要 `CreateJobObjectW/AssignProcessToJobObject/SetInformationJobObject` 的 win32 调用面（新依赖或手写 syscall），且须在 `Command::spawn` 前介入进程创建参数——超出「最小修订、不改生产」边界。pidfile 方案在纯测试代码内闭合 P1-3 的发现通路，故为主案；Job Object 登记为后续增强候选（另立 Task，须依赖许可核查）。

### 2.4 L2 registry 语义边界（真实 OS 线程、直接 track）[建议]

同 v1（复核 B6 PASS）：扩展 `ac2_saturated_registry_answers_boundedly_and_never_loses_the_handle`（9665-9715）：fill 32 个真实 sleep 线程 + 第 33 个，断言 refused/accepted/holder 语义（9710-9712 handle 不丢、1767-1784 capacity 分支真实触发）。**明确标注**：人工阻塞替身，证明 32 边界语义，不是生产饱和，不得写进 AC3 通过依据。

### 2.5 结构性不可达的处置

若 L1 实测 `peak==0`（预期）：AC3 维持 **BLOCKED**，交付物 = L1 对照数据 + L2 语义边界证明 + §1.5 完整排除论证（含 F5），交 Codex/用户裁定 AC 口径；`peak>=32`（819-822）原样保留不放宽。

---

## AC3 R2-F02..05 最小修订（v2）

### 3.1 R2-F02：fault 断言硬化（multichannel_stress_tests.rs:729-737）——维持 v1（复核 C1 PASS）

`assert!(res.is_err())`（734）前加 `assert!(writer_unfinished && reader_unfinished)` 与 `assert!(err_detail.contains("stdin write timed out"))`；补一行注释明确 pre/post 分界（756-764 pre-drop flags / 195-233 post-Drop 检查）。测试计划与生产不变性声明同 v1。

### 3.2（v1 §R2-F04 修订 2，位置调整）child_lock tasklist → `pid_still_alive`——维持 v1（复核 C4 PASS）

两处裸 `Command::new("tasklist")`（library_bridge.rs:8549-8553、8559-8563）改 `assert!(!pid_still_alive(pid))` / `assert!(!pid_still_alive(grandchild_pid))`；`pid_still_alive`（stress:146-159）已 `status.success()` 检查且失败按存活 fail-safe。helper 提 `pub(crate)`（同 bin 的 cfg(test) 模块，main.rs:42-44 已证可行），单一来源。

### 3.3 R2-F03：guard 显式收尾 + thread-local 账本（library_bridge.rs:6069-6145，cfg(test)）[建议]

**修订（P1-4 + P2-5）**：

1. 把现 `Drop for RegistryTestGuard`（6118-6145）的主体提为私有 `fn cleanup(&mut self) -> (usize, usize)`：`reap_now(2000ms)` → `remaining>0` 时 eprintln **并累加 thread-local `TEST_GUARD_DROP_UNRECLAIMED: Cell<usize>`** → 清 override slot（含验证）→ 清 `IN_REGISTRY_TEST` → 释放 EXCLUSIVE。返回 `(reaped, remaining)`。
2. 新增 `fn finish(mut self) -> GuardFinishReport`（`GuardFinishReport { reaped, remaining, arc_released }`）：调 `cleanup()` 后，若 `Arc::strong_count(&self.registry) > 1`（holder 线程仍持 clone），有界等待 ≤2s/10ms 步进；`arc_released = strong_count==1`；返回报告，`self` 连同最后一个 Arc 在返回时释放。
3. `impl Drop` 改为 `fn drop(&mut self) { self.cleanup(); }`——panic unwind 走同一路径并写 thread-local；Drop 路径不做 Arc 等待（panic 兜底要快）。
4. **测试 a（正常路径，断言位置修复）**：`let report = guard.finish(); assert_eq!(report.remaining, 0); assert!(report.arc_released);`——断言读 `finish` 的**返回值**，时序上必然后于 reap；不依赖任何隐式 drop。既有 4 个 acquire 点（9462/9498/9561/9666）全部从 `let _registry_guard = …` 迁移为 `let guard = …; …; let report = guard.finish(); assert_eq!(report.remaining, 0);`（ac2 在 9711-9713 已先 sleep 4100ms+reap，迁移后 remaining 必为 0）。
5. **测试 b（panic 路径）**：`catch_unwind(AssertUnwindSafe(|| { let _g = RegistryTestGuard::acquire(); panic!(…) }))` → `assert!(result.is_err())` → **同线程** `TEST_GUARD_DROP_UNRECLAIMED.with(|c| assert_eq!(c.get(), 0))`。catch_unwind 返回时 unwind 已跑完 guard 的 Drop（局部变量先销毁），账本已写；Rust 每个测试独占线程，thread_local 天然 per-test 隔离——**不再存在「断言先于 drop 执行」的恒真窗口，也无全局 Atomic 并行污染**。
6. **不改变生产**：全部位于 `#[cfg(test)] mod tests`（6042 起）；生产 `with_unreaped_registry`（cfg(not(test)) 1727-1731）字节不动。风险披露：`finish` 的 Arc 等望最坏 +2s（EXCLUSIVE 已释放后才等，不占串行锁）；正常路径零成本。

### 3.4 R2-F04：真实线程账本断言（P1-2 重做）[建议]

**v1 撤销项**：不在 multichannel_stress_tests.rs:797 断言 `threads_spawned/threads_joined`——该行所在 fault 函数**没有**这两个变量（797-798 只打印结构常量 `channel_reader_writer_threads=20*2` 与 pre-drop 的 `joined_flags`），v1 的写法不可编译。

**修订（全部可编译、断言真实观察点）**：

1. **helper 账本（real-core 场景）**：`run_real_core_scenario` 在 scope 结束（555 `});`，全部 ping/cancel/sampler worker 已 join）与 557 wall 计算之间加 `assert_eq!(threads_spawned, threads_joined)`（变量即 417-418 的局部计数器，463/532/554 累加点不变）。**注明语义**：它只证明「场景自建的测试 helper 线程全部 join」，**不是** channel reader/writer 的 join 证据。
2. **reader/writer join 账本（fault 与 real-core 通用通路）**：`ChildIdentity.worker_flags`（131）持有 `resources_for_test()`（3200-3205）返回的 4 个 Arc——`[reader_finished, writer_finished, reader_joined, writer_joined]`——在 channel Drop 后仍存活（PID ledger 235-239 正为此保活）。fault 场景在 `take_ledger()`（805）+ 逐 id `assert_pid_gone`（806-809，其 199-205 已对每 channel 有界等待并断言 `both reader/writer must finish AND be joined` + handle 槽清零）**之后**、peak 断言（811）之前，加聚合账本断言：
   ```rust
   let all_workers_finished_and_joined = identities.iter()
       .all(|id| id.worker_flags.iter().all(|f| f.load(Ordering::SeqCst)));
   assert!(all_workers_finished_and_joined,
       "join ledger: all 20x2 fault reader/writer workers must be finished+joined");
   ```
   此时每个 id 已各自通过 `assert_pid_gone` 的 30s 有界等待，聚合断言零额外等待、纯账本汇总。real-core 场景（574 起同一 `assert_pid_gone` 通路）自动获得同等证据。
3. **797-799 行**：保留原样，上方加注释：「`channel_reader_writer_threads` 是场景结构常量（20×2），非运行时计数；真实 join 证据见下方 `assert_pid_gone` 与聚合 join ledger」。
4. **child_lock 项**：见 §3.2。
5. **测试计划**：默认套件跑 §3.2（153 口径）；两 stress 场景抽跑核新断言，预期 helper 账本与聚合 join 账本全过、fault 仍于 819-822 exit101（BLOCKED 保留）。若聚合 join 断言失败 = 存在未 join 的 reader/writer（holder 退避超 30s 或泄漏），停下诊断——这正是该断言要抓的缺陷类别。
6. **不改变生产**：两文件改动均在 `#[cfg(test)]` 面；`resources_for_test` 既有签名不动。

### 3.5 R2-F05：fail-closed 直接分支与 owner mismatch（library_bridge.rs:1706-1727，cfg(test)）[建议]

维持 v1 两测试，补 **P2-4 握手**：fail-closed 测试中辅助线程改为「lock 拿到后经 `mpsc::channel` 发信号再持锁 ≥60ms」；owner 线程 `rx.recv()` 确认已持锁后才 `catch_unwind(AssertUnwindSafe(|| with_unreaped_registry(...)))` 断言 panic 含 `fail-closed`（1716-1721 的 30ms 超时 None 分支确定性触发）；结束后有界 join 辅助线程（≤1s，超时 = 测试失败）。owner mismatch 分支维持 v1（1712-1714 `_ =>` 走 global、私有 registry 状态不变）。预期默认套件 153→157（F03 测试 a/b 合并计入 F05 的两个新测试后总计 +4，以实施时清单为准）。

---

## 4. 结论与裁定项

**判断**：
1. 本 v2 设计对 4 条 P1 逐条闭合（§0 对照表）、6 条 P2 一并处置，为**可释放**的完整设计切片——按任务卡 AC4，仍须由 Codex 冻结新 head SHA 并新 Appointment 交独立复核（上下文独立、只读被审 head）后才能定案；本交付不自批。
2. 父 Task（GIT-CLEAN-RUST-ISOLATION-1）AC3 真实 32 饱和：**读代码推断 + r2 实测（peak=0）支持结构性不可达**，且论证已覆盖全部四个 track 入口（TA..TD）；确定性反证窗口收敛于共同前置 P 的 F1 组合，由 AC2-L1 检验。L1 落地实测前 AC3 维持 BLOCKED。

**需 Codex/用户裁定**：
1. AC3 口径（同 v1：L1 实测 `peak==0` 后是否改判「不可达证明 + L2 边界验证」或永久 BLOCKED）。
2. 实施范围冻结：L1 v2/L2/R2-F02..05 若采纳，另立实施 Task（Codex 冻 SHA）。
3. §3.2 helper 共享方式：`pub(crate)` 单一来源（建议）vs 就地复制。

## 5. 交付说明（P2-6 处置，Codex/DSH 侧执行）

本 v2 落盘时应冻结 **design-only head**：仅含 `verification/GIT-CLEAN-RUST-CAPACITY-DESIGN-1/DESIGN.md`（v2 全文）、新增 `HANDOFF.md`（记录设计基准 `1829a38`、复核报告引用、v1→v2 修订对照）与 Task 卡 `allowed_paths` 更新；不再混入 `check.ps1`/starter 等其它治理改动（v1 交付 commit `3ca77fc` 的教训，见复核 P2-6）。

---

**推荐下一步**：本 v2 全文交 DSH 派发新的上下文独立 design-reviewer 子 agent 复核（只读本 v2 + `1829a38`，重点核 §0 对照表四条 P1 是否闭合）；复核通过后由 Codex 冻结实施 Task 承载 L1 v2 对照实验与 R2-F02..05。本会话只读，无文件改动、无 commit。

---

以上就是修订后的完整 DESIGN v2（含「本次修订对照」开篇节）。四条 P1 的闭合方式概括：**P1-1** 用 TA..TD 四入口全表 + F5 + 「共同前置 P」重构论证（不可达结论保留，支柱换掉）；**P1-2** 撤销 797 处不可编译断言，改用 555 后的局部变量断言 + `worker_flags` 聚合 join 账本；**P1-3** B 自写 pidfile 给出完整发现→taskkill→复核链，fail-loud 兜底；**P1-4** `finish()` 显式收尾读返回值 + thread-local 账本，断言时序与并行污染同时修复。

---

## DSH 集成附记 v3（2026-11-17）：第二轮复核余 P1=2，ZCode 已给修订段（待第三轮确认）

第二轮复核（同一独立复核者，head `759687d59`）：**verdict2: BLOCKED**，P1-2 与 P1-4 仍不成立（P1-1、P1-3 已 PASS）。

ZCode 第三轮修订（session `sess_d2430af2-3d80-4fbe-a6e0-7b51c2578cfe`，仅替换受影响章节）：

- **P1-2**：fault 场景 `for id in &identities`（按引用遍历，`ChildIdentity` 无 `Clone`），
  聚合 join 账本断言保留在循环之后、peak 断言之前；`assert_pid_gone` 本就收 `&ChildIdentity`，调用改为 `assert_pid_gone(scenario, id)`。
- **P1-4**：`RegistryTestGuard` 增加 `cleaned: bool` 幂等短路（`finish(self)` → `cleanup()` 后 Drop 再进一次时零副作用返回）；
  slot 清除改为 **owner-aware**（只清 owner 是本线程的 slot，二次执行时不会误清别的测试的 override）；账本只在非短路分支累加一次。

以下为 ZCode 修订段原文（v3 候选），未经第三轮复核，**仍未释放**。


# P1-2 / P1-4 修订段落（DESIGN v2 → v3，只替换受影响章节）

## 修订段 1：P1-2 —— 替换 DESIGN.md §3.4 第 2 点

**改法**：fault 场景 807 循环改为**按引用遍历**（`&identities`），聚合断言位置**保持不变**（`assert_pid_gone` 循环之后、811 peak 断言之前）。`ChildIdentity`（stress:118-133）无 `Clone` derive，克隆方案需额外改测试面，不取；`assert_pid_gone` 签名（195：`fn assert_pid_gone(scenario: &str, id: &ChildIdentity)`）本就收引用，按引用遍历是最小改法。[建议]

```rust
// multichannel_stress_tests.rs（fault 场景，原 805-809 修订）：
let identities = take_ledger();                                              // 805 原样
assert_eq!(identities.len(), 20, "OS identity checks must cover all fault channels");  // 806 原样
for id in &identities {          // 807 原 `for id in identities`（按值 move）→ 改借用
    assert_pid_gone(scenario, id);   // 808 原 `&id` → `id`（id 已是 &ChildIdentity）
}
// 新插入（809 之后、811 peak 断言之前）——聚合 join 账本断言：
let all_workers_finished_and_joined = identities
    .iter()
    .all(|id| id.worker_flags.iter().all(|f| f.load(Ordering::SeqCst)));
assert!(
    all_workers_finished_and_joined,
    "join ledger: all 20x2 fault reader/writer workers must be finished+joined"
);
```

**断言位置说明** [推断]：

- **留在循环后（不前移）**：`assert_pid_gone`（195-233）内部 199-202 先做 ≤`CLEANUP_BUDGET`(30s) 有界等待，204 逐 id 断言 `worker_finished_joined` 全 true、205 断言 handle 槽清零。循环后读 `worker_flags` 时每 id 已逐个通过该断言——聚合读数**零额外等待、纯汇总**；失败只能归因于 PID ledger/flags 保活语义（235-239）被破坏，正是该断言要抓的缺陷类别。
- **不移到 move 之前**：199-202 的等待发生在逐 id 断言内部，循环**前**读 flags 存在假阴性窗口（某 worker 尚未置位，聚合先失败——失败为真但归因错误为「读得太早」），且丢失「逐 id 已等待」的时序保证。
- `joined_flags`（661 定义、764 push）维持原状：它记录 Drop **前**的 pre-drop 标志，定位是机制证据，不承担 post-drop join 账本职责（本轮复核已确认其不可替代）。
- **判别力诚实边界**：204 已逐 id 断言同一事实，聚合断言不引入新观察点；其价值是 (a) 单条汇总 ledger 防将来削弱 204 断言面的回归，(b) 与 §3.4 第 3 点的 797 行注释配合，杜绝 `20*2` 结构常量被误读为运行时 join 计数。
- **real-core 侧（574-578）不改**：v2「real-core 自动获得同等证据」经 199-205 的逐 id 断言即成立；`for id in identities`（576）后无对 `identities` 的再使用，无 E0382 问题。若实施时希望 real-core 也加同款聚合断言，**必须**同步把 576 改为 `for id in &identities`（调用改 `assert_pid_gone(scenario, id)`）——两选项二选一，实施时定案。[建议]

**§0 对照表 P1-2 行**追加一句：「fault 侧 807 循环改 `&identities` 借用遍历（E0382 修复），聚合断言位置不变」。

---

## 修订段 2：P1-4b —— 替换 DESIGN.md §3.3 修订点 1/2/3，并改写第 4 点断言

**改法**：`cleaned: bool` done 标记为主修复（cleanup 一次性执行）+ slot 清除改 **owner-aware** 为纵深防御；`finish` 不采用 `ManuallyDrop`/`mem::forget`。[建议]

**1. 结构体（6069-6072）加一个字段，`acquire()`（6096-6099）初始化为 `false`**：

```rust
struct RegistryTestGuard {
    _exclusive: Option<std::sync::MutexGuard<'static, ()>>,
    registry: TestRegistry,
    cleaned: bool,   // P1-4b：cleanup 一次性执行标记
}
```

**2. cleanup 提取（原 Drop 主体 6118-6145）+ 开头幂等短路 + owner-aware slot 清除**：

```rust
fn cleanup(&mut self) -> (usize, usize) {
    if self.cleaned {
        // P1-4b：finish(self) 返回时 self 析构会再次进入这里；
        // 此时 EXCLUSIVE 已释放、slot 可能已属别的测试——必须零副作用返回。
        return (0, 0);
    }
    self.cleaned = true;
    let (reaped, remaining) = self.reap_now(Duration::from_millis(2000));
    if remaining > 0 {
        eprintln!(
            "[registry-test] guard drop: reaped {reaped}, {remaining} worker(s) still unfinished (their bounded test threads will detach and end on their own)"
        );
        // 账本只在此非短路分支累加——天然只记一次（修复二次累加）
        TEST_GUARD_DROP_UNRECLAIMED.with(|c| c.set(c.get() + remaining));
    }
    {
        let mut slot = TEST_REGISTRY_OVERRIDE
            .lock()
            .unwrap_or_else(|poisoned| poisoned.into_inner());
        // P1-4b 纵深防御：只清 owner 仍是本线程的 slot
        // （比较方式同既有安装验证 6087-6089）
        let mine = slot
            .as_ref()
            .map(|(owner, _)| *owner == std::thread::current().id())
            .unwrap_or(false);
        if mine {
            *slot = None;
            assert!(
                slot.is_none(),
                "RegistryTestGuard: TEST_REGISTRY_OVERRIDE could not be cleared"
            );
        }
        // owner 非本线程 = 另一测试在 EXCLUSIVE 释放后合法安装的 override，
        // 不属于本 guard，绝不清除，也不视为本 guard 的失败。
    }
    IN_REGISTRY_TEST.with(|flag| flag.set(false));
    drop(self._exclusive.take());
    (reaped, remaining)
}
```

相对现有 Drop 的**唯一行为变化**：slot 清除从无条件 `*slot = None`（6133）变为 owner 检查后清除。首次 cleanup 运行时 slot 必然 owner==本线程（EXCLUSIVE 仍持有、串行保证），清除行为与现状一致；owner mismatch 只可能出现在二次执行场景，不清是正确语义。[推断]

**3. `finish` 与 `Drop`**：

```rust
fn finish(mut self) -> GuardFinishReport {
    let (reaped, remaining) = self.cleanup();   // 唯一一次完整 cleanup（cleaned 置 true）
    let mut arc_released = false;
    let deadline = Instant::now() + Duration::from_secs(2);
    while Instant::now() < deadline {
        if Arc::strong_count(&self.registry) == 1 { arc_released = true; break; }
        std::thread::sleep(Duration::from_millis(10));
    }
    if Arc::strong_count(&self.registry) == 1 { arc_released = true; }
    GuardFinishReport { reaped, remaining, arc_released }
    // 返回值移出后 self 析构 → Drop::drop → cleanup() 二次进入 →
    // cleaned 已为 true，短路返回 (0,0)：不碰 slot、不 reap、不记账、
    // _exclusive 已 None；registry Arc 随字段正常析构释放。
}

impl Drop for RegistryTestGuard {
    fn drop(&mut self) {
        let _ = self.cleanup();
    }
}
```

不采用 `mem::forget(self)`/`ManuallyDrop` 的理由 [推断]：forget 会跳过**全部**字段析构——registry Arc 泄漏，且正确性依赖「cleanup 必已先跑」的隐含前提；ManuallyDrop 需 unsafe 或同样放弃字段析构。done 标记让 panic unwind 路径（Drop 首次执行）与显式路径共享同一段幂等逻辑，全安全代码、零泄漏。

**4. 时序（P1-4b 修复后的完整链）** [推断]：

- **正常路径**：`guard.finish()` 进入（EXCLUSIVE 持有、slot owner=本线程）→ cleanup#1（cleaned=true → reap_now(2s) → 账本仅 remaining>0 时累加 → owner 检查 mine=true 清 slot+验证 → `IN_REGISTRY_TEST=false` → 释放 EXCLUSIVE）→ Arc 等待 ≤2s（此窗口另一测试 acquire 并安装自己的 slot——合法，互不干扰）→ report 移出 → `self` 析构 → Drop → cleanup#2 **短路**（返回 (0,0)，零副作用）→ 调用方拿到 report。
- **panic unwind**：guard 局部变量 drop → cleanup#1 完整执行（同上）→ 无 Arc 等待（兜底要快）。catch_unwind 返回时 unwind 已跑完 guard Drop，账本已写。

**5. 断言（测试 a，替换 v2 §3.3 第 4 点）**：

```rust
let report = guard.finish();
assert_eq!(report.remaining, 0, "guard finish: no unreclaimed workers allowed");
assert!(report.arc_released, "guard finish: registry Arc must be back to 1");
TEST_GUARD_DROP_UNRECLAIMED.with(|c| assert_eq!(c.get(), 0));
```

- **时序依据** [推断]：Rust 语义上按值参数 `self` 在返回值移出之后、调用方语句结束之前析构——`finish()` 返回时 cleanup#2 已执行（被短路），账本断言**即刻可读**，不存在「断言先于 drop」的恒真窗口。
- **账本断言的回归探针作用**：`report.remaining==0` ⇒ cleanup#1 未记账；若 done 短路将来失效（回归），cleanup#2 会二次 reap/记账或触碰他人 slot——账本 >0 或其他测试失败即可被抓。
- 测试 b（`catch_unwind` 后**同线程**读 thread-local 断言）与既有 4 个 acquire 点迁移（9462/9498/9561/9666 → `guard.finish()`）维持 v2 原文不变。

**6. P2-8 随本修订一并闭合**：finish 的 Arc 等待仍在 EXCLUSIVE 释放后进行（不占串行锁），其与第二次 cleanup 的组合危害已由「done 短路 + owner-aware」双层消除。§0 对照表 P1-4 行追加「done 短路 + owner-aware slot 清除，P2-8 一并闭合」，P2 处置一览补 P2-8 行。

风险披露：cleanup#1 中途 panic（如 slot 清除验证 assert 失败）时 Drop 不会重入同一 guard（正在 unwind 中），与 v1/v2 相同，非新增风险；owner-aware 后该 assert 仅在 mine 分支内，触发面更小。全部改动位于 `#[cfg(test)] mod tests`（6042 起），生产零改动。

---

## 是否需同步改 DSH 附记

- **Task 卡**（`doc/tasks/GIT-CLEAN-RUST-CAPACITY-DESIGN-1.md`）：AC3 只有需求级一句「guard正常/异常收尾和Arc所有权；实际线程join账本」，**不含机制级描述，无需改**。
- **复核报告**（`doc/reviews/…2026-11-17.md`）：历史 Review 按治理规则保持原字节，**不改**。
- **需改的只有 DESIGN.md 自身**：§3.3（上述修订段 2 替换）、§3.4 第 2 点（修订段 1 替换）、§0 对照表 P1-2/P1-4 两行补注、P2 一览补 P2-8。`checkpoint.md` 无相关内容，不改。

---

**推荐下一步**：本两段修订交 DSH 集成落盘为 DESIGN v3（建议一并按 P2-11 冻结 design-only head + 补 `HANDOFF.md`），并派第三轮上下文独立 design-reviewer 复核（只读 v3 + `1829a38`，重点核两片段可编译性、finish 返回时序、owner-aware 语义）。本会话只读，无文件改动、无 commit。

---

## DSH 集成附记 v4（2026-11-17）：第三轮复核 **RELEASABLE**，设计切片收口

第三轮窄确认（同一独立复核者，head `ab6a0e6ef`）：**verdict3: RELEASABLE**，P1 剩余 **0**（仅余 P2）。

- **P1-2 PASS**：`ChildIdentity`（`multichannel_stress_tests.rs:118-133`）无 `Clone`；`assert_pid_gone`（:195）收 `&ChildIdentity`；
  `for id in &identities` + `assert_pid_gone(scenario, id)` 类型匹配，循环后 `identities.iter()` 仍可借用，无 E0382。
- **P1-4 PASS**：`cleaned` 首次 cleanup 置位后，`finish`→Drop 的 cleanup#2 短路；账本只累加一次、slot 仅 owner-aware 清除、
  `_exclusive` 不会二次 take，EXCLUSIVE 释放后的 Arc 等待不再误清他测 slot。
- **遗留 P2（不阻断发布，属实施任务）：** ①补 `GuardFinishReport` 结构定义；②修正「Drop 不会重入」措辞（实际会进入但被短路）；
  ③评估 `cleaned=true` 后理论 panic 路径的清理短路。

**结论**：本设计**可释放**（releasable），但**仍未实施**：产品源码零改动、压力测试未跑。实施须另立 Task 并重新冻结范围。

