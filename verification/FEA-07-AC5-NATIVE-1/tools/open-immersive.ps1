# FEA-07-AC5-NATIVE-1 / open-immersive.ps1
# 通过双击读者页图像打开沉浸 ReaderWindow（免键盘焦点问题），采样窗口并截图。
[CmdletBinding()]
param([int]$ProcessId = 0, [string]$OutDir = "", [string]$ShotDir = "G:\CODEX\New Manga.workspace\FEA-07-AC5-NATIVE-1\ac5-fullscreen")
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-AC5-NATIVE-1\evidence' }
New-Item -ItemType Directory -Force -Path $OutDir, $ShotDir | Out-Null
Add-Type -AssemblyName System.Drawing

if ($ProcessId -le 0) { $p = Get-Process NewManga.App | Sort-Object StartTime | Select-Object -Last 1; $ProcessId = $p.Id }
$cs = @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
public static class Imm {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int left, top, right, bottom; }
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool IsZoomed(IntPtr h);
  [DllImport("user32.dll")] public static extern int GetWindowLongW(IntPtr h, int index);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, UIntPtr e);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr v);
  public static IntPtr Find(uint pid, string title) {
    SetProcessDpiAwarenessContext(new IntPtr(-4));
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
  public static void DoubleClick(int x, int y) {
    SetCursorPos(x, y); System.Threading.Thread.Sleep(200);
    mouse_event(0x0002, 0, 0, 0, UIntPtr.Zero); System.Threading.Thread.Sleep(40); mouse_event(0x0004, 0, 0, 0, UIntPtr.Zero);
    System.Threading.Thread.Sleep(120);
    mouse_event(0x0002, 0, 0, 0, UIntPtr.Zero); System.Threading.Thread.Sleep(40); mouse_event(0x0004, 0, 0, 0, UIntPtr.Zero);
  }
}
'@
Add-Type -TypeDefinition $cs -ErrorAction Stop

function Capture($name) {
  $f = Join-Path $ShotDir ("{0}-{1}.png" -f (Get-Date -Format 'yyyyMMdd-HHmmss'), $name)
  $b = New-Object System.Drawing.Bitmap 2560, 1440
  $g = [System.Drawing.Graphics]::FromImage($b); $g.CopyFromScreen(0, 0, 0, 0, (New-Object System.Drawing.Size 2560, 1440)); $g.Dispose()
  $b.Save($f, [System.Drawing.Imaging.ImageFormat]::Png); $b.Dispose()
  [pscustomobject]@{ file = $f; sha256 = (Get-FileHash -Algorithm SHA256 -Path $f).Hash.ToLowerInvariant() }
}

$main = [Imm]::Find([uint32]$ProcessId, 'New Manga')
if ($main -eq [IntPtr]::Zero) { throw 'main window not found' }
[Imm]::SetForegroundWindow($main) | Out-Null
Start-Sleep -Milliseconds 600
$b = ([Imm]::Info($main)) -split '\|'
$cx = [int]$b[0] + [int]([int]$b[2] * 0.5)
$cy = [int]$b[1] + [int]([int]$b[3] * 0.55)
[Imm]::DoubleClick($cx, $cy)
Start-Sleep -Milliseconds 2500

$reader = [Imm]::Find([uint32]$ProcessId, '阅读器')
if ($reader -eq [IntPtr]::Zero) {
  Start-Sleep -Milliseconds 1500
  $reader = [Imm]::Find([uint32]$ProcessId, '阅读器')
}
$shot = Capture 'immersive-open'
$doc = [ordered]@{ action='open-immersive'; capturedAt=(Get-Date -Format o); pid=$ProcessId; doubleClickAt=@($cx,$cy); found=($reader -ne [IntPtr]::Zero) }
if ($reader -ne [IntPtr]::Zero) {
  $r = ([Imm]::Info($reader)) -split '\|'
  $doc.immersive = [ordered]@{ left=[int]$r[0]; top=[int]$r[1]; width=[int]$r[2]; height=[int]$r[3]; zoomed=($r[4]-eq'1'); hasCaption=($r[5]-eq'1'); coversPrimary=(($r[0] -le 0) -and ($r[1] -le 0) -and (([int]$r[2]) -ge 2560) -and (([int]$r[3]) -ge 1440)) }
  Write-Host ("immersive: ({0},{1}) {2}x{3} zoomed={4} caption={5}" -f $r[0],$r[1],$r[2],$r[3],$r[4],$r[5])
} else { Write-Host 'immersive window NOT found after double-click' }
$doc.screenshot = $shot
$out = Join-Path $OutDir ("open-immersive-{0}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$doc | ConvertTo-Json -Depth 5 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
