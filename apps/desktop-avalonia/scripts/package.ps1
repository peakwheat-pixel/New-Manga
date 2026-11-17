[CmdletBinding()] param(
  [string]$OutputRoot=$( $v11rRepo = (Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent); if ($env:NEWMANGA_WORKSPACE_ROOT) { Join-Path $env:NEWMANGA_WORKSPACE_ROOT 'task-envs/FINAL-VALIDATION-1/out' } else { Join-Path (Join-Path (Split-Path $v11rRepo -Parent) ((Split-Path $v11rRepo -Leaf) + '.workspace')) 'task-envs/FINAL-VALIDATION-1/out' } ),
  [string]$Version='0.1.0',
  [string]$SidecarDir='',
  [string]$BuildPython=$( if ($env:NEWMANGA_BUILD_PYTHON) { $env:NEWMANGA_BUILD_PYTHON } else { 'python' } ),
  [switch]$WithModels,
  [int]$MaxZipMB=0,
  # FEA-15-A2-1: trimming analysis warnings (IL2026, Avalonia XAML loader / JsonSerializer
  # reflection) are suppressed for the publish only -- the installer smoke then verifies the
  # trimmed build actually starts. -NoTrim publishes without trimming as a fallback path.
  [switch]$SuppressTrimWarnings,
  [switch]$NoTrim
)
$ErrorActionPreference='Stop'
$root=Resolve-Path (Join-Path $PSScriptRoot '..'); $repo=Resolve-Path (Join-Path $root '..\..')
if([string]::IsNullOrWhiteSpace($SidecarDir)){$SidecarDir=Join-Path $repo 'apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar'}
$variant=if($WithModels){'models'}else{'base'}
$stageName=if($WithModels){"NewManga-$Version-win-x64-models"}else{"NewManga-$Version-win-x64"}
$stage=Join-Path $OutputRoot $stageName
if($MaxZipMB -le 0){$MaxZipMB=if($WithModels){2048}else{150}}
if(Test-Path $stage){Remove-Item $stage -Recurse -Force}
New-Item -ItemType Directory -Force (Join-Path $stage 'app')|Out-Null

# ---- 1) Avalonia Host/App (single-file self-contained) ----------------------
$publishArgs = if ($NoTrim) {
  @('-p:PublishTrimmed=false', '-p:PublishReadyToRun=false', '-p:EnableCompressionInSingleFile=false')
} else {
  $trimArgs = @('-p:PublishTrimmed=true', '-p:IncludeNativeLibrariesForSelfExtract=true', '-p:PublishReadyToRun=true', '-p:EnableCompressionInSingleFile=true')
  if ($SuppressTrimWarnings) { $trimArgs += '-p:SuppressTrimAnalysisWarnings=true' }
  $trimArgs
}
Push-Location $root
& dotnet publish src/NewManga.App/NewManga.App.csproj -c Release -r win-x64 --self-contained -p:PublishSingleFile=true @publishArgs -o (Join-Path $stage 'app') 2>&1 | Tee-Object -FilePath (Join-Path $OutputRoot "publish-$variant.log") | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'dotnet publish failed' }
Pop-Location

# ---- 2) Python Core sidecar (FINAL-VALIDATION-1 AC1 artifact) --------------
# Layout: <stage>/app/core-sidecar/ — the packaged SidecarLocator probes
# <app dir>/core-sidecar first, so the built sidecar rides beside the exe.
if(-not (Test-Path (Join-Path $SidecarDir 'core_service.exe'))){throw "sidecar bundle missing under SidecarDir: $SidecarDir (run packaging/m2ac5/build_sidecar.ps1 -Force first)"}

# SIDECAR-SCHEMA-STALE-1 (DSH 2026-11-16): the sidecar carries its own copy of the SQLite schema
# migrations. If the bundle is older than the source tree, the packaged app starts, the sidecar opens the
# data root, sees a NEWER schema than it knows and fail-closes ("database schema vN is newer than this
# application knows (vM); refusing to run") -- i.e. the installed product simply does not work.
#
# The bundle therefore has to declare which schema it was built against. build_sidecar.ps1 writes that
# into build-manifest.json; we refuse to package when the declaration is missing or stale.
$sidecarManifest = Join-Path $SidecarDir 'build-manifest.json'
if(-not (Test-Path $sidecarManifest)){
    throw ("sidecar bundle has no build-manifest.json under $SidecarDir -- it cannot prove which schema it understands. Rebuild it with packaging/m2ac5/build_sidecar.ps1 -Force (that script writes the manifest).")
}
$sidecarManifestInfo = Get-Content $sidecarManifest -Raw | ConvertFrom-Json
$sidecarSchema = $sidecarManifestInfo.schema_version
if($null -eq $sidecarSchema){throw "sidecar build-manifest.json does not declare schema_version: $sidecarManifest"}

# Read the newest schema version the *source tree* knows.
$schemaPy = Join-Path $repo 'src/infrastructure/sqlite/schema.py'
if(-not (Test-Path $schemaPy)){throw "cannot read source schema version: $schemaPy not found"}
$sourceSchema = (Select-String -Path $schemaPy -Pattern 'SCHEMA_VERSION_V(\d+)\s*=' -AllMatches |
    ForEach-Object { $_.Matches } | ForEach-Object { [int]$_.Groups[1].Value } |
    Measure-Object -Maximum).Maximum
if($null -eq $sourceSchema){throw "no SCHEMA_VERSION_V<n> constants found in $schemaPy"}

if([int]$sidecarSchema -ne [int]$sourceSchema){
    throw ("sidecar bundle is built against schema v$sidecarSchema but the source tree is at v$sourceSchema. The packaged app would fail at startup. Rebuild the bundle: packaging/m2ac5/build_sidecar.ps1 -Force.")
}
Write-Host ("sidecar schema check: v{0} == source v{0} (HEAD={1})" -f $sidecarSchema, $sidecarManifestInfo.git_head)

$sidecarDst=Join-Path $stage 'app/core-sidecar'
New-Item -ItemType Directory -Force $sidecarDst|Out-Null
$roboArgs=@($SidecarDir,$sidecarDst,'/E','/NFL','/NDL','/NJH','/NJS','/NP')
if(-not $WithModels){$roboArgs+=@('/XD',(Join-Path $SidecarDir 'models'))}
& robocopy @roboArgs | Out-Null
if($LASTEXITCODE -ge 8){throw "robocopy sidecar failed ($LASTEXITCODE)"}
$requiredSidecar=@('core_service.exe','host_bridge.exe','catalog_loader.exe')
foreach($n in $requiredSidecar){if(-not (Test-Path (Join-Path $sidecarDst $n))){throw "packaged sidecar incomplete: missing $n"}}
$sidecarFiles=Get-ChildItem $sidecarDst -Recurse -File
$sidecarBytes=($sidecarFiles|Measure-Object Length -Sum).Sum
$modelsBundled=(Test-Path (Join-Path $sidecarDst 'models'))
$modelsBytes=if($modelsBundled){(Get-ChildItem (Join-Path $sidecarDst 'models') -Recurse -File|Measure-Object Length -Sum).Sum}else{0}
# VERSION-JSON-GUARD-ALIGN-1 (reviewer-pvd F-PVD-01): the guard sums *.onnx only, while the
# directory total above also counts config/vocab files (109,678 B in the 0.1.1 sidecar). Both
# numbers are real; the ONE that goes into VERSION.json must be the guard's basis.
$modelsOnnxFiles=if($modelsBundled){@(Get-ChildItem (Join-Path $sidecarDst 'models') -Recurse -File -Filter '*.onnx')}else{@()}
$modelsOnnxBytes=($modelsOnnxFiles|Measure-Object Length -Sum).Sum; if($null -eq $modelsOnnxBytes){$modelsOnnxBytes=0}
if($WithModels -and -not $modelsBundled){throw 'WithModels requested but the built sidecar has no models/ directory'}

# ---- 2b) RELEASE-REPACK-1: record which sidecar build the package embeds ----
# The frozen core_service.exe is rebuilt from src/ by packaging/m2ac5/build_sidecar.ps1;
# the package metadata must identify the exact bytes so a stale build can never be
# mistaken for the current one (AC1 requires old/new sha256 comparison).
$sidecarExe = Join-Path $sidecarDst 'core_service.exe'
$sidecarBuildInfo = [ordered]@{
    core_service_sha256 = (Get-FileHash $sidecarExe -Algorithm SHA256).Hash.ToLower()
    core_service_bytes = (Get-Item $sidecarExe).Length
    core_service_built_at_utc = (Get-Item $sidecarExe).LastWriteTimeUtc.ToString('o')
    repo_head = (& git -C $repo rev-parse HEAD 2>$null)
    variant = $variant
    models_bundled = $modelsBundled
}
Write-Host ("sidecar build: {0} ({1} bytes, HEAD={2})" -f $sidecarBuildInfo.core_service_sha256, $sidecarBuildInfo.core_service_bytes, $sidecarBuildInfo.repo_head)

# ---- 3) license files: byte-identical to the repo root ----------------------
# AGPL-RELEASE-1: the models variant ships Ultralytics YOLO11s-seg (AGPL-3.0), so the GNU
# AGPL-3.0 full text rides in BOTH variants (base carries it as the optional-component notice;
# its own declaration stays GPL-3.0-or-later). Every file is copied and SHA-256 verified.
$lic=@('LICENSE','LICENSE-AGPL-3.0.txt','NOTICE.md','THIRD_PARTY_LICENSES.md')
$licHashes=@{}
foreach($n in $lic){
  $src=Join-Path $repo $n; $dst=Join-Path $stage $n
  if(-not (Test-Path $src)){throw "license file missing in repo root: $n"}
  Copy-Item $src $dst -Force
  $a=(Get-FileHash $src -Algorithm SHA256).Hash.ToLower(); $b=(Get-FileHash $dst -Algorithm SHA256).Hash.ToLower()
  if($a -ne $b){throw "license mismatch $n"}
  $licHashes[$n]=$a
}

# ---- 4) installer scripts + docs -------------------------------------------
@('install.ps1','uninstall.ps1','migrate-legacy-dryrun.ps1')|ForEach-Object{Copy-Item (Join-Path $PSScriptRoot $_) (Join-Path $stage $_) -Force}
$docs=Join-Path $root 'docs'
Copy-Item (Join-Path $docs 'MANUAL_VERIFY.md') $stage -Force
Copy-Item (Join-Path $docs 'UPGRADE.md') $stage -Force
Copy-Item (Join-Path $docs 'LICENSE_AUDIT.md') $stage -Force

# ---- 4b) GPU-ORT-PROBE-1: packaged device probe (ORT EP list) ----------------
# The release closure is torch-free and ships onnxruntime-directml, so the
# device verdict must come from the build environment's ONNX Runtime provider
# list; the settings page renders it from VERSION.json. A probe failure leaves
# devices=null (the UI then shows "未打包探测") and is never faked.
$deviceProbe = $null
$gpuProbeScript = Join-Path $PSScriptRoot 'gpu_probe.py'
if (Test-Path $BuildPython) {
    try {
        $probeOutput = & $BuildPython $gpuProbeScript 2>$null | Out-String
        if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($probeOutput)) {
            $deviceProbe = $probeOutput | ConvertFrom-Json
        }
    } catch {
        $deviceProbe = $null
    }
}
if ($null -eq $deviceProbe) { Write-Warning 'GPU device probe unavailable; VERSION.json devices=null' }

# ---- 5) VERSION.json: real model distribution strategy + license declaration
$modelsStrategy=if($modelsBundled){
  "bundled: app/core-sidecar/models ($([math]::Round($modelsBytes/1MB,1)) MiB in-package); no download at run time"
}else{
  "separated: base package ships NO models; the frozen Core reports typed PROVIDER_NOT_CONFIGURED until the pinned models are placed on %APPDATA%\com.newmanga.desktop\models (data root) or passed via NEWMANGA_DETECTOR_WEIGHTS / NEWMANGA_MANGA_OCR_WEIGHTS; a separate '-models' package ships the same models in-bundle"
}
# AGPL-RELEASE-1 AC2/AC4: the package metadata itself must state the variant's overall license.
# models ships Ultralytics YOLO11s-seg (AGPL-3.0) -> the whole variant is AGPL-3.0; base has no
# weights -> GPL-3.0-or-later. The AGPL full text rides in both variants (see section 3).
$licenseDeclaration=if($modelsBundled){'AGPL-3.0'}else{'GPL-3.0-or-later'}
$bundledWeightsLicense=if($modelsBundled){
  # VERSION-JSON-GUARD-ALIGN-1: name the weights that are ACTUALLY in this sidecar instead of a
  # hard-coded one (the template used to claim yolo11s-seg even when the detector was rtdetr).
  $modelFiles=@(Get-ChildItem (Join-Path $sidecarDst 'models') -Recurse -File -Filter '*.onnx' | ForEach-Object { $_.FullName.Substring($sidecarDst.Length+1).Replace('\','/') })
  'AGPL-3.0 (conservative: ' + ($modelFiles -join ', ') + ')'
}else{'none (no model weights in this variant)'}
# VERSION-JSON-GUARD-ALIGN-1 (reviewer-pvd F-PVD-02): the guard requires app_build and there was no
# generator for it, so no clean package.ps1 output could ever pass. Derive it from the staged exe;
# repo_head comes from the head the single-file publish embedded in ProductVersion.
$appExe=Join-Path $stage 'app/NewManga.App.exe'
if(-not (Test-Path -LiteralPath $appExe)){throw 'app_build cannot be derived: packaged exe missing at '+$appExe}
$appExeSha=(Get-FileHash -LiteralPath $appExe -Algorithm SHA256).Hash.ToLowerInvariant()
$appExeBytes=(Get-Item -LiteralPath $appExe).Length
$appProductVersion=(Get-Item -LiteralPath $appExe).VersionInfo.ProductVersion
$appHead=$null
if($appProductVersion -match '([0-9a-fA-F]{40})'){$appHead=$Matches[1].ToLowerInvariant()}
if(-not $appHead){$appHead=(git -C $repo rev-parse HEAD).Trim()}
@{version=$Version;channel='stable';variant=$variant;data_root='%APPDATA%\com.newmanga.desktop';license=$licenseDeclaration;license_files=$lic;bundled_weights_license=$bundledWeightsLicense;models=$modelsStrategy;models_bundled=$modelsBundled;models_bundled_bytes=[int64]$modelsOnnxBytes;models_dir_bytes=[int64]$modelsBytes;app_build=@{exe_sha256=$appExeSha;exe_bytes=[int64]$appExeBytes;repo_head=$appHead};sidecar='bundled: app/core-sidecar (core_service/host_bridge/catalog_loader/acceptance_bridge/sfx_detect_probe + _internal + python)';migration='runtime dry-run script included';devices=$deviceProbe;sidecar_build=$sidecarBuildInfo}|ConvertTo-Json|Set-Content (Join-Path $stage 'VERSION.json') -Encoding utf8
# Keep a copy beside the exe too: the single-file host always sees its own directory,
# so the settings page can render the packaged device probe on every layout.
Copy-Item (Join-Path $stage 'VERSION.json') (Join-Path $stage 'app/VERSION.json') -Force

# ---- 6) manifest + zip + budget gate ---------------------------------------
$files=Get-ChildItem $stage -Recurse -File; $bytes=($files|Measure-Object Length -Sum).Sum
$manifest=[ordered]@{package=$stageName;version=$Version;variant=$variant;bytes=$bytes;sidecar_bytes=$sidecarBytes;models_bundled=$modelsBundled;models_bytes=[int64]$modelsOnnxBytes;models_dir_bytes=[int64]$modelsBytes;licenses=$licHashes;files=@()}
foreach($f in $files){$manifest.files+=@{path=$f.FullName.Substring($stage.Length+1).Replace('\','/');bytes=$f.Length;sha256=(Get-FileHash $f.FullName -Algorithm SHA256).Hash.ToLower()}}
$manifest|ConvertTo-Json -Depth 5|Set-Content (Join-Path $stage 'package-manifest.json') -Encoding utf8
$zip=Join-Path $OutputRoot "$stageName.zip"
if(Test-Path $zip){Remove-Item $zip -Force}
Compress-Archive -Path (Join-Path $stage '*') -DestinationPath $zip -CompressionLevel Optimal
$zipBytes=(Get-Item $zip).Length
if($zipBytes -gt ($MaxZipMB*1MB)){throw "package exceeds ${MaxZipMB}MB: $zipBytes"}
$summary=[ordered]@{ac='AC2';variant=$variant;version=$Version;zip=$zip;zip_bytes=$zipBytes;zip_mb=[math]::Round($zipBytes/1MB,2);max_zip_mb=$MaxZipMB;uncompressed_bytes=$bytes;uncompressed_mb=[math]::Round($bytes/1MB,2);file_count=$files.Count;sidecar_bytes=$sidecarBytes;sidecar_mb=[math]::Round($sidecarBytes/1MB,2);models_bundled=$modelsBundled;models_bytes=$modelsBytes;licenses_byte_identical=$true;license_hashes=$licHashes;generated_at_utc=[DateTime]::UtcNow.ToString('o')}
$summary|ConvertTo-Json -Depth 4|Set-Content (Join-Path $OutputRoot "package-summary-$variant.json") -Encoding utf8
$summary|ConvertTo-Json -Depth 4
