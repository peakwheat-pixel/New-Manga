---
task_id: P20-ISOLATION-1
reviewer: Codex
author: Antigravity
base_commit: 13da2211a571801ef0bd037e4f1c6a8c8a87ba7f
reviewed_head: c16e00c761e1fdd55472298164e8f6e53d3eee98
decision: changes_requested
---

# P20-ISOLATION-1 独立复审 R2

## 1. 结论

**decision = changes_requested**。

代码复审覆盖 `13da2211a..9d3924c05`；实际仓库 `HEAD` 是 `c16e00c761`，它只追加了 handoff 文档。R-001 的短命崩溃预算、R-002 指定启动路径的 `.expect`、R-003 的强引用环、R-006 横幅重试按钮均有实质修复；R-004 的真实桌面记录确实观测到故障文案和自动重生，R-007 对 P20 AC4 的误标也已纠正。

尚不能批准：R-005 的 Task/Handoff/evidence pins 仍互相不一致，治理检查因此失败；AC2 没有处理“进程存活但 IPC 无响应”；R-003 的 Drop 可在无响应路径上无限等待；AC3 与 AC4 的验收证据不足，且 Task 把仍待验证的 AC4 标成通过。

本次只读源码、Task、Handoff 和已落盘证据；未运行产品测试、未改产品代码。治理检查为只读检查，结果见第 5 节。

## 2. R-001 / R-002 / R-003 / R-006 逐项复核

### R-001：已修复快速崩溃无限重启；稳定期补预算缺少独立测试

- `library_bridge.rs:2482-2493` 只有 `last_spawn_time.elapsed() >= stable_duration` 才清零预算；默认值为 30 秒（`2429-2445`）。成功重生后保留已消耗计数并记录启动时间（`2605-2618`）。短于 30 秒的 EOF/请求失败再次经过同一个 `trigger_restart`，不会补预算。
- EOF 回调、心跳和请求错误最终都进入 `trigger_restart`（`2597-2603`、`2728-2753`、`2771-2785`）；入口及心跳检查 `is_fatal`，到达预算后进入 fatal，不再启动恢复线程（`2477-2507`、`2703-2711`）。长时间稳定后若收到 EOF，`trigger_restart` 会先补预算，因此 30 秒本身不会阻止后续自愈；耗尽预算进入 fatal 后则不会自动复活，这是当前有界策略的预期结果，需重启应用。
- `resilient_channel_crash_loop_is_bounded_and_reaches_fatal` 确实用 `cmd /c exit 0` 产生真实短命子进程，并断言 spawn 总数为 3、fatal、再次触发不再 spawn（`4361-4431`），不是空断言或预置 fatal 计数。该测试将 `new(None)` 默认的初始失败计数手动改成 0（`4390-4393`），用于验证从零预算开始的三次快速崩溃；没有覆盖“存活满 30 秒后预算补充”的边界。
- 判断：原 R-001 的短命成功/退出循环已被有界预算堵住。证据足以支持这一点；稳定期恢复路径是代码检查支持、无独立测试覆盖。

### R-002：指定启动错误不再 panic；setup/UI 通知和线程创建仍有边界

- `main.rs:1331-1355` 的 `spawn_with_startup_ping` 与 `open_host_session` 已改为 `Result` 链；失败记录日志、构造 `None` channel。`ResilientLibraryChannel::new(None)` 初值为 1（`2653-2667`），随后 `record_initial_failure()` 是 `store(1)` 而非加一（`2688-2690`），没有重复计数。
- `main.rs:1443-1460` 先绑定状态 emitter，再检查 `is_unhealthy()` 并触发恢复。测试 `resilient_channel_early_startup_failure_recovers_without_panic` 实际断言空 channel 不健康、ping 返回 `CORE_UNAVAILABLE`，之后通过真实子进程恢复并观察 restarting/recovered（`4438-4493`）。但测试手动执行 `trigger_restart()`，没有运行 `main.rs` 的 Tauri setup 钩子，也没有验证 WebView 事件监听已就绪。
- 这里仍有时序风险：前端事件监听是异步注册，轮询每 2 秒才开始检查；后端只在 emitter 注册时重播 restarting/fatal，不保留并重播 recovered 状态（`AppShell.tsx:41-90`、`library_bridge.rs:3009-3017`）。若 setup/恢复事件早于 WebView listener，且首次轮询时 Core 已恢复，前端不会显示这次短暂故障。当前真实桌面注入覆盖运行中崩溃，不覆盖这种启动时序。
- 指定的两个启动 `.expect` 已移除；这不是 `main.rs` 全部无 panic：自愈/心跳线程 `Builder::spawn(...).expect(...)` 仍存在（`library_bridge.rs:2645`、`2757`），但不是启动 `Result` 的原 panic 点。判断：R-002 的主修复成立，UI 可见性和线程创建失败路径未被测试证明。

### R-003：静态引用环已解除，空闲 channel 回收测试有效；无响应时 Drop 仍可能卡死

- 初始 channel 与恢复 channel 的 `on_down` 都捕获 `Weak<ResilientCoreContext>`（`2597-2603`、`2673-2681`），消除了 `context → channel → callback → context` 强引用环。`ResilientLibraryChannel::drop` 设置 stop 并 `take()` 内部 channel（`2791-2800`）。
- 测试用真实 `cmd /c pause` 子进程，断言 context 的 weak 引用失效并用 PID 精确过滤 `tasklist`（`4499-4550`）；因此不会误匹配无关 PID。测试没有断言 `tasklist` 的 `output.status.success()`，且没有启动生产 heartbeat 线程；`weak_ctx.upgrade().is_none()` 不能代表生产 heartbeat 的 Arc 已同步释放（生产路径在 `main.rs:1356` 启动 heartbeat）。子进程检查本身是有意义的，但其辅助断言覆盖不完整。
- **未闭合的关闭风险**：`with_channel` 持有 `inner` mutex 调用整个 IPC（`2764-2775`）；IPC 响应使用无期限 `rx.recv()`（`library_bridge.rs:1277-1280`）。Drop 要等待同一 `inner` 锁（`2795`）；拿到后，`StdioLibraryChannel::drop` 还会先执行 `CloseHostSession` round trip，再发 shutdown/等待子进程（`1655-1679`），该 round trip 同样没有响应超时。sidecar 活着但无响应时，Drop 可以无限等待，5 秒 kill 逻辑到不了。普通 EOF 路径没有发现新的锁循环死锁，但无响应与在途调用可阻塞关闭；详见新 finding R-009。

### R-006：横幅中的“重试连接”按钮已移除，日志指引保留

- `AppShell.tsx:330-372` 只保留状态文案；R1 中的 `handleManualRetry` 与按钮已从 diff 删除。测试断言 fatal 横幅内无 button（`AppShell.lifecycle.test.tsx:110-125`），该断言真实有效。
- 后端 fatal 文案为“后端服务异常，自动重启失败，请检查服务日志”（`library_bridge.rs:2502-2505`、`2637-2641`），指向日志的指引存在。组件测试只断言文案前缀，没有断言“请检查服务日志”。
- 书架错误区仍可能独立显示“重试”按钮：`CORE_UNAVAILABLE` 标为 retryable，`BookshelfPage.tsx:303-319` 的按钮仅重试书架读取，不会重启 supervisor。它不是已删除的“重试连接”按钮，但 fatal 屏幕仍可能出现此上下文重试操作；当前测试只检查横幅子树、mock 也不返回 `CORE_UNAVAILABLE`，没有覆盖整屏 fatal 态。
- 判断：R-006 对原横幅按钮修复成立；若产品要求 fatal 整屏不出现任何重试操作，现有断言与实现范围不够。

## 3. R-004 / R-005 / R-007 修复确认

### R-004：故障态确实被观测，脚本仍有判定与计时缺陷

- `run-r004-timeline.ps1:47` 使用故障文案匹配；从 kill 时刻开始轮询，证据 `r004-20261018-082539/01-failure-banner.png` 实拍黄色后端故障横幅，`02-recovered-banner.png` 实拍恢复横幅。`trace.log` 记录 `failure_banner_ms=96`、`respawn_ms=631`、`recovered_banner_ms=926`，原始时间顺序也显示 UI_TEXT 在 RESPawn 之前。因此本轮 AC1 的“有界时间内显示故障”有直接桌面证据；AC2 成功恢复也有直接桌面证据。
- 但“+7ms 出现”来自 `ui-timeline.csv`，不等于实际观测时间：脚本在 `AllNames` UIA 查询前就取 `$el`（第 78-85 行），respawn 行还复用进程枚举前的 `$el`（第 89-91 行）。日志时间显示 kill 为 `08:25:41.392`、UI_TEXT 为 `08:25:41.481`，截图在 `08:25:41.583`；因此 +7ms 至少低估了 UIA 观测/截图耗时。summary 的 96ms/631ms 比 CSV 的 7ms/518ms 更接近真实观测时刻。
- 另 `A()` 只写 PASS/FAIL 文本（第 24-25 行），脚本结束时没有将失败断言转为非零退出码（第 101-108 行）。本次日志和截图明确是 PASS，单次结果仍可核验；但脚本失败时仍可能退出 0，不能作为 fail-closed 自动化 Gate。结论：旧的“把恢复文案当故障文案”已修复，R-004 的单次观测成立，脚本质量仍有 P2 遗留（R-012）。

### R-005：未修复，当前交付 head 与 pins 仍落后

- Task front matter 仍写 `delivery_head: eb62dbc7f`（`doc/tasks/P20-ISOLATION-1.md:17`）；Canonical Evidence 仍把测试、前端测试、构建产物和脚本 pin 到 `eb62dbc7f`（第 75-78 行）。但相应代码/测试修订在 `9d3924c05`，Handoff front matter 写的是 `delivery_head: 0e3b74dc0`（`doc/handoffs/P20-ISOLATION-1-antigravity.md:6`），仍比产品代码提交落后一版。
- `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P20-ISOLATION-1.md` 返回 **FAIL (7 errors, 3 warnings)**：4 个 Evidence class (`unit_test`、`component_test`、`build_artifact`、`test_script`) 不在检查器允许枚举内；3 个 `eb62dbc7f` commit pin 不包含所列文件。检查器只读，未修改工作区。
- 结论：R-005 未闭环。Task 最新 Review 指针、delivery head、evidence commit/class 必须由协调者修正；本 Review 按授权只写入 review 文件，没有改 Task。

### R-007：AC4 误标已纠正

- `doc/tasks/P20.md` 当前提交把 P20 AC4 保持为未勾选，并明确记载平均 36.0ms、p95 62.4ms、FPS/撕裂未测（`doc/tasks/P20.md:37`）；这纠正了将部分失败描述成整体通过的记录。R-007 修复成立。
- 但 P20 AC6 同行仍写 `fatal+手动重试`（`doc/tasks/P20.md:39`），与 R-006 删除横幅按钮后的当前实现不一致，属新的文档陈述过期，见 R-013。

## 4. 新发现与遗留 finding

| ID | 级别 | 文件/行 | 影响与证据 | 建议 |
|---|---|---|---|---|
| R-008 | P1 | `library_bridge.rs:2692-2753`, `1217-1280` | AC2 写明 sidecar“无响应或退出”须重启，但 heartbeat 只看 `is_down` 与 `Child::try_wait()`；进程存活但不处理 IPC 时 `try_wait()` 返回仍运行，读响应又无限 `recv()`，不会触发 restart 或 fatal。 | 给 IPC 心跳/请求增加有界超时，并把超时交给同一有界恢复状态机；增加挂起 sidecar 的故障注入证据。 |
| R-009 | P1 | `library_bridge.rs:1277-1280`, `1655-1683`, `2764-2800` | 无响应请求可一直占用 `inner`；Drop 等锁，或在 `CloseHostSession` 的无限等待处卡住，导致退出清理无法到达 5 秒 kill。 | 让请求和 shutdown round trip 有界；Drop 不能在无限等待的 IPC 上持锁销毁 channel。 |
| R-010 | P1 | `AppShell.lifecycle.test.tsx:128-218`; Task `doc/tasks/P20-ISOLATION-1.md:40` | 测试确实断言标题草稿跨两个合成 lifecycle 回调仍保留并可提交；但故障与恢复都是直接调用 mock listener，没有杀 sidecar，也没有覆盖 Task 明文要求的导入/编辑进行中注入。完整 AC3 未证实。 | 补符合 Task 原文的真实或可复现故障注入，或把未覆盖范围如实留为未通过。 |
| R-011 | P1 | Task `doc/tasks/P20-ISOLATION-1.md:41` | AC4 打勾，但括号明确“四页与冷启动端到端待交互式桌面复核”。本轮截图只见书架 shell；旧 `bundle-resource-hash.json` 来自此前 P20 Gate，不能证明当前 head 的冷启动/四页回归。AC4 当前证据不完整。 | 对当前构建复跑并保存冷启动、四页可达、bundle/resource 两处 hash 及原始日志；未完成前不要标 PASS。 |
| R-012 | P2 | `run-r004-timeline.ps1:24-25,78-103,108` | ASSERT 失败不影响进程退出码；CSV 的 `$el` 在 UIA/进程查询前取值，造成 +7ms/+518ms 低估。单次现有 trace 仍明确记录了真实失败横幅、恢复与重生。 | 失败时返回非零，并在查询结果取得后记录观测时间；保留 trace 与 metadata。 |
| R-013 | P2 | `doc/tasks/P20.md:39` | AC6 的当前实现说明仍称 `fatal+手动重试`，与 `AppShell.tsx` 已删除 fatal banner retry 不一致。 | 更新 AC6 说明，保留历史事实时明确标为历史状态。 |

## 5. 阻断项 / 遗留项

- 阻断批准：R-005 evidence pins/governance FAIL；R-008、R-009 的无响应与关闭路径；R-010 AC3 真实故障注入证据；R-011 AC4 当前 head 回归证据。
- R-003 的弱引用修复、R-001 的快速崩溃预算、R-006 横幅按钮移除本身成立；R-004 的单次截图/日志支持本次故障提示和恢复结果，但脚本需 R-012 修正后才可作为自动 Gate。
- R1 修复包中的 Rust `.meta.json` 与原始日志命令、cwd、exit_code 相符，日志为 5 个真实测试通过；前端 focused test 的 meta 与原始日志也相符，为 3 个测试通过，测试有实质断言。日志包含 React `act` 环境警告和重复 key 警告，退出码为 0，不构成测试失败。README 声称的全量 `npm test` 29 files/288 tests 没有对应原始日志与 metadata；Coordinator 所称当前构建通过也未在本次指定证据包中看到可核验的构建日志，故不作为本 Review 的已验证事实。
- 本轮变更确实触及 `doc/tasks/P20.md`（0e3b74d 修正 AC4 记录）、本 Task 与 Handoff；`doc/STATUS.md`、`doc/REBASELINE_PLAN.md` 未在 `13da2211a..HEAD` 中变更。`LibraryChannel` trait 增加了两个内部 Rust 方法；未发现 IPC 命令/事件 schema、Tauri ACL、依赖版本或既有数值阈值被改。新增默认稳定期为 30 秒，没有降低已有验收阈值。前端 `events.ts` 六个领域事件常量（`TaskFailed`、`RunPaused`、`RunCompleted`、`CurrentPageStepChanged`、`ExportProgressChanged`、`ReadingProgressChanged`）未改。

## 6. AC1 / AC2 / AC3 / AC4 独立判断

| AC | 判断 | 证据支持 | 证据不足 |
|---|---|---|---|
| AC1 用户可见提示 | **支持（针对运行中强杀场景）** | R004 桌面截图与 trace 看到明确“后端服务异常，正在尝试热重启...”文案；summary 记录约 96ms，远小于 5s。focused component test 也检查真实文案。 | CSV 的 +7ms 不是实际 UIA 观测时间；启动早期事件可能早于 WebView listener。不要宣称“7ms 实测”。 |
| AC2 重启与降级 | **部分支持** | 短命真实子进程循环断言三次后 fatal；桌面强杀实测自动重生并收到 recovered。 | 活进程无响应没有 IPC 超时/探测；没有当前 head 的真实连续 spawn 失败到 fatal 的端到端 UI 验收。 |
| AC3 状态保全 | **部分机制成立，AC 不通过** | 页面 Keep-Alive 与合成生命周期事件期间标题草稿保存、恢复后可提交有实际断言。 | 没有 sidecar 真实故障注入，也未覆盖 AC 指定的导入/编辑进行中行为；mock 不证明真实故障期间数据/操作状态保全。 |
| AC4 不回归 | **证据不足** | 源码保留四页容器；本轮桌面截图确认窗口与书架 shell 可达；代码 diff 未改 `core_service.exe` 来源，旧 Gate 的两个 hash 相等。 | 当前 head 没有冷启动耗时、四页导航和 bundle/resource 两处 hash 的新证据；Task 自己注明四页与冷启动待复核却勾选通过。 |

**建议下一步：** Coordinator 先修正 Task/Handoff 的 delivery head、Canonical Evidence class 与 pins；Owner Antigravity 处理 R-008/R-009 并补齐 AC3/AC4 所需证据，再由 Codex 对新 head 复审。

未执行：本轮未重跑产品测试、冷启动、四页导航或构建/hash；原因是只读复审并核验现存证据。主要风险是“无响应”场景目前既不能自动恢复，也可能阻塞应用关闭。
