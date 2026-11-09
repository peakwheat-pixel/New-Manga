# FEA-07-AC5-NATIVE-1 / open-immersive-dblclick.ps1
# 在页面图像上的多个候选取点双击，检测是否出现沉浸 ReaderWindow；命中即抓证据。
[CmdletBinding()]
param([string]$OutDir = "", [string]$ShotDir = "G:\CODEX\New Manga.workspace\FEA-07-AC5-NATIVE-1\ac5-fullscreen")
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-AC5-NATIVE-1\evidence' }
New-Item -ItemType Directory -Force -Path $OutDir, $ShotDir | Out-Null
Add-Type -AssemblyName System.Drawing

$cs = @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
public static class Dbl {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int left, top, right, bottom; }
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern int GetWindowLongW(IntPtr h, int i);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, UIntPtr e);
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr v);
  public static string[] V(uint pid) {
    SetProcessDpiAwarenessContext(new IntPtr(-4));
    var l = new List<string>();
    EnumWindows((h,x) => {
      uint p; GetWindowThreadProcessId(h, out p);
      if (p != pid || !IsWindowVisible(h)) return true;
      var t=new StringBuilder(200); GetWindowTextW(h,t,200);
      RECT r; GetWindowRect(h,out r);
      int style = GetWindowLongW(h, -16);
      bool cap = (style & 0x00C00000) == 0x00C00000;
      l.Add(string.Format("{0}|{1}|{2}|{3}|{4}|{5}|{6}", h, r.left,r.top,r.right-r.left,r.bottom-r.top, cap?1:0, t));
      return true;
    }, IntPtr.Zero);
    return l.ToArray();
  }
  public static void DblClick(int x,int y) {
    SetCursorPos(x,y); System.Threading.Thread.Sleep(200);
    mouse_event(0x0002,0,0,0,UIntPtr.Zero); System.Threading.Thread.Sleep(40); mouse_event(0x0004,0,0,0,UIntPtr.Zero);
    System.Threading.Thread.Sleep(140);
    mouse_event(0x0002,0,0,0,UIntPtr.Zero); System.Threading.Thread.Sleep(40); mouse_event(0x0004,0,0,0,UIntPtr.Zero);
  }
}
'@
Add-Type -TypeDefinition $cs -ErrorAction Stop

function Capture($name) {
  $f = Join-Path $ShotDir ("{0}-{1}.png" -f (Get-Date -Format 'yyyyMMdd-HHmmss'), $name)
  $b = New-Object System.Drawing.Bitmap 2560,1440
  $g = [System.Drawing.Graphics]::FromImage($b); $g.CopyFromScreen(0,0,0,0,(New-Object System.Drawing.Size 2560,1440)); $g.Dispose()
  $b.Save($f, [System.Drawing.Imaging.ImageFormat]::Png); $b.Dispose()
  [pscustomobject]@{ file=$f; sha256=(Get-FileHash -Algorithm SHA256 -Path $f).Hash.ToLowerInvariant() }
}

$app = Get-Process NewManga.App | Sort-Object StartTime | Select-Object -Last 1
$pidApp = $app.Id
$wins = [Dbl]::V([uint32]$pidApp)
$main = $null
foreach ($l in $wins) { $p = $l -split '\|',7; if ($p[6] -eq 'New Manga') { $main = $p } }
if (-not $main) { throw 'main window not found' }
$left=[int]$main[1]; $top=[int]$main[2]; $w=[int]$main[3]; $h=[int]$main[4]
Write-Host "window: ($left,$top) ${w}x${h}"
[Dbl]::SetForegroundWindow([IntPtr][int64]$main[0]) | Out-Null
Start-Sleep -Milliseconds 600

$found = $null; $shot = $null; $attempts = @()
foreach ($fx in @(0.50, 0.45, 0.55)) {
  foreach ($fy in @(0.35, 0.45, 0.55, 0.30)) {
    $cx = $left + [int]($w * $fx); $cy = $top + [int]($h * $fy)
    [Dbl]::DblClick($cx, $cy)
    Start-Sleep -Milliseconds 900
    $now = [Dbl]::V([uint32]$pidApp)
    $extra = @($now | Where-Object { ($_ -split '\|',7)[6] -ne 'New Manga' })
    $attempts += [ordered]@{ x=$cx; y=$cy; extra=$extra.Count }
    if ($extra.Count -gt 0) {
      $p = $extra[0] -split '\|',7
      $found = [ordered]@{ hwnd=[int64]$p[0]; left=[int]([int64]$p[1]); top=[int]([int64]$p[2]); width=[int]([int64]$p[3]); height=[int]([int64]$p[4]); hasCaption=($p[5] -eq '1'); title=$p[6]; coversPrimary=(([int64]$p[1] -le 0) -and ([int64]$p[2] -le 0) -and ([int64]$p[3] -ge 2560) -and ([int64]$p[4] -ge 1440)) }
      $shot = Capture 'dblclick-immersive'
      break
    }
  }
  if ($found) { break }
}
$doc = [ordered]@{ action='open-immersive-dblclick'; capturedAt=(Get-Date -Format o); pid=$pidApp; window=$main; attempts=$attempts; found=($null -ne $found); immersive=$found; screenshot=$shot }
$out = Join-Path $OutDir ("dblclick-immersive-{0}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$doc | ConvertTo-Json -Depth 6 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
if ($found) { Write-Host ("IMMERSIVE rect=({0},{1}) {2}x{3} caption={4} title={5} covers={6}" -f $found.left,$found.top,$found.width,$found.height,$found.hasCaption,$found.title,$found.coversPrimary) } else { Write-Host 'immersive NOT found by double-click sweep' }
