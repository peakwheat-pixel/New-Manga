<#
.SYNOPSIS
    P02 Workbench Real WebView2 Verification Runner (Stage A r4).
.DESCRIPTION
    Runs read-only environment identity probe, static frontend control probe,
    and Stage A preflight verification harness. Adheres strictly to the
    Hard Build Barrier: does not invoke Cargo or Tauri build in this worktree.
.PARAMETER ProbeOnly
    If specified, runs only the read-only environment and static contract probes,
    logging output to probe-execution-probeonly.log.
#>

param(
    [switch]$ProbeOnly
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..\..")

# Distinct log path per mode (Item 5: ProbeOnly and Full Stage A do not overwrite each other)
$LogFile = if ($ProbeOnly) { "probe-execution-probeonly.log" } else { "probe-execution-full.log" }
$LogPath = Join-Path $ScriptDir $LogFile
$LegacyLogPath = Join-Path $ScriptDir "probe-execution.log"

$PythonExe = (Get-Command python).Source
$NodeVer = try { (node -v) } catch { "UNAVAILABLE" }
$NpmVer = try { (npm.cmd -v) } catch { "UNAVAILABLE" }

$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$LogBuffer = [System.Collections.Generic.List[string]]::new()

function Append-Log([string]$line) {
    $LogBuffer.Add($line)
}

function Flush-Log {
    $allText = ($LogBuffer -join "`n") + "`n"
    $allTextLf = $allText.Replace("`r`n", "`n").Replace("`r", "`n")
    [System.IO.File]::WriteAllText($LogPath, $allTextLf, $Utf8NoBom)
    if (-not $ProbeOnly) {
        # Keep legacy probe-execution.log synced for full run
        [System.IO.File]::WriteAllText($LegacyLogPath, $allTextLf, $Utf8NoBom)
    }
}

Append-Log "=========================================================="
Append-Log "P02 Probe Execution Log"
Append-Log "Date: $(Get-Date -Format "yyyy-MM-ddTHH:mm:ssK")"
Append-Log "PowerShell: $($PSVersionTable.PSVersion)"
Append-Log "Python: $PythonExe ($(& $PythonExe --version))"
Append-Log "Node: $NodeVer"
Append-Log "npm: $NpmVer"
Append-Log "Worktree: $RepoRoot"
Append-Log "Mode: $(if ($ProbeOnly) { 'ProbeOnly' } else { 'Full Stage A' })"
Append-Log "LogFile: $LogFile"
Append-Log "=========================================================="

function Execute-Step {
    param(
        [string]$StepName,
        [string]$Command,
        [string[]]$Arguments
    )

    Write-Host "`n[$StepName] Executing: $Command $($Arguments -join ' ')..." -ForegroundColor Yellow
    Append-Log "`n--- [$StepName] ---"
    Append-Log "Command: $Command $($Arguments -join ' ')"

    $output = & $Command @Arguments 2>&1
    $exitCode = $LASTEXITCODE

    $outStr = ($output | Out-String).Trim()
    if ($outStr) {
        Write-Host $outStr
        Append-Log "OUTPUT:`n$outStr"
    }

    Append-Log "EXIT: $exitCode"

    if ($exitCode -ne 0) {
        Append-Log "`n[FAILURE] [$StepName] Failed with exit code $exitCode"
        Flush-Log
        Write-Host "[$StepName] Failed with exit code $exitCode" -ForegroundColor Red
        exit $exitCode
    }
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " P02 Real Workbench WebView2 Verification Harness (Stage A r4)" -ForegroundColor Cyan
Write-Host " Worktree: $RepoRoot" -ForegroundColor Cyan
Write-Host " Mode: $(if ($ProbeOnly) { 'ProbeOnly' } else { 'Full Stage A' })" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

try {
    # 1. Environment & Identity Probe
    $EnvProbe = Join-Path $ScriptDir "probes\env_identity_probe.py"
    Execute-Step "Step 1: Environment Identity Probe" $PythonExe @($EnvProbe)

    # 2. Static Source Contract Control Probe
    $StaticProbe = Join-Path $ScriptDir "probes\static_control_probe.py"
    Execute-Step "Step 2: Static Source Contract Probe" $PythonExe @($StaticProbe)

    if ($ProbeOnly) {
        Write-Host "`nProbeOnly specified; Stage A preflight probes complete (EXIT=0)." -ForegroundColor Green
        Append-Log "`nProbeOnly execution completed successfully with EXIT=0."
        exit 0
    }

    # 3. Stage A Harness & Verdict Generator
    $HarnessPy = Join-Path $ScriptDir "harness\workbench_cdp_harness.py"
    Execute-Step "Step 3: Stage A Verdict Harness" $PythonExe @($HarnessPy)

    Write-Host "`n==========================================================" -ForegroundColor Green
    Write-Host " P02 Stage A Full Execution Complete (EXIT=0)" -ForegroundColor Green
    Write-Host "==========================================================" -ForegroundColor Green

    Append-Log "`nFull Stage A execution completed successfully with EXIT=0."
    exit 0
}
catch {
    Append-Log "`n[UNHANDLED_EXCEPTION] $($_.Exception.Message)"
    Write-Host "Unhandled exception: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
finally {
    Flush-Log
}
