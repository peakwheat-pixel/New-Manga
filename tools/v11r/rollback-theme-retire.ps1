#Requires -Version 7.0
<#
.SYNOPSIS
  V11R-C-3 rollback procedure for the legacy-theme retirement.

.DESCRIPTION
  Restores the pre-retirement code and (optionally) the persisted theme settings, then runs a build and
  a settings-parse smoke check. Designed for the C-3 operator:

    git tag v11r-pre-retire            # once, before starting C-3 (R1)
    pwsh -NoProfile -File tools/v11r/rollback-theme-retire.ps1 -DryRun                 # verify plan
    pwsh -NoProfile -File tools/v11r/rollback-theme-retire.ps1 -CreateTag             # R1
    # ... C-3 deletion steps R3-R6 ...
    pwsh -NoProfile -File tools/v11r/rollback-theme-retire.ps1                        # rollback
    pwsh -NoProfile -File tools/v11r/rollback-theme-retire.ps1 -Mode reset -Force     # destructive reset

  Default mode is non-destructive: it creates a `rollback/v11r-c3-<timestamp>` branch at the tag and
  switches to it, leaving the current branch untouched. `-Mode reset` requires `-Force` and is intended
  only for the main checkout when the team explicitly decided to abandon the retirement work.

  The script never pushes and never edits evidence files. Artefacts (settings backup, build log, report)
  are written to -ArtifactDirectory (default: %TEMP%\v11r-c3-rollback\<timestamp>).
#>
[CmdletBinding()]
param(
    [string]$RepositoryRoot = '',
    [string]$Tag = 'v11r-pre-retire',
    [string]$ArtifactDirectory = '',
    [string]$SettingsPath = '',
    [switch]$RestoreSettings,
    [switch]$ResetSettings,
    [ValidateSet('checkout', 'reset')]
    [string]$Mode = 'checkout',
    [switch]$Force,
    [switch]$CreateTag,
    [switch]$SkipBuild,
    [switch]$DryRun,
    [switch]$AllowDirty
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($RepositoryRoot)) {
    $RepositoryRoot = (& git rev-parse --show-toplevel).Trim()
}
else {
    $RepositoryRoot = (Resolve-Path -LiteralPath $RepositoryRoot).Path
}
if ([string]::IsNullOrWhiteSpace($SettingsPath)) {
    $SettingsPath = Join-Path ([Environment]::GetFolderPath('ApplicationData')) 'NewManga/theme-settings.json'
}
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
if ([string]::IsNullOrWhiteSpace($ArtifactDirectory)) {
    $ArtifactDirectory = Join-Path ([System.IO.Path]::GetTempPath()) "v11r-c3-rollback/$timestamp"
}
$ArtifactDirectory = [System.IO.Path]::GetFullPath($ArtifactDirectory)

function Invoke-Git([string[]]$Arguments) {
    $output = & git -C $RepositoryRoot @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) { throw "git $($Arguments -join ' ') failed: $output" }
    return $output
}

$head = (& git -C $RepositoryRoot rev-parse HEAD).Trim()
$branch = (& git -C $RepositoryRoot rev-parse --abbrev-ref HEAD).Trim()
$dirty = ((& git -C $RepositoryRoot status --porcelain | Out-String).Trim().Length -gt 0)
$tagExists = $false
if (-not $CreateTag) {
    & git -C $RepositoryRoot rev-parse -q --verify "refs/tags/$Tag" > $null 2>&1
    $tagExists = ($LASTEXITCODE -eq 0)
}

$actions = [System.Collections.Generic.List[string]]::new()
if ($CreateTag) {
    $actions.Add("git tag -a $Tag -m 'V11R pre-retire rollback point'")
}
elseif (-not $tagExists) {
    throw "rollback tag '$Tag' does not exist; create it with -CreateTag before starting C-3"
}

if ($dirty -and -not $AllowDirty -and -not $DryRun) {
    throw "working tree is dirty; commit/stash first or pass -AllowDirty (rollback would mix local changes)"
}
if ($Mode -eq 'reset' -and -not $Force) {
    throw "refusing to reset --hard without -Force; use the default checkout mode or pass -Force explicitly"
}

if ($RestoreSettings) {
    $backupPattern = Join-Path $ArtifactDirectory 'theme-settings.*.json'
    $backup = Get-ChildItem -Path $backupPattern -File -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -eq $backup) {
        throw "-RestoreSettings requested but no theme-settings backup exists in $ArtifactDirectory"
    }

    $actions.Add("restore settings: $($backup.FullName) -> $SettingsPath")
}
if ($ResetSettings) {
    $actions.Add("reset settings to shipped default: $SettingsPath")
}

$actions.Add("backup settings: $SettingsPath -> $ArtifactDirectory (when the file exists)")
if ($Mode -eq 'checkout') {
    $actions.Add("git switch --create rollback/v11r-c3-$timestamp $Tag")
}
else {
    $actions.Add("git reset --hard $Tag")
}
if (-not $SkipBuild) {
    $actions.Add("dotnet build apps/desktop-avalonia/src/NewManga.App/NewManga.App.csproj -warnaserror")
}
$actions.Add('verify old theme symbols are back: git grep ThemePackService (count > 0)')
$actions.Add('verify settings JSON parses; write report.json')

if ($DryRun) {
    Write-Output 'DRY RUN - no files, refs or settings are changed.'
    Write-Output "repo   : $RepositoryRoot"
    Write-Output "branch : $branch @ $head"
    Write-Output "dirty  : $dirty"
    Write-Output "tag    : $Tag (exists=$tagExists)"
    foreach ($action in $actions) { Write-Output "  - $action" }
    return
}

New-Item -ItemType Directory -Path $ArtifactDirectory -Force | Out-Null

# 1. Back up the persisted theme settings before anything else changes.
$settingsBackup = $null
if (Test-Path -LiteralPath $SettingsPath) {
    $settingsBackup = Join-Path $ArtifactDirectory "theme-settings.$timestamp.json"
    Copy-Item -LiteralPath $SettingsPath -Destination $settingsBackup -Force
}
else {
    Set-Content -LiteralPath (Join-Path $ArtifactDirectory 'theme-settings.missing.txt') -Value 'settings file did not exist before rollback'
}

# 2. Create the tag when requested (R1), otherwise verify it.
if ($CreateTag) {
    & git -C $RepositoryRoot tag -a $Tag -m 'V11R pre-retire rollback point' $head
    if ($LASTEXITCODE -ne 0) { throw "failed to create tag '$Tag'" }
    $tagExists = $true
}

# 3. Roll the code back (non-destructive by default).
$rollbackBranch = "rollback/v11r-c3-$timestamp"
if ($Mode -eq 'checkout') {
    & git -C $RepositoryRoot switch --create $rollbackBranch $Tag
    if ($LASTEXITCODE -ne 0) { throw "failed to switch to rollback branch '$rollbackBranch'" }
}
else {
    & git -C $RepositoryRoot reset --hard $Tag
    if ($LASTEXITCODE -ne 0) { throw "failed to reset to tag '$Tag'" }
}

# 4. Restore or reset the persisted settings when requested.
if ($RestoreSettings) {
    $directory = Split-Path -Parent $SettingsPath
    if (-not [string]::IsNullOrWhiteSpace($directory)) { New-Item -ItemType Directory -Path $directory -Force | Out-Null }
    Copy-Item -LiteralPath $settingsBackup -Destination $SettingsPath -Force
}
elseif ($ResetSettings) {
    $directory = Split-Path -Parent $SettingsPath
    if (-not [string]::IsNullOrWhiteSpace($directory)) { New-Item -ItemType Directory -Path $directory -Force | Out-Null }
    Set-Content -LiteralPath $SettingsPath -Encoding utf8 -Value @'
{
  "schema": "newmanga.theme-settings/1",
  "themeId": "newmanga-default",
  "appearance": "system"
}
'@
}

# 5. Smoke checks: build, old-symbol presence, settings parse.
$buildExitCode = $null
$buildLog = Join-Path $ArtifactDirectory 'build.log'
if (-not $SkipBuild) {
    $buildOutput = & dotnet build (Join-Path $RepositoryRoot 'apps/desktop-avalonia/src/NewManga.App/NewManga.App.csproj') -warnaserror 2>&1
    $buildExitCode = $LASTEXITCODE
    [System.IO.File]::WriteAllText($buildLog, ($buildOutput | Out-String), [System.Text.UTF8Encoding]::new($false))
    if ($buildExitCode -ne 0) {
        throw "rollback build failed (see $buildLog)"
    }
}

$themeReferences = (& git -C $RepositoryRoot grep -c -E '\bThemePackService\b' -- 'apps/desktop-avalonia/src' 2>$null | Out-String)
$settingsParseOk = $true
$settingsParseError = $null
if (Test-Path -LiteralPath $SettingsPath) {
    try {
        Get-Content -LiteralPath $SettingsPath -Raw | ConvertFrom-Json | Out-Null
    }
    catch {
        $settingsParseOk = $false
        $settingsParseError = $_.Exception.Message
    }
}

$finalHead = (& git -C $RepositoryRoot rev-parse HEAD).Trim()
$report = [ordered]@{
    schema            = 'newmanga.v11r.c3-rollback/1'
    task              = 'V11R-C-3'
    executedAt        = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
    repository        = $RepositoryRoot
    previousBranch    = $branch
    previousHead      = $head
    tag               = $Tag
    tagCommit         = (& git -C $RepositoryRoot rev-parse "$Tag^{commit}").Trim()
    mode              = $Mode
    rollbackBranch    = if ($Mode -eq 'checkout') { $rollbackBranch } else { $null }
    finalHead         = $finalHead
    settingsPath      = $SettingsPath
    settingsBackup    = $settingsBackup
    settingsRestored  = [bool]$RestoreSettings
    settingsReset     = [bool]$ResetSettings
    settingsParses    = $settingsParseOk
    settingsParseError = $settingsParseError
    buildSkipped      = [bool]$SkipBuild
    buildExitCode     = $buildExitCode
    oldThemeReferences = $themeReferences.Trim()
    artifactDirectory = $ArtifactDirectory
}
$reportPath = Join-Path $ArtifactDirectory 'report.json'
[System.IO.File]::WriteAllText($reportPath, ($report | ConvertTo-Json -Depth 4) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))

Write-Output 'ROLLBACK COMPLETE'
Write-Output "  final HEAD : $finalHead"
Write-Output "  branch     : $(if ($Mode -eq 'checkout') { $rollbackBranch } else { $branch })"
Write-Output "  settings   : $SettingsPath (parses=$settingsParseOk)"
Write-Output "  old refs   : $($themeReferences.Trim())"
Write-Output "  artifacts  : $ArtifactDirectory"
if ($buildExitCode -ne $null) { Write-Output "  build      : exit=$buildExitCode" }
