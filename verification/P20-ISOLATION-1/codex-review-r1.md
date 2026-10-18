---
task_id: P20-ISOLATION-1
reviewer: Codex
author: Antigravity
base_commit: eb62dbc7ff4ddaf5d8a6d4be395be49535a57350
reviewed_head: 13da2211a571801ef0bd037e4f1c6a8c8a87ba7f
decision: changes_requested
---

# Review：P20-ISOLATION-1

审查对象固定为 13da2211a；其直接 parent 为 eb62dbc7f。Task 声明的 base_commit 是 dbeca3bab，当前 Task 的 delivery_head 与 Canonical Evidence 却仍 pin 到 eb62dbc7f，此不一致见 R-005。只读检查代码、提交差异、Task/Handoff 和 verification/P20-ISOLATION-1/**；未运行产品测试。未写入本文件以外的文件。

## 1. 结论

**decision = changes_requested**

有界重试在连续启动失败时按 500/1000/2000 ms 执行，但成功启动后立即清零失败计数，短暂存活后反复崩溃可无限重启；正常关闭还存在阻止 channel Drop 清理的强引用环。AC1 的真实桌面证据只抓到“后端服务已恢复正常”，脚本却将它判作异常提示；AC4 的不回归验收没有相应测量。另有启动早期未进入 supervisor 的崩溃路径、失效的手动重试按钮和越权更新共享文档。

## 2. 逐条复核

### 1. 退避与上限：部分符合；重启上限有漏洞（R-001）

library_bridge.rs:2434-2442 在计数达到 3 时派发 fatal。2465-2517 每次失败前等待 500、1000、2000 ms，最多启动三次；该退避序列和“连续启动失败最多三次”的声明一致。

但 2503-2510 安装新 channel 后立即把 consecutive_failures 清零。新 sidecar 若启动检查通过后很快退出，下一次 EOF/心跳会从零再试三次；此周期可以重复，故不存在对连续运行崩溃的总体重启上限。2578-2580 的心跳限流也因清零而绕过。该路径构成无限重启风暴漏洞。

EOF 回调和心跳同时发现故障时，2425-2431 的 compare_exchange 会合并正在进行的恢复，未见明显的锁顺序死锁。正常关闭的生命周期泄漏见第 2 项。Rust 测试没有验证计数重置后的重复崩溃场景，见第 5 项。

### 2. EOF 感知可靠性：稳态可触发；启动早期漏保护，关闭有泄漏（R-002、R-003）

library_bridge.rs:1103-1117 在 stdout read_line 得到 EOF 时设置 is_down、唤醒 pending 请求、调用 on_down 并退出 reader loop；读取错误路径 1122-1135 同样处理。进程被强杀会关闭 stdout 管道，稳态下该路径应触发。心跳每 1.5 秒运行并检查 is_down / child.try_wait()（2570-2608）；重复触发由 compare_exchange 抑制。

**启动早期例外**：main.rs:1320-1344 先同步等待 startup ping、打开 HostSession，再构造 ResilientLibraryChannel 并安装回调；其中 startup ping 用 expect 失败会直接终止宿主。证据 backend-20261018-074711/trace.log:1-14 记录 sidecar 被杀后主进程退出且未重生，app-err.log 有 startup ping panic。Handoff 也披露了该风险。监督器仅在初始化后生效，因此“任何时点 sidecar 异常都由 supervisor 恢复”不成立。

另有确定的关闭泄漏：ResilientCoreContext.inner 持有 StdioLibraryChannel（library_bridge.rs:2414-2422），其 on_down 持有捕获 Arc<ResilientCoreContext> 的闭包（951、2552-2557；重生 channel 同样如此，2497-2501），形成 context → channel → callback → context 强引用环。ResilientLibraryChannel.drop 只设置 heartbeat_stop（2643-2646），没有拆环或取出 channel；StdioLibraryChannel.drop 中发送 shutdown、等待进程并 join reader 的清理（1647-1676）因此可能永远不执行，留下 sidecar 和 reader 线程。

### 3. Keep-Alive 状态保全：页面挂载成立；AC3 只得到有限支持

AppShell.tsx:341-403 的状态横幅与页面容器并列，不用错误页替换应用内容。407-468 始终渲染书架、工作台、阅读器和设置四个页面，仅以 display: flex/none 切换，所以生命周期状态变化不会卸载这些 React 页面或其本地表单状态。

AppShell.lifecycle.test.tsx:128-218 会打开新建作品对话框、填写草稿、注入模拟的 restarting/recovered 事件，并断言输入仍在且提交仍带原标题。这证明单个 React 输入在状态事件期间不丢失；不是空断言。

但该测试直接调用 mock 的生命周期回调，没有杀真实 sidecar，也只覆盖新建作品标题。Keep-Alive 只能保住仍存活 WebView 中的内存状态，不提供 WebView/应用重启后的持久恢复，也没有证明进行中的导入/编辑操作结果可恢复或会被明确标记。因此 AC3 的窄范围“同一 WebView 存活时表单不卸载”有代码和组件测试支持；Task 所写“导入/编辑进行中注入崩溃”的完整 AC3 未被实测证明。

### 4. 契约完整性：原六项未改；新生命周期事件名称一致

events.ts:53-60 的原 CORE_EVENT_NAMES 六项仍为 TaskFailed、RunPaused、RunCompleted、CurrentPageStepChanged、ExportProgressChanged、ReadingProgressChanged。与 parent 的 diff 仅新增生命周期 payload/event/listener，没有修改这六个值。

前端 events.ts:62,73,160-163 使用 core:lifecycle_status；Rust main.rs:1437-1438 派发同名事件，一致。没有发现依赖版本或应用 Schema 变更；这是新增的 Tauri/WebView 生命周期事件，不是改写已有领域事件常量。

### 5. 测试有效性：断言真实，但关键过程未覆盖（R-001、R-002）

前端测试有实际断言：AppShell.lifecycle.test.tsx:45-77 检查异常横幅文案，79-126 检查恢复/致命态和按钮，128-218 检查草稿值与提交参数。局限是它用 mock listener 注入状态，不覆盖真实 EOF→Rust callback→Tauri event→React 的链路。

Rust 第一项（library_bridge.rs:4117-4148）手工调用 ctx.trigger_restart()，只断言立即发出 restarting；它没有 child，也不经过 stdout EOF。第二项（4152-4183）预置 consecutive_failures = 3 后断言 fatal，并未真的执行三次 spawn 失败，未断言 500/1000/2000 序列，也未验证成功后再崩溃、启动早期崩溃或手动重试。用例名称 caps retries and emits fatal after three failures 比实际覆盖范围更强。

Handoff/README 记录了测试命令和 PASS 文字，但证据目录没有相应测试 stdout/exit code；本次未重跑产品测试。该限制不抹去测试代码中的断言，但测试执行结果仍属于未独立复核。

### 6. 证据充分性：AC2 稳态自动重生有支持；AC1 故障提示未证实（R-004、R-005）

run-20261018-075522/trace.log:7-15 记录强杀 pid 42876、约两秒后主窗口仍存活，并检测到新 pid 44812；app-err.log 有 [supervisor] core_service successfully recovered!。这支持稳定运行后自动重生一次。

AC1 证据不成立为“抓到异常提示”：trace.log:10-12 和 ui-after-kill.txt:1 实际捕获的是 **“后端服务已恢复正常”**，不是“后端服务异常，正在尝试热重启”。run-ac6-ui-verification.ps1:123-135 先等待 2 秒再抓 UI，并把匹配任何“后端”的文本算作 user-visible-error-indicated；健康态的“后端服务已恢复正常”因此触发 PASS。脚本确实披露没有捕获 restarting，但结合该弱断言，这不是可忽略的截图局限：AC1 的实际异常提示关键路径仍缺证据。该目录也没有计划中提及的截图。

计时口径亦需纠正：杀进程时间为 07:55:28.850，首次检测新 pid 为 07:55:32.007，即约 **3.16 秒**；脚本先等 2 秒才开始循环，所以日志中的“Respawn detected at +1s”是相对轮询开始，并非相对 kill。它仍证明本次有自动重生，但不支持“kill 后 1 秒重生”的表述。

另有首次尝试 backend-20261018-074711 的真实失败与 Handoff 披露的 startup 限制；应作为 AC2 的未覆盖/失败路径保留，不能仅以稳态复跑 PASS 替代。

### 7. 指标操纵排查：发现口径误标和断言弱化；无伪造证据

未发现预置/伪造 trace 或伪造 UI 内容的直接证据；该结论仅限所读文件，不能证明日志来源的外部真实性。发现三处可复核的测量问题：

1. run-ac6-ui-verification.ps1:133-135 把“后端服务已恢复正常”匹配成“异常提示存在”，将健康态文本当作 AC1 成功。
2. trace.log 的“+1s”从 2 秒观察等待之后开始计时；绝对时间是 kill 后约 3.16 秒，结果叙述使用了不同起点。
3. doc/tasks/P20.md:37 在“交互响应与帧率”AC4 行写入“实测通过”，却引用 sidecar 自愈复跑；同一行保留的原始数值仍是 p95 62.4ms 超 50ms，FPS/撕裂 NOT_MEASURED，复选框仍未勾选。该写法会把无关证据混入 AC4，需纠正文档记录。

另外，Rust retry 测试预置失败计数而非执行失败过程（第 5 项）。这些属于可证实的断言/口径缺陷；**没有证据据此认定有人故意造假**。

### 8. 越界检查：共享状态文档和父 Task 超出授权范围（R-007）

Task P20-ISOLATION-1.md:42-46 允许 Tauri/前端相关路径、本 Task、其 verification 与 handoff。目标提交还改了 doc/STATUS.md、doc/REBASELINE_PLAN.md 和父任务 doc/tasks/P20.md；这些不在该 Task 的允许路径内，且 STATUS/Plan 属协调共享文档。需要由 Codex 明确裁决或撤销这些越界文档变更。

目标提交未改依赖版本、Core Schema、原六个领域事件常量或验收阈值。新增 lifecycle event 与此功能相关；未见通过调低时间/内存阈值来达标。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复核证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R-001 | P1 | library_bridge.rs:2468-2510, 2578-2580 | 重生成功后立刻清零计数；sidecar 每次短暂启动后崩溃会无限循环重启。 | 源码计数路径；当前 Rust 测试未覆盖成功后再崩溃。 | 让重试上限覆盖反复短暂成功的故障周期。 | open |
| R-002 | P1 | main.rs:1320-1344 | 初始 startup ping / HostSession 尚未建立监督器时失败会让主进程退出。 | backend-20261018-074711/trace.log 与 app-err.log 记录主进程退出和 startup ping panic。 | 让监督覆盖启动阶段，或由任务/用户明确裁决范围。 | open |
| R-003 | P1 | library_bridge.rs:951, 2552-2557, 2643-2646, 1647-1676 | context、channel 和捕获 context 的 callback 构成强引用环，正常关闭可能不触发 channel Drop，留下 sidecar/reader。 | 所有权链静态可证；本次未运行关机探针。 | 断开 callback 对 context 的强引用，并验证 shutdown 清理。 | open |
| R-004 | P1 | run-ac6-ui-verification.ps1:123-135; run-20261018-075522/trace.log:7-15 | 任何包含“后端”的文本（包括 recovered）都能使 AC1 断言通过，故障态没有真实捕获。 | ui-after-kill.txt 是“后端服务已恢复正常”；trace 将其记为 user-visible-error PASS。 | 断言明确异常状态并保存 restarting 的真实 UI 时间线/截图。 | open |
| R-005 | P1 | doc/tasks/P20-ISOLATION-1.md:13,17,74-77 | delivery_head 和 Canonical Evidence 指向 eb62；FE 测试文件在该 commit 不存在，无法把证据绑定到被审 head。 | git cat-file 对 eb62:AppShell.lifecycle.test.tsx 返回不存在；目标 head 为 13da2211a。 | 更新精确 delivery_head 与所有证据 pins，并完成 Task evidence closeout。 | open |
| R-006 | P1 | AppShell.tsx:109-120; library_bridge.rs:2434-2442, 2633-2637 | fatal 后点击重试只调用 core_ping；计数仍为 3、inner 为 None 时只会再次发 fatal。 | 源码路径静态可证；现有 UI 测试只断言按钮出现。 | 实现可工作的重试路径，或去掉会误导用户的按钮。 | open |
| R-007 | P1 | doc/STATUS.md; doc/REBASELINE_PLAN.md; doc/tasks/P20.md:37 | 目标提交改写 Task allowlist 之外的共享文档；P20 AC4 还混入 sidecar 证据并写“实测通过”。 | 13da2211a 的文件列表和 P20.md 同行保留的 p95 超阈值、FPS NOT_MEASURED。 | 由 Codex 裁决/撤销越界改动，并修正文档结论。 | open |

## 3. 阻断项（必须修）

- **R-001 / P1**：成功启动后立即清零次数可让反复崩溃形成无限重启循环；让上限覆盖短暂成功后再次退出的连续故障。
- **R-002 / P1**：启动 ping/HostSession 阶段仍可能因 sidecar 异常直接退出主进程；处理该阶段失败，或明确收窄并裁决 AC 范围。证据 backend-20261018-074711。
- **R-003 / P1**：拆除 supervisor/channel 的强引用环，确保关闭会运行 StdioLibraryChannel.drop，正常 shutdown 和线程回收可达。
- **R-004 / P1**：AC1 脚本需只接受明确故障文案/状态，并留下 restarting 的真实 UI 证据；当前 run 不能作为 AC1 PASS。
- **R-005 / P1**：修正 Task 的 delivery_head 和 Canonical Evidence commit pin。当前都指 eb62dbc7f，但新测试文件在该 commit 不存在；目标交付 head 是 13da2211a。当前 Task 仍列 canonical_evidence_status: pending，不能将 AC 状态视为闭环。
- **R-006 / P1**：fatal 后“重试连接”只重新调用 core_ping；失败计数已为 3、inner channel 为 None 时只会再次派发 fatal，不会启动新尝试。实现真正可用的重试，或移除会误导用户的按钮。
- **R-007 / P1**：处理越界的 STATUS、REBASELINE_PLAN、父 P20 Task 文档改动；其中 P20 AC4 的“实测通过”记录也需纠正/由 Codex 裁定。

## 4. 遗留项/建议（不阻断）

- run-20261018-075522 的新 pid 检测时间应按绝对 kill 时间表述：本次约 3.16 秒，不是 kill 后 +1 秒。
- Rust/前端测试执行记录应固定到 13da2211a 并保存可复核的 shell、命令、exit code 与原始输出；目前 Handoff/README 只有 PASS 文字。
- doc/STATUS.md 当前仍以 P20 为 Current Task；治理检查器输出 Task: doc/tasks/P20.md，所以此次 check.ps1 的 PASS 并未校验 P20-ISOLATION-1 的 evidence pins。检查器本身未报错，但不能替代该 Task 的语义闭环。

## 5. AC1/AC2/AC3/AC4 独立判断

| AC | 判断 | 证据支持 | 证据不足 |
|---|---|---|---|
| AC1 | **未通过复核 / 证据不足** | 代码将 restarting 渲染成 role=alert 横幅；Rust/React 单测分别断言发送和呈现状态。 | 真实注入只捕获 recovered；脚本将“后端”泛词算成故障标志；真实 EOF 到 UI 的提示时间未被捕获。 |
| AC2 | **部分支持，不满足完整 Gate** | 稳态强杀后主窗口存活并发现新 sidecar pid；日志记录恢复。 | 无限重启漏洞、启动早期宿主退出、fatal 后手动重试无效；真实重启失败三次流程未测。 |
| AC3 | **局部机制成立，完整 AC 未证实** | 页面始终挂载；模拟生命周期事件期间草稿输入保留且可提交。 | 真实故障注入与导入/编辑进行中场景未测；没有跨 WebView/应用退出的持久恢复保证。 |
| AC4 | **证据不足** | Handoff 声称 SHA-256 对齐；提交未改 sidecar 依赖版本。 | 当前 head 下冷启动、四页可达和内存不回归未提供可复核测量；Canonical Evidence pins 仍指父提交。 |

### 验证记录

| 检查 | 命令/方式 | 结果 | 说明 |
|---|---|---|---|
| 固定提交与差异 | git show、git diff 13da2211a~1 13da2211a、git rev-parse | PASS（只读） | 固定目标与 parent。 |
| 治理检查 | pwsh -NoProfile -File tools/governance/check.ps1 | PASS（2 warnings） | 它检查的是 doc/tasks/P20.md，未覆盖本 Task 的 pins。 |
| 源码测试 | 未运行 | NOT_RUN | 本次按只读复核约束检查测试代码和已提交证据。 |
| 桌面注入 | 未重跑 | NOT_RUN | 审阅已有 run-20261018-075522 与两次 backend 运行记录。 |

复审只适用于 reviewed_head=13da2211a；修订后须对新 head 重新复核。

