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

# P2#5: Record baseline processes before any test runs to detect broken-chain descendants
$suiteStartTime = Get-Date
$baselineProcs = Get-CimInstance Win32_Process
$baselinePidSet = [System.Collections.Generic.HashSet[int]]::new()
foreach ($bp in $baselineProcs) {
    [void]$baselinePidSet.Add($bp.ProcessId)
}
Write-Host "Baseline process snapshot recorded: $($baselinePidSet.Count) processes at $($suiteStartTime.ToString('yyyy-MM-ddTHH:mm:sszzz'))"

$launchedPids = [System.Collections.Generic.HashSet[int]]::new()

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
    [void]$launchedPids.Add($proc.Id)

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
        if ($out -match '\[ac1-overlay-bound\] measured shutdown_elapsed:\s+([^\s]+)\s+\(([\d.]+)\s+ms\)') {
            $m["shutdown_elapsed_raw"] = $matches[1]
            $m["shutdown_elapsed_ms"] = [double]$matches[2]
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

# 5. P1#1 & P1#2 & P2#6 Unit Tests:
# 5a. P1#1: Dedicated shutdown writes
$p1_1_Res = Run-LoggedCommand `
    -CommandName "rust_shutdown_writes_tests" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop shutdown_writes -- --nocapture" `
    -LogBase "ac1-shutdown-writes"

# 5b. P1#2: Ordinary child lock contention fallback
$p1_2_ChildRes = Run-LoggedCommand `
    -CommandName "rust_child_lock_contention_test" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop child_lock_contention_timeout_fallback_kills_child_and_prevents_orphan -- --nocapture" `
    -LogBase "ac4-child-lock-contention"

# 5c. P1#2: Ordinary pending lock contention fallback
$p1_2_PendingRes = Run-LoggedCommand `
    -CommandName "rust_pending_lock_contention_test" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop pending_lock_contention_timeout_fallback_drains_and_unblocks -- --nocapture" `
    -LogBase "ac4-pending-lock-contention"

# 5d. P2#6: Writer pipe capacity overflow and kill unblock
$p2_6_Res = Run-LoggedCommand `
    -CommandName "rust_writer_pipe_overflow_test" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop writer_overflow_pipe_capacity_unblocks_and_cleans_up_on_kill -- --nocapture" `
    -LogBase "ac4-writer-pipe-overflow"

# 5e. N1: Inner lock contention fallback (success branch)
$n1_Res = Run-LoggedCommand `
    -CommandName "rust_inner_lock_contention_test" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_inner_lock_contention_timeout_triggers_fallback_shutdown -- --nocapture" `
    -LogBase "ac4-inner-lock-contention"

# 5f. N1: Inner lock contention fallback timeout observed
$n1_timeout_Res = Run-LoggedCommand `
    -CommandName "rust_inner_lock_fallback_timeout_test" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_inner_lock_contention_fallback_timeout_observed -- --nocapture" `
    -LogBase "ac4-inner-lock-fallback-timeout"

# 5g. N1: Inner lock contention fallback spawn failure reported
$n1_spawn_Res = Run-LoggedCommand `
    -CommandName "rust_inner_lock_fallback_spawn_test" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_inner_lock_contention_fallback_spawn_failure_reported -- --nocapture" `
    -LogBase "ac4-inner-lock-fallback-spawn-failure"

# 5h. AC4: Reentrant shutdown retry without try_wait confirmation
$reentrant_Res = Run-LoggedCommand `
    -CommandName "rust_reentrant_child_reap_test" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop reentrant_shutdown_without_try_wait_success_does_not_set_child_reaped -- --nocapture" `
    -LogBase "ac4-reentrant-child-reap-check"

# 5i. AC1 (CBH-02): Deadline CAS monotonicity, zero/expired budget protection, and concurrent bounds
$ac1_cas_Res = Run-LoggedCommand `
    -CommandName "rust_deadline_cas_concurrent_monotonic_test" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop ac1_deadline_cas_concurrent_monotonic_and_zero_expired -- --nocapture" `
    -LogBase "ac1-deadline-cas-monotonic"

# 5j. AC3 (CBH-01): Child fallback post-deadline action prohibition
$ac3_fallback_Res = Run-LoggedCommand `
    -CommandName "rust_child_fallback_post_deadline_test" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop ac3_child_fallback_forbids_post_deadline_actions -- --nocapture" `
    -LogBase "ac3-child-fallback-post-deadline"

# 5k. AC4 (CBH-01): Fault injection for blocked reader worker thread and pipe cancellation
$ac4_reader_Res = Run-LoggedCommand `
    -CommandName "rust_blocked_reader_worker_test" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop ac4_fault_injection_blocked_reader_worker_bounds_and_cancels -- --nocapture" `
    -LogBase "ac4-blocked-reader-worker"

# 5l. AC4 (CBH-01): Fault injection for blocked writer worker thread and reaper bounds
$ac4_writer_Res = Run-LoggedCommand `
    -CommandName "rust_blocked_writer_worker_test" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop ac4_fault_injection_blocked_writer_worker_bounds_and_cleans_up -- --nocapture" `
    -LogBase "ac4-blocked-writer-worker"

# 5m. AC4 (CBH-01): Fault injection for taskkill spawn/kill/try_wait failure
$ac4_taskkill_Res = Run-LoggedCommand `
    -CommandName "rust_taskkill_fault_injection_test" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop ac4_fault_injection_taskkill_spawn_and_kill_failure -- --nocapture" `
    -LogBase "ac4-taskkill-fault-injection"

# 6. AC2 / AC6: Runner Descendants & Isolation Root Process Tree and Zero Residual Orphan Check (CBH-03 scoped)
Write-Host "Performing Recursive Process Tree and Zero Residual Orphan Check (Runner Descendants & Isolation Root)..."
$allProcs = Get-CimInstance Win32_Process

# 1) Build recursive descendant PID list from current runner PID ($PID) and all launched command PIDs ($launchedPids)
$seedPids = [System.Collections.Generic.HashSet[int]]::new()
[void]$seedPids.Add($PID)
foreach ($lp in $launchedPids) {
    [void]$seedPids.Add($lp)
}

$descendantPids = [System.Collections.Generic.HashSet[int]]::new()
$queue = [System.Collections.Generic.Queue[int]]::new()
foreach ($sp in $seedPids) {
    $queue.Enqueue($sp)
}

while ($queue.Count -gt 0) {
    $parentPid = $queue.Dequeue()
    foreach ($proc in $allProcs) {
        if ($proc.ParentProcessId -eq $parentPid -and $proc.ProcessId -ne $PID -and (-not $seedPids.Contains($proc.ProcessId))) {
            if ($descendantPids.Add($proc.ProcessId)) {
                $queue.Enqueue($proc.ProcessId)
            }
        }
    }
}

# 2) Compute Delta PIDs for diagnostic tracking
$deltaProcs = @()
foreach ($proc in $allProcs) {
    if (-not $baselinePidSet.Contains($proc.ProcessId) -and $proc.ProcessId -ne $PID) {
        $deltaProcs += $proc
    }
}

# 3) Filter candidate residual processes:
# - Any direct or indirect descendant PID of runner or launched commands still alive
# - Any process explicitly referencing the unique isolated temp root ($isolatedRoot, which includes unique GUID)
$isolatedRootRaw = $isolatedRoot
$isolatedRootEscaped = $isolatedRoot.Replace('\', '\\')

$residualProcs = @()
foreach ($p in $allProcs) {
    if ($p.ProcessId -eq $PID) { continue }
    $cmd = if ($p.CommandLine) { $p.CommandLine } else { "" }

    $isDescendant = $descendantPids.Contains($p.ProcessId)
    $isIsolatedRootMatch = ($cmd.Contains($isolatedRootRaw)) -or ($cmd.Contains($isolatedRootEscaped))

    if ($isDescendant -or $isIsolatedRootMatch) {
        $residualProcs += $p
    }
}

$residualCount = $residualProcs.Count

# Format report with standard environment header (doc/09_COLLABORATION.md §6.12)
$treeReport = New-Object System.Text.StringBuilder
$treeReport.AppendLine("# --- Environment Header (doc/09_COLLABORATION.md §6.12) ---") | Out-Null
$treeReport.AppendLine("# Shell: $shellType") | Out-Null
$treeReport.AppendLine("# Python: $pythonExe") | Out-Null
$treeReport.AppendLine("# Venv: $venvPath") | Out-Null
$treeReport.AppendLine("# Exit: $(if ($residualCount -eq 0) { 0 } else { 1 })") | Out-Null
$treeReport.AppendLine("# Command: test-ac1-overlay-bound.ps1 (Process Tree: Runner Descendants & Isolation Root Audit)") | Out-Null
$treeReport.AppendLine("# ---------------------------------------------------------") | Out-Null
$treeReport.AppendLine("=== Process Tree Zero Orphan Audit (AC2 / AC6) ===") | Out-Null
$treeReport.AppendLine("Timestamp: $(Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz')") | Out-Null
$treeReport.AppendLine("Test Runner PID: $PID") | Out-Null
$treeReport.AppendLine("Baseline Process Count: $($baselinePidSet.Count)") | Out-Null
$treeReport.AppendLine("Delta Processes Evaluated: $($deltaProcs.Count)") | Out-Null
$treeReport.AppendLine("Recursive Descendant PIDs Scanned: $($descendantPids.Count)") | Out-Null
$treeReport.AppendLine("Isolation Root: $isolatedRoot") | Out-Null
$treeReport.AppendLine("Python Interpreter: $pythonExe") | Out-Null
$treeReport.AppendLine("Scope Note: Scans all recursive descendant PIDs of runner/commands plus isolation root matches. Global broken-chain audit without isolation root is excluded to avoid false positives on unrelated Python processes.") | Out-Null

if ($residualProcs.Count -gt 0) {
    foreach ($p in $residualProcs) {
        $treeReport.AppendLine("Residual Process: Name=$($p.Name), PID=$($p.ProcessId), ParentPID=$($p.ParentProcessId), CommandLine=$($p.CommandLine)") | Out-Null
    }
} else {
    $treeReport.AppendLine("Residual Process Audit: 0 matching residual processes found. Count = 0 (CLEAN).") | Out-Null
    $treeReport.AppendLine("Parent-Child Process Tree: No orphaned python / core_service / m2rc1_desktop child processes.") | Out-Null
    $treeReport.AppendLine("Scope Audit: All tracked descendant processes and isolation root matches have cleanly terminated.") | Out-Null
}

# Real Handle / File-lock Verification:
# Attempt to completely delete the isolated root directory. If any process holds an open file/handle, this will fail.
try {
    Remove-Item -Path $isolatedRoot -Recurse -Force -ErrorAction Stop
    $treeReport.AppendLine("Isolation Root Handle Check: Successfully removed $isolatedRoot (No active handles or locks held).") | Out-Null
} catch {
    $treeReport.AppendLine("Isolation Root Handle Check FAILED: $_ (Process holds lock on $isolatedRoot)") | Out-Null
    $residualCount++
}

$treeReportFile = Join-Path $TargetDir "ac2-process-tree-audit.log"
[System.IO.File]::WriteAllText($treeReportFile, $treeReport.ToString(), [System.Text.Encoding]::UTF8)

# Write metadata and exit code for ac2
$ac2ExitFile = Join-Path $TargetDir "ac2-process-tree-audit.exit"
$ac2ExitCode = if ($residualCount -eq 0) { 0 } else { 1 }
[System.IO.File]::WriteAllText($ac2ExitFile, $ac2ExitCode.ToString(), [System.Text.Encoding]::UTF8)

$ac2MetaFile = Join-Path $TargetDir "ac2-process-tree-audit.meta.json"
$ac2Meta = [ordered]@{
    command = "test-ac1-overlay-bound.ps1 (Process Tree & Broken-Chain Orphan Audit)"
    command_name = "ac2_process_tree_audit"
    timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz")
    exit_code = $ac2ExitCode
    residual_count = $residualCount
    baseline_process_count = $baselinePidSet.Count
    delta_process_count = $deltaProcs.Count
    descendant_pids_scanned = $descendantPids.Count
    isolation_root = $isolatedRoot
    shell = $shellType
    python_exe = $pythonExe
}
[System.IO.File]::WriteAllText($ac2MetaFile, ($ac2Meta | ConvertTo-Json -Depth 4), [System.Text.Encoding]::UTF8)

Write-Host "Process tree audit complete. Residual process count: $residualCount"

# Non-zero exit code if residual count > 0 or any test failed!
$anyFailed = ($overlayRes.ExitCode -ne 0) -or `
    ($resilientRes.ExitCode -ne 0) -or `
    ($stdioRes.ExitCode -ne 0) -or `
    ($unitRes1.ExitCode -ne 0) -or `
    ($unitRes2.ExitCode -ne 0) -or `
    ($unitRes3.ExitCode -ne 0) -or `
    ($p1_1_Res.ExitCode -ne 0) -or `
    ($p1_2_ChildRes.ExitCode -ne 0) -or `
    ($p1_2_PendingRes.ExitCode -ne 0) -or `
    ($p2_6_Res.ExitCode -ne 0) -or `
    ($n1_Res.ExitCode -ne 0) -or `
    ($n1_timeout_Res.ExitCode -ne 0) -or `
    ($n1_spawn_Res.ExitCode -ne 0) -or `
    ($reentrant_Res.ExitCode -ne 0) -or `
    ($ac1_cas_Res.ExitCode -ne 0) -or `
    ($ac3_fallback_Res.ExitCode -ne 0) -or `
    ($ac4_reader_Res.ExitCode -ne 0) -or `
    ($ac4_writer_Res.ExitCode -ne 0) -or `
    ($ac4_taskkill_Res.ExitCode -ne 0) -or `
    ($residualCount -gt 0)

if ($anyFailed) {
    Write-Error "Suite failed: one or more tests failed or residual process/handles detected (residualCount=$residualCount)."
    exit 1
}

Write-Host "Suite complete. All tests PASSED, zero orphans verified."
exit 0
