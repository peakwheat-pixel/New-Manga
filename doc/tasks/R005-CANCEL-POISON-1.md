---
id: R005-CANCEL-POISON-1
title: 修复 R-005 —— 调用方取消后管道未 poison 导致永久失步
kind: defect
governance_version: 3
status: in_progress
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - E7-CONCURRENCY-STATUS-1
approval: 用户 2026-11-15「全部授权、持续自动推进」；目标 B 的产品门槛收敛
base_commit: a718cbf49
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/R005-CANCEL-POISON-1
allowed_paths:
  - doc/tasks/R005-CANCEL-POISON-1.md
  - apps/desktop-avalonia/src/NewManga.CoreClient/Transport/SidecarProcess.cs
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/SidecarCancellationPoisonTests.cs
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/R005-CANCEL-POISON-1/**
---

# R005-CANCEL-POISON-1：取消后必须 poison

## 来源

`E7-CONCURRENCY-STATUS-1` 核实的权威 E-7 第 4 项（`PIPE-EXCLUSIVE-TRANSPORT-1.md:123-129`）：

> **R-005**：取消（`CancellationToken`）后流状态可能永久失步。

代码位置：`Transport/SidecarProcess.cs` 的 `ExchangeAsync`：

```csharp
catch (OperationCanceledException) when (!cancellationToken.IsCancellationRequested)
{
    _poisoned = true;   // ← 只有超时才 poison
    throw new SidecarException(SidecarErrorCode.RequestTimeout, ...);
}
```

**缺陷**：`ExchangeAsync` 已把请求行写进子进程 stdin（`_stdin.WriteLineAsync` + `FlushAsync`）。
调方主动取消时，上述 filter **不匹配** ⇒ 异常直抛、**不置 `_poisoned`** ⇒ 请求已发出、响应未读，
管道里残留一帧；下一个 `ExchangeAsync` 会把它当成**自己**的响应 ⇒ **永久 off-by-one**（协议严格一行一次交换）。

## 目标（一个可观察结果）

新增测试在**修改前红**、**修改后绿**；超时路径行为不变。

## Acceptance Criteria

- [ ] **AC1 测试先行且先红**：新增 `SidecarCancellationPoisonTests`，用「PowerShell 假子进程（不读 stdin、
      不写 stdout）」构造「请求已写出但无响应」；断言「取消后下一次 `ExchangeAsync` 立即 fail-closed」。
      在**未修改**的 `SidecarProcess` 上必须 **FAIL**，并记录红日志。
- [ ] **AC2 修复精确**：`ExchangeAsync` 的取消处理在**超时与主动取消两种情况下都置 `_poisoned`**；
      主动取消仍重抛 `OperationCanceledException`（调用方可区分「我取消了」与「超时了」）。
      **不得**改动 `ReadNextResponseLineAsync`（它不写请求，取消不会造成请求/响应错配）。
- [ ] **AC3 修后绿**：同一测试通过，且耗时明显短于红时（不再白等一次完整超时）。
- [ ] **AC4 超时路径不变**：对照测试 `Timeout_StillPoisonsChannel_Unchanged` 通过。
- [ ] **AC5 不回归**：`NewManga.CoreClient.Tests` 全量 **0 failed**；四件套 PASS。
- [ ] **AC6 独立复核**：固定 head 交独立上下文 Review。

## 允许修改范围

见 frontmatter `allowed_paths`：**只改 `SidecarProcess.ExchangeAsync` 的取消分支 + 新增一个测试文件**。

## 禁止范围

- 不得修改 `ReadNextResponseLineAsync` 的取消行为；
- 不得为让测试通过而放宽断言或改测试语义；
- 不得引入新错误码（复用 `RequestTimeout` 的 poison 语义，`ThrowIfPoisoned` 已有）；
- 不得顺带做 R-002（错配重同步）—— 那是独立项。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| 新测试（红） | `dotnet test … --filter FullyQualifiedName~SidecarCancellationPoisonTests` | 修改前 **1 failed / 1 passed** |
| 新测试（绿） | 同上 | 修改后 **2 passed**，耗时下降 |
| 全量不回归 | `dotnet test …NewManga.CoreClient.Tests.csproj` | **194 passed / 0 failed / 30 skipped** |
| 四件套 | check / pins / inventory | PASS / 18-18 / 87 |

## 证据

红/绿日志、全量日志、修复 diff 写入 `verification/R005-CANCEL-POISON-1/`。
