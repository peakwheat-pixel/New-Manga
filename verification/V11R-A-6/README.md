# V11R-A-6 证据包：启动契约自检 + 测试基础设施（并行 SQLite 稳定）

- Task：`V11R-A-6`（A-5 遗留 #1 + 测试基础设施；Lead 2026-10-30 分配）
- Owner：`core-bridge`
- Worktree：`G:/CODEX/New Manga.workspace/worktrees/V11R-CORE-BRIDGE`，分支 `v11r/core-bridge`
- 交付 commit：`c9a5bb57430347a41e96709050e1243e9767708a`（实现）；证据 commit 见 Handoff
- 设计文档：`doc/plan/V11R_WRITE_POLICY.md` §6「启动自检」
- 状态：AC 全部实现并有真实执行证据；Owner 未自审。

## 1. 设计（先设计后实现）

Host 启动、`core.ping` 握手成功后执行一次契约自检（`NewManga.Host.StartupSelfCheck`）：

| 校验 | 失败码（typed） | 行为 |
|---|---|---|
| `status == ready` | `CORE_NOT_READY` | 只读 |
| `protocol_version.major == 2` | `PROTOCOL_VERSION_MISMATCH` | 只读 |
| `protocol_version.minor >= CoreProtocol.DefaultMinor`（=3；7/8/10 是逐命令请求级扩展，不由 ping 报告） | `CORE_PROTOCOL_MINOR_TOO_OLD` | 只读 |
| `capabilities` 含 `library.list_books` | `CORE_CAPABILITY_MISSING` | 只读 |

- 全部通过 → `SelfCheckStatus.Degraded`（**写入保持开启**）。这是诚实的降级：`core.ping` 不公开
  完整命令面枚举，启动时逐条探测 66 条命令会执行写命令，不可接受；`Detail`/host.log 明确记录
  "完整命令面比对未执行（follow-up）"，**不是**"永远通过"的空自检。
- 失败 → 新增 `HostMode.ReadOnlySelfCheckFailed`；`HostStartResult`：`Status=Ready`（sidecars 已启动，
  只读浏览可用）、`Mode=ReadOnlySelfCheckFailed`、`ErrorCode=<typed>`、`UserMessage=<中文原因>`；
  `DataRootPolicy.WritesAllowed=false`；写 API 抛 `ReadOnlyHostException(HOST_READ_ONLY)`；
  UI 通过 `HostViewSnapshot.WritesAllowed=false` + `ReadOnlyReason="只读（启动自检失败）"` +
  `ErrorCode` 读到原因。
- 探测本身失败（`SidecarException`/`CoreOperationException`/取消）→ 按 Lead 裁定保持 **ReadWrite**，
  记录 `Degraded` + `SELF_CHECK_PROBE_FAILED` + 诊断（启动握手已成功，一次自检请求失败不足以判定 Core 不可用）。
- 测试 seam：`HostOptions.StartupPingProbe`（null = 真实 `core.ping`）；`HostRuntime.SelfCheck` 暴露结果。

## 2. AC / 验证矩阵

| 项 | 结论 | 证据 |
|---|---|---|
| 自检通过（真实 sidecar）→ `Degraded` + `ReadWrite` + 真实建书成功 | PASS | `StartupSelfCheckTests.RealHost_PassesCheapChecks_AndStaysWritable`；`startup-self-check/pass.json`（`core_protocol=2.3`，created_book_id） |
| mock 主版本不匹配 → 只读 + typed error + 写拒绝 | PASS | `MajorMismatch_DowngradesToReadOnly_AndRefusesWrites`；`startup-self-check/protocol-mismatch.json`；`host-logs/self-check-protocol-mismatch/host.log`（`self-check status=Failed code=PROTOCOL_VERSION_MISMATCH`、`self-check blocked writes`） |
| mock 能力缺失 → 只读 + `CORE_CAPABILITY_MISSING` | PASS | `MissingCapability_DowngradesToReadOnly_AndRefusesWrites`；`startup-self-check/capability-missing.json` |
| 单元矩阵：ready/主版本/次版本/能力/探测失败 | PASS | `StartupSelfCheckTests`（10 条） |
| UI 可读：快照只读 + `ReadOnlyReason` + typed error | PASS | `StartupSelfCheckUiTests.SelfCheckFailure_IsVisibleInTheSnapshot`（App 控制器 + 真实 sidecar + 注入不匹配 ping） |
| 文档：写入策略补自检一节 | PASS | `doc/plan/V11R_WRITE_POLICY.md` §6（含 §6.5 follow-up） |
| 测试基础设施：不加 `-m:1` 并行稳定 | PASS | `test-infra/parallel-run-1..3.log`（见 §4） |

## 3. 质量门（命令 / exit code / 结果）

| # | 命令（工作目录 `apps/desktop-avalonia`） | exit | 结果 | 证据 |
|---|---|---:|---|---|
| 1 | `dotnet build NewManga.sln -warnaserror` | 0 | 0 warning / 0 error | `logs/build.log` |
| 2 | `dotnet test tests/NewManga.Host.Tests --filter StartupSelfCheck` | 0 | 10/10 PASS | `logs/dotnet-test-host-self-check.log`, `trx/host-self-check.trx` |
| 3 | `dotnet test tests/NewManga.App.Tests --filter StartupSelfCheckUi` | 0 | 1/1 PASS | `logs/dotnet-test-app-self-check-ui.log`, `trx/app-self-check-ui.trx` |
| 4 | `dotnet test NewManga.sln --no-build --settings tests/NewManga.runsettings` ×3 | 0/0/0 | 649 tests，**0 failed**，9 skipped（见 §4） | `test-infra/parallel-run-1..3.log` |

## 4. 测试基础设施：并行 SQLite 争用

事实核对：

- 三个 .NET 测试程序集**已**在 `AssemblyInfo.cs` 设置 `CollectionBehavior(DisableTestParallelization = true)`
  （程序集内部测试串行）；残留争用来自 `dotnet test <solution>` 让**多个程序集的测试宿主并行**，
  Windows 上各自创建临时 SQLite catalog 的 `-shm`/`-wal` 兄弟文件在刚删除的临时目录上短暂相撞。
- 修法：新增 `apps/desktop-avalonia/tests/NewManga.runsettings`（`RunConfiguration.MaxCpuCount=1`）
  串行化 VSTest 宿主；**不使用** `-m:1`（那只限制 MSBuild 并行，不控制测试宿主并行）。
  CI/Release workflow 已改为 `--settings apps/desktop-avalonia/tests/NewManga.runsettings`。
- 每个测试仍使用独立临时数据根（`HostFixture.NewDataRoot` / `RunFixture` / `tmp_path`），无共享夹具。

三次连续运行（**未加 `-m:1`**，真实 sidecar 环境，`--no-build`）：

| Run | ThemeEngine | DesignSystem | App | CoreClient | Host | 结果 |
|---|---:|---:|---:|---:|---:|---|
| 1 | 200 | 67 | 239 | 62/67（5 skip） | 72/76（4 skip） | 0 failed, EXIT 0 |
| 2 | 200 | 67 | 239 | 62/67（5 skip） | 72/76（4 skip） | 0 failed, EXIT 0 |
| 3 | 200 | 67 | 239 | 62/67（5 skip） | 72/76（4 skip） | 0 failed, EXIT 0 |

Skip 原因（环境性，显式跳过，非静默）：本机此轮未设置 `NEWMANGA_S4_REGION_FIXTURE` /
`NEWMANGA_MODELS_SIDECAR_DIR` 等可选 task-env 夹具（RunBindingFix models-build 2 条、S4 region 4 条等）；
设置对应夹具后由 `scripts/test.ps1` 全量执行（A-2/A-5 证据中已全绿）。

## 5. 偏差 / 遗留

1. **完整命令面比对未实现（有意）**：`core.ping` 无命令枚举；探测 66 条命令会执行写命令。当前通过时
   为 `Degraded` 并记录缺口。Follow-up：Core 在 `core.ping` 暴露 `command_surface_sha256` 或命令名列表
   （归属 core-writer / V11R-F0-1 后续）后升级为真正集合比对并置 `Passed`。
2. **探测失败保持 ReadWrite**：Lead 明确裁定的降级路径（`SELF_CHECK_PROBE_FAILED` 可见）；若后续要求
   探测失败也降只读，只需把该分支改为 `Failed`（单点改动，测试已覆盖 Degraded 语义）。
3. **次版本校验用 base minor（3）**：Core 报告的 `protocol_version.minor` 是基础面；7/8/10 是逐命令
   请求级扩展（由 parity 测试与 dispatcher 覆盖），不纳入启动自检，避免误报只读。
4. 既有 `--parity=false` / 旧壳共存只读优先级不变；自检只在 Host 决定 ReadWrite 后运行（只读场景不覆盖）。

## 6. 文件清单

```
apps/desktop-avalonia/src/NewManga.Host/StartupSelfCheck.cs   （新增：自检逻辑/结果/探测失败语义）
apps/desktop-avalonia/src/NewManga.Host/Coexistence.cs        （+ReadOnlySelfCheckFailed + UI 文案）
apps/desktop-avalonia/src/NewManga.Host/HostOptions.cs        （+StartupPingProbe 测试 seam）
apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs        （+SelfCheck、握手后执行、失败降只读）
apps/desktop-avalonia/tests/NewManga.Host.Tests/StartupSelfCheckTests.cs （新增 10 条）
apps/desktop-avalonia/tests/NewManga.App.Tests/StartupSelfCheckUiTests.cs （新增 1 条）
apps/desktop-avalonia/tests/NewManga.runsettings              （新增：MaxCpuCount=1）
doc/plan/V11R_WRITE_POLICY.md                                 （§6 启动自检）
.github/workflows/ci.yml / build-release.yml                  （--settings 串行化）
verification/V11R-A-6/
  README.md（本文件）
  logs/build.log, logs/dotnet-test-*.log, trx/*.trx
  startup-self-check/{pass,protocol-mismatch,capability-missing}.json
  host-logs/self-check-*/host.log + wire NDJSON（真实 Core 帧）
  test-infra/parallel-run-1..3.log（3×649 tests，0 failed，无 -m:1）
```
