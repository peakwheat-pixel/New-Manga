# FEA-07-AC5-NATIVE-1 / post-f11.ps1
# 直接向应用主窗 PostMessage WM_KEYDOWN/WM_KEYUP(VK_F11)，再轮询沉浸窗口。
[CmdletBinding()]
param([string]$OutDir = "", [string]$ShotDir = "G:\CODEX\New Manga.workspace\FEA-07-AC5-NATIVE-1\ac5-fullscreen")
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $repo 'verification\FEA-07-AC5-NATIVE-1\evidence' }
New-Item -ItemType Directory -Force -Path $OutDir, $ShotDir | Out-Null
Add-Type -AssemblyName System.Drawing

$cs = @'
using System; using System.Collections.Generic; using System.Runtime.InteropServices; using System.Text;
public static class PostKey {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int left, top, right, bottom; }
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern int GetWindowLongW(IntPtr h, int i);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool PostMessageW(IntPtr h, uint msg, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr v);
  public static string[] V(uint pid) {
    SetProcessDpiAwarenessContext(new IntPtr(-4));
    var l = new List<string>();
    EnumWindows((h,x) => { uint p; GetWindowThreadProcessId(h, out p); if (p != pid || !IsWindowVisible(h)) return true;
      var t=new StringBuilder(200); GetWindowTextW(h,t,200); RECT r; GetWindowRect(h,out r);
      int st=GetWindowLongW(h,-16); bool cap=(st&0x00C00000)==0x00C00000;
      l.Add(string.Format("{0}|{1}|{2}|{3}|{4}|{5}|{6}", h, r.left,r.top,r.right-r.left,r.bottom-r.top, cap?1:0, t)); return true; }, IntPtr.Zero);
    return l.ToArray();
  }
  public static int F11(IntPtr h) {
    bool d = PostMessageW(h, 0x0100, (IntPtr)0x7A, (IntPtr)0x00470001); // WM_KEYDOWN VK_F11, scan 0x47
    System.Threading.Thread.Sleep(60);
    bool u = PostMessageW(h, 0x0101, (IntPtr)0x7A, unchecked((IntPtr)0xC0470001)); // WM_KEYUP
    return (d?1:0)+(u?2:0);
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
$pidA = $app.Id
$main = $null
foreach ($l in [PostKey]::V([uint32]$pidA)) { $p = $l -split '\|',7; if ($p[6] -eq 'New Manga') { $main = $p } }
if (-not $main) { throw 'main window not found' }
$hwnd = [IntPtr][int64]$main[0]
[PostKey]::SetForegroundWindow($hwnd) | Out-Null
Start-Sleep -Milliseconds 400
$rc = [PostKey]::F11($hwnd)
Write-Host "PostMessage F11 rc=$rc"
$found = $null
for ($i = 0; $i -lt 40; $i++) {
  Start-Sleep -Milliseconds 150
  foreach ($l in [PostKey]::V([uint32]$pidA)) { $p = $l -split '\|',7; if ($p[6] -ne 'New Manga') { $found = $p; break } }
  if ($found) { break }
}
$shot = $null
if ($found) {
  $shot = Capture 'post-f11-immersive'
  Write-Host ("IMMERSIVE rect=({0},{1}) {2}x{3} caption={4} title={5}" -f $found[1],$found[2],$found[3],$found[4],$found[5],$found[6])
} else { Write-Host 'not found' }
$doc = [ordered]@{ action='post-f11'; capturedAt=(Get-Date -Format o); pid=$pidA; rc=$rc; found=($null -ne $found); immersive=if($found){[ordered]@{left=[int]([int64]$found[1]);top=[int]([int64]$found[2]);width=[int]([int64]$found[3]);height=[int]([int64]$found[4]);hasCaption=($found[5]-eq'1');title=$found[6];coversPrimary=(([int64]$found[1] -le 0)-and([int64]$found[2] -le 0)-and([int64]$found[3] -ge 2560)-and([int64]$found[4] -ge 1440))}}else{$null}; screenshot=$shot }
$out = Join-Path $OutDir ("post-f11-{0}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$doc | ConvertTo-Json -Depth 6 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
