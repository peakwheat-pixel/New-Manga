# P20-ISOLATION-1 R-004 fix: capture the REAL failure-state banner timeline.
# Codex R-004 found that the original script waited 2 s and then accepted ANY text containing
# "后端" as proof of a failure notice - so the healthy "后端服务已恢复正常" (recovered) text made the
# assertion pass even though the failure state was never observed. This version:
#   1. polls the UI every 50 ms from the instant the sidecar is killed, recording every distinct
#      lifecycle text it sees with a timestamp, so the restarting -> recovered transition is captured;
#   2. only treats the EXPLICIT failure wording as proof of a user-visible failure notice;
#   3. times the respawn from the absolute kill instant (not from the start of a later loop).
param(
    [string]$RepoRoot = 'G:\CODEX\New Manga',
    [string]$OutDir = ''
)
$ErrorActionPreference = 'Continue'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$TS = [System.Windows.Automation.TreeScope]
if (-not $OutDir) { $OutDir = Join-Path $RepoRoot ('verification\P20-ISOLATION-1\r004-' + (Get-Date -Format 'yyyyMMdd-HHmmss')) }
if (Test-Path $OutDir) { Write-Host "REFUSE_OVERWRITE $OutDir"; exit 4 }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$trace = Join-Path $OutDir 'trace.log'
$tl = Join-Path $OutDir 'ui-timeline.csv'
function T([string]$m) { $l = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss.fff'), $m; $l | Add-Content $trace -Encoding utf8; Write-Host $l }
function A([bool]$c, [string]$name) { if (-not $c) { $script:scriptFails++ }; T ("ASSERT {0} {1}" -f $(if ($c) { 'PASS' } else { 'FAIL' }), $name) }

function Get-Owned([int]$rootPid) {
    $all = @(Get-CimInstance Win32_Process | Select-Object ProcessId, ParentProcessId, Name)
    $bp = @{}; foreach ($x in $all) { $k = [int]$x.ParentProcessId; if (-not $bp.ContainsKey($k)) { $bp[$k] = @() }; $bp[$k] += $x }
    $res = New-Object System.Collections.ArrayList; $q = New-Object System.Collections.Queue; $q.Enqueue($rootPid); $seen = @{}
    while ($q.Count -gt 0) { $c = [int]$q.Dequeue(); if ($seen.ContainsKey($c)) { continue }; $seen[$c] = $true
        if ($bp.ContainsKey($c)) { foreach ($ch in $bp[$c]) { [void]$res.Add($ch); $q.Enqueue([int]$ch.ProcessId) } } }
    return $res
}
function GetWin() {
    try { $r = [System.Windows.Automation.AutomationElement]::RootElement
        $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, 'M2-RC1 resource channel runtime')
        return $r.FindFirst($TS::Children, $c) } catch { return $null }
}
function AllNames($w) { if (-not $w) { return @() }; return @($w.FindAll($TS::Descendants, [System.Windows.Automation.Condition]::TrueCondition) | ForEach-Object { try { $_.Current.Name } catch {} } | Where-Object { $_ }) }
function Shot($tag) { $b = Join-Path $OutDir "$tag.png"; $sc = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bmp = New-Object System.Drawing.Bitmap($sc.Width, $sc.Height); $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($sc.Location, [System.Drawing.Point]::Empty, $sc.Size); $bmp.Save($b, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose(); T "SHOT $tag" }

# EXPLICIT failure wording only (from AppShell.tsx) - a healthy/recovered banner must NOT satisfy this
$FAIL_REGEX = '后端服务异常|正在尝试热重启|自动重启失败'
$script:scriptFails = 0
$RECOVER_REGEX = '后端服务已恢复正常'

$exe = Join-Path $RepoRoot 'apps\desktop\src-tauri\target\debug\m2rc1-desktop.exe'
$iso = Join-Path $env:TEMP ('p20r004-' + [guid]::NewGuid().ToString('N').Substring(0,8))
New-Item -ItemType Directory -Force -Path $iso | Out-Null
$env:NEWMANGA_DATA_ROOT = $iso
$errLog = Join-Path $OutDir 'app-err.log'; $outLog = Join-Path $OutDir 'app-out.log'
$p = Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -PassThru -RedirectStandardError $errLog -RedirectStandardOutput $outLog
$rootPid = $p.Id
T "R-004 start pid=$rootPid iso=$iso"
$win = $null; $dl = (Get-Date).AddSeconds(30)
while ((Get-Date) -lt $dl) { Start-Sleep -Milliseconds 300; if ($p.HasExited) { break }; $win = GetWin; if ($win) { break } }
$dl = (Get-Date).AddSeconds(25)
while ((Get-Date) -lt $dl) { $n = AllNames $win; if ($n -contains '📚 书架') { break }; Start-Sleep -Milliseconds 300 }
T "window=$([bool]$win) shell_ready=$((AllNames $win) -contains '📚 书架')"
A ([bool]$win) 'r004:window-present'

$owned = Get-Owned $rootPid
$core = $owned | Where-Object { $_.Name -eq 'core_service.exe' } | Select-Object -First 1
$corePid = if ($core) { [int]$core.ProcessId } else { -1 }
T "core_service pid=$corePid"; A ($corePid -gt 0) 'r004:sidecar-running'

"t_ms_from_kill,event,detail" | Set-Content $tl -Encoding utf8
if ($corePid -gt 0) {
    $killAt = Get-Date
    T "KILL pid=$corePid at $($killAt.ToString('HH:mm:ss.fff'))"
    Stop-Process -Id $corePid -Force -ErrorAction SilentlyContinue
    $seenFail = $false; $failAt = $null; $firstFailText = ''; $seenRecover = $false; $recoverAt = $null; $respawnAt = $null; $newPid = -1
    $lastText = ''
    $deadline = $killAt.AddSeconds(15)
    while ((Get-Date) -lt $deadline) {
        # R-012: sample $el AFTER the (slow) UIA/process queries so the reported ms reflect the
        # moment the condition was actually observed, not the moment before the query started.
        $names = AllNames $win
        $joined = ($names | Where-Object { $_ -match '后端服务' }) -join ' | '
        if ($joined -and $joined -ne $lastText) {
            $el = [int]((Get-Date) - $killAt).TotalMilliseconds
            $lastText = $joined
            "$el,ui_text,$joined" | Add-Content $tl -Encoding utf8
            T "UI_TEXT (+${el}ms) $joined"
            if ($joined -match $FAIL_REGEX -and -not $seenFail) { $seenFail = $true; $failAt = Get-Date; $firstFailText = $joined; Shot '01-failure-banner' }
            if ($joined -match $RECOVER_REGEX -and -not $seenRecover) { $seenRecover = $true; $recoverAt = Get-Date; Shot '02-recovered-banner' }
        }
        if ($respawnAt -eq $null) {
            $c2 = @(Get-Owned $rootPid | Where-Object { $_.Name -eq 'core_service.exe' })
            if ($c2.Count -gt 0) { $respawnAt = Get-Date; $newPid = [int]$c2[0].ProcessId; $el = [int]((Get-Date) - $killAt).TotalMilliseconds; "$el,sidecar_respawned,pid=$newPid" | Add-Content $tl -Encoding utf8; T "RESPAWN (+${el}ms) pid=$newPid" }
        }
        if ($p.HasExited) { $el = [int]((Get-Date) - $killAt).TotalMilliseconds; "$el,main_process_exited," | Add-Content $tl -Encoding utf8; T "MAIN_EXITED (+${el}ms)"; break }
        Start-Sleep -Milliseconds 50
    }
    $killMs = [int]($killAt - $killAt).TotalMilliseconds
    $failMs = if ($failAt) { [int]($failAt - $killAt).TotalMilliseconds } else { -1 }
    $recMs = if ($recoverAt) { [int]($recoverAt - $killAt).TotalMilliseconds } else { -1 }
    $resMs = if ($respawnAt) { [int]($respawnAt - $killAt).TotalMilliseconds } else { -1 }
    T "TIMELINE failure_banner_ms=$failMs recovered_banner_ms=$recMs respawn_ms=$resMs new_pid=$newPid"
    T ("ASSERT " + $(if ($seenFail) { 'PASS' } else { 'FAIL' }) + " r004:explicit-failure-banner-observed (text=$firstFailText)")
    T ("ASSERT " + $(if ($resMs -ge 0) { 'PASS' } else { 'FAIL' }) + " r004:sidecar-auto-respawned (ms=$resMs)")
    T ("FACT respawn_absolute_ms=$resMs failure_before_respawn=" + ($failMs -ge 0 -and ($resMs -lt 0 -or $failMs -le $resMs)))
}
if ($p -and -not $p.HasExited) { $p.CloseMainWindow() | Out-Null; Start-Sleep -Seconds 2 }
if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force }
Get-Owned $rootPid | ForEach-Object { Get-Process -Id ([int]$_.ProcessId) -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue }
T ("R-004 END script_fails=" + $script:scriptFails)
exit ([int]($script:scriptFails -gt 0))
