param(
    [string]$RepoRoot = 'G:\CODEX\New Manga'
)

$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$outDir = Join-Path $RepoRoot "verification\P20\gate-$ts"
Write-Host "Starting AC7 release gate into: $outDir"

Push-Location $RepoRoot
try {
    & pwsh -NoProfile -File 'verification\P19\rebuild-and-verify.ps1' -RepoRoot $RepoRoot -OutDir $outDir
    $code = $LASTEXITCODE
} finally {
    Pop-Location
}

Write-Host "Finished AC7 release gate with exit code: $code"
Write-Host "OutDir: $outDir"
exit $code
