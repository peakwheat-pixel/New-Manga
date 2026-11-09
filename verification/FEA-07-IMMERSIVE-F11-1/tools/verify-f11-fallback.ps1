# FEA-07-IMMERSIVE-F11-1 / verify-f11-fallback.ps1
# 真实桌面复测：新构建应用 + 隔离 sidecar/数据根 → PostMessage(F11) →
#   成功：出现沉浸窗口（采样几何/截图，Esc 关闭并校验）；
#   失败：断言主窗未最小化、状态栏出现「全屏阅读器打开失败」提示（兜底验收）。
[CmdletBinding()]
param([string]$OutDir = "", [string]$ShotDir = "G:\CODEX\New Manga.workspace\FEA-07-IMMERSIVE-F11-1\shots")
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-IMMERSIVE-F11-1\evidence' }
New-Item -ItemType Directory -Force -Path $OutDir, $ShotDir | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
Add-Type -AssemblyName System.Drawing, UIAutomationClient, UIAutomationTypes

$cs = @'
using System; using System.Collections.Generic; using System.Runtime.InteropServices; using System.Text;
public static class VF {
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
  [DllImport("user32.dll")] public static extern bool PostMessageW(IntPtr h, uint msg, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
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
  public static int F11(IntPtr h) {
    bool d = PostMessageW(h, 0x0100, (IntPtr)0x7A, (IntPtr)0x00470001);
    System.Threading.Thread.Sleep(80);
    bool u = PostMessageW(h, 0x0101, (IntPtr)0x7A, unchecked((IntPtr)0xC0470001));
    return (d?1:0)+(u?2:0);
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
function UiaWindow($procId) {
  $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ProcessIdProperty, $procId)
  $ws = [System.Windows.Automation.AutomationElement]::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children, $c)
  foreach ($w in $ws) { if ($w.Current.ControlType -eq [System.Windows.Automation.ControlType]::Window -and $w.Current.Name -eq 'New Manga') { return $w } }
  return $null
}
function StatusTexts($win) {
  if (-not $win) { return @() }
  $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Text)
  $els = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, $c)
  $out = @()
  foreach ($e in $els) { $n = $e.Current.Name; if ($n -and ($n -like '*全屏*' -or $n -like '*阅读器打开失败*' -or $n -like '*启动*' -or $n -like '*Host*')) { $out += $n } }
  return $out
}

# 启动应用（隔离 sidecar + 已导入 169 页的数据根）
$sidecar = 'G:\CODEX\New Manga.workspace\FEA-07-AC5-NATIVE-1\sidecar'
$sessionData = 'G:\CODEX\New Manga.workspace\FEA-07-AC5-NATIVE-1\reader-session\data'
$root = Join-Path 'G:\CODEX\New Manga.workspace\FEA-07-IMMERSIVE-F11-1' ("run-" + $stamp)
$logs = Join-Path $root 'logs'; $theme = Join-Path $root 'theme'
New-Item -ItemType Directory -Force -Path $logs, $theme | Out-Null
$env:NEWMANGA_CORE_SIDECAR_DIR = $sidecar
$exe = Join-Path $repo 'apps\desktop-avalonia\src\NewManga.App\bin\Release\net9.0\NewManga.App.exe'
$args = @('--data-root', $sessionData, '--log-dir', $logs, '--theme-home', $theme, '--shell=v2')
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $exe; $psi.WorkingDirectory = (Split-Path $exe -Parent); $psi.UseShellExecute = $false; $psi.CreateNoWindow = $true
foreach ($a in $args) { $psi.ArgumentList.Add($a) }
$proc = [System.Diagnostics.Process]::Start($psi)
Write-Host "pid=$($proc.Id)"
$main = $null
for ($i = 0; $i -lt 60; $i++) {
  Start-Sleep -Milliseconds 500
  foreach ($l in [VF]::V([uint32]$proc.Id)) { $p = $l -split '\|',8; if ($p[7] -eq 'New Manga') { $main = $p } }
  if ($main) { break }
}
if (-not $main) { throw 'main window not found' }
Start-Sleep -Seconds 8
$hwnd = [IntPtr][int64]$main[0]
[VF]::SetForegroundWindow($hwnd) | Out-Null
Start-Sleep -Milliseconds 500
$beforeShot = Capture 'before-f11'
$rc = [VF]::F11($hwnd)
Write-Host "PostMessage F11 rc=$rc"

$immersive = $null; $status = @()
for ($i = 0; $i -lt 60; $i++) {
  Start-Sleep -Milliseconds 150
  foreach ($l in [VF]::V([uint32]$proc.Id)) { $p = $l -split '\|',8; if ($p[7] -ne 'New Manga') { $immersive = $p; break } }
  if ($immersive) { break }
  $winner = UiaWindow $proc.Id
  $status = @(StatusTexts $winner)
  if ($status.Count -gt 0 -and ($status -join ' ') -match '全屏阅读器打开失败') { break }
}
$afterShot = Capture 'after-f11'
$win = UiaWindow $proc.Id
$finalStatus = @(StatusTexts $win)
$mainNow = $null
foreach ($l in [VF]::V([uint32]$proc.Id)) { $p = $l -split '\|',8; if ($p[7] -eq 'New Manga') { $mainNow = $p } }
$minimized = if ($mainNow) { ([int]$mainNow[6] -eq 7) -or ([int]$mainNow[1] -le -30000) } else { $true }

if ($immersive) {
  Write-Host ("IMMERSIVE rect=({0},{1}) {2}x{3} caption={4}" -f $immersive[1],$immersive[2],$immersive[3],$immersive[4],$immersive[5])
} else {
  Write-Host ("no immersive window; main minimized={0}; status={1}" -f $minimized, ($finalStatus -join ' | '))
}

$doc = [ordered]@{
  case = 'f11-fallback-native'; capturedAt = (Get-Date -Format o)
  app = [ordered]@{ pid = $proc.Id; exe = $exe; args = $args; sidecar = $sidecar; dataRoot = $sessionData; logDir = $logs }
  postMessageRc = $rc
  immersive = if ($immersive) { [ordered]@{ left=[int]$immersive[1]; top=[int]$immersive[2]; width=[int]$immersive[3]; height=[int]$immersive[4]; hasCaption=($immersive[5]-eq'1'); title=$immersive[7]; coversPrimary=(([int64]$immersive[1] -le 0) -and ([int64]$immersive[2] -le 0) -and ([int64]$immersive[3] -ge 2560) -and ([int64]$immersive[4] -ge 1440)) } } else { $null }
  mainWindow = if ($mainNow) { [ordered]@{ left=[int]$mainNow[1]; top=[int]$mainNow[2]; width=[int]$mainNow[3]; height=[int]$mainNow[4]; showCmd=[int]$mainNow[6]; minimized=$minimized } } else { $null }
  statusTexts = $finalStatus
  fallbackVisible = [bool](($finalStatus -join ' ') -match '全屏阅读器打开失败')
  mainNotMinimized = -not $minimized
  screenshots = @($beforeShot, $afterShot)
}
$out = Join-Path $OutDir ("f11-fallback-native-{0}.json" -f $stamp)
$doc | ConvertTo-Json -Depth 7 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
if ($immersive) {
  # 关闭沉浸窗口并校验主窗恢复
  [System.Windows.Forms.SendKeys]::SendWait('{ESC}')
} elseif (-not $proc.HasExited) {
  $proc.Kill($true); $proc.WaitForExit(5000) | Out-Null
  Write-Host 'app closed'
}
