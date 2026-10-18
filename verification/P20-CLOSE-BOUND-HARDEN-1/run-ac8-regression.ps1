# run-ac8-regression.ps1
# P20-CLOSE-BOUND-HARDEN-1 AC8: Comprehensive Regression Test Suite

param(
    [string]$TargetDir = "verification/P20-CLOSE-BOUND-HARDEN-1"
)

$ErrorActionPreference = "Stop"

if (-not $env:CARGO_TARGET_DIR) {
    $env:CARGO_TARGET_DIR = Join-Path $env:TEMP "cargo-p20-test-target"
}

if (-not (Test-Path $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
}

$results = [System.Collections.Generic.List[PSCustomObject]]::new()

function Run-RegressionTest {
    param(
        [string]$Name,
        [string]$CommandLine,
        [string]$BaseFileName,
        [string]$Summary
    )

    Write-Host "Running AC8 Regression: $Name..."
    $start = Get-Date
    $stdoutFile = Join-Path $TargetDir "$BaseFileName.stdout.log"
    $stderrFile = Join-Path $TargetDir "$BaseFileName.stderr.log"
    $exitFile   = Join-Path $TargetDir "$BaseFileName.exit"
    $metaFile   = Join-Path $TargetDir "$BaseFileName.meta.json"

    $pinfo = New-Object System.Diagnostics.ProcessStartInfo
    $pinfo.FileName = "cmd.exe"
    $pinfo.Arguments = "/c $CommandLine"
    $pinfo.RedirectStandardOutput = $true
    $pinfo.RedirectStandardError = $true
    $pinfo.UseShellExecute = $false
    $pinfo.CreateNoWindow = $true

    $p = New-Object System.Diagnostics.Process
    $p.StartInfo = $pinfo
    $p.Start() | Out-Null

    $stdoutTask = $p.StandardOutput.ReadToEndAsync()
    $stderrTask = $p.StandardError.ReadToEndAsync()
    $p.WaitForExit()

    $stdoutContent = $stdoutTask.Result
    $stderrContent = $stderrTask.Result
    $exitCode = $p.ExitCode
    $end = Get-Date
    $durationMs = [math]::Round(($end - $start).TotalMilliseconds, 2)

    [System.IO.File]::WriteAllText($stdoutFile, $stdoutContent, [System.Text.Encoding]::UTF8)
    [System.IO.File]::WriteAllText($stderrFile, $stderrContent, [System.Text.Encoding]::UTF8)
    [System.IO.File]::WriteAllText($exitFile, $exitCode.ToString(), [System.Text.Encoding]::UTF8)

    $meta = [ordered]@{
        name = $Name
        command = $CommandLine
        exit_code = $exitCode
        duration_ms = $durationMs
        start = $start.ToString("yyyy-MM-ddTHH:mm:sszzz")
        end = $end.ToString("yyyy-MM-ddTHH:mm:sszzz")
        summary = $Summary
    }
    [System.IO.File]::WriteAllText($metaFile, ($meta | ConvertTo-Json -Depth 4), [System.Text.Encoding]::UTF8)

    $status = if ($exitCode -eq 0) { "PASS" } else { "FAIL" }
    $fgColor = if ($exitCode -eq 0) { "Green" } else { "Red" }
    Write-Host "  -> Result: $status (ExitCode: $exitCode, Took: $durationMs ms)" -ForegroundColor $fgColor

    $results.Add([PSCustomObject]@{
        Name = $Name
        Command = $CommandLine
        ExitCode = $exitCode
        DurationMs = $durationMs
        Status = $status
        Summary = $Summary
        ExitFile = $exitFile
    })
}

# 1. R-008 心跳恢复
Run-RegressionTest `
    -Name "R-008_heartbeat_recovery" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_heartbeat_detects_unresponsive_child_and_recovers -- --nocapture" `
    -BaseFileName "ac8-r008-heartbeat-recovery" `
    -Summary "R-008: Heartbeat detects unresponsive child and recovers"

# 2. R-003 拆环与 reap
Run-RegressionTest `
    -Name "R-003_cycle_break_and_reap" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_shutdown_breaks_cycle_and_reaps_child_process -- --nocapture" `
    -BaseFileName "ac8-r003-cycle-break-and-reap" `
    -Summary "R-003: Shutdown breaks cycle and reaps child process"

# 3. R-006 错误呈现
Run-RegressionTest `
    -Name "R-006_error_presentation" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_triggers_restart_and_emits_restarting_status -- --nocapture" `
    -BaseFileName "ac8-r006-error-presentation" `
    -Summary "R-006: Channel restart emits restarting status and error view projection"

# 4. MAX_RETRIES=3
Run-RegressionTest `
    -Name "MAX_RETRIES_3" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_caps_retries_and_emits_fatal_after_three_failures -- --nocapture" `
    -BaseFileName "ac8-max-retries-3" `
    -Summary "MAX_RETRIES=3: Channel caps retries at 3 and emits fatal status"

# 5. is_down 普通写拒绝/关机写放行
Run-RegressionTest `
    -Name "is_down_write_routing" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop shutdown_writes_core_shutdown_to_sidecar_stdin_without_session -- --nocapture" `
    -BaseFileName "ac8-is-down-write-routing" `
    -Summary "is_down routing: Regular writes rejected when down while shutdown writes pass through"

# 6. 既有 resilient 9 项全量套件
Run-RegressionTest `
    -Name "resilient_suite_9_tests" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel" `
    -BaseFileName "ac8-resilient-suite-9-tests" `
    -Summary "Resilient 9 tests suite (startup, restart, max retries, heartbeat, crashloop, shutdown, drop bounded)"

# 7. stdio drop
Run-RegressionTest `
    -Name "stdio_channel_drop" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop stdio_channel_drop_with_unresponsive_session_completes_in_bounded_time -- --nocapture" `
    -BaseFileName "ac8-stdio-channel-drop" `
    -Summary "Stdio channel drop with unresponsive session completes within bound"

# 8. shutdown writes
Run-RegressionTest `
    -Name "shutdown_writes_suite" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop shutdown_writes -- --nocapture" `
    -BaseFileName "ac8-shutdown-writes-suite" `
    -Summary "Shutdown writes send CoreShutdown without session and protocol shutdown with session"

# 9. 2 MB pipe overflow
Run-RegressionTest `
    -Name "pipe_overflow_2mb" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop writer_overflow_pipe_capacity_unblocks_and_cleans_up_on_kill -- --nocapture" `
    -BaseFileName "ac8-pipe-overflow-2mb" `
    -Summary "2 MB pipe capacity overflow unblocks, cleans up on process kill"

# Summary report output
$reportFile = Join-Path $TargetDir "ac8-regression-summary.md"
$sb = New-Object System.Text.StringBuilder
$sb.AppendLine("# AC8 Regression Test Summary") | Out-Null
$sb.AppendLine("") | Out-Null
$sb.AppendLine("| # | Test Name | Command | Exit | Duration (ms) | Status | Summary |") | Out-Null
$sb.AppendLine("|---|---|---|---|---|---|---|") | Out-Null
$idx = 1
$anyFail = $false
foreach ($r in $results) {
    if ($r.ExitCode -ne 0) { $anyFail = $true }
    $sb.AppendLine("| $idx | $($r.Name) | ``$($r.Command)`` | $($r.ExitCode) | $($r.DurationMs) | $($r.Status) | $($r.Summary) |") | Out-Null
    $idx++
}

[System.IO.File]::WriteAllText($reportFile, $sb.ToString(), [System.Text.Encoding]::UTF8)
Write-Host "`nAC8 Regression Summary written to: $reportFile"

if ($anyFail) {
    Write-Host "SOME AC8 REGRESSION TESTS FAILED!" -ForegroundColor Red
    exit 1
} else {
    Write-Host "ALL AC8 REGRESSION TESTS PASSED!" -ForegroundColor Green
    exit 0
}
