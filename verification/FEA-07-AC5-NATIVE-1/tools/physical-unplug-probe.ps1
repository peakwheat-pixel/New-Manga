# FEA-07-AC5-NATIVE-1 / physical-unplug-probe.ps1
# 有序物理拔屏：窗口置于 4K → 轮询等待 4K 消失（用户拔线）→ 抓窗口迁移证据 → 等待 4K 回来 → 抓恢复。
[CmdletBinding()]
param(
  [string]$OutDir = "",
  [string]$TargetFriendly = "PHL 279M1RV",
  [int]$WaitUnplugSec = 240,
  [int]$WaitReplugSec = 300
)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-AC5-NATIVE-1\evidence' }
$shots = Join-Path $OutDir 'screenshots'; New-Item -ItemType Directory -Force -Path $OutDir, $shots | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
Add-Type -AssemblyName System.Drawing

$cs = @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
public static class PhysApi {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int left, top, right, bottom; }
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
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern uint GetDpiForWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr a, int x, int y, int cx, int cy, uint f);
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr v);

  public static string[] Active() {
    var list = new List<string>();
    for (uint i = 0; i < 16; i++) {
      var dd = new DISPLAY_DEVICE(); dd.cb = Marshal.SizeOf(dd);
      if (!EnumDisplayDevicesW(null, i, ref dd, 0)) break;
      if ((dd.StateFlags & 0x1) == 0) continue;
      var dm = new DEVMODE(); dm.dmSize = (ushort)Marshal.SizeOf(dm);
      if (!EnumDisplaySettingsW(dd.DeviceName, -1, ref dm)) continue;
      list.Add(string.Format("{0}|{1}|{2}|{3}|{4}|{5}|{6}", dd.DeviceName, dd.DeviceString, dm.dmPelsWidth, dm.dmPelsHeight, dm.dmPositionX, dm.dmPositionY, dm.dmDisplayFrequency));
    }
    return list.ToArray();
  }
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
function Displays { @([PhysApi]::Active() | ForEach-Object { $p = $_ -split '\|'; [pscustomobject]@{ device = $p[0]; adapter = $p[1]; width = [int]$p[2]; height = [int]$p[3]; x = [int]$p[4]; y = [int]$p[5]; hz = [int]$p[6] } }) }

# 找目标屏（4K）的 EDID 友好名：用 probe 工具的映射
$probe = & pwsh -NoProfile -File (Join-Path $PSScriptRoot 'probe-displays.ps1') -OutDir $OutDir -Label 'physical-probe' 2>&1 | Out-String
$latest = Get-ChildItem $OutDir -Filter 'displays-physical-probe-*.json' | Sort-Object LastWriteTime | Select-Object -Last 1
$disp = Get-Content -Raw $latest.FullName | ConvertFrom-Json
$target = $disp.displays | Where-Object { $_.friendlyName -eq $TargetFriendly } | Select-Object -First 1
if (-not $target) { throw "target display '$TargetFriendly' not active; current: $($disp.displays.friendlyName -join ', ')" }
Write-Host ("target 4K: {0} {1}x{2} @({3},{4}) scale={5}%" -f $target.friendlyName,$target.width,$target.height,$target.left,$target.top,$target.scalePercent)

$root = Join-Path $env:TEMP ("nm-fea07-phys-{0}" -f $stamp)
$dr = Join-Path $root 'data'; $ld = Join-Path $root 'logs'; $th = Join-Path $root 'theme'
New-Item -ItemType Directory -Force -Path $dr, $ld, $th | Out-Null
$exe = Join-Path $repo 'apps\desktop-avalonia\src\NewManga.App\bin\Release\net9.0\NewManga.App.exe'
$appArgs = @('--data-root', $dr, '--log-dir', $ld, '--theme-home', $th, '--shell=v2')
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $exe; $psi.WorkingDirectory = (Split-Path $exe -Parent); $psi.UseShellExecute = $false; $psi.CreateNoWindow = $true
foreach ($a in $appArgs) { $psi.ArgumentList.Add($a) }
$proc = [System.Diagnostics.Process]::Start($psi)
Write-Host "launched pid=$($proc.Id)"
$main = [IntPtr]::Zero
for ($i = 0; $i -lt 40; $i++) { Start-Sleep -Milliseconds 500; $main = [PhysApi]::Main([uint32]$proc.Id); if ($main -ne [IntPtr]::Zero) { break } }
if ($main -eq [IntPtr]::Zero) { throw 'window not found' }

# 放到 4K 上
$w = [int]($target.width * 0.45); $h = [int]($target.height * 0.45)
$mx = $target.left + [int](($target.width - $w) / 2); $my = $target.top + 200
[PhysApi]::SetWindowPos($main, [IntPtr]::Zero, $mx, $my, $w, $h, 0x0004) | Out-Null
Start-Sleep -Milliseconds 1500
$on4k = ([PhysApi]::Rect($main)) -split '\|'
$shot4k = Capture $target.left $target.top $target.width $target.height (Join-Path $shots ("{0}-phys-on4k.png" -f $stamp))
Write-Host ("window on 4K: ({0},{1}) {2}x{3}@{4}% — NOW UNPLUG 4K" -f $on4k[0],$on4k[1],$on4k[2],$on4k[3],$on4k[5])

# 等待 4K 消失
$gone = $false; $t0 = Get-Date
while (((Get-Date) - $t0).TotalSeconds -lt $WaitUnplugSec) {
  Start-Sleep -Milliseconds 900
  $now = Displays
  if (-not ($now | Where-Object { $_.device -eq $target.gdiDevice })) { $gone = $true; break }
}
if (-not $gone) { throw "4K did not disappear within $WaitUnplugSec s" }
$tGone = Get-Date
Start-Sleep -Milliseconds 1200
$afterGone = Displays
$rectAfter = ([PhysApi]::Rect($main)) -split '\|'
$alive = -not $proc.HasExited
$primary = $afterGone | Sort-Object x | Select-Object -First 1
$l = [int]$rectAfter[0]; $t = [int]$rectAfter[1]
$r = $l + [int]$rectAfter[2]; $b = $t + [int]$rectAfter[3]
$contained = ($l -ge $primary.x) -and ($t -ge $primary.y) -and ($r -le ($primary.x + $primary.width)) -and ($b -le ($primary.y + $primary.height))
$shotAfter = Capture $primary.x $primary.y $primary.width $primary.height (Join-Path $shots ("{0}-phys-after-unplug.png" -f $stamp))
Write-Host ("4K gone at {0:HH:mm:ss}; window=({1},{2}) {3}x{4}@{5}% alive={6} containedInPrimary={7} — NOW REPLUG 4K" -f $tGone,$rectAfter[0],$rectAfter[1],$rectAfter[2],$rectAfter[3],$rectAfter[5],$alive,$contained)

# 等待 4K 回来
$back = $false; $t1 = Get-Date
while (((Get-Date) - $t1).TotalSeconds -lt $WaitReplugSec) {
  Start-Sleep -Milliseconds 900
  $now = Displays
  if ($now | Where-Object { $_.device -eq $target.gdiDevice }) { $back = $true; break }
}
$tBack = Get-Date
Start-Sleep -Milliseconds 1500
$afterBack = Displays
$rectBack = ([PhysApi]::Rect($main)) -split '\|'
$probe2 = & pwsh -NoProfile -File (Join-Path $PSScriptRoot 'probe-displays.ps1') -OutDir $OutDir -Label 'physical-replug' 2>&1 | Out-String
$latest2 = Get-ChildItem $OutDir -Filter 'displays-physical-replug-*.json' | Sort-Object LastWriteTime | Select-Object -Last 1
$disp2 = Get-Content -Raw $latest2.FullName | ConvertFrom-Json
$shotBack = Capture $primary.x $primary.y $primary.width $primary.height (Join-Path $shots ("{0}-phys-after-replug.png" -f $stamp))

$doc = [ordered]@{
  case = 'physical-unplug'; capturedAt = (Get-Date -Format o)
  app = [ordered]@{ pid = $proc.Id; exe = $exe; args = $appArgs }
  target = [ordered]@{ friendlyName = $target.friendlyName; device = $target.gdiDevice; width = $target.width; height = $target.height; left = $target.left; top = $target.top; scalePercent = $target.scalePercent }
  before = [ordered]@{ displays = $disp.displays; window = [ordered]@{ left = [int]$on4k[0]; top = [int]$on4k[1]; width = [int]$on4k[2]; height = [int]$on4k[3]; dpi = [int]$on4k[4]; percent = [int]$on4k[5] } }
  unplugDetectedAt = $tGone.ToString('o'); replugDetectedAt = $tBack.ToString('o')
  afterUnplug = [ordered]@{ displays = $afterGone; window = [ordered]@{ left = [int]$rectAfter[0]; top = [int]$rectAfter[1]; width = [int]$rectAfter[2]; height = [int]$rectAfter[3]; dpi = [int]$rectAfter[4]; percent = [int]$rectAfter[5]; appAlive = $alive; containedInPrimary = $contained } }
  afterReplug = [ordered]@{ displays = $disp2.displays; window = [ordered]@{ left = [int]$rectBack[0]; top = [int]$rectBack[1]; width = [int]$rectBack[2]; height = [int]$rectBack[3]; dpi = [int]$rectBack[4]; percent = [int]$rectBack[5]; appAlive = (-not $proc.HasExited) } }
  screenshots = @($shot4k, $shotAfter, $shotBack)
}
$out = Join-Path $OutDir ("physical-unplug-{0}.json" -f $stamp)
$doc | ConvertTo-Json -Depth 8 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
if (-not $proc.HasExited) { $proc.Kill($true); $proc.WaitForExit(5000) | Out-Null; Write-Host 'app closed' }
