<#
.SYNOPSIS
    P02 Workbench Real WebView2 Verification Runner.
.DESCRIPTION
    Runs read-only environment identity probe, static frontend control probe,
    and the AC1-AC7 behavior verification harness. Adheres strictly to the
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

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " P02 Real Workbench WebView2 Verification Harness" -ForegroundColor Cyan
Write-Host " Worktree: $RepoRoot" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Environment & Identity Probe
Write-Host "`n[Step 1/3] Running Environment & Identity Probe..." -ForegroundColor Yellow
$EnvProbe = Join-Path $ScriptDir "probes\env_identity_probe.py"
& python $EnvProbe
if ($LASTEXITCODE -ne 0) {
    Write-Error "Environment identity probe failed with exit code $LASTEXITCODE"
}

# 2. Static Source Contract Control Probe
Write-Host "`n[Step 2/3] Running Static Source Contract Probe..." -ForegroundColor Yellow
$StaticProbe = Join-Path $ScriptDir "probes\static_control_probe.py"
& python $StaticProbe
if ($LASTEXITCODE -ne 0) {
    Write-Error "Static source contract probe failed with exit code $LASTEXITCODE"
}

if ($ProbeOnly) {
    Write-Host "`nProbeOnly specified; skipping full AC harness execution." -ForegroundColor Green
    exit 0
}

# 3. Behavior Verification Harness
Write-Host "`n[Step 3/3] Running AC1-AC7 Behavior Verification Harness..." -ForegroundColor Yellow
$HarnessPy = Join-Path $ScriptDir "harness\workbench_cdp_harness.py"
& python $HarnessPy
if ($LASTEXITCODE -ne 0) {
    Write-Error "Harness execution failed with exit code $LASTEXITCODE"
}

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host " P02 Stage A Safe Foundation Execution Complete" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
exit 0
