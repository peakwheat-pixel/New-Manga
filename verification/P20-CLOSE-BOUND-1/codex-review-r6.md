# P20-CLOSE-BOUND-1 Codex Review R6（终审）

- `decision`: **changes_requested**
- `reviewed_head`: `835f4bb17df565581a76cf66062760cdd3c85a9e`
- `parent`: `e44a589a0a49193cf38b9184f30c498bf10bff13`
- `scope`: 仅审查该提交中的 `library_bridge.rs`、验证脚本、handoff 与证据；未将 P09 未提交内容计入问题。没有运行 `cargo build` 或测试，复核了已归档日志、脚本、哈希与源码。
- `closure_disposition`: 按用户授权以 `closed_with_limitations` 收口；下节的遗留项应由加固 Task 接手，不将未通过项改写为 PASS。

## 1. 最终判定

**`changes_requested`。** 本轮确实修掉 R5 的 deadline Mutex、Drop 重开预算、零预算启动 taskkill、以及 `child_reaped` 假阳性问题。但 AC1/AC4 的核心承诺仍无法由实现和审计证明：fallback 在 deadline 后仍有清理动作；reader/writer reaper 只限制等待它们的 reaper 线程，没有终止仍阻塞的原 worker；多个 `join()` 仍无显式时限；WCET 清单未覆盖线程创建、taskkill 输出读取等同步成本。AC6 的哈希与 Task pins 在终审时未对齐；收口时已校正可核条目，但 exact-head 桌面 OutDir 仍欠缺。

按用户的最终裁决，本 Review 将本 Task 的 disposition 定为 **`closed_with_limitations`**；遗留项单列给 `P20-CLOSE-BOUND-HARDEN-1`。P20 的 AC7 打包/四页 Gate 本身不因这些 findings 变成 FAIL；关闭路径硬上界与零残留子 Gate 仍不得声称已证明。

**Standards 视角：** 未发现违反明确编码规范的硬问题。非阻塞质量项是 deadline CAS 实现在 `library_bridge.rs:1506-1534` 与 `3863-3891` 重复；`git diff --check e44a589a 835f4bb17` 仅报告 3 个新增 stdout 日志 EOF 空行。详细 findings 以 Spec/AC 为准。

## 2. R5 七项逐项复核

| # | R5 finding | 本轮判定与证据 |
|---|---|---|
| 1a | `shutdown_deadline` 普通 Mutex 阻塞 | **部分闭合。** `shutdown_deadline` Mutex 已消失；`StdioLibraryChannel` 使用 CAS：`library_bridge.rs:1506-1524`，`ResilientCoreContext` 使用重复实现：`:3863-3881`。但两个 `register_deadline` 都是无重试上限的 `loop`。CAS 是 lock-free，不等于每次调用有 wait-free 时间上界；审计把它记为 0 ms（`concurrency-lock-audit.md:13,44`）没有依据。`offset_ms.max(1)`（`:1507-1508,3864-3865`）还会将零/已过期相对截止值编码为至少 +1 ms。 |
| 1b | Drop 复用已登记 deadline | **闭合。** `StdioLibraryChannel::drop` 先取已有 deadline，仅缺失时新建：`:3016-3023`；`ResilientLibraryChannel::drop` 同理：`:4363-4371`。之后都交给 deadline 版本的 shutdown。 |
| 1c | deadline 归零仍启动 taskkill | **闭合。** `run_taskkill_bounded` 在 `timeout.is_zero()` 时立即返回，位于 `Command::new("taskkill").spawn()` 之前：`:2354-2364`。非零 timeout 的同步 `Command::spawn()` 仍不受该 timeout 截断，见第 3 节。 |
| 1d | fallback worker 循环受 deadline | **部分闭合。** 三个主循环分别受 `Instant::now() < deadline` 约束：inner `:4325-4350`、pending `:2571-2604`、child `:2795-2833`。但 child worker 离开循环后无条件执行 `child.kill()` 与 `try_wait()`：`:2834-2838`，可能在原 deadline 后工作；`child-reap-fallback` 也没有 deadline 已归零时禁止同步 spawn 的前置分支（`:2791-2794`）。 |
| 1e | taskkill/reader/writer reaper 有界且不泄漏 | **未闭合。** taskkill reaper 在 `:2407-2419` 轮询 200 ms，但每轮 `sleep(15ms)` 未按 remaining 截断，且启动前 `child.kill()` 忽略错误（`:2403`）；其存活可能超过声明的 200 ms，kill 失败时不能证明 taskkill 子进程退出。reader/writer reaper（`:2913-2930,2980-2997`）在 200 ms 后只记录错误并丢弃原 worker 的 `JoinHandle`；若原 reader 卡在 `read_line` 或 writer 卡在管道写入，原线程仍可无限存活。两个 reaper 的 sleep 未截断，超时后还各有最多 20 ms 错误锁等待（`:2923-2929,2990-2996`）。另外，shutdown 路径仍有 6 个条件式 `JoinHandle::join()`：`:2893,2907,2919,2960,2974,2986`；finished flag 在 worker 真正返回前设置（reader `:1421,1440`，writer `:1469`），因此不能推出 `join()` 有界。`try_wait` 是状态轮询，但 200 ms 只限定 reaper 的意图轮询窗，不能给 OS 调用和调度延迟建立硬墙钟上界；更关键的是，reader/writer reaper 到期后原 worker 仍可能卡在 I/O，故 reaper 自身有界不等于线程无泄漏。 |
| 1f | `child_reaped` 仅在确认回收后置位 | **闭合。** 所有 store 点经逐项核对：重入路径 `:2452` 仅在 `wait_timeout_or_kill_with_reap` 成功后，`:2476,2502` 仅在 `Ok(Some(_))`；主路径 `:2671` 同样只在该 helper 成功后，`:2703,2729` 仅在 `Ok(Some(_))`；fallback `:2808,2837` 也只在 `Ok(Some(_))`。helper 成功返回的路径来自 `try_wait` 得到退出状态。没有发现其他置位点。 |
| 1g | 22 项审计表及 WCET | **未闭合。** 审计确有 22 个编号行（`concurrency-lock-audit.md:23-44`），但不是源码中独立同步操作的一对一清单；第 16 行把 taskkill spawn、等待、读 stdout/stderr、kill 与 reaper spawn 合成一项，第 19/21 行也未给 `join()` 独立上界，第 22 行把多条 Drop/重入路径合为 0 ms。第 4 行声称 transaction lock 上限 80 ms（审计 `:26`），源码实际把 `session_timeout` 传给 `acquire_transaction_lock`（`library_bridge.rs:1694-1734,1784`），无独立 80 ms 上限。 |

## 3. 审计表与 WCET 复核

### 独立计数

审计表行数为 **22**，算术上可以逐项数清；但“22 个独立前台阻塞点”的源码映射不成立。我额外按源码逐点数出 **20 个被行级复合项掩盖的同步/可能阻塞操作位点**：

- 2 个 CAS deadline 注册循环：`:1506-1524`、`:3863-3881`。
- 6 个 shutdown 路径同步 `std::thread::Builder::spawn`：taskkill `:2404-2406`、pending `:2567-2569`、child `:2791-2794`、reader `:2913-2916`、writer `:2980-2983`、inner fallback `:4322-4325`。
- taskkill 自身 1 个同步 `Command::spawn`（`:2359-2364`）、2 个管道 `read_to_string`（`:2371-2378`）、3 个 `child.kill()` 位点（`:2300,2403,2835`）。
- 6 个独立 `join()` 位点：`:2893,2907,2919,2960,2974,2986`。

这些 20 个位点与审计的 22 个高层类别有交叠，故不能简单相加当成最终总数；它们说明“22”是表格行数，不是逐个阻塞操作的计数。另有 child fallback handle 保存锁 `:2863-2867`、pending 响应 `SyncSender::send`（`:2555-2558,2578-2583`）等也需要在分支矩阵中标出。审计应改为逐调用点清单，并明确前台等待、同步系统调用与后台生命周期的计数口径。

### WCET 算式

审计的主路径公式算术正确：

```text
50 + 30 + 30 + 240 + 60 + (50 + 1000 + 400 + 10 + 250 + 10)
    + (30 + 100) + (30 + 80) + 0
= 2370 ms
```

因此 **2370 ms ≤ 2400 ms**（距 3000 ms 为 630 ms）在列出的理想化阶段预算内成立；Task 正文仍保留 20 项/2340 ms/660 ms（`doc/tasks/P20-CLOSE-BOUND-1.md:37,91`），与本轮审计的 22 项/2370 ms 不一致。

但 2370 ms **不是全链路 WCET**。`Command::spawn` 在计时循环开始前同步发生（`:2359-2366`）；taskkill 成功后同步读两个输出流（`:2371-2378`）；`child.kill()`（`:2300,2403,2835`）及 6 次 `Builder::spawn` 均未分配预算。`join()` 仅靠一个先行 AtomicBool 决定是否调用，不能据此给 join 一个硬上限。审计仅如实说明了 OS 进程创建和系统调度限制（`concurrency-lock-audit.md:119-122`），没有覆盖线程创建、kill 和输出读取的同步边界。

**fallback/reaper 线程本身也没有进入 WCET。** `spawn()` 是调用线程的同步调用；reaper 在新线程实际开始后才设置 200 ms 计时起点，睡眠也可能越过该点，reader/writer reaper 的错误记录锁还延长其生命周期。线程的逻辑轮询窗口有限，不等于线程从前台派发到实际终止的硬上界。

## 4. AC2、AC5、AC6 与证据

### AC2：残留范围

`test-ac1-overlay-bound.ps1:206-262` 现在只筛 runner/本次启动命令的 PID 后代，或命令行命中唯一隔离根；已删全局进程名与工作区根路径匹配。因此另一个独立启动、命令行仅含工作区路径的 Python 测试**不会仅因其名称/工作区路径被误报**。这是按脚本筛选代码静态核验，本轮没有另起 Python 进程或重跑整套测试。AC5 脚本 `run-desktop-close-verification.ps1:148-174` 也将判定限于 app/sidecar PID 树与隔离根。

限制是断链后代：AC1 runner 的 BFS 从 runner 和所有 launched PIDs 开始（`:206-235`），但候选只接受 BFS 中的后代或隔离根命中（`:245-262`）；若中间 parent 已退出，且遗留进程命令行不含隔离根，就漏检。AC2 日志仍写“Broken-Chain Process Audit”及“无 unlinked descendant”（`ac2-process-tree-audit.log`），脚本实际不再做原先的全局 delta/工作区匹配；该日志措辞需收窄。R6 保存的该次日志仍记录 residual=0、exit=0，可证明本次受限扫描结果，不能证明任意断链进程均不存在。

### AC5：桌面运行及管道行为

脚本自己创建 OutDir，并显式 `exit $scriptExitCode`（`:15-27,200-255`）。不是任意管道调用都会导致退出码不一致；`ac5-20261018-1552` 的 console 明确显示 `WriteAllLines` 因 `ac5-console.log` 被占用而失败（`:208`），与 Coordinator 用 `Tee-Object` 同时写同一日志路径吻合。这是调用方对同一路径并发写入的冲突；显式 `exit` 已存在，且无法消除文件锁。

脚本仍有独立的证据写入健壮性缺口：`:208` 的未捕获日志写入异常发生在 `finally` 内，会中止后续 `ac5.exit` 与 metadata 写入（`:210-249`）；读回不匹配时也仅把 `$scriptExitCode` 置 1（`:216-218`），没有重写 `ac5.exit`。因此该错误路径无法保证 artifact 与真实 exit 一致。最小修法是隔离各 artifact 写入错误，保证 console 写入/读回失败时仍写出一致的退出码与 metadata，并增加锁定 console 文件的故障用例。

磁盘上的 direct run `ac5-20261018-1555` 有完整 console、metadata、`ac5.exit`，记录 exit=0、**129.3082 ms**、残留 0；metadata 的 `release_sha256=5f9170…` 与 release exe 及 Coordinator 声明的 R6 build SHA 一致，但 `head=e44a589a` 是 Review head `835f4bb17` 的父提交。另一个 `1552` console 记录 **294.2243 ms、残留 0**，但因上述 Tee 文件锁没有 exit/metadata。运行结果已有成功证据；AC5/AC6 的 exact-head 完整 OutDir 仍需 Coordinator 在交互式桌面直接重跑一次，使 metadata 记录 `835f4bb17`。不要让 Tee 写入同一 OutDir 日志。

### AC6：hash 与当前 Task pin

最初核对 Handoff 的 46 项时，有 **26 项 SHA 与磁盘不符**。按实际文件重算并更新后，复核为 **46/46 匹配**。Task 原 75 项 Canonical Evidence 指向早期 commit/hash；收口时保留原文为 Historical Evidence Pins，另建 R6 表，固定 delivery head `835f4bb17` 并 pin 当前源码、审计、脚本和可复核输出。治理检查负责验证新 pins 与 Resource Manifest。

AC6 **部分达成**：提交、R6 source/test pins 与 Handoff hashes 已校正；但 `1555` 成功 run metadata 的 `head=e44a589a`，`1552` 的 294.2243 ms run 缺 exit/metadata，当前仍无 metadata 精确记录 `835f4bb17` 的完整桌面 OutDir。
## 5. 新回归与已有证据

- R-008 心跳恢复、心跳失败限次、R-003 shutdown 拆环/reap、in-flight 关闭：`ac3-resilient-channel.stdout.log` 显示 **9 passed / 0 failed**，其中含 `resilient_channel_heartbeat_detects_unresponsive_child_and_recovers`、`resilient_channel_shutdown_breaks_cycle_and_reaps_child_process` 与 bounded drop 用例。
- `stdio_channel_drop`：**1 passed / 0 failed**；两条 `shutdown_writes` 用例 **2 passed / 0 failed**。对应源码断言外部写在 `is_down` 时拒绝、shutdown 专用写仍成功（测试 `library_bridge.rs:6642-6812`）；`MAX_RETRIES=3` 用例名与通过结果见 `:5911` 及上述 9 项日志。
- R6 新增的 fallback timeout、spawn failure、reentrant reap 检查均有对应 stdout/exit 证据，三项 `.exit=0`；当前 Close-Bound 目录根级 15 个 R6 套件 `.exit` 文件均为 0。Reviewer 本轮没有重跑测试。
- R-006 的前端实现不在该 diff 中，未见本提交改动其语义；本轮测试没有重新执行 R-006 UI 用例，沿用此前已接受的交互证据。

## 6. AC1–AC6 最终状态

| AC | 状态 | 依据 |
|---|---|---|
| AC1 | **部分** | R6 强杀 + 在途请求日志通过，实测 10.8919 ms；Drop/零预算等修正确认。但 CAS 无重试上界、`join()`/同步创建与读写未纳入 deadline，不能证明 2400 ms 全链路硬上界。 |
| AC2 | **部分** | 独立 workspace Python 不会因工作区路径/name 被误报；本次扫描 exit=0/residual=0。但不含隔离根的断链后代可漏检，日志仍错误宣称 broken-chain 全覆盖。 |
| AC3 | **达成** | 9 项 resilient + 1 项 stdio drop + 2 项 shutdown write 日志全绿；R-008、R-003、`MAX_RETRIES=3` 和 `is_down` 语义未见退化；R-006 前端未被该提交修改。 |
| AC4 | **未达成** | 22 行不是逐调用点；第 4 项 80 ms 与源码不符；后台 worker 可脱离生命周期、部分动作越过 deadline；2370 ms 算术正确但不是完整 WCET。 |
| AC5 | **部分** | Direct run 已以同 SHA release binary 证明 129.3082 ms、残留 0、exit 0；但读回失败分支不重写 `ac5.exit`，日志写入异常会中断后续 artifacts，成功 run metadata head 是 e44。 |
| AC6 | **部分** | Task 已指向 835f，当前 Canonical Evidence 与 46 项 Handoff SHA 已校正；缺少 metadata 明确指向 835f 的完整 direct-run OutDir。 |
## 7. 收口 disposition、未闭合清单与后续 Task

以下是当前交接项；前两项是阻止 `approved` 的 P1。**本轮按用户指示将本 Task 以 `closed_with_limitations` 处理**，保留其未达成 AC 原始状态，不将它们记为技术通过。

| ID / 级别 | 未闭合点与精确位置 | 最小可接手修法 | P20 Gate 影响 |
|---|---|---|---|
| CBH-01 / P1 | deadline 后 child fallback 仍 `kill/try_wait`（`:2834-2838`）；reader/writer reaper 超时后 detach 仍可能阻塞的原 worker（`:2925-2930,2992-2997`）；六处条件式 `join()`（`:2893,2907,2919,2960,2974,2986`）；taskkill reaper kill 错误忽略且轮询可越过 200 ms（`:2403-2419`）。 | 禁止 deadline 后任何清理动作；把 sleep 与错误记录纳入 reaper 截止；用可取消的 pipe I/O/句柄关闭确保原 worker 实际结束，或显式定义并监控可接受的 detach 行为；仅对已完全结束的 thread join。新增永久阻塞 reader/writer 和 kill 失败注入测试。 | 不改变 P20 AC7 打包/hash/四页事实；P20 的“强杀关闭有界、零残留”可靠性子 Gate 未满足时不得宣称全项通过。 |
| CBH-02 / P1 | CAS retry 无硬上界（`:1506-1524,3863-3881`）；同步 `Command::spawn`、输出读、kill、六次 `Builder::spawn` 及额外 `join` 未纳入 WCET（`:2300,2359-2424,2567-2569,2791-2867,2881-3010,4322-4350`）；审计表 `:26,44,52-70`。 | 给 deadline 更新建立可证明的重试/单调性边界并正确编码 zero/expired；逐 callsite 计时；预建/复用关闭 worker 或把系统调用边界明确写为无法纳入的限制，重算 WCET，禁止继续引用 2370 ms 为全路径 WCET。 | 同 CBH-01；P20 AC7 本身不受影响，close-bound 子 Gate 仍保留限制。 |
| CBH-03 / P2 | AC2 断链进程覆盖/措辞：`test-ac1-overlay-bound.ps1:226-262,273-280`。 | 在用户接受的范围内明确只证明 runner 后代+隔离根，去掉 broken-chain 全覆盖措辞；若需全树保证，则维护进程句柄/Job Object 或等价追踪并增加断链测试。 | P20 AC7 无影响；AC2 close-bound 证据限定为当前扫描范围。 |
| CBH-04 / P2 | exact-head 运行证据：`ac5-20261018-1555/ac5-metadata.json` 记 `head=e44a589a`；`ac5-20261018-1552/ac5-console.log` 记 294.2243 ms，但因文件锁缺 exit/metadata。 | Coordinator 在交互式桌面直跑一次，生成完整 OutDir，metadata 标 `835f4bb17`，确认 binary SHA、`ac5.exit` 与真实进程 exit 一致。 | 不影响 P20 AC7 构建产物；close-bound AC5/AC6 evidence pin 未完整前保留 limitation。 |
| CBH-05 / P2 | AC5 artifact 写入失败控制流：脚本 `run-desktop-close-verification.ps1:208-249`；读回不一致分支 `:216-218`。Tee 锁同一日志路径使 1552 run 无 exit/meta。 | 分离 console/exit/metadata 错误处理；artifact 写入失败时仍生成一致 `ac5.exit`、metadata 与宿主退出码，并增加日志文件锁定故障用例。 | 不影响 P20 AC7 构建产物；AC5 evidence 生成可靠性保留限制。 |

建议的后续 Task：

- **Task**：`P20-CLOSE-BOUND-HARDEN-1`，shutdown deadline 与 worker 生命周期加固；依赖本 Task 的 limitation 记录，作为 `proposed` 任务等待 Codex 完成 DAG/STATUS 注册后释放。
- **Agent**：Owner=`Antigravity`，Reviewer=`Codex`。不分配给 Qoder。
- **Recovery point**：仓库 `G:/CODEX/New Manga`，`base_commit=835f4bb17df565581a76cf66062760cdd3c85a9e`，当前 `head` 同此；新 linked worktree（如需）待 Codex 在相邻 `G:/CODEX/New Manga.workspace/` 创建。
- **Scope**：允许修改 `apps/desktop/src-tauri/src/library_bridge.rs`、本 Task 自身的测试与 `verification/P20-CLOSE-BOUND-1/**`、新 Task/Handoff；禁止扩大产品行为或修改共享契约、Schema、依赖、P09 在制品与无关文档。
- **Deliverables / Verification**：逐 callsite shutdown audit 与正确 WCET；CAS/zero deadline、永久阻塞 pipe worker、taskkill spawn/kill/reap 失败及 fallback deadline 用例；AC2 脚本声明/范围校正；AC5 exact-head 输出与 SHA pins；回归 resilient 9 项、stdio drop、shutdown writes、2 MB pipe overflow；交付固定 commit、Handoff 与完整 stdout/stderr/exit/metadata。NOT_RUN/BLOCKED 项逐项保留，不得记 PASS。

**可直接转发给 Owner 的指令：**

> 执行 `P20-CLOSE-BOUND-HARDEN-1`。基线和当前 head 均为 `835f4bb17df565581a76cf66062760cdd3c85a9e`，工作路径 `G:/CODEX/New Manga`（新 worktree 如需由 Codex 放在相邻 `G:/CODEX/New Manga.workspace/` 创建）。只修改 shutdown 相关 Rust 源码/测试、`verification/P20-CLOSE-BOUND-1/**`、该 Task/Handoff；不得碰 P09 在制品、共享契约/Schema/依赖或扩大产品行为。逐调用点证明 deadline、处理零/过期 deadline 和 CAS 竞争；保证 fallback/reaper 不在 deadline 后继续动作，永久阻塞 reader/writer 不被静默 detach，所有 join/thread spawn/taskkill spawn/read/kill 的界限诚实进入 WCET。补故障注入覆盖 kill/spawn/reap 失败与阻塞 I/O，并复跑 resilient 9、stdio drop、shutdown writes、2 MB pipe overflow；覆盖 AC5 artifact 写入失败与锁定 console 文件。修正 AC2 的覆盖声明，保存并 SHA-256 pin 针对交付 head 的 AC5 交互式桌面产物。提交固定 commit、完整日志/退出码/metadata 和 Handoff；逐项报告 PASS/FAIL/NOT_RUN/BLOCKED 后请求 Codex 独立 Review。

