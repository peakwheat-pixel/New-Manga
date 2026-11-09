# FEA-07-AC5-NATIVE-1 / set-scale-uia.ps1  (v2)
# 先选「显示器 N」，再设「缩放」= Percent。校验：探测所有屏 DPI，报告哪个变化。
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][int]$MonitorNumber,
  [Parameter(Mandatory = $true)][int]$Percent,
  [string]$OutDir = "",
  [int]$TimeoutSec = 25
)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-AC5-NATIVE-1\evidence' }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes

$cs = @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
public static class MonProbe {
  [StructLayout(LayoutKind.Sequential)] public struct POINT { public int x, y; }
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int left, top, right, bottom; }
  [StructLayout(LayoutKind.Sequential)] public struct MONITORINFO { public int cbSize; public RECT rcMonitor; public RECT rcWork; public int dwFlags; }
  [DllImport("user32.dll")] public static extern bool EnumDisplayMonitors(IntPtr hdc, IntPtr clip, EnumProc cb, IntPtr data);
  [DllImport("user32.dll")] public static extern bool GetMonitorInfo(IntPtr h, ref MONITORINFO mi);
  [DllImport("user32.dll")] public static extern IntPtr MonitorFromPoint(POINT pt, uint flags);
  [DllImport("shcore.dll")] public static extern int GetDpiForMonitor(IntPtr h, int t, out uint dx, out uint dy);
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr v);
  public delegate bool EnumProc(IntPtr h, IntPtr hdc, IntPtr lprc, IntPtr data);
  public static string[] All() {
    SetProcessDpiAwarenessContext(new IntPtr(-4));
    var rows = new List<string>();
    EnumDisplayMonitors(IntPtr.Zero, IntPtr.Zero, (h, d, l, x) => {
      var mi = new MONITORINFO(); mi.cbSize = Marshal.SizeOf(mi);
      if (!GetMonitorInfo(h, ref mi)) return true;
      uint dx = 0, dy = 0; GetDpiForMonitor(h, 0, out dx, out dy);
      rows.Add(string.Format("{0}|{1}|{2}|{3}|{4}|{5}", mi.rcMonitor.left, mi.rcMonitor.top, mi.rcMonitor.right, mi.rcMonitor.bottom, dx, Math.Round(dx / 96.0 * 100)));
      return true;
    }, IntPtr.Zero);
    return rows.ToArray();
  }
}
'@
if (-not ('MonProbe' -as [type])) { Add-Type -TypeDefinition $cs -ErrorAction Stop }

function Get-AllDpi {
  $r = @()
  foreach ($m in [MonProbe]::All()) {
    $p = $m -split '\|'
    $r += [pscustomobject]@{ left = [int]$p[0]; top = [int]$p[1]; width = [int]$p[2] - [int]$p[0]; height = [int]$p[3] - [int]$p[1]; dpi = [int]$p[4]; percent = [int]$p[5] }
  }
  return $r | Sort-Object left
}

$before = @(Get-AllDpi)
Write-Host ("before: " + (($before | ForEach-Object { "{0}x{1}@{2}%({3},{4})" -f $_.width,$_.height,$_.percent,$_.left,$_.top }) -join ' | '))

Get-Process SystemSettings -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 800
Start-Process 'ms-settings:display'
$win = $null
for ($i = 0; $i -lt ($TimeoutSec * 2); $i++) {
  Start-Sleep -Milliseconds 500
  $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Window)
  $wins = [System.Windows.Automation.AutomationElement]::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children, $cond)
  foreach ($w in $wins) { if ($w.Current.Name -match '设置|Settings') { $win = $w; break } }
  if ($win) { break }
}
if (-not $win) { throw 'settings window not found' }
$pageReady = $false
for ($i = 0; $i -lt 30; $i++) {
  Start-Sleep -Milliseconds 700
  $cbCond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::ComboBox)
  $cbs = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, $cbCond)
  foreach ($c in $cbs) { if ($c.Current.Name -eq '缩放') { $pageReady = $true; break } }
  if ($pageReady) { break }
}
if (-not $pageReady) { throw 'display page not ready (scale combo missing)' }

function Find-Item($root, [string]$name, $controlType) {
  $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, $controlType)
  $els = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, $cond)
  foreach ($e in $els) { if ($e.Current.Name -eq $name -and -not $e.Current.IsOffscreen) { return $e } }
  foreach ($e in $els) { if ($e.Current.Name -eq $name) { return $e } }
  return $null
}

$monName = "显示器 $MonitorNumber"
$mon = Find-Item $win $monName ([System.Windows.Automation.ControlType]::ListItem)
if (-not $mon) { throw "monitor item '$monName' not found" }
try {
  ($mon.GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern)).Select()
} catch {
  ($mon.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)).Invoke()
}
Write-Host "selected monitor: $monName"
Start-Sleep -Milliseconds 1500

$comboCond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::ComboBox)
$combos = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, $comboCond)
$scaleCombo = $null
foreach ($c in $combos) { if ($c.Current.Name -eq '缩放') { $scaleCombo = $c; break } }
if (-not $scaleCombo) { throw 'scale combo not found' }
$ep = $scaleCombo.GetCurrentPattern([System.Windows.Automation.ExpandCollapsePattern]::Pattern)
$ep.Expand()
Start-Sleep -Milliseconds 900
$target = "$Percent%"
$item = $null
$itemCond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::ListItem)
foreach ($scope in @($scaleCombo, $win)) {
  $cands = $scope.FindAll([System.Windows.Automation.TreeScope]::Descendants, $itemCond)
  foreach ($c in $cands) {
    $nm = $c.Current.Name
    if ($nm -match ('^\s*' + $Percent + '%')) { $item = $c; break }
  }
  if ($item) { break }
}
if (-not $item) {
  $cond2 = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::ListItem)
  $all = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, $cond2)
  $names = @($all | ForEach-Object { $_.Current.Name } | Where-Object { $_ -match '%' } | Select-Object -Unique)
  throw "scale item '$target' not found; candidates: $($names -join ', ')"
}
($item.GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern)).Select()
Start-Sleep -Milliseconds 1800
try { $ep.Collapse() } catch {}
Write-Host "selected scale: $target (monitor $MonitorNumber)"

$after = @(Get-AllDpi)
Write-Host ("after:  " + (($after | ForEach-Object { "{0}x{1}@{2}%({3},{4})" -f $_.width,$_.height,$_.percent,$_.left,$_.top }) -join ' | '))

$changed = @()
for ($i = 0; $i -lt [math]::Min($before.Count, $after.Count); $i++) {
  if ($before[$i].percent -ne $after[$i].percent) {
    $changed += [pscustomobject]@{ left = $after[$i].left; width = $after[$i].width; before = $before[$i].percent; after = $after[$i].percent }
  }
}
try { ($win.GetCurrentPattern([System.Windows.Automation.WindowPattern]::Pattern)).Close() } catch {}
Start-Sleep -Milliseconds 600

$doc = [ordered]@{
  action = 'set-scale-uia'; capturedAt = (Get-Date -Format o)
  monitorNumber = $MonitorNumber; targetPercent = $Percent
  before = $before; after = $after; changed = $changed
}
$out = Join-Path $OutDir ("scale-uia-m{0}-{1}pct-{2}.json" -f $MonitorNumber, $Percent, (Get-Date -Format 'yyyyMMdd-HHmmss'))
$doc | ConvertTo-Json -Depth 6 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
if ($changed.Count -eq 0) { Write-Host "WARN: no percent change detected" }
