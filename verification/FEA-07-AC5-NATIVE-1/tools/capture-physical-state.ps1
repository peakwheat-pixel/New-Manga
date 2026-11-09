# FEA-07-AC5-NATIVE-1 / capture-physical-state.ps1
# 抓当前显示拓扑 + 指定进程主窗几何/DPI/存活 + 主屏截图（用于物理拔屏前后对照）。
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][string]$Label,
  [int]$ProcessId = 0,
  [string]$OutDir = ""
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
public static class PhysState {
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
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr v);

  public static string[] Displays() {
    var list = new List<string>();
    for (uint i = 0; i < 16; i++) {
      var dd = new DISPLAY_DEVICE(); dd.cb = Marshal.SizeOf(dd);
      if (!EnumDisplayDevicesW(null, i, ref dd, 0)) break;
      string state = ((dd.StateFlags & 0x1) != 0) ? "active" : "inactive";
      string primary = ((dd.StateFlags & 0x4) != 0) ? "primary" : "-";
      var dm = new DEVMODE(); dm.dmSize = (ushort)Marshal.SizeOf(dm);
      bool ok = EnumDisplaySettingsW(dd.DeviceName, -1, ref dm);
      list.Add(string.Format("{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}|{8}", dd.DeviceName, dd.DeviceString, state, primary,
        ok ? (int)dm.dmPelsWidth : 0, ok ? (int)dm.dmPelsHeight : 0, ok ? dm.dmPositionX : 0, ok ? dm.dmPositionY : 0, ok ? (int)dm.dmDisplayFrequency : 0));
    }
    return list.ToArray();
  }
  public static string WindowOf(uint pid) {
    SetProcessDpiAwarenessContext(new IntPtr(-4));
    var rows = new List<string>();
    EnumWindows((h, l) => {
      uint p; GetWindowThreadProcessId(h, out p);
      if (p != pid || !IsWindowVisible(h)) return true;
      RECT r; GetWindowRect(h, out r);
      if (r.right - r.left < 200) return true;
      rows.Add(string.Format("{0}|{1}|{2}|{3}|{4}|{5}|{6}", r.left, r.top, r.right - r.left, r.bottom - r.top, GetDpiForWindow(h), Math.Round(GetDpiForWindow(h) / 96.0 * 100), (int)h));
      return true;
    }, IntPtr.Zero);
    return rows.Count > 0 ? rows[0] : "";
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

$displays = @([PhysState]::Displays() | ForEach-Object {
  $p = $_ -split '\|'
  [pscustomobject]@{ device = $p[0]; adapter = $p[1]; state = $p[2]; role = $p[3]; width = [int]$p[4]; height = [int]$p[5]; x = [int]$p[6]; y = [int]$p[7]; hz = [int]$p[8] }
})
$active = $displays | Where-Object { $_.state -eq 'active' }
$primary = $active | Where-Object { $_.role -eq 'primary' } | Select-Object -First 1
if (-not $primary) { $primary = $active | Sort-Object x | Select-Object -First 1 }

$win = $null; $alive = $false
if ($ProcessId -gt 0) {
  $proc = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
  $alive = [bool]$proc
  if ($alive) {
    $row = [PhysState]::WindowOf([uint32]$ProcessId)
    if ($row) {
      $q = $row -split '\|'
      $win = [ordered]@{ left = [int]$q[0]; top = [int]$q[1]; width = [int]$q[2]; height = [int]$q[3]; dpi = [int]$q[4]; percent = [int]$q[5]; hwnd = [int64]$q[6] }
      $win.containedInPrimary = ($win.left -ge $primary.x) -and ($win.top -ge $primary.y) -and (($win.left + $win.width) -le ($primary.x + $primary.width)) -and (($win.top + $win.height) -le ($primary.y + $primary.height))
    }
  }
}
$shot = Capture $primary.x $primary.y $primary.width $primary.height (Join-Path $shots ("{0}-{1}.png" -f $stamp, $Label))
$doc = [ordered]@{
  label = $Label; capturedAt = (Get-Date -Format o); pid = $ProcessId
  displays = $displays
  activeCount = @($active).Count
  has4k = [bool]($active | Where-Object { $_.width -eq 3840 -and $_.height -eq 2160 })
  window = $win; appAlive = $alive
  screenshot = $shot
}
$out = Join-Path $OutDir ("physical-state-{0}-{1}.json" -f $Label, $stamp)
$doc | ConvertTo-Json -Depth 7 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
Write-Host ("active={0} has4k={1} primary={2} {3}x{4}" -f $doc.activeCount,$doc.has4k,$primary.device,$primary.width,$primary.height)
if ($win) { Write-Host ("window=({0},{1}) {2}x{3}@{4}% alive={5} containedInPrimary={6}" -f $win.left,$win.top,$win.width,$win.height,$win.percent,$alive,$win.containedInPrimary) } else { Write-Host "window: none (alive=$alive)" }
