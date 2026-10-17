param(
  [ValidateSet('before', 'before-retry', 'before-confirm', 'after')]
  [string]$Stage = 'before',
  [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$outDir = Join-Path $PSScriptRoot $Stage
New-Item -ItemType Directory -Path $outDir -Force | Out-Null
$isoRoot = Join-Path $RepoRoot 'apps/desktop/src-tauri/target/p19-ui-fix-2-isolation-20261017'
$exe = Join-Path $RepoRoot 'apps/desktop/src-tauri/target/debug/m2rc1-desktop.exe'
$exeDir = Split-Path $exe
$trace = Join-Path $outDir 'uia-run.log'
$windowTitle = 'M2-RC1 resource channel runtime'
$AE = [System.Windows.Automation.AutomationElement]
$TS = [System.Windows.Automation.TreeScope]
$CT = [System.Windows.Automation.ControlType]
$ANY = [System.Windows.Automation.Condition]::TrueCondition
$Invoke = [System.Windows.Automation.InvokePattern]::Pattern

foreach ($name in @('uia-run.log', 'import-open.uia.txt', 'app-out.log', 'app-err.log')) {
  if (Test-Path -LiteralPath (Join-Path $outDir $name)) { throw "refusing to overwrite existing evidence: $Stage/$name" }
}

function Write-Trace([string]$message) {
  $line = "[$(Get-Date -Format 'HH:mm:ss.fff')] $message"
  Add-Content -LiteralPath $trace -Value $line -Encoding utf8
  Write-Output $line
}

function Get-AppWindow([int]$processId) {
  $windows = $AE::RootElement.FindAll($TS::Children, $ANY)
  for ($i = 0; $i -lt $windows.Count; $i += 1) {
    $window = $windows.Item($i)
    if ($window.Current.ProcessId -eq $processId -and $window.Current.Name -eq $windowTitle) { return $window }
  }
  return $null
}

function Find-Button([System.Windows.Automation.AutomationElement]$window, [string]$namePart) {
  $buttons = $window.FindAll($TS::Descendants, (New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty, $CT::Button)))
  for ($i = 0; $i -lt $buttons.Count; $i += 1) {
    $button = $buttons.Item($i)
    if ($button.Current.Name.Contains($namePart)) { return $button }
  }
  return $null
}

$process = $null
$failed = $false
try {
  if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw "application executable missing: $exe" }
  foreach ($dir in @('profile', 'local', 'tmp', 'derived', 'managed', 'webview')) {
    if (-not (Test-Path -LiteralPath (Join-Path $isoRoot $dir) -PathType Container)) { throw "isolated directory missing: $dir" }
  }

  $env:APPDATA = Join-Path $isoRoot 'profile'
  $env:LOCALAPPDATA = Join-Path $isoRoot 'local'
  $env:TEMP = Join-Path $isoRoot 'tmp'
  $env:TMP = $env:TEMP
  $env:NEWMANGA_DATA_ROOT = Join-Path $isoRoot 'data'
  $env:M2RC1_DERIVED_ROOT = Join-Path $isoRoot 'derived'
  $env:M2RC1_MANAGED_ROOT = Join-Path $isoRoot 'managed'
  $env:M2RC2_CATALOG_DB = Join-Path $isoRoot 'catalog/catalog.sqlite'
  $env:WEBVIEW2_USER_DATA_FOLDER = Join-Path $isoRoot 'webview'

  $exeHash = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant()
  Write-Trace "RUN stage=$Stage exe_sha256=$exeHash data_root=isolated"
  $process = Start-Process -FilePath $exe -WorkingDirectory $exeDir -PassThru `
    -RedirectStandardOutput (Join-Path $outDir 'app-out.log') `
    -RedirectStandardError (Join-Path $outDir 'app-err.log')
  Write-Trace "pid=$($process.Id)"

  $deadline = (Get-Date).AddSeconds(75)
  $window = $null
  while ((Get-Date) -lt $deadline) {
    $process.Refresh()
    if ($process.HasExited) { throw "application exited before UIA ready: exit=$($process.ExitCode)" }
    $window = Get-AppWindow $process.Id
    if ($window) { break }
    Start-Sleep -Milliseconds 500
  }
  if (-not $window) { throw 'application window not found before timeout' }
  $topLevel = $AE::RootElement.FindAll($TS::Children, $ANY)
  Write-Trace "WINDOW title=$($window.Current.Name) bounds=$($window.Current.BoundingRectangle) top_level_count=$($topLevel.Count)"
  Start-Sleep -Seconds 4

  $initialElements = $window.FindAll($TS::Descendants, $ANY)
  foreach ($element in $initialElements) {
    $name = $element.Current.Name
    $controlType = $element.Current.ControlType.ProgrammaticName -replace 'ControlType\.', ''
    if ($controlType -eq 'Button' -or $name -match '书架|导入|作品') {
      Write-Trace "INITIAL_ELEMENT $controlType|$name|IsEnabled=$($element.Current.IsEnabled)|IsOffscreen=$($element.Current.IsOffscreen)"
    }
  }

  $importButton = $null
  $buttonDeadline = (Get-Date).AddSeconds(30)
  while ((Get-Date) -lt $buttonDeadline -and -not $importButton) {
    $window = Get-AppWindow $process.Id
    if ($window) { $importButton = Find-Button $window '导入作品' }
    if (-not $importButton) { Start-Sleep -Milliseconds 300 }
  }
  if (-not $importButton) { throw 'top-bar 导入作品 button not found' }
  Write-Trace "TOPBAR_IMPORT IsEnabled=$($importButton.Current.IsEnabled) IsOffscreen=$($importButton.Current.IsOffscreen)"
  if (-not $importButton.Current.IsEnabled -or $importButton.Current.IsOffscreen) { throw 'top-bar import button is disabled or offscreen' }
  $importButton.GetCurrentPattern($Invoke).Invoke()
  Start-Sleep -Milliseconds 900

  $window = Get-AppWindow $process.Id
  $names = [System.Collections.Generic.List[string]]::new()
  $elements = $window.FindAll($TS::Descendants, $ANY)
  foreach ($element in $elements) {
    $name = $element.Current.Name
    if ($name -match '导入页面到章节|未开放|选择图片|选择文件夹|目标章节') {
      $controlType = $element.Current.ControlType.ProgrammaticName -replace 'ControlType\.', ''
      $names.Add("$controlType|$name|IsEnabled=$($element.Current.IsEnabled)|IsOffscreen=$($element.Current.IsOffscreen)")
    }
  }
  if ($names.Count -eq 0) { throw 'top-bar click produced no visible UIA import dialog or feedback' }
  $names | Set-Content -LiteralPath (Join-Path $outDir 'import-open.uia.txt') -Encoding utf8
  Write-Trace "IMPORT_UIA_FEEDBACK=PASS elements=$($names.Count)"
  foreach ($line in $names) { Write-Trace "IMPORT_ELEMENT $line" }
  $notice = $names | Where-Object { $_ -match '\|未开放：' -and $_ -match 'IsOffscreen=False' } | Select-Object -First 1
  if ($notice) {
    if (-not $notice.Contains('IsEnabled=True')) { throw 'unavailable notice is not enabled in UIA' }
    $filePicker = $names | Where-Object { $_ -match '选择图片 / PDF 文件' } | Select-Object -First 1
    $folderPicker = $names | Where-Object { $_ -match '选择图片文件夹' } | Select-Object -First 1
    if (-not $filePicker -or -not $folderPicker -or $filePicker -notmatch 'IsEnabled=False' -or $folderPicker -notmatch 'IsEnabled=False') { throw 'no-target picker buttons are not both disabled and visible' }
    Write-Trace 'UNAVAILABLE_ASSERTION=PASS visible_notice=true file_disabled=true folder_disabled=true'
  }
} catch {
  $failed = $true
  Write-Trace "FATAL $($_.Exception.Message)"
} finally {
  if ($process) {
    $process.Refresh()
    if (-not $process.HasExited) {
      $null = $process.CloseMainWindow()
      if (-not $process.WaitForExit(12000)) { Stop-Process -Id $process.Id -Force; $process.WaitForExit() }
    }
    $process.Refresh()
    if ($process.HasExited) {
      $null = $process.WaitForExit()
      $process.Refresh()
      $processExitCode = $process.ExitCode
      Write-Trace "APP_EXIT has_exited=true exit_code=$processExitCode"
      if ($processExitCode -ne 0) { $failed = $true }
    } else {
      Write-Trace 'APP_EXIT has_exited=false exit_code=NOT_AVAILABLE'
      $failed = $true
    }
  }
}

if ($failed) { Write-Trace 'exit_code=1'; exit 1 }
Write-Trace 'exit_code=0'
exit 0
