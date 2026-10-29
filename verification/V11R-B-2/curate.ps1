# V11R-B-2 evidence curation (R-19: this explicit command is the only writer of repo evidence)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path

$env:NEWMANGA_EVIDENCE_SYNC = '1'
Remove-Item (Join-Path $PSScriptRoot 'screens') -Recurse -Force -ErrorAction SilentlyContinue

Push-Location (Join-Path $repoRoot 'apps\desktop-avalonia')
try {
    dotnet test tests\NewManga.App.Tests\NewManga.App.Tests.csproj `
        --filter "FullyQualifiedName~V2ConsoleUiTests" `
        --nologo 2>&1 | Tee-Object -FilePath (Join-Path $PSScriptRoot 'test.log')
    if ($LASTEXITCODE -ne 0) { throw "curation test run failed (exit $LASTEXITCODE)" }
}
finally {
    Pop-Location
}

$screens = (Get-ChildItem (Join-Path $PSScriptRoot 'screens') -File -ErrorAction SilentlyContinue).Count
if ($screens -lt 8) { throw "evidence incomplete: $screens screenshots (expected >= 8 B-2 screens)" }
Write-Host "curated $screens B-2 screenshots + conformance inventory into $PSScriptRoot"
