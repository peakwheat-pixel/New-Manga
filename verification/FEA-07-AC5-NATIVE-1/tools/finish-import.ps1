# FEA-07-AC5-NATIVE-1 / finish-import.ps1
# 关闭错误框 → Invoke 选择框的「选择文件夹」→ 依次 Invoke 导入向导按钮 → 观察 wire import。
[CmdletBinding()]
param([string]$OutDir = "")
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-AC5-NATIVE-1\evidence' }
$shots = Join-Path $OutDir 'screenshots'; New-Item -ItemType Directory -Force -Path $OutDir, $shots | Out-Null
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes, System.Windows.Forms, System.Drawing

$cs = @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
public static class Fin {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int left, top, right, bottom; }
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassNameW(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  public static string[] Visible() {
    var list = new List<string>();
    EnumWindows((h,l) => {
      if (!IsWindowVisible(h)) return true;
      var c = new StringBuilder(200); GetClassNameW(h,c,200);
      var t = new StringBuilder(300); GetWindowTextW(h,t,300);
      RECT r; GetWindowRect(h, out r);
      list.Add(string.Format("{0}|{1}|{2}|{3}|{4}|{5}", h, c, r.left, r.top, r.right-r.left, t));
      return true;
    }, IntPtr.Zero);
    return list.ToArray();
  }
}
'@
Add-Type -TypeDefinition $cs -ErrorAction Stop

function Capture($name) {
  $f = Join-Path $shots ("{0}-{1}.png" -f (Get-Date -Format 'yyyyMMdd-HHmmss'), $name)
  $b = New-Object System.Drawing.Bitmap 2560, 1440
  $g = [System.Drawing.Graphics]::FromImage($b); $g.CopyFromScreen(0,0,0,0,(New-Object System.Drawing.Size 2560,1440)); $g.Dispose()
  $b.Save($f, [System.Drawing.Imaging.ImageFormat]::Png); $b.Dispose()
  return $f
}
function Find-WindowByTitlePart([string]$part) {
  foreach ($line in [Fin]::Visible()) {
    $p = $line -split '\|', 6
    if ($p[5] -match $part) { return $p }
  }
  return $null
}
function Invoke-ByName($root, [string]$name) {
  $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $name)
  $el = $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $cond)
  if (-not $el) { return $false }
  try { ($el.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)).Invoke(); return $true } catch { return $false }
}
function UiaFromHwnd([string]$hwnd) { return [System.Windows.Automation.AutomationElement]::FromHandle([IntPtr][int64]$hwnd) }
function UiaAppWindow($procId) {
  $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ProcessIdProperty, $procId)
  $wins = [System.Windows.Automation.AutomationElement]::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children, $cond)
  foreach ($w in $wins) { if ($w.Current.ControlType -eq [System.Windows.Automation.ControlType]::Window -and $w.Current.Name -eq 'New Manga') { return $w } }
  return $null
}

$app = Get-Process NewManga.App -ErrorAction SilentlyContinue | Sort-Object StartTime | Select-Object -Last 1
if (-not $app) { throw 'app not running' }

# 1) 关闭“找不到”错误框（标题含 文件资源管理器，或按钮“确定”）
$err = Find-WindowByTitlePart '文件资源管理器'
if ($err) {
  Write-Host "error dialog: hwnd=$($err[0]) title=$($err[5])"
  [Fin]::SetForegroundWindow([IntPtr][int64]$err[0]) | Out-Null
  Start-Sleep -Milliseconds 400
  [System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
  Start-Sleep -Milliseconds 900
}
$shot1 = Capture 'finish-after-error'

# 2) 选择框：Invoke「选择文件夹」
$dlg = Find-WindowByTitlePart '导入文件夹'
if ($dlg) {
  Write-Host "picker: hwnd=$($dlg[0])"
  $root = UiaFromHwnd $dlg[0]
  $ok = $false
  foreach ($n in @('选择文件夹', '确定', '选择')) { if (Invoke-ByName $root $n) { $ok = $true; Write-Host "invoked picker button: $n"; break } }
  if (-not $ok) {
    [Fin]::SetForegroundWindow([IntPtr][int64]$dlg[0]) | Out-Null
    Start-Sleep -Milliseconds 400
    [System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
    Write-Host "sent ENTER to picker"
  }
  Start-Sleep -Milliseconds 3000
}
$shot2 = Capture 'finish-after-pick'

# 3) 导入向导：依次 Invoke
$win = UiaAppWindow $app.Id
$clicked = @()
foreach ($n in @('选择目录并预览', '选择源并预览', '开始导入', '确认导入')) {
  if (Invoke-ByName $win $n) { $clicked += $n; Write-Host "invoked: $n"; Start-Sleep -Milliseconds 3500; $s = Capture ("finish-wizard-" + $clicked.Count) }
}
Start-Sleep -Milliseconds 5000
$shot3 = Capture 'finish-final'

$doc = [ordered]@{ action='finish-import'; capturedAt=(Get-Date -Format o); clicked=$clicked; screenshots=@($shot1,$shot2,$shot3) }
$out = Join-Path $OutDir ("finish-import-{0}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$doc | ConvertTo-Json -Depth 5 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"; Write-Host "clicked: $($clicked -join ' -> ')"
