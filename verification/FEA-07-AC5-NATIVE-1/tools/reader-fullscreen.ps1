# FEA-07-AC5-NATIVE-1 / reader-fullscreen.ps1
# 对已运行的 Host-ready 应用：打开作品→章节→阅读器→按 F 进入全屏→Esc 退出，记录窗口几何/样式与截图（截图存仓外）。
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
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes, System.Windows.Forms, System.Drawing

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
public static class FsApi {
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
  [DllImport("user32.dll")] public static extern IntPtr MonitorFromWindow(IntPtr h, uint flags);
  [DllImport("shcore.dll")] public static extern int GetDpiForMonitor(IntPtr h, int t, out uint dx, out uint dy);
  public static IntPtr Main(uint pid) {
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
  public static string Info(IntPtr h) {
    RECT r; GetWindowRect(h, out r);
    int style = GetWindowLongW(h, -16);
    bool caption = (style & 0x00C00000) == 0x00C00000;
    bool thickframe = (style & 0x00040000) != 0;
    uint dx = 0, dy = 0; IntPtr mon = MonitorFromWindow(h, 2); if (mon != IntPtr.Zero) GetDpiForMonitor(mon, 0, out dx, out dy);
    return string.Format("{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}|{8}", r.left, r.top, r.right - r.left, r.bottom - r.top, IsZoomed(h) ? 1 : 0, caption ? 1 : 0, thickframe ? 1 : 0, dx, Math.Round(dx / 96.0 * 100));
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
function UiaAppWindow($procId) {
  $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ProcessIdProperty, $procId)
  $wins = [System.Windows.Automation.AutomationElement]::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children, $cond)
  foreach ($w in $wins) { if ($w.Current.ControlType -eq [System.Windows.Automation.ControlType]::Window -and $w.Current.Name -eq 'New Manga') { return $w } }
  return $null
}
function Invoke-ByName($root, [string]$name) {
  $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $name)
  $el = $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $cond)
  if (-not $el) { return $false }
  try { ($el.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)).Invoke(); return $true } catch { try { $p = $el.GetClickablePoint(); [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point([int]$p.X,[int]$p.Y); return $true } catch { return $false } }
}

$main = [FsApi]::Main([uint32]$ProcessId)
if ($main -eq [IntPtr]::Zero) { throw 'main window not found' }
[FsApi]::SetForegroundWindow($main) | Out-Null
$win = UiaAppWindow $ProcessId
$steps = @()
foreach ($n in @('打开作品：测试', '打开章节：1', '阅读')) {
  if (-not $win) { break }
  if (Invoke-ByName $win $n) { $steps += $n; Write-Host "invoked: $n"; Start-Sleep -Milliseconds 2500 } else { Write-Host "not found: $n" }
}
Start-Sleep -Milliseconds 2500
$before = ([FsApi]::Info($main)) -split '\|'
$shotBefore = Capture 'reader-before'
Write-Host ("before: rect=({0},{1}) {2}x{3} zoomed={4} caption={5} dpi={6}" -f $before[0],$before[1],$before[2],$before[3],$before[4],$before[5],$before[7])

# F 全屏
[FsApi]::SetForegroundWindow($main) | Out-Null
Start-Sleep -Milliseconds 400
[System.Windows.Forms.SendKeys]::SendWait('f')
Start-Sleep -Milliseconds 1600
$fs = ([FsApi]::Info($main)) -split '\|'
$shotFs = Capture 'reader-fullscreen'
Write-Host ("fullscreen: rect=({0},{1}) {2}x{3} zoomed={4} caption={5} dpi={6}" -f $fs[0],$fs[1],$fs[2],$fs[3],$fs[4],$fs[5],$fs[7])

# Esc 退出
[System.Windows.Forms.SendKeys]::SendWait('{ESC}')
Start-Sleep -Milliseconds 1400
$ex = ([FsApi]::Info($main)) -split '\|'
$shotExit = Capture 'reader-after-esc'
Write-Host ("after esc: rect=({0},{1}) {2}x{3} zoomed={4} caption={5}" -f $ex[0],$ex[1],$ex[2],$ex[3],$ex[4],$ex[5])

$doc = [ordered]@{
  case = 'reader-fullscreen'; capturedAt = (Get-Date -Format o); pid = $ProcessId
  stepsClicked = $steps
  before = [ordered]@{ left=[int]$before[0]; top=[int]$before[1]; width=[int]$before[2]; height=[int]$before[3]; zoomed=($before[4]-eq'1'); hasCaption=($before[5]-eq'1'); dpi=[int]$before[7]; percent=[int]$before[8] }
  fullscreen = [ordered]@{ left=[int]$fs[0]; top=[int]$fs[1]; width=[int]$fs[2]; height=[int]$fs[3]; zoomed=($fs[4]-eq'1'); hasCaption=($fs[5]-eq'1'); dpi=[int]$fs[7]; percent=[int]$fs[8]; coversMonitor=(($fs[0] -le 0) -and ($fs[1] -le 0) -and (([int]$fs[2]) -ge 2560) -and (([int]$fs[3]) -ge 1440)) }
  afterEsc = [ordered]@{ left=[int]$ex[0]; top=[int]$ex[1]; width=[int]$ex[2]; height=[int]$ex[3]; zoomed=($ex[4]-eq'1'); hasCaption=($ex[5]-eq'1') }
  screenshots = @(
    [ordered]@{ step='before'; shot=$shotBefore.file; sha256=$shotBefore.sha256; note='contains user-provided manga content; kept outside repo' },
    [ordered]@{ step='fullscreen'; shot=$shotFs.file; sha256=$shotFs.sha256; note='same' },
    [ordered]@{ step='after-esc'; shot=$shotExit.file; sha256=$shotExit.sha256; note='same' }
  )
}
$out = Join-Path $OutDir ("reader-fullscreen-{0}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$doc | ConvertTo-Json -Depth 6 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out (screenshots outside repo: $ShotDir)"
