# verify-p1-1.ps1
# P20-CLOSE-BOUND-1 P1#1 Regression Fix Verification Suite
# Owner: Antigravity

$ErrorActionPreference = "Continue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "../../..")
Set-Location $RepoRoot

$Timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"
Write-Host "[$Timestamp] Starting P1#1 regression fix verification..."

# Setup isolated temp root for test environment
$isolatedRoot = Join-Path $env:TEMP "p20-p1-1-fix-$([guid]::NewGuid().ToString('N').Substring(0, 8))"
New-Item -ItemType Directory -Path $isolatedRoot -Force | Out-Null
$env:NEWMANGA_DATA_ROOT = Join-Path $isolatedRoot "data"
$env:M2RC1_DERIVED_ROOT = Join-Path $isolatedRoot "derived"
$env:M2RC1_PYTHON = (Get-Command python -ErrorAction SilentlyContinue).Source

$pythonExe = if ($env:M2RC1_PYTHON) { $env:M2RC1_PYTHON } else { (Get-Command python -ErrorAction SilentlyContinue).Source }
$venvPath  = if ($env:VIRTUAL_ENV) { $env:VIRTUAL_ENV } else { "none" }
$shellType = "pwsh (PowerShell $($PSVersionTable.PSVersion))"

function Run-LoggedCommand {
    param(
        [string]$CommandName,
        [string]$CommandLine,
        [string]$LogBase
    )
    $startTime = Get-Date
    $isoStart = $startTime.ToString("yyyy-MM-ddTHH:mm:sszzz")
    Write-Host "[$isoStart] Executing: $CommandLine"

    $stdoutFile = Join-Path $ScriptDir "$LogBase.stdout.log"
    $stderrFile = Join-Path $ScriptDir "$LogBase.stderr.log"
    $exitFile   = Join-Path $ScriptDir "$LogBase.exit"
    $metaFile   = Join-Path $ScriptDir "$LogBase.meta.json"

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

    # Header per doc/09_COLLABORATION.md §6.12
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

    $metaJson = $meta | ConvertTo-Json -Depth 4
    [System.IO.File]::WriteAllText($metaFile, $metaJson, [System.Text.Encoding]::UTF8)

    Write-Host "[$isoEnd] Finished $CommandName -> ExitCode: $exitCode, Duration: $([math]::Round($durationMs, 2)) ms"
    return @{ ExitCode = $exitCode; DurationMs = $durationMs; Stdout = $stdout }
}

# 1. P1#1: Dedicated shutdown write tests (with session and without session)
$t1 = Run-LoggedCommand `
    -CommandName "shutdown_writes_tests" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop shutdown_writes -- --nocapture" `
    -LogBase "p1-1-shutdown-writes"

# 2. Resilient channel regression suite (9 tests)
$t2 = Run-LoggedCommand `
    -CommandName "resilient_channel_suite" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop resilient_channel -- --nocapture" `
    -LogBase "p1-1-resilient-channel"

# 3. Stdio channel drop regression test
$t3 = Run-LoggedCommand `
    -CommandName "stdio_channel_drop_test" `
    -CommandLine "cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop stdio_channel_drop -- --nocapture" `
    -LogBase "p1-1-stdio-drop"

# 4. Governance check
$t4 = Run-LoggedCommand `
    -CommandName "governance_check" `
    -CommandLine "pwsh -NoProfile -File tools/governance/check.ps1" `
    -LogBase "p1-1-governance"

# Clean up temp isolated dir
try {
    Remove-Item -Path $isolatedRoot -Recurse -Force -ErrorAction SilentlyContinue
} catch {}

# Final summary verdict
$allPassed = ($t1.ExitCode -eq 0) -and ($t2.ExitCode -eq 0) -and ($t3.ExitCode -eq 0) -and ($t4.ExitCode -eq 0)
Write-Host "========================================="
Write-Host "P1#1 Verification Suite Final Verdict: $(if ($allPassed) { 'ALL PASSED' } else { 'FAILED' })"
Write-Host "========================================="
if (-not $allPassed) {
    exit 1
}
exit 0
