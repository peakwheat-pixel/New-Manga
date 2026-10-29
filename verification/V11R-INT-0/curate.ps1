# V11R-INT-0 evidence curation (R-19: this explicit command is the only writer of repo evidence)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path

$env:NEWMANGA_EVIDENCE_SYNC = '1'
Remove-Item (Join-Path $PSScriptRoot 'screens') -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $PSScriptRoot 'test.log') -Force -ErrorAction SilentlyContinue

Push-Location (Join-Path $repoRoot 'apps\desktop-avalonia')
try {
    dotnet test tests\NewManga.App.Tests\NewManga.App.Tests.csproj `
        --filter "FullyQualifiedName~Int0_" `
        --nologo 2>&1 | Tee-Object -FilePath (Join-Path $PSScriptRoot 'test.log')
    if ($LASTEXITCODE -ne 0) { throw "curation test run failed (exit $LASTEXITCODE)" }
}
finally {
    Pop-Location
}

$screens = (Get-ChildItem (Join-Path $PSScriptRoot 'screens') -File -ErrorAction SilentlyContinue).Count
if ($screens -lt 6) { throw "evidence incomplete: $screens screenshots (expected >= 6 INT-0 screens)" }
Write-Host "curated $screens INT-0 screenshots into $PSScriptRoot"
