# DISPLAY-PERF-DECISION-1 / baseline — Win32 cold-start probe.
#
# Observes (never touches) the real packaged app:
#   * OS process StartTime                 -> authoritative "process start"
#   * core_service.exe child               -> "Core sidecar spawn" (ParentProcessId checked)
#   * first visible top-level window       -> "window visible" (ownership + class verified)
#   * WebView2 browser processes           -> "webview created" (younger than our t0 only)
#   * catalog database first created       -> "Core catalog authority up"
#
# Output: JSON-lines, flushed immediately, one object per event.

param(
  [Parameter(Mandatory = $true)][string]$PidFile,
  [Parameter(Mandatory = $true)][string]$ClockFile,
  [Parameter(Mandatory = $true)][string]$OutFile,
  [int]$TimeoutMs = 120000
)

$ErrorActionPreference = "Continue"

Add-Type -TypeDefinition @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class DpWin {
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern int GetWindowTextW(IntPtr hWnd, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern int GetClassNameW(IntPtr hWnd, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
}
"@

function Now-Ms { [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds() }
function Epoch-Ms([datetime]$dt) { ([DateTimeOffset]$dt).ToUnixTimeMilliseconds() }

$clock = Get-Content -Raw -Path $ClockFile | ConvertFrom-Json
$t0 = [long]$clock.t0EpochMs

$sink = New-Object System.IO.StreamWriter($OutFile, $false, (New-Object System.Text.UTF8Encoding($false)))
$sink.AutoFlush = $true
function Emit([hashtable]$obj) { $obj["t0EpochMs"] = $t0; $sink.WriteLine(($obj | ConvertTo-Json -Compress)) }

Emit @{ kind = "probe_ready"; epochMs = (Now-Ms) }

# ---- phase A: wait for node to publish the spawned pid -------------------
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
if ($appPid -eq 0) { Emit @{ kind = "probe_error"; epochMs = (Now-Ms); error = "pid file never appeared" }; $sink.Dispose(); exit 2 }
Emit @{ kind = "pid_observed"; epochMs = (Now-Ms); appPid = $appPid }

$app = $null
for ($i = 0; $i -lt 800; $i++) { try { $app = [System.Diagnostics.Process]::GetProcessById($appPid); break } catch { Start-Sleep -Milliseconds 2 } }
if ($null -eq $app) { Emit @{ kind = "probe_error"; epochMs = (Now-Ms); error = "app pid never resolvable" }; $sink.Dispose(); exit 3 }

try {
  Emit @{ kind = "app_started"; epochMs = (Now-Ms); appPid = $appPid; exeStartEpochMs = (Epoch-Ms $app.StartTime); exeName = $app.ProcessName }
} catch {
  Emit @{ kind = "probe_error"; epochMs = (Now-Ms); error = "StartTime unavailable: $($_.Exception.Message)" }
}

$catalogPath = $clock.catalogDb
$seenCore = @{}
$seenWebview = @{}
$windowVisible = $false
$catalogSeen = $false
$startedAt = Now-Ms
$loopStarted = $startedAt
Emit @{ kind = "probe_loop_started"; epochMs = $loopStarted }

while ($true) {
  $now = Now-Ms
  if ((($now - $startedAt) -gt $TimeoutMs)) { break }

  # ---- real Core sidecar --------------------------------------------------
  try {
    foreach ($p in [System.Diagnostics.Process]::GetProcessesByName("core_service")) {
      $key = [string]$p.Id
      if (-not $seenCore.ContainsKey($key)) {
        $seenCore[$key] = $true
        $parentPid = -1
        try {
          $cim = Get-CimInstance -ClassName Win32_Process -Filter "ProcessId=$($p.Id)" -ErrorAction SilentlyContinue
          if ($cim) { $parentPid = [int]$cim.ParentProcessId }
        } catch { }
        Emit @{ kind = "core_service_first_seen"; epochMs = $now; corePid = $p.Id; parentPid = $parentPid; isOwnChild = ($parentPid -eq $appPid) }
      }
    }
  } catch { }

  # ---- WebView2 browser processes (only ones younger than our launch) ------
  try {
    foreach ($p in [System.Diagnostics.Process]::GetProcessesByName("msedgewebview2")) {
      $key = [string]$p.Id
      if (-not $seenWebview.ContainsKey($key)) {
        $isOurs = $false
        try { if ((Epoch-Ms $p.StartTime) -ge ($t0 - 2000)) { $isOurs = $true } } catch { }
        if (-not $isOurs) { continue }
        $seenWebview[$key] = $true
        if ($seenWebview.Count -eq 1) { Emit @{ kind = "webview2_first_seen"; epochMs = $now; webviewPid = $p.Id } }
      }
    }
  } catch { }

  # ---- first visible top-level window OWNED BY OUR PID -------------------
  if (-not $windowVisible) {
    try {
      $app.Refresh()
      $h = [IntPtr]$app.MainWindowHandle
      if ($h -ne [IntPtr]::Zero) {
        $ownerPid = [uint32]0
        [void][DpWin]::GetWindowThreadProcessId($h, [ref]$ownerPid)
        $sb = New-Object System.Text.StringBuilder 256
        [void][DpWin]::GetWindowTextW($h, $sb, 256)
        $cls = New-Object System.Text.StringBuilder 256
        [void][DpWin]::GetClassNameW($h, $cls, 256)
        # Attribution guard: a window from another process can never be "ours".
        $ownedByApp = ($ownerPid -eq [uint32]$appPid)
        $fg = [DpWin]::GetForegroundWindow()
        Emit @{
          kind = "window_candidate"; epochMs = $now; hwnd = [string]$h; ownerPid = [int]$ownerPid
          ownedByApp = $ownedByApp; visible = [DpWin]::IsWindowVisible($h)
          title = $sb.ToString(); class = $cls.ToString(); isForeground = ($fg -eq $h)
        }
        if ($ownedByApp) {
          Emit @{ kind = "window_visible"; epochMs = $now; hwnd = [string]$h; title = $sb.ToString(); class = $cls.ToString() }
          $windowVisible = $true
        }
      }
    } catch { }
  }

  # ---- Core catalog authority first created ------------------------------
  if (-not $catalogSeen -and $catalogPath) {
    try {
      if (Test-Path -LiteralPath $catalogPath) { Emit @{ kind = "catalog_db_first_seen"; epochMs = $now; path = $catalogPath }; $catalogSeen = $true }
    } catch { }
  }

  # ---- app exit -----------------------------------------------------------
  try { if ($app.HasExited) { Emit @{ kind = "app_exited"; epochMs = $now; exitCode = $app.ExitCode }; break } } catch { }

  if ($windowVisible -and ($seenCore.Count -gt 0) -and ($seenWebview.Count -gt 0) -and $catalogSeen) {
    if (-not $script:settleStart) { $script:settleStart = $now }
    if (($now - $script:settleStart) -gt 1500) { break }
  }

  Start-Sleep -Milliseconds 3
}

Emit @{ kind = "probe_done"; epochMs = (Now-Ms); windowVisible = $windowVisible; coreSeen = $seenCore.Count; webviewSeen = $seenWebview.Count; catalogSeen = $catalogSeen }
$sink.Dispose()
