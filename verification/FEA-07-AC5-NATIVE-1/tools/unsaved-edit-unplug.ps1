# FEA-07-AC5-NATIVE-1 / unsaved-edit-unplug.ps1
# 未 flush 编辑态 + 显示移除：命令面板输入未提交文本 → OS 级拔屏 → 断言 app 存活且输入缓冲保留 → 恢复。
[CmdletBinding()]
param([string]$OutDir = "")
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-AC5-NATIVE-1\evidence' }
$shots = Join-Path $OutDir 'screenshots'; New-Item -ItemType Directory -Force -Path $OutDir, $shots | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
Add-Type -AssemblyName System.Drawing, UIAutomationClient, UIAutomationTypes, System.Windows.Forms

$cs = @'
using System;
using System.Runtime.InteropServices;
public static class UnApi {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int left, top, right, bottom; }
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern uint GetDpiForWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr v);
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
}
'@
Add-Type -TypeDefinition $cs -ErrorAction Stop

function Capture([int]$x, [int]$y, [int]$w, [int]$h, [string]$file) {
  $bmp = New-Object System.Drawing.Bitmap $w, $h
  $g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($x, $y, 0, 0, (New-Object System.Drawing.Size $w, $h)); $g.Dispose()
  $bmp.Save($file, [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
  [pscustomobject]@{ file = (Split-Path $file -Leaf); width = $w; height = $h; sha256 = (Get-FileHash -Algorithm SHA256 -Path $file).Hash.ToLowerInvariant() }
}
function Displays {
  $sig = @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
public static class UnDisplays {
  [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
  public struct DISPLAY_DEVICE { public int cb; [MarshalAs(UnmanagedType.ByValTStr, SizeConst=32)] public string DeviceName; [MarshalAs(UnmanagedType.ByValTStr, SizeConst=128)] public string DeviceString; public int StateFlags; [MarshalAs(UnmanagedType.ByValTStr, SizeConst=128)] public string DeviceID; [MarshalAs(UnmanagedType.ByValTStr, SizeConst=128)] public string DeviceKey; }
  [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
  public struct DEVMODE {
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)] public string dmDeviceName;
    public ushort dmSpecVersion, dmDriverVersion, dmSize, dmDriverExtra; public uint dmFields;
    public int dmPositionX, dmPositionY; public uint dmDisplayOrientation, dmDisplayFixedOutput;
    public short dmColor, dmDuplex, dmYResolution, dmTTOption, dmCollate;
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)] public string dmFormName;
    public ushort dmLogPixels; public uint dmBitsPerPel, dmPelsWidth, dmPelsHeight, dmDisplayFlags, dmDisplayFrequency;
    public uint dmICMMethod, dmICMIntent, dmMediaType, dmDitherType, dmReserved1, dmReserved2, dmPanningWidth, dmPanningHeight;
  }
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern bool EnumDisplayDevicesW(string dev, uint i, ref DISPLAY_DEVICE dd, uint flags);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern bool EnumDisplaySettingsW(string dev, int mode, ref DEVMODE dm);
  public static string[] All() {
    var list = new List<string>();
    for (uint i = 0; i < 16; i++) {
      var dd = new DISPLAY_DEVICE(); dd.cb = Marshal.SizeOf(dd);
      if (!EnumDisplayDevicesW(null, i, ref dd, 0)) break;
      if ((dd.StateFlags & 0x1) == 0) continue;
      var dm = new DEVMODE(); dm.dmSize = (ushort)Marshal.SizeOf(dm);
      if (!EnumDisplaySettingsW(dd.DeviceName, -1, ref dm)) continue;
      list.Add(string.Format("{0}|{1}|{2}|{3}|{4}", dd.DeviceName, dm.dmPelsWidth, dm.dmPelsHeight, dm.dmPositionX, dm.dmPositionY));
    }
    return list.ToArray();
  }
}
'@
  if (-not ('UnDisplays' -as [type])) { Add-Type -TypeDefinition $sig -ErrorAction Stop }
  @([UnDisplays]::All() | ForEach-Object { $p = $_ -split '\|'; [pscustomobject]@{ device = $p[0]; width = [int]$p[1]; height = [int]$p[2]; x = [int]$p[3]; y = [int]$p[4] } })
}
function UiaWindow($procId) {
  $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ProcessIdProperty, $procId)
  $wins = [System.Windows.Automation.AutomationElement]::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children, $cond)
  foreach ($w in $wins) { if ($w.Current.ControlType -eq [System.Windows.Automation.ControlType]::Window) { return $w } }
  return $null
}
function PaletteValue($win) {
  $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Edit)
  $edits = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, $cond)
  $vals = @()
  foreach ($e in $edits) {
    try { $vals += ($e.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)).Current.Value } catch { $vals += $null }
  }
  return @($vals | Where-Object { $_ -ne $null -and $_ -ne '' })
}

$root = Join-Path $env:TEMP ("nm-fea07-unsaved-{0}" -f $stamp)
$dr = Join-Path $root 'data'; $ld = Join-Path $root 'logs'; $th = Join-Path $root 'theme'
New-Item -ItemType Directory -Force -Path $dr, $ld, $th | Out-Null
$exe = Join-Path $repo 'apps\desktop-avalonia\src\NewManga.App\bin\Release\net9.0\NewManga.App.exe'
$appArgs = @('--data-root', $dr, '--log-dir', $ld, '--theme-home', $th, '--shell=v2')
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $exe; $psi.WorkingDirectory = (Split-Path $exe -Parent); $psi.UseShellExecute = $false; $psi.CreateNoWindow = $true
foreach ($a in $appArgs) { $psi.ArgumentList.Add($a) }
$proc = [System.Diagnostics.Process]::Start($psi)
$main = [IntPtr]::Zero
for ($i = 0; $i -lt 50; $i++) { Start-Sleep -Milliseconds 500; $main = [UnApi]::Main([uint32]$proc.Id); if ($main -ne [IntPtr]::Zero) { break } }
if ($main -eq [IntPtr]::Zero) { throw 'window not found' }
Start-Sleep -Milliseconds 2000
$before = Displays
$win = UiaWindow $proc.Id
[UnApi]::SetForegroundWindow($main) | Out-Null
Start-Sleep -Milliseconds 400
[System.Windows.Forms.SendKeys]::SendWait('^k')
Start-Sleep -Milliseconds 1200
$edits = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Edit)))
if ($edits.Count -eq 0) { throw 'palette edit not found' }
$target = $edits[$edits.Count - 1]
try { $target.SetFocus() } catch {}
Start-Sleep -Milliseconds 400
[System.Windows.Forms.SendKeys]::SendWait('draft1')
Start-Sleep -Milliseconds 900
$valBefore = PaletteValue $win
if ($valBefore.Count -eq 0) { throw 'palette buffer empty after typing' }
$shot1 = Capture $before[0].x $before[0].y $before[0].width $before[0].height (Join-Path $shots ("{0}-unsaved-before.png" -f $stamp))

$ds = & DisplaySwitch.exe /internal 2>&1 | Out-String
Start-Sleep -Milliseconds 3200
$during = Displays
$valDuring = PaletteValue $win
$alive = -not $proc.HasExited
$rectDuring = ([UnApi]::Rect($main)) -split '\|'
$shot2 = Capture $during[0].x $during[0].y $during[0].width $during[0].height (Join-Path $shots ("{0}-unsaved-after-unplug.png" -f $stamp))

& DisplaySwitch.exe /extend 2>&1 | Out-Null
Start-Sleep -Milliseconds 3200
$after = Displays
$valAfter = PaletteValue $win
$rectAfter = ([UnApi]::Rect($main)) -split '\|'
$shot3 = Capture $after[0].x $after[0].y $after[0].width $after[0].height (Join-Path $shots ("{0}-unsaved-after-restore.png" -f $stamp))

$doc = [ordered]@{
  case = 'unsaved-edit-unplug'; capturedAt = (Get-Date -Format o)
  app = [ordered]@{ pid = $proc.Id; exe = $exe; args = $appArgs; dataRoot = $dr }
  before = [ordered]@{ displays = $before; paletteValues = $valBefore; window = [ordered]@{ left = [int]$rectDuring[0]; top = [int]$rectDuring[1] } }
  afterUnplug = [ordered]@{ displaySwitch = $ds.Trim(); displays = $during; paletteValues = $valDuring; appAlive = $alive; window = [ordered]@{ left = [int]$rectDuring[0]; top = [int]$rectDuring[1]; width = [int]$rectDuring[2]; height = [int]$rectDuring[3]; dpi = [int]$rectDuring[4]; percent = [int]$rectDuring[5] } }
  afterRestore = [ordered]@{ displays = $after; paletteValues = $valAfter; appAlive = (-not $proc.HasExited); window = [ordered]@{ left = [int]$rectAfter[0]; top = [int]$rectAfter[1]; width = [int]$rectAfter[2]; height = [int]$rectAfter[3]; dpi = [int]$rectAfter[4]; percent = [int]$rectAfter[5] } }
  bufferRetainedAfterUnplug = [bool](($valDuring -join '|') -match 'draft')
  screenshots = @($shot1, $shot2, $shot3)
}
$out = Join-Path $OutDir ("unsaved-edit-unplug-{0}.json" -f $stamp)
$doc | ConvertTo-Json -Depth 8 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
Write-Host ("bufferRetainedAfterUnplug={0} appAlive={1} beforeValues={2} duringValues={3}" -f $doc.bufferRetainedAfterUnplug,$alive,($valBefore -join '|'),($valDuring -join '|'))
if (-not $proc.HasExited) { $proc.Kill($true); $proc.WaitForExit(5000) | Out-Null; Write-Host 'app closed' }
