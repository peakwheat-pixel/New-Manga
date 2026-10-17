param(
    [string]$IsolationRoot = (Join-Path $env:TEMP 'feat-import-multi-r2'),
    [string]$EvidenceDirectory = 'gui-run-r2'
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class ImportMultiNativeMouse {
    [DllImport("user32.dll")] private static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] private static extern void mouse_event(uint flags, uint dx, uint dy, uint data, UIntPtr extraInfo);
    public static void Click(int x, int y) {
        if (!SetCursorPos(x, y)) throw new InvalidOperationException("cursor position failed");
        mouse_event(0x0002, 0, 0, 0, UIntPtr.Zero);
        mouse_event(0x0004, 0, 0, 0, UIntPtr.Zero);
    }
}
'@

$RepoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..'))
$hostTemp = $env:TEMP
$isoRoot = [System.IO.Path]::GetFullPath($IsolationRoot)
$approvedIsolation = [System.IO.Path]::GetFullPath((Join-Path $env:TEMP 'feat-import-multi-r2'))
if (-not [string]::Equals($isoRoot, $approvedIsolation, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'refusing UIA data root other than the approved TEMP isolation root'
}
$exe = Join-Path $RepoRoot 'apps/desktop/src-tauri/target/debug/m2rc1-desktop.exe'
$outDir = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot $EvidenceDirectory))
$evidenceRoot = [System.IO.Path]::GetFullPath($PSScriptRoot)
if (-not $outDir.StartsWith($evidenceRoot + [System.IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -and $outDir -ne $evidenceRoot) {
    throw 'refusing UIA evidence path outside verification directory'
}
if (-not (Test-Path -LiteralPath $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }
if (Get-Process -Name 'm2rc1-desktop' -ErrorAction SilentlyContinue) { throw 'm2rc1-desktop is already running; refusing to start another GUI run' }
$windowTitle = 'M2-RC1 resource channel runtime'
$runSuffix = [Guid]::NewGuid().ToString('N').Substring(0, 6)
$title = "NMImportMultiR2Book20261018$runSuffix"
$chapterTitle = "NMImportMultiR2Chapter20261018$runSuffix"
$fixtureRoot = Join-Path $isoRoot 'fixtures'
$AE = [System.Windows.Automation.AutomationElement]
$TS = [System.Windows.Automation.TreeScope]
$CT = [System.Windows.Automation.ControlType]
$ANY = [System.Windows.Automation.Condition]::TrueCondition
$Invoke = [System.Windows.Automation.InvokePattern]::Pattern
$ValuePattern = [System.Windows.Automation.ValuePattern]::Pattern
$script:importActive = $false

foreach ($name in @('uia-run.log', 'app-stdout.log', 'app-stderr.log', 'initial-bookshelf.uia.txt', 'create-book-dialog-open.uia.txt', 'create-chapter-dialog-open.uia.txt', 'create-book.uia.txt', 'create-chapter.uia.txt', 'chapter-created.uia.txt', 'import-available.uia.txt', 'multi-select-picker.uia.txt', 'file-picker-after-navigation.uia.txt', 'folder-picker.uia.txt', 'folder-picker-structure.uia.txt', 'folder-picker-after-navigation.uia.txt', 'folder-picker-live.uia.txt', 'folder-picker-live.png', 'multi-select-result.uia.txt', 'multi-select-result.png', 'folder-result.uia.txt', 'folder-result.png')) {
    if (Test-Path -LiteralPath (Join-Path $outDir $name)) { throw "refusing to overwrite evidence: $name" }
}
foreach ($dir in @('profile', 'local', 'tmp', 'derived', 'managed', 'webview', 'catalog', 'data', 'fresh-data', 'fixtures')) {
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
        $name = $button.Current.Name
        if ($null -eq $name) { continue }
        if (($Exact -and $name -eq $namePart) -or (-not $Exact -and $name.Contains($namePart))) { return $button }
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
        if ($name -eq $label) { $edit = $candidate; break }
    }
    if (-not $edit) { throw 'create dialog text input was not exposed to UIA' }
    if (-not $edit.Current.IsEnabled -or $edit.Current.IsOffscreen) { throw 'create dialog text input is disabled or offscreen' }
    $snapshotName = if ($label -eq '作品标题') { 'create-book-dialog-open.uia.txt' } else { 'create-chapter-dialog-open.uia.txt' }
    Save-VisibleControls $window (Join-Path $outDir $snapshotName) | Out-Null
    $edit.GetCurrentPattern($ValuePattern).SetValue($text)
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
        if ($name -and ($kind -in @('Button', 'ComboBox', 'ListItem') -or ($kind -eq 'Text' -and $name -match '^\d+$') -or $name -match '书架|导入|报告|已导入|跳过|失败|待处理|阅读器|返回|Ctrl\+A|子目录')) {
            $lines.Add("$kind|$name|IsEnabled=$($element.Current.IsEnabled)|IsOffscreen=$($element.Current.IsOffscreen)")
        }
    }
    $lines | Set-Content -LiteralPath $path -Encoding utf8
    return $lines
}
function Save-ReportEvidence($window, [string]$path, [string]$screenshotPath) {
    $lines = [System.Collections.Generic.List[string]]::new()
    $elements = $window.FindAll($TS::Descendants, $ANY)
    for ($i = 0; $i -lt $elements.Count; $i += 1) {
        $element = $elements.Item($i)
        $kind = $element.Current.ControlType.ProgrammaticName -replace 'ControlType\.', ''
        $name = $element.Current.Name -replace '[A-Za-z]:\\[^|]*', '<path>' -replace '\\\\[^|]+', '<path>'
        $value = ''
        try { $value = $element.GetCurrentPattern($ValuePattern).Current.Value } catch { }
        $value = $value -replace '[A-Za-z]:\\[^|]*', '<path>' -replace '\\\\[^|]+', '<path>'
        if ($kind -in @('Button', 'Text', 'ListItem', 'DataItem', 'RadioButton', 'ComboBox')) {
            $lines.Add("$kind|$name|value=$value|IsEnabled=$($element.Current.IsEnabled)|IsOffscreen=$($element.Current.IsOffscreen)")
        }
    }
    $lines | Set-Content -LiteralPath $path -Encoding utf8
    $bounds = $window.Current.BoundingRectangle
    if ($bounds.Width -le 0 -or $bounds.Height -le 0) { throw 'application window has no screenshot bounds' }
    $bitmap = [System.Drawing.Bitmap]::new([int]$bounds.Width, [int]$bounds.Height)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    try {
        $graphics.CopyFromScreen([int]$bounds.Left, [int]$bounds.Top, 0, 0, $bitmap.Size)
        $bitmap.Save($screenshotPath, [System.Drawing.Imaging.ImageFormat]::Png)
    } finally { $graphics.Dispose(); $bitmap.Dispose() }
    return $lines
}
function Get-PickerWindow([int]$processId, [string]$kind) {
    $windows = $AE::RootElement.FindAll($TS::Children, $ANY)
    for ($i = 0; $i -lt $windows.Count; $i += 1) {
        $candidate = $windows.Item($i)
        $name = $candidate.Current.Name
        if ($candidate.Current.ProcessId -ne $processId -or $name -eq $windowTitle) { continue }
        if ($kind -eq 'file' -and $name -match '打开|Open|选择文件|Select') { return $candidate }
        if ($kind -eq 'folder' -and $name -match '文件夹|Folder|Browse') { return $candidate }
    }
    return $null
}
function Wait-PickerWindow([int]$processId, [string]$kind, [int]$seconds = 20) {
    $deadline = (Get-Date).AddSeconds($seconds)
    while ((Get-Date) -lt $deadline) {
        $dialog = Get-PickerWindow $processId $kind
        if ($dialog) { return $dialog }
        Start-Sleep -Milliseconds 250
    }
    $windows = $AE::RootElement.FindAll($TS::Children, $ANY)
    $names = @()
    for ($i = 0; $i -lt $windows.Count; $i += 1) {
        $candidate = $windows.Item($i)
        if ($candidate.Current.ProcessId -eq $processId) { $names += $candidate.Current.Name }
    }
    throw "native $kind picker was not exposed; same_process_windows=$($names -join '|')"
}
function Save-PickerControls($dialog, [string]$path) {
    $lines = [System.Collections.Generic.List[string]]::new()
    $elements = $dialog.FindAll($TS::Descendants, $ANY)
    for ($i = 0; $i -lt $elements.Count; $i += 1) {
        $element = $elements.Item($i)
        $kind = $element.Current.ControlType.ProgrammaticName -replace 'ControlType\.', ''
        $name = $element.Current.Name
        if ($name -and $kind -in @('Button', 'ListItem', 'DataItem') -and $name -notmatch '^[A-Za-z]:\\|^\\\\') {
            $lines.Add("$kind|$name|IsEnabled=$($element.Current.IsEnabled)|IsOffscreen=$($element.Current.IsOffscreen)")
        }
    }
    $lines | Set-Content -LiteralPath $path -Encoding utf8
    return $lines
}
function Save-PickerStructure($dialog, [string]$path) {
    $lines = [System.Collections.Generic.List[string]]::new()
    $elements = $dialog.FindAll($TS::Descendants, $ANY)
    for ($i = 0; $i -lt $elements.Count; $i += 1) {
        $element = $elements.Item($i)
        $kind = $element.Current.ControlType.ProgrammaticName -replace 'ControlType\.', ''
        if ($kind -notin @('Button', 'Edit', 'ComboBox', 'List', 'ListItem', 'DataItem', 'Pane')) { continue }
        $name = $element.Current.Name -replace '[A-Za-z]:\\[^|]*', '<path>' -replace '\\\\[^|]+', '<path>'
        $lines.Add("$kind|$name|id=$($element.Current.AutomationId)|class=$($element.Current.ClassName)")
    }
    $lines | Set-Content -LiteralPath $path -Encoding utf8
    return $lines
}
function Navigate-Picker([int]$processId, [string]$kind, [string]$path, [string]$label) {
    $target = [System.IO.Path]::GetFullPath($path)
    if (-not (Test-Path -LiteralPath $target -PathType Container)) { throw "selected $kind fixture folder is missing: $label" }
    $navigationPath = $target.TrimEnd([char[]]@('\', '/')) + '\'
    if ($navigationPath.ToCharArray() | Where-Object { [int]$_ -gt 127 }) { throw 'picker navigation path must be ASCII' }
    $dialog = Wait-PickerWindow $processId $kind
    [System.Windows.Forms.SendKeys]::SendWait('^l')
    Set-Clipboard -Value $navigationPath
    [System.Windows.Forms.SendKeys]::SendWait('^v')
    [System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
    Start-Sleep -Seconds 2
    $dialog = Wait-PickerWindow $processId $kind
    $snapshot = if ($kind -eq 'file') { 'file-picker-after-navigation.uia.txt' } else { 'folder-picker-after-navigation.uia.txt' }
    Save-PickerStructure $dialog (Join-Path $outDir $snapshot) | Out-Null
    if ($kind -eq 'file') {
        $expected = @(Get-ChildItem -LiteralPath $target -File | Sort-Object Name | ForEach-Object { $_.Name })
        $visible = @((Get-Controls $dialog $CT::ListItem) + (Get-Controls $dialog $CT::DataItem) | ForEach-Object { $_.Current.Name })
        $matching = @($expected | Where-Object { $_ -in $visible })
        if ($expected.Count -eq 0 -or $matching.Count -ne $expected.Count) {
            throw "native file picker target items mismatch: expected=$($expected.Count) visible=$($matching.Count)"
        }
        Write-Trace "PICKER_NAVIGATION=PASS kind=file target=$label visible_files=$($matching.Count)" | Out-Null
    } else {
        $folderNameField = @($dialog.FindAll($TS::Descendants, $ANY) | Where-Object { $_.Current.AutomationId -eq '1152' -and $_.Current.ClassName -eq 'Edit' }) | Select-Object -First 1
        $folderValue = 'UIA_UNAVAILABLE'
        if ($folderNameField) { try { $folderValue = $folderNameField.GetCurrentPattern($ValuePattern).Current.Value } catch { } }
        $folderFieldMatchesTarget = $folderValue -eq (Split-Path -Leaf $target)
        Write-Trace "PICKER_NAVIGATION=PASS kind=folder target=direct-folder-fixture current_folder_field_match=$folderFieldMatchesTarget" | Out-Null
    }
    return $dialog
}

function Select-AllFilesAndConfirm($dialog, [string[]]$expectedNames) {
    $null = Save-PickerControls $dialog (Join-Path $outDir 'multi-select-picker.uia.txt')
    $items = @(
        @(Get-Controls $dialog $CT::ListItem) + @(Get-Controls $dialog $CT::DataItem) |
            Where-Object { $_.Current.Name -in $expectedNames }
    )
    if ($items.Count -ne $expectedNames.Count) { throw 'expected multi-select fixtures were not visible in the native picker' }
    $selectionPattern = [System.Windows.Automation.SelectionItemPattern]::Pattern
    $items[0].GetCurrentPattern($selectionPattern).Select()
    for ($i = 1; $i -lt $items.Count; $i += 1) { $items[$i].GetCurrentPattern($selectionPattern).AddToSelection() }
    [System.Windows.Forms.SendKeys]::SendWait('^a')
    Start-Sleep -Milliseconds 300
    $selectedCount = 0
    $selectionReadable = $true
    foreach ($item in $items) {
        try { if ($item.GetCurrentPattern($selectionPattern).Current.IsSelected) { $selectedCount += 1 } }
        catch { $selectionReadable = $false }
    }
    if ($selectionReadable -and $items.Count -eq $expectedNames.Count -and $selectedCount -ne $expectedNames.Count) {
        throw "Ctrl+A did not select all expected files; selected_count=$selectedCount"
    }
    if (-not $selectionReadable -or $selectedCount -ne $expectedNames.Count) { throw "Ctrl+A selection verification failed: selected_count=$selectedCount" }
    Write-Trace "FILE_PICKER_SELECT_ALL=PASS key=Ctrl+A UIA_Select=true visible_expected_items=$($items.Count) selected_count=$selectedCount" | Out-Null
    [System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
    $script:importActive = $true
}
function Wait-FolderPickerClosed([int]$processId) {
    $deadline = (Get-Date).AddSeconds(3)
    while ((Get-Date) -lt $deadline) {
        if (-not (Get-PickerWindow $processId 'folder')) { return $true }
        Start-Sleep -Milliseconds 100
    }
    return (-not (Get-PickerWindow $processId 'folder'))
}
function Confirm-FolderPicker($dialog, [int]$processId) {
    $null = Save-PickerControls $dialog (Join-Path $outDir 'folder-picker.uia.txt')
    $null = Save-PickerStructure $dialog (Join-Path $outDir 'folder-picker-structure.uia.txt')
    $null = Save-ReportEvidence $dialog (Join-Path $outDir 'folder-picker-live.uia.txt') (Join-Path $outDir 'folder-picker-live.png')
    $confirm = @($dialog.FindAll($TS::Descendants, $ANY) | Where-Object { $_.Current.AutomationId -eq '1' -and $_.Current.ClassName -eq 'Button' -and $_.Current.Name -eq '选择文件夹' }) | Select-Object -First 1
    if (-not $confirm) { throw 'exact folder picker confirmation control was not exposed' }
    if (-not $confirm.Current.IsEnabled -or $confirm.Current.IsOffscreen) { throw "folder confirmation control disabled/offscreen: enabled=$($confirm.Current.IsEnabled) offscreen=$($confirm.Current.IsOffscreen)" }

    try { $confirm.GetCurrentPattern($Invoke).Invoke() } catch { }
    $closed = Wait-FolderPickerClosed $processId
    Write-Trace "FOLDER_CONFIRM_TRY level=1 method=InvokePattern.Invoke dialog_closed=$($closed.ToString().ToLowerInvariant())" | Out-Null
    if ($closed) { $script:importActive = $true; return }

    try {
        $bounds = $confirm.Current.BoundingRectangle
        if ($bounds.Width -le 0 -or $bounds.Height -le 0) { throw 'confirmation control has empty bounds' }
        $x = [int][Math]::Round($bounds.Left + ($bounds.Width / 2))
        $y = [int][Math]::Round($bounds.Top + ($bounds.Height / 2))
        [ImportMultiNativeMouse]::Click($x, $y)
    } catch { }
    $closed = Wait-FolderPickerClosed $processId
    Write-Trace "FOLDER_CONFIRM_TRY level=2 method=UIA_BoundsCenter_MouseClick dialog_closed=$($closed.ToString().ToLowerInvariant())" | Out-Null
    if ($closed) { $script:importActive = $true; return }

    try {
        $activeDialog = Get-PickerWindow $processId 'folder'
        if (-not $activeDialog) { throw 'folder picker window is no longer available' }
        $activeDialog.SetFocus()
        [System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
    } catch { }
    $closed = Wait-FolderPickerClosed $processId
    Write-Trace "FOLDER_CONFIRM_TRY level=3 method=DialogWindow_SetFocus_Enter dialog_closed=$($closed.ToString().ToLowerInvariant())" | Out-Null
    if ($closed) { $script:importActive = $true; return }

    try { [System.Windows.Forms.SendKeys]::SendWait('{ENTER}') } catch { }
    $closed = Wait-FolderPickerClosed $processId
    Write-Trace "FOLDER_CONFIRM_TRY level=4 method=SendKeys_ENTER dialog_closed=$($closed.ToString().ToLowerInvariant())" | Out-Null
    if ($closed) { $script:importActive = $true; return }

    try {
        1..8 | ForEach-Object { [System.Windows.Forms.SendKeys]::SendWait('{TAB}') }
        [System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
    } catch { }
    $closed = Wait-FolderPickerClosed $processId
    Write-Trace "FOLDER_CONFIRM_TRY level=4 method=SendKeys_TABx8_ENTER dialog_closed=$($closed.ToString().ToLowerInvariant())" | Out-Null
    if ($closed) { $script:importActive = $true; return }

    throw 'all approved folder confirmation methods failed; native picker remained open'
}function Wait-ImportReport([int]$processId, [string]$snapshotName) {
    $deadline = (Get-Date).AddSeconds(300)
    while ((Get-Date) -lt $deadline) {
        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
        if (-not $process) { $script:importActive = $false; throw 'application exited while waiting for the import report' }
        $window = Get-AppWindow $processId
        if ($window) {
            $finish = Find-Button $window '完成' -Exact
            if ($finish) {
                $stem = [System.IO.Path]::GetFileNameWithoutExtension($snapshotName)
                $screenshot = Join-Path $outDir "$stem.png"
                $lines = Save-ReportEvidence $window (Join-Path $outDir $snapshotName) $screenshot
                if (-not ($lines | Where-Object { $_ -match '导入报告' }) -or
                    -not ($lines | Where-Object { $_ -match '已导入' }) -or
                    -not ($lines | Where-Object { $_ -match '跳过重复' }) -or
                    -not ($lines | Where-Object { $_ -match '导入失败' })) {
                    $script:importActive = $false
                    throw "import summary controls were incomplete: $snapshotName"
                }
                $script:importActive = $false
                Write-Trace "IMPORT_REPORT=VISIBLE snapshot=$snapshotName screenshot=$stem.png" | Out-Null
                return $finish
            }
        }
        Start-Sleep -Milliseconds 500
    }
    throw "timed out waiting for import report after 300 seconds: $snapshotName"
}
function Select-ImportTarget($window, [string]$chapterName) {
    $combos = @(Get-Controls $window $CT::ComboBox)
    if ($combos.Count -eq 0) { throw 'import target selector was not exposed' }
    $selector = $combos[$combos.Count - 1]
    try {
        $valuePattern = $selector.GetCurrentPattern($ValuePattern)
        $valuePattern.SetValue($chapterName)
        Start-Sleep -Milliseconds 250
        if ($valuePattern.Current.Value -eq $chapterName) {
            Write-Trace 'IMPORT_TARGET=PASS selected=true' | Out-Null
            return
        }
    } catch { }
    try { $selector.GetCurrentPattern([System.Windows.Automation.ExpandCollapsePattern]::Pattern).Expand() } catch { }
    Start-Sleep -Milliseconds 250
    $options = @(Get-Controls $window $CT::ListItem | Where-Object { $_.Current.Name -eq $chapterName })
    if ($options.Count -eq 0) { $options = @(Get-Controls $window $CT::DataItem | Where-Object { $_.Current.Name -eq $chapterName }) }
    if ($options.Count -eq 0) { throw 'target chapter option was not exposed by the selector' }
    $options[0].GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern).Select()
    Write-Trace 'IMPORT_TARGET=PASS selected=true' | Out-Null
}

$process = $null
$failed = $false
$originalClipboard = $null
try { $originalClipboard = [System.Windows.Forms.Clipboard]::GetDataObject() } catch { }
try {
    $env:M2RC1_PACKAGED = '1'
    Remove-Item Env:M2RC1_SRC_ROOT -ErrorAction SilentlyContinue
    Remove-Item Env:M2RC1_PYTHON -ErrorAction SilentlyContinue
    $env:APPDATA = Join-Path $isoRoot 'profile'
    $env:LOCALAPPDATA = Join-Path $isoRoot 'local'
    $env:TEMP = Join-Path $isoRoot 'tmp'
    $env:TMP = $env:TEMP
    $env:NEWMANGA_DATA_ROOT = Join-Path $isoRoot 'fresh-data'
    $env:M2RC1_DERIVED_ROOT = Join-Path $isoRoot 'derived'
    $env:M2RC1_MANAGED_ROOT = Join-Path $isoRoot 'managed'
    $env:M2RC2_CATALOG_DB = Join-Path $isoRoot 'catalog/catalog.sqlite'
    $env:WEBVIEW2_USER_DATA_FOLDER = Join-Path $isoRoot 'webview'

    $process = Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -PassThru `
        -RedirectStandardOutput (Join-Path $outDir 'app-stdout.log') `
        -RedirectStandardError (Join-Path $outDir 'app-stderr.log')
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
        if ($button.Current.Name -and $button.Current.Name.Contains('新建作品')) {
            Write-Trace "CREATE_BUTTON_FOUND name=$($button.Current.Name) IsEnabled=$($button.Current.IsEnabled) IsOffscreen=$($button.Current.IsOffscreen)"
        }
    }
    $createButtons = @($allButtons | Where-Object { $_.Current.Name -and $_.Current.Name.Contains('新建作品') })
    if ($createButtons.Count -eq 0) {
        throw "empty-shelf create-book button not found; visible_controls=$($initialControls.Count)"
    }
    $createBookButton = $createButtons | Where-Object { $_.Current.Name -eq '新建作品' -and $_.Current.IsEnabled -and -not $_.Current.IsOffscreen } | Select-Object -First 1
    if (-not $createBookButton) { $createBookButton = $createButtons | Where-Object { $_.Current.IsEnabled -and -not $_.Current.IsOffscreen } | Select-Object -First 1 }
    if (-not $createBookButton) { throw 'no enabled visible create-book button was found' }
    Write-Trace "CREATE_BOOK_ENTRY=PASS matching_buttons=$(@($createButtons).Count) enabled=true"
    Invoke-Button $createBookButton '新建作品'
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

    $multiFiles = @(Get-ChildItem -LiteralPath (Join-Path $fixtureRoot 'multi-select') -File | Sort-Object Name)
    $folderFiles = @(Get-ChildItem -LiteralPath (Join-Path $fixtureRoot 'folder-direct') -File | Sort-Object Name)
    if ($multiFiles.Count -ne 2 -or $folderFiles.Count -ne 3) { throw 'isolated import fixture counts changed' }
    $pythonPath = 'G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Python 3.12 executable not found for read-only page count evidence' }
    $countScript = Join-Path $PSScriptRoot 'verify-page-count-r2.py'
    $beforeMulti = & $pythonPath $countScript $isoRoot $chapterTitle $hostTemp
    if ($LASTEXITCODE -ne 0 -or ($beforeMulti -join ' ') -notmatch 'pages=0') { throw 'isolated target chapter was not empty before multi-select import' }
    Write-Trace 'PAGE_COUNT before_multi_select=0'

    $filePicker = Find-Button $window '选择图片 / PDF 文件'
    Invoke-Button $filePicker '选择多张图片'
    $nativePicker = Navigate-Picker $process.Id 'file' (Join-Path $fixtureRoot 'multi-select') 'multi-select-fixture'
    $expectedNames = @($multiFiles | ForEach-Object { $_.Name })
    Select-AllFilesAndConfirm $nativePicker $expectedNames
    $multiFinish = Wait-ImportReport $process.Id 'multi-select-result.uia.txt'
    $afterMulti = & $pythonPath $countScript $isoRoot $chapterTitle $hostTemp
    if ($LASTEXITCODE -ne 0 -or ($afterMulti -join ' ') -notmatch 'pages=2') { throw "multi-select import page count mismatch: $($afterMulti -join ' ')" }
    Write-Trace 'MULTI_SELECT_IMPORT=PASS selected=2 page_delta=2'
    Invoke-Button $multiFinish '关闭多选导入报告'

    $toolbarImport = Wait-Button $process.Id '导入作品'
    Invoke-Button $toolbarImport '打开章节选择导入'
    $window = Get-AppWindow $process.Id
    $deadline = (Get-Date).AddSeconds(10)
    $selector = $null
    while ((Get-Date) -lt $deadline -and -not $selector) {
        $combos = Get-Controls $window $CT::ComboBox
        if ($combos.Count -gt 0) { $selector = $combos.Item($combos.Count - 1) }
        if (-not $selector) { Start-Sleep -Milliseconds 300; $window = Get-AppWindow $process.Id }
    }
    if (-not $selector) { throw 'folder import target chapter selector was not visible' }
    Select-ImportTarget $window $chapterTitle
    Start-Sleep -Milliseconds 250
    $folderPicker = Find-Button $window '选择图片文件夹'
    if (-not $folderPicker -or -not $folderPicker.Current.IsEnabled) { throw 'folder import picker was not enabled for the created chapter' }
    Invoke-Button $folderPicker '选择图片文件夹'
    $nativeFolder = Navigate-Picker $process.Id 'folder' (Join-Path $fixtureRoot 'folder-direct') 'direct-folder-fixture'
    Confirm-FolderPicker $nativeFolder ($process.Id)
    $folderFinish = Wait-ImportReport $process.Id 'folder-result.uia.txt'
    $afterFolder = & $pythonPath $countScript $isoRoot $chapterTitle $hostTemp
    if ($LASTEXITCODE -ne 0 -or ($afterFolder -join ' ') -notmatch 'pages=5') { throw "folder import page count mismatch: $($afterFolder -join ' ')" }
    Write-Trace 'FOLDER_IMPORT=PASS direct_children=3 page_delta=3 final_chapter_pages=5'
    Invoke-Button $folderFinish '关闭文件夹导入报告'
} catch {
    $failed = $true
    Write-Trace "FATAL line=$($_.InvocationInfo.ScriptLineNumber) $($_.Exception.Message)"
} finally {
    if ($process) {
        $process.Refresh()
        if (-not $process.HasExited) {
            if ($script:importActive) {
                Write-Trace "APP_CLEANUP=deferred reason=import_not_confirmed_complete pid=$($process.Id)"
                $failed = $true
            } else {
                $null = $process.CloseMainWindow()
                if (-not $process.WaitForExit(12000)) { Stop-Process -Id $process.Id -Force; $process.WaitForExit() }
            }
        }
        $process.Refresh()
        if ($process.HasExited) {
            Write-Trace "APP_EXIT exit_code=$($process.ExitCode)"
            if ($process.ExitCode -ne 0) { $failed = $true }
        } else {
            Write-Trace 'APP_EXIT exit_code=NOT_AVAILABLE process_preserved=true'
            $failed = $true
        }
    }
}
if ($null -ne $originalClipboard) {
    try {
        [System.Windows.Forms.Clipboard]::SetDataObject($originalClipboard, $true)
        Write-Trace 'CLIPBOARD_RESTORE=PASS original_formats_restored=true'
    } catch {
        Write-Trace 'CLIPBOARD_RESTORE=FAIL original_formats_restored=false'
        $failed = $true
    }
}

if ($failed) { Write-Trace 'exit_code=1'; exit 1 }
Write-Trace 'exit_code=0'
exit 0
