---
task_id: P20-CLOSE-BOUND-1
reviewer: Codex
owner: Antigravity
base_commit: 694de50789de4e9b6ecde831364ddbca167fcb44
reviewed_head: d4e3b3eb96c036f67da28909a485dab354b1dbe4
decision: changes_requested
---

# P20-CLOSE-BOUND-1 独立 Review R3

## 1. 结论

**decision = changes_requested**。固定审查范围为 `694de5078..d4e3b3eb9`。当前工作区 HEAD 已前移至 `b6f6da892`：后续 `9bbd3a3e7` 更新了 Task 中 AC5 的桌面运行记录，`b6f6da892` 更新 P09 文档；两者不属于本 Review 的 reviewed_head。

只读检查了固定提交、关闭调用链、R2 Review、Task/Handoff、R3 测试源码及落盘日志。未改产品代码、未运行 `cargo build` 或测试套件。仅新增本 Review 文件。按项目要求运行只读治理检查：`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-CLOSE-BOUND-1.md`，结果 **FAIL（22 errors, 3 warnings）**，包括 22 条 evidence SHA-256 不匹配与未登记过程文件 warning。

尚有 P1 闭环缺口，不能批准 AC1/AC4；AC2/AC6 也只有部分证据。P2#4 的生产入口计时与写后握手基本闭合。

## 2. R2 六项逐项闭合确认

### P1#2 — 未闭合：超时 fallback 没有完成回收保证

- `library_bridge.rs:2088-2098` 的 `child-reap-fallback` 只捕获 `child_id`，固定 sleep 两秒并打印 `fallback reap completed`；没有取得 `Child` 锁，也没有调用 `child.wait()`。Handoff `:17` 对后台 `child.wait()` 的声明与实现不符。
- `pending_responses` fallback 在 `:1995-2005` 最多等锁 500 ms，超时后静默退出；线程 spawn 结果也被 `let _` 忽略。锁持续竞争超过 500 ms 或 spawn 失败时，`recv()` 无自身超时的调用者仍可能永久等待。现有测试只覆盖 250 ms 持锁。
- 普通 child 锁竞争测试能证明目标 Python PID 被杀，但不能证明 fallback reap；测试中的锁仅持有 300 ms。`child_killed` 在 taskkill 结果未知时仍被置为 true（`:2083-2086`），后续 Drop 不会重试。

**建议**：让 fallback 真正拥有可回收的 Child/进程句柄，并观察 wait 结果；pending fallback 需避免超时后放弃通知，并将 spawn/终止错误作为失败状态暴露。

### P1#3 — 未闭合：共享 deadline 没有覆盖整个关闭调用

- 绝对 `deadline` 在 `StdioLibraryChannel::shutdown_and_kill` 的 `:1976-1979` 才创建；生产入口 `ResilientLibraryChannel::shutdown` 先在 `:3291-3295` 独立等待 `ctx.inner` 最多 50 ms。该外层等待不在 deadline 内，且超时会直接返回、不调用 channel shutdown，详见新发现 N1。
- 三处 `Command::new("taskkill").output()`（`:1966-1968`、`:2066-2068`、`:2083-2085`）同步等待命令完成，没有 timeout/deadline；因此 2400 ms 的“动态物理上限”没有覆盖所有阻塞等待。
- `exchange_expected_minor_timeout_internal` 的 request timeout 到期后仍会额外获取 `pending_responses` 锁 50 ms 清理（`:1481-1483`、`:1507-1511`）；这段不再按关闭的剩余 deadline 截断。错误记录路径还使用普通 `last_shutdown_error.lock()`（`:2062`、`:2079`）。
- `shutdown_executed` 的重入分支并非总是 0 ms：若并发进入且 `child_killed` 尚为 false，会再获取 child 锁并运行 `wait_timeout_or_kill(200 ms)`（`:1958-1970`）；其强杀后 reap 另有固定 400 ms（`:1931-1944`），且 taskkill 仍无界。

### P2#4 — 基本闭合，保留一个握手精度限制

`exchange_expected_minor_timeout_internal` 仅在写成功后递增计数（`:1480-1494`），RAII guard 在 `recv_timeout` 返回后才递减；测试等待该计数后才 taskkill，并单独计时真实入口 `resilient.shutdown`（`:5372-5407`）。因此已排除“只登记 pending、请求尚未写出”的旧竞争。

计数在调用 `rx.recv_timeout` 前一刻更新，并不直接观测线程已经阻塞在该调用里；它证明写成功且执行流到达响应等待阶段，不是内核级阻塞观测。该限制不推翻写出握手，但不应再称为对线程调度状态的直接观测。

另有报告数字不一致：Task/Handoff/审计文档称 `0.5072 ms`，当前 `ac1-overlay-bound.stdout.log` 和 metadata 实值均为 `0.4826 ms`（metadata 的精度修复有效，记录的是浮点毫秒）。

### P2#5 — 部分闭合：BFS 与失败路径有实现，快照可能漏掉断链后代

脚本确实从本次 PowerShell runner `$PID` 以队列 BFS 枚举后代（`test-ac1-overlay-bound.ps1:175-191`），隔离根删除失败会计入残留（`:245-251`），任一测试失败或残留会 `exit 1`（`:257-272`）。这几项声明成立。

但快照在全部 `Run-LoggedCommand` 子进程都 `WaitForExit()` 后才取（`:59`、`:173-175`）。若遗留进程的直接父进程是已退出的 cmd/cargo/test runner，该父 PID 不在 `$allProcs` 中，BFS 无法沿已消失的节点发现后代；当前审计日志也记录 `Recursive Descendant PIDs Scanned: 0`。隔离目录删除只证明目录可删，不证明线程或管道句柄都退出。

### P2#6 — 未闭合：测试没有断言 writer/joiner/ChildStdin 已释放

2 MB 写入测试让不读 stdin 的子进程保持存活，断言调用线程在 500 ms 内返回；2 MB 远超本次运行中可写入的管道容量，测试 stdout 显示该测试通过。kill 后测试没有读取 writer 的 `BrokenPipe` 结果或观察 writer 线程完成。

`shutdown_and_kill` 在 `:2105`、`:2125` 先从 slot `take()` join handle，再由守护线程 join；`recv_timeout` 结果被忽略（`:2116`、`:2137`）。测试 `:5888-5901` 只断言 slot 为 `None`，而 slot 在 join 之前就已被取空；这不能证明 joiner 完成，也不能证明持有 `ChildStdin` 的 writer 已退出。可能永久阻塞的 joiner 仍可在主调用超时后脱离。

### P2#7 — 部分闭合：主 wait 错误上报了，taskkill 兜底失败仍静默

`wait_timeout_or_kill` 现在记录 `child.kill()` 错误及 reap 超时（`:1925-1953`），主关闭分支也记录 `wait_res` 错误至 `last_shutdown_error`（`:2058-2064`）。但随后的 taskkill `.output()` 结果被忽略，且无论结果如何都设置 `child_killed=true`（`:2065-2070`、`:2082-2086`）。重入分支又忽略 `wait_timeout_or_kill` 和 taskkill 两个结果（`:1962-1969`）。

AC2 的特定测试若目标 Python PID 仍在会失败，但生产关闭没有记录 taskkill 失败，也没有基于该结果区分“已杀”与“未杀”。

## 3. WCET 闭式性专项结论

`concurrency-lock-audit.md:48-55` 的列项算术为 **2070 ms**，不是 2120 ms：`50 + 30 + (30 + 80 + 50 + 80) + 60 + (50 + 1000 + 400) + 130 + 110 + 0 = 2070`。若只修正算术，名义裕度应为 **930 ms**，不是 880 ms；2120 ms 是保守多算 50 ms，但不能称为表内公式的结果。

更重要的是，这组数仍不是完整闭式上界：生产入口外层 `ctx.inner` 等待未受同一 deadline 控制；`taskkill.output()` 没有 timeout；CloseHostSession 的 timeout 清理锁可再等待 50 ms；`last_shutdown_error.lock()` 是未设上限的 blocking lock；重入分支不走首次 deadline。`poll.min(remaining)` 消除计划 sleep 时长超过剩余预算的情况，但操作系统线程晚于 sleep 目标时间恢复时，仍不能推出“物理执行时间严格不超过 2400 ms”。

因此，静态表即使把 2120 改成 2070，也不能证明 AC1 的实现保证；当前 3000 ms 结论仍缺少对同步 taskkill、外层锁超时失败语义及超时后清理的闭环。

## 4. taskkill fallback 的 PID 复用与线程有界性

- `child_id` 来自新建通道时的 `child.id()`（`library_bridge.rs:1213`），来源可靠；调用 taskkill 前没有显式重查 PID 身份。
- Windows 的进程对象在句柄关闭前仍被引用；Rust Windows `Child` 持有进程 handle，关闭代码借用 `&self` 时 `Mutex<Child>` 仍存活。因此当前 fallback 调用期间没有证据表明 PID 可被复用并误杀无关进程。见 [Microsoft 的进程句柄与标识符说明](https://learn.microsoft.com/en-us/windows/win32/procthread/process-handles-and-identifiers) 与 [Rust Windows std 进程实现](https://github.com/rust-lang/rust/blob/main/library/std/src/sys/process/windows.rs)。代码仍依赖 Child handle 生命周期；未来若在 taskkill 前释放该 handle，就必须重新校验身份或使用进程 handle 终止。
- `child-reap-fallback` 自身有固定 2 秒后退出，pending fallback 最多尝试 500 ms，二者并非无限等待线程；但 child fallback 没做 reap，pending fallback 会放弃通知。reader/writer joiner 的 `.join()` 则可长期等待，主关闭只限时等 done channel 后脱钩。
- taskkill 命令的执行耗时自身没有上界，且执行结果没有检查；所以 fallback 的调用线程边界与实际回收成功是两件不同的事。
- 三处 taskkill 参数只有 `/F /PID`，没有 `/T`；Microsoft 文档说明 `/T` 才会终止指定进程启动的子进程。若 sidecar 已启动 helper，fallback 只杀 PID 不保证整棵进程树退出；当前锁竞争测试只启动一个 Python sleeper，没有覆盖孙进程。此为 AC2 的条件风险，需用进程树故障注入或确认当前 Core 不会派生进程来闭合。

## 5. 新发现

### N1 — P1：`ctx.inner` 锁超时会静默跳过生产关闭

`ResilientLibraryChannel::shutdown` 在 `library_bridge.rs:3291-3295` 对 `ctx.inner` 等待 50 ms。锁仍被占用时 `chan=None`，函数直接返回，不记录失败、不发起备用关闭；channel 仍留在 `inner`，且此函数没有设置该 channel 的 `is_down`。显式调用者会得到“已返回”但 Core 仍运行的结果。AC1 的真实入口不能只对 `shutdown_and_kill` 做上界计时。

**建议**：对取 channel 失败建立可验证的后续关闭/错误报告路径，不能把锁超时当作关闭完成。

### N2 — P2：AC6 的 evidence pins 与当前证据不一致

Task `:17` 与 Handoff `:6` 的 `delivery_head` 仍是 `bae81ad29`；Task Canonical Evidence 表 `:92-122` 的源码、R3 测试输出和审计文件也仍 pin 到旧 commit/hash。例：Task `:93` 的 AC1 stdout pin 是 `bae81ad29` / `6abe...`，当前 stdout SHA-256 为 `A7FB2AD151B6569B5F2CE8888F3548B6C3A09E9233ABCF81FE4E27505E69C652`。按协作协议 §4.1，路径对应的 commit/hash 不匹配即不能作为当前 canonical evidence。

AC1 数值也有文档和日志不符（文档 0.5072 ms，stdout/meta 0.4826 ms）。AC2 日志没有环境头、命令和退出码字段。当前 HEAD 的 Task 将 AC5 更新为 12:44 的 146.69 ms，但 Handoff 仍记录 11:55 的 76.54 ms；`verification/P20-CLOSE-BOUND-1/` 中没有 `ac5-20261018-1245` 原始证据文件可供复核。AC5 的交互式运行已有 Coordinator 记录，但应把实际日志/metadata、release hash 与正确 commit pin 入库；若无法恢复，再由 Coordinator 重跑。

**建议**：更新 Task/Handoff 的 delivery head 与每条 canonical evidence commit/hash，统一 AC1 实际数字，并保存 AC5 原始运行产物后再把 AC6 标为完整。

### N3 — P2：PID 强杀测试没有覆盖后代进程

`library_bridge.rs:2066-2068, 2083-2085` 的 `taskkill /F /PID` 不带 `/T`，而 `child_lock_contention_timeout_fallback_kills_child_and_prevents_orphan`（`:5742-5789`）只验证单个 Python 子进程退出。若 Core 进程派生 helper，parent PID 消失并不等于整个树清空；该分支需要进程树测试或保证 sidecar 不创建子进程的证据。Microsoft 的 [taskkill 文档](https://learn.microsoft.com/windows-server/administration/windows-commands/taskkill) 将 `/T` 定义为同时结束目标进程创建的子进程。

### Standards 视角

存在文档证据纪律问题：Handoff `:17` 宣称 fallback 在锁释放后调用 `child.wait()`，实现没有该行为；这违反协作协议 §4.1、§5 对实际交付/证据引用的要求。重复的 taskkill 调用属于判断型 **possible Duplicated Code**（`:1966`、`:2066`、`:2083`）；本 Review 将其错误处理差异作为 P2#7，而不另列风格阻塞。

### Spec 视角

Task AC1、AC2、AC4、AC6 的关键要求尚未全部达到：child fallback reap、全链路上界、完整后代审计、writer/joiner/ChildStdin 释放断言以及当前 evidence pins 均不成立或不完整。P2#4 的请求已在写成功后进入等待阶段，测试也计量真实生产关闭入口。

## 6. 越界检查

`d4e3b3eb9` 实际修改 **40 个文件**，均落在 Task allowlist：`library_bridge.rs`、Task、Handoff、`verification/P20-CLOSE-BOUND-1/**`；未改 `main.rs`、Schema、依赖、共享契约、阈值或禁止路径。提交文件集合与当前 43 项 tracked dirty 路径交集为 **0**；未跟踪项目不作清理或改动。

## 7. AC1–AC6 与 P20 收口影响

| AC | R3 独立复核 |
|---|---|
| AC1 | **未达成。** 2120 ms 算术不符；生产入口的全部阻塞点未共享 deadline，taskkill 同步等待无界。 |
| AC2 | **部分达成。** 当前日志记录 0 个残留并成功删除隔离根；BFS 与非零失败路径真实存在，但 post-run 快照可能漏掉父进程已退出的后代，不能证明完整进程树为零。 |
| AC3 | **通过现有证据。** 已入库日志显示 `resilient_channel` 9 passed、`stdio_channel_drop` 1 passed；关联的 wait helper、reader guard、poisoned lock 与 P1#1 shutdown-write 测试均有 exit 0。R-008 心跳、R-003 拆环、`MAX_RETRIES=3` 阈值未见退化；R-006 错误呈现路径未改动，但本轮未单独复跑其测试。 |
| AC4 | **未达成。** P1#2/P1#3 未闭合；2 MB 注入成立，但资源释放断言不足；taskkill 兜底错误仍被忽略。 |
| AC5 | **有 Coordinator 的桌面运行声明，但证据未完整入库。** 当前 Task 记录 R3 release 12:44 / 146.69 ms / 零残留；Handoff 和当前 `verification` 目录没有对应原始运行产物。恢复并 pin 原始证据；若无法恢复则由 Coordinator 在交互式桌面重跑。 |
| AC6 | **部分达成。** 多数单项测试日志有环境头和 exit 0；suite 逻辑有失败 exit；但 Task/Handoff delivery head、canonical pins、AC1 数字和 AC2/AC5 原始证据未对齐。 |

**P20 收口影响**：Task 维持 `in_review`，不进入 `done/closed`；R-009 关闭硬上界不能标记已验收。下一步建议 Coordinator 将本 Review 的 open findings 登记为 `changes_requested`，再请用户裁决是否授权第 4 轮返修；授权前不应派发实现任务。

### Architecture 与 Verification

- **Architecture：通过范围检查。** 变更限于 Tauri/Rust sidecar 生命周期、Task/Handoff 与 verification；未改共享 IPC、Schema、依赖或 React/SQLite 边界。
- **Verification：**

| 检查 | 命令或证据 | 结果 |
|---|---|---|
| 固定提交代码与测试审查 | `git diff 694de5078..d4e3b3eb9` 及受影响函数/调用点 | PASS（静态只读审查） |
| 既有 AC3 日志 | `ac3-resilient-channel.stdout.log`、`ac3-stdio-channel-drop.stdout.log` 及关联 exit/meta | PASS（日志记载；本 Review 未重跑） |
| P1/P2 R3 测试日志 | child lock、pending lock、writer overflow、shutdown writes | PASS（各单项日志记载；不足以闭合资源/回收断言） |
| 完整 AC1 runner | `pwsh -NoProfile -File verification/P20-CLOSE-BOUND-1/test-ac1-overlay-bound.ps1` | NOT_RUN（避免重写证据文件；未执行构建） |
| Release build | `cargo build` | NOT_RUN（按用户明确限制） |
| 治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-CLOSE-BOUND-1.md` | FAIL（22 errors, 3 warnings） |
| AC5 交互桌面 | Task 声明的 `ac5-20261018-1245` | NOT_RUN by Reviewer；Coordinator 声明已运行，原始产物未在版本化 evidence 目录找到 |

Verdict: fix P1#2, P1#3 and the listed evidence/resource findings before approval.
