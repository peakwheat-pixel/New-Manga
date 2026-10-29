# V11R-A-7 证据包：导出 stale 策略契约缺口修复（`abort` / `continue_existing`）

- Task：`V11R-A-7`（Lead 2026-10-30 分配；解除 B-5 F3-5 唯一功能性缺口）
- Owner：`core-bridge`
- Worktree：`G:/CODEX/New Manga.workspace/worktrees/V11R-CORE-BRIDGE`，分支 `v11r/core-bridge`
- 交付 commit：见 Handoff（本证据 commit 的父 commit）
- 状态：实现 + 测试 + 契约语义已完成；Owner 未自审。

## 1. 事实核对（先核实，不猜）

| 事实 | 源码位置 |
|---|---|
| Core `handle_start_export` **要求**六字段之一 `stale_policy`，且值只能是 `abort` / `continue_existing` | `src/bootstrap/core_service.py:2853-2864`（required 集合 :2854；值域 :2863） |
| Core 把 `stale_policy` 映射为 `StalePolicy.ABORT` / `StalePolicy.CONTINUE` | `core_service.py:2948` |
| Host 侧 issuer 镜像同一校验（六字段 + 值域） | `apps/desktop-avalonia/src/NewManga.CoreClient/Issuer/HostIssuer.cs:360-386`（值域 :382-386） |
| Host 既有 payload 构造器本就有 `stalePolicy` 参数（默认 `abort`），只是 `IHostController` 未暴露 | `apps/desktop-avalonia/src/NewManga.App/Services/ImportExportContracts.cs:201-242`（:240 写 `stale_policy`） |

结论：缺口只在**服务层 API 未暴露**；Core/HostIssuer/payload 三层本来就支持两个值。

## 2. 变更

| 文件 | 变更 |
|---|---|
| `src/NewManga.App/Services/IHostController.cs` | `StartExportAsync(...)` **追加可选参数** `string? stalePolicy = null`（既有方法签名参数不变，仅尾部新增；旧调用方零改动）。 |
| `src/NewManga.App/Services/HostController.cs` | 校验：`null`/空白 → 默认 `abort`；非 `abort`/`continue_existing` → `SetLastError("INVALID_REQUEST")` 并返回 null（**零帧**，本地拒绝）；合法值透传 payload 构造器；成功清空 `LastError`。 |
| `src/NewManga.App/Services/NullHostController.cs` | 同步新增可选参数（设计时 inert，返回 null）。 |
| `tests/NewManga.App.Tests/FakeHostController.cs` | `StartExportCalls` 追加 `StalePolicy` 字段，供 UI 测试断言"UI 请求了哪个策略"。 |
| `doc/contracts/V11R_COMMAND_CONTRACT_V1.md`（C064 `library_start_export`） | 补 `stale_policy` 语义：仅两值、`null`=默认 abort、非法值本地 `INVALID_REQUEST` 零帧；生成器 `build_contract_doc.py` 的 C064 覆盖同步更新，避免重新生成时回退。 |

未改：Python Core、UI 视图/ViewModel（`ImportExportPanels.cs` 的"continue_existing 未支持"文案由 ui-studio
按 Lead 通知改为真实可选）、`HostRuntime`/`HostGrantCoordinator`（payload 已正确传 `stale_policy`）。

## 3. 测试（真实执行）

| # | 测试 | 结果 | 证据 |
|---|---|---|---|
| 1 | `ExportStalePolicyTests.FakeController_RecordsTheRequestedStalePolicy` | PASS | `trx/app-stale-policy.trx` |
| 2 | `NullController_AcceptsBothPolicies_WithoutThrowing` | PASS | 同上 |
| 3 | `IllegalPolicy_IsRefusedLocally_WithTypedCode_AndNoFrames`（`LastError=INVALID_REQUEST`、`WireFrameCount=0`） | PASS | 同上 |
| 4 | `BlankPolicy_FallsBackToTheDefaultAbort`（不误报非法） | PASS | 同上 |
| 5 | `ExportStalePolicyWireTests.BothPolicies_AreSentToTheCore_AsStartExportFrames`（真实 sidecar：两值各发真实帧，Core 接受字段并返回 `TARGET_NOT_FOUND`——证明字段通过 HostIssuer+Core 校验，非 `INVALID_REQUEST`） | PASS | `trx/host-stale-policy-wire.trx`；`export-stale-policy/{abort,continue_existing}.json`（含完整请求/响应行） |

关键 wire 证据（`continue_existing.json`）：

```
request : {"protocol":"new-manga.core","version":{"major":2,"minor":3},"request_id":"req-8",
           "command":"StartExport","payload":{...,"stale_policy":"continue_existing",
           "target_ref":"etref1.grant_…"}}
response: {"protocol":"new-manga.core","version":{"major":2,"minor":3},"request_id":"req-8",
           "result":null,"error":{"code":"TARGET_NOT_FOUND","category":"not_found",
           "message":"Export target was not found","retryable":false}}
```

## 4. 质量门

| # | 命令（`apps/desktop-avalonia`） | exit | 结果 |
|---|---|---:|---|
| 1 | `dotnet build NewManga.sln -warnaserror` | 0 | 0 warning / 0 error |
| 2 | `dotnet test tests/NewManga.App.Tests --filter ExportStalePolicy` | 0 | 4/4 PASS |
| 3 | `dotnet test tests/NewManga.Host.Tests --filter ExportStalePolicyWire` | 0 | 1/1 PASS |

日志/TRX：`verification/V11R-A-7/logs/`、`trx/`。

## 5. 对 UI 的接口（供 ui-studio）

```csharp
// abort（默认，保持旧行为）
await controller.StartExportAsync(bookId, chapterId, pageIds, target, format: "zip");
// continue_existing（真实可选）
await controller.StartExportAsync(bookId, chapterId, pageIds, target, format: "zip",
    stalePolicy: "continue_existing");
```

- 合法值：`"abort"` / `"continue_existing"` / `null`（=abort）。
- 非法值：返回 null，`Snapshot.LastError == "INVALID_REQUEST"`，不发任何 Core 帧。
- 其他导出错误仍按既有通道（`LastError`/`ErrorCode`）返回。

## 6. 偏差 / 遗留

1. **UI 文案变更不在本卡写域**：`ImportExportPanels.cs` 中 `continue_existing` 的"未支持"降级由 ui-studio
   改为真实可选（Lead 已转达）；本卡只提供服务层能力与证据。
2. **契约文档直接编辑**：C064 行由本卡追加语义；core-writer F0-I2 已把 C077 占位改为真实
   `list_page_region_texts`（Lead 已知悉）。若后续重新运行 A-3 生成器，C077 的 F0 内容需以合并后
   文档为准（生成器 C064 覆盖已同步，无回退）。
3. **`HostRuntime` 无独立 StartExport 方法**：导出经 `HostGrantCoordinator`（`grants`）执行，payload 构造器
   已写 `stale_policy`；本卡未改 Host 侧代码，只核实并测试（避免无意义改动）。
