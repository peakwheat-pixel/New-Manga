# FEA-07-AC5-NATIVE-1 / set-display-scale.ps1
# 每屏 DPI 缩放查询/设置（DisplayConfig GET/SET_DPI_SCALE，undocumented -3/-4；失败则如实报错）。
# 用法：
#   pwsh -File set-display-scale.ps1 -Device \\.\DISPLAY2 -Action query
#   pwsh -File set-display-scale.ps1 -Device \\.\DISPLAY2 -Action set-relative -Relative -1
#   pwsh -File set-display-scale.ps1 -Device \\.\DISPLAY2 -Action set-percent -Percent 125
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][string]$Device,
  [Parameter(Mandatory = $true)][ValidateSet('query', 'set-relative', 'set-percent', 'restore-recommended')][string]$Action,
  [int]$Relative = 0,
  [int]$Percent = 0
)
$ErrorActionPreference = 'Stop'
$cs = @'
using System;
using System.Runtime.InteropServices;

public static class DpiScale {
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
  [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)] public struct SOURCE_DEVICE_NAME {
    public DEVICE_INFO_HEADER header;
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)] public string viewGdiDeviceName;
  }
  [StructLayout(LayoutKind.Sequential)] public struct GET_DPI_SCALE {
    public DEVICE_INFO_HEADER header; public int minRelativeScale; public int curRelativeScale; public int maxRelativeScale;
  }
  [StructLayout(LayoutKind.Sequential)] public struct SET_DPI_SCALE {
    public DEVICE_INFO_HEADER header; public int scaleRel;
  }
  [DllImport("user32.dll")] public static extern int GetDisplayConfigBufferSizes(uint flags, out uint numPath, out uint numMode);
  [DllImport("user32.dll")] public static extern int QueryDisplayConfig(uint flags, ref uint numPath, [Out] PATH_INFO[] paths, ref uint numMode, [Out] MODE_INFO[] modes, IntPtr currentTopologyId);
  [DllImport("user32.dll")] public static extern int DisplayConfigGetDeviceInfo(ref SOURCE_DEVICE_NAME info);
  [DllImport("user32.dll")] public static extern int DisplayConfigGetDeviceInfo(ref GET_DPI_SCALE info);
  [DllImport("user32.dll")] public static extern int DisplayConfigSetDeviceInfo(ref SET_DPI_SCALE info);

  public static string[] FindTarget(string gdiDevice) {
    uint np = 0, nm = 0;
    if (GetDisplayConfigBufferSizes(2, out np, out nm) != 0) return new string[] { "ERR|buffer" };
    var paths = new PATH_INFO[np]; var modes = new MODE_INFO[nm];
    if (QueryDisplayConfig(2, ref np, paths, ref nm, modes, IntPtr.Zero) != 0) return new string[] { "ERR|query" };
    for (int i = 0; i < np; i++) {
      var src = new SOURCE_DEVICE_NAME(); src.header.type = 1; src.header.size = (uint)Marshal.SizeOf(src);
      src.header.adapterId = paths[i].sourceInfo.adapterId; src.header.id = paths[i].sourceInfo.id;
      if (DisplayConfigGetDeviceInfo(ref src) != 0) continue;
      if (!string.Equals(src.viewGdiDeviceName, gdiDevice, StringComparison.OrdinalIgnoreCase)) continue;
      return new string[] { "OK|" + paths[i].targetInfo.adapterId.LowPart + "|" + paths[i].targetInfo.adapterId.HighPart + "|" + paths[i].targetInfo.id + "|" + paths[i].sourceInfo.adapterId.LowPart + "|" + paths[i].sourceInfo.adapterId.HighPart + "|" + paths[i].sourceInfo.id };
    }
    return new string[] { "ERR|not-found" };
  }

  public static string QueryScale(string gdiDevice) {
    var t = FindTarget(gdiDevice)[0];
    if (!t.StartsWith("OK|")) return t;
    var p = t.Split('|');
    var info = new GET_DPI_SCALE();
    info.header.type = unchecked((uint)-3); info.header.size = (uint)Marshal.SizeOf(info);
    info.header.adapterId.LowPart = Convert.ToUInt32(p[1]); info.header.adapterId.HighPart = Convert.ToInt32(p[2]);
    info.header.id = Convert.ToUInt32(p[3]);
    int rc = DisplayConfigGetDeviceInfo(ref info);
    return "rc=" + rc + "|min=" + info.minRelativeScale + "|cur=" + info.curRelativeScale + "|max=" + info.maxRelativeScale;
  }

  public static string SetScale(string gdiDevice, int rel) {
    var t = FindTarget(gdiDevice)[0];
    if (!t.StartsWith("OK|")) return t;
    var p = t.Split('|');
    var info = new SET_DPI_SCALE();
    info.header.type = unchecked((uint)-4); info.header.size = (uint)Marshal.SizeOf(info);
    info.header.adapterId.LowPart = Convert.ToUInt32(p[1]); info.header.adapterId.HighPart = Convert.ToInt32(p[2]);
    info.header.id = Convert.ToUInt32(p[3]);
    info.scaleRel = rel;
    int rc = DisplayConfigSetDeviceInfo(ref info);
    return "rc=" + rc + "|rel=" + rel;
  }
}
'@
Add-Type -TypeDefinition $cs -ErrorAction Stop

function Get-DeviceDpi([string]$dev) {
  Add-Type -AssemblyName System.Windows.Forms
  $scr = [System.Windows.Forms.Screen]::AllScreens | Where-Object { $_.DeviceName -eq $dev } | Select-Object -First 1
  if (-not $scr) { return $null }
  $sig = @'
using System;
using System.Runtime.InteropServices;
public static class DpiAt {
  [StructLayout(LayoutKind.Sequential)] public struct POINT { public int x; public int y; }
  [DllImport("user32.dll")] public static extern IntPtr MonitorFromPoint(POINT pt, uint flags);
  [DllImport("shcore.dll")] public static extern int GetDpiForMonitor(IntPtr h, int t, out uint dx, out uint dy);
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr v);
  public static int At(int x, int y) {
    SetProcessDpiAwarenessContext(new IntPtr(-4));
    var pt = new POINT(); pt.x = x; pt.y = y;
    IntPtr h = MonitorFromPoint(pt, 2);
    uint dx = 0, dy = 0; GetDpiForMonitor(h, 0, out dx, out dy);
    return (int)dx;
  }
}
'@
  if (-not ('DpiAt' -as [type])) { Add-Type -TypeDefinition $sig -ErrorAction Stop }
  $cx = $scr.Bounds.X + [int]($scr.Bounds.Width / 2); $cy = $scr.Bounds.Y + [int]($scr.Bounds.Height / 2)
  return [DpiAt]::At($cx, $cy)
}

switch ($Action) {
  'query' {
    $q = [DpiScale]::QueryScale($Device)
    $dpi = Get-DeviceDpi $Device
    "device=$Device scale=$q dpi=$dpi percent=$([math]::Round($dpi/96.0*100))"
  }
  'set-relative' {
    $before = Get-DeviceDpi $Device
    $rc = [DpiScale]::SetScale($Device, $Relative)
    Start-Sleep -Milliseconds 1200
    $after = Get-DeviceDpi $Device
    "device=$Device set $rc ; dpi $before -> $after (percent $([math]::Round($before/96.0*100)) -> $([math]::Round($after/96.0*100)))"
  }
  'set-percent' {
    if ($Percent -le 0) { throw "-Percent required" }
    $cur = [DpiScale]::QueryScale($Device)
    $before = Get-DeviceDpi $Device
    $found = $null; $log = @()
    foreach ($rel in @(0, -1, 1, -2, 2, -3, 3, -4, 4, -5, 5)) {
      $rc = [DpiScale]::SetScale($Device, $rel)
      Start-Sleep -Milliseconds 700
      $d = Get-DeviceDpi $Device
      $p = [math]::Round($d / 96.0 * 100)
      $log += "rel=$rel rc=$rc dpi=$d percent=$p"
      if ($p -eq $Percent) { $found = $rel; break }
    }
    "device=$Device query(before)=$cur dpiBefore=$before"
    $log | ForEach-Object { $_ }
    if ($null -eq $found) {
      [DpiScale]::SetScale($Device, 0) | Out-Null
      "RESULT=NOT_REACHABLE percent=$Percent (restored to recommended rel=0)"
    } else {
      "RESULT=OK percent=$Percent rel=$found"
    }
  }
  'restore-recommended' {
    $rc = [DpiScale]::SetScale($Device, 0)
    Start-Sleep -Milliseconds 900
    "device=$Device restore rel=0 $rc dpi=$(Get-DeviceDpi $Device)"
  }
}
