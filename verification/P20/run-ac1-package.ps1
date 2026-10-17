# P20 AC1: produce a distributable Windows installer via Tauri Bundler (NSIS per tauri.conf.json).
$ErrorActionPreference = 'Continue'
$repo = 'G:\CODEX\New Manga'
$outDir = Join-Path $repo 'verification\P20\ac1-package'
if (Test-Path $outDir) { Write-Host "REFUSE_OVERWRITE $outDir"; exit 4 }
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$log = Join-Path $outDir 'cargo-tauri-build.log'
$trace = Join-Path $outDir 'ac1-trace.log'
function T([string]$m) { $l = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss.fff'), $m; $l | Add-Content $trace -Encoding utf8; Write-Host $l }

T "AC1 start"
T ("cargo tauri version: " + ((& cargo tauri --version) -join ' '))
$tauriDir = Join-Path $repo 'apps\desktop\src-tauri'
Push-Location $tauriDir
try {
    & cargo tauri build *>> $log
    $code = $LASTEXITCODE
} finally { Pop-Location }
T "cargo tauri build exit_code=$code"

# enumerate bundle artifacts
$release = Join-Path $repo 'apps\desktop\src-tauri\target\release'
$bundle = Join-Path $release 'bundle'
$arts = @()
if (Test-Path $bundle) { $arts = @(Get-ChildItem $bundle -Recurse -File -Include *.exe,*.msi,*.zip -ErrorAction SilentlyContinue) }
foreach ($a in $arts) {
    T ("ARTIFACT " + $a.FullName.Replace($repo + '\','') + " bytes=" + $a.Length + " sha256=" + (Get-FileHash $a.FullName -Algorithm SHA256).Hash.ToLower())
}
$exe = Join-Path $release 'm2rc1-desktop.exe'
if (Test-Path $exe) { T ("RELEASE_EXE bytes=" + (Get-Item $exe).Length + " sha256=" + (Get-FileHash $exe -Algorithm SHA256).Hash.ToLower()) }
@(
    "runner=run-ac1-package.ps1"
    "cargo_tauri_build_exit=$code"
    "artifact_count=$($arts.Count)"
    "started=$(Get-Date -Format o)"
) | Set-Content (Join-Path $outDir 'ac1-metadata.txt') -Encoding utf8
T ("AC1 END exit_code=" + $(if ($code -ne 0) { 1 } else { 0 }) + " artifacts=" + $arts.Count)
exit ([int]($code -ne 0))
