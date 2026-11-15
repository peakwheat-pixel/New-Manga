---
id: E7-2-FAILCLOSED-1
title: E-7 #2 —— 按 Codex 裁决把生产路径改为 fail-closed（无 request_id 不再视为属于本请求）
kind: defect
governance_version: 3
status: done
suggested_owner: DSH
owner: DSH
reviewer: e7-2-review（r1，CHANGES_REQUESTED）+ e7-2-review-r2（r2，APPROVED_WITH_LIMITATIONS）
integration_commit: 6b847ab91
canonical_evidence_status: complete
resource_closeout_status: complete
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
  `BelongsToRequest` 由 `private` 改为 `internal`（**r2 更正理由**：同类型的 `private` 成员本来就可被 `EnsureResponseBelongsToRequest` 互调，改 `internal` 的真正目的是让**测试直接断言谓词**；仍非 `public`，不违反裁决「不加新公开 API」）；
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

生产路径对「无 id 非事件帧」fail-closed；全量 **210 passed / 0 failed / 30 skipped** 不退化。

## Acceptance Criteria

- [x] **AC1 按裁决实施**：`BelongsToRequest` 收紧为「必须 id 完全相等」。 <<MET>>
- [x] **AC2 `SendRawAsync` 语义保持**：确认它不经 `BelongsToRequest`，原始观察语义不变。 <<MET>>
- [x] **AC3 事件帧不受影响**：`IsEventFrame` 守卫保持，事件帧仍被跳过。 <<MET>>
- [x] **AC4 测试同步**：原 fail-open 用例改为 fail-closed 用例并断言 drain 次数。 <<MET>>
- [x] **AC5 不回归**：全量 **210 / 0 / 30**；四件套 PASS。 <<MET>>
- [x] **AC6 独立复核**：固定 head 交独立上下文 Review。 <<MET>>

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
| 定向 | `--filter "R002ResyncTests\|PipeResponsePairingValidationTests"` | 14 passed |
| 全量 | `dotnet test …NewManga.CoreClient.Tests.csproj` | 210 / 0 / 30 |
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
| §5.3 其它用例：**错 id→无 id→匹配**（多帧混合）、**无 id 耗尽预算→poison**、**事件帧+无 id 混排**、**raw 的 idless 请求错误仍可观察** | ❌ 均未做（同上，缺假 sidecar 夹具） |
| **bridge 侧**同类 fail-open（`HostBridgeClient.ParseResponse` 在 `expectedId == null` 时不校验） | ❌ 不在本卡范围，需另一份裁决 |
| `AcquireExchangeLeaseAsync` / `ReadNextResponseLineAsync` 仍 `public` | ❌ E7-1 明确不做 |
| `R002-RESYNC-1` 的 P2-F1（测试不覆盖调用点） | ❌ 仍未关闭 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-E72-01 | AC1/AC4 全量不回归（210/0/30） | verification/E7-2-FAILCLOSED-1/coreclient-full.log | 1aa27c0cb | 7a16ee7f203a16944307eb2cdab0d13da752a7849b4c4ca98f5fe36d6904b89a | CANONICAL | BLOB |
| EV-E72-02 | AC1/AC2/AC3/AC4 修复 diff | verification/E7-2-FAILCLOSED-1/fix.diff | 1aa27c0cb | faca1bf24dc5eb87617648db419d3fd2116a0a3f0308ecd0c0a40bd1c48a69bb | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/E7-2-FAILCLOSED-1/ | NOT_APPLICABLE | — | — | 新增证据，无迁移/归档 |

## Closeout Record

- Closeout：2026-11-16，DSH；实现 `16bac8f91` + r1 返修 `6b847ab91` + r2 处置（本提交）。
- **裁决采纳**：Codex 2026-11-16（`doc/reviews/E7-2-FAILOPEN-RULING-codex-2026-11-16.md`），
  verdict「条件化：生产路径 fail-closed；`SendRawAsync` 保留原始语义，不加 opt-out 开关」。
  DSH 以其名义集成。
- **结果**：
  - `BelongsToRequest` 改为严格谓词（必须 id 完全相等），生产重同步路径 fail-closed；
  - `EnsureResponseBelongsToRequest` **复用同一谓词**（r1 F1：初版误读裁决为「可以不改 Ensure」，
    已改）；错误消息**区分**「无可用 id」与「id 错配」（r2 R2-01）；
  - `SendRawAsync` 语义未变（不经过 `BelongsToRequest`）；
  - 事件帧守卫不变；两处旧断言已迁移（r1 F2/§5.3 要求）。
- **独立复核两轮**：r1 `CHANGES_REQUESTED`（0/1/1/3）→ r2 `APPROVED_WITH_LIMITATIONS`（0/0/3/4）。
- **门禁**：定向 **14 passed**；全量 **210 passed / 0 failed / 30 skipped / EXIT=0**；
  `check.ps1` PASS (3 warnings)｜`verify_pins` 18/18｜`api_inventory` 1/80/6=87。
- **未关闭项（不淡化）**：
  1. **裁决 §5.3 的动态证据缺口**：真实 `SendAsync`/`SendHostControlAsync` 调用链的假 sidecar 测试
     未做（`StartAsync` 需 `core.ping` 握手），以及「错 id→无 id→匹配」「无 id 耗尽→poison」
     「事件+无 id 混排」「raw idless 观察」等用例 ⇒ **`E-7 #2` 整项不得据此关闭**；
  2. **bridge 侧**同类 fail-open（`HostBridgeClient.ParseResponse` 在 `expectedId == null` 时不校验）
     **未处理**，需另一份裁决；
  3. `R002-RESYNC-1` 的 P2-F1（测试不覆盖调用点）仍未关闭；
  4. `-TaskPath` 因 DAG 未登记而 FAIL（表外卡既有边界，标 done 后消解）。

