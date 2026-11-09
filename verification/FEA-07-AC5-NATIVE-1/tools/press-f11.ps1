# FEA-07-AC5-NATIVE-1 / press-f11.ps1
# 用 SendInput（硬件级按键）向 NewManga.App 发送一次 F11，并轮询捕获沉浸 ReaderWindow。
[CmdletBinding()]
param([string]$OutDir = "", [string]$ShotDir = "G:\CODEX\New Manga.workspace\FEA-07-AC5-NATIVE-1\ac5-fullscreen", [switch]$KeepOpen)
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
public static class F11Snd {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int left, top, right, bottom; }
  [StructLayout(LayoutKind.Sequential)] public struct INPUT { public uint type; public KEYBDINPUT ki; public ulong pad; }
  [StructLayout(LayoutKind.Sequential)] public struct KEYBDINPUT { public ushort wVk; public ushort wScan; public uint dwFlags; public uint time; public IntPtr dwExtraInfo; }
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern int GetWindowLongW(IntPtr h, int i);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, UIntPtr e);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern uint SendInput(uint n, INPUT[] inputs, int size);
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr v);
  [DllImport("user32.dll")] public static extern int GetWindowLongPtrW(IntPtr h, int i);

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
  public static void Click(int x,int y){ SetCursorPos(x,y); System.Threading.Thread.Sleep(180); mouse_event(0x0002,0,0,0,UIntPtr.Zero); System.Threading.Thread.Sleep(110); mouse_event(0x0004,0,0,0,UIntPtr.Zero); }
  public static uint PressF11() {
    var inputs = new INPUT[2];
    inputs[0].type = 1; inputs[0].ki.wVk = 0x7A; inputs[0].ki.dwFlags = 0; // VK_F11 down
    inputs[1].type = 1; inputs[1].ki.wVk = 0x7A; inputs[1].ki.dwFlags = 2; // key up
    return SendInput(2, inputs, Marshal.SizeOf(typeof(INPUT)));
  }
  public static string Fg() { return GetForegroundWindow().ToString(); }
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
$wins = [F11Snd]::Visible([uint32]$pidApp)
$main = $null
foreach ($l in $wins) { $p = $l -split '\|',7; if ($p[6] -eq 'New Manga') { $main = $p } }
if (-not $main) { throw 'main window not found' }
[F11Snd]::SetForegroundWindow([IntPtr][int64]$main[0]) | Out-Null
Start-Sleep -Milliseconds 500
$cx = [int]$main[1] + [int]([int]$main[3] * 0.5); $cy = [int]$main[2] + [int]([int]$main[4] * 0.55)
[F11Snd]::Click($cx, $cy)
Start-Sleep -Milliseconds 800
Write-Host "fg=$([F11Snd]::Fg()) expected=$($main[0])"
$sent = [F11Snd]::PressF11()
Write-Host "SendInput returned=$sent"

$found = $null
for ($i = 0; $i -lt 40; $i++) {
  Start-Sleep -Milliseconds 150
  $now = [F11Snd]::Visible([uint32]$pidApp)
  foreach ($l in $now) { $p = $l -split '\|',7; if ($p[6] -ne 'New Manga') { $found = $p; break } }
  if ($found) { break }
}
$shot = Capture 'f11-sendinput'
$doc = [ordered]@{
  action='press-f11-sendinput'; capturedAt=(Get-Date -Format o); pid=$pidApp
  sendInputReturned=$sent; found=($null -ne $found)
  windows=[F11Snd]::Visible([uint32]$pidApp)
  immersive=if ($found) { [ordered]@{ hwnd=[int64]$found[0]; left=[int]([int64]$found[1]); top=[int]([int64]$found[2]); width=[int]([int64]$found[3]); height=[int]([int64]$found[4]); hasCaption=($found[5] -eq '1'); title=$found[6]; coversPrimary=(([int64]$found[1] -le 0) -and ([int64]$found[2] -le 0) -and ([int64]$found[3] -ge 2560) -and ([int64]$found[4] -ge 1440)) } } else { $null }
  screenshot=$shot
}
$out = Join-Path $OutDir ("press-f11-{0}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$doc | ConvertTo-Json -Depth 6 | Set-Content -Path $out -Encoding UTF8
Write-Host "saved: $out"
if ($found) { Write-Host ("IMMERSIVE: rect=({0},{1}) {2}x{3} caption={4} title={5}" -f $found[1],$found[2],$found[3],$found[4],$found[5],$found[6]) } else { Write-Host 'immersive NOT found' }
