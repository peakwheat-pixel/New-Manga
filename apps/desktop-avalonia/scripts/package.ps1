[CmdletBinding()] param(
  [string]$OutputRoot='G:/CODEX/New Manga.workspace/task-envs/FINAL-VALIDATION-1/out',
  [string]$Version='0.1.0',
  [string]$SidecarDir='',
  [string]$BuildPython='G:/CODEX/New Manga.task-envs/m2ac5-build/Scripts/python.exe',
  [switch]$WithModels,
  [int]$MaxZipMB=0
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
Push-Location $root
& dotnet publish src/NewManga.App/NewManga.App.csproj -c Release -r win-x64 --self-contained -p:PublishSingleFile=true -p:PublishTrimmed=true -p:IncludeNativeLibrariesForSelfExtract=true -p:PublishReadyToRun=true -p:EnableCompressionInSingleFile=true -o (Join-Path $stage 'app') 2>&1 | Tee-Object -FilePath (Join-Path $OutputRoot "publish-$variant.log") | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'dotnet publish failed' }
Pop-Location

# ---- 2) Python Core sidecar (FINAL-VALIDATION-1 AC1 artifact) --------------
# Layout: <stage>/app/core-sidecar/ — the packaged SidecarLocator probes
# <app dir>/core-sidecar first, so the built sidecar rides beside the exe.
if(-not (Test-Path (Join-Path $SidecarDir 'core_service.exe'))){throw "sidecar bundle missing under SidecarDir: $SidecarDir (run packaging/m2ac5/build_sidecar.ps1 -Force first)"}
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
$bundledWeightsLicense=if($modelsBundled){'AGPL-3.0 (Ultralytics YOLO11s-seg: app/core-sidecar/models/detector/yolo11s-seg.onnx)'}else{'none (no model weights in this variant)'}
@{version=$Version;channel='stable';variant=$variant;data_root='%APPDATA%\com.newmanga.desktop';license=$licenseDeclaration;license_files=$lic;bundled_weights_license=$bundledWeightsLicense;models=$modelsStrategy;sidecar='bundled: app/core-sidecar (core_service/host_bridge/catalog_loader/acceptance_bridge/sfx_detect_probe + _internal + python)';migration='runtime dry-run script included';devices=$deviceProbe;sidecar_build=$sidecarBuildInfo}|ConvertTo-Json|Set-Content (Join-Path $stage 'VERSION.json') -Encoding utf8
# Keep a copy beside the exe too: the single-file host always sees its own directory,
# so the settings page can render the packaged device probe on every layout.
Copy-Item (Join-Path $stage 'VERSION.json') (Join-Path $stage 'app/VERSION.json') -Force

# ---- 6) manifest + zip + budget gate ---------------------------------------
$files=Get-ChildItem $stage -Recurse -File; $bytes=($files|Measure-Object Length -Sum).Sum
$manifest=[ordered]@{package=$stageName;version=$Version;variant=$variant;bytes=$bytes;sidecar_bytes=$sidecarBytes;models_bundled=$modelsBundled;models_bytes=$modelsBytes;licenses=$licHashes;files=@()}
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
