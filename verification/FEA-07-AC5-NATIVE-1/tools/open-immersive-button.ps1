# FEA-07-AC5-NATIVE-1 / open-immersive-button.ps1
# 用 Reader 页「沉浸模式 (Esc/H/F)」按钮打开沉浸 ReaderWindow，采样几何/样式/截图，Esc 关闭并校验恢复。
[CmdletBinding()]
param([string]$OutDir = "", [string]$ShotDir = "G:\CODEX\New Manga.workspace\FEA-07-AC5-NATIVE-1\ac5-fullscreen")
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-AC5-NATIVE-1\evidence' }
New-Item -ItemType Directory -Force -Path $OutDir, $ShotDir | Out-Null
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes, System.Windows.Forms, System.Drawing

$cs = @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
public static class ImmBtn {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int left, top, right, bottom; }
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern int GetWindowLongW(IntPtr h, int i);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
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
function UiaMain($procId) {
  $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ProcessIdProperty, $procId)
  $wins = [System.Windows.Automation.AutomationElement]::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children, $cond)
  foreach ($w in $wins) { if ($w.Current.ControlType -eq [System.Windows.Automation.ControlType]::Window -and $w.Current.Name -eq 'New Manga') { return $w } }
  return $null
}
function Find-ByNamePart($root, [string]$part) {
  $bc = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Button)
  $els = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, $bc)
  foreach ($e in $els) { if ($e.Current.Name -and $e.Current.Name.StartsWith($part)) { return $e } }
  return $null
}
function Invoke-El($el) { try { ($el.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)).Invoke(); return $true } catch { return $false } }

$app = Get-Process NewManga.App | Sort-Object StartTime | Select-Object -Last 1
$pidApp = $app.Id
$win = UiaMain $pidApp
if (-not $win) { throw 'UIA main window not found' }

# 确保在 reader 页：依次找 打开作品/打开章节/阅读（存在就点）
foreach ($n in @('打开作品：', '打开章节：')) {
  $bc = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Button)
  $els = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, $bc)
  foreach ($e in $els) { if ($e.Current.Name -and $e.Current.Name.StartsWith($n)) { Invoke-El $e | Out-Null; Start-Sleep -Milliseconds 1500; break } }
}
$read = Find-ByNamePart $win '阅读'
if ($read) { Invoke-El $read | Out-Null; Start-Sleep -Milliseconds 2500 }
$win = UiaMain $pidApp

$imm = Find-ByNamePart $win '沉浸模式'
if (-not $imm) { Write-Host 'immersive button not found'; throw 'immersive button missing (reader page not loaded?)' }
Write-Host "found button: $($imm.Current.Name)"
$ok = Invoke-El $imm
Write-Host "invoked=$ok"

$found = $null
for ($i = 0; $i -lt 40; $i++) {
  Start-Sleep -Milliseconds 150
  $now = [ImmBtn]::V([uint32]$pidApp)
  foreach ($l in $now) { $p = $l -split '\|',7; if ($p[6] -ne 'New Manga') { $found = $p; break } }
  if ($found) { break }
}
$shot = $null
if ($found) {
  $shot = Capture 'immersive-button'
  Write-Host ("IMMERSIVE: hwnd={0} rect=({1},{2}) {3}x{4} caption={5} title={6}" -f $found[0],$found[1],$found[2],$found[3],$found[4],$found[5],$found[6])
  # Esc 关闭
  [ImmBtn]::SetForegroundWindow([IntPtr][int64]$found[0]) | Out-Null
  Start-Sleep -Milliseconds 500
  [System.Windows.Forms.SendKeys]::SendWait('{ESC}')
  Start-Sleep -Milliseconds 1800
  $after = [ImmBtn]::V([uint32]$pidApp)
  $extra = @($after | Where-Object { ($_ -split '\|',7)[6] -ne 'New Manga' }).Count
  Write-Host "after ESC extraWindows=$extra"
} else { Write-Host 'immersive window NOT found after button invoke' }
$doc = [ordered]@{
  action='open-immersive-button'; capturedAt=(Get-Date -Format o); pid=$pidApp
  buttonFound=$true; buttonName=$imm.Current.Name; invoked=$ok; found=($null -ne $found)
  immersive=if ($found) { [ordered]@{ hwnd=[int64]$found[0]; left=[int]([int64]$found[1]); top=[int]([int64]$found[2]); width=[int]([int64]$found[3]); height=[int]([int64]$found[4]); hasCaption=($found[5] -eq '1'); title=$found[6]; coversPrimary=(([int64]$found[1] -le 0) -and ([int64]$found[2] -le 0) -and ([int64]$found[3] -ge 2560) -and ([int64]$found[4] -ge 1440)) } } else { $null }
  screenshot=$shot
}
$out = Join-Path $OutDir ("immersive-button-{0}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$doc | ConvertTo-Json -Depth 6 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
