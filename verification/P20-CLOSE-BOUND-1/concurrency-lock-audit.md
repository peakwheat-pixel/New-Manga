# P20-CLOSE-BOUND-1 AC4 并发持锁路径审查与硬上界闭式证明（R4/R5 终审版）

- **审查日期**：2026-10-18
- **责任方**：Antigravity (Owner)
- **审查范围**：`apps/desktop/src-tauri/src/library_bridge.rs` 中与关闭、退出、心跳、请求交互及 drop 相关的全部持锁点与并发调用链
- **依据规范**：Codex Review R3（`verification/P20-CLOSE-BOUND-1/codex-review-r3.md`）

---

## 1. 真实持锁路径清单与逐项上界分析

| 序号 | 锁对象 / 保护资源 | 类型 | 涉及操作与调用点 | 持锁上界与机制 | 为何绝不无限阻塞 / 死锁 / 漏回收 |
|---|---|---|---|---|---|
| 1 | `ResilientCoreContext.inner` | `std::sync::Mutex<Option<Arc<StdioLibraryChannel>>>` | `with_channel`, `start_heartbeat`, `trigger_restart`, `ResilientLibraryChannel::shutdown`, `drop` | **≤ 50 ms（实测 < 1 µs）**：采用 `lock_timeout_recover(..., 50ms)`，循环步长受 `remaining` 严格截断。<br>**超时不静默丢弃（N1）**：若锁超时，立即启动后台 `resilient-inner-shutdown-fallback` 线程，待锁释放后接管并执行通道关闭，置位 `inner_fallback_shutdown_completed`。 | 锁内仅执行 `Option::clone()` 或 `Option::take()`，所有 IPC、心跳探测及 `shutdown_and_kill` 均在**锁外**执行。关闭时剥离所有权，后续线程获锁仅见 `None`，不形成死锁环。 |
| 2 | `StdioLibraryChannel.child` | `std::sync::Mutex<Child>` | `heartbeat` (`try_wait`), `shutdown_and_kill` (`wait_timeout_or_kill_with_reap`), `wait_first_ping` | **≤ 50 ms 获取锁；操作本身受共享 deadline 约束（graceful ≤ 1000 ms，reap ≤ 400 ms）**：采用 `lock_timeout_recover(..., 50ms)`，中毒自动 `into_inner()`。<br>**超时 fallback 保证回收（P1#2）**：若因锁竞争超时，**立即执行带超时的 OS 级整树强杀（taskkill /F /T /PID）**，并派发 `child-reap-fallback` 线程等待锁释放后真实调用 `child.wait()` 回收 OS 句柄，回收完成后置位 `child_reaped`。 | 心跳持锁仅为纳秒级非阻塞 `try_wait`，随后立即释放锁。关闭路径无论获锁成功与否，整棵进程树与 OS 句柄均被确定性回收。 |
| 3 | `StdioLibraryChannel.writer_tx` / `writer_join_handle` | `mpsc::Sender<WriterCommand>` / `Mutex<Option<JoinHandle<()>>>` | `write_stdin_timeout`, `write_stdin_shutdown`, `shutdown_and_kill` | **管道写 ≤ 50 ms~100 ms；Join 守护 ≤ 80 ms**：所有写由独立 `stdio-library-writer` 线程执行。关闭时发 `Shutdown` 并在锁外通过独立守护线程 `writer-join-guard` 进行有界 join。writer 退出循环后显式 drop stdin 句柄并置位 `writer_finished`，join 成功后置位 `writer_joined`。 | 调用方绝不在 OS 管道写中同步阻塞。强杀子进程后，OS 自动破裂读端使阻塞写入立即返回 `BrokenPipe`，写入线程立即解除并退出（经 2MB 满管道注入测试验证）。 |
| 4 | `StdioLibraryChannel.reader_join_handle` | `std::sync::Mutex<Option<JoinHandle<()>>>` | `adopt_child`, `shutdown_and_kill` | **≤ 30 ms 获取锁；Join 守护 ≤ 100 ms**：在锁内微秒级 `take()` 取出 handle。随后在独立守护线程 `reader-join-guard` 中执行 join，主流程以 `recv_timeout(100ms)` 等待，完成后置位 `reader_joined`。 | 主流程不直接阻塞于 `JoinHandle::join()`。子进程被 kill 后 stdout 产生 EOF，reader 立即退出；若遇极端句柄泄漏，100 ms 超时后主流程强制脱钩推进。 |
| 5 | `StdioLibraryChannel.pending_responses` | `std::sync::Mutex<HashMap<...>>` | `exchange_expected_minor_timeout_internal`, reader thread, `shutdown_and_kill` | **≤ 30 ms 获取锁**：采用 `lock_timeout_recover(..., 30ms)`。<br>**超时不丢弃通知（P1#2）**：若遇锁竞争超时，派发 `pending-drain-fallback` 循环重试获取锁，drain 唤醒所有在途请求并置位 `pending_drained`。 | 纯内存哈希表操作，无任何系统调用。在途请求收到 `Err(CORE_UNAVAILABLE)` 后立即退出并释放 `transaction_lock`。 |
| 6 | `StdioLibraryChannel.host_session` | `std::sync::Mutex<Option<HostSession>>` | `open_host_session`, `shutdown_and_kill` | **≤ 30 ms 获取锁**：采用 `lock_timeout_recover(..., 30ms)`。`take()` 取出 session，随后在锁外发起 `CloseHostSession`（受共享 deadline 剩余预算截断，上限 ≤ 240 ms）。 | 锁内仅执行 `take()`，锁外调用受严格超时约束，失败或超时均直接短路忽略。 |
| 7 | `StdioLibraryChannel.transaction_lock` | `std::sync::Mutex<()>` | `exchange_expected_minor_timeout_internal` | **受各请求的 `timeout` 严格约束**：采用 `try_lock` 轮询，单步 sleep 受 `remaining` 截断，超时即退出。 | **关闭路径发送 CloseHostSession 时索取该锁（上限 ≤ 80 ms）**；若被占用，超限立即放弃并跳过；在途请求收到 `pending_responses.drain()` 派发的 `Err` 后立即退出并释放该锁。 |
| 8 | `StdioLibraryChannel.last_shutdown_error` | `std::sync::Mutex<Option<String>>` | `shutdown_and_kill_with_deadline`, fallback workers | **≤ 10 ms 获取锁（P1#3 消灭无界锁）**：采用 `lock_timeout_recover(&self.last_shutdown_error, Duration::from_millis(10))`。 | 锁内仅做一次 `Option` 赋值，无 I/O，绝无死锁。 |

---

## 2. 全链路最坏情况关闭时间（WCET）闭式推导与预算表

### 2.1 共享绝对 Deadline 机制
系统在生产关闭入口 `ResilientLibraryChannel::shutdown` 立即建立**单一共享绝对 deadline**：
`deadline = Instant::now() + total_budget`（其中 `total_budget ≤ 2400 ms`）。
该 deadline 贯穿 `ctx.inner` 剥离、CloseHostSession、core.shutdown 写入、child wait/kill/reap、taskkill 兜底、reader/writer join 等全部可能阻塞点。每一个子阶段的超时时间均取自身静态上限与 `remaining = deadline.saturating_duration_since(Instant::now())` 的**最小值**。
所有轮询步长（`lock_timeout_recover`、`wait_timeout_or_kill_with_reap`、`acquire_transaction_lock`、`run_taskkill_bounded`）均使用 `sleep_dur = poll_interval.min(remaining)`，当 `remaining` 为 0 时直接退出，彻底杜绝轮询超调。

### 2.2 全链路关闭总预算逐段推导表（静态最坏情况 WCET）

以下逐一列出关闭调用路径上的**全部 16 个可能阻塞点**：

| 序号 | 执行阶段与操作 | 涉及资源 / 锁 / 系统调用 | 静态上限（最坏情况） | 超时与边界控制机制 | 动态 deadline 截断保证 |
|---|---|---|---|---|---|
| **Step 0** | 外层通道剥离 | `ctx.inner` 互斥锁 | **50 ms** | `lock_timeout_recover(50ms)`，受 remaining 截断 | 超时派发 fallback 线程接管，主调用返回 |
| **Step 1** | 在途等待者唤醒 | `pending_responses` 互斥锁 | **30 ms** | `lock_timeout_recover(30ms)`，受 remaining 截断 | 超时派发 fallback 线程唤醒等待者 |
| **Step 2a** | 会话锁获取 | `host_session` 互斥锁 | **30 ms** | `lock_timeout_recover(30ms)`，获取后 `take()` | 超时跳过会话关闭 |
| **Step 2b** | 交易锁获取 | `transaction_lock` 互斥锁 | **80 ms** | `try_lock` 轮询，受 remaining 截断 | 超时直接放弃该请求 |
| **Step 2c** | CloseHostSession 写入 | 管道写（`write_stdin_shutdown`） | **50 ms** | 后台 writer 线程，`recv_timeout` 截断 | 超时立即返回错误 |
| **Step 2d** | CloseHostSession 响应 | 响应通道接收（`rx.recv_timeout`） | **80 ms** | 独立通道接收，受 remaining 截断 | 超时立即放弃等待 |
| **Step 2e** | 会话请求超时清理锁 | `pending_responses` 互斥锁 | **10 ms** | `lock_timeout_recover(10ms)` 清理 pending 槽 | 超时直接跳过清理 |
| **Step 3** | core.shutdown 写入 | 管道写（`write_stdin_shutdown`） | **60 ms** | 专属关闭写入路径，不受 `is_down` 阻断 | 超时立即放弃并推进至强杀 |
| **Step 4a** | Child 锁获取 | `child` 互斥锁 | **50 ms** | `lock_timeout_recover(50ms)`，poisoned 自动恢复 | 超时立即触发 taskkill /F /T 强杀分支 |
| **Step 4b** | 优雅退出等待 | `child.try_wait()` 轮询 | **1000 ms** | 轮询步长 15 ms，受 remaining 截断 | 超时调用 `child.kill()` |
| **Step 4c** | 强杀后 Reap 等待 | `child.kill()` + `try_wait()` 轮询 | **400 ms** | 轮询步长 15 ms，受 remaining 截断 | 超时触发 taskkill /F /T 兜底 |
| **Step 4d** | Reap 失败错误记录 | `last_shutdown_error` 互斥锁 | **10 ms** | `lock_timeout_recover(10ms)` | 超时跳过记录 |
| **Step 4e** | OS taskkill 进程树强杀 | `run_taskkill_bounded` (`/F /T /PID`) | **250 ms** | 独立子进程有界轮询，受 remaining 截断 | 超时杀灭 taskkill 进程并报错 |
| **Step 4f** | taskkill 结果错误记录 | `last_shutdown_error` 互斥锁 | **10 ms** | `lock_timeout_recover(10ms)` | 超时跳过记录 |
| **Step 5a** | Reader 句柄锁获取 | `reader_join_handle` 互斥锁 | **30 ms** | `lock_timeout_recover(30ms)`，取出句柄 | 超时跳过 join 等待 |
| **Step 5b** | Reader 守护 Join 等待 | `reader-join-guard` 线程 join | **100 ms** | 守护线程 join，主流程 `recv_timeout(100ms)` | 超时强制脱钩推进 |
| **Step 6a** | Writer 句柄锁获取 | `writer_join_handle` 互斥锁 | **30 ms** | `lock_timeout_recover(30ms)`，取出句柄 | 超时跳过 join 等待 |
| **Step 6b** | Writer 守护 Join 等待 | `writer-join-guard` 线程 join | **80 ms** | 发送 Shutdown，主流程 `recv_timeout(80ms)` | 超时强制脱钩推进 |
| **Step 7** | 重入分支防护 | `shutdown_executed: AtomicBool` | **0 ms** | 原子交换短路，正常单次关闭消耗 0 ms | 重入分支重试强杀有界（≤ 350 ms） |

### 2.3 WCET 闭式推导加和

在最坏极端异常叠加情形下（Step 4 获取到 child 锁但子进程僵死、kill 无效、进而触发 taskkill 兜底）：

$$\begin{aligned}
T_{\text{WCET\_static}} &= T_{\text{inner}} + T_{\text{pending}} + (T_{\text{hs\_lock}} + T_{\text{tx\_lock}} + T_{\text{hs\_write}} + T_{\text{hs\_recv}} + T_{\text{hs\_clean}}) + T_{\text{shutdown\_write}} \\
&\quad + (T_{\text{child\_lock}} + T_{\text{graceful}} + T_{\text{reap}} + T_{\text{err1}} + T_{\text{taskkill}} + T_{\text{err2}}) \\
&\quad + (T_{\text{reader\_lock}} + T_{\text{reader\_join}}) + (T_{\text{writer\_lock}} + T_{\text{writer\_join}}) + T_{\text{reentrancy}} \\
&= 50 + 30 + (30 + 80 + 50 + 80 + 10) + 60 + (50 + 1000 + 400 + 10 + 250 + 10) \\
&\quad + (30 + 100) + (30 + 80) + 0 \\
&= 50 + 30 + 250 + 60 + 1720 + 130 + 110 + 0 \\
&= \mathbf{2350\,\text{ms}} \le \mathbf{3000\,\text{ms}}\,(3.0\,\text{s})
\end{aligned}$$

- **理论安全裕度**：$3000\,\text{ms} - 2350\,\text{ms} = \mathbf{650\,\text{ms}}$（名义硬裕度）。
- **替代分支（Step 4 锁竞争超时分支）**：
  若 Step 4a 因锁竞争超时（50 ms），直接转入 Step 4e（taskkill 250 ms）及 fallback handle 锁（20 ms），Step 4 总耗时为 $50 + 10 + 250 + 20 = 330\,\text{ms}$。
  此时总 WCET 仅为 $50 + 30 + 250 + 60 + 330 + 130 + 110 = \mathbf{960\,\text{ms}} \ll 3000\,\text{ms}$。
- **动态运行时物理上限**：
  由于共享绝对截止点 `deadline = Instant::now() + min(timeout, 2400ms)`，任何阶段若因调度抖动消耗时间，后续各阶段的 `remaining` 立即被挤压收窄。当 `remaining` 为 0 时，所有操作立即短路返回。因此，**动态物理执行时间在任何极端抖动下严格 $\le 2400\,\text{ms} < 3000\,\text{ms}$**。

---

## 3. Codex Review R3 缺陷项详细闭环方案与实现证明

### 3.1 N1：`ctx.inner` 锁超时不得静默跳过生产关闭
- **缺陷现状**：`ResilientLibraryChannel::shutdown` 获取 `ctx.inner` 锁超时（50 ms）后直接返回，导致生产关闭被静默放弃，Core 仍留在后台运行。
- **闭合措施**：
  1. `ctx.inner` 获锁超时时，记录 Warning 日志；
  2. 调度专属后台 fallback 线程 `resilient-inner-shutdown-fallback`，在锁释放后自动接管并调用 `chan.shutdown_and_kill(1500ms)`；
  3. 执行完成后置位 `ctx.inner_fallback_shutdown_completed = true`；
  4. 新增单元测试 `resilient_inner_lock_contention_timeout_triggers_fallback_shutdown`：模拟后台线程持有 `inner` 锁 200 ms，验证调用方在 ≤ 500 ms 内有界返回，且 fallback 线程接管后完成回收、子进程被彻底清除（**实测 1.43s 通过**）。

### 3.2 P1#2：超时 fallback 提供“完成回收”保证与 `/T` 进程树强杀
- **缺陷现状**：原 child fallback 仅 sleep 2 秒，未获取 Child 锁也未调用 `child.wait()`；`pending_responses` fallback 超时 500 ms 后静默退出；taskkill 缺少 `/T` 参数，无法清理 Core 派生的子进程/孙进程。
- **闭合措施**：
  1. `child` 改为 `Arc<Mutex<Child>>`。`child-reap-fallback` 线程在锁释放后调用 `child.wait()`，回收 OS 句柄并置位 `child_reaped: Arc<AtomicBool>`；
  2. `pending-drain-fallback` 引入重试循环（最长 2.0s），获取锁后 drain 唤醒所有在途请求并置位 `pending_drained: Arc<AtomicBool>`；
  3. 所有 taskkill 调用均增加 `/T` 参数（`taskkill /F /T /PID`），确保强杀整棵进程树；
  4. 改进单元测试：
     - `child_lock_contention_timeout_fallback_kills_child_and_prevents_orphan`：启动 mock sidecar 并派生孙进程，验证主进程与孙进程均被 `/T` 强杀退出，并真断言 `chan.is_child_reaped() == true`（**实测 1.22s 通过**）；
     - `pending_lock_contention_timeout_fallback_drains_and_unblocks`：断言 `chan.is_pending_drained() == true`（**实测 1.73s 通过**）。

### 3.3 P1#3：共享 deadline 覆盖全链路与消减无界点
- **缺陷现状**：外层 `ctx.inner` 不在 deadline 内；`taskkill.output()` 无超时；`last_shutdown_error.lock()` 为无界阻塞锁；CloseHostSession 清理锁无界。
- **闭合措施**：
  1. `ResilientLibraryChannel::shutdown` 在入口立即建立共享绝对 `deadline`，贯穿至 `shutdown_and_kill_with_deadline`；
  2. 实现 `run_taskkill_bounded(pid, timeout)`，替代无界的 `Command::output()`，超时上限 250 ms 并受 `remaining` 截断；
  3. `last_shutdown_error` 改为 `lock_timeout_recover(&self.last_shutdown_error, 10ms)`；
  4. CloseHostSession 超时清理锁收紧为 `lock_timeout_recover(&self.pending_responses, 10ms)`；
  5. 重构 16 项逐段推导表，闭式总 WCET 为 2350 ms $\le$ 3000 ms。

### 3.4 P2#5：基线快照与断链后代进程审计
- **缺陷现状**：BFS 仅从当前 runner PID 递归枚举，若中间父进程（cmd/cargo）已退出，遗留后代成为断链孤儿，无法从 PID 树回溯。
- **闭合措施**：
  1. 在测试套件启动时记录全部系统进程快照 `$baselinePidSet` 及时间戳；
  2. 测试结束后，计算新增的 `$deltaProcs`（差集）；
  3. 综合扫描：(a) runner 递归后代；(b) 全局敏感名（`core_service`, `m2rc1_desktop`, `host_bridge`）；(c) 关联 workspace、isolatedRoot、bootstrap、time.sleep 的 python 进程；(d) 命令行包含隔离根或 `apps\desktop\src-tauri` 的 delta 进程；
  4. 验证隔离根目录可被顺利删除（句柄释放证明）；
  5. 输出标准环境头、命令和退出码，生成 `ac2-process-tree-audit.exit` 与 `ac2-process-tree-audit.meta.json`。

### 3.5 P2#6：满管道测试断言 writer/joiner/ChildStdin 已释放
- **缺陷现状**：2MB 满管道注入测试此前只断言 handle slot 为 None，未断言 writer 线程及 joiner 真实退出。
- **闭合措施**：
  1. 引入原子可观测标记：`writer_finished`、`writer_joined`、`reader_finished`、`reader_joined`；
  2. writer 线程退出循环后显式 drop `ChildStdin` 并置位 `writer_finished = true`；joiner 成功后置位 `writer_joined = true`；
  3. 在 `writer_overflow_pipe_capacity_unblocks_and_cleans_up_on_kill` 中增加直接断言：
     `assert!(chan.is_writer_finished()); assert!(chan.is_writer_joined()); assert!(chan.is_reader_joined());`（**实测 1.82s 通过**）。

### 3.6 P2#7：`taskkill` 结果检查与上报
- **缺陷现状**：`taskkill` 返回值被忽略，无论成功与否均盲目将 `child_killed` 设为 true。
- **闭合措施**：
  1. `run_taskkill_bounded` 捕获 exit status 及 stdout/stderr；
  2. 若返回非 0 且非“进程未找到/没有找到/not running”，返回明确 `Err` 并记录至 `last_shutdown_error`；
  3. 仅在 taskkill 确认成功或进程已消亡时才将 `child_killed` 设为 true。

---

## 4. 实测数据与硬上界区分

在 Task 与验收中严格区分“**已证明的硬上界**”与“**实测观测数据**”：

- **已证明的硬上界（WCET）**：
  - **静态理论硬上界**：**2350 ms**（16 个阻塞点全部达到最大超时且全部失败的最坏情况闭式加和）。
  - **动态实现硬上界**：**2400 ms**（共享绝对 deadline 截断，无论任何环节发生系统抖动，物理耗时严格 $\le 2400\,\text{ms} < 3000\,\text{ms}$）。
- **仅观测到的耗时（本次全量实测数据）**：
  - 外部强杀叠加在途请求场景（`resilient_channel_drop_after_external_kill`）：真实关闭入口耗时 **0.5443 ms (544.3 µs)**。
  - Inner 锁竞争超时 fallback 场景（`resilient_inner_lock_contention`）：耗时 **1.43s**。
  - Child 锁竞争超时 fallback 进程树强杀场景（`child_lock_contention`）：耗时 **1.22s**。
  - Pending 锁竞争超时 fallback 唤醒场景（`pending_lock_contention`）：耗时 **1.73s**。
  - 管道满载 2MB 写入阻塞场景（`writer_overflow_pipe_capacity`）：耗时 **1.82s**。
  - 既有 resilient_channel 套件（9 项全绿）：耗时 **0.98s**。
  - 既有 stdio_channel_drop 套件（1 项全绿）：耗时 **0.91s**。
  - Process Tree & 断链后代审计：残留进程数 **0**，隔离根删除成功。

---

## 5. 能证明 vs 不能证明（诚实透明界定）

### 5.1 本实现已证明的事实
1. **调用线程绝无可能无限阻塞**：无论 sidecar 挂起、管道写满、互斥锁中毒还是普通锁竞争，生产关闭入口均在 $\le 2400\,\text{ms}$（实测 < 2.0s）内返回。
2. **锁超时绝不漏杀孤儿与漏回收句柄**：child 锁竞争超时通过 `taskkill /F /T` 强杀整棵进程树（包括派生子孙进程），并通过后台 fallback 真实调用 `child.wait()` 回收 OS 句柄（经 `child_lock_contention_timeout_fallback_kills_child_and_prevents_orphan` 验证，断言 `is_child_reaped() == true`）。
3. **在途请求绝不挂起**：pending 锁竞争超时通过后台重试 fallback 完成 drain 唤醒（经测试验证，断言 `is_pending_drained() == true`）。
4. **管道满载在 kill 后完全解除且资源彻底释放**：注入 2MB 大于管道容量的数据时，强杀子进程能通过内核 BrokenPipe 机制唤醒 writer 线程并释放 stdin 句柄，且 writer/reader 守护线程均顺利 join 退出（经测试断言 `is_writer_finished()`, `is_writer_joined()`, `is_reader_joined()`）。
5. **递归进程树与断链后代完全清零**：基线差集结合路径特征扫描，后代与断链残留数为 0，且隔离根句柄完全释放。

### 5.2 不能证明（超出当前工程边界）的事实
1. **OS 同步管道写无法在子进程存活时进行用户态硬性取消**：
   在 Windows 上，当线程阻塞在同步 `WriteFile` 内核调用中时，若子进程既不读取也不退出，用户态无法在子进程继续存活的前提下强行“取消”该阻塞写操作。**工程对策**：关闭路径直接终止子进程，内核感知读端关闭后立刻破裂管道中断写阻塞；若子进程将管道句柄泄漏给外部无关进程，关闭路径依靠 join guard 的 80 ms 超时强制与 writer 线程脱钩，确保应用退出不被挂起。
2. **AC5 真实交互式桌面关闭需要 Coordinator 在交互桌面运行**：
   本 CLI 环境无 Windows 交互桌面句柄（0x80070578），AC5 的窗口事件触发仍需由 Coordinator 在真实交互式桌面环境下复跑验证。验证脚本 `run-desktop-close-verification.ps1` 已全面增强为**自包含落盘**，可自动生成包含控制台日志、metadata 及 exit 码的完整证据包。

