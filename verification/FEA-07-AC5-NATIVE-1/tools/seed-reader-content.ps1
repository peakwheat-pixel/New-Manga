# FEA-07-AC5-NATIVE-1 / seed-reader-content.ps1 (v2)
# 合成 ASCII 路径漫画 → 启动应用（隔离根）→ UIA 驱动「导入文件夹」对话框 → 导入 → 导出 UIA。
[CmdletBinding()]
param([string]$OutDir = "", [switch]$KeepRunning)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-AC5-NATIVE-1\evidence' }
$shots = Join-Path $OutDir 'screenshots'; New-Item -ItemType Directory -Force -Path $OutDir, $shots | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
Add-Type -AssemblyName System.Drawing, UIAutomationClient, UIAutomationTypes, System.Windows.Forms

$root = Join-Path $env:TEMP ("nm-fea07-reader-{0}" -f $stamp)
$src = Join-Path $root 'src\MyManga'
$data = Join-Path $root 'data'; $logs = Join-Path $root 'logs'; $theme = Join-Path $root 'theme'
New-Item -ItemType Directory -Force -Path $data, $logs, $theme | Out-Null
foreach ($ch in 1..2) {
  $chDir = Join-Path $src ("Chapter-{0}" -f $ch)
  New-Item -ItemType Directory -Force -Path $chDir | Out-Null
  foreach ($pg in 1..3) {
    $bmp = New-Object System.Drawing.Bitmap 800, 1200
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.Clear([System.Drawing.Color]::White)
    $font = New-Object System.Drawing.Font 'Microsoft YaHei', 40
    $g.DrawString(("Ch{0} P{1}" -f $ch, $pg), $font, [System.Drawing.Brushes]::Black, 60, 120)
    $g.DrawRectangle([System.Drawing.Pens]::Gray, 20, 20, 760, 1160)
    $g.Dispose()
    $file = Join-Path $chDir ("{0:D3}.png" -f $pg)
    $bmp.Save($file, [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
  }
}
Write-Host "seeded: $src"

$cs = @'
using System;
using System.Runtime.InteropServices;
public static class Seed2Api {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int left, top, right, bottom; }
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern uint GetDpiForWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr v);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, UIntPtr e);
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
  public static string Rect(IntPtr h) {
    RECT r; GetWindowRect(h, out r);
    uint d = GetDpiForWindow(h);
    return string.Format("{0}|{1}|{2}|{3}|{4}|{5}", r.left, r.top, r.right - r.left, r.bottom - r.top, d, Math.Round(d / 96.0 * 100));
  }
  public static void Click(int x, int y) {
    SetCursorPos(x, y); System.Threading.Thread.Sleep(120);
    mouse_event(0x0002, 0, 0, 0, UIntPtr.Zero); System.Threading.Thread.Sleep(80);
    mouse_event(0x0004, 0, 0, 0, UIntPtr.Zero);
  }
}
'@
Add-Type -TypeDefinition $cs -ErrorAction Stop

function Capture([int]$x, [int]$y, [int]$w, [int]$h, [string]$file) {
  $bmp = New-Object System.Drawing.Bitmap $w, $h
  $g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($x, $y, 0, 0, (New-Object System.Drawing.Size $w, $h)); $g.Dispose()
  $bmp.Save($file, [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
  [pscustomobject]@{ file = (Split-Path $file -Leaf); width = $w; height = $h; sha256 = (Get-FileHash -Algorithm SHA256 -Path $file).Hash.ToLowerInvariant() }
}
function UiaWindow($procId) {
  $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ProcessIdProperty, $procId)
  $wins = [System.Windows.Automation.AutomationElement]::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children, $cond)
  foreach ($w in $wins) { if ($w.Current.ControlType -eq [System.Windows.Automation.ControlType]::Window) { return $w } }
  return $null
}
function Find-ByName($root, [string]$name) {
  return $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $name)))
}
function Click-Element($el) {
  $p = $el.GetClickablePoint(); [Seed2Api]::Click([int]$p.X, [int]$p.Y)
}

$exe = Join-Path $repo 'apps\desktop-avalonia\src\NewManga.App\bin\Release\net9.0\NewManga.App.exe'
$appArgs = @('--data-root', $data, '--log-dir', $logs, '--theme-home', $theme, '--shell=v2')
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $exe; $psi.WorkingDirectory = (Split-Path $exe -Parent); $psi.UseShellExecute = $false; $psi.CreateNoWindow = $true
foreach ($a in $appArgs) { $psi.ArgumentList.Add($a) }
$proc = [System.Diagnostics.Process]::Start($psi)
$main = [IntPtr]::Zero
for ($i = 0; $i -lt 50; $i++) { Start-Sleep -Milliseconds 500; $main = [Seed2Api]::Main([uint32]$proc.Id); if ($main -ne [IntPtr]::Zero) { break } }
if ($main -eq [IntPtr]::Zero) { throw 'window not found' }
Start-Sleep -Milliseconds 2500
$win = $null
for ($i = 0; $i -lt 20; $i++) {
  Start-Sleep -Milliseconds 500
  $win = UiaWindow $proc.Id
  if ($win) { break }
}
if (-not $win) {
  try { $win = [System.Windows.Automation.AutomationElement]::FromHandle($main) } catch { $win = $null }
}
if (-not $win) { throw 'UIA window not available' }
Start-Sleep -Milliseconds 1500
[Seed2Api]::SetForegroundWindow($main) | Out-Null
Write-Host "app pid=$($proc.Id)"

$importBtn = Find-ByName $win '导入文件夹'
if (-not $importBtn) { throw 'import folder button not found' }
Click-Element $importBtn
Start-Sleep -Milliseconds 3000
$shot1 = Capture 0 0 2560 1440 (Join-Path $shots ("{0}-seed2-dialog.png" -f $stamp))

# 文件夹对话框：Alt+D 聚焦地址栏，用 SendKeys 输入 ASCII 路径，Enter 导航，再 Enter 确认
Start-Sleep -Milliseconds 1500
[System.Windows.Forms.SendKeys]::SendWait('%d')
Start-Sleep -Milliseconds 800
[System.Windows.Forms.SendKeys]::SendWait($src)
Start-Sleep -Milliseconds 900
[System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
Start-Sleep -Milliseconds 2200
[System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
Start-Sleep -Milliseconds 1000

# 点击「选择文件夹」
$pick = Find-ByName $dlg '选择文件夹'
if (-not $pick) { $pick = Find-ByName $dlg '确定' }
if ($pick) { Click-Element $pick } else { Write-Host 'pick button not found' }
Start-Sleep -Milliseconds 8000
$shot2 = Capture 0 0 2560 1440 (Join-Path $shots ("{0}-seed2-after-import.png" -f $stamp))

function DumpUia($win) {
  $rows = @()
  foreach ($ct in @([System.Windows.Automation.ControlType]::Button, [System.Windows.Automation.ControlType]::ListItem, [System.Windows.Automation.ControlType]::List, [System.Windows.Automation.ControlType]::TabItem, [System.Windows.Automation.ControlType]::TreeItem, [System.Windows.Automation.ControlType]::Edit)) {
    $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, $ct)
    $els = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, $cond)
    foreach ($e in $els) { $rows += [pscustomobject]@{ type = $ct.ProgrammaticName.Replace('ControlType.',''); name = $e.Current.Name; id = $e.Current.AutomationId } }
  }
  return $rows
}
$rows = DumpUia $win
$doc = [ordered]@{
  case = 'seed-reader-content'; capturedAt = (Get-Date -Format o)
  app = [ordered]@{ pid = $proc.Id; exe = $exe; args = $appArgs; dataRoot = $data; source = $src }
  controls = $rows; screenshots = @($shot1, $shot2)
}
$out = Join-Path $OutDir ("seed-{0}.json" -f $stamp)
$doc | ConvertTo-Json -Depth 6 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
$rows | Where-Object { $_.name } | Select-Object -First 30 | Format-Table -AutoSize | Out-String | Write-Host
if (-not $KeepRunning) { if (-not $proc.HasExited) { $proc.Kill($true); $proc.WaitForExit(5000) | Out-Null }; Write-Host 'app closed' } else { Write-Host "kept running pid=$($proc.Id) dataRoot=$data" }
