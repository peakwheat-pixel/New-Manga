# V11R-A11Y-1 real-machine UIA audit.
#
# Launches the real v2 shell with a real sidecar and an isolated data/log root, then enumerates the
# window's UIA tree (Button / Edit / ComboBox) and fails (exit 1) when any Button has no readable name
# or still exposes a CLR type name. Re-runnable; always terminates the app and its sidecar children.
#
# Usage:
#   pwsh -NoProfile -File tools/e2e/uia-audit.ps1 [-OutFile <path>]
# All paths with spaces must be passed to the app as --key="value" (the app parser only accepts =).

param(
    [string]$AppExe = '',
    [string]$SidecarDir = '',
    [string]$DataRoot = '',
    [string]$LogDir = '',
    [string]$OutFile = '',
    [int]$TimeoutSeconds = 30,
    [int]$ExitAfterMs = 60000,
    [string]$Variant = 'dark'
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$workRoot = Join-Path $env:TEMP 'newmanga-uia-audit'
$runStamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$runRoot = Join-Path $workRoot $runStamp
if ([string]::IsNullOrWhiteSpace($AppExe)) {
    $AppExe = Join-Path $repoRoot 'apps\desktop-avalonia\src\NewManga.App\bin\Debug\net9.0\NewManga.App.exe'
}
if ([string]::IsNullOrWhiteSpace($SidecarDir)) {
    $SidecarDir = Join-Path $repoRoot 'apps\desktop-avalonia\build\sidecar\core-sidecar\core-sidecar'
}
if ([string]::IsNullOrWhiteSpace($DataRoot)) { $DataRoot = Join-Path $runRoot 'data' }
if ([string]::IsNullOrWhiteSpace($LogDir)) { $LogDir = Join-Path $runRoot 'logs' }
if ([string]::IsNullOrWhiteSpace($OutFile)) { $OutFile = Join-Path $runRoot 'uia-audit.json' }
New-Item -ItemType Directory -Force $DataRoot, $LogDir | Out-Null
New-Item -ItemType Directory -Force (Split-Path $OutFile) | Out-Null

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$process = $null
try {
    if (-not (Test-Path $AppExe)) { throw "app exe not found: $AppExe" }
    if (-not (Test-Path $SidecarDir)) { throw "sidecar dir not found: $SidecarDir" }

    # Start-Process joins -ArgumentList strings with spaces; pass ONE pre-quoted string so paths with
    # spaces survive. The app parser requires --key=value; the quotes are part of the value token.
    $argumentLine = '--shell=v2 --variant={0} --width=1600 --height=1000 --exit-after={1} --sidecar-dir="{2}" --data-root="{3}" --log-dir="{4}"' -f `
        $Variant, $ExitAfterMs, $SidecarDir, $DataRoot, $LogDir
    $process = Start-Process -FilePath $AppExe -ArgumentList $argumentLine -PassThru
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $window = $null
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Milliseconds 500
        if ($process.HasExited) { break }
        $condition = New-Object System.Windows.Automation.PropertyCondition(
            [System.Windows.Automation.AutomationElement]::ProcessIdProperty, $process.Id)
        $candidate = [System.Windows.Automation.AutomationElement]::RootElement.FindFirst(
            [System.Windows.Automation.TreeScope]::Children, $condition)
        if ($candidate) {
            $window = $candidate
            break
        }
    }

    if (-not $window) {
        throw "main window not found within ${TimeoutSeconds}s (app exited=$($process.HasExited), pid=$($process.Id))"
    }

    # Give the shell one layout pass + Host readiness before reading the subtree.
    Start-Sleep -Seconds 4

    $buttonCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Button)
    $editCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Edit)
    $comboCondition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::ComboBox)
    $orCondition = New-Object System.Windows.Automation.OrCondition($buttonCondition, $editCondition, $comboCondition)
    $elements = $window.FindAll([System.Windows.Automation.TreeScope]::Descendants, $orCondition)

    $typeNamePattern = '^(Avalonia\.|NewManga\.|System\.Windows\.Automation\.)'
    $controls = New-Object System.Collections.Generic.List[object]
    $unnamedButtons = New-Object System.Collections.Generic.List[object]
    $namedButtons = 0
    $buttonCount = 0

    foreach ($element in $elements) {
        try {
            $name = $element.Current.Name
            $controlType = $element.Current.ControlType.ProgrammaticName
            $automationId = $element.Current.AutomationId
            $isButton = $element.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button
            if ($isButton) { $buttonCount++ }
            $isReadable = -not [string]::IsNullOrWhiteSpace($name) -and ($name -notmatch $typeNamePattern)
            if ($isButton -and $isReadable) { $namedButtons++ }
            $record = [ordered]@{
                type         = $controlType
                name         = $name
                automationId = $automationId
                readable     = $isReadable
                enabled      = $element.Current.IsEnabled
                offscreen    = $element.Current.IsOffscreen
            }
            $controls.Add([pscustomobject]$record)
            if ($isButton -and -not $isReadable) { $unnamedButtons.Add([pscustomobject]$record) }
        }
        catch { }
    }

    $result = [ordered]@{
        generatedAt   = (Get-Date).ToString('o')
        appExe        = $AppExe
        sidecarDir    = $SidecarDir
        dataRoot      = $DataRoot
        logDir        = $LogDir
        appPid        = $process.Id
        windowName    = $window.Current.Name
        counts        = [ordered]@{
            enumerated      = $controls.Count
            buttons         = $buttonCount
            namedButtons    = $namedButtons
            unnamedButtons  = $unnamedButtons.Count
            editsAndCombos  = $controls.Count - $buttonCount
        }
        unnamedButtons = $unnamedButtons
        controls        = $controls
    }
    $result | ConvertTo-Json -Depth 6 | Set-Content -Path $OutFile -Encoding UTF8

    Write-Host ("UIA audit: buttons={0} named={1} unnamed={2} -> {3}" -f `
        $buttonCount, $namedButtons, $unnamedButtons.Count, $OutFile)
    if ($unnamedButtons.Count -gt 0) {
        $i = 0
        foreach ($bad in $unnamedButtons) {
            $i++
            Write-Host ("  [{0}] {1} name='{2}' id='{3}'" -f $i, $bad.type, $bad.name, $bad.automationId)
        }
        exit 1
    }

    exit 0
}
finally {
    if ($process -and -not $process.HasExited) {
        $children = Get-CimInstance Win32_Process -Filter "ParentProcessId=$($process.Id)" -ErrorAction SilentlyContinue
        foreach ($child in $children) {
            Stop-Process -Id $child.ProcessId -Force -ErrorAction SilentlyContinue
        }
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    }
}
