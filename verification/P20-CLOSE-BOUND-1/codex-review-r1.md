# P20-CLOSE-BOUND-1 独立 Review R1

- Reviewer：Codex
- Owner：Antigravity
- Base：`8bf3ae30a`
- Reviewed implementation：`3c46f6522`
- Review head：`4524769b6`
- Decision：`changes_requested`
- 范围：只读复核实现 diff、Task/Handoff 与对应验收证据。未修改产品代码；未触碰既有未提交内容。

## 1. 结论

`decision = changes_requested`。目前不能确认 AC1 的 3000 ms 是完整关闭路径的硬上界：关闭路径仍有同步管道写和无超时 Mutex 获取；3000 ms 公式遗漏了额外等待与第二次析构清理。叠加测试也可能在未计时或未调用被测清理的情况下通过。AC3 指定回归通过；没有发现本提交改动禁止文件、共享契约、Schema、依赖或阈值。治理检查通过（有两条文档预算提醒）。

## 2. AC1（硬上界）逐项复核

**结论：当前实现没有建立完整的 3000 ms 硬上界。**

已确认的改进：`wait_timeout_or_kill` 用 `try_wait()` 轮询替代超时后的 `child.wait()`，强杀后最多轮询 1000 ms；reader 的生产清理路径用守护线程和 500 ms `recv_timeout` 代替在主关闭线程直接 `join()`。但这些上界不能覆盖关闭路径其余步骤：

1. **同步 stdin 写仍可阻塞关闭。** `shutdown_and_kill` 在 `library_bridge.rs:1799-1801` 用 `try_lock()` 取得 stdin 后执行 `writeln!`/`flush`。`try_lock` 只约束获取 Mutex 的时间，不约束管道写；sidecar 不读取且管道已满时，写操作可以阻塞，后续 `child.lock()` 和强杀逻辑不可达。`exchange_expected_minor_timeout` 同样在 `library_bridge.rs:1298-1315` 先做同步 `write_all`/`flush`，再进入响应超时等待，所以响应 timeout 不能限制写入时间。心跳在 `library_bridge.rs:2891-2896` 持有 `child` 锁期间调用 `ping_timeout`，因此这类写阻塞也能让关闭线程无限期等待 `child.lock()`（`1805`）。
2. **关闭路径仍获取多个无超时 Mutex。** `pending_responses.lock()`（`1761`）、`child.lock()`（`1805`）、`reader_join_handle.lock()`（`1811`）和 `ctx.inner.lock()`（`2693`、`2965）都没有超时。`pending_responses.drain()` 本身只是有限的内存遍历及容量为 1 的响应发送；在正常持锁者路径下没有发现它等待 I/O，但锁获取本身没有硬上界。审查材料把 `child` 描述成仅做非阻塞查询、把 stdin 描述成 0 ms，与持锁跨 `ping_timeout` 和同步写不符。
3. **3000 ms 预算少算步骤，且析构会再次清理。** `shutdown_and_kill` 在 child wait 前还有 host-session 处理；其 transaction-lock 获取有 500 ms timeout（`1783`），该时段没有计入 1500+1000+500 的预算。另 `ResilientLibraryChannel::drop` 在锁外调用 1500 ms 关闭后，若释放的是最后一个 `Arc`，`StdioLibraryChannel::drop` 会再调用一次 `shutdown_and_kill(5s)`（`1828-1830`）。第一次 kill/wait 返回 `TimedOut` 时，第二次调用仍可额外等待 5 秒再进行 1000 ms kill-wait；这不符合单次 3000 ms 的总关闭预算。
4. **错误/失败分支可能跳过进程回收。** host-session/stdin 的 `try_lock` 失败会跳过优雅关闭请求，但若之后 child 锁取得成功，仍会尝试终止进程；这两个跳过本身不必然造成进程残留。相反，`child.lock()` 返回 poisoned 时当前 `if let Ok` 静默跳过整个 `wait_timeout_or_kill`；`Child` 被 drop 不会替代显式 kill/reap，因此这条错误路径不能声称零残留。
5. **reader guard 的正常唤醒成立，但验证偏弱。** reader 正常结束时守护线程 `join()` 返回后会发送 `done_tx`（`1817-1821`），主线程因此能提前结束等待。超时则 reader/joiner 被 detach；它们不会阻止进程退出，但可能继续存活至宿主进程退出。新增 guard 测试（`5122-5150`）只复制“join + recv_timeout”算法，没有调用生产 `shutdown_and_kill`，不能证明生产锁范围、spawn 失败或 detach 路径。

叠加测试启动的确实是一个存活、不会响应的 Python 子进程（`time.sleep(60)`），且 `taskkill /F` 成功；不是已退出假 child。但它没有同步确认请求已进入响应等待。外部 kill 会令 reader 收到 EOF 并触发 `on_down`/异步 `trigger_restart`；恢复线程可先在 `library_bridge.rs:2693-2700` 取走 channel。随后测试自己的 `inner.take()`（`5053-5060`）可能得到 `None`，跳过被测关闭却仍通过 3 秒断言。`worker_handle.join()`（`5072`）在关闭计时之外且无 timeout。因此现有 0.33 秒测试总耗时不足以证明关闭调用本身按期完成；成功日志也没有打印 `shutdown_elapsed` 的实测值。

## 3. AC2 / AC3 / AC4 复核

- **AC2 零残留：部分证实。** 叠加测试检查了被 taskkill 的那个 Python PID 已不在进程表中，且检查命令退出码成功。这能证明该测试 child 被杀掉。`ac2-process-tree-audit.log` 的脚本只按 `core_service`、`m2rc1_desktop`、`host_bridge` 名称筛选，不按本次运行 PID/父子关系核查；它不会覆盖名为 python 的测试进程，也没有运行真实桌面/sidecar 进程。测试没有启动 heartbeat，因此也未验证 heartbeat 线程收尾。不能据此把 AC2 的完整进程树及线程条件标为已证实。
- **AC3 不回归：通过指定回归。** 我在 `4524769b6` 实际运行 `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel`：9 passed、0 failed、exit 0；运行 `... stdio_channel_drop`：1 passed、0 failed、exit 0。没有发现已确认的 R-008、R-003、R-006 或阈值被重开/改变。
- **AC4 并发审查：审查材料结论不成立。** `concurrency-lock-audit.md` 漏掉 `child` 锁跨 `ping_timeout`、stdin 同步写不受 response timeout 控制、reader handle MutexGuard 覆盖 `recv_timeout`（`1811-1823`），也未计入第二次 `StdioLibraryChannel::drop` 清理。锁外关闭使用取出的旧 `Arc<StdioLibraryChannel>`，强杀的 child 与该 Arc 绑定，没有看到“拿旧 Arc 却杀新 channel”的直接串线；但并发 EOF 重启会竞取 `inner`，令新增叠加测试的计时路径不确定。锁审查需按真实调用链重做。

## 4. 新发现问题

1. **P1：关闭路径仍可能无限阻塞，3000 ms 不是完整硬上界。** 同步 stdin 写、持锁跨 heartbeat ping、关闭路径无超时锁获取及第二次析构清理均见 AC1。需让关闭步骤本身可中断/有界，并让所有重试/析构合计纳入预算。
2. **P1：叠加测试存在竞争绕过。** EOF 回调可让恢复线程先取走 channel；测试的手动 take 可为空，导致时限断言没有测到清理。应以同步握手证明请求已发出并等待响应、串行化/关闭自动恢复干扰，实际经过生产 drop/关闭入口，并把在途调用解除纳入有界断言。
3. **P2：AC2 的全树零残留证据不足。** 目前只验证一个测试 PID 与一组全局进程名，未按本次隔离根及 PID 树审计实际应用、sidecar 和后代进程。
4. **P2：AC5 复跑脚本可能把强杀清理误判为通过。** `run-desktop-close-verification.ps1:100-101` 在应用未于上界内正常退出后执行 `$proc.Kill()`；如果随后残留进程数为零，`127` 会打印 `Clean exit verified`、`133` 返回 0，即使 `exitedInBound` 为 false。应保留清理动作，同时让正常退出失败明确返回非零。
5. **P2：交付指针与证据环境记录未完成。** Task 与 Handoff 分别仍为 `status: ready` / `delivery_head: pending`，而实际实现提交为 `3c46f6522`；应按生命周期更新为 `in_review` 并固定交付 head。新增 N-passed 日志/metadata 没有记录 shell/venv 类型与 Python 解释器路径，不满足 `doc/09_COLLABORATION.md` §6.12 的运行证据要求。`ac1` metadata 的 898.76 ms 是 cargo 命令总时长，stdout 的 0.33 s 是测试总时长；成功日志未单独记录关闭段耗时。

## 5. 基线漂移的定性与建议

按 Coordinator 给出的可比结果，基线为 117 passed / 12 failed / 1 ignored，本次为 120 passed / 12 failed / 1 ignored；新增 3 个测试通过，失败数量与基线一致，因此没有证据把这 12 项归因于本次实现。指定的两组 AC3 回归我也独立重跑通过。

目前将这 12 项定性为**环境/测试运行配置漂移，且暴露集成测试对 `M2RC1_PYTHON` 的环境依赖缺少自检或隔离**，不是已证实的产品缺陷。单个 `same_channel_concurrent_round_trips_keep_response_ownership` 在设置变量后通过，不能单独证明其余 11 项同因。建议另立环境修复 Task：固定并记录 Python 可执行文件路径，补足完整套件运行环境证据，分别在基线和当前 head 重跑；未完成前将完整套件记录为带既有失败的环境阻塞，不将失败忽略或计为全绿。该基线漂移不改变 AC3 两项指定回归的通过结果，也不是本 Review 的主要拒绝理由。

## 6. 阻断项 / 遗留项与对 P20 收口的影响

- 本 Task 目前不能通过 Review：先修复关闭链路剩余阻塞、3 秒预算与重复析构问题；重做能确实触发生产关闭路径、覆盖在途调用并验证零残留的叠加测试和并发审查，再固定新 head 复审。
- AC5 **未运行且未被 Owner 声称通过**；Handoff 如实标为 `NOT_RUN`。不需要为纠正虚假通过声明而重跑；但 Task 完成前仍须在交互桌面执行修正后的 AC5 脚本。当前脚本可误报成功，不能直接作为有效 Gate。
- 本次变更没有修改 `STATUS`、`REBASELINE_PLAN`、`P20.md` 或 `P20-ISOLATION-1.md`，也未改共享契约、Schema、依赖、AC 阈值；用户 43 项未提交改动保持未触碰。此前已确认的 R-008、R-003、R-006 保持原结论。
- **对 P20：** R-009 窄 Task 尚未关闭，因此 P20 收口不能把“关闭硬上界”标成完成；待修复通过独立 Review、AC5 实测并按治理流程更新 Task/证据后再裁决。

推荐下一步：由 Antigravity 在本 Task 范围内修复上述 P1/P2 项、更新 Task/Handoff 与证据 pins，提交新 head 后交 Codex 独立复审；随后由 Coordinator 在交互桌面完成 AC5。
