<#
.SYNOPSIS
    P02 Workbench Real WebView2 Verification Runner (Stage A r2).
.DESCRIPTION
    Runs read-only environment identity probe, static frontend control probe,
    and the Stage A preflight verification harness. Adheres strictly to the
    Hard Build Barrier: does not invoke Cargo or Tauri build in this worktree.
.PARAMETER ProbeOnly
    If specified, runs only the read-only environment and static contract probes.
#>

param(
    [switch]$ProbeOnly
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..\..")
$LogPath = Join-Path $ScriptDir "probe-execution.log"

$PythonExe = (Get-Command python).Source
$NodeVer = try { (node -v) } catch { "UNAVAILABLE" }
$NpmVer = try { (npm.cmd -v) } catch { "UNAVAILABLE" }

$LogHeader = @"
==========================================================
P02 Probe Execution Log
Date: $(Get-Date -Format "yyyy-MM-ddTHH:mm:ssK")
PowerShell: $($PSVersionTable.PSVersion)
Python: $PythonExe ($(& $PythonExe --version))
Node: $NodeVer
npm: $NpmVer
Worktree: $RepoRoot
==========================================================
"@

Set-Content -Path $LogPath -Value $LogHeader -Encoding utf8

function Execute-Step {
    param(
        [string]$StepName,
        [string]$Command,
        [string[]]$Arguments
    )

    Write-Host "`n[$StepName] Executing: $Command $($Arguments -join ' ')..." -ForegroundColor Yellow
    Add-Content -Path $LogPath -Value "`n--- [$StepName] ---" -Encoding utf8
    Add-Content -Path $LogPath -Value "Command: $Command $($Arguments -join ' ')" -Encoding utf8

    $output = & $Command @Arguments 2>&1
    $exitCode = $LASTEXITCODE

    $outStr = ($output | Out-String).Trim()
    if ($outStr) {
        Write-Host $outStr
        Add-Content -Path $LogPath -Value "OUTPUT:`n$outStr" -Encoding utf8
    }

    Add-Content -Path $LogPath -Value "EXIT: $exitCode" -Encoding utf8

    if ($exitCode -ne 0) {
        Write-Error "[$StepName] Failed with exit code $exitCode"
        exit $exitCode
    }
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " P02 Real Workbench WebView2 Verification Harness (Stage A r2)" -ForegroundColor Cyan
Write-Host " Worktree: $RepoRoot" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Environment & Identity Probe
$EnvProbe = Join-Path $ScriptDir "probes\env_identity_probe.py"
Execute-Step "Step 1: Environment Identity Probe" $PythonExe @($EnvProbe)

# 2. Static Source Contract Control Probe
$StaticProbe = Join-Path $ScriptDir "probes\static_control_probe.py"
Execute-Step "Step 2: Static Source Contract Probe" $PythonExe @($StaticProbe)

if ($ProbeOnly) {
    Write-Host "`nProbeOnly specified; Stage A preflight complete." -ForegroundColor Green
    exit 0
}

# 3. Stage A Harness & Verdict Generator
$HarnessPy = Join-Path $ScriptDir "harness\workbench_cdp_harness.py"
Execute-Step "Step 3: Stage A Verdict Harness" $PythonExe @($HarnessPy)

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host " P02 Stage A Safe Foundation Execution Complete (EXIT=0)" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
exit 0
