# R-005（取消后 poison）修复 — 证据

Task：`R005-CANCEL-POISON-1`（Owner：DSH）｜基线 `a718cbf49`

## 1. 缺陷（修改前）

`Transport/SidecarProcess.cs` 的 `ExchangeAsync`：

```csharp
await _stdin.WriteLineAsync(wireLine);   // 请求已写出
await _stdin.FlushAsync();
...
try { responseLine = await _stdout.ReadLineAsync(timeoutSource.Token); }
catch (OperationCanceledException) when (!cancellationToken.IsCancellationRequested)
{
    _poisoned = true;                    // ← 只有超时才 poison
    throw new SidecarException(SidecarErrorCode.RequestTimeout, ...);
}
```

调用方取消时 filter 不匹配 ⇒ `OperationCanceledException` 直抛、`_poisoned` **保持 false** ⇒
请求已写出但响应未读，管道里残留一帧；下一次 `ExchangeAsync` 读到它并当成自己的响应 ⇒ **永久 off-by-one**。

## 2. TDD：先写测试，确认红

夹具：`SidecarLifecycleTests` 同款「PowerShell 假子进程」——
`powershell.exe -NoProfile -NonInteractive -Command "$PID | Set-Content <pidFile>; Start-Sleep -Seconds 30"`，
该子进程**不读 stdin、不写 stdout**，所以「请求已写出但无响应」可复现，**无需 792 MB 真实 sidecar**。

两条测试：
- `CallerCancellation_PoisonsChannel_SoTheNextExchangeFailsClosed`（本卡修复对象）
- `Timeout_StillPoisonsChannel_Unchanged`（对照，防止把超时路径改窄）

**修改前结果（`test-red.log`）**：

```
失败!  - 失败: 1，通过: 1，已跳过: 0，总计: 2，持续时间: 13 s
[xUnit.net] NewManga.CoreClient.Tests.SidecarCancellationPoisonTests.CallerCancellation_PoisonsChannel_SoTheNextExchangeFailsClosed [FAIL]
```

**红的机制正确**：没 poison ⇒ 下一次 `ExchangeAsync` 真的又发请求并白等 5 秒超时，
所以 `Assert.ThrowsAsync<SidecarException>` 仍通过、但 `Assert.Contains("poisoned", follow.Message)` 失败；
13 秒总时长（500ms 等待 + 5s 白等 + 夹具启动）也印证了「没有 fail-closed」。

## 3. 修复

```csharp
catch (OperationCanceledException)
{
    // 请求行已写出；取消调用方并不会把它撤回。
    // 无论子进程之后是否响应，本管道上的请求/响应配对已不可知 ——
    // 残留响应会被当成下一个请求的答案（永久 off-by-one）。
    // 因此两种结果都 poison：超时与主动取消。
    // 只有超时被翻译成 RequestTimeout；主动取消保留 OperationCanceledException，
    // 让调用方仍能区分「我取消了」与「超时了」。
    _poisoned = true;
    if (cancellationToken.IsCancellationRequested)
    {
        throw;
    }

    throw new SidecarException(
        SidecarErrorCode.RequestTimeout, Spec.Name,
        $"no response within {timeout.TotalMilliseconds:F0} ms; stderr tail: {Truncate(StderrTail)}",
        Spec.StderrLogPath);
}
```

**未改动** `ReadNextResponseLineAsync` 的取消分支 —— 它不写请求，取消不会造成请求/响应错配。
完整 diff 见 `fix.diff`。

## 4. 修后绿

```
已通过! - 失败: 0，通过: 2，已跳过: 0，总计: 2，持续时间: 8 s
```

耗时 **13s → 8s**：additionally 证明下一次调用不再白等 5 秒超时，而是立即 fail-closed。

## 5. 不回归

```
不带 sidecar 环境变量的 CoreClient 全量：
  已通过! - 失败: 0，通过: 194，已跳过: 30，总计: 224，耗时 29s，EXIT=0
```

> 卡面历史基线是 `189/0/27`（`PIPE-EXCLUSIVE-TRANSPORT-1` 时期）；此后其它卡加入新测试，
> 现为 194/0/30，差值来自新测试而非本卡放宽。

**带 sidecar 环境变量时另有 4 个失败，均为「Frozen Core 前提」测试**：
`B1Commands_ExecuteAgainstFrozenCore`、`B2Commands_ExecuteAgainstFrozenCore`、
`Fea12Core_DeleteTrashCapabilityProbe_OldCoreFailsClosedBeforeAnyCommandFrame`、
`Fea12NewCommands_FrozenCoreFailsClosedWithTypedError`。

这些测试**要求 sidecar 是「旧/冻结」的**（缺新命令），而本机 sidecar 是 `SIDECAR-REBUILD-1`
用当前 `src/` 重建的（具备全部能力）⇒ 前提消失 ⇒ 失败属**预期内的契约变化**，
与 `PIPE-EXCLUSIVE-TRANSPORT-1` 记录的「CoreClient 4 个 Frozen Core 前提测试（与管道无关）」一致，
**非本卡引入**。见 `coreclient-full.log`（带 sidecar）、`coreclient-no-sidecar.log`（不带）。

## 6. 四件套

```
check.ps1（全局）                → PASS (3 warnings)
verify_pins.ps1                  → PASS (all 18)
generate_api_inventory.py --check → OK (1/80/6=87)
```

## 7. 边界（不淡化）

- 本卡**只**修 R-005。E-7 另外四项（`_pipeGate` 未统一、fail-open、R-002 错配重同步、
  `Dispose`/`StopAsync` 在租约外）**仍开** ⇒ **「并发安全」仍不可宣称**。
- 修复依赖「请求行确实已写出」这一前提；`_stdin.WriteLineAsync` 失败的分支仍走 `ProcessExitedFailure`，
  未改动。
