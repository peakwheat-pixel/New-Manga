# FEA-07-IMMERSIVE-F11-1 / verify-immersive-button.ps1
# 新构建应用：进 Reader 页 → 点「沉浸模式 (Esc/H/F)」按钮 →
#   成功：沉浸窗口出现（采样/截图/Esc 关闭/主窗恢复）
#   失败：状态栏出现「全屏阅读器打开失败（已恢复主窗）」且主窗未最小化（兜底验收）
[CmdletBinding()]
param([string]$OutDir = "", [string]$ShotDir = "G:\CODEX\New Manga.workspace\FEA-07-IMMERSIVE-F11-1\shots")
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-IMMERSIVE-F11-1\evidence' }
New-Item -ItemType Directory -Force -Path $OutDir, $ShotDir | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
Add-Type -AssemblyName System.Drawing, UIAutomationClient, UIAutomationTypes, System.Windows.Forms

$cs = @'
using System; using System.Collections.Generic; using System.Runtime.InteropServices; using System.Text;
public static class VB {
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
function Btn($root, [string]$prefix) {
  if (-not $root) { return $null }
  $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Button)
  foreach ($e in $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, $c)) {
    $n = $e.Current.Name
    if ($n -and $n.StartsWith($prefix)) { return $e }
  }
  return $null
}
function Invoke2($el) { try { ($el.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)).Invoke(); return $true } catch { return $false } }
function StatusTexts($win) {
  if (-not $win) { return @() }
  $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Text)
  $out = @()
  foreach ($e in $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, $c)) {
    $n = $e.Current.Name
    if ($n -and $n -like '*全屏阅读器打开失败*') { $out += $n }
  }
  return $out
}

$sidecar = 'G:\CODEX\New Manga.workspace\FEA-07-AC5-NATIVE-1\sidecar'
$sessionData = 'G:\CODEX\New Manga.workspace\FEA-07-AC5-NATIVE-1\reader-session\data'
$root = Join-Path 'G:\CODEX\New Manga.workspace\FEA-07-IMMERSIVE-F11-1' ("btn-" + $stamp)
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
for ($i = 0; $i -lt 60; $i++) { Start-Sleep -Milliseconds 500; foreach ($l in [VB]::V([uint32]$proc.Id)) { $p = $l -split '\|',8; if ($p[7] -eq 'New Manga') { $main = $p } }; if ($main) { break } }
if (-not $main) { throw 'main window not found' }
Start-Sleep -Seconds 8
$win = UiaWindow $proc.Id
$read = Btn $win '阅读'
Write-Host "阅读 button=$([bool]$read)"
if ($read) { Invoke2 $read | Out-Null; Start-Sleep -Seconds 3 }

$imm = $null
for ($i = 0; $i -lt 40; $i++) { Start-Sleep -Milliseconds 400; $win = UiaWindow $proc.Id; $imm = Btn $win '沉浸模式'; if ($imm) { break } }
$beforeShot = Capture 'button-before'
$invoked = $false
if ($imm) { $invoked = Invoke2 $imm; Write-Host "immersive button found & invoked=$invoked" } else { Write-Host 'immersive button NOT found' }
Start-Sleep -Milliseconds 400

$immersive = $null; $fallback = @()
for ($i = 0; $i -lt 60; $i++) {
  Start-Sleep -Milliseconds 150
  foreach ($l in [VB]::V([uint32]$proc.Id)) { $p = $l -split '\|',8; if ($p[7] -ne 'New Manga') { $immersive = $p; break } }
  if ($immersive) { break }
  $fallback = @(StatusTexts (UiaWindow $proc.Id))
  if ($fallback.Count -gt 0) { break }
}
$afterShot = Capture 'button-after'
$mainNow = $null
foreach ($l in [VB]::V([uint32]$proc.Id)) { $p = $l -split '\|',8; if ($p[7] -eq 'New Manga') { $mainNow = $p } }
$minimized = if ($mainNow) { ([int]$mainNow[6] -eq 7) -or ([int]$mainNow[1] -le -30000) } else { $true }

$doc = [ordered]@{
  case='immersive-button-native'; capturedAt=(Get-Date -Format o)
  app=[ordered]@{ pid=$proc.Id; exe=$exe; args=$args; sidecar=$sidecar; dataRoot=$sessionData; logDir=$logs }
  buttonFound=[bool]$imm; buttonInvoked=$invoked
  immersive=if($immersive){[ordered]@{left=[int]$immersive[1];top=[int]$immersive[2];width=[int]$immersive[3];height=[int]$immersive[4];hasCaption=($immersive[5]-eq'1');title=$immersive[7];coversPrimary=(([int64]$immersive[1] -le 0)-and([int64]$immersive[2] -le 0)-and([int64]$immersive[3] -ge 2560)-and([int64]$immersive[4] -ge 1440))}}else{$null}
  mainWindow=if($mainNow){[ordered]@{left=[int]$mainNow[1];top=[int]$mainNow[2];width=[int]$mainNow[3];height=[int]$mainNow[4];showCmd=[int]$mainNow[6];minimized=$minimized}}else{$null}
  fallbackTexts=$fallback
  fallbackVisible=[bool]($fallback.Count -gt 0)
  mainNotMinimized=-not $minimized
  screenshots=@($beforeShot,$afterShot)
}
$out = Join-Path $OutDir ("immersive-button-native-{0}.json" -f $stamp)
$doc | ConvertTo-Json -Depth 7 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
if ($immersive) { [System.Windows.Forms.SendKeys]::SendWait('{ESC}'); Start-Sleep -Seconds 2; $after = @([VB]::V([uint32]$proc.Id) | Where-Object { ($_ -split '\|',8)[7] -ne 'New Manga' }).Count; Write-Host "after ESC extra=$after" }
if (-not $proc.HasExited) { $proc.Kill($true); $proc.WaitForExit(5000) | Out-Null; Write-Host 'app closed' }
