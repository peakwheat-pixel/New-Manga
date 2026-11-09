# FEA-07-AC5-NATIVE-1 / drive-import2.ps1
# 驱动已打开的系统文件夹选择框（#32770 导入文件夹）选择指定目录，再点击应用导入向导按钮，直到出现 import wire。
[CmdletBinding()]
param([string]$Folder = "", [string]$OutDir = "")
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-AC5-NATIVE-1\evidence' }
$shots = Join-Path $OutDir 'screenshots'; New-Item -ItemType Directory -Force -Path $OutDir, $shots | Out-Null
if ([string]::IsNullOrWhiteSpace($Folder)) { throw '-Folder required' }
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes, System.Windows.Forms, System.Drawing

$cs = @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
public static class Dlg3 {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int left, top, right, bottom; }
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassNameW(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, UIntPtr e);
  public static string FindDialog(uint pid, string titlePart) {
    string found = "";
    EnumWindows((h,l) => {
      uint p; GetWindowThreadProcessId(h, out p);
      if (p != pid || !IsWindowVisible(h)) return true;
      var c = new StringBuilder(200); GetClassNameW(h,c,200);
      var t = new StringBuilder(200); GetWindowTextW(h,t,200);
      if (c.ToString() == "#32770" && t.ToString().Contains(titlePart)) { found = h + "|" + t; return false; }
      return true;
    }, IntPtr.Zero);
    return found;
  }
  public static void Click(int x, int y) {
    SetCursorPos(x, y); System.Threading.Thread.Sleep(120);
    mouse_event(0x0002, 0, 0, 0, UIntPtr.Zero); System.Threading.Thread.Sleep(80);
    mouse_event(0x0004, 0, 0, 0, UIntPtr.Zero);
  }
}
'@
Add-Type -TypeDefinition $cs -ErrorAction Stop

function Capture($name) {
  $f = Join-Path $shots ("{0}-{1}.png" -f (Get-Date -Format 'yyyyMMdd-HHmmss'), $name)
  $bmp = New-Object System.Drawing.Bitmap 2560, 1440
  $g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen(0, 0, 0, 0, (New-Object System.Drawing.Size 2560, 1440)); $g.Dispose()
  $bmp.Save($f, [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
  return $f
}
$app = Get-Process NewManga.App -ErrorAction SilentlyContinue | Sort-Object StartTime | Select-Object -Last 1
if (-not $app) { throw 'NewManga.App not running' }
$found = [Dlg3]::FindDialog([uint32]$app.Id, '导入文件夹')
if (-not $found) { throw 'import folder dialog not found' }
$dlgHwnd = [IntPtr][int64](($found -split '\|')[0])
Write-Host "dialog hwnd=$dlgHwnd title=$(($found -split '\|')[1])"
[Dlg3]::SetForegroundWindow($dlgHwnd) | Out-Null
Start-Sleep -Milliseconds 600

# Ctrl+L 地址栏 → ASCII 路径 → Enter 导航 → Enter 选定
[System.Windows.Forms.SendKeys]::SendWait('^l')
Start-Sleep -Milliseconds 700
[System.Windows.Forms.SendKeys]::SendWait($Folder)
Start-Sleep -Milliseconds 700
[System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
Start-Sleep -Milliseconds 2200
$shotNav = Capture 'import-nav'
[System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
Start-Sleep -Milliseconds 2500
$shotPick = Capture 'import-picked'

# 应用导入向导按钮（UIA）
function UiaWindow($procId) {
  $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ProcessIdProperty, $procId)
  $wins = [System.Windows.Automation.AutomationElement]::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children, $cond)
  foreach ($w in $wins) { if ($w.Current.ControlType -eq [System.Windows.Automation.ControlType]::Window -and $w.Current.Name -eq 'New Manga') { return $w } }
  return $null
}
function Find-ByName($root, [string]$name) {
  return $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $name)))
}
function Click-Element($el) { $p = $el.GetClickablePoint(); [Dlg3]::Click([int]$p.X, [int]$p.Y) }

$win = UiaWindow $app.Id
$steps = @()
foreach ($name in @('选择目录并预览', '开始导入', '确认导入', '选择源并预览')) {
  if (-not $win) { break }
  $b = Find-ByName $win $name
  if ($b -and $b.Current.IsEnabled) {
    Click-Element $b
    $steps += $name
    Write-Host "clicked: $name"
    Start-Sleep -Milliseconds 3000
    $shot = Capture ("import-step-" + ($steps.Count))
  }
  if ($steps.Count -gt 0 -and $name -eq '确认导入') { break }
}
Start-Sleep -Milliseconds 4000
$finalShot = Capture 'import-final'

$doc = [ordered]@{
  action = 'drive-import2'; capturedAt = (Get-Date -Format o)
  folder = $Folder; dialog = "$dlgHwnd"; stepsClicked = $steps
  screenshots = @($shotNav, $shotPick) + @(if ($finalShot) { $finalShot })
}
$out = Join-Path $OutDir ("drive-import2-{0}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$doc | ConvertTo-Json -Depth 5 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
Write-Host "steps: $($steps -join ' -> ')"; Write-Host "final shot: $finalShot"
