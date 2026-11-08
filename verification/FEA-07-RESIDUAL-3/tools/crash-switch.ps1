# FEA-07-RESIDUAL-3 / AC-R4b-2（AC3）：外部驱动的跨进程崩溃注入（park -> kill -> recover）。
#
# 三阶段（每个阶段都是**独立进程**；不使用 Environment.FailFast、不同进程冒充、不加生产 backdoor）：
#   1. park    : `dotnet test --filter Fea07Residual3CrashTests.Park...`
#                生产切换事务（FrontendSwitchCoordinator + SwitchJournal + 唯一外观写者）在
#                beforeJournalCommit 停住：目标 frontend 已落盘、journal 未 commit（真实半切换窗口）。
#   2. kill    : 本脚本用 Process.Kill(entireProcessTree: true) 杀掉 launcher 与被测宿主，
#                并以「心跳文件冻结」证明进程真的死了（不是脚本以为它死了）。
#   3. recover : 新进程调用生产恢复入口 App.RecoverInterruptedSwitch，断言 journal 终态 RolledBack、
#                frontend 回到上一已提交、appearance.FrontendId 未被 target 污染、二次恢复零变化、
#                暂停期外部改动被采用（不回写旧快照）、真实 library.db 保护列零写。
#
# Exit code 语义（显式，不把 NOT_RUN 写成 PASS）：
#   0  = 三阶段全部通过
#   10 = kill 后进程未真死（心跳仍在推进 / 进程仍存活）
#   11 = park 未在超时内到达（或崩溃现场前置条件不成立）
#   12 = recover 阶段断言失败（journal 未 RolledBack / 外观被污染 / 保护列被写 / 证据缺失）
#   2  = 用法或前置条件错误（缺 dotnet / 未构建 / 缺 python / 缺仓库）
#
# 用法：pwsh -NoProfile -File verification/FEA-07-RESIDUAL-3/tools/crash-switch.ps1
[CmdletBinding()]
param(
    [string]$Configuration = 'Release',
    [int]$ParkTimeoutSeconds = 180,
    [string]$Python = $(if ($env:NEWMANGA_BUILD_PYTHON) { $env:NEWMANGA_BUILD_PYTHON } else { 'C:/Python314/python.exe' })
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$scriptPath = $PSCommandPath
$evidenceDir = Split-Path -Parent (Split-Path -Parent $scriptPath)   # verification/FEA-07-RESIDUAL-3
$repo = Split-Path -Parent (Split-Path -Parent $evidenceDir)         # repository root
if (-not (Test-Path (Join-Path $repo '.git'))) {
    Write-Host "FATAL: repository root not found from $scriptPath"
    exit 2
}

$evidenceOut = Join-Path $evidenceDir 'evidence'
$logOut = Join-Path $evidenceDir 'logs'
New-Item -ItemType Directory -Force -Path $evidenceOut | Out-Null
New-Item -ItemType Directory -Force -Path $logOut | Out-Null

$logPath = Join-Path $logOut 'crash-switch.log'
$log = [System.Collections.Generic.List[string]]::new()
function Log([string]$message) {
    $line = "[{0}] {1}" -f (Get-Date -Format 'yyyy-MM-ddTHH:mm:ss.fffK'), $message
    $log.Add($line)
    Write-Host $line
}

$testDll = Join-Path $repo "apps/desktop-avalonia/tests/NewManga.App.Tests/bin/$Configuration/net9.0/NewManga.App.Tests.dll"
$testProject = Join-Path $repo 'apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj'

try {
    if (-not (Test-Path $testDll)) { Log "FATAL: test assembly missing: $testDll (build first)"; exit 2 }
    if (-not (Test-Path $Python)) { Log "FATAL: python not found: $Python"; exit 2 }
    if (-not (Get-Command dotnet -ErrorAction SilentlyContinue)) { Log 'FATAL: dotnet not on PATH'; exit 2 }

    $root = Join-Path ($repo + '.workspace') ('FEA-07-RESIDUAL-3/crash/' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + ([guid]::NewGuid().ToString('N').Substring(0, 6)))
    New-Item -ItemType Directory -Force -Path $root | Out-Null
    Log "repo=$repo"
    Log "root=$root"
    Log "python=$Python"

    $parkJson = Join-Path $root 'park.json'
    $heartbeat = Join-Path $root 'heartbeat.txt'
    $journalPath = Join-Path $root 'theme-home/switch-journal.json'
    $evidenceJson = Join-Path $root 'recover-evidence.json'

    function New-TestProcess([string]$phase, [string]$filter) {
        $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
        $startInfo.FileName = 'dotnet'
        foreach ($argument in @('test', $testProject, '-c', $Configuration, '--no-build', '--nologo', '--filter', $filter)) {
            $startInfo.ArgumentList.Add($argument)
        }
        $startInfo.UseShellExecute = $false
        $startInfo.CreateNoWindow = $true
        $startInfo.RedirectStandardOutput = $true
        $startInfo.RedirectStandardError = $true
        $startInfo.Environment['NEWMANGA_FEA07_CRASH'] = '1'
        $startInfo.Environment['NEWMANGA_FEA07_CRASH_PHASE'] = $phase
        $startInfo.Environment['NEWMANGA_FEA07_CRASH_ROOT'] = $root
        $startInfo.Environment['NEWMANGA_BUILD_PYTHON'] = $Python
        return [System.Diagnostics.Process]::Start($startInfo)
    }

    # ------------------------------------------------------------------ phase 1: park
    Log 'phase=park starting (production switch parks before the journal commit)'
    $park = New-TestProcess 'park' 'FullyQualifiedName~Fea07Residual3CrashTests.Park_'
    $parkOut = $park.StandardOutput.ReadToEndAsync()
    $parkErr = $park.StandardError.ReadToEndAsync()

    $deadline = (Get-Date).AddSeconds($ParkTimeoutSeconds)
    while ((Get-Date) -lt $deadline -and -not (Test-Path $parkJson) -and -not $park.HasExited) {
        Start-Sleep -Milliseconds 250
    }

    if (-not (Test-Path $parkJson)) {
        Log 'FATAL(11): park.json was never written inside the timeout'
        if (-not $park.HasExited) { try { $park.Kill($true) } catch { } }
        Log ('park stdout: ' + $parkOut.Result)
        Log ('park stderr: ' + $parkErr.Result)
        exit 11
    }

    $parkState = Get-Content -Raw -Path $parkJson | ConvertFrom-Json
    Log ("park reached: pid=$($parkState.pid) stage=$($parkState.journalStage) " +
         "target=$($parkState.target) appearance.frontendId=$($parkState.appearanceFrontend) " +
         "heartbeat=$($parkState.heartbeat)")
    if ($parkState.phase -ne 'beforeJournalCommit' -or
        $parkState.appearanceFrontend -ne $parkState.target -or
        $parkState.journalStage -in @('Committed', 'RolledBack', 'Idle')) {
        Log 'FATAL(11): the parked state is not the frozen crash window (beforeJournalCommit)'
        try { $park.Kill($true) } catch { }
        exit 11
    }

    Start-Sleep -Milliseconds 700
    $beat1 = if (Test-Path $heartbeat) { [int](Get-Content -Raw -Path $heartbeat) } else { -1 }
    Start-Sleep -Milliseconds 900
    $beat2 = if (Test-Path $heartbeat) { [int](Get-Content -Raw -Path $heartbeat) } else { -1 }
    if ($beat2 -le $beat1) {
        Log "FATAL(11): heartbeat did not advance before the kill ($beat1 -> $beat2)"
        try { $park.Kill($true) } catch { }
        exit 11
    }
    Log "heartbeat advancing before kill: $beat1 -> $beat2"

    # ------------------------------------------------------------ phase 2: kill
    $testHostId = [int]$parkState.pid
    Log "phase=kill Kill(entireProcessTree:true) launcher pid=$($park.Id) testhost pid=$testHostId"
    $killErrors = [System.Collections.Generic.List[string]]::new()
    try { $park.Kill($true) } catch { $killErrors.Add("launcher: $($_.Exception.Message)") }
    $testHostProcess = $null
    try {
        $testHostProcess = [System.Diagnostics.Process]::GetProcessById($testHostId)
        $testHostProcess.Kill($true)
    }
    catch [System.ArgumentException] {
        Log "testhost pid=$testHostId was already gone (kill via the launcher tree)"
    }
    catch { $killErrors.Add("testhost: $($_.Exception.Message)") }

    $launcherExited = $park.WaitForExit(30000)
    $testHostExited = $true
    if ($null -ne $testHostProcess) {
        $testHostExited = $testHostProcess.WaitForExit(30000)
    }
    # P3-05: 「真死」显式三件套 —— launcher WaitForExit + testhost 已消失 + heartbeat frozen。
    $testHostGone = $true
    try {
        $stillThere = [System.Diagnostics.Process]::GetProcessById($testHostId)
        $testHostGone = $stillThere.HasExited
    }
    catch [System.ArgumentException] {
        $testHostGone = $true
    }
    catch {
        $testHostGone = $false
        $killErrors.Add("testhost-liveness: $($_.Exception.Message)")
    }
    if (-not $launcherExited -or -not $testHostExited -or -not $testHostGone) {
        Log ("FATAL(10): the parked processes did not really die " +
             "(launcherExited=$launcherExited testhostExited=$testHostExited testhostGone=$testHostGone)")
        exit 10
    }

    $frozen1 = if (Test-Path $heartbeat) { [int](Get-Content -Raw -Path $heartbeat) } else { -1 }
    Start-Sleep -Milliseconds 1200
    $frozen2 = if (Test-Path $heartbeat) { [int](Get-Content -Raw -Path $heartbeat) } else { -1 }
    if ($frozen1 -ne $frozen2) {
        Log "FATAL(10): heartbeat kept advancing after the kill ($frozen1 -> $frozen2); the process is not really dead"
        exit 10
    }
    Log ("process really dead: launcherExited=$launcherExited testhostExited=$testHostExited " +
         "testhostGone=$testHostGone heartbeat frozen at $frozen1 (kill errors: $($killErrors -join '; '))")

    if (-not (Test-Path $journalPath)) {
        Log "FATAL(11): the killed run left no switch journal at $journalPath"
        exit 11
    }
    $journalAfterKill = Get-Content -Raw -Path $journalPath | ConvertFrom-Json
    Log "journal after kill: stage=$($journalAfterKill.Stage) target=$($journalAfterKill.TargetFrontendId) previous=$($journalAfterKill.PreviousFrontendId)"
    if ($journalAfterKill.Stage -in @('Committed', 'RolledBack', 'Idle')) {
        Log 'FATAL(11): the killed run left a terminal journal (not an interrupted switch)'
        exit 11
    }
    if (Test-Path $evidenceJson) {
        Log 'FATAL(11): recover evidence existed before the recover phase (stale root)'
        exit 11
    }

    # --------------------------------------------------------- phase 3: recover
    Log 'phase=recover starting (new process; production App.RecoverInterruptedSwitch)'
    $recover = New-TestProcess 'recover' 'FullyQualifiedName~Fea07Residual3CrashTests.Recover_'
    $recoverOut = $recover.StandardOutput.ReadToEndAsync()
    $recoverErr = $recover.StandardError.ReadToEndAsync()
    $recoverExited = $recover.WaitForExit(300000)
    if (-not $recoverExited) {
        Log 'FATAL(12): the recover process did not finish in 300s'
        try { $recover.Kill($true) } catch { }
        exit 12
    }
    Log "recover exit code=$($recover.ExitCode)"
    Log ('recover stdout: ' + $recoverOut.Result)
    if ($recover.ExitCode -ne 0) {
        Log ('recover stderr: ' + $recoverErr.Result)
        Log 'FATAL(12): recover fact failed'
        exit 12
    }
    if (-not (Test-Path $evidenceJson)) {
        Log "FATAL(12): recover evidence missing at $evidenceJson"
        exit 12
    }

    $recoverState = Get-Content -Raw -Path $evidenceJson | ConvertFrom-Json
    Log ("recover evidence: status=$($recoverState.status) journalStage=$($recoverState.journalStage) " +
         "finalFrontendId=$($recoverState.finalFrontendId) latestMode=$($recoverState.latestModePreserved) " +
         "secondRecoveryChangedNothing=$($recoverState.secondRecoveryChangedNothing) " +
         "protectedColumnDiffs=$($recoverState.protectedColumnDiffs)")

    $failures = [System.Collections.Generic.List[string]]::new()
    if ($recoverState.status -ne 'ok') { $failures.Add('recover status != ok') }
    if ($recoverState.journalStage -ne 'RolledBack') { $failures.Add("journal stage is '$($recoverState.journalStage)', expected RolledBack") }
    if ($recoverState.finalFrontendId -ne 'builtin.current-v2') { $failures.Add("final frontend is '$($recoverState.finalFrontendId)', expected the last committed frontend") }
    if ($recoverState.finalFrontendId -eq $parkState.target) { $failures.Add('appearance.FrontendId was polluted by the interrupted target') }
    if ($recoverState.latestModePreserved -ne 'Light') { $failures.Add("latest appearance state was not adopted ('$($recoverState.latestModePreserved)')") }
    if (-not $recoverState.secondRecoveryChangedNothing) { $failures.Add('a second recovery changed state') }
    # P2-03: 暂停期保护状态 = 真实 library.db 的 current/inpaint 锁（不只是 appearance 配置）。
    if ([string]::IsNullOrWhiteSpace([string]$recoverState.pausedRevisionId)) { $failures.Add('no paused protected-state revision was recorded') }
    if ([string]$recoverState.currentRevisionAfterRecovery -ne [string]$recoverState.pausedRevisionId) {
        $failures.Add("recovery did not adopt the paused current_revision_id ('$($recoverState.currentRevisionAfterRecovery)' != '$($recoverState.pausedRevisionId)')")
    }
    if ([string]$recoverState.pausedInpaintLocked -ne '1') { $failures.Add("paused inpaint lock was not preserved ('$($recoverState.pausedInpaintLocked)')") }
    if ([int]$recoverState.crashWindowProtectedColumnDiffs -ne 0) { $failures.Add("park/kill window changed protected columns ($($recoverState.crashWindowProtectedColumnDiffs) diffs)") }
    if ([int]$recoverState.protectedColumnDiffs -ne 0) { $failures.Add("protected columns changed ($($recoverState.protectedColumnDiffs) diffs)") }
    if ([int]$recoverState.protectedColumns -le 0) { $failures.Add('no protected columns were compared') }

    $journalFinal = Get-Content -Raw -Path $journalPath | ConvertFrom-Json
    if ($journalFinal.Stage -ne 'RolledBack') { $failures.Add("journal file stage is '$($journalFinal.Stage)'") }

    $result = [ordered]@{
        task = 'FEA-07-RESIDUAL-3'
        ac = 'AC-R4b-2 (AC3 cross-process crash injection)'
        mode = 'external park/kill/recover (three separate processes)'
        generatedAt = (Get-Date).ToString('o')
        root = $root
        park = [ordered]@{
            pid = $testHostId
            launcherPid = $park.Id
            stage = $parkState.journalStage
            target = $parkState.target
            previous = $parkState.previous
            appearanceFrontendAtPark = $parkState.appearanceFrontend
            heartbeatBefore = $beat2
        }
        kill = [ordered]@{
            api = 'Process.Kill(entireProcessTree: true)'
            launcherExited = $launcherExited
            testHostExited = $testHostExited
            testhostGone = $testHostGone
            heartbeatFrozenAt = $frozen1
            heartbeatFrozen = ($frozen1 -eq $frozen2)
            killErrors = @($killErrors)
            realDeathProven = ($launcherExited -and $testHostExited -and $testHostGone -and ($frozen1 -eq $frozen2))
        }
        journalAfterKill = [ordered]@{
            stage = $journalAfterKill.Stage
            target = $journalAfterKill.TargetFrontendId
            previous = $journalAfterKill.PreviousFrontendId
        }
        recover = $recoverState
        exitCode = $(if ($failures.Count -eq 0) { 0 } else { 12 })
        failures = @($failures)
        verdict = $(if ($failures.Count -eq 0) { 'PASS' } else { 'FAIL' })
    }
    $resultJson = $result | ConvertTo-Json -Depth 8
    [System.IO.File]::WriteAllText((Join-Path $evidenceOut 'crash-switch-r4b.json'), $resultJson + [Environment]::NewLine,
        [System.Text.UTF8Encoding]::new($false))

    if ($failures.Count -gt 0) {
        Log ('FATAL(12): ' + ($failures -join '; '))
        exit 12
    }

    Log 'PASS: park -> kill(entireProcessTree) -> recover verified (launcher WaitForExit + testhost gone + heartbeat frozen; journal RolledBack; last committed frontend restored; paused real-DB protected state adopted, not the old snapshot; protected columns untouched)'
    exit 0
}
finally {
    $log | Out-Null
    try {
        if (-not $logPath) { $logPath = Join-Path (Join-Path (Split-Path -Parent (Split-Path -Parent $PSCommandPath)) 'logs') 'crash-switch.log' }
        [System.IO.File]::WriteAllText($logPath, ($log -join [Environment]::NewLine) + [Environment]::NewLine,
            [System.Text.UTF8Encoding]::new($false))
    }
    catch {
        Write-Host "WARN: could not write $logPath"
    }
}
