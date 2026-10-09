<#
.SYNOPSIS
    P02 Workbench Real WebView2 Verification Runner (Stage A r8).
.DESCRIPTION
    Runs read-only environment identity probe, TypeScript protocol check,
    static frontend control probe, Stage A preflight verification harness,
    and two-phase evidence hash finalization. Adheres strictly to the
    Hard Build Barrier: does not invoke Cargo or Tauri build in this worktree.
.PARAMETER ProbeOnly
    If specified, runs only the read-only environment, TypeScript contract,
    and static contract probes, logging output to probe-execution-probeonly.log.
.PARAMETER FinalizeFailTest
    If specified, passes --finalize-fail-test to verify finalizer failure handling (R5-02).
.PARAMETER ExceptionTest
    If specified, injects a synthetic unhandled exception to verify catch block handling (R6-04).
#>

param(
    [switch]$ProbeOnly,
    [switch]$FinalizeFailTest,
    [switch]$ExceptionTest
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..\..")

# Distinct log path per mode (ProbeOnly and Full Stage A do not overwrite each other)
$LogFile = if ($ProbeOnly) { "probe-execution-probeonly.log" } else { "probe-execution-full.log" }
$LogPath = Join-Path $ScriptDir $LogFile
$LegacyLogPath = Join-Path $ScriptDir "probe-execution.log"

$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$LogBuffer = [System.Collections.Generic.List[string]]::new()
$Global:LogsFlushed = $false
$Global:CurrentStepName = "Startup"
$Global:CurrentCommand = ""
$Global:CurrentArguments = @()
$Global:CurrentStepOutput = $null
$Global:CurrentStepExitCode = $null
$Global:NativeCommandActive = $false

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

# R4-10: Immediately write run header and flush to disk so stale EXIT=0 logs are truncated
Append-Log "=========================================================="
Append-Log "P02 Probe Execution Log"
Append-Log "Date: $(Get-Date -Format "yyyy-MM-ddTHH:mm:ssK")"
Append-Log "PowerShell: $($PSVersionTable.PSVersion)"
Append-Log "Worktree: $RepoRoot"
Append-Log "Mode: $(if ($ProbeOnly) { 'ProbeOnly' } else { 'Full Stage A' })"
Append-Log "LogFile: $LogFile"
Append-Log "Status: IN_PROGRESS"
Append-Log "=========================================================="
Flush-Log

function Execute-Step {
    param(
        [string]$StepName,
        [string]$Command,
        [string[]]$Arguments
    )

    $Global:CurrentStepName = $StepName
    $Global:CurrentCommand = $Command
    $Global:CurrentArguments = $Arguments
    $Global:CurrentStepOutput = $null
    $Global:CurrentStepExitCode = $null
    $Global:NativeCommandActive = $true

    Write-Host "`n[$StepName] Executing: $Command $($Arguments -join ' ')..." -ForegroundColor Yellow
    Append-Log "`n--- [$StepName] ---"
    Append-Log "Command: $Command $($Arguments -join ' ')"

    $output = try {
        $prevEap = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        & $Command @Arguments 2>&1
    } finally {
        $ErrorActionPreference = $prevEap
        $Global:NativeCommandActive = $false
    }

    $exitCode = $LASTEXITCODE
    $Global:CurrentStepExitCode = $exitCode

    $outStr = ($output | Out-String).Trim()
    $Global:CurrentStepOutput = $outStr

    if ($outStr) {
        Write-Host $outStr
        Append-Log "OUTPUT:`n$outStr"
    } else {
        Append-Log "OUTPUT: [NO_OUTPUT]"
    }

    Append-Log "EXIT: $exitCode"

    if ($exitCode -ne 0) {
        Append-Log "`n[FAILURE] [$StepName] Failed with exit code $exitCode"
        Append-Log "Status: FAILED (EXIT=$exitCode)"
        Flush-Log
        $Global:LogsFlushed = $true
        Write-Host "[$StepName] Failed with exit code $exitCode" -ForegroundColor Red
        exit $exitCode
    }
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " P02 Real Workbench WebView2 Verification Harness (Stage A r8)" -ForegroundColor Cyan
Write-Host " Worktree: $RepoRoot" -ForegroundColor Cyan
Write-Host " Mode: $(if ($ProbeOnly) { 'ProbeOnly' } else { 'Full Stage A' })" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

try {
    # R6-04: Injected unhandled exception test for Scenario C microprobe verification
    if ($ExceptionTest) {
        $Global:CurrentStepName = "Injected Exception Test"
        $Global:CurrentCommand = "throw-synthetic-exception"
        $Global:CurrentArguments = @("--force-unhandled")
        throw [System.InvalidOperationException]::new("Injected unhandled exception for Scenario C microprobe verification")
    }

    $PythonExe = (Get-Command python).Source
    $NodeVer = try { (node -v) } catch { "UNAVAILABLE" }
    $NpmVer = try { (npm.cmd -v) } catch { "UNAVAILABLE" }

    Append-Log "Python: $PythonExe ($(& $PythonExe --version))"
    Append-Log "Node: $NodeVer"
    Append-Log "npm: $NpmVer"

    # 1. Environment & Identity Probe
    $EnvProbe = Join-Path $ScriptDir "probes\env_identity_probe.py"
    Execute-Step "Step 1: Environment Identity Probe" $PythonExe @($EnvProbe)

    # 2. TypeScript E2E Protocol Contract Check (R4-01, R5-04, R6-01)
    # Dynamically resolve tsc binary from current worktree or git common dir root
    $TscCandidate1 = Join-Path $RepoRoot "apps\desktop\frontend\node_modules\typescript\bin\tsc"
    $TscPath = if (Test-Path $TscCandidate1) {
        $TscCandidate1
    } else {
        # R6-01: Explicitly pass -C $RepoRoot so git resolves common dir independent of caller CWD
        $GitCommonDir = try { (git -C $RepoRoot rev-parse --git-common-dir 2>$null).Trim() } catch { "" }
        if ($GitCommonDir) {
            $CommonRoot = if ([System.IO.Path]::IsPathRooted($GitCommonDir)) {
                Split-Path -Parent $GitCommonDir
            } else {
                Split-Path -Parent (Resolve-Path (Join-Path $RepoRoot $GitCommonDir))
            }
            $Cand = Join-Path $CommonRoot "apps\desktop\frontend\node_modules\typescript\bin\tsc"
            if (Test-Path $Cand) { $Cand } else { $null }
        } else {
            $null
        }
    }

    if (-not $TscPath -or -not (Test-Path $TscPath)) {
        $Global:CurrentStepName = "Step 2: TypeScript Protocol Check"
        $Global:CurrentCommand = "tsc"
        $Global:CurrentArguments = @()
        $Global:CurrentStepExitCode = 1
        Append-Log "`n--- [Step 2: TypeScript Protocol Check] ---"
        Append-Log "[FAILURE] TypeScript compiler (tsc) not found in worktree ($RepoRoot) or git common root (fail-closed per R5-04)."
        Append-Log "EXIT: 1"
        Append-Log "`n[FAILURE] [Step 2: TypeScript Protocol Check] Failed with exit code 1"
        Append-Log "Status: FAILED (EXIT=1)"
        Flush-Log
        $Global:LogsFlushed = $true
        Write-Host "[Step 2: TypeScript Protocol Check] FAILED: tsc binary not found (fail-closed per R5-04)" -ForegroundColor Red
        exit 1
    }

    $E2eProtocolTs = Join-Path $RepoRoot "apps\desktop\frontend\e2e\workbench_driver_protocol.ts"
    Execute-Step "Step 2: TypeScript Protocol Check" "node" @(
        $TscPath,
        "--noEmit",
        "--strict",
        "--skipLibCheck",
        "--target", "ES2021",
        "--lib", "ES2021,DOM",
        $E2eProtocolTs
    )
    $TscExitCode = $Global:CurrentStepExitCode

    # 3. Static Source Contract Control Probe
    $StaticProbe = Join-Path $ScriptDir "probes\static_control_probe.py"
    Execute-Step "Step 3: Static Source Contract Probe" $PythonExe @($StaticProbe)

    if ($ProbeOnly) {
        Write-Host "`nProbeOnly specified; Stage A preflight probes complete (EXIT=0)." -ForegroundColor Green
        Append-Log "`nProbeOnly execution completed successfully with EXIT=0."
        Append-Log "Status: COMPLETED (EXIT=0)"
        Flush-Log
        $Global:LogsFlushed = $true
        exit 0
    }

    # 4. Stage A Harness & Verdict Generator (R6-02: pass observed tsc exit code)
    $HarnessPy = Join-Path $ScriptDir "harness\workbench_cdp_harness.py"
    $HarnessArgs = @($HarnessPy, "--tsc-exit", "$TscExitCode")
    Execute-Step "Step 4: Stage A Verdict Harness" $PythonExe $HarnessArgs

    Write-Host "`n==========================================================" -ForegroundColor Green
    Write-Host " P02 Stage A Preflight & Verdict Complete (EXIT=0)" -ForegroundColor Green
    Write-Host "==========================================================" -ForegroundColor Green

    # 5. Two-Phase Artifact Hash Finalization (R4-03, R5-02)
    $Global:CurrentStepName = "Step 5: Finalize Evidence Hashes"
    $Global:CurrentCommand = $PythonExe
    $FinArgs = if ($FinalizeFailTest) { @($HarnessPy, "--finalize", "--finalize-fail-test") } else { @($HarnessPy, "--finalize") }
    $Global:CurrentArguments = $FinArgs
    $Global:CurrentStepOutput = $null
    $Global:CurrentStepExitCode = $null
    $Global:NativeCommandActive = $true

    Append-Log "`n--- [Step 5: Finalize Evidence Hashes] ---"
    Append-Log "Command: $PythonExe $($FinArgs -join ' ')"
    Flush-Log
    $Global:LogsFlushed = $true

    Write-Host "`n[Step 5: Finalize Evidence Hashes] Executing: $PythonExe $($FinArgs -join ' ')..." -ForegroundColor Yellow

    $finOutput = try {
        $prevEap = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        & $PythonExe @FinArgs 2>&1
    } finally {
        $ErrorActionPreference = $prevEap
        $Global:NativeCommandActive = $false
    }

    $finExit = $LASTEXITCODE
    $Global:CurrentStepExitCode = $finExit
    $finStr = ($finOutput | Out-String).Trim()
    $Global:CurrentStepOutput = $finStr
    if ($finStr) {
        Write-Host $finStr
    }

    if ($finExit -ne 0) {
        # R5-02: Finalizer failed! Append failure verdict and overwrite status so failed runs NEVER claim success.
        Append-Log "`n[FAILURE] [Step 5: Finalize Evidence Hashes] Finalizer failed with exit code $finExit"
        if ($finStr) {
            Append-Log "OUTPUT:`n$finStr"
        }
        Append-Log "Status: FAILED (EXIT=$finExit)"
        Flush-Log
        Write-Host "Evidence finalization failed with exit code $finExit" -ForegroundColor Red
        exit $finExit
    }

    Write-Host "`n==========================================================" -ForegroundColor Green
    Write-Host " P02 Stage A Full Execution Complete (EXIT=0)" -ForegroundColor Green
    Write-Host "==========================================================" -ForegroundColor Green
    exit 0
}
catch {
    # R4-06, R5-03: Persist exact failed step, command, arguments, captured process output, and stack trace
    $errRecord = $_
    $ex = $errRecord.Exception
    Append-Log "`n[UNHANDLED_EXCEPTION]"
    Append-Log "Failed Step: $Global:CurrentStepName"
    Append-Log "Failed Command: $Global:CurrentCommand $($Global:CurrentArguments -join ' ')"
    Append-Log "Exception Type: $($ex.GetType().FullName)"
    Append-Log "Exception Message: $($ex.Message)"

    # R5-03: Capture and persist process output (or record UNAVAILABLE)
    $capturedOut = if ($Global:CurrentStepOutput) {
        $Global:CurrentStepOutput
    } elseif ($errRecord.ErrorDetails -and $errRecord.ErrorDetails.Message) {
        $errRecord.ErrorDetails.Message
    } else {
        "UNAVAILABLE (exception occurred before process output stream could be captured)"
    }
    Append-Log "Captured Process Output:`n$capturedOut"

    # R5-03: Persist full stack trace
    $stackTrace = if ($ex.StackTrace) {
        $ex.StackTrace
    } elseif ($errRecord.ScriptStackTrace) {
        $errRecord.ScriptStackTrace
    } else {
        "UNAVAILABLE"
    }
    Append-Log "Stack Trace:`n$stackTrace"

    # R5-03: Explicit child exit code (never reuse stale $LASTEXITCODE from previous command)
    if ($Global:CurrentStepExitCode -ne $null) {
        Append-Log "Observed Child ExitCode: $Global:CurrentStepExitCode"
    } elseif ($Global:NativeCommandActive -and $LASTEXITCODE -ne $null) {
        Append-Log "Observed Child ExitCode: $LASTEXITCODE"
    } else {
        Append-Log "Observed Child ExitCode: null (exception aborted execution before exit code could be observed)"
    }

    Append-Log "Status: FAILED"
    Flush-Log
    $Global:LogsFlushed = $true
    Write-Host "Unhandled exception in [$Global:CurrentStepName]: $($ex.Message)" -ForegroundColor Red
    exit 1
}
finally {
    if (-not $Global:LogsFlushed) {
        Flush-Log
    }
}
