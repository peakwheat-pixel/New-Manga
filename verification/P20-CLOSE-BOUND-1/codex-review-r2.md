# P20-CLOSE-BOUND-1 独立 Review R2（终审）

- Reviewer：Codex
- Owner：Antigravity
- Base：`4524769b6`
- 实现提交：`bae81ad29`
- 文档提交 / Review head：`95d483888`
- Decision：`changes_requested`
- 范围：只读审查提交差异、关闭调用链、Task/Handoff 与 AC 证据；未修改产品代码、未提交、未 push。
- 验证：当前 HEAD 为 `95d48388883c53b6af6ef4c73299c039b81b2cf5`。复跑测试结果见第 7 节。

## 1. 结论

`decision = changes_requested`。R1 中若干实现点已改进：同步管道写移到专用线程、心跳在 ping 前释放 child 锁、关闭路径采用限时锁、poisoned child 锁可恢复、二次析构由原子标记短路，且叠加测试不再因 `inner.take() == None` 而假通过。但 AC1/AC4 的 3000 ms 可信硬上界仍未成立：关闭协议消息实际被 `is_down` 提前拒绝；超时锁获取失败时会跳过进程回收；2950 ms 推导有漏项且轮询存在预算外超调。AC1 测试也没有同步证明请求已写出并进入响应等待，AC2 的“全树/线程/句柄”审计包含未实际测量的静态结论。

## 2. R1 的 ① 逐点闭合确认

### (a) stdin 写与关闭线程

- **同步写阻塞关闭线程：部分闭合。** `write_stdin_timeout` 将写请求交给 `stdio-library-writer`，带超时调用方通过 `recv_timeout` 返回（`library_bridge.rs:1184-1195,1220-1245`）。这避免关闭线程直接卡在 `WriteFile`。
- **关闭请求并未真正走这条有界写路径。** `shutdown_and_kill` 先在 `1846` 将 `is_down` 置为 `true`，而 `write_stdin_timeout` 在 `1225-1227` 遇到该状态立即返回；后续 `core.shutdown` 调用（`1889`）不会入队。`CloseHostSession` 同样在 `exchange_expected_minor_timeout` 的 `1369` 被拒绝。因此当前代码的 100 ms shutdown-write 阶段是空操作，不能作为“写入已受到 100 ms 控制”的证据。
- writer 自身没有取消正在进行的 `write_all` 的机制；`WriterCommand::Shutdown` 只能排在现有写命令后面。关闭路径最多等 join guard 100 ms 后就放弃等待（`1914-1927`），不会因此阻塞调用线程，但 writer / joiner 可能继续存活。强杀直接子进程通常会关闭其管道读端并令写操作返回；本轮没有满管道、子进程保留 stdin 句柄或 writer 卡住场景的测试，故不能确认所有路径都能释放 `ChildStdin` 与线程。详见第 3 节。

### (b) 心跳是否持 child 锁跨越 `ping_timeout`

- **R1 的持锁跨 ping 问题已闭合。** 心跳只在 50 ms 限时锁内执行 `child.try_wait()`，离开该作用域后才调用 `ping_timeout`（`library_bridge.rs:2993-3008`）。
- **但线程收尾证据不成立。** `start_heartbeat` 没有保存或 join 线程句柄；线程先 `sleep(heartbeat_interval)`，醒来后才检查 stop 标志（`2953-2958`）。叠加测试只设置 `heartbeat_stop`（`5172`），AC2 日志所写“Heartbeat Thread State: Cleanly terminated”并非由 join 或状态观测得出。

### (c) pending / child / reader / ctx.inner 的锁超时

- **直接关闭调用链大多已增加限时获取：** `pending_responses` 50 ms（`1849`）、`host_session` 50 ms（`1859`）、`child` 100 ms（`1892`）、reader/writer handle 各 50 ms（`1898,1914`）；`ResilientLibraryChannel::drop` 与 restart 清理的 `ctx.inner` 使用 100 ms（`2797,3073`）。`CloseHostSession` 通过 `exchange_expected_minor_timeout(..., 250 ms)` 取得 transaction lock（`1869-1871,1360`），因此审计文档“关闭路径完全不索取 transaction_lock”不准确。
- `host_session` 的 MutexGuard 仍跨在 `exchange_expected_minor_timeout` 调用外层作用域，最长持有到该调用返回；它不是文档所述“take 后立即在锁外请求”（`1859-1872`）。
- **限时获取失败时的回收行为未闭合。** `child` 锁超过 100 ms 时，`if let Some(...)` 分支直接跳过 `wait_timeout_or_kill`（`1892-1893`）；但 `shutdown_executed` 已在函数开头置为 true（`1842`），后续 `Drop` 不会重试。若 `pending_responses` 获取失败则跳过唤醒在途请求（`1849-1855`）。因此“有超时”只证明关闭调用能继续返回，不证明超时后仍完成 kill、reap 和等待者唤醒。新增 poisoned 锁测试覆盖的是 poisoned 分支，不覆盖普通 `WouldBlock` 超时分支。
- `ctx.inner` 在 `with_channel`、restart 安装新 channel 等短临界区仍使用普通 `.lock()`（`2868,3037-3043`）。这些不是关闭函数内部的长等待，但审计不能概括为“全链路每处 inner lock 都有限时”。

### (d) 预算、transaction lock 与二次析构

- **二次析构问题已闭合。** `shutdown_executed.swap(true, ...)` 令第二次清理立即返回（`1842-1844`）；`StdioLibraryChannel::drop` 默认传入 1200 ms（`1932-1935`），`ResilientLibraryChannel::drop` 也传 1200 ms（`3070-3081`）。这消除了 R1 中 5 秒第二次析构叠加。
- **2950 ms / 50 ms 裕度推导不成立。** `concurrency-lock-audit.md` 的公式把 close session 记为 250 ms，但漏掉其前面的 `host_session` 锁获取最多 50 ms（`library_bridge.rs:1859`）；transaction-lock 最多再等 250 ms（`1360,1298-1324`）。公式又计入 100 ms shutdown write，但该写当前被 `is_down` 拒绝，实际没有执行。两者互相抵消只是在纸面凑出 2950 ms，不能证明实现预算。
- `wait_timeout_or_kill` 在 1200 ms 与 800 ms 两段都以 20 ms `sleep` 轮询，睡眠后才重新检查 elapsed（`1807-1838`）；`lock_timeout_recover` 用 5 ms 轮询，transaction lock 用 10 ms 轮询（`957-975,1298-1324`）。各段边界可能越过配置时长，且没有共享的绝对 deadline 将超时按剩余预算收窄。因此不能声称 2950 ms 是可验证的严格上界或留有 50 ms 裕度。

### (e) poisoned child 锁是否恢复并 kill

- **poisoned 分支已闭合。** `lock_timeout_recover` 对 `TryLockError::Poisoned` 调用 `into_inner()`（`957-975`），`poisoned_child_lock_is_recovered_and_killed` 通过，实际断言 PID 消失。
- 这不覆盖获取锁超时后跳过 kill 的分支，也不覆盖 `child.kill()` 失败：`wait_timeout_or_kill` 忽略 kill 返回值，调用方又忽略整个 `Result`（`1820,1893`）。失败时 shutdown 仍返回，但 AC2 的零残留没有保证。

## 3. writer 线程与叠加测试的有效性

### writer 线程

写操作被隔离到后台线程，因而关闭调用线程可以在自己的 timeout 到期后继续；这部分设计方向有效。但 timeout 只终止等待 reply 的调用方，不会取消 writer 已开始的 `stdin.write_all()`。`WriterCommand::Shutdown` 也不能中断队首的阻塞 Write；join guard 超时后把 join 工作留在另一个线程继续等待（`1914-1927`）。若管道读端仍被进程树中的其他进程持有，writer 与 joiner 可在 restart 后残留；当前测试未填满管道或检查 writer 线程退出，也未证明 ChildStdin 已释放。该风险不推翻“关闭调用线程不直接同步写管道”，但不支持“writer 线程退出有硬上界”。

### 叠加测试

- **原竞争绕过已修复：** 测试现在 `expect` `inner.take()` 必须为 Some（`5184-5189`），确实调用生产 `shutdown_and_kill`；同一 `shutdown_elapsed` 变量同时用于打印与 `< 3s` 断言（`5193-5205`）。worker join 也有 2 秒守护等待。
- **握手仍不证明请求已写出并等待响应：** `exchange_expected_minor_timeout` 先把 sender 插入 pending（`1375-1377`），再写 stdin（`1394`），写完成后才进入响应接收（`1409-1423`）。测试只轮询 `pending_responses` 非空（`5150-5167`）；观察到 pending 时，worker 仍可能尚未完成 writer 写入。随后测试就外部强杀，存在请求未送达便结束的竞争窗口。
- 测试确实计时了 `shutdown_and_kill` 本身，而非 cargo 总耗时；但它在外部 taskkill 成功之后才开始计时（`5175-5195`），且没有调用 `ResilientLibraryChannel::drop` 这一层入口。被测进程此时已退出，`is_down` 也可能已置位，因此该 201.4 µs 测量没有覆盖满管道写阻塞、优雅关闭或完整窗口退出。
- 当前提交证据 stdout 记录 201.4 µs；我复跑同一过滤测试得到 192.5 µs。两者都只是上述已强杀场景的 `shutdown_and_kill` 耗时，不代表 3 秒最坏路径。

## 4. AC2 / AC5 / R1⑤

### AC2：零残留

本轮 PID 审计日志记录 0 个匹配残留进程；测试本身也在 taskkill 后用 `tasklist` 检查目标 Python PID 已消失。这证明了该运行中的目标测试子进程已退出。完整 PID 树、线程和句柄审计仍不充分：

- `test-ac1-overlay-bound.ps1:158-167` 只检查全局进程名、当前 PowerShell 的直接子进程和少数 Python 命令行，没有从本轮 runner PID 递归遍历 cmd → cargo → 测试 → 子孙 PID；`$repoPath` 虽计算但未用于筛选。
- `$isolatedRootEscaped` 把反斜杠加倍后用于 `-like`（`156,164`），实际 CIM 命令行中的单反斜杠路径可能无法匹配。
- “Heartbeat Thread State: Cleanly terminated”与“没有进程持有隔离根句柄/引用”是直接写入的字符串（`176,187`），脚本没有 join 心跳线程或检查句柄。若筛选到残留，脚本记录数量但没有因 `residualCount > 0` 返回非零（`178-192`）。

所以 AC2 对目标 Python PID 的证据成立，Task 所声明的“PID 树、父子链、隔离根、应用线程与句柄全面核查”仍为 **PARTIAL**。

### AC5：真实桌面关闭

R1 指出的强杀清理误判已修复：主进程没有在 5 秒内退出时，脚本先强杀用于清理，再明确 `exit 1`（`run-desktop-close-verification.ps1:93-105`）；残留进程也会非零退出（`109-129`）。但 Handoff 标注 AC5 为 NOT_RUN，本轮没有交互桌面运行证据，AC5 仍未完成。该脚本的 PID 收集也只取主进程直接子进程，需注意它不能单独证明更深层后代均退出。

### R1⑤：交付指针与运行证据

- **大部分已闭合：** Task 的 `delivery_head` 与 Handoff 均固定到 `bae81ad29`；R2 日志及 metadata 已补 shell、venv、Python 路径；Handoff 状态为 `in_review`。Task frontmatter 仍为 `ready`，按 Owner 记录是当前治理检查对 READY DAG 的要求，不据此认定交付 head 缺失。
- **计时 metadata 有精度丢失：** 当前 HEAD 的 `ac1-overlay-bound.meta.json` 实值是 `shutdown_elapsed_ms: 0`，不是 `0.2014`。测试打印 `Duration.as_millis()` 整数（`library_bridge.rs:5196`），脚本仅解析整数毫秒（`test-ac1-overlay-bound.ps1:114-115`），所以 201.4 µs 被截为 0 ms；raw stdout 保留了微秒值。该字段可能被误读为测量为零。
- AC2 日志本身没有 command、exit code、shell/venv 字段；目前有时间戳和 Python 路径，但不足以支持 README 所称的完整运行证据字段。

## 5. 越界确认

逐提交检查文件名：

- `bae81ad29` 仅改 `apps/desktop/src-tauri/src/library_bridge.rs`、`verification/P20-CLOSE-BOUND-1/**`、`doc/tasks/P20-CLOSE-BOUND-1.md`、`doc/handoffs/P20-CLOSE-BOUND-1-antigravity.md`，均在 Task allowlist 内。
- `95d483888` 仅改 Task 与对应 Handoff，也在 allowlist 内。
- 未发现修改 `main.rs`、共享契约、Schema、依赖、阈值、R-006 错误呈现或其他越界文件。R-008 的心跳释放锁行为与 R-003 弱引用环仍在；`MAX_RETRIES = 3` 未改。
- 按 Coordinator 登记，Owner 自行执行了 git commit，违反项目“由 Coordinator 提交”的流程要求；提交对象的 author/committer 是 `peakwheat-pixel`，Git 元数据不能独立证明执行者身份，因此越界事实依据 Coordinator 的运行记录。内容范围在 allowlist 内，提交未 push；本 Review 未撤销或改写提交。
- Task 明确要求 GUI/故障注入使用 `%TEMP%` 隔离根（`doc/tasks/P20-CLOSE-BOUND-1.md:55`），故不把测试脚本的临时隔离目录列为额外越界。

只读治理检查 `pwsh -NoProfile -File tools/governance/check.ps1` 返回 PASS（2 条文档预算 warning）。

## 6. 新发现与未闭合发现

1. **P1：正常关闭时协议级优雅关闭消息被永久拒绝。** `shutdown_and_kill` 先置 `is_down=true`，随后 `write_stdin_timeout` 必然在入口返回；HostSession 请求也在 exchange 的 is_down 检查返回。正常桌面关闭不会向 Core 发送 `core.shutdown` 或 `CloseHostSession`，只会等 `kill_timeout` 后强杀。应保留对外请求的拒绝，同时提供关闭专用写入路径，且让测试覆盖该路径。
2. **P1：锁超时会以“有限时间返回”换取漏杀/漏唤醒。** child 锁被持有超过 100 ms 时，`shutdown_and_kill` 跳过 child kill；pending 锁超过 50 ms 时跳过 in-flight 通知。`shutdown_executed` 已设为 true，后续 Drop 不重试。应使超时分支仍能可靠推进回收/通知，或将此路径明确纳入验收并证明它不会发生；新增测试需覆盖普通锁竞争超时，不只 poisoned 锁。
3. **P1：AC1/AC4 的 ≤3000 ms 硬上界没有闭式证明。** 审计漏算 host_session 锁、把被拒绝的 100 ms 写入计入预算，并忽略轮询超调；加之锁超时分支可能跳过清理，现有 2950 ms 不能作为总关闭 WCET。使用共享绝对 deadline，逐段按剩余预算等待，并重算包括所有锁、write、kill/reap、join 与析构的总预算。
4. **P2：叠加测试可能在请求写出前触发 taskkill。** pending map 只证明请求登记，不证明写已完成或响应接收已开始。增加一个测试同步点，等 writer 确认写成功且请求进入响应等待后再 taskkill；并计量真实 drop/窗口关闭入口。
5. **P2：AC2 审计不是递归 PID 树/线程/句柄核验，且发现残留不会令脚本失败。** 递归保存本次 runner 的进程链，实际观察 heartbeat/reader/writer 收尾及句柄状态；存在残留时返回非零。
6. **P2：writer 的 timeout 不会取消 writer 操作。** 当前调用线程可以按时返回，但后台写与 join guard 的生命周期没有硬上界证据。新增大于 pipe capacity 的写入故障注入，并证明 kill 后 writer、joiner 与 ChildStdin 全部退出/释放。
7. **P2：关闭/kill 失败被静默吞掉。** `child.kill()` 与 `wait_timeout_or_kill` 结果均被忽略（`1820,1893`）；即使强杀或 reaping 未成功，生产关闭仍静默返回。至少应记录/上报失败，并让 AC2 验收检测进程仍存在。

## 7. AC1–AC6 与 P20 收口影响

| AC | R2 复核 |
|---|---|
| AC1 | **未达成。** 有限时锁、异步 writer 与 kill 机制已有实现；但硬上界推导不可信，测试未证明请求已进入响应等待，计时只覆盖外部强杀后的直接 `shutdown_and_kill`。 |
| AC2 | **部分达成。** 目标 Python PID 消失有直接断言；完整 PID 树、heartbeat/writer/reader 线程、句柄和脚本失败行为未证实。 |
| AC3 | **达成。** 当前 HEAD 复跑 `resilient_channel`：9 passed；`stdio_channel_drop`：1 passed；poisoned child、reader guard、wait helper 各 1 passed。R-008/R-003/R-006 与阈值未见回归。 |
| AC4 | **未达成。** 并发审计文档与代码行为不符，遗漏锁/轮询预算，且超时分支可能跳过清理。 |
| AC5 | **未执行。** 强杀误判修复有效；需 Coordinator 在交互式桌面复跑 `run-desktop-close-verification.ps1`。 |
| AC6 | **部分达成。** 主要运行日志已补环境字段；AC1 metadata 计时精度被截断，AC2 审计日志与静态结论缺少可复核运行证据。 |

因此本 Task 不应进入 done/closed，R-009 关闭硬上界仍未解除。P20 其他状态不在本 Review 授权内；在本 Task 获得后续独立 Review 通过、AC2 证据补实并由 Coordinator 完成 AC5 交互式复跑前，不应把“关闭硬上界”作为已验收收口条件。推荐下一步由 Antigravity 在现有 allowlist 内修复第 6 节问题并交付新 head；随后由 Codex 复审，再由 Coordinator 执行 AC5。
