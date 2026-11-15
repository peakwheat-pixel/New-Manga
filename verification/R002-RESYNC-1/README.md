# R-002（错配后重同步）— 证据

Task：`R002-RESYNC-1`（Owner：DSH）｜基线 `eac6110e9`

## 1. 缺陷

`CoreServiceClient` 处理响应时，id 错配**立即抛** `MalformedResponse`，但**真正的响应还在管道里**：

```csharp
var response = CoreProtocol.Parse(responseLine);
EnsureResponseBelongsToRequest(response, requestId, _options.StderrLogPath);   // 抛，不 drain
```

下一次 `ExchangeAsync` 会读到它 ⇒ **永久 off-by-one**，直到 restart sidecar。
本缺陷在**两个方法**里各出现一次：`SendHostControlAsync`（原 L702-711）与 `SendAsync`（原 L2500-2509）。

## 2. 设计判断（先写后做，见卡 §设计判断）

| 问题 | 决定 | 理由 |
|---|---|---|
| Q1 drain 上限 | **16** | 与既有事件帧跳过界限同值，不引入第二个魔法数字 |
| Q2 超限后 | **poison** | 管道已严重错位，继续用只会让每个命令都读到别人的响应；poison 把「静默错位」变成「明确要求重启」 |
| Q3 期间遇事件帧 | **跳过** | 事件帧是单向通知，不属于任何请求 |
| Q4 期间 timeout/取消 | **沿用现有语义** | timeout ⇒ poison + `RequestTimeout`；取消 ⇒ poison + 重抛 OCE（R-005 已实现） |
| Q5 改在哪层 | **`CoreServiceClient`** | `SidecarProcess` 保持「只读一行」单一职责；客户端同时持有 `requestId` 与 `CoreProtocol` |
| Q6 如何测试 | **抽 static helper + 假委托** | `CoreServiceClient.StartAsync` 会做 `core.ping` 握手，假 sidecar 需完整协议；抽 helper 后无需真实进程 |

## 3. 实现

`SidecarProcess` 新增一个显式钩子（不改读/写语义）：

```csharp
internal void Poison() => _poisoned = true;
```

`CoreServiceClient` 新增 `ReadResponseForRequestAsync` + `ResyncMaxDrainFrames = 16`：
统一循环，**同时**跳过事件帧与 id 错配帧，上限 16；超限 poison 并抛 `MalformedResponse`。

两处调用点（`SendHostControlAsync`、`SendAsync`）都改为调用它。

**行为变化（如实登记）**：原逻辑是「事件帧最多跳过 16 次，之后不再检查是不是事件帧」；
新逻辑是「总跳过 16 帧（含事件帧与错配帧）」。正常场景（0–2 个事件帧）无差别；
极端场景（>16 个事件帧）会 poison 而不是继续 —— 这实际上更安全。

## 4. 测试（4 条，`R002ResyncTests`）

用假「读下一行」委托驱动 helper，**无需真实 core 进程**：

| 测试 | 断言 |
|---|---|
| `MismatchedFirstFrame_IsDrainedUntilTheMatchingResponseArrives` | 错 id 帧被丢弃、拿到匹配响应、**未被 poison** |
| `EventFramesAreStillSkippedWhileResynchronising` | 事件帧与错 id 帧混排时仍能拿到匹配响应 |
| `ResyncGivesUpAfterMaxFrames_AndPoisonsTheChannel` | 一直错 id ⇒ 抛 `MalformedResponse` + **poison 被调用** + drained 次数 = 上限 |
| `ResponseWithoutRequestId_IsAcceptedWithoutDraining` | 无 `request_id` 的响应按既有语义视为属于本请求，**不触发 drain** |

**测试抓到了实现缺陷**：第一版 helper 把事件帧（无 `request_id`）当成「无 id 的响应 ⇒ 属于本请求」直接返回
—— `EventFramesAreStillSkippedWhileResynchronising` 因此 FAIL。修正为**先判 `IsEventFrame` 再判 id**。

## 5. 结果

```
新建测试：        4 passed / 8 ms
全量（不带 sidecar）：203 passed / 0 failed / 30 skipped / 41s / EXIT=0
  （前一轮 199，+4 = 本卡新增）
编译：NewManga.CoreClient.csproj  EXIT=0（无 error）
```

## 6. 四件套

```
check.ps1 PASS (3 warnings)｜verify_pins 18/18｜api_inventory 1/80/6=87
```

## 7. 边界（不淡化）

- 本卡**只修 R-002**。E-7 仍未完成：`_pipeGate` 未统一 + `ExchangeAsync` 仍 `public`、
  无 `request_id` 时 fail-open ⇒ **「并发安全」仍不可宣称**；
- 行为变化：事件帧总跳过上限由「16 次事件帧」变为「16 帧总计」（含错配帧），见 §3；
- drain 期间若子进程持续吐帧且永不匹配，会在 16 帧后 poison —— 这是设计意图，不是挂死。
