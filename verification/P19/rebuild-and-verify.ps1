# Rebuild the product from the current main checkout and enforce the P20 release gate:
#   frontend build -> frozen sidecar -> cargo build -> bundle==resource SHA256 -> startup smoke.
# Implements R3-005 infrastructure: fresh timestamped output dir, refuse-overwrite,
# assertion counters, non-zero exit when any gate step fails.
# NOTE: apps/desktop/src-tauri/target/core-sidecar is a Junction shared with linked
# worktrees, so the sidecar artifact is shared; this script still refreshes target/debug.
param(
  [string]$RepoRoot = 'G:/CODEX/New Manga',
  [string]$OutDir,
  [switch]$AllowOverwrite,
  [switch]$SkipSmoke,
  [int]$SmokeWaitSeconds = 45
)
$ErrorActionPreference = 'Continue'
Add-Type -AssemblyName System.Drawing -ErrorAction SilentlyContinue
Add-Type -AssemblyName UIAutomationClient -ErrorAction SilentlyContinue
Add-Type -AssemblyName UIAutomationTypes -ErrorAction SilentlyContinue

if (-not $OutDir) { $OutDir = Join-Path $RepoRoot ('verification/P19/rebuild-' + (Get-Date -Format 'yyyyMMdd-HHmmss')) }
if (Test-Path $OutDir) {
  $existing = @(Get-ChildItem $OutDir -Recurse -File -ErrorAction SilentlyContinue)
  if ($existing.Count -gt 0 -and -not $AllowOverwrite) { Write-Host "REFUSING_OVERWRITE $OutDir ($($existing.Count) files)"; exit 4 }
} else { New-Item -ItemType Directory -Force -Path $OutDir | Out-Null }
$tr = Join-Path $OutDir 'gate-trace.log'
Remove-Item $tr -ErrorAction SilentlyContinue
$script:Checks = 0; $script:Fails = 0
function T($m){ $l='['+(Get-Date -Format 'HH:mm:ss.fff')+'] '+$m; Add-Content -Path $tr -Value $l -Encoding utf8; Write-Host $l }
function A($ok,$what){ $script:Checks++; if($ok){ T "ASSERT PASS $what" } else { $script:Fails++; T "ASSERT FAIL $what" } }
function Run($label,$file,$argList,$workdir){
  $log = Join-Path $OutDir "$label.log"
  "shell=PowerShell`nworkdir=$workdir`ncommand=$file $($argList -join ' ')" | Set-Content $log -Encoding utf8
  Push-Location $workdir
  try { & $file @argList *>> $log; $code = $LASTEXITCODE } finally { Pop-Location }
  "exit_code=$code" | Add-Content $log -Encoding utf8
  T "$label exit_code=$code  log=$log"
  return $code
}

$env:PYINSTALLER_CONFIG_DIR = Join-Path $env:TEMP 'newmanga-pyinstaller-cache'
New-Item -ItemType Directory -Force -Path $env:PYINSTALLER_CONFIG_DIR | Out-Null
T "START outdir=$OutDir pyinstaller_cache=$env:PYINSTALLER_CONFIG_DIR"
$meta = New-Object System.Collections.Generic.List[string]
$meta.Add('runner=rebuild-and-verify.ps1'); $meta.Add('started_local='+(Get-Date).ToString('o')); $meta.Add('outdir='+$OutDir)

# 1) frontend production build
$fe = Join-Path $RepoRoot 'apps/desktop/frontend'
$c1 = Run 'frontend-npm-build' 'npm' @('run','build') $fe
A ($c1 -eq 0) 'frontend:npm-run-build'
$meta.Add("frontend_build_exit=$c1")

# 2) frozen sidecar
$c2 = Run 'sidecar-build' 'pwsh' @('-NoProfile','-File','packaging/m2ac5/build_sidecar.ps1','-Force') $RepoRoot
A ($c2 -eq 0) 'sidecar:build'
$meta.Add("sidecar_build_exit=$c2")

# 3) cargo build (debug) — refreshes target/debug/resources
$tauri = Join-Path $RepoRoot 'apps/desktop/src-tauri'
$c3 = Run 'cargo-build' 'cargo' @('build') $tauri
A ($c3 -eq 0) 'cargo:build'
$meta.Add("cargo_build_exit=$c3")

# 4) THE GATE: bundle vs resource core_service.exe SHA256 must be identical
$bundle   = Join-Path $tauri 'target/core-sidecar/core-sidecar/core_service.exe'
$resource = Join-Path $tauri 'target/debug/resources/core-sidecar/core_service.exe'
$hb = $null; $hr = $null
if (Test-Path $bundle)   { $hb = (Get-FileHash $bundle   -Algorithm SHA256).Hash.ToLower() } else { T "MISSING bundle=$bundle" }
if (Test-Path $resource) { $hr = (Get-FileHash $resource -Algorithm SHA256).Hash.ToLower() } else { T "MISSING resource=$resource" }
T "bundle_sha256=$hb"; T "resource_sha256=$hr"
A (($hb -ne $null) -and ($hb -eq $hr)) 'gate:bundle-equals-resource-sha256'
$gate = [ordered]@{ algorithm='SHA256'; bundle_path=$bundle; bundle_sha256=$hb; resource_path=$resource; resource_sha256=$hr; equal=($hb -eq $hr) }
($gate | ConvertTo-Json) | Set-Content (Join-Path $OutDir 'bundle-resource-hash.json') -Encoding utf8
$meta.Add("bundle_sha256=$hb"); $meta.Add("resource_sha256=$hr"); $meta.Add("bundle_equals_resource=$($hb -eq $hr)")

# 5) startup smoke: the app must start and expose the four-page shell (window present)
if (-not $SkipSmoke) {
  $exe = Join-Path $tauri 'target/debug/m2rc1-desktop.exe'
  if (-not (Test-Path $exe)) { T "SMOKE skipped: exe missing"; A $false 'smoke:exe-present' }
  else {
    $iso = Join-Path $env:TEMP ('p19-smoke-'+[guid]::NewGuid().ToString('N').Substring(0,8))
    $env:NEWMANGA_DATA_ROOT = $iso
    $p = Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -PassThru `
      -RedirectStandardOutput (Join-Path $OutDir 'smoke-out.log') -RedirectStandardError (Join-Path $OutDir 'smoke-err.log')
    T "SMOKE pid=$($p.Id) iso=$iso"
    $ok = $false
    $dl = (Get-Date).AddSeconds($SmokeWaitSeconds)
    while ((Get-Date) -lt $dl) {
      Start-Sleep -Milliseconds 700
      if ($p.HasExited) { T "SMOKE early exit=$($p.ExitCode)"; break }
      $w = [System.Windows.Automation.AutomationElement]::RootElement
      try {
        $cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, 'M2-RC1 resource channel runtime')
        $hit = $w.FindFirst([System.Windows.Automation.TreeScope]::Children, $cond)
        if ($hit) { $ok = $true; break }
      } catch {}
    }
    if ($p -and -not $p.HasExited) { $p.CloseMainWindow() | Out-Null; Start-Sleep -Seconds 2 }
    if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force }
    T "SMOKE window_found=$ok exit=$($p.ExitCode)"
    A $ok 'smoke:window-present'
    $meta.Add("smoke_window=$ok")
  }
}

$meta.Add("checks=$script:Checks"); $meta.Add("fails=$script:Fails")
$rc = if ($script:Fails -gt 0) { 1 } else { 0 }
$meta.Add("exit_code=$rc")
T "END checks=$script:Checks fails=$script:Fails exit=$rc"
$meta | Set-Content (Join-Path $OutDir 'run-metadata.txt') -Encoding utf8
exit $rc
