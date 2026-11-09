# FEA-07-AC5-NATIVE-1 / watch-immersive.ps1
# 100ms 轮询：一旦出现非 "New Manga" 的顶层窗口，立即抓几何/样式/截图并落盘；再等它消失记录关闭。
[CmdletBinding()]
param([int]$TimeoutSec = 180, [string]$OutDir = "", [string]$ShotDir = "G:\CODEX\New Manga.workspace\FEA-07-AC5-NATIVE-1\ac5-fullscreen")
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-AC5-NATIVE-1\evidence' }
New-Item -ItemType Directory -Force -Path $OutDir, $ShotDir | Out-Null
Add-Type -AssemblyName System.Drawing

$cs = @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
public static class WatchImm {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int left, top, right, bottom; }
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern int GetWindowLongW(IntPtr h, int i);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr v);
  public static string[] Visible(uint pid) {
    SetProcessDpiAwarenessContext(new IntPtr(-4));
    var l = new List<string>();
    EnumWindows((h,x) => {
      uint p; GetWindowThreadProcessId(h, out p);
      if (p != pid || !IsWindowVisible(h)) return true;
      var t=new StringBuilder(200); GetWindowTextW(h,t,200);
      RECT r; GetWindowRect(h,out r);
      int style = GetWindowLongW(h, -16);
      bool caption = (style & 0x00C00000) == 0x00C00000;
      l.Add(string.Format("{0}|{1}|{2}|{3}|{4}|{5}|{6}", h, r.left,r.top,r.right-r.left,r.bottom-r.top, caption?1:0, t));
      return true;
    }, IntPtr.Zero);
    return l.ToArray();
  }
}
'@
Add-Type -TypeDefinition $cs -ErrorAction Stop

function Capture($name) {
  $f = Join-Path $ShotDir ("{0}-{1}.png" -f (Get-Date -Format 'yyyyMMdd-HHmmss'), $name)
  $b = New-Object System.Drawing.Bitmap 2560,1440
  $g = [System.Drawing.Graphics]::FromImage($b); $g.CopyFromScreen(0,0,0,0,(New-Object System.Drawing.Size 2560,1440)); $g.Dispose()
  $b.Save($f, [System.Drawing.Imaging.ImageFormat]::Png); $b.Dispose()
  [pscustomobject]@{ file=$f; sha256=(Get-FileHash -Algorithm SHA256 -Path $f).Hash.ToLowerInvariant() }
}

$app = Get-Process NewManga.App | Sort-Object StartTime | Select-Object -Last 1
$pidApp = $app.Id
$deadline = (Get-Date).AddSeconds($TimeoutSec)
$found = $null; $shot = $null; $closedAt = $null
while ((Get-Date) -lt $deadline) {
  $now = @([WatchImm]::Visible([uint32]$pidApp))
  $extra = @($now | Where-Object { ($_ -split '\|',7)[6] -ne 'New Manga' })
  if ($extra.Count -gt 0 -and -not $found) {
    $p = $extra[0] -split '\|',7
    $found = [ordered]@{ hwnd=[int64]$p[0]; left=[int]([int64]$p[1]); top=[int]([int64]$p[2]); width=[int]([int64]$p[3]); height=[int]([int64]$p[4]); hasCaption=($p[5] -eq '1'); title=$p[6]; coversPrimary=(([int64]$p[1] -le 0) -and ([int64]$p[2] -le 0) -and ([int64]$p[3] -ge 2560) -and ([int64]$p[4] -ge 1440)) }
    $shot = Capture 'watch-immersive'
    Write-Host "FOUND: $($found | ConvertTo-Json -Compress)"
    break
  }
  Start-Sleep -Milliseconds 100
}
$doc = [ordered]@{ action='watch-immersive'; capturedAt=(Get-Date -Format o); pid=$pidApp; found=($null -ne $found); immersive=$found; screenshot=$shot; windows=[WatchImm]::Visible([uint32]$pidApp) }
$out = Join-Path $OutDir ("watch-immersive-{0}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$doc | ConvertTo-Json -Depth 6 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
if ($found) { Write-Host ("IMMERSIVE rect=({0},{1}) {2}x{3} caption={4} title={5} covers={6}" -f $found.left,$found.top,$found.width,$found.height,$found.hasCaption,$found.title,$found.coversPrimary) }
