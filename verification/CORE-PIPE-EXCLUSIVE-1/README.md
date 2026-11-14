# CORE-PIPE-EXCLUSIVE-1 证据（E-6 / P1）

卡面：`doc/tasks/CORE-PIPE-EXCLUSIVE-1.md`。基线 `0fb8abdc4`。

## 1. 缺陷（wire 帧确证）

失败 session 的最后一帧：

```
# 6  REQ list_chapters  req-7  →  RESP req-6  result: {"targets": []}
```

`list_chapters` 拿到了 `source_list_scan_targets` 的响应 ⇒ 无 `chapters` 属性 ⇒ 静默返回空 ⇒
`Assert.NotEmpty(chapters)` @ `HostReaderChaptersIntegrationTests.cs:47` 失败。

## 2. 根因（三方）

| 环节 | 事实 | 位置 |
|---|---|---|
| 管道 | `ExchangeAsync` **无锁**，假定一次一个在途 | `Transport/SidecarProcess.cs:186-240` |
| Host 保护面 | `_readerIoGate` 只覆盖 reader 类方法 | `HostRuntime.cs:511/527/543/559/576/784` |
| **漏洞** | 后台 source 扫描**绕过 gate** 直接调 client | `SourceScanScheduler.cs:2415`、`SourceOperationCoordinator.cs:219` |
| 放大器 | `SendAsync` **不校验 `request_id`** | `CoreServiceClient.cs:2366` |

**并发时更直接的失败形态**（判别测试实测）：
`System.InvalidOperationException : The stream is currently in use by a previous operation on the stream.`
（`StreamReader` 被并发读）

## 3. 改动

| 位置 | 改动 |
|---|---|
| `CoreServiceClient.cs` | 新增 `_pipeGate = new SemaphoreSlim(1,1)`；`SendAsync` 与 `SendHostControlAsync` **各自**把 `ExchangeAsync` + 事件帧跳过循环 + 解析**整段**包进 `try/finally`，进入/退出持锁 |
| `CoreServiceClient.cs` | 新增 `EnsureResponseBelongsToRequest`：响应 `request_id` 与请求不一致时抛 `SidecarException(MalformedResponse)`，**不再静默接受** |
| 新增 `tests/.../Commands/PipeResponsePairingTests.cs` | 判别测试：并发 6×`ListBooks`（result 是**数组**）+ 6×`source_list_scan_targets`（result 是**对象**含 `targets`），断言各自形状 ||

**为什么锁在 `SendAsync`/`SendHostControlAsync` 而不是 `ExchangeAsync`**：`ExchangeAsync` 返回后，
`SendAsync` 还会调 `ReadNextResponseLineAsync` 跳过事件帧 —— 那仍在读**同一条 stream**。
若锁只管 `ExchangeAsync`，事件帧读取窗口仍然敞开。故锁必须覆盖**整个请求-响应周期**。

## 4. 验证

| 项 | 结果 |
|---|---|
| **修复前**判别测试 | **FAIL**：`InvalidOperationException: The stream is currently in use by a previous operation on the stream` ⇒ 证明测试抓得住缺陷 |
| **修复后**判别测试 | **PASS** |
| **AC4 判别力（回退实验）** | 把 `_pipeGate` 从 `new(1,1)` 改为 `new(8,8)`（允许并发）→ 判别测试**重新变红**，错误同前；改回 `(1,1)` → 转绿。已还原，`PROBE` 标记清零 |
| **AC5 带新 sidecar 全量** | CoreClient **209/4/0/213**（修复前 208/4/0/212，pass +1 = 新测试）；Host **349/2/44/395**（修复前 **342/9/44/395**，**fail 9→2，pass +7**） |
| **AC6 无夹具全量** | CoreClient **186/0/27/213**；Host **321/0/74/395**；fail 均为 **0** |

**关于 skip 26→27**：新增的 `PipeResponsePairingTests` 是 `[SidecarFact]`，无夹具时按既有机制 SKIP。
这是**新增测试**带来的 +1，**不是**放宽既有断言或规避失败；既有 186 pass 与 26 skip 未变化。

## 5. 剩余失败（未在本卡范围内）

### 5.1 CoreClient 4 个 —— "Frozen Core" 前提过期

```
CommandIntegrationTests.Fea12Core_DeleteTrashCapabilityProbe_OldCoreFailsClosedBeforeAnyCommandFrame
CommandIntegrationTests.Fea12NewCommands_FrozenCoreFailsClosedWithTypedError
CommandWiringB2Tests.B2Commands_ExecuteAgainstFrozenCore
CommandWiringB1Tests.B1Commands_ExecuteAgainstFrozenCore
```

这 4 个**以"sidecar 是旧的"为前提**（断言 Core **不**宣告 delete/trash）。新 sidecar 已具备该能力 ⇒ 前提消失。
**不得删除**：它们守 `CORE_CAPABILITY_MISSING` fail-closed 语义，需改为**显式构造缺失能力的 Core**。
**与管道缺陷无关**，本卡未触碰。

### 5.2 Host 剩余 3 个 —— 症状不同，未归因

```
Fea11WatchHostRuntimeTests.Ready_ArmsWatcher_RealFileEventProducesHint_DisposeDisarms  → SOURCE_REGISTRY_BUSY
GrantIssuerTests.Export_GrantRegisters_ThenCoreFailsTyped_OnMissingTranslatedPages     → KeyNotFoundException
GrantIssuerTests.Import_IntoNewChapter_Executes_AndRegistersGrant                      → KeyNotFoundException
```

三者均**不是** `request_id` 错配症状，未在本卡归因。`SOURCE_REGISTRY_BUSY` 疑为并发/残留锁；
`KeyNotFoundException` 需核缺失的字典键。

## 6. 诚实边界

- 本卡**只修了管道独占与 request_id 校验**，未修 5.1/5.2 的 7 个失败。
- 未改 `ListChaptersAsync` 的"属性缺失时静默返回空"语义（属行为变更，需另卡）。
- 未验证 `HostBridgeClient` 的并发路径是否也需要独立 gate —— 它调 `ExchangeAsync`（`:269/:291`），
  而 `ExchangeAsync` 本身已由本卡的锁保护**其自身**的写+读，但**不含**事件帧跳过（那是
  `CoreServiceClient`/`HostBridgeClient` 各自的后置处理）⇒ **`HostBridgeClient` 可能仍有同类窗口**，
  未在本卡修复。**这是一处已知未覆盖面。**
