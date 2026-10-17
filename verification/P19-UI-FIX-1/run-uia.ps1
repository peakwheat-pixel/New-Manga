param(
  [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$outDir = $PSScriptRoot
$isoRoot = Join-Path $RepoRoot 'apps/desktop/src-tauri/target/p19-ui-fix-1-isolation-20261017'
$exe = Join-Path $RepoRoot 'apps/desktop/src-tauri/target/debug/m2rc1-desktop.exe'
$exeDir = Split-Path $exe
$trace = Join-Path $outDir 'uia-run.log'
$windowTitle = 'M2-RC1 resource channel runtime'
$AE = [System.Windows.Automation.AutomationElement]
$TS = [System.Windows.Automation.TreeScope]
$CT = [System.Windows.Automation.ControlType]
$ANY = [System.Windows.Automation.Condition]::TrueCondition
$Invoke = [System.Windows.Automation.InvokePattern]::Pattern

foreach ($name in @('uia-run.log', '04-settings.uia.txt', 'import-open.uia.txt', 'app-out.log', 'app-err.log')) {
  if (Test-Path -LiteralPath (Join-Path $outDir $name)) { throw "refusing to overwrite existing evidence: $name" }
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
    if ($window.Current.ProcessId -eq $processId -and $window.Current.Name -eq $windowTitle) {
      return $window
    }
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

function Invoke-Button([System.Windows.Automation.AutomationElement]$button) {
  $button.GetCurrentPattern($Invoke).Invoke()
}

$process = $null
$failed = $false
try {
  if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw "application executable missing: $exe" }
  foreach ($dir in @('profile', 'local', 'tmp', 'derived', 'managed')) {
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

  $exeHash = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLower()
  Write-Trace "RUN start exe_sha256=$exeHash data_root=isolated"
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
  Write-Trace 'READY'
  Start-Sleep -Seconds 4

  $settingsNav = Find-Button $window '设置'
  if (-not $settingsNav) { throw 'settings navigation button not found' }
  Invoke-Button $settingsNav
  Start-Sleep -Milliseconds 900

  $closedCategories = @('OCR', '图片修复', '排版样式', '模型/GPU', '任务/并发', '缓存/Revision', '回收站', '备份/恢复', 'Plugin/Hooks')
  $settingsLines = [System.Collections.Generic.List[string]]::new()
  $settingsLines.Add("# 04-settings $(Get-Date -Format o) count=$($closedCategories.Count)")
  foreach ($category in $closedCategories) {
    $button = Find-Button $window $category
    if (-not $button) { throw "disabled settings category not found: $category" }
    $name = $button.Current.Name
    $enabled = $button.Current.IsEnabled
    $offscreen = $button.Current.IsOffscreen
    $invokeResult = 'blocked'
    $invokeDetail = 'InvokePattern unavailable'
    try {
      $button.GetCurrentPattern($Invoke).Invoke()
      $invokeResult = 'UNEXPECTED_SUCCESS'
      $invokeDetail = 'InvokePattern succeeded'
    } catch {
      $invokeDetail = $_.Exception.GetType().Name
    }
    $settingsLines.Add("Button|$name|IsEnabled=$enabled|IsOffscreen=$offscreen|Invoke=$invokeResult|detail=$invokeDetail")
    Write-Trace "SETTINGS category=$category IsEnabled=$enabled IsOffscreen=$offscreen Invoke=$invokeResult detail=$invokeDetail"
    if ($enabled -or $offscreen -or $invokeResult -eq 'UNEXPECTED_SUCCESS' -or -not $name.Contains('未开放')) {
      throw "settings category accessibility assertion failed: $category"
    }
  }
  $settingsLines | Set-Content -LiteralPath (Join-Path $outDir '04-settings.uia.txt') -Encoding utf8
  Write-Trace 'SETTINGS_ASSERTIONS=9/9 PASS'

  $bookshelfNav = Find-Button $window '书架'
  if (-not $bookshelfNav) { throw 'bookshelf navigation button not found' }
  Invoke-Button $bookshelfNav
  Start-Sleep -Milliseconds 700
  $importButton = Find-Button $window '导入作品'
  if (-not $importButton) { throw '导入作品 button not found' }
  Invoke-Button $importButton
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
  if ($names.Count -eq 0) { throw 'clicking 导入作品 produced no visible UIA import feedback' }
  $names | Set-Content -LiteralPath (Join-Path $outDir 'import-open.uia.txt') -Encoding utf8
  Write-Trace "IMPORT_UIA_FEEDBACK=PASS elements=$($names.Count)"
  foreach ($line in $names) { Write-Trace "IMPORT_ELEMENT $line" }
} catch {
  $failed = $true
  Write-Trace "FATAL $($_.Exception.Message)"
} finally {
  if ($process) {
    $process.Refresh()
    if (-not $process.HasExited) {
      $null = $process.CloseMainWindow()
      if (-not $process.WaitForExit(12000)) {
        Stop-Process -Id $process.Id -Force
        $process.WaitForExit()
      }
    }
    $process.Refresh()
    if ($process.HasExited) {
      $null = $process.WaitForExit()
      $process.Refresh()
      $processExitCode = $process.ExitCode
      Write-Trace "APP_EXIT has_exited=true exit_code=$processExitCode"
      if ($processExitCode -ne '0') { $failed = $true }
    } else {
      Write-Trace 'APP_EXIT has_exited=false exit_code=NOT_AVAILABLE'
      $failed = $true
    }
  }
}

if ($failed) {
  Write-Trace 'exit_code=1'
  exit 1
}
Write-Trace 'exit_code=0'
exit 0
