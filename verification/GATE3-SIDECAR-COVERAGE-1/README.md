# GATE3-SIDECAR-COVERAGE-1 证据

卡面：`doc/tasks/GATE3-SIDECAR-COVERAGE-1.md`。基线 `766719dcc`。

## 1. 实测数字

**环境**：`NEWMANGA_CORECLIENT_SIDECAR_DIR=G:\CODEX\New Manga\apps\desktop-avalonia\build\sidecar\core-sidecar\core-sidecar`
（`SIDECAR-REBUILD-1` 产物；`core_service.exe` 400,098 B / sha256 `60508811…52ee`）。

| 运行 | 结果 | 耗时 |
|---|---|---|
| **App.Tests 带 sidecar** | **957 passed / 0 failed / 4 skipped / 961** | **5m10s** |
| App.Tests 无夹具 | 950 passed / 0 failed / 11 skipped / 961 | ~1-2 min |

⇒ **skip 11 → 4，pass 950 → 957，0 failed**。

## 2. 转绿的 7 个测试（`FullyQualifiedName`，已实测 7 passed / 0 skipped）

用"无夹具 11 个 skip"与"带夹具 4 个 skip"的**差集**确定，然后用
`--filter "FullyQualifiedName~HostIntegrationTests|FullyQualifiedName~WritePolicyUi|FullyQualifiedName~StartupSelfCheck"`
复跑，得到 **`已通过! 失败: 0，通过: 7，已跳过: 0，总计: 7`**：

1. `NewManga.App.Tests.StartupSelfCheckUiTests.SelfCheckFailure_IsVisibleInTheSnapshot`
2. `NewManga.App.Tests.RunControllerHostIntegrationTests.RunCommands_WhenReadOnly_PublishHostReadOnly`
3. `NewManga.App.Tests.RunControllerHostIntegrationTests.RunCommands_StartSuccessfulRun_ProjectRealPerPageState_AndReuseKey`
4. `NewManga.App.Tests.RunControllerHostIntegrationTests.RunCommands_MapCoreErrors_AndReuseIdempotencyKeys`
5. `NewManga.App.Tests.WritePolicyUiIntegrationTests.DefaultController_IsWritable_AndParityFalse_IsReadOnlyWithReason`
6. `NewManga.App.Tests.CreateChapterHostIntegrationTests.HostController_CreateChapter_SucceedsThenMapsCoreFailures`
7. `NewManga.App.Tests.CreateChapterHostIntegrationTests.HostController_CreateChapter_WhenReadOnly_PublishesHostReadOnly`

## 3. 剩余 4 个 App skip（全部 opt-in gated，**不是** sidecar 缺失）

| 测试 | 为何仍 skip |
|---|---|
| `PerformanceBaselineTests.Gated_HotSwitch_UiThreadSchedulingGapStaysWithinThePerfGateBudget` | 性能门控，需显式 opt-in（`Gated_` 前缀即门控标记） |
| `Fea07Residual3CrashTests.Park_ProductionSwitchStopsBetweenPersistedTargetAndJournalCommit` | 崩溃注入需专门 harness |
| `Fea07Residual3CrashTests.Recover_NewProcessRollsBackAndAdoptsTheLatestProtectedState` | 同上 |
| `StartupDiagnosticsTests.RealProcessLaunchMatrix_ExitZeroAndDiagnosableStartupLog` | 真实进程启动矩阵，需 opt-in 环境 |

**这 4 个在无夹具与带夹具时都 skip**（差集证明），所以它们与 sidecar 无关。

## 4. 对条件 3 矩阵的更新

### 4.1 "书架只读"格：⚠️ → ✅

原 ⚠️ 理由：「`[WritePolicySidecarFact]` 的 `WritePolicyUiTests` 覆盖只读写拒绝 → 需 sidecar，本环境 NOT_RUN」。

**现在有实测**：`WritePolicyUiIntegrationTests.DefaultController_IsWritable_AndParityFalse_IsReadOnlyWithReason`
在带 sidecar 下**真实执行并通过**（含 `IsWritable` 与只读原因两个断言面）。

**注意区分**：`WritePolicyUiTests`（4 个普通 `[Fact]`，不依赖 sidecar）与
`WritePolicyUiIntegrationTests`（`[WritePolicySidecarFact]`）是**两个类**；
矩阵里那句把两者混称了，本轮一并澄清。

### 4.2 skip 总量：111 → **104**

| 项目 | 无夹具 skip | 带夹具 skip |
|---|---|---|
| Host | 74 | 44 |
| CoreClient | 26 | 0（带新 sidecar 时 208/4/0；r1 后 214/4/0） |
| **App** | **11** | **4** |
| 合计 | **111** | **48**（Host 44 + CoreClient 0 + App 4） |

**更正**：矩阵 §5 写的"111 skip"是**无夹具**口径。带 sidecar 时实际是 **48**，
其中 Host 44（opt-in/需真实 IPC）、App 4（opt-in gated）、CoreClient 0。
本卡的 104 口径是"App 改用带 sidecar 后的三项目合计"（74 + 26 + 4）；
**两种口径必须写清是"无夹具"还是"带夹具"**，不得混用。

## 5. 边界（不得越过的结论）

- 本卡**没有**让条件 3 判 MET：仍有 **Host 44 + App 4 = 48 个带夹具 skip**、
  §0 未纳范围的 GUI 流程（回收站/命令面板/源恢复/沉浸）、以及真机走查。
- 7 个转绿测试里，`RunControllerHostIntegrationTests` 与 `CreateChapterHostIntegrationTests`
  依赖真实 IPC（真 sidecar 进程），**在有 sidecar 的环境才可复现**；无夹具环境仍会 skip（既有机制，不是新增）。
- 本卡**只改证据与矩阵**，未动任何测试断言。
