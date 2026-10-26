# Window probe / cold-start harness for the S0 Avalonia spike.
#
# Measures process-create -> window-visible latency by polling the native HWND (not by trusting the
# app's own timestamps), captures the window from the desktop (so DWM-composed Mica is included),
# then kills the process. Every run writes raw per-run numbers to JSON; screenshots land next to it.
#
# Examples:
#   pwsh -NoProfile -File scripts/window_probe.ps1 -Exe "publish/win-x64-single-trimmed/Spike.App.exe" `
#        -Arguments "--out=... --assets=..." -OutDir ".../cold-start" -Runs 3 -WarmupRuns 1
#
#   pwsh -NoProfile -File scripts/window_probe.ps1 -Exe ... -Arguments "--mode=window --mica=off ..." `
#        -OutDir ".../mica" -Runs 1 -ClientOnly
param(
    [Parameter(Mandatory = $true)][string]$Exe,
    [string]$Arguments = "",
    [Parameter(Mandatory = $true)][string]$OutDir,
    [string]$PngPrefix = "window",
    [int]$Runs = 1,
    [int]$WarmupRuns = 0,
    [int]$SettleMs = 1200,
    [int]$TimeoutMs = 20000,
    [switch]$ClientOnly,
    [switch]$NoKill
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
Add-Type -AssemblyName System.Drawing

if (-not ('WindowProbe.Native' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

namespace WindowProbe {
    public static class Native {
        [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
        [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
        [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr hWnd, out RECT rect);
        [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr hWnd, ref POINT point);
        [DllImport("dwmapi.dll")] public static extern int DwmGetWindowAttribute(IntPtr hwnd, int attr, out RECT value, int size);
        [DllImport("dwmapi.dll")] public static extern int DwmGetWindowAttribute(IntPtr hwnd, int attr, out int value, int size);
        [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
        [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X, Y; }
        public const int DWMWA_EXTENDED_FRAME_BOUNDS = 9;
        public const int DWMWA_CLOAKED = 14;
    }
}
'@
}

function Get-VisibleBounds([IntPtr]$hwnd) {
    $rect = New-Object WindowProbe.Native+RECT
    $sizeof = [System.Runtime.InteropServices.Marshal]::SizeOf([type][WindowProbe.Native+RECT])
    if ([WindowProbe.Native]::DwmGetWindowAttribute($hwnd, [WindowProbe.Native]::DWMWA_EXTENDED_FRAME_BOUNDS, [ref]$rect, $sizeof) -ne 0) {
        [void][WindowProbe.Native]::GetWindowRect($hwnd, [ref]$rect)
    }
    return $rect
}

function Test-Cloaked([IntPtr]$hwnd) {
    $cloaked = 0
    $hr = [WindowProbe.Native]::DwmGetWindowAttribute($hwnd, [WindowProbe.Native]::DWMWA_CLOAKED, [ref]$cloaked, 4)
    return ($hr -eq 0 -and $cloaked -ne 0)
}

function Capture-Window([IntPtr]$hwnd, [string]$path, [switch]$ClientOnlyCapture) {
    if ($ClientOnlyCapture) {
        $rect = New-Object WindowProbe.Native+RECT
        [void][WindowProbe.Native]::GetClientRect($hwnd, [ref]$rect)
        $origin = New-Object WindowProbe.Native+POINT
        $origin.X = 0; $origin.Y = 0
        [void][WindowProbe.Native]::ClientToScreen($hwnd, [ref]$origin)
        $x = $origin.X; $y = $origin.Y
        $w = $rect.Right - $rect.Left; $h = $rect.Bottom - $rect.Top
    } else {
        $rect = Get-VisibleBounds $hwnd
        $x = $rect.Left; $y = $rect.Top
        $w = $rect.Right - $rect.Left; $h = $rect.Bottom - $rect.Top
    }
    if ($w -le 0 -or $h -le 0) { throw "window has empty capture rect ($w x $h)" }
    $bmp = New-Object System.Drawing.Bitmap($w, $h)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    try {
        $g.CopyFromScreen($x, $y, 0, 0, (New-Object System.Drawing.Size($w, $h)))
    } finally {
        $g.Dispose()
    }
    $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $bmp.Dispose()
    return @{ x = $x; y = $y; width = $w; height = $h }
}

function Invoke-OneRun([int]$index, [bool]$measure) {
    $startSw = [System.Diagnostics.Stopwatch]::StartNew()
    $startUtc = [DateTime]::UtcNow
    if ($Arguments.Trim().Length -gt 0) {
        $process = Start-Process -FilePath $Exe -ArgumentList $Arguments -PassThru
    } else {
        $process = Start-Process -FilePath $Exe -PassThru
    }

    $visibleMs = $null
    $foundUtc = $null
    $hwnd = [IntPtr]::Zero
    $deadline = $startSw.ElapsedMilliseconds + $TimeoutMs
    while ($startSw.ElapsedMilliseconds -lt $deadline) {
        $process.Refresh()
        $candidate = $process.MainWindowHandle
        if ($candidate -ne [IntPtr]::Zero) {
            if ([WindowProbe.Native]::IsWindowVisible($candidate) -and -not (Test-Cloaked $candidate)) {
                $hwnd = $candidate
                $visibleMs = $startSw.ElapsedMilliseconds
                $foundUtc = [DateTime]::UtcNow
                break
            }
        }
        Start-Sleep -Milliseconds 2
    }
    $startSw.Stop()
    if ($null -eq $visibleMs) {
        try { $process.Kill($true) } catch {}
        throw "window did not become visible within $TimeoutMs ms (run $index)"
    }

    Start-Sleep -Milliseconds $SettleMs
    $png = Join-Path $OutDir ("{0}_run{1}.png" -f $PngPrefix, $index)
    $bounds = Capture-Window -hwnd $hwnd -path $png -ClientOnlyCapture:$ClientOnly

    $process.Refresh()
    $fromCreateMs = $null
    try {
        $fromCreateMs = [math]::Round(($foundUtc - $process.StartTime.ToUniversalTime()).TotalMilliseconds, 1)
    } catch {
        $fromCreateMs = $null
    }
    $result = [ordered]@{
        run = $index
        measured = $measure
        process_create_utc = $startUtc.ToString('o')
        window_visible_ms = $visibleMs
        window_visible_from_create_ms = $fromCreateMs
        hwnd = ('0x{0:X}' -f $hwnd.ToInt64())
        pid = $process.Id
        working_set_mb = [math]::Round($process.WorkingSet64 / 1MB, 1)
        process_start_time = $process.StartTime.ToString('o')
        capture = $bounds
        png = $png
    }

    if (-not $NoKill) {
        try { $process.CloseMainWindow() | Out-Null } catch {}
        if (-not $process.WaitForExit(2000)) {
            try { $process.Kill($true) } catch {}
        }
    }
    return $result
}

$results = @()
# Warm-up run (filesystem cache / AV scan / single-file self-extract); not part of the metric.
for ($w = 1; $w -le $WarmupRuns; $w++) {
    $null = Invoke-OneRun -index 0 -measure $false
}
for ($i = 1; $i -le $Runs; $i++) {
    $results += Invoke-OneRun -index $i -measure $true
}

$measuredRuns = @($results | Where-Object { $_.measured })
$sorted = @($measuredRuns | ForEach-Object { $_.window_visible_ms } | Sort-Object)
$sortedFromCreate = @($measuredRuns | ForEach-Object { $_.window_visible_from_create_ms } | Where-Object { $_ -ne $null } | Sort-Object)
$json = [ordered]@{
    exe = $Exe
    arguments = $Arguments
    runs = $results
    measured_count = $measuredRuns.Count
    visible_ms_sorted = $sorted
    visible_ms_p50 = if ($sorted.Count -gt 0) { $sorted[[int][math]::Floor(($sorted.Count - 1) / 2)] } else { $null }
    visible_from_create_ms_sorted = $sortedFromCreate
    visible_from_create_ms_p50 = if ($sortedFromCreate.Count -gt 0) { $sortedFromCreate[[int][math]::Floor(($sortedFromCreate.Count - 1) / 2)] } else { $null }
    visible_from_create_ms_min = if ($sortedFromCreate.Count -gt 0) { $sortedFromCreate[0] } else { $null }
    visible_from_create_ms_max = if ($sortedFromCreate.Count -gt 0) { $sortedFromCreate[-1] } else { $null }
    captured_at_utc = [DateTime]::UtcNow.ToString('o')
}
$jsonPath = Join-Path $OutDir ($PngPrefix + '.json')
$json | ConvertTo-Json -Depth 6 | Set-Content -Path $jsonPath -Encoding utf8
Write-Output ($json | ConvertTo-Json -Depth 6)
