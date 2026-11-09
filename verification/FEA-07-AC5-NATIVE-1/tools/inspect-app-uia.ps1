# FEA-07-AC5-NATIVE-1 / inspect-app-uia.ps1
# 启动应用（隔离根），导出主窗 UIA 可交互元素（按钮/编辑框/菜单/页签），用于选择 IME/编辑/全屏驱动面。
[CmdletBinding()]
param([string]$OutDir = "", [int]$WaitSec = 25)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-AC5-NATIVE-1\evidence' }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$root = Join-Path $env:TEMP ("nm-fea07-uia-{0}" -f $stamp)
$dr = Join-Path $root 'data'; $ld = Join-Path $root 'logs'; $th = Join-Path $root 'theme'
New-Item -ItemType Directory -Force -Path $dr, $ld, $th | Out-Null
$exe = Join-Path $repo 'apps\desktop-avalonia\src\NewManga.App\bin\Release\net9.0\NewManga.App.exe'
$appArgs = @('--data-root', $dr, '--log-dir', $ld, '--theme-home', $th, '--shell=v2')
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $exe; $psi.WorkingDirectory = (Split-Path $exe -Parent); $psi.UseShellExecute = $false; $psi.CreateNoWindow = $true
foreach ($a in $appArgs) { $psi.ArgumentList.Add($a) }
$proc = [System.Diagnostics.Process]::Start($psi)
Write-Host "launched pid=$($proc.Id)"
$win = $null
for ($i = 0; $i -lt ($WaitSec * 2); $i++) {
  Start-Sleep -Milliseconds 500
  $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ProcessIdProperty, $proc.Id)
  $wins = [System.Windows.Automation.AutomationElement]::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children, $cond)
  foreach ($w in $wins) { if ($w.Current.ControlType -eq [System.Windows.Automation.ControlType]::Window) { $win = $w; break } }
  if ($win) { break }
}
if (-not $win) { throw 'app window not found' }
Start-Sleep -Milliseconds 2500
Write-Host "window: $($win.Current.Name)"

$rows = @()
foreach ($ct in @([System.Windows.Automation.ControlType]::Button, [System.Windows.Automation.ControlType]::Edit, [System.Windows.Automation.ControlType]::TabItem, [System.Windows.Automation.ControlType]::MenuItem, [System.Windows.Automation.ControlType]::ComboBox)) {
  $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, $ct)
  $els = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, $cond)
  foreach ($e in $els) {
    $rows += [pscustomobject]@{ type = $ct.ProgrammaticName.Replace('ControlType.', ''); name = $e.Current.Name; automationId = $e.Current.AutomationId; enabled = $e.Current.IsEnabled; offscreen = $e.Current.IsOffscreen }
  }
}
$rows | Sort-Object type, name | Format-Table -AutoSize -Wrap | Out-String -Width 200 | Write-Host
$out = Join-Path $OutDir ("app-uia-{0}.json" -f $stamp)
@{ pid = $proc.Id; window = $win.Current.Name; controls = $rows; dataRoot = $dr; logDir = $ld; themeHome = $th } | ConvertTo-Json -Depth 5 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
if (-not $proc.HasExited) { $proc.Kill($true); $proc.WaitForExit(5000) | Out-Null; Write-Host 'app closed' }
