# P20 AC5: graceful degradation without a GPU / without CUDA.
# This host HAS an RTX 5070 Ti, so the no-GPU condition is simulated by disabling CUDA visibility
# (CUDA_VISIBLE_DEVICES=-1) and forcing WebView2 into software rendering (--disable-gpu).
# AC5 requires: the app still starts, basic functions work, and it must NOT fail to start due to a
# missing GPU driver.
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
$CT = [System.Windows.Automation.ControlType]
if (-not $OutDir) { $OutDir = Join-Path $RepoRoot ('verification\P20\ac5-' + (Get-Date -Format 'yyyyMMdd-HHmmss')) }
if (Test-Path $OutDir) { Write-Host "REFUSE_OVERWRITE $OutDir"; exit 4 }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$trace = Join-Path $OutDir 'ac5-trace.log'
$checks = 0; $fails = 0
function T([string]$m) { $l = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss.fff'), $m; $l | Add-Content $trace -Encoding utf8; Write-Host $l }
function A([bool]$c, [string]$name) { $script:checks++; if (-not $c) { $script:fails++ }; T ("ASSERT {0} {1}" -f $(if ($c) { 'PASS' } else { 'FAIL' }), $name) }
function Shot([string]$tag) {
    $b = Join-Path $OutDir "$tag.png"; $w = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bmp = New-Object System.Drawing.Bitmap($w.Width, $w.Height); $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($w.Location, [System.Drawing.Point]::Empty, $w.Size); $bmp.Save($b, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose(); if (Test-Path $b) { T "SHOT $tag OK" }
}
function Win() {
    try {
        $r = [System.Windows.Automation.AutomationElement]::RootElement
        $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, 'M2-RC1 resource channel runtime')
        return $r.FindFirst($TS::Children, $c)
    } catch { return $null }
}
function Names($w) { if (-not $w) { return @() }; return @($w.FindAll($TS::Descendants, [System.Windows.Automation.Condition]::TrueCondition) | ForEach-Object { try { $_.Current.Name } catch {} } | Where-Object { $_ }) }
function F($w, $n, $ct) { if (-not $w) { return $null }; $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $n); $c2 = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, $ct); $and = New-Object System.Windows.Automation.AndCondition($c, $c2); return $w.FindFirst($TS::Descendants, $and) }

$exe = Join-Path $RepoRoot 'apps\desktop\src-tauri\target\debug\m2rc1-desktop.exe'
$iso = Join-Path $env:TEMP ('p20ac5-' + [guid]::NewGuid().ToString('N').Substring(0,8))
New-Item -ItemType Directory -Force -Path $iso | Out-Null
# simulate no CUDA + software-only WebView2
$env:NEWMANGA_DATA_ROOT = $iso
$env:CUDA_VISIBLE_DEVICES = '-1'
$env:NVIDIA_VISIBLE_DEVICES = 'none'
$env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS = '--disable-gpu --disable-gpu-compositing --disable-software-rasterizer=false'
$env:LIBGL_ALWAYS_SOFTWARE = '1'
T "AC5 start simulated_no_gpu=1 iso=$iso"
T "ENV CUDA_VISIBLE_DEVICES=-1 NVIDIA_VISIBLE_DEVICES=none WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS='--disable-gpu --disable-gpu-compositing'"
$errLog = Join-Path $OutDir 'app-err.log'; $outLog = Join-Path $OutDir 'app-out.log'
$p = Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -PassThru -RedirectStandardError $errLog -RedirectStandardOutput $outLog
$win = $null; $dl = (Get-Date).AddSeconds(40)
while ((Get-Date) -lt $dl) {
    Start-Sleep -Milliseconds 500
    if ($p.HasExited) { break }
    $win = Win; if ($win) { break }
}
T "window_found=$([bool]$win) exited=$($p.HasExited) exit=$($p.ExitCode)"
A ([bool]$win) 'ac5:starts-without-gpu'
# The native window appears well before the frontend finishes rendering; wait for the shell nav to
# actually materialise (bounded) instead of probing immediately.
if ($win) {
    $navDeadline = (Get-Date).AddSeconds(25)
    while ((Get-Date) -lt $navDeadline) {
        $probe = F $win '📚 书架' $CT::Button
        if ($probe) { break }
        Start-Sleep -Milliseconds 500
    }
    $navReady = [bool](F $win '📚 书架' $CT::Button)
    T "nav_ready=$navReady (waited up to 25s for frontend render)"
    A $navReady 'ac5:frontend-shell-rendered'
}
if ($win) {
    Shot '01-started-no-gpu'
    foreach ($pg in @('📚 书架','🛠️ 工作台','📖 阅读器','⚙️ 设置')) {
        $b = F $win $pg $CT::Button
        if (-not $b) { T "PAGE '$pg' NOT_FOUND"; A $false "ac5:page:$pg"; continue }
        try { $b.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); Start-Sleep -Milliseconds 1000; T "PAGE '$pg' reached"; A $true "ac5:page:$pg" }
        catch { T "PAGE '$pg' FAILED $($_.Exception.Message)"; A $false "ac5:page:$pg" }
    }
    # basic function: return to the shelf first (the create button lives there), then open the
    # create-book dialog and cancel it - proves the UI is genuinely interactive without a GPU.
    $shelf = F $win '📚 书架' $CT::Button
    if ($shelf) { $shelf.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); Start-Sleep -Milliseconds 1200 }
    $cr = F $win '＋ 新建作品' $CT::Button; if (-not $cr) { $cr = F $win '+ 新建作品' $CT::Button }
    if ($cr -and $cr.Current.IsEnabled) {
        try {
            $cr.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); Start-Sleep -Milliseconds 1200
            $names = Names $win
            $dlg = @($names | Where-Object { $_ -match '作品标题|创建作品' })
            T ("create_dialog_markers=" + ($dlg -join ' ; '))
            A ($dlg.Count -gt 0) 'ac5:basic-function-create-dialog'
            $cancel = F $win '取消' $CT::Button
            if ($cancel) { $cancel.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); Start-Sleep -Milliseconds 800 }
            Shot '02-create-dialog'
        } catch { T "CREATE_DIALOG_FAILED $($_.Exception.Message)"; A $false 'ac5:basic-function-create-dialog' }
    } else { T 'CREATE_BUTTON unavailable'; A $false 'ac5:basic-function-create-dialog' }
    # no crash after interaction
    Start-Sleep -Seconds 3
    A (-not $p.HasExited) 'ac5:no-crash-after-interaction'
}
if ($p -and -not $p.HasExited) { $p.CloseMainWindow() | Out-Null; Start-Sleep -Seconds 2 }
if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force }
Get-Process core_service,host_bridge -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
if (Test-Path $errLog) { T ("app_err_tail=" + ((Get-Content $errLog -Tail 4) -join ' / ')) }
@(
    "runner=run-ac5-no-gpu.ps1"
    "simulated=CUDA_VISIBLE_DEVICES=-1;NVIDIA_VISIBLE_DEVICES=none;WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS=--disable-gpu"
    "checks=$checks"; "fails=$fails"; "exit_code=$([int]($fails -gt 0))"
) | Set-Content (Join-Path $OutDir 'ac5-metadata.txt') -Encoding utf8
T ("AC5 END checks=$checks fails=$fails")
exit ([int]($fails -gt 0))
