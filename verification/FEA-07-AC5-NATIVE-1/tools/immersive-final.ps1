# FEA-07-AC5-NATIVE-1 / immersive-final.ps1
# 1) 资源柜点「阅读」进 Reader 页 2) 轮询等「沉浸模式」按钮 3) 点击打开沉浸窗口 4) 采样+截图 5) Esc 关闭校验
[CmdletBinding()]
param([string]$OutDir = "", [string]$ShotDir = "G:\CODEX\New Manga.workspace\FEA-07-AC5-NATIVE-1\ac5-fullscreen")
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-AC5-NATIVE-1\evidence' }
New-Item -ItemType Directory -Force -Path $OutDir, $ShotDir | Out-Null
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes, System.Windows.Forms, System.Drawing

$cs = @'
using System; using System.Collections.Generic; using System.Runtime.InteropServices; using System.Text;
public static class IF {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int left, top, right, bottom; }
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
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
      l.Add(string.Format("{0}|{1}|{2}|{3}|{4}|{5}|{6}", h, r.left,r.top,r.right-r.left,r.bottom-r.top, cap?1:0, t)); return true; }, IntPtr.Zero);
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
function MainWin($procId) {
  $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ProcessIdProperty, $procId)
  $ws = [System.Windows.Automation.AutomationElement]::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children, $c)
  foreach ($w in $ws) { if ($w.Current.ControlType -eq [System.Windows.Automation.ControlType]::Window -and $w.Current.Name -eq 'New Manga') { return $w } }
  return $null
}
function Btn($root, [string]$prefix) {
  if (-not $root) { return $null }
  $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Button)
  $els = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, $c)
  foreach ($e in $els) { $n = $e.Current.Name; if ($n -and $n.StartsWith($prefix)) { return $e } }
  return $null
}
function Invoke2($el) { try { ($el.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)).Invoke(); return $true } catch { return $false } }

$app = Get-Process NewManga.App | Sort-Object StartTime | Select-Object -Last 1
$pidA = $app.Id
$win = MainWin $pidA
$read = Btn $win '阅读'
Write-Host "阅读 button: $([bool]$read)"
if ($read) { Invoke2 $read | Out-Null; Start-Sleep -Seconds 3 }

$imm = $null
for ($i = 0; $i -lt 40; $i++) {
  Start-Sleep -Milliseconds 400
  $win = MainWin $pidA
  $imm = Btn $win '沉浸模式'
  if ($imm) { break }
}
if (-not $imm) {
  Write-Host 'immersive button not found; current buttons:'
  $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Button)
  $win = MainWin $pidA
  if ($win) { $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, $c) | ForEach-Object { if ($_.Current.Name) { Write-Host "  $($_.Current.Name)" } } | Select-Object -First 30 }
  throw 'immersive button missing'
}
Write-Host "found: $($imm.Current.Name)"
$inv = Invoke2 $imm
Write-Host "invoked=$inv"

$found = $null
for ($i = 0; $i -lt 50; $i++) {
  Start-Sleep -Milliseconds 150
  foreach ($l in [IF]::V([uint32]$pidA)) { $p = $l -split '\|',7; if ($p[6] -ne 'New Manga') { $found = $p; break } }
  if ($found) { break }
}
$shot = $null
if ($found) {
  $shot = Capture 'immersive-open'
  Write-Host ("IMMERSIVE hwnd={0} rect=({1},{2}) {3}x{4} caption={5} title={6}" -f $found[0],$found[1],$found[2],$found[3],$found[4],$found[5],$found[6])
  [IF]::SetForegroundWindow([IntPtr][int64]$found[0]) | Out-Null
  Start-Sleep -Milliseconds 600
  [System.Windows.Forms.SendKeys]::SendWait('{ESC}')
  Start-Sleep -Milliseconds 2000
  $extra = @([IF]::V([uint32]$pidA) | Where-Object { ($_ -split '\|',7)[6] -ne 'New Manga' }).Count
  Write-Host "after ESC extra=$extra"
}
$doc = [ordered]@{ action='immersive-final'; capturedAt=(Get-Date -Format o); pid=$pidA; button=$imm.Current.Name; invoked=$inv; found=($null -ne $found); immersive=if($found){[ordered]@{left=[int]([int64]$found[1]);top=[int]([int64]$found[2]);width=[int]([int64]$found[3]);height=[int]([int64]$found[4]);hasCaption=($found[5] -eq '1');title=$found[6];coversPrimary=(([int64]$found[1] -le 0)-and([int64]$found[2] -le 0)-and([int64]$found[3] -ge 2560)-and([int64]$found[4] -ge 1440))}}else{$null}; screenshot=$shot }
$out = Join-Path $OutDir ("immersive-final-{0}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$doc | ConvertTo-Json -Depth 6 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
