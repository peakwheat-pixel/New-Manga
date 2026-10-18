# run-desktop-close-verification.ps1
# P20-CLOSE-BOUND-1 AC5: Real Interactive Desktop Window Close & Process Tree Verification Script
# NOTE: This script is intended to be run by the Coordinator in an interactive Windows desktop session
# with fully functional WebView2 runtime. Non-interactive agent sessions lack desktop GUI interaction (0x80070578).

param(
    [string]$AppExe = "apps/desktop/src-tauri/target/release/m2rc1-desktop.exe",
    [string]$SidecarDir = "resources/core-sidecar",
    [int]$HardBoundSeconds = 5
)

$ErrorActionPreference = "Stop"
$Timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"
Write-Host "[$Timestamp] === P20-CLOSE-BOUND-1 AC5 Interactive Desktop Verification ==="

# 1. Setup isolated data roots under $env:TEMP (strict isolation guarantee)
$isolatedId = [System.Guid]::NewGuid().ToString("N").Substring(0, 8)
$isolatedRoot = Join-Path $env:TEMP "p20close-$isolatedId"
$dataRoot = Join-Path $isolatedRoot "data"
$derivedRoot = Join-Path $isolatedRoot "derived"
$catalogDb = Join-Path $isolatedRoot "catalog/catalog.sqlite"

New-Item -ItemType Directory -Path $dataRoot -Force | Out-Null
New-Item -ItemType Directory -Path $derivedRoot -Force | Out-Null
New-Item -ItemType Directory -Path (Split-Path $catalogDb) -Force | Out-Null

Write-Host "Isolated root prepared at: $isolatedRoot"

# 2. Set environment variables for isolated execution
$env:NEWMANGA_DATA_ROOT = $dataRoot
$env:M2RC1_DERIVED_ROOT = $derivedRoot
$env:M2RC2_CATALOG_DB = $catalogDb
$env:M2RC1_MANAGED_ROOT = Join-Path $isolatedRoot "managed"
New-Item -ItemType Directory -Path $env:M2RC1_MANAGED_ROOT -Force | Out-Null

# Verify binary existence
if (-not (Test-Path $AppExe)) {
    # Check debug binary if release not found
    $AppExe = "apps/desktop/src-tauri/target/debug/m2rc1-desktop.exe"
}
if (-not (Test-Path $AppExe)) {
    Write-Error "Could not find m2rc1-desktop binary. Please build the desktop app first."
    exit 1
}

$resolvedExe = (Resolve-Path $AppExe).Path
Write-Host "Launching desktop application: $resolvedExe"

$pinfo = New-Object System.Diagnostics.ProcessStartInfo
$pinfo.FileName = $resolvedExe
$pinfo.UseShellExecute = $false
$pinfo.RedirectStandardOutput = $true
$pinfo.RedirectStandardError = $true
$pinfo.CreateNoWindow = $false

$proc = New-Object System.Diagnostics.Process
$proc.StartInfo = $pinfo
$proc.Start() | Out-Null
$appPid = $proc.Id

Write-Host "App launched with PID: $appPid. Waiting for window initialization and sidecar spawn (up to 10s)..."

$sidecarPids = @()
$foundWindow = $false
$pollStart = Get-Date

while (($null -eq $foundWindow -or -not $foundWindow) -and ((Get-Date) - $pollStart).TotalSeconds -lt 15) {
    Start-Sleep -Milliseconds 500
    
    # Query process tree
    $children = Get-CimInstance Win32_Process | Where-Object { $_.ParentProcessId -eq $appPid }
    if ($children) {
        $sidecarPids = $children | ForEach-Object { $_.ProcessId }
    }
    
    # Check main window handle
    $proc.Refresh()
    if ($proc.MainWindowHandle -ne 0) {
        $foundWindow = $true
        Write-Host "Main window detected! Handle: $($proc.MainWindowHandle)"
        break
    }
}

Write-Host "Process tree state: Main PID=$appPid, Child PIDs=$($sidecarPids -join ',')"

# 3. Request normal window close (CloseMainWindow / WM_CLOSE)
Write-Host "Sending CloseMainWindow request..."
$closeStart = Get-Date
$closeSuccess = $proc.CloseMainWindow()
Write-Host "CloseMainWindow returned: $closeSuccess"

# 4. Wait for application exit within hard upper bound
$exitedInBound = $proc.WaitForExit($HardBoundSeconds * 1000)
$closeEnd = Get-Date
$closeElapsedMs = ($closeEnd - $closeStart).TotalMilliseconds

Write-Host "App process exited: $exitedInBound (Took $closeElapsedMs ms, bound was $($HardBoundSeconds * 1000) ms)"

if (-not $exitedInBound) {
    Write-Error "TIMEOUT FAILED: Main application did NOT exit within $HardBoundSeconds seconds (Took $closeElapsedMs ms)! Force killing for test cleanup..."
    $proc.Kill()
    Remove-Item -Path $isolatedRoot -Recurse -Force -ErrorAction SilentlyContinue
    exit 1
}

# 5. Process Tree & Zero Residual Orphan Check
Start-Sleep -Milliseconds 500
$residualProcs = Get-CimInstance Win32_Process | Where-Object {
    $_.ProcessId -eq $appPid -or
    $sidecarPids -contains $_.ProcessId -or
    $_.ParentProcessId -eq $appPid -or
    $_.Name -like "*core_service*" -or
    $_.Name -like "*m2rc1_desktop*"
}

Write-Host "=== Process Tree Verification Summary ==="
Write-Host "Exit within bound: $exitedInBound"
Write-Host "Exit duration: $closeElapsedMs ms"
Write-Host "Residual process count: $($residualProcs.Count)"

if ($residualProcs.Count -gt 0) {
    Write-Host "FAILED: Residual processes found:" -ForegroundColor Red
    $residualProcs | ForEach-Object {
        Write-Host "  Name=$($_.Name), PID=$($_.ProcessId), ParentPID=$($_.ParentProcessId)"
    }
    Remove-Item -Path $isolatedRoot -Recurse -Force -ErrorAction SilentlyContinue
    exit 2
} else {
    Write-Host "SUCCESS: Application exited within bound ($closeElapsedMs ms) and zero orphan processes remaining. Clean exit verified." -ForegroundColor Green
}

# Cleanup isolated directory
Remove-Item -Path $isolatedRoot -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "Isolated root cleaned."
exit 0
