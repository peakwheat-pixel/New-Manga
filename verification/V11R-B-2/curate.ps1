# V11R-B-2 evidence curation (R-19: this explicit command is the only writer of repo evidence)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path

$env:NEWMANGA_EVIDENCE_SYNC = '1'
# B-2 reuses the shared conformance inventory scan (V2ConformanceTests) but targets its own evidence dir.
$env:NEWMANGA_EVIDENCE_TASK = 'V11R-B-2'
Remove-Item (Join-Path $PSScriptRoot 'screens') -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $PSScriptRoot 'conformance') -Recurse -Force -ErrorAction SilentlyContinue

Push-Location (Join-Path $repoRoot 'apps\desktop-avalonia')
try {
    dotnet test tests\NewManga.App.Tests\NewManga.App.Tests.csproj `
        --filter "FullyQualifiedName~V2ConsoleUiTests|FullyQualifiedName~V2ConformanceTests" `
        --nologo 2>&1 | Tee-Object -FilePath (Join-Path $PSScriptRoot 'test.log')
    if ($LASTEXITCODE -ne 0) { throw "curation test run failed (exit $LASTEXITCODE)" }
}
finally {
    Pop-Location
}

$screens = (Get-ChildItem (Join-Path $PSScriptRoot 'screens') -File -ErrorAction SilentlyContinue).Count
$conformance = Test-Path (Join-Path $PSScriptRoot 'conformance\v2-tokens-and-classes.json')
if ($screens -lt 8) { throw "evidence incomplete: $screens screenshots (expected >= 8 B-2 screens)" }
if (-not $conformance) { throw "evidence incomplete: conformance/v2-tokens-and-classes.json missing" }
Write-Host "curated $screens B-2 screenshots + conformance inventory into $PSScriptRoot"
