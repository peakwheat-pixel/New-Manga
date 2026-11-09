# FEA-07-AC5-NATIVE-1 / undock-os.ps1
# OS 级拔屏：应用窗口在 4K 上 → 禁用 4K → 断言窗口回到 2K 且进程存活 → 重新启用 4K → 校验。
[CmdletBinding()]
param([string]$OutDir = "", [int]$SettleMs = 2000)
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
using System.Text;
public static class Undock2 {
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
  [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
  public struct DISPLAY_DEVICE {
    public int cb; [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)] public string DeviceName;
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 128)] public string DeviceString;
    public int StateFlags; [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 128)] public string DeviceID;
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 128)] public string DeviceKey;
  }
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int left, top, right, bottom; }
  [StructLayout(LayoutKind.Sequential)] public struct POINT { public int x, y; }
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern bool EnumDisplayDevicesW(string dev, uint i, ref DISPLAY_DEVICE dd, uint flags);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern bool EnumDisplaySettingsW(string dev, int mode, ref DEVMODE dm);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int ChangeDisplaySettingsExW(string dev, ref DEVMODE dm, IntPtr hwnd, uint flags, IntPtr param);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern uint GetDpiForWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr a, int x, int y, int cx, int cy, uint f);
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr v);
  [DllImport("user32.dll")] public static extern IntPtr MonitorFromPoint(POINT pt, uint flags);
  [DllImport("shcore.dll")] public static extern int GetDpiForMonitor(IntPtr h, int t, out uint dx, out uint dy);

  public static DEVMODE NewDevMode() { var dm = new DEVMODE(); dm.dmSize = (ushort)Marshal.SizeOf(dm); return dm; }
  public static string[] Active() {
    var list = new List<string>();
    for (uint i = 0; i < 16; i++) {
      var dd = new DISPLAY_DEVICE(); dd.cb = Marshal.SizeOf(dd);
      if (!EnumDisplayDevicesW(null, i, ref dd, 0)) break;
      if ((dd.StateFlags & 0x1) == 0) continue;
      var dm = NewDevMode();
      if (!EnumDisplaySettingsW(dd.DeviceName, -1, ref dm)) continue;
      SetProcessDpiAwarenessContext(new IntPtr(-4));
      var pt = new POINT(); pt.x = dm.dmPositionX + (int)(dm.dmPelsWidth / 2); pt.y = dm.dmPositionY + (int)(dm.dmPelsHeight / 2);
      IntPtr h = MonitorFromPoint(pt, 2); uint dx = 0, dy = 0; GetDpiForMonitor(h, 0, out dx, out dy);
      list.Add(string.Format("{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}|{8}", dd.DeviceName, dm.dmPelsWidth, dm.dmPelsHeight, dm.dmDisplayFrequency, dm.dmPositionX, dm.dmPositionY, dx, Math.Round(dx / 96.0 * 100), ((dd.StateFlags & 0x4) != 0) ? 1 : 0));
    }
    return list.ToArray();
  }
  public static string Disable(string dev) {
    var dm = NewDevMode(); dm.dmPelsWidth = 0; dm.dmPelsHeight = 0; dm.dmFields = 0x00080000 | 0x00100000;
    return "rc=" + ChangeDisplaySettingsExW(dev, ref dm, IntPtr.Zero, 0x00000001, IntPtr.Zero);
  }
  public static string Enable(string dev, int w, int h, int hz, int x, int y) {
    var dm = NewDevMode();
    if (!EnumDisplaySettingsW(dev, -1, ref dm)) return "ERR|mode";
    dm.dmPelsWidth = (uint)w; dm.dmPelsHeight = (uint)h; dm.dmPositionX = x; dm.dmPositionY = y;
    if (hz > 0) dm.dmDisplayFrequency = (uint)hz;
    dm.dmFields = 0x00080000 | 0x00100000 | 0x00000020 | 0x00400000;
    return "rc=" + ChangeDisplaySettingsExW(dev, ref dm, IntPtr.Zero, 0x00000001, IntPtr.Zero);
  }
  public static IntPtr MainWindow(uint pid) {
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
    uint dpi = GetDpiForWindow(h);
    return string.Format("{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}", r.left, r.top, r.right - r.left, r.bottom - r.top, dpi, Math.Round(dpi / 96.0 * 100), r.right, r.bottom);
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
function State { @([Undock2]::Active() | ForEach-Object { $p = $_ -split '\|'; [pscustomobject]@{ device = $p[0]; width = [int]$p[1]; height = [int]$p[2]; hz = [int]$p[3]; x = [int]$p[4]; y = [int]$p[5]; dpi = [int]$p[6]; percent = [int]$p[7]; primary = ($p[8] -eq '1') } }) }

$before = @(State)
Write-Host ("before: " + (($before | ForEach-Object { "{0} {1}x{2}@{3}%({4},{5})" -f $_.device,$_.width,$_.height,$_.percent,$_.x,$_.y }) -join ' | '))
$primary = $before | Where-Object { $_.primary } | Select-Object -First 1
$secondary = $before | Where-Object { -not $_.primary } | Select-Object -First 1
if (-not $secondary) { throw 'no secondary display' }

$root = Join-Path $env:TEMP ("nm-fea07-undock2-{0}" -f $stamp)
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
for ($i = 0; $i -lt 40; $i++) { Start-Sleep -Milliseconds 500; $main = [Undock2]::MainWindow([uint32]$proc.Id); if ($main -ne [IntPtr]::Zero) { break } }
if ($main -eq [IntPtr]::Zero) { throw 'main window not found' }

# move window onto secondary
$w = [int]($secondary.width * 0.45); $h = [int]($secondary.height * 0.45)
$mx = $secondary.x + [int](($secondary.width - $w) / 2); $my = $secondary.y + 200
[Undock2]::SetWindowPos($main, [IntPtr]::Zero, $mx, $my, $w, $h, 0x0004) | Out-Null
Start-Sleep -Milliseconds ($SettleMs + 800)
$onSecondary = ([Undock2]::Rect($main)) -split '\|'
$shotBefore = Capture $secondary.x $secondary.y $secondary.width $secondary.height (Join-Path $shots ("{0}-undock-before.png" -f $stamp))

$dsOut = & DisplaySwitch.exe /internal 2>&1 | Out-String
Write-Host ("DisplaySwitch /internal: " + $dsOut.Trim())
Start-Sleep -Milliseconds ($SettleMs + 1500)
$alive = -not $proc.HasExited
$after = @(State)
Write-Host ("after disable: " + (($after | ForEach-Object { "{0} {1}x{2}@{3}%({4},{5})" -f $_.device,$_.width,$_.height,$_.percent,$_.x,$_.y }) -join ' | '))
$moved = ([Undock2]::Rect($main)) -split '\|'
$shotAfter = Capture $primary.x $primary.y $primary.width $primary.height (Join-Path $shots ("{0}-undock-after.png" -f $stamp))

$dsOut2 = & DisplaySwitch.exe /extend 2>&1 | Out-String
Write-Host ("DisplaySwitch /extend: " + $dsOut2.Trim())
Start-Sleep -Milliseconds 1500
$now = @(State)
if (-not ($now | Where-Object { $_.device -eq $secondary.device })) {
  Write-Host ("re-enable via ChangeDisplaySettingsEx: " + ([Undock2]::Enable($secondary.device, $secondary.width, $secondary.height, $secondary.hz, $secondary.x, $secondary.y)))
}
Start-Sleep -Milliseconds ($SettleMs + 1200)
$restored = @(State)
$final = ([Undock2]::Rect($main)) -split '\|'
$shotRestored = Capture $primary.x $primary.y $primary.width $primary.height (Join-Path $shots ("{0}-undock-restored.png" -f $stamp))

$doc = [ordered]@{
  case = 'undock-os-disable'; capturedAt = (Get-Date -Format o)
  app = [ordered]@{ pid = $proc.Id; exe = $exe; args = $appArgs }
  before = $before; afterDisable = $after; afterReenable = $restored
  window = [ordered]@{
    onSecondary = [ordered]@{ left = [int]$onSecondary[0]; top = [int]$onSecondary[1]; width = [int]$onSecondary[2]; height = [int]$onSecondary[3]; dpi = [int]$onSecondary[4]; percent = [int]$onSecondary[5] }
    afterDisable = [ordered]@{ left = [int]$moved[0]; top = [int]$moved[1]; width = [int]$moved[2]; height = [int]$moved[3]; dpi = [int]$moved[4]; percent = [int]$moved[5]; appAlive = $alive; containedInPrimary = (([int]$moved[0] -ge $primary.x) -and (([int]$moved[0] + [int]$moved[2]) -le ($primary.x + $primary.width))) }
    afterReenable = [ordered]@{ left = [int]$final[0]; top = [int]$final[1]; width = [int]$final[2]; height = [int]$final[3]; dpi = [int]$final[4]; percent = [int]$final[5]; appAlive = (-not $proc.HasExited) }
  }
  screenshots = @($shotBefore, $shotAfter, $shotRestored)
}
$out = Join-Path $OutDir ("undock-os-{0}.json" -f $stamp)
$doc | ConvertTo-Json -Depth 8 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
Write-Host ("onSecondary=({0},{1}) {2}x{3}@{4}% | afterDisable=({5},{6}) {7}x{8}@{9}% alive={10} inPrimary={11}" -f `
  $onSecondary[0],$onSecondary[1],$onSecondary[2],$onSecondary[3],$onSecondary[5],$moved[0],$moved[1],$moved[2],$moved[3],$moved[5],$alive,$doc.window.afterDisable.containedInPrimary)
if (-not $proc.HasExited) { $proc.Kill($true); $proc.WaitForExit(5000) | Out-Null; Write-Host 'app closed' }
