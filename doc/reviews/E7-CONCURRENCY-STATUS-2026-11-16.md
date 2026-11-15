# E-7 并发项 — 现状精确核实（2026-11-16，DSH）｜**r1 复核后重写**

**结论先行（r1 更正后的正确版本）**：

> **「E-7 仍有 5 项开放、并发安全不可宣称」在本 head 上仍然准确。**
> 5 项**全部仍开**。本报告初版曾错误地宣称「不是 5 项，而是 1+1+1」——那个更正**方向反了**，见 §4。

**权威枚举**（两处独立文档一致，本报告以此为准）：
- `doc/tasks/PIPE-EXCLUSIVE-TRANSPORT-1.md:123-129`
- `doc/reviews/MAINT-1-EXISTING-FINDINGS-2026-11-14.md:162-168`

---

## 1. 权威 5 项的逐项核实（全部仍开）

| # | 权威表述 | 代码实测 | 判定 |
|---|---|---|---|
| **1** | `CoreServiceClient` 仍用自己的 `_pipeGate`，未改用传输层租约；`ExchangeAsync` 仍 `public` ⇒ 未来直调绕过独占（AC1 PARTIAL / AC2 NOT MET） | `CoreServiceClient.cs:426` `_pipeGate`；`SidecarProcess.ExchangeAsync` 为 `public`（`:219`），且**内部不加锁**（无 `_exchangeGate.WaitAsync`） | **仍开** |
| **2** | 无 `request_id` 时 fail-open；bridge 仅校验数字 id（AC4 后半 NOT MET） | `EnsureResponseBelongsToRequest`（`CoreServiceClient.cs:~2406` 判据）对**缺失** `request_id` 直接放过（配合 `CoreProtocol.cs:63-65`）；`HostBridgeClient.ParseResponse`（`:322-333`）仅校验数字 `id`，`:272` 的 `SendRawAsync` 不传 `expectedId` | **仍开（生产路径）** |
| **3** | **R-002**：id 错配后无重同步，流中可能残留一帧（AC5 NOT MET） | `CoreServiceClient.cs:2408-2413` 错配时抛 `SidecarException`，无 drain/poison；协议按行一次一响应 ⇒ 抛错后本次响应残留，下一次读到上一条 = **永久 off-by-one** | **仍开** |
| **4** | **R-005**：取消（`CancellationToken`）后流状态可能永久失步 | `SidecarProcess.cs:250-258`：`catch (OperationCanceledException) when (!cancellationToken.IsCancellationRequested)` —— **只有超时才 `_poisoned = true`**；**调用方主动取消**时该 filter 不匹配 ⇒ 异常直抛、**不置 poison** ⇒ 流状态未定义 | **仍开** |
| **5** | `Dispose`/`StopAsync` 在租约外，在途命令会得 `ProcessExited` | `CoreServiceClient.DisposeAsync`（`:2620-2631`）：直接 `await _process.StopAsync()` → `await _process.DisposeAsync()`，**两处都不持 lease** | **仍开** |

## 2. 关键机制澄清（理解 1–5 的前提）

`SidecarProcess.ExchangeAsync`（`:219`）**本身不加锁** —— 它只做 `ThrowIfPoisoned` → 写 stdin → 读 stdout 一行。
独占必须由调用方通过 `AcquireExchangeLeaseAsync`（`:40-43`，底层 `_exchangeGate` SemaphoreSlim(1,1)，`:34`）持 lease 实现。

⇒ 由此可推出第 1 项为何是缺口：`ExchangeAsync` 是 `public` 且不自锁，「未来任何直调即绕过独占」。
当前两条管道各自加锁（Fluent 侧走传输层 lease、Core 侧走私有 `_pipeGate`），**功能有保护但机制未统一**。

## 3. 已在的修复（不属于 5 项，供参照，不是本报告的"更正"）

这两项在 `MAINT-1:158-159`、`GOAL-PROGRESS:1571-1572` 中**早已记为已修**，从未计入 5 项：

- `HostBridgeClient` 已用传输层 lease：`Bridge/HostBridgeClient.cs:269`/`:292`，
  全文件仅 2 处 `ExchangeAsync`（`:270`/`:293`）且都在 lease 之下；其余公开方法走 `SendAsync`，**无绕过路径**。
- `CoreServiceClient.SendRawAsync` 已持 `_pipeGate`：`:2386` Wait → `:2387-2393` try → `:2394-2397` finally Release。

## 4. r1 复核指出的错误（本报告初版，已更正）

| 错误 | 说明 |
|---|---|
| **P1：§3「不是 5 项而是 1+1+1」** | 我把卡面 AC1/AC2/AC4/AC5 的 `[~]` 行当成"5 项"，并把 a/b（早已修、从未计入）也纳进来"更正"，**方向反了**；还漏了 R-005 与 Dispose 两项，把开放项从 5 降到 3。**已按权威枚举重写为 §1。** |
| **P2：d 归类为「设计如此」** | 初版引 `CoreServiceClient.cs:2384-2385` 的注释论证 fail-open 是故意的 —— 但那注释描述的是**测试钩子** `SendRawAsync`（全仓无生产调用者）。第 2 项指的是**生产路径** `EnsureResponseBelongsToRequest` 对缺失 `request_id` 放过。**归为「设计如此」掩盖了生产路径残余风险**，已改判为「仍开」。 |
| **P2：AC2 解读错位** | 初版把 AC2「core 侧两处仍直调 `ExchangeAsync`」误读为 `SendRawAsync`；实指 `CoreServiceClient.cs:699-701` 与 `:2431`。AC2 `[~]` 仍成立。 |

**保留的部分**：a（HostBridgeClient 已用 lease）、b（SendRawAsync 已持锁）、c（两把 gate 分属独立管道、无双重锁）、
以及「`ExchangeAsync` 本身不加锁」四项代码结论经 r1 复核确认准确，无需返工。

## 5. 真实剩余工作（按风险排序）

| 优先级 | 项 | 为何排这个位置 |
|---|---|---|
| **P1** | **4 / R-005 取消失步** | 最现实的触发路径：任何一次 `CancellationToken` 取消都会让流永久失步，且**不置 poison**（无法自愈） |
| **P1** | **3 / R-002 错配无重同步** | 协议按行一次一响应，抛错即 off-by-one，后续所有调用错位 |
| P2 | **5 / Dispose 与在途命令竞态** | `StopAsync` 不持 lease，在途命令得 `ProcessExited`（表现为随机失败） |
| P2 | **1 / 统一到传输层租约** | 架构一致性；`ExchangeAsync` 仍 `public` 是「未来直调即绕过」的根因 |
| P3 | **2 / fail-open 收紧** | 需要先定「缺失 id 时应 fail-closed 还是允许」的契约，属设计决策 |

## 6. 第 5 次同类错误（如实记录）

初版方法里我写了「读完整实现，不只 grep」，但 §3 的错恰恰是**另一种"读到一半"**：
我读了卡面 AC 行，**没去找「5 项」的权威枚举定义**（它在同一张卡的「未达成」小节里，`PIPE-EXCLUSIVE-TRANSPORT-1.md:123-129`，
以及 `MAINT-1:162-168` 有同样的列表）。

前四次：`0x00` 映射猜错 → 默认壳看错分支 → 手工绕过 `package.ps1` → grep 无 `lock` 判「无锁」。
**这一次是：把"看起来像清单的行"当成了权威清单，而没找原始定义。**

⇒ 归纳一条可执行的纪律：**凡要复述「N 项」这类枚举，必须先定位它的定义处并逐条对照，不得从二手行文里反推。**

## 7. 本轮范围

**不修改任何 `.cs`**（本卡只做状态核实）。四件套已复跑：`check` PASS(3w) / `pins` 18/18 / `inventory` 1/80/6=87。
