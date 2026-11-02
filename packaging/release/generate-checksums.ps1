# RELEASE-VERIFY-1: generate a standard SHA256SUMS manifest for the 0.1.0 release artifacts.
#
# The artifacts are large (~900 MB total) and live outside the repository, so this script only
# READS + hashes them; it never copies them into the repo. The manifest stores file names only
# (<sha256>  <filename>), which keeps SHA256SUMS portable while the sidecar JSON records the
# byte sizes, source paths and release version for audit.
#
# Usage (all explicit):
#   pwsh -NoProfile -File packaging/release/generate-checksums.ps1 `
#     -BaseZip <NewManga-0.1.0-win-x64.zip> `
#     -ModelsZip <NewManga-0.1.0-win-x64-models.zip> `
#     -SetupExe <NewManga-0.1.0-setup.exe>
#
# Usage (staged directory, standard file names):
#   pwsh -NoProfile -File packaging/release/generate-checksums.ps1 -ArtifactDir <dir>
#
# With no path arguments the script falls back to the known task-env locations produced by
# AGPL-RELEASE-1 / NSIS-INSTALLER-1.
[CmdletBinding()]
param(
    [string]$BaseZip = '',
    [string]$ModelsZip = '',
    [string]$SetupExe = '',
    [string]$ArtifactDir = '',
    [string]$OutFile = '',
    [string]$JsonOutFile = '',
    [string]$Release = '0.1.0',
    [switch]$NoWrite
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$releaseDir = $PSScriptRoot
$repoRoot = (Resolve-Path (Join-Path $releaseDir '..\..')).Path

$defaultBase = $( $v11rRepo = (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent); if ($env:NEWMANGA_WORKSPACE_ROOT) { Join-Path $env:NEWMANGA_WORKSPACE_ROOT 'task-envs/AGPL-RELEASE-1/out/NewManga-0.1.0-win-x64.zip' } else { Join-Path (Join-Path (Split-Path $v11rRepo -Parent) ((Split-Path $v11rRepo -Leaf) + '.workspace')) 'task-envs/AGPL-RELEASE-1/out/NewManga-0.1.0-win-x64.zip' } )
$defaultModels = $( $v11rRepo = (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent); if ($env:NEWMANGA_WORKSPACE_ROOT) { Join-Path $env:NEWMANGA_WORKSPACE_ROOT 'task-envs/AGPL-RELEASE-1/out/NewManga-0.1.0-win-x64-models.zip' } else { Join-Path (Join-Path (Split-Path $v11rRepo -Parent) ((Split-Path $v11rRepo -Leaf) + '.workspace')) 'task-envs/AGPL-RELEASE-1/out/NewManga-0.1.0-win-x64-models.zip' } )
$defaultSetup = $( $v11rRepo = (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent); if ($env:NEWMANGA_WORKSPACE_ROOT) { Join-Path $env:NEWMANGA_WORKSPACE_ROOT 'task-envs/NSIS-INSTALLER-1/out/NewManga-0.1.0-setup.exe' } else { Join-Path (Join-Path (Split-Path $v11rRepo -Parent) ((Split-Path $v11rRepo -Leaf) + '.workspace')) 'task-envs/NSIS-INSTALLER-1/out/NewManga-0.1.0-setup.exe' } )

function Resolve-Artifact([string]$Explicit, [string]$Directory, [string]$DirectoryName, [string]$Default, [string]$Role) {
    if (-not [string]::IsNullOrWhiteSpace($Explicit)) {
        if (-not (Test-Path -LiteralPath $Explicit)) { throw "artifact not found (explicit -$Role): $Explicit" }
        return (Resolve-Path -LiteralPath $Explicit).Path
    }
    if (-not [string]::IsNullOrWhiteSpace($Directory)) {
        $candidate = Join-Path $Directory $DirectoryName
        if (-not (Test-Path -LiteralPath $candidate)) { throw "artifact not found in -ArtifactDir (${Role}): $candidate" }
        return (Resolve-Path -LiteralPath $candidate).Path
    }
    if (-not (Test-Path -LiteralPath $Default)) {
        throw "artifact not found at default location ($Role): $Default. Pass -ArtifactDir or the explicit path."
    }
    return (Resolve-Path -LiteralPath $Default).Path
}

function Get-Sha256([string]$Path) {
    $stream = [System.IO.File]::OpenRead($Path)
    try {
        $sha = [System.Security.Cryptography.SHA256]::Create()
        try {
            return ([System.BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-', '').ToLowerInvariant()
        } finally { $sha.Dispose() }
    } finally { $stream.Dispose() }
}

if ([string]::IsNullOrWhiteSpace($OutFile)) {
    $OutFile = Join-Path $releaseDir 'SHA256SUMS'
} elseif (-not [System.IO.Path]::IsPathRooted($OutFile)) {
    $OutFile = Join-Path $repoRoot $OutFile
}
if ([string]::IsNullOrWhiteSpace($JsonOutFile)) {
    $JsonOutFile = "$OutFile.json"
} elseif (-not [System.IO.Path]::IsPathRooted($JsonOutFile)) {
    $JsonOutFile = Join-Path $repoRoot $JsonOutFile
}

$artifactDirFull = if ([string]::IsNullOrWhiteSpace($ArtifactDir)) { '' } else { (Resolve-Path -LiteralPath $ArtifactDir).Path }
$roles = @(
    [ordered]@{ role = 'base_zip'; name = 'NewManga-0.1.0-win-x64.zip'; path = (Resolve-Artifact -Explicit $BaseZip -Directory $artifactDirFull -DirectoryName 'NewManga-0.1.0-win-x64.zip' -Default $defaultBase -Role 'BaseZip') },
    [ordered]@{ role = 'models_zip'; name = 'NewManga-0.1.0-win-x64-models.zip'; path = (Resolve-Artifact -Explicit $ModelsZip -Directory $artifactDirFull -DirectoryName 'NewManga-0.1.0-win-x64-models.zip' -Default $defaultModels -Role 'ModelsZip') },
    [ordered]@{ role = 'setup_exe'; name = 'NewManga-0.1.0-setup.exe'; path = (Resolve-Artifact -Explicit $SetupExe -Directory $artifactDirFull -DirectoryName 'NewManga-0.1.0-setup.exe' -Default $defaultSetup -Role 'SetupExe') }
)

$entries = New-Object System.Collections.Generic.List[object]
foreach ($artifact in $roles) {
    $item = Get-Item -LiteralPath $artifact.path
    Write-Host ("hashing {0} ({1:N0} bytes) ..." -f $item.Name, $item.Length)
    $sha = Get-Sha256 $item.FullName
    $entries.Add([ordered]@{
        role = $artifact.role
        filename = $item.Name
        bytes = $item.Length
        mb = [math]::Round($item.Length / 1MB, 2)
        sha256 = $sha
        source_path = $item.FullName
    })
}

# Standard sha256sum order: file names in ordinal (byte) order.
$byName = @{}
foreach ($entry in $entries) { $byName[[string]$entry.filename] = $entry }
$names = [string[]]@($byName.Keys)
[Array]::Sort($names, [System.StringComparer]::Ordinal)
$ordered = New-Object System.Collections.Generic.List[object]
foreach ($name in $names) { $ordered.Add($byName[$name]) }
$manifestLines = ($ordered | ForEach-Object { "$($_.sha256)  $($_.filename)" }) -join "`n"
$manifestText = $manifestLines + "`n"

$sidecar = [ordered]@{
    task = 'RELEASE-VERIFY-1'
    release = $Release
    format = 'sha256sum'
    separator = 'two spaces (sha256sum compatible)'
    artifacts = $ordered
    total_bytes = ($ordered | ForEach-Object { $_.bytes } | Measure-Object -Sum).Sum
    generated_at_utc = [DateTime]::UtcNow.ToString('o')
}

Write-Host ''
Write-Host '--- SHA256SUMS ---'
Write-Host $manifestText.TrimEnd()
Write-Host ''

if (-not $NoWrite) {
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [IO.File]::WriteAllText($OutFile, $manifestText, $utf8)
    [IO.File]::WriteAllText($JsonOutFile, (($sidecar | ConvertTo-Json -Depth 6) + "`n"), $utf8)
    Write-Host ("wrote: {0}" -f $OutFile)
    Write-Host ("wrote: {0}" -f $JsonOutFile)
}
$sidecar | ConvertTo-Json -Depth 6
