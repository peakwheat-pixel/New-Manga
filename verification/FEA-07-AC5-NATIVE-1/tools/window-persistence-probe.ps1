# FEA-07-AC5-NATIVE-1 / window-persistence-probe.ps1
# 关闭/重开两次，记录窗口几何是否持久化（若产品无持久化，则 AC-N4 该子项 NOT_APPLICABLE/NOT_RUN）。
[CmdletBinding()]
param([string]$OutDir = "")
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-AC5-NATIVE-1\evidence' }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'

$cs = @'
using System;
using System.Runtime.InteropServices;
public static class WinRect2 {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int left, top, right, bottom; }
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern uint GetDpiForWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr a, int x, int y, int cx, int cy, uint f);
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
    uint dpi = GetDpiForWindow(h);
    return string.Format("{0}|{1}|{2}|{3}|{4}|{5}", r.left, r.top, r.right - r.left, r.bottom - r.top, dpi, Math.Round(dpi / 96.0 * 100));
  }
}
'@
Add-Type -TypeDefinition $cs -ErrorAction Stop

$root = Join-Path $env:TEMP ("nm-fea07-persist-{0}" -f $stamp)
$dr = Join-Path $root 'data'; $ld = Join-Path $root 'logs'; $th = Join-Path $root 'theme'
New-Item -ItemType Directory -Force -Path $dr, $ld, $th | Out-Null
$exe = Join-Path $repo 'apps\desktop-avalonia\src\NewManga.App\bin\Release\net9.0\NewManga.App.exe'
$appArgs = @('--data-root', $dr, '--log-dir', $ld, '--theme-home', $th, '--shell=v2')

function Launch-App {
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $exe; $psi.WorkingDirectory = (Split-Path $exe -Parent); $psi.UseShellExecute = $false; $psi.CreateNoWindow = $true
  foreach ($a in $appArgs) { $psi.ArgumentList.Add($a) }
  $p = [System.Diagnostics.Process]::Start($psi)
  $h = [IntPtr]::Zero
  for ($i = 0; $i -lt 40; $i++) { Start-Sleep -Milliseconds 500; $h = [WinRect2]::Main([uint32]$p.Id); if ($h -ne [IntPtr]::Zero) { break } }
  if ($h -eq [IntPtr]::Zero) { throw 'window not found' }
  return @{ proc = $p; hwnd = $h }
}

$a = Launch-App
Start-Sleep -Milliseconds 1200
$rectInitial = ([WinRect2]::Rect($a.hwnd)) -split '\|'
# 明确移动到 4K 上（记录为“用户最后位置”）
[WinRect2]::SetWindowPos($a.hwnd, [IntPtr]::Zero, 3600, 300, 1800, 1000, 0x0004) | Out-Null
Start-Sleep -Milliseconds 1200
$rectMoved = ([WinRect2]::Rect($a.hwnd)) -split '\|'
if (-not $a.proc.HasExited) { $a.proc.Kill($true); $a.proc.WaitForExit(5000) | Out-Null }
Start-Sleep -Milliseconds 1500

$b = Launch-App
Start-Sleep -Milliseconds 1500
$rectReopen = ([WinRect2]::Rect($b.hwnd)) -split '\|'
if (-not $b.proc.HasExited) { $b.proc.Kill($true); $b.proc.WaitForExit(5000) | Out-Null }

$doc = [ordered]@{
  probe = 'window-persistence'
  capturedAt = (Get-Date -Format o)
  app = [ordered]@{ exe = $exe; args = $appArgs; dataRoot = $dr }
  initial = [ordered]@{ left = [int]$rectInitial[0]; top = [int]$rectInitial[1]; width = [int]$rectInitial[2]; height = [int]$rectInitial[3]; dpi = [int]$rectInitial[4]; percent = [int]$rectInitial[5] }
  moved = [ordered]@{ left = [int]$rectMoved[0]; top = [int]$rectMoved[1]; width = [int]$rectMoved[2]; height = [int]$rectMoved[3]; dpi = [int]$rectMoved[4]; percent = [int]$rectMoved[5] }
  reopen = [ordered]@{ left = [int]$rectReopen[0]; top = [int]$rectReopen[1]; width = [int]$rectReopen[2]; height = [int]$rectReopen[3]; dpi = [int]$rectReopen[4]; percent = [int]$rectReopen[5] }
  restored = (([int]$rectReopen[0] -eq [int]$rectMoved[0]) -and ([int]$rectReopen[1] -eq [int]$rectMoved[1]) -and ([int]$rectReopen[2] -eq [int]$rectMoved[2]) -and ([int]$rectReopen[3] -eq [int]$rectMoved[3]))
}
$out = Join-Path $OutDir ("window-persistence-{0}.json" -f $stamp)
$doc | ConvertTo-Json -Depth 5 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
Write-Host ("initial=({0},{1}) {2}x{3} | moved=({4},{5}) {6}x{7} | reopen=({8},{9}) {10}x{11} | restored={12}" -f `
  $rectInitial[0],$rectInitial[1],$rectInitial[2],$rectInitial[3],$rectMoved[0],$rectMoved[1],$rectMoved[2],$rectMoved[3],$rectReopen[0],$rectReopen[1],$rectReopen[2],$rectReopen[3],$doc.restored)
