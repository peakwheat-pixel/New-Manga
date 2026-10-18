# P20-CLOSE-BOUND-1 AC4 并发持锁路径审查与硬上界闭式证明（R5 终审版）

- **审查日期**：2026-10-18
- **责任方**：Antigravity (Owner)
- **审查范围**：`apps/desktop/src-tauri/src/library_bridge.rs` 中与关闭、退出、心跳、请求交互及 drop 相关的全部持锁点与并发调用链
- **依据规范**：Codex Review R4（`verification/P20-CLOSE-BOUND-1/codex-review-r4.md`）

---

## 1. 真实持锁路径清单与逐项上界分析

| 序号 | 锁对象 / 保护资源 | 类型 | 涉及操作与调用点 | 持锁上界与机制 | 为何绝不无限阻塞 / 死锁 / 漏回收 |
|---|---|---|---|---|---|
| 1 | `ResilientCoreContext.inner` | `std::sync::Mutex<Option<Arc<StdioLibraryChannel>>>` | `with_channel`, `start_heartbeat`, `trigger_restart`, `ResilientLibraryChannel::shutdown`, `drop` | **≤ 50 ms（实测 < 1 µs）**：采用 `lock_timeout_recover(..., 50ms)`，单步受 `remaining` 严格截断。<br>**超时不静默丢弃且继承绝对 deadline（N1 终版）**：若锁超时，派发 `resilient-inner-shutdown-fallback` 线程。fallback **继承同一绝对 deadline**（不重新开预算），且**获锁后立即释放 guard**，在锁外执行关闭；spawn 失败与超时均显式上报并置位标记。 | 锁内仅执行 `Option::clone()` 或 `Option::take()`，所有 IPC、心跳探测及 `shutdown_and_kill` 均在**锁外**执行。关闭时剥离所有权，后续线程获锁仅见 `None`，不形成死锁环。 |
| 2 | `StdioLibraryChannel.child` | `std::sync::Mutex<Child>` | `heartbeat` (`try_wait`), `shutdown_and_kill` (`wait_timeout_or_kill_with_reap`), `wait_first_ping` | **≤ 50 ms 获取锁；操作本身受共享 deadline 约束（graceful ≤ 1000 ms，reap ≤ 400 ms）**：采用 `lock_timeout_recover(..., 50ms)`，中毒自动 `into_inner()`。<br>**超时 fallback 保证回收（P1#2 终版）**：若因锁竞争超时，**立即执行带超时的 OS 级整树强杀（taskkill /F /T /PID）**，并派发 `child-reap-fallback` 线程。获锁后执行**有界轮询 `try_wait()`（≤ 400ms），绝不执行无界 `wait()`**；回收完成后置位 `child_reaped`。 | 心跳持锁仅为纳秒级非阻塞 `try_wait`，随后立即释放锁。关闭路径无论获锁成功与否，整棵进程树与 OS 句柄均被确定性回收。 |
| 3 | `StdioLibraryChannel.writer_tx` / `writer_join_handle` | `mpsc::Sender<WriterCommand>` / `Mutex<Option<JoinHandle<()>>>` | `write_stdin_timeout`, `write_stdin_shutdown`, `shutdown_and_kill` | **管道写 ≤ 50 ms~100 ms；Join 守护 ≤ 80 ms**：所有写由独立 `stdio-library-writer` 线程执行。关闭时发 `Shutdown` 并在锁外通过独立守护线程 `writer-join-guard` 进行有界 join。writer 退出循环后显式 drop stdin 句柄并置位 `writer_finished`，join 成功后置位 `writer_joined`。 | 调用方绝不在 OS 管道写中同步阻塞。强杀子进程后，OS 自动破裂读端使阻塞写入立即返回 `BrokenPipe`，写入线程立即解除并退出（经 2MB 满管道注入测试验证）。 |
| 4 | `StdioLibraryChannel.reader_join_handle` | `std::sync::Mutex<Option<JoinHandle<()>>>` | `adopt_child`, `shutdown_and_kill` | **≤ 30 ms 获取锁；Join 守护 ≤ 100 ms**：在锁内微秒级 `take()` 取出 handle。随后在独立守护线程 `reader-join-guard` 中执行 join，主流程以 `recv_timeout(100ms)` 等待，完成后置位 `reader_joined`。 | 主流程不直接阻塞于 `JoinHandle::join()`。子进程被 kill 后 stdout 产生 EOF，reader 立即退出；若遇极端句柄泄漏，100 ms 超时后主流程强制脱钩推进。 |
| 5 | `StdioLibraryChannel.pending_responses` | `std::sync::Mutex<HashMap<...>>` | `exchange_expected_minor_timeout_internal`, reader thread, `shutdown_and_kill` | **≤ 30 ms 获取锁（主路径）；注册锁 ≤ 100 ms（受剩余预算截断）**：采用 `lock_timeout_recover`。<br>**超时不丢弃通知（P1#2 终版）**：若遇锁竞争超时，派发 `pending-drain-fallback` 循环重试获取锁，drain 唤醒所有在途请求并置位 `pending_drained`；spawn 失败显式记录到错误槽。 | 纯内存哈希表操作，无任何系统调用。在途请求收到 `Err(CORE_UNAVAILABLE)` 后立即退出并释放 `transaction_lock`。 |
| 6 | `StdioLibraryChannel.host_session` | `std::sync::Mutex<Option<HostSession>>` | `open_host_session`, `shutdown_and_kill` | **≤ 30 ms 获取锁**：采用 `lock_timeout_recover(..., 30ms)`。`take()` 取出 session，随后在锁外发起 `CloseHostSession`（受外层会话预算 `min(240ms, rem)` 严格截断）。 | 锁内仅执行 `take()`，锁外调用受严格超时约束，失败或超时均直接短路忽略。 |
| 7 | `StdioLibraryChannel.transaction_lock` | `std::sync::Mutex<()>` | `exchange_expected_minor_timeout_internal` | **受各请求的 `timeout` 严格约束**：采用 `try_lock` 轮询，单步 sleep 受 `remaining` 截断，超时即退出。 | **关闭路径发送 CloseHostSession 时索取该锁（上限 ≤ 80 ms）**；若被占用，超限立即放弃并跳过；在途请求收到 `pending_responses.drain()` 派发的 `Err` 后立即退出并释放该锁。 |
| 8 | `StdioLibraryChannel.last_shutdown_error` | `std::sync::Mutex<Option<String>>` | `shutdown_and_kill_with_deadline`, fallback workers | **≤ 10 ms 获取锁，且受 `deadline` 剩余预算 `remaining` 严格截断**：采用 `lock_timeout_recover(&self.last_shutdown_error, 10ms.min(rem))`。 | 锁内仅做一次 `Option` 赋值，无 I/O，剩余预算为 0 时直接短路跳过，绝无死锁。 |
| 9 | `StdioLibraryChannel.shutdown_deadline` | `std::sync::Mutex<Option<Instant>>` | `shutdown_and_kill`, `shutdown_and_kill_with_deadline`, `Drop` | **瞬时非竞争互斥锁（< 1 µs）**：记录首次调用时建立的共享绝对 deadline。`Drop` 自动继承该 deadline，绝不新开 2400ms 预算。 | 仅在关闭入口与 drop 中进行一次 `Option::get_or_insert` 赋值，无 I/O，无递归。 |

---

## 2. 全链路最坏情况关闭时间（WCET）闭式推导与预算表

### 2.1 共享绝对 Deadline 机制
系统在生产关闭入口 `ResilientLibraryChannel::shutdown` 立即建立**单一共享绝对 deadline**：
`deadline = Instant::now() + total_budget`（其中 `total_budget ≤ 2400 ms`）。
该 deadline 贯穿 `ctx.inner` 剥离、CloseHostSession、core.shutdown 写入、child wait/kill/reap、taskkill 兜底、reader/writer join 以及后续 `Drop` 等全部可能阻塞点。每一个子阶段的超时时间均取自身静态上限与 `remaining = deadline.saturating_duration_since(Instant::now())` 的**最小值**。
所有轮询步长（`lock_timeout_recover`、`wait_timeout_or_kill_with_reap`、`acquire_transaction_lock`、`run_taskkill_bounded`）均使用 `sleep_dur = poll_interval.min(remaining)`，当 `remaining` 为 0 时直接退出，彻底杜绝轮询超调。

### 2.2 全链路关闭总预算逐段推导表（真实项数：20 项细分阻塞点）

以下逐一列出关闭调用路径上的**全部 20 个可能阻塞点**（与 `apps/desktop/src-tauri/src/library_bridge.rs` 源码逐行对应可复核）：

| 序号 | 执行阶段与操作 | 涉及资源 / 锁 / 系统调用 | 源码对应行号 | 静态上限（最坏情况） | 超时与边界控制机制 | 动态 deadline 截断保证 |
|---|---|---|---|---|---|---|
| **Step 0** | 外层通道剥离 | `ctx.inner` 互斥锁 | `library_bridge.rs:3925` | **50 ms** | `lock_timeout_recover(50ms.min(rem))` | 超时派发 fallback 线程接管（继承同一 deadline），主调用返回 |
| **Step 1** | 在途等待者唤醒 | `pending_responses` 互斥锁 | `library_bridge.rs:2404` | **30 ms** | `lock_timeout_recover(30ms.min(rem))` | 超时派发 fallback 线程唤醒等待者，主线程推进 |
| **Step 2a** | 会话锁获取 | `host_session` 互斥锁 | `library_bridge.rs:2452` | **30 ms** | `lock_timeout_recover(30ms.min(rem))` | 超时跳过会话关闭 |
| **Step 2b** | 交易锁获取 | `transaction_lock` 互斥锁 | `library_bridge.rs:1750` | **80 ms** | `try_lock` 轮询，受 `session_timeout` 截断 | 超时直接放弃该请求 |
| **Step 2c** | 会话请求 pending 注册锁 | `pending_responses` 互斥锁 | `library_bridge.rs:1765` | **100 ms** (受包络截断) | `lock_timeout_recover(100ms.min(rem))` | 受剩余会话预算截断，超时直接放弃 |
| **Step 2d** | CloseHostSession 写入 | 管道写（`write_stdin_shutdown`） | `library_bridge.rs:1785` | **50 ms** (受包络截断) | 后台 writer 线程，`recv_timeout` 截断 | 超时立即返回错误 |
| **Step 2e** | CloseHostSession 响应 | 响应通道接收（`rx.recv_timeout`） | `library_bridge.rs:1817` | **80 ms** (受包络截断) | 独立通道接收，受 `session_timeout` 截断 | 超时立即放弃等待 |
| **Step 2f** | 会话请求超时清理锁 | `pending_responses` 互斥锁 | `library_bridge.rs:1774,1792,1821` | **10 ms** (受包络截断) | `lock_timeout_recover(10ms.min(rem))` | 受剩余会话预算截断，超时直接跳过清理 |
| **Step 3** | core.shutdown 写入 | 管道写（`write_stdin_shutdown`） | `library_bridge.rs:2515` | **60 ms** | 专属关闭写入路径，不受 `is_down` 阻断 | 超时立即放弃并推进至强杀 |
| **Step 4a** | Child 锁获取 | `child` 互斥锁 | `library_bridge.rs:2520` | **50 ms** | `lock_timeout_recover(50ms.min(rem))` | 超时立即触发 taskkill /F /T 强杀分支 |
| **Step 4b** | 优雅退出等待 | `child.try_wait()` 轮询 | `library_bridge.rs:2527` | **1000 ms** | 轮询步长 15 ms，预留 450 ms，受 remaining 截断 | 超时调用 `child.kill()` |
| **Step 4c** | 强杀后 Reap 等待 | `child.kill()` + `try_wait()` 轮询 | `library_bridge.rs:2528` | **400 ms** | 轮询步长 15 ms，预留 200 ms，受 remaining 截断 | 超时触发 taskkill /F /T 兜底 |
| **Step 4d** | Reap 失败错误记录 | `last_shutdown_error` 互斥锁 | `library_bridge.rs:2534` | **10 ms** | `lock_timeout_recover(10ms.min(rem))` | 受 remaining 截断，超时跳过记录 |
| **Step 4e** | OS taskkill 进程树强杀 | `run_taskkill_bounded` (`/F /T /PID`) | `library_bridge.rs:2541` | **250 ms** | 独立子进程有界轮询，受 remaining 截断 | 超时杀灭 taskkill 进程，后台守护回收，主流程不阻塞 |
| **Step 4f** | taskkill 结果错误记录 | `last_shutdown_error` 互斥锁 | `library_bridge.rs:2549` | **10 ms** | `lock_timeout_recover(10ms.min(rem))` | 受 remaining 截断，超时跳过记录 |
| **Step 5a** | Reader 句柄锁获取 | `reader_join_handle` 互斥锁 | `library_bridge.rs:2636` | **30 ms** | `lock_timeout_recover(30ms.min(rem))` | 超时跳过 join 等待 |
| **Step 5b** | Reader 守护 Join 等待 | `reader-join-guard` 线程 join | `library_bridge.rs:2648` | **100 ms** | 守护线程 join，主流程 `recv_timeout(100ms.min(rem))` | 超时强制脱钩推进 |
| **Step 6a** | Writer 句柄锁获取 | `writer_join_handle` 互斥锁 | `library_bridge.rs:2658` | **30 ms** | `lock_timeout_recover(30ms.min(rem))` | 超时跳过 join 等待 |
| **Step 6b** | Writer 守护 Join 等待 | `writer-join-guard` 线程 join | `library_bridge.rs:2670` | **80 ms** | 发送 Shutdown，主流程 `recv_timeout(80ms.min(rem))` | 超时强制脱钩推进 |
| **Step 7** | 重入与 Drop 机制 | `shutdown_executed` / `shutdown_deadline` | `library_bridge.rs:2360,2708` | **0 ms**（正常） | 原子交换短路，继承已有 deadline；重入重试受剩余 deadline 截断 | 若前次已 killed 耗时 0 ms；未 killed 最多消耗 `rem` 剩余时间 |

> **关于 Step 2 会话关闭的包络说明**：
> 在 `library_bridge.rs:2456-2458` 中，会话交互被外部调用方强制限定为 `session_timeout = Duration::from_millis(240).min(rem_session)`。因此，虽然 Step 2a–2f 细分各步骤的独立上限之和为 $30 + 80 + 100 + 50 + 80 + 10 = 350\,\text{ms}$，但在全链路中由于 `session_timeout` 的总包络约束，**Step 2 实际最大总耗时严格 $\le 240\,\text{ms}$**。

---

### 2.3 WCET 闭式推导加和与分支分析

#### 2.3.1 最坏情况（Worst-Case Execution Time）主路径推导
在最坏极端异常叠加情形下（Step 4 获取到 child 锁，但子进程僵死、优雅等待 1000 ms 超时、kill reap 400 ms 超时、进而触发 taskkill 兜底 250 ms）：

$$\begin{aligned}
T_{\text{WCET\_static}} &= T_{\text{inner}} + T_{\text{pending}} + T_{\text{session\_envelope}} + T_{\text{shutdown\_write}} \\
&\quad + (T_{\text{child\_lock}} + T_{\text{graceful}} + T_{\text{reap}} + T_{\text{err1}} + T_{\text{taskkill}} + T_{\text{err2}}) \\
&\quad + (T_{\text{reader\_lock}} + T_{\text{reader\_join}}) + (T_{\text{writer\_lock}} + T_{\text{writer\_join}}) + T_{\text{reentrancy}} \\
&= 50 + 30 + 240 + 60 + (50 + 1000 + 400 + 10 + 250 + 10) \\
&\quad + (30 + 100) + (30 + 80) + 0 \\
&= 50 + 30 + 240 + 60 + 1720 + 130 + 110 + 0 \\
&= \mathbf{2340\,\text{ms}} \le \mathbf{2400\,\text{ms}} < \mathbf{3000\,\text{ms}}\,(3.0\,\text{s})
\end{aligned}$$

- **理论安全硬裕度**：$3000\,\text{ms} - 2340\,\text{ms} = \mathbf{660\,\text{ms}}$。
- **即使完全不考虑 Step 2 的 240 ms 包络限制**，单项直接相加总和为 $2340 + (350 - 240) = 2450\,\text{ms} \le 3000\,\text{ms}$（仍具 550 ms 硬裕度）。

#### 2.3.2 替代分支（Step 4 锁竞争超时分支）
若 Step 4a 因普通锁竞争超时（50 ms），直接转入 Step 4 锁争用分支：
- 记录争锁 Warning（10 ms）；
- 立即发起 `run_taskkill_bounded` 整树强杀（250 ms）；
- 记录 taskkill 结果（10 ms）；
- 保存 fallback reap handle 锁（20 ms）；
- 派发后台 `child-reap-fallback` 线程回收句柄（主线程推进）。

此时 Step 4 总耗时为 $50 + 10 + 250 + 10 + 20 = 340\,\text{ms}$。
总静态 WCET 为：
$$T_{\text{contention}} = 50 + 30 + 240 + 60 + 340 + 130 + 110 + 0 = \mathbf{960\,\text{ms}} \ll 2400\,\text{ms}$$

#### 2.3.3 动态运行时物理硬上限保证
由于共享绝对截止点 `deadline = Instant::now() + min(timeout, 2400ms)`，任何阶段若因调度抖动消耗时间，后续各阶段的 `remaining` 立即被挤压收窄。当 `remaining` 为 0 时，所有操作立即短路返回。因此，**动态物理执行时间在任何极端抖动下严格 $\le 2400\,\text{ms} < 3000\,\text{ms}$**。

---

## 3. 后台 Workers 有界性与无悬挂/无泄漏证明

针对 Codex Review R4 指认的后台 worker 潜在无界路径，本次返修进行了全量防御性加固：

### 3.1 N1 Fallback Worker (`resilient-inner-shutdown-fallback`)
- **继承绝对 deadline**：彻底移除 `max(2000ms, remaining)`，轮询条件严格限制为 `while Instant::now() < deadline`。原 deadline 到期后立即退出，绝不在原 deadline 之后继续等待。
- **立即释放 inner guard**：获取到 `ctx.inner` 锁后，执行 `let chan = guard.take(); drop(guard);`，**在 guard 释放后**才在锁外调用 `chan.shutdown_and_kill_with_deadline(deadline)`，绝不长期持有 `ctx.inner` guard。
- **绝不另开新预算**：通道关闭直接调用 `shutdown_and_kill_with_deadline(deadline)`，共享同一绝对截止时间，绝不另开 1500 ms 独立预算。
- **spawn 失败与超时显式上报**：线程创建失败不再使用 `let _` 忽略，记录日志并置位 `inner_fallback_spawn_failed = true`；超时未拿锁置位 `inner_fallback_timed_out = true`。

### 3.2 Child Reap Fallback Worker (`child-reap-fallback`)
- **消灭无界 `child.wait()`**：获取 `child` 锁后，执行**有界轮询 `child.try_wait()`（单步 15 ms，上限 400 ms）**，绝不调用无界阻塞的 `child.wait()`。
- **超时兜底强杀**：若 400 ms 内未检测到退出，执行 `child.kill()` 并最后一次 `try_wait()`，然后退出线程，绝不无限挂起后台线程。
- **spawn 失败显式上报**：`fallback_spawn` 的 `Err` 显式写入 `last_shutdown_error`。

### 3.3 Taskkill Reaper Worker (`taskkill-reaper-{pid}`)
- **消除 `run_taskkill_bounded` 超时无界 `wait()`**：当 `taskkill` 进程自身超时时，主调用线程执行 `child.kill()` 后，将 `child` 所有权移交给后台轻量守护线程进行句柄回收，主调用线程立即返回 `Err(TimedOut)`，绝不在主调用线程做无界同步 `wait()`。

### 3.4 Drop 路径预算继承
- `StdioLibraryChannel` 引入 `shutdown_deadline: Mutex<Option<Instant>>`。
- 首次进入 `shutdown_and_kill` 或 `shutdown_and_kill_with_deadline` 时原子登记该 deadline。
- `StdioLibraryChannel::drop` 读取已登记的 deadline 并传入 `shutdown_and_kill_with_deadline`，若已超过 deadline 或子进程已消亡，瞬间返回（0 ms），绝不重新开辟 2400 ms 全新预算。

---

## 4. 实测数据与硬上界区分

在 Task 与验收中严格区分“**已证明的硬上界**”与“**实测观测数据**”：

- **已证明的硬上界（WCET）**：
  - **静态理论硬上界**：**2340 ms**（20 个阻塞点全部达到最大超时且全部失败的最坏情况闭式加和）。
  - **动态实现硬上界**：**2400 ms**（共享绝对 deadline 截断，无论任何环节发生系统抖动，物理耗时严格 $\le 2400\,\text{ms} < 3000\,\text{ms}$）。
- **仅观测到的耗时（本次全量实测数据）**：
  - 外部强杀叠加在途请求场景（`resilient_channel_drop_after_external_kill`）：真实关闭入口耗时 **0.4523 ms (452.3 µs)**。
  - Inner 锁竞争超时 fallback 成功接管场景（`resilient_inner_lock_contention_timeout_triggers_fallback_shutdown`）：通过。
  - Inner 锁竞争超时 fallback deadline 超时观测场景（`resilient_inner_lock_contention_fallback_timeout_observed`）：通过。
  - Inner 锁竞争超时 fallback spawn 失败上报场景（`resilient_inner_lock_contention_fallback_spawn_failure_reported`）：通过。
  - Child 锁竞争超时 fallback 进程树强杀场景（`child_lock_contention`）：耗时 **0.69s** 通过。
  - Pending 锁竞争超时 fallback 唤醒场景（`pending_lock_contention`）：耗时 **1.18s** 通过。
  - 管道满载 2MB 写入阻塞场景（`writer_overflow_pipe_capacity`）：耗时 **1.31s** 通过。
  - 既有 resilient_channel 套件（9 项全绿）：耗时 **0.46s** 通过。
  - 既有 stdio_channel_drop 套件（1 项全绿）：耗时 **0.38s** 通过。

---

## 5. 能证明 vs 不能证明（诚实透明界定）

### 5.1 本实现已证明的事实
1. **调用线程绝无可能无限阻塞**：无论 sidecar 挂起、管道写满、互斥锁中毒还是普通锁竞争，生产关闭入口均在 $\le 2400\,\text{ms}$（实测 < 2.0s）内返回。
2. **锁超时绝不漏杀孤儿与漏回收句柄**：child 锁竞争超时通过 `taskkill /F /T` 强杀整棵进程树（包括派生子孙进程），并通过后台 fallback 有界轮询 `child.try_wait()` 回收 OS 句柄（经 `child_lock_contention_timeout_fallback_kills_child_and_prevents_orphan` 验证，断言 `is_child_reaped() == true`）。
3. **在途请求绝不挂起**：pending 锁竞争超时通过后台重试 fallback 完成 drain 唤醒（经测试验证，断言 `is_pending_drained() == true`）。
4. **管道满载在 kill 后完全解除且资源彻底释放**：注入 2MB 大于管道容量的数据时，强杀子进程能通过内核 BrokenPipe 机制唤醒 writer 线程并释放 stdin 句柄，且 writer/reader 守护线程均顺利 join 退出（经测试断言 `is_writer_finished()`, `is_writer_joined()`, `is_reader_joined()`）。
5. **已识别特征后代进程完全清零与隔离根释放**：基于测试前后的系统进程快照差集，对匹配已知特征（进程名包含 core_service/m2rc1_desktop/host_bridge、命令行包含工作区路径或隔离根路径等）的后代/派生进程进行全量扫描审计为 0 残留，并完成隔离根目录强制删除以验证句柄完全释放。

### 5.2 不能证明（超出当前工程边界）的事实
1. **任意未知断链后代的绝对数学排除（AC2 范围声明收窄）**：
   对于未继承父进程特征、命令行脱钩且不包含任何已知工作区或 sidecar 标志特征的第三方任意断链进程，快照差集启发式扫描无法做绝对排他性证明。AC2 的证明范围严格限定于“已知进程名与工作区路径特征差集覆盖”。
2. **AC5 真实交互式桌面关闭需要 Coordinator 在交互桌面运行**：
   本 CLI 环境无 Windows 交互桌面句柄（0x80070578），AC5 的窗口事件触发仍需由 Coordinator 在真实交互式桌面环境下复跑验证。验证脚本 `run-desktop-close-verification.ps1` 已全面修复控制流，消除了所有直接 return，确保宿主进程退出码与 `ac5.exit` 绝对一致。
3. **AC6 证据全量对齐（当前标为未达成）**：
   根据任务协作规则，Antigravity 不得自行执行 `git commit`。当前所有代码修改与测试日志均位于工作区，未打入 commit hash，故 Canonical Evidence 表处于 pending/待集成状态，不作“complete/全量对齐”声明。
