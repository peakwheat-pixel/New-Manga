---
id: BRIDGE-ID-FAILCLOSED-1
title: 按 Codex 裁决把 bridge 侧 id 校验改为 fail-closed（洞 2），并对不可归属响应 poison 通道
kind: defect
governance_version: 3
status: in_progress
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - E7-2-DYNAMIC-EVIDENCE-1
approval: Codex 裁决 2026-11-16（doc/reviews/E-7-BRIDGE-ID-RULING-codex-2026-11-16.md）；用户 2026-11-15「全部授权」
base_commit: 8b4bc2748
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/BRIDGE-ID-FAILCLOSED-1
allowed_paths:
  - doc/tasks/BRIDGE-ID-FAILCLOSED-1.md
  - doc/reviews/E-7-BRIDGE-ID-RULING-codex-2026-11-16.md
  - apps/desktop-avalonia/src/NewManga.CoreClient/Bridge/HostBridgeClient.cs
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Bridge/BridgeResponseIdValidationTests.cs
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/BRIDGE-ID-FAILCLOSED-1/**
---

# BRIDGE-ID-FAILCLOSED-1：bridge 侧 fail-closed

## 裁决（Codex，2026-11-16，已落盘署名）

> **洞 1 保留；洞 2 改为 fail-closed。**
> - raw 保留不做关联校验的观察语义，与 core 裁决一致；
> - 生产响应必须携带精确匹配的 `Int32 id`；缺失、类型非法、越界或错配均为 `MalformedResponse`；
> - bridge 应立即拒绝并 **poison 通道**，不新增重同步循环；
> - 三条既有测试中，第 3 条必须从「接受无 id」迁移为「拒绝无 id」。

裁决还说：**「静态 parser 只负责判定并抛错，持有 process 的生产调用点负责禁用通道；不能只改 parser 就宣布会话安全。」**

**DSH 采纳**：本卡按裁决实施，以 DSH 名义集成。

## 被修的两个洞

`ParseResponse` 原判据：

```csharp
if (expectedId is { } wanted && root.TryGetProperty("id", out var actualId)
    && actualId.ValueKind == JsonValueKind.Number && actualId.TryGetInt32(out var actual)
    && actual != wanted) { throw ...; }
```

条件链**短路** ⇒ 响应缺失 `id` 或 id 非 Int32 时**整个 if 为 false** ⇒ 静默接受。
生产 `SendAsync` 是传 `expectedId` 的，所以这不是 raw 的特例，而是**每个生产命令都暴露**的洞。

## 实施

### 3.1 parser 改为严格（`ParseResponse`）

按裁决逐字实施，三类错误消息明确区分：

| 场景 | 消息关键词 |
|---|---|
| 缺属性 | `response is missing id (expected Int32 N)` |
| 类型/数值非法 | `response id is not an Int32 JSON number (expected N; kind X)` |
| 合法 Int32 但值不同 | `response id X does not match request Y` |

一律 `MalformedResponse`；不新增错误码；不做字符串解析/浮点截断/补填期望值。
`expectedId == null`（raw 调用点）**保持原语义**。

### 3.2 生产调用点负责 poison（`SendAsync`）

```csharp
try { return ParseResponse(method, frame.ResponseLine, requestId); }
catch (SidecarException ex) when (ex.Code == SidecarErrorCode.MalformedResponse)
{
    _process.Poison();
    throw;
}
```

在**租约释放前**执行（`using var lease` 的作用域内），因此排队中的下一请求不能在 poison 前写入。
匹配 id 的业务 `BridgeException` **不进**这个 catch —— 业务失败仍保留可用会话。
`SendRawAsync` **不套**这段 catch（保持原始行为）。

### 测试迁移（裁决 §4）

| 原测试 | 处置 |
|---|---|
| `MismatchedNumericId_ThrowsMalformedResponse` | 保留 |
| `MatchingNumericId_IsAccepted` | 保留 |
| `MissingId_CurrentlyFailsOpen_DocumentedLimitation` | **改名为 `MissingId_ThrowsMalformedResponse`**，断言 `MalformedResponse` + 消息含 `missing id` 与期望 id |
| — | 新增 `NonInt32Id_ThrowsMalformedResponse`（7 形态参数化：`null` / `"1"` / `true` / `{}` / `[]` / `1.5` / 超 Int32） |
| — | 新增 `RawWithNoExpectedId_StillObservesIdlessFrame`（证明洞 1 保留） |

## 目标（一个可观察结果）

生产 `ParseResponse` 对缺失/非法/错配 id 一律 `MalformedResponse`；raw 保持观察语义；
全量 **222 passed / 0 failed / 30 skipped**。

## Acceptance Criteria

- [ ] **AC1 洞 2 收紧**：`expectedId != null` 时响应必须有精确匹配的 `Int32 id`，否则 `MalformedResponse`。
- [ ] **AC2 洞 1 保留**：`expectedId == null`（raw）对无 id 帧仍返回结果。
- [ ] **AC3 生产调用点 poison**：`SendAsync` 捕获 `MalformedResponse` 后先 `_process.Poison()` 再抛，且在租约释放前。
- [ ] **AC4 测试迁移**：第 3 条按裁决改名并反转断言；新增 7 形态参数化与 raw 保留用例。
- [ ] **AC5 不回归**：全量 **222 / 0 / 30**；四件套 PASS。
- [ ] **AC6 独立复核**：固定 head 交独立上下文 Review。

## 允许修改范围

见 frontmatter `allowed_paths`：只改 `HostBridgeClient`（parser + 一个 catch）与一个测试文件。

## 禁止范围

- 不得改 Python Core、wire 形状、Schema、依赖或公开签名；
- 不得给 raw 调用点加关联校验（裁决洞 1）；
- 不得新增重同步循环（裁决明确：bridge 只抛错 + poison）；
- 不得为测试扩大生产公共 API（裁决 §4 末段）。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| 定向 | `--filter FullyQualifiedName~BridgeResponseIdValidationTests` | 11 passed |
| 全量 | `dotnet test …NewManga.CoreClient.Tests.csproj` | 222 / 0 / 30 |
| 四件套 | check / pins / inventory | PASS / 18-18 / 87 |

## 证据

裁决文件、全量日志、变异日志、修复 diff 写入 `doc/reviews/` 与 `verification/BRIDGE-ID-FAILCLOSED-1/`。
