$ErrorActionPreference = "Stop"
$packageRoot = "C:\Program Files\New Manga\NewManga"
$distributionRoot = "C:\Program Files\New Manga"
$evidenceRoot = "C:\GateEvidence"
$exe = Join-Path $packageRoot "NewManga.exe"
$stdout = Join-Path $evidenceRoot "app.stdout.log"
$stderr = Join-Path $evidenceRoot "app.stderr.log"
$summary = Join-Path $evidenceRoot "summary.txt"

Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

function Save-Desktop([string]$Path) {
    $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bitmap = New-Object System.Drawing.Bitmap($bounds.Width, $bounds.Height)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    try {
        $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
        $bitmap.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
    } finally {
        $graphics.Dispose()
        $bitmap.Dispose()
    }
}

function Get-AppAutomationElements([int]$ProcessId) {
    $condition = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ProcessIdProperty,
        $ProcessId
    )
    return [System.Windows.Automation.AutomationElement]::RootElement.FindAll(
        [System.Windows.Automation.TreeScope]::Descendants,
        $condition
    )
}

"UTC=$([DateTime]::UtcNow.ToString('o'))" | Set-Content -LiteralPath $summary -Encoding utf8
"USER=$([Environment]::UserName)" | Add-Content -LiteralPath $summary
$os = Get-CimInstance Win32_OperatingSystem
"OS_CAPTION=$($os.Caption)`nOS_VERSION=$($os.Version)`nOS_BUILD=$($os.BuildNumber)`nOS_ARCH=$($os.OSArchitecture)" | Add-Content -LiteralPath $summary
"LOCALAPPDATA=$env:LOCALAPPDATA`nPATH=$env:PATH" | Add-Content -LiteralPath $summary
foreach ($command in @("python.exe", "py.exe", "git.exe")) {
    $found = Get-Command $command -ErrorAction SilentlyContinue
    "$command=$([bool]$found)" | Add-Content -LiteralPath $summary
}

if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw "Packaged executable missing: $exe" }
$manifestLine = Get-Content -LiteralPath (Join-Path $distributionRoot "artifact-manifest.sha256") |
    Where-Object { $_ -match "  NewManga\.exe$" } | Select-Object -First 1
if (-not $manifestLine) { throw "Manifest does not include NewManga.exe" }
$expectedExeHash = ($manifestLine -split "  ", 2)[0]
$actualExeHash = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant()
"EXE_SHA256_EXPECTED=$expectedExeHash`nEXE_SHA256_ACTUAL=$actualExeHash" | Add-Content -LiteralPath $summary
if ($expectedExeHash -ne $actualExeHash) { throw "Executable hash does not match the manifest" }

$writeProbe = Join-Path $packageRoot ".readonly-probe.tmp"
try {
    [System.IO.File]::WriteAllText($writeProbe, "probe")
    "PROGRAM_DIRECTORY_READONLY=False" | Add-Content -LiteralPath $summary
    Remove-Item -LiteralPath $writeProbe -Force
    throw "Mapped program directory unexpectedly accepted writes"
} catch [System.UnauthorizedAccessException] {
    "PROGRAM_DIRECTORY_READONLY=True`nREADONLY_PROBE=UnauthorizedAccessException" | Add-Content -LiteralPath $summary
} catch [System.IO.IOException] {
    "PROGRAM_DIRECTORY_READONLY=True`nREADONLY_PROBE=IOException" | Add-Content -LiteralPath $summary
}

$process = Start-Process -FilePath $exe -WorkingDirectory $packageRoot -PassThru `
    -RedirectStandardOutput $stdout -RedirectStandardError $stderr
"APP_PID=$($process.Id)`nAPP_START_UTC=$([DateTime]::UtcNow.ToString('o'))`nAPP_ARGS=<none>" | Add-Content -LiteralPath $summary

$elements = @()
for ($attempt = 0; $attempt -lt 60; $attempt++) {
    Start-Sleep -Seconds 1
    $process.Refresh()
    if ($process.HasExited) { break }
    $elements = @(Get-AppAutomationElements -ProcessId $process.Id)
    if ($elements.Count -gt 0) { break }
}
if (-not $process.HasExited) {
    # The first automation provider to appear is often the console window;
    # allow the QQuickWindow to finish showing before recording the UI.
    Start-Sleep -Seconds 8
    $elements = @(Get-AppAutomationElements -ProcessId $process.Id)
}

$tree = foreach ($element in $elements) {
    try {
        [pscustomobject]@{
            Type = $element.Current.ControlType.ProgrammaticName
            Name = $element.Current.Name
            AutomationId = $element.Current.AutomationId
            ClassName = $element.Current.ClassName
            Bounds = $element.Current.BoundingRectangle.ToString()
        }
    } catch { }
}
$tree | Export-Csv -LiteralPath (Join-Path $evidenceRoot "ui-tree.csv") -NoTypeInformation -Encoding UTF8
Save-Desktop -Path (Join-Path $evidenceRoot "desktop.png")

"UIA_ELEMENT_COUNT=$($elements.Count)`nAPP_STDOUT=$stdout`nAPP_STDERR=$stderr" | Add-Content -LiteralPath $summary
if ($process.HasExited) {
    "APP_EXITED_BEFORE_INTERACTION=$($process.ExitCode)" | Add-Content -LiteralPath $summary
} else {
    $windows = @($elements | Where-Object {
        try { $_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Window } catch { $false }
    })
    foreach ($window in $windows) {
        try {
            $windowPattern = $null
            if ($window.TryGetCurrentPattern([System.Windows.Automation.WindowPattern]::Pattern, [ref]$windowPattern)) {
                $windowPattern.Close()
            }
        } catch { }
    }
    $process.WaitForExit(15000) | Out-Null
    $process.Refresh()
    if (Test-Path -LiteralPath (Join-Path $env:LOCALAPPDATA "New Manga\library.db")) {
        Copy-Item -LiteralPath (Join-Path $env:LOCALAPPDATA "New Manga\library.db") -Destination (Join-Path $evidenceRoot "library.db")
    }
    if ($process.HasExited) { "APP_EXIT_CODE=$($process.ExitCode)" | Add-Content -LiteralPath $summary }
    else { "APP_EXIT_CODE=STILL_RUNNING" | Add-Content -LiteralPath $summary }
}

"DONE_UTC=$([DateTime]::UtcNow.ToString('o'))" | Add-Content -LiteralPath $summary
