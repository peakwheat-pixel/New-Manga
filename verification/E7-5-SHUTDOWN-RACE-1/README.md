# E-7 第 5 项（`Dispose`/`StopAsync` 在租约外）— 核证证据

Task：`E7-5-SHUTDOWN-RACE-1`（Owner：DSH）｜基线 `f65adfb4b`

## 1. 代码现状

- `SidecarProcess.StopAsync(gracefulTimeoutMs = 3000)` → `_stopTask ??= StopCoreAsync(...)`（单飞）
- `StopCoreAsync`：`_stdin.Close()` → `_process.WaitForExitAsync(3s)` → 超时 `TryKill()` → 再等退出
- `CoreServiceClient.DisposeAsync`（`:2620-2631`）：直接 `await _process.StopAsync()` → `await _process.DisposeAsync()`
- **三处都不持交换租约**（`AcquireExchangeLeaseAsync` / `_pipeGate`）

## 2. 诊断方法

夹具：Windows PowerShell 子进程

```powershell
$PID | Set-Content -LiteralPath '<pidFile>'
Start-Sleep -Seconds 5
[Console]::Out.WriteLine('{"id":1,"result":null}')
[Console]::Out.Flush()
Start-Sleep -Seconds 30
```

先在 0.5s 处发起 `ExchangeAsync`（请求写出、等待响应），再在约 1.5s 处并发
`StopAsync(gracefulTimeoutMs: 200)` —— 此时子进程还在 `Start-Sleep -Seconds 5` 里，
响应**永远不会到达**。观察在途 `ExchangeAsync` 抛什么。

## 3. 实测结果（`probe-exact-code.log`）

| 场景 | 观测到的结果 |
|---|---|
| **在途交换 + 并发 StopAsync** | **`SidecarException`，`Code = ProcessExited`** |
| **StopAsync 完成后的新交换** | `SidecarException`，**`ProcessExited`**（精确；`IoFailure` 无 throw 点、已不作为容忍项），**fail-fast 不挂起** |
| 是否有 BCL 异常泄漏给调用方 | **没有**（两条测试都走 `SidecarException` 分支；若泄漏，
测试会 `Assert.Fail("leaked a non-SidecarException")`） |

诊断先用了宽松断言通过，随后改**精确断言**复跑仍通过 ⇒ 观测值确定是 `ProcessExited`。

> **r1 P2-1 更正**：另一条测试仍保留 `ProcessExited or IoFailure`，而 **`SidecarErrorCode.IoFailure` 在全仓没有任何 throw 点**（只出现在 `SidecarException.cs:53` 的消息模板）⇒ 那是**死容忍**，未来行为变化不会让测试变红。已改为精确断言。

## 4. 书面判定（AC4）

**① E-7 第 5 项的表述是否准确？—— 准确。**
「在途命令会得 `ProcessExited`」与实测一致 —— **但仅在该窗口之外准确**：
若子进程已写出**一行不完整 JSON**，调用方见到的是 `MalformedResponse`（见 §4④ 与 F-5 的边界说明）。

**② 这算不算缺陷？—— 部分算，但风险低于清单暗示。**
- `ProcessExited` 是**明确、可处理**的错误码：进程确实退出了，调用方能区分它与超时、与协议错误；
- 没有 BCL 异常泄漏（这是最重要的：泄漏会让调用方的 `catch (SidecarException)` 失效）；
- `StopAsync` 是**单飞**的（`_stopTask ??=`），并发调用安全；
- 因此「在租约外」导致的后果是**可接受的错误，而不是静默损坏**。

**③ 是否需要改产品代码？—— 本轮判定：不需要**（理由见下）。

**④ 半行窗口：r1 复核证明它**可稳定复现**，不是窄竞态。**

子进程写一行**不完整 JSON**（`{"id":1,"resu`）并 flush；`ReadLineAsync` 会把这**一整行**返回，
随后 `CoreProtocol.Parse` 抛 `MalformedResponse`（**不是** `ProcessExited`）。这是确定性的，
不需要精确时序控制。

⇒ **E-7 #5 的表述因此只在该窗口之外准确**：「在途命令会得 `ProcessExited`」成立；
但若子进程已写出一行不完整响应，调用方拿到的是 `MalformedResponse`。两者都是 typed、可处理，
差别只在错误码。

本轮把该行为固化为测试 `HalfWrittenResponseLine_SurfacesMalformedResponse_NotProcessExited`。
（注意：`ExchangeAsync` 本身只读一行、**不解析 JSON**；`MalformedResponse` 来自调用方的
`CoreProtocol.Parse` —— 测试按同样两步驱动。）

## 5. 处置

- **不改产品代码**（AC 允许范围本就不含产品代码；诊断未发现必须修的理由）；
- 把两条诊断测试**固化为回归**：断言精确到 `ProcessExited`，未来任何行为变化都会变红；
- 这为「并发安全」的讨论提供了一个事实基础：至少这一项不是静默损坏。

## 6. 不回归

```
诊断测试：        4 passed / 8s
全量（不带 sidecar）：199 passed / 0 failed / 30 skipped / EXIT=0
  （前一轮 195，+4 = 本卡原有的两条 + r1 要求补的两条）
check.ps1 PASS (3 warnings)｜verify_pins 18/18｜api_inventory 1/80/6=87
```

## 6.1 数据来源与测试边界（r2 F-4 / F-5）

**F-4：`16/16 ProcessExited` 的来源。** 这个数字来自 **r1 复核者**在仓库外跑的探针
（`probe-b.log`：E1A 6 次 + E1B 10 次），不是本卡自测。已把该日志复制进证据目录
（`r1-probe-b.log`）以便复算；本卡自测覆盖的是 4 条 `[Fact]`。

**F-5：半行回归测试钉住的是什么。** `HalfWrittenResponseLine_SurfacesMalformedResponse_NotProcessExited`
的夹具是「子进程**主动写一行截断的 JSON**」，**没有经过 stop/kill**。所以它钉住的行为是：

> 一行内容不完整（但不是半行传输）⇒ `ReadLineAsync` 返回该整行 ⇒ `CoreProtocol.Parse` 抛 `MalformedResponse`。

它**不区分成因**：无论是子进程故意写残行，还是被杀时只写了一半，对 `ReadLineAsync` 来说都是
「一行拿到了但内容不完整」。如果未来 shutdown 路径改用别的 EOF 处理（例如读到 null 就返回
`ProcessExited` 而不再尝试解析），**这条测试不会变红** —— 这是它作为回归的已知局限，已记录。

## 7. 边界（不淡化）

- 本卡**没有改任何产品代码**，只核证 + 固化（新增 4 条测试）；
- r1 指出的「真实关停路径是 `CoreServiceClient.DisposeAsync`，`HostRuntime` 不持 `_pipeGate`」已用 `DisposeWhileExchangeInFlight_DoesNotLeakBclException` 覆盖：**实测 16/16 `ProcessExited`，dispose 从不抛**，未发现缺陷；
- **E-7 另外四项仍开**：`_pipeGate` 未统一 + `ExchangeAsync` 仍 `public`、无 `request_id` 时 fail-open、
  R-002 错配无重同步、以及本项的「写响应中被杀的半行窗口」⇒ **「并发安全」仍不可宣称**；
- 「不需要改代码」是**基于本轮实测**的判断，不等于证明该项在任何时序下都安全。
