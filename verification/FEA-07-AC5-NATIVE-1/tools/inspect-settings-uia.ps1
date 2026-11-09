# FEA-07-AC5-NATIVE-1 / inspect-settings-uia.ps1
# 只读：打开「设置 → 显示」，导出显示器选择器/缩放下拉的 UIA 元素（名称/类型/能否选择）。
[CmdletBinding()]
param([string]$OutDir = "")
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-AC5-NATIVE-1\evidence' }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes

Start-Process 'ms-settings:display'
$win = $null
for ($i = 0; $i -lt 40; $i++) {
  Start-Sleep -Milliseconds 500
  $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Window)
  $wins = [System.Windows.Automation.AutomationElement]::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children, $cond)
  foreach ($w in $wins) { if ($w.Current.Name -match '设置|Settings') { $win = $w; break } }
  if ($win) { break }
}
if (-not $win) { throw 'settings window not found' }
Write-Host "settings: $($win.Current.Name) pid=$($win.Current.ProcessId)"
Start-Sleep -Milliseconds 1800

$rows = @()
foreach ($ct in @([System.Windows.Automation.ControlType]::ListItem, [System.Windows.Automation.ControlType]::Button, [System.Windows.Automation.ControlType]::ComboBox, [System.Windows.Automation.ControlType]::RadioButton, [System.Windows.Automation.ControlType]::Text)) {
  $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, $ct)
  $els = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, $cond)
  foreach ($e in $els) {
    $n = $e.Current.Name
    if ([string]::IsNullOrWhiteSpace($n)) { continue }
    if ($n -notmatch '显示器|Display|缩放|Scale|监视器|百分比|%') { continue }
    $pats = @()
    foreach ($p in @([System.Windows.Automation.SelectionItemPattern]::Pattern, [System.Windows.Automation.ExpandCollapsePattern]::Pattern, [System.Windows.Automation.InvokePattern]::Pattern, [System.Windows.Automation.ValuePattern]::Pattern)) {
      try { $null = $e.GetCurrentPattern($p); $pats += $p.ProgrammaticName.Replace('PatternIdentifiers.Pattern', '') } catch {}
    }
    $rows += [pscustomobject]@{ type = $ct.ProgrammaticName; name = $n; patterns = ($pats -join ','); offscreen = $e.Current.IsOffscreen }
  }
}
$rows | Sort-Object type, name | Format-Table -AutoSize | Out-String | Write-Host
$out = Join-Path $OutDir ("settings-uia-{0}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$rows | ConvertTo-Json -Depth 5 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
try { ($win.GetCurrentPattern([System.Windows.Automation.WindowPattern]::Pattern)).Close() } catch {}
