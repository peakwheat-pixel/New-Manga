<#
.SYNOPSIS
  GATE4-PAGES-UPGRADE-1: capture one top-level page of the INSTALLED app, rendered from the window itself.

.DESCRIPTION
  IMPORTANT LESSON BAKED IN: the first version of this script used Graphics.CopyFromScreen on the window
  rectangle. That captured whatever happened to be on screen -- it produced four images of the *desktop*
  (a chat window) instead of four pages of the app, and their differing hashes made them look plausible.
  Screen grabbing proves nothing unless you own the foreground.

  This version therefore:
    1. resolves the window handle and requires its title to contain "NewManga" (fail closed otherwise);
    2. renders with PrintWindow(PW_RENDERFULLCONTENT), which does not depend on the window being visible
       or unoccluded;
    3. falls back to PrintWindow(0) if the full-content flag yields a blank frame;
    4. measures pixel variance so a black/one-colour frame is a FAILURE, not evidence.

  A human must still eyeball the resulting PNG before it counts as a page-reachability proof.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Page,
    [Parameter(Mandatory = $true)][string]$OutPath,
    [Parameter(Mandatory = $true)][string]$ExePath,
    [Parameter(Mandatory = $true)][string]$DataRoot,
    [Parameter(Mandatory = $true)][string]$LogDir,
    [Parameter(Mandatory = $true)][string]$SidecarDir,
    [Parameter(Mandatory = $true)][string]$ThemeHome,
    [int]$RenderWaitMs = 5000,
    [double]$MinVariance = 40.0
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

if (-not ('Gate4Win32' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class Gate4Win32 {
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
}
'@
}

function Get-WindowTitle([IntPtr]$handle) {
    $buffer = New-Object System.Text.StringBuilder 512
    [void][Gate4Win32]::GetWindowText($handle, $buffer, $buffer.Capacity)
    return $buffer.ToString()
}

function Measure-LumaVariance([System.Drawing.Bitmap]$bitmap) {
    $sum = 0.0
    $sumSquares = 0.0
    $count = 0
    for ($y = 0; $y -lt $bitmap.Height; $y += 17) {
        for ($x = 0; $x -lt $bitmap.Width; $x += 17) {
            $pixel = $bitmap.GetPixel($x, $y)
            $luma = 0.299 * $pixel.R + 0.587 * $pixel.G + 0.114 * $pixel.B
            $sum += $luma
            $sumSquares += $luma * $luma
            $count++
        }
    }
    if ($count -eq 0) { return 0.0 }
    $mean = $sum / $count
    return ($sumSquares / $count) - ($mean * $mean)
}

$psi = [System.Diagnostics.ProcessStartInfo]::new($ExePath)
$psi.UseShellExecute = $false
foreach ($arg in @(
    '--shell=v2',
    "--page=$Page",
    '--exit-after=30000',
    "--data-root=$DataRoot",
    "--log-dir=$LogDir",
    "--sidecar-dir=$SidecarDir",
    "--theme-home=$ThemeHome",
    '--width=1400',
    '--height=900',
    '--legacy-shell-check=off'
)) {
    $psi.ArgumentList.Add($arg)
}

$process = [System.Diagnostics.Process]::Start($psi)
try {
    $handle = [IntPtr]::Zero
    $title = ''
    for ($attempt = 0; $attempt -lt 80; $attempt++) {
        Start-Sleep -Milliseconds 250
        $process.Refresh()
        if ($process.HasExited) { break }
        if ($process.MainWindowHandle -ne [IntPtr]::Zero) {
            $handle = $process.MainWindowHandle
            $title = Get-WindowTitle $handle
            if ($title -like '*NewManga*' -or $title -like '*New Manga*') { break }
            $handle = [IntPtr]::Zero
        }
    }
    if ($handle -eq [IntPtr]::Zero) {
        Write-Host "FAIL($Page): no NewManga window appeared (title='$title', exited=$($process.HasExited))"
        exit 1
    }

    # Render from the window itself -- never from the screen, which is what the first attempt did wrong.
    Start-Sleep -Milliseconds $RenderWaitMs
    $rect = New-Object Gate4Win32+RECT
    [void][Gate4Win32]::GetWindowRect($handle, [ref]$rect)
    $width = $rect.Right - $rect.Left
    $height = $rect.Bottom - $rect.Top
    if ($width -lt 200 -or $height -lt 200) {
        Write-Host "FAIL($Page): window too small (${width}x${height})"
        exit 1
    }

    $directory = Split-Path -Parent $OutPath
    if (-not (Test-Path -LiteralPath $directory)) {
        New-Item -ItemType Directory -Force -Path $directory | Out-Null
    }

    $best = $null
    $bestVariance = -1.0
    foreach ($flags in @([uint32]2, [uint32]0)) {
        $bitmap = New-Object System.Drawing.Bitmap $width, $height
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
        try {
            $hdc = $graphics.GetHdc()
            try {
                [void][Gate4Win32]::PrintWindow($handle, $hdc, $flags)
            } finally {
                $graphics.ReleaseHdc($hdc)
            }
        } finally {
            $graphics.Dispose()
        }
        $variance = Measure-LumaVariance $bitmap
        if ($variance -gt $bestVariance) {
            if ($null -ne $best) { $best.Dispose() }
            $best = $bitmap
            $bestVariance = $variance
        } else {
            $bitmap.Dispose()
        }
        if ($bestVariance -ge $MinVariance) { break }
    }

    try {
        $best.Save($OutPath, [System.Drawing.Imaging.ImageFormat]::Png)
        $bytes = (Get-Item -LiteralPath $OutPath).Length
        if ($bestVariance -lt $MinVariance) {
            Write-Host "FAIL($Page): PrintWindow yielded a blank-ish frame (variance=$([math]::Round($bestVariance,1)) < $MinVariance) title='$title'"
            exit 2
        }
        Write-Host "OK($Page): ${width}x${height} variance=$([math]::Round($bestVariance,1)) bytes=$bytes title='$title' -> $OutPath"
        exit 0
    } finally {
        $best.Dispose()
    }
} finally {
    if (-not $process.HasExited) {
        try { $process.Kill() } catch { }
    }
    $process.Dispose()
}
