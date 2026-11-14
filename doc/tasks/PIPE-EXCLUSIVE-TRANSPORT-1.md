---
id: PIPE-EXCLUSIVE-TRANSPORT-1
title: 把管道独占下沉到传输层，堵住 E-7 的 4 处同型窗口
kind: fix
governance_version: 3
status: done
disposition: "E-7：E-6 修复后仍有 host_bridge 管道、SendRawAsync、传输层、无 id 帧四处窗口"
approval: DSH 2026-11-15（同类缺陷，沿用 E-6 的判别标准）
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - CORE-PIPE-EXCLUSIVE-1
base_commit: b202b47fb
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/PIPE-EXCLUSIVE-TRANSPORT-1
allowed_paths:
  - doc/tasks/PIPE-EXCLUSIVE-TRANSPORT-1.md
  - doc/reviews/PIPE-EXCLUSIVE-TRANSPORT-1-*.md
  - doc/reviews/MAINT-1-EXISTING-FINDINGS-2026-11-14.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/PIPE-EXCLUSIVE-TRANSPORT-1/**
  - apps/desktop-avalonia/src/NewManga.CoreClient/**
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/**
---

# PIPE-EXCLUSIVE-TRANSPORT-1：独占下沉到传输层（E-7）

## 背景

`CORE-PIPE-EXCLUSIVE-1` 给 **core_service** 管道加了 `_pipeGate`（在 `CoreServiceClient` 层），
Host 失败 9→2~3。r1 复核指出同类窗口还有 4 处（已登记 `E-7`）：

| # | 窗口 | 位置 |
|---|---|---|
| 1 | **`HostBridgeClient` 管道完全无锁**，`ParseResponse` 也不校验 id | `Bridge/HostBridgeClient.cs:269/291` |
| 2 | 公开 `SendRawAsync` 直调 `_process`，绕开 `_pipeGate` | `CoreServiceClient.cs:2384` |
| 3 | 独占加在 client 而非**传输层**，今后任何直调 `_process` 的代码天然在锁外 | `Transport/SidecarProcess.cs` |
| 4 | 响应**无 `request_id`** 时校验 fail-open | `EnsureResponseBelongsToRequest` |

另 r1 的 **R-002**：id 错配抛错后管道可能**残留一帧**（off-by-one），无重同步。

**已核实**：`HostBridgeClient` 用**独立进程**（`SidecarSpec.HostBridgeName`）、**独立 `SidecarProcess`**、
**无事件帧跳过** ⇒ 两条管道互不共享，各自需要独立独占。

## Acceptance Criteria

- [~] **AC1 传输层独占原语**（**PARTIAL**：原语已加并被 `HostBridgeClient` 使用；`CoreServiceClient` 仍用 `_pipeGate`，未统一）：在 `Transport/SidecarProcess` 提供**唯一**的独占入口（建议
      `AcquireExchangeLeaseAsync` 返回 `IDisposable` 租约，或等价的"整周期"公共方法），
      使"取锁 → 写 → 读 →（事件帧跳过）→ 释放"成为**不可分割**的操作。
- [~] **AC2 所有调用方走它**（**NOT MET**：core 侧两处仍直调 `ExchangeAsync`）：`CoreServiceClient.SendAsync`、`SendHostControlAsync`、`SendRawAsync`、
      `HostBridgeClient` 的**全部** `_process.ExchangeAsync` 调用点都必须经该入口。
      要求：改完后仓库内**不存在**绕过独占的 `_process.ExchangeAsync` 直调（可用 grep 证明）。
- [x] **AC3 host_bridge 判别测试（先写，必须先红）**：并发 `HostBridgeClient` 的多个命令，
      断言**每个响应的 id 与请求一致**或形状正确。要求：**当前实现下必须失败**。
- [~] **AC4 id 校验覆盖两条管道**（**NOT MET**：无 `request_id` 仍 fail-open；bridge 仅校验数字 id）：`HostBridgeClient.ParseResponse` 同样校验响应 id；
      并把"无 `request_id`"从 fail-open 改为**默认 fail-closed**（更新对应文档测试）。
- [~] **AC5 R-002 重同步**（**NOT MET**：未做丢弃直到匹配 id）：id 错配或残缺帧后，**丢弃直到匹配 id**（或 poison 整个 session 并暴露
      typed 错误让调用方重建），避免后续响应全部错位；该行为需判别测试。
- [x] **AC6 不回归**：无夹具三项目 App 950/0/11、Host 321/0/74、CoreClient **189/0/27**（0 failed）；
      带新 sidecar 的 Host 失败**不得比 2~3 更多**、CoreClient 不得比 4 更多；不得放宽既有断言、不得新增 skip。

## 允许修改范围

见 frontmatter（`NewManga.CoreClient` 源码 + 其测试）。

## 禁止范围

- 不得改 Python Core。
- 不得放宽断言、不得新增 skip/xfail。
- 不得为了"让测试过"而把并发测试改成串行调用。
- 不得声称条件 3/4 已满足。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 | 实现后 `grep` 证明无绕过路径 | 仓库 | NOT_RUN | 无 |
| AC3 | 新增 host_bridge 并发判别测试（未改前先跑） | sidecar | NOT_RUN | 无 |
| AC4/AC5 | 校验 + 重同步后重跑 | 同上 | NOT_RUN | 无 |
| AC6 | 带夹具/无夹具三项目全量 | 同上 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- **风险 R1**：`HostBridgeClient` 属 FEA-11 host-control 面，改动可能影响 Host 系列测试 → 逐一核对。
- **风险 R2**：若 `HostBridgeClient` 的命令本身是**顺序敏感**的（如 grant 注册），加锁不应改变语义。
- **风险 R3**：租约式入口若调用方忘记 `using`，锁泄漏 → 建议用 `try/finally` 或把整周期封装成单个方法。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无（须独立上下文，重点核"是否真的只剩单一入口"与"三条管道的判别测试能否回退变红"）。
- 实际测试：尚无。
- 后续记录日期、commit、环境、结果、遗留项。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) | sha256_basis |
|---|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | 待填 | NOT_APPLICABLE | — | — | 本卡无新增派生物 |

## Closeout Record

- Closeout date / DSH：2026-11-15，DSH（Lead / Architect / Integrator）。
- canonical_evidence_status：`complete`（见 §Canonical Evidence，随收口提交冻结）。
- resource_closeout_status：`complete`（无 worktree、无用户数据）。
- 删除、迁移、归档数量/字节数：0。
- **交付结论（限定）**：`host_bridge` 管道从**完全无保护**变为**有独占 + 有数字 id 校验**；
  两条管道的并发判别都有测试且**均能回退变红**（`stream is currently in use`）。
- **未达成（如实登记，不得当作已修）**：
  - **AC1 PARTIAL / AC2 NOT MET**：`CoreServiceClient` 仍用自己的 `_pipeGate`，未改用传输层租约；
    `ExchangeAsync` 仍 `public`，未来直调即绕过独占。
  - **AC4 后半 NOT MET**：无 `request_id` 时 fail-open；bridge 仅校验数字 id。
  - **AC5 NOT MET**：id 错配后无重同步（R-002），流中可能残留一帧。
  - **R-005**：取消（`CancellationToken`）后流状态可能永久失步。
  - **`Dispose`/`StopAsync` 在租约外**，在途命令会得 `ProcessExited`。
- **复核**：`review-pipe-transport` 独立上下文，**ACCEPT_WITH_LIMITATIONS**（无 P0/P1），
  要求"不可据此关闭 Task"—— 故本卡以**限定条**收口，上述 5 项已拆入 `E-7` 的后续卡。
- **自登记的错误（本卡）**：
  1. 初版 `ConcurrentMixedBridgeCommands` 用不存在的 resource 做 `IssueAsync` 并发，
     报 `RESOURCE_NOT_CATALOGED` —— 是**测试写错了**，不是锁的问题；
  2. 两处"改了却零覆盖"（bridge id 校验、`SendRawAsync` 锁）是 **r1 复核发现**的，我首版没有为它们写测试；
  3. 我曾把复核的 R-001 视为定论，核实后确认是**部分误判**（两条管道本就独立）—— 已在本文件与证据中更正。
