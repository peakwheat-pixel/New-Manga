<#
.SYNOPSIS
  End-to-end smoke of the published single-file new shell against the real Python Core.

.DESCRIPTION
  Launches the published exe with an isolated data root + unlabelled sidecar copy, waits for the
  window, captures it, proves there is no console window anywhere in the process tree, checks that
  both sidecars were spawned and are gone after exit, and stores wire/log evidence (AC2/AC3/AC6).

.EXAMPLE
  pwsh -NoProfile -File scripts/smoke.ps1
#>
[CmdletBinding()]
param(
    [string]$Exe = '',
    [string]$OutDir = '',
    [string]$SidecarDirectory = 'G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1/sidecar-copy',
    [int]$ExitAfterMs = 12000
)

$ErrorActionPreference = 'Stop'
$root = Resolve-Path (Join-Path $PSScriptRoot '..')
$repoRoot = Resolve-Path (Join-Path $root '..\..')
if ([string]::IsNullOrWhiteSpace($Exe)) {
    $Exe = Join-Path $root 'artifacts/win-x64-single/NewManga.App.exe'
}
if ([string]::IsNullOrWhiteSpace($OutDir)) {
    $OutDir = Join-Path $repoRoot 'verification/HOST-CORECLIENT-1/smoke'
}
if (-not (Test-Path $Exe)) {
    throw "published exe not found: $Exe (run scripts/publish.ps1 first)"
}
if (-not (Test-Path (Join-Path $SidecarDirectory 'core_service.exe'))) {
    throw "sidecar copy not found: $SidecarDirectory (run scripts/prepare-sidecar.ps1)"
}
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
Add-Type -AssemblyName System.Drawing

if (-not ('SmokeNative' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using System.Text;
public static class SmokeNative {
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc callback, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetClassName(IntPtr hWnd, StringBuilder name, int max);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
    [DllImport("dwmapi.dll")] public static extern int DwmGetWindowAttribute(IntPtr hwnd, int attr, out RECT value, int size);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
    public const int DWMWA_EXTENDED_FRAME_BOUNDS = 9;
}
'@
}

$dataRoot = Join-Path $env:TEMP ('newmanga-s1-smoke-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
$logDir = Join-Path $dataRoot 'logs'
foreach ($sub in @('derived', 'catalog', 'managed')) {
    New-Item -ItemType Directory -Force -Path (Join-Path $dataRoot $sub) | Out-Null
}
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$beforeCore = @(Get-Process core_service -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id)
$beforeBridge = @(Get-Process host_bridge -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id)

$arguments = @(
    "--data-root=`"$dataRoot`"",
    "--log-dir=`"$logDir`"",
    "--sidecar-dir=`"$SidecarDirectory`"",
    "--mutex-name=Local\NewManga.Host.Smoke",
    "--parity", "--demo-write", "--auto-roundtrip",
    "--exit-after=$ExitAfterMs"
) -join ' '

$process = Start-Process -FilePath $Exe -ArgumentList $arguments -PassThru
$visibleMs = $null
$hwnd = [IntPtr]::Zero
$deadline = [Environment]::TickCount64 + 20000
while ([Environment]::TickCount64 -lt $deadline) {
    $process.Refresh()
    if ($process.HasExited) { break }
    $candidate = $process.MainWindowHandle
    if ($candidate -ne [IntPtr]::Zero -and [SmokeNative]::IsWindowVisible($candidate)) {
        $hwnd = $candidate
        $visibleMs = [math]::Round(((Get-Date).ToUniversalTime() - $process.StartTime.ToUniversalTime()).TotalMilliseconds, 1)
        break
    }
    Start-Sleep -Milliseconds 5
}
if ($hwnd -eq [IntPtr]::Zero) {
    try { $process.Kill($true) } catch {}
    throw "window never became visible"
}

[void][SmokeNative]::SetForegroundWindow($hwnd)
Start-Sleep -Milliseconds 5000

# Window screenshot (composited, includes Mica).
$rect = New-Object SmokeNative+RECT
$size = [System.Runtime.InteropServices.Marshal]::SizeOf([type][SmokeNative+RECT])
if ([SmokeNative]::DwmGetWindowAttribute($hwnd, [SmokeNative]::DWMWA_EXTENDED_FRAME_BOUNDS, [ref]$rect, $size) -ne 0) {
    [void][SmokeNative]::GetWindowRect($hwnd, [ref]$rect)
}
$width = $rect.Right - $rect.Left
$height = $rect.Bottom - $rect.Top
$screenshot = Join-Path $OutDir 'window.png'
$bitmap = New-Object System.Drawing.Bitmap($width, $height)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
try {
    $graphics.CopyFromScreen($rect.Left, $rect.Top, 0, 0, (New-Object System.Drawing.Size($width, $height)))
} finally {
    $graphics.Dispose()
}
$bitmap.Save($screenshot, [System.Drawing.Imaging.ImageFormat]::Png)
$bitmap.Dispose()

# Process tree + console-window leak check.
$tree = @($process.Id)
$frontier = @($process.Id)
while ($frontier.Count -gt 0) {
    $next = @()
    foreach ($parent in $frontier) {
        foreach ($child in (Get-CimInstance Win32_Process -Filter "ParentProcessId=$parent" -ErrorAction SilentlyContinue)) {
            if (-not $tree.Contains([int]$child.ProcessId)) {
                $tree += [int]$child.ProcessId
                $next += [int]$child.ProcessId
            }
        }
    }
    $frontier = $next
}

$consoleWindows = @()
$visibleTitles = @()
$callback = [SmokeNative+EnumWindowsProc] {
    param($hWnd, $lParam)
    if ([SmokeNative]::IsWindowVisible($hWnd)) {
        $procId = [uint32]0
        [void][SmokeNative]::GetWindowThreadProcessId($hWnd, [ref]$procId)
        if ($tree -contains [int]$procId) {
            $name = New-Object System.Text.StringBuilder 256
            [void][SmokeNative]::GetClassName($hWnd, $name, 256)
            $class = $name.ToString()
            if ($class -eq 'ConsoleWindowClass') {
                $script:consoleWindows += [ordered]@{ pid = [int]$procId; class = $class }
            } else {
                $script:visibleTitles += [ordered]@{ pid = [int]$procId; class = $class }
            }
        }
    }
    return $true
}
[void][SmokeNative]::EnumWindows($callback, [IntPtr]::Zero)

$sidecarPids = @()
foreach ($name in @('core_service', 'host_bridge')) {
    foreach ($proc in (Get-Process $name -ErrorAction SilentlyContinue)) {
        if ($proc.StartTime.ToUniversalTime() -ge $process.StartTime.ToUniversalTime()) {
            $sidecarPids += [ordered]@{ name = $name; pid = $proc.Id }
        }
    }
}

if (-not $process.WaitForExit(25000)) {
    try { $process.Kill($true) } catch {}
    throw "published app did not exit within 25s"
}
$exitCode = $process.ExitCode
Start-Sleep -Milliseconds 500

$afterCore = @(Get-Process core_service -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id)
$afterBridge = @(Get-Process host_bridge -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id)
$leftoverCore = @($afterCore | Where-Object { $beforeCore -notcontains $_ })
$leftoverBridge = @($afterBridge | Where-Object { $beforeBridge -notcontains $_ })

$wireDir = Join-Path $logDir 'wire'
$wireFiles = @()
if (Test-Path $wireDir) {
    $targetWire = Join-Path $OutDir 'wire'
    New-Item -ItemType Directory -Force -Path $targetWire | Out-Null
    foreach ($file in Get-ChildItem $wireDir -File) {
        Copy-Item $file.FullName (Join-Path $targetWire $file.Name) -Force
        $wireFiles += $file.Name
    }
}
$hostLog = Join-Path $logDir 'host.log'
$hostLogCopy = $null
if (Test-Path $hostLog) {
    $hostLogCopy = Join-Path $OutDir 'host.log'
    Copy-Item $hostLog $hostLogCopy -Force
}

$hostLogText = if (Test-Path $hostLog) { Get-Content $hostLog -Raw } else { '' }
$coreWirePath = Join-Path $wireDir 'core-service.ndjson'
$chineseRoundTripEvidence = $false
$chineseWireSample = $null
if (Test-Path $coreWirePath) {
    foreach ($line in (Get-Content $coreWirePath)) {
        try { $frame = $line | ConvertFrom-Json } catch { continue }
        if ($frame.request -like '*CreateBook*' -and $frame.request -match '\\u96fe\\u6e2f\\u6765\\u4fe1\\u30fb\\u65e5\\u672c\\u8a9e\\u30c6\\u30b9\\u30c8') {
            $chineseRoundTripEvidence = $true
            $chineseWireSample = [ordered]@{
                request = $frame.request
                request_ascii_only = $frame.request_ascii_only
                response_ascii_only = $frame.response_ascii_only
                request_utf8_hex = $frame.request_utf8_hex
            }
            break
        }
    }
}
$chineseRoundTripEvidence = $chineseRoundTripEvidence

$result = [ordered]@{
    ac = 'AC2/AC3/AC6'
    exe = (Resolve-Path $Exe).Path
    data_root = $dataRoot
    window_visible_ms = $visibleMs
    window_rect = [ordered]@{ x = $rect.Left; y = $rect.Top; width = $width; height = $height }
    screenshot = $screenshot
    process_tree = $tree
    sidecars_spawned = $sidecarPids
    console_windows = $consoleWindows
    console_window_count = $consoleWindows.Count
    visible_window_classes = $visibleTitles
    exit_code = $exitCode
    leftover_sidecar_pids = [ordered]@{ core_service = $leftoverCore; host_bridge = $leftoverBridge }
    wire_files = $wireFiles
    host_log = $hostLogCopy
    chinese_roundtrip_wire_evidence = $chineseRoundTripEvidence
    chinese_roundtrip_wire_sample = $chineseWireSample
    at_utc = [DateTime]::UtcNow.ToString('o')
}
$result | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $OutDir 'smoke.json') -Encoding utf8
$result | ConvertTo-Json -Depth 4

if ($consoleWindows.Count -ne 0) { throw "console window leak detected" }
if ($exitCode -ne 0) { throw "published app exited with $exitCode" }
if ($leftoverCore.Count -ne 0 -or $leftoverBridge.Count -ne 0) { throw "sidecar process leak after exit" }
if (-not $chineseRoundTripEvidence) { throw "core wire evidence for the Chinese round trip missing" }
Write-Output "SMOKE PASS"
