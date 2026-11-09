# FEA-07-IMMERSIVE-F11-1 / capture-after-f11.ps1
# 用户手动按 F11 后：采样主窗/沉浸窗状态、状态栏提示、日志文件，落盘证据 JSON（截图存仓外）。
[CmdletBinding()]
param([int]$ProcessId = 0, [string]$OutDir = "", [string]$LogDir = "", [string]$ShotDir = "G:\CODEX\New Manga.workspace\FEA-07-IMMERSIVE-F11-1\shots")
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-IMMERSIVE-F11-1\evidence' }
if ([string]::IsNullOrWhiteSpace($LogDir)) { $LogDir = 'G:\CODEX\New Manga.workspace\FEA-07-IMMERSIVE-F11-1\native-sticky\logs' }
New-Item -ItemType Directory -Force -Path $OutDir, $ShotDir | Out-Null
Add-Type -AssemblyName System.Drawing, UIAutomationClient, UIAutomationTypes

if ($ProcessId -le 0) { $ProcessId = (Get-Process NewManga.App | Sort-Object StartTime | Select-Object -Last 1).Id }
$cs = @'
using System; using System.Collections.Generic; using System.Runtime.InteropServices; using System.Text;
public static class CAF {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int left, top, right, bottom; }
  [StructLayout(LayoutKind.Sequential)] public struct WINDOWPLACEMENT { public int length; public int flags; public int showCmd; public int p1x; public int p1y; public int p2x; public int p2y; public RECT normal; }
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool GetWindowPlacement(IntPtr h, ref WINDOWPLACEMENT p);
  [DllImport("user32.dll")] public static extern int GetWindowLongW(IntPtr h, int i);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr v);
  public static string[] V(uint pid) {
    SetProcessDpiAwarenessContext(new IntPtr(-4));
    var l = new List<string>();
    EnumWindows((h,x) => { uint p; GetWindowThreadProcessId(h, out p); if (p != pid || !IsWindowVisible(h)) return true;
      var t=new StringBuilder(200); GetWindowTextW(h,t,200); RECT r; GetWindowRect(h,out r);
      int st=GetWindowLongW(h,-16); bool cap=(st&0x00C00000)==0x00C00000;
      var wp=new WINDOWPLACEMENT(); wp.length=Marshal.SizeOf(typeof(WINDOWPLACEMENT)); GetWindowPlacement(h, ref wp);
      l.Add(string.Format("{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}", h, r.left,r.top,r.right-r.left,r.bottom-r.top, cap?1:0, wp.showCmd, t)); return true; }, IntPtr.Zero);
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
  $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ProcessIdProperty, $procId)
  foreach ($w in [System.Windows.Automation.AutomationElement]::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children, $c)) {
    if ($w.Current.ControlType -eq [System.Windows.Automation.ControlType]::Window -and $w.Current.Name -eq 'New Manga') { return $w }
  }
  return $null
}
function Texts($win) {
  if (-not $win) { return @() }
  $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Text)
  $out = @()
  foreach ($e in $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, $c)) { if ($e.Current.Name) { $out += $e.Current.Name } }
  return $out
}

$wins = @([CAF]::V([uint32]$ProcessId))
$main = $null; $extra = @()
foreach ($l in $wins) { $p = $l -split '\|',8; if ($p[7] -eq 'New Manga') { $main = $p } else { $extra += $p } }
$shot = Capture 'after-f11'
$win = UiaMain $ProcessId
$texts = @(Texts $win)
$hint = @($texts | Where-Object { $_ -like '*全屏阅读器打开失败*' })
$logFile = Join-Path $LogDir 'immersive-open.log'
$logLines = if (Test-Path $logFile) { @(Get-Content $logFile) } else { @() }
$minimized = if ($main) { ([int]$main[6] -eq 7) -or ([int]$main[1] -le -30000) } else { $true }

$doc = [ordered]@{
  case = 'f11-native-after-fix'; capturedAt = (Get-Date -Format o); pid = $ProcessId
  immersiveWindows = @($extra | ForEach-Object { [ordered]@{ left=[int]$_[0] } })
  immersiveCount = $extra.Count
  mainWindow = if ($main) { [ordered]@{ left=[int]$main[1]; top=[int]$main[2]; width=[int]$main[3]; height=[int]$main[4]; hasCaption=($main[5] -eq '1'); showCmd=[int]$main[6]; minimized=$minimized } } else { $null }
  statusHint = $hint
  hintVisible = ($hint.Count -gt 0)
  statusTextsSample = @($texts | Select-Object -First 12)
  logFile = $logFile
  logExists = (Test-Path $logFile)
  logLines = $logLines
  mainNotMinimized = -not $minimized
  screenshot = $shot
}
$out = Join-Path $OutDir ("f11-native-after-fix-{0}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$doc | ConvertTo-Json -Depth 7 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
Write-Host ("immersiveCount={0} mainMinimized={1} hintVisible={2} logExists={3}" -f $extra.Count,$minimized,$doc.hintVisible,$doc.logExists)
if ($hint.Count -gt 0) { Write-Host ("hint: " + ($hint -join ' | ')) }
if ($doc.logExists) { Write-Host ("log: " + ($logLines -join ' | ')) }
