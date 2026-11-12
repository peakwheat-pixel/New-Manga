param([string]$WorkspaceRoot)

$ErrorActionPreference = 'Stop'
$repoRoot = 'G:\CODEX\New Manga'
$defaultProbeRoot = 'G:\CODEX\New Manga.workspace\task-env\NEW-MANGA-V1-FULL-AUDIT\sidecar-lifecycle-probe'
if ([string]::IsNullOrWhiteSpace($WorkspaceRoot)) {
    $runId = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffffffZ')
    $WorkspaceRoot = Join-Path $defaultProbeRoot $runId
}
$workspacePrefix = [System.IO.Path]::GetFullPath('G:\CODEX\New Manga.workspace\').TrimEnd('\') + '\'
$resolvedWorkspace = [System.IO.Path]::GetFullPath($WorkspaceRoot)
if (-not $resolvedWorkspace.StartsWith($workspacePrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "probe output must remain under New Manga.workspace: $resolvedWorkspace"
}

$assemblyPath = 'G:\CODEX\New Manga.workspace\agent-output\codex\NEW-MANGA-V1-FULL-AUDIT\build-20261112\bin\Debug\net9.0\NewManga.CoreClient.dll'
$childExe = Join-Path $env:WINDIR 'System32\WindowsPowerShell\v1.0\powershell.exe'
if (-not (Test-Path -LiteralPath $assemblyPath)) { throw "built assembly not found: $assemblyPath" }
if (-not (Test-Path -LiteralPath $childExe)) { throw "PowerShell child executable not found: $childExe" }

New-Item -ItemType Directory -Force -Path $resolvedWorkspace | Out-Null
Add-Type -Path $assemblyPath
$assemblyHash = (Get-FileHash -LiteralPath $assemblyPath -Algorithm SHA256).Hash
$head = (& git -C $repoRoot rev-parse HEAD).Trim()
$startedUtc = [DateTime]::UtcNow.ToString('o')

function New-ProbeSpec([string]$name, [string]$pidFile, [string]$stderrLog) {
    $environment = [System.Collections.Generic.Dictionary[string, string]]::new([System.StringComparer]::Ordinal)
    $environment['NM_AUDIT_PID_FILE'] = $pidFile
    $script = '[System.IO.File]::WriteAllText($env:NM_AUDIT_PID_FILE, [string]$PID); Start-Sleep -Seconds 60'
    $spec = [NewManga.CoreClient.Transport.SidecarSpec]::new()
    $spec.Name = $name
    $spec.ExecutablePath = $childExe
    $spec.WorkingDirectory = $resolvedWorkspace
    $spec.Environment = $environment
    $spec.AdditionalArguments = [string[]]@('-NoLogo', '-NoProfile', '-NonInteractive', '-Command', $script)
    $spec.StderrLogPath = $stderrLog
    $spec.StartupTimeout = [TimeSpan]::FromSeconds(5)
    $spec.RequestTimeout = [TimeSpan]::FromSeconds(5)
    return $spec
}

function Wait-ChildPid([string]$pidFile) {
    if (Test-Path -LiteralPath $pidFile) { throw "refusing stale PID marker: $pidFile" }
    $until = [DateTime]::UtcNow.AddSeconds(5)
    while ([DateTime]::UtcNow -lt $until) {
        if (Test-Path -LiteralPath $pidFile) {
            $value = (Get-Content -LiteralPath $pidFile -Raw).Trim()
            if ($value -match '^\d+$') { return [int]$value }
        }
        Start-Sleep -Milliseconds 100
    }
    throw "child did not write PID marker: $pidFile"
}

function Get-ChildAlive([int]$processId) {
    try {
        $process = [System.Diagnostics.Process]::GetProcessById($processId)
        return -not $process.HasExited
    }
    catch [System.ArgumentException] {
        return $false
    }
}

function Stop-ProbeChild([int]$processId) {
    try {
        $process = [System.Diagnostics.Process]::GetProcessById($processId)
        if (-not $process.HasExited) { $process.Kill($true) }
        $process.WaitForExit(5000) | Out-Null
        return $process.HasExited
    }
    catch [System.ArgumentException] {
        return $true
    }
}

$results = [System.Collections.Generic.List[object]]::new()

$cancelPidFile = Join-Path $resolvedWorkspace 'pre-cancel-child.pid'
$cancelStderr = Join-Path $resolvedWorkspace 'pre-cancel-child.stderr.log'
$cancelSource = [System.Threading.CancellationTokenSource]::new()
$cancelSource.Cancel()
$cancelException = 'none'
$cancelPid = 0
try {
    $spec = New-ProbeSpec 'audit-pre-cancel' $cancelPidFile $cancelStderr
    try {
        [NewManga.CoreClient.Transport.SidecarProcess]::StartAsync($spec, $cancelSource.Token).GetAwaiter().GetResult() | Out-Null
    }
    catch [System.OperationCanceledException] {
        $cancelException = $_.Exception.GetType().Name
    }
catch {
    $cancelException = $_.Exception.GetType().Name
}
    $cancelPid = Wait-ChildPid $cancelPidFile
    Start-Sleep -Milliseconds 500
    $cancelAlive = Get-ChildAlive $cancelPid
    $cancelKilled = Stop-ProbeChild $cancelPid
    $results.Add([pscustomobject]@{
        case = 'pre_cancel_after_spawn'
        observed_exception = $cancelException
        child_pid = $cancelPid
        child_alive_after_start_failed = $cancelAlive
        cleanup_killed_child = $cancelKilled
    })
}
finally {
    if ($cancelPid -gt 0 -and (Get-ChildAlive $cancelPid)) { Stop-ProbeChild $cancelPid | Out-Null }
    $cancelSource.Dispose()
}

$disposePidFile = Join-Path $resolvedWorkspace 'dispose-only-child.pid'
$disposeStderr = Join-Path $resolvedWorkspace 'dispose-only-child.stderr.log'
$disposePid = 0
try {
    $spec = New-ProbeSpec 'audit-dispose-only' $disposePidFile $disposeStderr
    $sidecar = [NewManga.CoreClient.Transport.SidecarProcess]::StartAsync($spec).GetAwaiter().GetResult()
    $disposePid = Wait-ChildPid $disposePidFile
    $disposeClock = [System.Diagnostics.Stopwatch]::StartNew()
    $sidecar.DisposeAsync().AsTask().GetAwaiter().GetResult() | Out-Null
    $disposeClock.Stop()
    Start-Sleep -Milliseconds 500
    $disposeAlive = Get-ChildAlive $disposePid
    $disposeKilled = Stop-ProbeChild $disposePid
    $results.Add([pscustomobject]@{
        case = 'dispose_without_explicit_stop'
        child_pid = $disposePid
        dispose_elapsed_ms = $disposeClock.ElapsedMilliseconds
        child_alive_after_dispose_returned = $disposeAlive
        cleanup_killed_child = $disposeKilled
    })
}
finally {
    if ($disposePid -gt 0 -and (Get-ChildAlive $disposePid)) { Stop-ProbeChild $disposePid | Out-Null }
}

[pscustomobject]@{
    generated_utc = $startedUtc
    generated_head = $head
    assembly_path = $assemblyPath
    assembly_sha256 = $assemblyHash
    child_executable = $childExe
    workspace_root = $resolvedWorkspace
    results = @($results)
} | ConvertTo-Json -Depth 6
