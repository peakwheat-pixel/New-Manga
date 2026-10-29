<#
.SYNOPSIS
  V11R-L4-EVIDENCE: real-window launch matrix for the shipped Avalonia shell.

.DESCRIPTION
  Launches the real app (no headless/CI fakes) for six size x appearance combinations plus the legacy
  rollback shell, waits for the actual top-level window, captures it with Win32/GDI (PrintWindow, with a
  CopyFromScreen fallback), waits for the process to exit naturally (the app's own --exit-after timer),
  and writes verification/V11R-L4-EVIDENCE/launch-matrix.json + screens/*.png.

  Exit handling (V11R-A-8 / Lead ruling after the first INT-2 rerun): a pass requires the window, a
  successful screenshot, Host ready, and a graceful exit code 0. The harness waits for the natural
  --exit-after exit; only if the app does not exit within a grace window does it send WM_CLOSE to the
  main window (recorded as exit_kind=graceful_close). Force-killing is the last resort, is recorded as
  terminated_by_harness=true, and can never count as a pass.

  Each case uses an isolated --data-root (temp, deleted afterwards) and an isolated --log-dir (kept as
  evidence). The real sidecar bundle is required: without it the Host legitimately reports
  SidecarBundleMissing and the window is not "Host ready", so the script fails fast instead of
  producing misleading screenshots.

  Any non-zero exit code, missing window, screenshot failure, Host-not-ready case or timeout makes the
  script exit non-zero with the reason recorded in the JSON (failures are never swallowed).

.PARAMETER SidecarDir
  Packaged sidecar directory (core_service.exe + host_bridge.exe). Defaults to
  $env:NEWMANGA_CORECLIENT_SIDECAR_DIR.

.PARAMETER OutputRoot
  Evidence root. Defaults to <repo>/verification/V11R-L4-EVIDENCE.

.PARAMETER TimeoutSeconds
  Per-case window-appearance timeout (default 30).

.PARAMETER ExitGraceSeconds
  Extra wait after --exit-after before the harness sends WM_CLOSE (default 20).

.PARAMETER SettleMs
  Extra wait after the window appears before the screenshot (default 1800 ms, lets first layout paint).

.PARAMETER SkipBuild
  Reuse the existing build output (the default builds NewManga.sln first with -warnaserror).

.PARAMETER IncludeLegacy
  Also run the --shell=legacy rollback smoke (default on; use -IncludeLegacy:$false to skip).

.EXAMPLE
  pwsh -NoProfile -File tools/e2e/v2-launch-matrix.ps1 -SidecarDir "D:\NewManga.workspace\task-envs\HOST-CORECLIENT-1\sidecar-copy"

.NOTES
  V11R-L4-EVIDENCE. Read-only w.r.t. product code; only writes under verification/V11R-L4-EVIDENCE/ and
  the OS temp directory. Win32/GDI capture only (no CUA/pointer automation).
#>
[CmdletBinding()]
param(
    [string]$SidecarDir = $env:NEWMANGA_CORECLIENT_SIDECAR_DIR,
    [string]$OutputRoot = '',
    [int]$TimeoutSeconds = 30,
    [int]$ExitGraceSeconds = 20,
    [int]$SettleMs = 1800,
    [switch]$SkipBuild,
    [bool]$IncludeLegacy = $true,
    [string]$Configuration = 'Debug'
)

$ErrorActionPreference = 'Stop'

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..\..')
$appProjectDir = Join-Path $repoRoot 'apps\desktop-avalonia'
if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    $OutputRoot = Join-Path $repoRoot 'verification\V11R-L4-EVIDENCE'
}
$screensDir = Join-Path $OutputRoot 'screens'
$logsDir = Join-Path $OutputRoot 'logs'
New-Item -ItemType Directory -Force -Path $OutputRoot, $screensDir, $logsDir | Out-Null

# ---------------------------------------------------------------------------------------------
# Win32/GDI capture (PrintWindow with PW_RENDERFULLCONTENT; CopyFromScreen fallback) + WM_CLOSE.
# System.Drawing is loaded as a PowerShell type reference, so only user32 needs Add-Type.
# ---------------------------------------------------------------------------------------------
Add-Type -AssemblyName System.Drawing.Common

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

public static class L4Native
{
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }

    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);

    [DllImport("user32.dll")]
    public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint flags);

    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool IsWindow(IntPtr hWnd);

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder text, int count);

    [DllImport("user32.dll")]
    public static extern bool PostMessage(IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam);

    public const uint WM_CLOSE = 0x0010;

    public static string Title(IntPtr hWnd)
    {
        var buffer = new System.Text.StringBuilder(512);
        GetWindowText(hWnd, buffer, buffer.Capacity);
        return buffer.ToString();
    }

    public static bool CloseWindow(IntPtr hWnd) => hWnd != IntPtr.Zero && IsWindow(hWnd) && PostMessage(hWnd, WM_CLOSE, IntPtr.Zero, IntPtr.Zero);
}
'@

function Save-WindowCapture {
    param([IntPtr]$Handle, [string]$Path)

    if ($Handle -eq [IntPtr]::Zero -or -not [L4Native]::IsWindowVisible($Handle)) {
        return 'window handle is zero or the window is not visible'
    }

    $rect = New-Object L4Native+RECT
    if (-not [L4Native]::GetWindowRect($Handle, [ref]$rect)) { return 'GetWindowRect failed' }
    $width = $rect.Right - $rect.Left
    $height = $rect.Bottom - $rect.Top
    if ($width -le 0 -or $height -le 0) { return "invalid window rect ${width}x${height}" }

    $bitmap = [System.Drawing.Bitmap]::new($width, $height, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    try {
        $hdc = $graphics.GetHdc()
        try { $printed = [L4Native]::PrintWindow($Handle, $hdc, 2) } finally { $graphics.ReleaseHdc($hdc) }
        if (-not $printed) {
            try {
                $graphics.CopyFromScreen($rect.Left, $rect.Top, 0, 0, [System.Drawing.Size]::new($width, $height), [System.Drawing.CopyPixelOperation]::SourceCopy)
            }
            catch {
                return "PrintWindow and CopyFromScreen both failed: $($_.Exception.Message)"
            }
        }

        $bitmap.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
        return ''
    }
    finally {
        $graphics.Dispose()
        $bitmap.Dispose()
    }
}

# ---------------------------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------------------------
function Get-RepoHead {
    Push-Location $repoRoot
    try { return (& git rev-parse HEAD) } finally { Pop-Location }
}

function Clear-LeftoverApps {
    $leftovers = @(Get-Process -Name 'NewManga.App' -ErrorAction SilentlyContinue)
    foreach ($leftover in $leftovers) { try { $leftover.Kill() } catch { } }
    if ($leftovers.Count -gt 0) { Start-Sleep -Milliseconds 400 }
    return $leftovers.Count
}

function Wait-AppWindow {
    param([datetime]$StartedAt, [int]$TimeoutSeconds)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $candidates = Get-Process -Name 'NewManga.App' -ErrorAction SilentlyContinue |
            Where-Object { $_.StartTime -ge $StartedAt -and $_.MainWindowHandle -ne 0 -and $_.MainWindowTitle -eq 'New Manga' }
        if ($candidates) {
            $process = $candidates | Sort-Object StartTime | Select-Object -First 1
            return [pscustomobject]@{ Process = $process; Handle = [IntPtr]$process.MainWindowHandle; Title = $process.MainWindowTitle }
        }

        Start-Sleep -Milliseconds 250
    }

    return $null
}

function Wait-ProcessExit {
    param([int]$ProcessId, [int]$TimeoutSeconds)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
        if (-not $process) { return $true }
        Start-Sleep -Milliseconds 200
    }

    return $false
}

function Stop-AppProcess {
    param([int]$ProcessId)
    $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if ($process) { try { $process.Kill() } catch { } }
}

function Invoke-LaunchCase {
    param(
        [string]$Name,
        [string]$Shell,
        [int]$Width,
        [int]$Height,
        [string]$Variant,
        [int]$ExitAfterMs,
        [string]$Sidecar
    )

    $leftoversKilled = Clear-LeftoverApps
    $caseStart = Get-Date
    $dataRoot = Join-Path $env:TEMP ("nm-l4-data-$Name-" + [guid]::NewGuid().ToString('N').Substring(0, 8))
    $caseLogDir = Join-Path $logsDir $Name
    New-Item -ItemType Directory -Force -Path $caseLogDir | Out-Null
    $mutex = "Local\NewManga.L4Evidence.$($Name)." + [guid]::NewGuid().ToString('N').Substring(0, 8)
    $screenshot = Join-Path $screensDir "$Name.png"

    $result = [ordered]@{
        case = $Name
        shell = $Shell
        width = $Width
        height = $Height
        variant = $Variant
        exit_after_ms = $ExitAfterMs
        data_root = $dataRoot
        log_dir = $caseLogDir
        screenshot = $screenshot
        pass = $false
        window_found = $false
        window_title = $null
        window_width = $null
        window_height = $null
        exit_code = $null
        exit_kind = $null
        terminated_by_harness = $false
        leftovers_killed_before_case = $leftoversKilled
        elapsed_ms = $null
        failure_reason = $null
        host_ready = $false
        host_ready_expected = $true
        host_log = $null
    }

    $job = Start-Job -ScriptBlock {
        param($AppDir, $Shell, $Width, $Height, $Variant, $ExitAfterMs, $DataRoot, $LogDir, $Sidecar, $Mutex)
        Set-Location $AppDir
        $argsList = @(
            'run', '--project', 'src/NewManga.App', '--no-build', '--',
            "--shell=$Shell",
            "--exit-after=$ExitAfterMs",
            "--data-root=$DataRoot",
            "--log-dir=$LogDir",
            "--sidecar-dir=$Sidecar",
            "--width=$Width",
            "--height=$Height",
            "--variant=$Variant",
            '--legacy-shell-check=off',
            "--mutex-name=$Mutex"
        )
        $output = & dotnet @argsList 2>&1
        $code = $LASTEXITCODE
        "EXIT_CODE=$code"
        $output | ForEach-Object { "APP_OUTPUT: $_" }
    } -ArgumentList $appProjectDir, $Shell, $Width, $Height, $Variant, $ExitAfterMs, $dataRoot, $caseLogDir, $Sidecar, $mutex

    $appProcessId = 0
    try {
        $window = Wait-AppWindow -StartedAt $caseStart -TimeoutSeconds $TimeoutSeconds
        if (-not $window) {
            $result.failure_reason = "window not found within ${TimeoutSeconds}s (no NewManga.App window with a non-zero handle)"
        }
        else {
            $appProcessId = $window.Process.Id
            $result.window_found = $true
            $result.window_title = $window.Title
            $rect = New-Object L4Native+RECT
            if ([L4Native]::GetWindowRect($window.Handle, [ref]$rect)) {
                $result.window_width = $rect.Right - $rect.Left
                $result.window_height = $rect.Bottom - $rect.Top
            }

            Start-Sleep -Milliseconds $SettleMs
            $captureError = Save-WindowCapture -Handle $window.Handle -Path $screenshot
            if ([string]::IsNullOrEmpty($captureError)) {
                $result.screenshot = $screenshot
            }
            else {
                $result.failure_reason = "screenshot failed: $captureError"
            }

            # Graceful-exit ladder: natural --exit-after first, WM_CLOSE only if it overruns, kill last.
            $naturalDeadline = [Math]::Max(5, [int]($ExitAfterMs / 1000) + $ExitGraceSeconds)
            if (Wait-ProcessExit -ProcessId $appProcessId -TimeoutSeconds $naturalDeadline) {
                $result.exit_kind = 'natural'
            }
            else {
                $closed = [L4Native]::CloseWindow($window.Handle)
                $graceful = $closed -and (Wait-ProcessExit -ProcessId $appProcessId -TimeoutSeconds 8)
                if ($graceful) {
                    $result.exit_kind = 'graceful_close'
                }
                else {
                    $result.exit_kind = 'harness_terminated'
                    $result.terminated_by_harness = $true
                    $result.failure_reason = 'app did not exit naturally or after WM_CLOSE; harness terminated it'
                    Stop-AppProcess -ProcessId $appProcessId
                }
            }
        }

        $job | Wait-Job -Timeout ([Math]::Max(30, $ExitGraceSeconds + 15)) | Out-Null
        if ($job.State -ne 'Completed') {
            if (-not $result.failure_reason) { $result.failure_reason = "launcher did not finish (job state $($job.State))" }
            $job | Stop-Job -ErrorAction SilentlyContinue
        }
        else {
            $jobOutput = Receive-Job $job
            $exitLine = $jobOutput | Where-Object { $_ -match '^EXIT_CODE=(-?\d+)$' } | Select-Object -Last 1
            if ($exitLine) { $result.exit_code = [int]($exitLine -replace '^EXIT_CODE=', '') }
            $appOutput = $jobOutput | Where-Object { $_ -like 'APP_OUTPUT:*' }
            if ($appOutput) {
                Set-Content -LiteralPath (Join-Path $caseLogDir 'app-console.log') -Value ($appOutput -join "`n") -Encoding utf8
            }
        }
    }
    finally {
        if ($appProcessId -gt 0) { Stop-AppProcess -ProcessId $appProcessId }
        Clear-LeftoverApps | Out-Null
        if ($job) { Remove-Job $job -Force -ErrorAction SilentlyContinue }
        $result.elapsed_ms = [int]((Get-Date) - $caseStart).TotalMilliseconds

        $hostLog = Join-Path $caseLogDir 'host.log'
        if (Test-Path -LiteralPath $hostLog) {
            $result.host_log = $hostLog
            $hostText = Get-Content -LiteralPath $hostLog -Raw
            $result.host_ready = ($hostText -match 'core_service ready') -and ($hostText -match 'self-check status=') -and ($hostText -match 'mode=ReadWrite')
        }

        if (Test-Path -LiteralPath $dataRoot) { Remove-Item -LiteralPath $dataRoot -Recurse -Force -ErrorAction SilentlyContinue }
    }

    if ($null -eq $result.exit_code) {
        if (-not $result.failure_reason) { $result.failure_reason = 'exit code was not reported by the launcher' }
    }
    elseif ($result.exit_code -ne 0) {
        $result.failure_reason = "non-zero exit code $($result.exit_code) (exit_kind=$($result.exit_kind))"
    }
    elseif (-not $result.window_found) {
        if (-not $result.failure_reason) { $result.failure_reason = 'window not found' }
    }
    elseif (-not (Test-Path -LiteralPath $screenshot)) {
        if (-not $result.failure_reason) { $result.failure_reason = 'screenshot file missing' }
    }
    elseif (-not $result.host_ready) {
        if (-not $result.failure_reason) { $result.failure_reason = 'Host did not reach ready state (see logs/<case>/host.log)' }
    }
    elseif ($result.terminated_by_harness) {
        if (-not $result.failure_reason) { $result.failure_reason = 'terminated_by_harness is never a pass' }
    }

    $result.pass = [string]::IsNullOrEmpty($result.failure_reason)
    return [pscustomobject]$result
}

# ---------------------------------------------------------------------------------------------
# Preconditions
# ---------------------------------------------------------------------------------------------
if ([string]::IsNullOrWhiteSpace($SidecarDir)) {
    throw 'SidecarDir is required: pass -SidecarDir or set NEWMANGA_CORECLIENT_SIDECAR_DIR (a directory with core_service.exe + host_bridge.exe)'
}
$SidecarDir = (Resolve-Path -LiteralPath $SidecarDir -ErrorAction Stop).Path
foreach ($exe in @('core_service.exe', 'host_bridge.exe')) {
    if (-not (Test-Path -LiteralPath (Join-Path $SidecarDir $exe))) {
        throw "sidecar bundle incomplete: $SidecarDir is missing $exe"
    }
}

$matrix = @(
    @{ Width = 1600; Height = 1000 },
    @{ Width = 1280; Height = 800 },
    @{ Width = 1024; Height = 700 }
)
$variants = @('dark', 'light')

Push-Location $appProjectDir
try {
    if (-not $SkipBuild) {
        $buildLog = Join-Path $logsDir 'build.log'
        & dotnet build NewManga.sln -warnaserror -c $Configuration 2>&1 | Tee-Object -FilePath $buildLog | Select-Object -Last 3
        if ($LASTEXITCODE -ne 0) { throw "dotnet build failed with exit code $LASTEXITCODE (see $buildLog)" }
    }
}
finally {
    Pop-Location
}

# ---------------------------------------------------------------------------------------------
# Matrix
# ---------------------------------------------------------------------------------------------
$cases = [System.Collections.Generic.List[object]]::new()
foreach ($size in $matrix) {
    foreach ($variant in $variants) {
        $name = "v2-$($size.Width)x$($size.Height)-$variant"
        Write-Host "== $name =="
        $case = Invoke-LaunchCase -Name $name -Shell 'v2' -Width $size.Width -Height $size.Height `
            -Variant $variant -ExitAfterMs 10000 -Sidecar $SidecarDir
        $cases.Add($case) | Out-Null
        Write-Host ("   pass={0} exit={1} exit_kind={2} elapsed={3}ms host_ready={4} reason={5}" -f `
            $case.pass, $case.exit_code, $case.exit_kind, $case.elapsed_ms, $case.host_ready, $case.failure_reason)
    }
}

$legacy = $null
if ($IncludeLegacy) {
    Write-Host '== legacy-rollback =='
    $legacy = Invoke-LaunchCase -Name 'legacy-1280x800-dark' -Shell 'legacy' -Width 1280 -Height 800 `
        -Variant 'dark' -ExitAfterMs 6000 -Sidecar $SidecarDir
    Write-Host ("   pass={0} exit={1} exit_kind={2} elapsed={3}ms host_ready={4} reason={5}" -f `
        $legacy.pass, $legacy.exit_code, $legacy.exit_kind, $legacy.elapsed_ms, $legacy.host_ready, $legacy.failure_reason)
}

$failures = @($cases | Where-Object { -not $_.pass })
if ($legacy -and -not $legacy.pass) { $failures += $legacy }

$allCases = @($cases) + $(if ($legacy) { @($legacy) } else { @() })
$summary = [ordered]@{
    total = $allCases.Count
    passed = ($allCases | Where-Object { $_.pass }).Count
    failed = $failures.Count
    host_ready_cases = ($allCases | Where-Object { $_.host_ready }).Count
    host_ready_expected_cases = ($allCases | Where-Object { $_.host_ready_expected }).Count
    natural_exit_cases = ($allCases | Where-Object { $_.exit_kind -eq 'natural' }).Count
    graceful_close_cases = ($allCases | Where-Object { $_.exit_kind -eq 'graceful_close' }).Count
    harness_terminated_cases = ($allCases | Where-Object { $_.terminated_by_harness }).Count
}

$document = [ordered]@{
    task = 'V11R-L4-EVIDENCE'
    generated_at = (Get-Date).ToUniversalTime().ToString('o')
    git_head = Get-RepoHead
    dotnet = (& dotnet --version)
    os = [System.Runtime.InteropServices.RuntimeInformation]::OSDescription
    sidecar_dir = $SidecarDir
    evidence_root = $OutputRoot
    matrix = $matrix
    variants = $variants
    exit_policy = 'natural --exit-after exit; WM_CLOSE only after the grace window (graceful_close); kill is recorded as terminated_by_harness and never passes'
    summary = $summary
    cases = $cases
    legacy_rollback = $legacy
    failures = @($failures | ForEach-Object { [ordered]@{ case = $_.case; reason = $_.failure_reason; exit_code = $_.exit_code; exit_kind = $_.exit_kind } })
}

$jsonPath = Join-Path $OutputRoot 'launch-matrix.json'
$document | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $jsonPath -Encoding utf8

Write-Host ''
Write-Host "launch matrix: $($summary.passed)/$($summary.total) passed, $($summary.failed) failed"
Write-Host "host ready: $($summary.host_ready_cases)/$($summary.total) | natural=$($summary.natural_exit_cases) graceful_close=$($summary.graceful_close_cases) harness_terminated=$($summary.harness_terminated_cases)"
Write-Host "screenshots: $((Get-ChildItem -LiteralPath $screensDir -Filter '*.png' -ErrorAction SilentlyContinue).Count) in $screensDir"
Write-Host "json: $jsonPath"

if ($failures.Count -gt 0) {
    Write-Host 'FAILURES:'
    $failures | ForEach-Object { Write-Host "  - $($_.case): $($_.failure_reason)" }
    exit 1
}

exit 0
