---
task_id: GIT-CLEAN-RUST-CAPACITY-DESIGN-1
reviewer: 子 agent design-reviewer
reviewer_kind: subagent
author: ZCode（DESIGN.md）/ DSH（集成）
base_commit: 1829a38a41587a0d680001a40d206886afb0911d
reviewed_head: 1829a38a41587a0d680001a40d206886afb0911d
design_artifact_commit: 3ca77fc10cccdb17bd5addb75374f4072a06c800
review_time: 2026-11-17T03:10:18+08:00
decision: blocked
---

# 独立复核：GIT-CLEAN-RUST-CAPACITY-DESIGN-1

- **复核者**：子 agent `design-reviewer`（独立上下文；未参与该设计、实现或返修；来源：DSH `lead` 派发的 `subagent`）。
- **被复核文档**：`verification/GIT-CLEAN-RUST-CAPACITY-DESIGN-1/DESIGN.md`（载于主仓 commit `3ca77fc10cccdb17bd5addb75374f4072a06c800`）。
- **代码基准**：`1829a38a41587a0d680001a40d206886afb0911d`（隔离仓 `G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-ISOLATION-1/source-r2`，`git status --porcelain` 为空）。
- **复核时间**：2026-11-17T03:10:18+08:00。
- **只读声明**：本次复核未修改任何文件（唯一写入为本报告）、未 commit/push/集成/清理、未运行 Rust、真实 Core 或压力测试。代码事实全部用 `git -C <isolated> show 1829a38:<path>` 读取；`[实测]` 数字仅引用 R2 Review 已记录的运行事实，本次不重跑。

## 结论

**verdict: BLOCKED**

一句话理由：文档对 `1829a38` 的主要行号/符号核对应属准确，但 **AC1 的 “唯一 track 入口” 与代码不符（漏掉 4004/4139 两条 reaper-spawn-failure 路径）**，**R2-F04 在 `multichannel_stress_tests.rs:797` 引用了不存在的 `threads_spawned/threads_joined` 变量**，**AC2-L1 的 B 进程没有 PID 发现通路，`taskkill /F /PID` 清理不可执行**，**R2-F03 的“正常路径结尾断言”按字面会先于 guard drop 执行而是恒真**；四项 P1 未闭合，不能按“可释放完整设计切片”定案。

- **P1：4 项**（P1-1..P1-4）。
- **P2：6 项**（P2-1..P2-6，不阻断但应在移交实施前修订）。

## 基准与核查方法

```powershell
$p = "G:\CODEX\New Manga.workspace\task-envs\GIT-CLEAN-RUST-ISOLATION-1\source-r2"
git -C $p rev-parse HEAD
# 1829a38a41587a0d680001a40d206886afb0911d
git -C $p status --porcelain | Measure-Object -Line
# Lines: 0
Get-FileHash -Algorithm SHA256 "$p\apps\desktop\src-tauri\src\library_bridge.rs"
Get-FileHash -Algorithm SHA256 "$p\apps\desktop\src-tauri\src\multichannel_stress_tests.rs"
Get-FileHash -Algorithm SHA256 "$p\apps\desktop\src-tauri\src\main.rs"
```

| 文件 | 本次 SHA256 | 文档/ R2 Review 记录 | 结果 |
|---|---|---|---|
| `library_bridge.rs` | `145a6a2af589c9eafc3b1f59ea276389965318802f087a13dba549398dc6c03a` | `145a6a2a…` | PASS |
| `multichannel_stress_tests.rs` | `dd2dfeaaae38424570c6efeb6c3b6c3f3bd630997f833a5f4b86e2ce0189ee8f` | `dd2dfeaa…` | PASS |
| `main.rs` | `b315e632e51befc7311ddb58fb513d6e6f400f9e84d1d0737d0a0e74404764cd` | `b315e632…` | PASS |

说明：`1829a38` 不在主仓对象库；主仓 `git rev-parse HEAD` 为 `3ca77fc`，`DESIGN.md` 由该 commit 引入。所有代码行号均以隔离仓 `1829a38` 的三文件为准。

## AC1 事实性

| # | 核查点 | 结果 | 证据与关键输出 |
|---|---|---|---|
| A1 | 基准 commit、工作树清洁、三文件哈希 | **PASS** | 见上表；`rev-parse HEAD`=`1829a38…`；`status --porcelain` 0 行。 |
| A2 | `adopt_child`、真实 pipe、`raw_stdin_handle`/`raw_stdout_handle` | **PASS** | `2106: fn adopt_child`；`2146: let raw_stdout_handle = …`；`2149: let raw_stdin_handle = …`；`2103: Self::adopt_child(child)`；`2108-2113` 从 `child.stdin/stdout` 取 raw handle。 |
| A3 | reader/writer 线程与退出分支 | **PASS** | `2156: .name("stdio-library-reader")`；`2223: match reader.read_line(&mut line)`；`2224-2237: Ok(0) → is_down / drain pending / on_down / break`；`2242-2255: Err → 同样 drain/on_down/break`；`2264: .name("stdio-library-writer")`；`2332: stdin.write_all(&bytes).and_then(flush)`；`2335-2337: if is_err { break; }`。 |
| A4 | 清理钩子、Drop 默认 2400ms、kill/join/reaper/track 行号 | **PASS** | `1339-1343: ThreadFinishedGuard::drop`；`2160-2178/2268-2286: Reader/WriterHandleCleaner`；`3427: shutdown_and_kill_with_deadline`；`4171-4202: impl Drop`；`4176: 2400ms`；`3658-3693: kill/graceful/reap`；`3895-4027: reader join 100ms`；`4029-4162: writer join 80ms`；`3932/4067: reader/writer-join-bounded-reaper`；`3980/4115: 200ms 后 track`；`4167/4200: reap(50ms)/reap(20ms)`。文档的 1.3 时序表与代码一致。 |
| A5 | “20 真实 pipe、峰 0”是否有代码/实测支撑 | **PASS（限定为测试场景）** | `multichannel_stress_tests.rs:652-657`：`for idx in 0..20` 生成 fault 场景 20 channel；`712: 4MB pad`；`729-730: writer_unfinished/reader_unfinished`；`753-770: Drop 串行`；`819-822: peak>=32`；`823-826: remaining==0`；`827-830: 120s`。`1829a38` 的 real-core 矩阵为 1/8/20；**代码没有生产 channel 上限 20**。R2 Review（source pin `.../r2/dsh-review-r2.md` 第 44/85/97/133 行）记录 20/20 `stdin write timed out`、`peak_registry=0`、exit101。 |
| A6 | “到 32 需要的故障前提”与 track 分支是否完整 | **FAIL（P1-1）** | 文档 1.5 只列 F1–F4，并在 1.3 写“唯一 track 入口 (3980/4115)”。但 `git -C $p grep -n "track_unreaped_worker(" 1829a38 -- apps/desktop/src-tauri/src` 还返回 **4004/4139**：`if let Err(e) = spawn_res`（reader/writer reaper 线程 spawn 失败）时直接 `track_unreaped_worker(...)`。这两条不需要“worker 熬过 200ms cancel”，而是 reaper 线程创建失败即进入 track；文档的“唯一反证窗口 F1+cancel 无效”不成立，需补 F5（或证明不可达）。 |
| A7 | F1 机制、`CancelSynchronousIo`、`DuplicateHandle` | **PARTIAL** | `2316: DUPLICATE_SAME_ACCESS`；`2320: writer_thread_handle.store`；`2268-2286: Cleaner 仅线程退出清零`；`1550-1568: cancel_worker_io`；`1553-1560: sync cancel 路径`。F1 的代码前提成立；但 1.5 的“单独不够”依赖 `CancelSynchronousIo` 对阻塞 WriteFile 有效，属 OS 行为推断（[推断]，非本 head 实测）。 |
| A8 | `spawn_with_startup_ping` / `adopt_child_for_test` 调用点 | **PASS** | `multichannel_stress_tests.rs:299-307: spawn_with_startup_ping`；`368: adopt_child_for_test`；`library_bridge.rs:3211: adopt_child_for_test`。 |

### AC1 关键判断

- **“20 真实 pipe、峰 0”本身有代码 + R2 实测支撑，但它是冻结测试场景的上限，不是生产 channel 上限。** 文档 1.4 已把 `MAX_UNREAPED_WORKERS=32` 与 channel 数区分开（`1606: const MAX_UNREAPED_WORKERS: usize = 32`），方向正确；建议在 1.4 标题/首句明写 “20 是测试矩阵上限，生产无 20 cap”，避免被读成产品容量结论（P2-2）。
- **“32 饱和结构性不可达”的排除表不完整。** 4004/4139 是真实生产分支，虽然只在 reaper 线程 spawn 失败时触发（与 F2 同属“不可确定性构造”），但 AC1 要求“逐分支”；必须把它作为 F5 列入并说明为何不能作为 Gate，或改写“唯一 track 入口/唯一反证窗口”的措辞。当前结论把 32 不可达归因于“shutdown 层层解除先于 track”，对 spawn-failure 路径不成立（P1-1）。

## AC2 方案真实性

| # | 核查点 | 结果 | 证据与关键输出 |
|---|---|---|---|
| B1 | 是否真的 test-only、是否改生产语义 | **PASS** | L1 只改 `FAULT_SIDECAR_SCRIPT`（test-only Python 进程/管道）；L2 只改 `library_bridge.rs` `#[cfg(test)] mod tests`；L3 用既有 `TEST_REGISTRY_OVERRIDE`/`TEST_THREAD_REGISTRY`/`IN_REGISTRY_TEST`（`1641-1656`）。文档明确“不放宽 `peak>=32`”（`819-822` 原样保留），未提改 MAX/锁/背压/holder/kill 预算。 |
| B2 | 120s+30s 预算、sampler 180s、停止条件 | **PASS（条件性）** | `multichannel_stress_tests.rs:50-55`：`SCENARIO_WALL_LIMIT=120s`、`CLEANUP_BUDGET=30s`、`SAMPLER_ABSOLUTE_LIMIT=180s`；`783-791`：`remaining==0` 或 30s 耗尽；`823-830`：remaining/wall 断言。预算数字与代码一致。 |
| B3 | L1 的 B 进程清理是否可执行 | **FAIL（P1-3）** | 文档 85 行要求“测试收尾在 CLEANUP_BUDGET 内显式 `taskkill /F /PID` 清 B”，但 B 是 sidecar 再派生的孙进程，测试不持有其 `Child`/PID；`stress_mark` 只作为 sidecar argv/tag 使用（`349/353/379`），仓库没有按 command line 查找 PID 的 helper。没有 PID 发现/有界重试，“taskkill /F /PID” 不可执行；B 若持续持有 stdin 读端（sidecar 现有 `time.sleep(3600)` 模式，`343`），会泄漏/污染环境。 |
| B4 | L1 的 stdin/stdout 继承是否只保留“读端” | **PARTIAL（P2-3）** | 文档只写“spawn A（subprocess 继承 stdin 读端），A 再 spawn B（再继承读端）”。Python `subprocess` 默认还会继承 stdout/stderr；若 B 同时持有 sidecar 的 stdout 写端，reader 不会 EOF，实验就不再是“writer 单独阻塞”的 F1 形态（cancel 仍可能让 peak=0，但机制/证据解释会漂移）。应显式 `stdout=DEVNULL`/`stderr=DEVNULL`，只继承 stdin。 |
| B5 | 预算/停止条件是否覆盖 B | **FAIL（同 P1-3）** | 现有 120s/30s 断言位于 fault 场景尾部（`827-830/823-826`），清理循环只 `reap_unreaped_workers`（`783-791`），不处理 B；文档没有把 B 的 `taskkill` 放进 30s 清理循环或给出其成功判据。 |
| B6 | 假 worker 是否被写成真实饱和 | **PASS** | L2 明写“人工阻塞替身（sleep 线程），证明 32 边界的 accepted/refused/holder 语义，不是生产饱和，不得写进 AC3 通过依据”（文档 88 行）；与任务卡禁止范围一致。`ac2_saturated_registry_answers_boundedly_and_never_loses_the_handle`（`9665-9715`）现有实现确实用 32 个 sleep 线程 + 第 33 个，且只断言有界/不丢 handle，没有冒充生产饱和。 |

## AC3 R2-F02..05 修订可行性

| # | 修订 | 结果 | 证据与关键输出 |
|---|---|---|---|
| C1 | R2-F02 fault 硬断言 | **PASS** | `multichannel_stress_tests.rs:729-730` 已计算 `writer_unfinished/reader_unfinished`；`734-737` 只有 `assert!(res.is_err())`；`720-724` 生成 `err_detail`。在 `734` 前加 `assert!(writer_unfinished && reader_unfinished)` 与 `assert!(err_detail.contains("stdin write timed out"))` 可执行、有意义；`756-757/764` 的 pre/post 分界与 `195-232` 的 `assert_pid_gone` 检查、`823-826` remaining 断言均存在。 |
| C2 | R2-F03 guard 收尾账本与 Arc 生命周期 | **FAIL（P1-4）** | 修订点 `6118-6145/6124-6128` 正确；guard 的 `reap_now` 后 `remaining>0` 分支确实只 eprintln。但“新测试 a：ac4/ac1/ac2 正常路径结尾断言 `TEST_GUARD_DROP_UNRECLAIMED==0`”按字面是在测试函数末尾、局部 guard（如 `_registry_guard`/`registry_guard`）的隐式 drop 之前执行；此时账本尚未被 guard drop 累加，断言恒为 0，抓不住缺陷。要成立必须显式 `drop(registry_guard)` 后再断言；而届时 `TEST_REGISTRY_EXCLUSIVE` 已释放，全局 Atomic 又可能被并行测试污染。需要 per-test 账本/重置或明确的串行断言区，不能只写“结尾断言”。 |
| C3 | R2-F04 线程账本断言（565/797） | **FAIL（P1-2）** | 文档 116 行写“两处 ledger 行（565、797）后加 `assert_eq!(threads_spawned, threads_joined)`”。`git grep -n "threads_spawned"` / `"threads_joined"` 只返回 `417/418/463/485/532/554/565`，**没有 797**；`797-798` 只是 `ledger channel_reader_writer_threads={}` + 常量 `20*2`。`threads_spawned` 是 `run_real_core_scenario` 的局部变量，fault 函数根本不在作用域；即使补变量，它也只计 ping/cancel/sampler 等测试 helper，不是 fault 场景的 reader/writer 线程。该修订在 797 行不可编译，也不构成“实际线程 join 账本”。 |
| C4 | R2-F04 child_lock tasklist → `pid_still_alive` | **PASS** | `library_bridge.rs:8549-8553、8559-8563` 确为裸 `Command::new("tasklist")`，不检查 `status`；`multichannel_stress_tests.rs:146-159` 的 `pid_still_alive` 检查 `out.status.success()` 且失败按“存活”fail-safe；`main.rs:42-44` 把 `multichannel_stress_tests` 作为同 bin 的 `#[cfg(test)] mod` 编译，`pub(crate)` 可见性可行。 |
| C5 | R2-F05 fail-closed / owner mismatch | **PARTIAL（P2-4）** | 修订点 `1706-1725`、`1712-1714`（`_ =>` global）、`1717-1721`（30ms timeout + `IN_REGISTRY_TEST` panic）均真实。测试设计需补“辅助线程已持锁”的握手（channel/Barrier）；否则 owner 线程可能在辅助线程拿锁前调用，30ms 超时分支不触发，测试会偶然走 private registry 而不 panic。owner mismatch 分支本身可执行。 |

## 禁止范围

| 核查点 | 结果 | 证据 |
|---|---|---|
| 改产品源码 / 改 `MAX_UNREAPED_WORKERS=32` / 改锁与背压 / 改 holder/kill/reap/taskkill 预算 | **PASS（文档正文）** | `1829a38` 三文件哈希与 R2 记录一致；DESIGN.md 只读设计，明确“不放宽 `peak>=32`”“不改生产 MAX/锁/背压/holder/kill 预算”；L2 明确 fake worker 不写成真实饱和。 |
| 把未实施写成已实施 | **PASS（文档正文）** | 全文用 `[建议]`/`[推断]`/`[实测]` 标注；AC3 明写“未实施、未复核”；设计结论要求新 Appointment/新 head，未自称已验收。 |
| 交付 head 是否“只增加 DESIGN/HANDOFF 与来源说明” | **PARTIAL（P2-6）** | 主仓 `3ca77fc` 除新增 `DESIGN.md` 与本 Task 卡更新（`allowed_paths`）外，还修改 `doc/handoffs/NEXT-SESSION-STARTER.md`、`tools/governance/check.ps1`，并新增另一份 governance review；没有 `HANDOFF.md`。这不是 DESIGN 正文越界（未改产品源码/依赖），但 AC4 的“新 head 只增加 DESIGN/HANDOFF 与来源说明”未被该 commit 满足；应在最终定案前冻结干净的 design-only head 并补 HANDOFF。 |

## 结论与裁定项是否被证据支持

| 文档结论 | 结果 | 复核 |
|---|---|---|
| “本设计（AC1 时序链/分支排除表、AC2 分层方案、AC3 四项最小修订）为可释放的完整设计切片” | **FAIL** | A6/P1-1、C3/P1-2、B3/P1-3、C2/P1-4 四项未闭合；不能称“完整可释放”。 |
| “父 Task AC3 真实 32 饱和：读代码推断 + r2 实测（peak=0）支持结构性不可达；唯一反证窗口（F1 组合）由 AC2-L1 检验” | **PARTIAL/FAIL** | `peak=0` 的 R2 实测支持“当前 fault 场景未触界”；但“唯一反证窗口”被 4004/4139 的 spawn-failure track 路径打破，需补 F5 或限定条件。 |
| “AC3 维持 BLOCKED，L1 落地前不改 AC” | **PASS** | 与任务卡“保留 AC3 BLOCKED、不自动改 AC”一致；`819-822` 的 `peak>=32` 保留。 |
| “AC 口径只能由 Codex/用户裁定” | **PASS** | 文档 138 行明确不自行改 AC；符合任务卡。 |

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| P1-1 | P1 | `verification/GIT-CLEAN-RUST-CAPACITY-DESIGN-1/DESIGN.md:50-52,60-71`；`library_bridge.rs:4004,4139` | 文档称 3980/4115 是“唯一 track 入口”，1.5 只列 F1–F4；代码在 reader/writer reaper 线程 spawn 失败时（4004/4139）直接 track。由此“唯一反证窗口 F1+cancel 无效”和“32 结构性不可达”不是逐分支成立的。 | `git -C $p grep -n "track_unreaped_worker("` → 3980、4004、4115、4139（另 1861 holder、1882 helper）；`3999-4004` 为 `if let Err(e) = spawn_res` 分支。 | 把 4004/4139 列入 1.3/1.5；新增 F5“reaper 线程 spawn 失败”并说明其不可确定性构造/是否 Gate；改写“唯一 track 入口/唯一反证窗口”。 | open |
| P1-2 | P1 | `DESIGN.md:116`；`multichannel_stress_tests.rs:797-798` | R2-F04 要求在 565、797 两处加 `assert_eq!(threads_spawned, threads_joined)`；797 所在 fault 函数没有这两个变量，只有常量 `channel_reader_writer_threads=20*2`。该修订不可编译；即使补计数，也只覆盖测试 helper，不覆盖 fault 的 reader/writer 线程。 | `git grep -n "threads_spawned\|threads_joined"` → 仅 417/418/463/485/532/554/565；`797-798` 输出常量。 | 要么只保留 565（并说明它只断言测试 helper 账本），要么在 fault 场景新增真实 spawn/join 计数并纳入断言；另用 `resources_for_test` 的 per-channel flags 作为 reader/writer join 证据。 | open |
| P1-3 | P1 | `DESIGN.md:82-86` | L1 的 B 是 sidecar 的孙进程，测试无 PID/Child；`taskkill /F /PID` 没有 PID 来源；30s 清理循环只 reap registry，不处理 B。B sleep 3600 且持有 stdin 读端，会泄漏/污染环境，AC2 的清理条件不可执行。 | `stress_mark` 仅 349/353/379；仓库无按 marker 查找 PID 的 helper；`783-791` 仅 `reap_unreaped_workers`。 | 让 sidecar 把 B 的 PID 写入测试临时目录/输出一行，测试读取并在 30s 内有界 `taskkill /F /PID` + `pid_still_alive` 复核；或使用 Job Object 兜底；把 B 清理纳入 CLEANUP_BUDGET 断言。 | open |
| P1-4 | P1 | `DESIGN.md:108-111`；`library_bridge.rs:6118-6145` | “新测试 a：正常路径结尾断言 `TEST_GUARD_DROP_UNRECLAIMED==0`”按字面在局部 guard 隐式 drop 前执行，账本尚未累加，断言恒真；若显式 drop 后再断言，全局 Atomic 又可能被并行测试污染。 | `6118-6145` guard drop 才 `reap_now`/记录；现有 ac 测试用局部 guard（`_registry_guard`/`registry_guard`）直到函数末尾隐式 drop。 | 明确 `drop(registry_guard); assert_eq!(...)` 的顺序；为每个测试使用独立账本或串行区/重置；测试 b 的 panic 路径可保留。 | open |
| P2-1 | P2 | `DESIGN.md:82`；`library_bridge.rs:3318-3323` | 文档称 `run_taskkill_bounded` 的 `/T` 按父链快照 BFS（3318-3323）；该区间只是 `Command::new("taskkill").args(["/F","/T","/PID",...])` 的构造，BFS 是 taskkill 的 OS 行为，不是 Rust 代码。结论可能仍成立，但证据引用不准确。 | `3318-3323` 输出仅为命令构造。 | 改写为“由 Windows taskkill /T 在调用时枚举父链”，或补真实枚举 helper；不要把 3318-3323 说成 BFS 实现。 | open |
| P2-2 | P2 | `DESIGN.md:55-58` | “20 真实 pipe”是 fault 测试的 0..20 矩阵；代码没有生产 channel 上限 20。文档虽写了“场景矩阵冻结 20”，但标题/结论容易被读成产品容量。 | `652-657` 为 `for idx in 0..20`；real-core 1/8/20；`1606` 只是 registry 32。 | 在 1.4 首句明写“20 是冻结测试场景上限，不是生产 channel cap”。 | open |
| P2-3 | P2 | `DESIGN.md:82` | A/B 若默认继承 sidecar stdout/stderr，会同时持有 reader 的写端，reader 不 EOF，L1 不再是“writer 单独阻塞”的 F1 形态。 | Python `subprocess` 默认 `stdout=None` 继承父进程；文档只写“继承读端”。 | B spawn 时显式 `stdin=inherit/None`、`stdout=DEVNULL`、`stderr=DEVNULL`；在预注册判据中记录 reader 状态。 | open |
| P2-4 | P2 | `DESIGN.md:123-125` | fail-closed 测试要求辅助线程持 `TEST_REGISTRY_OVERRIDE` ≥60ms；没有“已持锁”握手时，owner 线程可能在辅助线程拿锁前调用，30ms 超时分支不触发，测试偶发不 panic。 | `1711` 30ms；`1716-1724` fail-closed 分支；设计未给 signal。 | 用 channel/Barrier 在辅助线程持锁后通知 owner，再 `catch_unwind`；超时/失败时显式 `join` 辅助线程。 | open |
| P2-5 | P2 | `DESIGN.md:108-111` | `TEST_GUARD_DROP_UNRECLAIMED` 为全局 Atomic；ac1/ac2/ac4 并行时，测试 a 的 0 断言可能受其他测试/前序泄漏影响；测试 b 的 panic 路径同样。 | 6118-6145 为全局 tests 模块；无 per-test reset。 | 每测试开始 reset 或在 guard drop 时记录到测试局部账本；测试 a/b 用串行区。 | open |
| P2-6 | P2 | `DESIGN.md:133-140`；主仓 `3ca77fc` | AC4 要求“新 head 只增加 DESIGN/HANDOFF 与来源说明”；`3ca77fc` 还改 handoff/check.ps1（task 卡自更新属 `allowed_paths`）并新增另一 review，且无 HANDOFF.md。非产品源码越界，但 AC4 head 证据不干净。 | `git show --stat 3ca77fc`；`git diff --name-status 3ca77fc^ 3ca77fc`。 | 另冻 design-only head（DESIGN/HANDOFF/来源说明），或把本 commit 的其它治理改动拆出；在 HANDOFF 中记录设计基准/证据。 | open |

## 已核对的其余引用（抽样清单）

以下引用本次逐一读过，未发现阻断性偏差；行号有少量 2–5 行范围误差，属 P3 级，不单列 P2：

- `library_bridge.rs:2106-2380`（`adopt_child`）、`2146-2149`（raw handles）、`2156/2264`（线程名）、`2223-2255`（reader EOF/Err）、`2332-2337`（writer 写错误 break）。
- `library_bridge.rs:3427/3429/3432-3535`（shutdown 幂等/重入）、`3539-3613`（drain pending）、`3615-3640`（CloseHostSession）、`3642-3656`（core.shutdown 60ms）、`3658-3693`（kill child）、`3755-3782`（taskkill fallback）。
- `library_bridge.rs:3895-4027`（reader join 100ms）、`4029-4162`（writer join 80ms）、`3932/4067`（reaper 线程名）、`3980/4115`（track）、`4164-4167/4200`（reap 50ms/20ms）、`4171-4202`（Drop）。
- `library_bridge.rs:1606`（`MAX_UNREAPED_WORKERS=32`）、`1748-1809`（track 10×50ms、容量分支、refuse）、`1825-1878`（holder 50→500ms/失败同步 join）、`1906-1949`（reap=prune+cancel）。
- `library_bridge.rs:2499-2526`（`write_stdin_raw_timeout`，2513-2515 timeout）、`2665-2672`（exchange）、`2842-2855`（round_trip）。
- `multichannel_stress_tests.rs:50-55`（预算）、`146-159`（`pid_still_alive`）、`195-233`（`assert_pid_gone`）、`299-307/368`（spawn/adopt）、`349`（stress_mark）、`652-657`（20 channel）、`712`（4MB）、`729-737`（fault 断言）、`753-770`（Drop）、`783-791`（cleanup）、`819-830`（peak/remaining/wall）。
- `library_bridge.rs:6042-6145`（`RegistryTestGuard`）、`9462/9498/9561/9666`（acquire 点）、`9665-9715`（ac2 32 边界）、`1706-1725/1712-1714/1717-1721`（fail-closed/owner mismatch）、`1641-1656`（test-only 状态）。

## 未审 / 限制

- 本次**未重跑** Rust、真实 Core、fault sidecar 或任何压力测试；`[实测]` 数字（20/20、peak=0、exit101）仅引用 R2 Review 已记录事实（source pin），不构成本次独立运行 PASS。
- 未审 packaged sidecar、安装包、模型、GUI/WebView、release、main 集成；未审父 Task 的 AC3 真实饱和门槛。
- 未改任何产品源码、测试、Task、Status、Plan、证据或 ACL；唯一写入为本报告。

## 复审建议

1. **修 P1-1**：补 4004/4139 与 F5，改写“唯一 track 入口/唯一反证窗口”；如认为 spawn 失败不可注入，也须在 1.5 逐条说明，不能省略。
2. **修 P1-2**：把 R2-F04 的 797 行断言改为真实可编译的计数，或删除 797、只保留 565，并明确“helper 账本 ≠ reader/writer join 账本”；reader/writer 以 `resources_for_test` flags 为准。
3. **修 P1-3**：给 B 明确 PID 发现/清理路径（sidecar 写 PID 文件或 stdout，测试读取；30s 内 taskkill + 复核）；B 只继承 stdin，stdout/stderr DEVNULL。
4. **修 P1-4**：R2-F03 测试 a 明确先 `drop(registry_guard)` 再断言，并用 per-test 账本/串行区避免全局 Atomic 污染；否则该断言恒真或偶发。
5. 修 P2-1..P2-6 后可再次提交独立复核；在 P1 全闭合前，本设计不应按“可释放完整设计切片”定案。

---

## 第二轮复核（v2）

- **复核者**：子 agent `design-reviewer`（同一独立上下文；未参与 v2 修订）。
- **被复核 head2**：`759687d59bf345adc4892613e19c3c9253f7c239`（主仓 `759687d59`，仅改 `DESIGN.md` 与 Task 卡）；代码基准仍为 `1829a38a41587a0d680001a40d206886afb0911d`。
- **复核时间**：2026-11-17T03:20:00+08:00。
- **只读声明**：本次只读 v2 与 `1829a38` 代码；未改任何文件（仅本报告追加）、未 commit/push/集成、未运行 Rust/压力测试。

**verdict2: BLOCKED**——P1-1、P1-3 已实质修复；P1-2 仍会编译失败，P1-4 引入了新的 double-cleanup 竞态，故仍不能释放。

| P1 | v2 结果 | 关键证据 |
|---|---|---|
| P1-1 | **PASS** | v2 §1.3 列出 TA=3980、TB=4004、TC=4115、TD=4139 四入口，并补 F5；`git grep` 与代码一致；4004/4139 确在 `if let Err(e) = spawn_res`（3999/4134）分支内。1.5 以“共同前置 P + TA/TC 或 TB/TD”重构，F5 不放宽 P，论证逐分支完整。 |
| P1-2 | **FAIL** | real-core 在 555 后的真实局部变量断言可编译；但 fault 聚合断言写在 `for id in identities`（807，按值移动）之后，却使用 `identities.iter()`，按 v2 的插入点仍是 `E0382: use of moved value`。`joined_flags` 是 661/764 的 pre-drop 标志，不能替代 post-drop join 证据。 |
| P1-3 | **PASS（附 P2-7）** | B 自写 pidfile、测试 ≤2s 发现、`run_taskkill_bounded(5s)`、`wait_for_pid_exit(10s)`、缺文件 fail-loud：PID 发现与清理机制本身可执行，未把不可行写成可行；落点需按 P2-7 保住 `TempDir` 生命周期。 |
| P1-4 | **FAIL（新 P1-4b）** | `finish(self)` 内 `cleanup()` 后 `self` 仍在返回时 Drop，`Drop` 会再次 `cleanup()`；`cleanup` 无条件清 `TEST_REGISTRY_OVERRIDE`。`finish` 已释放 EXCLUSIVE 并最多等 Arc 2s，期间另一测试可安装自己的 slot，随后第二次 cleanup 会把它清掉；`remaining>0` 时还会二次累加 thread-local 账本。 |

### P1-1 复核细节（PASS）

```powershell
git -C "G:\CODEX\New Manga" rev-parse HEAD
# 759687d59bf345adc4892613e19c3c9253f7c239
git -C "G:\CODEX\New Manga" show --stat --oneline 759687d59
# DESIGN.md 240 +-, Task 卡 4 +-
$p="G:\CODEX\New Manga.workspace\task-envs\GIT-CLEAN-RUST-ISOLATION-1\source-r2"
git -C $p grep -n "track_unreaped_worker(" 1829a38 -- apps/desktop/src-tauri/src
# 1861, 1882, 3980, 4004, 4115, 4139, 9472, ...
```

`git -C $p show 1829a38:apps/desktop/src-tauri/src/library_bridge.rs` 的 3999-4004 / 4134-4139 明确显示：

```text
3999: if let Err(e) = spawn_res {
4000:     let err_msg = format!("failed to spawn reader-join-bounded-reaper: {e}");
4001:     eprintln!("[shutdown] {err_msg}");
4002:     if let Ok(mut h_lock) = handle_shared.lock() {
4003:         let mut h_opt = h_lock.take();
4004:         let tracked = track_unreaped_worker("reader", ...);
4134: if let Err(e) = spawn_res {
4139:     let tracked = track_unreaped_worker("writer", ...);
```

因此 v2 的 TA..TD 全表与 F5 成立；“首次 track 只能经 TA..TD、1861 只是 refused handle 重投递”也与代码一致。  
P2 备注：F2 只写“cancel 双失败”并以“DUPLICATE_SAME_ACCESS 句柄有效”为理由；但 `2321-2324` 的 DuplicateHandle 失败会把 `writer_thread_handle` 置负，`1555-1557` 的 cancel 会失败——这是同属“资源面/不可注入”的 F2 子情形，建议并入 F2 或另列 F6，不影响 P1-1 通过。

### P1-2 复核细节（FAIL）

v2 §3.4 的 fault 断言插入点如下（`git -C $p show 1829a38:apps/desktop/src-tauri/src/multichannel_stress_tests.rs`）：

```text
805: let identities = take_ledger();
806: assert_eq!(identities.len(), 20, "OS identity checks must cover all fault channels");
807: for id in identities {
808:     assert_pid_gone(scenario, &id);
809: }
```

`for id in identities` 按值移动 `Vec<ChildIdentity>`；v2 §3.4 却把

```rust
let all_workers_finished_and_joined = identities.iter()
    .all(|id| id.worker_flags.iter().all(|f| f.load(Ordering::SeqCst)));
```

写在 806-809 **之后**、811 之前。该插入点会编译失败（`identities` 已 move）。修法只有两种：把聚合断言移到 807 之前，或把循环改成 `for id in &identities`；v2 未写这一步。  
另外，`joined_flags` 是真实变量（661 定义、764 push），但存的是 Drop **前**的 `writer_joined_pre_drop`/`reader_joined_pre_drop`，不是 post-drop join 账本；不能作为替代证据。  
real-core 侧 v2 要求在 555 `});` 后断言 `threads_spawned == threads_joined`：变量确实在 417/418 定义、463/532/554 累加，**这一段可编译**；它只证明测试 helper 线程 join，v2 已如实注明。P1-2 的失败点是 fault 侧聚合断言，不是这一处。

### P1-3 复核细节（PASS，附 P2-7）

v2 §2.2 的链路逐项可执行：B 脚本 `open(sys.argv[1],'w').write(str(os.getpid()))` 写 pidfile；测试 ≤2s 轮询；`run_taskkill_bounded` 在 `3308` 存在且接受 `u32` PID；`wait_for_pid_exit` 在 `170-179` 存在；`pid_still_alive` 在 `146-159` 检查 `status.success()`，失败按存活 fail-safe。缺 pidfile 时 fail-loud 并给人工 `wmic` 指引，没有静默跳过。

P2-7：pidfile 在 `dir.path().join("escape_b.pid")`，而既有 fault Drop 循环在 `769` 执行 `drop(lab.dir)`；v2 说“L1 场景函数尾部”才读取 pidfile，却未说明保留 `TempDir` 或提前读取。若照既有循环先删目录，pidfile 会消失。实施时必须：读取 PID 后再 `drop(lab.dir)`，或把 `TempDir` 保活到 B 清理完成；否则 pidfile 方案在时序上仍不可执行。另建议给 B 清理加 RAII/`defer` 兜底，保证 panic 路径也执行 taskkill。

### P1-4 复核细节（FAIL，新 P1-4b）

v2 §3.3 把 `Drop` 主体抽成 `cleanup()`，新增：

```text
fn finish(mut self) -> GuardFinishReport {
    ... self.cleanup() ...
    ... Arc::strong_count(&self.registry) 等待 ≤2s ...
    return report;
}
impl Drop { fn drop(&mut self) { self.cleanup(); } }
```

Rust 中 `finish(self)` 返回前会正常 drop `self`，因此 `Drop::drop` 会第二次调用 `cleanup()`。而现有 `cleanup` 的 slot 清除（`library_bridge.rs:6129-6139`）是无条件 `*slot = None`；`finish` 的 `cleanup` 已先释放 `TEST_REGISTRY_EXCLUSIVE`，再等 Arc 最多 2s。等待窗口内另一 registry 测试可取得 EXCLUSIVE 并安装自己的 override；随后第二次 `cleanup` 会清掉**别人的** slot，导致测试互相污染。若第一次 `cleanup` 的 `remaining>0`，第二次还会再次累加 thread-local 账本。

修法：`finish` 用 `std::mem::ManuallyDrop`/`mem::forget` 抑制 Drop，或给 guard 加 `finished: bool` 让 `cleanup` 只执行一次；同时把 slot 清除改成仅当 slot owner 仍是当前线程时才清。v2 的“断言读 finish 返回值 + thread-local 账本”方向正确，但没有处理这次 double cleanup，故 P1-4 仍未闭合。

### v2 新增/剩余 P2

- **P2-7**：pidfile 的 `TempDir` 生命周期（见上）；L1 清理须在 `drop(lab.dir)` 前读取 PID，或保活目录。
- **P2-8**：`finish` 的 Arc 等待在释放 EXCLUSIVE 后进行，本身可接受；但与 P1-4b 的第二次 cleanup 组合会跨测试清 slot，必须一起修。
- **P2-9**：v2 §3.5 写“默认套件 153→157（F03 测试 a/b 合并计入 F05 的两个新测试后总计 +4）”，但 F03 test a 是迁移既有测试、不是新增；按字面 +3（F03 b + F05 两个），需在实施清单里重新核对，避免测试计数口径错误。
- **P2-10**：v2 §1.4 的“TA..TD 四入口均未执行”仍是从 `peak=0` 反推的 [推断]，R2 日志没有“四入口调用计数”；建议改为“四入口均未观察到 accepted worker”或补 log 证据。
- **P2-11**：head `759687d59` 只改 `DESIGN.md` + Task 卡，仍无 `HANDOFF.md`；v2 §5 要求的 design-only head/HANDOFF 尚未落盘，AC4 的交付面仍待 Codex/DSH 补齐。

### 第二轮命令摘录

```powershell
cd "G:\CODEX\New Manga"
git rev-parse HEAD
# 759687d59bf345adc4892613e19c3c9253f7c239
git show --stat --oneline 759687d59
# doc/tasks/... 4 +- ; verification/.../DESIGN.md 240 +-
$p="G:\CODEX\New Manga.workspace\task-envs\GIT-CLEAN-RUST-ISOLATION-1\source-r2"
git -C $p grep -n "track_unreaped_worker(" 1829a38 -- apps/desktop/src-tauri/src
git -C $p show 1829a38:apps/desktop/src-tauri/src/library_bridge.rs
# 3999-4004, 4134-4139; 6118-6145; 3199-3205
git -C $p show 1829a38:apps/desktop/src-tauri/src/multichannel_stress_tests.rs
# 795-809: for id in identities; 661/764: joined_flags; 170-179: wait_for_pid_exit
```

**verdict2: BLOCKED**（P1 剩余 2 条：P1-2 编译失败、P1-4b double cleanup；P1-1、P1-3 已修复，P1-3 需落 P2-7 生命周期修正）。
