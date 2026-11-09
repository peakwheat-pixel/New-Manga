# FEA-07-AC5-NATIVE-1 / run-native-matrix.ps1
# 真实桌面驱动：启动 NewManga.App（隔离根），枚举窗口，跨 2K/4K 移动，逐案例截图 + JSON。
# 用法：pwsh -File run-native-matrix.ps1 -Case mixed-dpi-move [-KeepRunning]
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][ValidateSet('mixed-dpi-move', 'straddle', 'cross-persistence')][string]$Case,
  [string]$OutDir = "",
  [switch]$KeepRunning,
  [int]$SettleMs = 1200
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

public static class WinProbe {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int left, top, right, bottom; }
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc cb, IntPtr l);
  public delegate bool EnumWindowsProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetClassNameW(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern uint GetDpiForWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int cx, int cy, uint flags);
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr v);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);

  public static string[] WindowsOf(uint pid) {
    SetProcessDpiAwarenessContext(new IntPtr(-4));
    var rows = new List<string>();
    EnumWindows((h, l) => {
      uint p; GetWindowThreadProcessId(h, out p);
      if (p != pid) return true;
      bool vis = IsWindowVisible(h);
      var t = new StringBuilder(256); GetWindowTextW(h, t, 256);
      var c = new StringBuilder(256); GetClassNameW(h, c, 256);
      RECT r; GetWindowRect(h, out r);
      uint dpi = 0; try { dpi = GetDpiForWindow(h); } catch {}
      rows.Add(string.Format("{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}|{8}", h, vis ? 1 : 0, r.left, r.top, r.right, r.bottom,
        dpi, Math.Round(dpi / 96.0 * 100), t.ToString().Replace("|", "/") + "::" + c.ToString().Replace("|", "/")));
      return true;
    }, IntPtr.Zero);
    return rows.ToArray();
  }
  public static string Move(IntPtr h, int x, int y, int w, int hgt) {
    bool ok = SetWindowPos(h, IntPtr.Zero, x, y, w, hgt, 0x0004 /*SWP_NOZORDER*/);
    return "ok=" + ok;
  }
  public static string Show(IntPtr h, int cmd) { return "ok=" + ShowWindow(h, cmd); }
}
'@
Add-Type -TypeDefinition $cs -ErrorAction Stop
Add-Type -AssemblyName System.Drawing

function Capture-Monitor([string]$name, [int]$x, [int]$y, [int]$w, [int]$h, [string]$file) {
  $bmp = New-Object System.Drawing.Bitmap $w, $h
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen($x, $y, 0, 0, (New-Object System.Drawing.Size $w, $h))
  $g.Dispose()
  $bmp.Save($file, [System.Drawing.Imaging.ImageFormat]::Png)
  $bmp.Dispose()
  $sha = (Get-FileHash -Algorithm SHA256 -Path $file).Hash.ToLowerInvariant()
  return [pscustomobject]@{ name = $name; file = (Split-Path $file -Leaf); width = $w; height = $h; sha256 = $sha }
}

function Get-Displays {
  $probe = Join-Path $PSScriptRoot 'probe-displays.ps1'
  $out = & pwsh -NoProfile -File $probe -OutDir $OutDir -Label ('matrix-' + $Case) 2>&1 | Out-String
  $latest = Get-ChildItem $OutDir -Filter 'displays-matrix-*.json' -ErrorAction SilentlyContinue | Sort-Object LastWriteTime | Select-Object -Last 1
  if (-not $latest) { throw "display probe produced no JSON. output: $out" }
  return (Get-Content -Raw -Path $latest.FullName | ConvertFrom-Json)
}

$disp = Get-Displays
$mon1 = $disp.displays | Where-Object { $_.primary -eq $true } | Select-Object -First 1
$mon2 = $disp.displays | Where-Object { $_.primary -ne $true } | Select-Object -First 1
if (-not $mon1 -or -not $mon2) { throw "need two active displays; got $($disp.displays.Count)" }
Write-Host ("mon1={0} {1}x{2}@{3}% | mon2={4} {5}x{6}@{7}%" -f $mon1.friendlyName,$mon1.width,$mon1.height,$mon1.scalePercent,$mon2.friendlyName,$mon2.width,$mon2.height,$mon2.scalePercent)

$root = Join-Path $env:TEMP ("nm-fea07-ac5-{0}" -f $stamp)
$dataRoot = Join-Path $root 'data'; $logDir = Join-Path $root 'logs'; $themeHome = Join-Path $root 'theme'
New-Item -ItemType Directory -Force -Path $dataRoot,$logDir,$themeHome | Out-Null
$exe = Join-Path $repo 'apps\desktop-avalonia\src\NewManga.App\bin\Release\net9.0\NewManga.App.exe'
if (-not (Test-Path $exe)) { throw "missing exe: $exe" }
$appArgs = @('--data-root', $dataRoot, '--log-dir', $logDir, '--theme-home', $themeHome, '--shell=v2')
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $exe
$psi.WorkingDirectory = (Split-Path $exe -Parent)
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true
foreach ($a in $appArgs) { $psi.ArgumentList.Add($a) }
$proc = [System.Diagnostics.Process]::Start($psi)
Write-Host "launched pid=$($proc.Id) exe=$exe"

$main = [IntPtr]::Zero
for ($i = 0; $i -lt 40; $i++) {
  Start-Sleep -Milliseconds 500
  $wins = [WinProbe]::WindowsOf([uint32]$proc.Id)
  foreach ($row in $wins) {
    $p = $row -split '\|', 9
    if ($p[1] -eq '1' -and $p[8] -notmatch 'Popup|ToolTip|IME') { $main = [IntPtr][int64]$p[0]; break }
  }
  if ($main -ne [IntPtr]::Zero) { break }
}
if ($main -eq [IntPtr]::Zero) { throw "main window not found (pid $($proc.Id))" }
Write-Host "main hwnd=$main"

$results = @()
function Add-Result($name, $extra) {
  $wins = [WinProbe]::WindowsOf([uint32]$proc.Id)
  $mainRow = $wins | Where-Object { ($_ -split '\|')[0] -eq "$([int64]$main)" } | Select-Object -First 1
  $p = if ($mainRow) { $mainRow -split '\|', 9 } else { @() }
  $rec = [ordered]@{
    case = $Case; step = $name
    windowCount = ($wins | Where-Object { ($_ -split '\|')[1] -eq '1' }).Count
    main = if ($p.Count -ge 9) { [ordered]@{ hwnd = [int64]$main; visible = ($p[1] -eq '1'); left = [int]$p[2]; top = [int]$p[3]; right = [int]$p[4]; bottom = [int]$p[5]; width = [int]$p[4] - [int]$p[2]; height = [int]$p[5] - [int]$p[3]; dpi = [int]$p[6]; scalePercent = [int]$p[7]; text = $p[8] } } else { $null }
    windows = @($wins | ForEach-Object { $q = $_ -split '\|', 9; [ordered]@{ hwnd = [int64]$q[0]; visible = ($q[1] -eq '1'); left = [int]$q[2]; top = [int]$q[3]; width = [int]$q[4] - [int]$q[2]; height = [int]$q[5] - [int]$q[3]; dpi = [int]$q[6]; scalePercent = [int]$q[7]; titleClass = $q[8] } })
    extra = $extra
  }
  $script:results += ,$rec
}

$shots1 = @()
$shots1 += Capture-Monitor 'mon1-before' $mon1.left $mon1.top $mon1.width $mon1.height (Join-Path $shots ("{0}-mon1-before.png" -f $stamp))
Add-Result 'launch' ([ordered]@{ note = 'app launched, initial placement' })

# place centered on mon1
$w = [int]($mon1.width * 0.7); $h = [int]($mon1.height * 0.7)
$mx = $mon1.left + [int](($mon1.width - $w) / 2); $my = $mon1.top + [int](($mon1.height - $h) / 2)
[WinProbe]::Move($main, $mx, $my, $w, $h) | Out-Null
Start-Sleep -Milliseconds $SettleMs
$shots2 = Capture-Monitor 'mon1-placed' $mon1.left $mon1.top $mon1.width $mon1.height (Join-Path $shots ("{0}-mon1-placed.png" -f $stamp))
Add-Result 'placed-on-mon1' ([ordered]@{ requested = [ordered]@{ x = $mx; y = $my; w = $w; h = $h } })

# move to mon2
$w2 = [int]($mon2.width * 0.6); $h2 = [int]($mon2.height * 0.6)
$mx2 = $mon2.left + [int](($mon2.width - $w2) / 2); $my2 = $mon2.top + [int](($mon2.height - $h2) / 2)
[WinProbe]::Move($main, $mx2, $my2, $w2, $h2) | Out-Null
Start-Sleep -Milliseconds $SettleMs
$shots3 = Capture-Monitor 'mon2-placed' $mon2.left $mon2.top $mon2.width $mon2.height (Join-Path $shots ("{0}-mon2-placed.png" -f $stamp))
Add-Result 'moved-to-mon2' ([ordered]@{ requested = [ordered]@{ x = $mx2; y = $my2; w = $w2; h = $h2 }; mon2 = [ordered]@{ left = $mon2.left; top = $mon2.top; width = $mon2.width; height = $mon2.height; scale = $mon2.scalePercent } })

# straddle boundary
$sx = $mon2.left - [int]($w2 / 2)
[WinProbe]::Move($main, $sx, $mon2.top + 80, $w2, [int]($h2 * 0.8)) | Out-Null
Start-Sleep -Milliseconds $SettleMs
$shots4 = Capture-Monitor 'straddle-full' 0 0 ([int]$disp.displays[0].width + [int]$mon2.width) ([math]::Max([int]$mon1.height, [int]$mon2.height)) (Join-Path $shots ("{0}-straddle.png" -f $stamp))
Add-Result 'straddle-boundary' ([ordered]@{ requestedX = $sx })

# back to mon1 (persistence / no drift)
[WinProbe]::Move($main, $mx, $my, $w, $h) | Out-Null
Start-Sleep -Milliseconds $SettleMs
Add-Result 'back-to-mon1' ([ordered]@{ requested = [ordered]@{ x = $mx; y = $my; w = $w; h = $h } })
$shots5 = Capture-Monitor 'mon1-back' $mon1.left $mon1.top $mon1.width $mon1.height (Join-Path $shots ("{0}-mon1-back.png" -f $stamp))

$doc = [ordered]@{
  case = $Case
  capturedAt = (Get-Date -Format o)
  app = [ordered]@{ exe = $exe; pid = $proc.Id; args = $appArgs; dataRoot = $dataRoot; logDir = $logDir; themeHome = $themeHome }
  displays = $disp.displays
  steps = $results
  screenshots = @($shots1 + $shots2 + $shots3 + $shots4 + $shots5)
}
$out = Join-Path $OutDir ("native-{0}-{1}.json" -f $Case, $stamp)
$doc | ConvertTo-Json -Depth 10 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"

if (-not $KeepRunning) {
  try { [WinProbe]::Show($main, 6) | Out-Null } catch {}
  Start-Sleep -Milliseconds 400
  if (-not $proc.HasExited) { $proc.Kill($true); $proc.WaitForExit(5000) | Out-Null }
  Write-Host "app closed"
} else {
  Write-Host "app left running (pid $($proc.Id))"
}
$results | ForEach-Object { "{0,-20} dpi={1} rect=({2},{3}) {4}x{5} scale={6}%" -f $_.step, $_.main.dpi, $_.main.left, $_.main.top, $_.main.width, $_.main.height, $_.main.scalePercent }
