# FEA-07-AC5-NATIVE-1 / probe-f11.ps1
# 单次 F11 + 200ms 轮询所有顶层窗口（不只是标题匹配），捕获沉浸 ReaderWindow 并采样，再关闭退出。
[CmdletBinding()]
param([string]$OutDir = "", [string]$ShotDir = "G:\CODEX\New Manga.workspace\FEA-07-AC5-NATIVE-1\ac5-fullscreen")
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-AC5-NATIVE-1\evidence' }
New-Item -ItemType Directory -Force -Path $OutDir, $ShotDir | Out-Null
Add-Type -AssemblyName System.Windows.Forms, System.Drawing

$cs = @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
public static class F11Probe {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int left, top, right, bottom; }
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern int GetWindowLongW(IntPtr h, int i);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, UIntPtr e);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassNameW(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr v);
  public static string[] Visible(uint pid) {
    SetProcessDpiAwarenessContext(new IntPtr(-4));
    var list = new List<string>();
    EnumWindows((h,l) => {
      uint p; GetWindowThreadProcessId(h, out p);
      if (p != pid || !IsWindowVisible(h)) return true;
      var t = new StringBuilder(200); GetWindowTextW(h,t,200);
      var c = new StringBuilder(200); GetClassNameW(h,c,200);
      RECT r; GetWindowRect(h, out r);
      int style = GetWindowLongW(h, -16);
      bool caption = (style & 0x00C00000) == 0x00C00000;
      list.Add(string.Format("{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}|{8}", h, r.left, r.top, r.right-r.left, r.bottom-r.top, caption?1:0, t, c, 0));
      return true;
    }, IntPtr.Zero);
    return list.ToArray();
  }
  public static void Click(int x, int y) { SetCursorPos(x,y); System.Threading.Thread.Sleep(150); mouse_event(0x0002,0,0,0,UIntPtr.Zero); System.Threading.Thread.Sleep(90); mouse_event(0x0004,0,0,0,UIntPtr.Zero); }
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
$pid2 = $app.Id
$before = [F11Probe]::Visible([uint32]$pid2)
Write-Host "before windows: $($before.Count)"
$before | ForEach-Object { Write-Host "  $_" }

$main = $null
foreach ($line in $before) { $p = $line -split '\|',9; if ($p[6] -eq 'New Manga') { $main = $p } }
if (-not $main) { throw 'main window not found' }
[F11Probe]::SetForegroundWindow([IntPtr][int64]$main[0]) | Out-Null
Start-Sleep -Milliseconds 500
# 点击画面中心离开文本框焦点
$cx = [int]$main[1] + [int]([int]$main[3] * 0.5)
$cy = [int]$main[2] + [int]([int]$main[4] * 0.55)
[F11Probe]::Click($cx, $cy)
Start-Sleep -Milliseconds 800
Write-Host "clicked canvas at $cx,$cy"
[System.Windows.Forms.SendKeys]::SendWait('{F11}')

$found = $null; $samples = @()
for ($i = 0; $i -lt 30; $i++) {
  Start-Sleep -Milliseconds 200
  $now = [F11Probe]::Visible([uint32]$pid2)
  $samples += ,@($now)
  foreach ($line in $now) {
    $p = $line -split '\|',9
    if ($p[6] -ne 'New Manga') { $found = $p; break }
  }
  if ($found) { break }
}
$shotFs = $null
if ($found) {
  $shotFs = Capture 'f11-immersive'
  Write-Host ("FOUND immersive: hwnd={0} rect=({1},{2}) {3}x{4} caption={5} title={6}" -f $found[0],$found[1],$found[2],$found[3],$found[4],$found[5],$found[6])
  # 关闭：F11
  [F11Probe]::SetForegroundWindow([IntPtr][int64]$found[0]) | Out-Null
  Start-Sleep -Milliseconds 400
  [System.Windows.Forms.SendKeys]::SendWait('{F11}')
  Start-Sleep -Milliseconds 1800
  $after = [F11Probe]::Visible([uint32]$pid2)
  $still = @($after | Where-Object { ($_ -split '\|',9)[6] -ne 'New Manga' }).Count
  Write-Host "after F11 close: extraWindows=$still"
} else {
  Write-Host 'NOT FOUND after 6s polling'
  $shotFs = Capture 'f11-notfound'
}
$doc = [ordered]@{
  case='probe-f11'; capturedAt=(Get-Date -Format o); pid=$pid2
  beforeWindows=$before; found=($null -ne $found)
  immersive=if ($found) { [ordered]@{ hwnd=[int64]$found[0]; left=[int]([int64]$found[1]); top=[int]([int64]$found[2]); width=[int]([int64]$found[3]); height=[int]([int64]$found[4]); hasCaption=($found[5] -eq '1'); title=$found[6]; coversPrimary=(([int64]$found[1] -le 0) -and ([int64]$found[2] -le 0) -and ([int64]$found[3] -ge 2560) -and ([int64]$found[4] -ge 1440)) } } else { $null }
  screenshot=$shotFs
}
$out = Join-Path $OutDir ("probe-f11-{0}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$doc | ConvertTo-Json -Depth 6 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
