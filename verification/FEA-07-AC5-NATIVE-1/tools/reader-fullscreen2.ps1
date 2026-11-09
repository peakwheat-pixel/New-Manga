# FEA-07-AC5-NATIVE-1 / reader-fullscreen2.ps1
# 正确路径：Reader 页 → 应用级 F11 打开沉浸 ReaderWindow（FullScreen/无边框）→ 采样+截图 → F11/Esc 关闭 → 校验主窗恢复。
[CmdletBinding()]
param(
  [int]$ProcessId = 0,
  [string]$OutDir = "",
  [string]$ShotDir = "G:\CODEX\New Manga.workspace\FEA-07-AC5-NATIVE-1\ac5-fullscreen"
)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-AC5-NATIVE-1\evidence' }
New-Item -ItemType Directory -Force -Path $OutDir, $ShotDir | Out-Null
Add-Type -AssemblyName System.Windows.Forms, System.Drawing

if ($ProcessId -le 0) {
  $p = Get-Process NewManga.App -ErrorAction SilentlyContinue | Sort-Object StartTime | Select-Object -Last 1
  if (-not $p) { throw 'app not running' }
  $ProcessId = $p.Id
}
Write-Host "app pid=$ProcessId"

$cs = @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
public static class FsApi2 {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int left, top, right, bottom; }
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool IsZoomed(IntPtr h);
  [DllImport("user32.dll")] public static extern int GetWindowLongW(IntPtr h, int index);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr v);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassNameW(IntPtr h, StringBuilder s, int n);
  public static string[] Windows(uint pid) {
    SetProcessDpiAwarenessContext(new IntPtr(-4));
    var rows = new List<string>();
    EnumWindows((h, l) => {
      uint p; GetWindowThreadProcessId(h, out p);
      if (p != pid || !IsWindowVisible(h)) return true;
      var t = new StringBuilder(200); GetWindowTextW(h, t, 200);
      var c = new StringBuilder(200); GetClassNameW(h, c, 200);
      RECT r; GetWindowRect(h, out r);
      int style = GetWindowLongW(h, -16);
      bool caption = (style & 0x00C00000) == 0x00C00000;
      rows.Add(string.Format("{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}|{8}", h, r.left, r.top, r.right - r.left, r.bottom - r.top, IsZoomed(h) ? 1 : 0, caption ? 1 : 0, t, c, 0));
      return true;
    }, IntPtr.Zero);
    return rows.ToArray();
  }
  public static IntPtr Find(uint pid, string title) {
    IntPtr found = IntPtr.Zero;
    EnumWindows((h, l) => {
      uint p; GetWindowThreadProcessId(h, out p);
      if (p != pid || !IsWindowVisible(h)) return true;
      var t = new StringBuilder(200); GetWindowTextW(h, t, 200);
      RECT r; GetWindowRect(h, out r);
      if (t.ToString() == title && r.right - r.left > 200) { found = h; return false; }
      return true;
    }, IntPtr.Zero);
    return found;
  }
  public static string Info(IntPtr h) {
    RECT r; GetWindowRect(h, out r);
    int style = GetWindowLongW(h, -16);
    bool caption = (style & 0x00C00000) == 0x00C00000;
    return string.Format("{0}|{1}|{2}|{3}|{4}|{5}", r.left, r.top, r.right - r.left, r.bottom - r.top, IsZoomed(h) ? 1 : 0, caption ? 1 : 0);
  }
}
'@
Add-Type -TypeDefinition $cs -ErrorAction Stop

function Capture($name) {
  $f = Join-Path $ShotDir ("{0}-{1}.png" -f (Get-Date -Format 'yyyyMMdd-HHmmss'), $name)
  $b = New-Object System.Drawing.Bitmap 2560, 1440
  $g = [System.Drawing.Graphics]::FromImage($b); $g.CopyFromScreen(0, 0, 0, 0, (New-Object System.Drawing.Size 2560, 1440)); $g.Dispose()
  $b.Save($f, [System.Drawing.Imaging.ImageFormat]::Png); $b.Dispose()
  return [pscustomobject]@{ file = $f; sha256 = (Get-FileHash -Algorithm SHA256 -Path $f).Hash.ToLowerInvariant() }
}
function Fg($h) { [FsApi2]::SetForegroundWindow($h) | Out-Null; Start-Sleep -Milliseconds 500 }

$main = [FsApi2]::Find([uint32]$ProcessId, 'New Manga')
if ($main -eq [IntPtr]::Zero) { throw 'main window not found' }
Fg $main
$before = ([FsApi2]::Info($main)) -split '\|'
# 让焦点离开文本输入（否则 F11 被忽略）：点击窗口内容区中心
$cx = [int]$before[0] + [int]([int]$before[2] * 0.5)
$cy = [int]$before[1] + [int]([int]$before[3] * 0.55)
$sigClick = @'
using System;
using System.Runtime.InteropServices;
public static class ClickFs {
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, UIntPtr e);
  public static void Do(int x, int y) {
    SetCursorPos(x, y); System.Threading.Thread.Sleep(150);
    mouse_event(0x0002, 0, 0, 0, UIntPtr.Zero); System.Threading.Thread.Sleep(90);
    mouse_event(0x0004, 0, 0, 0, UIntPtr.Zero);
  }
}
'@
Add-Type -TypeDefinition $sigClick
[ClickFs]::Do($cx, $cy)
Start-Sleep -Milliseconds 700
$shotBefore = Capture 'fs2-before'
Write-Host ("main before: rect=({0},{1}) {2}x{3} zoomed={4} caption={5}" -f $before[0],$before[1],$before[2],$before[3],$before[4],$before[5])

# 应用级 F11 → 沉浸 ReaderWindow
[System.Windows.Forms.SendKeys]::SendWait('{F11}')
Start-Sleep -Milliseconds 2500
$reader = [FsApi2]::Find([uint32]$ProcessId, '阅读器')
if ($reader -eq [IntPtr]::Zero) {
  Start-Sleep -Milliseconds 1500
  $reader = [FsApi2]::Find([uint32]$ProcessId, '阅读器')
}
if ($reader -eq [IntPtr]::Zero) {
  Write-Host 'reader window NOT found; windows:'
  [FsApi2]::Windows([uint32]$ProcessId) | ForEach-Object { Write-Host "  $_" }
  throw 'immersive reader window not opened by F11'
}
$fs = ([FsApi2]::Info($reader)) -split '\|'
$shotFs = Capture 'fs2-fullscreen'
Write-Host ("reader: rect=({0},{1}) {2}x{3} zoomed={4} caption={5}" -f $fs[0],$fs[1],$fs[2],$fs[3],$fs[4],$fs[5])

# 关闭：F11（沉浸窗口内）
Fg $reader
[System.Windows.Forms.SendKeys]::SendWait('{F11}')
Start-Sleep -Milliseconds 2000
$readerGone = ([FsApi2]::Find([uint32]$ProcessId, '阅读器')) -eq [IntPtr]::Zero
$after = ([FsApi2]::Info($main)) -split '\|'
$shotAfter = Capture 'fs2-after-close'
Write-Host ("readerClosed={0} main after: rect=({1},{2}) {3}x{4} zoomed={5}" -f $readerGone,$after[0],$after[1],$after[2],$after[3],$after[4])

$doc = [ordered]@{
  case = 'reader-fullscreen-f11'; capturedAt = (Get-Date -Format o); pid = $ProcessId
  before = [ordered]@{ left=[int]$before[0]; top=[int]$before[1]; width=[int]$before[2]; height=[int]$before[3]; zoomed=($before[4]-eq'1'); hasCaption=($before[5]-eq'1') }
  immersive = [ordered]@{ found=$true; left=[int]$fs[0]; top=[int]$fs[1]; width=[int]$fs[2]; height=[int]$fs[3]; zoomed=($fs[4]-eq'1'); hasCaption=($fs[5]-eq'1'); coversPrimary=(($fs[0] -le 0) -and ($fs[1] -le 0) -and (([int]$fs[2]) -ge 2560) -and (([int]$fs[3]) -ge 1440)) }
  afterClose = [ordered]@{ readerClosed=$readerGone; left=[int]$after[0]; top=[int]$after[1]; width=[int]$after[2]; height=[int]$after[3]; zoomed=($after[4]-eq'1') }
  screenshots = @(
    [ordered]@{ step='before'; shot=$shotBefore.file; sha256=$shotBefore.sha256; note='contains user manga content; kept outside repo' },
    [ordered]@{ step='fullscreen'; shot=$shotFs.file; sha256=$shotFs.sha256; note='same' },
    [ordered]@{ step='after-close'; shot=$shotAfter.file; sha256=$shotAfter.sha256; note='same' }
  )
}
$out = Join-Path $OutDir ("reader-fullscreen-f11-{0}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$doc | ConvertTo-Json -Depth 6 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
