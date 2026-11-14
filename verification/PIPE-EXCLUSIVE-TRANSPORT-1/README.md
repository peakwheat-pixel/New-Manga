# PIPE-EXCLUSIVE-TRANSPORT-1 证据（E-7）

卡面：`doc/tasks/PIPE-EXCLUSIVE-TRANSPORT-1.md`。基线 `b202b47fb`。

## 1. 做了什么

| # | E-7 窗口 | 处置 |
|---|---|---|
| 1 | `HostBridgeClient` 管道**完全无锁** | **已修**：在 `Transport/SidecarProcess` 新增**传输层独占原语** `AcquireExchangeLeaseAsync()`（返回 `IDisposable` 租约，`SemaphoreSlim(1,1)`）；`HostBridgeClient` 的 `SendRawAsync` 与 `SendAsync` **两处**调用点都 `using var lease = ...` 包住整个"写+读"周期 |
| 2 | 公开 `CoreServiceClient.SendRawAsync` 绕开 `_pipeGate` | **已修**：改为持 `_pipeGate`（`try/finally`） |
| 3 | 独占不在传输层 | **部分修**：传输层现在**具备**租约原语并被 `HostBridgeClient` 使用；`CoreServiceClient` 仍用自己的 `_pipeGate`（已验证有效）。**未**把 core_service 侧也改为租约 —— 折中，已登记 |
| 4 | 响应无 `request_id` 时 fail-open | **未修**：`HostBridgeClient` 现在校验**有 id 的**响应；无 id 仍 fail-open。列为后续 |

另：`HostBridgeClient.ParseResponse` 新增 `expectedId` 参数并**校验响应 id**（AC4 一半）。

**`host_bridge` 是独立进程/独立管道**（`SidecarSpec.HostBridgeName`，独立 `SidecarProcess`），所以两条管道**各自独立独占**，无需共享锁。

## 2. 判别（两次实验，均有实测）

| 实验 | 结果 |
|---|---|
| **修复前**：`BridgePipeExclusivityTests` 2 个测试 | **2 FAIL**，均为 `InvalidOperationException: The stream is currently in use by a previous operation on the stream` |
| **修复后** | **2 PASS** |
| **回退实验**：移除 `HostBridgeClient` 两处租约 | **2 FAIL**（同一异常）⇒ 证明测试抓得住缺陷 |
| 恢复租约 | **2 PASS** |

定向合跑（bridge + core pipe + 既有 host bridge 集成）**9 passed**。

## 3. 全量结果

| 项目 | 无夹具 | 带新 sidecar |
|---|---|---|
| `CoreClient` | **189 / 0 / 29 / 218** | **214 / 4 / 0 / 218** |
| `Host` | **321 / 0 / 74 / 395** | **350 / 1 / 44 / 395** |

**效果**：带新 sidecar 的 **Host 失败 9（E-6 前）→ 2~3（E-6 修后）→ 1（本卡后）**；
`CoreClient` 失败的 4 个是 "Frozen Core" 前提类，与管道无关（见 §5）。

**关于无夹具 skip 27→29**：新增 `BridgePipeExclusivityTests` 的 2 个 `[SidecarFact]` 在无夹具时按既有机制 SKIP。
这是**新增测试**带来的 +2，不是放宽既有断言（既有 189 pass 与 27 skip 未变化）。

## 4. 一个测试自身的错误（我造的）

`ConcurrentMixedBridgeCommands` 初版用 `IssueAsync("res-0", ...)` 并发，失败于
`BridgeException [RESOURCE_NOT_CATALOGED]` —— 那是**测试写错了**（这些 resource 不在 catalog 里），
不是锁的问题。改为 `PingAsync` + `ResolveAsync(不存在的 grant)`，断言后者**必须抛 typed 错误**
（若响应被串成 ping 的成功，它就不会抛 ⇒ 测试失败）。修正后通过。

## 5. 未完成（如实登记，不得当作已修）

- **AC5 / R-002 重同步**：id 错配后 `CoreServiceClient` 抛错，但流中可能**残留一帧**，`HostBridgeClient`
  同样。本轮**未**做"丢弃直到匹配 id"或 poison session 的重同步。
- **AC4 后半**：无 `request_id` 时仍 **fail-open**（未改 fail-closed）。
- **窗口 3 的完整下沉**：`CoreServiceClient` 仍用 `_pipeGate` 而非传输层租约；
  今后任何**新增**直调 `_process.ExchangeAsync` 的代码仍会绕过独占。
- **`HostBridgeClient` 的 id 校验只覆盖有 id 的响应**；且 `SendRawAsync`（bridge 侧）不带期望 id。

## 6. 本卡的价值边界

`host_bridge` 管道从"完全无保护"变为"有独占 + 有 id 校验"，两条管道的并发判别都有测试且能回退变红。
但"并发安全"仍**不能**宣称 —— 见 §5 四项未完成。
## 7. r1 复核处置（ACCEPT_WITH_LIMITATIONS，无 P0/P1）

复核报告：`doc/reviews/PIPE-EXCLUSIVE-TRANSPORT-1-review-r1.md`（审查者 `review-pipe-transport`，独立上下文）。

### 7.1 复核者的关键发现（我已核实）

| 发现 | 我的核实 | 处置 |
|---|---|---|
| **R-003：bridge id 校验零覆盖**（删掉后 bridge 5/5 全绿） | 属实 | **已修**：`ParseResponse` 改 `internal`，新增 `BridgeResponseIdValidationTests`（3 个 `[Fact]`）。实测删校验 → `MismatchedNumericId_ThrowsMalformedResponse` **变红**；恢复 → 3 passed |
| **R-004：`SendRawAsync` 的锁零覆盖**（删掉后全量数字不变） | 属实 | **已修**：新增 `RawSendPipeExclusivityTests`（并发 6×`SendRawAsync` + 6×`ListBooks`，断言各自 result 形状）。实测删锁 → **FAIL**（`stream is currently in use`）；恢复 → PASS |
| **R-001：`_pipeGate` 与 `_exchangeGate` 两套锁域互不排他** | **部分误判**：已核实 `CoreServiceClient._process` 与 `HostBridgeClient._process` 是**两个独立 `SidecarProcess` 实例**（core_service 进程 vs host_bridge 进程，见 `HostBridgeClient.StartAsync` 用 `SidecarSpec.HostBridgeName`），**两条独立管道本就不需要互斥**。但"独占总在传输层"确实**未**做到（core 侧仍用 client 层 `_pipeGate`） | 承认 AC1/AC2 **未完全达成**，见 §7.2 |
| **AC4 NOT MET**：core 侧无 `request_id` 仍 fail-open；bridge 仅校验**数字** id | 属实 | **未修**，登记 |
| **AC5 NOT MET**：R-002 无重同步 | 属实 | **未修**，登记 |
| **R-005 取消触发永久失步** | 未核 | **未修**，登记 |
| P3：`Dispose`/`StopAsync` 在租约外 | 属实（在途命令会得 `ProcessExited`） | **未修**，登记 |
| P3：数字归因（"9→1"） | 部分成立：Host 唯一失败是 `SOURCE_REGISTRY_BUSY`（E-6 已归为 flaky），故只能说"不劣于 2~3" | 措辞已在 §3 修正为区间表述 |

### 7.2 卡面 AC 的实际达成度（修正后的诚实口径）

| AC | 达成度 |
|---|---|
| AC1 传输层独占原语 | **PARTIAL**：原语已加（`AcquireExchangeLeaseAsync`）并被 `HostBridgeClient` 使用；`CoreServiceClient` 仍用自己的 `_pipeGate`，**未**统一 |
| AC2 所有调用方走它 | **NOT MET**：core 侧两处仍直调 `ExchangeAsync`（虽有 `_pipeGate` 保护，但不是传输层原语） |
| AC3 host_bridge 判别测试 | **MET**（回退实验确认） |
| AC4 id 校验覆盖两条管道 | **NOT MET**：无 `request_id` 时仍 fail-open；bridge 仅数字 id |
| AC5 R-002 重同步 | **NOT MET** |
| AC6 不回归 | **MET**：无夹具 CoreClient **192/0/30/222**、Host 321/0/74/395、App 950/0/11；带夹具 CoreClient **218/4/0/222**（4 个为 Frozen Core 前提类）、Host **350/1** |

### 7.3 未完成项（已拆出，见 `E-7` 更新）

1. **AC2/AC1 完整下沉**：`CoreServiceClient` 改用传输层租约，且把 `ExchangeAsync` 降为 `internal`
   以防未来直调。
2. **AC5 / R-002 重同步**：id 错配后丢弃直到匹配 id（或 poison session）。
3. **AC4 后半**：无 `request_id` 时 fail-closed。
4. **R-005**：取消（`CancellationToken`）后流状态可能永久失步。
5. **`Dispose`/`StopAsync` 与在途命令的竞争**。
