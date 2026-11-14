<#
.SYNOPSIS
  GATE4-READER-PAGE-1: try to reach the READER without a human, and prove or disprove it honestly.

.DESCRIPTION
  Facts this script is built on (verified in code, not guessed):
    * App.axaml.cs SpaceForStartupPage maps "bookshelf"|"library"|"reader" all to SpaceId.Library,
      so --page=reader cannot open the reader; it only picks the Library space.
    * The reader is an IMMERSIVE WINDOW opened by ImmersiveReaderRequested, raised either by bare F11
      or by ShellCommandIds.LibraryImmersiveReader (AppShellViewModel).

  So the only parameter-free path is: launch into Library, select a book, press F11. Selecting a book
  needs a pointer click; this script does NOT fake that. It presses F11 and reports what actually
  happened. If no new window appears, the honest answer is NEEDS_INTERACTION.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$OutPath,
    [Parameter(Mandatory = $true)][string]$ExePath,
    [Parameter(Mandatory = $true)][string]$DataRoot,
    [Parameter(Mandatory = $true)][string]$LogDir,
    [Parameter(Mandatory = $true)][string]$SidecarDir,
    [Parameter(Mandatory = $true)][string]$ThemeHome
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

if (-not ('Reader4Win32' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class Reader4Win32 {
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
}
'@
}

function Get-Title([IntPtr]$h) {
    $b = New-Object System.Text.StringBuilder 512
    [void][Reader4Win32]::GetWindowText($h, $b, $b.Capacity)
    return $b.ToString()
}

function Get-LumaVariance([System.Drawing.Bitmap]$bmp) {
    $sum = 0.0; $sq = 0.0; $n = 0
    for ($y = 0; $y -lt $bmp.Height; $y += 17) {
        for ($x = 0; $x -lt $bmp.Width; $x += 17) {
            $px = $bmp.GetPixel($x, $y)
            $l = 0.299 * $px.R + 0.587 * $px.G + 0.114 * $px.B
            $sum += $l; $sq += $l * $l; $n++
        }
    }
    if ($n -eq 0) { return 0.0 }
    $m = $sum / $n
    return ($sq / $n) - ($m * $m)
}

$psi = [System.Diagnostics.ProcessStartInfo]::new($ExePath)
$psi.UseShellExecute = $false
foreach ($arg in @(
    '--shell=v2', '--page=library', '--exit-after=60000',
    "--data-root=$DataRoot", "--log-dir=$LogDir", "--sidecar-dir=$SidecarDir",
    "--theme-home=$ThemeHome", '--width=1400', '--height=900', '--legacy-shell-check=off'
)) { $psi.ArgumentList.Add($arg) }

$process = [System.Diagnostics.Process]::Start($psi)
try {
    # Poll (30s) -- the first attempt used a bare 8s sleep and gave up while the app was still starting.
    $handle = [IntPtr]::Zero
    for ($i = 0; $i -lt 120; $i++) {
        Start-Sleep -Milliseconds 250
        $process.Refresh()
        if ($process.HasExited) { break }
        if ($process.MainWindowHandle -ne [IntPtr]::Zero) { $handle = $process.MainWindowHandle; break }
    }
    if ($handle -eq [IntPtr]::Zero) {
        Write-Host "FAIL: no main window within 30s (exited=$($process.HasExited))"
        exit 1
    }
    $shellTitle = Get-Title $handle
    Write-Host "shell window: handle=$handle title='$shellTitle'"

    # Give the shell time to load the library projection before we ask it for the reader.
    Start-Sleep -Seconds 6
    [void][Reader4Win32]::ShowWindow($handle, 9)
    [void][Reader4Win32]::SetForegroundWindow($handle)
    Start-Sleep -Milliseconds 900
    $foreground = [Reader4Win32]::GetForegroundWindow()
    Write-Host "foreground=$foreground (shell=$handle, match=$($foreground -eq $handle))"

    # Bare F11 (VK_F11 = 0x7A): key down, then key up.
    [Reader4Win32]::keybd_event(0x7A, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 150
    [Reader4Win32]::keybd_event(0x7A, 0, 2, [UIntPtr]::Zero)
    Start-Sleep -Seconds 4

    $process.Refresh()
    $afterTitle = if ($process.MainWindowHandle -ne [IntPtr]::Zero) { Get-Title $process.MainWindowHandle } else { '' }
    Write-Host "after F11: mainHandle=$($process.MainWindowHandle) title='$afterTitle'"

    $target = [IntPtr]::Zero
    if ($process.MainWindowHandle -ne [IntPtr]::Zero -and $process.MainWindowHandle -ne $handle) {
        $target = $process.MainWindowHandle
    }

    if ($target -eq [IntPtr]::Zero) {
        Write-Host "NEEDS_INTERACTION: F11 did not open a separate reader window; no book is selected,"
        Write-Host "  and selecting one requires a pointer click that this script refuses to fake."
        exit 3
    }

    $rect = New-Object Reader4Win32+RECT
    [void][Reader4Win32]::GetWindowRect($target, [ref]$rect)
    $w = $rect.Right - $rect.Left
    $hgt = $rect.Bottom - $rect.Top
    $bitmap = New-Object System.Drawing.Bitmap $w, $hgt
    $g = [System.Drawing.Graphics]::FromImage($bitmap)
    $hdc = $g.GetHdc()
    try { [void][Reader4Win32]::PrintWindow($target, $hdc, [uint32]2) } finally { $g.ReleaseHdc($hdc); $g.Dispose() }
    $variance = Get-LumaVariance $bitmap
    $dir = Split-Path -Parent $OutPath
    if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    $bitmap.Save($OutPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $bitmap.Dispose()
    Write-Host "reader window: ${w}x${hgt} variance=$([math]::Round($variance,1)) title='$(Get-Title $target)' -> $OutPath"
    if ($variance -lt 40) { Write-Host "FAIL: reader frame is blank-ish"; exit 2 }
    exit 0
} finally {
    if (-not $process.HasExited) { try { $process.Kill() } catch { } }
    $process.Dispose()
}
