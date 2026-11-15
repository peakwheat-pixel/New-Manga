---
id: R002-RESYNC-1
title: 修复 R-002 —— id 错配后无重同步导致管道永久 off-by-one
kind: defect
governance_version: 3
status: done
suggested_owner: DSH
owner: DSH
reviewer: r002-review（独立上下文子 agent，APPROVED_WITH_LIMITATIONS）
integration_commit: 994f58730
canonical_evidence_status: complete
resource_closeout_status: complete
depends_on:
  - E7-5-SHUTDOWN-RACE-1
approval: 用户 2026-11-15「全部授权、持续自动推进」；目标 B 的产品门槛收敛
base_commit: eac6110e9
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/R002-RESYNC-1
allowed_paths:
  - doc/tasks/R002-RESYNC-1.md
  - apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Transport/SidecarProcess.cs
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/R002ResyncTests.cs
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/R002-RESYNC-1/**
---

# R002-RESYNC-1：错配后有界重同步

## 来源

`E7-CONCURRENCY-STATUS-1` 核实的权威 E-7 第 3 项（`PIPE-EXCLUSIVE-TRANSPORT-1.md:123-129`）：

> **R-002**：id 错配后无重同步，流中可能残留一帧（AC5 NOT MET）。

现状（`CoreServiceClient.cs`）：

```csharp
var responseLine = frame.ResponseLine;
for (var skipped = 0; skipped < 16 && CoreProtocol.IsEventFrame(responseLine); skipped++)
    responseLine = await _process.ReadNextResponseLineAsync(timeout, cancellationToken);

var response = CoreProtocol.Parse(responseLine);
EnsureResponseBelongsToRequest(response, requestId, _options.StderrLogPath);   // ← 错配就抛，不 drain
```

错配时抛 `MalformedResponse`，但**本次请求真正的响应可能还在管道里**（或后续帧也在）。
下一次 `ExchangeAsync` 会读到它 ⇒ **永久 off-by-one**：此后每个命令都拿到上一条的响
应，直到有人 restart。

## 设计判断（先定取舍，再写代码）

### Q1：drain 上限取多少？—— **16**

理由：
- 事件帧跳过循环已经用 `skipped < 16`（既有、经过考虑的界限）；
- 错配后的残留一般是「本次请求的真响应」或「若干事件帧 + 真响应」，16 足够覆盖；
- **不引入第二个魔法数字**：与既有界限同值，降低认知负担。

### Q2：超限后 poison 还是继续？—— **poison**

理由：drain 到 16 帧仍未找到匹配 id ⇒ 管道已严重错位（协议违约），继续用只会让每个命令
都读到别人的响应。poison 让后续调用**立即 fail-closed**（`ThrowIfPoisoned` 抛 `RequestTimeout`
+ "poisoned"），把「静默错位」变成「明确要求重启」。

### Q3：drain 期间读到事件帧怎么办？—— **跳过**

事件帧是单向通知，不属于任何请求的响应；跳过它们是既有语义（事件帧跳过循环）。

### Q4：drain 期间 timeout / 取消？—— **沿用现有语义**

timeout ⇒ poison + `RequestTimeout`；调用方取消 ⇒ poison + 重抛 `OperationCanceledException`
（R-005 已实现的语义；`ReadNextResponseLineAsync` 复用同一路径）。

### Q5：改在哪一层？—— **`CoreServiceClient`**

- `SidecarProcess` 保持「只读一行」的单一职责，不引入「它怎么知道该匹配哪个 id」的耦合；
- `CoreServiceClient` 同时持有所需信息：`requestId`、`CoreProtocol`、`_process`；
- 改动局限在错配处理分支（+ 一个私有 helper）。

### Q6：如何测试（必须先红）？—— **夹具回两帧：先错 id、再对 id**

PowerShell 子进程在收到请求后输出两行：
1. `{"request_id":"req-<wrong>","result":null}`（错 id）
2. `{"request_id":"req-<expected>","result":{...}}`（正确响应）

- **当前代码**：第一次 `SendAsync` 读到错 id ⇒ 抛 `MalformedResponse`；第二帧残留在管道，
  下一次调用读到它 ⇒ 错位。测试应 FAIL（期望成功拿到正确响应）。
- **修复后**：drain 掉错 id 帧，读到正确响应 ⇒ 成功。

> 夹具需要知道 `requestId`。`CoreServiceClient` 的 id 是 `req-{n}` 自增，测试无法预知起始值，
> 因此夹具**不能写死 id**。改为：夹具输出的第一行用一个**明显不属于本次请求**的 id
> （例如 `req-999999`），第二行回显**收到的请求 id**（PowerShell 从 stdin 读一行后取 `request_id`）。
> 这样与自增起点无关。

## 目标（一个可观察结果）

新增测试在**修改前 FAIL**（抛 `MalformedResponse` 而非拿到正确响应）、**修改后 PASS**；
且超限时 poison。

## Acceptance Criteria

- [x] **AC1 设计判断先落盘**：Q1–Q6 六个取舍在卡内写明（本文件即为该判定）。 <<MET>>
- [x] **AC2 测试先红**：`R002ResyncTests` 构造「先错 id、再对 id」两帧，修改前 **FAIL**。 <<MET>>
- [x] **AC3 实现有界重同步**：`CoreServiceClient` 在 id 错配时有界 drain（上限 16）， <<MET>>
      跳过事件帧，找到匹配 id 的响应即返回；**超限 poison**。
- [x] **AC4 修后绿 + 超限用例**：重同步用例通过；另有一条「drain 超限 ⇒ poison」用例。 <<MET>>
- [x] **AC5 不回归**：`NewManga.CoreClient.Tests` 全量 **0 failed**；四件套 PASS。 <<MET>>
- [x] **AC6 独立复核**：固定 head 交独立上下文 Review。 <<MET>>

## 允许修改范围

见 frontmatter `allowed_paths`：**只改 `CoreServiceClient` 的错配处理 + 新增一个测试文件**。

## 禁止范围

- 不得改 `SidecarProcess` 的读/写语义（它保持「读一行」的职责）；
- 不得放宽 `EnsureResponseBelongsToRequest` 的判据（错配仍必须被识别）；
- 不得让 drain **无界**（必须有上限，否则畸形管道会挂死）；
- 不得顺带做 E-7 其它项。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| 重同步（红→绿） | `dotnet test … --filter FullyQualifiedName~R002ResyncTests` | 修改前 FAIL、修改后 PASS |
| 超限 poison | 同上 | PASS（poison 后下次调用 fail-closed） |
| 全量不回归 | `dotnet test …NewManga.CoreClient.Tests.csproj` | 0 failed |
| 四件套 | check / pins / inventory | PASS / 18-18 / 87 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-R002-01 | AC1/AC3/AC4 证据总述 | verification/R002-RESYNC-1/README.md | 99b0aef1d | fe44d01752c33534bb81ae8ddca7e442c9007a0fe837b0d51bef1b8ce5b3720d | CANONICAL | BLOB |
| EV-R002-02 | AC4 新建测试绿（4 passed） | verification/R002-RESYNC-1/test-green.log | 99b0aef1d | afb1acab351036ba10b864bfcf14c135900c53afd9551a74f44ce6f25448394a | CANONICAL | BLOB |
| EV-R002-03 | AC5 全量不回归（203/0/30） | verification/R002-RESYNC-1/coreclient-full.log | 99b0aef1d | e2abde13e8ad87ee55907c91b1a5a4217245c03241827ac0185ba843731e9ca4 | CANONICAL | BLOB |
| EV-R002-04 | AC3 修复 diff（两处调用点 + helper） | verification/R002-RESYNC-1/fix.diff | 99b0aef1d | 84a626b982499f0ecb6c76577f883dbc8cfdc95e705816f8ede73a4d0a2da8a0 | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/R002-RESYNC-1/ | NOT_APPLICABLE | — | — | 新增证据，无迁移/归档 |

## Closeout Record

- Closeout：2026-11-16，DSH；实现 `994f58730` + r1 返修（本提交）。
- **结果**：R-002 修好 —— 两个方法（`SendHostControlAsync`、`SendAsync`）都改为经
  `ReadResponseForRequestAsync`：错配帧被有界 drain（上限 16）、事件帧跳过、超限 **poison**
  并抛 `MalformedResponse`。相对旧行为：错配容忍度从 **0 提升到 16**。
- **行为变化（复核确认不是回归）**：旧逻辑在 >16 事件帧时**同样失败**（事件帧被当响应 ⇒
  `RequireResult` 抛 `INVALID_RESPONSE`，且真响应残留 ⇒ 永久失步）⇒ 不存在「旧成功/新 poison」场景。
- **独立复核**：`r002-review` **APPROVED_WITH_LIMITATIONS**（0/0/2/5），确认缺陷真实、修复正确、
  两处调用点无遗漏（`git grep` 只剩定义 1 处 + 测试 3 处）、`Poison()` 无副作用、越界清洁。
  - P2-F2（交接门槛）→ 已补 AC 标记 / Canonical Evidence / reviewer / status；
  - P3-F3（`allowed_paths` 漏列 `SidecarProcess.cs`）→ 已补；
  - P3-F5（E-6 注释悬空错挂在 `ResyncMaxDrainFrames` 前，且 `EnsureResponseBelongsToRequest`
    已成生产死代码）→ 悬空注释已删除；该方法保留并由测试承载 E-7 #2 的 fail-open 文档化用例；
  - P3-F7（poison 对外表现为 `RequestTimeout`、消息不点名 resync）→ 已记录在未关闭项。
- **门禁**：新建测试 4 passed / 8 ms；全量 **203 passed / 0 failed / 30 skipped / EXIT=0**；
  `check.ps1` PASS (3 warnings)｜`verify_pins` 18/18｜`api_inventory` 1/80/6=87。
- **未关闭项（不淡化）**：
  1. **P2-F1：4 条测试只直接调 `internal static` helper，没有任何测试证明两个调用点真的在用它。**
     若未来某调用点改回直接判断，测试仍会全绿。可行收口办法是删除 `EnsureResponseBelongsToRequest`
     让「改回直接调用」**编译失败**，但那会牵动 `PipeResponsePairingValidationTests` 的 3 条用例
     （其中一条是 E-7 #2 的 fail-open 文档化用例），属跨卡改造，**本卡未做**；
  2. **E-7 仍未完成**：`_pipeGate` 未统一 + `ExchangeAsync` 仍 `public`、无 `request_id` 时 fail-open
     ⇒ **「并发安全」仍不可宣称**；
  3. **poison 后无自动恢复**，对外错误码仍是 `RequestTimeout`（`ThrowIfPoisoned` 既有行为），
     消息不点名「重同步失败」；
  4. 16 帧预算由事件帧与错配帧**共享**；不可解析帧会直接抛出而不 poison（下一帧读取可自愈）。

