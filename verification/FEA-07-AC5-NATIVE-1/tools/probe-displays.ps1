# FEA-07-AC5-NATIVE-1 / probe-displays.ps1
# 只读：活动显示路径（source→EDID friendly name）+ 每屏 rect/主屏/DPI + 当前模式 + 恢复点。
[CmdletBinding()]
param(
  [string]$OutDir = "",
  [string]$Label = "baseline"
)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-AC5-NATIVE-1\evidence' }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$csharp = @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;

public static class DcProbe {
  [StructLayout(LayoutKind.Sequential)] public struct LUID { public uint LowPart; public int HighPart; }
  [StructLayout(LayoutKind.Sequential)] public struct RATIONAL { public uint Numerator; public uint Denominator; }
  [StructLayout(LayoutKind.Sequential)] public struct PATH_SOURCE_INFO { public LUID adapterId; public uint id; public uint modeInfoIdx; public uint statusFlags; }
  [StructLayout(LayoutKind.Sequential)] public struct PATH_TARGET_INFO {
    public LUID adapterId; public uint id; public uint modeInfoIdx; public uint outputTechnology;
    public uint rotation; public uint scaling; public RATIONAL refreshRate; public uint scanLineOrdering;
    public int targetAvailable; public uint statusFlags;
  }
  [StructLayout(LayoutKind.Sequential)] public struct PATH_INFO { public PATH_SOURCE_INFO sourceInfo; public PATH_TARGET_INFO targetInfo; public uint flags; }
  [StructLayout(LayoutKind.Sequential)] public struct MODE_INFO { public uint infoType; public uint id; public LUID adapterId; public ulong pad0,pad1,pad2,pad3,pad4,pad5,pad6,pad7,pad8,pad9,pad10,pad11; }
  [StructLayout(LayoutKind.Sequential)] public struct DEVICE_INFO_HEADER { public uint type; public uint size; public LUID adapterId; public uint id; }
  [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)] public struct TARGET_DEVICE_NAME {
    public DEVICE_INFO_HEADER header; public uint flags; public uint outputTechnology; public ushort edidManufactureId; public ushort edidProductCodeId; public uint connectorInstance;
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 64)] public string monitorFriendlyDeviceName;
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 128)] public string monitorDevicePath;
  }
  [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)] public struct SOURCE_DEVICE_NAME {
    public DEVICE_INFO_HEADER header;
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)] public string viewGdiDeviceName;
  }
  [StructLayout(LayoutKind.Sequential)] public struct POINT { public int x; public int y; }
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int left, top, right, bottom; }
  [StructLayout(LayoutKind.Sequential)] public struct MONITORINFO { public int cbSize; public RECT rcMonitor; public RECT rcWork; public int dwFlags; }

  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr value);
  [DllImport("user32.dll")] public static extern int GetDisplayConfigBufferSizes(uint flags, out uint numPath, out uint numMode);
  [DllImport("user32.dll")] public static extern int QueryDisplayConfig(uint flags, ref uint numPath, [Out] PATH_INFO[] paths, ref uint numMode, [Out] MODE_INFO[] modes, IntPtr currentTopologyId);
  [DllImport("user32.dll")] public static extern int DisplayConfigGetDeviceInfo(ref SOURCE_DEVICE_NAME info);
  [DllImport("user32.dll")] public static extern int DisplayConfigGetDeviceInfo(ref TARGET_DEVICE_NAME info);
  [DllImport("user32.dll")] public static extern IntPtr MonitorFromPoint(POINT pt, uint flags);
  [DllImport("user32.dll")] public static extern bool GetMonitorInfo(IntPtr hMonitor, ref MONITORINFO mi);
  [DllImport("shcore.dll")] public static extern int GetDpiForMonitor(IntPtr hmon, int dpiType, out uint dpiX, out uint dpiY);
  [DllImport("user32.dll")] public static extern bool EnumDisplayMonitors(IntPtr hdc, IntPtr lprcClip, MonitorEnumProc lpfnEnum, IntPtr dwData);
  public delegate bool MonitorEnumProc(IntPtr hMonitor, IntPtr hdc, IntPtr lprc, IntPtr data);

  public static string[] Monitors() {
    SetProcessDpiAwarenessContext(new IntPtr(-4));
    var rows = new List<string>();
    uint primaryFlag = 1;
    EnumDisplayMonitors(IntPtr.Zero, IntPtr.Zero, (h, d, r, x) => {
      var mi = new MONITORINFO(); mi.cbSize = Marshal.SizeOf(mi);
      bool ok = GetMonitorInfo(h, ref mi);
      uint dx = 0, dy = 0; int hr = GetDpiForMonitor(h, 0, out dx, out dy);
      rows.Add(string.Format("{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}|{8}",
        ok ? "ok" : "err", mi.rcMonitor.left, mi.rcMonitor.top, mi.rcMonitor.right, mi.rcMonitor.bottom,
        ((mi.dwFlags & primaryFlag) != 0) ? 1 : 0, dx, hr, (int)h));
      return true;
    }, IntPtr.Zero);
    return rows.ToArray();
  }

  public static string[] Paths() {
    uint np = 0, nm = 0;
    int rc = GetDisplayConfigBufferSizes(2, out np, out nm);
    if (rc != 0) return new string[] { "ERR|GetDisplayConfigBufferSizes|" + rc };
    var paths = new PATH_INFO[np]; var modes = new MODE_INFO[nm];
    rc = QueryDisplayConfig(2, ref np, paths, ref nm, modes, IntPtr.Zero);
    if (rc != 0) return new string[] { "ERR|QueryDisplayConfig|" + rc };
    var rows = new List<string>();
    for (int i = 0; i < np; i++) {
      var src = new SOURCE_DEVICE_NAME(); src.header.type = 1; src.header.size = (uint)Marshal.SizeOf(src);
      src.header.adapterId = paths[i].sourceInfo.adapterId; src.header.id = paths[i].sourceInfo.id;
      string gdi = "?"; if (DisplayConfigGetDeviceInfo(ref src) == 0) gdi = src.viewGdiDeviceName;
      var tgt = new TARGET_DEVICE_NAME(); tgt.header.type = 2; tgt.header.size = (uint)Marshal.SizeOf(tgt);
      tgt.header.adapterId = paths[i].targetInfo.adapterId; tgt.header.id = paths[i].targetInfo.id;
      string name = "?", dpath = "?";
      if (DisplayConfigGetDeviceInfo(ref tgt) == 0) { name = tgt.monitorFriendlyDeviceName; dpath = tgt.monitorDevicePath; }
      double hz = paths[i].targetInfo.refreshRate.Denominator != 0
        ? (double)paths[i].targetInfo.refreshRate.Numerator / paths[i].targetInfo.refreshRate.Denominator : 0;
      rows.Add(string.Format("{0}|{1}|{2}|{3}|{4}|{5}|{6}", gdi, name, dpath, paths[i].targetInfo.outputTechnology, paths[i].targetInfo.rotation, paths[i].targetInfo.scaling, hz.ToString("0.###")));
    }
    return rows.ToArray();
  }
}
'@
Add-Type -TypeDefinition $csharp -ErrorAction Stop

function Get-Displays {
  $m = [DcProbe]::Monitors()
  $p = [DcProbe]::Paths()
  $pathsByGdi = @{}
  foreach ($row in $p) {
    $q = $row -split '\|', 7
    if ($q[0] -eq 'ERR') { continue }
    $pathsByGdi[$q[0]] = [pscustomobject]@{ friendlyName = $q[1]; devicePath = $q[2]; outputTechnology = [int]$q[3]; rotation = [int]$q[4]; scaling = [int]$q[5]; refreshHz = [double]$q[6] }
  }
  $own = $m | ForEach-Object {
    $f = $_ -split '\|'
    [pscustomobject]@{ left = [int]$f[1]; top = [int]$f[2]; right = [int]$f[3]; bottom = [int]$f[4]; primary = ($f[5] -eq '1'); dpi = [int]$f[6] }
  } | Sort-Object left, top
  $screens = [System.Windows.Forms.Screen]::AllScreens | Sort-Object { $_.Bounds.X }, { $_.Bounds.Y }
  $out = for ($i = 0; $i -lt $own.Count; $i++) {
    $o = $own[$i]; $s = $screens[$i]
    $pth = $pathsByGdi[$s.DeviceName]
    [pscustomobject]@{
      gdiDevice = $s.DeviceName
      friendlyName = if ($pth) { $pth.friendlyName } else { $null }
      devicePath = if ($pth) { $pth.devicePath } else { $null }
      left = $o.left; top = $o.top; width = $o.right - $o.left; height = $o.bottom - $o.top
      primary = $o.primary
      dpi = $o.dpi
      scalePercent = [math]::Round($o.dpi / 96.0 * 100)
      refreshHz = if ($pth) { $pth.refreshHz } else { $null }
      outputTechnology = if ($pth) { $pth.outputTechnology } else { $null }
      scalingMode = if ($pth) { $pth.scaling } else { $null }
    }
  }
  return $out
}

Add-Type -AssemblyName System.Windows.Forms
$displays = @(Get-Displays)
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$doc = [ordered]@{
  label = $Label
  capturedAt = (Get-Date -Format o)
  session = (Get-Process -Id $PID).SessionId
  displayCount = $displays.Count
  displays = $displays
}
$out = Join-Path $OutDir ("displays-{0}-{1}.json" -f $Label, $stamp)
$doc | ConvertTo-Json -Depth 6 | Set-Content -Path $out -Encoding UTF8
Write-Host "=== displays ($Label) ==="
$displays | Format-Table gdiDevice, friendlyName, width, height, dpi, scalePercent, primary, refreshHz -AutoSize | Out-String | Write-Host
Write-Host "saved: $out"
