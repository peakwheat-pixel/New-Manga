---
task_id: CORE-PIPE-EXCLUSIVE-1
reviewer: review-pipe-exclusive（DSH 派发的独立上下文子 agent；父会话 lead）
reviewer_kind: subagent
author: DSH（被审提交 065b9990fbb7）
base_commit: 0fb8abdc4
reviewed_head: 065b9990fbb7149f475e17c52d345a1f0ce2017c
decision: approved
verdict: ACCEPT_WITH_LIMITATIONS
---

# Review r1：CORE-PIPE-EXCLUSIVE-1（E-6 / P1 管道响应错配）

## 0. 审查者、来源与被审对象

- **审查者**：`review-pipe-exclusive`，DSH 派发的**独立上下文子 agent**（父会话 `lead`），
  **未参与**该 Task 的实现、诊断或返修；本轮只读复核。
- **被审 head**：`065b9990fbb7149f475e17c52d345a1f0ce2017c`
  （`fix(core-client): 修复 core_service 管道响应错配（E-6 / P1）—— 全局独占 + request_id 校验`），
  基线 `0fb8abdc4f957bf8c8d4b3cf42eddd3a5969b4de`。
- **被审改动**：`apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs`（+50 行）、
  新增 `tests/NewManga.CoreClient.Tests/Commands/PipeResponsePairingTests.cs`（115 行）、
  卡面/证据/指针文档。`git diff 0fb8abdc4..HEAD --name-status` 显示测试项目**只有新增文件**，
  没有任何既有测试文件被修改（§6）。
- **只读约束**：除本报告外未写入仓库。实验用的临时改动全部用 `git checkout -- <file>` 还原；
  还原后实测 `git status --short` 为空（§5），`git rev-parse HEAD` 仍为被审 head。
  写入本报告后 `git status --short` 只应出现本文件（未跟踪）。

## 1. Verdict

**ACCEPT_WITH_LIMITATIONS。**

修复方向正确、生产调用路径确实被覆盖、无死锁/重入、判别测试在回退时**确实变红**（我亲自复现），
AC5/AC6 的数字也可复现。但存在 5 项 P2 限制（其中"AC3 零测试覆盖"是我用实验证实的实质缺口），
以及 3 项 P3 文档/口径问题。P0/P1：**无**。

## 2. 逐 AC 判定

| AC | 判定 | 依据 |
|---|---|---|
| **AC1** 判别测试（先写、必须先红、断言 request_id 相等） | **PARTIAL** | 测试存在且在回退时变红（§5 实验 B）；但断言对象是 `result` 的 JSON **形状**（`PipeResponsePairingTests.cs:66-86`），不是卡面要求的"每个响应的 `request_id` 等于其请求的 id"（`doc/tasks/CORE-PIPE-EXCLUSIVE-1.md:64-66`）。"先写先红"的证据只有 `verification/CORE-PIPE-EXCLUSIVE-1/four-pieces.log:16` 的一行手写记录（无原始测试输出/trx），无法独立复核那次运行。见 R-006。 |
| **AC2** 底层独占覆盖所有调用路径 | **MET（生产路径）/ PARTIAL（字面"所有"）** | `SendAsync`（`CoreServiceClient.cs:2416-2444`）与 `SendHostControlAsync`（`:696-723`）各持 `_pipeGate` 覆盖整周期；原先绕过 Host gate 的 `SourceScanScheduler.cs:2415`、`SourceOperationCoordinator.cs:219` 都经 `ListSourceScanTargetsAsync`→`SendAsync` ⇒ 已在锁内。但公开 `SendRawAsync`（`:2381-2387`）在锁外，且独占**不在** `SidecarProcess.ExchangeAsync` 内部 ⇒ 与卡面"最底层"表述有偏差。见 R-004、§4。 |
| **AC3** request_id 校验（typed error，不得静默接受） | **PARTIAL** | 实现为 `SidecarException(MalformedResponse)`（`:2392-2403`），但 `response.RequestId` 为 **null 时直接放过**（`if (response.RequestId is { } actual && ...)`）⇒ fail-open。**且该功能零测试覆盖**（§5 实验 D 证明删掉校验测试仍绿）。见 R-001、R-005。 |
| **AC4** 判别力实测（回退→红→还原→绿，须记录） | **MET** | 我把 `_pipeGate` 改为 `new(8, 8)` 后测试变红，`git checkout --` 还原后转绿（§5 实验 A–C）。注意：红的原因是 transport 层 `InvalidOperationException`，**不是** request_id 校验先抓住错配；卡面括号已允许"或测试变红"。 |
| **AC5** 带新 sidecar 失败数下降 | **MET（数字可复现）** | CoreClient **209/4/0/213**（与 `verification/.../README.md:48` 完全一致，4 个失败即 §5.1 四个 Frozen Core 前提测试）；Host 两次全量 **349/2/44/395** 与 **348/3/44/395**，三个残留全部落在 README §5.2 名单内 ⇒ 无新增失败。但"fail 9→2"不是稳定定值（见 R-008）。也确认**没有**通过改测试 gate 达成绩效：`HostRuntime._readerIoGate` 与全部既有测试均未被修改。 |
| **AC6** 不回归（三项目 0 failed，不新增 skip、不放宽断言） | **MET** | 无夹具实测：App **950/0/11/961**、Host **321/0/74/395**（3 次中 2 次；另 1 次出现 1 个 flaky 失败，名称因输出截断未捕获，见 §6 注）、CoreClient **186/0/27/213**。skip 26→27 已核实为新增 `[SidecarFact]` 测试（`PipeResponsePairingTests` 在无夹具时 SKIP，我实测到该 SKIP 行），既有 186 pass 未变；diff 无任何既有断言改动。 |

## 3. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R-001 | P2 | `CoreServiceClient.cs:2392-2403`（`EnsureResponseBelongsToRequest`） | `response.RequestId == null` 时不报错。`CoreProtocol.IsEventFrame`（`CoreProtocol.cs:47-49`）只跳过"含 `event_type` 且不含 `request_id`"的帧；一个既无 `event_type` 又无 `request_id` 的帧不会被跳过，却会被当作本命令响应接受 ⇒ E-6 这类"拿错响应"在"Core 不回 request_id"的变体下仍然静默通过。 | 代码路径；契约 `doc/contracts/V11R_COMMAND_CONTRACT_V1.md:35` 规定**响应**含 `request_id`、`:36` 规定**事件**无 `request_id` ⇒ 无 request_id 的非事件帧属畸形，按契约应拒绝。 | 非事件帧 request_id 为 null 时同样抛 `SidecarException(MalformedResponse)`（fail-closed）。 | open |
| R-002 | P2 | `CoreServiceClient.cs:2432-2444`、`:710-723`；`SidecarProcess.cs:219/279`（`_poisoned` 只在超时置位） | 一旦发生 request_id 错配，`EnsureResponseBelongsToRequest` 抛错但**不**置 poison、不排空、不重启：真实响应仍留在流里，其后每个请求读到的都是"上一个请求的响应"⇒ 每次都 mismatch ⇒ core 通道**永久失效直到应用重启**。Host 侧 `Fail()`（`HostRuntime.cs:1672`）只在启动期标记，运行期不重建 client。 | 代码推断（未构造错配 sidecar 实验，见 §7）；`_poisoned` 设置点只有 `SidecarProcess.cs:219`（读超时）与 `:279`（事件帧读超时）。 | 把 mismatch 视为致命传输错误（poison + 杀进程，由 Host 重建），或做有界 drain-to-resync；至少上报 typed "管道已失步"并拒绝继续接受命令。 | open |
| R-003 | P2 | `Bridge/HostBridgeClient.cs:267-272`、`:274-293`；`ParseResponse:297-330` | `HostBridgeClient` 是**同一缺陷类**的未堵窗口，只是换了管道（`host_bridge.exe`）：`_process.ExchangeAsync` 两处调用**无任何锁**，`NextRequestId()`（`:295`）生成的 `id` 在 `ParseResponse` 中**从未比对**（只读 `error`/`result`）。目前生产调用点只有 `HostRuntime.ReadPageImageAsync`（`:1018-1075`，持 `_readerIoGate`）与 `DisposeAsync`（`:1138/1689`）；一旦有新调用者绕过 `_readerIoGate`，`issue`/`resolve` 交叉会返回**错误授权/错误页面字节**且无法被发现——与 E-6 完全同型。 | 代码路径；`grep ExchangeAsync` 全仓仅 5 个调用点（§4）。另：`verification/.../README.md:86` 称"`ExchangeAsync` 本身已由本卡的锁保护"**与代码不符**（锁在 `CoreServiceClient`，不在 `SidecarProcess`）。 | `HostBridgeClient` 加同型 `_pipeGate` 并在 `ParseResponse` 校验 `id`；或抽公共 `SidecarProcess.RunExclusiveAsync(Func<Task<T>>)` 让独占成为传输层职责。 | open |
| R-004 | P2 | `CoreServiceClient.cs:2380-2387`（`SendRawAsync`） | 公开方法直接 `_process.ExchangeAsync`，**没有** `_pipeGate`。一旦与任一命令并发（或未来被生产代码使用），即可 desync 管道，并在 R-002 机制下把整条 core 通道打死。 | 代码路径；唯一调用者是测试 `tests/.../CoreServiceIntegrationTests.cs:117`（"Raw 转义/负向"用例）。 | 让 `SendRawAsync` 走同一 `_pipeGate`（最省事），或降为 `internal` 并注明测试专用。 | open |
| R-005 | P2 | `PipeResponsePairingTests.cs` 全文；`CoreServiceClient.cs:711/2433` | **AC3 的 request_id 校验零测试覆盖**：我删掉两处 `EnsureResponseBelongsToRequest` 调用（gate 保持 `(1,1)`）后，判别测试**仍然通过**（§5 实验 D）。删掉 AC3 实现不会有任何测试变红。 | 实验 D（PASS 1/0/0，434 ms）；全仓 grep 无断言 mismatch / "another command's response" 的测试。 | 新增确定性单测：用可注入可执行文件（`SidecarFixture.CreateCoreOptions(..., executablePath)` 已支持）或把校验提为可单测的静态纯函数，构造 `request_id` 不等/缺失的帧，断言 `SidecarException(MalformedResponse)`。 | open |
| R-006 | P3 | `PipeResponsePairingTests.cs:42-61`、`:66-86` | 断言的是 result 的**形状**而非 request_id 相等；且没有 barrier/观测点断言"确实有 ≥2 个请求同时在途"。未来 runtime 若让提交实际串行化，测试会**静默失去判别力**（今天有判别力，已实测）。 | 代码；§5 实验 B。 | 直接断言 `response.RequestId` 等于请求 id（让 `SendAsync` 暴露 id 或改在更底层断言）；加"并发实际发生"的观测。 | open |
| R-007 | P3 | `CoreServiceClient.cs:2416`、`:696` | 全局单锁无"获取超时"：`WaitAsync(cancellationToken)` 只受调用方 token 约束，命令自身的 `timeout` 在**拿到锁之后**才开始计时。一条挂住的命令（默认 `RequestTimeout` 30s，`:347`；夹具 60s）会阻塞全部 core 命令（含 host-control 与 `core.ping`）；Host readers 还持 `_readerIoGate` 等待，形成叠加延迟；`ShutdownAsync`（5s 预算，`:2599`）也可能远超预算。 | 代码推断，**未测量**（无基准数据）。 | gate 获取纳入同一 timeout 预算；或给 host-control/健康检查单独优先通道；至少登记为已知可用性取舍。 | open |
| R-008 | P3 | `doc/tasks/CORE-PIPE-EXCLUSIVE-1.md:64-98,108-110`；`verification/CORE-PIPE-EXCLUSIVE-1/README.md:48,69-75,86`；`doc/TASK_LEDGER.md` | 文档未同步/自相矛盾：① 卡面 AC1–AC6 全部未勾选、测试要求表 5 行全 `NOT_RUN`、"Handoff/Review/实际测试：尚无"，与证据 README 的实际结果冲突；② README:48 写 `Host 349/2/44/395（fail 9→2）`，但同文件 :69-75 列 **3** 个残留失败、commit message 亦写"Host 剩余 3 个"，2 与 3 矛盾；③ README:86 关于 `ExchangeAsync` 已受保护的表述与代码不符（见 R-003）；④ `TASK_LEDGER` 仍把 `SIDECAR-REBUILD-1` 记 `in_progress`，而 Plan/STATUS 已标 `done`。 | 文档比对 + 我的两次 Host 全量（349/2 与 348/3）。 | 实现者补齐卡面 AC/测试表/Handoff；AC5 改写成区间并注明 3 个残留为 flaky；修正 README:86 表述；对齐 LEDGER。 | open |

**其他观察（不计 finding）**：`_pipeGate`/`_sessionGate` 均未在 `DisposeAsync` 中释放（SemaphoreSlim 未创建 wait handle，无实际影响）；
`SidecarProcess.StopAsync`（`:316/328`）关闭 `_stdin` 与在途请求无协调（既有问题，非本卡引入）；
Host `_readerIoGate` + client `_pipeGate` 两层串行化冗余但无死锁（§4）。

## 4. `_pipeGate` 覆盖点清单（全部会碰 `_process` stdin/stdout 的路径）

| # | 调用点 | 方法 | 在锁内？ | 说明 |
|---|---|---|---|---|
| 1 | `CoreServiceClient.cs:700` | `SendHostControlAsync` → `ExchangeAsync` | **是**（`:696` 取 / `:722` 释） | host-control 通道；`OpenHostSessionAsync:617` 亦经此 |
| 2 | `CoreServiceClient.cs:706` | `SendHostControlAsync` → `ReadNextResponseLineAsync` | **是** | 事件帧跳过循环（同一条 stream） |
| 3 | `CoreServiceClient.cs:2419` | `SendAsync` → `ExchangeAsync` | **是**（`:2416` 取 / `:2443` 释） | 所有 app 通道命令：`CoreServiceClient` 内约 50 个公开方法 |
| 4 | `CoreServiceClient.cs:2428` | `SendAsync` → `ReadNextResponseLineAsync` | **是** | 事件帧跳过循环 |
| 5 | `CoreServiceClient.cs:2384` | `SendRawAsync` → `ExchangeAsync` | **否** | 公开 raw 钩子；仅测试调用（R-004） |
| 6 | `HostBridgeClient.cs:291` | `HostBridgeClient.SendAsync` → `ExchangeAsync` | **否** | 另一条管道（`host_bridge.exe`），无锁、无 id 校验（R-003） |
| 7 | `HostBridgeClient.cs:269` | `HostBridgeClient.SendRawAsync` → `ExchangeAsync` | **否** | 同上 |
| 8 | `SidecarProcess.cs:186 / :259` | `ExchangeAsync` / `ReadNextResponseLineAsync` **自身** | 不设锁 | 独占完全由调用方负责 ⇒ 任何未来直接调用的代码天然在锁外（本类缺陷复发的结构原因） |
| 9 | `SidecarProcess.cs:328` | `StopAsync` → `_stdin.Close()` | 不受 gate 协调 | dispose 与在途请求的竞态（既有） |

**生产调用者是否全覆盖**：`HostRuntime.cs:306/1316/1335/1405/2034/2131`、`HostGrantCoordinator.cs:135/224/271`、
`SourceScanScheduler.cs:2415`、`SourceOperationCoordinator.cs:219`、`SourceReadCoordinator.cs:814`、
`CoreCredentialBridge.cs:34/80/108`、`HostCommandDispatcher.cs:305` 全部经 `SendAsync` ⇒ **都在锁内**。
原先"绕过 `_readerIoGate`"的两个后台点（Scheduler/Coordinator）因此被底层 gate 兜住。

**死锁/重入判定**：
- `_sessionGate` 只在 `OpenHostSessionAsync`（`:607/:645`）使用，顺序 **S→P**；
  `SendAsync`/`SendHostControlAsync` 内部**不碰** `_sessionGate` ⇒ 不存在 **P→S 反序**，无 ABBA 死锁。
- gate 内不执行任何用户回调：payload writer 在 `WaitAsync` **之前**执行（`:669-693` / `:2413`），
  gate 内只有 transport + `CoreProtocol.Parse` + 抛错 ⇒ 非重入的 `SemaphoreSlim` 无重入死锁。
- `WaitAsync` 在 `try` **之外** ⇒ 取消不会释放未获取的锁；`finally` 保证异常路径释放。
- 结论：**未发现死锁或重入风险**；`_readerIoGate`（Host）与 `_pipeGate`（client）之间无反向持有路径。

## 5. 判别力实验记录（我亲自执行）

环境：Windows / pwsh / `.NET 10.0.401` / `-c Debug`；夹具
`NEWMANGA_CORECLIENT_SIDECAR_DIR=G:\CODEX\New Manga\apps\desktop-avalonia\build\sidecar\core-sidecar\core-sidecar`。
命令统一为：

```
cd apps/desktop-avalonia
dotnet test tests/NewManga.CoreClient.Tests/NewManga.CoreClient.Tests.csproj -c Debug \
  --filter "FullyQualifiedName~PipeResponsePairingTests" --nologo
```

| 实验 | 做了什么 | 结果 | 是否还原 |
|---|---|---|---|
| **A 基线** | 直接跑 | **PASS** `失败:0，通过:1，跳过:0，总计:1，441 ms`，exit 0 | — |
| **B 回退（gate 8）** | `_pipeGate = new(1,1)` → `new(8,8)`（`:426`） | **FAIL**，437 ms，exit 1。错误：`SidecarException [ProcessExited] core_service: process exited`，`Inner: System.InvalidOperationException: The stream is currently in use by a previous operation on the stream.`（`StreamWriter.ThrowAsyncIOInProgress` → `SidecarProcess.ExchangeAsync:202` → `SendAsync:2419`）。**注意：红的原因是传输层并发写，不是 request_id 校验命中。** | `git checkout -- apps/.../CoreServiceClient.cs` |
| **C 还原后转绿** | 还原 `(1,1)` 再跑 | **PASS** `失败:0，通过:1，总计:1，449 ms`，exit 0 | 已还原 |
| **D 去校验（gate 保持 1,1）** | 删掉 `:711` 与 `:2433` 两处 `EnsureResponseBelongsToRequest(...)` 调用后跑 | **PASS** `失败:0，通过:1，总计:1，434 ms`，exit 0 ⇒ **判别测试抓不住 AC3 被删除**（R-005 的实证） | `git checkout --` 还原 |
| **E 还原确认** | `git checkout --`，检查 `_pipeGate = new(1, 1)` | `git status --short` **为空**；`git rev-parse HEAD` = `065b9990...`（未变） | ✅ 已完成 |

**结论**：测试对"独占被放宽"**确有判别力**（B 红 / C 绿）；但对"request_id 校验被删除"**没有**判别力（D 绿）。
另外，B 的失败形态是 transport 异常，说明该测试实际固定的是"单请求在途"，而不是卡面文字要求的
"响应 request_id 与请求一致"——后者在 gate 生效时**永远不会被触发**。

## 6. 回归面实测

| 场景 | 命令（省略公共前缀 `dotnet test <proj> -c Debug --nologo`） | 结果 | 与声明对比 |
|---|---|---|---|
| CoreClient 无夹具 | `tests/NewManga.CoreClient.Tests/...` | **186 pass / 0 fail / 27 skip / 213**，21 s | 与 README 一致；skip 26→27 = 新增 `[SidecarFact]`（实测到 `PipeResponsePairingTests ... [SKIP]` 行） |
| Host 无夹具（3 次） | `tests/NewManga.Host.Tests/...` | 320/1/74/395；321/0/74/395；321/0/74/395（各 6 s） | 2/3 次与声明一致；1 次出现 1 个 flaky 失败（`Select-Object -Last 6` 截断，**名称未捕获**，无法归因；未见与本改动相关的路径） |
| App 无夹具 | `tests/NewManga.App.Tests/...` | **950 / 0 / 11 / 961**，4 m 42 s | 与 AC6 一致 |
| CoreClient 有夹具 | 设 `NEWMANGA_CORECLIENT_SIDECAR_DIR` | **209 / 4 / 0 / 213**，46 s；4 个 = README §5.1 名单（`Fea12Core_DeleteTrashCapabilityProbe_OldCoreFailsClosedBeforeAnyCommandFrame`、`Fea12NewCommands_FrozenCoreFailsClosedWithTypedError`、`B2Commands_ExecuteAgainstFrozenCore`、`B1Commands_ExecuteAgainstFrozenCore`） | 与 AC5 声明**完全一致** |
| Host 有夹具（2 次） | 同上 | **348/3/44/395**（2×GrantIssuer + Fea11Watch）；**349/2/44/395**（2×GrantIssuer） | 与 AC5 声明一致（349/2）；三个残留全在 README §5.2 名单 ⇒ 无新增失败 |
| 残留类聚焦重跑 | `--filter "FullyQualifiedName~GrantIssuerTests|FullyQualifiedName~Fea11WatchHostRuntimeTests"` | 4 pass / 1 fail（仅 Fea11Watch `SOURCE_REGISTRY_BUSY`） | ⇒ 三个残留测试**顺序/状态敏感（flaky）**，单独跑时两个 GrantIssuer 通过 |

**断言是否被放宽**：`git diff 0fb8abdc4..HEAD --name-status` 的测试侧只有
`A apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/PipeResponsePairingTests.cs`，
**没有任何既有测试文件被修改**；`git diff 0fb8abdc4..HEAD -- tests` 全量即该新文件的 +115 行。
`HostRuntime._readerIoGate`（`HostRuntime.cs:34` 等 40 余处）也未被触碰。

## 7. 我没有验证的面

1. **未在 GUI/阅读器实机**复现"后台扫描时章节列表变空 → 修复后恢复"；只跑了测试。
2. **未构造"错配 sidecar"**验证 R-002（错配后是否真的 off-by-one、是否需要重启）；这是代码推断。
3. **未测量** R-007 的延迟/head-of-line 阻塞（没有基准数据，也没有并发压测）。
4. **未对 `HostBridgeClient` 做并发实验**（无现成测试；加测试会改动仓库，超出只读范围）。
5. **未切到基线 `0fb8abdc4` 跑对照**（只读约束下不切 commit）。"修复前失败"用 `gate=8` 等价实验证明；
   严格意义上这不是同一构建。
6. **未验证 Python Core 侧**是否绝对串行写 stdout、是否永不复用/遗漏 `request_id`（不改 Python）。
7. **未跑其余测试项目**（Appearance / ApplicationCore / DesignSystem / Presentation / ThemeEngine）——
   AC6 只要求 App/Host/CoreClient 三项，且这些项目不引用被改源码路径。

## 8. 明确回答

**这个 P1 是否真的修好了？**
**核心管道上：是。** `core_service` 这条 stdin/stdout 管道的"两个命令同时在途"窗口，已由
`SendAsync`/`SendHostControlAsync` 覆盖**整周期**（写 + 读 + 事件帧跳过 + 解析）的 `_pipeGate` 关闭；
原先绕过 Host `_readerIoGate` 的两个后台调用点（`SourceScanScheduler.cs:2415`、`SourceOperationCoordinator.cs:219`）
现在都经 `SendAsync` 在锁内；无死锁/重入；判别测试在回退时**确实变红**（实测）。E-6 的
"`list_chapters` 拿到 `source_list_scan_targets` 响应 ⇒ 静默空列表"这条路径已被从根上堵住。

**还有没有同一类窗口未堵？有 4 处：**
1. **`host_bridge` 管道**（`HostBridgeClient`）：无锁 + `ParseResponse` 完全不校验 `id` ⇒ 同型错配在
   资源通道可返回**错误的授权/页面字节**。目前只靠 Host `_readerIoGate` 事实性串行化，属于"下一个人
   加个调用点就复发"的结构性风险（R-003）。
2. **公开 `SendRawAsync`**（`CoreServiceClient.cs:2380`）：锁外；今天只有测试用，但是可被生产代码误用（R-004）。
3. **独占不在 `SidecarProcess` 内部**：任何未来直接调 `_process.ExchangeAsync` 的代码天然在锁外。
   这是本类缺陷能复发的根本原因，建议把独占下沉到传输层（R-003 建议）。
4. **无 `request_id` 的响应帧**：校验 fail-open，该变体下错配仍会被静默接受（R-001）。
5. 附带风险：错配命中后**无自愈**（R-002），会把"偶发静默错误"变成"整条通道失效直到重启"；
   加上 AC3 无测试（R-005），这条防线目前既没有回归保护，也不具备恢复策略。

**建议处置**：可交 DSH 集成（无 P0/P1）；R-001/R-002/R-003/R-004/R-005 建议在本卡关闭前至少
登记为后续 Task（管道独占下沉 + `HostBridgeClient` 同型修复 + request_id 校验单测），
R-008 的卡面/证据同步由实现者在集成前补齐。
