# P20-CLOSE-BOUND-1 独立 Review R5

- **task_id**：P20-CLOSE-BOUND-1
- **reviewer / owner**：Codex / Antigravity
- **base_commit**：`8bf3ae30a`
- **reviewed_head**：`5021f039ffb0802d4dae9765e433463a736d680a`
- **decision**：`changes_requested`
- **方式**：只读审查。未运行 `cargo build` 或测试；未修改产品代码、提交、push、reset 或清理工作区。核对源码、脚本、现有日志、Task/Handoff 与 R4 Review。
- **范围说明**：R5 提交 `5021f039f` 的产品代码改动只有 `apps/desktop/src-tauri/src/library_bridge.rs`；该提交没有改 `main.rs`。基线至 HEAD 的 `main.rs` 历史差异包含 P09 提交内容，按要求排除，不作为本 Task 越界或失败。工作区既有 P09 前端、`src/**`、`tests/**` 在本 Review 中保留且未审查。

## 1. 结论

**不批准；R5 仍有 AC1/AC4 的 P1 级未闭合点。**

N1 fallback 的轮询、及时释放 `ctx.inner` guard、共享传入 deadline、失败标志和测试分支在源码中均有实质修正。但单一 deadline 尚未覆盖所有退出与回收路径：普通阻塞的 `shutdown_deadline.lock()` 未限时，`ResilientLibraryChannel::Drop` 可新开 2400 ms 预算，若 deadline 已归零，`run_taskkill_bounded` 仍先同步启动 taskkill；多个后台 worker 仍会在共享 deadline 后运行，且 taskkill/reader/writer reaper 有无界 `wait/join`。另外，重入路径会在未确认 `try_wait` 成功时置位 `child_reaped`。

审计表目前是 20 行，表格行数本身正确；但 2f 将三个独立锁调用合成一项，源代码实际至少有 22 个不同的前台阻塞调用位置，且另漏列 deadline mutex、后台 fallback/reaper 和若干无界同步操作。修正会话包络后，作者公式的静态主路径至少应为 **2370 ms**，而非 2340 ms；该数字仍未计入未界定的同步操作，因此不能作为 WCET 证明。

AC2 范围文字已收窄到已知特征，但 runner 把全机匹配进程及工作区内 Python 进程当作残留，Coordinator 并行跑 Python 测试时会误报。当前独占复跑的日志为 0 残留，支持该时点的已知特征检查；脚本仍需缩窄为本次执行的 PID/隔离根证据。AC5 落盘与退出码控制流的代码修复成立，但当前交互式桌面实测仍须 Coordinator 使用当前 build 复跑。AC6 仍未闭合：Task/Handoff 指向旧 delivery head，Canonical Evidence 表含旧 commit 和 pending；其中“尚未 commit”的原因现已过期。

## 2. A–E 逐项闭合确认

### A. N1 deadline、guard、失败上报与测试分支

**源码修正确认；运行证据不完整。**

- `ResilientLibraryChannel::shutdown` 建立绝对 deadline 后，fallback 的循环条件是 `Instant::now() < deadline`，轮询与 sleep 均按 remaining 截断：`library_bridge.rs:3926-3932,3965-3987\)。已去掉 R4 指出的 `max(2000ms, remaining)`。
- fallback 获取 `ctx.inner` 后执行 `guard.take()`、`drop(guard)`，再于锁外调用 `shutdown_and_kill_with_deadline(deadline)`：`library_bridge.rs:3971-3979\)。调用确实接收原始 `Instant`；关闭阶段逐段按剩余时间收窄，并未在此处重新计算 1500 ms：`library_bridge.rs:2362-2704`。
- 超时/spawn 失败有 stderr 日志及 atomic 标记；`pub fn` getter 可供同 crate 调用者及测试断言：`library_bridge.rs:3912-3923,3989-3996`。字段为 `pub(crate)`，模块声明为私有（`main.rs:39`），所以不是 Tauri IPC 或用户界面可读取的运行状态；错误日志是运行时外部可见信号。
- 新测试的分支构造是真实的：timeout 用例持锁 600 ms、传入 150 ms 并断言 timeout flag（`library_bridge.rs:6763-6813`）；spawn-failure 用例在主调用线程启用注入、持锁后调用 shutdown 并断言 spawn-failed flag（`library_bridge.rs:6824-6865`）。成功测试也检查 `tasklist` 退出码及目标 PID 缺失（`library_bridge.rs:6696-6757`）。
- **证据缺口**：当前 11 组脚本只调用成功分支测试（`test-ac1-overlay-bound.ps1:182-186`）。verification 中没有 timeout/spawn-failure 两个新测试各自的运行日志、exit 或 metadata；源码测试分支正确不等于有已存档的执行证据。两项运行结果按证据规则记为 **NOT_RUN / 未提供可复核运行证据**。
- A 不能据此视为全闭合，因为下节所列的 deadline mutex、重入及 Drop、任务派发/后台 worker 路径会绕开“全链路单一 deadline”声明。

### B. 逐个阻塞点与统一 deadline

**未闭合，至少有以下具体反例。**

1. `shutdown_deadline` 在 `shutdown_and_kill`、`shutdown_and_kill_with_deadline`、`Drop` 中使用普通 `.lock()`，没有 `min(自身上限, remaining)`：`library_bridge.rs:2350,2363,2709`。并发关闭线程若在持锁期间被挂起，另一个关闭/Drop 线程会无限等这把锁。poison 分支还会开新预算：`library_bridge.rs:2355-2357,2711-2712`。
2. taskkill deadline 归零时仍会先同步 `Command::spawn()`：`library_bridge.rs:2294-2300`；`timeout == 0` 只会让之后的轮询不运行，不会跳过进程启动。即使调用方传入 `min(250ms, rem) == 0`，关闭路径仍可能在原 deadline 之后创建 taskkill。
3. timeout 分支忽略 `child.kill()` 结果，随后派发 taskkill-reaper，并在后台执行无界 `child.wait()`：`library_bridge.rs:2339-2345`。若 kill 失败，reaper 可永久阻塞；线程 spawn 失败也被 `let _ = ...` 忽略。主调用虽然不做同步 wait，但后台线程的有界性与资源回收并未闭合。
4. 其余后台 fallback 也不共享本轮 deadline：pending worker 固定重试 2 s，锁等待每轮 50 ms、sleep 15 ms，并在失败记录时另等 20 ms：`library_bridge.rs:2436-2459`；child-reap worker 固定尝试获取锁 2.5 s，再轮询 400 ms，随后 kill/try_wait：`library_bridge.rs:2591-2638`。它们可以在原 deadline 后继续运行。后者不是无期限循环，但不是共享预算，也不是表中 2400 ms 全链路的一部分。
5. Reader/writer join guard 只对主调用线程的 `recv_timeout` 限时，守护线程本身执行无界 `handle.join()`：`library_bridge.rs:2666-2678,2689-2701`。两个 `Builder::spawn` 的错误只通过 `is_ok()` 分支被忽略，没有记录；若底层 reader/writer 未退出，会遗留 joiner 线程。
6. Drop 仅在 `StdioLibraryChannel` 已登记 deadline 且 mutex 可读时复用它：`library_bridge.rs:2707-2714`。外层 `ResilientLibraryChannel::Drop` 每次调用 `shutdown(2400ms)`，而该方法每次都创建新 deadline：`library_bridge.rs:3926-3929,4002-4006`。此前一次 shutdown 若因 `ctx.inner` 锁竞争派发了未完成 fallback，Drop 可以再派发一个带新预算的 fallback。并且 `shutdown_and_kill_with_deadline` 只在槽为 None 时登记 deadline，却仍按本次传入的 deadline 执行，不会将较晚的 deadline 收窄到已登记值：`library_bridge.rs:2362-2367`。
7. taskkill 成功后确实调用 `child.try_wait()`，但忽略返回值后无条件置位 `child_reaped = true`：重入路径 `library_bridge.rs:2384-2388`、常规路径 `library_bridge.rs:2540-2545`。只有 `Ok(Some(status))` 才能证明句柄已由 Rust `Child` 实际回收；`Ok(None)` 或 `Err` 也会被当前代码错误标为已 reap。

### C. 阻塞点清单、行号和 WCET 复核

**行数修正了，清单与推导仍不闭合。**

#### 我复核的前台阻塞调用位置

| # | 当前源码位置 | 操作与实际边界 | 与 owner 表的差异 |
|---:|---|---|---|
| 1 | `library_bridge.rs:3931-3939` | `ctx.inner` 获取：主线程 ≤ `50ms.min(rem)`；fallback 轮询共享 deadline | owner 表写 3925；后台 worker 的 spawn/fallback 本身未列 |
| 2 | `:2421-2429` | shutdown 的 pending 主锁 ≤ `30ms.min(rem)` | owner 表写 2404 |
| 3 | `:2475-2497` | host_session 获取 ≤ `30ms.min(rem)` | owner 表写 2452 |
| 4 | `:1752`，helper `:1662-1701` | transaction lock 的 try-lock 总预算是传入的 session timeout，最高可达 240 ms；没有 80 ms 单项上限 | owner 表的 80 ms 没有对应代码上限 |
| 5 | `:1767-1779` | pending 注册锁 ≤ `100ms.min(local remaining)` | owner 表写 1765（该行实际是创建 sync channel） |
| 6 | `:1782-1801`，writer 回执 `:1555-1575` | 写入调用方等待按 transaction/session 剩余预算；不是固定 50 ms | owner 表写 1785 并标 50 ms，源码没有该独立上限 |
| 7 | `:1823-1844` | 响应 `recv_timeout` 按 session 剩余预算；最高可能接近 240 ms | owner 表写 1817（实际是 `InFlightGuard`）并标 80 ms |
| 8 | `:1785-1788` | 写入前超时分支清 pending 锁 ≤ `10ms.min(rem)` | owner 2f 合并计数 |
| 9 | `:1803-1810` | 写入失败清 pending 锁 ≤ `10ms.min(rem)` | 同上 |
| 10 | `:1834-1839` | 响应超时清 pending 锁 ≤ `10ms.min(rem)` | 同上 |
| 11 | `:2500-2514` | core.shutdown writer 回执 ≤ `60ms.min(rem)` | owner 写 2515，实际调用在 2513 |
| 12 | `:2517-2519` | child 锁 ≤ `50ms.min(rem)` | owner 写 2520，实际是注释 |
| 13 | `:2521-2525`；helper `:2237-2247` | graceful wait ≤ `1000ms` 且由 remaining 收窄 | owner 把调用后的状态行 2527 当作等待位置 |
| 14 | helper `:2252-2274` | child kill 后 reap 轮询 ≤ `reap_timeout`，由 remaining 收窄 | owner 把 2528 当作 reap 位置 |
| 15 | `:2530-2535` | wait 失败记录锁 ≤ `10ms.min(rem)` | owner 行 2534 正确落在该调用 |
| 16 | `:2537-2545`；helper `:2294-2345` | taskkill 主路径轮询 ≤ `250ms.min(rem)`；但同步 spawn/read/kill 未受此限时；timeout 后另有后台 reaper | owner 仅列 helper 的 250 ms，漏其内部阻塞/worker |
| 17 | `:2546-2551` | taskkill 失败记录锁 ≤ `10ms.min(rem)` | owner 写 2549；实际获取锁为 2550 |
| 18 | `:2660-2664` | reader join-handle 锁 ≤ `30ms.min(rem)` | owner 写 2636 |
| 19 | `:2665-2678` | 主线程等待 reader joiner ≤ `100ms.min(rem)`；joiner 内 `handle.join()` 无界 | owner 写 2648，主线程位置为 2675 |
| 20 | `:2682-2686` | writer join-handle 锁 ≤ `30ms.min(rem)` | owner 写 2658 |
| 21 | `:2687-2701` | 主线程等待 writer joiner ≤ `80ms.min(rem)`；joiner 内 `handle.join()` 无界 | owner 写 2670，主线程位置为 2698 |
| 22 | `:2371-2416,2707-2714,3926-4006` | 重入、Stdio Drop 与 Resilient Drop；按分支调用锁/等待/taskkill，Drop deadline 可能新开 | owner 把此组标 0 ms，忽略重入分支与 outer Drop |

这 22 项只计上述前台代码中可分别触发的阻塞调用位置；owner 表 2f 把三处清理锁并成一行，因而“20”是**行数**，不是该表声称的所有独立代码阻塞点。另有未计入 22 项的阻塞/异步操作：

- `shutdown_deadline.lock()` 三处普通 mutex 等待（`:2350,2363,2709`）。
- taskkill helper 的 `Command::spawn()`、成功后 `stdout/stderr.read_to_string()`、`kill()` 与后台 `wait()`（`:2295-2315,2339-2344`）。
- pending/child fallback 的独立超时循环及清理（`:2436-2459,2591-2638`）。
- reader/writer joiner 中无界 `join()`、joiner 创建失败未上报（`:2666-2678,2689-2701`）。

#### WCET 算式

owner 的主路径算式列项相加是 **2340 ms**，但把 host_session 的 30 ms 锁等待漏在 `session_timeout` 包络之外：session timeout 是在 host_session 锁成功之后才算（`:2475-2480`）。按 owner 表自己的上限，静态和应为：

```text
50 inner
+ 30 pending
+ 30 host_session lock
+ 240 CloseHostSession exchange envelope
+ 60 core.shutdown write
+ 50 child lock
+ 1000 graceful wait
+ 400 reap
+ 10 wait error record
+ 250 taskkill
+ 10 taskkill error record
+ 30 reader handle lock
+ 100 reader main-thread wait
+ 30 writer handle lock
+ 80 writer main-thread wait
= 2370 ms
```

因此，按该理想化列表尚有 30 ms 到 2400 ms。owner 写的“无 envelope”结果 2450 ms 数值碰巧与 `非会话段 + 350ms` 一致，但其公式把漏掉的 host_session 锁与包络差额抵消了；不能据此补足主路径漏项。

更关键的是 2370 ms **不是实现 WCET**：表外的普通 deadline mutex 没有超时；helper 的进程启动/读取不受 timeout 限制；taskkill/reader/writer detached reaper 的等待未有界；若 remaining 为 0，helper 仍会 spawn taskkill。故 `2340/2370ms` 均只能算选择性静态上限之和，不能证明“所有关闭与回收均在 2400 ms 内完成”。另外，在一般 Windows 调度环境中，`sleep` 被系统延迟唤醒时也不能证明真实墙钟时间严格不越过 deadline；可证明的是传给受控等待的超时值被收窄，而不是任意系统抖动下的物理时限。

#### owner 表行号差异

除表中恰好落在相关代码附近的若干行，以下引用与当前 HEAD 的实际阻塞点不符：Step 0 `3925 → 3934`；Step 1 `2404 → 2423`；Step 2a `2452 → 2477`；2b `1750 → 1752`；2c `1765 → 1777`；2d `1785 → 1797-1801`；2e `1817 → 1831`；2f `1774/1792/1821 → 1787/1808/1836`；Step 3 `2515 → 2513`；4a `2520 → 2519`；4b `2527 → 2525`；4c `2528 → helper 2252-2274`；4f `2549 → 2550`；5a `2636 → 2663`；5b `2648 → 2675`；6a `2658 → 2685`；6b `2670 → 2698`；Step 7 应包含 `2363,2374-2416,2709,4005`。

### D. AC2/AC6 声明范围

- **AC2：文字已收窄，但证据 runner 过宽。** Task 将结论限定为已知进程名/工作区特征与隔离根（Task 行约 30-35），未再宣称能排除任意未知断链后代，方向与已有证据范围相符。现有独占复跑记录 0 matching processes、delta=11、runner 后代=0、隔离根删除成功（`ac2-process-tree-audit.log:8-17`）；它支持“该时点没有匹配已知特征的进程 + 隔离根可删”，不能证明未知断链后代绝对为零。
- **AC6：仍未达成，且 Task 说明过期。** Task front matter 仍是 `delivery_head: fdf715e79`、`canonical_evidence_status: pending`（`doc/tasks/P20-CLOSE-BOUND-1.md:17-19`）；Canonical Evidence 多数指向旧 `fdf715e79`，AC2 exit/meta、AC4 inner-lock 组仍为 pending（`:108-110,144-147`）。当前源码 SHA256 为 `1b971be36998c3701190ad5f5f43e5fde01dceed8768fe1bb5a252b5ec9ac119`，Task 中 R5 source pin 仍是 `82c1cc9d...`；审计文件当前 hash 为 `607036d7...`，旧 pin 是 `67d2ed1f...`。Handoff 的 `delivery_head` 也仍是 `fdf715e79`。Task AC6 仍以“尚未 commit”解释未达成（Task 行 42），但当前已有 `5021f039f` 提交；应改为真实原因“提交后 pin/head 未对齐”，并在后续更新中重算 evidence pins。
- Task 的 overlay 测量文字及 audit/Handoff 报告为 **0.4523 ms**，当前入库的 R5 `ac1-overlay-bound.stdout.log` 实测为 **0.4771 ms**。二者都低于测试阈值，但应按实际 run/head 分开引用，不能把旧观测值写成当前证据。

### E. AC5 脚本

**脚本实现修复确认；交互式运行仍待 Coordinator。**

`run-desktop-close-verification.ps1` 会计算并创建自有 `OutDir`（`:15-28`），finally 中写 console log、`ac5.exit`、metadata 的同一个 `$scriptExitCode`，然后执行 `exit $scriptExitCode`（`:183-228`）。当前版本没有直接 `return`，所以 R4 指出的 return 绕过最终 exit 问题已修复；退出码与文件值在正常成功写盘路径上由同一变量构造。没有在 finally 结束前再读取文件做独立断言；若写盘本身失败，则不能声称文件和宿主 exit 一定一致。

脚本逻辑静态闭合不等于 AC5 运行完成：已保存的 `ac5-20261018-1256` 是较早版本证据，仍需 Coordinator 在交互式 Windows 桌面以当前 release build 运行，并保存此次 `OutDir` 产物及进程退出码。

## 3. taskkill-reaper 有界性

**不有界。**

主线程在 taskkill 轮询超时后确实不再同步调用 `child.wait()`，这解决了“主调用线程直接无限等”的一部分问题；但代码把 Child 交给线程后执行无期限的 `wait()`（`library_bridge.rs:2340-2344`）。`child.kill()` 的结果被忽略；线程创建失败也被忽略。如果 taskkill 自身未被成功 kill，reaper 可永久等待，且每次超时都可再创建一条线程。因而“调用线程立即返回”成立，“reaper 有界/无泄漏/回收完成”不成立，也不符合 Task AC4 所列的 bounded `try_wait` 要求。

此外，reader/writer join guard 采用同一种“主线程有 recv timeout、后台线程无界 join”的结构（`:2666-2678,2689-2701`），也应计入后台 worker 有界性审计。

## 4. Coordinator 的“残留”误报范围

`test-ac1-overlay-bound.ps1` 的残留筛选会对**全系统**进程快照工作：全局匹配 `core_service/m2rc1_desktop/host_bridge` 进程名（`:233`）；对命令行含仓库根路径的任意 Python 进程匹配（`:234-241`）；对 suite 开始后新建、命令行含隔离根或 `apps\\desktop\\src-tauri` 的任意进程匹配（`:242-249`）。这些条件没有证明进程是本次 runner 启动的。Coordinator 并行运行的 Python 测试命令行包含仓库路径时会被算作本 Task 残留；所以第一次 suite 的残留 1 是符合脚本误报机制的审计器 false positive，不能作为 P20 失败证据。用户给出的独占复跑 11 组全 ExitCode 0、残留 0 更适合作为本轮证据。

建议把判定改为**本次 suite 记录的启动 PID 及其子孙链 + 每次运行唯一隔离根/句柄清理检查**，删除工作区全局 Python/进程名命中条件。为了仍能识别父进程提前退出的断链后代，应在每条 runner 命令启动时记录 PID/父 PID 与 run-specific 标记，再在结束后追踪这些已记录 PID；仅在结尾从当前 runner PID 做 BFS，无法重建已经断开的进程祖先关系。真实 P20 目标进程应通过本次启动 PID 和独立隔离根识别，避免并行任务干扰。

## 5. 新发现与回归证据

1. **AC4 reaper 状态可能是假阳性**：常规与重入分支都调用了 `try_wait`，但没有检查 `Ok(Some(_))` 就设 `child_reaped=true`（`:2386-2388,2542-2544`）。后续依赖此标志的测试/诊断可能把“taskkill 命令成功”误当作 Rust Child handle 已 reap。
2. **R5 新测试没有进入现有 11 组 runner**：当前脚本 N1 项仅跑成功分支；timeout/spawn-failure 测试没有归档日志与 exit。Coordinator 的 11 组 ExitCode 0 不能替代这两项。
3. **WCET 表“20”是表行数而非独立调用点数**：2f 将三处 pending 清理锁合并；当前前台至少 22 个可分别触发位置，此外另有后台和系统调用。
4. **main.rs 变更归属**：R5 commit 的文件清单没有 `main.rs`。基线间 main.rs 的更改来自其他历史提交（含 P09）；本 Review 未把它们归因给本 Task。
5. **P09 在制品**：未运行 P09 测试，未发现可以从 CLOSE-BOUND 关闭路径静态审查中认定的 P09 失败；P09 在制品未作为本 Task 越界项。

治理检查（只读）使用 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-CLOSE-BOUND-1.md`，结果 `FAIL (37 errors, 3 warnings)`：37 项为当前 evidence SHA 与 Task pins 不一致；warnings 包括本 Review 与 R4 Review 尚未登记为 evidence pin，以及 STATUS/Plan 达到 80% 文档预算。检查未修改文件。Review 新文件需由 Coordinator 后续按 Task 生命周期登记；当前大量 pin 漂移也印证 AC6 未闭合。
现有 R5 日志目录内 11 个 stdout 组均有 `.exit=0`；`resilient_channel` 为 9 passed，`stdio_channel_drop` 为 1 passed，writer overflow、child/pending/inner lock、poisoned lock、reader guard、wait helper 与 shutdown-writes 均各自通过。该证据没有由本 Reviewer 重跑。当前关闭改动未放宽 `write_stdin_timeout` 的 `is_down` 拒绝（`:1582-1590`），专用 shutdown writer 才绕过它（`:1593-1600`）；`MAX_RETRIES=3` 仍在 `:3581-3602`。现有 resilient 日志及源码检查未见 R-008 心跳、R-003 拆环、R-006 呈现或重试阈值退化。

## 6. AC1–AC6 与 P20 收口影响

| AC | R5 结论 | 说明 |
|---|---|---|
| **AC1** | **未达成** | N1 与大部分前台等待正确采用共享 deadline；但普通 deadline mutex、taskkill spawn/read、到期后继续 spawn、外层 Drop 重开预算和后台无界 reaper 使 2400 ms 全链路硬上界不成立。 |
| **AC2** | **部分达成（收窄范围）** | Task 现只声明已知特征/路径范围，独占复跑记录 0 命中与隔离根可删；runner 的全局过滤会把无关 Python/匹配进程算作残留，未证明所有结果属于本次 runner。 |
| **AC3** | **通过已存档回归证据** | 日志显示 resilient 9 passed、stdio drop 1 passed 且 11 组全 exit 0；源码未见 R-008/R-003/R-006 或 `MAX_RETRIES=3` 回归。未由 Reviewer 重跑。 |
| **AC4** | **未达成** | taskkill-reaper 仍无界 wait；其他 detached joiner 也无界 join；deadline/drop/fallback 路径不全受统一上界约束；reap 标志可能误置；WCET 表漏点且引用错行。 |
| **AC5** | **脚本实现通过；交互运行待做** | 自写 OutDir 与 `ac5.exit`/宿主退出码共享同一值，控制流修复成立。Coordinator 仍需当前 release 在交互式桌面复跑。 |
| **AC6** | **未达成** | Task/Handoff delivery head、Canonical Evidence commit/hash 与 5021 当前 HEAD 不一致，多条 pin 旧或 pending；Task 的“尚未 commit”原因过期。 |

**P20 收口影响**：Task 保持 `in_review`，本轮不批准集成或关闭。下一步应由 Coordinator 将本 Review 的 R6 必修点提交给用户裁决；在取得第六轮明确授权前，不向 Owner 派发新的产品返修。获授权后，应优先封住 deadline mutex/outer Drop、所有后台 worker 与 taskkill timeout 路径，修正 reaped 判定与 WCET 表，归档两条新 N1 测试运行证据，并更新 Task/Handoff pins；之后再做当前 build 的 AC5 交互式桌面复跑。


