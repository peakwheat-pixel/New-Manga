# test-ac1-overlay-bound.ps1
# P20-CLOSE-BOUND-1 AC1, AC2, AC3, AC6 Automated Verification Suite
param(
    [string]$TargetDir = "verification/P20-CLOSE-BOUND-1"
)

$ErrorActionPreference = "Continue"
$Timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"
Write-Host "[$Timestamp] Starting P20-CLOSE-BOUND-1 verification run..."

# Ensure target directory exists
if (-not (Test-Path $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
}

function Run-LoggedCommand {
    param(
        [string]$CommandName,
        [string]$CommandLine,
        [string]$LogBase
    )
    $startTime = Get-Date
    $isoStart = $startTime.ToString("yyyy-MM-ddTHH:mm:sszzz")
    Write-Host "[$isoStart] Executing: $CommandLine"

    $stdoutFile = Join-Path $TargetDir "$LogBase.stdout.log"
    $stderrFile = Join-Path $TargetDir "$LogBase.stderr.log"
    $exitFile   = Join-Path $TargetDir "$LogBase.exit"
    $metaFile   = Join-Path $TargetDir "$LogBase.meta.json"

    $pinfo = New-Object System.Diagnostics.ProcessStartInfo
    $pinfo.FileName = "cmd.exe"
    $pinfo.Arguments = "/c $CommandLine"
    $pinfo.RedirectStandardOutput = $true
    $pinfo.RedirectStandardError = $true
    $pinfo.UseShellExecute = $false
    $pinfo.CreateNoWindow = $true

    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $pinfo
    $proc.Start() | Out-Null

    $stdoutTask = $proc.StandardOutput.ReadToEndAsync()
    $stderrTask = $proc.StandardError.ReadToEndAsync()

    $proc.WaitForExit()
    $exitCode = $proc.ExitCode
    $stdout = $stdoutTask.Result
    $stderr = $stderrTask.Result

    $endTime = Get-Date
    $durationMs = ($endTime - $startTime).TotalMilliseconds
    $isoEnd = $endTime.ToString("yyyy-MM-ddTHH:mm:sszzz")

    [System.IO.File]::WriteAllText($stdoutFile, $stdout, [System.Text.Encoding]::UTF8)
    [System.IO.File]::WriteAllText($stderrFile, $stderr, [System.Text.Encoding]::UTF8)
    [System.IO.File]::WriteAllText($exitFile, $exitCode.ToString(), [System.Text.Encoding]::UTF8)

    $meta = @{
        command = $CommandLine
        command_name = $CommandName
        start_time = $isoStart
        end_time = $isoEnd
        duration_ms = [math]::Round($durationMs, 2)
        exit_code = $exitCode
        cwd = (Get-Location).Path
    }
    $metaJson = $meta | ConvertTo-Json -Depth 4
    [System.IO.File]::WriteAllText($metaFile, $metaJson, [System.Text.Encoding]::UTF8)

    Write-Host "[$isoEnd] Finished $CommandName -> ExitCode: $exitCode, Duration: $([math]::Round($durationMs, 2)) ms"
    return @{ ExitCode = $exitCode; DurationMs = $durationMs; Stdout = $stdout }
}

# 1. AC1 & AC2: In-flight unresponsive call + external kill overlay test
$overlayRes = Run-LoggedCommand `
    -CommandName "rust_overlay_bound_test" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_drop_after_external_kill" `
    -LogBase "ac1-overlay-bound"

# 2. AC3: Regression check for resilient_channel (9 passed)
$resilientRes = Run-LoggedCommand `
    -CommandName "rust_resilient_channel_tests" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel" `
    -LogBase "ac3-resilient-channel"

# 3. AC3: Regression check for stdio_channel_drop (1 passed)
$stdioRes = Run-LoggedCommand `
    -CommandName "rust_stdio_channel_drop_test" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop stdio_channel_drop" `
    -LogBase "ac3-stdio-channel-drop"

# 4. AC1/AC4: Hard upper bound unit tests (already exited child & hung reader guard)
$unitRes1 = Run-LoggedCommand `
    -CommandName "rust_wait_timeout_or_kill_test" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop wait_timeout_or_kill_returns_immediately" `
    -LogBase "ac4-wait-timeout-or-kill"

$unitRes2 = Run-LoggedCommand `
    -CommandName "rust_reader_guard_test" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop reader_join_guard_enforces_hard_timeout" `
    -LogBase "ac4-reader-guard"

# 5. AC2: Direct Process Tree and Zero Residual Orphan Check
Write-Host "Checking system for residual core_service / m2rc1-desktop / host_bridge processes..."
$procs = Get-CimInstance Win32_Process | Where-Object {
    $_.Name -like "*core_service*" -or
    $_.Name -like "*m2rc1_desktop*" -or
    $_.Name -like "*host_bridge*"
}

$treeReport = New-Object System.Text.StringBuilder
$treeReport.AppendLine("=== Process Tree Zero Orphan Audit ===") | Out-Null
$treeReport.AppendLine("Timestamp: $(Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz')") | Out-Null

$residualCount = 0
if ($procs) {
    foreach ($p in $procs) {
        $treeReport.AppendLine("Process: Name=$($p.Name), PID=$($p.ProcessId), ParentPID=$($p.ParentProcessId), CommandLine=$($p.CommandLine)") | Out-Null
        $residualCount++
    }
} else {
    $treeReport.AppendLine("No matching residual processes found. Count = 0 (CLEAN)") | Out-Null
}

$treeReportFile = Join-Path $TargetDir "ac2-process-tree-audit.log"
[System.IO.File]::WriteAllText($treeReportFile, $treeReport.ToString(), [System.Text.Encoding]::UTF8)
Write-Host "Process tree audit complete. Residual process count: $residualCount"

Write-Host "Suite complete."
