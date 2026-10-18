---
task_id: P20-CLOSE-BOUND-1
reviewer: Codex
owner: Antigravity
base_commit: d4e3b3eb96c036f67da28909a485dab354b1dbe4
reviewed_head: 41bb13679615af557478b85ad6e0bd217f221666
decision: changes_requested
---

# P20-CLOSE-BOUND-1 独立 Review R4

**复核方式**：只读检查当前 HEAD `41bb13679`。比较范围 `d4e3b3eb9..41bb13679`，覆盖 R3 后的修复与证据；按用户指示排除 P09 DELETE 命令/Schema/ACL 的产品行为，只检查 CLOSE-BOUND 关闭路径。未运行 `cargo build` 或项目测试；核查了现有测试日志、源码断言和脚本。另运行只读 `tools/governance/check.ps1`，结果见本文末。

## 1. 结论

**decision = `changes_requested`。** R4 解决了部分原始缺陷，但 AC1/AC4 的 2400 ms 全链路硬上界仍未成立：`run_taskkill_bounded` 的超时回收仍同步 `wait()`，关闭请求中存在不受剩余预算截断的锁等待，`Drop` 和 inner fallback 会重新开预算；WCET 清单既未覆盖这些路径，标称的 16 项实际列出 19 项。N1、P1#2、P1#3 仍有实质缺口；AC2/AC6 的声明也超过现有证据。

## 2. 逐项闭合确认

| 项目 | R4 复核 | 证据与未闭合点 |
|---|---|---|
| **N1** | **部分闭合** | `shutdown` 在 `ctx.inner` 超时后会告警并派发专用线程；测试确实断言了调用方有界返回、完成标记以及 PID 消失（`library_bridge.rs:6532-6592`，现有日志记 1 passed）。但 fallback 预算用 `max(2000ms, remaining)`，最多可在原 deadline 后继续等待；成功取得锁后又调用 `shutdown_and_kill(1500ms)` 另开预算，并在该调用返回前一直持有 `ctx.inner` guard（`:3819-3837`）。等待超时会报错后退出，Core 仍可能留在 `inner`；线程 spawn 的 `Err` 被忽略（`:3821`）。测试只覆盖持锁 200 ms 的成功分支，没有覆盖超时或 spawn 失败。 |
| **P1#2** | **部分闭合** | child 改为 `Arc<Mutex<Child>>`；争锁 fallback 确实调用 `child.wait()`，且仅在 `wait()` 返回 `Ok` 后置位 `child_reaped`（`:2514-2550`）。pending fallback 也在实际 drain 后置位 `pending_drained`（`:2387-2405`）。测试有直接断言，child 测试派生孙进程并分别检查 parent/grandchild PID（`:6364-6388`），pending 测试检查通知和 `pending_drained`（`:6422-6435`）。但 reaper 的 `child.wait()` 无超时，taskkill 失败时会让后台线程无限等待（`:2527`）；取锁最多 2.5 s 后放弃（`:2524-2549`），spawn 失败被 `.ok()` 静默吞掉（`:2519-2554`）。pending fallback 两秒后放弃 drain，spawn 失败也未报告（`:2382-2407`）。此外正常 wait 失败后，只凭 taskkill 返回 `Ok` 就将 `child_reaped=true`，没有对 Rust `Child` 调用 `wait()`（`:2475-2479`），该标记不等于真实回收。生产 taskkill 走 `/F /T /PID` helper；测试专用外部强杀仍直接使用 `/F /PID`（`:5945-5948`），不属于生产 fallback。 |
| **P1#3** | **未闭合** | 入口建立 deadline 并传给正常通道关闭分支（`:3798-3813`），但下文 WCET 专项列出未纳入的阻塞与重置预算路径。 |
| **P2#5** | **部分闭合** | 增加基线 PID 差集、runner BFS 和路径/进程名筛选（`test-ac1-overlay-bound.ps1:28-35,188-249`），隔离目录删除失败会导致非零退出（`:287-327`）。差集并未递归追踪所有新 PID，只按已知名称和命令行路径特征过滤；不带这些特征的断链 helper 仍可漏检。当前日志记录 `Delta Processes Evaluated: 0`、`Recursive Descendant PIDs Scanned: 0`，该次没有验证断链后代判别路径。成功删除隔离目录证明目录可删，不等价于证明所有进程句柄均已释放。 |
| **P2#6** | **已闭合（测试覆盖范围内）** | writer 在显式 drop `ChildStdin` 后设置 `writer_finished`（`library_bridge.rs:1465-1467`）；满管道测试直接断言 writer/reader finished、writer/reader joined（`:6512-6516`），不是日志打印或 slot 为 None 的替代断言。现有日志记该测试通过。 |
| **P2#7** | **部分闭合** | helper 采集 exit status 和输出，主关闭分支检查错误并记录（`:2276-2307,2472-2511`）。但重入分支两处 `if let Ok(_)` 仍静默吞 taskkill 失败（`:2350,2357`）；helper 将非零但匹配“not found/not running”的结果作为 `Ok`，调用方随后可能错误置位回收标记（`:2302-2305,2475-2479`）。 |
| **AC5 流程修正** | **脚本自包含落盘已实现；失败状态传播有新缺口** | 脚本创建 `$OutDir`，`finally` 写 `ac5-console.log`、metadata txt/json 和 `ac5.exit`（`run-desktop-close-verification.ps1:13-27,187-234`），不依赖调用方 Tee。失败分支的 `return`（`:84,149,175`）会在 finally 后直接返回，跳过底部 `exit $scriptExitCode`（`:234`）；一次 PowerShell 控制流探针确认此类 `return` 可让宿主进程仍以 exit 0 结束。因此 `ac5.exit` 可记录 1，但依赖 PowerShell 进程退出码的调用方可能误判成功。 |

**测试断言边界**：`tasklist` 的 PID 缺失断言是真实断言；不过 child/grandchild 检查只对 `.output().expect(...)`，未断言 `tasklist` 自身 `status.success()`（`:6371-6388`）。证据因而依赖该查询成功执行。P2#6 的资源释放断言不受此限制。

## 3. WCET 16 项阻塞点核对

### 清单与算术

`concurrency-lock-audit.md:35-57` 声称列出 **16 项**，按表格实际计数是 **19 行**：Step 0、1 各 1 项，Step 2a–2e 共 5 项，Step 3 为 1 项，Step 4a–4f 共 6 项，Step 5a–5b 与 Step 6a–6b 共 4 项，Step 7 为 1 项。

表内闭式加法本身正确：`50 + 30 + 250 + 60 + 1720 + 130 + 110 = 2350 ms`，替代分支 `960 ms` 也按其列项算术成立。但它只是所列上限的和，不能证明实现 WCET，因为存在未列阻塞点和分支重置预算。Step 7 写 `0 ms`，而实际重入分支可执行 150 ms child-lock wait、最多 150 ms graceful wait、100 ms reap、100 ms taskkill；该分支不在 2350 ms 加和中（`library_bridge.rs:2334-2360`）。

与 R3 声称的 2120 ms 相比，R4 声称增加 230 ms；R3 原公式实际为 2070 ms（R3 Review 已指出 50 ms 算术偏差）。按 R3 原列项到 R4 列项，R4 增加 pending 清理锁 10 ms、两处错误记录锁 20 ms、taskkill 250 ms，合计增加 280 ms，得到 2350 ms。该差异可由新增列项解释，但不能补足未列路径。

### `min(自身上限, remaining)` 核对

- 逐行核对并不是 16 行，而是表内实际 19 行：

| 审计表行 | 实际控制 | 判定 |
|---|---|---|
| Step 0 `ctx.inner` | 主路径 `min(50ms, rem)`（`:3803-3807`）；超时 worker 不共用此 deadline | 主路径 PASS；fallback FAIL |
| Step 1 pending 主锁 | `min(30ms, rem)`（`:2366-2369`）；worker 独立重试至 2 s（`:2387-2407`） | 主路径 PASS；worker 不在共享 deadline 内 |
| Step 2a `host_session` | `min(30ms, rem)`（`:2412-2418`） | PASS |
| Step 2b `transaction_lock` | 调用方传 `min(240ms, rem)` 的 session timeout；锁自身按该局部 timeout 轮询（`:2416-2432,1660-1695`） | PARTIAL：后续 pending 注册锁不取其 remaining |
| Step 2c CloseHostSession 写入 | 写入 timeout 按请求局部 remaining；writer 回执 `recv_timeout`（`:1770-1787`） | PARTIAL：局部预算可受 100 ms pending 锁等待挤出 |
| Step 2d CloseHostSession 响应 | `rx.recv_timeout` 用请求局部 remaining（`:1806-1815`） | PARTIAL：超时后的清理锁另加固定 10 ms |
| Step 2e pending 清理锁 | 固定 `10ms`，未与 shutdown deadline 取 min（`:1774-1777,1791-1794,1818-1821`） | FAIL |
| Step 3 `core.shutdown` 写入 | `min(60ms, rem)`（`:2437-2450`） | PASS |
| Step 4a child 锁 | `min(50ms, rem)`（`:2453-2456`） | PASS |
| Step 4b graceful wait | 最多 1000 ms，并留出 450 ms/受剩余量截断（`:2457-2459`） | PASS（主路径） |
| Step 4c reap wait | 最多 400 ms/受剩余量截断；轮询 sleep 截断（`:2460-2462,2242-2256`） | PASS（主路径） |
| Step 4d wait 错误记录锁 | 固定 `10ms`（`:2466-2471`） | FAIL |
| Step 4e taskkill | 外层传 `min(250ms, rem)`，但 helper 之后有同步读取与无界 wait（`:2472-2475,2288-2323`） | FAIL |
| Step 4f taskkill 错误记录锁 | 固定 `10ms`（`:2480-2484`） | FAIL |
| Step 5a reader handle 锁 | `min(30ms, rem)`（`:2557-2561`） | PASS |
| Step 5b reader join 等待 | 调用线程 `recv_timeout(min(100ms, rem))`（`:2562-2575`）；后台线程自身 `handle.join()` 无上限 | 调用线程 PASS；后台 join 未界定 |
| Step 6a writer handle 锁 | `min(30ms, rem)`（`:2579-2583`） | PASS |
| Step 6b writer join 等待 | 调用线程 `recv_timeout(min(80ms, rem))`（`:2584-2599`）；后台线程自身 `handle.join()` 无上限 | 调用线程 PASS；后台 join 未界定 |
| Step 7 重入关闭 | 表列 0 ms；实际重入可做 150 ms lock + 150 ms graceful + 100 ms reap + 100 ms taskkill（`:2334-2360`） | FAIL；未纳入 2350 ms |

- **未列入这 19 行的阻塞点**：CloseHostSession 注册 pending 槽固定等 100 ms（`:1763-1767`）；inner fallback 的独立重试/新关闭预算（`:3819-3837`）；child reaper 的无界 `child.wait()`（`:2527`）；`Drop` 再开预算（`:2604-2606,2327-2330`）。错误记录锁虽然有自设 10 ms 上限，也未按共享 remaining 截断。
- `run_taskkill_bounded` 的轮询 sleep 按自身 timeout 截断，但整个操作并未有界：进程退出后 stdout/stderr 同步 `read_to_string`（`:2288-2296`），超时则同步 `child.kill()` 后无期限 `child.wait()`（`:2321-2323`）。即使传入 0 ms，仍先 spawn taskkill，再进入 kill/wait。`min(250ms, remaining)` 不能限制这些同步等待。
- `StdioLibraryChannel::drop` 会再调用 `shutdown_and_kill(2400ms)`，后者每次重新建立 deadline（`:2604-2606,2327-2330`）；inner fallback 也在原 deadline 外等待，并以新的 1500 ms 预算关闭（`:3819-3830`）。

据此，2350 ms 静态数值与 2400 ms 动态 deadline 目前均不是实现保证；AC1/AC4 不能验收。不能把轮询 sleep 截断等同于对上述同步锁、管道读取、子进程 wait 和重入调用的全链路截断。

## 4. N1 fallback 是否引入新的无界路径

inner fallback 的锁重试窗口有时限（`max(2000ms, remaining)`，最大不超过约 2400 ms），锁始终拿不到时会打印 Error 后退出，所以这个锁轮询本身不是无限循环。但它不是原 deadline 的一部分；取得锁后又单独关闭最多 1500 ms，并且 `ctx.inner` guard 覆盖关闭过程。除此之外，它的线程创建失败被忽略。独立的 `child-reap-fallback` 则在取得锁后直接 `child.wait()`，没有超时；taskkill 失败时确实可形成新的无界后台等待。因此 N1 的常见 200 ms 锁竞争测试有真实杀进程证据，但 N1/P1#2 的回收失败路径没有形成“有界且可观察”的闭环。

## 5. 新发现

1. **P2：AC5 失败时 PowerShell 进程退出码可能仍为 0。** `return` 路径会跳过脚本尾部的 `exit $scriptExitCode`；metadata/`ac5.exit` 记录错误码不修复调用方读取的进程退出码。建议失败路径使用共同收尾出口，确保落盘和进程退出码一致。
2. **P2：PID 审计的断链覆盖声明过强。** 脚本扫描的是“新增 PID 且命令行/名称命中特征”的候选，不是全部新进程或任意断链后代；本轮 audit 的两个扫描计数都是 0。建议把 AC2 结论限定为已知进程名/路径特征覆盖，或加入能判别未知断链后代的故障注入。
3. **AC6 证据 pin 仍不一致。** Task `delivery_head` 仍为 `fdf715e79`；Canonical Evidence 中 source 和多份 R4 日志仍指向 `fdf715e79`，新 AC2/inner-lock 产物则标 `pending`（`doc/tasks/P20-CLOSE-BOUND-1.md:17,92-148`）。source 行 SHA-256 与当前文件相同，但 `fdf715e79` 中该路径 Git blob 为 `9a2d2a2…`，当前 HEAD blob 为 `376c780…`，前者不包含 R4 实现。`ac4-inner-lock-contention.meta.json` 也没有 `HEAD`/源文件 hash，无法自行把 14:11 的运行绑定到之后提交的实现。故 AC6 的“complete/全量对齐”不成立；Coordinator 已修 N2 的声明与当前 Task 表不符。

## 6. 越界与提交组织问题

- 按用户明确指示，`d9f7a628c` 中 P09 DELETE 命令、Schema v5、ACL 和相关测试不作为 P20 CLOSE-BOUND 越界问题，也未审查其产品行为。已通过 `git blame` 确认关闭路径 helper `run_taskkill_bounded`（`library_bridge.rs:2273-2323`）由 `d9f7a628c` 引入；该提交标题属于 P09，且与 P09 改动混在同一 `library_bridge.rs` 提交中。必须按用户要求继续审查这部分关闭路径，不能因 commit message 排除。
- **Coordinator 已承认误提交用户 23 个未提交生成文件**，路径范围为 `gen/schemas/**` 与 `permissions/autogenerated/**`。这违反用户文件归属与 Task `:55` 的“不动用户未提交改动”边界，责任记录为 Coordinator 的提交/集成失误，不归责 Antigravity 的关闭实现。当前 `41bb13679` 可见的生成路径差异为 4 个 schema 文件及 2 个新增 ACL 文件；当前树无法还原提交前 23 个文件的完整清单，需 Coordinator 另行对照原始工作区清单登记，不得据此清理/回滚用户内容。
- 工作区原本存在大量 tracked dirty 与 untracked 文件；本 Review 未修改/清理它们，也未改产品代码。仅按请求新增本 Review 文件。
- `doc/STATUS.md` 仍记录 P20-CLOSE-BOUND-1 为“授权第 3 轮”，与用户本轮明确授权第 4/5 轮不一致。此次复审遵循用户直接授权；后续由 Coordinator 修正权威指针/状态记录。

## Standards

**1 项文档标准硬问题**：`doc/09_COLLABORATION.md:80-84`（§4.1）要求 Canonical Evidence 记录“含该文件的 commit”。Task `:17,92-148` 多项仍 pin 到不含 R4 源码/新日志的 `fdf715e79`，另有 `pending` pin，却宣称 evidence complete，违反证据引用规范。

**判断型 smell**：存在轻微 possible Duplicated Code，错误记录与 taskkill 状态处理分散在多个关闭分支（`library_bridge.rs:2469-2511`）；不是本次阻塞原因。其余 Fowler smell baseline 未发现需要单列的问题。

## 7. AC1–AC6 与 P20 收口影响

| AC | R4 结论 |
|---|---|
| **AC1** | **未达成**：WCET 表漏掉不受 deadline 控制的同步 wait/read、锁清理、Drop 重入与 inner fallback 新预算；现有 0.5443 ms 日志只是一种测试情形，不证明硬上界。 |
| **AC2** | **部分达成**：当前日志记残留数为 0、隔离目录删除成功；差集/路径扫描已增加，但不能证明任意断链后代为零，本次扫描计数也为 0。 |
| **AC3** | **未见源码回归，但未由 Reviewer 重跑**：close-bound diff 未改心跳/拆环/错误呈现语义；现有日志记录 `resilient_channel` 9 项、`stdio_channel_drop` 1 项通过，仍是历史运行证据。`write_stdin_timeout` 继续按 `is_down` 拒绝外部请求，只有专用 `write_stdin_shutdown` 绕过该检查；既有测试有拒绝断言（`:1584-1593,6194-6200,6279-6285`）。阈值未见放宽。 |
| **AC4** | **未达成**：测试断言改实，child/pending 典型争锁路径通过日志记录；但回收 fallback 仍可能无限 wait，taskkill 重入失败仍静默，16/19 清单不完整且 WCET 不是全链路证明。 |
| **AC5** | **代码流程修正部分达成**：脚本现有自包含 OutDir、console log、metadata 和 `ac5.exit`。当前目录的桌面交互证据仍是 R3 代码运行，不能代表 R4；需 Coordinator 使用当前 R4 release 在真实交互桌面复跑，并核验 PowerShell 进程码与 `ac5.exit` 一致。 |
| **AC6** | **未达成**：多条 commit pin 仍是 `fdf715e79`，新产物有 `pending` pin，source hash 与 commit 内容不对应；当前 evidence complete 声明应撤回/修正。 |

**P20 收口影响**：Task 保持 `in_review`，不批准集成或标记 `done/closed`。用户已授权第 5 轮，可由 Antigravity 按 P1#2/P1#3/N1、P2#5/P2#7、AC5 退出码与 AC6 pins 修复；Coordinator 随后修订指针并在交互式桌面复跑 AC5。AC3 无需扩大改动范围。

## Spec

**`changes_requested`。** 对照 Task `:37-42,52-59`：AC1/AC4 的上界和回收条件不完整（`library_bridge.rs:1765,1774-1794,1818,2276-2323,2475-2479,2527,2604-2606,3819-3837`）；AC2 的“全方位断链后代”声明没有被候选路径过滤器证明（脚本 `:209-249`）；AC6 pins 仍旧或 pending（Task `:92-148`）；AC5 虽新增自包含写盘，但失败进程码可错报成功（脚本 `:84,149,175,234`）。P09 DELETE/Schema/ACL 产品行为按用户说明排除，不列为本 Task scope creep。

## Verification 记录

| 检查 | 结果 |
|---|---|
| 固定 head | PASS：`HEAD=41bb13679615af557478b85ad6e0bd217f221666` |
| 关闭路径静态审阅 | 完成；未改产品代码 |
| 已提交日志 | AC1 0.5443 ms；inner lock fallback 1 passed；证据均未由本 Reviewer 重跑 |
| `cargo build` / cargo tests | NOT_RUN（按用户约束/只读复核） |
| `pwsh -NoProfile -File tools/governance/check.ps1` | PASS（2 warnings）；检查器报告当前 Task 为 `doc/tasks/P20.md`，`STATUS.md` / `REBASELINE_PLAN.md` 达到 80% 文档预算 |

**轴线汇总**：Standards 有 1 项文档标准硬问题、1 项轻微判断型 smell；Spec 有 4 组未满足/部分满足要求（AC1/AC4、AC2、AC5 失败退出码、AC6 证据 pins），其中 AC1/AC4 含阻塞性 P1。
