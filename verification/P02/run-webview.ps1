<#
.SYNOPSIS
    P02 Workbench Real WebView2 Verification Runner (Stage A r5).
.DESCRIPTION
    Runs read-only environment identity probe, TypeScript protocol check,
    static frontend control probe, Stage A preflight verification harness,
    and two-phase evidence hash finalization. Adheres strictly to the
    Hard Build Barrier: does not invoke Cargo or Tauri build in this worktree.
.PARAMETER ProbeOnly
    If specified, runs only the read-only environment, TypeScript contract,
    and static contract probes, logging output to probe-execution-probeonly.log.
#>

param(
    [switch]$ProbeOnly
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
        $Global:LogsFlushed = $true
        Write-Host "[$StepName] Failed with exit code $exitCode" -ForegroundColor Red
        exit $exitCode
    }
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " P02 Real Workbench WebView2 Verification Harness (Stage A r5)" -ForegroundColor Cyan
Write-Host " Worktree: $RepoRoot" -ForegroundColor Cyan
Write-Host " Mode: $(if ($ProbeOnly) { 'ProbeOnly' } else { 'Full Stage A' })" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

try {
    $PythonExe = (Get-Command python).Source
    $NodeVer = try { (node -v) } catch { "UNAVAILABLE" }
    $NpmVer = try { (npm.cmd -v) } catch { "UNAVAILABLE" }

    Append-Log "Python: $PythonExe ($(& $PythonExe --version))"
    Append-Log "Node: $NodeVer"
    Append-Log "npm: $NpmVer"

    # 1. Environment & Identity Probe
    $EnvProbe = Join-Path $ScriptDir "probes\env_identity_probe.py"
    Execute-Step "Step 1: Environment Identity Probe" $PythonExe @($EnvProbe)

    # 2. TypeScript E2E Protocol Contract Check (R4-01)
    $TscCandidate1 = Join-Path $RepoRoot "apps\desktop\frontend\node_modules\typescript\bin\tsc"
    $TscCandidate2 = "G:\CODEX\New Manga\apps\desktop\frontend\node_modules\typescript\bin\tsc"
    $TscPath = if (Test-Path $TscCandidate1) { $TscCandidate1 } else { $TscCandidate2 }

    if (Test-Path $TscPath) {
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
    } else {
        Write-Host "`n[Step 2: TypeScript Protocol Check] Warning: tsc binary not found at $TscPath" -ForegroundColor Yellow
        Append-Log "`n[Step 2: TypeScript Protocol Check] Warning: tsc binary not found at $TscPath"
    }

    # 3. Static Source Contract Control Probe
    $StaticProbe = Join-Path $ScriptDir "probes\static_control_probe.py"
    Execute-Step "Step 3: Static Source Contract Probe" $PythonExe @($StaticProbe)

    if ($ProbeOnly) {
        Write-Host "`nProbeOnly specified; Stage A preflight probes complete (EXIT=0)." -ForegroundColor Green
        Append-Log "`nProbeOnly execution completed successfully with EXIT=0."
        Flush-Log
        $Global:LogsFlushed = $true
        exit 0
    }

    # 4. Stage A Harness & Verdict Generator
    $HarnessPy = Join-Path $ScriptDir "harness\workbench_cdp_harness.py"
    Execute-Step "Step 4: Stage A Verdict Harness" $PythonExe @($HarnessPy)

    Write-Host "`n==========================================================" -ForegroundColor Green
    Write-Host " P02 Stage A Full Execution Complete (EXIT=0)" -ForegroundColor Green
    Write-Host "==========================================================" -ForegroundColor Green

    Append-Log "`nFull Stage A execution completed successfully with EXIT=0."

    # R4-03: Finalize runner log on disk BEFORE computing final evidence artifact hashes
    Flush-Log
    $Global:LogsFlushed = $true

    # 5. Two-Phase Artifact Hash Finalization (R4-03)
    Write-Host "`n[Step 5: Finalize Evidence Hashes] Executing: $PythonExe $HarnessPy --finalize..." -ForegroundColor Yellow
    $finOutput = & $PythonExe $HarnessPy --finalize 2>&1
    $finExit = $LASTEXITCODE
    $finStr = ($finOutput | Out-String).Trim()
    if ($finStr) {
        Write-Host $finStr
    }
    if ($finExit -ne 0) {
        Write-Host "Evidence finalization failed with exit code $finExit" -ForegroundColor Red
        exit $finExit
    }

    exit 0
}
catch {
    # R4-06: Persist exact failed step, command, arguments, and exception stack trace
    Append-Log "`n[UNHANDLED_EXCEPTION]"
    Append-Log "Failed Step: $Global:CurrentStepName"
    Append-Log "Failed Command: $Global:CurrentCommand $($Global:CurrentArguments -join ' ')"
    Append-Log "Exception Message: $($_.Exception.Message)"
    Append-Log "Exception Type: $($_.Exception.GetType().FullName)"
    if ($LASTEXITCODE -ne $null) {
        Append-Log "LastExitCode: $LASTEXITCODE"
    }
    Flush-Log
    $Global:LogsFlushed = $true
    Write-Host "Unhandled exception in [$Global:CurrentStepName]: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
finally {
    if (-not $Global:LogsFlushed) {
        Flush-Log
    }
}
