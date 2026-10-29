# V11R-INT-2 evidence curation (R-19: this explicit command is the only writer of repo evidence)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path

$env:NEWMANGA_EVIDENCE_SYNC = '1'
# Keep the manually captured real-window evidence (real sidecar) and the L4 pre-fix reference;
# only regenerate the headless screenshots produced by the Int2_ tests.
Get-ChildItem (Join-Path $PSScriptRoot 'screens') -File -Filter '*.png' -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -notlike 'int2-real-*' -and $_.Name -notlike 'pre-fix-*' } |
    Remove-Item -Force

Push-Location (Join-Path $repoRoot 'apps\desktop-avalonia')
try {
    dotnet test tests\NewManga.App.Tests\NewManga.App.Tests.csproj `
        --filter "FullyQualifiedName~Int2_" `
        --nologo 2>&1 | Tee-Object -FilePath (Join-Path $PSScriptRoot 'test.log')
    if ($LASTEXITCODE -ne 0) { throw "curation test run failed (exit $LASTEXITCODE)" }
}
finally {
    Pop-Location
}

$headless = (Get-ChildItem (Join-Path $PSScriptRoot 'screens') -File -Filter '*.png' |
    Where-Object { $_.Name -notlike 'int2-real-*' -and $_.Name -notlike 'pre-fix-*' }).Count
$real = (Get-ChildItem (Join-Path $PSScriptRoot 'screens') -File -Filter 'int2-real-*').Count
if ($headless -lt 6) { throw "evidence incomplete: $headless headless screenshots (expected >= 6)" }
if ($real -lt 2) { throw "evidence incomplete: $real real-window screenshots (expected >= 2)" }
Write-Host "curated $headless headless + $real real-window INT-2 screenshots into $PSScriptRoot"
