# P20-CLOSE-BOUND-1 AC4 并发持锁路径审查与硬上界闭式证明（R6 终审收口版）

- **审查日期**：2026-10-18
- **责任方**：Antigravity (Owner)
- **审查范围**：`apps/desktop/src-tauri/src/library_bridge.rs` 中与关闭、退出、心跳、请求交互及 Drop 相关的全部持锁点、同步等待、后台 Worker 与并发调用链
- **依据规范**：Codex Review R5（`verification/P20-CLOSE-BOUND-1/codex-review-r5.md`）

---

## 1. 真实持锁与同步机制清单（前台 22 项阻塞调用点 + 统一 Deadline 机制）

在 R6 中，针对 R5 审查提出的所有指认，已做出以下闭环重构：
1. **彻底消除 `shutdown_deadline` 互斥锁**：改用 `created_at: Instant` + `shutdown_deadline_ms: AtomicU64` 原子量 CAS 机制。无锁、无等待、不可重入死锁、无优先级反转，耗时 0 ms。
2. **`Drop` 绝对复用已建立 Deadline**：`StdioLibraryChannel::drop` 与 `ResilientLibraryChannel::drop` 均首先通过 `get_deadline()` 读取已有截止时间，若存在直接继承，严禁重新开辟 2400 ms 预算。
3. **`run_taskkill_bounded` 归零保护**：在 `timeout.is_zero()` 时立即短路返回 `Err`，绝不启动 `taskkill` 进程。
4. **后台 Worker 严格受限**：所有 fallback worker 均共享 `Instant::now() < deadline`，所有 detached reaper（taskkill、reader、writer）均设有固定 **200 ms** 轮询上界，彻底消除无界 `wait()` 与 `join()`。
5. **重入与假阳性闭环**：仅在 `child.try_wait()` 明确返回 `Ok(Some(_))` 时才置位 `child_reaped = true`。

### 1.1 前台 22 处独立阻塞调用点详细清单

| 序号 | 源码精确行号 | 阻塞操作与涉及资源 | 静态最坏上限 | 动态 Deadline 截断机制 | 为何绝不无限阻塞 / 死锁 / 假阳性 |
|---:|---|---|---|---|---|
| **1** | `library_bridge.rs:4291-4299` | `ctx.inner` 获取（`ResilientLibraryChannel::shutdown`） | **50 ms** | `lock_timeout_recover(&self.ctx.inner, 50ms.min(rem))` | 仅执行 `guard.take()` 剥离所有权；若超时派发后台 fallback（共享同一 deadline，见第 3 节 Worker 1），主线程立即推进。 |
| **2** | `library_bridge.rs:2552-2560` | `pending_responses` 锁获取（关闭入口排空等待者） | **30 ms** | `lock_timeout_recover(&self.pending_responses, 30ms.min(rem))` | 仅在内存中遍历 `drain()` 并唤醒在途请求；若超时派发后台 fallback（共享同一 deadline，见第 3 节 Worker 2），主线程推进。 |
| **3** | `library_bridge.rs:2619-2622` | `host_session` 锁获取（提取 HostSession） | **30 ms** | `lock_timeout_recover(&self.host_session, 30ms.min(rem))` | 仅在锁内执行 `session_slot.take()`，随后在锁外发起 `CloseHostSession`；超时直接跳过会话关闭。 |
| **4** | `library_bridge.rs:1784`<br>helper `1694-1734` | `acquire_transaction_lock`（交易锁轮询） | **80 ms**<br>*(受包络约束)* | `try_lock` 轮询，单步 10 ms，受 `session_timeout`（≤ 240 ms）严格截断 | 在途请求收到 `pending_responses` 唤醒错误后立即释放该锁；超时立即放弃。 |
| **5** | `library_bridge.rs:1809-1812` | `pending_responses` 注册锁（CloseHostSession） | **100 ms**<br>*(受包络约束)* | `lock_timeout_recover(&self.pending_responses, 100ms.min(rem))` | 纯哈希表插入，受外层 `session_timeout` 剩余时间截断。 |
| **6** | `library_bridge.rs:1829-1833`<br>writer `1627-1675` | 管道写回执等待（`write_stdin_shutdown`） | **50 ms**<br>*(受包络约束)* | 受 `remaining_for_write`（受会话预算截断）约束 | 由后台 writer 线程写入，通道满时受 OS 破裂管道或超时保护，超时立即返回错误。 |
| **7** | `library_bridge.rs:1855-1877` | 响应接收等待（`rx.recv_timeout`） | **80 ms**<br>*(受包络约束)* | 受 `session_timeout` 剩余预算约束（上限 240 ms） | 独占 sync_channel，Core 响应或管道 EOF 立即唤醒，超时立即放弃等待。 |
| **8** | `library_bridge.rs:1818-1821` | 写入前超时清理锁（`pending_responses`） | **10 ms**<br>*(受包络约束)* | `lock_timeout_recover(&self.pending_responses, 10ms.min(rem))` | 纯内存 `remove`，受剩余预算截断，超时跳过清理。 |
| **9** | `library_bridge.rs:1836-1842` | 写入失败清理锁（`pending_responses`） | **10 ms**<br>*(受包络约束)* | `lock_timeout_recover(&self.pending_responses, 10ms.min(rem))` | 纯内存 `remove`，受剩余预算截断，超时跳过清理。 |
| **10** | `library_bridge.rs:1867-1870` | 响应超时清理锁（`pending_responses`） | **10 ms**<br>*(受包络约束)* | `lock_timeout_recover(&self.pending_responses, 10ms.min(rem))` | 纯内存 `remove`，受剩余预算截断，超时跳过清理。 |
| **11** | `library_bridge.rs:2646-2658` | `core.shutdown` 写入管道（`write_stdin_shutdown`） | **60 ms** | 受 `shutdown_write_timeout = 60ms.min(rem)` 截断 | 专用关机写通道，绕过 `is_down`，超时立即放弃并转入进程强杀。 |
| **12** | `library_bridge.rs:2661-2663` | `child` 锁获取（获取子进程句柄） | **50 ms** | `lock_timeout_recover(&self.child, 50ms.min(rem))` | 中毒自动恢复；若竞争超时直接转入 OS taskkill 强杀分支（见 Step 4 替代分支）。 |
| **13** | `library_bridge.rs:2666-2670`<br>helper `2267-2286` | 子进程优雅退出等待（`child.try_wait()` 轮询） | **1000 ms** | 轮询步长 15 ms，预留 450 ms，受 `remaining` 严格截断 | 超时调用 `child.kill()` 发送终止信号。 |
| **14** | helper `library_bridge.rs:2306-2324` | 终止信号后 Reap 轮询（`child.try_wait()` 轮询） | **400 ms** | 轮询步长 15 ms，预留 200 ms，受 `remaining` 严格截断 | 超时返回 `TimedOut` 错误，主流程推进至 OS taskkill 兜底强杀。 |
| **15** | `library_bridge.rs:2676-2680` | wait 失败记录锁（`last_shutdown_error`） | **10 ms** | `lock_timeout_recover(&self.last_shutdown_error, 10ms.min(rem))` | 纯内存记录错误日志，超时直接短路跳过。 |
| **16** | `library_bridge.rs:2683-2745`<br>helper `2354-2425` | OS 级 taskkill 强杀及 Reap（`run_taskkill_bounded`） | **250 ms** | `timeout = 250ms.min(rem)`；**归零时短路不启动**；超时派发后台 200ms reaper | 调用 `taskkill /F /T /PID`；仅在确认 `try_wait` 成功返回 `Ok(Some(_))` 时才置位 `child_reaped`，消除假阳性。 |
| **17** | `library_bridge.rs:2748-2753` | taskkill 失败记录锁（`last_shutdown_error`） | **10 ms** | `lock_timeout_recover(&self.last_shutdown_error, 10ms.min(rem))` | 纯内存记录错误日志，超时直接短路跳过。 |
| **18** | `library_bridge.rs:2882-2885` | `reader_join_handle` 锁获取 | **30 ms** | `lock_timeout_recover(&self.reader_join_handle, 30ms.min(rem))` | 锁内仅微秒级 `take()` 取出 handle，锁外轮询等待。 |
| **19** | `library_bridge.rs:2888-2904` | Reader 线程退出等待（前台轮询） | **100 ms** | `join_timeout = 100ms.min(rem)`，单步 10 ms 轮询 | 子进程终止后 stdout EOF 触发退出；若前台超时移交后台 200 ms reaper，前台绝无死锁。 |
| **20** | `library_bridge.rs:2948-2951` | `writer_join_handle` 锁获取 | **30 ms** | `lock_timeout_recover(&self.writer_join_handle, 30ms.min(rem))` | 锁内仅微秒级 `take()` 取出 handle，锁外发送 Shutdown。 |
| **21** | `library_bridge.rs:2954-2971` | Writer 线程退出等待（前台轮询） | **80 ms** | `join_timeout = 80ms.min(rem)`，单步 10 ms 轮询 | 发送 Shutdown 并在管道破裂后退出；若前台超时移交后台 200 ms reaper，前台绝无死锁。 |
| **22** | `library_bridge.rs:2440-2548`<br>`:3016-3024, 4363-4371` | 重入路径、Stdio Drop 与 Resilient Drop | **0 ms**<br>*(正常无重入)* | `Drop` 自动继承已有 deadline；重入重试全部受剩余 deadline 截断 | 原子 swap 短路；仅在未 killed 时尝试重试；reap 判定严格检查 `try_wait` 成功，绝无假阳性。 |

---

## 2. 全链路最坏情况关闭时间（WCET）闭式推导

### 2.1 静态最坏情况（WCET）主路径闭式推导

在最坏极端异常叠加情形下（Step 4 获取到 `child` 锁，但子进程处于僵死状态：优雅退出等待 1000 ms 超时、终止信号 Reap 400 ms 超时、进而触发 OS taskkill 强杀兜底 250 ms）：

会话交互在 `library_bridge.rs:2623-2625` 中被外部逻辑严格限制为 `session_timeout = Duration::from_millis(240).min(rem_session)`，故 Step 2b–2f 处于该 240 ms 统一包络之内。而 Step 2a（`host_session` 互斥锁获取）发生在会话预算建立之前（行 2620-2621），其自身上限为 30 ms。

因此，真实主路径各段静态最坏上限精确加和为：

$$\begin{aligned}
T_{\text{WCET\_static}} &= T_{\text{inner}} + T_{\text{pending}} + T_{\text{host\_session\_lock}} + T_{\text{session\_envelope}} + T_{\text{shutdown\_write}} \\
&\quad + (T_{\text{child\_lock}} + T_{\text{graceful}} + T_{\text{reap}} + T_{\text{err1}} + T_{\text{taskkill}} + T_{\text{err2}}) \\
&\quad + (T_{\text{reader\_lock}} + T_{\text{reader\_wait}}) + (T_{\text{writer\_lock}} + T_{\text{writer\_wait}}) + T_{\text{reentrancy}} \\
&= 50 + 30 + 30 + 240 + 60 + (50 + 1000 + 400 + 10 + 250 + 10) \\
&\quad + (30 + 100) + (30 + 80) + 0 \\
&= 50 + 30 + 30 + 240 + 60 + 1720 + 130 + 110 + 0 \\
&= \mathbf{2370\,\text{ms}} \le \mathbf{2400\,\text{ms}} < \mathbf{3000\,\text{ms}}\,(3.0\,\text{s})
\end{aligned}$$

- **理论安全硬裕度**：$3000\,\text{ms} - 2370\,\text{ms} = \mathbf{630\,\text{ms}}$。
- **即使完全不考虑 Step 2 的 240 ms 包络限制**（将 Step 2b 80ms + 2c 100ms + 2d 50ms + 2e 80ms + 2f 10ms = 320ms 直接相加），单项直接相加总和为：
  $$2370 + (320 - 240) = 2450\,\text{ms} \le 3000\,\text{ms}$$
  仍具备 **550 ms** 确定性硬安全裕度。

### 2.2 替代分支（Step 4 child 锁竞争超时分支）

若 Step 4 因锁竞争超时（50 ms），直接转入锁争用 fallback 分支（行 2756-2860）：
- 记录争锁 Warning（10 ms）；
- 立即发起 `run_taskkill_bounded` 整树强杀（250 ms）；
- 记录 taskkill 结果（10 ms）；
- 保存 fallback handle 锁（20 ms）；
- 派发后台 `child-reap-fallback` 线程回收句柄（主线程推进）。

此时 Step 4 总耗时为 $50 + 10 + 250 + 10 + 20 = 340\,\text{ms}$。
总静态 WCET 为：
$$T_{\text{contention}} = 50 + 30 + 30 + 240 + 60 + 340 + 130 + 110 + 0 = \mathbf{990\,\text{ms}} \ll 2400\,\text{ms}$$

### 2.3 动态运行时物理硬上限保证

在生产关闭入口 `ResilientLibraryChannel::shutdown` 建立的绝对截止时间：
$$\text{deadline} = \text{Instant::now()} + \min(\text{timeout}, 2400\,\text{ms})$$
后续每一个步骤均通过 `deadline.saturating_duration_since(Instant::now())` 动态收窄。若系统调度抖动使得某一阶段消耗过多时间，后续所有操作的等待时间自动被挤压归零并短路跳过。

---

## 3. 后台 Worker 与独立 Reaper 的有界性与最坏存活界

对于结构上不阻塞前台主流程推进的后台 Worker 和 Reaper，逐项证明其生命周期有界性：

| 线程名称 | 源码生成位置 | 触发条件 | 退出控制机制与最坏存活上界 | 是否阻塞前台关闭 |
|---|---|---|---|:---:|
| **Worker 1**<br>`resilient-inner-shutdown-fallback` | `library_bridge.rs:4322-4352` | 前台获取 `ctx.inner` 超过 50 ms 超时 | 循环条件严格为 `while Instant::now() < deadline`，单步 sleep 受剩余 deadline 截断。<br>**最坏存活时间**：不超过主关闭 deadline。获锁后立即释放 guard，无级联阻塞。 | **否** |
| **Worker 2**<br>`pending-drain-fallback` | `library_bridge.rs:2567-2605` | 前台获取 `pending_responses` 超过 30 ms 超时 | 循环条件严格为 `while Instant::now() < deadline`，单步 sleep 受剩余 deadline 截断。<br>**最坏存活时间**：不超过主关闭 deadline。获锁后遍历 drain 并退出。 | **否** |
| **Worker 3**<br>`child-reap-fallback` | `library_bridge.rs:2791-2860` | 前台获取 `child` 超过 50 ms 超时 | 循环条件严格为 `while Instant::now() < deadline`，获锁后轮询 `child.try_wait()` 同样受 deadline 截断。<br>**最坏存活时间**：不超过主关闭 deadline。 | **否** |
| **Worker 4**<br>`taskkill-reaper-{pid}` | `library_bridge.rs:2404-2420` | 前台 `run_taskkill_bounded` 超过 250 ms 超时 | 内部设固定 `reap_timeout = 200 ms`，每 15 ms 调用 `child.try_wait()`，到期自动退出。<br>**最坏存活时间**：**严格 ≤ 200 ms**。彻底消除无界 `child.wait()`。 | **否** |
| **Worker 5**<br>`reader-join-bounded-reaper` | `library_bridge.rs:2913-2930` | 前台等待 reader 退出超过 100 ms 超时 | 内部设固定 `deadline = Instant::now() + 200 ms`，每 10 ms 检查 `reader_finished`，到期自动退出。<br>**最坏存活时间**：**严格 ≤ 200 ms**。彻底消除无界 `handle.join()`。 | **否** |
| **Worker 6**<br>`writer-join-bounded-reaper` | `library_bridge.rs:2980-2997` | 前台等待 writer 退出超过 80 ms 超时 | 内部设固定 `deadline = Instant::now() + 200 ms`，每 10 ms 检查 `writer_finished`，到期自动退出。<br>**最坏存活时间**：**严格 ≤ 200 ms**。彻底消除无界 `handle.join()`。 | **否** |

---

## 4. 能证明 vs 不能证明（物理边界诚实声明）

### 4.1 能确定性证明的事实
1. **前台主路径无无界等待**：前台关闭路径上全部 22 处可能发生阻塞的调用点，均设有显式超时上限，且均由单一共享 deadline（≤ 2400 ms）严格收窄。
2. **前台静态总预算闭式收敛**：静态最坏情况总和严格为 **2370 ms**，满足 $\le 2400\,\text{ms} < 3000\,\text{ms}$，具备 630 ms 确定性硬裕度。
3. **消除所有无界后台等待**：消除了所有后台 `wait()` / `join()`，所有后台 Worker 均受单一 deadline 或固定 200 ms 上限约束。
4. **无锁化 Deadline 消除自锁与重入**：`AtomicU64` CAS 机制消除了 Mutex 竞争、毒化与优先级反转。
5. **Reap 状态无假阳性**：只有在 `child.try_wait()` 明确返回 `Ok(Some(_))` 时才记录为已回收。
6. **缩窄后的残留检测无误报**：基于当前执行的 PID 树与唯一隔离根路径，完全不受工作区其他并行进程干扰。

### 4.2 结构上不能证明的事实（系统物理极限说明）
1. **OS 进程创建的物理延迟**：`run_taskkill_bounded` 中执行 `Command::new("taskkill").spawn()` 是操作系统内核级同步调用。代码通过在 `timeout.is_zero()` 时短路拦截消除了零预算时的启动，但无法在物理上保证 Windows 内核在极限资源耗尽下创建进程的墙钟耗时（尽管实测通常 < 20 ms）。
2. **操作系统线程调度的物理精度**：`std::thread::sleep` 依赖 Windows 操作系统定时器与调度器。在高负载或系统挂起唤醒场景下，实际睡眠时长可能存在微小的调度延迟抖动。可证明的是传给受控等待的超时参数严格收窄，而不能证明物理硬件始终不发生系统级挂起。
3. **后台 Reaper 的独立边界**：Worker 4–6 是在前台超时脱钩后在后台异步运行的资源回收线程，其最坏 200 ms 存活时间属于后台异步回收边界，不计入前台直接返回用户的 2370 ms 关闭时间。
