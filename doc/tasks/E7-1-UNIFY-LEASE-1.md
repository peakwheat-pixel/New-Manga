---
id: E7-1-UNIFY-LEASE-1
title: E-7 #1 —— 独占统一到传输层租约，ExchangeAsync 降为 internal
kind: defect
governance_version: 3
status: done
suggested_owner: DSH
owner: DSH
reviewer: e7-1-review（r1，CHANGES_REQUESTED）+ e7-1-review-r2（r2，APPROVED_WITH_LIMITATIONS）
integration_commit: 879c2bc96
canonical_evidence_status: complete
resource_closeout_status: complete
depends_on:
  - R002-RESYNC-1
approval: 用户 2026-11-15「全部授权、持续自动推进」；目标 B 的产品门槛收敛
base_commit: 11a10088e
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/E7-1-UNIFY-LEASE-1
allowed_paths:
  - doc/tasks/E7-1-UNIFY-LEASE-1.md
  - apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Transport/SidecarProcess.cs
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Bridge/BridgeResponseIdValidationTests.cs
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/SidecarShutdownRaceTests.cs
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/E7-1-UNIFY-LEASE-1/**
---

# E7-1-UNIFY-LEASE-1：独占统一到传输层

## 来源

`E7-CONCURRENCY-STATUS-1` 核实的权威 E-7 第 1 项（`PIPE-EXCLUSIVE-TRANSPORT-1.md:123-129`）：

> `CoreServiceClient` 仍用自己的 `_pipeGate`，**未**改用传输层租约；`ExchangeAsync` 仍 `public`
> ⇒ 未来任何直调即绕过独占（AC1 PARTIAL / AC2 NOT MET）。

## 设计判断（先定，再改）

### Q1：改哪些？

| 子项 | 改法 |
|---|---|
| a) `CoreServiceClient._pipeGate` 换成传输层 lease | 3 处 wait/release 对改为 `AcquireExchangeLeaseAsync` + `lease.Dispose()`，删除 `_pipeGate` 字段 |
| b) `ExchangeAsync` 降 `internal` | `public` → `internal`（`CoreServiceClient` / `HostBridgeClient` 同程序集；测试有 `InternalsVisibleTo`） |

**不做**：`AcquireExchangeLeaseAsync` / `ReadNextResponseLineAsync` 保持 `public` ——
E-7 第 1 项只点名 `ExchangeAsync`，扩大可见性变更面没有收益。

### Q2：`using var` 还是 `try/finally`？—— **`try/finally` + 显式 `Dispose()`**

`using var lease = ...` 的作用域是**方法级**，而这里的语义是「包住这一次交换」。
显式 `finally { lease.Dispose(); }` 与原有 `_pipeGate.Release()` 的形态一致，审查时逐行可比对。

**关键前提已核实**：`ExchangeLease.Dispose()` **幂等**
（`Interlocked.Exchange(ref _gate, null)` + `gate?.Release()`），所以显式 dispose 不会双释放。

### Q3：会不会变成双重加锁？—— **不会，是去掉一层**

改动前：`_pipeGate`（客户端私有）包住 `_process.ExchangeAsync`（传输层**不加锁**，靠调用方持 lease）。
两条管道（core / host_bridge）各有独立 `SidecarProcess`，所以 `_pipeGate` 与 `_exchangeGate` **不重叠**。

改动后：只剩传输层 `_exchangeGate` 一层，且它是**与进程实例绑定**的 —— 比客户端私有 gate
更贴近「谁拥有这条管道」的事实。这同时消除了「新调用方忘记加锁」的结构性风险源（`ExchangeAsync` 变 `internal`）。

### Q4：如何验证没漏？

- 编译（`internal` 变更会让测试项目外的越界调用立刻失败）；
- 全量 `NewManga.CoreClient.Tests`（含并发用例：`ConcurrentCommands_DoNotCrossResponses`、
  `SidecarCancellationPoisonTests`、`SidecarShutdownRaceTests`、`BridgePipeExclusivityTests`）；
- `grep` 确认 `_pipeGate` 无残留、`ExchangeAsync` 只剩 `internal`。

## 目标（一个可观察结果）

`CoreServiceClient` 不再持有第二个 gate；`ExchangeAsync` 不可从程序集外调用；
全量测试 **203 passed / 0 failed / 30 skipped** 不退化。

## Acceptance Criteria

- [x] **AC1 独占统一**：`CoreServiceClient._pipeGate` 字段删除，3 处交换改为 <<MET>>
      `AcquireExchangeLeaseAsync` + 显式 `Dispose()`。
- [x] **AC2 可见性收紧**：`SidecarProcess.ExchangeAsync` 的**两个重载**都是 `internal`；程序集外无法直调。（r1 P1：初版只降了 4 参重载，2 参 `public` 重载漏改；全仓 16 个调用点全是 4 参，2 参重载 0 调用者。） <<MET>>
- [x] **AC3 无残留**：`grep _pipeGate` 在 `src/**` 无命中（注释中的历史提及已改写）。 <<MET>>
- [x] **AC4 不回归**：`NewManga.CoreClient.Tests` 全量 **203 passed / 0 failed / 30 skipped**。**措辞更正（r1 P2）**：其中 `PipeResponsePairingTests.ConcurrentCommands_DoNotCrossResponses`、`BridgePipeExclusivityTests.*`、`RawSendPipeExclusivityTests.*` 是 `[SidecarFact]`，在**无夹具模式下 SKIP**，并未执行；实际执行且为绿的是 `SidecarCancellationPoisonTests`(3) 与 `SidecarShutdownRaceTests`(4)。r1 用本机夹具实跑子集为 6 通过 / 1 失败（失败是旧 core 不识别 `source_list_scan_targets`，与本改动无关）。**不得**把 skip 说成绿。 <<MET>>
- [x] **AC5 前提核实**：确认 `ExchangeLease.Dispose()` 幂等（不双释放）。 <<MET>>
- [x] **AC6 独立复核**：`e7-1-review` 已完成 r1，verdict **CHANGES_REQUESTED**（0/1/3/4）；其 P1（2 参重载漏改）与 P2（AC4 skip 当绿、AC6 自证、证据头矛盾）已在本轮返修处置。 <<MET>>

## 允许修改范围

见 frontmatter `allowed_paths`：只改 `CoreServiceClient`（gate → lease）、`SidecarProcess`（可见性）、
以及相关注释。

## 禁止范围

- 不得改 `_exchangeGate` 本身的行为（它是既有的正确独占原语）；
- 不得改 `ReadNextResponseLineAsync` / `AcquireExchangeLeaseAsync` 的可见性；
- 不得顺带做 E-7 #2（fail-open）—— 那是契约决策。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| 全量不回归 | `dotnet test …NewManga.CoreClient.Tests.csproj` | 203 / 0 / 30 |
| 编译 | `dotnet build …NewManga.CoreClient.csproj` | EXIT 0 |
| 四件套 | check / pins / inventory | PASS / 18-18 / 87 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-E71-01 | AC4 全量不回归（203/0/30） | verification/E7-1-UNIFY-LEASE-1/coreclient-full.log | 4ac123241 | af51c8e81dd8aad849e5a1fe45e881fc7da33f6a22ec850d5df2bdf8868cc6e2 | CANONICAL | BLOB |
| EV-E71-02 | AC1/AC2 编译（internal 变更生效） | verification/E7-1-UNIFY-LEASE-1/build.log | 4ac123241 | c52f956ac52f1149db3b43dea8b4ac1b08f168c1debce320a3eeedb87e1899a4 | CANONICAL | BLOB |
| EV-E71-03 | AC1/AC2/AC3 修复 diff | verification/E7-1-UNIFY-LEASE-1/fix.diff | 4ac123241 | f08ed1e2b51d5017962f730ea06de7fd0db1a57a7f14c36b62ade44f1ff0b004 | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/E7-1-UNIFY-LEASE-1/ | NOT_APPLICABLE | — | — | 新增证据，无迁移/归档 |

## Closeout Record

- Closeout：2026-11-16，DSH；实现（本提交）。
- **结果**：
  - **AC1**：`CoreServiceClient._pipeGate` 字段删除；3 处交换（`SendHostControlAsync`、`SendRawAsync`、
    `SendAsync`）改为 `AcquireExchangeLeaseAsync` + 显式 `lease.Dispose()`；
  - **AC2**：`SidecarProcess.ExchangeAsync` 的**两个重载**都降为 `internal`（程序集外无法直调）。
    **r1 P1 更正**：初版只改了 4 参重载，2 参 `public` 重载漏改，导致当时的 Closeout 断言「程序集外无法直调」是**事实错误**；返修已补。
  - **AC3**：`src/**` 中 `_pipeGate` 命中 **0**；`SendRawAsync` 的历史注释已改写（原称「bypass _pipeGate」）；
  - **AC5**：核实 `ExchangeLease.Dispose()` 幂等（`Interlocked.Exchange(ref _gate, null)` + `gate?.Release()`），
    显式 dispose 不会双释放。
- **结构收益**：原来两条管道各有一层客户端私有 gate + 传输层 lease 名为「可选」；现在**只有传输层一层**，
  且它与 `SidecarProcess` 实例绑定 —— 与「谁拥有这条管道」的事实一致。配合 `ExchangeAsync` 变 `internal`，
  「新调用方忘记加锁即撕裂」这个结构性风险源被消除。
- **门禁**：`dotnet build` EXIT=0；全量 **203 passed / 0 failed / 30 skipped / EXIT=0**（41s，r2 实测同为 41s）；
  `check.ps1` PASS (3 warnings)｜`verify_pins` 18/18｜`api_inventory` 1/80/6=87。
- **未关闭项（不淡化）**：
  1. **E-7 #2 仍开**：无 `request_id` 时 fail-open（`BelongsToRequest` 与
     `EnsureResponseBelongsToRequest` 均把「无 id」视为属于本请求）—— 需先定契约（fail-closed 还是允许）；
  2. `AcquireExchangeLeaseAsync` / `ReadNextResponseLineAsync` 仍 `public`（E-7 #1 只点名
     `ExchangeAsync`）；
  3. ~~`R002-RESYNC-1` 的 P2-F1 仍未关闭（测试不覆盖调用点）~~ —— **已关闭**：`E7-2-DYNAMIC-EVIDENCE-1`（commit `5794fa6c4`） 用两个真实调用点
     （`SendAsync` / `SendHostControlAsync`）的动态证据覆盖，且后者经变异验证；
  4. `tools/perf/wire_serialisation_probe.py:12` 仍把已删除的 `CoreServiceClient._pipeGate`
     当作串行判据（r1 R-005 第 3 处 / r2 R2-002）—— 该文件不在本卡 `allowed_paths` 内，**未改**，
     已登记为残余；它只影响该探针的说明文字，不影响产品行为。

