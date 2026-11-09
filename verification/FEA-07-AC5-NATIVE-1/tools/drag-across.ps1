# FEA-07-AC5-NATIVE-1 / drag-across.ps1
# 真实鼠标拖动：把应用主窗从 2K 屏拖到 4K 屏（真实用户手势），记录 DPI/rect/越界与截图。
[CmdletBinding()]
param(
  [string]$OutDir = "",
  [int]$SettleMs = 1200,
  [switch]$KeepRunning
)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-AC5-NATIVE-1\evidence' }
$shots = Join-Path $OutDir 'screenshots'
New-Item -ItemType Directory -Force -Path $OutDir, $shots | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'

$cs = @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;

public static class DragApi {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int left, top, right, bottom; }
  [StructLayout(LayoutKind.Sequential)] public struct POINT { public int x, y; }
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc cb, IntPtr l);
  public delegate bool EnumWindowsProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern uint GetDpiForWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr a, int x, int y, int cx, int cy, uint f);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint flags, uint dx, uint dy, uint data, UIntPtr extra);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr v);
  [DllImport("user32.dll")] public static extern bool GetCursorPos(out POINT p);
  [DllImport("user32.dll")] public static extern IntPtr WindowFromPoint(POINT p);
  [DllImport("user32.dll")] public static extern IntPtr GetAncestor(IntPtr h, uint flags);

  public static IntPtr MainWindowOf(uint pid) {
    SetProcessDpiAwarenessContext(new IntPtr(-4));
    IntPtr found = IntPtr.Zero;
    EnumWindows((h, l) => {
      uint p; GetWindowThreadProcessId(h, out p);
      if (p != pid || !IsWindowVisible(h)) return true;
      RECT r; GetWindowRect(h, out r);
      if (r.right - r.left < 200) return true;
      found = h; return false;
    }, IntPtr.Zero);
    return found;
  }
  public static string Rect(IntPtr h) {
    RECT r; GetWindowRect(h, out r);
    return string.Format("{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}", r.left, r.top, r.right - r.left, r.bottom - r.top, GetDpiForWindow(h), Math.Round(GetDpiForWindow(h) / 96.0 * 100), r.right, r.bottom);
  }
  public static string Drag(int fromX, int fromY, int toX, int toY, int steps) {
    SetCursorPos(fromX, fromY);
    System.Threading.Thread.Sleep(120);
    mouse_event(0x0002, 0, 0, 0, UIntPtr.Zero); // LEFTDOWN
    System.Threading.Thread.Sleep(150);
    for (int i = 1; i <= steps; i++) {
      int x = fromX + (toX - fromX) * i / steps;
      int y = fromY + (toY - fromY) * i / steps;
      SetCursorPos(x, y);
      System.Threading.Thread.Sleep(90);
    }
    System.Threading.Thread.Sleep(250);
    mouse_event(0x0004, 0, 0, 0, UIntPtr.Zero); // LEFTUP
    return "dragged " + fromX + "," + fromY + " -> " + toX + "," + toY;
  }
}
'@
Add-Type -TypeDefinition $cs -ErrorAction Stop
Add-Type -AssemblyName System.Drawing

function Capture([int]$x, [int]$y, [int]$w, [int]$h, [string]$file) {
  $bmp = New-Object System.Drawing.Bitmap $w, $h
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen($x, $y, 0, 0, (New-Object System.Drawing.Size $w, $h))
  $g.Dispose(); $bmp.Save($file, [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
  return [pscustomobject]@{ file = (Split-Path $file -Leaf); width = $w; height = $h; sha256 = (Get-FileHash -Algorithm SHA256 -Path $file).Hash.ToLowerInvariant() }
}

function Get-Displays {
  $probe = Join-Path $PSScriptRoot 'probe-displays.ps1'
  $null = & pwsh -NoProfile -File $probe -OutDir $OutDir -Label 'drag' 2>&1
  $latest = Get-ChildItem $OutDir -Filter 'displays-drag-*.json' | Sort-Object LastWriteTime | Select-Object -Last 1
  if (-not $latest) { throw 'display probe failed' }
  Get-Content -Raw -Path $latest.FullName | ConvertFrom-Json
}
function Test-Contained($r, $m) {
  ($r.left -ge $m.left) -and ($r.top -ge $m.top) -and (($r.left + $r.width) -le ($m.left + $m.width)) -and (($r.top + $r.height) -le ($m.top + $m.height))
}

$disp = Get-Displays
$mon1 = $disp.displays | Where-Object { $_.primary } | Select-Object -First 1
$mon2 = $disp.displays | Where-Object { -not $_.primary } | Select-Object -First 1

$root = Join-Path $env:TEMP ("nm-fea07-drag-{0}" -f $stamp)
$dataRoot = Join-Path $root 'data'; $logDir = Join-Path $root 'logs'; $themeHome = Join-Path $root 'theme'
New-Item -ItemType Directory -Force -Path $dataRoot, $logDir, $themeHome | Out-Null
$exe = Join-Path $repo 'apps\desktop-avalonia\src\NewManga.App\bin\Release\net9.0\NewManga.App.exe'
$appArgs = @('--data-root', $dataRoot, '--log-dir', $logDir, '--theme-home', $themeHome, '--shell=v2')
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $exe; $psi.WorkingDirectory = (Split-Path $exe -Parent); $psi.UseShellExecute = $false; $psi.CreateNoWindow = $true
foreach ($a in $appArgs) { $psi.ArgumentList.Add($a) }
$proc = [System.Diagnostics.Process]::Start($psi)
Write-Host "launched pid=$($proc.Id)"

$main = [IntPtr]::Zero
for ($i = 0; $i -lt 40; $i++) {
  Start-Sleep -Milliseconds 500
  $main = [DragApi]::MainWindowOf([uint32]$proc.Id)
  if ($main -ne [IntPtr]::Zero) { break }
}
if ($main -eq [IntPtr]::Zero) { throw 'main window not found' }

$steps = @()
function Record($step) {
  $parts = ([DragApi]::Rect($main)) -split '\|'
  $r = [pscustomobject]@{ left = [int]$parts[0]; top = [int]$parts[1]; width = [int]$parts[2]; height = [int]$parts[3]; dpi = [int]$parts[4]; scalePercent = [int]$parts[5] }
  [pscustomobject]@{ step = $step; left = $r.left; top = $r.top; width = $r.width; height = $r.height; dpi = $r.dpi; scalePercent = $r.scalePercent; right = $r.left + $r.width; bottom = $r.top + $r.height; cursor = $cursorText }
}

# 1) put on mon1, size to ~55% of mon1 work area (physical)
$w = [int]($mon1.width * 0.55); $h = [int]($mon1.height * 0.55)
$x = $mon1.left + [int](($mon1.width - $w) / 2); $y = $mon1.top + 120
[DragApi]::SetWindowPos($main, [IntPtr]::Zero, $x, $y, $w, $h, 0x0004) | Out-Null
Start-Sleep -Milliseconds $SettleMs
$cursorText = 'none'
$steps += Record 'placed-mon1'
$shot1 = Capture $mon1.left $mon1.top $mon1.width $mon1.height (Join-Path $shots ("{0}-drag-mon1.png" -f $stamp))

# 2) real mouse drag: grab title bar, drag to mon2 center
[DragApi]::SetForegroundWindow($main) | Out-Null
Start-Sleep -Milliseconds 300
$grabX = $x + [int]($w / 2); $grabY = $y + 14
$targetX = $mon2.left + [int]($mon2.width / 2); $targetY = $mon2.top + 300
$dragInfo = [DragApi]::Drag($grabX, $grabY, $targetX, $targetY, 24)
$cursorText = "drag $grabX,$grabY -> $targetX,$targetY"
Start-Sleep -Milliseconds ($SettleMs + 600)
$steps += Record 'after-drag'
$shot2 = Capture $mon2.left $mon2.top $mon2.width $mon2.height (Join-Path $shots ("{0}-drag-mon2.png" -f $stamp))

$doc = [ordered]@{
  case = 'drag-mixed-dpi'
  capturedAt = (Get-Date -Format o)
  app = [ordered]@{ exe = $exe; pid = $proc.Id; args = $appArgs }
  monitors = [ordered]@{ primary = $mon1; secondary = $mon2 }
  steps = $steps
  containment = [ordered]@{
    'placed-mon1' = (Test-Contained $steps[0] $mon1)
    'after-drag' = (Test-Contained $steps[1] $mon2)
  }
  drag = $dragInfo
  screenshots = @($shot1, $shot2)
}
$out = Join-Path $OutDir ("drag-mixed-dpi-{0}.json" -f $stamp)
$doc | ConvertTo-Json -Depth 8 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
$steps | ForEach-Object { "step={0} rect=({1},{2}) {3}x{4} dpi={5} scale={6}% contained-primary={7} contained-secondary={8}" -f $_.step,$_.left,$_.top,$_.width,$_.height,$_.dpi,$_.scalePercent,(Test-Contained $_ $mon1),(Test-Contained $_ $mon2) }

if (-not $KeepRunning) {
  [DragApi]::ShowWindow($main, 6) | Out-Null
  Start-Sleep -Milliseconds 400
  if (-not $proc.HasExited) { $proc.Kill($true); $proc.WaitForExit(5000) | Out-Null }
  Write-Host 'app closed'
}
