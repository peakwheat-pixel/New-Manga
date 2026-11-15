---
id: R005-CANCEL-POISON-1
title: 修复 R-005 —— 调用方取消后管道未 poison 导致永久失步
kind: defect
governance_version: 3
status: done
suggested_owner: DSH
owner: DSH
reviewer: r005-review-r2（独立上下文子 agent，APPROVED_WITH_LIMITATIONS；r1 亦为 APPROVED_WITH_LIMITATIONS）
integration_commit: 47fde6aba
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC1 测试先行且先红**：新增 `SidecarCancellationPoisonTests`，用「PowerShell 假子进程（不读 stdin、 <<MET>>
      不写 stdout）」构造「请求已写出但无响应」；断言「取消后下一次 `ExchangeAsync` 立即 fail-closed」。
      在**未修改**的 `SidecarProcess` 上必须 **FAIL**，并记录红日志。
      另需覆盖**第二分支**：`CallerCancellation_DuringEventSkip_PoisonsChannel`（事件帧已到达、
      真响应未读时取消），修复前同样必须 FAIL。
- [x] **AC2 修复精确（含第二 poison 分支）**：**两处**取消处理在**超时与主动取消两种情况下都置 `_poisoned`**—— <<MET>>
      ① `ExchangeAsync`；② `ReadNextResponseLineAsync`（它在事件帧跳过循环里被调用，此时请求已写出、
      真响应未读，取消同样会残留 → r1 P2-01 指出初版漏了它）。主动取消仍重抛 `OperationCanceledException`
      （调用方可区分「我取消了」与「超时了」）。超时路径的错误码/消息不变。
- [x] **AC3 修后绿**：同一测试通过，且耗时明显短于红时（不再白等一次完整超时）。 <<MET>>
- [x] **AC4 超时路径不变**：对照测试 `Timeout_StillPoisonsChannel_Unchanged` 通过。 <<MET>>
- [x] **AC5 不回归**：`NewManga.CoreClient.Tests` 全量 **0 failed**；四件套 PASS。 <<MET>>
- [x] **AC6 独立复核**：固定 head 交独立上下文 Review。 <<MET>>

## 允许修改范围

见 frontmatter `allowed_paths`：**只改 `SidecarProcess` 的**两个**取消分支（`ExchangeAsync` 与
`ReadNextResponseLineAsync`）+ 新增一个测试文件**。
（初版只允许改第一处，是基于错误的论证；r2 P2-01 指出第二处同样是 R-005 的一部分，已解冻。）

## 禁止范围

- ~~不得修改 `ReadNextResponseLineAsync` 的取消行为~~（**该条已撤回**：它在事件帧跳过循环里运行，
  此时请求已写出、真响应未读，取消同样造成失步 —— 属 R-005 的第二分支，必须一并修）；
- 不得修改 `ReadNextResponseLineAsync` 的**其它**行为（读帧、错误消息、超时语义保持原样）；
- 不得为让测试通过而放宽断言或改测试语义；
- 不得引入新错误码（复用 `RequestTimeout` 的 poison 语义，`ThrowIfPoisoned` 已有）；
- 不得顺带做 R-002（错配重同步）—— 那是独立项。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| 新测试（红，第一分支） | `dotnet test … --filter FullyQualifiedName~SidecarCancellationPoisonTests` | 修改前 **1 failed / 1 passed**（13s） |
| 新测试（红，第二分支） | 同上（加事件帧用例后） | 修改前 **1 failed / 2 passed**（16s） |
| 新测试（绿） | 同上 | 修改后 **3 passed / 11s** |
| 全量不回归 | `dotnet test …NewManga.CoreClient.Tests.csproj` | **195 passed / 0 failed / 30 skipped** |
| 四件套 | check / pins / inventory | PASS / 18-18 / 87 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-R005-01 | AC1/AC2/AC3/AC4 证据总述 | verification/R005-CANCEL-POISON-1/README.md | 2ef08110c | 29ea0710a3ce7fee2c3bd470ba2db8c16d55c33abd2245749d39ffa4734ff4a4 | CANONICAL | BLOB |
| EV-R005-02 | AC1 第一分支红日志 | verification/R005-CANCEL-POISON-1/test-red.log | 2ef08110c | e066509b9418b2b7ff427c2a2f530338d23f175de5ed94d54e83a637b235c90a | CANONICAL | BLOB |
| EV-R005-03 | AC1 第二分支红日志 | verification/R005-CANCEL-POISON-1/test-red2-eventskip.log | 2ef08110c | 84996f5b6e86c10619d892f8c66e2b3c16911942d6e7b98272316d78307b26f7 | CANONICAL | BLOB |
| EV-R005-04 | AC3 修后绿（3 passed） | verification/R005-CANCEL-POISON-1/test-green3-final.log | 2ef08110c | d27518b9f6506b1b618357f2979d2902b95324ec26113e64116202bf817eaad2 | CANONICAL | BLOB |
| EV-R005-05 | AC5 全量不回归（195/0/30） | verification/R005-CANCEL-POISON-1/coreclient-no-sidecar-final.log | 2ef08110c | f0f0721cd517b15254e1794959123226a27e6822ee5942bd345993295e8edecb | CANONICAL | BLOB |
| EV-R005-06 | AC2 修复 diff（两分支） | verification/R005-CANCEL-POISON-1/fix.diff | 2ef08110c | a88ad6251be3d94820da32321d0cfb24758c109a2be1566b3189ac63e087fae5 | CANONICAL | BLOB |
| EV-R005-07 | AC 过程证据（中间态/对照） | verification/R005-CANCEL-POISON-1/coreclient-full.log | 2ef08110c | e3649d94fe131a9a7e3690e10965da51c590ca07cab3d23d5d7001e3efb8e7ef | CANONICAL | BLOB |
| EV-R005-08 | AC 过程证据（中间态/对照） | verification/R005-CANCEL-POISON-1/coreclient-no-sidecar.log | 2ef08110c | 7cf6fdc00736ad21af40f8427fd9dfc7f3d03418060702953c560154b3ec82d5 | CANONICAL | BLOB |
| EV-R005-09 | AC 过程证据（中间态/对照） | verification/R005-CANCEL-POISON-1/coreclient-no-sidecar-after2.log | 2ef08110c | f0f0721cd517b15254e1794959123226a27e6822ee5942bd345993295e8edecb | CANONICAL | BLOB |
| EV-R005-10 | AC 过程证据（中间态/对照） | verification/R005-CANCEL-POISON-1/test-green.log | 2ef08110c | f439fc5c5e0391d06213b1d992aae20aa78e40b1e03c9a6e06a185fcd7ba0337 | CANONICAL | BLOB |
| EV-R005-11 | AC 过程证据（中间态/对照） | verification/R005-CANCEL-POISON-1/test-green2-eventskip.log | 2ef08110c | d27518b9f6506b1b618357f2979d2902b95324ec26113e64116202bf817eaad2 | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/R005-CANCEL-POISON-1/ | NOT_APPLICABLE | — | — | 新增证据，无迁移/归档 |

## Closeout Record

- Closeout：2026-11-16，DSH；实现 `80c8142a1`（第一分支）+ `47fde6aba`（第二分支）+ 本收口。
- **结果**：R-005 **两个 poison 分支**均修好——`ExchangeAsync` 与 `ReadNextResponseLineAsync`
  在「超时」与「调用方主动取消」两种情况下都置 `_poisoned`；主动取消重抛 `OperationCanceledException`
  （调用方可区分「我取消了」与「超时了」）；超时路径的错误码与消息逐字未变。
- **TDD**：
  - 第一分支：红 `1 failed / 1 passed / 13s` → 绿 `2 passed / 8s`；
  - 第二分支（r1 指出我漏掉的）：红 `1 failed / 2 passed / 16s` → 绿 `3 passed / 11s`。
- **独立复核两轮**：
  - r1 `APPROVED_WITH_LIMITATIONS`（0/0/1/4）—— 抓出**我只修了一半**，且我「`ReadNextResponseLineAsync`
    不写请求所以安全」的论证**不成立**（它只在 `ExchangeAsync` 之后的事件帧跳过循环里被调用，
    此时请求已写出、真响应未读）。
  - r2 `APPROVED_WITH_LIMITATIONS`（0/0/1/5）—— 确认第二分支修复正确、两处结构一致、消息逐字未变；
    r1 的 P2-01 关闭。r2 的 P2-01（卡面允许/禁止/测试要求三处仍写单分支）已在本收口处置；
    P3-01（夹具行不满足 `IsEventFrame`）已修（改用 `event_type` 并加 `IsEventFrame` 断言）；
    P3-03（README 引用旧快照数字）已更新；P3-04（`ThrowIfPoisoned` 消息仍写 "after a timeout"）
    已改为 "after a timeout or caller cancellation"。
- **不回归**：CoreClient 全量（不带 sidecar）**195 passed / 0 failed / 30 skipped / EXIT=0**；
  `check.ps1` PASS (3 warnings)｜`verify_pins.ps1` PASS (18/18)｜`generate_api_inventory.py --check` OK (1/80/6=87)。
- **未关闭项（不淡化）**：
  1. **E-7 另外四项仍开**：`_pipeGate` 未统一 + `ExchangeAsync` 仍 `public`；无 `request_id` 时 fail-open；
     R-002 错配无重同步；`Dispose`/`StopAsync` 在租约外 ⇒ **「并发安全」仍不可宣称**；
  2. **取消后通道进入 poison，需重启 sidecar 才能恢复**（`ThrowIfPoisoned` 无自动重建）；
  3. 夹具在 `%TEMP%` 留 pid 文件与 stderr 目录（与既有 `SidecarLifecycleTests` 同款模式，
     本卡新增测试也会留；已记录未清理）；
  4. 红/绿日志为裁剪摘要（无失败堆栈），红点靠代码 + 时长算术 + 夹具复现三重推导。
