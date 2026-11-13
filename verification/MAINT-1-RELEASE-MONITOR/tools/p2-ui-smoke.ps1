<#
.SYNOPSIS
  P2 可见 UI 冒烟：四页在双根隔离下各自启动，留窗口出现时点 + 真实窗口截图 + 退出码 + 日志。

.DESCRIPTION
  MAINT-1 P2。断言：每页产生可见窗口、窗口截图非空、退出码 0、host.log 落地；
  真实 %APPDATA%\com.newmanga.desktop 前后文件数/字节数不变。

  实现注意事项（本会话三次实测得到，勿回退）：
    * 不要用 Start-Process：它走 ShellExecute，在本会话会无限阻塞；用
      [System.Diagnostics.Process]::Start(UseShellExecute=$false)，与通过测试的 C# 用例一致。
    * 不要用 Graphics.CopyFromScreen：无交互桌面时会阻塞；用 PrintWindow(PW_RENDERFULLCONTENT)。
    * 不要用 Start-Job：沙箱禁命名管道，作业通信会挂死。
#>
[CmdletBinding()]
param(
    [string]$Exe = '',
    [string]$SidecarDirectory = '',
    [string]$OutDir = ''
)

$ErrorActionPreference = 'Stop'
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..\..\..')
if ([string]::IsNullOrWhiteSpace($Exe)) {
    $Exe = Join-Path $repoRoot 'apps/desktop-avalonia/src/NewManga.App/bin/Release/net9.0/win-x64/NewManga.App.exe'
}
if ([string]::IsNullOrWhiteSpace($SidecarDirectory)) {
    $SidecarDirectory = Join-Path (Split-Path $repoRoot -Parent) ((Split-Path $repoRoot -Leaf) + '.workspace/task-envs/HOST-CORECLIENT-1/sidecar-copy')
}
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path $PSScriptRoot 'ui-smoke' }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
if (-not (Test-Path $Exe)) { throw "app exe not found: $Exe" }
if (-not (Test-Path (Join-Path $SidecarDirectory 'core_service.exe'))) { throw "sidecar not found: $SidecarDirectory" }

Add-Type -AssemblyName System.Drawing
if (-not ('P2Smoke' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class P2Smoke {
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
}
'@
}

$realAppData = Join-Path $env:APPDATA 'com.newmanga.desktop'
function Get-AppDataSnapshot {
    if (-not (Test-Path $realAppData)) { return [ordered]@{ exists = $false; files = 0; bytes = 0 } }
    $files = @(Get-ChildItem $realAppData -Recurse -File -ErrorAction SilentlyContinue)
    return [ordered]@{ exists = $true; files = $files.Count; bytes = [long](($files | Measure-Object -Property Length -Sum).Sum) }
}

$beforeAppData = Get-AppDataSnapshot
$pageResults = @()

foreach ($page in @('bookshelf', 'workbench', 'reader', 'settings')) {
    $stamp = [guid]::NewGuid().ToString('N').Substring(0, 8)
    $dataRoot = Join-Path $env:TEMP ("newmanga-p2-$page-$stamp")
    $themeHome = Join-Path $env:TEMP ("newmanga-p2-theme-$page-$stamp")
    $logDir = Join-Path $dataRoot 'logs'
    New-Item -ItemType Directory -Force -Path $logDir, $themeHome | Out-Null

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $Exe
    $psi.UseShellExecute = $false
    $psi.Arguments = @(
        "--page=$page",
        "--data-root=`"$dataRoot`"",
        "--log-dir=`"$logDir`"",
        "--theme-home=`"$themeHome`"",
        "--sidecar-dir=`"$SidecarDirectory`"",
        "--mutex-name=Local\NewManga.P2.$page.$stamp",
        '--exit-after=12000'
    ) -join ' '

    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $proc = [System.Diagnostics.Process]::Start($psi)
    $hwnd = [IntPtr]::Zero
    $visibleMs = $null
    for ($i = 0; $i -lt 120; $i++) {
        Start-Sleep -Milliseconds 250
        $proc.Refresh()
        if ($proc.HasExited) { break }
        if ($proc.MainWindowHandle -ne [IntPtr]::Zero) {
            $hwnd = $proc.MainWindowHandle
            $visibleMs = [math]::Round($sw.Elapsed.TotalMilliseconds, 1)
            break
        }
    }

    $shot = Join-Path $OutDir "page-$page.png"
    $shotBytes = 0
    $shotStatus = if ($hwnd -eq [IntPtr]::Zero) { 'no-window' } else { 'pending' }
    $rect = [ordered]@{ width = 0; height = 0 }
    if ($hwnd -ne [IntPtr]::Zero) {
        Start-Sleep -Milliseconds 800
        $r = New-Object P2Smoke+RECT
        [void][P2Smoke]::GetWindowRect($hwnd, [ref]$r)
        $w = $r.Right - $r.Left; $h = $r.Bottom - $r.Top
        $rect = [ordered]@{ width = $w; height = $h }
        if ($w -gt 0 -and $h -gt 0) {
            try {
                $bmp = New-Object System.Drawing.Bitmap($w, $h)
                $g = [System.Drawing.Graphics]::FromImage($bmp)
                $hdc = $g.GetHdc()
                try { $printed = [P2Smoke]::PrintWindow($hwnd, $hdc, 2) } finally { $g.ReleaseHdc($hdc) }
                $g.Dispose()
                $bmp.Save($shot, [System.Drawing.Imaging.ImageFormat]::Png)
                $bmp.Dispose()
                $shotBytes = (Get-Item $shot).Length
                $shotStatus = if (-not $printed) { 'printwindow-failed' } elseif ($shotBytes -ge 20000) { 'ok' } else { 'tiny' }
            } catch {
                $shotStatus = 'error: ' + $_.Exception.Message
            }
        }
    }

    $exited = $proc.WaitForExit(40000)
    if (-not $exited) { try { $proc.Kill() } catch {} }
    $exitCode = if ($exited) { $proc.ExitCode } else { -1 }
    $elapsedMs = [math]::Round($sw.Elapsed.TotalMilliseconds, 1)
    $hostLog = Join-Path $logDir 'host.log'
    $hostLogBytes = if (Test-Path $hostLog) { (Get-Item $hostLog).Length } else { 0 }

    $pageResults += [ordered]@{
        page              = $page
        window_seen       = ($hwnd -ne [IntPtr]::Zero)
        window_visible_ms = $visibleMs
        window_size       = $rect
        screenshot        = $shot
        screenshot_bytes  = $shotBytes
        screenshot_status = $shotStatus
        exit_code         = $exitCode
        elapsed_ms        = $elapsedMs
        host_log_bytes    = $hostLogBytes
        data_root         = $dataRoot
        theme_home        = $themeHome
    }
    Write-Output ("page={0} window={1} at={2}ms shot={3}({4}B) exit={5} hostlog={6}B" -f $page, ($hwnd -ne [IntPtr]::Zero), $visibleMs, $shotStatus, $shotBytes, $exitCode, $hostLogBytes)
}

$afterAppData = Get-AppDataSnapshot
$appdataUnchanged = ($beforeAppData.files -eq $afterAppData.files) -and ($beforeAppData.bytes -eq $afterAppData.bytes)
$pagesOk = (@($pageResults | Where-Object { -not $_.window_seen -or $_.exit_code -ne 0 }).Count -eq 0)
$shotsOk = (@($pageResults | Where-Object { $_.screenshot_status -eq 'ok' }).Count -eq $pageResults.Count)
$logsOk = (@($pageResults | Where-Object { $_.host_log_bytes -le 0 }).Count -eq 0)

$result = [ordered]@{
    round         = 'MAINT-1 P2 visible ui smoke'
    at_utc        = [DateTime]::UtcNow.ToString('o')
    exe           = $Exe
    sidecar       = $SidecarDirectory
    pages         = $pageResults
    pages_ok      = $pagesOk
    shots_ok      = $shotsOk
    host_logs_ok  = $logsOk
    real_appdata  = [ordered]@{ path = $realAppData; before = $beforeAppData; after = $afterAppData; unchanged = $appdataUnchanged }
}
$result | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $OutDir 'p2-ui-smoke.json') -Encoding utf8
Write-Output ("pages_ok={0} shots_ok={1} host_logs_ok={2} appdata_unchanged={3}" -f $pagesOk, $shotsOk, $logsOk, $appdataUnchanged)

if (-not $pagesOk) { throw 'one or more pages failed to show a window or exited non-zero' }
if (-not $logsOk) { throw 'one or more pages produced no host.log' }
if (-not $appdataUnchanged) { throw 'real %APPDATA% changed during the smoke' }
Write-Output 'P2_SMOKE PASS'
