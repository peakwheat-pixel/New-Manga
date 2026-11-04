# FEA-09-UI-1 AC 证据矩阵（Owner 交付，2026-11-04）

状态口径：`MET` = 本矩阵列出的命令/测试在本工作树实际运行且全绿，且逐项判别有证据映射；`PARTIAL` 如实登记。本表为 Task 进入 `in_review` 的逐 AC 证据；最终 `done` 以 Codex 独立 Review + DSH 集成验证为准。

## 门禁结果（工作树，base `1a5894282`，clean 起步）

| 命令 | 结果 |
|---|---|
| `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **0 warning / 0 error** |
| `dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build` | **1313 passed / 0 failed**（8 程序集；基准 1300/0 保持，+13=ReferencedImportUiTests；skip 63=既有 58+新真实 IPC 门 5） |
| `NEWMANGA_FEA09_IPC=1 … --filter Fea09UiImportIpcTests` | **5/5 passed**（真实 Python Core stdio） |
| `pwsh tools/governance/check.ps1` | **FAIL 1 error**（READY DAG 滞后：PLAN 未随认领推进；PLAN/STATUS 不在 Owner 写域，交 DSH 集成同步——与 FEA-09 认领期同型过渡态）+3 既有 warning |
| `pwsh tools/governance/verify_pins.ps1` | **17/17 PASS**（C-05/C-15/C-16 冻结字节未触碰） |
| `git diff --name-only` | 全部在冻结 allowed_paths 内（FEA-09 canonical 证据被旧测试复跑覆盖后已 `git checkout` 恢复原字节） |
| FEA-06 四 PNG | **4/4 UNCHANGED** |

## AC 结论

| AC | 判别项 → 证据 | 结果 |
|---|---|---|
| **AC-1 plan 预览/确认/拒绝** | `ReferencedImportUiTests.PlanPreviewRendersCorePlanAndTotals`（Core plan 投影/总数/按章拒绝）、`PlanRefusalRendersTypedCodeOnly`（typed code）、`PlanWithoutChapterIsRefusedBeforeAnyHostCall`（零 Host 调用）、`PlanStaleStartRefusalDropsThePlanAndAsksForAFreshPreview`（确认前源变化→`SOURCE_PLAN_STALE` typed 拒绝、不静默提交、要求重新预览）；真实 IPC `PlanPreviewConfirmAndReceiptOverRealStdio`（plan→confirm→receipt completed→章节页可见） | **MET** |
| **AC-2 密码/零泄漏/AES** | 真实 IPC `EncryptedZipPasswordRetryOverRealStdio`：plan `status=encrypted`（不请求密码）→ 错密码→`SOURCE_PASSWORD_INVALID` typed 失败且 0 页 → 正确密码（DPAPI 一次性 secret_ref：WritePassword→IssueSecretGrants→重 plan→start）→ **completed/2 页**；token 文件 0 残留；`WriteEvidenceAndAssertZeroPasswordLeakage`：wire 113 帧 + core stderr + 证据 JSON 对密码字面量/UTF-8 hex（大小写）/base64 **0 命中**；`AesZipPlanIsTypedUnsupportedOverRealStdio`：AES ZIP plan `unsupported` + `SOURCE_FORMAT_UNSUPPORTED`（不请求密码）；VM 侧 `EncryptedPlanRequiresPasswordBeforeConfirm`/`PasswordIsClearedAfterStartAndNeverAppearsInUiText`/`FailedReceiptRendersTypedReasonWithoutSecrets`（UI 文本零密码零路径） | **MET** |
| **AC-3 取消/重试/计数** | 真实 IPC `CancelKeepsCommittedPagesOverRealStdio`：终态后 cancel `accepted:false`（冻结语义）+ 运行中 cancel `accepted:true`→`Cancelled`；已提交页保留（chapter_pages == imported_pages，5 页）、未提交 0 出现；receipt 计数与 `committed_boundary` 一致。VM 侧 `ConfirmWhileRunningIsIgnored…`（运行中二次确认 no-op、plan 消费后不可再确认）、`ConsumedPlanCannotBeReconfirmed_RetryGoesThroughAFreshPlan`（重试=新 plan→新 operation；自然键去重由 Core 保障——FEA-09 AC-5 已测）、`RunningCancelInvokesTheHostCancelFace` | **MET** |
| **AC-4 真实 production adapter 证据** | `Fea09UiImportIpcTests`（真实 stdio Python Core + 生产 `CoreServiceClient`/`SourceReadCoordinator`/`HostCommandDispatcher` HostLocal 路由 + 生产 `SourceImportCoordinator`——即 `IHostController` 四方法背后的同一编排类；非 fake controller、非进程内替代）；断言对象为 UI 面向模型（plan 预览/typed 原因/计数/receipt 状态）；wire 断言 `RegisterSourceReadGrant/PlanImportReferences/StartImportReferences/GetImportReceipt/CancelImport` 全部在帧中；证据 `verification/FEA-09-UI-1/ipc/ui-import-ipc.json` + `.wire.ndjson`（路径已由 WireLog 脱敏 `[REDACTED]`，密码 0 命中）；VM/View 层（ImportDockViewModel+ImportDockView 真实控件渲染）由 `ReferencedImportUiTests` 13 例覆盖（headless Avalonia；VM 状态机测试，非 AC-4 证据主体） | **MET** |
| **AC-5 旧行为不变/无用户数据/不减少/未 push** | 旧 `ImportPages` 路径零改动（`ImportDockViewModel` 旧方法/旧 Rows 流程保留；`ImportExportUiTests` 既有用例全绿）；FEA-06 四 PNG 4/4 UNCHANGED；全量 1313/0（≥基准 1300/0）；fixture 全部隔离于 `G:\CODEX\New Manga.workspace\FEA-09-UI-1\ipc-*`（合成数据/冻结 FEA-09 fixture，无真实用户数据/AppData）；未 commit、未 push | **MET** |

## 限制与如实登记

1. **HostCommandDispatcher/HostCommandRegistry 零改动**：Appointment 的「payload pass-through」缺口经核实**已由 FEA-09 交付**（Registry 将 8 个 source 命令注册为 HostLocal；`HostCommandDispatcher.InvokeAsync` 对 HostLocal 命令原样传递 payload，经 `HostRuntime.HostLocalAsync` 路由到 `SourceReadCoordinator`）；本 Task 未改命令语义、未新增命令。
2. **check.ps1 1 error**：`READY DAG 只允许 ready` —— PLAN 的 READY 节点未随 Owner 认领推进（`doc/REBASELINE_PLAN.md`/`doc/STATUS.md` 不在本 Task allowed_paths）；交 DSH 集成同步（FEA-09 认领期同型过渡态）。
3. **FEA-09 canonical 证据可被常规测试复跑重写**：`Fea09RealIpcTests`（IPC 门）写 `verification/FEA-09/ipc/*`（EV-004/005）；`NewManga.CoreClient.Tests/WireLogSourceRedactionTests`（**默认门**，无需 IPC env）写 `logs/wire-redacted.ndjson`（EV-060）。本次两类覆盖均已恢复原字节并复算 pin 一致；登记债务候选（FEA-09 测试设计）。
4. **C-07 口径（返修后）**：**未新增 `IHostController` 方法**；新增独立 `ISourceImportController`（App 层 capability 端口），`python tools/generate_api_inventory.py --check` PASS → C-07 冻结清单不变，无需 UNFREEZE。
5. **取消时序竞态**：真实 IPC 的 mid-run cancel 依赖到达时序；测试断言协议不变量（accepted 语义 + 仅已提交页可见），不硬编排竞态结果。

## 结论

- AC-1…AC-5 全部 **MET**（Owner 自评；待 Codex 独立实现 Review + DSH 集成验证确认）。
- 证据文件：`verification/FEA-09-UI-1/ipc/ui-import-ipc.json`、`ipc/ui-import-ipc.wire.ndjson`、`logs/gates.json`、本文件。
