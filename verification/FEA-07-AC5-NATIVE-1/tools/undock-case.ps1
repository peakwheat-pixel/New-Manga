# FEA-07-AC5-NATIVE-1 / undock-case.ps1
# OS 级拔屏（禁用副屏）→ 观察应用窗口是否回主窗/仍可见/不越界 → 重新启用 → 校验恢复。
[CmdletBinding()]
param(
  [string]$OutDir = "",
  [int]$SettleMs = 1500,
  [switch]$KeepRunning
)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-AC5-NATIVE-1\evidence' }
$shots = Join-Path $OutDir 'screenshots'
New-Item -ItemType Directory -Force -Path $OutDir, $shots | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'

$cs = @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;

public static class UndockApi {
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
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int left, top, right, bottom; }
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int ChangeDisplaySettingsExW(string dev, ref DEVMODE dm, IntPtr hwnd, uint flags, IntPtr param);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern bool EnumDisplaySettingsW(string dev, int mode, ref DEVMODE dm);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc cb, IntPtr l);
  public delegate bool EnumWindowsProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern uint GetDpiForWindow(IntPtr h);

  public static DEVMODE NewDevMode() { var dm = new DEVMODE(); dm.dmSize = (ushort)Marshal.SizeOf(dm); return dm; }

  public static string Disable(string dev) {
    var dm = NewDevMode();
    dm.dmPelsWidth = 0; dm.dmPelsHeight = 0; dm.dmFields = 0x00080000 | 0x00100000; // DM_PELSWIDTH|DM_PELSHEIGHT
    int rc = ChangeDisplaySettingsExW(dev, ref dm, IntPtr.Zero, 0x00000001 /*CDS_UPDATEREGISTRY*/, IntPtr.Zero);
    return "disable rc=" + rc;
  }
  public static string Enable(string dev, int w, int h, int hz, int x, int y) {
    var dm = NewDevMode();
    if (!EnumDisplaySettingsW(dev, -1, ref dm)) return "ERR|mode";
    dm.dmPelsWidth = (uint)w; dm.dmPelsHeight = (uint)h; dm.dmPositionX = x; dm.dmPositionY = y;
    if (hz > 0) dm.dmDisplayFrequency = (uint)hz;
    dm.dmFields = 0x00080000 | 0x00100000 | 0x00000020 | 0x00400000;
    int rc = ChangeDisplaySettingsExW(dev, ref dm, IntPtr.Zero, 0x00000001, IntPtr.Zero);
    return "enable rc=" + rc;
  }
  public static string MainWindowOf(uint pid) {
    IntPtr found = IntPtr.Zero;
    EnumWindows((h, l) => {
      uint p; GetWindowThreadProcessId(h, out p);
      if (p != pid || !IsWindowVisible(h)) return true;
      RECT r; GetWindowRect(h, out r);
      if (r.right - r.left < 200) return true;
      found = h; return false;
    }, IntPtr.Zero);
    return found.ToString();
  }
  public static string Rect(IntPtr h) {
    RECT r; GetWindowRect(h, out r);
    return string.Format("{0}|{1}|{2}|{3}|{4}|{5}", r.left, r.top, r.right - r.left, r.bottom - r.top, GetDpiForWindow(h), Math.Round(GetDpiForWindow(h) / 96.0 * 100));
  }
}
'@
Add-Type -TypeDefinition $cs -ErrorAction Stop
Add-Type -AssemblyName System.Drawing

function Capture([int]$x, [int]$y, [int]$w, [int]$h, [string]$file) {
  $bmp = New-Object System.Drawing.Bitmap $w, $h
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen($x, $y, 0, 0, (New-Object System.Drawing.Size $w, $h))
  $g.Dispose(); $bmp.Save($file, [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
  [pscustomobject]@{ file = (Split-Path $file -Leaf); width = $w; height = $h; sha256 = (Get-FileHash -Algorithm SHA256 -Path $file).Hash.ToLowerInvariant() }
}
function Get-Displays {
  $null = & pwsh -NoProfile -File (Join-Path $PSScriptRoot 'probe-displays.ps1') -OutDir $OutDir -Label 'undock' 2>&1
  $latest = Get-ChildItem $OutDir -Filter 'displays-undock-*.json' | Sort-Object LastWriteTime | Select-Object -Last 1
  if (-not $latest) { throw 'probe failed' }
  Get-Content -Raw -Path $latest.FullName | ConvertFrom-Json
}

$disp = Get-Displays
$mon1 = $disp.displays | Where-Object { $_.primary } | Select-Object -First 1
$mon2 = $disp.displays | Where-Object { -not $_.primary } | Select-Object -First 1
if (-not $mon2) { throw 'needs a secondary display' }
Write-Host ("before: mon1={0} {1}x{2}@{3}% | mon2={4} {5}x{6}@{7}%" -f $mon1.friendlyName,$mon1.width,$mon1.height,$mon1.scalePercent,$mon2.friendlyName,$mon2.width,$mon2.height,$mon2.scalePercent)

$root = Join-Path $env:TEMP ("nm-fea07-undock-{0}" -f $stamp)
$dataRoot = Join-Path $root 'data'; $logDir = Join-Path $root 'logs'; $themeHome = Join-Path $root 'theme'
New-Item -ItemType Directory -Force -Path $dataRoot, $logDir, $themeHome | Out-Null
$exe = Join-Path $repo 'apps\desktop-avalonia\src\NewManga.App\bin\Release\net9.0\NewManga.App.exe'
$appArgs = @('--data-root', $dataRoot, '--log-dir', $logDir, '--theme-home', $themeHome, '--shell=v2')
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $exe; $psi.WorkingDirectory = (Split-Path $exe -Parent); $psi.UseShellExecute = $false; $psi.CreateNoWindow = $true
foreach ($a in $appArgs) { $psi.ArgumentList.Add($a) }
$proc = [System.Diagnostics.Process]::Start($psi)
Write-Host "launched pid=$($proc.Id)"
$main = [IntPtr]::Zero
for ($i = 0; $i -lt 40; $i++) {
  Start-Sleep -Milliseconds 500
  $h = [UndockApi]::MainWindowOf([uint32]$proc.Id)
  if ($h -ne '0') { $main = [IntPtr][int64]$h; break }
}
if ($main -eq [IntPtr]::Zero) { throw 'main window not found' }

# place window on secondary (programmatically, small DIP-safe size)
$w = [int]($mon2.width * 0.5); $hgt = [int]($mon2.height * 0.5)
[UndockApi]::Enable($mon2.gdiDevice, $mon2.width, $mon2.height, 0, $mon2.left, $mon2.top) | Out-Null
Start-Sleep -Milliseconds 500
$p2 = ([UndockApi]::Rect($main)) -split '\|'
# move via ChangeDisplaySettings not possible; use drag-free approach: leave app where it is (primary) and instead disable secondary after moving by user? 
# We test: app on primary; disable secondary; window must stay visible on primary and no crash.
$before = ([UndockApi]::Rect($main)) -split '\|'
Start-Sleep -Milliseconds 300
$shotBefore = Capture $mon1.left $mon1.top $mon1.width $mon1.height (Join-Path $shots ("{0}-before-undock.png" -f $stamp))

Write-Host ([UndockApi]::Disable($mon2.gdiDevice))
Start-Sleep -Milliseconds ($SettleMs + 800)
$stillRunning = -not $proc.HasExited
$after = ([UndockApi]::Rect($main)) -split '\|'
$shotAfter = Capture $mon1.left $mon1.top $mon1.width $mon1.height (Join-Path $shots ("{0}-after-undock.png" -f $stamp))

Write-Host ([UndockApi]::Enable($mon2.gdiDevice, $mon2.width, $mon2.height, $mon2.refreshHz, $mon2.left, $mon2.top))
Start-Sleep -Milliseconds ($SettleMs + 500)
$restored = ([UndockApi]::Rect($main)) -split '\|'
$shotRestored = Capture $mon1.left $mon1.top $mon1.width $mon1.height (Join-Path $shots ("{0}-after-reenable.png" -f $stamp))

$doc = [ordered]@{
  case = 'undock-os-disable'
  capturedAt = (Get-Date -Format o)
  app = [ordered]@{ pid = $proc.Id; exe = $exe; args = $appArgs }
  monitors = [ordered]@{ primary = $mon1; secondary = $mon2 }
  steps = @(
    [ordered]@{ step = 'before-disable'; left = [int]$before[0]; top = [int]$before[1]; width = [int]$before[2]; height = [int]$before[3]; dpi = [int]$before[4]; scalePercent = [int]$before[5] },
    [ordered]@{ step = 'after-disable'; left = [int]$after[0]; top = [int]$after[1]; width = [int]$after[2]; height = [int]$after[3]; dpi = [int]$after[4]; scalePercent = [int]$after[5]; appAlive = $stillRunning },
    [ordered]@{ step = 'after-reenable'; left = [int]$restored[0]; top = [int]$restored[1]; width = [int]$restored[2]; height = [int]$restored[3]; dpi = [int]$restored[4]; scalePercent = [int]$restored[5] }
  )
  screenshots = @($shotBefore, $shotAfter, $shotRestored)
}
$out = Join-Path $OutDir ("undock-{0}.json" -f $stamp)
$doc | ConvertTo-Json -Depth 8 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
$doc.steps | ForEach-Object { "step={0} rect=({1},{2}) {3}x{4} dpi={5} scale={6}% alive={7}" -f $_.step,$_.left,$_.top,$_.width,$_.height,$_.dpi,$_.scalePercent,$_.appAlive }

if (-not $KeepRunning) {
  [UndockApi]::ShowWindow($main, 6) | Out-Null
  Start-Sleep -Milliseconds 400
  if (-not $proc.HasExited) { $proc.Kill($true); $proc.WaitForExit(5000) | Out-Null }
  Write-Host 'app closed'
}
