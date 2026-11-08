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
        $childCwd = Split-Path -Parent $exe
        $startInfo.WorkingDirectory = $childCwd

        # r1/r2 (P1-01) 红线：**主闸是产品契约**「显式 --log-dir 拥有全部日志文件」（含 legacy 的
        # window-material.log 两条分支：材质行 + RenderScaling 行）。下面注入 APPDATA/LOCALAPPDATA/USERPROFILE
        # 只是让子进程暴露在隔离环境里，**不是隔离保证**（r2 实测：App 的 GetFolderPath(ApplicationData)
        # 可能返回空 → 落成 cwd 相对路径）。隔离证据改为 App 可见断言（见下面 sink 行 / cwd / 唯一文件）。
        $isolatedAppData = Join-Path $root 'appdata'
        $isolatedLocalAppData = Join-Path $root 'localappdata'
        $isolatedProfile = Join-Path $root 'userprofile'
        foreach ($dir in @($isolatedAppData, $isolatedLocalAppData, $isolatedProfile)) {
            New-Item -ItemType Directory -Force -Path $dir | Out-Null
        }
        $startInfo.Environment['APPDATA'] = $isolatedAppData
        $startInfo.Environment['LOCALAPPDATA'] = $isolatedLocalAppData
        $startInfo.Environment['USERPROFILE'] = $isolatedProfile

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

        # 隔离直接证据（r2 App 可见探针）：
        #  (a) sink 安装行必须指向本用例的隔离 log 目录；
        #  (b) sink isolation 行给出 App 实见的 log-dir/appdata/cwd，且 appdata 不得被指向本用例根。
        $sinkLine = 'startup-diagnostics: sink v1 installed (' + [System.IO.Path]::GetFullPath($startupPath) + ')'
        if (-not $startupText.Contains($sinkLine)) {
            $failures.Add("$($case.name): startup.log install line does not point at the isolated log dir")
        }
        $isolationLine = ($startupText -split "`n" | Where-Object { $_.Contains('startup-diagnostics: isolation') } | Select-Object -Last 1)
        if (-not $isolationLine) {
            $failures.Add("$($case.name): startup.log carries no App-visible isolation line")
            $appDataSeen = '<missing>'
        }
        else {
            if (-not $isolationLine.Contains('log-dir=' + [System.IO.Path]::GetFullPath($logDir))) {
                $failures.Add("$($case.name): the App-visible isolation line does not point at the isolated log dir")
            }
            $appDataToken = ($isolationLine -split ' ' | Where-Object { $_.StartsWith('appdata=') } | Select-Object -First 1)
            $appDataSeen = if ($appDataToken) { $appDataToken.Substring('appdata='.Length) } else { '' }
            if ($appDataSeen -and $appDataSeen.StartsWith([System.IO.Path]::GetFullPath($root), [System.StringComparison]::OrdinalIgnoreCase)) {
                $failures.Add("$($case.name): the App-visible appdata was redirected into the case root ('$appDataSeen')")
            }
        }

        # legacy 外壳的历史诊断文件（window-material.log）现在也受 --log-dir 契约约束：落隔离目录。
        $isolatedMaterial = Join-Path $logDir 'window-material.log'
        $isolatedMaterialLines = if (Test-Path $isolatedMaterial) { @([System.IO.File]::ReadAllLines($isolatedMaterial)).Count } else { 0 }
        if ($case.name -eq 'shell-legacy' -and $isolatedMaterialLines -le 0) {
            $failures.Add("$($case.name): window-material.log did not land inside the isolated --log-dir")
        }

        # r2：window-material.log 只允许出现在隔离 --log-dir 内；子进程 cwd 下不得出现 com.newmanga.desktop。
        $strayMaterial = [System.Collections.Generic.List[string]]::new()
        $cwdNamespace = Join-Path $childCwd 'com.newmanga.desktop'
        if (Test-Path $cwdNamespace) { $strayMaterial.Add($cwdNamespace) }
        if (Test-Path $cwdNamespace) {
            Get-ChildItem -Recurse -File -Path $cwdNamespace -Filter 'window-material.log' -ErrorAction SilentlyContinue |
                ForEach-Object { $strayMaterial.Add($_.FullName) }
        }
        if ($strayMaterial.Count -gt 0) {
            $failures.Add("$($case.name): writes outside the isolated --log-dir: $($strayMaterial -join '; ')")
        }

        # 红线：真实 %APPDATA% 的 window-material.log 行数不得增长。
        $realLinesNow = if (Test-Path $script:realMaterialLog) { @([System.IO.File]::ReadAllLines($script:realMaterialLog)).Count } else { 0 }
        if ($realLinesNow -ne $script:realMaterialLinesBefore) {
            $failures.Add("$($case.name): the real %APPDATA% window-material.log grew $($script:realMaterialLinesBefore) -> $realLinesNow")
        }

        Log ("case=$($case.name) exit=$exitCode fatal=$fatalExists startupBytes=$($startupText.Length) " +
             "matched=$matched fallback=$fallbackMatched isolatedMaterialLines=$isolatedMaterialLines " +
             "appdataSeen=$appDataSeen strayOutsideIsolation=$($strayMaterial.Count) " +
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
            appVisibleIsolationLine = $isolationLine
            appVisibleAppData = $appDataSeen
            injectedAppData = $isolatedAppData
            childCwd = $childCwd
            strayOutsideIsolation = @($strayMaterial)
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
