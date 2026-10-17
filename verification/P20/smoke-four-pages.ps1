# P20 AC7 smoke supplement: launch the built product in THIS interactive session and assert
# the four primary pages are reachable. Antigravity's sandbox session cannot create the WebView2
# window (HRESULT 0x80070578), so this half of AC7 must run here.
param(
    [string]$RepoRoot = 'G:\CODEX\New Manga',
    [string]$OutDir = ''
)
$ErrorActionPreference = 'Continue'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$CT = [System.Windows.Automation.ControlType]
$TS = [System.Windows.Automation.TreeScope]
$AE = [System.Windows.Automation.AutomationElement]

if (-not $OutDir) { $OutDir = Join-Path $RepoRoot ('verification\P20\smoke-' + (Get-Date -Format 'yyyyMMdd-HHmmss')) }
if (Test-Path $OutDir) { Write-Host "REFUSE_OVERWRITE $OutDir"; exit 4 }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$trace = Join-Path $OutDir 'smoke-trace.log'
$checks = 0; $fails = 0
function T([string]$m) { $line = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss.fff'), $m; $line | Add-Content -Path $trace -Encoding utf8; Write-Host $line }
function A([bool]$c, [string]$name) { $script:checks++; if (-not $c) { $script:fails++ }; T ("ASSERT {0} {1}" -f $(if($c){'PASS'}else{'FAIL'}), $name) }
function Shot([string]$tag) { $b = Join-Path $OutDir "$tag.png"; Add-Type -AssemblyName System.Drawing
  $w = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
  $bmp = New-Object System.Drawing.Bitmap($w.Width, $w.Height)
  $g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($w.Location, [System.Drawing.Point]::Empty, $w.Size)
  $bmp.Save($b, [System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose()
  if (Test-Path $b) { T "SHOT $tag OK" } }

$iso = Join-Path $env:TEMP ('p19-smoke-' + [guid]::NewGuid().ToString('N').Substring(0,8))
New-Item -ItemType Directory -Force -Path $iso | Out-Null
$env:NEWMANGA_DATA_ROOT = $iso
$exe = Join-Path $RepoRoot 'apps\desktop\src-tauri\target\debug\m2rc1-desktop.exe'
T "SMOKE start exe=$exe iso=$iso"
T ("EXE_SHA256=" + (Get-FileHash $exe -Algorithm SHA256).Hash.ToLower())
$errLog = Join-Path $OutDir 'smoke-err.log'; $outLog = Join-Path $OutDir 'smoke-out.log'
$p = Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -PassThru -RedirectStandardError $errLog -RedirectStandardOutput $outLog
$win = $null
$dl = (Get-Date).AddSeconds(40)
while ((Get-Date) -lt $dl) {
  Start-Sleep -Milliseconds 700
  if ($p.HasExited) { T "SMOKE early exit=$($p.ExitCode)"; break }
  try {
    $root = [System.Windows.Automation.AutomationElement]::RootElement
    $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, 'M2-RC1 resource channel runtime')
    $h = $root.FindFirst($TS::Children, $c)
    if ($h) { $win = $h; break }
  } catch {}
}
T "SMOKE window_found=$([bool]$win) pid=$($p.Id) exited=$($p.HasExited)"
A ([bool]$win) 'smoke:window-present'
if ($win) {
  Shot '00-launched'
  foreach ($pg in @('📚 书架','🛠️ 工作台','📖 阅读器','⚙️ 设置')) {
    $pc = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $pg)
    $btn = $win.FindFirst($TS::Descendants, $pc)
    if (-not $btn) { T "SMOKE_PAGE '$pg' NOT_FOUND"; A $false "smoke:page:$pg"; continue }
    try {
      $btn.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
      Start-Sleep -Milliseconds 1100
      T "SMOKE_PAGE '$pg' reached"
      A $true "smoke:page:$pg"
    } catch { T "SMOKE_PAGE '$pg' FAILED $($_.Exception.Message)"; A $false "smoke:page:$pg" }
  }
  Shot '01-four-pages'
}
if ($p -and -not $p.HasExited) { $p.CloseMainWindow() | Out-Null; Start-Sleep -Seconds 2 }
if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force }
T ("END checks={0} fails={1}" -f $checks, $fails)
@(
  "runner=smoke-four-pages.ps1"
  "exe=$exe"
  "exe_sha256=$((Get-FileHash $exe -Algorithm SHA256).Hash.ToLower())"
  "iso=$iso"
  "checks=$checks"
  "fails=$fails"
  "exit_code=$([int]($fails -gt 0))"
) | Set-Content (Join-Path $OutDir 'smoke-metadata.txt') -Encoding utf8
exit ([int]($fails -gt 0))
