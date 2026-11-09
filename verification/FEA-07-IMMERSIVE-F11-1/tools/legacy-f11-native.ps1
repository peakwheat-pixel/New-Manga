# FEA-07-IMMERSIVE-F11-1 / legacy-f11-native.ps1
# 仅 legacy 壳（--shell=legacy）承载 MainWindow/F11 沉浸：启动 → 记录 args/shell → PostMessage F11 →
# 采样沉浸窗口/状态栏/日志 → 若成功再 Esc 关闭并校验主窗恢复。
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
public static class LF {
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
  public static int Key(IntPtr h, int vk) {
    bool d = PostMessageW(h, 0x0100, (IntPtr)vk, (IntPtr)0x00010001);
    System.Threading.Thread.Sleep(80);
    bool u = PostMessageW(h, 0x0101, (IntPtr)vk, unchecked((IntPtr)0xC0010001));
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
function UiaWin($procId, $title) {
  $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ProcessIdProperty, $procId)
  foreach ($w in [System.Windows.Automation.AutomationElement]::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children, $c)) {
    if ($w.Current.ControlType -eq [System.Windows.Automation.ControlType]::Window -and $w.Current.Name -eq $title) { return $w }
  }
  return $null
}
function BtnNames($win) {
  if (-not $win) { return @() }
  $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Button)
  $out = @()
  foreach ($e in $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, $c)) { if ($e.Current.Name) { $out += $e.Current.Name } }
  return $out
}
function Texts($win) {
  if (-not $win) { return @() }
  $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Text)
  $out = @()
  foreach ($e in $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, $c)) { if ($e.Current.Name) { $out += $e.Current.Name } }
  return $out
}

$sidecar = 'G:\CODEX\New Manga.workspace\FEA-07-AC5-NATIVE-1\sidecar'
$sessionData = 'G:\CODEX\New Manga.workspace\FEA-07-AC5-NATIVE-1\reader-session\data'
$root = Join-Path 'G:\CODEX\New Manga.workspace\FEA-07-IMMERSIVE-F11-1' ("legacy-" + $stamp)
$logs = Join-Path $root 'logs'; $theme = Join-Path $root 'theme'
New-Item -ItemType Directory -Force -Path $logs, $theme | Out-Null
$env:NEWMANGA_CORE_SIDECAR_DIR = $sidecar
$exe = Join-Path $repo 'apps\desktop-avalonia\src\NewManga.App\bin\Release\net9.0\NewManga.App.exe'
$args = @('--shell=legacy', '--data-root', $sessionData, '--log-dir', $logs, '--theme-home', $theme)
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $exe; $psi.WorkingDirectory = (Split-Path $exe -Parent); $psi.UseShellExecute = $false; $psi.CreateNoWindow = $true
foreach ($a in $args) { $psi.ArgumentList.Add($a) }
$proc = [System.Diagnostics.Process]::Start($psi)
Write-Host "pid=$($proc.Id) shell=legacy"
$main = $null
for ($i = 0; $i -lt 60; $i++) { Start-Sleep -Milliseconds 500; foreach ($l in [LF]::V([uint32]$proc.Id)) { $p = $l -split '\|',8; if ($p[7] -eq 'New Manga') { $main = $p } }; if ($main) { break } }
if (-not $main) { throw 'main window not found' }
Start-Sleep -Seconds 6
$win = UiaWin $proc.Id 'New Manga'
$navs = BtnNames $win
Write-Host ("nav sample: " + (($navs | Select-Object -First 12) -join ', '))
$hwnd = [IntPtr][int64]$main[0]
[LF]::SetForegroundWindow($hwnd) | Out-Null
Start-Sleep -Milliseconds 500
$beforeShot = Capture 'legacy-before'
$rc = [LF]::Key($hwnd, 0x7A)  # VK_F11
Write-Host "PostMessage F11 rc=$rc"

$immersive = $null
for ($i = 0; $i -lt 60; $i++) {
  Start-Sleep -Milliseconds 150
  foreach ($l in [LF]::V([uint32]$proc.Id)) { $p = $l -split '\|',8; if ($p[7] -ne 'New Manga') { $immersive = $p; break } }
  if ($immersive) { break }
}
Start-Sleep -Milliseconds 500
$winAfter = UiaWin $proc.Id 'New Manga'
$texts = @(Texts $winAfter)
$hint = @($texts | Where-Object { $_ -like '*全屏阅读器打开失败*' })
$mainNow = $null
foreach ($l in [LF]::V([uint32]$proc.Id)) { $p = $l -split '\|',8; if ($p[7] -eq 'New Manga') { $mainNow = $p } }
$minimized = if ($mainNow) { ([int]$mainNow[6] -eq 7) -or ([int]$mainNow[1] -le -30000) } else { $true }
$afterShot = Capture 'legacy-after'

$doc = [ordered]@{
  case='legacy-f11-native'; capturedAt=(Get-Date -Format o)
  app=[ordered]@{ pid=$proc.Id; exe=$exe; args=$args; shell='legacy'; sidecar=$sidecar; dataRoot=$sessionData; logDir=$logs }
  navSample=@($navs | Select-Object -First 12)
  postMessageRc=$rc
  immersive=if($immersive){[ordered]@{left=[int]$immersive[1];top=[int]$immersive[2];width=[int]$immersive[3];height=[int]$immersive[4];hasCaption=($immersive[5]-eq'1');title=$immersive[7];coversPrimary=(([int64]$immersive[1] -le 0)-and([int64]$immersive[2] -le 0)-and([int64]$immersive[3] -ge 2560)-and([int64]$immersive[4] -ge 1440))}}else{$null}
  mainWindow=if($mainNow){[ordered]@{left=[int]$mainNow[1];top=[int]$mainNow[2];width=[int]$mainNow[3];height=[int]$mainNow[4];showCmd=[int]$mainNow[6];minimized=$minimized}}else{$null}
  statusHint=$hint; hintVisible=($hint.Count -gt 0)
  statusSample=@($texts | Select-Object -First 10)
  logFile=(Join-Path $logs 'immersive-open.log'); logExists=(Test-Path (Join-Path $logs 'immersive-open.log'))
  screenshots=@($beforeShot,$afterShot)
}
$out = Join-Path $OutDir ("legacy-f11-native-{0}.json" -f $stamp)
$doc | ConvertTo-Json -Depth 7 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
Write-Host ("immersive={0} hint={1} minimized={2} nav={3}" -f ($null -ne $immersive), $doc.hintVisible, $minimized, (($navs | Select-Object -First 4) -join '/'))
if ($immersive) {
  [LF]::SetForegroundWindow([IntPtr][int64]$immersive[0]) | Out-Null
  Start-Sleep -Milliseconds 500
  [LF]::Key([IntPtr][int64]$immersive[0], 0x1B) | Out-Null  # Esc
  Start-Sleep -Seconds 2
  $extra = @([LF]::V([uint32]$proc.Id) | Where-Object { ($_ -split '\|',8)[7] -ne 'New Manga' }).Count
  $afterMain = $null
  foreach ($l in [LF]::V([uint32]$proc.Id)) { $p = $l -split '\|',8; if ($p[7] -eq 'New Manga') { $afterMain = $p } }
  $afterShot = Capture 'legacy-after-esc'
  # N-012: persist the post-Esc state instead of only printing it.
  $doc.afterEsc = [ordered]@{
    extraWindows = $extra
    main = if ($afterMain) { [ordered]@{ left=[int]$afterMain[1]; top=[int]$afterMain[2]; width=[int]$afterMain[3]; height=[int]$afterMain[4]; hasCaption=($afterMain[5] -eq '1'); showCmd=[int]$afterMain[6] } } else { $null }
    screenshot = $afterShot
  }
} else {
  $doc.afterEsc = [ordered]@{ extraWindows = $null; main = $null; screenshot = $null; note = 'immersive not opened; Esc not sent' }
}

# N-012: bind the artefact to the build and the live topology.
$doc.build = [ordered]@{
  exeSha256 = (Get-FileHash -Algorithm SHA256 -Path $exe).Hash.ToLowerInvariant()
  exeMtime = (Get-Item $exe).LastWriteTime.ToString('o')
  repoHead = (& git -C $repo rev-parse HEAD).Trim()
}
$probeOut = Join-Path $root 'probe'
& pwsh -NoProfile -File (Join-Path $repo 'verification/FEA-07-AC5-NATIVE-1/tools/probe-displays.ps1') -OutDir $probeOut -Label 'legacy-session' 2>&1 | Out-Null
$probeFile = Get-ChildItem $probeOut -Filter 'displays-legacy-session-*.json' -ErrorAction SilentlyContinue | Sort-Object LastWriteTime | Select-Object -Last 1
if ($probeFile) {
  $probeJson = Get-Content -Raw $probeFile.FullName | ConvertFrom-Json
  $doc.displaysNow = @($probeJson.displays | ForEach-Object { [ordered]@{ gdiDevice=$_.gdiDevice; friendlyName=$_.friendlyName; width=$_.width; height=$_.height; dpi=$_.dpi; scalePercent=$_.scalePercent; primary=$_.primary } })
} else {
  $doc.displaysNow = @()
}
$doc | ConvertTo-Json -Depth 9 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved (with afterEsc/build/displays): $out"

if (-not $proc.HasExited) { $proc.Kill($true); $proc.WaitForExit(5000) | Out-Null; Write-Host 'app closed' }
