# FEA-07-AC5-NATIVE-1 / inspect-import-dialog.ps1
# 读取当前 NewManga.App 的「导入文件夹」对话框 UIA 结构（含所有顶层窗口，按 pid 枚举 + FromHandle）。
[CmdletBinding()]
param([string]$OutDir = "")
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-AC5-NATIVE-1\evidence' }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes

$cs = @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
public static class DlgWins {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int left, top, right, bottom; }
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassNameW(IntPtr h, StringBuilder s, int n);
  public static string[] Of(uint pid) {
    var list = new List<string>();
    EnumWindows((h,l) => {
      uint p; GetWindowThreadProcessId(h, out p);
      if (p != pid || !IsWindowVisible(h)) return true;
      var t = new StringBuilder(300); GetWindowTextW(h,t,300);
      var c = new StringBuilder(300); GetClassNameW(h,c,300);
      RECT r; GetWindowRect(h, out r);
      list.Add(string.Format("{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}", h, r.left, r.top, r.right-r.left, r.bottom-r.top, c, t, IsWindowVisible(h)));
      return true;
    }, IntPtr.Zero);
    return list.ToArray();
  }
}
'@
Add-Type -TypeDefinition $cs -ErrorAction Stop
$app = Get-Process NewManga.App -ErrorAction SilentlyContinue | Sort-Object StartTime | Select-Object -Last 1
if (-not $app) { throw 'NewManga.App not running' }
Write-Host "app pid=$($app.Id)"
$rows = @()
foreach ($line in [DlgWins]::Of([uint32]$app.Id)) {
  $p = $line -split '\|', 8
  Write-Host ("hwnd={0} rect=({1},{2}) {3}x{4} class={5} title={6}" -f $p[0],$p[1],$p[2],$p[3],$p[4],$p[5],$p[6])
  try { $el = [System.Windows.Automation.AutomationElement]::FromHandle([IntPtr][int64]$p[0]) } catch { continue }
  if (-not $el) { continue }
  $rows += [pscustomobject]@{ hwnd = $p[0]; title = $p[6]; rect = "$($p[1]),$($p[2]) $($p[3])x$($p[4])"; kind = 'window' }
  foreach ($ct in @([System.Windows.Automation.ControlType]::Button, [System.Windows.Automation.ControlType]::Edit, [System.Windows.Automation.ControlType]::ListItem, [System.Windows.Automation.ControlType]::Text, [System.Windows.Automation.ControlType]::ComboBox, [System.Windows.Automation.ControlType]::Tree, [System.Windows.Automation.ControlType]::TreeItem)) {
    $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, $ct)
    $els = $el.FindAll([System.Windows.Automation.TreeScope]::Descendants, $cond)
    foreach ($e in $els) {
      $rows += [pscustomobject]@{ hwnd = $p[0]; title = $p[6]; rect = "-"; kind = $ct.ProgrammaticName.Replace('ControlType.',''); name = $e.Current.Name; id = $e.Current.AutomationId }
    }
  }
}
$out = Join-Path $OutDir ("import-dialog-uia-{0}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$rows | ConvertTo-Json -Depth 4 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
$rows | Where-Object { $_.name } | Select-Object -First 50 | Format-Table -AutoSize | Out-String -Width 200 | Write-Host
