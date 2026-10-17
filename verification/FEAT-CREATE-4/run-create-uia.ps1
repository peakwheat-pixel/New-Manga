param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path,
    [string]$IsolationName = 'feat-create-4-isolation-20261017',
    [string]$EvidenceDirectory = '.'
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms

$RepoRoot = [System.IO.Path]::GetFullPath($RepoRoot)
$isoRoot = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot "apps/desktop/src-tauri/target/$IsolationName"))
$targetRoot = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot 'apps/desktop/src-tauri/target'))
if (-not $isoRoot.StartsWith($targetRoot + [System.IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'refusing UIA data root outside worktree target'
}
$exe = Join-Path $RepoRoot 'apps/desktop/src-tauri/target/debug/m2rc1-desktop.exe'
$outDir = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot $EvidenceDirectory))
$evidenceRoot = [System.IO.Path]::GetFullPath($PSScriptRoot)
if (-not $outDir.StartsWith($evidenceRoot + [System.IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -and $outDir -ne $evidenceRoot) {
    throw 'refusing UIA evidence path outside verification directory'
}
if (-not (Test-Path -LiteralPath $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }
$windowTitle = 'M2-RC1 resource channel runtime'
$title = 'MangaCreate4UIA20261017'
$chapterTitle = 'MangaChapter4UIA20261017'
$AE = [System.Windows.Automation.AutomationElement]
$TS = [System.Windows.Automation.TreeScope]
$CT = [System.Windows.Automation.ControlType]
$ANY = [System.Windows.Automation.Condition]::TrueCondition
$Invoke = [System.Windows.Automation.InvokePattern]::Pattern
$ValuePattern = [System.Windows.Automation.ValuePattern]::Pattern

foreach ($name in @('uia-run.log', 'initial-bookshelf.uia.txt', 'create-book-dialog-open.uia.txt', 'create-chapter-dialog-open.uia.txt', 'create-book.uia.txt', 'create-chapter.uia.txt', 'chapter-created.uia.txt', 'import-available.uia.txt', 'app-out.log', 'app-err.log')) {
    if (Test-Path -LiteralPath (Join-Path $outDir $name)) { throw "refusing to overwrite evidence: $name" }
}
foreach ($dir in @('profile', 'local', 'tmp', 'derived', 'managed', 'webview', 'catalog', 'data')) {
    if (-not (Test-Path -LiteralPath (Join-Path $isoRoot $dir) -PathType Container)) { throw "isolated directory missing: $dir" }
}
if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw 'built application executable is missing' }

$trace = Join-Path $outDir 'uia-run.log'
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
function Get-Controls($window, $controlType) {
    return $window.FindAll($TS::Descendants, (New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty, $controlType)))
}
function Find-Button($window, [string]$namePart, [switch]$Exact) {
    $buttons = Get-Controls $window $CT::Button
    for ($i = 0; $i -lt $buttons.Count; $i += 1) {
        $button = $buttons.Item($i)
        if (($Exact -and $button.Current.Name -eq $namePart) -or (-not $Exact -and $button.Current.Name.Contains($namePart))) { return $button }
    }
    return $null
}
function Wait-Button($processId, [string]$namePart, [int]$seconds = 20) {
    $deadline = (Get-Date).AddSeconds($seconds)
    while ((Get-Date) -lt $deadline) {
        $window = Get-AppWindow $processId
        if ($window) {
            $button = Find-Button $window $namePart
            if ($button) { return $button }
        }
        Start-Sleep -Milliseconds 300
    }
    throw "UIA button not found before timeout: $namePart"
}
function Wait-ExactButton($processId, [string]$name, [int]$seconds = 20) {
    $deadline = (Get-Date).AddSeconds($seconds)
    while ((Get-Date) -lt $deadline) {
        $window = Get-AppWindow $processId
        if ($window) {
            $button = Find-Button $window $name -Exact
            if ($button) { return $button }
        }
        Start-Sleep -Milliseconds 300
    }
    throw "UIA button not found before timeout: $name"
}
function Invoke-Button($button, [string]$label) {
    if (-not $button.Current.IsEnabled -or $button.Current.IsOffscreen) { throw "button is disabled or offscreen: $label" }
    $button.GetCurrentPattern($Invoke).Invoke()
    Write-Trace "CLICK name=$($button.Current.Name) IsEnabled=true IsOffscreen=false"
}
function Set-DialogTitle($window, [string]$text, [string]$label) {
    $edits = @(Get-Controls $window $CT::Edit)
    foreach ($candidate in $edits) { Write-Trace "EDIT_FOUND name=$($candidate.Current.Name) IsEnabled=$($candidate.Current.IsEnabled) IsOffscreen=$($candidate.Current.IsOffscreen)" }
    $edit = $null
    for ($i = 0; $i -lt $edits.Count; $i += 1) {
        $candidate = $edits.Item($i)
        $name = $candidate.Current.Name
        if ($name -and $name.Contains($label) -and -not $name.Contains('搜索')) { $edit = $candidate; break }
    }
    if (-not $edit) {
        foreach ($candidate in $edits) {
            $name = $candidate.Current.Name
            if (-not $name -or -not $name.Contains('搜索')) { $edit = $candidate }
        }
    }
    if (-not $edit) { throw 'create dialog text input was not exposed to UIA' }
    if (-not $edit.Current.IsEnabled -or $edit.Current.IsOffscreen) { throw 'create dialog text input is disabled or offscreen' }
    $snapshotName = if ($label -eq '作品标题') { 'create-book-dialog-open.uia.txt' } else { 'create-chapter-dialog-open.uia.txt' }
    Save-VisibleControls $window (Join-Path $outDir $snapshotName) | Out-Null
    try { $edit.GetCurrentPattern($ValuePattern).SetValue($text) } catch {
        $edit.SetFocus()
        [System.Windows.Forms.SendKeys]::SendWait('^a')
        [System.Windows.Forms.SendKeys]::SendWait($text)
    }
    Start-Sleep -Milliseconds 250
    $actual = $edit.GetCurrentPattern($ValuePattern).Current.Value
    if ($actual -ne $text) { throw "UIA text entry did not stick: expected=$text actual=$actual" }
    Write-Trace "TEXT_ENTRY label=$($edit.Current.Name) value=$actual"
}
function Save-VisibleControls($window, [string]$path) {
    $lines = [System.Collections.Generic.List[string]]::new()
    $elements = $window.FindAll($TS::Descendants, $ANY)
    for ($i = 0; $i -lt $elements.Count; $i += 1) {
        $element = $elements.Item($i)
        $kind = $element.Current.ControlType.ProgrammaticName -replace 'ControlType\.', ''
        $name = $element.Current.Name
        if ($name -and ($kind -in @('Button', 'Edit', 'ComboBox', 'Text', 'ListItem') -or $name -match '书架|作品|章节|导入|阅读器|返回')) {
            $lines.Add("$kind|$name|IsEnabled=$($element.Current.IsEnabled)|IsOffscreen=$($element.Current.IsOffscreen)")
        }
    }
    $lines | Set-Content -LiteralPath $path -Encoding utf8
    return $lines
}

$process = $null
$failed = $false
try {
    $env:APPDATA = Join-Path $isoRoot 'profile'
    $env:LOCALAPPDATA = Join-Path $isoRoot 'local'
    $env:TEMP = Join-Path $isoRoot 'tmp'
    $env:TMP = $env:TEMP
    $env:NEWMANGA_DATA_ROOT = Join-Path $isoRoot 'data'
    $env:M2RC1_DERIVED_ROOT = Join-Path $isoRoot 'derived'
    $env:M2RC1_MANAGED_ROOT = Join-Path $isoRoot 'managed'
    $env:M2RC2_CATALOG_DB = Join-Path $isoRoot 'catalog/catalog.sqlite'
    $env:WEBVIEW2_USER_DATA_FOLDER = Join-Path $isoRoot 'webview'

    $process = Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -PassThru `
        -RedirectStandardOutput (Join-Path $outDir 'app-out.log') `
        -RedirectStandardError (Join-Path $outDir 'app-err.log')
    Write-Trace "APP_START pid=$($process.Id) exe_sha256=$((Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant()) data_root=isolated"

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
    Start-Sleep -Seconds 4

    $initialControls = Save-VisibleControls $window (Join-Path $outDir 'initial-bookshelf.uia.txt')
    $allButtons = @(Get-Controls $window $CT::Button)
    foreach ($button in $allButtons) {
        if ($button.Current.Name.Contains('新建作品')) {
            Write-Trace "CREATE_BUTTON_FOUND name=$($button.Current.Name) IsEnabled=$($button.Current.IsEnabled) IsOffscreen=$($button.Current.IsOffscreen)"
        }
    }
    $createButtons = @($allButtons | Where-Object { $_.Current.Name.Contains('新建作品') })
    if ($createButtons.Count -eq 0) {
        throw "empty-shelf create-book button not found; visible_controls=$($initialControls.Count)"
    }
    if (@($createButtons | Where-Object { -not $_.Current.IsEnabled -or $_.Current.IsOffscreen }).Count -gt 0) {
        throw 'empty-shelf create-book button is disabled or offscreen'
    }
    Write-Trace "EMPTY_SHELF_CREATE_BOOK=PASS matching_buttons=$(@($createButtons).Count) enabled=true"
    $emptyButton = $createButtons | Where-Object { $_.Current.Name -eq '新建作品' } | Select-Object -First 1
    if (-not $emptyButton) { $emptyButton = $createButtons | Select-Object -First 1 }
    Invoke-Button $emptyButton '新建作品'
    $window = Get-AppWindow $process.Id
    Set-DialogTitle $window $title '作品标题'
    Save-VisibleControls $window (Join-Path $outDir 'create-book.uia.txt') | Out-Null
    Invoke-Button (Wait-Button $process.Id '创建作品') '创建作品'
    $bookButton = Wait-Button $process.Id $title 30
    if (-not $bookButton) { throw 'created book did not appear in the bookshelf' }
    Write-Trace 'CREATE_BOOK=PASS returned_book_visible=true'

    $chapterButton = Wait-Button $process.Id '新建章节'
    Invoke-Button $chapterButton '新建章节'
    $window = Get-AppWindow $process.Id
    Set-DialogTitle $window $chapterTitle '章节标题'
    Save-VisibleControls $window (Join-Path $outDir 'create-chapter.uia.txt') | Out-Null
    Invoke-Button (Wait-Button $process.Id '创建章节') '创建章节'
    $chapterEntry = Wait-ExactButton $process.Id '阅读'
    $chapterElements = Save-VisibleControls (Get-AppWindow $process.Id) (Join-Path $outDir 'chapter-created.uia.txt')
    if (-not ($chapterElements | Where-Object { $_ -like "*Text|$chapterTitle|*" -or $_ -like "*Button|$chapterTitle|*" })) {
        $window = Get-AppWindow $process.Id
        $allNames = $window.FindAll($TS::Descendants, $ANY)
        $visibleChapter = $false
        for ($i = 0; $i -lt $allNames.Count; $i += 1) { if ($allNames.Item($i).Current.Name -eq $chapterTitle) { $visibleChapter = $true } }
        if (-not $visibleChapter) { throw 'created chapter did not appear in the chapter list' }
    }
    Write-Trace 'CREATE_CHAPTER=PASS chapter_visible=true reader_action_enabled=true'
    Invoke-Button $chapterEntry '进入阅读器'
    $readerReturn = Wait-Button $process.Id '返回书架'
    if (-not $readerReturn) { throw 'reader navigation did not open the reader view' }
    Write-Trace 'READER_ENTRY=PASS reader_return_action_visible=true'
    Invoke-Button $readerReturn '返回书架'

    $window = Get-AppWindow $process.Id
    $toolbarImport = Find-Button $window '导入作品' -Exact
    if (-not $toolbarImport) { throw 'bookshelf import entry was not found after reader return' }
    Invoke-Button $toolbarImport '导入作品'
    $window = Get-AppWindow $process.Id
    $deadline = (Get-Date).AddSeconds(10)
    $selector = $null
    while ((Get-Date) -lt $deadline -and -not $selector) {
        $combos = Get-Controls $window $CT::ComboBox
        if ($combos.Count -gt 0) { $selector = $combos.Item($combos.Count - 1) }
        if (-not $selector) { Start-Sleep -Milliseconds 300; $window = Get-AppWindow $process.Id }
    }
    if (-not $selector) { throw 'import target chapter selector was not visible' }
    $importControls = Save-VisibleControls $window (Join-Path $outDir 'import-available.uia.txt')
    if ($importControls | Where-Object { $_ -match '未开放：' }) { throw 'import still reports that no target exists' }
    Write-Trace "IMPORT_ENTRY=PASS target_selector_visible=true selector_name=$($selector.Current.Name) unavailable_notice=false"

    $closeImport = Find-Button $window '✕'
    if ($closeImport) { Invoke-Button $closeImport '关闭导入对话框' }
    Start-Sleep -Milliseconds 500
    $window = Get-AppWindow $process.Id
    $chapterImport = Find-Button $window '导入页面到此章节'
    if (-not $chapterImport) { $chapterImport = Find-Button $window '导入' -Exact }
    if (-not $chapterImport) { throw 'chapter import action was not found' }
    Invoke-Button $chapterImport '导入到已创建章节'
    $window = Get-AppWindow $process.Id
    $filePicker = Find-Button $window '选择图片 / PDF 文件'
    $folderPicker = Find-Button $window '选择图片文件夹'
    if (-not $filePicker -or -not $folderPicker -or -not $filePicker.Current.IsEnabled -or -not $folderPicker.Current.IsEnabled) {
        throw 'file and folder import pickers did not become enabled for the created chapter'
    }
    $importControls = Save-VisibleControls $window (Join-Path $outDir 'import-available.uia.txt')
    Write-Trace 'IMPORT_PICKERS=PASS file_enabled=true folder_enabled=true'
    $closeImport = Find-Button $window '✕'
    if ($closeImport) { Invoke-Button $closeImport '关闭导入对话框' }
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
            Write-Trace "APP_EXIT exit_code=$($process.ExitCode)"
            if ($process.ExitCode -ne 0) { $failed = $true }
        } else {
            Write-Trace 'APP_EXIT exit_code=NOT_AVAILABLE'
            $failed = $true
        }
    }
}

if ($failed) { Write-Trace 'exit_code=1'; exit 1 }
Write-Trace 'exit_code=0'
exit 0
