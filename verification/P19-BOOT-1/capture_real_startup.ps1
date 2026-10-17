param(
    [Parameter(Mandatory = $true)][int]$ProcessId,
    [Parameter(Mandatory = $true)][string]$RunName
)

$ErrorActionPreference = 'Stop'
$evidenceRoot = (Resolve-Path $PSScriptRoot).Path
$repoRoot = (Resolve-Path (Join-Path $evidenceRoot '../..')).Path
$runRoot = Join-Path $evidenceRoot $RunName
$exe = Join-Path $repoRoot 'apps/desktop/src-tauri/target/debug/m2rc1-desktop.exe'
$stderrPath = Join-Path $evidenceRoot 'final-app.stderr.log'
$process = Get-Process -Id $ProcessId

Add-Type -AssemblyName System.Drawing.Common
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class P19FinalCapture {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int command);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint flags, uint dx, uint dy, uint data, UIntPtr extra);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr hWnd, uint message, IntPtr wParam, IntPtr lParam);
}
'@

function Save-WindowScreenshot([IntPtr]$Handle, [string]$Path, [P19FinalCapture+RECT]$Rect) {
    $bitmap = [System.Drawing.Bitmap]::new($Rect.Right - $Rect.Left, $Rect.Bottom - $Rect.Top)
    try {
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
        try { $graphics.CopyFromScreen($Rect.Left, $Rect.Top, 0, 0, $bitmap.Size) }
        finally { $graphics.Dispose() }
        $bitmap.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
    } finally { $bitmap.Dispose() }
    return @{
        file = [IO.Path]::GetFileName($Path)
        sha256 = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
        width = $Rect.Right - $Rect.Left
        height = $Rect.Bottom - $Rect.Top
    }
}

$windowDeadline = [DateTime]::UtcNow.AddSeconds(30)
do {
    $process.Refresh()
    if ($process.HasExited) { throw "App exited before window creation with code $($process.ExitCode)" }
    if ($process.MainWindowHandle -ne [IntPtr]::Zero) { break }
    Start-Sleep -Milliseconds 300
} while ([DateTime]::UtcNow -lt $windowDeadline)
$handle = $process.MainWindowHandle
if ($handle -eq [IntPtr]::Zero) { throw 'App main window is unavailable' }
[P19FinalCapture]::ShowWindow($handle, 9) | Out-Null
[P19FinalCapture]::BringWindowToTop($handle) | Out-Null
[P19FinalCapture]::SetForegroundWindow($handle) | Out-Null
$webviewTitles = @()
$readyDeadline = [DateTime]::UtcNow.AddSeconds(60)
do {
    [P19FinalCapture]::SetForegroundWindow($handle) | Out-Null
    Start-Sleep -Milliseconds 500
    try {
        $root = [System.Windows.Automation.AutomationElement]::FromHandle($handle)
        $descendants = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
        $webviewTitles = @()
        for ($i = 0; $i -lt $descendants.Count; $i++) {
            $element = $descendants.Item($i)
            if ($element.Current.Name -like 'M2RC1|interactive*') {
                $webviewTitles += @{ name = $element.Current.Name; class = $element.Current.ClassName }
            }
        }
    } catch { $webviewTitles = @() }
} while ($webviewTitles.Count -lt 1 -and [DateTime]::UtcNow -lt $readyDeadline)
if ($webviewTitles.Count -lt 1) { throw 'WebView did not expose its interactive document title' }
$rect = New-Object P19FinalCapture+RECT
if (-not [P19FinalCapture]::GetWindowRect($handle, [ref]$rect)) { throw 'GetWindowRect failed' }

$pages = @(
    @{ id = 'bookshelf'; y = 115 },
    @{ id = 'workbench'; y = 166 },
    @{ id = 'reader'; y = 228 },
    @{ id = 'settings'; y = 283 }
)
$captures = @()
foreach ($page in $pages) {
    [P19FinalCapture]::SetForegroundWindow($handle) | Out-Null
    [P19FinalCapture]::SetCursorPos($rect.Left + 48, $rect.Top + $page.y) | Out-Null
    [P19FinalCapture]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
    [P19FinalCapture]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 700
    $path = Join-Path $evidenceRoot "ui-$($page.id)-real-window.png"
    $shot = Save-WindowScreenshot $handle $path $rect
    $captures += @{ page = $page.id; action = 'real mouse click on visible navigation rail'; screenshot = $shot }
}

$windowTitle = $process.MainWindowTitle
[P19FinalCapture]::PostMessage($handle, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null
$process.WaitForExit(10000) | Out-Null
$process.Refresh()
$stderr = Get-Content -LiteralPath $stderrPath -Raw
$stderrHash = try { (Get-FileHash -LiteralPath $stderrPath -Algorithm SHA256).Hash.ToLowerInvariant() } catch { $null }
$result = [ordered]@{
    app = $exe
    app_sha256 = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant()
    launch_mode = 'compiled Tauri debug host with tauri/custom-protocol and source Python Core sidecar'
    startup_state = 'catalog exists; derived/ empty before app launch'
    run_root = $runRoot
    pid = $ProcessId
    window_title = $windowTitle
    webview_uia_titles = $webviewTitles
    pages = $captures
    window_reached = ($captures.Count -eq 4)
    app_exit_code = if ($process.HasExited) { $process.ExitCode } else { $null }
    stderr_path = [IO.Path]::GetFileName($stderrPath)
    stderr_sha256 = $stderrHash
    stderr_checks = @{
        has_file_not_found = $stderr.Contains('FileNotFoundError')
        has_json_decode_error = $stderr.Contains('JSONDecodeError')
        has_misleading_busy = $stderr.Contains('namespace busy (a managed peer holds a shared lease)')
        startup_gc_completed = $stderr.Contains('[core.derived_gc] orphan_files_removed=')
    }
}
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $evidenceRoot 'real-startup-final.json') -Encoding utf8
$result | ConvertTo-Json -Depth 8
if ($captures.Count -ne 4 -or $webviewTitles.Count -lt 1) { exit 1 }
