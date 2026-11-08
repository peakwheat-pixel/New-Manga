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

# 红线（P1-01）：真实用户目录下既有 legacy 诊断日志的行数基线；整轮矩阵前后必须**不变**。
# 解析走 .NET 的 KnownFolder（与本脚本自身 APPDATA env 无关），测的就是真实用户目录。
$realMaterialLog = Join-Path ([Environment]::GetFolderPath([Environment+SpecialFolder]::ApplicationData)) 'com.newmanga.desktop\logs\window-material.log'
$realMaterialLinesBefore = if (Test-Path $realMaterialLog) { @([System.IO.File]::ReadAllLines($realMaterialLog)).Count } else { 0 }

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

        # r1 (P1-01) 红线加固 —— 纵深防御：子进程的 APPDATA/LOCALAPPDATA/USERPROFILE 也指向本用例隔离根。
        # 真正阻止写真实用户目录的是产品契约「显式 --log-dir 拥有全部日志文件」（含 legacy 的 window-material.log）；
        # env 注入是第二道闸。注入后用**同一环境字典**回读子进程值确认生效。
        $isolatedAppData = Join-Path $root 'appdata'
        $isolatedLocalAppData = Join-Path $root 'localappdata'
        $isolatedProfile = Join-Path $root 'userprofile'
        foreach ($dir in @($isolatedAppData, $isolatedLocalAppData, $isolatedProfile)) {
            New-Item -ItemType Directory -Force -Path $dir | Out-Null
        }
        $startInfo.Environment['APPDATA'] = $isolatedAppData
        $startInfo.Environment['LOCALAPPDATA'] = $isolatedLocalAppData
        $startInfo.Environment['USERPROFILE'] = $isolatedProfile

        $probeFile = Join-Path $root 'env-probe.txt'
        $probeInfo = [System.Diagnostics.ProcessStartInfo]::new('pwsh')
        # 注意：-Command 载荷内部用**双引号**。用单引号包路径时，外层命令行引用会让子进程把路径当相对路径
        # （实测：WriteAllText('C:\..') 被解析成 "<cwd>\ C:\.."），探针因此静默失败。
        $probeCommand = '[System.IO.File]::WriteAllText("' + $probeFile + '", $env:APPDATA + "|" + $env:LOCALAPPDATA)'
        foreach ($a in @('-NoProfile', '-Command', $probeCommand)) { $probeInfo.ArgumentList.Add($a) }
        $probeInfo.UseShellExecute = $false
        $probeInfo.CreateNoWindow = $true
        $probeInfo.Environment['APPDATA'] = $isolatedAppData
        $probeInfo.Environment['LOCALAPPDATA'] = $isolatedLocalAppData
        $probeInfo.Environment['USERPROFILE'] = $isolatedProfile
        $probe = [System.Diagnostics.Process]::Start($probeInfo)
        $probe.WaitForExit(60000) | Out-Null
        if (-not (Test-Path $probeFile)) {
            $failures.Add("$($case.name): the child environment probe produced no output")
            $envProbe = '<missing>'
        }
        else {
            $envProbe = [System.IO.File]::ReadAllText($probeFile)
            if (-not ($envProbe.StartsWith([System.IO.Path]::GetFullPath($isolatedAppData), [System.StringComparison]::OrdinalIgnoreCase))) {
                $failures.Add("$($case.name): injected APPDATA did not reach the child ($envProbe)")
            }
        }
        Log "case=$($case.name) env-probe=$envProbe"

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

        # 隔离直接证据：sink 安装行必须指向本用例的隔离 log 目录。
        $sinkLine = 'startup-diagnostics: sink v1 installed (' + [System.IO.Path]::GetFullPath($startupPath) + ')'
        if (-not $startupText.Contains($sinkLine)) {
            $failures.Add("$($case.name): startup.log install line does not point at the isolated log dir")
        }

        # legacy 外壳的历史诊断文件（window-material.log）现在也受 --log-dir 契约约束：落隔离目录。
        $isolatedMaterial = Join-Path $logDir 'window-material.log'
        $isolatedMaterialLines = if (Test-Path $isolatedMaterial) { @([System.IO.File]::ReadAllLines($isolatedMaterial)).Count } else { 0 }
        if ($case.name -eq 'shell-legacy' -and $isolatedMaterialLines -le 0) {
            $failures.Add("$($case.name): window-material.log did not land inside the isolated --log-dir")
        }

        # 红线：真实 %APPDATA% 的 window-material.log 行数不得增长。
        $realLinesNow = if (Test-Path $script:realMaterialLog) { @([System.IO.File]::ReadAllLines($script:realMaterialLog)).Count } else { 0 }
        if ($realLinesNow -ne $script:realMaterialLinesBefore) {
            $failures.Add("$($case.name): the real %APPDATA% window-material.log grew $($script:realMaterialLinesBefore) -> $realLinesNow")
        }

        Log ("case=$($case.name) exit=$exitCode fatal=$fatalExists startupBytes=$($startupText.Length) " +
             "matched=$matched fallback=$fallbackMatched isolatedMaterialLines=$isolatedMaterialLines " +
             "realAppDataMaterialLines=$realLinesNow elapsedMs=$($timer.ElapsedMilliseconds)")

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
            isolatedLogDir = $logDir
            isolatedAppData = $isolatedAppData
            childEnvironmentProbe = $envProbe
            isolatedMaterialLines = $isolatedMaterialLines
            realAppDataMaterialLines = $realLinesNow
            elapsedMs = $timer.ElapsedMilliseconds
            root = $root
        })

        $caseLog = Join-Path $logOut ("startup-matrix-$($case.name).log")
        [System.IO.File]::WriteAllText($caseLog, $startupText + [Environment]::NewLine,
            [System.Text.UTF8Encoding]::new($false))
    }

    $realMaterialLinesAfter = if (Test-Path $realMaterialLog) { @([System.IO.File]::ReadAllLines($realMaterialLog)).Count } else { 0 }
    if ($realMaterialLinesAfter -ne $realMaterialLinesBefore) {
        $failures.Add("red line: the real %APPDATA% window-material.log grew $realMaterialLinesBefore -> $realMaterialLinesAfter")
    }
    Log "red line: real %APPDATA% window-material.log lines $realMaterialLinesBefore -> $realMaterialLinesAfter (delta=$($realMaterialLinesAfter - $realMaterialLinesBefore))"

    $evidence = [ordered]@{
        task = 'FEA-07-RESIDUAL-3'
        ac = 'AC-R4b-3 (AC4 real startup entry + diagnostics sink)'
        mode = 'real process, four argument sets, isolated data root / theme home / log dir / child APPDATA'
        generatedAt = (Get-Date).ToString('o')
        executable = $exe
        exitAfterMs = $ExitAfterMs
        realUserProfileWindowMaterialLog = [ordered]@{
            path = $realMaterialLog
            linesBefore = $realMaterialLinesBefore
            linesAfter = $realMaterialLinesAfter
            delta = $realMaterialLinesAfter - $realMaterialLinesBefore
            untouched = ($realMaterialLinesAfter -eq $realMaterialLinesBefore)
        }
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

    Log 'PASS: 4/4 real startup cases -> exit_code=0, no fatal.log, startup.log carries the expected diagnostic line, legacy window-material.log inside the isolated --log-dir, real %APPDATA% untouched'
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
