---
id: E7-2-FAILCLOSED-1
title: E-7 #2 —— 按 Codex 裁决把生产路径改为 fail-closed（无 request_id 不再视为属于本请求）
kind: defect
governance_version: 3
status: in_progress
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - E7-1-UNIFY-LEASE-1
approval: Codex 裁决 2026-11-16（doc/reviews/E7-2-FAILOPEN-RULING-codex-2026-11-16.md）；用户 2026-11-15「全部授权」
base_commit: 2bcb58fa7
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/E7-2-FAILCLOSED-1
allowed_paths:
  - doc/tasks/E7-2-FAILCLOSED-1.md
  - doc/reviews/E7-2-FAILOPEN-RULING-codex-2026-11-16.md
  - apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/R002ResyncTests.cs
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/PipeResponsePairingValidationTests.cs
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/E7-2-FAILCLOSED-1/**
---

# E7-2-FAILCLOSED-1：按裁决实施 fail-closed

## 裁决（Codex，2026-11-16，已落盘署名）

> **verdict：条件化 —— 生产路径改为 fail-closed；`SendRawAsync` 保留原始 wire 观察语义，
> 不新增允许无 id 开关。**

关键理由（摘自裁决）：

1. **独占只能保证串行访问，不能证明响应归属**；风险还包括本请求响应损坏、重复帧、
   以及重同步提前结束；
2. 事件帧已有排除守卫（`IsEventFrame`），**无需为其保留生产 fail-open**；
3. Core 的无关联 id 错误响应确实存在，但**未发现正常生产请求必须接受它的兼容依据**；
4. **最小修复应收紧生产使用的 `BelongsToRequest`**，复用有界重同步；仅修改无生产调用的
   `EnsureResponseBelongsToRequest` 不足。

**DSH 采纳**：本卡按上述裁决实施，实施与集成以 DSH 名义记录。裁决范围只覆盖契约与最小方案，
不批准既有实现、不关闭 E-7、不改变 Release Gate。

## 实施

### 改了什么

`CoreServiceClient.BelongsToRequest`：

```csharp
// before（fail-open）
response.RequestId is not { } actual || string.Equals(actual, requestId, ...)
// after（fail-closed）
response.RequestId is { } actual && string.Equals(actual, requestId, StringComparison.Ordinal)
```

⇒ 无 `request_id` 的**非事件帧**不再被视为属于本请求：它会被**有界重同步**（16 帧）丢弃；
若预算内仍无匹配帧，渠道 **poison**（而不是静默交出无法验证的响应）。

### 没改什么（按裁决）

- **`SendRawAsync` 不改**：它是原始 wire 观察钩子，走 `CoreProtocol.Parse` 直接返回，
  **从不经过 `BelongsToRequest`** ⇒ 裁决要求的「保留原始语义、不新增 opt-out 开关」已天然满足；
- ~~`EnsureResponseBelongsToRequest` 不改~~ —— **该判断错误（r1 F1 指出）**：裁决原文 §5.1 是
  「它**若保留，应复用同一严格谓词**」、§5.3 是「**不能只改 Ensure，也不能只改 Parse**」，
  我把它误读为「可以不改 Ensure」。**返修已改**：`EnsureResponseBelongsToRequest` 现在复用
  同一个 `BelongsToRequest` 严格谓词（无/非法 id ⇒ `MalformedResponse`），
  `BelongsToRequest` 由 `private` 改为 `internal` 以共享（仍非 public，不违反裁决「不加新公开 API」）；
- 事件帧排除守卫 `!CoreProtocol.IsEventFrame(line)` 不变。

### 测试影响（契约变更，测试随之改）

两处旧断言都已迁移（裁决 §5.3 要求「必须同时迁移」）：

1. `R002ResyncTests.ResponseWithoutRequestId_IsAcceptedWithoutDraining`
   → `ResponseWithoutRequestId_IsTreatedAsMismatch_AndDrained`
   （无 id 的非事件帧被 drain 1 次，拿到匹配响应后才成功，未 poison）；
2. `PipeResponsePairingValidationTests.MissingRequestId_CurrentlyFailsOpen_DocumentedLimitation`
   → `MissingRequestId_ThrowsTypedMalformedResponse`（无 id ⇒ `MalformedResponse`，消息含 `<missing>`）；
   并新增 `NonStringOrEmptyRequestId_ThrowsTypedMalformedResponse`（`null`/数字/布尔/对象/数组/空串
   六种形态参数化）与 `BelongsToRequest_IsStrict_ForMissingAndMismatchedIds`（谓词与判据一致性）。

## 目标（一个可观察结果）

生产路径对「无 id 非事件帧」fail-closed；全量 **203 passed / 0 failed / 30 skipped** 不退化。

## Acceptance Criteria

- [ ] **AC1 按裁决实施**：`BelongsToRequest` 收紧为「必须 id 完全相等」。
- [ ] **AC2 `SendRawAsync` 语义保持**：确认它不经 `BelongsToRequest`，原始观察语义不变。
- [ ] **AC3 事件帧不受影响**：`IsEventFrame` 守卫保持，事件帧仍被跳过。
- [ ] **AC4 测试同步**：原 fail-open 用例改为 fail-closed 用例并断言 drain 次数。
- [ ] **AC5 不回归**：全量 **203 / 0 / 30**；四件套 PASS。
- [ ] **AC6 独立复核**：固定 head 交独立上下文 Review。

## 允许修改范围

见 frontmatter `allowed_paths`。裁决文件本身只读引用，不改内容。

## 禁止范围

- 不得给 `SendRawAsync` 新增「允许无 id」的开关（裁决明确不做）；
- 不得放宽 `BelongsToRequest` 的判据；
- 不得改变事件帧跳过语义；
- 不得顺带改 bridge 侧（那是独立的 fail-open 面，需单独裁决）。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| 定向 | `--filter "R002ResyncTests\|PipeResponsePairingValidationTests"` | 7 passed |
| 全量 | `dotnet test …NewManga.CoreClient.Tests.csproj` | 203 / 0 / 30 |
| 四件套 | check / pins / inventory | PASS / 18-18 / 87 |

## 裁决 §5.3 的未实施项（如实登记，不淡化）

裁决要求在**真实的 `SendAsync` / `SendHostControlAsync` 调用链**上各有确定性假 sidecar 测试，
覆盖「握手后注入坏帧与正常匹配帧」，以证明生产调用点确实使用严格 helper。

**本轮未做**：`CoreServiceClient.StartAsync` 会先发 `core.ping` 并要求 `Ready` + 协议主版本匹配，
假 sidecar 需实现完整握手协议；本轮无此夹具预算。风险由 r1 复核的静态确认部分覆盖
（`BelongsToRequest` 全仓唯一生产调用点是 `ReadResponseForRequestAsync:2438`，
而 `ReadResponseForRequestAsync` 被两处调用点使用），但**没有动态证据**。

⇒ 这属于本卡**已知缺口**；`E-7 #2` 整项**不得**据此关闭。

## 残余清单

| 项 | 状态 |
|---|---|
| `EnsureResponseBelongsToRequest` 严格化 + 两处旧断言迁移 | ✅ 本轮完成 |
| 非法 id 六种形态覆盖 | ✅ 本轮完成 |
| 真实调用链（`SendAsync`/`SendHostControlAsync`）的假 sidecar 测试 | ❌ 未做（见上） |
| **bridge 侧**同类 fail-open（`HostBridgeClient.ParseResponse` 在 `expectedId == null` 时不校验） | ❌ 不在本卡范围，需另一份裁决 |
| `AcquireExchangeLeaseAsync` / `ReadNextResponseLineAsync` 仍 `public` | ❌ E7-1 明确不做 |
| `R002-RESYNC-1` 的 P2-F1（测试不覆盖调用点） | ❌ 仍未关闭 |

## 证据

裁决文件、全量日志、修复 diff 写入 `doc/reviews/` 与 `verification/E7-2-FAILCLOSED-1/`。
