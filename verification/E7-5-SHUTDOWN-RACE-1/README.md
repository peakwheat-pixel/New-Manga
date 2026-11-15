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
| **StopAsync 完成后的新交换** | `SidecarException`（`ProcessExited` 或 `IoFailure`），**fail-fast 不挂起** |
| 是否有 BCL 异常泄漏给调用方 | **没有**（两条测试都走 `SidecarException` 分支；若泄漏，
测试会 `Assert.Fail("leaked a non-SidecarException")`） |

诊断先用了宽松断言（`ProcessExited or IoFailure or RequestTimeout`）通过；
随后改成**精确断言** `Assert.Equal(SidecarErrorCode.ProcessExited, ...)` 复跑仍通过
⇒ 观测值确定是 `ProcessExited`，不是三者之一。

## 4. 书面判定（AC4）

**① E-7 第 5 项的表述是否准确？—— 准确。**
「在途命令会得 `ProcessExited`」与实测完全一致。

**② 这算不算缺陷？—— 部分算，但风险低于清单暗示。**
- `ProcessExited` 是**明确、可处理**的错误码：进程确实退出了，调用方能区分它与超时、与协议错误；
- 没有 BCL 异常泄漏（这是最重要的：泄漏会让调用方的 `catch (SidecarException)` 失效）；
- `StopAsync` 是**单飞**的（`_stopTask ??=`），并发调用安全；
- 因此「在租约外」导致的后果是**可接受的错误，而不是静默损坏**。

**③ 是否需要改产品代码？—— 本轮判定：不需要**（理由见下）。

**④ 未能覆盖的残余窗口（如实登记）**：
真正可能产生**误导性错误码**的窗口是**「子进程正在写响应时被 kill」** ⇒ 读到半行 ⇒
`CoreProtocol.Parse` 失败 ⇒ `MalformedResponse`（而不是 `ProcessExited`）。
本轮夹具让子进程在 5s 后才写，而 stop 发生在 0.5s，所以**没有命中这个窗口**。
该窗口极窄（写一行是微秒级），且要稳定复现需要精确时序控制（例如让子进程在写入中途被挂起）
—— 本轮未做，**登记为残余**。

## 5. 处置

- **不改产品代码**（AC 允许范围本就不含产品代码；诊断未发现必须修的理由）；
- 把两条诊断测试**固化为回归**：断言精确到 `ProcessExited`，未来任何行为变化都会变红；
- 这为「并发安全」的讨论提供了一个事实基础：至少这一项不是静默损坏。

## 6. 不回归

```
诊断测试：        2 passed / 1s
全量（不带 sidecar）：197 passed / 0 failed / 30 skipped / 34s / EXIT=0
  （前一轮 195，+2 = 本卡新增的两条）
check.ps1 PASS (3 warnings)｜verify_pins 18/18｜api_inventory 1/80/6=87
```

## 7. 边界（不淡化）

- 本卡**没有修任何东西**，只核证 + 固化；
- **E-7 另外四项仍开**：`_pipeGate` 未统一 + `ExchangeAsync` 仍 `public`、无 `request_id` 时 fail-open、
  R-002 错配无重同步、以及本项的「写响应中被杀的半行窗口」⇒ **「并发安全」仍不可宣称**；
- 「不需要改代码」是**基于本轮实测**的判断，不等于证明该项在任何时序下都安全。
