<#
.SYNOPSIS
    Build the per-user, unsigned NSIS installer (NSIS-INSTALLER-1) from the packaged base stage.

.DESCRIPTION
    Packages the AGPL-RELEASE-1 base stage (app + bundled Core sidecar + the four license files +
    installer docs) into NewManga-<version>-setup.exe. The installer itself installs per-user to
    %LOCALAPPDATA%\Programs\NewManga, writes an HKCU uninstall entry, creates Start Menu shortcuts
    and supports /S silent install + silent uninstall. It never touches the user data root
    %APPDATA%\com.newmanga.desktop and never writes HKLM/Program Files.

    The setup.exe is a build artifact and deliberately NOT written inside the repository: -OutDir
    must point outside the repo (the default is the task env), and the script records
    bytes/sha256/Authenticode status in build-info.json for the evidence pins.

.PARAMETER StageDir
    Packaged base stage directory (defaults to the AGPL-RELEASE-1 base stage output).

.PARAMETER MakensisPath
    Path to makensis.exe. When omitted the script probes $env:NEWMANGA_MAKENSIS,
    %LOCALAPPDATA%\tauri\NSIS\makensis.exe and the NSIS installer locations; a clear error is raised
    when none exists.

.PARAMETER OutDir
    Directory that receives NewManga-<version>-setup.exe, the NSIS build log and build-info.json.
    Must be outside the repository; defaults to the NSIS-INSTALLER-1 task env.

.PARAMETER Version
    Package version (defaults to <StageDir>\VERSION.json version).

.PARAMETER NsiScript
    Installer script (defaults to packaging/nsis/installer.nsi).

.PARAMETER IconPath
    Optional .ico used for the installer/shortcut icon (defaults to the in-repo app icon when it
    exists; the installer falls back to the stock NSIS icon otherwise).
#>
[CmdletBinding()]
param(
    [string]$StageDir = 'G:/CODEX/New Manga.workspace/task-envs/AGPL-RELEASE-1/out/NewManga-0.1.0-win-x64',
    [string]$MakensisPath = '',
    [string]$OutDir = 'G:/CODEX/New Manga.workspace/task-envs/NSIS-INSTALLER-1/out',
    [string]$Version = '',
    [string]$NsiScript = '',
    [string]$IconPath = ''
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$scriptRoot = $PSScriptRoot
$repo = (Resolve-Path (Join-Path $scriptRoot '..\..\..')).Path
if ([string]::IsNullOrWhiteSpace($NsiScript)) { $NsiScript = Join-Path $repo 'packaging/nsis/installer.nsi' }
if ([string]::IsNullOrWhiteSpace($IconPath)) {
    $candidate = Join-Path $repo 'apps/desktop/src-tauri/icons/icon.ico'
    if (Test-Path -LiteralPath $candidate) { $IconPath = $candidate }
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Resolve-Makensis([string]$Explicit) {
    if (-not [string]::IsNullOrWhiteSpace($Explicit)) {
        if (-not (Test-Path -LiteralPath $Explicit)) { throw "makensis.exe not found at -MakensisPath: $Explicit" }
        return (Resolve-Path -LiteralPath $Explicit).Path
    }
    $candidates = New-Object System.Collections.Generic.List[string]
    if (-not [string]::IsNullOrWhiteSpace($env:NEWMANGA_MAKENSIS)) { $candidates.Add($env:NEWMANGA_MAKENSIS) }
    if (-not [string]::IsNullOrWhiteSpace($env:LOCALAPPDATA)) {
        $candidates.Add((Join-Path $env:LOCALAPPDATA 'tauri\NSIS\makensis.exe'))
    }
    if (-not [string]::IsNullOrWhiteSpace($env:ProgramFiles)) {
        $candidates.Add((Join-Path $env:ProgramFiles 'NSIS\makensis.exe'))
    }
    if (-not [string]::IsNullOrWhiteSpace(${env:ProgramFiles(x86)})) {
        $candidates.Add((Join-Path ${env:ProgramFiles(x86)} 'NSIS\makensis.exe'))
    }
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) { return (Resolve-Path -LiteralPath $candidate).Path }
    }
    $probed = ($candidates -join '; ')
    throw "makensis.exe was not found. Probe order: $probed. Install NSIS 3.x or pass -MakensisPath <makensis.exe> (e.g. the portable NSIS shipped with the Tauri cache)."
}

# ---- validate inputs ---------------------------------------------------------
if (-not (Test-Path -LiteralPath $StageDir)) { throw "StageDir does not exist: $StageDir" }
$stageFull = (Resolve-Path -LiteralPath $StageDir).Path
$requiredFiles = @(
    'app/NewManga.App.exe',
    'app/core-sidecar/core_service.exe',
    'install.ps1',
    'uninstall.ps1',
    'LICENSE',
    'LICENSE-AGPL-3.0.txt',
    'NOTICE.md',
    'THIRD_PARTY_LICENSES.md',
    'LICENSE_AUDIT.md',
    'UPGRADE.md',
    'MANUAL_VERIFY.md',
    'VERSION.json',
    'package-manifest.json'
)
$missing = @($requiredFiles | Where-Object { -not (Test-Path -LiteralPath (Join-Path $stageFull $_)) })
if ($missing.Count -gt 0) { throw "StageDir is missing required files: $($missing -join ', ')" }
if (-not (Test-Path -LiteralPath $NsiScript)) { throw "NSIS script not found: $NsiScript" }

$versionJson = Get-Content -LiteralPath (Join-Path $stageFull 'VERSION.json') -Raw | ConvertFrom-Json
if ([string]::IsNullOrWhiteSpace($Version)) {
    if ([string]::IsNullOrWhiteSpace([string]$versionJson.version)) { throw 'VERSION.json has no version and -Version was not supplied' }
    $Version = [string]$versionJson.version
}
if ($Version -notmatch '^\d+\.\d+\.\d+$') { throw "Version must be x.y.z (got '$Version')" }
$Version4 = "$Version.0"

$outFull = [IO.Path]::GetFullPath($OutDir)
$repoFull = [IO.Path]::GetFullPath($repo).TrimEnd('\')
if ($outFull.TrimEnd('\') -ieq $repoFull -or $outFull.StartsWith($repoFull + '\', [StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to write the installer into the repository: -OutDir '$OutDir'. Build artifacts belong in the task env; pass -OutDir outside the repo."
}
New-Item -ItemType Directory -Force -Path $outFull | Out-Null

$makensis = Resolve-Makensis $MakensisPath
$makensisVersion = (& $makensis /VERSION 2>&1 | Out-String).Trim()
if ($LASTEXITCODE -ne 0) { throw "makensis /VERSION failed (exit $LASTEXITCODE): $makensisVersion" }
if ($makensisVersion -notmatch 'v3\.\d+') { throw "Unsupported makensis version '$makensisVersion' (NSIS 3.x required)" }
$makensisSha256 = Get-Sha256 $makensis

# ---- stage fingerprint -------------------------------------------------------
$stageFiles = Get-ChildItem -LiteralPath $stageFull -Recurse -File
$stageFileCount = @($stageFiles).Count
$stageBytes = ($stageFiles | Measure-Object -Property Length -Sum).Sum
$stageLines = New-Object System.Collections.Generic.List[string]
foreach ($file in $stageFiles | Sort-Object FullName) {
    $relative = $file.FullName.Substring($stageFull.Length + 1).Replace('\', '/')
    $stageLines.Add("$relative`t$($file.Length)`t$(Get-Sha256 $file.FullName)")
}
$stageManifestText = ($stageLines -join "`n") + "`n"
$stageManifestSha256 = [System.Convert]::ToHexString(
    [System.Security.Cryptography.SHA256]::HashData([System.Text.Encoding]::UTF8.GetBytes($stageManifestText))
).ToLowerInvariant()
$installSizeKb = [int][math]::Ceiling($stageBytes / 1KB)

# ---- run makensis ------------------------------------------------------------
$exePath = Join-Path $outFull "NewManga-$Version-setup.exe"
$logPath = Join-Path $outFull 'build-installer.log'
$buildInfoPath = Join-Path $outFull 'build-info.json'
if (Test-Path -LiteralPath $exePath) { Remove-Item -LiteralPath $exePath -Force }

$argsList = @(
    "/DVERSION=$Version",
    "/DVERSION4=$Version4",
    "/DSTAGE_DIR=$stageFull",
    "/DOUT_FILE=$exePath",
    "/DINSTALL_SIZE_KB=$installSizeKb",
    "/DLICENSE_FILE=$(Join-Path $stageFull 'NOTICE.md')"
)
if (-not [string]::IsNullOrWhiteSpace($IconPath) -and (Test-Path -LiteralPath $IconPath)) {
    $argsList += "/DICON_FILE=$((Resolve-Path -LiteralPath $IconPath).Path)"
}
$argsList += $NsiScript

Write-Host ("makensis {0} ({1} bytes, sha256 {2})" -f $makensisVersion, (Get-Item $makensis).Length, $makensisSha256)
Write-Host ("stage: {0} files / {1} bytes / manifest sha256 {2}" -f $stageFileCount, $stageBytes, $stageManifestSha256)
Write-Host ("building NewManga-{0}-setup.exe into {1}" -f $Version, $outFull)

$started = Get-Date
& $makensis @argsList 2>&1 | Tee-Object -FilePath $logPath | Out-Host
$exitCode = $LASTEXITCODE
$elapsedSeconds = [math]::Round(((Get-Date) - $started).TotalSeconds, 2)
if ($exitCode -ne 0) {
    $tail = (Get-Content -LiteralPath $logPath -Tail 25) -join "`n"
    throw "makensis failed (exit $exitCode) after $elapsedSeconds s. Log tail:`n$tail"
}
if (-not (Test-Path -LiteralPath $exePath)) { throw "makensis reported success but the installer is missing: $exePath" }

$installer = Get-Item -LiteralPath $exePath
$installerSha256 = Get-Sha256 $exePath
$signature = Get-AuthenticodeSignature -LiteralPath $exePath
$fileVersion = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($exePath)

$buildInfo = [ordered]@{
    task = 'NSIS-INSTALLER-1'
    variant = 'base'
    version = $Version
    version4 = $Version4
    installer = [ordered]@{
        path = $exePath
        file_name = $installer.Name
        bytes = $installer.Length
        mb = [math]::Round($installer.Length / 1MB, 2)
        sha256 = $installerSha256
        build_seconds = $elapsedSeconds
        authenticode_status = [string]$signature.Status
        file_version = [string]$fileVersion.FileVersion
        product_name = [string]$fileVersion.ProductName
        product_version = [string]$fileVersion.ProductVersion
        description = [string]$fileVersion.FileDescription
    }
    stage = [ordered]@{
        path = $stageFull
        file_count = $stageFileCount
        bytes = $stageBytes
        mb = [math]::Round($stageBytes / 1MB, 2)
        manifest_sha256 = $stageManifestSha256
        install_size_kb = $installSizeKb
        version_json = [ordered]@{
            version = [string]$versionJson.version
            variant = [string]$versionJson.variant
            license = [string]$versionJson.license
        }
    }
    toolchain = [ordered]@{
        makensis = $makensis
        makensis_version = $makensisVersion
        makensis_sha256 = $makensisSha256
        nsi_script = (Resolve-Path -LiteralPath $NsiScript).Path
        icon = $IconPath
    }
    generated_at_utc = [DateTime]::UtcNow.ToString('o')
}
$buildInfo | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $buildInfoPath -Encoding utf8

Write-Host ("installer: {0} ({1:N0} bytes, {2} MB)" -f $exePath, $installer.Length, $buildInfo.installer.mb)
Write-Host ("sha256: {0}" -f $installerSha256)
Write-Host ("authenticode: {0} (unsigned release by design)" -f $signature.Status)
Write-Host ("build info: {0}" -f $buildInfoPath)
$buildInfo | ConvertTo-Json -Depth 6
