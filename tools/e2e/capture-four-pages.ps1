<#
.SYNOPSIS
    GATE3-FOUR-PAGE-WALKTHROUGH-1: capture the four first-class pages from the REAL Avalonia window.

.DESCRIPTION
    Condition 3 has long carried a "real device walkthrough" gap. That label was wrong: the app can be
    launched non-interactively (--page / --exit-after) and its top-level window captured with Win32/GDI,
    exactly as tools/e2e/v2-launch-matrix.ps1 does. This script reuses that approach for the four pages.

    For each page it launches the real app (no headless fakes), waits for a visible top-level window,
    captures it with PrintWindow (CopyFromScreen fallback), then lets the app's own --exit-after timer
    end the process.

    Read-only w.r.t. product code; writes only under verification/GATE3-FOUR-PAGE-WALKTHROUGH-1/.
#>
[CmdletBinding()]
param(
    [string]$SidecarDir = $env:NEWMANGA_CORECLIENT_SIDECAR_DIR,
    [string]$OutputRoot = '',
    [int]$ExitAfterMs = 12000,
    [int]$TimeoutSeconds = 45,
    [int]$SettleMs = 2200,
    [int]$Width = 1416,
    [int]$Height = 939,
    [switch]$SkipBuild
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    $OutputRoot = Join-Path $repoRoot 'verification\GATE3-FOUR-PAGE-WALKTHROUGH-1'
}
New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

public static class FpNative
{
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left, Top, Right, Bottom; }

    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint flags);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool IsWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    public static extern int GetWindowTextLength(IntPtr hWnd);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder text, int count);
}
'@

function Get-TopLevelWindow {
    param([System.Diagnostics.Process]$Process, [int]$TimeoutSeconds)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $Process.Refresh()
        if ($Process.HasExited) { return [IntPtr]::Zero }
        if ($Process.MainWindowHandle -ne [IntPtr]::Zero -and [FpNative]::IsWindowVisible($Process.MainWindowHandle)) {
            return $Process.MainWindowHandle
        }
        Start-Sleep -Milliseconds 200
    }
    return [IntPtr]::Zero
}

function Save-WindowCapture {
    param([IntPtr]$Handle, [string]$Path)

    if ($Handle -eq [IntPtr]::Zero -or -not [FpNative]::IsWindowVisible($Handle)) {
        return 'window handle is zero or the window is not visible'
    }

    $rect = New-Object FpNative+RECT
    if (-not [FpNative]::GetWindowRect($Handle, [ref]$rect)) { return 'GetWindowRect failed' }
    $width = $rect.Right - $rect.Left
    $height = $rect.Bottom - $rect.Top
    if ($width -le 0 -or $height -le 0) { return "invalid window rect ${width}x${height}" }

    $bitmap = New-Object System.Drawing.Bitmap $width, $height
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $hdc = $graphics.GetHdc()
    $printed = $false
    try { $printed = [FpNative]::PrintWindow($Handle, $hdc, 2) }
    finally { $graphics.ReleaseHdc($hdc) }

    if (-not $printed) {
        # CopyFromScreen fallback: PrintWindow can fail for composited/GPU windows.
        $graphics.CopyFromScreen($rect.Left, $rect.Top, 0, 0, (New-Object System.Drawing.Size $width, $height))
    }

    $bitmap.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
    $graphics.Dispose()
    $bitmap.Dispose()
    return $null
}

$appExe = Join-Path $repoRoot 'apps\desktop-avalonia\src\NewManga.App\bin\Debug\net9.0\NewManga.App.exe'
if (-not (Test-Path $appExe)) {
    $candidate = Get-ChildItem -Recurse -Filter 'NewManga.App.exe' -Path (Join-Path $repoRoot 'apps\desktop-avalonia\src') -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($candidate) { $appExe = $candidate.FullName }
}
if (-not (Test-Path $appExe)) { throw "NewManga.App.exe not found. Build first: dotnet build apps/desktop-avalonia/src/NewManga.App" }

$pages = @('bookshelf', 'library', 'reader', 'settings', 'workbench')
$results = @()

foreach ($page in $pages) {
    $name = "page-$page"
    $png = Join-Path $OutputRoot "$name.png"
    $log = Join-Path $OutputRoot "$name.startup.log"
    Remove-Item $png, $log -ErrorAction SilentlyContinue

    $args = @(
        "--page=$page", "--exit-after=$ExitAfterMs",
        "--width=$Width", "--height=$Height",
        "--log-dir=$OutputRoot"
    )
    if ($SidecarDir) { $args += "--sidecar-dir=$SidecarDir" }

    $proc = Start-Process -FilePath $appExe -ArgumentList $args -PassThru
    $handle = Get-TopLevelWindow -Process $proc -TimeoutSeconds $TimeoutSeconds

    if ($handle -eq [IntPtr]::Zero) {
        $results += [pscustomobject]@{ Page = $page; Captured = $false; Title = ''; Reason = 'no visible top-level window' }
        if (-not $proc.HasExited) { $proc.Kill() }
        continue
    }

    Start-Sleep -Milliseconds $SettleMs
    $title = [FpNative]::GetWindowTextLength($handle) -gt 0 ? '' : ''
    $reason = Save-WindowCapture -Handle $handle -Path $png
    $captured = (Test-Path $png)

    if (-not $proc.WaitForExit($TimeoutSeconds * 1000)) { try { $proc.Kill() } catch { } }

    $results += [pscustomobject]@{ Page = $page; Captured = $captured; Title = $title; Reason = ($reason ?? '') }
    Write-Host ("page={0,-10} captured={1} {2}" -f $page, $captured, $reason)
}

$results | ConvertTo-Json -Depth 4 | Set-Content (Join-Path $OutputRoot 'four-page-walkthrough.json') -Encoding utf8
Write-Host ''
Write-Host ("captured {0}/{1} pages -> {2}" -f ($results | Where-Object Captured).Count, $results.Count, $OutputRoot)
