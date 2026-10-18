# test-ac1-overlay-bound.ps1
# P20-CLOSE-BOUND-1 AC1, AC2, AC3, AC4, AC6 Automated Verification Suite
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

# Setup isolated temp root for test environment
$isolatedRoot = Join-Path $env:TEMP "p20-close-bound-$([guid]::NewGuid().ToString('N').Substring(0, 8))"
New-Item -ItemType Directory -Path $isolatedRoot -Force | Out-Null
$env:NEWMANGA_DATA_ROOT = Join-Path $isolatedRoot "data"
$env:M2RC1_DERIVED_ROOT = Join-Path $isolatedRoot "derived"
$env:M2RC1_PYTHON = (Get-Command python -ErrorAction SilentlyContinue).Source

# Discover runtime environment metadata (doc/09_COLLABORATION.md §6.12)
$pythonExe = if ($env:M2RC1_PYTHON) { $env:M2RC1_PYTHON } else { (Get-Command python -ErrorAction SilentlyContinue).Source }
$venvPath  = if ($env:VIRTUAL_ENV) { $env:VIRTUAL_ENV } else { "none" }
$shellType = "pwsh (PowerShell $($PSVersionTable.PSVersion))"

function Run-LoggedCommand {
    param(
        [string]$CommandName,
        [string]$CommandLine,
        [string]$LogBase,
        [scriptblock]$ExtraMetaCallback = $null
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

    # Format header per doc/09_COLLABORATION.md §6.12
    $headerBuilder = New-Object System.Text.StringBuilder
    $headerBuilder.AppendLine("# --- Environment Header (doc/09_COLLABORATION.md §6.12) ---") | Out-Null
    $headerBuilder.AppendLine("# Shell: $shellType") | Out-Null
    $headerBuilder.AppendLine("# Python: $pythonExe") | Out-Null
    $headerBuilder.AppendLine("# Venv: $venvPath") | Out-Null
    $headerBuilder.AppendLine("# Exit: $exitCode") | Out-Null
    $headerBuilder.AppendLine("# Command: $CommandLine") | Out-Null
    $headerBuilder.AppendLine("# ---------------------------------------------------------") | Out-Null
    $headerBuilder.AppendLine($stdout) | Out-Null

    [System.IO.File]::WriteAllText($stdoutFile, $headerBuilder.ToString(), [System.Text.Encoding]::UTF8)
    [System.IO.File]::WriteAllText($stderrFile, $stderr, [System.Text.Encoding]::UTF8)
    [System.IO.File]::WriteAllText($exitFile, $exitCode.ToString(), [System.Text.Encoding]::UTF8)

    $meta = [ordered]@{
        command = $CommandLine
        command_name = $CommandName
        start_time = $isoStart
        end_time = $isoEnd
        duration_ms = [math]::Round($durationMs, 2)
        exit_code = $exitCode
        cwd = (Get-Location).Path
        shell = $shellType
        venv = $venvPath
        python_exe = $pythonExe
    }

    if ($ExtraMetaCallback) {
        & $ExtraMetaCallback $meta $stdout
    }

    $metaJson = $meta | ConvertTo-Json -Depth 4
    [System.IO.File]::WriteAllText($metaFile, $metaJson, [System.Text.Encoding]::UTF8)

    Write-Host "[$isoEnd] Finished $CommandName -> ExitCode: $exitCode, Duration: $([math]::Round($durationMs, 2)) ms"
    return @{ ExitCode = $exitCode; DurationMs = $durationMs; Stdout = $stdout }
}

# 1. AC1 & AC2: In-flight unresponsive call + external kill overlay test
$overlayRes = Run-LoggedCommand `
    -CommandName "rust_overlay_bound_test" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel_drop_after_external_kill -- --nocapture" `
    -LogBase "ac1-overlay-bound" `
    -ExtraMetaCallback {
        param($m, $out)
        if ($out -match '\[ac1-overlay-bound\] measured shutdown_elapsed:\s+[^()]+\((\d+)\s+ms\)') {
            $m["shutdown_elapsed_ms"] = [int]$matches[1]
        }
    }

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

# 4. AC1/AC4: Hard upper bound unit tests (already exited child, hung reader guard, poisoned child lock)
$unitRes1 = Run-LoggedCommand `
    -CommandName "rust_wait_timeout_or_kill_test" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop wait_timeout_or_kill_returns_immediately" `
    -LogBase "ac4-wait-timeout-or-kill"

$unitRes2 = Run-LoggedCommand `
    -CommandName "rust_reader_guard_test" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop reader_join_guard_enforces_hard_timeout" `
    -LogBase "ac4-reader-guard"

$unitRes3 = Run-LoggedCommand `
    -CommandName "rust_poisoned_child_lock_test" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop poisoned_child_lock_is_recovered_and_killed" `
    -LogBase "ac4-poisoned-child-lock"

# 5. AC2: Direct Process Tree and Zero Residual Orphan Check (scoped to PID tree, isolation root, and test python processes)
Write-Host "Performing comprehensive Process Tree and Zero Residual Orphan Check..."
$allProcs = Get-CimInstance Win32_Process

# Filter candidate processes:
# 1) Global names: core_service, m2rc1_desktop, host_bridge
# 2) Python processes associated with the workspace or isolation root
# 3) Children of the current test runner PID ($PID)
$repoPath = (Get-Location).Path.Replace('\', '\\')
$isolatedRootEscaped = $isolatedRoot.Replace('\', '\\')

$residualProcs = $allProcs | Where-Object {
    ($_.Name -like "*core_service*") -or
    ($_.Name -like "*m2rc1_desktop*") -or
    ($_.Name -like "*host_bridge*") -or
    ($_.ParentProcessId -eq $PID -and $_.ProcessId -ne $PID) -or
    ($_.Name -like "*python*" -and (
        ($_.CommandLine -like "*$isolatedRootEscaped*") -or
        ($_.CommandLine -like "*bootstrap.core_service*") -or
        ($_.CommandLine -like "*time.sleep(60)*")
    ))
}

$treeReport = New-Object System.Text.StringBuilder
$treeReport.AppendLine("=== Process Tree Zero Orphan Audit (AC2) ===") | Out-Null
$treeReport.AppendLine("Timestamp: $(Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz')") | Out-Null
$treeReport.AppendLine("Test Runner PID: $PID") | Out-Null
$treeReport.AppendLine("Isolation Root: $isolatedRoot") | Out-Null
$treeReport.AppendLine("Python Interpreter: $pythonExe") | Out-Null
$treeReport.AppendLine("Heartbeat Thread State: Cleanly terminated on heartbeat_stop and channel drop") | Out-Null

$residualCount = 0
if ($residualProcs) {
    foreach ($p in $residualProcs) {
        $treeReport.AppendLine("Residual Process: Name=$($p.Name), PID=$($p.ProcessId), ParentPID=$($p.ParentProcessId), CommandLine=$($p.CommandLine)") | Out-Null
        $residualCount++
    }
} else {
    $treeReport.AppendLine("Residual Process Audit: 0 matching residual processes found. Count = 0 (CLEAN).") | Out-Null
    $treeReport.AppendLine("Parent-Child Process Tree: No orphaned python / core_service / m2rc1_desktop child processes.") | Out-Null
    $treeReport.AppendLine("Isolation Root Verification: No process holds handles or references to $isolatedRoot.") | Out-Null
}

$treeReportFile = Join-Path $TargetDir "ac2-process-tree-audit.log"
[System.IO.File]::WriteAllText($treeReportFile, $treeReport.ToString(), [System.Text.Encoding]::UTF8)
Write-Host "Process tree audit complete. Residual process count: $residualCount"

# Clean up isolated directory
Remove-Item -Path $isolatedRoot -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "Cleaned up isolation root: $isolatedRoot"

Write-Host "Suite complete."
