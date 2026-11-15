---
id: E7-5-SHUTDOWN-RACE-1
title: 核证 E-7 第 5 项（Dispose/StopAsync 在租约外）并把在途交换行为固化为回归测试
kind: defect
governance_version: 3
status: in_progress
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - R005-CANCEL-POISON-1
approval: 用户 2026-11-15「全部授权、持续自动推进」；目标 B 的产品门槛收敛
base_commit: f65adfb4b
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/E7-5-SHUTDOWN-RACE-1
allowed_paths:
  - doc/tasks/E7-5-SHUTDOWN-RACE-1.md
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/SidecarShutdownRaceTests.cs
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/E7-5-SHUTDOWN-RACE-1/**
---

# E7-5-SHUTDOWN-RACE-1：核证 `Dispose`/`StopAsync` 在租约外

## 来源

`E7-CONCURRENCY-STATUS-1` 核实的权威 E-7 第 5 项（`PIPE-EXCLUSIVE-TRANSPORT-1.md:123-129`）：

> **`Dispose`/`StopAsync` 在租约外**，在途命令会得 `ProcessExited`。

代码：`CoreServiceClient.DisposeAsync`（`:2629-2630`）与 `SidecarProcess.StopCoreAsync`
—— 两者都不持交换租约。

## 本轮做法：先实测，再决定是否改代码

R-005 的教训是「理解不准就动手会返修」。第 5 项的表述只说了「会得 `ProcessExited`」，
**没说这是不是缺陷** —— 如果错误码明确、可处理，那它可能只是描述了一个合理行为。
所以本轮先写**诊断测试**观察真实行为，再决定。

## 目标（一个可观察结果）

两条测试把当前行为**固化为回归**，并给出书面判定：E-7 第 5 项的表述是否准确、
风险是否如清单暗示的那样严重、以及是否需要改产品代码。

## Acceptance Criteria

- [ ] **AC1 在途交换的诊断**：构造「子进程 5s 后才响应 + 0.5s 时并发 `StopAsync`」，
      记录在途 `ExchangeAsync` 抛出的**异常类型与错误码**。
- [ ] **AC2 停止后的诊断**：`StopAsync` 完成后发起新交换，记录其错误类型与码
      （必须 fail-fast、不得挂起、不得泄漏 BCL 异常）。
- [ ] **AC3 固化断言**：把实测到的具体错误码写进断言（而非宽松的「三者之一」），
      使未来任何行为变化都会让测试变红。
- [ ] **AC4 书面判定**：明确回答「第 5 项表述是否准确」「是否真有缺陷」「是否需要改代码」，
      并如实说明未能覆盖的残余窗口。
- [ ] **AC5 不回归**：`NewManga.CoreClient.Tests` 全量 **197 passed / 0 failed / 30 skipped**；
      四件套 PASS。
- [ ] **AC6 独立复核**：固定 head 交独立上下文 Review。

## 允许修改范围

见 frontmatter `allowed_paths`：**只新增测试文件，不改产品代码**
（除非诊断发现真缺陷 —— 那须在卡内说明并扩范围）。

## 禁止范围

- 不得为「让第 5 项看起来已修」而改 `StopCoreAsync`/`DisposeAsync`；
- 不得把「错误码明确」夸大成「无风险」；
- 不得声称 E-7 第 5 项已修复（本轮只核证 + 固化）。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| 诊断测试 | `dotnet test … --filter FullyQualifiedName~SidecarShutdownRaceTests` | 2 passed |
| 全量不回归 | `dotnet test …NewManga.CoreClient.Tests.csproj` | 197 / 0 / 30 |
| 四件套 | check / pins / inventory | PASS / 18-18 / 87 |

## 证据

诊断日志、探针日志、最终绿与全量日志写入 `verification/E7-5-SHUTDOWN-RACE-1/`。
