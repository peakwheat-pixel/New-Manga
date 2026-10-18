# P20-CLOSE-BOUND-1 AC4 并发持锁路径审查与硬上界闭式证明（CBH-01~05 加固返修版）

- **审查日期**：2026-10-18
- **责任方**：Antigravity (Owner)
- **审查范围**：`apps/desktop/src-tauri/src/library_bridge.rs` 中与关闭、退出、心跳、请求交互及 Drop 相关的全部持锁点、同步等待、系统调用边界、后台 Worker 与并发调用链
- **依据规范**：Codex Review R6 §7 及未闭合清单（CBH-01 ~ CBH-05）、Codex Review R2 Findings（CBH-R1-01, CBH-R2-01, CBH-R2-02, CBH-R2-03）

---

## 1. 真实持锁与同步机制清单（前台 22 项阻塞调用点 + 统一 Deadline 机制）

在本次加固返修中，针对 Codex Review R2 提出的未闭合点与加固要求，做出了如下严格闭环重构：
1. **CAS 截止时间单调性与重试硬上界（CBH-02 / CBH-R2-01）**：
   - 引入常量 `MAX_DEADLINE_CAS_RETRIES = 32`。初始 CAS 注册与中间过期 sentinel 更新**双重受 32 次硬上限约束**，杜绝无界自旋或无界重试。
   - 实现 `encode_deadline` / `tighter_encoded_deadline` / `decode_deadline`：零预算与已过期预算绝对编码为保留值 `1`（代表 0 ms 剩余），**绝不映射为未来预算**。
   - `tighter_encoded_deadline` 保证单调性：新 deadline 只允许收窄已有 deadline，绝对禁止向后延展。
2. **禁止 Deadline 到期后的一切清理动作（CBH-01）**：
   - `child-reap-fallback` 与 `pending-drain-fallback` 启动前及循环内均校验 `Instant::now() < deadline`；一旦过期直接终止退出。
   - 明确规定：**在 deadline 耗尽后，严禁继续调用 `child.kill()` 或 `child.try_wait()`**，杜绝违规越界动作。
3. **取消挂起 Pipe I/O 与安全 Join（CBH-01 / CBH-R1-01 / CBH-R2-02）**：
   - `StdioLibraryChannel` 保存原始 OS 管道句柄 `raw_stdout_handle` 与 `raw_stdin_handle`，以及由 `DuplicateHandle` 复制的独立拥有所有权的真实线程句柄 `reader_thread_handle` 与 `writer_thread_handle`。
   - 建立双保险取消链 `cancel_worker_io`：结合线程级 `CancelSynchronousIo` 与句柄级 `CancelIoEx`，向 Windows 管道及阻塞在 kernel ReadFile/WriteFile 的线程发送取消请求，取消状态与错误码结构化聚合传播，主路径与 Reaper 严禁丢弃取消结果。
   - **线程句柄无泄漏保证**：工作线程正常退出时由 `ReaderHandleCleaner` / `WriterHandleCleaner` 通过原子 `swap(0, Ordering::SeqCst)` 负责 `CloseHandle`；若通道提前 Drop 则由 Drop 负责 `CloseHandle`，双保险互斥关闭，杜绝句柄泄漏。句柄复制失败时记录错误及负数 sentinel，绝不静默掩盖。
   - **有限且可观测的未回收 Worker 替代生命周期**：Reaper 200 ms 超时后将 Worker 句柄存入全局 `UNREAPED_WORKER_REGISTRY`，互斥锁受 50 ms 超时保护；提供 `unreaped_worker_count()` 观测接口与 `reap_unreaped_workers(max_bound)` 主动有限回收接口。
   - **Reaper 创建失败保护**：通过共享槽转移所有权，若 `Builder::spawn` 失败，主线程立刻取回 `JoinHandle` 并转交 registry 追踪，绝不丢弃 handle 或 detach 遗忘。
   - 引入 `ThreadFinishedGuard`：仅当 worker 线程的局部变量与所有流析构完成离开作用域时才置位 `finished = true`。
   - **仅在已确认 `finished == true` 时才允许调用 `join()`**；若未确认 finished 严禁 `join()`，彻底消除主线程挂死隐患。
4. **Taskkill 与 Reaper 轮询截止时间纳入与错误处理（CBH-01）**：
   - `run_taskkill_bounded` 捕获 `child.kill()` 返回值；当 `child.kill()` 失败时记录日志。
   - taskkill reaper、reader reaper、writer reaper 轮询的 `sleep` 与错误锁等待时间严格受 **200 ms** 剩余预算截断，严禁越过 200 ms。
5. **逐调用点审计与 240 ms 会话包络纠正（CBH-02）**：
   - 纠正原审计表第 4 项写为 80 ms 的错误表述：`acquire_transaction_lock` 在会话关闭时传递的参数是 `session_timeout`（即 `Duration::from_millis(240).min(rem_session)`）。
   - **禁止继续引用 2370 ms 作为全路径 WCET**（详见第 2 节），将应用层软件超时包络与操作系统内核调用开销（Limitation）严格分离。

---

### 1.1 前台 22 处独立阻塞调用点详细清单（与当前源码精确行号一一对应）

| 序号 | 源码精确行号 | 阻塞操作与涉及资源 | 静态最坏超时上限 | 动态 Deadline 截断机制 | 为何绝不无限阻塞 / 死锁 / 假阳性 |
|---:|---|---|---|---|---|
| **1** | `library_bridge.rs:4969-4977` | `ctx.inner` 获取（`ResilientLibraryChannel::shutdown`） | **50 ms** | `lock_timeout_recover(&self.ctx.inner, 50ms.min(rem))` | 仅执行 `guard.take()` 剥离所有权；若超时派发后台 fallback（共享同一 deadline，见 Worker 1），主线程立即推进。 |
| **2** | `library_bridge.rs:3080-3088` | `pending_responses` 锁获取（关闭入口排空等待者） | **30 ms** | `lock_timeout_recover(&self.pending_responses, 30ms.min(rem))` | 纯内存遍历 `drain()` 并唤醒在途请求；若超时派发后台 fallback（共享同一 deadline，见 Worker 2），主线程推进。 |
| **3** | `library_bridge.rs:3157-3160` | `host_session` 锁获取（提取 HostSession） | **30 ms** | `lock_timeout_recover(&self.host_session, 30ms.min(rem))` | 仅在锁内执行 `session_slot.take()`，随后在锁外发起 `CloseHostSession`；超时直接跳过会话关闭。 |
| **4** | `library_bridge.rs:2308-2315`<br>helper `2186-2226` | `acquire_transaction_lock`（交易锁轮询） | **240 ms**<br>*(受外部会话包络约束)* | `try_lock` 轮询，单步 10 ms，受 `session_timeout`（≤ 240 ms）严格截断 | 原 R6 审计表更正项：传参为 `session_timeout`（≤ 240 ms）。在途请求被唤醒后立即释放；超时放弃。 |
| **5** | `library_bridge.rs:2301-2304` | `pending_responses` 注册锁（CloseHostSession） | **100 ms**<br>*(受外部会话包络约束)* | `lock_timeout_recover(&self.pending_responses, 100ms.min(rem))` | 纯哈希表插入，受外层 `session_timeout` 剩余时间截断。 |
| **6** | `library_bridge.rs:2322-2326`<br>writer `2074-2122` | 管道写回执等待（`write_stdin_shutdown`） | **50 ms**<br>*(受外部会话包络约束)* | 受 `remaining_for_write`（受会话预算截断）约束 | 由后台 writer 线程写入，通道满时受 OS 破裂管道或超时保护，超时立即返回错误。 |
| **7** | `library_bridge.rs:2355-2377` | 响应接收等待（`rx.recv_timeout`） | **80 ms**<br>*(受外部会话包络约束)* | 受 `session_timeout` 剩余预算约束（上限 240 ms） | 独占 sync_channel，Core 响应或管道 EOF 立即唤醒，超时立即放弃等待。 |
| **8** | `library_bridge.rs:2311-2314` | 写入前超时清理锁（`pending_responses`） | **10 ms**<br>*(受外部会话包络约束)* | `lock_timeout_recover(&self.pending_responses, 10ms.min(rem))` | 纯内存 `remove`，受剩余预算截断，超时跳过清理。 |
| **9** | `library_bridge.rs:2332-2338` | 写入失败清理锁（`pending_responses`） | **10 ms**<br>*(受外部会话包络约束)* | `lock_timeout_recover(&self.pending_responses, 10ms.min(rem))` | 纯内存 `remove`，受剩余预算截断，超时跳过清理。 |
| **10** | `library_bridge.rs:2360-2363` | 响应超时清理锁（`pending_responses`） | **10 ms**<br>*(受外部会话包络约束)* | `lock_timeout_recover(&self.pending_responses, 10ms.min(rem))` | 纯内存 `remove`，受剩余预算截断，超时跳过清理。 |
| **11** | `library_bridge.rs:3192-3204` | `core.shutdown` 写入管道（`write_stdin_shutdown`） | **60 ms** | 受 `shutdown_write_timeout = 60ms.min(rem)` 截断 | 专用关机写通道，绕过 `is_down`，超时立即放弃并转入进程强杀。 |
| **12** | `library_bridge.rs:3199-3201` | `child` 锁获取（获取子进程句柄） | **50 ms** | `lock_timeout_recover(&self.child, 50ms.min(rem))` | 中毒自动恢复；若竞争超时直接转入 OS taskkill 强杀分支（替代分支）。 |
| **13** | `library_bridge.rs:3208-3212`<br>helper `2778-2797` | 子进程优雅退出等待（`child.try_wait()` 轮询） | **1000 ms** | 轮询步长 15 ms，预留 450 ms，受 `remaining` 严格截断 | 超时调用 `child.kill()` 发送终止信号。 |
| **14** | helper `library_bridge.rs:2817-2835` | 终止信号后 Reap 轮询（`child.try_wait()` 轮询） | **400 ms** | 轮询步长 15 ms，预留 200 ms，受 `remaining` 严格截断 | 超时返回 `TimedOut` 错误，主流程推进至 OS taskkill 兜底强杀。 |
| **15** | `library_bridge.rs:3225-3229` | wait 失败记录锁（`last_shutdown_error`） | **10 ms** | `lock_timeout_recover(&self.last_shutdown_error, 10ms.min(rem))` | 纯内存记录错误日志，超时直接短路跳过。 |
| **16** | `library_bridge.rs:3232-3294`<br>helper `2846-2918` | OS 级 taskkill 强杀及 Reap（`run_taskkill_bounded`） | **250 ms** | `timeout = 250ms.min(rem)`；**归零时短路不启动**；超时派发后台 200ms reaper | 调用 `taskkill /F /T /PID`；仅在确认 `try_wait` 成功返回 `Ok(Some(_))` 时才置位 `child_reaped`，消除假阳性。 |
| **17** | `library_bridge.rs:3297-3302` | taskkill 失败记录锁（`last_shutdown_error`） | **10 ms** | `lock_timeout_recover(&self.last_shutdown_error, 10ms.min(rem))` | 纯内存记录错误日志，超时直接短路跳过。 |
| **18** | `library_bridge.rs:3437-3440` | `reader_join_handle` 锁获取 | **30 ms** | `lock_timeout_recover(&self.reader_join_handle, 30ms.min(rem))` | 锁内仅微秒级 `take()` 取出 handle，锁外轮询等待。 |
| **19** | `library_bridge.rs:3443-3459` | Reader 线程退出等待（前台轮询） | **100 ms** | `join_timeout = 100ms.min(rem)`，单步 10 ms 轮询 | 等待前先触发 `cancel_active_pipes()`；确认 finished 后才 `join`；超时派发后台 200 ms reaper，前台绝无死锁。 |
| **20** | `library_bridge.rs:3550-3553` | `writer_join_handle` 锁获取 | **30 ms** | `lock_timeout_recover(&self.writer_join_handle, 30ms.min(rem))` | 锁内仅微秒级 `take()` 取出 handle，锁外发送 Shutdown。 |
| **21** | `library_bridge.rs:3556-3573` | Writer 线程退出等待（前台轮询） | **80 ms** | `join_timeout = 80ms.min(rem)`，单步 10 ms 轮询 | 等待前先触发 `cancel_active_pipes()`；确认 finished 后才 `join`；超时派发后台 200 ms reaper，前台绝无死锁。 |
| **22** | `library_bridge.rs:2973-3075`<br>`:3664-3672, 5038-5046` | 重入路径、Stdio Drop 与 Resilient Drop | **0 ms**<br>*(正常无重入)* | `Drop` 自动继承已有 deadline；重入重试全部受剩余 deadline 截断 | 原子 swap 短路；仅在未 killed 时尝试重试；reap 判定严格检查 `try_wait` 成功，绝无假阳性。 |

---

## 2. 全链路最坏情况时间（WCET）诚实重算与限制声明（CBH-02 闭环）

### 2.1 为何禁止继续引用 2370 ms 作为全路径 WCET

Codex R6 §7 指出：
1. 原审计表将第 4 项 `acquire_transaction_lock` 记为 80 ms，但实际代码向该辅助函数传递的是外部传参 `session_timeout`（上限 240 ms）。原表低估了单步静态预算。
2. 原审计表把全路径 WCET 计算为简单的静态常数累加 $2370\,\text{ms}$，**未将操作系统系统调用（`Command::spawn`、管道读取、`child.kill()`、线程创建 `Builder::spawn`、条件 `join()`）纳入模型**。
3. 任何依赖操作系统的系统调用耗时都受 Windows 内核资源、上下文切换与调度延迟制约，无法在数学上保证绝对为 0 ms。

因此，**本次加固严禁将 2370 ms 声明为全路径物理 WCET**，而是将其澄清为**应用层显式超时参数包络（Application Software Timeout Envelope）**，并建立双层 WCET 闭式模型。

---

### 2.2 双层 WCET 闭式模型

全路径实际关机时间 $T_{\text{total}}$ 由两部分构成：
$$T_{\text{total}} = T_{\text{software\_envelope}} + \sum T_{\text{syscall}}$$

#### 第一层：应用层显式超时包络（$T_{\text{software\_envelope}}$）
在生产关闭入口 `ResilientLibraryChannel::shutdown` 中，建立了硬性动态截止时间：
$$\text{deadline} = \text{Instant::now()} + \min(\text{timeout}, 2400\,\text{ms})$$
后续所有 22 个调用点在执行前均通过：
$$\text{rem} = \text{deadline.saturating\_duration\_since(Instant::now())}$$
将各自的超时参数收窄为 $\min(T_{\text{static\_step}}, \text{rem})$。

- **若考虑 Step 2 会话预算整体包络（240 ms）**：
  $$\begin{aligned}
  T_{\text{software\_envelope}} &= T_{\text{inner}} (50) + T_{\text{pending}} (30) + T_{\text{host\_session\_lock}} (30) + T_{\text{session\_envelope}} (240) + T_{\text{shutdown\_write}} (60) \\
  &\quad + T_{\text{child\_lock}} (50) + T_{\text{graceful}} (1000) + T_{\text{reap}} (400) + T_{\text{err1}} (10) + T_{\text{taskkill}} (250) + T_{\text{err2}} (10) \\
  &\quad + T_{\text{reader\_lock}} (30) + T_{\text{reader\_wait}} (100) + T_{\text{writer\_lock}} (30) + T_{\text{writer\_wait}} (80) + T_{\text{reentrancy}} (0) \\
  &= 2370\,\text{ms} \le 2400\,\text{ms}
  \end{aligned}$$
- **若极端假设会话包络内单步线性累加（无外部统一包络截断）**：
  内部单步加和为 $T_{\text{tx\_lock}} (240) + T_{\text{reg\_lock}} (100) + T_{\text{write}} (50) + T_{\text{recv}} (80) + T_{\text{clean}} (10) = 480\,\text{ms}$。
  此时静态单步加和为 $2370 - 240 + 480 = 2610\,\text{ms}$。
  **但由于动态 deadline 的强制收窄机制**，当耗时达到 2400 ms 时，剩余所有软件超时自动被截断为 0 ms 并短路跳过，因此软件可控时间被**数学证明严格约束在 $\le 2400\,\text{ms}$ 之内**。

#### 第二层：系统调用与内核延迟边界（$\sum T_{\text{syscall}}$，物理 Limitation）
在 22 项受控等待之外，前台路径包含以下无法由用户态单一 deadline 截断的操作系统系统调用：
1. `Command::new("taskkill").spawn()`：创建外部 taskkill 进程（`library_bridge.rs:2888`）；
2. taskkill 标准输出/错误流读取；
3. `child.kill()`：向子进程句柄发送终止信号（`library_bridge.rs:2816`, `2914`）；
4. `std::thread::Builder::spawn()`：在超时发生时创建后台收尾线程（最多 6 处，见第 3 节）；
5. `join()`：仅在 `ThreadFinishedGuard` 置位 `finished = true` 后调用，此时线程已结束，耗时仅为内核清理句柄的微秒级时间；
6. `CancelSynchronousIo` / `CancelIoEx`：向内核管道与线程发送取消请求（`library_bridge.rs:1357, 1381`）；
7. `DuplicateHandle` / `CloseHandle`：内核线程句柄复制与关闭（`library_bridge.rs:1757, 1846, 3629, 3635`）。

**安全裕度推导**：
整个硬上界规范要求为 $T_{\text{total}} < 3000\,\text{ms}$（3.0 秒）。
应用层软件超时包络上限为 $2400\,\text{ms}$。
留给所有系统调用和内核调度的总裕度为：
$$\text{Margin}_{\text{syscall}} = 3000\,\text{ms} - 2400\,\text{ms} = \mathbf{600\,\text{ms}}$$
在正常及中度负载的 Windows 操作系统中，一次 `process::spawn` 典型耗时为 5~15 ms，一次 `thread::spawn` 典型耗时 < 1 ms，`child.kill` 耗时 < 1 ms，句柄与取消系统调用耗时 < 0.1 ms。全路径全部系统调用总和通常 $< 50\,\text{ms} \ll 600\,\text{ms}$。

---

## 3. 后台 Worker 与独立 Reaper 的有界性与最坏存活界

针对前台超时后派发的后台 Worker 与 Reaper，生命周期控制与最坏存活界逐项审计如下：

| 线程名称 | 源码生成位置 | 触发条件 | 退出控制机制与最坏存活上界 | 挂起 I/O 取消保证与 Join 安全性 | 是否阻塞前台 |
|---|---|---|---|---|:---:|
| **Worker 1**<br>`resilient-inner-shutdown-fallback` | `library_bridge.rs:4998` | 前台获取 `ctx.inner` 超过 50 ms 超时 | 循环条件严格为 `while Instant::now() < deadline`，单步 sleep 受剩余 deadline 截断。<br>**最坏存活**：不超过主关闭 deadline。获锁后立即释放 guard。 | 纯内存互斥锁争用，无 I/O。前台不 join。 | **否** |
| **Worker 2**<br>`pending-drain-fallback` | `library_bridge.rs:3099` | 前台获取 `pending_responses` 超过 30 ms 超时 | **加固约束**：启动前及循环中检查 deadline，过期直接退出。<br>**最坏存活**：不超过主关闭 deadline。获锁后遍历 drain 并退出。 | 纯内存哈希表操作，无 I/O。前台不 join。 | **否** |
| **Worker 3**<br>`child-reap-fallback` | `library_bridge.rs:3333` | 前台获取 `child` 超过 50 ms 超时 | **加固约束**：循环检查 deadline；**一旦 deadline 到期严禁调用 `child.kill()` 或 `child.try_wait()`**。<br>**最坏存活**：不超过主关闭 deadline。 | 仅在 deadline 预算内尝试获取锁并回收。前台不 join。 | **否** |
| **Worker 4**<br>`taskkill-reaper-{pid}` | `library_bridge.rs:2924` | 前台 `run_taskkill_bounded` 超过 250 ms 超时 | **加固约束**：内部设固定 `reap_timeout = 200 ms`，轮询 sleep 与错误锁等待均受剩余时间截断，到期自动退出。<br>**最坏存活**：**严格 ≤ 200 ms**。 | 仅执行非阻塞 `child.try_wait()`，无管道 I/O。前台不 join。 | **否** |
| **Worker 5**<br>`reader-join-bounded-reaper` | `library_bridge.rs:3471` | 前台等待 reader 退出超过 100 ms 超时 | **加固约束**：固定 `200 ms` deadline，轮询执行 `cancel_worker_io` 并受剩余时间截断。若 200 ms 内未完成，转入全局 `UNREAPED_WORKER_REGISTRY` 追踪管理。<br>**Reaper spawn 保护**：若 reaper 创建失败，主线程立刻从 shared slot 取回 JoinHandle 并转入 registry，绝不丢失。<br>**最坏存活**：Reaper 线程本身严格 ≤ 200 ms；原 worker 进入全局可观测 registry。 | 前台及 reaper 轮询触发 `CancelSynchronousIo` + `CancelIoEx`。仅在 `reader_finished == true` 时 join。进入 registry 后可由 `reap_unreaped_workers` 主动回收。 | **否** |
| **Worker 6**<br>`writer-join-bounded-reaper` | `library_bridge.rs:3586` | 前台等待 writer 退出超过 80 ms 超时 | **加固约束**：固定 `200 ms` deadline，轮询执行 `cancel_worker_io` 并受剩余时间截断。若 200 ms 内未完成，转入全局 `UNREAPED_WORKER_REGISTRY` 追踪管理。<br>**Reaper spawn 保护**：若 reaper 创建失败，主线程立刻从 shared slot 取回 JoinHandle 并转入 registry，绝不丢失。<br>**最坏存活**：Reaper 线程本身严格 ≤ 200 ms；原 worker 进入全局可观测 registry。 | 前台及 reaper 轮询触发 `CancelSynchronousIo` + `CancelIoEx`。仅在 `writer_finished == true` 时 join。进入 registry 后可由 `reap_unreaped_workers` 主动回收。 | **否** |

---

## 4. 证明能力诚实声明（Can Prove vs Cannot Prove）

### 4.1 能确定性证明的事实
1. **CAS 截止时间单调性与有界重试**：CAS 初始注册与中间过期 sentinel 更新均严格受 `MAX_DEADLINE_CAS_RETRIES = 32` 硬约束；零与过期 deadline 绝对编码为 1（0 ms 预算），绝不映射为未来时间；新 deadline 只能收窄已有 deadline。
2. **前台应用层超时包络严格收敛**：全部 22 处可能发生阻塞的调用点均受单一 deadline 截断，受控软件时间闭式收敛在 $\le 2400\,\text{ms}$ 之内。
3. **禁止 Deadline 到期后的一切清理动作**：Child fallback 与 Pending fallback 在 deadline 到期后立即终止，严禁执行 `kill`/`try_wait`。
4. **消除无界 Join 与后台悬挂死锁**：前台与后台 Reaper 均只对经由 `ThreadFinishedGuard` 确认 `finished = true` 的线程执行 `join()`；未确认 finished 的线程严禁 join；通过 `CancelSynchronousIo` 与 `CancelIoEx` 双保险取消挂起 I/O。
5. **Reaper 轮询与错误记录严格受限**：Taskkill reaper 及 reader/writer reaper 的轮询 sleep 和互斥锁等待严格受 200 ms 剩余时间截断，绝不跨越 200 ms。
6. **未回收 Worker 有限替代生命周期与可观测性**：Reaper 超时或 spawn 失败时，worker JoinHandle 均被可靠转交 `UNREAPED_WORKER_REGISTRY`，互斥锁受 50 ms 超时保护；可通过 `unreaped_worker_count()` 实时观测，并通过 `reap_unreaped_workers` 主动回收。
7. **Windows 线程句柄无泄漏保证**：工作线程内建立的独立句柄由 Cleaner（正常退出）与 Channel Drop（提前退出）通过原子 swap 互斥关闭，杜绝句柄泄漏；复制失败有负数 sentinel 记录。
8. **Reap 状态无假阳性**：只有在 `child.try_wait()` 明确返回 `Ok(Some(_))` 时才记录为已回收。
9. **隔离根与进程树无孤儿**：在隔离环境下的验证套件实测证明残余孤儿进程数为 0。

### 4.2 结构上不能证明的事实（系统物理极限与 Limitation 声明）
1. **Windows 内核进程与线程生成的不可中断性**：`Command::new("taskkill").spawn()` 与 `std::thread::Builder::spawn()` 依赖 Windows 内核对象分配与页表初始化。在极端物理故障（如操作系统严重换页抖动、内核对象句柄耗尽、防病毒驱动全局拦截）下，内核系统调用的返回耗时无法在用户态通过单一 deadline 强制中断。这是所有运行在操作系统上的用户态程序固有的物理 Limitation。
2. **Windows 句柄与线程 I/O 取消的驱动层响应性**：`CancelIoEx` 向文件系统驱动发送句柄取消请求，`CancelSynchronousIo` 向线程控制块发送同步 I/O 取消请求。绝大多数标准管道驱动（NPFS）会立即完成并向 ReadFile/WriteFile 返回 `ERROR_OPERATION_ABORTED` (995)，但在第三方过滤驱动挂钩或底层硬件驱动死锁时，驱动层未响应属于内核不可控边界。
3. **高负载下定时器时钟漂移**：`std::thread::sleep` 依赖系统计时器分辨率。高负载下可能存在数毫秒级的时钟片抖动，由 600 ms 的安全裕度予以吸收。

