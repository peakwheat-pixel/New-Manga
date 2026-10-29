# V11R-A-2 证据包：Run 控制服务层补齐（审计 P-02）

- Task：`V11R-A-2`（`doc/tasks/V11R-A-2.md`）
- Owner：`core-bridge`（DSH teammate）
- Worktree：`G:/CODEX/New Manga.workspace/worktrees/V11R-CORE-BRIDGE`，分支 `v11r/core-bridge`
- 基线 commit：`c73239999`（含 Lead R-08 契约修订的 main 已合入：`d96ff800f`）
- 交付 commit（本证据对应的代码 SHA）：`9709029d4822b97839f058404ca3174967699ca4`
- 契约：`doc/plan/V11R_AVALONIA_CONTRACT.md` §5.2（FROZEN，含 R-08 幂等键签名修订）
- 状态：AC1–AC7 已实现并有真实执行证据；Owner 未自审，待独立 Reviewer。

## 1. 交付内容

| 文件 | 变更 |
|---|---|
| `apps/desktop-avalonia/src/NewManga.App/Services/RunContracts.cs` | **新建**：`IRunController`（按 R-08 冻结签名）、`RunControlAction`、`RunStartRequest`、DTO（`RunStartInfo`/`RunControlInfo`/`RunSnapshotInfo`/`RunScopeInfo`/`RunTargetInfo`/`TaskProjectionInfo`/`RunStepFlowInfo`/`RunRowInfo`/`RunTaskInfo`/`RunStepInfo`/`RunCountsInfo`/`RunControlsInfo`）、total JSON 解析器、C056–C061 精确 wire payload 构造器。 |
| `apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs` | 实现 6 个 Run 方法，全部走**已注册命令**（`HostCommandDispatcher` → C056–C061，protocol minor 3）；R-08 幂等键本地拒绝；Run 写操作先过 Host data-root 策略（只读 → `HOST_READ_ONLY`）；Core typed 错误码保留到 `Snapshot.LastError`。 |
| `apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs` | `IHostController` 继承 `IRunController`（契约 §5.2 允许）；既有 36 方法签名/行为未改；`LastError` 文档延伸为 Run 读拒绝同样上报。 |
| `apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs` | 内存 Run 假实现：幂等键复用/冲突、冻结转换表、诚实空投影（计数 null 不伪造）、retry 仅 `completed_with_failures`。 |
| `apps/desktop-avalonia/src/NewManga.App/Shell/ShellSupport.cs` | `ShellCommandCatalog.WriteEvidence` 写前创建父目录（Lead 裁定 R-08 附带修复）。 |
| `apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs` | 追加 Run 脚本化双实现：记录请求、可排队 typed 结果、默认确定性状态机。 |
| `apps/desktop-avalonia/tests/NewManga.App.Tests/RunControllerTests.cs` | **新建** 13 条测试（见 §3）。 |
| `apps/desktop-avalonia/tests/NewManga.App.Tests/ShellEvidenceWriteTests.cs` | **新建** 1 条：父目录不存在时 WriteEvidence 可写。 |

未修改：Python Core、UI 视图/ViewModel、旧 `apps/desktop`、`NewManga.Host/**`。

## 2. AC 覆盖

| AC | 结论 | 证据 |
|---|---|---|
| AC1 `IRunController` + DTO + HostController 实现 + Null 假实现 | PASS | `RunContracts.cs`；`NullHostController.cs`；`IHostController.cs`（继承） |
| AC2 命令映射与 Registry 一致（C056–C061，minor 3） | PASS | `HostCommandRegistry.cs:147-152`；真实 wire `core-wire-run.ndjson`（全部 `version.minor=3`，请求键与 Dispatcher 特判一致） |
| AC3 幂等键：StartRun 必填 / RetryFailedTargets 必填 / ControlRun 仅 restart；缺失本地拒绝不静默生成 | PASS | 单测 `RunWrites_MissingMandatoryIdempotencyKey_AreRefusedLocally`；集成 `IDEMPOTENCY_KEY_REUSED` + 幂等复用（同 key 返回同 run_id） |
| AC4 `GetTaskProjection` 真实逐页/逐阶段状态，不伪造进度 | PASS | `RunCommands_StartSuccessfulRun_ProjectRealPerPageState_AndReuseKey`（真实 8 页：`rows=8`、`counts.total=8`、`step_flow` 非空）；wire 证据显示 pending 时 `rows=[]`、计划后 `rows=8`（原样透传，未补数） |
| AC5 错误映射 `INVALID_REQUEST/TARGET_NOT_FOUND/IDEMPOTENCY_KEY_REUSED/INVALID_RUN_TRANSITION` 保留 code | PASS | 集成测试 + wire：`EMPTY_TARGET_SELECTION→INVALID_REQUEST`、未知 run→`TARGET_NOT_FOUND`、同 key 异请求→`IDEMPOTENCY_KEY_REUSED`、非 paused/interrupted 的 continue→`INVALID_RUN_TRANSITION` |
| AC6 单测覆盖成功/非法转换/幂等复用/取消；`dotnet test` PASS | PASS | 13/13 Run 测试 + 全量 282 PASS/0 失败/0 跳过（§4） |
| AC7 `verification/V11R-A-2/` 证据 | PASS | 本目录 |

## 3. 测试（真实执行）

`RunControllerTests.cs` 13 条：

- `RunControllerNullFakeTests`（5）：确定性 run id / 幂等复用 / key 冲突；缺 scope/key 拒绝；冻结转换表（pending→stop=cancelled，pending→pause 非法，cancelled 再 stop 非法，restart 无 key 拒绝）；快照与投影 echo（targets 空、counts null 不伪造）；resume/retry 在无 Core 状态下 typed 拒绝。
- `RunControllerUiSeamTests`（2）：Fake 记录 StartRun/ControlRun 请求 + 脚本失败走 `SCRIPTED_FAILURE`；真实停止转换 pending→cancelled。
- `RunControllerHostLocalFailureTests`（3）：未启动 → `HOST_NOT_READY`（写与读一致）；缺 key/null 请求 → `INVALID_REQUEST`；取消 token → `CANCELLED`。
- `RunControllerHostIntegrationTests`（3，self-skip；本机全执行）：
  1. `RunCommands_MapCoreErrors_AndReuseIdempotencyKeys`（sidecar）：空章 scope → `INVALID_REQUEST`；5 个面未知 run → `TARGET_NOT_FOUND`；取消 → `CANCELLED`（零 wire）。
  2. `RunCommands_StartSuccessfulRun_ProjectRealPerPageState_AndReuseKey`（sidecar + BOOK-FIXTURE 副本）：真实 `StartRun`→pending；同 key 复用同 run_id；异请求同 key → `IDEMPOTENCY_KEY_REUSED`；GetRunSnapshot targets=8（全部 page）；GetTaskProjection 轮询到真实 `rows=8 / counts.total=8 / step_flow 非空`；`ControlRun(Resume)` → `INVALID_RUN_TRANSITION`。
  3. `RunCommands_WhenReadOnly_PublishHostReadOnly`（sidecar, parity=false）：StartRun/ControlRun/RetryFailedTargets → `HOST_READ_ONLY`；读仍可用且保留 Core `TARGET_NOT_FOUND`。

运行环境（既有仓库夹具约定）：
- `NEWMANGA_CORECLIENT_SIDECAR_DIR=G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1/sidecar-copy`
- `NEWMANGA_BOOK_FIXTURE_ROOT=G:/CODEX/New Manga.workspace/task-envs/BOOK-FIXTURE-1/isolated-data`（8 页真实书库；测试复制到一次性 root，按既有 BookFixture 规则跳过 derived/catalog/lock）

```
cd apps/desktop-avalonia
dotnet test tests/NewManga.App.Tests/NewManga.App.Tests.csproj --no-build \
  --filter "FullyQualifiedName~RunController" --logger "console;verbosity=minimal"
# 通过: 13, 跳过: 0, 总计: 13 → EXIT=0
```

## 4. 质量门（命令 / exit code / 结果）

| # | 命令（工作目录 `apps/desktop-avalonia`） | exit | 结果 | 证据 |
|---|---|---:|---|---|
| 1 | `dotnet build NewManga.sln -warnaserror` | 0 | 0 warning / 0 error | `build.log` |
| 2 | `dotnet test tests/NewManga.App.Tests/... --no-build` | 0 | 通过 161 / 失败 0 / 跳过 0 | `dotnet-test-app.log`, `trx/app.trx` |
| 3 | `dotnet test tests/NewManga.Host.Tests/... --no-build` | 0 | 通过 60 / 失败 0 / 跳过 0 | `dotnet-test-host.log`, `trx/host.trx` |
| 4 | `dotnet test tests/NewManga.CoreClient.Tests/... --no-build` | 0 | 通过 61 / 失败 0 / 跳过 0 | `dotnet-test-coreclient.log`, `trx/coreclient.trx` |
| 5 | `dotnet test NewManga.sln --no-build`（整解） | 0 | 通过 161 + 60 + 61 = 282 / 失败 0 / 跳过 0 | `dotnet-test-full.log` |

（App.Tests 从 A-1 的 147 增至 161：新增 Run 13 + Shell 1。）`ShellCommandCatalog.WriteEvidence` 修复后，`S3ShellTests.SettingsWiring` 在全新 `NEWMANGA_EVIDENCE_DIR` 下也不再失败（`ShellEvidenceWriteTests` 覆盖）。

## 5. 契约核实（Core 源码 + 真实 wire）

### 5.1 Core 源码（`c73239999`）

| 事实 | 引用 |
|---|---|
| `_RUN_COMMANDS` 六条全部路由到 `_dispatch_run_command`（protocol minor 记录来自请求 version） | `src/bootstrap/core_service.py:253-256`、`:3697-3703`、`:3256-3423` |
| StartRun：`command` 必须在 `COMMAND_CATALOG`；`idempotency_key` 必填；`overrides` 必须是对象；`overrides.provider_profiles` 需要 minor 7（`_P15_PROTOCOL_MINOR`，即“Core 2.6”）；scope 为 5 种冻结变体之一 | `core_service.py:3273-3296`、`:3129-3159`；`src/domain/tasks/models.py:66-87` |
| ControlRun：action ∈ {pause,continue,stop,restart,abandon}；restart 必填 `idempotency_key`，其它 action 传 key → INVALID_REQUEST | `core_service.py:3301-3321` |
| ControlRun 转换表：pause←running；continue←paused/interrupted；stop←pending/running/paused/blocked；restart←undisposed interrupted | `src/application/tasks/service.py:1008-1092` |
| ResumeBlockedRun：仅 blocked；不接受 idempotency_key | `core_service.py:3322-3326`；`service.py:981-985` |
| GetRunSnapshot：run_id → {run_id,command,scope,status,targets[]}（+source_run_id/retry_reason） | `core_service.py:3327-3350` |
| GetTaskProjection：`_task_projection_to_wire` 固定外形（step_flow/rows/tasks/counts/blocked_reasons/controls/extra） | `core_service.py:3173-3254`、`:3351-3354` |
| RetryFailedTargets：run_id + 必填 key；仅 completed_with_failures；无 failed 页→TARGET_NOT_FOUND | `core_service.py:3355-3364`；`service.py:1140-1186` |
| 错误映射：`EMPTY_TARGET_SELECTION→INVALID_REQUEST`、`TARGET_DELETED→TARGET_NOT_FOUND`，四类 code 原样返回，retryable=false | `core_service.py:3389-3411` |
| C# 注册：六条均 `CoreCommand` 对应 + **minor 3** | `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs:147-152` |
| C# Dispatcher 参数形状：StartRun(command,scope,overrides?,idempotency_key)；ControlRun(run_id,action,idempotency_key 可选)；Resume/Snapshot/Projection(run_id)；RetryFailed(run_id,idempotency_key)；StartRun 自动注入 Host 默认 provider_bindings | `HostCommandDispatcher.cs:198-220`、`:562-624` |

### 5.2 真实 wire（`core-wire-run-summary.json`；原始帧 `core-wire-run.ndjson`）

| host / req | 命令 | minor | 结果 |
|---|---|---:|---|
| v11r-a2-errors req-7 | StartRun（空章 scope） | 3 | `error.code=INVALID_REQUEST`（Core `EMPTY_TARGET_SELECTION` 映射） |
| v11r-a2-errors req-8..req-12 | GetRunSnapshot / GetTaskProjection / ControlRun(stop) / ResumeBlockedRun / RetryFailedTargets（missing-run） | 3 | 全部 `TARGET_NOT_FOUND` |
| v11r-a2-readonly req-4 | GetRunSnapshot（missing-run） | 3 | `TARGET_NOT_FOUND`（只读不影响读） |
| v11r-a2-run req-6 | StartRun(translate_all, chapter 8 页) | 3 | `{run_id:"run-da51…", status:"pending"}` |
| v11r-a2-run req-7 | 同 key 同请求 StartRun | 3 | 同 `run_id`（幂等复用） |
| v11r-a2-run req-8 | 同 key 不同 command | 3 | `IDEMPOTENCY_KEY_REUSED` |
| v11r-a2-run req-9 | GetRunSnapshot | 3 | `status:"pending"`，`targets=8`（全部 `page`） |
| v11r-a2-run req-10 / req-11 | GetTaskProjection 两次 | 3 | pending 时 `rows=[]`；计划后 `run_status:"running"`、`rows=8`、`counts={total:8, failed:4, waiting:4}`（真实执行失败，未补数） |
| v11r-a2-run req-12 | ControlRun(continue) | 3 | `INVALID_RUN_TRANSITION` |

## 6. 偏差 / 遗留

1. **R-08 已按 Lead 裁定实现**：`ControlRunAsync(runId, action, string? idempotencyKey = null, CancellationToken)`；`RetryFailedTargetsAsync(runId, string idempotencyKey, CancellationToken)`；StartRun 用 `RunStartRequest.IdempotencyKey`；缺失/空白 → 本地 `INVALID_REQUEST`，不生成。未加 `RestartRunAsync` 重载。
2. **`CancelExportAsync` 不在 `IRunController`**（Lead 采纳）：导出归导出域，沿用 `IHostController.CancelExportAsync`。
3. **Run 写的只读策略门（新增行为，请 Reviewer 关注）**：StartRun/ControlRun/ResumeBlockedRun/RetryFailedTargets 在 `HostRuntime.Policy.WritesAllowed == false` 时本地拒绝 `HOST_READ_ONLY`，与既有 region 写方法一致；读操作不受限。契约 §5.2 未明写，属安全默认，已在 `RunCommands_WhenReadOnly_PublishHostReadOnly` 固化。
4. **restart 的 `new_run_id/new_run_status` 未做集成实证**：需要“undisposed interrupted run”状态（进程重启/中断恢复），当前测试夹具无法在单一会话内制造；DTO/解析/载荷已实现并有单测覆盖映射，集成留待运行时恢复场景（`V11R-B-4` 前后可用真实中断 run 补齐）。
5. **Core `abandon` action 未暴露**：冻结枚举只有 4 个动作；`abandon` 仅用于中断处置，记录为 A-3 契约 GAP。
6. **集成测试使用既有 AC11 sidecar 副本 + BOOK-FIXTURE 数据根**（未从 `c73239999` 重建）；行为已逐条对照当前源码（§5.1）；证据不声称副本由本 SHA 构建。数据根均复制到临时目录，不写共享夹具。
7. **投影测试需轮询**：新 run 为 pending 时 Core 投影 `rows=[]`、`counts=0`（真实状态，非伪造），测试等待调度器计划（≤250ms 轮询、上限 10s）后再断言 8 行；已在 wire 证据中显示 pending→running 的真实转变。

## 7. 文件清单

```
verification/V11R-A-2/
  README.md                       （本文件）
  build.log                       dotnet build -warnaserror（0 warning/0 error, EXIT=0）
  dotnet-test-full.log            整解 dotnet test（282 PASS, EXIT=0）
  dotnet-test-run-controller.log   RunController + ShellEvidenceWrite 过滤（14 PASS = 13+1, EXIT=0）
  dotnet-test-app.log / -host.log / -coreclient.log
  trx/app.trx / host.trx / coreclient.trx / run-controller.trx
  core-wire-run.ndjson            真实 C056-C061 wire 帧（请求+配对响应）
  core-wire-run-summary.json      帧摘要（命令/minor/错误码/状态/targets/rows）
```
