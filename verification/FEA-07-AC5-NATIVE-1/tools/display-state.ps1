# FEA-07-AC5-NATIVE-1 / display-state.ps1
# 显示状态采样 / 恢复点 / 模式切换（ChangeDisplaySettingsEx）。
# 用法：
#   pwsh -File display-state.ps1 -Action capture  -OutDir <dir> -Label before
#   pwsh -File display-state.ps1 -Action set-mode -Device \\.\DISPLAY1 -Width 2560 -Height 1440
#   pwsh -File display-state.ps1 -Action restore  -From <capture.json>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][ValidateSet('capture', 'set-mode', 'restore', 'list-modes')][string]$Action,
  [string]$OutDir = "",
  [string]$Label = "",
  [string]$Device = "",
  [int]$Width = 0,
  [int]$Height = 0,
  [int]$RefreshHz = 0,
  [string]$From = ""
)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-AC5-NATIVE-1\evidence' }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$cs = @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;

public static class DisplayState {
  [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
  public struct DEVMODE {
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)] public string dmDeviceName;
    public ushort dmSpecVersion, dmDriverVersion, dmSize, dmDriverExtra;
    public uint dmFields;
    public int dmPositionX, dmPositionY; public uint dmDisplayOrientation, dmDisplayFixedOutput;
    public short dmColor, dmDuplex, dmYResolution, dmTTOption, dmCollate;
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)] public string dmFormName;
    public ushort dmLogPixels; public uint dmBitsPerPel, dmPelsWidth, dmPelsHeight, dmDisplayFlags, dmDisplayFrequency;
    public uint dmICMMethod, dmICMIntent, dmMediaType, dmDitherType, dmReserved1, dmReserved2, dmPanningWidth, dmPanningHeight;
  }
  [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
  public struct DISPLAY_DEVICE {
    public int cb;
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)] public string DeviceName;
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 128)] public string DeviceString;
    public int StateFlags;
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 128)] public string DeviceID;
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 128)] public string DeviceKey;
  }

  [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern bool EnumDisplaySettingsW(string dev, int mode, ref DEVMODE dm);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern bool EnumDisplayDevicesW(string dev, uint i, ref DISPLAY_DEVICE dd, uint flags);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int ChangeDisplaySettingsExW(string dev, ref DEVMODE dm, IntPtr hwnd, uint flags, IntPtr param);
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr v);
  [DllImport("shcore.dll")] public static extern int GetDpiForMonitor(IntPtr hmon, int dpiType, out uint dpiX, out uint dpiY);
  [DllImport("user32.dll")] public static extern IntPtr MonitorFromPoint(POINT pt, uint flags);
  [StructLayout(LayoutKind.Sequential)] public struct POINT { public int x; public int y; }

  public static DEVMODE NewDevMode() { var dm = new DEVMODE(); dm.dmSize = (ushort)Marshal.SizeOf(dm); return dm; }

  public static string[] ActiveDevices() {
    var list = new List<string>();
    for (uint i = 0; i < 16; i++) {
      var dd = new DISPLAY_DEVICE(); dd.cb = Marshal.SizeOf(dd);
      if (!EnumDisplayDevicesW(null, i, ref dd, 0)) break;
      if ((dd.StateFlags & 0x1) != 0) list.Add(dd.DeviceName + "|" + ((dd.StateFlags & 0x4) != 0 ? "primary" : "secondary") + "|" + dd.DeviceString);
    }
    return list.ToArray();
  }

  public static string CurrentMode(string dev) {
    var dm = NewDevMode();
    if (!EnumDisplaySettingsW(dev, -1, ref dm)) return "ERR|EnumDisplaySettings";
    uint dx = 0, dy = 0;
    SetProcessDpiAwarenessContext(new IntPtr(-4));
    var pt = new POINT(); pt.x = dm.dmPositionX + (int)(dm.dmPelsWidth / 2); pt.y = dm.dmPositionY + (int)(dm.dmPelsHeight / 2);
    IntPtr hmon = MonitorFromPoint(pt, 2);
    if (hmon != IntPtr.Zero) GetDpiForMonitor(hmon, 0, out dx, out dy);
    return string.Format("{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}|{8}", dm.dmPelsWidth, dm.dmPelsHeight, dm.dmDisplayFrequency,
      dm.dmPositionX, dm.dmPositionY, dm.dmBitsPerPel, dm.dmDisplayOrientation, dx, Math.Round(dx / 96.0 * 100));
  }

  public static string[] Modes(string dev, int minW, int minH) {
    var seen = new HashSet<string>();
    var rows = new List<string>();
    for (int i = 0; i < 4096; i++) {
      var dm = NewDevMode();
      if (!EnumDisplaySettingsW(dev, i, ref dm)) break;
      if (dm.dmPelsWidth < minW || dm.dmPelsHeight < minH) continue;
      if ((dm.dmDisplayFlags & 0x1) != 0) continue; // interlace
      string key = dm.dmPelsWidth + "x" + dm.dmPelsHeight + "@" + dm.dmDisplayFrequency;
      if (seen.Add(key)) rows.Add(string.Format("{0}|{1}|{2}|{3}", dm.dmPelsWidth, dm.dmPelsHeight, dm.dmDisplayFrequency, dm.dmBitsPerPel));
    }
    return rows.ToArray();
  }

  public static string SetMode(string dev, int w, int h, int hz, int x, int y) {
    var dm = NewDevMode();
    if (!EnumDisplaySettingsW(dev, -1, ref dm)) return "ERR|current-mode";
    dm.dmPelsWidth = (uint)w; dm.dmPelsHeight = (uint)h;
    dm.dmPositionX = x; dm.dmPositionY = y;
    if (hz > 0) dm.dmDisplayFrequency = (uint)hz;
    dm.dmFields = 0x80000 /*DM_PELSWIDTH*/ | 0x100000 /*DM_PELSHEIGHT*/ | 0x20 /*DM_POSITION*/ | 0x400000 /*DM_DISPLAYFREQUENCY*/;
    int rc = ChangeDisplaySettingsExW(dev, ref dm, IntPtr.Zero, 0x00000001 /*CDS_UPDATEREGISTRY*/, IntPtr.Zero);
    return "rc=" + rc;
  }
}
'@
Add-Type -TypeDefinition $cs -ErrorAction Stop

function Get-State {
  $rows = @()
  foreach ($d in [DisplayState]::ActiveDevices()) {
    $p = $d -split '\|', 3
    $m = ([DisplayState]::CurrentMode($p[0])) -split '\|'
    if ($m[0] -eq 'ERR') { throw "current mode failed for $($p[0])" }
    $rows += [pscustomobject]@{
      device = $p[0]; role = $p[1]; adapter = $p[2]
      width = [int]$m[0]; height = [int]$m[1]; refreshHz = [int]$m[2]
      x = [int]$m[3]; y = [int]$m[4]; bitsPerPel = [int]$m[5]
      orientation = [int]$m[6]; dpi = [int]$m[7]; scalePercent = [int]$m[8]
    }
  }
  return $rows
}

switch ($Action) {
  'capture' {
    $state = @(Get-State)
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $label = if ($Label) { $Label } else { 'state' }
    $doc = [ordered]@{ label = $label; capturedAt = (Get-Date -Format o); displays = $state }
    $out = Join-Path $OutDir ("display-state-{0}-{1}.json" -f $label, $stamp)
    $doc | ConvertTo-Json -Depth 5 | Set-Content -Path $out -Encoding UTF8
    $state | Format-Table device, role, width, height, refreshHz, x, y, dpi, scalePercent -AutoSize | Out-String | Write-Host
    Write-Host "saved: $out"
  }
  'list-modes' {
    if (-not $Device) { throw "-Device required" }
    $rows = [DisplayState]::Modes($Device, $Width, $Height)
    "count=$($rows.Count)"
    $rows | Select-Object -First 80
  }
  'set-mode' {
    if (-not $Device -or $Width -le 0 -or $Height -le 0) { throw "-Device/-Width/-Height required" }
    $cur = @(Get-State) | Where-Object { $_.device -eq $Device }
    if (-not $cur) { throw "device not active: $Device" }
    $x = $cur[0].x; $y = $cur[0].y
    $rc = [DisplayState]::SetMode($Device, $Width, $Height, $RefreshHz, $x, $y)
    Start-Sleep -Milliseconds 900
    $now = @(Get-State) | Where-Object { $_.device -eq $Device }
    "set-mode $Device -> $Width x $Height @${RefreshHz}Hz : $rc ; now = $($now[0].width)x$($now[0].height)@$($now[0].refreshHz) dpi=$($now[0].dpi)"
  }
  'restore' {
    if (-not $From) { throw "-From required" }
    $doc = Get-Content -Raw -Path $From | ConvertFrom-Json
    foreach ($d in $doc.displays) {
      $rc = [DisplayState]::SetMode($d.device, [int]$d.width, [int]$d.height, [int]$d.refreshHz, [int]$d.x, [int]$d.y)
      Write-Host ("restore {0} -> {1}x{2}@{3} ({4},{5}) : {6}" -f $d.device, $d.width, $d.height, $d.refreshHz, $d.x, $d.y, $rc)
    }
    Start-Sleep -Milliseconds 1200
    Get-State | Format-Table device, role, width, height, refreshHz, x, y, dpi, scalePercent -AutoSize | Out-String | Write-Host
  }
}
