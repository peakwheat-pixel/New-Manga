<#
.SYNOPSIS
  V11R-PUB-1: reproducible release publishing for the shipped Avalonia app.

.DESCRIPTION
  Publishes NewManga.App in one of the three release shapes and (optionally) smoke-tests the real
  artifact: the published exe is started with the packaged sidecar, an isolated data root/log dir/
  theme home, the window must appear, the Host must become ready (host.log: core_service ready +
  host_bridge ready), and the process must exit 0 (natural --exit-after, WM_CLOSE fallback).

  Modes:
    singlefile : self-contained single file, native libs bundled, no debug symbols (verified shape).
    trimmed    : + PublishTrimmed=true. The default run is an EXPECTED FAILURE: DesignSystem's
                 IL2026 (AvaloniaXamlLoader.Load) is promoted to an error by that project's
                 TreatWarningsAsErrors. -AllowTrimAnalysisWarnings produces a caveat build whose trim
                 safety is NOT analyzed.
    aot        : + PublishAot=true. The default run is an EXPECTED FAILURE (the csproj pins
                 PublishTrimmed=false, which native compilation cannot disable);
                 -AllowTrimAnalysisWarnings produces a caveat build (still IL3050 MicroCom warnings).

  Every run records the exact command, elapsed time, exit code, artifact path/size/sha256, a warning
  summary, smoke result and the git HEAD into <OutRoot>/manifest-<mode>.json plus build-<mode>.log.
  Binaries and manifests stay OUTSIDE the repository; -EvidenceDir copies only text evidence.

.PARAMETER Mode
  singlefile (default) | trimmed | aot | all (all three, in that order).

.PARAMETER Configuration
  Publish configuration (default Release).

.PARAMETER Runtime
  Target runtime identifier (default win-x64).

.PARAMETER OutRoot
  Artifact root; defaults to G:\CODEX\New Manga.workspace\artifacts\publish (never inside the repo).

.PARAMETER Smoke
  Run the real-window smoke test for each produced artifact (default on).

.PARAMETER SidecarDir
  Packaged sidecar bundle (core_service.exe + host_bridge.exe). Required when -Smoke is used.

.PARAMETER AllowTrimAnalysisWarnings
  Allow trimmed/aot publishes to suppress trim analysis warnings (caveat builds). Without it the
  trimmed/aot runs are expected failures and are reported as such, not as silent passes.

.PARAMETER EvidenceDir
  Optional evidence directory (e.g. verification/V11R-PUB-1). Logs/manifests/smoke JSON/screenshots
  are copied there; binaries never are.

.PARAMETER ExitAfterMs
  Smoke lifetime for the published exe (default 12000 ms); the harness waits for the natural exit.

.EXAMPLE
  pwsh -NoProfile -File tools/build/publish-release.ps1 -Mode all -AllowTrimAnalysisWarnings -Smoke `
    -SidecarDir "D:\NewManga.workspace\task-envs\HOST-CORECLIENT-1\sidecar-copy" `
    -EvidenceDir verification/V11R-PUB-1

.NOTES
  V11R-PUB-1. Read-only w.r.t. product code. Requires .NET 9 SDK; Windows long paths enabled for the
  deep verification/** tree. The published app needs the sidecar bundle at runtime.
#>
[CmdletBinding()]
param(
    [ValidateSet('singlefile', 'trimmed', 'aot', 'all')]
    [string]$Mode = 'singlefile',
    [string]$Configuration = 'Release',
    [string]$Runtime = 'win-x64',
    [string]$OutRoot = 'G:\CODEX\New Manga.workspace\artifacts\publish',
    [switch]$Smoke = $true,
    [string]$SidecarDir = $env:NEWMANGA_CORECLIENT_SIDECAR_DIR,
    [switch]$AllowTrimAnalysisWarnings,
    [string]$EvidenceDir = '',
    [int]$ExitAfterMs = 12000
)

$ErrorActionPreference = 'Stop'

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..\..')
$appProject = Join-Path $repoRoot 'apps\desktop-avalonia\src\NewManga.App\NewManga.App.csproj'
New-Item -ItemType Directory -Force -Path $OutRoot | Out-Null
if (-not [string]::IsNullOrWhiteSpace($EvidenceDir)) {
    New-Item -ItemType Directory -Force -Path $EvidenceDir | Out-Null
}

# ---------------------------------------------------------------------------------------------
# Win32/GDI helpers: window rect, PrintWindow capture, WM_CLOSE.
# ---------------------------------------------------------------------------------------------
Add-Type -AssemblyName System.Drawing.Common
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

public static class PubNative
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
    public static extern bool PostMessage(IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam);

    public const uint WM_CLOSE = 0x0010;

    public static bool CloseWindow(IntPtr hWnd) => hWnd != IntPtr.Zero && PostMessage(hWnd, WM_CLOSE, IntPtr.Zero, IntPtr.Zero);
}
'@

function Save-WindowScreenshot {
    param([IntPtr]$Handle, [string]$Path)

    if ($Handle -eq [IntPtr]::Zero -or -not [PubNative]::IsWindowVisible($Handle)) {
        return 'window handle is zero or the window is not visible'
    }

    $rect = New-Object PubNative+RECT
    if (-not [PubNative]::GetWindowRect($Handle, [ref]$rect)) { return 'GetWindowRect failed' }
    $width = $rect.Right - $rect.Left
    $height = $rect.Bottom - $rect.Top
    if ($width -le 0 -or $height -le 0) { return "invalid window rect ${width}x${height}" }

    $bitmap = [System.Drawing.Bitmap]::new($width, $height, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    try {
        $hdc = $graphics.GetHdc()
        try { $printed = [PubNative]::PrintWindow($Handle, $hdc, 2) } finally { $graphics.ReleaseHdc($hdc) }
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

function Clear-LeftoverApps {
    $leftovers = @(Get-Process -Name 'NewManga.App' -ErrorAction SilentlyContinue)
    foreach ($leftover in $leftovers) { try { $leftover.Kill() } catch { } }
    if ($leftovers.Count -gt 0) { Start-Sleep -Milliseconds 400 }
    return $leftovers.Count
}

function Wait-ForWindow {
    param([int]$ProcessId, [int]$TimeoutSeconds)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
        if (-not $process) { return $null }
        if ($process.MainWindowHandle -ne 0) {
            return [pscustomobject]@{ Handle = [IntPtr]$process.MainWindowHandle; Title = $process.MainWindowTitle }
        }

        Start-Sleep -Milliseconds 250
    }

    return $null
}

function Wait-HostReady {
    param([string]$HostLog, [int]$TimeoutSeconds)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-Path -LiteralPath $HostLog) {
            $text = Get-Content -LiteralPath $HostLog -Raw -ErrorAction SilentlyContinue
            if ($text -match 'core_service ready' -and $text -match 'host_bridge ready') {
                return $true
            }
        }

        Start-Sleep -Milliseconds 300
    }

    return $false
}

# ---------------------------------------------------------------------------------------------
# Publish + smoke
# ---------------------------------------------------------------------------------------------
function Get-RepoHead {
    Push-Location $repoRoot
    try { return (& git rev-parse HEAD) } finally { Pop-Location }
}

function Get-PublishArgs {
    param([string]$PublishMode)

    # NOTE: never name this $args — the automatic $args variable is a fixed-size array.
    $arguments = [System.Collections.Generic.List[string]]::new()
    $arguments.Add('publish'); $arguments.Add($appProject)
    $arguments.Add('-c'); $arguments.Add($Configuration)
    $arguments.Add('-r'); $arguments.Add($Runtime)
    $arguments.Add('--self-contained'); $arguments.Add('true')
    switch ($PublishMode) {
        'singlefile' {
            $arguments.Add('-p:PublishSingleFile=true')
            $arguments.Add('-p:IncludeNativeLibrariesForSelfExtract=true')
            $arguments.Add('-p:DebugType=None')
        }
        'trimmed' {
            $arguments.Add('-p:PublishTrimmed=true')
            if ($AllowTrimAnalysisWarnings) { $arguments.Add('-p:SuppressTrimAnalysisWarnings=true') }
        }
        'aot' {
            $arguments.Add('-p:PublishAot=true')
            $arguments.Add('-p:PublishTrimmed=true')
            if ($AllowTrimAnalysisWarnings) { $arguments.Add('-p:SuppressTrimAnalysisWarnings=true') }
        }
        default { throw "unknown publish mode '$PublishMode'" }
    }

    return ,$arguments
}

function Get-ExpectedFailureKind {
    param([string]$PublishMode, [string]$LogText)

    if ($PublishMode -eq 'trimmed' -and $LogText -match 'IL2026') {
        return 'expected: IL2026 trim analysis error promoted by TreatWarningsAsErrors (DesignSystem)'
    }

    if ($PublishMode -eq 'aot') {
        # AOT implies trimming, so the same IL2026 usually fires before the parameter conflict below.
        if ($LogText -match 'IL2026') {
            return 'expected: PublishAot implies trimming, so DesignSystem IL2026 (promoted to error) fires first'
        }

        if ($LogText -match 'PublishTrimmed is implied by native compilation and cannot be disabled') {
            return 'expected: PublishAot implies PublishTrimmed but the csproj pins PublishTrimmed=false'
        }
    }

    return $null
}

function Invoke-Smoke {
    param([string]$PublishMode, [string]$ExePath, [string]$ModeOutDir)

    $smokeRoot = Join-Path $OutRoot ("smoke-" + $PublishMode + "-" + [guid]::NewGuid().ToString('N').Substring(0, 8))
    $dataRoot = Join-Path $smokeRoot 'data'
    $logDir = Join-Path $smokeRoot 'logs'
    $themeHome = Join-Path $smokeRoot 'theme-home'
    New-Item -ItemType Directory -Force -Path $smokeRoot, $themeHome | Out-Null
    $mutex = 'Local\NewManga.Pub1.' + $PublishMode + '.' + [guid]::NewGuid().ToString('N').Substring(0, 8)
    $screenshot = Join-Path $ModeOutDir ("published-" + $PublishMode + ".png")
    $hostLog = Join-Path $logDir 'host.log'
    $smoke = [ordered]@{
        mode = $PublishMode
        exe = $ExePath
        data_root = $dataRoot
        log_dir = $logDir
        theme_home = $themeHome
        window_found = $false
        window_title = $null
        host_ready = $false
        exit_code = $null
        exit_kind = $null
        screenshot = $screenshot
        pass = $false
        failure_reason = $null
    }

    Clear-LeftoverApps | Out-Null
    # ProcessStartInfo.ArgumentList passes each argument verbatim; Start-Process would split the
    # space-containing OutRoot/SidecarDir paths and the app would reject the mis-parsed arguments.
    $psi = [System.Diagnostics.ProcessStartInfo]::new($ExePath)
    $psi.UseShellExecute = $false
    foreach ($argument in @(
        '--shell=v2',
        "--exit-after=$ExitAfterMs",
        "--data-root=$dataRoot",
        "--log-dir=$logDir",
        "--sidecar-dir=$SidecarDir",
        "--theme-home=$themeHome",
        '--width=1400',
        '--height=900',
        '--variant=dark',
        '--legacy-shell-check=off',
        "--mutex-name=$mutex"
    )) {
        $psi.ArgumentList.Add($argument)
    }

    $proc = [System.Diagnostics.Process]::Start($psi)
    try {
        $window = Wait-ForWindow -ProcessId $proc.Id -TimeoutSeconds 60
        if (-not $window) {
            $smoke.failure_reason = 'published app did not show a window within 60s'
        }
        else {
            $smoke.window_found = $true
            $smoke.window_title = $window.Title
            $smoke.host_ready = Wait-HostReady -HostLog $hostLog -TimeoutSeconds 60
            Start-Sleep -Milliseconds 1500
            $captureError = Save-WindowScreenshot -Handle $window.Handle -Path $screenshot
            if (-not [string]::IsNullOrEmpty($captureError)) {
                $smoke.failure_reason = "screenshot failed: $captureError"
            }
            elseif (-not $smoke.host_ready) {
                $smoke.failure_reason = 'Host did not reach ready state (host.log lacks core_service ready + host_bridge ready)'
            }

            # Graceful exit ladder: natural --exit-after first, WM_CLOSE only after the grace window.
            $graceMs = $ExitAfterMs + 20000
            if ($proc.WaitForExit($graceMs)) {
                $smoke.exit_kind = 'natural'
            }
            else {
                [PubNative]::CloseWindow($window.Handle) | Out-Null
                if ($proc.WaitForExit(10000)) {
                    $smoke.exit_kind = 'graceful_close'
                }
                else {
                    $smoke.exit_kind = 'harness_terminated'
                    $smoke.failure_reason = 'published app did not exit naturally or after WM_CLOSE; harness terminated it'
                    try { $proc.Kill() } catch { }
                }
            }
        }

        if (-not $proc.HasExited) {
            try { $proc.Kill() } catch { }
            $proc.WaitForExit(5000) | Out-Null
        }
        $smoke.exit_code = $proc.ExitCode
    }
    finally {
        Clear-LeftoverApps | Out-Null
        if (Test-Path -LiteralPath $smokeRoot) { Remove-Item -LiteralPath $smokeRoot -Recurse -Force -ErrorAction SilentlyContinue }
    }

    if ($null -eq $smoke.exit_code) {
        if (-not $smoke.failure_reason) { $smoke.failure_reason = 'exit code was not reported' }
    }
    elseif ($smoke.exit_code -ne 0) {
        $smoke.failure_reason = "non-zero exit code $($smoke.exit_code) (exit_kind=$($smoke.exit_kind))"
    }
    elseif (-not $smoke.window_found) {
        if (-not $smoke.failure_reason) { $smoke.failure_reason = 'window not found' }
    }
    elseif (-not (Test-Path -LiteralPath $screenshot)) {
        if (-not $smoke.failure_reason) { $smoke.failure_reason = 'screenshot file missing' }
    }
    elseif (-not $smoke.host_ready) {
        if (-not $smoke.failure_reason) { $smoke.failure_reason = 'Host not ready' }
    }

    $smoke.pass = [string]::IsNullOrEmpty($smoke.failure_reason)
    return [pscustomobject]$smoke
}

function Invoke-PublishMode {
    param([string]$PublishMode)

    $started = Get-Date
    $modeOutDir = Join-Path $OutRoot ($PublishMode + '-' + $Configuration + '-' + $Runtime)
    if (Test-Path -LiteralPath $modeOutDir) { Remove-Item -LiteralPath $modeOutDir -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $modeOutDir | Out-Null

    $publishArgs = Get-PublishArgs -PublishMode $PublishMode
    $publishArgs.Add('-o'); $publishArgs.Add($modeOutDir)
    $commandText = 'dotnet ' + (($publishArgs | ForEach-Object { if ($_ -match '\s') { '"' + $_ + '"' } else { $_ } }) -join ' ')
    $logPath = Join-Path $modeOutDir ('build-' + $PublishMode + '.log')

    Push-Location $repoRoot
    try {
        & dotnet @publishArgs 2>&1 | Tee-Object -FilePath $logPath | Out-Null
        $exitCode = $LASTEXITCODE
    }
    finally {
        Pop-Location
    }

    $elapsedMs = [int]((Get-Date) - $started).TotalMilliseconds
    $logText = Get-Content -LiteralPath $logPath -Raw -ErrorAction SilentlyContinue
    $warningLines = @([regex]::Matches($logText, '(?m)^.*\bwarning\s+(IL\d+|\w+)\b.*$') | ForEach-Object { $_.Value.Trim() } | Select-Object -First 40)
    $warningCodes = @([regex]::Matches($logText, '\b(IL\d{4}|CS\d{4})\b') | ForEach-Object { $_.Value } | Sort-Object -Unique)

    $exePath = Join-Path $modeOutDir 'NewManga.App.exe'
    $artifact = $null
    if (Test-Path -LiteralPath $exePath) {
        $item = Get-Item -LiteralPath $exePath
        $publishedFiles = @(Get-ChildItem -LiteralPath $modeOutDir -File -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -notlike 'build-*.log' -and $_.Name -notlike 'published-*.png' })
        $directoryBytes = ($publishedFiles | Measure-Object -Property Length -Sum).Sum
        if (-not $directoryBytes) { $directoryBytes = $item.Length }
        $artifact = [ordered]@{
            path = $item.FullName
            exe_size_bytes = $item.Length
            exe_size_mb = [math]::Round($item.Length / 1MB, 2)
            directory_size_bytes = $directoryBytes
            directory_size_mb = [math]::Round($directoryBytes / 1MB, 2)
            # Single-file modes ship one exe; trimmed publishes an apphost exe plus DLLs, so the
            # meaningful size is the directory total (recorded above).
            sha256 = (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash
        }
    }

    $expectedFailure = $null
    if ($exitCode -ne 0) {
        $expectedFailure = Get-ExpectedFailureKind -PublishMode $PublishMode -LogText $logText
        if ($expectedFailure -and -not $AllowTrimAnalysisWarnings) {
            # Documented default failure: expected, not a silent pass.
        }
        elseif ($expectedFailure) {
            $expectedFailure = $null
        }
    }

    $smokeResult = $null
    if ($Smoke -and $exitCode -eq 0 -and $artifact) {
        $smokeResult = Invoke-Smoke -PublishMode $PublishMode -ExePath $artifact.path -ModeOutDir $modeOutDir
    }

    $modeResult = 'FAIL'
    if ($exitCode -eq 0) {
        $modeResult = if ($Smoke -and $smokeResult -and -not $smokeResult.pass) { 'FAIL' } else { 'PASS' }
    }
    elseif ($expectedFailure -and -not $AllowTrimAnalysisWarnings) {
        $modeResult = 'EXPECTED_FAIL'
    }

    $manifest = [ordered]@{
        task = 'V11R-PUB-1'
        generated_at = (Get-Date).ToUniversalTime().ToString('o')
        git_head = Get-RepoHead
        dotnet = (& dotnet --version)
        os = [System.Runtime.InteropServices.RuntimeInformation]::OSDescription
        mode = $PublishMode
        configuration = $Configuration
        runtime = $Runtime
        allow_trim_analysis_warnings = [bool]$AllowTrimAnalysisWarnings
        command = $commandText
        publish_exit_code = $exitCode
        publish_elapsed_ms = $elapsedMs
        result = $modeResult
        expected_failure = if ($expectedFailure) { $expectedFailure } else { $null }
        guidance = if ($expectedFailure) { 'This is an expected failure; re-run with -AllowTrimAnalysisWarnings to produce the documented caveat build.' } else { $null }
        warning_codes = $warningCodes
        warnings_sample = $warningLines
        artifact = $artifact
        output_dir = $modeOutDir
        build_log = $logPath
        smoke = $smokeResult
        caveat = if ($PublishMode -in @('trimmed', 'aot')) { 'trim/AOT safety is NOT analyzed; SuppressTrimAnalysisWarnings only silences the analyzer.' } else { $null }
    }

    $manifestPath = Join-Path $OutRoot ('manifest-' + $PublishMode + '.json')
    $manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $manifestPath -Encoding utf8

    if (-not [string]::IsNullOrWhiteSpace($EvidenceDir)) {
        Copy-Item -LiteralPath $logPath -Destination $EvidenceDir -Force
        Copy-Item -LiteralPath $manifestPath -Destination $EvidenceDir -Force
        if ($smokeResult -and (Test-Path -LiteralPath $smokeResult.screenshot)) {
            Copy-Item -LiteralPath $smokeResult.screenshot -Destination $EvidenceDir -Force
        }

        $smokePath = Join-Path $EvidenceDir ('smoke-' + $PublishMode + '.json')
        if ($smokeResult) {
            $smokeResult | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $smokePath -Encoding utf8
        }
    }

    Write-Host ("[{0}] result={1} exit={2} elapsed={3}s artifact={4}" -f `
        $PublishMode, $modeResult, $exitCode, [math]::Round($elapsedMs / 1000.0, 1), `
        $(if ($artifact) { "$($artifact.directory_size_mb) MB sha256=$($artifact.sha256.Substring(0, 16))..." } else { 'none' }))
    if ($expectedFailure) { Write-Host ("   expected failure: {0}" -f $expectedFailure) }
    if ($smokeResult) {
        Write-Host ("   smoke: pass={0} exit={1} exit_kind={2} host_ready={3} reason={4}" -f `
            $smokeResult.pass, $smokeResult.exit_code, $smokeResult.exit_kind, $smokeResult.host_ready, $smokeResult.failure_reason)
    }

    return [pscustomobject]@{ mode = $PublishMode; result = $modeResult; exit_code = $exitCode; artifact = $artifact; smoke = $smokeResult; manifest = $manifestPath; expected_failure = $expectedFailure }
}

# ---------------------------------------------------------------------------------------------
# Preconditions + run
# ---------------------------------------------------------------------------------------------
if ($Smoke) {
    if ([string]::IsNullOrWhiteSpace($SidecarDir)) {
        throw 'SidecarDir is required when -Smoke is on: pass -SidecarDir or set NEWMANGA_CORECLIENT_SIDECAR_DIR'
    }

    $SidecarDir = (Resolve-Path -LiteralPath $SidecarDir -ErrorAction Stop).Path
    foreach ($exe in @('core_service.exe', 'host_bridge.exe')) {
        if (-not (Test-Path -LiteralPath (Join-Path $SidecarDir $exe))) {
            throw "sidecar bundle incomplete: $SidecarDir is missing $exe"
        }
    }
}

$modes = if ($Mode -eq 'all') { @('singlefile', 'trimmed', 'aot') } else { @($Mode) }
$results = [System.Collections.Generic.List[object]]::new()
foreach ($publishMode in $modes) {
    Write-Host "== $publishMode =="
    $results.Add((Invoke-PublishMode -PublishMode $publishMode)) | Out-Null
}

$hardFailures = @($results | Where-Object { $_.result -eq 'FAIL' })
$expectedFailures = @($results | Where-Object { $_.result -eq 'EXPECTED_FAIL' })
$summary = [ordered]@{
    total = $results.Count
    passed = @($results | Where-Object { $_.result -eq 'PASS' }).Count
    expected_failures = $expectedFailures.Count
    failed = $hardFailures.Count
}
$summaryPath = Join-Path $OutRoot 'manifest-summary.json'
$summaryDoc = [ordered]@{
    task = 'V11R-PUB-1'
    generated_at = (Get-Date).ToUniversalTime().ToString('o')
    git_head = Get-RepoHead
    modes = @($results | ForEach-Object {
        [ordered]@{
            mode = $_.mode
            result = $_.result
            publish_exit_code = $_.exit_code
            artifact_exe_size_mb = if ($_.artifact) { $_.artifact.exe_size_mb } else { $null }
            artifact_directory_size_mb = if ($_.artifact) { $_.artifact.directory_size_mb } else { $null }
            artifact_sha256 = if ($_.artifact) { $_.artifact.sha256 } else { $null }
            smoke_pass = if ($_.smoke) { $_.smoke.pass } else { $null }
            expected_failure = $_.expected_failure
        }
    })
    summary = $summary
}
$summaryDoc | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $summaryPath -Encoding utf8
if (-not [string]::IsNullOrWhiteSpace($EvidenceDir)) {
    Copy-Item -LiteralPath $summaryPath -Destination $EvidenceDir -Force
}

Write-Host ''
Write-Host "publish: $($summary.passed)/$($summary.total) PASS, $($summary.expected_failures) expected-failure(s), $($summary.failed) FAIL"
foreach ($result in $results) {
    Write-Host ("  - {0}: {1}" -f $result.mode, $result.result)
}

if ($hardFailures.Count -gt 0) {
    Write-Host 'FAILURES:'
    foreach ($failure in $hardFailures) { Write-Host ("  - {0}: publish exit {1}; smoke reason: {2}" -f $failure.mode, $failure.exit_code, $(if ($failure.smoke) { $failure.smoke.failure_reason } else { 'n/a' })) }
    exit 1
}

exit 0



