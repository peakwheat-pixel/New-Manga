# DISPLAY-PERF-DECISION-1 / baseline — first-paint pixel probe (fast path).
#
# The frozen release exe exposes NO WebView2 CDP endpoint (evidence in
# REPORT.md), so the page cannot be asked when it painted. This probe answers
# "when did the window start showing content" from the OUTSIDE: it blits the
# app window's client area ~60x/second and records a pixel signature per frame
# (mean luminance, horizontal edge energy, dark fraction, hash). The full
# series is written verbatim so the first-content timestamp is re-derivable.
#
# The sampling hot loop lives in compiled C# (Bitmap.LockBits + Marshal.Copy);
# a PowerShell GetPixel loop needed ~1.1 s/frame, which was far too coarse.
#
# Observes only: never sends input, never touches app data.

param(
  [Parameter(Mandatory = $true)][string]$PidFile,
  [Parameter(Mandatory = $true)][string]$OutFile,
  [string]$ShotDir = "",
  [int]$SampleMs = 6000,
  [int]$TimeoutMs = 40000,
  [int]$SleepMs = 8
)

$ErrorActionPreference = "Continue"
Add-Type -AssemblyName System.Drawing

$cs = @"
using System;
using System.Text;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;

public class DpPaint {
  public Bitmap bmp;
  public Graphics g;
  public int W, H;

  [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr hWnd, out RECT r);
  [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr hWnd, ref POINT p);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();

  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
  [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X; public int Y; }

  public DpPaint(int w, int h) {
    W = w; H = h;
    bmp = new Bitmap(w, h, PixelFormat.Format32bppArgb);
    g = Graphics.FromImage(bmp);
    g.PixelOffsetMode = System.Drawing.Drawing2D.PixelOffsetMode.Half;
  }

  // returns { meanL, edge, darkFrac, hash } or null on failure
  public long[] Grab(int srcX, int srcY, int gx, int gy) {
    try {
      g.CopyFromScreen(srcX, srcY, 0, 0, new Size(W, H), CopyPixelOperation.SourceCopy);
    } catch { return null; }
    BitmapData bd = null;
    long meanSum = 0, edgeSum = 0, dark = 0, count = 0;
    long hash = 1469598103934665603L;
    int stride = 0;
    try {
      bd = bmp.LockBits(new Rectangle(0, 0, W, H), ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
      stride = bd.Stride;
      byte[] buf = new byte[stride * H];
      Marshal.Copy(bd.Scan0, buf, 0, buf.Length);
      for (int iy = 0; iy < gy; iy++) {
        int py = (int)((long)H * (iy * 2 + 1) / (gy * 2));
        if (py >= H) py = H - 1;
        long prevL = -1;
        for (int ix = 0; ix < gx; ix++) {
          int px = (int)((long)W * (ix * 2 + 1) / (gx * 2));
          if (px >= W) px = W - 1;
          int idx = py * stride + px * 4;
          int b = buf[idx], gg = buf[idx + 1], r = buf[idx + 2];
          long L = (299L * r + 587L * gg + 114L * b) / 1000L;
          meanSum += L;
          if (L < 40) dark++;
          if (prevL >= 0) { long d = L - prevL; if (d < 0) d = -d; edgeSum += d; }
          prevL = L;
          hash = unchecked(hash * 1099511628211L + L);
          if (hash < 0) hash = hash & 0x7FFFFFFFFFFFFFFFL;
          count++;
        }
      }
    } finally {
      if (bd != null) bmp.UnlockBits(bd);
    }
    if (count == 0) return null;
    long denom = Math.Max(1L, count - gy);
    return new long[] { (meanSum * 1000L) / count, (edgeSum * 1000L) / denom, (dark * 1000L) / count, hash };
  }

  public void SavePng(string path) { try { bmp.Save(path, ImageFormat.Png); } catch { } }
}
"@
if (-not ("DpPaint" -as [type])) { Add-Type -TypeDefinition $cs -ReferencedAssemblies System.Drawing }
[void][DpPaint]::SetProcessDPIAware()

function Now-Ms { [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds() }

$sink = New-Object System.IO.StreamWriter($OutFile, $false, (New-Object System.Text.UTF8Encoding($false)))
$sink.AutoFlush = $true
function Emit([hashtable]$o) { $sink.WriteLine(($o | ConvertTo-Json -Compress)) }

Emit @{ kind = "paint_probe_ready"; epochMs = (Now-Ms) }

# ---- wait for the app pid ------------------------------------------------
$appPid = 0
$deadline = (Now-Ms) + 30000
while ((Now-Ms) -lt $deadline) {
  if (Test-Path -LiteralPath $PidFile) {
    try {
      $info = Get-Content -Raw -LiteralPath $PidFile | ConvertFrom-Json
      if ($info.appPid -and [int]$info.appPid -gt 0) { $appPid = [int]$info.appPid; break }
    } catch { }
  }
  Start-Sleep -Milliseconds 2
}
if ($appPid -eq 0) { Emit @{ kind = "paint_probe_error"; epochMs = (Now-Ms); error = "pid file never appeared" }; $sink.Dispose(); exit 2 }

$proc = $null
for ($i = 0; $i -lt 800; $i++) { try { $proc = [System.Diagnostics.Process]::GetProcessById($appPid); break } catch { Start-Sleep -Milliseconds 2 } }

$hwnd = [IntPtr]::Zero
$deadline = (Now-Ms) + $TimeoutMs
while ((Now-Ms) -lt $deadline) {
  try { $proc.Refresh(); if ($proc.MainWindowHandle -ne 0) { $hwnd = [IntPtr]$proc.MainWindowHandle; break } } catch { }
  Start-Sleep -Milliseconds 2
}
if ($hwnd -eq [IntPtr]::Zero) { Emit @{ kind = "paint_probe_error"; epochMs = (Now-Ms); error = "no visible window" }; $sink.Dispose(); exit 3 }
Emit @{ kind = "paint_window_found"; epochMs = (Now-Ms); hwnd = [string]$hwnd }

$rect = New-Object DpPaint+RECT
[void][DpPaint]::GetClientRect($hwnd, [ref]$rect)
$pt = New-Object DpPaint+POINT
$pt.X = 0; $pt.Y = 0
[void][DpPaint]::ClientToScreen($hwnd, [ref]$pt)
$w = [Math]::Max(1, $rect.Right - $rect.Left)
$h = [Math]::Max(1, $rect.Bottom - $rect.Top)
Emit @{ kind = "paint_client_rect"; epochMs = (Now-Ms); x = $pt.X; y = $pt.Y; w = $w; h = $h }

$gx = [Math]::Min(160, [Math]::Max(16, [int]($w / 6)))
$gy = [Math]::Min(120, [Math]::Max(12, [int]($h / 6)))
$painter = New-Object DpPaint($w, $h)

$started = Now-Ms
$frames = 0
$savedBlank = $false
$savedContent = $false
Emit @{ kind = "paint_loop_started"; epochMs = $started; gridX = $gx; gridY = $gy }

while (((Now-Ms) - $started) -lt $SampleMs) {
  $epoch = Now-Ms
  $sig = $painter.Grab($pt.X, $pt.Y, $gx, $gy)
  if ($null -ne $sig) {
    $meanL = [Math]::Round($sig[0] / 1000.0, 3)
    $edge = [Math]::Round($sig[1] / 1000.0, 3)
    $darkFrac = [Math]::Round($sig[2] / 1000.0, 3)
    $isFg = ([DpPaint]::GetForegroundWindow() -eq $hwnd)
    Emit @{ kind = "paint_frame"; epochMs = $epoch; seq = $frames; meanL = $meanL; edge = $edge; darkFrac = $darkFrac; hash = "$($sig[3])"; foreground = $isFg }
    if ($ShotDir) {
      if (-not $savedBlank) { $painter.SavePng((Join-Path $ShotDir "paint-frame-000.png")); $savedBlank = $true }
      elseif (-not $savedContent -and $edge -gt 1.5) { $painter.SavePng((Join-Path $ShotDir "paint-frame-first-content.png")); $savedContent = $true }
    }
    $frames++
  }
  Start-Sleep -Milliseconds $SleepMs
}

Emit @{ kind = "paint_probe_done"; epochMs = (Now-Ms); frames = $frames }
try { $painter.g.Dispose(); $painter.bmp.Dispose() } catch { }
$sink.Dispose()
