---
id: R002-RESYNC-1
title: 修复 R-002 —— id 错配后无重同步导致管道永久 off-by-one
kind: defect
governance_version: 3
status: in_progress
suggested_owner: DSH
owner: DSH
reviewer: null
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

- [ ] **AC1 设计判断先落盘**：Q1–Q6 六个取舍在卡内写明（本文件即为该判定）。
- [ ] **AC2 测试先红**：`R002ResyncTests` 构造「先错 id、再对 id」两帧，修改前 **FAIL**。
- [ ] **AC3 实现有界重同步**：`CoreServiceClient` 在 id 错配时有界 drain（上限 16），
      跳过事件帧，找到匹配 id 的响应即返回；**超限 poison**。
- [ ] **AC4 修后绿 + 超限用例**：重同步用例通过；另有一条「drain 超限 ⇒ poison」用例。
- [ ] **AC5 不回归**：`NewManga.CoreClient.Tests` 全量 **0 failed**；四件套 PASS。
- [ ] **AC6 独立复核**：固定 head 交独立上下文 Review。

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

## 证据

设计判断（本文件 §设计判断）、红/绿日志、全量日志写入 `verification/R002-RESYNC-1/`。
