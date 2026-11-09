# FEA-07-AC5-NATIVE-1 / drive-import.ps1
# 对已运行的 Host-ready 应用：点击「导入文件夹」→ UIA 驱动文件夹对话框 → 选 ASCII 漫画目录 → 观察 wire 是否出现 import 命令。
[CmdletBinding()]
param(
  [int]$ProcessId = 0,
  [string]$Folder = "",
  [string]$OutDir = ""
)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-AC5-NATIVE-1\evidence' }
$shots = Join-Path $OutDir 'screenshots'; New-Item -ItemType Directory -Force -Path $OutDir, $shots | Out-Null
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes, System.Windows.Forms, System.Drawing

if ($ProcessId -le 0) {
  $p = Get-Process NewManga.App -ErrorAction SilentlyContinue | Sort-Object StartTime | Select-Object -Last 1
  if (-not $p) { throw 'NewManga.App not running' }
  $ProcessId = $p.Id
}
if ([string]::IsNullOrWhiteSpace($Folder)) { throw '-Folder required' }
Write-Host "app pid=$ProcessId folder=$Folder"

$cs = @'
using System;
using System.Runtime.InteropServices;
public static class DrvApi {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, UIntPtr e);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  public static void Click(int x, int y) {
    SetCursorPos(x, y); System.Threading.Thread.Sleep(120);
    mouse_event(0x0002, 0, 0, 0, UIntPtr.Zero); System.Threading.Thread.Sleep(80);
    mouse_event(0x0004, 0, 0, 0, UIntPtr.Zero);
  }
  public static IntPtr TopWindow(uint pid) {
    IntPtr found = IntPtr.Zero;
    EnumWindows((h, l) => { uint p; GetWindowThreadProcessId(h, out p); if (p == pid && IsWindowVisible(h)) { found = h; return false; } return true; }, IntPtr.Zero);
    return found;
  }
}
'@
Add-Type -TypeDefinition $cs -ErrorAction Stop

function UiaWindow($procId) {
  $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ProcessIdProperty, $procId)
  $wins = [System.Windows.Automation.AutomationElement]::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children, $cond)
  foreach ($w in $wins) { if ($w.Current.ControlType -eq [System.Windows.Automation.ControlType]::Window) { return $w } }
  return $null
}
function Find-ByName($root, [string]$name) {
  return $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $name)))
}
function Click-Element($el) { $p = $el.GetClickablePoint(); [DrvApi]::Click([int]$p.X, [int]$p.Y) }

$win = UiaWindow $ProcessId
if (-not $win) { throw 'app UIA window not found' }
$main = [DrvApi]::TopWindow([uint32]$ProcessId)
[DrvApi]::SetForegroundWindow($main) | Out-Null
Start-Sleep -Milliseconds 500

$btn = Find-ByName $win '导入文件夹'
if (-not $btn) { throw '导入文件夹 button not found' }
Click-Element $btn
Start-Sleep -Milliseconds 3500

# 找对话框：同进程或任何可见且标题含 选择/文件夹/浏览 的窗口
$dlg = $null
for ($i = 0; $i -lt 24; $i++) {
  Start-Sleep -Milliseconds 500
  $condW = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Window)
  $wins = [System.Windows.Automation.AutomationElement]::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children, $condW)
  foreach ($w in $wins) {
    if ($w.Current.Name -match '选择|文件夹|浏览|Select|Browse|Folder' -and $w.Current.ProcessId -ne 8168) { $dlg = $w; break }
  }
  if ($dlg) { break }
}
$shot0 = $null
if ($dlg) {
  Write-Host "dialog: '$($dlg.Current.Name)' pid=$($dlg.Current.ProcessId)"
} else {
  Write-Host 'no dialog detected'
}
$bmp = New-Object System.Drawing.Bitmap 2560, 1440
$g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen(0, 0, 0, 0, (New-Object System.Drawing.Size 2560, 1440)); $g.Dispose()
$shot0 = Join-Path $shots ("{0}-drive-import-dialog.png" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$bmp.Save($shot0, [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
Write-Host "screenshot: $shot0"

if (-not $dlg) { throw 'folder dialog did not appear; cannot drive import' }

# 地址栏：优先 UIA SetValue，失败则 Alt+D + SendKeys(ASCII)
$editCond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Edit)
$edits = $dlg.FindAll([System.Windows.Automation.TreeScope]::Descendants, $editCond)
Write-Host "dialog edits: $($edits.Count)"
$set = $false
foreach ($e in $edits) {
  try { $vp = $e.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern); $vp.SetValue($Folder); $set = $true; break } catch {}
}
if (-not $set) {
  [System.Windows.Forms.SendKeys]::SendWait('%d'); Start-Sleep -Milliseconds 600
  [System.Windows.Forms.SendKeys]::SendWait($Folder); Start-Sleep -Milliseconds 500
}
Start-Sleep -Milliseconds 600
[System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
Start-Sleep -Milliseconds 2200
[System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
Start-Sleep -Milliseconds 1500

$pick = Find-ByName $dlg '选择文件夹'
if (-not $pick) { $pick = Find-ByName $dlg '确定' }
if ($pick) { Click-Element $pick; Write-Host "clicked pick" } else { Write-Host 'pick button NOT found' }
Start-Sleep -Milliseconds 9000

$shot1 = Join-Path $shots ("{0}-drive-import-after.png" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$bmp = New-Object System.Drawing.Bitmap 2560, 1440
$g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen(0, 0, 0, 0, (New-Object System.Drawing.Size 2560, 1440)); $g.Dispose()
$bmp.Save($shot1, [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()

$doc = [ordered]@{
  action = 'drive-import'; capturedAt = (Get-Date -Format o)
  pid = $ProcessId; folder = $Folder; dialogSeen = [bool]$dlg
  dialogTitle = if ($dlg) { $dlg.Current.Name } else { $null }
  screenshots = @($shot0, $shot1)
}
$out = Join-Path $OutDir ("drive-import-{0}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$doc | ConvertTo-Json -Depth 5 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
