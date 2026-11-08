# FEA-07-RESIDUAL-3 / AC-R4b-3（AC4）：真实进程启动入口矩阵（4 组参数）。
#
# 口径（冻结卡实现口径 3 + scope review §4）：真实 `NewManga.App.exe` 进程 + 隔离数据根/theme-home/log-dir，
# 逐个断言 `exit_code=0`、无 `fatal.log`、`<log-dir>/startup.log` 含对应诊断行；坏外观文档还必须
# `fallback=True`。不修改 `tools/e2e/**`、`scripts/**`（本脚本只放在本证据目录）。
#
# Exit code 语义：0 = 4 组全通过；2 = 前置条件/用法错误；12 = 有断言失败（含无桌面会话）。
#
# 用法：pwsh -NoProfile -File verification/FEA-07-RESIDUAL-3/tools/startup-matrix.ps1
[CmdletBinding()]
param(
    [string]$Configuration = 'Release',
    [int]$ExitAfterMs = 2500,
    [int]$TimeoutSeconds = 180
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$scriptPath = $PSCommandPath
$evidenceDir = Split-Path -Parent (Split-Path -Parent $scriptPath)
$repo = Split-Path -Parent (Split-Path -Parent $evidenceDir)
if (-not (Test-Path (Join-Path $repo '.git'))) {
    Write-Host "FATAL: repository root not found from $scriptPath"
    exit 2
}

$evidenceOut = Join-Path $evidenceDir 'evidence'
$logOut = Join-Path $evidenceDir 'logs'
New-Item -ItemType Directory -Force -Path $evidenceOut | Out-Null
New-Item -ItemType Directory -Force -Path $logOut | Out-Null

$log = [System.Collections.Generic.List[string]]::new()
function Log([string]$message) {
    $line = "[{0}] {1}" -f (Get-Date -Format 'yyyy-MM-ddTHH:mm:ss.fffK'), $message
    $log.Add($line)
    Write-Host $line
}

$exe = Join-Path $repo "apps/desktop-avalonia/src/NewManga.App/bin/$Configuration/net9.0/NewManga.App.exe"
$workspace = Join-Path ($repo + '.workspace') 'FEA-07-RESIDUAL-3/startup-matrix'

$cases = @(
    [ordered]@{ name = 'default'; extra = @(); corrupt = $false; marker = 'startup: shell=Default'; fallback = 'fallback=False' },
    [ordered]@{ name = 'presentation-host'; extra = @('--presentation-host=true'); corrupt = $false; marker = 'startup: shell=PresentationHost'; fallback = 'fallback=False' },
    [ordered]@{ name = 'shell-legacy'; extra = @('--shell=legacy'); corrupt = $false; marker = 'startup: shell=Legacy'; fallback = 'fallback=False' },
    [ordered]@{ name = 'corrupt-appearance'; extra = @(); corrupt = $true; marker = 'startup: appearance: appearance document is not valid JSON'; fallback = 'fallback=True' }
)

try {
    if (-not (Test-Path $exe)) { Log "FATAL: App executable missing: $exe (build first)"; exit 2 }
    Log "repo=$repo"
    Log "exe=$exe"

    $sessionId = (Get-Process -Id $PID).SessionId
    Log "powershell session id=$sessionId (0 = service session, no interactive desktop)"
    if ($sessionId -eq 0) {
        Log 'FATAL(12): no interactive desktop session; the real startup window matrix is NOT_RUN here'
        exit 12
    }

    $results = [System.Collections.Generic.List[object]]::new()
    $failures = [System.Collections.Generic.List[string]]::new()

    foreach ($case in $cases) {
        $root = Join-Path $workspace ($case.name + '-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + ([guid]::NewGuid().ToString('N').Substring(0, 6)))
        $themeHome = Join-Path $root 'theme'
        $logDir = Join-Path $root 'logs'
        New-Item -ItemType Directory -Force -Path $themeHome | Out-Null
        if ($case.corrupt) {
            [System.IO.File]::WriteAllText((Join-Path $themeHome 'presentation-settings.json'),
                '{ this is not a json appearance document', [System.Text.UTF8Encoding]::new($false))
        }

        # NOTE: build every argument as its own list element. PowerShell parses `'a=' + $x, 'b=' + $y`
        # as `'a=' + ($x, 'b=' + $y)` (comma binds tighter than +), which silently merges the arguments
        # into one space-joined string -- that bug made the app ignore --log-dir/--exit-after.
        $arguments = [System.Collections.Generic.List[string]]::new()
        $arguments.Add('--data-root=' + (Join-Path $root 'data'))
        $arguments.Add('--log-dir=' + $logDir)
        $arguments.Add('--theme-home=' + $themeHome)
        $arguments.Add('--mutex-name=Local\NewManga.Fea07Startup.' + [guid]::NewGuid().ToString('N').Substring(0, 12))
        $arguments.Add('--exit-after=' + $ExitAfterMs)
        foreach ($extra in $case.extra) { $arguments.Add($extra) }
        Log ("case=$($case.name) argCount=$($arguments.Count) args=" + ($arguments -join ' '))

        $startInfo = [System.Diagnostics.ProcessStartInfo]::new($exe)
        foreach ($argument in $arguments) { $startInfo.ArgumentList.Add($argument) }
        $startInfo.UseShellExecute = $false
        $startInfo.CreateNoWindow = $true
        $startInfo.RedirectStandardOutput = $true
        $startInfo.RedirectStandardError = $true
        $startInfo.WorkingDirectory = Split-Path -Parent $exe

        $timer = [System.Diagnostics.Stopwatch]::StartNew()
        $process = [System.Diagnostics.Process]::Start($startInfo)
        $stdout = $process.StandardOutput.ReadToEndAsync()
        $stderr = $process.StandardError.ReadToEndAsync()
        $exited = $process.WaitForExit($TimeoutSeconds * 1000)
        $timer.Stop()
        if (-not $exited) {
            try { $process.Kill($true) } catch { }
            $failures.Add("$($case.name): process did not exit within ${TimeoutSeconds}s")
            Log "case=$($case.name) TIMEOUT"
            $results.Add([ordered]@{ name = $case.name; exitCode = -1; fatalLog = $null; startupLogWritten = $false; matched = $false; elapsedMs = $timer.ElapsedMilliseconds })
            continue
        }

        $exitCode = $process.ExitCode
        $fatalPath = Join-Path $logDir 'fatal.log'
        $startupPath = Join-Path $logDir 'startup.log'
        $fatalExists = Test-Path $fatalPath
        $startupText = if (Test-Path $startupPath) { [System.IO.File]::ReadAllText($startupPath) } else { '' }
        $matched = $startupText.Contains($case.marker)
        $fallbackMatched = $startupText.Contains($case.fallback)

        if ($exitCode -ne 0) { $failures.Add("$($case.name): exit_code=$exitCode ($($stdout.Result)$($stderr.Result))") }
        if ($fatalExists) { $failures.Add("$($case.name): fatal.log was written") }
        if (-not $matched) { $failures.Add("$($case.name): startup.log has no '$($case.marker)' line") }
        if (-not $fallbackMatched) { $failures.Add("$($case.name): startup.log has no '$($case.fallback)' line") }

        Log ("case=$($case.name) exit=$exitCode fatal=$fatalExists startupBytes=$($startupText.Length) " +
             "matched=$matched fallback=$fallbackMatched elapsedMs=$($timer.ElapsedMilliseconds)")

        $results.Add([ordered]@{
            name = $case.name
            arguments = $arguments
            exitCode = $exitCode
            fatalLog = $fatalExists
            startupLogWritten = (Test-Path $startupPath)
            startupLogBytes = $startupText.Length
            matched = $matched
            expectedMarker = $case.marker
            fallbackMatched = $fallbackMatched
            expectedFallback = $case.fallback
            elapsedMs = $timer.ElapsedMilliseconds
            root = $root
        })

        $caseLog = Join-Path $logOut ("startup-matrix-$($case.name).log")
        [System.IO.File]::WriteAllText($caseLog, $startupText + [Environment]::NewLine,
            [System.Text.UTF8Encoding]::new($false))
    }

    $evidence = [ordered]@{
        task = 'FEA-07-RESIDUAL-3'
        ac = 'AC-R4b-3 (AC4 real startup entry + diagnostics sink)'
        mode = 'real process, four argument sets, isolated data root / theme home / log dir'
        generatedAt = (Get-Date).ToString('o')
        executable = $exe
        exitAfterMs = $ExitAfterMs
        cases = @($results)
        failures = @($failures)
        verdict = $(if ($failures.Count -eq 0) { 'PASS' } else { 'FAIL' })
    }
    [System.IO.File]::WriteAllText((Join-Path $evidenceOut 'startup-matrix-r4b.json'),
        ($evidence | ConvertTo-Json -Depth 8) + [Environment]::NewLine,
        [System.Text.UTF8Encoding]::new($false))

    if ($failures.Count -gt 0) {
        Log ('FATAL(12): ' + ($failures -join '; '))
        exit 12
    }

    Log 'PASS: 4/4 real startup cases -> exit_code=0, no fatal.log, startup.log carries the expected diagnostic line'
    exit 0
}
finally {
    try {
        $logPath = Join-Path $logOut 'startup-matrix.log'
        [System.IO.File]::WriteAllText($logPath, ($log -join [Environment]::NewLine) + [Environment]::NewLine,
            [System.Text.UTF8Encoding]::new($false))
    }
    catch {
        Write-Host 'WARN: could not write the startup-matrix log'
    }
}
