# FEA-07-AC5-NATIVE-1 / dpi-registry-scale.ps1
# 通过 HKCU\Control Panel\Desktop\PerMonitorSettings\<monitorKey>\DpiValue + 系统广播切换每屏缩放。
# 用法：-Action probe（读）/ -Action set -DpiValue N（写+广播+探测）/ -Action restore -DpiValue 原值
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][ValidateSet('probe', 'set')][string]$Action,
  [int]$DpiValue = 0,
  [string]$MonitorKey = ""
)
$ErrorActionPreference = 'Stop'

$cs = @'
using System;
using System.Runtime.InteropServices;
public static class DpiReg {
  [DllImport("user32.dll", CharSet = CharSet.Unicode)]
  public static extern IntPtr SendMessageTimeoutW(IntPtr hWnd, uint msg, UIntPtr wParam, string lParam, uint flags, uint timeout, out UIntPtr result);
  [DllImport("user32.dll")] public static extern IntPtr SendMessageTimeoutW(IntPtr hWnd, uint msg, UIntPtr wParam, IntPtr lParam, uint flags, uint timeout, out UIntPtr result);
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr v);
  [DllImport("shcore.dll")] public static extern int GetDpiForMonitor(IntPtr hmon, int t, out uint dx, out uint dy);
  [DllImport("user32.dll")] public static extern IntPtr MonitorFromPoint(POINT pt, uint flags);
  [StructLayout(LayoutKind.Sequential)] public struct POINT { public int x, y; }
  public static uint DpiAt(int x, int y) {
    SetProcessDpiAwarenessContext(new IntPtr(-4));
    var pt = new POINT(); pt.x = x; pt.y = y;
    IntPtr h = MonitorFromPoint(pt, 2);
    uint dx = 0, dy = 0; GetDpiForMonitor(h, 0, out dx, out dy);
    return dx;
  }
  public static void Broadcast() {
    UIntPtr r;
    // WM_SETTINGCHANGE = 0x1A, WM_DISPLAYCHANGE = 0x7E, HWND_BROADCAST = 0xFFFF
    SendMessageTimeoutW(new IntPtr(0xFFFF), 0x001A, UIntPtr.Zero, "Desktop", 0x0002 /*SMTO_ABORTIFHUNG*/, 3000, out r);
    SendMessageTimeoutW(new IntPtr(0xFFFF), 0x001A, UIntPtr.Zero, "Environment", 0x0002, 3000, out r);
    SendMessageTimeoutW(new IntPtr(0xFFFF), 0x007E, UIntPtr.Zero, IntPtr.Zero, 0x0002, 3000, out r);
  }
}
'@
Add-Type -TypeDefinition $cs -ErrorAction Stop

$base = 'HKCU:\Control Panel\Desktop\PerMonitorSettings'
if (-not (Test-Path $base)) { throw "no PerMonitorSettings" }
$keys = Get-ChildItem $base
if (-not $MonitorKey) {
  # 选 4K 屏的键（PHLC254 = Philips）；若只有一个键则用它
  $k = $keys | Where-Object { $_.PSChildName -like 'PHLC*' } | Select-Object -First 1
  if (-not $k) { $k = $keys | Select-Object -First 1 }
  if (-not $k) { throw "no monitor key" }
  $MonitorKey = $k.PSChildName
}
$path = Join-Path $base $MonitorKey
$props = Get-ItemProperty -Path $path
Write-Host "monitorKey=$MonitorKey"
Write-Host ("DpiValue(before)={0}" -f $props.DpiValue)
Write-Host ("allProps: " + (($props.PSObject.Properties | Where-Object { $_.Name -notlike 'PS*' } | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join '; '))

# 4K 屏中心点用于探测 DPI（探测前从 probe 取，这里用固定 2560+1920=4480, 1080）
$probeX = 4480; $probeY = 1080
$dpiBefore = [DpiReg]::DpiAt($probeX, $probeY)
Write-Host "dpi@4K(before)=$dpiBefore percent=$([math]::Round($dpiBefore/96.0*100))"

if ($Action -eq 'probe') { return }

Set-ItemProperty -Path $path -Name 'DpiValue' -Value ([int]$DpiValue) -Type DWord
Write-Host "wrote DpiValue=$DpiValue"
[DpiReg]::Broadcast()
Start-Sleep -Milliseconds 2500
$dpiAfter = [DpiReg]::DpiAt($probeX, $probeY)
Write-Host "dpi@4K(after broadcast)=$dpiAfter percent=$([math]::Round($dpiAfter/96.0*100))"
Write-Host ("DpiValue(after)={0}" -f (Get-ItemProperty -Path $path).DpiValue)
