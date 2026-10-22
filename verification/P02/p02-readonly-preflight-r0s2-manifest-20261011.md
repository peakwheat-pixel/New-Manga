# P02PRE-R0S2 候选只读取证 manifest

## 状态、授权与基线

- Task=`P02PRE-R0S2`；Owner/Author=`Codex /root`；非作者 Reviewer=`DeepSeek Harness`；Integrator/Adjudicator=`Codex /root`。
- 本 manifest 只供静态 Review。当前 `status=in_review`；未经非作者 Review 与 Codex adjudication，执行状态=`NOT_AUTHORIZED_TO_CAPTURE`。
- 用户已批准受控只读取证阶段。此授权不是新的 waiver 或任何 Gate PASS。
- Repo=`G:/CODEX/New Manga`；branch=`main`；HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。
- 风险原值：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。

## 静态来源及可证明范围

1. `verification/P02/p02-readonly-preflight-r0-manifest-20261011.md` L21/L65/L90 冻结 `.NET RegistryKey.OpenBaseKey` + `OpenSubKey(path, false)` 为只读键存在性 getter，并指定不得枚举 values/subkeys。
2. `verification/P02/p02-readonly-preflight-r0-evidence-20261011.md` L27 记录该 getter 在 `RegistryView.Default` 上对两个历史候选键的既有执行证据。
3. P02M9 `verification/P02/codex-p02-wer-per-image-bootstrap-contract-research-20261010.md` §2 说明 Windows Registry 的一般 WOW64 view 选择规则，但不证明 WER reader/helper 的实际 view、机器架构、映像集合或 view 是否对应不同物理对象。
4. Microsoft Learn：[`RegistryKey.OpenBaseKey`](https://learn.microsoft.com/en-us/dotnet/api/microsoft.win32.registrykey.openbasekey) 描述按请求 hive/view 打开本机 key；[`RegistryKey.OpenSubKey(String, Boolean)`](https://learn.microsoft.com/en-us/dotnet/api/microsoft.win32.registrykey.opensubkey) 描述指定 key 的只读/读写打开；页面同时说明 key 不存在时返回 null，也把 null 描述为操作失败结果。因此本 manifest 只记录精确 API 返回，不把 null 单独提升为 absence 证明。

这些来源说明方法用途与访问模式；不构成对 PowerShell shell startup、profile、runtime module、外部进程或整个进程无副作用的证明。Reviewer 必须对此独立裁定。若候选执行环境/启动行为不满足只读安全要求，结果应为 `NOT_SAFE_FOR_R0` 且不得运行。

## 精确对象与允许操作

- Hive=`RegistryHive.LocalMachine`。
- Subkey=`SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps`。
- 调用 1：`RegistryKey.OpenBaseKey(LocalMachine, Registry32)` → `OpenSubKey(exactSubkey, false)`。
- 调用 2：仅当调用 1 正常完成后，`OpenBaseKey(LocalMachine, Registry64)` → `OpenSubKey(exactSubkey, false)`。
- 不读取值、value kind、子键名、计数、ACL 或其他属性；不打开远程 hive；不探查 filesystem。
- 每个 RegistryKey handle 在 `finally` 中调用 `Dispose()`；不输出/序列化 handle。
- API exception/null 是结果不确定，不能当作 key absence；不重试、不 fallback。

## 唯一冻结命令候选

候选工具调用：Codex `functions.exec_command`，`shell="powershell.exe"`、`login=false`，`cmd` 为下方 fenced body 的完整原文。Review 只审查文本和边界；这不是当前运行授权。命令不写临时文件，不调用 module/provider/external executable，不启动子进程，不写任何状态。

```powershell
$ErrorActionPreference = 'Stop'
$capturePid = $PID
$expectedName = 'HOME-MY\49745'
$expectedSid = 'S-1-5-21-2196946971-914346751-4210154634-1001'
$identity = $null
$threadIdentity = $null
$identityError = $null
try {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent($false)
    $threadIdentity = [Security.Principal.WindowsIdentity]::GetCurrent($true)
} catch {
    $identityError = $_.Exception.GetType().FullName
}
$actualName = if ($null -ne $identity) { $identity.Name } else { '' }
$actualSid = if ($null -ne $identity -and $null -ne $identity.User) { $identity.User.Value } else { '' }
$authenticated = ($null -ne $identity -and $identity.IsAuthenticated)
if ($null -ne $identityError -or $actualName -ne $expectedName -or $actualSid -ne $expectedSid -or -not $authenticated -or $null -ne $threadIdentity) {
    [Console]::Out.WriteLine(('STOP|CapturePid={0}|Status=STOP_IDENTITY_UNPROVABLE_OR_MISMATCH|Name={1}|Sid={2}|Authenticated={3}|ThreadIdentityPresent={4}|IdentityError={5}' -f $capturePid, $actualName, $actualSid, $authenticated, ($null -ne $threadIdentity), $identityError))
    return
}
[Console]::Out.WriteLine(('IDENTITY|CapturePid={0}|Name={1}|Sid={2}|Authenticated={3}|ThreadIdentityPresent=false' -f $capturePid, $actualName, $actualSid, $authenticated))
$subkey = 'SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps'
foreach ($entry in @(
    [pscustomobject]@{ Name = 'Registry32'; View = [Microsoft.Win32.RegistryView]::Registry32 },
    [pscustomobject]@{ Name = 'Registry64'; View = [Microsoft.Win32.RegistryView]::Registry64 }
)) {
    $queryStartUtc = [DateTimeOffset]::UtcNow.ToString('o')
    $baseKey = $null
    $targetKey = $null
    try {
        $baseKey = [Microsoft.Win32.RegistryKey]::OpenBaseKey([Microsoft.Win32.RegistryHive]::LocalMachine, $entry.View)
        $targetKey = $baseKey.OpenSubKey($subkey, $false)
        $state = if ($null -eq $targetKey) { 'RETURNED_NULL' } else { 'OPENED_READ_ONLY' }
        [Console]::Out.WriteLine(('QUERY|View={0}|Hive=LocalMachine|Subkey={1}|StartUtc={2}|State={3}' -f $entry.Name, $subkey, $queryStartUtc, $state))
    } catch {
        $errorType = $_.Exception.GetType().FullName
        $errorHresult = '0x{0:X8}' -f [uint32]$_.Exception.HResult
        [Console]::Out.WriteLine(('STOP|View={0}|Hive=LocalMachine|Subkey={1}|StartUtc={2}|State=ERROR|ExceptionType={3}|HResult={4}' -f $entry.Name, $subkey, $queryStartUtc, $errorType, $errorHresult))
        return
    } finally {
        if ($null -ne $targetKey) { $targetKey.Dispose() }
        if ($null -ne $baseKey) { $baseKey.Dispose() }
    }
}
[Console]::Out.WriteLine(('COMPLETE|CapturePid={0}|EndUtc={1}' -f $capturePid, [DateTimeOffset]::UtcNow.ToString('o')))
```

## 停止边界与结果分类

- Identity API 异常、user/name/SID 不符、未认证或 thread identity 非空：在 registry 前 STOP，相关目标=`UNPROVABLE`。
- 第一个 view 任一异常或无法完整输出：STOP，不运行第二个 view；相关观察=`UNPROVABLE`。
- 一个 view 正常返回 handle/null 后关闭句柄，再继续第二个 view。`OPENED_READ_ONLY` 或 `RETURNED_NULL` 都仅是该 view、该时点的精确 API 观察，按 `PASS_WITH_EVIDENCE` 记载；因 null/error 语义未消歧，关于真实物理 key absence、WER 有效 view、policy、destination、T0 仍=`UNPROVABLE`。
- PID、query/start/end time 或完整 stdout 缺失：不补写、不重跑，相关观察=`UNPROVABLE`。
- 若 reviewer 认为 shell startup/profile 或本地过程状态不能证明满足只读约束，整个候选=`NOT_SAFE_FOR_R0`，不得执行。

## 明确禁止与 Gate

禁止任何 Registry write/create/delete/set/flush、ACL 修改、profile API、token/PInvoke/Add-Type、额外 module/provider/external executable/subprocess、文件/路径/TEMP/cache/WER目录查询、protected path 写入、Sandbox/Windows feature 查询或修改、build/Cargo、AC1–AC7、用户数据读取。禁止在 Review 前执行。

此候选不改风险裁决，不解除 P02PRE、Create、Build Gate 或 Hard Build Barrier，不授权 build/Cargo/AC1–AC7。`private_registry_absence=UNPROVABLE` 仅按既有 owner waiver 记录，不视为 PASS。
