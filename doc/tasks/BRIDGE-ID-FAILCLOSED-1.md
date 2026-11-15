---
id: BRIDGE-ID-FAILCLOSED-1
title: 按 Codex 裁决把 bridge 侧 id 校验改为 fail-closed（洞 2），并对不可归属响应 poison 通道
kind: defect
governance_version: 3
status: done
suggested_owner: DSH
owner: DSH
reviewer: bridge-id-review（独立上下文子 agent，APPROVED_WITH_LIMITATIONS 0/1/3/3）
integration_commit: 6f6fdda13
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC1 洞 2 收紧**：`expectedId != null` 时响应必须有精确匹配的 `Int32 id`，否则 `MalformedResponse`。 <<MET>>
- [x] **AC2 洞 1 保留**：`expectedId == null`（raw）对无 id 帧仍返回结果。 <<MET>>
- [x] **AC3 生产调用点 poison**：`SendAsync` 捕获 `MalformedResponse` 后先 `_process.Poison()` 再抛，且在租约释放前（`using var lease` 作用域内）。 <<MET>>
  > **限定（r1 F-01）**：接线**已实施**，但**无测试覆盖** —— 变异实测「删掉 `_process.Poison()` ⇒ 全量仍 222 passed / EXIT 0（存活）」。动态证据由 `BRIDGE-FAKE-HARNESS-1` 承接（DSH 裁决 2026-11-16）。
- [x] **AC4 测试迁移**：第 3 条按裁决改名并反转断言；新增 7 形态参数化与 raw 保留用例。 <<MET>>
- [x] **AC5 不回归**：全量 **222 / 0 / 30**；四件套 PASS。 <<MET>>
- [x] **AC6 独立复核**：固定 head 交独立上下文 Review。 <<MET>>

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

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-BID-01 | AC4/AC5 全量不回归（222/0/30） | verification/BRIDGE-ID-FAILCLOSED-1/coreclient-full.log | 6f6fdda13 | 781725c5ba400238d93df77bbb658c7f372190f32bc755e9b84b14285dbcb853 | CANONICAL | BLOB |
| EV-BID-02 | AC1/AC3 修复 diff | verification/BRIDGE-ID-FAILCLOSED-1/fix.diff | 6f6fdda13 | 720b1091477677e982a8d22c5049d1754892aaa15835b6843b9b862a8b05956b | CANONICAL | BLOB |
| EV-BID-03 | AC3 变异证据（删 Poison ⇒ **存活**） | verification/BRIDGE-ID-FAILCLOSED-1/mutation-poison-removed.log | 6f6fdda13 | 96498aa69946e9d1f7aa8f618539304f7d4754e71b9b8514bb1c3444d9ca7764 | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/BRIDGE-ID-FAILCLOSED-1/ | NOT_APPLICABLE | — | — | 新增证据，无迁移/归档 |

## Closeout Record

- Closeout：2026-11-16，DSH；实现 `6f6fdda13`。
- **裁决采纳**：Codex 2026-11-16（`doc/reviews/E-7-BRIDGE-ID-RULING-codex-2026-11-16.md`），
  verdict「洞 1 保留；洞 2 fail-closed；立即拒绝并 poison，不新增重同步」。DSH 以其名义集成。
- **结果**：
  - `ParseResponse` 三段式严格判据（缺失 / 非 Int32 / 值不匹配，各自独立 `MalformedResponse`）；
  - `expectedId == null`（raw）**保持观察语义**（洞 1）；
  - `SendAsync` 在**租约释放前**捕获 `MalformedResponse` ⇒ `_process.Poison()` ⇒ 重抛；
    业务 `BridgeException` 不进该 catch；`SendRawAsync` 不套；
  - 测试迁移：第 3 条**改名并反转断言**；新增 7 形态参数化 + raw 保留用例。
- **独立复核**：`bridge-id-review` **APPROVED_WITH_LIMITATIONS**（0/1/3/3）。它用**强制重建后的反射探测**
  逐字验证三类错误消息与裁决一致，并做了反向变异（收紧 raw ⇒ RED；`kind` 顺序反 ⇒ 5 红），
  证明 parser 层测试**有判别力**。
- **r1 的方法学告警（已采纳为纪律）**：从备份恢复源文件会保留旧时间戳，`dotnet build` 可能**跳过重编译**，
  导致测试跑的是上一次变异的 DLL。**后续所有变异验证必须 `dotnet build --no-incremental` 强制重建。**
- **门禁**：定向 **11 passed**；全量 **222 passed / 0 failed / 30 skipped / EXIT=0**；
  `check.ps1` PASS (3 warnings)｜`verify_pins` 18/18｜`api_inventory` 1/80/6=87。
- **未关闭项（不淡化）**：
  1. ~~**F-01：poison 接线无测试覆盖**（变异存活已实测）。~~ **已关闭**：`BRIDGE-FAKE-HARNESS-1` 建成 `FakeBridgeHost` 夹具并补了 2 条经真实 `StartAsync` → `IssueAsync` 链的动态测试；**变异实测**「删掉 `_process.Poison()` ⇒ 2 条变红」。
     **剩余**：core 侧 host-control 的同类分支仍未覆盖（见该卡未关闭项 1）；
  2. **`E-7 #2` 继续开放**，本卡**不得**被引用为「bridge 侧会话安全」的证据；
  3. 裁决 §4 还要求的这些边界仍未覆盖：error 信封先于 id 校验、匹配 id 的业务错误不 poison、
     握手期非法 id ⇒ `HandshakeFailed`（内层 `MalformedResponse`）、raw + error 仍 `BridgeException`；
  4. **`-TaskPath` 曾 FAIL**（「当前 DAG 未登记非终态 Task」，`check.ps1:702`）—— 标 `done` 后消解。

